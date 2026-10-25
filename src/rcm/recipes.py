"""Reusable authoring recipes. References only; the normal source remains truth."""
import copy
import math
from .model import identifier, mapping, sequence

TYPES = ('talk', 'go_to_place', 'trigger_actions', 'trigger_cinematic', 'pickup',
         'quest', 'encounter', 'travel', 'note', 'object_conversation')
COLLECTIONS = {'actors', 'objects', 'conversations', 'events', 'triggers',
               'sequences', 'encounters', 'entries', 'quests', 'flags'}


def validate_authoring(root):
    authoring = mapping(root.get('authoring', {}), {'recipes', 'prefabs'}, label='authoring')
    seen = set()
    for recipe in sequence(authoring.get('recipes', []), 'authoring.recipes'):
        mapping(recipe, {'id', 'type', 'version', 'scene', 'refs'},
                {'id', 'type', 'version', 'scene', 'refs'}, 'recipe')
        ident = identifier(recipe['id'], 'recipe.id', 16)
        if ident in seen or recipe['type'] not in TYPES or type(recipe['version']) is not int or recipe['version'] != 1:
            raise ValueError('Invalid or duplicate authoring recipe')
        seen.add(ident)
        identifier(recipe['scene'], 'recipe.scene', 16)
        refs = mapping(recipe['refs'], set(recipe['refs']), label='recipe.refs')
        for role, ref in refs.items():
            identifier(role, 'recipe role', 24)
            mapping(ref, {'scene', 'collection', 'id'}, {'collection', 'id'}, 'recipe reference')
            if ref['collection'] not in COLLECTIONS:raise ValueError('Invalid recipe collection')
            identifier(ref['id'], 'recipe reference', 24)
            if ref['collection'] not in {'quests', 'flags'}:
                identifier(ref.get('scene'), 'recipe reference scene', 16)
    prefab_ids = set()
    for prefab in sequence(authoring.get('prefabs', []), 'authoring.prefabs'):
        mapping(prefab, {'id', 'name', 'items'}, {'id', 'name', 'items'}, 'prefab')
        ident = identifier(prefab['id'], 'prefab.id', 16)
        if ident in prefab_ids or not isinstance(prefab['name'], str):
            raise ValueError('Invalid or duplicate authoring prefab')
        prefab_ids.add(ident)
        items = sequence(prefab['items'], 'prefab.items')
        if not 1 <= len(items) <= 64:
            raise ValueError('Prefab requires 1..64 items')
        for item in items:
            mapping(item, {'name', 'template', 'geometry', 'offset', 'orientation'},
                    {'name', 'offset'}, 'prefab item')
            if not isinstance(item['name'], str):
                raise ValueError('Prefab item requires a name')
            if ('template' in item) == ('geometry' in item):
                raise ValueError('Prefab item requires exactly one of template or geometry')
            if 'template' in item and not isinstance(item['template'], str):
                raise ValueError('Prefab item template requires text')
            if 'geometry' in item:
                from .scenery import validate_geometry
                validate_geometry(item['geometry'])
            for key in ('offset', 'orientation'):
                vector = item.get(key, [0, 0, 0])
                if not isinstance(vector, list) or len(vector) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector):
                    raise ValueError('Prefab item requires 3 finite numbers in ' + key)


def recipes(root):
    return root.get('authoring', {}).get('recipes', [])


def resolve(root, ref):
    kind, ident = ref['collection'], ref['id']
    if kind == 'flags':
        return root.get('state', {}).get('flags', {}).get(ident)
    if kind == 'quests':rows = root.get('quests', [])
    else:
        scene = next((s for s in root['scenes'] if s['id'] == ref.get('scene')), None)
        rows = scene.get(kind, []) if scene else []
    return next((row for row in rows if row['id'] == ident), None)


def missing(root, recipe):
    absent = [role for role, ref in recipe['refs'].items() if resolve(root, ref) is None]
    if not any(s['id'] == recipe['scene'] for s in root['scenes']):absent.insert(0, 'scene')
    return absent


