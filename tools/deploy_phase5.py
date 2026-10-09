"""Prepare the authorized RCM demo; preserve old tests and audit every write."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import deploy,game_running,safe_target
from rcm.catalogue import verify_sources

GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
ws=Workspace(ROOT,GAME)
if game_running():raise SystemExit('Cierra Vampire antes del despliegue')
safe_target(GAME,GAME/'RCM/phase5_demo')
safe_target(GAME,GAME/'RCM/east_demo')
def hashes():
    result={}
    for p in (GAME/'RCM').rglob('*'):
        safe_target(GAME,p)
        if p.is_file():result[p.relative_to(GAME/'RCM').as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return result
originals=verify_sources(ws,GAME)
before=hashes()
out=ROOT/'research/phase5';out.mkdir(parents=True,exist_ok=True)
stamp=str(time.time_ns())
(out/('rcm_before_'+stamp+'.json')).write_text(json.dumps(before,indent=2),encoding='utf8')
standalone=deploy(ws,'phase5_demo')
shared=deploy(ws,'phase5_demo','east_demo')
after=hashes()
allowed={k.replace('\\','/') for r in [standalone,shared] for k in r['files']}
unchanged={k for k,v in before.items() if after.get(k)==v}
changed={k for k in set(before)|set(after) if before.get(k)!=after.get(k)}
if not changed<=allowed:raise RuntimeError('Cambio inesperado en RCM: '+str(changed-allowed))
if not set(before)-allowed<=unchanged:raise RuntimeError('Se modificó una prueba anterior')
verified=verify_sources(ws,GAME)
result={'standalone':standalone,'existing_shortcut':shared,'previous_files_preserved':len(unchanged),'changed_files':sorted(changed),'originals_before':originals,'originals_after':verified,'native_engine_test':False}
ws.write('research/phase5/deployment_audit.json',json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))

