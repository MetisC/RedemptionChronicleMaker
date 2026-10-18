"""Campaign code generation against inspected Codex signatures; no authoring tools."""
from pathlib import Path
import hashlib,json,math
from .generator import build as build_scene, zip_bytes, java_string as js, java_vector as jv


def runtime(campaign,scene,p):
    name=p.prefix+'_Scene'; entities={e.id:i for i,e in enumerate(p.entities)}; convs={c.id:i for i,c in enumerate(p.conversations)}
    quests={q['id']:q for q in campaign.source.get('quests',[])};groups={g['id']:g for g in scene.get('encounters',[])}
    actors={a['id']:a for a in scene['actors']}
    reserved=campaign.reserved; flags=p.flags
    def item_template(value):
        if '.' not in value:return p.prefix+'_'+value
        sid,eid=value.split('.',1)
        return next(project.prefix+'_'+eid for row,project in campaign.scenes if row['id']==sid)
    def flag(key): return 'CodexSequence.GetChronicleFlag('+str(reserved[key])+')'
    def setflag(key): return 'CodexSequence.SetChronicleFlag('+str(reserved[key])+');'
    def cond(c):
        if 'all' in c:return '('+' && '.join(cond(x) for x in c['all'])+')'
        if 'any' in c:return '('+' || '.join(cond(x) for x in c['any'])+')'
        if 'not' in c:return '!('+cond(c['not'])+')'
        if next(iter(c)) in {'actor_health','generator_state','generator_count'}:
            from .dynamic_runtime import condition_java
            return condition_java(c,scene,entities)
        if 'flag' in c:return ('' if c['is_set'] else '!')+'CodexSequence.GetChronicleFlag('+str(flags[c['flag']])+')'
        if 'quest' in c:
            stem='q/'+c['quest']+'/'
            if 'step' in c:return flag(stem+'start')+' && !'+flag(stem+'done')+' && '+('true' if c['step']==0 else flag(stem+str(c['step']-1)))+' && !'+flag(stem+str(c['step']))
            if c['state']=='not_started': return '!'+flag(stem+'start')
            if c['state']=='complete':return flag(stem+'done')
            return flag(stem+'start')+' && !'+flag(stem+'done')
        k,v=next(iter(c.items()))
        if k=='owns_item':return 'owns(player, '+js(item_template(v))+')'
        i=entities[v]
        if k=='entity_exists':return 'local(things['+str(i)+'])'
        if k=='actor_alive':return 'alive('+str(i)+')'
        return 'owns(player, '+js(p.prefix+'_'+v)+')'
    trace_path=js('RCM/'+campaign.id+'/runtime_trace.log')
    if campaign.source.get('runtime_profile') in ('phase9','phase10'):
        # Redemption's Java 1.1 File stores the path verbatim: getParent only
        # recognises separatorChar. Forward slashes yield null on Windows.
        trace_path+=".replace('/',java.io.File.separatorChar)"
    code=[f'public class {name} extends Codex {{',
          f' private int[] things=new int[{len(entities)}];',f' private boolean[] enabled=new boolean[{len(entities)}];',f' private boolean[] createdOnce=new boolean[{len(entities)}];',
          f' private boolean[] inside=new boolean[{len(p.triggers)}];',f' private boolean[] previous=new boolean[{len(scene["events"])}];',
          ' private int active=-1, starter=0, ticks=0, player=0; private boolean restoredState=false, transitioning=false; private int cameraTicks=0, cameraPlayer=0; private boolean pendingStart=false;',
          f' private void trace(String s) {{ CodexConsole.Print(0,0,"RCM: "+s); try {{ java.io.File current=new java.io.File({trace_path}); new java.io.File(current.getParent()).mkdirs(); if(current.length()>1048576L) {{ java.io.File old=new java.io.File(current.getPath()+".1"); if(old.exists()&&!old.delete()) return; if(!current.renameTo(old)) return; }} java.io.PrintStream log=new java.io.PrintStream(new java.io.FileOutputStream(current.getPath(),true)); log.println(s); log.close(); }} catch(Exception error) {{ CodexConsole.PrintError("RCM trace: "+error); }} }}',
          ' private boolean local(int g) { return g!=0 && (IsPlayerGuid(g)||IsActorGuid(g)||IsItemGuid(g)||IsPropGuid(g)||IsWeaponGuid(g)||IsArmorGuid(g)) && new CodexThing(g).GetLocationNum()==CodexSequence.GetCurrentLocation(); }',
          ' private int localPlayer(int g) { if(IsPlayerGuid(g)&&local(g)) return g; g=CodexPlayer.GetCurrentPlayer(); if(IsPlayerGuid(g)&&local(g)) return g; for(int i=0;i<CodexPlayer.GetNumMPPlayers();i++) { g=CodexPlayer.GetMPPlayer(i); if(IsPlayerGuid(g)&&local(g)) return g; } return 0; }',
          ' private boolean alive(int i) { return IsActorGuid(things[i]) && local(things[i]) && new CodexActor(things[i]).GetActorHealth()>0.0f; }',
          ' private int inventory(int owner,String template) { if(!IsActorGuid(owner)) return 0; int item=new CodexActor(owner).GetActorFirstInventoryItem(); for(int n=0;item!=0 && n<4096;n++) { if(template.equalsIgnoreCase(new CodexThing(item).GetTemplateName())) return item; item=new CodexItem(item).GetNextInventoryItem(); } return 0; }',
          ' private boolean owns(int owner,String template) { return inventory(owner,template)!=0; }',
          ' private boolean give(int i,int owner) { if(!IsActorGuid(owner)) return false; if(owns(owner,template(i))) return true; int item=things[i]; if(!IsItemGuid(item)&&!IsWeaponGuid(item)&&!IsArmorGuid(item)) item=new CodexThing(owner).SpawnThingNear(template(i),0.0f,0); if(item==0) return false; if(!new CodexActor(owner).AddToActorInventory(item)) { new CodexThing(item).Remove(); return false; } new CodexThing(item).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(item).SetThingFlags(THING_FLAG_SAVEALWAYS); things[i]=item; createdOnce[i]=true; return true; }',
          ' private String template(int i) { switch(i) {']
    for eid,i in entities.items():code.append(f' case {i}: return {js(p.prefix+"_"+eid)};')
    code+=[' } return ""; }',' private void spawn(int i) { if(local(things[i]) || createdOnce[i]) return; things[i]=CodexThing.GuidFromCastID(template(i)); boolean fresh=!local(things[i]); if(fresh) { switch(i) {']
    for e in p.entities:
        i=entities[e.id]
        creation=(f'new CodexThing(player).SpawnThingNear(template({i}),0.0f,0)' if e.transform.placement=='near_player' else f'new CodexWorld(WORLD_CURRENT).CreateThing(template({i}),{jv(e.transform.position)},{jv(e.transform.orientation)})')
        code += [f' case {i}:', (' if(player==0) return;' if e.transform.placement=='near_player' else ''), f' things[{i}]={creation}; break;']
    code+=[' } } if(!local(things[i])) return; if(fresh) { switch(i) {']
    for e in p.entities:
        if e.transform.placement=='near_player':code += [f' case {entities[e.id]}: new CodexThing(things[i]).SetOrientation({jv(e.transform.orientation)}); break;']
    code += [' } } createdOnce[i]=true; new CodexThing(things[i]).ClearThingFlags(THING_FLAG_SAVENEVER|THING_FLAG_SAVESUSPEND); new CodexThing(things[i]).SetThingFlags(THING_FLAG_SAVEALWAYS); CaptureThing(things[i],i+1); switch(i) {']
    for eid,a in actors.items():
        i=entities[eid]; enemy=a.get('behavior','npc')=='enemy'
        code += [f' case {i}: new CodexActor(things[i]).SetActorTeam({"TEAM_ENEMY0" if enemy else "TEAM_PEDESTRIANS"});',
                 f' new CodexActor(things[i]).{"ClearActorFlags" if enemy else "SetActorFlags"}(THING_AF_AIPAUSED|THING_AF_NEUTRAL);']
        if a.get('conversation') or any(e.get('actor')==eid and e['when']=='actor_clicked' for e in scene['events']):code += [f' new CodexActor(things[i]).SetActorFlags(THING_AF_TALKTO);']
        for it in a.get('inventory',[]):code += [f' if(!give({entities[it]},things[i])) trace("inventory failed {it}");']
        from .wtd import actor_java
        code += actor_java(a,'things['+str(i)+']')
        code += [' break;']
    code += [' } trace("spawn "+template(i)+" guid="+things[i]); }',
             ' public void beginscene(int who,int capture) { if(NetIsClient()) return; player=localPlayer(who); active=-1; starter=0; transitioning=false; if(!restoredState) { ticks=0; pendingStart=true; } restoredState=false; poll(); }',
             ' public void timer(int id,float a,float b,float c,float d) { if(id==9400&&!NetIsClient()&&!transitioning) poll(); }',
             ' private void poll() { try { pollImpl(); } catch(Throwable error) { trace("runtime exception: "+error); SetTimer(0.15f,9400); } } private void pollImpl() { player=localPlayer(player); if(pendingStart && player!=0) { pendingStart=false; dispatch("scene_start","",0); } if(transitioning) return; ticks++; if(cameraTicks>0 && --cameraTicks==0) releaseCamera(); for(int i=0;i<enabled.length;i++) if(enabled[i]) spawn(i); if(player!=0 && active==-1 && !transitioning) {']
    for ti,t in enumerate(p.triggers):
        code += [f' boolean now{ti}=volume({ti}); if(now{ti}&&!inside[{ti}]) dispatch("trigger_enter",{js(t.id)},0); if(!now{ti}&&inside[{ti}]) dispatch("trigger_leave",{js(t.id)},0); inside[{ti}]=now{ti};']
    for ei,e in enumerate(scene['events']):
        w=e['when']; test=None
        if w=='actor_killed': test=f'createdOnce[{entities[e["actor"]]}] && IsActorGuid(things[{entities[e["actor"]]}]) && new CodexActor(things[{entities[e["actor"]]}]).GetActorHealth()<=0.0f'
        elif w=='item_picked_up':test=f'owns(player,{js(p.prefix+"_"+e["item"])})'
        elif w=='encounter_complete':test=' && '.join(f'createdOnce[{entities[a]}] && IsActorGuid(things[{entities[a]}]) && new CodexActor(things[{entities[a]}]).GetActorHealth()<=0.0f' for a in groups[e['encounter']]['actors'])
        elif w=='timer':test=f'ticks*0.15f>={float(e["seconds"])}f'
        elif w=='state_changed':test=' && '.join(cond(c) for c in e['conditions']) or 'true'
        if test:
            if w=='timer' and not e.get('once',True):
                code += [f' if(ticks % {math.ceil(e["seconds"]/.15)} == 0) event{ei}();']
                continue
            if campaign.source.get('runtime_profile') in ('phase9','phase10'):
                code += [f' boolean matched{ei}=({test}); if(!matched{ei}) previous[{ei}]=false; else if(!previous[{ei}]) previous[{ei}]=event{ei}();']
            else:code += [f' boolean matched{ei}=({test}); if(matched{ei}&&!previous[{ei}]) event{ei}(); previous[{ei}]=matched{ei};']
    code+=[' } if(!transitioning) SetTimer(0.15f,9400); }',' private boolean volume(int which) { for(int n=-1;n<CodexPlayer.GetNumMPPlayers();n++) { int g=n==-1?player:CodexPlayer.GetMPPlayer(n); if(!IsPlayerGuid(g)||!local(g)) continue; float[] v=new CodexThing(g).GetPosition(); switch(which) {']
    for ti,t in enumerate(p.triggers):
        theta=math.radians(t.transform.orientation[2]);co,si=math.cos(theta),math.sin(theta)
        test=f'x*x+y*y+z*z<={t.radius*t.radius}' if t.shape=='sphere' else f'Math.abs({co}*x+{si}*y)<={t.size[0]/2} && Math.abs({-si}*x+{co}*y)<={t.size[1]/2} && Math.abs(z)<={t.size[2]/2}'
        code += [f' case {ti}: {{ double x=v[0]-({t.transform.position[0]}),y=v[1]-({t.transform.position[1]}),z=v[2]-({t.transform.position[2]}); if({test}) return true; break; }}']
    code+=[' } } return false; }',' private void dispatch(String kind,String target,int result) { if(transitioning) return;']
    for ei,e in enumerate(scene['events']):
        if e['when'] not in {'scene_start','actor_clicked','object_clicked','note_closed','conversation_ended','trigger_enter','trigger_leave','sequence_ended','generator_started','wave_started','wave_complete','generator_complete','generator_stopped','generator_threshold'}: continue
        fk={'object_clicked':'object','actor_clicked':'actor','conversation_ended':'conversation','trigger_enter':'trigger','trigger_leave':'trigger','sequence_ended':'sequence'}.get(e['when'])
        test=f'kind.equals({js(e["when"])})'+(f' && target.equals({js(e[fk])})' if fk else '')+(f' && result=={e["result"]}' if 'result' in e else '')
        if 'generator' in e:
            target=e['generator']+('/'+e['phase'] if 'phase' in e else '')
            test+=f' && target.equals({js(target)})'+(f' && result=={e["wave"]}' if 'wave' in e else '')
        extra=' || kind.equals("object_clicked")' if campaign.source.get('runtime_profile') in ('phase9','phase10') else ''
        code+=[f' if({test}) {{ if(event{ei}() && (transitioning || kind.equals("actor_clicked"){extra})) return; }}']
    code+=[' }']
    for ei,e in enumerate(scene['events']):
        marker='e/'+scene['id']+'/'+e['id'];once=marker in reserved
        guards=['transitioning']+([flag(marker)] if once else [])
        check=' && '.join(cond(c) for c in e.get('conditions',[])) or 'true'
        progress_marker='progress/'+scene['id']+'/'+e['id']
        if progress_marker in reserved:check='('+flag(progress_marker)+' || ('+check+'))'
        code += [f' // source: scene {scene["id"]} event {e["id"]}',f' private boolean event{ei}() {{ if('+ ' || '.join(guards)+f' || !({check})) return false;']
        if progress_marker in reserved:code+=[' '+setflag(progress_marker)]
        for ai,a in enumerate(e['actions']):
            k,v=next(iter(a.items()));statement=''
            if k=='spawn':
                statement=f'enabled[{entities[v]}]=true; spawn({entities[v]});'
                if campaign.source.get('runtime_profile') in ('phase9','phase10'):statement+=f' if(!createdOnce[{entities[v]}]) return false;'
            elif k=='remove':statement=f'if(local(things[{entities[v]}])) new CodexThing(things[{entities[v]}]).Remove(); enabled[{entities[v]}]=false;'
            elif k in ('set_flag','clear_flag'):statement=f'CodexSequence.{"SetChronicleFlag" if k=="set_flag" else "ClearChronicleFlag"}({flags[v]});'
            elif k in ('start_quest','advance_quest','complete_quest'):statement=f'if(!quest({js(v)},{["start_quest","advance_quest","complete_quest"].index(k)})) return false;'
            elif k=='give_item':statement=f'if(!give({entities[v]},player)) {{ trace("item reward failed"); return false; }}'
            elif k=='take_item':statement=f'{{ int item=inventory(player,{js(item_template(v))}); if(item!=0) {{ new CodexItem(item).RemoveItemFromInventory(); new CodexThing(item).Remove(); }} }}'
            elif k=='reward_xp':statement=f'if(!IsPlayerGuid(player)) return false; new CodexPlayer(player).AwardPlayerExperience({v});'
            elif k in ('spawn_encounter','remove_encounter'):
                statement=' '.join(f'enabled[{entities[a]}]=true; spawn({entities[a]});' if k=='spawn_encounter' else f'if(local(things[{entities[a]}])) new CodexThing(things[{entities[a]}]).Remove(); enabled[{entities[a]}]=false;' for a in groups[v]['actors'])
            elif k=='start_conversation':statement=f'if(!conversation({convs[v]})) return false;'
            elif k=='show_note':
                from .notes import note_id
                statement=f'if(!showNote({js(note_id(p.prefix,ei,ai))})) return false;'
            elif k=='jump':statement=f'if({js(v)}.equals({js(scene["id"])})) {{ trace("SELF_LINK_BLOCKED"); return false; }}' if v==scene['id'] else f'releaseCamera(); transitioning=true; KillTimer(9400); CodexSequence.Jump({js(v)},0);'
            elif k=='travel':statement=f'if(!travel({js(v["scene"])},{js(v["entry"])})) return false;'
            elif k=='run_event':statement=f'if(!event{next(i for i,row in enumerate(scene["events"]) if row["id"]==v)}()) return false; if(transitioning) return true;'
            elif k=='start_patrol':statement=f'if(!startPatrol({next(i for i,row in enumerate(scene["paths"]) if row["id"]==v)})) return false;'
            elif k=='stop_patrol':statement=f'stopPatrol({entities[v]});'
            elif k in ('open_exit','close_exit'):statement=f'if(!CodexSequence.IsExitValid({js(v)},0)) {{ trace("EXIT_FAILED "+{js(v)}); return false; }} CodexSequence.{"OpenExit" if k=="open_exit" else "CloseExit"}({js(v)},0);'
            elif k=='control_door':
                call=f'door.MoveToFrame({v["frame"]},{float(v["parameter"])}f)' if v['mode']=='frames' else f'door.RotatePivot({v["frame"]},{float(v["parameter"])*(1 if v["open"] else -1)}f)'
                statement=f'{{ int guid=CodexThing.GuidFromCastID({js(v["cast_id"])}); if(!local(guid)) {{ trace("DOOR_FAILED missing/local cast ID"); return false; }} CodexThing door=new CodexThing(guid); if(!door.HasFrames() || door.GetNumFrames()<={v["frame"]} || !{call}) {{ trace("DOOR_FAILED frame/motion"); return false; }} }}'
            elif k=='control_original':
                from .original_objects import targets,key,OPERATIONS
                index=list(targets(scene)).index(key(v))
                statement=f'if(!originalApply({index},{OPERATIONS.index(v["operation"])},{v.get("frame",0)},{float(v.get("parameter",1))}f,{str(v.get("open",True)).lower()})) return false;'
            elif k in ('set_actor_clan','set_discipline'):
                guid='player' if v['actor']=='Player' else 'things['+str(entities[v['actor']])+']'
                call='SetActorClan('+js(v['clan'])+')' if k=='set_actor_clan' else 'SetActorDisciplineLevel('+js(v['discipline'])+','+str(v['level'])+')'
                statement=f'if(!local({guid}) || !(IsActorGuid({guid})||IsPlayerGuid({guid})) || !new CodexActor({guid}).{call}) {{ trace("ACTOR_TRAIT_FAILED"); return false; }}'
            elif k=='play_sound':
                point=next(r for r in scene['waypoints'] if r['id']==v['waypoint'])
                statement=f'new CodexSound({js(v["resource"]+".wav")},{float(v["min_distance"])}f,{float(v["max_distance"])}f,{v["volume"]},0,0,{jv(point["transform"]["position"])});'
            elif k=='start_music':statement=f'CodexSound.StartMusic({js(v)},100);'
            elif k=='start_ambient':statement=f'CodexSound.StartAmbient({js(v)},100);'
            elif k in ('stop_music','stop_ambient'):statement=f'CodexSound.{"StopMusic" if k=="stop_music" else "StopAmbient"}();'
            elif k=='release_camera':statement='releaseCamera();'
            elif k=='play_sequence':
                seq=next(x for x in scene['sequences'] if x['id']==v);shot={'medium':'MS','close':'CU','wide':'WS'}[seq['shot']]
                statement='' if seq['actor']=='Player' else f'if(!alive({entities[seq["actor"]]}) || player==0 || active!=-1) return false; CodexCamera.SetupCutscene(player,things[{entities[seq["actor"]]}],0); CodexCamera.ShotType(CAMERA_SHOT_{shot}); CodexCamera.ShotAngle(CAMERA_ANGLE_{seq["angle"].upper()}); cameraPlayer=player; cameraTicks={math.ceil(seq["duration"]/.15)};'
                if 'preset' in seq and seq['actor']!='Player':
                    from .camera_presets import shot_arguments
                    args=shot_arguments(seq['preset'],seq['angle'])
                    statement=f'if(!alive({entities[seq["actor"]]}) || player==0 || active!=-1) return false; CodexCamera.SetupCutscene(player,things[{entities[seq["actor"]]}],player); CodexCamera.SetShot(player,{args},0,0.3f); cameraPlayer=player; cameraTicks={math.ceil(seq["duration"]/.15)};'
                if any(k in seq for k in ('steps','camera_path','move_path','prop_motion')):
                    statement=f'if(!beginCinema({scene["sequences"].index(seq)})) return false;'
            elif k in ('enable_ai','disable_ai'):statement=f'if(IsActorGuid(things[{entities[v]}])) new CodexActor(things[{entities[v]}]).{"ClearActorFlags" if k=="enable_ai" else "SetActorFlags"}(THING_AF_AIPAUSED);'
            elif k in ('start_generator','stop_generator','pause_generator','resume_generator','reset_generator'):
                gi=next(i for i,g in enumerate(scene['generators']) if g['id']==v)
                statement=f'if(!dynamicCommand({gi},{["start_generator","stop_generator","pause_generator","resume_generator","reset_generator"].index(k)})) return false;'
            action_marker='action/'+scene['id']+'/'+e['id']+'/'+str(ai)
            if action_marker in reserved:
                statement='if(!'+flag(action_marker)+') { '+statement+' '+setflag(action_marker)+' }'
            code += [f' // action {ai+1}: {k}', ' '+statement]
        code+=[' '+(setflag(marker) if once else ''), *([' CodexSequence.ClearChronicleFlag('+str(reserved[progress_marker])+');'] if progress_marker in reserved else []),f' trace({js("event "+scene["id"]+"/"+e["id"])}); return true; }}']
    code += [' private void releaseCamera() { if(cameraPlayer!=0) CodexCamera.Release(cameraPlayer); cameraPlayer=0; cameraTicks=0; }',
             ' private boolean conversation(int index) { if(active!=-1 || !IsPlayerGuid(player)) return false; releaseCamera(); boolean ok=false; int conversationPlayer=player; active=index; starter=conversationPlayer; try { switch(index) {']
    for c in p.conversations:
        cid=p.prefix+'_'+c.id
        code+=[f' case {convs[c.id]}: if(alive({entities[c.speaker]})) ok=ExecuteConversation(conversationPlayer,0,{js(cid)},{js(cid+".nco")},CONV_XFLAG_WANTFEEDBACK|CONV_XFLAG_ALLOWABORT); break;']
    code+=[' } } catch(Throwable error) { trace("conversation failed: "+error); } if(!ok && active==index && starter==conversationPlayer) { active=-1; starter=0; CodexCamera.Release(conversationPlayer); cameraPlayer=0; cameraTicks=0; trace("conversation failed to start"); } return ok; }',
             ' public void clicked(int target,int clicker,int capture) { if(NetIsClient()||active!=-1||transitioning||!IsPlayerGuid(clicker)||!local(clicker)) return; player=clicker;']
    for eid,i in entities.items():
        kind='object_clicked' if eid not in actors and campaign.source.get('runtime_profile') in ('phase9','phase10') else 'actor_clicked'
        code+=[f' if(target==things[{i}]) {{ dispatch({js(kind)},{js(eid)},0);']
        e=next(e for e in p.entities if e.id==eid)
        if e.conversation:
            select=str(convs[e.conversation]) if not e.when_flag else f'CodexSequence.GetChronicleFlag({flags[e.when_flag]})?{convs[e.after_conversation]}:{convs[e.conversation]}'
            code+=[f' if(active==-1) conversation({select});']
        code+=[' return; }']
    code+=[' }',' public void convreached(int who,int event,int line,int speaker,int capture) { if(active==-1||who!=starter) return; int target=local(speaker)?speaker:0; if(target==0) { switch(active) {']
    for c in p.conversations:code+=[f' case {convs[c.id]}: target=things[{entities[c.speaker]}]; break;']
    code+=[' } } trace("CONVERSATION_LINE "+active+" player="+who+" speaker="+speaker+" target="+target); if(local(target)) { CodexCamera.SetupCutscene(who,target,0); cameraPlayer=who; cameraTicks=0; } }',
           ' public void convended(int who,boolean aborted,int result) { if(active==-1||who!=starter) return; int completed=active; active=-1; starter=0; CodexCamera.Release(who); cameraPlayer=0; cameraTicks=0; player=who; if(aborted) return; switch(completed) {']
    for c in p.conversations:
        code+=[f' case {convs[c.id]}: switch(result) {{']
        for ch in c.choices:
            if ch.result is not None:
                code+=[f' case {ch.result}: '+(f'CodexSequence.{"SetChronicleFlag" if ch.value else "ClearChronicleFlag"}({flags[ch.flag]}); ' if ch.flag else '')+f'dispatch("conversation_ended",{js(c.id)},result); break;']
        code+=[' } break;']
    code+=[' } }',' private boolean completeEntry(String name) { int q=CodexQuest.Load(name); if(q<0) return false; new CodexQuest(q).Complete(); return true; }',' private boolean quest(String id,int action) {']
    for qi,(qid,q) in enumerate(quests.items()):
        stem='q/'+qid+'/';qn='R_'+campaign.id+'_q'+str(qi)
        code += [f' if(id.equals({js(qid)})) {{',f' if(action==0) {{ if({flag(stem+"start")}) return true;',f' if(CodexQuest.Load({js(qn)})<0 || CodexQuest.Load({js(qn+"s0")})<0) {{ trace("quest load failed"); return false; }}',setflag(stem+'start'),' return true; }',f' if(action==1 && {flag(stem+"start")} && !{flag(stem+"done")}) {{']
        for st in range(len(q['steps'])):
            code += [(' if' if st==0 else ' else if')+f'(!{flag(stem+str(st))}) {{ if(!completeEntry({js(qn+"s"+str(st))})) return false; '+(f' if(CodexQuest.Load({js(qn+"s"+str(st+1))})<0) return false;' if st+1<len(q['steps']) else '')+setflag(stem+str(st))+' return true; }']
        code+=[' return false; }',f' if(action==2 && {flag(stem+"done")}) return true;',f' if(action==2 && {flag(stem+"start")} && '+ ' && '.join(flag(stem+str(st)) for st in range(len(q['steps'])))+f') {{ if(!completeEntry({js(qn)})) return false; '+setflag(stem+'done')+(f' if(IsPlayerGuid(player)) new CodexPlayer(player).AwardPlayerExperience({q.get("reward_xp",0)});' if q.get('reward_xp',0) else '')+' return true; } return false; }']
    code+=[' return false; }',' public void save(int capture) { for(int i=0;i<things.length;i++) { CodexSequence.SaveInt(things[i]); CodexSequence.SaveBoolean(enabled[i]); CodexSequence.SaveBoolean(createdOnce[i]); } for(int i=0;i<previous.length;i++) CodexSequence.SaveBoolean(previous[i]); CodexSequence.SaveInt(ticks); }',
           ' public void restore(int capture) { for(int i=0;i<things.length;i++) { things[i]=CodexSequence.RestoreInt(); enabled[i]=CodexSequence.RestoreBoolean(); createdOnce[i]=CodexSequence.RestoreBoolean(); } for(int i=0;i<previous.length;i++) previous[i]=CodexSequence.RestoreBoolean(); ticks=CodexSequence.RestoreInt(); restoredState=true; }',
           ' public void restored(int capture) { if(NetIsClient()) return; active=-1; starter=0; transitioning=false; releaseCamera(); for(int i=0;i<inside.length;i++) inside[i]=false; player=localPlayer(0); poll(); }','}']
    java='\n'.join(code)+'\n'
    if campaign.source.get('runtime_profile') in ('phase9','phase10'):
        from .runtime9 import extend
        java=extend(java,campaign,scene,p)
    if campaign.source.get('runtime_profile')=='phase10':
        from .dynamic_runtime import extend_dynamic
        java=extend_dynamic(java,campaign,scene,p)
    from .original_runtime import extend as extend_original
    java=extend_original(java,campaign,scene)
    from .click_interactions import extend as extend_clicks,guard_events
    java=extend_clicks(java,scene,p)
    return name,guard_events(java,scene)


