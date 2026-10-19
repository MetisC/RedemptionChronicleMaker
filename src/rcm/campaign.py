"""Schema 2 campaigns. Legacy scene codecs remain shared and unchanged."""
from dataclasses import dataclass
import copy, math, re
import yaml
from .model import mapping, sequence, identifier, text, parse_project, UniqueLoader

# One shared library for authoring, validation and Java generation.
ACTIONS = {
 'spawn': ('Mundo / Crear entidad','entity'), 'remove': ('Mundo / Retirar entidad','entity'),
 'start_conversation': ('Historia / Conversación','conversations'),
 'show_note': ('Historia / Mostrar nota','note'),
 'set_flag': ('Estado / Activar flag','flags'), 'clear_flag': ('Estado / Desactivar flag','flags'),
 'start_quest': ('Quest / Iniciar','quests'), 'advance_quest': ('Quest / Siguiente paso','quests'),
 'complete_quest': ('Quest / Completar','quests'),
 'give_item': ('Inventario / Dar objeto al jugador','item'), 'take_item': ('Inventario / Quitar objeto del jugador','item_global'),
 'reward_xp': ('Recompensa / Experiencia del jugador','number'),
 'spawn_encounter': ('Encuentro / Crear grupo','encounters'), 'remove_encounter': ('Encuentro / Retirar grupo','encounters'),
 'jump': ('Viaje / Cambiar ubicación','scenes'),
 'start_music': ('Audio / Música','music'), 'stop_music': ('Audio / Detener música','none'),
 'push_music': ('Audio / Música temporal','temporary_music'), 'pop_music': ('Audio / Restaurar música anterior','none'),
 'start_ambient': ('Audio / Ambiente','ambient'), 'stop_ambient': ('Audio / Detener ambiente','none'),
 'play_sequence': ('Cámara / Secuencia','sequences'), 'release_camera': ('Cámara / Devolver control','none'),
 'enable_ai': ('AI / Activar','actors'), 'disable_ai': ('AI / Pausar','actors'),
 'travel': ('Viaje / Escena y punto de llegada','arrival'),
 'start_patrol': ('Movimiento / Seguir recorrido','paths'), 'stop_patrol': ('Movimiento / Detener actor','actors'),
 'open_exit': ('Salida original / Abrir','native_exit'), 'close_exit': ('Salida original / Cerrar','native_exit'),
 'control_door': ('Puerta existente / Movimiento','door'),
 'control_original': ('Escenario original / Objeto o puerta','original'),
 'run_event': ('Evento / Ejecutar','events'),
 'set_actor_clan': ('Actor / Cambiar clan','wtd_clan'),
 'set_discipline': ('Actor / Establecer disciplina','wtd_discipline'),
 'play_sound': ('Audio / Sonido situado','spatial_sound'),
 'stop_sound': ('Audio / Detener sonido situado','sound_source'),
 'camera_shot': ('Cámara / Cambiar plano','camera_shot'),
 'play_camera_path': ('Cámara / Reproducir travelling','camera_path_action'),
 'camera_fade': ('Cámara / Fundido','camera_fade'),
 'camera_flash': ('Cámara / Flash blanco','camera_flash'),
 'camera_filter': ('Cámara / Filtro blanco','camera_filter'),
 'clear_camera_effects': ('Cámara / Limpiar efectos','none'),
 'look_at': ('Actor / Mirar a actor','look_at'),
 'look_at_point': ('Actor / Mirar a punto','look_at_point'),
 'play_motion': ('Actor / Reproducir gesto','play_motion'),
 'stop_actor': ('Actor / Detener acción','actors'),
 'set_weather': ('Ambiente / Cambiar clima','weather'),
 'set_dynamic_light': ('Ambiente / Luz dinámica','dynamic_light'),
 'clear_dynamic_light': ('Ambiente / Retirar luz dinámica','entity'),
}
WHEN = {'manual':'Desde otro evento','scene_start':'Inicia la escena','actor_clicked':'Hablan con actor','object_clicked':'Usan un objeto','note_closed':'Cierran una nota','conversation_ended':'Termina conversación',
 'trigger_enter':'Entra en trigger','trigger_leave':'Sale de trigger','actor_killed':'Actor muerto (muestreo)',
 'item_picked_up':'Objeto en inventario (muestreo)','encounter_complete':'Todos los enemigos muertos',
 'timer':'Tiempo desde entrada','state_changed':'Se cumple una condición',
 'sequence_ended':'Termina una secuencia de cámara'}
