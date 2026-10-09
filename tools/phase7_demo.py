"""Build a reviewable three-scene regression chronicle from authored data."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.document import Document
from rcm.service import Backend,source_text
from rcm.packages import create_package
ws=Workspace(ROOT);backend=Backend(ws)
source=Document.load(ws,'tests/fixtures/chronicles/system_test/project.yaml').snapshot()
source['chronicle']={'id':'rcm_stable','name':'Londres: prueba de estabilización','description':'Tres escenas, dos levels originales; diálogos, quests, inventario, cámara y regreso con estado compartido.'}
source['metadata']['version']='0.7.0'
source['metadata']['description']='Fase 7. Seguir docs/PHASE7_PLAYTEST.md. Pruebas offline no equivalen a aceptación nativa.'
source['resources']['templates'][0].update(id='T_rcm7_victoria',properties={'ai':'AI_rcm7','script':'RCM7Actor'})
source['resources']['ai_profiles'][0]['id']='AI_rcm7'
java='tests/fixtures/chronicles/phase7_demo/resources/RCM7Actor.java'
ws.write(java,'public class RCM7Actor extends Codex { public RCM7Actor() { CodexConsole.Print(0,0,"RCM7 custom actor constructed"); } }\n')
source['resources']['scripts']=[{'id':'RCM7Actor','source':java}]
source['scenes'][0]['actors'][0]['template']='T_rcm7_victoria'
for scene in source['scenes']:
    lid=scene['level']['source'];scene['level']['environment_scene']=backend.levels[lid]['scenes'][0]
    for event in scene['events']:
        for action in event['actions']:
            if scene['id']=='west' and action.get('jump')=='london':action['jump']='east_return'
actor={'id':'witness','name':'Testigo del regreso','template':'businessWoman','transform':{'placement':'near_player','orientation':[0,0,180]},'conversation':{'default':'back','when_flag':'alliance','then':'ally'}}
convs=[]
for cid,prompt in [('back','Has vuelto al este de Londres. La escena conserva tus decisiones. Puedes regresar al inicio para comprobarlas.'),('ally','Nuestro pacto sigue vigente después del viaje. Esta escena comparte el mismo EastLondon y tiene su propio testigo.')]:
    convs.append({'id':cid,'speaker':'witness','prompt':prompt,'choices':[{'text':'Regresar al inicio.','result':1},{'text':'Quedarme aquí.','result':2}]})
source['scenes'].append({'id':'east_return','level':{'source':'EastLondon','name':'Londres: el regreso','environment_scene':'EAST_28_1.nsd'},'actors':[actor],'objects':[],'conversations':convs,'events':[
    {'id':'entry','when':'scene_start','actions':[{'spawn':'witness'}]},
    *[{'id':'back'+str(i),'when':'conversation_ended','conversation':c['id'],'result':1,'once':False,'actions':[{'jump':'london'}]} for i,c in enumerate(convs)]], 'triggers':[], 'encounters':[], 'sequences':[]})
source['playtests']=[{'id':'phase7','name':'Recorrido de estabilización','instructions':'docs/PHASE7_PLAYTEST.md. Partida nueva; anotar observaciones reales.'}]
ws.write('tests/fixtures/chronicles/phase7_demo/project.yaml',source_text(source))
report=backend.build(copy.deepcopy(source))
package='build/rcm_stable/rcm_stable.rcmpack'
manifest=create_package(ws,'rcm_stable',package)
result={'source':'tests/fixtures/chronicles/phase7_demo/project.yaml','scenes':report['scenes'],'class_versions':report['class_versions'],'environment_profiles':report['environment_profiles'],'geometry_in_package':report['geometry_in_package'],'package':package,'requires_rcm':manifest['requires_rcm'],'native_engine_test':False}
ws.write('research/phase7/demo_build.json',json.dumps(result,indent=2));print(json.dumps({'report':'research/phase7/demo_build.json','scenes':result['scenes'],'package':package,'native_engine_test':False},indent=2))
