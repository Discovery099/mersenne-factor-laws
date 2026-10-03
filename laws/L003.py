"""Zero-fit Poisson-binomial multiplicity law with the L001 pair means."""
from functools import lru_cache
from math import log

LAW_ID = "L003"
FITTED_PARAMETERS = 0
C2 = 0.6601618158468696


@lru_cache(maxsize=100000)
def coefficient(k):
    n, r, a = k, 2, 2*C2/k
    while r*r <= n:
        if n % r == 0:
            if r > 2:
                a *= (r-1)/(r-2)
            while n % r == 0:
                n //= r
        r += 1
    if n > 2:
        a *= (n-1)/(n-2)
    return a


def weight(p, k):
    if k % 4 not in ((0, 3) if p % 4 == 1 else (0, 1)):
        return 0.0
    return coefficient(k)/log(2*k*p)


def distribution(probabilities, degree=24):
    """Coefficients through degree of product(1-w+w*z), without renormalizing."""
    if type(degree) is not int or degree < 0:
        raise ValueError("degree must be nonnegative")
    mass = [1.0] + [0.0]*degree
    for w in probabilities:
        if not 0 <= w < 1:
            raise ValueError("Bernoulli weight outside [0,1)")
        for j in range(degree, 0, -1):
            mass[j] = mass[j]*(1-w) + mass[j-1]*w
        mass[0] *= 1-w
    return mass


def multiplicity(p, K, degree=24):
    return distribution((weight(p, k) for k in range(1, K+1)), degree)
