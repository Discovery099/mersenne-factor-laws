"""Bounded, checkpointed open-cell computation; never opens a vault."""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
from .checker import read_pairs
from .stats import stats
from .null_n0 import predict

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');tmp.replace(path)


def open_bounds(bounds):
    lo,hi,K=bounds
    if not (3<=lo<=hi<1000000 and 1<=K<=100000):
        raise ValueError('this initial runner is restricted to open data below 10^6; no Vault-S execution')


def source_hashes():
    paths=['mf/checker.py','mf/checker2.c','mf/census_kp.c','mf/census_pk.c','mf/stats.py','mf/null_n0.py','mf/score.py']
    return {p:digest(ROOT/p) for p in paths}


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def preregister(name,bounds):
    open_bounds(bounds)
    if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):
        raise ValueError('unsafe cell name')
    path=ROOT/'predictions'/f'{name}.json'
    if path.exists() or (ROOT/'runs'/name).exists():raise ValueError('cell already registered or observed')
    baseline=predict(bounds)
    payload={'id':name,'bounds':list(bounds),'cells':['total'],'law_id':'N0',
             'fitted_parameters':0,'law':{'total':baseline['total']},'null':{'total':baseline['total']},
             'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'law_sha256':digest(ROOT/'laws/N0.py'),'null_sha256':digest(ROOT/'mf/null_n0.py'),
             'score_sha256':digest(ROOT/'mf/score.py'),
             'status':'baseline protocol rehearsal, not a distinct new law'}
    data=(json.dumps(payload,indent=2,sort_keys=True)+'\n').encode()
    with path.open('xb') as f:f.write(data)
    h=digest(path)
    with (ROOT/'ALERTS.md').open('a') as f:f.write(f'\nPreregistration {name}: SHA-256 {h}, bounds {bounds}; baseline rehearsal.\n')
    subprocess.run(['git','add',str(path.relative_to(ROOT)),'ALERTS.md'],cwd=ROOT,check=True)
    subprocess.run(['git','commit','-m',f'I001 preregister {name} N0 baseline'],cwd=ROOT,check=True,capture_output=True)
    return {'prediction':str(path.relative_to(ROOT)),'sha256':h,'git_commit':git('rev-parse','HEAD')}


def registered(path):
    rel=str(path.relative_to(ROOT))
    committed=subprocess.check_output(['git','show',f'HEAD:{rel}'],cwd=ROOT)
    if committed!=path.read_bytes():raise ValueError('prediction differs from committed bytes')
    value=json.loads(committed);open_bounds(value['bounds'])
    if value['law_id']!='N0' or value['law_sha256']!=digest(ROOT/'laws/N0.py'):
        raise ValueError('baseline law changed after preregistration')
    if value['null_sha256']!=digest(ROOT/'mf/null_n0.py') or value['score_sha256']!=digest(ROOT/'mf/score.py'):
        raise ValueError('null/scoring code changed after preregistration')
    return value,git('rev-parse','HEAD')


