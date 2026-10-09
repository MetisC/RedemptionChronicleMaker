"""Deploy only our two examples to the existing shortcut's RCM directory.

No game launch. Original archives are read and verified, never changed.
"""
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import default_game
from rcm.deployment_many import deploy_many
from rcm.document import Document
from rcm.catalogue import verify_sources

def main():
    game=default_game(ROOT)
    if game is None:raise ValueError('No installation selected')
    ws=Workspace(ROOT,game)
    sources={}
    for ident,folder in [('rcm_tutor','tutorial'),('rcm_mini','mini_chronicle')]:
        sources[ident]=Document.load(ws,ROOT/'chronicles'/folder/'project.yaml').snapshot()
    result=deploy_many(ws,list(sources),'east_demo',sources)
    integrity=verify_sources(ws,game)
    ws.write('research/round0/original_integrity.json',json.dumps(integrity,indent=2))
    ws.write('research/round0/runtime_preparation.json',json.dumps(result,indent=2))
    print(json.dumps(dict(deployment=result,originals=integrity,game_launched=False),indent=2))

if __name__=='__main__':main()
