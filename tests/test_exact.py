import hashlib
import json
from math import gcd
from pathlib import Path
import random
import subprocess
import sys
import unittest
import tempfile
import shutil
import os
import checker_reference as ref
from mf import checker as c
from mf.stats import summary
from ops.common import execute_engine, executable, second_checker
from mf.protocol import ROOT
import oracle


class ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, _ = execute_engine("census_kp", (3, 200, 10000))
        cls.pairs = c.parse_census(cls.raw)

    def test_reference_bytes_and_stdout(self):
        self.assertEqual(hashlib.sha256((ROOT / "checker_reference.py").read_bytes()).hexdigest(), "afc67c6ab6610c94577a82bef095817ab746baa76d6db62df4651741211514bc")
        actual = subprocess.check_output([sys.executable, "checker_reference.py"], cwd=ROOT).decode().replace("\r\n", "\n")
        expected = (ROOT / "tests/reference_expected.txt").read_text()
        self.assertEqual(actual, expected)

    def test_reference_census_and_two_independent_engines(self):
        other, _ = execute_engine("census_pk", (3, 200, 10000))
        self.assertEqual(c.census_hash(self.pairs), c.census_hash(c.parse_census(other)))
        self.assertEqual(len(self.pairs), 46)
        self.assertTrue(c.census_hash(self.pairs).startswith("4c37caf1201fe83d"))
        self.assertEqual(self.pairs, ref.census(3, 200, 10000))
        self.assertEqual(second_checker(self.pairs), 46)

    def test_division_oracle(self):
        self.assertEqual(sorted(oracle.census(3, 200, 10000)), self.pairs)

    def test_medium_regression(self):
        a, _ = execute_engine("census_kp", (1000, 3000, 20000))
        b, _ = execute_engine("census_pk", (1000, 3000, 20000))
        self.assertEqual(c.census_hash(c.parse_census(a)), c.census_hash(c.parse_census(b)))
        self.assertEqual(len(c.parse_census(a)), 215)

    def test_small_prime_sieve_exceptions_and_empty_ranges(self):
        for bounds in ((0, 2, 10), (3, 3, 1), (5, 5, 3), (11, 11, 4), (14, 16, 7), (0, 0, 1)):
            a, _ = execute_engine("census_kp", bounds)
            b, _ = execute_engine("census_pk", bounds)
            expected = ref.census(*bounds)
            self.assertEqual(c.parse_census(a), expected)
            self.assertEqual(c.parse_census(b), expected)

    def test_random_engine_ranges_and_cache_contamination(self):
        rng = random.Random(12002)
        for _ in range(20):
            lo = rng.randrange(3, 300)
            bounds = lo, lo + rng.randrange(1, 50), rng.randrange(1, 600)
            expected = ref.census(*bounds)
            for name in ("census_kp", "census_pk"):
                raw, _ = execute_engine(name, bounds)
                self.assertEqual(c.parse_census(raw), expected)

    def test_random_10000_claims_reference_and_C(self):
        rng = random.Random(12)
        cases = []
        for i in range(10000):
            p, k = rng.choice(self.pairs)
            q = 2*p*k + 1
            mode = i % 5
            if mode == 1:
                q += rng.choice((-2, 2))
            elif mode == 2:
                p = rng.randrange(0, 1000)
            elif mode == 3:
                p, q = 11, 2047
            elif mode == 4:
                p, q = rng.randrange(0, 1000), rng.randrange(0, 10000000)
            cases.append((p, q))
        raw = "".join(f"{p} {q}\n" for p, q in cases).encode()
        batch = subprocess.run([str(executable("checker2")), "--batch"], input=raw, capture_output=True)
        answers = [json.loads(line)["valid"] for line in batch.stdout.splitlines()]
        self.assertEqual(len(answers), 10000)
        for (p, q), second in zip(cases, answers):
            first = c.verify_factor(p, q)["valid"]
            self.assertEqual(first, second, (p, q))
            self.assertEqual(first, ref.verify_factor(p, q)[0], (p, q))

    def test_mutations(self):
        cases = []
        for p, k in self.pairs:
            q = 2*p*k+1
            next_p = p+2
            while not c.is_prime(next_p):
                next_p += 2
            for pp, qq in ((p, q-2), (p, q+2), (next_p, q)):
                self.assertFalse(c.verify_factor(pp, qq)["valid"])
                cases.append(f"{pp} {qq}\n")
        out = subprocess.run([str(executable("checker2")), "--batch"], input="".join(cases).encode(), capture_output=True)
        self.assertTrue(all(not json.loads(line)["valid"] for line in out.stdout.splitlines()))

    def test_mr_bound_correction(self):
        pseudoprime = 318665857834031151167461
        self.assertTrue(ref.is_prime_mr(pseudoprime))
        self.assertFalse(c.is_prime(pseudoprime))
        self.assertFalse(c.is_prime(c.MR_LIMIT))
        for n in range(1000):
            self.assertEqual(c.is_prime(n), oracle.trial_prime(n))

    def test_pocklington_above_mr_limit_and_corruptions(self):
        p, q = 89, 2**89 - 1
        factors = [2, 3, 5, 17, 23, 89, 353, 397, 683, 2113, 2931542417]
        F = 1
        for r in factors:
            F *= r
        self.assertEqual(F, q-1)
        cert = []
        for r in factors:
            a = next(a for a in range(2, 1000) if pow(a,q-1,q)==1 and gcd(pow(a,(q-1)//r,q)-1,q)==1)
            cert.append([r,1,a])
        self.assertFalse(c.verify_factor(p,q)["valid"])
        self.assertTrue(c.verify_factor(p,q,cert)["valid"])
        good = subprocess.run([str(executable("checker2")), str(p), str(q), *[":".join(map(str,x)) for x in cert]], capture_output=True)
        self.assertEqual(good.returncode,0,good.stdout)
        mutations = [cert[:-1], cert + [cert[0]], [[r,0,a] if i==0 else [r,e,a] for i,(r,e,a) in enumerate(cert)], [[r,e,1] if i==0 else [r,e,a] for i,(r,e,a) in enumerate(cert)]]
        # Dropping the largest factor still leaves F>sqrt(n), so use a genuinely insufficient F.
        mutations[0] = cert[:2]
        for bad in mutations:
            self.assertFalse(c.verify_factor(p,q,bad)["valid"])
            result = subprocess.run([str(executable("checker2")),str(p),str(q),*[":".join(map(str,x)) for x in bad]],capture_output=True)
            self.assertNotEqual(result.returncode,0)
        self.assertFalse(c.verify_factor(11,89,[[2,3,2],[11,1,3]])["valid"])

    def test_invalid_inputs_and_duplicate_census(self):
        for raw in (b"11 4\n11 4\n",b"11 -1\n",b"11 0\n",b"11 4 5\n",b"1.0 3\n"):
            with self.assertRaises(ValueError):
                c.parse_census(raw)
        self.assertFalse(c.verify_factor(True, 7)["valid"])
        for name in ("census_kp", "census_pk"):
            result = subprocess.run([str(executable(name)), "-1", "200", "10000"],capture_output=True)
            self.assertNotEqual(result.returncode,0)
        with self.assertRaises(ValueError):
            c.verify_census([(11, 4)], (3, 7, 4))

    def test_exact_statistics(self):
        s = summary(self.pairs,3,200,10000)
        self.assertEqual(sum(s["dyadic"].values()),46)
        self.assertEqual(sum(v["count"] for v in s["valuations"].values()),46)
        self.assertEqual(sum(s["smoothness"].values()),46)
        self.assertEqual(sum(s["multiplicity"].values()),45)
        for counts in s["residues"].values():
            self.assertEqual(sum(counts),46)
        self.assertEqual(summary([],3,7,1)["multiplicity"],{"0":3})

    def test_montgomery_near_signed64_limit(self):
        rng=random.Random(1264)
        cases=[(2,127,2**63-1),(2**64-1,2**64-1,2**63-25),(0,0,3)]
        cases += [(rng.randrange(2**64),rng.randrange(2**64),(rng.randrange(3,2**63)//2)*2+1) for _ in range(1000)]
        with tempfile.TemporaryDirectory() as td:
            binary=Path(td)/("probe.exe" if os.name=="nt" else "probe")
            cc=os.environ.get("CC") or shutil.which("gcc") or shutil.which("clang")
            subprocess.run([cc,"-O2","-std=c11",str(ROOT/"tests/montgomery_probe.c"),"-o",str(binary)],check=True,capture_output=True)
            payload="".join(f"{a} {e} {n}\n" for a,e,n in cases).encode()
            out=subprocess.check_output([str(binary)],input=payload)
            self.assertEqual(list(map(int,out.splitlines())),[pow(a,e,n) for a,e,n in cases])
