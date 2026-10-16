#!/usr/bin/env python3
"""Root synthesis provenance and gate boundaries; not deployment/readiness certification."""
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def inspect(root=ROOT):
    base=root/'context/reconciliation'
    load=lambda n:json.loads((base/n).read_text())
    t=load('root-architecture-traceability.json'); p=load('platform-convergence-review.json'); d=load('database-posture-confirmation-2026-10-16.json')
    errors=[]
    text=(root/t['root']).read_text();rulings=(base/'platform-architecture-rulings.md').read_text()
    if hashlib.sha256((root/t['root']).read_bytes()).hexdigest()!=t['root_sha256']:errors.append('Root synthesis changed without traceability review')
    if p['status']!='GATE_5_PASSED_ARCHITECTURAL_CONVERGENCE' or not p['root_synthesis_authorized']:errors.append('Root synthesis lacks Gate 5 entry evidence')
    if d['posture']!='D' or d['status']!='COMPLETE_POSTURE_CONFIRMATION_D_EXTERNALLY_GATED':errors.append('Database posture falsely promoted')
    if any(d[k] for k in ['environment_evidence_obtained','live_database_contacted','migration_seed_reset_executed','disposable_replay_performed']):errors.append('Unexpected database execution/evidence claim')
    for section in t['sections']:
        if '## '+section['section'] not in text:errors.append('Missing root concern '+section['section'])
        for ruling in section['rulings']:
            if not re.search(r'^## '+ruling+r'\b',rulings,re.M):errors.append('Unknown root ruling '+ruling)
        for path,expected in section['sources'].items():
            if not (root/path).is_file() or hashlib.sha256((root/path).read_bytes()).hexdigest()!=expected:errors.append('Root basis drift '+path)
    for k in ['new_module_or_cluster','root_build_plan_created','parallel_implementation_authorized','executable_contract_freeze','database_or_provider_qualification']:
        if t[k]:errors.append('Unsupported root promotion '+k)
    for path in ['context/build-plan.md','build-plan.md']:
        if (root/path).exists():errors.append('Unexpected root build plan '+path)
    return {'errors':errors,'root':t['root'],'sections':len(t['sections']),'status':t['status'],'scope':'Synthesis traceability and gate boundaries only; implementation and external qualification remain open.'}
if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
