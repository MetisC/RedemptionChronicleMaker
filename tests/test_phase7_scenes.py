"""Scene/geometry separation, compatibility, environment validation and Qt authoring."""
import copy,hashlib,struct,tempfile,unittest
from pathlib import Path
from rcm.paths import Workspace
from rcm.formats import Scene
from rcm.service import Backend,project_source
from rcm.document import Document
from rcm.catalogue import associate_static_scenes
from rcm.scene_profiles import environment,read_profile,reference,catalogue
ROOT=Path(__file__).resolve().parents[1]

class SceneProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws=Workspace(ROOT);cls.backend=Backend(cls.ws)
        cls.data=Document.load(cls.ws,'chronicles/east_demo.yaml').snapshot()
    def test_static_association_does_not_treat_nss_description_as_scene(self):
        levels={'A':{'nil':'rooms.nil','scenes':['ST_SCENE_3_1.nsd'], 'references':[{'scene':'NULL'},{'scene':'night.nsd'}]}}
        associate_static_scenes(levels,{'rooms.nsd':{'source':{'path':'scenes/ROOMS.nsd'}}})
        self.assertEqual(levels['A']['scenes'],['night.nsd','ROOMS.nsd'])
        self.assertEqual(levels['A']['static_scene'],'ROOMS.nsd')
    def test_original_default_stays_first(self):
        level=self.backend.levels['EastLondon']
        self.assertEqual(reference(level,self.backend.hints)[0],'EAST_28_1.nsd')
        self.assertEqual(level['static_scene'].casefold(),'l1_east.nsd')
    def test_model_roundtrip_explicit_profile_and_casefold(self):
        d=copy.deepcopy(self.data);d['level']['environment_scene']='east_28_1.NSD'
        result=self.backend.validate(d);self.assertTrue(result.valid)
        self.assertEqual(project_source(result.project)['level'],d['level'])
    def test_invalid_cross_level_paths_null_and_types_rejected(self):
        for value in ['WEST_28_1.nsd','../EAST_28_1.nsd','null','',None,[],3]:
            with self.subTest(value=value):
                d=copy.deepcopy(self.data);d['level']['environment_scene']=value
                self.assertFalse(self.backend.validate(d).valid)
    def test_catalogue_errors_and_unknown_binary_version_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as root:
            ws=Workspace(Path(root));data=b'NSD\x10'+struct.pack('<I',99)+bytes(280)
            ws.write('research/original/fake.nob/scenes/fake.nsd',data)
            hint={'source':{'archive':'fake.nob','path':'scenes/fake.nsd','sha256':hashlib.sha256(data).hexdigest()},'entities':[{}]}
            profiles=catalogue(ws,{'A':{'scenes':['fake.nsd']}},{'fake.nsd':hint})
            self.assertIn('error',profiles['A'][0])
            with self.assertRaisesRegex(ValueError,'versión 8'):read_profile(ws,'fake.nsd',hint)
    def test_copied_source_corruption_rejected_before_build(self):
        level=self.backend.levels['EastLondon'];name,hint=reference(level,self.backend.hints)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as root:
            ws=Workspace(Path(root));src=Path('research/original')/hint['source']['archive']/hint['source']['path']
            data=self.ws.output(src).read_bytes();ws.write(src,data[:-1]+bytes([data[-1]^1]))
            with self.assertRaisesRegex(ValueError,'difiere'):read_profile(ws,name,hint)
    def test_every_available_profile_preserves_full_tail(self):
        profiles=catalogue(self.ws,self.backend.levels,self.backend.hints)
        total=0
        for lid,rows in profiles.items():
            for row in rows:
                if 'error' in row:continue
                block,record=environment(self.ws,self.backend.levels[lid],self.backend.hints,row['id'])
                source=row['source'];data=self.ws.output(Path('research/original')/source['archive']/source['path']).read_bytes()
                self.assertEqual(block,bytes(16)+data[-176:]);self.assertEqual(record,row);total+=1
        self.assertGreater(total,100)
    def test_build_explicit_environment_without_importing_original_entities(self):
        d=copy.deepcopy(self.data);d['chronicle']['id']='p7_scene';d['level']['environment_scene']='l1_east.nsd'
        report=self.backend.build(d,compile_java=False)
        path='build/p7_scene/runtime/scenes/R_p7_scene.nsd'
        generated=Scene.read(self.ws.output(path).read_bytes())
        block,_=environment(self.ws,self.backend.levels['EastLondon'],self.backend.hints,'l1_east.nsd')
        self.assertEqual(generated.environment,block);self.assertEqual(len(generated.entities),1)
        self.assertFalse(report['geometry_in_package']);self.assertFalse(report['original_scene_entities_imported'])
    def test_campaign_empty_scene_reports_missing_profile_source(self):
        d={'schema':2,'chronicle':{'id':'p7_empty','name':'Empty'},'entry':'a','scenes':[{'id':'a','level':{'source':'EastLondon','environment_scene':'EAST_28_1.nsd'},'actors':[],'conversations':[],'events':[]}]}
        backend=Backend(self.ws);backend.hints=copy.deepcopy(backend.hints)
        backend.hints['east_28_1.nsd']['source']['sha256']='0'*64
        result=backend.validate(d);self.assertFalse(result.valid)
        self.assertIn(('scenes',0,'level','environment_scene'),[p.path for p in result.problems])
    def test_campaign_two_scenes_same_geometry_independent_profiles(self):
        d={'schema':2,'chronicle':{'id':'p7_multi','name':'Two scenes'},'entry':'a','scenes':[
            {'id':sid,'level':{'source':'EastLondon','environment_scene':profile},'actors':[],'conversations':[],'events':[]}
            for sid,profile in [('a','EAST_28_1.nsd'),('b','l1_east.nsd')]]}
        report=self.backend.build(d,compile_java=False)
        self.assertEqual(report['scenes'],['a','b'])
        self.assertEqual([r['id'] for r in report['environment_profiles'].values()],['EAST_28_1.nsd','l1_east.nsd'])
    def test_build_fingerprint_tracks_original_environment_input(self):
        from rcm.service import build_inputs_fingerprint
        d=copy.deepcopy(self.data);d['level']['environment_scene']='l1_east.nsd'
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as root:
            ws=Workspace(Path(root))
            for name in ['levels','scene_hints']:ws.write('cache/'+name+'.json',self.ws.output('cache/'+name+'.json').read_bytes())
            _,hint=reference(self.backend.levels['EastLondon'],self.backend.hints,'l1_east.nsd')
            src=Path('research/original')/hint['source']['archive']/hint['source']['path']
            ws.write(src,self.ws.output(src).read_bytes());before=build_inputs_fingerprint(ws,d)
            content=ws.output(src).read_bytes();ws.write(src,content[:-1]+bytes([content[-1]^1]))
            with self.assertRaises(ValueError):build_inputs_fingerprint(ws,d)
            ws.write(src,content);self.assertEqual(build_inputs_fingerprint(ws,d),before)
    def test_package_version_contract_uses_current_application_version(self):
        import json
        from rcm import __version__
        from rcm.packages import verify_manifest
        files={'manifest.json':json.dumps({'format':1,'kind':'chronicle','id':'p7_pkg','version':'1.0.0','files':{},'custom_code':False,'requires_rcm':__version__}).encode()}
        self.assertEqual(verify_manifest(files,'chronicle')['requires_rcm'],__version__)
    def test_legacy_package_bytes_remain_pinned(self):
        expected='90b41cb0b203510fafadde9f08bef5afe484aaefcb2cc8aaafbc636b88ca86ab'
        d=Document.load(self.ws,'chronicles/editor_acceptance/project.yaml').snapshot()
        self.backend.build(d)
        package=self.ws.output('build/'+d['chronicle']['id']+'/'+d['chronicle']['id']+'_distribution.zip')
        self.assertEqual(hashlib.sha256(package.read_bytes()).hexdigest(),expected)

class SceneProfileGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])
    def test_select_save_undo_and_change_level_clear_profile(self):
        from PySide6.QtWidgets import QComboBox
        from rcm.editor.window import MainWindow
        backend=Backend(Workspace(ROOT));win=MainWindow(backend)
        win.doc=Document.load(backend.ws,'chronicles/east_demo.yaml');win.doc.path=ROOT/'build/tests/p7_gui.yaml'
        try:
            win.refresh();win.select(('level',));self.app.processEvents()
            combo=win.properties.widget().findChild(QComboBox,'environment_scene')
            combo.setCurrentIndex(combo.findData('l1_east.nsd'));self.app.processEvents()
            self.assertEqual(win.doc.data['level']['environment_scene'],'l1_east.nsd')
            win.doc.save();loaded=Document.load(backend.ws,win.doc.path)
            self.assertEqual(loaded.data['level']['environment_scene'],'l1_east.nsd')
            win.undo_project();self.assertNotIn('environment_scene',win.doc.data['level'])
            win.redo_project();self.assertEqual(win.doc.data['level']['environment_scene'],'l1_east.nsd')
            win.resource_chosen('levels','WestLondon');self.assertNotIn('environment_scene',win.doc.data['level'])
        finally:win.doc=None;win.close();self.app.processEvents()
