"""Recover settings/cache safely and prepare a first-run workspace."""
from pathlib import Path
import json
import sys
import time
from .generator import ECJ_SHA256
import hashlib


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
        for folder,dest in [('docs','docs'),('examples','chronicles')]:
            if not ws.output(dest).exists():
                for path in (base/folder).rglob('*'):
                    if path.is_file():ws.write(Path(dest)/path.relative_to(base/folder),path.read_bytes())
    compiler=ws.output('cache/toolchain/ecj-3.26.0.jar')
    if not compiler.is_file() and (bundle/'toolchain/ecj-3.26.0.jar').is_file():ws.write(compiler,(bundle/'toolchain/ecj-3.26.0.jar').read_bytes())
    if not compiler.is_file() or hashlib.sha256(compiler.read_bytes()).hexdigest()!=ECJ_SHA256:raise ValueError('Falta el compilador ECJ verificado. Revisa la distribución o tools/bootstrap.ps1')
    errors=cache_errors(ws)
    if errors:
        if not ws.game:raise ValueError('Selecciona la instalación original para crear los catálogos')
        for name in ['levels','resources','scene_hints']:
            path=ws.output('cache/'+name+'.json')
            if path.is_file():ws.write('research/startup/'+str(time.time_ns())+'_'+name+'.json',path.read_bytes())
        progress('Leyendo instalación original; creando catálogos…')
        from .catalogue import discover
        discover(ws,ws.game,False)
    if not ws.output('cache/toolchain/classes.zip').is_file():
        if not ws.game:raise ValueError('Falta classes.zip; selecciona la instalación original')
        ws.write('cache/toolchain/classes.zip',(ws.game/'classes.zip').read_bytes())
    if cache_errors(ws):raise ValueError('No se pudieron reconstruir los catálogos')
    return {'cache_rebuilt':bool(errors),'original_tools_used':False}
