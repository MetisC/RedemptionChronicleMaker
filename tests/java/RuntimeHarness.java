// Independent scenario assertions against generated Java, not the native game.
public class RuntimeHarness {
    static int checks=0;
    static void check(boolean condition,String message) {
        checks++;
        if(!condition) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        R_east_demo_Scene scene = new R_east_demo_Scene();
        scene.beginscene(0,0);
        check(MockEngine.created==0 && MockEngine.timerSet==1,"wait until player arrives");
        MockEngine.ThingData player=new MockEngine.ThingData();
        player.template="test_player"; player.position=new float[]{800,500,24};
        MockEngine.world.put(1,player);
        scene.timer(9001,0,0,0,0);
        int npc=CodexThing.GuidFromCastID("R_east_demo_victoria");
        MockEngine.ThingData data=MockEngine.world.get(npc);
        check(npc!=0 && MockEngine.created==1,"NPC must be created once");
        check(data.position[0]==848 && data.position[1]==500 && data.position[2]==24,"NPC near actual player, not old fixed coordinates");
        check(MockEngine.timerKilled==1,"successful spawn stops retry");
        check(data.orientation[0]==0 && data.orientation[1]==0 && data.orientation[2]==180,"pitch roll yaw");
        check((data.actorFlags & 128)!=0 && MockEngine.captured==1,"talkable and captured");
        scene.beginscene(1,0);
        check(MockEngine.created==1,"repeated beginscene must not duplicate NPC");
        scene.clicked(npc,1,1);
        check(MockEngine.conversation.endsWith("_intro"),"first greeting");
        scene.convreached(1,0,0,0,0);
        scene.convended(2,false,1);
        check(!MockEngine.flags[1],"foreign callback must not mutate state");
        scene.convended(1,false,1);
        check(MockEngine.flags[1],"acceptance sets native flag");
        scene.clicked(npc,1,1);
        check(MockEngine.conversation.endsWith("_ally"),"state changes later scene behaviour");
        scene.convended(1,true,2);
        check(MockEngine.flags[1],"aborted response must not commit");
        scene.clicked(npc,1,1);
        scene.convended(1,false,2);
        check(!MockEngine.flags[1],"second choice clears flag");
        scene.clicked(npc,1,1);
        check(MockEngine.conversation.endsWith("_intro"),"cleared state changes later greeting");
        scene.convended(1,false,999);
        check(!MockEngine.flags[1],"unknown return must not mutate state");
        MockEngine.failConversation=true;
        scene.clicked(npc,1,1);
        scene.convended(1,false,1);
        check(!MockEngine.flags[1],"failed start must not commit a return");
        MockEngine.failConversation=false;
        scene.clicked(npc,1,1);
        scene.convended(1,false,1);
        scene.save(0);
        data.position[0]=1234;
        R_east_demo_Scene restored=new R_east_demo_Scene();
        restored.restore(0); restored.restored(0);
        check(MockEngine.created==1 && data.position[0]==1234,"restore retains NPC and its changed transform");
        restored.clicked(npc,1,1);
        check(MockEngine.conversation.endsWith("_ally"),"restored flag controls next dialogue");
        restored.convended(1,false,2);
        MockEngine.client=true;
        new R_east_demo_Scene().beginscene(1,0);
        check(MockEngine.created==1,"client must not create duplicate world content");
        MockEngine.client=false;
        MockEngine.world.clear(); MockEngine.failSpawn=true;
        MockEngine.world.put(1,player);
        R_east_demo_Scene failed=new R_east_demo_Scene();
        failed.beginscene(1,0);
        for(int i=0;i<121;i++) failed.timer(9001,0,0,0,0);
        check(MockEngine.created==1 && !CodexConsole.errors.isEmpty(),"failed spawn is reported safely");
        System.out.println("PASS: "+checks+" runtime logic checks with test doubles; native runtime NOT tested");
    }
}
