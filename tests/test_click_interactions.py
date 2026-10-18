"""Native click links: format readback, authoring, safety and real Codex compile.

No native gameplay is automated. Java doubles cannot certify hit testing/UI.
"""
import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import struct
import subprocess
import tempfile
from unittest import TestCase
from PySide6.QtWidgets import QApplication,QDialog,QComboBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.campaign_generator import runtime
from rcm.click_interactions import validate,brush,surface
from rcm.formats import Scene,Tag,cstring
from rcm.spatial.scene_mesh import read_brush
from rcm.spatial.assets import Assets
from rcm.editor.original_objects import PassageDialog
from rcm.editor.window import MainWindow
from rcm.campaign_relations import graph
from rcm import recipes
from test_release10 import blank
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]


def mesh():return dict(materials=['London\\CTdoor_L'],vertices=[[-40,0,0,0,0],[40,0,0,1,0],[-40,0,160,0,1]],material_ids=[0],sector=1)
def source():
    root=blank();root['state']['flags']={'clicked':0};scene=root['scenes'][0]
    scene['objects']=[dict(id='door',name='Club entrance',template='tracker_thing',transform=dict(position=[0,0,0],orientation=[0,0,0]),interaction=mesh())]
    scene['events']=[dict(id='use',when='object_clicked',object='door',once=False,actions=[{'reward_xp':7},{'set_flag':'clicked'}])]
    return root


