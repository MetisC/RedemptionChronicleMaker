public class R_rcm_tutor_s0_Scene extends Codex {
 private int[] things=new int[14];
 private boolean[] enabled=new boolean[14];
 private boolean[] createdOnce=new boolean[14];
 private boolean[] inside=new boolean[1];
 private boolean[] previous=new boolean[53];
 private int active=-1, starter=0, ticks=0, player=0; private boolean restoredState=false, transitioning=false; private int cameraTicks=0, cameraPlayer=0; private boolean pendingStart=false;
 private void trace(String s) { CodexConsole.Print(0,0,"RCM: "+s); try { java.io.File current=new java.io.File("RCM/rcm_tutor/runtime_trace.log"); new java.io.File(current.getParent()).mkdirs(); if(current.length()>1048576L) { java.io.File old=new java.io.File(current.getPath()+".1"); if(old.exists()&&!old.delete()) return; if(!current.renameTo(old)) return; } java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream(current.getPath(),true)); log.println(s); log.close(); } catch(Exception error) { CodexConsole.PrintError("RCM trace: "+error); } }
 private boolean local(int g) { return g!=0 && (IsPlayerGuid(g)||IsActorGuid(g)||IsItemGuid(g)||IsPropGuid(g)||IsWeaponGuid(g)||IsArmorGuid(g)) && new CodexThing(g).GetLocationNum()==CodexSequence.GetCurrentLocation(); }
 private int localPlayer(int g) { if(IsPlayerGuid(g)&&local(g)) return g; g=CodexPlayer.GetCurrentPlayer(); if(IsPlayerGuid(g)&&local(g)) return g; for(int i=0;i<CodexPlayer.GetNumMPPlayers();i++) { g=CodexPlayer.GetMPPlayer(i); if(IsPlayerGuid(g)&&local(g)) return g; } return 0; }
 private boolean alive(int i) { return IsActorGuid(things[i]) && local(things[i]) && new CodexActor(things[i]).GetActorHealth()>0.0f; }
 private int inventory(int owner,String template) { if(!IsActorGuid(owner)) return 0; int item=new CodexActor(owner).GetActorFirstInventoryItem(); for(int n=0;item!=0 && n<4096;n++) { if(template.equalsIgnoreCase(new CodexThing(item).GetTemplateName())) return item; item=new CodexItem(item).GetNextInventoryItem(); } return 0; }
 private boolean owns(int owner,String template) { return inventory(owner,template)!=0; }
 private boolean give(int i,int owner) { if(!IsActorGuid(owner)) return false; if(owns(owner,template(i))) return true; int item=things[i]; if(!IsItemGuid(item)&&!IsWeaponGuid(item)&&!IsArmorGuid(item)) item=new CodexThing(owner).SpawnThingNear(template(i),0.0f,0); if(item==0) return false; if(!new CodexActor(owner).AddToActorInventory(item)) { new CodexThing(item).Remove(); return false; } if(!owns(owner,template(i))) { trace("INVENTORY_NOT_RETAINED template="+template(i)+" owner="+owner); return false; } new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); trace("INVENTORY_GIVEN template="+template(i)+" owner="+owner+" item="+item); things[i]=item; createdOnce[i]=true; return true; }
 private String template(int i) { switch(i) {
 case 0: return "R_rcm_tutor_s0_mentor";
 case 1: return "R_rcm_tutor_s0_camera";
 case 2: return "R_rcm_tutor_s0_director";
 case 3: return "R_rcm_tutor_s0_keeper";
 case 4: return "R_rcm_tutor_s0_gate";
 case 5: return "R_rcm_tutor_s0_walker";
 case 6: return "R_rcm_tutor_s0_lab";
 case 7: return "R_rcm_tutor_s0_labwalker";
 case 8: return "R_rcm_tutor_s0_npc_key";
 case 9: return "R_rcm_tutor_s0_npc_book";
 case 10: return "R_rcm_tutor_s0_key";
 case 11: return "R_rcm_tutor_s0_barrel";
 case 12: return "R_rcm_tutor_s0_reward";
 case 13: return "R_rcm_tutor_s0_stage_door";
 } return ""; }
 private void spawn(int i) { if(local(things[i]) || createdOnce[i]) return; things[i]=CodexThing.GuidFromCastID(template(i)); boolean fresh=!local(things[i]); if(fresh) { switch(i) {
 case 0:

 things[0]=createAt(0,new float[]{-176.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 1:

 things[1]=createAt(1,new float[]{-176.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 2:

 things[2]=createAt(2,new float[]{-176.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 3:

 things[3]=createAt(3,new float[]{-176.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 4:

 things[4]=createAt(4,new float[]{-176.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 5:

 things[5]=createAt(5,new float[]{-342.0f, -1018.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 6:

 things[6]=createAt(6,new float[]{-342.0f, -612.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 7:

 things[7]=createAt(7,new float[]{-342.0f, -730.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 8:

 things[8]=createAt(8,new float[]{-62.0f, -768.0f, 368.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 9:

 things[9]=createAt(9,new float[]{-62.0f, -768.0f, 368.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 10:

 things[10]=createAt(10,new float[]{-176.0f, -768.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 11:

 things[11]=createAt(11,new float[]{-342.0f, -768.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 12:

 things[12]=createAt(12,new float[]{-342.0f, -800.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 case 13:

 things[13]=createAt(13,new float[]{-342.0f, -950.0f, 384.0f},new float[]{0.0f, 0.0f, 180.0f}); break;
 } } if(!local(things[i])) { if(ticks%20==0) trace("SPAWN_FAILED template="+template(i)+" guid="+things[i]+" currentLocation="+CodexSequence.GetCurrentLocation()+" playerXYZ="+positionText(player)); return; } if(fresh) { switch(i) {
 } } createdOnce[i]=true; new CodexThing(things[i]).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(things[i]).SetThingFlags(THING_FLAG_SAVEALWAYS); CaptureThing(things[i],i+1); switch(i) {
 case 0: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 case 1: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 case 2: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 case 3: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 if(!give(8,things[i])) trace("inventory failed npc_key");
 if(!give(9,things[i])) trace("inventory failed npc_book");
 break;
 case 4: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 case 5: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 break;
 case 6: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);
 break;
 case 7: new CodexActor(things[i]).SetActorTeam(TEAM_PEDESTRIANS);
 new CodexActor(things[i]).SetActorFlags(THING_AF_AIPAUSED|THING_AF_NEUTRAL);
 break;
 } trace("spawn "+template(i)+" guid="+things[i]); }
 public void beginscene(int who,int capture) { if(NetIsClient()) return; player=localPlayer(who); active=-1; starter=0; transitioning=false; if(!restoredState) { ticks=0; pendingStart=true; needsArrival=true; } poll(); }
 public void timer(int id,float a,float b,float c,float d) { if(id>=9500 && id<9500+dialogueMotionGuids.length) { if(!NetIsClient()) finishDialogueMotion(id-9500); return; } if(id==9400&&!NetIsClient()&&!transitioning) poll(); }
 private void poll() { try { pollImpl(); } catch(Throwable error) { trace("runtime exception: "+error); schedulePoll(); } } private void pollImpl() { player=localPlayer(player); if(!restorePlayerPose()) { schedulePoll(); return; } if(pendingStart && player!=0 && arrive()) { pendingStart=false; dispatch("scene_start","",0); } if(transitioning) return; finishNote(); finishDialogue(); if(transitioning) return; ticks++; pollCinema(); pollPatrols(); if(cameraTicks>0 && --cameraTicks==0) finishCameraTimer(); for(int i=0;i<enabled.length;i++) if(enabled[i]) spawn(i); if(player!=0 && notePlayer==0 && !pendingNoteEnd && active==-1 && !pendingDialogueEnd && !transitioning) { resumeEvents(); if(transitioning) return;
 boolean now0=volume(0); if(now0&&!inside[0]) dispatch("trigger_enter","station",0); if(!now0&&inside[0]) dispatch("trigger_leave","station",0); inside[0]=now0;
 boolean matched34=(CodexSequence.GetChronicleFlag(1) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && true && !CodexSequence.GetChronicleFlag(258)); if(!matched34) previous[34]=false; else if(!previous[34]) previous[34]=event34();
 boolean matched35=(CodexSequence.GetChronicleFlag(2) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259)); if(!matched35) previous[35]=false; else if(!previous[35]) previous[35]=event35();
 boolean matched36=(CodexSequence.GetChronicleFlag(3) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(259) && !CodexSequence.GetChronicleFlag(260)); if(!matched36) previous[36]=false; else if(!previous[36]) previous[36]=event36();
 boolean matched37=(CodexSequence.GetChronicleFlag(4) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(260) && !CodexSequence.GetChronicleFlag(261)); if(!matched37) previous[37]=false; else if(!previous[37]) previous[37]=event37();
 boolean matched51=(owns(player,"R_rcm_tutor_s0_reward")); if(!matched51) previous[51]=false; else if(!previous[51]) previous[51]=event51();
 } if(!transitioning) schedulePoll(); }
 private boolean volume(int which) { for(int n=-1;n<CodexPlayer.GetNumMPPlayers();n++) { int g=n==-1?player:CodexPlayer.GetMPPlayer(n); if(!IsPlayerGuid(g)||!local(g)) continue; float[] v=new CodexThing(g).GetPosition(); switch(which) {
 case 0: { double x=v[0]-(-342.0),y=v[1]-(-800.0),z=v[2]-(444.0); if(Math.abs(-1.0*x+1.2246467991473532e-16*y)<=50.0 && Math.abs(-1.2246467991473532e-16*x+-1.0*y)<=50.0 && Math.abs(z)<=60.0) return true; break; }
 } } return false; }
 private void dispatch(String kind,String target,int result) { if(transitioning) return;
 if(kind.equals("scene_start")) { if(event0() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("menu")) { if(event1() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("inventory")) { if(event2() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("camera") && result==1) { if(event3() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("camera") && result==2) { if(event4() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("cinema") && result==1) { if(event5() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("cinema") && result==2) { if(event6() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("sequence_ended") && target.equals("walk_scene")) { if(event7() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("framed") && result==1) { if(event8() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("framed") && result==2) { if(event9() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_2") && result==1) { if(event10() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_2") && result==2) { if(event11() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_3") && result==1) { if(event12() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_3") && result==2) { if(event13() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_4") && result==1) { if(event14() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_4") && result==2) { if(event15() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_5") && result==1) { if(event16() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_5") && result==2) { if(event17() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_6") && result==1) { if(event18() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_6") && result==2) { if(event19() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_7") && result==1) { if(event20() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_7") && result==2) { if(event21() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_8") && result==1) { if(event22() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_8") && result==2) { if(event23() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_9") && result==1) { if(event24() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_9") && result==2) { if(event25() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_10") && result==1) { if(event26() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_10") && result==2) { if(event27() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_11") && result==1) { if(event28() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_11") && result==2) { if(event29() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_12") && result==1) { if(event30() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_12") && result==2) { if(event31() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_13") && result==1) { if(event32() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("frame_13") && result==2) { if(event33() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("gate")) { if(event38() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==1) { if(event39() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==2) { if(event40() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==3) { if(event41() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==4) { if(event42() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==5) { if(event43() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==7) { if(event44() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==8) { if(event45() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("scene_start")) { if(event46() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("conversation_ended") && target.equals("lab") && result==11) { if(event47() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("object_clicked") && target.equals("barrel")) { if(event48() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("object_clicked") && target.equals("stage_door")) { if(event49() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("trigger_enter") && target.equals("station")) { if(event50() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 if(kind.equals("trigger_leave") && target.equals("station")) { if(event52() && (transitioning || kind.equals("actor_clicked") || kind.equals("object_clicked"))) return; }
 }
 // source: scene workshop event arrival
 private boolean event0() { if(transitioning || !(true)) return false;
 // action 1: start_quest
 if(!quest("guide",0)) return false;
 // action 2: spawn
 enabled[0]=true; spawn(0); if(!createdOnce[0]) return false;
 // action 3: spawn
 enabled[6]=true; spawn(6); if(!createdOnce[6]) return false;
 // action 4: spawn
 enabled[7]=true; spawn(7); if(!createdOnce[7]) return false;
 // action 5: start_music
 CodexSound.StartMusic("London_Hub",100);
 // action 6: start_ambient
 CodexSound.StartAmbient("amb_londonStreet",100);
 
 trace("event workshop/arrival"); return true; }
 // source: scene workshop event finish_menu
 private boolean event1() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && true && !CodexSequence.GetChronicleFlag(258))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(1);
 
 trace("event workshop/finish_menu"); return true; }
 // source: scene workshop event finish_inventory
 private boolean event2() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(260) && !CodexSequence.GetChronicleFlag(261))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(4);
 
 trace("event workshop/finish_inventory"); return true; }
 // source: scene workshop event show_frame
 private boolean event3() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(2)) return false;
 
 trace("event workshop/show_frame"); return true; }
 // source: scene workshop event skip_camera
 private boolean event4() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_camera"); return true; }
 // source: scene workshop event film
 private boolean event5() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(259) && !CodexSequence.GetChronicleFlag(260))) return false;
 // action 1: play_sequence
 if(!beginCinema(0)) return false;
 
 trace("event workshop/film"); return true; }
 // source: scene workshop event skip_film
 private boolean event6() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(259) && !CodexSequence.GetChronicleFlag(260))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(3);
 
 trace("event workshop/skip_film"); return true; }
 // source: scene workshop event film_finished
 private boolean event7() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(259) && !CodexSequence.GetChronicleFlag(260))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(3);
 
 trace("event workshop/film_finished"); return true; }
 // source: scene workshop event next_framed
 private boolean event8() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(3)) return false;
 
 trace("event workshop/next_framed"); return true; }
 // source: scene workshop event skip_framed
 private boolean event9() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_framed"); return true; }
 // source: scene workshop event next_frame_2
 private boolean event10() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(4)) return false;
 
 trace("event workshop/next_frame_2"); return true; }
 // source: scene workshop event skip_frame_2
 private boolean event11() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_2"); return true; }
 // source: scene workshop event next_frame_3
 private boolean event12() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(5)) return false;
 
 trace("event workshop/next_frame_3"); return true; }
 // source: scene workshop event skip_frame_3
 private boolean event13() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_3"); return true; }
 // source: scene workshop event next_frame_4
 private boolean event14() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(6)) return false;
 
 trace("event workshop/next_frame_4"); return true; }
 // source: scene workshop event skip_frame_4
 private boolean event15() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_4"); return true; }
 // source: scene workshop event next_frame_5
 private boolean event16() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(7)) return false;
 
 trace("event workshop/next_frame_5"); return true; }
 // source: scene workshop event skip_frame_5
 private boolean event17() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_5"); return true; }
 // source: scene workshop event next_frame_6
 private boolean event18() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(8)) return false;
 
 trace("event workshop/next_frame_6"); return true; }
 // source: scene workshop event skip_frame_6
 private boolean event19() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_6"); return true; }
 // source: scene workshop event next_frame_7
 private boolean event20() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(9)) return false;
 
 trace("event workshop/next_frame_7"); return true; }
 // source: scene workshop event skip_frame_7
 private boolean event21() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_7"); return true; }
 // source: scene workshop event next_frame_8
 private boolean event22() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(10)) return false;
 
 trace("event workshop/next_frame_8"); return true; }
 // source: scene workshop event skip_frame_8
 private boolean event23() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_8"); return true; }
 // source: scene workshop event next_frame_9
 private boolean event24() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(11)) return false;
 
 trace("event workshop/next_frame_9"); return true; }
 // source: scene workshop event skip_frame_9
 private boolean event25() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_9"); return true; }
 // source: scene workshop event next_frame_10
 private boolean event26() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(12)) return false;
 
 trace("event workshop/next_frame_10"); return true; }
 // source: scene workshop event skip_frame_10
 private boolean event27() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_10"); return true; }
 // source: scene workshop event next_frame_11
 private boolean event28() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(13)) return false;
 
 trace("event workshop/next_frame_11"); return true; }
 // source: scene workshop event skip_frame_11
 private boolean event29() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_11"); return true; }
 // source: scene workshop event next_frame_12
 private boolean event30() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: start_conversation
 if(!conversation(14)) return false;
 
 trace("event workshop/next_frame_12"); return true; }
 // source: scene workshop event skip_frame_12
 private boolean event31() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_12"); return true; }
 // source: scene workshop event next_frame_13
 private boolean event32() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/next_frame_13"); return true; }
 // source: scene workshop event skip_frame_13
 private boolean event33() { if(transitioning || !(CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(2);
 
 trace("event workshop/skip_frame_13"); return true; }
 // source: scene workshop event next_1
 private boolean event34() { if(transitioning || CodexSequence.GetChronicleFlag(265) || !((CodexSequence.GetChronicleFlag(278) || (CodexSequence.GetChronicleFlag(1) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && true && !CodexSequence.GetChronicleFlag(258))))) return false;
 CodexSequence.SetChronicleFlag(278);
 // action 1: advance_quest
 if(!CodexSequence.GetChronicleFlag(279)) { if(!quest("guide",1)) return false; CodexSequence.SetChronicleFlag(279); }
 // action 2: remove
 if(!CodexSequence.GetChronicleFlag(280)) { if(local(things[0])) new CodexThing(things[0]).Remove(); enabled[0]=false; CodexSequence.SetChronicleFlag(280); }
 // action 3: spawn
 if(!CodexSequence.GetChronicleFlag(281)) { enabled[1]=true; spawn(1); if(!createdOnce[1]) return false; CodexSequence.SetChronicleFlag(281); }
 CodexSequence.SetChronicleFlag(265);
 CodexSequence.ClearChronicleFlag(278);
 trace("event workshop/next_1"); return true; }
 // source: scene workshop event next_2
 private boolean event35() { if(transitioning || CodexSequence.GetChronicleFlag(266) || !((CodexSequence.GetChronicleFlag(282) || (CodexSequence.GetChronicleFlag(2) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(258) && !CodexSequence.GetChronicleFlag(259))))) return false;
 CodexSequence.SetChronicleFlag(282);
 // action 1: advance_quest
 if(!CodexSequence.GetChronicleFlag(283)) { if(!quest("guide",1)) return false; CodexSequence.SetChronicleFlag(283); }
 // action 2: remove
 if(!CodexSequence.GetChronicleFlag(284)) { if(local(things[1])) new CodexThing(things[1]).Remove(); enabled[1]=false; CodexSequence.SetChronicleFlag(284); }
 // action 3: spawn
 if(!CodexSequence.GetChronicleFlag(285)) { enabled[5]=true; spawn(5); if(!createdOnce[5]) return false; CodexSequence.SetChronicleFlag(285); }
 // action 4: spawn
 if(!CodexSequence.GetChronicleFlag(286)) { enabled[13]=true; spawn(13); if(!createdOnce[13]) return false; CodexSequence.SetChronicleFlag(286); }
 // action 5: spawn
 if(!CodexSequence.GetChronicleFlag(287)) { enabled[2]=true; spawn(2); if(!createdOnce[2]) return false; CodexSequence.SetChronicleFlag(287); }
 CodexSequence.SetChronicleFlag(266);
 CodexSequence.ClearChronicleFlag(282);
 trace("event workshop/next_2"); return true; }
 // source: scene workshop event next_3
 private boolean event36() { if(transitioning || CodexSequence.GetChronicleFlag(267) || !((CodexSequence.GetChronicleFlag(288) || (CodexSequence.GetChronicleFlag(3) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(259) && !CodexSequence.GetChronicleFlag(260))))) return false;
 CodexSequence.SetChronicleFlag(288);
 // action 1: advance_quest
 if(!CodexSequence.GetChronicleFlag(289)) { if(!quest("guide",1)) return false; CodexSequence.SetChronicleFlag(289); }
 // action 2: remove
 if(!CodexSequence.GetChronicleFlag(290)) { if(local(things[2])) new CodexThing(things[2]).Remove(); enabled[2]=false; CodexSequence.SetChronicleFlag(290); }
 // action 3: remove
 if(!CodexSequence.GetChronicleFlag(291)) { if(local(things[5])) new CodexThing(things[5]).Remove(); enabled[5]=false; CodexSequence.SetChronicleFlag(291); }
 // action 4: remove
 if(!CodexSequence.GetChronicleFlag(292)) { if(local(things[13])) new CodexThing(things[13]).Remove(); enabled[13]=false; CodexSequence.SetChronicleFlag(292); }
 // action 5: spawn
 if(!CodexSequence.GetChronicleFlag(293)) { enabled[3]=true; spawn(3); if(!createdOnce[3]) return false; CodexSequence.SetChronicleFlag(293); }
 CodexSequence.SetChronicleFlag(267);
 CodexSequence.ClearChronicleFlag(288);
 trace("event workshop/next_3"); return true; }
 // source: scene workshop event next_4
 private boolean event37() { if(transitioning || CodexSequence.GetChronicleFlag(268) || !((CodexSequence.GetChronicleFlag(294) || (CodexSequence.GetChronicleFlag(4) && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(260) && !CodexSequence.GetChronicleFlag(261))))) return false;
 CodexSequence.SetChronicleFlag(294);
 // action 1: give_item
 if(!CodexSequence.GetChronicleFlag(295)) { if(!give(10,player)) { trace("item reward failed"); return false; } CodexSequence.SetChronicleFlag(295); }
 // action 2: set_flag
 if(!CodexSequence.GetChronicleFlag(296)) { CodexSequence.SetChronicleFlag(8); CodexSequence.SetChronicleFlag(296); }
 // action 3: advance_quest
 if(!CodexSequence.GetChronicleFlag(297)) { if(!quest("guide",1)) return false; CodexSequence.SetChronicleFlag(297); }
 // action 4: remove
 if(!CodexSequence.GetChronicleFlag(298)) { if(local(things[3])) new CodexThing(things[3]).Remove(); enabled[3]=false; CodexSequence.SetChronicleFlag(298); }
 // action 5: spawn
 if(!CodexSequence.GetChronicleFlag(299)) { enabled[11]=true; spawn(11); if(!createdOnce[11]) return false; CodexSequence.SetChronicleFlag(299); }
 // action 6: spawn
 if(!CodexSequence.GetChronicleFlag(300)) { enabled[4]=true; spawn(4); if(!createdOnce[4]) return false; CodexSequence.SetChronicleFlag(300); }
 CodexSequence.SetChronicleFlag(268);
 CodexSequence.ClearChronicleFlag(294);
 trace("event workshop/next_4"); return true; }
 // source: scene workshop event change_layout
 private boolean event38() { if(transitioning || CodexSequence.GetChronicleFlag(269) || !((CodexSequence.GetChronicleFlag(301) || (CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257) && CodexSequence.GetChronicleFlag(261) && !CodexSequence.GetChronicleFlag(262) && owns(player, "R_rcm_tutor_s0_key"))))) return false;
 CodexSequence.SetChronicleFlag(301);
 // action 1: set_flag
 if(!CodexSequence.GetChronicleFlag(302)) { CodexSequence.SetChronicleFlag(5); CodexSequence.SetChronicleFlag(302); }
 // action 2: remove
 if(!CodexSequence.GetChronicleFlag(303)) { if(local(things[11])) new CodexThing(things[11]).Remove(); enabled[11]=false; CodexSequence.SetChronicleFlag(303); }
 // action 3: advance_quest
 if(!CodexSequence.GetChronicleFlag(304)) { if(!quest("guide",1)) return false; CodexSequence.SetChronicleFlag(304); }
 // action 4: travel
 if(!CodexSequence.GetChronicleFlag(305)) { if(!travel("combat","safe")) return false; CodexSequence.SetChronicleFlag(305); }
 CodexSequence.SetChronicleFlag(269);
 CodexSequence.ClearChronicleFlag(301);
 trace("event workshop/change_layout"); return true; }
 // source: scene workshop event lab_1
 private boolean event39() { if(transitioning || !(true)) return false;
 // action 1: start_patrol
 if(!startPatrol(1)) return false;
 
 trace("event workshop/lab_1"); return true; }
 // source: scene workshop event lab_2
 private boolean event40() { if(transitioning || !(true)) return false;
 // action 1: stop_patrol
 stopPatrol(7);
 
 trace("event workshop/lab_2"); return true; }
 // source: scene workshop event lab_3
 private boolean event41() { if(transitioning || !(true)) return false;
 // action 1: disable_ai
 if(IsActorGuid(things[7])) new CodexActor(things[7]).SetActorFlags(THING_AF_AIPAUSED);
 
 trace("event workshop/lab_3"); return true; }
 // source: scene workshop event lab_4
 private boolean event42() { if(transitioning || !(true)) return false;
 // action 1: enable_ai
 if(IsActorGuid(things[7])) new CodexActor(things[7]).ClearActorFlags(THING_AF_AIPAUSED);
 
 trace("event workshop/lab_4"); return true; }
 // source: scene workshop event lab_5
 private boolean event43() { if(transitioning || !(true)) return false;
 // action 1: play_sequence
 if(!beginCinema(1)) return false;
 
 trace("event workshop/lab_5"); return true; }
 // source: scene workshop event lab_7
 private boolean event44() { if(transitioning || !(true)) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(15);
 
 trace("event workshop/lab_7"); return true; }
 // source: scene workshop event lab_8
 private boolean event45() { if(transitioning || !(true)) return false;
 // action 1: clear_flag
 CodexSequence.ClearChronicleFlag(15);
 
 trace("event workshop/lab_8"); return true; }
 // source: scene workshop event welcome_note
 private boolean event46() { if(transitioning || CodexSequence.GetChronicleFlag(270) || !((CodexSequence.GetChronicleFlag(306) || (true)))) return false;
 CodexSequence.SetChronicleFlag(306);
 // action 1: show_note
 if(!CodexSequence.GetChronicleFlag(307)) { if(!showNote("R_rcm_tutor_s0_t46_0")) return false; CodexSequence.SetChronicleFlag(307); }
 CodexSequence.SetChronicleFlag(270);
 CodexSequence.ClearChronicleFlag(306);
 trace("event workshop/welcome_note"); return true; }
 // source: scene workshop event lab_note
 private boolean event47() { if(transitioning || !(true)) return false;
 // action 1: show_note
 if(!showNote("R_rcm_tutor_s0_t47_0")) return false;
 
 trace("event workshop/lab_note"); return true; }
 // source: scene workshop event barrel_note
 private boolean event48() { if(transitioning || !(true)) return false;
 // action 1: show_note
 if(!showNote("R_rcm_tutor_s0_t48_0")) return false;
 
 trace("event workshop/barrel_note"); return true; }
 // source: scene workshop event door_talk
 private boolean event49() { if(transitioning || !(true)) return false;
 // action 1: start_conversation
 if(!conversation(18)) return false;
 
 trace("event workshop/door_talk"); return true; }
 // source: scene workshop event reward_spawn
 private boolean event50() { if(transitioning || CodexSequence.GetChronicleFlag(271) || !((CodexSequence.GetChronicleFlag(308) || (true)))) return false;
 CodexSequence.SetChronicleFlag(308);
 // action 1: spawn
 if(!CodexSequence.GetChronicleFlag(309)) { enabled[12]=true; spawn(12); if(!createdOnce[12]) return false; CodexSequence.SetChronicleFlag(309); }
 // action 2: set_flag
 if(!CodexSequence.GetChronicleFlag(310)) { CodexSequence.SetChronicleFlag(12); CodexSequence.SetChronicleFlag(310); }
 CodexSequence.SetChronicleFlag(271);
 CodexSequence.ClearChronicleFlag(308);
 trace("event workshop/reward_spawn"); return true; }
 // source: scene workshop event pickup
 private boolean event51() { if(transitioning || CodexSequence.GetChronicleFlag(272) || !((CodexSequence.GetChronicleFlag(311) || (true)))) return false;
 CodexSequence.SetChronicleFlag(311);
 // action 1: set_flag
 if(!CodexSequence.GetChronicleFlag(312)) { CodexSequence.SetChronicleFlag(13); CodexSequence.SetChronicleFlag(312); }
 // action 2: reward_xp
 if(!CodexSequence.GetChronicleFlag(313)) { if(!IsPlayerGuid(player)) return false; new CodexPlayer(player).AwardPlayerExperience(10); CodexSequence.SetChronicleFlag(313); }
 CodexSequence.SetChronicleFlag(272);
 CodexSequence.ClearChronicleFlag(311);
 trace("event workshop/pickup"); return true; }
 // source: scene workshop event zone_left
 private boolean event52() { if(transitioning || !(true)) return false;
 // action 1: set_flag
 CodexSequence.SetChronicleFlag(14);
 
 trace("event workshop/zone_left"); return true; }
 private void releaseCamera() { stopCinema(); if(cameraPlayer!=0) CodexCamera.Release(cameraPlayer); cameraPlayer=0; cameraTicks=0; }
 private boolean conversation(int index) { if(notePlayer!=0 || pendingNoteEnd || active!=-1 || pendingDialogueEnd || cameraTicks>0 || !IsPlayerGuid(player)) return false; releaseCamera(); holdPatrols(); prepareDialogue(player,dialoguePartner(index)); boolean ok=false; int conversationPlayer=player; active=index; starter=conversationPlayer; try { switch(index) {
 case 0: if(alive(0)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_menu","R_rcm_tutor_s0_menu.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 1: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_camera","R_rcm_tutor_s0_camera.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 2: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_framed","R_rcm_tutor_s0_framed.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 3: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_2","R_rcm_tutor_s0_frame_2.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 4: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_3","R_rcm_tutor_s0_frame_3.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 5: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_4","R_rcm_tutor_s0_frame_4.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 6: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_5","R_rcm_tutor_s0_frame_5.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 7: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_6","R_rcm_tutor_s0_frame_6.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 8: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_7","R_rcm_tutor_s0_frame_7.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 9: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_8","R_rcm_tutor_s0_frame_8.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 10: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_9","R_rcm_tutor_s0_frame_9.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 11: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_10","R_rcm_tutor_s0_frame_10.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 12: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_11","R_rcm_tutor_s0_frame_11.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 13: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_12","R_rcm_tutor_s0_frame_12.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 14: if(alive(1)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_frame_13","R_rcm_tutor_s0_frame_13.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 15: if(alive(2)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_cinema","R_rcm_tutor_s0_cinema.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 16: if(alive(3)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_inventory","R_rcm_tutor_s0_inventory.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 17: if(alive(4)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_gate","R_rcm_tutor_s0_gate.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 case 18: if(alive(6)) ok=ExecuteConversation(conversationPlayer,0,"R_rcm_tutor_s0_lab","R_rcm_tutor_s0_lab.nco",CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;
 } } catch(Throwable error) { trace("conversation failed: "+error); } if(!ok && active==index && starter==conversationPlayer) { active=-1; starter=0; CodexCamera.Release(conversationPlayer); cameraPlayer=0; cameraTicks=0; resumePatrols(); trace("conversation failed to start"); } return ok; }
 public void clicked(int target,int clicker,int capture) { if(NetIsClient()||notePlayer!=0||pendingNoteEnd||active!=-1||pendingDialogueEnd||cameraTicks>0||transitioning||!IsPlayerGuid(clicker)||!local(clicker)) return; player=clicker; noteOrigin=target;
 if(target==things[0]) { dispatch("actor_clicked","mentor",0);
 if(active==-1) conversation(0);
 return; }
 if(target==things[1]) { dispatch("actor_clicked","camera",0);
 if(active==-1) conversation(1);
 return; }
 if(target==things[2]) { dispatch("actor_clicked","director",0);
 if(active==-1) conversation(15);
 return; }
 if(target==things[3]) { dispatch("actor_clicked","keeper",0);
 if(active==-1) conversation(16);
 return; }
 if(target==things[4]) { dispatch("actor_clicked","gate",0);
 if(active==-1) conversation(17);
 return; }
 if(target==things[5]) { dispatch("actor_clicked","walker",0);
 return; }
 if(target==things[6]) { dispatch("actor_clicked","lab",0);
 if(active==-1) conversation(18);
 return; }
 if(target==things[7]) { dispatch("actor_clicked","labwalker",0);
 return; }
 if(target==things[8]) { dispatch("object_clicked","npc_key",0);
 return; }
 if(target==things[9]) { dispatch("object_clicked","npc_book",0);
 return; }
 if(target==things[10]) { dispatch("object_clicked","key",0);
 return; }
 if(target==things[11]) { dispatch("object_clicked","barrel",0);
 return; }
 if(target==things[12]) { dispatch("object_clicked","reward",0);
 return; }
 if(target==things[13]) { dispatch("object_clicked","stage_door",0);
 return; }
 }
 public void convreached(int who,int event,int line,int duration,int speaker) { if(active==-1||who!=starter) return; int target=local(speaker)?speaker:0; if(target==0 || target==who) { switch(active) {
 case 0: target=things[0]; break;
 case 1: target=things[1]; break;
 case 2: target=things[1]; break;
 case 3: target=things[1]; break;
 case 4: target=things[1]; break;
 case 5: target=things[1]; break;
 case 6: target=things[1]; break;
 case 7: target=things[1]; break;
 case 8: target=things[1]; break;
 case 9: target=things[1]; break;
 case 10: target=things[1]; break;
 case 11: target=things[1]; break;
 case 12: target=things[1]; break;
 case 13: target=things[1]; break;
 case 14: target=things[1]; break;
 case 15: target=things[2]; break;
 case 16: target=things[3]; break;
 case 17: target=things[4]; break;
 case 18: target=things[6]; break;
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
 case 1: dispatch("conversation_ended","menu",result); break;
 case 2: dispatch("conversation_ended","menu",result); break;
 } break;
 case 1: switch(result) {
 case 1: dispatch("conversation_ended","camera",result); break;
 case 2: dispatch("conversation_ended","camera",result); break;
 } break;
 case 2: switch(result) {
 case 1: dispatch("conversation_ended","framed",result); break;
 case 2: dispatch("conversation_ended","framed",result); break;
 } break;
 case 3: switch(result) {
 case 1: dispatch("conversation_ended","frame_2",result); break;
 case 2: dispatch("conversation_ended","frame_2",result); break;
 } break;
 case 4: switch(result) {
 case 1: dispatch("conversation_ended","frame_3",result); break;
 case 2: dispatch("conversation_ended","frame_3",result); break;
 } break;
 case 5: switch(result) {
 case 1: dispatch("conversation_ended","frame_4",result); break;
 case 2: dispatch("conversation_ended","frame_4",result); break;
 } break;
 case 6: switch(result) {
 case 1: dispatch("conversation_ended","frame_5",result); break;
 case 2: dispatch("conversation_ended","frame_5",result); break;
 } break;
 case 7: switch(result) {
 case 1: dispatch("conversation_ended","frame_6",result); break;
 case 2: dispatch("conversation_ended","frame_6",result); break;
 } break;
 case 8: switch(result) {
 case 1: dispatch("conversation_ended","frame_7",result); break;
 case 2: dispatch("conversation_ended","frame_7",result); break;
 } break;
 case 9: switch(result) {
 case 1: dispatch("conversation_ended","frame_8",result); break;
 case 2: dispatch("conversation_ended","frame_8",result); break;
 } break;
 case 10: switch(result) {
 case 1: dispatch("conversation_ended","frame_9",result); break;
 case 2: dispatch("conversation_ended","frame_9",result); break;
 } break;
 case 11: switch(result) {
 case 1: dispatch("conversation_ended","frame_10",result); break;
 case 2: dispatch("conversation_ended","frame_10",result); break;
 } break;
 case 12: switch(result) {
 case 1: dispatch("conversation_ended","frame_11",result); break;
 case 2: dispatch("conversation_ended","frame_11",result); break;
 } break;
 case 13: switch(result) {
 case 1: dispatch("conversation_ended","frame_12",result); break;
 case 2: dispatch("conversation_ended","frame_12",result); break;
 } break;
 case 14: switch(result) {
 case 1: dispatch("conversation_ended","frame_13",result); break;
 case 2: dispatch("conversation_ended","frame_13",result); break;
 } break;
 case 15: switch(result) {
 case 1: dispatch("conversation_ended","cinema",result); break;
 case 2: dispatch("conversation_ended","cinema",result); break;
 } break;
 case 16: switch(result) {
 case 1: dispatch("conversation_ended","inventory",result); break;
 case 2: dispatch("conversation_ended","inventory",result); break;
 } break;
 case 17: switch(result) {
 case 1: dispatch("conversation_ended","gate",result); break;
 case 2: dispatch("conversation_ended","gate",result); break;
 } break;
 case 18: switch(result) {
 case 11: dispatch("conversation_ended","lab",result); break;
 case 10: dispatch("conversation_ended","lab",result); break;
 case 1: dispatch("conversation_ended","lab",result); break;
 case 2: dispatch("conversation_ended","lab",result); break;
 case 3: dispatch("conversation_ended","lab",result); break;
 case 4: dispatch("conversation_ended","lab",result); break;
 case 5: dispatch("conversation_ended","lab",result); break;
 case 6: dispatch("conversation_ended","lab",result); break;
 case 7: dispatch("conversation_ended","lab",result); break;
 case 8: dispatch("conversation_ended","lab",result); break;
 } break;
 } }
 private boolean completeEntry(String name) { int q=CodexQuest.Load(name); if(q<0) return false; new CodexQuest(q).Complete(); return true; }
 private boolean quest(String id,int action) {
 if(id.equals("guide")) {
 if(action==0) { if(CodexSequence.GetChronicleFlag(256)) return true;
 if(CodexQuest.Load("R_rcm_tutor_q0s0")<0) { trace("quest load failed"); return false; }
CodexSequence.SetChronicleFlag(256);
 return true; }
 if(action==1 && CodexSequence.GetChronicleFlag(256) && !CodexSequence.GetChronicleFlag(257)) {
 if(!CodexSequence.GetChronicleFlag(258)) { if(!completeEntry("R_rcm_tutor_q0s0")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s1")<0) return false;CodexSequence.SetChronicleFlag(258); return true; }
 else if(!CodexSequence.GetChronicleFlag(259)) { if(!completeEntry("R_rcm_tutor_q0s1")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s2")<0) return false;CodexSequence.SetChronicleFlag(259); return true; }
 else if(!CodexSequence.GetChronicleFlag(260)) { if(!completeEntry("R_rcm_tutor_q0s2")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s3")<0) return false;CodexSequence.SetChronicleFlag(260); return true; }
 else if(!CodexSequence.GetChronicleFlag(261)) { if(!completeEntry("R_rcm_tutor_q0s3")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s4")<0) return false;CodexSequence.SetChronicleFlag(261); return true; }
 else if(!CodexSequence.GetChronicleFlag(262)) { if(!completeEntry("R_rcm_tutor_q0s4")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s5")<0) return false;CodexSequence.SetChronicleFlag(262); return true; }
 else if(!CodexSequence.GetChronicleFlag(263)) { if(!completeEntry("R_rcm_tutor_q0s5")) return false;  if(CodexQuest.Load("R_rcm_tutor_q0s6")<0) return false;CodexSequence.SetChronicleFlag(263); return true; }
 else if(!CodexSequence.GetChronicleFlag(264)) { if(!completeEntry("R_rcm_tutor_q0s6")) return false; CodexSequence.SetChronicleFlag(264); return true; }
 return false; }
 if(action==2 && CodexSequence.GetChronicleFlag(257)) return true;
 if(action==2 && CodexSequence.GetChronicleFlag(256) && CodexSequence.GetChronicleFlag(258) && CodexSequence.GetChronicleFlag(259) && CodexSequence.GetChronicleFlag(260) && CodexSequence.GetChronicleFlag(261) && CodexSequence.GetChronicleFlag(262) && CodexSequence.GetChronicleFlag(263) && CodexSequence.GetChronicleFlag(264)) { CodexSequence.SetChronicleFlag(257); if(IsPlayerGuid(player)) new CodexPlayer(player).AwardPlayerExperience(20); return true; } return false; }
 return false; }
 public void save(int capture) { CodexSequence.SaveBoolean(cinema>=0); CodexSequence.SaveInt(cinemaActor); savePlayerPose(); trace("SAVE_STATE workshop"); for(int route=0;route<patrolRunning.length;route++) { CodexSequence.SaveBoolean(patrolRunning[route]); CodexSequence.SaveInt(patrolPoint[route]); CodexSequence.SaveInt(patrolWait[route]); } for(int i=0;i<things.length;i++) { CodexSequence.SaveInt(things[i]); CodexSequence.SaveBoolean(enabled[i]); CodexSequence.SaveBoolean(createdOnce[i]); } for(int i=0;i<previous.length;i++) CodexSequence.SaveBoolean(previous[i]); CodexSequence.SaveInt(ticks); }
 public void restore(int capture) { cinemaRestored=CodexSequence.RestoreBoolean(); cinemaActor=CodexSequence.RestoreInt(); cinema=-1; readPlayerPose(); trace("RESTORE_STATE workshop"); needsArrival=false; pendingStart=false; for(int route=0;route<patrolRunning.length;route++) { patrolRunning[route]=CodexSequence.RestoreBoolean(); patrolPoint[route]=CodexSequence.RestoreInt(); patrolWait[route]=CodexSequence.RestoreInt(); } for(int i=0;i<things.length;i++) { things[i]=CodexSequence.RestoreInt(); enabled[i]=CodexSequence.RestoreBoolean(); createdOnce[i]=CodexSequence.RestoreBoolean(); } for(int i=0;i<previous.length;i++) previous[i]=CodexSequence.RestoreBoolean(); ticks=CodexSequence.RestoreInt(); restoredState=true; }
 public void restored(int capture) { notePlayer=0; noteOrigin=0; pendingNoteEnd=false; clearDialogueMotions(true); if(NetIsClient()) return; active=-1; starter=0; pendingDialogueEnd=false; endedConversation=-1; endedPlayer=0; transitioning=false; releaseCamera(); for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); if(cinemaRestored) { if(player!=0) EndCutscene(player,0); AIOn(); if(cinemaActor>=0) stopPatrol(cinemaActor); cinemaActor=-1; cinemaRestored=false; trace("RESTORE_CINEMA_CANCELLED"); } if(player!=0) CodexCamera.Release(player); for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]&&!commandPatrol(route)) stopPatrol(patrolActor(route)); trace("RESTORED workshop"); poll(); }

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
 private boolean needsArrival=false; private boolean[] patrolRunning=new boolean[2];
 private String positionText(int who) { float[] p=new CodexThing(who).GetPosition(); return p==null ? "null" : p[0]+","+p[1]+","+p[2]; }
 private int[] patrolPoint=new int[2], patrolWait=new int[2];
 private boolean travel(String destination,String entry) { if(player==0 || active!=-1) return false; int flag=-1;
 if(destination.equals("workshop") && entry.equals("safe")) flag=277;
 if(destination.equals("combat") && entry.equals("safe")) flag=314;
 if(destination.equals("finished") && entry.equals("safe")) flag=325;
 if(flag<0) return false;
 if(destination.equals("combat")) { CodexSequence.ChangeScene(destination,"R_rcm_tutor_s1.nsd"); trace("LAYOUT_SELECT "+destination); }
 if(destination.equals("finished")) { CodexSequence.ChangeScene(destination,"R_rcm_tutor_s2.nsd"); trace("LAYOUT_SELECT "+destination); }
 CodexSequence.ClearChronicleFlag(277);
 CodexSequence.ClearChronicleFlag(314);
 CodexSequence.ClearChronicleFlag(325);
 CodexSequence.SetChronicleFlag(flag); trace("TRAVEL "+destination+" entry="+entry); releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump(destination,0); return true; }
 private boolean arrive() { if(!needsArrival || player==0) return !needsArrival; int entry=-1;
 if(CodexSequence.GetChronicleFlag(277)) entry=0;
 if(entry<0) entry=0; trace("ARRIVAL_BEFORE player="+player+" location="+CodexSequence.GetCurrentLocation()+" xyz="+positionText(player)); boolean ok=true; switch(entry) {
 case 0: ok=new CodexThing(player).SetPosition(new float[]{-176.0f, -768.0f, 384.0f}); if(ok) ok=new CodexThing(player).SetOrientation(new float[]{0.0f, 0.0f, 0.0f}); if(ok) { CodexSequence.ClearChronicleFlag(277); trace("ARRIVAL workshop/safe"); } break;
 } if(!ok) { trace("ARRIVAL_FAILED: engine rejected position/orientation"); return false; } if(entry>=0) CodexCamera.Release(player); trace("ARRIVAL_AFTER xyz="+positionText(player)); needsArrival=false; return true; }
 private int patrolActor(int route) { switch(route) {
 case 0: return 5;
 case 1: return 7;
 } return -1; }
 private float[] patrolTarget(int route) { switch(route) {
 case 0: switch(patrolPoint[0]) {
 case 0: return new float[]{-342.0f, -1018.0f, 384.0f};
 case 1: return new float[]{-342.0f, -878.0f, 384.0f};
 } break;
 case 1: switch(patrolPoint[1]) {
 case 0: return new float[]{-342.0f, -730.0f, 384.0f};
 case 1: return new float[]{-342.0f, -800.0f, 384.0f};
 } break;
 } return null; }
 private float patrolSpeed(int route) { switch(route) {
 case 0: return 60.0f;
 case 1: return 60.0f;
 } return 90.0f; }
 private boolean commandPatrol(int route) { int a=patrolActor(route); float[] target=patrolTarget(route); if(a<0 || !alive(a) || target==null) return false; float[] pos=new CodexThing(things[a]).GetPosition(); if(pos!=null) { double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; switch(route) {
 case 0: tolerance=24.0; break;
 case 1: tolerance=24.0; break;
 } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) return true; } new CodexActor(things[a]).ClearActorFlags(THING_AF_AIPAUSED); boolean ok=new CodexActor(things[a]).SendActorToPos(target,patrolSpeed(route)); if(!ok) trace("PATH_FAILED route="+route+" actor="+things[a]); return ok; }
 private boolean startPatrol(int route) { if(patrolRunning[route]) return true; patrolPoint[route]=0; patrolWait[route]=0; patrolRunning[route]=commandPatrol(route); return patrolRunning[route]; }
 private void stopPatrol(int actor) { for(int route=0;route<patrolRunning.length;route++) if(patrolActor(route)==actor) { patrolRunning[route]=false; if(alive(actor)) { CodexActor stopped=new CodexActor(things[actor]); stopped.StopActorAction(); stopped.SetActorFlags(THING_AF_AIPAUSED); } } }
 private void holdPatrols() { for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route] && alive(patrolActor(route))) { new CodexActor(things[patrolActor(route)]).StopActorAction(); new CodexActor(things[patrolActor(route)]).SetActorFlags(THING_AF_AIPAUSED); } }
 private void resumePatrols() { if(transitioning) return; for(int route=0;route<patrolRunning.length;route++) if(patrolRunning[route]) commandPatrol(route); }
 private void pollPatrols() { if(active!=-1 || pendingDialogueEnd || (cameraTicks>0 && cinema<0)) return; for(int route=0;route<patrolRunning.length;route++) { if(!patrolRunning[route]) continue; int a=patrolActor(route); if(!alive(a)) { patrolRunning[route]=false; continue; } float[] target=patrolTarget(route), pos=new CodexThing(things[a]).GetPosition(); if(target==null || pos==null) { stopPatrol(a); continue; } double dx=pos[0]-target[0],dy=pos[1]-target[1],dz=pos[2]-target[2]; double tolerance=24.0; int count=0; boolean loop=false; switch(route) {
 case 0: tolerance=24.0; count=2; loop=false; break;
 case 1: tolerance=24.0; count=2; loop=true; break;
 } if(dx*dx+dy*dy+dz*dz<=tolerance*tolerance) { patrolWait[route]=0; patrolPoint[route]++; if(patrolPoint[route]>=count) { if(loop) patrolPoint[route]=0; else { stopPatrol(a); trace("PATH_COMPLETE route="+route); continue; } } if(!commandPatrol(route)) stopPatrol(a); } else if(++patrolWait[route]>400) { trace("PATH_TIMEOUT route="+route); stopPatrol(a); } } }
 private String conversationID(int index) { switch(index) {
 case 0: return "workshop/menu";
 case 1: return "workshop/camera";
 case 2: return "workshop/framed";
 case 3: return "workshop/frame_2";
 case 4: return "workshop/frame_3";
 case 5: return "workshop/frame_4";
 case 6: return "workshop/frame_5";
 case 7: return "workshop/frame_6";
 case 8: return "workshop/frame_7";
 case 9: return "workshop/frame_8";
 case 10: return "workshop/frame_9";
 case 11: return "workshop/frame_10";
 case 12: return "workshop/frame_11";
 case 13: return "workshop/frame_12";
 case 14: return "workshop/frame_13";
 case 15: return "workshop/cinema";
 case 16: return "workshop/inventory";
 case 17: return "workshop/gate";
 case 18: return "workshop/lab";
 } return "unknown"; }
 private void resumeEvents() {
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(278)) event34();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(282)) event35();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(288)) event36();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(294)) event37();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(301)) event38();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(306)) event46();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(308)) event50();
 if(!transitioning && active==-1 && CodexSequence.GetChronicleFlag(311)) event51();
 }
 private void dialogueCamera(int who,int target) { switch(active) {
 case 0: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 1: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 2: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 3: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_POV_A,CAM_ANGLE_MEDIUM,CAM_DIST_EXTREMECLOSEUP,0,0.3f); return;
 case 4: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_POV_C,CAM_ANGLE_MEDIUM,CAM_DIST_EXTREMECLOSEUP,0,0.3f); return;
 case 5: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_POV_A,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 6: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_POV_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 7: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_A,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 8: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_MEDIUM,0,0.3f); return;
 case 9: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_A,CAM_ANGLE_MEDIUM,CAM_DIST_MEDIUM,0,0.3f); return;
 case 10: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_PROFILE_A,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 11: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_PROFILE_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 12: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_ANGULAR_B,CAM_ANGLE_MEDIUM,CAM_DIST_FULL,0,0.3f); return;
 case 13: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_ANGULAR_C,CAM_ANGLE_MEDIUM,CAM_DIST_MEDIUM,0,0.3f); return;
 case 14: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_ANGULAR_C,CAM_ANGLE_MEDIUM,CAM_DIST_FULL,0,0.3f); return;
 case 15: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 16: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 17: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 case 18: CodexCamera.SetupCutscene(who,target,who); CodexCamera.SetShot(who,CAM_SHOT_OTS_C,CAM_ANGLE_MEDIUM,CAM_DIST_CLOSEUP,0,0.3f); return;
 } }
 private int dialoguePartner(int index) { switch(index) { case 0: return things[0]; case 1: return things[1]; case 2: return things[1]; case 3: return things[1]; case 4: return things[1]; case 5: return things[1]; case 6: return things[1]; case 7: return things[1]; case 8: return things[1]; case 9: return things[1]; case 10: return things[1]; case 11: return things[1]; case 12: return things[1]; case 13: return things[1]; case 14: return things[1]; case 15: return things[2]; case 16: return things[3]; case 17: return things[4]; case 18: return things[6]; } return 0; }
 private void faceDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; new CodexThing(who).LookAtThing(target); new CodexThing(target).LookAtThing(who); }
 private void prepareDialogue(int who,int target) { if(who==target || !local(who) || !local(target)) return; if(IsActorGuid(who)||IsPlayerGuid(who)) new CodexActor(who).StopActorAction(); if(IsActorGuid(target)) new CodexActor(target).StopActorAction(); faceDialogue(who,target); }
 private void schedulePoll() { KillTimer(9400); SetTimer(0.15f,9400); }
 private void dialogueMotion(int event,int line,int speaker) { switch(active) {
 case 18:
 if(event==0 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(194,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/opening/0 gesture10 guid="+guid+" result="+result); } return; }
 if(event==1 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(191,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/motion/0 gesture7 guid="+guid+" result="+result); } return; }
 if(event==4 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(33,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/stand/0 stand guid="+guid+" result="+result); } return; }
 if(event==5 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(49,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/idle/0 idle guid="+guid+" result="+result); } return; }
 if(event==6 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(117,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/talk/0 talk guid="+guid+" result="+result); } return; }
 if(event==7 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(118,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/listen/0 listen guid="+guid+" result="+result); } return; }
 if(event==8 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(154,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/gesture3/0 gesture3 guid="+guid+" result="+result); } return; }
 if(event==9 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(191,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/gesture7/0 gesture7 guid="+guid+" result="+result); } return; }
 if(event==10 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(192,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/gesture8/0 gesture8 guid="+guid+" result="+result); } return; }
 if(event==11 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(193,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/gesture9/0 gesture9 guid="+guid+" result="+result); } return; }
 if(event==12 && line==0) { int guid=local(speaker)&&IsActorGuid(speaker)?speaker:things[6]; if(local(guid)&&IsActorGuid(guid)) { CodexThing actor=new CodexThing(guid); actor.PlayMotionSetMode(MOTION_STAND,true,30.0f); int result=actor.PlayMotionSetMode(194,false,30.0f); if(result>=0) { dialogueMotionGuids[6]=guid; SetTimer(Math.max(0.01f,result/1000.0f),9506); } else actor.PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION lab/gesture10/0 gesture10 guid="+guid+" result="+result); } return; }
 break;
 } }
 private int[] dialogueMotionGuids=new int[14];
 private void finishDialogueMotion(int i) { int guid=dialogueMotionGuids[i]; dialogueMotionGuids[i]=0; KillTimer(9500+i); if(local(guid)&&IsActorGuid(guid)&&new CodexActor(guid).GetActorHealth()>0.0f) { new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,true,30.0f); new CodexThing(guid).PlayMotionSetMode(MOTION_STAND,false,30.0f); trace("DIALOGUE_MOTION_REST guid="+guid); } }
 private void clearDialogueMotions(boolean rest) { for(int i=0;i<dialogueMotionGuids.length;i++) { if(rest) finishDialogueMotion(i); else { KillTimer(9500+i); dialogueMotionGuids[i]=0; } } }
 private boolean pendingDialogueEnd=false, endedAborted=false; private int endedConversation=-1, endedPlayer=0, endedResult=0;
 private boolean savedPose=false, restorePosePending=false; private int restorePoseDelay=0,restorePoseAttempts=0; private float[] savedPosition=new float[3],savedOrientation=new float[3];
 private boolean finitePose(float[] v) { if(v==null || v.length!=3) return false; for(int axis=0;axis<3;axis++) if(Float.isNaN(v[axis]) || Float.isInfinite(v[axis])) return false; return true; }
 private void savePlayerPose() { int who=localPlayer(player); float[] position=who==0?null:new CodexThing(who).GetPosition(), orientation=who==0?null:new CodexThing(who).GetOrientation(); savedPose=who!=0 && finitePose(position) && finitePose(orientation); CodexSequence.SaveBoolean(savedPose); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?position[axis]:0.0f); for(int axis=0;axis<3;axis++) CodexSequence.SaveFloat(savedPose?orientation[axis]:0.0f); trace("SAVE_POSE player="+who+" xyz="+(who==0?"none":positionText(who))); }
 private void readPlayerPose() { savedPose=CodexSequence.RestoreBoolean(); for(int axis=0;axis<3;axis++) savedPosition[axis]=CodexSequence.RestoreFloat(); for(int axis=0;axis<3;axis++) savedOrientation[axis]=CodexSequence.RestoreFloat(); restorePosePending=savedPose && finitePose(savedPosition) && finitePose(savedOrientation); restorePoseDelay=1; restorePoseAttempts=0; if(savedPose&&!restorePosePending) trace("RESTORE_POSE_INVALID"); }
 private boolean restorePlayerPose() {
 if(CodexSequence.GetChronicleFlag(277)) { restorePosePending=false; restoredState=false; needsArrival=true; pendingStart=true; trace("RESTORE_TRAVEL_ARRIVAL"); return true; }
 if(!restorePosePending) return true; if(restorePoseDelay>0) { restorePoseDelay--; return false; } if(++restorePoseAttempts>20) { restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE_FAILED: keeping native player position"); return true; } if(player==0) return false; CodexThing actor=new CodexThing(player); if(!actor.SetPosition(savedPosition) || !actor.SetOrientation(savedOrientation)) { trace("RESTORE_POSE_RETRY"); return false; } restorePosePending=false; needsArrival=false; pendingStart=false; trace("RESTORE_POSE player="+player+" xyz="+positionText(player)); return true; }


 private int cinema=-1, cinemaAge=0, cinemaStep=-1, cinemaActor=-1; private boolean cinemaMoving=false, cinemaRestored=false;
 private boolean beginCinema(int index) { if(active!=-1 || player==0) return false; releaseCamera(); BeginCutscene(player,0); AIOff(); cinema=index; cinemaAge=0; cinemaStep=-1; cameraPlayer=player; cameraTicks=0; switch(index) {
 case 0: if(!alive(5)) { stopCinema(); return false; }
 spawn(13); if(!local(things[13])) { stopCinema(); return false; }
 CodexCamera.SetupCutscene(player,things[5],player);
 cameraTicks=81; pollCinema(); cinemaAge=0; return true;
 case 1: if(!alive(6)) { stopCinema(); return false; }
 if(!CodexCamera.PlayPath(player,GetGUID(),"EASTOttoVan.ncp",1.0f)) { stopCinema(); return false; }
 cameraTicks=55; pollCinema(); cinemaAge=0; return true;
 } return false; }
 private void stopCinema() { if(cinema<0) return; int client=cameraPlayer; int actor=cinemaActor; cinema=-1; cinemaAge=0; cinemaStep=-1; cinemaActor=-1; cinemaMoving=false; if(actor>=0) stopPatrol(actor); if(client!=0) EndCutscene(client,0); AIOn(); trace("CUTSCENE_END"); }
 private void pollCinema() { if(cinema<0) return; switch(cinema) {
 case 0:
 if(cinemaAge>=20) { if(!local(things[13])) { trace("CUTSCENE_PROP_MISSING"); releaseCamera(); return; } float fraction=Math.min(1.0f,Math.max(0.0f,(cinemaAge*0.15f-3.0f)/3.0f)); float[] position=new float[]{-342.0f, -950.0f, 384.0f}, delta=new float[]{0.0f, 0.0f, 208.0f}; for(int axis=0;axis<3;axis++) position[axis]+=delta[axis]*fraction; if(!new CodexThing(things[13]).SetPosition(position)) { trace("CUTSCENE_PROP_REJECTED"); releaseCamera(); return; } }
 if(!cinemaMoving && cinemaAge>=40) { if(!startPatrol(0)) { trace("CUTSCENE_PATH_FAILED"); releaseCamera(); return; } cinemaActor=patrolActor(0); cinemaMoving=true; }
 if(cinemaStep<0 && cinemaAge>=0) { if(!alive(5) || !local(things[13])) { releaseCamera(); return; } CodexCamera.SetupCutscene(cameraPlayer,things[13],things[5]); CodexCamera.SetShot(cameraPlayer,CAM_SHOT_ANGULAR_B,CAM_ANGLE_HIGH,CAM_DIST_LONG,0,0.0f); cinemaStep=0; trace("CUTSCENE_SHOT walk_scene/0"); }
 if(cinemaStep<1 && cinemaAge>=20) { if(!alive(5) || !local(things[13])) { releaseCamera(); return; } CodexCamera.SetupCutscene(cameraPlayer,things[13],things[5]); CodexCamera.SetShot(cameraPlayer,CAM_SHOT_ANGULAR_C,CAM_ANGLE_MEDIUM,CAM_DIST_FULL,0,0.7f); cinemaStep=1; trace("CUTSCENE_SHOT walk_scene/1"); }
 if(cinemaStep<2 && cinemaAge>=40) { if(!alive(5) || !local(things[5])) { releaseCamera(); return; } CodexCamera.SetupCutscene(cameraPlayer,things[5],player); CodexCamera.SetShot(cameraPlayer,CAM_SHOT_ANGULAR_C,CAM_ANGLE_MEDIUM,CAM_DIST_FULL,0,0.6f); cinemaStep=2; trace("CUTSCENE_SHOT walk_scene/2"); }
 if(cinemaStep<3 && cinemaAge>=60) { if(!alive(2) || !local(things[2])) { releaseCamera(); return; } CodexCamera.SetupCutscene(cameraPlayer,things[2],player); CodexCamera.SetShot(cameraPlayer,CAM_SHOT_ANGULAR_B,CAM_ANGLE_MEDIUM,CAM_DIST_FULL,0,0.5f); cinemaStep=3; trace("CUTSCENE_SHOT walk_scene/3"); }
 break;
 case 1:
 break;
 } cinemaAge++; }
 private void finishCameraTimer() { int completed=cinema; releaseCamera(); switch(completed) {
 case 0: trace("CUTSCENE_COMPLETE walk_scene"); dispatch("sequence_ended","walk_scene",0); break;
 case 1: trace("CUTSCENE_COMPLETE original_path"); dispatch("sequence_ended","original_path",0); break;
 } }

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

}
