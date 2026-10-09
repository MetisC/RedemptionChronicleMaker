"""Opt-in runtime extension, leaving accepted legacy bytecode generation unchanged.

Arrival points use SetPosition/SetOrientation after Jump(scene, 0). Waypoint
motion delegates to Redemption's existing pathfinder, never a new navmesh.
"""
from .generator import java_string as js,java_vector as jv

def extend(java,campaign,scene,project):
    def replace(old,new):
        nonlocal java
        if java.count(old)!=1:raise ValueError('Runtime 9: punto de integración ambiguo: '+old[:55])
        java=java.replace(old,new)
    entities={e.id:i for i,e in enumerate(project.entities)}
    paths=scene.get('paths',[]);waypoints={r['id']:r for r in scene.get('waypoints',[])}
    lines=[f' private boolean needsArrival=false; private boolean[] patrolRunning=new boolean[{len(paths)}];',
           f' private int[] patrolPoint=new int[{len(paths)}], patrolWait=new int[{len(paths)}];',
           ' private boolean travel(String destination,String entry) { if(player==0 || active!=-1) return false; int flag=-1;']
    for s,p in campaign.scenes:
        for point in s.get('entries',[]):
            index=campaign.reserved['arrival/'+s['id']+'/'+point['id']]
            lines.append(f' if(destination.equals({js(s["id"])}) && entry.equals({js(point["id"])})) flag={index};')
    lines.append(' if(flag<0) return false;')
    for key,index in campaign.reserved.items():
        if key.startswith('arrival/'):lines.append(f' CodexSequence.ClearChronicleFlag({index});')
    lines+=[' CodexSequence.SetChronicleFlag(flag); trace("TRAVEL "+destination+" entry="+entry); releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump(destination,0); return true; }',
            ' private boolean arrive() { if(!needsArrival || player==0) return !needsArrival; int entry=-1;']
    entries=scene.get('entries',[])
    for i,point in enumerate(entries):
        index=campaign.reserved['arrival/'+scene['id']+'/'+point['id']]
        lines.append(f' if(CodexSequence.GetChronicleFlag({index})) entry={i};')
    default=next((i for i,p in enumerate(entries) if p['id']==scene.get('default_entry')),-1)
    lines.append(f' if(entry<0) entry={default}; boolean ok=true; switch(entry) {{')
    for i,point in enumerate(entries):
        pos=point['transform']['position'];ori=point['transform']['orientation'];flag=campaign.reserved['arrival/'+scene['id']+'/'+point['id']]
        lines+= [f' case {i}: ok=new CodexThing(player).SetPosition({jv(pos)}); if(ok) ok=new CodexThing(player).SetOrientation({jv(ori)}); if(ok) {{ CodexSequence.ClearChronicleFlag({flag}); trace({js("ARRIVAL "+scene["id"]+"/"+point["id"])}); }} break;']
    lines+=[' } if(!ok) { trace("ARRIVAL_FAILED: engine rejected position/orientation"); return false; } needsArrival=false; return true; }',
            ' private int patrolActor(int route) { switch(route) {']
    for i,row in enumerate(paths):lines.append(f' case {i}: return {entities[row["actor"]]};')
    lines+=[' } return -1; }',' private float[] patrolTarget(int route) { switch(route) {']
    for i,row in enumerate(paths):
        lines.append(f' case {i}: switch(patrolPoint[{i}]) {{')
        for j,key in enumerate(row['points']):lines.append(f' case {j}: return {jv(waypoints[key]["transform"]["position"])};')
        lines.append(' } break;')
    lines+=[' } return null; }',
            ' private float patrolSpeed(int route) { switch(route) {']
    for i,row in enumerate(paths):lines.append(f' case {i}: return {float(row.get("speed",90))}f;')
    lines+=[' } return 90.0f; }',
            ' private boolean commandPatrol(int route) { int a=patrolActor(route); float[] target=patrolTarget(route); if(a<0 || !alive(a) || target==null) return false; new CodexActor(things[a]).ClearActorFlags(THING_AF_AIPAUSED); boolean ok=new CodexActor(things[a]).SendActorToPos(target,patrolSpeed(route)); if(!ok) trace("PATH_FAILED route="+route+" actor="+things[a]); return ok; }',
            ' private boolean startPatrol(int route) { if(patrolRunning[route]) return true; patrolPoint[route]=0; patrolWait[route]=0; patrolRunning[route]=commandPatrol(route); return patrolRunning[route]; }',
            ' private void stopPatrol(int actor) { for(int route=0;route<patrolRunning.length;route++) if(patrolActor(route)==actor) { patrolRunning[route]=false; if(alive(actor)) { new CodexActor(things[actor]).StopActorMotion(); new CodexActor(things[actor]).SetActorFlags(THING_AF_AIPAUSED); } } }',
            ' private void holdPatrols() { for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route] && alive(patrolActor(route))) { new CodexActor(things[patrolActor(route)]).StopActorMotion(); new CodexActor(things[patrolActor(route)]).SetActorFlags(THING_AF_AIPAUSED); } }',
            ' private void resumePatrols() { if(transitioning) return; for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]) commandPatrol(route); }',
            ' private void pollPatrols() { if(active!=-1 || cameraTicks>0) return; for(int route=0;route<patrolRunning.length;route++) { if(!patrolRunning[route]) continue; int a=patrolActor(route); if(!alive(a)) { patrolRunning[route]=false; continue; } float[] target=patrolTarget(route), pos=new CodexThing(things[a]).GetPosition(); if(target==null || pos==null) { stopPatrol(a); continue; } double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; int count=0; boolean loop=false; switch(route) {']
    for i,row in enumerate(paths):lines.append(f' case {i}: tolerance={float(row.get("tolerance",24))}; count={len(row["points"])}; loop={str(row.get("loop",False)).lower()}; break;')
    lines+=[' } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) { patrolWait[route]=0; patrolPoint[route]++; if(patrolPoint[route]>=count) { if(loop) patrolPoint[route]=0; else { stopPatrol(a); trace("PATH_COMPLETE route="+route); continue; } } if(!commandPatrol(route)) stopPatrol(a); } else if(++patrolWait[route]>400) { trace("PATH_TIMEOUT route="+route); stopPatrol(a); } } }',
            ' private String conversationID(int index) { switch(index) {']
    for i,c in enumerate(project.conversations):lines.append(f' case {i}: return {js(scene["id"]+"/"+c.id)};')
    lines+=[' } return "unknown"; }']
    lines+=[' private void resumeEvents() {']
    for i,e in enumerate(scene['events']):
        key='progress/'+scene['id']+'/'+e['id']
        if key in campaign.reserved:lines.append(f' if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag({campaign.reserved[key]})) event{i}();')
    lines+=[' }']
    replace('if(!restoredState) { ticks=0; pendingStart=true; }','if(!restoredState) { ticks=0; pendingStart=true; needsArrival=true; }')
    replace('if(pendingStart && player!=0)', 'if(pendingStart && player!=0 && arrive())')
    replace('ticks++; if(cameraTicks>0','ticks++; pollPatrols(); if(cameraTicks>0')
    replace('if(player!=0 && active==-1 && !transitioning) {','if(player!=0 && active==-1 && !transitioning) { resumeEvents(); if(transitioning) return;')
    replace('CodexCamera.SetupCutscene(who,target,0); cameraPlayer=who;', 'CodexCamera.SetupCutscene(who,target,who); CodexCamera.ShotType(CAMERA_SHOT_MS); CodexCamera.ShotAngle(CAMERA_ANGLE_MEDIUM); cameraPlayer=who;')
    replace('int completed=active;', 'trace("DIALOGUE_END "+conversationID(active)+" return="+result+" aborted="+aborted); int completed=active;')
    replace('boolean ok=false; int conversationPlayer=player;', 'holdPatrols(); boolean ok=false; int conversationPlayer=player;')
    replace('trace("conversation failed to start");', 'resumePatrols(); trace("conversation failed to start");')
    replace('player=who; if(aborted) return;', 'player=who; resumePatrols(); if(aborted) return;')
    # Additional records are explicitly covered by the versioned save contract.
    replace('public void save(int capture) {', 'public void save(int capture) { trace("SAVE_STATE '+scene['id']+'"); for(int route=0;route<patrolRunning.length;route++) { CodexSequence.SaveBoolean(patrolRunning[route]); CodexSequence.SaveInt(patrolPoint[route]); CodexSequence.SaveInt(patrolWait[route]); }')
    replace('public void restore(int capture) {', 'public void restore(int capture) { trace("RESTORE_STATE '+scene['id']+'"); needsArrival=false; pendingStart=false; for(int route=0;route<patrolRunning.length;route++) { patrolRunning[route]=CodexSequence.RestoreBoolean(); patrolPoint[route]=CodexSequence.RestoreInt(); patrolWait[route]=CodexSequence.RestoreInt(); }')
    replace('for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); poll();', 'for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); if(player!=0) CodexCamera.Release(player); for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]&&!commandPatrol(route)) stopPatrol(patrolActor(route)); trace("RESTORED '+scene['id']+'"); poll();')
    return java[:-2]+'\n'+'\n'.join(lines)+'\n}\n'
