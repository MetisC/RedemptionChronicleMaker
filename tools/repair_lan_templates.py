"""Repair startup visibility of our NOTs without changing a player or Java.

Default: stage and audit inside the workspace. --apply: backed-up, bounded
replacement of the installed RCM NOB and its ownership manifest only.
"""
import argparse
import hashlib
import io
import json
import re
import struct
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'cache/vendor')]
from rcm.deployment import game_running, installation, safe_target
from rcm.file_transaction import replace_files
from rcm.formats import NotFile
from rcm.generator import zip_bytes

GAME = Path(r'H:\GOG\Vampire The Masquerade - Redemption')
EVIDENCE = ROOT / 'research/runtime_test/lan_crash'


def digest(data):
    return hashlib.sha256(data).hexdigest()


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    game = installation(GAME)
    target = safe_target(game, game / 'RCM/east_demo/rcm_tutor.nob')
    manifest_path = safe_target(game, target.parent / '.rcm_deployment.json')
    original = target.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest['files'].get(target.name) != digest(original):
        raise ValueError('Installed NOB differs from ownership manifest')
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        payload = {n: archive.read(n) for n in archive.namelist()}
    repaired, renames = promote(payload)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    staged = EVIDENCE / 'rcm_tutor_startup_repair.nob'
    replacement = zip_bytes(repaired)
    staged.write_bytes(replacement)
    profile = game / 'Crypt/npf000000.npf'
    profile_data = profile.read_bytes()
    (EVIDENCE / 'npf000000_readonly_copy.npf').write_bytes(profile_data)
    references = saved_templates(profile_data)
    own_refs = [r for r in references if r['template'].casefold().startswith('r_')]
    unavailable_before = [r for r in own_refs if r['template'].casefold() not in startup_templates(payload)]
    unavailable_after = [r for r in own_refs if r['template'].casefold() not in startup_templates(repaired)]
    if unavailable_after:
        raise ValueError('Saved custom templates still unavailable: ' + str(unavailable_after))
    changed = [n for n in payload if n in repaired and payload[n] != repaired[n]]
    if any(not n.endswith('.nmf') for n in changed):
        raise ValueError('Unexpected resource modification')
    report = dict(target=str(target), original_sha256=digest(original), repaired_sha256=digest(replacement),
                  renames=renames, modified_resources=changed,
                  template_bytes_preserved=all(payload[a] == repaired[b] for a, b in renames.items()),
                  other_resource_bytes_preserved=all(data == repaired[name] for name, data in payload.items() if name not in renames and name not in changed),
                  saved_character=dict(path=str(profile), sha256=digest(profile_data), references=references,
                                       unavailable_before=unavailable_before, unavailable_after=unavailable_after),
                  java_replaced=False, applied=False, native_LAN_test='pending')
    if args.apply:
        if game_running():
            raise ValueError('Vampire must be closed before replacing loaded resources')
        if target.read_bytes() != original or manifest_path.read_bytes() != manifest_bytes:
            raise ValueError('Deployment changed during preflight')
        if renames:
            manifest['files'][target.name] = digest(replacement)
            backup = EVIDENCE / ('before_startup_repair_' + str(time.time_ns()) + '.zip')
            replace_files({target: replacement, manifest_path: json.dumps(manifest, indent=2).encode('utf8')},
                          [], backup, game / 'RCM', lambda p: safe_target(game, p))
            report['backup'] = str(backup)
        report['applied'] = True
        if profile.read_bytes() != profile_data:
            raise ValueError('Character changed unexpectedly during deployment')
    (EVIDENCE / 'startup_repair.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
