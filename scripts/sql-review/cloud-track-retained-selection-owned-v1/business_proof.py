"""Held two-case recipe validation and read-only state comparisons."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / 'recipe-v4' / 'packet'
MANIFEST_SHA = '642d361d24b0c87aee8a11539ade9e85795e40a0802a6a9c54f4c21182a88a26'
PROOF_SHA = '93aaad3108c339b1e8b3da64b6b32abe1f763da09b7a073e8f7df5197c6430a5'
REVIEW_SHA = 'b7047fcc4cb4de45d6e11d465069d083e2d68c4a08b28bf6554e68b5ba10db80'
GENERATOR_SHA = '7933b4d06496f3a9207e6f6fc4fb6f8d61b3c68463a2e078968ca6bc2f4b31a6'
CATALOG_SHA = '59a6a99a96748b72d8d639977c457857058777bf99346afb59804df926c107a9'
MIGRATION_SHA = (
    '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
    '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7',
    'ae7b94aae1689b54d6da0b9443b2512087018270774124f2b1d012f65f6ddcdb',
)
CASES = ('retained-free', 'retained-paid-shape')
STEPS = ('source-customer', 'prior-selection-fixture', 'schedule', 'claim', 'retained-effect')
CASE_LEAVES = set(STEPS) | {'source-customer-observe', 'before-retained-observe', 'after-retained-observe'}
SHARED_LEAVES = {'complete-state-observe', 'identity-bootstrap', 'user-plan-fixtures',
                 'restore-prior-selection-owner-commits', 'restore-user-plan-owner-commits'}
GRANT_TABLE = 'platform.database_action_grant'
WORK_TABLE = 'platform.runtime_work_item'
INSERTS = {'app.track_enrollment_receipt': 'enrollment', 'platform.runtime_attempt': 'attempt',
           'platform.runtime_command_receipt': 'command', 'platform.runtime_effect_receipt': 'effect',
           'platform.runtime_inbox_receipt': 'inbox'}
STAGE_DELTAS = {
    'user-plan-fixtures': {'app.users': 2, 'app.user_security_profiles': 2, 'app.track_plans': 2},
    'identity-bootstrap': {'platform_private.identity_service_authorization': 1, 'platform_private.identity_service_receipt': 1},
    'source-customer': {'app.customer_profiles': 1, 'app.customer_profile_lifecycle_event': 1,
                        'platform.owner_mutation_evidence': 1, 'platform.runtime_command_receipt': 1,
                        'platform.runtime_outbox_message': 2, GRANT_TABLE: 1},
    'prior-selection-fixture': {'app.track_base_selection': 1, 'app.track_subscriptions': 1},
    'schedule': {WORK_TABLE: 1, GRANT_TABLE: 1},
    'claim': {WORK_TABLE: 0, GRANT_TABLE: 1},
    'retained-effect': {**dict.fromkeys(INSERTS, 1), GRANT_TABLE: 1, WORK_TABLE: 0},
}
ROLE_GRANTS = {'source-customer': ('wa_app_runtime', 'SH-004.v1', 179),
               'schedule': ('wa_app_runtime', 'runtime.schedule_work.v1', 25),
               'claim': ('wa_worker', 'runtime.claim_work.v1', 21),
               'retained-effect': ('wa_worker', 'assignDefaultFreeTrack.v1', 181)}
PREEXISTING_EMPTY = ('app.track_entitlement_grants', 'app.track_subscription_events', 'app.track_usage_counters',
                     'app.track_usage_events', 'app.track_usage_reservation')
PROFILE_SOURCES = {
    'scripts/sql-review/cloud-track-retained-base-v1/operation.py': 'fa2b211aed19cd5f4fc30b7172f9b581b25504f3dedcfcea9a8a68a2362f78ef',
    'scripts/sql-review/cloud-app-source8-v1/app_child.py': '5f3a616745ba26ad6baae8266bbb254b4d791510289a1ba290bb30002fc5acfc',
    'scripts/sql-review/cloud-app-source8-v1/host_session.py': '0149b82add667b485a2d6e044ee252f5f30add8db8ea87df9147cf9181fe3757',
    'scripts/sql-review/run-scoped-read-companion-rehearsal.py': '4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15',
    'scripts/sql-review/run-worker-recovery-control-rehearsal.py': 'eff0342fd3dfb3768c5dd7809635b5d38db330512bde3aca7ccb5b5d2aee216c',
    'scripts/worker_recovery_control_protocol.py': '2ef788f124adaa248ba01bd0bad852cbc113ad2d0e9cd1fc942d4f6d35d6ceb1',
    'scripts/sql-review/collect_native_catalog.sql': '9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f',
}
HASH = re.compile('[0-9a-f]{64}')
XID = re.compile('[1-9][0-9]{0,19}')
DATABASE = 'wa_p0c_rehearsal'


class Held(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def need(value, code):
    if not value:
        raise Held(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def exact(value, expected, code):
    need(canonical(value) == canonical(expected), code)


def unique_json(raw):
    def pairs(entries):
        value = dict(entries)
        need(len(value) == len(entries), 'TRACK_DUPLICATE_JSON_FIELD')
        return value

    def refuse(_text):
        raise Held('TRACK_JSON_INTEGER_OR_BOOLEAN_REQUIRED')

    need(type(raw) in (str, bytes) and 0 < len(raw) <= 8 * 1024 * 1024, 'TRACK_JSON_BOUND')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=refuse, parse_float=refuse)


def path_hash(path, digest):
    need(path.resolve(strict=True) == path and path.is_file() and path.stat().st_nlink == 1, 'TRACK_SOURCE_REGULAR_FILE')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        need(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1 and opened.st_size <= 8 * 1024 * 1024,
             'TRACK_SOURCE_OPENED_FILE')
        raw = stream.read(opened.st_size + 1)
        closed = os.fstat(stream.fileno())
    need((opened.st_dev, opened.st_ino, opened.st_size, opened.st_ctime_ns)
         == (closed.st_dev, closed.st_ino, closed.st_size, closed.st_ctime_ns)
         and len(raw) == opened.st_size and sha(raw) == digest, 'TRACK_SOURCE_DIGEST')
    return raw


def canonical_uuid(value):
    try:
        return type(value) is str and str(uuid.UUID(value)) == value
    except ValueError:
        return False


def load(root=ROOT, packet=PACKET):
    """Return verified source bytes. Source review carries no dispatch authority."""
    from pglast import __version__, ast, parse_sql

    manifest = unique_json(path_hash(packet / 'MANIFEST.json', MANIFEST_SHA))
    spec = unique_json(path_hash(packet / 'PROOF.json', PROOF_SHA))
    review = unique_json(path_hash(packet.parent / 'independent-source-review.json', REVIEW_SHA))
    need(review['decision'] == 'APPROVE_HELD_SOURCE_PREPARATION' and review['reviewer'] != review['source_author']
         and review['runtime'] == 'NOT_RUN' and review['operational_authority'] is False
         and review['packet_manifest_sha256'] == MANIFEST_SHA and review['packet_proof_sha256'] == PROOF_SHA
         and review['generator_sha256'] == manifest['generator_sha256'] == GENERATOR_SHA
         and review['expected_effective_catalog_sha256'] == spec['expected_catalog_sha256'] == CATALOG_SHA
         and review['assertion_promotions'] == spec['assertion_promotions'] == 0
         and spec['status'] == 'HELD_SOURCE_ONLY' and spec['database_execution_authorized'] is False
         and tuple(spec['ordered_migration_sha256']) == MIGRATION_SHA and __version__ == spec['parser']['version'] == 'v7.21',
         'TRACK_EXACT_HELD_SOURCE_REVIEW')
    path_hash(packet.parent / 'prepare.py', GENERATOR_SHA)
    sql_names = {f'{name}.sql' for name in SHARED_LEAVES} | {f'{case}/{name}.sql' for case in CASES for name in CASE_LEAVES}
    pins = manifest['files_sha256']
    need(set(pins) == sql_names | {'README.md', 'PROOF.json', 'test_grant_values.py'} and len(pins) == 24
         and not any(path.is_symlink() for path in packet.rglob('*'))
         and {path.relative_to(packet).as_posix() for path in packet.rglob('*') if path.is_file()} == set(pins) | {'MANIFEST.json'},
         'TRACK_EXACT_RECIPE_TREE')
    files = {name: path_hash(packet / name, digest) for name, digest in pins.items()}
    sources = {name: path_hash(root / name, digest) for name, digest in {**spec['source_pins'], **PROFILE_SOURCES}.items()}
    parsed = {name: parse_sql(files[name].decode()) for name in sql_names}
    native = unique_json(sources['review-output/track-retained-base-candidate-v1/expected-catalog.json'])
    tables = frozenset(native['expected']['tables'])
    select, = parsed['complete-state-observe.sql']
    expression = select.stmt.targetList[0].val
    need(isinstance(expression, ast.FuncCall) and expression.funcname[0].sval == 'jsonb_build_object'
         and len(tables) == len(expression.args[::2]) == 42
         and {key.val.sval for key in expression.args[::2]} == tables, 'TRACK_FULL42_SOURCE_TABLES')
    need(set(spec['cases']) == set(CASES) and spec['retained_stage_exact_row_count_delta'] == STAGE_DELTAS['retained-effect']
         and spec['retained_stage_work_update_columns'] == ['effect_receipt_id', 'mutation_transaction_id'],
         'TRACK_EFFECT_ALLOWLIST_SOURCE')
    all_case_ids = []
    for case in CASES:
        item = spec['cases'][case]
        need(tuple(item['stages']) == STEPS and set(item['grants']) == set(ROLE_GRANTS)
             and item['provider_category'] == ('none' if case == CASES[0] else 'manual')
             and item['externally_paid_proof'] is False, 'TRACK_EXACT_TWO_CASES')
        all_case_ids.extend(item['ids'].values())
        all_case_ids.extend(item['source_ids'].values())
        for step, wanted in ROLE_GRANTS.items():
            grant = item['grants'][step]
            fields = grant['allowed_fields']
            need((grant['database_login_role'], grant['action'], len(fields)) == wanted
                 and fields == sorted(set(fields)) and all(type(field) is str and '*' not in field for field in fields),
                 'TRACK_EXACT_GRANT_TEMPLATE')
    need(len(all_case_ids) == len(set(all_case_ids)) and all(canonical_uuid(value) for value in all_case_ids), 'TRACK_DISJOINT_IDS')
    return spec, files, sources, tables


def final_counts(tables):
    result = Counter(dict.fromkeys(tables, 0))
    for step, delta in STAGE_DELTAS.items():
        for table, change in delta.items():
            result[table] += change * (2 if step in STEPS else 1)
    return dict(result)


def count_hash(row):
    need(type(row) is dict and set(row) == {'count', 'rows_sha256'} and type(row['count']) is int
         and 0 <= row['count'] <= 64 and type(row['rows_sha256']) is str and HASH.fullmatch(row['rows_sha256']),
         'TRACK_STRICT_COUNT_HASH')
    return row


def full_state(value, tables):
    need(type(value) is dict and set(value) == set(tables) and len(value) == 42, 'TRACK_EXACT_FULL42_SCHEMA')
    return {table: count_hash(row) for table, row in value.items()}


def state_delta(before, after, tables, step):
    full_state(before, tables)
    full_state(after, tables)
    delta = STAGE_DELTAS[step]
    need(all(after[table]['count'] == before[table]['count'] + delta.get(table, 0)
             and (after[table]['rows_sha256'] != before[table]['rows_sha256'] if table in delta else after[table] == before[table])
             for table in tables), 'TRACK_UNDECLARED_FULL42_DELTA')


def read_only(sql):
    return 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n' + sql.rstrip() + '\nROLLBACK;\n'


def projection_sql(case, grant_id, holder_hash, captured_xid):
    """Build an observer where substituted values have closed types and fixed SQL roles."""
    ids = case['ids']
    need(all(canonical_uuid(ids[key]) for key in ('work', *INSERTS.values()))
         and (grant_id is None or canonical_uuid(grant_id))
         and type(holder_hash) is str and HASH.fullmatch(holder_hash)
         and type(captured_xid) is str and XID.fullmatch(captured_xid), 'TRACK_OBSERVER_BIND_TYPES')
    selected = {table: f"'{ids[key]}'::uuid" for table, key in INSERTS.items()}
    selected[GRANT_TABLE] = 'NULL::uuid' if grant_id is None else f"'{grant_id}'::uuid"

    def rows(table, without):
        return ("(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to("
                "coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text COLLATE \"C\"),'[]'::jsonb)::text,"
                f"'UTF8')),'hex')) FROM {table} t WHERE t.id IS DISTINCT FROM {without})")

    inserts = ','.join(f"'{table}',jsonb_build_object('own_count',(SELECT count(*) FROM {table} WHERE id={target}),"
                       f"'unaffected',{rows(table, target)})" for table, target in sorted(selected.items()))
    work = f"'{ids['work']}'::uuid"
    sql = f"""SELECT jsonb_build_object('database',current_database(),'login',session_user,'effective_login',current_user,
 'read_only',current_setting('transaction_read_only')='on','server_version_num',current_setting('server_version_num')::int,
 'work',(SELECT jsonb_build_object('id',w.id,'state',w.state,'fence',w.fence,'attempt_count',w.attempt_count,
   'effect_pointer',w.effect_receipt_id,'exact_live_lease',coalesce(w.lease_expires_at>clock_timestamp() AND w.lease_token_hash='{holder_hash}',false),
   'exact_transaction',w.mutation_transaction_id='{captured_xid}',
   'stable_sha256',encode(sha256(convert_to((to_jsonb(w)-ARRAY['effect_receipt_id','mutation_transaction_id'])::text,'UTF8')),'hex'))
   FROM {WORK_TABLE} w WHERE w.id={work}),
 'other_work',{rows(WORK_TABLE, work)},'inserts',jsonb_build_object({inserts}));"""
    return read_only(sql)


def validate_projection(data, case, *, after):
    header = {'database': DATABASE, 'login': 'postgres', 'effective_login': 'postgres', 'read_only': True, 'server_version_num': 170011}
    need(type(data) is dict and set(data) == {*header, 'work', 'other_work', 'inserts'}, 'TRACK_OBSERVER_FIELDS')
    exact({key: data[key] for key in header}, header, 'TRACK_OBSERVER_DATABASE_CONTEXT')
    work = data['work']
    wanted = {'id': case['ids']['work'], 'state': 'leased', 'fence': 1, 'attempt_count': 1,
              'effect_pointer': case['ids']['effect'] if after else None, 'exact_live_lease': True, 'exact_transaction': True}
    need(type(work) is dict and set(work) == {*wanted, 'stable_sha256'} and type(work['stable_sha256']) is str
         and HASH.fullmatch(work['stable_sha256']), 'TRACK_EXACT_WORK_PROJECTION')
    exact({key: work[key] for key in wanted}, wanted, 'TRACK_EXACT_WORK_RECEIPT')
    count_hash(data['other_work'])
    need(type(data['inserts']) is dict and set(data['inserts']) == {*INSERTS, GRANT_TABLE}, 'TRACK_EXACT_INSERT_TABLES')
    for row in data['inserts'].values():
        need(type(row) is dict and set(row) == {'own_count', 'unaffected'} and type(row['own_count']) is int
             and row['own_count'] == (1 if after else 0), 'TRACK_EXACT_ONE_INSERT_ID')
        count_hash(row['unaffected'])
    return data


def effect_pair(case, before, after, before_state, after_state, tables):
    state_delta(before_state, after_state, tables, 'retained-effect')
    validate_projection(before, case, after=False)
    validate_projection(after, case, after=True)
    need(before['work']['stable_sha256'] == after['work']['stable_sha256'] and before['other_work'] == after['other_work']
         and before['other_work']['count'] + 1 == before_state[WORK_TABLE]['count'], 'TRACK_UNDECLARED_WORK_FIELD_OR_ROW_DRIFT')
    for table in before['inserts']:
        original = before['inserts'][table]['unaffected']
        need(original == after['inserts'][table]['unaffected'] == before_state[table]
             and original['count'] + 1 == after_state[table]['count'], 'TRACK_UNDECLARED_EXISTING_ROW_DRIFT')
    need(all(before_state[table]['count'] == after_state[table]['count'] == 0 for table in PREEXISTING_EMPTY),
         'TRACK_EMPTY_GRANT_HISTORY_USAGE_REQUIRED')
    return {'other_35_tables_unchanged': True, 'only_declared_work_row_fields_changed': True,
            'six_exact_insert_ids_and_existing_rows_preserved': True}
