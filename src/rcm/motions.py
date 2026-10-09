"""Catalogue actual NMS slots and Codex constants; never guess animation IDs."""
import hashlib
import json
import struct
import zipfile
from pathlib import PurePosixPath
from .formats import NotFile, cstring


def constants(data):
    pos=8
    def take(n):
        nonlocal pos
        if pos+n>len(data):raise ValueError('Codex.class truncado')
        result=data[pos:pos+n];pos+=n;return result
    def u2():return struct.unpack('>H',take(2))[0]
    def u4():return struct.unpack('>I',take(4))[0]
    if data[:4]!=bytes.fromhex('cafebabe'):raise ValueError('Codex.class inválido')
    pool={};i=1;count=u2()
    while i<count:
        tag=take(1)[0]
        if tag==1:pool[i]=take(u2()).decode('utf8')
        elif tag==3:pool[i]=struct.unpack('>i',take(4))[0]
        elif tag in (7,8):take(2)
        elif tag in (4,9,10,11,12):take(4)
        elif tag in (5,6):take(8);i+=1
        else:raise ValueError('Constant pool no reconocido')
        i+=1
    take(6);take(2*u2());result={}
    for unused in range(u2()):
        take(2);name,kind=pool[u2()],pool[u2()]
        for unused in range(u2()):
            attr=pool[u2()];payload=take(u4())
            if attr=='ConstantValue' and kind=='I' and name.startswith('MOTION_'):
                result[name[7:].lower()]=pool[struct.unpack('>H',payload)[0]]
    return result


def parse_nms(data,modes):
    result=[]
    for raw in data.decode('cp1252').splitlines():
        parts=raw.split(';',1)[0].split()
        if len(parts)<2 or parts[0].lower() not in modes or not parts[1].lower().endswith('.nad'):continue
        mode=parts[0].lower()
        result.append(dict(mode=mode,value=modes[mode],animation=parts[1],flags=parts[2:]))
    return result


def ensure_catalogue(ws,resources,game=None):
    codex=ws.output('research/original/Codex.nob/Codex.class')
    if not codex.is_file():return {'templates':{},'sets':{},'modes':{}}
    data=codex.read_bytes();signature=hashlib.sha256(data).hexdigest()
    dest=ws.output('cache/motions.json')
    if dest.is_file():
        cached=json.loads(dest.read_text(encoding='utf8'))
        if cached.get('version')==1 and cached.get('codex_sha256')==signature:return cached
    if game is None:
        from .deployment import default_game
        game=ws.game or default_game(ws.root)
    if game is None:return {'templates':{},'sets':{},'modes':{}}
    modes=constants(data);sets={};raw={}
    for archive in sorted(game.glob('*.nob')):
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if name.lower().endswith('.nms'):
                    key=PurePosixPath(name.replace('\\','/')).name.casefold()
                    sets.setdefault(key,[]).append(dict(archive=archive.name,path=name,slots=parse_nms(z.read(name),modes)))
    for entry in resources['entries']:
        if entry['extension'].lower()!='.not':continue
        path=ws.output('research/original/'+entry['archive']+'/'+entry['path'])
        for template in NotFile.read(path.read_bytes()).templates:raw.setdefault(template.name.casefold(),[]).append(template.values())
    def resolve(key,trail=()):
        records=raw.get(key.casefold(),[])
        if len(records)!=1 or key.casefold() in trail:return None
        v=records[0]
        if 9 in v:return cstring(v[9])
        return resolve(cstring(v[0]),trail+(key.casefold(),)) if 0 in v else None
    result=dict(version=1,codex_sha256=signature,modes=modes,sets=sets,templates={t['id']:resolve(t['id']) for t in resources['templates']})
    ws.write(dest,json.dumps(result,ensure_ascii=False,indent=2));return result


def slots(resources,template,trail=()):
    catalogue=resources.get('motion_catalogue',{})
    candidates=[r for r in resources.get('templates',[]) if r['id']==template]
    if len(candidates)!=1 or template in trail:return []
    row=candidates[0];motion_set=catalogue.get('templates',{}).get(template)
    if row.get('project_owned'):
        if row.get('motions'):motion_set=row['motions']
        else:return slots(resources,row.get('parent'),trail+(template,))
    if not motion_set:return []
    entries=catalogue.get('sets',{}).get(PurePosixPath(motion_set).name.casefold(),[])
    return entries[0]['slots'] if len(entries)==1 else []


LABELS={'stand':'Reposo','idle':'Gesto de reposo','talk':'Hablar','listen':'Escuchar'}
def label(slot):
    return f"{LABELS.get(slot['mode'],slot['mode'])} · {slot['mode']} · {slot['animation']}"


def validate_motion(mode,template,resources):
    match=next((s for s in slots(resources,template) if s['mode']==mode),None) if isinstance(mode,str) else None
    if match is None:
        raise ValueError('Animación no disponible para '+str(template)+': '+str(mode))
    return match['value']
