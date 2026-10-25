"""Native selectable brush props layered over scenery; never proximity triggers.

NSD v8 reader 0x4a8560 and brush reader 0x4c3e50, plus ClickExit.clicked,
are the format/API evidence. Only our unframed, unlit brush subset
is written. NIL is never changed.
"""
import math
import struct
from .model import mapping,sequence
from .formats import fixed


def validate_placement(ws,level,objects):
    """Never write an out-of-range native sector pointer from editable YAML."""
    if not objects:return
    import zipfile
    entry=level['geometry'][0]
    if entry.get('imported_pack'):
        from .wtd import read_entry
        data=read_entry(ws,entry)
    else:
        if not ws.game:raise ValueError('Selecciona una instalación para verificar el sector de la superficie pulsable.')
        with zipfile.ZipFile(ws.game/entry['archive']) as archive:
            with archive.open(entry['path']) as stream:
                data=stream.read(96)
                if len(data)!=96 or data[:8]!=b'NIL\x10\x1b\0\0\0':raise ValueError('Invalid interaction base level header')
                materials=struct.unpack_from('<I',data,92)[0]
                if materials>10000:raise ValueError('Invalid interaction base level materials')
                data+=stream.read(materials*32+4)
    if len(data)<96 or data[:8]!=b'NIL\x10\x1b\0\0\0':raise ValueError('Invalid interaction base level header')
    materials=struct.unpack_from('<I',data,92)[0];offset=96+materials*32
    if materials>10000 or offset+4>len(data):raise ValueError('Invalid interaction base level sectors')
    sectors=struct.unpack_from('<I',data,offset)[0]
    for obj in objects:
        if not 0<=obj['interaction']['sector']<sectors:raise ValueError('Sector de superficie pulsable fuera del level: '+obj['id'])


def validate(value):
    mapping(value,{'materials','vertices','material_ids','sector','source'},{'materials','vertices','material_ids','sector'},'interaction')
    if 'source' in value:
        mapping(value['source'],{'level','template','position','cast_id'},{'level','template'},'interaction.source')
    names=sequence(value['materials'],'interaction.materials')
    if not 1<=len(names)<=64:raise ValueError('Interaction: 1..64 materials')
    for name in names:
        if not isinstance(name,str) or not name or any(c in name for c in '\n\r\0'):raise ValueError('Invalid interaction material')
        fixed(name)
    points=sequence(value['vertices'],'interaction.vertices');ids=sequence(value['material_ids'],'interaction.material_ids')
    if not 1<=len(ids)<=2048 or len(points)!=len(ids)*3:raise ValueError('Interaction: 1..2048 triangles')
    for point in points:
        if not isinstance(point,list) or len(point)!=5 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e7 for v in point):raise ValueError('Invalid interaction vertex')
    if any(type(i) is not int or not 0<=i<len(names) for i in ids):raise ValueError('Invalid interaction material index')
    if type(value['sector']) is not int or not 0<=value['sector']<100000:raise ValueError('Invalid interaction sector')
    # Degenerate faces cannot be selected and can break native plane maths.
    for i in range(len(ids)):
        a,b,c=[points[i*3+j][:3] for j in range(3)];u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        if sum((u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3])**2 for j in range(3))<1e-10:raise ValueError('Degenerate interaction triangle')
    return value


def box_planes(bounds):
    """Native n.dot(point)<=distance planes; give flat faces finite depth."""
    result=[]
    for axis in range(3):
        low,high=float(bounds[axis]),float(bounds[axis+3])
        if high-low<1:low-=.5;high+=.5
        for sign,distance in [(-1,-low),(1,high)]:
            normal=[0.,0.,0.];normal[axis]=sign;result.append((*normal,distance))
    return struct.pack('<I',6)+b''.join(struct.pack('<4f',*plane) for plane in result)


def brush(value):
    """40-byte vertices, uint16 indices, 28-byte groups, bounds, six planes."""
    validate(value);vertices=[];indices=[];groups=[]
    for material in range(len(value['materials'])):
        rows=[i for i,m in enumerate(value['material_ids']) if m==material]
        if not rows:continue
        start=len(vertices)
        for i in rows:
            a,b,c=[value['vertices'][i*3+j] for j in range(3)]
            u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
            n=[u[(j+1)%3]*v[(j+2)%3]-u[(j+2)%3]*v[(j+1)%3] for j in range(3)];length=math.sqrt(sum(x*x for x in n));n=[x/length for x in n]
            first=len(vertices)-start
            vertices.extend(struct.pack('<10f',*p[:3],*n,*p[3:],1,0) for p in (a,b,c));indices.append(struct.pack('<3H',first,first+1,first+2))
        # Fields +4/+8 are native scratch pointers, zero on disk. +12 is flags.
        groups.append(struct.pack('<iIIIHHII',material,0,0,0,len(rows),len(rows)*3,len(rows)*3|(4<<16),0))
    xyz=[p[:3] for p in value['vertices']];bounds=list(struct.unpack('<6f',struct.pack('<6f',*[min(p[j] for p in xyz) for j in range(3)],*[max(p[j] for p in xyz) for j in range(3)])))
    return (struct.pack('<I',len(value['materials']))+b''.join(fixed(n) for n in value['materials'])+
            struct.pack('<IIHI',len(vertices),len(indices),len(groups),6)+b''.join(vertices+indices+groups)+struct.pack('<6f',*bounds)+box_planes(bounds))


