import argparse
import json
import math
from pathlib import Path
import sys
from .checker import parse_census
from .protocol import audit, digest, atomic_json
from .stats import summary, scoring_cells


def poisson_deviance(y, mu):
    if type(y) is not int or y < 0 or not math.isfinite(mu) or mu < 0:
        raise ValueError("invalid count or expectation")
    if y == 0:
        return 2 * mu
    if mu == 0:
        return math.inf
    return max(0.0, 2 * (mu - y + y * math.log(y / mu)))


def score_cells(observed, predictions, fitted_parameters=0):
    if set(observed) != set(predictions["null"]["cells"]) or set(observed) != set(predictions["law"]["cells"]):
        raise ValueError("every scored cell must have been preregistered")
    residuals = {}
    totals = {"null": 0.0, "law": 0.0}
    for cell, y in observed.items():
        residuals[cell] = {"observed": y}
        for model in ("null", "law"):
            mu = predictions[model]["cells"][cell]
            dev = poisson_deviance(y, mu)
            totals[model] += dev
            residuals[cell][model] = {"predicted": mu, "residual": y - mu, "deviance": dev if math.isfinite(dev) else "infinity"}
    gain = totals["null"] - totals["law"]
    threshold = 2 * fitted_parameters + 14
    disjoint = {}
    for label, keys in (("total_only", ["total"]), ("dyadic_partition", [k for k in observed if k.startswith("dyadic:")])):
        if not keys or any(k not in observed for k in keys):
            continue
        d = {model: sum(poisson_deviance(observed[k], predictions[model]["cells"][k]) for k in keys) for model in ("null", "law")}
        difference = d["null"] - d["law"]
        disjoint[label] = {"deviance": {k: v if math.isfinite(v) else "infinity" for k,v in d.items()},
                           "gain": difference if math.isfinite(difference) else "undefined-or-infinite",
                           "threshold_met": not math.isnan(difference) and difference >= threshold}
    return {"deviance": {k: v if math.isfinite(v) else "infinity" for k, v in totals.items()},
            "gain": gain if math.isfinite(gain) else "undefined-or-infinite", "threshold": threshold,
            "threshold_met": not math.isnan(gain) and gain >= threshold,
            "interpretation": "descriptive composite score: overlapping queries are dependent",
            "residuals": residuals, "disjoint_scores": disjoint}


def run(law, predictions, census, manifest):
    pred, _ = audit(predictions, census, manifest)
    if digest(law) != pred["sources"][pred["law_path"]]:
        raise ValueError("law differs from committed source")
    stats = summary(parse_census(Path(census).read_bytes()), *pred["bounds"])
    result = score_cells(scoring_cells(stats), pred, pred["fitted_parameters"])
    result.update({"bounds": pred["bounds"], "census_sha256": stats["sha256"], "law_id": pred["law_id"],
                   "operator_vault_confirmation": False})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--census", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--output")
    a = ap.parse_args()
    try:
        value = run(a.law, a.predictions, a.census, a.manifest or str(a.census) + ".manifest.json")
        if a.output:
            atomic_json(a.output, value)
        print(json.dumps(value, allow_nan=False, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
