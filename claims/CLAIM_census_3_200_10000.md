# census_3_200_10000

Exact finite statement: C(3,200,10000) contains 46 pairs.
Claim level: C2 finite enumeration, awaiting human review; fixed benchmarks also C0 reproduction.

Census SHA-256: `4c37caf1201fe83d3c9b44d05b9c2770b9e09c9c8ef631c4d957ceb6bf182d6c`.
Certificate: `certificates/census_3_200_10000_4c37caf1201f.json`. Artifact SHA-256: `ee6c9cc02036c34aff3e2d07f577d45bca0736d5abcfff613076724ff194815a`.

Evidence: independent p-first and k-first exhaustive C algorithms; exact Python
and C/mini-gmp membership/primality checks; full replay in final verification.
Canonical representation is sorted unique (p,k), so no symmetry minimization
is relevant. Reproduce with `python -m ops.verify`.

These are small-k finite census values, not newly credited GIMPS factors or a
claim of beating a published record. Prior overlap: Shanks–Kravitz and Wagstaff;
see SOURCE.md (accessed 2026-10-03). No claim of novel tables is made.
