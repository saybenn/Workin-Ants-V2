#!/usr/bin/env python3
"""Compile source expectations for P0C-CATALOG-01 without executing SQL.

Requires the existing isolated pglast==7.21 / PostgreSQL 17 parser. This module
does not import a database client, shell, subprocess or network library. It reads
the integrated application packet exactly once (never appends raw structure SQL).

The result is an EXPECTED manifest, not an observed catalog or parity verdict.
PostgreSQL expression deparsing/type resolution is deliberately not simulated:
source expression ASTs and hashes remain explicit for a separately reviewed
native collector/comparator. Unnamed constraints must match by full semantics;
the comparator must not discard them or equate object counts with parity.

By default JSON is written to stdout. --pins accepts a JSON path -> SHA-256 map
binding every input; without it the result is fingerprinted and needs review.
No credentials, environment variables, database URLs or live target are read.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import pglast
from pglast.parser import parse_sql_json


ROOT = Path(__file__).resolve().parents[2]
INPUTS = (
    'review-output/foundation-bootstrap.review.sql',
    'review-output/foundation-application.review.sql',
    'review-output/foundation-bootstrap-finalize.review.sql',
    'scripts/sql-review/foundation-bootstrap-finalize.sql',
    'prisma/review/foundation-candidate.prisma',
    'context/reconciliation/foundation-sql-draft-models.json',
    'context/reconciliation/foundation-sql-draft-access.json',
    'context/reconciliation/foundation-sql-verifier-access.json',
)
ORIGINAL_GRANTOR = '<original-bootstrap-grantor>'
PUBLIC_SCHEMA_OWNER = '<independently-verified-public-schema-owner>'
BUILTINS = set(('bool bytea bpchar char cidr date float4 float8 inet int2 int4 '
                'int8 interval json jsonb name numeric oid record text time '
                'timestamp timestamptz timetz trigger uuid varchar void').split())
PRIVILEGES = {
    'TABLE': ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER', 'MAINTAIN'),
    'SEQUENCE': ('SELECT', 'UPDATE', 'USAGE'),
    'FUNCTION': ('EXECUTE',),
    'SCHEMA': ('USAGE', 'CREATE'),
    'TYPE': ('USAGE',),
}
MANAGED_REVOCATION_BODY = """DECLARE r text; BEGIN
 FOREACH r IN ARRAY ARRAY['anon','authenticated','service_role'] LOOP
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname=r) THEN
   EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA app,platform FROM %I',r);
   EXECUTE format('REVOKE ALL ON SCHEMA app,platform,platform_private FROM %I',r);
   EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM %I',r);
  END IF;
 END LOOP;
END"""


class ManifestError(ValueError):
    """Fail closed on unsupported or inconsistent source."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return sha256(canonical(value).encode('utf-8')).hexdigest()


def clean(value):
    """Remove parser byte positions, retaining semantic order and every value."""
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()
                if k not in ('location', 'stmt_location', 'stmt_len', 'arg_location')}
    return value


def node(value, expected=None):
    if not isinstance(value, dict) or len(value) != 1:
        raise ManifestError('expected one tagged PostgreSQL AST node')
    kind, data = next(iter(value.items()))
    if expected and kind != expected:
        raise ManifestError('expected AST kind ' + expected + ', got ' + kind)
    return data


def literal(value):
    if not isinstance(value, dict):
        return value
    if 'A_Const' in value:
        value = value['A_Const']
        if value.get('isnull'):
            return None
        for key in ('sval', 'ival', 'fval', 'boolval'):
            if key in value:
                return value[key].get(key, False if key == 'boolval' else 0)
    for tag, key, default in (('String', 'sval', ''), ('Boolean', 'boolval', False),
                              ('Integer', 'ival', 0), ('Float', 'fval', '0')):
        if tag in value:
            return value[tag].get(key, default)
    raise ManifestError('unsupported literal AST kind')


def names(values):
    return [node(v, 'String')['sval'] for v in values]


def relation(value):
    if 'RangeVar' in value:
        value = value['RangeVar']
    if not value.get('schemaname'):
        raise ManifestError('unqualified relation in expected packet')
    return value['schemaname'] + '.' + value['relname']


def role(value, current):
    if 'RoleSpec' in value:
        value = value['RoleSpec']
    kind = value['roletype']
    if kind == 'ROLESPEC_PUBLIC':
        return 'PUBLIC'
    if kind == 'ROLESPEC_CURRENT_USER':
        return current
    if kind != 'ROLESPEC_CSTRING':
        raise ManifestError('unsupported role reference ' + kind)
    return value['rolename']


def typename(value):
    if 'TypeName' in value:
        value = value['TypeName']
    parts = names(value['names'])
    if len(parts) == 1 and parts[0] in BUILTINS:
        parts.insert(0, 'pg_catalog')
    if len(parts) != 2:
        raise ManifestError('unresolved source type ' + '.'.join(parts))
    return {'name': '.'.join(parts),
            'array_dimensions': len(value.get('arrayBounds', [])),
            'typmods_ast': clean(value.get('typmods', [])),
            'setof': value.get('setof', False)}


