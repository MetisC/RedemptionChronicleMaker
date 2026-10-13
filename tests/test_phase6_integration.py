from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
from rcm.paths import Workspace
from rcm.service import Backend
from rcm.campaign_document import CampaignDocument
from rcm.safe_edit import delete_candidate
from rcm.packages import export_project,import_project,create_package,inspect_package
from rcm.startup import settings,cache_errors,prepare_workspace,reset_settings
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from campaign_fixture_helpers import system_source,large_source


class Phase6IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ws=Workspace(ROOT);cls.backend=Backend(cls.ws)
    def source(self):return system_source(self.ws)
    def test_end_to_end_build_package_determinism_and_export_import(self):
        root=self.source();root['chronicle']['id']='p6_e2e';root['metadata']['dependencies']=[]
        first=self.backend.build(root);path=self.ws.output('build/p6_e2e/p6_e2e_distribution.zip');data=path.read_bytes();second=self.backend.build(root)
        self.assertEqual(path.read_bytes(),data);self.assertEqual(first['class_versions'],second['class_versions']);self.assertGreater(first['format_validation']['conversations'],0)
        archive=self.ws.output('build/tests/p6_e2e.rcmpack');m=create_package(self.ws,'p6_e2e',archive);self.assertTrue(m['custom_code']);inspect_package(archive)
        sourcezip=export_project(self.ws,root,'build/tests/e2e.rcmproject')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            imported=import_project(self.ws,sourcezip,tmp);self.assertTrue(self.backend.validate(imported.snapshot()).valid);self.assertTrue((Path(tmp)/'IMPORTED_CODE_NOTICE.txt').is_file());self.backend.build(imported.snapshot());self.assertEqual(path.read_bytes(),data)
    def test_invalid_build_invalidates_previous_distribution(self):
        root=self.source();root['chronicle']['id']='p6_failure';self.backend.build(root);previous=self.ws.output('build/p6_failure/p6_failure.nob').read_bytes();root['scenes'][0]['actors'][0]['template']='missing'
        with self.assertRaises(ValueError):self.backend.build(root)
        self.assertEqual(json.loads(self.ws.output('build/p6_failure/build_report.json').read_text())['status'],'failed');self.assertEqual(self.ws.output('build/p6_failure/p6_failure.nob').read_bytes(),previous)
        with self.assertRaises(ValueError):create_package(self.ws,'p6_failure','build/tests/failed.rcmpack')
    def test_publish_failure_does_not_publish_partial_build(self):
        root=self.source();root['chronicle']['id']='p6_atomic';self.backend.build(root);path=self.ws.output('build/p6_atomic/p6_atomic.nob');old=path.read_bytes();root['chronicle']['name']='Cambio'
        from rcm.file_transaction import os
        original=os.replace
        def fail(src,dest):
            if dest==path:raise OSError('injected publication failure')
            return original(src,dest)
        with patch('rcm.file_transaction.os.replace',side_effect=fail),self.assertRaises(OSError):self.backend.build(root)
        self.assertEqual(path.read_bytes(),old);self.assertEqual(json.loads(self.ws.output('build/p6_atomic/build_report.json').read_text())['status'],'failed');self.assertFalse(list(self.ws.output('build/.staging').iterdir()))
    def test_safe_delete_entry_actor_inventory_and_quest(self):
        doc=CampaignDocument(self.ws,self.source());before=doc.snapshot()
        for path in [('scenes',0),('scenes',0,'actors',0),('quests',0)]:
            with self.assertRaises(ValueError):delete_candidate(doc,path,self.backend)
            self.assertEqual(doc.snapshot(),before)
        doc.campaign['scenes'][1]['events'].append({'id':'unused','when':'timer','seconds':1,'actions':[{'reward_xp':1}]});candidate=delete_candidate(doc,('scenes',1,'events',len(doc.campaign['scenes'][1]['events'])-1),self.backend);self.assertTrue(self.backend.validate(candidate).valid)
    def test_generated_java_namespace_collision_blocked(self):
        root=self.source();script=root['resources']['scripts'][0];script['id']='R_rcm_system_s0_Scene';script['source']='build/tests/R_rcm_system_s0_Scene.java';self.ws.write(script['source'],'public class '+script['id']+' extends Codex {}')
        result=self.backend.validate(root);self.assertFalse(result.valid);self.assertTrue(any('namespace' in p.message for p in result.problems))
    def test_own_file_edits_invalidate_build_fingerprint(self):
        from rcm.service import build_inputs_fingerprint,source_fingerprint
        root=self.source();original=build_inputs_fingerprint(self.ws,root);yamlhash=source_fingerprint(root);path=self.ws.output(root['resources']['scripts'][0]['source']);path.write_text(path.read_text()+'// changed bytes\n',encoding='utf8')
        self.assertEqual(source_fingerprint(root),yamlhash);self.assertNotEqual(build_inputs_fingerprint(self.ws,root),original)
    def test_save_contract_change_is_reported(self):
        root=self.source();root['chronicle']['id']='p6_contract';first=self.backend.build(root);second=self.backend.build(root);self.assertFalse(second['new_game_required']);self.assertEqual(first['save_schema_sha256'],second['save_schema_sha256'])
        root['state']['flags']['newflag']=12;third=self.backend.build(root);self.assertTrue(third['new_game_required']);self.assertNotEqual(first['save_schema_sha256'],third['save_schema_sha256'])
    def test_custom_compile_failure_retains_diagnostics(self):
        root=self.source();root['chronicle']['id']='p6_badjava';path=self.ws.write('build/tests/BrokenOwn.java','public class BrokenOwn extends Codex { not valid Java! }');root['resources']['scripts']=[{'id':'BrokenOwn','source':path.relative_to(ROOT).as_posix()}];root['resources']['templates'][0]['properties']['script']='BrokenOwn'
        with self.assertRaisesRegex(ValueError,'Diagnóstico'):self.backend.build(root)
        attempts=list(self.ws.output('build/failed_attempts').glob('p6_badjava_*'));self.assertTrue(attempts);self.assertTrue(any(list(p.rglob('custom_compiler.log')) for p in attempts))
    def test_startup_corrupt_settings_and_caches(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            ws=Workspace(Path(tmp));ws.write('cache/game_settings.json','bad');self.assertEqual(settings(ws),{});self.assertTrue(list(ws.output('research/startup').iterdir()));self.assertEqual(len(cache_errors(ws)),3)
            for name in ['levels','resources','scene_hints']:ws.write('cache/'+name+'.json','[]')
            self.assertEqual(len(cache_errors(ws)),3)
            self.assertTrue(reset_settings(ws));self.assertFalse(ws.output('cache/game_settings.json').exists())
    def test_loose_resource_catalogue_accepts_null_archive(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            ws=Workspace(Path(tmp))
            for name in ['levels','resources','scene_hints']:ws.write('cache/'+name+'.json',self.ws.output('cache/'+name+'.json').read_bytes())
            self.assertFalse(cache_errors(ws))
            data=json.loads(ws.output('cache/resources.json').read_text(encoding='utf8'));loose=next(e for e in data['entries'] if e['archive'] is None);loose['archive']=42;ws.write('cache/resources.json',json.dumps(data))
            self.assertTrue(any(e.startswith('resources:') for e in cache_errors(ws)))
    def test_first_run_fresh_cache_and_repair_from_read_only_game(self):
        game=Path(r'H:\GOG\Vampire The Masquerade - Redemption')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            ws=Workspace(Path(tmp),game);ws.write('cache/toolchain/ecj-3.26.0.jar',self.ws.output('cache/toolchain/ecj-3.26.0.jar').read_bytes());result=prepare_workspace(ws);self.assertTrue(result['cache_rebuilt']);self.assertFalse(cache_errors(ws));self.assertEqual(len(Backend(ws).levels),len(self.backend.levels))
            ws.write('cache/levels.json','bad');self.assertTrue(prepare_workspace(ws)['cache_rebuilt']);self.assertFalse(cache_errors(ws));self.assertTrue(list(ws.output('research/startup').glob('*_levels.json')))
    def test_large_fixture_counts_validation_and_real_compile(self):
        root=large_source(self.backend);self.assertEqual(len(root['scenes']),5);self.assertEqual(sum(len(s['actors']) for s in root['scenes']),100);self.assertEqual(sum(len(s['events']) for s in root['scenes']),100);self.assertEqual(sum(len(s['conversations']) for s in root['scenes']),50)
        result=self.backend.validate(root);self.assertTrue(result.valid,[p.message for p in result.problems]);report=self.backend.build(root);self.assertEqual(len(report['class_versions']),10);self.assertEqual(report['format_validation']['conversations'],50)
    def test_golden_build_matches_pinned_artifact_and_contract(self):
        import hashlib
        from rcm.document import Document
        self.source()  # Restore the fixture's known custom Java bytes.
        root=Document.load(self.ws,'tests/fixtures/chronicles/golden/project.yaml').snapshot();expected=json.loads(self.ws.output('tests/fixtures/chronicles/golden/expected.json').read_text(encoding='utf8'));report=self.backend.build(root)
        self.assertEqual(len(report['scenes']),expected['scenes']);self.assertFalse(report['geometry_in_package']);self.assertTrue(all(v==expected['class_version'] for v in report['class_versions'].values()))
        archive=self.ws.output('build/rcm_golden/rcm_golden_distribution.zip');self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),expected['distribution_sha256'],'Golden output changed: review generator changes and update the baseline explicitly after acceptance')
