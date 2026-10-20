"""The full test command must preserve existing local rolling backups."""
from pathlib import Path
import importlib.util
import tempfile
from unittest import TestCase

from rcm.paths import Workspace
from rcm.project_safety import backup_source

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rcm_test_workspace', ROOT/'tools/test_workspace.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
isolated_repository_backups = module.isolated_repository_backups


class RunnerIsolationTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'build/tests')
        self.root = Path(self.temp.name)
        self.ws = Workspace(self.root)

    def tearDown(self):self.temp.cleanup()

    def test_real_retention_prunes_only_test_backups_and_keeps_existing_recovery(self):
        originals = {self.ws.write('backups/story/'+str(i)+'.yaml', 'original '+str(i)):('original '+str(i)).encode() for i in range(4)}
        with isolated_repository_backups(self.root) as scratch:
            paths = [backup_source(self.ws, 'story', ('new '+str(i)).encode(), limit=2) for i in range(4)]
            self.assertTrue(all(p.is_relative_to(scratch) for p in paths))
            self.assertEqual(len(list(self.ws.output('backups/story').glob('*.yaml'))), 2)
            self.assertEqual(self.ws.output(self.root/'backups/story'), scratch/'story')
            for path, content in originals.items():self.assertEqual(path.read_bytes(), content)
        self.assertFalse(scratch.exists())
        self.assertEqual(self.ws.output('backups/story'), self.root/'backups/story')
        for path, content in originals.items():self.assertEqual(path.read_bytes(), content)

    def test_other_workspaces_and_normal_files_keep_real_paths_and_checks(self):
        other = Workspace(self.root/'other');other.root.mkdir()
        with isolated_repository_backups(self.root):
            self.assertEqual(self.ws.write('chronicles/mine/project.yaml', 'mine'), self.root/'chronicles/mine/project.yaml')
            self.assertEqual(backup_source(other, 'story', b'backup').parent, other.root/'backups/story')
            with self.assertRaises(ValueError):self.ws.output('../outside.yaml')
        self.assertEqual((self.root/'chronicles/mine/project.yaml').read_text(), 'mine')
