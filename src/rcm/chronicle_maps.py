"""Own informational maps: native NUI/TGA/NLS and NSC location bindings."""
import io
import math
from .model import mapping,identifier,text


def labels(chronicle,map_id,point_id=None):
    import hashlib
    stem='M_'+hashlib.sha256((chronicle+'/'+map_id).encode()).hexdigest()[:12]
    return stem if point_id is None else stem+'_'+point_id


def map_image(path):
    from PIL import Image
    if path.stat().st_size>32*1024*1024:raise ValueError('Map image: maximum 32 MiB')
    try:
        with Image.open(path) as image:
            if min(image.size)<1 or max(image.size)>4096:raise ValueError('Map image: maximum 4096 pixels per axis')
            return image.convert('RGB').resize((640,480),Image.Resampling.LANCZOS)
    except Image.DecompressionBombError as error:raise ValueError('Map image: maximum 4096 pixels per axis') from error


def validate(row,scenes):
    mapping(row,{'id','name','source','original','points'},{'id','name','points'},'Map')
    identifier(row['id'],'map.id',16);text(row['name'],'map.name')
    if ('source' in row)==('original' in row) or not isinstance(row.get('source',row.get('original')),str):raise ValueError('Choose one map image source: own image or original game map')
    if not isinstance(row['points'],list) or len(row['points'])>128:raise ValueError('Map: maximum 128 locations')
    seen=set()
    for point in row['points']:
        mapping(point,{'id','name','position','visible','haven'},{'id','name','position'},'Map location')
        identifier(point['id'],'map.point.id',16);text(point['name'],'map.point.name')
        if point['id'].casefold() in seen:raise ValueError('Duplicate map location')
        seen.add(point['id'].casefold())
        pos=point['position']
        if not isinstance(pos,list) or len(pos)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in pos) or not 0<=pos[0]<=624 or not 0<=pos[1]<=464:raise ValueError('Map position: X 0..624, Y 0..464')
        for key in ('visible','haven'):
            if type(point.get(key,False)) is not bool:raise ValueError('Map flags require booleans')
        for value in (point['name'],):
            if any(c in value for c in '\r\n\0'):raise ValueError('Map location name requires one line')
            value.encode('cp1252')


def prepare(ws,source,resources=None):
    payload={};catalogue={};names={};ids=set()
    if len(source.get('resources',{}).get('maps',[]))>16:raise ValueError('Map authoring budget: maximum 16 maps')
    for row in source.get('resources',{}).get('maps',[]):
        validate(row,source['scenes'])
        if row['id'].casefold() in ids:raise ValueError('Duplicate map ID')
        ids.add(row['id'].casefold())
        stem=labels(source['chronicle']['id'],row['id']);lines=['name='+stem,'pos=0,0']
        if 'original' in row:
            from .original_maps import read
            original=read(ws,resources or {},row['original'])
            for quad in original['quads']:
                x,y=quad['position'];w,h=quad['size'];lines.append(f'quad mat={quad["material"]} pos={x},{y} size={w},{h}')
        else:
            image=map_image(ws.output(row['source']))
        # Original NUI Y axis is bottom-up; TGA maintains ordinary image rows.
        index=0
        for bottom,height in (() if 'original' in row else ((224,256),(96,128),(32,64),(0,32))):
            for left,width in ((0,256),(256,256),(512,128)):
                index+=1;name=stem+f'_{index:02d}.tga';tile=image.crop((left,480-bottom-height,left+width,480-bottom));out=io.BytesIO();tile.save(out,format='TGA')
                payload['ui/Materials/'+name]=out.getvalue();lines.append(f'quad mat={name} pos={left},{bottom} size={width},{height}')
        lines.append('element textbox maxitems=1 name=mapLocations flags=0x02 textboxflags=0x03 pos=0,0 size=640,16')
        points={}
        for point in row['points']:
            label=labels(source['chronicle']['id'],row['id'],point['id']);x,y=point['position']
            lines.append(f'element imagearray name={label} size=16,16 flags=0x08 pos={round(x)},{round(y)}')
            names[label]=point['name'];points[point['id']]=dict(point,label=label)
        lines.append('element button name=MapCloseButton pos=300,16 size=40,34 bitmap=closeButton depressed=closeButtonDep')
        payload['ui/'+stem+'.nui']=('\r\n'.join(lines)+'\r\n').encode('cp1252')
        catalogue[row['id']]=dict(file=stem+'.nui',points=points)
    for scene in source['scenes']:
        binding=scene.get('map_location')
        if binding is not None:resolve(binding,catalogue)
    return payload,catalogue,names


def resolve(binding,catalogue):
    mapping(binding,{'map','point'},{'map','point'},'Scene map location')
    row=catalogue.get(binding['map'])
    if not row or binding['point'] not in row['points']:raise ValueError('Map location missing')
    return row,row['points'][binding['point']]


def location(scene,resources,reference):
    if 'map_location' not in scene:return reference['map_ui'],reference['map_label'],0
    row,point=resolve(scene['map_location'],resources.get('authored_maps',{}))
    return row['file'],point['label'],(8 if point.get('visible',False) else 0)|(16 if point.get('haven',False) else 0)
