"""Enemy provenance from original template inheritance and observed scene use."""
from collections import defaultdict
from .formats import NotFile,u32

def catalogue(backend):
    key=id(backend.resources)
    if getattr(backend,'_enemy_catalogue_key',None)==key:return backend._enemy_catalogue
    raw=defaultdict(list)
    for path in backend.ws.output('research/original').rglob('*.not'):
        for t in NotFile.read(path.read_bytes()).templates:raw[t.name.casefold()].append(t.values())
    templates=defaultdict(list)
    for t in backend.resources['templates']:templates[t['id'].casefold()].append(t)
    usage=defaultdict(set)
    for scene,row in backend.hints.items():
        for e in row.get('entities',[]):usage[e['template'].casefold()].add(scene)
    result={}
    def resolve(name,seen):
        if name.casefold() in seen or len(templates[name.casefold()])!=1:return {},[]
        row=templates[name.casefold()][0];parent=row.get('parent');values={};chain=[row['id']]
        if parent:values,ancestors=resolve(parent,seen|{name.casefold()});chain+=ancestors
        if len(raw[name.casefold()])==1:values={**values,**raw[name.casefold()][0]}
        return values,chain
    for name,rows in templates.items():
        if len(rows)!=1 or rows[0].get('kind')!='actors':continue
        t=rows[0];values,chain=resolve(t['id'],set());flags=t.get('actor_flags',0)
        # Original taxonomy, not a substring/guess on the displayed actor name.
        enemy='_Enemies' in chain and not (flags&262144)
        result[t['id']]={'enemy':enemy,'enemy_evidence':'original _Enemies inheritance; non-neutral actor flags' if enemy else 'not established as an original enemy',
                         'group':'animals' if flags&8192 else 'other','ancestor_chain':chain,'original_scene_usage':sorted(usage[name]),
                         'health':u32(values[52]) if 52 in values else None,'max_health':u32(values[60]) if 60 in values else None,
                         'clan':u32(values[26]) if 26 in values else None,'actor_flags':flags,'model':t.get('model'),'ai':t.get('ai'),'script':t.get('script'),
                         'source':t.get('archive','')+'/'+t.get('path',''),'project_owned':bool(t.get('project_owned')),
                         'usage_confidence':'bounded NSD tag hints; not a complete scene parser'}
    backend._enemy_catalogue_key=key;backend._enemy_catalogue=result
    return result

def details(row):
    fields=[]
    for label,key in [('Vida original','health'),('Vida máxima original','max_health'),('Clan (ID nativo)','clan'),('Flags originales','actor_flags')]:
        if row.get(key) is not None:fields.append((label,str(row[key])))
    if row.get('original_scene_usage'):fields.append(('Usado en escenas originales',', '.join(row['original_scene_usage'])))
    fields.append(('Clasificación','Familia original de enemigos' if row.get('enemy') else 'Sin clasificar como enemigo original'))
    return fields
