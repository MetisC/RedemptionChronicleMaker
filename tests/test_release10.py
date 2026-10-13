"""Release authoring contracts and actual Java scenarios; no native claims."""
import copy
import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from rcm import recipes
from rcm.campaign_generator import runtime
from test_stability_revision import compile_scenario
ROOT=Path(__file__).resolve().parents[1]


def blank():
    def scene(ident):return dict(id=ident,level=dict(source='EastLondon',environment_scene='EAST_28_1.nsd'),actors=[],objects=[],conversations=[],events=[],triggers=[],sequences=[],encounters=[],paths=[],waypoints=[],entries=[dict(id='start',name='Arrival',transform=dict(position=[-62,-768,384],orientation=[0,0,180]))],default_entry='start')
    return dict(schema=2,project_format=9,chronicle=dict(id='rc_test',name='A release test'),entry='street',state={'flags':{}},scenes=[scene('street'),scene('home')],quests=[],resources={})


class RecipeContracts(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT))
    def valid(self,data):
        v=self.backend.validate(data);self.assertTrue(v.valid,[p.message for p in v.problems if p.severity=='ERROR']);return v.project
    def test_all_ten_recipes_create_normal_valid_entities_and_reopen_current_values(self):
        for kind in recipes.TYPES:
            with self.subTest(kind=kind):
                root,rid=recipes.apply(blank(),kind,'street',{'destination':'home'})
                self.valid(root)
                reopened=CampaignDocument.load_data(self.backend.ws,copy.deepcopy(root),ROOT/'chronicles/test_draft.yaml')
                recipe=recipes.recipes(reopened.campaign)[0]
                current=recipes.values(reopened.campaign,recipe)
                candidate,_=recipes.apply(reopened.snapshot(),kind,'street',current,rid)
                self.assertEqual(candidate,reopened.snapshot(),'Opening and applying unchanged settings must be lossless')
                self.assertFalse(recipes.missing(candidate,recipe))
    def test_runtime_ignores_all_authoring_metadata(self):
        root,_=recipes.apply(blank(),'go_to_place','street',{})
        first=self.valid(root);other=copy.deepcopy(root);other.pop('authoring');second=self.valid(other)
        self.assertEqual(first.source,second.source)
        self.assertEqual(runtime(first,*first.scenes[0]),runtime(second,*second.scenes[0]))
    def test_tutorial_wizard_reopen_preserves_followup_conversation_and_travel(self):
        root=Document.load(self.backend.ws,'chronicles/tutorial/project.yaml').snapshot()
        recipe=recipes.recipes(root)[0];current=recipes.values(root,recipe)
        changed,_=recipes.apply(root,'go_to_place','square',current,recipe['id'])
        self.assertEqual(changed,root)
        mentor=recipes.resolve(changed,recipe['refs']['actor'])
        self.assertEqual(mentor['conversation']['then'],'to_elena')
        self.valid(changed)
    def test_prerelease_packages_compare_versions_without_claiming_final_release(self):
        from rcm.versioning import version_key
        from rcm.packages import verify_manifest
        from rcm import __version__
        import json
        versions=['0.9.13','1.0.0-alpha1','1.0.0-beta1','1.0.0-rc1','1.0.0-rc2','1.0.0','1.0.1-rc1']
        self.assertEqual(sorted(versions,key=version_key),versions)
        for invalid in [None,'1.0','1.0.0-rc0','1.0.0-rcfoo','1.0.0;cmd']:
            with self.assertRaises(ValueError):version_key(invalid)
        manifest=dict(format=1,kind='chronicle',id='sample',version='0.1.0',custom_code=False,files={},requires_rcm=__version__)
        self.assertEqual(verify_manifest({'manifest.json':json.dumps(manifest).encode()},'chronicle')['requires_rcm'],__version__)
        manifest['requires_rcm']='99.0.0'
        with self.assertRaises(ValueError):verify_manifest({'manifest.json':json.dumps(manifest).encode()},'chronicle')
    def test_metadata_validation_rejects_malformed_versions_refs_and_duplicate_ids(self):
        root,_=recipes.apply(blank(),'talk','street',{})
        for value in [None,[],{'recipes':[None]},{'recipes':[dict(id='x',type='talk',version=True,scene='street',refs={})]}]:
            row=copy.deepcopy(root);row['authoring']=value
            self.assertFalse(self.backend.validate(row).valid)
        row=copy.deepcopy(root);row['authoring']['recipes']*=2;self.assertFalse(self.backend.validate(row).valid)
    def test_manual_edits_and_additional_nodes_remain_single_source_of_truth(self):
        root,rid=recipes.apply(blank(),'go_to_place','street',{})
        recipe=recipes.recipes(root)[0];actor=recipes.resolve(root,recipe['refs']['actor']);actor['name']='Changed outside wizard';actor['transform']['position']=[12,34,56]
        conv=recipes.resolve(root,recipe['refs']['conversation']);conv['prompt']='An edited instruction';conv['camera']='speaker_close'
        seq=recipes.resolve(root,recipe['refs']['sequence']);seq['steps'].insert(1,dict(at=1,actor='Player',preset='full',transition=.7))
        data=recipes.values(root,recipe);self.assertEqual(data['text'],'An edited instruction');self.assertEqual(data['position'],[12,34,56]);self.assertEqual(data['camera'],'speaker_close')
        changed,_=recipes.apply(root,'go_to_place','street',data,rid);self.assertEqual(changed,root)
    def test_renames_follow_typed_recipe_references_without_changing_text(self):
        root,rid=recipes.apply(blank(),'go_to_place','street',{})
        doc=CampaignDocument(self.backend.ws,root);recipe=recipes.recipes(root)[0]
        actor=recipes.resolve(root,recipe['refs']['actor']);conv=recipes.resolve(root,recipe['refs']['conversation']);conv['prompt']=actor['id']
        doc.rename('actors',0,'new_npc');self.assertEqual(recipe['refs']['actor']['id'],'new_npc');self.assertNotEqual(conv['prompt'],'new_npc')
        doc.rename_flag(recipe['refs']['flag']['id'],'go_square');self.assertEqual(recipe['refs']['flag']['id'],'go_square')
        doc.rename_global('scenes',0,'plaza');self.assertEqual(recipe['scene'],'plaza');self.assertEqual(recipe['refs']['actor']['scene'],'plaza');self.valid(root)
    def test_incomplete_recipe_requires_explicit_repair_or_rebind_or_unlink(self):
        root,rid=recipes.apply(blank(),'quest','street',{})
        root['quests']=[];recipe=recipes.recipes(root)[0]
        self.assertIn('quest',recipes.missing(root,recipe))
        with self.assertRaisesRegex(ValueError,'Incomplete'):recipes.apply(root,'quest','street',{},rid)
        restored,_=recipes.apply(root,'quest','street',{},rid,repair=True);self.valid(restored)
        self.assertEqual(recipes.resolve(restored,recipe['refs']['quest'])['id'],recipe['refs']['quest']['id'])
        unlinked=recipes.unlink(restored,rid);self.assertEqual(unlinked['quests'],restored['quests']);self.assertEqual(recipes.recipes(unlinked),[])
    def test_trigger_conditions_once_and_player_target_are_validated(self):
        root,_=recipes.apply(blank(),'go_to_place','street',{})
        self.valid(root);s=root['scenes'][0];seq=s['sequences'][0]
        for mutation in [lambda d:d['scenes'][0]['sequences'][0].pop('steps'),lambda d:d['scenes'][0]['sequences'][0]['steps'][0].update(actor='Missing'),lambda d:d['scenes'][0]['sequences'][0]['steps'][1].update(transition=-1),lambda d:d['scenes'][0]['sequences'][0]['steps'][1].update(at=9),lambda d:d['scenes'][0]['sequences'][0].update(reference='Missing')]:
            data=copy.deepcopy(root);mutation(data);self.assertFalse(self.backend.validate(data).valid)
        self.assertEqual(seq['actor'],'Player');self.assertEqual(s['events'][2]['conditions'][0]['is_set'],True)
    def test_recipe_rebind_preserves_entities_and_target_selection(self):
        root,rid=recipes.apply(blank(),'talk','street',{})
        root['scenes'][0]['actors'].append(dict(id='other',name='Other',template='LonCiv1',transform=dict(placement='absolute',position=[0,0,384],orientation=[0,0,0])))
        result=recipes.rebind(root,rid,'actor',dict(scene='street',collection='actors',id='other'))
        self.assertEqual(len(result['scenes'][0]['actors']),2)
        self.assertEqual(recipes.values(result,recipes.recipes(result)[0])['name'],'Other')
        self.assertEqual(result['scenes'][0]['conversations'][0]['speaker'],'other')
        self.valid(result)
    def test_rebinding_actor_does_not_overwrite_an_unrelated_conversation(self):
        root,rid=recipes.apply(blank(),'talk','street',{})
        root,_=recipes.apply(root,'talk','street',{})
        before=copy.deepcopy(root)
        with self.assertRaisesRegex(ValueError,'otra conversación'):
            recipes.rebind(root,rid,'actor',dict(scene='street',collection='actors',id='actor2'))
        self.assertEqual(root,before);self.valid(root)
    def test_travel_edit_creates_arrival_in_new_destination_and_preserves_old(self):
        root,rid=recipes.apply(blank(),'travel','street',{'destination':'home'})
        root['scenes'].append(copy.deepcopy(root['scenes'][1]));root['scenes'][-1]['id']='third'
        changed,_=recipes.apply(root,'travel','street',{'destination':'third','arrival_position':[1,2,384]},rid)
        self.valid(changed);self.assertEqual(len(changed['scenes'][1]['entries']),2);self.assertEqual(len(changed['scenes'][2]['entries']),3)
    def test_repeating_trigger_disables_both_once_guards_and_manual_box_is_preserved(self):
        root,rid=recipes.apply(blank(),'trigger_actions','street',{'once':False})
        area=root['scenes'][0]['triggers'][0];self.assertFalse(area['once']);self.assertFalse(root['scenes'][0]['events'][0]['once'])
        area['shape']='box';area.pop('radius');area['size']=[80,100,40];area['transform']['orientation']=[0,0,45]
        changed,_=recipes.apply(root,'trigger_actions','street',recipes.values(root,recipes.recipes(root)[0]),rid)
        self.assertEqual(changed,root);self.valid(changed)
    def test_deleting_recipe_event_is_soft_reference_and_marks_incomplete(self):
        from rcm.safe_edit import delete_candidate
        root,rid=recipes.apply(blank(),'talk','street',{})
        doc=CampaignDocument(self.backend.ws,root)
        deleted=delete_candidate(doc,('scenes',0,'events',0),self.backend)
        self.assertIn('spawn_event',recipes.missing(deleted,recipes.recipes(deleted)[0]))
        self.assertTrue(self.backend.validate(deleted).valid)
        self.assertTrue(any('Incomplete configuration' in p.message for p in self.backend.validate(deleted).problems))
    def test_encounter_zero_reward_does_not_emit_invalid_award_and_edits_existing_reward(self):
        root,rid=recipes.apply(blank(),'encounter','street',{'reward_xp':7})
        current=recipes.values(root,recipes.recipes(root)[0]);self.assertEqual(current['reward_xp'],7)
        root,_=recipes.apply(root,'encounter','street',{'reward_xp':0},rid);self.valid(root)
        self.assertFalse(any('reward_xp' in a for e in root['scenes'][0]['events'] for a in e['actions']))
    def test_note_edit_preserves_manual_actions_before_and_after_text_panel(self):
        root,rid=recipes.apply(blank(),'note','street',{})
        root['state']['flags']['read']=25;event=root['scenes'][0]['events'][-1]
        event['actions'].insert(0,{'set_flag':'read'});event['actions'].append({'reward_xp':3})
        new,_=recipes.apply(root,'note','street',{'title':'Edited letter','text':'A human-written message.'},rid)
        self.assertEqual(new['scenes'][0]['events'][-1]['actions'],[{'set_flag':'read'},{'show_note':{'title':'Edited letter','text':'A human-written message.'}},{'reward_xp':3}]);self.valid(new)


