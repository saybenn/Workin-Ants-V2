"""Environment-free source/packet checks. Every subprocess boundary is refused.

These checks qualify a proposed protocol and typed source artifacts only; no
database, authentication, transaction, rollback or grant behavior is executed.
"""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

from pglast import ast, parse_sql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
M = runpy.run_path(str(ROOT / 'scripts/prepare-context-control-rehearsal.py'))


class ContextPacketChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(subprocess, 'run', side_effect=AssertionError('PROCESS_FORBIDDEN')), patch.object(subprocess, 'Popen', side_effect=AssertionError('PROCESS_FORBIDDEN')), patch.object(subprocess, 'check_output', side_effect=AssertionError('PROCESS_FORBIDDEN')):
            cls.files, cls.packet = M['build']()

    def setUp(self):
        for name in ('run', 'Popen', 'check_output'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('PROCESS_FORBIDDEN'))
            guard.start(); self.addCleanup(guard.stop)

    def test_selected_definition_and_not_run_boundaries_are_exact(self):
        source = json.loads((ROOT / 'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))
        expected = next(row for row in source['tests'] if row['id'] == 'P0C-CTX-01')
        self.assertEqual(self.packet['source_control_definition'], expected)
        self.assertEqual(self.packet['selected_control_ids'], ['P0C-CTX-01'])
        self.assertEqual(self.packet['database_posture'], 'D')
        for row in self.packet['cases'] + self.packet['unprepared_obligations']:
            self.assertEqual(row['status'], 'NOT_RUN'); self.assertTrue(row['execution_dependencies'])
        self.assertFalse(self.packet['database_contacted']); self.assertFalse(self.packet['sql_executed'])
        self.assertEqual(self.packet['source_creation_lifetime_protocol']['status'], 'NOT_RUN')

    def test_every_generated_sql_parses_without_psql_substitution(self):
        for name, text in self.files.items():
            if name.endswith('.sql'):
                with self.subTest(name=name): self.assertTrue(parse_sql(text))

    def test_only_two_exact_owner_commit_setup_bypasses_with_full_restoration(self):
        statements = parse_sql(self.files['trusted-identity-fixtures.sql'])
        changes = [item.stmt for item in statements if isinstance(item.stmt, ast.AlterTableStmt)]
        self.assertEqual(len(changes), 4)
        self.assertEqual([(item.relation.schemaname, item.relation.relname) for item in changes],
                         [('app', 'users'), ('app', 'user_security_profiles'), ('app', 'user_security_profiles'), ('app', 'users')])
        self.assertTrue(all(len(item.cmds) == 1 and item.cmds[0].name == 'owner_commit' for item in changes))
        expected = self.packet['fixture_trigger_contract']
        self.assertTrue(expected['physical_guards_retained'])
        self.assertEqual(len(expected['expected_user_triggers']), 4)
        observer = self.files['fixture-trigger-restore-observe.sql']
        for fragment in ('EXCEPT SELECT * FROM actual', 'EXCEPT SELECT * FROM expected', 't.tgenabled', 'no_project_user_trigger_disabled'):
            self.assertIn(fragment, observer)
        self.assertNotIn('DISABLE TRIGGER USER', '\n'.join(self.files.values()))

    def test_source_creation_retries_exact_group_once_only_terminal_outcome_changes(self):
        normal = self.files['source-customer.sql'].rstrip()
        rolled = self.files['source-customer-rollback.sql'].rstrip()
        self.assertTrue(normal.endswith('COMMIT;'))
        self.assertEqual(rolled, normal[:-len('COMMIT;')] + 'SET CONSTRAINTS ALL IMMEDIATE;\nROLLBACK;')
        steps = self.packet['source_creation_lifetime_protocol']['steps']
        issues = [step for step in steps if step['op'] == 'issue']
        self.assertEqual([step['instance'] for step in issues], ['CREATE1', 'CREATE2'])
        self.assertTrue(all(step['template'] == 'source_customer' for step in issues))
        self.assertEqual([step['file'] for step in steps if step['op'] == 'sql'], ['source-customer-rollback.sql', 'source-customer.sql'])
        self.assertEqual(steps[-3]['op'], 'close')
        self.assertEqual(self.packet['source_creation_lifetime_protocol']['semantic_key'], self.packet['source_customer']['semantic_key'])

    def test_actual_scopes_and_finite_caps_do_not_invent_worker_query_or_customer_sh003(self):
        source = json.loads((ROOT / 'context/reconciliation/foundation-sql-scope-policy.json').read_text(encoding='utf8'))
        self.assertIn(self.packet['registered_positive_scope'], source['domain_scopes'])
        app, worker = [self.packet['grants'][key] for key in ('app', 'worker')]
        self.assertEqual((app['action'], app['purpose'], app['target_kind']), ('SH-004.v1', 'resolve', 'CustomerProfile'))
        self.assertEqual((worker['action'], worker['purpose'], worker['target_kind']), ('runtime.claim_work.v1', 'work.claim', 'RuntimeWorkItem'))
        self.assertFalse(any('/UPDATE/' in value or '/INSERT/' in value for grant in (app, worker) for value in grant['allowed_fields']))
        self.assertTrue(all('*' not in value for grant in self.packet['grants'].values() for value in grant['allowed_fields']))
        acl = json.loads((ROOT / M['ACL']).read_text(encoding='utf8'))
        self.assertEqual(self.packet['worker_acl_ceiling_rows'], [row for row in acl if row['role'] == 'wa_worker'])
        self.assertEqual(len(self.packet['worker_acl_ceiling_rows']), 32)
        for key in ('worker_claims', 'worker_processing', 'worker_enrollments'):
            self.assertEqual(self.packet['finite_caps'][key], 0)
        self.assertFalse(self.packet['finite_caps']['polling_or_worker_loop'])

    def test_fresh_namespace_disjoint_from_customer_and_worker_packets(self):
        ours = set(self.packet['namespace_policy']['ids'].values())
        customer = json.loads((ROOT / 'review-output/customer-control-rehearsal/fixtures.json').read_text(encoding='utf8'))
        theirs = {value for case in customer['cases'] for value in case['ids'].values()}
        worker = json.loads((ROOT / 'review-output/worker-control-rehearsal/fixtures.json').read_text(encoding='utf8'))
        theirs |= set(worker['ids'].values()) | set(worker['source_customer']['ids'].values())
        self.assertFalse(ours & theirs)
        self.assertEqual(self.packet['namespace_policy']['mode'], 'FRESH_DISJOINT_ONLY')

    def test_savepoint_and_pool_protocol_preserve_same_xid_rebind_and_new_xid_boundary(self):
        cases = {row['name']: row for row in self.packet['cases']}
        for family in ('app', 'worker'):
            steps = cases[family + '-savepoint-bind-rollback-rebind']['steps']
            sql_steps = [step for step in steps if step['op'] == 'sql']
            self.assertEqual([step['file'] for step in sql_steps], ['savepoint.sql', family + '-read.sql', 'rollback-to-savepoint.sql', family + '-read.sql', family + '-read.sql', 'rollback.sql'])
            self.assertEqual([step['expected'] for step in sql_steps if step['file'] == family + '-read.sql'], [{'visible_exact_root': 1}, {'visible_exact_root': 0}, {'visible_exact_root': 1}])
            self.assertEqual([step['instance'] for step in steps if step['op'] == 'bind'], ['G1', 'G1'])
            for ending in ('commit', 'rollback'):
                pooled = cases[family + '-' + ending + '-same-pool-fresh-then-old']['steps']
                captures = [step for step in pooled if step['op'] == 'capture']
                self.assertEqual(captures[1]['require_same_backend_as'], 'T1')
                self.assertEqual(captures[1]['require_distinct_xid_from'], 'T1')
                self.assertEqual([step['instance'] for step in pooled if step['op'] == 'issue'], ['G1', 'G2'])
                self.assertTrue(all(step['commit_and_close_issuer_before_bind'] for step in pooled if step['op'] == 'issue'))

    def test_errors_close_before_observers_no_on_error_stop_relaxation_or_later_behavior(self):
        for case in self.packet['cases'] + [self.packet['source_creation_lifetime_protocol']]:
            steps = case['steps']; dead = set()
            for step in steps:
                self.assertIn(step['op'], M['OPS'])
                if step['op'] == 'expect_bind_error':
                    self.assertEqual(step['psql_exit_code'], 3); self.assertIs(step['acknowledgement'], False)
                    self.assertTrue(step['later_statements_forbidden']); dead.add(step['session'])
                elif step['op'] == 'close': dead.discard(step['session'])
                elif step.get('session') in dead: self.fail('Statement after expected binder error')
                if step['op'] == 'observer': self.assertFalse(dead)
            self.assertFalse(dead)
        self.assertNotIn('ON_ERROR_STOP', '\n'.join(text for name, text in self.files.items() if name.endswith('.sql')))

    def test_read_purpose_has_otherwise_matching_update_caps_and_zero_row_verdict(self):
        grant = self.packet['grants']['app-read-with-update-caps']
        self.assertEqual(grant['purpose'], 'resolve')
        prefix = 'CustomerProfile/' + grant['target_id'] + '/UPDATE/'
        self.assertTrue({prefix + name for name in ('@row', 'displayName', 'revision')} <= set(grant['allowed_fields']))
        case = next(row for row in self.packet['cases'] if row['name'] == 'app-resolve-purpose-denies-source-update')
        self.assertEqual([step['expected'] for step in case['steps'] if step['op'] == 'sql'], [{'visible_exact_root': 1}, {'modified': 0}, None])
        self.assertIn('has_column_privilege', self.files['grant-write-acl-observe.sql'])

    def test_all_old_instances_require_retention_expiry_and_new_tuple_denial(self):
        for case in self.packet['cases']:
            self.assertIn('EACH case-issued old instance', case['mandatory_after_case'])
        binding = self.packet['runtime_binding_contract']
        self.assertIn('EVERY issued instance', binding['every_old_instance'])
        self.assertIn('unexpired', binding['grant_retention'])
        self.assertIn('tuple', binding['every_old_instance'])
        self.assertIn('raw rows', binding['grant_retention'])

    def test_every_case_requires_complete_state_and_trigger_acl_observers_after_closure(self):
        observers = {row['file']: row['expected'] for row in self.packet['mandatory_after_case_observers']}
        self.assertEqual(set(observers), {'source-customer-observe.sql', 'work-observe.sql', 'fixture-trigger-restore-observe.sql', 'grant-write-acl-observe.sql'})
        self.assertEqual(observers['source-customer-observe.sql'], self.packet['source_customer']['observer_expected'])
        self.assertEqual(observers['work-observe.sql'], {'work_count': 1, 'exact_pending_work': True, 'attempts': 0, 'track_enrollments': 0})
        self.assertTrue(all(observers['grant-write-acl-observe.sql'].values()))
        self.assertIn('ALL original/retirement clients exit', self.packet['after_case_observer_order'])
        self.assertIn('No later case', self.packet['after_case_observer_order'])

    def test_source_pin_mismatch_stops_before_any_helper_import(self):
        pins = deepcopy(self.packet['source_files_sha256']); pins[M['APPLICATION']] = '0' * 64
        globals_ = M['build'].__globals__
        with patch.dict(globals_, helper=lambda root: (_ for _ in ()).throw(AssertionError('UNVERIFIED_HELPER'))):
            with self.assertRaisesRegex(ValueError, 'approved source pins differ'): M['build'](expected_sha256=pins)

    def test_import_and_help_do_not_execute_helpers_or_processes(self):
        path = ROOT / 'scripts/prepare-context-control-rehearsal.py'
        namespace = {'__file__': str(path), '__name__': 'context_source_import_mock'}
        with patch.object(M['importlib'].util, 'spec_from_file_location', side_effect=AssertionError('UNVERIFIED_HELPER')):
            exec(compile(path.read_text(encoding='utf8'), str(path), 'exec'), namespace)
            with patch.object(sys, 'argv', [str(path), '--help']), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as found:
                namespace['main']()
            self.assertEqual(found.exception.code, 0)

    def test_byte_reproduction_and_manifest_fingerprints(self):
        files, packet = M['build'](expected_sha256=self.packet['source_files_sha256'])
        self.assertEqual(files, self.files); self.assertEqual(packet, self.packet)
        for name, digest in packet['prepared_files_sha256'].items():
            self.assertEqual(hashlib.sha256(files[name].encode()).hexdigest(), digest)
        if M['OUT'].exists():
            self.assertEqual({item.name for item in M['OUT'].iterdir()}, set(files))
            for name, text in files.items(): self.assertEqual((M['OUT'] / name).read_bytes(), text.encode('utf8'))


if __name__ == '__main__': unittest.main(verbosity=2)
