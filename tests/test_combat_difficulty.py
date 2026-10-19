"""Optional combat modifiers: real generation/compilation and API doubles.

These tests do not observe native combat balance or native save serialization.
"""
import copy,hashlib,json,os,subprocess,tempfile,zipfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QComboBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.combat_difficulty import MODIFIERS,selected
from rcm.editor.window import MainWindow
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]


def source(mode=None,dynamic=False):
    root=blank();root['chronicle']['id']='diff_test';root['scenes']=root['scenes'][:1]
    if mode is not None:root['chronicle']['difficulty']=mode
    s=root['scenes'][0];t=copy.deepcopy(s['entries'][0]['transform'])
    s['actors']=[dict(id='foe',name='Foe',template='Rat',behavior='enemy',transform=copy.deepcopy(t)),dict(id='mentor',name='Mentor',template='businessWoman',transform=copy.deepcopy(t))]
    s['events']=[dict(id='start',when='scene_start',actions=[dict(spawn='foe'),dict(spawn='mentor')])]
    if dynamic:
        root['project_format']=10;root['state']['flags']={'half':0,'low':1}
        s['waypoints']=[dict(id='p',name='Spawn',transform=copy.deepcopy(t))]
        group=lambda role,team:dict(role=role,template='Rat',count=1,health=50,team=team)
        groups=[group('hostile',12),group('ally',0),group('neutral',10),dict(role='talker',template='businessWoman',count=1,health=50,team=12)]
        s['generators']=[dict(id='group',name='Group',mode='ambush',spawn_points=['p'],max_alive=4,waves=[dict(groups=groups)]),dict(id='boss',name='Boss',mode='boss',spawn_points=['p'],max_alive=1,waves=[dict(groups=[dict(role='boss',template='Rat',count=1,health_multiplier=2)])],boss=dict(role='boss'),phases=[dict(id='half',percent=50,actions=[dict(set_flag='half'),dict(reward_xp=7)]),dict(id='low',value=40,actions=[dict(set_flag='low')])])]
        s['events'][0]['actions']+=[dict(start_generator='group'),dict(start_generator='boss')]
    return root


def doubles(code):
    code=code.replace('class CE {','class CE {')
    code=code.replace('float health=100,maxHealth=100;', 'float health=100,maxHealth=100; int flags=0,scaleWrites=0; float[] base=new float[]{40,40,40},stats=new float[]{40,40,40};')
    code=code.replace('x.template=t;','x.template=t;if(t.equals("businessWoman"))x.flags=8;if(t.endsWith("_elite")){x.maxHealth=400;x.health=200;x.base[0]=80;x.stats[0]=80;}')
    code=code.replace('class Codex {','class Codex {static final int TEAM_ENEMY_FIRST=12,TEAM_ENEMY_LAST=19,ACTOR_STAT_STRENGTH=0,ACTOR_STAT_STAMINA=2;')
    code=code.replace('class CodexActor extends CodexThing {','''class CodexActor extends CodexThing {
      int GetActorFlags(){return CE.world.get(guid).flags;}
      float GetActorBaseStat(int s){return CE.world.get(guid).base[s];}
      float GetActorStat(int s){return CE.world.get(guid).stats[s];}
      float SetActorBaseStat(int s,float v){CE.world.get(guid).scaleWrites++;return CE.world.get(guid).base[s]=v;}
      float SetActorStat(int s,float v){return CE.world.get(guid).stats[s]=v;}
    ''')
    code=code.replace('int SetActorFlags(int f){return f;}','int SetActorFlags(int f){return CE.world.get(guid).flags|=f;}').replace('int ClearActorFlags(int f){return f;}','int ClearActorFlags(int f){return CE.world.get(guid).flags&=~f;}')
    return code


