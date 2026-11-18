"""Primary-source rule regressions; no server or process invocation."""
from copy import deepcopy
import unittest

import catalog_manifest as source
import pg17_catalog_rules as rules


class Pg17RuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = source.build_manifest()['expected']

    def test_primary_sources_are_release_pinned(self):
        self.assertEqual(rules.PG_RELEASE, 'REL_17_11')
        self.assertTrue(all('/postgres/postgres/REL_17_11/src/' in r['url'] for r in rules.SOURCES.values()))

    def test_current_source_has_312_internal_fk_and_40_user_constraint_rows(self):
        rows = []
        for table, info in self.expected['tables'].items():
            for index, constraint in enumerate(info['constraints']):
                rows.extend(rules.internal_trigger_matrix(table, info, constraint, constraint['name'] or 'synthetic_' + str(index)))
        self.assertEqual(len(rows), 312)
        self.assertTrue(all(r['constraint'] and r['enabled'] == 'O' for r in rows))
        self.assertTrue(all(not r['deferrable'] and not r['initially_deferred'] for r in rows))
        self.assertEqual(len(rules.user_trigger_constraints(self.expected)), 40)
        for row in rules.user_trigger_constraints(self.expected).values():
            self.assertEqual(row['kind'], 't')
            self.assertTrue(row['no_inherit'] and row['validated'])
            self.assertEqual(row['columns'], [])

    def test_restrict_action_does_not_inherit_deferred_check_semantics(self):
        table = {'relkind': 'r'}
        constraint = {'kind': 'FOREIGN', 'references': 'app.parent', 'deferrable': True,
                      'initially_deferred': True, 'delete_action': 'r', 'update_action': 'a'}
        rows = rules.internal_trigger_matrix('app.child', table, constraint, 'child_parent_fk', 'app.parent_unique')
        self.assertEqual([(r['table_name'], r['function'], r['type_bits'], r['deferrable'], r['initially_deferred']) for r in rows], [
            ('app.child', 'pg_catalog.RI_FKey_check_ins', 5, True, True),
            ('app.child', 'pg_catalog.RI_FKey_check_upd', 17, True, True),
            ('app.parent', 'pg_catalog.RI_FKey_restrict_del', 9, False, False),
            ('app.parent', 'pg_catalog.RI_FKey_noaction_upd', 17, True, True)])
        self.assertEqual([r['referenced_table'] for r in rows], ['app.parent', 'app.parent', 'app.child', 'app.child'])
        self.assertTrue(all(r['constraint_index'] == 'app.parent_unique' and r['has_constraint_index'] for r in rows))
        self.assertTrue(all(len(r['dependencies']) == 1 for r in rows))

    def test_source_fk_index_candidates_require_exact_unique_key_semantics(self):
        index = {'table': 'app.parent', 'owner': 'owner', 'unique': True, 'access_method': 'btree',
                 'predicate': None, 'keys_ast': [{'IndexElem': {'name': 'a'}}, {'IndexElem': {'name': 'b'}}]}
        indexes = {'app.good': index}
        for suffix, changes in [('wrong_columns', {'keys_ast': [{'IndexElem': {'name': 'a'}}]}),
                                ('wrong_owner', {'owner': 'worker'}), ('nonunique', {'unique': False}),
                                ('wrong_method', {'access_method': 'hash'}), ('partial', {'predicate': {'ast': 'x'}}),
                                ('expression', {'keys_ast': [{'IndexElem': {'expr': {}}}, {'IndexElem': {'name': 'b'}}]})]:
            indexes['app.' + suffix] = {**index, **changes}
        expected = {'tables': {'app.parent': {'owner': 'owner'}}, 'explicit_indexes': indexes}
        foreign = {'references': 'app.parent', 'referenced_columns': ['b', 'a']}
        self.assertEqual(rules.eligible_fk_indexes(expected, [], foreign), {'app.good'})
        constraint = {'kind': 'UNIQUE', 'name': 'declared_key', 'columns': ['a', 'b'], 'deferrable': False}
        bindings = [('app.parent', {}, constraint, {'index_name': 'app.unexpected_renaming'})]
        self.assertEqual(rules.eligible_fk_indexes(expected, bindings, foreign), {'app.good', 'app.declared_key'})

    def test_pinned_builtin_function_edges_are_omitted_but_user_function_edges_remain(self):
        self.assertEqual(rules.PINNED_TRIGGER_FUNCTIONS['pg_catalog.RI_FKey_check_ins()'], 1644)
        self.assertEqual(rules.PINNED_TRIGGER_FUNCTIONS['pg_catalog.unique_key_recheck()'], 1250)
        self.assertEqual(len(rules.PINNED_TRIGGER_FUNCTIONS), 13)
        user = {'function': 'platform_private.guard_user', 'table': 'app.users', 'name': 'guard_user',
                'constraint': False, 'ast': {}, 'when': None}
        self.assertTrue(any(e['class'] == 'function' and e['object'] == 'platform_private.guard_user()'
                            for e in rules.user_trigger_dependencies(user)))
        fk = {'kind': 'FOREIGN', 'references': 'app.parent', 'deferrable': False,
              'initially_deferred': False, 'delete_action': 'r', 'update_action': 'r'}
        for row in rules.internal_trigger_matrix('app.child', {'relkind': 'r'}, fk, 'fk', 'app.parent_key'):
            self.assertTrue(row['function_release_builtin'])
            self.assertEqual([e['class'] for e in row['dependencies']], ['constraint'])

    def test_all_source_action_functions_and_deferral_rules(self):
        for action, name in [('a', 'noaction'), ('r', 'restrict'), ('c', 'cascade'), ('n', 'setnull'), ('d', 'setdefault')]:
            constraint = {'kind': 'FOREIGN', 'references': 'app.parent', 'deferrable': True,
                          'initially_deferred': True, 'delete_action': action, 'update_action': action}
            rows = rules.internal_trigger_matrix('app.child', {'relkind': 'r'}, constraint, 'fk')
            self.assertEqual(rows[2]['function'], 'pg_catalog.RI_FKey_' + name + '_del')
            self.assertEqual(rows[3]['function'], 'pg_catalog.RI_FKey_' + name + '_upd')
            self.assertEqual(rows[2]['deferrable'], action == 'a')
            self.assertEqual(rows[3]['initially_deferred'], action == 'a')

    def test_self_reference_keeps_both_check_and_action_identities(self):
        c = {'kind': 'FOREIGN', 'references': 'app.self', 'deferrable': False,
             'initially_deferred': False, 'delete_action': 'r', 'update_action': 'r'}
        rows = rules.internal_trigger_matrix('app.self', {'relkind': 'r'}, c, 'self_fk')
        self.assertEqual(len({rules.internal_identity(r) for r in rows}), 4)
        self.assertTrue(all(rules.native_internal_name_matches(r['name_prefix'] + '1234', r['name_prefix']) for r in rows))
        self.assertFalse(rules.native_internal_name_matches('unrelated', rows[0]['name_prefix']))

    def test_noncheck_noinherit_and_check_explicit_flag(self):
        for kind in ('FOREIGN', 'PRIMARY', 'UNIQUE', 'EXCLUSION'):
            self.assertTrue(rules.constraint_no_inherit({'relkind': 'r'}, {'kind': kind}))
        self.assertFalse(rules.constraint_no_inherit({'relkind': 'r'}, {'kind': 'CHECK', 'no_inherit': False}))
        self.assertTrue(rules.constraint_no_inherit({'relkind': 'r'}, {'kind': 'CHECK', 'no_inherit': True}))
        with self.assertRaises(source.ManifestError):
            rules.constraint_no_inherit({'relkind': 'p'}, {'kind': 'FOREIGN'})

    def test_generated_types_and_collector_projection_ignore_creator_type_defaults(self):
        types = rules.generated_types(self.expected)
        self.assertEqual(len(types), 113)
        self.assertEqual(sum(t['category'] == 'C' for t in types.values()), 42)
        self.assertEqual(sum(t['category'] == 'A' for t in types.values()), 71)
        projection = rules.generated_type_acl_projection(self.expected)
        self.assertEqual(len(projection), 226)
        self.assertTrue(all(r['privilege'] == 'USAGE' and not r['grant_option'] for r in projection))
        self.assertEqual(types['app._account_track']['usage_delegates_to'], 'app.account_track')
        # Enum PUBLIC USAGE is revoked, while the collector's generated-array
        # projection still expands its NULL typacl using acldefault('T').
        self.assertFalse([r for r in self.expected['nonowner_acl'] if r['object'] == 'app.account_track' and r['grantee'] == 'PUBLIC'])
        self.assertTrue([r for r in projection if r['object'] == 'app._account_track' and r['grantee'] == 'PUBLIC'])

    def test_array_name_collision_or_unreviewed_truncation_rejects(self):
        expected = {'tables': {}, 'enums': {'app.e': {'owner': 'o'}, 'app._e': {'owner': 'o'}}}
        with self.assertRaises(source.ManifestError):
            rules.generated_types(expected)
        expected['enums'] = {'app.' + 'x' * 63: {'owner': 'o'}}
        with self.assertRaises(source.ManifestError):
            rules.generated_types(expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
