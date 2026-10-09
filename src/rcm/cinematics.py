"""Timed native shots and existing NCP playback; no speculative NCP writer."""
import math
from .model import mapping, sequence
from .camera_presets import CINEMA_PRESETS as PRESETS, shot_arguments
from .generator import java_string as js, java_vector as jv


def validate_sequence(row,actors,paths,resources,modern,objects=None):
    if not any(k in row for k in ('steps','move_path','camera_path','path_speed','prop_motion','move_at')):return
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
    if 'path_speed' in row:
        value=row['path_speed']
        if 'camera_path' not in row or type(value) not in (int,float) or not math.isfinite(value) or not .01<=value<=100:raise ValueError('Velocidad NCP 0.01..100 requiere recorrido de cámara')
    if 'steps' not in row:return
    steps=sequence(row['steps'],'sequence.steps')
    if not 1<=len(steps)<=64:raise ValueError('Timeline requiere 1..64 planos')
    previous=-1
    for step in steps:
        mapping(step,{'at','actor','preset','angle','transition','focus'},{'at','actor','preset'},'plano')
        if 'focus' in step and step['focus'] not in (objects or {}):raise ValueError('Objeto enfocado ausente')
        at=step['at']
        if type(at) not in (int,float) or not math.isfinite(at) or not previous<at<row['duration']:raise ValueError('Planos en tiempos crecientes anteriores al final')
        if previous==-1 and at!=0:raise ValueError('El primer plano comienza en 0')
        previous=at
        if step['actor'] not in actors or step['preset'] not in PRESETS or step.get('angle','medium') not in ('low','medium','high'):raise ValueError('Actor/preset/ángulo de plano inválido')
        transition=step.get('transition',.3)
        if type(transition) not in (int,float) or not math.isfinite(transition) or not 0<=transition<=10:raise ValueError('Transición de cámara 0..10 segundos')


def extend_runtime(java,scene,project):
    rows=scene.get('sequences',[])
    if not any(any(k in r for k in ('steps','move_path','camera_path','prop_motion')) for r in rows):return java
    entities={e.id:i for i,e in enumerate(project.entities)}
    routes=scene.get('paths',[])
    code=[' private int cinema=-1, cinemaAge=0, cinemaStep=-1, cinemaActor=-1; private boolean cinemaMoving=false;',
          ' private boolean beginCinema(int index) { if(active!=-1 || player==0) return false; releaseCamera(); BeginCutscene(player,0); AIOff(); cinema=index; cinemaAge=0; cinemaStep=-1; cameraPlayer=player; cameraTicks=0; switch(index) {']
    for i,row in enumerate(rows):
        code.append(f' case {i}: if(!alive({entities[row["actor"]]})) {{ stopCinema(); return false; }}')
        if 'prop_motion' in row:
            index=entities[row['prop_motion']['object']]
            code.append(f' spawn({index}); if(!local(things[{index}])) {{ stopCinema(); return false; }}')
        if 'move_path' in row and not row.get('move_at',0):
            route=next(n for n,r in enumerate(routes) if r['id']==row['move_path'])
            code.append(f' if(!startPatrol({route})) {{ stopCinema(); return false; }} cinemaActor=patrolActor({route}); cinemaMoving=true;')
        if 'camera_path' in row:
            code.append(f' if(!CodexCamera.PlayPath(player,GetGUID(),{js(row["camera_path"]+".ncp")},{float(row.get("path_speed",1))}f)) {{ stopCinema(); return false; }}')
        else:code.append(f' CodexCamera.SetupCutscene(player,things[{entities[row["actor"]]}],player);')
        # The triggering poll is t=0, not the first elapsed 150 ms interval.
        code.append(f' cameraTicks={math.ceil(row["duration"]/.15)+1}; pollCinema(); cinemaAge=0; return true;')
    code+=[' } return false; }',
           ' private void stopCinema() { if(cinema<0) return; int client=cameraPlayer; int actor=cinemaActor; cinema=-1; cinemaAge=0; cinemaStep=-1; cinemaActor=-1; cinemaMoving=false; if(actor>=0) stopPatrol(actor); if(client!=0) EndCutscene(client,0); AIOn(); trace("CUTSCENE_END"); }',
           ' private void pollCinema() { if(cinema<0) return; switch(cinema) {']
    for i,row in enumerate(rows):
        code.append(f' case {i}:')
        if 'prop_motion' in row:
            motion=row['prop_motion'];index=entities[motion['object']]
            code.append(f' if(cinemaAge>={math.ceil(motion["at"]/.15)}) {{ if(!local(things[{index}])) {{ trace("CUTSCENE_PROP_MISSING"); releaseCamera(); return; }} float fraction=Math.min(1.0f,Math.max(0.0f,(cinemaAge*0.15f-{float(motion["at"])}f)/{float(motion["duration"])}f)); float[] position={jv(project.entities[index].transform.position)}, delta={jv(motion["translation"])}; for(int axis=0;axis<3;axis++) position[axis]+=delta[axis]*fraction; if(!new CodexThing(things[{index}]).SetPosition(position)) {{ trace("CUTSCENE_PROP_REJECTED"); releaseCamera(); return; }} }}')
        if 'move_path' in row and row.get('move_at',0):
            route=next(n for n,r in enumerate(routes) if r['id']==row['move_path'])
            code.append(f' if(!cinemaMoving && cinemaAge>={math.ceil(row["move_at"]/.15)}) {{ if(!startPatrol({route})) {{ trace("CUTSCENE_PATH_FAILED"); releaseCamera(); return; }} cinemaActor=patrolActor({route}); cinemaMoving=true; }}')
        if 'camera_path' not in row:
            steps=row.get('steps',[dict(at=0,actor=row['actor'],preset=row.get('preset','medium'),angle=row['angle'])])
            for n,step in enumerate(steps):
                focus=entities[step.get('focus',step['actor'])]
                second=f'things[{entities[step["actor"]]}]' if 'focus' in step else 'player'
                code.append(f' if(cinemaStep<{n} && cinemaAge>={math.ceil(step["at"]/.15)}) {{ if(!alive({entities[step["actor"]]}) || !local(things[{focus}])) {{ releaseCamera(); return; }} CodexCamera.SetupCutscene(cameraPlayer,things[{focus}],{second}); CodexCamera.SetShot(cameraPlayer,{shot_arguments(step["preset"],step.get("angle","medium"))},0,{float(step.get("transition",.3))}f); cinemaStep={n}; trace("CUTSCENE_SHOT {row["id"]}/{n}"); }}')
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
    java=java.replace('public void save(int capture) {','public void save(int capture) { CodexSequence.SaveInt(cinemaActor);')
    java=java.replace('public void restore(int capture) {','public void restore(int capture) { cinemaActor=CodexSequence.RestoreInt(); cinema=-1;')
    return java[:-2]+'\n'+'\n'.join(code)+'\n}\n'
