"""Prospective expected Poisson-deviance separation; never consumes outcomes."""
import math
from decimal import Decimal, localcontext
from itertools import combinations

THRESHOLD = 14.0


def expected_deviance_gain(truth, alternative):
    """E_truth[D(Y,alternative)-D(Y,truth)] for ANY Y with E[Y]=truth.

    Only this expectation is claimed, not the probability of exceeding 14.
    Decimal prevents loss of significance when two predicted means are close.
    """
    if not math.isfinite(truth) or not math.isfinite(alternative) or min(truth, alternative) < 0:
        raise ValueError("means must be finite and nonnegative")
    if truth == alternative:
        return 0.0
    if truth == 0:
        return 2*alternative
    if alternative == 0:
        return math.inf
    with localcontext() as ctx:
        ctx.prec = 50
        a, b = Decimal(str(truth)), Decimal(str(alternative))
        return float(2*(b-a+a*(a/b).ln()))


def comparison(a, b, cells):
    if not cells or len(set(cells)) != len(cells):
        raise ValueError("score cells must be nonempty and unique")
    directions = {}
    for label, truth, alternative in (("A_true", a, b), ("B_true", b, a)):
        per_cell = {c: expected_deviance_gain(truth[c], alternative[c]) for c in cells}
        directions[label] = {"expected_gain": math.fsum(per_cell.values()), "per_cell": per_cell}
    return {**directions, "threshold": THRESHOLD,
            "passes_both_directions": min(directions[k]["expected_gain"] for k in directions) >= THRESHOLD}


def matrix(models, cells):
    names = sorted(models, key=lambda name: (name != "N0", name))
    return {f"{a}_vs_{b}": comparison(models[a], models[b], cells) for a, b in combinations(names, 2)}


def require_power(report):
    if not report:
        raise ValueError("at least one competing-law power comparison is required")
    failed = [name for name, result in report.items() if not result["passes_both_directions"]]
    if failed:
        raise ValueError("underpowered comparisons; enlarge the prospective design before preregistration: " + ", ".join(failed))


def multiplicity_cells():
    return ["at_least_one", "at_least_two", "maximum"]
