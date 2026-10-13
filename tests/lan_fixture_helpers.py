"""Pure resource helpers for LAN regression fixtures; no filesystem writes."""
from pathlib import Path
import re
import struct
from rcm.formats import NotFile


def promote(payload):
    """Rename libraries, retaining template IDs/bytes and all other resources."""
    result = dict(payload)
    renames = {}
    for name in payload:
        path = Path(name)
        if path.suffix.lower() != '.not' or path.name.startswith('_'):
            continue
        if not path.name.startswith('R_') or path.parent.as_posix().lower() != 'misc/templates':
            raise ValueError('Unexpected library: ' + name)
        new = path.with_name('_' + path.name).as_posix()
        if new in payload:
            raise ValueError('Library collision: ' + new)
        NotFile.read(payload[name])
        result[new] = result.pop(name)
        renames[name] = new
    for name, data in payload.items():
        if name.lower().endswith('.nmf'):
            for old, new in renames.items():
                pattern = rb'(?im)^(NOT[ \t]+)' + re.escape(Path(old).name.encode('ascii')) + rb'(?=[ \t\r\n]|$)'
                data = re.sub(pattern, lambda m: m[1] + Path(new).name.encode('ascii'), data)
            result[name] = data
    for old in renames:
        for name, data in result.items():
            if name.lower().endswith(('.nmf', '.nsd')) and Path(old).name.encode('ascii') in data.replace(Path(renames[old]).name.encode('ascii'), b''):
                raise ValueError('Old library reference remains: ' + name)
    return result, renames


def saved_templates(data):
    # Native base-thing loader: marker 0x1e, uint32 instance, template[32].
    references = []
    for match in re.finditer(re.escape(struct.pack('<I', 0x1e)), data):
        offset = match.start() + 8
        field = data[offset:offset + 32]
        if len(field) != 32 or b'\0' not in field:
            continue
        name = field.split(b'\0', 1)[0]
        if re.fullmatch(rb'[A-Za-z_][A-Za-z0-9_]*', name):
            references.append(dict(offset=offset, template=name.decode('ascii')))
    return references


def startup_templates(payload):
    return {t.name.casefold() for name, data in payload.items()
            if name.lower().endswith('.not') and Path(name).name.startswith('_')
            for t in NotFile.read(data).templates}


