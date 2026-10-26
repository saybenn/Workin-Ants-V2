#!/usr/bin/env python3
"""Phase0 source/evidence preservation. Actual HTTP/framework checks run separately."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = ['project-overview.md','architecture.md','build-plan.md','code-standards.md','library-docs.md','ui-tokens.md','ui-rules.md','ui-registry.md','progress-tracker.md']


def inspect_database_observation(root, status, provenance):
    """Validate retained read-only observations without qualifying a write target."""
    reference = status.get('database_observation')
    if reference is None:
        return ['Unsupported Phase0 database contact without observation'] if status['database_contacted'] or provenance['database_contacted'] else []
    expected = 'context/reconciliation/database-observations/2026-10-26/manifest.json'
    if reference != expected or provenance.get('existing_target_observation') != expected:
        return ['Database observation reference is unregistered']
    errors = []
    try:
        base = (root / expected).parent
        read = lambda name: json.loads((base / name).read_text())
        manifest = read('manifest.json')
        required = {'project.json', 'project-url.json', 'organization.json', 'catalog.json',
                    'access-review.json', 'prisma-migration-ledger.json',
                    'supabase-migration-ledger.json', 'security-advisors.json',
                    'table-summary.json', 'table-identity-comparison.json', 'catalog-probe.sql', 'access-review.sql',
                    'prisma-ledger-probe.sql'}
        if set(manifest['files_sha256']) != required:
            errors.append('Database observation evidence coverage changed')
        for name in required:
            if not (base / name).is_file() or hashlib.sha256((base / name).read_bytes()).hexdigest() != manifest['files_sha256'].get(name):
                errors.append('Database observation evidence fingerprint changed ' + name)
        mode = 'READ_ONLY_EXISTING_TARGET_NOT_ADOPTED'
        if (manifest['kind'] != mode or status.get('database_access_mode') != mode
                or not status['database_contacted'] or not provenance['database_contacted']
                or manifest['database_contacted'] is not True
                or any(manifest[key] is not False for key in ['database_writes_executed',
                       'application_rows_exported', 'application_row_emptiness_proven',
                       'fresh_target_qualified', 'baseline_adopted'])):
            errors.append('Unsupported Phase0 database observation scope')
        project, endpoint, catalog, access = [read(name) for name in ['project.json', 'project-url.json', 'catalog.json', 'access-review.json']]
        target = provenance['reported_target']
        if (manifest['project_ref'] != project['id'] or project['id'] != target['project_ref']
                or manifest['project_url'] != endpoint['url']
                or endpoint['url'] != 'https://' + project['id'] + '.supabase.co'
                or target['fresh_target_qualified'] is not False or target['adopted_for_writes'] is not False):
            errors.append('Database observation target mismatch or promotion')
        if catalog['transaction_read_only'] != 'on' or access['transaction_read_only'] != 'on':
            errors.append('Database observation is not recorded as read-only')
        if not any(row['schema'] == 'app' and row['kind'] in ['r', 'p'] for row in catalog['relations']):
            errors.append('Database observation existing-schema classification unsupported')
    except (OSError, KeyError, TypeError, ValueError) as exc:
        errors.append('Database observation evidence unavailable or malformed: ' + type(exc).__name__)
    return errors


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
    agents=(root/'AGENTS.md').read_text()
    truth_start=agents.find('<!-- BEGIN:workinants-database-truth-rules -->')
    truth_end=agents.find('<!-- END:workinants-database-truth-rules -->')
    if truth_start < agents.find('<!-- END:nextjs-agent-rules -->') or truth_end < truth_start or 'Supabase/Postgres is the source of truth.' not in agents[truth_start:truth_end]:errors.append('Project database rules missing or inside generated framework block')
    for p in (root/'app').rglob('*'):
        if p.suffix in ['.ts','.tsx'] and '@/legacy' in p.read_text():errors.append('Active app imports inactive legacy source')
    if 'legacy' not in read('tsconfig.json')['exclude'] or 'legacy/**' not in (root/'eslint.config.mjs').read_text():errors.append('Legacy source entered active compiler/lint scope')
    if (status['database_posture']!='D' or status['migrations_seed_reset_or_provisioning_executed'] or status['runtime_shared_contracts_qualified'] or status['externally_gated_contracts']!=13 or status['authorized_parallel_lanes'] or status['production_development_authorized']):errors.append('Unsupported Phase0 database/runtime/production promotion')
    provenance=read('context/reconciliation/database-provenance-requirements.json')
    if provenance['strategy_selected'] or provenance['database_posture']!='D' or any(provenance[key] for key in ['database_provisioned','migrations_executed','old_supabase_reused_reset_or_erased']) or any(x['actual_evidence'] is not None or x['status']!='NOT_OBTAINED' for x in provenance['requirements']):errors.append('Unproven database provenance or baseline adoption')
    errors.extend(inspect_database_observation(root, status, provenance))
    models=read('context/reconciliation/greenfield-model-security-inventory.json')['models']
    registry=read('context/reconciliation/platform-schema-compatibility-review.json')['model_owner_coverage']
    expected={x['model']:x['owners'][0] for x in registry}
    if len(models)!=177 or len({x['model'] for x in models})!=177 or {x['model']:x['source_owner'] for x in models}!=expected:errors.append('Greenfield source-model owner coverage changed')
    if any(x['baseline_disposition']!='RECONCILE_THEN_REVIEW_NOT_ADOPTED' or x['browser_default']!='DENY_NO_GRANT_NO_ALLOW_POLICY' for x in models):errors.append('Unapproved database baseline or browser access')
    if read('context/reconciliation/greenfield-model-security-inventory.json')['compatibility_cases']!=read('context/reconciliation/platform-schema-compatibility-review.json')['compatibility_mirrors']:errors.append('Physical/logical compatibility cases lost')
    for action in ['migrate','seed','check']:
        if read('package.json')['scripts']['db:'+action]!='node scripts/database-write-gate.mjs '+action:errors.append('Database write alias bypass '+action)
    if 'datasource' in (root/'prisma.offline.config.ts').read_text() or 'dotenv' in (root/'prisma.offline.config.ts').read_text():errors.append('Offline schema validation unexpectedly configures a datasource')
    evidence_name=status.get('qualification_evidence','phase0-foundation-validation.json')
    if evidence_name not in ['phase0-foundation-validation.json','phase0-security-requalification.json']:
        errors.append('Unregistered Phase0 qualification evidence');evidence_name='phase0-foundation-validation.json'
    evidence_path=base/evidence_name
    evidence=read('context/reconciliation/'+evidence_name) if evidence_path.exists() else {}
    if status['P0_B'].startswith('FRAMEWORK_ACCEPTANCE_PASS'):
        commands={c['id']:c for c in evidence.get('commands',[])}
        for id in ['clean_install','lint','typecheck','build','http_smoke','schema_validate']:
            if commands.get(id,{}).get('exit_code')!=0:errors.append('Missing real Phase0 qualification evidence '+id)
        if evidence.get('http_smoke',{}).get('status')!='PASS' or evidence.get('http_smoke',{}).get('total',0)<41:errors.append('Incomplete real dev/production HTTP evidence')
        if not evidence.get('foundation_source_sha256'):errors.append('Missing qualified foundation source fingerprints')
        for p,expected_sha in evidence.get('foundation_source_sha256',{}).items():
            if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=expected_sha:errors.append('Qualified foundation source drift '+p)
        security=read('context/reconciliation/dependency-security-review.json')
        if status.get('dependency_security_gate')=='PASS_KNOWN_ADVISORIES_REMEDIATED' and evidence_name=='phase0-security-requalification.json':
            errors.extend(runpy.run_path(str(root/'scripts/phase0_security_evidence.py'))['inspect_qualification'](root,evidence))
            previous=read('context/reconciliation/phase0-approved-file-changes.json')
            errors.extend(runpy.run_path(str(root/'scripts/phase0_security_evidence.py'))['inspect_change_review'](root,previous)['errors'])
        elif security['status']!='OPEN_CONTROLLED_REMEDIATION_REQUIRED' or status.get('dependency_security_gate')!='OPEN':errors.append('Known dependency security gate silently cleared')
    return {'errors':errors,'nine_roles':len(review['roles']),'archived_files':len(inventory['files']),'source_models':len(models),'database_posture':'D','status':status['P0_B'],'scope':'Static source/evidence/context/denial gate checks, including integrity of the separately recorded read-only existing-database observation. No fresh-target adoption, RLS behavior, owner-runtime or SH qualification.'}


if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
