"""Frozen L001 diagnostic and disjoint-partition scores; no fitting."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from .score import deviance
from .checker import read_pairs
from .stats import stats


def observed(pairs,bounds):
    s=stats(pairs,bounds);joint=[[0]*120 for _ in range(bounds[2].bit_length())]
    for p,k in pairs:joint[k.bit_length()-1][k%120]+=1
    out={'total':len(pairs),'ge1':s['exponents_ge1'],'ge2':s['exponents_ge2'],'maximum':s['maximum_multiplicity']}
    for j in range(len(joint)):out[f'dyadic:{j}']=sum(joint[j])
    for m in (3,4,5,8,12):
        for r in range(m):out[f'mod{m}:{r}']=s['residues'][str(m)][r]
    return out,joint


def evaluate(prediction,pairs):
    obs,joint=observed(pairs,prediction['bounds']);law=prediction['law'];null=prediction['null']
    if set(law)!=set(obs) or set(null)!=set(obs):raise ValueError('summary cell mismatch')
    def get(keys):
        a=sum(deviance(obs[k],law[k]) for k in keys);b=sum(deviance(obs[k],null[k]) for k in keys)
        return {'law_deviance':a,'null_deviance':b,'improvement':b-a,'threshold':14,'passes_task_threshold':b-a>=14}
    full=get(obs);dyadic=get([k for k in obs if k.startswith('dyadic:')]);total=get(['total'])
    ja=sum(deviance(y,prediction['law_joint'][j][r]) for j,row in enumerate(joint) for r,y in enumerate(row))
    jb=sum(deviance(y,prediction['null_joint'][j][r]) for j,row in enumerate(joint) for r,y in enumerate(row))
    return {'observed':obs,'all_summary_diagnostic':full,'disjoint_dyadic':dyadic,'total_only':total,
            'disjoint_joint':{'law_deviance':ja,'null_deviance':jb,'improvement':jb-ja,'threshold':14,'passes_task_threshold':jb-ja>=14},
            'limitations':['All-summary cells overlap; no independent likelihood ratio.',
                           'Poisson laws for multiplicities and independence are hypotheses.',
                           'Vault-S score/hash remains provisional until operator confirms.']}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('prediction');ap.add_argument('census');a=ap.parse_args()
    pred=json.loads(Path(a.prediction).read_text());pairs,h=read_pairs(a.census,pred['bounds']);result=evaluate(pred,pairs)
    result['census_sha256']=h;result['prediction_sha256']=hashlib.sha256(Path(a.prediction).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2,sort_keys=True,allow_nan=False))
