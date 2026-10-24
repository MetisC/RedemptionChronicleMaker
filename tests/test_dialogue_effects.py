"""Response actions, actual flag edges and native AI presets; no gameplay automation."""
import copy
import os
from pathlib import Path
import subprocess
import tempfile
from unittest import TestCase
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QPushButton,QComboBox,QMessageBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.campaign_relations import graph
from rcm.safe_edit import deletion_plan
from rcm.editor.window import MainWindow
from rcm.editor.dialogue_actions import behavior_action,edit_flag_reaction
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]


def source():
    root=blank();root['chronicle']['id']='reply_test';root['state']['flags']={'hostile':0}
    scene=root['scenes'][0]
    scene['actors']=[dict(id='mentor',name='Mentor',template='Rat',behavior='npc',
        transform=dict(position=[10,20,30],orientation=[0,0,0]),conversation=dict(default='talk'))]
    scene['conversations']=[dict(id='talk',speaker='mentor',entry='hello',nodes=[dict(id='hello',
        lines=[dict(text='Speak.')],choices=[dict(text='Fight.',result=1,set_flag='hostile',actions=[behavior_action('mentor'),dict(reward_xp=7)]),dict(text='Leave.',result=2)])])]
    scene['events']=[dict(id='arrival',when='scene_start',actions=[dict(spawn='mentor')]),
        dict(id='angry',when='flag_changed',flag='hostile',is_set=True,once=False,actions=[behavior_action('mentor'),dict(reward_xp=10)]),
        dict(id='calm',when='flag_changed',flag='hostile',is_set=False,once=False,actions=[behavior_action('mentor','npc'),dict(reward_xp=5)])]
    return root


class EffectContracts(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT))

    def valid(self,root):
        result=self.backend.validate(root)
        self.assertTrue(result.valid,[p.message for p in result.problems if p.severity=='ERROR'])
        return result.project

    def test_raw_source_roundtrip_and_lowering_never_rewrites_author_data(self):
        root=source();before=copy.deepcopy(root);campaign=self.valid(root)
        name,code=runtime(campaign,*campaign.scenes[0])
        self.assertEqual(root,before)
        self.assertIn('flagNow',code)
        self.assertIn('ClearActorFlags(THING_AF_NEUTRAL|THING_AF_TALKTO)',code)
        self.assertIn('SetActorFlags(THING_AF_NEUTRAL)',code)
        self.assertIn('case 1: CodexSequence.SetChronicleFlag(0); event3();',code)
        self.assertIn('finishDialogue()',code)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            doc=CampaignDocument(self.backend.ws,copy.deepcopy(root),Path(tmp)/'project.yaml');doc.save()
            self.assertEqual(CampaignDocument.load(self.backend.ws,doc.path).snapshot(),before)

    def test_invalid_flags_presets_goto_and_modal_action_combinations_are_rejected(self):
        mutations=[
            lambda s:s['events'][1].update(flag='missing'),
            lambda s:s['events'][1].update(is_set=1),
            lambda s:s['events'][1].update(flag=[]),
            lambda s:s['events'][1].update(when='scene_start'),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0].update(actions=[]),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0]['actions'][0]['actor_behavior'].update(behavior=[]),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0]['actions'][0]['actor_behavior'].update(paused=True),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0].update(goto='hello'),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0].update(actions=[dict(show_note=dict(title='a',text='b')),dict(start_conversation='talk')]),
            lambda s:s['conversations'][0]['nodes'][0]['choices'][0].update(actions=[dict(jump='home'),dict(reward_xp=5)]),
        ]
        for change in mutations:
            with self.subTest(change=change):
                root=source();change(root['scenes'][0]);self.assertFalse(self.backend.validate(root).valid)
        root=source();root['project_format']=4;self.assertFalse(self.backend.validate(root).valid)

    def test_actor_and_flag_renames_reach_response_actions_and_reactions(self):
        doc=CampaignDocument(self.backend.ws,source())
        doc.rename('actors',0,'renamed');doc.rename_flag('hostile','anger')
        root=doc.snapshot();self.valid(root)
        self.assertEqual(root['scenes'][0]['conversations'][0]['nodes'][0]['choices'][0]['actions'][0]['actor_behavior']['actor'],'renamed')
        self.assertEqual(root['scenes'][0]['events'][1]['flag'],'anger')
        self.assertTrue(any(link.detail[-1:] == ('actor',) and 'choices' in link.detail for link in graph(root)))

    def test_removing_last_response_action_detaches_actions_not_the_choice(self):
        root=source();choice=root['scenes'][0]['conversations'][0]['nodes'][0]['choices'][0]
        choice['actions']=[dict(reward_xp=7)]
        doc=CampaignDocument(self.backend.ws,root)
        path=('scenes',0,'conversations',0,'nodes',0,'choices',0,'actions',0)
        candidate=deletion_plan(doc,path,self.backend).candidate
        answer=candidate['scenes'][0]['conversations'][0]['nodes'][0]['choices'][0]
        self.assertNotIn('actions',answer);self.assertEqual(answer['result'],1);self.valid(candidate)

    def test_actor_deletion_removes_its_response_effect_without_losing_the_response(self):
        root=source();scene=root['scenes'][0]
        other=copy.deepcopy(scene['actors'][0]);other.update(id='guard',name='Guard');other.pop('conversation')
        scene['actors'].append(other)
        scene['conversations'][0]['nodes'][0]['choices'][0]['actions']=[behavior_action('guard')]
        candidate=deletion_plan(CampaignDocument(self.backend.ws,root),('scenes',0,'actors',1),self.backend).candidate
        answer=candidate['scenes'][0]['conversations'][0]['nodes'][0]['choices'][0]
        self.assertNotIn('actions',answer);self.assertEqual(answer['text'],'Fight.');self.valid(candidate)

    def test_note_from_response_is_packaged_and_compiles_against_real_codex(self):
        root=source();root['scenes'][0]['conversations'][0]['nodes'][0]['choices'][0]['actions']=[dict(show_note=dict(title='After reply',text='A note after talking.'))]
        self.valid(root);report=self.backend.build(root)
        self.assertEqual(set(report['class_versions'].values()),{'45.3'})
        notes=[path for path in report['files'] if path.endswith('.ntx')]
        self.assertEqual(len(notes),1)
        note=(ROOT/'build/reply_test/runtime'/notes[0]).read_bytes()
        self.assertIn(b'After reply',note);self.assertIn(b'A note after talking.',note)


