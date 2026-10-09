"""Named arrival and movement layers. They never edit NIL geometry or portals."""
import math
from .model import mapping,sequence,identifier,text

def validate_markers(scene,actors):
    points={}
    for kind in ('entries','waypoints'):
        rows={}
        for row in sequence(scene.get(kind,[]),kind):
            mapping(row,{'id','name','transform'},{'id','name','transform'},kind)
            key=identifier(row['id'],kind+'.id',16);text(row['name'],kind+'.name')
            if key in rows:raise ValueError(kind+': ID duplicado')
            transform=mapping(row['transform'],{'position','orientation','placement'},{'position','orientation'},kind+'.transform')
            if transform.get('placement','absolute')!='absolute':raise ValueError('Marcadores requieren posición absoluta')
            for field in ('position','orientation'):
                vector=transform[field]
                if not isinstance(vector,list) or len(vector)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e7 for v in vector):raise ValueError('Transform de marcador inválido')
            rows[key]=row
        points[kind]=rows
    if scene.get('default_entry') not in (None,*points['entries']):raise ValueError('Entrada inicial ausente')
    paths={}
    for row in sequence(scene.get('paths',[]),'paths'):
        mapping(row,{'id','name','actor','points','loop','tolerance','speed'},{'id','name','actor','points'},'path')
        key=identifier(row['id'],'path.id',16);text(row['name'],'path.name')
        if key in paths:raise ValueError('Recorrido duplicado')
        if row['actor'] not in actors:raise ValueError('Actor del recorrido ausente')
        route=sequence(row['points'],'path.points')
        if not 2<=len(route)<=128 or any(not isinstance(p,str) or p not in points['waypoints'] for p in route):raise ValueError('Recorrido requiere 2..128 waypoints existentes')
        if type(row.get('loop',False)) is not bool:raise ValueError('path.loop requiere booleano')
        value=row.get('tolerance',24)
        if type(value) not in (int,float) or not math.isfinite(value) or not 1<=value<=256:raise ValueError('Tolerancia de llegada: 1..256')
        speed=row.get('speed',90)
        if type(speed) not in (int,float) or not math.isfinite(speed) or not 1<=speed<=1000:raise ValueError('Parámetro de movimiento: 1..1000')
        paths[key]=row
    # Concurrent commands to one actor would fight over the engine pathfinder.
    if len({p['actor'] for p in paths.values()})!=len(paths):raise ValueError('Un solo recorrido por actor; duplica waypoints para otro actor')
    return paths
