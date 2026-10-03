import argparse
import json
from pathlib import Path
import subprocess
import sys
from mf.checker import verify_census, verify_factor, parse_census, census_hash
from mf.protocol import ROOT, digest
from mf.stats import summary
from .common import second_checker, execute_engine, executable


def verify_all():
    results=[]
    for path in sorted((ROOT/"certificates").glob("*")):
        if not path.is_file():
            continue
        if path.suffix != ".json":
            raise ValueError(f"unknown certificate format: {path}")
        obj=json.loads(path.read_text())
        if obj.get("kind")=="census":
            pairs=[tuple(x) for x in obj["pairs"]]
            result=verify_census(pairs,obj["bounds"])
            if result["sha256"] != obj["sha256"] or summary(pairs,*obj["bounds"])!=obj["statistics"]:
                raise ValueError("certificate hash/statistics mismatch")
            second_checker(pairs)
            for engine in ("census_kp","census_pk"):
                raw,_=execute_engine(engine,obj["bounds"])
                if census_hash(parse_census(raw)) != obj["sha256"]:
                    raise ValueError(f"incomplete census: {path}")
            results.append({"path":str(path.relative_to(ROOT)),"kind":"census","factors":len(pairs),"both_checkers":True,
                            "both_exhaustive_engines":True,"artifact_sha256":digest(path),"census_sha256":obj["sha256"]})
        elif obj.get("kind")=="factor":
            p,q,cert=obj["p"],obj["q"],obj.get("certificate")
            if not verify_factor(p,q,cert)["valid"]:
                raise ValueError("invalid factor certificate")
            args=[str(executable("checker2")),str(p),str(q)]
            if cert is not None:
                args += [":".join(map(str,row)) for row in cert]
            subprocess.run(args,check=True,capture_output=True)
            results.append({"path":str(path.relative_to(ROOT)),"kind":"factor","both_checkers":True,"artifact_sha256":digest(path)})
        else:
            raise ValueError(f"unknown certificate type: {path}")
    return {"verified":True,"certificates":results,"count":len(results)}


if __name__=="__main__":
    argparse.ArgumentParser(description="Recheck every immutable certificate, including census completeness").parse_args()
    try:
        print(json.dumps(verify_all(),sort_keys=True))
    except Exception as exc:
        print(json.dumps({"verified":False,"error":str(exc)}))
        sys.exit(1)
