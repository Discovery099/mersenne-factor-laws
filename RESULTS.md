# Verified results — v0.4

P12 closeout by **Chris Miki**: [paper-style PDF](output/pdf/P12_Chris_Miki.pdf), [editable LaTeX](reports/P12_Chris_Miki.tex).

The full committed design C(10000001,30000000,10000) is complete. All 40 chunks
were independently enumerated by both C engines and accepted by the Python
and C factor checkers. The subsequent artifact audit verified coverage,
prediction chronology, frozen sources, hashes, certificate pairs and an
independent summary recount. Region 1 was not rerun.

Prediction SHA-256: `a4fb571f0c65367afec4b02d58dd5b5c6bc269bb252bb2ff4c3c17f40483d641`.
Prediction commit: `0a3a73847f3f533dae5fcface0c0abd5099801cb`.

| Scope | Inclusive p range | K | Factors | Census SHA-256 |
|---|---|---:|---:|---|
| sealed_region_2 | 10000001–20000000 | 10000 | 250,614 | `4cd1542dbe1264ef0510b43bc165cc1a761ef24b3e42ba65118406e65bde5415` |
| extension | 20000001–30000000 | 10000 | 236,411 | `57e1388a33a8e248154ffedbc83ce229cb5fba90c35729fcad6d7783716f7c94` |
| enlarged_design | 10000001–30000000 | 10000 | 487,025 | `478aef5d3b6d09952fddef0189dc985ecec117f7ddff41c3769307ff8e9c577b` |

The primary design is the union of the first two rows; these are overlapping
reports of one run, not three independent replications. The extension was
preregistered but is not an operator-sealed vault. The external operator reports an exact region 2 census hash and four-cell match. This is a user-relayed attestation; the original withheld file was not inspected locally. The operator did not receive the prediction fingerprint before computation, so prediction-first chronology has local Git evidence but no independent pre-run receipt.

| Law | Full primary composite deviance | Gain over N0 | Threshold 14 met |
|---|---:|---:|---|
| L001 | 97.667317 | 484.547087 | True |
| L002 | 538.633081 | 43.581323 | True |
| L003 | 27.878740 | 554.335664 | True |

L003 improves over L001 by **69.788577** on the enlarged primary
design and **35.487328** on the original region 2. Their factor-count
expectations coincide, so this contrast comes entirely from multiplicity.
The original region 2 N0/L002 comparison remains underpowered and has no
standalone confirmatory verdict.

These scores are the prescribed overlapping-cell diagnostic, not calibrated
p-values or a proof of independence. The result evaluates the standard finite
Bernoulli correction; no new theorem, factor discovery or novelty is claimed.
Do not refit laws and retest them on these now-observed bands.

Detailed predictions, multiplicity cells, alternate score groups and audit:
[Vault-S results](results/Vault_S2_full/RESULTS.md),
[audit JSON](results/Vault_S2_full/audit.json).
Recorded native engine work: 1.023741 CPU-hours, excluding checkers, build,
aggregation, prediction and audit work. The supervisor has completed and stopped.

Validation history: 36 research/build test cases checked (35 in the full run,
then the corrected incomplete fixture in a targeted passing rerun); four new
execution-adapter tests and one independent-recount test passed. The actual
census also passed all dual-engine and dual-checker validations above.

## Historical v0.3 build results

The following is the retained earlier build report; its pending-work statements
describe that earlier stage. The v0.4 status above supersedes them.

26 test groups pass. All 5 immutable census certificates were
rechecked with both factor checkers and both exhaustive engines.

| Inclusive p range | K | Factors | Census SHA-256 |
|---|---:|---:|---|
| 10000–20000 | 1000 | 520 | `ec51f40e56e125c65a1107f8147af63e6633752d34dec4cb5fc3320eee77a9ce` |
| 1000–3000 | 20000 | 215 | `d0e00ccf55de45e684dcb44dfde662e959a9d4a93ef43cc09949e329bdfbe943` |
| 200001–210000 | 1000 | 312 | `28029a76b0985fc978acda2baeee8c66dcdeeb58ffdc56ae668333c2cfd6f7cd` |
| 3–100000 | 10000 | 5773 | `6de6b2ac9a1b8c3d3b36ae90dc04f4c3973dc62d920183a6f4071c3041a8b2ec` |
| 3–200 | 10000 | 46 | `4c37caf1201fe83d3c9b44d05b9c2770b9e09c9c8ef631c4d957ceb6bf182d6c` |

## Prediction-before-computation demonstration

L002 and N0 were committed in d47690fe9303c28df9572b3442e93481b42d5b53
before C(200001,210000,1000) was computed by the supervisor. Predictions were
335.943583334915 (L002) and 336.8895263286887 (N0); observed count: 312.
The composite deviance improvement is 1.139065174121, below 14. The
disjoint dyadic improvement is 0.139055066623.
**L002 failed the stipulated criterion.** Predictions, residuals and sources
are retained. No revised model may reuse this cell as a fresh test.

N0 sanity: 507.62974052227594 predicted versus 520 observed. Directed-rounding
Euler-product bounds establish C2=0.660162 and 2C2=1.320324 to six decimals.
Those constants do not prove a Mersenne distribution law.

## Scope

R0 infrastructure is implemented and tested, including arbitrary-size C
Pocklington checking. Generic Track 0 oracles pass at 8/60/200 limits; faithful
original seed reproduction remains unresolved. Full open grid, operator-sealed
confirmation, discovery calibration and GIMPS credit are pending. Historical
v0.2 vault results are preserved in the supplied ZIP, not re-certified here.

The problem asks for exact Mersenne factor censuses and predictive laws tested
on data withheld before computation. This build establishes the finite C2
values above, reproduces known benchmarks at C0, and completes an auditable
open-cell prediction experiment. It was checked with independent arithmetic,
exhaustive enumeration, adversarial tests and fresh certificate replays. It
could support reliable future research and measured discovery allocation. It
does not establish a new theorem, successful law or credited new factor. The
single next experiment with the most information value is a committed L001
versus N0 comparison on a new band, C(220001,225000,1000), before computation.