class ClickInteractions(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT,Path(r'H:\GOG\Vampire The Masquerade - Redemption')));cls.backend.safe_mode=True
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
    def valid(self,root):
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems if p.severity=='ERROR']);return result.project
    def test_brush_roundtrip_matches_original_native_record_layout(self):
        value=mesh();value['materials'].append('London\\CTdoor_L');value['vertices']+=value['vertices'];value['material_ids']=[1,0]
        body=brush(value);read=read_brush(body,0);self.assertEqual(read.material_ids.tolist(),[0,1]);self.assertEqual(len(body),read.source_end+100);self.assertEqual(struct.unpack_from('<I',body,read.source_end)[0],6)
        scene=Scene('Short','Long',[[Tag.text(0,'ghost')],[Tag.text(0,'tracker_thing'),Tag.text(82,'CLICK_DESC')]],brushes={1:body});encoded=scene.encode();decoded=Scene.read(encoded)
        self.assertEqual(decoded.encode(),encoded);self.assertEqual(decoded.brushes,{1:body});self.assertEqual(cstring(decoded.entities[1][1].value),'CLICK_DESC')
        with self.assertRaises(ValueError):Scene.read(encoded[:-1])
        bad=bytearray(encoded);offset=encoded.index(body)+read.source_end;struct.pack_into('<I',bad,offset,1)
        with self.assertRaisesRegex(ValueError,'collision planes'):Scene.read(bad)
    def test_mesh_validation_rejects_unbounded_degenerate_nonfinite_and_invalid_sectors(self):
        for mutate in (lambda v:v.update(vertices=[]),lambda v:v['vertices'][0].__setitem__(0,float('nan')),lambda v:v.update(material_ids=[5]),lambda v:v.update(sector=-1),lambda v:v.update(materials=['x'*32]),lambda v:v.update(vertices=[[0,0,0,0,0]]*3),lambda v:v.update(material_ids=[0]*2049,vertices=v['vertices']*2049)):
            with self.subTest(mutate=mutate):
                value=mesh();mutate(value)
                with self.assertRaises(ValueError):validate(value)
    def test_tenebrae_door_patch_does_not_select_the_other_door_and_has_real_sector(self):
        import numpy as np
        level=Assets(self.backend).load('ClubTenebrae');index=next(i for i,m in enumerate(level.mesh.material_ids) if level.mesh.materials[m]=='London\\CTdoor_L' and level.mesh.triangles[i].mean(0)[0]<700)
        center,value=surface(level.mesh,index,[0,-1,0]);validate(value)
        vertices=np.asarray(value['vertices'])[:,:3]+center;self.assertLess(vertices[:,0].max(),800);self.assertGreater(len(value['material_ids']),1);self.assertGreaterEqual(value['sector'],0);self.assertLess(value['sector'],level.mesh.sectors)
    def test_same_scene_travel_jump_and_recipe_are_rejected_even_with_valid_entry(self):
        for action in [{'travel':dict(scene='street',entry='start')},{'jump':'street'}]:
            root=source();root['scenes'][0]['events'][0]['actions']=[action];result=self.backend.validate(root);self.assertFalse(result.valid);self.assertTrue(any('misma escena' in p.message for p in result.problems));self.assertEqual(result.problems[0].path,('scenes',0,'events',0,'actions',0))
        with self.assertRaisesRegex(ValueError,'misma escena'):recipes.apply(blank(),'travel','street',{'destination':'street'})
    def test_manual_events_run_any_normal_actions_and_cycles_are_blocked(self):
        root=source();scene=root['scenes'][0];scene['events'].append(dict(id='effect',when='manual',actions=[{'set_flag':'clicked'},{'reward_xp':10}]))
        scene['events'][0]['actions']=[{'run_event':'effect'}];self.valid(root)
        self.assertTrue(any(link.label=='run_event' and link.target==('scenes',0,'events',1) for link in graph(root)))
        doc=CampaignDocument(self.backend.ws,root);doc.rename('events',1,'renamed');self.assertEqual(scene['events'][0]['actions'],[{'run_event':'renamed'}])
        scene['events'][1]['actions']=[{'run_event':'use'}];self.assertFalse(self.backend.validate(root).valid)
    def test_dialog_is_transactional_all_action_types_available_and_no_self_destination(self):
        root=blank();root['scenes']=root['scenes'][:1];win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,root);win.refresh();self.addCleanup(lambda:(setattr(win,'doc',None),win.close()));before=win.doc.snapshot()
        target=dict(fixed_surface=True,level='EastLondon',material='London\\CTdoor_L',position=[0,0,0],interaction=mesh())
        dialog=PassageDialog(win,target);self.assertEqual(dialog.when.currentData(),'object_clicked');self.assertFalse(dialog.once.isChecked())
        kind=dialog.actions.scroll.widget().findChild(QComboBox,'action_kind')
        for action in ('travel','jump','start_conversation','run_event','play_sequence','show_note','control_original','set_flag'):self.assertGreaterEqual(kind.findData(action),0)
        kind.setCurrentIndex(kind.findData('travel'));destination=dialog.actions.scroll.widget().findChild(QComboBox,'travel_scene');self.assertEqual([destination.itemData(i) for i in range(destination.count())],[''])
        dialog.accept();self.assertNotEqual(dialog.result(),QDialog.DialogCode.Accepted);self.assertEqual(win.doc.snapshot(),before)
        kind=dialog.actions.scroll.widget().findChild(QComboBox,'action_kind');kind.setCurrentIndex(kind.findData('reward_xp'));dialog.label.setText('Entrance');dialog.accept()
        self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted,dialog.error.text());scene=win.doc.data
        self.assertEqual(scene['events'][-1]['when'],'object_clicked');self.assertEqual(scene['events'][-1]['actions'],[{'reward_xp':100}]);self.assertEqual(scene['triggers'],[]);self.assertEqual(scene['objects'][-1]['name'],'Entrance');self.valid(win.doc.snapshot())
        win.undo_project();self.assertEqual(win.doc.snapshot(),before)
    def test_native_brush_static_layer_builds_against_real_codex_and_preserves_hover_nls(self):
        root=source();root['chronicle']['id']='click_test';report=self.backend.build(root);self.assertEqual(report['status'],'compiled-unverified-in-game');self.assertFalse(report['geometry_in_package'])
        prefix='R_click_test_s0';nsd=Scene.read((ROOT/f'build/click_test_s0/runtime/scenes/{prefix}.nsd').read_bytes());self.assertEqual(len(nsd.brushes),1)
        tags={t.id:t.value for t in nsd.entities[1]};self.assertEqual(cstring(tags[81]),prefix+'_door');self.assertEqual(cstring(tags[82]),prefix+'_door')
        nls=(ROOT/f'build/click_test_s0/runtime/strings/_{prefix}.nls').read_text(encoding='cp1252');self.assertIn(prefix+'_door Club entrance',nls)
        java=(ROOT/f'build/click_test/generated/java/{prefix}_Scene.java').read_text();self.assertNotIn('CreateThing(template(0)',java);self.assertIn('THING_FLAG_NOHIGHLIGHT',java);self.assertIn('dispatch("object_clicked","door",0)',java);self.assertNotIn('dispatch("trigger_enter"',java)
    def test_doubles_require_click_reject_clients_preserve_restore_and_guard_runtime_self_link(self):
        root=source();scene=root['scenes'][0];scene['events'][0]['actions']=[{'run_event':'effect'}];scene['events'].append(dict(id='effect',when='manual',actions=[{'reward_xp':7},{'set_flag':'clicked'}]))
        campaign=self.valid(root);name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''import java.lang.reflect.*;
