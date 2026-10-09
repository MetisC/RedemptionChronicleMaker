"""Preflight deletion against references and the validator, without mutations."""
import copy


def delete_candidate(doc, path, backend, remove_spawns=False):
    path = tuple(path)
    root = doc.snapshot()
    if hasattr(doc, 'campaign'):
        from .campaign_relations import graph
        links = graph(root)
    else:
        from .spatial.relations import graph
        links = graph(root)
    def inside(p):return tuple(p[:len(path)]) == path
    incoming = [link for link in links if inside(link.target) and not inside(link.source)]
    # A generated spawn is a use of the entity being deleted, not an unrelated
    # story dependency. Remove those exact actions in the same undo transaction.
    spawn_actions = set()
    if remove_spawns and len(path) >= 2 and path[-2] in {'actors', 'objects'}:
        for link in incoming:
            if link.label != 'spawn':
                continue
            detail = tuple(link.detail)
            if detail[-1] == 'spawn':
                detail = detail[:-1]
            action = root
            for part in detail:
                action = action[part]
            if isinstance(action, dict) and set(action) == {'spawn'}:
                spawn_actions.add(detail)
        incoming = [link for link in incoming if not (link.label == 'spawn' and (tuple(link.detail[:-1]) if link.detail[-1] == 'spawn' else tuple(link.detail)) in spawn_actions)]
    if incoming:
        raise ValueError('No se borra: '+str(len(incoming))+' referencias externas. Reasígnalas primero; usa Buscar referencias.')
    candidate = copy.deepcopy(root)
    for action_path in sorted(spawn_actions, key=lambda p: (repr(p[:-1]), p[-1]), reverse=True):
        actions = candidate
        for part in action_path[:-1]:
            actions = actions[part]
        actions.pop(action_path[-1])
    empty_starts = set()
    for action_path in spawn_actions:
        event_path = action_path[:-2]
        event = candidate
        for part in event_path:
            event = event[part]
        if event.get('when') == 'scene_start' and not event.get('conditions') and not event['actions']:
            empty_starts.add(event_path)
    for event_path in sorted(empty_starts, key=lambda p: (repr(p[:-1]), p[-1]), reverse=True):
        events = candidate
        for part in event_path[:-1]:
            events = events[part]
        events.pop(event_path[-1])
    parent = candidate
    for part in path[:-1]:parent = parent[part]
    if isinstance(parent, list):parent.pop(path[-1])
    else:parent.pop(path[-1])
    before = {p.message for p in backend.validate(root).problems if p.severity=='ERROR'}
    after = {p.message for p in backend.validate(candidate).problems if p.severity=='ERROR'}
    added = after-before
    if added:raise ValueError('No se borra: '+ '\n'.join(sorted(added)))
    return candidate
