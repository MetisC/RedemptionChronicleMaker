"""Stock constructor metadata from actual Java classfiles, never source regex."""
import re
import struct
from .classfile_limits import inspect_class

TYPES={'I':('integer',1),'F':('float',2),'Ljava/lang/String;':('string',7),'LCodexThing;':('thing',3),'LCodexActor;':('actor',8),'LCodexRegion;':('region',5),'LCodexItem;':('item',10)}
_catalogues={}


def declared(row):
    from .model import mapping
    values=row.get('parameters',[])
    if not isinstance(values,list) or len(values)>16:raise ValueError('Custom script: maximum 16 typed parameters')
    by_type={value[0]:(key,value[1]) for key,value in TYPES.items()};parameters=[];descriptor='('
    for value in values:
        mapping(value,{'type','label'},{'type','label'},'Custom parameter')
        if value['type'] not in by_type:raise ValueError('Custom script: unsupported parameter type')
        label=value['label']
        if not isinstance(label,str) or not label.strip() or len(label)>120 or any(c in label for c in '\0\r\n'):raise ValueError('Custom parameter: one nonempty label required')
        token,native=by_type[value['type']];descriptor+=token;parameters.append(dict(type=value['type'],native_type=native,label=label))
    return dict(descriptor=descriptor+')V',parameters=parameters,literal_metadata=False)


def available(ws,resources,source):
    result=dict(catalogue(ws,resources))
    for row in source.get('resources',{}).get('scripts',[]):result[row['id']]=declared(row)
    return result


def literal_labels(record):
    """Recognise ONLY the literal String[] initializer used by stock _params.

    This is a pattern decoder, not a Java interpreter. Any extra instruction,
    computed value or foreign field leaves the metadata unavailable.
    """
    code=next((bytes.fromhex(m['bytecode']) for m in record['methods'] if m['name']=='<clinit>'),b'');p=0
    def byte():
        nonlocal p
        if p>=len(code):raise ValueError('metadata truncated')
        v=code[p];p+=1;return v
    def number():
        opcode=byte()
        if 2<=opcode<=8:return opcode-3
        if opcode==16:return struct.unpack('b',bytes([byte()]))[0]
        if opcode==17:return struct.unpack('>h',bytes([byte(),byte()]))[0]
        raise ValueError('computed metadata')
    try:
        n=number()
        if not 0<=n<=16 or byte()!=0xbd:return []
        byte();byte();result=[]
        for i in range(n):
            if byte()!=0x59 or number()!=i:return []
            opcode=byte()
            index=byte() if opcode==0x12 else (byte()<<8)|byte() if opcode==0x13 else -1
            text=record['string_literals'].get(index)
            if text is None or byte()!=0x53:return []
            result.append(text)
        if byte()!=0xb3:return []
        index=(byte()<<8)|byte()
        if record['field_names'].get(index)!=('_params','[Ljava/lang/String;') or code[p:]!=b'\xb1':return []
        return result
    except ValueError:return []


def constructors(data):
    record=inspect_class(data,metadata=True);labels=literal_labels(record)
    rows=[]
    for method in record['methods']:
        if method['name']!='<init>' or not method['access_flags']&1:continue
        signature=method['descriptor']
        if not signature.startswith('(') or not signature.endswith(')V'):continue
        tokens=re.findall(r'L[^;]+;|\[.|[BCDFIJSZ]',signature[1:-2])
        if ''.join(tokens)!=signature[1:-2] or len(tokens)>16 or any(t not in TYPES for t in tokens):continue
        parameters=[]
        for i,t in enumerate(tokens):
            label=labels[i] if len(labels)==len(tokens) else 'Parameter '+str(i+1)
            title,separator,default=label.partition(';')
            parameter=dict(type=TYPES[t][0],native_type=TYPES[t][1],label=title)
            if separator and parameter['type'] not in ('actor','thing','region','item'):
                try:
                    value=int(default) if t=='I' else float(default) if t=='F' else default
                    from .script_parameters import authored
                    authored(TYPES[t][1],value,{})
                    parameter['default']=value
                except ValueError:pass
            parameters.append(parameter)
        rows.append(dict(descriptor=signature,parameters=parameters,literal_metadata=len(labels)==len(tokens)))
    return rows


