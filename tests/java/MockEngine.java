// Test doubles for callback logic only. NOT a replacement for native engine tests.
import java.util.*;

class MockEngine {
    static Map<Integer,ThingData> world = new HashMap<Integer,ThingData>();
    static boolean[] flags = new boolean[256];
    static List<Integer> saved = new ArrayList<Integer>();
    static int readIndex, created, captured, released, timerSet, timerKilled;
    static boolean client, failConversation, failSpawn;
    static String conversation;
    static int nextGuid = 100;
    static class ThingData {
        String template;
        float[] position, orientation;
        int location = 0;
        int actorFlags, thingFlags;
    }
    static boolean valid(int guid) { return world.containsKey(guid); }
}

class Codex {
    public static final int WORLD_CURRENT=12345678, THING_FLAG_SAVENEVER=1,
        THING_FLAG_SAVESUSPEND=2, THING_FLAG_SAVEALWAYS=8, THING_AF_AIPAUSED=4,
        THING_AF_NEUTRAL=262144, THING_AF_NOFEED=8, THING_AF_TALKTO=128,
        TEAM_PEDESTRIANS=10, CONV_XFLAG_WANTFEEDBACK=4, CONV_XFLAG_ALLOWABORT=8;
    public void BeginCutscene(int player, int flags) { }
    public void EndCutscene(int player, int flags) { }
    public void AIOff() { }
    public void AIOn() { }
    public static boolean NetIsClient() { return MockEngine.client; }
    public static boolean IsPlayerGuid(int guid) { return guid == 1 || guid == 2; }
    public static boolean IsActorGuid(int guid) { return MockEngine.valid(guid); }
    public static boolean IsPropGuid(int guid) { return false; }
    public static boolean IsItemGuid(int guid) { return false; }
    public static boolean IsWeaponGuid(int guid) { return false; }
    public static boolean IsArmorGuid(int guid) { return false; }
    public boolean CaptureThing(int guid, int capture) {
        if (!MockEngine.valid(guid)) throw new AssertionError("invalid capture");
        MockEngine.captured++;
        return true;
    }
    public boolean ExecuteConversation(int player, int capture, String id, String file, int flags) {
        MockEngine.conversation = id;
        return !MockEngine.failConversation;
    }
    public boolean SetTimer(float delay, int id) { MockEngine.timerSet++; return true; }
    public boolean KillTimer(int id) { MockEngine.timerKilled++; return true; }
}

class CodexThing extends Codex {
    int guid;
    CodexThing(int guid) { this.guid=guid; }
    public int GetLocationNum() {
        if (!MockEngine.valid(guid)) throw new AssertionError("invalid native lookup");
        return MockEngine.world.get(guid).location;
    }
    public static int GuidFromCastID(String id) {
        for (Map.Entry<Integer,MockEngine.ThingData> e:MockEngine.world.entrySet())
            if (e.getValue().template.equals(id)) return e.getKey();
        return 0;
    }
    public int ClearThingFlags(int flags) { return MockEngine.world.get(guid).thingFlags &= ~flags; }
    public int SetThingFlags(int flags) { return MockEngine.world.get(guid).thingFlags |= flags; }
    public boolean SetOrientation(float[] orientation) { MockEngine.world.get(guid).orientation=orientation.clone(); return true; }
    public float[] GetPosition() { return MockEngine.world.get(guid).position.clone(); }
    public int SpawnThingNear(String template,float distance,int flags) {
        float[] position=MockEngine.world.get(guid).position.clone();
        // A test double models adjacency; it does not reproduce native collision.
        position[0]+=48;
        return new CodexWorld(WORLD_CURRENT).CreateThing(template,position,new float[]{0,0,0});
    }
}

class CodexPlayer extends Codex {
    public static int GetMPPlayer(int index) { return MockEngine.valid(index+1) ? index+1 : 0; }
    public static int GetNumMPPlayers() { return 2; }
    public static int GetCurrentPlayer() { return MockEngine.valid(1) ? 1 : 0; }
}

class CodexActor extends CodexThing {
    CodexActor(int guid) { super(guid); }
    public int SetActorFlags(int flags) { return MockEngine.world.get(guid).actorFlags |= flags; }
    public int SetActorTeam(int team) { return team; }
}

class CodexWorld extends Codex {
    CodexWorld(int id) { if(id!=WORLD_CURRENT) throw new AssertionError("world"); }
    public int CreateThing(String template,float[] position,float[] orientation) {
        if (MockEngine.failSpawn) return 0;
        int guid=MockEngine.nextGuid++;
        MockEngine.ThingData d=new MockEngine.ThingData();
        d.template=template; d.position=position.clone(); d.orientation=orientation.clone();
        MockEngine.world.put(guid,d); MockEngine.created++;
        return guid;
    }
}

class CodexSequence extends Codex {
    public static int GetCurrentLocation() { return 0; }
    public static boolean GetChronicleFlag(int flag) { return MockEngine.flags[flag]; }
    public static boolean SetChronicleFlag(int flag) { MockEngine.flags[flag]=true; return true; }
    public static boolean ClearChronicleFlag(int flag) { MockEngine.flags[flag]=false; return true; }
    public static boolean SaveInt(int value) { MockEngine.saved.add(value); return true; }
    public static int RestoreInt() { return MockEngine.saved.get(MockEngine.readIndex++); }
}

class CodexCamera extends Codex {
    public static void SetupCutscene(int player,int actor,int unused) {
        if(!MockEngine.valid(actor)) throw new AssertionError("camera target");
    }
    public static void Release(int player) { MockEngine.released++; }
}

class CodexConsole extends Codex {
    static List<String> errors = new ArrayList<String>();
    public static void PrintError(String text) { errors.add(text); }
    public static void Print(int flags,int guid,String text) { }
}
