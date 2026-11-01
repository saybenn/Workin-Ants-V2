#!/usr/bin/env python3
"""Adversarial source mutations; none is a database/runtime test."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
module = runpy.run_path(str(ROOT / 'scripts/check-database-candidate.py'))
packet = module['load']()
inspect = module['inspect']
assert not inspect(packet)['errors'], inspect(packet)['errors']
REC = 'context/reconciliation/'
results = []


def case(label, name, change, expected, text=False):
    altered = dict(packet)
    path = name if '/' in name or name.endswith('.ts') else REC + name + '.json'
    value = altered[path] if text else json.loads(altered[path])
    replacement = change(value)
    altered[path] = replacement if text else json.dumps(value)
    # Fingerprints deliberately disabled. Require the specific semantic rule.
    errors = inspect(altered, check_hashes=False)['errors']
    assert any(expected in error for error in errors), (label, errors)
    results.append({'case': label, 'result': 'REJECTED', 'rule': expected})


def review(j):
    return j['physical_candidate_review']


case('Original model omitted', 'greenfield-model-security-inventory', lambda j: review(j)['rows'].pop(0), 'Candidate model ledger coverage')
case('Foreign source owner substituted', 'greenfield-model-security-inventory', lambda j: review(j)['rows'][0].update(source_owner='payment_payout_tax'), 'Source owner mismatch')
case('Source field disposition omitted', 'greenfield-model-security-inventory', lambda j: review(j)['rows'][0]['field_dispositions'].pop(), 'Source field disposition missing')
case('Compatibility case omitted', 'greenfield-model-security-inventory', lambda j: review(j)['compatibility_cases'].pop(), 'Twelve compatibility')
case('Queue concept made physical', 'greenfield-model-security-inventory', lambda j: review(j)['architecture_only_cases'][0].update(physical_disposition='NEW_TABLE'), 'Architecture-only queue')
case('Review falsely adopted', 'greenfield-model-security-inventory', lambda j: review(j).update(adopted=True), 'falsely promoted')
case('Generated SQL falsely claimed', 'database-candidate-manifest', lambda j: j.update(ddl_generated=True), 'manifest falsely promoted')
case('Brain approval invented', 'database-candidate-manifest', lambda j: j.update(brain_approved=True), 'manifest falsely promoted')
case('Runtime proof invented', 'database-candidate-manifest', lambda j: j.update(runtime_implemented=True), 'manifest falsely promoted')
schema = 'prisma/review/physical-candidate.prisma'
case('Cascade erases retained proof', schema, lambda s: s.replace('onDelete: Restrict', 'onDelete: Cascade', 1), 'Retained-history FK weakened', True)
case('Screening source removed', schema, lambda s: s.replace('  platform_screening\n', ''), 'Screening source requires fake seller', True)
case('Screening seller forced', schema, lambda s: __import__('re').sub(r'(sellerProfessionalProfileId\s+String)\?', r'\1', s, count=1), 'Screening source requires fake seller', True)
case('Consent presentation proof removed', schema, lambda s: s.replace('presentationId String ', 'presentationId String? ', 1), 'Consent exact content/presentation', True)
case('Semantic ledger uniqueness removed', schema, lambda s: s.replace('semanticEffectKey String @unique', 'semanticEffectKey String', 1), 'Durable semantic effect/receipt missing', True)
case('Direct browser grant added', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r['kind']=='table')['browser_api_roles'].update(authenticated=['SELECT']), 'Internal API grant')
case('RLS force removed', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r['kind']=='table').update(rls='ENABLE_ONLY'), 'Table ownership/RLS')
case('Runtime gains bypass', 'database-candidate-access-matrix', lambda j: next(r for r in j['roles'] if r['role']=='wa_app_runtime').update(bypassrls=True), 'Runtime/helper bypass')
case('Helper owner becomes login', 'database-candidate-access-matrix', lambda j: next(r for r in j['roles'] if r['role']=='wa_private_helper_owner').update(login=True), 'Nonlogin owner')
case('Two independent application histories', 'database-candidate-access-matrix', lambda j: j.update(migration_driver='PRISMA_PLUS_SUPABASE'), 'Competing migration driver')
case('Advisor cleared without execution', 'database-candidate-access-matrix', lambda j: j['advisor_dispositions'][0].update(status='REMEDIATED'), 'Advisor remediation falsely claimed')
case('Positive access test omitted', 'database-candidate-tests', lambda j: j['tests'].pop(0), 'Actual role positive/negative test missing')
case('Unexecuted test promoted', 'database-candidate-tests', lambda j: j['tests'][0].update(status='PASS'), 'Unexecuted tests promoted')
case('Context loses transaction binding', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1].update(exact_requirement='Trust actor userId GUC'), 'Trusted context binding weakened')
case('Atomic required intent omitted', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][7].update(exact_requirement='Source only; outbox later'), 'Atomic source/history/message obligation')
case('JSON wildcard permitted', 'database-candidate-json-boundaries', lambda j: j['boundaries'][0].update(admission='ANY_JSON',schemas=[]), 'Untyped JSON admission')
case('Empty committed evidence permitted', 'contracts/database-review/owner-mutation-evidence.v1.schema.json', lambda j: j['$defs']['CustomerProfile']['properties']['committed'].update(required=[]), 'Empty/incomplete evidence snapshot')
case('Source revision omitted from evidence', 'contracts/database-review/owner-mutation-evidence.v1.schema.json', lambda j: j['$defs']['CustomerProfile']['properties']['committed']['properties'].pop('revision'), 'Evidence omits source revision')
case('Offline config loads target environment', 'prisma.review.config.ts', lambda s: s + '\nconst url = process.env.DATABASE_URL;\n', 'Offline config can select database', True)
case('Grant nullable backend permits unbound issuance', schema, lambda s: s.replace('backendPid Int ', 'backendPid Int? ', 1), 'Grant immutable tuple must be nonnullable', True)
case('Grant nullable transaction permits retargeting', schema, lambda s: s.replace('transactionId String ', 'transactionId String? ', 1), 'Grant immutable tuple must be nonnullable', True)
case('Rollback-safe issuer commit omitted', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1]['binding_protocol'].update(issuer_commit='SOURCE_TRANSACTION_UPDATE'), 'Issuer commit/source-lock ordering')
case('Wrong snapshot isolation selected', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1]['binding_protocol'].update(isolation='REPEATABLE_READ'), 'Rollback-safe issuance/isolation')
case('Helper mutates rollbackable binding', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1]['binding_protocol'].update(helper_grant_writes=['UPDATE']), 'Immutable tuple/helper write boundary')
case('Savepoint rollback omitted', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1]['binding_protocol'].update(rollback_rule='COMMIT_ONLY'), 'Rollback/savepoint lifetime')
case('Capture allowed under business locks', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][1]['binding_protocol'].update(capture_before='AFTER_SOURCE_LOCK'), 'Issuer commit/source-lock ordering')
case('Consent user made optional', schema, lambda s: s.replace('userId String @map("user_id") @db.Uuid\n  actionOwner', 'userId String? @map("user_id") @db.Uuid\n  actionOwner', 1), 'Consent accepting user/action/context fields missing', True)
case('Consent composite unique removed', schema, lambda s: s.replace('@@unique([id, contentRevisionId, userId])', '', 1), 'Consent presentation composite key missing', True)
case('Consent composite FK weakened', schema, lambda s: s.replace('fields: [presentationId, contentRevisionId, userId], references: [id, contentRevisionId, userId]', 'fields: [presentationId], references: [id]', 1), 'Consent presentation composite FK missing', True)
case('Consent acknowledged hash omitted', schema, lambda s: s.replace('presentationHash String ', 'presentationHash String? ', 1), 'Consent acknowledged presentation hash missing', True)
case('Consent action omitted from equality', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][4]['consent_binding'].update(equal_fields=['contextKind']), 'Consent exact context/hash comparison')
case('Consent NULL becomes wildcard', 'database-candidate-sql-objects', lambda j: j['objects_and_invariants'][4]['consent_binding'].update(null_safe_fields=[]), 'Consent exact context/hash comparison')
case('Runtime receives grant SELECT', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r.get('model')=='DatabaseActionGrant')['operations_by_role']['wa_app_runtime'].append('SELECT'), 'Direct grant-table access permitted')
case('Worker receives grant INSERT', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r.get('model')=='DatabaseActionGrant')['operations_by_role']['wa_worker'].append('INSERT'), 'Direct grant-table access permitted')
case('Helper receives grant UPDATE', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r.get('model')=='DatabaseActionGrant')['operations_by_role']['wa_private_helper_owner'].append('UPDATE'), 'Helper grant writes or login')
case('Issuer receives broad UPDATE', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r.get('model')=='DatabaseActionGrant')['operations_by_role']['wa_context_issuer'].append('UPDATE'), 'Issuer grant operations ambiguous')
case('Worker direct grant denial removed', 'database-candidate-access-matrix', lambda j: next(r for r in j['objects'] if r.get('model')=='DatabaseActionGrant')['direct_denials_by_role']['wa_worker'].remove('SELECT'), 'Direct grant-table denial missing')
case('Table allow test has vague principal', 'database-candidate-tests', lambda j: next(t for t in j['tests'] if t['id']=='P0C-TABLE-DatabaseActionGrant-ALLOW')['setup'].pop('operations_by_role'), 'Exact access-test role operations missing')
case('Rollback test drops savepoint path', 'database-candidate-tests', lambda j: next(t for t in j['tests'] if t['id']=='P0C-CTX-01').update(action='Commit only'), 'Rollback/savepoint/pool negative test missing')
print(json.dumps({'status':'PASS','total':len(results),'cases':results,
                  'scope':'Semantic source mutations with fingerprint checks disabled; no actual DB/RLS/runtime execution'}, indent=2))
