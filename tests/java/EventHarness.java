// Exercise stateful event routing/retries with doubles, not native geometry/NCO.
public class EventHarness {
    static int checks = 0;
    static void check(boolean value, String message) {
        checks++;
        if (!value) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        R_event_test_Scene scene = new R_event_test_Scene();
        scene.beginscene(0, 0);
        check(MockEngine.flags[2], "scene-start condition commits its flag action");
        check(MockEngine.created == 0 && MockEngine.timerSet == 1, "conditional spawn waits for player");
        MockEngine.ThingData player = new MockEngine.ThingData();
        player.template = "player"; player.position = new float[]{800, 500, 24};
        MockEngine.world.put(1, player);
        scene.timer(9001, 0, 0, 0, 0);
        int npc = CodexThing.GuidFromCastID("R_event_test_victoria");
        check(npc != 0, "gate survives flag change while waiting for player");
        scene.clicked(npc, 1, 1);
        check(MockEngine.conversation.endsWith("_intro"), "flag off selects initial event");
        scene.convended(2, false, 3);
        check(!MockEngine.flags[1] && !MockEngine.flags[3], "foreign callback does not change state");
        scene.convended(1, true, 3);
        check(!MockEngine.flags[1] && !MockEngine.flags[3], "abort does not fire end event");
        scene.clicked(npc, 1, 1); scene.convended(1, false, 999);
        check(!MockEngine.flags[1] && !MockEngine.flags[3], "unknown return does not fire end event");
        scene.clicked(npc, 1, 1); scene.convended(1, false, 3);
        check(MockEngine.flags[1] && MockEngine.flags[3], "RETURN sets flag before end-event condition");
        scene.clicked(npc, 1, 1);
        check(MockEngine.conversation.endsWith("_ally"), "flag on selects alternate event");
        scene.convended(1, false, 2);
        check(!MockEngine.flags[1], "alternate response clears alliance");
        scene.beginscene(1, 0);
        check(MockEngine.created == 1, "existing actor remains; no duplicate when start condition now false");
        MockEngine.world.clear(); MockEngine.world.put(1, player);
        new R_event_test_Scene().beginscene(1, 0);
        check(MockEngine.created == 1, "false condition does not create absent actor on a new scene start");
        MockEngine.client = true; MockEngine.flags[2] = false;
        new R_event_test_Scene().beginscene(1, 0);
        check(!MockEngine.flags[2] && MockEngine.created == 1, "client neither runs scene actions nor creates content");
        System.out.println("PASS: " + checks + " event logic checks with doubles; native engine NOT tested");
    }
}
