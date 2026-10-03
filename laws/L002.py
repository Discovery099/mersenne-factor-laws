"""Finite Bateman--Horn tail correction to N0; exploratory, zero fitted parameters."""
from functools import lru_cache
from mf.null_n0 import weight as baseline

FITTED_PARAMETERS = 0
LAW_ID = "L002"
TAIL = tuple(r for r in range(53, 998) if all(r % d for d in range(2, 1 + __import__('math').isqrt(r))))


@lru_cache(maxsize=1000000)
def correction(k):
    c = 1.0
    for r in TAIL:
        c *= r / (r - 1) if k % r == 0 else r * (r - 2) / ((r - 1) ** 2)
    return c


def weight(p, k):
    return baseline(p, k) * correction(k)
