"""Resuming an AI preserves allegiance; explicit hostility changes it."""
import copy
import os
from pathlib import Path
import subprocess
import tempfile
from unittest import TestCase

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QPushButton
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.editor import i18n
from rcm.editor.click_actions import ClickActions
from rcm.editor.dialogue_actions import behavior_action
from rcm.editor.window import MainWindow
from rcm.paths import Workspace
from rcm.service import Backend
from test_dialogue_effects import source
from test_stability_revision import compile_scenario

ROOT = Path(__file__).resolve().parents[1]


class HostilityControls(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT))
        cls.backend.safe_mode = True

    def setUp(self):
        self.win = MainWindow(self.backend)
        root = source()
        root['scenes'][0]['events'][1]['actions'] = [dict(enable_ai='mentor')]
        self.win.doc = CampaignDocument(self.backend.ws, root)
        self.win.refresh()
        self.path = ('events', 1, 'actions', 0)

    def tearDown(self):
        self.win.doc = None
        self.win.close()
        self.app.processEvents()

    def test_inspecting_resume_does_not_change_data_and_conversion_is_one_undo(self):
        before = self.win.doc.snapshot()
        self.win.select(self.path)
        self.assertEqual(self.win.doc.snapshot(), before)
        self.win.properties.widget().findChild(QPushButton, 'ai_make_hostile').click()
        self.assertEqual(self.win.at(self.path), behavior_action('mentor'))
        self.assertEqual(self.win.selection, self.path)
        self.win.undo_project()
        self.assertEqual(self.win.doc.snapshot(), before)

    def test_conversion_in_response_and_flag_action_drafts_stays_transactional(self):
        before = self.win.doc.snapshot()
        controls = ClickActions(self.win, copy.deepcopy(before), 1, QLabel())
        controls.scroll.widget().findChild(QPushButton, 'ai_make_hostile').click()
        self.assertEqual(controls.event['actions'], [behavior_action('mentor')])
        self.assertTrue(controls.commit())
        self.assertEqual(self.win.doc.snapshot(), before)
        controls.close()

    def test_conversion_waits_for_target_and_keeps_the_selected_actor(self):
        root = self.win.doc.snapshot()
        root['scenes'][0]['actors'].append(dict(id='gator', name='Crocodile', template='alligator',
            transform=dict(position=[0, 0, 384], orientation=[0, 0, 0])))
        root['scenes'][0]['events'][1]['actions'] = [dict(enable_ai='')]
        controls = ClickActions(self.win, root, 1, QLabel())
        button = controls.scroll.widget().findChild(QPushButton, 'ai_make_hostile')
        self.assertFalse(button.isEnabled())
        target = controls.scroll.widget().findChild(QComboBox, 'action_target')
        target.setCurrentIndex(target.findData('gator'))
        self.assertTrue(button.isEnabled())
        button.click()
        self.assertEqual(controls.event['actions'], [behavior_action('gator')])
        controls.close()

    def test_new_behavior_action_defaults_to_real_hostility_but_old_advanced_data_stays(self):
        root = self.win.doc.snapshot()
        controls = ClickActions(self.win, copy.deepcopy(root), 1, QLabel())
        kind = controls.scroll.widget().findChild(QComboBox, 'action_kind')
        kind.setCurrentIndex(kind.findData('actor_behavior'))
        self.assertEqual(controls.event['actions'], [behavior_action('mentor')])
        controls.close()
        root['scenes'][0]['events'][1]['actions'] = [dict(actor_behavior=dict(actor='mentor', team=12, paused=False))]
        controls = ClickActions(self.win, copy.deepcopy(root), 1, QLabel())
        self.assertEqual(controls.scroll.widget().findChild(QComboBox, 'control_behavior').currentData(), '')
        self.assertEqual(controls.doc.snapshot(), root)
        controls.close()

    def test_resume_explanation_and_action_names_are_available_in_both_languages(self):
        old = i18n._language
        try:
            for language, fragment in [('es', 'conserva el bando'), ('en', 'allegiance and neutrality')]:
                i18n._language = language
                self.win.select(self.path)
                labels = [label.text() for label in self.win.properties.widget().findChildren(QLabel)]
                self.assertTrue(any(fragment in label for label in labels), labels)
        finally:
            i18n._language = old


