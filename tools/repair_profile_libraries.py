"""Repair only owned RCM startup libraries; never launch or edit saved characters."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]


def main():
    from rcm.paths import Workspace
    from rcm.profile_compatibility import profile_references,refresh_installed_profiles
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path,required=True);args=parser.parse_args()
    ws=Workspace(ROOT,args.game)
    profiles={p:dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),references=sorted(profile_references(p.read_bytes()))) for p in (ws.game/'Crypt').glob('*.npf')}
    result=refresh_installed_profiles(ws)
    for path,record in profiles.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('El perfil cambió durante la reparación')
    result['profiles']={p.name:r for p,r in profiles.items()};result['profiles_unchanged']=True
    ws.write('research/runtime_test/profile_startup_repair.json',json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
