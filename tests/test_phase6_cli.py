"""Public commands exercised in process, so their errors and coverage are visible."""
from pathlib import Path
import contextlib,io,json,tempfile,unittest
from unittest.mock import patch
from rcm.cli import main
ROOT=Path(__file__).resolve().parents[1]

class Phase6CliTests(unittest.TestCase):
    def command(self,*args):
        out=io.StringIO();error=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(error):code=main(['--workspace',str(ROOT),*args])
        return code,out.getvalue(),error.getvalue()
    def test_validate_campaign_lists_all_levels(self):
        code,out,err=self.command('validate','chronicles/system_test/project.yaml');self.assertEqual(code,0,err);self.assertEqual(json.loads(out)['levels'],['EastLondon','WestLondon'])
    def test_invalid_yaml_error_is_concise(self):
        path=ROOT/'build/tests/cli_bad.yaml';path.write_text('chronicle: [bad',encoding='utf8');code,out,err=self.command('validate',str(path));self.assertEqual(code,1);self.assertIn('YAML',err);self.assertNotIn('Traceback',err)
    def test_corrupt_package_is_concise(self):
        path=ROOT/'build/tests/cli_bad.rcmpack';path.write_bytes(b'bad');code,out,err=self.command('inspect-package',str(path));self.assertEqual(code,1);self.assertIn('corrupto',err);self.assertNotIn('Traceback',err)
    def test_export_import_commands_roundtrip(self):
        path=ROOT/'build/tests/cli_export.rcmproject';code,out,err=self.command('export-project','chronicles/system_test/project.yaml',str(path));self.assertEqual(code,0,err)
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as tmp:
            code,out,err=self.command('import-project',str(path),tmp);self.assertEqual(code,0,err);self.assertTrue(Path(json.loads(out)['project']).exists())
    def test_diagnostics_and_clean_commands(self):
        code,out,err=self.command('diagnostics');self.assertEqual(code,0,err);self.assertFalse(json.loads(out)['native_engine_test'])
        code,out,err=self.command('clean','nonexistent');self.assertEqual(code,0,err);self.assertEqual(json.loads(out)['removed'],[])
    def test_build_failure_invalidates_known_id(self):
        from rcm.service import source_text
        from phase6_fixtures import system_source
        from rcm.paths import Workspace
        root=system_source(Workspace(ROOT));root['chronicle']['id']='p6_clifail';root['scenes'][0]['actors'][0]['template']='missing';path=ROOT/'build/tests/cli_failed.yaml';path.write_text(source_text(root),encoding='utf8')
        code,out,err=self.command('build',str(path));self.assertEqual(code,1);self.assertEqual(json.loads((ROOT/'build/p6_clifail/build_report.json').read_text())['status'],'failed')
    def test_package_install_and_uninstall_commands_use_backend(self):
        with patch('rcm.packages.install_package',return_value={'id':'test'}) as install:
            code,out,err=self.command('install-package','fixture.rcmpack','--accept-custom-code');self.assertEqual(code,0,err);self.assertTrue(install.call_args.args[2])
        with patch('rcm.packages.uninstall_package',return_value={'removed':[]}) as uninstall:
            code,out,err=self.command('uninstall-package','test');self.assertEqual(code,0,err);self.assertEqual(uninstall.call_args.args[1],'test')
