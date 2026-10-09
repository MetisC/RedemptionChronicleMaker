"""Persist local verification and a recoverable source checkpoint, excluding assets."""
from pathlib import Path
import hashlib,json,shutil,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.catalogue import verify_sources
from rcm.deployment import default_game
from rcm.packages import inspect_package


def main():
    ws=Workspace(ROOT,default_game(ROOT));originals=verify_sources(ws,ws.game)
    tests=json.loads(ws.output('build/tests/test_report.json').read_text(encoding='utf8'));quality=json.loads(ws.output('build/tests/quality_report.json').read_text(encoding='utf8'));probe=json.loads(ws.output('research/phase6/portable_probe.json').read_text(encoding='utf8'))
    if not tests['successful'] or not quality['successful'] or not probe['valid_project'] or not probe['real_gl']:raise ValueError('La verificación final conserva fallos; no crear checkpoint aceptado')
    package=ws.output('build/rcm_system/rcm_system.rcmpack');inspect_package(package)
    checkpoint=ws.output('research/checkpoints/phase6_source_final.zip');hashes={}
    with zipfile.ZipFile(checkpoint,'w',zipfile.ZIP_DEFLATED) as archive:
        for folder in ['src','tools','tests','docs','chronicles']:
            for path in sorted((ROOT/folder).rglob('*')):
                if not path.is_file() or '__pycache__' in path.parts or path.name.endswith(('.backup','.autosave','.pre_format5','.pyc')):continue
                relative=path.relative_to(ROOT).as_posix();data=path.read_bytes();archive.writestr(relative,data);hashes[relative]=hashlib.sha256(data).hexdigest()
        for name in ['README.md','AGENTS.md','pyproject.toml','requirements.txt','requirements-editor.txt','requirements-dev.txt']:
            data=(ROOT/name).read_bytes();archive.writestr(name,data);hashes[name]=hashlib.sha256(data).hexdigest()
    ws.write('research/checkpoints/phase6_source_final.json',json.dumps(hashes,indent=2))
    app=ws.output('build/portable/RedemptionChronicleMaker')
    shutil.copy2(ROOT/'README.md',app/'README.md');shutil.copytree(ROOT/'docs',app/'docs',dirs_exist_ok=True);shutil.copy2(ROOT/'tests/fixtures/chronicles/golden/expected.json',app/'examples/golden/expected.json')
    result={'created_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'originals':originals,'full_tests':tests,'static_gate':quality['successful'],'portable_probe':probe,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'portable_executable_sha256':hashlib.sha256((app/'RedemptionChronicleMaker.exe').read_bytes()).hexdigest(),'source_checkpoint':str(checkpoint),'source_files':len(hashes),'staging_empty':not any(ws.output('build/.staging').iterdir()),'native_acceptance':False,'private_beta_accepted':False}
    ws.write('research/phase6/final_integrity.json',json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
