"""Environment-free review checks for the rollback-only expression oracle."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from pglast import ast, parse_sql, parse_plpgsql
from pglast.stream import RawStream

import catalog_manifest as source
import compare_native_catalog as compare
import catalog_expression_oracle as oracle


class OracleSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        first = source.build_manifest()
        cls.manifest = source.build_manifest(expected_sha256=first['inputs_sha256'])
        cls.plan = oracle.build_plan(cls.manifest)
        cls.sql = oracle.emit_sql(cls.manifest, cls.plan, database='wa_first_rehearsal', grantor='postgres')
        cls.statements = parse_sql(cls.sql)

    def test_current_source_expression_scope_and_provenance(self):
        self.assertEqual(self.plan['expression_count'], 416)
        self.assertEqual(self.plan['by_operation'], {'check-not-valid': 93, 'column-default': 144,
                         'function-default-list': 4, 'policy': 175})
        self.assertEqual(self.plan['expected_tables'], 42)
        self.assertEqual(self.plan['expected_columns'], 600)
        self.assertFalse(self.plan['database_contacted'] or self.plan['sql_executed'])
        self.assertEqual(self.plan['status'], 'DRAFT_PENDING_INDEPENDENT_REVIEW')
        self.assertTrue(all('expression_sql' not in e for e in self.plan['expressions']))
        self.assertEqual(self.plan['source_expected_sha256'], self.manifest['expected_sha256'])

    def test_packet_only_writes_temporary_objects_and_never_commits(self):
        self.assertEqual(len(self.statements), 475)
        transactions = [s.stmt.kind.name for s in self.statements if isinstance(s.stmt, ast.TransactionStmt)]
        self.assertEqual(transactions, ['TRANS_STMT_BEGIN', 'TRANS_STMT_ROLLBACK'])
        forbidden = (ast.InsertStmt, ast.UpdateStmt, ast.DeleteStmt, ast.DropStmt, ast.CreateSchemaStmt, ast.GrantRoleStmt)
        self.assertFalse(any(isinstance(s.stmt, forbidden) for s in self.statements))
        for item in self.statements:
            stmt = item.stmt
            if isinstance(stmt, ast.CreateStmt):
                self.assertEqual(stmt.relation.relpersistence, 't')
                self.assertTrue(stmt.relation.relname.startswith('wa_expr_oracle_t_'))
            elif isinstance(stmt, ast.AlterTableStmt):
                self.assertEqual(stmt.relation.schemaname, 'pg_temp')
            elif isinstance(stmt, ast.CreatePolicyStmt):
                self.assertEqual(stmt.table.schemaname, 'pg_temp')
            elif isinstance(stmt, ast.CreateFunctionStmt):
                self.assertEqual(stmt.funcname[0].sval, 'pg_temp')
                opts = {o.defname: o.arg for o in stmt.options}
                self.assertEqual(opts['as'][0].sval.strip(), 'SELECT NULL::pg_catalog.int4')
            elif isinstance(stmt, ast.GrantStmt):
                self.assertFalse(stmt.is_grant)
                self.assertEqual(stmt.objects[0].objname[0].sval, 'pg_temp')

    def test_preflight_assertion_parses_and_runs_before_first_temporary_ddl(self):
        kinds = [type(s.stmt).__name__ for s in self.statements]
        self.assertLess(kinds.index('DoStmt'), kinds.index('CreateStmt'))
        for item in self.statements:
            if isinstance(item.stmt, ast.DoStmt):
                self.assertEqual(len(parse_plpgsql(RawStream()(item))), 1)
        self.assertIn('no_event_triggers', self.sql)
        self.assertIn('function_set_headers_and_bodies', self.sql)
        self.assertIn('columns_and_native_types', self.sql)
        self.assertIn('original_grantor_finalization', self.sql)
        self.assertIn('no_restricted_clients', self.sql)

    def test_original_grantor_gate_requires_authenticated_and_effective_identity(self):
        gate = oracle._prerequisites(self.manifest, 'wa_first_rehearsal', 'postgres')['target_identity']
        self.assertIn("current_user='postgres'", gate)
        self.assertIn("session_user='postgres'", gate)
        self.assertIn('SELECT rolsuper FROM pg_roles WHERE rolname=current_user', gate)
        self.assertIn(gate, self.sql)

    def test_checks_are_not_valid_and_no_source_fk_or_guard_is_installed(self):
        checks = []
        for item in self.statements:
            if isinstance(item.stmt, ast.AlterTableStmt):
                for cmd in item.stmt.cmds:
                    if cmd.subtype.name == 'AT_AddConstraint':
                        checks.append(cmd.def_)
        self.assertEqual(len(checks), 93)
        self.assertTrue(all(c.contype.name == 'CONSTR_CHECK' and c.skip_validation for c in checks))
        self.assertFalse(any(isinstance(s.stmt, ast.CreateTrigStmt) for s in self.statements))
        self.assertIn('all_oracle_tables_absent', self.sql)
        self.assertIn('all_oracle_functions_absent', self.sql)

    def test_unpinned_tampered_plan_and_unsafe_identity_reject(self):
        with self.assertRaisesRegex(source.ManifestError, 'complete reviewed source input pin map'):
            oracle.emit_sql(source.build_manifest(), self.plan, database='wa_first_rehearsal', grantor='postgres')
        changed = deepcopy(self.plan); changed['expression_count'] += 1
        with self.assertRaisesRegex(source.ManifestError, 'plan digest mismatch'):
            oracle.emit_sql(self.manifest, changed, database='wa_first_rehearsal', grantor='postgres')
        for bad in ["db'; SELECT 1;--", 'hosted/db', '']:
            with self.assertRaisesRegex(source.ManifestError, 'bounded explicit local'):
                oracle.emit_sql(self.manifest, self.plan, database=bad, grantor='postgres')

    def test_expression_authority_and_whole_row_subquery_cast_reject(self):
        for text in ['(SELECT true)', 'unknown_column = 1', 'example.state IS NULL',
                     "nextval('secret-sequence') > 0", "'x'::app.unreviewed_type"]:
            with self.subTest(text=text), self.assertRaises(source.ManifestError):
                oracle.validate_expression(compare.expression_ast(text), {'state'}, self.manifest['expected'])

    def test_zero_false_empty_and_list_ast_reproduction(self):
        for text in ['0', 'FALSE', "''", "state IN ('a','b')"]:
            expected = compare.expression_ast(text)
            rendered = RawStream()(compare._ast_node(expected))
            self.assertEqual(compare.expression_ast(rendered), expected)
        self.assertIn(compare.text_hash('0'), compare.expression_hashes({'ast': compare.expression_ast('0')}))

    def test_collector_still_has_only_readonly_catalog_statements(self):
        path = Path(source.ROOT) / 'scripts/sql-review/collect_native_catalog.sql'
        sql = path.read_text(encoding='utf-8')
        statements = parse_sql(sql)
        self.assertEqual(len(statements), 4)
        self.assertIsInstance(statements[2].stmt, ast.SelectStmt)
        self.assertIn('BEGIN READ ONLY', sql)
        self.assertIn('tgconstrrelid', sql)
        self.assertIn('tgconstrindid', sql)
        self.assertIn('trigger_dependency_edges', sql)

    def synthetic_evidence(self):
        # Contract-only fixture: it is deliberately not database evidence.
        native = {'server_version_num': 170011, 'read_only': True}
        plan = oracle.build_plan(self.manifest)
        preflight = {'format': 'workinants.expression-oracle-preflight.v1', 'plan_sha256': plan['plan_sha256'],
                     'outcomes': {k: True for k in oracle._prerequisites(self.manifest, 'wa_first_rehearsal', 'postgres')}}
        results = {'format': 'workinants.expression-oracle-results.v1',
            'source_expected_sha256': self.manifest['expected_sha256'],
            'source_inputs_aggregate_sha256': self.manifest['inputs_aggregate_sha256'],
            'plan_sha256': plan['plan_sha256'], 'server_version_num': 170011,
            'expression_count': plan['expression_count'], 'expressions': [
                {**{k: e[k] for k in ('category', 'subject', 'field', 'source_expression_sha256')},
                 'value_sha256': '0' * 64} for e in plan['expressions']]}
        closure = {'format': 'workinants.expression-oracle-closure.v1', 'plan_sha256': plan['plan_sha256'],
                   'all_oracle_tables_absent': True, 'all_oracle_functions_absent': True}
        proof = {'format': 'workinants.reviewed-expression-oracle-evidence.v1', 'database': 'wa_first_rehearsal',
            'oracle_sql_sha256': source.sha256(oracle.emit_sql(self.manifest, plan,
                database='wa_first_rehearsal', grantor='postgres').encode('utf-8')).hexdigest(),
            'preflight': preflight, 'results': results, 'closure': closure,
            'connection_closed_before_observation': True,
            'pre_oracle_catalog_sha256': source.digest(native), 'post_rollback_catalog_sha256': source.digest(native)}
        return native, proof

    def test_synthetic_evidence_contract_requires_all_source_hashes_and_closure(self):
        native, proof = self.synthetic_evidence()
        registry = oracle.validate_evidence(self.manifest, native, proof, database='wa_first_rehearsal', grantor='postgres')
        self.assertEqual(len(registry), 416)
        mutations = [
            lambda p: p.update(oracle_sql_sha256='f' * 64),
            lambda p: p['results'].update(source_expected_sha256='f' * 64),
            lambda p: p['closure'].update(all_oracle_tables_absent=False),
            lambda p: p.update(connection_closed_before_observation=False),
            lambda p: p.update(post_rollback_catalog_sha256='f' * 64),
            lambda p: p['preflight']['outcomes'].update(target_identity=1),
            lambda p: p['results']['expressions'].pop(),
            lambda p: p['results']['expressions'].append(dict(p['results']['expressions'][0])),
            lambda p: p['results']['expressions'][0].update(value_sha256=None),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(source.ManifestError):
                altered = deepcopy(proof); mutation(altered)
                oracle.validate_evidence(self.manifest, native, altered, database='wa_first_rehearsal', grantor='postgres')

    def test_oracle_contract_excludes_arbitrary_retained_fields(self):
        native, proof = self.synthetic_evidence()
        canary = 'SECRET-CANARY-arbitrary-runtime-output'
        proof['raw_probe'] = canary
        with self.assertRaises(source.ManifestError) as failure:
            oracle.validate_evidence(self.manifest, native, proof, database='wa_first_rehearsal', grantor='postgres')
        self.assertNotIn(canary, str(failure.exception))

    def test_reviewed_source_oracle_resolves_hashes_and_real_drift_fails(self):
        expected = {'ast': compare.expression_ast("'active'"), 'ast_sha256': source.digest(compare.expression_ast("'active'"))}
        comparison = compare.Comparison(self.manifest['expected'])
        comparison.hash_expr('columns', 'app.example/state', 'default', expected, '0' * 64)
        self.assertEqual(comparison.totals['INCOMPLETE'], 1)
        comparison.oracle_hashes[('columns', 'app.example/state', 'default', expected['ast_sha256'])] = '0' * 64
        comparison.hash_expr('columns', 'app.example/state', 'default', expected, '0' * 64)
        comparison.hash_expr('columns', 'app.example/state', 'default', expected, '1' * 64)
        self.assertEqual(comparison.totals['PASS'], 1)
        self.assertEqual(comparison.totals['FAIL'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
