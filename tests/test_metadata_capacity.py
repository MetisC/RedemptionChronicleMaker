"""Regression for the native NMF CASH overwrite on mixed-map module load."""
from pathlib import Path
import sys,tempfile,unittest,zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'cache/vendor')]
from rcm.campaign_generator import merge_metadata
from rcm.output_validation import verify_output
from rcm.paths import Workspace


class CurrencyMetadataTests(unittest.TestCase):
    def test_mixed_original_maps_have_one_bounded_currency_table(self):
        lines=['NLS london.nls','CASH cashuk','NOT first.not','CASH cashus',
               'NLS mp_salon.nls','CASH GoldBag GoldCoins cashus cashuk']
        meta,profile=merge_metadata(lines)
        self.assertEqual([r for r in meta if r.startswith('CASH')],['CASH cashuk cashus GoldBag'])
        self.assertEqual(profile['omitted_templates'],['GoldCoins'])
        self.assertEqual([r for r in meta if not r.startswith('CASH')],
                         ['NLS london.nls','NOT first.not','NLS mp_salon.nls'])

    def test_case_variants_and_commas_do_not_append_native_slots(self):
        meta,profile=merge_metadata(['CASH cashuk','cash CASHUK, cashus','CASH cashus'])
        self.assertEqual(meta,['CASH cashuk cashus'])
        self.assertEqual(profile['omitted_templates'],[])

    def test_single_native_line_keeps_its_first_three_tokens(self):
        meta,profile=merge_metadata(['CASH GoldBag GoldCoins cashus cashuk'])
        self.assertEqual(meta,['CASH GoldBag GoldCoins cashus'])
        self.assertEqual(profile['templates'],['GoldBag','GoldCoins','cashus'])
        self.assertEqual(merge_metadata(['NLS london.nls'])[0],['NLS london.nls'])

    def test_output_gate_rejects_cumulative_cash_even_when_lines_are_short(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temporary:
            ws=Workspace(Path(temporary));target=ws.output('build/demo/demo.nob')
            target.parent.mkdir(parents=True)
            for text,valid in [('CASH cashuk\nCASH cashus\nCASH GoldBag GoldCoins cashus\n',False),
                               ('CASH cashuk\nCASH cashuk\nCASH cashuk\nCASH cashuk\n',False),
                               ('CASH cashuk cashus GoldBag\n',True),
                               ('CASH GoldBag GoldCoins cashus cashuk\n',True)]:
                with zipfile.ZipFile(target,'w') as archive:
                    archive.writestr('chronicles/test.nmf',text)
                if valid:verify_output(ws,{'chronicle':'demo'},{'entries':[]})
                else:
                    with self.assertRaisesRegex(ValueError,'CASH.*capacity'):
                        verify_output(ws,{'chronicle':'demo'},{'entries':[]})

    def test_showcase_build_merges_all_scene_metadata(self):
        import yaml
        from rcm.service import Backend
        from rcm.deployment import default_game
        data=yaml.safe_load((ROOT/'chronicles/showcase/project.yaml').read_text(encoding='utf8'))
        data['chronicle']['id']='cash_test'
        report=Backend(Workspace(ROOT,default_game(ROOT))).build(data,False)
        self.assertEqual(report['currency_profile']['templates'],['cashuk','cashus','GoldBag'])
        self.assertEqual(report['currency_profile']['omitted_templates'],['GoldCoins'])
        with zipfile.ZipFile(ROOT/'build/cash_test/cash_test.nob') as archive:
            meta=archive.read('chronicles/R_cash_test.nmf').decode('cp1252')
        self.assertEqual([r for r in meta.splitlines() if r.startswith('CASH')],
                         ['CASH cashuk cashus GoldBag'])
