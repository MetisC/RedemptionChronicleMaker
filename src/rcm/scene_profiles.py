"""Scene environment presets, read from copied originals, independent of geometry.

The version-8 reader in Vampire.exe (0x4a81c7..0x4a82e5) reads the
176-byte fixed tail after variable scene arrays. Unknown settings stay opaque.
"""
import hashlib
from pathlib import Path

from .formats import cstring


def reference(level, hints, selected=None):
    names = level.get('scenes', [])
    if selected is not None:
        matches = [s for s in names if s.casefold() == selected.casefold()]
        if len(matches) != 1 or matches[0].casefold() not in hints:
            raise ValueError('Entorno: escena original ausente o no asociada al level')
        return matches[0], hints[matches[0].casefold()]
    for name in names:
        hint = hints.get(name.casefold())
        if hint and hint.get('entities'):
            return name, hint
    raise ValueError('Entorno: el level no ofrece una escena original estudiada')


def read_profile(ws, name, hint):
    source = hint['source']
    if source.get('imported_pack'):
        from .wtd import read_entry
        data=read_entry(ws,source)
    else:data = ws.output(Path('research/original') / source['archive'] / source['path']).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if source.get('sha256') != digest:
        raise ValueError('Entorno: la copia original NSD difiere del catálogo; vuelve a escanear')
    if len(data) < 276 or data[:8] != b'NSD\x10\x08\0\0\0':
        raise ValueError('Entorno: se requiere NSD versión 8 con bloque completo')
    tail = data[-176:]
    record = {'id': name, 'source': dict(source), 'source_sha256': digest,
              'environment_sha256': hashlib.sha256(tail).hexdigest(),
              'sky_model': cstring(tail[-64:-32]), 'sky_animation': cstring(tail[-32:]),
              'unknown_bytes_preserved': True}
    return record, tail


def environment(ws, level, hints, selected=None):
    name, hint = reference(level, hints, selected)
    record, tail = read_profile(ws, name, hint)
    return bytes(16) + tail, record


def catalogue(ws, levels, hints):
    """Derive available presets; a bad copy remains visible as an unavailable row."""
    result = {}
    for lid, level in levels.items():
        rows = []
        for name in level.get('scenes', []):
            try:
                _, hint = reference(level, hints, name)
                record, _ = read_profile(ws, name, hint)
                rows.append(record)
            except (ValueError, OSError, KeyError) as error:
                rows.append({'id': name, 'error': str(error)})
        result[lid] = rows
    return result
