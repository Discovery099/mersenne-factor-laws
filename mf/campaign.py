"""Reviewable preregistration and queue preparation; computing is supervised."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from .predict import create
from .protocol import ROOT, digest, git


def preregister(name, bounds, law="laws/L002.py"):
    if not name or not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("ID must contain only letters, digits, hyphens and underscores")
    lo, hi, K = bounds
    if not 3 <= lo <= hi < 1_000_000 or not 1 <= K <= 100_000:
        raise ValueError("this convenience command is restricted to the open range; vault operation requires separate review")
    for path in (ROOT / "certificates").glob("*.json"):
        cert = json.loads(path.read_text())
        if cert.get("kind") == "census":
            a, b, _ = cert["bounds"]
            if max(a, lo) <= min(b, hi):
                raise ValueError("region overlaps a previously observed census; use an unseen exponent band")
    imported = ROOT / "data/observed_regions.json"
    if imported.exists():
        for region in json.loads(imported.read_text()):
            a, b, _ = region["bounds"]
            if max(a, lo) <= min(b, hi):
                raise ValueError("region overlaps a run present in the supplied archives")
    path = ROOT / "predictions" / f"{name}.json"
    if path.exists() or (ROOT / "runs" / name).exists():
        raise ValueError("prediction or run ID already exists")
    output = create(bounds, law, path)
    alerts = ROOT / "ALERTS.md"
    old = alerts.read_text() if alerts.exists() else "# Alerts\n"
    alerts.write_text(f"# Alerts\n\n## Preregistration {name}\n\nBounds {bounds}; law {law}; SHA-256 `{output['sha256']}`.\nPrediction created before census; awaiting computation.\n\n" + old.removeprefix("# Alerts\n"), encoding="utf-8")
    pred = json.loads(path.read_text())
    subprocess.run(["git", "-C", str(ROOT), "add", "--", str(path.relative_to(ROOT)), "ALERTS.md", *pred["sources"]], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-m", f"L002 preregister {name} before computation"], check=True, capture_output=True)
    return {**output, "commit": git("rev-parse", "HEAD"), "next": "add the job to ops/queue.jsonl and run the supervisor"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("preregister")
    p.add_argument("id")
    p.add_argument("--bounds", nargs=3, type=int, required=True)
    p.add_argument("--law", default="laws/L002.py")
    a = ap.parse_args()
    try:
        print(json.dumps(preregister(a.id, a.bounds, a.law), sort_keys=True))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
