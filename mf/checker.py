"""Frozen acceptance code. Deliberately independent of every search module."""
import argparse
import hashlib
import json
import re
import sys
from math import gcd, isqrt
from pathlib import Path

MR_LIMIT = 3317044064679887385961981
BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


def is_prime(n):
    if type(n) is not int or n < 2 or n >= MR_LIMIT:
        return False
    for r in BASES:
        if n % r == 0:
            return n == r
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def pocklington(n, certificate):
    if type(n) is not int or n < 3 or not isinstance(certificate, list) or not 1 <= len(certificate) <= 128:
        return False
    seen, F = set(), 1
    for row in certificate:
        if not isinstance(row, (list, tuple)) or len(row) != 3:
            return False
        r, e, a = row
        if any(type(v) is not int for v in row) or r in seen:
            return False
        if not is_prime(r) or not 1 <= e <= n.bit_length() or not 1 < a < n:
            return False
        seen.add(r)
        F *= r ** e
        if F > n - 1 or (n - 1) % F:
            return False
        if pow(a, n - 1, n) != 1 or gcd(pow(a, (n - 1) // r, n) - 1, n) != 1:
            return False
    return F * F > n


def k_class_ok(p, k):
    return k % 4 in ((0, 3) if p % 4 == 1 else (0, 1))


def verify_factor(p, q, certificate=None):
    def bad(reason):
        return {"valid": False, "reason": reason}
    if type(p) is not int or p < 3 or not is_prime(p):
        return bad("exponent is not a proven odd prime")
    if type(q) is not int or q < 3 or (q - 1) % (2 * p):
        return bad("factor has invalid form")
    k = (q - 1) // (2 * p)
    if q % 8 not in (1, 7) or pow(2, p, q) != 1:
        return bad("residue or divisibility check failed")
    if certificate is not None:
        if not pocklington(q, certificate):
            return bad("invalid Pocklington certificate")
        method = "Pocklington"
    elif k <= 2 * p + 1:
        method = "L2"
    elif is_prime(q):
        method = "deterministic-MR-13"
    else:
        return bad("composite or primality certificate required")
    return {"valid": True, "p": p, "q": q, "k": k, "primality_method": method}


def primes_upto(n):
    if type(n) is not int or n < 0:
        raise ValueError("prime-sieve bound must be nonnegative")
    s = bytearray(b"\x01") * (n + 1)
    s[:min(2, n + 1)] = b"\x00" * min(2, n + 1)
    for r in range(2, isqrt(n) + 1):
        if s[r]:
            start = r * r
            s[start:n + 1:r] = b"\x00" * ((n - start) // r + 1)
    return [i for i, value in enumerate(s) if value]


def validate_bounds(lo, hi, K):
    if any(type(x) is not int for x in (lo, hi, K)) or not 0 <= lo <= hi or K < 1:
        raise ValueError("require 0 <= lo <= hi and K >= 1")
    if 2 * hi * K + 1 >= 2 ** 63 or hi > 100_000_000 or K > 10_000_000:
        raise ValueError("bounds exceed the declared engine resource/domain limits")


def canonical_bytes(pairs):
    return "".join(f"{p} {k}\n" for p, k in sorted(pairs)).encode("ascii")


def census_hash(pairs):
    return hashlib.sha256(canonical_bytes(pairs)).hexdigest()


def parse_census(data):
    if isinstance(data, bytes):
        data = data.decode("ascii")
    pairs = []
    for line in data.splitlines():
        if not re.fullmatch(r"[0-9]+ [0-9]+", line):
            raise ValueError("census lines must contain exactly two nonnegative integers")
        p, k = map(int, line.split(" "))
        if k < 1:
            raise ValueError("k must be positive")
        pairs.append((p, k))
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate census pair")
    if data.encode("ascii") != canonical_bytes(pairs):
        raise ValueError("census must be sorted canonical ASCII with exactly one newline per pair")
    return pairs


def verify_census(pairs, bounds=None):
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate census pair")
    if bounds:
        validate_bounds(*bounds)
    for p, k in pairs:
        if bounds and not (bounds[0] <= p <= bounds[1] and 1 <= k <= bounds[2]):
            raise ValueError("pair outside declared census bounds")
        result = verify_factor(p, 2 * p * k + 1)
        if not result["valid"]:
            raise ValueError(f"invalid pair {p},{k}: {result['reason']}")
    return {"valid": True, "count": len(pairs), "sha256": census_hash(pairs),
            "claim": "membership-only; completeness needs independent enumeration"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("factor")
    f.add_argument("p", type=int)
    f.add_argument("q", type=int)
    f.add_argument("--certificate", type=Path)
    c = sub.add_parser("census")
    c.add_argument("path")
    c.add_argument("--bounds", nargs=3, type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "factor":
            cert = json.loads(args.certificate.read_text()) if args.certificate else None
            result = verify_factor(args.p, args.q, cert)
        else:
            data = sys.stdin.buffer.read() if args.path == "-" else Path(args.path).read_bytes()
            result = verify_census(parse_census(data), args.bounds)
    except (ValueError, OSError, TypeError, OverflowError) as exc:
        result = {"valid": False, "reason": str(exc)}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
