"""Native NSD entrance records; no relocation through SetPosition on arrival.

The v8 loader reads 60-byte sector/matrix/entry/player records (0x4a7fc9).
TeleportPartyToEntrance refreshes the actor's floor polygon (0x4b0b18).
"""
import hashlib
import json
import math
import struct
import zipfile
import zlib


def enabled(campaign,scene):
    return bool(scene.get('entries')) and (campaign.source.get('runtime_profile')=='phase10' or any('interaction' in o for o in scene.get('objects',[])) or any(c.get('staging') for c in scene.get('conversations',[])))


def ordered(scene):
    rows=scene.get('entries',[])
    return sorted(rows,key=lambda e:e['id']!=scene.get('default_entry'))


def validate_record(data):
    if len(data)!=60:raise ValueError('NSD: invalid entrance record size')
    sector,*values,entry,player=struct.unpack('<I12fII',data)
    if sector>=100000 or entry>4095 or player>8 or not all(math.isfinite(v) and abs(v)<1e7 for v in values):raise ValueError('NSD: invalid entrance values')
    axes=[values[i:i+3] for i in (0,3,6)]
    if any(abs(sum(v*v for v in axis)-1)>.01 for axis in axes) or any(abs(sum(a*b for a,b in zip(axes[i],axes[j])))>.01 for i,j in ((0,1),(0,2),(1,2))):raise ValueError('NSD: invalid entrance orientation')
    return data


def cache_path(ws,entry):
    identity={k:entry.get(k) for k in ('archive','path','crc32','size','imported_pack')}
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    return ws.output('cache/levels/'+key+'-sectors.json'),identity


def planes(ws,level):
    entry=level['geometry'][0];path,identity=cache_path(ws,entry)
    if ws.game or entry.get('imported_pack'):
        if entry.get('imported_pack'):
            from .wtd import read_entry
            data=read_entry(ws,entry)
        else:
            with zipfile.ZipFile(ws.game/entry['archive']) as archive:data=archive.read(entry['path'])
        if len(data)!=entry['size'] or entry.get('crc32') and format(zlib.crc32(data),'08x')!=entry['crc32'].lower():raise ValueError('La geometría no coincide con el catálogo')
        from .spatial.geometry import read_nil
        result=read_nil(data).sector_planes
        ws.write(path,json.dumps({'identity':identity,'planes':result},separators=(',',':')))
    else:
        if not path.is_file():raise ValueError('Selecciona la instalación para comprobar los puntos de llegada')
        record=json.loads(path.read_text(encoding='utf8'))
        if record.get('identity')!=identity:raise ValueError('Catálogo de sectores incompatible')
        result=record['planes']
    if not isinstance(result,list) or not 1<=len(result)<=100000:raise ValueError('Catálogo de sectores inválido')
    for sector in result:
        if not isinstance(sector,list) or len(sector)>255 or any(not isinstance(p,list) or len(p)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p) for p in sector):raise ValueError('Planos de sector inválidos')
    return result


def sector_at(sectors,position):
    # NIL inward normals use dot(n,p)>=distance. Probe just above the feet.
    p=[float(position[0]),float(position[1]),float(position[2])+.05]
    matches=[i for i,rows in enumerate(sectors) if rows and all(sum(a*b for a,b in zip(plane[:3],p))-plane[3]>=-.01 for plane in rows)]
    if not matches:raise ValueError('Punto de llegada fuera de los sectores del escenario: '+str(position))
    return matches[0]


def records(ws,level,scene):
    sectors=planes(ws,level);result=[]
    for i,entry in enumerate(ordered(scene)):
        pos=entry['transform']['position'];sector=sector_at(sectors,pos)
        # The native loader accepts an identity basis. Authored orientation is
        # applied with SetOrientation after the native relocation succeeds.
        result.append(validate_record(struct.pack('<I12fII',sector,1,0,0,0,1,0,0,0,1,*pos,i,0)))
    return result
