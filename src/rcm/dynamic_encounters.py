"""Format-10 combat authoring, layered over existing events and native actors."""
import copy,hashlib,math
from .model import mapping,sequence,identifier,text

MODES={'ambush':'Emboscada','waves':'Oleadas','continuous':'Generador continuo','reinforcements':'Refuerzos','boss':'Jefe por fases'}
GENERATOR_ACTIONS=('start_generator','stop_generator','pause_generator','resume_generator','reset_generator')
GENERATOR_EVENTS=('generator_started','wave_started','wave_complete','generator_complete','generator_stopped')
COMPARISONS=('<','<=','>','>=','==')

def number(value,label,low,high,integer=False):
    if type(value) not in ((int,) if integer else (int,float)) or not math.isfinite(value) or not low<=value<=high:
        raise ValueError(label+f': {low}..{high}')
    return value

def phase_event(generator,phase):
    return 'dp_'+hashlib.sha256((generator+'/'+phase).encode()).hexdigest()[:12]


def unique_health_role(generator,role):
    count=sum(e['count'] for wave in generator['waves'] for e in wave['groups'] if e['role']==role)
    return count==1 and (generator['mode']!='continuous' or (generator.get('target_alive') or generator['max_alive'])==1)

def validate_generators(scene,templates,actors):
    rows=sequence(scene.get('generators',[]),'generators')
    if len(rows)>32:raise ValueError('Máximo 32 encuentros dinámicos por escena')
    waypoints={p['id'] for p in scene.get('waypoints',[])};objects={p['id'] for p in scene.get('objects',[])}
    result={};slots=0
    for g in rows:
        mapping(g,{'id','name','mode','spawn_points','placement','point_selection','selection','waves','interval','max_alive','max_total','target_alive','persistence','cooldown','retry_limit','remove_on_stop','visual','boss','phases'}, {'id','name','mode','waves','max_alive'},'Encuentro dinámico')
        key=identifier(g['id'],'generators.id',16);text(g['name'],'generators.name')
        if key in result:raise ValueError('Encuentro dinámico duplicado: '+key)
        if g['mode'] not in MODES:raise ValueError('Tipo de encuentro dinámico desconocido')
        points=sequence(g.get('spawn_points',[]),'spawn_points')
        if g.get('placement','points') not in {'points','near_player'}:raise ValueError('Aparición: puntos o cerca del jugador')
        if g.get('placement','points')=='points' and (not points or len(points)>32 or any(p not in waypoints for p in points)):
            raise ValueError('Selecciona 1..32 puntos de aparición existentes')
        if len(set(points))!=len(points):raise ValueError('Punto de aparición duplicado')
        if g.get('point_selection','round_robin') not in {'sequential','round_robin','random'}:raise ValueError('Distribución de puntos desconocida')
        if g.get('selection','round_robin') not in {'round_robin','random'}:raise ValueError('Selección de enemigos desconocida')
        slots+=number(g['max_alive'],'Máximo vivos',1,64,True)
        number(g.get('max_total',0),'Máximo total',0,1000000,True)
        number(g.get('interval',5),'Intervalo',.3,86400)
        number(g.get('target_alive',0),'Objetivo de vivos',0,g['max_alive'],True)
        number(g.get('retry_limit',3),'Intentos de aparición',1,8,True)
        if g.get('persistence','once') not in {'once','resume','reset','cooldown'}:raise ValueError('Persistencia desconocida')
        if g.get('persistence')=='cooldown':number(g.get('cooldown',30),'Tiempo de repetición',.3,86400)
        if type(g.get('remove_on_stop',False)) is not bool:raise ValueError('Retirar al detener requiere booleano')
        if g.get('visual') and g['visual'] not in objects:raise ValueError('Representación visual ausente')
        waves=sequence(g['waves'],'waves')
        if not 1<=len(waves)<=32:raise ValueError('Encuentro requiere 1..32 oleadas')
        if g['mode']!='waves' and len(waves)!=1:raise ValueError('Sólo Oleadas admite varios grupos sucesivos')
        roles={};groups=0
        for wave in waves:
            mapping(wave,{'groups','delay'},{'groups'},'Oleada')
            number(wave.get('delay',0),'Retardo de oleada',0,86400)
            enemies=sequence(wave['groups'],'Enemigos')
            if not (0 if g['mode']=='boss' and 'actor' in g.get('boss',{}) else 1)<=len(enemies)<=32:raise ValueError('Oleada requiere 1..32 tipos de enemigo')
            for group in enemies:
                mapping(group,{'role','template','count','weight','spawn_points','health_multiplier','health','team'},{'role','template','count'},'Enemigo')
                role=identifier(group['role'],'Rol de enemigo',16)
                roles[role]=roles.get(role,0)+number(group['count'],'Cantidad de enemigos',1,128,True)
                candidates=[t for t in templates if t['id']==group['template'] and t['kind']=='actors']
                if len(candidates)!=1:raise ValueError('Plantilla de enemigo ausente o ambigua: '+str(group['template']))
                number(group.get('weight',1),'Peso de selección',1,1000,True)
                extra=sequence(group.get('spawn_points',[]),'Puntos del enemigo')
                if any(p not in waypoints for p in extra) or len(extra)>32:raise ValueError('Punto de aparición del enemigo ausente')
                if g.get('placement','points')=='near_player' and extra:raise ValueError('Cerca del jugador no admite puntos del enemigo')
                if 'health' in group and 'health_multiplier' in group:raise ValueError('Elige vida personalizada o multiplicador')
                if 'health' in group:number(group['health'],'Vida personalizada',1,1000000)
                if 'health_multiplier' in group:number(group['health_multiplier'],'Multiplicador de vida',.1,10)
                if 'team' in group:number(group['team'],'Equipo nativo',0,19,True)
                groups+=1
        if groups>256:raise ValueError('Máximo 256 grupos por encuentro')
        phases=sequence(g.get('phases',[]),'Fases del jefe')
        if g['mode']=='boss' and not phases:raise ValueError('El jefe necesita al menos una fase')
        if phases and g['mode']!='boss':raise ValueError('Las fases necesitan el tipo Jefe por fases')
        boss=g.get('boss',{})
        if phases:
            if len(phases)>16:raise ValueError('Máximo 16 fases por jefe')
            if set(boss)=={'actor'}:
                if boss['actor'] not in actors:raise ValueError('Actor del jefe ausente')
            elif set(boss)=={'role'}:
                if roles.get(boss['role'])!=1:raise ValueError('El rol del jefe debe generar exactamente un actor')
            else:raise ValueError('Selecciona un actor o rol único como jefe')
            ids=set();thresholds=set()
            for phase in phases:
                mapping(phase,{'id','percent','value','actions','once'},{'id','actions'},'Fase')
                pid=identifier(phase['id'],'Fase.id',16)
                if pid in ids:raise ValueError('Fase duplicada')
                ids.add(pid)
                fields=set(phase)&{'percent','value'}
                if len(fields)!=1:raise ValueError('Fase: porcentaje o vida absoluta')
                field=next(iter(fields));threshold=number(phase[field],'Umbral de vida',.1,99.9 if field=='percent' else 1000000)
                if (field,threshold) in thresholds:raise ValueError('Umbral de jefe duplicado')
                thresholds.add((field,threshold))
                if type(phase.get('once',True)) is not bool:raise ValueError('Fase.once requiere booleano')
                if not sequence(phase['actions'],'Acciones de fase'):raise ValueError('Fase sin acciones')
        result[key]=g
    if slots>256:raise ValueError('Máximo 256 actores dinámicos simultáneos por escena')
    return result

