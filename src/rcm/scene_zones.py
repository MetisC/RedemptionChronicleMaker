"""Activation zones reuse existing volumes, owned sound handles and light actions."""
import hashlib


def sound_id(trigger):return 'zone_'+hashlib.sha256(trigger['id'].encode()).hexdigest()[:12]


def validate(scene,actors,objects,resources,flags=None):
    from .model import mapping
    from .cinematics import number,validate_action
    light_owners=set()
    for trigger in scene.get('triggers',[]):
        if 'zone_flag' in trigger:
            gate=trigger['zone_flag'];mapping(gate,{'flag','is_set'},{'flag','is_set'},'Zone flag')
            if not any(key in trigger for key in ('sound_zone','light_zone')):raise ValueError('Zone flag requires a sound or light zone')
            if not isinstance(gate['flag'],str) or gate['flag'] not in (flags or {}) or type(gate['is_set']) is not bool:raise ValueError('Zone flag requires an existing flag and boolean state')
        if trigger.get('native_script') and any(key in trigger for key in ('sound_zone','light_zone')):raise ValueError('Choose native region ownership or an RCM sound/light zone')
        if 'sound_zone' in trigger:
            sound=trigger['sound_zone'];mapping(sound,{'resource','volume','min_distance','max_distance'},{'resource','volume','min_distance','max_distance'},'Sound zone')
            if len([e for e in resources['entries'] if e['id']==sound['resource'] and e['extension'].lower()=='.wav'])!=1:raise ValueError('Sound zone: unknown or ambiguous WAV')
            if type(sound['volume']) is not int or not 0<=sound['volume']<=100:raise ValueError('Sound zone volume: 0..100')
            for key in ('min_distance','max_distance'):number(sound[key],0,100000,'Sound zone distance')
            if sound['max_distance']<=sound['min_distance']:raise ValueError('Sound zone: maximum distance must exceed minimum')
        if 'light_zone' in trigger:
            light=trigger['light_zone'];validate_action('set_dynamic_light',light,scene,actors,objects,resources,True)
            if light['entity'] in light_owners:raise ValueError('A light can belong to only one activation zone')
            light_owners.add(light['entity'])


def lights(scene):
    return [(i,t['light_zone']) for i,t in enumerate(scene.get('triggers',[])) if 'light_zone' in t]


def guard(scene,index,flags):
    """Use ordinary saved chronicle flags; no second state/save manager."""
    gate=scene['triggers'][index].get('zone_flag')
    if gate is None:return f'volume({index})'
    return f'(volume({index}) && '+('' if gate['is_set'] else '!')+f'CodexSequence.GetChronicleFlag({flags[gate["flag"]]}))'
