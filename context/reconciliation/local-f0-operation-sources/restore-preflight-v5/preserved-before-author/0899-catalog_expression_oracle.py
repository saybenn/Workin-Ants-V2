#!/usr/bin/env python3
"""Prepare a source-derived, rollback-only PG17 expression normalization packet.

SOURCE ONLY: this module never executes SQL or contacts Docker/a database. The
default command prints a review plan; --emit-sql requires a complete input pin
map and exact local database/bootstrap identity. The root operator must review
the generated SQL/run manifest independently before execution.

Only source-AST expressions are installed on empty TEMP shadow tables. Original
tables, triggers, constraints, policies, functions and migration history are
untouched. There are no row INSERT/UPDATE/DELETE/SELECT operations. Catalog-only
preflight verifies the original types/functions before expression compilation.
Expected hashes come from SOURCE-created objects, never observed definitions.

Compilation can fold immutable constant expressions: fixed builtin calls and
the reviewed application call set below are therefore mandatory, as are exact
function-body/header, server, type and no-event-trigger checks. Whole-row refs,
subqueries and arbitrary functions fail closed before any SQL is generated.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from pglast.stream import RawStream

import catalog_manifest as source
import compare_native_catalog as compare


BUILTIN_CALLS = {'convert_to', 'encode', 'jsonb_build_object', 'jsonb_typeof',
                 'length', 'pg_backend_pid', 'pg_current_xact_id', 'sha256'}
SQL_VALUE_FUNCTIONS = {'SVFOP_CURRENT_TIMESTAMP', 'SVFOP_SESSION_USER'}
FORBIDDEN_NODES = {'SubLink', 'SelectStmt', 'RangeVar', 'ParamRef', 'A_Star',
                   'SQLNextValueExpr', 'CurrentOfExpr', 'SetToDefault'}
SOURCE_MODULES = ('scripts/sql-review/catalog_manifest.py',
                  'scripts/sql-review/compare_native_catalog.py',
                  'scripts/sql-review/pg17_catalog_rules.py',
                  'scripts/sql-review/catalog_expression_oracle.py',
                  'scripts/sql-review/collect_native_catalog.sql')


def ident(value):
    return '"' + value.replace('"', '""') + '"'


def literal(value):
    return "'" + value.replace("'", "''") + "'"


def native_type_sql(info):
    schema, name = info['name'].split('.')
    result = ident(schema) + '.' + ident(name)
    if info['typmods_ast']:
        result += '(' + ','.join(str(source.literal(v)) for v in info['typmods_ast']) + ')'
    return result + '[]' * info['array_dimensions']


def _application_calls(expected):
    approved = {'platform_private.row_allowed', 'platform_private.worker_track_allowed'}
    approved |= {f['name'] for f in expected['functions'].values()
                 if f['name'].startswith('platform_private.json_') and f['volatility'] == 'immutable'}
    return approved


def validate_expression(ast, columns, expected):
    application_calls = _application_calls(expected)
    calls = set()

    def visit(value):
        if isinstance(value, list):
            for child in value:
                visit(child)
            return
        if not isinstance(value, dict):
            return
        if set(value) & FORBIDDEN_NODES:
            raise source.ManifestError('unsupported expression execution/reference form')
        if 'ColumnRef' in value:
            fields = value['ColumnRef'].get('fields', [])
            if len(fields) != 1 or 'String' not in fields[0] or fields[0]['String']['sval'] not in columns:
                raise source.ManifestError('whole-row/foreign/unknown column reference')
        if 'FuncCall' in value:
            call = '.'.join(source.names(value['FuncCall']['funcname']))
            builtin = call.removeprefix('pg_catalog.')
            if call not in application_calls and not (builtin in BUILTIN_CALLS and ('.' not in call or call.startswith('pg_catalog.'))):
                raise source.ManifestError('function outside reviewed expression call set')
            calls.add(call)
        if 'SQLValueFunction' in value and value['SQLValueFunction']['op'] not in SQL_VALUE_FUNCTIONS:
            raise source.ManifestError('SQL value function outside reviewed expression set')
        if 'A_Expr' in value:
            name = source.names(value['A_Expr']['name'])
            if len(name) > 1 and name[0] != 'pg_catalog':
                raise source.ManifestError('operator outside pg_catalog')
        if 'TypeCast' in value:
            typ = source.typename(value['TypeCast']['typeName'])['name']
            if typ not in expected['enums'] and not (typ.startswith('pg_catalog.') and typ.split('.')[1] in source.BUILTINS):
                raise source.ManifestError('cast input type outside reviewed builtin/enum set')
        for child in value.values():
            visit(child)

    visit(ast)
    text = RawStream()(compare._ast_node(ast))
    if compare.expression_ast(text) != ast:
        raise source.ManifestError('expression AST did not byte-position-free reproduce')
    return text, calls


def expression_entries(expected):
    entries = []
    calls = set()
    for table, info in sorted(expected['tables'].items()):
        columns = set(info['columns'])
        for name, col in info['columns'].items():
            if col['collation_ast'] is not None:
                raise source.ManifestError('explicit shadow column collation requires separate review')
            if col['default'] is not None:
                text, used = validate_expression(col['default']['ast'], set(), expected)
                calls |= used
                entries.append({'category': 'columns', 'subject': table + '/' + name, 'field': 'default',
                    'source_expression_sha256': col['default']['ast_sha256'], 'table': table,
                    'operation': 'column-default', 'column': name, 'expression_sql': text})
        for ordinal, constraint in enumerate(info['constraints']):
            if constraint['kind'] != 'CHECK':
                continue
            text, used = validate_expression(constraint['expression']['ast'], columns, expected)
            calls |= used
            name = constraint['name'] or '<semantic-' + str(ordinal) + '>'
            entries.append({'category': 'constraints', 'subject': table + '/' + name, 'field': 'expression',
                'source_expression_sha256': constraint['expression']['ast_sha256'], 'table': table,
                'operation': 'check-not-valid', 'expression_sql': text})
    for identity, policy in sorted(expected['policies'].items()):
        for source_field, report_field in [('using', 'using'), ('with_check', 'with-check')]:
            expr = policy[source_field]
            if expr is None:
                continue
            text, used = validate_expression(expr['ast'], set(expected['tables'][policy['table']]['columns']), expected)
            calls |= used
            entries.append({'category': 'policies', 'subject': identity, 'field': report_field,
                'source_expression_sha256': expr['ast_sha256'], 'table': policy['table'],
                'operation': 'policy', 'policy_identity': identity, 'source_policy_field': source_field,
                'expression_sql': text})
    for identity, index in sorted(expected['explicit_indexes'].items()):
        if index['predicate'] is None:
            continue
        if any(source.node(k, 'IndexElem').get('expr') for k in index['keys_ast']) or index.get('include_ast'):
            raise source.ManifestError('predicate oracle requires separately reviewed expression/include index keys')
        text, used = validate_expression(index['predicate']['ast'], set(expected['tables'][index['table']]['columns']), expected)
        calls |= used
        entries.append({'category': 'indexes', 'subject': identity, 'field': 'predicate',
            'source_expression_sha256': index['predicate']['ast_sha256'], 'table': index['table'],
            'operation': 'index-predicate', 'expression_sql': text})
    for identity, function in sorted(expected['functions'].items()):
        defaults = [p['default'] for p in function['parameters'] if p['default'] is not None]
        if not defaults:
            continue
        for param in function['parameters']:
            if param['mode'] not in ('FUNC_PARAM_DEFAULT', 'FUNC_PARAM_IN'):
                raise source.ManifestError('surrogate default function requires ordinary IN parameters')
            if param['default'] is not None:
                _, used = validate_expression(param['default']['ast'], set(), expected)
                calls |= used
        entries.append({'category': 'functions', 'subject': identity, 'field': 'argument-defaults',
            'source_expression_sha256': source.digest([d['ast'] for d in defaults]),
            'operation': 'function-default-list'})
    identities = [(e['category'], e['subject'], e['field']) for e in entries]
    if len(identities) != len(set(identities)):
        raise source.ManifestError('duplicate source expression oracle identity')
    return entries, sorted(calls)


def build_plan(manifest, root=source.ROOT):
    entries, calls = expression_entries(manifest['expected'])
    hashes = {path: source.sha256((Path(root) / path).read_bytes()).hexdigest() for path in SOURCE_MODULES}
    plan = {
        'format': 'workinants.expression-oracle-plan.v1', 'status': 'DRAFT_PENDING_INDEPENDENT_REVIEW',
        'database_posture': 'D', 'database_contacted': False, 'sql_executed': False,
        'source_expected_sha256': manifest['expected_sha256'],
        'source_inputs_aggregate_sha256': manifest['inputs_aggregate_sha256'],
        'source_inputs_sha256': manifest['inputs_sha256'], 'oracle_modules_sha256': hashes,
        'server_version_num': 170011, 'parser': source.pglast.__version__,
        'expected_tables': len(manifest['expected']['tables']),
        'expected_columns': sum(len(t['columns']) for t in manifest['expected']['tables'].values()),
        'expression_count': len(entries),
        'by_operation': dict(sorted(Counter(e['operation'] for e in entries).items())),
        'expressions': [{k: v for k, v in e.items() if k != 'expression_sql'} for e in entries],
        'allowed_calls_exercised_during_compilation_only': calls,
        'execution_contract': [
            'Root verifies exact disposable Docker/image/resource/run identity and fresh external evidence directory.',
            'Fresh original-bootstrap-superuser connection; READ COMMITTED; no other restricted client and no enabled event trigger.',
            'Require source-pinned original table/column/enum/function identity/header/body prerequisites before any TEMP DDL.',
            'Create empty TEMP shadows only; no application data access; no source PK/FK/triggers copied.',
            'CHECK constraints are NOT VALID on empty shadows; original validation flags compare separately.',
            'Policies are compiled only; no source owner behavior, row access or protected operation is invoked.',
            'Function-default surrogates return NULL::integer; source function bodies are never copied or invoked.',
            'Retain only fixed preflight Booleans, source identities and expression hashes; no raw output/messages/SQL.',
            'ROLLBACK unconditionally on success; on unexpected failure close connection to abort before observations.',
            'Require explicit rollback/temporary-absence closure and independent original catalog recollection before accepting hashes.',
        ],
    }
    plan['plan_sha256'] = source.digest(plan)
    return plan


def _prerequisites(manifest, database, grantor):
    expected = manifest['expected']
    tables = []
    columns = []
    functions = []
    enums = []
    for table, info in expected['tables'].items():
        tables.append({'object': table, 'owner': info['owner'], 'rls': info['rls'], 'force_rls': info['force_rls']})
        for name, col in info['columns'].items():
            modifier = compare._typmod(col['type'])
            if modifier is None:
                raise source.ManifestError('unsupported shadow prerequisite type modifier')
            columns.append({'object': table, 'name': name, 'ordinal': col['ordinal'], 'type': compare._typename(col['type']),
                            'typmod': modifier, 'dimensions': col['type']['array_dimensions'], 'nullable': col['nullable']})
    for identity, info in expected['functions'].items():
        if any(p['mode'] not in ('FUNC_PARAM_DEFAULT', 'FUNC_PARAM_IN') for p in info['parameters']):
            raise source.ManifestError('function prerequisite needs separately reviewed OUT/variadic projection')
        settings = [s['name'] + '=' + ', '.join(str(source.literal(v)) for v in s.get('args', [])) for s in info['settings_ast']]
        functions.append({'identity': identity, 'owner': info['owner'], 'body': info['body_sha256'],
            'security': info['security_definer'], 'strict': info['strict'], 'volatility': info['volatility'][0],
            'parallel': {'unsafe': 'u', 'restricted': 'r', 'safe': 's'}[info['parallel']], 'language': info['language'],
            'return_type': compare._typename(info['return_type']), 'returns_set': info['return_type']['setof'], 'settings': settings,
            'argument_names': [p['name'] for p in info['parameters']],
            'default_count': sum(p['default'] is not None for p in info['parameters']),
            'cost': info['cost'], 'rows': info['rows'], 'leakproof': info['leakproof']})
    for identity, info in expected['enums'].items():
        enums.append({'identity': identity, 'owner': info['owner'], 'labels': info['labels']})
    values = lambda value: literal(source.canonical(value)) + '::jsonb'
    schemas = "ARRAY['app','platform','platform_private']"
    return {
        'target_identity': "current_setting('server_version_num')::integer=170011 AND current_database()=" + literal(database) + " AND current_user=" + literal(grantor) + " AND session_user=" + literal(grantor) + " AND (SELECT rolsuper FROM pg_roles WHERE rolname=current_user)",
        'read_committed': "current_setting('transaction_isolation')='read committed'",
        'no_event_triggers': "NOT EXISTS(SELECT 1 FROM pg_event_trigger WHERE evtenabled<>'D')",
        'no_restricted_clients': "NOT EXISTS(SELECT 1 FROM pg_stat_activity WHERE datname=current_database() AND usename=ANY(ARRAY['wa_migrator','wa_context_issuer','wa_app_runtime','wa_worker','wa_identity_service_authority']) AND backend_type='client backend')",
        'no_preexisting_temp_objects': "NOT EXISTS(SELECT 1 FROM pg_class WHERE relnamespace=pg_my_temp_schema()) AND NOT EXISTS(SELECT 1 FROM pg_proc WHERE pronamespace=pg_my_temp_schema())",
        'table_set_and_owners': "(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname=ANY(" + schemas + ") AND c.relkind IN ('r','p','v','m','S','f'))=" + str(len(tables)) + " AND NOT EXISTS(SELECT 1 FROM jsonb_to_recordset(" + values(tables) + ") e(object text,owner text,rls boolean,force_rls boolean) LEFT JOIN pg_class c ON c.oid=to_regclass(e.object) WHERE c.oid IS NULL OR c.relkind<>'r' OR pg_get_userbyid(c.relowner) IS DISTINCT FROM e.owner OR c.relrowsecurity IS DISTINCT FROM e.rls OR c.relforcerowsecurity IS DISTINCT FROM e.force_rls)",
        'columns_and_native_types': "(SELECT count(*) FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname=ANY(" + schemas + ") AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped)=" + str(len(columns)) + " AND NOT EXISTS(SELECT 1 FROM jsonb_to_recordset(" + values(columns) + ") e(object text,name text,ordinal integer,type text,typmod integer,dimensions integer,nullable boolean) LEFT JOIN pg_attribute a ON a.attrelid=to_regclass(e.object) AND a.attname=e.name LEFT JOIN pg_type t ON t.oid=a.atttypid WHERE a.attnum IS DISTINCT FROM e.ordinal OR a.attisdropped OR a.atttypid IS DISTINCT FROM to_regtype(e.type) OR a.atttypmod IS DISTINCT FROM e.typmod OR a.attndims IS DISTINCT FROM e.dimensions OR (NOT a.attnotnull) IS DISTINCT FROM e.nullable OR a.attidentity<>'' OR a.attgenerated<>'' OR a.attcollation IS DISTINCT FROM t.typcollation OR a.attstorage IS DISTINCT FROM t.typstorage)",
        'function_set_headers_and_bodies': "(SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname=ANY(" + schemas + "))=" + str(len(functions)) + " AND NOT EXISTS(SELECT 1 FROM jsonb_to_recordset(" + values(functions) + ") e(identity text,owner text,body text,security boolean,strict boolean,volatility text,parallel text,language text,return_type text,returns_set boolean,settings jsonb,argument_names jsonb,default_count integer,cost real,rows real,leakproof boolean) LEFT JOIN pg_proc p ON p.oid=to_regprocedure(e.identity) LEFT JOIN pg_language l ON l.oid=p.prolang WHERE p.oid IS NULL OR p.prokind<>'f' OR pg_get_userbyid(p.proowner) IS DISTINCT FROM e.owner OR encode(sha256(convert_to(p.prosrc,'UTF8')),'hex') IS DISTINCT FROM e.body OR p.prosecdef IS DISTINCT FROM e.security OR p.proisstrict IS DISTINCT FROM e.strict OR p.provolatile::text IS DISTINCT FROM e.volatility OR p.proparallel::text IS DISTINCT FROM e.parallel OR l.lanname IS DISTINCT FROM e.language OR p.prorettype IS DISTINCT FROM to_regtype(e.return_type) OR p.proretset IS DISTINCT FROM e.returns_set OR COALESCE(to_jsonb(p.proconfig),'[]'::jsonb) IS DISTINCT FROM e.settings OR COALESCE(to_jsonb(p.proargnames),'[]'::jsonb) IS DISTINCT FROM e.argument_names OR p.pronargdefaults IS DISTINCT FROM e.default_count OR p.procost IS DISTINCT FROM e.cost OR p.prorows IS DISTINCT FROM e.rows OR p.proleakproof IS DISTINCT FROM e.leakproof OR p.provariadic<>0 OR p.prosupport<>0 OR p.proallargtypes IS NOT NULL OR p.proargmodes IS NOT NULL)",
        'enum_set_owners_and_labels': "(SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname=ANY(" + schemas + ") AND t.typtype='e')=" + str(len(enums)) + " AND NOT EXISTS(SELECT 1 FROM jsonb_to_recordset(" + values(enums) + ") e(identity text,owner text,labels jsonb) LEFT JOIN pg_type t ON t.oid=to_regtype(e.identity) WHERE t.oid IS NULL OR t.typtype<>'e' OR pg_get_userbyid(t.typowner) IS DISTINCT FROM e.owner OR (SELECT jsonb_agg(x.enumlabel ORDER BY x.enumsortorder) FROM pg_enum x WHERE x.enumtypid=t.oid) IS DISTINCT FROM e.labels)",
        'original_grantor_finalization': "NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member=to_regrole('wa_schema_owner') AND roleid=ANY(ARRAY[to_regrole('wa_private_helper_owner'),to_regrole('wa_customer_verifier'),to_regrole('wa_track_verifier')])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE')",
    }


def emit_sql(manifest, plan, *, database, grantor):
    if manifest['approval_binding'] != 'ALL_INPUT_HASHES_VERIFIED':
        raise source.ManifestError('SQL emission requires a complete reviewed source input pin map')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9-]{0,62}', database) or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,62}', grantor):
        raise source.ManifestError('bounded explicit local database/grantor identity required')
    if plan['source_expected_sha256'] != manifest['expected_sha256']:
        raise source.ManifestError('plan/source mismatch')
    if plan['plan_sha256'] != source.digest({k: v for k, v in plan.items() if k != 'plan_sha256'}):
        raise source.ManifestError('plan digest mismatch')
    expected = manifest['expected']
    entries, _ = expression_entries(expected)
    tables = {name: 'wa_expr_oracle_t_' + str(i).zfill(3) for i, name in enumerate(sorted(expected['tables']))}
    preflight = _prerequisites(manifest, database, grantor)
    sql = ["-- DRAFT expression oracle; exact packet/run needs independent review before local execution.",
           "-- Source plan SHA256 " + plan['plan_sha256'],
           "BEGIN; SET LOCAL TRANSACTION ISOLATION LEVEL READ COMMITTED;",
           "SET LOCAL search_path=pg_catalog; SET LOCAL statement_timeout='30s'; SET LOCAL lock_timeout='2s';",
           "SET LOCAL log_statement='none'; SET LOCAL log_min_error_statement='panic'; SET LOCAL client_min_messages='warning';"]
    outcomes = ','.join(literal(name) + ',COALESCE((' + query + '),false)' for name, query in preflight.items())
    sql.append("SELECT jsonb_build_object('format','workinants.expression-oracle-preflight.v1','plan_sha256'," + literal(plan['plan_sha256']) + ",'outcomes',jsonb_build_object(" + outcomes + '));')
    sql.append("DO $wa_oracle_gate$ BEGIN IF NOT (" + ' AND '.join('COALESCE((' + q + '),false)' for q in preflight.values()) + ") THEN RAISE EXCEPTION 'catalog expression oracle prerequisite failed' USING ERRCODE='P0001'; END IF; END $wa_oracle_gate$;")
    for table, temporary in tables.items():
        cols = [ident(name) + ' ' + native_type_sql(col['type']) + (' NOT NULL' if not col['nullable'] else '') for name, col in expected['tables'][table]['columns'].items()]
        sql.append('CREATE TEMP TABLE ' + ident(temporary) + '(' + ','.join(cols) + ') ON COMMIT DROP;')
    selections = []
    surrogate_functions = []
    for index, entry in enumerate(entries):
        oracle_name = 'wa_expr_oracle_e_' + str(index).zfill(4)
        target = 'pg_temp.' + ident(tables[entry['table']]) if entry.get('table') else None
        operation = entry['operation']
        if operation == 'column-default':
            sql.append('ALTER TABLE ' + target + ' ALTER COLUMN ' + ident(entry['column']) + ' SET DEFAULT ' + entry['expression_sql'] + ';')
            query = 'SELECT encode(sha256(convert_to(pg_get_expr(d.adbin,d.adrelid,false),\'UTF8\')),\'hex\') FROM pg_attrdef d JOIN pg_attribute a ON a.attrelid=d.adrelid AND a.attnum=d.adnum WHERE d.adrelid=' + literal('pg_temp.' + tables[entry['table']]) + '::regclass AND a.attname=' + literal(entry['column'])
        elif operation == 'check-not-valid':
            sql.append('ALTER TABLE ' + target + ' ADD CONSTRAINT ' + ident(oracle_name) + ' CHECK(' + entry['expression_sql'] + ') NOT VALID;')
            query = 'SELECT encode(sha256(convert_to(pg_get_expr(c.conbin,c.conrelid,false),\'UTF8\')),\'hex\') FROM pg_constraint c WHERE c.conrelid=' + literal('pg_temp.' + tables[entry['table']]) + '::regclass AND c.conname=' + literal(oracle_name)
        elif operation == 'policy':
            # Compile one source policy expression per policy, retaining its
            # command and role semantics while collecting each clause alone.
            policy = expected['policies'][entry['policy_identity']]
            clause = 'USING' if entry['source_policy_field'] == 'using' else 'WITH CHECK'
            sql.append('CREATE POLICY ' + ident(oracle_name) + ' ON ' + target + ' AS ' + ('PERMISSIVE' if policy['permissive'] else 'RESTRICTIVE') + ' FOR ' + policy['command'].upper() + ' TO ' + ','.join('PUBLIC' if r == 'PUBLIC' else ident(r) for r in policy['roles']) + ' ' + clause + '(' + entry['expression_sql'] + ');')
            field = 'polqual' if entry['source_policy_field'] == 'using' else 'polwithcheck'
            query = 'SELECT encode(sha256(convert_to(pg_get_expr(p.' + field + ',p.polrelid,false),\'UTF8\')),\'hex\') FROM pg_policy p WHERE p.polrelid=' + literal('pg_temp.' + tables[entry['table']]) + '::regclass AND p.polname=' + literal(oracle_name)
        elif operation == 'index-predicate':
            info = expected['explicit_indexes'][entry['subject']]
            keys = ','.join(ident(source.node(k, 'IndexElem')['name']) for k in info['keys_ast'])
            sql.append('CREATE INDEX ' + ident(oracle_name) + ' ON ' + target + ' USING ' + ident(info['access_method']) + '(' + keys + ') WHERE ' + entry['expression_sql'] + ';')
            query = 'SELECT encode(sha256(convert_to(pg_get_expr(i.indpred,i.indrelid,false),\'UTF8\')),\'hex\') FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid WHERE i.indrelid=' + literal('pg_temp.' + tables[entry['table']]) + '::regclass AND c.relname=' + literal(oracle_name)
        elif operation == 'function-default-list':
            info = expected['functions'][entry['subject']]
            args = []
            for param in info['parameters']:
                arg = (ident(param['name']) + ' ' if param['name'] else '') + native_type_sql(param['type'])
                if param['default'] is not None:
                    arg += ' DEFAULT ' + validate_expression(param['default']['ast'], set(), expected)[0]
                args.append(arg)
            signature = 'pg_temp.' + ident(oracle_name) + '(' + ','.join(native_type_sql(p['type']) for p in info['parameters']) + ')'
            sql.append('CREATE FUNCTION pg_temp.' + ident(oracle_name) + '(' + ','.join(args) + ') RETURNS pg_catalog.int4 LANGUAGE sql SECURITY INVOKER SET search_path=pg_catalog AS $wa_oracle_null$ SELECT NULL::pg_catalog.int4 $wa_oracle_null$;')
            sql.append('REVOKE ALL ON FUNCTION ' + signature + ' FROM PUBLIC;')
            surrogate_functions.append(oracle_name)
            query = 'SELECT encode(sha256(convert_to(pg_get_expr(p.proargdefaults,0,false),\'UTF8\')),\'hex\') FROM pg_proc p WHERE p.oid=' + literal('pg_temp.' + oracle_name + '(' + ','.join(compare._typename(p['type']) for p in info['parameters']) + ')') + '::regprocedure'
        else:
            raise source.ManifestError('unsupported source oracle operation')
        record = {k: entry[k] for k in ('category', 'subject', 'field', 'source_expression_sha256')}
        selections.append('(' + literal(source.canonical(record)) + '::jsonb || jsonb_build_object(\'value_sha256\',(' + query + ')))')
    sql.append("SELECT jsonb_build_object('format','workinants.expression-oracle-results.v1','source_expected_sha256'," + literal(manifest['expected_sha256']) + ",'source_inputs_aggregate_sha256'," + literal(manifest['inputs_aggregate_sha256']) + ",'plan_sha256'," + literal(plan['plan_sha256']) + ",'server_version_num',current_setting('server_version_num')::integer,'expression_count'," + str(len(entries)) + ",'expressions',(SELECT jsonb_agg(value) FROM (VALUES " + ',\n'.join(selections) + ') source_derived_expected(value)));')
    sql.append('ROLLBACK;')
    names_sql = 'ARRAY[' + ','.join(literal(n) for n in tables.values()) + ']'
    functions_sql = 'ARRAY[' + ','.join(literal(n) for n in surrogate_functions) + ']::text[]'
    sql.append("SELECT jsonb_build_object('format','workinants.expression-oracle-closure.v1','plan_sha256'," + literal(plan['plan_sha256']) + ",'all_oracle_tables_absent',NOT EXISTS(SELECT 1 FROM pg_class WHERE relnamespace=pg_my_temp_schema() AND relname=ANY(" + names_sql + ")), 'all_oracle_functions_absent',NOT EXISTS(SELECT 1 FROM pg_proc WHERE pronamespace=pg_my_temp_schema() AND proname=ANY(" + functions_sql + ')));')
    return '\n'.join(sql) + '\n'


def validate_evidence(manifest, native_snapshot, evidence, *, database, grantor, root=source.ROOT):
    """Bind root-retained sanitized proof to reviewed source and rollback state.

    This validates an evidence contract; the root runner alone performs and
    independently observes the actual target/connection/rollback operations.
    No claimed success or arbitrary retained field can replace a required item.
    """
    fields = {'format', 'database', 'oracle_sql_sha256', 'preflight', 'results', 'closure',
              'connection_closed_before_observation', 'pre_oracle_catalog_sha256',
              'post_rollback_catalog_sha256'}
    if not isinstance(evidence, dict) or set(evidence) != fields:
        raise source.ManifestError('oracle evidence field set invalid')
    if evidence['format'] != 'workinants.reviewed-expression-oracle-evidence.v1' or evidence['database'] != database:
        raise source.ManifestError('oracle evidence target/format mismatch')
    plan = build_plan(manifest, root)
    sql = emit_sql(manifest, plan, database=database, grantor=grantor)
    if evidence['oracle_sql_sha256'] != source.sha256(sql.encode('utf-8')).hexdigest():
        raise source.ManifestError('oracle SQL packet mismatch')
    preflight, results, closure = evidence['preflight'], evidence['results'], evidence['closure']
    if not isinstance(preflight, dict) or set(preflight) != {'format', 'plan_sha256', 'outcomes'}:
        raise source.ManifestError('oracle preflight malformed')
    if preflight['format'] != 'workinants.expression-oracle-preflight.v1' or preflight['plan_sha256'] != plan['plan_sha256']:
        raise source.ManifestError('oracle preflight source mismatch')
    outcomes = preflight['outcomes']
    if not isinstance(outcomes, dict) or set(outcomes) != set(_prerequisites(manifest, database, grantor)) or not all(v is True for v in outcomes.values()):
        raise source.ManifestError('oracle preflight did not pass every exact control')
    result_fields = {'format', 'source_expected_sha256', 'source_inputs_aggregate_sha256', 'plan_sha256',
                     'server_version_num', 'expression_count', 'expressions'}
    if not isinstance(results, dict) or set(results) != result_fields:
        raise source.ManifestError('oracle results malformed')
    bindings = {'format': 'workinants.expression-oracle-results.v1',
                'source_expected_sha256': manifest['expected_sha256'],
                'source_inputs_aggregate_sha256': manifest['inputs_aggregate_sha256'],
                'plan_sha256': plan['plan_sha256'], 'server_version_num': 170011,
                'expression_count': plan['expression_count']}
    if any(results[k] != v for k, v in bindings.items()):
        raise source.ManifestError('oracle results source/version mismatch')
    if not isinstance(closure, dict) or set(closure) != {'format', 'plan_sha256', 'all_oracle_tables_absent', 'all_oracle_functions_absent'} or closure['format'] != 'workinants.expression-oracle-closure.v1' or closure['plan_sha256'] != plan['plan_sha256'] or closure['all_oracle_tables_absent'] is not True or closure['all_oracle_functions_absent'] is not True:
        raise source.ManifestError('oracle rollback closure missing')
    if evidence['connection_closed_before_observation'] is not True:
        raise source.ManifestError('oracle backend closure missing')
    snapshot_hash = source.digest(native_snapshot)
    if evidence['pre_oracle_catalog_sha256'] != snapshot_hash or evidence['post_rollback_catalog_sha256'] != snapshot_hash:
        raise source.ManifestError('oracle before/after application catalog preservation mismatch')
    if native_snapshot.get('server_version_num') != 170011 or native_snapshot.get('read_only') is not True:
        raise source.ManifestError('oracle independent native observation mismatch')
    expected_keys = {(e['category'], e['subject'], e['field'], e['source_expression_sha256']) for e in plan['expressions']}
    registry = {}
    if not isinstance(results['expressions'], list):
        raise source.ManifestError('oracle expression results missing')
    for row in results['expressions']:
        if not isinstance(row, dict) or set(row) != {'category', 'subject', 'field', 'source_expression_sha256', 'value_sha256'}:
            raise source.ManifestError('oracle expression result malformed')
        key = (row['category'], row['subject'], row['field'], row['source_expression_sha256'])
        if key not in expected_keys or key in registry or not isinstance(row['value_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', row['value_sha256']):
            raise source.ManifestError('oracle expression result identity/hash invalid')
        registry[key] = row['value_sha256']
    if set(registry) != expected_keys:
        raise source.ManifestError('oracle expression coverage incomplete')
    return registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=source.ROOT)
    parser.add_argument('--pins', type=Path)
    parser.add_argument('--emit-sql', action='store_true')
    parser.add_argument('--database')
    parser.add_argument('--bootstrap-grantor')
    args = parser.parse_args()
    pins = json.loads(args.pins.read_text(encoding='utf-8')) if args.pins else None
    manifest = source.build_manifest(args.root, pins)
    plan = build_plan(manifest, args.root)
    if args.emit_sql:
        if not args.database or not args.bootstrap_grantor:
            raise source.ManifestError('SQL emission requires explicit database/bootstrap identity')
        print(emit_sql(manifest, plan, database=args.database, grantor=args.bootstrap_grantor), end='')
    else:
        print(json.dumps(plan, indent=2))


if __name__ == '__main__':
    main()
