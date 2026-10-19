"""Small owned runtime lights and weather; never baked lightmaps or NIL edits."""
import json
from .generator import java_vector as jv,java_string as js

STYLES=('constant','torch1','torch2','torch3','pulse1','pulse2','pulse3','fluoro1','fluoro2','fluoro3')


def room_types(scene):
    values=[]
    def visit(node):
        if isinstance(node,list):
            for child in node:visit(child)
        elif isinstance(node,dict):
            if set(node)=={'set_room_type'}:values.append(node['set_room_type'])
            else:
                for key,child in node.items():
                    if not key.startswith('_'):visit(child)
    visit(scene)
    value=scene.get('level',{}).get('environment',{}).get('room_type')
    if value is not None:values.append(value)
    return sorted(set(values))


def extend_room_type(java,scene):
    values=room_types(scene)
    if not values:return java
    initial=scene.get('level',{}).get('environment',{}).get('room_type');index=values.index(initial) if initial is not None else -1
    code=[f' private int roomTypeState={index}; private boolean roomTypePending=true;',
          ' private boolean sceneRoomType(int index) { boolean ok=false; switch(index) {']
    for i,value in enumerate(values):code.append(f' case {i}: ok=CodexConsole.Execute("roomtype {value}"); break;')
    code+=[' } if(!ok) { trace("ROOM_TYPE_COMMAND_FAILED"); return false; } roomTypeState=index; roomTypePending=false; trace("ROOM_TYPE_APPLIED "+index); return true; }']
    java=java.replace('ticks++;','if(roomTypePending && player!=0) { roomTypePending=false; if(roomTypeState>=0) sceneRoomType(roomTypeState); } ticks++;',1)
    java=java.replace('public void beginscene(int who,int capture) {','public void beginscene(int who,int capture) { roomTypePending=true;',1)
    java=java.replace('public void save(int capture) {','public void save(int capture) { CodexSequence.SaveInt(roomTypeState);',1)
    java=java.replace('public void restore(int capture) {',f'public void restore(int capture) {{ roomTypeState=CodexSequence.RestoreInt(); if(roomTypeState< -1 || roomTypeState>={len(values)}) roomTypeState=-1; roomTypePending=true;',1)
    return java[:-2]+'\n'+'\n'.join(code)+'\n}\n'


def configurations(scene):
    lights=[];weather=[]
    def visit(node):
        if isinstance(node,list):
            for item in node:visit(item)
        elif isinstance(node,dict):
            if len(node)==1 and next(iter(node)) in {'set_dynamic_light','clear_dynamic_light'}:
                if node not in lights:lights.append(node)
            elif set(node)=={'set_weather'}:
                if node['set_weather'] not in weather:weather.append(node['set_weather'])
            else:
                for value in node.values():visit(value)
    visit({k:v for k,v in scene.items() if not k.startswith('_')})
    from .scene_zones import lights as zone_lights
    for _,light in zone_lights(scene):
        for action in ({'set_dynamic_light':light},{'clear_dynamic_light':light['entity']}):
            if action not in lights:lights.append(action)
    return sorted(lights,key=lambda value:json.dumps(value,sort_keys=True)),sorted(weather)


