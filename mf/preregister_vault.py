"""Power-gated, write-once multi-law preregistration. Never runs a census."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

from .power import matrix, multiplicity_cells, require_power
from .protocol import ROOT, digest, git, utcnow, write_once

MODELS = ("N0", "L001", "L002", "L003")
SOURCES = ("laws/L001.py", "laws/L002.py", "laws/L003.py", "laws/L003.md",
           "mf/null_n0.py", "mf/forecast.py", "mf/forecast_n0.c", "mf/power.py",
           "mf/preregister_vault.py", "mf/vault_score.py", "mf/forecast_design.py", "POWER_PROTOCOL.md",
           "mf/checker.py", "mf/checker2.c", "mf/census_kp.c", "mf/census_pk.c",
           "mf/stats.py", "mf/score.py", "mf/protocol.py", "vendor/mini-gmp.c",
           "vendor/mini-gmp.h", "mf/__init__.py")


def verify_forecast(report, root=ROOT):
    if report.get("schema") != "prospective-power-v1" or report.get("census_computed") is not False:
        raise ValueError("an outcome-free prospective forecast is required")
    if set(report["models"]) != set(MODELS):
        raise ValueError("all three laws and mandatory N0 must be present")
    for name, sha in report["sources"].items():
        if digest(root/name) != sha:
            raise ValueError("forecast source changed: " + name)
    required = {"mf/forecast.py", "mf/forecast_n0.c", "mf/power.py", "mf/null_n0.py",
                "laws/L001.py", "laws/L002.py", "laws/L003.py", "laws/L003.md", "POWER_PROTOCOL.md"}
    if "constituents" in report:
        required.add("mf/forecast_design.py")
        last_hi = report["bounds"][0]-1
        for part in report["constituents"]:
            if part["bounds"][0] != last_hi+1 or part["bounds"][2] != report["bounds"][2]:
                raise ValueError("constituent region coverage mismatch")
            last_hi=part["bounds"][1]
            if digest(root/part["file"]) != part["sha256"]:
                raise ValueError("constituent forecast changed")
            child=json.loads((root/part["file"]).read_text())
            if child["bounds"] != part["bounds"]: raise ValueError("constituent bounds mismatch")
            verify_forecast(child,root)
        if last_hi != report["bounds"][1]: raise ValueError("incomplete design coverage")
    if set(report["sources"]) != required:
        raise ValueError("forecast source set mismatch")
    if "constituents" not in report:
        numeric=report["numerics"]
        if numeric["cross_resolution_max_absolute_cell_error"] > 1e-6 or numeric["smooth"]["direct_sample_max_absolute_error"] > 1e-11:
            raise ValueError("numerical accuracy gate failed")
        for model in MODELS:
            side="native" if model in ("N0","L002") else "smooth"
            if not 0 <= numeric[side][model]["maximum_total_truncation_bound"] < 1e-9:
                raise ValueError("maximum truncation error exceeds allowance")
    all_cells = list(report["models"]["N0"])
    for model in MODELS:
        if set(report["models"][model]) != set(all_cells):
            raise ValueError("model cell sets differ")
    expected_cells = {"total", *multiplicity_cells()}
    expected_cells.update(f"dyadic:{j}" for j in range(report["bounds"][2].bit_length()))
    expected_cells.update(f"residue:{m}:{r}" for m in (3,4,5,8,12) for r in range(m))
    if set(all_cells) != expected_cells:
        raise ValueError("fixed complete summary cell set required")
    for name, cells in report["score_cells"].items():
        if report["power"][name] != matrix(report["models"],cells):
            raise ValueError("power report does not match predictions")
    if set(report["score_cells"]["descriptive_composite"]) != expected_cells:
        raise ValueError("primary score must use the original complete summary exactly once")
    return matrix(report["models"],report["score_cells"]["descriptive_composite"])


def create(forecast_path, output, root=ROOT):
    forecast_path, output = Path(forecast_path).resolve(), Path(output).resolve()
    forecast_path.relative_to(root); output.relative_to(root)
    report = json.loads(forecast_path.read_text())
    primary_power = verify_forecast(report,root)
    require_power(primary_power)
    if report["bounds"] != [10_000_001,30_000_000,10_000]:
        raise ValueError("this registration requires the declared power-enlarged design")
    if [part["bounds"] for part in report.get("constituents",[])] != [[10_000_001,20_000_000,10_000],[20_000_001,30_000_000,10_000]]:
        raise ValueError("sealed region 2 must remain a separately identified fixed subregion")
    region2=json.loads((root/report["constituents"][0]["file"]).read_text())
    laws = {}
    for law in MODELS[1:]:
        path = root/"laws"/(law+".py")
        size = len(gzip.compress(path.read_bytes(),mtime=0))
        if size > 2000: raise ValueError("law source exceeds 2000 compressed bytes")
        laws[law] = {"fitted_parameters": 0, "gzip_bytes": size, "path": path.relative_to(root).as_posix()}
    record = {"schema": "vault-multilaw-v1", "id": "Vault_S2_L001_L002_L003",
              "status": "frozen-predictions; registration requires matching git commit and SHA delivery",
              "created_at": utcnow(), "bounds": report["bounds"], "exponents": report["exponents"],
              "models": report["models"], "laws": laws, "power": report["power"],
              "score_cells": report["score_cells"], "primary_score": "descriptive_composite",
              "threshold": 14, "required_power_directions": "both",
              "score_definition": "sum 2*(mu-y+y*log(y/mu)); y=0 term 2*mu; maximum included once",
              "interpretation": "prescribed composite diagnostic; overlapping cells are not an independent likelihood",
              "multiplicity_contrast": "L003 versus L001: same factor-count means, finite Bernoulli versus Poisson",
              "selection_model": "exact complete census; no discovery-method selection",
              "census_computed": False, "sealed_summaries_inspected": False,
              "design_reason": "fixed region 2 L002 versus N0 expected gain was below 14 in both directions; prospective cell enlarged before commitment",
              "regions": report["constituents"],
              "sealed_region_2": {"bounds":region2["bounds"],"models":region2["models"],
                                  "power":region2["power"],"score_cells":region2["score_cells"],
                                  "L002_vs_N0_status":"underpowered on this subset; no standalone threshold claim; primary test is enlarged design"},
              "external_confirmation": "operator comparison and census-hash confirmation required after computation",
              "forecast_file": forecast_path.relative_to(root).as_posix(), "forecast_sha256": digest(forecast_path),
              "sources": {name: digest(root/name) for name in SOURCES}}
    raw = (json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    write_once(output,raw)
    return {"path": str(output), "sha256": hashlib.sha256(raw).hexdigest()}


def registered(prediction, root=ROOT):
    path = Path(prediction).resolve(); rel = path.relative_to(root).as_posix()
    raw = path.read_bytes(); record = json.loads(raw); sha = hashlib.sha256(raw).hexdigest()
    if record.get("schema") != "vault-multilaw-v1" or set(record["sources"]) != set(SOURCES):
        raise ValueError("incorrect multi-law registration schema or source set")
    for name,expected in record["sources"].items():
        if digest(root/name) != expected: raise ValueError("frozen source changed: "+name)
    if digest(root/record["forecast_file"]) != record["forecast_sha256"]:
        raise ValueError("power forecast artifact changed")
    report = json.loads((root/record["forecast_file"]).read_text())
    require_power(verify_forecast(report,root))
    if record["models"] != report["models"] or record["power"] != report["power"] or record["score_cells"] != report["score_cells"] or record["bounds"] != report["bounds"]:
        raise ValueError("prediction does not match power-checked forecast")
    region2=json.loads((root/report["constituents"][0]["file"]).read_text())
    for key in ("bounds","models","power","score_cells"):
        if record["sealed_region_2"][key] != region2[key]:
            raise ValueError("sealed region 2 subrecord differs from its fixed forecast")
    for commit in reversed(git("log","--format=%H","--",rel,root=root).splitlines()):
        artifacts={**record["sources"],record["forecast_file"]:record["forecast_sha256"]}
        artifacts.update({part["file"]:part["sha256"] for part in record["regions"]})
        names=[rel,"ALERTS.md",*artifacts]
        try:
            result=subprocess.run(["git","-C",str(root),"cat-file","--batch"],
                input="".join(f"{commit}:{name}\n" for name in names).encode(),capture_output=True,check=True)
            stream=io.BytesIO(result.stdout); blobs={}
            for name in names:
                header=stream.readline().rstrip(b"\n").split()
                if len(header)!=3 or header[1]!=b"blob": break
                blobs[name]=stream.read(int(header[2])); stream.read(1)
            if len(blobs)!=len(names): continue
            def blob(name): return blobs[name]
            if blob(rel) != raw or sha not in blob("ALERTS.md").decode(): continue
            for name,expected in artifacts.items():
                if hashlib.sha256(blob(name)).hexdigest() != expected:
                    raise ValueError("source/power bytes were not frozen with prediction")
            return {"prediction_sha256":sha,"prediction_commit":commit,
                    "commit_time":git("show","-s","--format=%cI",commit,root=root)}
        except subprocess.CalledProcessError:
            continue
    raise ValueError("prediction, sources, power report and SHA alert must be committed before census")


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("forecast"); ap.add_argument("output")
    args=ap.parse_args()
    print(json.dumps(create(args.forecast,args.output)))
