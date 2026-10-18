"""Publish an existing local WTD import to the shared RCM runtime, no gameplay."""
from pathlib import Path
import json
import sys
import argparse

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]


def main():
    from rcm.paths import Workspace
    from rcm.deployment import configured_game,safe_target
    from rcm.wtd import manifest,publish_shared,ROOT as CONTENT_ROOT,ARCHIVE,sha
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--game',type=Path);args=parser.parse_args()
    ws=Workspace(ROOT,args.game);ws=Workspace(ROOT,configured_game(ws))
    record=manifest(ws)
    if not record:raise ValueError('Importa Within The Darkness antes de publicar el contenido compartido')
    data=ws.output(CONTENT_ROOT+'/'+ARCHIVE).read_bytes()
    publish_shared(ws,data,record)
    paths=[safe_target(ws.game,ws.game/'RCM'/ARCHIVE)]
    for name in ('.rcm_deployment.json','.rcm_manifest.json'):
        for entry in (ws.game/'RCM').glob('*/'+name):
            target=safe_target(ws.game,entry.parent/ARCHIVE)
            if target.is_file():paths.append(target)
    result=dict(sha256=sha(data),files=[dict(path=p.relative_to(ws.game/'RCM').as_posix(),verified=sha(p.read_bytes())==record['sha256']) for p in paths],native_engine_test=False)
    if not all(row['verified'] for row in result['files']):raise ValueError('La verificación del contenido compartido falló')
    ws.write('research/runtime_test/shared_content.json',json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
