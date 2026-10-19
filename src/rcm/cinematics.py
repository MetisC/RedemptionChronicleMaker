"""Native choreography through shared Actions; evidenced NCPs are normal resources."""
import math
import copy
from .model import mapping, sequence
from .camera_presets import CINEMA_PRESETS as PRESETS, shot_arguments
from .generator import java_string as js, java_vector as jv
from .dynamic_targets import indices as target_indices

DIRECTOR_ACTIONS={'camera_shot','play_camera_path','camera_fade','camera_flash','camera_filter','clear_camera_effects','look_at','look_at_point','play_motion','stop_actor','set_weather','set_dynamic_light','clear_dynamic_light'}
WEATHER=('drizzle','lightRain','heavyRain','snow')  # Actual original script arguments.


def number(value,low,high,label):
    if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:raise ValueError(label+': valor fuera de rango')


def validate_action(kind,value,scene,actors,objects,resources,modern):
    if kind not in DIRECTOR_ACTIONS:return False
    if not modern:raise ValueError('Esta acción requiere formato de proyecto 9 o 10')
    def actor(key):
        if key!='Player' and key not in actors:raise ValueError('Actor de puesta en escena ausente')
    if kind=='clear_camera_effects':
        if value is not True:raise ValueError('Limpiar efectos requiere true')
    elif kind=='stop_actor':actor(value)
    elif kind=='clear_dynamic_light':
        if value not in {*actors,*objects}:raise ValueError('Entidad de luz ausente')
    elif kind=='set_dynamic_light':
        from .world_effects import STYLES
        mapping(value,{'entity','color','intensity','radius','style'},{'entity','color','intensity','radius'},kind)
        if value['entity'] not in {*actors,*objects}:raise ValueError('Entidad de luz ausente')
        if not isinstance(value['color'],list) or len(value['color'])!=3:raise ValueError('Color de luz requiere tres componentes')
        for component in value['color']:number(component,0,1,'Color de luz')
        number(value['intensity'],0,1000,'Intensidad de luz');number(value['radius'],.01,100000,'Radio de luz')
        if value.get('style','constant') not in STYLES:raise ValueError('Estilo de luz desconocido')
    elif kind=='set_weather':
        if value not in WEATHER:raise ValueError('Clima sin evidencia en scripts originales')
    elif kind in {'look_at','look_at_point'}:
        field='target' if kind=='look_at' else 'waypoint'
        mapping(value,{'actor',field},{'actor',field},kind);actor(value['actor'])
        if kind=='look_at':
            actor(value[field])
            if value['actor']==value[field]:raise ValueError('El actor debe mirar a otro interlocutor')
        elif value[field] not in {r['id'] for r in scene.get('waypoints',[])}:raise ValueError('Punto de mirada ausente')
    elif kind=='play_motion':
        mapping(value,{'actor','motion'},{'actor','motion'},kind)
        if value['actor'] not in actors:raise ValueError('Elige un NPC con motionset conocido')
        from .motions import validate_motion
        for template in actors[value['actor']].get('templates',[actors[value['actor']]['template']]):validate_motion(value['motion'],template,resources)
    elif kind=='play_camera_path':
        mapping(value,{'resource','speed'},{'resource','speed'},kind)
        if len([e for e in resources['entries'] if e['extension']=='.ncp' and e['id']==value['resource']])!=1:raise ValueError('Travelling desconocido o ambiguo')
        number(value['speed'],.01,100,'Velocidad del travelling')
        if any(e.get('timed') and e['id']==value['resource'] for e in resources['entries']) and value['speed']!=1:raise ValueError('Timed camera paths play at speed 1 (seconds)')
    elif kind=='camera_shot':
        mapping(value,{'actor','reference','preset','angle','transition'},{'actor','preset'},kind);actor(value['actor'])
        if value.get('reference'):actor(value['reference'])
        if value['preset'] not in PRESETS or value.get('angle','medium') not in ('low','medium','high'):raise ValueError('Plano de cámara inválido')
        number(value.get('transition',.3),0,10,'Transición')
    elif kind in {'camera_fade','camera_flash'}:
        mapping(value,{'initial','target','duration','bounce'},{'initial','target','duration'},kind)
        for key in ('initial','target'):number(value[key],0,255,'Intensidad')
        number(value['duration'],.01,120,'Duración de efecto')
        if type(value.get('bounce',False)) is not bool:raise ValueError('Rebote requiere booleano')
    elif kind=='camera_filter':
        mapping(value,{'duration'},{'duration'},kind);number(value['duration'],.01,120,'Duración de filtro')
    return True


