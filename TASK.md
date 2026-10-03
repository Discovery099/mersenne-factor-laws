# Coding Task P12 — Mersenne Factor Laws: Exact Censuses, Sealed Predictions, and New Factors

**Seed records:** 01002 *Prime-factor forests with divisor-token grafting* (A02, primary) · 00302 *Joint prime-adic valuation counts through incompatible digit carries* (A02) · 00902 *Arithmetic-progression sieves with residue-cache contamination* (A02)
**Frontier:** the Great Internet Mersenne Prime Search (GIMPS). 52 Mersenne primes are known; the largest is M136279841 (October 2024). GIMPS participants report new factors of Mersenne numbers every day, found by trial factoring (TF), P−1 and ECM, and each one is credited by name in the public database. There is no published exact census of Mersenne factors by their multiplier k with a first-principles law tested against sealed data (to be confirmed by the novelty gate)
**Novelty status:** `unreviewed` — confirm or correct it on day 0 (Section 2.3)

---

## Task

Build **`mersenne-factor-laws`**, a Python + C codebase that:

1. verifies Mersenne factor claims exactly (form, divisibility, and primality via Lemma L2, deterministic Miller–Rabin or a Pocklington certificate), with two independent checkers;
2. computes exact **censuses** of Mersenne factors q = 2kp + 1 by their multiplier k, with two independent algorithms that must agree on the census hash;
3. runs the core engine (Section 5.1): **laws derived from first principles, committed before each census cell is computed**, and scored against a mandatory null model and against sealed values held by the operator;
4. reproduces the three seed oracles exactly (Track 0);
5. hunts **new factors** with standard tools on exponents assigned through GIMPS, allocated by the laws, and credited to the operator's GIMPS account.

This is an open-ended campaign: work autonomously and continuously, for weeks or longer, under the long-run protocol in Section 9. There is no planned end; a verified discovery raises an alert and the campaign continues. Sections 0–6 give the research context and exact definitions, Section 7 specifies the code, and Section 8 lists the first actions.

This file is self-contained. The seed archive it cites is not provided to you: the seed summary in Section 2 is the authoritative description of the seed, and you should record the seed IDs from this file in `SOURCE.md`. Everything else you need (papers, tables, software) you must find and cite yourself.

---

## 0. Context and goal

Every prime factor of a Mersenne number M_p = 2^p − 1 (p an odd prime) has the form **q = 2kp + 1**, with q ≡ ±1 (mod 8). The multiplier **k** is the factor's fingerprint: it decides whether P−1 can find the factor (k must be smooth), how deep trial factoring must go (q grows with k), and it is where any hidden regularity of Mersenne factors must show up.

Traditional factor hunting is blind search with textbook success estimates. This task works like the BSL campaign (exact values, then a growth law), and adds sealed tests so that any "law" it claims is real:

1. **Exact census ladder (Track C).** Compute N(X₁, X₂, K), the exact number of prime factors q = 2kp + 1 of M_p with X₁ ≤ p ≤ X₂ and k ≤ K, together with exact statistics of k (buckets, residue classes, valuations, smoothness). These are exact, checkable tables, like S1(L) for BSL.
2. **Law track (Track L).** Derive, from first principles, formulas that predict the census: a *factor-count law* with an explicit constant, and laws for the k-structure. Every prediction is committed (SHA-256) **before** the census cell is computed, and is scored against a mandatory null model and against **sealed values the agent never sees**.
3. **Discovery track (Track D).** Use the laws to decide where a laptop's CPU-hour is most likely to find a **new factor** (P−1 bounds, ECM curves, TF depth), run the standard tools on exponents assigned through GIMPS, and get each new factor credited to the operator's GIMPS account.

**Be honest about value.** Factors with small k are already known to GIMPS (its trial factoring has covered all small q), so the census itself discovers no new factors. Its products are the exact tables and the laws. New factors come only from Track D.

## 1. Background you must verify (dated 2026-10-02)

- **GIMPS mathematics page** (mersenne.org/various/math.php). Record its exact statements:
  - factors have the form 2kp + 1 and are 1 or 7 mod 8;
  - the chance of a factor between 2^x and 2^(x+1) is about 1/x;
  - how TF sieves, how P−1 works (stage 1 bound B1, stage 2 bound B2, factor found when k is smooth);
  - PRP tests with Pietrzak proofs (since 2020).
- **Data sources:** the mersenne.org Known Factors report (factor, date found, method) and mersenne.ca (per-exponent status, factors, P−1 bounds already done, ECM progress). **Respect each site's terms and robots.txt.** Pages that disallow automated fetching are downloaded by the operator in a browser and supplied as files. Never scrape aggressively; cache everything locally with the access date.
- **Literature:**
  - S. S. Wagstaff Jr., *Divisors of Mersenne numbers* (Math. Comp., 1983) and later work on the distribution of Mersenne factors;
  - the Bateman–Horn conjecture (primes of the form 2kp + 1 with p prime);
  - the Chebotarev density theorem and Kummer theory for "2 is a 2k-th power residue mod q" (the densities behind any factor-count law);
  - Artin's primitive-root conjecture and its correction factors (the same style of constant appears here).
- **Software:**
  - mprime/Prime95 (P−1, ECM, PRP on the CPU, with its own P−1 bound-selection rule: this is the baseline Track D must beat);
  - GMP-ECM;
  - mfaktc/mfakto (TF on GPUs);
  - PRPLL/GpuOwl;
  - AutoPrimeNet (submitting GPU results).
