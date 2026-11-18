"""Pure, fail-closed assertion mapping for the independently reviewed 196c run.

This is deliberately not a generic successful-run adapter. Five exact assertions
can receive PASS and three incomplete assertions can receive PARTIAL. Existing
cleanup evidence has its own parser. No database, process, Git or network is used.
Retained operator text is hashed as data, never imported. Only the exact reviewed
diagnostics module bytes are loaded, after their SHA-256 is checked, to reconstruct
the bounded server proof. Its process-reading function is never called.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import types

RESULT = 'PASS_GENUINE_FIRST_NOOP_FAILURE_REVIEWED_RESOLVE_SAME_CHECKSUM_RETRY'
RUN = '196c3d8a-5772-4327-a72f-b760be420203'
COMMIT = '6b8910dca9e647bf41733e9f9c5fd6fd5515141f'
TREE = 'c27194d4593f8c030e6d07e8a6b67a76faf2a540'
PACKET = 'd06b1ed973c57a6a0ef531be45370ea34a161c4a322d08ad2912a869761b2cb8'
SQL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
MIGRATION = '20261117000100_f0_local_initial'
DIAGNOSTICS = 'scripts/sql-review/migration_server_diagnostics.py'
DIAGNOSTICS_SHA = '6d4d08362f3f4527138fb166324f03b5720cf912a9c38d987a28164e3a54e54d'
ASSETS = 'context/reconciliation/local-f0-run-assets/6b8910d-genuine-migration'
REPORT_SHA = '9a8f4bff653dc1292c24f48cda90cb14b2cd5787653896a083389333d51ef090'
# Canonical JSON of the separately byte-pinned e657bd4 execution record. This
# also refuses new narrative/metadata fields until their mapping is reviewed.
EXECUTION_CANONICAL_SHA = 'effd7f704e8f4d661da8354c6f5b63570b31c035a0f7ded1dad1313b93ba0d8e'
OK = 'wa-p0c-196c3d8a-migrate-ok'
FAIL = 'wa-p0c-196c3d8a-migrate-fail'
CIDS = {
    OK: 'b59f46b24a9d01ef2e97aa0bb2ea93cf0194ee607b125ceaaa7e5c0550755bd4',
    FAIL: '1b42dd3bb88e28d59f1f64464e34e3c8c59a3352e81c1e0561acfdd2f2a227c5',
}
CLAIMS = {
    ('P0C-INSTALL-01', 'control.empty_deploy'): 'PASS',
    ('P0C-INSTALL-01', 'control.second_deploy'): 'PASS',
    ('P0C-INSTALL-02', 'control.failed_ledger'): 'PASS',
    ('P0C-INSTALL-02', 'control.recovery'): 'PASS',
    ('P0C-INSTALL-02', 'control.immutable_applied_history'): 'PASS',
    ('P0C-INSTALL-01', 'control.private_ledger'): 'PARTIAL',
    ('P0C-INSTALL-01', 'vector.INSTALL-CLEANUP.positive'): 'PARTIAL',
    ('P0C-INSTALL-02', 'control.intended_failure'): 'PARTIAL',
}
PARTIAL_LIMITS = {
    'control.private_ledger': 'Full eight-privilege, type, index and native ledger proof remains unrun.',
    'vector.INSTALL-CLEANUP.positive': 'Runtime credentials were provisioned before independent cleanup verification; the activation hold was not exercised.',
    'control.intended_failure': 'The injected fault was temporary SET membership withholding, a permission failure; no distinct failing SQL-history variant was exercised.',
}
SNAPSHOTS = {
    'authentication-fail-authentication-results-ok.json': '21c3b8c7433671bcccd54501f382202ae98480e87a858327aaac0a7ba0a3f7d9',
    'authentication-ok-authentication-results-ok.json': '757b2ef37c035e745e44bbb730bab20e116d6a3f14b6531cbbdaa19186fb2548',
    'fail-history-manifest.json': 'f66647e57c6ffb925f11fed1e070fd2ee09b79a7790536c3f933435d002a2aa2',
    'fail-migration-manifest.json': '4794f0dbea8efca8e3417cc72ec9ecbdd50f5ccd35ad5e5aaf3f368f46b6219a',
    'ok-history-manifest.json': '9cf9d8b4d3404b6873a46cd7338a6369174bf2de45c47e32432cb2db24dbf4ef',
    'ok-migration-manifest.json': '331157228f92dce6570bd9b9be9e166d9055892f7af6c13f243b6fad861d53ac',
    'operation-manifest.json': 'b103fa7f5c9ec8a4d6c488165c66eede06e20a869acf1ebfb71e752de802d727',
    'operation-steps.py.txt': '47514ed5e9d116db5ce112e5cbb677a703107dc2cd6c9bbc75fc571afac35cf6',
    'operational-review.json': '3d04306366030264377048631c937fcf04b8938f93fd7bb52460c08e17afc2d1',
    'operator-snapshot.py.txt': 'd7159320e2ce040119e2377736dfc409c582a2c81d70d01c7a25adbbac0aecf2',
    'recovery-review-approval.json': '575b21cc044db4bec6dbadfead2bc024edf8c01ef6bbb4264921645275cea7ed',
    'reviewed-rollback-proof.json': 'a70238ca6659c5a8234269bdf2ad317f0a2a3572d69098f4fbbfdb16b84cba2e',
    'rollback-proof-for-review.json': '62e00b55902a0c021b39656130ccc431e5228d969ae89f9723a2ad3ad56fc941',
    'server-error-proof.json': '214388a1071550097d0c7f8fb37e2a4c350186506be5ce13fbc09406d43b8275',
}
STEPS = {name: 'PASS' for name in ('MIGRATE-SETUP', 'MIGRATE-AUTH', 'MIGRATE-TOOLS', 'MIGRATE-EMPTY', 'MIGRATE-NOOP', 'MIGRATE-RESOLVE', 'MIGRATE-SANITIZED_EXPORT', 'MIGRATE-CLEANUP')}
STEPS.update({'MIGRATE-FAILURE': 'PASS_SERVER_42501_INTENDED_SET_ROLE_GUARD_AND_ROLLBACK', 'MIGRATE-RETRY': 'PASS_SAME_SQL_CHECKSUM_RETAINED_FAILED_ROW'})
CLASSIFICATION = 'SERVER_42501_WITH_SECONDARY_25P02_UNWRITTEN_FAILURE_LOGS'
APPLICATION_COUNTS = {'application_relations': 188, 'application_functions': 147, 'application_types': 142, 'application_enums': 29, 'application_tables': 42}
LEAVES = ('wa_track_verifier', 'wa_customer_verifier', 'wa_private_helper_owner')
RECORD_FIELDS = {
    'local_date', 'timezone', 'scope', 'actual_result', 'source_commit', 'source_tree',
    'packet_sha256', 'run_id', 'application_sql_sha256', 'actual_steps', 'unexpected',
    'operator_raw_safe_report', 'external_json_artifacts_sha256',
    'snapshot_files_sha256', 'independent_absence', 'limits', 'posture',
    'next_action', 'actual_failure_diagnostic', 'recovery_review',
    'historical_distinction',
}


class EvidenceFailure(ValueError):
    """Only fixed refusal codes escape the evidence boundary."""


def _need(value, code):
    if not value:
        raise EvidenceFailure(code)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def _same(value, expected, code):
    # JSON comparison distinguishes true/1 and false/0, unlike Python equality.
    _need(_json(value) == _json(expected), code)


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _read(root, relative, expected):
    _need(type(relative) is str and '\\' not in relative and not relative.startswith('/') and all(x not in ('', '.', '..') for x in relative.split('/')), 'MIGRATION_EVIDENCE_PATH')
    path = (root / relative).resolve(strict=True)
    _need(path.is_relative_to(root), 'MIGRATION_EVIDENCE_PATH')
    raw = path.read_bytes()
    _need(_hash(raw) == expected, 'MIGRATION_EVIDENCE_FILE_HASH')
    return raw


def _load_snapshots(root, execution):
    _same(execution['snapshot_files_sha256'], SNAPSHOTS, 'MIGRATION_SNAPSHOT_BINDING')
    external = {name: SNAPSHOTS[name] for name in ('recovery-review-approval.json', 'reviewed-rollback-proof.json', 'rollback-proof-for-review.json', 'server-error-proof.json')}
    external.update({'authentication-fail/authentication-results-ok.json': SNAPSHOTS['authentication-fail-authentication-results-ok.json'], 'authentication-ok/authentication-results-ok.json': SNAPSHOTS['authentication-ok-authentication-results-ok.json'], 'run-evidence.json': REPORT_SHA})
    _same(execution['external_json_artifacts_sha256'], external, 'MIGRATION_EXTERNAL_ARTIFACT_BINDING')
    result = {}
    for name, digest in SNAPSHOTS.items():
        raw = _read(root, ASSETS + '/' + name, digest)
        if name.endswith('.json'):
            result[name] = json.loads(raw)
    return result


def _source(root, execution, report, snapshots):
    identity = {'run_id': RUN, 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET}
    for key, expected in identity.items():
        _same(execution[key], expected, 'MIGRATION_IDENTITY')
    _same(execution['application_sql_sha256'], SQL, 'MIGRATION_SQL_IDENTITY')
    _same(report['run_id'], RUN, 'MIGRATION_REPORT_IDENTITY')
    for key, expected in [('approved_commit', COMMIT), ('approved_tree', TREE), ('approved_packet_sha256', PACKET)]:
        _same(report[key], expected, 'MIGRATION_REPORT_IDENTITY')
    manifest = snapshots['operation-manifest.json']
    _same(report['run_manifest'], manifest, 'MIGRATION_MANIFEST_BINDING')
    _same(report['run_manifest_sha256'], SNAPSHOTS['operation-manifest.json'], 'MIGRATION_MANIFEST_BINDING')
    _need(manifest['review_status'] == 'APPROVED_GENUINE_MIGRATION_ATTEMPT', 'MIGRATION_OPERATION_REVIEW')
    hashes = manifest['packet_files_sha256']
    _need(type(hashes) is dict and len(hashes) == 45 and all(type(k) is str and type(v) is str and re.fullmatch('[0-9a-f]{64}', v) for k, v in hashes.items()), 'MIGRATION_PACKET_FIELDS')
    aggregate = _hash(''.join(p + '\0' + hashes[p] + '\n' for p in sorted(hashes)).encode())
    _same(aggregate, PACKET, 'MIGRATION_PACKET_AGGREGATE')
    _same(report['source_verification'], {'commit': COMMIT, 'tree': TREE, 'packet_sha256': PACKET, 'files_sha256': hashes, 'file_count': 45}, 'MIGRATION_SOURCE_VERIFICATION')
    for path, digest in hashes.items():
        _read(root, path, digest)
    for path in ['review-output/foundation-application.review.sql', 'prisma/foundation/migrations/' + MIGRATION + '/migration.sql']:
        _same(hashes[path], SQL, 'MIGRATION_HISTORY_SQL')
    _need(report['packet_unchanged_after_run'] is True, 'MIGRATION_SOURCE_PRESERVATION')
    for kind, name in [('ok', OK), ('fail', FAIL)]:
        target_manifest = snapshots[kind + '-migration-manifest.json']
        history = snapshots[kind + '-history-manifest.json']
        _same(target_manifest['run_id'], RUN, 'MIGRATION_HISTORY_BINDING')
        _same(target_manifest['target']['container_name'], name, 'MIGRATION_HISTORY_BINDING')
        _same(target_manifest['source']['integrated_sql_sha256'], SQL, 'MIGRATION_HISTORY_BINDING')
        _same(target_manifest['migration'], {'id': MIGRATION, 'history': 'prisma/foundation/migrations'}, 'MIGRATION_HISTORY_BINDING')
        _same(history['run_id'], RUN, 'MIGRATION_HISTORY_BINDING')
        _same(history['migration_id'], MIGRATION, 'MIGRATION_HISTORY_BINDING')
        _same(history['source_sql_sha256'], SQL, 'MIGRATION_HISTORY_BINDING')
        _same(history['run_manifest_sha256'], SNAPSHOTS[kind + '-migration-manifest.json'], 'MIGRATION_HISTORY_BINDING')
        _same(history['files_sha256'], {p: h for p, h in manifest['migration_targets'][kind]['source_files_sha256'].items() if p != 'prisma/foundation/history-manifest.json'}, 'MIGRATION_HISTORY_BINDING')
        _same(target_manifest['source']['runtime_files_sha256'], {p: hashes[p] for p in ('prisma.local-f0.config.mjs', 'scripts/sql-review/local-f0-migrate-guard.mjs', 'scripts/sql-review/local-f0-migrate-runner.mjs')}, 'MIGRATION_RUNTIME_BINDING')
    _same(snapshots['ok-migration-manifest.json']['tools'], snapshots['fail-migration-manifest.json']['tools'], 'MIGRATION_TOOL_CLOSURE')


def _operations(report):
    phases = [('EMPTY_PRISMA_DEPLOY', OK, 'deploy'), ('SECOND_PRISMA_DEPLOY', OK, 'deploy'), ('EXPECTED_FAILED_PRISMA_DEPLOY', FAIL, 'deploy'), ('STANDARD_PRISMA_RESOLVE', FAIL, 'resolve-rolled-back'), ('SAME_CHECKSUM_RECOVERY_DEPLOY', FAIL, 'deploy'), ('RECOVERED_SECOND_DEPLOY', FAIL, 'deploy')]
    ops = report['migration_operations']
    _need(type(ops) is list and len(ops) == len(phases), 'MIGRATION_OPERATION_SET')
    fields = {'target', 'stage', 'schema', 'operation', 'status', 'exit_code', 'prisma_codes', 'sqlstates', 'diagnostic_format', 'no_pending_message_observed', 'raw_output_discarded', 'database_qualification_claimed', 'run_id', 'container_id', 'source_sql_sha256', 'attestation_sha256'}
    for op, (phase, target, operation) in zip(ops, phases):
        _need(type(op) is dict and set(op) == fields, 'MIGRATION_OPERATION_FIELDS')
        for key, value in {'schema': 'workinants.local-f0-migrate-result.v2', 'target': target, 'stage': phase, 'operation': operation, 'run_id': RUN, 'container_id': CIDS[target], 'source_sql_sha256': SQL, 'prisma_codes': [], 'sqlstates': [], 'raw_output_discarded': True, 'database_qualification_claimed': False}.items():
            _same(op[key], value, 'MIGRATION_OPERATION_IDENTITY')
        failed = phase == 'EXPECTED_FAILED_PRISMA_DEPLOY'
        _same(op['exit_code'], 1 if failed else 0, 'MIGRATION_OPERATION_CLOSURE')
        _same(op['status'], 'CLI_OUTPUT_REJECTED_STOP_AND_INSPECT' if failed else 'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS', 'MIGRATION_OPERATION_STATUS')
        _same(op['no_pending_message_observed'], phase in ('SECOND_PRISMA_DEPLOY', 'RECOVERED_SECOND_DEPLOY'), 'MIGRATION_NOOP_MESSAGE')
        _same(op['diagnostic_format'], {'text_valid': True, 'sgr_stripped': False, 'headers_valid': not failed, 'prisma_header_present': failed, 'prisma_header_unique': failed, 'database_header_present': False, 'database_header_unique': False}, 'MIGRATION_CLI_FORMAT')
        _need(type(op['attestation_sha256']) is str and re.fullmatch('[0-9a-f]{64}', op['attestation_sha256']), 'MIGRATION_ATTESTATION_HASH')
    return ops


def _row(finished, rolled_back, steps):
    return {'name': MIGRATION, 'steps': steps, 'checksum': SQL, 'finished': finished, 'logs_state': 'NULL', 'rolled_back': rolled_back, 'expected_error_code': False, 'expected_set_role_error': False}


def _ledger(value, stage, rows, counts):
    expected = {'stage': stage, 'ledger_present': True, 'ledger_regular': True, 'active_migrators': 0, **counts, 'ledger_owner_expected': True, 'public_relation_count': 1, 'rows': rows, 'ledger_rows_observed': True, 'owner': 'wa_migrator', 'runtime_ledger_access': False}
    _same(value, expected, 'MIGRATION_LEDGER_STATE')


def _targets(report, snapshots):
    _need(type(report['targets']) is dict and set(report['targets']) == set(CIDS), 'MIGRATION_TARGET_SET')
    for kind, name in [('ok', OK), ('fail', FAIL)]:
        target = report['targets'][name]
        for key, value in {'container_id': CIDS[name], 'volume': name + '-data', 'network_mode': 'none', 'published_ports': False, 'bootstrap': 'PASS', 'finalization': 'PASS', 'labels': {'workinants.rehearsal': 'p0c-local-f0', 'workinants.rehearsal.run': RUN}}.items():
            _same(target[key], value, 'MIGRATION_TARGET_IDENTITY')
        _same(target['server_settings'], {'auth': 'scram-sha-256:postgres', 'safe': True, 'login': 'postgres', 'superuser': True, 'diagnostics_safe': True}, 'MIGRATION_SERVER_SETTINGS')
        _same(target['connections_before_finalization'], {'migrator': 0, 'tagged_other_clients': 0}, 'MIGRATION_BACKEND_CLOSURE')
        _same(target['finalization_observation'], {'auth': 'scram-sha-256:postgres', 'grantor': 'postgres', 'leaf_create': dict.fromkeys(LEAVES, False), 'remaining_memberships': 0, 'active_install_connections': 0}, 'MIGRATION_FINALIZATION')
        for field in ('application_relations', 'public_relations', 'event_triggers'):
            _same(target['baseline'][field], 0, 'MIGRATION_EMPTY_BASELINE')
        auth = snapshots['authentication-' + kind + '-authentication-results-ok.json']
        _same(auth['target'], name, 'MIGRATION_AUTHENTICATION')
        _same(auth['status'], 'PASS_PREFLIGHT_ONLY', 'MIGRATION_AUTHENTICATION')
        _need(len(auth['authentication']) == 6 and all(a['correct_password'] == 'PASS_SCRAM' and a['wrong_password'] == 'PASS_REJECTED' and type(a['wrong_password_exit_code']) is int and a['wrong_password_exit_code'] == 2 for a in auth['authentication']), 'MIGRATION_AUTHENTICATION')
        _same(target['linux_tool_compatibility'], {'node': 'v24.22.1', 'engine_commit': 'd1b3f377ca835d73fd50954a5e22128b9ebdd6b8', 'preexec_hashes_verified': True}, 'MIGRATION_TOOL_COMPATIBILITY')
        comparison = target['second_deploy_schema_comparison']
        projection = {'sha256': '718c3f037343b7e766e3e540924d018cb6ab7e5010fa5ca1a01c1b5d2d6e7ffe', 'random_dump_meta_lines_removed': 2, 'raw_schema_dump_retained': False}
        _same(comparison, {'first': projection, 'second': projection, 'identical': True}, 'MIGRATION_SCHEMA_NOOP')
    good = report['targets'][OK]['ledger_observations']
    bad = report['targets'][FAIL]['ledger_observations']
    _need(type(good) is list and len(good) == 2 and type(bad) is list and len(bad) == 4, 'MIGRATION_LEDGER_SET')
    success, failed, resolved = _row(True, False, 1), _row(False, False, 0), _row(False, True, 0)
    for value, stage in zip(good, ('FIRST_DEPLOY_LEDGER', 'SECOND_DEPLOY_LEDGER')):
        _ledger(value, stage, [success], APPLICATION_COUNTS)
    for value, stage, rows, counts in zip(bad, ('FAILED_DEPLOY_LEDGER_AND_ROLLBACK', 'RESOLVED_LEDGER_OBSERVER', 'RECOVERED_LEDGER_OBSERVER', 'RECOVERED_SECOND_LEDGER'), ([failed], [resolved], [resolved, success], [resolved, success]), (dict.fromkeys(APPLICATION_COUNTS, 0), dict.fromkeys(APPLICATION_COUNTS, 0), APPLICATION_COUNTS, APPLICATION_COUNTS)):
        _ledger(value, stage, rows, counts)
    _same(report['targets'][FAIL]['intentional_setup_fault'], {'remaining_two': 2, 'missing_customer_verifier': True}, 'MIGRATION_FAULT_BOUNDARY')
    return bad[0]


def _load_diagnostics(raw):
    # Compile the very bytes just hashed, rather than reopening a module path.
    namespace = types.ModuleType('_reviewed_local_f0_diagnostics')
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        exec(compile(raw, '<reviewed-migration-diagnostics>', 'exec'), namespace.__dict__)
    _need(not output.getvalue(), 'MIGRATION_HELPER_OUTPUT')
    return namespace


def _proof(root, execution, report, snapshots, ops, failed):
    target = report['targets'][FAIL]
    proof = snapshots['server-error-proof.json']
    identity = {'run_id': RUN, 'container_id': CIDS[FAIL], 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET, 'application_sql_sha256': SQL, 'module_sha256': DIAGNOSTICS_SHA, 'migration_id': MIGRATION}
    observations = target['server_error_observations']
    _need(type(observations) is list and len(observations) == 2, 'MIGRATION_SERVER_OBSERVATIONS')
    before, after = [], []
    for item, stage, dest in zip(observations, ('BEFORE_EXPECTED_FAILED_PRISMA_DEPLOY', 'AFTER_CONFIRMED_CLOSURE_AND_FINALIZATION'), (before, after)):
        _same(item['stage'], stage, 'MIGRATION_SERVER_OBSERVATIONS')
        dest.append({k: v for k, v in item.items() if k != 'stage'})
    helper = _load_diagnostics(_read(root, DIAGNOSTICS, DIAGNOSTICS_SHA))
    helper.validate_proof(proof, identity)
    rebuilt = helper.build_proof(identity, ops[2], failed, before[0], after[0], {'logging_settings_verified': True, 'original_grantor_finalized': True, 'operation_backends_absent': True})
    _same(rebuilt, proof, 'MIGRATION_SERVER_PROOF_REBUILD')
    _same(target['failure_diagnostic_proof'], proof, 'MIGRATION_SERVER_PROOF_BINDING')
    _same(target['server_error_delta'], proof['delta'], 'MIGRATION_SERVER_PROOF_BINDING')
    _same(report['server_error_proof_sha256'], SNAPSHOTS['server-error-proof.json'], 'MIGRATION_SERVER_PROOF_BINDING')
    _same(execution['actual_failure_diagnostic'], {'classification': CLASSIFICATION, 'provenance': 'OWNED_POSTGRES_TERSE_ERROR_LOG_DELTA', 'server_error_delta': proof['delta'], 'failed_row_logs_state': 'NULL', 'CLI_status': ops[2]['status'], 'retained_P3018_claimed': False, 'server_proof_sha256': SNAPSHOTS['server-error-proof.json']}, 'MIGRATION_FAILURE_SCOPE')
    pending = snapshots['rollback-proof-for-review.json']
    _same(pending['run_id'], RUN, 'MIGRATION_ROLLBACK_PROOF')
    _same(pending['container_id'], CIDS[FAIL], 'MIGRATION_ROLLBACK_PROOF')
    for key in ('application_object_count', 'application_relation_count', 'application_function_count', 'application_type_count', 'application_enum_count', 'finished_migration_rows', 'rolled_back_migration_rows'):
        _same(pending[key], 0, 'MIGRATION_ROLLBACK_PROOF')
    _same(pending['failed_migration_rows'], 1, 'MIGRATION_ROLLBACK_PROOF')
    _need(pending['backend_closed'] is True and pending['application_transaction_rolled_back'] is True, 'MIGRATION_ROLLBACK_PROOF')
    # ledger() returned only its second query, before the reporting envelope was
    # merged with the preceding catalog-presence observation.
    envelope = {'stage', 'ledger_present', 'ledger_regular', 'ledger_owner_expected', 'ledger_rows_observed'}
    ledger_payload = {key: value for key, value in failed.items() if key not in envelope}
    _same(pending['ledger_evidence_sha256'], _hash(json.dumps(ledger_payload, sort_keys=True).encode()), 'MIGRATION_ROLLBACK_LEDGER_HASH')
    catalog = {short: failed[long] for short, long in [('relations', 'application_relations'), ('functions', 'application_functions'), ('types', 'application_types'), ('enums', 'application_enums')]}
    catalog['finalization'] = target['finalization_observation']
    _same(pending['catalog_evidence_sha256'], _hash(json.dumps(catalog, sort_keys=True).encode()), 'MIGRATION_ROLLBACK_CATALOG_HASH')
    _same(snapshots['reviewed-rollback-proof.json'], {**pending, 'disposition': 'REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK'}, 'MIGRATION_REVIEWED_PROOF')
    approval = {'decision': 'APPROVE_STANDARD_RESOLVE_AND_RETRY', 'reviewer': 'review_track_ports', 'run_id': RUN, 'proof_sha256': SNAPSHOTS['rollback-proof-for-review.json']}
    for value in (snapshots['recovery-review-approval.json'], report['recovery_review'], execution['recovery_review']):
        _same(value, approval, 'MIGRATION_RECOVERY_APPROVAL')
    _same(report['reviewed_rollback_proof_sha256'], SNAPSHOTS['reviewed-rollback-proof.json'], 'MIGRATION_REVIEWED_PROOF')


def _events_and_cleanup(execution, report):
    events = report['events']
    _need(type(events) is list and len(events) == 50, 'MIGRATION_EVENT_SET')
    for event in events:
        _need(type(event) is dict, 'MIGRATION_EVENT_FIELDS')
        if 'operation' in event:
            for key, expected in {'role': 'postgres', 'exit_code': 0, 'errors': [], 'client_exited': True}.items():
                _same(event[key], expected, 'MIGRATION_SQL_OPERATION_CLOSURE')
            _need(event['target'] in CIDS, 'MIGRATION_SQL_OPERATION_TARGET')
    for name in CIDS:
        sql = [e['operation'] for e in events if e.get('target') == name and 'operation' in e]
        repeats = 1 if name == OK else 2
        for operation in ('PRE_FINALIZATION_CONNECTION_OBSERVER', 'ORIGINAL_GRANTOR_FINALIZATION', 'FINALIZATION_OBSERVER'):
            _same(sql.count(operation), repeats, 'MIGRATION_FINALIZATION_SEQUENCE')
        for operation in ('BOOTSTRAP', 'CREDENTIAL_PROVISION', 'EMPTY_APPLICATION_BASELINE'):
            _same(sql.count(operation), 1, 'MIGRATION_SETUP_SEQUENCE')
    hold = [i for i, e in enumerate(events) if e.get('stage') == 'RECOVERY_REVIEW_REQUIRED']
    _need(len(hold) == 1 and events[hold[0]]['status'] == 'HELD' and events[hold[0]]['proof_sha256'] == SNAPSHOTS['rollback-proof-for-review.json'], 'MIGRATION_REVIEW_HOLD')
    positions = {name: next(i for i, e in enumerate(events) if e.get('operation') == name) for name in ('FAILED_DEPLOY_LEDGER_AND_ROLLBACK', 'RESOLVED_LEDGER_OBSERVER', 'ORIGINAL_GRANTOR_EXACT_TEMPORARY_REARM', 'REARM_AUTHORITY_OBSERVER', 'RECOVERED_LEDGER_OBSERVER')}
    _need(positions['FAILED_DEPLOY_LEDGER_AND_ROLLBACK'] < hold[0] < positions['RESOLVED_LEDGER_OBSERVER'] < positions['ORIGINAL_GRANTOR_EXACT_TEMPORARY_REARM'] < positions['REARM_AUTHORITY_OBSERVER'] < positions['RECOVERED_LEDGER_OBSERVER'], 'MIGRATION_RECOVERY_SEQUENCE')
    names = {n: False for name in CIDS for n in (name, name + '-data')}
    _same(report['cleanup_summary']['resource_presence_after'], names, 'MIGRATION_RESOURCE_ABSENCE')
    _same(execution['independent_absence']['resource_presence'], names, 'MIGRATION_INDEPENDENT_ABSENCE')
    for name in CIDS:
        _same(report['cleanup'][name], {'removed': True, 'verified_id': CIDS[name], 'name_and_both_labels_verified': True}, 'MIGRATION_CLEANUP_IDENTITY')
        _same(report['cleanup'][name + '-data'], {'removed': True, 'name_labels_creation_identity_verified': True}, 'MIGRATION_CLEANUP_IDENTITY')
    for value, fields in [(report['cleanup_summary'], {'private_directory_absent': True, 'image_removed': False, 'unrelated_resources_changed': False}), (execution['independent_absence'], {'host_private_absent': True, 'image_retained': True, 'shared_resources_changed': False}), (report['host_secret_cleanup'], {'private_directory_absent': True})]:
        for key, expected in fields.items():
            _same(value[key], expected, 'MIGRATION_SECRET_CLEANUP')
    _same(report['host_secret_cleanup']['deleted'], ['ok-bootstrap-password', 'fail-bootstrap-password'], 'MIGRATION_SECRET_CLEANUP')
    _same(report['sanitization'], {'files_scanned': 8, 'actual_password_values_found': False, 'unrestricted_subprocess_output_persisted': False, 'raw_context_handles_persisted': False, 'coordinator_evidence_uses_reviewed_allowlist': True}, 'MIGRATION_SANITIZATION')


def validate_claim(case_id, assertion_id, status, execution, root):
    """Return True or raise EvidenceFailure with a fixed, data-free refusal code.

    PARTIAL means the recorded subset exists, never that its omitted requirement
    passed. The caller must still bind inventory expectation/evidence hashes and
    refuse whole-case PASS until every mandatory assertion is actually PASS.
    """
    try:
        _need(all(type(v) is str for v in (case_id, assertion_id, status)), 'MIGRATION_CLAIM_FIELDS')
        _need(CLAIMS.get((case_id, assertion_id)) == status, 'MIGRATION_CLAIM_NOT_SUPPORTED')
        _need(type(execution) is dict and execution.get('actual_result') == RESULT, 'MIGRATION_RECORD_KIND')
        _need(set(execution) == RECORD_FIELDS, 'MIGRATION_RECORD_FIELDS')
        _need(execution['scope'] == 'GENUINE_LOCAL_PRISMA_MIGRATION_HISTORY_SUBSET_ONLY' and execution['posture'] == 'D', 'MIGRATION_RECORD_SCOPE')
        _same(execution['actual_steps'], STEPS, 'MIGRATION_STEPS')
        _same(execution['unexpected'], [], 'MIGRATION_UNEXPECTED')
        base = Path(root).resolve(strict=True)
        report = execution['operator_raw_safe_report']
        _need(type(report) is dict and report['status'] == 'PASS_GENUINE_MIGRATION_SUBSET_ONLY', 'MIGRATION_REPORT_KIND')
        _same(report['steps'], STEPS, 'MIGRATION_STEPS')
        _same(report['unexpected'], [], 'MIGRATION_UNEXPECTED')
        snapshots = _load_snapshots(base, execution)
        _source(base, execution, report, snapshots)
        ops = _operations(report)
        failed = _targets(report, snapshots)
        _proof(base, execution, report, snapshots, ops, failed)
        _events_and_cleanup(execution, report)
        # Preserve all remaining bounded operator fields exactly as reviewed,
        # including opaque paths as data. They never become executable inputs.
        _same(_hash((json.dumps(report, indent=2) + '\n').encode()), REPORT_SHA, 'MIGRATION_RETAINED_REPORT_HASH')
        _same(_hash(_json(execution).encode()), EXECUTION_CANONICAL_SHA, 'MIGRATION_RETAINED_EXECUTION_HASH')
        return True
    except EvidenceFailure:
        raise
    except BaseException:
        # Helpers, JSON, paths and malformed evidence never expose raw content.
        raise EvidenceFailure('MIGRATION_EVIDENCE_REJECTED') from None