def action_java(kind,value,scene,project):
    if kind not in DIRECTOR_ACTIONS:return None
    from .dynamic_targets import indices as target_indices
    indices=target_indices(scene,project)
    def guid(name):return 'player' if name=='Player' else f'things[{indices[name]}]'
    if kind=='set_weather':
        from .world_effects import configurations
        return f'applySceneWeather({configurations(scene)[1].index(value)});'
    if kind in {'set_dynamic_light','clear_dynamic_light'}:
        from .world_effects import configurations
        return f'if(!sceneLight({configurations(scene)[0].index({kind:value})})) return false;'
    if kind=='play_camera_path':return f'if(player==0 || !CodexCamera.PlayPath(player,GetGUID(),{js(value["resource"]+".ncp")},{float(value["speed"])}f)) {{ trace("CINEMA_PATH_FAILED"); return false; }} cameraPlayer=player; trace("CINEMA_PATH {value["resource"]}");'
    if kind=='clear_camera_effects':return 'if(player!=0) CodexCamera.ClearAllEffects(player);'
    if kind in {'camera_fade','camera_flash','camera_filter'}:
        if kind=='camera_filter':call=f'CodexCamera.AddFilter(player,{float(value["duration"])}f,16777215)'
        else:
            args=f'player,{float(value["initial"])}f,{float(value["target"])}f,{float(value["duration"])}f,'
            call='CodexCamera.'+('AddFade' if kind=='camera_fade' else 'AddFlash')+'('+args+('16777215,' if kind=='camera_flash' else '')+str(value.get('bounce',False)).lower()+')'
        return f'if(player==0 || {call}<0) {{ trace("CINEMA_EFFECT_FAILED"); return false; }} trace("CINEMA_EFFECT {kind}");'
    if kind=='camera_shot':
        who=guid(value['actor']);other=guid(value.get('reference','Player'))
        return f'if(!local({who}) || !local({other}) || player==0) return false; CodexCamera.SetupCutscene(player,{who},{other}); CodexCamera.SetShot(player,{shot_arguments(value["preset"],value.get("angle","medium"))},0,{float(value.get("transition",.3))}f); cameraPlayer=player;'
    if kind=='stop_actor':
        who=guid(value);return f'if(local({who}) && IsActorGuid({who})) {{ new CodexActor({who}).StopActorAction(); new CodexThing({who}).Stop(); }}'
    who=guid(value['actor'])
    if kind=='look_at':call=f'new CodexThing({who}).LookAtThing({guid(value["target"])})';check=f'!local({guid(value["target"])}) || '
    elif kind=='look_at_point':
        point=next(p for p in scene['waypoints'] if p['id']==value['waypoint']);call=f'new CodexThing({who}).LookAtPos({jv(point["transform"]["position"])})';check=''
    else:return f'if(!stageMotion({indices[value["actor"]]},MOTION_{value["motion"].upper()})) return false;'
    return f'if(!local({who}) || {check}!{call}) {{ trace("CINEMA_ACTOR_MISSING"); return false; }}'


def validate_calls(scene):
    nodes={('event',e['id']):e['actions'] for e in scene['events']}
    nodes.update({('sequence',s['id']):[a for c in s.get('cues',[]) for a in c['actions']] for s in scene.get('sequences',[])})
    visiting=set();done=set()
    def visit(key):
        if key in visiting:raise ValueError('Ciclo entre eventos y secuencias')
        if key in done:return
        if len(visiting)>=32:raise ValueError('Demasiadas llamadas de coreografía')
        visiting.add(key)
        for action in nodes.get(key,[]):
            for name,category in [('run_event','event'),('play_sequence','sequence')]:
                if name in action:visit((category,action[name]))
        visiting.remove(key);done.add(key)
    for key in nodes:visit(key)
    def modal(actions):
        for action in actions:
            if set(action)&{'start_conversation','play_sequence','show_note','jump','travel'}:return True
            if 'run_event' in action and modal(nodes.get(('event',action['run_event']),[])):return True
        return False
    for conversation in scene['conversations']:
        for node in conversation.get('nodes',[]):
            for line in node['lines']:
                if modal(line.get('actions',[])):raise ValueError('Las acciones de línea no pueden abrir otra conversación, nota, película o viaje; usa conversación terminada')


