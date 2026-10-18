"""New choices remain in ordinary inspectors with undo and saved source."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QComboBox,QSpinBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.document import Document
from rcm.editor.window import MainWindow
from test_final_flecks import source

ROOT=Path(__file__).resolve().parents[1]


class FinalFlecksUI(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=CampaignDocument(self.backend.ws,source());self.win.refresh()
        self.win.center_tabs.setCurrentIndex(1)
    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()
    def test_native_formation_choice_and_two_undo_steps(self):
        win=self.win;before=win.doc.snapshot();win.select(('conversations',0))
        choose=win.properties.widget().findChild(QComboBox,'conversation_staging')
        value=dict(mode='native',entries=['start']);index=choose.findData(value);self.assertGreaterEqual(index,0);choose.setCurrentIndex(index)
        point=win.properties.widget().findChild(QComboBox,'conversation_party_1');self.assertIsNotNone(point)
        point.setCurrentIndex(point.findData('companion'));self.assertEqual(win.doc.data['conversations'][0]['staging']['entries'],['start','companion'])
        win.resize(1100,720);win.show();self.app.processEvents()
        current=win.properties.widget().findChild(QComboBox,'conversation_staging')
        self.assertEqual(current.toolTip(),current.currentText())
        self.assertLessEqual(win.properties.horizontalScrollBar().maximum(),1)
        self.assertTrue(win.backend.validate(win.doc.snapshot()).valid)
        win.undo_project();self.assertEqual(win.doc.data['conversations'][0]['staging']['entries'],['start'])
        win.undo_project();self.assertEqual(win.doc.snapshot(),before)
    def test_music_action_volume_serialization_and_undo(self):
        win=self.win;data=win.doc.snapshot();data['scenes'][0]['events'].append(dict(id='music',when='manual',actions=[{'pop_music':True}]))
        win.doc=CampaignDocument(win.backend.ws,data);win.refresh();before=win.doc.snapshot()
        win.campaign_panel.navigate(('scenes',0,'events',1,'actions',0))
        kind=win.properties.widget().findChild(QComboBox,'action_kind');kind.setCurrentIndex(kind.findData('push_music'))
        volume=win.properties.widget().findChild(QSpinBox,'temporary_music_volume');self.assertIsNotNone(volume);win.history_time=0;volume.setValue(37)
        self.assertEqual(win.doc.data['events'][1]['actions'][0]['push_music']['volume'],37)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temporary:
            path=Path(temporary)/'project.yaml';win.doc.save(path)
            self.assertEqual(Document.load(win.backend.ws,path).snapshot(),win.doc.snapshot())
        win.undo_project();self.assertEqual(win.doc.data['events'][1]['actions'][0]['push_music']['volume'],50)
        win.undo_project();self.assertEqual(win.doc.snapshot(),before)
