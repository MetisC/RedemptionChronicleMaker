"""Reproducible single curated acceptance adventure; never starts the game.

Its source is deliberately curated, not presented as GUI authoring evidence.
Qt authoring and real spatial controls are exercised separately.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.deployment import default_game
from rcm.packages import create_package
from rcm.spatial.assets import Assets
from rcm.spatial.geometry import read_nil
from rcm.spatial.math3d import Raycaster

def make_source():
    def transform(pos,yaw=180):return dict(placement='absolute',position=pos,orientation=[0,0,yaw])
    def actor(key,name,pos,conversation=None,template='businessWoman',enemy=False):
        row=dict(id=key,name=name,template=template,transform=transform(pos),behavior='enemy' if enemy else 'npc')
        if conversation:row['conversation']={'default':conversation}
        return row
    def conv(key,speaker,prompt,choices):return dict(id=key,speaker=speaker,prompt=prompt,choices=[dict(text=text,result=i+1) for i,text in enumerate(choices)])
    def event(key,when,actions,**fields):return dict(id=key,when=when,actions=actions,**fields)
    def travel(scene):return {'travel':{'scene':scene,'entry':'safe'}}
    def scene(key,level,title,arrival):return dict(id=key,level=dict(source=level,name=title),actors=[],objects=[],conversations=[],events=[],triggers=[],encounters=[],sequences=[],entries=[dict(id='safe',name='Llegada segura',transform=transform(arrival,0))],default_entry='safe',waypoints=[],paths=[])
    quay=scene('quay','EastLondon','Londres: el pacto',[1016,-210,0])
    archive=scene('archive','GunHaven','El archivo de la deuda',[200,790,0])
    returned=scene('return','EastLondon','Londres: las voces recuerdan',[1016,-210,0])
    quay['actors']=[actor('victoria','Victoria · empieza aquí',[1016,-54,0],template='T_rcm9_victoria'),actor('guide','Guía · viajes y combate opcional',[850,-210,0],'guide')]
    for i,pos in enumerate([[850,-550,0],[950,-550,0],[850,-650,0],[950,-650,0]]):quay['actors'].append(actor('enemy'+str(i+1),'Enemigo de prueba '+str(i+1),pos,template='brujahFled_MD',enemy=True))
    quay['encounters']=[dict(id='optional_combat',name='Combate opcional · cuatro enemigos',actors=['enemy'+str(i+1) for i in range(4)])]
    quay['actors'][1]['conversation'].update(when_flag='combat_done',then='cleared')
    quay['conversations']=[
        conv('intro','victoria','Un libro puede resolver nuestra deuda. Acepta el encargo y la guía te llevará al archivo. Puedes rechazarlo y volver a hablar sin perder los controles.',['Acepto el encargo.','No quiero involucrarme.']),
        conv('pact','victoria','Recuerdo nuestro pacto. La guía te lleva al archivo; después entrega el libro al testigo en el regreso.',['Seguimos juntos.','Me quedo aquí.']),
        conv('guide','guide','Primero habla con Victoria. El combate es una estación opcional: sólo empieza si lo eliges expresamente.',['Viajar al archivo.','Quedarme aquí.','Activar combate opcional: cuatro enemigos.']),
        conv('cleared','guide','El encuentro ha terminado; el premio se entrega una sola vez. Puedes seguir con el circuito.',['Viajar al archivo.','Quedarme aquí.']),
    ]
    quay['conversations'][0]['choices'][0]['set_flag']='alliance'
    quay['events']=[event('arrival','scene_start',[{'spawn':'victoria'},{'spawn':'guide'},{'start_music':'London_Hub'},{'start_ambient':'amb_londonStreet'},{'start_patrol':'guide_walk'}]),
        event('new','actor_clicked',[{'start_conversation':'intro'}],actor='victoria',conditions=[{'flag':'alliance','is_set':False}]),
        event('remember','actor_clicked',[{'start_conversation':'pact'}],actor='victoria',conditions=[{'flag':'alliance','is_set':True}]),
        event('accept','conversation_ended',[{'start_quest':'ledger'},{'advance_quest':'ledger'},{'start_quest':'debt'}],conversation='intro',result=1,once=True),
        event('to_archive','conversation_ended',[travel('archive')],conversation='guide',result=1,once=False,conditions=[{'flag':'alliance','is_set':True}]),
        event('cleared_trip','conversation_ended',[travel('archive')],conversation='cleared',result=1,once=False,conditions=[{'flag':'alliance','is_set':True}]),
        event('combat','conversation_ended',[{'spawn_encounter':'optional_combat'}],conversation='guide',result=3,once=True),
        event('combat_done','encounter_complete',[{'set_flag':'combat_done'},{'reward_xp':100}],encounter='optional_combat'),
    ]
    quay['waypoints']=[dict(id='guide_a',name='Guía: inicio',transform=transform([850,-210,0])),dict(id='guide_b',name='Guía: vuelta',transform=transform([850,-320,0]))]
    quay['paths']=[dict(id='guide_walk',name='Paseo corto de la guía',actor='guide',points=['guide_a','guide_b'],loop=True,speed=90,tolerance=24)]
    archive['actors']=[actor('archivist','Archivera · elige una rama',[200,944,0],'ledger'),actor('keeper','Custodia · regreso y cámara',[340,850,0],'back')]
    archive['objects']=[dict(id='book',name='El libro de la deuda',template='I_rcm9_ledger',quest_item=True,transform=transform([300,900,0]))]
    archive['conversations']=[conv('ledger','archivist','Elige cómo recuperar el libro. La negociación y la intimidación llevan a respuestas distintas en el regreso. Sólo recibirás un libro.',['Negociar y recibir el libro.','Me voy.','Intimidar y recibir el libro.']),
        conv('back','keeper','Cuando tengas el libro, te llevaré al regreso. Allí te espera el testigo. La cámara es una prueba aparte y devuelve el control tras tres segundos.',['Viajar al regreso.','Quedarme aquí.','Probar plano y sonido situados.'])]
    archive['events']=[event('arrival','scene_start',[{'spawn':'archivist'},{'spawn':'keeper'},{'start_music':'Haven'}]),
        event('peace','conversation_ended',[{'set_flag':'peaceful'},{'give_item':'book'},{'advance_quest':'ledger'},{'advance_quest':'debt'}],conversation='ledger',result=1,once=True,conditions=[{'quest':'ledger','step':1}]),
        event('force','conversation_ended',[{'clear_flag':'peaceful'},{'give_item':'book'},{'advance_quest':'ledger'},{'advance_quest':'debt'}],conversation='ledger',result=3,once=True,conditions=[{'quest':'ledger','step':1}]),
        event('to_return','conversation_ended',[travel('return')],conversation='back',result=1,once=False,conditions=[{'owns_item':'book'}]),
        event('camera','conversation_ended',[{'play_sequence':'two_shot'},{'play_sound':dict(resource='thunder_01',waypoint='sound',volume=60,min_distance=128,max_distance=512)}],conversation='back',result=3,once=False),
    ]
    archive['sequences']=[dict(id='two_shot',name='Dos personajes',actor='keeper',duration=3,shot='medium',angle='medium',preset='two_shot')]
    archive['waypoints']=[dict(id='sound',name='Fuente de sonido de prueba',transform=transform([200,790,0]))]
    returned['actors']=[actor('witness','Testigo · entrega y final',[1016,-54,0]),actor('courier','Mensajera · vuelve al comienzo',[850,-210,0],'back')]
    returned['conversations']=[conv('peace','witness','La archivera dice que elegiste negociar. Entrega el libro y dejaremos saldada la deuda.',['Entregar el libro y cerrar ambas quests.','Todavía no.']),
        conv('force','witness','La archivera recuerda tu intimidación. Entrega el libro; la deuda acabará, aunque Londres recordará cómo actuaste.',['Entregar el libro y cerrar ambas quests.','Todavía no.']),
        conv('final','witness','Las voces de Londres recuerdan tu decisión. Ambas quests han terminado y la recompensa sólo se entrega una vez. Puedes guardar y volver al principio con la mensajera.',['Terminar la conversación.','Volver a hablar después.']),
        conv('back','courier','Esta escena usa la misma geometría de EastLondon y tiene sus propios NPC. Puedes volver al inicio para comprobar el pacto y repetir el circuito.',['Volver al comienzo.','Quedarme aquí.'])]
    returned['events']=[event('arrival','scene_start',[{'spawn':'witness'},{'spawn':'courier'},{'start_patrol':'courier_walk'}]),
        event('peace','actor_clicked',[{'start_conversation':'peace'}],actor='witness',conditions=[{'flag':'peaceful','is_set':True},{'flag':'finished','is_set':False}]),
        event('force','actor_clicked',[{'start_conversation':'force'}],actor='witness',conditions=[{'flag':'peaceful','is_set':False},{'flag':'finished','is_set':False}]),
        event('final','actor_clicked',[{'start_conversation':'final'}],actor='witness',conditions=[{'flag':'finished','is_set':True}]),
        event('back','conversation_ended',[travel('quay')],conversation='back',result=1,once=False)]
    for cid in ('peace','force'):
        returned['events'].append(event('finish_'+cid,'conversation_ended',[{'take_item':'archive.book'},{'advance_quest':'ledger'},{'complete_quest':'ledger'},{'advance_quest':'debt'},{'complete_quest':'debt'},{'set_flag':'finished'},{'start_music':'Haven'}],conversation=cid,result=1,once=True,conditions=[{'quest':'ledger','step':2},{'owns_item':'archive.book'},*[{'flag':'visited'+str(i),'is_set':True} for i in range(3)]]))
    returned['waypoints']=[dict(id='courier_a',name='Mensajera: inicio',transform=transform([850,-210,0])),dict(id='courier_b',name='Mensajera: vuelta',transform=transform([850,-320,0]))]
    returned['paths']=[dict(id='courier_walk',name='Paseo corto de la mensajera',actor='courier',points=['courier_a','courier_b'],loop=True,speed=90,tolerance=24)]
    for i,s in enumerate((quay,archive,returned)):
        pos=s['entries'][0]['transform']['position'];s['triggers']=[dict(id='arrival_zone',name='Zona de llegada',shape='box',transform=transform([pos[0],pos[1],pos[2]+60],0),size=[160,160,120],once=True)]
        s['events'].append(event('arrival_trigger','trigger_enter',[{'set_flag':'visited'+str(i)}],trigger='arrival_zone'))
    return dict(schema=2,project_format=9,chronicle=dict(id='rcm_circuit',name='Las voces de Londres · Circuito',description='Una aventura de prueba: pacto, libro, decisión, regreso y final. Combate opcional.'),entry='quay',state={'flags':{'alliance':1,'peaceful':2,'finished':3,'combat_done':4,'visited0':5,'visited1':6,'visited2':7}},scenes=[quay,archive,returned],quests=[dict(id='ledger',title='El libro de la deuda',description='Recupera y entrega el libro.',steps=['Aceptar el encargo','Recuperar el libro','Entregarlo al testigo'],reward_xp=500),dict(id='debt',title='Una deuda, dos caminos',description='Elige negociación o intimidación; la crónica recordará tu decisión.',steps=['Elegir cómo recuperar el libro','Sellar el pacto'],reward_xp=150)],resources={'templates':[dict(id='T_rcm9_victoria',base='businessWoman',mode='inherit',properties={'ai':'AI_rcm9','script':'RCM9Actor'}),dict(id='I_rcm9_ledger',base='ledger',mode='inherit',properties={})],'ai_profiles':[dict(id='AI_rcm9',base='civilian',properties={'wanderRadius':0})],'scripts':[dict(id='RCM9Actor',source='tests/fixtures/chronicles/circuit/resources/RCM9Actor.java')],'textures':[]},metadata=dict(author='Redemption Chronicle Maker',version='0.9.0',requires_game='Redemption 1.1',description='Prueba manual aplazada; generación y compilación comprobadas.',dependencies=[]),build_options={'debug':True},playtests=[dict(id='circuit',name='Circuito único',instructions='docs/PHASE9_PLAYTEST.md; partida nueva.')])

def main():
    ws=Workspace(ROOT,default_game(ROOT));backend=Backend(ws);data=make_source();floors=[]
    for s in data['scenes']:
        s['level']['environment_scene']=backend.levels[s['level']['source']]['scenes'][0]
        entry=backend.levels[s['level']['source']]['geometry'][0];ray=Raycaster(read_nil(Assets(backend).read(entry['path'],entry['archive'])))
        for kind in ('entries','actors','objects','waypoints'):
            for entity in s[kind]:
                pos=entity['transform']['position'];hit=ray.ground(pos,64,128)
                if hit is None:raise ValueError('Sin suelo en '+s['id']+'/'+entity['id'])
                entity['transform']['position']=hit.position.tolist();floors.append(dict(scene=s['id'],kind=kind,id=entity['id'],position=hit.position.tolist(),native_collision_verified=False))
    ws.write('tests/fixtures/chronicles/circuit/resources/RCM9Actor.java','public class RCM9Actor extends Codex { public RCM9Actor() { CodexConsole.Print(0,0,"RCM9 own actor initialized"); } }\n')
    ws.write('tests/fixtures/chronicles/circuit/project.yaml',source_text(data));report=backend.build(data)
    package='build/rcm_circuit/rcm_circuit.rcmpack';create_package(ws,'rcm_circuit',package)
    evidence=dict(source='tests/fixtures/chronicles/circuit/project.yaml',curated_source=True,gui_authored_adventure=False,package=package,scenes=report['scenes'],npc=6,enemies=4,quests=2,patrols=2,ground_checks=floors,native_engine_test=False)
    ws.write('research/phase9/circuit_build.json',json.dumps(evidence,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in evidence.items() if k!='ground_checks'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