class EffectGui(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT));cls.backend.safe_mode=True

    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=CampaignDocument(self.backend.ws,source());self.win.refresh()
        self.path=('conversations',0,'nodes',0,'choices',0)

    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()

    def test_one_click_hostility_is_attached_to_response_and_is_one_undo(self):
        answer=self.win.at(self.path);answer.pop('actions');self.win.changed(True)
        self.win.select(self.path);before=self.win.doc.snapshot()
        self.win.properties.widget().findChild(QPushButton,'answer_make_hostile').click()
        self.assertEqual(answer['actions'],[behavior_action('mentor')])
        self.win.properties.widget().findChild(QPushButton,'answer_make_hostile').click()
        self.assertEqual(answer['actions'],[behavior_action('mentor')])
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)

    def test_response_action_dialog_cancel_edit_and_remove(self):
        self.win.select(self.path);before=self.win.doc.snapshot()
        with patch('rcm.editor.director.edit_actions') as dialog:
            self.win.properties.widget().findChild(QPushButton,'answer_actions').click()
            dialog.assert_called_once();self.assertEqual(self.win.doc.snapshot(),before)
            apply=dialog.call_args.args[2];apply([dict(reward_xp=2)])
        self.assertEqual(self.win.at(self.path)['actions'],[dict(reward_xp=2)])
        with patch('rcm.editor.director.edit_actions') as dialog:
            self.win.properties.widget().findChild(QPushButton,'answer_actions').click();dialog.call_args.args[2]([])
        self.assertNotIn('actions',self.win.at(self.path))

    def test_flag_buttons_create_edit_and_remove_normal_events_without_duplicates(self):
        self.win.doc.data['events'][:]=self.win.doc.data['events'][:1]
        self.win.select(('state','flags','hostile'));before=self.win.doc.snapshot()
        with patch('rcm.editor.director.edit_actions') as dialog:
            self.win.properties.widget().findChild(QPushButton,'flag_on_actions').click()
            self.assertEqual(self.win.doc.snapshot(),before)
            dialog.call_args.args[2]([behavior_action('mentor')])
        event=self.win.doc.data['events'][-1]
        self.assertEqual((event['when'],event['flag'],event['is_set'],event['once']),('flag_changed','hostile',True,False))
        with patch('rcm.editor.director.edit_actions') as dialog:
            edit_flag_reaction(self.win,'hostile',True);dialog.call_args.args[2]([dict(reward_xp=3)])
        self.assertEqual(len(self.win.doc.data['events']),2)
        with patch('rcm.editor.director.edit_actions') as dialog:
            edit_flag_reaction(self.win,'hostile',False);dialog.call_args.args[2]([behavior_action('mentor','npc')])
        self.assertFalse(self.win.doc.data['events'][-1]['is_set'])
        with patch('rcm.editor.director.edit_actions') as dialog:
            edit_flag_reaction(self.win,'hostile',True);dialog.call_args.args[2]([])
        self.assertEqual(len(self.win.doc.data['events']),2)
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)

    def test_switching_to_goto_requires_confirmation_before_removing_actions(self):
        self.win.select(self.path);before=self.win.doc.snapshot()
        combo=self.win.properties.widget().findChild(QComboBox,'answer_mode')
        with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.No):combo.setCurrentIndex(combo.findData('goto'))
        self.assertEqual(self.win.doc.snapshot(),before)
        combo=self.win.properties.widget().findChild(QComboBox,'answer_mode')
        with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):combo.setCurrentIndex(combo.findData('goto'))
        self.assertNotIn('actions',self.win.at(self.path));self.assertNotIn('result',self.win.at(self.path))

    def test_event_preset_ui_and_flag_filter_can_be_edited(self):
        self.win.select(('events',1,'actions',0))
        combo=self.win.properties.widget().findChild(QComboBox,'control_behavior')
        combo.setCurrentIndex(combo.findData('npc'))
        self.assertEqual(self.win.at(('events',1,'actions',0)),behavior_action('mentor','npc'))
        self.win.select(('events',1))
        combo=self.win.properties.widget().findChild(QComboBox,'event_flag_state');combo.setCurrentIndex(combo.findData(False))
        self.assertFalse(self.win.doc.data['events'][1]['is_set'])
        combo=self.win.properties.widget().findChild(QComboBox,'event_when');combo.setCurrentIndex(combo.findData('manual'))
        self.assertNotIn('flag',self.win.doc.data['events'][1]);self.assertNotIn('is_set',self.win.doc.data['events'][1])

    def test_action_picker_defaults_behavior_to_an_npc_and_presets_are_visible(self):
        from rcm.editor.click_actions import ClickActions
        from PySide6.QtWidgets import QLabel
        root=self.win.doc.snapshot();root['scenes'][0]['events'].append(dict(id='draft',when='manual',actions=[dict(reward_xp=1)]))
        controls=ClickActions(self.win,root,len(root['scenes'][0]['events'])-1,QLabel())
        combo=controls.scroll.widget().findChild(QComboBox,'action_kind');combo.setCurrentIndex(combo.findData('actor_behavior'))
        self.assertEqual(controls.event['actions'][0]['actor_behavior']['actor'],'mentor')
        combo=controls.scroll.widget().findChild(QComboBox,'control_behavior');combo.setCurrentIndex(combo.findData('enemy'))
        self.assertEqual(controls.event['actions'][0],behavior_action('mentor'))
        controls.close()