- **Facts to record with sources:** the total number of known Mersenne factors, the recent daily rate of new factors, and the current P−1 and ECM wavefronts. Do not trust numbers quoted in this file.

## 2. Seed change log and novelty gate

### 2.1 What the seeds specify

- **01002 (primary):**
  - **Task:** for a set of query integers, build *prime-factor forests* (trees whose leaves multiply to each integer), grafting shared divisor tokens under a budget.
  - **Objective:** minimize maximum proof depth, then consumed tokens, returning factor-product certificates for all queries.
  - **Oracle:** for at most 8 integers, enumerate every parent map and multiply the leaf labels directly.
- **00302:** return the exact bivariate histogram of capped prime-adic valuations (x, y), with the smallest n in each occupied bin. Oracle: R ≤ 60, evaluating factorial quotients directly.
- **00902:** count admissible integers exactly over overlapping arithmetic-progression sieves.
  - A residue cache may be reused across a refined modulus only through a supplied projection.
  - Contaminated cache entries become explicit ambiguity classes.
  - Oracle: N ≤ 200, tested directly.

### 2.2 Change log (record verbatim in `DELTA.md`)

| Seed element | Status here | Reason |
|---|---|---|
| Factor-product certificates for every query (01002) | **Kept, and made central.** Every claimed factor carries a certificate: divisibility, plus primality by Lemma L2, deterministic Miller–Rabin, or a Pocklington certificate. Every full factorization carries a factor forest | A factor claim without a primality certificate is not a result |
| Minimize proof depth, then tokens (01002) | **Kept** as a secondary metric: certificate size and depth for each fully factored M_p | Smaller certificates are cheaper to re-check |
| Capped valuation histograms (00302) | **Specialized** to the census: the exact histogram of (min(v₂(k), 6), min(v₃(k), 6)) with the smallest p per bin, plus the largest-prime-factor (smoothness) profile of k | k's valuations decide P−1 success |
| Arithmetic-progression sieves with cache soundness (00902) | **Kept** as the census engine: the progressions q = 2kp + 1 are sieved by small primes. Any residue table reused across exponents must carry a written soundness argument and a contamination test | This is exactly where a fast census can silently go wrong |
| Seed oracles (≤ 8 integers; R ≤ 60; N ≤ 200) | **Kept exactly** as Track 0 (rung R1) | Faithful reproduction first |
| **Added:** sealed vaults, preregistered laws, the null model, and the discovery track | New | The research engine and the tangible results |

### 2.3 Day-0 novelty gate

Search for the following, then record the closest work in `SOURCE.md` and set the novelty state before any claim:
- (a) exact tables of Mersenne factors counted by k;
- (b) Wagstaff (1983) and successors on the distribution of Mersenne divisors;
- (c) the distribution of k modulo small numbers ("k classes");
- (d) explicit constants for the expected number of Mersenne factors with k ≤ K (Bateman–Horn/Chebotarev type);
- (e) any prior factor-count law tested out of sample.

## 3. Formal definitions (`SPEC.md`)

### 3.1 Objects

- **Exponents:** p ranges over odd primes, and M_p = 2^p − 1.
- **Census factor:** a pair (p, k) with k ≥ 1 such that q = 2kp + 1 is prime and q divides M_p.
- **Census:** C(X₁, X₂, K) is the set of census factors with X₁ ≤ p ≤ X₂ and k ≤ K, and N(X₁, X₂, K) = |C(X₁, X₂, K)|.
- **Canonical encoding:** the lines `"p k\n"` in ASCII, sorted by (p, k); its SHA-256 is the **census hash**.

### 3.2 Lemmas (prove each in `SPEC.md`; the checker uses them)

- **L1 (k classes).** q ≡ ±1 (mod 8) forces k ≡ 0 or 3 (mod 4) when p ≡ 1 (mod 4), and k ≡ 0 or 1 (mod 4) when p ≡ 3 (mod 4).
- **L2 (automatic primality).** If q = 2kp + 1 divides M_p and k ≤ 2p + 1, then q is prime.
  - Every prime factor r of q has order p modulo 2, so r ≡ 1 (mod 2p) and r ≥ 2p + 1.
  - So a composite q would satisfy q ≥ (2p + 1)², which forces k ≥ 2p + 2.
- **L3 (power residues).** For a prime q = 2kp + 1: q divides M_p if and only if the order of 2 mod q is p, if and only if 2 is a 2k-th power residue mod q.

### 3.3 Exact statistics of a census (all integer-valued)

- **Dyadic buckets:** n_j = #{(p, k) ∈ C : 2^j ≤ k < 2^(j+1)}.
- **Residue profile:** counts by k mod m for m ∈ {3, 4, 5, 8, 12, 24, 60}.
- **Valuation histogram** (from 00302): H(a, b) = #{(p, k) : min(v₂(k), 6) = a, min(v₃(k), 6) = b}, with the smallest p in each occupied bin.
- **Smoothness profile:** counts by the largest prime factor of k, in dyadic bins.
- **Multiplicity profile:** the number of exponents p with exactly j census factors, for j = 0, 1, 2, ….

### 3.4 Laws, the null model, and scoring

