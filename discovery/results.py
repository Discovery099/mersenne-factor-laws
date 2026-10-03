"""Prepare verified result packages; do not make unsupported novelty/credit claims."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from mf.checker import verify_factor
from mf.protocol import write_once, digest, utcnow
from ops.common import executable
from .plan import assignment


def package(p, q, row, known, operator, certificate=None, receipt=None):
    assignment(row, operator)
    if row["p"] != p:
        raise ValueError("result exponent does not match assignment")
    first = verify_factor(p, q, certificate)
    if not first["valid"]:
        raise ValueError(first["reason"])
    argv = [str(executable("checker2")), str(p), str(q)]
    if certificate is not None:
        argv += [":".join(map(str, item)) for item in certificate]
    second = subprocess.run(argv, capture_output=True, text=True)
    if second.returncode or not json.loads(second.stdout)["valid"]:
        raise ValueError("independent checker rejected factor")
    if not known.get("source") or not known.get("accessed_at"):
        raise ValueError("known-factor export needs source and access date")
    dt = datetime.fromisoformat(known["accessed_at"])
    if dt.tzinfo is None or dt > datetime.now(timezone.utc):
        raise ValueError("invalid export access date")
    absent = [p, q] not in known["factors"]
    if receipt:
        for field, value in (("p", p), ("q", q), ("account", operator), ("assignment_id", row["assignment_id"])):
            if receipt.get(field) != value:
                raise ValueError("receipt does not match result and operator")
        if not receipt.get("url") or not receipt.get("credited_at"):
            raise ValueError("receipt lacks credit evidence")
    return {"schema": 1, "kind": "factor", "p": p, "q": q, "certificate": certificate,
            "verified_at": utcnow(), "assignment": row, "known_export_accessed_at": known["accessed_at"],
            "absent_from_supplied_export": absent, "receipt": receipt,
            "discovery_status": "operator receipt supplied; external confirmation pending" if absent and receipt else "verified factor; no confirmed new-factor credit",
            "valid": True}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("p", type=int)
    ap.add_argument("q", type=int)
    ap.add_argument("--assignment", type=Path, required=True)
    ap.add_argument("--known", type=Path, required=True)
    ap.add_argument("--operator", required=True)
    ap.add_argument("--certificate", type=Path)
    ap.add_argument("--receipt", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    result = package(a.p, a.q, json.loads(a.assignment.read_text()), json.loads(a.known.read_text()), a.operator,
                     json.loads(a.certificate.read_text()) if a.certificate else None,
                     json.loads(a.receipt.read_text()) if a.receipt else None)
    result["known_export_sha256"] = digest(a.known)
    write_once(a.output, (json.dumps(result, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"valid": True, "artifact_sha256": digest(a.output), "status": result["discovery_status"]}))
