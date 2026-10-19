"""Product lifecycle helpers layered over the existing authoring backend."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import unicodedata
import re


def project_id(name, workspace):
    stem = unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode().lower()
    stem = re.sub('[^a-z0-9_]+', '_', stem).strip('_') or 'chronicle'
    if not stem[0].isalpha():stem = 'c_' + stem
    stem = stem[:14]
    candidate = stem; number = 2
    while (Path(workspace) / 'chronicles' / candidate).exists():
        suffix = str(number); candidate = stem[:14-len(suffix)] + suffix; number += 1
    return candidate


def validate_workspace(path, game=None, program=None):
    from .paths import Workspace
    ws = Workspace(Path(path), Path(game) if game else None)
    if program and (ws.root.is_relative_to(Path(program).resolve()) or Path(program).resolve().is_relative_to(ws.root)):
        raise ValueError('Elige una carpeta de proyectos separada del programa.')
    ws.root.mkdir(parents=True, exist_ok=True)
    probe = ws.output('.write_probe_' + str(time.time_ns()))
    probe.write_bytes(b'RCM'); probe.unlink()
    return ws


def example_root():
    return Path(sys.executable).parent / 'examples' if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2] / 'chronicles'


def copy_example(ws, name, clean=False):
    """Bundled masters are never edited. Existing work is never overwritten."""
    source = example_root() / name
    if not (source / 'project.yaml').is_file():raise ValueError('Falta el ejemplo en la distribución: ' + name)
    target = ws.output('chronicles/' + name)
    if target.exists() and not clean:return target / 'project.yaml'
    if target.exists():
        i = 2
        while ws.output('chronicles/' + name + '_' + str(i)).exists():i += 1
        target = ws.output('chronicles/' + name + '_' + str(i))
    for path in source.rglob('*'):
        if path.is_symlink():raise ValueError('Enlace en ejemplo')
        if path.is_file() and path.suffix not in {'.autosave','.backup'}:
            ws.write(target / path.relative_to(source), path.read_bytes())
    from .input_limits import parse_source
    from .service import source_text
    project=target/'project.yaml';data=parse_source(project.read_text(encoding='utf8'))
    for kind in ('scripts','textures','maps'):
        for resource in data.get('resources',{}).get(kind,[]):
            original=Path(resource['source']);parts=list(original.parts)
            if len(parts)>=3 and parts[:2]==['chronicles',name]:
                resource['source']=(target/Path(*parts[2:])).relative_to(ws.root).as_posix()
    ws.write(project,source_text(data))
    ws.write(target / '.rcm_example.json', json.dumps(dict(format=1, example=name, master_sha256=hashlib.sha256((source/'project.yaml').read_bytes()).hexdigest())))
    return target / 'project.yaml'


def detect_games():
    """Bounded candidates from Windows registries; never scan whole drives."""
    candidates = []
    if os.name == 'nt':
        import winreg
        for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            for view in [winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY]:
                for keyname in [r'SOFTWARE\GOG.com\Games', r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall']:
                    try:
                        with winreg.OpenKey(hive,keyname,0,winreg.KEY_READ|view) as parent:
                            for index in range(winreg.QueryInfoKey(parent)[0]):
                                try:
                                    with winreg.OpenKey(parent,winreg.EnumKey(parent,index)) as child:
                                        values = {}
                                        for field in ('gameName','DisplayName','path','InstallLocation'):
                                            try:values[field] = winreg.QueryValueEx(child,field)[0]
                                            except OSError:pass
                                        if 'redemption' in str(values.get('gameName',values.get('DisplayName',''))).casefold():
                                            path = values.get('path',values.get('InstallLocation'))
                                            if isinstance(path,str):candidates.append(Path(path))
                                except OSError:pass
                    except OSError:pass
    from .deployment import installation
    result = []
    for path in candidates:
        try:path = installation(path)
        except (OSError, ValueError):continue
        if path not in result:result.append(path)
    return result


def verify_installation(game):
    import zipfile
    from .deployment import installation
    game=installation(game)
    if (game/'Vampire.exe').read_bytes()[:2]!=b'MZ':raise ValueError('Vampire.exe no es un ejecutable válido.')
    for name in ('Resource.nob','Codex.nob','classes.zip'):
        if not zipfile.is_zipfile(game/name):raise ValueError('Esta instalación está incompleta o dañada: '+name)
    if not (game/'Chronicles').is_dir():raise ValueError('Falta la carpeta Chronicles del juego.')
    return game


def ensure_runtime_root(game):
    from .deployment import safe_target
    root = safe_target(game, game/'RCM'); root.mkdir(exist_ok=True)
    marker = safe_target(game,root/'.rcm_root.json')
    if marker.exists():
        if json.loads(marker.read_text(encoding='utf8')).get('format') != 1:raise ValueError('Marcador RCM desconocido; se conserva.')
    else:
        # Never adopt ownership of existing contents just by marking the root.
        marker.write_text(json.dumps(dict(format=1,application='Redemption Chronicle Maker',existing_content_preserved=True)),encoding='utf8')
    probe = safe_target(game,root/('.write_probe_' + str(time.time_ns())))
    probe.write_bytes(b'RCM'); probe.unlink()
    return root
