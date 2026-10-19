"""Native box regions use existing trigger transforms and original scripts."""
import math
from .formats import Tag


def active(scene):return [r for r in scene.get('triggers',[]) if r.get('native_script') or r.get('native_region') is True]


def validate(scene):
    for row in scene.get('triggers',[]):
        if 'native_region' in row and type(row['native_region']) is not bool:raise ValueError('Native region requires boolean')
    rows=active(scene)
    if len(rows)>8:raise ValueError('Maximum 8 native scripted regions per scene')
    for row in rows:
        if row['shape']!='box':raise ValueError('Native script region requires a box')
        if any(abs(v)>.001 for v in row['transform']['orientation'][:2]):raise ValueError('Native region supports yaw rotation only')
        if row.get('native_script') and any(e.get('trigger')==row['id'] for e in scene['events']):raise ValueError('Native region owns its callbacks: remove ordinary trigger events or remove the native script')
        if row.get('native_frames'):raise ValueError('Native region cannot have movement frames')


def box(size):
    from .click_interactions import brush
    x,y,z=[v/2 for v in size]
    points=[[-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],[-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]]
    triangles=((0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7))
    # Material and local-coordinate box semantics occur in the original region corpus.
    return brush(dict(materials=['Prague\\TCarches1_2_p'],vertices=[points[i]+[0,0] for tri in triangles for i in tri],material_ids=[0]*12,sector=0))


def sector_links(sectors,region):
    position=region['transform']['position'];angle=math.radians(region['transform']['orientation'][2]);co,si=math.cos(angle),math.sin(angle);half=[v/2 for v in region['size']]
    links=[]
    for i,planes in enumerate(sectors):
        if not planes:continue
        if all(sum(n*p for n,p in zip(plane[:3],position))+abs(plane[0]*co+plane[1]*si)*half[0]+abs(-plane[0]*si+plane[1]*co)*half[1]+abs(plane[2])*half[2]>=plane[3]-.01 for plane in planes):links.append(i)
    if not links:raise ValueError('Native region does not intersect a known level sector')
    return links


def append(model,scene,project,sectors,index):
    for i,row in enumerate(active(scene)):
        number=len(model.entities);name=project.prefix+'_t'+str(i);index[row['id']]=number;links=sector_links(sectors,row)
        model.entities.append([Tag.text(0,'trigger_region'),Tag.text(81,name),Tag.vector(1,row['transform']['orientation']),Tag.vector(2,row['transform']['position']),Tag.integer(3,links[0])])
        if model.brushes is None:model.brushes={}
        if model.regions is None:model.regions={}
        model.brushes[number]=box(row['size']);model.regions[number]=links