def extend(java,scene,project):
    java=extend_room_type(java,scene)
    lights,weather=configurations(scene)
    if not lights and not weather:return java
    from .dynamic_targets import indices as target_indices
    indices=target_indices(scene,project)
    targets=list(dict.fromkeys(a.get('set_dynamic_light',{}).get('entity') if 'set_dynamic_light' in a else a['clear_dynamic_light'] for a in lights))
    code=[]
    if lights:
        count=len(targets)
        code += [f' private int[] sceneLightState=new int[]{{{",".join("-1" for _ in targets)}}}, sceneLightGuid=new int[{count}];',
                 ' private boolean sceneLight(int command) { int slot=-1,guid=0; switch(command) {']
        for ci,action in enumerate(lights):
            kind,value=next(iter(action.items()));entity=value['entity'] if kind=='set_dynamic_light' else value
            code.append(f' case {ci}: slot={targets.index(entity)}; guid=things[{indices[entity]}]; break;')
        code += [' } if(slot<0 || !local(guid)) { trace("LIGHT_TARGET_MISSING"); return false; } CodexThing thing=new CodexThing(guid); thing.ClearDynamicLight(); boolean ok=true; switch(command) {']
        if any(str(target).startswith('dynamic/') for target in targets):code[-1]=code[-1].replace('CodexThing thing=', 'if(sceneLightGuid[slot]!=guid && local(sceneLightGuid[slot])) new CodexThing(sceneLightGuid[slot]).ClearDynamicLight(); CodexThing thing=')
        for ci,action in enumerate(lights):
            if 'set_dynamic_light' not in action:continue
            value=action['set_dynamic_light']
            code.append(f' case {ci}: ok=thing.AllocateDynamicLight() && thing.SetDynamicLightColor({jv(value["color"])}) && thing.SetDynamicLightIntensity({float(value["intensity"])}f) && thing.SetDynamicLightRadius({float(value["radius"])}f) && thing.SetDynamicLightStyle(LIGHTSTYLE_{value.get("style","constant").upper()}); break;')
        code += [' } sceneLightGuid[slot]=guid; if(!ok) { thing.ClearDynamicLight(); trace("LIGHT_FAILED"); return false; } sceneLightState[slot]=command; trace("LIGHT_APPLIED "+command); return true; }',
                 ' private void pollSceneLights() {']
        for i,target in enumerate(targets):
            if str(target).startswith('dynamic/'):
                code.append(f' if(!local(things[{indices[target]}]) && sceneLightGuid[{i}]!=0) {{ if(local(sceneLightGuid[{i}])) new CodexThing(sceneLightGuid[{i}]).ClearDynamicLight(); sceneLightGuid[{i}]=0; }}')
            code.append(f' if(sceneLightState[{i}]>=0 && local(things[{indices[target]}]) && sceneLightGuid[{i}]!=things[{indices[target]}]) sceneLight(sceneLightState[{i}]);')
        code.append(' }')
        from .scene_zones import lights as zone_lights
        zones=zone_lights(scene)
        if zones:
            code += [f' private int[] lightZoneState=new int[{len(zones)}]; private void pollLightZones() {{ if(player==0) return;']
            for zi,(ti,light) in enumerate(zones):
                on=lights.index({'set_dynamic_light':light});off=lights.index({'clear_dynamic_light':light['entity']});slot=targets.index(light['entity'])
                code.append(f' if(local(things[{indices[light["entity"]]}])) {{ int desired=volume({ti})?1:2; if(lightZoneState[{zi}]!=desired || sceneLightState[{slot}]!=(desired==1?{on}:{off})) {{ if(sceneLight(desired==1?{on}:{off})) lightZoneState[{zi}]=desired; }} }}')
            code.append(' }');java=java.replace('ticks++;','pollLightZones(); ticks++;',1)
        java=java.replace('ticks++;','pollSceneLights(); ticks++;',1)
        java=java.replace('public void save(int capture) {','public void save(int capture) { for(int i=0;i<sceneLightState.length;i++) CodexSequence.SaveInt(sceneLightState[i]);',1)
        java=java.replace('public void restore(int capture) {','public void restore(int capture) { for(int i=0;i<sceneLightState.length;i++) { sceneLightState[i]=CodexSequence.RestoreInt(); if(sceneLightState[i]<-1 || sceneLightState[i]>='+str(len(lights))+') sceneLightState[i]=-1; sceneLightGuid[i]=0; }',1)
    if weather:
        code += [' private int sceneWeather=-1; private boolean sceneWeatherRestore=false;',
                 ' private void applySceneWeather(int index) { switch(index) {']
        for i,name in enumerate(weather):code.append(f' case {i}: SetWeatherEffect({js(name)}); sceneWeather=index; break;')
        code.append(' } }')
        java=java.replace('ticks++;','if(sceneWeatherRestore) { sceneWeatherRestore=false; applySceneWeather(sceneWeather); } ticks++;',1)
        java=java.replace('public void save(int capture) {','public void save(int capture) { CodexSequence.SaveInt(sceneWeather);',1)
        java=java.replace('public void restore(int capture) {','public void restore(int capture) { sceneWeather=CodexSequence.RestoreInt(); sceneWeatherRestore=true;',1)
    return java[:-2]+'\n'+'\n'.join(code)+'\n}\n'
