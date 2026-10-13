"""Real generated Java + native API doubles, never a native-game acceptance."""
import copy,json,subprocess,tempfile,time,unittest
from pathlib import Path
import yaml
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/tests').mkdir(parents=True,exist_ok=True)

def fixture():
    root=yaml.safe_load((ROOT/'tests/fixtures/chronicles/dynamic_lab/project.yaml').read_text(encoding='utf8'))
    root['state']['flags']={'half':0,'quarter':1,'finished':2};s=root['scenes'][0];s['events']=[]
    base=s['generators'][0]
    other=copy.deepcopy(s['waypoints'][0]);other['id']='spawn_b';other['transform']['position'][0]+=100;s['waypoints'].append(other);base['spawn_points'].append('spawn_b')
    continuous=copy.deepcopy(base);continuous.update(id='continuous',mode='continuous',interval=.3,max_alive=3,max_total=5,waves=[{'groups':[{'role':'rats','template':'Rat','count':1},{'role':'wolves','template':'Wolf','count':2,'weight':2}]}])
    adds=copy.deepcopy(base);adds.update(id='adds',mode='reinforcements',max_alive=2,waves=[{'groups':[{'role':'adds','template':'Rat','count':2,'health_multiplier':.5}]}])
    boss=copy.deepcopy(base);boss.update(id='boss',mode='boss',max_alive=1,waves=[{'groups':[{'role':'boss','template':'Rat','count':1,'health_multiplier':2}]}],boss={'role':'boss'},phases=[{'id':'half','percent':50,'actions':[{'set_flag':'half'},{'start_generator':'adds'}]},{'id':'quarter','percent':25,'actions':[{'set_flag':'quarter'}]}])
    ambush=copy.deepcopy(base);ambush.update(id='ambush',mode='ambush',max_alive=2,waves=[{'groups':[{'role':'rats','template':'Rat','count':2}]}])
    cycle=copy.deepcopy(ambush);cycle['id']='cycle'
    authored=copy.deepcopy(boss);authored['id']='authored';authored['boss']={'actor':'static_boss'};authored['waves']=[{'groups':[]}];authored['phases']=[{'id':'half','percent':50,'actions':[{'set_flag':'half'}]},{'id':'low','value':20,'once':False,'actions':[{'set_flag':'quarter'},{'reward_xp':2}]}]
    s['actors']=[{'id':'static_boss','name':'Static boss','template':'Rat','behavior':'enemy','transform':copy.deepcopy(s['waypoints'][0]['transform'])}]
    cooldown=copy.deepcopy(ambush);cooldown.update(id='cooldown',persistence='cooldown',cooldown=1.8)
    s['generators']=[base,continuous,adds,boss,ambush,cycle,authored,cooldown]
    s['events']=[{'id':'done','when':'generator_complete','generator':'boss','once':True,'actions':[{'set_flag':'finished'},{'reward_xp':5},{'stop_generator':'continuous'}]}]
    s['events'] += [{'id':'cycle_stop','when':'generator_started','generator':'cycle','actions':[{'stop_generator':'cycle'}]},{'id':'cycle_start','when':'generator_stopped','generator':'cycle','actions':[{'start_generator':'cycle'}]}]
    return root

class DynamicValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.backend=Backend(Workspace(ROOT))
    def test_formats_9_10_and_future_gate(self):
        self.assertTrue(self.backend.validate(fixture()).valid)
        self.assertTrue(self.backend.validate((ROOT/'chronicles/tutorial/project.yaml').read_text(encoding='utf8')).valid)
        data=fixture();data['project_format']=11;self.assertFalse(self.backend.validate(data).valid)
        data['project_format']=9;self.assertFalse(self.backend.validate(data).valid)
    def test_shared_point_lists_serialize_without_forbidden_yaml_aliases(self):
        from rcm.service import source_text
        from rcm.input_limits import parse_source
        data=fixture();shared=data['scenes'][0]['generators'][0]['spawn_points']
        for g in data['scenes'][0]['generators']:g['spawn_points']=shared
        text=source_text(data);self.assertNotIn('&id',text);self.assertEqual(parse_source(text),data);self.assertTrue(self.backend.validate(text).valid)
    def test_limits_and_invalid_groups_points_thresholds(self):
        for mutation in [lambda g:g.update(max_alive=0),lambda g:g.update(interval=.01),lambda g:g.update(spawn_points=['missing']),lambda g:g.update(waves=[{'groups':[]}]),lambda g:g['waves'][0]['groups'][0].update(template='unknown')]:
            data=fixture();mutation(data['scenes'][0]['generators'][0]);self.assertFalse(self.backend.validate(data).valid)
        data=fixture();g=data['scenes'][0]['generators'][3];g['phases'].append({'id':'another','percent':50,'actions':[{'set_flag':'half'}]});self.assertFalse(self.backend.validate(data).valid)
    def test_phase_actions_use_existing_validation(self):
        data=fixture();data['scenes'][0]['generators'][3]['phases'][0]['actions']=[{'start_quest':'missing'}]
        self.assertFalse(self.backend.validate(data).valid)
    def test_general_health_counter_and_state_conditions(self):
        for condition in [{'actor_health':{'generator':'boss','role':'boss','comparison':'<=','value':20}}, {'actor_health':{'generator':'boss','role':'boss','comparison':'>','percent':50}}, {'generator_count':{'generator':'continuous','counter':'alive','comparison':'<=','value':1}}, {'generator_state':{'generator':'boss','state':'complete'}}]:
            data=fixture();data['scenes'][0]['events'].append({'id':'sample','when':'state_changed','conditions':[condition],'actions':[{'set_flag':'half'}]});self.assertTrue(self.backend.validate(data).valid)
    def test_activation_and_unbounded_warnings(self):
        data=fixture();data['scenes'][0]['generators'][1]['max_total']=0
        messages=[p.message for p in self.backend.validate(data).problems]
        self.assertTrue(any('sin vía de activación' in p for p in messages))
        data['scenes'][0]['events']=[];messages=[p.message for p in self.backend.validate(data).problems];self.assertTrue(any('sin límite total' in p for p in messages))
    def test_continuous_health_role_must_have_one_living_target(self):
        data=fixture();scene=data['scenes'][0];scene['events'].append({'id':'health_watch','when':'state_changed','conditions':[{'actor_health':{'generator':'continuous','role':'rats','comparison':'<=','percent':50}}],'actions':[{'set_flag':'half'}]})
        self.assertFalse(self.backend.validate(data).valid)
        scene['generators'][1]['max_alive']=1;self.assertTrue(self.backend.validate(data).valid)

