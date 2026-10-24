"""Typing must never run authoring, history, validation or filesystem work."""
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFocusEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QPlainTextEdit, QSpinBox

from rcm.campaign_document import CampaignDocument
from rcm.editor.text_commit import bind_text, bind_spin, bind_filter
from rcm.editor.window import MainWindow, NewProjectDialog
from rcm.paths import Workspace
from rcm.service import Backend
from test_campaign import source

ROOT = Path(__file__).resolve().parents[1]


class DeferredEditTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_line_commits_once_after_editing_and_ignores_repeat_finish(self):
        field = QLineEdit('Original')
        save = Mock()
        bind_text(field, save)
        QTest.keyClicks(field, ' longer title')
        save.assert_not_called()
        self.assertTrue(field._rcm_pending)
        field.editingFinished.emit()
        save.assert_called_once_with('Original longer title')
        field.editingFinished.emit()
        field._rcm_commit()
        save.assert_called_once()

    def test_reverting_to_original_is_not_an_edit(self):
        for kind in (QLineEdit, QPlainTextEdit):
            with self.subTest(kind=kind):
                field = kind('Original')
                save = Mock()
                bind_text(field, save)
                field.setText('Changed') if kind is QLineEdit else field.setPlainText('Changed')
                field.setText('Original') if kind is QLineEdit else field.setPlainText('Original')
                self.assertFalse(field._rcm_pending)
                self.assertTrue(field._rcm_commit())
                save.assert_not_called()

    def test_multiline_return_keeps_typing_and_focus_loss_commits(self):
        field = QPlainTextEdit()
        save = Mock()
        bind_text(field, save)
        QTest.keyClicks(field, 'A line')
        QTest.keyClick(field, Qt.Key.Key_Return)
        QTest.keyClicks(field, 'Another line')
        save.assert_not_called()
        QApplication.sendEvent(field, QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.TabFocusReason))
        save.assert_called_once_with('A line\nAnother line')
        self.assertFalse(field._rcm_pending)

    def test_context_menu_does_not_commit_multiline(self):
        field = QPlainTextEdit()
        save = Mock()
        bind_text(field, save)
        field.setPlainText('Draft')
        QApplication.sendEvent(field, QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.PopupFocusReason))
        save.assert_not_called()
        field._rcm_commit()
        save.assert_called_once_with('Draft')

    def test_failed_commit_retains_draft_and_can_be_retried(self):
        field = QLineEdit('Original')
        save = Mock(side_effect=[False, True])
        bind_text(field, save)
        field.setText('Draft')
        self.assertFalse(field._rcm_commit())
        self.assertTrue(field._rcm_pending)
        self.assertTrue(field._rcm_commit())
        self.assertFalse(field._rcm_pending)
        self.assertEqual(save.call_count, 2)

    def test_reentrant_finish_cannot_commit_twice(self):
        field = QLineEdit('Original')
        save = Mock(side_effect=lambda value: field.editingFinished.emit())
        bind_text(field, save)
        field.setText('Draft')
        self.assertTrue(field._rcm_commit())
        save.assert_called_once_with('Draft')

    def test_discarded_draft_does_not_commit_when_widget_loses_focus(self):
        field = QPlainTextEdit('Original')
        save = Mock()
        bind_text(field, save)
        field.setPlainText('Discard me')
        field._rcm_pending = False
        QApplication.sendEvent(field, QFocusEvent(QEvent.Type.FocusOut, Qt.FocusReason.OtherFocusReason))
        save.assert_not_called()

    def test_numeric_typing_defers_processing_but_arrows_still_work(self):
        field = QSpinBox()
        field.setRange(0, 10000)
        bind_spin(field)
        save = Mock()
        field.valueChanged.connect(save)
        field.lineEdit().selectAll()
        QTest.keyClicks(field.lineEdit(), '1234')
        save.assert_not_called()
        self.assertEqual(field.value(), 0)
        self.assertTrue(field._rcm_pending)
        self.assertTrue(field._rcm_commit())
        save.assert_called_once_with(1234)
        self.assertFalse(field._rcm_pending)
        field.stepUp()
        self.assertEqual(save.call_args.args, (1235,))
        field.editingFinished.emit()
        self.assertEqual(save.call_count, 2)

    def test_search_typing_waits_for_enter_and_programmatic_resets_still_apply(self):
        field = QLineEdit()
        search = Mock()
        bind_filter(field, search)
        QTest.keyClicks(field, 'businessWoman')
        search.assert_not_called()
        QTest.keyClick(field, Qt.Key.Key_Return)
        search.assert_called_once_with()
        field.editingFinished.emit()
        search.assert_called_once()
        field.setText('Rat')
        self.assertEqual(search.call_count, 2)
        field.setText('Rat')
        self.assertEqual(search.call_count, 2)

    def test_search_clear_button_is_an_explicit_request(self):
        from PySide6.QtWidgets import QToolButton
        field = QLineEdit()
        field.setClearButtonEnabled(True)
        search = Mock()
        bind_filter(field, search)
        field.setText('Original')
        field.findChild(QToolButton).click()
        self.assertEqual(field.text(), '')
        self.assertEqual(search.call_count, 2)


class AuthoredTextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT))

    def setUp(self):
        self.win = MainWindow(self.backend)
        self.win.doc = CampaignDocument(self.backend.ws, source())
        self.win.refresh()
        self.win.validation_timer.stop()

    def tearDown(self):
        # A pending multiline field must not commit into the next test on teardown.
        for field in self.win.pending_properties():
            field._rcm_pending = False
        self.win.doc = None
        self.win.close()
        self.app.processEvents()

    def test_all_inspector_text_fields_are_deferred_without_project_work(self):
        paths = [('chronicle',), ('actors', 0), ('conversations', 0), ('events', 0)]
        for path in paths:
            self.win.select(path)
            panel = self.win.properties.widget()
            fields = panel.findChildren(QLineEdit) + panel.findChildren(QPlainTextEdit)
            for field in fields:
                if field.isReadOnly() or not hasattr(field, '_rcm_commit'):
                    continue
                with self.subTest(path=path, name=field.objectName()):
                    original = field.text() if isinstance(field, QLineEdit) else field.toPlainText()
                    with patch.object(self.win, 'changed') as changed, \
                         patch.object(self.win.doc, 'snapshot') as snapshot, \
                         patch('rcm.campaign_document.source_text', side_effect=AssertionError('YAML while typing')):
                        field.setText(original + ' draft') if isinstance(field, QLineEdit) else field.setPlainText(original + ' draft')
                        changed.assert_not_called()
                        snapshot.assert_not_called()
                        field.setText(original) if isinstance(field, QLineEdit) else field.setPlainText(original)
                        self.assertFalse(field._rcm_pending)
                        self.assertTrue(field._rcm_commit())
                        changed.assert_not_called()

    def test_chronicle_typing_performs_no_snapshot_serialization_or_validation(self):
        self.win.select(('chronicle',))
        self.win.doc.save(ROOT / 'build/tests/text_commit_saved.yaml')
        self.win._title()
        panel = self.win.properties.widget()
        name = panel.findChild(QLineEdit, 'chronicle_name')
        description = panel.findChild(QPlainTextEdit, 'chronicle_description')
        before = self.win.doc.snapshot()
        with patch.object(self.win, 'changed') as changed, \
             patch.object(self.win.doc, 'snapshot') as snapshot, \
             patch('rcm.campaign_document.source_text', side_effect=AssertionError('YAML while typing')):
            name.setText('A completely new name')
            QTest.keyClicks(description, 'A useful description, typed without processing.')
            self.assertTrue(self.win.windowTitle().startswith('*'))
            self.assertFalse(self.win.validation_timer.isActive())
            snapshot.assert_not_called()
            changed.assert_not_called()
        self.assertEqual(self.win.doc.snapshot(), before)
        self.assertEqual(len(self.win.pending_properties()), 2)
        with patch.object(self.win, 'changed', wraps=self.win.changed) as changed:
            self.assertTrue(self.win.commit_properties())
            self.assertEqual(changed.call_count, 2)
            self.win.commit_properties()
            self.assertEqual(changed.call_count, 2)
        self.assertEqual(self.win.doc.data['chronicle']['name'], name.text())
        self.assertEqual(self.win.doc.data['chronicle']['description'], description.toPlainText())

    def test_multiline_is_saved_without_focus_loss(self):
        path = ROOT / 'build/tests/text_commit_description.yaml'
        self.win.doc.save(path)
        self.win.select(('chronicle',))
        field = self.win.properties.widget().findChild(QPlainTextEdit, 'chronicle_description')
        field.setPlainText('First line\nSecond line')
        self.assertTrue(self.win.save_project())
        restored = CampaignDocument.load(self.backend.ws, path)
        self.assertEqual(restored.data['chronicle']['description'], field.toPlainText())
        self.assertFalse(self.win.pending_properties())

    def test_selection_switch_flushes_name_and_description(self):
        self.win.select(('chronicle',))
        panel = self.win.properties.widget()
        panel.findChild(QLineEdit, 'chronicle_name').setText('A new title')
        panel.findChild(QPlainTextEdit, 'chronicle_description').setPlainText('A new description')
        self.win.select(('actors', 0))
        self.assertEqual(self.win.doc.data['chronicle']['name'], 'A new title')
        self.assertEqual(self.win.doc.data['chronicle']['description'], 'A new description')
        self.assertFalse(self.win.pending_properties())

    def test_quest_step_does_not_mutate_during_typing(self):
        self.win.campaign_panel.navigate(('quests', 0))
        field = self.win.campaign_panel.findChild(QLineEdit, 'quest_step_0')
        before = self.win.doc.campaign['quests'][0]['steps'][0]
        with patch.object(self.win, 'changed', wraps=self.win.changed) as changed:
            field.setText('Find the hidden letter')
            self.assertEqual(self.win.doc.campaign['quests'][0]['steps'][0], before)
            changed.assert_not_called()
            self.assertTrue(self.win.commit_properties())
            changed.assert_called_once()
        self.assertEqual(self.win.doc.campaign['quests'][0]['steps'][0], 'Find the hidden letter')

    def test_new_project_name_does_not_search_filesystem_during_typing(self):
        with patch('rcm.product.project_id', wraps=__import__('rcm.product', fromlist=['project_id']).project_id) as derive:
            # Construct while patched to observe the real name -> ID path.
            dialog = NewProjectDialog(self.backend.ws, self.win)
            dialog.name.selectAll()
            QTest.keyClicks(dialog.name, 'My next chronicle')
            derive.assert_not_called()
            dialog.name.editingFinished.emit()
            derive.assert_called_once()
        dialog.reject()

    def test_maps_commit_names_to_previous_selection_only(self):
        from rcm.editor.maps import MapDialog
        self.win.doc.campaign['project_format'] = 9
        self.win.doc.campaign['resources'] = {'maps': [dict(id='map1', name='City', original='mapLondonEast.nui', points=[
            dict(id='a', name='First', position=[20, 20], visible=True, haven=False),
            dict(id='b', name='Second', position=[40, 40], visible=True, haven=False)])]}
        dialog = MapDialog(self.win)
        dialog.maps.setCurrentIndex(0)
        dialog.point_name.setText('New first')
        self.assertEqual(dialog.rows[0]['points'][0]['name'], 'First')
        dialog.points.setCurrentRow(1)
        self.assertEqual(dialog.rows[0]['points'][0]['name'], 'New first')
        self.assertEqual(dialog.rows[0]['points'][1]['name'], 'Second')
        dialog.name.setText('New city')
        self.assertEqual(dialog.rows[0]['name'], 'City')
        dialog.maps.setCurrentIndex(1)
        self.assertEqual(dialog.rows[0]['name'], 'New city')
        dialog.reject()
        self.assertEqual(self.win.doc.campaign['resources']['maps'][0]['name'], 'City')

    def test_resource_fields_and_java_write_only_on_commit(self):
        from test_phase5_resources import custom_source
        self.win.doc = CampaignDocument(self.backend.ws, custom_source())
        self.win.refresh()
        panel = self.win.project_resources_panel
        panel.select(0)
        hover = panel.findChild(QLineEdit, 'resource_hover_text')
        with patch.object(self.win, 'changed', wraps=self.win.changed) as changed:
            hover.setText('My character')
            changed.assert_not_called()
            self.win.commit_properties()
            changed.assert_called_once()
            hover.editingFinished.emit()
            changed.assert_called_once()
        panel.kind.setCurrentIndex(panel.kind.findData('scripts'))
        panel.select(0)
        editor = panel.findChild(QPlainTextEdit, 'custom_java')
        with patch.object(self.win.doc, '_atomic_write') as write:
            editor.setPlainText(editor.toPlainText() + '\n// A draft comment')
            write.assert_not_called()
            self.win.commit_properties()
            self.assertEqual(write.call_count, 2)  # One backup, one source write.
            self.win.commit_properties()
            self.assertEqual(write.call_count, 2)

    def test_pending_numeric_input_is_committed_by_save_without_focus_loss(self):
        self.win.campaign_panel.navigate(('quests', 0))
        field = self.win.campaign_panel.findChild(QSpinBox, 'quest_reward')
        before = self.win.doc.campaign['quests'][0].get('reward_xp', 0)
        field.lineEdit().selectAll()
        QTest.keyClicks(field.lineEdit(), '1234')
        self.assertEqual(self.win.doc.campaign['quests'][0].get('reward_xp', 0), before)
        self.assertIn(field, self.win.pending_properties())
        self.assertTrue(self.win.commit_properties())
        self.assertEqual(self.win.doc.campaign['quests'][0]['reward_xp'], 1234)

    def test_deferred_action_dialog_flushes_multiline_on_accept(self):
        from rcm.editor.dynamic_wizard import ActionsDialog
        dialog = ActionsDialog(self.win, self.win.doc.snapshot(), [{'show_note': {'title': 'Note', 'text': 'Original'}}])
        fields = dialog.findChildren(QPlainTextEdit)
        field = next(f for f in fields if hasattr(f, '_rcm_commit'))
        field.setPlainText('Updated note')
        dialog.accept()
        self.assertEqual(dialog.result(), dialog.DialogCode.Accepted)
        self.assertTrue(any(f.toPlainText() == 'Updated note' for f in fields))
        self.assertFalse(field._rcm_pending)
        self.assertEqual(dialog.actions[0]['show_note']['text'], 'Updated note')

    def test_action_selection_flushes_previous_multiline_draft(self):
        from rcm.editor.dynamic_wizard import ActionsDialog
        dialog = ActionsDialog(self.win, self.win.doc.snapshot(), [
            {'show_note': {'title': 'First', 'text': 'Original'}},
            {'show_note': {'title': 'Second', 'text': 'Another note'}}])
        field = next(f for f in dialog.scroll.widget().findChildren(QPlainTextEdit) if hasattr(f, '_rcm_commit'))
        field.setPlainText('First note edited')
        dialog.list.setCurrentRow(1)
        self.assertEqual(dialog.actions[0]['show_note']['text'], 'First note edited')
        self.assertEqual(dialog.actions[1]['show_note']['text'], 'Another note')
        dialog.reject()

    def test_click_action_selection_flushes_previous_multiline_draft(self):
        from rcm.editor.click_actions import ClickActions
        from PySide6.QtWidgets import QLabel
        root = self.win.doc.snapshot()
        root['scenes'][0]['events'][0]['actions'] = [
            {'show_note': {'title': 'First', 'text': 'Original'}},
            {'show_note': {'title': 'Second', 'text': 'Another note'}}]
        panel = ClickActions(self.win, root, 0, QLabel())
        field = next(f for f in panel.scroll.widget().findChildren(QPlainTextEdit) if hasattr(f, '_rcm_commit'))
        field.setPlainText('First note edited')
        panel.actions.setCurrentIndex(1)
        self.assertEqual(panel.event['actions'][0]['show_note']['text'], 'First note edited')
        self.assertEqual(panel.event['actions'][1]['show_note']['text'], 'Another note')
        panel.close()

    def test_setup_path_checks_files_only_after_editing(self):
        from rcm.editor.product_ui import SetupDialog
        from rcm.app_settings import AppSettings
        # Preferences API is intentionally avoided: this dialog only needs the
        # saved language to exercise the executable field.
        preferences = Mock(spec=AppSettings)
        preferences.data = {'language': 'es'}
        dialog = SetupDialog(preferences, parent=self.win)
        with patch.object(Path, 'is_file', return_value=False) as check:
            dialog.exe.setText('H:/Games/Redemption/Vampire.exe')
            check.assert_not_called()
            dialog.exe.editingFinished.emit()
            self.assertEqual(check.call_count, 3)
            dialog.exe.editingFinished.emit()
            self.assertEqual(check.call_count, 3)
        dialog.reject()

    def test_resource_search_from_empty_results_applies_before_enter_navigation(self):
        from rcm.editor.browser import ResourceBrowser
        browser = ResourceBrowser(self.backend, 'actors')
        browser.search.setText('no_possible_match_xyz')
        self.assertEqual(browser.table.rowCount(), 0)
        browser.search.selectAll()
        with patch.object(browser, 'refresh', wraps=browser.refresh) as refresh:
            # bind_filter captures the original refresh callback; table population
            # and preview are the observable work, rather than this patched name.
            QTest.keyClicks(browser.search, 'businessWoman')
            self.assertEqual(browser.table.rowCount(), 0)
            refresh.assert_not_called()
        QTest.keyClick(browser.search, Qt.Key.Key_Return)
        self.assertGreater(browser.table.rowCount(), 0)
        self.assertIsNotNone(browser.selected())
        browser.close()

    def test_filter_reset_can_repeat_the_same_user_query(self):
        from rcm.editor.browser import ResourceBrowser
        browser = ResourceBrowser(self.backend, 'actors')
        browser.search.setText('businessWoman')
        filtered = browser.table.rowCount()
        browser.reset_filters()
        self.assertGreater(browser.table.rowCount(), filtered)
        QTest.keyClicks(browser.search, 'businessWoman')
        QTest.keyClick(browser.search, Qt.Key.Key_Return)
        self.assertEqual(browser.table.rowCount(), filtered)
        browser.close()

    def test_opening_another_document_resets_search_baselines(self):
        self.win.nav_search.setText('no_possible_match_xyz')
        self.win.campaign_panel.search.setText('no_possible_match_xyz')
        self.win.doc = CampaignDocument(self.backend.ws, source())
        self.win.refresh()
        self.assertGreater(self.win.campaign_panel.tree.topLevelItemCount(), 0)
        for field in (self.win.nav_search, self.win.campaign_panel.search):
            QTest.keyClicks(field, 'no_possible_match_xyz')
            field._rcm_commit()
        self.assertTrue(self.win.nav_items[('actors', 0)].isHidden())
        self.assertEqual(self.win.campaign_panel.tree.topLevelItemCount(), 0)

    def test_spatial_update_resets_numeric_baseline_before_user_types(self):
        from test_spatial import spatial_source
        from rcm.document import Document
        from PySide6.QtWidgets import QDoubleSpinBox
        self.win.doc = Document(self.backend.ws, spatial_source())
        self.win.refresh()
        self.win.select(('actors', 1))
        field = self.win.properties.widget().findChild(QDoubleSpinBox, 'position_x')
        previous = field.value()
        self.win.spatial.transform(('actors', 1), {'position': [previous + 100, -54, 0]})
        field.lineEdit().selectAll()
        QTest.keyClicks(field.lineEdit(), str(int(previous)))
        self.assertTrue(field._rcm_pending)
        self.assertTrue(self.win.commit_properties())
        self.assertEqual(self.win.doc.data['actors'][1]['transform']['position'][0], previous)
