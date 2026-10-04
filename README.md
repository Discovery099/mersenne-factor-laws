# Mersenne factor laws — Windows build v0.4

The bounded P12 comparison is complete. [Chris Miki's closeout report](output/pdf/P12_Chris_Miki.pdf)
records exact counts, the externally reported region 2 match, the missing
external pre-run timestamp, model comparisons and residuals. Editable source:
[reports/P12_Chris_Miki.tex](reports/P12_Chris_Miki.tex).

The 4 October revision includes the full supplied region 1 review, saved in
`data/sources/REVIEW_VAULT_S1_L001.md` with its SHA-256 recorded in `SOURCE.md`.
Section 5 transcribes its census hash, 72.01 versus 209.98 deviances and
137.97 gain, with explicit external-review qualifications. No census was rerun.

Exact Python + C verification, independent exhaustive censuses, immutable
certificates, preregistered predictions, and bounded resumable jobs.
Built from the P12 brief, with the supplied v0.1/v0.2 sources inspected and
preserved under `archive/supplied-source/`. Original ZIPs remain untouched.

The v0.4 research additions implement zero-fit L003 multiplicity predictions,
prospective power checks, a scalable prediction-only engine, and a multi-law
registration for the fixed Vault-S region 2 plus a separately named extension.
See `REGISTRATION.md` and `POWER_PROTOCOL.md`. The user authorized the full
committed census after receiving the prediction SHA-256. Execution state is
recorded in `runs/Vault_S2_full/progress.json`; region 1 has not been rerun.
The original exact-tool and v0.3 experiment source fingerprints remain unchanged.

## Code and data availability

The complete experiment and full Git history are available in the public
[Discovery099/mersenne-factor-laws repository](https://github.com/Discovery099/mersenne-factor-laws).
Zenodo archival publication is in progress; no archive DOI is claimed yet.
Original code is [MIT-licensed](LICENSE); the report and LaTeX source are
[CC BY 4.0](LICENSE-REPORT.txt), copyright 2026 Chris Miki. Third-party source
and external reviews retain their own rights and attribution. See
[LICENSING.md](LICENSING.md) for the scope and vendored GNU mini-gmp terms.
`CITATION.cff` and `.zenodo.json` provide the release's citation metadata.
The prepared release procedure is in [RELEASE.md](RELEASE.md).

Reproducibility materials:

- `mf/`, `laws/`, `ops/`, `tests/`: exact engines and checkers, models, execution and validation.
- `predictions/Vault_S2_L001_L002_L003.json`: frozen forecasts and source hashes, with links to the prospective power artifacts.
- `runs/Vault_S2_full/`: both engines' 40 chunk outputs, run records, and regional and union subdirectories containing `census.txt`, `summary_cells.json` and `score.json`.
- `certificates/`: explicit factor pairs and verification records; `results/Vault_S2_full/`: audit and result tables.
- `REGISTRATION.md`, `POWER_PROTOCOL.md`, `SOURCE.md` and `data/sources/`: design, source provenance and attributed external confirmations.

Preserve full Git history and all tracked run data when sharing or cloning.
The audit checks prediction commit `0a3a73847f3f533dae5fcface0c0abd5099801cb`
and execution provenance; completed results were committed as
`b1540d0360028c7982f58c24481e8707f62e7454`. A shallow checkout or source-only
ZIP cannot supply that history. `.gitattributes` preserves exact file bytes.

For a saved-artifact audit, use Python 3.10+ and Git, then run from this root:

```sh
python -m ops.vault_report
```

This checks existing evidence and frozen scores and refreshes the generated
audit and result tables. It does not run a census, repeat primality checks or
create an external pre-run timestamp. Audit timestamps may change; the
canonical census and prediction fingerprints must stay fixed.

For independent computational replay, use a separate full checkout, Python
3.12 (3.12.14 was used here), Git and a C11 GCC/Clang compiler with unsigned
128-bit support (MinGW-w64 on Windows), then run:

```sh
python -m pip install -r requirements-research.txt
python -m ops.build
python -m unittest discover -s tests -v
python -m ops.verify
```

The last command checks every stored certificate with both factor checkers
and repeats every stored census with both engines, including overlapping
regional and union certificates. It is substantially more expensive than the
saved-artifact audit. Compare the canonical hashes listed in the report.
Such replays are verification of observed data, not fresh sealed tests.

## Build and verify

On this Windows machine, open PowerShell in this directory and run:

```powershell
.\run.ps1 all
```

This builds the three native executables, runs the tests, and rechecks every
certificate using both independent factor checkers and exhaustive engines.
It deliberately repeats the exhaustive censuses, including large certificates.
To audit the completed Vault-S run's recorded evidence and recompute its frozen
scores without repeating enumeration, use `.\run.ps1 audit` on Windows or
`python -m ops.vault_report` directly (`make audit` on Unix).
That audit requires the full run to have completed and verifies both engines'
saved census bytes, coverage, prediction provenance, certificates and summaries.
Python 3.10+ and GCC/Clang with unsigned 128-bit arithmetic are required.
GNU mini-gmp 6.3.0 is vendored with licenses and pinned file hashes; there are
no Python package dependencies for the exact tools. The accelerated research
predictor and its additional tests use NumPy (`requirements-research.txt`).
Windows uses MinGW-w64; no WSL is needed.

On Linux/macOS with an appropriate GCC/Clang compiler:

```sh
make test verify PYTHON=python3
```

`make test-full` additionally produces the large fixed regression census.
`python -m ops.build` is the cross-platform equivalent of `make build`.
Read `RESULTS.md` for verified counts and `LIMITATIONS.md` for research status.

## Exact tools

```sh
python -m mf.checker factor 11 89
mf/checker2.exe 11 89
mf/census_kp.exe 3 200 10000
python -m mf.checker census runs/example.txt --bounds 3 200 10000
python -m mf.stats runs/example.txt --bounds 3 200 10000
```

Omit `.exe` on Unix. Engines emit canonical `p k` rows; other normal command
results are JSON. In PowerShell use the supervisor or Python file handles to
save census bytes: older PowerShell redirection may re-encode native stdout.
Canonical input is sorted ASCII with LF line endings and no duplicate pairs.
Factor verification proves membership; completeness requires exhaustive
replay. Engine bounds enforce `2*hi*K+1 < 2^63` and documented resource limits.

For large factors, `--certificate CERT.json` takes distinct `[r,e,a]` triples
for Pocklington; C takes the equivalent `r:e:a` arguments. Supplied certificates
are always checked. No PRP result is silently accepted as primality.

## Prediction-first jobs

Choose a genuinely unseen open exponent band, then:

```sh
python -m mf.campaign preregister next_open --bounds 220001 225000 1000 --law laws/L002.py
```

This computes only theoretical predictions, writes them once, records their
hash in `ALERTS.md`, and commits both the predictions and their source closure.
It refuses overlap with recorded observations and archive run regions.
Review and append this line to `ops/queue.jsonl`:

```json
{"id":"next_open","kind":"census","predictions":"predictions/next_open.json","checkpoint":"runs/next_open","seed":12,"hours":0.25,"chunk":1000}
```

```sh
python -m ops.supervisor run --slots 1 --hours 0.25
python -m mf.score --law laws/L002.py --predictions predictions/next_open.json --census runs/next_open/census.txt --manifest runs/next_open/manifest.json
python -m ops.supervisor status
```

`ops/start.ps1 -Hours 1 -Slots 1 -Python PATH` starts a hidden detached Windows
supervisor. It rereads the queue, retries crashes at most three times, retains
checkpoints, and respects the explicit budget. Removing a running queue entry
cancels that child process tree. Budget expiry is unknown, not a proof of
absence. Resume with a new queue ID and an explicit new budget pointing at the
same checkpoint, keeping seed, predictions and binary hashes unchanged.

The source hashes are frozen: changing an acceptance, prediction, scoring or
execution dependency invalidates the old active protocol until a versioned
reverification/migration is performed. Local git dates are an audit trail,
not a trusted external timestamp. No perpetual job or scheduled automation is
installed by this build. A persistent host is required for unattended work.
Git attributes disable line-ending conversion so a checkout preserves the
exact bytes covered by the registered SHA-256 values.

## Supplied versions and discovery

L001 is a scalar standard-library adapter of the supplied v0.2 formula. Its
original NumPy/interpolation code is retained in the source archive. L002 is
a separate finite-local-prime correction experiment, without fitted parameters.
Neither is presented as a new theorem. Non-overlapping dyadic scores are
reported separately from the dependent marginal-summary score.

The v0.2 ZIP contains historical vault results. Their contents were not
imported into this build's model or certificate store, and their historical
claims have not been re-certified here. This build does not claim a new sealed
test of those same cells. See `IMPORT_REVIEW.md`.

The operator has GIMPS assignments; account name, assignment export, installed
tool paths and CPU budget are pending. `discovery/README.md` specifies the
inputs for allocation, matched A/B planning, GMP-ECM command preparation and
dual-checker result packaging. PrimeNet submission uses the operator's official
client. No new factor or credited discovery is claimed by this software build.
