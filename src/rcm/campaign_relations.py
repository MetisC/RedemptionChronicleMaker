"""Typed references/search for the complete campaign source."""
from .campaign import ACTIONS
from .spatial.relations import Link

def graph(root):
    index={};links=[]
    for qi,q in enumerate(root.get('quests',[])):index[('quest',q['id'])]=('quests',qi)
    for i,t in enumerate(root.get('resources',{}).get('templates',[])):index[('templates',t['id'])]=('resources','templates',i)
    for i,t in enumerate(root.get('resources',{}).get('camera_paths',[])):index[('camera_paths',t['id'])]=('resources','camera_paths',i)
    for kind in ('ai_profiles','scripts','textures'):
        for i,t in enumerate(root.get('resources',{}).get(kind,[])):index[(kind,t['id'])]=('resources',kind,i)
    for alias in root.get('state',{}).get('flags',{}):index[('flag',alias)]=('state','flags',alias)
    for si,s in enumerate(root['scenes']):
        index[('scene',s['id'])]=('scenes',si)
        for i,point in enumerate(s.get('entries',[])):index[('arrival',s['id']+'.'+point['id'])]=('scenes',si,'entries',i)
        for i,o in enumerate(s.get('objects',[])):index[('objects',s['id']+'.'+o['id'])]=('scenes',si,'objects',i)
    entry=index.get(('scene',root.get('entry')))
    if entry:links.append(Link(('entry',),entry,'entry',('entry',)))
    for i,row in enumerate(root.get('resources',{}).get('camera_paths',[])):
        target=index.get(('scene',row.get('scene')))
        if target:links.append(Link(('resources','camera_paths',i),target,'creation scene',('resources','camera_paths',i,'scene')))
    def scan(value,path,source,local):
        if isinstance(value,list):
            for i,v in enumerate(value):scan(v,path+(i,),source,local)
        elif isinstance(value,dict):
            for k,v in value.items():
                if k=='native_script' and isinstance(v,dict):
                    target=index.get(('scripts',v.get('class')))
                    if target:links.append(Link(source,target,'native script class',path+(k,'class')))
                    for pi,arg in enumerate(v.get('parameters',[])):
                        if isinstance(arg,dict) and arg.get('type') in ('actor','thing'):
                            target=local.get(('entity',arg.get('value')))
                            if target:links.append(Link(source,target,'native script parameter',path+(k,'parameters',pi,'value')))
                if k=='native_frames' and isinstance(v,list):
                    for pi,key in enumerate(v):
                        target=local.get(('waypoints',key))
                        if target:links.append(Link(source,target,'native movement frames',path+(k,pi)))
                if k=='staging' and isinstance(v,dict):
                    for pi,key in enumerate(v.get('entries',[])):
                        target=local.get(('entries',key))
                        if target:links.append(Link(source,target,'conversation placement',path+(k,'entries',pi)))
                if k=='travel' and isinstance(v,dict):
                    for category,name in [('scene',v.get('scene')),('arrival',str(v.get('scene'))+'.'+str(v.get('entry')))]:
                        target=index.get((category,name))
                        if target:links.append(Link(source,target,'travel',path+(k,)))
                category={'reference':'actors','sequence':'sequences','move_path':'paths','focus':'objects','object':'objects','speaker':'actors','actor':'actors','actor_alive':'actors','entity_exists':'entity','item':'objects','item_global':'objects','owns_item':'objects','conversation':'conversations','default':'conversations','then':'conversations','trigger':'triggers','encounter':'encounters','quest':'quest','flag':'flag','when_flag':'flag','generator':'generators','visual':'objects','template':'templates'}.get(k)
                category={'camera_path':'camera_paths','staging':'entries','target':'actors','waypoint':'waypoints','stop_actor':'actors','entity':'entity'}.get(k,category)
                if k=='ai':category='ai_profiles'
                if k=='script':category='scripts'
                if k=='base' and path[:1]==('resources',) and len(path)>1 and path[1] in ('templates','ai_profiles'):category=path[1]
                if k=='resource' and path[-1:]==('play_camera_path',):category='camera_paths'
                if k=='stop_sound' and isinstance(v,str):
                    for target in local.get(('sound_loop',v),[]):links.append(Link(source,target,'stop_sound',path+(k,)))
                if k in ACTIONS:category={'flags':'flag','quests':'quest','scenes':'scene','item':'objects','item_global':'objects'}.get(ACTIONS[k][1],ACTIONS[k][1])
                if isinstance(v,str) and category:
                    target=index.get((category,v)) or local.get((category,v))
                    if target:links.append(Link(source,target,k,path+(k,)))
                if k=='spawn_points' and isinstance(v,list):
                    for pi,key in enumerate(v):
                        target=local.get(('waypoints',key))
                        if target:links.append(Link(source,target,'spawn_points',path+(k,pi)))
                if isinstance(v,(dict,list)):scan(v,path+(k,),source,local)
    for kind,records in root.get('resources',{}).items():
        for i,row in enumerate(records):
            source=('resources',kind,i);scan(row,source,source,{})
    for si,s in enumerate(root['scenes']):
        local={}
        for k in ('actors','objects','triggers','conversations','events','encounters','sequences','entries','waypoints','paths','generators'):
            for i,row in enumerate(s.get(k,[])):
                local[(k,row['id'])]=('scenes',si,k,i)
                if k in ('actors','objects'):local[('entity',row['id'])]=('scenes',si,k,i)
        def sound_definitions(value,path):
            if isinstance(value,list):
                for i,child in enumerate(value):sound_definitions(child,path+(i,))
            elif isinstance(value,dict):
                sound=value.get('play_sound')
                if isinstance(sound,dict) and sound.get('loop') is True:local.setdefault(('sound_loop',sound.get('id')),[]).append(path)
                for key,child in value.items():sound_definitions(child,path+(key,))
        sound_definitions(s,('scenes',si))
        for k in ('actors','objects','triggers','conversations','events','encounters','sequences','entries','waypoints','paths','generators'):
            for i,row in enumerate(s.get(k,[])):
                source=('scenes',si,k,i);scan(row,source,source,local)
                for listkey,targetkind in [('actors','actors'),('inventory','objects'),('points','waypoints')]:
                    for mi,member in enumerate(row.get(listkey,[])):
                        target=local.get((targetkind,member))
                        if target:links.append(Link(source,target,listkey,source+(listkey,mi)))
        if s.get('default_entry'):
            target=local.get(('entries',s['default_entry']))
            if target:links.append(Link(('scenes',si),target,'default_entry',('scenes',si,'default_entry')))
    from .recipes import recipes
    for ri,recipe in enumerate(recipes(root)):
        source=('authoring','recipes',ri)
        for role,ref in recipe['refs'].items():
            target=index.get(('quest',ref['id'])) if ref['collection']=='quests' else index.get(('flag',ref['id'])) if ref['collection']=='flags' else None
            if ref['collection'] not in {'quests','flags'}:
                for si,s in enumerate(root['scenes']):
                    if s['id']==ref.get('scene'):
                        target=next((('scenes',si,ref['collection'],i) for i,row in enumerate(s.get(ref['collection'],[])) if row['id']==ref['id']),None)
            if target:links.append(Link(source,target,'authoring recipe',source+('refs',role)))
    return links
