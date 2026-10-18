"""Owned native spatial loop handles; existing positioned one-shots stay intact."""
import json
from .generator import java_string as js,java_vector as jv


def loops(scene):
    found={}
    def visit(value):
        if isinstance(value,list):
            for child in value:visit(child)
        elif isinstance(value,dict):
            if set(value)=={'play_sound'} and isinstance(value['play_sound'],dict) and value['play_sound'].get('loop') is True:
                row=value['play_sound'];name=row.get('id')
                if name in found and json.dumps(found[name],sort_keys=True)!=json.dumps(row,sort_keys=True):raise ValueError('Un sonido en bucle no puede tener dos configuraciones distintas')
                found[name]=row
            else:
                for child in value.values():visit(child)
    visit({k:v for k,v in scene.items() if not k.startswith('_')})
    if len(found)>32:raise ValueError('Máximo 32 sonidos situados en bucle por escena')
    return dict(sorted(found.items(),key=lambda item:str(item[0])))


def rename_loop(scene,old,new):
    from .model import identifier
    identifier(new,'ID de sonido en bucle')
    if new!=old and new in loops(scene):raise ValueError('ID duplicado')
    def visit(value):
        if isinstance(value,list):
            for child in value:visit(child)
        elif isinstance(value,dict):
            if isinstance(value.get('play_sound'),dict) and value['play_sound'].get('loop') and value['play_sound'].get('id')==old:value['play_sound']['id']=new
            if value.get('stop_sound')==old:value['stop_sound']=new
            for child in value.values():visit(child)
    visit(scene)


def extend(java,scene,project):
    sources=loops(scene)
    if not sources:return java
    # Source definitions can occur again in lowered compiler-only events.
    code=[f' private CodexSound[] sceneSounds=new CodexSound[{len(sources)}]; private boolean[] soundActive=new boolean[{len(sources)}];',
          ' private void stopSceneSound(int i) { soundActive[i]=false; if(sceneSounds[i]!=null) { sceneSounds[i].Stop(); sceneSounds[i]=null; } }',
          ' private boolean startSceneSound(int i) { if(sceneSounds[i]!=null) return true; if(player==0) return false; switch(i) {']
    for i,(name,value) in enumerate(sources.items()):
        point=next(p for p in scene['waypoints'] if p['id']==value['waypoint'])
        code.append(f' case {i}: sceneSounds[i]=new CodexSound({js(value["resource"]+".wav")},{float(value["min_distance"])}f,{float(value["max_distance"])}f,{value["volume"]},0,SOUND_FLAG_LOOP,{jv(point["transform"]["position"])}); soundActive[i]=true; trace("SOUND_LOOP_START {name}"); return true;')
    code += [' } return false; }',' private void pollSceneSounds() { if(player!=0) for(int i=0;i<sceneSounds.length;i++) if(soundActive[i] && sceneSounds[i]==null) startSceneSound(i); }',
             ' private void stopSceneSounds() { for(int i=0;i<sceneSounds.length;i++) stopSceneSound(i); }']
    java=java.replace('ticks++;','pollSceneSounds(); ticks++;',1)
    java=java.replace('public void save(int capture) {','public void save(int capture) { for(int i=0;i<soundActive.length;i++) CodexSequence.SaveBoolean(soundActive[i]);',1)
    java=java.replace('public void restore(int capture) {','public void restore(int capture) { for(int i=0;i<soundActive.length;i++) { if(sceneSounds[i]!=null) sceneSounds[i].Stop(); sceneSounds[i]=null; soundActive[i]=CodexSequence.RestoreBoolean(); }',1)
    # Native scripts own these handles. Explicit travel stops them; world end
    # is an additional cleanup path. Save/restore recreates at most one handle.
    java=java.replace('transitioning=true;','stopSceneSounds(); transitioning=true;')
    marker='public void endscene(int client,int next,int capture) {'
    if marker in java:java=java.replace(marker,marker+' stopSceneSounds();',1)
    else:code.append(' public void endscene(int client,int next,int capture) { if(!NetIsClient()) { stopSceneSounds(); releaseCamera(); KillTimer(9400); } }')
    return java[:-2]+'\n'+'\n'.join(code)+'\n}\n'