def type_identity(value):
    info = typename(value)
    return info['name'] + '[]' * info['array_dimensions']


def function_identity(value):
    if 'ObjectWithArgs' in value:
        value = value['ObjectWithArgs']
    return '.'.join(names(value['objname'])) + '(' + ','.join(
        type_identity(v) for v in value.get('objargs', [])) + ')'


def expression(value):
    return None if value is None else {'ast': clean(value), 'ast_sha256': digest(clean(value))}


def prisma_default_expression(attributes):
    start = attributes.find('@default(')
    if start < 0:
        return None
    start += len('@default(')
    depth, quoted, escaped = 1, False, False
    end = start
    for end in range(start, len(attributes)):
        char = attributes[end]
        if escaped:
            escaped = False
            continue
        if quoted and char == '\\':
            escaped = True
        elif char == '"':
            quoted = not quoted
        elif not quoted and char == '(':
            depth += 1
        elif not quoted and char == ')':
            depth -= 1
            if depth == 0:
                break
    if depth or quoted:
        raise ManifestError('malformed Prisma default')
    value = attributes[start:end].strip()
    if re.fullmatch(r'(?:uuid|cuid|ulid)\(\)', value):
        return None
    if value == 'now()':
        sql = 'CURRENT_TIMESTAMP'
    elif value.startswith('dbgenerated(') and value.endswith(')'):
        sql = json.loads(value[len('dbgenerated('):-1])
    elif value.startswith('"'):
        sql = "'" + json.loads(value).replace("'", "''") + "'"
    elif value in ('true', 'false') or re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        sql = value
    elif re.fullmatch(r'[A-Za-z_]\w*', value):
        sql = "'" + value + "'"
    else:
        raise ManifestError('unsupported Prisma default form')
    parsed = json.loads(parse_sql_json('SELECT ' + sql))['stmts']
    if len(parsed) != 1 or 'SelectStmt' not in parsed[0]['stmt']:
        raise ManifestError('Prisma default must be one expression')
    select = parsed[0]['stmt']['SelectStmt']
    if set(select) - {'targetList', 'limitOption', 'op'} or len(select['targetList']) != 1:
        raise ManifestError('unsupported Prisma default expression structure')
    return expression(node(select['targetList'][0], 'ResTarget')['val'])


