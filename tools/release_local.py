"""Local release pipeline: verify, build, stage and publish without GitHub Actions.

GitHub is used only as repository, tag and release storage through the official
``gh`` CLI. Publication is always explicit and two-staged (draft, then publish);
existing published releases are never modified. All file writes stay inside the
workspace through :class:`rcm.paths.Workspace` and release outputs are staged
under ``build/release/<version>/`` so tracked files are not dirtied.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'cache/vendor')]
from rcm.paths import Workspace

REPO = 'MetisC/RedemptionChronicleMaker'
VERSION_RE = re.compile(r'^\d+\.\d+\.\d+(-rc\d+)?$')
ECJ_JAR = 'cache/toolchain/ecj-3.26.0.jar'
ECJ_SHA256 = 'ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5'
# Tracked paths whose content can alter the packaged product. Any local
# modification or untracked file there makes the build unreproducible.
PRODUCT_INPUT_DIRS = ('src/', 'tools/', 'docs/', 'chronicles/')
PRODUCT_INPUT_FILES = {
    'requirements.txt', 'requirements-dev.txt', 'requirements-editor.txt',
    'pyproject.toml', 'LICENSE', 'CHANGELOG.md', 'RELEASE_NOTES.md',
    'README.md', 'README.en.md', 'editor.py'}
MIN_FREE_BYTES = 3 * 1024 ** 3


class ReleaseError(Exception):
    """Blocking failure with a human-readable recovery hint."""


def _default_runner(argv, cwd):
    return subprocess.run(argv, cwd=cwd, capture_output=True)


def _text(data):
    return data.decode('utf-8', 'replace') if isinstance(data, bytes) else data


def _out(result):
    return _text(result.stdout)


def _err(result):
    return (_text(result.stderr) or _text(result.stdout)).strip()


class Git:
    def __init__(self, runner=_default_runner):
        self.runner = runner

    def __call__(self, *args, check=True):
        try:
            result = self.runner(['git', *args], ROOT)
        except OSError as exc:
            raise ReleaseError(f'git not runnable: {exc}')
        if check and result.returncode:
            raise ReleaseError(f"git {' '.join(args)} failed: {_err(result)}")
        return _out(result)


def find_gh():
    """Locate gh.exe on PATH or in canonical Windows install locations."""
    found = shutil.which('gh')
    if found:
        return found
    local = os.environ.get('LOCALAPPDATA', '')
    candidates = [
        Path('C:/Program Files/GitHub CLI/gh.exe'),
        Path(local) / 'Microsoft/WinGet/Links/gh.exe',
        *sorted(Path(local).glob('Microsoft/WinGet/Packages/GitHub.cli*/bin/gh.exe'))]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


class Gh:
    """Official GitHub CLI; the only remote-write channel allowed."""

    def __init__(self, runner=_default_runner, repo=REPO, exe=None):
        self.runner = runner
        self.repo = repo
        self.exe = exe

    def _bin(self):
        return self.exe or find_gh() or 'gh'

    def __call__(self, *args, binary=False):
        try:
            result = self.runner([self._bin(), *args], ROOT)
        except OSError:
            raise ReleaseError('github cli not found; install: winget install --id GitHub.cli')
        if result.returncode:
            raise ReleaseError(f"gh {' '.join(args)} failed: {_err(result)}")
        return result.stdout if binary else _text(result.stdout)

    def api_json(self, path, *extra):
        return json.loads(self('api', path, *extra))

    def release_json(self, tag):
        """Release metadata dict, or None when the tag has no release."""
        try:
            result = self.runner(
                [self._bin(), 'release', 'view', tag, '--repo', self.repo, '--json',
                 'id,url,tagName,name,body,isDraft,isPrerelease,isImmutable,'
                 'targetCommitish,createdAt,publishedAt,assets'], ROOT)
        except OSError:
            raise ReleaseError('github cli not found; install: '
                               'winget install --id GitHub.cli')
        if result.returncode or not result.stdout.strip():
            return None
        return json.loads(_out(result))


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def app_version(root=None):
    root = root or ROOT
    text = (root / 'src/rcm/__init__.py').read_text(encoding='utf-8')
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not match:
        raise ReleaseError('Cannot read __version__ from src/rcm/__init__.py')
    return match.group(1)


def tag_for(version):
    return 'v' + version


def stage_dir(version, root=None):
    return (root or ROOT) / 'build/release' / version


def zip_name(version):
    return f'RedemptionChronicleMaker-{version}-win64.zip'


def is_product_input(path):
    path = path.replace('\\', '/').lstrip('/')
    if any(path.startswith(d) for d in PRODUCT_INPUT_DIRS):
        return True
    return path in PRODUCT_INPUT_FILES


def worktree_status(git):
    """Classify `git status --porcelain` entries into product/other paths."""
    product, other = [], []
    for line in git('status', '--porcelain').splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if ' -> ' in path:
            path = path.split(' -> ', 1)[1]
        path = path.strip().strip('"')
        (product if is_product_input(path) else other).append(
            {'status': line[:2].strip(), 'path': path})
    return product, other


def remote_tag_commit(git, tag):
    """Peeled commit of a remote tag, or None when absent."""
    out = git('ls-remote', 'origin', f'refs/tags/{tag}*')
    peeled, direct = None, None
    for line in out.splitlines():
        sha, ref = line.split('\t')
        if ref == f'refs/tags/{tag}^{{}}':
            peeled = sha
        elif ref == f'refs/tags/{tag}':
            direct = sha
    return peeled or direct


def remote_branch_commit(git, branch='main'):
    out = git('ls-remote', 'origin', f'refs/heads/{branch}').strip()
    return out.split('\t')[0] if out else None


def local_tag_commit(git, tag):
    out = git('rev-parse', '-q', '--verify', f'refs/tags/{tag}^{{commit}}',
              check=False).strip()
    return out or None


def version_published_tags(git):
    tags = {}
    for line in git('ls-remote', '--tags', 'origin').splitlines():
        sha, ref = line.split('\t')
        name = ref.removeprefix('refs/tags/').removesuffix('^{}')
        if not ref.endswith('^{}'):
            tags.setdefault(name, {})['object'] = sha
        else:
            tags.setdefault(name, {})['commit'] = sha
    return {name: v.get('commit', v['object']) for name, v in tags.items()}


def notes_cover(notes_path, version):
    if not notes_path.is_file():
        return False
    pattern = re.compile(r'^#.*' + re.escape(version) + r'\b', re.M)
    return bool(pattern.search(notes_path.read_text(encoding='utf-8')))


# --------------------------------------------------------------------------
# Phase reports
# --------------------------------------------------------------------------

def phase_check(env_run=_default_runner):
    """Environment diagnostics; every entry has ok/detail/required."""
    entries = []

    def add(name, ok, detail='', required=True):
        entries.append({'name': name, 'ok': bool(ok), 'detail': detail,
                        'required': required})

    version = sys.version_info
    add('python', version >= (3, 10),
        f'{version.major}.{version.minor}.{version.micro}'
        + ('' if version[:2] == (3, 12) else ' (CI reference is 3.12)'))
    try:
        git = Git(env_run)
        add('git', True, git('--version').strip())
        add('repository', git('rev-parse', '--is-inside-work-tree').strip() == 'true',
            str(ROOT))
        remote = git('remote', 'get-url', 'origin', check=False).strip()
        add('remote origin', REPO in remote, remote or 'missing')
    except ReleaseError as exc:
        add('git', False, str(exc))
    for folder, probe in (('cache/vendor', 'PySide6'), ('cache/devtools', 'ruff')):
        target = ROOT / folder
        names = [p.name.lower() for p in target.iterdir()] if target.is_dir() else []
        has_probe = any(n == probe.lower() or n.startswith(probe.lower() + '-')
                        or n == probe.lower() + '.py' for n in names)
        add(folder, bool(names) and has_probe,
            'present' if has_probe else f'missing - pip install -r into {folder}')
    ecj = ROOT / ECJ_JAR
    if ecj.is_file():
        digest = sha256_file(ecj)
        add('ecj-3.26.0', digest == ECJ_SHA256,
            'sha256 verified' if digest == ECJ_SHA256 else f'HASH MISMATCH {digest}')
    else:
        add('ecj-3.26.0', False, f'missing {ECJ_JAR}')
    try:
        from build_portable import resolve_jlink
        add('jlink', True, str(resolve_jlink()))
    except Exception as exc:
        add('jlink', False, str(exc))
    try:
        result = env_run(['java', '-version'], ROOT)
        java_ok = result.returncode == 0 and '"21' in _err(result)
        add('java 21', java_ok, _err(result).splitlines()[0] if _err(result) else 'not found')
    except OSError:
        add('java 21', False, 'not found')
    gh_path = find_gh()
    add('github cli', bool(gh_path),
        gh_path or 'install: winget install --id GitHub.cli')
    if gh_path:
        result = env_run([gh_path, 'auth', 'status'], ROOT)
        add('gh auth', result.returncode == 0,
            'authenticated' if result.returncode == 0 else 'run: gh auth login')
        if result.returncode == 0:
            try:
                perms = Gh(env_run).api_json(f'repos/{REPO}').get('permissions', {})
                add('repo permissions', perms.get('push'), json.dumps(perms), required=False)
            except ReleaseError as exc:
                add('repo permissions', False, str(exc), required=False)
    free = shutil.disk_usage(ROOT.drive or str(ROOT)).free
    add('disk space', free >= MIN_FREE_BYTES, f'{free // 1024 ** 3} GiB free')
    try:
        probe = Workspace(ROOT).output('build/.release_probe')
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text('ok')
        probe.unlink()
        add('workspace writable', True, 'build/')
    except Exception as exc:
        add('workspace writable', False, str(exc))
    try:
        from rcm.deployment import default_game
        game = default_game(ROOT)
        add('game installation', game is not None,
            str(game) if game else 'not detected (native-sector step may fail)',
            required=False)
    except Exception as exc:
        add('game installation', False, str(exc), required=False)
    ok = all(e['ok'] for e in entries if e['required'])
    return {'successful': ok, 'checks': entries}


def phase_prepare(git, require_clean=True, strict_remote=True):
    """Version, notes and Git state gate shared by build and publish."""
    errors, warnings = [], []
    version = app_version()
    tag = tag_for(version)
    if not VERSION_RE.match(version):
        errors.append(f'unsupported version format: {version} (want X.Y.Z or X.Y.Z-rcN)')
    head = git('rev-parse', 'HEAD').strip()
    branch = git('rev-parse', '--abbrev-ref', 'HEAD').strip()
    if branch != 'main':
        warnings.append(f'current branch is {branch}, not main')
    product, other = worktree_status(git)
    if product:
        detail = ', '.join(f"{e['path']} ({e['status'] or '??'})" for e in product[:10])
        message = 'product inputs with uncommitted changes: ' + detail
        (errors if require_clean else warnings).append(message)
    if other:
        warnings.append('uncommitted changes outside product inputs: '
                        + ', '.join(e['path'] for e in other[:10]))
    remote_main = remote_branch_commit(git)
    synced = remote_main == head
    if not synced:
        warnings.append(f'HEAD {head[:8]} != origin/main {remote_main and remote_main[:8]}'
                        ' (publish requires the tagged commit to be pushed)')
    local_tag = local_tag_commit(git, tag)
    remote_tag = remote_tag_commit(git, tag)
    if remote_tag and remote_tag != head:
        detail = (f'remote tag {tag} already exists on {remote_tag[:8]} '
                  f'!= HEAD {head[:8]}; bump the version')
        (errors if strict_remote else warnings).append(detail)
    if local_tag and local_tag != head:
        warnings.append(f'local tag {tag} points to {local_tag[:8]}, will be recreated')
    notes = notes_cover(ROOT / 'RELEASE_NOTES.md', version)
    changelog = notes_cover(ROOT / 'CHANGELOG.md', version)
    if not notes:
        errors.append(f'RELEASE_NOTES.md has no heading for {version}')
    if not changelog:
        warnings.append(f'CHANGELOG.md has no heading for {version}')
    published = version_published_tags(git)
    known = sorted(n for n in published if re.match(r'^v\d+\.\d+\.\d+-rc\d+$', n))
    report = {
        'successful': not errors, 'version': version, 'tag': tag, 'head': head,
        'branch': branch, 'remote_main': remote_main, 'head_pushed': synced,
        'local_tag_commit': local_tag, 'remote_tag_commit': remote_tag,
        'product_inputs_dirty': product, 'other_dirty': other,
        'release_notes': notes, 'changelog': changelog,
        'is_prerelease': bool(re.search(r'-rc\d+$', version)),
        'existing_remote_tags': known,
        'errors': errors, 'warnings': warnings}
    return report


# --------------------------------------------------------------------------
# Build pipeline
# --------------------------------------------------------------------------

def _step(runner, argv, log):
    result = runner(argv, ROOT)
    log.append({'command': ' '.join(argv), 'returncode': result.returncode,
                'tail': (_text(result.stdout) + _text(result.stderr))[-4000:]})
    if result.returncode:
        tail = _text(result.stdout)[-2000:] or _text(result.stderr)[-2000:]
        raise ReleaseError(f"step failed ({result.returncode}): {' '.join(argv)}\n{tail}")
    return result


def phase_build(runner=_default_runner, skip_quality=False, out=print):
    ws = Workspace(ROOT)
    git = Git(runner)
    report = phase_prepare(git, require_clean=True, strict_remote=False)
    if not report['successful']:
        raise ReleaseError('prepare gate failed: ' + '; '.join(report['errors']))
    for warning in report['warnings']:
        out('warning: ' + warning)
    version, tag, head = report['version'], report['tag'], report['head']
    stage = stage_dir(version)
    ws.output(stage).mkdir(parents=True, exist_ok=True)
    before = (head, worktree_status(git)[0])
    log = []
    quality = {'status': 'skipped'}
    if not skip_quality:
        out('== full offline quality suite ==')
        _step(runner, [sys.executable, 'tools/quality.py', '--no-coverage'], log)
        quality = json.loads((ROOT / 'build/tests/quality_report.json')
                             .read_text(encoding='utf-8'))
        if not quality.get('successful'):
            raise ReleaseError('quality suite reported failures')
        quality = {'status': 'passed',
                   'report': 'build/tests/quality_report.json'}
        try:
            tests = json.loads((ROOT / 'build/tests/test_report.json')
                               .read_text(encoding='utf-8'))
            quality['tests'] = tests.get('tests')
            quality['failures'] = tests.get('failures')
            quality['errors'] = tests.get('errors')
        except (OSError, json.JSONDecodeError):
            pass
    out('== portable build ==')
    _step(runner, [sys.executable, 'tools/build_portable.py'], log)
    out('== frozen source verification ==')
    _step(runner, [sys.executable, 'tools/verify_frozen_sources.py',
                   '--report', str(stage / 'frozen_sources.json')], log)
    out('== product audit and packaging ==')
    archive = stage / zip_name(version)
    _step(runner, [sys.executable, 'tools/product_release.py',
                   '--folder', 'build/portable/RedemptionChronicleMaker',
                   '--output', str(archive), '--manifest',
                   str(stage / 'release_manifest.json'),
                   '--report', str(stage / 'product_audit.json')], log)
    manifest = json.loads((stage / 'release_manifest.json').read_text(encoding='utf-8'))
    problems = []
    if manifest.get('version') != version:
        problems.append('manifest version mismatch')
    if manifest.get('user_zip') != archive.name:
        problems.append('manifest archive name mismatch')
    if manifest.get('sha256') != sha256_file(archive):
        problems.append('manifest sha256 does not match archive')
    if manifest.get('size') != archive.stat().st_size:
        problems.append('manifest size does not match archive')
    if not manifest.get('all_hashes_verified'):
        problems.append('audit did not verify every file hash')
    audit = json.loads((stage / 'product_audit.json').read_text(encoding='utf-8'))
    if not audit.get('successful'):
        problems.append('product audit failed: ' + '; '.join(audit.get('errors', [])))
    import zipfile
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    if len(names) != manifest.get('files'):
        problems.append(f"zip entries {len(names)} != manifest files {manifest.get('files')}")
    if problems:
        raise ReleaseError('archive verification failed: ' + '; '.join(problems))
    sums = f"{manifest['sha256']}  {archive.name}\n"
    ws.write(stage / 'SHA256SUMS.txt', sums)
    after = (git('rev-parse', 'HEAD').strip(), worktree_status(git)[0])
    if after != before:
        raise ReleaseError('source state changed during the build; investigate before retrying')
    receipt = {
        'state': 'COMPILED_LOCALLY', 'version': version, 'tag': tag,
        'source_commit': head, 'built_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'quality': quality, 'product_audit_successful': audit['successful'],
        'audit_file_count': len(audit['files']),
        'archive': {'name': archive.name, 'size': archive.stat().st_size,
                    'sha256': manifest['sha256']},
        'assets': [archive.name, 'release_manifest.json', 'SHA256SUMS.txt'],
        'steps': log, 'warnings': report['warnings']}
    ws.write(stage / 'build_receipt.json', json.dumps(receipt, indent=2))
    out(f"== staged in {stage} ==")
    out(f"  {archive.name}  {manifest['sha256']}")
    return receipt


# --------------------------------------------------------------------------
# Remote planning and publication
# --------------------------------------------------------------------------

def _gh_ready(gh):
    """Authentication and repository access required for remote reads/writes."""
    gh('auth', 'status')
    perms = gh.api_json(f'repos/{gh.repo}').get('permissions', {})
    if not perms.get('push'):
        raise ReleaseError(f'no push permission on {gh.repo}: {perms}')


def _load_receipt(version):
    receipt_path = stage_dir(version) / 'build_receipt.json'
    if not receipt_path.is_file():
        raise ReleaseError(f'no staged build for {version}; run -Build first')
    return json.loads(receipt_path.read_text(encoding='utf-8'))


def phase_plan(runner=_default_runner, out=print):
    """Read-only publication preview. No remote writes, no tags, no releases."""
    git, gh = Git(runner), Gh(runner)
    report = phase_prepare(git, require_clean=True)
    errors = list(report['errors'])
    if not report['head_pushed']:
        errors.append('HEAD is not pushed to origin/main')
    try:
        _gh_ready(gh)
        remote_ok, gh_detail = True, 'authenticated with push access'
    except ReleaseError as exc:
        remote_ok, gh_detail = False, str(exc)
        errors.append('github cli: ' + str(exc))
    release = None
    if remote_ok:
        release = gh.release_json(report['tag'])
        if release and not release['isDraft']:
            errors.append(f"release {report['tag']} is already published; "
                          'published assets are immutable - bump the version')
    receipt = None
    try:
        receipt = _load_receipt(report['version'])
        if receipt['source_commit'] != report['head']:
            errors.append('staged build came from a different commit; rebuild')
        if receipt['quality'].get('status') != 'passed':
            errors.append('staged build lacks a passed full quality suite')
    except ReleaseError as exc:
        errors.append(str(exc))
    report.update({'remote_ok': remote_ok, 'gh_detail': gh_detail,
                   'existing_release': bool(release),
                   'existing_release_draft': bool(release and release['isDraft']),
                   'staged': bool(receipt),
                   'will_publish': False, 'errors': errors})
    report['successful'] = not errors
    if report['successful']:
        out('Publication plan (nothing will be sent):')
        out(f"  version {report['version']} -> tag {report['tag']} on {report['head'][:8]}")
        out(f"  prerelease: {report['is_prerelease']}")
        if receipt:
            out(f"  assets: {', '.join(receipt['assets'])}")
            out(f"  archive sha256: {receipt['archive']['sha256']}")
        out(f"  draft first, then publish to {REPO}")
    return report


def _release_assets_ok(release, expected):
    """Compare remote asset names/sizes with the expected local files."""
    remote = {a['name']: a['size'] for a in release.get('assets', [])}
    problems = []
    for name, size in expected.items():
        if name not in remote:
            problems.append(f'missing remote asset {name}')
        elif remote[name] != size:
            problems.append(f'remote asset {name} size {remote[name]} != {size}')
    extra = set(remote) - set(expected)
    if extra:
        problems.append('unexpected remote assets: ' + ', '.join(sorted(extra)))
    return problems


def _download_asset(gh, asset, dest):
    url = asset.get('url')
    if url:
        path = url.replace('https://api.github.com/', '')
        data = gh('api', path, '-H', 'Accept: application/octet-stream', binary=True)
        dest.write_bytes(data)
        return
    raise ReleaseError(f"asset {asset.get('name')} has no download url")


def phase_publish(runner=_default_runner, confirm_tag=None, stable=False,
                  input_fn=input, out=print):
    git, gh = Git(runner), Gh(runner)
    report = phase_plan(runner, out=lambda *a: None)
    if not report['successful']:
        raise ReleaseError('publication gate failed: ' + '; '.join(report['errors']))
    version, tag, head = report['version'], report['tag'], report['head']
    if not report['is_prerelease'] and not stable:
        raise ReleaseError(f'{version} is a stable version; rerun with -Stable to '
                           'authorise marking it as the latest release')
    if confirm_tag is None:
        out(f'About to publish {tag} ({version}) to {REPO} from commit {head[:8]}.')
        try:
            confirm_tag = input_fn(f'Type {tag} to confirm publication: ').strip()
        except EOFError:
            confirm_tag = ''
    if confirm_tag != tag:
        raise ReleaseError('publication cancelled: confirmation did not match ' + tag)
    stage = stage_dir(version)
    receipt = _load_receipt(version)
    expected = {n: (stage / n).stat().st_size for n in receipt['assets']}
    lock = stage / 'publish.lock'
    fd = None
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ReleaseError(f'another publication of {version} is already running '
                           f'(remove {lock} only if it is stale)')
    try:
        # ---- tag: create only if absent, push, verify remote peeled commit
        if local_tag_commit(git, tag) != head:
            if local_tag_commit(git, tag):
                raise ReleaseError(f'local tag {tag} points elsewhere; refusing to move it')
            git('tag', '-a', tag, head, '-m', f'Redemption Chronicle Maker {version}')
        remote = remote_tag_commit(git, tag)
        if remote is None:
            git('push', 'origin', f'refs/tags/{tag}')
            remote = remote_tag_commit(git, tag)
        if remote != head:
            raise ReleaseError(f'remote tag {tag} resolves to {remote and remote[:8]}, '
                               f'expected {head[:8]}')
        out(f'tag {tag} verified on remote commit {head[:8]}')

        # ---- draft release with assets
        release = gh.release_json(tag)
        asset_paths = [stage / n for n in receipt['assets']]
        if release is None:
            args = ['release', 'create', tag, '--repo', gh.repo,
                    '--title', f'Redemption Chronicle Maker {version}',
                    '--notes-file', str(ROOT / 'RELEASE_NOTES.md'),
                    '--verify-tag', '--draft']
            args += ['--prerelease', '--latest=false'] if report['is_prerelease'] \
                else ['--latest=true']
            gh(*args, *[str(p) for p in asset_paths])
            out(f'draft release created with {len(asset_paths)} assets')
        elif release['isDraft']:
            missing = [p for p in asset_paths
                       if p.name not in {a['name'] for a in release.get('assets', [])}]
            present = [a for a in release.get('assets', [])
                       if a['name'] in expected]
            bad = [a['name'] for a in present if a['size'] != expected[a['name']]]
            if bad:
                raise ReleaseError('draft assets with wrong size: ' + ', '.join(bad) +
                                   '; delete them with `gh release delete-asset` and retry')
            if missing:
                gh('release', 'upload', tag, '--repo', gh.repo,
                   *[str(p) for p in missing])
                out(f'uploaded {len(missing)} missing draft assets')
        else:
            raise ReleaseError(f'release {tag} is already published; refusing to modify it')

        # ---- verify draft content before publishing (names, sizes, bytes)
        release = gh.release_json(tag)
        if not release or not release['isDraft']:
            raise ReleaseError(f'draft release {tag} not found after creation')
        problems = _release_assets_ok(release, expected)
        if problems:
            raise ReleaseError('draft assets incomplete: ' + '; '.join(problems) +
                               '; fix with gh release delete-asset/upload, then retry')
        with tempfile.TemporaryDirectory(prefix='rcm_draft_') as tmp:
            for asset in release['assets']:
                dest = Path(tmp) / asset['name']
                _download_asset(gh, asset, dest)
                local = stage / asset['name']
                if sha256_file(dest) != sha256_file(local):
                    raise ReleaseError(f"draft asset {asset['name']} bytes differ from "
                                       'the staged file; delete the remote asset and retry')
        out('draft assets verified byte-for-byte')

        # ---- publish the draft
        gh('api', f"repos/{gh.repo}/releases/{release['id']}",
           '-X', 'PATCH', '-f', 'draft=false')
        out('release published')

        # ---- remote verification: download what GitHub stored
        final = gh.release_json(tag)
        if not final or final['isDraft']:
            raise ReleaseError('release still marked as draft after publish')
        if final['isPrerelease'] != report['is_prerelease']:
            raise ReleaseError('published release has wrong prerelease classification')
        if final['tagName'] != tag:
            raise ReleaseError('published release tag mismatch')
        problems = _release_assets_ok(final, expected)
        if problems:
            raise ReleaseError('published assets incomplete: ' + '; '.join(problems))
        verified = []
        with tempfile.TemporaryDirectory(prefix='rcm_verify_') as tmp:
            for name in expected:
                gh('release', 'download', tag, '--repo', gh.repo,
                   '--dir', tmp, '--pattern', name, '--clobber')
                dest = Path(tmp) / name
                digest = sha256_file(dest)
                if digest != sha256_file(stage / name):
                    raise ReleaseError(f'downloaded {name} hash {digest} differs from '
                                       'the staged build')
                verified.append({'name': name, 'sha256': digest})
        receipt_out = {
            'state': ['COMPILED_LOCALLY', 'PUBLISHED_TO_GITHUB',
                      'REMOTE_DOWNLOAD_VERIFIED'],
            'version': version, 'tag': tag, 'source_commit': head,
            'published_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'release_url': final['url'], 'prerelease': final['isPrerelease'],
            'immutable': final.get('isImmutable'), 'assets_verified': verified,
            'quality': receipt['quality'],
            'product_audit_successful': receipt['product_audit_successful'],
            'archive': receipt['archive']}
        Workspace(ROOT).write(stage / 'publish_receipt.json',
                              json.dumps(receipt_out, indent=2))
        out(f"remote download verified; receipt: {stage / 'publish_receipt.json'}")
        out(f"release url: {final['url']}")
        return receipt_out
    finally:
        if fd is not None:
            os.close(fd)
        if lock.exists():
            lock.unlink()


def phase_verify(runner=_default_runner, tag=None, out=print):
    """Re-check a published release: metadata, sizes and real downloaded bytes.

    The release's own manifest and SHA256SUMS are the reference, so this also
    works when no local staging exists (e.g. auditing historical releases).
    """
    git, gh = Git(runner), Gh(runner)
    tag = tag or tag_for(app_version())
    release = gh.release_json(tag)
    if release is None:
        raise ReleaseError(f'no release found for {tag}')
    problems = []
    if release['isDraft']:
        problems.append('release is still a draft')
    remote_assets = {a['name']: a for a in release.get('assets', [])}
    required = {'release_manifest.json', 'SHA256SUMS.txt'}
    zips = {n for n in remote_assets if n.endswith('.zip')}
    missing = required - set(remote_assets)
    if missing:
        problems.append('missing required assets: ' + ', '.join(sorted(missing)))
    if len(zips) != 1:
        problems.append(f'expected exactly one zip asset, found {sorted(zips)}')
    verified = []
    downloads = {}
    manifest = {}
    declared = {}
    with tempfile.TemporaryDirectory(prefix='rcm_verify_') as tmp:
        for name, asset in remote_assets.items():
            gh('release', 'download', tag, '--repo', gh.repo,
               '--dir', tmp, '--pattern', name, '--clobber')
            dest = Path(tmp) / name
            digest = sha256_file(dest)
            downloads[name] = digest
            row = {'name': name, 'size': dest.stat().st_size, 'sha256': digest,
                   'size_matches': dest.stat().st_size == asset['size']}
            if not row['size_matches']:
                problems.append(f'{name} size differs from metadata')
            verified.append(row)
        zip_name = next(iter(zips), None)
        if 'release_manifest.json' in downloads:
            try:
                manifest = json.loads(
                    (Path(tmp) / 'release_manifest.json').read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                problems.append('release_manifest.json is not valid JSON')
        if manifest.get('sha256') and zip_name:
            if manifest['sha256'] != downloads[zip_name]:
                problems.append('zip sha256 differs from release_manifest.json')
        if manifest.get('user_zip') and manifest['user_zip'] != zip_name:
            problems.append('manifest archive name mismatch')
        if 'SHA256SUMS.txt' in downloads:
            declared = {l.split()[-1]: l.split()[0] for l in
                        (Path(tmp) / 'SHA256SUMS.txt').read_text().splitlines()
                        if l.strip()}
        for name, digest in declared.items():
            if downloads.get(name) != digest:
                problems.append(f'{name} differs from SHA256SUMS.txt')
    stage = stage_dir(tag.lstrip('v'))
    local_manifest = stage / 'release_manifest.json'
    if local_manifest.is_file() and zip_name:
        local = json.loads(local_manifest.read_text(encoding='utf-8'))
        if local.get('sha256') != downloads.get(zip_name):
            problems.append('remote zip differs from local staged manifest')
    remote_commit = remote_tag_commit(git, tag)
    report = {'tag': tag, 'url': release.get('url'), 'draft': release['isDraft'],
              'prerelease': release['isPrerelease'],
              'immutable': release.get('isImmutable'),
              'remote_tag_commit': remote_commit, 'assets': verified,
              'successful': not problems, 'problems': problems}
    out(json.dumps(report, indent=2))
    if problems:
        raise ReleaseError('remote verification failed: ' + '; '.join(problems))
    return report


def draft_notes(git, out_path=None):
    """Editable release-notes draft from real history; never auto-published."""
    published = sorted(version_published_tags(git),
                       key=lambda t: [int(x) for x in re.findall(r'\d+', t)])
    base = published[-1] if published else None
    range_spec = f'{base}..HEAD' if base else 'HEAD'
    commits = git('log', '--format=%h %s', range_spec).splitlines()
    files = git('diff', '--name-only', range_spec).splitlines() if base else []
    code = sorted(f for f in files if f.startswith(('src/', 'tools/')))
    docs = sorted(f for f in files if f.startswith(('docs/', 'chronicles/')))
    lines = [f'# DRAFT release notes for {app_version()} - REVIEW BEFORE PUBLISHING',
             '', f'Changes since {base or "repository start"}:', '',
             *[f'- {c}' for c in commits], '',
             '## Code touched', '', *[f'- {f}' for f in code], '',
             '## Docs/chronicles touched', '', *[f'- {f}' for f in docs], '',
             'Remember: offline tests do not certify native gameplay. Keep manual',
             'acceptance items (DYN01-12, MANUAL_RUNTIME_CHECKLIST) listed as pending.',
             '']
    text = '\n'.join(lines)
    dest = out_path or ROOT / 'build/release/notes_draft.md'
    Workspace(ROOT).write(dest, text)
    return dest


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(prog='release_local',
                                     description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    sub.add_parser('prepare')
    p_build = sub.add_parser('build')
    p_build.add_argument('--skip-quality', action='store_true',
                         help='diagnostic builds only; such output can never be published')
    sub.add_parser('plan')
    p_pub = sub.add_parser('publish')
    p_pub.add_argument('--confirm-tag')
    p_pub.add_argument('--stable', action='store_true')
    p_ver = sub.add_parser('verify')
    p_ver.add_argument('tag', nargs='?')
    p_notes = sub.add_parser('notes')
    p_notes.add_argument('out', nargs='?')
    args = parser.parse_args(argv)

    try:
        if args.command == 'check':
            report = phase_check()
            for e in report['checks']:
                mark = 'ok ' if e['ok'] else ('FAIL' if e['required'] else 'warn')
                print(f"[{mark}] {e['name']}: {e['detail']}")
            if not report['successful']:
                raise ReleaseError('environment is not ready')
        elif args.command == 'prepare':
            report = phase_prepare(Git(), require_clean=True)
            print(json.dumps(report, indent=2))
            for warning in report['warnings']:
                print('warning:', warning)
            if not report['successful']:
                raise ReleaseError('prepare failed')
        elif args.command == 'build':
            phase_build(skip_quality=args.skip_quality)
        elif args.command == 'plan':
            report = phase_plan()
            if not report['successful']:
                for e in report['errors']:
                    print('error:', e)
                raise ReleaseError('not ready to publish')
        elif args.command == 'publish':
            phase_publish(confirm_tag=args.confirm_tag, stable=args.stable)
        elif args.command == 'verify':
            phase_verify(tag=args.tag)
        elif args.command == 'notes':
            dest = draft_notes(Git(), Path(args.out) if args.out else None)
            print('draft notes written to', dest)
        return 0
    except ReleaseError as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
