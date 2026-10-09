"""GUI campaign regressions: one source across scenes, undo and unconfirmed fields."""
import os,sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')];os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication,QLineEdit,QComboBox,QPushButton,QMessageBox
from rcm.editor.window import MainWindow
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from rcm.paths import Workspace
from rcm.service import Backend
from test_campaign import source
class CampaignEditorTests(TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
 def setUp(self):
  self.w=MainWindow(self.backend);self.w.doc=CampaignDocument(self.backend.ws,source());self.w.doc.path=ROOT/'build/tests/campaign_ui.yaml';self.w.refresh();self.w.campaign_panel.navigate(('quests',0))
 def tearDown(self):self.w.doc=None;self.w.close();self.app.processEvents()
 def test_save_commits_quest_title_without_focus_change(self):
  field=self.w.campaign_panel.findChild(QLineEdit,'quest_title');field.setText('Título pendiente');self.w.actions['save'].trigger();self.app.processEvents();d=Document.load(self.backend.ws,self.w.doc.path);self.assertEqual(d.campaign['quests'][0]['title'],'Título pendiente')
 def test_quest_undo_rebinds_controls_to_restored_source(self):
  panel=self.w.campaign_panel;panel.findChild(QPushButton,'add_quest_step').click();self.assertEqual(len(self.w.doc.campaign['quests'][0]['steps']),4);self.w.undo_project();self.assertEqual(len(self.w.doc.campaign['quests'][0]['steps']),3)
  panel.findChild(QLineEdit,'quest_title').setText('Después de undo');self.w.commit_properties();self.assertEqual(self.w.doc.campaign['quests'][0]['title'],'Después de undo')
 def test_scene_view_selection_and_full_campaign_undo(self):
  self.w.campaign_panel.scene.setCurrentIndex(1);self.assertEqual(self.w.doc.data['level']['source'],'WestLondon');self.w.doc.data['actors'].append({'id':'test','name':'Test','template':'businessWoman','transform':{'placement':'near_player','orientation':[0,0,0]}});self.w.changed(True);self.w.undo_project();self.assertFalse(self.w.doc.campaign['scenes'][1]['actors']);self.assertEqual(len(self.w.doc.snapshot()['scenes']),2)
 def test_extended_condition_gui_has_explicit_empty_choice(self):
  self.w.doc.data['events'][-1]['conditions']=[{'quest':'','step':2}];self.w.select(('events',len(self.w.doc.data['events'])-1,'conditions',0));combo=self.w.properties.widget().findChild(QComboBox,'condition_quest');self.assertEqual(combo.currentData(),'');combo.setCurrentIndex(combo.findData('mission'));self.assertEqual(self.w.doc.data['events'][-1]['conditions'][0]['quest'],'mission')
 def test_references_include_quest_and_cross_scene_navigation(self):
  self.w.find_references(('quests',0));root=self.w.reference_tree.topLevelItem(0);self.assertGreater(root.childCount(),0);self.w.navigate_reference(root.child(0).data(0,__import__('PySide6.QtCore',fromlist=['Qt']).Qt.ItemDataRole.UserRole));self.assertEqual(self.w.selection[0],'events')
 def test_invalid_campaign_rename_does_not_save(self):
  field=self.w.campaign_panel.findChild(QLineEdit,'campaign_id');field.setText('invalid id')
  with patch.object(QMessageBox,'warning'):self.assertFalse(self.w.save_project())
  self.assertEqual(self.w.doc.campaign['quests'][0]['id'],'mission');self.assertTrue(field._rcm_pending)
 def test_invalid_pending_rename_blocks_adding_quest(self):
  field=self.w.campaign_panel.findChild(QLineEdit,'campaign_id');field.setText('invalid id');before=len(self.w.doc.campaign['quests'])
  with patch.object(QMessageBox,'warning'):self.w.campaign_panel.add_quest()
  self.assertEqual(len(self.w.doc.campaign['quests']),before)
