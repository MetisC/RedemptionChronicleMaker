"""Owned native spatial loop handles; existing positioned one-shots stay intact."""
import json
from .generator import java_string as js,java_vector as jv


def has_temporary_music(scene):
    if isinstance(scene,list):return any(has_temporary_music(v) for v in scene)
    if isinstance(scene,dict):return any(k in {'push_music','pop_music'} or has_temporary_music(v) for k,v in scene.items())
    return False


def extend_music(java,scene):
    if not has_temporary_music(scene):return java
    film='cinema' if ' private int cinema=' in java else '-1'
    code='''
 private boolean temporaryMusicOwned=false; private String temporaryPrevious="",temporaryCurrent=""; private int temporaryVolume=0,temporaryFilm=-1;
 private boolean sameMusic(String a,String b) { return a==null ? b==null : a.equalsIgnoreCase(b); }
 private boolean pushTemporaryMusic(String name,int volume) {
  if(temporaryMusicOwned) { trace("MUSIC_TEMP_NESTED_REJECTED"); return false; }
  CodexSound.PushMusic(name,volume); temporaryPrevious=CodexSound.aMusicName; temporaryVolume=CodexSound.musicVolume;
  temporaryCurrent=CodexSound.GetMusicName(); temporaryMusicOwned=true; temporaryFilm=FILM;
  if(temporaryCurrent==null || temporaryCurrent.length()==0) { popTemporaryMusic(); trace("MUSIC_TEMP_START_FAILED"); return false; }
  trace("MUSIC_TEMP_PUSH "+name); return true;
 }
 private boolean popTemporaryMusic() {
  if(!temporaryMusicOwned) { trace("MUSIC_TEMP_UNOWNED_REJECTED"); return false; }
  temporaryMusicOwned=false; temporaryFilm=-1;
  if(!sameMusic(CodexSound.aMusicName,temporaryPrevious) || CodexSound.musicVolume!=temporaryVolume || !sameMusic(CodexSound.GetMusicName(),temporaryCurrent)) { trace("MUSIC_TEMP_FOREIGN_REPLACEMENT"); return false; }
  CodexSound.PopMusic(); trace("MUSIC_TEMP_POP"); return true;
 }
 private void releaseTemporaryMusic() { if(temporaryMusicOwned) popTemporaryMusic(); }
'''.replace('FILM',film)
    # Codex stores one global Java snapshot, not a native stack. No invented
    # save records or replay; ownership is transient and is dropped on restore.
    java=java.replace('public void restore(int capture) {','public void restore(int capture) { temporaryMusicOwned=false; temporaryFilm=-1;',1)
    java=java.replace('transitioning=true;','releaseTemporaryMusic(); transitioning=true;')
    java=java.replace('if(cinema<0) return; int client=cameraPlayer;','if(cinema<0) return; if(temporaryMusicOwned && temporaryFilm==cinema) popTemporaryMusic(); int client=cameraPlayer;',1)
    java=java.replace('CodexSound.StartMusic(', 'temporaryMusicOwned=false; CodexSound.StartMusic(')
    java=java.replace('CodexSound.StopMusic();', 'temporaryMusicOwned=false; CodexSound.StopMusic();')
    marker='public void endscene(int client,int next,int capture) {'
    if marker in java:java=java.replace(marker,marker+' if(!NetIsClient()) releaseTemporaryMusic();',1)
    else:code+=' public void endscene(int client,int next,int capture) { if(!NetIsClient()) releaseTemporaryMusic(); }\n'
    return java[:-2]+'\n'+code+'\n}\n'


def loops(scene):
    found: dict = {}
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
    from .scene_zones import sound_id
    for trigger in scene.get('triggers',[]):
        if 'sound_zone' in trigger:
            name=sound_id(trigger)
            if name in found:raise ValueError('Reserved sound zone ID collision')
            found[name]=dict(trigger['sound_zone'],id=name,loop=True,_position=trigger['transform']['position'])
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
    java=extend_music(java,scene)
    sources=loops(scene)
    if not sources:return java
    from .dynamic_targets import indices
    targets=indices(scene,project)
    def actor_guid(value):return 'player' if value['actor']=='Player' else 'things['+str(targets[value['actor']])+']'
    # Source definitions can occur again in lowered compiler-only events.
    code=[f' private CodexSound[] sceneSounds=new CodexSound[{len(sources)}]; private boolean[] soundActive=new boolean[{len(sources)}];',
          ' private void stopSceneSound(int i) { soundActive[i]=false; if(sceneSounds[i]!=null) { sceneSounds[i].Stop(); sceneSounds[i]=null; } }',
          ' private boolean startSceneSound(int i) { if(sceneSounds[i]!=null) return true; if(player==0) return false; switch(i) {']
    for i,(name,value) in enumerate(sources.items()):
        if 'actor' in value:position=actor_guid(value)
        else:position=jv(value['_position'] if '_position' in value else next(p for p in scene['waypoints'] if p['id']==value['waypoint'])['transform']['position'])
        guard=f' if(!local({position})) return false; soundActorGuid[i]={position};' if 'actor' in value else ''
        code.append(f' case {i}:{guard} sceneSounds[i]=new CodexSound({js(value["resource"]+".wav")},{float(value["min_distance"])}f,{float(value["max_distance"])}f,{value["volume"]},0,SOUND_FLAG_LOOP,{position}); soundActive[i]=true; trace("SOUND_LOOP_START {name}"); return true;')
    code += [' } return false; }',' private void pollSceneSounds() { if(player!=0) for(int i=0;i<sceneSounds.length;i++) if(soundActive[i] && sceneSounds[i]==null) startSceneSound(i); }',
             ' private void stopSceneSounds() { for(int i=0;i<sceneSounds.length;i++) stopSceneSound(i); }']
    from .scene_zones import sound_id,guard as zone_guard
    zones=[(ti,list(sources).index(sound_id(t))) for ti,t in enumerate(scene.get('triggers',[])) if 'sound_zone' in t]
    if zones:
        for i,line in enumerate(code):
            if 'private void pollSceneSounds()' in line:
                pre=''.join(f' if({zone_guard(scene,ti,project.flags)}) {{ if(sceneSounds[{si}]==null) startSceneSound({si}); }} else stopSceneSound({si});' for ti,si in zones)
                excluded=' && '.join(f'i!={si}' for _,si in zones)
                code[i]=line.replace('if(player!=0) for',f'if(player==0) return; {pre} for').replace('if(soundActive[i]',f'if({excluded} && soundActive[i]')
    attached=[(i,row) for i,row in enumerate(sources.values()) if 'actor' in row]
    if attached:
        code.append(f' private int[] soundActorGuid=new int[{len(sources)}];')
        pre=''.join(f' if(soundActive[{i}] && soundActorGuid[{i}]!={actor_guid(row)}) {{ if(sceneSounds[{i}]!=null) sceneSounds[{i}].Stop(); sceneSounds[{i}]=null; soundActorGuid[{i}]=0; }}' for i,row in attached)
        for i,line in enumerate(code):
            if 'private void pollSceneSounds()' in line:code[i]=line.replace('private void pollSceneSounds() {','private void pollSceneSounds() {'+pre)
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
