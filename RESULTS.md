# Verified build results — v0.3

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
