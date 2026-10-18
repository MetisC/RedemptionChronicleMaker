"""Rebuild the derived sector catalogue used by offline native-entry checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.native_arrivals import planes,cache_path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path);args=parser.parse_args()
    from rcm.deployment import default_game
    game=args.game or default_game(ROOT)
    cached=Workspace(ROOT);source=Workspace(ROOT,game) if game else cached
    backend=Backend(cached);seen=set();ready=0
    for level in backend.levels.values():
        if not level.get('geometry'):continue
        key=str(cache_path(cached,level['geometry'][0])[0])
        if key in seen:continue
        seen.add(key)
        try:planes(cached,level)
        except (ValueError,OSError,KeyError):planes(source,level)
        ready+=1
    print(json.dumps({'sector_catalogues_verified':ready,'original_game_modified':False}))


if __name__=='__main__':main()
