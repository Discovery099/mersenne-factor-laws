# Supplied archive review — 2026-10-03

`archive/IMPORTS.json` records SHA-256 fingerprints of both complete supplied
ZIPs and every retained source file. Source snapshots were extracted only to
new paths. No ZIP Git configuration/hooks were executed or installed.

v0.1 provides bounded checkers and regression evidence. v0.2 adds a theoretical
L001 predictor, interpolation, partition scoring and sealed-run machinery.
The v0.2 filenames reveal already computed open/vault regions; those regions
are marked as previously observed. Vault census, score and certificate values
were deliberately not read into this model-building workflow. Source code and
law derivation are the parts used. The original ZIPs retain all historical
commits and outputs for a separate operator audit.

Changes delivered here:

| Area | Supplied implementation | Current build |
|---|---|---|
| C proof checker | uint64 inputs | mini-gmp arbitrary integers; Pocklington beyond MR domain |
| MR bound | Corrected 12-base limit in acceptance | 13 bases, expanded proven bound; original reference untouched |
| Windows | WSL suggested; fcntl/resource/statvfs | Native MinGW build, Windows locks/process accounting/launcher |
| Law | v0.2 L001 with NumPy interpolation | Compatible scalar formula plus separately named L002 experiment |
| Scoring | Diagnostic marginals plus disjoint partitions | Marginals plus disjoint dyadic/total scores, provenance gate |
| Preregistration | Supplied historical chain | New git chain; no retroactive claim over supplied results |
| Checkpoints | Source and chunk hashes | Also contiguous bound coverage, counts, binaries and process locks |
| Track 0 | Specification gap noted | Gap retained; explicit generic oracles and boundary tests supplied |
| Discovery | Operator instructions | Assignment validation, budgeted ranking, paired A/B and verified packages |

Archive formulas and numeric intervals are user-supplied research, not
automatically accepted theorems. No old certificate is rewritten or relabelled
as newly discovered. API/schema changes are intentional and documented; this
is a standalone v0.3 build, not a byte-compatible replacement for old scripts.