def rename_references(root, collection, old, new, scene=None):
    for recipe in recipes(root):
        if collection == 'scenes':
            if recipe['scene'] == old:recipe['scene'] = new
            for ref in recipe['refs'].values():
                if ref.get('scene') == old:ref['scene'] = new
        else:
            for ref in recipe['refs'].values():
                if ref['collection'] == collection and ref['id'] == old and (scene is None or ref.get('scene') == scene):
                    ref['id'] = new


def unlink(root, ident):
    result = copy.deepcopy(root)
    result['authoring']['recipes'] = [r for r in recipes(result) if r['id'] != ident]
    return result


def rebind(root, ident, role, ref):
    result = copy.deepcopy(root)
    recipe = next(r for r in recipes(result) if r['id'] == ident)
    if role not in recipe['refs'] or ref['collection'] != recipe['refs'][role]['collection'] or resolve(result, ref) is None:
        raise ValueError('Choose an existing resource of the same kind')
    old=recipe['refs'][role]
    if role=='actor' and recipe['type'] in {'talk','go_to_place'}:
        existing=resolve(result,ref).get('conversation',{}).get('default')
        conversation=recipe['refs'].get('conversation',{}).get('id')
        if existing and existing!=conversation:
            raise ValueError('El actor elegido ya tiene otra conversación predeterminada.')
    if old['collection'] not in {'quests','flags','entries'} and ref.get('scene')!=old.get('scene'):
        raise ValueError('Choose a resource in the same scene')
    def path(reference):
        if reference['collection']=='flags':return ('state','flags',reference['id']) if reference['id'] in result.get('state',{}).get('flags',{}) else None
        rows=result.get('quests',[]) if reference['collection']=='quests' else next((s for s in result['scenes'] if s['id']==reference.get('scene')),{}).get(reference['collection'],[])
        index=next((i for i,r in enumerate(rows) if r['id']==reference['id']),None)
        if index is None:return None
        if reference['collection']=='quests':return ('quests',index)
        si=next(i for i,s in enumerate(result['scenes']) if s['id']==reference['scene'])
        return ('scenes',si,reference['collection'],index)
    old_path=path(old);owned={path(r) for r in recipe['refs'].values()}
    if old_path:
        from .campaign_relations import graph
        for link in graph(result):
            if link.label=='authoring recipe' or link.target!=old_path or link.source not in owned:continue
            node=result
            for key in link.detail[:-1]:node=node[key]
            key=link.detail[-1];value=node[key]
            if isinstance(value,str) and value==old['id']:node[key]=ref['id']
            elif isinstance(value,list):node[key]=[ref['id'] if item==old['id'] else item for item in value]
            elif link.label=='travel' and isinstance(value,dict):value.update(scene=ref['scene'],entry=ref['id'])
    else:
        from .document import Document
        keys={'actors':{'speaker','actor','reference','spawn','remove','actor_alive','entity_exists','enable_ai','disable_ai','stop_patrol'},'objects':{'spawn','remove','object','focus','item','give_item','take_item','owns_item','entity_exists'},'flags':{'flag','when_flag','set_flag','clear_flag'},'quests':{'quest','start_quest','advance_quest','complete_quest'},'conversations':{'conversation','start_conversation','default','then'},'sequences':{'sequence','play_sequence'},'triggers':{'trigger'},'encounters':{'encounter','spawn_encounter','remove_encounter'},'entries':{'default_entry'},'events':set()}[old['collection']]
        for reference in recipe['refs'].values():
            row=resolve(result,reference)
            if isinstance(row,dict):Document._replace(row,keys,old['id'],ref['id'])
    if role=='actor' and recipe['type'] in {'talk','go_to_place'}:
        # Moving a conversation's speaker also transfers its default binding.
        # Keep the previous actor and all unrelated bindings intact.
        conv_ref=recipe['refs'].get('conversation')
        old_actor=resolve(result,old);new_actor=resolve(result,ref)
        if conv_ref:
            bindings=old_actor.get('conversation',{}) if old_actor else {}
            for key,value in list(bindings.items()):
                if value==conv_ref['id']:bindings.pop(key)
            if old_actor is not None and not bindings:old_actor.pop('conversation',None)
            new_actor.setdefault('conversation',{})['default']=conv_ref['id']
    recipe['refs'][role] = copy.deepcopy(ref)
    return result


