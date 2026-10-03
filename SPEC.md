# Specification, version 1

The supplied P12 brief is a project specification, not authority to make external
submissions or consume unbounded CPU. This implementation keeps research claims
separate from software capability. Vault-S is not computed during the build.

## Objects and exact acceptance

p is an odd prime; k is a positive integer; q=2kp+1 is prime and 2^p mod q=1.
C(lo,hi,K) contains all such (p,k) for inclusive lo<=p<=hi and 1<=k<=K.
Canonical bytes are ASCII `p k\n` sorted by (p,k), without duplicates. SHA-256
identifies these bytes. A list passing factor verification proves membership,
not completeness. Completeness evidence requires both exhaustive engines,
identical bounds, independent hashes and an execution manifest.

Acceptance uses integers only. Approximate logs, expectations and deviances live
outside the acceptance checker. Exponents must be below the proven MR bound;
unsupported exponents are rejected as unproved, not labelled composite.

## Proofs

**Factor form.** A prime divisor r of 2^p-1 has ord_r(2)=p: its order divides p
and cannot be 1. Thus p divides r-1; r is odd, so 2p divides r-1. Also
2^((r-1)/2)=(2^p)^((r-1)/(2p))=1 mod r. Euler's criterion and the supplementary
quadratic reciprocity law give r=1 or 7 mod 8.

**L1.** Reducing 2kp+1=1 or 7 mod 8 gives kp=0 or 3 mod 4.
If p=1 mod 4, k=0 or 3 mod 4; if p=3 mod 4, its inverse is 3 and k=0 or 1.

**L2.** If q divides 2^p-1, every prime divisor r of q has ord_r(2)=p
(the brief reverses the order notation in one sentence). Therefore r>=2p+1.
A composite q, including a prime power, is at least (2p+1)^2. Comparing with
q=2kp+1 gives k>=2p+2. Hence k<=2p+1 proves primality after divisibility.

**L3.** For prime q=2kp+1, the multiplicative group is cyclic of order 2kp.
Its 2k-th powers form its unique subgroup of order p, exactly the roots of x^p=1.
Thus 2 is such a power iff 2^p=1 mod q. Since q>=7, 2 is not the identity,
so its order is exactly p. No assumption gcd(2k,p)=1 is needed.

## Primality correction and certificates

The reference is preserved byte-for-byte. Its twelve bases through 37 do NOT
justify its advertised bound. The production checkers use thirteen bases
through 41 and require n<3317044064679887385961981. The twelve-base
counterexample is 318665857834031151167461. See Sorenson--Webster (SOURCE.md).
Agreement with the reference is required on its sound domain, not on that bug.

A Pocklington certificate is a nonempty JSON list of distinct `[r,e,a]` triples.
r is proven prime by bounded deterministic MR, e is a positive integer, and
F=product(r^e) divides n-1 with F^2>n. For every r, 1<a<n,
a^(n-1)=1 mod n and gcd(a^((n-1)/r)-1,n)=1. These conditions prove n prime.
Supplying a certificate always verifies it, even if MR or L2 could suffice.
The C interface encodes each triple as `r:e:a`. Unsupported ECPP certificates
are refused; there is no probable-prime acceptance fallback.

## Census algorithms and residue soundness

A iterates p then k, uses a fresh incremental small-prime progression sieve
for each p, and Montgomery exponentiation. B iterates k then p, marks q in a
fresh sieve over the integer p interval, and uses ordinary 128-bit remainders
and a separate deterministic 64-bit prime test. Both preserve q equal to the
sieving prime. They share no modular-arithmetic or primality implementation.
Bounds satisfy 2*hi*K+1<2^63; invalid/overflowing inputs fail before allocation.
For r not dividing 2p, the forbidden k class is -(2p)^(-1) mod r.
For r dividing 2p, q=1 mod r and nothing is struck. B uses the corresponding
class p=-(2k)^(-1) mod r. No cached residue is reused across exponents.
Track 0 implements explicit projection validation and ambiguity classes for
experiments that do reuse residues. Invalid refinements are rejected.

## Statistics

Dyadic bucket j means 2^j<=k<2^(j+1). Residue moduli are 3,4,5,8,12,24,60.
Valuations are capped at 6 with minimum p per occupied bin. LPF(1)=1;
its smoothness bin is j=0 (also containing LPF=1). All other LPFs use ordinary
dyadic bins. Multiplicity includes prime exponents with zero factors, using
the declared inclusive bounds, even when the census list is empty.

## Predictions and scoring

N0 is implemented literally: for an L1-allowed pair the weight is
product(r/(r-1), primes r<=47)/(k*ln(q)) if no such r divides q, else zero.
In particular N0 gives zero when q itself is a small prime; this is a feature
of the specified baseline, not silently corrected. Expectations are numerical
approximations and never certify a factor.

Law L002 is a zero-fit, finite-local-prime correction hypothesis, with its
assumptions in laws/L002.md. It does not claim a new Kummer theorem or a
six-digit global constant. The source closure (law, N0, prediction helpers,
checker and scorer) is hashed and committed. Source size <=2000 gzip bytes
applies to the whole predictor closure except the declared fixed N0 baseline
and generic statistics aggregator; a predictor may not hide lookup tables
in dependencies. Fitted parameters <=8; fitting provenance must lie in the
open region. This implementation ships no fitted law.

Predictions are write-once. Before computing a cell, the worker verifies a git
commit containing identical prediction bytes and their SHA in ALERTS.md,
records HEAD, bounds, timestamp and the frozen source hashes. Scoring checks
those hashes, ancestor relationship and time ordering. This is an audit trail,
not a cryptographic trusted clock: a malicious operator can rewrite local git.
Overlapping summary cells are dependent; summed Poisson deviances are reported
as a descriptive composite score, not automatically a likelihood ratio.
D(y,mu)=2*(mu-y+y*ln(y/mu)), D(0,mu)=2mu. Positive y with mu=0 gives infinity.
Threshold: D(N0)-D(law)>=2*fitted_parameters+14. Vault-S certification remains
operator-only. Revisions may only test cells not already observed.

## Seed reconstruction limits

Only the summaries in the supplied brief exist. Track 0 provides exhaustive
parent-map forest checks (<=8 labelled nodes), direct factorial-quotient
valuation histograms (R<=60), and direct AP sieve enumeration (N<=200), with
independent implementations. Forest topology/token accounting and the actual
factorial quotients are not fully specified in the summary. Explicit generic
input schemas are documented in mf/track0/README.md. Passing these tests is
not represented as exact reproduction of unavailable seed instances.
