"""Offline tests for tools/release_local.py using a simulated git/gh runner."""
from pathlib import Path
from types import SimpleNamespace
import json
import shutil
import sys
import unittest
import unittest.mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tools')]

import release_local as rl

SHA = 'a' * 40
OTHER_SHA = 'b' * 40


def result(stdout=b'', returncode=0, stderr=b''):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    """Records every argv and replies through ordered string-prefix routes."""

    def __init__(self):
        self.calls = []
        self.routes = []

    def when(self, prefix, reply):
        if isinstance(reply, (bytes, str)):
            payload = reply.encode() if isinstance(reply, str) else reply
            reply = result(payload)
        self.routes.append((prefix, reply))
        return self

    def __call__(self, argv, cwd):
        argv = [str(a) for a in argv]
        self.calls.append(argv)
        line = ' '.join(argv)
        for prefix, reply in reversed(self.routes):
            if line.startswith(prefix):
                return reply(argv) if callable(reply) else reply
        return result()


def base_runner(head=SHA, state=None):
    """Reads needed by prepare/plan against a clean, synced repository."""
    state = state if state is not None else {}
    r = FakeRunner()
    r.when('git rev-parse HEAD', (head + '\n').encode())
    r.when('git rev-parse --abbrev-ref', b'main\n')
    r.when('git status --porcelain', b'')
    r.when('git ls-remote origin refs/heads/main',
           f'{head}\trefs/heads/main\n'.encode())
    r.when('git ls-remote --tags origin', b'')
    r.when('gh auth status', b'Logged in to github.com')

    def api_repos(argv):
        if '-X' in argv and 'PATCH' in argv:
            state['published'] = True
            return result(b'{}')
        return result(json.dumps({'permissions': {'push': True}}).encode())
    r.when('gh api repos/' + rl.REPO, api_repos)
    return r


class VersionTests(unittest.TestCase):
    def test_current_version_is_valid(self):
        self.assertTrue(rl.VERSION_RE.match(rl.app_version()))

    def test_invalid_version_rejected(self):
        for bad in ('1.0', 'v1.0.0', '1.0.0-rc', '1.0.0-beta1', 'x'):
            self.assertFalse(rl.VERSION_RE.match(bad), bad)

    def test_is_product_input(self):
        for yes in ('src/rcm/app.py', 'tools/build_portable.py', 'docs/X.md',
                    'chronicles/mini_chronicle/project.yaml', 'RELEASE_NOTES.md',
                    'LICENSE', 'requirements.txt'):
            self.assertTrue(rl.is_product_input(yes), yes)
        for no in ('research/x.json', 'state/y.json', 'build/z.txt',
                   '.github/workflows/ci.yml', 'AGENTS.md', '.gitignore',
                   'release_manifest.json', 'SHA256SUMS.txt'):
            self.assertFalse(rl.is_product_input(no), no)


class StatusTests(unittest.TestCase):
    def status_git(self, porcelain):
        return rl.Git(FakeRunner().when('git status --porcelain', porcelain))

    def test_clean_tree(self):
        product, other = rl.worktree_status(self.status_git(b''))
        self.assertEqual((product, other), ([], []))

    def test_modified_product_input(self):
        product, other = rl.worktree_status(self.status_git(b' M src/rcm/model.py\n'))
        self.assertEqual(product[0]['path'], 'src/rcm/model.py')
        self.assertEqual(other, [])

    def test_untracked_product_input(self):
        product, _ = rl.worktree_status(self.status_git(b'?? src/rcm/new.py\n'))
        self.assertEqual(product[0]['path'], 'src/rcm/new.py')

    def test_exempt_paths(self):
        product, other = rl.worktree_status(self.status_git(
            b' M research/x.json\n M .gitignore\n M release_manifest.json\n'))
        self.assertEqual(product, [])
        self.assertEqual(len(other), 3)

    def test_rename_takes_new_path(self):
        product, _ = rl.worktree_status(
            self.status_git(b'R  src/old.py -> src/rcm/model.py\n'))
        self.assertEqual(product[0]['path'], 'src/rcm/model.py')


