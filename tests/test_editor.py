"""A few meaningful editor interactions, complementing the vertical GUI acceptance."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "cache/vendor")]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLineEdit, QComboBox, QSpinBox, QMessageBox
    from PySide6.QtTest import QTest
    HAVE_QT = True
except ImportError:
    HAVE_QT = False

from rcm.paths import Workspace
from rcm.service import Backend, source_text
from rcm.document import Document
from test_phase2 import graph_source


@unittest.skipUnless(HAVE_QT, "Install optional requirements-editor.txt to test the GUI")
class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.ws = Workspace(ROOT, Path(r"H:\GOG\Vampire The Masquerade - Redemption"))
        cls.backend = Backend(cls.ws)

    def setUp(self):
        from rcm.editor.window import MainWindow
        self.w = MainWindow(self.backend)
        self.w.doc = Document(self.ws, graph_source())
        self.w.refresh(); self.w.show(); self.app.processEvents()

    def tearDown(self):
        self.w.doc = None
        self.w.close(); self.app.processEvents()

    def control(self, kind, name):
        return self.w.properties.widget().findChild(kind, name)

    def test_actor_edit_is_dirty_and_shared_backend_sees_it(self):
        self.w.doc.save(ROOT / "build/tests/editor_actor.yaml")
        self.w.select(("actors", 0))
        self.control(QLineEdit, "actor_name").setText("Victoria del Támesis")
        self.assertTrue(self.w.doc.modified)
        self.assertTrue(self.w.windowTitle().startswith("*"))
        v = self.backend.validate(self.w.doc.data)
        self.assertTrue(v.valid)
        self.assertEqual(v.project.entities[0].name, "Victoria del Támesis")

    def test_problem_navigation_and_repair_broken_graph(self):
        path = ROOT / "build/tests/editor_broken.yaml"
        d = graph_source(); d["conversations"][0]["nodes"][0]["choices"][0]["goto"] = "missing"
        self.ws.write(path, source_text(d)); self.w.open_path(path)
        self.assertFalse(self.w.validate_project().valid)
        self.w.problem_selected(0, 0)
        self.assertEqual(self.w.selection, ("conversations", 0, "nodes", 0))
        self.w.select(("conversations", 0, "nodes", 0, "choices", 0))
        control = self.control(QComboBox, "answer_target")
        control.setCurrentIndex(control.findData("identity"))
        self.assertTrue(self.w.validate_project().valid)

    def test_invalid_draft_does_not_replace_current_project(self):
        original = self.w.doc
        path = ROOT / "build/tests/editor_corrupt.yaml"
        self.ws.write(path, "chronicle: bad\nlevel: {}\nactors: []\nconversations: []\nevents: []\n")
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Ok) as warning:
            self.w.guard(lambda: self.w.open_path(path))
        self.assertIs(self.w.doc, original)
        self.assertTrue(warning.called)

    def test_invalid_build_is_blocked_before_worker(self):
        self.w.doc.data["state"]["flags"]["duplicate"] = 1
        self.w.actions["build"].trigger()
        self.assertFalse(self.w.busy)
        self.assertIsNone(self.w.last_build)
        self.assertEqual(self.w.bottom_tabs.currentIndex(), 0)

    def test_cancel_on_dirty_close_and_save_action(self):
        self.w.doc.path = ROOT / "build/tests/editor_dirty.yaml"
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.w.can_leave())
        self.w.actions["save"].trigger()
        self.assertFalse(self.w.doc.modified)
        self.assertTrue(self.w.can_leave())

    def test_deleting_graph_target_is_blocked_and_window_alive(self):
        self.w.select(("conversations", 0, "nodes", 1))
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes),patch.object(QMessageBox,'warning') as warning:
            QTest.mouseClick(self.w.buttons["delete"], Qt.MouseButton.LeftButton)
        self.assertTrue(warning.called)
        self.assertTrue(self.w.validate_project().valid)
        self.assertTrue(self.w.isVisible())
        self.assertEqual(len(self.w.doc.data["conversations"][0]["nodes"]), 2)

    def test_save_commits_id_without_enter_or_focus_change(self):
        path = ROOT / "build/tests/editor_unconfirmed_id.yaml"
        self.w.doc.save(path)
        self.w._title()
        self.assertFalse(self.w.windowTitle().startswith("*"))
        self.w.select(("actors", 0))
        self.control(QLineEdit, "actor_id").setText("vicky")
        self.assertTrue(self.w.windowTitle().startswith("*"))
        self.w.actions["save"].trigger()
        loaded = Document.load(self.ws, path)
        self.assertEqual(loaded.data["actors"][0]["id"], "vicky")
        self.assertEqual(loaded.data["conversations"][0]["speaker"], "vicky")
        self.assertFalse(self.w.doc.modified)

    def test_flag_index_tree_updates_immediately(self):
        target = ("state", "flags", "alliance")
        self.w.select(target)
        self.control(QSpinBox, "flag_index").setValue(2)
        self.assertEqual(self.w.content_items[target].text(1), "2")

    def test_condition_and_answer_destination_tree_updates(self):
        self.w.select(("events", 0)); self.w.add_condition()
        target = self.w.selection
        self.control(QComboBox, "condition_state").setCurrentIndex(1)
        self.assertEqual(self.w.content_items[target].text(1), "alliance desactivado")
        target = ("conversations", 0, "nodes", 0, "choices", 0)
        self.w.select(target)
        combo = self.control(QComboBox, "answer_target")
        combo.setCurrentIndex(combo.findData("opening"))
        self.assertEqual(self.w.content_items[target].text(0), "→ opening")

    def test_invalid_unconfirmed_id_does_not_overwrite_saved_project(self):
        path = ROOT / "build/tests/editor_invalid_id.yaml"
        self.w.doc.save(path)
        original = path.read_bytes()
        self.w.select(("actors", 0))
        field = self.control(QLineEdit, "actor_id")
        field.setText("Invalid ID!")
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Ok) as warning:
            self.assertFalse(self.w.save_project())
        self.assertTrue(warning.called)
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue(self.w.pending_properties())
        field.setText("vicky")
        self.assertTrue(self.w.save_project())
        self.assertFalse(self.w.pending_properties())

    def test_unconfirmed_edit_can_cancel_close_or_discard(self):
        self.w.doc.save(ROOT / "build/tests/editor_pending_close.yaml")
        self.w.select(("actors", 0))
        self.control(QLineEdit, "actor_id").setText("vicky")
        self.assertFalse(self.w.doc.modified)  # Pending UI edit, before rename commit.
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.w.can_leave())
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard):
            self.assertTrue(self.w.can_leave())
        self.assertFalse(self.w.pending_properties())
        self.assertEqual(self.control(QLineEdit, "actor_id").text(), "victoria")

    def test_spatial_transform_is_serializable_and_updates_properties(self):
        import numpy as np
        from PySide6.QtWidgets import QDoubleSpinBox
        self.w.select(('actors',0))
        self.w.spatial.transform(('actors',0),{'position':[np.float64(1016),np.float64(-54),np.float64(0)],'orientation':[0,0,np.float64(90)]})
        self.assertEqual(self.w.doc.data['actors'][0]['transform']['placement'],'absolute')
        self.assertEqual(self.control(QDoubleSpinBox,'position_x').value(),1016)
        self.assertEqual(self.control(QDoubleSpinBox,'orientation_2').value(),90)
        self.assertTrue(self.w.backend.validate(self.w.doc.data).valid)
        self.w.doc.save(ROOT/'build/tests/editor_spatial_transform.yaml')

    def test_spatial_trigger_rename_keeps_event_reference(self):
        from test_spatial import spatial_source
        self.w.doc=Document(self.ws,spatial_source());self.w.refresh()
        self.w.select(('triggers',0))
        field=self.control(QLineEdit,'trigger_id');field.setText('new_entry');field.editingFinished.emit()
        self.assertEqual(self.w.doc.data['events'][1]['trigger'],'new_entry')
        self.assertTrue(self.w.backend.validate(self.w.doc.data).valid)

    def test_undo_redo_restores_spatial_and_story_data(self):
        self.w.select(('actors',0))
        original=self.w.doc.snapshot()
        self.w.spatial.transform(('actors',0),{'position':[1016,-54,0]})
        changed=self.w.doc.snapshot()
        self.assertNotEqual(original,changed)
        self.w.actions['undo'].trigger()
        self.assertEqual(self.w.doc.data,original)
        self.w.actions['redo'].trigger()
        self.assertEqual(self.w.doc.data,changed)

    def test_original_entity_cannot_be_deleted(self):
        original=self.w.doc.snapshot()
        self.w.selection=('original',0)
        with patch.object(QMessageBox,'question') as question:
            self.w.delete_selected()
        question.assert_not_called()
        self.assertEqual(self.w.doc.data,original)

    def test_transform_during_level_switch_does_not_write_old_geometry_coordinates(self):
        from types import SimpleNamespace
        original=self.w.doc.snapshot()
        stale=SimpleNamespace(level=SimpleNamespace(name='OtherLevel'))
        with patch.object(self.w.spatial,'viewport',stale):
            self.w.spatial.transform(('actors',0),{'position':[100,200,0]})
        self.assertEqual(self.w.doc.data,original)


if __name__ == "__main__":
    unittest.main()
