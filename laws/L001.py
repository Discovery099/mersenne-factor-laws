"""Scalar adapter of the user-supplied v0.2 L001; no fit or archived observations."""
from functools import lru_cache
from math import log

FITTED_PARAMETERS = 0
LAW_ID = "L001"
C2 = 0.6601618158468696


@lru_cache(maxsize=1000000)
def correction(k):
    n, r, c = k, 2, 1.0
    while r * r <= n:
        if n % r == 0:
            if r > 2:
                c *= (r - 1) / (r - 2)
            while n % r == 0:
                n //= r
        r += 1
    if n > 2:
        c *= (n - 1) / (n - 2)
    return c


def weight(p, k):
    if k % 4 not in ((0, 3) if p % 4 == 1 else (0, 1)):
        return 0.0
    return 2 * C2 * correction(k) / (k * log(2 * k * p))
