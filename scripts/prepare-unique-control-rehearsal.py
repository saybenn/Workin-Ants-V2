"""Prepare five finite races for existing P0C-UNIQUE-01. No process execution.

Complete registered SH004 source groups only. This proposes a coordinator
protocol; its transport/credential/target wrapper still requires separate review.
No Customer UPDATE/CAS codec, worker loop or owner-generation port is invented.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review-output/unique-control-rehearsal'
NS = uuid.UUID('b9cf5d07-b1b7-4abc-8944-bd1924266eb6')
CONTROL = 'P0C-UNIQUE-01'
ACL = 'context/reconciliation/foundation-sql-draft-access.json'
CONSTRAINT = 'runtime_command_receipt_owner_module_id_operation_subject_s_key'
GATE = 'CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED'
INPUTS = ('scripts/prepare-unique-control-rehearsal.py', 'scripts/check-unique-control-rehearsal.py',
          'scripts/unique_control_protocol.py', 'scripts/prepare-customer-control-rehearsal.py', 'scripts/contract_schema.py',
          ACL, 'context/reconciliation/database-candidate-tests.json', 'context/reconciliation/local-f0-assertions.json',
          'context/reconciliation/database-candidate-corrections-first-replay-selection.json',
          'context/reconciliation/foundation-sql-scope-policy.json', 'review-output/foundation-application.review.sql',
          'review-output/foundation-structure.sql', 'scripts/sql-review/foundation-invariants.sql',
          'contracts/shared/SH-004.v1.schema.json', 'contracts/shared/types.v1.schema.json',
          'contracts/database-review/foundation-payloads.v1.schema.json', 'contracts/database-review/owner-mutation-evidence.v1.schema.json',
          'context/shared/contracts/SH-004.md',
          'context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md',
          'context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-implementation-plan.md')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def uid(value): return str(uuid.uuid5(NS, value))
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'))


def helper(root):
    spec = importlib.util.spec_from_file_location('unique_customer_fixture_source', root / 'scripts/prepare-customer-control-rehearsal.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def replace_all(value, substitutions):
    if type(value) is str:
        for old, new in substitutions.items(): value = value.replace(old, new)
        return value
    if type(value) is dict: return {key: replace_all(item, substitutions) for key, item in value.items()}
    if type(value) is list: return [replace_all(item, substitutions) for item in value]
    return value


def build(root=ROOT, expected_sha256=None):
    root = Path(root); fingerprints = {path: sha((root / path).read_bytes()) for path in INPUTS}
    if expected_sha256 is not None and expected_sha256 != fingerprints: raise ValueError('reviewed source pins differ before helper import')
    cm = helper(root); acl = json.loads((root / ACL).read_bytes()); registry = cm.FixtureRegistry(root)
    for path in ('contracts/database-review/foundation-payloads.v1.schema.json', 'contracts/database-review/owner-mutation-evidence.v1.schema.json'):
        doc = json.loads((root / path).read_bytes()); registry.documents[doc['$id']] = doc
    register = json.loads((root / 'context/reconciliation/database-candidate-tests.json').read_bytes())['tests']
    inventory = json.loads((root / 'context/reconciliation/local-f0-assertions.json').read_bytes())
    selection = json.loads((root / 'context/reconciliation/database-candidate-corrections-first-replay-selection.json').read_bytes())['first_p0c_replay']['ids']
    if CONTROL not in selection or len(selection) != 94: raise ValueError('exact selected94 UNIQUE identity missing')
    source_control = next(row for row in register if row['id'] == CONTROL)
    assertions = next(row['assertions'] for row in inventory['cases'] if row['id'] == CONTROL)
    if [row['id'] for row in assertions] != ['control.same_semantic_identity', 'control.changed_fingerprint', 'control.different_scope']:
        raise ValueError('UNIQUE assertion inventory changed')
    schema = json.loads((root / 'contracts/shared/SH-004.v1.schema.json').read_bytes())
    if schema['$defs']['request']['properties']['input']['properties']['purpose']['enum'] != ['resolve', 'provision']:
        raise ValueError('SH004 purpose changed')
    application = (root / 'review-output/foundation-application.review.sql').read_text(encoding='utf8')
    if CONSTRAINT not in (root / 'review-output/foundation-structure.sql').read_text(encoding='utf8'):
        raise ValueError('exact source native semantic constraint unavailable')
    files, races, users = {}, [], set()
    definitions = [('same-fingerprint-holder-commit', False, 'COMMIT', False),
                   ('same-fingerprint-holder-rollback', False, 'ROLLBACK', False),
                   ('changed-fingerprint-holder-commit', True, 'COMMIT', False),
                   ('changed-fingerprint-holder-rollback', True, 'ROLLBACK', False),
                   ('different-subjects-identical-text-key', False, 'COMMIT', True)]
    for name, changed, outcome, different in definitions:
        semantic = 'unique-control-' + name
        participants = {}
        for side in ('A', 'B'):
            case, text, observer = cm.create_case('unique-race-' + name + '-' + side.lower(), 'valid', acl, registry, semantic=semantic)
            case['control_ids'] = [CONTROL]
            if side == 'B' and not different:
                first = participants['A']['source_case']
                changes = {case['ids']['CustomerProfile']: first['ids']['CustomerProfile'], case['ids']['user']: first['ids']['user']}
                case, text, observer = [replace_all(value, changes) for value in (case, text, observer)]
            if side == 'B' and changed:
                old = case['fixture_values']['response']['value']['receipt']['fingerprint']
                changes = {old: sha(('different synthetic SQL-only intent:' + semantic).encode())}
                case, text, observer = [replace_all(value, changes) for value in (case, text, observer)]
            if registry.check('SH-004', 'response', case['fixture_values']['response']): raise ValueError('closed registered SH004 result invalid')
            # Existing valid helper has one command INSERT first and one terminal
            # COMMIT. No string split of arbitrary user SQL is accepted.
            lines = text.splitlines()
            if not lines[0].startswith('INSERT INTO platform.runtime_command_receipt ') or lines[-1] != 'COMMIT;' or lines.count("SELECT 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT';") != 1:
                raise ValueError('reviewed Customer source transaction shape changed')
            before = 'WA_UNIQUE_' + side + '_BEFORE_COMMAND'; after = 'WA_UNIQUE_' + side + '_AFTER_COMMAND'; ready = 'WA_UNIQUE_' + side + '_GROUP_READY'
            command = "SELECT " + quote(before) + ';\n' + lines[0] + '\nSELECT ' + quote(after) + ';\n'
            remainder = '\n'.join(line for line in lines[1:-1] if line != "SELECT 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT';") + '\nSET CONSTRAINTS ALL IMMEDIATE;\nSELECT ' + quote(ready) + ';\n'
            prefix = name + '-' + side.lower()
            for suffix, sql in (('command', command), ('remainder', remainder), ('hold-ready', command + remainder), ('observe', observer)):
                files[prefix + '-' + suffix + '.sql'] = sql
            case['transaction_sql'] = prefix + '-hold-ready.sql'; case['observer_sql'] = prefix + '-observe.sql'
            participants[side] = {'actual_login': 'wa_app_runtime', 'status': 'NOT_RUN', 'source_case': case,
                                  'command_sql': prefix + '-command.sql', 'remainder_sql': prefix + '-remainder.sql',
                                  'hold_ready_sql': prefix + '-hold-ready.sql', 'observer_sql': prefix + '-observe.sql',
                                  'markers': {'before_command': before, 'after_command': after, 'group_ready': ready}}
            users.add(case['ids']['user'])
        a, b = [participants[side]['source_case'] for side in ('A', 'B')]
        roots = sorted({a['ids']['CustomerProfile'], b['ids']['CustomerProfile']}); commands = [a['ids']['RuntimeCommandReceipt'], b['ids']['RuntimeCommandReceipt']]
        winner = 'B' if outcome == 'ROLLBACK' else 'BOTH' if different else 'A'
        count = 2 if different else 1
        condition = lambda values: ','.join(quote(value) for value in values)
        observer = "SELECT jsonb_build_object('customers',(SELECT count(*) FROM app.customer_profiles WHERE id IN (" + condition(roots) + ")),'commands',(SELECT count(*) FROM platform.runtime_command_receipt WHERE id IN (" + condition(commands) + ")),'history',(SELECT count(*) FROM app.customer_profile_lifecycle_event WHERE customer_profile_id IN (" + condition(roots) + ")),'evidence',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile' AND aggregate_id IN (" + condition(roots) + ")),'outbox',(SELECT count(*) FROM platform.runtime_outbox_message WHERE aggregate_kind='CustomerProfile' AND aggregate_id IN (" + condition(roots) + ")),'effects',(SELECT count(*) FROM platform.runtime_effect_receipt WHERE command_receipt_id IN (" + condition(commands) + ")),'track_enrollments',(SELECT count(*) FROM app.track_enrollment_receipt WHERE profile_id IN (" + condition(roots) + ")));\n"
        files[name + '-complete-observe.sql'] = observer
        # Full semantic UNIQUE identity is owner/operation/subject/key. UUIDs and
        # source bodies stay in prepared fixtures, never runtime handles/evidence.
        target_assertion = 'control.different_scope' if different else 'control.changed_fingerprint' if changed else 'control.same_semantic_identity'
        races.append({'name': name, 'control_id': CONTROL, 'assertion_id': target_assertion, 'status': 'NOT_RUN',
            'runtime_eligibility': 'PROPOSED_FINITE_PROTOCOL_REQUIRES_INDEPENDENT_COORDINATOR_AND_TARGET_REVIEW',
            'execution_dependencies': ['FRESH_DISJOINT_SYNTHETIC_NAMESPACE', 'EXACT_SOURCE_NATIVE_CATALOG_AUTH_FINALIZATION_PASS', 'FIXTURE_TRIGGER_RESTORATION', 'REVIEWED_ACTUAL_APP_ISSUER_SESSION_TRANSPORT', 'REVIEWED_FIXED_BARRIER_OBSERVER_AND_DIAGNOSTIC_PARSER'],
            'participants': participants, 'different_subject_scope': different, 'changed_fingerprint': changed,
            'holder_outcome': outcome, 'expected_winner': winner, 'semantic_key': semantic,
            'observer_sql': name + '-complete-observe.sql', 'observer_expected': {'customers': count, 'commands': count, 'history': count, 'evidence': count, 'outbox': 2 * count, 'effects': 0, 'track_enrollments': 0},
            'required_coherent_participants': ['A', 'B'] if different else [winner],
            'native_duplicate_diagnostic': None if different or outcome == 'ROLLBACK' else {'sqlstate': '23505', 'exact_message': 'duplicate key value violates unique constraint "' + CONSTRAINT + '"', 'schema': 'platform', 'table': 'runtime_command_receipt', 'constraint': CONSTRAINT, 'native_routine': '_bt_check_unique', 'native_file': 'nbtinsert.c', 'detail_expected': 'ABSENT_RLS_ENABLED', 'row_security_enabled_required': True, 'required_psql_exit': 3, 'acknowledgement': False, 'expected_completed_markers': [participants['B']['markers']['before_command']], 'forbidden_markers': [participants['B']['markers']['after_command'], participants['B']['markers']['group_ready']]},
            'barrier': {'required': not different, 'holder_complete_group_constraints_checked_before_B': True, 'B_before_command_marker_required': True,
                        'observer_binding': 'Same actual A/B PID+backend_start+login+database tuples captured before work; distinct connections/full xids; fixed pg_stat_activity/pg_blocking_pids observation is synchronization, not post-rollback business evidence.',
                        'expected': {'A_idle_in_transaction': True, 'B_active': True, 'B_wait_event_type_lock': True, 'B_wait_event_transactionid': True, 'B_blocked_only_by_A': True},
                        'limits': {'max_observations': 40, 'deadline_seconds': 2, 'lock_timeout_seconds': 5, 'statement_timeout_seconds': 10, 'idle_transaction_timeout_seconds': 30},
                        'sql_builder': 'scripts/unique_control_protocol.py#barrier_sql',
                        'no_sleep_sql': True, 'unobserved_overlap_disposition': 'STOP_NOT_CONCURRENCY_PASS'},
            'limits': ['Native storage uniqueness is not an application idempotency replay/conflict response.', 'Fingerprint values are a declared synthetic SQL fixture convention; no owner request canonicalization is qualified.', 'No Customer UPDATE/CAS, worker claim/enrollment loop, appAttempt/Inbox, usage, Privacy or owner-generation transition.']})
    seed = ['-- TRUSTED synthetic Identity prerequisites only; no Identity owner mutation proof.', 'BEGIN;',
            'ALTER TABLE app.users DISABLE TRIGGER owner_commit;', 'ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;']
    for user in sorted(users):
        seed += [cm.insert('app.users', {'id': quote(user), 'is_public': 'false', 'revision': '0', 'privacy_generation': '0', 'created_at': 'clock_timestamp()', 'updated_at': 'clock_timestamp()'}),
                 cm.insert('app.user_security_profiles', {'id': quote(uid(user + '/security')), 'user_id': quote(user), 'revision': '0', 'security_generation': '0', 'created_at': 'clock_timestamp()', 'updated_at': 'clock_timestamp()'})]
    seed += ['ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;', 'ALTER TABLE app.users ENABLE TRIGGER owner_commit;', 'COMMIT;']
    files['trusted-identity-fixtures.sql'] = '\n'.join(seed) + '\n'
    triggers, restoration = cm.fixture_trigger_restoration(application); files['fixture-trigger-restore-observe.sql'] = restoration
    files['commit.sql'] = 'COMMIT;\n'; files['rollback.sql'] = 'ROLLBACK;\n'
    matrix = []
    for case in inventory['cases']:
        for assertion in case['assertions']:
            if case['id'] == CONTROL:
                disposition, dependencies = 'SOURCE_PREPARED_FIVE_FINITE_RACES_NOT_RUN', []
            elif case['id'] == 'P0C-CAS-01':
                disposition = 'BLOCKED_MISSING_COMPLETE_OWNER_RESULT' if assertion['availability'] != 'DEPENDENCY_BLOCKED' else 'BLOCKED_REGISTERED_DEPENDENCY'
                dependencies = assertion['dependency_ids'] or [GATE]
            elif case['id'] == 'P0C-TRACK-01' and (assertion['id'] == 'control.concurrent_fence' or assertion['id'].startswith(('vector.LEASE-RENEW.', 'vector.LEASE-RECOVERY.'))):
                disposition, dependencies = 'SOURCE_PREPARABLE_SEPARATE_LEASE_PACKET_REQUIRED_NOT_RUN', ['SEPARATELY_REVIEWED_EXPIRY_RECLAIM_CURRENT_HOLDER_EFFECT_PROTOCOL']
            elif case['id'] == 'P0C-CTX-02' and assertion['id'] == 'control.revocation_schedule':
                disposition, dependencies = 'APP_REVOCATION_COMPONENT_SOURCE_PREPARABLE_NOT_INCLUDED', ['SEPARATE_ACTUAL_APP_REVOKE_COMMIT_BEFORE_ACTION_PROTOCOL']
            else: continue
            matrix.append({'case_id': case['id'], 'assertion_id': assertion['id'], 'expected_assertion': assertion['expected_assertion'], 'expected_assertion_sha256': sha(assertion['expected_assertion'].encode()), 'source_availability': assertion['availability'], 'status': 'NOT_RUN', 'disposition': disposition, 'execution_dependencies': dependencies})
    manifest = {'schema': 'workinants.unique-control-fixtures.v1', 'status': 'NOT_RUN', 'database_posture': 'D', 'database_contacted': False, 'sql_executed': False,
        'selected_control_ids': [CONTROL], 'source_control_definition': source_control, 'source_assertion_definitions': assertions,
        'source_files_sha256': fingerprints, 'races': races, 'remaining_concurrency_matrix': matrix,
        'finite_caps': {'races': 5, 'actual_app_connections': 10, 'committed_customer_groups': 6, 'rolled_back_holder_groups': 2, 'expected_native_duplicate_failures': 2,
                        'identity_fixture_users': len(users), 'issuer_grants': 10, 'worker_operations': 0, 'app_attempt_inbox_operations': 0, 'production_worker_loop': False},
        'namespace_policy': {'fresh_only': True, 'reuse': 'BLOCKED_WITHOUT_SEPARATE_EXACT_RETAINED_STATE_REVIEW', 'all_participant_source_ids_absent_before_setup': True, 'users': sorted(users), 'security_profiles': [uid(user + '/security') for user in sorted(users)]},
        'fixture_trigger_contract': {'status': 'NOT_RUN', 'bypassed': ['app.users/owner_commit', 'app.user_security_profiles/owner_commit'], 'physical_guards_retained': True, 'expected_user_triggers': triggers, 'observer_sql': 'fixture-trigger-restore-observe.sql'},
        'runtime_contract': ['This packet proposes a finite coordinator protocol; no real transport/target wrapper is provided or approved.',
            'Actual separately authenticated wa_app_runtime A/B, READ COMMITTED, exact current_user/session_user/database; capture distinct PID/backend_start/full xid before any protected work.',
            'Each actual issuer commits a fresh secret hash/immutable tuple/finite capability row independently and closes before its app binds; no SET ROLE or self-written grant.',
            'A runs complete registered source/history/command/evidence/exact-message group and SET CONSTRAINTS ALL IMMEDIATE, then stops at GROUP_READY without ending its transaction.',
            'B emits BEFORE_COMMAND then sends only its command INSERT and AFTER_COMMAND. Observe exact native transactionid wait on A before ending A. No timeout/sleep/error is substituted for overlap.',
            'Commit-race: end A with COMMIT and confirm its closure; B must exit3 with exact native23505/table/schema/constraint diagnostic and only BEFORE marker. No body tail runs.',
            'Rollback-race: full ROLLBACK A and confirm closure; B must acknowledge its command+AFTER marker, then complete remainder/SET CONSTRAINTS/GROUP_READY/COMMIT and close.',
            'Distinct-scope: both complete source groups reach GROUP_READY before either COMMIT; both COMMIT/close. Identical text key is allowed only because exact subject scopes differ.',
            'Any unexpected marker, SQLSTATE/native location/constraint, wait schedule, count, currentness, acknowledgment or closure stops later races. Finally close/rollback all live operation connections, then observe exact complete state/coherence and trigger restoration.',
            'Each winning source/command/history/evidence/outbox mutation xid must equal that winner actual captured full xid; compare in memory and retain only winner_transaction_ids_match. A coherent group from a different backend/transaction does not qualify.',
            'Keep secrets/hashes/raw runtime UUID handles/PIDs/xids/backend_start/statement bodies/diagnostic detail out of evidence. Retain only known source identifiers, typed comparisons/counts, stages, hashes, exits and bounded failure codes incrementally.',
            'All source controls/assertions remain NOT_RUN until real independently reviewed execution evidence. Partial components cannot promote compound CAS/Track/CTX cases.'],
        'external_authority_limit': 'No DB/Docker/SQL/Prisma/Git/provider execution, permission/schema edits or hosted operation authorized by this preparation.'}
    files['README.md'] = '''# Proposed finite UNIQUE races

Source-only, NOT_RUN. Exact existing P0C-UNIQUE-01 only, with the existing closed
SH004 result and complete Customer group. Five finite schedules: identical and
changed fingerprint collisions with holder COMMIT or ROLLBACK; identical text key
under two separate legitimate Customer subjects where both complete groups commit.
The privileged wait observer proves actual overlapping transactions; a timeout or
sequential duplicate is not concurrency evidence. No protected row is privileged-seeded.

Native23505 proves only storage uniqueness. It is never a production idempotency
API response. Existing Customer UPDATE/CAS missing result codecs, owner-generation
ports, usage/Privacy and worker-loop paths remain held. The concurrency matrix
distinguishes missing owner contracts from separately preparable lease/revoke work.

Only two exact owner_commit triggers are bypassed for synthetic Identity facts;
all physical guards remain. Exact trigger restoration and complete native parity
are required before any actual restricted operation. A separate reviewed target,
authentication, transport/diagnostic/barrier wrapper and cleanup remain mandatory.

Native diagnostic and wait SQL builders are source-only helpers in the proposed
protocol. PG17.11 BuildIndexValueDescription suppresses key DETAIL when RLS is
enabled; this actual restricted app path therefore expects no key-value DETAIL.
The native B-tree unique error still identifies the exact schema/table/index.
Primary source: https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/access/index/genam.c
and https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/access/nbtree/nbtinsert.c

Plain English: Two real keys try to save the same ticket at once. We first prove
one is waiting for the other. Keeping the first ticket blocks a duplicate; tearing
it up lets the waiting ticket finish. Different customers may use the same words.
'''
    manifest['prepared_files_sha256'] = {name: sha(text.encode()) for name, text in files.items()}
    manifest['source_only_packet_sha256'] = sha(canonical({key: manifest[key] for key in ('source_files_sha256', 'prepared_files_sha256')}).encode())
    manifest['packet_digest_recipe'] = "SHA256(UTF8 canonical sorted compact JSON of source_files_sha256 and prepared_files_sha256); fixtures.json excluded"
    files['fixtures.json'] = json.dumps(manifest, indent=2) + '\n'
    return files, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--prepare', action='store_true'); args = parser.parse_args()
    files, manifest = build()
    if args.prepare:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, text in files.items():
            with (OUT / name).open('x', encoding='utf8', newline='\n') as handle: handle.write(text)
    print(json.dumps({'status': 'PREPARED_NOT_RUN' if args.prepare else 'PLAN_ONLY_NOT_RUN', 'races': 5, 'files': len(files), 'packet_sha256': manifest['source_only_packet_sha256'], 'database_contacted': False}))


if __name__ == '__main__': main()