class PrepareTests(unittest.TestCase):
    def test_remote_tag_on_other_commit_blocks(self):
        tag = rl.tag_for(rl.app_version())
        r = base_runner()
        r.when('git ls-remote origin refs/tags/' + tag,
               f'x\trefs/tags/{tag}\n{OTHER_SHA}\trefs/tags/{tag}^{{}}\n'.encode())
        report = rl.phase_prepare(rl.Git(r), require_clean=True)
        self.assertFalse(report['successful'])
        self.assertTrue(any('already exists' in e for e in report['errors']))

    def test_remote_tag_on_head_allows_resume(self):
        tag = rl.tag_for(rl.app_version())
        r = base_runner()
        r.when('git ls-remote origin refs/tags/' + tag,
               f'x\trefs/tags/{tag}\n{SHA}\trefs/tags/{tag}^{{}}\n'.encode())
        r.when('git rev-parse -q --verify', SHA.encode())
        report = rl.phase_prepare(rl.Git(r), require_clean=True)
        self.assertTrue(all('already exists' not in e for e in report['errors']))

    def test_dirty_product_input_blocks(self):
        r = base_runner()
        r.when('git status --porcelain', b' M src/rcm/model.py\n')
        report = rl.phase_prepare(rl.Git(r), require_clean=True)
        self.assertFalse(report['successful'])
        self.assertTrue(any('product inputs' in e for e in report['errors']))

    def test_dirty_research_only_warns(self):
        r = base_runner()
        r.when('git status --porcelain', b' M research/x.json\n')
        report = rl.phase_prepare(rl.Git(r), require_clean=True)
        self.assertEqual(report['errors'], [])
        self.assertTrue(report['warnings'])

    def test_remote_tag_conflict_warns_when_not_strict(self):
        tag = rl.tag_for(rl.app_version())
        r = base_runner()
        r.when('git ls-remote origin refs/tags/' + tag,
               f'x\trefs/tags/{tag}\n{OTHER_SHA}\trefs/tags/{tag}^{{}}\n'.encode())
        report = rl.phase_prepare(rl.Git(r), require_clean=True, strict_remote=False)
        self.assertTrue(report['successful'])
        self.assertTrue(any('already exists' in w for w in report['warnings']))

    def test_unpushed_head_warns_in_prepare(self):
        r = base_runner()
        r.when('git ls-remote origin refs/heads/main',
               f'{OTHER_SHA}\trefs/heads/main\n'.encode())
        report = rl.phase_prepare(rl.Git(r), require_clean=True)
        self.assertFalse(report['head_pushed'])


