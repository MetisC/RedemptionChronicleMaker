"""Read-only PE evidence for the native -user option and JVM search paths.

Optional research dependency: capstone 5.0.7 in cache/vendor.
Never runs the game or changes its installation.
"""
from pathlib import Path
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cache/vendor"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

SOURCE = Path(r"H:\GOG\Vampire The Masquerade - Redemption\Vampire.exe")
DEST = ROOT / "research/user_directory"
DEST.mkdir(parents=True, exist_ok=True)
data = SOURCE.read_bytes()
(DEST / "Vampire.exe").write_bytes(data)
pe = struct.unpack_from("<I", data, 0x3c)[0]
section_count = struct.unpack_from("<H", data, pe + 6)[0]
optional_size = struct.unpack_from("<H", data, pe + 20)[0]
base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
sections = []
for index in range(section_count):
    offset = pe + 24 + optional_size + index * 40
    name = data[offset:offset+8].rstrip(b"\0").decode("ascii")
    vsize, rva, rawsize, raw = struct.unpack_from("<IIII", data, offset + 8)
    sections.append((name, base + rva, raw, rawsize))

def address(raw_offset):
    for name, va, raw, size in sections:
        if raw <= raw_offset < raw + size:
            return va + raw_offset - raw
    raise ValueError("Offset outside PE sections")

def raw_offset(va):
    for name, start, raw, size in sections:
        if start <= va < start + size:
            return raw + va - start
    raise ValueError("Address outside PE sections")

md = Cs(CS_ARCH_X86, CS_MODE_32)
needles = [b"-user\0", b"/user\0", b"classes.zip;%s\\codex", b"classes.zip;codex"]
evidence = []
texts = []
for va in [0x50054c, 0x52da04, 0x52da08]:
    raw = raw_offset(va)
    value = data[raw:data.index(b"\0", raw)].decode("ascii")
    texts.append(f"String {va:08x}: {value!r}")
for va, size, label in [(0x4281f1, 70, "-user argument handler"), (0x4b3ae0, 120, "JVM classpath construction"), (0x42848e, 100, "user directory registration"), (0x4cac10, 90, "directory registration function"), (0x4cbbd0, 1000, "directory search-list builder"), (0x412a29, 142, "multiplayer chronicle selector"), (0x4cae60, 656, "file enumerator: loose scan and NOB indices")]:
    raw = raw_offset(va)
    texts.append("\n" + label + "\n" + "\n".join(f"{i.address:08x}: {i.mnemonic} {i.op_str}" for i in md.disasm(data[raw:raw+size], va)))
user_references = []
cursor = 0
while True:
    cursor = data.find(struct.pack("<I", 0x613bc4), cursor)
    if cursor < 0:
        break
    va = address(cursor)
    user_references.append(hex(va))
    window = cursor - 32
    texts.append(f"\nUSER DIRECTORY BUFFER reference {va:08x}\n" + "\n".join(f"{i.address:08x}: {i.mnemonic} {i.op_str}" for i in md.disasm(data[window:cursor+110], address(window))))
    cursor += 4
for needle in needles:
    start = data.index(needle)
    va = address(start)
    text = data[start:data.index(b"\0", start)].decode("ascii")
    references = []
    packed = struct.pack("<I", va)
    cursor = 0
    while True:
        cursor = data.find(packed, cursor)
        if cursor < 0:
            break
        ref = address(cursor)
        references.append(hex(ref))
        # Retain a wide window; decoding from an arbitrary boundary is evidence,
        # not a complete control-flow recovery. Focused decoding can follow.
        window = max(cursor - 80, 0)
        lines = [f"{i.address:08x}: {i.mnemonic} {i.op_str}" for i in md.disasm(data[window:cursor+260], address(window))]
        texts.append(f"\nSTRING {text!r} at {va:08x}; reference {ref:08x}\n" + "\n".join(lines))
        cursor += 4
    evidence.append({"text": text, "address": hex(va), "references": references})
(DEST / "string_references.json").write_text(json.dumps(evidence, indent=2), encoding="utf8")
(DEST / "user_buffer_references.json").write_text(json.dumps(user_references, indent=2), encoding="utf8")
(DEST / "disassembly.txt").write_text("\n".join(texts), encoding="utf8")
print(json.dumps(evidence, indent=2))
