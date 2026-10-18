"""Small owned runtime lights and weather; never baked lightmaps or NIL edits."""
import json
from .generator import java_vector as jv,java_string as js

STYLES=('constant','torch1','torch2','torch3','pulse1','pulse2','pulse3','fluoro1','fluoro2','fluoro3')


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
    return sorted(lights,key=lambda value:json.dumps(value,sort_keys=True)),sorted(weather)


def extend(java,scene,project):
    lights,weather=configurations(scene)
    if not lights and not weather:return java
    indices={e.id:i for i,e in enumerate(project.entities)}
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
        for ci,action in enumerate(lights):
            if 'set_dynamic_light' not in action:continue
            value=action['set_dynamic_light']
            code.append(f' case {ci}: ok=thing.AllocateDynamicLight() && thing.SetDynamicLightColor({jv(value["color"])}) && thing.SetDynamicLightIntensity({float(value["intensity"])}f) && thing.SetDynamicLightRadius({float(value["radius"])}f) && thing.SetDynamicLightStyle(LIGHTSTYLE_{value.get("style","constant").upper()}); break;')
        code += [' } sceneLightGuid[slot]=guid; if(!ok) { thing.ClearDynamicLight(); trace("LIGHT_FAILED"); return false; } sceneLightState[slot]=command; trace("LIGHT_APPLIED "+command); return true; }',
                 ' private void pollSceneLights() {']
        for i,target in enumerate(targets):code.append(f' if(sceneLightState[{i}]>=0 && local(things[{indices[target]}]) && sceneLightGuid[{i}]!=things[{indices[target]}]) sceneLight(sceneLightState[{i}]);')
        code.append(' }')
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
