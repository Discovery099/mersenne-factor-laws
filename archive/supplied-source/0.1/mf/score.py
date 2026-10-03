import argparse
import json
import math
from .checker import read_pairs
from .stats import stats


def deviance(y,mu):
    if not math.isfinite(mu) or mu<0 or y<0:
        raise ValueError("invalid counts")
    if mu==0:return 0.0 if y==0 else math.inf
    return 2*mu if y==0 else 2*(mu-y+y*math.log(y/mu))


def score(observed,law,null,parameters):
    if type(parameters) is not int or not 0<=parameters<=8:raise ValueError("parameter limit")
    if set(observed)!=set(law) or set(observed)!=set(null):raise ValueError("cell mismatch")
    ld=sum(deviance(y,law[c]) for c,y in observed.items())
    nd=sum(deviance(y,null[c]) for c,y in observed.items())
    return {"law_deviance":ld,"null_deviance":nd,"required_improvement":2*parameters+14,
            "beats_N0":nd-ld>=2*parameters+14}


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--predictions",required=True);ap.add_argument("--census",required=True)
    args=ap.parse_args();pred=json.load(open(args.predictions));pairs,h=read_pairs(args.census,pred["bounds"])
    if pred["cells"]!=["total"]:raise ValueError("initial scorer supports disjoint total cell only")
    actual={"total":len(pairs)};out=score(actual,pred["law"],pred["null"],pred["fitted_parameters"])
    # JSON never emits the nonstandard Infinity token.
    out={k:("infinity" if isinstance(v,float) and math.isinf(v) else v) for k,v in out.items()}
    out["census_sha256"]=h;out["status"]="diagnostic; chronological proof required separately"
    print(json.dumps(out,sort_keys=True,allow_nan=False))
