"""Canonical RC4 demonstrations using original Rat actors and existing UI flows."""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.camera_presets import DEFAULT_DIALOGUE_CAMERA
from rcm.service import Backend,source_text

def add_showcase_station(root):
    root=copy.deepcopy(root)
    if root.get('project_format')==10 and any(g['id']=='dyn_rats' for s in root['scenes'] for g in s.get('generators',[])):return root
    root['project_format']=10;s=root['scenes'][0]
    guide=next(c for c in s['conversations'] if c['id']=='guide')
    guide['choices'].append({'text':'Laboratorio opcional: encuentros dinámicos.','result':8})
    s['conversations'].append({'id':'dyn','speaker':'guide','camera':DEFAULT_DIALOGUE_CAMERA,'prompt':'Aquí puedes ver enemigos creados durante la partida. Primero salen dos ratas; al vencerlas aparece una rata con más vida. A la mitad llama un refuerzo. Esto es opcional y no cambia el encargo del libro.','choices':[{'text':'Probar el encuentro dinámico.','result':1},{'text':'Parar el generador continuo.','result':2},{'text':'Volver al taller.','result':3},{'text':'Probar el generador continuo (máximo dos ratas).','result':4}]})
    point='audio';group=lambda role,count,**opts:{'role':role,'template':'Rat','count':count,**opts}
    common={'spawn_points':[point],'persistence':'once'}
    s.setdefault('generators',[]).extend([
        dict(id='dyn_rats',name='Dos ratas del laboratorio',mode='ambush',max_alive=2,waves=[{'groups':[group('rats',2)]}],**common),
        dict(id='dyn_boss',name='Rata por fases',mode='boss',max_alive=1,waves=[{'groups':[group('boss',1,health_multiplier=10)]}],boss={'role':'boss'},phases=[{'id':'half','percent':50,'actions':[{'start_generator':'dyn_add'}]},{'id':'quarter','percent':25,'actions':[copy.deepcopy(next(a for e in s['events'] for a in e['actions'] if 'play_sound' in a))]}],**common),
        dict(id='dyn_add',name='Refuerzo de la rata',mode='reinforcements',max_alive=1,waves=[{'groups':[group('adds',1)]}],**common),
        dict(id='dyn_portal',name='Generador continuo del laboratorio',mode='continuous',max_alive=2,interval=5,waves=[{'groups':[group('rats',1)]}],**common)])
    root['quests'].append({'id':'dynamic_lab','title':'Laboratorio: encuentros dinámicos','description':'Una estación opcional del taller.','steps':['Vence a las dos ratas.','Observa los refuerzos y vence al jefe.'],'reward_xp':0})
    s['events'].extend([
        {'id':'dyn_menu','when':'conversation_ended','conversation':'guide','result':8,'once':False,'actions':[{'start_conversation':'dyn'}]},
        {'id':'dyn_begin','when':'conversation_ended','conversation':'dyn','result':1,'once':True,'actions':[{'start_quest':'dynamic_lab'},{'start_generator':'dyn_rats'}]},
        {'id':'dyn_next','when':'generator_complete','generator':'dyn_rats','once':True,'actions':[{'advance_quest':'dynamic_lab'},{'start_generator':'dyn_boss'}]},
        {'id':'dyn_end','when':'generator_complete','generator':'dyn_boss','once':True,'actions':[{'stop_generator':'dyn_portal'},{'stop_generator':'dyn_add'},{'advance_quest':'dynamic_lab'},{'complete_quest':'dynamic_lab'}]},
        {'id':'dyn_stop','when':'conversation_ended','conversation':'dyn','result':2,'once':False,'actions':[{'stop_generator':'dyn_portal'}]},
        {'id':'dyn_portal','when':'conversation_ended','conversation':'dyn','result':4,'once':False,'actions':[{'start_generator':'dyn_portal'}]}])
    return root

