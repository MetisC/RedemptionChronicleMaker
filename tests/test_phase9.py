"""Phase 9: arrivals, partial-failure idempotence and persistence, not native QA."""
from pathlib import Path
import sys,subprocess,tempfile,json,hashlib
from unittest import TestCase
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.campaign_generator import runtime
from rcm.campaign_document import CampaignDocument
from rcm.campaign_relations import graph
from rcm.deployment import deploy
from rcm.story_graph import scene_reachability
from rcm.debugging import parse_trace
from test_campaign import source

def modern():
    data=source();data['chronicle']['id']='p9_test';data['project_format']=9
    for s in data['scenes']:
        s['entries']=[dict(id='safe',name='Llegada segura',transform=dict(position=[100,200,32],orientation=[0,0,180]))]
        s['default_entry']='safe';s['waypoints']=[];s['paths']=[]
    s=data['scenes'][0]
    s['waypoints']=[dict(id='p'+str(i),name='Punto '+str(i),transform=dict(position=[100+i*50,200,32],orientation=[0,0,0])) for i in range(2)]
    s['paths']=[dict(id='walk',name='Recorrido',actor='victoria',points=['p0','p1'],loop=False)]
    s['events'][-1]['actions'][-1]={'travel':{'scene':'west','entry':'safe'}}
    return data