public class StabilityHarness {
 static void check(boolean value,String why){if(!value)throw new AssertionError(why);}
 public static void main(String[] args)throws Exception {
 CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);
 SCENE missing=new SCENE();missing.beginscene(1,0);check(CE.created==0,"missing NSD brush does not create an unclickable ghost");
 int door=CE.make("PREFIX_door",new float[]{0,0,0});SCENE s=new SCENE();s.beginscene(1,0);check(CE.captures==1,"exactly one native capture");
 check(CE.xp==0 && !CE.flags[0],"standing on surface never clicks");int captures=CE.captures;for(int i=0;i<8;i++)s.timer(9400,0,0,0,0);check(CE.captures==captures,"capture list bounded");
 CE.client=true;s.clicked(door,1,1);check(CE.xp==0,"client ignored");CE.client=false;s.clicked(door,1,1);check(CE.xp==7 && CE.flags[0],"native click dispatches arbitrary nested actions");
 Field running=SCENE.class.getDeclaredField("eventRunning");running.setAccessible(true);((boolean[])running.get(s))[0]=true;s.clicked(door,1,1);check(CE.xp==7,"synchronous callback reentry ignored");((boolean[])running.get(s))[0]=false;
 s.save(0);SCENE restored=new SCENE();CE.read=0;restored.restore(0);restored.restored(0);check(CE.xp==7,"restore does not fire click");restored.clicked(door,1,1);check(CE.xp==14,"restored prop recaptures click");
 Method travel=SCENE.class.getDeclaredMethod("travel",String.class,String.class);travel.setAccessible(true);check(!(Boolean)travel.invoke(restored,"street","start"),"runtime rejects self even bypassing validator");check(CE.jump.equals(""),"no engine jump for self");
 System.out.println("CLICK_PASS");}}
