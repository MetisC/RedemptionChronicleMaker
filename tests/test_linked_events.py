"""Contextual event authoring with real Qt, ordinary source data and Codex builds."""
import copy,json,os,tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QPushButton,QComboBox,QDialogButtonBox,QMessageBox,QMenu,QLineEdit,QPlainTextEdit
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor import linked_events as api
from rcm.editor.dialogue_actions import edit_flag_reaction
from test_dialogue_effects import source

ROOT=Path(__file__).resolve().parents[1]


def world():
    root=source();root['chronicle']['id']='link_test';scene=root['scenes'][0]
    guard=copy.deepcopy(scene['actors'][0]);guard.update(id='guard',name='Guard',behavior='enemy');guard.pop('conversation');scene['actors'].append(guard)
    scene['objects']=[dict(id='letter',name='Letter',template='ledger',quest_item=True,transform=dict(position=[10,20,30],orientation=[0,0,0])),
                      dict(id='barrel',name='Barrel',template='barrel1',transform=dict(position=[40,20,30],orientation=[0,0,0]))]
    scene['triggers']=[dict(id='zone',name='Zone',shape='sphere',radius=100,once=False,transform=dict(position=[10,20,30],orientation=[0,0,0]))]
    scene['sequences']=[dict(id='film',name='Film',actor='mentor',duration=1,shot='wide',angle='high',steps=[dict(at=0,actor='mentor',preset='full')])]
    scene['encounters']=[dict(id='guards',name='Guards',actors=['guard'])]
    root['quests']=[dict(id='task',title='Task',description='An errand',steps=['Find it','Return it'],reward_xp=0)]
    return root


