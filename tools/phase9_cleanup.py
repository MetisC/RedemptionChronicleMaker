"""Replace our historical deployed demos with one circuit, inside RCM only.

Every path is preflighted; old bytes are archived in the workspace before any
replacement. Unknown files are preserved. This never touches saves elsewhere,
original archives, shortcuts or executables, and never starts Vampire.
"""
from pathlib import Path
import hashlib,json,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import configured_game,safe_target,game_running,default_game
from rcm.file_transaction import replace_files
from rcm.packages import archive_path

OLD={'east_demo','east_compare','editor_playtest','phase3_demo','phase4_demo','phase5_demo','rcm_stable','rcm_system'}
FOLDERS=OLD-{'east_compare'}

def owned(path):
    name=path.name
    if path.suffix=='.nob' and path.stem in OLD:
        with zipfile.ZipFile(path) as z:
            names=[n for n in z.namelist() if n.startswith('chronicles/') and n.endswith('.nsc')]
            return bool(names) and all(Path(n).stem in OLD|{'rcm_east_base','rcm_east_scene'} for n in names)
    if path.suffix=='.class':return any(name.startswith('R_'+key+'_') for key in OLD) or name in {'RCM5Actor.class','RCM6Actor.class','RCM7Actor.class'}
    if name in {'runtime_trace.log','runtime_trace.log.1'}:return True
    if name in {'.rcm_manifest.json','.rcm_deployment.json'}:
        data=json.loads(path.read_text(encoding='utf8'))
        return data.get('id',data.get('chronicle')) in OLD or data.get('package',{}).get('id') in OLD
    return False

def main():
    ws=Workspace(ROOT,default_game(ROOT));game=configured_game(ws);root=safe_target(game,game/'RCM')
    if game_running():raise ValueError('Vampire está abierto; no se ha retirado ningún archivo')
    report=json.loads(ws.output('build/rcm_circuit/build_report.json').read_text(encoding='utf8'))
    if report['status']!='compiled-unverified-in-game':raise ValueError('Circuito sin compilación válida')
    target=safe_target(game,root/'east_demo');files={}
    for relative,record in report['distribution_files'].items():
        archive_path(relative);path=ws.output('build/rcm_circuit/bundle/'+relative);data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Build modificado: '+relative)
        files[safe_target(game,target/relative)]=data
    manifest=target/'.rcm_deployment.json'
    files[safe_target(game,manifest)]=json.dumps({'format':1,'chronicle':'rcm_circuit','files':{p.relative_to(target).as_posix():hashlib.sha256(d).hexdigest() for p,d in files.items()}},indent=2).encode('utf8')
    obsolete=[];foreign=[];directories=[]
    for name in sorted(FOLDERS):
        directory=safe_target(game,root/name)
        if not directory.is_dir():continue
        for path in directory.rglob('*'):
            safe_target(game,path)
            if path.is_dir():directories.append(path)
            elif path.is_file() and path not in files:
                (obsolete if owned(path) else foreign).append(path)
        directories.append(directory)
    # Backups are complete and verified by replace_files before deletion starts.
    backup=ws.output('research/phase9/retired_rcm_'+str(time.time_ns())+'.zip')
    replace_files(files,obsolete,backup,root,lambda p:safe_target(game,p))
    for directory in sorted(set(directories),key=lambda p:len(p.parts),reverse=True):
        safe_target(game,directory)
        if directory.is_dir() and not any(directory.iterdir()):directory.rmdir()
    safe_target(game,root/'rcm_circuit').mkdir(parents=True,exist_ok=True)
    result={'chronicle':'rcm_circuit','visible_name':'Las voces de Londres · Circuito','destination':str(target),'backup':str(backup),'removed':[p.relative_to(root).as_posix() for p in obsolete],'preserved_foreign':[p.relative_to(root).as_posix() for p in foreign],'deployed':{p.relative_to(root).as_posix():hashlib.sha256(d).hexdigest() for p,d in files.items()},'native_engine_test':False,'game_launched':False}
    prior=ws.output('research/phase9/deployment_cleanup.json')
    if prior.exists():
        previous=json.loads(prior.read_text(encoding='utf8'))
        result['earlier_backups']=previous.get('earlier_backups',[])+[previous['backup']]
        result['removed']=sorted(set(result['removed']+previous['removed']))
    ws.write('research/phase9/deployment_cleanup.json',json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('removed','deployed')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
