# Operator discovery handoff

The operator has confirmed having GIMPS assignments; details and resource caps
are pending. No credentials, invented assignments, submissions or new-factor
claims are included. Private exports belong in `discovery/private/` or
`data/private/` (git ignored).

Assignment JSON: `[{"assignment_id":"...","account":"...","p":...,
"method":"pm1","status":"assigned","source":"export or URL",
"expires_at":"2026-11-01T00:00:00+00:00","completed_B1":0,"completed_B2":0}]`.
Each candidate has assignment_id, method, B1, B2 (and curves for ECM),
cpu_seconds, expected_new_factors, prediction_source_sha256, and an explicit
selection_model: pm1-smoothness, ecm-curve-probability or tf-bit-interval.
These expectations need calibration against the installed tool and completed
work. Extrapolating L002's small-k census to discovery is not validated.

`python -m discovery.plan --assignments discovery/private/assignments.json
--candidates discovery/private/candidates.json --operator NAME --cpu-hours 1
--output discovery/private/allocation.json` produces a reviewable immutable
allocation. `matched_ab` freezes method/bounds-matched pairs. Prime95 default
bounds must be captured from the installed version; they are not guessed.

`ecm_command` prepares a GMP-ECM argument list with saved residues and standard
input. Execution and PrimeNet submission remain with the operator's configured
client until its paths/version, assignments and resource budget are supplied.
GPU TF and Prime95 worktodo syntax depend on the actual installed tool.

Result packaging: `python -m discovery.results P Q --assignment ROW.json
--known KNOWN.json --operator NAME --output certificates/factor_ID.json`.
KNOWN contains source, accessed_at (timezone-aware ISO timestamp), and factors
as integer [p,q] pairs. Add `--certificate CERT.json` for Pocklington and
`--receipt RECEIPT.json` for operator-supplied credit evidence. Both independent
checkers must accept. Absence from a supplied export is not proof that no one
else has found the factor since that export. No result is labelled a credited
discovery until its external receipt and freshness are confirmed.
