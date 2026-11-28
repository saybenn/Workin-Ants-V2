"""Read the exact closed evidence for one Cloud Consent assertion."""

import hashlib
import json
import os
from pathlib import Path
import re
import stat

from local_f0_cloud_csp9e633e3f_evidence import EvidenceFailure as ClosedJSONFailure, document as closed_json


ASSET = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/consent-97465adb'
DERIVED = f'{ASSET}/qualified-evidence.json'
KIND = 'DERIVED_REVIEWED_CLOUD_CONSENT_EMPTY_CONTEXT_ASSERTION_ONLY'
DERIVED_SHA = '362b3fefa50a74ed07755660e3030f028a65cf8ea258f45b287ce9e126366933'
CASE = 'P0C-IMMUTABLE-01'
ASSERTION = 'control.empty_context'
EXPECTED = 'd66b619c87e226d08fa575c71b4485f1a6dff355bb8bca2478fca3e77a237fcd'
APP_SQL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
APPEND = '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7'
IDENTITY = {
    'run_id': '97465adb-9cad-4dca-870b-7d5e77570960',
    'source_commit': '333d07196124a943d6f64015add8ca29cf1ce989',
    'source_tree': '0a44e4bc2239b87c2bc4adb63bbad94b0eb0ac93',
    'packet_sha256': '58ac8f2f82180db3ddc0bb4fbf8856303cbdc39d05d6ab86fa037ec1e82095c6',
}
FIXTURE = '6429c125-d793-4e70-ab13-6cf47a84fae2'
CID = '7f7cc4e9182ed0cd20d22b90c05fd2defdf7e101a335f58c23a9d7e3d4fa6a6a'
BIRTH = '2026-11-28T05:09:09Z'
NATIVE = 'c795fa7d78516e6b39c3e8995bcbace8ac31bef66704b8e360b767c639e711dc'
EXPECTED_NATIVE = 'cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4'
GUARD = '61dc444ce22f462fbbfcfa706f0cfdce5a7e16a028592b51d1fec07fa219e7ae'
RECIPE = 'ba4894a1104cc1fe7dd4851dc1f5ce6af93aaa9b571e23bcdad17b72a940a9d4'
CASES = ['null-context', 'empty-context']
CONTROLS = ['matching_null_context', 'matching_empty_context']
RAW_PASS = 'PASS_TWO_EMPTY_CONTEXT_ROLLBACK_DENIALS_ONLY'
OUTER_PASS = 'PASS_MACHINERY_SUBSET_ONLY'
SCOPE = 'Two restricted Consent proof denials with matching null or empty contexts on the reviewed Cloud source8 history.'
LIMIT = ('The pinned child issued exact 42-table application data parity checks and retained typed results and zero-residue outcomes. '
         'Per-table application fingerprints were unretained. The 42 native catalog relation rows and complete retained ledger/catalog '
         'artifacts were independently replayed.')
AUDIT = 'independent-closure.json'
ACCEPTANCE = 'acceptance.json'
OUTER = 'evidence/run-evidence.json'
CHILD = 'evidence/noop-consent-immutable-results.json'
EXIT = 'operation-exit.json'
PINS = {
    ACCEPTANCE: '542c223ec6877a69088a7cff39de4f0c6e21c6dfa4420fbb6b60848e0b3d7421',
    AUDIT: '158f8d9b75404e4ee628339d197f73b1d32b77514993a55e194503efdaa3850c',
    EXIT: '09df0c5d47db6118a7e2acdddb00dca7b9b57bdfb2995a4b950f9a6ce66825f6',
    OUTER: 'a2382e4fc838703514a4821e193dc26dc7b7377c9c64519ea2dccdc2e3369b3d',
    CHILD: '278f283d65d315fcac8c7218d3b23b1c1d11b157305567bef479a17f8eb7d766',
    'operation.json': IDENTITY['packet_sha256'],
}
MAX_FILE = 3 * 1024 * 1024
MAX_CAPTURE = 22 * 1024 * 1024


class EvidenceFailure(ValueError):
    """A fixed failure for the closed Consent evidence boundary."""


