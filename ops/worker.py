"""One bounded census job. Only the supervisor should launch campaign jobs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import signal
from mf.checker import parse_census, canonical_bytes, census_hash, verify_census
from mf.protocol import ROOT, begin, atomic_json, digest, write_once, utcnow
from mf.stats import summary
from .common import execute_engine, executable, ledger, second_checker, exclusive_lock


def work(prediction, checkpoint, seed, hours, chunk=1000):
    if hours <= 0 or chunk < 1:
        raise ValueError("hours and chunk must be positive")
    checkpoint = Path(checkpoint)
    checkpoint.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    manifest_path = checkpoint / "manifest.json"
    manifest = begin(prediction, manifest_path)
    lo, hi, K = manifest["bounds"]
    binaries = {name: digest(executable(name)) for name in ("census_kp", "census_pk", "checker2")}
    state_path = checkpoint / "checkpoint.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        "bounds": [lo, hi, K], "seed": seed, "binaries": binaries, "next": lo, "parts": [], "cpu_s": 0.0,
        "wall_s": 0.0, "status": "running"}
    if state["bounds"] != [lo, hi, K] or state["seed"] != seed or state["binaries"] != binaries:
        raise ValueError("checkpoint parameters or binaries changed")
    cursor = lo
    for part in state["parts"]:
        a, b, bound_k = part["bounds"]
        if a != cursor or not a <= b <= hi or bound_k != K or part["path"] != f"part_{a}_{b}.txt":
            raise ValueError("checkpoint coverage or path was modified")
        if digest(checkpoint / part["path"]) != part["sha256"]:
            raise ValueError("checkpoint census part was modified")
        prior_pairs = parse_census((checkpoint / part["path"]).read_bytes())
        verify_census(prior_pairs, part["bounds"])
        if len(prior_pairs) != part["count"]:
            raise ValueError("checkpoint count mismatch")
        cursor = b + 1
    if cursor != state["next"]:
        raise ValueError("checkpoint endpoint was modified")
    cpu_before = state["cpu_s"]
    outcome, certificate = "failed", None
    try:
        while state["next"] <= hi:
            remaining = hours * 3600 - (time.monotonic() - start)
            if remaining <= 0:
                raise subprocess.TimeoutExpired("budget", hours * 3600)
            bounds = [state["next"], min(hi, state["next"] + chunk - 1), K]
            raw_a, timing_a = execute_engine("census_kp", bounds, remaining)
            remaining = hours * 3600 - (time.monotonic() - start)
            raw_b, timing_b = execute_engine("census_pk", bounds, max(0.001, remaining))
            pairs_a, pairs_b = parse_census(raw_a), parse_census(raw_b)
            verify_census(pairs_a, bounds)
            if census_hash(pairs_a) != census_hash(pairs_b):
                raise ValueError("independent census hashes disagree")
            second_checker(pairs_a)
            name = f"part_{bounds[0]}_{bounds[1]}.txt"
            raw = canonical_bytes(pairs_a)
            path = checkpoint / name
            if path.exists():
                if path.read_bytes() != raw:
                    raise ValueError("existing checkpoint part differs")
            else:
                write_once(path, raw)
            state["parts"].append({"path": name, "sha256": digest(path), "bounds": bounds,
                                    "count": len(pairs_a), "engines": [timing_a, timing_b]})
            state["next"] = bounds[1] + 1
            state["cpu_s"] += sum(t["cpu_s"] or 0 for t in (timing_a, timing_b))
            atomic_json(state_path, state)
        combined = b"".join((checkpoint / part["path"]).read_bytes() for part in state["parts"])
        pairs = parse_census(combined)
        census_path = checkpoint / "census.txt"
        if not census_path.exists():
            write_once(census_path, canonical_bytes(pairs))
        elif census_path.read_bytes() != canonical_bytes(pairs):
            raise ValueError("existing census differs")
        subprocess.run([sys.executable, "-m", "mf.checker", "census", str(census_path), "--bounds", *map(str, (lo,hi,K))],
                       cwd=ROOT, capture_output=True, check=True)
        manifest.update({"status": "complete", "completed_at": utcnow(), "census_sha256": digest(census_path),
                         "binaries": binaries, "seed": seed, "parts": state["parts"]})
        atomic_json(manifest_path, manifest)
        stats = summary(pairs, lo, hi, K)
        atomic_json(checkpoint / "statistics.json", stats)
        cert = {"schema": 1, "kind": "census", "bounds": [lo, hi, K], "pairs": pairs,
                "sha256": stats["sha256"], "statistics": stats, "execution": manifest}
        certificate = ROOT / "certificates" / f"census_{lo}_{hi}_{K}_{stats['sha256'][:12]}.json"
        raw = (json.dumps(cert, sort_keys=True, indent=2) + "\n").encode()
        if not certificate.exists():
            write_once(certificate, raw)
        elif certificate.read_bytes() != raw:
            # A completed resume need not rewrite the existing immutable evidence.
            existing = json.loads(certificate.read_text())
            if existing["sha256"] != stats["sha256"]:
                raise ValueError("certificate mismatch")
        outcome = "complete"
        return {"status": outcome, "count": len(pairs), "sha256": stats["sha256"], "certificate": str(certificate)}
    except subprocess.TimeoutExpired:
        outcome = "paused-budget"
        return {"status": outcome, "conclusion": "unknown; checkpoint retained", "next": state["next"]}
    finally:
        state["status"] = outcome
        state["wall_s"] += time.monotonic() - start
        atomic_json(state_path, state)
        ledger("census", [lo, hi, K], seed, time.monotonic() - start, state["cpu_s"] - cpu_before, outcome == "complete",
               outcome, str(certificate) if certificate else None, code_sha=manifest["start_head"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--hours", type=float, required=True)
    ap.add_argument("--chunk", type=int, default=1000)
    args = ap.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt("supervisor stopped the job")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        with exclusive_lock(Path(args.checkpoint) / "worker.lock"):
            result = work(args.predictions, args.checkpoint, args.seed, args.hours, args.chunk)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "complete" else 75
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