def choreography_events(scene):
    """Lower timed/line actions into the SAME ordinary event compiler.

    These records exist only in compilation, never in the user's event list.
    """
    events=[];cues={};dialogue={};base=len(scene['events'])
    def add(actions):
        index=base+len(events);events.append(dict(id='rcm_director_'+str(index),when='manual',actions=actions));return index
    for si,row in enumerate(scene.get('sequences',[])):
        for ci,cue in enumerate(row.get('cues',[])):cues[si,ci]=add(cue['actions'])
    for ci,conversation in enumerate(scene['conversations']):
        nodes=conversation.get('nodes',[]);ordered=[n for n in nodes if n['id']==conversation['entry']]+[n for n in nodes if n['id']!=conversation['entry']] if nodes else []
        for ni,node in enumerate(ordered):
            for li,line in enumerate(node['lines']):
                if line.get('actions'):dialogue[ci,ni,li]=add(line['actions'])
    return events,cues,dialogue


def compile_scene(scene):
    events,cues,dialogue=choreography_events(scene)
    if not events:return scene
    result=copy.deepcopy(scene);result['events']+=events;result['_director_cues']=cues;result['_director_lines']=dialogue;return result


def conversation_source(row):
    result=copy.deepcopy(row);result.pop('camera',None);result.pop('staging',None)
    for node in result.get('nodes',[]):
        for line in node['lines']:line.pop('actions',None)
    return result


def validate_sequence(row,actors,paths,resources,modern,objects=None):
    if not any(k in row for k in ('steps','move_path','camera_path','path_speed','prop_motion','move_at','cues')):return
    if not modern:raise ValueError('Timeline requiere formato de proyecto 9')
    if 'move_path' in row and row['move_path'] not in paths:raise ValueError('Recorrido de cutscene ausente')
    if 'move_at' in row:
        at=row['move_at']
        if 'move_path' not in row or type(at) not in (int,float) or not math.isfinite(at) or not 0<=at<row['duration']:raise ValueError('Inicio de paseo requiere recorrido y tiempo dentro de la cutscene')
    if 'prop_motion' in row:
        motion=mapping(row['prop_motion'],{'object','at','duration','translation'},{'object','at','duration','translation'},'Movimiento de decorado')
        obj=(objects or {}).get(motion['object'])
        if obj is None or obj.get('transform',{}).get('placement')!='absolute':raise ValueError('Decorado móvil requiere objeto con posición absoluta')
        for key in ['at','duration']:
            value=motion[key]
            if type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError('Tiempo de movimiento inválido')
        if motion['duration']<=0 or motion['at']+motion['duration']>row['duration']:raise ValueError('Movimiento fuera de la duración de la cutscene')
        vector=motion['translation']
        if not isinstance(vector,list) or len(vector)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>10000 for x in vector):raise ValueError('Traslación de decorado requiere tres coordenadas válidas')
    if 'camera_path' in row:
        matches=[e for e in resources['entries'] if e['extension'].lower()=='.ncp' and e['id']==row['camera_path']]
        if len(matches)!=1:raise ValueError('Recorrido de cámara original desconocido o ambiguo')
        if 'steps' in row:raise ValueError('Elige timeline de planos o recorrido NCP')
        if matches[0].get('timed') and row.get('path_speed',1)!=1:raise ValueError('Timed camera paths play at speed 1 (seconds)')
    if 'path_speed' in row:
        value=row['path_speed']
        if 'camera_path' not in row or type(value) not in (int,float) or not math.isfinite(value) or not .01<=value<=100:raise ValueError('Velocidad NCP 0.01..100 requiere recorrido de cámara')
    if 'steps' not in row:return
    steps=sequence(row['steps'],'sequence.steps')
    if not 1<=len(steps)<=64:raise ValueError('Timeline requiere 1..64 planos')
    previous=-1
    for step in steps:
        mapping(step,{'at','actor','preset','angle','transition','focus','reference'},{'at','actor','preset'},'plano')
        if 'reference' in step and step['reference'] not in (*actors,'Player'):raise ValueError('Referencia de cámara ausente')
        if step['actor']=='Player' and 'focus' in step:raise ValueError('Player y foco de objeto son alternativas')
        if 'focus' in step and step['focus'] not in (objects or {}):raise ValueError('Objeto enfocado ausente')
        at=step['at']
        if type(at) not in (int,float) or not math.isfinite(at) or not previous<at<row['duration']:raise ValueError('Planos en tiempos crecientes anteriores al final')
        if previous==-1 and at!=0:raise ValueError('El primer plano comienza en 0')
        previous=at
        if step['actor'] not in (*actors,'Player') or step['preset'] not in PRESETS or step.get('angle','medium') not in ('low','medium','high'):raise ValueError('Actor/preset/ángulo de plano inválido')
        transition=step.get('transition',.3)
        if type(transition) not in (int,float) or not math.isfinite(transition) or not 0<=transition<=10:raise ValueError('Transición de cámara 0..10 segundos')


