public class R_p9_test_s0_Scene extends Codex {
 private int[] things=new int[2];
 private boolean[] enabled=new boolean[2];
 private boolean[] createdOnce=new boolean[2];
 private boolean[] inside=new boolean[0];
 private boolean[] previous=new boolean[4];
 private int active=-1, starter=0, ticks=0, player=0; private boolean restoredState=false, transitioning=false; private int cameraTicks=0, cameraPlayer=0; private boolean pendingStart=false;
 private void trace(String s) { CodexConsole.Print(0,0,"RCM: "+s); try { java.io.File current=new java.io.File("RCM/p9_test/runtime_trace.log"); new java.io.File(current.getParent()).mkdirs(); if(current.length()>1048576L) { java.io.File old=new java.io.File(current.getPath()+".1"); if(old.exists()&&!old.delete()) return; if(!current.renameTo(old)) return; } java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream(current.getPath(),true)); log.println(s); log.close(); } catch(Exception error) { CodexConsole.PrintError("RCM trace: "+error); } }
 private boolean local(int g) { return g!=0 && (IsPlayerGuid(g)||IsActorGuid(g)||IsItemGuid(g)||IsPropGuid(g)||IsWeaponGuid(g)||IsArmorGuid(g)) && new CodexThing(g).GetLocationNum()==CodexSequence.GetCurrentLocation(); }
 private int localPlayer(int g) { if(IsPlayerGuid(g)&&local(g)) return g; g=CodexPlayer.GetCurrentPlayer(); if(IsPlayerGuid(g)&&local(g)) return g; for(int i=0;i<CodexPlayer.GetNumMPPlayers();i++) { g=CodexPlayer.GetMPPlayer(i); if(IsPlayerGuid(g)&&local(g)) return g; } return 0; }
 private boolean alive(int i) { return IsActorGuid(things[i]) && local(things[i]) && new CodexActor(things[i]).GetActorHealth()>0.0f; }
 private int inventory(int owner,String template) { if(!IsActorGuid(owner)) return 0; int item=new CodexActor(owner).GetActorFirstInventoryItem(); for(int n=0;item!=0 && n<4096;n++) { if(template.equalsIgnoreCase(new CodexThing(item).GetTemplateName())) return item; item=new CodexItem(item).GetNextInventoryItem(); } return 0; }
 private boolean owns(int owner,String template) { return inventory(owner,template)!=0; }
 private boolean give(int i,int owner) { if(!IsActorGuid(owner)) return false; if(owns(owner,template(i))) return true; int item=things[i]; if(!IsItemGuid(item)&&!IsWeaponGuid(item)&&!IsArmorGuid(item)) item=new CodexThing(owner).SpawnThingNear(template(i),0.0f,0); if(item==0) return false; if(!new CodexActor(owner).AddToActorInventory(item)) { new CodexThing(item).Remove(); return false; } if(!owns(owner,template(i))) { trace("INVENTORY_NOT_RETAINED template="+template(i)+" owner="+owner); return false; } new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); trace("INVENTORY_GIVEN template="+template(i)+" owner="+owner+" item="+item); things[i]=item; createdOnce[i]=true; return true; }
 private String template(int i) { switch(i) {
 case 0: return "R_p9_test_s0_victoria";
 case 1: return "R_p9_test_s0_book";
 } return ""; }
 private void spawn(int i) { if(local(things[i]) || createdOnce[i]) return; things[i]=CodexThing.GuidFromCastID(template(i)); boolean fresh=!local(things[i]); if(fresh) { switch(i) {
 case 0:

 things[0]=createAt(0,new float[]{1016.0f, -54.0f, 0.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 1:
 if(player==0) return;
 things[1]=new CodexThing(player).SpawnThingNear(template(1),0.0f,0); break;
 } } if(!local(things[i])) { if(ticks%20==0) trace("SPAWN_FAILED template="+template(i)+" guid="+things[i]+" currentLocation="+CodexSequence.GetCurrentLocation()+" playerXYZ="+positionText(player)); return; } if(fresh) { switch(i) {
 case 1: new CodexThing(things[i]).SetOrientation(new float[]{0.0f, 0.0f, 0.0f}); break;
 } } createdOnce[i]=true; new CodexThing(things[i]).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(things[i]).SetThingFlags(THING_FLAG_SAVEALWAYS); CaptureThing(things[i],i+1); switch(i) {
 case 0: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 } trace("spawn "+template(i)+" guid="+things[i]); }
 public void beginscene(int who,int capture) { if(NetIsClient()) return; player=localPlayer(who); active=-1; starter=0; transitioning=false; if(!restoredState) { ticks=0; pendingStart=true; needsArrival=true; } poll(); }
 public void timer(int id,float a,float b,float c,float d) { if(id>=9500 && id<9500+dialogueMotionGuids.length) { if(!NetIsClient()) finishDialogueMotion(id-9500); return; } if(id==9400&&!NetIsClient()&&!transitioning) poll(); }
 private void poll() { try { pollImpl(); } catch(Throwable error) { trace("runtime exception: "+error); schedulePoll(); } } private void pollImpl() { player=localPlayer(player); if(!restorePlayerPose()) { schedulePoll(); return; } if(pendingStart && player!=0 && arrive()) { pendingStart=false; dispatch("scene_start","",0); } if(transitioning) return; finishDialogue(); if(transitioning) return; ticks++; pollPatrols(); if(cameraTicks>0 && --cameraTicks==0) releaseCamera(); for(int i=0;i<enabled.length;i++) if(enabled[i]) spawn(i); if(player!=0 && active==-1 && !pendingDialogueEnd && !transitioning) { resumeEvents(); if(transitioning) return;
 } if(!transitioning) schedulePoll(); }
 private boolean volume(int which) { for(int n=-1;n<CodexPlayer.GetNumMPPlayers();n++) { int g=n==-1?player:CodexPlayer.GetMPPlayer(n); if(!IsPlayerGuid(g)||!local(g)) continue; float[] v=new CodexThing(g).GetPosition(); switch(which) {
 } } return false; }
 private void dispatch(String kind,String target,int result) { if(transitioning) return;
 if(kind.equals("scene_start")) { if(event0() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("actor_clicked") && target.equals("victoria")) { if(event1() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("actor_clicked") && target.equals("victoria")) { if(event2() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("scene_start")) { if(event3() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 }
 // source: scene london event event1
 private boolean event0() { if(transitioning || !(true)) return false;
 // action 1: spawn
 enabled[0]=true; spawn(0); if(!createdOnce[0]) return false;
 // action 2: spawn
 enabled[1]=true; spawn(1); if(!createdOnce[1]) return false;
 
 trace("event london/event1"); return true; }
 // source: scene london event greet_new
 private boolean event1() { if(transitioning || !(!CodexSequence.GetChronicleFlag(1))) return false;
 // action 1: start_conversation
 if(!conversation(0)) return false;
 
 trace("event london/greet_new"); return true; }
 // source: scene london event greet_ally
 private boolean event2() { if(transitioning || !(CodexSequence.GetChronicleFlag(1))) return false;
 // action 1: start_conversation
 if(!conversation(1)) return false;
 
 trace("event london/greet_ally"); return true; }
 // source: scene london event once_reward
 private boolean event3() { if(transitioning || CodexSequence.GetChronicleFlag(261) || !((CodexSequence.GetChronicleFlag(263) || (true)))) return false;
 CodexSequence.SetChronicleFlag(263);
 // action 1: reward_xp
 if(!CodexSequence.GetChronicleFlag(264)) { if(!IsPlayerGuid(player)) return false; new CodexPlayer(player).AwardPlayerExperience(7); CodexSequence.SetChronicleFlag(264); }
 CodexSequence.SetChronicleFlag(261);
 CodexSequence.ClearChronicleFlag(263);
 trace("event london/once_reward"); return true; }
 private void releaseCamera() { if(cameraPlayer!=0) CodexCamera.Release(cameraPlayer); cameraPlayer=0; cameraTicks=0; }
 private boolean conversation(int index) { if(active!=-1 || pendingDialogueEnd || !IsPlayerGuid(player)) return false; releaseCamera(); holdPatrols(); prepareDialogue(player,dialoguePartner(index)); boolean ok=false; int conversationPlayer=player; active=index; starter=conversationPlayer; try { switch(index) {
 case 0: if(alive(0)) ok=ExecuteConversation(conversationPlayer,0,"R_p9_test_s0_intro","R_p9_test_s0_intro.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 1: if(alive(0)) ok=ExecuteConversation(conversationPlayer,0,"R_p9_test_s0_ally","R_p9_test_s0_ally.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 } } catch(Throwable error) { trace("conversation failed: "+error); } if(!ok && active==index && starter==conversationPlayer) { active=-1; starter=0; CodexCamera.Release(conversationPlayer); cameraPlayer=0; cameraTicks=0; resumePatrols(); trace("conversation failed to start"); } return ok; }
 public void clicked(int target,int clicker,int capture) { if(NetIsClient()||active!=-1||pendingDialogueEnd||transitioning||!IsPlayerGuid(clicker)||!local(clicker)) return; player=clicker;
 if(target==things[0]) { dispatch("actor_clicked","victoria",0);
 return; }
 if(target==things[1]) { dispatch("object_clicked","book",0);
 return; }
 }
 public void convreached(int who,int event,int line,int duration,int speaker) { if(active==-1||who!=starter) return; int target=local(speaker)?speaker:0; if(target==0 || target==who) { switch(active) {
 case 0: target=things[0]; break;
 case 1: target=things[0]; break;
 } } clearDialogueMotions(false); dialogueMotion(event,line,speaker); trace("CONVERSATION_LINE "+active+" player="+who+" speaker="+speaker+" target="+target); if(local(target)) { faceDialogue(who,target); dialogueCamera(who,target); cameraPlayer=who; cameraTicks=0; } }
 public void convended(int who,boolean aborted,int result) {
 if(active==-1 || who!=starter || pendingDialogueEnd) return;
 trace("DIALOGUE_END "+conversationID(active)+" return="+result+" aborted="+aborted);
 endedConversation=active; endedPlayer=who; endedResult=result; endedAborted=aborted;
 active=-1; starter=0; pendingDialogueEnd=true; schedulePoll();
 }
 private void finishDialogue() {
 if(!pendingDialogueEnd) return; clearDialogueMotions(true);
 int completed=endedConversation,who=endedPlayer,result=endedResult; boolean aborted=endedAborted;
 pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0;
 CodexCamera.Release(who); cameraPlayer=0; cameraTicks=0;
 trace("DIALOGUE_RELEASE player="+who); player=localPlayer(who); resumePatrols();
 if(aborted || player!=who) return;
 switch(completed) {
 case 0: switch(result) {
 case 1: dispatch("conversation_ended","intro",result); break;
 } break;
 case 1: switch(result) {
 case 1: dispatch("conversation_ended","ally",result); break;
 case 2: CodexSequence.ClearChronicleFlag(1); dispatch("conversation_ended","ally",result); break;
 } break;
 } }
 private boolean completeEntry(String name) { int q=CodexQuest.Load(name); if(q<0) return false; new CodexQuest(q).Complete(); return true; }
 private boolean quest(String id,int action) {
 if(id.equals("mission")) {
 if(action==0) { if(CodexSequence.GetChronicleFlag(256)) return true;
 if(CodexQuest.Load("R_p9_test_q0s0")<0) { trace("quest load failed"); return false; }
CodexSequence.SetChronicleFlag(256);
 return true; }
 if(action==1 && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257)) {
 if(!CodexSequence.GetChronicleFlag(258)) { if(!completeEntry("R_p9_test_q0s0")) return false;  if(CodexQuest.Load("R_p9_test_q0s1")<0) return false;CodexSequence.SetChronicleFlag(258); return true; }
 else if(!CodexSequence.GetChronicleFlag(259)) { if(!completeEntry("R_p9_test_q0s1")) return false;  if(CodexQuest.Load("R_p9_test_q0s2")<0) return false;CodexSequence.SetChronicleFlag(259); return true; }
 else if(!CodexSequence.GetChronicleFlag(260)) { if(!completeEntry("R_p9_test_q0s2")) return false; CodexSequence.SetChronicleFlag(260); return true; }
 return false; }
 if(action==2 && CodexSequence.GetChronicleFlag(257)) return true;
 if(action==2 && CodexSequence.GetChronicleFlag(256) && CodexSequence.GetChronicleFlag(258) && CodexSequence.GetChronicleFlag(259) && CodexSequence.GetChronicleFlag(260)) { CodexSequence.SetChronicleFlag(257); if(IsPlayerGuid(player)) new CodexPlayer(player).AwardPlayerExperience(500); return true; } return false; }
 return false; }
 public void save(int capture) { savePlayerPose(); trace("SAVE_STATE london"); for(int route=0;route<patrolRunning.length;route++) { CodexSequence.SaveBoolean(patrolRunning[route]); CodexSequence.SaveInt(patrolPoint[route]); CodexSequence.SaveInt(patrolWait[route]); } for(int i=0;i<things.length;i++) { CodexSequence.SaveInt(things[i]); CodexSequence.SaveBoolean(enabled[i]); CodexSequence.SaveBoolean(createdOnce[i]); } for(int i=0;i<previous.length;i++) CodexSequence.SaveBoolean(previous[i]); CodexSequence.SaveInt(ticks); }
 public void restore(int capture) { readPlayerPose(); trace("RESTORE_STATE london"); needsArrival=false; pendingStart=false; for(int route=0;route<patrolRunning.length;route++) { patrolRunning[route]=CodexSequence.RestoreBoolean(); patrolPoint[route]=CodexSequence.RestoreInt(); patrolWait[route]=CodexSequence.RestoreInt(); } for(int i=0;i<things.length;i++) { things[i]=CodexSequence.RestoreInt(); enabled[i]=CodexSequence.RestoreBoolean(); createdOnce[i]=CodexSequence.RestoreBoolean(); } for(int i=0;i<previous.length;i++) previous[i]=CodexSequence.RestoreBoolean(); ticks=CodexSequence.RestoreInt(); restoredState=true; }
 public void restored(int capture) { clearDialogueMotions(true); if(NetIsClient()) return; active=-1; starter=0; pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0; transitioning=false; releaseCamera(); for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); if(player!=0) CodexCamera.Release(player); for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]&&!commandPatrol(route)) stopPatrol(patrolActor(route)); trace("RESTORED london"); poll(); }

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
 private boolean travel(String destination,String entry) { if(player==0 || active!=-1) return false; int flag=-1;
 if(destination.equals("london") && entry.equals("safe")) flag=262;
 if(destination.equals("west") && entry.equals("safe")) flag=265;
 if(flag<0) return false;
 CodexSequence.ClearChronicleFlag(262);
 CodexSequence.ClearChronicleFlag(265);
 CodexSequence.SetChronicleFlag(flag); trace("TRAVEL "+destination+" entry="+entry); releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump(destination,0); return true; }
 private boolean arrive() { if(!needsArrival || player==0) return !needsArrival; int entry=-1;
 if(CodexSequence.GetChronicleFlag(262)) entry=0;
 if(entry<0) entry=0; trace("ARRIVAL_BEFORE player="+player+" location="+CodexSequence.GetCurrentLocation()+" xyz="+positionText(player)); boolean ok=true; switch(entry) {
 case 0: ok=new CodexThing(player).SetPosition(new float[]{100.0f, 200.0f, 32.0f}); if(ok) ok=new CodexThing(player).SetOrientation(new float[]{0.0f, 0.0f, 180.0f}); if(ok) { CodexSequence.ClearChronicleFlag(262); trace("ARRIVAL london/safe"); } break;
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
 case 0: return "london/intro";
 case 1: return "london/ally";
 } return "unknown"; }
 private void resumeEvents() {
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(263)) event3();
 }
 private void dialogueCamera(int who,int target) { switch(active) {
 case 0: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 1: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 } }
 private int dialoguePartner(int index) { switch(index) { case 0: return things[0]; case 1: return things[0]; } return 0; }
 private void faceDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; new CodexThing(who).LookAtThing(target); new CodexThing(target).LookAtThing(who); }
 private void prepareDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; if(IsActorGuid(who)||IsPlayerGuid(who)) new CodexActor(who).StopActorAction(); if(IsActorGuid(target)) new CodexActor(target).StopActorAction(); faceDialogue(who,target); }
 private void schedulePoll() { KillTimer(9400); SetTimer(0.15f,9400); }
 private void dialogueMotion(int event,int line,int speaker) { switch(active) {
 case 0:
 if(event==0 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[0]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(154,false,30.0f); if(result>=0) { dialogueMotionGuids[0]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9500); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION intro/entry/0 gesture3 guid="+guid+" result="+result); } return; }
 if(event==0 && line==1) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[0]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(117,false,30.0f); if(result>=0) { dialogueMotionGuids[0]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9500); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION intro/entry/1 talk guid="+guid+" result="+result); } return; }
 break;
 } }
 private int[] dialogueMotionGuids=new int[2];
 private void finishDialogueMotion(int i) { int guid=dialogueMotionGuids[i]; dialogueMotionGuids[i]=0; KillTimer(9500+i); if(local(guid)&&IsActorGuid(guid)&&new CodexActor(guid).GetActorHealth()>0.0f) { new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,true,30.0f); new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION_REST guid="+guid); } }
 private void clearDialogueMotions(boolean rest) { for(int i=0;i<dialogueMotionGuids.length;i++) { if(rest) finishDialogueMotion(i); else { KillTimer(9500+i); dialogueMotionGuids[i]=0; } } }
 private boolean pendingDialogueEnd=false, endedAborted=false; private int endedConversation=-1, endedPlayer=0, endedResult=0;
 private boolean savedPose=false, restorePosePending=false; private int restorePoseDelay=0,restorePoseAttempts=0; private float[] savedPosition=new float[3],savedOrientation=new float[3];
 private boolean finitePose(float[] v) { if(v==null || v.length!=3) return false; for(int axis=0;axis<3;axis++) if(Float.isNaN(v[axis]) || Float.isInfinite(v[axis])) return false; return true; }
 private void savePlayerPose() { int who=localPlayer(player); float[] position=who==0?null:new CodexThing(who).GetPosition(), orientation=who==0?null:new CodexThing(who).GetOrientation(); savedPose=who!=0 && finitePose(position) && finitePose(orientation); CodexSequence.SaveBoolean(savedPose); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?position[axis]:0.0f); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?orientation[axis]:0.0f); trace("SAVE_POSE player="+who+" xyz="+(who==0?"none":positionText(who))); }
 private void readPlayerPose() { savedPose=CodexSequence.RestoreBoolean(); for(int axis=0;axis<3;axis++) savedPosition[axis]=CodexSequence.RestoreFloat(); for(int axis=0;axis<3;axis++) savedOrientation[axis]=CodexSequence.RestoreFloat(); restorePosePending=savedPose && finitePose(savedPosition) && finitePose(savedOrientation); restorePoseDelay=1; restorePoseAttempts=0; if(savedPose&&!restorePosePending) trace("RESTORE_POSE_INVALID"); }
 private boolean restorePlayerPose() {
 if(CodexSequence.GetChronicleFlag(262)) { restorePosePending=false; restoredState=false; needsArrival=true; pendingStart=true; trace("RESTORE_TRAVEL_ARRIVAL"); return true; }
 if(!restorePosePending) return true; if(restorePoseDelay>0) { restorePoseDelay--; return false; } if(++restorePoseAttempts>20) { restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE_FAILED: keeping native player position"); return true; } if(player==0) return false; CodexThing actor=new CodexThing(player); if(!actor.SetPosition(savedPosition) || !actor.SetOrientation(savedOrientation)) { trace("RESTORE_POSE_RETRY"); return false; } restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player="+player+" xyz="+positionText(player)); return true; }

}
