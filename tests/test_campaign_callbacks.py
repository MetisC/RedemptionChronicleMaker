"""Exercise callbacks during ExecuteConversation, not only after its return."""
import subprocess
from unittest import TestCase
from test_campaign import ROOT,source
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.campaign_generator import runtime

class CampaignCallbackTests(TestCase):
 def test_immediate_feedback_rejection_abort_failure_and_retry(self):
  campaign=Backend(Workspace(ROOT)).validate(source()).project;name,java=runtime(campaign,*campaign.scenes[0]);out=ROOT/'build/tests/callback_java';out.mkdir(parents=True,exist_ok=True);(out/(name+'.java')).write_text(java,encoding='utf8')
  harness='''public class CallbackHarness {
   static void check(boolean b,String m){if(!b)throw new AssertionError(m);System.out.println(m);}
   public static void main(String[]args){CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);R_c4_test_s0_Scene s=new R_c4_test_s0_Scene();s.beginscene(1,0);int npc=CodexThing.GuidFromCastID("R_c4_test_s0_victoria");
    CE.syncFeedback=true;s.clicked(npc,1,0);check(CE.cameraTarget==npc,"immediate callback with zero speaker uses main actor");
    s.convended(2,false,2);check(CE.cameraTarget==npc,"unrelated player cannot release camera");
    s.convended(1,false,2);check(CE.cameraTarget==0&&!CE.flags[1],"reject restores camera ownership and does not set flag");
    int n=CE.conversationCalls;s.clicked(npc,1,0);check(CE.conversationCalls==n+1&&CE.cameraTarget==npc,"second conversation works after rejection");s.convended(1,true,3);check(CE.cameraTarget==0&&!CE.flags[1],"abort restores camera without applying choice");
    CE.syncEnd=true;n=CE.released;s.clicked(npc,1,0);check(CE.released==n+1&&CE.cameraTarget==0,"synchronous end is not lost during ExecuteConversation");
    n=CE.conversationCalls;s.clicked(npc,1,0);check(CE.conversationCalls==n+1,"synchronous end does not leave active conversation stuck");
    CE.syncEnd=false;CE.failConversation=true;s.clicked(npc,1,0);CE.failConversation=false;n=CE.conversationCalls;s.clicked(npc,1,0);check(CE.conversationCalls==n+1,"failed start rolls back busy state");s.convended(1,false,3);check(CE.flags[1],"accepted choice still applies chronicle flag");
    s.save(0);R_c4_test_s0_Scene r=new R_c4_test_s0_Scene();r.restore(0);r.restored(0);check(CodexThing.GuidFromCastID("R_c4_test_s0_victoria")==npc,"real int callback signatures preserve restored identity");
   }
  }'''
  (out/'CallbackHarness.java').write_text(harness,encoding='utf8')
  compile=subprocess.run(['javac','-d',str(out),str(ROOT/'tests/java/CampaignEngine.java'),str(out/(name+'.java')),str(out/'CallbackHarness.java')],capture_output=True,text=True);self.assertEqual(compile.returncode,0,compile.stderr)
  run=subprocess.run(['java','-cp',str(out),'CallbackHarness'],cwd=ROOT/'build/tests',capture_output=True,text=True);(out/'harness.log').write_text(run.stdout+run.stderr,encoding='utf8');self.assertEqual(run.returncode,0,run.stdout+run.stderr)
