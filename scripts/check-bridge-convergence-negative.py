#!/usr/bin/env python3
"""Static source/event negative regressions; no runtime contract execution."""
import json,runpy,tempfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'context/reconciliation'
check=runpy.run_path(str(R/'scripts/check-bridge-convergence.py'))['inspect']; event=runpy.run_path(str(R/'scripts/check-authority-events.py'))['inspect']
results=[]
with tempfile.TemporaryDirectory(prefix='wa-bridge-negative-') as name:
 t=Path(name);shutil.copytree(R/'context',t/'context',ignore=shutil.ignore_patterns('*.docx','*.png','*.pdf'))
 p=t/'context/reconciliation/bridge-review-complete.json';original=p.read_text()
 tests=[('missing source coverage',lambda j:j['record_coverage'].pop()),('duplicate source coverage',lambda j:j['record_coverage'].append(j['record_coverage'][0])),('lost directional facet',lambda j:j['families'][0]['historical_directional_facets'].pop()),('wrong family mapping',lambda j:j['record_coverage'][0].update(family_id='BF-268')),('unsupported frozen claim',lambda j:j['families'][0].update(frozen=True,contract_status='FROZEN_FOR_IMPLEMENTATION')),('missing rail matrix',lambda j:j['rail_matrices'].pop('CL-08'))]
 for title,mut in tests:
  j=json.loads(original);mut(j);p.write_text(json.dumps(j));out=check(t);assert out['errors'],title;results.append({'case':title,'result':'REJECTED','errors':out['errors']});p.write_text(original)
 j=json.loads(original);e=next(z for z in j['evidence_index'] if 'candidate-application-resume-privacy-module-architecture' in z);q=t/e;s=q.read_text();q.write_text(s.replace('before promoting a late parse result','after promoting a late parse result')+'\nUnreviewed weakened obligation.\n');out=check(t);assert out['errors'];results.append({'case':'owner contract evidence drift','result':'REJECTED','errors':out['errors']});q.write_text(s)
 ep=json.loads((B/'authority-event-review.json').read_text())['modules']
 for m,ev in [('candidate_application_resume_privacy','media.availability_changed.v1'),('payment_payout_tax','order.outcome_changed.v1')]:
  q=t/ep[m]['architecture'];s=q.read_text();head='## WA-R068 / WA-R069 — Authority facts and committed event obligations';a,b=s.split(head,1);block,rest=b.split('\n## ',1);block='\n'.join(l for l in block.splitlines() if not l.startswith('- `'+ev+'`'));q.write_text(a+head+block+'\n## '+rest);out=event(t);assert out['errors'];results.append({'case':'missing '+m+' subscriber for '+ev,'result':'REJECTED','errors':out['errors']});q.write_text(s)
 assert not check(t)['errors'];assert not event(t)['errors']
report={'date':'2026-10-16','baseline':check(R),'negative_regressions':results,'scope':'Static evidence/coverage/registration mutation tests only; these do not execute producer/consumer runtime or prove semantic correctness.'}
print(json.dumps(report,indent=2))
