"""Non-destructive developer CLI for the editor diagnostic."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
def main():
    from rcm.paths import Workspace
    from rcm.deployment import default_game
    from rcm.diagnostics import diagnostic_report
    from rcm.managed_deployments import list_deployments
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path);parser.add_argument('--workspace',type=Path,default=ROOT);args=parser.parse_args()
    ws=Workspace(args.workspace,args.game or default_game(args.workspace));report=diagnostic_report(ws)
    if ws.game:report['deployments']=[dict(id=r['id'],modified=r['modified']) for r in list_deployments(ws)]
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