def lab_source(backend):
    import yaml
    tutorial=yaml.safe_load((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8'))
    first=copy.deepcopy(tutorial['scenes'][0]);base=copy.deepcopy(first['entries'][0]);base['id']='safe'
    root={'schema':2,'project_format':10,'chronicle':{'id':'rcm_dynamic','name':'RCM · Dynamic Encounter Lab','description':'Opcional: oleadas, refuerzos, jefe por fases, generador continuo y guardado.'},'entry':'lab','state':{'flags':{'armed':0}},'quests':[{'id':'combat','title':'Encuentros dinámicos','description':'Habla con Anezka para empezar. Sólo aparecen enemigos si aceptas.','steps':['Limpia las dos oleadas.','Vence a la rata por fases.'],'reward_xp':0}],'resources':{},'metadata':{'version':'1.0.0'},'scenes':[]}
    sourcepoints=[a['transform'] for a in first['actors'] if a.get('behavior')=='enemy']
    # Reuse accepted tutorial actor coordinates rather than inventing a point.
    accepted=copy.deepcopy(sourcepoints[0] if sourcepoints else base['transform'])
    points=[{'id':'spawn_a','name':'Aparición: posición de la rata del tutorial','transform':accepted}]
    npc=copy.deepcopy(first['actors'][0]);npc.update(id='mentor',name='Anezka: laboratorio',template='Anezka',conversation={'default':'lab'});npc.pop('inventory',None)
    conversation={'id':'lab','speaker':'mentor','camera':DEFAULT_DIALOGUE_CAMERA,'prompt':'Este laboratorio es independiente del encargo de la carta. Para las oleadas, acepta y acércate al barril del combate. Puedes probar oleadas, un jefe con refuerzos o un generador continuo. Guarda a mitad de combate y carga para comprobar que conserva el grupo.','choices':[{'text':'Preparar las oleadas. Después iré al barril.','result':1},{'text':'Probar el generador continuo (máximo tres ratas).','result':2},{'text':'Parar el generador continuo.','result':3},{'text':'Pausarlo.','result':4},{'text':'Reanudarlo.','result':5},{'text':'No empezar todavía.','result':6}]}
    common={'spawn_points':['spawn_a'],'persistence':'once'}
    row={'id':'lab','level':first['level'],'actors':[npc],'objects':[],'conversations':[conversation],'entries':[base],'default_entry':'safe','waypoints':points,'paths':[],'triggers':[],'encounters':[],'sequences':[], 'generators':[
        dict(id='waves',name='Dos oleadas de ratas',mode='waves',max_alive=3,waves=[{'groups':[{'role':'rats','template':'Rat','count':3}]},{'delay':2,'groups':[{'role':'rats','template':'Rat','count':2}]}],**common),
        dict(id='boss',name='Rata: jefe por fases',mode='boss',max_alive=1,waves=[{'groups':[{'role':'boss','template':'Rat','count':1,'health_multiplier':10}]}],boss={'role':'boss'},phases=[{'id':'half','percent':50,'actions':[{'start_generator':'adds'}]},{'id':'quarter','percent':25,'actions':[]}],**common),
        dict(id='adds',name='Dos refuerzos',mode='reinforcements',max_alive=2,waves=[{'groups':[{'role':'adds','template':'Rat','count':2}]}],**common),
        dict(id='continuous',name='Continuo: máximo tres vivos',mode='continuous',max_alive=3,interval=5,waves=[{'groups':[{'role':'rats','template':'Rat','count':1}]}],**common)],'events':[]}
    # Existing confirmed spatial-audio action, relocated to the accepted point.
    showcase=__import__('yaml').safe_load((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
    sound=copy.deepcopy(next(a for s in showcase['scenes'] for e in s['events'] for a in e['actions'] if 'play_sound' in a));sound['play_sound']['waypoint']='spawn_a'
    row['generators'][1]['phases'][1]['actions']=[sound]
    barrel=next((copy.deepcopy(o) for o in first.get('objects',[]) if next((t.get('kind') for t in backend.resources['templates'] if t['id']==o['template']),None)=='props'),None)
    if barrel:
        barrel['id']='barrel';barrel['name']='Barril del combate';row['objects']=[barrel]
        zone=copy.deepcopy(barrel['transform']);row['triggers']=[{'id':'arena','name':'Zona del barril','shape':'sphere','radius':120,'transform':zone,'once':False}]
        row['generators'][0]['visual']='barrel'
    else:row['triggers']=[{'id':'arena','name':'Zona del combate','shape':'sphere','radius':120,'transform':copy.deepcopy(accepted),'once':False}]
    row['events']=[{'id':'welcome','when':'scene_start','actions':[{'spawn':'mentor'}]+([{'spawn':'barrel'}] if barrel else [])},
        {'id':'begin','when':'conversation_ended','conversation':'lab','result':1,'once':True,'actions':[{'start_quest':'combat'},{'set_flag':'armed'}]},
        {'id':'boss','when':'generator_complete','generator':'waves','once':True,'actions':[{'advance_quest':'combat'},{'start_generator':'boss'}]},
        {'id':'complete','when':'generator_complete','generator':'boss','once':True,'actions':[{'stop_generator':'continuous'},{'stop_generator':'adds'},{'advance_quest':'combat'},{'complete_quest':'combat'}]}]
    row['events'].append({'id':'arena','when':'trigger_enter','trigger':'arena','once':False,'conditions':[{'flag':'armed','is_set':True}],'actions':[{'start_generator':'waves'}]})
    for result,key in [(2,'start_generator'),(3,'stop_generator'),(4,'pause_generator'),(5,'resume_generator')]:row['events'].append({'id':'control'+str(result),'when':'conversation_ended','conversation':'lab','result':result,'once':False,'actions':[{key:'continuous'}]})
    root['scenes']=[row];return root

def main():
    import yaml
    ws=Workspace(ROOT);backend=Backend(ws)
    source=yaml.safe_load((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
    for path,data in [('chronicles/showcase/project.yaml',add_showcase_station(source)),('chronicles/dynamic_lab/project.yaml',lab_source(backend))]:
        result=backend.validate(data)
        if not result.valid:raise ValueError([p.message for p in result.problems if p.severity=='ERROR'])
        ws.write(path,source_text(data))
    print('Optional Showcase station and independent dynamic lab sources validated; no game deployment.')

if __name__=='__main__':main()
