"""Local diagnostics: never sends telemetry or reads unrelated user data."""
import importlib.metadata
import json
import platform
import shutil


def diagnostic_report(ws):
    from . import __version__
    result={'rcm':__version__,'python':platform.python_version(),'platform':platform.platform(),'workspace':str(ws.root),'game':str(ws.game) if ws.game else None,'native_engine_test':False,'catalogues':{},'dependencies':{}}
    for name in ['levels','resources','scene_hints']:
        try:
            data=json.loads(ws.output('cache/'+name+'.json').read_text(encoding='utf8'))
            if not isinstance(data,dict):raise ValueError('El índice debe ser un objeto')
            result['catalogues'][name]={'valid_json':True,'records':len(data)}
        except (OSError,ValueError) as error:result['catalogues'][name]={'error':str(error)}
    for name in ['PySide6','PyYAML','numpy','Pillow']:
        try:result['dependencies'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:result['dependencies'][name]='missing'
    result['java']=shutil.which('java');result['compiler_present']=ws.output('cache/toolchain/ecj-3.26.0.jar').is_file();result['bootclasspath_present']=ws.output('cache/toolchain/classes.zip').is_file()
    path=ws.write('build/diagnostics/report.json',json.dumps(result,ensure_ascii=False,indent=2));result['report']=str(path);return result