def lower_phases(scene):
    """Compile phase actions through the existing event/checkpoint machinery."""
    ids={e['id'] for e in scene['events']}
    for g in scene.get('generators',[]):
        for phase in g.get('phases',[]):
            key=phase_event(g['id'],phase['id'])
            if key in ids:raise ValueError('ID de evento reservado para una fase: '+key)
            ids.add(key)
            scene['events'].append({'id':key,'when':'generator_threshold','generator':g['id'],'phase':phase['id'],'once':phase.get('once',True),'actions':copy.deepcopy(phase['actions'])})

def validate_dynamic_condition(c,actors,generators):
    key=next(iter(c));value=c[key]
    if key=='actor_health':
        mapping(value,{'actor','generator','role','comparison','percent','value'},{'comparison'},'Vida del actor')
        if 'actor' in value:
            if set(value)&{'generator','role'} or value['actor'] not in actors:raise ValueError('Actor de vida ausente o ambiguo')
        else:
            g=generators.get(value.get('generator'));role=value.get('role')
            if not g or not unique_health_role(g,role):raise ValueError('Vida necesita un rol dinámico único')
        fields=set(value)&{'percent','value'}
        if len(fields)!=1:raise ValueError('Vida: porcentaje o valor absoluto')
        field=next(iter(fields));number(value[field],'Vida',0,100 if field=='percent' else 1000000)
        if value['comparison'] not in COMPARISONS[:4]:raise ValueError('Comparación de vida inválida')
    elif key=='generator_state':
        mapping(value,{'generator','state'},{'generator','state'},'Estado del encuentro')
        if value['generator'] not in generators or value['state'] not in {'ready','active','paused','complete','stopped','error'}:raise ValueError('Estado de encuentro inválido')
    elif key=='generator_count':
        mapping(value,{'generator','role','counter','comparison','value'},{'generator','counter','comparison','value'},'Contador del encuentro')
        g=generators.get(value['generator'])
        if not g or value['counter'] not in {'alive','killed','total','wave'} or value['comparison'] not in COMPARISONS:raise ValueError('Contador de encuentro inválido')
        if 'role' in value and (value['counter']=='wave' or value['role'] not in {e['role'] for w in g['waves'] for e in w['groups']}):raise ValueError('Rol del contador ausente')
        number(value['value'],'Contador',0,1000000,True)
    else:raise ValueError('Condición dinámica desconocida')

def integrity(scene):
    warnings=[]
    starts={a['start_generator'] for e in scene['events'] for a in e['actions'] if 'start_generator' in a}
    starts|={a['start_generator'] for g in scene.get('generators',[]) for phase in g.get('phases',[]) for a in phase['actions'] if 'start_generator' in a}
    for i,g in enumerate(scene.get('generators',[])):
        if g['id'] not in starts:warnings.append((i,'Encuentro dinámico sin vía de activación: '+g['name']))
        if g['max_alive']>32:warnings.append((i,'Más de 32 enemigos simultáneos: comprueba rendimiento en Redemption.'))
        if g['mode']=='continuous' and not g.get('max_total') and not any(a.get('stop_generator')==g['id'] for e in scene['events'] for a in e['actions']):
            warnings.append((i,'Generador continuo sin límite total ni evento para detenerlo.'))
    return warnings
