import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def build():
    cc = os.environ.get("CC") or shutil.which("gcc") or shutil.which("clang")
    if not cc:
        raise RuntimeError("Install a C11 compiler supporting unsigned __int128 (GCC or Clang)")
    provenance = json.loads((ROOT / "vendor/PROVENANCE.json").read_text())
    for name, sha in provenance["files"].items():
        if hashlib.sha256((ROOT / "vendor" / name).read_bytes()).hexdigest() != sha:
            raise RuntimeError(f"vendored source changed: {name}")
    records = []
    for name in ("checker2", "census_kp", "census_pk"):
        output = ROOT / "mf" / (name + (".exe" if os.name == "nt" else ""))
        cmd = [cc, "-O3", "-std=c11", "-Wall", "-Wextra", "-Wno-misleading-indentation",
               str(ROOT / "mf" / (name + ".c")), "-o", str(output)]
        if name == "checker2":
            cmd += ["-Wno-unused-parameter", "-Wno-sign-compare", "-I", str(ROOT / "vendor"), str(ROOT / "vendor/mini-gmp.c")]
        if os.name == "nt":
            cmd += ["-Wl,--no-insert-timestamp"]
        subprocess.run(cmd, check=True, cwd=ROOT)
        records.append({"binary": str(output.relative_to(ROOT)), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()})
    (ROOT / "build").mkdir(exist_ok=True)
    (ROOT / "build/manifest.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps({"built": records}))


if __name__ == "__main__":
    argparse.ArgumentParser(description="Build all three C components").parse_args()
    build()
