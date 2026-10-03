# Alerts

## P12 closeout and external region 2 confirmation — 2026-10-03

The external operator reports an exact region 2 census hash and four-cell match. This is a user-relayed attestation; the original withheld file was not inspected locally. The operator did not receive the prediction fingerprint before computation, so prediction-first chronology has local Git evidence but no independent pre-run receipt.

All source, forecast, census and score artifacts remain unchanged. The finite Bernoulli
model wins the prescribed comparison but leaves smaller residuals. No discovery is claimed.
Report author: Chris Miki. PDF: output/pdf/P12_Chris_Miki.pdf. No further computation was launched.

## Vault-S full committed design completed — 2026-10-03

All 40 chunks and the final audit passed. See results/Vault_S2_full/RESULTS.md.
L003 gain over L001: 69.788577 (full primary), 35.487328 (region 2).
External operator confirmation of the original region 2 sealed hash is pending.
Region 1 was not rerun; no model or prediction was changed.

## Vault-S region 2 and powered extension — 2026-10-03

L001, L002, L003 and mandatory N0 predictions frozen in
`predictions/Vault_S2_L001_L002_L003.json`.
SHA-256: `a4fb571f0c65367afec4b02d58dd5b5c6bc269bb252bb2ff4c3c17f40483d641`.
Original sealed subregion: C(10000001,20000000,10000).
Powered primary design: C(10000001,30000000,10000).
The extra band is separately named and is not an operator-sealed vault.
Every primary pair passes expected-gain >=14 in both directions.
At preregistration, neither region 2 nor its extension had been censused.
The SHA was delivered before the user authorized the subsequently completed run.
No region 1 rerun occurred.

## 2026-10-03 — C2 open demonstration, awaiting human review

C(200001,210000,1000) has **312 factors**, independently enumerated and checked.
Census SHA-256: 28029a76b0985fc978acda2baeee8c66dcdeeb58ffdc56ae668333c2cfd6f7cd.
L002 does not beat N0: improvement 1.1391 < 14. This is a finite census result,
not a new factor, validated growth law or operator-confirmed vault result.
Prediction commit: d47690fe9303c28df9572b3442e93481b42d5b53.
Claims and immutable evidence are in claims/ and certificates/.

## Preregistration L002_open_demo

Bounds [200001, 210000, 1000]; law laws/L002.py; SHA-256 `c8c35b53f2e6e396e5218e5938dafaa8e7ed290123dce1172c4179432a0b3755`.
Prediction created before census; awaiting computation.


## 2026-10-03 â€” operator inputs pending

Operator confirmed having GIMPS assignments. Need sanitized active assignment
export, account name, installed client/tool paths and CPU/time cap to select the
discovery band. Dated known-factor and completed-bound exports are needed;
restricted report routes were not scraped. No submission has occurred.

## 2026-10-03 â€” reference MR correction

Supplied reference is preserved byte-for-byte. Acceptance uses thirteen prime
bases through 41 to support the advertised bound. The twelve-base pseudoprime
is a permanent regression test. See SPEC.md and SOURCE.md.

## 2026-10-03 â€” prior overlap and imported archives

Shanksâ€“Kravitz tables and Wagstaff's heuristic overlap this proposal. Novelty
state is overlap-found. Original v0.1/v0.2 source snapshots and ZIP hashes are
retained; historical vault results are not imported into current model work.