class EffectRuntime(TestCase):
    def test_initial_enabled_flag_does_not_fire_and_once_reactions_stay_once(self):
        root=source();root['scenes'][0]['events'][1]['once']=True
        campaign=Backend(Workspace(ROOT)).validate(root).project
        name=runtime(campaign,*campaign.scenes[0])[0]
        harness='''public class StabilityHarness {
          static void check(boolean ok){if(!ok)throw new AssertionError("flag edges/once");}
          static void tick(SCENE s){for(int i=0;i<3;i++)s.timer(9400,0,0,0,0);}
          public static void main(String[] args){CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);CE.flags[0]=true;
            SCENE s=new SCENE();s.beginscene(1,0);tick(s);check(CE.xp==0);
            CodexSequence.ClearChronicleFlag(0);tick(s);check(CE.xp==5);
            CodexSequence.SetChronicleFlag(0);tick(s);check(CE.xp==15);
            CodexSequence.ClearChronicleFlag(0);tick(s);check(CE.xp==20);
            CodexSequence.SetChronicleFlag(0);tick(s);check(CE.xp==20);
            System.out.println("PASS");}
        }'''.replace('SCENE',name)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            compile_scenario(Path(tmp),campaign,harness)
            run=subprocess.run(['java','-cp',tmp,'StabilityHarness'],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_responses_flags_ai_abort_repeated_state_and_save_restore_with_doubles(self):
        backend=Backend(Workspace(ROOT));result=backend.validate(source());self.assertTrue(result.valid)
        campaign=result.project;name=runtime(campaign,*campaign.scenes[0])[0]
        harness='''public class StabilityHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
          static void tick(SCENE s){for(int i=0;i<3;i++)s.timer(9400,0,0,0,0);}
          public static void main(String[] args){
            CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
            SCENE s=new SCENE();s.beginscene(1,0);tick(s);
            int npc=CodexThing.GuidFromCastID("R_reply_test_s0_mentor");
            check(npc!=0 && CE.world.get(npc).team==10 && (CE.world.get(npc).actorFlags&12)==12,"neutral spawn");
            check(CE.xp==0,"inactive initial flag must not fire");
            s.clicked(npc,1,0);s.convended(1,true,1);tick(s);
            check(!CE.flags[0] && CE.xp==0,"aborted response must not execute");
            s.clicked(npc,1,0);s.convended(99,false,1);check(CE.xp==0,"wrong player");s.convended(1,false,2);tick(s);
            check(CE.xp==0,"other response must not execute");
            s.clicked(npc,1,0);s.convended(1,false,1);
            check(!CE.flags[0] && CE.xp==0,"effects wait for native cleanup");tick(s);
            check(CE.flags[0] && CE.xp==17,"response then flag reaction");
            check(CE.world.get(npc).team==12 && (CE.world.get(npc).actorFlags&12)==0,"enemy needs active non-neutral AI");
            check((CE.world.get(npc).actorFlags&Codex.THING_AF_TALKTO)==0,"hostility must remove conversation cursor");
            CodexSequence.SetChronicleFlag(0);tick(s);check(CE.xp==17,"same flag value cannot retrigger");
            CE.save.clear();s.save(0);CE.read=0;SCENE restored=new SCENE();restored.restore(0);restored.beginscene(1,0);tick(restored);
            check(CE.xp==17,"restore does not replay flag edge");
            CodexSequence.ClearChronicleFlag(0);tick(restored);
            check(CE.xp==22 && CE.world.get(npc).team==10 && (CE.world.get(npc).actorFlags&12)==12,"clear edge and neutral AI");
            check((CE.world.get(npc).actorFlags&Codex.THING_AF_TALKTO)!=0,"neutral dialogue binding becomes interactive again");
            CodexSequence.SetChronicleFlag(0);tick(restored);check(CE.xp==32,"each genuine edge fires once");
            System.out.println("PASS");
          }
        }'''.replace('SCENE',name)
        def flags(text):
            return text.replace('String template;','int actorFlags=0;String template;').replace('int SetActorFlags(int f){return f;}','int SetActorFlags(int f){return CE.world.get(guid).actorFlags|=f;}').replace('int ClearActorFlags(int f){return f;}','int ClearActorFlags(int f){return CE.world.get(guid).actorFlags&=~f;}')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            compile_scenario(Path(tmp),campaign,harness,flags)
            run=subprocess.run(['java','-cp',tmp,'StabilityHarness'],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('PASS',run.stdout)
