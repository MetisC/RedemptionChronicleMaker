"""Shared director actions, validation, real Codex compilation and compatibility."""
import copy,subprocess,tempfile
from pathlib import Path
from unittest import TestCase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')


class Director(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT,GAME))
    def source(self):
        root=blank();root['chronicle']['id']='director_test';root['state']['flags']={'seen':0}
        s=root['scenes'][0];s['actors']=[dict(id='mentor',name='Mentor',template='Anezka',transform=dict(position=[10,20,30],orientation=[0,0,0]))]
        s['events']=[dict(id='spawn',when='scene_start',actions=[{'spawn':'mentor'}]),dict(id='done',when='manual',actions=[{'set_flag':'seen'}])]
        s['sequences']=[dict(id='intro',name='Intro',actor='mentor',duration=6,shot='wide',angle='high',cues=[dict(at=0,actions=[{'camera_fade':dict(initial=0,target=255,duration=1)}]),dict(at=1,actions=[{'look_at':dict(actor='mentor',target='Player')},{'play_motion':dict(actor='mentor',motion='gesture1')}]),dict(at=3,actions=[{'camera_shot':dict(actor='mentor',reference='Player',preset='ots_speaker_close')}]),dict(at=5,actions=[{'run_event':'done'}])])]
        s['conversations']=[dict(id='talk',speaker='mentor',entry='hello',nodes=[dict(id='hello',lines=[dict(text='Welcome.',actions=[{'camera_shot':dict(actor='mentor',reference='Player',preset='speaker_close')},{'look_at':dict(actor='mentor',target='Player')}])],choices=[dict(text='Continue',result=1)])])]
        return root
    def validate(self,root):
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems]);return result.project
    def test_shared_compilation_and_source_stays_authored(self):
        root=self.source();before=copy.deepcopy(root);campaign=self.validate(root);scene,p=campaign.scenes[0];name,code=runtime(campaign,scene,p)
        self.assertEqual(root,before);self.assertEqual(len(scene['events']),2)
        for expected in ('CINEMA_CUE intro/','directorLine(event,line)','AddFade','LookAtThing','stageMotion','ClearAllEffects','cinemaRoutesRestored'):
            self.assertIn(expected,code)
        self.assertNotIn('SetTimer(1.0f',code)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            directory=Path(tmp);file=directory/(name+'.java');file.write_text(code,encoding='utf8')
            result=subprocess.run(['java','-jar',str(ROOT/'cache/toolchain/ecj-3.26.0.jar'),'-1.3','-proc:none','-encoding','UTF-8','-bootclasspath',str(ROOT/'cache/toolchain/classes.zip'),'-classpath',str(ROOT/'research/original/Codex.nob'),'-d',str(directory),str(file)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            from rcm.classfile_limits import inspect_class
            self.assertEqual(inspect_class((directory/(name+'.class')).read_bytes())['version'],'45.3')
    def test_invalid_time_and_motion_and_recursive_sequence(self):
        for edit in ('negative','end','nan','reverse','motion','cycle','modal_line','indirect_modal_line'):
            root=self.source();s=root['scenes'][0];cues=s['sequences'][0]['cues']
            if edit=='negative':cues[0]['at']=-1
            elif edit=='end':cues[-1]['at']=6
            elif edit=='nan':cues[-1]['at']=float('nan')
            elif edit=='reverse':cues[-1]['at']=.5
            elif edit=='motion':cues[1]['actions'][1]['play_motion']['motion']='gesture843'
            elif edit=='cycle':s['events'][1]['actions']=[{'play_sequence':'intro'}]
            elif edit=='modal_line':s['conversations'][0]['nodes'][0]['lines'][0]['actions']=[{'start_conversation':'talk'}]
            else:
                s['events'][1]['actions']=[{'show_note':dict(title='Note',text='Text')}]
                s['conversations'][0]['nodes'][0]['lines'][0]['actions']=[{'run_event':'done'}]
            with self.subTest(edit=edit):self.assertFalse(self.backend.validate(root).valid)
    def test_custom_path_audio_loop_and_staging_compile(self):
        root=self.source();s=root['scenes'][0];s['entries']=[dict(id='stage',name='Stage',transform=dict(position=[1,2,3],orientation=[0,0,90]))]
        s['actors'].append(dict(id='guard',name='Guard',template='LonCiv2',transform=dict(position=[50,20,30],orientation=[0,0,0])))
        s['default_entry']='stage'
        s['waypoints']=[dict(id='bell',name='Bell',transform=dict(position=[10,20,30],orientation=[0,0,0]))]
        sound=next(e['id'] for e in self.backend.resources['entries'] if e['extension']=='.wav')
        s['events'][0]['actions'] += [{'play_sound':dict(id='loop1',loop=True,resource=sound,waypoint='bell',volume=40,min_distance=50,max_distance=500)},{'stop_sound':'loop1'},{'set_weather':'drizzle'},{'camera_flash':dict(initial=0,target=255,duration=.2,bounce=True)},{'camera_filter':dict(duration=.5)}]
        s['events'][0]['actions'] += [{'set_dynamic_light':dict(entity='mentor',color=[1,1,.5],intensity=1,radius=200,style='torch1')},{'clear_dynamic_light':'mentor'}]
        s['conversations'][0]['staging']='stage'
        root['resources']['camera_paths']=[dict(id='own_path',scene=s['id'],level=s['level']['source'],points=[dict(position=[0,0,200],orientation=[-30,0,0]),dict(position=[100,0,200],orientation=[-30,0,15])])]
        s['sequences'][0]['camera_path']='own_path'
        campaign=self.validate(root);scene,p=campaign.scenes[0];name,code=runtime(campaign,scene,p)
        self.assertIn('SOUND_FLAG_LOOP',code);self.assertIn('TeleportPartyToEntrance(player,0)',code)
        timeline=copy.deepcopy(root);timeline['scenes'][0]['sequences'][0].pop('camera_path');timeline['scenes'][0]['sequences'][0]['steps']=[dict(at=0,actor='mentor',reference='guard',preset='aerial')]
        pair=self.validate(timeline);pair_scene,pair_project=pair.scenes[0];pair_code=runtime(pair,pair_scene,pair_project)[1]
        self.assertIn('SetupCutscene(cameraPlayer,things[0],things[1])',pair_code)
        self.assertIn('public void endscene(int client,int next,int capture)',code);self.assertEqual(code.count('public void endscene('),1)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            directory=Path(tmp);file=directory/(name+'.java');file.write_text(code,encoding='utf8')
            result=subprocess.run(['java','-jar',str(ROOT/'cache/toolchain/ecj-3.26.0.jar'),'-1.3','-proc:none','-encoding','UTF-8','-bootclasspath',str(ROOT/'cache/toolchain/classes.zip'),'-classpath',str(ROOT/'research/original/Codex.nob'),'-d',str(directory),str(file)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_path_resources_references_safe_delete_and_package_roundtrip(self):
        from rcm.project_resources import prepare
        from rcm.camera_paths import CameraPath
        from rcm.campaign_document import CampaignDocument
        from rcm.campaign_relations import graph
        from rcm.safe_edit import deletion_plan
        from rcm.packages import export_project,import_project
        from rcm.service import build_inputs_fingerprint
        root=self.source();s=root['scenes'][0];s['sequences'][0]['camera_path']='own_path'
        root['resources']['camera_paths']=[dict(id='own_path',scene=s['id'],level=s['level']['source'],points=[dict(position=[0,0,100],orientation=[-20,0,0])])]
        self.validate(root)
        unused,resources,payload,info=prepare(self.backend.ws,root,self.backend.original_resources)
        self.assertEqual(len(CameraPath.read(payload['paths/own_path.ncp']).records),1)
        self.assertTrue(next(e for e in resources['entries'] if e['id']=='own_path')['project_owned'])
        links=graph(root);self.assertTrue(any(l.target==('resources','camera_paths',0) for l in links))
        doc=CampaignDocument(self.backend.ws,root);plan=deletion_plan(doc,('resources','camera_paths',0),self.backend)
        self.assertEqual(plan.candidate['resources']['camera_paths'],[]);self.assertEqual(doc.snapshot(),root)
        before=build_inputs_fingerprint(self.backend.ws,root);changed=copy.deepcopy(root);changed['resources']['camera_paths'][0]['points'][0]['position'][0]=1
        self.assertNotEqual(before,build_inputs_fingerprint(self.backend.ws,changed))
        missing=copy.deepcopy(root);missing['resources']['camera_paths']=[]
        self.assertFalse(self.backend.validate(missing).valid)
        collision=copy.deepcopy(root);original=next(e['id'] for e in self.backend.resources['entries'] if e['extension']=='.ncp')
        collision['resources']['camera_paths'][0]['id']=original;collision['scenes'][0]['sequences'][0]['camera_path']=original
        self.assertFalse(self.backend.validate(collision).valid)
        other=copy.deepcopy(root['scenes'][0]);other['id']='other';cross=copy.deepcopy(root);cross['scenes'].append(other)
        validation=self.backend.validate(cross);self.assertTrue(validation.valid)
        self.assertTrue(any(p.severity=='WARNING' and 'otra escena' in p.message for p in validation.problems))
        doc.rename_global('scenes',0,'renamed');self.assertEqual(doc.snapshot()['resources']['camera_paths'][0]['scene'],'renamed');self.validate(doc.snapshot())
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            ws=Workspace(Path(tmp));archive=export_project(ws,root,'source.rcmproject');imported=import_project(ws,archive,'imported')
            self.assertEqual(imported.snapshot()['resources']['camera_paths'],root['resources']['camera_paths'])
    def test_director_rename_and_cascade_keep_source_valid(self):
        from rcm.campaign_document import CampaignDocument
        from rcm.safe_edit import deletion_plan
        root=self.source();s=root['scenes'][0]
        s['waypoints']=[dict(id='bell',name='Bell',transform=dict(position=[10,20,30],orientation=[0,0,0]))]
        sound=next(e['id'] for e in self.backend.resources['entries'] if e['extension']=='.wav')
        s['events'][0]['actions'] += [{'play_sound':dict(id='wind',loop=True,resource=sound,waypoint='bell',volume=40,min_distance=50,max_distance=500)},{'set_dynamic_light':dict(entity='mentor',color=[1,1,1],intensity=1,radius=200)}]
        s['events'][1]['actions'].append({'stop_sound':'wind'})
        from rcm.audio import rename_loop
        rename_loop(s,'wind','ambience');self.assertEqual(s['events'][1]['actions'][-1],{'stop_sound':'ambience'})
        self.validate(root);doc=CampaignDocument(self.backend.ws,root)
        doc.rename('actors',0,'guide');self.validate(doc.snapshot())
        self.assertEqual(doc.snapshot()['scenes'][0]['events'][0]['actions'][-1]['set_dynamic_light']['entity'],'guide')
        plan=deletion_plan(doc,('scenes',0,'waypoints',0),self.backend);self.validate(plan.candidate)
        self.assertFalse(any('stop_sound' in a for e in plan.candidate['scenes'][0]['events'] for a in e['actions']))
        line=('scenes',0,'conversations',0,'nodes',0,'lines',0)
        root=doc.snapshot();root['scenes'][0]['conversations'][0]['nodes'][0]['lines'][0]['actions']=[{'look_at':dict(actor='guide',target='Player')}]
        doc=CampaignDocument(self.backend.ws,root);plan=deletion_plan(doc,line+('actions',0),self.backend)
        self.assertEqual(plan.candidate['scenes'][0]['conversations'][0]['nodes'][0]['lines'][0]['text'],'Welcome.')
        self.assertNotIn('actions',plan.candidate['scenes'][0]['conversations'][0]['nodes'][0]['lines'][0]);self.validate(plan.candidate)

    def test_timeline_once_failure_restore_and_conversation_with_doubles(self):
        from test_stability_revision import compile_scenario
        campaign=self.validate(self.source());name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness {
          static void check(boolean value,String label){if(!value)throw new AssertionError(label);}
          static void tick(SCENE s){s.timer(9400,0,0,0,0);}
          static boolean begin(SCENE s)throws Exception{java.lang.reflect.Method m=SCENE.class.getDeclaredMethod("beginCinema",int.class);m.setAccessible(true);return ((Boolean)m.invoke(s,0)).booleanValue();}
          public static void main(String[] args)throws Exception {
            CE.Thing player=new CE.Thing();player.template="Player";CE.world.put(1,player);
            SCENE s=new SCENE();s.beginscene(1,0);
            check(begin(s),"film begins");check(CE.cutscene&&CE.aiOff,"film owns controls");check(CE.fades==1,"opening cue once");
            check(!begin(s),"second film cannot steal control");check(CE.fades==1,"conflicting start cannot replay cue");
            tick(s);check(CE.fades==1,"opening cue not repeated");
            if(args[0].equals("restore")){s.save(0);SCENE loaded=new SCENE();loaded.restore(0);loaded.restored(0);for(int i=0;i<10;i++)tick(loaded);check(!CE.cutscene&&!CE.aiOff,"restore cancels film and releases controls");check(CE.fades==1,"restore never replays side effects");return;}
            if(args[0].equals("missing")){int npc=CodexThing.GuidFromCastID("PREFIX_mentor");CE.world.remove(npc);for(int i=0;i<12;i++)tick(s);check(!CE.cutscene&&!CE.aiOff,"missing actor abort releases controls");return;}
            for(int i=0;i<48;i++)tick(s);check(!CE.cutscene&&!CE.aiOff,"natural end releases controls");check(CE.flags[0],"ordinary event action fired");check(CE.fades==1,"cue remains once after end");
            java.lang.reflect.Method talk=SCENE.class.getDeclaredMethod("conversation",int.class);talk.setAccessible(true);check(((Boolean)talk.invoke(s,0)).booleanValue(),"conversation starts after film");
            int npc=CodexThing.GuidFromCastID("PREFIX_mentor");s.convreached(1,0,0,0,npc);check(CE.world.get(npc).facing==1,"line action uses real target");s.convended(1,true,0);tick(s);check(!CE.cutscene&&!CE.aiOff,"dialogue abort releases controls");
          }
        }'''.replace('SCENE',name).replace('PREFIX',campaign.scenes[0][1].prefix)
        def doubles(text):
            text=text.replace('class CE {','class CE {static int fades=0,cleared=0;')
            value=self.backend.resources['motion_catalogue']['modes']['gesture1']
            text=text.replace('class Codex {','class Codex {static final int MOTION_GESTURE1='+str(value)+';')
            return text.replace('class CodexCamera extends Codex {','class CodexCamera extends Codex {static int AddFade(int p,float a,float b,float d,boolean bounce){CE.fades++;return 1;}static void ClearAllEffects(int p){CE.cleared++;}')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            out=Path(tmp);compile_scenario(out,campaign,harness,doubles)
            for mode in ('normal','restore','missing'):
                result=subprocess.run(['java','-cp',str(out),'StabilityHarness',mode],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,mode+result.stdout+result.stderr)
    def test_owned_audio_light_and_weather_restore_with_doubles(self):
        from test_stability_revision import compile_scenario
        root=self.source();s=root['scenes'][0];s['sequences']=[];s['conversations']=[]
        s['waypoints']=[dict(id='bell',name='Bell',transform=dict(position=[0,0,10],orientation=[0,0,0]))]
        sound=next(e['id'] for e in self.backend.resources['entries'] if e['extension']=='.wav')
        s['events'][0]['actions'] += [{'play_sound':dict(id='loop1',loop=True,resource=sound,waypoint='bell',volume=40,min_distance=50,max_distance=500)},{'set_weather':'drizzle'},{'set_dynamic_light':dict(entity='mentor',color=[1,1,.5],intensity=1,radius=200,style='torch1')}]
        campaign=self.validate(root);name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness {
          static void check(boolean value,String label){if(!value)throw new AssertionError(label);}
          public static void main(String[] args){CE.Thing player=new CE.Thing();player.template="Player";CE.world.put(1,player);
            SCENE s=new SCENE();s.beginscene(1,0);for(int i=0;i<4;i++)s.timer(9400,0,0,0,0);
            check(CE.soundStarts==1,"one sound handle");check(CE.lights==1,"one light allocation");check(CE.weather.equals("drizzle"),"weather applied");
            s.save(0);CE.fail=args.length>0;SCENE r=new SCENE();r.restore(0);r.restored(0);r.beginscene(1,0);for(int i=0;i<15;i++)r.timer(9400,0,0,0,0);
            check(CE.soundStarts==2,"restore recreates once");check(CE.lights==2,"restore reapplies once");
            r.endscene(1,0,0);check(CE.soundStops==1,"scene end stops owned handle");
          }}'''.replace('SCENE',name)
        def doubles(text):
            text=text.replace('class CE {','class CE {static int soundStarts=0,soundStops=0,lights=0;static boolean fail=false;static String weather="";')
            text=text.replace('class Codex {','class Codex {static final int SOUND_FLAG_LOOP=1,LIGHTSTYLE_TORCH1=1;static void SetWeatherEffect(String value){CE.weather=value;}')
            text=text.replace('class CodexThing extends Codex {','class CodexThing extends Codex {boolean AllocateDynamicLight(){CE.lights++;return !CE.fail;}boolean ClearDynamicLight(){return true;}boolean SetDynamicLightColor(float[] v){return true;}boolean SetDynamicLightIntensity(float v){return true;}boolean SetDynamicLightRadius(float v){return true;}boolean SetDynamicLightStyle(int v){return true;}')
            return text.replace('class CodexSound extends Codex {','class CodexSound extends Codex {CodexSound(String n,float a,float b,int v,int pan,int flags,float[] p){CE.soundStarts++;}void Stop(){CE.soundStops++;}')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            out=Path(tmp);compile_scenario(out,campaign,harness,doubles)
            result=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=subprocess.run(['java','-cp',str(out),'StabilityHarness','fail'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