- **Law:** a computable predictor that maps a census query (range, bucket or class) to a predicted count. Constraints:
  - It is a program of at most **2,000 bytes** of gzipped source, with at most **8 fitted parameters**.
  - Lookup tables of observed counts are forbidden.
  - Fitted parameters may be fitted **only on the open range** (Section 3.5); a law with zero fitted parameters, derived purely from theory, is preferred.
- **Null model N0** (mandatory baseline; implement it exactly). Each pair (p, k) allowed by L1 contributes
  `E₀(p, k) = (1/k) · Π_{r ≤ 47, r prime} [r ∤ q] · r/(r−1) · 1/ln q`, with q = 2kp + 1.
  - The product term is the probability that q is prime given that it has no prime factor ≤ 47; r = 2 is included and contributes a factor 2, because q is always odd.
  - A sanity check written into this task: for 10⁴ ≤ p ≤ 2·10⁴ and k ≤ 10³, the census has 520 factors and N0 predicts about 508. N0 is a good first approximation, so beating it requires capturing real structure.
  - The 1/k term is the naive chance that 2 is a 2k-th power residue (1/(2k)), doubled because L1 already makes 2 a quadratic residue.
- **Scoring:**
  - For each preregistered query, compute the Poisson deviance between the observed and predicted counts.
  - A law **beats N0** on a vault only if its total deviance is lower than N0's by at least 2·(number of fitted parameters) + 14 (roughly a factor of 1,000 in likelihood), with every query preregistered.
  - A law that fails is kept in `DEAD_ENDS.md` with its residuals; it is never re-tested on the same cells after edits.

### 3.5 Data regions and vaults

- **Open range:** C(3, 10⁶, 10⁵). The agent computes it, explores it freely, and may fit on it.
- **Vault-S (sealed, operator-held):** exact summaries of two censuses were computed independently before this task was issued and are held by the operator. The agent never sees them and must not try to infer them from outside sources:
  - C(10⁶, 10⁷, 10⁵);
  - C(10⁷ + 1, 2·10⁷, 10⁴).

  The summaries contain the totals, the dyadic buckets, the k mod 3/4/5/8/12 profiles, the number of exponents with at least 1 and at least 2 factors, the maximum number of factors for one exponent, and the census hash.

  **Protocol:**
  1. Commit predictions for every summary cell: write `predictions/vaultS.json`, record its SHA-256 in `ALERTS.md` and in a git commit.
  2. Only after the commit, compute the census.
  3. Report the census hash and statistics.

  The operator scores the predictions and confirms the hash.
- **Rolling vault:** every new census cell beyond the vault ranges (for example X up to 10⁸ or 10⁹ with smaller K) is predicted and committed before it is computed. This is the long-run growth-law campaign.
- **Vault-T (time-sealed):** predictions about factors that the whole GIMPS community will report **after** the commit date. These cover a declared exponent band and method: for example the k-class proportions of new factors, or the smoothness of P−1 factors relative to their bounds, conditioned on the method that found them. Data that does not exist yet cannot leak.
  - **Selection-effect rule:** TF only finds factors below a bit limit, and P−1 only finds factors with smooth k. Any Vault-T law must model the discovery method's selection explicitly, or it is void.

### 3.6 Discovery objects (Track D)

