"""Native encounter control in the existing scene timer and save callbacks."""
import math
from .generator import java_string as js,java_vector as jv
from .dynamic_encounters import phase_event

STATES={'ready':0,'active':1,'paused':2,'complete':3,'stopped':4,'error':5}

def role_index(g,role):
    return list(dict.fromkeys(e['role'] for w in g['waves'] for e in w['groups'])).index(role)

def condition_java(c,scene,entities):
    kind,value=next(iter(c.items()));rows=scene.get('generators',[])
    gi=next((i for i,g in enumerate(rows) if g['id']==value.get('generator')),-1)
    if kind=='generator_state':return f'dState[{gi}]=={STATES[value["state"]]}'
    if kind=='generator_count':
        role=role_index(rows[gi],value['role']) if 'role' in value else -1
        return f'dynamicCount({gi},{js(value["counter"])},{role}){value["comparison"]}{value["value"]}'
    target=f'things[{entities[value["actor"]]}]' if 'actor' in value else f'dynamicRoleGuid({gi},{role_index(rows[gi],value["role"])})'
    return f'dynamicHealth({target},{str("percent" in value).lower()},{float(value.get("percent",value.get("value")))}f,{js(value["comparison"])})'

def extend_dynamic(java,campaign,scene,project):
    rows=scene.get('generators',[]);n=len(rows);entities={e.id:i for i,e in enumerate(project.entities)}
    def replace(old,new):
        nonlocal java
        if java.count(old)!=1:raise ValueError('Dynamic runtime integration ambiguous: '+old[:80])
        java=java.replace(old,new)
    fields=f'''
 private int[] dState=new int[{n}],dWave=new int[{n}],dWait=new int[{n}],dCursor=new int[{n}],dStreamEntry=new int[{n}],dStreamLeft=new int[{n}],dPoint=new int[{n}],dFailures=new int[{n}],dTotal=new int[{n}],dKills=new int[{n}],dCap=new int[{n}],dLimit=new int[{n}],dInterval=new int[{n}],dTarget=new int[{n}],dRetry=new int[{n}],dPolicy=new int[{n}],dCooldown=new int[{n}],dMode=new int[{n}],dFlag=new int[{n}],dStartFlag=new int[{n}],dBossActor=new int[{n}],dBossRole=new int[{n}];
 private boolean[] dWaveOpen=new boolean[{n}],dUnsafe=new boolean[{n}],dRemove=new boolean[{n}],dRandom=new boolean[{n}],dRandomPoint=new boolean[{n}],dNear=new boolean[{n}];
 private int[][] dGuid=new int[{n}][],dSlotEntry=new int[{n}][],dSpawned=new int[{n}][],dRole=new int[{n}][],dEntryWave=new int[{n}][],dCount=new int[{n}][],dWeight=new int[{n}][],dTeam=new int[{n}][],dRoleTotal=new int[{n}][],dRoleKills=new int[{n}][],dDelay=new int[{n}][],dPointSet=new int[{n}][],dPointCount=new int[{n}][];
 private String[][] dTemplate=new String[{n}][],dRoleName=new String[{n}][];
 private String dScene={js(scene["id"])}; private String[] dName=new String[{n}]; private float[][] dHealth=new float[{n}][],dMultiplier=new float[{n}][];
 private boolean[][] dAttached=new boolean[{n}][],dPhasePending=new boolean[{n}][],dPhaseDone=new boolean[{n}][];
 private float[] dBossPrevious=new float[{n}]; private boolean[] dBossSeen=new boolean[{n}];
 private boolean dConfigured=false,dRestoring=false; private int dRestoreWait=0,dBudget=0,dNotifyDepth=0;
'''
    config=[' private void dynamicConfigure() { if(dConfigured) return; dConfigured=true;']+[f' dynamicConfig{i}();' for i in range(n)]+[' }']
    def ints(values):return 'new int[]{'+','.join(str(v) for v in values)+'}'
    def floats(values):return 'new float[]{'+','.join(str(float(v))+'f' for v in values)+'}'
    def strings(values):return 'new String[]{'+','.join(js(v) for v in values)+'}'
    point_sets=[];point_indices=[]
    for g in rows:
        indices=[]
        for group in [e for wave in g['waves'] for e in wave['groups']]:
            keys=tuple(group.get('spawn_points') or g.get('spawn_points',[]))
            if keys not in point_sets:point_sets.append(keys)
            indices.append(point_sets.index(keys))
        point_indices.append(indices)
    for i,g in enumerate(rows):
        groups=[e for w in g['waves'] for e in w['groups']];roles=list(dict.fromkeys(e['role'] for e in groups));cap=g['max_alive']
        waveids=[wi for wi,w in enumerate(g['waves']) for e in w['groups']]
        config += [f' private void dynamicConfig{i}() {{ int g={i};',f' dBossActor[g]={entities.get(g.get("boss",{}).get("actor"),-1)}; dBossRole[g]={roles.index(g["boss"]["role"]) if g.get("boss",{}).get("role") in roles else -1}; dName[g]={js(g["id"])}; dCap[g]={cap}; dLimit[g]={g.get("max_total",0)}; dInterval[g]={math.ceil(g.get("interval",5)/.15)}; dTarget[g]={g.get("target_alive",0)}; dRetry[g]={g.get("retry_limit",3)};',
                   f' dStartFlag[g]={campaign.reserved["generator/"+scene["id"]+"/"+g["id"]+"/started"]}; dMode[g]={1 if g["mode"]=="continuous" else 0}; dPolicy[g]={dict(once=0,resume=1,reset=2,cooldown=3)[g.get("persistence","once")]}; dCooldown[g]={math.ceil(g.get("cooldown",30)/.15)}; dFlag[g]={campaign.reserved["generator/"+scene["id"]+"/"+g["id"]+"/complete"]};',
                   f' dRemove[g]={str(g.get("remove_on_stop",False)).lower()}; dRandom[g]={str(g.get("selection")=="random").lower()}; dRandomPoint[g]={str(g.get("point_selection")=="random").lower()}; dNear[g]={str(g.get("placement")=="near_player").lower()};',
                   f' dAttached[g]=new boolean[{cap}]; dGuid[g]=new int[{cap}]; dSlotEntry[g]=new int[{cap}]; dSpawned[g]=new int[{len(groups)}]; dRoleTotal[g]=new int[{len(roles)}]; dRoleKills[g]=new int[{len(roles)}];',
                   f' dTemplate[g]={strings(e["template"] for e in groups)}; dRoleName[g]={strings(roles)}; dRole[g]={ints(roles.index(e["role"]) for e in groups)}; dEntryWave[g]={ints(waveids)};',
                   f' dCount[g]={ints(e["count"] for e in groups)}; dWeight[g]={ints(e.get("weight",1) for e in groups)}; dTeam[g]={ints(e.get("team",-1) for e in groups)};',
                   f' dHealth[g]={floats(e.get("health",0) for e in groups)}; dMultiplier[g]={floats(e.get("health_multiplier",0) for e in groups)}; dDelay[g]={ints(math.ceil(w.get("delay",0)/.15) for w in g["waves"])};',
                   f' dPointSet[g]={ints(point_indices[i])}; dPointCount[g]={ints(len(point_sets[pi]) for pi in point_indices[i])};',
                   f' dPhasePending[g]=new boolean[{len(g.get("phases",[]))}]; dPhaseDone[g]=new boolean[{len(g.get("phases",[]))}]; }}']
    # Share repeated point sets and partition lookup methods: no method grows
    # with generators × waves × groups × points.
    points=[' private float[] dynamicPosition(int g,int e,int point,boolean orientation) { int set=dPointSet[g][e]; switch(set/32) {']
    pointnames=[' private String dynamicPointName(int g,int e,int point) { int set=dPointSet[g][e]; switch(set/32) {']
    pointcounts=[' private int dynamicPoints(int g,int e) { return dPointCount[g][e]; }']
    markers={p['id']:p for p in scene.get('waypoints',[])}
    for page in range(math.ceil(len(point_sets)/32)):
        points.append(f' case {page}: return dynamicPositionPage{page}(set%32,point,orientation);')
        pointnames.append(f' case {page}: return dynamicNamePage{page}(set%32,point);')
    points+=[' } return null; }'];pointnames+=[' } return "near_player"; }']
    for page in range(math.ceil(len(point_sets)/32)):
        points.append(f' private float[] dynamicPositionPage{page}(int set,int point,boolean orientation) {{ switch(set) {{')
        pointnames.append(f' private String dynamicNamePage{page}(int set,int point) {{ switch(set) {{')
        for offset in range(min(32,len(point_sets)-page*32)):
            pi=page*32+offset;points.append(f' case {offset}: return dynamicCoordinates{pi}(point,orientation);');pointnames.append(f' case {offset}: return dynamicPointLabel{pi}(point);')
        points+=[' } return null; }'];pointnames+=[' } return "near_player"; }']
    for pi,names in enumerate(point_sets):
        points.append(f' private float[] dynamicCoordinates{pi}(int point,boolean orientation) {{ switch(point) {{')
        pointnames.append(f' private String dynamicPointLabel{pi}(int point) {{ switch(point) {{')
        for index,key in enumerate(names):
            t=markers[key]['transform'];points.append(f' case {index}: return orientation?{jv(t["orientation"])}:{jv(t["position"])};');pointnames.append(f' case {index}: return {js(key)};')
        points+=[' } return null; }'];pointnames+=[' } return "near_player"; }']
    phases=[' private void dynamicPhases(int g) { switch(g) {']
    for gi,g in enumerate(rows):
        if g.get('phases'):phases.append(f' case {gi}: dynamicPhase{gi}(g); break;')
    phases.append(' } }')
    for gi,g in enumerate(rows):
        if not g.get('phases'):continue
        boss=g['boss'];target=f'things[{entities[boss["actor"]]}]' if 'actor' in boss else f'dynamicRoleGuid(g,{role_index(g,boss["role"])})'
        phases += [f' private void dynamicPhase{gi}(int g) {{ int who={target}; if(!IsActorGuid(who)||!local(who)) return; float hp=new CodexActor(who).GetActorHealth(),maximum=new CodexActor(who).GetActorMaxHealth(); if(hp<=0.0f || Float.isNaN(hp) || Float.isInfinite(hp) || Float.isNaN(maximum) || Float.isInfinite(maximum)) return; float before=dBossPrevious[g]; if(!dBossSeen[g]) {{ dBossSeen[g]=true; before=hp; }}']
        for pi,phase in enumerate(g['phases']):
            threshold=f'maximum*{float(phase["percent"])/100}f' if 'percent' in phase else f'{float(phase["value"])}f'
            event=phase_event(g['id'],phase['id']);ei=next(i for i,e in enumerate(scene['events']) if e['id']==event)
            marker=campaign.reserved.get('e/'+scene['id']+'/'+event)
            if marker is not None:phases += [f' if(CodexSequence.GetChronicleFlag({marker})) {{ dPhaseDone[g][{pi}]=true; dPhasePending[g][{pi}]=false; }}']
            phases += [f' if(!dPhaseDone[g][{pi}] && before>({threshold}) && hp<=({threshold})) dPhasePending[g][{pi}]=true;',
                       f' if(dPhasePending[g][{pi}]) {{ trace("GENERATOR_THRESHOLD generator="+dName[g]+" role="+{js(boss.get("role",boss.get("actor")))}+" threshold={phase.get("percent",phase.get("value"))}"); if(event{ei}()) {{ dPhasePending[g][{pi}]=false; dPhaseDone[g][{pi}]={str(phase.get("once",True)).lower()}; }} if(transitioning) return; }}']
        phases+=[' dBossPrevious[g]=hp; }']
    code=fields+'\n'.join(config+points+pointnames+pointcounts+phases)+COMMON
    from .combat_difficulty import active
    if active(campaign.source):
        hook='if(dTeam[g][e]>=0) actor.SetActorTeam(dTeam[g][e]);'
        if code.count(hook)!=1:raise ValueError('Difficulty dynamic creation hook missing')
        code=code.replace(hook,hook+' difficultyEnemy(who);')
    code=code.replace('+dName[g]', '+dName[g]+" scene="+dScene')
    replace('ticks++;','ticks++; dynamicPoll(); if(transitioning) return;')
    replace('public void save(int capture) {','public void save(int capture) { dynamicSave();')
    replace('public void restore(int capture) {','public void restore(int capture) { dynamicRestore();')
    replace('player=localPlayer(who); active=-1;','player=localPlayer(who); dynamicBegin(restoredState); active=-1;')
    java=java[:-2]+code+'\n}\n'
    return java

