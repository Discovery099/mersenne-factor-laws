import gzip
import itertools
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from laws import L001, L003
from mf import forecast, power
from mf.checker import primes_upto
from mf.null_n0 import weight as n0
from laws.L002 import weight as l002
from mf.predict import expectations
from mf import preregister_vault, forecast_design, vault_score


class PowerTests(unittest.TestCase):
    def test_expected_gain_against_enumerated_poisson(self):
        # Explicit expectation over outcomes, independent of the KL shortcut.
        a, b = 2.5, 4.0
        def d(y, mu):
            return 2*(mu-y+(y*math.log(y/mu) if y else 0))
        expected = sum(math.exp(-a)*a**y/math.factorial(y)*(d(y,b)-d(y,a)) for y in range(70))
        self.assertAlmostEqual(power.expected_deviance_gain(a,b), expected, places=13)
        self.assertGreater(power.expected_deviance_gain(336.9,335.9), 0)
        self.assertLess(power.expected_deviance_gain(336.9,335.9), .004)

    def test_gate_both_directions_and_bad_inputs(self):
        self.assertEqual(power.expected_deviance_gain(0,0),0)
        self.assertEqual(power.expected_deviance_gain(0,2),4)
        self.assertTrue(math.isinf(power.expected_deviance_gain(2,0)))
        for a,b in [(-1,2),(1,float('nan')),(float('inf'),1)]:
            with self.assertRaises(ValueError): power.expected_deviance_gain(a,b)
        report = power.matrix({'A': {'t':10.}, 'B': {'t':30.}}, ['t'])
        power.require_power(report)
        with self.assertRaisesRegex(ValueError,'underpowered'):
            power.require_power(power.matrix({'A': {'t':335.9}, 'B': {'t':336.9}}, ['t']))
        with self.assertRaises(ValueError): power.comparison({'a':1},{'a':2},['a','a'])

    def test_json_order_does_not_change_contrasts(self):
        models={'N0':{'x':10.},'L001':{'x':20.},'L002':{'x':30.},'L003':{'x':40.}}
        self.assertEqual(power.matrix(models,['x']),power.matrix(json.loads(json.dumps(models,sort_keys=True)),['x']))

    def test_underpowered_registration_writes_nothing(self):
        with tempfile.TemporaryDirectory(dir=forecast.ROOT/'build') as td:
            path=Path(td)/'forecast.json'; path.write_text('{}')
            output=Path(td)/'registration.json'
            failed=power.matrix({'N0':{'x':335.9},'L002':{'x':336.9}},['x'])
            with patch.object(preregister_vault,'verify_forecast',return_value=failed):
                with self.assertRaisesRegex(ValueError,'underpowered'):
                    preregister_vault.create(path,output)
            self.assertFalse(output.exists())


class L003Tests(unittest.TestCase):
    def test_full_outcome_space(self):
        probs = [.03,.17,.22,.41]
        exact = [0.]*(len(probs)+1)
        for bits in itertools.product((0,1), repeat=len(probs)):
            exact[sum(bits)] += math.prod(w if b else 1-w for w,b in zip(probs,bits))
        actual = L003.distribution(probs,len(probs))
        np.testing.assert_allclose(actual,exact,rtol=2e-15,atol=1e-16)
        mean = sum(j*v for j,v in enumerate(actual))
        variance = sum((j-mean)**2*v for j,v in enumerate(actual))
        self.assertAlmostEqual(mean,sum(probs))
        self.assertAlmostEqual(variance,sum(w*(1-w) for w in probs))
        self.assertEqual(L003.FITTED_PARAMETERS,0)
        self.assertLessEqual(len(gzip.compress(Path(L003.__file__).read_bytes(),mtime=0)),2000)

    def test_weights_same_as_L001_and_validation(self):
        for p in (1001,1013,10000019):
            for k in (1,2,3,4,30,105,997,10000):
                self.assertAlmostEqual(L001.weight(p,k),L003.weight(p,k),places=15)
        for w in (-.1,1,float('nan')):
            with self.assertRaises(ValueError): L003.distribution([w])


