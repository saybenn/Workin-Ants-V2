#!/usr/bin/env python3
"""Offline candidate/evidence checks. Never connects or generates SQL.

Semantic inspection is separable from fingerprint inspection so mutation tests
prove the intended rule, rather than merely noticing that a file changed.
"""
import hashlib
import json
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REC = 'context/reconciliation/'
PARSER = runpy.run_path(str(ROOT / 'scripts/prepare-database-candidate.py'))
parse, fields = PARSER['parse'], PARSER['fields']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(root=ROOT):
    paths = [
        'prisma/schema.prisma', 'prisma/review/physical-candidate.prisma',
        'prisma/review/foundation-candidate.prisma', 'prisma.review.config.ts',
        'prisma.foundation-review.config.ts',
        'contracts/database-review/owner-mutation-evidence.v1.schema.json',
        'contracts/database-review/foundation-payloads.v1.schema.json',
        'tests/database/candidate-fixtures.json',
    ]
    names = ['greenfield-model-security-inventory', 'database-candidate-additions',
             'database-candidate-access-matrix', 'database-candidate-sql-objects',
             'database-candidate-tests', 'database-candidate-source-review',
             'database-candidate-manifest', 'database-candidate-corrections-native-validation',
             'database-candidate-json-boundaries']
    paths += [REC + n + '.json' for n in names]
    return {p: (root / p).read_text() for p in paths}


