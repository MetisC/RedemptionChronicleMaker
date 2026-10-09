"""Tutorial flow and cinematic ownership with Java doubles, not native QA."""
import json
import re
import subprocess
from pathlib import Path
from unittest import TestCase

from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime

ROOT = Path(__file__).resolve().parents[1]


class GuidedTutorial(TestCase):
    def test_authored_walking_positions_have_original_floor_and_headroom(self):
        from rcm.deployment import default_game
        from rcm.spatial.assets import Assets
        from rcm.spatial.geometry import read_nil
        from rcm.spatial.math3d import Raycaster
        backend = Backend(Workspace(ROOT, default_game(ROOT)))
        source = backend.validate((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')).project.source
        entry = backend.levels['EastLondon']['geometry'][0]
        ray = Raycaster(read_nil(Assets(backend).read(entry['path'],entry['archive'])))
        records = []
        for scene in source['scenes']:
            rows = scene['actors']+scene.get('entries',[])+scene.get('waypoints',[])
            rows += [o for o in scene.get('objects',[]) if o['id'] in {'reward','barrel','stage_door'}]
            for row in rows:
                point = row['transform']['position']
                hit = ray.ground(point,64,128)
                self.assertIsNotNone(hit,(scene['id'],row['id'],point))
                self.assertAlmostEqual(float(hit.position[2]),float(point[2]),places=1)
                self.assertIsNone(ray.cast(hit.position+[0,0,1],[0,0,1],False,110),(scene['id'],row['id']))
                records.append(dict(scene=scene['id'],id=row['id'],point=point,ground=hit.position.tolist()))
        lab=next(a for a in source['scenes'][0]['actors'] if a['id']=='lab')
        start=source['scenes'][0]['entries'][0]['transform']['position']
        import numpy as np
        a=np.array(start)+[0,0,50];b=np.array(lab['transform']['position'])+[0,0,50]
        self.assertIsNone(ray.cast(a,b-a,False,float(np.linalg.norm(b-a))),'Laboratorio separado por pared')
        dest = ROOT/'research/round0/guided_tutorial/spatial_check.json'
        dest.write_text(json.dumps(records,indent=2),encoding='utf8')

    def test_sequence_completion_requires_a_real_timeline_and_correct_filter(self):
        import copy
        backend = Backend(Workspace(ROOT))
        source = backend.validate((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')).project.source
        for kind, sequence in [('sequence_ended', 'missing'), ('actor_clicked', 'walk_scene')]:
            candidate = copy.deepcopy(source)
            candidate['scenes'][0]['events'].append(dict(id='invalid_sequence', when=kind, sequence=sequence, actor='mentor', actions=[{'set_flag':'step1'}]))
            self.assertFalse(backend.validate(candidate).valid)

    def test_physical_key_preserves_original_appearance_and_avoids_consumed_type(self):
        from rcm.formats import NotFile, cstring, u32
        backend=Backend(Workspace(ROOT))
        import yaml
        source=yaml.safe_load((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8'))
        backend.sync_resources(source)
        templates=[t for path,data in backend.project_payload.items() if path.endswith('.not') for t in NotFile.read(data).templates]
        key=next(t for t in templates if t.name=='T_tutor_key')
        self.assertEqual(cstring(key.values()[0]),'BoneKey')
        self.assertEqual(u32(key.values()[20]),0)
        workshop=source['scenes'][0]
        self.assertEqual(next(o for o in workshop['objects'] if o['id']=='key')['template'],'T_tutor_key')
        change=next(e for e in workshop['events'] if e['id']=='next_4')
        self.assertEqual(change['actions'][0],{'give_item':'key'})

    def test_cinematic_prop_validation_rejects_incomplete_or_unsafe_motion(self):
        import copy
        backend=Backend(Workspace(ROOT))
        source=backend.validate((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')).project.source
        for changes in [{'object':'absent'},{'at':11,'duration':3},{'translation':[float('nan'),0,0]},{'translation':[1,2]}]:
            candidate=copy.deepcopy(source)
            candidate['scenes'][0]['sequences'][0]['prop_motion'].update(changes)
            self.assertFalse(backend.validate(candidate).valid)

    def test_seven_lessons_each_has_skip_and_laboratory_is_separate(self):
        source = (ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')
        result = Backend(Workspace(ROOT)).validate(source)
        self.assertTrue(result.valid, [p.message for p in result.problems])
        campaign = result.project
        self.assertEqual(len(campaign.source['quests']), 1)
        self.assertEqual(len(campaign.source['quests'][0]['steps']), 7)
        for scene, _ in campaign.scenes:
            for conv in scene['conversations']:
                if conv['id'] == 'lab':
                    continue
                self.assertEqual(len(conv['choices']), 2)
                self.assertIn('Omitir', conv['choices'][1]['text'])
        workshop = campaign.scenes[0][0]
        main = [a for a in workshop['actors'] if a['id'] in {'mentor','camera','director','keeper','gate'}]
        self.assertGreaterEqual(len({a['template'] for a in main}), 5)
        self.assertFalse(any(a['template']=='businessWoman' for a in main))
        initial = workshop['events'][0]['actions']
        self.assertEqual([a['spawn'] for a in initial if 'spawn' in a], ['mentor','lab','labwalker'])
        for a in main:
            self.assertEqual(a['transform']['position'], [-176,-612,384])
        barrel = next(o for o in workshop['objects'] if o['id']=='barrel')
        self.assertGreater(sum((x-y)**2 for x,y in zip(barrel['transform']['position'],main[0]['transform']['position'])), 150**2)

    def test_complete_and_skip_tours_and_clicks_during_film(self):
        campaign = Backend(Workspace(ROOT)).validate((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')).project
        out = ROOT/'build/tests/guided_tutorial'
        out.mkdir(parents=True, exist_ok=True)
        java_files = []
        code = ''
        for s,p in campaign.scenes:
            name, java = runtime(campaign,s,p)
            file = out/(name+'.java')
            file.write_text(java, encoding='utf8')
            java_files.append(str(file))
            code += java
        doubles = (ROOT/'tests/java/CampaignEngine.java').read_text(encoding='utf8')
        doubles = doubles.replace('boolean item=false','boolean tpose=false; int actionStops=0; boolean item=false')
        doubles = doubles.replace('static boolean client=false','static boolean consumeRewards=false;static boolean client=false')
        doubles = doubles.replace('boolean AddToActorInventory(int item){', 'boolean AddToActorInventory(int item){if(CE.consumeRewards&&CE.world.get(item).template.endsWith("_key")){CE.world.remove(item);return true;}')
        # Real SetTimer APPENDS even with the same ID. Reproduce it, rather
        # than manually invoking an idealized single recurring timer chain.
        doubles = doubles.replace('class CE {', '''class CE {
          static class Pending {Codex owner;int id;int due;Pending(Codex o,int i,int d){owner=o;id=i;due=d;}}
          static int time=0,maxPending=0;static List<Pending> timers=new ArrayList<Pending>();
          static void pulse()throws Exception{time+=150;int calls=0;while(true){Pending ready=null;for(Pending p:timers)if(p.due<=time){ready=p;break;}if(ready==null)break;timers.remove(ready);ready.owner.getClass().getMethod("timer",int.class,float.class,float.class,float.class,float.class).invoke(ready.owner,ready.id,0f,0f,0f,0f);if(++calls>100)throw new AssertionError("timer explosion");}if(timers.size()>1)throw new AssertionError("duplicate polling timers: "+timers.size());}
        ''')
        doubles = doubles.replace('boolean SetTimer(float s,int id){return true;}', 'boolean SetTimer(float s,int id){CE.timers.add(new CE.Pending(this,id,CE.time+Math.round(s*1000)));CE.maxPending=Math.max(CE.maxPending,CE.timers.size());return true;}')
        doubles = doubles.replace('boolean KillTimer(int id){return true;}', 'boolean KillTimer(int id){for(int i=CE.timers.size()-1;i>=0;i--)if(CE.timers.get(i).owner==this&&CE.timers.get(i).id==id)CE.timers.remove(i);return true;}')
        doubles = doubles.replace('void StopActorAction(){}','void StopActorAction(){CE.world.get(guid).actionStops++;}')
        doubles = doubles.replace('boolean SetOrientation(float[] a)', 'boolean SetPosition(float[] a){CE.world.get(guid).pos=a.clone();return true;} boolean SetOrientation(float[] a)')
        doubles = doubles.replace('int SetActorTeam(int t)', 'void StopActorMotion(){CE.world.get(guid).tpose=true;} boolean SendActorToPos(float[] p,float v){CE.world.get(guid).pos=p.clone();return true;} int SetActorTeam(int t)')
        doubles = doubles.replace('t.contains("reward")', 't.contains("reward")||t.contains("key")')
        doubles = doubles.replace('static void Jump(String s,int e)', 'static String layout=""; static void ChangeScene(String s,String file){layout=file;} static void Jump(String s,int e)')
        constants = sorted(set(re.findall(r'\bCAM_(?:SHOT|DIST|ANGLE)_[A-Z_]+\b', code)))
        doubles = doubles.replace('class Codex {', 'class Codex {int GetGUID(){return 5000;}' + ''.join('static final int '+c+'='+str(i)+';' for i,c in enumerate(constants) if not re.search(r'\b'+c+r'\s*=',doubles)))
        doubles = doubles.replace('static void SetShot(int p,int s,int a,int d,int f,float t){}','static void SetShot(int p,int s,int a,int d,int f,float t){shots++;lastShot=s;lastDistance=d;}')
        doubles = doubles.replace('class CodexCamera extends Codex {', 'class CodexCamera extends Codex {static int shots=0,lastShot=0,lastDistance=0; static boolean PlayPath(int p,int c,String path,float speed){return true;}')
        (out/'CampaignEngine.java').write_text(doubles, encoding='utf8')
        harness = '''public class GuidedHarness {
          static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);System.out.println(why);}
          static void tick(R_rcm_tutor_s0_Scene s){try{CE.pulse();}catch(Exception e){throw new RuntimeException(e);}}
          static void answer(R_rcm_tutor_s0_Scene s,String actor,int answer){int npc=CodexThing.GuidFromCastID("R_rcm_tutor_s0_"+actor);check(CE.valid(npc),"teacher "+actor+" available");int stops=CE.world.get(1).actionStops;s.clicked(npc,1,0);check(CE.world.get(npc).facing==1&&CE.world.get(1).facing==npc,"interlocutors face each other");check(CE.world.get(1).actionStops==stops+1,"stop action only before native conversation");s.convreached(1,0,0,0,npc);check(CE.world.get(1).actionStops==stops+1&&!CE.world.get(1).tpose&&!CE.world.get(npc).tpose,"line feedback preserves actor animation");s.convended(1,false,answer);tick(s);}
          static void close(R_rcm_tutor_s0_Scene s,int answer){s.convended(1,false,answer);tick(s);}
          public static void main(String[] args)throws Exception{
            boolean skip=args[0].equals("skip");CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);CE.syncFeedback=true;
            R_rcm_tutor_s0_Scene s=new R_rcm_tutor_s0_Scene();s.beginscene(1,0);
            check(CE.quests.size()==1,"journal reveals only the first lesson");
            check(CodexThing.GuidFromCastID("R_rcm_tutor_s0_camera")==0,"future teachers are not spawned at start");
            answer(s,"mentor",skip?2:1);check(CE.quests.size()==2,"lesson 2 revealed");
            answer(s,"camera",skip?2:1);if(!skip){CAMERA_TOUR}
            check(CE.quests.size()==3,"lesson 3 revealed");
            if(skip)answer(s,"director",2);
            else{
              int walker=CodexThing.GuidFromCastID("R_rcm_tutor_s0_walker");CE.Thing walking=CE.world.get(walker);
              answer(s,"director",1);check(CE.cutscene&&CE.aiOff,"film owns native cutscene mode");
              int door=CodexThing.GuidFromCastID("R_rcm_tutor_s0_stage_door");CE.Thing doorState=CE.world.get(door);check(doorState.pos[2]==384,"door starts shut");
              int calls=CE.conversationCalls;s.clicked(CodexThing.GuidFromCastID("R_rcm_tutor_s0_director"),1,0);check(calls==CE.conversationCalls,"click cannot tear down film");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&doorState.pos[2]==384&&walking.pos[1]==-1018,"establishing shot waits three real seconds; walker stays behind door");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&doorState.pos[2]>580,"door opens over three seconds before actor walks");
              for(int i=0;i<20;i++)tick(s);check(CE.cutscene&&walking.pos[1]==-878,"nine seconds into film: walker has passed and control stays locked");
              for(int i=0;i<23;i++)tick(s);
              check(!CE.cutscene&&!CE.aiOff&&CodexCamera.shots>=4,"four shots complete after twelve real seconds and release cutscene");
              check(CE.maxPending==1,"thirteen camera conversations do not multiply native timers");
            }
            check(CE.quests.size()==4,"lesson 4 appears after film or skip");
            if(!skip)CE.consumeRewards=true;
            answer(s,"keeper",skip?2:1);
            if(!skip){check(!CE.flags[8]&&CE.world.get(1).inventory.size()==0&&CE.valid(CodexThing.GuidFromCastID("R_rcm_tutor_s0_keeper")),"consumed token cannot claim delivery or remove Elena");CE.consumeRewards=false;tick(s);}
            check(CE.flags[8]&&CE.world.get(1).inventory.size()==1,"skip also supplies required physical key");
            check(CE.quests.size()==5,"lesson 5 revealed");
            int barrel=CodexThing.GuidFromCastID("R_rcm_tutor_s0_barrel");check(CE.valid(barrel),"decorative barrel visible before layout change");
            answer(s,"gate",skip?2:1);check(CE.jump.equals("combat")&&!CE.valid(barrel),"layout request removes barrel visibly");
            check(CodexSequence.layout.equals("R_rcm_tutor_s1.nsd"),"same geometry selects target NSD explicitly");
            CE.location=1;player.location=1;R_rcm_tutor_s1_Scene combat=new R_rcm_tutor_s1_Scene();combat.beginscene(1,0);
            int guide=CodexThing.GuidFromCastID("R_rcm_tutor_s1_guide");combat.clicked(guide,1,0);combat.convended(1,false,skip?2:1);combat.timer(9400,0,0,0,0);
            if(!skip){int rat=CodexThing.GuidFromCastID("R_rcm_tutor_s1_rat");check(CE.valid(rat),"one rat spawned close to arrival");CE.world.get(rat).health=0;combat.timer(9400,0,0,0,0);}
            check(CE.jump.equals("finished")&&CE.quests.size()==7,"kill or skip reveals final lesson");
            CE.location=2;player.location=2;R_rcm_tutor_s2_Scene end=new R_rcm_tutor_s2_Scene();end.beginscene(1,0);
            end.clicked(CodexThing.GuidFromCastID("R_rcm_tutor_s2_mentor"),1,0);end.convended(1,false,skip?2:1);end.timer(9400,0,0,0,0);
            check(CE.flags[11]&&CE.complete.size()==7,"all seven objectives complete in order");
          }
        }'''
        from rcm.camera_presets import PRESETS, DEFAULT_DIALOGUE_CAMERA
        order = [DEFAULT_DIALOGUE_CAMERA,*[k for k in PRESETS if k!=DEFAULT_DIALOGUE_CAMERA]]
        examples = [next(c for c in campaign.scenes[0][0]['conversations'] if c['camera']==preset and (c['id']=='framed' or c['id'].startswith('frame_'))) for preset in order]
        tour = []
        for index,example in enumerate(examples):
            _,shot,distance = PRESETS[example['camera']]
            tour.append('check(CE.conversation.endsWith("'+example['id']+'"),"camera '+str(index+1)+' opens in order");')
            tour.append('check(CodexCamera.lastShot==CAM_SHOT_'+shot+'&&CodexCamera.lastDistance==CAM_DIST_'+distance+',"frame preset applied");')
            tour.append('tick(s);check(CE.conversation.endsWith("'+example['id']+'"),"camera waits for user");close(s,1);')
        harness = harness.replace('CAMERA_TOUR',''.join(tour)).replace('==CAM_SHOT_','==Codex.CAM_SHOT_').replace('==CAM_DIST_','==Codex.CAM_DIST_')
        (out/'GuidedHarness.java').write_text(harness, encoding='utf8')
        result = subprocess.run(['javac','-d',str(out),str(out/'CampaignEngine.java'),*java_files,str(out/'GuidedHarness.java')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        for mode in ['complete','skip']:
            result = subprocess.run(['java','-cp',str(out),'GuidedHarness',mode],cwd=out,capture_output=True,text=True)
            (out/(mode+'.log')).write_text(result.stdout+result.stderr,encoding='utf8')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        (out/'verification.json').write_text(json.dumps(dict(tours=['complete','skip'], native_engine_test=False),indent=2),encoding='utf8')
