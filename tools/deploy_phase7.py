"""Authorized RCM-only deployment, backups and original-file integrity checks."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.deployment import default_game,game_running,deploy
from rcm.catalogue import verify_sources
from rcm.shortcut import launch_info
from rcm.document import Document
ws=Workspace(ROOT,default_game(ROOT))
if game_running():raise ValueError('Vampire está abierto: no se reemplazan recursos cargados')
before=verify_sources(ws,ws.game)
source=Document.load(ws,'tests/fixtures/chronicles/phase7_demo/project.yaml').snapshot()
shortcut=launch_info(ws)
if not shortcut:raise ValueError('No se encontró el acceso exacto del usuario; no se inventa un lanzamiento')
result=deploy(ws,'rcm_stable',directory=shortcut['relative'],current_source=source)
after=verify_sources(ws,ws.game)
record={'deployment':result,'originals_before':before,'originals_after':after,'shortcut':str(shortcut['shortcut']),'chronicle_name':source['chronicle']['name'],'game_launched':False,'native_engine_test':False}
ws.write('research/phase7/deployment.json',json.dumps(record,indent=2));print(json.dumps(record,indent=2))
