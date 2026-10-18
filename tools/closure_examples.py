"""One optional Showcase lab and one coherent acceptance chronicle, no gameplay."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.paths import Workspace
from rcm.service import Backend,source_text
from rcm.input_limits import parse_source
from rcm.original_objects import catalogue,selector
from rcm.click_interactions import target_mesh


def transform(position,yaw=0):return dict(position=position,orientation=[0,0,yaw])


def scene(backend,sid,destination,entry):
    target=next(r for r in catalogue(backend,'RaveClub') if r.get('mesh_offset')==6800)
    position,orientation,interaction=target_mesh(backend,target)
    door=dict(id='refuge_door',name='Refuge',template='tracker_thing',transform=dict(position=position,orientation=orientation),interaction=interaction)
    speech=lambda text,actions=None:dict(text=text,**({'actions':actions} if actions else {}))
    converse=lambda cid,text,choices,actions=None:dict(id=cid,speaker='mentor',camera='ots_speaker_close',entry='hello',nodes=[dict(id='hello',lines=[speech(text,actions)],choices=[dict(text=t,result=r) for t,r in choices])])
    path_id='rcm_refuge_cam'
    s=dict(id=sid,level=dict(source='RaveClub',name='The refuge'),default_entry='safe',entries=[dict(id='safe',name='Arrival outside the refuge',transform=transform([365,-976,-512],90))],
        actors=[dict(id='mentor',name='Elena',template='Anezka',transform=transform([300,-850,-512],180)),
                dict(id='guard',name='Keeper of the refuge',template='LonCiv2',transform=transform([430,-900,-512],180)),
                dict(id='rat',name='A rat in the refuge',template='Rat',behavior='enemy',transform=transform([600,-750,-512],180))],
        objects=[door],triggers=[],encounters=[],waypoints=[dict(id='guard_a',name='Guard departure',transform=transform([430,-900,-512])),dict(id='guard_b',name='Guard destination',transform=transform([430,-780,-488])),dict(id='noise',name='Distant sound',transform=transform([600,-750,-512]))],
        paths=[dict(id='guard_walk',name='The guard crosses the room',actor='guard',points=['guard_a','guard_b'],loop=False,speed=60,tolerance=24)],
        conversations=[converse('welcome','Come in. The keeper will make sure the refuge is safe. Stay with me; it should only take a moment.',[('I am ready.',1),('Skip the film and continue.',2)],[{'camera_shot':dict(actor='mentor',reference='Player',preset='ots_speaker_close')},{'look_at':dict(actor='mentor',target='Player')},{'play_motion':dict(actor='mentor',motion='gesture1')}]),converse('wait','The entrance is just behind you. Point at the door marked Refuge and click it; walking past it will not start the scene.',[('I will knock.',1)]),converse('after','Well done. It was only a rat, but we can rest here now. Come with me.',[('Let us go.',1)]),converse('waiting','The keeper is still checking the room. Deal with the rat when it appears, then come back to me.',[('Understood.',1)])],
        sequences=[dict(id='refuge_film',name='The keeper checks the refuge',actor='mentor',shot='wide',angle='high',duration=10,steps=[dict(at=0,actor='mentor',reference='guard',preset='aerial',transition=0)],cues=[
            dict(at=0,actions=[{'look_at':dict(actor='mentor',target='guard')},{'set_dynamic_light':dict(entity='mentor',color=[1,.8,.5],intensity=1,radius=180,style='constant')}]),
            dict(at=1,actions=[{'play_motion':dict(actor='mentor',motion='gesture1')}]),
            dict(at=2,actions=[{'start_patrol':'guard_walk'}]),
            dict(at=3,actions=[{'play_sound':dict(resource='wind_hollow_01',waypoint='noise',volume=35,min_distance=50,max_distance=1000)}]),
            dict(at=3.5,actions=[{'play_camera_path':dict(resource=path_id,speed=50)}]),
            dict(at=8.5,actions=[{'camera_fade':dict(initial=255,target=0,duration=1)}])])],events=[
            dict(id='arrival',when='scene_start',once=True,actions=[{'spawn':'mentor'},{'spawn':'guard'},{'start_quest':'director'},{'show_note':dict(title='Arrival at the refuge',text='You have reached the refuge. Turn towards the original door, hover to see Refuge, then click it. Elena will greet you. After the short film, defeat the rat and speak to her again.')}]),
            dict(id='click_refuge',when='object_clicked',object='refuge_door',once=True,actions=[{'set_flag':'director_knock'},{'control_original':{**selector(target), 'operation':'hide'}},{'start_conversation':'welcome'}]),
            dict(id='watch',when='conversation_ended',conversation='welcome',result=1,once=False,actions=[{'play_sequence':'refuge_film'}]),
            dict(id='skip',when='conversation_ended',conversation='welcome',result=2,once=False,actions=[{'run_event':'begin_guard'}]),
            dict(id='film_end',when='sequence_ended',sequence='refuge_film',once=True,actions=[{'run_event':'begin_guard'}]),
            dict(id='begin_guard',when='manual',once=True,actions=[{'advance_quest':'director'},{'set_flag':'director_ready'},{'spawn':'rat'},{'clear_dynamic_light':'mentor'},{'show_note':dict(title='A small intruder',text='A rat has slipped into the refuge. Defeat it, then speak to Elena. You can now move and use the interface normally.')}]),
            dict(id='rat_defeated',when='actor_killed',actor='rat',once=True,actions=[{'set_flag':'director_fight'},{'advance_quest':'director'}]),
            dict(id='leave_refuge',when='conversation_ended',conversation='after',result=1,once=True,actions=[{'advance_quest':'director'},{'complete_quest':'director'},{'camera_fade':dict(initial=255,target=0,duration=.5)},{'travel':dict(scene=destination,entry=entry)}])])
    # Aborting the welcome must never strand the player behind a one-shot door.
    for eid,conversation,conditions in [('mentor_start','wait',[('director_knock',False),('director_fight',False)]),('mentor_resume','welcome',[('director_knock',True),('director_ready',False),('director_fight',False)]),('mentor_wait','waiting',[('director_ready',True),('director_fight',False)]),('mentor_after','after',[('director_fight',True)])]:
        s['events'].append(dict(id=eid,when='actor_clicked',actor='mentor',once=False,conditions=[dict(flag=k,is_set=v) for k,v in conditions],actions=[{'start_conversation':conversation}]))
    points=[]
    for position in ([550,-1000,-300],[600,-750,-320]):
        delta=[300-position[0],-850-position[1],-440-position[2]]
        pitch=math.degrees(math.atan2(delta[2],math.hypot(delta[0],delta[1])));yaw=math.degrees(math.atan2(delta[1],delta[0]))-90
        points.append(dict(position=list(position),orientation=[pitch,0,yaw]))
    path=dict(id=path_id,name='Across the refuge',scene=sid,level='RaveClub',points=points)
    quest=dict(id='director',title='A place before dawn',description='Elena has offered you shelter. Make sure the room is safe.',steps=['Knock on the refuge door and speak to Elena.','Watch the keeper, then defeat the rat.','Speak to Elena and follow her.'],reward_xp=0)
    return s,path,quest


def main():
    ws=Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption'));backend=Backend(ws)
    s,path,quest=scene(backend,'refuge','epilogue','safe')
    epilogue=dict(id='epilogue',level=dict(source='RaveClub',name='Shelter before dawn'),default_entry='safe',entries=[dict(id='safe',name='Inside the refuge',transform=transform([365,-976,-512],90))],actors=[],objects=[],conversations=[],events=[dict(id='complete',when='scene_start',once=True,actions=[{'camera_fade':dict(initial=0,target=255,duration=1)},{'show_note':dict(title='Safe before dawn',text='You reached the refuge. The journal records your arrival and the rat is behind you. This small chronicle was authored in RCM, including its camera path; the original geometry has not changed.')}])])
    acceptance=dict(schema=2,project_format=10,chronicle=dict(id='rcm_director',name='RCM · Arrival at the refuge',description='A short acceptance chronicle for native scenery clicks and the Cinematic Director.'),entry='refuge',state={'flags':{'director_ready':0,'director_fight':1,'director_knock':2}},scenes=[s,epilogue],quests=[quest],resources={'camera_paths':[path]},metadata={'version':'1.0.0'},build_options={'debug':True})
    showcase=parse_source((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
    if not any(s['id']=='director_lab' for s in showcase['scenes']):
        first=showcase['scenes'][0];guide=next(c for c in first['conversations'] if c['id']=='guide')
        next(c for c in guide['choices'] if c['result']==8)['text']='Laboratorios opcionales: encuentros y cine.'
        next(e for e in first['events'] if e['id']=='dyn_menu')['actions']=[{'start_conversation':'dyn_hub'}]
        first['conversations'].append(dict(id='dyn_hub',speaker='guide',camera='ots_speaker_close',prompt='Los dos laboratorios son opcionales. Puedes probar enemigos dinámicos o visitar una pequeña escena dirigida, sin cambiar el encargo del libro.',choices=[dict(text='Encuentros dinámicos.',result=1),dict(text='Cinematic Director Lab.',result=2),dict(text='Volver.',result=3)]))
        first['events'] += [dict(id='dyn_hub_play',when='conversation_ended',conversation='dyn_hub',result=1,once=False,actions=[{'start_conversation':'dyn'}]),dict(id='dyn_hub_cinema',when='conversation_ended',conversation='dyn_hub',result=2,once=False,actions=[{'travel':dict(scene='director_lab',entry='safe')}]),dict(id='dyn_hub_back',when='conversation_ended',conversation='dyn_hub',result=3,once=False,actions=[{'start_conversation':'guide'}])]
        lab,path,quest=scene(backend,'director_lab',showcase['scenes'][0]['id'],showcase['scenes'][0]['default_entry']);showcase['scenes'].append(lab)
        flags=showcase['state']['flags'];used=set(flags.values())
        for key in ('director_ready','director_fight','director_knock'):
            value=next(i for i in range(1024) if i not in used);flags[key]=value;used.add(value)
        showcase['resources'].setdefault('camera_paths',[]).append(path);showcase['quests'].append(quest)
    else:
        lab,path,quest=scene(backend,'director_lab',showcase['scenes'][0]['id'],showcase['scenes'][0]['default_entry'])
        index=next(i for i,s in enumerate(showcase['scenes']) if s['id']=='director_lab');showcase['scenes'][index]=lab
        rows=showcase['resources']['camera_paths'];rows[next(i for i,r in enumerate(rows) if r['id']==path['id'])]=path
        if 'director_knock' not in showcase['state']['flags']:
            used=set(showcase['state']['flags'].values());showcase['state']['flags']['director_knock']=next(i for i in range(1024) if i not in used)
    for folder,source in [('director_acceptance',acceptance),('showcase',showcase)]:
        validation=backend.validate(source)
        if not validation.valid:raise ValueError([p.message for p in validation.problems if p.severity=='ERROR'])
        ws.write('chronicles/'+folder+'/project.yaml',source_text(source))
    from rcm.spatial.assets import Assets
    from rcm.spatial.math3d import Raycaster
    caster=Raycaster(Assets(backend).load('RaveClub').mesh);samples=[]
    for kind in ('entries','actors','waypoints'):
        for row in s[kind]:
            position=row['transform']['position'];hit=caster.ground(position,above=25,below=150)
            samples.append(dict(kind=kind,id=row['id'],position=position,surface=hit.position.tolist() if hit else None,triangle=hit.triangle if hit else None))
    grounded=all(r['surface'] and abs(r['surface'][2]-r['position'][2])<=1 for r in samples)
    if not grounded:raise ValueError('Example placement does not match the original floor')
    ws.write('research/embrace_closure/example_positions.json',json.dumps(dict(samples=samples,native_walkability_verified=False,native_camera_collision_verified=False),indent=2))
    evidence=dict(acceptance='chronicles/director_acceptance/project.yaml',showcase_lab='director_lab',original_door='RaveClub tracker_thing NSD offset 6560',door_operation='hide and clear collision; not fabricated animation',ground_positions_checked=grounded,native_engine_test=False)
    ws.write('research/embrace_closure/examples.json',json.dumps(evidence,indent=2));print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