def catalogue(ws,resources):
    from .project_resources import original_bytes
    key=(str(ws.root),str(ws.game),tuple((e.get('archive'),e['path'],e.get('size'),e.get('crc32')) for e in resources['entries'] if e['extension']=='.class' and not e.get('project_owned') and not e.get('imported_pack')))
    if key in _catalogues:return _catalogues[key]
    rows={};parents={}
    for entry in resources['entries']:
        if entry['extension']!='.class' or entry.get('project_owned') or entry.get('imported_pack'):continue
        name=entry['id']
        if '/' in name:continue
        data=original_bytes(ws,entry);record=inspect_class(data);parents[name]=record['superclass']
        if name.startswith('Codex'):continue
        found=constructors(data)
        if len(found)==1:rows[name]=found[0]
    def script(name,trail=()):
        if name=='Codex':return True
        return name not in trail and name in parents and script(parents[name],trail+(name,))
    result={name:value for name,value in rows.items() if script(name)}
    _catalogues.clear();_catalogues[key]=result
    return result


def placement(scene,scripts,kinds=None):
    """Validate all native targets before the generator can write entity indices."""
    from .native_regions import active as regions,validate as validate_regions
    validate_regions(scene)
    rows=scene.get('actors',[])+scene.get('objects',[])+regions(scene);index={r['id']:r for r in rows};native={r['id'] for r in regions(scene)}
    points={w['id']:w for w in scene.get('waypoints',[])}
    def actions(value):
        if isinstance(value,list):
            for child in value:yield from actions(child)
        elif isinstance(value,dict):
            if 'actions' in value:yield from value['actions']
            for key,child in value.items():
                if key!='actions':yield from actions(child)
    all_actions=list(actions(scene))
    for row in rows:
        if 'native_frames' not in row:continue
        frames=row['native_frames']
        if not isinstance(frames,list) or not 1<=len(frames)<=127 or any(not isinstance(n,str) or n not in points for n in frames):raise ValueError('Frames nativos: selecciona 1..127 puntos existentes')
        native.add(row['id'])
    for row in rows:
        value=row.get('native_script')
        if value is None:continue
        from .model import mapping
        mapping(value,{'class','parameters'},{'class','parameters'},'Script nativo')
        name=value['class']
        if name not in scripts:raise ValueError('Script sin constructor nativo demostrado: '+str(name))
        metadata=scripts[name]['parameters'];args=value['parameters']
        if not isinstance(args,list) or len(args)!=len(metadata):raise ValueError('Script nativo: número de parámetros incorrecto')
        native.add(row['id'])
        for argument,param in zip(args,metadata):
            mapping(argument,{'type','value'},{'type','value'},'Parámetro nativo')
            if argument['type']!=param['type']:raise ValueError('Script nativo: tipo distinto al constructor original')
            arg=argument['value']
            if param['type'] in ('actor','thing','region','item'):
                # Although -1 is a proven native null, stock constructors often
                # dereference it immediately. Normal authoring requires a link.
                if not isinstance(arg,str) or arg not in index:raise ValueError('Script nativo: referencia local ausente')
                if param['type']=='actor' and arg not in {a['id'] for a in scene.get('actors',[])}:raise ValueError('Script nativo requiere un actor')
                if param['type']=='region' and arg not in {r['id'] for r in regions(scene)}:raise ValueError('Native script requires a native region')
                if param['type']=='item' and arg not in {r['id'] for r in scene.get('objects',[]) if r.get('_native_item') or (kinds or {}).get(r.get('template')) in ('items','weapons','armour')}:raise ValueError('Native script requires an item template')
                native.add(arg)
            from .script_parameters import authored
            authored(param['native_type'],arg,{name:i for i,name in enumerate(index)})
        requirements={'ClassBobbing':[row['id']],'ParticleMover':[row['id']],'DoorSwitch':[row['id'],args[2]['value']] if name=='DoorSwitch' else [],'DoubleDoor':[row['id'],args[1]['value']] if name=='DoubleDoor' else []}.get(name,[])
        if any(not index[target].get('native_frames') for target in requirements):raise ValueError('Este script requiere frames nativos en el objeto y sus objetivos de movimiento')
        if name=='ClassBobbing':
            low,high,delay=[a['value'] for a in args[1:]]
            if not 0<low<=high or delay<0:raise ValueError('ClassBobbing: velocidad positiva, máximo >= mínimo y retardo >= 0')
    for name in native:
        row=index[name]
        if row.get('transform',{}).get('placement','absolute')!='absolute':raise ValueError('Script nativo requiere coordenadas de escena')
        if row.get('conversation') or row.get('inventory') or row.get('quest_item') or row.get('interaction'):raise ValueError('Script nativo: usa una entidad sin conversación, inventario ni interacción RCM')
        if any(name in a.get('inventory',[]) for a in scene.get('actors',[])):raise ValueError('Script nativo: un objeto de inventario no se coloca en la escena')
        if any(name in g.get('actors',[]) for g in scene.get('encounters',[])) or any(name==g.get('boss',{}).get('actor') for g in scene.get('generators',[])):raise ValueError('Script nativo: no puede pertenecer a un encuentro')
        if any(event.get('actor')==name or event.get('object')==name for event in scene.get('events',[])) or any(a.get('spawn')==name or a.get('give_item')==name or isinstance(a.get('actor_inventory'),dict) and a['actor_inventory'].get('item')==name for a in all_actions):raise ValueError('Script nativo: se crea al cargar; retira su acción de creación o interacción RCM')
    return native


