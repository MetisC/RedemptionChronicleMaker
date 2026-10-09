public class RCM5Actor extends Codex {
 public RCM5Actor() {
  CodexConsole.Print(0,0,"RCM5 custom actor script created");
  try { java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream("RCM/phase5_demo/custom_actor_trace.log",true)); log.println("RCM5Actor constructor, custom template script loaded by native runtime"); log.close(); } catch(Exception error) {}
 }
}
