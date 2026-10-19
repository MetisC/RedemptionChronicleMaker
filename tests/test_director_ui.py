"""Director UI transactions and discoverability; no native game automation."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy
from pathlib import Path
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QPushButton,QComboBox,QListWidget
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.editor.window import MainWindow
from rcm.editor.director import CameraPathDialog
import test_director

ROOT=Path(__file__).resolve().parents[1]


class DirectorUI(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=CampaignDocument(self.backend.ws,test_director.Director.source(self));self.win.refresh()
        from rcm.editor.viewport import Viewport
        self.win.spatial.viewport=Viewport(self.win.spatial)
    def tearDown(self):
        self.win.doc=None;self.win.close();self.app.processEvents()
    def test_capture_cancel_apply_and_single_undo(self):
        win=self.win;before=win.doc.snapshot();path=('scenes',0,'sequences',0)
        dialog=CameraPathDialog(win,path);dialog.reject();self.assertEqual(win.doc.snapshot(),before)
        dialog=CameraPathDialog(win,path);first=copy.deepcopy(dialog.row['points'][0]);win.spatial.viewport.pos[0]+=100;dialog.add()
        self.assertEqual(dialog.list.count(),2);self.assertEqual(dialog.row['points'][0],first)
        dialog.accept();self.assertEqual(dialog.result(),dialog.DialogCode.Accepted,dialog.error.text())
        self.assertEqual(len(win.doc.campaign['resources']['camera_paths'][0]['points']),2)
        self.assertTrue(self.backend.validate(win.doc.snapshot()).valid)
        win.undo_project();self.assertEqual(win.doc.snapshot(),before)
    def test_sequence_and_line_controls_share_existing_home(self):
        win=self.win;win.campaign_panel.path=('scenes',0,'sequences',0);win.campaign_panel.render()
        self.assertIsNotNone(win.campaign_panel.findChild(QPushButton,'director_camera_path'))
        self.assertIsNotNone(win.campaign_panel.findChild(QListWidget,'director_cues'))
        win.select(('conversations',0,'nodes',0,'lines',0));self.assertIsNotNone(win.properties.widget().findChild(QPushButton,'director_line_actions'))
        win.select(('conversations',0));self.assertIsNotNone(win.properties.widget().findChild(QComboBox,'conversation_staging'))
        self.assertGreaterEqual(win.browser.category.findData('.ncp'),0)
    def test_path_edit_rejects_stale_project_and_duplicate_position(self):
        dialog=CameraPathDialog(self.win,('scenes',0,'sequences',0));dialog.add();dialog.accept()
        self.assertNotEqual(dialog.result(),dialog.DialogCode.Accepted);self.assertTrue(dialog.error.text());dialog.reject()
        dialog=CameraPathDialog(self.win,('scenes',0,'sequences',0));self.win.doc.campaign['chronicle']['name']='Changed';dialog.accept()
        self.assertNotEqual(dialog.result(),dialog.DialogCode.Accepted);self.assertTrue(dialog.error.text());dialog.reject()

    def test_edit_timed_path_preserves_initial_shots_and_playback_action(self):
        root=self.win.doc.snapshot();sequence=root['scenes'][0]['sequences'][0]
        sequence['steps']=[dict(at=0,actor='mentor',preset='aerial')]
        sequence['cues'].append(dict(at=5.5,actions=[{'play_camera_path':dict(resource='own_path',speed=50)}]))
        root['resources']['camera_paths']=[dict(id='own_path',scene=root['scenes'][0]['id'],level=root['scenes'][0]['level']['source'],points=[dict(position=[0,0,100],orientation=[0,0,0]),dict(position=[100,0,100],orientation=[0,0,20])])]
        self.win.doc.data=root;dialog=CameraPathDialog(self.win,('scenes',0,'sequences',0))
        self.assertEqual(dialog.list.count(),2);self.assertFalse(dialog.main_binding)
        dialog.name.setText('New name');dialog.accept();self.assertEqual(dialog.result(),dialog.DialogCode.Accepted)
        result=self.win.doc.snapshot();self.assertEqual(result['scenes'][0]['sequences'][0],sequence)
        self.assertNotIn('camera_path',result['scenes'][0]['sequences'][0]);self.assertEqual(len(result['resources']['camera_paths']),1)

    def test_sequence_form_scrolls_without_overlapping_rows(self):
        from PySide6.QtWidgets import QDoubleSpinBox
        win=self.win;win.resize(1100,720);win.show();win.campaign_panel.navigate(('scenes',0,'sequences',0));self.app.processEvents()
        panel=win.campaign_panel;duration=panel.findChild(QDoubleSpinBox,'sequence_duration');button=panel.findChild(QPushButton,'director_camera_path');cues=panel.findChild(QListWidget,'director_cues')
        self.assertGreater(panel.scroll.verticalScrollBar().maximum(),0)
        self.assertLess(duration.geometry().bottom(),button.geometry().top())
        self.assertLess(button.geometry().bottom(),cues.geometry().top());self.assertGreaterEqual(cues.height(),130)

    def test_converting_shared_path_to_seconds_retimes_sequence_cues_and_events(self):
        root=self.win.doc.snapshot();scene=root['scenes'][0];sequence=scene['sequences'][0]
        sequence.pop('steps',None);sequence['camera_path']='own_path';sequence['path_speed']=30
        sequence['cues'].append(dict(at=5.5,actions=[dict(play_camera_path=dict(resource='own_path',speed=50))]))
        scene['events'].append(dict(id='shared_path',when='manual',actions=[dict(play_camera_path=dict(resource='own_path',speed=25))]))
        root['resources']['camera_paths']=[dict(id='own_path',scene=scene['id'],level=scene['level']['source'],points=[dict(position=[0,0,100],orientation=[0,0,0]),dict(position=[100,0,100],orientation=[0,0,20])])]
        self.win.doc.data=root;self.win.changed(True);before=self.win.doc.snapshot()
        dialog=CameraPathDialog(self.win,None,'own_path');dialog.timed.setChecked(True);dialog.accept();self.assertEqual(dialog.result(),dialog.DialogCode.Accepted,dialog.error.text())
        result=self.win.doc.snapshot();sequence=result['scenes'][0]['sequences'][0]
        self.assertEqual(sequence['path_speed'],1);self.assertEqual(sequence['cues'][-1]['actions'][0]['play_camera_path']['speed'],1);self.assertEqual(result['scenes'][0]['events'][-1]['actions'][0]['play_camera_path']['speed'],1)
        valid=self.backend.validate(result);self.assertTrue(valid.valid,[p.message for p in valid.problems])
        self.win.undo_project();self.assertEqual(self.win.doc.snapshot(),before)
