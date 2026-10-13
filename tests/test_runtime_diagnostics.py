"""Diagnostics must execute in the current scheduler and Java 1.1 paths."""
from pathlib import Path
import subprocess
import unittest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime
from rcm.debugging import instrument,parse_trace
from test_release10 import blank
from rcm import recipes
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]


class RuntimeDiagnostics(unittest.TestCase):
    def test_live_flags_and_trigger_edges_are_recorded_after_deferred_answer(self):
        source,_=recipes.apply(blank(),'go_to_place','street',dict(trigger_position=[-320,-850,384],radius=110))
        source['chronicle']['id']='diag_test'
        backend=Backend(Workspace(ROOT));campaign=backend.validate(source).project
        self.assertIsNotNone(campaign)
        name,code=runtime(campaign,*campaign.scenes[0]);code=instrument(code,campaign,campaign.scenes[0][0],{'debug':True})
        # Java 1.1 File does not normalise '/' on Windows. Normalise before
        # getParent/mkdirs so diagnostics work with the installed JVM too.
        self.assertIn(".replace('/',java.io.File.separatorChar)",code)
        harness='''public class StabilityHarness {
          public static void main(String[] args){
            CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);
            R_diag_test_s0_Scene s=new R_diag_test_s0_Scene();s.beginscene(1,0);
            int npc=CodexThing.GuidFromCastID("R_diag_test_s0_actor1");
            s.clicked(npc,1,0);s.convended(1,false,1);s.timer(9400,0,0,0,0);
            p.pos=new float[]{-273.147f,-821.691f,384};s.timer(9400,0,0,0,0);
            if(!CE.cutscene)throw new AssertionError("native save position must enter the barrel area");
          }
        }'''
        out=ROOT/'build/tests/runtime_diagnostics';compile_scenario(out,campaign,harness)
        (out/(name+'.java')).write_text(code,encoding='utf8')
        run=subprocess.run(['javac','-cp',str(out),'-d',str(out),str(out/(name+'.java'))],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        log=out/'RCM/diag_test/runtime_trace.log'
        if log.exists():log.unlink()
        run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],cwd=out,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        text=log.read_text(encoding='utf8');parsed=parse_trace(text)
        self.assertTrue(parsed['flags']['flag1'],text)
        self.assertIn('DIALOGUE_END street/conv1 return=1 aborted=false',text)
        self.assertIn('TRIGGER street/trigger1 inside=true',text)
        self.assertIn('CUTSCENE_SHOT sequence1/0 Player',text)
