"""Views of the existing encounter GUID slots, never spawned/saved actors."""


def candidates(scene):
    result={}
    for gi,generator in enumerate(scene.get('generators',[])):
        roles=list(dict.fromkeys(group['role'] for wave in generator['waves'] for group in wave['groups']))
        for ri,role in enumerate(roles):
            templates=list(dict.fromkeys(group['template'] for wave in generator['waves'] for group in wave['groups'] if group['role']==role))
            for ordinal in range(generator['max_alive']):
                key=f'dynamic/{generator["id"]}/{role}/{ordinal}'
                result[key]=dict(id=key,name=generator['name']+' / '+role+' #'+str(ordinal+1),template=templates[0],templates=templates,generator=gi,role=ri,ordinal=ordinal)
    return result


def used(scene):
    available=candidates(scene);found=set()
    def visit(value):
        if isinstance(value,str) and value in available:found.add(value)
        elif isinstance(value,list):
            for child in value:visit(child)
        elif isinstance(value,dict):
            for key,child in value.items():
                if not key.startswith('_'):visit(child)
    visit(scene)
    return {key:available[key] for key in sorted(found)}


def indices(scene,project):
    result={entity.id:i for i,entity in enumerate(project.entities)}
    result.update({key:len(result)+i for i,key in enumerate(used(scene))})
    return result


def choices(scene):return [(row['name'],key) for key,row in candidates(scene).items()]


def rename(scene,old,new):
    fields={'actor','reference','target','stop_actor','stop_patrol','enable_ai','disable_ai','entity','actor_alive','entity_exists','clear_dynamic_light'}
    def visit(value):
        if isinstance(value,list):
            for child in value:visit(child)
        elif isinstance(value,dict):
            for key,child in list(value.items()):
                if key in fields and isinstance(child,str) and child.startswith('dynamic/'+old+'/'):value[key]='dynamic/'+new+'/'+child.split('/',2)[2]
                elif isinstance(child,(dict,list)):visit(child)
    visit(scene)


def extend(java,scene,project):
    targets=used(scene)
    if not targets:return java
    base=len(project.entities)
    # Alias mirrors are transient reads of dGuid. All old entity loops and save
    # records retain their original length; aliases are never captured/created.
    java=java.replace(f'private int[] things=new int[{base}];',f'private int[] things=new int[{base+len(targets)}];')
    java=java.replace('i<things.length',f'i<{base}')
    lines=[' private int dynamicTarget(int g,int role,int ordinal) { if(!dConfigured || dRestoring || g<0 || g>=dGuid.length || dUnsafe[g]) return 0; for(int s=0;s<dGuid[g].length;s++) { int guid=dGuid[g][s],entry=dSlotEntry[g][s]; if(entry<0 || entry>=dRole[g].length || dRole[g][entry]!=role || !dynamicOwned(g,s) || !local(guid) || !IsActorGuid(guid) || new CodexActor(guid).GetActorHealth()<=0.0f) continue; if(ordinal--==0) return guid; } return 0; }',
           ' private void refreshDynamicTargets() {']
    for i,(_,row) in enumerate(targets.items()):lines.append(f' things[{base+i}]=dynamicTarget({row["generator"]},{row["role"]},{row["ordinal"]});')
    camera_aliases={str(base+i) for i in range(len(targets))}
    if 'CodexCamera.SetupCutscene(' in java:
        import re
        def pin(match):
            arguments=match[1].split(',')
            if len(arguments)!=3:return match[0]
            slots=[]
            for argument in arguments[1:]:
                m=re.fullmatch(r'things\[(\d+)\]',argument.strip());slots.append(int(m[1]) if m and m[1] in camera_aliases else -1)
            return match[0]+f' pinDynamicCamera({slots[0]},{slots[1]});'
        java=re.sub(r'CodexCamera.SetupCutscene\(([^;]+)\);',pin,java)
        lines.append(' if((dynamicCameraA>=0 && things[dynamicCameraA]!=dynamicCameraGuidA)||(dynamicCameraB>=0 && things[dynamicCameraB]!=dynamicCameraGuidB)) { trace("CINEMA_DYNAMIC_TARGET_CHANGED"); releaseCamera(); } }')
        lines+=[' private int dynamicCameraA=-1,dynamicCameraB=-1,dynamicCameraGuidA=0,dynamicCameraGuidB=0;',
                ' private void pinDynamicCamera(int a,int b) { dynamicCameraA=a; dynamicCameraB=b; dynamicCameraGuidA=a<0?0:things[a]; dynamicCameraGuidB=b<0?0:things[b]; }']
        java=java.replace('private void releaseCamera() {','private void releaseCamera() { pinDynamicCamera(-1,-1);',1)
    else:lines.append(' }')
    # Resolve at every action boundary, not only at the next timer tick. A spawn
    # callback/phase may fire inside dynamicPoll or during a synchronous event.
    import re
    java=re.sub(r'(private boolean event\d+\(\) \{)',r'\1 refreshDynamicTargets();',java)
    # Resolve before audio/light/camera poll hooks as well as event boundaries.
    java=java.replace('private void pollImpl() {','private void pollImpl() { refreshDynamicTargets();',1)
    java=java.replace('private boolean beginCinema(int index) {','private boolean beginCinema(int index) { refreshDynamicTargets();',1)
    java=java.replace('private void pollCinema() {','private void pollCinema() { refreshDynamicTargets();',1)
    return java[:-2]+'\n'+'\n'.join(lines)+'\n}\n'
