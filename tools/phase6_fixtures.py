"""Reproducible authored projects; generated output is never hand-edited."""
from pathlib import Path
import copy,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.service import Backend,source_text
from rcm.paths import Workspace
from rcm.document import Document


def system_source(ws):
    root=Document.load(ws,'tests/fixtures/chronicles/phase5_demo/project.yaml').snapshot()
    root['chronicle']={'id':'rcm_system','name':'RCM System Test','description':'NPC, decisiones, flags, quests, objetos, cámaras y cambio de mapa'}
    root['metadata']={'author':'Redemption Chronicle Maker','version':'0.6.0','requires_game':'Redemption 1.1','description':'Fixture oficial de regresión; checklist en docs/RUNTIME_TEST_MATRIX.md','dependencies':[]}
    root['resources']['templates'][0].update(id='T_rcm6_victoria',properties={'ai':'AI_rcm6','script':'RCM6Actor'})
    root['resources']['ai_profiles'][0]['id']='AI_rcm6'
    root['resources']['scripts']=[{'id':'RCM6Actor','source':'tests/fixtures/chronicles/system_test/resources/RCM6Actor.java'}]
    ws.write(root['resources']['scripts'][0]['source'],'public class RCM6Actor extends Codex { public RCM6Actor() { CodexConsole.Print(0,0,"RCM6 custom actor constructed"); } }\n')
    root['scenes'][0]['actors'][0]['template']='T_rcm6_victoria'
    for scene in root['scenes']:
        for actor in scene['actors']:
            if actor['id'] in {'witness','keeper'}:
                ident=actor['id'];actor['name']='Prueba: '+actor['id'];actor['conversation']={'default':ident}
                scene['conversations'].append({'id':ident,'speaker':actor['id'],'entry':'start','nodes':[{'id':'start','lines':[{'speaker':actor['id'],'text':'Prueba independiente de interacción. Puedes salir y hablar otra vez.'}],'choices':[{'text':'Volver al juego.','result':1},{'text':'Repetir después.','result':2}]}]})
    root['playtests']=[{'id':'native','name':'Prueba nativa completa','instructions':'Seguir docs/RUNTIME_TEST_MATRIX.md. No marcar PASS sin resultado observado en Redemption.'}]
    return root


def large_source(backend):
    levels=[n for n in backend.levels if backend.level_usable(n)]
    selected=[n for n in ['EastLondon','WestLondon'] if n in levels]+[n for n in sorted(levels) if n not in {'EastLondon','WestLondon'}][:3]
    root={'schema':2,'chronicle':{'id':'rcm_large','name':'RCM Large Fixture'},'state':{'flags':{'f'+str(i):i+1 for i in range(20)}},'entry':'map0','scenes':[],'quests':[{'id':'q'+str(i),'title':'Quest '+str(i),'description':'Stress test','steps':['Objetivo'],'reward_xp':10} for i in range(20)]}
    for si,level in enumerate(selected):
        scene={'id':'map'+str(si),'level':{'source':level},'actors':[],'objects':[],'conversations':[],'events':[],'triggers':[],'encounters':[],'sequences':[]}
        for i in range(20):
            a={'id':'actor'+str(i),'name':'Actor '+str(i),'template':'businessWoman','transform':{'position':[i*100-500,si*80,0],'orientation':[0,0,i*10]},'behavior':'enemy' if i>=17 else 'npc'}
            if i<10:
                a['conversation']={'default':'conv'+str(i)}
                scene['conversations'].append({'id':'conv'+str(i),'speaker':a['id'],'prompt':'Diálogo sintético '+str(i),'choices':[{'text':'Aceptar','result':1,'set_flag':'f'+str(i)},{'text':'Rechazar','result':2}]})
            scene['actors'].append(a)
        for i in range(6):scene['objects'].append({'id':'item'+str(i),'name':'Objeto '+str(i),'template':'ledger','transform':{'position':[i*80,160,0],'orientation':[0,0,0]},'quest_item':True})
        for i in range(10):scene['triggers'].append({'id':'area'+str(i),'name':'Trigger '+str(i),'shape':'sphere','transform':{'position':[i*200,0,0],'orientation':[0,0,0]},'radius':64,'once':False})
        scene['encounters']=[{'id':'guards','name':'Encuentro','actors':['actor17','actor18','actor19']}]
        scene['sequences']=[{'id':'shot','name':'Plano','actor':'actor0','duration':1.5,'shot':'wide','angle':'high'}]
        scene['events'].append({'id':'start','when':'scene_start','actions':[{'spawn':a['id']} for a in scene['actors'][:17]]+[{'spawn':o['id']} for o in scene['objects']]+[{'spawn_encounter':'guards'},{'start_quest':'q'+str(si*4)}]})
        for i in range(10):scene['events'].append({'id':'enter'+str(i),'when':'trigger_enter','trigger':'area'+str(i),'once':False,'actions':[{'set_flag':'f'+str(i)}]})
        for i in range(9):scene['events'].append({'id':'timer'+str(i),'when':'timer','seconds':i+1.0,'once':False,'conditions':[{'flag':'f'+str(i),'is_set':True}],'actions':[{'clear_flag':'f'+str(i)}]})
        root['scenes'].append(scene)
    return root


def create():
    ws=Workspace(ROOT);backend=Backend(ws);system=system_source(ws);golden=copy.deepcopy(system);golden['chronicle'].update(id='rcm_golden',name='RCM Golden Project');golden['resources']['templates'][0]['id']='T_rcm6_golden';golden['scenes'][0]['actors'][0]['template']='T_rcm6_golden'
    for folder,root in [('system_test',system),('golden',golden),('large_fixture',large_source(backend))]:
        result=backend.validate(root)
        if not result.valid:raise ValueError(folder+': '+'; '.join(p.message for p in result.problems if p.severity=='ERROR'))
        ws.write('chronicles/'+folder+'/project.yaml',source_text(root))
    # A generator run must not silently reset an independently accepted baseline.
    if not ws.output('tests/fixtures/chronicles/golden/expected.json').exists():raise ValueError('Falta baseline Golden: recuperar expected.json del proyecto antes de generar fixtures')
    print('SystemTest, Golden y fixture grande validados y guardados')


if __name__=='__main__':create()
