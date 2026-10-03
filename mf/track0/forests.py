"""Exhaustive divisor-parent maps with independently multiplied leaf proofs."""
from itertools import product
from math import prod
from mf.checker import is_prime


def factor_leaves(n):
    if type(n) is not int or n < 2:
        raise ValueError("query integers must be >=2")
    factors, d = [], 2
    while d*d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def verify(queries, parents, leaves, budget):
    if not 1 <= len(queries) <= 8 or len(parents) != len(queries) or len(leaves) != len(queries):
        return None
    tokens = sum(parent != -1 for parent in parents)
    if tokens > budget:
        return None
    depths, products = {}, {}
    def visit(i, active):
        if i in active:
            raise ValueError("cycle")
        if i in products:
            return products[i], depths[i]
        par = parents[i]
        if type(par) is not int or par < -1 or par >= len(queries):
            raise ValueError("parent range")
        if any(not is_prime(r) for r in leaves[i]):
            raise ValueError("leaf is not prime")
        local = prod(leaves[i])
        parent_value, parent_depth = (1, 0) if par == -1 else visit(par, active | {i})
        value, depth = parent_value * local, parent_depth + 1
        if value != queries[i]:
            raise ValueError("leaf product differs from query")
        products[i], depths[i] = value, depth
        return value, depth
    try:
        for i in range(len(queries)):
            visit(i, set())
    except (ValueError, TypeError):
        return None
    return max(depths.values()), tokens


def enumerate_forests(queries, budget):
    if not 1 <= len(queries) <= 8 or budget < 0:
        raise ValueError("forest oracle requires <=8 query integers")
    [factor_leaves(n) for n in queries]
    # All arithmetically possible parent maps, including equal-label cycles.
    choices = [[-1] + [j for j, d in enumerate(queries) if j != i and n % d == 0] for i, n in enumerate(queries)]
    best, checked = None, 0
    for parents in product(*choices):
        if sum(p != -1 for p in parents) > budget:
            continue
        leaves = [factor_leaves(n if p == -1 else n // queries[p]) if p == -1 or n != queries[p] else [] for n, p in zip(queries, parents)]
        score = verify(queries, parents, leaves, budget)
        checked += 1
        if score is not None and (best is None or score < tuple(best["objective"])):
            best = {"parents": list(parents), "leaves": leaves, "objective": list(score)}
    return {"best": best, "parent_maps_checked": checked}
