"""Combine disjoint forecast regions without computing any census values."""
import argparse
import json
import math
from pathlib import Path

from .power import matrix, multiplicity_cells
from .protocol import ROOT, digest, utcnow, write_once


def combine(paths, output):
    paths = [Path(p).resolve() for p in paths]
    reports = [json.loads(p.read_text()) for p in paths]
    reports_and_paths = sorted(zip(reports,paths),key=lambda pair:pair[0]["bounds"][0])
    reports, paths = map(list, zip(*reports_and_paths))
    K = reports[0]["bounds"][2]
    for i,report in enumerate(reports):
        if report.get("schema") != "prospective-power-v1" or report.get("census_computed") is not False:
            raise ValueError("only prospective forecasts may be combined")
        if report["bounds"][2] != K or (i and reports[i-1]["bounds"][1]+1 != report["bounds"][0]):
            raise ValueError("design regions must be disjoint, contiguous and share K")
        for name,sha in report["sources"].items():
            if digest(ROOT/name) != sha: raise ValueError("forecast source changed: "+name)
        if report["sources"] != reports[0]["sources"]:
            raise ValueError("constituent forecasts must share sources")
    models = {}; numeric = {}
    for model in ("N0","L001","L002","L003"):
        row = {c:math.fsum(r["models"][model][c] for r in reports) for c in reports[0]["models"][model] if c != "maximum"}
        side = "native" if model in ("N0","L002") else "smooth"
        arrays = [r["numerics"][side][model]["maximum_log_cdf"] for r in reports]
        if len({len(a) for a in arrays}) != 1: raise ValueError("maximum truncation degree mismatch")
        logcdf = [math.fsum(a[j] for a in arrays) for j in range(len(arrays[0]))]
        row["maximum"] = math.fsum(-math.expm1(v) for v in logcdf)
        models[model] = row
        numeric[model] = {"maximum_log_cdf":logcdf,
            "maximum_total_truncation_bound":math.fsum(r["numerics"][side][model]["maximum_total_truncation_bound"] for r in reports)}
    cells = reports[0]["score_cells"]
    record = {"schema":"prospective-power-v1","status":"power-check-only-not-preregistered",
        "created_at":utcnow(),"bounds":[reports[0]["bounds"][0],reports[-1]["bounds"][1],K],
        "exponents":sum(r["exponents"] for r in reports),"census_computed":False,
        "sources":{**reports[0]["sources"],"mf/forecast_design.py":digest(ROOT/"mf/forecast_design.py")},
        "constituents":[{"file":p.relative_to(ROOT).as_posix(),"sha256":digest(p),"bounds":r["bounds"]} for p,r in zip(paths,reports)],
        "models":models,"numerics":{"combined":numeric,"maximum_rule":"product of CDFs, not sum of region maxima"},
        "score_cells":cells,"power":{group:matrix(models,cs) for group,cs in cells.items()}}
    raw=(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    write_once(output,raw)
    return {"path":str(output),"sha256":digest(output),"power":{
        pair:[row["A_true"]["expected_gain"],row["B_true"]["expected_gain"]] for pair,row in record["power"]["descriptive_composite"].items()}}


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output"); ap.add_argument("forecasts",nargs="+")
    args=ap.parse_args()
    print(json.dumps(combine(args.forecasts,Path(args.output))))