'''.replace('SCENE',name).replace('PREFIX',campaign.scenes[0][1].prefix)
        def doubles(text):
            text=text.replace('class CE {','class CE {static int captures=0;')
            text=text.replace('static class Thing {String template;','static class Thing {int clickFlags=134218240;String template;')
            text=text.replace('int ClearThingFlags(int f){return f;}int SetThingFlags(int f){return f;}','int ClearThingFlags(int f){return CE.world.get(guid).clickFlags&=~f;}int SetThingFlags(int f){return CE.world.get(guid).clickFlags|=f;}')
            text=text.replace('static boolean IsPropGuid(int g){return false;}','static boolean IsPropGuid(int g){return g!=1 && CE.valid(g);}')
            text=text.replace('boolean CaptureThing(int g,int i){return CE.valid(g);}','boolean CaptureThing(int g,int i){if((CE.world.get(g).clickFlags&512)!=0 || (CE.world.get(g).clickFlags&134217728)!=0)throw new AssertionError("brush must keep the native selectable flags");CE.captures++;return CE.valid(g);}')
            return text.replace('class Codex {','class Codex {static final int THING_FLAG_NOHIGHLIGHT=64,THING_FLAG_BLOCKSELECT=524288,THING_FLAG_PROXIMITYTRIGGER=1024,THING_FLAG_VISBLOCK=8192,THING_FLAG_CAMERABLOCK=16384,THING_FLAG_DISABLECOLLIDE=512,THING_FLAG_NOSTDELETE=2097152,THING_FLAG_NOBLOCK=134217728;')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
            out=Path(d);compile_scenario(out,campaign,harness,doubles);run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('CLICK_PASS',run.stdout)
    def test_no_feature_keeps_accepted_runtime_extension_absent(self):
        campaign=self.valid(blank());java=runtime(campaign,*campaign.scenes[0])[1];self.assertNotIn('eventRunning',java);self.assertNotIn('clickCaptured',java)
    def test_nsd_without_cast_registry_binds_by_description_and_rejects_duplicate_identity(self):
        campaign=self.valid(source());name=campaign.scenes[0][1].prefix+'_Scene';prefix=campaign.scenes[0][1].prefix
        harness='''public class StabilityHarness {
 static void check(boolean value,String why){if(!value)throw new AssertionError(why);}
 public static void main(String[] args) {
 CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
 int door=CE.make("PREFIX_door",new float[]{0,0,0});
 int foreign=CE.make("PREFIX_door",new float[]{0,0,0});CE.world.get(foreign).location=3;
 SCENE scene=new SCENE();scene.beginscene(1,0);
 check(CE.captures==1,"NSD prop binds without a Cast ID registry entry; foreign world excluded");
 for(int i=0;i<5;i++)scene.timer(9400,0,0,0,0);
 check(CE.captures==1 && CE.xp==0,"bounded capture; no actions on proximity");
 scene.clicked(door,1,1);check(CE.xp==7,"native callback reaches authored action");
 CE.make("PREFIX_door",new float[]{0,0,0});SCENE ambiguous=new SCENE();ambiguous.beginscene(1,0);
 check(CE.captures==1,"ambiguous identity is never captured");
 System.out.println("NSD_IDENTITY_PASS");}}
