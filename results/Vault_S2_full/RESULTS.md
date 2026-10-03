# Vault-S region 2 and supplementary band — local results

The fixed prediction SHA-256 is `a4fb571f0c65367afec4b02d58dd5b5c6bc269bb252bb2ff4c3c17f40483d641`.
Prediction commit: `0a3a73847f3f533dae5fcface0c0abd5099801cb`.
Both independent engines agree on every chunk. Both factor checkers accepted every pair.
Region 1 was not rerun. Operator comparison with the original sealed region 2 hash is pending.

## Original sealed region 2

Bounds: p in [10000001, 20000000], k <= 10000.
Census SHA-256: `4cd1542dbe1264ef0510b43bc165cc1a761ef24b3e42ba65118406e65bde5415`.

| Cell | Observed | N0 | L001 | L002 | L003 |
| --- | ---: | ---: | ---: | ---: | ---: |
| total | 250614 | 251136.303437 | 250537.121057 | 250585.127068 | 250537.121057 |
| at_least_one | 206852 | 202520.293464 | 205109.160160 | 202176.161812 | 206220.257925 |
| at_least_two | 38568 | 41263.453767 | 39559.377939 | 41105.624858 | 38876.163793 |
| maximum | 5 | 6.762721 | 6.129575 | 6.753858 | 5.992731 |

| Law | Full-summary deviance | Gain over N0 | Power eligible in this scope | Eligible win (gain >=14) |
| --- | ---: | ---: | --- | --- |
| L001 | 76.929779 | 235.683718 | True | True |
| L002 | 299.531919 | 13.081578 | False | False |
| L003 | 41.442450 | 271.171046 | True | True |

L003 gain over L001: **35.487328** (threshold 14).
Their factor-count expectations are identical; this contrast comes entirely from multiplicity.

## Enlarged primary design

Bounds: p in [10000001, 30000000], k <= 10000.
Census SHA-256: `478aef5d3b6d09952fddef0189dc985ecec117f7ddff41c3769307ff8e9c577b`.

| Cell | Observed | N0 | L001 | L002 | L003 |
| --- | ---: | ---: | ---: | ---: | ---: |
| total | 487025 | 488561.488419 | 487437.085618 | 487490.328632 | 487437.085618 |
| at_least_one | 402988 | 394974.546798 | 399965.072824 | 394301.923840 | 402101.603433 |
| at_least_two | 74233 | 79594.347184 | 76295.240105 | 79289.480099 | 74972.029195 |
| maximum | 6 | 7.036322 | 6.296694 | 7.027659 | 6.173554 |

| Law | Full-summary deviance | Gain over N0 | Power eligible in this scope | Eligible win (gain >=14) |
| --- | ---: | ---: | --- | --- |
| L001 | 97.667317 | 484.547087 | True | True |
| L002 | 538.633081 | 43.581323 | True | True |
| L003 | 27.878740 | 554.335664 | True | True |

L003 gain over L001: **69.788577** (threshold 14).
Their factor-count expectations are identical; this contrast comes entirely from multiplicity.

## Supplementary band (descriptive)

Bounds: p in [20000001, 30000000], k <= 10000.
Census SHA-256: `57e1388a33a8e248154ffedbc83ce229cb5fba90c35729fcad6d7783716f7c94`.

| Cell | Observed | N0 | L001 | L002 | L003 |
| --- | ---: | ---: | ---: | ---: | ---: |
| total | 236411 | 237425.184983 | 236899.964561 | 236905.201564 | 236899.964561 |
| at_least_one | 196136 | 192454.253334 | 194855.912663 | 192125.762028 | 195881.345509 |
| at_least_two | 35665 | 38330.893418 | 36735.862166 | 38183.855242 | 36095.865402 |
| maximum | 6 | 6.666198 | 6.071199 | 6.657777 | 5.927603 |

| Law | Full-summary deviance | Gain over N0 | Power eligible in this scope | Eligible win (gain >=14) |
| --- | ---: | ---: | --- | --- |
| L001 | 75.105123 | 241.720561 | True | True |
| L002 | 286.338447 | 30.487238 | False | False |
| L003 | 40.684930 | 276.140754 | True | True |

L003 gain over L001: **34.420193** (threshold 14).
Their factor-count expectations are identical; this contrast comes entirely from multiplicity.

## Interpretation and limits

Scores use the frozen complete summary, including maximum once. These overlapping
cells form a composite diagnostic, not an independent likelihood ratio or a p-value.
A lower L003 score supports its finite Bernoulli correction relative to L001 on
these cells; it does not prove independence of actual Mersenne factors or establish novelty.
On the enlarged design, observed minus L003 predicted is +886.396567 for >=1
and -739.029195 for >=2. A relative win does not establish calibrated goodness
of fit or justify treating every remaining residual as ordinary noise.
The original region 2 N0/L002 comparison remains underpowered, regardless of its realized gain.
No law may be refitted and retested on these now-observed bands.

Native engine CPU time recorded: 1.023741 CPU-hours.
Checker, Python aggregation, build, and audit CPU time are not included in that figure.