def require(condition, code):
    if not condition:
        raise EvidenceFailure(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def document(raw):
    try:
        return closed_json(raw)
    except ClosedJSONFailure:
        raise EvidenceFailure('CONSENT_INVALID_JSON') from None


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8')


def _same(actual, expected, code):
    require(_canonical(actual) == _canonical(expected), code)


def _fields(actual, expected, code):
    _same({key: actual[key] for key in expected}, expected, code)


def _read(path, wanted):
    def stable():
        require(path.resolve(strict=True) == path, 'CONSENT_EVIDENCE_PATH_ALIAS')
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= MAX_FILE,
                'CONSENT_EVIDENCE_FILE_SHAPE')

        def identity(item):
            return (item.st_mode, item.st_dev, item.st_ino, item.st_nlink, item.st_size, item.st_mtime_ns, item.st_ctime_ns)

        with os.fdopen(os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)), 'rb') as stream:
            opened = os.fstat(stream.fileno())
            require(identity(opened)[:-1] == identity(before)[:-1], 'CONSENT_EVIDENCE_OPEN_DRIFT')
            raw = stream.read(MAX_FILE + 1)
            require(identity(opened) == identity(os.fstat(stream.fileno())), 'CONSENT_EVIDENCE_HANDLE_DRIFT')
        require(identity(path.lstat()) == identity(before) and len(raw) == before.st_size and sha(raw) == wanted,
                'CONSENT_EVIDENCE_BYTES_DRIFT')
        return raw

    try:
        first = stable()
        require(stable() == first, 'CONSENT_EVIDENCE_CLOSED_REREAD_DRIFT')
        return first
    except (OSError, RuntimeError):
        raise EvidenceFailure('CONSENT_EVIDENCE_UNAVAILABLE') from None


def _capture(root):
    folder = root / ASSET
    audit_raw = _read(folder / AUDIT, PINS[AUDIT])
    audit = document(audit_raw)
    raw_pins = audit['file_sha256']
    require(len(raw_pins) == 41 and all(re.fullmatch(r'(?:evidence/)?[a-z0-9][a-z0-9-]*\.json', name)
            and type(pin) is str and re.fullmatch(r'[a-f0-9]{64}', pin) for name, pin in raw_pins.items()),
            'CONSENT_EXACT_41_SAFE_RAW_PATHS')
    require(all(raw_pins.get(name) == wanted for name, wanted in PINS.items() if name not in (AUDIT, ACCEPTANCE)),
            'CONSENT_RAW_PRIMARY_PINS')
    blobs = {name: _read(folder / name, pin) for name, pin in raw_pins.items()}
    blobs.update({AUDIT: audit_raw, ACCEPTANCE: _read(folder / ACCEPTANCE, PINS[ACCEPTANCE])})
    require(sum(map(len, blobs.values())) <= MAX_CAPTURE, 'CONSENT_RAW_CAPTURE_SIZE')
    return blobs


