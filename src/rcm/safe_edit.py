"""Preflight deletion against references and the validator, without mutations."""
import copy
from dataclasses import dataclass


def at(root,path):
    for key in path:root=root[key]
    return root


def reference_links(doc,path):
    from .campaign_relations import graph as campaign_graph
    from .spatial.relations import graph as scene_graph
    links=(campaign_graph if hasattr(doc,'campaign') else scene_graph)(doc.snapshot())
    path=tuple(path)
    return [link for link in links if link.target[:len(path)]==path and link.source[:len(path)]!=path and link.label!='authoring recipe']


@dataclass
class DeletionPlan:
    candidate: dict
    removed: tuple
    references: tuple
    changed: tuple=()


def deletion_plan(doc,path,backend):
    """Explicit cascade preview; no mutation and no weakened conditions.

    Remove exact action/list uses when possible. Required dependencies remove
    their owning record, recursively. Conditions remove the dependent record,
    never turn a guarded event into an unconditional event. Validate the result.
    """
    from .campaign_relations import graph as campaign_graph
    from .spatial.relations import graph as scene_graph
    root=doc.snapshot();path=tuple(path)
    if not path or (isinstance(at(root,path[:-1]),list) and type(path[-1]) is not int):raise ValueError('Selecciona un elemento para eliminar')
    if path==('scenes',) or path[:1] in {('chronicle',),('level',),('geometry',),('original',)}:raise ValueError('Esta parte del proyecto no se puede eliminar')
    removed={path};changed={};links=(campaign_graph if hasattr(doc,'campaign') else scene_graph)(root)
    def inside(p):return any(tuple(p[:len(r)])==r for r in removed)
    def delete(p):
        p=tuple(p)
        if not inside(p):removed.add(p)
    def list_uses(p):
        value=at(root,p)
        return [v for i,v in enumerate(value) if not inside(p+(i,))]
    processed=set()
    while True:
        pending=[link for link in links if inside(link.target) and not inside(link.source) and not inside(link.detail) and link not in processed]
        if not pending:break
        for link in pending:
            processed.add(link);source=tuple(link.source);detail=tuple(link.detail)
            if link.label=='authoring recipe':delete(source);continue
            if link.label in {'native script parameter','native script class'}:delete(source+('native_script',));continue
            if link.label=='native movement frames':delete(source);continue
            if link.label in {'ai','script'}:delete(detail);continue
            if detail==('entry',):
                scenes=[s for i,s in enumerate(root['scenes']) if not inside(('scenes',i))]
                if not scenes:raise ValueError('La campaña necesita una escena')
                changed[detail]=scenes[0]['id'];continue
            if link.label=='default_entry':delete(detail);continue
            if link.label=='map_location':delete(detail);continue
            if link.label=='staging':delete(detail);continue
            if link.label=='conversation placement':
                delete(detail)
                if not list_uses(detail[:-1]):delete(detail[:-2])
                continue
            # A single action is an independently editable reference.
            action=next((detail[:i+2] for i,k in enumerate(detail[:-1]) if k=='actions' and type(detail[i+1]) is int),None)
            if action:
                delete(action)
                actions=action[:-1]
                if not list_uses(actions):
                    if 'lines' in actions:
                        delete(actions);continue
                    # Event/phase without actions cannot run; remove it as well.
                    delete(actions[:-1])
                continue
            # Optional bindings are detached rather than deleting the actor.
            if 'conversation' in detail and source[-2:-1]==('actors',):
                delete(source+('conversation',));continue
            if link.label in {'visual','reference'}:delete(detail);continue
            parent=at(root,detail[:-1])
            if isinstance(parent,list) and type(detail[-1]) is int:
                delete(detail);remaining=list_uses(detail[:-1]);kind=detail[-2]
                if kind=='actors' and not remaining:delete(source)
                elif kind=='points' and len(remaining)<2:delete(source)
                elif kind=='spawn_points' and not remaining:
                    if detail[:-2]==source and at(root,source).get('placement','points')=='points':delete(source)
                    else:delete(detail[:-1])
                continue
            # A missing speaker/trigger/boss/condition requires removing its
            # dependent entity, not leaving an invalid or widened behavior.
            delete(source)
    # Deleting an action directly uses the same empty-container policy.
    for p in tuple(removed):
        if len(p)>=2 and p[-2]=='actions' and not list_uses(p[:-1]):delete(p[:-1] if 'lines' in p else p[:-2])
    if 'scenes' in root and all(inside(('scenes',i)) for i in range(len(root['scenes']))):raise ValueError('La campaña necesita una escena')
    removed={p for p in removed if not any(p!=other and p[:len(other)]==other for other in removed)}
    candidate=copy.deepcopy(root)
    for p,value in changed.items():
        if not inside(p):at(candidate,p[:-1])[p[-1]]=value
    for p in sorted(removed,key=lambda p:tuple((0,k) if isinstance(k,str) else (1,k) for k in p),reverse=True):
        parent=at(candidate,p[:-1]);parent.pop(p[-1])
    before={p.message for p in backend.validate(root).problems if p.severity=='ERROR'}
    after={p.message for p in backend.validate(candidate).problems if p.severity=='ERROR'}
    if after-before:raise ValueError('No se puede completar el borrado: '+'\n'.join(sorted(after-before)))
    return DeletionPlan(candidate,tuple(sorted(removed,key=repr)),tuple(reference_links(doc,path)),tuple(changed))


def delete_candidate(doc, path, backend, remove_spawns=False, remove_references=False):
    if remove_references:return deletion_plan(doc,path,backend).candidate
    path = tuple(path)
    root = doc.snapshot()
    if hasattr(doc, 'campaign'):
        from .campaign_relations import graph
        links = graph(root)
    else:
        from .spatial.relations import graph
        links = graph(root)
    def inside(p):return tuple(p[:len(path)]) == path
    incoming = [link for link in links if inside(link.target) and not inside(link.source) and link.label!='authoring recipe']
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
        raise ValueError('No se borra sin revisar: '+str(len(incoming))+' referencias cruzadas. Revisa el borrado conjunto.')
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
