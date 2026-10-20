"""Original informational maps discovered through NSC references and NUI data.

Only generated controls reference the game's tiles; original assets are never
copied into authored projects or distribution packages.
"""
import io,re
from pathlib import PurePosixPath
from .project_resources import original_entry,original_bytes


def read(ws,resources,name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\.nui',name,re.I):raise ValueError('Original map requires a NUI filename')
    entry=original_entry(resources,'.nui',name)
    if entry.get('imported_pack'):raise ValueError('Choose a map from the original game')
    raw=original_bytes(ws,entry)
    if len(raw)>65536:raise ValueError('Original map NUI exceeds 64 KiB')
    text=raw.decode('cp1252');quads=[];points=[]
    for line in text.splitlines():
        line=line.split(';',1)[0].strip()
        quad=re.fullmatch(r'quad mat=([\w]+\.tga) pos=(\d+),(\d+) size=(\d+),(\d+)',line,re.I)
        if quad:
            mat=quad[1];x,y,w,h=map(int,quad.groups()[1:])
            if w<1 or h<1 or x+w>640 or y+h>480:raise ValueError('Invalid original map tile bounds')
            tile=original_entry(resources,'.tga',mat)
            if tile.get('imported_pack'):raise ValueError('Original map tiles must belong to the game')
            quads.append(dict(material=mat,position=[x,y],size=[w,h]));continue
        point=re.fullmatch(r'element imagearray name=(\w+) size=16,16 flags=0x08 pos=(\d+),(\d+)',line)
        if point:
            x,y=int(point[2]),int(point[3])
            if x>624 or y>464:raise ValueError('Invalid original map marker bounds')
            points.append(dict(label=point[1],position=[x,y]))
    if len(quads)!=12 or sum(q['size'][0]*q['size'][1] for q in quads)!=640*480 or not points or len(points)>128 or 'name=mapLocations' not in text or 'name=MapCloseButton' not in text:raise ValueError('Unsupported original informational map')
    return dict(file=PurePosixPath(entry['path']).name,quads=quads,points=points)


def catalogue(backend):
    names=sorted({r['map_ui'] for level in backend.levels.values() for r in level.get('references',[]) if r['map_ui'].casefold()!='foobar.nui'})
    result={}
    for name in names:
        if not backend.ws.game:
            entry=original_entry(backend.original_resources,'.nui',name)
            if not backend.ws.output('research/original/'+entry['archive']+'/'+entry['path']).is_file():continue
        row=read(backend.ws,backend.original_resources,name)
        if not backend.ws.game:
            tiles=[original_entry(backend.original_resources,'.tga',q['material']) for q in row['quads']]
            if any(not backend.ws.output('research/original/'+e['archive']+'/'+e['path']).is_file() for e in tiles):continue
        row['name']=re.sub(r'([a-z])([A-Z])',r'\1 \2',PurePosixPath(name).stem.removeprefix('map'))
        for point in row['points']:point['name']=backend.strings.get(point['label'],point['label'])
        result[row['file']]=row
    return result


def associated(level,available):
    for ref in level.get('references',[]):
        for name,row in available.items():
            if name.casefold()==ref['map_ui'].casefold():
                point=next((p for p in row['points'] if p['label']==ref['map_label']),None)
                if point:return row,point
    return None,None


def image_bytes(ws,resources,row):
    from PIL import Image
    image=Image.new('RGB',(640,480))
    for quad in row['quads']:
        data=original_bytes(ws,original_entry(resources,'.tga',quad['material']))
        with Image.open(io.BytesIO(data)) as tile:
            if list(tile.size)!=quad['size']:raise ValueError('Original map tile dimensions differ from NUI')
            x,y=quad['position'];image.paste(tile.convert('RGB'),(x,480-y-tile.height))
    out=io.BytesIO();image.save(out,format='PNG');return out.getvalue()
