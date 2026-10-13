"""Recover settings/cache safely and prepare a first-run workspace."""
from pathlib import Path
import json
import sys
import time
from .generator import ECJ_SHA256
import hashlib


def cached_identity(ws):
    try:
        value=json.loads(ws.output('cache/installation_identity.json').read_text(encoding='utf8'))
        from .catalogue import identity_from_records
        records=value['files']
        if value.get('format')!=1 or not isinstance(records,list) or not records:raise ValueError('Invalid identity')
        core=[r for r in records if r['sha256'] is not None]
        loose=[dict(path=r['file'],size=r['size'],extension=Path(r['file']).suffix,archive=None) for r in records if r['sha256'] is None]
        rebuilt=identity_from_records(core,loose)
        return rebuilt if rebuilt==value else None
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None


def legacy_identity(ws):
    """Adopt an intact RC2 catalogue without treating a new path as new content."""
    try:
        from .catalogue import identity_from_records
        records=json.loads(ws.output('research/source_manifest.json').read_text(encoding='utf8'))
        entries=json.loads(ws.output('cache/resources.json').read_text(encoding='utf8'))['entries']
        return identity_from_records(records,entries)
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None


def invalidate_installation_cache(ws):
    # These paths contain derived data only. Compiler, user projects, custom
    # resources and backups are deliberately outside this bounded list.
    paths=[ws.output('cache/'+name+'.json') for name in ('levels','geometry','resources','chronicles','scene_hints','scene_profiles','motions','installation_identity')]
    paths += [ws.output(p) for p in ws.output('cache/levels').glob('*.json')]
    from .catalogue import RESEARCH_EXTENSIONS
    extracted=RESEARCH_EXTENSIONS- {'.txt','.bat','.dsp'}
    extracted |= {'.nsc','.nmf','.nss','.nui'}
    paths += [ws.output(p) for p in ws.output('research/original').rglob('*') if p.is_file() and p.suffix.lower() in extracted]
    # Meshes/textures use content hashes in their filenames. They remain valid
    # only for those bytes, and can coexist safely with a different installation.
    # Never remove whole directories that may contain an authored Java/image file.
    for path in paths:ws.output(path)
    for path in paths:
        if path.exists():ws.output(path).unlink()


def settings(ws):
    path=ws.output('cache/game_settings.json')
    if not path.exists():return {}
    try:
        data=json.loads(path.read_text(encoding='utf8'))
        if not isinstance(data,dict) or not isinstance(data.get('installation'),str):raise ValueError('Settings inválidos')
        return data
    except (ValueError,OSError):
        if path.is_file():ws.write('research/startup/settings_'+str(time.time_ns())+'.json',path.read_bytes())
        return {}


def cache_errors(ws):
    errors=[]
    for name in ['levels','resources','scene_hints']:
        try:
            data=json.loads(ws.output('cache/'+name+'.json').read_text(encoding='utf8'))
            if not isinstance(data,dict) or not data:raise ValueError('Índice vacío/inválido')
            if name=='resources' and (not isinstance(data.get('entries'),list) or not isinstance(data.get('templates'),list)):raise ValueError('Tablas ausentes')
            if name=='resources':
                if any(not isinstance(e,dict) or any(not isinstance(e.get(k),str) for k in ['id','path','extension']) or ('archive' not in e or (e['archive'] is not None and not isinstance(e['archive'],str))) for e in data['entries']):raise ValueError('Registro de recurso inválido')
                if any(not isinstance(e,dict) or not isinstance(e.get('id'),str) for e in data['templates']):raise ValueError('Registro de template inválido')
            if name=='scene_hints' and any(not isinstance(v,dict) or not isinstance(v.get('entities'),list) for v in data.values()):raise ValueError('Anchor inválido')
            if name=='levels' and any(not isinstance(v,dict) or not isinstance(v.get('geometry'),list) or not isinstance(v.get('references'),list) for v in data.values()):raise ValueError('Level inválido')
        except (OSError,ValueError) as error:errors.append(name+': '+str(error))
    return errors

