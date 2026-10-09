"""Persist final Phase 9 evidence without starting or mutating the game.

--refresh-portable copies only current documentation and our circuit source.
The default mode checks build/source/deployment integrity and archives sources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'cache/vendor')]
from rcm.catalogue import digest, verify_sources
from rcm.deployment import default_game, safe_target
from rcm.document import Document
from rcm.packages import inspect_package
from rcm.paths import Workspace
from rcm.service import Backend, build_inputs_fingerprint, source_fingerprint


def refresh_portable():
    app = ROOT / 'build/portable/RedemptionChronicleMaker'
    if not (app / 'RedemptionChronicleMaker.exe').is_file():
        raise ValueError('Build portable missing')
    shutil.copy2(ROOT / 'README.md', app / 'README.md')
    shutil.copytree(ROOT / 'docs', app / 'docs', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'chronicles/circuit', app / 'examples/circuit', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('*.backup', '*.autosave', '__pycache__'))
    print('Portable documentation and unified circuit refreshed')


def finalize():
    ws = Workspace(ROOT, default_game(ROOT))
    evidence = ROOT / 'research/phase9'
    source = Document.load(ws, ROOT / 'chronicles/circuit/project.yaml').snapshot()
    report = json.loads((ROOT / 'build/rcm_circuit/build_report.json').read_text())
    if report['authoring_source_sha256'] != source_fingerprint(source):
        raise ValueError('Source changed after build')
    if report['build_inputs_sha256'] != build_inputs_fingerprint(ws, source):
        raise ValueError('Custom inputs changed after build')
    validation = Backend(ws).validate(source)
    if not validation.valid or any(p.severity in ('ERROR', 'WARNING') for p in validation.problems):
        raise ValueError('Circuit validation has errors/warnings')
    original = verify_sources(ws, ws.game)
    if not original['hashes_match']:
        raise ValueError('Original hash mismatch')
    deployed = json.loads((evidence / 'final_deployment.json').read_text())
    for relative, expected in deployed['files'].items():
        path = safe_target(ws.game, ws.game / 'RCM' / relative)
        if digest(path) != expected:
            raise ValueError('Deployed file mismatch: ' + relative)
    archives = []
    chronicles = []
    for path in sorted((ws.game / 'RCM').rglob('*.nob')):
        safe_target(ws.game, path)
        with zipfile.ZipFile(path) as z:
            names = [name for name in z.namelist() if name.startswith('chronicles/') and name.endswith('.nsc')]
        archives.append(str(path.relative_to(ws.game / 'RCM')))
        chronicles.extend(names)
    if chronicles != ['chronicles/rcm_circuit.nsc']:
        raise ValueError('Expected exactly the unified circuit in RCM: ' + str(chronicles))
    package = ROOT / 'build/rcm_circuit/rcm_circuit.rcmpack'
    inspect_package(package)
    full = json.loads((evidence / 'full_tests.json').read_text())
    focused = json.loads((evidence / 'focused_tests.json').read_text())
    portable = json.loads((evidence / 'portable_probe.json').read_text())
    gui = json.loads((evidence / 'gui/probe.json').read_text())
    if not full['successful'] or not focused['successful'] or portable['exit_code']:
        raise ValueError('Offline acceptance report failed')
    cleanup = json.loads((evidence / 'deployment_cleanup.json').read_text())
    with zipfile.ZipFile(evidence / 'retired_all_demos.zip') as z:
        if len(z.namelist()) != len(cleanup['removed']):
            raise ValueError('Retired demos backup inventory mismatch')
    source_hashes = {}
    archive = evidence / 'after_implementation.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        paths = []
        for name in ['src', 'tools', 'tests', 'docs', 'chronicles']:
            paths.extend((ROOT / name).rglob('*'))
        paths.extend(ROOT / name for name in ['AGENTS.md', 'README.md', 'pyproject.toml', 'requirements.txt', 'requirements-editor.txt', 'requirements-dev.txt'])
        for path in sorted(paths):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.pyc', '.backup', '.autosave'}:
                continue
            name = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            z.writestr(name, data)
            source_hashes[name] = hashlib.sha256(data).hexdigest()
    (evidence / 'after_implementation.json').write_text(json.dumps(source_hashes, indent=2))
    result = {
        'version': '0.9.0', 'original_sources': original,
        'circuit_valid_without_errors_or_warnings': True,
        'build_matches_source_and_custom_inputs': True,
        'deployed_hashes_match': True, 'deployed_archives': archives,
        'selectable_custom_chronicles': chronicles,
        'retired_demo_files': len(cleanup['removed']),
        'package_sha256': digest(package), 'class_versions': report['class_versions'],
        'full_suite': full, 'focused_suite': focused,
        'gui_probe': gui, 'portable_probe': portable,
        'source_snapshot': str(archive.relative_to(ROOT)),
        'source_snapshot_sha256': digest(archive),
        'source_file_count': len(source_hashes),
        'native_engine_test': False, 'game_launched': False,
        'clean_machine_test': False, 'full_gui_adventure_acceptance': False,
        'phase9_native_acceptance': 'DEFERRED_BY_USER',
    }
    (evidence / 'final_integrity.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf8')
    print(json.dumps({key: result[key] for key in ['version', 'original_sources', 'deployed_hashes_match', 'selectable_custom_chronicles', 'retired_demo_files', 'source_file_count', 'phase9_native_acceptance']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh-portable', action='store_true')
    args = parser.parse_args()
    if args.refresh_portable:
        refresh_portable()
    else:
        finalize()
