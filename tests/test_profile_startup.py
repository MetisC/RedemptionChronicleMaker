"""Saved inventory restoration precedes chronicle selection (offline regressions)."""
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
from unittest import TestCase
from unittest.mock import patch
import zipfile

from rcm.formats import NotFile,Tag,Template
from rcm.generator import zip_bytes
from rcm.paths import Workspace
from rcm.profile_compatibility import compatibility_files,refresh_installed_profiles

ROOT=Path(__file__).resolve().parents[1]


class ProfileStartupTests(TestCase):
    def setUp(self):
        (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests')
        self.root=Path(self.tmp.name);self.game=self.root/'game';self.game.mkdir()
        (self.game/'Vampire.exe').write_bytes(b'MZfixture');(self.game/'Resource.nob').write_bytes(b'fixture')
        (self.game/'Crypt').mkdir();self.ws=Workspace(self.root/'workspace',self.game);self.ws.root.mkdir()
        self.key=Template('R_rcm_showcase_s1_key',[Tag.text(0,'oldKey'),Tag.text(11,'R_rcm_showcase_s1_Passive'),Tag(400,bytes(range(32)))])
        self.key_nob=zip_bytes({'misc/templates/_showcase.not':NotFile([self.key]).encode()})
        self.empty_nob=zip_bytes({'misc/templates/_tutorial.not':NotFile([]).encode()})
        self.saved=struct.pack('<II',0x1e,7)+b'R_rcm_showcase_s1_key'.ljust(32,b'\0')
        self.profile=self.game/'Crypt/player.npf'

    def tearDown(self):self.tmp.cleanup()

    def installed(self,name,files,owners=None):
        folder=self.game/'RCM'/name;folder.mkdir(parents=True)
        for relative,data in files.items():
            file=folder/relative;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
        manifest=dict(format=1,chronicle=name,files={n:hashlib.sha256(d).hexdigest() for n,d in files.items()})
        if owners is not None:manifest['owners']=owners
        (folder/'.rcm_deployment.json').write_text(json.dumps(manifest))
        return folder

    def donor(self):
        return self.installed('rcm_showcase',{'rcm_showcase.nob':self.key_nob,'codex/R_rcm_showcase_s1_Passive.class':b'fixture-bytecode'})

    def test_shared_directory_after_new_item_and_return_to_desktop_shortcut(self):
        from rcm.playtest import finish_playtest
        self.donor();folder=self.installed('east_demo',{'rcm_tutor.nob':self.empty_nob},owners={'rcm_tutor':['rcm_tutor.nob']})
        self.profile.write_bytes(self.saved)
        before=(folder/'rcm_tutor.nob').read_bytes()
        with patch('rcm.deployment.game_running',return_value=False):
            record=finish_playtest(self.ws,{'chronicle':'rcm_showcase'},0)
            again=refresh_installed_profiles(self.ws)
        self.assertNotIn('profile_compatibility_error',record)
        self.assertIn('east_demo',record['profile_compatibility']['updated']);self.assertEqual(again['updated'],[])
        self.assertEqual(self.profile.read_bytes(),self.saved);self.assertEqual((folder/'rcm_tutor.nob').read_bytes(),before)
        with zipfile.ZipFile(folder/'rcm_compat.nob') as z:
            library=NotFile.read(z.read('misc/Templates/_rcm_compat.not'))
        self.assertEqual(library.templates[0].encode(),self.key.encode())
        self.assertEqual((folder/'codex/R_rcm_showcase_s1_Passive.class').read_bytes(),b'fixture-bytecode')

    def test_shared_deploy_unions_startup_libraries_and_preserves_compat_on_redeploy(self):
        from rcm.deployment_many import deploy_many
        self.donor();self.profile.write_bytes(self.saved)
        for ident in ('tutorial','mini'):
            self.ws.write('build/'+ident+'/bundle/'+ident+'.nob',self.empty_nob)
            self.ws.write('build/'+ident+'/build_report.json',json.dumps(dict(status='compiled-unverified-in-game',distribution_files={ident+'.nob':dict(sha256=hashlib.sha256(self.empty_nob).hexdigest())})))
        with patch('rcm.deployment_many.game_running',return_value=False):
            deploy_many(self.ws,['tutorial','mini'],'east_demo')
            deploy_many(self.ws,['tutorial'],'east_demo',preserve_siblings=True)
        folder=self.game/'RCM/east_demo';manifest=json.loads((folder/'.rcm_deployment.json').read_text())
        self.assertIn('rcm_compat.nob',manifest['files']);self.assertEqual(set(manifest['owners']),{'tutorial','mini'})
        self.assertTrue((folder/'rcm_compat.nob').is_file());self.assertEqual(self.profile.read_bytes(),self.saved)
        self.assertEqual(compatibility_files(self.game,[self.empty_nob,self.key_nob]),{})

    def test_nmf_only_library_does_not_count_as_startup_definition(self):
        self.donor();self.profile.write_bytes(self.saved)
        late=zip_bytes({'misc/templates/showcase.not':NotFile([self.key]).encode()})
        result=compatibility_files(self.game,late)
        with zipfile.ZipFile(io.BytesIO(result['rcm_compat.nob'])) as z:
            self.assertEqual(NotFile.read(z.read('misc/Templates/_rcm_compat.not')).templates[0].name,self.key.name)

    def test_missing_owned_definition_blocks_preparation_instead_of_ignoring_inventory(self):
        self.profile.write_bytes(self.saved)
        with self.assertRaisesRegex(ValueError,'r_rcm_showcase_s1_key'):compatibility_files(self.game,self.empty_nob)

    def test_modified_donor_cannot_be_adopted_and_running_game_cannot_be_updated(self):
        donor=self.donor();folder=self.installed('east_demo',{'rcm_tutor.nob':self.empty_nob});self.profile.write_bytes(self.saved)
        (donor/'rcm_showcase.nob').write_bytes(self.empty_nob)
        with patch('rcm.deployment.game_running',return_value=False):
            with self.assertRaises(ValueError):refresh_installed_profiles(self.ws)
        self.assertFalse((folder/'rcm_compat.nob').exists())
        with patch('rcm.deployment.game_running',return_value=True):
            with self.assertRaises(ValueError):refresh_installed_profiles(self.ws)
        self.assertEqual(self.profile.read_bytes(),self.saved)

    def test_explicit_single_destination_also_keeps_carried_item(self):
        from rcm.deployment import deploy
        self.donor();self.profile.write_bytes(self.saved)
        self.ws.write('build/tutorial/bundle/tutorial.nob',self.empty_nob)
        self.ws.write('build/tutorial/build_report.json',json.dumps(dict(status='compiled-unverified-in-game',distribution_files={'tutorial.nob':dict(sha256=hashlib.sha256(self.empty_nob).hexdigest())})))
        with patch('rcm.deployment.game_running',return_value=False):deploy(self.ws,'tutorial',directory='chosen')
        self.assertTrue((self.game/'RCM/chosen/rcm_compat.nob').is_file())
        self.assertEqual(self.profile.read_bytes(),self.saved)