class Phase9Tests(TestCase):
    @classmethod
    def setUpClass(cls):cls.ws=Workspace(ROOT);cls.backend=Backend(cls.ws)
    def valid(self,data):
        result=self.backend.validate(data);self.assertTrue(result.valid,[p.message for p in result.problems]);return result.project
    def test_named_arrivals_paths_native_compilation_and_save_contract(self):
        data=modern();data['scenes'][0]['events'][0]['actions'] += [{'start_patrol':'walk'},{'stop_patrol':'victoria'},{'open_exit':'existing_exit'},{'close_exit':'existing_exit'}]
        report=self.backend.build(data)
        self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        first=report['save_schema_sha256'];data['scenes'][0]['paths'][0]['loop']=True
        changed=self.backend.build(data);self.assertNotEqual(first,changed['save_schema_sha256']);self.assertTrue(changed['new_game_required'])
        budgets=changed['format_validation']['classfile_budgets'];self.assertTrue(budgets);self.assertTrue(all(v['largest_method_bytes']<65536 for v in budgets.values()))
    def test_camera_sound_and_existing_door_compile_against_real_codex(self):
        data=modern();s=data['scenes'][0]
        s['sequences']=[dict(id='two',name='Plano de dos personajes',actor='victoria',duration=2,shot='medium',angle='medium',preset='two_shot')]
        s['events'].append(dict(id='optional',when='timer',seconds=30,actions=[{'play_sequence':'two'},{'play_sound':dict(resource='thunder_01',waypoint='p0',volume=80,min_distance=128,max_distance=512)},{'control_door':dict(cast_id='EastDoor',mode='frames',frame=1,parameter=150,open=True)},{'control_door':dict(cast_id='EastDoor',mode='pivot',frame=1,parameter=3,open=False)}]))
        report=self.backend.build(data);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        self.assertFalse(report['native_engine_test'])
    def test_invalid_arrival_path_motion_values_and_old_format_rejected(self):
        changes=[lambda d:d['scenes'][0]['events'][-1]['actions'][-1]['travel'].update(entry='missing'),lambda d:d['scenes'][0]['paths'][0].update(points=['p0','missing']),lambda d:d['scenes'][0]['paths'][0].update(actor='missing'),lambda d:d['scenes'][0]['paths'][0].update(speed=float('nan')),lambda d:d['scenes'][0]['entries'][0]['transform'].update(position=[float('inf'),0,0]),lambda d:d.update(project_format=5),lambda d:d['scenes'][0].update(default_entry='missing')]
        for change in changes:
            data=modern();change(data);self.assertFalse(self.backend.validate(data).valid)
    def test_marker_rename_graph_and_safe_delete_references(self):
        doc=CampaignDocument(self.ws,modern());doc.active=1;doc.rename('entries',0,'landing')
        self.assertEqual(doc.campaign['scenes'][0]['events'][-1]['actions'][-1]['travel']['entry'],'landing')
        doc.rename_global('scenes',1,'refuge');doc.active=0;doc.rename('waypoints',0,'start')
        self.assertEqual(doc.data['entries'][0]['id'],'safe');self.assertEqual(doc.campaign['scenes'][0]['paths'][0]['points'][0],'start')
        self.valid(doc.snapshot());self.assertFalse(scene_reachability(doc.snapshot()))
        self.assertTrue(any(x.target==('scenes',1,'entries',0) for x in graph(doc.snapshot())))
        from rcm.safe_edit import delete_candidate
        with self.assertRaises(ValueError):delete_candidate(doc,('scenes',1,'entries',0),self.backend)
    def test_trace_action_and_dialogue_results_locate_source(self):
        rows=parse_trace('ACTION scene dock event quest_done action 2: complete_quest\nDIALOGUE_END dock/victoria return=2 aborted=true')['events']
        self.assertEqual(rows[0]['context']['action'],2);self.assertTrue(rows[1]['context']['aborted'])
        rows=parse_trace('SAVE_STATE dock\nRESTORED dock\nWATCH_QUEST ledger 2 1 0')['events']
        self.assertEqual(rows[0]['context']['phase'],'SAVE_STATE');self.assertEqual(rows[1]['context']['scene'],'dock');self.assertEqual(rows[2]['context']['quest'],'ledger')
    def test_deploy_removes_obsolete_owned_files_preserves_foreign(self):
        data=modern();self.backend.build(data)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            game=Path(tmp);(game/'Vampire.exe').write_bytes(b'fixture');(game/'Resource.nob').write_bytes(b'fixture')
            with patch('rcm.deployment.configured_game',return_value=game),patch('rcm.deployment.game_running',return_value=False):
                result=deploy(self.ws,'p9_test','unique');dest=Path(result['destination']);foreign=dest/'foreign.txt';foreign.write_text('keep')
                old=dest/'codex/OldOwned.class';old.write_bytes(b'old');manifest=dest/'.rcm_deployment.json';owned=json.loads(manifest.read_text());owned['files']['codex/OldOwned.class']=hashlib.sha256(b'old').hexdigest();manifest.write_text(json.dumps(owned))
                deploy(self.ws,'p9_test','unique');self.assertFalse(old.exists());self.assertEqual(foreign.read_text(),'keep')
                owned=json.loads(manifest.read_text());old.write_bytes(b'modified');owned['files']['codex/OldOwned.class']=hashlib.sha256(b'old').hexdigest();manifest.write_text(json.dumps(owned))
                with self.assertRaisesRegex(ValueError,'modificado'):deploy(self.ws,'p9_test','unique')
                self.assertEqual(old.read_bytes(),b'modified')
    def test_generated_logic_arrival_reject_restore_patrol_partial_failure(self):
        data=modern();s=data['scenes'][0];s['events'].append(dict(id='partial',when='timer',seconds=.15,once=True,conditions=[{'flag':'alliance','is_set':False}],actions=[{'reward_xp':10},{'set_flag':'alliance'},{'give_item':'book'}]))
        # Only the initial scene creation remains. The item is created by the reward.
        s['events'][0]['actions']=[{'spawn':'victoria'},{'start_patrol':'walk'}];s['events']=s['events'][:1]+s['events'][-1:]
        p=self.valid(data);name,java=runtime(p,*p.scenes[0]);out=ROOT/'build/tests/phase9_runtime';out.mkdir(parents=True,exist_ok=True)
        (out/(name+'.java')).write_text(java,encoding='utf8')
        doubles=(ROOT/'tests/java/CampaignEngine.java').read_text()
        doubles=doubles.replace('boolean SetOrientation(float[] a)', 'boolean SetPosition(float[] a){if(CE.failSpawn)return false;CE.world.get(guid).pos=a.clone();return true;} boolean SetOrientation(float[] a)')
        doubles=doubles.replace('int SetActorTeam(int t)', 'void StopActorMotion(){} boolean SendActorToPos(float[] p,float v){CE.world.get(guid).pos=p.clone();return true;} int SetActorTeam(int t)')
        doubles=doubles.replace('boolean AddToActorInventory(int item){', 'boolean AddToActorInventory(int item){if(CE.failConversation)return false;')
        (out/'CampaignEngine.java').write_text(doubles)
        harness='''public class Phase9Harness { static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);} public static void main(String[] args) {
          CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);CE.failSpawn=true;
          R_p9_test_s0_Scene scene=new R_p9_test_s0_Scene();scene.beginscene(1,0);check(CE.created==0,"rejected arrival prevents scene-start content");
          CE.failSpawn=false;CE.failConversation=true;scene.timer(9400,0,0,0,0);check(CE.world.get(1).pos[0]==100,"named arrival applies transform");check(CE.xp==10,"partial reward grants XP once");
          int count=CE.created;scene.timer(9400,0,0,0,0);check(CE.xp==10,"retry after failed inventory does not grant XP again");
          CE.failConversation=false;scene.timer(9400,0,0,0,0);check(CE.world.get(1).inventory.size()==1,"failed action can recover");
          int npc=CodexThing.GuidFromCastID("R_p9_test_s0_victoria");check(CE.world.get(npc).pos[0]==150,"patrol visits second waypoint");
          CE.world.get(1).pos=new float[]{999,0,32};scene.save(0);R_p9_test_s0_Scene restored=new R_p9_test_s0_Scene();restored.restore(0);restored.restored(0);
          check(CE.world.get(1).pos[0]==999,"restore does not relocate player");check(CE.xp==10&&CE.world.get(1).inventory.size()==1,"restore retains once action progress");check(CE.released>0,"restored controller releases native camera");
        }}'''
        (out/'Phase9Harness.java').write_text(harness)
        result=subprocess.run(['javac','-d',str(out),str(out/'CampaignEngine.java'),str(out/(name+'.java')),str(out/'Phase9Harness.java')],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run(['java','-cp',str(out),'Phase9Harness'],cwd=ROOT/'build/tests',capture_output=True,text=True);(out/'harness.log').write_text(result.stdout+result.stderr);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