class AlligatorHostility(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend = Backend(Workspace(ROOT))

    def scenario(self, route):
        root = source()
        scene = root['scenes'][0]
        scene['actors'][0]['template'] = 'alligator'
        choices = scene['conversations'][0]['nodes'][0]['choices']
        choices[1]['actions'] = [dict(enable_ai='mentor')]
        choices[0]['actions'] = [behavior_action('mentor')] if route != 'flag' else []
        if not choices[0]['actions']:choices[0].pop('actions')
        scene['events'][1]['actions'] = [behavior_action('mentor')]
        if route == 'response':scene['events'].pop(1)
        return root

    def test_alligator_keeps_original_ai_and_hostility_compiles_against_codex(self):
        root = self.scenario('both')
        root['chronicle']['id'] = 'gator_ai'
        report = self.backend.build(root)
        self.assertEqual(set(report['class_versions'].values()), {'45.3'})
        original = next(t for t in self.backend.resources['templates'] if t['id'] == 'alligator')
        self.assertEqual(original['ai'], 'enemyGhoulAlligator.nai')

    def test_response_flag_and_combined_routes_remove_neutrality_after_dialogue_cleanup(self):
        for route in ('response', 'flag', 'both'):
            with self.subTest(route=route):
                validation = self.backend.validate(self.scenario(route))
                self.assertTrue(validation.valid)
                campaign = validation.project
                name = runtime(campaign, *campaign.scenes[0])[0]
                harness = '''public class StabilityHarness {
                  static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
                  static void tick(SCENE s){for(int i=0;i<3;i++)s.timer(9400,0,0,0,0);}
                  public static void main(String[] args){
                    CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);
                    SCENE s=new SCENE();s.beginscene(1,0);tick(s);
                    int g=CodexThing.GuidFromCastID("R_reply_test_s0_mentor");
                    check(CE.world.get(g).team==10,"starts peaceful");
                    s.clicked(g,1,0);s.convended(1,false,2);tick(s);
                    check(CE.world.get(g).team==10,"resume must preserve team");
                    check((CE.world.get(g).actorFlags&Codex.THING_AF_NEUTRAL)!=0,"resume must preserve neutrality");
                    check((CE.world.get(g).actorFlags&Codex.THING_AF_AIPAUSED)==0,"resume must clear pause");
                    s.clicked(g,1,0);s.convended(1,false,1);
                    check(CE.world.get(g).team==10,"effects wait for dialogue cleanup");tick(s);
                    check(CE.world.get(g).team==12,"hostile enemy team");
                    check((CE.world.get(g).actorFlags&(Codex.THING_AF_NEUTRAL|Codex.THING_AF_AIPAUSED|Codex.THING_AF_TALKTO))==0,"hostile active actor with no talk cursor");
                    System.out.println("PASS");
                  }}'''.replace('SCENE', name)
                def flags(text):
                    return text.replace('String template;', 'int actorFlags=0;String template;').replace('int SetActorFlags(int f){return f;}', 'int SetActorFlags(int f){return CE.world.get(guid).actorFlags|=f;}').replace('int ClearActorFlags(int f){return f;}', 'int ClearActorFlags(int f){return CE.world.get(guid).actorFlags&=~f;}')
                with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                    compile_scenario(Path(tmp), campaign, harness, flags)
                    run = subprocess.run(['java', '-cp', tmp, 'StabilityHarness'], capture_output=True, text=True, timeout=30)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    self.assertIn('PASS', run.stdout)