class ForecastTests(unittest.TestCase):
    def test_union_maximum_uses_distribution_not_addition(self):
        with tempfile.TemporaryDirectory(dir=forecast.ROOT/'build') as td:
            paths=[]; means=[np.array([.3,.5]),np.array([.7])]
            for i,mu in enumerate(means):
                cells,audit=forecast.poisson_summary(mu)
                models={name:cells for name in ('N0','L001','L002','L003')}
                part={'schema':'prospective-power-v1','census_computed':False,'sources':{},
                      'bounds':[1001+100*i,1100+100*i,1],'models':models,'exponents':len(mu),
                      'score_cells':{'multiplicity':power.multiplicity_cells(),'descriptive_composite':power.multiplicity_cells()},
                      'numerics':{'native':{'N0':audit,'L002':audit},'smooth':{'L001':audit,'L003':audit}}}
                p=Path(td)/f'part{i}.json';p.write_text(json.dumps(part));paths.append(p)
            output=Path(td)/'union.json'
            forecast_design.combine(paths,output)
            combined=json.loads(output.read_text())
            union,_=forecast.poisson_summary(np.concatenate(means))
            self.assertAlmostEqual(combined['models']['L003']['maximum'],union['maximum'],places=13)
            self.assertLess(union['maximum'],sum(forecast.poisson_summary(m)[0]['maximum'] for m in means))
            bad=json.loads(paths[1].read_text());bad['bounds'][0]-=1;paths[1].write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'disjoint'):
                forecast_design.combine(paths,Path(td)/'bad.json')

    def test_operator_scorer_does_not_promote_underpowered_comparison(self):
        models={'N0':{'maximum':1.},'L002':{'maximum':1.01}}
        pred={'models':models,'score_cells':{'multiplicity':['maximum']},
              'power':{'multiplicity':power.matrix(models,['maximum'])}}
        result=vault_score.score({'maximum':10000},pred)
        row=result['scores']['multiplicity']['comparisons']['N0_vs_L002']
        self.assertLess(row['gain_for_first_law'],-14)
        self.assertFalse(row['second_law_wins'])
        self.assertFalse(result['operator_hash_confirmation'])
        with self.assertRaises(ValueError): vault_score.score({'maximum':-1},pred)

    def test_native_against_scalar_and_resume_integrity(self):
        bounds = (1001,1200,100)
        with tempfile.TemporaryDirectory(dir=forecast.ROOT/'build') as td:
            ps, models, audit = forecast.native_forecast(bounds,Path(td),.05,1000)
            self.assertEqual(ps.tolist(),[p for p in primes_upto(1200) if p>=1001])
            for name,weight in (('N0',n0),('L002',l002)):
                expected = expectations(bounds,weight)
                for cell,value in expected['cells'].items():
                    self.assertAlmostEqual(models[name][cell],value,places=11)
                self.assertAlmostEqual(models[name]['maximum'],expected['expected_max_factors'],places=10)
            ps2, models2, _ = forecast.native_forecast(bounds,Path(td),.05,1000)
            self.assertEqual(models,models2)
            path = next(Path(td).glob('*.means.csv'))
            with path.open('ab') as f: f.write(b'\n')
            with self.assertRaisesRegex(ValueError,'artifact mismatch'):
                forecast.native_forecast(bounds,Path(td),.05,1000)

    def test_smooth_and_maximum_against_direct_coefficients(self):
        bounds = (1001,1200,100)
        ps = np.array([p for p in primes_upto(1200) if p>=1001])
        models,audit = forecast.smooth_models(ps,100,bounds)
        direct = expectations(bounds,L001.weight)
        for cell,value in direct['cells'].items():
            self.assertAlmostEqual(models['L001'][cell],value,places=11)
        masses = np.array([L003.multiplicity(int(p),100) for p in ps])
        # Independent product-of-CDF formulation is stable for this small case.
        cdf = np.cumsum(masses,axis=1)
        maximum = float(np.sum(1-np.prod(cdf,axis=0)))
        self.assertAlmostEqual(models['L003']['maximum'],maximum,places=10)
        self.assertAlmostEqual(models['L003']['at_least_one'],float((1-masses[:,0]).sum()),places=11)
        self.assertAlmostEqual(models['L003']['at_least_two'],float((1-masses[:,0]-masses[:,1]).sum()),places=11)
        self.assertLess(audit['direct_sample_max_absolute_error'],1e-11)


if __name__ == '__main__': unittest.main()
