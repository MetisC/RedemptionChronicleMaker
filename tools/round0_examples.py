"""Two curated examples, grounded against the original meshes; never runs game."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor'),str(ROOT/'tools')]
from phase9_circuit import make_source
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.deployment import default_game
from rcm.spatial.assets import Assets
from rcm.spatial.geometry import read_nil
from rcm.spatial.math3d import Raycaster
from rcm.packages import create_package

def transform(pos,yaw=180):return dict(placement='absolute',position=pos,orientation=[0,0,yaw])
def actor(ident,name,pos,conversation=None,template='businessWoman',enemy=False):
    row=dict(id=ident,name=name,template=template,transform=transform(pos),behavior='enemy' if enemy else 'npc')
    if conversation:row['conversation']={'default':conversation}
    return row
def item(ident,name,template,pos):return dict(id=ident,name=name,template=template,transform=transform(pos))
def conversation(ident,speaker,prompt,choices,camera='native'):
    return dict(id=ident,speaker=speaker,prompt=prompt,camera=camera,choices=[dict(text=t,result=i+1) for i,t in enumerate(choices)])
def event(ident,when,actions,**filters):return dict(id=ident,when=when,actions=actions,**filters)
def travel(scene):return {'travel':dict(scene=scene,entry='safe')}
def scene(ident,title):return dict(id=ident,level=dict(source='EastLondon',name=title),actors=[],objects=[],conversations=[],events=[],triggers=[],encounters=[],sequences=[],entries=[dict(id='safe',name='Inicio elegido · muelle',transform=transform([1016,-210,0],0))],default_entry='safe',waypoints=[],paths=[])

def mini():
    data=make_source();data['chronicle']=dict(id='rcm_mini',name='Las voces de Londres · Mini crónica',description='Pacto, investigación, dos mapas, tres layouts, llave, libro y combate opcional con una rata.')
    data['metadata']['version']='0.9.6'
    data['resources']['scripts'][0]=dict(id='RCMMiniActor',source='chronicles/mini_chronicle/resources/RCMMiniActor.java')
    template=data['resources']['templates'][0];template['id']='T_mini_victoria';template['properties']['script']='RCMMiniActor'
    template['properties']['ai']='AI_mini';data['resources']['ai_profiles'][0]['id']='AI_mini'
    data['resources']['templates'][1]['id']='I_mini_ledger'
    quay,archive,returned=data['scenes'];quay['actors'][0]['template']='T_mini_victoria';archive['objects'][0]['template']='I_mini_ledger'
    quay['actors']=[a for a in quay['actors'] if a['id'] not in {'enemy2','enemy3','enemy4'}]
    enemy=quay['actors'][-1];enemy['template']='Rat';enemy['name']='Rata de las minas · combate fácil y opcional'
    quay['encounters'][0].update(name='Una rata · combate opcional',actors=['enemy1'])
    quay['conversations'][2]['choices'][2]['text']='Activar combate opcional: una rata básica.'
    quay['conversations'][0]['camera']='native';quay['conversations'][1]['camera']='two_shot'
    archive['sequences'][0].update(duration=7,steps=[dict(at=0,actor='keeper',preset='two_shot'),dict(at=2,actor='archivist',preset='speaker_close',transition=.6),dict(at=4,actor='keeper',preset='full',transition=1.0)],move_path='keeper_walk')
    archive['conversations'][1]['prompt']=archive['conversations'][1]['prompt'].replace('tras tres segundos','tras siete segundos; incluye tres planos y mi recorrido')
    archive['waypoints'] += [dict(id='keeper_a',name='Custodia: inicio',transform=transform([340,850,0])),dict(id='keeper_b',name='Custodia: destino',transform=transform([340,960,0]))]
    archive['paths']=[dict(id='keeper_walk',name='Cutscene · custodia en movimiento',actor='keeper',points=['keeper_a','keeper_b'],loop=False,speed=60,tolerance=24)]
    archive['objects'].append(item('key','Llave del regreso','IronKeyLondon',[300,900,0]))
    for ev in archive['events']:
        if ev['id'] in {'peace','force'}:ev['actions'].insert(1,{'give_item':'key'})
        if ev['id']=='to_return':ev['conditions'].append({'owns_item':'key'})
    data['playtests']=[dict(id='story',name='Mini crónica · recorrido completo',instructions='Tutorial / Ayuda → guía local. Victoria acepta; guía lleva al archivo; archivera entrega libro y llave; custodia vuelve al muelle; testigo recibe libro. Guarda y carga, vuelve a entrar y comprueba que no duplica premios. Combate de una rata sólo si lo eliges. Cámara de 7 s: tres planos y custodia caminando.')]
    for row in (quay,returned):
        row['entries'][0]['name']='Inicio del jugador · calle de EastLondon'
        for kind in ('entries','actors','objects','waypoints','triggers'):
            for entity in row[kind]:
                pos=entity['transform']['position'];entity['transform']['position']=[pos[0]-1192,pos[1]-558,pos[2]+384]
    enemy['transform']['position']=[-342,-1018,384]
    return data

def tutorial():
    first=scene('workshop','Tutorial RCM · taller junto al muelle');combat=scene('combat','Tutorial RCM · mismo muelle, otro layout');final=scene('finished','Tutorial RCM · layout final')
    first['actors']=[actor('mentor','01 · Mentora / decisiones y flags',[1016,-54,0],'menu',template='T_tutor_mentor'),actor('camera','02 · Cineasta / cámaras y movimiento',[850,-210,0],'camera'),actor('keeper','03 · Custodia / inventario y llaves',[1130,-210,0],'inventory'),actor('gate','04 · Guardiana / cambio de scene',[1016,-370,0],'gate'),actor('walker','05 · Caminante / waypoints y AI',[850,-320,0])]
    first['actors'][2]['inventory']=['npc_key','npc_book']
    first['objects']=[item('npc_key','Llave en inventario de la custodia','IronKeyLondon',[1130,-210,0]),item('npc_book','Libro en inventario de la custodia','ledger',[1130,-210,0]),item('key','Llave del jugador','BoneKey',[1016,-210,0]),item('barrel','Prop · barril reutilizado','barrel1',[1100,-210,0]),item('reward','Libro recogible de prueba','ledger',[1100,-310,0])]
    first['objects'][2]['quest_item']=True
    first['conversations']=[conversation('menu','mentor','Bienvenido. Cada personaje es una estación del tutorial. Inicia la quest, habla con cineasta y custodia y lleva una llave a la guardiana. El otro layout usa exactamente este mismo muelle.',['Iniciar quest y activar el flag de acceso.','¿Dónde se edita todo esto?','Cerrar y volver después.']),conversation('camera','camera','Puedes comparar la cámara automática del juego, un plano propio, una cutscene con caminante y tres planos, o el travelling original EASTOttoVan. La última opción es experimental: no hemos creado ese recorrido.',['Diálogo con plano propio.','Cutscene: caminante y tres planos, 8 segundos.','Travelling original, 8 segundos.','Cerrar.']),conversation('framed','camera','Este diálogo usa el preset sobre el hombro. En el editor selecciona la conversación y cambia Cámara de diálogo; Automática deja que decida el motor.',['Volver a los controles.','Terminar.'],camera='ots_speaker'),conversation('inventory','keeper','Mi inventario inicial contiene una llave y un libro; selecciónalos en el editor, Editar inventario inicial, + Del catálogo. Para la salida te doy una llave distinta.',['Recibir la llave del jugador.','Cerrar.']),conversation('gate','gate','Para entrar en el layout de combate necesitas iniciar la quest y llevar la llave. El combate es una sola rata básica de las primeras minas; sólo aparece en el otro layout. Si te falta algo, vuelve a mentora o custodia.',['Abrir salida lógica con flag Y objeto; cambiar layout.','Cerrar.']),conversation('help','mentor','Tutorial / Ayuda contiene enlaces a cada entidad y los pasos exactos del editor. Las puertas físicas originales y el writer de travelling NCP siguen pendientes: no son funciones completas.',['Volver.','Cerrar.'])]
    menu=first['conversations'][0];prompt=menu.pop('prompt');choices=menu.pop('choices')
    choices.insert(2,dict(text='Herramientas: AI, movimiento, prop y flag.',goto='tools'))
    menu.update(entry='opening',nodes=[dict(id='opening',lines=[dict(speaker='mentor',text=prompt)],choices=choices),dict(id='tools',lines=[dict(speaker='mentor',text='Estas acciones afectan al caminante y al barril. Puedes repetir pausa/reanudar; retirar el barril es permanente para esta partida.')],choices=[dict(text=t,result=i+4) for i,t in enumerate(['Pausar AI del caminante.','Reanudar AI del caminante.','Detener recorrido.','Iniciar recorrido.','Retirar barril.','Desactivar flag ready.'])]+[dict(text='Volver al menú.',goto='opening')])])
    first['events']=[event('arrival','scene_start',[*[{'spawn':a['id']} for a in first['actors']],{'spawn':'barrel'},{'start_music':'London_Hub'},{'start_ambient':'amb_londonStreet'},{'start_patrol':'walker_walk'}]),event('accept','conversation_ended',[{'advance_quest':'guide'},{'complete_quest':'guide'},{'start_quest':'lesson'},{'advance_quest':'lesson'},{'set_flag':'access'}],conversation='menu',result=1,once=True),event('help','conversation_ended',[{'start_conversation':'help'}],conversation='menu',result=2),event('framed','conversation_ended',[{'start_conversation':'framed'}],conversation='camera',result=1),event('cutscene','conversation_ended',[{'play_sequence':'walk_scene'},{'play_sound':dict(resource='thunder_01',waypoint='walker_a',volume=50,min_distance=128,max_distance=512)}],conversation='camera',result=2),event('travelling','conversation_ended',[{'play_sequence':'original_path'}],conversation='camera',result=3),event('key','conversation_ended',[{'give_item':'key'},{'set_flag':'has_key'}],conversation='inventory',result=1,once=True),event('unlock','conversation_ended',[{'set_flag':'unlocked'},travel('combat')],conversation='gate',result=1,once=False,conditions=[{'all':[{'flag':'access','is_set':True},{'owns_item':'key'}]}]),event('reward_spawn','trigger_enter',[{'spawn':'reward'},{'set_flag':'entered_zone'}],trigger='station',once=True),event('pickup','item_picked_up',[{'set_flag':'picked_up'},{'reward_xp':10}],item='reward'),event('zone_left','trigger_leave',[{'set_flag':'left_zone'}],trigger='station',once=False),event('timer','timer',[{'set_flag':'timer_done'}],seconds=4),event('key_seen','state_changed',[{'set_flag':'ready'}],conditions=[{'all':[{'flag':'has_key','is_set':True},{'any':[{'flag':'access','is_set':True},{'not':{'flag':'picked_up','is_set':True}}]}]}])]
    first['triggers']=[dict(id='station',name='Trigger de prop / pickup',shape='box',transform=transform([1100,-310,60],0),size=[100,100,120],once=True)]
    for i,(action,value) in enumerate([('disable_ai','walker'),('enable_ai','walker'),('stop_patrol','walker'),('start_patrol','walker_walk'),('remove','barrel'),('clear_flag','ready')]):first['events'].append(event('tool'+str(i),'conversation_ended',[{action:value}],conversation='menu',result=i+4,once=False))
    first['events'][-1]['conditions']=[{'flag':'ready','is_set':True}]
    first['waypoints']=[dict(id='walker_a',name='Caminar: inicio / sonido',transform=transform([850,-320,0])),dict(id='walker_b',name='Caminar: destino',transform=transform([850,-460,0]))]
    first['paths']=[dict(id='walker_walk',name='Paseo del caminante',actor='walker',points=['walker_a','walker_b'],loop=True,speed=60,tolerance=24)]
    first['sequences']=[dict(id='walk_scene',name='Cutscene · caminante y cambios de plano',actor='walker',duration=8,shot='medium',angle='medium',move_path='walker_walk',steps=[dict(at=0,actor='walker',preset='full',transition=.3),dict(at=3,actor='camera',preset='speaker_close',transition=.6),dict(at=5,actor='walker',preset='two_shot',transition=1.0)]),dict(id='original_path',name='Travelling ORIGINAL · EASTOttoVan · experimental',actor='camera',duration=8,shot='medium',angle='medium',camera_path='EASTOttoVan',path_speed=1)]
    combat['actors']=[actor('guide','Mismo level · nuevo layout',[1016,-54,0],'layout'),actor('rat','Rata básica · combate opcional',[850,-550,0],template='Rat',enemy=True)]
    combat['encounters']=[dict(id='one_rat',name='Una rata básica',actors=['rat'])]
    combat['conversations']=[conversation('layout','guide','Misma geometría, contenido nuevo. Puedes probar una única rata o volver al taller. No estás obligado a combatir. Tras matarla podrás ir al layout final.',['Crear la rata.','Ir al layout final (tras combatir).','Volver al taller.','Cerrar.'])]
    combat['conversations'][0]['choices'].append(dict(text='Retirar la rata sin premio y volver al taller.',result=5))
    combat['events']=[event('arrival','scene_start',[{'spawn':'guide'},{'start_music':'London_Hub'},{'start_conversation':'layout'}]),event('fight','conversation_ended',[{'spawn_encounter':'one_rat'}],conversation='layout',result=1,once=True),event('cleared','encounter_complete',[{'set_flag':'combat_done'},{'advance_quest':'lesson'},{'reward_xp':10}],encounter='one_rat',conditions=[{'quest':'lesson','state':'active'}]),event('death','actor_killed',[{'set_flag':'rat_killed'}],actor='rat'),event('next','conversation_ended',[travel('finished')],conversation='layout',result=2,once=False,conditions=[{'flag':'combat_done','is_set':True}]),event('back','conversation_ended',[travel('workshop')],conversation='layout',result=3,once=False)]
    combat['events'].append(event('cancel','conversation_ended',[{'remove_encounter':'one_rat'},travel('workshop')],conversation='layout',result=5,once=False))
    final['actors']=[actor('mentor','Final · flags y persistencia',[1016,-54,0],'final')]
    final['conversations']=[conversation('final','mentor','El muelle tiene ahora un tercer layout. Completa la quest, guarda y carga; vuelve al taller para comprobar reentrada y que la llave no se duplica.',['Completar quest y retirar la llave.','Volver al taller.','Cerrar.'],camera='speaker_close')]
    final['events']=[event('arrival','scene_start',[{'spawn':'mentor'}]),event('finish','conversation_ended',[{'advance_quest':'lesson'},{'complete_quest':'lesson'},{'take_item':'workshop.key'},{'set_flag':'finished'},{'stop_music':True},{'stop_ambient':True}],conversation='final',result=1,once=True,conditions=[{'quest':'lesson','step':2}]),event('back','conversation_ended',[travel('workshop')],conversation='final',result=2,once=False)]
    guide='Habla con 01 Mentora, junto al punto de inicio, y elige Iniciar quest. En el editor, Espacio 3D > Inicio muestra la llegada; selecciona Mentora en Actores para editar su conversación.'
    first['events'] += [event('help_back','conversation_ended',[{'start_conversation':'menu'}],conversation='help',result=1),event('framed_back','conversation_ended',[{'start_conversation':'camera'}],conversation='framed',result=1)]
    first['events'].insert(0,event('journal_init','scene_start',[{'start_quest':'guide'}]))
    flags=['access','has_key','unlocked','entered_zone','picked_up','left_zone','timer_done','ready','combat_done','rat_killed','finished']
    # The previous Otto/van neighbourhood has failed the user's native walk test.
    # Anchor the whole tutorial at the original walking bobbie (sector 119),
    # maintaining station spacing and keeping all layouts on the same street.
    for row in (first,combat,final):
        row['level']['name']=row['level']['name'].replace('junto al muelle','en la calle').replace('mismo muelle','misma calle')
        row['entries'][0]['name']='Inicio del jugador · calle de EastLondon'
        for kind in ('entries','actors','objects','waypoints','triggers'):
            for entity in row[kind]:
                pos=entity['transform']['position'];entity['transform']['position']=[pos[0]-1192,pos[1]-558,pos[2]+384]
        for conv in row['conversations']:
            for key in ('prompt',):
                if key in conv:conv[key]=conv[key].replace('muelle','calle')
            for node in conv.get('nodes',[]):
                for line in node['lines']:line['text']=line['text'].replace('muelle','calle')
    combat['actors'][1]['transform']['position']=[-342,-1018,384]
    return dict(schema=2,project_format=9,chronicle=dict(id='rcm_tutor',name='RCM · Tutorial de creación',description='Un único level, tres layouts. Estaciones de autoría, cine, inventario, llave, flags, quest y rata opcional.'),entry='workshop',state={'flags':{f:i+1 for i,f in enumerate(flags)}},scenes=[first,combat,final],quests=[dict(id='lesson',title='Aprender a crear',description='Completa el circuito del taller.',steps=['Aceptar la lección de 01 Mentora.','Prueba las cámaras con 02 Cineasta y recibe la llave de 03 Custodia. Después habla con 04 Guardiana: acceso y llave permiten cambiar al layout de combate. Allí la guía crea una rata básica sólo si lo pides. Mátala para avanzar. Editor: conversaciones, inventario inicial, eventos, flags, entradas y escenas.','Pide a la guía viajar al layout final y habla con la mentora para completar la lección. Guarda, carga y vuelve al taller para comprobar el estado. Editor: Campaña / Quests > escenas y eventos; cada layout reutiliza la misma geometría.'],reward_xp=20),dict(id='guide',title='Tutorial RCM: empieza aquí',description=guide,steps=[guide])],resources={'templates':[dict(id='T_tutor_mentor',base='businessWoman',mode='inherit',properties=dict(ai='AI_tutor',script='RCMTutorActor'))],'ai_profiles':[dict(id='AI_tutor',base='civilian',properties={'wanderRadius':0})],'scripts':[dict(id='RCMTutorActor',source='chronicles/tutorial/resources/RCMTutorActor.java')],'textures':[]},metadata=dict(author='RCM',version='0.9.6',description='Estaciones editables. Primeros planos y cutscenes con control nativo; recorridos NCP requieren prueba manual en motor.',requires_game='Redemption 1.1',dependencies=[]),build_options={'debug':True},playtests=[dict(id='tutorial',name='Tutorial · un único level',instructions='El journal carga Tutorial RCM: empieza aquí al llegar, antes de crear NPC. Abre Tutorial / Ayuda en el editor. Mentora inicia lección; cineasta compara cámaras, primeros planos y cutscene; custodia da llave; guardiana cambia layout; guía crea una rata si lo eliges o vuelve al taller; final completa quest. Guarda/carga y reentra. Comparar UI/cámara, inventario, planos, rutas, sonido, flags y premios. No aceptar el travelling original o puertas como verificados sin probarlos.')])

def main():
    ws=Workspace(ROOT,default_game(ROOT));backend=Backend(ws);assets=Assets(backend);rays={};reports=[]
    for folder,source in [('tutorial',tutorial()),('mini_chronicle',mini())]:
        for script in source['resources']['scripts']:
            ws.write(script['source'],'public class '+script['id']+' extends Codex { public '+script['id']+'() { CodexConsole.Print(0,0,"RCM own actor initialized"); } }\n')
        floors=[]
        for row in source['scenes']:
            name=row['level']['source'];row['level']['environment_scene']=backend.levels[name]['scenes'][0]
            if name not in rays:
                entry=backend.levels[name]['geometry'][0];rays[name]=Raycaster(read_nil(assets.read(entry['path'],entry['archive'])))
            for kind in ('entries','actors','objects','waypoints'):
                for entity in row[kind]:
                    pos=entity['transform']['position'];hit=rays[name].ground(pos,64,128)
                    if hit is None:raise ValueError('Sin suelo '+row['id']+'/'+entity['id'])
                    entity['transform']['position']=hit.position.tolist();floors.append(dict(scene=row['id'],entity=entity['id'],position=hit.position.tolist(),native_collision_verified=False))
        ws.write('chronicles/'+folder+'/project.yaml',source_text(source));validation=backend.validate(source)
        if not validation.valid:raise ValueError([p.message for p in validation.problems])
        report=backend.build(source);package='build/'+source['chronicle']['id']+'/'+source['chronicle']['id']+'.rcmpack';create_package(ws,source['chronicle']['id'],package)
        reports.append(dict(project=folder,id=source['chronicle']['id'],status=report['status'],ground_checks=floors,problems=[dict(severity=p.severity,message=p.message) for p in validation.problems],native_game_test=False,source_curated=True,gui_authored=False))
    ws.write('research/round0/examples_build.json',json.dumps(reports,ensure_ascii=False,indent=2));print(json.dumps([{k:v for k,v in r.items() if k!='ground_checks'} for r in reports],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