class RecipeGui(TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        from rcm.editor.window import MainWindow
        self.win=MainWindow(self.backend);self.win.autosave_timer.stop();self.win.doc=CampaignDocument(self.backend.ws,blank());self.win.refresh()
    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()
    def wizard(self,kind,rid=None):
        from rcm.editor.recipe_wizard import RecipeWizard
        w=RecipeWizard(self.win,kind,rid);w.initializePage(1);return w
    def test_all_ten_actual_wizards_apply_without_yaml_and_undo_redo(self):
        for kind in recipes.TYPES:
            self.win.doc.data=blank();self.win.history_document=None;self.win.refresh();before=self.win.doc.snapshot()
            w=self.wizard(kind);w.accept();self.assertTrue(recipes.recipes(self.win.doc.campaign),(kind,w.error.text()))
            self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid,(kind,w.error.text()))
            after=self.win.doc.snapshot();self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before);self.win.redo_project();self.assertEqual(self.win.doc.snapshot(),after);w.deleteLater()
    def test_reopen_after_save_and_external_edit_shows_current_text_and_position(self):
        w=self.wizard('go_to_place');w.accept();rid=w.recipe_id;w.deleteLater()
        root=self.win.doc.campaign;r=recipes.recipes(root)[0];conv=recipes.resolve(root,r['refs']['conversation']);conv['prompt']='Read the actual edited text.'
        actor=recipes.resolve(root,r['refs']['actor']);actor['transform']['position']=[10,20,384]
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            self.win.doc.save(Path(folder)/'project.yaml');self.win.doc=Document.load(self.backend.ws,Path(folder)/'project.yaml');self.win.refresh()
            w=self.wizard('go_to_place',rid);self.assertEqual(w.controls['text'].toPlainText(),conv['prompt']);self.assertEqual([a.value() for a in w.controls['position']],[10,20,384]);w.deleteLater()
    def test_cancel_and_validation_failure_leave_document_and_history_unchanged(self):
        before=self.win.doc.snapshot();w=self.wizard('talk');w.reject();self.assertEqual(self.win.doc.snapshot(),before);w.deleteLater()
        w=self.wizard('talk');w.controls['template'].setText('missing_template');w.accept();self.assertTrue(w.error.text());self.assertEqual(self.win.doc.snapshot(),before);w.deleteLater()
    def test_changed_document_is_not_overwritten_by_open_wizard(self):
        w=self.wizard('talk');self.win.doc.campaign['chronicle']['name']='Another edit';w.accept();self.assertIn('cambió',w.error.text());self.assertFalse(recipes.recipes(self.win.doc.campaign));w.deleteLater()
    def test_tutorial_links_open_appropriate_wizard(self):
        from PySide6.QtCore import QUrl
        with patch('rcm.editor.recipe_wizard.open_wizard') as open_wizard:
            self.win.guide_panel.navigate(QUrl('rcm://wizard/trigger_cinematic/new'));open_wizard.assert_called_once_with(self.win,'trigger_cinematic',None)
    def test_authoring_references_navigate_to_assistant_without_inspecting_metadata_as_entity(self):
        w=self.wizard('talk');w.accept();w.deleteLater();rid=recipes.recipes(self.win.doc.campaign)[0]['id']
        self.win.find_references(('actors',0));self.assertIn(rid,self.win.reference_label(('authoring','recipes',0)))
        with patch('rcm.editor.recipe_wizard.open_wizard') as opened:
            self.win.navigate_reference(('authoring','recipes',0));opened.assert_called_once_with(self.win,None,rid)
    def test_recipe_menu_passes_id_instead_of_action_checked_boolean(self):
        w=self.wizard('talk');w.accept();w.deleteLater();rid=recipes.recipes(self.win.doc.campaign)[0]['id']
        with patch('rcm.editor.recipe_wizard.open_wizard') as opened:
            self.win.recipe_menu.aboutToShow.emit();self.win.recipe_menu.actions()[0].trigger()
            opened.assert_called_once_with(self.win,None,rid)
    def test_player_sequence_selector_mode_rename_and_reference_roundtrip(self):
        from PySide6.QtWidgets import QComboBox,QLineEdit
        w=self.wizard('go_to_place');w.accept();w.deleteLater()
        self.win.campaign_panel.navigate(('scenes',0,'sequences',0))
        panel=self.win.campaign_panel
        self.assertEqual(panel.findChild(QComboBox,'sequence_actor').currentData(),'Player')
        self.assertEqual(panel.findChild(QComboBox,'sequence_mode').currentData(),'timeline')
        field=panel.findChild(QLineEdit,'campaign_id');field.setText('arrival');self.win.commit_properties()
        recipe=recipes.recipes(self.win.doc.campaign)[0];self.assertEqual(recipe['refs']['sequence']['id'],'arrival')
        end=recipes.resolve(self.win.doc.campaign,recipe['refs']['end_event']);self.assertEqual(end['sequence'],'arrival')
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
    def test_wizard_1100x720_and_large_font_scroll_without_reducing_text(self):
        from PySide6.QtGui import QFont
        w=self.wizard('go_to_place');w.setFont(QFont('Segoe UI',15));w.resize(700,620);w.show();self.app.processEvents()
        self.assertGreater(w.scroll.height(),190);self.assertGreater(w.scroll.viewport().width(),300);self.assertEqual(w.font().pointSize(),15);w.reject();w.deleteLater()


