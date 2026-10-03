import argparse
from collections import Counter
import json
from pathlib import Path
from .checker import parse_census, primes_upto, verify_census

MODULI = (3, 4, 5, 8, 12, 24, 60)


def valuation(n, r):
    a = 0
    while n % r == 0:
        n //= r
        a += 1
    return a


def largest_prime_factor(n):
    largest, r = 1, 2
    while r * r <= n:
        while n % r == 0:
            largest, n = r, n // r
        r += 1
    return max(largest, n)


def summary(pairs, lo, hi, K):
    verified = verify_census(pairs, (lo, hi, K))
    buckets = {str(j): 0 for j in range(K.bit_length())}
    residue = {str(m): [0] * m for m in MODULI}
    valuations, smoothness, per_p = {}, Counter(), Counter()
    for p, k in pairs:
        buckets[str(k.bit_length() - 1)] += 1
        for m in MODULI:
            residue[str(m)][k % m] += 1
        key = f"{min(valuation(k, 2), 6)},{min(valuation(k, 3), 6)}"
        cell = valuations.setdefault(key, {"count": 0, "min_p": p})
        cell["count"] += 1
        cell["min_p"] = min(cell["min_p"], p)
        smoothness[str(largest_prime_factor(k).bit_length() - 1)] += 1
        per_p[p] += 1
    multiplicity = Counter(per_p[p] for p in primes_upto(hi) if p >= max(3, lo))
    return {"bounds": [lo, hi, K], "count": len(pairs), "sha256": verified["sha256"],
            "dyadic": buckets, "residues": residue, "valuations": valuations,
            "smoothness": dict(smoothness), "multiplicity": {str(j): n for j, n in sorted(multiplicity.items())},
            "at_least_one": sum(n for j, n in multiplicity.items() if j >= 1),
            "at_least_two": sum(n for j, n in multiplicity.items() if j >= 2),
            "max_factors": max(multiplicity, default=0)}


def scoring_cells(stats):
    out = {"total": stats["count"], "at_least_one": stats["at_least_one"], "at_least_two": stats["at_least_two"]}
    out.update({f"dyadic:{j}": n for j, n in stats["dyadic"].items()})
    out.update({f"residue:{m}:{r}": n for m in (3, 4, 5, 8, 12) for r, n in enumerate(stats["residues"][str(m)])})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("census", type=Path)
    ap.add_argument("--bounds", nargs=3, type=int, required=True)
    a = ap.parse_args()
    print(json.dumps(summary(parse_census(a.census.read_bytes()), *a.bounds), sort_keys=True))
