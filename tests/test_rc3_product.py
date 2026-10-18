"""RC3 safety and product behaviour, using real codecs/Qt and synthetic installs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from rcm.paths import Workspace
from rcm.document import Document
from rcm.campaign_document import CampaignDocument
from rcm.input_limits import CURRENT_PROJECT_FORMAT
from rcm.startup import prepare_workspace
from rcm.formats import NotFile,Template,Tag

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/tests').mkdir(parents=True,exist_ok=True)


def draft():
    return dict(schema=2,project_format=9,chronicle=dict(id='rc3_test',name='RC3 test'),state={'flags':{}},entry='scene1',scenes=[dict(id='scene1',level={'source':'EastLondon'},actors=[],objects=[],conversations=[],events=[],triggers=[],entries=[],waypoints=[],paths=[],sequences=[],encounters=[])],quests=[],resources={})


class FormatSafety(unittest.TestCase):
    def test_current_and_supported_older_formats_open_without_rewriting(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));self.assertEqual(CURRENT_PROJECT_FORMAT,10)
            from rcm.service import source_text
            for version in (9,5,None):
                source=draft()
                if version is None:source.pop('project_format')
                else:source['project_format']=version
                path=ws.write('project.yaml',source_text(source));before=path.read_bytes();doc=Document.load(ws,path)
                self.assertIsInstance(doc,CampaignDocument);self.assertEqual(path.read_bytes(),before)

    def test_future_format_rejected_before_document_or_destination_write(self):
        from rcm.service import source_text
        from rcm.packages import export_project,import_project
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));source=draft();source['project_format']=11
            path=ws.write('project.yaml',source_text(source));before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'versión más reciente'):Document.load(ws,path)
            self.assertEqual(path.read_bytes(),before)
            archive=export_project(ws,source,'future.rcmproject')
            with self.assertRaisesRegex(ValueError,'Actualiza Redemption'):import_project(ws,archive,'imported')
            self.assertFalse(ws.output('imported').exists())

    def test_future_recovery_does_not_mutate_the_open_document(self):
        from rcm.service import source_text
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            ws=Workspace(Path(folder));path=ws.write('project.yaml',source_text(draft()));doc=Document.load(ws,path);before=doc.snapshot()
            future=draft();future['project_format']=11;ws.write(doc.recovery_path,source_text(future))
            with self.assertRaises(ValueError):doc.recover()
            self.assertEqual(doc.snapshot(),before);self.assertEqual(path.read_text(encoding='utf8'),source_text(draft()))


class InstallationCache(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.base=Path(self.temp.name);self.game=self.base/'game';self.game.mkdir();(self.game/'Chronicles').mkdir()
        (self.game/'Vampire.exe').write_bytes(b'MZ synthetic identity input')
        self.classes(b'first class library')
        with zipfile.ZipFile(self.game/'Codex.nob','w') as archive:archive.writestr('Codex.class',(ROOT/'research/original/Codex.nob/Codex.class').read_bytes())
        with zipfile.ZipFile(self.game/'Resource.nob','w') as archive:
            archive.writestr('scenes/base.nsd',(ROOT/'research/original/Resource.nob/scenes/EAST_28_1.nsd').read_bytes())
            archive.writestr('levels/base.nil',b'NIL\x10'+struct.pack('<I',27))
            archive.writestr('misc/Templates/global.not',NotFile([Template('ghost',[Tag(16,struct.pack('<I',9).ljust(32,b'\0'))])]).encode())
        (self.game/'Chronicles/demo.nsc').write_text('location Demo base.nil base.nsd map.nui demo 0x0060\n',encoding='ascii')
        self.ws=Workspace(self.base/'work',self.game)
        self.ws.write('cache/toolchain/ecj-3.26.0.jar',(ROOT/'cache/toolchain/ecj-3.26.0.jar').read_bytes())
        self.user=self.ws.write('chronicles/mine/project.yaml','user work\n');self.resource=self.ws.write('chronicles/mine/resources/mine.java','custom source\n');self.backup=self.ws.write('backups/mine.yaml','saved user version\n')
        self.unusual=self.ws.write('research/original/my_java.java','authored source outside the default folder\n')
    def tearDown(self):self.temp.cleanup()
    def classes(self,content):
        with zipfile.ZipFile(self.game/'classes.zip','w') as archive:archive.writestr('java/lang/Object.class',content)
    def intact(self):
        self.assertEqual(self.user.read_bytes(),b'user work\n');self.assertEqual(self.resource.read_bytes(),b'custom source\n');self.assertEqual(self.backup.read_bytes(),b'saved user version\n')
        self.assertEqual(self.unusual.read_bytes(),b'authored source outside the default folder\n')
    def test_first_scan_same_installation_and_equivalent_path(self):
        from rcm.catalogue import discover
        self.assertTrue(prepare_workspace(self.ws)['cache_rebuilt']);self.assertTrue(self.ws.output('cache/installation_identity.json').is_file())
        with patch('rcm.catalogue.discover',wraps=discover) as scan:
            self.assertFalse(prepare_workspace(self.ws)['cache_rebuilt']);scan.assert_not_called()
            other=self.base/'same_content';shutil.copytree(self.game,other);self.ws.game=other
            self.assertFalse(prepare_workspace(self.ws)['cache_rebuilt']);scan.assert_not_called()
        self.intact()
    def test_resource_change_rebuilds_and_discards_stale_derived_content(self):
        prepare_workspace(self.ws);old=json.loads(self.ws.output('cache/installation_identity.json').read_text())
        self.ws.write('research/original/Codex.nob/Removed.class',b'stale');self.ws.write('cache/textures/stale.png',b'derived')
        with zipfile.ZipFile(self.game/'Resource.nob','a') as archive:archive.writestr('new.txt','new resource')
        messages=[];result=prepare_workspace(self.ws,messages.append)
        self.assertTrue(result['installation_changed']);self.assertTrue(result['cache_rebuilt']);self.assertFalse(self.ws.output('research/original/Codex.nob/Removed.class').exists());self.assertEqual(self.ws.output('cache/textures/stale.png').read_bytes(),b'derived')
        self.assertNotEqual(json.loads(self.ws.output('cache/installation_identity.json').read_text())['sha256'],old['sha256']);self.assertTrue(any('ha cambiado' in m for m in messages));self.intact()
    def test_classes_zip_refresh_and_corrupt_identity_repair(self):
        prepare_workspace(self.ws);self.classes(b'changed class library');self.assertTrue(prepare_workspace(self.ws)['cache_rebuilt'])
        self.assertEqual(self.ws.output('cache/toolchain/classes.zip').read_bytes(),(self.game/'classes.zip').read_bytes())
        self.ws.write('cache/installation_identity.json','broken');self.assertTrue(prepare_workspace(self.ws)['cache_rebuilt']);self.intact()
    def test_legacy_cache_adopts_identity_without_rebuild(self):
        from rcm.catalogue import discover
        prepare_workspace(self.ws);self.ws.output('cache/installation_identity.json').unlink()
        with patch('rcm.catalogue.discover',wraps=discover) as scan:self.assertFalse(prepare_workspace(self.ws)['cache_rebuilt']);scan.assert_not_called()
        self.intact()


class ProductUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])
        cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');cls.root=Path(cls.temp.name)
        for name in ('levels','geometry','resources','chronicles','scene_hints','scene_profiles','motions'):
            source=ROOT/'cache'/(name+'.json')
            if source.exists():target=cls.root/'cache'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        shutil.copytree(ROOT/'research/original',cls.root/'research/original')
        for example in ('tutorial','showcase','mini_chronicle'):shutil.copytree(ROOT/'chronicles'/example,cls.root/'chronicles'/example)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):
        from rcm.service import Backend
        from rcm.app_settings import AppSettings
        from rcm.editor.i18n import configure
        from rcm.editor.window import MainWindow
        self.ws=Workspace(self.root);self.prefs=AppSettings(self.root/'settings');self.prefs.data['language']='es';self.ws.app_settings=self.prefs;configure(self.ws)
        self.backend=Backend(self.ws);self.backend.safe_mode=True;self.win=MainWindow(self.backend);self.win.show();self.app.processEvents()
    def tearDown(self):
        self.win.busy=False;self.win.doc=None;self.win.close();self.app.processEvents()
    def open_draft(self):
        from rcm.service import source_text
        path=self.ws.write('projects/current/project.yaml',source_text(draft()));self.win.open_path(path);self.app.processEvents();return path
    def test_valid_open_and_validation_keep_dock_hidden_and_reset_is_reasonable(self):
        from rcm.editor.product_ui import reset_layout,restore_ui
        path=self.open_draft();before=path.read_bytes();self.assertFalse(self.win.build_dock.isVisible());self.assertTrue(self.win.validate_project().valid);self.assertFalse(self.win.build_dock.isVisible())
        self.win.build_dock.show();self.win.validate_project();self.assertTrue(self.win.build_dock.isVisible());reset_layout(self.win);self.assertFalse(self.win.build_dock.isVisible());self.assertEqual(path.read_bytes(),before)
        import base64
        self.win.build_dock.show();self.prefs.data['window_state']=base64.b64encode(bytes(self.win.saveState())).decode();restore_ui(self.win);self.assertFalse(self.win.build_dock.isVisible())
    def test_errors_references_and_build_failure_open_correct_dock_pages(self):
        self.open_draft();self.win.doc.data['level']['source']='unknown';self.assertFalse(self.win.validate_project().valid);self.assertTrue(self.win.build_dock.isVisible());self.assertEqual(self.win.bottom_tabs.currentIndex(),0)
        self.win.doc.data['level']['source']='EastLondon';self.win.find_references(('state','flags'));self.assertTrue(self.win.build_dock.isVisible());self.assertEqual(self.win.bottom_tabs.currentIndex(),2)
        self.win.build_dock.hide();self.win.build_failed('expected failure','details');self.assertTrue(self.win.build_dock.isVisible());self.assertEqual(self.win.bottom_tabs.currentIndex(),1)
    def test_build_opens_construction_before_worker_completion(self):
        from PySide6.QtCore import QObject,Signal
        class FakeWorker(QObject):
            progress=Signal(str);succeeded=Signal(object);failed=Signal(str,str);completed=Signal()
            def __init__(self,*args):super().__init__()
            def run(self):self.completed.emit()
        self.open_draft()
        with patch('rcm.editor.window.BuildWorker',FakeWorker):
            self.win.build_project();self.assertTrue(self.win.build_dock.isVisible());self.assertEqual(self.win.bottom_tabs.currentIndex(),1)
            for _ in range(100):
                self.app.processEvents()
                if not self.win.busy:break
                from PySide6.QtTest import QTest
                QTest.qWait(10)
        self.assertFalse(self.win.busy)
    def test_conversion_only_offered_to_legacy_and_hidden_afterwards(self):
        self.open_draft();self.assertFalse(self.win.campaign_panel.convert_button.isVisible());self.assertFalse(self.win.convert_campaign_action.isVisible())
        legacy=json.loads(json.dumps(draft()));scene=legacy.pop('scenes')[0];legacy.pop('project_format');legacy.pop('entry');legacy.update(scene);legacy['schema']=1
        from rcm.service import source_text
        self.win.open_path(self.ws.write('projects/legacy/project.yaml',source_text(legacy)));self.win.center_tabs.setCurrentWidget(self.win.campaign_panel);self.app.processEvents()
        self.assertTrue(self.win.campaign_panel.convert_button.isVisible());self.assertTrue(self.win.convert_campaign_action.isVisible());self.assertTrue(self.win.campaign_panel.convert());self.assertFalse(self.win.campaign_panel.convert_button.isVisible());self.assertFalse(self.win.convert_campaign_action.isVisible())
    def test_import_uses_opening_lock_recents_and_releases_previous_lock(self):
        from rcm.packages import export_project
        from rcm.project_safety import ProjectLock
        from rcm.editor import package_panel
        old=self.open_draft();source=draft();source['chronicle']['id']='imported';archive=export_project(self.ws,source,'incoming.rcmproject');target=self.root/'projects/imported'
        with patch.object(package_panel.QFileDialog,'getOpenFileName',return_value=(str(archive),'')),patch.object(package_panel.QFileDialog,'getExistingDirectory',return_value=str(target)):package_panel.import_project(self.win)
        self.assertEqual(self.win.doc.path,target/'project.yaml');competitor=ProjectLock(self.win.doc.path);self.assertFalse(competitor.acquire());previous=ProjectLock(old);self.assertTrue(previous.acquire());previous.release()
        self.assertEqual(self.prefs.data['recent_projects'][0]['path'],str(self.win.doc.path));self.assertTrue(self.win.validate_project().valid)
        from rcm.editor.product_ui import close_project
        close_project(self.win);self.assertTrue(competitor.acquire());competitor.release();self.win.open_path(target/'project.yaml');self.assertIsNotNone(self.win.doc)
    def test_import_cancel_keeps_document_and_its_lock(self):
        from rcm.editor import package_panel
        old=self.open_draft()
        with patch.object(package_panel.QFileDialog,'getOpenFileName',return_value=('','')):package_panel.import_project(self.win)
        self.assertEqual(self.win.doc.path,old)
        from rcm.project_safety import ProjectLock
        self.assertFalse(ProjectLock(old).acquire())
    def test_no_hidden_legacy_controls_or_duplicate_language_selector(self):
        from PySide6.QtCore import QObject
        from PySide6.QtWidgets import QMenu
        self.assertIsNone(self.win.findChild(QMenu,'language_menu'));self.assertTrue(any(a.objectName()=='action_settings' for a in self.win.tools_menu.actions()))
        for name in ('campaign_save','campaign_integrity','campaign_deploy','campaign_run','game_settings','game_shortcut'):self.assertIsNone(self.win.campaign_panel.findChild(QObject,name))
        for method in ('deploy','run_game','game_settings','game_shortcut'):self.assertFalse(hasattr(self.win.campaign_panel,method))
        self.assertEqual(self.win.center_tabs.count(),7);self.assertIn('Vista global',self.win.center_tabs.tabText(self.win.center_tabs.indexOf(self.win.campaign_panel)))
    def test_welcome_hierarchy_and_help_names_keep_essential_actions(self):
        from PySide6.QtWidgets import QPushButton
        for name in ('new','open','tutorial','showcase','install'):self.assertTrue(self.win.welcome.findChild(QPushButton,'welcome_'+name).isVisible())
        self.assertTrue(self.win.welcome.findChild(QPushButton,'welcome_install').isFlat());self.assertFalse(self.win.welcome.findChild(QPushButton,'welcome_new').isFlat())
        self.assertEqual([a.text() for a in self.win.help_menu.actions()][:5],['Tutorial rápido','Showcase completo','Guía de esta crónica','Guía del editor','Atajos'])
    def test_chronicle_properties_keep_path_in_tooltip(self):
        from PySide6.QtWidgets import QLabel, QLineEdit
        self.open_draft();self.win.selection=('chronicle',);self.win.inspect()
        name=self.win.properties.widget().findChild(QLineEdit,'chronicle_name')
        self.assertEqual(name.toolTip(),str(self.win.doc.path))
        notes=[label.text() for label in self.win.properties.widget().findChildren(QLabel)]
        self.assertFalse(any(str(self.win.doc.path) in text or 'build/<ID>' in text for text in notes))
        self.assertTrue(any('F5' in text for text in notes))
    def test_human_status_uses_existing_technical_states(self):
        from rcm.editor.product_ui import refresh_status
        self.open_draft();self.win.product_valid=True
        with patch('rcm.playtest.current_build',return_value={'status':'success'}),patch('rcm.playtest.current_deploy',return_value=True):refresh_status(self.win)
        self.assertEqual(self.win.product_status.text(),'✓ Lista para probar');self.assertEqual(self.win.project_status.build,'current');self.assertIn('Construcción',self.win.product_status.toolTip())
        self.win.doc.data['chronicle']['name']='changed';refresh_status(self.win);self.assertIn('Cambios sin guardar',self.win.product_status.text());self.win.product_valid=False;refresh_status(self.win);self.assertIn('Hay errores',self.win.product_status.text())
        self.win.busy=True;refresh_status(self.win);self.assertIn('Preparando prueba',self.win.product_status.text())


class ShowcaseGuide(unittest.TestCase):
    def test_human_sections_precede_complete_index_and_links_resolve(self):
        import re
        source=json.loads(json.dumps(__import__('yaml').safe_load((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))))
        for filename,heading in [('README.md','## Índice técnico completo'),('README.en.md','## Complete technical index')]:
            text=(ROOT/'chronicles/showcase'/filename).read_text(encoding='utf8');self.assertGreater(text.index(heading),text.index('## '));intro=text[:text.index(heading)];self.assertNotIn('[quay · cam',intro)
            for scene,kind,ident in re.findall(r'\]\(rcm://([^/]+)/([^/]+)/([^/)]+)\)',text):
                if kind=='quests':self.assertTrue(any(q['id']==ident for q in source['quests']));continue
                s=next(s for s in source['scenes'] if s['id']==scene)
                if kind=='scene':self.assertEqual(s['id'],ident)
                else:self.assertTrue(any(e['id']==ident for e in s[kind]))
    def test_only_showcase_labels_and_comments_changed_not_its_story(self):
        baseline=json.loads((ROOT/'tests/fixtures/rc3_story.json').read_text(encoding='utf8'));self.assertEqual(hashlib.sha256((ROOT/'chronicles/tutorial/project.yaml').read_bytes()).hexdigest(),baseline['tutorial_sha256'])
        import yaml
        original=baseline['showcase']
        current=yaml.safe_load((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
        def normalise(value):
            if isinstance(value,dict):
                for key,child in value.items():
                    if key in {'prompt','text','title','description'} and isinstance(child,str):value[key]=child.replace('Victoria','Anezka')
                    else:normalise(child)
            elif isinstance(value,list):
                for child in value:normalise(child)
        # RC4 explicitly adds only an optional station. Keep the RC3 story
        # pinned after removing those named additions, never normalise broadly.
        if current.get('project_format')==10:
            current['project_format']=9
            # The requested closure adds one named optional cinematic room and
            # its menu hub. Keep the ORIGINAL fixture pinned, removing only
            # these explicit additions before comparing the main story.
            current['scenes']=[s for s in current['scenes'] if s['id']!='director_lab']
            current['quests']=[q for q in current['quests'] if q['id'] not in {'dynamic_lab','director'}]
            for key in ('director_ready','director_fight','director_knock'):current['state']['flags'].pop(key,None)
            current['resources'].pop('camera_paths',None)
            for scene in current['scenes']:
                scene.pop('generators',None)
                scene['events']=[e for e in scene['events'] if e['id'] not in {'dyn_menu','dyn_begin','dyn_next','dyn_end','dyn_stop','dyn_portal','dyn_hub_play','dyn_hub_cinema','dyn_hub_back'}]
                scene['conversations']=[c for c in scene['conversations'] if c['id'] not in {'dyn','dyn_hub'}]
                for conversation in scene['conversations']:
                    if conversation['id']=='guide':conversation['choices']=[c for c in conversation['choices'] if c.get('result')!=8]
        for data in (original,current):
            for scene in data['scenes']:
                for kind in ('actors','objects'):
                    for entity in scene[kind]:entity.pop('name',None);entity.pop('comment',None)
            normalise(data)
        self.assertEqual(current,original)

