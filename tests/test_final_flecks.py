"""Surgical closure: real Codex signatures, bounded NSD and shared Actions."""
import copy,json,math,re,struct,subprocess,tempfile,zipfile
from pathlib import Path
from unittest import TestCase
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.formats import Scene
from rcm.native_arrivals import conversation_groups,conversation_records
from rcm.campaign_generator import runtime
from rcm.campaign_document import CampaignDocument
from rcm.safe_edit import deletion_plan
from rcm.camera_paths import CameraPath,authored
from test_release10 import blank

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')


def source():
    root=blank();root['chronicle']['id']='fleck_test';s=root['scenes'][0]
    s['actors']=[dict(id='mentor',name='Elena',template='Anezka',transform=dict(position=[-176,-612,384],orientation=[0,0,180]))]
    s['entries'].append(dict(id='companion',name='Companion',transform=dict(position=[-176,-768,384],orientation=[0,0,90])))
    s['conversations']=[dict(id='talk',speaker='mentor',entry='hello',nodes=[dict(id='hello',lines=[dict(text='Welcome.')],choices=[dict(text='Continue',result=1)])])]
    s['events']=[dict(id='arrival',when='scene_start',actions=[{'spawn':'mentor'}])]
    return root


class FinalFlecks(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT,GAME))
    def valid(self,data):
        result=self.backend.validate(data);self.assertTrue(result.valid,[p.message for p in result.problems]);return result.project
    def test_music_validation_and_shared_line_cue_actions(self):
        data=source();s=data['scenes'][0]
        push={'push_music':dict(resource='London_Hub',volume=50)}
        s['events'][0]['actions'] += [push,{'pop_music':True}]
        s['conversations'][0]['nodes'][0]['lines'][0]['actions']=[push,{'pop_music':True}]
        s['sequences']=[dict(id='film',name='Film',actor='mentor',duration=2,shot='wide',angle='high',cues=[dict(at=0,actions=[push]),dict(at=1,actions=[{'pop_music':True}])])]
        p=self.valid(data);code=runtime(p,*p.scenes[0])[1]
        self.assertIn('CodexSound.PushMusic(name,volume)',code);self.assertIn('CodexSound.PopMusic()',code)
        self.assertIn('pushTemporaryMusic("London_Hub.mp3",50)',code)
        for volume in [-1,101,True,float('nan')]:
            bad=copy.deepcopy(data);bad['scenes'][0]['events'][0]['actions'][1]['push_music']['volume']=volume
            self.assertFalse(self.backend.validate(bad).valid)
        for value in [{'resource':'missing','volume':50},{'resource':'London_Hub','volume':50,'nested':True}]:
            bad=copy.deepcopy(data);bad['scenes'][0]['events'][0]['actions'][1]={'push_music':value};self.assertFalse(self.backend.validate(bad).valid)
        bad=copy.deepcopy(data);bad['scenes'][0]['events'][0]['actions'][2]={'pop_music':False};self.assertFalse(self.backend.validate(bad).valid)
        from test_dynamic_encounters import fixture
        boss=fixture();boss['scenes'][0]['generators'][3]['phases'][0]['actions']=[push,{'pop_music':True}]
        p=self.valid(boss);self.assertIn('pushTemporaryMusic("London_Hub.mp3",50)',runtime(p,*p.scenes[0])[1])

    def test_legacy_music_ambient_and_staging_do_not_gain_helpers(self):
        data=source();s=data['scenes'][0];s['conversations'][0]['staging']='start'
        s['events'][0]['actions'] += [{'start_music':'London_Hub'},{'stop_music':True},{'start_ambient':'amb_londonStreet'},{'stop_ambient':True}]
        p=self.valid(data);code=runtime(p,*p.scenes[0])[1]
        self.assertNotIn('temporaryMusicOwned',code)
        self.assertIn('CodexSound.StartMusic("London_Hub",100)',code);self.assertIn('CodexSound.StopAmbient()',code)
        self.assertIn('TeleportPartyToEntrance',code);self.assertNotIn('TeleportPartyToConversation',code)

    def test_native_staging_validation_groups_and_bounds(self):
        data=source();s=data['scenes'][0];s['conversations'][0]['staging']=dict(mode='native',entries=['start','companion'])
        p=self.valid(data);self.assertEqual(conversation_groups(s),[('start','companion')])
        self.assertIn('CodexPlayer.TeleportPartyToConversation(player,0)',runtime(p,*p.scenes[0])[1])
        for value in [dict(mode='native',entries=[]),dict(mode='native',entries=['missing']),dict(mode='native',entries=['start','start']),dict(mode='other',entries=['start']),dict(mode='native',entries=['start'],raw_index=7)]:
            bad=copy.deepcopy(data);bad['scenes'][0]['conversations'][0]['staging']=value;self.assertFalse(self.backend.validate(bad).valid)
        bad=copy.deepcopy(data);bad['scenes'][0]['entries'][0]['transform']['orientation'][0]=10;self.assertFalse(self.backend.validate(bad).valid)
        many=copy.deepcopy(s)
        for i in range(17):
            entry=copy.deepcopy(many['entries'][0]);entry['id']='p'+str(i);many['entries'].append(entry)
            c=copy.deepcopy(many['conversations'][0]);c['id']='c'+str(i);c['staging']['entries']=[entry['id']];many['conversations'].append(c)
        with self.assertRaisesRegex(ValueError,'16'):conversation_groups(many)

    def test_generated_nsd_conversation_table_roundtrip_and_tail_preservation(self):
        data=source();s=data['scenes'][0];s['conversations'][0]['staging']=dict(mode='native',entries=['start','companion'])
        level=self.backend.levels['EastLondon'];records=conversation_records(self.backend.ws,level,s)
        self.assertEqual(len(records),2);self.assertEqual([struct.unpack_from('<II',r,52) for r in records],[(0,0),(0,0)])
        tail=bytes(16)+bytes(range(176));model=Scene('scene','layout',[],tail,entrances=[records[0]],conversation_starts=records)
        raw=model.encode();read=Scene.read(raw);self.assertEqual(raw,read.encode());self.assertEqual(read.environment,tail)
        self.assertEqual(read.conversation_starts,records);self.assertEqual(read.entrances,[records[0]])
        row=struct.unpack('<I12fII',records[1]);self.assertAlmostEqual(row[1],0,places=5);self.assertAlmostEqual(row[2],-1,places=5)
        for bad in [raw[:-1],raw[:100],raw[:84]+bytes(12)+struct.pack('<I',65)+bytes(176)]:
            with self.assertRaises(ValueError):Scene.read(bad)
        invalid=bytearray(records[0]);struct.pack_into('<I',invalid,52,16)
        with self.assertRaises(ValueError):Scene('s','l',[],conversation_starts=[bytes(invalid)]).encode()
        invalid=bytearray(records[0]);struct.pack_into('<I',invalid,56,1)
        with self.assertRaises(ValueError):Scene('s','l',[],conversation_starts=[bytes(invalid)]).encode()

    def test_original_native_tables_match_proven_record_layout(self):
        from rcm.native_arrivals import validate_record
        tables=json.loads((ROOT/'research/embrace_closure/original_conversation_tables.json').read_text())
        self.assertEqual(len(tables),99);self.assertEqual(sum(t['count'] for t in tables),473)
        archives={}
        try:
            for table in tables:
                if table['archive'] not in archives:archives[table['archive']]=zipfile.ZipFile(GAME/table['archive'])
                z=archives[table['archive']]
                data=z.read(table['path']);at=table['offset'];self.assertEqual(struct.unpack_from('<I',data,at)[0],table['count'])
                for i,row in enumerate(table['records']):
                    raw=data[at+4+60*i:at+4+60*(i+1)]
                    self.assertEqual(validate_record(raw),struct.pack('<I12fII',*row));self.assertLessEqual(row[-2],15)
        finally:
            for archive in archives.values():archive.close()

    def test_native_marker_references_rename_and_safe_delete(self):
        data=source();data['scenes'][0]['conversations'][0]['staging']=dict(mode='native',entries=['start','companion'])
        doc=CampaignDocument(self.backend.ws,data);doc.rename('entries',1,'side');self.assertEqual(doc.data['conversations'][0]['staging']['entries'],['start','side'])
        plan=deletion_plan(doc,('scenes',0,'entries',1),self.backend);self.valid(plan.candidate)
        self.assertEqual(plan.candidate['scenes'][0]['conversations'][0]['staging']['entries'],['start'])
        doc=CampaignDocument(self.backend.ws,plan.candidate);plan=deletion_plan(doc,('scenes',0,'entries',0),self.backend)
        self.valid(plan.candidate);self.assertNotIn('staging',plan.candidate['scenes'][0]['conversations'][0]);self.assertEqual(len(plan.candidate['scenes'][0]['conversations']),1)

    def test_real_codex_build_packages_native_points_and_temporary_music(self):
        data=source();s=data['scenes'][0];s['conversations'][0]['staging']=dict(mode='native',entries=['start','companion'])
        s['events'][0]['actions'] += [{'push_music':dict(resource='London_Hub',volume=50)},{'pop_music':True}]
        report=self.backend.build(data);self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        with zipfile.ZipFile(ROOT/'build/fleck_test/fleck_test.nob') as z:
            model=Scene.read(z.read('scenes/R_fleck_test_s0.nsd'));self.assertEqual(len(model.conversation_starts),2)
        from rcm.packages import export_project,import_project,create_package,inspect_package
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            p=Path(tmp);export_project(self.backend.ws,data,p/'source.zip');doc=import_project(self.backend.ws,p/'source.zip',p/'imported')
            self.assertEqual(doc.snapshot()['scenes'][0]['conversations'][0]['staging'],s['conversations'][0]['staging'])
            create_package(self.backend.ws,'fleck_test',p/'test.rcmpack');self.assertEqual(inspect_package(p/'test.rcmpack')[0]['class_version'],'45.3')

    def test_stationary_original_keys_are_not_evidence_of_a_timed_hold(self):
        rows=json.loads((ROOT/'research/embrace_closure/ncp_catalogue.json').read_text());pairs=[]
        for row in rows:
            for a,b in zip(row['frames'],row['frames'][1:]):
                if math.dist(a[2:5],b[2:5])<.001:pairs.append((a,b))
        self.assertEqual(len(pairs),22);self.assertEqual(sum(a[14:17]!=b[14:17] for a,b in pairs),8)
        self.assertTrue(all(a[0]==b[0] for a,b in pairs))
        self.assertTrue(any(any(abs(c)>.001 for c in a[5:14]) for a,b in pairs))
        with self.assertRaises(ValueError):authored([dict(position=[0,0,0],orientation=[0,0,0]),dict(position=[0,0,0],orientation=[0,0,90])])

    def test_ncp_rejects_invalid_parameters_without_changing_duplicate_originals(self):
        path=authored([dict(position=[0,0,0],orientation=[0,0,0]),dict(position=[100,0,0],orientation=[0,0,90])])
        for at,value in [(8,-1),(112,-1),(112,200),(12,-1),(8,float('inf'))]:
            raw=bytearray(path.encode());struct.pack_into('<f',raw,at,value)
            with self.assertRaises(ValueError):CameraPath.read(bytes(raw))

    def test_music_owned_cleanup_nesting_foreign_and_restore_with_doubles(self):
        from test_stability_revision import compile_scenario
        data=source();data['scenes'][0]['events'].append(dict(id='temp',when='manual',actions=[{'push_music':dict(resource='London_Hub',volume=50)}]))
        data['scenes'][0]['sequences']=[dict(id='film',name='Film',actor='mentor',duration=2,shot='wide',angle='high',cues=[dict(at=0,actions=[{'push_music':dict(resource='London_Hub',volume=50)}]),dict(at=1,actions=[{'pop_music':True}])])]
        campaign=self.valid(data);name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness {
          static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
          static boolean push(SCENE s,String name)throws Exception{java.lang.reflect.Method m=SCENE.class.getDeclaredMethod("pushTemporaryMusic",String.class,int.class);m.setAccessible(true);return ((Boolean)m.invoke(s,name,50)).booleanValue();}
          static boolean pop(SCENE s)throws Exception{java.lang.reflect.Method m=SCENE.class.getDeclaredMethod("popTemporaryMusic");m.setAccessible(true);return ((Boolean)m.invoke(s)).booleanValue();}
          public static void main(String[] a)throws Exception{
           CE.Thing p=new CE.Thing();p.template="Player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);
           CodexSound.StartMusic("normal.mp3",70);check(!pop(s),"unowned rejected");check(CodexSound.pops==0,"no native pop");
           check(push(s,"temp.mp3"),"push");check(!push(s,"nested.mp3"),"nested rejected");check(CodexSound.aMusicName.equals("normal.mp3"),"snapshot not overwritten");
           check(pop(s),"pop");check(CE.music.equals("normal.mp3")&&CodexSound.currentVolume==70,"restored original volume");check(!pop(s),"no double pop");
           check(push(s,"temp.mp3"),"push again");CodexSound.PushMusic("foreign.mp3",60);check(!pop(s),"foreign snapshot rejected");check(CodexSound.pops==1&&CE.music.equals("foreign.mp3"),"foreign untouched");
           check(push(s,"temp.mp3"),"owned before load");s.save(0);SCENE loaded=new SCENE();loaded.restore(0);check(!pop(loaded),"restore cannot claim native snapshot");check(CodexSound.pops==1,"restore does not pop");
           s.endscene(1,0,0);check(CodexSound.pops==2,"owned end cleanup once");s.endscene(1,0,0);check(CodexSound.pops==2,"end idempotent");
           CodexSound.StartMusic("normal.mp3",70);SCENE film=new SCENE();film.beginscene(1,0);
           java.lang.reflect.Method begin=SCENE.class.getDeclaredMethod("beginCinema",int.class);begin.setAccessible(true);
           java.lang.reflect.Method stop=SCENE.class.getDeclaredMethod("releaseCamera");stop.setAccessible(true);
           check(((Boolean)begin.invoke(film,0)).booleanValue(),"film starts");check(CE.music.equals("London_Hub.mp3"),"cue pushes");stop.invoke(film);
           check(CE.music.equals("normal.mp3")&&CodexSound.pops==3,"cancel balances owned cue");
           check(((Boolean)begin.invoke(film,0)).booleanValue(),"film repeats");for(int i=0;i<20;i++)film.timer(9400,0,0,0,0);
           check(CE.music.equals("normal.mp3")&&CodexSound.pops==4,"explicit cue pop not repeated at end");
          }}'''.replace('SCENE',name)
        def doubles(text):
            sound='''class CodexSound extends Codex {static String aMusicName="";static int musicVolume=0,currentVolume=0,pops=0;
            static String GetMusicName(){return CE.music;} static int GetMusicVolume(){return currentVolume;}
            static boolean StartMusic(String name,int v){CE.music=name;currentVolume=v;return true;}static void StopMusic(){CE.music="";}
            static void PushMusic(String n,int v){aMusicName=GetMusicName();musicVolume=GetMusicVolume();StopMusic();StartMusic(n,v);}
            static void PopMusic(){pops++;StopMusic();StartMusic(aMusicName,musicVolume);}static boolean StartAmbient(String n,int v){return true;}static void StopAmbient(){}}
            '''
            text=text.replace('class CodexCamera extends Codex {','class CodexCamera extends Codex {static void ClearAllEffects(int p){}')
            return re.sub(r'class CodexSound extends Codex \{[^\n]*\}',lambda m:sound,text)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            out=Path(tmp);compile_scenario(out,campaign,harness,doubles)
            result=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
