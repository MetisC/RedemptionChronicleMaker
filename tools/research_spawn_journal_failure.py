"""Persist read-only evidence from the original PE research copy and NOT."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from native_disassembly import disassemble
from rcm.formats import NotFile,cstring

out=ROOT/'research/round0/npc_journal_fix';out.mkdir(parents=True,exist_ok=True)
pe=ROOT/'research/user_directory/Vampire.exe'
(out/'native_factories.txt').write_text('Original PE SHA256 '+hashlib.sha256(pe.read_bytes()).hexdigest()+'\nCreateThing JNI (native method table pointer at file offset 0x111148)\n'+disassemble(0x477260,370)+'\nSpawnThingNear JNI\n'+disassemble(0x473b70,260),encoding='utf8')
rows=[]
for file in (ROOT/'research/original').rglob('*.not'):
    for template in NotFile.read(file.read_bytes()).templates:
        if template.name in {'businessWoman','_civilians_MD'}:
            values=template.values()
            rows.append(dict(template=template.name,source=str(file.relative_to(ROOT)),ai=cstring(values[56]) if 56 in values else None,parent=cstring(values[0]) if 0 in values else None))
(out/'original_ai_reference.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps(dict(original_records=rows,native_proof=str(out/'native_factories.txt'),game_launched=False),indent=2))
