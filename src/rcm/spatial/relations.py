"""Reference graph derived from the shared YAML, never a separate story model."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Link:
    source: tuple
    target: tuple
    label: str
    detail: tuple

def graph(data):
    ids = {}
    for key in ('actors', 'objects', 'conversations', 'events', 'triggers','waypoints','generators'):
        for i, item in enumerate(data.get(key, [])):
            if item.get('id'):
                ids[(key, item['id'])] = (key, i)
    for key in data.get('state', {}).get('flags', {}):
        ids[('flags', key)] = ('state', 'flags', key)
    links = []
    def add(source, kind, value, label, detail):
        if not isinstance(value,str):return
        target = ids.get((kind, value))
        if target is not None:
            links.append(Link(source, target, label, detail))
    for i, a in enumerate(data.get('actors', [])):
        p = ('actors', i)
        for k, v in a.get('conversation', {}).items():
            add(p, 'flags' if k == 'when_flag' else 'conversations', v, k, p + ('conversation', k))
    for i, c in enumerate(data.get('conversations', [])):
        p = ('conversations', i)
        add(p, 'actors', c.get('speaker'), 'speaker', p + ('speaker',))
        for ni, node in enumerate(c.get('nodes', [c])):
            prefix = p + ('nodes', ni) if 'nodes' in c else p
            for li, line in enumerate(node.get('lines', [])):
                add(p, 'actors', line.get('speaker', c.get('speaker')), 'línea', prefix + ('lines', li))
            for ci, ch in enumerate(node.get('choices', [])):
                for k in ('set_flag', 'clear_flag'):
                    if k in ch:
                        add(p, 'flags', ch[k], k, prefix + ('choices', ci))
    for i, e in enumerate(data.get('events', [])):
        p = ('events', i)
        for k, kind in [('actor', 'actors'), ('conversation', 'conversations'), ('trigger', 'triggers')]:
            if k in e:
                add(p, kind, e[k], 'activado por ' + k, p)
        for ci, c in enumerate(e.get('conditions', [])):
            add(p, 'flags', c.get('flag'), 'condición', p + ('conditions', ci))
        for ai, a in enumerate(e.get('actions', [])):
            for k, v in a.items():
                kind = 'generators' if k in ('start_generator','stop_generator','pause_generator','resume_generator','reset_generator') else 'conversations' if k == 'start_conversation' else 'flags'
                if k == 'spawn':
                    kind = 'actors' if ('actors', v) in ids else 'objects'
                add(p, kind, v, k, p + ('actions', ai))
    for gi,g in enumerate(data.get('generators',[])):
        p=('generators',gi)
        for pi,key in enumerate(g.get('spawn_points',[])):add(p,'waypoints',key,'spawn point',p+('spawn_points',pi))
        for wave in g['waves']:
            for group in wave['groups']:
                for key in group.get('spawn_points',[]):add(p,'waypoints',key,'spawn point',p)
        if g.get('visual'):add(p,'objects',g['visual'],'visual',p+('visual',))
        if g.get('boss',{}).get('actor'):add(p,'actors',g['boss']['actor'],'boss',p+('boss','actor'))
    return links

def references(data, path):
    links = graph(data)
    path = tuple(path)
    return ([x for x in links if x.target == path], [x for x in links if x.source == path])

def affected(data, path):
    """Selection-only highlights: one event neighborhood, not all transitive flags."""
    links = graph(data)
    neighborhood = {tuple(path)}
    if path and path[0] in ('actors', 'objects', 'triggers','generators'):
        neighborhood |= {x.source for x in links if x.target == tuple(path) and x.source[0] == 'events'}
    return {x.target for x in links if x.source in neighborhood and x.target[0] in ('actors', 'objects', 'triggers','waypoints')}
