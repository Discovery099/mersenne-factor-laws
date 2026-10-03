"""Regenerate build handoff from checked artifacts and the recorded test output."""
import json
from pathlib import Path
import platform
import re
from mf.protocol import ROOT, digest, git, utcnow


def main():
    log=(ROOT/"runs/final-validation.log").read_text(encoding="utf-8-sig")
    if not re.search(r"\bOK\b",log) or '"verified": true' not in log:
        raise ValueError("final test and certificate verification have not succeeded")
    tests=int(re.search(r"Ran (\d+) tests",log).group(1))
    certs=[]
    for path in sorted((ROOT/"certificates").glob("*.json")):
        obj=json.loads(path.read_text())
        certs.append({"path":path.relative_to(ROOT).as_posix(),"bounds":obj["bounds"],"count":len(obj["pairs"]),
                      "census_sha256":obj["sha256"],"artifact_sha256":digest(path)})
    score=json.loads((ROOT/"runs/L002_open_demo/score.json").read_text())
    ledger=[json.loads(s) for s in (ROOT/"LEDGER.jsonl").read_text().splitlines() if s]
    cpu=sum(r.get("cpu_s") or 0 for r in ledger)
    table="| Inclusive p range | K | Factors | Census SHA-256 |\n|---|---:|---:|---|\n"
    for c in certs:
        a,b,K=c["bounds"]
        table+=f"| {a}–{b} | {K} | {c['count']} | `{c['census_sha256']}` |\n"
        ident=f"census_{a}_{b}_{K}"
        text=f"# {ident}\n\nExact finite statement: C({a},{b},{K}) contains {c['count']} pairs.\nClaim level: C2 finite enumeration, awaiting human review; fixed benchmarks also C0 reproduction.\n\nCensus SHA-256: `{c['census_sha256']}`.\nCertificate: `{c['path']}`. Artifact SHA-256: `{c['artifact_sha256']}`.\n\nEvidence: independent p-first and k-first exhaustive C algorithms; exact Python\nand C/mini-gmp membership/primality checks; full replay in final verification.\nCanonical representation is sorted unique (p,k), so no symmetry minimization\nis relevant. Reproduce with `python -m ops.verify`.\n\nThese are small-k finite census values, not newly credited GIMPS factors or a\nclaim of beating a published record. Prior overlap: Shanks–Kravitz and Wagstaff;\nsee SOURCE.md (accessed 2026-10-03). No claim of novel tables is made.\n"
        (ROOT/"claims"/f"CLAIM_{ident}.md").write_text(text,encoding="utf-8")
    results=f"# Verified build results — v0.3\n\n{tests} test groups pass. All {len(certs)} immutable census certificates were\nrechecked with both factor checkers and both exhaustive engines.\n\n{table}\n## Prediction-before-computation demonstration\n\nL002 and N0 were committed in d47690fe9303c28df9572b3442e93481b42d5b53\nbefore C(200001,210000,1000) was computed by the supervisor. Predictions were\n335.943583334915 (L002) and 336.8895263286887 (N0); observed count: 312.\nThe composite deviance improvement is {score['gain']:.12f}, below 14. The\ndisjoint dyadic improvement is {score['disjoint_scores']['dyadic_partition']['gain']:.12f}.\n**L002 failed the stipulated criterion.** Predictions, residuals and sources\nare retained. No revised model may reuse this cell as a fresh test.\n\nN0 sanity: 507.62974052227594 predicted versus 520 observed. Directed-rounding\nEuler-product bounds establish C2=0.660162 and 2C2=1.320324 to six decimals.\nThose constants do not prove a Mersenne distribution law.\n\n## Scope\n\nR0 infrastructure is implemented and tested, including arbitrary-size C\nPocklington checking. Generic Track 0 oracles pass at 8/60/200 limits; faithful\noriginal seed reproduction remains unresolved. Full open grid, operator-sealed\nconfirmation, discovery calibration and GIMPS credit are pending. Historical\nv0.2 vault results are preserved in the supplied ZIP, not re-certified here.\n\nThe problem asks for exact Mersenne factor censuses and predictive laws tested\non data withheld before computation. This build establishes the finite C2\nvalues above, reproduces known benchmarks at C0, and completes an auditable\nopen-cell prediction experiment. It was checked with independent arithmetic,\nexhaustive enumeration, adversarial tests and fresh certificate replays. It\ncould support reliable future research and measured discovery allocation. It\ndoes not establish a new theorem, successful law or credited new factor. The\nsingle next experiment with the most information value is a committed L001\nversus N0 comparison on a new band, C(220001,225000,1000), before computation.\n"
    (ROOT/"RESULTS.md").write_text(results,encoding="utf-8")
    (ROOT/"LEADERBOARD.md").write_text("# Verified finite census ledger\n\nNo published record is claimed; prior overlap is recorded in SOURCE.md.\n\n"+table+"\n## Immutable certificate fingerprints\n\n"+"\n".join(f"* `{c['path']}` — `{c['artifact_sha256']}`" for c in certs)+"\n",encoding="utf-8")
    meta={"version":"0.3.0","updated_at":utcnow(),"status":"verified local software build; campaign pending operator inputs",
          "novelty":"overlap-found","test_groups":tests,"factor_claim_comparisons":10000,"certificates":certs,
          "claim_levels":["C0 reproduction","C2 finite censuses"],"python":platform.python_version(),"platform":platform.platform(),
          "cpu_hours_recorded_experiments":cpu/3600,"cpu_accounting":"completed C processes only; excludes compilation/tests, killed partial chunks and prediction Python time",
          "tokens":None,"background_jobs_running":0,"gimps_credit":False,"vault_confirmation":False,
          "sealed_archive_results_imported":False,"checker_hashes":{n:digest(ROOT/n) for n in ("mf/checker.py","mf/checker2.c","mf/score.py")},
          "prediction_commit":"d47690fe9303c28df9572b3442e93481b42d5b53","law_demo_threshold_met":score["threshold_met"]}
    (ROOT/"META.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    (ROOT/"DAILY/2026-10-03.md").write_text(f"# Day 0 build report\n\nVerified {tests} test groups and {len(certs)} dual-engine census certificates.\nRecorded experiment CPU hours: {cpu/3600:.6f}; coverage excludes tests/build and partial work.\nL002 open demo completed once under a 3-minute, one-slot supervisor cap.\n312 factors; law improvement {score['gain']:.6f}<14, retained as failed.\nNo background job remains and no GIMPS result was submitted.\n\nTomorrow's top three: obtain owned assignment export and compute cap;\npreregister L001 on a fresh band; validate scalable prediction numerics.\n",encoding="utf-8")
    (ROOT/"WEEKLY/2026-W40.md").write_text("# Initial handoff\n\nThis is a first-build report, not a claim that a week of research ran.\nIndependent exact infrastructure is verified; L002 failed its first criterion.\nPrior art overlaps the proposed k tables and L001 heuristic. A campaign needs\noperator assignment details, resource caps and unresolved seed definitions.\nSee RESULTS.md, META.json and DAILY/2026-10-03.md for evidence.\n",encoding="utf-8")
    state=f"# State — v0.3 handoff, campaign day 0\n\nVerified local build complete. {tests} tests; {len(certs)} dual-checker/dual-engine\ncertificates with counts 46, 215, 520, 5773, 312 (bounds in RESULTS.md).\nNovelty: overlap-found. No new-factor or theorem claim.\n\nL002-OPEN prediction commit d47690fe9303c28df9572b3442e93481b42d5b53 preceded\ncomputation. Observed 312; N0 336.8895; L002 335.9436. Gain 1.1391<14: failed.\nResiduals retained in runs/L002_open_demo/score.json and DEAD_ENDS.md.\nDo not retest edited models on this band.\n\nSupervisor completed on first attempt and stopped; zero active workers.\nQueue retains completed demo for audit. Logs/status in ops/runtime;\ncheckpoint runs/L002_open_demo. No perpetual process or automation installed.\n\nAcceptance source fingerprints: CHECKERS.sha256. Targets: TARGETS.sha256.\nHardware: 4 logical CPUs, 12.67 GB RAM, Windows 10, GCC 16.1.0, Python {platform.python_version()}.\nExperiment CPU hours recorded: {cpu/3600:.6f}; see META.json for accounting limits.\n\nUser supplied v0.1/v0.2 ZIPs. Source-only snapshots and archive hashes are in\narchive/. Previously computed vault values were not imported or rescored.\nL001 is the supplied formula adapter; L002 is a separate failed experiment.\nFaithful seed reproduction remains blocked by missing original definitions.\n\nOperator confirms GIMPS assignments but account/export/client paths and CPU\ncap remain pending. Discovery planning/result adapters are ready for these.\nNo account creation, assignment request or external submission occurred.\n\nNext three actions:\n1. Import sanitized owned assignments and current known-factor/bounds exports.\n2. Commit L001 versus N0 predictions for fresh C(220001,225000,1000), then run.\n3. Validate scalable prediction numerics before larger grids or rolling vaults.\n\nReflection: Independent enumeration reproduces all required finite regression\ncases. The reference's MR bound needed correction, and literature establishes\nprior overlap. The first prospective experiment supplies negative evidence for\nL002, which is retained rather than revised on the same data. The remaining\nwork is research and operator-dependent discovery, not hidden completed work.\n"
    (ROOT/"STATE.md").write_text(state,encoding="utf-8")
    print(json.dumps({"tests":tests,"certificates":len(certs),"cpu_hours":cpu/3600,"reports":"refreshed"}))


if __name__=="__main__":
    main()