'''.replace('SCENE',name).replace('PREFIX',prefix)
        def doubles(text):
            start=text.index('static int GuidFromCastID(String id)');end=text.index('\n',start)
            text=text[:start]+'static int GuidFromCastID(String id){return 0;}'+text[end:]
            text=text.replace('class CE {','class CE {static int captures=0;')
            text=text.replace('boolean CaptureThing(int g,int i){return CE.valid(g);}','boolean CaptureThing(int g,int i){CE.captures++;return CE.valid(g);}')
            text=text.replace('static boolean IsPropGuid(int g){return false;}','static boolean IsPropGuid(int g){return g!=1 && CE.valid(g);}')
            return text.replace('class Codex {','class Codex {static final int THING_FLAG_NOHIGHLIGHT=64,THING_FLAG_BLOCKSELECT=524288,THING_FLAG_PROXIMITYTRIGGER=1024,THING_FLAG_VISBLOCK=8192,THING_FLAG_CAMERABLOCK=16384,THING_FLAG_DISABLECOLLIDE=512,THING_FLAG_NOSTDELETE=2097152,THING_FLAG_NOBLOCK=134217728;')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
            out=Path(d);compile_scenario(out,campaign,harness,doubles);run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('NSD_IDENTITY_PASS',run.stdout)
    def test_format10_arrival_and_restore_clear_old_movement_without_repeating_on_poll(self):
        root=blank();root['project_format']=10;campaign=self.valid(root);name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness {
 public static void main(String[] args) {
 CE.Thing player=new CE.Thing();player.template="player";CE.world.put(1,player);
 SCENE s=new SCENE();s.beginscene(1,0);
 if(CE.teleports!=1 || CE.stops!=0 || CE.cancels!=0 || CE.stopBeforePosition)throw new AssertionError("reset once, after relocating player");
 for(int i=0;i<5;i++)s.timer(9400,0,0,0,0);
 if(CE.teleports!=1 || CE.stops!=0)throw new AssertionError("poll must not cancel user movement");
 s.save(0);SCENE restored=new SCENE();CE.read=0;restored.restore(0);restored.restored(0);restored.timer(9400,0,0,0,0);
 if(CE.teleports!=1 || CE.stops!=1 || CE.cancels!=1)throw new AssertionError("save restoration resets movement once");
 System.out.println("ARRIVAL_RESET_PASS");}}
'''.replace('SCENE',name)
        def doubles(text):
            text=text.replace('class CE {','class CE {static int stops=0,cancels=0;static boolean stopBeforePosition=false;')
            text=text.replace('boolean Stop(){return true;}','boolean Stop(){CE.stops++;if(CE.poseWrites==0)CE.stopBeforePosition=true;return true;}')
            return text.replace('boolean CancelActorAction(){return true;}','boolean CancelActorAction(){CE.cancels++;return true;}')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
            out=Path(d);compile_scenario(out,campaign,harness,doubles);run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('ARRIVAL_RESET_PASS',run.stdout)
    def test_old_self_proximity_link_cannot_jump_even_if_validation_is_bypassed(self):
        root=blank();scene=root['scenes'][0];point=scene['entries'][0]['transform']['position']
        scene['triggers']=[dict(id='old_zone',name='Old zone',shape='sphere',radius=120,once=True,transform=dict(position=point,orientation=[0,0,0]))]
        scene['events']=[dict(id='old_link',when='trigger_enter',trigger='old_zone',once=True,actions=[{'travel':dict(scene='home',entry='start')}])]
        campaign=self.valid(root)
        # Simulate an unsafe old build/model supplied without the parser.
        campaign.scenes[0][0]['events'][0]['actions'][0]['travel']['scene']='street'
        name=campaign.scenes[0][1].prefix+'_Scene'
        harness='''public class StabilityHarness {
 public static void main(String[] args) {
 CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);
 for(int i=0;i<100;i++)s.timer(9400,0,0,0,0);
 if(!CE.jump.equals(""))throw new AssertionError("Old self-trigger reached native Jump");
 System.out.println("SELF_TRIGGER_BLOCKED");}}
'''.replace('SCENE',name)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as d:
            out=Path(d);compile_scenario(out,campaign,harness);run=subprocess.run(['java','-cp',str(out),'StabilityHarness'],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertIn('SELF_TRIGGER_BLOCKED',run.stdout)
    def test_native_sector_index_is_checked_against_actual_nil_before_writing(self):
        from rcm.click_interactions import validate_placement
        objects=source()['scenes'][0]['objects'];validate_placement(self.backend.ws,self.backend.levels['EastLondon'],objects)
        objects[0]['interaction']['sector']=99999
        with self.assertRaisesRegex(ValueError,'fuera del level'):validate_placement(self.backend.ws,self.backend.levels['EastLondon'],objects)
    def test_opt_in_click_brush_also_compiles_with_phase10_runtime(self):
        root=source();root['project_format']=10;root['chronicle']['id']='click_test'
        from rcm.original_objects import catalogue,selector
        row=next(r for r in catalogue(self.backend,'EastLondon') if r['template']=='ironBench');root['scenes'][0]['objects'][0]['interaction']['source']=selector(row)
        report=self.backend.build(root);self.assertEqual(report['status'],'compiled-unverified-in-game');self.assertTrue(all(v=='45.3' for v in report['class_versions'].values()))
        java=(ROOT/'build/click_test/generated/java/R_click_test_s0_Scene.java').read_text();self.assertIn('clickSources',java);self.assertIn('overlay.SetPosition(source.GetPosition())',java)
    def test_click_object_and_called_event_delete_without_dangling_references(self):
        from rcm.safe_edit import deletion_plan
        root=source();root['scenes'][0]['events'].append(dict(id='independent',when='manual',actions=[{'reward_xp':3}]))
        doc=CampaignDocument(self.backend.ws,copy.deepcopy(root));plan=deletion_plan(doc,('scenes',0,'objects',0),self.backend);self.valid(plan.candidate)
        self.assertEqual(plan.candidate['scenes'][0]['objects'],[]);self.assertEqual([e['id'] for e in plan.candidate['scenes'][0]['events']],['independent']);self.assertEqual(doc.snapshot(),root)
        root['scenes'][0]['events'][0]['actions']=[{'run_event':'independent'}];doc=CampaignDocument(self.backend.ws,root);plan=deletion_plan(doc,('scenes',0,'events',1),self.backend);self.valid(plan.candidate);self.assertEqual(plan.candidate['scenes'][0]['events'],[])
