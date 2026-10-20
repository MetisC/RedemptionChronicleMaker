"""Local project deletion: real files and Qt widgets, never user chronicles."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from rcm.app_settings import AppSettings
from rcm.editor.product_ui import Welcome
from rcm.paths import Workspace
from rcm.project_safety import ProjectLock, delete_project, project_deletion_target

ROOT = Path(__file__).resolve().parents[1]


class ProjectDeletionTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'build/tests')
        self.root = Path(self.temp.name)
        self.ws = Workspace(self.root/'workspace')
        self.ws.root.mkdir()
        self.prefs = AppSettings(self.root/'preferences')
        self.ws.app_settings = self.prefs
        self.path = self.ws.write('chronicles/mine/project.yaml', 'chronicle: {id: mine, name: Mine}')
        self.prefs.recent(self.path, 'My chronicle')
        self.win = SimpleNamespace(backend=SimpleNamespace(ws=self.ws), new_project=Mock(), open_project=Mock(),
                                   open_path=Mock(), guard=lambda cb:cb())
        self.welcome = Welcome(self.win)

    def tearDown(self):
        self.welcome.close();self.welcome.deleteLater();self.app.processEvents()
        self.temp.cleanup()

    def test_delete_removes_local_assets_and_recent_but_preserves_other_projects_and_game(self):
        self.ws.write('chronicles/mine/assets/a.txt', 'asset')
        self.ws.write('chronicles/mine/project.yaml.autosave', 'draft')
        sibling = self.ws.write('chronicles/other/project.yaml', 'other')
        installed = self.root/'game/RCM/mine.nob';installed.parent.mkdir(parents=True);installed.write_bytes(b'installed')
        delete_project(self.ws, self.path)
        self.assertFalse(self.path.parent.exists())
        self.assertEqual(sibling.read_text(), 'other');self.assertEqual(installed.read_bytes(), b'installed')
        self.assertEqual(AppSettings(self.root/'preferences').data['recent_projects'], [])

    def test_button_selection_cancel_and_confirm(self):
        self.assertFalse(self.welcome.delete_button.isEnabled())
        self.welcome.recents.setCurrentRow(0)
        self.assertTrue(self.welcome.delete_button.isEnabled())
        with patch.object(QMessageBox, 'warning', return_value=QMessageBox.StandardButton.No) as dialog:
            self.welcome.delete_button.click()
        self.assertTrue(self.path.exists());self.assertEqual(len(self.prefs.data['recent_projects']), 1)
        self.assertIn(str(self.path.parent), dialog.call_args.args[2])
        self.assertEqual(dialog.call_args.args[4], QMessageBox.StandardButton.No)
        with patch.object(QMessageBox, 'warning', return_value=QMessageBox.StandardButton.Yes):
            self.welcome.delete_button.click()
        self.assertFalse(self.path.parent.exists());self.assertEqual(self.welcome.recents.count(), 0)
        self.assertFalse(self.welcome.delete_button.isEnabled())

    def test_delete_shortcut_requires_list_focus_and_asks_confirmation(self):
        self.welcome.show();self.welcome.activateWindow();self.welcome.recents.setCurrentRow(0)
        self.welcome.recents.setFocus();self.app.processEvents()
        with patch.object(QMessageBox, 'warning', return_value=QMessageBox.StandardButton.No) as dialog:
            QTest.keyClick(self.welcome.recents, Qt.Key.Key_Delete)
        self.assertEqual(dialog.call_count, 1);self.assertTrue(self.path.exists())

    def test_context_menu_uses_right_clicked_project_and_offers_real_delete(self):
        other = self.ws.write('chronicles/other/project.yaml', 'other');self.prefs.recent(other, 'Other')
        self.welcome.refresh();self.welcome.resize(700, 650);self.welcome.show();self.app.processEvents()
        self.welcome.recents.setCurrentRow(0)
        item = self.welcome.recents.item(1)
        menu = Mock()
        def choose(position):
            label, callback = menu.addAction.call_args_list[-1].args
            self.assertIn(label, ('Eliminar crónica…', 'Delete chronicle…'))
            callback()
        menu.exec.side_effect = choose
        with patch('rcm.editor.product_ui.QMenu', return_value=menu), patch.object(QMessageBox, 'warning', return_value=QMessageBox.StandardButton.Yes):
            self.welcome.context(self.welcome.recents.visualItemRect(item).center())
        self.assertFalse(self.path.exists());self.assertTrue(other.exists())

    def test_missing_project_can_only_be_removed_from_recents(self):
        self.path.unlink();self.welcome.recents.setCurrentRow(0)
        keep = self.ws.write('chronicles/mine/keep.txt', 'keep')
        with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
            self.welcome.delete_recent()
        self.assertTrue(keep.exists());self.assertEqual(self.welcome.recents.count(), 0)

    def test_open_project_cannot_be_deleted(self):
        lock = ProjectLock(self.path);self.assertTrue(lock.acquire())
        try:
            with self.assertRaisesRegex(ValueError, 'abierta'):delete_project(self.ws, self.path)
            self.assertTrue(self.path.exists());self.assertEqual(len(self.prefs.data['recent_projects']), 1)
        finally:lock.release()

    def test_standalone_yaml_preserves_folder_and_shared_assets(self):
        path = self.ws.write('custom/story.yml', 'chronicle: {}')
        self.ws.write('custom/story.yml.autosave', 'draft');keep = self.ws.write('custom/picture.tga', 'keep')
        self.assertEqual(project_deletion_target(self.ws, path), path)
        delete_project(self.ws, path)
        self.assertFalse(path.exists());self.assertFalse(Path(str(path)+'.autosave').exists());self.assertTrue(keep.exists())

    def test_workspace_roots_reserved_dirs_and_nested_projects_are_protected(self):
        for relative in ('project.yaml', 'chronicles/project.yaml', 'user_workspaces/project.yaml', 'src/user/project.yaml'):
            with self.subTest(relative=relative):
                path = self.ws.write(relative, 'chronicle: {}')
                with self.assertRaises(ValueError):delete_project(self.ws, path)
                self.assertTrue(path.exists());path.unlink()
        nested = self.ws.write('chronicles/mine/child/project.yaml', 'chronicle: {}')
        for path in (self.path, nested):
            with self.assertRaises(ValueError):delete_project(self.ws, path)
        self.assertTrue(nested.exists());self.assertTrue(self.path.exists())

    def test_bundled_master_is_protected_but_working_copy_is_deletable(self):
        with patch('rcm.product.example_root', return_value=self.ws.root/'chronicles'):
            master = self.ws.write('chronicles/tutorial/project.yaml', 'chronicle: {}')
            with self.assertRaisesRegex(ValueError, 'ejemplo original'):delete_project(self.ws, master)
            self.assertTrue(master.exists())
        delete_project(self.ws, self.path);self.assertFalse(self.path.exists())

    def test_link_in_assets_aborts_before_deleting_anything(self):
        outside = self.root/'outside.txt';outside.write_text('private')
        link = self.path.parent/'linked.txt'
        os.link(outside, link)
        try:
            with self.assertRaises(ValueError):delete_project(self.ws, self.path)
            self.assertTrue(self.path.exists());self.assertEqual(outside.read_text(), 'private')
        finally:link.unlink()

    def test_windows_reparse_directory_is_rejected_before_descending(self):
        linked = self.path.parent/'linked';linked.mkdir()
        real_lstat = Path.lstat
        def reparse(path):
            info = real_lstat(path)
            if path == linked:
                return SimpleNamespace(st_mode=info.st_mode, st_nlink=info.st_nlink, st_file_attributes=0x400)
            return info
        with patch.object(Path, 'lstat', reparse), self.assertRaises(ValueError):
            delete_project(self.ws, self.path)
        self.assertTrue(self.path.exists());self.assertTrue(linked.exists())

    def test_confirmation_and_button_are_translated_in_both_languages(self):
        from rcm.editor import i18n
        for code, label, title in [('en', 'Delete chronicle…', 'Delete chronicle'), ('es', 'Eliminar crónica…', 'Eliminar crónica')]:
            with self.subTest(language=code), patch.object(i18n, '_language', code):
                welcome = Welcome(self.win)
                try:
                    self.assertEqual(welcome.delete_button.text(), label)
                    welcome.recents.setCurrentRow(0)
                    with patch.object(QMessageBox, 'warning', return_value=QMessageBox.StandardButton.No) as dialog:
                        welcome.delete_recent()
                    self.assertEqual(dialog.call_args.args[1], title)
                    self.assertTrue(self.path.exists())
                finally:welcome.close();welcome.deleteLater()

    def test_validation_or_disk_failure_preserves_recent_entry(self):
        with patch.object(Path, 'unlink', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):delete_project(self.ws, self.path)
        self.assertTrue(self.path.exists());self.assertEqual(len(self.prefs.data['recent_projects']), 1)
