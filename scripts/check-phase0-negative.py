#!/usr/bin/env python3
"""Adversarial Phase0 evidence/source checks; not DB/provider runtime tests."""
import json
import runpy
import shutil
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHECK=runpy.run_path(str(ROOT/'scripts/check-phase0.py'))['inspect']
results=[]
with tempfile.TemporaryDirectory(prefix='wa-phase0-negative-') as directory:
    root=Path(directory)
    for name in ['context','app','legacy','scripts']:
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('*.docx','__pycache__'))
    for name in ['package.json','tsconfig.json','eslint.config.mjs','next.config.ts','postcss.config.mjs','package-lock.json','AGENTS.md','.node-version','prisma.offline.config.ts']:
        shutil.copy2(ROOT/name,root/name)
    assert not CHECK(root)['errors'],CHECK(root)['errors']
    def case(label,path,mutate,expected):
        p=root/path;original=p.read_bytes();value=json.loads(original);mutate(value);p.write_text(json.dumps(value))
        errors=CHECK(root)['errors'];p.write_bytes(original)
        assert any(expected in e for e in errors),(label,errors)
        results.append({'case':label,'result':'REJECTED','errors':errors})
    case('missing ninth context role','context/reconciliation/context-foundation-review.json',lambda j:j['roles'].pop(),'Nine context role mapping')
    case('invented database contact qualification','context/reconciliation/phase0-foundation-status.json',lambda j:j.update(database_contacted=True),'Unsupported Phase0')
    case('baseline adopted without provenance','context/reconciliation/database-provenance-requirements.json',lambda j:j.update(strategy_selected=True),'Unproven database provenance')
    case('fabricated target evidence','context/reconciliation/database-provenance-requirements.json',lambda j:j['requirements'][0].update(actual_evidence='assumed-empty',status='VERIFIED'),'Unproven database provenance')
    case('missing model owner coverage','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['models'].pop(),'source-model owner coverage')
    case('logical compatibility case lost','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['compatibility_cases'].pop(),'compatibility cases lost')
    case('browser access silently allowed','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['models'][0].update(browser_default='ALLOW_ALL'),'Unapproved database baseline')
    case('write alias bypasses posture D','package.json',lambda j:j['scripts'].update({'db:check':'node scripts/check-db-integrity.ts'}),'Database write alias bypass')
    case('failed build promoted to qualified','context/reconciliation/phase0-foundation-validation.json',lambda j:next(x for x in j['commands'] if x['id']=='build').update(exit_code=1),'Missing real Phase0 qualification')
    case('known security gate cleared','context/reconciliation/phase0-foundation-status.json',lambda j:j.update(dependency_security_gate='CLOSED'),'security gate silently cleared')
    for label,path,expected in [('archived source altered','legacy/checkpoint-005/application/pages/page.tsx','Legacy archive bytes changed'),('production gate source weakened','app/api/debug/env-check/route.ts','Qualified foundation source drift')]:
        p=root/path;original=p.read_bytes();p.write_bytes(original+b'\n// unreviewed mutation\n');errors=CHECK(root)['errors'];p.write_bytes(original)
        assert any(expected in e for e in errors),(label,errors)
        results.append({'case':label,'result':'REJECTED','errors':errors})
    (root/'pages').mkdir();errors=CHECK(root)['errors'];(root/'pages').rmdir();assert any('Pages router reactivated'in e for e in errors)
    results.append({'case':'old active router silently restored','result':'REJECTED','errors':errors})
report={'status':'PASS','total':len(results),'cases':results,'scope':'Source/evidence mutations only. Separately executed real HTTP tests prove the current diagnostic behavior; no actual DB/RLS/provider/owner-runtime test is implied.'}
print(json.dumps(report,indent=2))
