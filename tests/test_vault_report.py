import unittest
from ops.vault_report import recount_cells


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


if __name__=='__main__': unittest.main()