def surface(mesh,index,normal):
    """Connected material patch only: the other door/wall is not selected."""
    import numpy as np
    material=int(mesh.material_ids[index]);triangles=mesh.triangles
    candidates=np.flatnonzero(mesh.material_ids==material);adjacency={}
    for i in candidates:
        for vertex in triangles[i]:adjacency.setdefault(tuple(np.round(vertex,2)),[]).append(int(i))
    selected=set();pending=[index]
    while pending:
        i=pending.pop()
        if i in selected:continue
        selected.add(i)
        if len(selected)>2048:raise ValueError('La superficie es demasiado grande; elige un objeto o una superficie más pequeña.')
        for vertex in triangles[i]:pending.extend(j for j in adjacency[tuple(np.round(vertex,2))] if j not in selected)
    indices=[i for i in sorted(selected) if np.linalg.norm(np.cross(triangles[i,1]-triangles[i,0],triangles[i,2]-triangles[i,0]))>1e-5]
    if not indices:raise ValueError('La superficie no contiene triángulos seleccionables.')
    points=mesh.vertices.reshape(-1,3,5)[indices].copy().reshape(-1,5)
    # Put the native selectable face just ahead of the immutable original.
    points[:,:3]+=np.asarray(normal)*.75;center=points[:,:3].mean(0);points[:,:3]-=center
    sectors=getattr(mesh,'triangle_sectors',None)
    if sectors is None:raise ValueError('Recarga el escenario para identificar el sector de esta superficie.')
    value=dict(materials=[mesh.materials[material]],vertices=points.tolist(),material_ids=[0]*len(indices),sector=int(sectors[index]))
    validate(value);return center.tolist(),value


def target_mesh(backend,target):
    """Recover a pointed static prop's actual mesh, not a guessed radius."""
    import numpy as np
    from .original_objects import catalogue,selector
    from .spatial.assets import Assets
    from .spatial.scene_mesh import read_brush
    row=next((r for r in catalogue(backend,target['level']) if selector(r)==selector(target)),None)
    if row is None:raise ValueError('No se encuentra el objeto original seleccionado.')
    assets=Assets(backend)
    if 'mesh_offset' in row:
        source=backend.hints[row['origin'].casefold()]['source'];mesh=read_brush(assets.read(source['path'],source['archive']),row['mesh_offset'])
    elif row.get('model'):mesh=assets.model(row['model'])[0]
    else:raise ValueError('Este objeto no tiene una superficie seleccionable. Elige una superficie visible en 3D.')
    # Per-face offset keeps the overlay selectable from either side and avoids
    # coincident depth. The original object's own script remains untouched.
    points=mesh.vertices.copy().reshape(-1,3,5);tri=points[:,:,:3];normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);valid=length>1e-5
    points=points[valid];normals=normals[valid]/length[valid,None];points[:,:,:3]+=normals[:,None,:]*.75
    value=dict(materials=mesh.materials,vertices=points.reshape(-1,5).tolist(),material_ids=mesh.material_ids[valid].tolist(),sector=row['sector'],source=selector(row))
    validate(value);return row['position'],row['orientation'],value


