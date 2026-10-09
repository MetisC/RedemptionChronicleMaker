"""Author the owned tutorial as seven lessons with a separate laboratory.

Writes only to the workspace, preserving the old sources in a ZIP. This is
our own data generator; it never executes original authoring applications.
"""
import copy
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'cache/vendor'), str(ROOT / 'src')]
import yaml
from rcm.camera_presets import DEFAULT_DIALOGUE_CAMERA, PRESETS


def transform(position=(-176, -612, 384)):
    return dict(placement='absolute', position=list(position), orientation=[0, 0, 180])


def actor(ident, name, template, conversation=None, position=(-176, -612, 384)):
    row = dict(id=ident, name=name, template=template, transform=transform(position), behavior='npc')
    if conversation:
        row['conversation'] = dict(default=conversation)
    return row


def conv(ident, speaker, text, accept, camera=DEFAULT_DIALOGUE_CAMERA):
    return dict(id=ident, speaker=speaker, camera=camera, prompt=text,
                choices=[dict(text=accept, result=1), dict(text='Omitir esta parte y continuar.', result=2)])


def event(ident, when, actions, **fields):
    return dict(id=ident, when=when, actions=actions, **fields)


def done(lesson):
    return {'set_flag': 'step' + str(lesson)}


def current(step):
    return [dict(quest='guide', step=step - 1)]


