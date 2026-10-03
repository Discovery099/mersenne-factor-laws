import unittest
import copy
import json
import tempfile
from pathlib import Path
from mf.protocol import ROOT, digest
from ops.vault_report import recount_cells, operator_review


class VaultReportTests(unittest.TestCase):
    def test_independent_recount(self):
        cells=recount_cells([(11,1),(11,4),(23,1)],8)
        self.assertEqual([cells[c] for c in ('total','at_least_one','at_least_two','maximum')],[3,2,1,2])
        self.assertEqual(cells['dyadic:0'],2)
        self.assertEqual(cells['dyadic:2'],1)
        self.assertEqual(cells['residue:4:1'],2)
        self.assertEqual(cells['residue:4:0'],1)
        self.assertEqual(recount_cells([],8)['maximum'],0)
        with self.assertRaises(ValueError): recount_cells([(11,9)],8)

    def test_operator_confirmation_is_bound_to_exact_artifacts(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            source=Path(tmp)/'source.md';source.write_text('Synthetic operator attestation',encoding='utf-8')
            path=Path(tmp)/'review.json'
            region={'output':{'bounds':[11,23,4],'sha256':'a'*64},
                    'observed':{'total':3,'at_least_one':2,'at_least_two':1,'maximum':2}}
            record={'schema':1,'kind':'user-relayed-external-operator-attestation',
                    'source_path':str(source.relative_to(ROOT)),'source_sha256':digest(source),
                    'bounds':[11,23,4],'reference_census_sha256':'a'*64,'prediction_sha256':'b'*64,
                    'confirmed_cells':region['observed'],'operator_reports_exact_hash_match':True,
                    'external_prediction_receipt_before_computation':False}
            self.assertIsNone(operator_review(path,region,'b'*64))
            path.write_text(json.dumps(record))
            self.assertFalse(operator_review(path,region,'b'*64)['attestation']['external_prediction_receipt_before_computation'])
            for key,value in [('bounds',[11,29,4]),('reference_census_sha256','c'*64),
                              ('confirmed_cells',{**region['observed'],'total':4}),
                              ('prediction_sha256','c'*64),('operator_reports_exact_hash_match',False)]:
                with self.subTest(key=key):
                    bad=copy.deepcopy(record);bad[key]=value;path.write_text(json.dumps(bad))
                    with self.assertRaises(ValueError): operator_review(path,region,'b'*64)
            path.write_text(json.dumps(record));source.write_text('Changed source')
            with self.assertRaises(ValueError): operator_review(path,region,'b'*64)


if __name__=='__main__': unittest.main()
