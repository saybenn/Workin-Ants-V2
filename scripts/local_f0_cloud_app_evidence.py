"""Read the two independently reviewed Cloud application assertion receipts."""

import hashlib
import json
from pathlib import Path

from local_f0_cloud_csp9e633e3f_evidence import document


ASSET = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/app-2e59e073'
DERIVED = f'{ASSET}/qualified-evidence.json'
KIND = 'DERIVED_REVIEWED_CLOUD_SOURCE8_TWO_APP_WRITE_ASSERTIONS_ONLY'
DERIVED_SHA = '3c89b789402a2f257307e03938e208525165448804991912dececd461b37fc4e'
BASELINE_LEDGER = '8a0c0965c131058586c950ecb982f7f59f1797a78363915ef8ab3dbf136d9650'
APPLICATION = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
APPEND = '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7'
EXPECTED_ASSERTION = '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c'
IDENTITY = {
    'run_id': '2e59e073-ef6e-4895-bf05-f920767d8543',
    'source_commit': '9fd12ffb882fd7704ab7b428c2073a6fead03296',
    'source_tree': 'a1b2974622afa55cf41b5416ccf24195d6956f22',
    'packet_sha256': '7495da1a762f3e25e7fe6e1a6d35a729dc535ba34dffa62444131d9d1fdfc49a',
}
SCOPES = (
    ('P0C-TABLE-RuntimeEffectReceipt-ALLOW', 'positive.wa_app_runtime.insert', 'genuine-sh004-effect-insert',
     'Restricted App effect insert within the reviewed genuine Customer provisioning transaction.'),
    ('P0C-TABLE-RuntimeWorkItem-ALLOW', 'positive.wa_app_runtime.update', 'pending-work-next-attempt-update',
     'Restricted App changed only next-attempt time on its separate genuinely scheduled pending work item.'),
)
CHILD = 'evidence/app-source8/app-write-two-results.json'
OUTER = 'evidence/run-evidence.json'
PINS = {
    'acceptance.json': 'af7258881decbf7d78f1c413a4283f64d7b0235d48c3c7f2200f8b683a69f7cc',
    'independent-closure.json': '39eb70917db0bffe61f2f6e0fb6f4f0741f7292d00ca4b73e31387ed7b71329a',
    'operation-exit.json': '4a8165503726b33722de649d38ad279bd5dfac1692368455b39094d2991ce027',
    'operation.json': IDENTITY['packet_sha256'],
    OUTER: '426bf87e47346532fc3f0998d71e415b131b103d56959c2a1757841f3a8e5e8c',
    CHILD: '00e0746f1f32c76dd7246a51192482c5647cef0f10c960c18478dc73b3a24f1a',
}
LIMIT = 'SOURCE8_SYNTHETIC_RESTRICTED_SQL_CRITERION_ONLY'
RAW_PASS = 'PASS_FINITE_TWO_APP_WRITE_CRITERIA_ONLY'


class EvidenceFailure(ValueError):
    """A known mismatch in the two-assertion App evidence boundary."""


