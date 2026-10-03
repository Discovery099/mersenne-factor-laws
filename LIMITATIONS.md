# Limits and pending inputs

1. Full open grid, rolling vaults and a credited GIMPS discovery remain research
   milestones. The operator reports a region 1 sealed-hash match and scoring;
   the original review document is pending. Region 2 local results and external
   seal confirmation are reported separately in `results/Vault_S2_full/`.
   No weeks-long campaign has been launched without an explicit CPU/time cap.
2. v0.2 contains historical vault results. They were not imported into model
   development here; any later audit must preserve their original commitments.
3. The original seed summaries lack full inputs and graft semantics. Generic
   exhaustive oracles are implemented, but faithful R1 reproduction is pending
   the missing definitions. In the stated generic forest model, all roots is
   trivially optimal; that is not represented as the original seed's optimum.
4. Python/C proof checks are exact. Predictions use binary64 arithmetic and
   heuristic distributions, including Poisson and L003's Poisson-binomial
   model. Numerical convergence checks do not prove the modeling assumptions.
   L002 omits full Kummer corrections. L001 has direct prior overlap; L003's
   finite Bernoulli construction is standard, with no claim of novelty.
5. Marginal score cells overlap. The threshold of 14 in the brief is recorded
   as a diagnostic; a formal independent likelihood claim needs the separate
   disjoint model assumptions. The v0.4 prescribed score includes the maximum
   once as a composite diagnostic; the historical v0.3 score excluded it.
   Prospective expected-gain >=14 in each direction is the operator's design
   criterion, not an 80% power calculation or a calibrated significance level.
   ECPP and full large-cofactor factorization are unsupported.
6. Deterministic MR requires p below its proven bound. Pocklington supports at
   most 128 distinct factors of q-1, each with bounded-MR prime proof. Unsupported
   primality is rejected as unproved. C censuses require q<2^63, hi<=10^8 and
   K<=10^7; storage/runtime become limiting well before the largest grid cells.
7. The v0.4 runner checkpoints each completed engine output and each verified
   chunk. An interrupted engine calculation is recomputed; already checkpointed
   outputs are reused after hash checks. Recorded CPU time measures completed C
   engine work on Windows; killed partial chunks, checkers and orchestration
   are not included. The accelerated predictor is validated for the registered
   design; broader bounds still need numerical and resource checks.
8. Local Git/file timestamps can be rewritten by a malicious operator. The
   audit blocks accidental ordering violations; independent operator custody
   or external timestamping is needed for stronger guarantees. For this test,
   the operator explicitly reports no pre-run receipt of the prediction hash;
   the later outcome confirmation does not supply that missing timestamp.
9. GIMPS report routes and mersenne.ca status/factor routes restrict automated
   access. Current total factors, daily discovery rate and P-1/ECM wavefronts
   remain unverified pending dated operator exports. None are invented.
10. Discovery allocation needs actual owned assignments, installed tools,
    method-conditioned yield estimates and measured CPU costs. Command
    preparation/result checking are implemented; automatic execution and
    submission await those concrete inputs. No secrets are requested in chat.

Only finite cases actually rerun and verified are listed in RESULTS.md.
