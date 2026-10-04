P12 technical report by Chris Miki, with source code, complete census outputs,
certificates, forecasts and external operator reviews.

Two independent exhaustive engines found 487,025 factor pairs over prime
exponents 10,000,001 through 30,000,000 with k at most 10,000. The operator's
region 2 census and four summary cells matched exactly. The supplied region 1
review reports 307,582 factors and the matching sealed hash, with L001 deviance
72.01 versus N0 209.98 (gain 137.97).

L003 is a zero-fit Poisson-binomial correction to this project's L001 Poisson
approximation, consistent with established prior art. The report preserves
the remaining discrepancy and the missing external pre-run timestamp for
region 2. It makes no new-theorem, new-law or credited-factor claim.

Original code is MIT-licensed; the report is CC BY 4.0. Third-party notices
and source licences are retained in LICENSING.md and vendor/.

Use a full Git checkout or the accompanying history bundle, then run
`python -m ops.vault_report` from the repository root to audit the saved
experiment without repeating a census. The release archive alone must not
be assumed to contain Git history. See README.md for full replay commands.
