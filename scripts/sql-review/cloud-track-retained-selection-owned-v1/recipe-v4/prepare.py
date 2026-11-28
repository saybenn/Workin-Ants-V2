"""Prepare held Track retained-selection business SQL from the exact Worker B42 sources."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

import pglast
from pglast import ast, parse_sql
from pglast.stream import RawStream


BASE = 'review-output/worker-recovery-control-rehearsal'
CANDIDATE = 'review-output/track-retained-base-candidate-v1'
ACCEPTED_WORKER = 'context/reconciliation/local-f0-worker-5f189aa-b42c35d5-qualified-evidence.json'
TWO = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/two-2f71c365/operation.json'
CONTEXT = 'scripts/sql-review/run-context-control-rehearsal.py'
PINS = {
    f'{BASE}/fixtures.json': '497275a81de4c06bef1033a461f8cc3ada6d6b42bc1899ae77a7a1f0ca7678f0',
    ACCEPTED_WORKER: '45489b9495ca594034ee9a4d8651813826da464cb12b83b0f82641efb21c897a',
    TWO: 'ad689dc962febeeb72b5f7583598cef559d475b2fe7227d097e57558625cef30',
    CONTEXT: '5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33',
    'review-output/foundation-application.review.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
    'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql':
        '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7',
    f'{CANDIDATE}/migration.sql': 'ae7b94aae1689b54d6da0b9443b2512087018270774124f2b1d012f65f6ddcdb',
    f'{CANDIDATE}/expected-catalog.json': 'df3197e77f3d4c540417c371f8bcd4b80d9c6020c8cf03cc7a18ce23379e8359',
    f'{CANDIDATE}/independent-source-review.json': '88dd682505df6b3d52a39c9eab9ceda75fc7dee04f35849d5596ff605c5f802d',
}
WORKER_FILES = ('B-source-customer.sql', 'B-source-customer-observe.sql', 'B-schedule.sql', 'B-claim.sql',
                'B-genuine-leased-group.sql', 'identity-bootstrap.sql', 'independent-fixtures.sql',
                'complete-state-observe.sql')
UUID = re.compile(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b')
FIXTURE_OWNERS = ('app.users', 'app.user_security_profiles', 'app.track_plans')
PRIOR_OWNERS = ('app.track_subscriptions', 'app.track_base_selection')
REQUIRED_CATALOG = '59a6a99a96748b72d8d639977c457857058777bf99346afb59804df926c107a9'
RESULT_SCHEMA = 'urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult'
EXPECTED_WRITES = Counter({
    ('INSERT', 'platform.runtime_command_receipt'): 1, ('UPDATE', 'platform.runtime_command_receipt'): 1,
    ('INSERT', 'platform.runtime_effect_receipt'): 1, ('INSERT', 'platform.runtime_inbox_receipt'): 1,
    ('UPDATE', 'platform.runtime_work_item'): 1, ('INSERT', 'app.track_enrollment_receipt'): 1,
    ('INSERT', 'platform.runtime_attempt'): 1,
})
EXPECTED_REMOVALS = Counter({
    ('INSERT', 'app.track_subscriptions'): 1, ('INSERT', 'app.track_base_selection'): 1,
    ('INSERT', 'app.track_subscription_events'): 1, ('INSERT', 'app.track_entitlement_grants'): 1,
    ('INSERT', 'platform.owner_mutation_evidence'): 3,
})
EXPECTED_STAGE_NAMES = ('source-customer', 'prior-selection-fixture', 'schedule', 'claim', 'retained-effect')


def need(condition, code):
    if not condition:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wrapped_json(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def pinned(root, relative, digest):
    path = root / relative
    need(path.resolve(strict=True) == path and path.is_file(), 'SOURCE_PATH_DRIFT')
    raw = path.read_bytes()
    need(sha(raw) == digest, 'SOURCE_DIGEST_DRIFT')
    return raw


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def relation(statement):
    return statement.relation.schemaname + '.' + statement.relation.relname


def write_identity(statement):
    if isinstance(statement, ast.InsertStmt):
        return 'INSERT', relation(statement)
    if isinstance(statement, ast.UpdateStmt):
        return 'UPDATE', relation(statement)
    return None


def named_sql(table, values):
    return f"INSERT INTO {table} ({','.join(values)}) VALUES ({','.join(values.values())});"


def source_rows(sql, table):
    values = []
    for wrapped in parse_sql(sql):
        statement = wrapped.stmt
        if isinstance(statement, ast.InsertStmt) and relation(statement) == table:
            [row] = statement.selectStmt.valuesLists
            values.append({field.name: RawStream()(value)
                           for field, value in zip(statement.cols, row, strict=True)})
    return values


def closed_fixture(tables, inserts):
    return '\n'.join(['BEGIN;', *(f'ALTER TABLE {table} DISABLE TRIGGER owner_commit;' for table in tables),
                      *inserts, 'SET CONSTRAINTS ALL IMMEDIATE;',
                      *(f'ALTER TABLE {table} ENABLE TRIGGER owner_commit;' for table in reversed(tables)),
                      'COMMIT;', ''])


def validate_fixture(sql, tables, wanted_rows):
    asts = [row.stmt for row in parse_sql(sql)]
    toggles = [(relation(row), command.subtype.name, command.name) for row in asts
               if isinstance(row, ast.AlterTableStmt) for command in row.cmds]
    need(toggles == [(table, 'AT_DisableTrig', 'owner_commit') for table in tables]
         + [(table, 'AT_EnableTrig', 'owner_commit') for table in reversed(tables)], 'FIXTURE_GUARD_SCOPE')
    writes = Counter(identity for row in asts if (identity := write_identity(row)) is not None)
    need(writes == Counter({('INSERT', table): count for table, count in wanted_rows.items()})
         and len(asts) == 2 * len(tables) + sum(wanted_rows.values()) + 3
         and isinstance(asts[0], ast.TransactionStmt) and isinstance(asts[-1], ast.TransactionStmt)
         and sum(isinstance(row, ast.ConstraintsSetStmt) for row in asts) == 1, 'FIXTURE_FINITE_TRANSACTION')


def retained_body(sql, case):
    retained, removed = [], Counter()
    for line in sql.splitlines():
        parsed = parse_sql(line)
        if not parsed:
            need(not line.strip() or line.lstrip().startswith('--'), 'UNEXPECTED_B42_LINE')
            continue
        [row] = parsed
        identity = write_identity(row.stmt)
        if identity in EXPECTED_REMOVALS:
            removed[identity] += 1
        else:
            retained.append(line)
    need(removed == EXPECTED_REMOVALS, 'B42_GROUP_DRIFT')
    body = '\n'.join([*retained, ''])
    need(body.count('"outcome":"enrolled"') == 3 and body.count("'enrolled'") == 1,
         'B42_RESULT_BOUNDARIES')
    body = body.replace('"outcome":"enrolled"', '"outcome":"already_enrolled"').replace(
        "'enrolled'", "'already_enrolled'")
    marker_name = 'WA_WR_BEFORE_B_GENUINE_LEASED_GROUP'
    need(body.count(marker_name) == 1 and body.count('WA_WR_AFTER_B_GENUINE_LEASED_GROUP') == 1, 'B42_MARKERS')
    stem = case.upper().replace('-', '_')
    before, after = f'WA_TRACK_BEFORE_{stem}', f'WA_TRACK_AFTER_{stem}'
    body = body.replace(marker_name, before).replace('WA_WR_AFTER_B_GENUINE_LEASED_GROUP', after)
    asts = [row.stmt for row in parse_sql(body)]
    need(Counter(identity for row in asts if (identity := write_identity(row)) is not None) == EXPECTED_WRITES
         and len(asts) == 15 and isinstance(asts[-1], ast.TransactionStmt)
         and sum(isinstance(row, ast.ConstraintsSetStmt) for row in asts) == 1, 'RETAINED_EFFECT_SCOPE')
    expected = [before, 'WA_WORKER_EFFECT_LINKED', 'WA_WORKER_GROUP_STAGED', 'WA_WORKER_CONSTRAINTS_CHECKED',
                {'linked_effect_matches': True, 'still_leased': True}, after]
    return body, expected


def narrowed_fields(worker, ids, source, plan_version, plan_digest):
    def caps(model, key, verb):
        [row] = [row for row in worker['worker_acl_rows'] if (row['model'], row['operation']) == (model, verb)]
        return {f'{model}/{key}/{verb}/{field}' for field in row['fields']}

    surfaces = (
        ('RuntimeWorkItem', ids['work'], ('SELECT',)),
        ('RuntimeOutboxMessage', source['free'], ('SELECT',)),
        ('RuntimeCommandReceipt', ids['command'], ('INSERT', 'SELECT')),
        ('RuntimeEffectReceipt', ids['effect'], ('INSERT', 'SELECT')),
        ('RuntimeInboxReceipt', ids['inbox'], ('INSERT', 'SELECT')),
        ('RuntimeAttempt', ids['attempt'], ('INSERT',)),
        ('TrackEnrollmentReceipt', ids['enrollment'], ('INSERT', 'SELECT')),
        ('TrackBaseSelection', ids['selection'], ('SELECT',)),
        ('TrackSubscription', ids['subscription'], ('SELECT',)),
        ('TrackPlan', ids['plan'], ('SELECT',)),
    )
    wanted = {field for model, key, verbs in surfaces for verb in verbs for field in caps(model, key, verb)}
    wanted |= {f'RuntimeWorkItem/{ids["work"]}/{token}' for token in (
        'revision/1', 'UPDATE/@row', 'UPDATE/effectReceiptId', f'command/{ids["command"]}', f'effect/{ids["effect"]}',
    )}
    wanted |= {f'RuntimeCommandReceipt/{ids["command"]}/UPDATE/{field}' for field in (
        '@row', 'state', 'resultBody', 'resultDigest',
    )}
    wanted |= {
        f'CustomerProfile/{source["CustomerProfile"]}/revision/0',
        f'RuntimeEffectReceipt/{ids["effect"]}/revision/1',
        f'TrackBaseSelection/{ids["selection"]}/revision/0', f'TrackSubscription/{ids["subscription"]}/revision/0',
        f'TrackPlan/{ids["plan"]}/revision/0', f'TrackPlan/{ids["plan"]}/version/{plan_version}',
        f'TrackPlan/{ids["plan"]}/contentHash/{plan_digest}',
    }
    return wanted


def observations(ids, source, plan, provider, worker_principal):
    q = {**{name: quote(item) for name, item in ids.items()}, 'customer': quote(source['CustomerProfile']),
         'user': quote(source['user']), 'outbox': quote(source['free'])}
    period = ('s.current_period_start IS NULL AND s.current_period_end IS NULL' if provider == 'none' else
              's.current_period_start<=clock_timestamp() AND s.current_period_end>clock_timestamp()')
    price = 'p.monthly_price_cents IS NULL' if provider == 'none' else "p.monthly_price_cents=1 AND p.currency='USD'"
    prior = f"""SELECT 1 FROM app.track_base_selection b
  JOIN app.track_subscriptions s ON s.id=b.subscription_id
  JOIN app.track_plans p ON p.id=s.plan_id
  WHERE b.id={q['selection']} AND s.id={q['subscription']} AND p.id={q['plan']}
  AND b.user_id={q['user']} AND s.user_id=b.user_id AND b.track='customer' AND s.track=b.track AND p.track=b.track
  AND b.customer_profile_id={q['customer']} AND s.customer_profile_id=b.customer_profile_id
  AND b.candidate_profile_id IS NULL AND b.professional_profile_id IS NULL
  AND s.candidate_profile_id IS NULL AND s.professional_profile_id IS NULL
  AND b.revision=0 AND s.revision=0 AND b.source_generation=0 AND b.mutation_transaction_id=s.mutation_transaction_id
  AND s.status='active' AND s.ended_at IS NULL AND s.provider={quote(provider)}
  AND s.provider_customer_id IS NULL AND s.provider_subscription_id IS NULL AND s.provider_price_id IS NULL
  AND {period}
  AND p.status='active' AND p.billing_model={plan['billing_model']} AND p.version={plan['version']}
  AND p.content_hash={plan['content_hash']} AND {price}"""
    expected_result = f"jsonb_build_object('outcome','already_enrolled','selectionRevision','0','receipt',{q['enrollment']})"
    before = f"""BEGIN READ ONLY;