def extend_runtime(java,scene,project):
    java=extend_staging(java,scene,project)
    rows=scene.get('sequences',[])
    if not any(any(k in r for k in ('steps','move_path','camera_path','prop_motion','cues')) for r in rows):return java
    from .dynamic_targets import indices as target_indices
    entities=target_indices(scene,project)
    routes=scene.get('paths',[])
    code=[' private int cinema=-1, cinemaAge=0, cinemaStep=-1, cinemaActor=-1; private boolean cinemaMoving=false, cinemaRestored=false;',
          ' private boolean beginCinema(int index) { if(active!=-1 || player==0) return false; releaseCamera(); BeginCutscene(player,0); AIOff(); cinema=index; cinemaAge=0; cinemaStep=-1; cameraPlayer=player; cameraTicks=0; switch(index) {']
    for i,row in enumerate(rows):
        target='player' if row['actor']=='Player' else f'things[{entities[row["actor"]]}]'
        guard='!IsPlayerGuid(player)' if row['actor']=='Player' else f'!alive({entities[row["actor"]]})'
        code.append(f' case {i}: if({guard}) {{ stopCinema(); return false; }}')
        if 'prop_motion' in row:
            index=entities[row['prop_motion']['object']]
            code.append(f' spawn({index}); if(!local(things[{index}])) {{ stopCinema(); return false; }}')
        if 'move_path' in row and not row.get('move_at',0):
            route=next(n for n,r in enumerate(routes) if r['id']==row['move_path'])
            code.append(f' if(!startPatrol({route})) {{ stopCinema(); return false; }} cinemaActor=patrolActor({route}); cinemaMoving=true;')
        if 'camera_path' in row:
            code.append(f' if(!CodexCamera.PlayPath(player,GetGUID(),{js(row["camera_path"]+".ncp")},{float(row.get("path_speed",1))}f)) {{ stopCinema(); return false; }}')
        else:
            reference=('player' if row['reference']=='Player' else f'things[{entities[row["reference"]]}]') if row.get('reference') else ('0' if row['actor']=='Player' else 'player')
            code.append(f' CodexCamera.SetupCutscene(player,{target},{reference});')
        # The triggering poll is t=0, not the first elapsed 150 ms interval.
        code.append(f' cameraTicks={math.ceil(row["duration"]/.15)+1}; pollCinema(); '+('if(cinema<0 && !transitioning) return false; ' if row.get('cues') else '')+'cinemaAge=0; return true;')
    code+=[' } return false; }',
           ' private void stopCinema() { if(cinema<0) return; int client=cameraPlayer; int actor=cinemaActor; cinema=-1; cinemaAge=0; cinemaStep=-1; cinemaActor=-1; cinemaMoving=false; if(actor>=0) stopPatrol(actor); if(client!=0) EndCutscene(client,0); AIOn(); trace("CUTSCENE_END"); }',
           ' private void pollCinema() { if(cinema<0) return; switch(cinema) {']
    for i,row in enumerate(rows):
        code.append(f' case {i}:')
        if str(row['actor']).startswith('dynamic/'):
            code.append(f' if(!alive({entities[row["actor"]]})) {{ trace("CINEMA_DYNAMIC_TARGET_MISSING"); releaseCamera(); return; }}')
        if 'prop_motion' in row:
            motion=row['prop_motion'];index=entities[motion['object']]
            code.append(f' if(cinemaAge>={math.ceil(motion["at"]/.15)}) {{ if(!local(things[{index}])) {{ trace("CUTSCENE_PROP_MISSING"); releaseCamera(); return; }} float fraction=Math.min(1.0f,Math.max(0.0f,(cinemaAge*0.15f-{float(motion["at"])}f)/{float(motion["duration"])}f)); float[] position={jv(project.entities[index].transform.position)}, delta={jv(motion["translation"])}; for(int axis=0;axis<3;axis++) position[axis]+=delta[axis]*fraction; if(!new CodexThing(things[{index}]).SetPosition(position)) {{ trace("CUTSCENE_PROP_REJECTED"); releaseCamera(); return; }} }}')
        if 'move_path' in row and row.get('move_at',0):
            route=next(n for n,r in enumerate(routes) if r['id']==row['move_path'])
            code.append(f' if(!cinemaMoving && cinemaAge>={math.ceil(row["move_at"]/.15)}) {{ if(!startPatrol({route})) {{ trace("CUTSCENE_PATH_FAILED"); releaseCamera(); return; }} cinemaActor=patrolActor({route}); cinemaMoving=true; }}')
        if 'camera_path' not in row:
            steps=row.get('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','medium'),angle=row['angle'])])
            for n,step in enumerate(steps):
                if step['actor']=='Player':
                    reference=step.get('reference',row.get('reference'))
                    second=('player' if reference=='Player' else f'things[{entities[reference]}]') if reference else '0'
                    guard=f'!alive({entities[reference]}) || ' if reference and reference!='Player' else ''
                    code.append(f' if(cinemaStep<{n} && cinemaAge>={math.ceil(step["at"]/.15)}) {{ if({guard}!IsPlayerGuid(player) || !local(player)) {{ releaseCamera(); return; }} CodexCamera.SetupCutscene(cameraPlayer,player,{second}); CodexCamera.SetShot(cameraPlayer,{shot_arguments(step["preset"],step.get("angle","medium"))},0,{float(step.get("transition",.3))}f); cinemaStep={n}; trace("CUTSCENE_SHOT {row["id"]}/{n} Player"); }}')
                    continue
                focus=entities[step.get('focus',step['actor'])]
                second=f'things[{entities[step["actor"]]}]' if 'focus' in step else 'player'
                reference=step.get('reference',row.get('reference'));reference_guard=''
                if reference and 'focus' not in step:
                    second='player' if reference=='Player' else f'things[{entities[reference]}]'
                    reference_guard=f'!local({second}) || '
                code.append(f' if(cinemaStep<{n} && cinemaAge>={math.ceil(step["at"]/.15)}) {{ if({reference_guard}!alive({entities[step["actor"]]}) || !local(things[{focus}])) {{ releaseCamera(); return; }} CodexCamera.SetupCutscene(cameraPlayer,things[{focus}],{second}); CodexCamera.SetShot(cameraPlayer,{shot_arguments(step["preset"],step.get("angle","medium"))},0,{float(step.get("transition",.3))}f); cinemaStep={n}; trace("CUTSCENE_SHOT {row["id"]}/{n}"); }}')
        for ci,cue in enumerate(row.get('cues',[])):
            event=scene['_director_cues'][i,ci]
            code.append(f' if(cinemaCue<{ci} && cinemaAge>={math.ceil(cue["at"]/.15)}) {{ cinemaCue={ci}; trace("CINEMA_CUE {row["id"]}/{ci}"); if(!event{event}()) {{ trace("CINEMA_ABORTED cue failed"); releaseCamera(); return; }} if(cinema!={i} || transitioning) return; }}')
        code.append(' break;')
    code+=[' } cinemaAge++; }',
           ' private void finishCameraTimer() { int completed=cinema; releaseCamera(); switch(completed) {']
    for i,row in enumerate(rows):code.append(f' case {i}: trace("CUTSCENE_COMPLETE {row["id"]}"); dispatch("sequence_ended",{js(row["id"])},0); break;')
    code.append(' } }')
    def replace(old,new):
        nonlocal java
        if java.count(old)!=1:raise ValueError('Cutscene: integración ausente o ambigua: '+old)
        java=java.replace(old,new)
    replace('private void releaseCamera() {','private void releaseCamera() { stopCinema();')
    replace('ticks++; pollPatrols();','ticks++; pollCinema(); pollPatrols();')
    replace('if(active!=-1 || pendingDialogueEnd || cameraTicks>0) return;',
            'if(active!=-1 || pendingDialogueEnd || (cameraTicks>0 && cinema<0)) return;')
    replace('if(cameraTicks>0 && --cameraTicks==0) releaseCamera();',
            'if(cameraTicks>0 && --cameraTicks==0) finishCameraTimer();')
    # A click during a timed film must not open a dialogue and release it.
    replace('if(active!=-1 || pendingDialogueEnd || !IsPlayerGuid(player))',
            'if(active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player))')
    replace('if(NetIsClient()||active!=-1||pendingDialogueEnd||transitioning',
            'if(NetIsClient()||active!=-1||pendingDialogueEnd||cameraTicks>0||transitioning')
    # Restore cancels the transient film and stops the route it was driving.
    # This record is included in the versioned save contract, not guessed from
    # whether a general NPC patrol happened to be running during the save.
    replace('public void save(int capture) {','public void save(int capture) { CodexSequence.SaveBoolean(cinema>=0); CodexSequence.SaveInt(cinemaActor);')
    replace('public void restore(int capture) {','public void restore(int capture) { cinemaRestored=CodexSequence.RestoreBoolean(); cinemaActor=CodexSequence.RestoreInt(); cinema=-1;')
    replace('player=localPlayer(0); if(player!=0) CodexCamera.Release(player);', 'player=localPlayer(0); if(cinemaRestored) { if(player!=0) EndCutscene(player,0); AIOn(); if(cinemaActor>=0) stopPatrol(cinemaActor); cinemaActor=-1; cinemaRestored=false; trace("RESTORE_CINEMA_CANCELLED"); } if(player!=0) CodexCamera.Release(player);')
    # Opt-in record for new player films. The established NPC film contract is
    # unchanged. Interrupted Player films replay after the saved pose restores;
    # once event checkpoints and sequence_ended still deliver progress once.
    player_films=[i for i,r in enumerate(rows) if r['actor']=='Player' and not r.get('cues')]
    if player_films:
        code.append(' private int cinemaResume=-1;')
        replace('public void save(int capture) {','public void save(int capture) { CodexSequence.SaveInt(cinemaResume>=0?cinemaResume:cinema);')
        replace('public void restore(int capture) {','public void restore(int capture) { cinemaResume=CodexSequence.RestoreInt();')
        cases=' '.join(f'case {i}: beginCinema(resume); break;' for i in player_films)
        replace('ticks++; pollCinema();', 'if(cinemaResume>=0 && !restorePosePending && player!=0) { int resume=cinemaResume; cinemaResume=-1; switch(resume) { '+cases+' } } ticks++; pollCinema();')
    if scene.get('_director_cues'):
        code.append(' private int cinemaCue=-1; private boolean[] cinemaRoutesBefore=new boolean[patrolRunning.length], cinemaRoutesRestored=new boolean[patrolRunning.length];')
        code=[line.replace('cinema=index; cinemaAge=0;', 'cinema=index; cinemaCue=-1; for(int r=0;r<patrolRunning.length;r++) cinemaRoutesBefore[r]=patrolRunning[r]; trace("CINEMA_START "+index); cinemaAge=0;')
              .replace('if(active!=-1 || player==0) return false;', 'if(active!=-1 || player==0 || cinema>=0 || cameraTicks>0 || pendingDialogueEnd || transitioning) return false;')
              .replace('int client=cameraPlayer; int actor=cinemaActor;', 'int client=cameraPlayer; int actor=cinemaActor; for(int r=0;r<patrolRunning.length;r++) if(patrolRunning[r]&&!cinemaRoutesBefore[r]) stopPatrol(patrolActor(r)); clearStageMotions(); if(client!=0) CodexCamera.ClearAllEffects(client);') for line in code]
        replace('public void save(int capture) {','public void save(int capture) { for(int r=0;r<patrolRunning.length;r++) CodexSequence.SaveBoolean(cinema>=0 && patrolRunning[r]&&!cinemaRoutesBefore[r]);')
        replace('public void restore(int capture) {','public void restore(int capture) { for(int r=0;r<patrolRunning.length;r++) cinemaRoutesRestored[r]=CodexSequence.RestoreBoolean();')
        replace('public void restored(int capture) {','public void restored(int capture) { for(int r=0;r<patrolRunning.length;r++) if(cinemaRoutesRestored[r]) { stopPatrol(patrolActor(r)); cinemaRoutesRestored[r]=false; } if(player!=0) CodexCamera.ClearAllEffects(player);')
        replace('trace("runtime exception: "+error);','if(cinema>=0) { trace("CINEMA_ABORTED exception"); releaseCamera(); } trace("runtime exception: "+error);')
        code.append(' public void endscene(int client,int next,int capture) { if(!NetIsClient()) { releaseCamera(); clearStageMotions(); KillTimer(9400); } }')
    return java[:-2]+'\n'+'\n'.join(code)+'\n}\n'


