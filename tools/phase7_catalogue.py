"""Refresh derived scene associations without rereading or touching the game."""
from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.catalogue import associate_static_scenes
from rcm.scene_profiles import catalogue
ws=Workspace(ROOT)
levels=json.loads(ws.output('cache/levels.json').read_text(encoding='utf8'))
hints=json.loads(ws.output('cache/scene_hints.json').read_text(encoding='utf8'))
before=ws.output('cache/levels.json').read_bytes()
ws.write('research/phase7/levels_before.json',before)
associate_static_scenes(levels,hints)
ws.write('cache/levels.json',json.dumps(levels,ensure_ascii=False,indent=2))
profiles=catalogue(ws,levels,hints)
ws.write('cache/scene_profiles.json',json.dumps(profiles,ensure_ascii=False,indent=2))
text=ws.output('research/ALL_CODEX.bytecode.txt').read_text(encoding='utf8')
pattern=r'(?m)^\s*\d+: ldc(?:_w)?\s+#\d+\s+// String (\S+)\s*\n\s*\d+: ldc(?:_w)?\s+#\d+\s+// String (\S+)\s*\n\s*\d+: invokestatic\s+#\d+\s+// Method CodexSequence.ChangeScene:'
links=[{'location':loc,'scene':name,'line':text.count('\n',0,m.start())+1,'source':'research/ALL_CODEX.bytecode.txt','association':'literal arguments to ChangeScene; not an NSS index'} for m in re.finditer(pattern,text) for loc,name in [m.groups()]]
ws.write('research/phase7/codex_scene_links.json',json.dumps(links,indent=2))
report={'levels':len(levels),'profiles':sum(len(v) for v in profiles.values()),'unavailable':sum('error' in r for v in profiles.values() for r in v),'static_scenes':sum('static_scene' in l for l in levels.values()),'codex_literal_links':len(links),'codex_links_imported_as_presets':False,'native_engine_test':False}
ws.write('research/phase7/catalogue_report.json',json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