class ManifestCompiler:
    """Interpret only the reviewed packet's declarative DDL/ACL subset."""

    def __init__(self, *, original_bootstrap_superuser=True):
        self.roles = {}
        self.schemas = {}
        self.enums = {}
        self.tables = {}
        self.functions = {}
        self.indexes = {}
        self.policies = {}
        self.triggers = {}
        self.memberships = {}
        self.acl = {}
        self.default_acl = {}
        self.acl_events = []
        self.default_acl_events = []
        self.assertion_blocks = []
        self.conditional_acl_absences = []
        self.statement_counts = {}
        self.current = ORIGINAL_GRANTOR
        self.original_bootstrap_superuser = original_bootstrap_superuser

    def _default_public(self, kind, owner, schema):
        # Global defaults replace acldefault; schema defaults only add grants.
        baseline = {'FUNCTION': {'EXECUTE'}, 'TYPE': {'USAGE'}}.get(kind, set())
        global_key = (owner, '*', kind, 'PUBLIC')
        result = set(self.default_acl.get(global_key, baseline))
        result |= set(self.default_acl.get((owner, schema, kind, 'PUBLIC'), set()))
        return result

    def _new_object(self, kind, identity, schema, owner):
        for privilege in self._default_public(kind, owner, schema):
            self.acl[(kind, identity, 'PUBLIC', privilege, None)] = {
                'grantor': owner, 'grant_option': False, 'origin': 'creator_default'}

    def _constraint(self, table, raw, column=None):
        data = node(raw, 'Constraint')
        kind = data['contype'].removeprefix('CONSTR_')
        if kind == 'NOTNULL':
            return
        if kind == 'DEFAULT':
            return
        if kind not in ('PRIMARY', 'UNIQUE', 'FOREIGN', 'CHECK', 'EXCLUSION'):
            raise ManifestError('unsupported table constraint ' + kind)
        item = {
            'name': data.get('conname'), 'kind': kind,
            'columns': names(data.get('keys', data.get('fk_attrs', []))) or ([column] if column else []),
            'deferrable': data.get('deferrable', False),
            'initially_deferred': data.get('initdeferred', False),
            'validated': not data.get('skip_validation', False),
            'no_inherit': data.get('is_no_inherit', False),
            'nulls_not_distinct': data.get('nulls_not_distinct', False),
            'expression': expression(data.get('raw_expr')),
            'ast': clean(data),
        }
        if kind == 'FOREIGN':
            item.update(references=relation(data['pktable']),
                        referenced_columns=names(data.get('pk_attrs', [])),
                        match=data.get('fk_matchtype', 's'),
                        update_action=data.get('fk_upd_action', 'a'),
                        delete_action=data.get('fk_del_action', 'a'))
        item['semantic_sha256'] = digest({k: v for k, v in item.items() if k not in ('name', 'ast')})
        self.tables[table]['constraints'].append(item)
        if kind == 'PRIMARY':
            for col in item['columns']:
                self.tables[table]['columns'][col]['nullable'] = False
        if kind in ('PRIMARY', 'UNIQUE', 'EXCLUSION'):
            self.tables[table]['constraint_indexes'].append({
                'constraint_name': item['name'], 'constraint_semantic_sha256': item['semantic_sha256'],
                'name_resolution': 'explicit' if item['name'] else 'native_generated_match_full_semantics',
                'columns': item['columns'], 'primary': kind == 'PRIMARY',
                'unique': kind in ('PRIMARY', 'UNIQUE'), 'valid': True, 'ready': True,
                'nulls_not_distinct': item['nulls_not_distinct'],
                'access_method': data.get('access_method') or 'btree',
            })

    def _table(self, data):
        identity = relation(data['relation'])
        if identity in self.tables:
            raise ManifestError('duplicate table ' + identity)
        self.tables[identity] = {
            'owner': self.current, 'relkind': 'r',
            'persistence': data['relation'].get('relpersistence', 'p'),
            'rls': False, 'force_rls': False, 'columns': {},
            'constraints': [], 'constraint_indexes': [],
            'declaration_ast': clean(data),
        }
        pending = []
        for ordinal, raw in enumerate(data.get('tableElts', []), 1):
            if 'Constraint' in raw:
                pending.append((raw, None))
                continue
            col = node(raw, 'ColumnDef')
            constraints = [node(c, 'Constraint') for c in col.get('constraints', [])]
            allowed = {'CONSTR_NOTNULL', 'CONSTR_DEFAULT', 'CONSTR_PRIMARY',
                       'CONSTR_UNIQUE', 'CONSTR_FOREIGN', 'CONSTR_CHECK'}
            if any(c['contype'] not in allowed for c in constraints):
                raise ManifestError('unsupported column constraint ' + identity + '.' + col['colname'])
            defaults = [c for c in constraints if c['contype'] == 'CONSTR_DEFAULT']
            if len(defaults) > 1 or col.get('identity') or col.get('generated'):
                raise ManifestError('unsupported generated/default column')
            self.tables[identity]['columns'][col['colname']] = {
                'ordinal': len(self.tables[identity]['columns']) + 1,
                'type': typename(col['typeName']),
                'nullable': not any(c['contype'] in ('CONSTR_NOTNULL', 'CONSTR_PRIMARY') for c in constraints),
                'default': expression(defaults[0]['raw_expr']) if defaults else None,
                'collation_ast': clean(col.get('collClause')),
                'identity': '', 'generated': '',
            }
            pending.extend((c, col['colname']) for c in col.get('constraints', []))
        for constraint, column in pending:
            self._constraint(identity, constraint, column)
        self._new_object('TABLE', identity, identity.split('.')[0], self.current)

    def _function(self, data):
        parameters = [node(p, 'FunctionParameter') for p in data.get('parameters', [])]
        inputs = [p for p in parameters if p.get('mode', 'FUNC_PARAM_DEFAULT') not in ('FUNC_PARAM_OUT', 'FUNC_PARAM_TABLE')]
        identity = '.'.join(names(data['funcname'])) + '(' + ','.join(type_identity(p['argType']) for p in inputs) + ')'
        options = {node(o, 'DefElem')['defname']: node(o, 'DefElem')['arg'] for o in data['options'] if node(o, 'DefElem')['defname'] != 'set'}
        bodies = node(options['as'], 'List')['items']
        if len(bodies) != 1 or data.get('is_procedure'):
            raise ManifestError('unsupported function form ' + identity)
        body = literal(bodies[0])
        settings = []
        for opt in data['options']:
            opt = node(opt, 'DefElem')
            if opt['defname'] == 'set':
                settings.append(clean(node(opt['arg'], 'VariableSetStmt')))
        value = {
            'name': '.'.join(names(data['funcname'])), 'owner': self.current,
            'parameters': [{'name': p.get('name'), 'mode': p.get('mode', 'FUNC_PARAM_DEFAULT'),
                            'type': typename(p['argType']), 'default': expression(p.get('defexpr'))} for p in parameters],
            'return_type': typename(data['returnType']),
            'language': literal(options['language']),
            'security_definer': literal(options.get('security', {'Boolean': {}})),
            'volatility': literal(options.get('volatility', {'String': {'sval': 'volatile'}})),
            'strict': literal(options.get('strict', {'Boolean': {}})),
            'leakproof': literal(options.get('leakproof', {'Boolean': {}})),
            'parallel': literal(options.get('parallel', {'String': {'sval': 'unsafe'}})),
            'cost': literal(options['cost']) if 'cost' in options else 100,
            'rows': literal(options['rows']) if 'rows' in options else (1000 if data['returnType'].get('setof') else 0),
            'settings_ast': settings, 'body_sha256': sha256(body.encode('utf-8')).hexdigest(),
            'definition_ast_sha256': digest(clean(data)),
        }
        if identity in self.functions and not data.get('replace'):
            raise ManifestError('duplicate function identity ' + identity)
        if identity not in self.functions:
            self._new_object('FUNCTION', identity, value['name'].split('.')[0], self.current)
        self.functions[identity] = value

    def _objects(self, data):
        kind = data['objtype'].removeprefix('OBJECT_')
        if kind not in PRIVILEGES:
            raise ManifestError('unsupported ACL kind ' + kind)
        if data['targtype'] == 'ACL_TARGET_ALL_IN_SCHEMA':
            schemas = names(data['objects'])
            mapping = {'TABLE': self.tables, 'FUNCTION': self.functions,
                       'TYPE': self.enums, 'SEQUENCE': {}}[kind]
            return kind, [key for key in mapping if key.split('.')[0] in schemas]
        if data['targtype'] != 'ACL_TARGET_OBJECT':
            raise ManifestError('unsupported ACL target')
        objects = []
        for raw in data['objects']:
            if kind == 'TABLE':
                objects.append(relation(raw))
            elif kind == 'FUNCTION':
                objects.append(function_identity(raw))
            elif kind == 'SCHEMA':
                objects.append(literal(raw))
            elif kind == 'TYPE':
                objects.append('.'.join(names(node(raw, 'List')['items'])))
            else:
                raise ManifestError('unhandled object ACL ' + kind)
        return kind, objects

    def _grant(self, data):
        kind, objects = self._objects(data)
        event = clean(data)
        event['execution_role'] = self.current
        event['object_grantors'] = {}
        self.acl_events.append(event)
        for identity in objects:
            grantor = self.current
            if self.current == ORIGINAL_GRANTOR and self.original_bootstrap_superuser:
                # PostgreSQL17 records superuser object grants as the object
                # owner; membership grants retain the bootstrap grantor.
                # https://www.postgresql.org/docs/17/sql-grant.html
                mappings = {'SCHEMA': self.schemas, 'TABLE': self.tables,
                            'FUNCTION': self.functions, 'TYPE': self.enums}
                if kind == 'SCHEMA' and identity == 'public':
                    grantor = PUBLIC_SCHEMA_OWNER
                elif kind in mappings and identity in mappings[kind]:
                    grantor = mappings[kind][identity]['owner']
                else:
                    raise ManifestError('unresolved superuser object grantor ' + identity)
            event['object_grantors'][identity] = grantor
            for raw_role in data['grantees']:
                grantee = role(raw_role, self.current)
                privileges = [node(p, 'AccessPriv') for p in data.get('privileges', [])]
                if not privileges:
                    privileges = [{'priv_name': p} for p in PRIVILEGES[kind]]
                for privilege in privileges:
                    name = privilege['priv_name'].upper()
                    if name not in PRIVILEGES[kind]:
                        raise ManifestError('unknown privilege ' + name)
                    cols = names(privilege.get('cols', [])) or [None]
                    for column in cols:
                        if kind == 'TABLE' and identity not in self.tables:
                            raise ManifestError('ACL before table ' + identity)
                        if column and column not in self.tables[identity]['columns']:
                            raise ManifestError('ACL on nonexistent column ' + identity + '.' + column)
                        key = (kind, identity, grantee, name, column)
                        if data.get('is_grant', False):
                            self.acl[key] = {'grantor': grantor, 'grant_option': data.get('grant_option', False), 'origin': 'explicit'}
                        elif data.get('grant_option', False):
                            if key in self.acl:
                                self.acl[key]['grant_option'] = False
                        else:
                            self.acl.pop(key, None)

    def _defaults(self, data):
        opts = {node(o, 'DefElem')['defname']: node(o, 'DefElem')['arg'] for o in data.get('options', [])}
        owners = [role(v, self.current) for v in node(opts['roles'], 'List')['items']] if 'roles' in opts else [self.current]
        schemas = names(node(opts['schemas'], 'List')['items']) if 'schemas' in opts else ['*']
        action = data['action']
        kind = action['objtype'].removeprefix('OBJECT_')
        if kind not in PRIVILEGES:
            raise ManifestError('unsupported default ACL kind ' + kind)
        self.default_acl_events.append(clean(data))
        privileges = [node(v, 'AccessPriv')['priv_name'].upper() for v in action.get('privileges', [])] or list(PRIVILEGES[kind])
        for owner in owners:
            for schema in schemas:
                for raw_role in action['grantees']:
                    grantee = role(raw_role, self.current)
                    key = (owner, schema, kind, grantee)
                    if key not in self.default_acl:
                        self.default_acl[key] = set({'FUNCTION': ['EXECUTE'], 'TYPE': ['USAGE']}.get(kind, [])) if schema == '*' and grantee == 'PUBLIC' else set()
                    if action.get('is_grant', False):
                        self.default_acl[key].update(privileges)
                    else:
                        self.default_acl[key].difference_update(privileges)

    def consume(self, sql, phase):
        if pglast.__version__ != 'v7.21':
            raise ManifestError('requires pinned pglast v7.21')
        self.current = 'wa_migrator' if phase == 'application' else ORIGINAL_GRANTOR
        statements = json.loads(parse_sql_json(sql))['stmts']
        counts = Counter()
        for raw in statements:
            kind = next(iter(raw['stmt']))
            data = raw['stmt'][kind]
            counts[kind] += 1
            if kind == 'TransactionStmt':
                if data['kind'] not in ('TRANS_STMT_BEGIN', 'TRANS_STMT_COMMIT'):
                    raise ManifestError('unsupported source transaction statement')
            elif kind == 'VariableSetStmt':
                if data['name'] == 'role':
                    self.current = literal(data['args'][0]) if data['kind'] == 'VAR_SET_VALUE' else ('wa_migrator' if phase == 'application' else ORIGINAL_GRANTOR)
                elif data['name'] != 'search_path':
                    raise ManifestError('unhandled session setting ' + data['name'])
            elif kind == 'CreateRoleStmt':
                options = {node(v, 'DefElem')['defname']: literal(node(v, 'DefElem')['arg']) for v in data.get('options', [])}
                if data['role'] in self.roles:
                    raise ManifestError('duplicate role')
                self.roles[data['role']] = {
                    'options': options,
                    'native_attributes': {
                        'rolsuper': options.get('superuser', False),
                        'rolinherit': options.get('inherit', True),
                        'rolcreaterole': options.get('createrole', False),
                        'rolcreatedb': options.get('createdb', False),
                        'rolcanlogin': options.get('canlogin', False),
                        'rolreplication': options.get('isreplication', False),
                        'rolbypassrls': options.get('bypassrls', False),
                        'rolconnlimit': options.get('connectionlimit', -1),
                        'rolvaliduntil': options.get('validUntil'), 'rolconfig': None,
                    },
                    'password_verifier': 'not_part_of_source_manifest',
                }
            elif kind == 'GrantRoleStmt':
                options = {node(v, 'DefElem')['defname']: literal(node(v, 'DefElem')['arg']) for v in data.get('opt', [])}
                grantor = role(data['grantor'], self.current) if data.get('grantor') else self.current
                for granted in data['granted_roles']:
                    for member in data['grantee_roles']:
                        key = (node(granted, 'AccessPriv')['priv_name'], role(member, self.current), grantor)
                        if data.get('is_grant', False):
                            self.memberships[key] = options
                        else:
                            self.memberships.pop(key, None)
            elif kind == 'CreateSchemaStmt':
                owner = role(data['authrole'], self.current) if data.get('authrole') else self.current
                self.schemas[data['schemaname']] = {'owner': owner, 'declaration_ast': clean(data)}
            elif kind == 'AlterDefaultPrivilegesStmt':
                self._defaults(data)
            elif kind == 'CreateEnumStmt':
                identity = '.'.join(names(data['typeName']))
                self.enums[identity] = {'labels': names(data['vals']), 'owner': self.current}
                self._new_object('TYPE', identity, identity.split('.')[0], self.current)
            elif kind == 'CreateStmt':
                self._table(data)
            elif kind == 'CreateFunctionStmt':
                self._function(data)
            elif kind == 'AlterTableStmt':
                table = relation(data['relation'])
                if table not in self.tables:
                    raise ManifestError('ALTER before table ' + table)
                for cmd in data['cmds']:
                    cmd = node(cmd, 'AlterTableCmd')
                    subtype = cmd['subtype']
                    if subtype == 'AT_AddConstraint':
                        self._constraint(table, cmd['def'])
                    elif subtype == 'AT_EnableRowSecurity':
                        self.tables[table]['rls'] = True
                    elif subtype == 'AT_ForceRowSecurity':
                        self.tables[table]['force_rls'] = True
                    else:
                        raise ManifestError('unsupported ALTER TABLE subtype ' + subtype)
            elif kind == 'IndexStmt':
                table = relation(data['relation'])
                identity = table.split('.')[0] + '.' + data['idxname']
                self.indexes[identity] = {'table': table, 'owner': self.tables[table]['owner'],
                    'access_method': data.get('accessMethod', 'btree'),
                    'unique': data.get('unique', False), 'primary': data.get('primary', False),
                    'nulls_not_distinct': data.get('nulls_not_distinct', False),
                    'valid': True, 'ready': True, 'keys_ast': clean(data.get('indexParams', [])),
                    'include_ast': clean(data.get('indexIncludingParams', [])),
                    'predicate': expression(data.get('whereClause')), 'ast': clean(data)}
            elif kind == 'GrantStmt':
                self._grant(data)
            elif kind == 'CreatePolicyStmt':
                table = relation(data['table'])
                self.policies[table + '/' + data['policy_name']] = {
                    'table': table, 'name': data['policy_name'], 'command': data['cmd_name'],
                    'permissive': data.get('permissive', False),
                    'roles': sorted(role(v, self.current) for v in data.get('roles', [])),
                    'using': expression(data.get('qual')), 'with_check': expression(data.get('with_check')),
                    'ast': clean(data)}
            elif kind == 'CreateTrigStmt':
                table = relation(data['relation'])
                self.triggers[table + '/' + data['trigname']] = {
                    'table': table, 'name': data['trigname'],
                    'function': '.'.join(names(data['funcname'])),
                    'row': data.get('row', False), 'timing_bits': data.get('timing', 0),
                    'event_bits': data['events'], 'enabled': 'O',
                    'constraint': data.get('isconstraint', False),
                    'deferrable': data.get('deferrable', False),
                    'initially_deferred': data.get('initdeferred', False),
                    'arguments': names(data.get('args', [])),
                    'when': expression(data.get('whenClause')), 'ast': clean(data)}
            elif kind == 'AlterOwnerStmt':
                if data['objectType'] != 'OBJECT_FUNCTION':
                    raise ManifestError('unsupported ownership transfer')
                identity = function_identity(data['object'])
                old_owner = self.functions[identity]['owner']
                new_owner = role(data['newowner'], self.current)
                self.functions[identity]['owner'] = new_owner
                for key, grant in self.acl.items():
                    if key[:2] == ('FUNCTION', identity) and grant['grantor'] == old_owner:
                        grant['grantor'] = new_owner
            elif kind == 'DoStmt':
                options = {node(v, 'DefElem')['defname']: literal(node(v, 'DefElem')['arg']) for v in data['args']}
                body = options['as']
                if phase == 'application':
                    if ' '.join(body.split()) != ' '.join(MANAGED_REVOCATION_BODY.split()):
                        raise ManifestError('unrecognized dynamic application DDL/ACL block')
                    self.conditional_acl_absences = [
                        {'role': r, 'if_role_exists': True, 'kind': k, 'schemas': ss}
                        for r in ('anon', 'authenticated', 'service_role')
                        for k, ss in [('TABLE', ['app', 'platform']),
                                      ('SCHEMA', ['app', 'platform', 'platform_private']),
                                      ('FUNCTION', ['platform_private'])]]
                elif phase != 'finalize':
                    raise ManifestError('unrecognized procedural source block')
                self.assertion_blocks.append({'phase': phase, 'body_sha256': sha256(body.encode('utf-8')).hexdigest(),
                                              'assertion_execution': 'NOT_RUN'})
            else:
                raise ManifestError('unhandled SQL statement kind ' + kind)
        self.statement_counts[phase] = dict(sorted(counts.items()))

    def result(self):
        grouped = {}
        for (kind, identity, grantee, privilege, column), value in self.acl.items():
            key = (kind, identity, grantee, privilege, value['grantor'], value['grant_option'], column is None)
            grouped.setdefault(key, []).extend([] if column is None else [column])
        acl = [{'kind': k, 'object': o, 'grantee': r, 'privilege': p, 'grantor': g,
                'grant_option': opt, 'scope': 'object' if whole else 'columns',
                'columns': sorted(columns)} for (k, o, r, p, g, opt, whole), columns in grouped.items()]
        return {
            'roles': dict(sorted(self.roles.items())), 'schemas': dict(sorted(self.schemas.items())),
            'enums': dict(sorted(self.enums.items())), 'tables': dict(sorted(self.tables.items())),
            'functions': dict(sorted(self.functions.items())), 'explicit_indexes': dict(sorted(self.indexes.items())),
            'policies': dict(sorted(self.policies.items())), 'triggers': dict(sorted(self.triggers.items())),
            'memberships': [{'role': r, 'member': m, 'grantor': g, **v} for (r, m, g), v in sorted(self.memberships.items())],
            'nonowner_acl': sorted(acl, key=canonical),
            'default_acl': [{'creator': owner, 'schema': schema, 'kind': kind, 'grantee': grantee,
                             'privileges': sorted(values)} for (owner, schema, kind, grantee), values in sorted(self.default_acl.items())],
            'acl_source_operations': self.acl_events, 'default_acl_source_operations': self.default_acl_events,
            'conditional_acl_absences': self.conditional_acl_absences,
            'procedural_assertions': self.assertion_blocks, 'statement_counts': self.statement_counts,
        }