def _child(value):
    flags = lambda *keys: dict.fromkeys(keys, True)
    op = lambda stage, **fields: {'stage': stage, **fields}
    closure = op('GLOBAL_CLIENT_CLOSURE', zero_other_clients=True)
    catalog = op('UNCHANGED_NATIVE_AND_TRIGGERS', all_triggers_verified=100, native_catalog_unchanged=True)
    issuer = op('SEPARATE_ISSUER_COMMIT', **flags('commit_acknowledged', 'created_at_return_verified', 'issuer_committed', 'operation_closed'))
    diagnostic = {**flags('terminal_client_exit_3', 'before_marker_only', 'no_success_acknowledgment', 'exact_source_diagnostic'),
                  'sqlstate': 'P0001', 'source_body_sha256': GUARD, 'source_body_line': 17}
    operations = [op('ACTUAL_AUTHENTICATION', exact_current_login_controls=True, roles=['postgres', 'wa_context_issuer', 'wa_app_runtime']),
                  closure, catalog, op('TRUSTED_IDENTITY_SEED_ONLY', actual_login='postgres', commit_acknowledged=True, operation_closed=True),
                  closure, catalog, op('IDENTITY_BASELINE', only_two_expected_rows_added=True, synthetic_identity_only=True, tables_observed=42)]
    results = []
    for case, grant_count in zip(CASES, (3, 6), strict=True):
        operations.append(op('FRESH_APP_TUPLE_CAPTURE', actual_read_committed=True))
        for action, leaf in (('publishConsentVersion.v1', 'publisher.sql'), ('recordConsentPresentation.v1', 'presentation.sql'), ('SH-007.v1', 'preread.sql')):
            operations.extend([issuer, op('APP_TUPLE_RECAPTURE', same_backend_transaction=True),
                               op('SCOPED_GRANT_BIND', acknowledged=True, action=action),
                               op(leaf, consent_owner_committed=False, exact_acknowledged_observation=True)])
        operations.extend([op('EXPECTED_CONSENT_GUARD', **diagnostic), op('APP_BACKEND_CLOSURE', backend_absence_observed=True, exit_code=3),
                           closure, catalog, op('ISSUER_RETENTION', all_21_columns_verified=True, grants_exact=grant_count), closure, closure])
        results.append({'case': case, 'status': 'PASS_EXACT_DENIED_ROLLBACK_ONLY', 'diagnostic': diagnostic,
                        'app_and_issuer_closed': True, 'exact_consent_residue_zero': True, 'issued_grants_exact': grant_count,
                        'native_catalog_unchanged': True, 'original_triggers_verified': 100, 'tables_unchanged': 42})
    operations.append(closure)
    _same(value, {'schema': 'workinants.cloud-f0-consent-empty-context-result.v1', **IDENTITY, 'fixture_run_id': FIXTURE,
                  'container_id': CID, 'volume_created_at': BIRTH, 'posture': 'D', 'case_id': CASE, 'assertion_id': ASSERTION,
                  'status': RAW_PASS, 'case_order': CASES, 'current_case': None, 'current_stage': 'COMPLETE', 'first_failure': None,
                  'assertion_promotions': 0, 'consent_recipe_sha256': RECIPE, 'full_native_baseline_sha256': NATIVE,
                  'complete_final_client_closure': True, 'evidence_complete': True, 'remote_outcome_unconfirmed': False,
                  'operations': operations, 'results': results}, 'CONSENT_EXACT_48_OPERATIONS_AND_BOTH_ROLLBACKS')
    return results