class CombatDifficulty(TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT));cls.app=QApplication.instance() or QApplication([])
    def valid(self,root):
        report=self.backend.validate(root);self.assertTrue(report.valid,[p.message for p in report.problems]);return report.project
    def test_optional_value_formats_validation_and_lossless_roundtrip(self):
        for fmt in (9,10):
            for mode in (None,*MODIFIERS):
                root=source(mode);root['project_format']=fmt;self.valid(root)
                with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                    path=Path(tmp)/'project.yaml';doc=CampaignDocument(self.backend.ws,root,path);doc.save();loaded=CampaignDocument.load(self.backend.ws,path)
                    self.assertEqual(loaded.snapshot(),root);self.assertEqual(selected(root),mode or 'normal');self.assertEqual(loaded.campaign['project_format'],fmt)
        for bad in ('Easy','unknown','',True,None,[],{}):
            root=source();root['chronicle']['difficulty']=bad;self.assertFalse(self.backend.validate(root).valid)
    def test_normal_runtime_is_identical_to_pre_feature_baseline(self):
        baselines=json.loads((ROOT/'tests/fixtures/combat_difficulty_normal.json').read_text())
        for dynamic in (False,True):
            original=self.valid(source(dynamic=dynamic));explicit=self.valid(source('normal',dynamic))
            code=runtime(original,*original.scenes[0])[1];self.assertEqual(code,runtime(explicit,*explicit.scenes[0])[1])
            self.assertNotIn('difficultyEnemy',code);self.assertEqual(hashlib.sha256(code.encode()).hexdigest(),baselines[str(dynamic)])
    def run_java(self,root,harness):
        campaign=self.valid(root);name=runtime(campaign,*campaign.scenes[0])[0]
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            out=Path(tmp);compile_scenario(out,campaign,harness.replace('SCENE',name),doubles)
            run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('PASS',run.stdout)
    def test_fresh_manual_scaling_all_presets_preserves_ratios_and_npc(self):
        for mode,(hp,stat,defense) in MODIFIERS.items():
            self.run_java(source(mode),MANUAL.replace('HEALTH',str(100*hp)+'f').replace('STRENGTH',str(40*stat)+'f').replace('STAMINA',str(40*defense)+'f').replace('WRITES','0' if mode=='normal' else '2'))
    def test_dynamic_team_overrides_boss_thresholds_and_restore(self):self.run_java(source('nightmare',True),DYNAMIC)
    def test_relative_enemy_strength_and_wounded_health_ratio_are_preserved(self):
        root=source('hard');elite=copy.deepcopy(root['scenes'][0]['actors'][0]);elite.update(id='elite',name='Elite',template='Wolf');root['scenes'][0]['actors'].append(elite);root['scenes'][0]['events'][0]['actions'].append(dict(spawn='elite'))
        self.run_java(root,'''public class StabilityHarness {public static void main(String[] x){CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);CE.Thing weak=CE.world.get(CodexThing.GuidFromCastID("R_diff_test_s0_foe")),elite=CE.world.get(CodexThing.GuidFromCastID("R_diff_test_s0_elite"));if(Math.abs(elite.maxHealth/weak.maxHealth-4)>.001||Math.abs(elite.health/elite.maxHealth-.5)>.001||Math.abs(elite.stats[0]/weak.stats[0]-2)>.001)throw new AssertionError("relative values changed");System.out.println("PASS");}}''')
    def test_existing_guid_is_not_reinitialised_by_difficulty(self):
        self.run_java(source('hard'),'''public class StabilityHarness {public static void main(String[] x)throws Exception {CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);int existing=CE.make("R_diff_test_s0_foe",new float[]{0,0,0});CE.world.get(existing).health=33;SCENE s=new SCENE();s.beginscene(1,0);if(CE.world.get(existing).health!=33||CE.world.get(existing).scaleWrites!=0)throw new AssertionError("existing GUID scaled");System.out.println("PASS");}}''')
    def test_dead_neutral_player_and_client_guards(self):
        self.run_java(source('hard'),'''public class StabilityHarness {public static void main(String[] x)throws Exception {CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();java.lang.reflect.Method scale=SCENE.class.getDeclaredMethod("difficultyEnemy",int.class);scale.setAccessible(true);scale.invoke(s,1);int dead=CE.make("Rat",new float[]{0,0,0});CE.world.get(dead).health=0;scale.invoke(s,dead);int n=CE.make("businessWoman",new float[]{0,0,0});scale.invoke(s,n);int ally=CE.make("Rat",new float[]{0,0,0});CE.world.get(ally).team=0;scale.invoke(s,ally);CE.client=true;int client=CE.make("Rat",new float[]{0,0,0});scale.invoke(s,client);for(int g:new int[]{1,dead,n,ally,client})if(CE.world.get(g).scaleWrites!=0)throw new AssertionError("excluded actor scaled");System.out.println("PASS");}}''')
    def test_inspector_selection_persists_and_undo_is_atomic(self):
        w=MainWindow(self.backend);w.doc=CampaignDocument(self.backend.ws,source());w.refresh();w.select(('chronicle',));before=w.doc.snapshot()
        box=w.properties.widget().findChild(QComboBox,'chronicle_difficulty');self.assertEqual(box.currentData(),'normal');box.setCurrentIndex(box.findData('hard'))
        self.assertEqual(w.doc.snapshot()['chronicle']['difficulty'],'hard');w.undo_project();self.assertEqual(w.doc.snapshot(),before);w.redo_project();self.assertEqual(w.doc.snapshot()['chronicle']['difficulty'],'hard');w.doc=None;w.close()
    def test_real_codex_builds_and_normal_package_and_save_contract_identical(self):
        normal=source();normal['chronicle']['id']='diff_compile';first=self.backend.build(normal)
        nob=ROOT/'build/diff_compile/diff_compile.nob';original=nob.read_bytes();normal['chronicle']['difficulty']='normal';second=self.backend.build(normal)
        self.assertEqual(original,nob.read_bytes());self.assertEqual(first['save_schema_sha256'],second['save_schema_sha256'])
        root=source('normal',True);root['chronicle']['id']='diff_compile';contract=self.backend.build(root)['save_schema_sha256']
        for mode in ('easy','hard','nightmare'):
            root=source(mode,True);root['chronicle']['id']='diff_compile';report=self.backend.build(root)
            self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()));self.assertEqual(report['combat_difficulty'],mode);self.assertTrue(report['new_game_required']);self.assertIn('dificultad',report['save_warning'])
            self.assertEqual(report['save_schema_sha256'],contract)
            with zipfile.ZipFile(nob) as z:self.assertFalse(any(n.endswith('.nil') for n in z.namelist()))
        from rcm.build_transaction import failed_report
        failed_report(self.backend.ws,root,'Synthetic failed rebuild')
        self.assertEqual(json.loads((ROOT/'build/diff_compile/build_report.json').read_text())['combat_difficulty'],'nightmare')
        root['chronicle']['difficulty']='normal';report=self.backend.build(root);self.assertEqual(report['save_schema_sha256'],contract);self.assertTrue(report['new_game_required']);self.assertNotIn('combat_difficulty',report)


