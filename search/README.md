# Search implementation

The two independent native census engines live in `mf/census_kp.c` and
`mf/census_pk.c`, as prescribed by the task's public CLI. The campaign entry
point is `ops/worker.py`, launched through `ops/supervisor.py` and its queue.
Acceptance code imports neither this directory nor the engines.
