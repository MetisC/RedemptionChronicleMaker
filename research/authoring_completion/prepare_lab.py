"""Own optional acceptance site; never rewrites accepted examples or game files."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
import yaml
from PIL import Image,ImageDraw,ImageFont
from rcm.service import source_text

target=ROOT/'chronicles/completion_lab';target.mkdir(exist_ok=True);(target/'assets').mkdir(exist_ok=True)
root=yaml.safe_load((ROOT/'chronicles/strict_acceptance/project.yaml').read_text(encoding='utf8'))
root['chronicle']=dict(id='rcm_complete',name='RCM · Authoring laboratory',description='Optional focused acceptance site: native regions, timed camera rotation, generated actors and an informational map.')
root['quests']=[];root['state']['flags']={'guest_ready':0};root['resources']={'camera_paths':[]};s=root['scenes'][0];epilogue=root['scenes'][1]
s['level']['environment']['room_type']=5;s['actors']=s['actors'][:2];s['actors'][0]['name']='Anezka · authoring guide';s['objects']=[];s['events']=[];s['triggers']=[];s['paths']=[];s['encounters']=[];s['generators']=[]
base=copy.deepcopy(s['entries'][0]['transform'])
def transform(position):return dict(position=position,orientation=[0,0,0])
def event(name,actions,when='manual',**values):s['events'].append(dict(id=name,when=when,actions=actions,**values))
def note(title,text):return dict(show_note=dict(title=title,text=text))
def after(result,actions,**values):event('exercise_'+str(result),actions,'conversation_ended',conversation='lab',result=result,**values)
def dialogue(result,text):return dict(text=text,result=result)
root['resources']['camera_paths']=[dict(id='complete_pan',name='Turn and hold in place',scene=s['id'],level=s['level']['source'],timed=True,points=[dict(position=[550,-1000,-300],orientation=[-25,0,59],duration=3),dict(position=[550,-1000,-300],orientation=[-25,0,149],duration=2.5),dict(position=[550,-1000,-300],orientation=[-25,0,149])])]
s['sequences']=[dict(id='turn',name='Stationary camera: turn, then hold',actor='Player',duration=6,shot='wide',angle='high',camera_path='complete_pan',path_speed=1),dict(id='boss_view',name='Follow the current generated boss',actor='dynamic/lab_boss/boss/0',duration=4,shot='wide',angle='high',steps=[dict(at=0,actor='dynamic/lab_boss/boss/0',reference='Player',preset='full',angle='high',transition=.3),dict(at=2,actor='dynamic/lab_boss/boss/0',reference='Player',preset='ots_speaker_close',transition=.4)])]
s['waypoints']=[dict(id='boss_spot',name='Weak rat boss',transform=transform([600,-750,-512])),dict(id='guest_spot',name='Generated guest',transform=transform([410,-1010,-512]))]
s['generators']=[dict(id='lab_boss',name='Weak generated rat',mode='boss',spawn_points=['boss_spot'],max_alive=1,persistence='resume',remove_on_stop=True,waves=[dict(groups=[dict(role='boss',template='Rat',count=1,health=40)])],boss=dict(role='boss'),phases=[dict(id='half',percent=50,actions=[dict(play_motion=dict(actor='dynamic/lab_boss/boss/0',motion='stand')),dict(set_room_type=8)])]),dict(id='lab_guest',name='Generated neutral guest',mode='ambush',spawn_points=['guest_spot'],max_alive=1,persistence='resume',waves=[dict(groups=[dict(role='guest',template='LonCiv2',count=1,team=10)])])]
resources=json.loads((ROOT/'cache/resources.json').read_text(encoding='utf8'));available={t['id']:t for t in resources['templates']}
item=next((name for name in ('SilverRing','Dagger','ShortSword') if name in available and available[name]['kind'] in ('items','weapons','armour')),None)
if item is None:raise ValueError('No verified physical inventory template')
s['objects']=[dict(id='guest_item',name='Guest inventory test item',template=item,transform=copy.deepcopy(base))]
sound=next((e['id'] for e in resources['entries'] if e['extension'].lower()=='.wav' and 'bell' in e['id'].lower()),None)
if sound is None:raise ValueError('No original bell WAV found')
s['triggers']=[dict(id='native_bell',name='Native bell region beside the guard',shape='box',size=[96,96,120],once=False,transform=transform([430,-900,-464]),native_script={'class':'RegionTriggerSound','parameters':[dict(type=t,value=v) for t,v in [('string',sound+'.wav'),('float',64),('float',300),('integer',40),('integer',0),('integer',0),('integer',0)]]}),dict(id='sound_light',name='RCM sound and light activation zone',shape='box',size=[120,120,120],once=False,transform=transform([580,-820,-464]),sound_zone=dict(resource=sound,volume=20,min_distance=64,max_distance=300),light_zone=dict(entity='guard',color=[.4,.7,1],intensity=1,radius=300,style='constant'))]
s['actors'][0]['conversation']=dict(default='lab')
s['conversations']=[dict(id='lab',speaker='mentor',camera='ots_speaker_close',entry='hello',nodes=[dict(id='hello',lines=[dict(text='Welcome. This is a separate test site, so your tutorial is safe. Pick one exercise. You can come back to me between tests; the rat is deliberately weak.')],choices=[dialogue(1,'Show me the stationary camera turn.'),dialogue(2,'Create the weak rat boss.'),dialogue(3,'Follow the generated boss with the camera.'),dialogue(4,'Create the neutral guest and give them an item.'),dialogue(5,'Check the guest inventory.'),dialogue(6,'Show the second location on our map.'),dialogue(7,'Explain the two sound zones.'),dialogue(8,'Go to the second layout.'),dialogue(9,'Nothing for now.')])])]
hello=s['conversations'][0]['nodes'][0];hello['choices']=[c for c in hello['choices'] if c.get('result') not in (4,5)];hello['choices'].insert(3,dict(text='Generated guest and inventory…',goto='guest'))
s['conversations'][0]['nodes'].append(dict(id='guest',lines=[dict(text='Create the guest first, wait a moment, then ask me to check their inventory. Creating the guest also stops our test rat.')],choices=[dialogue(4,'Create the neutral guest and give them an item.'),dialogue(5,'Check the guest inventory.'),dict(text='Back to the other exercises.',goto='hello')]))
event('arrival',[dict(spawn='mentor'),dict(spawn='guard'),note('Authoring laboratory','Speak to Anezka just ahead. Try the stationary camera first, then the generated guest or weak rat. The map exercise reveals a second layout. This site is for manual acceptance; it does not replace your tutorial.')],'scene_start',once=True)
after(1,[dict(play_sequence='turn')]);after(2,[dict(start_generator='lab_boss')]);after(3,[dict(play_sequence='boss_view')],conditions=[dict(actor_alive='dynamic/lab_boss/boss/0')])
event('boss_missing',[note('Create the rat first','Choose Create the weak rat boss, wait a moment, then ask me to follow it.')],'conversation_ended',conversation='lab',result=3,conditions=[{'not':dict(actor_alive='dynamic/lab_boss/boss/0')}])
after(4,[dict(stop_generator='lab_boss'),dict(start_generator='lab_guest')])
event('guest_inventory',[dict(actor_behavior=dict(actor='dynamic/lab_guest/guest/0',team=10,paused=True)),dict(actor_inventory=dict(actor='dynamic/lab_guest/guest/0',item='guest_item',operation='give')),dict(set_flag='guest_ready')],'state_changed',once=True,conditions=[dict(actor_alive='dynamic/lab_guest/guest/0'),dict(flag='guest_ready',is_set=False)])
has_item=dict(actor_owns_item=dict(actor='dynamic/lab_guest/guest/0',item='guest_item'))
after(5,[note('The guest has the item','This message uses a real inventory condition on the generated guest. Its GUID comes from the existing encounter slots.')],conditions=[has_item])
event('guest_missing',[note('Create the guest first','Choose Create the neutral guest, wait a moment, then check again. If this still appears, retain the runtime trace for the inventory check.')],'conversation_ended',conversation='lab',result=5,conditions=[{'not':has_item}])
after(6,[dict(set_location_flags=dict(scene=epilogue['id'],visible=True,haven=False)),note('Open the map','The second layout should now appear. In RCM, select the chronicle and open Maps and locations to edit the image, drag points and assign scenes. This map only provides information; clicking a point does not travel.')])
after(7,[note('Two different mechanisms','Walk close to the guard for the original RegionTriggerSound bell. Then move towards the rat spawn corner: the larger RCM zone activates a loop and a blue point light on the guard. Move out again to stop them. Their boxes are visible in the editor. EAX needs a compatible 3D audio provider.')])
after(8,[dict(travel=dict(scene=epilogue['id'],entry=epilogue['entries'][0]['id']))])
event('turn_done',[note('Camera control returned','The camera should have turned for three seconds without changing position, held for two and a half seconds, then returned control. Its NCP uses timed polynomial segments; no original path was changed.')],'sequence_ended',sequence='turn')
epilogue['actors']=[dict(id='guide_back',name='Anezka · return to laboratory',template='Anezka',transform=transform([300,-850,-512]),conversation=dict(default='return'))];epilogue['objects']=[];epilogue['triggers']=[];epilogue['generators']=[];epilogue['paths']=[];epilogue['sequences']=[]
epilogue['conversations']=[dict(id='return',speaker='guide_back',camera='ots_speaker_close',entry='hello',nodes=[dict(id='hello',lines=[dict(text='Same geometry, another authored layout. Ready to return to the laboratory?')],choices=[dialogue(1,'Take me back.'),dialogue(2,'I will stay a moment.')])])]
epilogue['events']=[dict(id='arrive',when='scene_start',actions=[dict(spawn='guide_back')]),dict(id='return',when='conversation_ended',conversation='return',result=1,actions=[dict(travel=dict(scene=s['id'],entry=s['default_entry']))])]
image=Image.new('RGB',(640,480),'#17232e');draw=ImageDraw.Draw(image)
try:font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',23)
except OSError:font=ImageFont.load_default()
draw.text((35,30),'AUTHORING LABORATORY',fill='#f0d28a',font=font)
draw.rounded_rectangle((45,140,285,355),radius=16,outline='#8baaba',width=3);draw.rounded_rectangle((355,140,595,355),radius=16,outline='#8baaba',width=3);draw.line((285,245,355,245),fill='#f0d28a',width=3)
draw.text((75,175),'Laboratory',fill='white',font=font);draw.text((385,175),'Second layout',fill='white',font=font);draw.text((55,410),'Informational map: no click travel',fill='#c6d1d9',font=font)
image.save(target/'assets/laboratory_map.png')
root['resources']['maps']=[dict(id='laboratory',name='Laboratory map',source='chronicles/completion_lab/assets/laboratory_map.png',points=[dict(id='lab',name='Authoring laboratory',position=[155,220],visible=True,haven=False),dict(id='second',name='Second authored layout',position=[465,220],visible=False,haven=False)])]
s['map_location']=dict(map='laboratory',point='lab');epilogue['map_location']=dict(map='laboratory',point='second')
(target/'project.yaml').write_text(source_text(root),encoding='utf8')
(target/'README.md').write_text('''# Optional authoring laboratory

Open Help > Authoring laboratory, then F5 and create a new game. Speak to Anezka near arrival. This is separate from the accepted tutorial and mini chronicle.

1. Stationary camera: turn 3 seconds, hold 2.5 seconds, then regain control.
2. Spawn the weak Rat, then follow it. Kill/remove it while testing interruptions; the camera must return rather than switch targets.
3. Create the neutral guest (stops the rat), wait, then check inventory. The success note requires actual native inventory membership.
4. Reveal the second map location, inspect the in-game map, then travel using Anezka's dialogue. Return from the second layout.
5. Walk near the guard for the native bell region. The larger zone by the rat corner activates an owned sound loop and blue point light. Leave/re-enter; save/load and repeat.

EAX roomtype uses the original console command and requires a compatible native 3D audio provider. Neither compilation nor doubles prove visual/audio/native-save behaviour. Read docs/MANUAL_RUNTIME_CHECKLIST.md for the exact observations. All models, sounds and geometry are references to the user's game, not redistributed assets.
''',encoding='utf8')
print(target/'project.yaml')
