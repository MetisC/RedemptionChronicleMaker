"""Qt authoring contracts. Headless controls do not attest spatial/native UX."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QLineEdit,QComboBox,QDoubleSpinBox,QTreeWidgetItem
from PySide6.QtCore import Qt
from rcm.editor.window import MainWindow,NewProjectDialog
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.document import Document
from rcm.campaign_document import CampaignDocument
from test_phase9 import modern
ROOT=Path(__file__).resolve().parents[1]

class Phase9GuiTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):self.w=MainWindow(self.backend)
    def tearDown(self):self.w.doc=None;self.w.close();self.app.processEvents()
    def test_new_project_is_campaign_and_resource_upgrade_keeps_version_and_data(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            dialog=NewProjectDialog(self.backend.ws);dialog.pid.setText('p9_ui');dialog.name.setText('Nueva campaña');dialog.directory.setText(tmp)
            self.w.create_project(dialog);self.assertIsInstance(self.w.doc,CampaignDocument);self.assertEqual(self.w.doc.campaign['project_format'],9)
            self.w.doc.campaign['resources']={'templates':[{'id':'T_own','base':'businessWoman','properties':{}}]}
            self.w.project_resources_panel.upgrade();self.assertEqual(self.w.doc.campaign['resources']['templates'][0]['id'],'T_own');self.assertEqual(self.w.doc.campaign['project_format'],9)
            self.w.save_project();self.assertEqual(Document.load(self.backend.ws,self.w.doc.path).snapshot(),self.w.doc.snapshot())
    def test_marker_edit_undo_and_named_transition_selectors(self):
        self.w.doc=CampaignDocument(self.backend.ws,modern());self.w.refresh()
        self.w.add_spatial_entity('entries','',[20,30,40]);self.assertEqual(self.w.selection,('entries',1))
        panel=self.w.properties.widget();panel.findChild(QDoubleSpinBox,'position_x').setValue(44);self.assertEqual(self.w.doc.data['entries'][1]['transform']['position'][0],44)
        self.w.history_time=0;panel.findChild(QDoubleSpinBox,'orientation_2').setValue(90);self.w.undo_project();self.assertEqual(self.w.doc.data['entries'][1]['transform']['orientation'][2],0)
        s=self.w.doc.data;ei=len(s['events'])-1;ai=len(s['events'][ei]['actions'])-1;self.w.select(('events',ei,'actions',ai))
        panel=self.w.properties.widget();self.assertEqual(panel.findChild(QComboBox,'travel_scene').currentData(),'west');self.assertEqual(panel.findChild(QComboBox,'travel_entry').currentData(),'safe')
    def test_path_controls_and_delete_protects_references(self):
        self.w.doc=CampaignDocument(self.backend.ws,modern());self.w.refresh();self.w.campaign_panel.navigate(('scenes',0,'paths',0))
        field=self.w.campaign_panel.findChild(QLineEdit,'path_name');field.setText('Ruta editada');self.w.commit_properties();self.assertEqual(self.w.doc.campaign['scenes'][0]['paths'][0]['name'],'Ruta editada')
        combo=self.w.campaign_panel.findChild(QComboBox,'path_loop');combo.setCurrentIndex(combo.findData(True));self.assertTrue(self.w.doc.campaign['scenes'][0]['paths'][0]['loop'])
        from rcm.safe_edit import delete_candidate
        with self.assertRaises(ValueError):delete_candidate(self.w.doc,('scenes',0,'waypoints',0),self.backend)
    def test_debug_format9_navigation_to_action_conversation_and_quest(self):
        self.w.doc=CampaignDocument(self.backend.ws,modern());self.w.refresh();panel=self.w.debug_panel
        self.assertTrue(panel.enabled.isEnabled());panel.enabled.setChecked(False);self.assertFalse(self.w.doc.campaign['build_options']['debug'])
        for context,selection in [({'scene':'london','event':'finish','action':1},('events',len(self.w.doc.data['events'])-1,'actions',0)),({'scene':'london','conversation':'intro'},('conversations',0))]:
            item=QTreeWidgetItem();item.setData(0,Qt.ItemDataRole.UserRole,context);panel.navigate(item,0);self.assertEqual(self.w.selection,selection)
        item=QTreeWidgetItem();item.setData(0,Qt.ItemDataRole.UserRole,{'quest':'mission'});panel.navigate(item,0);self.assertEqual(self.w.campaign_panel.path,('quests',0))
