"""Source-only ledger registration/comparison mocks. No database/process calls."""
from copy import deepcopy
import json
from pathlib import Path
import runpy
import tempfile
import unittest

from pglast import ast, parse_sql, parse_plpgsql
from pglast.stream import RawStream

import catalog_manifest as source
import compare_native_catalog as comparator
import prisma_ledger_proof as proof


class PrismaLedgerProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = source.build_manifest()
        cls.migration = 'prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql'
        cls.rows = [{'path': cls.migration, 'migration_name': '20261117000100_f0_local_initial',
            'sha256': proof.sha((source.ROOT / cls.migration).read_bytes()), 'state': 'applied', 'count': 1}]
        cls.registration = proof.build_registration(cls.rows, run_id='15d5d9dc-5cee-42c2-9edc-d3fc7d0ef32e',
            target_attestation_sha256='a' * 64, source_expected_sha256=cls.manifest['expected_sha256'])
        cls.native = {'format': 'workinants.native-catalog.v1', 'public_owned_relations': [proof.public_relation()]}
        cls.observation = {**proof.schema_expectation(), 'format': proof.NATIVE_FORMAT, 'server_version_num': 170011,
            'database': 'wa_p0c_rehearsal', 'read_only': True, 'isolation': 'repeatable read',
            'collected_as': 'postgres', 'session_user': 'postgres', 'collector_is_superuser': True,
            'history_ids_unique': True, 'history': deepcopy(cls.registration['history_expected'])}

    def envelope(self, observation=None, registration=None):
        reg = registration or self.registration
        return {'format': proof.EVIDENCE_FORMAT, 'registration_sha256': proof.digest(reg),
            'collector_sql_sha256': reg['tool_source_files_sha256'][proof.COLLECTOR], 'run_id': reg['run_id'],
            'target_attestation_sha256': reg['target_attestation_sha256'],
            'native_catalog_before_sha256': proof.digest(self.native), 'native_catalog_after_sha256': proof.digest(self.native),
            'observation': deepcopy(observation or self.observation)}

    def compare(self, envelope=None, registration=None):
        return proof.compare_proof(registration or self.registration, envelope or self.envelope(), self.native,
            bootstrap_grantor='postgres', source_expected_sha256=self.manifest['expected_sha256'])

    def test_source_bound_complete_mock_passes_without_database_contact(self):
        result = self.compare()
        self.assertEqual(result['status'], 'PASS')
        self.assertTrue(all(check['status'] == 'PASS' for check in result['checks']))
        self.assertEqual(len(self.registration['history_expected']), 1)

    def test_fixed_eight_column_and_pg17_eight_privilege_spec(self):
        spec = proof.schema_expectation()
        self.assertEqual(len(spec['columns']), 8)
        self.assertEqual([column['name'] for column in spec['columns']], ['id', 'checksum', 'finished_at', 'migration_name', 'logs', 'rolled_back_at', 'started_at', 'applied_steps_count'])
        self.assertEqual(len(spec['table_acl']), 8)
        self.assertIn('MAINTAIN', [row['privilege'] for row in spec['table_acl']])
        self.assertEqual(spec['columns'][6]['default_sha256'], proof.text_hash('now()'))
        self.assertEqual(spec['columns'][7]['default_sha256'], proof.text_hash('0'))
        self.assertEqual(spec['indexes'][0]['keys'][0]['opclass'], 'pg_catalog.text_ops')

    def test_missing_native_evidence_stays_incomplete(self):
        result = proof.compare_proof(self.registration, None, self.native, bootstrap_grantor='postgres',
            source_expected_sha256=self.manifest['expected_sha256'])
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_registration_cannot_learn_schema_or_accept_unknown_fields(self):
        for mutation in ({'schema_spec_sha256': 'f' * 64}, {'unexpected_raw_logs': 'do-not-retain'}, {'engine_commit': 'f' * 40}):
            reg = {**self.registration, **mutation}
            self.assertEqual(self.compare(registration=reg)['status'], 'FAIL')
        wrong = deepcopy(self.rows); wrong[0]['sha256'] = 'f' * 64
        with self.assertRaisesRegex(proof.LedgerProofError, 'checksum mismatch'):
            proof.build_registration(wrong, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256='b' * 64)

    def test_new_checksum_is_exact_utf8_with_no_line_ending_or_bom_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / '20261117000100_test/migration.sql'; path.parent.mkdir()
            raw = b'\xef\xbb\xbfSELECT 1;\r\n'; path.write_bytes(raw)
            rows = [{'path': '20261117000100_test/migration.sql', 'migration_name': '20261117000100_test', 'sha256': proof.sha(raw), 'state': 'applied', 'count': 1}]
            reg = proof.build_registration(rows, root=root, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256='b' * 64)
            self.assertEqual(reg['history_expected'][0]['checksum_sha256'], proof.text_hash(proof.sha(raw)))
            rows[0]['sha256'] = proof.sha(b'SELECT 1;\n')
            with self.assertRaises(proof.LedgerProofError):
                proof.build_registration(rows, root=root, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256='b' * 64)

    def test_unsupported_adoption_paths_states_counts_and_names_reject(self):
        for field, value in (('path', '../outside/migration.sql'), ('migration_name', 'not-the-source-directory'),
                              ('state', 'resolve_applied'), ('count', 0), ('count', True)):
            rows = deepcopy(self.rows); rows[0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises((proof.LedgerProofError, OSError)):
                proof.build_registration(rows, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256='b' * 64)

    def test_columns_constraints_and_index_linkage_mutations_fail(self):
        for key in ('columns', 'constraints', 'indexes'):
            observed = deepcopy(self.observation); observed[key] = []
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')
        for field, value in (('typmod', 68), ('nullable', True), ('default_sha256', proof.text_hash('NULL'))):
            observed = deepcopy(self.observation); observed['columns'][0][field] = value
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')
        for field, value in (('unique', False), ('valid', False), ('owner', 'wa_schema_owner')):
            observed = deepcopy(self.observation); observed['indexes'][0][field] = value
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')

    def test_owner_nonowner_column_acl_and_extra_object_mutations_fail(self):
        mutations = [('table_acl', self.observation['table_acl'][:-1]),
            ('table_acl', self.observation['table_acl'] + [{'grantee': 'wa_app_runtime', 'grantor': 'wa_migrator', 'privilege': 'SELECT', 'grant_option': False}]),
            ('column_acl', [{'column': 'logs', 'grantee': 'PUBLIC', 'grantor': 'wa_migrator', 'privilege': 'SELECT', 'grant_option': False}]),
            ('triggers_count', 1), ('policies_count', 1), ('rules_count', 1)]
        for field, value in mutations:
            observed = {**deepcopy(self.observation), field: value}
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')

    def test_history_wrong_checksum_extra_missing_or_wrong_state_rejects(self):
        for field, value in (('checksum_sha256', 'f' * 64), ('steps', 0), ('logs_state', 'EMPTY'), ('id_is_uuid_v4', False),
                              ('time_order_valid', False), ('finished', False), ('rolled_back', True)):
            observed = deepcopy(self.observation); observed['history'][0][field] = value
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')
        for history in ([], self.observation['history'] * 2):
            observed = {**deepcopy(self.observation), 'history': history}
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')

    def test_failed_and_rolled_back_shapes_are_predeclared_not_runtime_learning(self):
        for state, rolled_back in (('failed', False), ('rolled_back', True)):
            rows = deepcopy(self.rows); rows[0]['state'] = state
            reg = proof.build_registration(rows, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256=self.manifest['expected_sha256'])
            expected = reg['history_expected'][0]
            self.assertEqual((expected['finished'], expected['rolled_back'], expected['steps'], expected['logs_state']), (False, rolled_back, 0, 'NONEMPTY'))
            observed = {**self.observation, 'history': reg['history_expected']}
            self.assertEqual(self.compare(self.envelope(observed, reg), reg)['status'], 'PASS')

    def masked_fixture(self, state='failed'):
        diagnostics = runpy.run_path(str(source.ROOT / proof.DIAGNOSTICS))
        identity = {'run_id': self.registration['run_id'], 'container_id': '1' * 64, 'source_commit': '2' * 40,
            'source_tree': '3' * 40, 'packet_sha256': '4' * 64, 'application_sql_sha256': self.rows[0]['sha256'],
            'module_sha256': proof.sha((source.ROOT / proof.DIAGNOSTICS).read_bytes()), 'migration_id': self.rows[0]['migration_name']}
        ready = diagnostics['PREFIX'] + '00000|postgres|wa_p0c_rehearsal|LOG:  server ready\n'
        before = diagnostics['summarize']('', ready)
        after = diagnostics['summarize']('', ready + diagnostics['PREFIX'] + '42501|wa_migrator|wa_p0c_rehearsal|ERROR:  ' + diagnostics['SET_ROLE'] + '\n' +
            diagnostics['PREFIX'] + '25P02|wa_migrator|wa_p0c_rehearsal|ERROR:  ' + diagnostics['ABORTED'] + '\n')
        cli = {'schema': 'workinants.local-f0-migrate-result.v2', 'operation': 'deploy', 'run_id': identity['run_id'], 'container_id': identity['container_id'],
            'source_sql_sha256': identity['application_sql_sha256'], 'status': 'CLI_OUTPUT_REJECTED_STOP_AND_INSPECT', 'exit_code': 1, 'prisma_codes': [], 'sqlstates': []}
        ledger = {key: 0 for key in ('application_relations', 'application_functions', 'application_types', 'application_enums', 'active_migrators')}
        ledger['rows'] = [{'name': identity['migration_id'], 'checksum': identity['application_sql_sha256'], 'finished': False, 'rolled_back': False,
            'steps': 0, 'logs_state': 'NULL', 'expected_error_code': False, 'expected_set_role_error': False}]
        artifact = diagnostics['build_proof'](identity, cli, ledger, before, after, dict.fromkeys(diagnostics['VERIFIED_FIELDS'], True))
        binding = {key: identity[key] for key in ('container_id', 'source_commit', 'source_tree', 'packet_sha256', 'module_sha256')}
        rows = [{**self.rows[0], 'state': state, 'failure_mode': proof.MASKED_MODE, 'failure_proof_sha256': proof.digest(artifact)}]
        registration = proof.build_registration(rows, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64,
            source_expected_sha256=self.manifest['expected_sha256'], failure_binding=binding)
        observed = {**deepcopy(self.observation), 'history': registration['history_expected']}
        envelope = self.envelope(observed, registration); envelope['failed_step_persistence_proofs'] = [artifact]
        return registration, envelope

    def test_masked_null_state_requires_predeclared_same_run_reviewed_source_error_artifact(self):
        for state in ('failed', 'rolled_back'):
            registration, evidence = self.masked_fixture(state)
            self.assertEqual(self.compare(evidence, registration)['status'], 'PASS')
            self.assertEqual(registration['history_expected'][0]['logs_state'], 'NULL')
            absent = {key: value for key, value in evidence.items() if key != 'failed_step_persistence_proofs'}
            self.assertEqual(self.compare(absent, registration)['status'], 'FAIL')
            wrong = deepcopy(evidence); wrong['observation']['history'][0]['logs_state'] = 'NONEMPTY'
            self.assertEqual(self.compare(wrong, registration)['status'], 'FAIL')
        # The generic/default failure still requires NONEMPTY; an observed NULL
        # row can never select the optional mode or promote old unobserved logs.
        rows = [{**self.rows[0], 'state': 'failed'}]
        reg = proof.build_registration(rows, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64, source_expected_sha256=self.manifest['expected_sha256'])
        observed = {**deepcopy(self.observation), 'history': [{**reg['history_expected'][0], 'logs_state': 'NULL'}]}
        self.assertEqual(self.compare(self.envelope(observed, reg), reg)['status'], 'FAIL')

    def test_masked_mode_rejects_wrong_identity_source_counts_types_or_secret_fields(self):
        registration, original = self.masked_fixture()
        mutations = [('run_id', '4bff363e-21bc-4892-a597-98ef1e0bf98d'), ('container_id', '5' * 64), ('source_commit', '6' * 40),
            ('source_tree', '7' * 40), ('packet_sha256', '8' * 64), ('module_sha256', '9' * 64), ('application_sql_sha256', 'a' * 64),
            ('classification', 'NORMAL_P3018_PERSISTENCE'), ('logging_settings_verified', 1), ('application_object_count', False), ('raw_logs', 'SECRET')]
        for field, value in mutations:
            evidence = deepcopy(original); artifact = evidence['failed_step_persistence_proofs'][0]; artifact[field] = value
            # Even when a caller predeclares this mutated artifact hash, source
            # and independent proof requirements must still reject the artifact.
            reg = deepcopy(registration); reg['migrations'][0]['failure_proof_sha256'] = proof.digest(artifact)
            evidence['registration_sha256'] = proof.digest(reg)
            result = self.compare(evidence, reg)
            self.assertEqual(result['status'], 'FAIL', field)
            self.assertNotIn('SECRET', json.dumps(result))
        for field, value in (('expected_set_role_42501', 0), ('aborted_transaction_25p02', 0), ('other_migrator_error', 1), ('registered_lines', True)):
            evidence = deepcopy(original); artifact = evidence['failed_step_persistence_proofs'][0]; artifact['delta'][field] = value
            reg = deepcopy(registration); reg['migrations'][0]['failure_proof_sha256'] = proof.digest(artifact)
            evidence['registration_sha256'] = proof.digest(reg)
            self.assertEqual(self.compare(evidence, reg)['status'], 'FAIL')

    def test_masked_registration_needs_finite_failed_state_and_independent_module_binding(self):
        registration, evidence = self.masked_fixture()
        for field, value in (('state', 'applied'), ('count', 2), ('count', True), ('failure_mode', 'OBSERVED_NULL_LOGS')):
            rows = deepcopy(registration['migrations']); rows[0][field] = value
            with self.assertRaises(proof.LedgerProofError):
                proof.build_registration(rows, run_id=self.registration['run_id'], target_attestation_sha256='a' * 64,
                    source_expected_sha256=self.manifest['expected_sha256'], failure_binding=registration['failure_binding'])
        with self.assertRaises(proof.LedgerProofError):
            proof.build_registration(registration['migrations'], run_id=self.registration['run_id'], target_attestation_sha256='a' * 64,
                source_expected_sha256=self.manifest['expected_sha256'])

    def test_wrong_run_target_snapshot_collector_identity_or_extra_fields_fail(self):
        for field, value in (('run_id', 'bad'), ('target_attestation_sha256', 'f' * 64), ('native_catalog_after_sha256', 'f' * 64), ('collector_sql_sha256', 'f' * 64)):
            evidence = self.envelope(); evidence[field] = value
            self.assertEqual(self.compare(evidence)['status'], 'FAIL')
        for field, value in (('session_user', 'another_superuser'), ('database', 'another_database'), ('server_version_num', 170010), ('read_only', False), ('raw_logs', 'SECRET')):
            observed = {**deepcopy(self.observation), field: value}
            report = self.compare(self.envelope(observed))
            self.assertEqual(report['status'], 'FAIL')
            self.assertNotIn('SECRET', json.dumps(report))

    def test_malformed_numeric_boolean_values_do_not_compare_equal(self):
        for field, value in (('read_only', 1), ('collector_is_superuser', 1), ('history_ids_unique', 1), ('server_version_num', 170011.0)):
            observed = {**deepcopy(self.observation), field: value}
            self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')
        observed = deepcopy(self.observation); observed['columns'][0]['nullable'] = 0
        self.assertEqual(self.compare(self.envelope(observed))['status'], 'FAIL')

    def test_collector_is_read_only_sanitized_source(self):
        text = (source.ROOT / proof.COLLECTOR).read_text(encoding='utf8')
        parsed = parse_sql(text)
        self.assertIsInstance(parsed[0].stmt, ast.TransactionStmt)
        self.assertIsInstance(parsed[-1].stmt, ast.TransactionStmt)
        self.assertEqual(parsed[-1].stmt.kind.name, 'TRANS_STMT_COMMIT')
        self.assertIn('REPEATABLE READ READ ONLY', text)
        self.assertFalse(any(isinstance(row.stmt, (ast.InsertStmt, ast.UpdateStmt, ast.DeleteStmt, ast.CreateStmt)) for row in parsed))
        guard = [row for row in parsed if isinstance(row.stmt, ast.DoStmt)]
        self.assertEqual(len(guard), 1)
        self.assertEqual(len(parse_plpgsql(RawStream()(guard[0]))), 1)
        self.assertIn('LOCK TABLE ONLY public._prisma_migrations IN ACCESS SHARE MODE', text)
        self.assertLess(text.index('LOCK TABLE ONLY'), text.index('DO $wa_ledger_shape$'))
        self.assertLess(text.index('END $wa_ledger_shape$'), text.index('safe_history_rows AS'))
        self.assertIn('current_user<>session_user', text)
        self.assertIn("c.relkind='r'", text)
        self.assertIn("am.amname='heap'", text)
        self.assertIn('ledger collector exact builtin columns required', text)
        self.assertNotIn('FROM public._prisma_migrations', text)
        self.assertIn('FROM ONLY public._prisma_migrations', text)
        self.assertNotIn("'logs',logs", text)
        self.assertNotIn("'id',id", text)
        self.assertNotIn("'migration_name',migration_name", text)
        self.assertIn("CASE WHEN logs IS NULL THEN 'NULL'", text)

    def test_optional_comparator_integration_removes_only_ledger_incomplete_with_valid_proof(self):
        report = comparator.compare_manifest(self.manifest, self.native, bootstrap_grantor='postgres',
            ledger_registration=self.registration, ledger_evidence=self.envelope())
        ledger = [row for row in report['findings'] if row['category'] == 'ledger']
        self.assertEqual(ledger, [])  # Comparator intentionally retains only non-PASS findings.
        self.assertNotEqual(report['status'], 'PASS')  # Other native evidence intentionally absent.
        report = comparator.compare_manifest(self.manifest, self.native, bootstrap_grantor='postgres', ledger_registration=self.registration)
        self.assertTrue(any(row['category'] == 'ledger' and row['status'] == 'INCOMPLETE' for row in report['findings']))


if __name__ == '__main__': unittest.main(verbosity=2)