SELECT jsonb_build_object(
 'exact_current_prior',EXISTS({prior}),
 'own_work_ready',EXISTS(SELECT 1 FROM platform.runtime_work_item w WHERE w.id={q['work']}
  AND w.outbox_message_id={q['outbox']} AND w.state='leased' AND w.fence=1 AND w.attempt_count=1
  AND w.effect_receipt_id IS NULL AND w.lease_expires_at>clock_timestamp()),
 'no_prior_operation_receipts',NOT EXISTS(SELECT 1 FROM platform.runtime_command_receipt WHERE id={q['command']})
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_effect_receipt WHERE id={q['effect']})
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_inbox_receipt WHERE id={q['inbox']})
  AND NOT EXISTS(SELECT 1 FROM app.track_enrollment_receipt WHERE profile_id={q['customer']})
  AND NOT EXISTS(SELECT 1 FROM platform.runtime_attempt WHERE work_item_id={q['work']})
);
COMMIT;
"""
    after = f"""BEGIN READ ONLY;
SELECT jsonb_build_object(
 'exact_current_prior',EXISTS({prior}),
 'exact_worker_result_and_prior_transaction',EXISTS(
  SELECT 1 FROM app.track_enrollment_receipt r
  JOIN app.track_base_selection b ON b.id=r.selection_id
  JOIN app.track_subscriptions s ON s.id=b.subscription_id
  JOIN platform.runtime_effect_receipt e ON e.id=r.effect_receipt_id
  JOIN platform.runtime_command_receipt c ON c.id=e.command_receipt_id
  JOIN platform.runtime_inbox_receipt i ON i.effect_receipt_id=e.id
  JOIN platform.runtime_work_item w ON w.effect_receipt_id=e.id
  JOIN platform.runtime_outbox_message m ON m.id=w.outbox_message_id AND m.id=i.outbox_message_id
  JOIN platform.runtime_attempt a ON a.work_item_id=w.id
  WHERE r.id={q['enrollment']} AND r.user_id={q['user']} AND r.profile_id={q['customer']} AND r.track='customer'
   AND b.id={q['selection']} AND s.id={q['subscription']} AND r.selection_revision=b.revision AND b.revision=0
   AND r.result_code='already_enrolled' AND r.source_owner='customer_buyer_profile' AND r.source_creation_revision=0
   AND e.id={q['effect']} AND c.id={q['command']} AND i.id={q['inbox']} AND w.id={q['work']} AND m.id={q['outbox']}
   AND a.id={q['attempt']} AND a.worker_id={quote(worker_principal)} AND a.attempt_number=1 AND a.fence=1 AND a.result='committed'
   AND w.state='leased' AND w.fence=1 AND w.attempt_count=1 AND e.state='committed' AND e.fence=w.fence AND c.state='committed'
   AND c.owner_module_id='track_subscription_entitlement' AND e.owner_module_id=c.owner_module_id
   AND c.operation='assignDefaultFreeTrack.v1' AND e.operation=c.operation AND w.handler_name=c.operation
   AND i.handler_name=c.operation AND i.consumer_owner=c.owner_module_id
   AND c.subject_scope='CustomerProfile:'||{q['customer']} AND e.subject_scope=c.subject_scope
   AND w.semantic_work_key=r.semantic_key AND c.semantic_key=r.semantic_key AND e.semantic_effect_key=r.semantic_key
   AND r.fingerprint=m.payload_hash AND c.fingerprint=m.payload_hash AND e.fingerprint=m.payload_hash AND i.payload_hash=m.payload_hash
   AND c.result_body={expected_result} AND c.result_digest=e.result_hash
   AND c.result_schema_id={quote(RESULT_SCHEMA)} AND e.result_schema_id=c.result_schema_id
   AND c.mutation_transaction_id=r.mutation_transaction_id AND e.mutation_transaction_id=r.mutation_transaction_id
   AND i.mutation_transaction_id=r.mutation_transaction_id AND w.mutation_transaction_id=r.mutation_transaction_id
   AND a.mutation_transaction_id=r.mutation_transaction_id AND b.mutation_transaction_id=s.mutation_transaction_id
   AND r.mutation_transaction_id<>b.mutation_transaction_id)
);
COMMIT;
"""
    return before, after


def build(root):
    inputs = {name: pinned(root, name, digest) for name, digest in PINS.items()}
    worker = json.loads(inputs[f'{BASE}/fixtures.json'])
    source_receipt = json.loads(inputs[ACCEPTED_WORKER])
    candidate = json.loads(inputs[f'{CANDIDATE}/expected-catalog.json'])
    held_review = json.loads(inputs[f'{CANDIDATE}/independent-source-review.json'])
    parser = json.loads(inputs[TWO])['parser']
    parser_root = Path(pglast.__file__).resolve().parent
    parser_files = {path.relative_to(parser_root).as_posix(): sha(path.read_bytes())
                    for path in parser_root.rglob('*') if path.is_file() and path.suffix in ('.py', '.so')}
    need(pglast.__version__ == parser['version'] == 'v7.21' and parser_files == parser['files_sha256'], 'PARSER_DRIFT')
    need(source_receipt['actual_result'] == 'DERIVED_REVIEWED_WORKER17_FINITE_SQL_ASSERTIONS_ONLY'
         and held_review['decision'] == 'APPROVE_HELD_SOURCE_PREPARATION' and held_review['runtime'] == 'NOT_RUN'
         and held_review['operational_authority'] is False and candidate['expected_catalog_sha256'] == REQUIRED_CATALOG,
         'REVIEWED_SOURCE_ANCESTRY')
    worker_pins = {f'{BASE}/{leaf}': worker['prepared_files_sha256'][leaf] for leaf in WORKER_FILES}
    old = {leaf: pinned(root, f'{BASE}/{leaf}', worker_pins[f'{BASE}/{leaf}']).decode() for leaf in WORKER_FILES}
    files = {leaf: old[leaf] for leaf in ('identity-bootstrap.sql', 'complete-state-observe.sql')}
    origin = worker['roots']['B']
    ids = {key: origin['ids'][key] for key in ('work', 'attempt', 'command', 'effect', 'inbox', 'enrollment',
                                               'plan', 'subscription', 'selection')}
    source = origin['source']['ids']
    fixture = old['independent-fixtures.sql']
    [user] = [row for row in source_rows(fixture, 'app.users') if row['id'] == quote(source['user'])]
    [security] = [row for row in source_rows(fixture, 'app.user_security_profiles') if row['user_id'] == quote(source['user'])]
    [base_plan] = [row for row in source_rows(fixture, 'app.track_plans') if row['id'] == quote(ids['plan'])]
    original_process = worker['grants']['B-process']
    original_allowed = narrowed_fields(worker, ids, source, base_plan['version'].strip("'"), base_plan['content_hash'].strip("'"))
    need(original_allowed <= set(original_process['allowed_fields']), 'B42_RETAINED_PROCESS_GRANT_SUBSET')
    original_templates = {stage: worker['grants'][name] for stage, name in (
        ('source-customer', 'B-source_customer'), ('schedule', 'B-schedule'), ('claim', 'B-claim'), ('retained-effect', 'B-process'),
    )}
    users_and_plans, cases = [], {}
    case_ids = set()
    for case, provider in (('retained-free', 'none'), ('retained-paid-shape', 'manual')):
        material = json.dumps((ids, source, original_templates, old, user, security))
        mapping = {value: str(uuid.uuid5(uuid.NAMESPACE_URL, f'workinants/cloud-track-retained-v3/{case}/{value}'))
                   for value in set(UUID.findall(material))}

        def renamed(text):
            return UUID.sub(lambda match: mapping[match[0]], text)

        def structured(value):
            return json.loads(renamed(json.dumps(value)))

        current_ids, current_source = structured(ids), structured(source)
        tracked_ids = set(current_ids.values()) | set(current_source.values())
        need(not case_ids & tracked_ids and not tracked_ids & (set(ids.values()) | set(source.values())), 'CASE_ID_SCOPE')
        case_ids.update(tracked_ids)
        plan = structured(base_plan)
        if provider == 'manual':
            paid_fields = {
                'key': 'f0-retained-manual-shape', 'name': 'F0 synthetic paid-shaped Track plan',
                'billing_model': 'subscription', 'version': 'f0-retained-manual-shape.v1', 'currency': 'USD',
            }
            plan.update({key: quote(value) for key, value in paid_fields.items()})
            plan.update(monthly_price_cents='1', content_hash=quote(sha(wrapped_json(paid_fields))))
        users_and_plans.extend(named_sql(table, row) for table, row in (
            ('app.users', structured(user)), ('app.user_security_profiles', structured(security)), ('app.track_plans', plan),
        ))
        [sub] = source_rows(old['B-genuine-leased-group.sql'], 'app.track_subscriptions')
        [selection] = source_rows(old['B-genuine-leased-group.sql'], 'app.track_base_selection')
        sub = structured(sub)
        if provider == 'manual':
            sub.update(provider=quote(provider), current_period_start="clock_timestamp()-interval '5 minutes'",
                       current_period_end="clock_timestamp()+interval '30 minutes'")
        prior_fixture = closed_fixture(PRIOR_OWNERS, [named_sql('app.track_subscriptions', sub),
                                                       named_sql('app.track_base_selection', structured(selection))])
        validate_fixture(prior_fixture, PRIOR_OWNERS, {table: 1 for table in PRIOR_OWNERS})
        held_effect, expected = retained_body(renamed(old['B-genuine-leased-group.sql']), case)
        before, after = observations(current_ids, current_source, plan, provider, worker['service_principal'])
        grants = structured(original_templates)
        for stage, grant in grants.items():
            grant['template_id'] = case + '-' + stage
        plan_version, plan_digest = plan['version'].strip("'"), plan['content_hash'].strip("'")
        actual_allowed = narrowed_fields(worker, current_ids, current_source, plan_version, plan_digest)
        renamed_original = set(structured(sorted(original_allowed)))
        permitted_delta = {f'TrackPlan/{current_ids["plan"]}/version/{plan_version}',
                           f'TrackPlan/{current_ids["plan"]}/contentHash/{plan_digest}'}
        need(actual_allowed - renamed_original <= permitted_delta and len(actual_allowed) == len(original_allowed)
             and not any(field.startswith(('TrackSubscription/', 'TrackBaseSelection/')) and '/SELECT/' not in field
                         and '/revision/' not in field for field in actual_allowed), 'RETAINED_CAPABILITY_BROADENED')
        grants['retained-effect']['allowed_fields'] = actual_allowed
        for grant in grants.values():
            fields = grant['allowed_fields']
            need(len(fields) == len(set(fields)), 'REMAPPED_CAPABILITY_COLLISION')
            grant['allowed_fields'] = sorted(fields)
        cases[case] = {'provider_category': provider, 'externally_paid_proof': False, 'ids': current_ids,
                       'source_ids': {key: current_source[key] for key in ('CustomerProfile', 'user', 'free')},
                       'grants': grants, 'scope': 'FINITELY_OBSERVED_PRIOR_SELECTION_RETENTION_ONLY',
                       'expected_source_records': ['WA_CUSTOMER_CONTROL_READY_TO_COMMIT'],
                       'expected_schedule_records': ['WA_WORKER_SCHEDULE_READY'],
                       'expected_claim_records': ['WA_WR_BEFORE_B_CLAIM', {'changed': 1}, 'WA_WR_AFTER_B_CLAIM'],
                       'expected_retained_records': expected, 'stages': list(EXPECTED_STAGE_NAMES),
                       'expected_source_observation': origin['source']['observer_expected'],
                       'expected_before': {'exact_current_prior': True, 'own_work_ready': True, 'no_prior_operation_receipts': True},
                       'expected_after': {'exact_current_prior': True, 'exact_worker_result_and_prior_transaction': True},
                       'lease_claim_fence': 0, 'lease_effect_fence': 1, 'status': 'NOT_RUN'}
        files.update({f'{case}/{leaf}': body for leaf, body in (
            ('source-customer.sql', renamed(old['B-source-customer.sql'])),
            ('source-customer-observe.sql', renamed(old['B-source-customer-observe.sql'])),
            ('prior-selection-fixture.sql', prior_fixture), ('schedule.sql', renamed(old['B-schedule.sql'])),
            ('claim.sql', renamed(old['B-claim.sql'])), ('retained-effect.sql', held_effect),
            ('before-retained-observe.sql', before), ('after-retained-observe.sql', after),
        )})
    setup = closed_fixture(FIXTURE_OWNERS, users_and_plans)
    validate_fixture(setup, FIXTURE_OWNERS, dict.fromkeys(FIXTURE_OWNERS, 2))
    files['user-plan-fixtures.sql'] = setup
    files['restore-user-plan-owner-commits.sql'] = '\n'.join(['BEGIN;', *(f'ALTER TABLE {table} ENABLE TRIGGER owner_commit;'
                               for table in reversed(FIXTURE_OWNERS)), 'COMMIT;', ''])
    files['restore-prior-selection-owner-commits.sql'] = '\n'.join(['BEGIN;', *(f'ALTER TABLE {table} ENABLE TRIGGER owner_commit;'
                               for table in reversed(PRIOR_OWNERS)), 'COMMIT;', ''])
    for sql in files.values():
        need(bool(parse_sql(sql)), 'SQL_PARSE_REQUIRED')
    retained_row_delta = {table: count for (verb, table), count in EXPECTED_WRITES.items() if verb == 'INSERT'}
    retained_row_delta.update({'platform.database_action_grant': 1, 'platform.runtime_work_item': 0})
    manifest = {
        'schema': 'workinants.track-retained-base-held-business-recipes.v3', 'status': 'HELD_SOURCE_ONLY',
        'runtime': 'NOT_RUN', 'database_posture': 'D', 'assertion_promotions': 0,
        'database_execution_authorized': False, 'expected_catalog_sha256': REQUIRED_CATALOG,
        'ordered_migration_sha256': candidate['ordered_migration_sha256'], 'source_pins': {**PINS, **worker_pins},
        'parser': {'version': parser['version'], 'files_aggregate_sha256': parser['files_aggregate_sha256']},
        'service_principal': worker['service_principal'], 'cases': cases,
        'fixture_authority_pending': {'user_plan_owner_commit_tables': list(FIXTURE_OWNERS),
            'prior_selection_owner_commit_tables': list(PRIOR_OWNERS), 'requires_native_pre_and_post_parity': True},
        'retained_stage_changed_tables': sorted({table for _, table in EXPECTED_WRITES} | {'platform.database_action_grant'}),
        'retained_stage_exact_row_count_delta': retained_row_delta,
        'retained_stage_work_update_columns': ['effect_receipt_id', 'mutation_transaction_id'],
        'retained_stage_grants_history_and_usage_start_empty': True,
        'complete_state_observer_table_count': 42,
        'actor_authority_update_race': 'HELD_SOURCE8_INVOKER_BINDING_CANNOT_READ_LINKED_CUSTOMER_PROFILE_AND_TRACK_PLAN',
    }
    return {**{name: value.encode() for name, value in files.items()}, 'PROOF.json': wrapped_json(manifest)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--checkout', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    root = args.checkout.resolve(strict=True)
    files = build(root)
    here = Path(__file__).resolve().parent
    for name in ('README.md', 'test_grant_values.py'):
        files[name] = (here / name).read_bytes()
    files['MANIFEST.json'] = wrapped_json({
        'schema': 'workinants.track-retained-base-held-business-manifest.v1', 'runtime': 'NOT_RUN',
        'generator_sha256': sha(Path(__file__).read_bytes()), 'files_sha256': {name: sha(raw) for name, raw in files.items()},
    })
    os.umask(0o077)
    args.output.mkdir(mode=0o700)
    for name, raw in files.items():
        path = args.output / name
        path.parent.mkdir(mode=0o700, exist_ok=True)
        with path.open('xb') as handle:
            handle.write(raw)
    print(json.dumps({'runtime': 'NOT_RUN', 'files': len(files), 'manifest_sha256': sha(files['MANIFEST.json'])}))


if __name__ == '__main__':
    main()
