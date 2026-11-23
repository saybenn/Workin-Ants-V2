"""Source-only ordered catalog; no database, process or network operations.

The caller provides the already compiled, pinned original catalog compiler and
the same captured input bytes it verified. Original source paths are never
rewritten to disguise a replacement as the old application packet.
"""
from copy import deepcopy
import hashlib
import json

INITIAL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
PATCH = '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7'
OLD_BODY = '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038'
NEW_BODY = 'dee63b1c682a3cdef8a125df691fa2d4a2ee163b7afc43f740ce04f8f41ae965'
OLD_EXPECTED = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
IDENTITY = 'platform_private.runtime_transition()'
PATCH_PATH = 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql'


def require(ok, code):
    if not ok:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def delta(old, new, path=''):
    """Exact recursive differences, including missing/extra fields and types."""
    if type(old) is not type(new):
        return [path]
    if isinstance(old, dict):
        result = []
        for key in sorted(set(old) | set(new)):
            if key not in old or key not in new:
                result.append(path + '/' + key)
            else:
                result.extend(delta(old[key], new[key], path + '/' + key))
        return result
    if isinstance(old, list):
        if len(old) != len(new):
            return [path]
        return [p for i, (a, b) in enumerate(zip(old, new))
                for p in delta(a, b, path + '/' + str(i))]
    return [] if old == new else [path]


