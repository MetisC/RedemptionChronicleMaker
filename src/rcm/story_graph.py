"""Derived story graphs over authoring data. No second execution model."""
def conversation_graph(conv, prefix=()):
    nodes=conv.get('nodes')
    if nodes is None:
        nodes=[dict(id='opening',lines=[dict(speaker=conv.get('speaker',''),text=conv.get('prompt',''))],choices=conv.get('choices',[]))]
    entry=conv.get('entry','opening');ids={n['id'] for n in nodes};edges=[];out={n:set() for n in ids};returns=set();missing=[]
    for i,n in enumerate(nodes):
        for j,a in enumerate(n.get('choices',[])):
            path=prefix+('nodes',i,'choices',j) if 'nodes' in conv else prefix+('choices',j)
            target=a.get('goto');edges.append(dict(source=n['id'],target=target,label=a.get('text',''),result=a.get('result'),path=path))
            if target is None:returns.add(n['id'])
            elif target in ids:out[n['id']].add(target)
            else:missing.append(target)
    def reachable(start):
        seen=set();todo=list(start)
        while todo:
            key=todo.pop()
            if key in seen or key not in ids:continue
            seen.add(key);todo.extend(out[key]-seen)
        return seen
    reached=reachable([entry]);escaping=set(returns)
    while True:
        nxt=escaping|{k for k,v in out.items() if v&escaping}
        if nxt==escaping:break
        escaping=nxt
    # A node is cyclic exactly when one of its successors can return to it.
    cycles={k for k,v in out.items() if any(k in reachable([s]) for s in v)}
    rows=[dict(id=n['id'],lines=n.get('lines',[]),entry=n['id']==entry,unreachable=n['id'] not in reached,dead=n['id'] not in escaping,cycle=n['id'] in cycles,path=prefix+('nodes',i) if 'nodes' in conv else prefix+('prompt',)) for i,n in enumerate(nodes)]
    return dict(nodes=rows,edges=edges,missing=missing,entry=entry)

def scene_reachability(root):
    scenes=root.get('scenes',[]);known={s['id'] for s in scenes};reached=set();todo=[root.get('entry')]
    while todo:
        sid=todo.pop()
        if sid in reached or sid not in known:continue
        reached.add(sid)
        scene=next(s for s in scenes if s['id']==sid)
        for event in scene.get('events',[]):
            for action in event.get('actions',[]):
                target=action.get('travel',action.get('jump'))
                if isinstance(target,str):todo.append(target)
                elif isinstance(target,dict):todo.append(target.get('scene'))
    return known-reached
