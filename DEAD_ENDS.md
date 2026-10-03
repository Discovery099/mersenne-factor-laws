# Retained failures and rejected assumptions

* The supplied reference's twelve bases are insufficient for its stated bound.
  Counterexample 318665857834031151167461 passes them. Production adds base 41.
* Novelty of exact k tables / L001 formula: direct prior overlap found.
* An all-summary deviance is not automatically an independent likelihood ratio:
  total, buckets and residues overlap. Report disjoint partitions separately.
* Arbitrary-size C/GMP was missing in the supplied build; resolved using pinned
  mini-gmp, with tests above the deterministic-MR range.
* Downloading a guessed third-party GMP tag returned 404. Used official GNU
  release archive instead; file and archive hashes are recorded.

Failed statistical hypotheses will be appended with immutable residual paths.

## L002-OPEN — 2026-10-03

On the preregistered cell C(200001,210000,1000), the exact count is 312.
L002 predicted 335.943583334915; N0 predicted 336.8895263286887.
Composite deviance improvement: 1.139065174121498, below the required 14.
Disjoint dyadic improvement: 0.13905506662327483; total-only improvement:
0.13730878692371107. L002 does not beat N0 by the prescribed criterion.
Frozen residuals: runs/L002_open_demo/score.json. Prediction SHA-256:
c8c35b53f2e6e396e5218e5938dafaa8e7ed290123dce1172c4179432a0b3755.
Do not edit L002 and retest on this same cell. Any revised law needs a new band.