def _closures(acceptance, audit, plan, outer, exit_record):
    ceiling = f'{CASE}/{ASSERTION}'
    _fields(acceptance, {**IDENTITY, 'schema': 'workinants.cloud-consent-immutable-acceptance.v1',
                         'decision': 'ACCEPT_EXACT_CONSENT_EMPTY_CONTEXT_DENIALS_AND_CLEANUP', 'Posture': 'D',
                         'operator_exit_code': 0, 'assertion_ceiling': ceiling, 'assertion_promotions': 0,
                         'observed_controls': CONTROLS, 'child_operation_records': 48, 'closed_issuer_grants': 6,
                         'qualification_limit': LIMIT, 'independent_closure_sha256': PINS[AUDIT], 'independent_reviewer': audit['reviewer']},
            'CONSENT_ACCEPTED_SINGLE_ASSERTION_AND_LIMIT')
    _fields(audit, {**IDENTITY, 'schema': 'workinants.cloud-consent-immutable-independent-closure-audit.v1',
                    'decision': 'EXACT_TWO_CONSENT_EMPTY_CONTEXT_DENIALS_AND_CLEANUP_VERIFIED', 'status': RAW_PASS, 'first_failure': None,
                    'outer_status': OUTER_PASS, 'fixture_run_id': FIXTURE, 'created_container_id': CID, 'operator': '/root',
                    'operator_exit_code': 0, 'operator_exit_receipt_sha256': PINS[EXIT], 'verified_committed_packet_files': 486,
                    'verified_consent_sql_assets': 15}, 'CONSENT_INDEPENDENT_ACTUAL_AUDIT')
    require(audit['source_author'] != audit['reviewer'] != audit['operator'], 'CONSENT_NONAUTHOR_AUDIT')
    _same(audit['scope'], {'posture': 'D', 'assertion_promotions': 0, 'supported_assertion_ceiling': ceiling,
           'qualified_cases': 'Matching null and empty Consent context rollback denials only.', 'evidence_limit': LIMIT,
           'consent_acceptance_or_legal_applicability_qualified': False, 'other_immutable_controls_qualified': False,
           'hosted_or_release_qualification': False}, 'CONSENT_INDEPENDENT_SCOPE')
    _same(audit['cleanup_verified'], dict.fromkeys(('approved_image_retained', 'container_id_absent', 'container_name_absent',
          'container_run_label_absent', 'private_host_paths_absent', 'same_daemon', 'transient_consent_evidence_absent',
          'volume_name_absent', 'volume_run_label_absent'), True), 'CONSENT_INDEPENDENT_EXACT_CLEANUP')
    _same(exit_record, {'schema': 'workinants.cloud-consent-operation-exit-observation.v1', 'run_id': IDENTITY['run_id'],
          'source_commit': IDENTITY['source_commit'], 'packet_sha256': IDENTITY['packet_sha256'], 'outer_evidence_sha256': PINS[OUTER],
          'observer': '/root', 'method': 'ACTUAL_OPERATING_PROCESS_EXIT', 'exit_code': 0, 'stdout_status': OUTER_PASS,
          'consent_status': RAW_PASS, 'evidence_complete': True}, 'CONSENT_TYPED_DIRECT_PROCESS_EXIT')
    _fields(plan, {'schema': 'workinants.cloud-f0-consent-immutable-owned-operation.v1', 'status': 'HELD_PENDING_EXACT_CONSENT_REVIEWS',
                   'posture': 'D', 'assertion_promotions': 0, 'candidate_adoption': False, 'run_id': IDENTITY['run_id'],
                   'source': {'commit': IDENTITY['source_commit'], 'tree': IDENTITY['source_tree']}, 'target': audit['target'],
                   'daemon': audit['daemon'], 'image': audit['image']}, 'CONSENT_EXACT_EXECUTED_PLAN')
    recipe = plan['consent_immutable']['recipe']
    _fields(recipe, {'case_id': CASE, 'assertion_id': ASSERTION, 'assertion_expected_sha256': EXPECTED, 'fixture_run_id': FIXTURE,
                     'source8_history_sha256': [APP_SQL, APPEND], 'grants_maximum': 6, 'posture': 'D', 'runtime': 'NOT_RUN'},
            'CONSENT_SOURCE_EXPECTATION')
    _same([c['name'] for c in recipe['cases']], CASES, 'CONSENT_EXACT_SOURCE_CASE_ORDER')
    require(sha(_canonical(recipe)) == plan['consent_immutable']['recipe_sha256'] == RECIPE, 'CONSENT_CLOSED_RECIPE')
    _fields(outer, {'schema': 'workinants.cloud-f0-consent-immutable-owned-run-evidence.v1', 'status': OUTER_PASS,
                    'stage': 'CONTROLLED_CLEANUP', 'run_id': IDENTITY['run_id'], 'approved_commit': IDENTITY['source_commit'],
                    'approved_tree': IDENTITY['source_tree'], 'approved_packet_sha256': IDENTITY['packet_sha256'], 'unexpected': [],
                    'cleanup': 'EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT', 'cleanup_full_container_identity_absent': True,
                    'final_original_references_verified': True, 'all_source_and_external_inputs_preserved_after_run': True,
                    'immutable_source_postcheck': 'PASS', 'container_id': CID, 'volume_created_at': BIRTH,
                    'actual_daemon': audit['daemon'], 'image': audit['image']}, 'CONSENT_ACTUAL_CLOSED_OWNER')
    require(outer['transport']['unknown_closure'] is False and outer.get('evidence_complete', True) is True
            and outer.get('persistence_failure', False) is False, 'CONSENT_NO_TRANSPORT_OR_PERSISTENCE_UNCERTAINTY')
    _fields(outer['consent_immutable'], {'status': RAW_PASS, 'child_status': RAW_PASS, 'assertion_promotions': 0, 'cases_observed': 2,
               'entered_after_same_live_full8_noop': True, 'cid': CID, 'volume_created_at': BIRTH, 'native_sha256': NATIVE,
               'child_receipt': {'path': CHILD.removeprefix('evidence/'), 'sha256': PINS[CHILD], 'bytes': 8887},
               'postcheck': 'PASS_CATALOG_AND_FULL_LEDGER_AFTER_CONSENT'}, 'CONSENT_SAME_OWNER_CLOSED_CHILD')


