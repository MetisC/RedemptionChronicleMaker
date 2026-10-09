public class StabilityHarness {
         static void check(boolean value,String why){if(!value)throw new AssertionError(why);System.out.println(why);}
         static void tick(R_p9_test_s0_Scene s){s.timer(9400,0,0,0,0);}
         public static void main(String[] args){CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria"),book=CodexThing.GuidFromCastID("R_p9_test_s0_book");
          if(args[0].startsWith("motion")){
           s.clicked(npc,1,0);s.convreached(1,0,0,4000,npc);
           check(CE.world.get(npc).baseMotion==33&&CE.world.get(npc).motion==194,"persistent base beneath one-shot gesture");
           check(Math.abs(CE.motionDelay-2.3f)<.001f,"motion timer uses returned milliseconds, not line duration");
           if(args[0].equals("motion_next")){s.convreached(1,1,0,4000,npc);CE.world.get(npc).motion=117;s.timer(9500,0,0,0,0);check(CE.world.get(npc).motion==117,"old completion cannot overwrite next automatic line");return;}
           if(args[0].equals("motion_abort")){s.convended(1,true,0);tick(s);check(CE.world.get(npc).motion==33,"abort restores neutral pose");return;}
           if(args[0].equals("motion_removed")){CE.world.remove(npc);s.timer(9500,0,0,0,0);return;}
           tick(s);check(CE.world.get(npc).motion==194,"regular poll does not interrupt gesture");
           CE.world.get(npc).motion=-1;check(CE.world.get(npc).baseMotion==33,"expired action retains visible base pose");
           s.timer(9500,0,0,0,0);check(CE.world.get(npc).motion==33,"completion restores action channel to rest");return;
          }
          CE.failNote=args[0].equals("failure");CE.syncNote=args[0].equals("sync");
          s.clicked(book,1,0);check(CE.noteCalls==1,"object click opens one native note");
          if(args[0].equals("failure")){CE.failNote=false;s.clicked(book,1,0);check(CE.noteCalls==2,"failed note can retry");}
          if(args[0].equals("restore")){s.save(0);R_p9_test_s0_Scene r=new R_p9_test_s0_Scene();r.restore(0);r.restored(0);r.clicked(npc,1,0);check(CE.conversationCalls==1,"restored controller releases transient note ownership");return;}
          s.clicked(npc,1,0);check(CE.conversationCalls==0,"note prevents nested dialogue");
          s.textended(999);if(!CE.syncNote){tick(s);check(CE.xp==0,"foreign close callback ignored");}
          if(!CE.syncNote){s.textended(1);s.textended(1);check(CE.xp==0,"close continuation deferred past native teardown");}
          tick(s);check(CE.xp==7,"close callback dispatches exactly once");s.textended(1);tick(s);check(CE.xp==7,"duplicate close ignored");
          s.clicked(book,1,0);check(CE.noteCalls>=2,"repeatable object reopens the note");
         }
        }