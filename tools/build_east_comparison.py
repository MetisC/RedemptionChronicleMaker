"""Build diagnostic chronicles referencing original EastLondon resources.

Only writes in the workspace. These are comparison cases, not new story layers
and not an authoring-tool or installer dependency.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
from rcm.catalogue import parse_chronicle
from rcm.generator import zip_bytes
from rcm.paths import Workspace


def build_comparison():
    ws = Workspace(ROOT, Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
    level = json.loads(ws.output("cache/levels.json").read_text(encoding="utf8"))["EastLondon"]
    story = next(r for r in level["references"] if r["chronicle"] == "London.nsc")
    base = next(r for r in level["references"] if r["chronicle"] == "MP_London_Null.nsc")
    assert story["nil"].casefold() == base["nil"].casefold() == "l1_east.nil"
    assert story["scene"] == "EAST_28_1.nsd" and base["scene"] == "null"
    labels = {"rcm_east_base": "RCM: EastLondon - mapa base original",
              "rcm_east_scene": "RCM: EastLondon - escena original"}
    resources = {}
    cases = []
    for cid, ref in [("rcm_east_base", base), ("rcm_east_scene", story)]:
        text = ("# RCM diagnostic: original EastLondon resources, direct entry\r\n"
                f"location EastLondon {ref['nil']} {ref['scene']} {ref['map_ui']} {ref['map_label']} {ref['flags']}\r\n"
                "metafile R_EastCompare.nmf\r\nreviveloc EastLondon 0\r\nflags 0x3\r\n")
        data = text.encode("cp1252")
        parsed = parse_chronicle(data)
        assert len(parsed["locations"]) == 1
        assert parsed["locations"][0]["nil"] == ref["nil"]
        assert parsed["locations"][0]["scene"] == ref["scene"]
        resources[f"chronicles/{cid}.nsc"] = data
        cases.append({"id": cid, "label": labels[cid], "original_reference": ref,
                      "first_location": "EastLondon", "revive_entrance": 0,
                      "native_same_position_verified": False})
    resources["chronicles/R_EastCompare.nmf"] = (
        "NLS london.nls\r\nCASH cashuk\r\nNVO game.nvo\r\nSPEAKER Christof\r\n"
        "NLS _R_EastCompare.nls\r\n").encode("cp1252")
    resources["strings/_R_EastCompare.nls"] = (
        "\r\n".join(f"{cid} {label}" for cid, label in labels.items()) + "\r\n").encode("cp1252")
    package = zip_bytes(resources)
    output = Path("build/diagnostics/east_compare")
    ws.write(output / "east_compare.nob", package)
    for name, data in resources.items():
        ws.write(output / "resources" / name, data)
    report = {"purpose": "Compare native EastLondon at direct entrance, without choosing another sky",
              "native_test": "pending user observation", "cases": cases,
              "geometry_or_original_scene_modified": False,
              "original_campaign_complete": False,
              "no_original_authoring_tools": True,
              "no_new_java_or_models": True,
              "package": "east_compare.nob", "sha256": hashlib.sha256(package).hexdigest(),
              "files": {n: {"size": len(d), "sha256": hashlib.sha256(d).hexdigest()}
                        for n, d in resources.items()},
              "limits": ["The story-scene case references original NPC/scripts; it is not a complete London campaign",
                         "Both cases reference the same NIL and entrance 0; actual starting position must be compared in game",
                         "The NULL case allows the motor's original base-level loading; no synthetic sky override"]}
    ws.write(output / "report.json", json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"output": str(ws.output(output)), "cases": labels,
                      "package_sha256": report["sha256"], "game_modified": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_comparison()
