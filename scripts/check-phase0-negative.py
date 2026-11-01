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
    for name in ['context','app','legacy','scripts','prisma','contracts','tests/database']:
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('*.docx','__pycache__'))
    for name in ['package.json','tsconfig.json','eslint.config.mjs','next.config.ts','postcss.config.mjs','package-lock.json','AGENTS.md','.node-version','prisma.offline.config.ts','prisma.review.config.ts','prisma.foundation-review.config.ts','vercel.json']:
        shutil.copy2(ROOT/name,root/name)
    assert not CHECK(root)['errors'],CHECK(root)['errors']
    def case(label,path,mutate,expected):
        p=root/path;original=p.read_bytes();value=json.loads(original);mutate(value);p.write_text(json.dumps(value))
        errors=CHECK(root)['errors'];p.write_bytes(original)
        assert any(expected in e for e in errors),(label,errors)
        results.append({'case':label,'result':'REJECTED','errors':errors})
    evidence_path='context/reconciliation/'+json.loads((root/'context/reconciliation/phase0-foundation-status.json').read_text()).get('qualification_evidence','phase0-foundation-validation.json')
    case('missing ninth context role','context/reconciliation/context-foundation-review.json',lambda j:j['roles'].pop(),'Nine context role mapping')
    case('unrecorded database contact','context/reconciliation/phase0-foundation-status.json',lambda j:j.pop('database_observation',None),'Unsupported Phase0')
    case('baseline adopted without provenance','context/reconciliation/database-provenance-requirements.json',lambda j:j.update(strategy_selected=True),'Unproven database provenance')
    case('fabricated target evidence','context/reconciliation/database-provenance-requirements.json',lambda j:j['requirements'][0].update(actual_evidence='assumed-empty',status='VERIFIED'),'Unproven database provenance')
    if json.loads((root/'context/reconciliation/phase0-foundation-status.json').read_text()).get('database_observation'):
        observation='context/reconciliation/database-observations/2026-10-26/'
        case('observation promoted to adopted baseline',observation+'manifest.json',lambda j:j.update(baseline_adopted=True),'Unsupported Phase0')
        case('read-only observation reports writes',observation+'manifest.json',lambda j:j.update(database_writes_executed=True),'Unsupported Phase0')
        case('catalog collection was not read-only',observation+'catalog.json',lambda j:j.update(transaction_read_only='off'),'Database observation')
        case('observation pointed at another project',observation+'project.json',lambda j:j.update(id='wrong-project'),'Database observation')
        case('observation evidence changed',observation+'prisma-migration-ledger.json',lambda j:j[0].update(checksum='invented'),'Database observation')
        case('fresh target silently qualified','context/reconciliation/database-provenance-requirements.json',lambda j:j['reported_target'].update(fresh_target_qualified=True),'Database observation')
    if json.loads((root/'context/reconciliation/phase0-foundation-status.json').read_text()).get('fresh_database_observation'):
        fresh='context/reconciliation/database-observations/2026-10-27/'
        case('fresh target points back to old project',fresh+'project.json',lambda j:j.update(id='sdceenkakajslwpctbgl'),'Fresh database observation')
        case('fresh catalog was not read-only',fresh+'catalog.json',lambda j:j.update(transaction_read_only='off'),'Fresh database observation')
        case('fresh application namespace not empty',fresh+'access-review.json',lambda j:j.update(application_relations=[{'schema':'app','name':'users','kind':'r'}]),'Fresh database observation')
        case('fresh baseline adopted from identity alone',fresh+'manifest.json',lambda j:j.update(baseline_adopted=True),'Fresh database observation')
        case('replay gate falsely completed','context/reconciliation/database-provenance-requirements.json',lambda j:j['requirements'][9].update(status='VERIFIED',actual_evidence='not-run'),'Unproven database provenance')
    case('missing model owner coverage','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['models'].pop(),'source-model owner coverage')
    case('logical compatibility case lost','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['compatibility_cases'].pop(),'compatibility cases lost')
    case('browser access silently allowed','context/reconciliation/greenfield-model-security-inventory.json',lambda j:j['models'][0].update(browser_default='ALLOW_ALL'),'Unapproved database baseline')
    case('write alias bypasses posture D','package.json',lambda j:j['scripts'].update({'db:check':'node scripts/check-db-integrity.ts'}),'Database write alias bypass')
    if json.loads((root/'context/reconciliation/phase0-foundation-status.json').read_text()).get('candidate_review_manifest'):
        case('candidate review falsely adopted','context/reconciliation/database-candidate-manifest.json',lambda j:j.update(adopted=True),'Database candidate review')
        case('physical candidate prematurely verified','context/reconciliation/database-provenance-requirements.json',lambda j:j['requirements'][8].update(status='VERIFIED'),'Unproven database provenance')
    case('failed build promoted to qualified',evidence_path,lambda j:next(x for x in j['commands'] if x['id']=='build').update(exit_code=1),'Missing real Phase0 qualification')
    case('known security gate cleared','context/reconciliation/phase0-foundation-status.json',lambda j:j.update(dependency_security_gate='CLOSED'),'security gate silently cleared')
    if evidence_path.endswith('phase0-security-requalification.json'):
        case('failed security audit promoted to passed',evidence_path,lambda j:next(x for x in j['commands'] if x['id']=='audit_full').update(exit_code=1),'Missing dependency requalification')
        case('qualification used wrong npm',evidence_path,lambda j:j['toolchain'].update(npm='11.17.0'),'toolchain mismatch')
        case('failed runtime security check promoted',evidence_path,lambda j:next(x for x in j['commands'] if x['id']=='runtime_security').update(exit_code=1),'Missing dependency requalification')
        case('audit snapshot changed after qualification','context/reconciliation/dependency-audit-full-2026-10-26.json',lambda j:j['metadata']['vulnerabilities'].update(high=1,total=1),'Dependency audit')
        case('audit results omitted','context/reconciliation/dependency-audit-production-2026-10-26.json',lambda j:j.pop('vulnerabilities'),'Dependency audit')
        case('unreviewed package pin','package.json',lambda j:j['dependencies'].update(next='16.2.6'),'Reviewed dependency file drift')
        case('package manifest preimage invented','context/reconciliation/phase0-security-file-changes.json',lambda j:j.update(previous_package_text='{}'),'manifest preimage mismatch')
        case('unreviewed lock integrity','package-lock.json',lambda j:j['packages']['node_modules/next'].update(integrity='invented'),'Reviewed dependency file drift')
        case('qualified HTTP surface source changed',evidence_path,lambda j:j['foundation_source_sha256'].update({'scripts/smoke-foundation.mjs':'invented'}),'Qualified foundation source drift')
    for label,path,expected in [('archived source altered','legacy/checkpoint-005/application/pages/page.tsx','Legacy archive bytes changed'),('production gate source weakened','app/api/debug/env-check/route.ts','Qualified foundation source drift'),('runtime pin changed after testing','.node-version','Qualified foundation source drift')]:
        p=root/path;original=p.read_bytes();p.write_bytes(original+b'\n// unreviewed mutation\n');errors=CHECK(root)['errors'];p.write_bytes(original)
        assert any(expected in e for e in errors),(label,errors)
        results.append({'case':label,'result':'REJECTED','errors':errors})
    (root/'pages').mkdir();errors=CHECK(root)['errors'];(root/'pages').rmdir();assert any('Pages router reactivated'in e for e in errors)
    results.append({'case':'old active router silently restored','result':'REJECTED','errors':errors})
report={'status':'PASS','total':len(results),'cases':results,'scope':'Source/evidence mutations only. Separately executed real HTTP tests prove the current diagnostic behavior; no actual DB/RLS/provider/owner-runtime test is implied.'}
print(json.dumps(report,indent=2))