- **New factor:** a pair (p, q) that passes the factor checker, is absent from the GIMPS known-factor data at a recorded check date, was found on an exponent assigned to the operator through PrimeNet (or listed as available, never another user's assignment), and is reported through PrimeNet under the operator's account.
- **Full-factorization event:** after dividing out all known factors, the cofactor of M_p is proven prime (a PRP test, then a primality certificate, for example ECPP, verified by an independent verifier). This is rare and notable.

### 3.7 Proposed questions (unresolved status)

- **Q1 (exact):** the table N(X, K) for X ∈ {10⁴, …, 10⁸} and K ∈ {10², …, 10⁶}, with all Section 3.3 statistics.
- **Q2 (growth law):** a closed formula N(X₁, X₂, K) ≈ Λ · F(X₁, X₂, K) with an explicit constant Λ derived from Chebotarev and Bateman–Horn densities, accurate to Poisson noise on every sealed and rolling cell. Compute Λ to six digits.
- **Q3 (k-class law):** the exact limiting proportions of census factors in each class k mod m (m ≤ 120), predicted and confirmed.
- **Q4 (multiplicity law):** is the number of census factors per exponent Poisson, or do factors of the same M_p repel or attract?
- **Q5 (efficiency):** does law-guided allocation find more new factors per CPU-hour than Prime95's default bound selection on matched exponents?

## 4. Frozen targets and milestone ladder

### 4.1 Frozen targets (create `TARGETS.md` on day 0)

- The census grid of Q1.
- The Vault-S summary cells (the list in Section 3.5).
- The rolling-vault schedule (which cells, in which order).
- The Track D discovery band. Choose it on day 0 with the operator, from the data:
  - P−1 on exponents whose earlier P−1 bounds are weak;
  - and/or ECM on small exponents through GIMPS ECM assignments.
- The A/B design for Q5.

Freeze the file with its SHA-256.

### 4.2 Milestone ladder

| Rung | Target | Claim level |
|---|---|---|
| R0 | Reference checker (Section 10) reproduced; two independent factor checkers (Python + C/GMP); two independent census engines (one loops k per p, the other loops p per k with a prime sieve on q) agreeing on census hashes; mutation tests | infrastructure |
| R1 | **Track 0:** the three seed oracles exactly as specified (forests for ≤ 8 integers; histogram at R ≤ 60; sieve counts at N ≤ 200) | C0/C2 |
| R2 | The open census grid computed exactly with all statistics and hashes; L1–L3 proved in `SPEC.md` | C2 |
| R3 | Law v1 derived from first principles (no fitted parameters); Vault-S predictions committed | preregistered |
| R4 | Vault-S censuses computed; hash confirmed by the operator; law scored against N0 | C2 + scored law |
| R5 | Rolling vault to X = 10⁸ (K ≤ 10⁴), each cell predicted before it is computed: **the growth-law campaign** | C2 per cell |
| R6 | **Track D:** first new factor credited to the operator's account; then Q5 measured | C1 (new object) |
| R7 (flagship) | A law with an explicit constant that survives every vault and rolling cell within noise, with a written derivation and proofs of its provable parts; **or** a full factorization of some M_p | C3-style evidence / C4 |

## 5. Core method and supporting strategies

### 5.1 Core engine: derive, preregister, compute exactly, score

1. **Derive.** Write each law as a short program in `laws/<id>.py` with its derivation in `laws/<id>.md`. Start from L3:
   - the density of primes q ≡ 1 (mod 2k) for which 2 is a 2k-th power, including the Kummer corrections where 2's roots interact with ζ₈;
   - the Bateman–Horn factor for 2kp + 1 being prime when p is prime;
   - summed over the census region. The constant Λ falls out of this sum.
2. **Preregister.** Before computing any new cell, commit its predictions. Then compute.
3. **Compute exactly.** Use a C census engine with Montgomery multiplication and an incremental small-prime sieve over the progression. Respect 00902's cache rule: a residue table reused across exponents needs its projection proved, plus a contamination test.
4. **Score** against N0 and against earlier laws. Residual patterns (by p mod small numbers, by the factorization of k, by bucket) become **new hypotheses, testable only on cells not yet computed.**
5. **Never look first.** A law edited after its cell was seen is a new law, tested on new cells.

### 5.2 Allocation engine (Track D)

- Turn the laws into an expected number of new factors per CPU-hour for each candidate (exponent, method, bounds), given the work already done on that exponent (from the supplied data).
- Run the standard tools (mprime for P−1/ECM, GMP-ECM, mfaktc/mfakto for TF if a GPU exists) on PrimeNet-assigned exponents.
- **A/B (Q5):** matched exponents, half with Prime95's default bounds and half with law-chosen bounds, on the same hardware. Use a preregistered metric (new factors per CPU-hour) and report a confidence interval.

### 5.3 Supporting strategies

1. A second census algorithm (loop over k, sieve q for primality, test p) for independent hashes.
2. Factor forests (01002) for fully factored exponents, with certificates as small as possible.
3. GPU kernels for the census (optional), cross-checked against the CPU engine on every batch.

## 6. Verification contract

- **Factor claims:**
  - two independent checkers;
  - divisibility: 2^p ≡ 1 (mod q);
  - form: q = 2kp + 1 and q ≡ ±1 (mod 8);
  - primality: L2, or deterministic Miller–Rabin below 3.3·10²⁴, or a Pocklington certificate with F = 2p × (fully factored part of k), or else an independently verified ECPP certificate.
- **Census claims:** the census hash from two independent algorithms, plus a brute-force oracle on small ranges (divide M_p by every prime up to the range's maximum q).
- **Law claims:**
  - the preregistration commit must precede the computation in the git history and in `ALERTS.md`;
  - the scoring script is frozen and computes the null with the same code;
  - Vault-S scores come from the operator.
- **Discovery claims:** a dated check against the GIMPS data, and the PrimeNet submission record.
- **GIMPS conduct (binding):**
  - use only the operator's account;
  - follow PrimeNet's assignment rules and never take work on an exponent assigned to someone else;
  - never submit a result that was not actually computed;
  - respect site terms and robots.txt.

### 6.1 Token and cost discipline (mandatory)

1. **Programs compute; the agent supervises.** Check long jobs at most every 30–60 minutes.
2. **Never paste large outputs into the context;** print summaries and hashes only. Census lists live on disk.
3. **Keep the context short;** resume from `STATE.md` + `MEMORY.md`.
4. **Reuse working tools;** build new ones only for a measured bottleneck.
5. **Budget:** log tokens per claim in `LEDGER.jsonl`; stop and explain if one target exceeds about 50 million tokens without progress.

## 7. Build specification

The deliverable is a git repository named `mersenne-factor-laws/`. The codebase is complete for a milestone only when `make test` passes and `make verify` re-checks every file in `certificates/` with both independent checkers and prints a summary table.

### 7.1 Repository layout

```text
mersenne-factor-laws/
├── SPEC.md  DELTA.md  SOURCE.md  PRIOR_ART.md  TARGETS.md  HARDWARE.md
├── STATE.md  MEMORY.md  LEDGER.jsonl  IDEAS.md  DEAD_ENDS.md  LEADERBOARD.md  ALERTS.md
├── checker_reference.py        # given verbatim in Section 10
├── mf/
│   ├── checker.py              # ACCEPTANCE: factor claims + census hashes
│   ├── checker2.c              # independent C/GMP factor checker
│   ├── census_kp.c             # census engine A: loop k per p (Montgomery, incremental sieve)
│   ├── census_pk.c             # census engine B: loop p per k, prime sieve on q
│   ├── stats.py                # Section 3.3 statistics from a census file
│   ├── null_n0.py              # the null model, exactly as in Section 3.4
│   ├── score.py                # frozen Poisson-deviance scoring
│   └── track0/                 # the three seed oracles
├── laws/                       # <id>.py (<= 2,000 bytes gzipped) + <id>.md derivations
├── predictions/                # committed prediction files (never edited)
├── discovery/                  # Track D: assignments, tool configs, results, PrimeNet receipts
├── data/                       # operator-supplied exports with access dates (never vault data)
├── certificates/  claims/  runs/  ops/
└── tests/
```

### 7.2 Command-line interface

Every command writes machine-readable JSON to stdout and exits non-zero on any failed check.

```bash
python -m mf.checker factor 11 89                          # -> {valid, k, primality_method}
./mf/checker2 11 89                                          # must agree
./mf/census_kp 3 1000000 100000 > runs/open.txt && python -m mf.checker census runs/open.txt   # -> {count, sha256}
./mf/census_pk 3 1000000 100000 | python -m mf.checker census -                               # same sha256
python -m mf.score --law laws/L001.py --predictions predictions/open_X1e6.json --census runs/open.txt
```

### 7.3 Required tests (all must pass before any search runs longer than 30 minutes)

- The reference checker's output (Section 10) is reproduced exactly: 46 census factors for 3 ≤ p ≤ 200, k ≤ 10⁴, hash prefix `4c37caf1201fe83d`.
- `census_kp` and `census_pk` produce identical census hashes on p ≤ 10⁵, k ≤ 10⁴, and both match a brute-force oracle (division of M_p by every prime up to the maximum q) for p ≤ 200; and 215 factors for 1000 ≤ p ≤ 3000, k ≤ 20,000.
- `checker.py` and `checker2.c` agree on 10⁴ random valid and invalid factor claims, including composite divisors with k > 2p + 1 and Pocklington certificates with corrupted witnesses.
- Mutation: changing q by ±2, p to the next prime, or one witness is rejected.
- Every census factor satisfies L1 (k classes); any violation is a bug.
- `score.py` reproduces N0's deviance on a fixed synthetic census; prediction files are refused unless their SHA-256 appears in a git commit older than the census file.
- Track 0 oracles pass at their seed limits.

### 7.4 Engineering rules

- Python ≥ 3.10 with a pinned `requirements.txt` (or `uv.lock`); compiled components build with one `make` target.
- Exact arithmetic only (integers, rationals, finite fields). No floating point in any acceptance path.
- Search code may import the checker; the checker may never import search code.
- Every long job takes `--seed`, `--hours` and `--checkpoint DIR`, resumes from its checkpoint, and appends one line to `LEDGER.jsonl` when it ends. Jobs are launched through `ops/supervisor.py` and its queue (Section 9.C), never only from the agent's own shell session.
- `ops/` holds the supervisor, the job queue and `make status`; `DAILY/`, `WEEKLY/`, `archive/`, `MEMORY.md` and `ALERTS.md` sit at the repository root.
- Every certificate file is written once, never edited, and its SHA-256 is recorded in `LEADERBOARD.md` or the relevant table.

## 8. First 90 minutes (execute in order)

0. Create the project folder, `git init`, the `ops/` supervisor skeleton, and create `checker_reference.py` exactly as given in Section 10. Run it and confirm its output matches the expected output shown there. If it does not match, debug the environment (Python version, file contents) until it does; write no other code before that.
1. Write `SPEC.md` from Section 3 with the proofs of L1–L3; complete the novelty gate (2.3); freeze `TARGETS.md` (4.1).
2. Build the C census engine and the second, independent one. Reproduce:
   - 46 census factors for 3 ≤ p ≤ 200, k ≤ 10⁴, with census-hash prefix `4c37caf1201fe83d` (the Section 10 output);
   - 215 census factors for 1000 ≤ p ≤ 3000, k ≤ 20,000.
3. Implement N0 exactly, and law v1 from first principles. Practise the protocol on the open range: commit predictions for the largest open cell *before* computing it.
4. Launch in the background: the open census grid, and the Track 0 oracles.
5. Write an `ALERTS.md` entry asking the operator to:
   - create or confirm a GIMPS account;
   - install mprime (and a GPU tool if available) for Track D;
   - supply the data exports for the discovery band (known factors, P−1 bounds already done).

---

## 9. Long-run protocol (open-ended, multi-week — read it twice)

This is an **open-ended, multi-week campaign**. There is no planned end date and no "finished" state. You keep working — for days, weeks, or longer — until a human stops you or a hard resource cap is reached. Reaching a target, even a record, does **not** end the campaign: you bank it, verify it, raise an alert (Section G), and climb to the next rung of the milestone ladder. When the ladder is exhausted, you widen the parameter range, choose new open cells by the rubric in Section D, or generalize your best objects into families.

The campaign runs on three clocks: the **cycle** (30–60 minutes), the **day** (every 24 hours), and the **week** (every 7 days). Each has its own duties below.

### A. Persistent memory (your context will be reset many times; files are your memory)

Create these at minute 0 and keep them current. After any context reset, compaction, restart or crash, **first read `STATE.md`, `MEMORY.md`, the last 30 lines of `LEDGER.jsonl`, and `IDEAS.md`** before doing anything else. A fresh agent must be able to resume from these files in under 10 minutes.

| File | Purpose | Rule |
|---|---|---|
| `STATE.md` | Current best result per target, claim level, active hypothesis, running background jobs (PID, command, log path, start time, expected end), checker SHA-256, campaign day number, next three actions | ≤150 lines. Rewrite before launching any job longer than 10 minutes and at the end of every cycle |
| `MEMORY.md` | Durable lessons: what works, what never works, key facts from the literature, conventions decided | ≤300 lines. Updated every day; condensed every week. This is what survives when old logs are archived |
| `LEDGER.jsonl` | Append-only experiment log: `{ts, cycle, target, idea_id, code_sha, params, seed, cpu_s, wall_s, best_score, verified, certificate_path, conclusion}` | One line per experiment, including failures. Never edit old lines. Rotated weekly to `archive/LEDGER_<week>.jsonl.gz` |
| `IDEAS.md` | Priority queue of hypotheses with an expected-information score (1–5) and cost estimate | Every cycle adds at least two ideas and retires or re-scores one. Pruned daily to ≤100 entries |
| `DEAD_ENDS.md` | Ideas that failed, with the reason and the evidence | Check before re-trying anything |
| `LEADERBOARD.md` | Best verified object per target vs. the best published value (source and access date) | Only checker-verified entries |
| `DAILY/<YYYY-MM-DD>.md` | One-page daily report | Section B.2 |
| `WEEKLY/<week>.md` | Two-page weekly report | Section B.3 |
| `ALERTS.md` | Every candidate discovery, newest first, with its status | Section G |
| `HEARTBEAT` | A timestamp written by the supervisor every 5 minutes | Section C |

Use `git` in the work folder and commit at the end of every cycle with a message naming the idea ID. Push to a remote (if one is configured) at least daily.

### B. The three clocks

**B.1 The cycle (30–60 minutes, repeated indefinitely)**

1. **Orient** — read `STATE.md`; check every background job (alive? progress? best score?); harvest finished results.
2. **Choose** — pick the highest expected-information idea from `IDEAS.md`. Keep roughly 70% of effort on the current best line and 30% on exploratory ideas from a *different* strategy family.
3. **Implement** — small, tested increments. Every new search component is unit-tested against the small-case oracle before it may run long.
4. **Launch** — long searches run under the supervisor (Section C), with a recorded seed, a time limit per run, and a checkpoint at least every 10 minutes.
5. **Work while it runs** — never idle-wait more than 5 minutes. Verify earlier outputs, write the next idea, read a paper, strengthen mutation tests, or analyze structure in the best objects so far.
6. **Verify** — every candidate goes through the frozen checker in a fresh process, reading from files. The search's own score is never trusted.
7. **Record** — one `LEDGER.jsonl` line per experiment; update `LEADERBOARD.md` only for verified improvements.
8. **Reflect** — 3–6 sentences in `STATE.md`: what happened, why, what it suggests. Add two or more ideas to `IDEAS.md`.
9. **Checkpoint** — `git commit`.

**B.2 The day (every 24 hours)**

1. Write `DAILY/<date>.md`: verified results and claim levels, CPU-hours used, jobs run, best scores per target vs. yesterday, the top three ideas for tomorrow.
2. Re-verify every banked result in `certificates/` with both checkers (`make verify`).
3. Restart any stalled or crashed jobs; kill jobs whose score has not moved in 24 hours and log why.
4. Prune `IDEAS.md`; move failures to `DEAD_ENDS.md`; distil new lessons into `MEMORY.md`.
5. Housekeeping: disk usage below 70% of the quota (compress logs, delete superseded checkpoints, keep every certificate), `git gc`, push.

**B.3 The week (every 7 days)**

1. **Literature and record check**: re-check every table, catalogue and arXiv listing relevant to your targets; record the date and whether any record moved. If someone else beat your target, update `LEADERBOARD.md` and re-plan.
2. **Portfolio review**: for each target, compare progress against CPU spent. Re-allocate cores toward the targets with the best recent rate of verified progress, but keep at least 20% of compute on exploration.
3. **Theory pass**: study the best objects found so far for symmetry, algebraic structure or recursive patterns. Turn each pattern into a precise conjecture, search for its smallest counterexample, and if it survives, attempt a proof (formalize in Lean where feasible).
4. **Code health**: profile the hottest search loop and optimize it; re-run the full test suite; rotate `LEDGER.jsonl`; condense `MEMORY.md`.
5. Write `WEEKLY/<week>.md`: what was established, what failed, where compute went, the plan for next week.

### C. Keeping the machine busy for weeks (the supervisor)

- Run `nproc`, `free -g` and `df -h` at start and record them in `STATE.md`.
- Build `ops/supervisor.py` (or an equivalent shell script run under `tmux`, `screen` or `systemd`). It reads a job queue file (`ops/queue.jsonl`), keeps the configured number of cores busy, restarts crashed jobs from their last checkpoint (at most 3 times per job, then marks it failed), writes `HEARTBEAT` every 5 minutes, and never deletes certificates.
- The supervisor must survive the agent's own context resets: the agent adds and removes jobs by editing `ops/queue.jsonl`, not by holding processes in its own session.
- `make status` prints the heartbeat age, running jobs, best score per target, disk usage and the last five `ALERTS.md` entries.
- At all times at least one long job runs on the main target. Stagger jobs so one finishes roughly every cycle. Record CPU-hours per result.

### D. Plateau and rotation rules (by time scale)

- **3 hours** without improvement in a tracked score → rotate to a different strategy *family* from the strategy bank (not a parameter tweak).
- **3 days** without improvement on a target → move sideways to an adjacent open target on the ladder, while keeping one background job on the old target.
- **2 weeks** without any verified progress anywhere → write `REPLAN.md`: re-score all open targets (consequence, verifiability, accessibility, room after prior art, resource fit), pick the best three, and restart the cycle on them. Never repeat a plan listed in `DEAD_ENDS.md` without a new reason.
- Choosing new open targets: prefer cells where the gap between the best known lower and upper bounds is large, where few recent papers exist, and where your existing code transfers directly.

### E. Anti-stopping rules

- Do **not** end your turn with a final summary. Summaries go into `DAILY/` and `WEEKLY/` files, and then you continue working.
- A plateau is not a stop condition; it triggers Section D. A discovery is not a stop condition; it triggers Section G, and then you continue.
- The only legitimate stops are: (a) a hard budget, time or resource cap set by the human is reached; (b) an unrecoverable environment failure after three documented recovery attempts; (c) an explicit human instruction to stop.
- If the harness forces your turn to end, leave `STATE.md` and the supervisor queue in a state where the next turn — or a fresh agent — resumes immediately. Background jobs keep running between turns.

### F. Integrity rules (non-negotiable)

- The acceptance checker is written from the definitions in this prompt **before** the search code, is kept small and boring, and its SHA-256 is recorded in `STATE.md`. Any change to it creates a new version, and every earlier claim must be re-verified with the new version.
- Never loosen a definition, change a convention, add a tolerance, or narrow a quantifier to make a result pass. If a definition turns out to be ambiguous, resolve it explicitly in `SPEC.md` and `DELTA.md` *before* using it.
- Mutation-test the checker: corrupt valid witnesses (flip one entry, drop one term, change one coefficient, swap a sign) and confirm every corruption is rejected. Log the results.
- A timeout is `unknown`, never `infeasible`. A heuristic that finds nothing proves nothing.
- Keep the novelty status honest: `unreviewed` → `overlap-found` / `candidate-distinction` → `expert-reviewed-distinction`. A question formulated here is a **proposed research question with unresolved status** until the literature check says otherwise.
- Never describe a result as "solving" a famous problem unless the famous problem's exact statement is what was verified.
- Long campaigns tempt drift. Every week, re-read Sections 3 and 6 of this file and confirm that the code still implements them exactly.

### G. Claim levels, the discovery protocol, and alerts

| Level | Meaning | Evidence required |
|---|---|---|
| C0 | Reproduced a known result | Checker accepts; matches the published value |
| C1 | New verified finite object | Witness file + frozen checker + second independent checker |
| C2 | Exact value for an explicit finite case | C1 witness **and** a complete-search log or a checkable infeasibility certificate (e.g. DRAT/LRAT proof) for the matching bound |
| C3 | Family-level theorem | Written proof; a Lean/Coq formalization where feasible, with axioms reported and no `sorry` |
| C4 | Beats a published record | C1/C2 evidence **plus** a dated check that the published record (table, catalogue, arXiv) has not already moved past it |

**When the checker accepts something that looks like a record (C1 on a frontier target, or any C2–C4):**
1. Freeze a copy in `certificates/` with its SHA-256.
2. Re-verify it with the independent second checker in a fresh process.
3. Re-check the relevant literature and tables for newer results (record the date and URL).
4. Canonicalize and, where meaningful, minimize the object; compute its symmetry group.
5. Write `claims/CLAIM_<id>.md`: exact statement, claim level, how it was checked, what it does not establish, and the one-command reproduction.
6. **Raise an alert**: add an entry at the top of `ALERTS.md` (date, claim ID, level, one-sentence statement, status `awaiting human review`) and copy it into `STATE.md`. If the harness offers a notification tool, use it.
7. **Keep going.** Do not wait for the human. Take the next rung, or generalize the object into a family.

### H. Handoff package (maintained continuously, not only at the end)

Because the campaign has no planned end, keep a handoff-ready package current at all times, refreshed weekly: `README.md` (one-command reproduction), `SOURCE.md` and `DELTA.md` (seed IDs, retained rules, explicit extensions), `PRIOR_ART.md` (dated search log, at least five primary sources inspected, comparison matrix), `SPEC.md`, `checker.py` + independent `checker2.*`, `oracle.py`, `reference.py`, `search/`, `ops/`, `certificates/`, `claims/`, `ALERTS.md`, `LEDGER.jsonl`, `RESULTS.md`, `LIMITATIONS.md`, `META.json` (status, claim levels, verification counts, CPU-hours, versions). `RESULTS.md` always ends with plain English: what the problem asks; what has been established and at which claim level; how it was checked; why it could matter; what it does not establish; the single next experiment with the most information value.

---

## 10. Reference checker — create `checker_reference.py`

Create this file verbatim as your first action (Section 8, step 0). It is a small seed checker that was executed and self-tested when this task was written. It is **not** your acceptance checker: write `checker.py` from `SPEC.md`, then add a test that requires both to agree on every test case.

SHA-256 of the file (UTF-8, ending with a single newline): `afc67c6ab6610c94577a82bef095817ab746baa76d6db62df4651741211514bc`

```python
# checker_reference.py -- P12 Mersenne factor laws: seed checker (exact integer arithmetic only)
import hashlib
from math import gcd

BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
MR_LIMIT = 3317044064679887385961981  # these 12 bases are a proof of primality below this bound

def is_prime_mr(n):
    """Deterministic Miller-Rabin, exact for n < MR_LIMIT."""
    if n < 2:
        return False
    for r in BASES:
        if n % r == 0:
            return n == r
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def pocklington_verify(n, F_primes, witnesses):
    """n-1 = F*R with F built from F_primes {r: e}; F*F > n; for each r a witness a_r with
    a_r^(n-1) = 1 (mod n) and gcd(a_r^((n-1)/r) - 1, n) = 1. Every r must itself be prime (MR)."""
    F = 1
    for r, e in F_primes.items():
        if not (r < MR_LIMIT and is_prime_mr(r)):
            return False, f"F-prime {r} not proven"
        F *= r ** e
    if (n - 1) % F or F * F <= n:
        return False, "F does not divide n-1 or F^2 <= n"
    for r in F_primes:
        a = witnesses[r]
        if pow(a, n - 1, n) != 1 or gcd(pow(a, (n - 1) // r, n) - 1, n) != 1:
            return False, f"witness fails for r={r}"
    return True, "Pocklington certificate valid"

def k_class_ok(p, k):
    """Known law: q = 2kp+1 = +-1 (mod 8)  <=>  k in {0,3} (mod 4) if p = 1 (mod 4), k in {0,1} (mod 4) if p = 3 (mod 4)."""
    return (k % 4 in (0, 3)) if p % 4 == 1 else (k % 4 in (0, 1))

def verify_factor(p, q, cert=None):
    """Accept iff q is a PRIME divisor of M_p = 2^p - 1 (p an odd prime)."""
    if p < 3 or not is_prime_mr(p):
        return False, "p is not an odd prime"
    if q < 3 or (q - 1) % (2 * p):
        return False, "q is not of the form 2kp+1"
    if q % 8 not in (1, 7):
        return False, "q is not +-1 mod 8"
    if pow(2, p, q) != 1:
        return False, "q does not divide M_p"
    k = (q - 1) // (2 * p)
    if k <= 2 * p + 1:
        return True, f"prime factor, k={k} (prime by the k <= 2p+1 lemma)"
    if q < MR_LIMIT:
        return (True, f"prime factor, k={k} (deterministic MR)") if is_prime_mr(q) else (False, f"composite divisor, k={k}")
    if cert is None:
        return False, "q >= MR_LIMIT needs a Pocklington certificate"
    ok, msg = pocklington_verify(q, *cert)
    return (True, f"prime factor, k={k} ({msg})") if ok else (False, msg)

def primes_upto(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]

def census(P_lo, P_hi, K):
    """All (p, k) with p prime in [P_lo, P_hi], 1 <= k <= K, q = 2kp+1 a prime divisor of M_p."""
    out = []
    for p in primes_upto(P_hi):
        if p < max(P_lo, 3):
            continue
        for k in range(1, K + 1):
            if not k_class_ok(p, k):
                continue
            q = 2 * k * p + 1
            if pow(2, p, q) == 1 and (k <= 2 * p + 1 or is_prime_mr(q)):
                out.append((p, k))
    return out

def canonical_hash(pairs):
    text = "".join(f"{p} {k}\n" for p, k in sorted(pairs))
    return hashlib.sha256(text.encode()).hexdigest()

def commit(prediction_bytes):
    return hashlib.sha256(prediction_bytes).hexdigest()

if __name__ == "__main__":
    print("M11 factors 23, 89:", verify_factor(11, 23), verify_factor(11, 89))
    print("M29 factors:", [verify_factor(29, q)[0] for q in (233, 1103, 2089)])
    print("2047 = 23*89 rejected as composite:", verify_factor(11, 2047))
    print("mutations rejected:", not verify_factor(11, 25)[0], not verify_factor(13, 53)[0], not verify_factor(15, 31)[0])
    print("Pocklington on q=89 (p=11):", pocklington_verify(89, {2: 3, 11: 1}, {2: 3, 11: 3}))
    print("bad Pocklington witness rejected:", not pocklington_verify(89, {2: 3, 11: 1}, {2: 2, 11: 3})[0])
    c = census(3, 200, 10000)
    print("census p<=200, k<=10000:", len(c), "factors; k-mod-4 law holds:", all(k_class_ok(p, k) for p, k in c))
    print("census sha256[:16]:", canonical_hash(c)[:16])
    print("smallest-k factor of M43, M47, M53:", [min(k for p, k in c if p == t) for t in (43, 47, 53)])
    print("commit('law: test') =", commit(b"law: test")[:16])
```

Expected output of `python3 checker_reference.py`:

```text
M11 factors 23, 89: (True, 'prime factor, k=1 (prime by the k <= 2p+1 lemma)') (True, 'prime factor, k=4 (prime by the k <= 2p+1 lemma)')
M29 factors: [True, True, True]
2047 = 23*89 rejected as composite: (False, 'composite divisor, k=93')
mutations rejected: True True True
Pocklington on q=89 (p=11): (True, 'Pocklington certificate valid')
bad Pocklington witness rejected: True
census p<=200, k<=10000: 46 factors; k-mod-4 law holds: True
census sha256[:16]: 4c37caf1201fe83d
smallest-k factor of M43, M47, M53: [5, 25, 60]
commit('law: test') = 281f1f73203c990b
```

---

**Start now with Section 8, step 0. Produce evidence before persuasion, and do not stop while budget remains.**
