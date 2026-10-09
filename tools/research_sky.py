"""Reproduce sky-resource evidence by reading the installation and copied PE."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r"H:\GOG\Vampire The Masquerade - Redemption")
OUT = ROOT / "research/sky"
OUT.mkdir(parents=True, exist_ok=True)

def text32(data):
    return data.split(b"\0", 1)[0].decode("cp1252")

report = {"source": str(GAME / "Resource.nob"), "scenes": [], "models": {}}
with zipfile.ZipFile(GAME / "Resource.nob") as archive:
    names = {name.lower(): name for name in archive.namelist()}
    for name in archive.namelist():
        if name.lower().endswith(".nsd"):
            data = archive.read(name)
            if data[:8] != b"NSD\x10\x08\0\0\0":
                raise ValueError("Unknown NSD version: " + name)
            report["scenes"].append({"file": name, "sky_model": text32(data[-64:-32]),
                                     "sky_animation": text32(data[-32:])})
    for model in ["LondonNightSky", "Sky", "LondonTower", "NewYorkDocks"]:
        name = names["3d/models/" + model.lower() + ".nod"]
        data = archive.read(name)
        version, count = struct.unpack_from("<II", data)
        if version != 7 or count > 100:
            raise ValueError("Unsupported model header")
        report["models"][model] = {"file": name, "sha256": hashlib.sha256(data).hexdigest(),
            "version": version, "materials": [text32(data[8+i*32:40+i*32]) for i in range(count)],
            "shape_name_strings": [s.decode("ascii") for s in re.findall(rb"[A-Za-z_][A-Za-z0-9_]*Shape[0-9]*", data)]}
        for item in [name, names["3d/anims/" + model.lower() + ".nad"]]:
            target = OUT / item
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(item))
(OUT / "sky_evidence.json").write_text(json.dumps(report, indent=2), encoding="utf8")

sys.path.insert(0, str(ROOT / "cache/vendor"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
data = (ROOT / "research/user_directory/Vampire.exe").read_bytes()
pe = struct.unpack_from("<I", data, 0x3c)[0]
base = struct.unpack_from("<I", data, pe + 52)[0]
table = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
sections = [struct.unpack_from("<IIII", data, table+i*40+8)
            for i in range(struct.unpack_from("<H", data, pe+6)[0])]
md = Cs(CS_ARCH_X86, CS_MODE_32)
lines = []
for va, size, label in [(0x420210, 523, "Sky render: current/base scene, model, camera-relative matrix"),
                         (0x4a7de0, 1550, "NSD reader: final sky model/animation fields"),
                         (0x4c35d0, 600, "NOD header/material loader")]:
    for _, rva, rawsize, raw in sections:
        if base + rva <= va < base + rva + rawsize:
            offset = raw + va-base-rva
            break
    else:
        raise ValueError(hex(va))
    lines.append("\n" + label)
    lines.extend(f"{i.address:08x}: {i.mnemonic} {i.op_str}"
                 for i in md.disasm(data[offset:offset+size], va))
(OUT / "native_evidence.txt").write_text("\n".join(lines), encoding="utf8")
print("Saved model/material evidence, all original NSD sky references and native reader/render evidence.")
