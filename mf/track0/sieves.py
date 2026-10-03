from math import lcm


def validate(N, exclusions):
    if not 0 <= N <= 200 or any(m < 1 or not 0 <= r < m for m, r in exclusions):
        raise ValueError("oracle requires N<=200 and normalized residue classes")


def direct(N, exclusions):
    validate(N, exclusions)
    return [n for n in range(1, N + 1) if all(n % m != r for m, r in exclusions)]


def sieve(N, exclusions):
    validate(N, exclusions)
    allowed = [True] * (N + 1)
    for m, r in exclusions:
        for n in range(r or m, N + 1, m):
            allowed[n] = False
    return [n for n in range(1, N + 1) if allowed[n]]


def project_cache(old_modulus, new_modulus, entries, projection):
    """An entry maps an old residue to a set of observed truth values.

    Conflicting observations remain ambiguous rather than being silently reused.
    """
    if old_modulus < 1 or new_modulus % old_modulus or len(projection) != new_modulus:
        raise ValueError("not a refinement")
    if any(projection[r] != r % old_modulus for r in range(new_modulus)):
        raise ValueError("projection does not preserve residue meaning")
    if any(r not in range(old_modulus) or not values or not set(values) <= {True, False} for r, values in entries.items()):
        raise ValueError("invalid residue cache")
    clean, ambiguous = {}, {}
    for r in range(new_modulus):
        values = set(entries.get(projection[r], {False, True}))
        if len(values) == 1:
            clean[r] = next(iter(values))
        else:
            ambiguous[r] = sorted(values)
    return {"clean": clean, "ambiguity_classes": ambiguous}
