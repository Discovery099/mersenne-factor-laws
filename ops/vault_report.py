"""Audit completed census artifacts and report the unchanged registered scores."""
from datetime import datetime
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from mf.preregister_vault import registered
from mf.protocol import ROOT, digest, atomic_json, utcnow
from mf.vault_score import score


def recount_cells(pairs, K):
    cells={'total':len(pairs)}
    cells.update({f'dyadic:{j}':0 for j in range(K.bit_length())})
    cells.update({f'residue:{m}:{r}':0 for m in (3,4,5,8,12) for r in range(m)})
    multiplicities=Counter()
    for p,k in pairs:
        if not 1<=k<=K: raise ValueError('k outside declared bounds')
        multiplicities[p]+=1
        cells[f'dyadic:{k.bit_length()-1}']+=1
        for m in (3,4,5,8,12): cells[f'residue:{m}:{k%m}']+=1
    cells.update(at_least_one=len(multiplicities),at_least_two=sum(v>=2 for v in multiplicities.values()),
                 maximum=max(multiplicities.values(),default=0))
    return cells


def report(work=ROOT/'runs/Vault_S2_full'):
    prediction=ROOT/'predictions/Vault_S2_L001_L002_L003.json'
    registration=registered(prediction)
    pred=json.loads(prediction.read_text())
    manifest=json.loads((work/'manifest.json').read_text())
    if manifest['status']!='complete': raise ValueError('full committed design is not complete')
    for key in ('prediction_sha256','prediction_commit'):
        if manifest[key]!=registration[key]: raise ValueError('run registration mismatch')
    if manifest['sources']!=pred['sources'] or manifest['bounds']!=pred['bounds']:
        raise ValueError('run source or bounds mismatch')
    subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',registration['prediction_commit'],manifest['start_head']],check=True)
    for name,sha in manifest['adapter_sources'].items():
        if digest(ROOT/name)!=sha: raise ValueError('execution adapter changed')
    started=datetime.fromisoformat(manifest['started_at']).timestamp()
    if datetime.fromisoformat(registration['commit_time']).timestamp()>=started:
        raise ValueError('run did not follow the prediction commit')
    cursor=manifest['bounds'][0]
    for part in manifest['parts']:
        lo,hi,K=part['bounds']
        if lo!=cursor or K!=manifest['bounds'][2]: raise ValueError('coverage gap/overlap')
        cursor=hi+1
        for field in ('path','second_path'):
            path=work/part[field]
            if path.name!=part[field] or digest(path)!=part['sha256'] or path.stat().st_mtime<started:
                raise ValueError('census part or chronology changed')
    if cursor!=manifest['bounds'][1]+1: raise ValueError('incomplete coverage')
    records={}
    for output in manifest['outputs']:
        label=output['label']; directory=work/label
        cells=json.loads((directory/'summary_cells.json').read_text())
        if cells['bounds']!=output['bounds'] or digest(directory/'census.txt')!=output['sha256']:
            raise ValueError('final census artifact changed')
        scope=(pred if label=='enlarged_design' else pred['sealed_region_2'] if label=='sealed_region_2'
               else json.loads((ROOT/pred['regions'][1]['file']).read_text()))
        rescored=score(cells['cells'],scope)
        stored=json.loads((directory/'score.json').read_text())
        if stored['scores']!=rescored['scores']: raise ValueError('stored score differs from frozen scorer')
        cert=json.loads((ROOT/output['certificate']).read_text())
        raw=''.join(f'{p} {k}\n' for p,k in cert['pairs']).encode()
        if hashlib.sha256(raw).hexdigest()!=output['sha256'] or cert['bounds']!=output['bounds']:
            raise ValueError('certificate/census mismatch')
        if recount_cells(cert['pairs'],output['bounds'][2])!=cells['cells']:
            raise ValueError('independent recount differs from saved summary cells')
        records[label]={'output':output,'observed':cells['cells'],'predictions':scope['models'],
                        'scores':rescored['scores'],'power':scope['power']}
    proof={'verified_at':utcnow(),'registration':registration,'start_head':manifest['start_head'],
           'status':'local dual-engine, dual-checker census; operator sealed confirmation pending',
           'records':records,'engine_cpu_seconds':manifest['engine_cpu_s'],
           'artifacts':{str(p.relative_to(ROOT)):digest(p) for p in work.rglob('*.json') if p.name not in ('progress.json',)}}
    target=ROOT/'results/Vault_S2_full';target.mkdir(parents=True,exist_ok=True)
    atomic_json(target/'audit.json',proof)
    lines=['# Vault-S region 2 and supplementary band — local results','',
           'The fixed prediction SHA-256 is `'+registration['prediction_sha256']+'`.',
           'Prediction commit: `'+registration['prediction_commit']+'`.',
           'Both independent engines agree on every chunk. Both factor checkers accepted every pair.',
           'Region 1 was not rerun. Operator comparison with the original sealed region 2 hash is pending.','']
    labels={'sealed_region_2':'Original sealed region 2','extension':'Supplementary band (descriptive)','enlarged_design':'Enlarged primary design'}
    for label in ('sealed_region_2','enlarged_design','extension'):
        rec=records[label];out=rec['output'];bounds=out['bounds']
        lines += ['## '+labels[label],'',f'Bounds: p in [{bounds[0]}, {bounds[1]}], k <= {bounds[2]}.',
                  f'Census SHA-256: `{out["sha256"]}`.','',
                  '| Cell | Observed | N0 | L001 | L002 | L003 |','| --- | ---: | ---: | ---: | ---: | ---: |']
        for cell in ('total','at_least_one','at_least_two','maximum'):
            lines.append('| '+cell+' | '+str(rec['observed'][cell])+' | '+' | '.join(f'{rec["predictions"][m][cell]:.6f}' for m in ('N0','L001','L002','L003'))+' |')
        ds=rec['scores']['descriptive_composite']['deviances']
        lines += ['','| Law | Full-summary deviance | Gain over N0 | Power eligible in this scope | Eligible win (gain >=14) |',
                  '| --- | ---: | ---: | --- | --- |']
        for law in ('L001','L002','L003'):
            row=rec['scores']['descriptive_composite']['comparisons']['N0_vs_'+law]
            lines.append(f'| {law} | {ds[law]:.6f} | {ds["N0"]-ds[law]:.6f} | {row["power_eligible"]} | {row["second_law_wins"]} |')
        lines += ['',f'L003 gain over L001: **{ds["L001"]-ds["L003"]:.6f}** (threshold 14).',
                  'Their factor-count expectations are identical; this contrast comes entirely from multiplicity.','']
    primary=records['enlarged_design']
    residual_one=primary['observed']['at_least_one']-primary['predictions']['L003']['at_least_one']
    residual_two=primary['observed']['at_least_two']-primary['predictions']['L003']['at_least_two']
    lines += ['## Interpretation and limits','',
              'Scores use the frozen complete summary, including maximum once. These overlapping',
              'cells form a composite diagnostic, not an independent likelihood ratio or a p-value.',
              'A lower L003 score supports its finite Bernoulli correction relative to L001 on',
              'these cells; it does not prove independence of actual Mersenne factors or establish novelty.',
              f'On the enlarged design, observed minus L003 predicted is {residual_one:+.6f} for >=1',
              f'and {residual_two:+.6f} for >=2. A relative win does not establish calibrated goodness',
              'of fit or justify treating every remaining residual as ordinary noise.',
              'The original region 2 N0/L002 comparison remains underpowered, regardless of its realized gain.',
              'No law may be refitted and retested on these now-observed bands.','',
              f'Native engine CPU time recorded: {manifest["engine_cpu_s"] / 3600:.6f} CPU-hours.',
              'Checker, Python aggregation, build, and audit CPU time are not included in that figure.','']
    (target/'RESULTS.md').write_bytes(('\n'.join(lines)).encode())
    print(json.dumps({'report':str(target/'RESULTS.md'),'audit':str(target/'audit.json'),
                     'counts':{k:v['output']['count'] for k,v in records.items()},
                     'hashes':{k:v['output']['sha256'] for k,v in records.items()},
                     'primary_scores':{k:v['scores']['descriptive_composite'] for k,v in records.items()}},indent=2))


if __name__=='__main__': report()
