"""Generic factorial-quotient histograms, direct and Legendre implementations."""
from math import factorial, prod
from mf.checker import is_prime


def direct_value(n, numerator, denominator):
    args = [a*n+b for a, b in numerator + denominator]
    if any(type(v) is not int or v < 0 for v in args):
        raise ValueError("factorial arguments must be nonnegative integers")
    top = prod(factorial(a*n+b) for a, b in numerator)
    bottom = prod(factorial(a*n+b) for a, b in denominator)
    value, rem = divmod(top, bottom)
    if rem:
        raise ValueError("factorial quotient is not an integer")
    return value


def vp(value, p):
    e = 0
    while value % p == 0:
        value //= p
        e += 1
    return e


def factorial_vp(n, p):
    total = 0
    while n:
        n //= p
        total += n
    return total


def histogram(R, x, y, px=2, py=3, cap=6, method="direct"):
    if not 0 <= R <= 60 or not is_prime(px) or not is_prime(py) or cap < 0 or method not in ("direct", "legendre"):
        raise ValueError("invalid oracle parameters")
    bins = {}
    for n in range(R + 1):
        values = []
        for (numerator, denominator), p in ((x, px), (y, py)):
            # Integrality is an input requirement, checked independently of valuation arithmetic.
            value = direct_value(n, numerator, denominator)
            e = vp(value, p) if method == "direct" else sum(factorial_vp(a*n+b, p) for a,b in numerator) - sum(factorial_vp(a*n+b, p) for a,b in denominator)
            values.append(min(e, cap))
        key = tuple(values)
        bin_ = bins.setdefault(key, {"count": 0, "min_n": n})
        bin_["count"] += 1
    return bins
