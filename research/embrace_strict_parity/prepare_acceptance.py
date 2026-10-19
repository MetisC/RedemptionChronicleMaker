"""Reproducible opt-in example. Does not change the accepted tutorial."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
import yaml
from rcm.service import Backend
from rcm.paths import Workspace
from rcm.native_arrivals import planes,sector_at

b=Backend(Workspace(ROOT));root=yaml.safe_load((ROOT/'chronicles/director_acceptance/project.yaml').read_text(encoding='utf8'))
root=copy.deepcopy(root);root['chronicle'].update(id='rcm_strict',name='RCM · Cargo at the refuge',description='Optional native authoring acceptance: help Elena secure a refuge and inspect its floating cargo. Not a replacement for the tutorial.')
root['resources']['camera_paths'][0]['id']='rcm_strict_cam'
def replace(value):
    if isinstance(value,dict):return {k:replace(v) for k,v in value.items()}
    if isinstance(value,list):return [replace(v) for v in value]
    return 'rcm_strict_cam' if value=='rcm_refuge_cam' else value
root=replace(root);s=root['scenes'][0]
for scene in root['scenes']:
    for key in ('actors','objects','conversations','events','entries','waypoints','paths','sequences','encounters','triggers','generators'):scene.setdefault(key,[])
s['level']['environment']=dict(music='London_Hub',music_volume=50,ambient_volume=35,fog=dict(mode='linear',color=[65,70,78],start=650,end=2600),zclip=4000)
s['actors'][0]['overrides']=dict(hover_text='Elena, keeper of the refuge',foley='npcGeneralFemale')
original=next(r for r in b.resources['templates'] if r['id']=='Anezka')
if original.get('ai'):s['actors'][0]['overrides']['ai']=original['ai']
s['actors'][0]['overrides']['motions']=b.resources['motion_catalogue']['templates']['Anezka']
def transform(x,y,z):return dict(position=[x,y,z],orientation=[0,0,0])
s['objects']+= [dict(id='cargo_mover',name='Cargo motion controller',template='tracker_thing',transform=transform(500,-900,-496),native_frames=['cargo_high'],native_script={'class':'ClassBobbing','parameters':[dict(type='thing',value='cargo'),dict(type='float',value=8),dict(type='float',value=15),dict(type='float',value=1)]}),dict(id='cargo',name='Floating cargo',template='barrel1',transform=transform(500,-900,-496)),dict(id='loot',name='Supplies for the refuge',template='container_barrel1',transform=transform(550,-900,-512),overrides=dict(treasure_class=230,hover_text='Supplies: break the barrel to search')),dict(id='default_loot',name='Ordinary supplies',template='container_barrel1',transform=transform(600,-900,-512))]
s.setdefault('waypoints',[]).append(dict(id='cargo_high',name='Cargo: upper destination',transform=transform(500,-900,-472)))
entry=next(e for e in s['events'] if e['when']=='scene_start')
entry['actions'] += [dict(spawn='loot'),dict(spawn='default_loot')]
end=root['scenes'][1]
end.setdefault('waypoints',[]).append(dict(id='interest',name='Optional native AI interest spot: group 8',interest_group=8,transform=transform(430,-900,-512)))
end['actors'].append(dict(id='scavenger',name='A harmless scavenger',template='Rat',transform=transform(365,-850,-512)))
end['events'][0]['actions'][:0]=[dict(spawn='scavenger'),dict(enable_ai='scavenger')]
note=end['events'][0]['actions'][-1]['show_note']
note['text']+=' A harmless rat searches the refuge for scraps, using its original AI and native interest group 8. The floating cargo outside uses ClassBobbing with a linked object and movement frame. The two supply barrels compare inherited treasure with class 230. These native behaviours require manual observation; this example does not certify them.'
for row in s['objects'][-4:]:sector_at(planes(b.ws,b.levels['RaveClub']),row['transform']['position'])
result=b.validate(root)
if not result.valid:raise ValueError(result.problems)
dest=ROOT/'chronicles/strict_acceptance';dest.mkdir(exist_ok=True);(dest/'project.yaml').write_text(yaml.safe_dump(root,allow_unicode=True,sort_keys=False,width=110),encoding='utf8')
(dest/'README.md').write_text('''# Cargo at the refuge — optional native acceptance

Open project.yaml in RCM, build and use Test in Redemption. Start a new game.
Knock on the refuge door, speak to Elena, watch or skip the keeper, defeat the
weak Rat, then follow Elena. The tutorial and mini chronicle are unchanged.

Before leaving, inspect the floating barrel and the two supply barrels near
the keeper. The left supply barrel uses native treasure class 230; the other
inherits its template. Break them to compare native loot (random, not guaranteed
on one attempt). Cargo motion uses ClassBobbing, scalar parameters and a thing
link; edit it under Object > Native script. Frame 0 is the initial transform;
the named cargo_high waypoint is frame 1. These are ordinary editor controls.

Level > Environment configures music, fog, audio volumes and ZClip. Elena >
Instance properties sets her hover text, Foley and matching original AI/motion
set explicitly. In the epilogue a harmless rat has its original AI enabled and
a matching native interest-group-8 waypoint. Observe whether it chooses that
spot; this generated setup does not certify native AI behaviour. EAX remains
inherited; no experimental sky is added to an unverified original surface.

All new native behaviour is MANUAL RUNTIME TEST REQUIRED. No original assets
or Java classes are copied into this example. Geometry remains immutable.
''',encoding='utf8')
print(json.dumps(dict(valid=True,chronicle=root['chronicle']['id'],native_game_test=False)))
