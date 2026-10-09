"""Final read-only build/deployment audit. Never writes into the game."""
from pathlib import Path
import sys,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import source_fingerprint
from rcm.catalogue import verify_sources
from rcm.deployment import safe_target
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption');ws=Workspace(ROOT,GAME)
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf8'))
report=read('build/phase4_demo/build_report.json');acceptance=read('build/campaign/acceptance/report.json')
tests=read('build/tests/test_report.json');regression=read('research/phase4/final_regression.json')
assert tests['successful'] and acceptance['successful'] and not acceptance['problems']
assert report['distribution_files']==acceptance['build']['distribution_files'],'GUI/CLI packages differ'
assert report['authoring_source_sha256']==source_fingerprint((ROOT/'tests/fixtures/chronicles/phase4_demo/project.yaml').read_text(encoding='utf8'))
assert report['status']=='compiled-unverified-in-game' and set(report['class_versions'].values())=={'45.3'}
assert len(regression)==5 and all(r['source_unchanged'] and r['real_gl'] for r in regression)
checked=0
for folder in ['phase4_demo','east_demo']:
    for relative,row in report['distribution_files'].items():
        p=safe_target(GAME,GAME/'RCM'/folder/relative)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'Deploy stale: '+str(p)
        checked+=1
with zipfile.ZipFile(ROOT/'research/checkpoints/phase3_before_phase4.zip') as z:
    assert z.read('tests/fixtures/chronicles/phase3_demo/project.yaml')==(ROOT/'tests/fixtures/chronicles/phase3_demo/project.yaml').read_bytes(),'Old source changed'
result={'successful':True,'tests':tests['tests'],'gui_cli_identical':True,'deployed_files_checked':checked,'originals':verify_sources(ws,GAME),'phase3_source_matches_checkpoint':True,'native_engine_run':False,'phase5_started':False}
ws.write('research/phase4/final_check.json',json.dumps(result,indent=2));print(json.dumps(result,indent=2))
