"""User journeys for search, selection recovery and guarded property navigation."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QLineEdit, QMessageBox, QListWidgetItem
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.document import Document
from rcm.editor.window import MainWindow
from rcm.editor.browser import ResourceDialog
from rcm.editor import i18n

ROOT = Path(__file__).resolve().parents[1]


class Usability(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT))
        cls.backend.safe_mode = True

    def setUp(self):
        self.language = i18n.language()
        i18n._language = 'es'
        self.win = MainWindow(self.backend)
        self.win.doc = Document.load(self.backend.ws, 'chronicles/tutorial/project.yaml')
        self.win.refresh()
        self.win.show()
        self.app.processEvents()
        self.before = self.win.doc.snapshot()

    def tearDown(self):
        self.win.doc = None
        self.win.close()
        self.app.processEvents()
        i18n._language = self.language

    def test_local_search_finds_id_and_preserves_expansion_and_document(self):
        actor = self.win.doc.data['actors'][0]
        self.win.nav_items[('objects',)].setExpanded(False)
        self.win.refresh()
        self.assertFalse(self.win.nav_items[('objects',)].isExpanded())
        self.win.focus_project_search()
        self.win.nav_search.setText(actor['id'])
        item = self.win.nav_items[('actors', 0)]
        self.assertFalse(item.isHidden())
        QTest.keyClick(self.win.nav_search, Qt.Key.Key_Return)
        self.assertEqual(self.win.selection, ('actors', 0))
        self.win.nav_search.setText('no_possible_match_xyz')
        self.assertFalse(self.win.nav_empty.isHidden())
        self.assertIsNone(self.win.nav.currentItem())
        self.win.nav.setFocus()
        with patch.object(QMessageBox, 'question') as question:
            QTest.keyClick(self.win.nav, Qt.Key.Key_Delete)
        question.assert_not_called()
        self.win.nav_search.clear()
        self.assertTrue(self.win.nav_empty.isHidden())
        self.assertFalse(self.win.nav_items[('objects',)].isExpanded())
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_global_search_opens_other_scene_with_enter_and_keeps_nested_text_search(self):
        panel = self.win.campaign_panel
        scene = self.win.doc.campaign['scenes'][-1]
        actor = scene['actors'][0]
        panel.focus_search()
        panel.search.setText(actor['id'])
        rows = [panel.tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole) for i in range(panel.tree.topLevelItemCount())]
        path = ('scenes', len(self.win.doc.campaign['scenes'])-1, 'actors', 0)
        self.assertIn(path, rows)
        self.assertNotIn(path[:2], rows)  # A scene must not match every word in its children.
        panel.tree.setCurrentItem(panel.tree.topLevelItem(rows.index(path)))
        QTest.keyClick(panel.search, Qt.Key.Key_Return)
        self.assertEqual(self.win.doc.active, path[1])
        self.assertEqual(self.win.selection, ('actors', 0))
        scene['events'][0]['comment'] = 'Unique search explanation'
        panel.search.setText('Unique search explanation')
        self.assertEqual(panel.tree.topLevelItemCount(), 1)
        panel.search.setText('no_possible_match_xyz')
        self.assertIn('Sin coincidencias', panel.search_status.text())
        panel.search.clear()
        self.assertGreater(panel.tree.topLevelItemCount(), 0)

    def test_keyboard_activation_of_global_results(self):
        panel = self.win.campaign_panel
        panel.focus_search()
        panel.search.setText(self.win.doc.campaign['quests'][0]['id'])
        panel.tree.setCurrentItem(panel.tree.topLevelItem(0))
        panel.tree.setFocus()
        QTest.keyClick(panel.tree, Qt.Key.Key_Return)
        self.assertEqual(panel.path, ('quests', 0))
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_global_flag_results_open_the_real_flag_editor_and_refresh_safely(self):
        alias = next(iter(self.win.doc.campaign['state']['flags']))
        self.win.campaign_panel.navigate(('state', 'flags', alias))
        self.assertEqual(self.win.selection, ('state', 'flags', alias))
        self.win.refresh()
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_overview_does_not_offer_a_broken_second_id_editor_for_ordinary_entities(self):
        panel = self.win.campaign_panel
        panel.navigate(('scenes', 0, 'entries', 0))
        panel.render()
        self.assertIsNone(panel.scroll.widget().findChild(QLineEdit, 'campaign_id'))
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_opening_another_project_clears_searches(self):
        self.win.nav_search.setText('no_possible_match_xyz')
        self.win.campaign_panel.search.setText('no_possible_match_xyz')
        self.win.doc = Document.load(self.backend.ws, 'chronicles/tutorial/project.yaml')
        self.win.refresh()
        self.assertFalse(self.win.nav_search.text())
        self.assertFalse(self.win.campaign_panel.search.text())
        self.assertTrue(self.win.nav_empty.isHidden())

    def test_recent_project_opens_with_enter(self):
        recents = self.win.welcome.recents
        item = QListWidgetItem('My chronicle')
        item.setData(Qt.ItemDataRole.UserRole, str(self.win.doc.path))
        recents.addItem(item)
        recents.setCurrentItem(item)
        with patch.object(self.win, 'open_path') as opened:
            QTest.keyClick(recents, Qt.Key.Key_Return)
        opened.assert_called_once_with(str(self.win.doc.path))

    def test_invalid_pending_property_stays_visible_when_selecting_another_item(self):
        self.win.select(('actors', 0))
        field = self.win.properties.widget().findChild(QLineEdit, 'actor_id')
        self.assertIsNotNone(field)
        field.setText('invalid id with spaces')
        with patch.object(QMessageBox, 'warning') as warning:
            result = self.win.select(('objects', 0))
        self.assertFalse(result)
        self.assertTrue(warning.called)
        self.assertEqual(self.win.selection, ('actors', 0))
        self.assertIs(self.win.properties.widget().findChild(QLineEdit, 'actor_id'), field)
        self.assertEqual(field.text(), 'invalid id with spaces')
        self.assertEqual(self.win.doc.snapshot(), self.before)
        field.setText(self.win.doc.data['actors'][0]['id'])
        self.win.select(('objects', 0))
        self.assertEqual(self.win.selection, ('objects', 0))

    def test_resource_empty_state_reset_preserves_category_and_inventory_constraints(self):
        dialog = ResourceDialog(self.backend, 'items', self.win)
        browser = dialog.browser
        browser.allowed_families = {'items'}
        browser.family.setCurrentIndex(browser.family.findData('weapons'))
        self.assertEqual(browser.table.rowCount(), 0)
        self.assertIn('Sin coincidencias', browser.details.text())
        self.assertFalse(browser.inspect_button.isEnabled())
        self.assertFalse(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        browser.reset_button.click()
        self.assertEqual(browser.category.currentData(), 'items')
        self.assertFalse(browser.category.isEnabled())
        self.assertGreater(browser.table.rowCount(), 0)
        self.assertEqual({browser.table.item(i, 1).text() for i in range(browser.table.rowCount())}, {'items'})
        self.assertFalse(browser.reset_button.isEnabled())
        dialog.reject()

    def test_resource_search_keyboard_choose_and_no_stale_selection(self):
        dialog = ResourceDialog(self.backend, 'actors', self.win)
        dialog.show()
        browser = dialog.browser
        browser.search.setText('businessWoman')
        self.assertFalse(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        QTest.keyClick(browser.search, Qt.Key.Key_Return)
        self.assertEqual(dialog.result(), 0)
        self.assertEqual(browser.selected()[0], 'businessWoman')
        self.assertTrue(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        browser.search.setText('no_possible_match_xyz')
        self.assertIsNone(browser.selected())
        self.assertFalse(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        browser.search.setText('businessWoman')
        browser.focus_results()
        browser.refresh()
        self.assertEqual(browser.selected()[0], 'businessWoman')
        QTest.keyClick(browser.table, Qt.Key.Key_Return)
        self.assertEqual(dialog.result(), dialog.DialogCode.Accepted)
        self.assertEqual(dialog.selection, 'businessWoman')
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_new_labels_are_translated_without_touching_authored_names(self):
        i18n._language = 'en'
        for source in ('Buscar en el proyecto', 'Restablecer filtros', 'Cámaras', 'Recorridos', 'Sin coincidencias. Cambia la búsqueda o restablece los filtros.'):
            self.assertNotEqual(i18n.tr(source), source)
        self.assertEqual(self.win.doc.snapshot(), self.before)
