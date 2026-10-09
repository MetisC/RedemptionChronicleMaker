"""Swap generated application files while leaving the user's workspace in place.

Build in a separate directory first. Every old application component is retained
in a recoverable backup, and a failed swap rolls back. Never touches Redemption.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def managed(path):
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Update outside workspace')
    for part in [path, *path.parents]:
        if part == ROOT:
            break
        if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
            raise ValueError('Update through link')
        if part.is_file() and part.stat().st_nlink != 1:
            raise ValueError('Update through hardlink')
    return path


def inventory(path):
    result = {}
    if path.exists():
        for file in path.rglob('*'):
            managed(file)
            if file.is_file():
                result[file.relative_to(path).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def update(source):
    running = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RedemptionChronicleMaker.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True, check=True)
    if 'redemptionchroniclemaker.exe' in running.stdout.casefold():
        raise ValueError('Cierra el editor antes de actualizarlo; la revisión nueva sigue preparada aparte')
    app = managed(ROOT / 'build/portable/RedemptionChronicleMaker')
    source = managed(ROOT / source / 'RedemptionChronicleMaker')
    if not (source / 'RedemptionChronicleMaker.exe').is_file() or source == app:
        raise ValueError('Missing separate portable build')
    components = sorted(p.name for p in source.iterdir() if p.name not in {'workspace', 'portable_console.log'})
    for name in components:
        for entry in [source / name, app / name]:
            managed(entry)
            if entry.is_dir():
                for child in entry.rglob('*'):
                    managed(child)
    workspace = managed(app / 'workspace')
    before = inventory(workspace)
    backup = managed(ROOT / 'build/portable_backups' / ('before_0.9.1_' + str(time.time_ns())))
    backup.mkdir(parents=True)
    old = []
    new = []
    try:
        for name in components:
            target = app / name
            if target.exists():
                os.replace(target, backup / name)
                old.append(name)
            os.replace(source / name, target)
            new.append(name)
        if inventory(workspace) != before:
            raise ValueError('User workspace changed during update')
    except Exception:
        for name in reversed(new):
            os.replace(app / name, source / name)
        for name in reversed(old):
            os.replace(backup / name, app / name)
        raise
    result = dict(executable=str(app / 'RedemptionChronicleMaker.exe'), backup=str(backup), workspace_preserved=True, user_files_checked=len(before), components=components, native_engine_test=False)
    report = ROOT / 'research/phase9/editor_fixes/portable_update.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs='?', default='build/portable_update_091')
    update(Path(parser.parse_args().source))
