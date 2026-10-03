"""Slow independent small-range oracle: build M_p and divide by each prime q."""
from math import isqrt


def trial_prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def census(lo, hi, K):
    if hi > 200 or K > 10000:
        raise ValueError("division oracle limited to p<=200, K<=10000")
    limit = 2 * hi * K + 1
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    for d in range(2, isqrt(limit) + 1):
        if sieve[d]:
            for multiple in range(d*d, limit + 1, d):
                sieve[multiple] = 0
    qs = [i for i in range(2, limit + 1) if sieve[i]]
    pairs = []
    for p in range(max(lo, 3), hi + 1):
        if not trial_prime(p):
            continue
        mersenne = (1 << p) - 1
        for q in qs:
            if q > 2 * p * K + 1:
                break
            if mersenne % q == 0:
                assert (q - 1) % (2 * p) == 0
                pairs.append((p, (q - 1) // (2 * p)))
    return pairs
