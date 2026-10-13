"""Small safe authoring conveniences, using the existing history and references."""
import copy
from .model import identifier


KINDS={'actors','objects','triggers','entries','waypoints','conversations','events','quests','encounters','sequences','paths','scenes','generators'}


def duplicate_entity(source,path):
    if len(path)<2 or path[-2] not in KINDS or type(path[-1]) is not int:raise ValueError('Selecciona un elemento para duplicarlo')
    candidate=copy.deepcopy(source);rows=candidate
    for key in path[:-1]:rows=rows[key]
    if not isinstance(rows,list):raise ValueError('La selección no es una entidad')
    kind=path[-2];row=copy.deepcopy(rows[path[-1]])
    stem=row['id'][:12];index=2;ident=stem+'_'+str(index)
    while any(r['id']==ident for r in rows):index+=1;ident=stem[:15-len(str(index))]+'_'+str(index)
    identifier(ident,'ID',16)
    if kind=='generators':rewire_generator(row,row['id'],ident)
    row['id']=ident
    if 'name' in row:row['name']+=' (copy)'
    if kind=='actors':row.pop('conversation',None);row.pop('inventory',None)
    if kind in {'actors','objects','triggers','entries','waypoints'} and 'position' in row.get('transform',{}):row['transform']['position'][0]+=40
    rows.append(row);selected=(*path[:-1],len(rows)-1)
    if kind in {'actors','objects'}:
        scene=candidate
        for key in path[:-2]:scene=scene[key]
        events=scene['events'];stem='copy_spawn';i=1
        while any(e.get('id')==stem+str(i) for e in events):i+=1
        events.append(dict(id=stem+str(i),when='scene_start',actions=[{'spawn':ident}]))
    return candidate,selected


def rewire_generator(row, old, new):
    """Only self references belong to a clone; external activation stays explicit."""
    keys={'generator','start_generator','stop_generator','pause_generator','resume_generator','reset_generator'}
    def visit(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in keys and item==old:value[key]=new
                else:visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    visit(row)
