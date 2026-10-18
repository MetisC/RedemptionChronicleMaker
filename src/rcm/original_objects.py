"""Read-only static-scene references and explicit runtime object overrides."""
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from .formats import read_tags,cstring,scene_entity_hints
from .model import mapping

BITS=('captured','render','collide','visibility','camera','hidden','removed')
OPERATIONS=('hide','restore','remove','frame','pivot')


def selector(value):
    return {k:([float(x) for x in value[k]] if k=='position' else value[k]) for k in ('level','template','position','cast_id') if k in value and value[k] not in (None,'')}


def key(value):return hashlib.sha256(json.dumps(selector(value),sort_keys=True).encode()).hexdigest()[:16]


def targets(scene):
    result={}
    def scan(value):
        if isinstance(value,dict):
            if 'control_original' in value:result.setdefault(key(value['control_original']),selector(value['control_original']))
            if isinstance(value.get('interaction'),dict) and 'source' in value['interaction']:
                target=value['interaction']['source'];result.setdefault(key(target),selector(target))
            for v in value.values():scan(v)
        elif isinstance(value,list):
            for v in value:scan(v)
    scan(scene)
    return result


def validate(value,resources,level):
    mapping(value,{'level','template','position','cast_id','operation','frame','parameter','open'},{'level','template','operation'},'control_original')
    if value['level']!=level:raise ValueError('El objeto original pertenece a otro escenario; vuelve a elegirlo')
    rows=[t for t in resources['templates'] if t['id'].casefold()==str(value['template']).casefold() and not t.get('project_owned')]
    if len(rows)!=1 or rows[0]['kind']!='props':raise ValueError('Elige un objeto original de escenario único; no un personaje ni geometría fija')
    if value['operation'] not in OPERATIONS:raise ValueError('Operación sobre objeto original desconocida')
    if 'position' in value:
        p=value['position']
        if not isinstance(p,list) or len(p)!=3 or any(type(x) not in (float,int) or not math.isfinite(x) or abs(x)>1e7 for x in p):raise ValueError('Posición del objeto original inválida')
    cast=value.get('cast_id','')
    if not isinstance(cast,str) or (cast and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',cast)):raise ValueError('Cast ID del objeto original inválido')
    if not cast and 'position' not in value:raise ValueError('El objeto original necesita posición o Cast ID')
    if value['operation'] in {'frame','pivot'}:
        if type(value.get('frame')) is not int or not 0<=value['frame']<=255:raise ValueError('Frame de puerta: 0..255')
        n=value.get('parameter')
        if type(n) not in (float,int) or not math.isfinite(n) or not 0<n<=1000:raise ValueError('Parámetro de puerta: 0..1000')
        if type(value.get('open',True)) is not bool:raise ValueError('Dirección de puerta inválida')
    elif any(k in value for k in ('frame','parameter','open')):raise ValueError('Los parámetros de movimiento sólo se usan al mover una puerta')


def catalogue(backend,level_name):
    """Only the matching-stem static NSD, not replaced story-layout NPCs.

    Records are bounded tag-pattern hints, never a claim to decode arbitrary
    NSD blocks or baked NIL surfaces. Runtime identity is checked independently.
    """
    level=backend.levels.get(level_name,{});name=level.get('static_scene');hint=backend.hints.get(str(name).casefold())
    if not hint:return []
    source=hint['source']
    if source.get('imported_pack'):
        from .wtd import read_entry
        data=read_entry(backend.ws,source)
    else:data=backend.ws.output(Path('research/original')/source['archive']/source['path']).read_bytes()
    if hashlib.sha256(data).hexdigest()!=source['sha256']:raise ValueError('La escena estática original cambió; reconstruye los catálogos')
    cache_key=(level_name,source['sha256'],id(backend.original_resources))
    cache=getattr(backend,'_original_object_catalogue',{})
    if cache_key in cache:return cache[cache_key]
    templates={}
    for t in backend.original_resources['templates']:templates.setdefault(t['id'].casefold(),[]).append(t)
    result=[];seen=set();boundaries=[h['offset'] for h in scene_entity_hints(data)]+[len(data)-192]
    for match in re.finditer(rb'\x00\x00\x00\x00([A-Za-z_][A-Za-z_0-9]{2,31})\x00',data):
        offset=match.start()-4
        if offset<84:continue
        try:
            tags,end=read_tags(data,offset);v={t.id:t.value for t in tags}
            if len(v)!=len(tags) or 0 not in v or not 2<=len(tags)<=100:continue
            rows=templates.get(cstring(v[0]).casefold(),[])
            if len(rows)!=1 or rows[0]['kind']!='props':continue
            t=rows[0];cast=cstring(v[81]) if 81 in v else t.get('cast_id')
            if cast and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,30}',cast):cast=None
            position=list(struct.unpack('<3f',v[2][:12])) if 2 in v and 3 in v else None
            if position is not None and any(not math.isfinite(x) or abs(x)>1e7 for x in position):continue
            if position is None and not cast:continue
            target={'level':level_name,'template':t['id']}
            if position is not None:target['position']=position
            if cast:target['cast_id']=cast
            ident=key(target)
            if ident in seen:continue
            seen.add(ident)
            from .spatial.scene_mesh import find_brush
            brush=find_brush(data,end,next(p for p in boundaries if p>offset))
            result.append(dict(target,orientation=list(struct.unpack('<3f',v[1][:12])) if 1 in v else [0,0,0],sector=struct.unpack('<I',v[3][:4])[0] if 3 in v else None,origin=name,offset=offset,script=cstring(v[11]) if 11 in v else t.get('script'),model=t.get('model'),description_key=cstring(v[82]) if 82 in v else None,read_only=True,confidence='static NSD tag-pattern; runtime identity required',**brush))
        except (ValueError,struct.error):continue
    cache[cache_key]=result;backend._original_object_catalogue=cache
    return result
