# Mersenne factor laws — Windows build v0.3

Exact Python + C verification, independent exhaustive censuses, immutable
certificates, preregistered predictions, and bounded resumable jobs.
Built from the P12 brief, with the supplied v0.1/v0.2 sources inspected and
preserved under `archive/supplied-source/`. Original ZIPs remain untouched.

## Build and verify

On this Windows machine, open PowerShell in this directory and run:

```powershell
.\run.ps1 all
```

This builds the three native executables, runs the tests, and rechecks every
certificate using both independent factor checkers and exhaustive engines.
Python 3.10+ and GCC/Clang with unsigned 128-bit arithmetic are required.
GNU mini-gmp 6.3.0 is vendored with licenses and pinned file hashes; there are
no Python package dependencies. Windows uses MinGW-w64; no WSL is needed.

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
