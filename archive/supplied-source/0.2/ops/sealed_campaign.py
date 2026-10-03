#!/usr/bin/env python3
"""L001 prediction-gated, parallel, checkpointed two-engine runner."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mf.campaign import atomic_json
from mf.checker import read_pairs
from mf.stats import stats
from mf.score_v2 import evaluate


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(predpath):
    pred=json.loads(predpath.read_text());rel=str(predpath.relative_to(ROOT))
    committed=subprocess.check_output(['git','show',f'HEAD:{rel}'],cwd=ROOT)
    if committed!=predpath.read_bytes():raise ValueError('prediction is not committed verbatim')
    if pred['law_id']!='L001' or pred['fitted_parameters']!=0:raise ValueError('unsupported law')
    for p,h in pred['frozen_sources'].items():
        if sha(ROOT/p)!=h:raise ValueError(f'preregistered source changed: {p}')
    lo,hi,K=pred['bounds']
    if not (3<=lo<=hi<=10000000 and 1<=K<=100000):raise ValueError('unsupported range')
    # Require both predictions to exist in the same committed revision before ANY run.
    for p in ('predictions/L001_open.json','predictions/vaultS.json'):
        if subprocess.check_output(['git','show',f'HEAD:{p}'],cwd=ROOT)!=(ROOT/p).read_bytes():raise ValueError('both commitments required')
    first=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',rel],cwd=ROOT,text=True).splitlines()
    if not first:raise ValueError('no creation commit')
    return pred,first[-1]


def worker(job,work,threads,source_hashes):
    a,b,K=job;stem=f'{a}-{b}';done=work/f'{stem}.json'
    if done.exists():
        record=json.loads(done.read_text())
        if record['sources']!=source_hashes or record['bounds']!=list(job):raise ValueError('checkpoint inputs differ')
        if sha(work/f'{stem}.txt')!=record['sha256']:raise ValueError('checkpoint corruption')
        return record
    start=time.monotonic();data=[];logs=[]
    for engine in ('census_kp_v2','census_pk_v2'):
        result=subprocess.run([str(ROOT/'search'/engine),*map(str,job),str(threads)],capture_output=True,check=True,timeout=540)
        data.append(result.stdout);logs.append(json.loads(result.stderr))
    if data[0]!=data[1]:raise ValueError(f'independent census mismatch {job}')
    path=work/f'{stem}.txt'
    if path.exists() and path.read_bytes()!=data[0]:raise ValueError('immutable chunk conflict')
    if not path.exists():path.write_bytes(data[0])
    pairs,h=read_pairs(str(path),job)
    record={'bounds':list(job),'count':len(pairs),'sha256':h,'engines':logs,'sources':source_hashes,
            'wall_s':time.monotonic()-start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    atomic_json(done,record);return record


def run(predpath,threads=4,workers=2,chunk=50000):
    if not (1<=threads<=8 and 1<=workers<=2 and threads*workers<=8 and 1000<=chunk<=100000):raise ValueError('resource bounds')
    pred,commit=validate(predpath);name=pred['id'];lo,hi,K=pred['bounds']
    work=ROOT/'runs'/name;work.mkdir(exist_ok=True)
    with (work/'LOCK').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        checkpoint=work/'checkpoint.json'
        state={'id':name,'bounds':pred['bounds'],'prediction_sha256':sha(predpath),'prediction_commit':commit,
               'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':False,
               'sources':pred['frozen_sources'],'chunks':[],'resource_cap':{'threads':threads,'workers':workers,'timeout_per_engine_s':540}}
        if checkpoint.exists():
            old=json.loads(checkpoint.read_text())
            if any(old[k]!=state[k] for k in ('bounds','prediction_sha256','prediction_commit','sources')):raise ValueError('campaign inputs changed')
            state=old
        jobs=[(a,min(hi,a+chunk-1),K) for a in range(lo,hi+1,chunk)]
        cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);wall0=time.monotonic()
        atomic_json(checkpoint,state)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(worker,job,work,threads,state['sources']):job for job in jobs}
            records=[]
            for future in as_completed(futures):
                records.append(future.result());state['chunks']=sorted(records,key=lambda x:x['bounds'])
                state['progress']={'completed_chunks':len(records),'total_chunks':len(jobs),'factors_in_completed_chunks':sum(r['count'] for r in records)}
                atomic_json(checkpoint,state)
                (ROOT/'HEARTBEAT').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
        records.sort(key=lambda r:r['bounds']);data=b''.join((work/f"{r['bounds'][0]}-{r['bounds'][1]}.txt").read_bytes() for r in records)
        path=work/'census.txt'
        if path.exists() and path.read_bytes()!=data:raise ValueError('census conflict')
        path.write_bytes(data);pairs,h=read_pairs(str(path),pred['bounds'])
        # Independent frozen checkers, each reading serialized values in fresh processes.
        subprocess.run([sys.executable,'-m','mf.checker','census',str(path),'--bounds',*map(str,pred['bounds'])],cwd=ROOT,capture_output=True,check=True)
        payload=''.join(f'{p} {2*p*k+1}\n' for p,k in pairs)
        check=subprocess.run([str(ROOT/'mf/checker2'),'--batch'],input=payload,capture_output=True,text=True,check=True)
        accepted=[json.loads(l)['valid'] for l in check.stdout.splitlines()]
        if len(accepted)!=len(pairs) or not all(accepted):raise ValueError('second checker failed')
        summary=stats(pairs,pred['bounds']);summary['sha256']=h;atomic_json(work/'stats.json',summary)
        scores=evaluate(pred,pairs);scores['census_sha256']=h;atomic_json(work/'score.json',scores)
        cpu1=resource.getrusage(resource.RUSAGE_CHILDREN)
        state.update({'complete':True,'count':len(pairs),'sha256':h,'wall_s':time.monotonic()-wall0,
                      'cpu_s':cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,
                      'census_path':str(path.relative_to(ROOT)),'stats_path':str((work/'stats.json').relative_to(ROOT)),
                      'stats_sha256':sha(work/'stats.json'),'score_path':str((work/'score.json').relative_to(ROOT)),
                      'score_sha256':sha(work/'score.json'),'claim_level':'C2 finite census; law heuristic',
                      'operator_vault_confirmation':'pending' if name=='L001_vault1' else 'not applicable'})
        atomic_json(checkpoint,state)
        dest=ROOT/'certificates/v2';dest.mkdir(exist_ok=True);certificate=dest/f'{name}.json'
        if certificate.exists():
            if json.loads(certificate.read_text())['sha256']!=h:raise ValueError('certificate conflict')
        else:
            with certificate.open('x') as f:json.dump(state,f,indent=2,sort_keys=True);f.write('\n')
        with (ROOT/'LEDGER.jsonl').open('a') as f:f.write(json.dumps({'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'idea_id':'I004','target':name,'code_sha':state['sources'],'params':{'bounds':pred['bounds']},'verified':True,
            'cpu_s':state['cpu_s'],'wall_s':state['wall_s'],'certificate_path':str(certificate.relative_to(ROOT)),
            'conclusion':'finite census verified; local law score provisional for vault','tokens':None})+'\n')
        return {'id':name,'count':len(pairs),'sha256':h,'score':scores['all_summary_diagnostic'],
                'cpu_s':state['cpu_s'],'wall_s':state['wall_s'],'certificate_sha256':sha(certificate)}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('prediction');ap.add_argument('--threads',type=int,default=4);ap.add_argument('--workers',type=int,default=2)
    a=ap.parse_args()
    try:print(json.dumps(run((ROOT/a.prediction).resolve(),a.threads,a.workers),sort_keys=True))
    except Exception as ex:print(json.dumps({'status':'failed','reason':str(ex)}));raise SystemExit(1)
