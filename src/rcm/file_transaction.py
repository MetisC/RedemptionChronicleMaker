"""Preflight, backup and roll back a bounded set of owned files.

Individual replacements are atomic. A transaction is not isolated from readers;
the calling build/install must publish its validity manifest last.
"""
import hashlib
import os
import zipfile
from pathlib import Path
from typing import Callable


def replace_files(targets: dict[Path, bytes], obsolete: list[Path], backup: Path, relative_root: Path, validate: Callable[[Path], Path]) -> Path:
    paths = [*targets, *obsolete]
    if len(set(paths)) != len(paths):
        raise ValueError('Destino repetido en transacción')
    temps = {}
    for path in paths:
        validate(path)
        if path.exists() and not path.is_file():
            raise ValueError('El destino no es un archivo: ' + str(path))
    for path in targets:
        temp = validate(path.with_name(path.name + '.rcm-tmp'))
        if temp.exists():
            raise ValueError('Temporal existente: ' + str(temp))
        temps[path] = temp
    backup.parent.mkdir(parents=True, exist_ok=True)
    prior = {}
    with zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            prior[path] = path.exists()
            if prior[path]:
                archive.writestr(path.relative_to(relative_root).as_posix(), path.read_bytes())
    changed = []
    try:
        for path, data in targets.items():
            validate(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            temps[path].write_bytes(data)
            os.replace(temps[path], path)
            changed.append(path)
            if hashlib.sha256(path.read_bytes()).digest() != hashlib.sha256(data).digest():
                raise OSError('Hash incorrecto al publicar ' + str(path))
        for path in obsolete:
            if path.exists():
                validate(path).unlink()
                changed.append(path)
    except OSError as error:
        failures = []
        with zipfile.ZipFile(backup) as archive:
            for path in reversed(changed):
                try:
                    validate(path)
                    if prior[path]:
                        path.write_bytes(archive.read(path.relative_to(relative_root).as_posix()))
                    elif path.exists():
                        path.unlink()
                except OSError as recovery_error:
                    failures.append(str(recovery_error))
        if failures:
            raise OSError(f'{error}; recuperación incompleta. Backup: {backup}; ' + '; '.join(failures)) from error
        raise
    finally:
        for temp in temps.values():
            if temp.is_file():
                validate(temp).unlink()
    return backup
