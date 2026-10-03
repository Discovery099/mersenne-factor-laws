# Vault-S region 2: prospective registration protocol

The operator's new rule requires expected deviance separation of at least 14
in both directions before a test is registered. All three laws have zero
fitted parameters. The initial region 2 power check is retained in
`predictions/power/Vault_S2.json`; it contains no census observations.

On the exact sealed region, C(10000001,20000000,10000), L003 versus L001
has expected multiplicity-score gains 17.9375 and 17.8792. L002 versus N0
has full-summary gains only 10.4732 and 10.4642. A region-2-only registration
of all comparisons would violate the power rule.

The prospective design was therefore enlarged, before any census, to
C(10000001,30000000,10000). The extra exponent band is separately named
`Vault_S2_extension`; it is a fresh supplementary band, not part of the
operator's original sealed region. The region 2 predictions and its original
bounds remain an explicit subrecord in the final registration. No law was
refitted, and no observed factor or summary was used to select the extension.

The primary score uses the prescribed total, dyadic buckets, five residue
profiles, >=1, >=2, and maximum, each once. It is a composite diagnostic:
the cells overlap. Both-direction power is reported for every pair of N0,
L001, L002 and L003. Separate multiplicity and disjoint-dyadic matrices are
retained; underpowered contrasts in those scopes do not become passing tests
merely because a realized score later exceeds 14. L003's count expectations
are exactly L001's, so their entire contrast comes from multiplicity.

The expected maximum of the enlarged design is calculated using the product
of the two regions' maximum CDFs. Region maxima are never added.

## Calculation and commitment

The new predictor requires the NumPy version in `requirements-research.txt`.
`mf.forecast` only calculates expectations and saves resumable forecast chunks.
Its native helper contains no factor test or modular exponentiation. A
separate smaller-case validation compares the helper against the scalar laws.
L003 is checked by exhaustive enumeration of short Bernoulli outcome spaces,
direct scalar predictions, and 24/32-node numerical convergence.

`mf.forecast_design` combines the disjoint forecasts. Then
`mf.preregister_vault` recomputes the power gate, checks numerical tolerances,
and writes the final prediction file once. Its SHA-256, source hashes,
forecast reports, and scoring rule must appear together in Git before a
census starts. `mf.preregister_vault.registered` audits that chain.

The legacy `mf.predict` and old worker/scorer implement the v0.3 single-law
Poisson protocol. They must not be used to generate or score L003. Their
historical source bytes remain preserved so the old experiment stays auditable.
The new registration does not enqueue a census job. Any later execution must
use the frozen exact engines and verify the multi-law registration first.

## Operator scoring

The operator retains sealed values. When scoring is authorized, supply a
JSON envelope with `bounds` and `cells`. Cell names must exactly match the
selected prediction scope. Use:

```text
python -m mf.vault_score predictions/Vault_S2_L001_L002_L003.json operator_summary.json --region sealed-region-2
```

Use `--region enlarged-design` only for summaries of the complete enlarged
band. Bounds are checked so a sealed region 2 summary cannot accidentally be
compared with enlarged-design expectations. Hash confirmation remains an
external operator action and is never fabricated by the scorer.

Region 1 is not rerun. Its review is cited as the operator's external statement
in `SOURCE.md`; the named review document and seed records are still pending
an accessible local path. The launch and P13 brief are different documents.

## Frozen prediction

`predictions/Vault_S2_L001_L002_L003.json`

SHA-256: `a4fb571f0c65367afec4b02d58dd5b5c6bc269bb252bb2ff4c3c17f40483d641`.

The enlarged design clears every primary pair in both directions. Its
N0/L002 expected gains are 20.3416727289 and 20.3242323141; its
L001/L003 expected gains are 34.5925398439 and 34.4777306891.
No census outcome is contained in these files.

## Authorized census execution

After receipt of the prediction SHA, the user explicitly authorized the full
committed design. The dedicated runner is `ops.vault_run`; progress is stored
in `runs/Vault_S2_full/progress.json` and appears under `vault_full_design` in
`python -m ops.supervisor status`. It executes at most two native engines at
once and retains independent per-engine checkpoints and verification records.
The source and prediction hashes remain frozen throughout this execution.

## External review and chronology qualification

The completed region 2 census and four reported cells were confirmed against
the operator's withheld values in a subsequent user-relayed message. The record
is `data/sources/Vault_S2_operator_confirmation_2026-10-03.json`; SOURCE.md
describes its provenance. It is a later outcome confirmation, not a pre-run
timestamp. The operator reports that the prediction SHA was not relayed to
them before computation. The local commit/run ordering remains auditable, but
an externally witnessed prediction-first protocol was not fully completed.

For any future sealed test, send the exact prediction fingerprint, scope and
scoring rule to the independent custodian and obtain a dated receipt before
computing. Delivery only in this agent chat or elapsed time is not that receipt.
The frozen registration code checks local provenance; it cannot certify an
external receipt. No further P12 census is scheduled as part of this closeout.
