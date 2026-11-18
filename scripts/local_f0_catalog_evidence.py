"""Pure assertion mapping for the independently audited 23bd catalog run.

This exact-record adapter permits thirteen catalog metadata assertions and one
private-ledger assertion. It never qualifies the adversarial vector or a whole
case. The actual native comparator, 416-expression oracle and 22-check ledger
proof were independently recomputed before these immutable bytes were accepted;
the separate audit SHA is 9ba3bcb59439c29c21df56a27a858f53bf69ffb3eea39dd824610d34ea51cbdb.

Every retained asset and all 78 source files are rehashed on every validation.
The final canonical record pin also refuses unmodeled narrative or secret fields.
Counts and PASS labels alone cannot qualify anything. No operator snapshot is
imported and no database, subprocess, Git or network operation is performed.
"""
import hashlib
import json
from pathlib import Path
import re

RESULT = 'PASS_LOCAL_NATIVE_CATALOG_SUBSET_ONLY'
RUN = '23bd8979-53ba-43af-ad77-8bba1900f163'
COMMIT = 'b9703d77792fa328392cf698a23e9c07c0adc6b1'
TREE = '2a40c3a1fc4d7f49daeae9d4554e4b026880d3d8'
PACKET = '8ec1bd586b527bbf47167c8b1da44c9e008541dc2f5707e8d142e471f2329f1c'
SQL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
MIGRATION = '20261117000100_f0_local_initial'
SOURCE_EXPECTED = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
NATIVE = 'a048478f5e834dc1686b558954ea9bdaeaba4278afcf63976510c114680f1fc6'
NATIVE_FILE = 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8'
REPORT_SHA = '5228f14580fbb32181017c17f73523d4db42fc062a98f894f53269e84ae047ef'
EXECUTION_CANONICAL_SHA = '98c153cf6e6b3eb011ced649cbc6eaa7afff2b0732eb67567afbabb72d94b2f9'
ASSETS = 'context/reconciliation/local-f0-run-assets/b9703d7-native-catalog-23bd8979'
TARGET = 'wa-p0c-23bd8979-catalog'
CID = 'd541ac87d7094d5063c283709b8169c75d63b200a72b3006afb71c63bc5d60df'
TOOL_PACKAGES = {
    'node_modules/@prisma/engines-version/package.json': '2dd9793255d6bbb5c399a624ecbfb6323d39233860863d172946b7f750f528bd',
    'node_modules/prisma/package.json': '6cdfef6df08d9a37f28908855797fe8bfc97a2d3d886a8d5cbe2e502d6848151',
}
SNAPSHOTS = {
    'operation-manifest.json': '92cca48f0e8e24c35f1de5fe2b635a229adf2731376a5e91cd33c91071d51be5',
    'operational-review.json': 'b44b28016dd20fa240ae70c5e0adfdf15cb8e55c3578432d1a4a376b791bcba5',
    'ok-migration-manifest.json': '325e9b31f83f22fa2537e9bdfdefbe41077fa1641c299340792e4cc5ed0a91a9',
    'ok-history-manifest.json': '595700b550b6c2e8cbc8502b479e6e8223f00702ef28620d525a438fbdccc6fb',
    'authentication-ok.json': 'b6023cb94e75efba76302dd213c20385bef993a2b741c8acc1cfc82309809a49',
    'acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
    'text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
    'native-before.json': NATIVE_FILE,
    'oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
    'oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
    'oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
    'oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
    'ledger-registration.json': '9f977133b5a4e382be1b2220901c9b6ddd4a97f72e948b8e5841200f2a6b2ece',
    'ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
    'ledger-evidence.json': 'f1cebfb4276c5aee2b634d246d746680a0b89c69dbb38eb703819d92a13ff24f',
    'catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
}
CATALOG_ASSERTIONS = {
    'control.relations_columns': 'ea678801b4ec5206ea54fb451e9cd35fa2a1526fd8d159141714fdd8cf33b784',
    'control.enums': '73a01d601c63406c798316bd174bea010ebe84c9f2953ff5b263683d5f13f7f5',
    'control.constraints': '5dd47b1fc27bf8c768725f863c33090ab0f0fe51a5f3b5df79ed7ecf01e233bf',
    'control.indexes': 'eb82e972660eb4fa67016c3db1efbd0595cd0cc56ab7f420f038ea55ffe43c66',
    'control.functions': 'be212c2e0208e4e45f97cc3da3c35ddec5e17e60dc3cb693bf933f6f22b66e2e',
    'control.triggers': '8671ea465e9a2e8cfe48378541d89d1a9337ab86e393f26f3069397de22b58f7',
    'control.views': 'a8e48c88b153305b32f055f3f9af56d57927957a9921652e53ea5a018af715d7',
    'control.roles_memberships': '6b539ade4cb960f53a53f1586ed2dd8b5ea6e75902133f4cff022728e86870c4',
    'control.all_acl_levels': 'b9f72da266f62f91e17b50a62d2c2b0dd78e0bf68dea208925d8173e6ec47de9',
    'control.rls_policies': 'be4faa963c10865331b9b1aa17b57b3e10b5931cc20cc9184d3344334f7461fe',
    'control.extensions': '9153b85ff96777d7c71db7e6fe1af7b0032eb38fc1471b966e4688e5572c8a32',
    'control.visibility': '4239bf941657c965aa02a1d77140f2011c908e4e04697e4a3af98ca806eda326',
    'vector.CATALOG-LEAVES.positive': '549d007c9e629c6d19812b0ed16be6f436aff3b0bd0156fb033f3be1539fa553',
}
CLAIMS = {('P0C-CATALOG-01', key): 'PASS' for key in CATALOG_ASSERTIONS}
CLAIMS[('P0C-INSTALL-01', 'control.private_ledger')] = 'PASS'
ASSERTION_HASHES = {('P0C-CATALOG-01', key): value for key, value in CATALOG_ASSERTIONS.items()}
ASSERTION_HASHES[('P0C-INSTALL-01', 'control.private_ledger')] = '3b6451de84c55481a914642694b664e9e8f6712f47af555b8b123be359141159'
STEPS = {
    'CATALOG-SETUP': 'PASS', 'CATALOG-AUTH': 'PASS', 'CATALOG-TOOLS': 'PASS',
    'CATALOG-INSTALL': 'PASS', 'CATALOG-ACL-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
    'CATALOG-TEXT-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
    'CATALOG-NATIVE': 'PASS_OBSERVED_NOT_QUALIFIED',
    'CATALOG-ORACLE': 'PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE',
    'CATALOG-LEDGER': 'PASS_SOURCE_BOUND_NATIVE_SUBSET',
    'CATALOG-COMPARE': 'PASS_SOURCE_BOUND_NATIVE_CATALOG_ONLY',
    'CATALOG-SANITIZED_EXPORT': 'PASS', 'CATALOG-CLEANUP': 'PASS',
}
RECORD_FIELDS = {
    'recorded_at', 'local_date', 'timezone', 'actual_result', 'scope', 'source_commit',
    'source_tree', 'packet_sha256', 'run_id', 'application_sql_sha256',
    'safe_raw_report_sha256', 'snapshot_files_sha256', 'identical_native_snapshot_files_sha256',
    'qualified_native_canonical_sha256', 'catalog_comparison', 'actual_steps', 'unexpected',
    'sanitized_report', 'historical_distinction', 'limits',
}