def prisma_crosscheck(text, expected, models):
    """Parse the repository's bounded Prisma declaration grammar, never run Prisma."""
    blocks = {n: (k, b) for k, n, b in re.findall(r'^(model|enum)\s+(\w+)\s*\{(.*?)^\}', text, re.M | re.S)}
    result = {'models': {}, 'enums': {}}
    for name, (kind, body) in blocks.items():
        schema = re.search(r'@@schema\("([^"\n]+)"\)', body)
        native = re.search(r'@@map\("([^"\n]+)"\)', body)
        if not schema or not native:
            raise ManifestError('unmapped Prisma declaration ' + name)
        identity = schema[1] + '.' + native[1]
        fields = []
        for line in body.splitlines():
            match = re.match(r'^\s*(\w+)\s+([\w\[\]?]+)(.*)$', line)
            if match and not line.strip().startswith(('/', '*', '@')):
                fields.append(match.groups())
        if kind == 'model':
            scalar = [(n, typ, attrs) for n, typ, attrs in fields
                      if typ.rstrip('?[]') not in blocks or blocks[typ.rstrip('?[]')][0] == 'enum']
            columns = []
            declarations = []
            for field, typ, attrs in scalar:
                mapped = re.search(r'@map\("([^"\n]+)"\)', attrs)
                column = mapped[1] if mapped else field
                columns.append(column)
                declarations.append({'field': field, 'column': column, 'prisma_type': typ,
                                     'attributes': attrs.strip()})
            if identity not in expected['tables'] or columns != list(expected['tables'][identity]['columns']):
                raise ManifestError('Prisma/SQL ordered column mismatch ' + name)
            for declaration in declarations:
                col = expected['tables'][identity]['columns'][declaration['column']]
                typ = declaration['prisma_type']
                base = typ.rstrip('?[]')
                attrs = declaration['attributes']
                native = re.search(r'@db\.(\w+)(?:\(([^)]*)\))?', attrs)
                modifiers = []
                if native:
                    native_name = {'Uuid': 'uuid', 'Char': 'bpchar', 'Timestamptz': 'timestamptz'}.get(native[1])
                    if not native_name:
                        raise ManifestError('unhandled Prisma native type ' + native[1])
                    if native[2]:
                        modifiers = [{'A_Const': {'ival': {'ival': int(x.strip())}}} for x in native[2].split(',')]
                    native_name = 'pg_catalog.' + native_name
                elif base in blocks and blocks[base][0] == 'enum':
                    enum_body = blocks[base][1]
                    native_name = re.search(r'@@schema\("([^"]+)"\)', enum_body)[1] + '.' + re.search(r'@@map\("([^"]+)"\)', enum_body)[1]
                else:
                    native_name = 'pg_catalog.' + {'String': 'text', 'Int': 'int4', 'BigInt': 'int8',
                        'Boolean': 'bool', 'Float': 'float8', 'Json': 'jsonb'}[base]
                declared_type = {'name': native_name, 'array_dimensions': 1 if typ.endswith('[]') else 0,
                                 'typmods_ast': modifiers, 'setof': False}
                if declared_type != col['type'] or (not typ.endswith('[]') and typ.endswith('?') != col['nullable']):
                    raise ManifestError('Prisma/SQL type or nullability mismatch ' + identity + '.' + declaration['column'])
                if typ.endswith('[]'):
                    # Prisma's list representation does not emit PostgreSQL
                    # NOT NULL here. Preserve the actual SQL expectation.
                    declaration['physical_nullable'] = col['nullable']
                    declaration['nullability_rule'] = 'compare reviewed SQL array nullability exactly; no inferred NOT NULL'
                # Prisma uuid()/cuid()/ulid() are client defaults, not SQL DDL.
                client_default = bool(re.search(r'@default\((?:uuid|cuid|ulid)\(\)\)', attrs))
                declaration['client_only_default'] = client_default
                has_default = '@default(' in attrs and not client_default
                if has_default != (col['default'] is not None):
                    raise ManifestError('Prisma/SQL default presence mismatch ' + identity + '.' + declaration['column'])
                if prisma_default_expression(attrs) != col['default']:
                    raise ManifestError('Prisma/SQL default value mismatch ' + identity + '.' + declaration['column'])
            result['models'][name] = {'object': identity, 'columns': columns, 'scalar_declarations': declarations,
                                     'relationship_declarations': [{'field': n, 'prisma_type': t, 'attributes': a.strip()}
                                         for n, t, a in fields if t.rstrip('?[]') in blocks and blocks[t.rstrip('?[]')][0] == 'model']}
        else:
            labels = []
            for line in body.splitlines():
                match = re.match(r'^\s*(\w+)(?:\s+@map\("([^"\n]+)"\))?\s*$', line)
                if match:
                    labels.append(match[2] or match[1])
            if expected['enums'].get(identity, {}).get('labels') != labels:
                raise ManifestError('Prisma/SQL enum labels mismatch ' + name)
            result['enums'][name] = {'object': identity, 'labels': labels}
    if set(result['models']) != {m['model'] for m in models}:
        raise ManifestError('Prisma/model register selection mismatch')
    for model in models:
        item = result['models'][model['model']]
        if item['object'] != model['object'] or set(item['columns']) != set(model['fields'].values()):
            raise ManifestError('Prisma/model register mapping mismatch ' + model['model'])
        primary = [c['columns'] for c in expected['tables'][item['object']]['constraints'] if c['kind'] == 'PRIMARY']
        if primary != [[model['fields'][f] for f in model['pk']]]:
            raise ManifestError('SQL/model register primary key mismatch ' + model['model'])
    return result


