"""RCM 3D+ corpus scan: walk every entity of every original NSD.

Tolerant walker replicating the native entity layout (0x4a8560):
  tags (u32 + 36*n) -> frames (u32 + 24*n) -> params (typed) ->
  brush flag u32 -> [mesh body + u32 planecount + 16*count] ->
  region links (u32 + 4*n) -> light dwords (u32 + 4*n).

Goal: classify which templates carry brushes, whether brushes correlate
with collision/render hints, and how big the original budgets are.
Writes entity_corpus.json; prints a summary to stdout.
"""
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCENES = ROOT / "research/original/Resource.nob/scenes"


def u32(data, p):
    return struct.unpack_from("<I", data, p)[0]


def cstring(data):
    return data.split(b"\0", 1)[0].decode("cp1252", "replace")


def walk_params(data, p, count):
    for _ in range(count):
        kind = u32(data, p); p += 4
        if not 1 <= kind <= 11:
            raise ValueError("param kind")
        size = 0 if kind == 6 else 4
        if kind == 7:
            size = u32(data, p); p += 4
            if not 1 <= size <= 65536:
                raise ValueError("param str")
        p += size
    return p


def walk_brush(data, p):
    """Return (info, new_offset). Body: mats, counts, verts, indices, groups, bounds, planes."""
    start = p
    mcount = u32(data, p); p += 4
    if not 0 < mcount <= 64:
        raise ValueError("brush materials")
    materials = [cstring(data[p + i * 32:p + (i + 1) * 32]) for i in range(mcount)]
    p += mcount * 32
    nv, nt, ng, flags = struct.unpack_from("<IIHI", data, p); p += 14
    if not (0 < nv <= 200000 and 0 < nt <= 200000 and 0 < ng <= 4096):
        raise ValueError("brush counts")
    p += nv * 40
    if flags & 1:
        p += nv * 2
    p += nt * 6 + ng * 28
    bounds = struct.unpack_from("<6f", data, p); p += 24
    planes = u32(data, p); p += 4
    if planes > 256 or p + planes * 16 > len(data):
        raise ValueError("brush planes")
    p += planes * 16
    return {"materials": materials, "vertices": nv, "triangles": nt, "groups": ng,
            "flags": flags, "bounds": [bounds[:3], bounds[3:]], "planes": planes,
            "offset": start}, p


def walk_entity(data, p):
    """Return (entity dict, new offset)."""
    n = u32(data, p)
    if not 0 < n <= 4096 or p + 4 + n * 36 > len(data):
        raise ValueError("tags")
    p += 4
    tags = {}
    tag_ids = []
    for _ in range(n):
        tid = u32(data, p)
        tags[tid] = data[p + 4:p + 36]
        tag_ids.append(tid)
        p += 36
    ent = {"tags": {str(k): cstring(v) if v.split(b"\0", 1)[0] and all(32 <= b < 127 or b >= 160 for b in v.split(b"\0", 1)[0]) else list(struct.unpack("<8I", v))
                    for k, v in tags.items()},
           "tag_ids": tag_ids}
    count = u32(data, p); p += 4
    if count > 4096 or p + 24 * count > len(data):
        raise ValueError("frames")
    ent["frames"] = count
    p += 24 * count
    count = u32(data, p); p += 4
    if count > 64:
        raise ValueError("params")
    ent["params"] = count
    p = walk_params(data, p, count)
    if u32(data, p):
        info, p = walk_brush(data, p + 4)
        ent["brush"] = info
    else:
        p += 4
    count = u32(data, p); p += 4
    if count > 10000 or p + 4 * count > len(data):
        raise ValueError("region links")
    ent["region_links"] = list(struct.unpack_from("<" + str(count) + "I", data, p)) if count else []
    p += 4 * count
    count = u32(data, p); p += 4
    if count > 10000 or p + 4 * count > len(data):
        raise ValueError("light")
    ent["light"] = count
    p += 4 * count
    return ent, p


def main():
    out = {}
    stats = Counter()
    brush_templates = Counter()
    region_templates = Counter()
    failures = {}
    for path in sorted(SCENES.glob("*.nsd")):
        data = path.read_bytes()
        try:
            if data[:4] != b"NSD\x10" or u32(data, 4) != 8:
                raise ValueError("header")
            n = u32(data, 80)
            if n > 100000:
                raise ValueError("entity count")
            p = 84
            ents = []
            for _ in range(n):
                e, p = walk_entity(data, p)
                ents.append(e)
            tail = len(data) - p
            out[path.name] = {"entities": ents, "tail": tail}
            for e in ents:
                t0 = e["tags"].get("0", "?")
                if isinstance(t0, list):
                    t0 = "?"
                stats["entities"] += 1
                if "brush" in e:
                    stats["brush_entities"] += 1
                    brush_templates[t0] += 1
                    stats["brush_tris"] += e["brush"]["triangles"]
                if e["region_links"]:
                    stats["region_entities"] += 1
                    region_templates[t0] += 1
                if e["frames"]:
                    stats["framed_entities"] += 1
                if e["light"]:
                    stats["lit_entities"] += 1
        except Exception as error:
            failures[path.name] = str(error)
    (ROOT / "research/scenography/entity_corpus.json").write_text(
        json.dumps(out, indent=1), encoding="utf8")
    print("scenes parsed:", len(out), "failures:", len(failures))
    for k, v in failures.items():
        print("  FAIL", k, v)
    print(json.dumps(stats, indent=1))
    print("BRUSH TEMPLATES:")
    for name, count in brush_templates.most_common(50):
        print(f"  {count:4d}  {name}")
    print("REGION-LINK TEMPLATES:")
    for name, count in region_templates.most_common(50):
        print(f"  {count:4d}  {name}")


if __name__ == "__main__":
    sys.exit(main())
