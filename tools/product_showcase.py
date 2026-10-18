"""Build a curated showcase from current, ordinary format-9 entities."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.input_limits import parse_source
from rcm.camera_presets import PRESETS
from rcm.campaign import ACTIONS,WHEN
from rcm.motions import slots,label


def generate(backend):
    root=copy.deepcopy(parse_source((ROOT/'chronicles/mini_chronicle/project.yaml').read_text(encoding='utf8')))
    root['chronicle']=dict(id='rcm_showcase',name='RCM · Taller del Narrador',description='Tres escenas, dos escenarios y un laboratorio opcional. Sigue el libro o explora cámaras, animaciones, recorridos y sonido.')
    root['metadata'].update(version='1.0.0',description=root['chronicle']['description'])
    first,field,returned=root['scenes']
    first['level']['name']='El taller';field['level']['name']='Prueba de campo';returned['level']['name']='Regreso: misma calle, otra escena'
    # Preserve the accepted movement/cinematic contracts, not historical patches.
    first['conversations'][0].update(camera='ots_speaker_close',prompt='Bienvenido al Taller del Narrador. Vamos a buscar un libro y volver para cerrar un pequeño encargo. Primero acepta y habla con la guía, a tu lado. Su laboratorio es opcional: puedes probar cámaras, música y recorridos antes de salir.')
    first['actors'][0]['name']='01 · Anezka: empieza aquí'
    root['resources']['templates'][0]['base']='Anezka'
    script=root['resources']['scripts'][0];script['id']='RCMShowcaseActor';script['source']='chronicles/showcase/resources/RCMShowcaseActor.java'
    root['resources']['templates'][0]['properties']['script']='RCMShowcaseActor'
    first['actors'][1]['template']='LonCiv2';first['actors'][1]['name']='02 · Guía: viaje y laboratorio opcional'
    field['actors'][0]['template']='Anezka';field['actors'][1]['template']='LonCiv2'
    returned['actors'][0]['template']='Anezka';returned['actors'][1]['template']='LonCiv2'
    root['state']['flags'].update(lab_note=10,zone_left=11,clock_seen=12,rat_seen=13,lab_pickup=14)
    first['events'][0]['actions']=[a for a in first['events'][0]['actions'] if 'start_patrol' not in a]
    gallery=[]
    for index,(preset,(human,unused_shot,unused_distance)) in enumerate(PRESETS.items()):
        ident='cam'+str(index+1);choices=[dict(text='Siguiente plano.',result=1),dict(text='Salir de la galería.',result=2)]
        if index==len(PRESETS)-1:choices[0]['text']='Terminar la galería.'
        gallery.append(dict(id=ident,speaker='guide',camera=preset,prompt=human+'. Mira el encuadre antes de continuar. Este plano se elige en Propiedades de la conversación; no necesitas escribir coordenadas de cámara.',choices=choices))
        if index<len(PRESETS)-1:first['events'].append(dict(id='cam_next'+str(index+1),when='conversation_ended',conversation=ident,result=1,once=False,actions=[dict(start_conversation='cam'+str(index+2))]))
    first['conversations'].extend(gallery)
    for conv in [c for c in first['conversations'] if c['id'] in ('guide','cleared')]:
        conv['choices'] += [dict(text='Laboratorio: ver los planos uno a uno.',result=4),dict(text='Laboratorio: animaciones.',result=5),dict(text='Laboratorio: recorrido y sonido.',result=6),dict(text='Omitir el combate y continuar.',result=7)]
        for result,actions in [(4,[{'start_conversation':'cam1'}]),(5,[{'start_conversation':'anim'}]),(6,[{'start_conversation':'lab'}]),(7,[{'remove_encounter':'optional_combat'},{'set_flag':'combat_done'}])]:
            first['events'].append(dict(id=conv['id']+'_lab'+str(result),when='conversation_ended',conversation=conv['id'],result=result,once=False,actions=actions))
    first['conversations'].append(dict(id='lab',speaker='guide',camera='ots_speaker_close',prompt='El recorrido lleva a la guía entre dos puntos de esta misma calle. Puedes iniciarlo, detenerlo y pausar su comportamiento. La música y el ambiente pertenecen a la escena; el trueno suena desde un punto concreto. Nada de esto es obligatorio para completar el encargo.',choices=[dict(text='Iniciar recorrido.',result=1),dict(text='Detener recorrido y pausar comportamiento.',result=2),dict(text='Activar comportamiento.',result=3),dict(text='Reproducir música, ambiente y trueno.',result=4),dict(text='Detener música y ambiente.',result=5),dict(text='Volver al recorrido principal.',result=6)]))
    first['waypoints'].append(dict(id='audio',name='Sonido del laboratorio',transform=dict(placement='absolute',position=[-62,-768,384],orientation=[0,0,0])))
    controls={1:[{'start_patrol':'guide_walk'}],2:[{'stop_patrol':'guide'},{'disable_ai':'guide'}],3:[{'enable_ai':'guide'}],4:[{'start_music':'London_Hub'},{'start_ambient':'amb_londonStreet'},{'play_sound':dict(resource='thunder_01',waypoint='audio',volume=60,min_distance=128,max_distance=512)}],5:[{'stop_music':True},{'stop_ambient':True}]}
    for result,actions in controls.items():first['events'].append(dict(id='controls'+str(result),when='conversation_ended',conversation='lab',result=result,once=False,actions=actions))
    supported=[s for s in slots(backend.resources,'LonCiv2') if s['mode'] in ('stand','idle','talk','listen') or s['mode'].startswith('gesture')][:8]
    nodes=[dict(id='menu',lines=[dict(text='Aquí sólo mostramos animaciones que existen en este modelo. Elige un gesto; al terminar puedes volver al menú o salir. En el editor se ajusta por nodo o por línea, en Propiedades.')],choices=[dict(text=label(slot),goto='m'+str(i)) for i,slot in enumerate(supported)]+[dict(text='Salir del laboratorio.',result=1)])]
    for i,slot in enumerate(supported):nodes.append(dict(id='m'+str(i),motion=slot['mode'],lines=[dict(text='Este es '+label(slot)+'. No todos los personajes tienen las mismas animaciones.')],choices=[dict(text='Ver otra animación.',goto='menu'),dict(text='Terminar.',result=100+i)]))
    first['conversations'].append(dict(id='anim',speaker='guide',camera='ots_speaker_close',entry='menu',nodes=nodes))
    first['objects'].append(dict(id='notice',name='Cartel del taller: leer nota',template='barrel1',transform=dict(placement='absolute',position=[-62,-1018,384],orientation=[0,0,0])))
    first['objects'].append(dict(id='sample',name='Libro del laboratorio: recoger',template='I_mini_ledger',quest_item=True,transform=dict(placement='absolute',position=[-62,-950,384],orientation=[0,0,0])))
    first['objects'].append(dict(id='talkprop',name='Atril: conversación con la guía',template='barrel1',transform=dict(placement='absolute',position=[-284,-821,384],orientation=[0,0,0])))
    first['events'][0]['actions'].append({'spawn':'notice'})
    first['events'][0]['actions'] += [{'spawn':'sample'},{'spawn':'talkprop'}]
    first['events'].append(dict(id='sample_taken',when='item_picked_up',item='sample',once=True,actions=[{'set_flag':'lab_pickup'}]))
    first['events'].append(dict(id='talk_prop',when='object_clicked',object='talkprop',once=False,actions=[{'start_conversation':'lab'}]))
    first['events'] += [dict(id='read_notice',when='object_clicked',object='notice',once=False,actions=[{'show_note':dict(title='El taller',text='El cartel es un objeto interactuable con una nota. Cuando cierras esta ventana, un evento puede cambiar el estado. Habla con Anezka para seguir el encargo; la guía ofrece el laboratorio opcional.')}]),dict(id='notice_closed',when='note_closed',once=False,actions=[{'set_flag':'lab_note'}]),dict(id='left_zone',when='trigger_leave',trigger='arrival_zone',once=True,actions=[{'set_flag':'zone_left'}]),dict(id='clock',when='timer',seconds=10,once=True,actions=[{'set_flag':'clock_seen'}]),dict(id='rat_killed',when='actor_killed',actor='enemy1',once=True,actions=[{'set_flag':'rat_seen'}])]
    first['actors'][1]['inventory']=['lab_key']
    first['objects'].append(dict(id='lab_key',name='Llave de la guía: inventario inicial',template='IronKeyLondon',transform=dict(placement='absolute',position=[-62,-768,384],orientation=[0,0,0])))
    first['events'].append(dict(id='state_lab',when='state_changed',once=True,conditions=[{'all':[{'flag':'lab_note','is_set':True},{'not':{'flag':'finished','is_set':True}}]}],actions=[{'clear_flag':'zone_left'}]))
    field['conversations'][1]['prompt']='Con el libro y la llave puedes volver a la calle inicial. Allí verás otra escena sobre la misma geometría: el testigo te espera para terminar. El plano y el sonido son una prueba opcional; puedes omitirlos.'
    root['playtests']=[dict(id='tour',name='Showcase completo',instructions='Anezka → guía (laboratorio opcional) → archivo → libro y llave → custodia → regreso → testigo. Prueba guardar/cargar y volver; los premios no deben repetirse. Las estaciones de cámaras, animaciones, recorrido y audio pueden repetirse o cerrarse en cualquier momento.')]
    names={'victoria':'Anezka','guide':'Guía','enemy1':'Rata de las minas','notice':'Cartel del taller','sample':'Libro del laboratorio','talkprop':'Atril','lab_key':'Llave de la guía','archivist':'Archivera','keeper':'Custodia','witness':'Testigo','courier':'Mensajera'}
    for scene in root['scenes']:
        for kind in ('actors','objects'):
            for row in scene[kind]:
                if row['id'] in names:
                    row['comment']=(row['name']+'\n'+row.get('comment','')).rstrip();row['name']=names[row['id']]
    def human_names(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in {'prompt','text','title','description'} and isinstance(child,str):value[key]=child.replace('Victoria','Anezka')
                else:human_names(child)
        elif isinstance(value,list):
            for child in value:human_names(child)
    human_names(root)
    return root


def matrix(root):
    rows=[]
    for scene in root['scenes']:
        sid=scene['id']
        for kind in ('entries','actors','objects','triggers','waypoints','paths','sequences','conversations','generators'):
            for row in scene.get(kind,[]):
                link='rcm://'+sid+'/'+kind+'/'+row['id']
                rows.append(dict(capability=kind,classification='NORMAL',scene=sid,entity=row['id'],link=link,in_game=True,in_editor=True,runtime_verified=False))
                def nested(value):
                    if isinstance(value,list):
                        for child in value:nested(child)
                    elif isinstance(value,dict):
                        if len(value)==1 and next(iter(value)) in ACTIONS:rows.append(dict(capability='action:'+next(iter(value)),classification='NORMAL',scene=sid,entity=row['id'],link=link,in_game=True,in_editor=True,runtime_verified=False))
                        else:
                            for child in value.values():nested(child)
                nested(row)
        for event in scene['events']:
            for capability in ['when:'+event['when'],*['action:'+k for action in event['actions'] for k in action]]:
                rows.append(dict(capability=capability,classification='NORMAL',scene=sid,entity=event['id'],link='rcm://'+sid+'/events/'+event['id'],in_game=True,in_editor=True,runtime_verified=False))
    found={r['capability'] for r in rows}
    for capability in [*['when:'+k for k in WHEN],*['action:'+k for k in ACTIONS]]:
        if capability not in found:rows.append(dict(capability=capability,classification='ADVANCED' if capability in {'action:control_door','action:open_exit','action:close_exit'} else 'NORMAL',scene='',entity='',link='',in_game=False,in_editor=True,runtime_verified=False))
    for capability in ('Original NCP','Native door/exit with valid Cast ID','Static inspector','NOT writer fields','Custom Java','Model-specific motions','Own camera path capture'):
        rows.append(dict(capability=capability,classification='EXPERIMENTAL',scene='',entity='',link='',in_game=capability=='Own camera path capture',in_editor=True,runtime_verified=False))
    return rows


def main():
    ws=Workspace(ROOT);backend=Backend(ws);root=generate(backend)
    from dynamic_examples import add_showcase_station
    root=add_showcase_station(root)
    java=(ROOT/'chronicles/mini_chronicle/resources/RCMMiniActor.java').read_text(encoding='utf8').replace('RCMMiniActor','RCMShowcaseActor');ws.write('chronicles/showcase/resources/RCMShowcaseActor.java',java)
    validation=backend.validate(root)
    if not validation.valid:raise ValueError([p.message for p in validation.problems if p.severity=='ERROR'])
    ws.write('chronicles/showcase/project.yaml',source_text(root))
    from closure_examples import main as add_director
    add_director();root=parse_source((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
    rows=matrix(root);ws.write('research/product_close/showcase_matrix.json',json.dumps(rows,ensure_ascii=False,indent=2))
    headers='| CAPACIDAD | NORMAL / ADVANCED / EXPERIMENTAL | DEMO IN GAME | DEMO IN EDITOR | SCENE | ENTITY | DEEPLINK | OFFLINE VERIFIED | RUNTIME VERIFIED |\n|---|---|---|---|---|---|---|---|---|'
    lines=['# Showcase: capacidades reales','', 'Generada desde las entidades del ejemplo y ACTIONS/WHEN actuales. Sin demo significa que se conserva en autoría o como límite; no se simula una puerta mediante un prop. Compilación y ejecución con doubles se documentan por separado del ensayo nativo.','',headers]
    for r in rows:lines.append('| '+' | '.join([r['capability'],r['classification'],'YES' if r['in_game'] else 'NO','YES' if r['in_editor'] else 'NO',r['scene'],r['entity'],r['link'],'SOURCE VALIDATED' if r['in_game'] else 'CATALOGUED','MANUAL TEST REQUIRED'])+' |')
    ws.write('docs/SHOWCASE_MATRIX.md','\n'.join(lines)+'\n')
    print('Showcase source validated. Native test remains manual.')


if __name__=='__main__':main()
