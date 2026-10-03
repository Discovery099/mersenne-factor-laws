# Track 0 input contracts

These are explicit reconstructions from the supplied summaries, not claims to
have recovered omitted seed inputs or objective conventions.

* 01002: `enumerate_forests(queries,budget)` enumerates every arithmetically
  possible divisor-parent map on up to eight supplied integers. Parent -1
  denotes a root; each graft consumes one token. Local prime leaves multiply
  to query/parent, and recursive leaf multiplication reconstructs each query.
  Cycles fail. Objective is (maximum recursive depth, grafts). With unlimited
  direct factorization, the all-root forest is necessarily optimal; a more
  restrictive token-grafting objective needs the missing seed conventions.
* 00302: `histogram(R,x,y,px,py,cap)` takes two factorial quotients as
  `(numerator,denominator)`, with each list containing affine arguments `(a,b)`
  for `(a*n+b)!`. Domain is **0<=n<=R**, R<=60. Direct integer quotients and
  Legendre valuations must agree; nonintegral quotients are refused. Example:
  central binomial coefficients are `([(2,0)],[(1,0),(1,0)])`.
* 00902: exclusions are `(modulus,residue)` on **1<=n<=N**, N<=200. The direct
  oracle and marking sieve must agree despite overlapping progressions.
  Cache refinement requires an explicit projection of every refined residue
  to its old class. Conflicting or missing cache observations are returned as
  ambiguity classes, never guessed away.

The boundary conventions and generic schemas above are additions necessitated
by missing detail, recorded in DELTA.md. Tests exercise all stated seed limits.