def extend_staging(java,scene,project):
    """Transient staging shares the existing 150 ms poll, never per-cue timers."""
    actions=[a for e in scene['events'] for a in e['actions']]
    motions=any('play_motion' in a for a in actions)
    line_map=scene.get('_director_lines',{})
    staged=[(i,c['staging']) for i,c in enumerate(scene['conversations']) if c.get('staging')]
    code=[]
    if any('play_camera_path' in a for a in actions):code.append(' public void pathended(int capture) { trace("CINEMA_PATH_END"); if(active<0 && cameraTicks==0) releaseCamera(); }')
    if motions or scene.get('_director_cues'):
        count=len(target_indices(scene,project))
        code += [f' private int[] stageGuids=new int[{count}], stageUntil=new int[{count}];',
                 ' private boolean stageMotion(int i,int mode) { if(!alive(i)) { trace("CINEMA_ACTOR_MISSING"); return false; } int guid=things[i]; CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int duration=actor.PlayMotionSetMode(mode,false,30.0f); if(duration<0) { actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); return false; } stageGuids[i]=guid; stageUntil[i]=ticks+Math.max(1,(duration+149)/150); return true; }',
                 ' private void restStage(int i) { int guid=stageGuids[i]; stageGuids[i]=0; if(local(guid)&&IsActorGuid(guid)&&new CodexActor(guid).GetActorHealth()>0.0f) { new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,true,30.0f); new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,false,30.0f); } }',
                 ' private void pollStageMotions() { for(int i=0;i<stageGuids.length;i++) if(stageGuids[i]!=0 && ticks>=stageUntil[i]) restStage(i); }',
                 ' private void clearStageMotions() { for(int i=0;i<stageGuids.length;i++) if(stageGuids[i]!=0) restStage(i); }']
        java=java.replace('ticks++;','pollStageMotions(); ticks++;',1)
        java=java.replace('public void restored(int capture) {','public void restored(int capture) { clearStageMotions();',1)
    if line_map:
        code.append(' private void directorLine(int event,int line) { int index=active; try {')
        for (ci,ni,li),event in line_map.items():code.append(f' if(index=={ci} && event=={ni} && line=={li}) {{ trace("CINEMA_LINE {ci}/{ni}/{li}"); if(!event{event}()) trace("CINEMA_LINE_FAILED"); return; }}')
        code.append(' } catch(Throwable error) { trace("CINEMA_LINE_FAILED "+error); } }')
        java=java.replace('dialogueCamera(who,target); cameraPlayer=who; cameraTicks=0;', 'dialogueCamera(who,target); cameraPlayer=who; cameraTicks=0; directorLine(event,line);',1)
    if staged:
        from .native_arrivals import ordered,conversation_groups
        entries={p['id']:i for i,p in enumerate(ordered(scene))}
        groups=conversation_groups(scene);cases=[]
        for ci,name in staged:
            if isinstance(name,dict):cases.append(f'case {ci}: if(!CodexPlayer.TeleportPartyToConversation(player,{groups.index(tuple(name["entries"]))})) return false; break; ')
            else:cases.append(f'case {ci}: if(!CodexPlayer.TeleportPartyToEntrance(player,{entries[name]})) return false; new CodexThing(player).SetOrientation({jv(next(p for p in scene["entries"] if p["id"]==name)["transform"].get("orientation",[0,0,0]))}); break; ')
        setup='switch(index) { '+''.join(cases)+' } '
        java=java.replace('holdPatrols(); prepareDialogue(',setup+'holdPatrols(); prepareDialogue(',1)
    if code:java=java[:-2]+'\n'+'\n'.join(code)+'\n}\n'
    return java
