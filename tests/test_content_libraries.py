"""Untrusted data selection and dependency ownership, without native execution."""
import json,tempfile,zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from rcm.paths import Workspace
from rcm.formats import NotFile,Template,Tag
from rcm.content_libraries import prepare_import,preview,import_content,overlay,local_dependencies,read_entry,remove_content,manifests,ROOT as LIBRARIES
from rcm.generator import zip_bytes

ROOT=Path(__file__).resolve().parents[1]


class ContentLibraries(TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.ws=Workspace(Path(self.tmp.name))
        original=NotFile([Template('_prop',[Tag.integer(16,2)])]).encode();self.ws.write('research/original/Resource.nob/misc/templates/_base.not',original)
        self.base=dict(entries=[dict(id='_base',extension='.not',archive='Resource.nob',path='misc/templates/_base.not'),dict(id='barrel',extension='.nod',archive='Resource.nob',path='3d/models/barrel.nod')],templates=[dict(id='_prop',kind='props')])
        self.child=NotFile([Template('newCrate',[Tag.text(0,'_prop'),Tag.text(4,'barrel.nod'),Tag.text(82,'box_hover'),Tag(127,b'\x90'+bytes(31))])]).encode()
        self.source=self.ws.write('mod.nob',zip_bytes({'misc/templates/new.not':self.child,'ui/menu.nui':b'not imported','codex/Untrusted.class':b'not imported','chronicles/demo.nsc':b'not imported','strings/text.nls':b'box_hover A strange crate\r\nunused Never import this\r\n'}))
    def tearDown(self):self.tmp.cleanup()
    def backend(self):return SimpleNamespace(ws=self.ws,original_resources=self.base,refresh_import=lambda:None)
    def test_real_backend_build_keeps_library_local_and_deploys_to_synthetic_rcm(self):
        import shutil
        from unittest.mock import patch
        from rcm.service import Backend
        from rcm.deployment import deploy
        from test_release10 import blank
        game=Path(r'H:\GOG\Vampire The Masquerade - Redemption');base=Backend(Workspace(ROOT,game));ws=Workspace(self.ws.root/'real',game)
        for name in ('levels','resources','scene_hints'):ws.write('cache/'+name+'.json',(ROOT/'cache'/ (name+'.json')).read_bytes())
        for name in base.levels['EastLondon']['scenes']:
            e=base.hints[name.casefold()]['source'];rel='research/original/'+e['archive']+'/'+e['path'];ws.write(rel,(ROOT/rel).read_bytes())
        shutil.copytree(ROOT/'research/original/Chronicles',ws.output('research/original/Chronicles'))
        shutil.copytree(ROOT/'research/original/Codex.nob',ws.output('research/original/Codex.nob'))
        for name in ('classes.zip','ecj-3.26.0.jar'):ws.write('cache/toolchain/'+name,(ROOT/'cache/toolchain'/name).read_bytes())
        backend=Backend(ws);source=ws.write('source.nob',zip_bytes({'templates/extra.not':NotFile([Template('libraryCrate',[Tag.text(0,'barrel1')])]).encode()}))
        record=import_content(backend,source,'templates/extra.not',['libraryCrate']);root=blank();root['chronicle']['id']='library_test';s=root['scenes'][0]
        s['objects']=[dict(id='crate',name='Crate',template='libraryCrate',transform=dict(position=[-176,-612,384],orientation=[0,0,0]))];s['events']=[dict(id='start',when='scene_start',actions=[dict(spawn='crate')])]
        report=backend.build(root);self.assertEqual(report['local_libraries'][0]['id'],record['id']);self.assertNotIn(record['archive'],report['distribution_files'])
        with zipfile.ZipFile(ws.output('build/library_test/library_test_distribution.zip')) as z:self.assertNotIn(record['archive'],z.namelist())
        fake=ws.output('test_game');fake.mkdir()
        # No files are written to the actual installation. This exercises the
        # deploy transaction against an owned synthetic destination only.
        with patch('rcm.deployment.configured_game',return_value=fake),patch('rcm.deployment.game_running',return_value=False),patch('rcm.wtd.shared_dependencies',return_value={}):deploy(ws,'library_test')
        self.assertEqual((fake/'RCM/library_test'/record['archive']).read_bytes(),local_dependencies(ws,report)[record['archive']])
        from rcm.deployment_many import deploy_many
        from rcm.profile_compatibility import compatibility_files
        from rcm.formats import fixed
        import struct
        (fake/'Crypt').mkdir();(fake/'Crypt/player.npf').write_bytes(struct.pack('<II',0x1e,123)+fixed('R_library_test_s0_crate'))
        compat=compatibility_files(fake,zip_bytes({}))
        self.assertEqual(compat[record['archive']],local_dependencies(ws,report)[record['archive']])
        with patch('rcm.deployment_many.configured_game',return_value=fake),patch('rcm.deployment_many.game_running',return_value=False),patch('rcm.wtd.shared_dependencies',return_value={}):deploy_many(ws,['library_test'],'shared')
        self.assertTrue((fake/'RCM/shared'/record['archive']).is_file())
        # The next workspace has no library dependency in its current build,
        # but updating the shared folder must retain its sibling's dependency.
        data=zip_bytes({});ws.write('build/other/bundle/other.nob',data);ws.write('build/other/build_report.json',json.dumps(dict(chronicle='other',status='compiled-unverified-in-game',distribution_files={'other.nob':dict(size=len(data),sha256=__import__('hashlib').sha256(data).hexdigest())})))
        with patch('rcm.deployment_many.configured_game',return_value=fake),patch('rcm.deployment_many.game_running',return_value=False),patch('rcm.wtd.shared_dependencies',return_value={}):deploy_many(ws,['other'],'shared',preserve_siblings=True)
        self.assertEqual((fake/'RCM/shared'/record['archive']).read_bytes(),compat[record['archive']])
        remove_content(backend,record['id']);self.assertFalse(any(t['id']=='libraryCrate' for t in backend.original_resources['templates']))
        self.assertEqual(compatibility_files(fake,zip_bytes({}))[record['archive']],compat[record['archive']])
    def test_selected_library_preserves_unknown_tags_without_importing_code_or_menus(self):
        self.assertEqual(preview(self.source),{'misc/templates/new.not':['newCrate']})
        data,record=prepare_import(self.ws,self.source,'misc/templates/new.not',['newCrate'],self.base)
        with zipfile.ZipFile(__import__('io').BytesIO(data)) as z:
            self.assertEqual(len(z.namelist()),2);self.assertFalse(any('ui/' in n or 'codex/' in n or 'demo' in n for n in z.namelist()))
            row=NotFile.read(z.read(record['not_path'])).templates[0];self.assertEqual(row.tags[-1].value,b'\x90'+bytes(31))
            self.assertIn(b'A strange crate',z.read(record['nls_path']));self.assertNotIn(b'unused',z.read(record['nls_path']))
            self.assertNotEqual(next(t.value for t in row.tags if t.id==82).split(b'\0')[0],b'box_hover')
        self.assertFalse(record['code_imported']);self.assertFalse(record['redistribute'])
    def test_library_ai_cannot_reference_missing_discipline_code(self):
        self.ws.write('research/original/Resource.nob/misc/game.ndd','KnownPower group 1 OriginalDiscipline\n')
        self.base['entries'].append(dict(id='game',extension='.ndd',archive='Resource.nob',path='misc/game.ndd'))
        template=NotFile([Template('extra',[Tag.text(0,'_prop'),Tag.text(56,'extra.nai')])]).encode()
        for power,valid in [('KnownPower',True),('UnknownPower',False)]:
            source=self.ws.write('ai.nob',zip_bytes({'templates/extra.not':template,'misc/AI/extra.nai':('discipline '+power+' 2\n').encode()}))
            if valid:self.assertTrue(prepare_import(self.ws,source,'templates/extra.not',['extra'],self.base)[1]['templates'])
            else:
                with self.assertRaisesRegex(ValueError,'unavailable discipline'):prepare_import(self.ws,source,'templates/extra.not',['extra'],self.base)
    def test_local_dependency_is_verified_and_import_is_idempotent(self):
        b=self.backend();record=import_content(b,self.source,'misc/templates/new.not',['newCrate']);self.assertEqual(import_content(b,self.source,'misc/templates/new.not',['newCrate']),record)
        merged=overlay(self.ws,self.base);entry=next(e for e in merged['entries'] if e['extension']=='.not' and e.get('imported_pack'))
        self.assertEqual(NotFile.read(read_entry(self.ws,entry)).templates[0].name,'newCrate')
        dependency=local_dependencies(self.ws,dict(local_libraries=merged['local_libraries']));self.assertEqual(set(dependency),{record['archive']})
        self.ws.write(LIBRARIES+'/'+record['id']+'/'+record['archive'],b'changed')
        with self.assertRaises(ValueError):local_dependencies(self.ws,dict(local_libraries=merged['local_libraries']))
    def test_remove_preserves_sources_and_blocks_project_and_parent_library_dependencies(self):
        original=self.source.read_bytes();a=import_content(self.backend(),self.source,'misc/templates/new.not',['newCrate'])
        source=self.ws.write('child.nob',zip_bytes({'child.not':NotFile([Template('childCrate',[Tag.text(0,'newCrate')])]).encode()}))
        b=import_content(SimpleNamespace(ws=self.ws,original_resources=overlay(self.ws,self.base),refresh_import=lambda:None),source,'child.not',['childCrate'])
        self.assertEqual(b['dependencies'][0]['id'],a['id'])
        # Preserve non-template asset dependencies too when a saved inventory
        # wrapper is later reused from an unrelated workspace/launch folder.
        from rcm.profile_compatibility import compatibility_files
        from rcm.formats import fixed
        import struct,hashlib
        game=self.ws.output('fake_game');folder=game/'RCM/old';folder.mkdir(parents=True);(game/'Crypt').mkdir()
        (game/'Crypt/player.npf').write_bytes(struct.pack('<II',0x1e,123)+fixed('R_rcm_test_key'))
        wrapper=zip_bytes({'misc/templates/_key.not':NotFile([Template('R_rcm_test_key',[Tag.text(0,'childCrate')])]).encode()})
        owned={'key.nob':wrapper,**{r['archive']:self.ws.output(LIBRARIES+'/'+r['id']+'/'+r['archive']).read_bytes() for r in (a,b)}}
        for name,data in owned.items():(folder/name).write_bytes(data)
        (folder/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,files={n:hashlib.sha256(v).hexdigest() for n,v in owned.items()})))
        compat=compatibility_files(game,zip_bytes({}));self.assertEqual(compat[a['archive']],owned[a['archive']]);self.assertEqual(compat[b['archive']],owned[b['archive']])
        (folder/a['archive']).unlink()
        with self.assertRaisesRegex(ValueError,'saved-inventory library dependency'):compatibility_files(game,zip_bytes({}))
        with self.assertRaisesRegex(ValueError,'Other libraries require'):remove_content(self.backend(),a['id'])
        with self.assertRaisesRegex(ValueError,'open chronicle uses'):remove_content(self.backend(),b['id'],dict(resources=dict(templates=[dict(id='own',base='childCrate')])))
        remove_content(self.backend(),b['id']);remove_content(self.backend(),a['id']);self.assertEqual(manifests(self.ws),[]);self.assertEqual(self.source.read_bytes(),original)
    def test_manager_removal_uses_explicit_confirmation_and_updates_catalogue(self):
        import os
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        from unittest.mock import patch
        from PySide6.QtWidgets import QApplication,QWidget,QDialog,QTreeWidget,QPushButton,QMessageBox
        from rcm.editor.content_libraries import manage_libraries
        app=QApplication.instance() or QApplication([]);record=import_content(self.backend(),self.source,'misc/templates/new.not',['newCrate'])
        win=QWidget();win.backend=self.backend();win.doc=None;win.commit_properties=lambda:True;win.refresh=lambda:None;win.browser=SimpleNamespace(refresh=lambda:None)
        def click(dialog):
            tree=dialog.findChild(QTreeWidget,'installed_libraries');tree.setCurrentItem(tree.topLevelItem(0));dialog.findChild(QPushButton,'library_remove').click();return QDialog.DialogCode.Rejected
        with patch('rcm.editor.content_libraries.QDialog.exec',click),patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.No):manage_libraries(win)
        self.assertEqual(manifests(self.ws)[0]['id'],record['id'])
        with patch('rcm.editor.content_libraries.QDialog.exec',click),patch.object(QMessageBox,'question',return_value=QMessageBox.StandardButton.Yes):manage_libraries(win)
        self.assertEqual(manifests(self.ws),[]);win.close();app.processEvents()
    def test_missing_data_external_code_collision_and_unknown_versions_fail_closed(self):
        for tag,value in [(4,'missing.nod'),(11,'Untrusted')]:
            source=self.ws.write('bad.nob',zip_bytes({'misc/a.not':NotFile([Template('other',[Tag.text(0,'_prop'),Tag.text(tag,value)])]).encode(),'codex/Untrusted.class':b'not executable here'}))
            with self.assertRaises(ValueError):prepare_import(self.ws,source,'misc/a.not',['other'],self.base)
        source=self.ws.write('bad.nob',zip_bytes({'misc/a.not':self.child,'3d/models/barrel.nod':b'replaces original'}))
        self.ws.write('research/original/Resource.nob/3d/models/barrel.nod',b'original')
        with self.assertRaises(ValueError):prepare_import(self.ws,source,'misc/a.not',['newCrate'],self.base)
    def test_source_export_never_contains_third_party_library_and_missing_dependency_is_clear(self):
        from rcm.packages import export_project,read_archive,import_project
        from test_release10 import blank
        import_content(self.backend(),self.source,'misc/templates/new.not',['newCrate'])
        root=blank();archive=self.ws.output('source.zip');export_project(self.ws,root,archive);files=read_archive(archive)
        self.assertEqual(set(files),{'manifest.json','project.yaml'});self.assertEqual(len(json.loads(files['manifest.json'])['local_libraries']),1)
        other=Workspace(self.ws.output('other'));other.root.mkdir()
        with self.assertRaisesRegex(ValueError,'required local template library'):import_project(other,archive,'imported')
