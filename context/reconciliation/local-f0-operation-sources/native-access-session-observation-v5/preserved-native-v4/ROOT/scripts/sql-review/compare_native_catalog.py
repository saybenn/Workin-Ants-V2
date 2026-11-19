#!/usr/bin/env python3
"""Offline comparison of source expectations and a reviewed PG17 catalog export.

Never connects to PostgreSQL or invokes a process. Native definitions arrive as
hashes, not raw SQL. Exact structural mismatches FAIL. Unresolved expression
deparse/default/opclass/ledger comparisons remain INCOMPLETE. Counts never pass
a comparison. Output contains allowlisted source identities and hashes only.

The source compiler and native collector require independent review before use.
The source compiler models superuser object GRANT as its owner. Membership
grantors stay bound to the explicitly supplied original bootstrap grantor.
The external public-schema owner must be separately registered; it is never
guessed or dropped from privilege comparisons.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from pglast import ast
from pglast.parser import parse_sql_json
from pglast.stream import RawStream

import catalog_manifest as source
import pg17_catalog_rules as pg17


def text_hash(text):
    return source.sha256(text.encode('utf-8')).hexdigest()


def expression_ast(sql):
    """One fixed SELECT wrapper; reject statements/clauses beyond one expression."""
    parsed = json.loads(parse_sql_json('SELECT ' + sql))['stmts']
    if len(parsed) != 1 or 'SelectStmt' not in parsed[0]['stmt']:
        raise source.ManifestError('one expression required')
    select = parsed[0]['stmt']['SelectStmt']
    if set(select) - {'targetList', 'limitOption', 'op'} or len(select['targetList']) != 1:
        raise source.ManifestError('unsupported expression wrapper structure')
    target = source.node(select['targetList'][0], 'ResTarget')
    if set(target) - {'val', 'location'}:
        raise source.ManifestError('expression alias or indirection is not supported')
    return source.clean(target['val'])


def equivalent_expression(left, right):
    """Normalize parser positions/parentheses/type aliases only; never erase casts."""
    return expression_ast(left) == expression_ast(right)


def _ast_node(value, field=None):
    if isinstance(value, list):
        return tuple(_ast_node(v) for v in value)
    if not isinstance(value, dict):
        return value
    if field == 'typeName':
        return ast.TypeName(**{k: _ast_node(v, k) for k, v in value.items()})
    if len(value) != 1:
        raise source.ManifestError('unsupported untagged source expression AST')
    kind, data = next(iter(value.items()))
    if kind == 'List':
        return tuple(_ast_node(v) for v in data.get('items', []))
    if kind == 'A_Const':
        if data.get('isnull'):
            return ast.A_Const(isnull=True)
        for key, cls, default in [('sval', ast.String, ''), ('ival', ast.Integer, 0),
                                  ('fval', ast.Float, '0'), ('boolval', ast.Boolean, False)]:
            if key in data:
                # libpg_query omits zero/false/empty scalar members. pglast
                # constructors default to None, which would print `None`.
                return ast.A_Const(val=cls(**{key: data[key].get(key, default)}))
        raise source.ManifestError('unsupported source constant')
    return getattr(ast, kind)(**{k: _ast_node(v, k) for k, v in data.items()})


def expression_hashes(expected):
    """Accept only renderings proven to parse to the same untouched source AST."""
    if expected is None:
        return {None}
    try:
        text = RawStream()(_ast_node(expected['ast']))
        candidates = (text, '(' + text + ')')
        return {text_hash(v) for v in candidates if expression_ast(v) == expected['ast']}
    except (ValueError, TypeError, AttributeError, KeyError, source.ManifestError):
        return set()


class Comparison:
    def __init__(self, expected):
        self.findings = []
        self.totals = Counter()
        self.allowlisted = set(expected['tables']) | set(expected['functions']) | set(expected['enums'])
        self.allowlisted |= set(expected['explicit_indexes']) | set(expected['schemas']) | set(expected['roles'])
        self.allowlisted |= set(expected['policies']) | set(expected['triggers'])
        self.oracle_hashes = {}

    def subject(self, value):
        return value if value in self.allowlisted else '<unregistered:' + source.digest(value)[:20] + '>'

    def record(self, category, subject, field, status, expected=None, actual=None):
        self.totals[status] += 1
        if status != 'PASS':
            item = {'category': category, 'subject': self.subject(subject), 'field': field, 'status': status}
            if expected is not None:
                item['expected_sha256'] = source.digest(expected)
            if actual is not None:
                item['actual_sha256'] = source.digest(actual)
            self.findings.append(item)

    def exact(self, category, subject, field, expected, actual):
        self.record(category, subject, field, 'PASS' if expected == actual else 'FAIL', expected, actual)

    def hash_expr(self, category, subject, field, expected, actual):
        key = (category, subject, field, expected['ast_sha256']) if expected is not None else None
        if key in self.oracle_hashes:
            self.exact(category, subject, field, self.oracle_hashes[key], actual)
        elif expected is None:
            self.exact(category, subject, field, None, actual)
        elif actual is None:
            self.record(category, subject, field, 'FAIL', expected['ast_sha256'], None)
        elif actual in expression_hashes(expected):
            self.record(category, subject, field, 'PASS')
        else:
            self.record(category, subject, field, 'INCOMPLETE', expected['ast_sha256'], actual)

    def mapping(self, category, rows, key):
        result = {}
        if not isinstance(rows, list):
            self.record(category, category, 'visibility', 'INCOMPLETE')
            return result
        for row in rows:
            try:
                identity = key(row)
            except (KeyError, TypeError):
                self.record(category, category, 'malformed-row', 'INCOMPLETE')
                continue
            if identity in result:
                self.record(category, identity, 'duplicate-native-identity', 'FAIL')
            result[identity] = row
        return result

    def sets(self, category, expected, actual):
        for identity in sorted(set(expected) | set(actual)):
            self.exact(category, identity, 'object-present', identity in expected, identity in actual)


def _typename(value):
    return value['name'] + '[]' * value['array_dimensions']


def _typmod(info):
    mods = info['typmods_ast']
    if not mods:
        return -1
    if len(mods) != 1:
        return None
    value = source.literal(mods[0])
    if info['name'] in ('pg_catalog.bpchar', 'pg_catalog.varchar'):
        return value + 4
    if info['name'] in ('pg_catalog.timestamptz', 'pg_catalog.timestamp', 'pg_catalog.time', 'pg_catalog.timetz'):
        return value
    return None


def _column_refs(value):
    result = set()
    if isinstance(value, dict):
        if 'ColumnRef' in value:
            fields = value['ColumnRef'].get('fields', [])
            if fields and 'String' in fields[-1]:
                result.add(fields[-1]['String']['sval'])
        for child in value.values():
            result |= _column_refs(child)
    elif isinstance(value, list):
        for child in value:
            result |= _column_refs(child)
    return result


def _acl_expected(expected, public_schema_owner):
    result = []
    for row in expected['nonowner_acl']:
        grantor = row['grantor']
        if grantor == source.PUBLIC_SCHEMA_OWNER:
            grantor = public_schema_owner or source.PUBLIC_SCHEMA_OWNER
        elif grantor == source.ORIGINAL_GRANTOR:
            raise source.ManifestError('source object-grantor semantics unresolved')
        for column in row['columns'] if row['scope'] == 'columns' else [None]:
            result.append({'kind': row['kind'], 'object': row['object'], 'column': column,
                           'grantee': row['grantee'], 'grantor': grantor,
                           'privilege': row['privilege'], 'grant_option': row['grant_option']})
    return result


def compare_manifest(manifest, native, *, bootstrap_grantor, bootstrap_superuser=False,
                     public_schema_owner=None, public_acl_registration=None, ledger_registration=None,
                     ledger_evidence=None, expression_oracle_evidence=None, oracle_database=None, root=source.ROOT):
    expected = manifest['expected']
    result = Comparison(expected)
    if expression_oracle_evidence is not None:
        try:
            if oracle_database is None:
                raise source.ManifestError('oracle target registration missing')
            import catalog_expression_oracle
            result.oracle_hashes = catalog_expression_oracle.validate_evidence(manifest, native,
                expression_oracle_evidence, database=oracle_database, grantor=bootstrap_grantor, root=root)
            result.record('expression-oracle', 'expression-oracle', 'source-derived-rollback-evidence', 'PASS')
        except (source.ManifestError, KeyError, TypeError, ValueError):
            result.record('expression-oracle', 'expression-oracle', 'invalid-or-incomplete-evidence', 'FAIL')
    if native.get('format') != 'workinants.native-catalog.v1':
        result.record('snapshot', 'snapshot', 'format', 'INCOMPLETE')
    result.exact('snapshot', 'snapshot', 'postgres-release', 170011, native.get('server_version_num'))
    result.exact('snapshot', 'snapshot', 'read-only', True, native.get('read_only'))
    if bootstrap_superuser:
        result.exact('snapshot', 'snapshot', 'collector-original-grantor', bootstrap_grantor, native.get('collected_as'))
        result.exact('snapshot', 'snapshot', 'collector-superuser', True, native.get('collector_is_superuser'))
    elif manifest.get('environment_assumptions', {}).get('original_bootstrap_requires_superuser'):
        result.record('snapshot', 'snapshot', 'bootstrap-superuser-provenance', 'INCOMPLETE')
    roles = result.mapping('roles', native.get('roles'), lambda r: r['name'])
    result.sets('roles', expected['roles'], roles)
    for identity in set(expected['roles']) & set(roles):
        for field, value in expected['roles'][identity]['native_attributes'].items():
            result.exact('roles', identity, field, value, roles[identity].get(field))
    schemas = result.mapping('schemas', native.get('schemas'), lambda r: r['object'])
    result.sets('schemas', expected['schemas'], schemas)
    for identity in set(expected['schemas']) & set(schemas):
        result.exact('schemas', identity, 'owner', expected['schemas'][identity]['owner'], schemas[identity].get('owner'))
    memberships = [{**r, 'grantor': bootstrap_grantor if r['grantor'] == source.ORIGINAL_GRANTOR else r['grantor']} for r in expected['memberships']]
    result.exact('memberships', 'memberships', 'complete-membership-set', sorted(memberships, key=source.canonical),
                 sorted(native.get('memberships', []), key=source.canonical))
    relations = result.mapping('relations', native.get('relations'), lambda r: r['object'])
    result.sets('relations', expected['tables'], relations)
    for identity in set(expected['tables']) & set(relations):
        want = expected['tables'][identity]
        for field, value in {'owner': want['owner'], 'kind': want['relkind'], 'persistence': want['persistence'],
                             'rls': want['rls'], 'force_rls': want['force_rls'], 'replica_identity': 'd'}.items():
            result.exact('relations', identity, field, value, relations[identity].get(field))
    columns = result.mapping('columns', native.get('columns'), lambda r: r['table_name'] + '/' + r['name'])
    wanted_columns = {table + '/' + col: value for table, info in expected['tables'].items() for col, value in info['columns'].items()}
    result.sets('columns', wanted_columns, columns)
    for identity in set(wanted_columns) & set(columns):
        want, got = wanted_columns[identity], columns[identity]
        for field, value in {'ordinal': want['ordinal'], 'type': _typename(want['type']),
                             'array_dimensions': want['type']['array_dimensions'], 'nullable': want['nullable'],
                             'identity': want['identity'], 'generated': want['generated'],
                             'storage_is_type_default': True, 'compression': '', 'is_local': True, 'inherited_count': 0}.items():
            result.exact('columns', identity, field, value, got.get(field))
        modifier = _typmod(want['type'])
        if modifier is None:
            result.record('columns', identity, 'typmod-normalization', 'INCOMPLETE')
        else:
            result.exact('columns', identity, 'typmod', modifier, got.get('typmod'))
        if want['collation_ast'] is None:
            result.exact('columns', identity, 'collation-is-type-default', True, got.get('collation_is_type_default'))
        else:
            result.record('columns', identity, 'explicit-collation', 'INCOMPLETE')
        result.hash_expr('columns', identity, 'default', want['default'], got.get('default_sha256'))
    enums = result.mapping('enums', native.get('enums'), lambda r: r['object'])
    result.sets('enums', expected['enums'], enums)
    for identity in set(expected['enums']) & set(enums):
        for field in ('owner', 'labels'):
            result.exact('enums', identity, field, expected['enums'][identity][field], enums[identity].get(field))
    # Native auto row/array types are explicit requirements, not ignored extras.
    types = result.mapping('types', native.get('types'), lambda r: r['object'])
    wanted_types = {identity: {k: v for k, v in info.items() if k != 'usage_delegates_to'}
                    for identity, info in pg17.generated_types(expected).items()}
    for identity, info in expected['enums'].items():
        wanted_types[identity] = {'owner': info['owner'], 'kind': 'e', 'category': 'E', 'element': None, 'relation': None}
    result.sets('types', wanted_types, types)
    for identity in set(wanted_types) & set(types):
        for field, value in wanted_types[identity].items():
            result.exact('types', identity, field, value, types[identity].get(field))
    constraints = result.mapping('constraints', native.get('constraints'), lambda r: r['table_name'] + '/' + r['name'])
    used_constraints = set()
    matched_source_constraints = []
    constraint_index_names = {}
    for table, info in expected['tables'].items():
        for ordinal, want in enumerate(info['constraints']):
            identity = table + '/' + (want['name'] or '<semantic-' + str(ordinal) + '>')
            candidates = [key for key, item in constraints.items() if item['table_name'] == table and key not in used_constraints
                          and (item['name'] == want['name'] if want['name'] else item['kind'] == {'PRIMARY': 'p', 'UNIQUE': 'u', 'FOREIGN': 'f', 'CHECK': 'c', 'EXCLUSION': 'x'}[want['kind']])]
            if not want['name']:
                wanted_cols = set(want['columns']) | _column_refs(want['expression']['ast'] if want['expression'] else {})
                candidates = [key for key in candidates if set(constraints[key]['columns']) == wanted_cols]
                if len(candidates) > 1:
                    oracle_key = ('constraints', identity, 'expression', want['expression']['ast_sha256']) if want['expression'] else None
                    hashes = {result.oracle_hashes[oracle_key]} if oracle_key in result.oracle_hashes else expression_hashes(want['expression'])
                    matching = [key for key in candidates if constraints[key].get('expression_sha256') in hashes]
                    candidates = matching or candidates
            if len(candidates) != 1:
                result.record('constraints', table, 'missing-or-ambiguous-constraint', 'FAIL' if not candidates else 'INCOMPLETE', want['semantic_sha256'], len(candidates))
                continue
            key = candidates[0]; used_constraints.add(key); got = constraints[key]
            matched_source_constraints.append((table, info, want, got))
            wanted_cols = sorted(_column_refs(want['expression']['ast'])) if want['kind'] == 'CHECK' and want['expression'] else want['columns']
            got_cols = sorted(got['columns']) if want['kind'] == 'CHECK' else got['columns']
            result.exact('constraints', table, 'columns', wanted_cols, got_cols)
            for field, value in {'kind': {'PRIMARY': 'p', 'UNIQUE': 'u', 'FOREIGN': 'f', 'CHECK': 'c', 'EXCLUSION': 'x'}[want['kind']],
                                 'deferrable': want['deferrable'], 'initially_deferred': want['initially_deferred'],
                                 'validated': want['validated'], 'has_index': want['kind'] in ('PRIMARY', 'UNIQUE', 'FOREIGN', 'EXCLUSION')}.items():
                result.exact('constraints', table, field, value, got.get(field))
            result.exact('constraints', table, 'no_inherit', pg17.constraint_no_inherit(info, want), got.get('no_inherit'))
            if want['kind'] == 'FOREIGN':
                for field in ('references', 'referenced_columns', 'match', 'update_action', 'delete_action'):
                    result.exact('constraints', table, field, want[field], got.get(field))
            result.hash_expr('constraints', identity, 'expression', want['expression'], got.get('expression_sha256'))
            if want['kind'] in ('PRIMARY', 'UNIQUE'):
                expected_name = table.split('.')[0] + '.' + want['name'] if want['name'] else got.get('index_name')
                if not isinstance(expected_name, str):
                    result.record('constraints', table, 'source-constraint-index-name', 'FAIL')
                    continue
                result.exact('constraints', table, 'source-constraint-index-name', expected_name, got.get('index_name'))
                constraint_index_names[expected_name] = {'table': table, 'owner': info['owner'], 'access_method': 'btree',
                    'unique': True, 'primary': want['kind'] == 'PRIMARY', 'nulls_not_distinct': want['nulls_not_distinct'],
                    'columns': want['columns'], 'predicate': None}
            if want['kind'] == 'EXCLUSION':
                result.record('constraints', table, 'exclusion-operators', 'INCOMPLETE')
    for identity, want in pg17.user_trigger_constraints(expected).items():
        if identity not in constraints:
            result.record('constraints', identity, 'source-user-trigger-constraint-row', 'FAIL')
            continue
        used_constraints.add(identity)
        for field, value in want.items():
            result.exact('constraints', identity, field, value, constraints[identity].get(field))
    for table, info, constraint, got in matched_source_constraints:
        if constraint['kind'] != 'FOREIGN':
            continue
        candidates = pg17.eligible_fk_indexes(expected, matched_source_constraints, constraint)
        if not candidates:
            result.record('constraints', table, 'source-eligible-referenced-unique-index', 'INCOMPLETE')
        else:
            result.exact('constraints', table, 'source-eligible-referenced-unique-index', True,
                         got.get('referenced_unique_index') in candidates)
    for key in set(constraints) - used_constraints:
        result.record('constraints', key, 'unexpected-or-unresolved-native-constraint', 'INCOMPLETE' if any(f['category'] == 'constraints' and f['status'] == 'INCOMPLETE' for f in result.findings) else 'FAIL')
    indexes = result.mapping('indexes', native.get('indexes'), lambda r: r['object'])
    wanted_indexes = dict(constraint_index_names)
    for identity, info in expected['explicit_indexes'].items():
        cols = [source.node(v, 'IndexElem').get('name') for v in info['keys_ast']]
        wanted_indexes[identity] = {**info, 'columns': cols}
    result.sets('indexes', wanted_indexes, indexes)
    for identity in set(wanted_indexes) & set(indexes):
        want, got = wanted_indexes[identity], indexes[identity]
        for field, value in {'table_name': want['table'], 'owner': want['owner'], 'access_method': want['access_method'],
                             'unique': want['unique'], 'primary': want['primary'], 'nulls_not_distinct': want['nulls_not_distinct'],
                             'valid': True, 'ready': True, 'live': True, 'immediate': True, 'clustered': False,
                             'replica_identity': False, 'key_count': len(want['columns'])}.items():
            result.exact('indexes', identity, field, value, got.get(field))
        result.exact('indexes', identity, 'key-columns', want['columns'], [r.get('column') for r in got.get('keys', []) if not r.get('included')])
        if want.get('include_ast'):
            result.record('indexes', identity, 'include-columns', 'INCOMPLETE')
        else:
            result.exact('indexes', identity, 'include-columns', [], [r.get('column') for r in got.get('keys', []) if r.get('included')])
        for position, key in enumerate(got.get('keys', [])):
            if key.get('included'):
                continue
            raw_key = source.node(want['keys_ast'][position], 'IndexElem') if want.get('keys_ast') and position < len(want['keys_ast']) else {}
            if raw_key.get('expr') or raw_key.get('opclass') or raw_key.get('collation'):
                result.record('indexes', identity, 'explicit-expression-opclass-collation', 'INCOMPLETE')
                continue
            result.exact('indexes', identity, 'expression-absent', None, key.get('expression_sha256'))
            result.exact('indexes', identity, 'default-opclass', True, key.get('opclass_default'))
            result.exact('indexes', identity, 'default-collation', True, key.get('collation_is_type_default'))
            descending = raw_key.get('ordering') == 'SORTBY_DESC'
            nulls = raw_key.get('nulls_ordering', 'SORTBY_NULLS_DEFAULT')
            result.exact('indexes', identity, 'descending', descending, key.get('descending'))
            result.exact('indexes', identity, 'nulls-first', nulls == 'SORTBY_NULLS_FIRST' or (nulls == 'SORTBY_NULLS_DEFAULT' and descending), key.get('nulls_first'))
        result.hash_expr('indexes', identity, 'predicate', want['predicate'], got.get('predicate_sha256'))
    functions = result.mapping('functions', native.get('functions'), lambda r: r['object'])
    result.sets('functions', expected['functions'], functions)
    modes = {'FUNC_PARAM_DEFAULT': 'i', 'FUNC_PARAM_IN': 'i', 'FUNC_PARAM_OUT': 'o', 'FUNC_PARAM_INOUT': 'b', 'FUNC_PARAM_VARIADIC': 'v', 'FUNC_PARAM_TABLE': 't'}
    for identity in set(expected['functions']) & set(functions):
        want, got = expected['functions'][identity], functions[identity]
        for field in ('name', 'owner', 'language', 'security_definer', 'strict', 'leakproof', 'cost', 'rows', 'body_sha256'):
            result.exact('functions', identity, field, want[field], got.get(field))
        for field, value in {'return_type': _typename(want['return_type']), 'returns_set': want['return_type']['setof'],
                             'volatility': want['volatility'][0], 'parallel': {'unsafe': 'u', 'restricted': 'r', 'safe': 's'}[want['parallel']],
                             'kind': 'f', 'variadic': any(p['mode'] == 'FUNC_PARAM_VARIADIC' for p in want['parameters']), 'support_function': False}.items():
            result.exact('functions', identity, field, value, got.get(field))
        params = [{'name': p['name'], 'mode': modes[p['mode']], 'type': _typename(p['type'])} for p in want['parameters']]
        result.exact('functions', identity, 'parameters', params, got.get('parameters'))
        settings = [s['name'] + '=' + ', '.join(str(source.literal(v)) for v in s.get('args', [])) for s in want['settings_ast']]
        result.exact('functions', identity, 'settings', sorted(settings), sorted(got.get('settings', [])))
        defaults = [p['default'] for p in want['parameters'] if p['default'] is not None]
        result.exact('functions', identity, 'default-count', len(defaults), got.get('default_count'))
        if defaults:
            key = ('functions', identity, 'argument-defaults', source.digest([d['ast'] for d in defaults]))
            if key in result.oracle_hashes:
                result.exact('functions', identity, 'argument-defaults', result.oracle_hashes[key], got.get('defaults_sha256'))
                continue
            try:
                rendered = ', '.join(RawStream()(_ast_node(d['ast'])) for d in defaults)
                result.record('functions', identity, 'argument-defaults', 'PASS' if text_hash(rendered) == got.get('defaults_sha256') else 'INCOMPLETE')
            except (ValueError, TypeError, AttributeError, KeyError):
                result.record('functions', identity, 'argument-defaults', 'INCOMPLETE')
        else:
            result.exact('functions', identity, 'argument-defaults', None, got.get('defaults_sha256'))
    triggers = result.mapping('triggers', [r for r in native.get('triggers', []) if not r.get('internal')], lambda r: r['table_name'] + '/' + r['name'])
    result.sets('triggers', expected['triggers'], triggers)
    for identity in set(expected['triggers']) & set(triggers):
        want, got = expected['triggers'][identity], triggers[identity]
        for field, value in {'function': want['function'], 'enabled': want['enabled'], 'constraint': want['constraint'],
                             'deferrable': want['deferrable'], 'initially_deferred': want['initially_deferred'],
                             'type_bits': want['event_bits'] | want['timing_bits'] | int(want['row']),
                             'argument_count': len(want['arguments'])}.items():
            result.exact('triggers', identity, field, value, got.get(field))
        referenced = pg17.user_trigger_reference(want)
        links = {'function_identity': want['function'] + '()',
                 'function_release_builtin': want['function'] + '()' in pg17.PINNED_TRIGGER_FUNCTIONS,
                 'constraint_name': want['name'] if want['constraint'] else None,
                 'constraint_table': want['table'] if want['constraint'] else None,
                 'has_constraint_relation': referenced is not None, 'referenced_table': referenced,
                 'has_constraint_index': False, 'constraint_index': None}
        for field, value in links.items():
            if field not in got:
                result.record('triggers', identity, field + '-visibility', 'INCOMPLETE')
            result.exact('triggers', identity, field, value, got.get(field))
        result.exact('triggers', identity, 'dependency-edges', pg17.user_trigger_dependencies(want),
                     sorted(got.get('dependencies', []), key=source.canonical))
        result.exact('triggers', identity, 'arguments', text_hash(''.join(v + '\0' for v in want['arguments'])), got.get('arguments_sha256'))
        result.hash_expr('triggers', identity, 'when', want['when'], got.get('when_sha256'))
    internal = result.mapping('internal-triggers', [r for r in native.get('triggers', []) if r.get('internal')], pg17.internal_identity)
    wanted_internal = {}
    for table, table_info, constraint, native_constraint in matched_source_constraints:
        index_name = native_constraint.get('referenced_unique_index') if constraint['kind'] == 'FOREIGN' else native_constraint.get('index_name')
        for row in pg17.internal_trigger_matrix(table, table_info, constraint, native_constraint['name'], index_name):
            wanted_internal[pg17.internal_identity(row)] = row
    result.sets('internal-triggers', wanted_internal, internal)
    for identity in set(wanted_internal) & set(internal):
        want, got = wanted_internal[identity], internal[identity]
        for field, value in want.items():
            if field != 'name_prefix':
                if field not in got:
                    result.record('internal-triggers', identity, field + '-visibility', 'INCOMPLETE')
                actual = sorted(got.get(field, []), key=source.canonical) if field == 'dependencies' else got.get(field)
                result.exact('internal-triggers', identity, field, value, actual)
        result.exact('internal-triggers', identity, 'source-generated-name', True,
                     pg17.native_internal_name_matches(got.get('name', ''), want['name_prefix']))
    policies = result.mapping('policies', native.get('policies'), lambda r: r['table_name'] + '/' + r['name'])
    result.sets('policies', expected['policies'], policies)
    for identity in set(expected['policies']) & set(policies):
        want, got = expected['policies'][identity], policies[identity]
        for field, value in {'command': {'all': '*', 'select': 'r', 'insert': 'a', 'update': 'w', 'delete': 'd'}[want['command']],
                             'roles': sorted(want['roles']), 'permissive': want['permissive']}.items():
            result.exact('policies', identity, field, value, sorted(got.get(field, [])) if field == 'roles' else got.get(field))
        result.hash_expr('policies', identity, 'using', want['using'], got.get('using_sha256'))
        result.hash_expr('policies', identity, 'with-check', want['with_check'], got.get('with_check_sha256'))
    try:
        wanted_acl = _acl_expected(expected, public_schema_owner)
        wanted_public = [r for r in wanted_acl if r['object'] == 'public']
        wanted_acl = [r for r in wanted_acl if r['object'] != 'public']
        result.exact('ACL', 'ACL', 'all-nonowner-object-column-grants', sorted(wanted_acl, key=source.canonical), sorted(native.get('nonowner_acl', []), key=source.canonical))
        public_expected = [{k: v for k, v in r.items() if k not in ('kind', 'object', 'column')} for r in wanted_public]
        public_actual = native.get('public_wa_schema_acl', [])
        if public_schema_owner is None:
            result.record('public-exception', 'public', 'registered-owner-and-complete-wa-grants', 'INCOMPLETE')
        else:
            result.exact('public-exception', 'public', 'wa-schema-grants', sorted(public_expected, key=source.canonical), sorted(public_actual, key=source.canonical))
            result.exact('public-exception', 'public', 'registered-owner', public_schema_owner, native.get('public_schema_owner'))
    except source.ManifestError:
        result.record('ACL', 'ACL', 'source-or-public-owner-grantor-provenance', 'INCOMPLETE')
    if public_acl_registration is None:
        result.record('public-exception', 'public', 'full-public-baseline-ACL-registration', 'INCOMPLETE')
    else:
        result.exact('public-exception', 'public', 'full-public-baseline-ACL',
                     sorted(public_acl_registration, key=source.canonical),
                     sorted(native.get('public_schema_acl', []), key=source.canonical))
    owner_acl = []
    for kind, mapping in [('SCHEMA', expected['schemas']), ('TABLE', expected['tables']),
                          ('FUNCTION', expected['functions']), ('TYPE', expected['enums'])]:
        for identity, info in mapping.items():
            for privilege in source.PRIVILEGES[kind]:
                owner_acl.append({'kind': kind, 'object': identity, 'column': None,
                    'grantee': info['owner'], 'grantor': info['owner'],
                    'privilege': privilege, 'grant_option': False})
    result.exact('ACL', 'ACL', 'complete-owner-ordinary-privileges', sorted(owner_acl, key=source.canonical),
                 sorted(native.get('owner_acl', []), key=source.canonical))
    result.exact('ACL', 'ACL', 'generated-row-array-type-collector-ACL-projection',
                 pg17.generated_type_acl_projection(expected),
                 sorted(native.get('generated_type_acl', []), key=source.canonical))
    actual_defaults = result.mapping('default-ACL', native.get('default_acl'), lambda r: r['creator'] + '/' + r['schema'] + '/' + r['kind'])
    explicit_defaults = {(r['creator'], r['schema'], r['kind'], r['grantee']): r['privileges'] for r in expected['default_acl']}
    wanted_defaults = {}
    for creator in expected['roles']:
        for schema in ('*', 'app', 'platform', 'platform_private'):
            for kind in ('TABLE', 'SEQUENCE', 'FUNCTION', 'TYPE', 'SCHEMA'):
                if kind == 'SCHEMA' and schema != '*':
                    continue
                entries = []
                default = ['EXECUTE'] if kind == 'FUNCTION' and schema == '*' else ['USAGE'] if kind == 'TYPE' and schema == '*' else []
                for privilege in explicit_defaults.get((creator, schema, kind, 'PUBLIC'), default):
                    entries.append({'grantee': 'PUBLIC', 'grantor': creator, 'privilege': privilege, 'grant_option': False})
                wanted_defaults[creator + '/' + schema + '/' + kind] = entries
    result.sets('default-ACL', wanted_defaults, actual_defaults)
    for identity in set(wanted_defaults) & set(actual_defaults):
        result.exact('default-ACL', identity, 'nonowner-default-grants', sorted(wanted_defaults[identity], key=source.canonical), sorted(actual_defaults[identity]['entries'], key=source.canonical))
    result.exact('default-ACL', 'default-ACL', 'outside-registered-schemas', [], native.get('default_acl_outside_registered_schemas'))
    public_relations = native.get('public_owned_relations', [])
    if ledger_registration is None:
        if public_relations:
            result.record('ledger', 'ledger', 'registered-public-client-ledger-exception', 'INCOMPLETE')
    elif isinstance(ledger_registration, dict) and ledger_registration.get('format') == 'workinants.prisma-ledger-registration.v1':
        import prisma_ledger_proof
        result.exact('ledger', 'ledger', 'registered-public-owned-relation-metadata',
                     [prisma_ledger_proof.public_relation()], public_relations)
        proof = prisma_ledger_proof.compare_proof(ledger_registration, ledger_evidence, native,
            bootstrap_grantor=bootstrap_grantor, source_expected_sha256=manifest['expected_sha256'], root=root)
        for check in proof['checks']:
            result.record('ledger', 'public._prisma_migrations', check['field'], check['status'],
                          check['expected_sha256'], check['actual_sha256'])
    else:
        result.exact('ledger', 'ledger', 'registered-public-owned-relation-metadata', ledger_registration, public_relations)
        result.record('ledger', 'ledger', 'ledger-column-index-history-checksum-verification', 'INCOMPLETE')
    for row in public_relations:
        if row.get('object') != 'public._prisma_migrations':
            result.record('public-exception', row.get('object'), 'unexpected-public-owned-relation', 'FAIL')
    result.exact('extensions', 'extensions', 'native-baseline', [{'name': 'plpgsql', 'version': '1.0', 'schema': 'pg_catalog', 'owner': bootstrap_grantor}], native.get('extensions'))
    status = 'FAIL' if result.totals['FAIL'] else 'INCOMPLETE' if result.totals['INCOMPLETE'] else 'PASS'
    return {'format': 'workinants.catalog-comparison.v1', 'status': status, 'case_id': 'P0C-CATALOG-01',
            'source_expected_sha256': manifest['expected_sha256'], 'native_snapshot_sha256': source.digest(native),
            'check_counts': dict(result.totals), 'findings': result.findings,
            'database_contacted_by_comparator': False, 'database_posture': 'D',
            'pg17_rule_release': pg17.PG_RELEASE, 'pg17_rule_sources': pg17.SOURCES,
            'limit': 'Public owner baseline and genuine Prisma ledger require separate reviewed evidence; unresolved expression hashes remain INCOMPLETE. Array effective USAGE follows verified element ACL; generated-type rows compare the collector default-ACL projection.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=source.ROOT)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--pins', type=Path)
    parser.add_argument('--bootstrap-grantor', required=True)
    parser.add_argument('--bootstrap-superuser', action='store_true')
    parser.add_argument('--public-schema-owner')
    parser.add_argument('--public-schema-acl-registration', type=Path)
    parser.add_argument('--ledger-registration', type=Path)
    parser.add_argument('--ledger-evidence', type=Path)
    parser.add_argument('--expression-oracle-evidence', type=Path)
    parser.add_argument('--oracle-database')
    args = parser.parse_args()
    pins = json.loads(args.pins.read_text(encoding='utf-8')) if args.pins else None
    registration = json.loads(args.ledger_registration.read_text(encoding='utf-8')) if args.ledger_registration else None
    ledger_evidence = json.loads(args.ledger_evidence.read_text(encoding='utf-8')) if args.ledger_evidence else None
    public_acl = json.loads(args.public_schema_acl_registration.read_text(encoding='utf-8')) if args.public_schema_acl_registration else None
    oracle_evidence = json.loads(args.expression_oracle_evidence.read_text(encoding='utf-8')) if args.expression_oracle_evidence else None
    manifest = source.build_manifest(args.root, pins)
    snapshot = json.loads(args.snapshot.read_text(encoding='utf-8'))
    report = compare_manifest(manifest, snapshot, bootstrap_grantor=args.bootstrap_grantor,
                              bootstrap_superuser=args.bootstrap_superuser,
                              public_schema_owner=args.public_schema_owner,
                              public_acl_registration=public_acl, ledger_registration=registration,
                              ledger_evidence=ledger_evidence,
                              expression_oracle_evidence=oracle_evidence, oracle_database=args.oracle_database, root=args.root)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 2)


if __name__ == '__main__':
    main()