def _post_proof(acceptance, audit, outer, blobs):
    native = audit['exact_native_and_ledger']
    _same(acceptance['postchecks'], native, 'CONSENT_ACCEPTED_POST_PROOF')
    _fields(native, {'expected_catalog_sha256': EXPECTED_NATIVE, 'native_catalog_sha256': NATIVE, 'native_snapshot_count': 9,
                    'complete_native_snapshots_identical': True, 'native_checks_replayed': 29089, 'native_relation_rows_compared': 42,
                    'genuine_applied_rows': 2, 'ledger_checks_replayed_each': 22, 'ledger_observation_identical_through_consent': True,
                    'full8_ledger_fingerprints_unchanged_through_consent': True, 'expression_observations_revalidated': 416,
                    'post_consent_oracle_evidence_scope': 'INITIAL_416_REUSED_AFTER_EXACT_NATIVE_PARITY'}, 'CONSENT_EXACT_NATIVE_AND_LEDGER')
    _same([migration['sha256'] for migration in native['source_migrations']], [APP_SQL, APPEND], 'CONSENT_EXACT_INITIAL_AND_APPEND')
    snapshots = [b for name, b in blobs.items() if re.fullmatch(r'evidence/.*-native-(?:before|after|after-ledger|after-oracle)\.json', name)]
    require(len(snapshots) == 9 and all(raw == snapshots[0] for raw in snapshots) and sha(_canonical(document(snapshots[0]))) == NATIVE,
            'CONSENT_NINE_RETAINED_IDENTICAL_NATIVE_SNAPSHOTS')
    fingerprints = [blobs[f'evidence/{name}-fingerprints.json'] for name in ('initial-before-noop', 'initial-after-noop', 'noop-consent-after')]
    require(fingerprints[0] == fingerprints[1] == fingerprints[2] and sha(fingerprints[0]) == native['full8_fingerprint_file_sha256'],
            'CONSENT_RETAINED_FULL8_FINGERPRINT_PARITY')
    ledger = [blobs[f'evidence/{name}-ledger-evidence.json'] for name in ('pre-activation', 'initial', 'noop', 'noop-consent-after')]
    require(ledger[0] == ledger[1] == ledger[2] == ledger[3] and len(document(ledger[0])['observation']['history']) == 2,
            'CONSENT_RETAINED_TWO_ROW_LEDGER_PARITY')
    _fields(outer['consent_immutable']['full8'], {'status': 'PASS_EXACT_TWO_ROW_HASH_PRESERVATION_ONLY', 'history_count': 2,
            'all_eight_columns_unchanged': True, 'database_qualification_claimed': False}, 'CONSENT_TYPED_FULL8_PROOF')
    _fields(audit['consent_controls'], {'case_order': CASES, 'completed_cases': 2, 'typed_ordered_child_operations': 48,
            'issuer_grants_exact': 6, 'grant_fields_checked': 21, 'per_case_grant_retention_counts': [3, 6],
            'application_table_count_compared_per_case': 42, 'per_case_application_table_parity_reported': True,
            'zero_exact_consent_residue_reported_per_case': True, 'raw_application_table_rows_or_fingerprints_retained': False},
            'CONSENT_TYPED_APPLICATION_PARITY_LIMIT')
    return native


