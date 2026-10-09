// Trigger polling/state tests with doubles. Does NOT simulate native collision.
public class SpatialHarness {
    static int checks=0;
    static void check(boolean value,String label) { checks++; if(!value) throw new AssertionError(label); }
    public static void main(String[] args) {
        MockEngine.ThingData player=new MockEngine.ThingData();
        player.template="player";player.position=new float[]{1000,1000,0};
        MockEngine.world.put(1,player);
        R_spatial_test_Scene scene=new R_spatial_test_Scene();
        scene.beginscene(1,0);
        check(MockEngine.created==1,"trigger actor not spawned at scene start");
        scene.timer(9002,0,0,0,0);
        check(!MockEngine.flags[2],"outside does not activate");
        player.position=new float[]{0,0,50};scene.timer(9002,0,0,0,0);
        check(MockEngine.flags[2] && MockEngine.created==2,"enter sets flag and creates actor");
        int actor=CodexThing.GuidFromCastID("R_spatial_test_actor2");
        check(actor!=0,"trigger spawn identity");
        MockEngine.flags[2]=false;scene.timer(9002,0,0,0,0);
        check(!MockEngine.flags[2] && MockEngine.created==2,"staying inside does not repeat");
        player.position=new float[]{1000,1000,0};scene.timer(9002,0,0,0,0);
        player.position=new float[]{0,0,50};scene.timer(9002,0,0,0,0);
        check(!MockEngine.flags[2],"once trigger does not repeat on reentry");
        scene.save(0);MockEngine.readIndex=0;
        R_spatial_test_Scene restored=new R_spatial_test_Scene();restored.restore(0);restored.restored(0);
        restored.timer(9002,0,0,0,0);
        check(MockEngine.created==2 && !MockEngine.flags[2],"restore preserves fired and spawned identity");
        player.position=new float[]{500,0,50};restored.timer(9002,0,0,0,0);
        check(MockEngine.flags[3],"sphere repeatable trigger fires");
        MockEngine.flags[3]=false;restored.timer(9002,0,0,0,0);check(!MockEngine.flags[3],"sphere stays does not repeat");
        player.position=new float[]{1000,0,50};restored.timer(9002,0,0,0,0);
        player.position=new float[]{500,0,50};restored.timer(9002,0,0,0,0);check(MockEngine.flags[3],"repeatable reentry fires");
        MockEngine.client=true;MockEngine.flags[3]=false;restored.timer(9002,0,0,0,0);check(!MockEngine.flags[3],"client cannot execute triggers");
        System.out.println("PASS: "+checks+" spatial runtime checks with doubles; native NOT tested");
    }
}
