"""Scalable, outcome-free forecasts. Does not call either census engine.

Native N0 exclusions are exact; L001/L003 use checked smooth interpolation.
The numerical settings are fixed independently of any census outcomes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from numpy.polynomial import chebyshev as ch

from laws import L001, L002, L003
from .power import matrix, multiplicity_cells
from .protocol import ROOT, atomic_json, digest, utcnow

DEGREE = 24
NODES = 24
CHECK_NODES = 32


def marginal_cells(byk):
    k = np.arange(1, len(byk)+1, dtype=np.int64)
    cells = {"total": float(np.sum(byk))}
    for j in range(len(byk).bit_length()):
        cells[f"dyadic:{j}"] = float(np.sum(byk[(k >= 2**j) & (k < 2**(j+1))]))
    for m in (3, 4, 5, 8, 12):
        for r in range(m):
            cells[f"residue:{m}:{r}"] = float(np.sum(byk[k % m == r]))
    return cells


def omitted_tail_bound(n, mu_max, degree=DEGREE):
    """Upper bound on omitted E[max] terms, for Poisson or Bernoulli sums.

    E[(X-degree)+] <= sum_{r=degree+1}^infty mu^r/r!.
    The geometric bound also bounds truncation in any individual survival.
    """
    if mu_max >= degree+2:
        raise ValueError("increase the fixed distribution degree before forecasting")
    return n * mu_max**(degree+1)/math.factorial(degree+1)/(1-mu_max/(degree+2))


def poisson_summary(mu):
    mass = np.empty((DEGREE+1, len(mu)))
    mass[0] = np.exp(-mu)
    for j in range(1, DEGREE+1):
        mass[j] = mass[j-1]*mu/j
    # Sum positive tails; 1-CDF loses precision when multiplied over many p.
    tails = np.cumsum(mass[:0:-1], axis=0)[::-1]
    logcdf = np.log1p(-np.minimum(tails, 1-np.finfo(float).eps)).sum(axis=1)
    return {"at_least_one": float(tails[0].sum()),
            "at_least_two": float(tails[1].sum()),
            "maximum": float((-np.expm1(logcdf)).sum())}, {
                "maximum_log_cdf": logcdf.tolist(),
                "omitted_tail_bound": omitted_tail_bound(len(mu), float(mu.max(initial=0))),
                "maximum_total_truncation_bound": (DEGREE+1)*omitted_tail_bound(len(mu), float(mu.max(initial=0)))}


def smooth_models(ps, K, bounds, nodes=NODES):
    lo, hi, _ = bounds
    k = np.arange(1, K+1, dtype=np.int64)
    a = np.array([L003.coefficient(int(t)) for t in k])
    center, half = (math.log(lo)+math.log(hi))/2, (math.log(hi)-math.log(lo))/2
    grid = np.cos(np.pi*(np.arange(nodes)+.5)/nodes)
    x = (np.log(ps)-center)/half if half else np.zeros(len(ps))
    byk = np.zeros(K)
    mu = np.zeros(len(ps))
    bernoulli = {"at_least_one": 0., "at_least_two": 0., "maximum": 0.}
    logcdf = np.zeros(DEGREE)
    error = 0.
    for c in (1, 3):
        sel = ps % 4 == c
        if not sel.any():
            continue
        ks = (k % 4 == 0) | (k % 4 == (3 if c == 1 else 1))
        weights = a[ks][None, :] / (np.log(2*k[ks])[None, :]+center+half*grid[:, None])
        if np.any(weights < 0) or np.any(weights >= 1):
            raise ValueError("L003 probability outside [0,1)")
        co = ch.chebfit(grid, weights, nodes-1)
        moments = ch.chebvander(x[sel], nodes-1).sum(axis=0)
        byk[ks] += moments @ co
        mu[sel] = ch.chebval(x[sel], co.sum(axis=1))
        mass = np.zeros((nodes, DEGREE+1)); mass[:, 0] = 1.
        for w in weights.T:
            mass[:, 1:] = mass[:, 1:]*(1-w[:, None]) + mass[:, :-1]*w[:, None]
            mass[:, 0] *= 1-w
        tails = np.cumsum(mass[:, :0:-1], axis=1)[:, ::-1]
        tc = ch.chebfit(grid, tails, nodes-1)
        for j in range(DEGREE):
            vals = ch.chebval(x[sel], tc[:, j])
            if vals.min(initial=0) < -1e-14 or vals.max(initial=0) > 1+1e-14:
                raise ValueError("invalid interpolated probability")
            vals = np.clip(vals, 0, 1-np.finfo(float).eps)
            if j == 0: bernoulli["at_least_one"] += float(vals.sum())
            if j == 1: bernoulli["at_least_two"] += float(vals.sum())
            logcdf[j] += np.log1p(-vals).sum()
        # Fixed, deterministic exponent samples validate away from nodes.
        sample = np.flatnonzero(sel)[np.linspace(0, sel.sum()-1, min(9, sel.sum()), dtype=int)]
        for i in sample:
            direct = np.array(L003.multiplicity(int(ps[i]), K, DEGREE))
            direct_tail = np.cumsum(direct[:0:-1])[::-1]
            interpolated = ch.chebval(x[i], tc)
            error = max(error, float(np.abs(direct_tail-interpolated).max()))
            direct_mu = math.fsum(L001.weight(int(ps[i]), int(t)) for t in k)
            error = max(error, abs(direct_mu-mu[i]))
    bernoulli["maximum"] = float((-np.expm1(logcdf)).sum())
    psummary, paudit = poisson_summary(mu)
    marginal = marginal_cells(byk)
    return {"L001": {**marginal, **psummary}, "L003": {**marginal, **bernoulli}}, {
        "nodes": nodes, "degree": DEGREE, "direct_sample_max_absolute_error": error,
        "L001": paudit, "L003": {"maximum_log_cdf": logcdf.tolist(),
        "omitted_tail_bound": omitted_tail_bound(len(ps), float(mu.max(initial=0))),
        "maximum_total_truncation_bound": (DEGREE+1)*omitted_tail_bound(len(ps), float(mu.max(initial=0)))}}


def native_forecast(bounds, work, hours=1., chunk=1_000_000):
    """Resume only hash-matching completed forecast chunks; bounded subprocesses."""
    lo, hi, K = bounds
    if not 3 <= lo <= hi <= 100_000_000 or not 1 <= K <= 1_000_000:
        raise ValueError("forecast bounds unsupported")
    if not math.isfinite(hours) or hours <= 0 or not 1 <= chunk <= 10_000_000:
        raise ValueError("invalid forecast budget or chunk size")
    work.mkdir(parents=True, exist_ok=True)
    exe = work.resolve() / ("forecast_n0.exe" if sys.platform == "win32" else "forecast_n0")
    exe.parent.mkdir(exist_ok=True)
    source = ROOT / "mf/forecast_n0.c"
    # Deterministic executable build (same flag supported by MinGW).
    command = ["gcc", "-O3", "-std=c11", str(source), "-o", str(exe), "-lm"]
    if sys.platform == "win32": command += ["-Wl,--no-insert-timestamp"]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    coefficients = np.array([L002.correction(k) for k in range(1, K+1)])
    cpath = work / "coefficients.txt"
    raw = "".join(f"{v:.17g}\n" for v in coefficients).encode()
    if cpath.exists() and cpath.read_bytes() != raw:
        raise ValueError("forecast coefficient checkpoint mismatch")
    cpath.write_bytes(raw)
    frozen = {name: digest(ROOT/name) for name in ("mf/forecast_n0.c", "mf/null_n0.py", "laws/L002.py")}
    frozen["coefficients"] = digest(cpath)
    frozen["executable"] = digest(exe)
    deadline = time.monotonic()+hours*3600
    parts = []; sums = np.zeros(K); all_means = []
    for a in range(lo, hi+1, chunk):
        b = min(a+chunk-1, hi); key = f"{a}_{b}_{K}"
        marker = work / f"{key}.json"
        means = work / f"{key}.means.csv"; byk = work / f"{key}.byk.csv"
        if marker.exists():
            record = json.loads(marker.read_text())
            if record["sources"] != frozen or record["bounds"] != [a,b,K]:
                raise ValueError("forecast checkpoint sources/bounds mismatch")
            if record["means_sha256"] != digest(means) or record["byk_sha256"] != digest(byk):
                raise ValueError("forecast checkpoint artifact mismatch")
        else:
            # Unfinished outputs are preserved; use a new work directory to retry.
            if means.exists() or byk.exists():
                raise ValueError("incomplete chunk exists; preserve it and use a new work directory")
            remaining = deadline-time.monotonic()
            if remaining <= 0: raise TimeoutError("forecast budget exhausted")
            started = utcnow(); clock = time.monotonic()
            result = subprocess.run([str(exe),str(a),str(b),str(K),str(cpath),str(means),str(byk)],
                                    capture_output=True, text=True, check=True, timeout=remaining)
            record = {**json.loads(result.stdout), "kind": "prediction-only", "started_at": started,
                      "wall_seconds": time.monotonic()-clock, "sources": frozen,
                      "means_sha256": digest(means), "byk_sha256": digest(byk)}
            atomic_json(marker, record)
        print(json.dumps({"forecast_chunk": [a,b,K], "exponents": record["exponents"]}), flush=True)
        values = np.loadtxt(means, delimiter=",", ndmin=2)
        ks = np.loadtxt(byk, delimiter=",", ndmin=2)
        if not np.array_equal(ks[:,0], np.arange(1,K+1)):
            raise ValueError("forecast k coverage mismatch")
        if values.shape != (record["exponents"],3):
            raise ValueError("forecast exponent output mismatch")
        sums += ks[:,1]; all_means.append(values); parts.append(record)
    rows = np.concatenate(all_means)
    n0, a0 = poisson_summary(rows[:,1]); l2, a2 = poisson_summary(rows[:,2])
    return rows[:,0].astype(np.int64), {
        "N0": {**marginal_cells(sums), **n0},
        "L002": {**marginal_cells(sums*coefficients), **l2}}, {"parts": parts,"N0": a0,"L002": a2}


def forecast(bounds, work, hours=1., chunk=1_000_000):
    names = ("mf/forecast.py","mf/forecast_n0.c","mf/power.py","mf/null_n0.py",
             "laws/L001.py","laws/L002.py","laws/L003.py","laws/L003.md","POWER_PROTOCOL.md")
    sources = {name: digest(ROOT/name) for name in names}
    ps, models, native = native_forecast(bounds, work, hours, chunk)
    smooth, audit = smooth_models(ps, bounds[2], bounds)
    check, check_audit = smooth_models(ps, bounds[2], bounds, CHECK_NODES)
    discrepancy = max(abs(smooth[m][c]-check[m][c]) for m in smooth for c in smooth[m])
    if discrepancy > 1e-6 or max(audit["direct_sample_max_absolute_error"],check_audit["direct_sample_max_absolute_error"]) > 1e-11:
        raise ValueError("forecast numerical validation failed")
    models.update(smooth)
    models = {m: models[m] for m in ("N0","L001","L002","L003")}
    cells = multiplicity_cells()
    dyadic = [c for c in models["N0"] if c.startswith("dyadic:")]
    composite = list(models["N0"])
    if sources != {name: digest(ROOT/name) for name in names}:
        raise ValueError("forecast source changed during the calculation; reaggregate saved chunks")
    return {"schema": "prospective-power-v1", "status": "power-check-only-not-preregistered",
            "created_at": utcnow(), "bounds": list(bounds), "exponents": len(ps),
            "census_computed": False, "sources": sources, "models": models,
            "numerics": {"native": native,"smooth": audit,"check_nodes": CHECK_NODES,
                         "cross_resolution_max_absolute_cell_error": discrepancy,
                         "numpy_version": np.__version__, "python_version": sys.version},
            "power": {"multiplicity": matrix(models,cells), "dyadic": matrix(models,dyadic),
                      "descriptive_composite": matrix(models,composite)},
            "score_cells": {"multiplicity": cells,"dyadic": dyadic,"descriptive_composite": composite}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bounds",nargs=3,type=int,required=True)
    ap.add_argument("--work",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--hours",type=float,default=1.)
    ap.add_argument("--chunk",type=int,default=1_000_000)
    args = ap.parse_args()
    output = Path(args.output)
    if output.exists(): raise ValueError("forecast output already exists")
    report = forecast(args.bounds,Path(args.work),args.hours,args.chunk)
    raw = (json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("xb") as f: f.write(raw)
    print(json.dumps({"forecast": str(output),"sha256": hashlib.sha256(raw).hexdigest(),
                      "multiplicity": {m:{c:v for c,v in row.items() if c in multiplicity_cells()} for m,row in report["models"].items()},
                      "power": {score:{pair:[v["A_true"]["expected_gain"],v["B_true"]["expected_gain"]] for pair,v in mat.items()} for score,mat in report["power"].items()}}),flush=True)
