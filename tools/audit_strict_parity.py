"""Read original files, never run original authoring programs or the game."""
from pathlib import Path
import collections,csv,hashlib,json,re,struct,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cache/vendor'),str(ROOT/'cache/devtools'),str(ROOT/'src')]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
OUT=ROOT/'research/embrace_strict_parity'


def run():
    import pefile,capstone
    from rcm.formats import NotFile,cstring
    OUT.mkdir(exist_ok=True)
    raw=(GAME/'Vampire.exe').read_bytes();pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase
    cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.skipdata=True
    sec=next(s for s in pe.sections if s.Name.startswith(b'.text'))
    ins=list(cs.disasm(sec.get_data(),base+sec.VirtualAddress))
    ranges=[('environment_apply',0x4a8f10,0x4a9420),('map_callbacks',0x411130,0x411420),('interest_table',0x4a8050,0x4a8110),('parameter_loader',0x4a85ce,0x4a89a1)]
    for name,start,end in ranges:
        (OUT/(name+'.txt')).write_text('\n'.join(f'{i.address:08x}: {i.mnemonic} {i.op_str}' for i in cs.disasm(pe.get_data(start-base,end-start),start)),encoding='utf8')
    # Ordered 40-byte property-name/type table; anchor checked against known tags.
    start=raw.find(b'DESCRIPTIONID')-82*40
    props=[dict(id=i,name=cstring(raw[start+40*i:start+40*i+32]),metadata=list(struct.unpack_from('<II',raw,start+40*i+32))) for i in range(128)]
    assert all(props[i]['name'].lower()==s for i,s in [(1,'orientation'),(6,'foley'),(11,'script'),(92,'treasureclass')])
    (OUT/'property_table.json').write_text(json.dumps(props,indent=2))
    # Direct address consumers and pointer-table consumers are recorded separately.
    for token in ['interestNum','mapLocations','TREASURECLASS']:
        offset=raw.find(token.encode());address=base+pe.get_rva_from_offset(offset)
        targets=[address]
        for match in re.finditer(re.escape(struct.pack('<I',address)),raw):
            if match.start()>=sec.PointerToRawData+sec.SizeOfRawData:targets.append(base+pe.get_rva_from_offset(match.start()))
        hits=[i for i,x in enumerate(ins) if any(hex(a) in x.op_str for a in targets)]
        (OUT/(token+'_consumers.txt')).write_text('\n\n'.join('\n'.join(f'{v.address:08x}: {v.mnemonic} {v.op_str}' for v in ins[max(0,i-18):i+40]) for i in hits))
    env=[];treasure=[];ai=[];foley=[]
    with zipfile.ZipFile(GAME/'Resource.nob') as z:
        for name in z.namelist():
            if name.lower().endswith('.nsd'):
                tail=z.read(name)[-176:]
                env.append(dict(path=name,sha256=hashlib.sha256(tail).hexdigest(),music=cstring(tail[:32]),ambient=cstring(tail[32:64]),ints=list(struct.unpack_from('<12I',tail,64)),floats=list(struct.unpack_from('<12f',tail,64))))
            if name.lower().endswith('.not'):
                for t in NotFile.read(z.read(name)).templates:
                    for tag in t.tags:
                        if tag.id==92:treasure.append(dict(library=name,template=t.name,value=struct.unpack_from('<I',tag.value)[0],raw=tag.value.hex()))
            if name.lower().endswith('.nai'):
                match=re.search(r'(?im)^interestNum[ \t]+(\S+)',z.read(name).decode('cp1252'))
                if match:ai.append(dict(path=name,interestNum=match[1]))
            if name.lower().endswith('.nfo'):foley.append(name)
        ntt=z.read('misc/game.ntt').decode('cp1252');(OUT/'game.ntt').write_text(ntt,encoding='utf8')
    classes=[];comment='';current=None
    for line in ntt.splitlines():
        if line.strip().startswith('//') and line.strip()[2:].strip():comment=line.strip()[2:].strip()
        match=re.match(r'CLASS:\s*(\d+)\s*$',line)
        if match:
            current=dict(id=int(match[1]),description=comment,items=[]);classes.append(current)
        elif line.startswith('CITEM:') and current:current['items'].append(line.split()[1:])
    (OUT/'treasure_catalogue.json').write_text(json.dumps(classes,indent=2))
    (OUT/'treasure_references.json').write_text(json.dumps(treasure,indent=2))
    (OUT/'interest_ai.json').write_text(json.dumps(ai,indent=2))
    (OUT/'environment_corpus.json').write_text(json.dumps(env,indent=2))
    with (OUT/'environment_profiles.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.writer(f);writer.writerow(['path','music','ambient',*[str(i) for i in range(64,112,4)]])
        for row in env:writer.writerow([row['path'],row['music'],row['ambient'],*row['ints']])
    maps=[]
    with zipfile.ZipFile(GAME/'Local_Eng.nob') as z:
        for name in z.namelist():
            if not name.lower().startswith('ui/map') or not name.lower().endswith('.nui'):continue
            text=z.read(name).decode('cp1252');(OUT/Path(name).name).write_text(text,encoding='utf8')
            maps.append(dict(path=name,sha256=hashlib.sha256(z.read(name)).hexdigest(),points=[dict(name=m[1],x=int(m[2]),y=int(m[3])) for m in re.finditer(r'element imagearray name=(\w+).*?pos=(-?\d+),(-?\d+)',text)],tiles=re.findall(r'quad mat=(\S+)',text)))
    (OUT/'map_catalogue.json').write_text(json.dumps(maps,indent=2))
    result=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),vampire_sha256=hashlib.sha256(raw).hexdigest(),original_scenes=len(env),treasure_references=len(treasure),treasure_classes=len(classes),interest_ai_values=dict(collections.Counter(r['interestNum'] for r in ai)),maps=len(maps),foley_files=foley,native_game_test=False)
    (OUT/'source_identity.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))


if __name__=='__main__':run()
