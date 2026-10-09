public class CompilerProbe extends Codex {
 public void beginscene(int player, int captureID) {
  int guid = new CodexWorld(WORLD_CURRENT).CreateThing("businessWoman", new float[]{1016.0f,-54.0f,0.0f}, new float[]{0.0f,0.0f,180.0f});
  CaptureThing(guid, 1);
 }
}
