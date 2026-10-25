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
    from .dynamic_targets import indices as target_indices
    entities=target_indices(scene,project)
    # AddToActorInventory may report success while consuming type-7 quest
    # tokens. Only a physical inventory member satisfies our give contract.
    java=java.replace('new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); things[i]=item;',
                      'if(!owns(owner,template(i))) { trace("INVENTORY_NOT_RETAINED template="+template(i)+" owner="+owner); return false; } new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); trace("INVENTORY_GIVEN template="+template(i)+" owner="+owner+" item="+item); things[i]=item;')
    # SetTimer appends a native queue entry; it does NOT replace the same ID.
    # A conversation end otherwise starts a second recurring poll chain.
    java=java.replace('SetTimer(0.15f,9400);', 'schedulePoll();')
    lines_timer=' private void schedulePoll() { KillTimer(9400); SetTimer(0.15f,9400); }'
    paths=scene.get('paths',[]);waypoints={r['id']:r for r in scene.get('waypoints',[])}
    lines=[f' private boolean needsArrival=false; private boolean[] patrolRunning=new boolean[{len(paths)}];',
           ' private String positionText(int who) { float[] p=new CodexThing(who).GetPosition(); return p==null ? "null" : p[0]+","+p[1]+","+p[2]; }',
           f' private int[] patrolPoint=new int[{len(paths)}], patrolWait=new int[{len(paths)}];',
           ' private boolean travel(String destination,String entry) { if(player==0 || active!=-1) return false; int flag=-1;']
    # New click links and any unvalidated legacy self-link get an independent
    # runtime guard. Accepted projects without this feature keep their bytes.
    guarded_travel=any('interaction' in o or o.get('geometry',{}).get('mode')=='interactive' for o in scene.get('objects',[])) or any('run_event' in a or a.get('travel',{}).get('scene')==scene['id'] for e in scene['events'] for a in e['actions'])
    if guarded_travel:
        lines[-1]=lines[-1].replace('if(player==0 || active!=-1)',f'if(transitioning || destination.equals({js(scene["id"])}) || player==0 || active!=-1)')
    # Keep the original world factory first. Its zero result in the native
    # tutorial must not strand the campaign: use the accepted near-player
    # factory and explicitly apply the authored transform, or remove the draft.
    for i,e in enumerate(project.entities):
        if e.transform.placement=='absolute':
            replace(f'new CodexWorld(WORLD_CURRENT).CreateThing(template({i}),{jv(e.transform.position)},{jv(e.transform.orientation)})',
                    f'createAt({i},{jv(e.transform.position)},{jv(e.transform.orientation)})')
    factory=''' private int createAt(int index,float[] position,float[] orientation) {
 int guid=new CodexWorld(WORLD_CURRENT).CreateThing(template(index),position,orientation);
 if(guid!=0 || player==0) return guid;
 boolean loaded=PreloadTemplate(template(index));
 guid=new CodexThing(player).SpawnThingNear(template(index),0.0f,0);
 if(guid==0) { if(ticks%20==0) trace("SPAWN_FACTORY_FAILED template="+template(index)+" preload="+loaded); return 0; }
 CodexThing placed=new CodexThing(guid);
 if(!local(guid) || !placed.SetPosition(position) || !placed.SetOrientation(orientation)) {
 placed.Remove(); trace("SPAWN_POSITION_REJECTED template="+template(index)); return 0;
 }
 trace("SPAWN_RECOVERED template="+template(index)+" guid="+guid+" xyz="+positionText(guid)); return guid;
 }'''
    for s,p in campaign.scenes:
        for point in s.get('entries',[]):
            index=campaign.reserved['arrival/'+s['id']+'/'+point['id']]
            lines.append(f' if(destination.equals({js(s["id"])}) && entry.equals({js(point["id"])})) flag={index};')
    lines.append(' if(flag<0) return false;'+(' transitioning=true; KillTimer(9400);' if guarded_travel else ''))
    # SDK ChangeScene selects a location's NSD, separately from Jump. Explicitly
    # select the authored layout when multiple locations reuse the same NIL.
    for target,target_project in campaign.scenes:
        if target['id']!=scene['id'] and target['level']['source']==scene['level']['source']:
            lines.append(f' if(destination.equals({js(target["id"])})) {{ CodexSequence.ChangeScene(destination,{js(target_project.prefix+".nsd")}); trace("LAYOUT_SELECT "+destination); }}')
    for key,index in campaign.reserved.items():
        if key.startswith('arrival/'):lines.append(f' CodexSequence.ClearChronicleFlag({index});')
    lines+=[' CodexSequence.SetChronicleFlag(flag); trace("TRAVEL "+destination+" entry="+entry); releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump(destination,0); return true; }',
            ' private boolean arrive() { if(!needsArrival || player==0) return !needsArrival; int entry=-1;']
    entries=scene.get('entries',[])
    from .native_arrivals import enabled as native_enabled,ordered as native_ordered
    native_arrivals=native_enabled(campaign,scene)
    native_ids={p['id']:i for i,p in enumerate(native_ordered(scene))}
    for i,point in enumerate(entries):
        index=campaign.reserved['arrival/'+scene['id']+'/'+point['id']]
        lines.append(f' if(CodexSequence.GetChronicleFlag({index})) entry={i};')
    default=next((i for i,p in enumerate(entries) if p['id']==scene.get('default_entry')),-1)
    lines.append(f' if(entry<0) entry={default}; trace("ARRIVAL_BEFORE player="+player+" location="+CodexSequence.GetCurrentLocation()+" xyz="+positionText(player)); boolean ok=true; switch(entry) {{')
    for i,point in enumerate(entries):
        pos=point['transform']['position'];ori=point['transform']['orientation'];flag=campaign.reserved['arrival/'+scene['id']+'/'+point['id']]
        placement=f'CodexPlayer.TeleportPartyToEntrance(player,{native_ids[point["id"]]})' if native_arrivals else f'new CodexThing(player).SetPosition({jv(pos)})'
        lines+= [f' case {i}: ok={placement}; if(ok) ok=new CodexThing(player).SetOrientation({jv(ori)}); if(ok) {{ CodexSequence.ClearChronicleFlag({flag}); trace({js("ARRIVAL "+scene["id"]+"/"+point["id"])}); }} break;']
    lines+=[' } if(!ok) { trace("ARRIVAL_FAILED: engine rejected position/orientation"); return false; } if(entry>=0) CodexCamera.Release(player); trace("ARRIVAL_AFTER xyz="+positionText(player)); needsArrival=false; return true; }',
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
            ' private boolean commandPatrol(int route) { int a=patrolActor(route); float[] target=patrolTarget(route); if(a<0 || !alive(a) || target==null) return false; float[] pos=new CodexThing(things[a]).GetPosition(); if(pos!=null) { double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; switch(route) {',
            *[f' case {i}: tolerance={float(row.get("tolerance",24))}; break;' for i,row in enumerate(paths)],
            ' } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) return true; } new CodexActor(things[a]).ClearActorFlags(THING_AF_AIPAUSED); boolean ok=new CodexActor(things[a]).SendActorToPos(target,patrolSpeed(route)); if(!ok) trace("PATH_FAILED route="+route+" actor="+things[a]); return ok; }',
            ' private boolean startPatrol(int route) { if(patrolRunning[route]) return true; patrolPoint[route]=0; patrolWait[route]=0; patrolRunning[route]=commandPatrol(route); return patrolRunning[route]; }',
            ' private void stopPatrol(int actor) { for(int route=0;route<patrolRunning.length;route++) if(patrolActor(route)==actor) { patrolRunning[route]=false; if(alive(actor)) { CodexActor stopped=new CodexActor(things[actor]); stopped.StopActorAction(); stopped.SetActorFlags(THING_AF_AIPAUSED); } } }',
            ' private void holdPatrols() { for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route] && alive(patrolActor(route))) { new CodexActor(things[patrolActor(route)]).StopActorAction(); new CodexActor(things[patrolActor(route)]).SetActorFlags(THING_AF_AIPAUSED); } }',
            ' private void resumePatrols() { if(transitioning) return; for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]) commandPatrol(route); }',
            ' private void pollPatrols() { if(active!=-1 || pendingDialogueEnd || cameraTicks>0) return; for(int route=0;route<patrolRunning.length;route++) { if(!patrolRunning[route]) continue; int a=patrolActor(route); if(!alive(a)) { patrolRunning[route]=false; continue; } float[] target=patrolTarget(route), pos=new CodexThing(things[a]).GetPosition(); if(target==null || pos==null) { stopPatrol(a); continue; } double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; int count=0; boolean loop=false; switch(route) {']
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
    replace('if(!local(things[i])) return; if(fresh)', 'if(!local(things[i])) { if(ticks%20==0) trace("SPAWN_FAILED template="+template(i)+" guid="+things[i]+" currentLocation="+CodexSequence.GetCurrentLocation()+" playerXYZ="+positionText(player)); return; } if(fresh)')
    replace('ticks++; if(cameraTicks>0','ticks++; pollPatrols(); if(cameraTicks>0')
    replace('if(player!=0 && active==-1 && !transitioning) {','if(player!=0 && active==-1 && !transitioning) { resumeEvents(); if(transitioning) return;')
    replace('CodexCamera.SetupCutscene(who,target,0); cameraPlayer=who;', 'dialogueCamera(who,target); cameraPlayer=who;')
    lines.append(' private void dialogueCamera(int who,int target) { switch(active) {')
    from .camera_presets import shot_arguments, DEFAULT_DIALOGUE_CAMERA
    for i,c in enumerate(scene['conversations']):
        camera=c.get('camera',DEFAULT_DIALOGUE_CAMERA)
        if camera=='native':lines.append(f' case {i}: CodexCamera.SetupCutscene(who,target,0); return;')
        else:lines.append(f' case {i}: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,{shot_arguments(camera)},0,0.3f); return;')
    lines.append(' } }')
    # Original SP/MP scripts explicitly face actors using LookAtThing.
    # A player-spoken line must still frame the NPC, never use who as both
    # endpoints of the camera's line of action.
    partners=' private int dialoguePartner(int index) { switch(index) {'
    for i,c in enumerate(project.conversations):partners+=f' case {i}: return things[{entities[c.speaker]}];'
    lines.append(partners+' } return 0; }')
    lines.append(' private void faceDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; new CodexThing(who).LookAtThing(target); new CodexThing(target).LookAtThing(who); }')
    lines.append(' private void prepareDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; if(IsActorGuid(who)||IsPlayerGuid(who)) new CodexActor(who).StopActorAction(); if(IsActorGuid(target)) new CodexActor(target).StopActorAction(); faceDialogue(who,target); }')
    replace('if(target==0) { switch(active)', 'if(target==0 || target==who) { switch(active)')
    replace('dialogueCamera(who,target);', 'faceDialogue(who,target); dialogueCamera(who,target);')
    replace('int completed=active;', 'trace("DIALOGUE_END "+conversationID(active)+" return="+result+" aborted="+aborted); int completed=active;')
    replace('boolean ok=false; int conversationPlayer=player;', 'holdPatrols(); prepareDialogue(player,dialoguePartner(index)); boolean ok=false; int conversationPlayer=player;')
    replace('trace("conversation failed to start");', 'resumePatrols(); trace("conversation failed to start");')
    replace('player=who; if(aborted) return;', 'player=who; resumePatrols(); if(aborted) return;')
    # The native conversation still owns its UI/actors while convended runs.
    # A nested ExecuteConversation can be torn down by the old conversation's
    # cleanup. Release and dispatch on the next timer, including aborts/travel.
    begin=java.index(' public void convended(')
    end=java.index(' private boolean completeEntry',begin)
    original=java[begin:end]
    body=original[original.index(' switch(completed) {'):]
    java=java[:begin]+''' public void convended(int who,boolean aborted,int result) {
 if(active==-1 || who!=starter || pendingDialogueEnd) return;
 trace("DIALOGUE_END "+conversationID(active)+" return="+result+" aborted="+aborted);
 endedConversation=active; endedPlayer=who; endedResult=result; endedAborted=aborted;
 active=-1; starter=0; pendingDialogueEnd=true; schedulePoll();
 }
 private void finishDialogue() {
 if(!pendingDialogueEnd) return;
 int completed=endedConversation,who=endedPlayer,result=endedResult; boolean aborted=endedAborted;
 pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0;
 CodexCamera.Release(who); cameraPlayer=0; cameraTicks=0;
 trace("DIALOGUE_RELEASE player="+who); player=localPlayer(who); resumePatrols();
 if(aborted || player!=who) return;
'''+body+java[end:]
    lines.append(lines_timer)
    # SDK convreached arguments: starter, event, line, duration, speaker GUID.
    replace('int line,int speaker,int capture)', 'int line,int duration,int speaker)')
    motions=[' private void dialogueMotion(int event,int line,int speaker) { switch(active) {']
    has_overrides=any(l.motion_value is not None for c in project.conversations for n in c.nodes for l in n.lines)
    for ci,c in enumerate(project.conversations):
        order=[n for n in c.nodes if n.id==c.entry]+[n for n in c.nodes if n.id!=c.entry]
        animated=[(ei,li,l) for ei,n in enumerate(order) for li,l in enumerate(n.lines) if l.motion_value is not None]
        if not animated:continue
        motions.append(f' case {ci}:')
        for ei,li,l in animated:
            index=entities[l.speaker]
            # bMotion selects a channel, NOT looping. AI-paused NPCs need a
            # persistent base pose beneath the one-shot action channel.
            motions.append(f' if(event=={ei} && line=={li}) {{ int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[{index}]; if(local(guid)&&IsActorGuid(guid)) {{ CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode({l.motion_value},false,30.0f); if(result>=0) {{ dialogueMotionGuids[{index}]=guid; SetTimer(Math.max(0.01f,result/1000.0f),{9500+index}); }} else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION {c.id}/{order[ei].id}/{li} {l.motion} guid="+guid+" result="+result); }} return; }}')
        motions.append(' break;')
    motions.append(' } }');lines.extend(motions)
    if has_overrides:
        lines += [f' private int[] dialogueMotionGuids=new int[{len(entities)}];',
                  ' private void finishDialogueMotion(int i) { int guid=dialogueMotionGuids[i]; dialogueMotionGuids[i]=0; KillTimer(9500+i); if(local(guid)&&IsActorGuid(guid)&&new CodexActor(guid).GetActorHealth()>0.0f) { new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,true,30.0f); new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION_REST guid="+guid); } }',
                  ' private void clearDialogueMotions(boolean rest) { for(int i=0;i<dialogueMotionGuids.length;i++) { if(rest) finishDialogueMotion(i); else { KillTimer(9500+i); dialogueMotionGuids[i]=0; } } }']
        replace('trace("CONVERSATION_LINE "+active', 'clearDialogueMotions(false); dialogueMotion(event,line,speaker); trace("CONVERSATION_LINE "+active')
        replace('if(id==9400&&!NetIsClient()&&!transitioning)', 'if(id>=9500 && id<9500+dialogueMotionGuids.length) { if(!NetIsClient()) finishDialogueMotion(id-9500); return; } if(id==9400&&!NetIsClient()&&!transitioning)')
        replace('if(!pendingDialogueEnd) return;', 'if(!pendingDialogueEnd) return; clearDialogueMotions(true);')
        replace('public void restored(int capture) {','public void restored(int capture) { clearDialogueMotions(true);')
    else:replace('trace("CONVERSATION_LINE "+active','dialogueMotion(event,line,speaker); trace("CONVERSATION_LINE "+active')
    lines.append(' private boolean pendingDialogueEnd=false, endedAborted=false; private int endedConversation=-1, endedPlayer=0, endedResult=0;')
    replace('if(active!=-1 || !IsPlayerGuid(player))', 'if(active!=-1 || pendingDialogueEnd || !IsPlayerGuid(player))')
    replace('if(NetIsClient()||active!=-1||transitioning', 'if(NetIsClient()||active!=-1||pendingDialogueEnd||transitioning')
    replace('ticks++; pollPatrols();', 'finishDialogue(); if(transitioning) return; ticks++; pollPatrols();')
    replace('if(player!=0 && active==-1 && !transitioning)', 'if(player!=0 && active==-1 && !pendingDialogueEnd && !transitioning)')
    replace('active=-1; starter=0; transitioning=false; releaseCamera();', 'active=-1; starter=0; pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0; transitioning=false; releaseCamera();')
    # Modern quests reveal only their current step, avoiding a second journal
    # row with a summary that discloses the whole route. Legacy output stays
    # unchanged; state, completion and rewards still use Chronicle Flags.
    for qi,q in enumerate(campaign.source.get('quests',[])):
        qn='R_'+campaign.id+'_q'+str(qi)
        replace(f'CodexQuest.Load({js(qn)})<0 || CodexQuest.Load({js(qn+"s0")})<0', f'CodexQuest.Load({js(qn+"s0")})<0')
        replace(f'if(!completeEntry({js(qn)})) return false; ', '')
    # Additional records are explicitly covered by the versioned save contract.
    replace('public void save(int capture) {', 'public void save(int capture) { trace("SAVE_STATE '+scene['id']+'"); for(int route=0;route<patrolRunning.length;route++) { CodexSequence.SaveBoolean(patrolRunning[route]); CodexSequence.SaveInt(patrolPoint[route]); CodexSequence.SaveInt(patrolWait[route]); }')
    replace('public void restore(int capture) {', 'public void restore(int capture) { trace("RESTORE_STATE '+scene['id']+'"); needsArrival=false; pendingStart=false; for(int route=0;route<patrolRunning.length;route++) { patrolRunning[route]=CodexSequence.RestoreBoolean(); patrolPoint[route]=CodexSequence.RestoreInt(); patrolWait[route]=CodexSequence.RestoreInt(); }')
    # MP restoration may recreate the player from the Crypt/entrance. Retain
    # this local player's actual save-time pose separately from arrivals.
    pose=''' private boolean savedPose=false, restorePosePending=false; private int restorePoseDelay=0,restorePoseAttempts=0; private float[] savedPosition=new float[3],savedOrientation=new float[3];
 private boolean finitePose(float[] v) { if(v==null || v.length!=3) return false; for(int axis=0;axis<3;axis++) if(Float.isNaN(v[axis]) || Float.isInfinite(v[axis])) return false; return true; }
 private void savePlayerPose() { int who=localPlayer(player); float[] position=who==0?null:new CodexThing(who).GetPosition(), orientation=who==0?null:new CodexThing(who).GetOrientation(); savedPose=who!=0 && finitePose(position) && finitePose(orientation); CodexSequence.SaveBoolean(savedPose); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?position[axis]:0.0f); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?orientation[axis]:0.0f); trace("SAVE_POSE player="+who+" xyz="+(who==0?"none":positionText(who))); }
 private void readPlayerPose() { savedPose=CodexSequence.RestoreBoolean(); for(int axis=0;axis<3;axis++) savedPosition[axis]=CodexSequence.RestoreFloat(); for(int axis=0;axis<3;axis++) savedOrientation[axis]=CodexSequence.RestoreFloat(); restorePosePending=savedPose && finitePose(savedPosition) && finitePose(savedOrientation); restorePoseDelay=1; restorePoseAttempts=0; if(savedPose&&!restorePosePending) trace("RESTORE_POSE_INVALID"); }
 private boolean restorePlayerPose() {
'''
    for point in entries:
        flag=campaign.reserved['arrival/'+scene['id']+'/'+point['id']]
        pose+=f' if(CodexSequence.GetChronicleFlag({flag})) {{ restorePosePending=false; restoredState=false; needsArrival=true; pendingStart=true; trace("RESTORE_TRAVEL_ARRIVAL"); return true; }}\n'
    pose+=''' if(!restorePosePending) return true; if(restorePoseDelay>0) { restorePoseDelay--; return false; } if(++restorePoseAttempts>20) { restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE_FAILED: keeping native player position"); return true; } if(player==0) return false; CodexThing actor=new CodexThing(player); if(!actor.SetPosition(savedPosition) || !actor.SetOrientation(savedOrientation)) { trace("RESTORE_POSE_RETRY"); return false; } restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player="+player+" xyz="+positionText(player)); return true; }
'''
    # Native TeleportPartyToEntrance resets movement (Thing.Stop) and cancels
    # the actor action after relocation; SetPosition alone omits both calls.
    # Opt in for format 10/new click layers; preserve the accepted format 9.
    if campaign.source.get('runtime_profile')=='phase10' or any('interaction' in o or o.get('geometry',{}).get('mode')=='interactive' for o in scene.get('objects',[])):
        pose=pose.replace('if(!actor.SetPosition(savedPosition) || !actor.SetOrientation(savedOrientation))', 'if(!actor.SetPosition(savedPosition))')
        pose=pose.replace('restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player=', 'resetArrivalMotion(); if(!actor.SetOrientation(savedOrientation)) return false; restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player=')
        lines.append(' private void resetArrivalMotion() { CodexActor actor=new CodexActor(player); actor.Stop(); actor.CancelActorAction(); trace("ARRIVAL_MOTION_RESET player="+player); }')
    lines.append(pose)
    replace('public void save(int capture) {','public void save(int capture) { savePlayerPose();')
    replace('public void restore(int capture) {','public void restore(int capture) { readPlayerPose();')
    replace('restoredState=false; poll(); }','poll(); }')
    replace('player=localPlayer(player); if(pendingStart','player=localPlayer(player); if(!restorePlayerPose()) { schedulePoll(); return; } if(pendingStart')
    replace('for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); poll();', 'for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); if(player!=0) CodexCamera.Release(player); for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]&&!commandPatrol(route)) stopPatrol(patrolActor(route)); trace("RESTORED '+scene['id']+'"); poll();')
    java=java[:-2]+'\n'+factory+'\n'+'\n'.join(lines)+'\n}\n'
    from .cinematics import extend_runtime
    java=extend_runtime(java,scene,project)
    from .audio import extend as extend_audio
    java=extend_audio(java,scene,project)
    from .world_effects import extend as extend_world_effects
    java=extend_world_effects(java,scene,project)
    if any('show_note' in a for e in scene['events'] for a in e['actions']) or any(e['when']=='note_closed' for e in scene['events']):
        from .notes_runtime import extend_notes
        java=extend_notes(java)
    return java
