"""Source-derived PostgreSQL 17.11 catalog rules; no database execution.

Limited to ordinary nonpartitioned, noninherited relations in the F0 packet.
Primary sources are the immutable release-tag URLs below, inspected before
implementing these rules. Unsupported partition/inheritance forms fail closed.
The generated-type ACL projection models the existing collector's
COALESCE(typacl,acldefault('T',owner)); array effective USAGE follows its element
type, rather than interpreting the projected PUBLIC row as an independent grant.
"""
import re

import catalog_manifest as source


PG_RELEASE = 'REL_17_11'
SOURCES = {
    'foreign_key_inheritance_and_trigger_matrix': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/commands/tablecmds.c',
        'ranges': ['9568-9619', '11309-11463', '11594-11794'],
        'symbols': ['addFkConstraint', 'transformFkeyCheckAttrs', 'CreateFKCheckTrigger', 'createForeignKeyActionTriggers'],
    },
    'index_constraint_inheritance_and_deferred_trigger': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/index.c',
        'ranges': ['1819-1864', '1888-1914'], 'symbols': ['index_constraint_create'],
    },
    'dependent_type_acl': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/pg_type.c',
        'ranges': ['315-325', '383-394'], 'symbols': ['TypeCreate'],
    },
    'type_acl_defaults_and_owner_flags': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/utils/adt/acl.c',
        'ranges': ['816-820', '840-861'], 'symbols': ['acldefault'],
    },
    'array_effective_usage_delegation': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/aclchk.c',
        'ranges': ['2301-2316', '3592-3617'], 'symbols': ['ExecGrant_Type_check', 'pg_type_aclmask_ext'],
    },
    'user_constraint_trigger_catalog_row_and_internal_names': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/commands/trigger.c',
        'ranges': ['754-803', '813-868', '978-1055'], 'symbols': ['CreateTriggerFiringOn'],
    },
    'pinned_dependencies_are_omitted': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/pg_depend.c',
        'ranges': ['98-106'], 'symbols': ['recordMultipleDependencies'],
    },
    'pinned_object_classification': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/catalog.c',
        'ranges': ['317-372'], 'symbols': ['IsPinnedObject'],
    },
    'release_pinned_trigger_functions': {
        'url': 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/include/catalog/pg_proc.dat',
        'ranges': ['3743-3789'], 'symbols': ['unique_key_recheck', 'RI_FKey_*'],
    },
}
PINNED_TRIGGER_FUNCTIONS = {
    'pg_catalog.unique_key_recheck()': 1250,
    'pg_catalog.RI_FKey_check_ins()': 1644, 'pg_catalog.RI_FKey_check_upd()': 1645,
    'pg_catalog.RI_FKey_cascade_del()': 1646, 'pg_catalog.RI_FKey_cascade_upd()': 1647,
    'pg_catalog.RI_FKey_restrict_del()': 1648, 'pg_catalog.RI_FKey_restrict_upd()': 1649,
    'pg_catalog.RI_FKey_setnull_del()': 1650, 'pg_catalog.RI_FKey_setnull_upd()': 1651,
    'pg_catalog.RI_FKey_setdefault_del()': 1652, 'pg_catalog.RI_FKey_setdefault_upd()': 1653,
    'pg_catalog.RI_FKey_noaction_del()': 1654, 'pg_catalog.RI_FKey_noaction_upd()': 1655,
}


def ordinary_table(info):
    declaration = info.get('declaration_ast', {})
    if info.get('relkind') != 'r' or declaration.get('inhRelations') or declaration.get('partspec'):
        raise source.ManifestError('PG17 rule limited to ordinary noninherited source tables')


def constraint_no_inherit(table, constraint):
    ordinary_table(table)
    if constraint['kind'] == 'CHECK':
        return constraint['no_inherit']
    if constraint['kind'] in ('PRIMARY', 'UNIQUE', 'EXCLUSION', 'FOREIGN'):
        return True
    raise source.ManifestError('unsupported native constraint inheritance form')


def generated_types(expected):
    """Names come from reviewed source, never an initial native observation."""
    base_types = {**expected['tables'], **expected['enums']}
    result = {}
    for identity, info in base_types.items():
        schema, name = identity.split('.')
        if not re.fullmatch(r'[a-z_][a-z_0-9]*', name) or len(name.encode('utf-8')) > 62:
            raise source.ManifestError('array name needs separately reviewed truncation/quoting rule')
        array_name = schema + '._' + name
        if array_name in base_types or array_name in result:
            raise source.ManifestError('array name needs separately reviewed collision rule')
        if identity in expected['tables']:
            ordinary_table(info)
            result[identity] = {'owner': info['owner'], 'kind': 'c', 'category': 'C',
                                'element': None, 'relation': identity, 'usage_delegates_to': None}
        result[array_name] = {'owner': info['owner'], 'kind': 'b', 'category': 'A',
                              'element': identity, 'relation': None, 'usage_delegates_to': identity}
    return result


def generated_type_acl_projection(expected):
    rows = []
    for identity, info in generated_types(expected).items():
        for grantee in ('PUBLIC', info['owner']):
            rows.append({'object': identity, 'grantee': grantee, 'grantor': info['owner'],
                         'privilege': 'USAGE', 'grant_option': False})
    return sorted(rows, key=source.canonical)


def dependency(direction, kind, identity, dependency_type):
    return {'direction': direction, 'class': kind, 'object': identity,
            'dependency_type': dependency_type, 'object_subid': 0, 'referenced_subid': 0}


def user_trigger_reference(trigger):
    value = trigger.get('ast', {}).get('constrrel')
    return source.relation(value) if value else None


