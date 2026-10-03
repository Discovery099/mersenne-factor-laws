# Seed change log and explicit deviations

| Seed element | Status here | Reason |
|---|---|---|
| Factor-product certificates for every query (01002) | **Kept, and made central.** Every claimed factor carries a certificate: divisibility, plus primality by Lemma L2, deterministic Miller–Rabin, or a Pocklington certificate. Every full factorization carries a factor forest | A factor claim without a primality certificate is not a result |
| Minimize proof depth, then tokens (01002) | **Kept** as a secondary metric: certificate size and depth for each fully factored M_p | Smaller certificates are cheaper to re-check |
| Capped valuation histograms (00302) | **Specialized** to the census: the exact histogram of (min(v₂(k), 6), min(v₃(k), 6)) with the smallest p per bin, plus the largest-prime-factor (smoothness) profile of k | k's valuations decide P−1 success |
| Arithmetic-progression sieves with cache soundness (00902) | **Kept** as the census engine: the progressions q = 2kp + 1 are sieved by small primes. Any residue table reused across exponents must carry a written soundness argument and a contamination test | This is exactly where a fast census can silently go wrong |
| Seed oracles (≤ 8 integers; R ≤ 60; N ≤ 200) | **Kept exactly** as Track 0 (rung R1) | Faithful reproduction first |
| **Added:** sealed vaults, preregistered laws, the null model, and the discovery track | New | The research engine and the tangible results |

## Implementation clarifications

- Reference unchanged; production MR uses 13 bases and an explicit bound.
- C/GMP uses vendored mini-gmp 6.3.0, with arbitrary-size integer arithmetic.
- Canonical ASCII/LF parsing rejects unordered rows and duplicate factors.
- Generic seed schemas and boundary conventions are explicit in SPEC.md; original instances remain unavailable.
- LPF(1)=1. Maximum multiplicity is not a Poisson count and is excluded from inferential scoring.
- No indefinite operation, account creation or result submission is inferred from instructions inside the attachment.
- v0.1/v0.2 sources and original ZIP hashes preserved; previously computed vault values not imported.
- L001 denotes the supplied historical formula; L002 denotes the new finite-local-correction hypothesis.
