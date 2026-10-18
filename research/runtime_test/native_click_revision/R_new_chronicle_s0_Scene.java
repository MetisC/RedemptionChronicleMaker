public class R_new_chronicle_s0_Scene extends Codex {
 private boolean[] eventRunning=new boolean[3];
 private int[] clickCaptured=new int[3];
 private int[] things=new int[3];
 private boolean[] enabled=new boolean[3];
 private boolean[] createdOnce=new boolean[3];
 private boolean[] inside=new boolean[0];
 private boolean[] previous=new boolean[3];
 private int active=-1, starter=0, ticks=0, player=0; private boolean restoredState=false, transitioning=false; private int cameraTicks=0, cameraPlayer=0; private boolean pendingStart=false;
 private void trace(String s) { CodexConsole.Print(0,0,"RCM: "+s); try { java.io.File current=new java.io.File("RCM/new_chronicle/runtime_trace.log".replace('/',java.io.File.separatorChar)); new java.io.File(current.getParent()).mkdirs(); if(current.length()>1048576L) { java.io.File old=new java.io.File(current.getPath()+".1"); if(old.exists()&&!old.delete()) return; if(!current.renameTo(old)) return; } java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream(current.getPath(),true)); log.println(System.currentTimeMillis()+"\t"+s); log.close(); } catch(Exception error) { CodexConsole.PrintError("RCM trace: "+error); } }
 private boolean local(int g) { return g!=0 && (IsPlayerGuid(g)||IsActorGuid(g)||IsItemGuid(g)||IsPropGuid(g)||IsWeaponGuid(g)||IsArmorGuid(g)) && new CodexThing(g).GetLocationNum()==CodexSequence.GetCurrentLocation(); }
 private int localPlayer(int g) { if(IsPlayerGuid(g)&&local(g)) return g; g=CodexPlayer.GetCurrentPlayer(); if(IsPlayerGuid(g)&&local(g)) return g; for(int i=0;i<CodexPlayer.GetNumMPPlayers();i++) { g=CodexPlayer.GetMPPlayer(i); if(IsPlayerGuid(g)&&local(g)) return g; } return 0; }
 private boolean alive(int i) { return IsActorGuid(things[i]) && local(things[i]) && new CodexActor(things[i]).GetActorHealth()>0.0f; }
 private int inventory(int owner,String template) { if(!IsActorGuid(owner)) return 0; int item=new CodexActor(owner).GetActorFirstInventoryItem(); for(int n=0;item!=0 && n<4096;n++) { if(template.equalsIgnoreCase(new CodexThing(item).GetTemplateName())) return item; item=new CodexItem(item).GetNextInventoryItem(); } return 0; }
 private boolean owns(int owner,String template) { return inventory(owner,template)!=0; }
 private boolean give(int i,int owner) { if(!IsActorGuid(owner)) return false; if(owns(owner,template(i))) return true; int item=things[i]; if(!IsItemGuid(item)&&!IsWeaponGuid(item)&&!IsArmorGuid(item)) item=new CodexThing(owner).SpawnThingNear(template(i),0.0f,0); if(item==0) return false; if(!new CodexActor(owner).AddToActorInventory(item)) { new CodexThing(item).Remove(); return false; } if(!owns(owner,template(i))) { trace("INVENTORY_NOT_RETAINED template="+template(i)+" owner="+owner); return false; } new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); trace("INVENTORY_GIVEN template="+template(i)+" owner="+owner+" item="+item); things[i]=item; createdOnce[i]=true; return true; }
 private String template(int i) { switch(i) {
 case 0: return "R_new_chronicle_s0_click1";
 case 1: return "R_new_chronicle_s0_click2";
 case 2: return "R_new_chronicle_s0_click3";
 } return ""; }
 private void spawn(int i) { if(local(things[i]) || createdOnce[i]) return; things[i]=(i==0 || i==1 || i==2)?findClick(i):CodexThing.GuidFromCastID(template(i)); boolean fresh=!local(things[i]); if(fresh) { switch(i) {
 case 0:

 things[0]=0; break;
 case 1:

 things[1]=0; break;
 case 2:

 things[2]=0; break;
 } } if(!local(things[i])) { if(ticks%20==0) trace("SPAWN_FAILED template="+template(i)+" guid="+things[i]+" currentLocation="+CodexSequence.GetCurrentLocation()+" playerXYZ="+positionText(player)); return; } if(fresh) { switch(i) {
 } } createdOnce[i]=true; new CodexThing(things[i]).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(things[i]).SetThingFlags(THING_FLAG_SAVEALWAYS); if(i==0 || i==1 || i==2) bindClick(i); else CaptureThing(things[i],i+1); switch(i) {
 } trace("spawn "+template(i)+" guid="+things[i]); }
 public void beginscene(int who,int capture) { if(NetIsClient()) return; trace("SCENE scene1"); player=localPlayer(who); dynamicBegin(restoredState); active=-1; starter=0; transitioning=false; if(!restoredState) { ticks=0; pendingStart=true; needsArrival=true; } poll(); }
 public void timer(int id,float a,float b,float c,float d) { if(id==9400&&!NetIsClient()&&!transitioning) poll(); }
 private void poll() { try { pollImpl(); } catch(Throwable error) { trace("runtime exception: "+error); traceStack(error); schedulePoll(); } } private void pollImpl() { originalReapply(); if(!createdOnce[0]) spawn(0); bindClick(0); if(!createdOnce[1]) spawn(1); bindClick(1); if(!createdOnce[2]) spawn(2); bindClick(2); if(local(things[1])) {
 int base=clickSources[1]; if(!originalMatches(0,base) && (base!=0 || ticks%10==0)) base=clickSources[1]=originalFind(0);
 CodexThing overlay=new CodexThing(things[1]);
 if(base<=0 || (new CodexThing(base).GetRenderFlags()&THING_RENDERFLAG_DONTRENDER)!=0) { overlay.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.SetThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }
 else { CodexThing source=new CodexThing(base); overlay.SetPosition(source.GetPosition()); overlay.SetOrientation(source.GetOrientation()); overlay.ClearRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.ClearThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }
 }  if(local(things[2])) {
 int base=clickSources[2]; if(!originalMatches(1,base) && (base!=0 || ticks%10==0)) base=clickSources[2]=originalFind(1);
 CodexThing overlay=new CodexThing(things[2]);
 if(base<=0 || (new CodexThing(base).GetRenderFlags()&THING_RENDERFLAG_DONTRENDER)!=0) { overlay.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.SetThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }
 else { CodexThing source=new CodexThing(base); overlay.SetPosition(source.GetPosition()); overlay.SetOrientation(source.GetOrientation()); overlay.ClearRenderFlags(THING_RENDERFLAG_DONTRENDER); overlay.ClearThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_DISABLECOLLIDE); }
 } player=localPlayer(player); if(!restorePlayerPose()) { schedulePoll(); return; } if(pendingStart && player!=0 && arrive()) { pendingStart=false; dispatch("scene_start","",0); } if(transitioning) return; finishNote(); finishDialogue(); if(transitioning) return; ticks++; dynamicPoll(); if(transitioning) return; pollPatrols(); if(cameraTicks>0 && --cameraTicks==0) releaseCamera(); for(int i=0;i<enabled.length;i++) if(enabled[i]) spawn(i); if(player!=0 && notePlayer==0 && !pendingNoteEnd && active==-1 && !pendingDialogueEnd && !transitioning) { resumeEvents(); if(transitioning) return;
 } traceState(); if(!transitioning) schedulePoll(); }
 private boolean volume(int which) { for(int n=-1;n<CodexPlayer.GetNumMPPlayers();n++) { int g=n==-1?player:CodexPlayer.GetMPPlayer(n); if(!IsPlayerGuid(g)||!local(g)) continue; float[] v=new CodexThing(g).GetPosition(); switch(which) {
 } } return false; }
 private void dispatch(String kind,String target,int result) { if(transitioning) return;
 if(kind.equals("object_clicked") && target.equals("click1")) { if(event0() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("object_clicked") && target.equals("click2")) { if(event1() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("object_clicked") && target.equals("click3")) { if(event2() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 }
 // source: scene scene1 event click1
 private boolean event0() { if(eventRunning[0]) return false; eventRunning[0]=true; try { if(transitioning || !(true)) return false;
 // action 1: show_note
 trace("ACTION scene scene1 event click1 action 1: show_note");
 if(!showNote("R_new_chronicle_s0_t0_0")) return false;
 
 trace("event scene1/click1"); return true; } finally { eventRunning[0]=false; } }
 // source: scene scene1 event click2
 private boolean event1() { if(eventRunning[1]) return false; eventRunning[1]=true; try { if(transitioning || !(true)) return false;
 // action 1: show_note
 trace("ACTION scene scene1 event click2 action 1: show_note");
 if(!showNote("R_new_chronicle_s0_t1_0")) return false;
 // action 2: reward_xp
 trace("ACTION scene scene1 event click2 action 2: reward_xp");
 if(!IsPlayerGuid(player)) return false; new CodexPlayer(player).AwardPlayerExperience(1000);
 
 trace("event scene1/click2"); return true; } finally { eventRunning[1]=false; } }
 // source: scene scene1 event click3
 private boolean event2() { if(eventRunning[2]) return false; eventRunning[2]=true; try { if(transitioning || CodexSequence.GetChronicleFlag(256) || !((CodexSequence.GetChronicleFlag(272) || (true)))) return false;
 CodexSequence.SetChronicleFlag(272);
 // action 1: start_ambient
 trace("ACTION scene scene1 event click3 action 1: start_ambient");
 if(!CodexSequence.GetChronicleFlag(273)) { CodexSound.StartAmbient("amb_monastery",100); CodexSequence.SetChronicleFlag(273); }
 CodexSequence.SetChronicleFlag(256);
 CodexSequence.ClearChronicleFlag(272);
 trace("event scene1/click3"); return true; } finally { eventRunning[2]=false; } }
 private void releaseCamera() { if(cameraPlayer!=0) CodexCamera.Release(cameraPlayer); cameraPlayer=0; cameraTicks=0; }
 private boolean conversation(int index) { if(notePlayer!=0 || pendingNoteEnd || active!=-1 || pendingDialogueEnd || !IsPlayerGuid(player)) return false; releaseCamera(); holdPatrols(); prepareDialogue(player,dialoguePartner(index)); boolean ok=false; int conversationPlayer=player; active=index; starter=conversationPlayer; try { switch(index) {
 } } catch(Throwable error) { trace("conversation failed: "+error); } if(!ok && active==index && starter==conversationPlayer) { active=-1; starter=0; CodexCamera.Release(conversationPlayer); cameraPlayer=0; cameraTicks=0; resumePatrols(); trace("conversation failed to start"); } return ok; }
 public void clicked(int target,int clicker,int capture) { trace("CLICK_RECEIVED target="+target+" player="+clicker+" capture="+capture); if(NetIsClient()||notePlayer!=0||pendingNoteEnd||active!=-1||pendingDialogueEnd||transitioning||!IsPlayerGuid(clicker)||!local(clicker)) return; player=clicker; noteOrigin=target;
 if(target==things[0]) { dispatch("object_clicked","click1",0);
 return; }
 if(target==things[1]) { dispatch("object_clicked","click2",0);
 return; }
 if(target==things[2]) { dispatch("object_clicked","click3",0);
 return; }
 }
 public void convreached(int who,int event,int line,int duration,int speaker) { if(active==-1||who!=starter) return; int target=local(speaker)?speaker:0; if(target==0 || target==who) { switch(active) {
 } } dialogueMotion(event,line,speaker); trace("CONVERSATION_LINE "+active+" player="+who+" speaker="+speaker+" target="+target); if(local(target)) { faceDialogue(who,target); dialogueCamera(who,target); cameraPlayer=who; cameraTicks=0; } }
 public void convended(int who,boolean aborted,int result) {
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
 switch(completed) {
 } }
 private boolean completeEntry(String name) { int q=CodexQuest.Load(name); if(q<0) return false; new CodexQuest(q).Complete(); return true; }
 private boolean quest(String id,int action) {
 return false; }
 public void save(int capture) { dynamicSave(); savePlayerPose(); trace("SAVE_STATE scene1"); for(int route=0;route<patrolRunning.length;route++) { CodexSequence.SaveBoolean(patrolRunning[route]); CodexSequence.SaveInt(patrolPoint[route]); CodexSequence.SaveInt(patrolWait[route]); } for(int i=0;i<things.length;i++) { CodexSequence.SaveInt(things[i]); CodexSequence.SaveBoolean(enabled[i]); CodexSequence.SaveBoolean(createdOnce[i]); } for(int i=0;i<previous.length;i++) CodexSequence.SaveBoolean(previous[i]); CodexSequence.SaveInt(ticks); }
 public void restore(int capture) { dynamicRestore(); readPlayerPose(); trace("RESTORE_STATE scene1"); needsArrival=false; pendingStart=false; for(int route=0;route<patrolRunning.length;route++) { patrolRunning[route]=CodexSequence.RestoreBoolean(); patrolPoint[route]=CodexSequence.RestoreInt(); patrolWait[route]=CodexSequence.RestoreInt(); } for(int i=0;i<things.length;i++) { things[i]=CodexSequence.RestoreInt(); enabled[i]=CodexSequence.RestoreBoolean(); createdOnce[i]=CodexSequence.RestoreBoolean(); } for(int i=0;i<previous.length;i++) previous[i]=CodexSequence.RestoreBoolean(); ticks=CodexSequence.RestoreInt(); restoredState=true; }
 public void restored(int capture) { for(int i=0;i<clickCaptured.length;i++) clickCaptured[i]=0; for(int i=0;i<originalApplied.length;i++) originalApplied[i]=false; notePlayer=0; noteOrigin=0; pendingNoteEnd=false; if(NetIsClient()) return; active=-1; starter=0; pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0; transitioning=false; releaseCamera(); for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); if(player!=0) CodexCamera.Release(player); for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]&&!commandPatrol(route)) stopPatrol(patrolActor(route)); trace("RESTORED scene1"); poll(); }

 private int createAt(int index,float[] position,float[] orientation) {
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
 }
 private boolean needsArrival=false; private boolean[] patrolRunning=new boolean[0];
 private String positionText(int who) { float[] p=new CodexThing(who).GetPosition(); return p==null ? "null" : p[0]+","+p[1]+","+p[2]; }
 private int[] patrolPoint=new int[0], patrolWait=new int[0];
 private boolean travel(String destination,String entry) { if(transitioning || destination.equals("scene1") || player==0 || active!=-1) return false; int flag=-1;
 if(destination.equals("scene1") && entry.equals("entry1")) flag=271;
 if(flag<0) return false; transitioning=true; KillTimer(9400);
 CodexSequence.ClearChronicleFlag(271);
 CodexSequence.SetChronicleFlag(flag); trace("TRAVEL "+destination+" entry="+entry); releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump(destination,0); return true; }
 private boolean arrive() { if(!needsArrival || player==0) return !needsArrival; int entry=-1;
 if(CodexSequence.GetChronicleFlag(271)) entry=0;
 if(entry<0) entry=0; trace("ARRIVAL_BEFORE player="+player+" location="+CodexSequence.GetCurrentLocation()+" xyz="+positionText(player)); boolean ok=true; switch(entry) {
 case 0: ok=CodexPlayer.TeleportPartyToEntrance(player,0); if(ok) ok=new CodexThing(player).SetOrientation(new float[]{0.0f, 0.0f, 0.0f}); if(ok) { CodexSequence.ClearChronicleFlag(271); trace("ARRIVAL scene1/entry1"); } break;
 } if(!ok) { trace("ARRIVAL_FAILED: engine rejected position/orientation"); return false; } if(entry>=0) CodexCamera.Release(player); trace("ARRIVAL_AFTER xyz="+positionText(player)); needsArrival=false; return true; }
 private int patrolActor(int route) { switch(route) {
 } return -1; }
 private float[] patrolTarget(int route) { switch(route) {
 } return null; }
 private float patrolSpeed(int route) { switch(route) {
 } return 90.0f; }
 private boolean commandPatrol(int route) { int a=patrolActor(route); float[] target=patrolTarget(route); if(a<0 || !alive(a) || target==null) return false; float[] pos=new CodexThing(things[a]).GetPosition(); if(pos!=null) { double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; switch(route) {
 } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) return true; } new CodexActor(things[a]).ClearActorFlags(THING_AF_AIPAUSED); boolean ok=new CodexActor(things[a]).SendActorToPos(target,patrolSpeed(route)); if(!ok) trace("PATH_FAILED route="+route+" actor="+things[a]); return ok; }
 private boolean startPatrol(int route) { if(patrolRunning[route]) return true; patrolPoint[route]=0; patrolWait[route]=0; patrolRunning[route]=commandPatrol(route); return patrolRunning[route]; }
 private void stopPatrol(int actor) { for(int route=0;route<patrolRunning.length;route++) if(patrolActor(route)==actor) { patrolRunning[route]=false; if(alive(actor)) { CodexActor stopped=new CodexActor(things[actor]); stopped.StopActorAction(); stopped.SetActorFlags(THING_AF_AIPAUSED); } } }
 private void holdPatrols() { for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route] && alive(patrolActor(route))) { new CodexActor(things[patrolActor(route)]).StopActorAction(); new CodexActor(things[patrolActor(route)]).SetActorFlags(THING_AF_AIPAUSED); } }
 private void resumePatrols() { if(transitioning) return; for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]) commandPatrol(route); }
 private void pollPatrols() { if(active!=-1 || pendingDialogueEnd || cameraTicks>0) return; for(int route=0;route<patrolRunning.length;route++) { if(!patrolRunning[route]) continue; int a=patrolActor(route); if(!alive(a)) { patrolRunning[route]=false; continue; } float[] target=patrolTarget(route), pos=new CodexThing(things[a]).GetPosition(); if(target==null || pos==null) { stopPatrol(a); continue; } double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; int count=0; boolean loop=false; switch(route) {
 } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) { patrolWait[route]=0; patrolPoint[route]++; if(patrolPoint[route]>=count) { if(loop) patrolPoint[route]=0; else { stopPatrol(a); trace("PATH_COMPLETE route="+route); continue; } } if(!commandPatrol(route)) stopPatrol(a); } else if(++patrolWait[route]>400) { trace("PATH_TIMEOUT route="+route); stopPatrol(a); } } }
 private String conversationID(int index) { switch(index) {
 } return "unknown"; }
 private void resumeEvents() {
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(272)) event2();
 }
 private void dialogueCamera(int who,int target) { switch(active) {
 } }
 private int dialoguePartner(int index) { switch(index) { } return 0; }
 private void faceDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; new CodexThing(who).LookAtThing(target); new CodexThing(target).LookAtThing(who); }
 private void prepareDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; if(IsActorGuid(who)||IsPlayerGuid(who)) new CodexActor(who).StopActorAction(); if(IsActorGuid(target)) new CodexActor(target).StopActorAction(); faceDialogue(who,target); }
 private void schedulePoll() { KillTimer(9400); SetTimer(0.15f,9400); }
 private void dialogueMotion(int event,int line,int speaker) { switch(active) {
 } }
 private boolean pendingDialogueEnd=false, endedAborted=false; private int endedConversation=-1, endedPlayer=0, endedResult=0;
 private void resetArrivalMotion() { CodexActor actor=new CodexActor(player); actor.Stop(); actor.CancelActorAction(); trace("ARRIVAL_MOTION_RESET player="+player); }
 private boolean savedPose=false, restorePosePending=false; private int restorePoseDelay=0,restorePoseAttempts=0; private float[] savedPosition=new float[3],savedOrientation=new float[3];
 private boolean finitePose(float[] v) { if(v==null || v.length!=3) return false; for(int axis=0;axis<3;axis++) if(Float.isNaN(v[axis]) || Float.isInfinite(v[axis])) return false; return true; }
 private void savePlayerPose() { int who=localPlayer(player); float[] position=who==0?null:new CodexThing(who).GetPosition(), orientation=who==0?null:new CodexThing(who).GetOrientation(); savedPose=who!=0 && finitePose(position) && finitePose(orientation); CodexSequence.SaveBoolean(savedPose); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?position[axis]:0.0f); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?orientation[axis]:0.0f); trace("SAVE_POSE player="+who+" xyz="+(who==0?"none":positionText(who))); }
 private void readPlayerPose() { savedPose=CodexSequence.RestoreBoolean(); for(int axis=0;axis<3;axis++) savedPosition[axis]=CodexSequence.RestoreFloat(); for(int axis=0;axis<3;axis++) savedOrientation[axis]=CodexSequence.RestoreFloat(); restorePosePending=savedPose && finitePose(savedPosition) && finitePose(savedOrientation); restorePoseDelay=1; restorePoseAttempts=0; if(savedPose&&!restorePosePending) trace("RESTORE_POSE_INVALID"); }
 private boolean restorePlayerPose() {
 if(CodexSequence.GetChronicleFlag(271)) { restorePosePending=false; restoredState=false; needsArrival=true; pendingStart=true; trace("RESTORE_TRAVEL_ARRIVAL"); return true; }
 if(!restorePosePending) return true; if(restorePoseDelay>0) { restorePoseDelay--; return false; } if(++restorePoseAttempts>20) { restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE_FAILED: keeping native player position"); return true; } if(player==0) return false; CodexThing actor=new CodexThing(player); if(!actor.SetPosition(savedPosition)) { trace("RESTORE_POSE_RETRY"); return false; } resetArrivalMotion(); if(!actor.SetOrientation(savedOrientation)) return false; restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player="+player+" xyz="+positionText(player)); return true; }


 private int notePlayer=0,noteOrigin=0; private boolean pendingNoteEnd=false;
 private boolean showNote(String name) {
 if(NetIsClient() || notePlayer!=0 || pendingNoteEnd || active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player)) return false;
 int who=player; notePlayer=who; holdPatrols(); boolean ok=false;
 try { ok=ExecuteText(who,local(noteOrigin)?noteOrigin:0,name); } catch(Throwable error) { trace("NOTE_FAILED "+error); }
 if(!ok) { notePlayer=0; pendingNoteEnd=false; resumePatrols(); trace("NOTE_FAILED "+name); }
 else trace("NOTE_OPEN "+name); noteOrigin=0; return ok;
 }
 public void textended(int who) { if(notePlayer==0 || who!=notePlayer || pendingNoteEnd) return; pendingNoteEnd=true; schedulePoll(); }
 private void finishNote() { if(!pendingNoteEnd) return; int who=notePlayer; notePlayer=0; pendingNoteEnd=false; resumePatrols(); if(!NetIsClient() && localPlayer(who)==who) { player=who; trace("NOTE_CLOSED"); dispatch("note_closed","",0); } }


 private int[] dState=new int[0],dWave=new int[0],dWait=new int[0],dCursor=new int[0],dStreamEntry=new int[0],dStreamLeft=new int[0],dPoint=new int[0],dFailures=new int[0],dTotal=new int[0],dKills=new int[0],dCap=new int[0],dLimit=new int[0],dInterval=new int[0],dTarget=new int[0],dRetry=new int[0],dPolicy=new int[0],dCooldown=new int[0],dMode=new int[0],dFlag=new int[0],dStartFlag=new int[0],dBossActor=new int[0],dBossRole=new int[0];
 private boolean[] dWaveOpen=new boolean[0],dUnsafe=new boolean[0],dRemove=new boolean[0],dRandom=new boolean[0],dRandomPoint=new boolean[0],dNear=new boolean[0];
 private int[][] dGuid=new int[0][],dSlotEntry=new int[0][],dSpawned=new int[0][],dRole=new int[0][],dEntryWave=new int[0][],dCount=new int[0][],dWeight=new int[0][],dTeam=new int[0][],dRoleTotal=new int[0][],dRoleKills=new int[0][],dDelay=new int[0][],dPointSet=new int[0][],dPointCount=new int[0][];
 private String[][] dTemplate=new String[0][],dRoleName=new String[0][];
 private String dScene="scene1"; private String[] dName=new String[0]; private float[][] dHealth=new float[0][],dMultiplier=new float[0][];
 private boolean[][] dAttached=new boolean[0][],dPhasePending=new boolean[0][],dPhaseDone=new boolean[0][];
 private float[] dBossPrevious=new float[0]; private boolean[] dBossSeen=new boolean[0];
 private boolean dConfigured=false,dRestoring=false; private int dRestoreWait=0,dBudget=0,dNotifyDepth=0;
 private void dynamicConfigure() { if(dConfigured) return; dConfigured=true;
 }
 private float[] dynamicPosition(int g,int e,int point,boolean orientation) { int set=dPointSet[g][e]; switch(set/32) {
 } return null; }
 private String dynamicPointName(int g,int e,int point) { int set=dPointSet[g][e]; switch(set/32) {
 } return "near_player"; }
 private int dynamicPoints(int g,int e) { return dPointCount[g][e]; }
 private void dynamicPhases(int g) { switch(g) {
 } }
 private void dynamicNotify(String kind,int g,int wave) { if(dNotifyDepth>=8) { dynamicError(g,"callback cycle"); return; } dNotifyDepth++; try { dispatch(kind,dName[g],wave); } finally { dNotifyDepth--; } }
 private boolean dynamicHealth(int who,boolean percent,float value,String op) { if(!IsActorGuid(who)||!local(who)) return false; CodexActor a=new CodexActor(who); float health=a.GetActorHealth(),max=a.GetActorMaxHealth(); if(percent && max<=0.0f) return false; float limit=percent?max*value/100.0f:value; if(op.equals("<")) return health<limit; if(op.equals("<=")) return health<=limit; if(op.equals(">")) return health>limit; return health>=limit; }
 private int dynamicRoleGuid(int g,int role) { for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && dRole[g][dSlotEntry[g][s]]==role && IsActorGuid(dGuid[g][s]) && new CodexActor(dGuid[g][s]).GetActorHealth()>0.0f) return dGuid[g][s]; return 0; }
 private int dynamicCount(int g,String counter,int role) { dynamicConfigure(); if(counter.equals("wave")) return dState[g]==0?0:dWave[g]+1; if(counter.equals("total")) return role<0?dTotal[g]:dRoleTotal[g][role]; if(counter.equals("killed")) return role<0?dKills[g]:dRoleKills[g][role]; int n=0; for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && (role<0 || dRole[g][dSlotEntry[g][s]]==role)) n++; return n; }
 private boolean dynamicOwned(int g,int s) { int who=dGuid[g][s]; return IsActorGuid(who) && local(who) && dTemplate[g][dSlotEntry[g][s]].equalsIgnoreCase(new CodexThing(who).GetTemplateName()); }
 private void dynamicKilled(int g,int s) { int who=dGuid[g][s],role=dRole[g][dSlotEntry[g][s]]; dGuid[g][s]=0; dAttached[g][s]=false; if(dKills[g]<1000000) dKills[g]++; if(dRoleKills[g][role]<1000000) dRoleKills[g][role]++; ReleaseThing(who); trace("GENERATOR_KILL generator="+dName[g]+" scene="+dScene+" role="+dRoleName[g][role]+" guid="+who); }
 public void killed(int who,int killer,int capture) { dynamicConfigure(); if(NetIsClient()) return; for(int g=0;g<dState.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]==who && who!=0) { if(!IsActorGuid(who) || new CodexActor(who).GetActorHealth()<=0.0f) dynamicKilled(g,s); return; } }
 private boolean dynamicRetire(int g) { for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0) { if(!dynamicOwned(g,s)) return false; int who=dGuid[g][s]; if(!new CodexThing(who).Remove()) return false; ReleaseThing(who); dGuid[g][s]=0; } return true; }
 private void dynamicError(int g,String why) { dState[g]=5; if(why.indexOf("GUID")>=0||why.indexOf("ownership")>=0||why.indexOf("saved")>=0) dUnsafe[g]=true; trace("GENERATOR_ERROR generator="+dName[g]+" scene="+dScene+" reason="+why); }
 private boolean dynamicReset(int g,boolean reentry) { if(dUnsafe[g]) return false; if(dynamicCount(g,"alive",-1)>0 && (!(reentry||dRemove[g]) || !dynamicRetire(g))) return false; dState[g]=0; dWave[g]=0; dWait[g]=0; dCursor[g]=0; dStreamEntry[g]=0; dStreamLeft[g]=0; dPoint[g]=0; dFailures[g]=0; dTotal[g]=0; dKills[g]=0; dWaveOpen[g]=false; dBossSeen[g]=false; for(int p=0;p<dPhasePending[g].length;p++) dPhasePending[g][p]=false; for(int e=0;e<dSpawned[g].length;e++) dSpawned[g][e]=0; for(int r=0;r<dRoleTotal[g].length;r++) { dRoleTotal[g][r]=0; dRoleKills[g][r]=0; } CodexSequence.ClearChronicleFlag(dFlag[g]); CodexSequence.ClearChronicleFlag(dStartFlag[g]); return true; }
 private void dynamicBegin(boolean loading) { dynamicConfigure(); if(loading || dRestoring) return; for(int g=0;g<dState.length;g++) { if(dState[g]==0 && CodexSequence.GetChronicleFlag(dStartFlag[g]) && !CodexSequence.GetChronicleFlag(dFlag[g])) { dUnsafe[g]=true; dynamicError(g,"persistent roster missing"); continue; } if(dPolicy[g]==2 && !dynamicReset(g,true)) dynamicError(g,"reentry ownership"); if(dPolicy[g]==0 && CodexSequence.GetChronicleFlag(dFlag[g])) dState[g]=3; } }
 private boolean dynamicCommand(int g,int command) { dynamicConfigure(); if(NetIsClient()||transitioning||(dUnsafe[g]&&command!=1)) return false; if(command==4) return dynamicReset(g,false); if(command==0) { if(dState[g]==5) return false; if(dState[g]==1||dState[g]==2||dState[g]==3) return true; if(dPolicy[g]==0 && CodexSequence.GetChronicleFlag(dFlag[g])) { dState[g]=3; return true; } if(dState[g]==0 && CodexSequence.GetChronicleFlag(dStartFlag[g]) && !CodexSequence.GetChronicleFlag(dFlag[g])) { dUnsafe[g]=true; dynamicError(g,"persistent roster missing"); return false; } CodexSequence.SetChronicleFlag(dStartFlag[g]); dState[g]=1; if(!dWaveOpen[g]) dWait[g]=dDelay[g][dWave[g]]; trace("GENERATOR_START generator="+dName[g]+" scene="+dScene); dynamicNotify("generator_started",g,0); return true; } if(command==1) { if(dState[g]==4 || dState[g]==3) return true; if(dRemove[g]&&!dynamicRetire(g)) return false; dState[g]=4; trace("GENERATOR_STOP generator="+dName[g]+" scene="+dScene); dynamicNotify("generator_stopped",g,0); return true; } if(command==2) { if(dState[g]==1) { dState[g]=2; trace("GENERATOR_PAUSE generator="+dName[g]+" scene="+dScene); } return true; } if(command==3) { if(dState[g]==2) { dState[g]=1; trace("GENERATOR_RESUME generator="+dName[g]+" scene="+dScene); } return true; } return false; }
 private int dynamicEntry(int g) { if(dMode[g]==1) { if(dStreamLeft[g]>0) return dStreamEntry[g]; if(dRandom[g]) { int sum=0; for(int e=0;e<dWeight[g].length;e++) sum+=dWeight[g][e]; int pick=(int)(Math.random()*sum); for(int e=0;e<dWeight[g].length;e++) { pick-=dWeight[g][e]; if(pick<0) { dStreamEntry[g]=e; dStreamLeft[g]=dCount[g][e]; return e; } } } int cursor=dCursor[g]; dCursor[g]=(cursor+1)%dTemplate[g].length; dStreamEntry[g]=cursor; dStreamLeft[g]=dCount[g][cursor]; return cursor; } for(int e=0;e<dSpawned[g].length;e++) if(dEntryWave[g][e]==dWave[g] && dSpawned[g][e]<dCount[g][e]) return e; return -1; }
 private boolean dynamicSpawn(int g,int e) { int slot=-1; for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]==0) { slot=s; break; } if(slot<0 || player==0 || dBudget<=0) return false; dBudget--; int count=dynamicPoints(g,e),point=count==0?0:(dRandomPoint[g]?(int)(Math.random()*count):dPoint[g]%count); dPoint[g]=(dPoint[g]+1)%Math.max(1,count); String template=dTemplate[g][e]; PreloadTemplate(template); int who=0;
 if(!dNear[g]) who=new CodexWorld(WORLD_CURRENT).CreateThing(template,dynamicPosition(g,e,point,false),dynamicPosition(g,e,point,true));
 if(who==0) who=new CodexThing(player).SpawnThingNear(template,0.0f,0);
 boolean duplicate=false; for(int k=0;k<things.length;k++) if(who!=0&&things[k]==who) duplicate=true; for(int k=0;k<dGuid.length;k++) for(int s=0;s<dGuid[k].length;s++) if(who!=0&&dGuid[k][s]==who) duplicate=true;
 if(duplicate) { dynamicError(g,"factory returned owned GUID"); return false; }
 boolean valid=who!=0 && IsActorGuid(who) && local(who) && template.equalsIgnoreCase(new CodexThing(who).GetTemplateName());
 if(valid&&!dNear[g]) valid=new CodexThing(who).SetPosition(dynamicPosition(g,e,point,false)) && new CodexThing(who).SetOrientation(dynamicPosition(g,e,point,true));
 if(!valid) { if(who!=0&&IsActorGuid(who)&&template.equalsIgnoreCase(new CodexThing(who).GetTemplateName())) new CodexThing(who).Remove(); dFailures[g]++; dWait[g]=2; trace("GENERATOR_SPAWN_FAILED generator="+dName[g]+" scene="+dScene+" template="+template+" point="+dynamicPointName(g,e,point)+" attempt="+dFailures[g]); if(dFailures[g]>=dRetry[g]) dynamicError(g,"spawn retries exhausted"); return false; }
 CodexActor actor=new CodexActor(who); if(dMultiplier[g][e]>0.0f || dHealth[g][e]>0.0f) { float hp=dHealth[g][e]>0.0f?dHealth[g][e]:actor.GetActorHealth()*dMultiplier[g][e],maximum=dHealth[g][e]>0.0f?dHealth[g][e]:actor.GetActorMaxHealth()*dMultiplier[g][e]; actor.SetActorMaxHealth(maximum); actor.SetActorHealth(hp); } if(dTeam[g][e]>=0) actor.SetActorTeam(dTeam[g][e]);
 CodexThing thing=new CodexThing(who); thing.ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); thing.SetThingFlags(THING_FLAG_SAVEALWAYS); dAttached[g][slot]=CaptureThing(who); dGuid[g][slot]=who; dSlotEntry[g][slot]=e; if(dSpawned[g][e]<1000000) dSpawned[g][e]++; if(dTotal[g]<1000000) dTotal[g]++; if(dRoleTotal[g][dRole[g][e]]<1000000) dRoleTotal[g][dRole[g][e]]++; if(dBossRole[g]==dRole[g][e]) { dBossPrevious[g]=actor.GetActorHealth(); dBossSeen[g]=true; } dFailures[g]=0;
 trace("GENERATOR_SPAWN generator="+dName[g]+" scene="+dScene+" wave="+(dWave[g]+1)+" role="+dRoleName[g][dRole[g][e]]+" template="+template+" guid="+who+" point="+dynamicPointName(g,e,point)); return true; }
 private void dynamicComplete(int g) { if(dState[g]==3) return; dState[g]=3; CodexSequence.SetChronicleFlag(dFlag[g]); dWait[g]=dCooldown[g]; trace("GENERATOR_COMPLETE generator="+dName[g]+" scene="+dScene); dynamicNotify("generator_complete",g,0); }
 private void dynamicPoll() { dynamicConfigure(); if(NetIsClient()||transitioning) return; boolean missing=false; for(int g=0;g<dGuid.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0) { if(dynamicOwned(g,s)) { if(!dAttached[g][s]) { ReleaseThing(dGuid[g][s]); dAttached[g][s]=CaptureThing(dGuid[g][s]); } if(new CodexActor(dGuid[g][s]).GetActorHealth()<=0.0f) dynamicKilled(g,s); } else { if(dRestoring) missing=true; else dynamicError(g,"owned GUID missing or nonlocal"); } }
 if(dRestoring) { if(missing && ++dRestoreWait<=20) return; dRestoring=false; if(missing) { for(int g=0;g<dGuid.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0&&!dynamicOwned(g,s)) dynamicError(g,"restored GUID unresolved; no replacement spawned"); } }
 dBudget=4; for(int g=0;g<dState.length;g++) { if(transitioning) return; if(dState[g]==3 && dPolicy[g]==3) { if(dWait[g]>0) { dWait[g]--; continue; } if(dynamicReset(g,false)) dynamicCommand(g,0); } if(dState[g]!=1) continue; dynamicPhases(g); if(transitioning || dState[g]!=1) continue; if(active!=-1||cameraTicks>0||pendingDialogueEnd) continue; if(dWait[g]>0) { dWait[g]--; continue; }
 if(!dWaveOpen[g]) { dWaveOpen[g]=true; trace("GENERATOR_WAVE_START generator="+dName[g]+" scene="+dScene+" wave="+(dWave[g]+1)); dynamicNotify("wave_started",g,dWave[g]+1); if(transitioning||dState[g]!=1) continue; }
 int alive=dynamicCount(g,"alive",-1); if(dMode[g]==1) { if(dLimit[g]>0 && dTotal[g]>=dLimit[g]) { if(alive==0) dynamicComplete(g); continue; } int desired=dTarget[g]>0?dTarget[g]:dCap[g]; if(alive<desired && dBudget>0) { int e=dynamicEntry(g); if(dynamicSpawn(g,e)) { dWait[g]=dInterval[g]; if(dStreamLeft[g]>0) dStreamLeft[g]--; } } continue; }
 int entry=dynamicEntry(g); if(entry>=0 && (dLimit[g]==0 || dTotal[g]<dLimit[g])) { while(dBudget>0 && alive<dCap[g] && entry>=0 && dState[g]==1) { if(!dynamicSpawn(g,entry)) break; alive++; if(dLimit[g]>0&&dTotal[g]>=dLimit[g]) break; entry=dynamicEntry(g); } continue; }
 if(alive==0 && (dBossActor[g]<0 || (IsActorGuid(things[dBossActor[g]]) && local(things[dBossActor[g]]) && new CodexActor(things[dBossActor[g]]).GetActorHealth()<=0.0f))) { trace("GENERATOR_WAVE_COMPLETE generator="+dName[g]+" scene="+dScene+" wave="+(dWave[g]+1)); dynamicNotify("wave_complete",g,dWave[g]+1); if(transitioning||dState[g]!=1) continue; if(dWave[g]+1>=dDelay[g].length || (dLimit[g]>0&&dTotal[g]>=dLimit[g])) dynamicComplete(g); else { dWave[g]++; dWaveOpen[g]=false; dWait[g]=dDelay[g][dWave[g]]; } }
 } }
 private void dynamicSave() { dynamicConfigure(); CodexSequence.SaveInt(1); for(int g=0;g<dState.length;g++) { CodexSequence.SaveInt(dState[g]); CodexSequence.SaveInt(dWave[g]); CodexSequence.SaveInt(dWait[g]); CodexSequence.SaveInt(dCursor[g]); CodexSequence.SaveInt(dStreamEntry[g]); CodexSequence.SaveInt(dStreamLeft[g]); CodexSequence.SaveInt(dPoint[g]); CodexSequence.SaveInt(dFailures[g]); CodexSequence.SaveInt(dTotal[g]); CodexSequence.SaveInt(dKills[g]); CodexSequence.SaveBoolean(dUnsafe[g]); CodexSequence.SaveBoolean(dWaveOpen[g]); CodexSequence.SaveBoolean(dBossSeen[g]); CodexSequence.SaveFloat(dBossPrevious[g]); for(int s=0;s<dGuid[g].length;s++) { CodexSequence.SaveInt(dGuid[g][s]); CodexSequence.SaveInt(dSlotEntry[g][s]); } for(int e=0;e<dSpawned[g].length;e++) CodexSequence.SaveInt(dSpawned[g][e]); for(int r=0;r<dRoleTotal[g].length;r++) { CodexSequence.SaveInt(dRoleTotal[g][r]); CodexSequence.SaveInt(dRoleKills[g][r]); } for(int p=0;p<dPhaseDone[g].length;p++) { CodexSequence.SaveBoolean(dPhaseDone[g][p]); CodexSequence.SaveBoolean(dPhasePending[g][p]); } } }
 private void dynamicRestore() { dynamicConfigure(); int version=CodexSequence.RestoreInt(); dRestoring=true; dRestoreWait=0; for(int g=0;g<dState.length;g++) { dState[g]=CodexSequence.RestoreInt(); dWave[g]=CodexSequence.RestoreInt(); dWait[g]=CodexSequence.RestoreInt(); dCursor[g]=CodexSequence.RestoreInt(); dStreamEntry[g]=CodexSequence.RestoreInt(); dStreamLeft[g]=CodexSequence.RestoreInt(); dPoint[g]=CodexSequence.RestoreInt(); dFailures[g]=CodexSequence.RestoreInt(); dTotal[g]=CodexSequence.RestoreInt(); dKills[g]=CodexSequence.RestoreInt(); dUnsafe[g]=CodexSequence.RestoreBoolean(); dWaveOpen[g]=CodexSequence.RestoreBoolean(); dBossSeen[g]=CodexSequence.RestoreBoolean(); dBossPrevious[g]=CodexSequence.RestoreFloat(); for(int s=0;s<dGuid[g].length;s++) { dGuid[g][s]=CodexSequence.RestoreInt(); dAttached[g][s]=false; dSlotEntry[g][s]=CodexSequence.RestoreInt(); } for(int e=0;e<dSpawned[g].length;e++) dSpawned[g][e]=CodexSequence.RestoreInt(); for(int r=0;r<dRoleTotal[g].length;r++) { dRoleTotal[g][r]=CodexSequence.RestoreInt(); dRoleKills[g][r]=CodexSequence.RestoreInt(); } for(int p=0;p<dPhaseDone[g].length;p++) { dPhaseDone[g][p]=CodexSequence.RestoreBoolean(); dPhasePending[g][p]=CodexSequence.RestoreBoolean(); } for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && (dSlotEntry[g][s]<0 || dSlotEntry[g][s]>=dTemplate[g].length)) { dGuid[g][s]=0; dSlotEntry[g][s]=0; dynamicError(g,"invalid saved slot ownership"); } if(version!=1 || dState[g]<0||dState[g]>5||dWave[g]<0||dWave[g]>=dDelay[g].length||dPoint[g]<0||dCursor[g]<0||dCursor[g]>=Math.max(1,dTemplate[g].length)||dStreamEntry[g]<0||dStreamEntry[g]>=Math.max(1,dTemplate[g].length)||dStreamLeft[g]<0||dStreamLeft[g]>128||dWait[g]<0||dFailures[g]<0||dTotal[g]<0||dTotal[g]>1000000||dKills[g]<0||dKills[g]>1000000) dynamicError(g,"invalid saved state"); } }


 private boolean[] originalApplied=new boolean[2], originalReported=new boolean[2];
 private int originalFlag(int i,int bit) { switch(i) {
 case 0: switch(bit) { case 0: return 257;case 1: return 258;case 2: return 259;case 3: return 260;case 4: return 261;case 5: return 262;case 6: return 263; } break;
 case 1: switch(bit) { case 0: return 264;case 1: return 265;case 2: return 266;case 3: return 267;case 4: return 268;case 5: return 269;case 6: return 270; } break;
 } return -1; }
 private boolean originalBit(int i,int bit) { return CodexSequence.GetChronicleFlag(originalFlag(i,bit)); }
 private void originalSet(int i,int bit,boolean value) { if(value) CodexSequence.SetChronicleFlag(originalFlag(i,bit)); else CodexSequence.ClearChronicleFlag(originalFlag(i,bit)); }
 private boolean originalError(int i,String reason) { if(!originalReported[i]) { trace("ORIGINAL_FAILED "+i+" "+reason); originalReported[i]=true; } return false; }
 private boolean originalNear(float[] p,double x,double y,double z) { if(p==null || p.length<3) return false; double dx=p[0]-x,dy=p[1]-y,dz=p[2]-z; return dx*dx+dy*dy+dz*dz<=64.0; }
 private boolean originalMatches(int i,int guid) { if(!IsPropGuid(guid) || !local(guid) || guid==GetGUID()) return false; for(int n=0;n<things.length;n++) if(things[n]==guid) return false; CodexThing item=new CodexThing(guid); switch(i) {
 case 0: { if(!"drippyCandle".equalsIgnoreCase(item.GetTemplateName())) return false; return originalNear(item.GetPosition(),1144.0,-504.0,-430.0) || (item.HasFrames() && item.GetNumFrames()>0 && originalNear(item.GetFramePosition(0),1144.0,-504.0,-430.0)); }
 case 1: { if(!"drippyCandle".equalsIgnoreCase(item.GetTemplateName())) return false; return originalNear(item.GetPosition(),1136.0,-344.0,-430.0) || (item.HasFrames() && item.GetNumFrames()>0 && originalNear(item.GetFramePosition(0),1136.0,-344.0,-430.0)); }
 } return false; }
 private int originalFind(int i) { switch(i) {
 } int found=0,g=new CodexWorld(WORLD_CURRENT).GetFirstThing(),steps=0; while(g!=0 && steps++<10000) { if(originalMatches(i,g)) { if(found!=0) return -1; found=g; } int next=new CodexThing(g).NextInWorld(); if(next==g) return -1; g=next; } return g==0?found:-1; }
 private boolean originalApply(int i,int operation,int frame,float parameter,boolean opening) {
 if(operation==1 && originalBit(i,6)) return originalError(i,"removed objects cannot be restored; use hide for reversible changes");
 int guid=originalFind(i); if(guid<0) return originalError(i,"ambiguous identity or scan limit"); if(guid==0) { if(operation==2 && originalBit(i,6)) { originalApplied[i]=true; return true; } return originalError(i,"missing/local/template identity"); } CodexThing item=new CodexThing(guid);
 if(operation>=3) { if(!item.HasFrames() || item.GetNumFrames()<=frame) return originalError(i,"missing frame"); boolean ok=operation==3?item.MoveToFrame(frame,parameter):item.RotatePivot(frame,opening?parameter:-parameter); if(!ok) return originalError(i,"engine rejected motion"); originalReported[i]=false; trace("ORIGINAL_DOOR "+i); return true; }
 if(operation==2) { if(!item.Remove()) return originalError(i,"engine rejected removal"); originalSet(i,6,true); originalSet(i,5,false); originalApplied[i]=true; originalReported[i]=false; trace("ORIGINAL_REMOVE "+i); return true; }
 if(!originalBit(i,0)) { originalSet(i,1,(item.GetRenderFlags()&THING_RENDERFLAG_DONTRENDER)!=0); originalSet(i,2,(item.GetThingFlags()&THING_FLAG_DISABLECOLLIDE)!=0); originalSet(i,3,(item.GetThingFlags()&THING_FLAG_VISBLOCK)!=0); originalSet(i,4,(item.GetThingFlags()&THING_FLAG_CAMERABLOCK)!=0); originalSet(i,0,true); }
 if(operation==0) { item.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); item.SetThingFlags(THING_FLAG_DISABLECOLLIDE); item.ClearThingFlags(THING_FLAG_VISBLOCK|THING_FLAG_CAMERABLOCK); originalSet(i,5,true); }
 else { if(originalBit(i,1)) item.SetRenderFlags(THING_RENDERFLAG_DONTRENDER); else item.ClearRenderFlags(THING_RENDERFLAG_DONTRENDER); int[] masks=new int[]{THING_FLAG_DISABLECOLLIDE,THING_FLAG_VISBLOCK,THING_FLAG_CAMERABLOCK}; for(int b=0;b<3;b++) { if(originalBit(i,b+2)) item.SetThingFlags(masks[b]); else item.ClearThingFlags(masks[b]); } originalSet(i,5,false); }
 originalApplied[i]=true; originalReported[i]=false; trace("ORIGINAL_STATE "+i+" "+operation); return true; }
 private void originalReapply() { for(int i=0;i<originalApplied.length;i++) if(!originalApplied[i] && (originalBit(i,0)||originalBit(i,6))) originalApply(i,originalBit(i,6)?2:originalBit(i,5)?0:1,0,1.0f,true); }
 private boolean clickMatches(int i,int guid) {
 if(!IsPropGuid(guid) || !local(guid) || guid==GetGUID()) return false;
 CodexThing item=new CodexThing(guid);
 return template(i).equalsIgnoreCase(item.GetDescriptionID());
 }
 private int findClick(int i) {
 int guid=CodexThing.GuidFromCastID(template(i)); if(clickMatches(i,guid)) return guid;
 int found=0,steps=0; guid=new CodexWorld(WORLD_CURRENT).GetFirstThing();
 while(guid!=0 && steps++<10000) {
 if(clickMatches(i,guid)) { if(found!=0) { trace("CLICK_AMBIGUOUS "+template(i)); return 0; } found=guid; }
 int next=new CodexThing(guid).NextInWorld(); if(next==guid) return 0; guid=next;
 }
 return guid==0?found:0;
 }
 private void bindClick(int i) {
 if(!local(things[i]) || clickCaptured[i]==things[i]) return;
 CodexThing clickable=new CodexThing(things[i]);
 clickable.ClearThingFlags(THING_FLAG_NOHIGHLIGHT|THING_FLAG_BLOCKSELECT|THING_FLAG_PROXIMITYTRIGGER|THING_FLAG_VISBLOCK|THING_FLAG_CAMERABLOCK|THING_FLAG_DISABLECOLLIDE|THING_FLAG_NOBLOCK);
 clickable.SetThingFlags(THING_FLAG_NOSTDELETE);
 if(CaptureThing(things[i],i+1)) { clickCaptured[i]=things[i]; trace("CLICK_BOUND "+template(i)+" guid="+things[i]); }
 else if(ticks%20==0) trace("CLICK_CAPTURE_FAILED "+template(i)+" guid="+things[i]);
 }
 private int[] clickSources=new int[3];
 private int[] watchFlags=new int[]{};
 private String[] watchQuests=new String[]{};
 private String debugPosition(int who) { if(who==0) return "none"; float[] p=new CodexThing(who).GetPosition(); return p==null ? "null" : p[0]+","+p[1]+","+p[2]; }
 private void traceState() {
 if(ticks%60==0) trace("PLAYER_CHECK player="+player+" xyz="+debugPosition(player)+" active="+active);
 }
 private void traceStack(Throwable t) { java.io.StringWriter w=new java.io.StringWriter(); t.printStackTrace(new java.io.PrintWriter(w)); trace("STACK "+w.toString()); }
}