from .dynamic_encounters import GENERATOR_ACTIONS,GENERATOR_EVENTS
ACTIONS.update({key:(label,'generators') for key,label in zip(GENERATOR_ACTIONS,('Encuentro dinámico / Iniciar','Encuentro dinámico / Detener','Encuentro dinámico / Pausar','Encuentro dinámico / Reanudar','Encuentro dinámico / Reiniciar (avanzado)'))})
WHEN.update({key:label for key,label in zip(GENERATOR_EVENTS,('Empieza encuentro dinámico','Empieza oleada','Termina oleada','Termina encuentro dinámico','Se detiene encuentro dinámico'))})
WHEN['generator_threshold']='Cruza umbral de vida del jefe'

@dataclass(frozen=True)
class Campaign:
    source: dict
    scenes: tuple
    reserved: dict
    @property
    def id(self): return self.source['chronicle']['id']
    @property
    def name(self): return self.source['chronicle']['name']
    @property
    def level(self): return next(p.level for s,p in self.scenes if s['id']==self.source['entry'])
    @property
    def entities(self): return tuple(e for s,p in self.scenes for e in p.entities)
    @property
    def conversations(self): return tuple(c for s,p in self.scenes for c in p.conversations)

def parse_campaign(source, levels, resources):
    raw = yaml.load(source, Loader=UniqueLoader) if isinstance(source,str) else copy.deepcopy(source)
    if len(yaml.safe_dump(raw))>1024*1024: raise ValueError('Campaña demasiado grande')
    root=mapping(raw,{'schema','chronicle','state','entry','scenes','quests','runtime_profile'}, {'schema','chronicle','entry','scenes'},'campaña')
    modern=root.get('runtime_profile') in ('phase9','phase10')
    if 'runtime_profile' in root and not modern: raise ValueError('Perfil de runtime desconocido')
    if type(root['schema']) is not int or root['schema']!=2: raise ValueError('schema de campaña debe ser 2')
    chron=mapping(root['chronicle'],{'id','name','description','difficulty'},{'id','name'},'chronicle')
    from .combat_difficulty import selected
    difficulty=selected(root)
    if difficulty!='normal' and not modern:raise ValueError('La dificultad configurable requiere formato 9 o 10')
    identifier(chron['id'],'chronicle.id',14); text(chron['name'],'chronicle.name')
    flags=mapping(root.get('state',{}),{'flags'},label='state').get('flags',{})
    mapping(flags,set(flags),label='flags')
    for k,v in flags.items():
        identifier(k,'flag')
        if type(v) is not int or not 0<=v<=255: raise ValueError('Flags de autoría: 0..255')
    if len(set(flags.values()))!=len(flags): raise ValueError('Índices de flag duplicados')
    def indexed(rows,label):
        result={}
        for row in sequence(rows,label):
            if not isinstance(row,dict): raise ValueError(label+': requiere registros')
            is_event=label.endswith(' events')
            key=identifier(row.get('id'),label+'.id',64 if is_event else 16,allow_upper=is_event)
            if key in result: raise ValueError(label+': ID duplicado '+key)
            result[key]=row
        return result
    scenes=indexed(root['scenes'],'scenes'); quests=indexed(root.get('quests',[]),'quests')
    if not 1<=len(scenes)<=32 or root['entry'] not in scenes: raise ValueError('Entrada ausente o número de escenas fuera de 1..32')
    reserved={}
    def reserve(key):
        reserved[key]=256+len(reserved)
        if reserved[key]>=1024: raise ValueError('Se exceden los 1024 flags de crónica que permite el motor')
    total_quests=0
    for q in quests.values():
        mapping(q,{'id','title','description','steps','reward_xp'},{'id','title','description','steps'},'quest '+q['id'])
        text(q['title'],'quest.title'); text(q['description'],'quest.description')
        steps=sequence(q['steps'],'quest.steps')
        if not 1<=len(steps)<=32: raise ValueError('Quest requiere 1..32 pasos')
        for st in steps: text(st,'quest.step')
        xp=q.get('reward_xp',0)
        if type(xp) is not int or not 0<=xp<=1000000: raise ValueError('Recompensa inválida')
        for suffix in ['start','done']+[str(i) for i in range(len(steps))]: reserve('q/'+q['id']+'/'+suffix)
        total_quests+=1+len(steps)
    if total_quests>64: raise ValueError('Journal: máximo nativo de 64 entradas contando quests y pasos')
    parsed=[]
    audio={kind:{r['id'] for r in resources['entries'] if r['path'].lower().startswith('sounds/'+('stereoambient' if kind=='ambient' else kind)+'/')} for kind in ['music','ambient']}
    templates={t['id']:t for t in resources['templates']}
    global_items={s['id']+'.'+o['id']:o for s in scenes.values() for o in s.get('objects',[]) if templates.get(o.get('template'),{}).get('kind') in {'items','weapons','armour'}}
    for si,s in enumerate(scenes.values()):
        label='Escena '+s['id']
        mapping(s,{'id','level','actors','objects','conversations','events','triggers','encounters','sequences','entries','default_entry','waypoints','paths','generators'}, {'id','level','actors','conversations','events'},label)
        dynamic=root.get('runtime_profile')=='phase10'
        if 'generators' in s and not dynamic:raise ValueError('Encuentros dinámicos requieren formato de proyecto 10')
        if any(k in s for k in ('entries','default_entry','waypoints','paths')) and not modern: raise ValueError('Entradas y recorridos requieren formato de proyecto 9')
        actors=indexed(s['actors'],label+' actors'); objects=indexed(s.get('objects',[]),label+' objects')
        from .dynamic_encounters import validate_generators,lower_phases,validate_dynamic_condition
        generators=validate_generators(s,resources['templates'],actors) if dynamic else {}
        if dynamic:lower_phases(s)
        entities={**actors,**objects}; convs=indexed(s['conversations'],label+' conversations')
        from .native_scripts import placement as native_placement
        native=native_placement(s,resources.get('native_scripts',{}))
        if native and not modern:raise ValueError('Script nativo requiere formato 9 o 10')
        if native:s['_native_entities']=sorted(native)
        from .camera_presets import PRESETS,CINEMA_PRESETS
        for conversation in convs.values():
            if 'staging' in conversation:
                stage=conversation['staging']
                if not modern or not isinstance(stage,(str,dict)) or isinstance(stage,str) and stage not in {p['id'] for p in s.get('entries',[])}:raise ValueError('Puesta en escena requiere una entrada existente')
            if 'camera' in conversation and (not modern or conversation['camera'] not in ('native','medium',*PRESETS)):
                raise ValueError('Cámara de conversación requiere formato 9 y preset conocido')
        from .native_arrivals import conversation_groups
        conversation_groups(s)
        if set(actors)&set(objects): raise ValueError(label+': IDs compartidos actor/objeto')
        groups=indexed(s.get('encounters',[]),label+' encounters'); shots=indexed(s.get('sequences',[]),label+' sequences')
        triggers=indexed(s.get('triggers',[]),label+' triggers')
        from .authoring9 import validate_markers
        paths=validate_markers(s,actors) if modern else {}
        def ref(value,ids,what):
            if not isinstance(value,str) or value not in ids: raise ValueError(label+': referencia '+what+' ausente: '+str(value))
        def item(value):
            ref(value,objects,'objeto')
            if templates.get(objects[value]['template'],{}).get('kind') not in {'items','weapons','armour'}: raise ValueError(label+': un prop no es un objeto de inventario')
        def global_item(value):
            if value in global_items:return
            item(value)
        for a in actors.values():
            from .wtd import validate_traits
            validate_traits(a,resources)
            if a.get('behavior','npc') not in {'npc','enemy'}: raise ValueError(label+': comportamiento debe ser npc o enemy')
            for it in sequence(a.get('inventory',[]),'inventory'): item(it)
        for o in objects.values():
            if 'interaction' in o:
                from .click_interactions import validate as validate_click
                if not modern or o['template']!='tracker_thing' or o['transform'].get('placement','absolute')!='absolute':raise ValueError('La superficie pulsable requiere tracker_thing y posición absoluta en formato 9/10')
                validate_click(o['interaction'])
                if 'source' in o['interaction']:
                    from .original_objects import validate as validate_original
                    validate_original(dict(o['interaction']['source'],operation='hide'),resources,s['level']['source'])
            if type(o.get('quest_item',False)) is not bool: raise ValueError('quest_item requiere booleano')
            if o.get('quest_item'): item(o['id'])
        for g in groups.values():
            mapping(g,{'id','name','actors'},{'id','name','actors'},'encounter'); text(g['name'],'encounter.name')
            members=sequence(g['actors'],'encounter.actors')
            if not members or len(set(members))!=len(members): raise ValueError('Encuentro vacío o duplicado')
            for a in members:
                ref(a,actors,'actor de encuentro')
                if actors[a].get('behavior')!='enemy': raise ValueError('Miembro de encuentro debe ser enemigo')
        for seq in shots.values():
            mapping(seq,{'id','name','actor','duration','shot','angle','preset','steps','move_path','camera_path','path_speed','move_at','prop_motion','reference','cues'},{'id','name','actor','duration','shot','angle'},'sequence')
            text(seq['name'],'sequence.name')
            if seq['actor']=='Player':
                if not modern or not any(k in seq for k in ('steps','camera_path','cues')):raise ValueError('Player requiere formato 9 y secuencia de planos')
            else:ref(seq['actor'],actors,'actor de cámara')
            if 'reference' in seq and seq['reference']!='Player':ref(seq['reference'],actors,'referencia de cámara')
            if type(seq['duration']) not in (float,int) or not math.isfinite(seq['duration']) or not .1<=seq['duration']<=120: raise ValueError('Duración de cámara 0.1..120 s')
            if seq['shot'] not in ('medium','close','wide') or seq['angle'] not in ('low','medium','high'): raise ValueError('Plano/ángulo de cámara inválido')
            if 'preset' in seq and (not modern or seq['preset'] not in CINEMA_PRESETS):raise ValueError('Preset de cámara requiere formato 9 y valor conocido')
            from .cinematics import validate_sequence
            validate_sequence(seq,actors,paths,resources,modern,objects)
        def condition(c,depth=0):
            if depth>12: raise ValueError('Condiciones demasiado anidadas')
            if not isinstance(c,dict): raise ValueError('Condición debe ser un objeto')
            if set(c) in ({'all'},{'any'}):
                key=next(iter(c)); children=sequence(c[key],key)
                if not children: raise ValueError('Grupo de condiciones vacío')
                for child in children: condition(child,depth+1)
            elif set(c)=={'not'}: condition(c['not'],depth+1)
            elif set(c)=={'flag','is_set'}:
                ref(c['flag'],flags,'flag')
                if type(c['is_set']) is not bool: raise ValueError('is_set requiere booleano')
            elif set(c)=={'quest','state'}:
                ref(c['quest'],quests,'quest')
                if c['state'] not in {'not_started','active','complete'}: raise ValueError('Estado de quest inválido')
            elif set(c)=={'quest','step'}:
                ref(c['quest'],quests,'quest')
                if type(c['step']) is not int or not 0<=c['step']<len(quests[c['quest']]['steps']): raise ValueError('Paso de quest fuera de rango')
            elif set(c) in ({'actor_alive'},{'entity_exists'},{'owns_item'}):
                k=next(iter(c))
                if k=='owns_item':global_item(c[k])
                else:ref(c[k],actors if k=='actor_alive' else entities,'entidad')
            elif dynamic and len(c)==1 and next(iter(c)) in {'actor_health','generator_state','generator_count'}:
                validate_dynamic_condition(c,actors,generators)
            else: raise ValueError('Condición desconocida: '+str(c))
        spawn_owners={}
        def action(a):
            if not isinstance(a,dict) or len(a)!=1: raise ValueError('Acción requiere una única operación')
            k,v=next(iter(a.items()))
            if k not in ACTIONS: raise ValueError('Acción no soportada: '+k)
            kind=ACTIONS[k][1]
            from .cinematics import validate_action
            if validate_action(k,v,s,actors,objects,resources,modern):return
            if k in {'push_music','pop_music'}:
                if not modern:raise ValueError('Música temporal requiere formato de proyecto 9 o 10')
                if k=='push_music':
                    mapping(v,{'resource','volume'},{'resource','volume'},'Música temporal')
                    matches=[r for r in resources['entries'] if r['id']==v['resource'] and r['path'].lower().startswith('sounds/music/') and r['extension'].lower()=='.mp3']
                    if len(matches)!=1:raise ValueError('Música temporal ausente o ambigua')
                    if type(v['volume']) is not int or not 0<=v['volume']<=100:raise ValueError('Volumen de música: 0..100')
                    return
            if kind in {'wtd_clan','wtd_discipline'}:
                if not modern:raise ValueError('Esta acción requiere formato de proyecto 9')
                field='clan' if kind=='wtd_clan' else 'discipline'
                mapping(v,{'actor',field,'level'} if field=='discipline' else {'actor',field},{'actor',field,'level'} if field=='discipline' else {'actor',field},k)
                if v['actor']!='Player':ref(v['actor'],actors,'actor')
                from .wtd import validate_traits
                validate_traits({'traits':{'clan':v['clan']} if field=='clan' else {'disciplines':{v['discipline']:v['level']}}},resources);return
            if kind=='generators':
                if not dynamic:raise ValueError('Encuentros dinámicos requieren formato de proyecto 10')
                ref(v,generators,'encuentro dinámico');return
            if k in {'show_note','travel','start_patrol','stop_patrol','open_exit','close_exit','control_door','control_original','play_sound'} and not modern: raise ValueError('Esta acción requiere formato de proyecto 9')
            if kind=='original':
                from .original_objects import validate
                validate(v,resources,s['level']['source']);return
            if kind=='note':
                from .notes import validate_note
                validate_note(v)
            elif kind=='arrival':
                mapping(v,{'scene','entry'},{'scene','entry'},'travel')
                ref(v['scene'],scenes,'escena de destino')
                if v['scene']==s['id']:raise ValueError(label+': Evento '+e['id']+': No se permite un enlace hacia la misma escena. Elige otra escena de destino.')
                ref(v['entry'],{r['id'] for r in scenes[v['scene']].get('entries',[])},'entrada de destino')
            elif kind=='native_exit':
                if not isinstance(v,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}',v):raise ValueError('Cast ID de salida inválido')
            elif kind=='door':
                mapping(v,{'cast_id','mode','frame','parameter','open'},{'cast_id','mode','frame','parameter','open'},'control_door')
                if not isinstance(v['cast_id'],str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}',v['cast_id']):raise ValueError('Cast ID de puerta inválido')
                if v['mode'] not in ('frames','pivot') or type(v['frame']) is not int or not 0<=v['frame']<=255 or type(v['open']) is not bool:raise ValueError('Modo/frame/estado de puerta inválido')
                if type(v['parameter']) not in (int,float) or not math.isfinite(v['parameter']) or not 0<v['parameter']<=1000:raise ValueError('Parámetro de movimiento de puerta: 0..1000')
            elif kind=='spatial_sound':
                mapping(v,{'resource','waypoint','volume','min_distance','max_distance','id','loop'},{'resource','waypoint','volume','min_distance','max_distance'},'play_sound')
                if 'loop' in v and type(v['loop']) is not bool:raise ValueError('Sonido en bucle requiere booleano')
                if v.get('loop'):
                    identifier(v.get('id'),'ID de sonido en bucle')
                elif 'id' in v:raise ValueError('Un sonido con ID requiere bucle')
                matches=[r for r in resources['entries'] if r['extension'].lower()=='.wav' and r['id']==v['resource']]
                if len(matches)!=1:raise ValueError('Sonido ausente o ambiguo')
                ref(v['waypoint'],{r['id'] for r in s.get('waypoints',[])},'waypoint de sonido')
                if type(v['volume']) is not int or not 0<=v['volume']<=100:raise ValueError('Volumen de sonido: 0..100')
                lo,hi=v['min_distance'],v['max_distance']
                if any(type(n) not in (int,float) or not math.isfinite(n) for n in (lo,hi)) or not 0<=lo<hi<=100000:raise ValueError('Radios de sonido inválidos')
            elif kind=='sound_source':
                from .audio import loops
                if not modern or v not in loops(s):raise ValueError('Sonido en bucle ausente')
            elif kind=='paths':ref(v,paths,'recorrido')
            elif kind=='number':
                if type(v) is not int or not 1<=v<=1000000: raise ValueError('Experiencia: entero 1..1000000')
            elif kind=='none':
                if v is not True: raise ValueError(k+': requiere true')
            elif kind=='item': item(v)
            elif kind=='item_global': global_item(v)
            elif k=='run_event':
                if not modern:raise ValueError('Ejecutar evento requiere formato 9/10')
                ref(v,events,'evento')
            else:
                ref(v,{'entity':entities,'actors':actors,'conversations':convs,'flags':flags,'quests':quests,'encounters':groups,'sequences':shots,'scenes':scenes,'music':audio['music'],'ambient':audio['ambient']}[kind],kind)
                if k=='jump' and v==s['id']:raise ValueError(label+': Evento '+e['id']+': No se permite un enlace hacia la misma escena. Elige otra escena de destino.')
            if k in {'spawn','spawn_encounter'}:
                for eid in [v] if k=='spawn' else groups[v]['actors']: spawn_owners[eid]=spawn_owners.get(eid,0)+1
        events=indexed(s['events'],label+' events')
        for e in events.values():
            mapping(e,{'id','when','actions','conditions','actor','object','conversation','result','trigger','item','encounter','sequence','seconds','once','generator','wave','phase'}, {'id','when','actions'},'event '+e['id'])
            w=e['when']
            if w not in WHEN: raise ValueError('Callback no soportado: '+str(w))
            if w in (*GENERATOR_EVENTS,'generator_threshold'):
                if not dynamic:raise ValueError('Callback dinámico requiere formato 10')
                ref(e.get('generator'),generators,'encuentro dinámico')
                if 'wave' in e and (w not in {'wave_started','wave_complete'} or type(e['wave']) is not int or not 1<=e['wave']<=len(generators[e['generator']]['waves'])):raise ValueError('Filtro de oleada inválido')
                if w=='generator_threshold' and e.get('phase') not in {p['id'] for p in generators[e['generator']].get('phases',[])}:raise ValueError('Fase ausente')
            elif any(k in e for k in ('generator','wave','phase')):raise ValueError('Filtro dinámico incompatible')
            if w in {'object_clicked','note_closed'} and not modern:raise ValueError('Notas y clic de objeto requieren formato de proyecto 9')
            if w=='sequence_ended':
                if not modern or e.get('sequence') not in shots:raise ValueError('Fin de secuencia requiere formato 9 y secuencia existente')
                if not any(k in shots[e['sequence']] for k in ('steps','move_path','camera_path','prop_motion','cues')):raise ValueError('Fin de secuencia requiere timeline o recorrido')
            if type(e.get('once',False)) is not bool: raise ValueError('event.once requiere booleano')
            filter_key={'object_clicked':'object','actor_clicked':'actor','actor_killed':'actor','conversation_ended':'conversation','trigger_enter':'trigger','trigger_leave':'trigger','item_picked_up':'item','encounter_complete':'encounter','sequence_ended':'sequence'}.get(w)
            for fk in ('actor','object','conversation','trigger','item','encounter','sequence','result','seconds'):
                if fk in e and fk != filter_key and not (fk=='result' and w=='conversation_ended') and not(fk=='seconds' and w=='timer'): raise ValueError('Filtro incompatible con '+w+': '+fk)
            if filter_key: ref(e.get(filter_key), {'object':objects,'actor':actors,'conversation':convs,'trigger':triggers,'item':objects,'encounter':groups,'sequence':shots}[filter_key],filter_key)
            if w=='item_picked_up': item(e['item'])
            if w=='timer' and (type(e.get('seconds')) not in (int,float) or not math.isfinite(e['seconds']) or not .15<=e['seconds']<=86400): raise ValueError('Timer requiere seconds 0.15..86400')
            if w=='state_changed' and not e.get('conditions'): raise ValueError('state_changed requiere condición')
            if 'result' in e:
                choices=convs[e['conversation']].get('choices',[]) + [c for n in convs[e['conversation']].get('nodes',[]) for c in n['choices']]
                if type(e['result']) is not int or e['result'] not in [c.get('result') for c in choices]: raise ValueError('RETURN de conversación no existe')
            for c in sequence(e.get('conditions',[]),'conditions'): condition(c)
            actions=sequence(e['actions'],'actions')
            if not actions: raise ValueError('Evento sin acciones')
            for a in actions: action(a)
            if any('show_note' in a for a in actions) and sum(any(k in a for k in ('show_note','start_conversation','play_sequence','travel','jump')) for a in actions)>1:raise ValueError('Una nota requiere su propio evento; continúa con Cuando cierran una nota')
            if sum('start_conversation' in a for a in actions)>1 or sum(('jump' in a or 'travel' in a) for a in actions)>1: raise ValueError('Evento inicia varias conversaciones o viajes')
            if any('jump' in a or 'travel' in a for a in actions) and not ('jump' in actions[-1] or 'travel' in actions[-1]): raise ValueError('El viaje debe ser la última acción')
            if e.get('once',w in {'actor_killed','item_picked_up','encounter_complete','timer','state_changed','generator_complete','generator_threshold'}) or (w=='trigger_enter' and triggers[e['trigger']].get('once',True)): reserve('e/'+s['id']+'/'+e['id'])
        from collections import Counter
        e={'id':'director'}
        for seq in shots.values():
            cues=sequence(seq.get('cues',[]),'cues');previous=-1
            if len(cues)>64:raise ValueError('Timeline: máximo 64 acciones de escena')
            if cues and not modern:raise ValueError('Acciones de escena requieren formato de proyecto 9 o 10')
            for cue in cues:
                mapping(cue,{'at','actions'},{'at','actions'},'Acción de escena')
                at=cue['at']
                if type(at) not in (int,float) or not math.isfinite(at) or not previous<=at<seq['duration'] or at<0:raise ValueError('Acciones de escena: tiempos ordenados dentro de la duración')
                previous=at
                if not isinstance(cue['actions'],list) or not 1<=len(cue['actions'])<=32:raise ValueError('Acción de escena: requiere 1..32 acciones')
                for a in cue['actions']:action(a)
        for conversation in convs.values():
            for node in conversation.get('nodes',[]):
                for line in node['lines']:
                    if 'actions' not in line:continue
                    if not modern or not isinstance(line['actions'],list) or not 1<=len(line['actions'])<=32:raise ValueError('Acciones de línea: requiere formato 9/10 y 1..32 acciones')
                    for a in line['actions']:
                        if any(k in a for k in ('start_conversation','play_sequence','show_note','jump','travel')):raise ValueError('La línea no puede abrir otra interfaz ni abandonar la conversación; usa conversación terminada')
                        action(a)
        # Reject recursive event chains before they can exhaust the old JVM's
        # stack. Runtime has a second guard for synchronous native callbacks.
        visiting=set();visited=set()
        def visit(eid):
            if eid in visiting:raise ValueError('Ciclo de llamadas entre eventos: '+eid)
            if eid in visited:return
            if len(visiting)>=32:raise ValueError('Demasiadas llamadas anidadas entre eventos (máximo 32)')
            visiting.add(eid)
            for a in events[eid]['actions']:
                if 'run_event' in a:visit(a['run_event'])
            visiting.remove(eid);visited.add(eid)
        for eid in events:visit(eid)
        from .cinematics import validate_calls
        validate_calls(s)
        inventory=Counter(it for a in actors.values() for it in a.get('inventory',[]))
        for eid in entities:
            n=spawn_owners.get(eid,0)+inventory[eid]
            if n>1: raise ValueError(label+': múltiples propietarios de creación de '+eid)
        # Use established parsers for transforms, templates, conversations and volumes.
        from .cinematics import conversation_source
        legacy={'schema':1,'chronicle':{**{k:v for k,v in chron.items() if k!='difficulty'},'id':chron['id']+'_s'+str(si)},'state':{'flags':flags},'level':s['level'],
                'actors':[{k:v for k,v in a.items() if k not in {'behavior','inventory','traits','native_script','native_frames'}} for a in actors.values()],
                'objects':[{k:v for k,v in a.items() if k not in {'quest_item','interaction','native_script','native_frames'}} for a in objects.values()],
                'conversations':[conversation_source(c) for c in s['conversations']],'triggers':s.get('triggers',[]),
                'events':[{'when':'scene_start','actions':[{'spawn':eid} for eid in entities]}] if entities else []}
        parsed.append((s,parse_project(yaml.safe_dump(legacy,sort_keys=False),levels,resources,allow_empty=True,allow_motions=modern)))
    if modern:
        for s in scenes.values():
            from .original_objects import targets,BITS
            for target in targets(s):
                for bit in BITS:reserve('original/'+s['id']+'/'+target+'/'+bit)
            for point in s.get('entries',[]): reserve('arrival/'+s['id']+'/'+point['id'])
            for e in s['events']:
                if 'e/'+s['id']+'/'+e['id'] in reserved:
                    reserve('progress/'+s['id']+'/'+e['id'])
                    for i,a in enumerate(e['actions']):reserve('action/'+s['id']+'/'+e['id']+'/'+str(i))
            if root.get('runtime_profile')=='phase10':
                for g in s.get('generators',[]):
                    reserve('generator/'+s['id']+'/'+g['id']+'/complete')
                    reserve('generator/'+s['id']+'/'+g['id']+'/started')
    return Campaign(root,tuple(parsed),reserved)

