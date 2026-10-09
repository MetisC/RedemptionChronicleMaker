"""Refresh the two owned examples after their final build, with backups."""
from pathlib import Path
import argparse,json,sys,time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src')]
from rcm.paths import Workspace
from rcm.file_transaction import replace_files

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',default='build/portable_update_096');args=parser.parse_args()
    ws=Workspace(ROOT)
    app=ws.output('build/portable/RedemptionChronicleMaker')
    stage=ws.output(args.stage+'/RedemptionChronicleMaker')
    targets={}
    for name in ('tutorial','mini_chronicle'):
        folder=ROOT/'chronicles'/name
        for source in folder.rglob('*'):
            if not source.is_file():continue
            relative=source.relative_to(folder)
            for destination in (app/'workspace/chronicles'/name,stage/'examples'/name):
                targets[ws.output(destination/relative)]=source.read_bytes()
    for ident in ('rcm_tutor','rcm_mini'):
        folder=ROOT/'build'/ident
        for source in folder.rglob('*'):
            if source.is_file():targets[ws.output(app/'workspace/build'/ident/source.relative_to(folder))]=source.read_bytes()
    for source in (ROOT/'docs').rglob('*'):
        if source.is_file():targets[ws.output(stage/'docs'/source.relative_to(ROOT/'docs'))]=source.read_bytes()
    targets[ws.output(stage/'README.md')]=(ROOT/'README.md').read_bytes()
    backup=ws.output('research/round0/examples_refresh_'+str(time.time_ns())+'.zip')
    replace_files(targets,[],backup,ROOT,ws.output)
    result=dict(files=len(targets),backup=str(backup),visible_projects=['tutorial','mini_chronicle'],user_settings_preserved=True)
    ws.write('research/round0/examples_refresh.json',json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
