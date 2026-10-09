"""Campaign contracts, invalid input, real compilation and generated callback scenarios."""
from pathlib import Path
import sys,copy,subprocess,tempfile
from unittest import TestCase
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.campaign_relations import graph
from rcm.not_inspector import inspect_not
from rcm.deployment import deploy,safe_target

def source():
    ws=Workspace(ROOT);d=CampaignDocument.convert(Document.load(ws,'tests/fixtures/chronicles/editor_acceptance/project.yaml'));root=d.snapshot();root['chronicle']['id']='c4_test'
    root['quests']=[dict(id='mission',title='El libro',description='Recupera el libro',steps=['Aceptar','Recuperar','Entregar'],reward_xp=500)]
    s=root['scenes'][0];s['objects']=[dict(id='book',name='Libro',template='ledger',quest_item=True,transform=dict(placement='near_player',orientation=[0,0,0]))]
    s['events'][0]['actions'].append({'spawn':'book'})
    s['events'] += [dict(id='start',when='conversation_ended',conversation='intro',result=3,once=True,actions=[{'start_quest':'mission'},{'advance_quest':'mission'}]),dict(id='pickup',when='item_picked_up',item='book',actions=[{'advance_quest':'mission'}]),dict(id='finish',when='conversation_ended',conversation='ally',result=1,conditions=[{'quest':'mission','step':2}],actions=[{'advance_quest':'mission'},{'complete_quest':'mission'},{'jump':'west'}])]
    root['scenes'].append(dict(id='west',level={'source':'WestLondon'},actors=[],objects=[],conversations=[],events=[]))
    return root

class CampaignTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.ws=Workspace(ROOT);cls.backend=Backend(cls.ws)
    def valid(self,data):
        result=self.backend.validate(data);self.assertTrue(result.valid,[p.message for p in result.problems]);return result.project
    def test_campaign_levels_legacy_geometry_and_steps(self):
        p=self.valid(source());self.assertEqual(len(p.scenes),2);self.assertEqual(len(p.source['quests'][0]['steps']),3);self.assertTrue(all(i>=256 for i in p.reserved.values()))
    def test_repeating_events_have_no_persistent_once_marker(self):
        d=source();s=d['scenes'][0];s['events'] += [dict(id='heartbeat',when='timer',seconds=.3,once=False,actions=[{'reward_xp':1}]),dict(id='pickup_again',when='item_picked_up',item='book',once=False,actions=[{'reward_xp':1}])]
        p=self.valid(d);self.assertNotIn('e/london/heartbeat',p.reserved);self.assertNotIn('e/london/pickup_again',p.reserved);self.assertIn('e/london/pickup',p.reserved);code=runtime(p,*p.scenes[0])[1];self.assertIn('ticks % 2 == 0',code)
    def test_corrupt_campaign_shapes_rejected_before_widgets(self):
        for change in [lambda d:d['quests'].append('bad'),lambda d:d['quests'][0].update(steps=[{}]),lambda d:d['scenes'][0].update(encounters=[{}]),lambda d:d['scenes'][0]['events'][0].update(conditions=[{'all':'bad'}]),lambda d:d['scenes'][0]['actors'][0].update(inventory='book')]:
            d=source();change(d)
            with self.assertRaises(ValueError):CampaignDocument.load_data(self.ws,d,None)
    def test_spawn_warnings_do_not_mix_local_scene_ids(self):
        d=source();d['scenes'][1]['actors']=[copy.deepcopy(d['scenes'][0]['actors'][0])];d['scenes'][1]['actors'][0].pop('conversation',None)
        result=self.backend.validate(d);self.assertTrue(any(p.path==('scenes',1,'actors',0) and 'nunca se crea' in p.message for p in result.problems))
    def test_safe_conditions_all_any_not(self):
        d=source();d['scenes'][0]['events'][-1]['conditions']=[{'all':[{'not':{'flag':'alliance','is_set':False}},{'any':[{'quest':'mission','step':2},{'owns_item':'book'}]}]}];p=self.valid(d);code=runtime(p,*p.scenes[0])[1];self.assertIn('&&',code);self.assertIn('||',code);self.assertIn('owns(player',code)
    def test_invalid_quest_references_steps_and_flags(self):
        for c in [{'quest':'missing','state':'active'},{'quest':'mission','step':3},{'quest':'mission','step':True},{'all':[]},{'flag':'bad','is_set':True},{'script':'anything'}]:
            d=source();d['scenes'][0]['events'][-1]['conditions']=[c];self.assertFalse(self.backend.validate(d).valid,c)
    def test_unknown_callbacks_actions_and_exit_are_rejected(self):
        for change in [lambda e:e.update(when='imaginary'),lambda e:e.update(actions=[{'invented':True}]),lambda e:e.update(actions=[{'jump':'missing'}]),lambda e:e.update(actions=[{'jump':'west'},{'set_flag':'alliance'}]),lambda e:e.update(seconds=1),lambda e:e.update(once='true')]:
            d=source();change(d['scenes'][0]['events'][-1]);self.assertFalse(self.backend.validate(d).valid)
    def test_prop_is_not_inventory_item(self):
        d=source();d['scenes'][0]['objects'][0]['template']='barrel1';self.assertFalse(self.backend.validate(d).valid)
    def test_inventory_unique_creation_owner(self):
        d=source();d['scenes'][0]['actors'][0]['inventory']=['book'];self.assertFalse(self.backend.validate(d).valid)
        d['scenes'][0]['events'][0]['actions']=[a for a in d['scenes'][0]['events'][0]['actions'] if a.get('spawn')!='book'];self.valid(d)
    def test_encounter_members_and_actor_behavior(self):
        d=source();s=d['scenes'][0];s['encounters']=[dict(id='guard',name='Guardia',actors=['victoria'])];self.assertFalse(self.backend.validate(d).valid)
        s['actors'][0]['behavior']='enemy';s['events'][0]['actions']=[{'spawn_encounter':'guard'},{'spawn':'book'}];self.valid(d)
    def test_sequences_audio_real_targets(self):
        d=source();s=d['scenes'][0];s['sequences']=[dict(id='view',name='Plano',actor='victoria',duration=2.5,shot='wide',angle='medium')];s['events'][0]['actions'] += [{'play_sequence':'view'},{'start_music':'London_Hub'},{'start_ambient':'amb_londonStreet'}];self.valid(d)
        s['sequences'][0]['duration']=float('nan');self.assertFalse(self.backend.validate(d).valid)
    def test_journal_budget_and_reserved_flags(self):
        d=source();d['quests']=[dict(id='q'+str(i),title='Quest',description='Texto',steps=['Paso']*32) for i in range(3)];self.assertFalse(self.backend.validate(d).valid)
    def test_global_rename_and_reference_graph(self):
        d=CampaignDocument(self.ws,source());d.rename_global('quests',0,'renamed');self.assertEqual(d.campaign['scenes'][0]['events'][-1]['actions'][1]['complete_quest'],'renamed')
        d.rename_global('scenes',1,'other');self.assertEqual(d.campaign['scenes'][0]['events'][-1]['actions'][-1]['jump'],'other');d.rename('objects',0,'ledger2');self.assertEqual(d.data['events'][-2]['item'],'ledger2');self.valid(d.snapshot())
        links=graph(d.campaign);self.assertTrue(any(x.target==('quests',0) for x in links));self.assertTrue(any(x.target==('scenes',1) for x in links))
    def test_campaign_document_atomic_recovery_backup_and_full_snapshot(self):
        path=ROOT/'build/tests/campaign_saved.yaml';d=CampaignDocument(self.ws,source());d.save(path);d.active=1;d.campaign['quests'][0]['title']='Otro título';d.autosave();loaded=Document.load(self.ws,path);self.assertTrue(loaded.recover());self.assertEqual(loaded.campaign['quests'][0]['title'],'Otro título');loaded.save();self.assertTrue(path.with_name(path.name+'.backup').exists());self.assertIn('scenes',loaded.snapshot());self.assertEqual(Document.load(self.ws,path).snapshot(),loaded.snapshot())
    def test_not_inspector_lossless_unknown_and_offsets(self):
        for name in ['Global','modernDay','darkAges','Multiplayer']:
            path=next((ROOT/'research/original/Resource.nob/misc/Templates').glob(name+'.not'));data=path.read_bytes();r=inspect_not(data);self.assertTrue(r['lossless_roundtrip']);self.assertTrue(r['templates']);self.assertTrue(all(p['offset']<len(data) for t in r['templates'] for p in t['properties']))
    def test_deploy_is_manifest_checked_and_stays_under_rcm(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            game=Path(tmp);(game/'Vampire.exe').write_bytes(b'fixture');(game/'Resource.nob').write_bytes(b'fixture');ws=Workspace(ROOT,game)
            self.backend.build(source());
            with patch('rcm.deployment.game_running',return_value=False), patch('rcm.deployment.configured_game',return_value=game):
                result=deploy(ws,'c4_test');self.assertTrue(Path(result['backup']).exists());self.assertTrue((game/'RCM/c4_test/c4_test.nob').exists())
                with self.assertRaises(ValueError):safe_target(game,game/'codex/unsafe.class')
                with self.assertRaises(ValueError):deploy(ws,'c4_test','../escape')
                stale=source();stale['chronicle']['name']='Otro nombre'
                with self.assertRaisesRegex(ValueError,'cambió'):deploy(ws,'c4_test',current_source=stale)
            with patch('rcm.deployment.game_running',return_value=True), patch('rcm.deployment.configured_game',return_value=game):
                with self.assertRaises(ValueError):deploy(ws,'c4_test')
    def test_campaign_build_real_api_package_no_geometry(self):
        report=self.backend.build(source());self.assertEqual(len(report['class_versions']),4);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()));self.assertFalse(report['geometry_in_package']);self.assertIn('quests/R_c4_test_q0s2.nqd',report['files'])
        nsc=(ROOT/'build/c4_test/runtime/chronicles/c4_test.nsc').read_text();self.assertIn('location london',nsc);self.assertIn('location west',nsc)
    def test_cross_scene_inventory_references_rename_and_generation(self):
        data=source();data['scenes'][0]['events'][-1]['conditions'].append({'owns_item':'london.book'});data['scenes'][0]['events'][-1]['actions'].insert(0,{'take_item':'london.book'});p=self.valid(data);code=runtime(p,*p.scenes[0])[1];self.assertIn('inventory(player,"R_c4_test_s0_book")',code)
        d=CampaignDocument(self.ws,data);d.rename_global('scenes',0,'east');d.rename('objects',0,'journal');self.assertEqual(d.data['events'][-1]['conditions'][-1]['owns_item'],'east.journal');self.valid(d.snapshot())
    def test_all_actions_compile_with_negative_spatial_transforms(self):
        data=source();s=data['scenes'][0];s['actors'][0]['behavior']='enemy';s['sequences']=[dict(id='cam',name='Plano',actor='victoria',duration=1.0,shot='wide',angle='high')];s['encounters']=[dict(id='guard',name='Guardia',actors=['victoria'])]
        s['triggers']=[dict(id='area',name='Entrada',shape='box',transform=dict(position=[-10,-50,-40],orientation=[0,0,-45]),size=[100,100,100])]
        s['events'][0]['actions']=[{'spawn_encounter':'guard'},{'spawn':'book'},{'start_music':'London_Hub'},{'start_ambient':'amb_londonStreet'},{'play_sequence':'cam'},{'release_camera':True},{'disable_ai':'victoria'},{'enable_ai':'victoria'}]
        s['events'].append(dict(id='extra',when='trigger_leave',trigger='area',actions=[{'give_item':'book'},{'take_item':'london.book'},{'reward_xp':10},{'stop_music':True},{'stop_ambient':True},{'remove_encounter':'guard'},{'remove':'book'}]))
        data['chronicle']['id']='c4_all';report=self.backend.build(data);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
    def test_generated_runtime_quest_item_save_and_transition(self):
        p=self.valid(source());name,java=runtime(p,*p.scenes[0]);out=ROOT/'build/tests/campaign_java';out.mkdir(parents=True,exist_ok=True);(out/(name+'.java')).write_text(java,encoding='utf8')
        harness='''public class CampaignHarness { static void check(boolean b,String s) { if(!b) throw new AssertionError(s); System.out.println(s); } public static void main(String[]args) {
          CE.Thing pl=new CE.Thing();pl.template="player";CE.world.put(1,pl);
          R_c4_test_s0_Scene scene=new R_c4_test_s0_Scene();scene.beginscene(1,0);
          int npc=CodexThing.GuidFromCastID("R_c4_test_s0_victoria"),book=CodexThing.GuidFromCastID("R_c4_test_s0_book");check(npc!=0&&book!=0,"spawn layer");
          scene.clicked(npc,1,0);check(CE.conversation.endsWith("intro"),"conversation intro");scene.convended(1,false,3);check(CE.quests.size()==3,"quest started and first step advanced");
          new CodexActor(1).AddToActorInventory(book);scene.timer(9400,0,0,0,0);check(CE.quests.size()==4,"pickup advances native step");int count=CE.created;scene.timer(9400,0,0,0,0);check(CE.created==count,"no duplicate spawn");
          scene.save(0);R_c4_test_s0_Scene loaded=new R_c4_test_s0_Scene();loaded.restore(0);loaded.restored(0);check(CE.created==count,"restore preserves entity GUIDs");
          loaded.clicked(npc,1,0);check(CE.conversation.endsWith("ally"),"flag selects remembered dialogue");loaded.convended(1,true,1);check(CE.xp==0,"abort does not complete quest");
          loaded.clicked(npc,1,0);loaded.convended(1,false,1);check(CE.xp==500&&CE.complete.size()==4,"three native steps quest completion reward");check(CE.jump.equals("west"),"confirmed Jump target");loaded.timer(9400,0,0,0,0);check(CE.xp==500,"reward idempotent");
          CE.client=true;new R_c4_test_s0_Scene().beginscene(1,0);check(CE.created==count,"client cannot author world");System.out.println("12 campaign runtime checks passed with doubles");
        }}'''
        (out/'CampaignHarness.java').write_text(harness,encoding='utf8');result=subprocess.run(['javac','-d',str(out),str(ROOT/'tests/java/CampaignEngine.java'),str(out/(name+'.java')),str(out/'CampaignHarness.java')],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run(['java','-cp',str(out),'CampaignHarness'],cwd=ROOT/'build/tests',capture_output=True,text=True);(out/'harness.log').write_text(result.stdout+result.stderr,encoding='utf8');self.assertEqual(result.returncode,0,result.stdout+result.stderr)