def require(condition, reason):
    if not condition:
        raise EvidenceFailure(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(root, relative, expected):
    leaf = root / relative
    require(leaf.resolve(strict=True) == leaf and leaf.is_file(), 'Cloud App evidence must be a regular source file')
    raw = leaf.read_bytes()
    require(sha(raw) == expected, 'Cloud App evidence digest mismatch')
    return raw


def derive_bytes(root):
    root = Path(root).resolve(strict=True)
    files = {name: document(read(root, f'{ASSET}/{name}', digest)) for name, digest in PINS.items()}
    acceptance, audit = files['acceptance.json'], files['independent-closure.json']
    child, outer, observed = files[CHILD], files[OUTER], files['operation-exit.json']
    require(all(all(record[k] == v for k, v in IDENTITY.items()) for record in (acceptance, audit, child)),
            'Cloud App fixture or packet identity drift')
    require(acceptance['operator_exit_code'] == audit['operator_exit_code'] == observed['exit_code'] == 0
            and acceptance['independent_reviewer'] == audit['reviewer'] != observed['observer']
            and audit['status'] == child['status'] == observed['app_status'] == RAW_PASS
            and child['evidence_complete'] is True and observed['evidence_complete'] is True
            and observed['outer_evidence_sha256'] == PINS[OUTER]
            and outer['app_source8']['child_evidence_sha256'] == PINS[CHILD]
            and child['database_posture'] == acceptance['Posture'] == 'D'
            and acceptance['assertion_promotions'] == 0 and not child['unexpected'],
            'Cloud App operation closure, reviewer, or posture was not verified')
    native = audit['exact_native_and_ledger']
    require(all(value is True for value in audit['cleanup_verified'].values())
            and native['passed_after_same_fresh_target_full_noop'] is True
            and native['every_full_row_fingerprint_unchanged'] is True
            and native['native_snapshots_identical'] is True
            and [row['sha256'] for row in native['source_derived_migrations']] == [APPLICATION, APPEND]
            and len(child['results']) == 14, 'Cloud App source8 or cleanup proof missing')
    wanted = [f'{case}|{assertion}' for case, assertion, _, _ in SCOPES]
    require(acceptance['assertion_ceilings'] == audit['scope']['supported_assertion_ceilings'] == wanted
            and [row['claim'] for row in child['results'] if row['claim'] is not None] == wanted,
            'Only the two reviewed Cloud App assertions are supported')
    claims = []
    for case, assertion, recipe, scope in SCOPES:
        [row] = [row for row in child['results'] if row['claim'] == f'{case}|{assertion}']
        require(row['case'] == recipe and row['status'] == 'PASS_FINITE_APP_WRITE_PROTOCOL_ONLY'
                and row['operation_closed_before_observers'] is True
                and row['all_other_tables_unchanged'] is True and row['tables_observed'] == 42
                and row['complete_record_sequence_match'] is True, 'Cloud App operation evidence missing')
        claims.append({'case_id': case, 'assertion_id': assertion, 'status': 'PASS',
                       'qualification_scope': scope, 'qualification_limit': LIMIT, 'observation': row})
    record = {'schema': 'workinants.cloud-app-source8-qualified-evidence.v1', **IDENTITY, 'actual_result': KIND,
              'database_posture': 'D', 'migration_history': [APPLICATION, APPEND], 'pins': PINS, 'claims': claims}
    return (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf8')


def is_reference(row):
    return (row.get('evidence_path') == DERIVED or row.get('run_id') == IDENTITY['run_id']
            or row.get('evidence_sha256') == DERIVED_SHA or row.get('actual_result') == KIND)


def links():
    rows = [{'case_id': case, 'assertion_id': assertion, 'status': 'PASS',
             'expected_assertion_sha256': EXPECTED_ASSERTION, **IDENTITY, 'application_sql_sha256': APPLICATION,
             'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA, 'json_pointer': f'/claims/{index}',
             'qualification_scope': scope, 'qualification_limit': LIMIT}
            for index, (case, assertion, _, scope) in enumerate(SCOPES)]
    execution = {**IDENTITY, 'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA,
                 'actual_result': KIND, 'qualification_scope': LIMIT}
    return rows, execution


def propose_ledger_delta(previous, derived):
    require(sha(previous) == BASELINE_LEDGER and sha(derived) == DERIVED_SHA, 'Cloud App admission input drift')
    ledger = document(previous)
    rows, execution = links()
    identities = {(row['case_id'], row['assertion_id']) for row in ledger['assertions']}
    require(not identities.intersection((row['case_id'], row['assertion_id']) for row in rows)
            and not any(map(is_reference, ledger['assertions'] + ledger['executions'])), 'Cloud App asserts only new rows')
    ledger['assertions'].extend(rows)
    ledger['executions'].append(execution)
    return ledger


class QualificationBatch:
    def __init__(self, root, ledger):
        self.root = Path(root).resolve(strict=True)
        self.raw = read(self.root, DERIVED, DERIVED_SHA)
        require(self.raw == derive_bytes(self.root), 'Cloud App record does not reproduce')
        self.rows, execution = links()
        require([row for row in ledger['assertions'] if is_reference(row)] == self.rows
                and [row for row in ledger['executions'] if is_reference(row)] == [execution],
                'Cloud App ledger must identify exactly two rows and one execution')
        self.seen = set()

    def validate_claim(self, execution, row):
        require(row in self.rows and execution == document(self.raw), 'Cloud App claim reference mismatch')
        identity = (row['case_id'], row['assertion_id'])
        require(identity not in self.seen, 'Cloud App claim repeated')
        self.seen.add(identity)

    def verify_unchanged(self):
        require(len(self.seen) == len(self.rows) and read(self.root, DERIVED, DERIVED_SHA) == self.raw
                and derive_bytes(self.root) == self.raw, 'Cloud App claims or closed evidence changed during validation')
