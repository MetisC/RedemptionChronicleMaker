public class GuidedHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_rcm_tutor_s0_Scene s){try{CE.pulse();}catch(Exception e){throw new RuntimeException(e);}}
          static void answer(R_rcm_tutor_s0_Scene s,String actor,int answer){int npc=CodexThing.GuidFromCastID("R_rcm_tutor_s0_"+actor);check(CE.valid(npc),"teacher "+actor+" available");int stops=CE.world.get(1).actionStops;s.clicked(npc,1,0);check(CE.world.get(npc).facing==1&&CE.world.get(1).facing==npc,"interlocutors face each other");check(CE.world.get(1).actionStops==stops+1,"stop action only before native conversation");s.convreached(1,0,0,0,npc);check(CE.world.get(1).actionStops==stops+1&&!CE.world.get(1).tpose&&!CE.world.get(npc).tpose,"line feedback preserves actor animation");s.convended(1,false,answer);tick(s);}
          static void close(R_rcm_tutor_s0_Scene s,int answer){s.convended(1,false,answer);tick(s);}
          public static void main(String[] args)throws Exception{
            boolean skip=args[0].equals("skip");CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);CE.syncFeedback=true;
            R_rcm_tutor_s0_Scene s=new R_rcm_tutor_s0_Scene();s.beginscene(1,0);
            s.textended(1);tick(s); // Close the native tutorial prologue.
            check(CE.quests.size()==1,"journal reveals only the first lesson");
            check(CodexThing.GuidFromCastID("R_rcm_tutor_s0_camera")==0,"future teachers are not spawned at start");
            answer(s,"mentor",skip?2:1);check(CE.quests.size()==2,"lesson 2 revealed");
            answer(s,"camera",skip?2:1);if(!skip){check(CE.conversation.endsWith("framed"),"camera 1 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_OTS_C&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("framed"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_2"),"camera 2 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_POV_A&&CodexCamera.lastDistance==Codex.CAM_DIST_EXTREMECLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_2"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_3"),"camera 3 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_POV_C&&CodexCamera.lastDistance==Codex.CAM_DIST_EXTREMECLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_3"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_4"),"camera 4 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_POV_A&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_4"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_5"),"camera 5 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_POV_C&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_5"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_6"),"camera 6 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_OTS_A&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_6"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_7"),"camera 7 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_OTS_C&&CodexCamera.lastDistance==Codex.CAM_DIST_MEDIUM,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_7"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_8"),"camera 8 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_OTS_A&&CodexCamera.lastDistance==Codex.CAM_DIST_MEDIUM,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_8"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_9"),"camera 9 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_PROFILE_A&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_9"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_10"),"camera 10 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_PROFILE_C&&CodexCamera.lastDistance==Codex.CAM_DIST_CLOSEUP,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_10"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_11"),"camera 11 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_ANGULAR_B&&CodexCamera.lastDistance==Codex.CAM_DIST_FULL,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_11"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_12"),"camera 12 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_ANGULAR_C&&CodexCamera.lastDistance==Codex.CAM_DIST_MEDIUM,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_12"),"camera waits for user");close(s,1);check(CE.conversation.endsWith("frame_13"),"camera 13 opens in order");check(CodexCamera.lastShot==Codex.CAM_SHOT_ANGULAR_C&&CodexCamera.lastDistance==Codex.CAM_DIST_FULL,"frame preset applied");tick(s);check(CE.conversation.endsWith("frame_13"),"camera waits for user");close(s,1);}
            check(CE.quests.size()==3,"lesson 3 revealed");
            if(skip)answer(s,"director",2);
            else{
              int walker=CodexThing.GuidFromCastID("R_rcm_tutor_s0_walker");CE.Thing walking=CE.world.get(walker);
              answer(s,"director",1);check(CE.cutscene&&CE.aiOff,"film owns native cutscene mode");
              int door=CodexThing.GuidFromCastID("R_rcm_tutor_s0_stage_door");CE.Thing doorState=CE.world.get(door);check(doorState.pos[2]==384,"door starts shut");
              int calls=CE.conversationCalls;s.clicked(CodexThing.GuidFromCastID("R_rcm_tutor_s0_director"),1,0);check(calls==CE.conversationCalls,"click cannot tear down film");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&doorState.pos[2]==384&&walking.pos[1]==-1018,"establishing shot waits three real seconds; walker stays behind door");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&doorState.pos[2]>580,"door opens over three seconds before actor walks");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&walking.pos[1]==-878,"nine seconds into film: walker has passed and control stays locked");
              for(int i=0;i<23;i++)tick(s);
              check(!CE.cutscene&&!CE.aiOff&&CodexCamera.shots>=4,"four shots complete after twelve real seconds and release cutscene");
              check(CE.maxPending==1,"thirteen camera conversations do not multiply native timers");
            }
            check(CE.quests.size()==4,"lesson 4 appears after film or skip");
            if(!skip)CE.consumeRewards=true;
            answer(s,"keeper",skip?2:1);
            if(!skip){check(!CE.flags[8]&&CE.world.get(1).inventory.size()==0&&CE.valid(CodexThing.GuidFromCastID("R_rcm_tutor_s0_keeper")),"consumed token cannot claim delivery or remove Elena");CE.consumeRewards=false;tick(s);}
            check(CE.flags[8]&&CE.world.get(1).inventory.size()==1,"skip also supplies required physical key");
            check(CE.quests.size()==5,"lesson 5 revealed");
            int barrel=CodexThing.GuidFromCastID("R_rcm_tutor_s0_barrel");check(CE.valid(barrel),"decorative barrel visible before layout change");
            answer(s,"gate",skip?2:1);check(CE.jump.equals("combat")&&!CE.valid(barrel),"layout request removes barrel visibly");
            check(CodexSequence.layout.equals("R_rcm_tutor_s1.nsd"),"same geometry selects target NSD explicitly");
            CE.location=1;player.location=1;R_rcm_tutor_s1_Scene combat=new R_rcm_tutor_s1_Scene();combat.beginscene(1,0);
            int guide=CodexThing.GuidFromCastID("R_rcm_tutor_s1_guide");combat.clicked(guide,1,0);combat.convended(1,false,skip?2:1);combat.timer(9400,0,0,0,0);
            if(!skip){int rat=CodexThing.GuidFromCastID("R_rcm_tutor_s1_rat");check(CE.valid(rat),"one rat spawned close to arrival");CE.world.get(rat).health=0;combat.timer(9400,0,0,0,0);}
            check(CE.jump.equals("finished")&&CE.quests.size()==7,"kill or skip reveals final lesson");
            CE.location=2;player.location=2;R_rcm_tutor_s2_Scene end=new R_rcm_tutor_s2_Scene();end.beginscene(1,0);
            end.clicked(CodexThing.GuidFromCastID("R_rcm_tutor_s2_mentor"),1,0);end.convended(1,false,skip?2:1);end.timer(9400,0,0,0,0);
            check(CE.flags[11]&&CE.complete.size()==7,"all seven objectives complete in order");
          }
        }