def validate_acl(expected, runtime_access, verifier_access):
    runtime_roles = {'wa_app_runtime', 'wa_worker'}
    runtime = [r for r in expected['nonowner_acl'] if r['kind'] == 'TABLE' and r['grantee'] in runtime_roles]
    actual = {(r['object'], r['grantee'], r['privilege'], tuple(r['columns'])) for r in runtime if r['scope'] == 'columns' and not r['grant_option']}
    models = {m['model']: m['object'] for m in expected['model_register']}
    registered = {(models[r['model']], r['role'], r['operation'], tuple(sorted(r['columns']))) for r in runtime_access}
    if len(actual) != len(runtime) or actual != registered:
        raise ManifestError('runtime ACL differs from independent exact column register')
    for grantee, profile in verifier_access['roles'].items():
        actual_verifier = {(r['object'], tuple(r['columns'])) for r in expected['nonowner_acl']
                           if r['kind'] == 'TABLE' and r['grantee'] == grantee
                           and r['privilege'] == 'SELECT' and r['scope'] == 'columns' and not r['grant_option']}
        required = {(table, tuple(sorted(cols))) for table, cols in profile['columns'].items()}
        extra = [r for r in expected['nonowner_acl'] if r['kind'] == 'TABLE' and r['grantee'] == grantee
                 and (r['privilege'] != 'SELECT' or r['scope'] != 'columns' or r['grant_option'])]
        if actual_verifier != required or extra:
            raise ManifestError('verifier SELECT-only surface mismatch ' + grantee)