def extend(java,scene,project):
    objects={o['id']:o for o in scene.get('objects',[]) if 'interaction' in o or 'geometry' in o}
    if not objects:return java
    def interactive(o):return 'interaction' in o or o.get('geometry',{}).get('mode')=='interactive'
    clicks=[i for i,e in enumerate(project.entities) if e.id in objects and interactive(objects[e.id])]
    decor=[i for i,e in enumerate(project.entities) if e.id in objects and not interactive(objects[e.id])]
    indices=clicks+decor
    # These objects are instantiated by NSD with an actual native brush. Do not
    # fall back to CreateThing: it would silently create an unselectable ghost.
    for i in indices:
        e=project.entities[i]
        from .generator import java_vector as jv
        call=f'createAt({i},{jv(e.transform.position)},{jv(e.transform.orientation)})'
        if java.count(call)!=1:raise ValueError('Ambiguous clickable brush factory integration')
        java=java.replace(call,'0')
    marker='private void pollImpl() {'
    java=java.replace('{','{\n private int[] clickCaptured=new int['+str(len(project.entities))+'];',1)
    # A single binding per GUID; duplicate captures can duplicate native clicks.
    choices=' || '.join('i=='+str(i) for i in indices)
    java=java.replace('things[i]=CodexThing.GuidFromCastID(template(i));',f'things[i]=({choices})?findClick(i):CodexThing.GuidFromCastID(template(i));',1)
    click_choices=' || '.join('i=='+str(i) for i in clicks) or 'false'
    decor_choices=' || '.join('i=='+str(i) for i in decor) or 'false'
    java=java.replace('CaptureThing(things[i],i+1);',f'if({click_choices}) bindClick(i); else if({decor_choices}) bindDecor(i); else CaptureThing(things[i],i+1);',1)
    helper=''' private boolean clickMatches(int i,int guid) {
 if(!IsPropGuid(guid) || !local(guid) || guid==GetGUID()) return false;
 CodexThing item=new CodexThing(guid);
 return template(i).equalsIgnoreCase(item.GetDescriptionID());
 }
 private int findClick(int i) {
 int guid=CodexThing.GuidFromCastID(template(i)); if(clickMatches(i,guid)) return guid;
 int found=0,steps=0; guid=new CodexWorld(WORLD_CURRENT).GetFirstThing();
 while(guid!=0 && steps++<10000) {
 if(clickMatches(i,guid)) { if(found!=0) { trace("CLICK_AMBIGUOUS "+template(i)); return 0; } found=guid; }
 int next=new CodexThing(guid).NextInWorld(); if(next==guid) return 0; guid=next;
 }
 return guid==0?found:0;
 }
 private void bindDecor(int i) {
 if(!local(things[i])) return;
 CodexThing piece=new CodexThing(things[i]);
 piece.ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND);
 piece.SetThingFlags(THING_FLAG_SAVEALWAYS|THING_FLAG_NOSTDELETE);
 }
'''
    helper+=''' private void bindClick(int i) {
 if(!local(things[i]) || clickCaptured[i]==things[i]) return;
 CodexThing clickable=new CodexThing(things[i]);
 clickable.ClearThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_BLOCKSELECT|THING_FLAG_PROXIMITYTRIGGER|THING_FLAG_VISBLOCK|THING_FLAG_CAMERABLOCK|THING_FLAG_DISABLECOLLIDE|THING_FLAG_NOBLOCK);
 clickable.SetThingFlags(THING_FLAG_NOSTDELETE);
 if(CaptureThing(things[i],i+1)) { clickCaptured[i]=things[i]; trace("CLICK_BOUND "+template(i)+" guid="+things[i]); }
 else if(ticks%20==0) trace("CLICK_CAPTURE_FAILED "+template(i)+" guid="+things[i]);
 }
'''
    from .original_objects import targets,key
    originals=list(targets(scene));follow=[]
    for i in clicks:
        obj=objects[project.entities[i].id]
        if 'source' not in obj.get('interaction',{}):continue
        index=originals.index(key(obj['interaction']['source']))
        follow.append(f''' if(local(things[{i}])) {{
 int base=clickSources[{i}]; if(!originalMatches({index},base) && (base!=0 || ticks%10==0)) base=clickSources[{i}]=originalFind({index});
 CodexThing overlay=new CodexThing(things[{i}]);
 if(base<=0 || (new CodexThing(base).GetRenderFlags()&THING_RENDERFLAG_DONTRENDER)!=0) {{ overlay.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.SetThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }}
 else {{ CodexThing source=new CodexThing(base); overlay.SetPosition(source.GetPosition()); overlay.SetOrientation(source.GetOrientation()); overlay.ClearRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.ClearThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }}
 }}''')
    if follow:helper+=f' private int[] clickSources=new int[{len(project.entities)}];\n'
    setup=' '.join(f'if(!createdOnce[{i}]) spawn({i}); bindClick({i});' for i in clicks)
    setup+=' '.join(f'if(!createdOnce[{i}]) spawn({i}); bindDecor({i});' for i in decor)+' '.join(follow)
    if 'private void pollImpl() { originalReapply();' in java:marker='private void pollImpl() { originalReapply();'
    java=java.replace(marker,marker+' '+setup,1)
    java=java.replace('public void restored(int capture) {','public void restored(int capture) { for(int i=0;i<clickCaptured.length;i++) clickCaptured[i]=0;',1)
    java=java.replace('public void clicked(int target,int clicker,int capture) {','public void clicked(int target,int clicker,int capture) { trace("CLICK_RECEIVED target="+target+" player="+clicker+" capture="+capture);',1)
    end=java.rfind('}');java=java[:end]+helper+java[end:]
    return java


def guard_events(java,scene):
    """Synchronous native callbacks and nested event calls cannot recurse."""
    from .generator import java_string as js
    if not any('interaction' in o or 'geometry' in o for o in scene.get('objects',[])) and not any('run_event' in a for e in scene['events'] for a in e['actions']):return java
    java=java.replace('{','{\n private boolean[] eventRunning=new boolean['+str(len(scene['events']))+'];',1)
    for i,event in enumerate(scene['events']):
        start=f'private boolean event{i}() {{'
        finish=f'trace({js("event "+scene["id"]+"/"+event["id"])}); return true; }}'
        if java.count(start)!=1 or java.count(finish)!=1:raise ValueError('Ambiguous click event guard integration')
        java=java.replace(start,start+f' if(eventRunning[{i}]) return false; eventRunning[{i}]=true; try {{',1)
        java=java.replace(finish,finish[:-1]+f'}} finally {{ eventRunning[{i}]=false; }} }}',1)
    return java
