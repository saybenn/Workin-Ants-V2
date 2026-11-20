#!/usr/bin/env python3
"""Environment-free source expectations; no Docker/database process boundary."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import catalog_manifest as catalog


class CatalogManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = catalog.build_manifest()
        cls.expected = cls.manifest['expected']
        cls.runtime = json.loads((catalog.ROOT / catalog.INPUTS[6]).read_text(encoding='utf-8'))
        cls.verifier = json.loads((catalog.ROOT / catalog.INPUTS[7]).read_text(encoding='utf-8'))

    def test_complete_reviewed_object_coverage(self):
        self.assertEqual(self.manifest['counts'], {
            'roles': 9, 'schemas': 3, 'tables': 42, 'enums': 29,
            'functions': 147, 'explicit_indexes': 102, 'policies': 150,
            'triggers': 100, 'columns': 600, 'constraints': 215, 'constraint_indexes': 44})
        self.assertTrue(all(t['rls'] and t['force_rls'] for t in self.expected['tables'].values()))
        self.assertTrue(all(t['owner'] == 'wa_schema_owner' for t in self.expected['tables'].values()))
        self.assertEqual(len(self.expected['prisma_declarations']['models']), 40)
        self.assertEqual(len(self.expected['prisma_declarations']['enums']), 29)

    def test_function_owners_security_and_body_hashes(self):
        from collections import Counter
        self.assertEqual(Counter(f['owner'] for f in self.expected['functions'].values()),
                         {'wa_schema_owner': 131, 'wa_private_helper_owner': 8,
                          'wa_customer_verifier': 1, 'wa_track_verifier': 7})
        for function in self.expected['functions'].values():
            self.assertEqual(function['security_definer'], function['owner'] != 'wa_schema_owner')
            self.assertEqual(len(function['body_sha256']), 64)
            self.assertEqual(function['settings_ast'], [{'kind': 'VAR_SET_VALUE', 'name': 'search_path',
                'args': [{'A_Const': {'sval': {'sval': 'pg_catalog'}}}]}])
            self.assertNotIn('body', function)

    def test_exact_runtime_column_surfaces(self):
        for role, count in [('wa_app_runtime', 94), ('wa_worker', 32)]:
            rows = [r for r in self.expected['nonowner_acl'] if r['kind'] == 'TABLE' and r['grantee'] == role]
            self.assertEqual(len(rows), count)
            self.assertTrue(all(r['scope'] == 'columns' and not r['grant_option'] for r in rows))
        catalog.validate_acl(self.expected, self.runtime, self.verifier)

    def test_broad_table_grant_mutation_rejects(self):
        changed = deepcopy(self.expected)
        changed['nonowner_acl'].append({'kind': 'TABLE', 'object': 'app.customer_profiles',
            'grantee': 'wa_worker', 'privilege': 'SELECT', 'scope': 'object', 'columns': [],
            'grant_option': False, 'grantor': 'wa_schema_owner'})
        with self.assertRaisesRegex(catalog.ManifestError, 'runtime ACL'):
            catalog.validate_acl(changed, self.runtime, self.verifier)

    def test_missing_worker_column_mutation_rejects(self):
        changed = deepcopy(self.expected)
        row = next(r for r in changed['nonowner_acl'] if r['kind'] == 'TABLE' and r['grantee'] == 'wa_worker')
        row['columns'].pop()
        with self.assertRaisesRegex(catalog.ManifestError, 'runtime ACL'):
            catalog.validate_acl(changed, self.runtime, self.verifier)

    def test_verifier_write_mutation_rejects(self):
        changed = deepcopy(self.expected)
        changed['nonowner_acl'].append({'kind': 'TABLE', 'object': 'app.customer_profiles',
            'grantee': 'wa_customer_verifier', 'privilege': 'UPDATE', 'scope': 'columns',
            'columns': ['status'], 'grant_option': False, 'grantor': 'wa_schema_owner'})
        with self.assertRaisesRegex(catalog.ManifestError, 'verifier SELECT-only'):
            catalog.validate_acl(changed, self.runtime, self.verifier)

    def test_no_public_function_execute_or_enum_usage(self):
        self.assertFalse([r for r in self.expected['nonowner_acl'] if r['grantee'] == 'PUBLIC'
                          and r['kind'] in ('FUNCTION', 'TYPE')])
        defaults = self.expected['default_acl']
        self.assertIn({'creator': 'wa_schema_owner', 'schema': '*', 'kind': 'FUNCTION',
                       'grantee': 'PUBLIC', 'privileges': []}, defaults)
        self.assertIn({'creator': 'wa_schema_owner', 'schema': '*', 'kind': 'TYPE',
                       'grantee': 'PUBLIC', 'privileges': []}, defaults)
        self.assertEqual(len(self.expected['default_acl_source_operations']), 8)

    def test_default_public_execute_is_not_assumed_absent(self):
        c = catalog.ManifestCompiler()
        c.consume('CREATE FUNCTION app.f() RETURNS boolean LANGUAGE sql AS $$SELECT true$$;', 'application')
        self.assertTrue(any(r['grantee'] == 'PUBLIC' and r['privilege'] == 'EXECUTE'
                            for r in c.result()['nonowner_acl']))

    def test_finalization_preserves_only_intended_membership(self):
        self.assertEqual(self.expected['memberships'], [{'role': 'wa_schema_owner',
            'member': 'wa_migrator', 'grantor': catalog.ORIGINAL_GRANTOR,
            'admin': False, 'inherit': False, 'set': True}])
        self.assertFalse([r for r in self.expected['nonowner_acl'] if r['kind'] == 'SCHEMA'
                          and r['grantee'] in ('wa_private_helper_owner', 'wa_customer_verifier', 'wa_track_verifier')
                          and r['privilege'] == 'CREATE'])

    def test_function_transfer_rewrites_grantor(self):
        row = next(r for r in self.expected['nonowner_acl']
                   if r['kind'] == 'FUNCTION' and r['object'].startswith('platform_private.row_allowed(')
                   and r['grantee'] == 'wa_worker')
        self.assertEqual(row['grantor'], 'wa_private_helper_owner')

    def test_bootstrap_superuser_object_grantors_are_owners(self):
        schemas = [r for r in self.expected['nonowner_acl'] if r['kind'] == 'SCHEMA']
        for row in schemas:
            self.assertEqual(row['grantor'], catalog.PUBLIC_SCHEMA_OWNER if row['object'] == 'public' else 'wa_schema_owner')
        self.assertTrue(self.manifest['environment_assumptions']['original_bootstrap_requires_superuser'])
        self.assertEqual(self.manifest['environment_assumptions']['public_schema_owner'], catalog.PUBLIC_SCHEMA_OWNER)
        self.assertEqual(self.expected['memberships'][0]['grantor'], catalog.ORIGINAL_GRANTOR)

    def test_grantor_rule_depends_on_explicit_superuser_assumption(self):
        sql = 'CREATE SCHEMA app AUTHORIZATION wa_schema_owner; GRANT USAGE ON SCHEMA app TO wa_worker;'
        c = catalog.ManifestCompiler(original_bootstrap_superuser=False)
        c.consume(sql, 'bootstrap')
        self.assertEqual(c.result()['nonowner_acl'][0]['grantor'], catalog.ORIGINAL_GRANTOR)
        c = catalog.ManifestCompiler(original_bootstrap_superuser=True)
        c.consume(sql, 'bootstrap')
        self.assertEqual(c.result()['nonowner_acl'][0]['grantor'], 'wa_schema_owner')

    def test_index_constraints_and_deferral_remain_explicit(self):
        table = self.expected['tables']['app.consent_logs']
        fk = next(c for c in table['constraints'] if c['name'] == 'consent_logs_presentation_id_content_revision_id_user_id_fkey')
        self.assertEqual(fk['columns'], ['presentation_id', 'content_revision_id', 'user_id'])
        self.assertEqual(fk['referenced_columns'], ['id', 'content_revision_id', 'user_id'])
        self.assertEqual((fk['update_action'], fk['delete_action']), ('r', 'r'))
        self.assertTrue(fk['validated'])
        self.assertFalse(fk['deferrable'])
        trigger = self.expected['triggers']['app.customer_profiles/customer_atomic']
        self.assertTrue(trigger['constraint'] and trigger['deferrable'] and trigger['initially_deferred'])
        self.assertEqual(trigger['enabled'], 'O')

    def test_location_and_format_changes_do_not_change_semantics(self):
        a, b = catalog.ManifestCompiler(), catalog.ManifestCompiler()
        a.consume('CREATE TABLE app.x(id uuid PRIMARY KEY, n bigint DEFAULT 0);', 'application')
        b.consume('-- source comment\n CREATE TABLE app.x ( id uuid PRIMARY KEY,\n n bigint DEFAULT 0 );', 'application')
        self.assertEqual(a.result(), b.result())

    def test_default_type_nullable_policy_and_body_mutations_are_visible(self):
        sources = [
            'CREATE TABLE app.x(id uuid PRIMARY KEY, n bigint NOT NULL DEFAULT 0);',
            'CREATE TABLE app.x(id uuid PRIMARY KEY, n bigint NOT NULL DEFAULT 1);',
            'CREATE TABLE app.x(id uuid PRIMARY KEY, n integer NOT NULL DEFAULT 0);',
            'CREATE TABLE app.x(id uuid PRIMARY KEY, n bigint DEFAULT 0);',
        ]
        fingerprints = []
        for sql in sources:
            c = catalog.ManifestCompiler(); c.consume(sql, 'application')
            fingerprints.append(catalog.digest(c.result()))
        self.assertEqual(len(set(fingerprints)), len(sources))
        for suffix in ['USING (true)', 'USING (false)']:
            c = catalog.ManifestCompiler()
            c.consume('CREATE TABLE app.x(id uuid); CREATE POLICY p ON app.x FOR SELECT TO PUBLIC ' + suffix + ';', 'application')
            fingerprints.append(catalog.digest(c.result()))
        self.assertNotEqual(fingerprints[-1], fingerprints[-2])

    def test_function_bodies_are_hashed_not_retained(self):
        canary = 'SECRET-CANARY-function-body-should-not-be-retained'
        c = catalog.ManifestCompiler()
        c.consume("CREATE FUNCTION app.f() RETURNS text LANGUAGE sql AS $$SELECT '" + canary + "'::text$$;", 'application')
        serialized = catalog.canonical(c.result())
        self.assertNotIn(canary, serialized)
        first = c.result()['functions']['app.f()']['body_sha256']
        c = catalog.ManifestCompiler()
        c.consume("CREATE FUNCTION app.f() RETURNS text LANGUAGE sql AS $$SELECT 'different'::text$$;", 'application')
        self.assertNotEqual(first, c.result()['functions']['app.f()']['body_sha256'])

    def test_unknown_ddl_and_dynamic_application_block_reject(self):
        for sql in ['DROP TABLE app.x;', 'CREATE EXTENSION btree_gist;', 'DO $$BEGIN NULL; END$$;']:
            with self.subTest(sql=sql), self.assertRaises(catalog.ManifestError):
                catalog.ManifestCompiler().consume(sql, 'application')

    def test_prisma_sql_type_mutation_rejects(self):
        source = (catalog.ROOT / catalog.INPUTS[4]).read_text(encoding='utf-8')
        source = source.replace('allowedFields String[]', 'allowedFields Int[]', 1)
        with self.assertRaisesRegex(catalog.ManifestError, 'type or nullability'):
            catalog.prisma_crosscheck(source, self.expected, self.expected['model_register'])

    def test_prisma_sql_default_value_mutation_rejects(self):
        source = (catalog.ROOT / catalog.INPUTS[4]).read_text(encoding='utf-8')
        source = source.replace('@default(0)', '@default(1)', 1)
        with self.assertRaisesRegex(catalog.ManifestError, 'default value mismatch'):
            catalog.prisma_crosscheck(source, self.expected, self.expected['model_register'])

    def test_pinned_inputs_and_bad_pin(self):
        pins = self.manifest['inputs_sha256']
        pinned = catalog.build_manifest(expected_sha256=pins)
        self.assertEqual(pinned['approval_binding'], 'ALL_INPUT_HASHES_VERIFIED')
        self.assertEqual(pinned['expected_sha256'], self.manifest['expected_sha256'])
        bad = dict(pins); bad[catalog.INPUTS[0]] = '0' * 64
        with self.assertRaisesRegex(catalog.ManifestError, 'source fingerprint mismatch'):
            catalog.build_manifest(expected_sha256=bad)
        with self.assertRaisesRegex(catalog.ManifestError, 'every manifest input'):
            catalog.build_manifest(expected_sha256={})

    def test_no_writes_or_process_network_database_imports(self):
        with patch.object(Path, 'write_text', side_effect=AssertionError('unexpected file write')), \
             patch.object(Path, 'write_bytes', side_effect=AssertionError('unexpected file write')):
            self.assertEqual(catalog.build_manifest()['expected_sha256'], self.manifest['expected_sha256'])
        tree = ast.parse(Path(catalog.__file__).read_text(encoding='utf-8'))
        modules = {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        modules |= {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        self.assertFalse(modules & {'subprocess', 'socket', 'urllib', 'requests', 'psycopg', 'psycopg2', 'docker', 'os'})
        self.assertEqual(self.manifest['status'], 'EXPECTED_SOURCE_ONLY_NATIVE_PARITY_NOT_RUN')
        self.assertFalse(self.manifest['sql_executed'] or self.manifest['database_contacted'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
