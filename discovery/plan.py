import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
from mf.checker import is_prime
from mf.protocol import digest, write_once


def assignment(row, operator):
    if row.get("account") != operator or row.get("status") != "assigned":
        raise ValueError("assignment must belong to the specified operator")
    if not row.get("assignment_id") or not row.get("source"):
        raise ValueError("assignment ID and provenance source required")
    p = row.get("p")
    if type(p) is not int or p < 3 or not is_prime(p):
        raise ValueError("assignment exponent must be a proven odd prime")
    expiry = datetime.fromisoformat(row["expires_at"])
    if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
        raise ValueError("assignment is expired or timezone is missing")
    if row.get("method") not in ("pm1", "ecm", "tf"):
        raise ValueError("unsupported assignment method")
    return row


def allocate(assignments, candidates, operator, cpu_hours):
    if not math.isfinite(cpu_hours) or cpu_hours <= 0:
        raise ValueError("positive CPU-hour budget required")
    rows = {}
    for row in assignments:
        assignment(row, operator)
        if row["assignment_id"] in rows:
            raise ValueError("duplicate assignment")
        rows[row["assignment_id"]] = row
    ranked = []
    for cand in candidates:
        row = rows[cand["assignment_id"]]
        if cand["method"] != row["method"]:
            raise ValueError("candidate does not match assignment method")
        if cand.get("selection_model") not in ("pm1-smoothness", "ecm-curve-probability", "tf-bit-interval"):
            raise ValueError("method selection model must be explicit")
        expected_model = {"pm1": "pm1-smoothness", "ecm": "ecm-curve-probability", "tf": "tf-bit-interval"}[row["method"]]
        if cand["selection_model"] != expected_model or not cand.get("prediction_source_sha256"):
            raise ValueError("method-conditioned prediction provenance required")
        cost, expected = cand["cpu_seconds"], cand["expected_new_factors"]
        if not math.isfinite(cost) or cost <= 0 or not math.isfinite(expected) or expected < 0:
            raise ValueError("invalid expected yield or benchmark cost")
        if row["method"] in ("pm1", "ecm"):
            if type(cand.get("B1")) is not int or type(cand.get("B2")) is not int or not 2 <= cand["B1"] <= cand["B2"]:
                raise ValueError("require integer 2<=B1<=B2")
            if row["method"] == "pm1" and cand["B1"] <= row.get("completed_B1", 0) and cand["B2"] <= row.get("completed_B2", 0):
                continue
            if row["method"] == "ecm" and (type(cand.get("curves")) is not int or cand["curves"] < 1):
                raise ValueError("positive ECM curve count required")
        elif not 0 <= cand["from_bits"] < cand["to_bits"] or cand["from_bits"] < row.get("completed_tf_bits", 0):
            raise ValueError("TF interval invalid or overlaps completed work")
        ranked.append({**cand, "p": row["p"], "factors_per_cpu_hour": expected * 3600 / cost})
    ranked.sort(key=lambda c: (-c["factors_per_cpu_hour"], c["p"]))
    selected, used, seen = [], 0.0, set()
    for candidate in ranked:
        if candidate["assignment_id"] in seen or used + candidate["cpu_seconds"] > cpu_hours * 3600:
            continue
        seen.add(candidate["assignment_id"])
        selected.append(candidate)
        used += candidate["cpu_seconds"]
    return {"selected": selected, "predicted_cpu_hours": used / 3600, "ranking": ranked,
            "limitation": "yield inputs require external method-specific calibration; L001 is not calibrated for discovery"}


def matched_ab(rows, seed):
    if len({r["p"] for r in rows}) != len(rows):
        raise ValueError("A/B exponents must be distinct")
    # Match method and completed bounds before matching nearest exponents.
    strata = {}
    for row in rows:
        key = (row["method"], row.get("completed_B1", 0), row.get("completed_B2", 0), row.get("completed_tf_bits", 0))
        strata.setdefault(key, []).append(row)
    rng, pairs, unmatched = random.Random(seed), [], []
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda r: r["p"])
        for i in range(0, len(group) - 1, 2):
            pair = group[i:i+2]
            rng.shuffle(pair)
            pairs.append({"baseline": pair[0], "law": pair[1]})
        if len(group) % 2:
            unmatched.append(group[-1])
    return {"seed": seed, "pairs": pairs, "unmatched": unmatched,
            "metric": "credited new factors / measured CPU hours", "hardware": "same host and resource allocation",
            "baseline": "operator-recorded Prime95 default bounds from the installed version"}


def bootstrap_rate_difference(matched_results, seed=12, samples=10000):
    if len(matched_results) < 2:
        raise ValueError("at least two matched pairs required for exploratory interval")
    rng = random.Random(seed)
    def difference(rows):
        rates = []
        for arm in ("baseline", "law"):
            exposure = sum(r[arm]["cpu_hours"] for r in rows)
            if exposure <= 0 or any(r[arm]["new_factors"] < 0 for r in rows):
                raise ValueError("invalid exposure/outcome")
            rates.append(sum(r[arm]["new_factors"] for r in rows) / exposure)
        return rates[1] - rates[0]
    draws = sorted(difference(rng.choices(matched_results, k=len(matched_results))) for _ in range(samples))
    return {"difference": difference(matched_results), "paired_bootstrap_95_percent": [draws[int(samples*.025)], draws[int(samples*.975)]],
            "caution": "exploratory; unstable with few discoveries or few matched pairs"}


def ecm_command(tool, row, candidate, checkpoint):
    if row["method"] not in ("pm1", "ecm"):
        raise ValueError("GPU TF requires the installed tool's reviewed configuration")
    if not Path(tool).is_file():
        raise ValueError("GMP-ECM executable not found")
    argv = [str(Path(tool).resolve())]
    if row["method"] == "pm1":
        argv += ["-pm1"]
    else:
        argv += ["-c", str(candidate["curves"])]
    argv += ["-save", str(Path(checkpoint) / "ecm-residues.txt"), str(candidate["B1"]), str(candidate["B2"])]
    return {"argv": argv, "stdin": f"2^{row['p']}-1\n", "submission": "operator-managed PrimeNet client"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Prepare an allocation plan from owned assignments and calibrated method predictions")
    ap.add_argument("--assignments", type=Path, required=True)
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--operator", required=True)
    ap.add_argument("--cpu-hours", type=float, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    result = allocate(json.loads(a.assignments.read_text()), json.loads(a.candidates.read_text()), a.operator, a.cpu_hours)
    result["assignment_export_sha256"] = digest(a.assignments)
    write_once(a.output, (json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"plan": str(a.output), "selected": len(result["selected"])}))
