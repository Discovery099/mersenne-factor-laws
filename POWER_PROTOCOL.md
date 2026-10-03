# Power gate — operator rule, 2026-10-03

Before any new preregistered test, compute expected deviance differences under
each competing model. Require at least 14 in **both** directions before a
comparison is eligible for preregistration. If insufficient, enlarge the
prospective design before committing it. Do not inspect outcomes to choose
the cell. Retain L002_open_demo as a failed, underpowered historical test.

For a cell with true mean a and alternative b,

    E_a[D(Y,b)-D(Y,a)] = 2*(b-a+a*ln(a/b)).

The Y*ln(Y) terms cancel, so this identity holds for any count distribution
with E[Y]=a, including the maximum cell. For independent Poisson cells it is
twice the KL divergence. With overlapping counts or a non-Poisson maximum it
is the expected prescribed diagnostic score, not a likelihood ratio. An
expected gain of 14 is the operator's design rule; it is not an assertion of
80%/95% statistical power. Both directions and every selected cell are saved.

Report separate matrices for the three multiplicity cells, the disjoint
dyadic count partition, and the task's combined summary. Identical expected
cells add zero information; overlapping cells must not be multiplied or
duplicated merely to inflate power. L003 comparisons principally concern the
multiplicity cells because its factor-count means equal L001.

Vault-S region 2 is fixed at [10000001,20000000], K<=10000. It must not be
silently redefined if a comparison is underpowered. Any supplementary region
must be separately identified and outside all previously observed/sealed
ranges. The region 2 subrecord stays unchanged. Source and prediction commits
must precede any census. The user must receive the prediction SHA-256 first.

Region 1 must never be rerun for this request. Operator confirmation is an
external source, not permission to fit on its values or rewrite its history.
