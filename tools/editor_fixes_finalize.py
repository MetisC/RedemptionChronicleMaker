"""Record final editor fix evidence and a recoverable source snapshot."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm import __version__
from rcm.catalogue import verify_sources,digest
from rcm.paths import Workspace
from rcm.deployment import default_game
out=ROOT/'research/phase9/editor_fixes'
def read(name):return json.loads((out/name).read_text(encoding='utf8'))
full=read('full_tests.json');focused=read('focused_tests.json');gui=read('gui/probe.json');colors=read('gui/colors.json');portable=read('portable_probe.json');binary=read('final_binary_diagnostics.json');update=read('portable_update.json')
if not all([full['successful'],focused['successful'],gui['success'],colors['success'],portable['exit_code']==0,binary['rcm']==__version__,update['workspace_preserved']]):raise ValueError('Final evidence failed')
originals=verify_sources(Workspace(ROOT,default_game(ROOT)),default_game(ROOT))
if not originals['hashes_match']:raise ValueError('Original sources modified')
source_hashes={};archive=out/'sources_0.9.1.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    paths=[]
    for folder in ['src','tools','tests','docs','chronicles']:paths.extend((ROOT/folder).rglob('*'))
    paths.extend(ROOT/name for name in ['README.md','AGENTS.md','pyproject.toml','requirements.txt','requirements-editor.txt','requirements-dev.txt'])
    for path in sorted(paths):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.pyc','.backup','.autosave'}:continue
        name=path.relative_to(ROOT).as_posix();data=path.read_bytes();z.writestr(name,data);source_hashes[name]=hashlib.sha256(data).hexdigest()
(out/'source_inventory.json').write_text(json.dumps(source_hashes,indent=2))
exe=Path(update['executable'])
result=dict(version=__version__,executable=str(exe),executable_sha256=digest(exe),full_suite=full,focused_suite=focused,real_gui=gui,rendered_colors=colors,portable_probe=portable,binary_diagnostics=binary,update=update,originals=originals,source_snapshot=str(archive.relative_to(ROOT)),source_snapshot_sha256=digest(archive),game_launched=False,native_engine_test=False,hardware_cursor_test=False)
(out/'final_integrity.json').write_text(json.dumps(result,indent=2),encoding='utf8')
build_report=ROOT/'build/portable_build_report.json';report=json.loads(build_report.read_text());(out/'portable_build_staged.json').write_text(json.dumps(report,indent=2));report.update(executable=str(exe),jvm_bundled=str(exe.parent/'runtime'),version=__version__,executable_sha256=digest(exe));build_report.write_text(json.dumps(report,indent=2))
print(json.dumps({k:result[k] for k in ['version','executable','executable_sha256','originals','hardware_cursor_test']},indent=2))
