"""Reproducible static audit of original bytecode, archives and scene hints."""
from pathlib import Path
import re,json,hashlib,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.formats import NotFile,cstring

def main():
    ws=Workspace(ROOT);dest=ws.output('research/dynamic_encounters');dest.mkdir(exist_ok=True)
    text=(ROOT/'research/ALL_CODEX.bytecode.txt').read_text(encoding='utf8');lines=text.splitlines()
    blocks=re.split(r'(?=Compiled from ")',text);calls=[];methods=[];classes=set()
    line_offset=0
    for block in blocks:
        match=re.search(r'^(?:public )?(?:(?:abstract|final) )?(?:class|interface) (\w+)',block,re.M)
        if not match:line_offset+=len(block.splitlines());continue
        cls=match[1];classes.add(cls);method='';rows=block.splitlines()
        for i,line in enumerate(rows):
            if re.match(r'  (?:public |private |protected |static |void )',line) and '(' in line and line.rstrip().endswith(';'):
                method=line.strip();methods.append({'class':cls,'signature':method})
            if re.search(r'// Method .*\.(?:SpawnThing|SpawnThingNear|CreateThing|PreloadTemplate):',line):
                calls.append({'class':cls,'method':method,'instruction':line.strip(),'line':line_offset+i+1,
                              'context':rows[max(0,i-12):i+16],
                              'related_calls':sorted(set(re.findall(r'// Method ([^:]+)',block))),
                              'strings':re.findall(r'// String (.*)',block),
                              'interpretation':'Bytecode callsite. Context/strings are evidence, not recovered source or asserted runtime behaviour.'})
        if cls in {'Generator','MysticSpawner','DisciplineSummonSoul','DisciplineSummonElemental','CodexThing','CodexWorld','CodexActor','Codex'}:
            ws.write(dest/(cls+'.bytecode.txt'),block)
        line_offset+=len(block.splitlines())
    hints=json.loads((ROOT/'cache/scene_hints.json').read_text(encoding='utf8'))
    uses=[]
    for scene,row in hints.items():
        for entity in row['entities']:
            if entity.get('script') in {'Generator','MysticSpawner'}:
                uses.append({'scene':scene,'source':row['source'],'entity':entity})
    templates=[]
    for path in (ROOT/'research/original').rglob('*.not'):
        for t in NotFile.read(path.read_bytes()).templates:
            if any(cstring(tag.value) in {'Generator','MysticSpawner'} for tag in t.tags if tag.id==11):
                templates.append({'template':t.name,'source':path.relative_to(ROOT).as_posix(),'tags':[{'id':tag.id,'hex':tag.value.hex()} for tag in t.tags]})
    # Inspect ALL archive names and script/reference bytes, including NSS/NSD
    # blocks whose variable parameters the scene-hint parser cannot decode.
    game=Path(r'H:\GOG\Vampire The Masquerade - Redemption');refs=[];archives={}
    for path in game.glob('*.nob'):
        with zipfile.ZipFile(path) as archive:
            archives[path.name]=len(archive.infolist())
            for entry in archive.infolist():
                if Path(entry.filename).suffix.lower() not in {'.nsd','.nss','.not','.nsc','.nmf','.class','.txt','.java'}:continue
                data=archive.read(entry)
                for pattern in (b'Generator',b'MysticSpawner'):
                    offsets=[m.start() for m in re.finditer(re.escape(pattern),data)]
                    if offsets:refs.append({'archive':path.name,'resource':entry.filename,'name':pattern.decode(),'offsets':offsets,'sha256':hashlib.sha256(data).hexdigest()})
    report={'classes_audited':len(classes),'spawn_calls':calls,'generator_scene_hints':uses,'generator_templates':templates,'archive_references':refs,'archives_scanned':archives,
            'health_related_callbacks':[m for m in methods if re.search(r'\b(?:damage|hurt|hit|killed|death)\(',m['signature'])],
            'rng_calls':sum('Method java/lang/Math.random:' in line for line in lines),
            'original_generator_found':True,'engine_native_test':False}
    ws.write(dest/'spawn_calls.json',json.dumps(report,ensure_ascii=False,indent=2))
    from rcm.service import Backend
    from rcm.enemy_catalogue import catalogue
    enemies=catalogue(Backend(ws));ws.write(dest/'enemy_catalogue.json',json.dumps(enemies,ensure_ascii=False,indent=2))
    print(json.dumps(dict(classes_audited=len(classes),spawn_calls=len(calls),archives_scanned=archives,original_generator_found=True,engine_native_test=False),ensure_ascii=False))

if __name__=='__main__':main()
