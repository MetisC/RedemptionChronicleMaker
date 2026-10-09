"""Regression cases from the user's first real editor session."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QColor, QPalette, QMouseEvent, QCursor
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox, QGraphicsTextItem
from PySide6.QtTest import QTest
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor.viewport import Viewport
from rcm.editor.theme import editor_palette
from rcm.safe_edit import delete_candidate
from test_phase2 import graph_source

ROOT = Path(__file__).resolve().parents[1]


def contrast(a, b):
    def luminance(color):
        channels = [color.redF(), color.greenF(), color.blueF()]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        return sum(a * b for a, b in zip(linear, [.2126, .7152, .0722]))
    x, y = sorted([luminance(a), luminance(b)])
    return (y + .05) / (x + .05)


class EditorFixes(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT))

    def setUp(self):
        self.w = MainWindow(self.backend)
        self.w.doc = Document(self.backend.ws, graph_source())
        self.w.refresh()
        self.w.show()
        self.w.activateWindow()
        self.app.processEvents()

    def tearDown(self):
        self.w.doc = None
        self.w.close()
        self.app.processEvents()

    def add_actor(self):
        with patch('rcm.editor.window.ResourceDialog') as dialog:
            dialog.return_value.exec.return_value = QDialog.DialogCode.Accepted
            dialog.return_value.selection = 'businessWoman'
            self.w.add_actor()

    def test_add_from_story_chooses_template_and_delete_undo_restores_spawn(self):
        before = self.w.doc.snapshot()
        self.add_actor()
        created = self.w.doc.snapshot()
        actor = self.w.doc.data['actors'][-1]
        self.assertEqual(actor['template'], 'businessWoman')
        self.assertTrue(any(a.get('spawn') == actor['id'] for e in self.w.doc.data['events'] for a in e['actions']))
        self.assertTrue(self.backend.validate(created).valid)
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            self.w.delete_selected()
        self.assertEqual(self.w.doc.snapshot(), before)
        self.w.undo_project()
        self.assertEqual(self.w.doc.snapshot(), created)
        self.w.redo_project()
        self.assertEqual(self.w.doc.snapshot(), before)

    def test_cancel_template_choice_does_not_create_invalid_actor(self):
        before = self.w.doc.snapshot()
        with patch('rcm.editor.window.ResourceDialog') as dialog:
            dialog.return_value.exec.return_value = QDialog.DialogCode.Rejected
            self.w.add_actor()
        self.assertEqual(before, self.w.doc.snapshot())

    def test_single_generated_spawn_event_is_removed_with_actor(self):
        from rcm.campaign_document import CampaignDocument
        self.w.doc = CampaignDocument.new(self.backend.ws, 'fix_new', 'Nueva', ROOT / 'build/tests/fix_new')
        self.w.doc.data['level']['source'] = 'EastLondon'
        self.w.refresh()
        before = self.w.doc.snapshot()
        self.add_actor()
        self.assertEqual(len(self.w.doc.data['events']), 1)
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            self.w.delete_selected()
        self.assertEqual(self.w.doc.snapshot(), before)
        self.assertTrue(self.backend.validate(self.w.doc.snapshot()).valid)

    def test_delete_key_from_tree_and_text_edit_does_not_delete_entity(self):
        self.add_actor()
        count = len(self.w.doc.data['actors'])
        name = self.w.properties.widget().findChild(QLineEdit, 'actor_name')
        name.setFocus()
        name.setCursorPosition(0)
        QTest.keyClick(name, Qt.Key.Key_Delete)
        self.assertEqual(len(self.w.doc.data['actors']), count)
        self.w.nav.setFocus()
        self.app.processEvents()
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.No) as question:
            QTest.keyClick(self.w.nav, Qt.Key.Key_Delete)
        self.assertTrue(question.called)
        self.assertEqual(len(self.w.doc.data['actors']), count)
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            QTest.keyClick(self.w.nav, Qt.Key.Key_Delete)
        self.assertEqual(len(self.w.doc.data['actors']), count - 1)

    def test_delete_created_trigger_and_keep_actual_story_references_protected(self):
        self.w.doc.data['triggers'] = [dict(id='unused', name='Trigger', shape='box', transform=dict(position=[0, 0, 50], orientation=[0, 0, 0]), size=[100, 100, 100], once=True)]
        self.w.refresh()
        self.w.select(('triggers', 0))
        self.w.nav.setFocus()
        self.app.processEvents()
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            QTest.keyClick(self.w.nav, Qt.Key.Key_Delete)
        self.assertEqual(self.w.doc.data['triggers'], [])
        source = self.w.doc.snapshot()
        with self.assertRaises(ValueError):
            delete_candidate(self.w.doc, ('actors', 0), self.backend, remove_spawns=True)
        self.assertEqual(source, self.w.doc.snapshot())

    def test_tabs_keep_position_across_modes_and_selection(self):
        positions = []
        for index in range(self.w.center_tabs.count()):
            self.w.center_tabs.setCurrentIndex(index)
            self.w.select(('actors', 0))
            self.app.processEvents()
            positions.append(self.w.center_tabs.tabBar().mapToGlobal(self.w.center_tabs.tabBar().rect().topLeft()).y())
        self.assertEqual(len(set(positions)), 1)
        self.assertEqual(self.w.story_header.parentWidget(), self.w.center_tabs.widget(1))

    def test_dark_light_rows_and_graph_text_have_explicit_readable_contrast(self):
        for window in ['#20242b', '#ffffff']:
            source = QPalette()
            source.setColor(QPalette.ColorRole.Window, QColor(window))
            palette = editor_palette(source)
            for background in [QPalette.ColorRole.Base, QPalette.ColorRole.AlternateBase]:
                self.assertGreater(contrast(palette.color(QPalette.ColorRole.Text), palette.color(background)), 7)
            self.assertGreater(contrast(palette.color(QPalette.ColorRole.HighlightedText), palette.color(QPalette.ColorRole.Highlight)), 4.5)
            self.w.setPalette(palette)
            panel = self.w.graph_panel
            panel.scene.clear()
            for i, color in enumerate(['#d9f0e6', '#fff0cf', '#f7d9d9', '#e7eef7', '#ffffff']):
                panel.card(('actors', 0), i * 300, 0, 'Texto legible', color)
            texts = [item for item in panel.scene.items() if isinstance(item, QGraphicsTextItem)]
            for text in texts:
                for color in ['#d9f0e6', '#fff0cf', '#f7d9d9', '#e7eef7', '#ffffff']:
                    self.assertGreater(contrast(text.defaultTextColor(), QColor(color)), 7)

    def test_camera_right_pitch_and_recenter_do_not_create_angle_jumps(self):
        v = Viewport()
        v.resize(600, 500)
        v.yaw = 0
        v.pitch = 0
        v.looking = True
        v.last_mouse = QPointF(300, 250)
        def move(x, y):
            event = QMouseEvent(QEvent.Type.MouseMove, QPointF(x, y), QPointF(x, y), Qt.MouseButton.NoButton, Qt.MouseButton.RightButton, Qt.KeyboardModifier.NoModifier)
            v.mouseMoveEvent(event)
        move(310, 240)
        self.assertLess(v.forward()[1], 0)  # Camera right at yaw zero is -Y.
        self.assertGreater(v.pitch, 0)
        v.warp_target = QPointF(300, 250)
        angles = v.yaw, v.pitch
        with patch.object(QCursor, 'pos', return_value=v.mapToGlobal(QPointF(300, 250).toPoint())):
            move(10, 10)  # Queued pre-warp event must not rotate again.
        move(300, 250)  # Synthetic return to center.
        self.assertEqual((v.yaw, v.pitch), angles)
        move(302, 248)
        self.assertAlmostEqual(v.pitch, angles[1] + .44)
        v.warp_target=QPointF(300,250)
        # Driver omitted synthetic center, next real movement must still work.
        with patch.object(QCursor, 'pos', return_value=v.mapToGlobal(QPointF(304, 247).toPoint())):
            move(304,247)
        self.assertIsNone(v.warp_target)
        self.assertAlmostEqual(v.pitch, angles[1] + .44 + .66)
        for pitch in [-88, -87.99, -60, 0, 60, 87.99, 88]:
            v.pitch = pitch
            v.pos = np.zeros(3)
            at_origin = v.matrices()
            v.pos = np.array([1000000., -1000000., 1000000.])
            matrix = v.matrices()
            self.assertTrue(all(np.all(np.isfinite(matrix.row(i).toTuple())) for i in range(4)))
            self.assertTrue(np.allclose([at_origin.row(i).toTuple()[:3] for i in range(4)], [matrix.row(i).toTuple()[:3] for i in range(4)], atol=1e-7))
        v.deleteLater()

    def test_orbit_keeps_radius_and_does_not_cross_vertical_pole(self):
        v = Viewport()
        v.resize(600, 500)
        v.selection = ('actors', 0)
        v.pos = np.array([100., 0., 50.])
        v.level = SimpleNamespace()
        actor = {'transform': {'placement': 'absolute', 'position': [0, 0, 0]}}
        v.orbiting = True
        v.last_mouse = QPointF(300, 250)
        with patch.object(v, 'entities', return_value=[(('actors', 0), actor, False)]):
            for y in [1000, 2000, 3000, 2000, 1000]:
                event = QMouseEvent(QEvent.Type.MouseMove, QPointF(300, y), QPointF(300, y), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.AltModifier)
                v.mouseMoveEvent(event)
                self.assertAlmostEqual(np.linalg.norm(v.pos - [0, 0, 50]), 100)
                self.assertLessEqual(abs(v.pitch), 88.0001)
        v.deleteLater()
