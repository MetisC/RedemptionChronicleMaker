"""Shared runtime content survives workspace and chronicle selection changes."""
import json
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch

from rcm.generator import zip_bytes
from rcm.paths import Workspace
from rcm.wtd import ARCHIVE,PACK,ROOT as IMPORT_ROOT,publish_shared,shared_dependencies,local_dependencies,sha

ROOT=Path(__file__).resolve().parents[1]


class SharedContent(TestCase):
    def setUp(self):
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.game=self.root/'game';self.game.mkdir()
        for name in ('Vampire.exe','Resource.nob'):(self.game/name).write_bytes(b'fixture')
        self.ws=Workspace(self.root/'workspace',self.game)
        self.pack=zip_bytes({'misc/game.ncd':b'local test content'})
        self.record=dict(sha256=sha(self.pack))
        # These installations are synthetic. Patch every imported alias so a
        # real game (or a restricted process query) cannot affect the fixture.
        from rcm import deployment, deployment_many, packages
        for module in (deployment,deployment_many,packages):
            running=patch.object(module,'game_running',return_value=False)
            running.start();self.addCleanup(running.stop)
    def publish(self):publish_shared(self.ws,self.pack,self.record)
    def build(self,ident):
        data=zip_bytes({});relative=ident+'.nob'
        self.ws.write('build/'+ident+'/bundle/'+relative,data)
        report=dict(status='compiled-unverified-in-game',chronicle=ident,distribution_files={relative:dict(sha256=sha(data))})
        self.ws.write('build/'+ident+'/build_report.json',json.dumps(report));return report
    def test_root_pack_available_without_workspace_import(self):
        self.publish();self.assertFalse(self.ws.output(IMPORT_ROOT+'/import.json').exists())
        self.assertEqual(shared_dependencies(self.game),{ARCHIVE:self.pack})
        self.assertEqual(local_dependencies(self.ws,{}),{ARCHIVE:self.pack})
        self.assertEqual(local_dependencies(Workspace(self.root/'another_workspace',self.game),{}),{ARCHIVE:self.pack})
        self.assertFalse((self.game/ARCHIVE).exists())
    def test_existing_launch_folders_receive_owned_mirror_and_legacy_is_retired(self):
        folder=self.game/'RCM/existing';folder.mkdir(parents=True)
        (folder/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,files={},owners={'existing':[]},compatibility_files=[ARCHIVE])))
        legacy=self.game/'RCM/_content/within_the_darkness';legacy.mkdir(parents=True)
        (legacy/ARCHIVE).write_bytes(self.pack)
        (legacy/'import.json').write_text(json.dumps(dict(format=1,id=PACK,sha256=sha(self.pack))))
        self.publish();self.assertEqual((folder/ARCHIVE).read_bytes(),self.pack)
        record=json.loads((folder/'.rcm_deployment.json').read_text())
        self.assertEqual(record['shared_content_files'],[ARCHIVE]);self.assertEqual(record['files'][ARCHIVE],sha(self.pack))
        self.assertEqual(record['compatibility_files'],[])
        self.assertEqual(record['owners'],{'existing':[]});self.assertFalse((legacy/ARCHIVE).exists())
        self.assertFalse((legacy/'import.json').exists())
    def test_foreign_mirror_aborts_before_writing_root(self):
        folder=self.game/'RCM/foreign';folder.mkdir(parents=True)
        (folder/'.rcm_deployment.json').write_text(json.dumps(dict(format=1,files={})))
        (folder/ARCHIVE).write_bytes(b'foreign')
        with self.assertRaises(ValueError):self.publish()
        self.assertFalse((self.game/'RCM'/ARCHIVE).exists());self.assertEqual((folder/ARCHIVE).read_bytes(),b'foreign')
    def test_running_game_and_tampered_root_are_rejected(self):
        with patch('rcm.deployment.game_running',return_value=True),self.assertRaises(ValueError):self.publish()
        self.publish();(self.game/'RCM'/ARCHIVE).write_bytes(b'changed')
        with self.assertRaises(ValueError):shared_dependencies(self.game)
        with self.assertRaises(ValueError):self.publish()
    def test_single_and_multi_deploy_without_import_and_playtest_cache(self):
        from rcm.deployment import deploy
        from rcm.deployment_many import deploy_many
        from rcm.playtest import current_deploy
        self.publish();report=self.build('single');self.build('second')
        deploy(self.ws,'single');self.assertEqual((self.game/'RCM/single'/ARCHIVE).read_bytes(),self.pack)
        self.assertTrue(current_deploy(self.ws,report))
        deploy_many(self.ws,['single','second'],'shared')
        folder=self.game/'RCM/shared';self.assertEqual((folder/ARCHIVE).read_bytes(),self.pack)
        record=json.loads((folder/'.rcm_deployment.json').read_text())
        self.assertEqual(record['shared_content_files'],[ARCHIVE])
        self.assertTrue(all(ARCHIVE not in names for names in record['owners'].values()))
        from rcm.profile_compatibility import refresh_installed_profiles
        refresh_installed_profiles(self.ws)
        self.assertEqual((folder/ARCHIVE).read_bytes(),self.pack)
        (self.game/'RCM/single'/ARCHIVE).write_bytes(b'changed');self.assertFalse(current_deploy(self.ws,report))
    def test_build_dependency_matches_shared_pack_without_local_import(self):
        self.publish();report=dict(imported_content=[dict(id=PACK,name='Within The Darkness',sha256=sha(self.pack),archive=ARCHIVE)])
        self.assertEqual(local_dependencies(self.ws,report),{ARCHIVE:self.pack})
        report['imported_content'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):local_dependencies(self.ws,report)
    def test_no_pack_leaves_base_game_deploy_unchanged(self):
        from rcm.deployment import deploy
        self.assertEqual(local_dependencies(self.ws,{}),{})
        self.build('base');deploy(self.ws,'base')
        self.assertFalse((self.game/'RCM/base'/ARCHIVE).exists())
    def test_package_install_update_and_remove_keep_root_content(self):
        from rcm.packages import install_package,uninstall_package
        from test_safety_unit import package
        self.publish();archive=self.ws.write('package.rcmpack',package())
        install_package(self.ws,archive,True);folder=self.game/'RCM/unit_demo'
        self.assertEqual((folder/ARCHIVE).read_bytes(),self.pack)
        archive.write_bytes(package(version='0.2.0'));install_package(self.ws,archive,True)
        self.assertEqual((folder/ARCHIVE).read_bytes(),self.pack)
        uninstall_package(self.ws,'unit_demo')
        self.assertFalse((folder/ARCHIVE).exists());self.assertEqual(shared_dependencies(self.game),{ARCHIVE:self.pack})
