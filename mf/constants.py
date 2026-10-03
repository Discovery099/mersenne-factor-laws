"""Directed-rounding enclosure of the twin-prime Euler product, no observed data."""
import argparse
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import json
from .checker import primes_upto


def enclose(bound=20_000_000, precision=50):
    if type(bound) is not int or not 3 <= bound <= 20_000_000 or precision < 30:
        raise ValueError("require 3<=bound<=20000000 and precision>=30")
    lo = hi = Decimal(1)
    for r in primes_upto(bound):
        if r == 2:
            continue
        d = (r-1)**2
        with localcontext() as ctx:
            ctx.prec, ctx.rounding = precision, ROUND_FLOOR
            lo *= Decimal(d-1)/Decimal(d)
        with localcontext() as ctx:
            ctx.prec, ctx.rounding = precision, ROUND_CEILING
            hi *= Decimal(d-1)/Decimal(d)
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = precision, ROUND_FLOOR
        lo *= Decimal(bound-2)/Decimal(bound-1)
        twice_lo = 2*lo
    with localcontext() as ctx:
        ctx.prec, ctx.rounding = precision, ROUND_CEILING
        twice_hi = 2*hi
    return {"bound":bound,"precision":precision,"C2_interval":[str(lo),str(hi)],
            "2C2_interval":[str(twice_lo),str(twice_hi)],
            "C2_six_decimals":[format(lo,'.6f'),format(hi,'.6f')],
            "2C2_six_decimals":[format(twice_lo,'.6f'),format(twice_hi,'.6f')],
            "tail_bound":"product >= 1 - sum_{integer m>B} 1/(m-1)^2 >= 1 - 1/(B-1)",
            "Lambda_heuristic":"1.000000; algebraic average under equidistribution assumptions, not a proven density"}


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bound",type=int,default=20_000_000)
    a=ap.parse_args()
    print(json.dumps(enclose(a.bound),sort_keys=True))