def scene_records(ws,level,scene,project,model,metadata):
    """Place native-owned entities before any constructor references are fixed."""
    native=placement(scene,metadata)
    if not native:return
    from .formats import Tag
    from .native_arrivals import planes,sector_at
    from .script_parameters import authored
    sectors=planes(ws,level);index={}
    for entity in project.entities:
        if entity.id not in native:continue
        index[entity.id]=len(model.entities);name=project.prefix+'_'+entity.id
        model.entities.append([Tag.text(0,name),Tag.vector(1,entity.transform.orientation),Tag.vector(2,entity.transform.position),Tag.integer(3,sector_at(sectors,entity.transform.position)),Tag.text(81,name)])
    from .native_regions import append as append_regions,active as regions
    append_regions(model,scene,project,sectors,index)
    parameters={}
    frames={};points={r['id']:r for r in scene.get('waypoints',[])}
    for row in scene['actors']+scene.get('objects',[])+regions(scene):
        if row.get('native_frames'):
            transforms=[row['transform']]+[points[name]['transform'] for name in row['native_frames']]
            frames[index[row['id']]]=[struct.pack('<6f',*t['orientation'],*t['position']) for t in transforms]
        value=row.get('native_script')
        if value is None:continue
        i=index[row['id']];model.entities[i].append(Tag.text(11,value['class']))
        args=[authored(p['native_type'],v['value'],index) for p,v in zip(metadata[value['class']]['parameters'],value['parameters'])]
        if args:parameters[i]=args
    model.parameters=parameters or None
    model.frames=frames or None


def adopt_runtime(java,scene,project):
    """Native scripts retain their own callback and save/restore ownership."""
    native=set(scene.get('_native_entities',[]))
    if not native:return java
    from .generator import java_string as js
    preamble='switch(i) {'
    for i,entity in enumerate(project.entities):
        if entity.id in native:preamble+=f' case {i}: if(!createdOnce[i]) {{ things[i]=CodexThing.GuidFromCastID({js(project.prefix+"_"+entity.id)}); if(local(things[i])) createdOnce[i]=true; }} return;'
    preamble+=' } '
    old='private void spawn(int i) {'
    if java.count(old)!=1:raise ValueError('Native script adoption hook missing')
    java=java.replace(old,old+' '+preamble,1)
    # Adoption resolves handles only; it never captures/pauses the stock script.
    hook='player=localPlayer(player);'
    calls=''.join(f'spawn({i});' for i,e in enumerate(project.entities) if e.id in native)
    if java.count(hook)!=1:raise ValueError('Native script poll hook missing')
    return java.replace(hook,hook+calls,1)
