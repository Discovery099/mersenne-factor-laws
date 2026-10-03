"""Verify sealed certificates, source provenance, chunk coverage and fresh checkers."""
import argparse, datetime, hashlib, json, subprocess, sys
from pathlib import Path
from .checker import read_pairs
from .stats import stats
from .score_v2 import evaluate
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(cert,rerun=False):
 if not __debug__:raise RuntimeError("verification requires assertions enabled")
 s=json.loads(cert.read_text());name=s['id'];predpath=ROOT/('predictions/vaultS.json' if name=='L001_vault1' else 'predictions/L001_open.json')
 pred=json.loads(predpath.read_text());assert sha(predpath)==s['prediction_sha256'],'prediction hash'
 assert subprocess.check_output(['git','show',s['prediction_commit']+':'+str(predpath.relative_to(ROOT))],cwd=ROOT)==predpath.read_bytes(),'commit'
 assert pred['frozen_sources']==s['sources'],'source manifest'
 provenance=json.loads((ROOT/'runs/L001_provenance.json').read_text())
 assert provenance['source_hashes']==s['sources'],'historical source manifest'
 sourcecommit=provenance['source_commit']
 when=subprocess.check_output(['git','show','-s','--format=%cI',sourcecommit],cwd=ROOT,text=True).strip()
 assert datetime.datetime.fromisoformat(when)<datetime.datetime.fromisoformat(s['started_utc']),'source commit after search'
 for p,h in s['sources'].items():
  assert sha(ROOT/p)==h,p
  historical=subprocess.check_output(['git','show',sourcecommit+':'+p],cwd=ROOT)
  assert hashlib.sha256(historical).hexdigest()==h,'uncommitted source'
 assert s['complete'],'incomplete certificate'
 lo,hi,K=s['bounds'];assert pred['bounds']==s['bounds'],'bounds'
 work=ROOT/'runs'/name;cursor=lo;parts=[]
 for c in s['chunks']:
  a,b,k=c['bounds'];assert a==cursor and a<=b<=hi and k==K,'chunk coverage'
  path=work/f'{a}-{b}.txt';pairs,h=read_pairs(str(path),(a,b,K));assert h==c['sha256'] and len(pairs)==c['count'],'chunk digest'
  assert c['sources']==s['sources'],'chunk sources'
  assert [e['engine'] for e in c['engines']]==['kp_v2','pk_v2'],'independent engines'
  assert all(e['complete'] and e['count']==len(pairs) for e in c['engines']),'engine completion'
  if rerun:
   for engine in ('census_kp_v2','census_pk_v2'):
    out=subprocess.check_output([str(ROOT/'search'/engine),str(a),str(b),str(K),'4'],stderr=subprocess.DEVNULL)
    assert out==path.read_bytes(),'independent exhaustive replay'
  parts.append(path.read_bytes());cursor=b+1
 assert cursor==hi+1,'coverage endpoint'
 path=ROOT/s['census_path'];assert path.read_bytes()==b''.join(parts),'merged data'
 pairs,h=read_pairs(str(path),s['bounds']);assert h==s['sha256'] and len(pairs)==s['count'],'census'
 subprocess.run([sys.executable,'-m','mf.checker','census',str(path),'--bounds',*map(str,s['bounds'])],cwd=ROOT,capture_output=True,check=True)
 payload=''.join(f'{p} {2*p*k+1}\n' for p,k in pairs)
 out=subprocess.run([str(ROOT/'mf/checker2'),'--batch'],input=payload,capture_output=True,text=True,check=True)
 answers=[json.loads(l)['valid'] for l in out.stdout.splitlines()];assert len(answers)==len(pairs) and all(answers),'checker 2'
 summary=stats(pairs,s['bounds']);summary['sha256']=h
 assert sha(ROOT/s['stats_path'])==s['stats_sha256'] and json.loads((ROOT/s['stats_path']).read_text())==json.loads(json.dumps(summary)),'statistics'
 scores=evaluate(pred,pairs);scores['census_sha256']=h
 assert sha(ROOT/s['score_path'])==s['score_sha256'] and json.loads((ROOT/s['score_path']).read_text())==scores,'scores'
 return name,len(pairs),h,scores['all_summary_diagnostic']['improvement']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rerun',action='store_true');a=ap.parse_args()
 print('sealed certificate | pairs | SHA-256 | local diagnostic improvement')
 for p in sorted((ROOT/'certificates/v2').glob('*.json')):print(' | '.join(map(str,verify(p,a.rerun))))
if __name__=='__main__':main()