class LinkedEvents(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT));cls.backend.safe_mode=True

    def setUp(self):
        self.win=MainWindow(self.backend);self.win.autosave_timer.stop();self.win.doc=CampaignDocument(self.backend.ws,world());self.win.refresh()

    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()

    def valid(self):
        result=self.backend.validate(self.win.doc.snapshot());self.assertTrue(result.valid,[p.message for p in result.problems if p.severity=='ERROR'])

    def spec(self,path,key=None):
        specs=api.available(self.win,path)
        return next(s for s in specs if s.key==key) if key else specs[0]

    def write(self,spec,actions=None):
        def change(win,event,reaction):
            event=copy.deepcopy(event)
            event['actions']=copy.deepcopy(actions if actions is not None else [dict(reward_xp=3)]);return event
        with patch.object(api,'edit_dialog',side_effect=change):api.edit(self.win,spec)

    def test_every_supported_origin_creates_valid_ordinary_events_and_reuses_them(self):
        paths=[('level',),('actors',0),('objects',0),('objects',1),('triggers',0),('conversations',0),('scenes',0,'sequences',0),('scenes',0,'encounters',0),('quests',0)]
        self.valid()
        for path in paths:
            for spec in api.available(self.win,path):
                with self.subTest(path=path,key=spec.key):
                    self.write(spec);self.valid();count=len(self.win.doc.data['events']);before=self.win.doc.snapshot()
                    self.write(spec);self.assertEqual(len(self.win.doc.data['events']),count);self.assertEqual(self.win.doc.snapshot(),before)
                    self.assertTrue(api.matching(self.win.doc.data['events'],spec))
        self.assertEqual(api.available(self.win,('state','flags')),[])
        self.assertEqual(api.available(self.win,('original',0)),[])

    def test_edit_cancel_noop_remove_and_single_undo_preserve_selection_and_data(self):
        spec=self.spec(('actors',0));before=self.win.doc.snapshot();selection=self.win.selection
        with patch.object(api,'edit_dialog',return_value=None):api.edit(self.win,spec)
        self.assertEqual(self.win.doc.snapshot(),before)
        self.write(spec);self.assertEqual(self.win.selection,selection)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)
        self.win.redo_project();self.write(spec,[]);self.assertEqual(self.win.doc.snapshot(),before)

    def test_existing_filters_conditions_and_once_are_kept_and_navigable(self):
        event=dict(id='after_talk',when='conversation_ended',conversation='talk',result=2,once=True,conditions=[dict(flag='hostile',is_set=False)],actions=[dict(reward_xp=1)])
        self.win.doc.data['events'].append(event);self.win.changed(True);spec=self.spec(('conversations',0))
        self.write(spec,[dict(reward_xp=4)])
        self.assertEqual((event['result'],event['once'],event['conditions']),(2,True,[dict(flag='hostile',is_set=False)]))
        api.open_event(self.win,spec);self.assertEqual(self.win.selection,('events',3));self.assertEqual(self.win.center_tabs.currentIndex(),1)
        self.assertIn('result=2',api.event_label(event));self.valid()

    def test_multiple_existing_routes_are_chosen_without_creating_duplicates(self):
        self.win.doc.data['events'] += [dict(id='a',when='actor_killed',actor='mentor',actions=[dict(reward_xp=1)]),dict(id='b',when='actor_killed',actor='mentor',conditions=[dict(flag='hostile',is_set=True)],actions=[dict(reward_xp=2)])]
        spec=self.spec(('actors',0));before=self.win.doc.snapshot()
        with patch.object(api.QInputDialog,'getItem',return_value=('',False)):self.write(spec)
        self.assertEqual(self.win.doc.snapshot(),before)
        label=api.event_label(self.win.doc.data['events'][-1])
        with patch.object(api.QInputDialog,'getItem',return_value=(label,True)):self.write(spec)
        self.assertEqual(len(self.win.doc.data['events']),5);self.assertEqual(self.win.doc.data['events'][-2]['actions'],[dict(reward_xp=1)]);self.assertEqual(self.win.doc.data['events'][-1]['actions'],[dict(reward_xp=3)])

    def test_referenced_event_cannot_be_silently_deleted_by_removing_its_actions(self):
        spec=self.spec(('actors',0));self.write(spec);ident=self.win.doc.data['events'][-1]['id']
        self.win.doc.data['events'].append(dict(id='caller',when='manual',actions=[dict(run_event=ident)]));self.win.changed(True);before=self.win.doc.snapshot()
        with patch.object(QMessageBox,'information') as notice:self.write(spec,[])
        notice.assert_called_once();self.assertEqual(self.win.doc.snapshot(),before);self.valid()

    def test_renaming_origin_before_editing_resolves_the_current_identifier(self):
        spec=self.spec(('actors',0));self.win.select(('actors',0))
        field=self.win.properties.widget().findChild(QLineEdit,'actor_id');field.setText('renamed')
        self.write(spec);self.assertEqual(self.win.doc.data['events'][-1]['actor'],'renamed');self.valid()

    def test_all_surfaces_offer_context_controls_and_keep_the_active_scene(self):
        for path in [('level',),('actors',0),('objects',0),('triggers',0),('conversations',0)]:
            self.win.select(path);panel=self.win.properties.widget().findChild(QComboBox,'linked_when');self.assertIsNotNone(panel,path)
            self.assertIsNotNone(self.win.properties.widget().findChild(QPushButton,'linked_edit'))
            menu=QMenu();api.context_menu(self.win,menu,path);self.assertTrue(menu.actions());menu.close()
        for path in [('quests',0),('scenes',0,'encounters',0),('scenes',0,'sequences',0)]:
            self.win.campaign_panel.navigate(path);self.assertIsNotNone(self.win.campaign_panel.scroll.widget().findChild(QComboBox,'linked_when'),path)
        self.assertEqual(self.win.doc.active,0)
        self.assertEqual(api.available(self.win,('scenes',1,'sequences',0)),[])
        self.win.doc.campaign['scenes'][0]['sequences'][0].pop('steps');self.assertEqual(api.available(self.win,('sequences',0)),[])
        self.win.doc.data['triggers'][0]['native_script']='OwnedByScript';self.assertEqual(api.available(self.win,('triggers',0)),[])
        self.win.doc.campaign['project_format']=5;self.assertEqual(api.available(self.win,('actors',0)),[])

    def test_real_dialog_applies_pending_text_extra_conditions_and_once_atomically(self):
        spec=self.spec(('quests',0),'complete');before=self.win.doc.snapshot();exceptions=[]
        def interact():
            dialog=self.app.activeModalWidget()
            try:
                actions=dialog.findChild(api.ClickActions,'linked_actions');conditions=dialog.findChild(api.ClickActions,'linked_conditions')
                self.assertEqual(dialog.findChild(api.QCheckBox,'linked_show_conditions').text(),api.tr('Mostrar condiciones adicionales'))
                actions.add();text=actions.scroll.widget().findChild(QPlainTextEdit,'note_text');text.setPlainText('A reward note.\nA second paragraph.')
                conditions.add();once=dialog.findChild(api.QCheckBox,'linked_once');once.setChecked(False)
                self.assertEqual(self.win.doc.snapshot(),before)
                dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok).click()
                self.assertEqual(dialog.result(),dialog.DialogCode.Accepted,dialog.findChildren(api.QLabel)[-1].text())
            except Exception as exc:exceptions.append(exc);dialog.reject()
        QTimer.singleShot(0,interact);api.edit(self.win,spec)
        if exceptions:raise exceptions[0]
        event=self.win.doc.data['events'][-1]
        self.assertEqual(event['conditions'],[dict(quest='task',state='complete'),dict(flag='hostile',is_set=True)])
        self.assertFalse(event['once']);self.assertEqual(event['actions'][0]['show_note']['text'],'A reward note.\nA second paragraph.');self.valid()
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)

    def test_real_dialog_cancel_and_unchanged_ok_do_not_modify_source(self):
        spec=self.spec(('actors',0));self.write(spec);event=self.win.doc.data['events'][-1];event.pop('once');event['conditions']=[];before=self.win.doc.snapshot()
        for accept in (False,True):
            def interact():
                dialog=self.app.activeModalWidget();button=QDialogButtonBox.StandardButton.Ok if accept else QDialogButtonBox.StandardButton.Cancel
                dialog.findChild(QDialogButtonBox).button(button).click()
            QTimer.singleShot(0,interact);api.edit(self.win,spec);self.assertEqual(self.win.doc.snapshot(),before)

    def test_required_quest_condition_keeps_its_order_and_invalid_draft_cannot_apply(self):
        spec=self.spec(('quests',0),'complete');self.write(spec)
        event=self.win.doc.data['events'][-1];event['conditions'].insert(0,dict(flag='hostile',is_set=True));before=self.win.doc.snapshot();exceptions=[]
        def interact():
            dialog=self.app.activeModalWidget()
            try:
                actions=dialog.findChild(api.ClickActions,'linked_actions');buttons=dialog.findChild(QDialogButtonBox)
                actions.event['actions']=[dict(start_conversation='missing')]
                buttons.button(QDialogButtonBox.StandardButton.Ok).click();self.assertEqual(dialog.result(),dialog.DialogCode.Rejected)
                self.assertEqual(self.win.doc.snapshot(),before)
                actions.event['actions']=[dict(reward_xp=3)];buttons.button(QDialogButtonBox.StandardButton.Ok).click()
                self.assertEqual(dialog.result(),dialog.DialogCode.Accepted)
            except Exception as error:exceptions.append(error);dialog.reject()
        QTimer.singleShot(0,interact);api.edit(self.win,spec)
        if exceptions:raise exceptions[0]
        self.assertEqual(self.win.doc.snapshot(),before)

    def test_flag_alias_pending_edit_and_referenced_empty_reaction_are_safe(self):
        self.win.select(('state','flags','hostile'));self.win.properties.widget().findChild(QLineEdit,'flag_alias').setText('angry')
        with patch('rcm.editor.director.edit_actions') as editor:edit_flag_reaction(self.win,'hostile',True);editor.call_args.args[2]([dict(reward_xp=1)])
        self.assertEqual(self.win.doc.data['events'][1]['flag'],'angry')
        self.win.doc.data['events'].append(dict(id='caller',when='manual',actions=[dict(run_event='angry')]))
        self.win.changed(True);before=self.win.doc.snapshot()
        with patch('rcm.editor.director.edit_actions') as editor,patch.object(QMessageBox,'information') as notice:
            edit_flag_reaction(self.win,'angry',True);editor.call_args.args[2]([])
        notice.assert_called_once();self.assertEqual(self.win.doc.snapshot(),before);self.valid()

    def test_callback_links_compile_against_real_codex_and_survive_save_reopen(self):
        for path in [('level',),('actors',0),('objects',0),('triggers',0),('conversations',0),('scenes',0,'sequences',0),('scenes',0,'encounters',0),('quests',0)]:
            for spec in api.available(self.win,path):self.write(spec)
        self.valid();report=self.backend.build(self.win.doc.snapshot());self.assertEqual(set(report['class_versions'].values()),{'45.3'})
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            self.win.doc.save(Path(tmp)/'project.yaml');self.assertEqual(Document.load(self.backend.ws,self.win.doc.path).snapshot(),self.win.doc.snapshot())

    def test_dynamic_callbacks_are_exposed_only_for_format_ten(self):
        root=json.loads(json.dumps(__import__('yaml').safe_load((ROOT/'tests/fixtures/chronicles/dynamic_lab/project.yaml').read_text(encoding='utf8'))))
        self.win.doc=CampaignDocument(self.backend.ws,root);self.win.refresh()
        specs=api.available(self.win,('generators',0));self.assertEqual(len(specs),5)
        for spec in specs:self.write(spec);self.valid()
        self.assertEqual({s.when for s in specs},{'generator_started','wave_started','wave_complete','generator_complete','generator_stopped'})
        self.win.doc.campaign['project_format']=9;self.assertEqual(api.available(self.win,('generators',0)),[])