class StageFixture:
    """Real staged artifacts under build/release/<version>/, removed after."""

    def __init__(self, version, head=SHA):
        self.stage = rl.stage_dir(version)
        self.stage.mkdir(parents=True, exist_ok=True)
        self.files = {}
        for name in (rl.zip_name(version), 'release_manifest.json',
                     'SHA256SUMS.txt'):
            path = self.stage / name
            path.write_bytes(b'content-of-' + name.encode())
            self.files[name] = path
        archive = self.files[rl.zip_name(version)]
        manifest = {'version': version, 'user_zip': rl.zip_name(version),
                    'sha256': rl.sha256_file(archive),
                    'size': archive.stat().st_size,
                    'files': 1, 'all_hashes_verified': True}
        self.files['release_manifest.json'].write_text(json.dumps(manifest))
        self.files['SHA256SUMS.txt'].write_text(
            f"{manifest['sha256']}  {manifest['user_zip']}\n")
        receipt = {'state': 'COMPILED_LOCALLY', 'version': version,
                   'source_commit': head, 'quality': {'status': 'passed'},
                   'product_audit_successful': True,
                   'archive': {'name': rl.zip_name(version),
                               'sha256': manifest['sha256'],
                               'size': manifest['size']},
                   'assets': list(self.files)}
        (self.stage / 'build_receipt.json').write_text(json.dumps(receipt))

    def destroy(self):
        shutil.rmtree(self.stage.parent, ignore_errors=True)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(unittest.mock.patch.object(
            rl, 'find_gh', lambda: 'gh').start())
        self.version = rl.app_version()
        self.stage = StageFixture(self.version)

    def tearDown(self):
        self.stage.destroy()

    def plan(self, runner):
        return rl.phase_plan(runner, out=lambda *a: None)

    def test_plan_ok(self):
        report = self.plan(base_runner())
        self.assertTrue(report['successful'], report['errors'])

    def test_plan_is_read_only(self):
        r = base_runner()
        report = self.plan(r)
        self.assertTrue(report['successful'], report['errors'])
        allowed = (('git', 'rev-parse'), ('git', 'status'),
                   ('git', 'ls-remote'), ('gh', 'auth'),
                   ('gh', 'api'), ('gh', 'release', 'view'))
        for call in r.calls:
            self.assertTrue(any(call[:len(p)] == list(p) for p in allowed), call)
            if call[:2] == ['gh', 'api']:
                self.assertNotIn('-X', call)

    def test_published_release_blocks(self):
        r = base_runner()
        r.when('gh release view',
               json.dumps({'isDraft': False, 'isPrerelease': True}).encode())
        report = self.plan(r)
        self.assertFalse(report['successful'])
        self.assertTrue(any('immutable' in e for e in report['errors']))

    def test_draft_release_allows_resume(self):
        r = base_runner()
        r.when('gh release view', json.dumps({'isDraft': True}).encode())
        report = self.plan(r)
        self.assertTrue(report['successful'], report['errors'])
        self.assertTrue(report['existing_release_draft'])

    def test_missing_build_receipt_blocks(self):
        self.stage.destroy()
        report = self.plan(base_runner())
        self.assertFalse(report['successful'])
        self.assertTrue(any('run -Build' in e for e in report['errors']))

    def test_stale_receipt_blocks(self):
        path = self.stage.stage / 'build_receipt.json'
        receipt = json.loads(path.read_text())
        receipt['source_commit'] = OTHER_SHA
        path.write_text(json.dumps(receipt))
        report = self.plan(base_runner())
        self.assertFalse(report['successful'])
        self.assertTrue(any('different commit' in e for e in report['errors']))

    def test_skipped_quality_blocks(self):
        path = self.stage.stage / 'build_receipt.json'
        receipt = json.loads(path.read_text())
        receipt['quality'] = {'status': 'skipped'}
        path.write_text(json.dumps(receipt))
        report = self.plan(base_runner())
        self.assertFalse(report['successful'])
        self.assertTrue(any('quality' in e for e in report['errors']))

    def test_gh_failure_blocks(self):
        r = base_runner()
        r.when('gh auth status', result(b'not logged in', 1))
        report = self.plan(r)
        self.assertFalse(report['successful'])


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(unittest.mock.patch.object(
            rl, 'find_gh', lambda: 'gh').start())
        self.version = rl.app_version()
        self.tag = rl.tag_for(self.version)
        self.stage = StageFixture(self.version)

    def tearDown(self):
        self.stage.destroy()

    def publish_runner(self, exists=False, has_assets=False):
        """Stateful fake: 404 until created, draft until PATCH, assets when set."""
        state = {'exists': exists, 'has_assets': has_assets,
                 'published': False, 'tag_pushed': False}
        r = base_runner(state=state)

        def ls_remote_tag(_argv):
            if state['tag_pushed']:
                return result(f'{SHA}\trefs/tags/{self.tag}^{{}}\n'.encode())
            return result()
        r.when('git ls-remote origin refs/tags/' + self.tag, ls_remote_tag)

        def push(_argv):
            state['tag_pushed'] = True
            return result()
        r.when('git push', push)

        def view(_argv):
            if not state['exists']:
                return result(b'not found', 1)
            assets = [{'name': n, 'size': p.stat().st_size,
                       'url': 'https://api.github.com/assets/' + n}
                      for n, p in self.stage.files.items()] if state['has_assets'] else []
            return result(json.dumps({
                'id': 99, 'isDraft': not state['published'],
                'isPrerelease': True, 'isImmutable': False, 'tagName': self.tag,
                'url': 'https://example/r', 'targetCommitish': SHA,
                'assets': assets}).encode())
        r.when('gh release view', view)

        def create(_argv):
            state['exists'] = True
            state['has_assets'] = True
            return result()
        r.when('gh release create', create)

        def upload(_argv):
            state['has_assets'] = True
            return result()
        r.when('gh release upload', upload)
        r.when('gh api assets',
               lambda argv: result(self.stage.files[argv[2].rsplit('/', 1)[-1]].read_bytes()))

        def download(argv):
            dest = Path(argv[argv.index('--dir') + 1])
            name = argv[argv.index('--pattern') + 1]
            (dest / name).write_bytes(self.stage.files[name].read_bytes())
            return result()
        r.when('gh release download', download)
        return r

    def test_wrong_confirm_tag_aborts(self):
        with self.assertRaises(rl.ReleaseError):
            rl.phase_publish(self.publish_runner(), confirm_tag='vNope',
                             out=lambda *a: None)

    def test_full_publish_sequence(self):
        r = self.publish_runner()
        receipt = rl.phase_publish(r, confirm_tag=self.tag, out=lambda *a: None)
        lines = [' '.join(c) for c in r.calls]
        self.assertTrue(any(l.startswith(f'git tag -a {self.tag} {SHA}')
                            for l in lines), lines)
        self.assertTrue(any(l == f'git push origin refs/tags/{self.tag}'
                            for l in lines), lines)
        create = next(c for c in r.calls if c[:3] == ['gh', 'release', 'create'])
        for flag in ('--draft', '--prerelease', '--latest=false', '--verify-tag'):
            self.assertIn(flag, create)
        patch = [c for c in r.calls if 'PATCH' in c]
        self.assertEqual(len(patch), 1)
        self.assertIn('draft=false', patch[0])
        downloads = [c for c in r.calls if c[:3] == ['gh', 'release', 'download']]
        self.assertEqual(len(downloads), len(self.stage.files))
        self.assertIn('PUBLISHED_TO_GITHUB', receipt['state'])
        self.assertIn('REMOTE_DOWNLOAD_VERIFIED', receipt['state'])

    def test_publish_leaves_no_lock(self):
        rl.phase_publish(self.publish_runner(), confirm_tag=self.tag,
                         out=lambda *a: None)
        self.assertFalse((self.stage.stage / 'publish.lock').exists())
        self.assertTrue((self.stage.stage / 'publish_receipt.json').exists())

    def test_remote_tag_mismatch_blocks(self):
        r = self.publish_runner()
        r.when('git ls-remote origin refs/tags/' + self.tag,
               f'x\trefs/tags/{self.tag}\n{OTHER_SHA}\trefs/tags/{self.tag}^{{}}\n'.encode())
        with self.assertRaises(rl.ReleaseError):
            rl.phase_publish(r, confirm_tag=self.tag, out=lambda *a: None)
        self.assertFalse(any(c[:2] == ['git', 'push'] for c in r.calls))

    def test_bad_draft_bytes_block(self):
        r = self.publish_runner()
        r.when('gh api assets', lambda _a: result(b'corrupted'))
        with self.assertRaises(rl.ReleaseError):
            rl.phase_publish(r, confirm_tag=self.tag, out=lambda *a: None)
        self.assertFalse(any('PATCH' in c for c in r.calls))

    def test_draft_resume_uploads_missing(self):
        r = self.publish_runner(exists=True, has_assets=False)
        rl.phase_publish(r, confirm_tag=self.tag, out=lambda *a: None)
        self.assertTrue(any(c[:3] == ['gh', 'release', 'upload']
                            for c in r.calls))
        self.assertFalse(any(c[:3] == ['gh', 'release', 'create']
                             for c in r.calls))

    def test_draft_with_assets_reuses_without_upload(self):
        r = self.publish_runner(exists=True, has_assets=True)
        rl.phase_publish(r, confirm_tag=self.tag, out=lambda *a: None)
        self.assertFalse(any(c[:3] == ['gh', 'release', 'upload']
                             for c in r.calls))

    def test_stable_version_requires_flag(self):
        fake_report = {'successful': True, 'version': '1.0.0',
                       'tag': 'v1.0.0', 'head': SHA, 'is_prerelease': False}
        with unittest.mock.patch.object(rl, 'phase_plan',
                                        return_value=fake_report):
            with self.assertRaises(rl.ReleaseError):
                rl.phase_publish(self.publish_runner(), confirm_tag='v1.0.0',
                                 out=lambda *a: None)


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(unittest.mock.patch.object(
            rl, 'find_gh', lambda: 'gh').start())
        self.version = rl.app_version()
        self.tag = rl.tag_for(self.version)
        self.stage = StageFixture(self.version)

    def tearDown(self):
        self.stage.destroy()

    def verify_runner(self, tamper=None):
        r = base_runner()
        r.when('gh release view', json.dumps({
            'isDraft': False, 'isPrerelease': True, 'isImmutable': False,
            'tagName': self.tag, 'url': 'https://example/r',
            'assets': [{'name': n, 'size': p.stat().st_size, 'url': 'x'}
                       for n, p in self.stage.files.items()]}).encode())

        def download(argv):
            dest = Path(argv[argv.index('--dir') + 1])
            name = argv[argv.index('--pattern') + 1]
            data = self.stage.files[name].read_bytes()
            if tamper and name in tamper:
                data = tamper[name]
            (dest / name).write_bytes(data)
            return result()
        r.when('gh release download', download)
        return r

    def test_verify_ok(self):
        report = rl.phase_verify(self.verify_runner(), out=lambda *a: None)
        self.assertTrue(report['successful'])

    def test_verify_detects_corruption(self):
        tampered = {rl.zip_name(self.version): b'evil'}
        with self.assertRaises(rl.ReleaseError):
            rl.phase_verify(self.verify_runner(tampered), out=lambda *a: None)

    def test_verify_missing_release(self):
        r = self.verify_runner()
        r.when('gh release view', result(b'not found', 1))
        with self.assertRaises(rl.ReleaseError):
            rl.phase_verify(r, out=lambda *a: None)


if __name__ == '__main__':
    unittest.main()
