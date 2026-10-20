"""Redirect legacy shared-fixture backups into a disposable test directory."""
from contextlib import contextmanager
from pathlib import Path
import tempfile
from unittest.mock import patch

from rcm.paths import Workspace


@contextmanager
def isolated_repository_backups(root):
    """Exercise the real backup policy without pruning local project recovery.

    Only the shared repository fixture workspace is redirected. Temporary
    workspaces created by individual tests retain their normal paths/policy.
    Path validation still runs before and after redirecting the destination.
    """
    root = Path(root).resolve()
    original = Workspace.output
    area = original(Workspace(root), 'build/tests')
    area.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='source_backups_', dir=area) as temporary:
        scratch = Path(temporary)
        def output(ws, path):
            target = original(ws, path)
            if ws.root == root and target.is_relative_to(root/'backups'):
                return original(ws, scratch/target.relative_to(root/'backups'))
            return target
        with patch.object(Workspace, 'output', output):
            yield scratch
