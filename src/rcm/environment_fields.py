"""Proven NSD-v8 scene fields; no guessed offsets or baked-light changes."""
import math,struct
from pathlib import PurePosixPath
from .model import mapping
from .formats import fixed,cstring

FOG_MODES={'none':0,'linear':1,'exponential':2}


def read(tail):
    if len(tail)!=176:raise ValueError('Entorno NSD: bloque de 176 bytes requerido')
    return dict(music=cstring(tail[:32]),ambient=cstring(tail[32:64]),music_volume=struct.unpack_from('<I',tail,68)[0],ambient_volume=struct.unpack_from('<I',tail,72)[0],eax=struct.unpack_from('<I',tail,76)[0],fog_type=struct.unpack_from('<I',tail,80)[0],fog_color=list(struct.unpack_from('<3f',tail,84)),fog_start=struct.unpack_from('<f',tail,96)[0],fog_end=struct.unpack_from('<f',tail,100)[0],zclip=struct.unpack_from('<f',tail,104)[0])


def number(value,label,low=0,high=1e7):
    if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:raise ValueError(label+': número finito fuera de rango')
    return float(value)


def audio_file(resources,kind,ident):
    if ident=='':return ''
    if not isinstance(ident,str):raise ValueError('Audio inicial: selecciona un recurso')
    kinds={'.mp3','.wav'} if kind=='music' else {'.wav'}
    found=[r for r in resources['entries'] if r['extension'].lower() in kinds and r['id']==ident]
    if len(found)!=1:raise ValueError('Audio inicial: recurso ausente o ambiguo: '+ident)
    name=PurePosixPath(found[0]['path'].replace('\\','/')).name;fixed(name)
    return name


def validate(value,resources):
    mapping(value,{'music','ambient','music_volume','ambient_volume','fog','zclip','room_type'},label='Entorno de escena')
    if 'room_type' in value and (type(value['room_type']) is not int or not 0<=value['room_type']<=25):raise ValueError('Native room type: integer 0..25')
    for kind in ('music','ambient'):
        if kind in value:audio_file(resources,kind,value[kind])
        volume=kind+'_volume'
        if volume in value and (type(value[volume]) is not int or not 0<=value[volume]<=100):raise ValueError('Audio inicial: volumen 0..100')
    if 'zclip' in value:number(value['zclip'],'ZClip')
    if 'fog' in value:
        f=mapping(value['fog'],{'mode','color','start','end'},{'mode','color','start','end'},'Niebla')
        if f['mode'] not in FOG_MODES:raise ValueError('Niebla: modo no soportado')
        if not isinstance(f['color'],list) or len(f['color'])!=3 or any(type(v) is not int or not 0<=v<=255 for v in f['color']):raise ValueError('Niebla: color RGB 0..255')
        start=number(f['start'],'Niebla / Distancia 1');end=number(f['end'],'Niebla / Distancia 2')
        if f['mode']=='linear' and end<=start:raise ValueError('Niebla lineal: la distancia final debe superar a la inicial')
        if f['mode']=='exponential' and start>1:raise ValueError('Niebla exponencial: densidad entre 0 y 1')


def patch(tail,value,resources):
    validate(value,resources)
    if len(tail)!=176:raise ValueError('Entorno NSD: bloque de 176 bytes requerido')
    result=bytearray(tail)
    for kind,offset in [('music',0),('ambient',32)]:
        if kind in value:result[offset:offset+32]=fixed(audio_file(resources,kind,value[kind]))
    for key,offset in [('music_volume',68),('ambient_volume',72)]:
        if key in value:struct.pack_into('<I',result,offset,value[key])
    if 'zclip' in value:struct.pack_into('<f',result,104,value['zclip'])
    if 'fog' in value:
        f=value['fog'];struct.pack_into('<I3f2f',result,80,FOG_MODES[f['mode']],*f['color'],f['start'],f['end'])
    return bytes(result)
