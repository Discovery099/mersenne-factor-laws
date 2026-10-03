"""Literal P12 N0. Floating-point predictions never participate in acceptance."""
from math import log, prod
from .checker import k_class_ok

SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
SIEVE_FACTOR = prod(r / (r - 1) for r in SMALL_PRIMES)


def weight(p, k):
    if not k_class_ok(p, k):
        return 0.0
    q = 2 * k * p + 1
    if any(q % r == 0 for r in SMALL_PRIMES):
        return 0.0
    return SIEVE_FACTOR / (k * log(q))
