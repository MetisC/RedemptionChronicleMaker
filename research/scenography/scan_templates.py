"""Dump NOT templates relevant to brush-bearing entities (tags resolved 1 level)."""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
from rcm.formats import NotFile, cstring, u32  # noqa: E402

NAMES = """trigger_region tracker_thing cameraclip_region tracker_thing_nohilite
trigger_region_exit wallgib glassgib stoneheavy_on_stone_nhl metallight_on_stone
tracker_thing_no_sound flesh_iris_door_nh woodgib stoneheavy_on_stone
tracker_thing_big tracker_thing_blocker tracker_thing_null small_lever1
metalheavy_on_metal metalheavy_on_metal2 elevatordoor_nh wood_on_stone
door_raise1_nhl wood_swing_medium1 large_lever2 wood_swing_heavy1_nhl
elevatordoor metallight_on_metal wood_swing_small2 small_lever2
metalheavy_on_stone stonelight_on_stone large_lever1 wood_swing_small1
wood_swing_medium2 metal_swing_gate dungeon_door wood_swing_heavy1
ghost metal_swing_2 stonelight_on_stone_s door_raise2 button_switch_small2
button_switch_small1 wood_swing_heavy2 woodendoor door_raise2_nhl
button_switch_medium2 _region prop""".split()


def load_templates():
    templates = {}
    for path in (ROOT / "research/original/Resource.nob/misc/Templates").glob("*.not"):
        nf = NotFile.read(path.read_bytes())
        for t in nf.templates:
            templates.setdefault(t.name.casefold(), (path.name, t))
    return templates


def render(templates, name):
    found = templates.get(name.casefold())
    if not found:
        return {"name": name, "missing": True}
    source, t = found
    values = {}
    cur = t
    seen = set()
    while cur is not None:
        for tag in cur.tags:
            if tag.id not in values:
                raw = tag.value
                text = raw.split(b"\0", 1)[0]
                if text and all(32 <= b < 127 for b in text):
                    values[tag.id] = cstring(raw)
                else:
                    values[tag.id] = struct.unpack("<8I", raw)
        parent = cstring(cur.values()[0]) if 0 in cur.values() else None
        if parent and parent.casefold() not in seen:
            seen.add(parent.casefold())
            nxt = templates.get(parent.casefold())
            cur = nxt[1] if nxt else None
        else:
            cur = None
    return {"name": t.name, "file": source, "parent": cstring(t.values()[0]) if 0 in t.values() else None,
            "tags": {str(k): (list(v) if isinstance(v, tuple) else v) for k, v in sorted(values.items())}}


def main():
    templates = load_templates()
    out = {name: render(templates, name) for name in NAMES}
    print(json.dumps(out, indent=1))
    (ROOT / "research/scenography/template_dump.json").write_text(json.dumps(out, indent=1), encoding="utf8")


if __name__ == "__main__":
    main()
