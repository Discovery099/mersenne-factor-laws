# checker_reference.py -- P12 Mersenne factor laws: seed checker (exact integer arithmetic only)
import hashlib
from math import gcd

BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
MR_LIMIT = 3317044064679887385961981  # these 12 bases are a proof of primality below this bound

def is_prime_mr(n):
    """Deterministic Miller-Rabin, exact for n < MR_LIMIT."""
    if n < 2:
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

def pocklington_verify(n, F_primes, witnesses):
    """n-1 = F*R with F built from F_primes {r: e}; F*F > n; for each r a witness a_r with
    a_r^(n-1) = 1 (mod n) and gcd(a_r^((n-1)/r) - 1, n) = 1. Every r must itself be prime (MR)."""
    F = 1
    for r, e in F_primes.items():
        if not (r < MR_LIMIT and is_prime_mr(r)):
            return False, f"F-prime {r} not proven"
        F *= r ** e
    if (n - 1) % F or F * F <= n:
        return False, "F does not divide n-1 or F^2 <= n"
    for r in F_primes:
        a = witnesses[r]
        if pow(a, n - 1, n) != 1 or gcd(pow(a, (n - 1) // r, n) - 1, n) != 1:
            return False, f"witness fails for r={r}"
    return True, "Pocklington certificate valid"

def k_class_ok(p, k):
    """Known law: q = 2kp+1 = +-1 (mod 8)  <=>  k in {0,3} (mod 4) if p = 1 (mod 4), k in {0,1} (mod 4) if p = 3 (mod 4)."""
    return (k % 4 in (0, 3)) if p % 4 == 1 else (k % 4 in (0, 1))

def verify_factor(p, q, cert=None):
    """Accept iff q is a PRIME divisor of M_p = 2^p - 1 (p an odd prime)."""
    if p < 3 or not is_prime_mr(p):
        return False, "p is not an odd prime"
    if q < 3 or (q - 1) % (2 * p):
        return False, "q is not of the form 2kp+1"
    if q % 8 not in (1, 7):
        return False, "q is not +-1 mod 8"
    if pow(2, p, q) != 1:
        return False, "q does not divide M_p"
    k = (q - 1) // (2 * p)
    if k <= 2 * p + 1:
        return True, f"prime factor, k={k} (prime by the k <= 2p+1 lemma)"
    if q < MR_LIMIT:
        return (True, f"prime factor, k={k} (deterministic MR)") if is_prime_mr(q) else (False, f"composite divisor, k={k}")
    if cert is None:
        return False, "q >= MR_LIMIT needs a Pocklington certificate"
    ok, msg = pocklington_verify(q, *cert)
    return (True, f"prime factor, k={k} ({msg})") if ok else (False, msg)

def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

def census(P_lo, P_hi, K):
    """All (p, k) with p prime in [P_lo, P_hi], 1 <= k <= K, q = 2kp+1 a prime divisor of M_p."""
    out = []
    for p in primes_upto(P_hi):
        if p < max(P_lo, 3):
            continue
        for k in range(1, K + 1):
            if not k_class_ok(p, k):
                continue
            q = 2 * k * p + 1
            if pow(2, p, q) == 1 and (k <= 2 * p + 1 or is_prime_mr(q)):
                out.append((p, k))
    return out

def canonical_hash(pairs):
    text = "".join(f"{p} {k}\n" for p, k in sorted(pairs))
    return hashlib.sha256(text.encode()).hexdigest()

def commit(prediction_bytes):
    return hashlib.sha256(prediction_bytes).hexdigest()

if __name__ == "__main__":
    print("M11 factors 23, 89:", verify_factor(11, 23), verify_factor(11, 89))
    print("M29 factors:", [verify_factor(29, q)[0] for q in (233, 1103, 2089)])
    print("2047 = 23*89 rejected as composite:", verify_factor(11, 2047))
    print("mutations rejected:", not verify_factor(11, 25)[0], not verify_factor(13, 53)[0], not verify_factor(15, 31)[0])
    print("Pocklington on q=89 (p=11):", pocklington_verify(89, {2: 3, 11: 1}, {2: 3, 11: 3}))
    print("bad Pocklington witness rejected:", not pocklington_verify(89, {2: 3, 11: 1}, {2: 2, 11: 3})[0])
    c = census(3, 200, 10000)
    print("census p<=200, k<=10000:", len(c), "factors; k-mod-4 law holds:", all(k_class_ok(p, k) for p, k in c))
    print("census sha256[:16]:", canonical_hash(c)[:16])
    print("smallest-k factor of M43, M47, M53:", [min(k for p, k in c if p == t) for t in (43, 47, 53)])
    print("commit('law: test') =", commit(b"law: test")[:16])
