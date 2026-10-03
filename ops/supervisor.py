"""Persistent queue supervisor with explicit resource caps and bounded retries."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from mf.protocol import ROOT, atomic_json, utcnow
from .common import exclusive_lock

RUNTIME = ROOT / "ops/runtime"


def queue(path):
    jobs, seen = [], set()
    if not Path(path).exists():
        return jobs
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        job = json.loads(line)
        if not isinstance(job.get("id"), str) or not job["id"].replace("-", "").replace("_", "").isalnum() or job["id"] in seen:
            raise ValueError("queue IDs must be unique safe filenames")
        if job.get("kind", "census") != "census" or job.get("hours", 0) <= 0 or type(job.get("seed")) is not int:
            raise ValueError("queue jobs require census kind, positive hours and integer seed")
        for field in ("checkpoint", "predictions"):
            (ROOT / job[field]).resolve().relative_to(ROOT)
        seen.add(job["id"])
        jobs.append(job)
    return jobs


def alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.OpenProcess.restype = wintypes.HANDLE
        handle = k.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = wintypes.DWORD()
        k.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.GetExitCodeProcess(handle, ctypes.byref(code))
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CloseHandle(handle)
        return code.value == 259
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def run(queue_path, slots, hours):
    if not 1 <= slots <= max(1, os.cpu_count() or 1) or hours <= 0:
        raise ValueError("explicit positive hours and a valid slot count are required")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    lock = RUNTIME / "supervisor.pid"
    if lock.exists():
        pid = int(lock.read_text())
        if alive(pid):
            raise ValueError("a supervisor is already running")
        lock.unlink()
    with lock.open("x") as f:
        f.write(str(os.getpid()))
    state_path = RUNTIME / "jobs.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    active, deadline, stopped = {}, time.monotonic() + hours * 3600, False
    def stop(signum, frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while time.monotonic() < deadline and not stopped:
            (ROOT / "HEARTBEAT").write_text(utcnow() + "\n")
            jobs = queue(queue_path)
            wanted = {job["id"] for job in jobs}
            for ident, (proc, logfile) in list(active.items()):
                if ident not in wanted and proc.poll() is None:
                    terminate_owned(proc)
                    state[ident]["cancelled"] = True
                rc = proc.poll()
                if rc is None:
                    continue
                logfile.close()
                item = state[ident]
                item["status"] = "cancelled" if item.get("cancelled") else ("complete" if rc == 0 else ("paused-budget" if rc == 75 else "crashed"))
                item["exit_code"], item["ended_at"] = rc, utcnow()
                item["elapsed_s"] = item.get("elapsed_s", 0) + time.time() - item["start_epoch"]
                active.pop(ident)
            for job in jobs:
                ident = job["id"]
                item = state.setdefault(ident, {"attempts": 0, "status": "queued", "job": job})
                if item["job"] != job:
                    raise ValueError("an existing job changed; use a new job ID")
                if item["status"] == "running" and ident not in active:
                    if alive(item.get("pid")):
                        # Leave an orphaned live worker alone; never duplicate its work.
                        continue
                    check = ROOT / job["checkpoint"] / "checkpoint.json"
                    item["status"] = json.loads(check.read_text()).get("status", "crashed") if check.exists() else "crashed"
                if ident in active or item["status"] in ("complete", "failed", "paused-budget", "running", "cancelled"):
                    continue
                live_orphans = sum(v["status"] == "running" and k not in active for k, v in state.items())
                if len(active) + live_orphans >= slots:
                    break
                if item["attempts"] >= 4:
                    item["status"] = "failed"
                    continue
                remaining = min(job["hours"] * 3600 - item.get("elapsed_s", 0), deadline - time.monotonic())
                if remaining <= 0:
                    item["status"] = "paused-budget"
                    continue
                log = RUNTIME / f"{ident}.log"
                handle = log.open("ab")
                cmd = [sys.executable, "-m", "ops.worker", "--predictions", job["predictions"], "--checkpoint", job["checkpoint"],
                       "--seed", str(job["seed"]), "--hours", str(remaining / 3600), "--chunk", str(job.get("chunk", 1000))]
                proc = subprocess.Popen(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT)
                item.update({"status": "running", "pid": proc.pid, "started_at": utcnow(), "start_epoch": time.time(),
                             "attempts": item["attempts"] + 1, "log": str(log), "command": cmd})
                active[ident] = proc, handle
            atomic_json(state_path, state)
            if not active and all(v["status"] in ("complete", "failed", "paused-budget", "cancelled") for v in state.values()):
                break
            time.sleep(1)
        # Workers have their own deadlines. A small grace period lets them checkpoint.
        for ident, (proc, handle) in active.items():
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                terminate_owned(proc)
                proc.wait(timeout=5)
            handle.close()
            state[ident].update(status="complete" if proc.returncode == 0 else "paused-budget", ended_at=utcnow())
        atomic_json(state_path, state)
        return state
    finally:
        lock.unlink(missing_ok=True)


def terminate_owned(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        # Only the exact child process tree launched by this supervisor is targeted.
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.terminate()


def status():
    heartbeat = ROOT / "HEARTBEAT"
    age = None
    if heartbeat.exists():
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(heartbeat.read_text().strip())).total_seconds()
    state = json.loads((RUNTIME / "jobs.json").read_text()) if (RUNTIME / "jobs.json").exists() else {}
    disk = shutil.disk_usage(ROOT)
    return {"heartbeat_age_s": age, "jobs": state, "disk_used_fraction": disk.used / disk.total,
            "leaderboard": (ROOT / "LEADERBOARD.md").read_text() if (ROOT / "LEADERBOARD.md").exists() else "",
            "alerts": (ROOT / "ALERTS.md").read_text().split("\n## ")[:6] if (ROOT / "ALERTS.md").exists() else []}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    p = sub.add_parser("run")
    p.add_argument("--queue", default="ops/queue.jsonl")
    p.add_argument("--slots", type=int, default=1)
    p.add_argument("--hours", type=float, required=True)
    a = ap.parse_args()
    try:
        if a.command == "status":
            result = status()
        else:
            with exclusive_lock(RUNTIME / "supervisor.lock"):
                result = run(a.queue, a.slots, a.hours)
        print(json.dumps(result, sort_keys=True))
        return 0 if a.command == "status" or all(v["status"] == "complete" for v in result.values()) else 1
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