def compute(name,chunk_size=500,time_limit=600):
    if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):raise ValueError('unsafe id')
    if chunk_size<1 or chunk_size>1000 or not 1<=time_limit<=3600:raise ValueError('bounded resources required')
    predpath=ROOT/'predictions'/f'{name}.json';prediction,commit=registered(predpath)
    lo,hi,K=prediction['bounds'];work=ROOT/'runs'/name;work.mkdir(exist_ok=True)
    with (work/'LOCK').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        hashes=source_hashes();checkpoint=work/'checkpoint.json'
        state=json.loads(checkpoint.read_text()) if checkpoint.exists() else {
            'id':name,'bounds':[lo,hi,K],'source_hashes':hashes,'prediction_sha256':digest(predpath),
            'prediction_commit':commit,'next_p':lo,'chunks':[],'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'wall_s':0.0,'complete':False}
        if state['source_hashes']!=hashes or state['prediction_sha256']!=digest(predpath) or state['bounds']!=[lo,hi,K]:
            raise ValueError('checkpoint inputs changed')
        # Every persisted chunk is validated before reuse, not trusted from the queue.
        for row in state['chunks']:
            if digest(work/row['file'])!=row['sha256']:raise ValueError('checkpoint chunk corruption')
        started=time.monotonic();run_started=started;cpu_start=time.process_time()
        try:
            while state['next_p']<=hi:
                if time.monotonic()-run_started>=time_limit:
                    atomic_json(checkpoint,state);return {'status':'checkpointed','next_p':state['next_p']}
                a=state['next_p'];b=min(hi,a+chunk_size-1);bounds=[a,b,K]
                outputs=[];logs=[]
                for engine in ('census_kp','census_pk'):
                    remaining=time_limit-(time.monotonic()-run_started)
                    if remaining<=0:raise subprocess.TimeoutExpired(engine,time_limit)
                    result=subprocess.run([str(ROOT/'mf'/engine),*map(str,bounds)],check=True,capture_output=True,timeout=min(remaining,540))
                    outputs.append(result.stdout);logs.append(json.loads(result.stderr))
                if outputs[0]!=outputs[1]:raise ValueError(f'independent census mismatch at {a}:{b}')
                filename=f'{a}-{b}.txt';path=work/filename
                if path.exists() and path.read_bytes()!=outputs[0]:raise ValueError('conflicting immutable chunk')
                if not path.exists():path.write_bytes(outputs[0])
                pairs,h=read_pairs(str(path),bounds)
                state['chunks'].append({'bounds':bounds,'file':filename,'sha256':h,'count':len(pairs),'engines':logs})
                state['next_p']=b+1;state['wall_s']+=time.monotonic()-started;started=time.monotonic()
                atomic_json(checkpoint,state)
            allbytes=b''.join((work/x['file']).read_bytes() for x in state['chunks'])
            censuspath=work/'census.txt';censuspath.write_bytes(allbytes)
            pairs,h=read_pairs(str(censuspath),(lo,hi,K));summary=stats(pairs,(lo,hi,K));summary['sha256']=h
            atomic_json(work/'stats.json',summary)
            state['complete']=True;state['count']=len(pairs);state['sha256']=h;atomic_json(checkpoint,state)
            certificate=ROOT/'certificates'/f'{name}.json'
            manifest={**state,'kind':'census','census_path':str(censuspath.relative_to(ROOT)),
                      'stats_path':str((work/'stats.json').relative_to(ROOT)),
                      'stats_sha256':digest(work/'stats.json'),'cpu_accounting':'subprocess totals recorded by outer supervisor'}
            if certificate.exists():
                old=json.loads(certificate.read_text())
                if any(old[x]!=manifest[x] for x in ('sha256','count','bounds','source_hashes')):raise ValueError('immutable certificate conflict')
            else:
                with certificate.open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
            with (ROOT/'LEDGER.jsonl').open('a') as f:
                f.write(json.dumps({'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':name,'idea_id':'I001',
                                    'params':{'bounds':[lo,hi,K]},'verified':False,'certificate_path':str(certificate.relative_to(ROOT)),
                                    'conclusion':'dual engine complete; fresh verify required','tokens':None,
                                    'agent_cpu_s':time.process_time()-cpu_start,'wall_s':state['wall_s']})+'\n')
            return {'status':'complete','count':len(pairs),'sha256':h,'certificate_sha256':digest(certificate)}
        except subprocess.TimeoutExpired:
            atomic_json(checkpoint,state);return {'status':'checkpointed','next_p':state['next_p']}
        finally:lock.close()


if __name__=='__main__':
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('preregister');p.add_argument('id');p.add_argument('bounds',nargs=3,type=int)
    c=sub.add_parser('compute');c.add_argument('id');c.add_argument('--chunk-size',type=int,default=500);c.add_argument('--time-limit',type=int,default=600)
    a=ap.parse_args()
    try:
        out=preregister(a.id,a.bounds) if a.command=='preregister' else compute(a.id,a.chunk_size,a.time_limit)
        print(json.dumps(out));raise SystemExit(0 if out.get('status')!='checkpointed' else 75)
    except (ValueError,OSError,subprocess.CalledProcessError) as ex:
        print(json.dumps({'status':'failed','reason':str(ex)}));raise SystemExit(1)
