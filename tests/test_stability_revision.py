"""Regression scenarios for animation callbacks and save/reentry; no native claims."""
import copy
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase

from rcm.campaign_generator import runtime
from rcm.motions import constants,ensure_catalogue,parse_nms,slots,validate_motion
from rcm.paths import Workspace
from rcm.service import Backend
from test_phase9 import modern

ROOT=Path(__file__).resolve().parents[1]


class MotionCatalogueTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend=Backend(Workspace(ROOT))
        cls.data=(ROOT/'research/original/Codex.nob/Codex.class').read_bytes()

    def test_real_constants_and_model_specific_slots(self):
        modes=constants(self.data)
        self.assertEqual(modes['talk'],117);self.assertEqual(modes['gesture10'],194)
        actual=slots(self.backend.resources,'ST_Christof_MD')
        self.assertIn('Christof_talk_long.nad',[s['animation'] for s in actual])
        self.assertEqual(validate_motion('gesture10','ST_Christof_MD',self.backend.resources),194)
        with self.assertRaisesRegex(ValueError,'no disponible'):validate_motion('gesture10','LonCiv1',self.backend.resources)

    def test_invalid_classfiles_and_nms_comments_do_not_invent_modes(self):
        for data in [b'',b'wrong',self.data[:20]]:
            with self.assertRaises((ValueError,KeyError)):constants(data)
        self.assertEqual(parse_nms(b'; talk Fake.nad\ntalk Real.nad loop\nmadeup Fake.nad\nstand not_animation.txt',{'talk':117}),[dict(mode='talk',value=117,animation='Real.nad',flags=['loop'])])

    def test_owned_inheritance_override_ambiguity_and_cycle(self):
        resources=copy.deepcopy(self.backend.resources)
        resources['templates'] += [dict(id='own',project_owned=True,parent='ST_Christof_MD'),dict(id='cycle',project_owned=True,parent='cycle')]
        self.assertEqual(slots(resources,'own'),slots(resources,'ST_Christof_MD'))
        self.assertEqual(slots(resources,'cycle'),[])
        base=resources['motion_catalogue']['templates']['LonCiv1']
        resources['templates'][-2]['motions']=base
        self.assertNotIn('gesture10',[s['mode'] for s in slots(resources,'own')])
        resources['motion_catalogue']['sets'][base.casefold()]*=2
        self.assertEqual(slots(resources,'own'),[])

    def test_corrupt_cache_repaired_and_resource_change_invalidates(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
            root=Path(temp);game=root/'original';game.mkdir()
            ws=Workspace(root/'workspace',game)
            ws.write('research/original/Codex.nob/Codex.class',self.data)
            with zipfile.ZipFile(game/'Resource.nob','w') as z:z.writestr('models/actor.nms','talk real.nad loop')
            resources={'entries':[],'templates':[dict(id='first')]}
            for broken in ['{invalid','null','[]']:
                ws.write('cache/motions.json',broken)
                result=ensure_catalogue(ws,resources,game)
                self.assertEqual(result['sets']['actor.nms'][0]['slots'][0]['value'],117)
            resources['templates'].append(dict(id='second'))
            result=ensure_catalogue(ws,resources,game)
            self.assertIn('second',result['templates'])
            self.assertEqual(json.loads(ws.output('cache/motions.json').read_text())['resources_sha256'],result['resources_sha256'])

    def test_node_inheritance_line_override_and_unsupported_model_rejected(self):
        source=modern();s=source['scenes'][0];s['actors'][0]['template']='ST_Christof_MD'
        s['events']=s['events'][:3]
        c=s['conversations'][0];c.pop('prompt',None);c.pop('choices',None)
        c.update(entry='hello',nodes=[dict(id='hello',motion='gesture3',lines=[dict(text='Primera.'),dict(text='Segunda.',motion='talk')],choices=[dict(text='Salir.',result=1)])])
        result=self.backend.validate(source);self.assertTrue(result.valid,[p.message for p in result.problems])
        lines=result.project.scenes[0][1].conversations[0].nodes[0].lines
        self.assertEqual([l.motion_value for l in lines],[154,117])
        s['actors'][0]['template']='LonCiv1'
        self.assertFalse(self.backend.validate(source).valid)


def compile_scenario(out,campaign,harness,doubles_transform=None):
    name,code=runtime(campaign,*campaign.scenes[0])
    doubles=(ROOT/'tests/java/CampaignEngine.java').read_text()
    doubles=doubles.replace('class CE {','class CE {static boolean rejectPose=false;static int poseWrites=0;')
    doubles=doubles.replace('boolean SetOrientation(float[] a)','boolean SetPosition(float[] a){CE.poseWrites++;if(CE.rejectPose)return false;CE.world.get(guid).pos=a.clone();return true;} boolean SetOrientation(float[] a)')
    doubles=doubles.replace('int SetActorTeam(int t)','boolean SendActorToPos(float[] p,float speed){CE.world.get(guid).pos=p.clone();return true;} int SetActorTeam(int t)')
    doubles=doubles.replace('class Codex {','class Codex {int GetGUID(){return 5000;}')
    needed=sorted(set(re.findall(r'\bCAM_(?:SHOT|DIST|ANGLE)_[A-Z_]+\b',code)))
    doubles=doubles.replace('class Codex {','class Codex {'+''.join('static final int '+c+'='+str(200+i)+';' for i,c in enumerate(needed) if not re.search(r'\b'+c+r'\s*=',doubles)))
    doubles=doubles.replace('static void Jump(String s,int e)','static void ChangeScene(String s,String file){} static void Jump(String s,int e)')
    if doubles_transform:doubles=doubles_transform(doubles)
    out.mkdir(parents=True,exist_ok=True)
    for file,text in [(name+'.java',code),('CampaignEngine.java',doubles),('StabilityHarness.java',harness)]:
        (out/file).write_text(text,encoding='utf8')
    result=subprocess.run(['javac','-d',str(out),*[str(out/f) for f in [name+'.java','CampaignEngine.java','StabilityHarness.java']]],capture_output=True,text=True)
    if result.returncode:raise AssertionError(result.stderr)


class SaveCallbackRegressionTests(TestCase):
    @classmethod
    def setUpClass(cls):
        backend=Backend(Workspace(ROOT));source=modern();s=source['scenes'][0]
        s['actors'][0]['template']='ST_Christof_MD'
        s['paths']=[];s['events']=s['events'][:3]+[dict(id='once_reward',when='scene_start',once=True,actions=[{'reward_xp':7}])]
        c=s['conversations'][0];c.pop('prompt',None);c.pop('choices',None)
        c.update(entry='entry',nodes=[dict(id='later',lines=[dict(text='Automática.')],choices=[dict(text='Salir.',result=1)]),dict(id='entry',motion='gesture3',lines=[dict(text='Saludo.'),dict(text='Hablar.',motion='talk')],choices=[dict(text='Continuar.',goto='later')])])
        campaign=backend.validate(source).project
        arrival=campaign.reserved['arrival/london/safe']
        cls.out=ROOT/'build/tests/stability_pose'
        harness='''public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_p9_test_s0_Scene s){s.timer(9400,0,0,0,0);}
          public static void main(String[] args){
            CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
            R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);
            int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria");
            if(args[0].equals("motion")){
              s.clicked(npc,1,0);s.convreached(1,0,0,999,npc);check(CE.world.get(npc).motion==154,"entry-first NCO index uses fifth callback argument as actor");
              s.convreached(1,0,1,999,npc);check(CE.world.get(npc).motion==117,"second line overrides node motion");
              CE.world.get(npc).motion=-1;s.convreached(1,1,0,999,npc);check(CE.world.get(npc).motion==-1,"automatic node preserves native animation");
              s.convended(1,true,0);tick(s);check(CE.released>0,"abort releases dialogue camera");return;
            }
            player.pos=new float[]{999,123,32};player.orientation=new float[]{0,0,77};
            if(args[0].equals("dialogue"))s.clicked(npc,1,0);
            s.save(0);int created=CE.created,loads=CE.questLoads;
            if(args[0].equals("no_pose")){CE.save.set(0,0);CE.flags[ARRIVAL]=true;}
            if(args[0].equals("invalid"))CE.save.set(1,Float.floatToIntBits(Float.NaN));
            if(args[0].equals("travel"))CE.flags[ARRIVAL]=true;
            R_p9_test_s0_Scene r=new R_p9_test_s0_Scene();r.restore(0);
            player.pos=new float[]{-555,-222,32};player.orientation=new float[]{0,0,0};
            if(args[0].equals("late"))CE.world.remove(1);
            if(args[0].equals("reject"))CE.rejectPose=true;
            r.restored(0);r.beginscene(1,0);
            if(args[0].equals("late")){tick(r);CE.world.put(1,player);}
            for(int i=0;i<25;i++)tick(r);
            if(args[0].equals("travel")||args[0].equals("no_pose"))check(player.pos[0]==100&&player.orientation[2]==180&&!CE.flags[ARRIVAL],"explicit travel arrival overrides saved or absent pose");
            else if(args[0].equals("invalid")||args[0].equals("reject"))check(player.pos[0]==-555,"invalid or rejected pose keeps native position");
            else check(player.pos[0]==999&&player.pos[1]==123&&player.orientation[2]==77,"restore recovers actual saved position and facing");
            int writes=CE.poseWrites;tick(r);tick(r);check(CE.poseWrites==writes,"pose restoration finishes instead of retrying forever");
            check(CE.xp==7&&CE.created==created&&CE.questLoads==loads,"restore/reentry preserves one-time rewards, actors and quests");
            int calls=CE.conversationCalls;r.clicked(npc,1,0);check(CE.conversationCalls==calls+1,"restored controller accepts a fresh dialogue");
          }
        }'''.replace('ARRIVAL',str(arrival))
        compile_scenario(cls.out,campaign,harness)

    def run_case(self,name):
        result=subprocess.run(['java','-cp',str(self.out),'StabilityHarness',name],cwd=self.out,capture_output=True,text=True)
        (self.out/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_callback_node_order_and_automatic_motion(self):self.run_case('motion')
    def test_restore_after_engine_recreates_player_and_repeated_beginscene(self):self.run_case('pose')
    def test_player_not_available_until_later_timer(self):self.run_case('late')
    def test_explicit_travel_overrides_saved_pose(self):self.run_case('travel')
    def test_explicit_travel_without_saved_pose(self):self.run_case('no_pose')
    def test_nonfinite_pose_is_ignored(self):self.run_case('invalid')
    def test_rejected_pose_has_bounded_retries_and_dialogue_recovers(self):self.run_case('reject')
    def test_save_during_dialogue_does_not_restore_transient_controls(self):self.run_case('dialogue')


class CinemaRestoreRegressionTests(TestCase):
    def run_film_restore(self,movement):
        source=modern();s=source['scenes'][0]
        s['sequences']=[dict(id='film',name='Película',actor='victoria',duration=3,shot='wide',angle='high',move_path='walk',steps=[dict(at=0,actor='victoria',preset='aerial',transition=0)])]
        if not movement:s['sequences'][0].pop('move_path');s['paths']=[]
        s['events']=[s['events'][0],dict(id='film',when='timer',seconds=.3,once=True,actions=[{'play_sequence':'film'}])]
        campaign=Backend(Workspace(ROOT)).validate(source).project
        out=ROOT/'build/tests/stability_film'
        harness='''public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          public static void main(String[] args){CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
          R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);s.timer(9400,0,0,0,0);check(CE.cutscene&&CE.aiOff,"film started");
          s.save(0);R_p9_test_s0_Scene r=new R_p9_test_s0_Scene();r.restore(0);r.restored(0);r.timer(9400,0,0,0,0);
          check(!CE.cutscene&&!CE.aiOff,"restored film releases cutscene and AI");
          int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria");CE.world.get(npc).pos[0]=999;
          for(int i=0;i<25;i++)r.timer(9400,0,0,0,0);
          check(CE.world.get(npc).pos[0]==999,"saved film does not restart its transient actor path");
        }}'''
        compile_scenario(out,campaign,harness)
        result=subprocess.run(['java','-cp',str(out),'StabilityHarness'],cwd=out,capture_output=True,text=True)
        (out/'restore.log').write_text(result.stdout+result.stderr,encoding='utf8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_restore_cancels_film_patrol_and_releases_controls(self):self.run_film_restore(True)
    def test_restore_releases_film_without_actor_movement(self):self.run_film_restore(False)