def unique(rows, stem):
    ids = {row['id'] for row in rows}
    for number in range(1, 10000):
        ident = stem[:11] + str(number)
        if ident not in ids:return ident
    raise ValueError('No available recipe identifier')


def values(root, recipe):
    """Read current entities, including edits made outside this wizard."""
    get = lambda role: resolve(root, recipe['refs'][role]) if role in recipe['refs'] else None
    result = {}
    entity = get('actor') or get('object') or get('enemy')
    if entity:
        result.update(name=entity['name'], template=entity['template'], position=entity['transform'].get('position', [0, 0, 0]), orientation=entity['transform'].get('orientation', [0, 0, 0]))
    obj=get('object')
    if recipe['type']=='object_conversation' and obj:result.update(object_template=obj['template'],object_name=obj['name'],object_position=obj['transform']['position'])
    conv = get('conversation')
    if conv:
        node = next((n for n in conv.get('nodes', []) if n['id'] == conv.get('entry')), None)
        result['text'] = node['lines'][0]['text'] if node else conv.get('prompt', '')
        choices = node['choices'] if node else conv['choices']
        if choices:result['accept'] = choices[0]['text']
        if len(choices) > 1:result['decline'] = choices[1]['text']
        result['camera'] = conv.get('camera', 'ots_speaker_close')
    trigger = get('trigger')
    if trigger:
        result.update(trigger_position=trigger['transform']['position'], radius=trigger.get('radius', 100))
    seq = get('sequence')
    if seq:
        result.update(duration=seq['duration'], target=seq['actor'], steps=copy.deepcopy(seq.get('steps', [])), reference=seq.get('reference'))
    event = get('event')
    if event:
        result.update(actions=copy.deepcopy(event['actions']), conditions=copy.deepcopy(event.get('conditions', [])), once=event.get('once', False))
        for action in event['actions']:
            if 'show_note' in action:result.update(title=action['show_note']['title'], text=action['show_note']['text'])
            if 'travel' in action:result.update(destination=action['travel']['scene'], arrival=action['travel']['entry'])
            if 'reward_xp' in action:result['reward_xp']=action['reward_xp']
    quest = get('quest')
    if quest:result.update(title=quest['title'], text=quest['description'], quest_steps=quest['steps'], reward_xp=quest.get('reward_xp', 0))
    entry = get('entry')
    if entry:result['arrival_position'] = entry['transform']['position']
    if 'flag' in recipe['refs']:result['flag'] = recipe['refs']['flag']['id']
    return copy.deepcopy(result)


