import argparse
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from .checker import primes_upto, validate_bounds
from .null_n0 import weight as n0


def load_law(path):
    path = Path(path).resolve()
    if len(gzip.compress(path.read_bytes(), mtime=0)) > 2000:
        raise ValueError("law exceeds 2000 gzipped bytes")
    spec = importlib.util.spec_from_file_location("registered_law", path)
    law = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(law)
    if type(law.FITTED_PARAMETERS) is not int or not 0 <= law.FITTED_PARAMETERS <= 8:
        raise ValueError("invalid fitted parameter count")
    if law.FITTED_PARAMETERS:
        raise ValueError("fitted laws require a reviewed open-range fitting provenance adapter")
    return law


def expectations(bounds, weight):
    lo, hi, K = bounds
    validate_bounds(*bounds)
    cells = {"total": 0.0, "at_least_one": 0.0, "at_least_two": 0.0}
    cells.update({f"dyadic:{j}": 0.0 for j in range(K.bit_length())})
    cells.update({f"residue:{m}:{r}": 0.0 for m in (3, 4, 5, 8, 12) for r in range(m)})
    lambdas = []
    for p in primes_upto(hi):
        if p < max(lo, 3):
            continue
        lam = 0.0
        for k in range(1, K + 1):
            value = weight(p, k)
            if not math.isfinite(value) or value < 0:
                raise ValueError("law returned a nonfinite or negative expectation")
            if value == 0:
                continue
            lam += value
            cells[f"dyadic:{k.bit_length() - 1}"] += value
            for m in (3, 4, 5, 8, 12):
                cells[f"residue:{m}:{k % m}"] += value
        lambdas.append(lam)
        cells["total"] += lam
        cells["at_least_one"] += -math.expm1(-lam)
        cells["at_least_two"] += 1 - math.exp(-lam) * (1 + lam)
    # E(max)=sum_j P(max>j). Tail approximation explicitly reported.
    cdfs = [math.exp(-lam) for lam in lambdas]
    masses = cdfs.copy()
    expected_max = 0.0
    for j in range(256):
        logprod = sum(math.log(min(1.0, c)) if c > 0 else -math.inf for c in cdfs)
        tail = -math.expm1(logprod)
        expected_max += tail
        if tail < 1e-12:
            break
        for i, lam in enumerate(lambdas):
            masses[i] *= lam / (j + 1)
            cdfs[i] += masses[i]
    else:
        raise ValueError("Poisson maximum approximation did not reach its tail tolerance")
    return {"cells": cells, "expected_max_factors": expected_max, "maximum_tail_tolerance": 1e-12}


def create(bounds, law_path, output):
    from .protocol import source_hashes, write_once, utcnow
    law = load_law(law_path)
    content = {"schema": 1, "created_at": utcnow(), "bounds": list(bounds),
               "law_id": law.LAW_ID, "law_path": Path(law_path).as_posix(),
               "fitted_parameters": law.FITTED_PARAMETERS,
               "sources": source_hashes(law_path), "null": expectations(bounds, n0),
               "law": expectations(bounds, law.weight),
               "selection_model": "exact census; no discovery-method selection",
               "score_interpretation": "overlapping cells: descriptive composite Poisson deviance"}
    raw = (json.dumps(content, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    write_once(Path(output), raw)
    return {"path": str(output), "sha256": hashlib.sha256(raw).hexdigest(), "N0": content["null"]["cells"]["total"], "law": content["law"]["cells"]["total"]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create a prediction without computing census values")
    ap.add_argument("--bounds", nargs=3, type=int, required=True)
    ap.add_argument("--law", default="laws/L002.py")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    print(json.dumps(create(a.bounds, a.law, a.output)))