MANUAL='''public class StabilityHarness {
 static void check(boolean v,String why){if(!v)throw new AssertionError(why);} static void near(float a,float b){check(Math.abs(a-b)<.001f,"value "+a+" != "+b);}
 public static void main(String[] x)throws Exception {
 CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);
 int g=CodexThing.GuidFromCastID("R_diff_test_s0_foe"),npc=CodexThing.GuidFromCastID("R_diff_test_s0_mentor");CE.Thing e=CE.world.get(g);
 near(e.maxHealth,HEALTH);near(e.health,HEALTH);near(e.base[0],STRENGTH);near(e.stats[2],STAMINA);check(e.scaleWrites==WRITES,"write count");near(CE.world.get(npc).health,100);check(CE.world.get(npc).scaleWrites==0,"NPC changed");near(p.health,100);
 e.health=17;s.save(0);int count=CE.created;SCENE restored=new SCENE();restored.restore(0);restored.restored(0);restored.beginscene(1,0);for(int i=0;i<25;i++)restored.timer(9400,0,0,0,0);
 near(e.health,17);check(e.scaleWrites==WRITES&&CE.created==count,"restore rescaled/duplicated");System.out.println("PASS");}}
'''

DYNAMIC='''public class StabilityHarness {
 static void check(boolean v,String why){if(!v)throw new AssertionError(why);} static void near(float a,float b){check(Math.abs(a-b)<.001f,"value "+a+" != "+b);}
 static int[][] guids(SCENE s)throws Exception {java.lang.reflect.Field f=SCENE.class.getDeclaredField("dGuid");f.setAccessible(true);return (int[][])f.get(s);}
 static void tick(SCENE s){s.timer(9400,0,0,0,0);}
 public static void main(String[] x)throws Exception {
 CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);for(int i=0;i<5;i++)tick(s);int[][] ids=guids(s);
 near(CE.world.get(ids[0][0]).health,75);near(CE.world.get(ids[0][0]).base[0],48);check(CE.world.get(ids[0][0]).scaleWrites==2,"hostile scale");
 for(int i=1;i<4;i++){near(CE.world.get(ids[0][i]).health,50);check(CE.world.get(ids[0][i]).scaleWrites==0,"team/neutral exclusion");}
 CE.Thing boss=CE.world.get(ids[1][0]);near(boss.maxHealth,300);near(boss.health,300);boss.health=140;tick(s);check(CE.flags[0]&&CE.xp==7,"scaled percent phase");boss.health=30;tick(s);check(CE.flags[1],"absolute phase");
 s.save(0);int count=CE.created;SCENE r=new SCENE();r.restore(0);r.restored(0);r.beginscene(1,0);for(int i=0;i<25;i++)tick(r);
 near(boss.health,30);near(boss.maxHealth,300);check(boss.scaleWrites==2&&CE.created==count&&CE.xp==7,"restore duplicated scaling/reward");System.out.println("PASS");}}
'''