class DynamicJava(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');cls.folder=Path(cls.temp.name)
        cls.backend=Backend(Workspace(ROOT));valid=cls.backend.validate(fixture());assert valid.valid
        scene,project=valid.project.scenes[0];cls.name,java=runtime(valid.project,scene,project)
        (cls.folder/(cls.name+'.java')).write_text(java,encoding='utf8')
        engine=(ROOT/'tests/java/CampaignEngine.java').read_text(encoding='utf8')
        engine=engine.replace('boolean SetOrientation(float[] a)','boolean SetPosition(float[] a){CE.world.get(guid).pos=a.clone();return true;} boolean SetOrientation(float[] a)')
        engine=engine.replace('int SetActorTeam(int t)','boolean SendActorToPos(float[] p,float speed){CE.world.get(guid).pos=p.clone();return true;} int SetActorTeam(int t)')
        # Native SetTimer appends. KillTimer removes that ID; model this here.
        engine=engine.replace('static int read=0;','static int read=0;static List<Integer> timers=new ArrayList<Integer>();')
        engine=engine.replace('static boolean valid(int g)', 'static boolean failPosition=false,failCreate=false;static boolean valid(int g)')
        engine=engine.replace('CE.world.get(guid).pos=a.clone();return true;', 'if(CE.failPosition)return false;CE.world.get(guid).pos=a.clone();return true;')
        engine=engine.replace('return CE.make(name,p);','return CE.failCreate?0:CE.make(name,p);')
        engine=engine.replace('boolean SetTimer(float s,int id){return true;}boolean KillTimer(int id){return true;}','boolean SetTimer(float s,int id){CE.timers.add(id);return true;}boolean KillTimer(int id){while(CE.timers.remove(Integer.valueOf(id))){}return true;}')
        (cls.folder/'CampaignEngine.java').write_text(engine,encoding='utf8')
        (cls.folder/'DynamicHarness.java').write_text(HARNESS.replace('CONTROLLER',cls.name),encoding='utf8')
        run=subprocess.run(['javac','-d',str(cls.folder),str(cls.folder/'CampaignEngine.java'),str(cls.folder/(cls.name+'.java')),str(cls.folder/'DynamicHarness.java')],capture_output=True,text=True)
        if run.returncode:raise AssertionError(run.stderr)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def scenario(self,name):
        run=subprocess.run(['java','-cp',str(self.folder),'DynamicHarness',name],capture_output=True,text=True,timeout=20)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('PASS '+name,run.stdout)
    def test_waves_wait_for_clear_then_delay_and_complete(self):self.scenario('waves')
    def test_continuous_cap_interval_max_total_and_replacement(self):self.scenario('continuous')
    def test_bounded_failure_retry_and_stop_after_error(self):self.scenario('failure')
    def test_pause_resume_and_stop_keep_live_actors(self):self.scenario('pause')
    def test_generated_boss_crossings_only_and_lethal_jump(self):self.scenario('boss')
    def test_absolute_health_and_multiplier_preserve_other_actors(self):self.scenario('health')
    def test_midwave_restore_no_duplicate_or_repeated_wave(self):self.scenario('save')
    def test_threshold_restore_no_duplicate_rewards_or_actions(self):self.scenario('boss_save')
    def test_missing_restored_actor_stalls_without_respawn(self):self.scenario('missing')
    def test_once_reentry_reset_and_completed_restore(self):self.scenario('reentry')
    def test_authored_boss_percentage_and_absolute_hp(self):self.scenario('static')
    def test_lethal_hit_skips_threshold_without_predeath_promise(self):self.scenario('lethal')
    def test_missing_reentry_records_fail_closed(self):self.scenario('cold')
    def test_remove_on_stop_only_removes_owned_slots(self):self.scenario('cleanup')
    def test_single_timer_and_client_guard(self):self.scenario('timer')
    def test_multiple_points_preserve_transforms(self):self.scenario('points')
    def test_callback_cycles_are_bounded(self):self.scenario('cycles')
    def test_native_factory_fallback_and_near_player(self):self.scenario('fallback')
    def test_failed_position_never_counts_an_enemy(self):self.scenario('position_failure')
    def test_random_pool_and_points_stay_within_the_authored_set(self):self.scenario('random')
    def test_pause_save_and_stream_batch_cursor(self):self.scenario('batch_save')
    def test_reset_on_reentry_preserves_other_generators(self):self.scenario('reset_policy')
    def test_resume_on_reentry_preserves_owned_guids(self):self.scenario('resume_policy')
    def test_cooldown_defers_restart_and_is_saved(self):self.scenario('cooldown')
    def test_repeatable_threshold_requires_healing_and_a_new_crossing(self):self.scenario('repeat_phase')
    def test_corrupt_saved_slot_fails_closed(self):self.scenario('invalid_slot')
    def test_long_continuous_run_keeps_slots_records_and_timer_bounded(self):self.scenario('long_run')
    def test_real_codex_compile_and_stress_bytecode_budget(self):
        data=fixture();s=data['scenes'][0];s['events']=[];g=copy.deepcopy(s['generators'][0]);s['generators']=[]
        for i in range(20):
            row=copy.deepcopy(g);row['id']='waves'+str(i);row['max_alive']=4;row['waves']=[{'groups':[{'role':'rats','template':'Rat','count':2},{'role':'others','template':'Wolf' if i%2 else 'Skel_Sword','count':1}]} for _ in range(10)]
            s['generators'].append(row)
            s['events'].append({'id':'start'+str(i),'when':'timer','seconds':i+1,'actions':[{'start_generator':row['id']}]})
            s['events'].append({'id':'finish'+str(i),'when':'generator_complete','generator':row['id'],'once':True,'actions':[{'set_flag':'finished'},{'stop_generator':'waves'+str((i+1)%20)}]})
        for i in range(5):
            row=copy.deepcopy(g);row.update(id='watch'+str(i),mode='boss',max_alive=1,waves=[{'groups':[]}],boss={'actor':'static_boss'},phases=[{'id':'half','percent':50,'actions':[{'start_generator':'waves'+str(i)}]},{'id':'quarter','value':20,'actions':[{'pause_generator':'waves'+str(i)}]}]);s['generators'].append(row)
        data['chronicle']['id']='dyn_stress'
        started=time.perf_counter();report=self.backend.build(data,True);self.assertEqual(report['status'],'compiled-unverified-in-game');self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        from rcm.classfile_limits import inspect_class
        metrics={p.name:inspect_class(p.read_bytes()) for p in (ROOT/'build/dyn_stress/bundle/codex').glob('*.class')}
        self.assertTrue(metrics);self.assertTrue(all(m['largest_method_bytes']<65535 and m['constant_pool_entries']<65534 for m in metrics.values()))
        (ROOT/'research/dynamic_encounters/stress.json').write_text(json.dumps(dict(generators=25,waves=205,enemy_entries=400,templates=['Rat','Wolf','Skel_Sword'],points=2,thresholds=10,callbacks=40,slots=85,build_seconds=time.perf_counter()-started,class_metrics=metrics,native_engine_test=False),indent=2),encoding='utf8')

HARNESS=r'''
import java.lang.reflect.*;import java.util.*;
public class DynamicHarness {
 static CONTROLLER c=new CONTROLLER();
 static Object field(String name)throws Exception {Field f=c.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(c);}
 static Object call(String name,Class[] types,Object... args)throws Exception {Method m=c.getClass().getDeclaredMethod(name,types);m.setAccessible(true);return m.invoke(c,args);}
 static int state(int g)throws Exception{return ((int[])field("dState"))[g];}
 static int total(int g)throws Exception{return ((int[])field("dTotal"))[g];}
 static int[] guids(int g)throws Exception{return ((int[][])field("dGuid"))[g];}
 static int alive(int g)throws Exception{int n=0;for(int who:guids(g))if(who!=0)n++;return n;}
 static void command(int g,int cmd)throws Exception{call("dynamicCommand",new Class[]{int.class,int.class},g,cmd);}
 static void tick(int n)throws Exception{for(int i=0;i<n;i++)c.timer(9400,0,0,0,0);}
 static void kill(int g)throws Exception{for(int who:guids(g).clone())if(who!=0){CE.world.get(who).health=0;c.killed(who,1,0);}}
 static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
 static void save()throws Exception{CE.save.clear();CE.read=0;c.save(0);c=new CONTROLLER();c.restore(0);c.restored(0);tick(4);}
 public static void main(String[] args)throws Exception{
  CE.Thing player=new CE.Thing();player.template="Player";CE.world.put(1,player);c.beginscene(1,0);tick(3);String test=args[0];
  if(test.equals("waves")){command(0,0);tick(1);check(alive(0)==3,"wave1");tick(30);check(total(0)==3,"await clear");kill(0);tick(1);check(alive(0)==0,"delay");tick(15);check(alive(0)==2,"wave2");kill(0);tick(2);check(state(0)==3,"complete");command(0,0);tick(20);check(total(0)==5,"once");}
  if(test.equals("continuous")){command(1,0);tick(20);check(alive(1)==3&&total(1)==3,"cap");kill(1);tick(20);check(total(1)==5&&alive(1)==2,"total");kill(1);tick(3);check(state(1)==3,"drain to complete");}
  if(test.equals("failure")){CE.failSpawn=true;command(0,0);tick(30);check(state(0)==5&&total(0)==0,"bounded failure");CE.failSpawn=false;tick(100);check(total(0)==0,"no error loop");}
  if(test.equals("pause")){command(1,0);tick(1);command(1,2);int count=total(1);tick(20);check(total(1)==count,"pause");command(1,3);tick(10);check(total(1)>count,"resume");command(1,1);count=CE.created;tick(20);check(CE.created==count&&alive(1)>0,"stop preserves live");}
  if(test.equals("boss")||test.equals("boss_save")){command(3,0);tick(1);int boss=guids(3)[0];CE.world.get(boss).health=120;tick(1);CE.world.get(boss).health=98;tick(3);check(CE.flags[0]&&alive(2)==2,"50 crossing adds");int created=CE.created;if(test.equals("boss_save"))save();tick(3);check(CE.created==created,"threshold once");CE.world.get(boss).health=40;tick(3);check(CE.flags[1],"25 crossing");kill(3);tick(3);check(CE.flags[2]&&CE.xp==5,"death reward");save();tick(5);check(CE.xp==5,"no duplicate reward");}
  if(test.equals("health")){command(2,0);tick(2);for(int who:guids(2))check(CE.world.get(who).health==50&&CE.world.get(who).maxHealth==50,"multiplier native baseline");check(CE.world.get(1).health==100,"player unchanged");}
  if(test.equals("save")){command(0,0);tick(1);int count=CE.created;save();check(CE.created==count&&alive(0)==3,"midwave restore");kill(0);tick(16);check(total(0)==5,"wave cursor restored");}
  if(test.equals("missing")){command(0,0);tick(1);int who=guids(0)[0];CE.save.clear();CE.read=0;c.save(0);CE.world.remove(who);int count=CE.created;c=new CONTROLLER();c.restore(0);c.restored(0);tick(40);check(state(0)==5&&CE.created==count,"fail closed missing guid");}
  if(test.equals("reentry")){command(4,0);tick(2);kill(4);tick(2);c.beginscene(1,0);command(4,0);tick(5);check(total(4)==2&&state(4)==3,"once reentry");save();check(state(4)==3,"completed restored");command(4,4);command(4,0);tick(2);check(total(4)==2&&alive(4)==2,"explicit reset");}
  if(test.equals("timer")){command(0,0);tick(40);check(CE.timers.size()==1&&CE.timers.get(0)==9400,"one poll queue");CE.client=true;int count=CE.created;command(1,0);tick(10);check(CE.created==count,"client no spawn");}
  if(test.equals("points")){command(0,0);tick(1);Set<Float> xs=new HashSet<Float>();for(int who:guids(0)){check(CE.world.get(who).pos[2]==384,"authored height");xs.add(CE.world.get(who).pos[0]);}check(xs.size()==2,"rotating spawn points");}
  if(test.equals("cycles")){command(5,0);tick(10);check(state(5)==5&&total(5)==0,"bounded callback cycle");}
  if(test.equals("static")){call("spawn",new Class[]{int.class},0);int who=((int[])field("things"))[0];command(6,0);tick(2);CE.world.get(who).health=49;tick(2);check(CE.flags[0],"static 50");CE.world.get(who).health=19;tick(2);check(CE.flags[1],"absolute HP");}
  if(test.equals("lethal")){command(3,0);tick(1);int who=guids(3)[0];CE.world.get(who).health=120;tick(1);CE.world.get(who).health=0;tick(2);check(!CE.flags[0]&&!CE.flags[1]&&state(3)==3,"lethal can skip phases");}
  if(test.equals("cold")){command(0,0);tick(1);int created=CE.created;c=new CONTROLLER();c.beginscene(1,0);command(0,0);tick(20);check(state(0)==5&&CE.created==created,"cold roster protection");}
  if(test.equals("cleanup")){command(0,0);command(4,0);tick(2);int other=guids(0)[0];((boolean[])field("dRemove"))[4]=true;command(4,1);check(alive(4)==0&&CE.valid(other)&&CE.valid(1),"only owned removal");}
  if(test.equals("fallback")){CE.failCreate=true;command(0,0);tick(1);check(alive(0)==3,"fallback factory");for(int who:guids(0))check(CE.world.get(who).pos[2]==384,"fallback authored position");((boolean[])field("dNear"))[4]=true;CE.world.get(1).pos=new float[]{7,8,9};command(4,0);tick(1);check(CE.world.get(guids(4)[0]).pos[0]==7,"near player");}
  if(test.equals("position_failure")){CE.failPosition=true;command(0,0);tick(30);check(state(0)==5&&total(0)==0&&alive(0)==0&&CE.world.size()==1,"failed transform removes fresh actor");}
  if(test.equals("random")){((boolean[])field("dRandom"))[1]=true;((boolean[])field("dRandomPoint"))[1]=true;command(1,0);tick(30);check(alive(1)==3,"random cap");float a=-62,b=38;for(int who:guids(1)){check(CE.world.get(who).pos[0]==a||CE.world.get(who).pos[0]==b,"random authored points");check(CE.world.get(who).template.equals("Rat")||CE.world.get(who).template.equals("Wolf"),"random authored pool");}for(int i=0;i<100;i++){((int[])field("dStreamLeft"))[1]=0;int entry=((Integer)call("dynamicEntry",new Class[]{int.class},1)).intValue();check(entry==0||entry==1,"weighted pool stays bounded");}}
  if(test.equals("batch_save")){((int[][])field("dCount"))[1][0]=3;command(1,0);tick(1);check(((int[])field("dStreamLeft"))[1]==2,"remaining batch");command(1,2);save();int count=CE.created;tick(20);check(state(1)==2&&CE.created==count&&((int[])field("dStreamLeft"))[1]==2,"paused save");command(1,3);tick(10);check(total(1)==3,"resume batch");}
  if(test.equals("reset_policy")){command(0,0);command(4,0);tick(2);int other=guids(0)[0],old=guids(4)[0];((int[])field("dPolicy"))[4]=2;c.beginscene(1,0);check(state(4)==0&&!CE.valid(old)&&CE.valid(other),"reset only owned on reentry");command(4,0);tick(2);check(alive(4)==2&&total(4)==2,"fresh reset");}
  if(test.equals("resume_policy")){((int[])field("dPolicy"))[4]=1;command(4,0);tick(2);int old=guids(4)[0],count=CE.created;c.beginscene(1,0);tick(5);check(guids(4)[0]==old&&CE.created==count&&state(4)==1,"resume roster");}
  if(test.equals("cooldown")){command(7,0);tick(2);kill(7);tick(1);check(state(7)==3,"cooldown complete");save();check(state(7)==3&&total(7)==2,"save cooldown");tick(20);check(state(7)==1&&alive(7)==2,"cooldown restart");}
  if(test.equals("repeat_phase")){call("spawn",new Class[]{int.class},0);int who=((int[])field("things"))[0];command(6,0);tick(1);CE.world.get(who).health=19;tick(2);check(CE.xp==2,"first crossing");tick(20);check(CE.xp==2,"no repeat below");CE.world.get(who).health=30;tick(1);CE.world.get(who).health=19;tick(2);check(CE.xp==4,"new crossing");}
  if(test.equals("invalid_slot")){command(0,0);tick(1);((int[][])field("dSlotEntry"))[0][0]=999;int count=CE.created;save();check(state(0)==5,"invalid slot rejected");command(0,4);command(0,0);tick(20);check(state(0)==5&&CE.created==count,"invalid ownership cannot reset");command(0,1);command(0,0);tick(20);check(state(0)!=1&&CE.created==count,"stop cannot bypass unsafe ownership");}
  if(test.equals("long_run")){((int[])field("dLimit"))[1]=0;command(1,0);int records=-1;long started=System.nanoTime();for(int i=0;i<1000;i++){tick(12);check(alive(1)<=3&&guids(1).length==3,"fixed active slots");int[] old=guids(1).clone();kill(1);for(int who:old)if(who!=0)CE.world.remove(who);CE.save.clear();c.save(0);if(records<0)records=CE.save.size();check(records==CE.save.size()&&CE.timers.size()==1,"fixed records and timer");}check(total(1)>=1000&&state(1)==1,"long continuous progress");System.out.println("SIMULATED_LOOP_MS "+((System.nanoTime()-started)/1000000)+" records="+records+" total="+total(1));}
  System.out.println("PASS "+test);
 }
}
'''
