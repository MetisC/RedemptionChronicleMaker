"""Widget authoring transactions, references and classification on real resources."""
import shutil,tempfile,unittest
from pathlib import Path
import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QGroupBox,QComboBox,QWizard,QPushButton
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor.dynamic_wizard import DynamicWizard,ActionsDialog

ROOT=Path(__file__).resolve().parents[1]

class DynamicGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');cls.root=Path(cls.temp.name)
        shutil.copytree(ROOT/'cache',cls.root/'cache',ignore=shutil.ignore_patterns('vendor','devtools','textures','meshes','models','toolchain'))
        shutil.copytree(ROOT/'research/original',cls.root/'research/original')
        cls.backend=Backend(Workspace(cls.root));cls.backend.safe_mode=True
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        self.win=MainWindow(self.backend);data=yaml.safe_load((ROOT/'tests/fixtures/chronicles/dynamic_lab/project.yaml').read_text(encoding='utf8'))
        data['project_format']=9;data['scenes'][0].pop('generators');data['scenes'][0]['events']=[]
        path=self.backend.ws.write('project.yaml',source_text(data));self.win.open_path(path);self.win.show();self.app.processEvents()
    def tearDown(self):
        if getattr(self.win,'project_lock',None):self.win.project_lock.release()
        self.win.doc=None;self.win.close();self.app.processEvents()
    def wizard(self,mode='ambush'):
        dialog=DynamicWizard(self.win);dialog.mode.setCurrentIndex(dialog.mode.findData(mode));dialog.points.item(0).setCheckState(Qt.CheckState.Checked);return dialog
    def test_wizard_upgrade_backup_atomic_undo_and_redo(self):
        before=self.win.doc.snapshot();path=self.win.doc.path;disk=path.read_bytes();dialog=self.wizard();dialog.accept();self.app.processEvents()
        self.assertEqual(dialog.result(),dialog.DialogCode.Accepted,dialog.error.text());self.assertEqual(self.win.doc.campaign['project_format'],10)
        self.assertEqual(path.read_bytes(),disk);self.assertTrue(any(self.backend.ws.output('backups/dyn_lab').glob('*.yaml')))
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before);self.win.redo_project();self.assertEqual(self.win.doc.campaign['project_format'],10)
    def test_cancel_and_invalid_wizard_do_not_modify_project(self):
        before=self.win.doc.snapshot();dialog=self.wizard();dialog.reject();self.assertEqual(self.win.doc.snapshot(),before)
        dialog=self.wizard();dialog.points.item(0).setCheckState(Qt.CheckState.Unchecked);dialog.accept();self.assertNotEqual(dialog.result(),dialog.DialogCode.Accepted);self.assertEqual(self.win.doc.snapshot(),before)
    def test_modes_presets_and_advanced_collapsed(self):
        for mode in ('ambush','waves','continuous','reinforcements','boss'):
            dialog=self.wizard(mode);self.assertFalse(dialog.findChild(QGroupBox,'dynamic_advanced').isChecked());candidate=dialog.preview_source()
            if mode=='reinforcements':self.assertEqual(dialog.start.currentData(),'manual')
            self.assertTrue(self.backend.validate(candidate).valid,[(p.severity,p.message) for p in self.backend.validate(candidate).problems]);dialog.reject()
    def test_quick_creation_uses_one_waypoint_and_cancel_is_clean(self):
        before=self.win.doc.snapshot();dialog=DynamicWizard(self.win,position=[-62,-768,384]);dialog.accept();self.app.processEvents()
        self.assertEqual(dialog.result(),dialog.DialogCode.Accepted,dialog.error.text());scene=self.win.doc.campaign['scenes'][0]
        self.assertEqual(len(scene['waypoints']),len(before['scenes'][0]['waypoints'])+1);self.assertEqual(scene['generators'][0]['spawn_points'],[dialog.new_point['id']]);self.assertTrue(scene['triggers'])
    def test_shared_action_editor_does_not_mutate_the_open_document(self):
        before=self.win.doc.snapshot();wizard=self.wizard('boss');dialog=ActionsDialog(self.win,wizard.preview_source(),[{'start_generator':wizard.ident+'_adds'}]);dialog.show();self.app.processEvents()
        combo=dialog.scroll.widget().findChild(QComboBox,'action_kind');self.assertIsNotNone(combo);combo.setCurrentIndex(combo.findData('reward_xp'));self.app.processEvents();dialog.accept()
        self.assertEqual(self.win.doc.snapshot(),before);self.assertEqual(next(iter(dialog.actions[0])),'reward_xp');dialog.close();wizard.reject()
    def test_enemy_filter_uses_original_taxonomy_and_real_properties(self):
        from rcm.enemy_catalogue import catalogue
        result=catalogue(self.backend);self.assertTrue(result['Rat']['enemy']);self.assertFalse(result['businessWoman']['enemy']);self.assertEqual(result['Rat']['health'],20);self.assertEqual(result['Rat']['max_health'],20)
        from rcm.editor.browser import ResourceDialog
        dialog=ResourceDialog(self.backend,'actors');dialog.browser.enemies.setCurrentIndex(1)
        names=[dialog.browser.table.item(i,0).text() for i in range(dialog.browser.table.rowCount())]
        self.assertIn('Rat',names);self.assertNotIn('businessWoman',names);dialog.close()
    def test_references_safe_delete_rename_and_duplicate(self):
        dialog=self.wizard();dialog.accept();self.app.processEvents();root=self.win.doc.campaign;scene=root['scenes'][0];key=scene['generators'][0]['id']
        from rcm.safe_edit import delete_candidate
        with self.assertRaisesRegex(ValueError,'referencias'):delete_candidate(self.win.doc,('scenes',0,'waypoints',0),self.backend)
        with self.assertRaisesRegex(ValueError,'referencias'):delete_candidate(self.win.doc,('scenes',0,'generators',0),self.backend)
        self.win.doc.rename('waypoints',0,'point_renamed');self.assertEqual(scene['generators'][0]['spawn_points'],['point_renamed'])
        self.win.doc.rename('generators',0,'renamed');self.assertTrue(any(a.get('start_generator')=='renamed' for e in scene['events'] for a in e['actions']))
        self.win.campaign_panel.path=('scenes',0,'generators',0);self.win.campaign_panel.duplicate();self.assertEqual(len(scene['generators']),2)
        clone=scene['generators'][1];self.assertNotEqual(clone['id'],key);self.assertFalse(any(a.get('start_generator')==clone['id'] for e in scene['events'] for a in e['actions']))
    def test_save_reload_does_not_downgrade_when_adding_markers(self):
        dialog=self.wizard();dialog.accept();self.app.processEvents();self.win.campaign_panel.enable_authoring9();self.assertEqual(self.win.doc.campaign['project_format'],10)
        self.win.save_project();source=Document.load(self.backend.ws,self.win.doc.path).snapshot();self.assertEqual(source,self.win.doc.snapshot())
    def test_trace_navigation_and_graph_projection(self):
        dialog=self.wizard();dialog.accept();self.app.processEvents();key=self.win.doc.campaign['scenes'][0]['generators'][0]['id']
        from rcm.debugging import parse_trace
        row=parse_trace('GENERATOR_SPAWN generator='+key+' scene=lab role=enemy guid=100')['events'][0];self.assertEqual(row['context'],{'scene':'lab','generator':key})
        panel=self.win.graph_panel;self.win.center_tabs.setCurrentWidget(panel);panel.kind.setCurrentIndex(panel.kind.findData('generators'));panel.refresh();self.assertGreater(len(panel.scene.items()),0)
        self.assertTrue(panel.findChild(QPushButton,'graph_add_node').isHidden())
        panel.kind.setCurrentIndex(panel.kind.findData('conversations'));panel.refresh();self.assertFalse(panel.findChild(QPushButton,'graph_add_node').isHidden())
        self.assertEqual(self.win.center_tabs.count(),7)
    def test_health_condition_units_and_callback_fields_are_authorable(self):
        dialog=self.wizard('boss');dialog.accept();self.app.processEvents();scene=self.win.doc.campaign['scenes'][0];gen=scene['generators'][0]
        scene['events'].append({'id':'health','when':'state_changed','conditions':[{'actor_health':{'generator':gen['id'],'role':'boss','comparison':'<=','percent':50}}],'actions':[{'pause_generator':gen['id']}]})
        index=len(scene['events'])-1;self.win.select(('events',index,'conditions',0));self.app.processEvents()
        unit=self.win.properties.widget().findChild(QComboBox,'health_unit');self.assertIsNotNone(unit);unit.setCurrentIndex(unit.findData('value'));self.app.processEvents()
        self.assertEqual(scene['events'][index]['conditions'][0]['actor_health']['value'],50)
        self.win.select(('events',index));self.app.processEvents();combo=self.win.properties.widget().findChild(QComboBox,'event_when');combo.setCurrentIndex(combo.findData('wave_complete'));self.app.processEvents()
        self.assertEqual(scene['events'][index]['generator'],gen['id']);self.assertIsNotNone(self.win.properties.widget().findChild(QComboBox,'event_generator'))
        combo=self.win.properties.widget().findChild(QComboBox,'event_when');combo.setCurrentIndex(combo.findData('timer'));self.app.processEvents();self.assertNotIn('generator',scene['events'][index])
    def test_boss_actions_self_references_rewire_on_duplicate(self):
        dialog=self.wizard('boss');dialog.accept();self.app.processEvents();scene=self.win.doc.campaign['scenes'][0];g=scene['generators'][0];g['phases'][0]['actions']=[{'pause_generator':g['id']}]
        self.win.campaign_panel.path=('scenes',0,'generators',0);self.win.campaign_panel.duplicate();clone=scene['generators'][-1]
        self.assertEqual(clone['phases'][0]['actions'],[{'pause_generator':clone['id']}]);self.assertEqual(g['phases'][0]['actions'],[{'pause_generator':g['id']}])
    def test_malformed_dynamic_drafts_fail_before_widgets(self):
        from rcm.campaign_document import CampaignDocument
        import copy
        data=yaml.safe_load((ROOT/'tests/fixtures/chronicles/dynamic_lab/project.yaml').read_text(encoding='utf8'))
        for edit in [lambda g:g.update(mode='unknown'),lambda g:g.update(waves=[{'groups':[3]}]),lambda g:g.update(phases=[{'id':'bad','actions':'wrong'}]),lambda g:g.update(boss=3),lambda g:g.update(spawn_points=3)]:
            candidate=copy.deepcopy(data);edit(candidate['scenes'][0]['generators'][0])
            with self.assertRaises(ValueError):CampaignDocument.load_data(self.backend.ws,candidate,self.backend.ws.output('bad.yaml'))
    def test_edit_existing_generator_keeps_activation_and_completion_callbacks(self):
        dialog=self.wizard();dialog.completion=[{'reward_xp':3}];dialog.accept();self.app.processEvents()
        scene=self.win.doc.campaign['scenes'][0];g=scene['generators'][0];before=len(scene['events'])
        edit=DynamicWizard(self.win,g['id']);edit.quantity.setValue(5);edit.accept();self.app.processEvents()
        self.assertEqual(edit.result(),edit.DialogCode.Accepted,edit.error.text());self.assertEqual(len(scene['events']),before)
        scene=self.win.doc.campaign['scenes'][0];self.assertEqual(scene['generators'][0]['waves'][0]['groups'][0]['count'],5)
        self.assertEqual(len(scene['events']),before)
        self.assertEqual([e['actions'] for e in scene['events'] if e.get('when')=='generator_complete'],[[{'reward_xp':3}]])
        self.assertTrue(self.backend.validate(self.win.doc.snapshot()).valid)
    def test_wizard_footer_visible_and_clickable_on_every_page(self):
        dialog=self.wizard('boss');dialog.resize(760,580);dialog.show();self.app.processEvents()
        for i in range(4):
            kind=QWizard.WizardButton.NextButton if i<3 else QWizard.WizardButton.FinishButton
            for button_kind in (kind,QWizard.WizardButton.CancelButton):
                button=dialog.button(button_kind);self.assertTrue(button.isVisible());self.assertTrue(dialog.rect().contains(button.mapTo(dialog,button.rect().bottomRight())))
            if i<3:dialog.button(kind).click();self.app.processEvents();self.assertEqual(dialog.currentId(),i+1)
        dialog.reject()
