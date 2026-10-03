"""Frozen operator-summary scorer for the multi-law, power-gated protocol.

Input is an operator-supplied cell dictionary, not an unverified sealed result.
Never fabricates hash confirmation or treats the composite as a likelihood.
"""
import argparse
import json
import math
from pathlib import Path
from .score import poisson_deviance
from .preregister_vault import registered
from .protocol import digest


def score(observed, prediction):
    models = prediction["models"]
    if set(observed) != set(models["N0"]):
        raise ValueError("operator summary must contain exactly the preregistered cells")
    residuals = {model:{c:{"observed":observed[c],"predicted":mu,
                         "deviance":poisson_deviance(observed[c],mu)} for c,mu in means.items()}
                 for model,means in models.items()}
    result = {}
    for group,cells in prediction["score_cells"].items():
        ds = {m:math.fsum(row[c]["deviance"] for c in cells) for m,row in residuals.items()}
        contrasts = {}
        for pair,power in prediction["power"][group].items():
            a,b=pair.split("_vs_"); delta=ds[b]-ds[a]
            eligible=power["passes_both_directions"]
            contrasts[pair] = {"gain_for_first_law":delta if math.isfinite(delta) else "undefined-or-infinite",
                "power_eligible":eligible,"first_law_wins":eligible and delta>=14,
                "second_law_wins":eligible and delta<=-14}
        result[group]={"deviances":{m:v if math.isfinite(v) else "infinity" for m,v in ds.items()},
                       "comparisons":contrasts}
    return {"scores":result,"operator_hash_confirmation":False,
            "interpretation":"composite diagnostic, dependent summary cells; hash confirmation is external"}


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prediction"); ap.add_argument("operator_cells")
    ap.add_argument("--region",choices=("sealed-region-2","enlarged-design"),required=True)
    args=ap.parse_args()
    audit=registered(args.prediction)
    pred=json.loads(Path(args.prediction).read_text())
    obj=json.loads(Path(args.operator_cells).read_text())
    if args.region == "sealed-region-2": pred=pred["sealed_region_2"]
    if obj.get("bounds") != pred["bounds"]:
        raise ValueError("operator summary bounds do not match the selected scope")
    print(json.dumps({**score(obj["cells"],pred),"registration":audit,"scope":args.region,"bounds":pred["bounds"],
                      "operator_summary_sha256":digest(args.operator_cells)},indent=2,allow_nan=False))