COMMON='''
 private void dynamicNotify(String kind,int g,int wave) { if(dNotifyDepth>=8) { dynamicError(g,"callback cycle"); return; } dNotifyDepth++; try { dispatch(kind,dName[g],wave); } finally { dNotifyDepth--; } }
 private boolean dynamicHealth(int who,boolean percent,float value,String op) { if(!IsActorGuid(who)||!local(who)) return false; CodexActor a=new CodexActor(who); float health=a.GetActorHealth(),max=a.GetActorMaxHealth(); if(percent && max<=0.0f) return false; float limit=percent?max*value/100.0f:value; if(op.equals("<")) return health<limit; if(op.equals("<=")) return health<=limit; if(op.equals(">")) return health>limit; return health>=limit; }
 private int dynamicRoleGuid(int g,int role) { for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && dRole[g][dSlotEntry[g][s]]==role && IsActorGuid(dGuid[g][s]) && new CodexActor(dGuid[g][s]).GetActorHealth()>0.0f) return dGuid[g][s]; return 0; }
 private int dynamicCount(int g,String counter,int role) { dynamicConfigure(); if(counter.equals("wave")) return dState[g]==0?0:dWave[g]+1; if(counter.equals("total")) return role<0?dTotal[g]:dRoleTotal[g][role]; if(counter.equals("killed")) return role<0?dKills[g]:dRoleKills[g][role]; int n=0; for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && (role<0 || dRole[g][dSlotEntry[g][s]]==role)) n++; return n; }
 private boolean dynamicOwned(int g,int s) { int who=dGuid[g][s]; return IsActorGuid(who) && local(who) && dTemplate[g][dSlotEntry[g][s]].equalsIgnoreCase(new CodexThing(who).GetTemplateName()); }
 private void dynamicKilled(int g,int s) { int who=dGuid[g][s],role=dRole[g][dSlotEntry[g][s]]; dGuid[g][s]=0; dAttached[g][s]=false; if(dKills[g]<1000000) dKills[g]++; if(dRoleKills[g][role]<1000000) dRoleKills[g][role]++; ReleaseThing(who); trace("GENERATOR_KILL generator="+dName[g]+" role="+dRoleName[g][role]+" guid="+who); }
 public void killed(int who,int killer,int capture) { dynamicConfigure(); if(NetIsClient()) return; for(int g=0;g<dState.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]==who && who!=0) { if(!IsActorGuid(who) || new CodexActor(who).GetActorHealth()<=0.0f) dynamicKilled(g,s); return; } }
 private boolean dynamicRetire(int g) { for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0) { if(!dynamicOwned(g,s)) return false; int who=dGuid[g][s]; if(!new CodexThing(who).Remove()) return false; ReleaseThing(who); dGuid[g][s]=0; } return true; }
 private void dynamicError(int g,String why) { dState[g]=5; if(why.indexOf("GUID")>=0||why.indexOf("ownership")>=0||why.indexOf("saved")>=0) dUnsafe[g]=true; trace("GENERATOR_ERROR generator="+dName[g]+" reason="+why); }
 private boolean dynamicReset(int g,boolean reentry) { if(dUnsafe[g]) return false; if(dynamicCount(g,"alive",-1)>0 && (!(reentry||dRemove[g]) || !dynamicRetire(g))) return false; dState[g]=0; dWave[g]=0; dWait[g]=0; dCursor[g]=0; dStreamEntry[g]=0; dStreamLeft[g]=0; dPoint[g]=0; dFailures[g]=0; dTotal[g]=0; dKills[g]=0; dWaveOpen[g]=false; dBossSeen[g]=false; for(int p=0;p<dPhasePending[g].length;p++) dPhasePending[g][p]=false; for(int e=0;e<dSpawned[g].length;e++) dSpawned[g][e]=0; for(int r=0;r<dRoleTotal[g].length;r++) { dRoleTotal[g][r]=0; dRoleKills[g][r]=0; } CodexSequence.ClearChronicleFlag(dFlag[g]); CodexSequence.ClearChronicleFlag(dStartFlag[g]); return true; }
 private void dynamicBegin(boolean loading) { dynamicConfigure(); if(loading || dRestoring) return; for(int g=0;g<dState.length;g++) { if(dState[g]==0 && CodexSequence.GetChronicleFlag(dStartFlag[g]) && !CodexSequence.GetChronicleFlag(dFlag[g])) { dUnsafe[g]=true; dynamicError(g,"persistent roster missing"); continue; } if(dPolicy[g]==2 && !dynamicReset(g,true)) dynamicError(g,"reentry ownership"); if(dPolicy[g]==0 && CodexSequence.GetChronicleFlag(dFlag[g])) dState[g]=3; } }
 private boolean dynamicCommand(int g,int command) { dynamicConfigure(); if(NetIsClient()||transitioning||(dUnsafe[g]&&command!=1)) return false; if(command==4) return dynamicReset(g,false); if(command==0) { if(dState[g]==5) return false; if(dState[g]==1||dState[g]==2||dState[g]==3) return true; if(dPolicy[g]==0 && CodexSequence.GetChronicleFlag(dFlag[g])) { dState[g]=3; return true; } if(dState[g]==0 && CodexSequence.GetChronicleFlag(dStartFlag[g]) && !CodexSequence.GetChronicleFlag(dFlag[g])) { dUnsafe[g]=true; dynamicError(g,"persistent roster missing"); return false; } CodexSequence.SetChronicleFlag(dStartFlag[g]); dState[g]=1; if(!dWaveOpen[g]) dWait[g]=dDelay[g][dWave[g]]; trace("GENERATOR_START generator="+dName[g]); dynamicNotify("generator_started",g,0); return true; } if(command==1) { if(dState[g]==4 || dState[g]==3) return true; if(dRemove[g]&&!dynamicRetire(g)) return false; dState[g]=4; trace("GENERATOR_STOP generator="+dName[g]); dynamicNotify("generator_stopped",g,0); return true; } if(command==2) { if(dState[g]==1) { dState[g]=2; trace("GENERATOR_PAUSE generator="+dName[g]); } return true; } if(command==3) { if(dState[g]==2) { dState[g]=1; trace("GENERATOR_RESUME generator="+dName[g]); } return true; } return false; }
 private int dynamicEntry(int g) { if(dMode[g]==1) { if(dStreamLeft[g]>0) return dStreamEntry[g]; if(dRandom[g]) { int sum=0; for(int e=0;e<dWeight[g].length;e++) sum+=dWeight[g][e]; int pick=(int)(Math.random()*sum); for(int e=0;e<dWeight[g].length;e++) { pick-=dWeight[g][e]; if(pick<0) { dStreamEntry[g]=e; dStreamLeft[g]=dCount[g][e]; return e; } } } int cursor=dCursor[g]; dCursor[g]=(cursor+1)%dTemplate[g].length; dStreamEntry[g]=cursor; dStreamLeft[g]=dCount[g][cursor]; return cursor; } for(int e=0;e<dSpawned[g].length;e++) if(dEntryWave[g][e]==dWave[g] && dSpawned[g][e]<dCount[g][e]) return e; return -1; }
 private boolean dynamicSpawn(int g,int e) { int slot=-1; for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]==0) { slot=s; break; } if(slot<0 || player==0 || dBudget<=0) return false; dBudget--; int count=dynamicPoints(g,e),point=count==0?0:(dRandomPoint[g]?(int)(Math.random()*count):dPoint[g]%count); dPoint[g]=(dPoint[g]+1)%Math.max(1,count); String template=dTemplate[g][e]; PreloadTemplate(template); int who=0;
 if(!dNear[g]) who=new CodexWorld(WORLD_CURRENT).CreateThing(template,dynamicPosition(g,e,point,false),dynamicPosition(g,e,point,true));
 if(who==0) who=new CodexThing(player).SpawnThingNear(template,0.0f,0);
 boolean duplicate=false; for(int k=0;k<things.length;k++) if(who!=0&&things[k]==who) duplicate=true; for(int k=0;k<dGuid.length;k++) for(int s=0;s<dGuid[k].length;s++) if(who!=0&&dGuid[k][s]==who) duplicate=true;
 if(duplicate) { dynamicError(g,"factory returned owned GUID"); return false; }
 boolean valid=who!=0 && IsActorGuid(who) && local(who) && template.equalsIgnoreCase(new CodexThing(who).GetTemplateName());
 if(valid&&!dNear[g]) valid=new CodexThing(who).SetPosition(dynamicPosition(g,e,point,false)) && new CodexThing(who).SetOrientation(dynamicPosition(g,e,point,true));
 if(!valid) { if(who!=0&&IsActorGuid(who)&&template.equalsIgnoreCase(new CodexThing(who).GetTemplateName())) new CodexThing(who).Remove(); dFailures[g]++; dWait[g]=2; trace("GENERATOR_SPAWN_FAILED generator="+dName[g]+" template="+template+" point="+dynamicPointName(g,e,point)+" attempt="+dFailures[g]); if(dFailures[g]>=dRetry[g]) dynamicError(g,"spawn retries exhausted"); return false; }
 CodexActor actor=new CodexActor(who); if(dMultiplier[g][e]>0.0f || dHealth[g][e]>0.0f) { float hp=dHealth[g][e]>0.0f?dHealth[g][e]:actor.GetActorHealth()*dMultiplier[g][e],maximum=dHealth[g][e]>0.0f?dHealth[g][e]:actor.GetActorMaxHealth()*dMultiplier[g][e]; actor.SetActorMaxHealth(maximum); actor.SetActorHealth(hp); } if(dTeam[g][e]>=0) actor.SetActorTeam(dTeam[g][e]);
 CodexThing thing=new CodexThing(who); thing.ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); thing.SetThingFlags(THING_FLAG_SAVEALWAYS); dAttached[g][slot]=CaptureThing(who); dGuid[g][slot]=who; dSlotEntry[g][slot]=e; if(dSpawned[g][e]<1000000) dSpawned[g][e]++; if(dTotal[g]<1000000) dTotal[g]++; if(dRoleTotal[g][dRole[g][e]]<1000000) dRoleTotal[g][dRole[g][e]]++; if(dBossRole[g]==dRole[g][e]) { dBossPrevious[g]=actor.GetActorHealth(); dBossSeen[g]=true; } dFailures[g]=0;
 trace("GENERATOR_SPAWN generator="+dName[g]+" wave="+(dWave[g]+1)+" role="+dRoleName[g][dRole[g][e]]+" template="+template+" guid="+who+" point="+dynamicPointName(g,e,point)); return true; }
 private void dynamicComplete(int g) { if(dState[g]==3) return; dState[g]=3; CodexSequence.SetChronicleFlag(dFlag[g]); dWait[g]=dCooldown[g]; trace("GENERATOR_COMPLETE generator="+dName[g]); dynamicNotify("generator_complete",g,0); }
 private void dynamicPoll() { dynamicConfigure(); if(NetIsClient()||transitioning) return; boolean missing=false; for(int g=0;g<dGuid.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0) { if(dynamicOwned(g,s)) { if(!dAttached[g][s]) { ReleaseThing(dGuid[g][s]); dAttached[g][s]=CaptureThing(dGuid[g][s]); } if(new CodexActor(dGuid[g][s]).GetActorHealth()<=0.0f) dynamicKilled(g,s); } else { if(dRestoring) missing=true; else dynamicError(g,"owned GUID missing or nonlocal"); } }
 if(dRestoring) { if(missing && ++dRestoreWait<=20) return; dRestoring=false; if(missing) { for(int g=0;g<dGuid.length;g++) for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0&&!dynamicOwned(g,s)) dynamicError(g,"restored GUID unresolved; no replacement spawned"); } }
 dBudget=4; for(int g=0;g<dState.length;g++) { if(transitioning) return; if(dState[g]==3 && dPolicy[g]==3) { if(dWait[g]>0) { dWait[g]--; continue; } if(dynamicReset(g,false)) dynamicCommand(g,0); } if(dState[g]!=1) continue; dynamicPhases(g); if(transitioning || dState[g]!=1) continue; if(active!=-1||cameraTicks>0||pendingDialogueEnd) continue; if(dWait[g]>0) { dWait[g]--; continue; }
 if(!dWaveOpen[g]) { dWaveOpen[g]=true; trace("GENERATOR_WAVE_START generator="+dName[g]+" wave="+(dWave[g]+1)); dynamicNotify("wave_started",g,dWave[g]+1); if(transitioning||dState[g]!=1) continue; }
 int alive=dynamicCount(g,"alive",-1); if(dMode[g]==1) { if(dLimit[g]>0 && dTotal[g]>=dLimit[g]) { if(alive==0) dynamicComplete(g); continue; } int desired=dTarget[g]>0?dTarget[g]:dCap[g]; if(alive<desired && dBudget>0) { int e=dynamicEntry(g); if(dynamicSpawn(g,e)) { dWait[g]=dInterval[g]; if(dStreamLeft[g]>0) dStreamLeft[g]--; } } continue; }
 int entry=dynamicEntry(g); if(entry>=0 && (dLimit[g]==0 || dTotal[g]<dLimit[g])) { while(dBudget>0 && alive<dCap[g] && entry>=0 && dState[g]==1) { if(!dynamicSpawn(g,entry)) break; alive++; if(dLimit[g]>0&&dTotal[g]>=dLimit[g]) break; entry=dynamicEntry(g); } continue; }
 if(alive==0 && (dBossActor[g]<0 || (IsActorGuid(things[dBossActor[g]]) && local(things[dBossActor[g]]) && new CodexActor(things[dBossActor[g]]).GetActorHealth()<=0.0f))) { trace("GENERATOR_WAVE_COMPLETE generator="+dName[g]+" wave="+(dWave[g]+1)); dynamicNotify("wave_complete",g,dWave[g]+1); if(transitioning||dState[g]!=1) continue; if(dWave[g]+1>=dDelay[g].length || (dLimit[g]>0&&dTotal[g]>=dLimit[g])) dynamicComplete(g); else { dWave[g]++; dWaveOpen[g]=false; dWait[g]=dDelay[g][dWave[g]]; } }
 } }
 private void dynamicSave() { dynamicConfigure(); CodexSequence.SaveInt(1); for(int g=0;g<dState.length;g++) { CodexSequence.SaveInt(dState[g]); CodexSequence.SaveInt(dWave[g]); CodexSequence.SaveInt(dWait[g]); CodexSequence.SaveInt(dCursor[g]); CodexSequence.SaveInt(dStreamEntry[g]); CodexSequence.SaveInt(dStreamLeft[g]); CodexSequence.SaveInt(dPoint[g]); CodexSequence.SaveInt(dFailures[g]); CodexSequence.SaveInt(dTotal[g]); CodexSequence.SaveInt(dKills[g]); CodexSequence.SaveBoolean(dUnsafe[g]); CodexSequence.SaveBoolean(dWaveOpen[g]); CodexSequence.SaveBoolean(dBossSeen[g]); CodexSequence.SaveFloat(dBossPrevious[g]); for(int s=0;s<dGuid[g].length;s++) { CodexSequence.SaveInt(dGuid[g][s]); CodexSequence.SaveInt(dSlotEntry[g][s]); } for(int e=0;e<dSpawned[g].length;e++) CodexSequence.SaveInt(dSpawned[g][e]); for(int r=0;r<dRoleTotal[g].length;r++) { CodexSequence.SaveInt(dRoleTotal[g][r]); CodexSequence.SaveInt(dRoleKills[g][r]); } for(int p=0;p<dPhaseDone[g].length;p++) { CodexSequence.SaveBoolean(dPhaseDone[g][p]); CodexSequence.SaveBoolean(dPhasePending[g][p]); } } }
 private void dynamicRestore() { dynamicConfigure(); int version=CodexSequence.RestoreInt(); dRestoring=true; dRestoreWait=0; for(int g=0;g<dState.length;g++) { dState[g]=CodexSequence.RestoreInt(); dWave[g]=CodexSequence.RestoreInt(); dWait[g]=CodexSequence.RestoreInt(); dCursor[g]=CodexSequence.RestoreInt(); dStreamEntry[g]=CodexSequence.RestoreInt(); dStreamLeft[g]=CodexSequence.RestoreInt(); dPoint[g]=CodexSequence.RestoreInt(); dFailures[g]=CodexSequence.RestoreInt(); dTotal[g]=CodexSequence.RestoreInt(); dKills[g]=CodexSequence.RestoreInt(); dUnsafe[g]=CodexSequence.RestoreBoolean(); dWaveOpen[g]=CodexSequence.RestoreBoolean(); dBossSeen[g]=CodexSequence.RestoreBoolean(); dBossPrevious[g]=CodexSequence.RestoreFloat(); for(int s=0;s<dGuid[g].length;s++) { dGuid[g][s]=CodexSequence.RestoreInt(); dAttached[g][s]=false; dSlotEntry[g][s]=CodexSequence.RestoreInt(); } for(int e=0;e<dSpawned[g].length;e++) dSpawned[g][e]=CodexSequence.RestoreInt(); for(int r=0;r<dRoleTotal[g].length;r++) { dRoleTotal[g][r]=CodexSequence.RestoreInt(); dRoleKills[g][r]=CodexSequence.RestoreInt(); } for(int p=0;p<dPhaseDone[g].length;p++) { dPhaseDone[g][p]=CodexSequence.RestoreBoolean(); dPhasePending[g][p]=CodexSequence.RestoreBoolean(); } for(int s=0;s<dGuid[g].length;s++) if(dGuid[g][s]!=0 && (dSlotEntry[g][s]<0 || dSlotEntry[g][s]>=dTemplate[g].length)) { dGuid[g][s]=0; dSlotEntry[g][s]=0; dynamicError(g,"invalid saved slot ownership"); } if(version!=1 || dState[g]<0||dState[g]>5||dWave[g]<0||dWave[g]>=dDelay[g].length||dPoint[g]<0||dCursor[g]<0||dCursor[g]>=Math.max(1,dTemplate[g].length)||dStreamEntry[g]<0||dStreamEntry[g]>=Math.max(1,dTemplate[g].length)||dStreamLeft[g]<0||dStreamLeft[g]>128||dWait[g]<0||dFailures[g]<0||dTotal[g]<0||dTotal[g]>1000000||dKills[g]<0||dKills[g]>1000000) dynamicError(g,"invalid saved state"); } }
'''
