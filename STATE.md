# State — build v0.3, campaign day 0

Original task: build the supplied P12 project. User subsequently supplied
v0.1 and v0.2 ZIPs and confirmed having GIMPS assignments; details pending.

Reference hash/output reproduced. Two C engines and independent Python/C
arbitrary-integer factor checkers built natively on Windows. Completed fixed
censuses: 46, 215, 520, 5773 factors; hashes stored in certificates and ledger.
N0 sanity expectation: 507.62974052227594. Directed constant enclosure confirms
C2=0.660162 and 2C2=1.320324 to six decimal places.

Novelty: overlap-found. Supplied v0.2 L001 is a known heuristic. Source-only
archive import preserves provenance; vault outputs are not used in this build.
R1 exact seed reproduction remains unresolved; generic bounded oracles tested.

Active hypothesis: L002 finite-prime tail correction; prospective open band
200001–210000, K=1000. Next: freeze predictions before computing this band.
No background campaign currently running. No discovery assignment imported.
No external result submitted. Long-run resource cap remains pending.

Hardware: Windows, 4 logical CPUs, 12.67 GB RAM; GCC 16.1.0 MinGW-w64.
Checker SHA-256 values are frozen in CHECKERS.sha256 before the demonstration.

Next three actions:
1. Finish protocol fault tests and commit the source snapshot.
2. Preregister L002 open demonstration; run it through a one-slot bounded queue.
3. Score, reverify certificates, refresh handoff and deliver a portable ZIP.

Reflection: Independent enumeration agrees with every disclosed benchmark.
The brief's MR claim needed correction, and prior literature refutes its
suggested novelty premise. The supplied archives add useful history, but their
completed vault outputs cannot be relabelled as new blind results. The useful
next evidence is an auditable prediction-before-computation run on fresh data.