def inspect(packet=None, root=ROOT, check_hashes=True):
    packet = load(root) if packet is None else packet
    read = lambda name: json.loads(packet[REC + name + '.json'])
    errors = []
    def need(condition, message):
        if not condition:
            errors.append(message)
    inventory = read('greenfield-model-security-inventory')
    review = inventory['physical_candidate_review']
    additions = read('database-candidate-additions')
    access = read('database-candidate-access-matrix')
    sql = read('database-candidate-sql-objects')['objects_and_invariants']
    tests = read('database-candidate-tests')
    manifest = read('database-candidate-manifest')
    native = read('database-candidate-corrections-native-validation')
    source = parse(packet['prisma/schema.prisma'])
    full = parse(packet[review['full_schema']])
    cut = parse(packet[review['foundation_schema']])
    original = {n: b for n, b in source.items() if b['kind'] == 'model'}
    models = {n: b for n, b in full.items() if b['kind'] == 'model'}
    foundation = {n: b for n, b in cut.items() if b['kind'] == 'model'}
    rows = {r['model']: r for r in review['rows']}
    baseline = {r['model']: r for r in inventory['models']}
    new = {r['model']: r for r in additions['models']}
    need(len(original) == len(baseline) == 177 and set(original) == set(baseline), 'Original 177-model coverage lost')
    need(set(models) == set(rows) == set(original) | set(new) and len(rows) == len(review['rows']), 'Candidate model ledger coverage lost')
    need(review['existing_models_reviewed'] == len(original) and review['candidate_model_count'] == len(models), 'Candidate count claim differs from source')
    need(set(foundation) <= set(models) and review['foundation_model_count'] == len(foundation), 'Foundation count/coverage mismatch')
    need(all(review.get(k) is False for k in ['adopted', 'ddl_generated', 'database_contacted_by_review']), 'Candidate review falsely promoted to execution/adoption')
    for key in ['brain_approved', 'adopted', 'ddl_generated', 'database_contacted_by_review', 'runtime_implemented']:
        need(manifest.get(key) is False, 'Candidate manifest falsely promoted: ' + key)
    need(manifest.get('status') == 'READY_FOR_BRAIN_REVIEW_NOT_APPROVED', 'Candidate review status changed')
    for n, block in models.items():
        row = rows.get(n, {})
        owner = baseline.get(n, {}).get('source_owner', new.get(n, {}).get('owner'))
        need(row.get('source_owner') == owner and bool(owner), 'Source owner mismatch: ' + n)
        for key in ['purpose', 'classification', 'stage', 'identifiers_and_indexes', 'deletion', 'history_and_proof', 'access', 'privacy_executor', 'authority', 'rulings', 'sql_companion']:
            need(bool(row.get(key)), 'Incomplete model disposition: ' + n + ':' + key)
        need(row.get('candidate_fields') == fields(block['body']), 'Field ledger drift: ' + n)
        if n in original:
            source_fields = fields(original[n]['body'])
            need(row.get('source_fields') == source_fields, 'Source field coverage changed: ' + n)
            dispositions = row.get('field_dispositions', [])
            need({f['field'] for f in dispositions} == {f['name'] for f in source_fields} and len(dispositions) == len(source_fields), 'Source field disposition missing: ' + n)
            need(all(f.get('basis') and f.get('disposition') for f in dispositions), 'Unjustified field change: ' + n)
        for f in fields(block['body']):
            if '@relation' in f['attributes'] and 'fields:' in f['attributes']:
                need('onDelete: Restrict' in f['attributes'] and 'onUpdate: Restrict' in f['attributes'], 'Retained-history FK weakened: ' + n + '.' + f['name'])
            if f['type'].startswith('DateTime'):
                need('@db.Timestamptz(6)' in f['attributes'], 'UTC physical type missing: ' + n + '.' + f['name'])
        need(any(f['name'] == 'mutationTransactionId' for f in fields(block['body'])), 'Atomic transaction identity missing: ' + n)
    reached = set(additions['foundation_roots'])
    while True:
        expanded = reached | {f['type'].rstrip('?[]') for n in reached for f in fields(models[n]['body']) if '@relation' in f['attributes'] and 'fields:' in f['attributes']}
        if expanded == reached:
            break
        reached = expanded
    need(set(foundation) == reached, 'Foundation parent-FK closure broken')
    for n, block in foundation.items():
        for f in fields(block['body']):
            target = f['type'].rstrip('?[]')
            need(target not in models or target in foundation, 'Foundation dangling relation: ' + n + '.' + f['name'])
        need(rows[n]['stage'] == 'F0_FOUNDATION', 'Foundation stage mismatch: ' + n)
    compatibility = review['compatibility_cases']
    need(len(compatibility) == 12 and {r['model'] for r in compatibility} == {r['model'] for r in inventory['compatibility_cases']}, 'Twelve compatibility dispositions incomplete')
    need(all(r.get('decision') and r.get('physical_disposition') and r.get('legacy_data_action') for r in compatibility), 'Compatibility lacks individual disposition')
    need('QueueJob' not in models and review['architecture_only_cases'][0]['physical_disposition'] == 'DERIVED_SQL_VIEW_ONLY_NO_TABLE', 'Architecture-only queue manufactured as storage')

    def body(n):
        return models[n]['body']
    def field(n, f):
        return next((x for x in fields(body(n)) if x['name'] == f), {})
    need('platform_screening' in full['OrderSourceType']['body'] and field('Order', 'sellerProfessionalProfileId').get('type') == 'String?', 'Screening source requires fake seller')
    need(all(field(n, 'customerProfileId').get('type') == 'String' for n in ['Order', 'Booking', 'BookingHold', 'BookingSlotLock']), 'Fresh buyer identity optional')
    need(all(field('ConsentLog', f).get('type') == 'String' for f in ['contentRevisionId', 'presentationId', 'acceptanceKey', 'fingerprint']), 'Consent exact content/presentation proof missing')
    need('@@unique([userId, acceptanceKey])' in body('ConsentLog'), 'Consent acceptance idempotency missing')
    # P0-C-02: semantic checks stay active even when fingerprints are disabled.
    for grant_field, grant_type in [('backendPid', 'Int'), ('transactionId', 'String')]:
        need(field('DatabaseActionGrant', grant_field).get('type') == grant_type, 'Grant immutable tuple must be nonnullable: ' + grant_field)
    need('@@unique([id, contentRevisionId, userId])' in body('ConsentPresentation'), 'Consent presentation composite key missing')
    need('fields: [presentationId, contentRevisionId, userId], references: [id, contentRevisionId, userId]' in field('ConsentLog', 'candidatePresentationId').get('attributes', ''), 'Consent presentation composite FK missing')
    for model in ['ConsentPresentation', 'ConsentLog']:
        need(all(field(model, f).get('type') == 'String' for f in ['userId', 'actionOwner', 'action', 'contextOwner', 'contextKind']), 'Consent accepting user/action/context fields missing: ' + model)
    need('@db.Uuid' in field('ConsentPresentation', 'userId').get('attributes', '') and 'fields: [userId], references: [id]' in field('ConsentPresentation', 'subject').get('attributes', ''), 'Consent presentation user FK missing')
    need(field('ConsentLog', 'presentationHash').get('type') == 'String' and '@db.Char(64)' in field('ConsentLog', 'presentationHash').get('attributes', ''), 'Consent acknowledged presentation hash missing')
    for n in ['PointLedgerEntry', 'ProfessionalBalanceLedgerEntry', 'PayoutTransfer', 'TrackUsageEvent']:
        need('@unique' in field(n, 'semanticEffectKey').get('attributes', '') and field(n, 'effectReceiptId').get('type') == 'String', 'Durable semantic effect/receipt missing: ' + n)
    need(field('MediaUploadSession', 'status').get('type') == 'MediaUploadAttemptState' and field('MediaUploadSession', 'policyId').get('type') == 'String', 'Media attempt conflated with asset/policy')
    need('@default(false)' in field('CandidateProfile', 'isVisible').get('attributes', '') and not field('CandidateProfile', 'resumeUrl'), 'Candidate discovery/private resume regression')
    need('@@unique([userId, track])' in body('TrackBaseSelection') and '@default(none)' in field('TrackSubscription', 'provider').get('attributes', ''), 'Free/current Track selection regression')
    for n in ['TaxYearEarningsSummary', 'PrizeTaxYearSummary']:
        need('@@unique([userId, taxYear, currency, jurisdiction, reportingRegime])' in body(n), 'Fiscal dimensions collapsed: ' + n)
    need(not any(field('NotificationSubscription', f) for f in ['endpoint', 'token', 'auth', 'p256dh']), 'Raw notification credentials reintroduced')
    need(not any(field(n, f) for n in ['BookingVideoRoom', 'JobInterviewVideoRoom'] for f in ['buyerJoinUrl', 'professionalJoinUrl', 'candidateJoinUrl', 'interviewerJoinUrl']), 'Reusable participant credentials reintroduced')
    need(not field('Order', 'stripeTransferId') and not field('BookingHold', 'lockId'), 'Retired compatibility authority reintroduced')

    evidence = json.loads(packet['contracts/database-review/owner-mutation-evidence.v1.schema.json'])
    need(set(evidence['$defs']) == set(models), 'Closed evidence shape coverage missing')
    for n, shape in evidence['$defs'].items():
        need(shape.get('additionalProperties') is False, 'Open evidence envelope: ' + n)
        for k in ['primaryKey', 'prior', 'committed']:
            value = shape['properties'][k]
            need(value.get('additionalProperties') is False and set(value.get('required', [])) == set(value['properties']), 'Empty/incomplete evidence snapshot allowed: ' + n + ':' + k)
        if field(n, 'revision'):
            need('revision' in shape['properties']['committed']['properties'], 'Evidence omits source revision: ' + n)
    boundaries = read('database-candidate-json-boundaries')['boundaries']
    expected_json = {(n, f['name']) for n, b in models.items() for f in fields(b['body']) if f['type'].rstrip('?') == 'Json'}
    need({(b['model'], b['field']) for b in boundaries} == expected_json and len(boundaries) == len(expected_json), 'JSON field boundary coverage missing')
    need(all(b['schemas'] or b['admission'] in ['DENY_NON_NULL_UNTIL_EXACT_CLOSED_SCHEMA_AND_OWNER_STAGE_REVIEW', 'NULL_ONLY_IN_INITIAL_CUSTOMER_SLICE'] for b in boundaries), 'Untyped JSON admission introduced')

    table_rows = [r for r in access['objects'] if r['kind'] == 'table']
    need({r['model'] for r in table_rows} == set(models) and len(table_rows) == len(models), 'Object access table coverage incomplete')
    for r in table_rows:
        need(r['postgres_owner'] == 'wa_schema_owner' and r['rls'] == 'ENABLE_AND_FORCE', 'Table ownership/RLS weakened: ' + r['model'])
        need(all(not grants for grants in r['browser_api_roles'].values()), 'Internal API grant introduced: ' + r['model'])
    roles = {r['role']: r for r in access['roles']}
    for n in ['wa_app_runtime', 'wa_worker', 'wa_context_issuer', 'wa_private_helper_owner', 'wa_schema_owner']:
        need(n in roles and roles[n]['bypassrls'] is False and roles[n]['inherit'] is False, 'Runtime/helper bypass or inheritance: ' + n)
    need(roles['wa_schema_owner']['login'] is False and roles['wa_private_helper_owner']['login'] is False, 'Nonlogin owner became login')
    need(access['migration_driver'] == 'PINNED_PRISMA_7_10_1_MIGRATE_DEPLOY_ONE_APPLICATION_SQL_HISTORY' and not access['data_api_exposure_for_tests'] and not access['tests_executed'], 'Competing migration driver/exposure/runtime claim')
    kinds = {r['kind'] for r in access['objects']}
    need({'schema', 'table', 'enum', 'function', 'trigger_and_function_family_instance', 'view', 'sequence_policy'} <= kinds, 'Object category missing')
    spec = {r['id']: r for r in sql}
    need(set(spec) == {'SQL-%02d' % n for n in range(1, 19)}, 'SQL-only enforcement register incomplete')
    for r in sql:
        need(r['implementation'] == 'SPECIFICATION_ONLY_NO_SQL_GENERATED' and r['test_status'] == 'NOT_RUN' and r['positive_test'] and r['negative_test'], 'SQL specification falsely executed or lacks coverage')
    binding = spec['SQL-02'].get('binding_protocol', {})
    need(binding.get('strategy') == 'ISSUER_COMMITS_IMMUTABLE_TRANSACTION_TUPLE' and binding.get('isolation') == 'READ_COMMITTED_ONLY', 'Rollback-safe issuance/isolation missing')
    need(binding.get('immutable_fields') == ['databaseLoginRole', 'backendPid', 'transactionId'] and binding.get('helper_grant_writes') == [], 'Immutable tuple/helper write boundary weakened')
    need(binding.get('issuer_commit') == 'SEPARATE_CREDENTIAL_AND_SEPARATE_TRANSACTION_BEFORE_BIND' and binding.get('capture_before') == 'ANY_BUSINESS_READ_OR_SOURCE_LOCK', 'Issuer commit/source-lock ordering missing')
    need(binding.get('rollback_rule') == 'OLD_GRANT_REMAINS_BOUND_TO_OLD_XID_AFTER_FULL_OR_SAVEPOINT_ROLLBACK', 'Rollback/savepoint lifetime missing')
    consent = spec['SQL-05'].get('consent_binding', {})
    need(consent.get('native_fk') == ['presentationId','contentRevisionId','userId'] and consent.get('presentation_key') == ['id','contentRevisionId','userId'], 'Consent SQL/native key disagreement')
    need(consent.get('equal_fields') == ['actionOwner','action','contextOwner','contextKind'] and consent.get('null_safe_fields') == ['contextId'] and consent.get('hash_pair') == ['presentationHash','renderedHash'], 'Consent exact context/hash comparison missing')
    need('IS NOT DISTINCT FROM' in spec['SQL-05']['exact_requirement'] and consent.get('new_personal_metadata') is False, 'Consent NULL-context/minimization missing')
    grant_access = next(r for r in table_rows if r['model'] == 'DatabaseActionGrant')
    operations = grant_access.get('operations_by_role', {})
    need(operations.get('wa_context_issuer') == ['INSERT_AUTHORIZED_IMMUTABLY_BOUND_GRANT','SELECT_OWN_ISSUED_GRANT','UPDATE_REVOKED_AT_NULL_TO_TIMESTAMP_ONLY'], 'Issuer grant operations ambiguous')
    need(operations.get('wa_private_helper_owner') == ['SELECT_BOUNDED_GRANT_COLUMNS_VIA_DEFINER_ONLY'], 'Helper grant writes or login permitted')
    for role in ['wa_app_runtime','wa_worker']:
        need(operations.get(role) == ['EXECUTE_BIND_REQUEST_CONTEXT','CONTEXT_ALLOWS_BOOLEAN_VIA_POLICY'], 'Direct grant-table access permitted: ' + role)
        need(grant_access.get('direct_denials_by_role', {}).get(role) == ['SELECT','INSERT','UPDATE','DELETE','SET_ROLE_ISSUER_HELPER_OWNER'], 'Direct grant-table denial missing: ' + role)
    helper_functions = [r for r in access['objects'] if r['kind'] == 'function']
    need(all('mutate only' not in r.get('purpose','') for r in helper_functions), 'Helper function still mutates grant binding')
    for token in ['256-bit', 'session_user', 'pg_backend_pid()', 'pg_current_xact_id()', 'security/source generations']:
        need(token in spec['SQL-02']['exact_requirement'], 'Trusted context binding weakened: ' + token)
    for token in ['same transaction', 'CustomerProfileLifecycleEvent', 'assignDefaultFreeTrack.v1', 'caller spoofing rejected']:
        need(token in spec['SQL-08']['exact_requirement'], 'Atomic source/history/message obligation missing: ' + token)
    need('btree_gist' in spec['SQL-13']['exact_requirement'] and 'native GiST exclusion' in spec['SQL-13']['exact_requirement'], 'Scheduling exclusion left unresolved')
    need(all(r.get('status') == 'PROPOSED_DISPOSITION_NOT_REMEDIATED' for r in access['advisor_dispositions']) and len(access['advisor_dispositions']) == 2, 'Advisor remediation falsely claimed')
    test_rows = tests['tests']
    for n in models:
        for suffix in ['ALLOW', 'DENY']:
            need(any(t['id'] == 'P0C-TABLE-' + n + '-' + suffix and t['phase'] == 'P0-C' for t in test_rows), 'Actual role positive/negative test missing: ' + n + ':' + suffix)
    table_by_model = {r['model']: r for r in table_rows}
    for test in test_rows:
        if test['id'].startswith('P0C-TABLE-'):
            model_name, direction = test['id'][10:].rsplit('-', 1)
            setup = test['setup']
            key = 'operations_by_role' if direction == 'ALLOW' else 'direct_denials_by_role'
            need(setup.get(key) == table_by_model[model_name].get(key) and bool(setup.get(key)), 'Exact access-test role operations missing: ' + test['id'])
            need('or the narrowly registered purpose role' not in str(setup), 'Ambiguous access-test principal: ' + test['id'])
    context_case = next(t for t in test_rows if t['id'] == 'P0C-CTX-01')
    need(all(token in context_case['action'] for token in ['full ROLLBACK','SAVEPOINT','failed bind','same-pool','new xid','wrong isolation']), 'Rollback/savepoint/pool negative test missing')
    need(all(t['status'] == 'NOT_RUN' and t.get('requirement') and t.get('action') and t.get('expected') for t in test_rows), 'Unexecuted tests promoted or lack expected outcome')
    need({'P0-C', 'P0-D', 'P0-E', 'P0-F'} <= {t['phase'] for t in test_rows}, 'Qualification phases conflated')
    for p in ['prisma.review.config.ts', 'prisma.foundation-review.config.ts']:
        config = '\n'.join(l for l in packet[p].splitlines() if not l.strip().startswith('//'))
        need(not any(word in config for word in ['datasource', 'dotenv', 'process.env', 'migrations', 'shadow']), 'Offline config can select database: ' + p)
    need('generator ' not in packet[review['full_schema']] and 'generator ' not in packet[review['foundation_schema']], 'Review unexpectedly generates application client')
    need(native['status'] == 'PASS_OFFLINE_SCHEMA_ONLY' and native.get('node') == 'v24.22.1' and native.get('prisma') == '7.10.1' and len(native['commands']) >= 2 and all(c['exit_code'] == 0 for c in native['commands']), 'Missing actual pinned native validation')
    for p, expected in native['schemas_sha256'].items():
        need(digest(packet[p].encode()) == expected, 'Native validation schema drift: ' + p)
    if check_hashes:
        need(digest(packet['prisma/schema.prisma'].encode()) == review['source_schema_sha256'] == inventory['schema_sha256'], 'Historical schema source changed')
        for path_key, hash_key in [('full_schema', 'full_schema_sha256'), ('foundation_schema', 'foundation_schema_sha256')]:
            need(digest(packet[review[path_key]].encode()) == review[hash_key], 'Candidate schema hash drift')
        for p, expected in manifest['files_sha256'].items():
            actual = packet[p].encode() if p in packet else (root / p).read_bytes()
            need(digest(actual) == expected, 'Candidate artifact fingerprint changed: ' + p)
        for row in read('database-candidate-source-review')['inputs']:
            need((root / row['path']).is_file() and digest((root / row['path']).read_bytes()) == row['sha256'], 'Reviewed source changed: ' + row['path'])
        for p, expected in manifest['preserved_source_sha256'].items():
            need((root / p).is_file() and digest((root / p).read_bytes()) == expected, 'Preserved source changed: ' + p)
    return {'status': 'FAIL' if errors else 'PASS', 'errors': errors,
            'existing_models': len(original), 'candidate_models': len(models),
            'foundation_models': len(foundation), 'compatibility_cases': len(compatibility),
            'sql_requirements': len(sql), 'planned_tests_not_run': len(test_rows),
            'scope': 'Offline source/evidence/semantic checks; not database/RLS/worker/provider execution'}


if __name__ == '__main__':
    try:
        result = inspect()
    except (OSError, KeyError, TypeError, ValueError) as exc:
        result = {'status': 'FAIL', 'errors': ['Candidate packet unavailable/malformed: ' + str(exc)]}
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
