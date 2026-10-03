# Build host — 2026-10-03

Windows, 4 logical processors, 12,670,570,496 bytes physical RAM (11.80 GiB).
At initial inspection C: used about 474.8 GB, free about 274.8 GB.
PowerShell native equivalents were used for nproc/free/df; no WSL assumption.

GCC: MinGW-w64 x86_64 UCRT POSIX, WinLibs GCC 16.1.0.
Python: bundled Codex workspace runtime (actual version in META.json).
Independent C checker: GNU mini-gmp 6.3.0.

Validation and the prospective demonstration use bounded single-worker runs.
No GPU was assumed or benchmarked. Long-campaign slot count and CPU-hour cap
remain operator choices. Binary hashes are recorded by ops/build.py.