def integrity(campaign,resources=None):
    from .service import Problem
    findings=[]
    def actions(value):
        if isinstance(value,list):
            for child in value:yield from actions(child)
        elif isinstance(value,dict):
            if len(value)==1 and next(iter(value)) in ACTIONS:yield value
            else:
                for child in value.values():yield from actions(child)
    all_actions=[a for s,p in campaign.scenes for a in actions(s)]
    for si,(s,p) in enumerate(campaign.scenes):
        for i,row in enumerate(s.get('sequences',[])):
            if row.get('camera_path'):
                entry=next((e for e in (resources or {}).get('entries',[]) if e['extension']=='.ncp' and e['id']==row['camera_path']),None)
                if entry and entry.get('project_owned') and (entry.get('creation_scene')!=s['id'] or entry.get('creation_level')!=s['level']['source']):findings.append(Problem('WARNING','Travelling creado para otra escena o escenario; comprueba sus puntos de cámara',('scenes',si,'sequences',i)))
        for action in actions(s):
            if 'play_camera_path' in action:
                entry=next((e for e in (resources or {}).get('entries',[]) if e['extension']=='.ncp' and e['id']==action['play_camera_path']['resource']),None)
                if entry and entry.get('project_owned') and (entry.get('creation_scene')!=s['id'] or entry.get('creation_level')!=s['level']['source']):findings.append(Problem('WARNING','Travelling creado para otra escena o escenario; comprueba sus puntos de cámara',('scenes',si)))
        from .dynamic_encounters import integrity as dynamic_integrity
        for gi,message in dynamic_integrity(s):findings.append(Problem('WARNING',message,('scenes',si,'generators',gi)))
        local_actions=list(actions(s))
        spawned={a.get('spawn') for a in local_actions}
        spawned|={m for g in s.get('encounters',[]) for m in g['actors'] if any(a.get('spawn_encounter')==g['id'] for a in local_actions)}
        inventory={it for a in s['actors'] for it in a.get('inventory',[])}
        for k in ['actors','objects']:
            for i,e in enumerate(s.get(k,[])):
                if 'interaction' not in e and e['id'] not in spawned|inventory and not any(a.get('give_item')==e['id'] for a in local_actions): findings.append(Problem('WARNING',e['name']+': nunca se crea',('scenes',si,k,i)))
        for ei,e in enumerate(s['events']):
            if e['when']=='actor_clicked' and any(a.get('conversation') for a in s['actors'] if a['id']==e['actor']): findings.append(Problem('ERROR','Actor con vínculo directo y evento de clic; elige uno',('scenes',si,'events',ei)))
    for qi,q in enumerate(campaign.source.get('quests',[])):
        for k in ['start_quest','complete_quest']:
            if not any(a.get(k)==q['id'] for a in all_actions): findings.append(Problem('WARNING',q['title']+': falta acción '+k,('quests',qi)))
    from .campaign_relations import graph
    links=graph(campaign.source)
    for alias in campaign.source.get('state',{}).get('flags',{}):
        target=('state','flags',alias)
        if not any(x.target==target and x.label in {'flag','when_flag'} for x in links):findings.append(Problem('WARNING',alias+': el flag nunca se lee',target))
    for si,(s,p) in enumerate(campaign.scenes):
        from .dynamic_encounters import integrity as dynamic_integrity
        for gi,message in dynamic_integrity(s):findings.append(Problem('WARNING',message,('scenes',si,'generators',gi)))
        for key in ['conversations','triggers','encounters','sequences']:
            for i,row in enumerate(s.get(key,[])):
                if not any(x.target==('scenes',si,key,i) for x in links):findings.append(Problem('WARNING',row.get('name',row['id'])+': sin referencias',('scenes',si,key,i)))
    return findings
