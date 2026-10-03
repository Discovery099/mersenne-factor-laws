# Limits and pending inputs

1. Full open grid, both operator-confirmed Vault-S scores, rolling vaults and
   a credited GIMPS discovery are research milestones, not completed outcomes.
   No weeks-long campaign has been launched without an explicit CPU/time cap.
2. v0.2 contains historical vault results. They were not imported into model
   development here; any later audit must preserve their original commitments.
3. The original seed summaries lack full inputs and graft semantics. Generic
   exhaustive oracles are implemented, but faithful R1 reproduction is pending
   the missing definitions. In the stated generic forest model, all roots is
   trivially optimal; that is not represented as the original seed's optimum.
4. Python/C proof checks are exact. Predictions and scores use binary64 logs
   and Poisson assumptions, and are not proofs. L002 omits full Kummer
   corrections. L001 is a supplied historical heuristic with prior overlap.
5. Marginal score cells overlap. The threshold of 14 in the brief is recorded
   as a diagnostic; a formal independent likelihood claim needs the separate
   disjoint model assumptions. Maximal multiplicity is predicted but not scored
   as a Poisson count. ECPP and full large-cofactor factorization are unsupported.
6. Deterministic MR requires p below its proven bound. Pocklington supports at
   most 128 distinct factors of q-1, each with bounded-MR prime proof. Unsupported
   primality is rejected as unproved. C censuses require q<2^63, hi<=10^8 and
   K<=10^7; storage/runtime become limiting well before the largest grid cells.
7. Checkpoints occur between bounded exponent chunks. An interrupted chunk is
   recomputed. Recorded CPU time measures completed C work on Windows; killed
   partial chunks and orchestration overhead are not included. The scalar
   predictor is intended for modest cells; large predictions need a validated,
   checkpointed numerical acceleration before a long campaign.
8. Local Git/file timestamps can be rewritten by a malicious operator. The
   audit blocks accidental ordering violations; independent operator custody
   or external timestamping is needed for stronger guarantees.
9. GIMPS report routes and mersenne.ca status/factor routes restrict automated
   access. Current total factors, daily discovery rate and P-1/ECM wavefronts
   remain unverified pending dated operator exports. None are invented.
10. Discovery allocation needs actual owned assignments, installed tools,
    method-conditioned yield estimates and measured CPU costs. Command
    preparation/result checking are implemented; automatic execution and
    submission await those concrete inputs. No secrets are requested in chat.

Only finite cases actually rerun and verified are listed in RESULTS.md.
