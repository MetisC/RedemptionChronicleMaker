"""Schema 2 campaigns. Legacy scene codecs remain shared and unchanged."""
from dataclasses import dataclass
import copy, math, re
import yaml
from .model import mapping, sequence, identifier, text, parse_project, UniqueLoader

# One shared library for authoring, validation and Java generation.
ACTIONS = {
 'spawn': ('Mundo / Crear entidad','entity'), 'remove': ('Mundo / Retirar entidad','entity'),
 'start_conversation': ('Historia / Conversación','conversations'),
 'set_flag': ('Estado / Activar flag','flags'), 'clear_flag': ('Estado / Desactivar flag','flags'),
 'start_quest': ('Quest / Iniciar','quests'), 'advance_quest': ('Quest / Siguiente paso','quests'),
 'complete_quest': ('Quest / Completar','quests'),
 'give_item': ('Inventario / Dar objeto al jugador','item'), 'take_item': ('Inventario / Quitar objeto del jugador','item_global'),
 'reward_xp': ('Recompensa / Experiencia del jugador','number'),
 'spawn_encounter': ('Encuentro / Crear grupo','encounters'), 'remove_encounter': ('Encuentro / Retirar grupo','encounters'),
 'jump': ('Viaje / Cambiar ubicación','scenes'),
 'start_music': ('Audio / Música','music'), 'stop_music': ('Audio / Detener música','none'),
 'start_ambient': ('Audio / Ambiente','ambient'), 'stop_ambient': ('Audio / Detener ambiente','none'),
 'play_sequence': ('Cámara / Secuencia','sequences'), 'release_camera': ('Cámara / Devolver control','none'),
 'enable_ai': ('AI / Activar','actors'), 'disable_ai': ('AI / Pausar','actors'),
 'travel': ('Viaje / Escena y punto de llegada','arrival'),
 'start_patrol': ('Movimiento / Seguir recorrido','paths'), 'stop_patrol': ('Movimiento / Detener actor','actors'),
 'open_exit': ('Salida original / Abrir','native_exit'), 'close_exit': ('Salida original / Cerrar','native_exit'),
 'control_door': ('Puerta existente / Movimiento','door'),
 'play_sound': ('Audio / Sonido situado','spatial_sound'),
}
WHEN = {'scene_start':'Inicia la escena','actor_clicked':'Hablan con actor','conversation_ended':'Termina conversación',
 'trigger_enter':'Entra en trigger','trigger_leave':'Sale de trigger','actor_killed':'Actor muerto (muestreo)',
 'item_picked_up':'Objeto en inventario (muestreo)','encounter_complete':'Todos los enemigos muertos',
 'timer':'Tiempo desde entrada','state_changed':'Se cumple una condición'}

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
    modern=root.get('runtime_profile')=='phase9'
    if 'runtime_profile' in root and not modern: raise ValueError('Perfil de runtime desconocido')
    if type(root['schema']) is not int or root['schema']!=2: raise ValueError('schema de campaña debe ser 2')
    chron=mapping(root['chronicle'],{'id','name','description'},{'id','name'},'chronicle')
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
            key=identifier(row.get('id'),label+'.id',16)
            if key in result: raise ValueError(label+': ID duplicado '+key)
            result[key]=row
        return result
    scenes=indexed(root['scenes'],'scenes'); quests=indexed(root.get('quests',[]),'quests')
    if not 1<=len(scenes)<=32 or root['entry'] not in scenes: raise ValueError('Entrada ausente o número de escenas fuera de 1..32')
    reserved={}
    def reserve(key):
        reserved[key]=256+len(reserved)
        if reserved[key]>=1024: raise ValueError('Se exceden los 1024 Chronicle Flags nativos')
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
        mapping(s,{'id','level','actors','objects','conversations','events','triggers','encounters','sequences','entries','default_entry','waypoints','paths'}, {'id','level','actors','conversations','events'},label)
        if any(k in s for k in ('entries','default_entry','waypoints','paths')) and not modern: raise ValueError('Entradas y recorridos requieren formato de proyecto 9')
        actors=indexed(s['actors'],label+' actors'); objects=indexed(s.get('objects',[]),label+' objects')
        entities={**actors,**objects}; convs=indexed(s['conversations'],label+' conversations')
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
            if a.get('behavior','npc') not in {'npc','enemy'}: raise ValueError(label+': comportamiento debe ser npc o enemy')
            for it in sequence(a.get('inventory',[]),'inventory'): item(it)
        for o in objects.values():
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
            mapping(seq,{'id','name','actor','duration','shot','angle','preset'},{'id','name','actor','duration','shot','angle'},'sequence')
            text(seq['name'],'sequence.name');ref(seq['actor'],actors,'actor de cámara')
            if type(seq['duration']) not in (float,int) or not math.isfinite(seq['duration']) or not .1<=seq['duration']<=120: raise ValueError('Duración de cámara 0.1..120 s')
            if seq['shot'] not in ('medium','close','wide') or seq['angle'] not in ('low','medium','high'): raise ValueError('Plano/ángulo de cámara inválido')
            if 'preset' in seq and (not modern or seq['preset'] not in {'speaker_close','listener_close','ots_speaker','ots_listener','two_shot','medium','full'}):raise ValueError('Preset de cámara requiere formato 9 y valor conocido')
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
            else: raise ValueError('Condición desconocida: '+str(c))
        spawn_owners={}
        def action(a):
            if not isinstance(a,dict) or len(a)!=1: raise ValueError('Acción requiere una única operación')
            k,v=next(iter(a.items()))
            if k not in ACTIONS: raise ValueError('Acción no soportada: '+k)
            kind=ACTIONS[k][1]
            if k in {'travel','start_patrol','stop_patrol','open_exit','close_exit','control_door','play_sound'} and not modern: raise ValueError('Esta acción requiere formato de proyecto 9')
            if kind=='arrival':
                mapping(v,{'scene','entry'},{'scene','entry'},'travel')
                ref(v['scene'],scenes,'escena de destino')
                ref(v['entry'],{r['id'] for r in scenes[v['scene']].get('entries',[])},'entrada de destino')
            elif kind=='native_exit':
                if not isinstance(v,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}',v):raise ValueError('Cast ID de salida inválido')
            elif kind=='door':
                mapping(v,{'cast_id','mode','frame','parameter','open'},{'cast_id','mode','frame','parameter','open'},'control_door')
                if not isinstance(v['cast_id'],str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,62}',v['cast_id']):raise ValueError('Cast ID de puerta inválido')
                if v['mode'] not in ('frames','pivot') or type(v['frame']) is not int or not 0<=v['frame']<=255 or type(v['open']) is not bool:raise ValueError('Modo/frame/estado de puerta inválido')
                if type(v['parameter']) not in (int,float) or not math.isfinite(v['parameter']) or not 0<v['parameter']<=1000:raise ValueError('Parámetro de movimiento de puerta: 0..1000')
            elif kind=='spatial_sound':
                mapping(v,{'resource','waypoint','volume','min_distance','max_distance'},{'resource','waypoint','volume','min_distance','max_distance'},'play_sound')
                matches=[r for r in resources['entries'] if r['extension'].lower()=='.wav' and r['id']==v['resource']]
                if len(matches)!=1:raise ValueError('Sonido ausente o ambiguo')
                ref(v['waypoint'],{r['id'] for r in s.get('waypoints',[])},'waypoint de sonido')
                if type(v['volume']) is not int or not 0<=v['volume']<=100:raise ValueError('Volumen de sonido: 0..100')
                lo,hi=v['min_distance'],v['max_distance']
                if any(type(n) not in (int,float) or not math.isfinite(n) for n in (lo,hi)) or not 0<=lo<hi<=100000:raise ValueError('Radios de sonido inválidos')
            elif kind=='paths':ref(v,paths,'recorrido')
            elif kind=='number':
                if type(v) is not int or not 1<=v<=1000000: raise ValueError('Experiencia: entero 1..1000000')
            elif kind=='none':
                if v is not True: raise ValueError(k+': requiere true')
            elif kind=='item': item(v)
            elif kind=='item_global': global_item(v)
            else: ref(v,{'entity':entities,'actors':actors,'conversations':convs,'flags':flags,'quests':quests,'encounters':groups,'sequences':shots,'scenes':scenes,'music':audio['music'],'ambient':audio['ambient']}[kind],kind)
            if k in {'spawn','spawn_encounter'}:
                for eid in [v] if k=='spawn' else groups[v]['actors']: spawn_owners[eid]=spawn_owners.get(eid,0)+1
        events=indexed(s['events'],label+' events')
        for e in events.values():
            mapping(e,{'id','when','actions','conditions','actor','conversation','result','trigger','item','encounter','seconds','once'}, {'id','when','actions'},'event '+e['id'])
            w=e['when']
            if w not in WHEN: raise ValueError('Callback no soportado: '+str(w))
            if type(e.get('once',False)) is not bool: raise ValueError('event.once requiere booleano')
            filter_key={'actor_clicked':'actor','actor_killed':'actor','conversation_ended':'conversation','trigger_enter':'trigger','trigger_leave':'trigger','item_picked_up':'item','encounter_complete':'encounter'}.get(w)
            for fk in ('actor','conversation','trigger','item','encounter','result','seconds'):
                if fk in e and fk != filter_key and not (fk=='result' and w=='conversation_ended') and not(fk=='seconds' and w=='timer'): raise ValueError('Filtro incompatible con '+w+': '+fk)
            if filter_key: ref(e.get(filter_key), {'actor':actors,'conversation':convs,'trigger':triggers,'item':objects,'encounter':groups}[filter_key],filter_key)
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
            if sum('start_conversation' in a for a in actions)>1 or sum(('jump' in a or 'travel' in a) for a in actions)>1: raise ValueError('Evento inicia varias conversaciones o viajes')
            if any('jump' in a or 'travel' in a for a in actions) and not ('jump' in actions[-1] or 'travel' in actions[-1]): raise ValueError('El viaje debe ser la última acción')
            if e.get('once',w in {'actor_killed','item_picked_up','encounter_complete','timer','state_changed'}) or (w=='trigger_enter' and triggers[e['trigger']].get('once',True)): reserve('e/'+s['id']+'/'+e['id'])
        from collections import Counter
        inventory=Counter(it for a in actors.values() for it in a.get('inventory',[]))
        for eid in entities:
            n=spawn_owners.get(eid,0)+inventory[eid]
            if n>1: raise ValueError(label+': múltiples propietarios de creación de '+eid)
        # Use established parsers for transforms, templates, conversations and volumes.
        legacy={'schema':1,'chronicle':{**chron,'id':chron['id']+'_s'+str(si)},'state':{'flags':flags},'level':s['level'],
                'actors':[{k:v for k,v in a.items() if k not in {'behavior','inventory'}} for a in actors.values()],
                'objects':[{k:v for k,v in a.items() if k!='quest_item'} for a in objects.values()],
                'conversations':s['conversations'],'triggers':s.get('triggers',[]),
                'events':[{'when':'scene_start','actions':[{'spawn':eid} for eid in entities]}] if entities else []}
        parsed.append((s,parse_project(yaml.safe_dump(legacy,sort_keys=False),levels,resources,allow_empty=True)))
    if modern:
        for s in scenes.values():
            for point in s.get('entries',[]): reserve('arrival/'+s['id']+'/'+point['id'])
            for e in s['events']:
                if 'e/'+s['id']+'/'+e['id'] in reserved:
                    reserve('progress/'+s['id']+'/'+e['id'])
                    for i,a in enumerate(e['actions']):reserve('action/'+s['id']+'/'+e['id']+'/'+str(i))
    return Campaign(root,tuple(parsed),reserved)

def integrity(campaign):
    from .service import Problem
    findings=[]
    all_actions=[a for s,p in campaign.scenes for e in s['events'] for a in e['actions']]
    for si,(s,p) in enumerate(campaign.scenes):
        local_actions=[a for e in s['events'] for a in e['actions']]
        spawned={a.get('spawn') for a in local_actions}
        spawned|={m for g in s.get('encounters',[]) for m in g['actors'] if any(a.get('spawn_encounter')==g['id'] for a in local_actions)}
        inventory={it for a in s['actors'] for it in a.get('inventory',[])}
        for k in ['actors','objects']:
            for i,e in enumerate(s.get(k,[])):
                if e['id'] not in spawned|inventory and not any(a.get('give_item')==e['id'] for a in local_actions): findings.append(Problem('WARNING',e['name']+': nunca se crea',('scenes',si,k,i)))
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
        for key in ['conversations','triggers','encounters','sequences']:
            for i,row in enumerate(s.get(key,[])):
                if not any(x.target==('scenes',si,key,i) for x in links):findings.append(Problem('WARNING',row.get('name',row['id'])+': sin referencias',('scenes',si,key,i)))
    return findings