def build_manifest(root=ROOT, expected_sha256=None):
    root = Path(root)
    blobs = {path: (root / path).read_bytes() for path in INPUTS}
    fingerprints = {path: sha256(value).hexdigest() for path, value in blobs.items()}
    if expected_sha256 is not None:
        if not set(INPUTS) <= set(expected_sha256):
            raise ManifestError('pin map must bind every manifest input')
        for path, actual in fingerprints.items():
            if expected_sha256[path] != actual:
                raise ManifestError('source fingerprint mismatch ' + path)
    if blobs[INPUTS[2]] != blobs[INPUTS[3]]:
        raise ManifestError('generated finalization differs from authoritative source')
    compiler = ManifestCompiler()
    for phase, path in zip(('bootstrap', 'application', 'finalize'), INPUTS[:3]):
        compiler.consume(blobs[path].decode('utf-8'), phase)
    expected = compiler.result()
    models = json.loads(blobs[INPUTS[5]])
    expected['model_register'] = models
    expected['prisma_declarations'] = prisma_crosscheck(blobs[INPUTS[4]].decode('utf-8'), expected, models)
    selected = {m['object'] for m in models}
    selected |= {'platform_private.identity_service_authorization', 'platform_private.identity_service_receipt'}
    if set(expected['tables']) != selected:
        raise ManifestError('SQL table set differs from 40 models plus two Identity leaves')
    validate_acl(expected, json.loads(blobs[INPUTS[6]]), json.loads(blobs[INPUTS[7]]))
    counts = {name: len(expected[name]) for name in ('roles', 'schemas', 'tables', 'enums', 'functions', 'explicit_indexes', 'policies', 'triggers')}
    counts.update(columns=sum(len(t['columns']) for t in expected['tables'].values()),
                  constraints=sum(len(t['constraints']) for t in expected['tables'].values()),
                  constraint_indexes=sum(len(t['constraint_indexes']) for t in expected['tables'].values()))
    return {
        'format': 'workinants.expected-catalog.v1', 'case_id': 'P0C-CATALOG-01',
        'status': 'EXPECTED_SOURCE_ONLY_NATIVE_PARITY_NOT_RUN', 'database_contacted': False,
        'sql_executed': False, 'database_posture': 'D', 'parser': pglast.__version__,
        'approval_binding': 'ALL_INPUT_HASHES_VERIFIED' if expected_sha256 is not None else 'FINGERPRINTED_REQUIRES_REVIEW',
        'inputs_sha256': fingerprints, 'aggregate_recipe': 'SHA256(UTF8(sorted path + TAB + lowercase sha256 + LF))',
        'environment_assumptions': {
            'original_bootstrap_role': ORIGINAL_GRANTOR,
            'original_bootstrap_requires_superuser': True,
            'public_schema_owner': PUBLIC_SCHEMA_OWNER,
            'public_owner_resolution': 'independently registered native baseline; no default owner assumption',
            'object_grantor_rule': 'PostgreSQL17 superuser object GRANT is recorded as object owner; role memberships retain bootstrap grantor',
            'authority': 'https://www.postgresql.org/docs/17/sql-grant.html',
        },
        'inputs_aggregate_sha256': sha256(''.join(p + '\t' + fingerprints[p] + '\n' for p in sorted(fingerprints)).encode('utf-8')).hexdigest(),
        'expected_sha256': digest(expected), 'counts': counts, 'expected': expected,
        'comparison_contract': {
            'exact_object_sets': True, 'compare_counts_only': False,
            'ignored_fields': ['native OIDs', 'source byte positions', 'ordering of unordered catalog result rows'],
            'required_normalization_review': ['native analyzed/deparsed expression casts and type resolution',
                'unnamed constraint and constraint-index names matched by complete semantics',
                'PostgreSQL-generated relation row/array types and internal FK triggers',
                'owner implicit privileges, acldefault, global plus additive schema defaults',
                'public schema baseline and separately owned Prisma migration ledger',
                'baseline built-in plpgsql extension versus application extension absence'],
            'unplanned_object_kinds_absent': ['views', 'materialized views', 'user sequences', 'application extensions'],
            'baseline_external_schemas': ['public', 'pg_catalog', 'information_schema'],
            'native_parity_status': 'NOT_RUN',
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--pins', type=Path, help='JSON map binding all input SHA-256 values')
    args = parser.parse_args()
    pins = json.loads(args.pins.read_text(encoding='utf-8')) if args.pins else None
    result = build_manifest(args.root, pins)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
