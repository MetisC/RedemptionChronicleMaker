public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_p9_test_s0_Scene s){s.timer(9400,0,0,0,0);}
          public static void main(String[] args){
            CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
            R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);
            int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria");
            if(args[0].equals("motion")){
              s.clicked(npc,1,0);s.convreached(1,0,0,999,npc);check(CE.world.get(npc).motion==154,"entry-first NCO index uses fifth callback argument as actor");
              s.convreached(1,0,1,999,npc);check(CE.world.get(npc).motion==117,"second line overrides node motion");
              CE.world.get(npc).motion=-1;s.convreached(1,1,0,999,npc);check(CE.world.get(npc).motion==-1,"automatic node preserves native animation");
              s.convended(1,true,0);tick(s);check(CE.released>0,"abort releases dialogue camera");return;
            }
            player.pos=new float[]{999,123,32};player.orientation=new float[]{0,0,77};
            if(args[0].equals("dialogue"))s.clicked(npc,1,0);
            s.save(0);int created=CE.created,loads=CE.questLoads;
            if(args[0].equals("no_pose")){CE.save.set(0,0);CE.flags[262]=true;}
            if(args[0].equals("invalid"))CE.save.set(1,Float.floatToIntBits(Float.NaN));
            if(args[0].equals("travel"))CE.flags[262]=true;
            R_p9_test_s0_Scene r=new R_p9_test_s0_Scene();r.restore(0);
            player.pos=new float[]{-555,-222,32};player.orientation=new float[]{0,0,0};
            if(args[0].equals("late"))CE.world.remove(1);
            if(args[0].equals("reject"))CE.rejectPose=true;
            r.restored(0);r.beginscene(1,0);
            if(args[0].equals("late")){tick(r);CE.world.put(1,player);}
            for(int i=0;i<25;i++)tick(r);
            if(args[0].equals("travel")||args[0].equals("no_pose"))check(player.pos[0]==100&&player.orientation[2]==180&&!CE.flags[262],"explicit travel arrival overrides saved or absent pose");
            else if(args[0].equals("invalid")||args[0].equals("reject"))check(player.pos[0]==-555,"invalid or rejected pose keeps native position");
            else check(player.pos[0]==999&&player.pos[1]==123&&player.orientation[2]==77,"restore recovers actual saved position and facing");
            int writes=CE.poseWrites;tick(r);tick(r);check(CE.poseWrites==writes,"pose restoration finishes instead of retrying forever");
            check(CE.xp==7&&CE.created==created&&CE.questLoads==loads,"restore/reentry preserves one-time rewards, actors and quests");
            int calls=CE.conversationCalls;r.clicked(npc,1,0);check(CE.conversationCalls==calls+1,"restored controller accepts a fresh dialogue");
          }
        }