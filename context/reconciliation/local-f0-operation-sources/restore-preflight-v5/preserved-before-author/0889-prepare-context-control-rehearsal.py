"""Prepare a finite P0C-CTX-01 source packet; no process or database execution.

The packet is a proposed session protocol, not an executable coordinator. Existing
selected tests remain NOT_RUN. --prepare exclusively creates a NEW output folder.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review-output/context-control-rehearsal'
CONTROL = 'P0C-CTX-01'
NS = uuid.UUID('5f48469a-ec0d-4582-83c4-9794e5a620e4')
APPLICATION = 'review-output/foundation-application.review.sql'
ACL = 'context/reconciliation/foundation-sql-draft-access.json'
INPUTS = ('scripts/prepare-context-control-rehearsal.py', 'scripts/check-context-control-rehearsal.py',
          'scripts/prepare-customer-control-rehearsal.py', 'scripts/contract_schema.py',
          APPLICATION, ACL, 'scripts/assemble-foundation-sql-review.py',
          'scripts/sql-review/foundation-verification.sql', 'scripts/sql-review/foundation-service-authority.sql',
          'context/reconciliation/foundation-sql-scope-policy.json', 'context/reconciliation/database-candidate-tests.json',
          'contracts/shared/SH-004.v1.schema.json', 'contracts/shared/types.v1.schema.json',
          'contracts/database-review/foundation-payloads.v1.schema.json',
          'contracts/database-review/owner-mutation-evidence.v1.schema.json', 'context/shared/contracts/SH-004.md',
          'context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md',
          'context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-implementation-plan.md',
          'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md',
          'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md')
DEPENDENCIES = ['EXACT_SOURCE_AND_PACKET_REVIEW', 'FRESH_OWNED_DISPOSABLE_TARGET',
                'AUTHENTICATION_AND_FINALIZATION_PASS', 'EXACT_NATIVE_CATALOG_PARITY',
                'EXACT_FIXTURE_NAMESPACE_ABSENCE', 'FIXTURE_TRIGGER_RESTORATION_PROOF',
                'ACTUAL_RESTRICTED_CUSTOMER_CREATION_AND_SCHEDULING', 'REVIEWED_FINITE_SESSION_COORDINATOR']
OPS = {'capture', 'issue', 'bind', 'sql', 'begin', 'close', 'observer', 'expect_bind_error'}


def uid(value): return str(uuid.uuid5(NS, value))
def sha(value): return hashlib.sha256(value).hexdigest()
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def sql(*lines): return '\n'.join(lines) + '\n'
def insert(table, values):
    return 'INSERT INTO ' + table + ' (' + ','.join('"' + key + '"' for key in values) + ') VALUES (' + ','.join(values.values()) + ');'


def helper(root):
    path = Path(root) / 'scripts/prepare-customer-control-rehearsal.py'
    spec = importlib.util.spec_from_file_location('context_customer_fixture_source', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def finite_fields(acl, login, model, row_id, verbs=('SELECT',), revision=0):
    result = {model + '/' + row_id + '/' + row['operation'] + '/' + field
              for row in acl if row['role'] == login and row['model'] == model and row['operation'] in verbs
              for field in row['fields']}
    result.add(model + '/' + row_id + '/revision/' + str(revision))
    if len(result) < 2 or any('*' in token for token in result): raise ValueError('empty/wildcard field scope')
    return sorted(result)


def build(root=ROOT, expected_sha256=None):
    root = Path(root)
    fingerprints = {path: sha((root / path).read_bytes()) for path in INPUTS}
    if expected_sha256 is not None and (set(expected_sha256) != set(INPUTS) or expected_sha256 != fingerprints):
        raise ValueError('approved source pins differ before helper import')
    acl = json.loads((root / ACL).read_text(encoding='utf8'))
    worker_acl = [row for row in acl if row['role'] == 'wa_worker']
    if len(worker_acl) != 32: raise ValueError('32-row worker ACL ceiling changed')
    scope = json.loads((root / 'context/reconciliation/foundation-sql-scope-policy.json').read_text(encoding='utf8'))
    customer_scope = {'owner': 'customer_buyer_profile', 'action': 'SH-004.v1', 'purpose': 'resolve', 'root_kind': 'CustomerProfile', 'verbs': ['SELECT']}
    if customer_scope not in scope['domain_scopes']: raise ValueError('registered Customer resolve scope changed')
    cm = helper(root); registry = cm.FixtureRegistry(root)
    for path in ('contracts/database-review/foundation-payloads.v1.schema.json', 'contracts/database-review/owner-mutation-evidence.v1.schema.json'):
        doc = json.loads((root / path).read_text(encoding='utf8')); registry.documents[doc['$id']] = doc
    source, source_sql, source_observer = cm.create_case('ctx01-source-customer', 'valid', acl, registry)
    source['control_ids'] = [CONTROL]
    source['transaction_sql'] = 'source-customer.sql'; source['observer_sql'] = 'source-customer-observe.sql'
    user, customer, outbox = [source['ids'][key] for key in ('user', 'CustomerProfile', 'free')]
    work, receipt, service = uid('work'), uid('identity-bootstrap'), 'ctx01-control-synthetic.v1'
    tables = ('app.users', 'app.user_security_profiles')
    seeds = ['-- Independent synthetic Identity prerequisites, not owner mutation proof.', 'BEGIN;']
    seeds += ['ALTER TABLE ' + table + ' DISABLE TRIGGER owner_commit;' for table in tables]
    seeds += [insert('app.users', {'id': quote(user), 'is_public': 'false', 'revision': '0', 'privacy_generation': '0', 'created_at': 'clock_timestamp()', 'updated_at': 'clock_timestamp()'}),
              insert('app.user_security_profiles', {'id': quote(uid('user-security')), 'user_id': quote(user), 'revision': '0', 'security_generation': '0', 'created_at': 'clock_timestamp()', 'updated_at': 'clock_timestamp()'})]
    seeds += ['ALTER TABLE ' + table + ' ENABLE TRIGGER owner_commit;' for table in reversed(tables)] + ['COMMIT;']
    triggers, restoration = cm.fixture_trigger_restoration((root / APPLICATION).read_text(encoding='utf8'))
    files = {'trusted-identity-fixtures.sql': sql(*seeds), 'fixture-trigger-restore-observe.sql': restoration,
             'source-customer.sql': source_sql, 'source-customer-observe.sql': source_observer}
    if source_sql.count('COMMIT;') != 1 or not source_sql.rstrip().endswith('COMMIT;'):
        raise ValueError('unexpected source transaction boundary')
    # Same exact registered source group and semantic key; only final transaction
    # outcome differs. No persistent mutation is declared as a successful API retry.
    files['source-customer-rollback.sql'] = source_sql.rstrip()[:-len('COMMIT;')] + 'SET CONSTRAINTS ALL IMMEDIATE;\nROLLBACK;\n'
    files['identity-bootstrap.sql'] = sql('-- Separate actual wa_identity_service_authority; fixture-only upstream authorization.', 'BEGIN;',
        insert('platform_private.identity_service_receipt', {'id': quote(receipt), 'service_principal': quote(service), 'security_generation': '0', 'transition': "'bootstrap'", 'identity_authorization_ref': "'ctx01-synthetic-bootstrap.v1'"}),
        insert('platform_private.identity_service_authorization', {'service_principal': quote(service), 'security_generation': '0', 'identity_receipt_id': quote(receipt)}), 'COMMIT;')
    files['schedule.sql'] = sql('-- Actual bound wa_app_runtime; separate issuer has committed.',
        insert('platform.runtime_work_item', {'id': quote(work), 'outbox_message_id': quote(outbox), 'handler_name': "'assignDefaultFreeTrack.v1'", 'semantic_work_key': quote(source['fixture_values']['free_command']['semanticKey']), 'state': "'pending'", 'fence': '0', 'attempt_count': '0'}),
        "SELECT 'WA_CTX01_SCHEDULE_READY';", 'COMMIT;')
    files['app-read.sql'] = sql("SELECT jsonb_build_object('visible_exact_root',count(*)) FROM app.customer_profiles WHERE id=" + quote(customer) + ';')
    files['worker-read.sql'] = sql("SELECT jsonb_build_object('visible_exact_root',count(*)) FROM platform.runtime_work_item WHERE id=" + quote(work) + ';')
    files['app-read-purpose-update.sql'] = sql("WITH changed AS (UPDATE app.customer_profiles SET display_name='ctx01 forbidden update',revision=revision+1 WHERE id=" + quote(customer) + " RETURNING id) SELECT jsonb_build_object('modified',count(*)) FROM changed;")
    files['savepoint.sql'] = 'SAVEPOINT ctx01_before_bind;\n'
    files['rollback-to-savepoint.sql'] = 'ROLLBACK TO SAVEPOINT ctx01_before_bind;\n'
    files['rollback.sql'] = 'ROLLBACK;\n'; files['commit.sql'] = 'COMMIT;\n'
    files['unissued-guc.sql'] = sql("SET LOCAL wa.actor_user_id=" + quote(user) + ';', "SET LOCAL wa.owner_module_id='customer_buyer_profile';",
        "SET LOCAL wa.action='SH-004.v1';", "SET LOCAL wa.purpose='resolve';", "SET LOCAL wa.context_hash='" + '0' * 64 + "';")
    files['work-observe.sql'] = sql("SELECT jsonb_build_object('work_count',(SELECT count(*) FROM platform.runtime_work_item WHERE id=" + quote(work) + "),'exact_pending_work',EXISTS(SELECT 1 FROM platform.runtime_work_item WHERE id=" + quote(work) + ' AND outbox_message_id=' + quote(outbox) + " AND handler_name='assignDefaultFreeTrack.v1' AND semantic_work_key=" + quote(source['fixture_values']['free_command']['semanticKey']) + " AND state='pending' AND fence=0 AND attempt_count=0 AND lease_token_hash IS NULL AND lease_expires_at IS NULL AND effect_receipt_id IS NULL),'attempts',(SELECT count(*) FROM platform.runtime_attempt WHERE work_item_id=" + quote(work) + "),'track_enrollments',(SELECT count(*) FROM app.track_enrollment_receipt WHERE profile_id=" + quote(customer) + '));')
    files['grant-write-acl-observe.sql'] = sql("SELECT jsonb_build_object('app_no_grant_write',NOT (has_table_privilege('wa_app_runtime','platform.database_action_grant','INSERT') OR has_any_column_privilege('wa_app_runtime','platform.database_action_grant','UPDATE') OR has_table_privilege('wa_app_runtime','platform.database_action_grant','DELETE')),'worker_no_grant_write',NOT (has_table_privilege('wa_worker','platform.database_action_grant','INSERT') OR has_any_column_privilege('wa_worker','platform.database_action_grant','UPDATE') OR has_table_privilege('wa_worker','platform.database_action_grant','DELETE')),'helper_no_grant_write',NOT (has_table_privilege('wa_private_helper_owner','platform.database_action_grant','INSERT') OR has_any_column_privilege('wa_private_helper_owner','platform.database_action_grant','UPDATE') OR has_table_privilege('wa_private_helper_owner','platform.database_action_grant','DELETE')),'app_native_update_columns',has_column_privilege('wa_app_runtime','app.customer_profiles','display_name','UPDATE') AND has_column_privilege('wa_app_runtime','app.customer_profiles','revision','UPDATE'));" )
    def template(name, login, owner, action, purpose, model, row_id, fields, principal=None, service_principal=None):
        return {'template_id': name, 'database_login_role': login, 'issuer_service': 'wa_context_issuer', 'owner_module_id': owner,
                'action': action, 'purpose': purpose, 'target_kind': model, 'target_id': row_id, 'principal_user_id': principal,
                'service_principal': service_principal, 'source_generation': '0', 'security_generation': '0', 'allowed_fields': fields,
                'policy_version': 'ctx01-source-fixture.v1', 'status': 'NOT_RUN'}
    app = template('app', 'wa_app_runtime', 'customer_buyer_profile', 'SH-004.v1', 'resolve', 'CustomerProfile', customer,
                   finite_fields(acl, 'wa_app_runtime', 'CustomerProfile', customer), principal=user)
    worker = template('worker', 'wa_worker', 'platform_integration_owner', 'runtime.claim_work.v1', 'work.claim', 'RuntimeWorkItem', work,
                      finite_fields(acl, 'wa_worker', 'RuntimeWorkItem', work), service_principal=service)
    schedule = template('schedule', 'wa_app_runtime', 'platform_integration_owner', 'runtime.schedule_work.v1', 'work.schedule', 'RuntimeWorkItem', work,
                        finite_fields(acl, 'wa_app_runtime', 'RuntimeWorkItem', work, ('SELECT', 'INSERT')), principal=user)
    grants = {'app': app, 'worker': worker, 'schedule': schedule, 'source_customer': source['grant']}
    grants['app-read-with-update-caps'] = {**deepcopy(app), 'template_id': 'app-read-with-update-caps', 'allowed_fields': sorted(app['allowed_fields'] + ['CustomerProfile/' + customer + '/UPDATE/' + field for field in ('@row', 'displayName', 'revision')])}
    for name, changes in [('wrong-purpose', {'purpose': 'profile_update'}), ('wrong-action', {'action': 'SH-114.v1'}),
                          ('wrong-owner', {'owner_module_id': 'track_subscription_entitlement'}), ('wrong-root-id', {'target_id': uid('foreign-root')}),
                          ('wrong-root-kind', {'target_kind': 'RuntimeWorkItem'})]:
        grants[name] = {**deepcopy(app), 'template_id': name, **changes}
    def step(op, **values):
        if op not in OPS: raise ValueError('unknown protocol operation')
        return {'op': op, **values}
    def capture(session='A', **more): return step('capture', session=session, login_identity='session_user=current_user=actual_login', database='wa_p0c_rehearsal', tuple_fields=['backend_pid', 'transaction_id', 'backend_start'], protected_reads_before_capture=False, **more)
    def issue(label, base, session='A'):
        return step('issue', session=session, instance=label, template=base, commit_and_close_issuer_before_bind=True)
    def bind(label, session='A'): return step('bind', session=session, instance=label)
    def query(file, expected, session='A'): return step('sql', session=session, file=file, expected=expected)
    def close(session='A'): return step('close', session=session, require_client_exit_and_exact_backend_absence=True)
    def error(label, session='A', reason='TUPLE_MISMATCH', message='invalid, stale or unsupported context'):
        return step('expect_bind_error', session=session, instance=label, reason=reason, psql_exit_code=3, acknowledgement=False,
                    diagnostic={'sqlstate': '42501', 'exact_message': message, 'function': 'platform_private.bind_request_context(text)', 'require_exact_source_body_hash_and_raise_line': True},
                    later_statements_forbidden=True)
    def begin(session='A', isolation='read committed'): return step('begin', session=session, isolation=isolation, same_actual_connection=True)
    cases = []
    def add(name, login, steps, *, vectors=('POOL-LIFETIME',), claim=None):
        cases.append({'name': name, 'control_id': CONTROL, 'vectors': list(vectors), 'actual_login': login, 'status': 'NOT_RUN',
                      'runtime_eligibility': 'PENDING_INDEPENDENT_PACKET_AND_COORDINATOR_REVIEW', 'execution_dependencies': list(DEPENDENCIES),
                      'steps': steps, 'bounded_claim': claim or 'Only exact restricted source binding/visibility for this finite transaction protocol.',
                      'mandatory_after_case': 'After all case backends close, independently verify every issued row remains issuer-owned, immutable, unrevoked and unexpired; attempt EACH case-issued old instance once on a fresh actual connection of its declared login/new xid, exact source-bound42501/psql3/noACK, then close before observations. The fresh unissued instance has no retention row.'})
    for family, login in (('app', 'wa_app_runtime'), ('worker', 'wa_worker')):
        read = family + '-read.sql'
        positive = lambda: query(read, {'visible_exact_root': 1})
        zero = lambda: query(read, {'visible_exact_root': 0})
        add(family + '-no-context', login, [capture(), zero(), query('rollback.sql', None), close()])
        add(family + '-same-live-xid-rebind', login, [capture(), issue('G1', family), bind('G1'), positive(), bind('G1'), positive(), query('rollback.sql', None), close()])
        for end in ('rollback', 'commit'):
            add(family + '-' + end + '-same-pool-fresh-then-old', login,
                [capture(tuple_label='T1'), issue('G1', family), bind('G1'), positive(), query(end + '.sql', None),
                 begin(), capture(tuple_label='T2', require_same_backend_as='T1', require_distinct_xid_from='T1'), issue('G2', family), bind('G2'), positive(), query('commit.sql', None),
                 begin(), capture(tuple_label='T3', require_same_backend_as='T1', require_distinct_xid_from=['T1', 'T2']), error('G1'), close(),
                 step('observer', file='grant-retention', instances=['G1', 'G2'], expected_unchanged_issuer_rows=2)],
                claim='Fresh separately committed G2 succeeds on same backend/new xid; G1 rejects later xid. No owner/API idempotency claim.')
        add(family + '-savepoint-bind-rollback-rebind', login,
            [capture(tuple_label='T1'), query('savepoint.sql', None), issue('G1', family), bind('G1'), positive(), query('rollback-to-savepoint.sql', None), zero(),
             bind('G1'), positive(), query('rollback.sql', None), begin(), capture(tuple_label='T2', require_same_backend_as='T1', require_distinct_xid_from='T1'), error('G1'), close(),
             step('observer', file='grant-retention', instances=['G1'], expected_unchanged_issuer_rows=1)])
        add(family + '-different-backend', login,
            [capture(tuple_label='T1'), issue('G1', family), bind('G1'), positive(), begin(session='B'), capture(session='B', tuple_label='T2', require_distinct_backend_from='T1'),
             error('G1', session='B'), close('B'), query('rollback.sql', None), close()])
        for isolation in ('repeatable read', 'serializable'):
            add(family + '-wrong-isolation-' + isolation.replace(' ', '-'), login,
                [begin(isolation=isolation), capture(), issue('G1', family), error('G1', reason='UNSUPPORTED_ISOLATION'), close()])
        add(family + '-unissued-hash-and-caller-gucs', login, [capture(), query('unissued-guc.sql', None), zero(), query('rollback.sql', None), close()],
            vectors=('POOL-LIFETIME', 'SCOPE-PURPOSE'), claim='Unissued context hash and caller identity/action GUCs confer no authority. A hash matching an independently committed exact tuple is valid transport, not an additional authorization source.')
        add(family + '-well-formed-unissued-secret', login, [capture(), error('UNISSUED_FRESH_SECRET', reason='NO_ISSUER_ROW'), close()])
        add(family + '-malformed-secret', login, [capture(), error('MALFORMED_RUNTIME_SECRET', reason='MALFORMED_SECRET', message='invalid context'), close()])
        add(family + '-failed-bind-wrong-xid-retains-issued-row', login,
            [capture(tuple_label='T1'), issue('G1', family), query('rollback.sql', None), begin(), capture(tuple_label='T2', require_same_backend_as='T1', require_distinct_xid_from='T1'), error('G1'), close(),
             step('observer', file='grant-retention', instances=['G1'], expected_unchanged_issuer_rows=1)])
    for name in ('wrong-purpose', 'wrong-action', 'wrong-owner', 'wrong-root-id', 'wrong-root-kind'):
        add('app-' + name, 'wa_app_runtime', [capture(), issue('G1', name), bind('G1'), query('app-read.sql', {'visible_exact_root': 0}), query('rollback.sql', None), close()], vectors=('SCOPE-PURPOSE',))
    add('app-resolve-purpose-denies-source-update', 'wa_app_runtime',
        [capture(), issue('G1', 'app-read-with-update-caps'), bind('G1'), query('app-read.sql', {'visible_exact_root': 1}),
         query('app-read-purpose-update.sql', {'modified': 0}), query('rollback.sql', None), close()], vectors=('READ-PURPOSE-NO-WRITE',),
        claim='Registered Customer resolve allows SELECT only despite exact root/revision/UPDATE caps and native column UPDATE privileges. Zero-row RLS denial, no update/result codec invented.')
    add('app-grant-does-not-bind-worker-login', 'wa_worker',
        [capture(session='A', tuple_label='T1'), issue('G1', 'app', session='A'), error('G1', reason='ACTUAL_LOGIN_MISMATCH'), close()], vectors=('POOL-LIFETIME',),
        claim='Issuer deliberately names app login while capture and bind use actual worker; login mismatch rejects even if PID/xid match.')
    # The source group itself is retried once only after full ROLLBACK, on the
    # same backend with a new xid and separately committed fresh authorization.
    creation_protocol = [capture(tuple_label='C1'), issue('CREATE1', 'source_customer'), bind('CREATE1'),
        query('source-customer-rollback.sql', {'marker': 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT', 'transaction_end': 'ROLLBACK_ACK'}),
        begin(), capture(tuple_label='C2', require_same_backend_as='C1', require_distinct_xid_from='C1'), issue('CREATE2', 'source_customer'), bind('CREATE2'),
        query('source-customer.sql', {'marker': 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT', 'transaction_end': 'COMMIT_ACK'}),
        begin(), capture(tuple_label='C3', require_same_backend_as='C1', require_distinct_xid_from=['C1', 'C2']), error('CREATE1'), close(),
        step('observer', file='source-customer-observe.sql', expected=source['observer_expected']),
        step('observer', file='grant-retention', instances=['CREATE1', 'CREATE2'], expected_unchanged_issuer_rows=2)]
    controls = json.loads((root / 'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))['tests']
    selected = next(value for value in controls if value['id'] == CONTROL)
    manifest = {'schema': 'workinants.context-control-fixtures.v1', 'status': 'NOT_RUN', 'database_posture': 'D', 'database_contacted': False, 'sql_executed': False,
        'selected_control_ids': [CONTROL], 'source_control_definition': deepcopy(selected), 'source_files_sha256': fingerprints,
        'namespace_policy': {'mode': 'FRESH_DISJOINT_ONLY', 'reuse': 'BLOCKED_WITHOUT_SEPARATELY_REVIEWED_EXACT_STATE_AND_SOURCE_PROOF', 'ids': {**source['ids'], 'work': work, 'identity_bootstrap': receipt, 'user_security': uid('user-security')}, 'service_principal': service, 'all_identity_business_work_grant_instances_must_be_absent': True, 'unissued_hash_must_have_no_matching_row': '0' * 64},
        'source_customer': source, 'source_creation_lifetime_protocol': {'status': 'NOT_RUN', 'actual_login': 'wa_app_runtime', 'steps': creation_protocol, 'execution_dependencies': list(DEPENDENCIES), 'semantic_key': source['semantic_key'], 'limit': 'Same SQL source group retried once after proven rollback; not an owner application adapter or durable committed-result replay.'},
        'setup_order': ['verify pinned source/native catalog/auth/finalization and exact fresh namespace', 'fixture-trigger-restore-observe.sql', 'trusted-identity-fixtures.sql as original bootstrap grantor', 'fixture-trigger-restore-observe.sql after COMMIT or failed-backend closure', 'source_creation_lifetime_protocol on actual app; complete observer only after closure', 'identity-bootstrap.sql as actual wa_identity_service_authority; COMMIT then close', 'schedule.sql as actual bound app with fresh issuer grant; COMMIT then close', 'work-observe.sql and grant-write-acl-observe.sql; then cases'],
        'fixture_trigger_contract': {'status': 'NOT_RUN', 'bypassed': [{'table': table, 'trigger': 'owner_commit'} for table in tables], 'physical_guards_retained': True, 'expected_user_triggers': triggers, 'observer_expected': {'expected_user_trigger_count': len(triggers), 'actual_user_trigger_count': len(triggers), 'exact_user_trigger_set_and_states': True, 'no_project_user_trigger_disabled': True}},
        'mandatory_after_case_observers': [{'file': 'source-customer-observe.sql', 'expected': source['observer_expected']},
            {'file': 'work-observe.sql', 'expected': {'work_count': 1, 'exact_pending_work': True, 'attempts': 0, 'track_enrollments': 0}},
            {'file': 'fixture-trigger-restore-observe.sql', 'expected': {'expected_user_trigger_count': len(triggers), 'actual_user_trigger_count': len(triggers), 'exact_user_trigger_set_and_states': True, 'no_project_user_trigger_disabled': True}},
            {'file': 'grant-write-acl-observe.sql', 'expected': {'app_no_grant_write': True, 'worker_no_grant_write': True, 'helper_no_grant_write': True, 'app_native_update_columns': True}}],
        'after_case_observer_order': 'After ALL original/retirement clients exit and exact backends are independently absent, execute every mandatory_after_case_observers entry and exact per-instance immutable grant-retention observations. No later case if any result differs; save partial evidence and controlled cleanup.',
        'grants': grants, 'cases': cases, 'registered_positive_scope': customer_scope, 'worker_acl_ceiling_rows': worker_acl,
        'worker_acl_ceiling_sha256': sha(json.dumps(worker_acl, sort_keys=True, separators=(',', ':')).encode()),
        'worker_read_scope_limit': 'Actual worker SELECT uses existing runtime.claim_work/work.claim transport scope and exact pending fence0 job. No claim, lease, enrollment, owner result, pure-query purpose or worker loop is created.',
        'runtime_binding_contract': {'status': 'NOT_RUN', 'login': 'Actual separately authenticated login, never SET ROLE.', 'isolation': 'READ COMMITTED except explicit denial controls.', 'tuple_capture': 'Capture actual session_user/current_user/database/PID/full xid/backend_start before protected work; exact PID and full xid must come from that same connection.', 'issuance': 'Fresh UUID grant instance and 256-bit secret per issue step; independently committed immutable row through actual wa_context_issuer; hash only in database, issuer client/backend closed before bind. Bound instance labels refer to memory only.', 'lifetime': 'SAVEPOINT is after tuple capture but before first bind, with fresh connection/no preexisting hash. ROLLBACK TO clears binding; same live full xid may rebind. Full ROLLBACK/COMMIT require explicit acknowledgements before BEGIN/new xid capture.', 'error': 'ON_ERROR_STOP remains enabled. Each expected binder failure requires exact psql3, no ACK, exactly one allowlisted source-bound diagnostic/frame. End connection; never send a later behavioral statement on it.', 'closure': 'Client exit plus independent absence of exact PID/backend_start/login/database before full-state observers. Same-backend new-xid controls finish before this closure; no concurrent business observer is used between their transactions.', 'grant_retention': 'External coordinator must derive fixed query from runtime-only instance UUIDs and compare issuer-owned immutable fields/token hashes to their pre-issue expectations; emit only exact_count/all_immutable_fields_equal/issuer_owned/revoked_false/unexpired booleans. Never retain hashes, secrets, PIDs, xids, backend_start or raw rows.', 'every_old_instance': 'After each finite case and source-creation lifetime protocol, test EVERY issued instance in a fresh actual declared-login READ COMMITTED connection with distinct xid while unrevoked/unexpired; require exact stale binder42501/psql3/noACK and closure. Runtime instance maps remain memory-only. Wrong-isolation cases also retain valid committed grant and retry only at new tuple; no expiry/revocation substitution for tuple proof.', 'output': 'Only allowlisted counts/Boolean comparisons/stage/exit code/source hashes. No arbitrary stderr, diagnostic dictionary, statement bodies or credentials. Persist incrementally on every stage and unexpected failure; stop later cases.'},
        'finite_caps': {'source_customer_groups_committed': 1, 'source_customer_full_rollback_attempts': 1, 'scheduled_jobs': 1, 'worker_claims': 0, 'worker_processing': 0, 'worker_enrollments': 0, 'context_case_count': len(cases), 'grant_instances_max': sum(step['op'] == 'issue' for case in cases for step in case['steps']) + 3, 'old_instance_retirement_probes_max': sum(step['op'] == 'issue' for case in cases for step in case['steps']) + 3, 'grant_ttl_seconds_max': 300, 'pool_connections_per_case_max': 2, 'service_bootstraps': 1, 'polling_or_worker_loop': False},
        'unprepared_obligations': [{'control_id': CONTROL, 'vector': 'READ-PURPOSE-NO-WRITE', 'status': 'NOT_RUN', 'execution_dependencies': ['OTHER_OWNER_READ_FIXTURES_AND_EXACT_SOURCE_REGISTERED_PURPOSES', 'APPEND_READ_PROOF_OWNER_OPERATION_RESULT_NOT_REGISTERED'], 'limit': 'Customer resolve covered only. No invented Customer SH003, projection/history/access-evidence write purpose or append-read proof.'}, {'control_id': CONTROL, 'vector': 'SERVICE-BOOTSTRAP', 'status': 'NOT_RUN', 'execution_dependencies': ['REAL_IDENTITY_UPSTREAM_AUTHORIZATION_QUALIFICATION'], 'limit': 'Synthetic independent service bootstrap supports worker binding only; generation/revoke transitions remain worker CTX02 proposal scope.'}, {'control_id': 'P0C-IMMUTABLE-01', 'status': 'NOT_RUN', 'execution_dependencies': ['SEPARATE_SOURCE_REVIEWED_AGE_AND_CONSENT_PACKET'], 'limit': 'No age/consent mutation or empty-context registry is fabricated here.'}],
        'safety_review_requirements': ['Review session FSM and every dynamic instance allocation/tuple equality; source packet is NOT a runtime coordinator.', 'Pin all source/helper/output hashes before helper execution or SQL; bind fresh immutable created container ID externally.', 'Authentication, original-grantor finalization and complete native catalog must pass before setup; rerun exact trigger restoration after any failure closure.', 'Verify every issued grant row remains immutable/issuer-owned across consumer rollback and binder failure without exporting handle or tuple.', 'Stop on unexpected diagnostic, marker, count, rollback/COMMIT acknowledgment, identity, closure or fixture conflict; retain partial sanitized evidence and controlled exact-resource cleanup.', 'All94 selection and451 database register cases remain NOT_RUN outside individually reviewed/exercised assertions; no migration/hosted/product/P0D authority.']}
    files['README.md'] = '''# CTX01 proposed finite source packet

This packet is source-only and NOT_RUN. It selects existing P0C-CTX-01 only.
Every operation requires a separately reviewed coordinator and fresh owned target.
The original source packet, canonical SQL and 32 worker ACL rows are unchanged.

The actual app creates one complete Customer source group, first rolling that
same group back, then committing a fresh authorization in a new xid on the same
backend. Only after closure may an independent observer check the complete group.
The actual app schedules one pending job; the actual worker reads it under its
existing transport claim scope. No lease, claim, worker loop or Track enrollment.

A savepoint rollback clears the local hash, while the independently committed
grant survives. Rebinding the same grant in that live xid is allowed. A new xid
needs a new grant. GUCs cannot create a missing issuer row: the context hash is
transport for the independently committed exact tuple, never a second authority.

Grant retention is deliberately a runtime-only fixed query contract, not a query
with fake IDs: grant UUIDs and secrets are freshly allocated per issuance. Its
reviewed implementation is a mandatory missing coordinator dependency, not PASS.

Customer resolve is an existing SELECT-only purpose. Its otherwise exact UPDATE
caps must still update zero rows. This proves only that scoped SQL boundary;
missing update result codecs, owner adapters and broader read purposes stay held.

Plain English: A key works for one real trip. Going back to a bookmark may erase
the key from the pocket, but the same trip may pick it up again. A new trip needs
a new key. Writing a pretend name on paper cannot make a real key.
'''
    manifest['prepared_files_sha256'] = {name: sha(text.encode('utf8')) for name, text in files.items()}
    manifest['packet_digest_recipe'] = "SHA256(UTF8 json.dumps({'source_files_sha256':...,'prepared_files_sha256':...},sort_keys=True,separators=(',',':'))); fixtures.json excluded"
    manifest['source_only_packet_sha256'] = sha(json.dumps({key: manifest[key] for key in ('source_files_sha256', 'prepared_files_sha256')}, sort_keys=True, separators=(',', ':')).encode())
    files['fixtures.json'] = json.dumps(manifest, indent=2) + '\n'
    return files, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--prepare', action='store_true'); args = parser.parse_args()
    files, manifest = build()
    if args.prepare:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, value in files.items():
            with (OUT / name).open('x', encoding='utf8', newline='\n') as handle: handle.write(value)
    print(json.dumps({'status': 'PREPARED_NOT_RUN' if args.prepare else 'PLAN_ONLY_NOT_RUN', 'files': len(files), 'cases': len(manifest['cases']), 'packet_sha256': manifest['source_only_packet_sha256'], 'database_contacted': False}))


if __name__ == '__main__': main()
