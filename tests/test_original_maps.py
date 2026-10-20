"""Native backgrounds, automatic associations and opt-in editable map layouts."""
import copy,io,os,sys,tempfile,zipfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from PIL import Image
from PySide6.QtWidgets import QApplication,QPushButton,QInputDialog,QDialog
from rcm.paths import Workspace
from rcm.service import Backend,build_inputs_fingerprint
from rcm.campaign_document import CampaignDocument
from rcm.original_maps import catalogue,associated,image_bytes,read
from rcm.chronicle_maps import labels
from rcm.packages import export_project,import_project
from test_authoring_completion import fixture

ROOT=Path(__file__).resolve().parents[1]
GAME=Path(r'H:\GOG\Vampire The Masquerade - Redemption')


class OriginalMaps(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT,GAME));cls.backend.safe_mode=True;cls.maps=catalogue(cls.backend)
    def source(self):
        root=fixture();root['chronicle']['id']='native_map'
        root['resources']['maps']=[dict(id='london',name='My London',original='mapLondonEast.nui',points=[dict(id='arrival',name='Our arrival',position=[219,313],visible=True,haven=False)])]
        root['scenes'][0]['map_location']=dict(map='london',point='arrival');return root
    def window(self,root):
        from rcm.editor.window import MainWindow
        win=MainWindow(self.backend);win.doc=CampaignDocument(self.backend.ws,root);win.refresh();return win
    def test_catalogue_uses_actual_nsc_associations_and_renders_all_eight_images(self):
        self.assertEqual(len(self.maps),8);associated_levels=0
        for name,row in self.maps.items():
            data=image_bytes(self.backend.ws,self.backend.original_resources,row)
            with Image.open(io.BytesIO(data)) as image:self.assertEqual(image.size,(640,480));self.assertGreater(len(image.getcolors(640*480)),100)
            self.assertEqual(row['file'],name);self.assertEqual(len(row['quads']),12)
        for level in self.backend.levels.values():
            native,point=associated(level,self.maps)
            if any(r['map_ui'].casefold() in {n.casefold() for n in self.maps} for r in level['references']):
                self.assertIsNotNone(native);self.assertIsNotNone(point);associated_levels+=1
                self.assertTrue(any(r['map_ui']==native['file'] and r['map_label']==point['label'] for r in level['references']))
        self.assertGreater(associated_levels,100)
        native,point=associated(self.backend.levels['EastLondon'],self.maps);self.assertEqual(native['file'],'mapLondonEast.nui');self.assertEqual(point['position'],[219,313])
        self.assertEqual(associated({'references':[dict(map_ui='foobar.nui',map_label='none')]},self.maps),(None,None))
    def test_default_preview_follows_active_level_without_mutating_project(self):
        from rcm.editor.maps import MapDialog
        root=fixture();other=copy.deepcopy(root['scenes'][0]);other['id']='club';other['level']['source']='ClubTenebrae';root['scenes'].append(other)
        win=self.window(root);before=win.doc.snapshot()
        try:
            for active,expected in ((0,'mapLondonEast.nui'),(1,'mapLondonWest.nui')):
                win.doc.active=active;dialog=MapDialog(win)
                self.assertIsNone(dialog.row());self.assertIsNone(dialog.maps.currentData());self.assertEqual(dialog.default_map['file'],expected)
                self.assertEqual(dialog.points.count(),len(dialog.default_map['points']));self.assertFalse(dialog.findChild(QPushButton,'map_image').isEnabled())
                dialog.reject();self.assertEqual(win.doc.snapshot(),before)
            root=fixture();root['scenes'][0]['level']['source']='';win.doc=CampaignDocument(self.backend.ws,root);dialog=MapDialog(win);self.assertIsNone(dialog.default_map);dialog.reject()
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_game_picker_defaults_to_current_level_cancel_apply_undo_and_save(self):
        from rcm.editor.maps import MapDialog
        win=self.window(fixture());before=win.doc.snapshot()
        try:
            dialog=MapDialog(win)
            def choose(*args):self.assertIn('mapLondonEast.nui',args[3][args[4]]);return args[3][args[4]],True
            with patch.object(QInputDialog,'getItem',side_effect=choose):dialog.findChild(QPushButton,'map_original').click()
            self.assertIn('original',dialog.row());self.assertEqual(dialog.point()['position'],[219,313]);dialog.reject();self.assertEqual(win.doc.snapshot(),before)
            dialog=MapDialog(win)
            with patch.object(QInputDialog,'getItem',side_effect=choose):dialog.add_original()
            dialog.point()['name']='My quay';dialog.accept();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted)
            after=win.doc.snapshot();self.assertTrue(self.backend.validate(after).valid);self.assertEqual(after['scenes'][0]['map_location'],dict(map='map1',point='place1'))
            win.undo_project();self.assertEqual(win.doc.snapshot(),before);win.redo_project();self.assertEqual(win.doc.snapshot(),after)
            with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                win.doc.path=Path(tmp)/'project.yaml';win.doc.save();loaded=CampaignDocument.load(self.backend.ws,win.doc.path);self.assertEqual(loaded.snapshot(),after)
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_original_background_build_references_tiles_without_copying_original_assets(self):
        root=self.source();before=copy.deepcopy(root);report=self.backend.build(root)
        self.assertEqual(root,before);self.assertEqual(set(report['class_versions'].values()),{'45.3'})
        stem=labels(root['chronicle']['id'],'london');point=labels(root['chronicle']['id'],'london','arrival')
        with zipfile.ZipFile(ROOT/'build/native_map/native_map.nob') as archive:
            nui=archive.read('ui/'+stem+'.nui').decode('cp1252');self.assertIn('quad mat=mapLondonEast01.tga pos=0,224 size=256,256',nui)
            self.assertIn('name='+point,nui);self.assertFalse(any(n.lower().endswith(('.tga','.nil')) for n in archive.namelist()))
            self.assertIn(stem+'.nui '+point,archive.read('chronicles/native_map.nsc').decode('cp1252'))
            self.assertIn('Our arrival',archive.read('strings/R_native_map_custom.nls').decode('cp1252'))
        self.assertEqual(build_inputs_fingerprint(self.backend.ws,root),build_inputs_fingerprint(self.backend.ws,copy.deepcopy(root)))
    def test_raveclub_can_choose_each_original_background_through_button_without_qt_errors(self):
        from rcm.editor.maps import MapDialog
        root=fixture();root['scenes'][0]['level']={'source':'RaveClub'};win=self.window(root);before=win.doc.snapshot()
        try:
            for filename,original in self.maps.items():
                dialog=MapDialog(win);self.assertIsNone(dialog.default_map)
                label=original['name']+' · '+filename
                with patch.object(QInputDialog,'getItem',return_value=(label,True)),patch.object(sys,'excepthook') as errors:
                    dialog.findChild(QPushButton,'map_original').click();errors.assert_not_called()
                self.assertEqual(dialog.row()['original'],filename);self.assertEqual(dialog.point()['position'],[312,232]);self.assertEqual(dialog.point()['name'],self.backend.level_label('RaveClub'))
                self.assertEqual(dialog.active_scene['map_location'],dict(map=dialog.row()['id'],point='place1'))
                dialog.reject();self.assertEqual(win.doc.snapshot(),before)
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_foreign_background_and_unselected_level_use_valid_names_and_persist(self):
        from rcm.editor.maps import MapDialog
        win=self.window(fixture())
        try:
            for source,name in (('EastLondon',self.backend.level_label('EastLondon')),('', 'street')):
                root=fixture();root['scenes'][0]['level']={'source':source};root['scenes'][0]['id']='street';root['entry']='street';win.doc=CampaignDocument(self.backend.ws,root)
                dialog=MapDialog(win);original=self.maps['mapVienna.nui']
                with patch.object(QInputDialog,'getItem',return_value=(original['name']+' · mapVienna.nui',True)):dialog.add_original()
                self.assertEqual(dialog.point()['name'],name);self.assertEqual(dialog.point()['position'],[312,232])
                dialog.accept();self.assertEqual(dialog.result(),QDialog.DialogCode.Accepted)
                with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                    win.doc.path=Path(tmp)/'project.yaml';win.doc.save();loaded=CampaignDocument.load(self.backend.ws,win.doc.path);self.assertEqual(loaded.snapshot(),win.doc.snapshot())
        finally:win.doc=None;win.close();self.app.processEvents()
    def test_project_export_import_keeps_only_original_map_reference_formats_9_10(self):
        for version in (9,10):
            root=self.source();root['project_format']=version
            if version==10:root['runtime_profile']='phase10'
            with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
                archive=export_project(self.backend.ws,root,Path(tmp)/'source.zip')
                with zipfile.ZipFile(archive) as z:self.assertEqual(set(z.namelist()),{'project.yaml','manifest.json'})
                restored=import_project(self.backend.ws,archive,Path(tmp)/'copy');self.assertEqual(restored.snapshot(),root);self.assertTrue(self.backend.validate(restored.snapshot()).valid)
    def test_invalid_map_sources_and_native_ui_names_are_rejected(self):
        for edit in ({'original':'../../mapLondonEast.nui'},{'original':'foobar.nui'},{'original':'missing.nui'},{'source':'x.png'}):
            root=self.source();root['resources']['maps'][0].update(edit);self.assertFalse(self.backend.validate(root).valid)
        for name in ('../mapLondonEast.nui','Vampire.exe','mapLondonEast.nui\n'):
            with self.assertRaises(ValueError):read(self.backend.ws,self.backend.original_resources,name)
