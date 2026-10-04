# Operator review: P12 Vault-S region 1 and law L001

Reviewed 3 October 2026 against the sealed values. These were computed on 2 October with independent code (`mcensus.c`), before the task file was issued.

## 1. Census hash: confirmed exactly

| Agent Sealed   |                                                                    |               |
| -------------- | ------------------------------------------------------------------ | ------------- |
| Region         | p ∈ [10⁶, 10⁷], k ≤ 10⁵                                            | same          |
| Census factors | 307,582                                                            | **307,582**   |
| Census SHA-256 | `119c03fad32551ef1d7abf2c8e66db6a4b344004948316e7091c0605e73a6a47` | **identical** |

The five earlier certificates were also recomputed with the independent code, and every count and hash matches: 46, 215, 520, 5,773 and 138.

**Preregistration check.**

- `predictions/vaultS.json` (SHA-256 `edec3781…`) is byte-identical to its version in commit `2c87791` (10:04).
- That commit contains no region-1 census; the census and scores arrive in `b1d0925` (10:19).

## 2. Official score (computed independently from the sealed summaries)

Poisson deviance per preregistered summary group:

| Group D(L001) D(N0) Gain         |           |            |            |
| -------------------------------- | --------- | ---------- | ---------- |
| total                            | 0.00      | 1.21       | 1.21       |
| dyadic k buckets (17 cells)      | 13.29     | 14.58      | 1.29       |
| exponents with ≥ 1 / ≥ 2 factors | 19.05     | 147.05     | **128.00** |
| k mod 3                          | 3.32      | 4.11       | 0.78       |
| k mod 4                          | 3.52      | 5.24       | 1.72       |
| k mod 5                          | 10.99     | 11.73      | 0.73       |
| k mod 8                          | 8.26      | 11.07      | 2.81       |
| k mod 12                         | 13.58     | 15.00      | 1.42       |
| **all preregistered cells**      | **72.01** | **209.98** | **137.97** |

**Verdict.**

- L001 passes the task's threshold (gain ≥ 14 with 0 fitted parameters) by the letter of Section 3.4. It reproduces your own 138.15 to rounding.
- The total is predicted to within 7 factors out of 307,582.
- As you said yourself, almost all of the gain (128 of 138) comes from the multiplicity cells. On the count partitions (buckets and residue classes), L001 and N0 are statistically indistinguishable, and both fit within Poisson noise.
- L001 is Wagstaff (1983), Eq. (1), so this is an **out-of-sample confirmation of a known law, not a new law**.
- Record it as: *C2 census confirmed by sealed hash; L001 (prior art) validated on sealed data; no novelty.*

## 3. The one real lead: multiplicity (Q4)

| Observed L001 N0           |         |           |           |
| -------------------------- | ------- | --------- | --------- |
| exponents with ≥ 1 factor  | 240,726 | 239,185.7 | 236,588.9 |
| exponents with ≥ 2 factors | 56,673  | 57,396.1  | 58,761.5  |

- **The residual pattern.** L001 gets the total right, but under-predicts "≥ 1" by about 1,540 (≈ 3σ) and over-predicts "≥ 2" by about 723 (≈ 3σ).
- **Why it matters.** Factors of the same M_p look **less clustered than independent Poisson**. Unmodelled heterogeneity between exponents would push the other way (more clustering). So either the per-exponent means μ_p in L001 vary more than they should, or there is real repulsion between factors of one exponent.
- **Is it new?** This is the only residual in region 1 that looks structural. Whether it is new depends on the prior-art check (look for "dispersion" or "number of prime factors" of Mersenne numbers, and the Erdős–Kac-type literature for shifted primes).

**Suggested next step.**

1. Derive a multiplicity law L002 (zero or few fitted parameters, fitted only on open cells).
2. Commit its predictions for **Vault-S region 2** (p ∈ (10⁷, 2·10⁷], k ≤ 10⁴), which is still untouched and held sealed by the operator, and which includes the ≥ 1 / ≥ 2 / maximum cells.
3. Then compute region 2.

L001 must not be edited on regions already seen.
