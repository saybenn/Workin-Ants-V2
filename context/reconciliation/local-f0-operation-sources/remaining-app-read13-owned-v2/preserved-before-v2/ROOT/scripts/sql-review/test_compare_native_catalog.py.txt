#!/usr/bin/env python3
"""Synthetic collector/comparator regressions; every database boundary is absent."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from pglast import parse_sql
import catalog_manifest as source
import compare_native_catalog as compare


def fixture():
    compiler = source.ManifestCompiler()
    compiler.consume('''CREATE ROLE wa_schema_owner NOLOGIN NOINHERIT;
CREATE ROLE wa_worker LOGIN NOINHERIT;
CREATE SCHEMA app AUTHORIZATION wa_schema_owner;
GRANT USAGE ON SCHEMA app TO wa_worker;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;''', 'bootstrap')
    body = 'BEGIN RETURN NEW; END;'
    compiler.consume('''SET LOCAL ROLE wa_schema_owner;
CREATE TABLE app.example(id uuid NOT NULL, state text NOT NULL DEFAULT 'active', revision bigint NOT NULL DEFAULT 0,
 CONSTRAINT example_pkey PRIMARY KEY(id));
ALTER TABLE app.example ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.example FORCE ROW LEVEL SECURITY;
CREATE INDEX example_state ON app.example(state);
CREATE FUNCTION app.row_guard() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$''' + body + '''$$;
CREATE TRIGGER before_write BEFORE UPDATE ON app.example FOR EACH ROW EXECUTE FUNCTION app.row_guard();
GRANT SELECT(id,state,revision) ON app.example TO wa_worker;
CREATE POLICY read_exact ON app.example FOR SELECT TO wa_worker USING(true);''', 'application')
    expected = compiler.result()
    manifest = {'expected': expected, 'expected_sha256': source.digest(expected),
                'environment_assumptions': {'original_bootstrap_requires_superuser': True}}
    native = {
        'format': 'workinants.native-catalog.v1', 'server_version_num': 170011,
        'read_only': True, 'collected_as': 'postgres', 'collector_is_superuser': True,
        'public_schema_owner': 'pg_database_owner',
        'roles': [{'name': name, **row['native_attributes']} for name, row in expected['roles'].items()],
        'schemas': [{'object': 'app', 'owner': 'wa_schema_owner'}], 'memberships': [],
        'relations': [{'object': 'app.example', 'kind': 'r', 'owner': 'wa_schema_owner', 'persistence': 'p',
                       'rls': True, 'force_rls': True, 'replica_identity': 'd'}],
        'columns': [
            {'table_name': 'app.example', 'name': name, 'ordinal': pos, 'type': typ, 'typmod': -1,
             'array_dimensions': 0, 'nullable': False, 'identity': '', 'generated': '',
             'collation_is_type_default': True, 'storage_is_type_default': True, 'compression': '',
             'is_local': True, 'inherited_count': 0, 'default_sha256': default}
            for name, pos, typ, default in [('id', 1, 'pg_catalog.uuid', None),
                ('state', 2, 'pg_catalog.text', compare.text_hash("'active'::text")),
                ('revision', 3, 'pg_catalog.int8', compare.text_hash('0'))]],
        'types': [{'object': 'app.example', 'owner': 'wa_schema_owner', 'kind': 'c', 'category': 'C', 'element': None, 'relation': 'app.example'},
                  {'object': 'app._example', 'owner': 'wa_schema_owner', 'kind': 'b', 'category': 'A', 'element': 'app.example', 'relation': None}],
        'enums': [],
        'constraints': [{'table_name': 'app.example', 'name': 'example_pkey', 'kind': 'p', 'columns': ['id'],
                         'deferrable': False, 'initially_deferred': False, 'validated': True, 'no_inherit': True,
                         'expression_sha256': None, 'index_name': 'app.example_pkey',
                         'has_index': True, 'referenced_unique_index': None}],
        'indexes': [
            {'object': identity, 'table_name': 'app.example', 'owner': 'wa_schema_owner', 'access_method': 'btree',
             'unique': unique, 'primary': unique, 'nulls_not_distinct': False, 'valid': True, 'ready': True,
             'live': True, 'immediate': True, 'clustered': False, 'replica_identity': False, 'key_count': 1,
             'keys': [{'position': 1, 'column': col, 'included': False, 'expression_sha256': None,
                       'opclass': opclass, 'opclass_default': True, 'collation_is_type_default': True,
                       'descending': False, 'nulls_first': False}], 'predicate_sha256': None}
            for identity, col, unique, opclass in [('app.example_pkey', 'id', True, 'pg_catalog.uuid_ops'),
                                                   ('app.example_state', 'state', False, 'pg_catalog.text_ops')]],
        'functions': [{'object': 'app.row_guard()', 'name': 'app.row_guard', 'owner': 'wa_schema_owner',
                       'language': 'plpgsql', 'return_type': 'pg_catalog.trigger', 'returns_set': False,
                       'security_definer': False, 'strict': False, 'leakproof': False, 'volatility': 'v',
                       'parallel': 'u', 'kind': 'f', 'cost': 100, 'rows': 0, 'settings': ['search_path=pg_catalog'],
                       'variadic': False, 'support_function': False, 'default_count': 0, 'defaults_sha256': None,
                       'body_sha256': compare.text_hash(body), 'parameters': []}],
        'triggers': [{'table_name': 'app.example', 'name': 'before_write', 'internal': False,
                      'function': 'app.row_guard', 'enabled': 'O', 'constraint': False, 'deferrable': False,
                      'initially_deferred': False, 'type_bits': 19, 'argument_count': 0,
                      'arguments_sha256': compare.text_hash(''), 'when_sha256': None,
                      'function_identity': 'app.row_guard()', 'function_release_builtin': False,
                      'constraint_name': None, 'constraint_table': None,
                      'has_constraint_relation': False, 'referenced_table': None,
                      'has_constraint_index': False, 'constraint_index': None,
                      'dependencies': [
                          {'direction': 'trigger_to', 'class': 'function', 'object': 'app.row_guard()',
                           'dependency_type': 'n', 'object_subid': 0, 'referenced_subid': 0},
                          {'direction': 'trigger_to', 'class': 'relation', 'object': 'app.example',
                           'dependency_type': 'a', 'object_subid': 0, 'referenced_subid': 0}]}],
        'policies': [{'table_name': 'app.example', 'name': 'read_exact', 'command': 'r', 'roles': ['wa_worker'],
                      'permissive': True, 'using_sha256': compare.text_hash('TRUE'), 'with_check_sha256': None}],
        'nonowner_acl': compare._acl_expected(expected, 'pg_database_owner'),
        'owner_acl': [], 'generated_type_acl': [],
        'public_wa_schema_acl': [], 'default_acl': [], 'default_acl_outside_registered_schemas': [],
        'extensions': [{'name': 'plpgsql', 'version': '1.0', 'schema': 'pg_catalog', 'owner': 'postgres'}],
        'public_owned_relations': [],
    }
    native['generated_type_acl'] = [
        {'object': identity, 'grantee': grantee, 'grantor': 'wa_schema_owner', 'privilege': 'USAGE', 'grant_option': False}
        for identity in ('app.example', 'app._example') for grantee in ('PUBLIC', 'wa_schema_owner')]
    for kind, mapping in [('SCHEMA', expected['schemas']), ('TABLE', expected['tables']),
                          ('FUNCTION', expected['functions']), ('TYPE', expected['enums'])]:
        for identity, info in mapping.items():
            for privilege in source.PRIVILEGES[kind]:
                native['owner_acl'].append({'kind': kind, 'object': identity, 'column': None,
                    'grantee': info['owner'], 'grantor': info['owner'], 'privilege': privilege, 'grant_option': False})
    for creator in ('wa_schema_owner', 'wa_worker'):
        for schema in ('*', 'app', 'platform', 'platform_private'):
            for kind in ('TABLE', 'SEQUENCE', 'FUNCTION', 'TYPE', 'SCHEMA'):
                if kind == 'SCHEMA' and schema != '*':
                    continue
                privs = ['EXECUTE'] if schema == '*' and kind == 'FUNCTION' and creator == 'wa_worker' else ['USAGE'] if schema == '*' and kind == 'TYPE' else []
                native['default_acl'].append({'creator': creator, 'schema': schema, 'kind': kind,
                    'entries': [{'grantee': 'PUBLIC', 'grantor': creator, 'privilege': p, 'grant_option': False} for p in privs]})
    return manifest, native


class NativeCatalogTests(unittest.TestCase):
    def report(self, native=None):
        manifest, baseline = fixture()
        return compare.compare_manifest(manifest, native or baseline, bootstrap_grantor='postgres',
            bootstrap_superuser=True, public_schema_owner='pg_database_owner')

    def test_collector_is_four_read_only_statements_and_no_table_data(self):
        sql = Path(__file__).with_name('collect_native_catalog.sql').read_text(encoding='utf-8')
        statements = parse_sql(sql)
        self.assertEqual(len(statements), 4)
        self.assertEqual(type(statements[2].stmt).__name__, 'SelectStmt')
        self.assertIn('BEGIN READ ONLY', sql)
        self.assertNotIn('FROM app.', sql)
        self.assertNotIn('FROM platform.', sql)
        self.assertNotIn('FROM public._prisma_migrations', sql)
        self.assertNotIn('rolpassword', sql)

    def test_collector_release_builtin_identity_map_matches_primary_source_rules(self):
        import pg17_catalog_rules as pg17
        sql = Path(__file__).with_name('collect_native_catalog.sql').read_text(encoding='utf-8')
        select = parse_sql(sql)[2].stmt
        cte = next(c for c in select.withClause.ctes if c.ctename == 'release_trigger_functions')
        declared = {'pg_catalog.' + row[0].val.sval + '()': row[1].arg.val.ival
                    for row in cte.ctequery.valuesLists}
        self.assertEqual(declared, pg17.PINNED_TRIGGER_FUNCTIONS)

    def test_baseline_ordinary_metadata_matches_but_unproved_hashes_incomplete(self):
        report = self.report()
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertNotIn('FAIL', report['check_counts'])
        self.assertGreater(report['check_counts']['PASS'], 100)
        self.assertTrue(any(f['field'] == 'default' and f['status'] == 'INCOMPLETE' for f in report['findings']))
        self.assertFalse(any(f['field'] in ('RI-action-linkage-matrix', 'native-noncheck-inheritance-semantics',
                                           'generated-row-array-type-privilege-semantics') for f in report['findings']))

    def test_type_nullability_owner_acl_policy_membership_drift_reject(self):
        mutations = [
            lambda n: n['columns'][0].update(type='pg_catalog.text'),
            lambda n: n['columns'][0].update(nullable=True),
            lambda n: n['relations'][0].update(owner='wa_worker'),
            lambda n: n['nonowner_acl'].append({'kind': 'TABLE', 'object': 'app.example', 'column': None,
                'grantee': 'wa_worker', 'grantor': 'wa_schema_owner', 'privilege': 'UPDATE', 'grant_option': False}),
            lambda n: n['policies'][0].update(permissive=False),
            lambda n: n['memberships'].append({'role': 'wa_schema_owner', 'member': 'wa_worker',
                'grantor': 'postgres', 'admin': False, 'inherit': False, 'set': True}),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                _, native = fixture(); mutate(native)
                self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_same_counts_wrong_objects_and_duplicate_identity_reject(self):
        _, native = fixture(); native['relations'][0]['object'] = 'app.other'
        self.assertEqual(self.report(native)['status'], 'FAIL')
        _, native = fixture(); native['columns'].append(dict(native['columns'][0]))
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_body_search_path_trigger_and_index_state_drift_reject(self):
        for section, field, value in [('functions', 'body_sha256', '0' * 64),
                ('functions', 'settings', ['search_path=public']), ('triggers', 'enabled', 'D'),
                ('indexes', 'valid', False), ('indexes', 'nulls_not_distinct', True)]:
            with self.subTest(section=section, field=field):
                _, native = fixture(); native[section][0][field] = value
                self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_expression_normalization_is_syntactic_and_casts_remain_distinct(self):
        self.assertTrue(compare.equivalent_expression('(revision > 0)', 'revision>0'))
        self.assertTrue(compare.equivalent_expression('true::boolean', 'TRUE::pg_catalog.bool'))
        self.assertFalse(compare.equivalent_expression("'1'", "'1'::integer"))
        self.assertFalse(compare.equivalent_expression('revision > 0', 'revision >= 0'))
        for unsafe in ['true; SELECT false', 'true FROM pg_roles', 'true AS chosen']:
            with self.assertRaises(source.ManifestError):
                compare.expression_ast(unsafe)

    def test_default_acl_broadening_and_unregistered_public_relation_reject(self):
        _, native = fixture(); native['default_acl'][0]['entries'].append({'grantee': 'wa_worker',
            'grantor': 'wa_schema_owner', 'privilege': 'INSERT', 'grant_option': True})
        self.assertEqual(self.report(native)['status'], 'FAIL')
        _, native = fixture(); native['public_owned_relations'].append({'object': 'public.other', 'owner': 'wa_migrator'})
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_unregistered_ledger_and_absent_public_baseline_are_incomplete(self):
        manifest, native = fixture()
        native['public_owned_relations'] = [{'object': 'public._prisma_migrations', 'owner': 'wa_migrator'}]
        report = compare.compare_manifest(manifest, native, bootstrap_grantor='postgres', bootstrap_superuser=True)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertTrue(any(f['category'] == 'ledger' for f in report['findings']))

    def test_unknown_catalog_canaries_and_raw_values_never_appear_in_report(self):
        _, native = fixture()
        canary = 'SECRET-CANARY-no-arbitrary-catalog-identifiers-or-values'
        native['relations'].append({'object': canary, 'owner': canary})
        native['functions'][0]['settings'] = [canary]
        output = json.dumps(self.report(native))
        self.assertNotIn(canary, output)
        self.assertIn('actual_sha256', output)

    def test_schema_acl_grantors_are_compared_not_dropped(self):
        _, native = fixture()
        native['nonowner_acl'][0]['grantor'] = 'postgres'
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_owner_ordinary_privilege_revocation_rejects(self):
        _, native = fixture(); native['owner_acl'].pop()
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_generated_type_acl_and_noncheck_inheritance_drift_reject(self):
        _, native = fixture(); native['generated_type_acl'].pop()
        self.assertEqual(self.report(native)['status'], 'FAIL')
        _, native = fixture(); native['constraints'][0]['no_inherit'] = False
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_generated_array_name_is_source_derived(self):
        _, native = fixture(); native['types'][1]['object'] = 'app.renamed_array'
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_all_attainable_synthetic_metadata_can_pass_without_permanent_gaps(self):
        manifest, native = fixture()
        native['columns'][1]['default_sha256'] = compare.text_hash("'active'")
        native['public_schema_acl'] = []
        report = compare.compare_manifest(manifest, native, bootstrap_grantor='postgres',
            bootstrap_superuser=True, public_schema_owner='pg_database_owner', public_acl_registration=[])
        self.assertEqual(report['status'], 'PASS')
        self.assertFalse(report['findings'])

    def test_exact_release_rule_rejects_another_postgres_17_minor(self):
        _, native = fixture(); native['server_version_num'] = 170010
        self.assertEqual(self.report(native)['status'], 'FAIL')

    def test_internal_fk_matrix_rejects_wrong_action_deferral_link_and_duplicates(self):
        manifest, native = fixture()
        c = source.ManifestCompiler(); c.tables = deepcopy(manifest['expected']['tables'])
        c.consume('ALTER TABLE app.example ADD CONSTRAINT self_fk FOREIGN KEY(id) REFERENCES app.example(id) ON DELETE RESTRICT ON UPDATE RESTRICT;', 'application')
        manifest['expected']['tables'] = c.tables
        manifest['expected_sha256'] = source.digest(manifest['expected'])
        native['constraints'].append({'table_name': 'app.example', 'name': 'self_fk', 'kind': 'f', 'columns': ['id'],
            'deferrable': False, 'initially_deferred': False, 'validated': True, 'no_inherit': True,
            'references': 'app.example', 'referenced_columns': ['id'], 'match': 's', 'update_action': 'r', 'delete_action': 'r',
            'expression_sha256': None, 'index_name': None, 'has_index': True,
            'referenced_unique_index': 'app.example_pkey'})
        for index, (function, bits, prefix) in enumerate([('RI_FKey_check_ins', 5, 'c'), ('RI_FKey_check_upd', 17, 'c'),
                                                        ('RI_FKey_restrict_del', 9, 'a'), ('RI_FKey_restrict_upd', 17, 'a')]):
            native['triggers'].append({'table_name': 'app.example', 'constraint_table': 'app.example', 'constraint_name': 'self_fk',
                'name': 'RI_ConstraintTrigger_' + prefix + '_' + str(100 + index), 'internal': True,
                'function': 'pg_catalog.' + function, 'type_bits': bits, 'enabled': 'O', 'constraint': True,
                'deferrable': False, 'initially_deferred': False, 'argument_count': 0,
                'arguments_sha256': compare.text_hash(''), 'when_sha256': None,
                'function_identity': 'pg_catalog.' + function + '()',
                'function_release_builtin': True,
                'has_constraint_relation': True, 'referenced_table': 'app.example',
                'has_constraint_index': True, 'constraint_index': 'app.example_pkey',
                'dependencies': [
                    {'direction': 'trigger_to', 'class': 'constraint', 'object': 'app.example/self_fk',
                     'dependency_type': 'i', 'object_subid': 0, 'referenced_subid': 0}]})
        run = lambda n: compare.compare_manifest(manifest, n, bootstrap_grantor='postgres',
            bootstrap_superuser=True, public_schema_owner='pg_database_owner')
        self.assertEqual(run(native)['status'], 'INCOMPLETE')
        self.assertNotIn('FAIL', run(native)['check_counts'])
        for field, value in [('function', 'pg_catalog.RI_FKey_noaction_del'), ('enabled', 'D'),
                             ('deferrable', True), ('constraint_table', 'app.foreign'),
                             ('referenced_table', 'app.foreign'), ('has_constraint_relation', False),
                             ('constraint_index', 'app.example_state'), ('has_constraint_index', False),
                             ('function_release_builtin', False),
                             ('function_identity', 'pg_catalog.RI_FKey_restrict_del(pg_catalog.text)')]:
            altered = deepcopy(native); altered['triggers'][3][field] = value
            self.assertEqual(run(altered)['status'], 'FAIL')
        altered = deepcopy(native); altered['triggers'].append(dict(altered['triggers'][1]))
        self.assertEqual(run(altered)['status'], 'FAIL')
        altered = deepcopy(native); altered['constraints'][1]['referenced_unique_index'] = 'app.example_state'
        for row in altered['triggers'][1:]:
            row['constraint_index'] = 'app.example_state'
        self.assertEqual(run(altered)['status'], 'FAIL')
        for mutation in ('missing', 'extra', 'wrong-signature', 'reverse-direction'):
            altered = deepcopy(native)
            edges = altered['triggers'][1]['dependencies']
            if mutation == 'missing':
                edges.pop()
            elif mutation == 'extra':
                edges.append(dict(edges[0]))
            elif mutation == 'wrong-signature':
                edges[0]['object'] += '(pg_catalog.text)'
            else:
                edges[0]['direction'] = 'to_trigger'
            self.assertEqual(run(altered)['status'], 'FAIL')
        altered = deepcopy(native)
        altered['triggers'][1]['dependencies'].append({'direction': 'trigger_to', 'class': 'function',
            'object': 'pg_catalog.RI_FKey_check_ins()', 'dependency_type': 'n',
            'object_subid': 0, 'referenced_subid': 0})
        self.assertEqual(run(altered)['status'], 'FAIL')

    def test_user_constraint_trigger_requires_its_source_derived_catalog_row(self):
        manifest, native = fixture()
        c = source.ManifestCompiler()
        c.consume('CREATE CONSTRAINT TRIGGER exact_state AFTER UPDATE ON app.example DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION app.row_guard();', 'application')
        manifest['expected']['triggers'].update(c.triggers)
        manifest['expected_sha256'] = source.digest(manifest['expected'])
        native['triggers'].append({'table_name': 'app.example', 'name': 'exact_state', 'internal': False,
            'function': 'app.row_guard', 'type_bits': 17, 'enabled': 'O', 'constraint': True,
            'deferrable': True, 'initially_deferred': True, 'argument_count': 0,
            'arguments_sha256': compare.text_hash(''), 'when_sha256': None,
            'function_identity': 'app.row_guard()', 'function_release_builtin': False,
            'constraint_name': 'exact_state', 'constraint_table': 'app.example',
            'has_constraint_relation': False, 'referenced_table': None, 'has_constraint_index': False, 'constraint_index': None,
            'dependencies': [
                {'direction': 'trigger_to', 'class': 'function', 'object': 'app.row_guard()',
                 'dependency_type': 'n', 'object_subid': 0, 'referenced_subid': 0},
                {'direction': 'trigger_to', 'class': 'relation', 'object': 'app.example',
                 'dependency_type': 'a', 'object_subid': 0, 'referenced_subid': 0},
                {'direction': 'to_trigger', 'class': 'constraint', 'object': 'app.example/exact_state',
                 'dependency_type': 'i', 'object_subid': 0, 'referenced_subid': 0}]})
        native['constraints'].append({'table_name': 'app.example', 'name': 'exact_state', 'kind': 't',
            'deferrable': True, 'initially_deferred': True, 'validated': True, 'no_inherit': True,
            'columns': [], 'references': None, 'referenced_columns': [], 'expression_sha256': None, 'index_name': None,
            'has_index': False, 'referenced_unique_index': None})
        run = lambda n: compare.compare_manifest(manifest, n, bootstrap_grantor='postgres',
            bootstrap_superuser=True, public_schema_owner='pg_database_owner')
        self.assertNotIn('FAIL', run(native)['check_counts'])
        altered = deepcopy(native); altered['constraints'].pop()
        self.assertEqual(run(altered)['status'], 'FAIL')
        altered = deepcopy(native); altered['triggers'][-1]['dependencies'].pop()
        self.assertEqual(run(altered)['status'], 'FAIL')

    def test_user_trigger_zero_links_and_dependency_edges_are_not_optional(self):
        for field, value in [('referenced_table', 'app.example'), ('has_constraint_relation', True),
                             ('constraint_index', 'app.example_pkey'), ('has_constraint_index', True),
                             ('constraint_table', 'app.example'), ('constraint_name', 'self_fk'),
                             ('function_release_builtin', True)]:
            _, native = fixture(); native['triggers'][0][field] = value
            self.assertEqual(self.report(native)['status'], 'FAIL')
        _, native = fixture(); del native['triggers'][0]['referenced_table']
        self.assertEqual(self.report(native)['status'], 'INCOMPLETE')
        self.assertTrue(any(f['field'] == 'referenced_table-visibility' for f in self.report(native)['findings']))
        _, native = fixture(); native['triggers'][0]['dependencies'].append(dict(native['triggers'][0]['dependencies'][0]))
        self.assertEqual(self.report(native)['status'], 'FAIL')
        _, native = fixture(); native['triggers'][0]['dependencies'][0]['object'] = 'app.row_guard(pg_catalog.text)'
        self.assertEqual(self.report(native)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main(verbosity=2)
