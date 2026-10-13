"""Product regressions. Synthetic process/filesystem and Qt are not Redemption."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import copy,hashlib,json,tempfile,zipfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch,Mock
from PySide6.QtWidgets import QApplication
from rcm.paths import Workspace
from rcm.app_settings import AppSettings
from rcm.product import project_id,validate_workspace,copy_example,verify_installation
from rcm.document import Document
from rcm.campaign_document import CampaignDocument
from rcm.project_safety import ExternalChange,backup_source,restore_backup,ProjectLock,duplicate_project
from rcm.playtest import prepare_playtest,launch_playtest,finish_playtest
from rcm.service import source_fingerprint,build_inputs_fingerprint,Backend,source_text

ROOT=Path(__file__).resolve().parents[1]


def source():
    return dict(schema=2,project_format=9,chronicle=dict(id='product_test',name='Test'),entry='street',state={'flags':{}},scenes=[dict(id='street',level={'source':'EastLondon'},actors=[],objects=[],conversations=[],events=[],triggers=[],entries=[],waypoints=[],paths=[],sequences=[],encounters=[])],quests=[],resources={},metadata={'version':'1.0.0'},build_options={'debug':True})


class ProductTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.root=Path(self.tmp.name);self.ws=Workspace(self.root/'workspace');self.ws.root.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def game(self):
        game=self.root/'game';game.mkdir();(game/'Vampire.exe').write_bytes(b'MZtest')
        for name in ('Resource.nob','Codex.nob','classes.zip'):
            with zipfile.ZipFile(game/name,'w') as z:z.writestr('test',b'data')
        (game/'Chronicles').mkdir();self.ws.game=game;return game
    def test_settings_migration_preserves_old_files_and_global_authority(self):
        old=self.ws.write('cache/game_settings.json',json.dumps({'installation':str(self.root/'game')}));lang=self.ws.write('cache/editor_settings.json','{"language":"es"}');before=(old.read_bytes(),lang.read_bytes())
        settings=AppSettings(self.root/'settings');settings.migrate(self.ws.root);self.assertEqual(settings.data['language'],'es');settings.save()
        settings.data['language']='en';settings.save();settings=AppSettings(self.root/'settings');settings.migrate(self.ws.root);self.assertEqual(settings.data['language'],'en');self.assertEqual(before,(old.read_bytes(),lang.read_bytes()))
    def test_corrupt_preferences_are_preserved_and_nonfatal(self):
        path=self.root/'settings';path.mkdir();(path/'settings.json').write_bytes(b'{broken')
        settings=AppSettings(path);self.assertTrue(settings.warning);self.assertEqual(next(path.glob('settings.corrupt.*')).read_bytes(),b'{broken');settings.save();self.assertEqual(AppSettings(path).data['schema'],1)
    def test_settings_reject_wrong_shapes_and_preserve_future_schema(self):
        for invalid in [dict(schema=1,recent_projects=[False]),dict(schema=1,autosave_seconds=-1),dict(schema=1,last_tab='x'),dict(schema=1,splitter_sizes=[-1])]:
            with self.assertRaises(ValueError):AppSettings.validate(invalid)
    def test_recents_dedupe_limit_missing_remove_does_not_delete(self):
        prefs=AppSettings(self.root/'settings')
        for i in range(15):prefs.recent(self.ws.root/(str(i)+'.yaml'),str(i))
        path=self.ws.write('14.yaml','private');prefs.recent(path,'Changed name');self.assertEqual(len(prefs.data['recent_projects']),12);self.assertEqual(prefs.data['recent_projects'][0]['name'],'Changed name');prefs.remove_recent(path);self.assertEqual(path.read_text(),'private')
    def test_ui_preferences_and_language_roundtrip(self):
        prefs=AppSettings(self.root/'settings');prefs.data.update(language='es',window_geometry='AA==',window_state='AA==',splitter_sizes=[200,700,340],last_tab=3,safe_mode=True);prefs.save();self.assertEqual(AppSettings(self.root/'settings').data,prefs.data)
    def test_name_id_collision_unicode_and_bound(self):
        self.assertEqual(project_id('Noche de Cenizas',self.ws.root),'noche_de_ceniz');ident=project_id('123 ñ',self.ws.root);self.assertTrue(ident.startswith('c_'));(self.ws.root/'chronicles'/ident).mkdir(parents=True);self.assertNotEqual(project_id('123 ñ',self.ws.root),ident);self.assertLessEqual(len(project_id('Very long title'*30,self.ws.root)),14)
    def test_installation_executable_and_archives_verified(self):
        game=self.game();self.assertEqual(verify_installation(game),game)
        (game/'Resource.nob').write_bytes(b'broken')
        with self.assertRaises(ValueError):verify_installation(game)
        with self.assertRaises(ValueError):validate_workspace(game/'projects',game)
    def test_example_copy_never_overwrites_and_owns_resource_paths(self):
        master=ROOT/'chronicles/tutorial/project.yaml';original=master.read_bytes();first=copy_example(self.ws,'tutorial');first.write_text('private edit');self.assertEqual(copy_example(self.ws,'tutorial').read_text(),'private edit');second=copy_example(self.ws,'tutorial',clean=True);self.assertNotEqual(first,second)
        loaded=Document.load(self.ws,second);resource=loaded.snapshot()['resources']['scripts'][0];self.assertTrue(self.ws.output(resource['source']).is_file());self.assertIn(second.parent.name,resource['source']);self.assertEqual(master.read_bytes(),original)
    def test_external_edit_blocks_save_before_any_backup_write(self):
        doc=CampaignDocument(self.ws,source());path=self.ws.output('chronicles/a/project.yaml');doc.save(path);saved=Document.load(self.ws,path);path.write_text('external edit');saved.campaign['chronicle']['name']='my edit'
        with self.assertRaises(ExternalChange):saved.save()
        self.assertEqual(path.read_text(),'external edit');saved.save(force=True);self.assertEqual(Document.load(self.ws,path).data['chronicle']['name'],'my edit')
    def test_another_editor_creating_new_draft_cannot_be_overwritten(self):
        doc=CampaignDocument.new(self.ws,'new_draft','Draft','chronicles/draft');self.ws.write(doc.path,'another editor')
        with self.assertRaises(ExternalChange):doc.save()
        self.assertEqual(doc.path.read_text(),'another editor')
    def test_changing_destination_does_not_compare_against_previous_file_hash(self):
        doc=CampaignDocument(self.ws,source());original=self.ws.output('chronicles/a/project.yaml');doc.save(original);before=original.read_bytes()
        doc.path=self.ws.output('chronicles/copy/project.yaml');doc.campaign['chronicle']['name']='Copy';doc.save()
        self.assertEqual(original.read_bytes(),before);self.assertEqual(Document.load(self.ws,doc.path).data['chronicle']['name'],'Copy')
    def test_rolling_backups_skip_duplicates_and_restore_both_states(self):
        doc=CampaignDocument(self.ws,source());doc.save(self.ws.output('chronicles/a/project.yaml'));old=doc.path.read_bytes()
        for i in range(25):backup_source(self.ws,'product_test',str(i).encode())
        count=len(list(self.ws.output('backups/product_test').glob('*.yaml')));backup_source(self.ws,'product_test',b'24');self.assertEqual(count,len(list(self.ws.output('backups/product_test').glob('*.yaml'))));self.assertEqual(count,20)
        valid=backup_source(self.ws,'product_test',old);doc.campaign['chronicle']['name']='unsaved';restore_backup(doc,valid);self.assertEqual(doc.campaign['chronicle']['name'],'Test');self.assertTrue(any(b'unsaved' in p.read_bytes() for p in self.ws.output('backups/product_test').glob('*.yaml')))
    def test_second_lock_warns_and_released_lock_is_recoverable(self):
        path=self.ws.write('chronicles/a/project.yaml',source_text(source()));first=ProjectLock(path);second=ProjectLock(path);self.assertTrue(first.acquire());self.assertFalse(second.acquire());first.release();self.assertTrue(second.acquire());second.release()
    def test_duplicate_project_contains_independent_custom_assets(self):
        data=source();self.ws.write('chronicles/a/custom.java','class Custom {}');data['resources']['scripts']=[dict(id='Custom',source='chronicles/a/custom.java')]
        doc=duplicate_project(self.ws,data,'chronicles/b','Copy','copy');self.assertEqual(doc.data['chronicle']['id'],'copy');script=doc.snapshot()['resources']['scripts'][0]['source'];self.assertEqual(self.ws.output(script).read_text(),'class Custom {}');self.assertNotEqual(script,data['resources']['scripts'][0]['source'])
    def test_duplicate_spatial_offset_no_external_redirect_and_undo_snapshot(self):
        from rcm.product_edit import duplicate_entity
        data=source();scene=data['scenes'][0];scene['actors']=[dict(id='mentor',name='Mentor',template='Anezka',transform=dict(position=[1,2,3],orientation=[0,0,0]),conversation={'default':'talk'})];original=copy.deepcopy(data)
        result,path=duplicate_entity(data,('scenes',0,'actors',0));self.assertEqual(data,original);self.assertEqual(result['scenes'][0]['actors'][1]['transform']['position'],[41,2,3]);self.assertNotIn('conversation',result['scenes'][0]['actors'][1]);self.assertEqual(path,('scenes',0,'actors',1));self.assertEqual(result['scenes'][0]['events'][0]['actions'],[{'spawn':'mentor_2'}])
    def test_playtest_incremental_ownership_and_direct_launch(self):
        game=self.game();data=source();ident=data['chronicle']['id'];backend=Mock(ws=self.ws);backend.validate.return_value=Mock(valid=True)
        def build(src,progress=None):
            bundle=self.ws.write('build/'+ident+'/bundle/'+ident+'.nob',b'generated package');report=dict(chronicle=ident,status='compiled-unverified-in-game',authoring_source_sha256=source_fingerprint(src),build_inputs_sha256=build_inputs_fingerprint(self.ws,src),distribution_files={ident+'.nob':dict(size=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest())});self.ws.write('build/'+ident+'/build_report.json',json.dumps(report));return report
        backend.build.side_effect=build
        with patch('rcm.deployment.game_running',return_value=False),patch('rcm.deployment.subprocess.Popen') as launch:
            launch.return_value.pid=123
            first=prepare_playtest(backend,data);self.assertTrue(first['built']);self.assertTrue(first['deployed']);second=prepare_playtest(backend,data);self.assertFalse(second['built']);self.assertFalse(second['deployed']);self.assertEqual(backend.build.call_count,1)
            process,record=launch_playtest(self.ws,ident);launch.assert_called_once_with([str(game/'Vampire.exe'),'-user','RCM\\'+ident],cwd=game);done=finish_playtest(self.ws,dict(record,pid=123),0);self.assertIsNotNone(done['ended'])
            target=game/'RCM'/ident/(ident+'.nob');target.write_bytes(b'user modified')
            with self.assertRaises(ValueError):prepare_playtest(backend,data)
            self.assertEqual(target.read_bytes(),b'user modified');self.assertEqual(process,launch.return_value)
    def test_invalid_or_open_game_never_builds_or_launches(self):
        backend=Mock(ws=self.ws);backend.validate.return_value=Mock(valid=False,problems=[Mock(severity='ERROR',message='bad')])
        with self.assertRaises(ValueError):prepare_playtest(backend,source())
        backend.build.assert_not_called();backend.validate.return_value=Mock(valid=True)
        with patch('rcm.deployment.game_running',return_value=True):
            with self.assertRaises(ValueError):prepare_playtest(backend,source())
        backend.build.assert_not_called()
    def test_managed_retirement_keeps_modified_foreign_and_legacy(self):
        from rcm.managed_deployments import list_deployments,remove_deployment
        game=self.game();folder=game/'RCM/product_test';folder.mkdir(parents=True);(folder/'own').write_bytes(b'own');(folder/'changed').write_bytes(b'edit');(folder/'foreign').write_bytes(b'foreign');legacy=game/'RCM/legacy';legacy.mkdir();(legacy/'data').write_bytes(b'legacy')
        (folder/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,chronicle='product_test',files={'own':hashlib.sha256(b'own').hexdigest(),'changed':hashlib.sha256(b'original').hexdigest()})))
        self.assertEqual(len(list_deployments(self.ws)),1)
        with patch('rcm.managed_deployments.game_running',return_value=False):result=remove_deployment(self.ws,'product_test')
        self.assertEqual(result['retained'],['changed']);self.assertFalse((folder/'own').exists());self.assertEqual((folder/'foreign').read_bytes(),b'foreign');self.assertEqual((legacy/'data').read_bytes(),b'legacy')
    def test_support_has_no_assets_projects_or_personal_paths_by_default(self):
        from rcm.support import support_bundle
        self.ws.write('build/editor/last_error.log',str(self.ws.root)+'\nprivate error');self.ws.write('chronicles/a/project.yaml','private project')
        path=support_bundle(self.ws,'support.zip')
        with zipfile.ZipFile(path) as archive:
            self.assertNotIn('project.yaml',archive.namelist());self.assertNotIn(str(self.ws.root),archive.read('build/editor/last_error.log').decode());self.assertFalse(any(n.endswith('.nob') for n in archive.namelist()))
    def test_setup_cancel_invalid_and_success_are_not_confused(self):
        from rcm.editor.product_ui import SetupDialog
        prefs=AppSettings(self.root/'settings');game=self.game();dialog=SetupDialog(prefs,game,self.ws.root)
        dialog.reject();self.assertFalse(prefs.data.get('setup_complete',False));self.assertFalse(prefs.path.exists())
        dialog.exe.setText(str(game/'not_vampire.exe'));dialog.check();self.assertEqual(dialog.result(),dialog.DialogCode.Rejected)
        dialog.exe.setText(str(game/'Vampire.exe'));dialog.check();self.assertEqual(dialog.result(),dialog.DialogCode.Accepted);self.assertEqual(dialog.ws.game,game)
    def test_shortcuts_created_on_destination_with_unicode_and_spaces(self):
        from rcm.shortcut import create_shortcut,read_shortcut
        target=self.ws.write('Tools with spaces ñ/app.exe',b'MZtest')
        path=create_shortcut(self.ws,'Mi crónica ñ',target,'-user RCM\\sample',target.parent)
        info=read_shortcut(path);self.assertEqual(Path(info['target']),target);self.assertEqual(Path(info['cwd']),target.parent);self.assertEqual(info['arguments'],'-user RCM\\sample')
    def test_release_translation_keys_cover_editor_calls(self):
        import ast
        from rcm.editor.i18n import catalogue
        missing=[]
        for path in (ROOT/'src/rcm/editor').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf8'))):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='tr' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str) and node.args[0].value not in catalogue():missing.append((path.name,node.args[0].value))
        self.assertEqual(missing,[])
    def test_carried_owned_templates_are_reused_without_changing_profiles(self):
        from rcm.profile_compatibility import compatibility_files,profile_references
        import struct,io
        game=self.game();old=game/'RCM/previous';old.mkdir(parents=True);archive=ROOT/'build/rcm_tutor/bundle/rcm_tutor.nob';data=archive.read_bytes();(old/'rcm_tutor.nob').write_bytes(data)
        payload={'rcm_tutor.nob':hashlib.sha256(data).hexdigest()}
        for p in (ROOT/'build/rcm_tutor/bundle/codex').glob('*.class'):
            (old/'codex').mkdir(exist_ok=True);(old/'codex'/p.name).write_bytes(p.read_bytes());payload['codex/'+p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
        (old/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,chronicle='rcm_tutor',files=payload)))
        profile=struct.pack('<II',0x1e,7)+b'R_rcm_tutor_s0_object1'.ljust(32,b'\0');(game/'Crypt').mkdir();(game/'Crypt/player.npf').write_bytes(profile)
        self.assertEqual(profile_references(profile),{'r_rcm_tutor_s0_object1'})
        current=(ROOT/'build/rcm_showcase/bundle/rcm_showcase.nob').read_bytes();result=compatibility_files(game,current)
        self.assertIn('rcm_compat.nob',result);self.assertEqual((game/'Crypt/player.npf').read_bytes(),profile)
        from rcm.formats import NotFile
        with zipfile.ZipFile(io.BytesIO(result['rcm_compat.nob'])) as z:
            names=[t.name for t in NotFile.read(z.read('misc/Templates/_rcm_compat.not')).templates]
        self.assertIn('R_rcm_tutor_s0_object1',names);self.assertFalse(any(name.endswith('.nsc') for name in result));self.assertTrue(any(name.endswith('Passive.class') for name in result))
        from rcm.packages import create_package,install_package,installed
        archive=self.ws.output('incoming.rcmpack');create_package(Workspace(ROOT),'rcm_showcase',archive)
        with patch('rcm.packages.game_running',return_value=False):install_package(self.ws,archive,True)
        registry=installed(self.ws);self.assertIn('rcm_compat.nob',registry['rcm_showcase']['files']);self.assertEqual((game/'Crypt/player.npf').read_bytes(),profile)


class ProductGuiTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([]);cls.backend=Backend(Workspace(ROOT))
    def test_welcome_actions_and_new_project_scenario_are_real_widgets(self):
        from rcm.editor.window import MainWindow,NewProjectDialog
        win=MainWindow(self.backend)
        self.assertEqual(win.product_stack.currentWidget(),win.welcome);self.assertEqual(win.actions['playtest'].shortcut().toString(),'F5');self.assertEqual(win.actions['build'].shortcut().toString(),'Ctrl+B')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            dialog=NewProjectDialog(win.backend.ws,win);dialog.pid.setText('new_ui');dialog.directory.setText(tmp);dialog.level.setCurrentIndex(dialog.level.findData('EastLondon'));win.create_project(dialog);self.assertTrue(win.backend.validate(win.doc.snapshot()).valid)
            win.project_lock.release()
        win.doc=None;win.close()
    def test_invalid_field_focus_loss_does_not_reenter_commit(self):
        from rcm.editor.window import MainWindow
        from PySide6.QtWidgets import QLineEdit,QMessageBox
        win=MainWindow(self.backend);win.open_path(ROOT/'chronicles/showcase/project.yaml');win.select(('actors',0));field=win.properties.widget().findChild(QLineEdit,'actor_id');before=win.doc.snapshot();field.setText('Invalid ID!')
        def focus_loss(*unused):field.editingFinished.emit();return QMessageBox.StandardButton.Ok
        with patch.object(QMessageBox,'warning',side_effect=focus_loss) as warning:self.assertFalse(win.commit_properties());self.assertEqual(warning.call_count,1)
        self.assertEqual(win.doc.snapshot(),before);self.assertTrue(field._rcm_pending);field._rcm_pending=False;win.doc=None;win.close()
    def test_showcase_all_deep_links_resolve_and_preset_count_is_current(self):
        from rcm.editor.window import MainWindow
        from PySide6.QtCore import QUrl
        from rcm.camera_presets import PRESETS
        win=MainWindow(self.backend);win.open_path(ROOT/'chronicles/showcase/project.yaml');matrix=json.loads((ROOT/'research/product_close/showcase_matrix.json').read_text(encoding='utf8'))
        self.assertEqual(len([c for c in win.doc.campaign['scenes'][0]['conversations'] if c['id'].startswith('cam')]),len(PRESETS))
        for row in matrix:
            if row['link']:win.guide_panel.navigate(QUrl(row['link']));self.assertIsNotNone(win.campaign_panel.path)
        win.doc._saved=source_text(win.doc.snapshot());win.close()
