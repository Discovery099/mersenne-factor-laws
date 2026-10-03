from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import tempfile
import unittest
from mf.null_n0 import weight, SMALL_PRIMES
from mf.predict import expectations, load_law
from mf.protocol import ROOT, write_once, registered
from mf.score import poisson_deviance, score_cells
from mf.track0.valuations import histogram
from mf.track0.sieves import direct, sieve, project_cache
from mf.track0.forests import enumerate_forests, verify
from discovery.plan import allocate, matched_ab
from mf.constants import enclose
from decimal import Decimal


class ModelTests(unittest.TestCase):
    def test_literal_null_and_log_deviance(self):
        self.assertEqual(weight(11,1),0)
        self.assertEqual(weight(11,2),0)
        p,k=101,4
        q=2*p*k+1
        expected=math.prod((0 if q%r==0 else r/(r-1)) for r in SMALL_PRIMES)/(k*math.log(q))
        self.assertAlmostEqual(weight(p,k),expected,14)
        self.assertEqual(poisson_deviance(0,2),4)
        self.assertEqual(poisson_deviance(3,3),0)
        self.assertEqual(poisson_deviance(3,0),math.inf)
        pred={"null":{"cells":{"a":2.0,"b":3.0}},"law":{"cells":{"a":1.0,"b":4.0}}}
        score=score_cells({"a":0,"b":3},pred)
        self.assertEqual(score["deviance"]["null"],4.0)
        self.assertAlmostEqual(score["deviance"]["law"],2+2*(4-3+3*math.log(3/4)))
        self.assertFalse(score["threshold_met"])
        with self.assertRaises(ValueError):
            score_cells({"a":0},pred)

    def test_law_constraints_and_prediction_totals(self):
        law=load_law(ROOT/"laws/L001.py")
        value=expectations((100,200,100),law.weight)
        total=value["cells"]["total"]
        self.assertAlmostEqual(total,sum(v for k,v in value["cells"].items() if k.startswith("dyadic:")),10)
        self.assertGreaterEqual(value["expected_max_factors"],0)

    def test_write_once_and_uncommitted_predictions_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/"runs") as tmp:
            path=Path(tmp)/"prediction.json"
            write_once(path,b"{}");
            with self.assertRaises(FileExistsError):
                write_once(path,b"changed")
            with self.assertRaises((ValueError,KeyError)):
                registered(path)

    def test_track0_histograms_R60(self):
        x=([(2,0)],[(1,0),(1,0)])
        y=([(3,0)],[(1,0),(1,0),(1,0)])
        a=histogram(60,x,y)
        b=histogram(60,x,y,method="legendre")
        self.assertEqual(a,b)
        self.assertEqual(sum(cell["count"] for cell in a.values()),61)
        self.assertEqual(a[(0,0)]["min_n"],0)

    def test_track0_sieve_N200_and_projection_contamination(self):
        exclusions=[(3,1),(6,1),(5,0),(7,6),(12,7)]
        self.assertEqual(direct(200,exclusions),sieve(200,exclusions))
        entries={0:{True},1:{False,True},2:{False}}
        value=project_cache(3,12,entries,[i%3 for i in range(12)])
        self.assertEqual(set(value["ambiguity_classes"]),{1,4,7,10})
        with self.assertRaises(ValueError):
            project_cache(3,12,entries,[(i+1)%3 for i in range(12)])

    def test_track0_forests_eight_queries_and_mutations(self):
        queries=[2,4,8,16,32,64,128,256]
        result=enumerate_forests(queries,8)
        self.assertEqual(result["parent_maps_checked"],40320)
        best=result["best"]
        self.assertEqual(verify(queries,best["parents"],best["leaves"],8),(1,0))
        bad=[list(x) for x in best["leaves"]]
        bad[-1][0]=3
        self.assertIsNone(verify(queries,best["parents"],bad,8))
        self.assertIsNone(verify([2,2],[1,0],[[],[]],2))

    def test_discovery_assignment_budget_and_matching(self):
        expiry=(datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
        rows=[{"assignment_id":str(p),"p":p,"account":"operator","status":"assigned","source":"test","expires_at":expiry,
               "method":"pm1","completed_B1":100,"completed_B2":1000} for p in (101,103,107,109)]
        candidates=[{"assignment_id":str(r["p"]),"method":"pm1","B1":1000,"B2":10000,"cpu_seconds":100,
                     "expected_new_factors":1,"selection_model":"pm1-smoothness","prediction_source_sha256":"a"*64} for r in rows]
        self.assertEqual(len(allocate(rows,candidates,"operator",200/3600)["selected"]),2)
        with self.assertRaises(ValueError):
            allocate(rows,candidates,"someone-else",1)
        self.assertEqual(matched_ab(rows,12),matched_ab(rows,12))
        self.assertEqual(len(matched_ab(rows,12)["pairs"]),2)

    def test_directed_constant_enclosure(self):
        a=enclose(100)
        b=enclose(1000)
        self.assertLess(Decimal(a["C2_interval"][0]),Decimal(b["C2_interval"][0]))
        self.assertGreater(Decimal(a["C2_interval"][1]),Decimal(b["C2_interval"][1]))
        self.assertLess(Decimal(b["C2_interval"][0]),Decimal('0.6601618158468696'))
        self.assertGreater(Decimal(b["C2_interval"][1]),Decimal('0.6601618158468696'))
