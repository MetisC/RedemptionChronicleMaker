"""Preserve the pre-implementation sources and scoped historical user evidence."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'research/phase9';dest.mkdir(parents=True,exist_ok=True)
archive=dest/'before_implementation.zip'
if not archive.exists():
    hashes={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for folder in ['src','tools','tests','docs','chronicles']:
            for path in sorted((ROOT/folder).rglob('*')):
                if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.pyc','.backup','.autosave'}:continue
                name=path.relative_to(ROOT).as_posix();data=path.read_bytes();z.writestr(name,data);hashes[name]=hashlib.sha256(data).hexdigest()
        for name in ['AGENTS.md','README.md','pyproject.toml','requirements.txt','requirements-editor.txt','requirements-dev.txt']:
            data=(ROOT/name).read_bytes();z.writestr(name,data);hashes[name]=hashlib.sha256(data).hexdigest()
    (dest/'before_implementation.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
evidence={'version':'0.7.0','chronicle':'Londres: prueba de estabilización','source':'user report in chat',
 'statement':'He entrado. Las 3 PNJS y las conversaciones van bien. Una de ellas me dice de teleportarme y me teleporta a un sitio donde hay muchos punkis que me matan en pocos segundos, entiendo que está bien',
 'observed':['three NPC interactions','conversations generally functional','transition to another location','enemy attacks at destination'],
 'not_verified':['abort','all first-rejection paths','save/load','reentry','reward idempotence','full custom NOT/AI properties','network'],
 'issue':'Arrival and combat must be separated for the acceptance circuit','transfers_to_phase9':False,'native_tests_deferred_by_user':True}
(dest/'phase7_user_observation.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf8')
print('Checkpoint and scoped user observation preserved')
