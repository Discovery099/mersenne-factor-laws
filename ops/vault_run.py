"""Bounded, resumable supervisor for the already-committed multi-law census.

The frozen laws, engines, checker, statistics and scoring code are unchanged.
This adapter adds execution provenance and recovery for the new file schema.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from mf.checker import canonical_bytes, parse_census
from mf.preregister_vault import registered
from mf.protocol import ROOT, atomic_json, digest, git, utcnow, write_once
from mf.stats import summary, scoring_cells
from mf.vault_score import score
from ops.common import execute_engine, executable, exclusive_lock, ledger, second_checker

ENGINES=("census_kp","census_pk")
ADAPTERS=("ops/vault_run.py","ops/common.py","ops/build.py")


def adapter_sources():
    local={name:digest(ROOT/name) for name in ADAPTERS}
    request="".join(f"HEAD:{name}\n" for name in ADAPTERS).encode()
    result=subprocess.run(["git","-C",str(ROOT),"cat-file","--batch"],input=request,capture_output=True,check=True)
    stream=io.BytesIO(result.stdout)
    for name,sha in local.items():
        header=stream.readline().split()
        if len(header)!=3 or header[1]!=b"blob": raise ValueError("execution adapter must be committed before census")
        raw=stream.read(int(header[2])); stream.read(1)
        if hashlib.sha256(raw).hexdigest()!=sha: raise ValueError("execution adapter differs from committed bytes")
    return local


def plan(regions, chunk):
    if type(chunk) is not int or chunk < 1: raise ValueError("chunk must be positive")
    result=[]; cursor=regions[0][0]
    for lo,hi,K in regions:
        if lo!=cursor or hi<lo: raise ValueError("regions must be contiguous and disjoint")
        for a in range(lo,hi+1,chunk): result.append([a,min(hi,a+chunk-1),K])
        cursor=hi+1
    return result


def chunk_name(bounds): return "part_"+"_".join(map(str,bounds))


def engine_part(work, bounds, engine, binaries, deadline):
    base=work/(chunk_name(bounds)+"_"+engine)
    rawpath=base.with_suffix('.txt'); marker=base.with_suffix('.json')
    if marker.exists():
        rec=json.loads(marker.read_text())
        if rec['bounds']!=bounds or rec['engine']!=engine or rec['binary_sha256']!=binaries[engine] or rec['sha256']!=digest(rawpath):
            raise ValueError("saved engine part changed")
        parse_census(rawpath.read_bytes())
        return rec,rawpath
    for attempt in range(1,4):
        remaining=deadline-time.monotonic()
        if remaining<=0: raise subprocess.TimeoutExpired(engine,0)
        started=utcnow()
        try:
            raw,timing=execute_engine(engine,bounds,remaining)
            if digest(executable(engine))!=binaries[engine]: raise ValueError("engine binary changed during execution")
            pairs=parse_census(raw)
            rec={'bounds':bounds,'engine':engine,'binary_sha256':binaries[engine],
                 'started_at':started,'completed_at':utcnow(),'attempt':attempt,
                 'count':len(pairs),'sha256':hashlib.sha256(raw).hexdigest(),**timing}
            if rawpath.exists():
                if rawpath.read_bytes()!=raw: raise ValueError("previous incomplete artifact differs")
            else: write_once(rawpath,raw)
            atomic_json(marker,rec)
            return rec,rawpath
        except RuntimeError as exc:
            atomic_json(base.with_suffix(f'.failure{attempt}.json'),{'error':str(exc),'at':utcnow()})
            if attempt==3: raise


def verify_part(work, bounds, results):
    (ra,pa),(rb,pb)=results
    if ra['sha256']!=rb['sha256'] or pa.read_bytes()!=pb.read_bytes():
        raise ValueError("independent engine outputs disagree; both artifacts retained")
    raw=pa.read_bytes(); pairs=parse_census(raw)
    verified=work/(chunk_name(bounds)+'_verified.json')
    if verified.exists():
        old=json.loads(verified.read_text())
        if old['bounds']!=bounds or old['sha256']!=ra['sha256'] or old['count']!=len(pairs):
            raise ValueError("verification checkpoint changed")
        return old
    # Fresh Python process and independent C checker, never trust engine claims.
    check=subprocess.run([sys.executable,'-m','mf.checker','census',str(pa),'--bounds',*map(str,bounds)],
                         cwd=ROOT,capture_output=True,check=True,text=True)
    py=json.loads(check.stdout)
    if not py['valid'] or py['sha256']!=ra['sha256']: raise ValueError("fresh Python checker rejected census")
    count=second_checker(pairs)
    if count!=len(pairs): raise ValueError("independent C checker count mismatch")
    record={'bounds':bounds,'sha256':ra['sha256'],'count':len(pairs),'engines':[ra,rb],
            'python_checker':py,'C_checker_accepted':count,'verified_at':utcnow(),
            'path':pa.name,'second_path':pb.name}
    atomic_json(verified,record)
    return record


def assemble(work, parts, bounds, label, pred, manifest):
    lo,hi,K=bounds
    selected=[p for p in parts if lo<=p['bounds'][0] and p['bounds'][1]<=hi]
    cursor=lo
    for part in selected:
        if part['bounds'][0]!=cursor or part['bounds'][2]!=K: raise ValueError("incomplete region coverage")
        cursor=part['bounds'][1]+1
        for key in ('path','second_path'):
            if digest(work/part[key])!=part['sha256']: raise ValueError("part changed before assembly")
    if cursor!=hi+1: raise ValueError("incomplete final census")
    raw=b''.join((work/p['path']).read_bytes() for p in selected)
    other=b''.join((work/p['second_path']).read_bytes() for p in selected)
    if raw!=other: raise ValueError("final engine hashes disagree")
    pairs=parse_census(raw); out=work/label; out.mkdir(exist_ok=True)
    census=out/'census.txt'
    if census.exists():
        if census.read_bytes()!=raw: raise ValueError("existing final census differs")
    else: write_once(census,raw)
    stats=summary(pairs,*bounds)
    cells={**scoring_cells(stats),'maximum':stats['max_factors']}
    atomic_json(out/'statistics.json',stats)
    atomic_json(out/'summary_cells.json',{'bounds':bounds,'cells':cells,'census_sha256':stats['sha256']})
    scored=score(cells,pred)
    scored.update(bounds=bounds,census_sha256=stats['sha256'],prediction_sha256=manifest['prediction_sha256'],
                  input_origin='local dual-engine verified census; operator sealed confirmation pending')
    atomic_json(out/'score.json',scored)
    certificate=ROOT/'certificates'/f"census_{lo}_{hi}_{K}_{stats['sha256'][:12]}.json"
    cert={'schema':1,'kind':'census','bounds':bounds,'pairs':pairs,'sha256':stats['sha256'],
          'statistics':stats,'execution':{**manifest,'status':'complete','completed_at':utcnow(),
                                        'bounds':bounds,'parts':selected,'census_sha256':stats['sha256']}}
    if not certificate.exists(): write_once(certificate,(json.dumps(cert,sort_keys=True,separators=(',',':'))+'\n').encode())
    elif json.loads(certificate.read_text())['sha256']!=stats['sha256']: raise ValueError("certificate mismatch")
    return {'label':label,'bounds':bounds,'count':len(pairs),'sha256':stats['sha256'],
            'certificate':certificate.relative_to(ROOT).as_posix(),'score':str((out/'score.json').relative_to(ROOT))}


def run(prediction, work, hours, chunk, processes):
    if not math.isfinite(hours) or hours<=0 or processes not in (1,2): raise ValueError("positive hours and one or two processes required")
    work=Path(work).resolve(); work.relative_to(ROOT)
    work.mkdir(parents=True,exist_ok=True)
    registration=registered(prediction)
    pred=json.loads(Path(prediction).read_text())
    if pred['bounds']!=[10000001,30000000,10000]: raise ValueError("only the authorized full committed design may run")
    adapters=adapter_sources()
    manifest_path=work/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        if manifest['prediction_sha256']!=registration['prediction_sha256'] or manifest['adapter_sources']!=adapters or manifest['chunk']!=chunk:
            raise ValueError("resume parameters or adapter changed")
    else:
        from ops.build import build
        build()  # Build only from the frozen source bytes already checked above.
        started=utcnow()
        if datetime.fromisoformat(started)<=datetime.fromisoformat(registration['commit_time']): raise ValueError("census must start after preregistration")
        manifest={**registration,'started_at':started,'start_head':git('rev-parse','HEAD'),
                  'status':'running','bounds':pred['bounds'],'sources':pred['sources'],'adapter_sources':adapters,
                  'chunk':chunk,'maximum_native_processes':processes,'logical_cpus':os.cpu_count(),
                  'binaries':{name:digest(executable(name)) for name in (*ENGINES,'checker2')},
                  'authorization':'User explicitly selected Run the full committed design after SHA delivery in chat',
                  'region1_rerun':False}
        write_once(manifest_path,(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
    binaries={name:digest(executable(name)) for name in (*ENGINES,'checker2')}
    if binaries!=manifest['binaries']: raise ValueError("census/checker binaries changed")
    regions=[part['bounds'] for part in pred['regions']]
    chunks=plan(regions,chunk); completed=[]; start=time.monotonic(); deadline=start+hours*3600
    progress=work/'progress.json'
    try:
        with ThreadPoolExecutor(max_workers=processes) as pool:
            for bounds in chunks:
                if time.monotonic()>=deadline: raise subprocess.TimeoutExpired('budget',hours*3600)
                futures=[pool.submit(engine_part,work,bounds,engine,binaries,deadline) for engine in ENGINES]
                pending=set(futures)
                while pending:
                    done,pending=wait(pending,timeout=10,return_when=FIRST_COMPLETED)
                    for f in done: f.result()  # Fail promptly; engine deadlines also bound shutdown.
                    atomic_json(progress,{'status':'running','completed_chunks':len(completed),'total_chunks':len(chunks),
                        'current_bounds':bounds,'native_engines_pending':len(pending),'updated_at':utcnow(),'elapsed_s':time.monotonic()-start})
                record=verify_part(work,bounds,[f.result() for f in futures])
                completed.append(record)
                atomic_json(work/'checkpoint.json',{'parts':completed,'next':bounds[1]+1,'status':'running'})
                print(json.dumps({'verified_chunks':len(completed),'total_chunks':len(chunks),'completed_through_p':bounds[1],
                                  'elapsed_s':time.monotonic()-start}),flush=True)
        registration_now=registered(prediction)
        if registration_now!=registration or adapter_sources()!=adapters: raise ValueError("registration/adapter changed during census")
        outputs=[]
        for i,(bounds,label) in enumerate(zip(regions,('sealed_region_2','extension'))):
            part_pred=pred['sealed_region_2'] if i==0 else json.loads((ROOT/pred['regions'][i]['file']).read_text())
            outputs.append(assemble(work,completed,bounds,label,part_pred,manifest))
        outputs.append(assemble(work,completed,pred['bounds'],'enlarged_design',pred,manifest))
        manifest.update(status='complete',completed_at=utcnow(),parts=completed,outputs=outputs,
                        engine_cpu_s=sum(t.get('cpu_s') or 0 for p in completed for t in p['engines']))
        atomic_json(manifest_path,manifest)
        atomic_json(progress,{'status':'complete','completed_chunks':len(chunks),'total_chunks':len(chunks),'outputs':outputs,'updated_at':utcnow()})
        ledger('Vault-S region 2 + extension',pred['bounds'],None,time.monotonic()-start,manifest['engine_cpu_s'],True,
               'local census and frozen scoring complete; operator confirmation pending',outputs[-1]['certificate'],
               code_sha=manifest['start_head'],prediction_sha256=manifest['prediction_sha256'])
        return {'status':'complete','outputs':outputs,'engine_cpu_s':manifest['engine_cpu_s']}
    except BaseException as exc:
        state='paused-budget' if isinstance(exc,subprocess.TimeoutExpired) else 'failed'
        atomic_json(progress,{'status':state,'error':str(exc),'completed_chunks':len(completed),'total_chunks':len(chunks),'updated_at':utcnow()})
        raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prediction',default='predictions/Vault_S2_L001_L002_L003.json')
    ap.add_argument('--work',default='runs/Vault_S2_full')
    ap.add_argument('--hours',type=float,required=True)
    ap.add_argument('--chunk',type=int,default=500000)
    ap.add_argument('--processes',type=int,choices=(1,2),default=2)
    a=ap.parse_args()
    with exclusive_lock(Path(a.work)/'supervisor.lock'):
        print(json.dumps(run(a.prediction,a.work,a.hours,a.chunk,a.processes)),flush=True)
