"""Frozen v1 acceptance: exact integer factor/certificate checks, strict census parsing."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
MR_LIMIT = 318665857834031151167461


def prime(n):
    if type(n) is not int or n < 2:
        return False
    if n >= MR_LIMIT:
        raise ValueError("outside proven twelve-base MR domain")
    for a in BASES:
        if n % a == 0:
            return n == a
    odd = n - 1
    shift = 0
    while not odd & 1:
        shift += 1
        odd >>= 1
    for a in BASES:
        v = pow(a, odd, n)
        if v == 1 or v == n - 1:
            continue
        for _ in range(shift - 1):
            v = v * v % n
            if v == n - 1:
                break
        else:
            return False
    return True


def pocklington(n, certificate):
    try:
        if type(n) is not int or n < 3 or not isinstance(certificate, dict):
            return False
        fs = certificate["factors"]
        if not isinstance(fs, list) or not fs:
            return False
        seen, F = set(), 1
        for row in fs:
            r, e, a = row["r"], row["e"], row["a"]
            if any(type(x) is not int for x in (r, e, a)):
                return False
            if r in seen or e < 1 or e > n.bit_length() or not prime(r) or not 1 < a < n:
                return False
            seen.add(r)
            F *= r ** e
            if F > n - 1 or (n - 1) % F:
                return False
            if pow(a, n - 1, n) != 1 or math.gcd(pow(a, (n - 1) // r, n) - 1, n) != 1:
                return False
        return F * F > n
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def factor(p, q, certificate=None):
    if type(p) is not int or type(q) is not int:
        return {"valid": False, "reason": "integer inputs required"}
    if p >= MR_LIMIT:
        return {"valid": False, "status": "unsupported", "reason": "exponent needs primality proof"}
    if p < 3 or not prime(p):
        return {"valid": False, "reason": "p is not an odd prime"}
    if q < 3 or (q - 1) % (2 * p) or q % 8 not in (1, 7):
        return {"valid": False, "reason": "form or residue fails"}
    if pow(2, p, q) != 1:
        return {"valid": False, "reason": "divisibility fails"}
    k = (q - 1) // (2 * p)
    if certificate is not None and not pocklington(q, certificate):
        return {"valid": False, "reason": "provided certificate fails"}
    if certificate is not None:
        method = "Pocklington"
    elif k <= 2 * p + 1:
        method = "L2"
    elif q < MR_LIMIT:
        if not prime(q):
            return {"valid": False, "reason": "composite divisor"}
        method = "deterministic-MR-12"
    else:
        return {"valid": False, "status": "unsupported", "reason": "certificate required"}
    return {"valid": True, "k": k, "primality_method": method}


def read_pairs(path, bounds=None):
    data = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    pairs = []
    previous = (0, 0)
    for line in data.splitlines(keepends=True):
        fields = line.decode("ascii").split()
        if len(fields) != 2:
            raise ValueError("expected two fields")
        p, k = map(int, fields)
        if line != f"{p} {k}\n".encode() or (p, k) <= previous or k < 1:
            raise ValueError("noncanonical, duplicate, unordered or invalid row")
        if bounds and not (bounds[0] <= p <= bounds[1] and k <= bounds[2]):
            raise ValueError("row outside declared region")
        if not factor(p, 2 * p * k + 1)["valid"]:
            raise ValueError(f"invalid factor at p={p}, k={k}")
        previous = (p, k)
        pairs.append(previous)
    return pairs, hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    subs = ap.add_subparsers(dest="command", required=True)
    f = subs.add_parser("factor")
    f.add_argument("p", type=int); f.add_argument("q", type=int)
    f.add_argument("--certificate")
    c = subs.add_parser("census")
    c.add_argument("path"); c.add_argument("--bounds", nargs=3, type=int)
    args = ap.parse_args()
    try:
        if args.command == "factor":
            cert = json.load(open(args.certificate)) if args.certificate else None
            result = factor(args.p, args.q, cert)
        else:
            pairs, digest = read_pairs(args.path, args.bounds)
            result = {"valid": True, "count": len(pairs), "sha256": digest,
                      "completeness": "not-established-by-row-check"}
        print(json.dumps(result)); return 0 if result["valid"] else 1
    except (ValueError, OSError, UnicodeError) as ex:
        print(json.dumps({"valid": False, "reason": str(ex)})); return 1


if __name__ == "__main__":
    sys.exit(main())
