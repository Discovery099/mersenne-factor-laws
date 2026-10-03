import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from mf.protocol import ROOT, digest
from ops.common import executable
from ops import vault_run


class VaultRunTests(unittest.TestCase):
    def test_plan_preserves_sealed_boundary(self):
        regions=[[10000001,20000000,10000],[20000001,30000000,10000]]
        chunks=vault_run.plan(regions,600000)
        self.assertEqual(chunks[0][0],10000001)
        self.assertEqual(chunks[-1][1],30000000)
        self.assertEqual(sum(b-a+1 for a,b,k in chunks),20000000)
        self.assertTrue(all(not (a<=20000000<b) for a,b,k in chunks))
        for left,right in zip(chunks,chunks[1:]): self.assertEqual(left[1]+1,right[0])
        with self.assertRaises(ValueError): vault_run.plan([[10,20,10],[20,30,10]],5)

    def test_real_engines_checkers_and_checkpoint_mutation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as td:
            work=Path(td); bounds=[1001,1030,100]
            binaries={n:digest(executable(n)) for n in vault_run.ENGINES}
            results=[vault_run.engine_part(work,bounds,n,binaries,time.monotonic()+90) for n in vault_run.ENGINES]
            record=vault_run.verify_part(work,bounds,results)
            self.assertEqual(record['sha256'],results[0][0]['sha256'])
            self.assertEqual(record['count'],record['C_checker_accepted'])
            with patch.object(vault_run,'execute_engine',side_effect=AssertionError('resume recomputed a completed engine')):
                resumed=vault_run.engine_part(work,bounds,vault_run.ENGINES[0],binaries,time.monotonic()+30)
            self.assertEqual(resumed[0],results[0][0])
            results[0][1].write_bytes(results[0][1].read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'saved engine part changed'):
                vault_run.engine_part(work,bounds,vault_run.ENGINES[0],binaries,time.monotonic()+30)

    def test_timeout_saves_no_false_success(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as td:
            with self.assertRaises(subprocess.TimeoutExpired):
                vault_run.engine_part(Path(td),[3,5,10],'census_kp',{},time.monotonic()-1)
            self.assertEqual(list(Path(td).iterdir()),[])

    def test_disagreement_is_fatal(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as td:
            a=Path(td)/'a';b=Path(td)/'b';a.write_bytes(b'');b.write_bytes(b'3 1\n')
            with self.assertRaisesRegex(ValueError,'disagree'):
                vault_run.verify_part(Path(td),[3,5,10],[({'sha256':digest(a)},a),({'sha256':digest(b)},b)])


if __name__=='__main__': unittest.main()