def build_manifest(source, blobs, pins):
    """Consume bootstrap -> immutable initial -> exact append -> finalization."""
    paths = tuple(source.INPUTS)
    require(set(blobs) == set(paths) | {PATCH_PATH}, 'EXACT_NINE_CATALOG_INPUTS')
    require(all(type(raw) is bytes and pins.get(p) == sha(raw)
                for p, raw in blobs.items()), 'CATALOG_SAME_CAPTURED_BYTES')
    require(sha(blobs[paths[1]]) == INITIAL and sha(blobs[PATCH_PATH]) == PATCH,
            'EXACT_ORDERED_MIGRATION_BYTES')
    require(blobs[paths[2]] == blobs[paths[3]], 'FINALIZATION_SOURCE_IDENTITY')

    # Parse the append independently before it can change compiler state.
    statements = json.loads(source.parse_sql_json(blobs[PATCH_PATH].decode('utf8')))['stmts']
    kinds = [next(iter(row['stmt'])) for row in statements]
    require(kinds == ['TransactionStmt', 'VariableSetStmt', 'CreateFunctionStmt',
                      'VariableSetStmt', 'TransactionStmt'], 'EXACT_APPEND_ENVELOPE')
    first, role, function, reset, last = [row['stmt'][kind]
        for row, kind in zip(statements, kinds)]
    require(first['kind'] == 'TRANS_STMT_BEGIN' and last['kind'] == 'TRANS_STMT_COMMIT',
            'BARE_APPEND_TRANSACTION')
    require(role['name'] == reset['name'] == 'role' and role['kind'] == 'VAR_SET_VALUE'
            and role.get('is_local') is True and source.literal(role['args'][0]) == 'wa_schema_owner'
            and reset['kind'] == 'VAR_RESET', 'EXACT_APPEND_ROLE_ENVELOPE')
    require(function.get('replace') is True and
            source.names(function['funcname']) == ['platform_private', 'runtime_transition']
            and not function.get('parameters'), 'ONE_EXISTING_FUNCTION_REPLACEMENT')

    def compile_catalog(append):
        compiler = source.ManifestCompiler()
        compiler.consume(blobs[paths[0]].decode('utf8'), 'bootstrap')
        compiler.consume(blobs[paths[1]].decode('utf8'), 'application')
        require(compiler.functions[IDENTITY]['owner'] == 'wa_schema_owner',
                'EXISTING_FUNCTION_OWNER_REQUIRED')
        if append:
            compiler.consume(blobs[PATCH_PATH].decode('utf8'), 'append_runtime_lease_v1')
        compiler.consume(blobs[paths[2]].decode('utf8'), 'finalize')
        expected = compiler.result()
        models = json.loads(blobs[paths[5]])
        expected['model_register'] = models
        expected['prisma_declarations'] = source.prisma_crosscheck(
            blobs[paths[4]].decode('utf8'), expected, models)
        wanted = {row['object'] for row in models} | {
            'platform_private.identity_service_authorization',
            'platform_private.identity_service_receipt'}
        require(set(expected['tables']) == wanted, 'UNCHANGED42_TABLE_SET')
        source.validate_acl(expected, json.loads(blobs[paths[6]]), json.loads(blobs[paths[7]]))
        return expected

    before, expected = compile_catalog(False), compile_catalog(True)
    require(source.digest(before) == OLD_EXPECTED and
            before['functions'][IDENTITY]['body_sha256'] == OLD_BODY,
            'CANONICAL_INITIAL_EXPECTED_REQUIRED')
    function = expected['functions'][IDENTITY]
    require(function['body_sha256'] == NEW_BODY and function['owner'] == 'wa_schema_owner'
            and function['security_definer'] is False and function['strict'] is False
            and function['volatility'] == 'volatile' and function['parallel'] == 'unsafe'
            and type(function['cost']) is int and function['cost'] == 100,
            'EXACT_REPLACEMENT_PROPERTIES')
    adjusted = deepcopy(expected)
    # These are explicitly recorded SOURCE provenance, not omitted native facts.
    require(set(adjusted['statement_counts']) == set(before['statement_counts']) | {'append_runtime_lease_v1'}
            and adjusted['statement_counts']['append_runtime_lease_v1'] == {
                'CreateFunctionStmt': 1, 'TransactionStmt': 2, 'VariableSetStmt': 2},
            'EXACT_APPEND_SOURCE_STATEMENT_COUNTS')
    del adjusted['statement_counts']['append_runtime_lease_v1']
    require(delta(before, adjusted) == [
        '/functions/' + IDENTITY + '/body_sha256',
        '/functions/' + IDENTITY + '/definition_ast_sha256'],
        'ONLY_DECLARED_FUNCTION_SOURCE_CHANGE')
    worker = [row for row in json.loads(blobs[paths[6]]) if row['role'] == 'wa_worker']
    require(len(worker) == 32 and len(expected['triggers']) == 100, 'ACL32_GUARDS100_REQUIRED')
    fingerprints = {p: sha(raw) for p, raw in sorted(blobs.items())}
    counts = {name: len(expected[name]) for name in
              ('roles', 'schemas', 'tables', 'enums', 'functions', 'explicit_indexes', 'policies', 'triggers')}
    counts.update(columns=sum(len(t['columns']) for t in expected['tables'].values()),
                  constraints=sum(len(t['constraints']) for t in expected['tables'].values()),
                  constraint_indexes=sum(len(t['constraint_indexes']) for t in expected['tables'].values()))
    return {'format': 'workinants.expected-catalog.v1', 'case_id': 'P0C-CATALOG-01',
        'status': 'EXPECTED_ORDERED_SOURCE_ONLY_NATIVE_PARITY_NOT_RUN',
        'database_contacted': False, 'sql_executed': False, 'database_posture': 'D',
        'parser': source.pglast.__version__, 'approval_binding': 'ALL_INPUT_HASHES_VERIFIED',
        'inputs_sha256': fingerprints,
        'aggregate_recipe': 'SHA256(UTF8(sorted path + TAB + lowercase sha256 + LF))',
        'inputs_aggregate_sha256': sha(''.join(p + '\t' + h + '\n' for p, h in fingerprints.items()).encode()),
        'expected_sha256': source.digest(expected), 'counts': counts, 'expected': expected,
        'environment_assumptions': {
            'original_bootstrap_role': source.ORIGINAL_GRANTOR,
            'original_bootstrap_requires_superuser': True,
            'public_schema_owner': source.PUBLIC_SCHEMA_OWNER,
            'public_owner_resolution': 'independently registered native baseline; no default owner assumption',
            'object_grantor_rule': 'PostgreSQL17 superuser object GRANT is recorded as object owner; role memberships retain bootstrap grantor',
            'authority': 'https://www.postgresql.org/docs/17/sql-grant.html'},
        'ordered_source': {'initial_sha256': INITIAL, 'append_sha256': PATCH,
            'old_body_sha256': OLD_BODY, 'new_body_sha256': NEW_BODY,
            'source_only_difference_paths': delta(before, expected),
            'worker_acl_rows': 32, 'external_trigger_count': 100,
            'no_executable_effective_SQL_projection': True},
        'comparison_contract': {'exact_object_sets': True, 'compare_counts_only': False,
            'ignored_fields': ['native OIDs', 'source byte positions', 'ordering of unordered catalog result rows'],
            'required_normalization_review': ['native analyzed/deparsed expression casts and type resolution',
                'unnamed constraint and constraint-index names matched by complete semantics',
                'PostgreSQL-generated relation row/array types and internal FK triggers',
                'owner implicit privileges, acldefault, global plus additive schema defaults',
                'public schema baseline and separately owned Prisma migration ledger',
                'baseline built-in plpgsql extension versus application extension absence'],
            'unplanned_object_kinds_absent': ['views', 'materialized views', 'user sequences', 'application extensions'],
            'baseline_external_schemas': ['public', 'pg_catalog', 'information_schema'],
            'native_parity_status': 'NOT_RUN'}}