def derive_bytes(root):
    """Reproduce the normalized one-claim record from closed retained bytes."""
    try:
        blobs = _capture(Path(root).resolve(strict=True))
        get = lambda name: document(blobs[name])
        acceptance, audit, plan, outer = (get(name) for name in (ACCEPTANCE, AUDIT, 'operation.json', OUTER))
        _same(acceptance['archived_files_sha256'], {**audit['file_sha256'], AUDIT: PINS[AUDIT]}, 'CONSENT_ACCEPTED_RAW_FILE_GRAPH')
        _closures(acceptance, audit, plan, outer, get(EXIT))
        results = _child(get(CHILD))
        native = _post_proof(acceptance, audit, outer, blobs)
    except (KeyError, TypeError, IndexError, OSError, RecursionError):
        raise EvidenceFailure('CONSENT_EVIDENCE_SHAPE') from None
    claim = {'case_id': CASE, 'assertion_id': ASSERTION, 'status': 'PASS', 'expected_assertion_sha256': EXPECTED,
             'qualification_scope': SCOPE, 'qualification_limit': LIMIT, 'matched_rollback_controls': results}
    record = {'schema': 'workinants.cloud-consent-empty-context-qualified-evidence.v1', **IDENTITY,
              'actual_result': KIND, 'raw_runtime_result': RAW_PASS, 'database_posture': 'D', 'application_sql_sha256': APP_SQL,
              'migration_history': [APP_SQL, APPEND], 'input_files_sha256': {name: sha(raw) for name, raw in blobs.items()},
              'native_and_ledger': native, 'evidence_limit': LIMIT, 'claims': [claim]}
    return (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf8')


def is_reference(row):
    return (row.get('evidence_path') == DERIVED or row.get('run_id') == IDENTITY['run_id']
            or row.get('evidence_sha256') == DERIVED_SHA or row.get('actual_result') == KIND)


def links():
    execution = {**IDENTITY, 'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA, 'actual_result': KIND, 'qualification_scope': SCOPE}
    row = {'case_id': CASE, 'assertion_id': ASSERTION, 'status': 'PASS', 'expected_assertion_sha256': EXPECTED, **IDENTITY,
           'application_sql_sha256': APP_SQL, 'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA,
           'json_pointer': '/claims/0', 'qualification_scope': SCOPE, 'qualification_limit': LIMIT}
    return [row], execution


def propose_ledger_delta(previous, derived):
    """Append one exact row and execution to the caller's accepted ledger in memory."""
    require(type(derived) is bytes and sha(derived) == DERIVED_SHA, 'CONSENT_EXACT_NORMALIZED_BYTES')
    ledger = document(previous)
    require(type(ledger) is dict and type(ledger.get('assertions')) is list and type(ledger.get('executions')) is list
            and all(type(row) is dict for row in ledger['assertions'] + ledger['executions']), 'CONSENT_PRIOR_LEDGER_SHAPE')
    identities = [(row.get('case_id'), row.get('assertion_id')) for row in ledger['assertions']]
    require(all(type(case) is str and type(assertion) is str for case, assertion in identities)
            and len(set(identities)) == len(identities), 'CONSENT_PRIOR_ASSERTION_IDENTITIES')
    require((CASE, ASSERTION) not in identities and not any(map(is_reference, ledger['assertions'] + ledger['executions'])),
            'CONSENT_APPEND_NEW_ASSERTION_AND_EXECUTION_ONLY')
    rows, execution = links()
    ledger['assertions'].extend(rows)
    ledger['executions'].append(execution)
    return ledger


class QualificationBatch:
    def __init__(self, root, ledger):
        self.root = Path(root).resolve(strict=True)
        self.raw = _read(self.root / DERIVED, DERIVED_SHA)
        require(self.raw == derive_bytes(self.root), 'CONSENT_REDERIVED_NORMALIZED_RECORD')
        rows, execution = links()
        _same([row for row in ledger['assertions'] if is_reference(row)], rows, 'CONSENT_EXACT_ONE_LEDGER_ROW')
        _same([row for row in ledger['executions'] if is_reference(row)], [execution], 'CONSENT_EXACT_ONE_EXECUTION')
        self.row, = rows
        self.observed = False
        self.finalized = False
        self.failure = None

    def _reject(self, code):
        self.failure = self.failure or code
        raise EvidenceFailure(self.failure) from None

    def validate_claim(self, execution, row):
        try:
            require(self.failure is None and not self.observed and not self.finalized, 'CONSENT_EXACT_SINGLE_CLAIM_USE')
            _same(row, self.row, 'CONSENT_EXACT_ASSERTION_ROW_AND_POINTER')
            _same(execution, document(self.raw), 'CONSENT_EXACT_NORMALIZED_EXECUTION')
            self.observed = True
            return True
        except EvidenceFailure as error:
            self._reject(str(error))
        except (TypeError, ValueError):
            self._reject('CONSENT_CLAIM_SHAPE')

    def verify_unchanged(self):
        try:
            require(self.failure is None and self.observed and not self.finalized, 'CONSENT_FINAL_SINGLE_CLAIM_REQUIRED')
            require(_read(self.root / DERIVED, DERIVED_SHA) == self.raw == derive_bytes(self.root), 'CONSENT_FINAL_ALL_INPUT_BYTES')
            self.finalized = True
            return True
        except EvidenceFailure as error:
            self._reject(str(error))
