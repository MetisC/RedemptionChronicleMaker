"""Controller workflows over Qt widgets; these do not test game UI or OpenGL."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QPlainTextEdit,QMessageBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.editor.window import MainWindow
from rcm.editor import package_panel
from campaign_fixture_helpers import system_source

ROOT=Path(__file__).resolve().parents[1]

class Phase6GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def setUp(self):
        self.win=MainWindow(self.backend);self.win.doc=CampaignDocument(self.backend.ws,system_source(self.backend.ws));self.win.doc.path=ROOT/'build/tests/phase6_gui.yaml';self.win.refresh();self.app.processEvents()
    def tearDown(self):self.win.doc=None;self.win.close();self.app.processEvents()
    def java_editor(self):
        panel=self.win.project_resources_panel;panel.kind.setCurrentIndex(3);panel.list.setCurrentRow(0);self.app.processEvents();return panel.findChild(QPlainTextEdit,'custom_java')
    def test_pending_java_is_committed_before_save(self):
        editor=self.java_editor();self.assertIsNotNone(editor);path=self.backend.ws.output(self.win.doc.campaign['resources']['scripts'][0]['source']);before=path.read_text(encoding='utf8');editor.setPlainText(before+'// pending custom Java\n')
        self.assertIn(editor,self.win.pending_properties());self.assertTrue(self.win.save_project());self.assertIn('// pending custom Java',path.read_text(encoding='utf8'));self.assertEqual(path.with_name(path.name+'.backup').read_text(encoding='utf8'),before);self.assertFalse(self.win.pending_properties())
    def test_pending_java_close_cancel_preserves_editor(self):
        editor=self.java_editor();editor.setPlainText(editor.toPlainText()+'// unsaved\n')
        with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Cancel):self.assertFalse(self.win.can_leave())
        self.assertTrue(editor._rcm_pending)
    def test_package_export_import_via_gui_preserves_project(self):
        self.win.doc.save();source=self.win.doc.snapshot();archive=ROOT/'build/tests/gui_project.rcmproject'
        with patch('rcm.editor.package_panel.QFileDialog.getSaveFileName',return_value=(str(archive),'')):package_panel.export_project(self.win)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            with patch('rcm.editor.package_panel.QFileDialog.getOpenFileName',return_value=(str(archive),'')),patch('rcm.editor.package_panel.QFileDialog.getExistingDirectory',return_value=tmp),patch.object(QMessageBox,'information'):package_panel.import_project(self.win)
            imported=self.win.doc.snapshot();self.assertEqual(imported['scenes'],source['scenes']);self.assertEqual(imported['quests'],source['quests']);self.assertTrue(self.backend.validate(imported).valid)
            self.win.doc=None
    def test_safe_delete_campaign_cancel_has_no_effect(self):
        s=self.win.doc.campaign['scenes'][1];s['events'].append({'id':'unused','when':'timer','seconds':1,'actions':[{'reward_xp':1}]});panel=self.win.campaign_panel;panel.path=('scenes',1,'events',len(s['events'])-1);before=self.win.doc.snapshot()
        with patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.No):panel.delete()
        self.assertEqual(self.win.doc.snapshot(),before)
    def test_safe_mode_avoids_viewport_creation(self):
        self.backend.safe_mode=True
        try:
            win=MainWindow(self.backend);self.assertIsNone(win.spatial.viewport);win.close()
        finally:self.backend.safe_mode=False
    def test_export_menu_and_diagnostics_available(self):
        titles=[a.text() for a in self.win.menuBar().actions()];self.assertIn('Herramientas',titles)
        self.assertEqual(self.win.package_menu.title(),'Paquetes')
        self.assertIn(self.win.package_menu.menuAction(),self.win.tools_menu.actions())
        from rcm.diagnostics import diagnostic_report
        report=diagnostic_report(self.backend.ws);self.assertTrue(Path(report['report']).exists());self.assertFalse(report['native_engine_test'])