def main():
    folder = ROOT / 'chronicles/tutorial'
    old = yaml.safe_load((folder / 'project.yaml').read_text(encoding='utf8'))
    backup = ROOT / 'research/round0/guided_tutorial' / ('sources_before_' + str(time.time_ns()) + '.zip')
    backup.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(backup, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in folder.rglob('*'):
            if p.is_file():
                z.write(p, p.relative_to(ROOT))
    original = old['scenes'][0]
    workshop = copy.deepcopy(original)
    workshop['level']['name'] = 'Tutorial · lecciones 1 a 5'
    workshop['actors'] = [actor('mentor', '01 · Tomás: empezar', 'T_tutor_mentor', 'menu'),
        actor('camera', '02 · Vera: conversación y cámara', 'gothGirl1', 'camera'),
        actor('director', '03 · Anezka: una cutscene', 'Anezka', 'cinema'),
        actor('keeper', '04 · Elena: inventario y llave', 'LonCiv2', 'inventory'),
        actor('gate', '05 · Agente: cambiar el layout', 'Bobbie', 'gate'),
        actor('walker', 'Paseante de la lección 3', 'LonCiv3', position=(-342, -1018, 384)),
        actor('lab', 'Laboratorio opcional · profesor de animación', 'ST_Christof_MD', 'lab', (-342, -612, 384)),
        actor('labwalker', 'Paseante del laboratorio', 'LonCiv3', position=(-342, -730, 384))]
    workshop['actors'][3]['inventory'] = ['npc_key', 'npc_book']
    # Keep these IDs: the player's existing NPF may retain a reward/key wrapper.
    workshop['objects'] = copy.deepcopy([r for r in original['objects'] if r['id']!='stage_door'])
    for row in workshop['objects']:
        if row['id'] == 'barrel':
            row['name'] = 'Barril · leer la nota'
            row['transform'] = transform((-342, -768, 384))
        if row['id'] == 'reward':
            row['name'] = 'Libro recogible · laboratorio'
            row['transform'] = transform((-342, -800, 384))
        if row['id'] in {'key','npc_key'}:
            row['template']='T_tutor_key'
            row['name']='Llave de hueso del tutorial'
    workshop['objects'].append(dict(id='stage_door',name='Puerta del decorado · se eleva durante la película',template='testdoor',transform=transform((-342,-950,384))))
    workshop['conversations'] = [
        conv('menu', 'mentor', 'Bienvenido. Soy Tomás y te acompañaré al empezar. No hace falta que recorras Londres buscando a los demás: cada profesor vendrá a esta misma esquina. El journal te recordará qué toca hacer. Si quieres cambiar dónde empieza tu personaje, abre Espacio 3D > Inicio en el editor y mueve la entrada safe. ¿Seguimos con Vera?', 'Sí, vamos con Vera.'),
        conv('camera', 'camera', 'Hola, soy Vera. Vamos a ver cómo cambia una conversación según dónde pongamos la cámara. Te enseñaré los planos uno a uno: pulsa Siguiente cuando quieras cambiar y tómate el tiempo que necesites. En el editor están en Cámara de diálogo, al seleccionar la conversación. El plano sobre el hombro es el que usamos por defecto.', 'Enséñame los planos.'),
        conv('cinema', 'director', 'Soy Anezka. Vamos a contar una pequeña historia sin movernos de esta calle: alguien espera detrás de una puerta, la puerta se levanta y le deja pasar. Verás el lugar, la apertura y su paseo desde varios planos. Dura doce segundos. En Cámaras > walk_scene puedes cambiar los planos, cuándo se abre la puerta y cuándo empieza a caminar el personaje. ¿La vemos?', 'Sí, vamos a verla.'),
        conv('inventory', 'keeper', 'Hola, soy Elena. Llevo una llave y un libro; puedes preparar lo que lleva cualquier personaje en Editar inventario inicial > + Del catálogo. Voy a darte una llave. Mira después tu inventario: un evento puede comprobar si la tienes para dejarte pasar. Si prefieres omitirlo, te la daré igualmente para que puedas seguir.', 'Gracias, dame la llave.'),
        conv('gate', 'gate', '¿Ves el barril a mi derecha? Si lo pulsas antes de hablar conmigo, puedes leer una nota. Ahora vamos a cambiar lo que hay en esta calle: el barril desaparecerá, nosotros nos iremos y llegará otro instructor. Las calles serán las mismas. En el editor lo preparas con + Escena > Nuevo layout sobre este level y un evento Viaje. Así puedes reutilizar un lugar en distintos momentos de la historia.', 'Vale, veamos cómo cambia la calle.'),
        dict(id='lab', speaker='lab', camera=DEFAULT_DIALOGUE_CAMERA, entry='opening', nodes=[
            dict(id='opening', lines=[dict(speaker='lab', text='Aquí puedes probar cosas a tu aire. No hace falta que hagas nada de esto para seguir con los profesores. ¿Qué te apetece probar?', motion='gesture10')], choices=[dict(text='Movimiento y cámaras.', goto='motion'), dict(text='Animaciones de conversación.', goto='motions'), dict(text='Objetos y decisiones que se recuerdan.', goto='objects'), dict(text='Leer una nota de ejemplo.', result=11), dict(text='Ya volveré, gracias.', result=10)]),
            dict(id='motion', lines=[dict(speaker='lab', text='Ese paseante es sólo para nuestras pruebas. Podemos hacerlo caminar o detenerlo. También hay un travelling del juego original; ese ejemplo todavía necesita más pruebas.', motion='gesture7')], choices=[dict(text='Que empiece a caminar.', result=1), dict(text='Que se detenga.', result=2), dict(text='Pausar su AI.', result=3), dict(text='Reanudar su AI.', result=4), dict(text='Ver el travelling original (experimental).', result=5), dict(text='Volver.', goto='opening')]),
            dict(id='motions', lines=[dict(speaker='lab', text='Normalmente el juego decide cuándo hablar y escuchar. Si quieres una actuación distinta, selecciona un nodo en el editor y cambia Animación al hablar. Vamos a ver los movimientos básicos; también puedo enseñarte mis gestos.')], choices=[dict(text=text, goto=mode) for mode,text in [('stand','Reposo: estar de pie.'),('idle','Gesto de reposo.'),('talk','Hablar.'),('listen','Escuchar.'),('gestures','Ver otros gestos.'),('opening','Volver al laboratorio.')]]),
            dict(id='gestures', lines=[dict(speaker='lab',text='Estos gestos pertenecen a este modelo. El nombre del archivo aparece en el editor: así puedes reconocer el que acabas de ver.')], choices=[dict(text='Ver gesto '+str(i)+'.',goto='gesture'+str(i)) for i in (3,7,8,9,10)]+[dict(text='Volver.',goto='motions')]),
            *[dict(id=mode,motion=mode,lines=[dict(speaker='lab',text=text)],choices=[dict(text='Elegir otro movimiento.',goto='motions'),dict(text='Volver al laboratorio.',goto='opening')]) for mode,text in [('stand','Ahora estoy en reposo. Es la postura normal de pie.'),('idle','Este es mi gesto de reposo: un movimiento que el personaje hace mientras espera.'),('talk','Así habla este personaje. Si dejas la animación en Automática, el juego se encarga de usarla.'),('listen','Esta es la animación de escuchar. Aquí la fuerzo durante mi frase para que puedas verla.')]],
            *[dict(id='gesture'+str(i), motion='gesture'+str(i), lines=[dict(speaker='lab', text='Este es el gesto '+str(i)+'. Puedes elegirlo en Animación al hablar al seleccionar este nodo en el editor. Prueba otro cuando quieras.')], choices=[dict(text='Elegir otro gesto.', goto='gestures'), dict(text='Volver al laboratorio.', goto='opening')]) for i in (3,7,8,9,10)],
            dict(id='objects', lines=[dict(speaker='lab', text='Acércate a la zona que hay un poco más allá de mí: aparecerá un libro que puedes recoger. En Debug > Leer trace queda anotado cuándo entras, sales y lo recoges. También puedes activar una flag: es una marca con la que la crónica recuerda lo que has hecho.')], choices=[dict(text='Voy a buscar el libro.', result=6), dict(text='Activar la flag del laboratorio.', result=7), dict(text='Desactivarla.', result=8), dict(text='Volver.', goto='opening')])])]
    # Each frame is a separate conversation. RETURN releases the old native
    # dialog before the next one sets its shot; the user controls every change.
    camera_texts = {
        'ots_speaker_close': 'Estamos sobre tu hombro, cerca de Vera. Ves a quien habla y un poco de quien escucha: es nuestro plano habitual.',
        'speaker_extreme': 'Ahora nos acercamos mucho al rostro de Vera. Va bien para una reacción importante, pero puede resultar demasiado intenso para una charla larga.',
        'listener_extreme': 'Este mismo acercamiento mira ahora a tu personaje. Sirve para enseñar su reacción mientras escucha.',
        'speaker_close': 'Este es un primer plano de Vera. Su rostro tiene el protagonismo; suele funcionar bien en los diálogos.',
        'listener_close': 'Ahora el primer plano es de tu personaje. Puedes alternar entre quien habla y quien escucha.',
        'ots_listener_close': 'Hemos pasado al otro hombro: miramos hacia tu personaje desde el lado de Vera.',
        'ots_speaker': 'Volvemos a mirar a Vera sobre tu hombro, pero con algo más de espacio alrededor.',
        'ots_listener': 'El mismo plano más abierto, desde el hombro de Vera hacia tu personaje.',
        'profile_speaker': 'Vemos a Vera de perfil. Un cambio lateral puede dar variedad a una conversación.',
        'profile_listener': 'Aquí vemos de perfil a tu personaje. Es la otra mitad del plano anterior.',
        'two_shot': 'Ahora entráis los dos en el encuadre. Este plano ayuda a mostrar la distancia y la relación entre ambos.',
        'medium': 'El plano medio deja ver más del cuerpo y de la calle. Es útil si importan los gestos o el lugar donde habláis.',
        'full': 'Nos alejamos para ver el cuerpo entero. Así puedes mostrar a los personajes dentro del escenario.'}
    order = [DEFAULT_DIALOGUE_CAMERA, *[k for k in PRESETS if k!=DEFAULT_DIALOGUE_CAMERA]]
    examples = [('framed' if i==0 else 'frame_'+str(i+1), preset) for i,preset in enumerate(order)]
    for i,(ident,preset) in enumerate(examples):
        text = f'{i+1} de {len(examples)} · {PRESETS[preset][0]}. '+camera_texts[preset]
        if i==len(examples)-1:text+=' Eso es todo. Puedes elegir el que más te guste en Cámara de diálogo. Anezka nos espera para enseñarnos una escena con movimiento.'
        example = conv(ident,'camera',text,'Siguiente plano.' if i<len(examples)-1 else 'Ya los he visto. Vamos con Anezka.',preset)
        example['choices'][1]['text']='Omitir los demás planos y continuar.'
        workshop['conversations'].insert(2+i,example)
    workshop['events'] = [event('arrival', 'scene_start', [{'start_quest': 'guide'}, {'spawn': 'mentor'}, {'spawn': 'lab'}, {'spawn': 'labwalker'}, {'start_music': 'London_Hub'}, {'start_ambient': 'amb_londonStreet'}])]
    for conversation, lesson in [('menu', 1), ('inventory', 4)]:
        workshop['events'].append(event('finish_' + conversation, 'conversation_ended', [done(lesson)], conversation=conversation, conditions=current(lesson), once=False))
    workshop['events'] += [event('show_frame', 'conversation_ended', [{'start_conversation': 'framed'}], conversation='camera', result=1, conditions=current(2), once=False),
        event('skip_camera', 'conversation_ended', [done(2)], conversation='camera', result=2, conditions=current(2), once=False),
        event('film', 'conversation_ended', [{'play_sequence': 'walk_scene'}], conversation='cinema', result=1, conditions=current(3), once=False),
        event('skip_film', 'conversation_ended', [done(3)], conversation='cinema', result=2, conditions=current(3), once=False),
        event('film_finished', 'sequence_ended', [done(3)], sequence='walk_scene', conditions=current(3), once=False)]
    for i,(ident,_) in enumerate(examples):
        actions = [{'start_conversation':examples[i+1][0]}] if i<len(examples)-1 else [done(2)]
        workshop['events'].append(event('next_'+ident,'conversation_ended',actions,conversation=ident,result=1,conditions=current(2),once=False))
        workshop['events'].append(event('skip_'+ident,'conversation_ended',[done(2)],conversation=ident,result=2,conditions=current(2),once=False))
    for lesson, old_actor, next_actor in [(1, 'mentor', 'camera'), (2, 'camera', 'director'), (3, 'director', 'keeper'), (4, 'keeper', 'gate')]:
        actions = [{'advance_quest': 'guide'}, {'remove': old_actor}]
        if lesson == 2:
            actions.extend([{'spawn': 'walker'},{'spawn':'stage_door'}])
        if lesson == 3:
            actions.extend([{'remove': 'walker'},{'remove':'stage_door'}])
        if lesson == 4:
            # Supply/verify the physical item before advancing/removing Elena.
            actions = [{'give_item':'key'}, {'set_flag':'has_key'}, *actions, {'spawn':'barrel'}]
        actions.append({'spawn': next_actor})
        workshop['events'].append(event('next_' + str(lesson), 'state_changed', actions, conditions=[dict(flag='step'+str(lesson), is_set=True), *current(lesson)], once=True))
    workshop['events'].append(event('change_layout', 'conversation_ended', [done(5), {'remove': 'barrel'}, {'advance_quest': 'guide'}, {'travel': dict(scene='combat', entry='safe')}], conversation='gate', conditions=[*current(5),dict(owns_item='key')], once=True))
    lab_actions = [({'start_patrol': 'lab_walk'}, 1), ({'stop_patrol': 'labwalker'}, 2), ({'disable_ai': 'labwalker'}, 3), ({'enable_ai': 'labwalker'}, 4), ({'play_sequence': 'original_path'}, 5), ({'set_flag': 'lab_ready'}, 7), ({'clear_flag': 'lab_ready'}, 8)]
    for action, result in lab_actions:
        workshop['events'].append(event('lab_' + str(result), 'conversation_ended', [action], conversation='lab', result=result, once=False))
    workshop['events'] += [
        event('welcome_note','scene_start',[{'show_note':dict(title='Bienvenido al tutorial',text='Tomás te espera justo delante. Habla con él y sigue las lecciones una a una. Cada profesor vendrá al mismo lugar.\n\nEl journal te recuerda el paso actual. Christof, a la izquierda, tiene un laboratorio opcional para experimentar.\n\nEsta ventana es una nota nativa. En el editor puedes crearla en Eventos, con Historia / Mostrar nota. Cierra la ventana para empezar.')}],once=True),
        event('lab_note','conversation_ended',[{'show_note':dict(title='Una carta de ejemplo',text='Querido visitante:\n\nEstas ventanas sirven para cartas, prólogos, instrucciones y avisos. No necesitan un personaje ni una conversación.\n\nEn el editor elige un objeto y pulsa Añadir nota al usar. Puedes escribir un título y varios párrafos. También puedes abrir una conversación con un personaje al usar un objeto.\n\nPara hacer algo cuando se cierre la ventana, crea un evento Cierran una nota; una flag permite distinguir cuál se ha leído.')}],conversation='lab',result=11,once=False),
        event('barrel_note','object_clicked',[{'show_note':dict(title='Una nota sobre el barril',text='Este barril tiene una nota. Basta con pulsarlo para leerla.\n\nSelecciona barrel en Objetos del editor y pulsa Añadir nota al usar para localizar el evento. Cuando el agente cambie el layout, el barril y esta interacción desaparecerán de esta calle.')}],object='barrel',once=False),
        event('door_talk','object_clicked',[{'start_conversation':'lab'}],object='stage_door',once=False),
    ]
    workshop['triggers'] = [dict(id='station', name='Laboratorio · zona del libro', shape='box', transform=transform((-342, -800, 444)), size=[100, 100, 120], once=True)]
    workshop['events'] += [event('reward_spawn', 'trigger_enter', [{'spawn': 'reward'}, {'set_flag': 'entered_zone'}], trigger='station', once=True),
        event('pickup', 'item_picked_up', [{'set_flag': 'picked_up'}, {'reward_xp': 10}], item='reward', once=True),
        event('zone_left', 'trigger_leave', [{'set_flag': 'left_zone'}], trigger='station', once=False)]
    workshop['waypoints'] = [dict(id='walker_a',name='Puerta: esperar detrás',transform=transform((-342,-1018,384))),dict(id='walker_b',name='Puerta: salir hacia la calle',transform=transform((-342,-878,384))),dict(id='lab_a', name='Laboratorio: inicio', transform=transform((-342, -730, 384))), dict(id='lab_b', name='Laboratorio: final', transform=transform((-342, -800, 384)))]
    workshop['paths'] = [dict(id='walker_walk', name='Lección 3 · recorrido corto', actor='walker', points=['walker_a', 'walker_b'], loop=False, speed=60, tolerance=24),
        dict(id='lab_walk', name='Laboratorio · paseo', actor='labwalker', points=['lab_a', 'lab_b'], loop=True, speed=60, tolerance=24)]
    workshop['sequences'] = copy.deepcopy(original['sequences'])
    workshop['sequences'][0].update(duration=12,move_at=6,prop_motion=dict(object='stage_door',at=3,duration=3,translation=[0,0,208]),steps=[dict(at=0,actor='walker',focus='stage_door',preset='aerial',angle='high',transition=0),dict(at=3,actor='walker',focus='stage_door',preset='full',transition=.7),dict(at=6,actor='walker',preset='full',transition=.6),dict(at=9,actor='director',preset='two_shot',transition=.5)])
    workshop['sequences'][1]['actor'] = 'lab'
    workshop['encounters'] = []
    combat = copy.deepcopy(old['scenes'][1])
    combat['level']['name'] = 'Tutorial · lección 6: otro layout'
    combat['actors'][0] = actor('guide', '06 · Instructor: encuentro opcional', 'LonCiv3', 'layout')
    combat['actors'][0]['conversation'].update(when_flag='rat_spawned', then='fighting')
    combat['actors'][1]['transform'] = transform((-342, -878, 384))
    combat['conversations'] = [conv('layout', 'guide', 'La calle sigue aquí, pero el barril y los otros profesores ya se han ido. Eso es cambiar de layout. Para probar un encuentro voy a hacer aparecer una sola rata, cerca de donde llegaste. Es un enemigo sencillo. En el editor la encontrarás en combat > Encuentros > one_rat. ¿La hacemos aparecer?', 'Sí, vamos a probar el combate.'),
        conv('fighting', 'guide', 'La rata está ahí cerca. Cierra esta conversación para poder atacarla. Cuando la mates pasaremos al último paso. Si no te apetece combatir, también puedes omitirlo.', 'Vamos allá.')]
    combat['events'] = [event('arrival', 'scene_start', [{'spawn': 'guide'}]),
        event('fight', 'conversation_ended', [{'spawn_encounter': 'one_rat'}, {'set_flag': 'rat_spawned'}], conversation='layout', result=1, once=True),
        event('skip', 'conversation_ended', [{'remove_encounter': 'one_rat'}, done(6)], conversation='layout', result=2, once=False),
        event('skip_started', 'conversation_ended', [{'remove_encounter': 'one_rat'}, done(6)], conversation='fighting', result=2, once=False),
        event('cleared', 'encounter_complete', [{'set_flag': 'rat_killed'}, done(6), {'reward_xp': 10}], encounter='one_rat', once=True),
        event('next', 'state_changed', [{'advance_quest': 'guide'}, {'travel': dict(scene='finished', entry='safe')}], conditions=[dict(flag='step6', is_set=True), *current(6)], once=True)]
    final = copy.deepcopy(old['scenes'][2])
    final['level']['name'] = 'Tutorial · lección 7: guardar y comprobar'
    final['actors'] = [actor('mentor', '07 · Tomás: guardar y terminar', 'LonCiv3', 'final')]
    final['conversations'] = [conv('final', 'mentor', 'Ya has llegado al final. Antes de terminar, prueba a guardar la partida y volver a cargarla: deberías seguir aquí y conservar la llave. Las flags sirven para recordar decisiones como las que has tomado. En el editor, Guardar conserva tu proyecto y BUILD CHRONICLE prepara los archivos para el juego. Para repetir estas lecciones desde el principio, crea una partida nueva.', 'Gracias, hemos terminado.')]
    final['events'] = [event('arrival', 'scene_start', [{'spawn': 'mentor'}]),
        event('finish', 'conversation_ended', [done(7), {'advance_quest': 'guide'}, {'complete_quest': 'guide'}, {'set_flag': 'finished'}], conversation='final', conditions=current(7), once=True)]
    old.update(scenes=[workshop, combat, final], quests=[dict(id='guide', title='Tutorial RCM · paso a paso', description='Siete lecciones; sólo se muestra la actual.', steps=[
        '1/7 · Tomás te espera delante de ti. Habla con él para empezar; los demás vendrán a esta misma esquina.',
        '2/7 · Ahora habla con Vera. Te enseñará los encuadres uno a uno. Pulsa Siguiente cuando quieras cambiar, o salta los demás.',
        '3/7 · Habla con Anezka: una puerta se abrirá y un personaje pasará por ella. La película dura doce segundos; puedes omitirla antes de empezar.',
        '4/7 · Elena te dará una llave. Habla con ella y mira después tu inventario.',
        '5/7 · Habla con el agente y fíjate en el barril. Vais a cambiar lo que hay en la calle sin cambiar sus edificios.',
        '6/7 · El instructor puede hacer aparecer una rata cerca de ti. Pídeselo y mátala para seguir, o dile que prefieres omitir el combate.',
        '7/7 · Tomás ha vuelto para despedirse. Prueba a guardar y cargar la partida; después habla con él para terminar.'], reward_xp=20)])
    old['chronicle'].update(name='RCM · Tutorial paso a paso', description='Siete lecciones cortas y un laboratorio opcional separado. Un level con tres layouts.')
    old['state']['flags'] = {**{'step'+str(i): i for i in range(1, 8)}, 'has_key': 8, 'rat_spawned': 9, 'rat_killed': 10, 'finished': 11, 'entered_zone': 12, 'picked_up': 13, 'left_zone': 14, 'lab_ready': 15}
    old['resources']['templates'][0]['base'] = 'LonCiv3'
    old['resources']['templates']=[r for r in old['resources']['templates'] if r['id']!='T_tutor_key']+[dict(id='T_tutor_key',base='BoneKey',mode='inherit',properties=dict(item_type=0))]
    old['metadata'].update(version='0.9.12', description='Tutorial guiado, notas nativas, objetos interactivos y reposo tras gestos.')
    old['playtests'] = [dict(id='tutorial', name='Siete lecciones', instructions='Partida nueva. Seguir los objetivos 1 a 7; repetir en otra partida usando Omitir en cada profesor. Verificar cutscene de doce segundos tras los 13 planos, apertura de puerta, paseo tras apertura, cámara y HUD restaurados, llave visible en inventario, laboratorio accesible a la izquierda, barril desaparecido, rata junto al inicio, final y save/load.')]
    (folder / 'project.yaml').write_text(yaml.safe_dump(old, allow_unicode=True, sort_keys=False, width=110), encoding='utf8')
    print('Tutorial authored; original sources backed up:', backup)


if __name__ == '__main__':
    main()
