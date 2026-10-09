"""Instrumentation and conservative parsing of our runtime trace and stack frames."""
import re
from .generator import java_string as js

def instrument(java,campaign,scene,info):
    lines=java.splitlines()
    if not info.get('debug',True):
        return '\n'.join(' private void trace(String s) {}' if 'private void trace(String s)' in l else re.sub(r'\btrace\([^;\n]*?\);','',l) for l in lines)+'\n'
    flags=campaign.source.get('state',{}).get('flags',{});quests=campaign.source.get('quests',[])
    watch=[' private int[] watchFlags=new int[]{'+','.join('-1' for f in flags)+'};',' private String[] watchQuests=new String[]{'+','.join('""' for q in quests)+'};',' private void traceState() {']
    for i,(name,index) in enumerate(flags.items()):watch.append(f' int f{i}=CodexSequence.GetChronicleFlag({index})?1:0; if(watchFlags[{i}]!=f{i}) {{ watchFlags[{i}]=f{i}; trace({js("WATCH_FLAG "+name+" ")}+f{i}); }}')
    for i,q in enumerate(quests):
        stem='q/'+q['id']+'/';r=campaign.reserved
        progress='+'.join(f'(CodexSequence.GetChronicleFlag({r[stem+str(k)]})?1:0)' for k in range(len(q['steps']))) or '0'
        watch.append(f' String q{i}=""+({progress})+" "+(CodexSequence.GetChronicleFlag({r[stem+"start"]})?1:0)+" "+(CodexSequence.GetChronicleFlag({r[stem+"done"]})?1:0); if(!q{i}.equals(watchQuests[{i}])) {{ watchQuests[{i}]=q{i}; trace({js("WATCH_QUEST "+q["id"]+" ")}+q{i}); }}')
    watch+=[' }',' private void traceStack(Throwable t) { java.io.StringWriter w=new java.io.StringWriter(); t.printStackTrace(new java.io.PrintWriter(w)); trace("STACK "+w.toString()); }']
    out=[];context=''
    for l in lines:
        if 'private void trace(String s)' in l:l=l.replace('log.println(s);','log.println(System.currentTimeMillis()+"\\t"+s);')
        if '// source:' in l:context=l.split('// source: ')[-1]
        if '// action ' in l:out.append(l);out.append(' trace('+js('ACTION '+context+' '+l.strip()[3:])+');');continue
        if 'trace("runtime exception: "+error);' in l:l=l.replace('trace("runtime exception: "+error);','trace("runtime exception: "+error); traceStack(error);')
        if 'public void beginscene' in l:l=l.replace('player=localPlayer(who);','trace('+js('SCENE '+scene['id'])+'); player=localPlayer(who);')
        if 'public void convended' in l:l=l.replace('int completed=active;','trace("CONVERSATION_END "+active+" return="+result+" aborted="+aborted); int completed=active;')
        if 'if(!transitioning) SetTimer(0.15f,9400);' in l:l=l.replace('if(!transitioning) SetTimer(0.15f,9400);','traceState(); if(!transitioning) SetTimer(0.15f,9400);')
        out.append(l)
    out[-1:-1]=watch
    return '\n'.join(out)+'\n'

def parse_trace(text,source_map=None):
    rows=[];flags={};quests={};spawns={};source_map=source_map or {}
    for line in text.splitlines()[-2000:]:
        m=re.match(r'^(\d{10,})\t(.*)$',line);stamp=int(m[1]) if m else None;body=m[2] if m else line;path=None;severity='ERROR' if 'exception' in body.lower() or 'failed' in body.lower() else 'INFO'
        if body.startswith('WATCH_FLAG '):
            bits=body.split()
            if len(bits)==3 and bits[2] in {'0','1'}:flags[bits[1]]=bits[2]=='1'
        elif body.startswith('WATCH_QUEST '):
            bits=body.split()
            if len(bits)==5 and all(x.isdigit() for x in bits[2:]):quests[bits[1]]={'step':int(bits[2]),'started':bits[3]=='1','complete':bits[4]=='1'}
        elif body.startswith('spawn '):
            m=re.match(r'spawn (\S+) guid=(\d+)',body)
            if m:spawns[m[1]]=int(m[2])
        m=re.search(r'(?:event |SCENE )([a-z0-9_]+)(?:/([a-z0-9_]+))?',body)
        if m:path={'scene':m[1],**({'event':m[2]} if m[2] else {})}
        action=re.search(r'ACTION scene (\w+) event (\w+) action (\d+): (\w+)',body)
        if action:path={'scene':action[1],'event':action[2],'action':int(action[3]),'operation':action[4]}
        dialogue=re.search(r'DIALOGUE_END (\w+)/(\w+) return=(-?\d+) aborted=(true|false)',body)
        if dialogue:path={'scene':dialogue[1],'conversation':dialogue[2],'result':int(dialogue[3]),'aborted':dialogue[4]=='true'}
        persistence=re.match(r'(SAVE_STATE|RESTORE_STATE|RESTORED) (\w+)',body)
        if persistence:path={'scene':persistence[2],'phase':persistence[1]}
        quest=re.match(r'WATCH_QUEST (\w+) ',body)
        if quest:path={'quest':quest[1]}
        frame=re.search(r'\(([^():]+\.java):(\d+)\)',body)
        if frame:path=source_map.get(frame[1],{}).get(frame[2],path)
        rows.append(dict(time=stamp,message=body,severity=severity,context=path))
    return {'events':rows,'flags':flags,'quests':quests,'spawned':spawns,'source':'runtime trace, no live memory access'}