def user_trigger_dependencies(trigger):
    if trigger.get('when') or trigger.get('ast', {}).get('columns'):
        raise source.ManifestError('trigger expression/column dependency needs its own reviewed projection')
    result = [dependency('trigger_to', 'relation', trigger['table'], 'a')]
    if trigger['function'] + '()' not in PINNED_TRIGGER_FUNCTIONS:
        result.append(dependency('trigger_to', 'function', trigger['function'] + '()', 'n'))
    referenced = user_trigger_reference(trigger)
    if referenced:
        result.append(dependency('trigger_to', 'relation', referenced, 'a'))
    if trigger['constraint']:
        result.append(dependency('to_trigger', 'constraint', trigger['table'] + '/' + trigger['name'], 'i'))
    return sorted(result, key=source.canonical)


def eligible_fk_indexes(expected, matched_constraints, foreign):
    """Allowed names are bound to source unique-key semantics, never counts."""
    table, columns = foreign['references'], foreign['referenced_columns']
    wanted = set(columns)
    if not columns or len(wanted) != len(columns):
        raise source.ManifestError('explicit distinct referenced source columns required')
    candidates = set()
    for identity, index in expected['explicit_indexes'].items():
        keys = [source.node(k, 'IndexElem').get('name') for k in index['keys_ast']]
        if index['table'] == table and index['owner'] == expected['tables'][table]['owner'] and index['unique'] and index['access_method'] == 'btree' and index['predicate'] is None and None not in keys and len(keys) == len(columns) and set(keys) == wanted:
            candidates.add(identity)
    for parent, info, constraint, native_name_binding in matched_constraints:
        if parent == table and constraint['kind'] in ('PRIMARY', 'UNIQUE') and not constraint['deferrable'] and len(constraint['columns']) == len(columns) and set(constraint['columns']) == wanted:
            name = parent.split('.')[0] + '.' + constraint['name'] if constraint['name'] else native_name_binding.get('index_name')
            if isinstance(name, str):
                candidates.add(name)
    return candidates


def internal_trigger_matrix(table_name, table, constraint, constraint_name, constraint_index=None):
    """Exact semantic matrix; native-generated OID suffixes are not identities."""
    ordinary_table(table)
    if not constraint_name:
        raise source.ManifestError('matched native constraint name required')
    rows = []

    def add(target, reference, function, event, deferred, initially, prefix):
        if 'pg_catalog.' + function + '()' not in PINNED_TRIGGER_FUNCTIONS:
            raise source.ManifestError('internal trigger function lacks exact release pin rule')
        rows.append({'table_name': target, 'constraint_table': table_name,
            'constraint_name': constraint_name, 'function': 'pg_catalog.' + function,
            'function_identity': 'pg_catalog.' + function + '()',
            'function_release_builtin': True,
            'type_bits': event | 1, 'enabled': 'O', 'constraint': True,
            'deferrable': deferred, 'initially_deferred': initially,
            'argument_count': 0, 'arguments_sha256': source.sha256(b'').hexdigest(),
            'when_sha256': None, 'name_prefix': prefix,
            'has_constraint_relation': reference is not None, 'referenced_table': reference,
            'has_constraint_index': constraint['kind'] == 'FOREIGN' or constraint['deferrable'], 'constraint_index': constraint_index,
            'dependencies': [dependency('trigger_to', 'constraint', table_name + '/' + constraint_name, 'i')]})

    if constraint['kind'] == 'FOREIGN':
        deferred, initially = constraint['deferrable'], constraint['initially_deferred']
        add(table_name, constraint['references'], 'RI_FKey_check_ins', 4, deferred, initially, 'RI_ConstraintTrigger_c_')
        add(table_name, constraint['references'], 'RI_FKey_check_upd', 16, deferred, initially, 'RI_ConstraintTrigger_c_')
        actions = {'a': 'noaction', 'r': 'restrict', 'c': 'cascade', 'n': 'setnull', 'd': 'setdefault'}
        for field, event, suffix in [('delete_action', 8, 'del'), ('update_action', 16, 'upd')]:
            action = constraint[field]
            if action not in actions:
                raise source.ManifestError('unsupported FK action')
            add(constraint['references'], table_name, 'RI_FKey_' + actions[action] + '_' + suffix, event,
                deferred if action == 'a' else False, initially if action == 'a' else False,
                'RI_ConstraintTrigger_a_')
    elif constraint['kind'] in ('PRIMARY', 'UNIQUE') and constraint['deferrable']:
        add(table_name, None, 'unique_key_recheck', 4 | 16, True, constraint['initially_deferred'],
            'PK_ConstraintTrigger_' if constraint['kind'] == 'PRIMARY' else 'Unique_ConstraintTrigger_')
    elif constraint['kind'] == 'EXCLUSION':
        raise source.ManifestError('exclusion internal trigger needs its own reviewed rule')
    return rows


def internal_identity(row):
    return (row['constraint_table'], row['constraint_name'], row['table_name'], row['function'], row['type_bits'])


def native_internal_name_matches(name, prefix):
    return bool(re.fullmatch(re.escape(prefix) + r'[0-9]+', name))


def user_trigger_constraints(expected):
    result = {}
    for identity, trigger in expected['triggers'].items():
        if not trigger['constraint']:
            continue
        ordinary_table(expected['tables'][trigger['table']])
        result[identity] = {'table_name': trigger['table'], 'name': trigger['name'], 'kind': 't',
            'deferrable': trigger['deferrable'], 'initially_deferred': trigger['initially_deferred'],
            'validated': True, 'no_inherit': True, 'columns': [], 'references': None,
            'referenced_columns': [], 'expression_sha256': None, 'index_name': None,
            'has_index': False, 'referenced_unique_index': None}
    return result
