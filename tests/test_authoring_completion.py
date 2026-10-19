"""Native formats/API compilation and transactional authoring; never game acceptance."""
import copy
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PIL import Image
from PySide6.QtWidgets import QApplication,QDialog,QComboBox
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_generator import runtime
from rcm.campaign_document import CampaignDocument
from rcm.camera_paths import authored,CameraPath
from rcm.formats import Scene
from rcm.dynamic_targets import candidates,indices
from rcm.campaign_relations import graph
from rcm.safe_edit import deletion_plan
from test_combat_difficulty import source
from test_stability_revision import compile_scenario

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')


def fixture(dynamic=False):
    root=source(dynamic=dynamic);root['chronicle']['id']='complete_test';return root


class Completion(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend=Backend(Workspace(ROOT,GAME));cls.app=QApplication.instance() or QApplication([])
        cls.image=ROOT/'build/tests/completion_map.png';cls.image.parent.mkdir(parents=True,exist_ok=True)
        image=Image.new('RGB',(640,480),'#254560');image.paste('#b49950',(0,0,256,256));image.save(cls.image)
    def valid(self,root):
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems]);return result.project
    def map_source(self):
        root=fixture();root['resources']['maps']=[dict(id='town',name='Own map',source='build/tests/completion_map.png',points=[dict(id='dock',name='The old quay',position=[123,321],visible=True,haven=False)])]
        root['scenes'][0]['map_location']=dict(map='town',point='dock');return root
    def test_timed_native_polynomials_rotate_hold_and_keep_legacy_rejection(self):
        points=[dict(position=[10,20,30],orientation=[0,0,350],duration=2),dict(position=[10,20,30],orientation=[0,0,10],duration=3),dict(position=[10,20,30],orientation=[0,0,10])]
        path=authored(points,True);self.assertAlmostEqual(path.total,5)
        self.assertEqual(path.sample(1)[0],[10,20,30]);self.assertAlmostEqual(path.sample(1)[1][2],360);self.assertAlmostEqual(path.sample(4)[1][2],10)
        self.assertEqual(CameraPath.read(path.encode()).encode(),path.encode())
        with self.assertRaises(ValueError):authored([{k:v for k,v in p.items() if k!='duration'} for p in points])
        for duration in (0,float('nan'),121,True):
            values=copy.deepcopy(points);values[0]['duration']=duration
            with self.assertRaises(ValueError):authored(values,True)
    def test_map_tiles_names_binding_and_real_package(self):
        root=self.map_source();root['scenes'][0]['events'][0]['actions'].append(dict(set_location_flags=dict(scene=root['entry'],visible=True,haven=True)))
        self.valid(root);report=self.backend.build(root)
        from rcm.chronicle_maps import labels
        stem=labels(root['chronicle']['id'],'town');key=labels(root['chronicle']['id'],'town','dock')
        with zipfile.ZipFile(ROOT/'build/complete_test/complete_test.nob') as archive:
            nui=archive.read('ui/'+stem+'.nui').decode('cp1252');self.assertIn('pos=123,321',nui);self.assertIn('name='+key,nui)
            self.assertEqual(len([n for n in archive.namelist() if n.startswith('ui/Materials/'+stem)]),12)
            import io
            with Image.open(io.BytesIO(archive.read('ui/Materials/'+stem+'_01.tga'))) as tile:self.assertEqual(tile.size,(256,256));self.assertEqual(tile.getpixel((0,0)),(180,153,80))
            nsc=archive.read('chronicles/complete_test.nsc').decode('cp1252');self.assertIn(stem+'.nui '+key,nsc);self.assertEqual(int(nsc.splitlines()[1].split()[-1],0)&0x28,0x28)
            self.assertIn(key+' The old quay',archive.read('strings/R_complete_test_custom.nls').decode('cp1252'))
        self.assertEqual(set(report['class_versions'].values()),{'45.3'})
    def test_map_references_export_import_and_image_invalidation(self):
        root=self.map_source();self.valid(root);before=copy.deepcopy(root);doc=CampaignDocument(self.backend.ws,root)
        from rcm.service import build_inputs_fingerprint
        old=self.image.read_bytes();fingerprint=build_inputs_fingerprint(self.backend.ws,root)
        try:
            self.image.write_bytes(old+b'\0');self.assertNotEqual(build_inputs_fingerprint(self.backend.ws,root),fingerprint)
        finally:self.image.write_bytes(old)
        links=graph(root);self.assertTrue(any(l.label=='map_location' for l in links))
        plan=deletion_plan(doc,('resources','maps',0),self.backend);self.assertNotIn('map_location',plan.candidate['scenes'][0]);self.assertEqual(root,before)
        from rcm.packages import export_project,import_project
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            archive=export_project(self.backend.ws,root,Path(tmp)/'project.zip');restored=import_project(self.backend.ws,archive,Path(tmp)/'copy');self.assertTrue(self.backend.validate(restored.snapshot()).valid)
            imported=restored.snapshot()['resources']['maps'][0]['source'];self.assertEqual(hashlib.sha256(self.backend.ws.output(imported).read_bytes()).digest(),hashlib.sha256(self.image.read_bytes()).digest())
        for value in ([-1,20],[625,1],[0,float('nan')]):
            bad=copy.deepcopy(root);bad['resources']['maps'][0]['points'][0]['position']=value;self.assertFalse(self.backend.validate(bad).valid)
    def test_native_region_sector_codec_binding_and_compilation(self):
        root=fixture();s=root['scenes'][0];transform=copy.deepcopy(s['entries'][0]['transform'])
        s['objects']=[dict(id='target',name='Target',template='tracker_thing',transform=copy.deepcopy(transform))]
        s['triggers']=[dict(id='native',name='Native region',shape='box',size=[64,64,64],once=False,transform=transform,native_script={'class':'RegionTrigger','parameters':[dict(type='thing',value='target')]})]
        self.valid(root);report=self.backend.build(root)
        scene=Scene.read((ROOT/'build/complete_test_s0/runtime/scenes/R_complete_test_s0.nsd').read_bytes());self.assertTrue(scene.regions);self.assertEqual(scene.encode(),Scene.read(scene.encode()).encode())
        self.assertTrue(all(index in scene.brushes for index in scene.regions));self.assertEqual(set(report['class_versions'].values()),{'45.3'})
        s['triggers'][0]['shape']='sphere';s['triggers'][0]['radius']=30;s['triggers'][0].pop('size');self.assertFalse(self.backend.validate(root).valid)
    def test_region_constructor_types_use_original_records(self):
        from rcm.native_scripts import catalogue
        records=catalogue(self.backend.ws,self.backend.resources)
        self.assertEqual(records['GOLDD_4_1']['parameters'][0]['native_type'],5)
        self.assertEqual(records['TOL4_30_1_Main']['parameters'][0]['native_type'],10)
        original=json.loads((ROOT/'research/embrace_strict_parity/script_parameter_records.json').read_text())
        gold=next(r for r in original if r['tags'].get('11')=='GOLDD_4_1');self.assertEqual(gold['params'][0]['type'],5)
    def test_dynamic_role_controls_compile_and_reference_lifecycle(self):
        root=fixture(True);s=root['scenes'][0];key='dynamic/boss/boss/0'
        s['sequences']=[dict(id='film',name='Follow boss',actor=key,duration=3,shot='medium',angle='high',steps=[dict(at=0,actor=key,preset='full')])]
        s['events'].append(dict(id='control',when='manual',actions=[dict(move_actor=dict(actor=key,waypoint='p',speed=90)),dict(actor_behavior=dict(actor=key,team=12,paused=True)),dict(play_motion=dict(actor=key,motion='stand')),dict(play_sequence='film')]))
        campaign=self.valid(root);self.backend.build(root);code=runtime(campaign,*campaign.scenes[0])[1]
        self.assertIn('refreshDynamicTargets()',code);self.assertIn('CINEMA_DYNAMIC_TARGET_MISSING',code);self.assertIn('pinDynamicCamera(2,-1)',code);self.assertIn('CINEMA_DYNAMIC_TARGET_CHANGED',code)
        self.assertEqual(len(indices(s,campaign.scenes[0][1])),len(campaign.scenes[0][1].entities)+1)
        self.assertIn('for(int i=0;i<2;i++) { CodexSequence.SaveInt(things[i])',code)
        self.assertNotIn(key,[e.id for e in campaign.entities]);self.assertIn(key,candidates(s))
        doc=CampaignDocument(self.backend.ws,copy.deepcopy(root));doc.rename('generators',1,'boss_new');self.assertEqual(doc.campaign['scenes'][0]['sequences'][0]['actor'],'dynamic/boss_new/boss/0');self.valid(doc.snapshot())
        plan=deletion_plan(doc,('scenes',0,'generators',1),self.backend);self.assertFalse(plan.candidate['scenes'][0]['sequences']);self.valid(plan.candidate)
    def test_dynamic_role_resolver_doubles_does_not_spawn_or_alias_foreign_actor(self):
        root=fixture(True);s=root['scenes'][0];s['events'].append(dict(id='check',when='manual',conditions=[dict(actor_alive='dynamic/boss/boss/0')],actions=[dict(set_flag='half')]))
        campaign=self.valid(root);name=runtime(campaign,*campaign.scenes[0])[0]
        harness='''public class StabilityHarness { public static void main(String[] args)throws Exception { CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE scene=new SCENE();scene.beginscene(1,0);for(int i=0;i<20;i++)scene.timer(9400,0,0,0,0);java.lang.reflect.Method resolve=SCENE.class.getDeclaredMethod("dynamicTarget",new Class[]{Integer.TYPE,Integer.TYPE,Integer.TYPE});resolve.setAccessible(true);int guid=((Integer)resolve.invoke(scene,new Object[]{Integer.valueOf(1),Integer.valueOf(0),Integer.valueOf(0)})).intValue();if(guid==0)throw new AssertionError("missing boss");int size=CE.world.size();String original=CE.world.get(guid).template;CE.world.get(guid).template="foreign";if(((Integer)resolve.invoke(scene,new Object[]{Integer.valueOf(1),Integer.valueOf(0),Integer.valueOf(0)})).intValue()!=0)throw new AssertionError("foreign template");CE.world.get(guid).template=original;java.lang.reflect.Field restoring=SCENE.class.getDeclaredField("dRestoring");restoring.setAccessible(true);restoring.setBoolean(scene,true);if(((Integer)resolve.invoke(scene,new Object[]{Integer.valueOf(1),Integer.valueOf(0),Integer.valueOf(0)})).intValue()!=0)throw new AssertionError("unreconciled restore");restoring.setBoolean(scene,false);CE.world.get(guid).health=0;if(((Integer)resolve.invoke(scene,new Object[]{Integer.valueOf(1),Integer.valueOf(0),Integer.valueOf(0)})).intValue()!=0)throw new AssertionError("dead boss");if(CE.world.size()!=size)throw new AssertionError("resolver spawned actor");System.out.println("PASS");} }'''.replace('SCENE',name)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            compile_scenario(Path(tmp),campaign,harness);run=subprocess.run(['java','-cp',tmp,'StabilityHarness'],capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr)
    def test_eax_native_command_and_zone_lifecycle_compile(self):
        root=fixture();s=root['scenes'][0];s['level']['environment']=dict(room_type=5)
        wav=next(e['id'] for e in self.backend.resources['entries'] if e['extension'].lower()=='.wav')
        s['triggers']=[dict(id='zone',name='Sound and light',shape='box',size=[100,100,100],transform=copy.deepcopy(s['entries'][0]['transform']),sound_zone=dict(resource=wav,volume=50,min_distance=64,max_distance=300),light_zone=dict(entity='mentor',color=[1,.5,.2],intensity=1,radius=150,style='torch1'))]
        s['events'][0]['actions'].append(dict(set_room_type=12));campaign=self.valid(root);report=self.backend.build(root);code=runtime(campaign,*campaign.scenes[0])[1]
        for token in ('roomtype 5','roomtype 12','pollSceneSounds','pollLightZones','sceneSounds[i].Stop()','CodexSequence.SaveInt(roomTypeState)'):self.assertIn(token,code)
        self.assertIn('save_schema_sha256',report)
        for bad in (26,-1,True,'5'):
            s['level']['environment']['room_type']=bad;self.assertFalse(self.backend.validate(root).valid)
    def test_map_editor_cancel_apply_drag_delete_and_undo(self):
        from rcm.editor.window import MainWindow
        from rcm.editor.maps import MapDialog,Marker
        from PySide6.QtCore import QPointF
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,self.map_source());win.refresh();before=win.doc.snapshot()
        try:
            dialog=MapDialog(win);dialog.add_point();dialog.reject();self.assertEqual(win.doc.snapshot(),before)
            dialog=MapDialog(win);dialog.add_point();marker=next(i for i in dialog.canvas.items() if isinstance(i,Marker));marker.setPos(QPointF(900,-10));self.assertEqual(marker.pos(),QPointF(624,0));marker.point['position']=[624,464]
            dialog.accept();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted);after=win.doc.snapshot();self.assertEqual(len(after['resources']['maps'][0]['points']),2)
            win.undo_project();self.assertEqual(win.doc.snapshot(),before);win.redo_project();self.assertEqual(win.doc.snapshot(),after)
            dialog=MapDialog(win);dialog.delete_map();dialog.accept();self.assertNotIn('map_location',win.doc.campaign['scenes'][0])
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_ui_exposes_dynamic_camera_and_room_type(self):
        from rcm.editor.window import MainWindow
        from rcm.editor.environment import EnvironmentDialog
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,fixture(True));win.refresh()
        try:
            dialog=EnvironmentDialog(win);field=dialog.fields['room_type'];self.assertEqual(field.count(),27);field.setCurrentIndex(field.findData(4));dialog.apply();self.assertEqual(win.doc.campaign['scenes'][0]['level']['environment']['room_type'],4)
            win.campaign_panel.add_sequence();field=win.campaign_panel.findChild(QComboBox,'sequence_actor');self.assertIsNotNone(field);self.assertGreaterEqual(field.findData('dynamic/boss/boss/0'),0)
        finally:win.doc=None;win.close();self.app.processEvents()

    def test_native_region_link_requires_selection_and_commits_with_undo(self):
        from unittest.mock import patch
        from rcm.editor.window import MainWindow
        from rcm.editor.native_scripts import NativeScriptDialog
        from PySide6.QtWidgets import QMessageBox
        root=fixture();s=root['scenes'][0];t=copy.deepcopy(s['entries'][0]['transform'])
        s['objects']=[dict(id='binder',name='Controller',template='tracker_thing',transform=t)]
        s['triggers']=[dict(id='region',name='Box',shape='box',size=[64,64,64],transform=copy.deepcopy(t))]
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,root);win.refresh();before=win.doc.snapshot()
        try:
            dialog=NativeScriptDialog(win,win.doc.data['objects'][0]);dialog.choose.setCurrentIndex(dialog.choose.findData('GOLDD_4_1'))
            with patch.object(QMessageBox,'warning') as warning:dialog.apply();self.assertEqual(warning.call_count,1)
            self.assertEqual(win.doc.snapshot(),before);self.assertEqual(dialog.result(),QDialog.DialogCode.Rejected)
            field=dialog.controls[0][1];field.setCurrentIndex(field.findData('region'));dialog.apply()
            self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted);self.assertTrue(win.doc.data['triggers'][0]['native_region']);self.valid(win.doc.snapshot())
            win.undo_project();self.assertEqual(win.doc.snapshot(),before)
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_original_traits_available_without_mod_and_unknown_content_rejected(self):
        from rcm.actor_traits import catalogue
        data=catalogue(self.backend.resources);self.assertTrue(data['clans']);self.assertTrue(data['disciplines'])
        root=fixture();root['scenes'][0]['actors'][0]['traits']=dict(clan=data['clans'][0]['id'],disciplines={data['disciplines'][0]['id']:1});self.valid(root);self.backend.build(root)
        root['scenes'][0]['actors'][0]['traits']['clan']='Unavailable_Mod_Clan';self.assertFalse(self.backend.validate(root).valid)
    def test_typed_region_links_compile_encode_and_rename_without_custom_yaml(self):
        root=fixture();s=root['scenes'][0];t=copy.deepcopy(s['entries'][0]['transform'])
        path=ROOT/'build/tests/BindRegion.java';path.write_text('public class BindRegion extends Codex {public BindRegion(CodexRegion region,CodexItem item) {}}',encoding='utf8')
        root['resources']['scripts']=[dict(id='BindRegion',source='build/tests/BindRegion.java',parameters=[dict(type='region',label='Region'),dict(type='item',label='Item')])]
        s['objects']=[dict(id='binder',name='Binding controller',template='tracker_thing',transform=t,native_script={'class':'BindRegion','parameters':[dict(type='region',value='region'),dict(type='item',value='native_item')]}),dict(id='native_item',name='Native item link',template='Dagger',transform=copy.deepcopy(t))]
        s['triggers']=[dict(id='region',name='Linked region',shape='box',size=[64,64,64],transform=copy.deepcopy(t),native_region=True)]
        self.valid(root);self.backend.build(root)
        encoded=(ROOT/'build/complete_test_s0/runtime/scenes/R_complete_test_s0.nsd').read_bytes();scene=Scene.read(encoded)
        self.assertEqual(scene.parameters[1][0].kind,5);self.assertEqual(int.from_bytes(scene.parameters[1][0].raw,'little'),3);self.assertEqual(scene.parameters[1][1].kind,10);self.assertEqual(int.from_bytes(scene.parameters[1][1].raw,'little'),2)
        doc=CampaignDocument(self.backend.ws,root);doc.rename('triggers',0,'renamed');self.assertEqual(doc.campaign['scenes'][0]['objects'][0]['native_script']['parameters'][0]['value'],'renamed');self.valid(doc.snapshot())
    def test_actor_sound_following_role_uses_native_guid_constructor(self):
        root=fixture(True);s=root['scenes'][0];sound=next(e['id'] for e in self.backend.resources['entries'] if e['extension'].lower()=='.wav')
        s['events'].append(dict(id='attached_sound',when='manual',actions=[dict(play_sound=dict(actor='dynamic/boss/boss/0',resource=sound,min_distance=64,max_distance=300,volume=30,loop=True,id='voice'))]))
        campaign=self.valid(root);self.backend.build(root);code=runtime(campaign,*campaign.scenes[0])[1]
        self.assertIn('soundActorGuid',code);self.assertIn('soundActorGuid[i]=things[2]',code);self.assertIn('sceneSounds[0].Stop()',code)
        s['events'][-1]['actions'][0]['play_sound']['waypoint']='p';self.assertFalse(self.backend.validate(root).valid)
    def test_eax_zones_save_restore_doubles_keep_one_handle(self):
        root=fixture();s=root['scenes'][0];s['level']['environment']=dict(room_type=5)
        sound=next(e['id'] for e in self.backend.resources['entries'] if e['extension'].lower()=='.wav')
        s['triggers']=[dict(id='zone',name='Zone',shape='box',size=[100,100,100],transform=copy.deepcopy(s['entries'][0]['transform']),sound_zone=dict(resource=sound,volume=20,min_distance=64,max_distance=300),light_zone=dict(entity='mentor',color=[1,1,1],intensity=1,radius=200,style='constant'))]
        campaign=self.valid(root);name=runtime(campaign,*campaign.scenes[0])[0]
        harness='''public class StabilityHarness {static void check(boolean ok,String m){if(!ok)throw new AssertionError(m);}public static void main(String[] args){CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE s=new SCENE();s.beginscene(1,0);for(int i=0;i<8;i++)s.timer(9400,0,0,0,0);check(CE.soundStarts==1,"one loop");check(CE.room.equals("roomtype 5"),"native room command");s.save(0);s.endscene(1,0,0);check(CE.soundStops==1,"cleanup before load");SCENE restored=new SCENE();restored.restore(0);restored.restored(0);restored.beginscene(1,0);for(int i=0;i<20;i++)restored.timer(9400,0,0,0,0);check(CE.soundStarts==2,"one restored loop");check(CE.roomCalls<=3,"room command not repeated each tick");CE.world.get(1).pos[0]+=1000;restored.timer(9400,0,0,0,0);check(CE.soundStops==2,"leaving stops loop");System.out.println("PASS");}}'''.replace('SCENE',name)
        def doubles(text):
            text=text.replace('class CE {','class CE {static int soundStarts=0,soundStops=0,roomCalls=0;static String room="";')
            text=text.replace('class CodexConsole extends Codex {','class CodexConsole extends Codex {static boolean Execute(String text){CE.room=text;CE.roomCalls++;return true;}')
            text=text.replace('class Codex {','class Codex {static final int SOUND_FLAG_LOOP=1,LIGHTSTYLE_CONSTANT=0;')
            text=text.replace('class CodexThing extends Codex {','class CodexThing extends Codex {boolean AllocateDynamicLight(){return true;}boolean ClearDynamicLight(){return true;}boolean SetDynamicLightColor(float[] v){return true;}boolean SetDynamicLightIntensity(float v){return true;}boolean SetDynamicLightRadius(float v){return true;}boolean SetDynamicLightStyle(int v){return true;}')
            return text.replace('class CodexSound extends Codex {','class CodexSound extends Codex {CodexSound(String n,float a,float b,int v,int p,int f,float[] pos){CE.soundStarts++;}void Stop(){CE.soundStops++;}')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            compile_scenario(Path(tmp),campaign,harness,doubles);run=subprocess.run(['java','-cp',tmp,'StabilityHarness'],capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr)
    def test_lab_has_no_errors_or_misleading_unused_warnings_and_sources_unchanged(self):
        import yaml
        source_=yaml.safe_load((ROOT/'chronicles/completion_lab/project.yaml').read_text(encoding='utf8'));result=self.backend.validate(source_)
        self.assertTrue(result.valid,[p.message for p in result.problems]);self.assertFalse([p.message for p in result.problems if p.severity=='WARNING'])
        for name in ('tutorial','mini_chronicle'):
            original=subprocess.check_output(['git','show','76cf263:chronicles/'+name+'/project.yaml']);self.assertEqual(original,(ROOT/'chronicles'/name/'project.yaml').read_bytes())

    def test_new_fields_reject_corrupt_editable_shapes_and_region_conflicts(self):
        for change in ('nan','parameter','zone'):
            root=fixture();s=root['scenes'][0]
            if change=='nan':root['resources']['maps']=[dict(id='town',name='Map',source='x',points=[dict(id='p',name='P',position=[float('nan'),0])])]
            elif change=='parameter':s['actors'][0]['native_script']=dict(class_='Foo',parameters=[dict(type='integer',value=2.5)]);s['actors'][0]['native_script']['class']='Foo'
            else:s['triggers']=[dict(id='zone',name='Zone',shape='box',size=[10,10,10],transform=copy.deepcopy(s['entries'][0]['transform']),light_zone=dict(color=['bad',1,1]))]
            with self.assertRaises(ValueError):CampaignDocument.load_data(self.backend.ws,root,None)
        root=fixture();s=root['scenes'][0];s['triggers']=[dict(id='region',name='Region',shape='box',size=[10,10,10],transform=copy.deepcopy(s['entries'][0]['transform']),native_script={'class':'RegionTriggerSound','parameters':[]})]
        s['events'].append(dict(id='enter',when='trigger_enter',trigger='region',actions=[dict(set_flag='half')]))
        self.assertFalse(self.backend.validate(root).valid)

    def test_oversized_map_header_fails_in_backend_and_import_without_copying(self):
        import struct,zlib
        from unittest.mock import patch
        from rcm.editor.window import MainWindow
        from rcm.editor.maps import MapDialog
        path=ROOT/'build/tests/oversized_map.png';body=struct.pack('>IIBBBBB',100000,100000,8,2,0,0,0)
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+struct.pack('>I',len(body))+b'IHDR'+body+struct.pack('>I',zlib.crc32(b'IHDR'+body))+self.image.read_bytes()[33:])
        root=self.map_source();root['resources']['maps'][0]['source']='build/tests/oversized_map.png'
        result=self.backend.validate(root);self.assertFalse(result.valid);self.assertIn('4096',result.problems[0].message)
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,fixture());win.refresh();before=win.doc.snapshot()
        try:
            dialog=MapDialog(win)
            with patch('rcm.editor.maps.QFileDialog.getOpenFileName',return_value=(str(path),'')):self.assertFalse(dialog.import_image(new=True))
            self.assertIn('4096',dialog.error.text());self.assertFalse(dialog.pending);dialog.reject();self.assertEqual(win.doc.snapshot(),before)
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_native_ownership_rejects_nested_conversation_creation(self):
        from rcm.native_scripts import placement
        root=fixture();s=root['scenes'][0];s['actors'][0]['native_frames']=['p'];s['waypoints']=[dict(id='p',name='Point',transform=copy.deepcopy(s['entries'][0]['transform']))]
        s['events']=[];s['conversations']=[dict(id='dialog',nodes=[dict(id='n',lines=[dict(text='Hello',actions=[dict(spawn=s['actors'][0]['id'])])])])]
        with self.assertRaisesRegex(ValueError,'crea al cargar'):placement(s,{})

    def test_lights_wait_for_missing_actor_and_clear_departed_dynamic_target(self):
        def doubles(text):
            text=text.replace('class CE {','class CE {static int missingLight=0;static java.util.Set<Integer> lights=new java.util.HashSet<Integer>();')
            text=text.replace('static void Print(int a,int b,String s){}','static void Print(int a,int b,String s){if(s.indexOf("LIGHT_TARGET_MISSING")>=0)CE.missingLight++;}')
            text=text.replace('class Codex {','class Codex {static final int LIGHTSTYLE_CONSTANT=0;')
            return text.replace('class CodexThing extends Codex {','class CodexThing extends Codex {boolean AllocateDynamicLight(){CE.lights.add(Integer.valueOf(guid));return true;}boolean ClearDynamicLight(){CE.lights.remove(Integer.valueOf(guid));return true;}boolean SetDynamicLightColor(float[] v){return true;}boolean SetDynamicLightIntensity(float v){return true;}boolean SetDynamicLightRadius(float v){return true;}boolean SetDynamicLightStyle(int v){return true;}')
        for dynamic,foreign in ((False,False),(True,False),(True,True)):
            root=fixture(dynamic);s=root['scenes'][0];light=dict(entity='dynamic/boss/boss/0' if dynamic else 'mentor',color=[1,1,1],intensity=1,radius=200,style='constant')
            if dynamic:s['events'].append(dict(id='light',when='manual',actions=[dict(set_dynamic_light=light)]))
            else:
                s['events'][0]['actions']=[dict(spawn='foe')]
                s['triggers']=[dict(id='zone',name='Zone',shape='box',size=[100,100,100],transform=copy.deepcopy(s['entries'][0]['transform']),light_zone=light)]
            campaign=self.valid(root);self.backend.build(root);name=runtime(campaign,*campaign.scenes[0])[0]
            check='java.lang.reflect.Method method=SCENE.class.getDeclaredMethod("sceneLight",Integer.TYPE);method.setAccessible(true);if(!((Boolean)method.invoke(scene,Integer.valueOf(0))).booleanValue())throw new AssertionError("light not applied");int guid=CE.lights.iterator().next().intValue();CE.world.get(guid).health=0;scene.timer(9400,0,0,0,0);if(CE.lights.contains(Integer.valueOf(guid)))throw new AssertionError("dead target still lit");' if dynamic else 'if(CE.missingLight!=0)throw new AssertionError("missing actor trace loop");'
            if foreign:check=check.replace('CE.world.get(guid).health=0;','CE.world.get(guid).template="foreign";').replace('if(CE.lights.contains(Integer.valueOf(guid)))','if(!CE.lights.contains(Integer.valueOf(guid)))').replace('dead target still lit','foreign light was cleared')
            harness=('public class StabilityHarness {public static void main(String[] args)throws Exception {CE.Thing p=new CE.Thing();p.template="player";CE.world.put(1,p);SCENE scene=new SCENE();scene.beginscene(1,0);for(int i=0;i<20;i++)scene.timer(9400,0,0,0,0);'+check+'System.out.println("PASS");}}').replace('SCENE',name)
            with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                compile_scenario(Path(tmp),campaign,harness,doubles);run=subprocess.run(['java','-cp',tmp,'StabilityHarness'],capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr)
