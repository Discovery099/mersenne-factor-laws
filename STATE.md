# State — v0.4 full-design execution authorized, 2026-10-03

L003 is a zero-fit Poisson-binomial multiplicity law using L001's pair means.
Power checks and prediction-only acceleration are implemented and validated.
The fixed sealed region 2 predictions are retained unchanged. L002 versus N0
was underpowered there (10.4732/10.4642 expected deviance gain), so the primary
design was enlarged before commitment to C(10000001,30000000,10000).
L002 versus N0 now has 20.3417/20.3242; L003 versus L001 34.5925/34.4777.
All six primary pairs pass >=14 in both directions. The full pair matrices,
three requested multiplicity cells and numerical checks are in the forecasts.

Prediction: predictions/Vault_S2_L001_L002_L003.json
SHA-256: a4fb571f0c65367afec4b02d58dd5b5c6bc269bb252bb2ff4c3c17f40483d641
Use mf.preregister_vault.registered to audit the Git/source/forecast chain.

The SHA was delivered before computation. The user then explicitly selected
"Run the full committed design". The dedicated ops.vault_run adapter is being
committed before execution. It runs at most two native processes, uses 500000
wide chunks split at the sealed boundary, and checkpoints each engine and each
dual-checker verification. Each invocation has a four-hour wall-time limit;
completed work can be resumed without changing any law or prediction.
Live execution state belongs in runs/Vault_S2_full/progress.json and manifest.json.
Region 1 must not be rerun. See REGISTRATION.md for the scoring scopes.

Validation: 36 test cases checked. The full run passed 35 and found one
incomplete synthetic fixture; the corrected fixture's targeted rerun passed.
No implementation failure remains. Numerical resolution differences are
recorded in predictions/power/*.json. Original exact-checker source hashes
and the v0.3 demonstration remain unchanged.

SOURCE.md records the operator's external region 1 hash-match/scoring statement.
The actual REVIEW_VAULT_S1_L001.md and SEEDS_P12_P13_full_records.md files still
need accessible paths. The launch and P13 brief are different documents.
Track 0 original-semantics reproduction remains pending the full seed records.
The user's subsequent approximate region 1 L003 estimates were recorded as
post-commit external commentary in data/sources/. They did not enter predictions.

Historical L002_open_demo remains a failed, underpowered test; do not retune
or retest that observed band. Novelty remains overlap-found; no new factor,
new theorem, or successful vault outcome is claimed.

GIMPS assignments exist per the operator; sanitized details and future CPU/time
budget remain pending. No assignment request or external submission occurred.
