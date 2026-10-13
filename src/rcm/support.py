"""Local opt-in support archive; never includes original assets or private projects."""
from pathlib import Path
import json
import platform
import re
import time
import zipfile


def support_bundle(ws,destination,include_project=None):
    from . import __version__
    def sanitize(text):
        for path,label in [(str(ws.root),'<workspace>'),(str(ws.game) if ws.game else '', '<game>'),(str(Path.home()),'<user>')]:
            if path:text=text.replace(path,label).replace(path.replace('\\','/'),label)
        return re.sub(r'[A-Za-z]:[\\/][^\r\n\"<>]*', '<path>',text)
    prefs=getattr(ws,'app_settings',None)
    settings={key:value for key,value in prefs.data.items() if key in ('schema','language','appearance','safe_mode','autosave_seconds')} if prefs else {}
    data={'summary.json':json.dumps(dict(rcm=__version__,platform=platform.platform(),created=time.time(),settings=settings,telemetry=False),indent=2)}
    for name in ['build/diagnostics/report.json','build/editor/last_error.log','build/editor/build_error.log','cache/last_playtest.json']:
        p=ws.output(name)
        if p.is_file():data[name]=sanitize(p.read_text(encoding='utf8',errors='replace')[-256000:])
    try:
        session=json.loads(ws.output('cache/last_playtest.json').read_text(encoding='utf8'))
        from .debugging import trace_file,trace_tail
        trace=trace_file(ws,session['chronicle'])
        if trace:data['runtime_trace.log']=sanitize(trace_tail(trace))
        report=ws.output('build/'+session['chronicle']+'/build_report.json')
        if report.is_file():data['build_report.json']=sanitize(report.read_text(encoding='utf8'))
    except (OSError,ValueError,KeyError):pass
    if include_project:data['project.yaml']=ws.output(include_project).read_text(encoding='utf8')
    target=ws.output(destination);target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,text in data.items():archive.writestr(name,text)
    return target
