#!/usr/bin/env python3
"""Detached bounded queue runner. Queue entries execute only mf.campaign open-cell jobs."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mf.campaign import atomic_json, open_bounds, registered


def valid_job(row):
    name=row['id']
    if not isinstance(name,str) or not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):raise ValueError('invalid job id')
    if not 1<=row.get('time_limit',600)<=3600:raise ValueError('bad resource limit')
    registered(ROOT/'predictions'/f'{name}.json')
    return row


def status():
    path=ROOT/'ops/processes.json';s=json.loads(path.read_text()) if path.exists() else {'jobs':{}}
    heartbeat=ROOT/'HEARTBEAT';s['heartbeat_age_s']=time.time()-heartbeat.stat().st_mtime if heartbeat.exists() else None
    disk=os.statvfs(ROOT);s['disk_used_fraction']=1-disk.f_bavail/disk.f_blocks
    s['alerts']=(ROOT/'ALERTS.md').read_text().splitlines()[-5:]
    print(json.dumps(s,indent=2))


def run(workers,max_seconds):
    if not 1<=workers<=2 or not 1<=max_seconds<=86400:raise ValueError('resource cap invalid')
    lock=(ROOT/'ops/SUPERVISOR_LOCK').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    statefile=ROOT/'ops/processes.json'
    state=json.loads(statefile.read_text()) if statefile.exists() else {'jobs':{}}
    # Kill only prior children belonging to this exact supervisor code, after an interrupted run.
    # Refuse to relaunch if a recorded PID still exists: operator must inspect it to avoid duplicate work.
    for row in state['jobs'].values():
        if row.get('status')=='running':
            try:os.kill(row['pid'],0)
            except ProcessLookupError:row['status']='interrupted'
            else:raise ValueError('previous worker still alive; inspect before restarting supervisor')
    active={};stop=[False]
    def halt(*_):stop[0]=True
    signal.signal(signal.SIGTERM,halt);signal.signal(signal.SIGINT,halt)
    began=time.monotonic();last_heartbeat=0;state['supervisor_pid']=os.getpid()
    try:
        while not stop[0] and time.monotonic()-began<max_seconds:
            if time.monotonic()-last_heartbeat>=300:
                (ROOT/'HEARTBEAT').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n');last_heartbeat=time.monotonic()
            # Read the full file before mutation, so a partial edit causes no launches.
            rows=[valid_job(json.loads(l)) for l in (ROOT/'ops/queue.jsonl').read_text().splitlines() if l.strip()]
            ids=[r['id'] for r in rows]
            if len(set(ids))!=len(ids):raise ValueError('duplicate queue id')
            for name,(proc,log,start) in list(active.items()):
                row=state['jobs'][name]
                if name not in ids or time.monotonic()-start>row['time_limit']+10:proc.terminate()
                code=proc.poll()
                if code is None:continue
                row['returncode']=code;row['status']='complete' if code==0 else 'checkpointed' if code==75 else 'failed'
                row['wall_s']=time.monotonic()-start;log.close();del active[name]
            for row in rows:
                name=row['id'];prior=state['jobs'].get(name,{})
                if name in active or prior.get('status')=='complete' or prior.get('attempts',0)>=4:continue
                if len(active)>=workers:break
                logpath=ROOT/'ops'/f'{name}.log';log=logpath.open('ab')
                command=[sys.executable,'-m','mf.campaign','compute',name,'--time-limit',str(row.get('time_limit',600))]
                proc=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
                active[name]=(proc,log,time.monotonic());state['jobs'][name]={'status':'running','pid':proc.pid,
                    'attempts':prior.get('attempts',0)+1,'time_limit':row.get('time_limit',600),'command':command,
                    'log_path':str(logpath.relative_to(ROOT)),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            usage=resource.getrusage(resource.RUSAGE_CHILDREN);state['cpu_s_completed_children']=usage.ru_utime+usage.ru_stime
            atomic_json(statefile,state)
            if not active and all(state['jobs'].get(n,{}).get('status')=='complete' or state['jobs'].get(n,{}).get('attempts',0)>=4 for n in ids):break
            time.sleep(1)
    finally:
        for name,(proc,log,start) in active.items():
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            log.close();state['jobs'][name]['status']='interrupted'
        state['supervisor_status']='stopped';atomic_json(statefile,state);lock.close()


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--status',action='store_true');ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--max-seconds',type=int,default=3600);a=ap.parse_args()
    if a.status:status()
    else:run(a.workers,a.max_seconds)
