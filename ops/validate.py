import argparse
import json
import time
from mf.checker import parse_census, census_hash, verify_census
from mf.protocol import ROOT, write_once, digest, utcnow
from mf.stats import summary
from .common import execute_engine, second_checker, ledger


def validate(bounds):
    start=time.monotonic()
    evidence=[]
    results=[]
    for name in ("census_kp","census_pk"):
        raw,timing=execute_engine(name,bounds)
        results.append(parse_census(raw))
        evidence.append(timing)
    if census_hash(results[0]) != census_hash(results[1]):
        raise ValueError("independent census mismatch")
    pairs=results[0]
    verify_census(pairs,bounds)
    second_checker(pairs)
    stats=summary(pairs,*bounds)
    lo,hi,K=bounds
    path=ROOT/"certificates"/f"census_{lo}_{hi}_{K}_{stats['sha256'][:12]}.json"
    cert={"schema":1,"kind":"census","bounds":list(bounds),"pairs":pairs,"sha256":stats["sha256"],
          "statistics":stats,"execution":{"purpose":"fixed infrastructure regression, not a sealed law test","completed_at":utcnow(),"engines":evidence}}
    if not path.exists():
        write_once(path,(json.dumps(cert,sort_keys=True,indent=2)+"\n").encode())
    elif json.loads(path.read_text())["sha256"] != stats["sha256"]:
        raise ValueError("existing certificate differs")
    ledger("regression-census",list(bounds),12,time.monotonic()-start,sum(t["cpu_s"] or 0 for t in evidence),True,
           "both exhaustive engines and both checkers agree",str(path),checker_sha256=digest(ROOT/"mf/checker.py"))
    return {"bounds":list(bounds),"count":len(pairs),"sha256":stats["sha256"],"artifact_sha256":digest(path),"seconds":time.monotonic()-start}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--full",action="store_true")
    args=ap.parse_args()
    cells=[(3,200,10000),(1000,3000,20000),(10000,20000,1000)]
    if args.full:
        cells.append((3,100000,10000))
    for bounds in cells:
        print(json.dumps(validate(bounds),sort_keys=True),flush=True)
