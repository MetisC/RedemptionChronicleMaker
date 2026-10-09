"""Native callback ordering simulated in Java; does not certify the game UI."""
from pathlib import Path
import subprocess
from unittest import TestCase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime
from test_phase9 import modern

ROOT=Path(__file__).resolve().parents[1]

class DialogueLifecycle(TestCase):
    def test_chained_native_dialogues_release_after_callback_abort_failure_and_sync_end(self):
        data=modern();scene=data['scenes'][0];scene['paths']=[];scene['actors'][0]['conversation']={'default':'intro'}
        scene['conversations']=[dict(id='intro',speaker='victoria',prompt='Menú',camera='native',choices=[dict(text='Aceptar',result=1),dict(text='Ayuda',result=2),dict(text='Cerrar',result=3)]),dict(id='ally',speaker='victoria',prompt='Dónde se edita',camera='native',choices=[dict(text='Volver',result=1),dict(text='Cerrar',result=2)])]
        scene['events']=[dict(id='arrival',when='scene_start',actions=[{'start_quest':'mission'},{'spawn':'victoria'}]),dict(id='help',when='conversation_ended',conversation='intro',result=2,actions=[{'start_conversation':'ally'}]),dict(id='back',when='conversation_ended',conversation='ally',result=1,actions=[{'start_conversation':'intro'}]),dict(id='accept',when='conversation_ended',conversation='intro',result=1,once=True,actions=[{'advance_quest':'mission'},{'reward_xp':10}])]
        result=Backend(Workspace(ROOT)).validate(data);self.assertTrue(result.valid,[x.message for x in result.problems])
        name,java=runtime(result.project,*result.project.scenes[0])
        out=ROOT/'build/tests/dialogue_lifecycle';out.mkdir(parents=True,exist_ok=True)
        (out/(name+'.java')).write_text(java,encoding='utf8')
        doubles=(ROOT/'tests/java/CampaignEngine.java').read_text()
        doubles=doubles.replace('static boolean valid(int g)','static boolean blocked=false,hud=true; static boolean valid(int g)')
        doubles=doubles.replace('boolean SetOrientation(float[] a)', 'boolean SetPosition(float[] a){CE.world.get(guid).pos=a.clone();return true;} boolean SetOrientation(float[] a)')
        doubles=doubles.replace('int SetActorTeam(int t)', 'void StopActorMotion(){} boolean SendActorToPos(float[] p,float v){return true;} int SetActorTeam(int t)')
        doubles=doubles.replace('CE.cameraTarget=b;', 'CE.cameraTarget=b;CE.blocked=true;CE.hud=false;')
        doubles=doubles.replace('CE.released++;CE.cameraTarget=0;', 'CE.released++;CE.cameraTarget=0;CE.blocked=false;CE.hud=true;')
        (out/'CampaignEngine.java').write_text(doubles)
        harness='''public class DialogueLifecycleHarness {
         static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
         static void nativeEnd(R_p9_test_s0_Scene scene,boolean aborted,int result){
          int calls=CE.conversationCalls,releases=CE.released;
          scene.convended(1,aborted,result);
          check(CE.conversationCalls==calls&&CE.released==releases,"callback does not start another dialogue or release engine-owned UI");
          // Native cleanup occurs after the callback. Any nested conversation
          // would inherit this cleanup; the following timer must take ownership.
          CE.cameraTarget=0;CE.blocked=false;CE.hud=false;
         }
         public static void main(String[] args){CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);
          R_p9_test_s0_Scene scene=new R_p9_test_s0_Scene();scene.beginscene(1,0);
          check(CE.quests.size()==1,"only current objective appears in initial journal");
          int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria");CE.syncFeedback=true;
          scene.clicked(npc,1,0);check(CE.blocked&&!CE.hud,"automatic camera still acquires conversation controls");
          scene.convended(99,false,2);check(CE.conversationCalls==1&&CE.blocked,"wrong player cannot close dialogue");
          nativeEnd(scene,false,2);scene.convended(1,false,2);scene.clicked(npc,1,0);
          check(CE.conversationCalls==1,"duplicate close and clicking before cleanup cannot restart dialogue");
          scene.timer(9400,0,0,0,0);check(CE.conversationCalls==2&&CE.conversation.endsWith("ally")&&CE.blocked,"help starts after native cleanup");
          nativeEnd(scene,false,1);scene.timer(9400,0,0,0,0);
          check(CE.conversationCalls==3&&CE.conversation.endsWith("intro")&&CE.blocked,"Volver returns to menu with controls owned");
          nativeEnd(scene,false,3);scene.timer(9400,0,0,0,0);check(!CE.blocked&&CE.hud,"close returns gameplay HUD and controls after cleanup");
          scene.clicked(npc,1,0);nativeEnd(scene,true,1);scene.timer(9400,0,0,0,0);
          check(!CE.blocked&&CE.hud&&CE.xp==0,"abort releases controls and suppresses result actions");
          CE.failConversation=true;scene.clicked(npc,1,0);check(!CE.blocked&&CE.hud,"failed conversation leaves no owned controls");CE.failConversation=false;
          CE.syncEnd=true;int calls=CE.conversationCalls;scene.clicked(npc,1,0);
          check(CE.conversationCalls==calls+1,"synchronous end does not recursively execute help");
          scene.timer(9400,0,0,0,0);check(CE.conversationCalls==calls+2,"synchronous end followup deferred to timer");
          scene.timer(9400,0,0,0,0);check(!CE.blocked&&CE.hud,"synchronous followup close releases controls");CE.syncEnd=false;
          scene.clicked(npc,1,0);nativeEnd(scene,false,1);scene.timer(9400,0,0,0,0);
          check(CE.xp==10&&CE.quests.size()==2,"accepted result reveals next objective and grants one reward");
          scene.clicked(npc,1,0);nativeEnd(scene,false,1);scene.timer(9400,0,0,0,0);
          check(CE.xp==10&&CE.quests.size()==2,"repeated result does not duplicate reward or objectives");
          scene.clicked(npc,1,0);nativeEnd(scene,false,2);scene.save(0);
          R_p9_test_s0_Scene restored=new R_p9_test_s0_Scene();restored.restore(0);restored.restored(0);
          check(!CE.blocked&&CE.hud,"restore discards transient pending dialogue and releases controls");
         }}'''
        (out/'DialogueLifecycleHarness.java').write_text(harness,encoding='utf8')
        files=[out/'CampaignEngine.java',out/(name+'.java'),out/'DialogueLifecycleHarness.java']
        run=subprocess.run(['javac','-d',str(out),*[str(f) for f in files]],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        run=subprocess.run(['java','-cp',str(out),'DialogueLifecycleHarness'],cwd=ROOT/'build/tests',capture_output=True,text=True)
        (out/'harness.log').write_text(run.stdout+run.stderr,encoding='utf8');self.assertEqual(run.returncode,0,run.stdout+run.stderr)
