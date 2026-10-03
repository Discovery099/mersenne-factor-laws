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
