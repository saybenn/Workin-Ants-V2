"""Source-bound genuine Prisma ledger exception, no runtime/database operations.

Pinned engine source defines expectations; observations never become a baseline.
Separate genuine CLI/provisioning/source-mount provenance remains mandatory.
Only the exact local fresh-ledger subset is supported, never hosted adoption.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import uuid

ROOT = Path(__file__).resolve().parents[2]
ENGINE = 'd1b3f377ca835d73fd50954a5e22128b9ebdd6b8'
PRISMA_VERSION = '7.10.1'
LEDGER = 'public._prisma_migrations'
OWNER = 'wa_migrator'
COLLECTOR = 'scripts/sql-review/collect_prisma_ledger.sql'
ADAPTER = 'scripts/sql-review/prisma_ledger_proof.py'
DIAGNOSTICS = 'scripts/sql-review/migration_server_diagnostics.py'
MASKED_MODE = 'ABORTED_TRANSACTION_FAILED_STEP_PERSISTENCE'
MASKED_CLASS = 'SERVER_42501_WITH_SECONDARY_25P02_UNWRITTEN_FAILURE_LOGS'
PREFIX = 'https://raw.githubusercontent.com/prisma/prisma-engines/' + ENGINE + '/'
AUTHORITIES = {
    'eight_column_ddl': PREFIX + 'schema-engine/connectors/sql-schema-connector/src/flavour/postgres.rs',
    'record_write_shapes': PREFIX + 'schema-engine/connectors/sql-schema-connector/src/sql_migration_persistence.rs',
    'one_success_step_per_script': PREFIX + 'schema-engine/commands/src/commands/apply_migrations.rs',
    'new_checksum_no_normalization': PREFIX + 'schema-engine/connectors/schema-connector/src/checksum.rs',
    'checksum_call': PREFIX + 'schema-engine/connectors/schema-connector/src/migration_persistence.rs',
    'pg17_table_privileges': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/include/utils/acl.h',
    'pg17_owner_and_world_defaults': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/utils/adt/acl.c',
    'pg17_catalog_only_lock': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/commands/lockcmds.c',
}
PRIVILEGES = ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER', 'MAINTAIN')
HASH = re.compile(r'^[0-9a-f]{64}$')
REG_FORMAT = 'workinants.prisma-ledger-registration.v1'
EVIDENCE_FORMAT = 'workinants.prisma-ledger-evidence.v1'
NATIVE_FORMAT = 'workinants.prisma-ledger-native.v1'


class LedgerProofError(ValueError): pass


def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def digest(value): return sha(canonical(value).encode('utf8'))
def text_hash(value): return sha(value.encode('utf8'))


def public_relation():
    return {'object': LEDGER, 'kind': 'r', 'owner': OWNER, 'rls': False, 'force_rls': False, 'nonowner_acl': []}


def schema_expectation():
    columns = []
    for ordinal, (name, typ, typmod, nullable, default) in enumerate((
        ('id', 'varchar', 40, False, None), ('checksum', 'varchar', 68, False, None),
        ('finished_at', 'timestamptz', -1, True, None), ('migration_name', 'varchar', 259, False, None),
        ('logs', 'text', -1, True, None), ('rolled_back_at', 'timestamptz', -1, True, None),
        ('started_at', 'timestamptz', -1, False, 'now()'), ('applied_steps_count', 'int4', -1, False, '0')), 1):
        columns.append({'name': name, 'ordinal': ordinal, 'type': 'pg_catalog.' + typ, 'typmod': typmod,
            'nullable': nullable, 'array_dimensions': 0, 'identity': '', 'generated': '',
            'collation_is_type_default': True, 'storage_is_type_default': True,
            'compression': '', 'is_local': True, 'inherited_count': 0,
            'default_sha256': text_hash(default) if default is not None else None})
    index = {'object': 'public._prisma_migrations_pkey', 'owner': OWNER, 'access_method': 'btree', 'persistence': 'p',
        'no_index_acl': True, 'no_options': True, 'default_tablespace': True,
        'unique': True, 'primary': True, 'valid': True, 'ready': True, 'live': True, 'immediate': True,
        'clustered': False, 'replica_identity': False, 'nulls_not_distinct': False,
        'key_count': 1, 'total_count': 1, 'no_expressions': True, 'no_predicate': True,
        'keys': [{'position': 1, 'column': 'id', 'included': False, 'opclass': 'pg_catalog.text_ops',
                  'opclass_default': True, 'collation_is_type_default': True, 'descending': False, 'nulls_first': False}]}
    return {'relations': [{'object': LEDGER, 'kind': 'r', 'owner': OWNER, 'persistence': 'p', 'access_method': 'heap',
            'rls': False, 'force_rls': False, 'replica_identity': 'd', 'no_options': True,
            'default_tablespace': True, 'not_partition': True, 'no_inheritance': True}],
        'columns': columns,
        'constraints': [{'name': '_prisma_migrations_pkey', 'kind': 'p', 'deferrable': False,
            'initially_deferred': False, 'validated': True, 'no_inherit': True, 'columns': ['id'],
            'index_name': 'public._prisma_migrations_pkey', 'no_referenced_relation': True, 'no_expression': True}],
        'indexes': [index], 'table_acl': sorted([{'grantee': OWNER, 'grantor': OWNER, 'privilege': privilege, 'grant_option': False}
            for privilege in PRIVILEGES], key=lambda item: (item['grantee'], item['grantor'], item['privilege'], item['grant_option'])),
        'column_acl': [], 'triggers_count': 0, 'policies_count': 0, 'rules_count': 0}


def _tool_pins(include_failure_diagnostics=False):
    engine_path = 'node_modules/@prisma/engines-version/package.json'
    prisma_path = 'node_modules/prisma/package.json'
    engine = json.loads((ROOT / engine_path).read_text(encoding='utf8'))
    prisma = json.loads((ROOT / prisma_path).read_text(encoding='utf8'))
    if engine.get('prisma', {}).get('enginesVersion') != ENGINE or prisma.get('version') != PRISMA_VERSION:
        raise LedgerProofError('pinned local tool source version mismatch')
    paths = (engine_path, prisma_path, ADAPTER, COLLECTOR) + ((DIAGNOSTICS,) if include_failure_diagnostics else ())
    return {path: sha((ROOT / path).read_bytes()) for path in paths}


def _validate_hash(value):
    if not isinstance(value, str) or HASH.fullmatch(value) is None: raise LedgerProofError('invalid hash')


def build_registration(migrations, *, run_id, target_attestation_sha256, source_expected_sha256,
                       root=ROOT, database='wa_p0c_rehearsal', failure_binding=None):
    """Predeclare exact source bytes/states. No native snapshot argument exists.

    migrations: [{path, migration_name, sha256, state, count}], paths relative to
    root, exact pinned migration.sql bytes, state applied/failed/rolled_back.
    Failed test-only copies must be independently retained under their own path.
    No resolve-applied/baseline adoption or line-ending fallback is supported.
    """
    if not isinstance(run_id, str) or str(uuid.UUID(run_id)) != run_id or database != 'wa_p0c_rehearsal': raise LedgerProofError('unregistered target')
    for value in (target_attestation_sha256, source_expected_sha256): _validate_hash(value)
    if not isinstance(migrations, list) or not migrations or len(migrations) > 16: raise LedgerProofError('bounded migration expectation list required')
    root = Path(root).resolve()
    history, seen, proof_hashes = [], set(), set()
    for row in migrations:
        if type(row) is not dict: raise LedgerProofError('migration expectation must be an object')
        base_fields = {'path', 'migration_name', 'sha256', 'state', 'count'}
        masked = row.get('failure_mode') == MASKED_MODE
        if set(row) != base_fields | ({'failure_mode', 'failure_proof_sha256'} if masked else set()): raise LedgerProofError('unsupported migration registration fields')
        path = PurePosixPath(row['path'])
        if path.is_absolute() or '\\' in row['path'] or any(part in ('', '.', '..') for part in path.parts): raise LedgerProofError('unsafe migration path')
        if path.name != 'migration.sql' or path.parent.name != row['migration_name'] or not re.fullmatch(r'[0-9]{14}_[a-z0-9_]+', row['migration_name']):
            raise LedgerProofError('migration name does not come from declared source directory')
        resolved = (root / row['path']).resolve()
        if not resolved.is_relative_to(root): raise LedgerProofError('source path escapes root')
        raw = resolved.read_bytes()
        raw.decode('utf8', errors='strict')  # Exact UTF8 bytes, no newline/BOM translation.
        _validate_hash(row['sha256'])
        if sha(raw) != row['sha256']: raise LedgerProofError('source checksum mismatch')
        if row['state'] not in ('applied', 'failed', 'rolled_back') or type(row['count']) is not int or not 1 <= row['count'] <= 4:
            raise LedgerProofError('unsupported history state/count')
        if masked:
            if row['state'] not in ('failed', 'rolled_back') or row['count'] != 1: raise LedgerProofError('masked persistence is one failed attempt only')
            _validate_hash(row['failure_proof_sha256'])
            if row['failure_proof_sha256'] in proof_hashes: raise LedgerProofError('failed attempt proof reused')
            proof_hashes.add(row['failure_proof_sha256'])
        identity = (row['migration_name'], row['sha256'], row['state'])
        if identity in seen: raise LedgerProofError('duplicate history expectation')
        seen.add(identity)
        applied = row['state'] == 'applied'
        safe = {'name_sha256': text_hash(row['migration_name']), 'checksum_sha256': text_hash(row['sha256']),
            'checksum_format_valid': True, 'id_is_uuid_v4': True, 'started': True, 'finished': applied,
            'rolled_back': row['state'] == 'rolled_back', 'time_order_valid': True,
            'steps': 1 if applied else 0, 'logs_state': 'NULL' if applied or masked else 'NONEMPTY'}
        history.extend([safe] * row['count'])
    if proof_hashes:
        fields = {'container_id', 'source_commit', 'source_tree', 'packet_sha256', 'module_sha256'}
        if type(failure_binding) is not dict or set(failure_binding) != fields: raise LedgerProofError('reviewed server proof binding required')
        for field in ('container_id', 'packet_sha256', 'module_sha256'): _validate_hash(failure_binding[field])
        for field in ('source_commit', 'source_tree'):
            if not isinstance(failure_binding[field], str) or re.fullmatch('[0-9a-f]{40}', failure_binding[field]) is None:
                raise LedgerProofError('server proof source identity required')
        if failure_binding['module_sha256'] != sha((ROOT / DIAGNOSTICS).read_bytes()): raise LedgerProofError('diagnostic module source mismatch')
    elif failure_binding is not None: raise LedgerProofError('server proof binding without masked expectation')
    registration = {'format': REG_FORMAT, 'engine_commit': ENGINE, 'prisma_version': PRISMA_VERSION,
        'run_id': run_id, 'database': database, 'target_attestation_sha256': target_attestation_sha256,
        'source_expected_sha256': source_expected_sha256, 'migrations': migrations,
        'history_expected': sorted(history, key=canonical), 'schema_spec_sha256': digest(schema_expectation()),
        'source_authorities': AUTHORITIES, 'tool_source_files_sha256': _tool_pins(bool(proof_hashes)),
        'scope': 'LOCAL_GENUINE_LEDGER_EXCEPTION_ONLY_NOT_CLI_OR_APPLICATION_PROVENANCE'}
    if proof_hashes: registration['failure_binding'] = failure_binding
    return registration


def _verify_masked_proofs(registration, proofs):
    """Independent source-error evidence is mandatory; ledger class is not cause."""
    wanted = {row['failure_proof_sha256']: row for row in registration['migrations'] if row.get('failure_mode') == MASKED_MODE}
    if type(proofs) is not list or len(proofs) != len(wanted): raise LedgerProofError('independent server proof missing')
    if len({digest(value) for value in proofs}) != len(proofs): raise LedgerProofError('duplicate server proof')
    if sha((ROOT / DIAGNOSTICS).read_bytes()) != registration['failure_binding']['module_sha256']:
        raise LedgerProofError('diagnostic source drift')
    try:
        module = runpy.run_path(str(ROOT / DIAGNOSTICS))
        validator = module['validate_proof']
    except Exception: raise LedgerProofError('reviewed server proof validator unavailable') from None
    for value in proofs:
        row = wanted.get(digest(value))
        if row is None: raise LedgerProofError('server proof does not match predeclared artifact')
        try: validator(value)
        except Exception: raise LedgerProofError('invalid independent server error proof') from None
        expected = {'run_id': registration['run_id'], **registration['failure_binding'],
            'migration_id': row['migration_name'], 'application_sql_sha256': row['sha256']}
        if any(type(value.get(key)) is not str or value[key] != item for key, item in expected.items()):
            raise LedgerProofError('server proof target or source binding mismatch')
        if value.get('classification') != MASKED_CLASS or value.get('failed_row_logs_state') != 'NULL':
            raise LedgerProofError('masked server proof classification required')


def compare_proof(registration, evidence, native, *, bootstrap_grantor, source_expected_sha256, root=ROOT):
    """Compare safe native metadata to fixed source rules; return hashed findings.

    The root-owned reviewed wrapper supplies evidence binding registration hash,
    collector hash/run/target attestation and equal pre/post main catalog hashes.
    It must establish actual target and genuine-CLI provenance independently.
    """
    findings = []
    def check(field, wanted, actual):
        expected_hash, actual_hash = digest(wanted), digest(actual)
        findings.append({'field': field, 'status': 'PASS' if expected_hash == actual_hash else 'FAIL',
            'expected_sha256': expected_hash, 'actual_sha256': actual_hash})
    try:
        if not isinstance(registration, dict): raise LedgerProofError('registration required')
        rebuilt = build_registration(registration['migrations'], run_id=registration['run_id'],
            target_attestation_sha256=registration['target_attestation_sha256'], source_expected_sha256=source_expected_sha256,
            root=root, database=registration['database'], failure_binding=registration.get('failure_binding'))
        check('source-bound-registration', rebuilt, registration)
        if rebuilt != registration: return {'status': 'FAIL', 'checks': findings}
    except (LedgerProofError, KeyError, TypeError, ValueError, OSError):
        check('source-bound-registration', True, False)
        return {'status': 'FAIL', 'checks': findings}
    if evidence is None:
        findings.append({'field': 'native-ledger-observation-required', 'status': 'INCOMPLETE',
                         'expected_sha256': None, 'actual_sha256': None})
        return {'status': 'INCOMPLETE', 'checks': findings}
    try:
        required = {'format', 'registration_sha256', 'collector_sql_sha256', 'run_id', 'target_attestation_sha256',
                    'native_catalog_before_sha256', 'native_catalog_after_sha256', 'observation'}
        masked = 'failure_binding' in registration
        if masked: required.add('failed_step_persistence_proofs')
        if not isinstance(evidence, dict) or set(evidence) != required: raise LedgerProofError('malformed evidence envelope')
        if masked:
            _verify_masked_proofs(registration, evidence['failed_step_persistence_proofs'])
            check('independent-server-failed-step-persistence-proof', True, True)
        expected_binding = {key: value for key, value in evidence.items() if key not in ('observation', 'failed_step_persistence_proofs')}
        actual_binding = {'format': EVIDENCE_FORMAT, 'registration_sha256': digest(registration),
            'collector_sql_sha256': registration['tool_source_files_sha256'][COLLECTOR], 'run_id': registration['run_id'],
            'target_attestation_sha256': registration['target_attestation_sha256'],
            'native_catalog_before_sha256': digest(native), 'native_catalog_after_sha256': digest(native)}
        check('same-run-collector-and-catalog-binding', actual_binding, expected_binding)
        got = evidence['observation']
        if not isinstance(got, dict): raise LedgerProofError('malformed native observation')
        spec = schema_expectation()
        top_keys = set(spec) | {'format', 'server_version_num', 'database', 'read_only', 'isolation', 'collected_as',
                              'session_user', 'collector_is_superuser', 'history', 'history_ids_unique'}
        check('complete-observation-fields', sorted(top_keys), sorted(got))
        for key, value in {'format': NATIVE_FORMAT, 'server_version_num': 170011, 'database': registration['database'],
                           'read_only': True, 'isolation': 'repeatable read', 'collected_as': bootstrap_grantor,
                           'session_user': bootstrap_grantor, 'collector_is_superuser': True, 'history_ids_unique': True}.items():
            check(key, value, got.get(key))
        for key, value in spec.items(): check('exact-' + key, value, got.get(key))
        history = got.get('history')
        if not isinstance(history, list): raise LedgerProofError('history visibility missing')
        check('complete-source-checksum-and-state-history', Counter(map(canonical, registration['history_expected'])), Counter(map(canonical, history)))
    except (LedgerProofError, KeyError, TypeError, ValueError):
        check('complete-sanitized-native-evidence', True, False)
    return {'status': 'FAIL' if any(row['status'] == 'FAIL' for row in findings) else 'PASS', 'checks': findings}