class PlayerCinematicRuntime(TestCase):
    def test_complete_tutorial_story_pickup_encounter_travel_quest_reward_and_save(self):
        import subprocess
        backend=Backend(Workspace(ROOT));campaign=backend.validate(Document.load(backend.ws,'chronicles/tutorial/project.yaml').snapshot()).project
        self.assertIsNotNone(campaign)
        harness='''public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_rcm_tutor_s0_Scene s,int n){for(int i=0;i<n;i++)s.timer(9400,0,0,0,0);}
          public static void main(String[] args)throws Exception{
            CE.Thing p=new CE.Thing();p.template="player";p.pos=new float[]{-62,-768,384};CE.world.put(1,p);
            int carried=CE.make("R_rcm_tutor_s0_object1",p.pos);new CodexActor(1).AddToActorInventory(carried);
            int belonging=CE.make("unrelated_book",p.pos);new CodexActor(1).AddToActorInventory(belonging);
            R_rcm_tutor_s0_Scene s=new R_rcm_tutor_s0_Scene();s.beginscene(1,0);s.textended(1);tick(s,1);
            check(CE.quests.size()==1,"journal starts with only current objective");
            check(!CE.valid(carried)&&p.inventory.size()==1&&p.inventory.contains(Integer.valueOf(belonging))&&CodexThing.GuidFromCastID("R_rcm_tutor_s0_enemy1")==0,"a carried mission letter from Crypt cannot skip the fresh tutorial or spawn the Rat early; other belongings are preserved");
            int npc=CodexThing.GuidFromCastID("R_rcm_tutor_s0_actor1");s.clicked(npc,1,0);s.convended(1,false,1);tick(s,1);
            p.pos=new float[]{-240,-850,384};tick(s,45);check(!CE.cutscene&&CE.quests.size()==2,"approaching the barrel completes first objective without touching its solid body");
            int letter=CodexThing.GuidFromCastID("R_rcm_tutor_s0_object1");check(CE.valid(letter),"arrival reveals pickup letter");new CodexActor(1).AddToActorInventory(letter);tick(s,2);
            int rat=CodexThing.GuidFromCastID("R_rcm_tutor_s0_enemy1");check(CE.valid(rat),"pickup spawns one basic enemy");CE.world.get(rat).health=0;tick(s,2);s.textended(1);tick(s,2);
            check(CE.xp==5&&CE.quests.size()==3,"encounter grants one reward and next objective");
            CE.save.clear();s.save(0);R_rcm_tutor_s0_Scene loaded=new R_rcm_tutor_s0_Scene();CE.read=0;loaded.restore(0);loaded.restored(0);tick(loaded,25);check(CE.xp==5,"loading after encounter does not repeat XP");
            p.pos=new float[]{-226.596f,-714.506f,384};tick(loaded,2);check(CE.jump.equals(""),"talking distance is outside the small automatic travel area");
            loaded.clicked(npc,1,0);check(CE.conversation.equals("R_rcm_tutor_s0_to_elena"),"Anezka offers delivery after the encounter instead of repeating the barrel request");
            loaded.convended(1,false,2);tick(loaded,2);check(CE.jump.equals(""),"declining travel keeps the player in the street");
            loaded.clicked(npc,1,0);loaded.convended(1,false,1);tick(loaded,2);check(CE.jump.equals("home"),"dialogue travels to Elena from outside the automatic area without using the letter");
            CE.location=1;p.location=1;R_rcm_tutor_s1_Scene h=new R_rcm_tutor_s1_Scene();h.beginscene(1,0);
            int elena=CodexThing.GuidFromCastID("R_rcm_tutor_s1_actor1");h.clicked(elena,1,0);h.convended(1,false,1);h.timer(9400,0,0,0,0);
            check(CE.xp==25&&CE.complete.size()==3,"letter delivery completes quest and grants final reward");
            h.clicked(elena,1,0);check(CE.conversation.equals("R_rcm_tutor_s1_delivered"),"Elena acknowledges completed delivery instead of requesting the letter again");h.convended(1,false,1);h.timer(9400,0,0,0,0);check(CE.xp==25,"second conversation does not repeat final reward");
            CE.save.clear();h.save(0);R_rcm_tutor_s1_Scene again=new R_rcm_tutor_s1_Scene();CE.read=0;again.restore(0);again.restored(0);for(int i=0;i<25;i++)again.timer(9400,0,0,0,0);check(CE.xp==25,"save after travel and completion retains progress");
            p.pos=new float[]{-240,-850,384};for(int i=0;i<2;i++)again.timer(9400,0,0,0,0);check(CE.jump.equals("square"),"approaching the visible barrel after delivery enables return journey");
            CE.location=0;p.location=0;int count=CE.world.size();R_rcm_tutor_s0_Scene revisit=new R_rcm_tutor_s0_Scene();revisit.beginscene(1,0);tick(revisit,3);revisit.beginscene(1,0);tick(revisit,3);
            check(CE.xp==25&&!CE.cutscene&&CE.world.size()==count,"reentry preserves reward and does not duplicate entities or film");
            CE.jump="";p.pos=new float[]{-176,-612,384};tick(revisit,2);check(CE.jump.equals(""),"completed delivery disables the automatic trip on reentry");
          }
        }'''
        out=ROOT/'build/tests/release_story'
        compile_scenario(out,campaign,'public class StabilityHarness { public static void main(String[] args) {} }',lambda data:data.replace('t.contains("book")||t.contains("reward")','t.contains("book")||t.contains("reward")||t.endsWith("_object1")'))
        (out/'StabilityHarness.java').write_text(harness,encoding='utf8')
        # The harness refers to the second ordinary generated scene.
        # Compile it before compiling/running the harness below.
        name,code=runtime(campaign,*campaign.scenes[1]);(out/(name+'.java')).write_text(code,encoding='utf8')
        run=subprocess.run(['javac','-cp',str(out),'-d',str(out),str(out/(name+'.java')),str(out/'StabilityHarness.java')],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_trigger_gate_player_shots_restore_once_sequence_end_and_reentry(self):
        backend=Backend(Workspace(ROOT));root,rid=recipes.apply(blank(),'go_to_place','street',{'trigger_position':[-342,-1018,384]})
        root['chronicle']['id']='p9_test'
        campaign=backend.validate(root).project;self.assertIsNotNone(campaign)
        r=recipes.recipes(root)[0];actor=r['refs']['actor']['id']
        requested=root['state']['flags'][r['refs']['flag']['id']];done=root['state']['flags'][r['refs']['done_flag']['id']]
        java=runtime(campaign,*campaign.scenes[0])[1]
        self.assertIn('SetupCutscene(cameraPlayer,player,things[0])',java);self.assertNotIn('SetupCutscene(cameraPlayer,player,player)',java)
        harness='''public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_p9_test_s0_Scene s,int n){for(int i=0;i<n;i++)s.timer(9400,0,0,0,0);}
          public static void main(String[] args)throws Exception{
            CE.Thing p=new CE.Thing();p.template="player";p.pos=new float[]{-62,-768,384};CE.world.put(1,p);
            R_p9_test_s0_Scene s=new R_p9_test_s0_Scene();s.beginscene(1,0);
            p.pos=new float[]{-342,-1018,384};tick(s,1);check(!CE.cutscene,"trigger gated before conversation");
            p.pos=new float[]{-62,-768,384};tick(s,1);
            int npc=CodexThing.GuidFromCastID("R_p9_test_s0_ACTOR");s.clicked(npc,1,0);s.convended(1,false,2);tick(s,1);check(!CE.flags[REQUEST],"decline does not arm trigger");
            s.clicked(npc,1,0);s.convended(1,true,1);tick(s,1);check(!CE.flags[REQUEST]&&CE.cameraTarget==0,"abort releases camera and does not arm");
            s.clicked(npc,1,0);s.convended(1,false,1);tick(s,1);check(CE.flags[REQUEST]&&CE.cameraTarget==0,"accepted return activates flag and restores camera");
            p.pos=new float[]{-342,-1018,384};tick(s,1);check(CE.cutscene&&CE.aiOff&&CE.cameraTarget==1,"arrival presents player with native cutscene ownership");
            int calls=CE.conversationCalls;s.clicked(npc,1,0);check(CE.conversationCalls==calls,"film retains control against clicks");
            tick(s,10);CE.save.clear();s.save(0);check(!CE.flags[DONE],"saving mid film does not complete progress early");
            R_p9_test_s0_Scene loaded=new R_p9_test_s0_Scene();CE.read=0;loaded.restore(0);loaded.restored(0);tick(loaded,60);
            check(CE.flags[DONE]&&!CE.cutscene&&!CE.aiOff&&CE.cameraTarget==0,"restore replays interrupted player film and delivers completion");
            check(CE.shots>=3&&CE.transitions.contains(Float.valueOf(1.5f)),"wide and close native shots use smooth transition");
            int shots=CE.shots,created=CE.created;tick(loaded,60);p.pos=new float[]{0,0,384};tick(loaded,1);p.pos=new float[]{-342,-1018,384};tick(loaded,1);check(CE.shots==shots,"once film cannot fire twice");
            loaded.beginscene(1,0);tick(loaded,2);check(CE.created==created&&!CE.cutscene,"reentry no duplicate actors or stranded camera");
            CE.save.clear();loaded.save(0);R_p9_test_s0_Scene after=new R_p9_test_s0_Scene();CE.read=0;after.restore(0);after.restored(0);tick(after,60);check(CE.shots==shots&&CE.flags[DONE],"save after completion retains once progress");
          }
        }'''.replace('ACTOR',actor).replace('REQUEST',str(requested)).replace('DONE',str(done))
        def double(data):
            data=data.replace('class CE {','class CE {static int shots=0; static java.util.List<Float> transitions=new java.util.ArrayList<Float>();')
            return data.replace('static void SetShot(int p,int s,int a,int d,int f,float t){}','static void SetShot(int p,int s,int a,int d,int f,float t){CE.shots++;CE.transitions.add(Float.valueOf(t));}')
        out=ROOT/'build/tests/release_player';compile_scenario(out,campaign,harness,double)
        import subprocess
        run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('save after completion retains once progress',run.stdout)
    def test_tutorial_and_mini_are_valid_and_have_player_arrival_and_two_scenes(self):
        backend=Backend(Workspace(ROOT))
        for name in ['tutorial','mini_chronicle']:
            root=Document.load(backend.ws,'chronicles/'+name+'/project.yaml').snapshot();v=backend.validate(root)
            self.assertTrue(v.valid,[p.message for p in v.problems if p.severity=='ERROR']);self.assertGreaterEqual(len(root['scenes']),2)
            self.assertTrue(any(q['actor']=='Player' for s in root['scenes'] for q in s.get('sequences',[])))
            self.assertTrue(recipes.recipes(root))
    def test_legacy_inventory_templates_remain_in_tutorial_startup_catalogue(self):
        backend=Backend(Workspace(ROOT));root=Document.load(backend.ws,'chronicles/tutorial/project.yaml').snapshot();backend.sync_resources(root)
        from rcm.formats import NotFile
        templates={t.name for key,data in backend.project_payload.items() if key.endswith('.not') for t in NotFile.read(data).templates}
        self.assertTrue({'R_rcm_tutor_s0_key','R_rcm_tutor_s0_reward','R_rcm_tutor_s0_npc_key','R_rcm_tutor_s0_npc_book'}<=templates)
