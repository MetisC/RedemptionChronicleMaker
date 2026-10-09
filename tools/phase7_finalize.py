"""Freeze Phase 7 evidence without changing historical Phase 6 acceptance."""
from pathlib import Path
import hashlib,json,shutil,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.catalogue import verify_sources
from rcm.deployment import default_game
from rcm.packages import inspect_package
from rcm import __version__
ws=Workspace(ROOT,default_game(ROOT))
tests=json.loads(ws.output('build/tests/test_report.json').read_text(encoding='utf8'))
quality=json.loads(ws.output('build/tests/quality_report.json').read_text(encoding='utf8'))
probe_path=ws.output('build/phase7_portable_probe/build/portable_smoke.json')
probe=json.loads(probe_path.read_text(encoding='utf8'))
if not tests['successful'] or not quality['successful'] or not probe.get('valid_project') or not probe.get('real_gl'):raise ValueError('Comprobaciones técnicas pendientes o fallidas')
ws.write('research/phase7/portable_probe.json',json.dumps(probe,indent=2))
originals=verify_sources(ws,ws.game)
package=ws.output('build/rcm_stable/rcm_stable.rcmpack');manifest,_=inspect_package(package)
deployment=json.loads(ws.output('research/phase7/deployment.json').read_text(encoding='utf8'))
for relative,digest in deployment['deployment']['files'].items():
    if hashlib.sha256((ws.game/'RCM'/relative).read_bytes()).hexdigest()!=digest:raise ValueError('El deploy difiere del build: '+relative)
report=json.loads(ws.output('build/rcm_stable/build_report.json').read_text(encoding='utf8'))
for path,record in report['distribution_files'].items():
    deployed=Path(deployment['deployment']['destination'])/path
    if hashlib.sha256(deployed.read_bytes()).hexdigest()!=record['sha256']:raise ValueError('El build y el deploy no coinciden')
checkpoint=ws.output('research/checkpoints/phase7_source_final.zip');hashes={}
with zipfile.ZipFile(checkpoint,'w',zipfile.ZIP_DEFLATED) as archive:
    for folder in ['src','tools','tests','docs','chronicles']:
        for path in sorted((ROOT/folder).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.name.endswith(('.backup','.autosave','.pre_format5','.pyc')):continue
            name=path.relative_to(ROOT).as_posix();data=path.read_bytes();archive.writestr(name,data);hashes[name]=hashlib.sha256(data).hexdigest()
    for name in ['README.md','AGENTS.md','pyproject.toml','requirements.txt','requirements-editor.txt','requirements-dev.txt']:
        data=(ROOT/name).read_bytes();archive.writestr(name,data);hashes[name]=hashlib.sha256(data).hexdigest()
ws.write('research/checkpoints/phase7_source_final.json',json.dumps(hashes,indent=2))
app=ws.output('build/portable/RedemptionChronicleMaker')
shutil.copy2(ROOT/'README.md',app/'README.md');shutil.copytree(ROOT/'docs',app/'docs',dirs_exist_ok=True)
shutil.copytree(ROOT/'chronicles/phase7_demo',app/'examples/phase7_demo',dirs_exist_ok=True)
result={'version':__version__,'created_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'full_tests':tests,'quality':quality['successful'],'originals':originals,'portable_probe':probe,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'package_requires_rcm':manifest['requires_rcm'],'portable_executable_sha256':hashlib.sha256((app/'RedemptionChronicleMaker.exe').read_bytes()).hexdigest(),'source_checkpoint':str(checkpoint),'source_files':len(hashes),'deployed_hashes_match':True,'native_acceptance':False,'clean_machine_test':False,'private_beta_accepted':False}
ws.write('research/phase7/final_integrity.json',json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['version','quality','deployed_hashes_match','native_acceptance','source_files']},indent=2))
