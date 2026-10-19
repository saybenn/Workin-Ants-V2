#!/usr/bin/env python3
"""Phase0 source/evidence preservation. Actual HTTP/framework checks run separately."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = ['project-overview.md','architecture.md','build-plan.md','code-standards.md','library-docs.md','ui-tokens.md','ui-rules.md','ui-registry.md','progress-tracker.md']


def inspect(root=ROOT):
    base=root/'context/reconciliation'
    if not (base/'phase0-foundation-status.json').exists():
        return {'errors':[],'status':'NOT_APPLICABLE_PRE_DIRECTIVE006'}
    read=lambda p:json.loads((root/p).read_text())
    errors=[]
    status=read('context/reconciliation/phase0-foundation-status.json')
    inventory=read('context/reconciliation/legacy-application-inventory.json')
    review=read('context/reconciliation/context-foundation-review.json')
    for f in inventory['files']:
        p=root/f['archive_path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:
            errors.append('Legacy archive bytes changed '+f['original_path'])
    if (root/'pages').exists() or (root/'src/pages').exists():errors.append('Legacy Pages router reactivated')
    if [x['path'] for x in review['roles']]!=['context/'+p for p in ROLES]:errors.append('Nine context role mapping incomplete')
    for p in ROLES:
        if not (root/'context'/p).is_file() or ('context/'+p) not in (root/'AGENTS.md').read_text():errors.append('Nine-role startup route missing '+p)
    for p in (root/'app').rglob('*'):
        if p.suffix in ['.ts','.tsx'] and '@/legacy' in p.read_text():errors.append('Active app imports inactive legacy source')
    if 'legacy' not in read('tsconfig.json')['exclude'] or 'legacy/**' not in (root/'eslint.config.mjs').read_text():errors.append('Legacy source entered active compiler/lint scope')
    if (status['database_posture']!='D' or status['database_contacted'] or status['migrations_seed_reset_or_provisioning_executed'] or status['runtime_shared_contracts_qualified'] or status['externally_gated_contracts']!=13 or status['authorized_parallel_lanes'] or status['production_development_authorized']):errors.append('Unsupported Phase0 database/runtime/production promotion')
    provenance=read('context/reconciliation/database-provenance-requirements.json')
    if provenance['strategy_selected'] or provenance['database_posture']!='D' or any(x['actual_evidence'] is not None or x['status']!='NOT_OBTAINED' for x in provenance['requirements']):errors.append('Unproven database provenance or baseline adoption')
    models=read('context/reconciliation/greenfield-model-security-inventory.json')['models']
    registry=read('context/reconciliation/platform-schema-compatibility-review.json')['model_owner_coverage']
    expected={x['model']:x['owners'][0] for x in registry}
    if len(models)!=177 or len({x['model'] for x in models})!=177 or {x['model']:x['source_owner'] for x in models}!=expected:errors.append('Greenfield source-model owner coverage changed')
    if any(x['baseline_disposition']!='RECONCILE_THEN_REVIEW_NOT_ADOPTED' or x['browser_default']!='DENY_NO_GRANT_NO_ALLOW_POLICY' for x in models):errors.append('Unapproved database baseline or browser access')
    if read('context/reconciliation/greenfield-model-security-inventory.json')['compatibility_cases']!=read('context/reconciliation/platform-schema-compatibility-review.json')['compatibility_mirrors']:errors.append('Physical/logical compatibility cases lost')
    for action in ['migrate','seed','check']:
        if read('package.json')['scripts']['db:'+action]!='node scripts/database-write-gate.mjs '+action:errors.append('Database write alias bypass '+action)
    if 'datasource' in (root/'prisma.offline.config.ts').read_text() or 'dotenv' in (root/'prisma.offline.config.ts').read_text():errors.append('Offline schema validation unexpectedly configures a datasource')
    evidence_path=base/'phase0-foundation-validation.json'
    evidence=read('context/reconciliation/phase0-foundation-validation.json') if evidence_path.exists() else {}
    if status['P0_B'].startswith('FRAMEWORK_ACCEPTANCE_PASS'):
        commands={c['id']:c for c in evidence.get('commands',[])}
        for id in ['clean_install','lint','typecheck','build','http_smoke','schema_validate']:
            if commands.get(id,{}).get('exit_code')!=0:errors.append('Missing real Phase0 qualification evidence '+id)
        if evidence.get('http_smoke',{}).get('status')!='PASS' or evidence.get('http_smoke',{}).get('total',0)<41:errors.append('Incomplete real dev/production HTTP evidence')
        if not evidence.get('foundation_source_sha256'):errors.append('Missing qualified foundation source fingerprints')
        for p,expected_sha in evidence.get('foundation_source_sha256',{}).items():
            if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=expected_sha:errors.append('Qualified foundation source drift '+p)
        security=read('context/reconciliation/dependency-security-review.json')
        if security['status']!='OPEN_CONTROLLED_REMEDIATION_REQUIRED' or status.get('dependency_security_gate')!='OPEN':errors.append('Known dependency security gate silently cleared')
    return {'errors':errors,'nine_roles':len(review['roles']),'archived_files':len(inventory['files']),'source_models':len(models),'database_posture':'D','status':status['P0_B'],'scope':'Static source/evidence/context/denial gate checks. Real installed framework/HTTP execution is separately recorded; no actual DB/RLS/provider/SH qualification.'}


if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