class EvidenceFailure(ValueError):
    """Evidence content never escapes in an exception or diagnostic."""


def _need(value, code):
    if not value:
        raise EvidenceFailure(code)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def _same(value, expected, code):
    _need(_json(value) == _json(expected), code)


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _digest(value):
    return _hash(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8'))


def _read(root, relative, expected):
    _need(type(relative) is str and '\\' not in relative and ':' not in relative and not relative.startswith('/') and all(p not in ('', '.', '..') for p in relative.split('/')), 'CATALOG_EVIDENCE_PATH')
    path = (root / relative).resolve(strict=True)
    _need(path.is_relative_to(root), 'CATALOG_EVIDENCE_PATH')
    raw = path.read_bytes()
    _need(_hash(raw) == expected, 'CATALOG_EVIDENCE_FILE_HASH')
    return raw


def _require_assertion(root, case_id, assertion_id):
    inventory = json.loads((root / 'context/reconciliation/local-f0-assertions.json').read_bytes())
    found = [a for c in inventory['cases'] if c['id'] == case_id for a in c['assertions'] if a['id'] == assertion_id]
    _need(len(found) == 1 and found[0]['mandatory_for_case'] is True and found[0]['availability'] == 'CANDIDATE_LOCAL_SQL_PATH', 'CATALOG_ASSERTION_REQUIREMENT')
    _same(_hash(found[0]['expected_assertion'].encode('utf8')), ASSERTION_HASHES[(case_id, assertion_id)], 'CATALOG_ASSERTION_REQUIREMENT')


def _snapshots(root, execution):
    paths = {ASSETS + '/' + name: digest for name, digest in SNAPSHOTS.items()}
    _same(execution['snapshot_files_sha256'], paths, 'CATALOG_SNAPSHOT_BINDING')
    return {name: json.loads(_read(root, ASSETS + '/' + name, digest)) for name, digest in SNAPSHOTS.items()}


def _source(root, execution, report, snapshots):
    for key, value in {'run_id': RUN, 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET, 'application_sql_sha256': SQL}.items():
        _same(execution[key], value, 'CATALOG_SOURCE_IDENTITY')
    for key, value in {'run_id': RUN, 'approved_commit': COMMIT, 'approved_tree': TREE, 'approved_packet_sha256': PACKET}.items():
        _same(report[key], value, 'CATALOG_REPORT_IDENTITY')
    manifest = snapshots['operation-manifest.json']
    _same(report['run_manifest'], manifest, 'CATALOG_MANIFEST_BINDING')
    _same(report['run_manifest_sha256'], SNAPSHOTS['operation-manifest.json'], 'CATALOG_MANIFEST_BINDING')
    hashes = manifest['packet_files_sha256']
    _need(type(hashes) is dict and len(hashes) == 78 and all(type(k) is str and type(v) is str and re.fullmatch('[0-9a-f]{64}', v) for k, v in hashes.items()), 'CATALOG_PACKET_FIELDS')
    _same(_hash(''.join(p + '\0' + hashes[p] + '\n' for p in sorted(hashes)).encode('utf8')), PACKET, 'CATALOG_PACKET_AGGREGATE')
    _same(report['source_verification'], {'commit': COMMIT, 'tree': TREE, 'packet_sha256': PACKET, 'files_sha256': hashes, 'file_count': 78}, 'CATALOG_SOURCE_VERIFICATION')
    for relative, digest in hashes.items():
        _read(root, relative, digest)
    _need(report['packet_unchanged_after_run'] is True and report['tool_source_data_unchanged_after_run'] is True, 'CATALOG_SOURCE_PRESERVATION')
    _same(manifest['catalog']['tool_source_files_sha256'], TOOL_PACKAGES, 'CATALOG_TOOL_PACKAGE_BINDING')
    # This preserved checkout intentionally junctions node_modules to the
    # original Windows checkout. Only these two fixed, byte-pinned JSON files
    # may cross that junction; ordinary source/evidence paths remain root-bound.
    for relative, digest in TOOL_PACKAGES.items():
        _same(_hash((root / relative).read_bytes()), digest, 'CATALOG_TOOL_PACKAGE_HASH')
    for relative in ('review-output/foundation-application.review.sql', 'prisma/foundation/migrations/' + MIGRATION + '/migration.sql'):
        _same(hashes[relative], SQL, 'CATALOG_SQL_IDENTITY')


def _proofs(root, execution, report, snapshots):
    expected = json.loads(_read(root, 'review-output/native-catalog/expected.json', report['run_manifest']['packet_files_sha256']['review-output/native-catalog/expected.json']))
    _same(_digest(expected['expected']), SOURCE_EXPECTED, 'CATALOG_EXPECTED_SOURCE')
    native = snapshots['native-before.json']
    _same(_digest(native), NATIVE, 'CATALOG_NATIVE_IDENTITY')
    _same(execution['qualified_native_canonical_sha256'], NATIVE, 'CATALOG_NATIVE_IDENTITY')
    _same(report['qualified_native_snapshot_sha256'], NATIVE, 'CATALOG_NATIVE_IDENTITY')
    _same(execution['identical_native_snapshot_files_sha256'], {n: NATIVE_FILE for n in ('native-before.json', 'native-after-oracle.json', 'native-after-ledger.json')}, 'CATALOG_NATIVE_PRESERVATION')
    _same(report['native_snapshots'], [{'stage': stage, 'status': 'OBSERVED_NOT_QUALIFIED', 'native_sha256': NATIVE, 'artifact': name, 'artifact_sha256': NATIVE_FILE} for stage, name in [('NATIVE_BEFORE_ORACLE', 'native-before.json'), ('NATIVE_AFTER_ORACLE', 'native-after-oracle.json'), ('NATIVE_AFTER_LEDGER', 'native-after-ledger.json')]], 'CATALOG_NATIVE_PRESERVATION')
    comparison = snapshots['catalog-comparison.json']
    _same(execution['catalog_comparison'], comparison, 'CATALOG_COMPARATOR_BINDING')
    _same(report['catalog_comparison'], comparison, 'CATALOG_COMPARATOR_BINDING')
    for key, value in {'status': 'PASS', 'source_expected_sha256': SOURCE_EXPECTED, 'native_snapshot_sha256': NATIVE, 'check_counts': {'PASS': 29089}, 'findings': [], 'database_contacted_by_comparator': False, 'database_posture': 'D'}.items():
        _same(comparison[key], value, 'CATALOG_COMPARATOR_RESULT')
    oracle = snapshots['oracle-evidence.json']
    for key, name in [('preflight', 'oracle-preflight.json'), ('results', 'oracle-results.json'), ('closure', 'oracle-closure.json')]:
        _same(oracle[key], snapshots[name], 'CATALOG_ORACLE_BINDING')
    _need(oracle['connection_closed_before_observation'] is True and all(v is True for v in oracle['preflight']['outcomes'].values()) and oracle['closure']['all_oracle_tables_absent'] is True and oracle['closure']['all_oracle_functions_absent'] is True, 'CATALOG_ORACLE_CLOSURE')
    _same(oracle['pre_oracle_catalog_sha256'], NATIVE, 'CATALOG_ORACLE_PRESERVATION')
    _same(oracle['post_rollback_catalog_sha256'], NATIVE, 'CATALOG_ORACLE_PRESERVATION')
    registration = snapshots['ledger-registration.json']
    observation = snapshots['ledger-observation.json']
    evidence = snapshots['ledger-evidence.json']
    _same(evidence['observation'], observation, 'CATALOG_LEDGER_BINDING')
    for key, value in {'run_id': RUN, 'source_expected_sha256': SOURCE_EXPECTED, 'database': 'wa_p0c_rehearsal', 'migrations': [{'path': 'prisma/foundation/migrations/' + MIGRATION + '/migration.sql', 'migration_name': MIGRATION, 'sha256': SQL, 'state': 'applied', 'count': 1}]}.items():
        _same(registration[key], value, 'CATALOG_LEDGER_SOURCE')
    history = [{'name_sha256': _hash(MIGRATION.encode()), 'checksum_sha256': _hash(SQL.encode()), 'checksum_format_valid': True, 'id_is_uuid_v4': True, 'started': True, 'finished': True, 'rolled_back': False, 'time_order_valid': True, 'steps': 1, 'logs_state': 'NULL'}]
    _same(registration['history_expected'], history, 'CATALOG_LEDGER_HISTORY')
    _same(observation['history'], history, 'CATALOG_LEDGER_HISTORY')
    acl = [{'grantee': 'wa_migrator', 'grantor': 'wa_migrator', 'privilege': p, 'grant_option': False} for p in ('DELETE', 'INSERT', 'MAINTAIN', 'REFERENCES', 'SELECT', 'TRIGGER', 'TRUNCATE', 'UPDATE')]
    _same(observation['table_acl'], acl, 'CATALOG_LEDGER_PRIVACY')
    _same(observation['column_acl'], [], 'CATALOG_LEDGER_PRIVACY')
    _same([r['owner'] for r in observation['relations']], ['wa_migrator'], 'CATALOG_LEDGER_PRIVACY')
    proof = report['ledger_comparison']
    _need(proof['status'] == 'PASS' and len(proof['checks']) == 22 and all(c['status'] == 'PASS' and c['expected_sha256'] == c['actual_sha256'] for c in proof['checks']), 'CATALOG_LEDGER_PROOF')


def _operations_and_cleanup(report, snapshots):
    _need(len(report['migration_operations']) == 1, 'CATALOG_OPERATION_SET')
    operation = report['migration_operations'][0]
    for key, value in {'target': TARGET, 'stage': 'CATALOG_GENUINE_INITIAL_DEPLOY', 'operation': 'deploy', 'exit_code': 0, 'run_id': RUN, 'container_id': CID, 'source_sql_sha256': SQL, 'raw_output_discarded': True, 'database_qualification_claimed': False}.items():
        _same(operation[key], value, 'CATALOG_INSTALLATION_BINDING')
    _same(sorted(report['targets']), [TARGET], 'CATALOG_TARGET_SET')
    target = report['targets'][TARGET]
    _same(target['container_id'], CID, 'CATALOG_TARGET_IDENTITY')
    _same(target['connections_before_finalization'], {'migrator': 0, 'tagged_other_clients': 0}, 'CATALOG_FINALIZATION')
    _same(target['finalization_observation'], {'auth': 'scram-sha-256:postgres', 'grantor': 'postgres', 'leaf_create': dict.fromkeys(('wa_track_verifier', 'wa_customer_verifier', 'wa_private_helper_owner'), False), 'remaining_memberships': 0, 'active_install_connections': 0}, 'CATALOG_FINALIZATION')
    auth = snapshots['authentication-ok.json']
    _need(auth['status'] == 'PASS_PREFLIGHT_ONLY' and auth['results'] == [] and auth['failure'] is None and len(auth['authentication']) == 6 and all(r['correct_password'] == 'PASS_SCRAM' and r['wrong_password'] == 'PASS_REJECTED' and type(r['wrong_password_exit_code']) is int and r['wrong_password_exit_code'] == 2 for r in auth['authentication']), 'CATALOG_AUTHENTICATION')
    stages = ('CATALOG_ACL_COMPATIBILITY', 'CATALOG_TEXT_COMPATIBILITY', 'NATIVE_BEFORE_ORACLE', 'EXPRESSION_ORACLE', 'NATIVE_AFTER_ORACLE', 'PRISMA_LEDGER_NATIVE', 'NATIVE_AFTER_LEDGER')
    _same([r['stage'] for r in report['catalog_operations']], list(stages), 'CATALOG_QUERY_SET')
    _same(report['backend_closures'], [{'stage': s, 'migrator_zero': True, 'tagged_clients_zero': True} for s in stages], 'CATALOG_BACKEND_CLOSURE')
    for operation in report['catalog_operations']:
        for key, value in {'exit_code': 0, 'client_exited': True, 'sqlstates': [], 'unexpected_stderr': False, 'raw_output_discarded': True}.items():
            _same(operation[key], value, 'CATALOG_QUERY_CLOSURE')
    _same(report['cleanup'], {TARGET: {'removed': True, 'verified_id': CID, 'name_and_both_labels_verified': True}, TARGET + '-data': {'removed': True, 'name_labels_creation_identity_verified': True}}, 'CATALOG_CLEANUP_IDENTITY')
    _same(report['cleanup_summary'], {'resource_presence_after': {TARGET: False, TARGET + '-data': False}, 'test_owned_secret_files_deleted': ['ok-bootstrap-password'], 'private_directory_absent': True, 'image_removed': False, 'unrelated_resources_changed': False}, 'CATALOG_CLEANUP_ABSENCE')
    _same(report['host_secret_cleanup'], {'deleted': ['ok-bootstrap-password'], 'private_directory_absent': True}, 'CATALOG_SECRET_CLEANUP')
    _same(report['sanitization'], {'files_scanned': 16, 'actual_password_values_found': False, 'unrestricted_subprocess_output_persisted': False, 'raw_context_handles_persisted': False, 'coordinator_evidence_uses_reviewed_allowlist': True}, 'CATALOG_SANITIZATION')


def validate_claim(case_id, assertion_id, status, execution, root):
    """Return True only for one of fourteen exact, independently audited claims.

    The caller must still bind its evidence row to the reviewed record bytes and
    aggregate whole-case status from every mandatory assertion. This function
    returns no whole-case, adversarial, activation or hosted-readiness claim.
    """
    try:
        _need(all(type(v) is str for v in (case_id, assertion_id, status)), 'CATALOG_CLAIM_FIELDS')
        _need(CLAIMS.get((case_id, assertion_id)) == status, 'CATALOG_CLAIM_NOT_SUPPORTED')
        _need(type(execution) is dict and execution.get('actual_result') == RESULT, 'CATALOG_RECORD_KIND')
        _need(set(execution) == RECORD_FIELDS, 'CATALOG_RECORD_FIELDS')
        _same(execution['scope'], 'ACTUAL_SOURCE_BOUND_NATIVE_CATALOG_ORACLE_AND_PRIVATE_LEDGER_SUBSET', 'CATALOG_RECORD_SCOPE')
        _same(execution['actual_steps'], STEPS, 'CATALOG_STEPS')
        _same(execution['unexpected'], [], 'CATALOG_UNEXPECTED')
        root = Path(root).resolve(strict=True)
        _require_assertion(root, case_id, assertion_id)
        report = execution['sanitized_report']
        _need(type(report) is dict and report['status'] == RESULT, 'CATALOG_REPORT_KIND')
        _same(report['steps'], STEPS, 'CATALOG_STEPS')
        _same(report['unexpected'], [], 'CATALOG_UNEXPECTED')
        _same(report['limits'], {'posture': 'D', '451_register': 'NOT_PROMOTED', '94_selection': 'NOT_PROMOTED', 'hosted_changes': False, 'migration_adoption': False, 'worker_loop': False, 'production_readiness': False}, 'CATALOG_SCOPE_HOLD')
        snapshots = _snapshots(root, execution)
        _source(root, execution, report, snapshots)
        _proofs(root, execution, report, snapshots)
        _operations_and_cleanup(report, snapshots)
        _same(execution['safe_raw_report_sha256'], REPORT_SHA, 'CATALOG_RETAINED_REPORT_HASH')
        _same(_hash((json.dumps(report, indent=2) + '\n').encode('utf8')), REPORT_SHA, 'CATALOG_RETAINED_REPORT_HASH')
        _same(_hash(_json(execution).encode('utf8')), EXECUTION_CANONICAL_SHA, 'CATALOG_RETAINED_EXECUTION_HASH')
        return True
    except EvidenceFailure:
        raise
    except BaseException:
        raise EvidenceFailure('CATALOG_EVIDENCE_REJECTED') from None