def reset_settings(ws):
    path=ws.output('cache/game_settings.json')
    if path.is_file():
        ws.write('research/startup/reset_settings_'+str(time.time_ns())+'.json',path.read_bytes())
        path.unlink()
    return True


def prepare_workspace(ws,progress=lambda _:None):
    bundle=Path(getattr(sys,'_MEIPASS',ws.root))
    if getattr(sys,'frozen',False):
        base=Path(sys.executable).parent
        for folder,dest in [('docs','docs')]:
            if not ws.output(dest).exists():
                for path in (base/folder).rglob('*'):
                    if path.is_file():ws.write(Path(dest)/path.relative_to(base/folder),path.read_bytes())
    compiler=ws.output('cache/toolchain/ecj-3.26.0.jar')
    if not compiler.is_file() and (bundle/'toolchain/ecj-3.26.0.jar').is_file():ws.write(compiler,(bundle/'toolchain/ecj-3.26.0.jar').read_bytes())
    if not compiler.is_file() and not getattr(sys,'frozen',False):
        source=Path(__file__).resolve().parents[2]/'cache/toolchain/ecj-3.26.0.jar'
        if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()==ECJ_SHA256:ws.write(compiler,source.read_bytes())
    if not compiler.is_file() or hashlib.sha256(compiler.read_bytes()).hexdigest()!=ECJ_SHA256:raise ValueError('Falta el compilador ECJ verificado. Revisa la distribución o tools/bootstrap.ps1')
    errors=cache_errors(ws)
    current=None;changed=False;previous=None
    identity_path=ws.output('cache/installation_identity.json')
    if ws.game:
        progress('Comprobando los recursos de Redemption…')
        from .catalogue import installation_identity
        current=installation_identity(ws.game)
        previous=cached_identity(ws) if identity_path.exists() else legacy_identity(ws)
        changed=previous!=current
    if errors or changed:
        if not ws.game:raise ValueError('Selecciona la instalación original para crear los catálogos')
        for name in ['levels','resources','scene_hints']:
            path=ws.output('cache/'+name+'.json')
            if path.is_file():ws.write('research/startup/'+str(time.time_ns())+'_'+name+'.json',path.read_bytes())
        if changed:
            if previous or identity_path.exists():progress('La instalación de Redemption ha cambiado. RCM actualizará sus catálogos.')
            invalidate_installation_cache(ws)
        progress('Leyendo escenarios y recursos de Redemption…')
        from .catalogue import discover
        discover(ws,ws.game,False,progress=progress,refresh_installation=True)
        if current is not None and cached_identity(ws)!=current:raise ValueError('La instalación cambió mientras se preparaban los catálogos. Vuelve a abrir RCM.')
    elif current is not None and not identity_path.exists():
        ws.write(identity_path,json.dumps(current,indent=2))
    classes=ws.output('cache/toolchain/classes.zip')
    source_classes=next((r['sha256'] for r in current['files'] if r['file']=='classes.zip'),None) if current else None
    if not classes.is_file() or (source_classes and hashlib.sha256(classes.read_bytes()).hexdigest()!=source_classes):
        if not ws.game:raise ValueError('Falta classes.zip; selecciona la instalación original')
        ws.write('cache/toolchain/classes.zip',(ws.game/'classes.zip').read_bytes())
    progress('Preparando el compilador…')
    if getattr(sys,'frozen',False):
        from .product import copy_example
        progress('Preparando tus copias de los ejemplos…')
        for name in ('tutorial','showcase','mini_chronicle'):
            if (base/'examples'/name/'project.yaml').is_file():copy_example(ws,name)
    if cache_errors(ws):raise ValueError('No se pudieron reconstruir los catálogos')
    return {'cache_rebuilt':bool(errors or changed),'installation_changed':changed,'original_tools_used':False}
