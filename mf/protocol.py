"""Write-once artifacts and a locally auditable preregistration chain."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_once(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def git(*args, root=ROOT):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


def source_hashes(law_path, root=ROOT):
    law = Path(law_path)
    law = law if law.is_absolute() else root / law
    names = [law.relative_to(root).as_posix(), "mf/checker.py", "mf/checker2.c", "mf/census_kp.c",
             "mf/census_pk.c", "mf/null_n0.py", "mf/predict.py", "mf/stats.py", "mf/score.py",
             "mf/protocol.py", "mf/__init__.py", "ops/__init__.py", "ops/worker.py", "ops/common.py", "vendor/mini-gmp.c", "vendor/mini-gmp.h"]
    return {name: digest(root / name) for name in names}


def registered(prediction, root=ROOT):
    path = Path(prediction).resolve()
    rel = path.relative_to(root.resolve()).as_posix()
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    obj = json.loads(data)
    if obj["sources"] != source_hashes(obj["law_path"], root):
        raise ValueError("frozen source hash mismatch: create a new law and use unseen cells")
    for commit in reversed(git("log", "--format=%H", "--", rel, root=root).splitlines()):
        try:
            blob = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{rel}"], stderr=subprocess.PIPE)
            alerts = git("show", f"{commit}:ALERTS.md", root=root)
            if blob != data or sha not in alerts:
                continue
            for name, expected in obj["sources"].items():
                raw = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:{name}"], stderr=subprocess.PIPE)
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError("source bytes were not frozen with prediction")
            return {"prediction_sha256": sha, "prediction_commit": commit,
                    "commit_time": git("show", "-s", "--format=%cI", commit, root=root), "prediction": rel}
        except subprocess.CalledProcessError:
            continue
    raise ValueError("prediction bytes and SHA in ALERTS.md must appear in a git commit before census computation")


def begin(prediction, manifest, root=ROOT):
    registration = registered(prediction, root)
    if Path(manifest).exists():
        old = json.loads(Path(manifest).read_text())
        if old["prediction_sha256"] != registration["prediction_sha256"]:
            raise ValueError("checkpoint belongs to different predictions")
        return old
    obj = json.loads(Path(prediction).read_text())
    start = utcnow()
    if datetime.fromisoformat(start) <= datetime.fromisoformat(registration["commit_time"]):
        raise ValueError("prediction commit timestamp must precede run start")
    value = {**registration, "started_at": start, "start_head": git("rev-parse", "HEAD", root=root),
             "sources": obj["sources"], "bounds": obj["bounds"], "status": "running"}
    write_once(manifest, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    return value


def audit(prediction, census, manifest, root=ROOT):
    current = registered(prediction, root)
    run = json.loads(Path(manifest).read_text())
    pred = json.loads(Path(prediction).read_text())
    for key in ("prediction_sha256", "prediction_commit"):
        if run[key] != current[key]:
            raise ValueError("run/preregistration mismatch")
    if run["sources"] != pred["sources"] or run["bounds"] != pred["bounds"]:
        raise ValueError("run sources or bounds mismatch")
    subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", current["prediction_commit"], run["start_head"]], check=True, capture_output=True)
    commit_at = datetime.fromisoformat(current["commit_time"]).timestamp()
    start_at = datetime.fromisoformat(run["started_at"]).timestamp()
    if not commit_at < start_at <= Path(census).stat().st_mtime:
        raise ValueError("census does not postdate preregistration")
    if run.get("status") != "complete" or run.get("census_sha256") != digest(census):
        raise ValueError("run incomplete or census artifact modified")
    return pred, run
