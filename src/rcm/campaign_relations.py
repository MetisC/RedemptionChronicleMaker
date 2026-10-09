"""Typed references/search for the complete campaign source."""
from .campaign import ACTIONS
from .spatial.relations import Link

def graph(root):
    index={};links=[]
    for qi,q in enumerate(root.get('quests',[])):index[('quest',q['id'])]=('quests',qi)
    for alias in root.get('state',{}).get('flags',{}):index[('flag',alias)]=('state','flags',alias)
    for si,s in enumerate(root['scenes']):
        index[('scene',s['id'])]=('scenes',si)
        for i,point in enumerate(s.get('entries',[])):index[('arrival',s['id']+'.'+point['id'])]=('scenes',si,'entries',i)
        for i,o in enumerate(s.get('objects',[])):index[('objects',s['id']+'.'+o['id'])]=('scenes',si,'objects',i)
    entry=index.get(('scene',root.get('entry')))
    if entry:links.append(Link(('entry',),entry,'entry',('entry',)))
    def scan(value,path,source,local):
        if isinstance(value,list):
            for i,v in enumerate(value):scan(v,path+(i,),source,local)
        elif isinstance(value,dict):
            for k,v in value.items():
                if k=='travel' and isinstance(v,dict):
                    for category,name in [('scene',v.get('scene')),('arrival',str(v.get('scene'))+'.'+str(v.get('entry')))]:
                        target=index.get((category,name))
                        if target:links.append(Link(source,target,'travel',path+(k,)))
                category={'speaker':'actors','actor':'actors','actor_alive':'actors','entity_exists':'entity','item':'objects','item_global':'objects','owns_item':'objects','conversation':'conversations','default':'conversations','then':'conversations','trigger':'triggers','encounter':'encounters','quest':'quest','flag':'flag','when_flag':'flag'}.get(k)
                if k in ACTIONS:category={'flags':'flag','quests':'quest','scenes':'scene','item':'objects','item_global':'objects'}.get(ACTIONS[k][1],ACTIONS[k][1])
                if isinstance(v,str) and category:
                    target=index.get((category,v)) or local.get((category,v))
                    if target:links.append(Link(source,target,k,path+(k,)))
                if isinstance(v,(dict,list)):scan(v,path+(k,),source,local)
    for si,s in enumerate(root['scenes']):
        local={}
        for k in ('actors','objects','triggers','conversations','events','encounters','sequences','entries','waypoints','paths'):
            for i,row in enumerate(s.get(k,[])):
                local[(k,row['id'])]=('scenes',si,k,i)
                if k in ('actors','objects'):local[('entity',row['id'])]=('scenes',si,k,i)
        for k in ('actors','objects','triggers','conversations','events','encounters','sequences','entries','waypoints','paths'):
            for i,row in enumerate(s.get(k,[])):
                source=('scenes',si,k,i);scan(row,source,source,local)
                for listkey,targetkind in [('actors','actors'),('inventory','objects'),('points','waypoints')]:
                    for member in row.get(listkey,[]):
                        target=local.get((targetkind,member))
                        if target:links.append(Link(source,target,listkey,source+(listkey,)))
        if s.get('default_entry'):
            target=local.get(('entries',s['default_entry']))
            if target:links.append(Link(('scenes',si),target,'default_entry',('scenes',si,'default_entry')))
    return links
