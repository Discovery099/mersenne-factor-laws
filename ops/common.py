import ctypes
import json
import os
from pathlib import Path
import subprocess
import time
from contextlib import contextmanager
from mf.protocol import ROOT, utcnow


def executable(name):
    path = ROOT / "mf" / (name + (".exe" if os.name == "nt" else ""))
    if not path.exists():
        raise FileNotFoundError("C binaries missing; run python -m ops.build")
    return path


def execute_engine(name, bounds, timeout=None):
    start = time.monotonic()
    proc = subprocess.Popen([str(executable(name)), *map(str, bounds)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate(timeout=timeout)
    except BaseException:
        proc.kill()
        proc.communicate()
        raise
    cpu = None
    if os.name == "nt":
        from ctypes import wintypes
        times = [wintypes.FILETIME() for _ in range(4)]
        fn = ctypes.windll.kernel32.GetProcessTimes
        fn.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        if fn(wintypes.HANDLE(int(proc._handle)), *[ctypes.byref(t) for t in times]):
            cpu = sum((t.dwHighDateTime << 32) + t.dwLowDateTime for t in times[2:]) / 1e7
    if proc.returncode:
        raise RuntimeError(f"{name} failed ({proc.returncode}): {err.decode(errors='replace')}")
    return out.replace(b"\r\n", b"\n"), {"engine": name, "wall_s": time.monotonic() - start, "cpu_s": cpu}


@contextmanager
def exclusive_lock(path):
    """OS-released lock, including after process crashes, on Windows and POSIX."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    try:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        handle.close()


def ledger(target, params, seed, wall_s, cpu_s, verified, conclusion, certificate_path=None, **extra):
    row = {"ts": utcnow(), "cycle": 0, "target": target, "idea_id": "BUILD-001",
           "code_sha": extra.pop("code_sha", None), "params": params, "seed": seed,
           "cpu_s": cpu_s, "wall_s": wall_s, "best_score": None, "verified": verified,
           "certificate_path": certificate_path, "conclusion": conclusion,
           "tokens": None, "token_note": "per-experiment token metering unavailable", **extra}
    raw = (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode()
    fd = os.open(str(ROOT / "LEDGER.jsonl"), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, raw)
    finally:
        os.close(fd)


def second_checker(pairs):
    data = "".join(f"{p} {2*p*k+1}\n" for p, k in pairs).encode()
    result = subprocess.run([str(executable("checker2")), "--batch"], input=data, capture_output=True)
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    if result.returncode or len(rows) != len(pairs) or not all(r["valid"] for r in rows):
        raise ValueError("independent C factor checker rejected census")
    return len(rows)
