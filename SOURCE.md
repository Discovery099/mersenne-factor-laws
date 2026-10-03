# Sources and access record — 2026-10-03

Seed IDs: **01002** (primary, A02), **00302** (A02), **00902** (A02).
The initial build used only the summaries in `TASK.md`. On 2026-10-03 the
operator named `SEEDS_P12_P13_full_records.md` as the full seed source. That
attachment is not yet accessible at a local path; its contents and fingerprint
remain pending. Track 0's original-semantics audit therefore remains pending.
The original brief and the two supplied ZIP fingerprints are retained.

Novelty state: **overlap-found**. This is not an expert-reviewed distinction.

1. [Shanks and Kravitz, On the Distribution of Mersenne Divisors (1967)](https://t5k.org/mersenne/literature/shanksKravitz.html).
   Author paper transcription inspected. Tables by k and exponent range and a
   heuristic using multiplier prime factors directly overlap the proposed task.
2. [Wagstaff, Divisors of Mersenne Numbers (1983)](https://www.ams.org/journals/mcom/1983-40-161/S0025-5718-1983-0679454-X/).
   Publisher fetch failed; [primary-paper mirror](https://scispace.com/pdf/divisors-of-mersenne-numbers-46sdm6m1d1.pdf)
   inspected, especially pages 385–388. Equation (1) already contains the
   supplied L001 weight; the paper also discusses averaging and Poisson limits.
3. [Sorenson and Webster, Strong Pseudoprimes to Twelve Prime Bases](https://arxiv.org/html/1509.00864).
   Theorem 1.1 gives the different 12- and 13-base thresholds. The production
   checker uses 13 bases through 41; the supplied reference remains unchanged.
4. [Stevenhagen, The correction factor in Artin's primitive root conjecture](https://jtnb.centre-mersenne.org/item/JTNB_2003__15_1_383_0/).
   Abstract inspected: corrections arise from dependencies among local conditions.
   This does not prove the Mersenne prime-quotient model used here.
5. [Moree, Artin's primitive root conjecture — a survey](https://arxiv.org/abs/math/0412262).
   Abstract and bibliographic context inspected; relevant background, not a
   source for claiming the joint primality/power-residue heuristic is proved.
6. [Moree and Stevenhagen, Computing higher rank primitive root densities](https://arxiv.org/abs/1203.4313).
   Abstract inspected. The supplied v0.2 derivation cites its entanglement
   machinery; the theorem-to-Mersenne-prime-quotient step remains heuristic.
7. [Conrad, Primality Statistics](https://kconrad.math.uconn.edu/ross2016/primestats.pdf).
   Primary expository notes inspected for Bateman–Horn local root counting.
8. [GIMPS mathematics](https://www.mersenne.org/various/math.php).
   Verified: prime factors satisfy the 2kp+1 form and residue restriction;
   TF uses progression sieving; the per-bit factor chance is an empirical 1/x
   approximation. P-1 has two bounds and benefits from smooth q-1. PRP proofs
   based on Pietrzak were adopted in 2020. These are algorithm/background
   statements, not current factor-count or wavefront measurements.
9. [GMP-ECM source README](https://github.com/sethtroisi/gmp-ecm/blob/main/README).
   Inspected P-1 bounds, ECM curves, saved residues and command-line conventions.
10. [mfakto](https://github.com/primesearch/mfakto) and
    [AutoPrimeNet](https://github.com/tdulcet/AutoPrimeNet/blob/main/README.md).
    Official repositories inspected for GPU TF and assignment/result handling.
    Tool support depends on the actual installed versions; no client was run.
11. [GNU GMP 6.3.0 source archive](https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz).
    mini-gmp C/header and upstream license texts are pinned in `vendor/`;
    `vendor/PROVENANCE.json` records archive and file SHA-256 hashes.
12. **External operator review, Vault-S region 1 (2026-10-03).** Source:
    the operator's message in this chat, naming `REVIEW_VAULT_S1_L001.md`.
    The operator states that the v0.2 census SHA-256 matched the sealed
    region 1 hash exactly and that L001 was scored against the sealed values.
    This is an externally reported confirmation, not a new local rerun or an
    independently inspected review document. The named Markdown attachment
    is not yet accessible; document bytes, SHA-256, precise scores and any
    reviewer qualifications are pending receipt. No numeric score or pass/fail
    verdict is inferred from the statement. Region 1 has not been rerun for
    this request and must not be used for fitting L003.
13. [Hong, On computing the distribution function for the Poisson binomial
    distribution (2013)](https://www.sciencedirect.com/science/article/pii/S0167947312003568).
    Publisher abstract inspected on 2026-10-03 for the independent,
    nonidentical Bernoulli-sum definition. L003 uses direct coefficient
    recursion; the source does not establish independence of Mersenne factors.
14. [Linderman, Exponential families, Stanford STATS 305B](https://slinderman.github.io/stats305b/lectures/04_expfam.html).
    Course notes inspected on 2026-10-03 for the Poisson KL identity. The
    expected deviance formula in `POWER_PROTOCOL.md` also follows directly
    by cancellation and is unit-tested by summing over Poisson outcomes.
15. [User-relayed post-commit assessment](data/sources/operator_note_after_preregistration_2026-10-03.md).
    Received after prediction commitment `0a3a738` and delivery of its SHA-256.
    Reports region 1 observations and approximate L003 estimates; the proposed
    explanation and sigma estimates are attributed external commentary, not
    independently checked results. None entered the frozen predictions.
    The user subsequently explicitly authorized the full committed design.
16. [External region 2 operator confirmation](data/sources/REVIEW_VAULT_S2_operator_2026-10-03.md).
    The user relayed an exact match to the withheld census hash and all four
    reported cells: 250614 factors, 206852 exponents with >=1, 38568 with >=2,
    and maximum 5. The [machine-readable record](data/sources/Vault_S2_operator_confirmation_2026-10-03.json)
    pins this record's bytes and binds
    the attestation to the local census. The original withheld file and the
    operator's identity were not independently inspected. The operator also
    reports that the prediction fingerprint was not received before computation:
    local Git chronology is preserved, but external pre-run timestamping was
    missed. This qualification supersedes any stronger reading of item 15.
17. **Closeout literature recheck (2026-10-03).** Wagstaff (1983), page 387,
    equation (4), already uses the product of no-factor probabilities; the
    surrounding discussion distinguishes small-factor behavior from a Poisson
    approximation. Read in the primary-paper mirror linked in item 2. This is
    direct prior overlap with the zero-count part of L003, not merely a general
    precedent for Poisson modeling. The report distinguishes the project's L001
    Poisson implementation from Wagstaff's full treatment. The PDF text was
    available; a fresh page-image fetch was blocked by the mirror's challenge.

## Access restrictions and missing live measurements

Both sites' robots.txt files were fetched once and cached with hashes and UTC
access dates under `data/sources/`. mersenne.org disallows most report routes;
mersenne.ca disallows exponent, factor, k and several status routes. Those data
routes were not scraped. Dated operator exports are needed for total known
factors, recent daily discovery rate and P-1/ECM wavefronts. They remain unknown.
No count or date from the task brief is silently treated as current fact.
