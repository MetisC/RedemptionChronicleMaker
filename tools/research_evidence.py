"""Reproducible supporting evidence; reads originals and writes only workspace."""
from pathlib import Path, PurePosixPath
import collections
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rcm.paths import Workspace
from rcm.formats import NotFile, cstring

GAME = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"H:\GOG\Vampire The Masquerade - Redemption")
ws = Workspace(ROOT, GAME)
evidence = {}
for archive in sorted(GAME.glob("*.nob")):
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            ext = PurePosixPath(info.filename).suffix.lower()
            if ext in {".nil", ".nsd", ".not", ".nod", ".nad", ".nco", ".nai", ".npc", ".nqd", ".nbs"}:
                with z.open(info) as f:
                    header = f.read(12)
                item = {"archive": archive.name, "path": info.filename, "size": info.file_size, "first12_hex": header.hex()}
                evidence.setdefault(ext, []).append(item)
ws.write("research/binary_headers.json", json.dumps(evidence, indent=2))
exe = (GAME / "Vampire.exe").read_bytes()
start = exe.index(b"basedon\0")
stop = exe.index(b"PARTICLENAME\0", start) + len(b"PARTICLENAME\0")
names = list(re.finditer(rb"[\x20-\x7e]+\0", exe[start:stop]))
tags = [{"candidate_tag": i, "name": m.group()[:-1].decode("ascii"), "executable_offset": start + m.start(), "status": "ordered native strings + original NOT value comparison; no SDK header available"} for i, m in enumerate(names)]
ws.write("research/template_tag_evidence.json", json.dumps(tags, indent=2))
api = ws.output("research/API_SIGNATURES.txt").read_text(encoding="utf8")
owner = None
methods, constants = [], []
for line in api.splitlines():
    if line.startswith("public class "):
        owner = line.split()[2]
    elif "(" in line and line.strip().startswith("public"):
        methods.append({"class": owner, "declaration": line.strip()})
    elif "public static final" in line:
        constants.append({"class": owner, "declaration": line.strip()})
bytecode = ws.output("research/ALL_CODEX.bytecode.txt").read_text(encoding="utf8")
owner = None
callbacks = collections.defaultdict(list)
for line in bytecode.splitlines():
    if line.startswith("public class "):
        owner = line.split()[2]
    if re.match(r"  public void (beginscene|endscene|created|clicked|entered|exited|triggered|timer|convended|convreached|save|restore|restored)\(", line):
        callbacks[line.strip()].append(owner)
ws.write("research/api_index.json", json.dumps({"methods": methods, "constants": constants, "callbacks": dict(callbacks)}, indent=2))
comparisons = []
for p in ws.output("research/original/Resource.nob/misc/Templates").glob("*.not"):
    data = p.read_bytes()
    nf = NotFile.read(data)
    comparisons.append({"file": p.name, "templates": len(nf.templates), "roundtrip_exact": nf.encode() == data, "opaque_trailing_bytes": len(nf.trailing)})
    for t in nf.templates:
        if t.name in {"businessWoman", "_actor", "ghost", "_civilians", "_civilians_MD"}:
            ws.write(Path("research/templates") / (t.name + ".json"), json.dumps({"name": t.name, "source": p.name, "tags": [{"id": tag.id, "payload_hex": tag.value.hex(), "cstring_preview": cstring(tag.value)} for tag in t.tags]}, indent=2))
ws.write("research/not_roundtrips.json", json.dumps(comparisons, indent=2))
print(json.dumps({"binary_extension_counts": {e: len(v) for e, v in evidence.items()}, "native_string_tag_candidates": len(tags), "api_methods": len(methods), "not_roundtrips": comparisons}, indent=2))