def build_campaign(ws,campaign,levels,resources,hints,compile_java=True,progress=None,runtime_transform=None):
    progress=progress or (lambda x:None); root=Path('build')/campaign.id
    # Invalidate final output first, so a failed scene cannot expose an old build.
    for suffix in ['.nob','_distribution.zip']:
        previous=ws.output(root/(campaign.id+suffix))
        if previous.exists(): previous.unlink()
    payload={}; meta=[]; locations=[]; versions={}; source_map={}; environments={}
    for scene,p in campaign.scenes:
        progress('Escena: '+scene['id'])
        def make_runtime(model):
            name,java=runtime(campaign,scene,model)
            if runtime_transform:java=runtime_transform(java,campaign,scene)
            ws.write(root/'generated/java'/(name+'.java'),java)
            context=None;mapping={}
            for n,line in enumerate(java.splitlines(),1):
                if '// source:' in line:context={'scene':scene['id'],'event':line.split(' event ')[-1]}
                elif '// action ' in line and context:
                    context={**context,'action':int(line.split('// action ')[1].split(':')[0])}
                elif line.startswith(' private ') and 'private boolean event' not in line:context=None
                if context:mapping[str(n)]=dict(context)
            source_map[name+'.java']=mapping
            ws.write(root/'source_map.json',json.dumps(source_map,indent=2))
            return name,java
        make_runtime.click_objects=[o for o in scene.get('objects',[]) if 'interaction' in o]
        from .native_arrivals import enabled as native_arrivals_enabled
        make_runtime.native_arrivals=scene if native_arrivals_enabled(campaign,scene) else None
        try:
            report=build_scene(ws,p,levels,resources,hints,compile_java,progress,make_runtime)
        except ValueError as error:
            import re
            log=ws.output(Path('build')/p.id/'compiler.log')
            match=re.search(r'\d+\. ERROR .*?\(at line (\d+)\)',log.read_text(encoding='utf8'),re.S) if log.exists() else None
            context=source_map.get(p.prefix+'_Scene.java',{}).get(match.group(1)) if match else None
            if context:raise ValueError('Escena '+context['scene']+' → Evento '+context['event']+' → Acción '+str(context.get('action','?'))+': '+str(error)) from error
            raise
        subroot=Path('build')/p.id
        environments[scene['id']] = {**report['environment_profile'], 'sky_override':report['sky_override']}
        for path in report['files']:
            if path.startswith('chronicles/') and path.endswith('.nsc'):continue
            payload[path]=ws.output(subroot/'runtime'/path).read_bytes()
            if path.endswith('.nmf'): meta+=payload[path].decode('cp1252').splitlines()
        versions.update(report['class_versions'])
        ref=levels[p.level]['references'][0]
        locations.append(f"location {scene['id']} {levels[p.level]['nil']} {p.prefix}.nsd {ref['map_ui']} {ref['map_label']} {hex(0x20 | (int(ref['flags'],0)&0x40))}")
        java=ws.output(subroot/'generated/java'/(p.prefix+'_Scene.java')).read_text(encoding='utf8')
        ws.write(root/'generated/java'/(p.prefix+'_Scene.java'),java)
        ws.write(root/'generated/java'/(p.prefix+'_Passive.java'),ws.output(subroot/'generated/java'/(p.prefix+'_Passive.java')).read_bytes())
    order=[x for x in locations if x.split()[1]==campaign.source['entry']]+[x for x in locations if x.split()[1]!=campaign.source['entry']]
    prefix='R_'+campaign.id
    payload['chronicles/'+campaign.id+'.nsc']=('\r\n'.join(['# RCM campaign',*order,'metafile '+prefix+'.nmf','reviveloc '+campaign.source['entry']+' 0','flags 0x3'])+'\r\n').encode('cp1252')
    payload['chronicles/'+prefix+'.nmf']=('\r\n'.join(dict.fromkeys(meta))+'\r\n').encode('cp1252')
    nls=[campaign.id+' '+campaign.name]
    for qi,q in enumerate(campaign.source.get('quests',[])):
        qn=prefix+'_q'+str(qi)
        entries=[(qn,q['title'],q['description']+' Objetivos: '+'; '.join(q['steps']))]+[(qn+'s'+str(i),q['title']+' / '+str(i+1),step) for i,step in enumerate(q['steps'])]
        for name,title,desc in entries:
            payload['quests/'+name+'.nqd']=f'QUEST 0 0 {name}S {name}L QuestCheck.tga 0\r\n'.encode('cp1252')
            nls += [name+'S '+title,name+'L '+desc]
    payload['strings/_'+prefix+'.nls']=('\r\n'.join(nls)+'\r\n').encode('cp1252')
    payload['chronicles/'+prefix+'.nmf']+=('NLS _'+prefix+'.nls\r\n').encode('cp1252')
    from .notes import encode_notes,note_id
    notes=[(note_id(p.prefix,ei,ai),a['show_note']) for scene,p in campaign.scenes for ei,e in enumerate(scene['events']) for ai,a in enumerate(e['actions']) if 'show_note' in a]
    if notes:
        payload['strings/'+prefix+'.ntx']=encode_notes(notes)
        payload['chronicles/'+prefix+'.nmf']+=('NTX '+prefix+'.ntx\r\n').encode('cp1252')
    # Keep the diagnostic runtime tree in sync as well as the published bundle.
    # This prevents a removed conversation/resource from being mistaken for a
    # current generated input during later inspections or deployments.
    old=ws.output(root/'build_report.json')
    if old.exists():
        for path in json.loads(old.read_text(encoding='utf8')).get('files',{}):
            relative=Path(path)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Ruta insegura en informe de build anterior')
            previous=ws.output(root/'runtime'/relative)
            if path not in payload and previous.is_file():
                previous.unlink()
    for path,data in payload.items():ws.write(root/'runtime'/path,data)
    nob=zip_bytes({k:v for k,v in payload.items() if not k.startswith('codex/')})
    distribution={campaign.id+'.nob':nob,**{k:v for k,v in payload.items() if k.startswith('codex/')}}
    ws.write(root/(campaign.id+'.nob'),nob)
    # Clean stale generated bundle entries only using the previous manifest.
    old=ws.output(root/'build_report.json')
    if old.exists():
        for path in json.loads(old.read_text(encoding='utf8')).get('distribution_files',{}):
            if path not in distribution:
                target=ws.output(root/'bundle'/path)
                if target.is_file():target.unlink()
    for path,data in distribution.items():ws.write(root/'bundle'/path,data)
    if compile_java:ws.write(root/(campaign.id+'_distribution.zip'),zip_bytes(distribution))
    report={'chronicle':campaign.id,'status':'compiled-unverified-in-game' if compile_java else 'generated-uncompiled',
        'scenes':[s['id'] for s,p in campaign.scenes],'class_versions':versions,'geometry_in_package':False,
        'files':{k:{'sha256':hashlib.sha256(v).hexdigest(),'size':len(v)} for k,v in sorted(payload.items())},
        'distribution_files':{k:{'sha256':hashlib.sha256(v).hexdigest(),'size':len(v)} for k,v in sorted(distribution.items())},
        'native_engine_test':False,'reserved_flags':campaign.reserved,'environment_profiles':environments}
    ws.write(root/'source_map.json',json.dumps(source_map,indent=2));ws.write(root/'model.json',json.dumps(campaign.source,ensure_ascii=False,indent=2))
    ws.write(root/'build_report.json',json.dumps(report,ensure_ascii=False,indent=2));return report