def apply(root, kind, scene_id, config, recipe_id=None, repair=False):
    """One source transaction. Repair is explicit; never silently recreate rows."""
    if kind not in TYPES or root.get('project_format') not in (9,10):raise ValueError('Recipes require a format 9 campaign')
    result = copy.deepcopy(root)
    if not any(s['id']==scene_id for s in result['scenes']):raise ValueError('Recipe scene is missing')
    saved = next((r for r in recipes(result) if r['id'] == recipe_id), None)
    if recipe_id and saved is None:raise ValueError('Recipe no longer exists')
    if saved and (saved['type'] != kind or saved['scene'] != scene_id):raise ValueError('Recipe kind or scene changed')
    if saved and missing(result, saved) and not repair:raise ValueError('Incomplete configuration: repair, choose another resource or unlink')
    recipe = saved or dict(id=unique(recipes(result), kind), type=kind, version=1, scene=scene_id, refs={})
    def ensure(role, coll, row, sid=scene_id):
        ref = recipe['refs'].get(role)
        current = resolve(result, ref) if ref else None
        if role=='entry' and ref and ref.get('scene')!=sid:
            ref=None;current=None
        if current is not None:return current
        target = result.get('quests', []) if coll == 'quests' else next(s for s in result['scenes'] if s['id'] == sid).setdefault(coll, [])
        stem={'conversation':'conv','spawn_event':'spawn','answer_event':'answer','end_event':'end'}.get(role,role)
        ident = ref['id'] if ref else unique(target, stem)
        if any(r['id'] == ident for r in target):raise ValueError('Recipe repair ID conflict')
        current = dict(id=ident, **copy.deepcopy(row));target.append(current)
        if coll == 'quests':result['quests'] = target
        recipe['refs'][role] = dict(collection=coll, id=ident, **({} if coll == 'quests' else dict(scene=sid)))
        return current
    def flag(role):
        ref = recipe['refs'].get(role)
        flags = result.setdefault('state', {}).setdefault('flags', {})
        alias = ref['id'] if ref else unique([{'id':k} for k in flags], role)
        if alias not in flags:
            free = next((i for i in range(256) if i not in flags.values()), None)
            if free is None:raise ValueError('No free Chronicle Flag')
            flags[alias] = free
        recipe['refs'][role] = dict(collection='flags', id=alias)
        return alias
    def transform(position):return dict(placement='absolute', position=list(position), orientation=list(config.get('orientation', [0, 0, 180])))
    position = config.get('position', [-176, -612, 384])
    def entity(role, coll, template):
        fields=config
        if role=='object' and kind=='object_conversation':fields={k[7:]:v for k,v in config.items() if k.startswith('object_')}
        row = ensure(role, coll, dict(name=fields.get('name', role), template=fields.get('template', template), transform=transform(fields.get('position',position))))
        for key in ('name', 'template'):
            if key in fields:row[key] = fields[key]
        if 'position' in fields:row['transform'] = transform(fields['position'])
        return row
    def event(role, when, actions, **filters):
        row = ensure(role, 'events', dict(when=when, actions=actions, **filters))
        row.update(when=when, **filters)
        return row
    def start_spawn(row):
        spawn = event('spawn_event', 'scene_start', [{'spawn':row['id']}])
        # Keep manual extra actions; only the referenced spawn is ours.
        if not any(a.get('spawn') == row['id'] for a in spawn['actions']):spawn['actions'].insert(0, {'spawn':row['id']})
    def conversation(actor):
        row = ensure('conversation', 'conversations', dict(speaker=actor['id'], prompt=config.get('text', 'Hello.'), choices=[dict(text=config.get('accept', 'Continue.'), result=1), dict(text=config.get('decline', 'Not yet.'), result=2)]))
        row['speaker'] = actor['id'];row['camera'] = config.get('camera', row.get('camera', 'ots_speaker_close'))
        node = next((n for n in row.get('nodes', []) if n['id'] == row.get('entry')), None)
        if node:
            if 'text' in config:node['lines'][0]['text'] = config['text']
            choices = node['choices']
        else:
            if 'text' in config:row['prompt'] = config['text']
            choices = row['choices']
        for i, key in enumerate(('accept', 'decline')):
            if key in config and i < len(choices):choices[i]['text'] = config[key]
        return row
    def trigger():
        row = ensure('trigger', 'triggers', dict(name='Arrival area', shape='sphere', transform=transform(config.get('trigger_position', position)), radius=config.get('radius', 100)))
        if 'trigger_position' in config:row['transform']['position'] = list(config['trigger_position'])
        if 'radius' in config and row['shape']=='sphere':row['radius'] = config['radius']
        if row['shape']=='sphere':row['transform']['orientation']=[0,0,0]
        return row
    def cinema():
        row = ensure('sequence', 'sequences', dict(name='Arrival', actor='Player', shot='wide', angle='high', duration=6., steps=[dict(at=0, actor='Player', preset='aerial', transition=0), dict(at=3, actor='Player', preset='speaker_close', transition=1.5)]))
        for key in ('duration', 'steps', 'reference'):
            if key in config:
                if config[key] is None:row.pop(key, None)
                else:row[key] = copy.deepcopy(config[key])
        if 'target' in config:
            row['actor'] = config['target']
            for step in row['steps']:step['actor'] = config['target']
        return row
    if kind in {'talk', 'go_to_place', 'object_conversation'}:
        actor = entity('actor', 'actors', 'Anezka');actor.setdefault('behavior', 'npc');start_spawn(actor)
        conv = conversation(actor)
        if kind != 'object_conversation':actor.setdefault('conversation', {})['default'] = conv['id']
        if kind == 'go_to_place':
            progress = flag('flag');done = flag('done_flag');area = trigger();film = cinema()
            if not saved and not config.get('reference'):film['reference']=actor['id']
            accepted = event('answer_event', 'conversation_ended', [{'set_flag':progress}], conversation=conv['id'], result=1)
            accepted['once'] = True
            enter = event('event', 'trigger_enter', [{'play_sequence':film['id']}], trigger=area['id'])
            enter.setdefault('conditions',[dict(flag=progress, is_set=True), dict(flag=done, is_set=False)]);enter.setdefault('once',True)
            ended = event('end_event', 'sequence_ended', [{'set_flag':done}], sequence=film['id']);ended['once'] = True
        elif kind == 'object_conversation':
            obj = entity('object', 'objects', 'barrel1');start_spawn(obj)
            event('event', 'object_clicked', [{'start_conversation':conv['id']}], object=obj['id'])
    elif kind in {'trigger_actions', 'trigger_cinematic', 'travel'}:
        area = trigger()
        actions = config.get('actions', [{'reward_xp':10}])
        if kind == 'trigger_cinematic':
            film = cinema();actions = [{'play_sequence':film['id']}]
            done = flag('done_flag')
            ended = event('end_event', 'sequence_ended', [{'set_flag':done}], sequence=film['id']);ended['once'] = True
        if kind == 'travel':
            destination = config.get('destination')
            if not any(s['id'] == destination for s in result['scenes']):raise ValueError('Choose a destination scene')
            if destination==scene_id:raise ValueError('No se permite un enlace hacia la misma escena. Elige otra escena de destino.')
            entry = ensure('entry', 'entries', dict(name='Arrival', transform=transform(config.get('arrival_position', position))), destination)
            if 'arrival_position' in config:entry['transform'] = transform(config['arrival_position'])
            actions = [dict(travel=dict(scene=destination, entry=entry['id']))]
        row = event('event', 'trigger_enter', actions, trigger=area['id'])
        row.update(actions=copy.deepcopy(actions), conditions=copy.deepcopy(config.get('conditions', row.get('conditions', []))), once=config.get('once', True))
        area['once']=row['once']
    elif kind == 'pickup':
        obj = entity('object', 'objects', 'ledger');obj['quest_item'] = True;start_spawn(obj)
        row = event('event', 'item_picked_up', [{'set_flag':flag('flag')}], item=obj['id']);row['once'] = True
    elif kind == 'quest':
        row = ensure('quest', 'quests', dict(title=config.get('title', 'An errand'), description=config.get('text', 'Find the letter.'), steps=config.get('quest_steps', ['Find the letter.']), reward_xp=config.get('reward_xp', 0)))
        for key, field in [('title','title'), ('text','description'), ('quest_steps','steps'), ('reward_xp','reward_xp')]:
            if key in config:row[field] = copy.deepcopy(config[key])
        event('event', 'scene_start', [{'start_quest':row['id']}])['once'] = True
    elif kind == 'encounter':
        enemy = entity('enemy', 'actors', 'Rat');enemy['behavior'] = 'enemy'
        group = ensure('encounter', 'encounters', dict(name='A small encounter', actors=[enemy['id']]))
        spawn = event('spawn_event', 'scene_start', [{'spawn_encounter':group['id']}]);spawn['once'] = True
        complete = event('event', 'encounter_complete', [{'set_flag':flag('flag')}, *([{'reward_xp':config.get('reward_xp', 10)}] if config.get('reward_xp',10)>0 else [])], encounter=group['id']);complete['once'] = True
        if saved and 'reward_xp' in config:
            complete['actions']=[a for a in complete['actions'] if 'reward_xp' not in a]
            if config['reward_xp']>0:complete['actions'].append({'reward_xp':config['reward_xp']})
    elif kind == 'note':
        obj = entity('object', 'objects', 'barrel1');start_spawn(obj)
        row = event('event', 'object_clicked', [{'show_note':dict(title=config.get('title', 'A letter'), text=config.get('text', 'Meet me at the square.'))}], object=obj['id'])
        note=next((a['show_note'] for a in row['actions'] if 'show_note' in a),None)
        if note is None:
            note=dict(title='A letter',text='Meet me at the square.');row['actions'].append({'show_note':note})
        for key in ('title','text'):
            if key in config:note[key]=config[key]
    if not saved:result.setdefault('authoring', {}).setdefault('recipes', []).append(recipe)
    validate_authoring(result)
    return result, recipe['id']
