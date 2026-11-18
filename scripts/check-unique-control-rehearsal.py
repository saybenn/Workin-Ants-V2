"""Environment-free source and finite scheduling mocks. No DB/process execution."""
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
M = runpy.run_path(str(ROOT / 'scripts/prepare-unique-control-rehearsal.py'))
P = runpy.run_path(str(ROOT / 'scripts/unique_control_protocol.py'))
CANARY = 'SECRET_PASSWORD_HANDLE_PID_XID_SQL_NOT_TO_RETAIN'


class MockPort:
    """Models orchestration states only, never PostgreSQL uniqueness behavior."""
    def __init__(self, race=None, mode='normal'):
        self.race, self.mode, self.events = race, mode, []
        self.opened, self.closed, self.pending, self.retained = set(), set(), set(), set()
        self.cases_started = 0
    def preflight(self, packet):
        self.events.append('preflight')
        return {'source_and_packet_pins': True, 'immutable_target_identity': True, 'auth_finalization_native_parity': True, 'fresh_namespace': self.mode != 'existing-namespace', 'fixture_triggers_restored': True}
    def seed_identity(self, packet):
        self.events.append('seed')
        return {'source_sql_exact': True, 'committed': True, 'backend_closed': True, 'all_triggers_restored': self.mode != 'setup-not-restored'}
    def open_bound(self, side, participant):
        if side == 'A':
            self.opened, self.closed, self.pending, self.retained = set(), set(), set(), set(); self.cases_started += 1
        self.events.append('bind' + side); self.opened.add(side)
        self.race = next(race for race in self.packet['races'] if race['participants']['A']['source_case']['ids']['CustomerProfile'] == participant['source_case']['ids']['CustomerProfile']) if self.race is None else self.race
        return {'actual_app_identity_and_tuple': 1 if self.mode == 'bad-identity-type' else True, 'independent_issuer_commit': True, 'issuer_backend_closed': True, 'bound_same_connection': True}
    def stage_group(self, side, participant):
        self.events.append('ready' + side); self.pending.add(side)
        return {'markers_exact': True, 'constraints_checked': self.mode != 'missing-constraint-check', 'group_ready': True, 'transaction_open': True}
    def start_waiting_command(self, side, participant):
        self.events.append('sendB'); assert 'A' in self.pending and 'A' not in self.closed
        return {'before_marker_exact': True, 'command_sent': True, 'after_marker_absent': True}
    def observe_barrier(self, contract):
        self.events.append('barrier'); assert 'A' in self.pending and not self.retained
        return {**contract['expected'], 'observations': 2, 'within_deadline': self.mode != 'no-overlap'}
    def end_transaction(self, side, outcome):
        self.events.append(outcome + side)
        if outcome == 'COMMIT': self.retained.add(side)
        self.pending.discard(side)
        return {'exit_code': 0, 'acknowledged': self.mode != 'missing-commit-ack', 'transaction_ended': True}
    def close(self, side):
        self.events.append('close' + side); self.pending.discard(side)
        if self.mode == 'closure-unknown' and side == 'B': return {'client_exited': True, 'backend_absent': False}
        self.closed.add(side); return {'client_exited': True, 'backend_absent': True}
    def finish_duplicate(self, side, expected):
        self.events.append('duplicateB'); assert 'A' in self.retained and 'A' in self.closed
        if self.mode == 'unexpected-after-A-commit': raise RuntimeError(CANARY)
        return {'exit_code': 2 if self.mode == 'wrong-exit' else 3, 'acknowledged': self.mode == 'unexpected-ack',
                'sqlstate': 'P0001' if self.mode == 'wrong-state' else '23505', 'schema_table_constraint_exact': self.mode != 'wrong-constraint',
                'native_location_exact': self.mode != 'trigger-frame', 'before_only_marker_exact': self.mode != 'later-marker', 'extra_output_absent': self.mode != 'extra-output'}
    def finish_waiting_command(self, side):
        self.events.append('releasedB'); assert not self.retained and 'A' in self.closed
        return {'before_after_markers_exact': True, 'acknowledged': True, 'transaction_open': True}
    def complete_remainder(self, side, participant): return self.stage_group(side, participant)
    def observe_complete(self, race):
        self.events.append('observe'); assert self.closed == {'A', 'B'}
        wanted = {'A', 'B'} if race['different_subject_scope'] else {race['expected_winner']}
        assert self.retained == wanted
        return {'counts': race['observer_expected'], 'winner_groups_coherent': True, 'winner_transaction_ids_match': True, 'all_triggers_restored': True, 'native_catalog_unchanged': True, 'issuer_grants_immutable': True}
    def observe_partial(self, race):
        self.events.append('partial'); assert self.closed == self.opened
        n = len(self.retained)
        return {'customers': n, 'commands': n, 'history': n, 'evidence': n, 'outbox': 2 * n, 'effects': 0, 'track_enrollments': 0}


class UniqueChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(subprocess, 'run', side_effect=AssertionError('PROCESS_FORBIDDEN')), patch.object(subprocess, 'Popen', side_effect=AssertionError('PROCESS_FORBIDDEN')), patch.object(subprocess, 'check_output', side_effect=AssertionError('PROCESS_FORBIDDEN')):
            cls.files, cls.packet = M['build']()
    def setUp(self):
        for name in ('run', 'Popen', 'check_output'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN')); guard.start(); self.addCleanup(guard.stop)
    def run_one(self, index=0, mode='normal'):
        race = self.packet['races'][index]; port = MockPort(race, mode); saved = []
        result = P['run_race'](race, port, saved.append)
        self.assertFalse(CANARY in json.dumps(saved))
        for field in ('"pid":', '"xid":', '"backend_start":', 'INSERT INTO', 'raw_stderr'):
            self.assertFalse(field in json.dumps(saved))
        return result, port, saved
    def test_exact_three_assertions_and_all_statuses_not_run(self):
        inventory = json.loads((ROOT / 'context/reconciliation/local-f0-assertions.json').read_bytes())
        source = next(case for case in inventory['cases'] if case['id'] == 'P0C-UNIQUE-01')
        self.assertEqual(self.packet['source_assertion_definitions'], source['assertions'])
        self.assertEqual({race['assertion_id'] for race in self.packet['races']}, {row['id'] for row in source['assertions']})
        self.assertTrue(all(row['status'] == 'NOT_RUN' for row in self.packet['races'] + self.packet['remaining_concurrency_matrix']))
        self.assertEqual(self.packet['finite_caps']['races'], 5); self.assertEqual(self.packet['finite_caps']['committed_customer_groups'], 6)
    def test_all_sql_parses_and_no_update_cas_worker_attempt_inbox_route(self):
        for name, text in self.files.items():
            if name.endswith('.sql'):
                with self.subTest(name=name): self.assertTrue(parse_sql(text))
                self.assertNotIn('UPDATE app.customer_profiles', text)
                self.assertNotIn('INSERT INTO platform.runtime_attempt', text); self.assertNotIn('INSERT INTO platform.runtime_inbox_receipt', text)
    def test_source_unique_index_is_exact_four_part_identity(self):
        stmt = next(row.stmt for row in parse_sql((ROOT / 'review-output/foundation-structure.sql').read_text(encoding='utf8')) if isinstance(row.stmt, ast.IndexStmt) and row.stmt.idxname == M['CONSTRAINT'])
        self.assertTrue(stmt.unique); self.assertEqual([col.name for col in stmt.indexParams], ['owner_module_id', 'operation', 'subject_scope', 'semantic_key'])
    def test_shared_scope_and_fingerprint_substitutions_preserve_registered_results(self):
        cm = M['helper'](ROOT); registry = cm.FixtureRegistry(ROOT)
        for race in self.packet['races']:
            a, b = [race['participants'][side]['source_case'] for side in ('A', 'B')]
            self.assertEqual(a['semantic_key'], b['semantic_key'])
            self.assertNotEqual(a['ids']['RuntimeCommandReceipt'], b['ids']['RuntimeCommandReceipt'])
            self.assertEqual(a['ids']['CustomerProfile'] != b['ids']['CustomerProfile'], race['different_subject_scope'])
            self.assertEqual(a['ids']['user'] != b['ids']['user'], race['different_subject_scope'])
            fps = [case['fixture_values']['response']['value']['receipt']['fingerprint'] for case in (a, b)]
            self.assertEqual(fps[0] != fps[1], race['changed_fingerprint'])
            for case in (a, b):
                self.assertEqual(registry.check('SH-004', 'response', case['fixture_values']['response']), [])
                self.assertEqual(case['grant']['target_id'], case['ids']['CustomerProfile'])
                self.assertEqual(case['grant']['principal_user_id'], case['ids']['user'])
                self.assertFalse(any('*' in cap for cap in case['grant']['allowed_fields']))
    def test_fixture_bypasses_only_two_owner_commit_guards_and_restores(self):
        changes = [row.stmt for row in parse_sql(self.files['trusted-identity-fixtures.sql']) if isinstance(row.stmt, ast.AlterTableStmt)]
        self.assertEqual(len(changes), 4); self.assertTrue(all(change.cmds[0].name == 'owner_commit' for change in changes))
        self.assertEqual(len(self.packet['fixture_trigger_contract']['expected_user_triggers']), 4)
        self.assertNotIn('DISABLE TRIGGER USER', '\n'.join(self.files.values()))
    def test_commit_collision_observes_wait_before_holder_commit_and_native_reject(self):
        for index in (0, 2):
            result, port, saved = self.run_one(index)
            self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION')
            self.assertLess(port.events.index('barrier'), port.events.index('COMMITA'))
            self.assertLess(port.events.index('closeA'), port.events.index('duplicateB'))
            self.assertLess(port.events.index('closeB'), port.events.index('observe'))
            self.assertNotIn('readyB', port.events); self.assertEqual(port.retained, {'A'})
            self.assertEqual(result['runtime_assertion_status'], 'NOT_RUN')
    def test_holder_rollback_releases_waiter_complete_group_and_distinct_both_commit(self):
        for index in (1, 3):
            result, port, saved = self.run_one(index)
            self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION')
            self.assertLess(port.events.index('ROLLBACKA'), port.events.index('releasedB'))
            self.assertLess(port.events.index('readyB'), port.events.index('COMMITB'))
            self.assertEqual(port.retained, {'B'})
        result, port, _ = self.run_one(4)
        self.assertLess(port.events.index('readyB'), port.events.index('COMMITA')); self.assertNotIn('barrier', port.events)
        self.assertEqual(port.retained, {'A', 'B'})
    def test_no_overlap_never_qualifies_and_rolls_back_both_before_partial_observation(self):
        result, port, saved = self.run_one(mode='no-overlap')
        self.assertEqual(result['failure']['code'], 'CONCURRENT_WAIT_UNPROVEN')
        self.assertNotIn('COMMITA', port.events); self.assertEqual(port.retained, set())
        self.assertLess(port.events.index('closeB'), port.events.index('partial')); self.assertLess(port.events.index('closeA'), port.events.index('partial'))
    def test_unrelated_state_constraint_location_extra_output_exit_and_marker_reject(self):
        for mode in ('wrong-state', 'wrong-constraint', 'trigger-frame', 'extra-output', 'wrong-exit', 'unexpected-ack', 'later-marker'):
            result, port, saved = self.run_one(mode=mode)
            self.assertEqual(result['status'], 'STOPPED_PROTOCOL_ONLY'); self.assertEqual(result['failure']['code'], 'DUPLICATE_GUARD_UNPROVEN')
            self.assertEqual(result['partial_counts']['customers'], 1)
    def test_unexpected_failure_retains_committed_holder_and_safe_partial_metadata(self):
        result, port, saved = self.run_one(mode='unexpected-after-A-commit')
        self.assertEqual(result['failure']['code'], 'UNEXPECTED_EXCEPTION'); self.assertEqual(result['partial_counts']['customers'], 1)
        self.assertTrue(any(row['stage'] == 'GROUP_A_READY' for row in saved))
    def test_unknown_closure_forbids_business_observation_and_binding_type_fails(self):
        result, port, saved = self.run_one(mode='closure-unknown')
        self.assertEqual(result['failure']['code'], 'OPERATION_CLOSURE_UNCONFIRMED'); self.assertNotIn('partial', port.events); self.assertNotIn('observe', port.events)
        result, port, _ = self.run_one(mode='bad-identity-type'); self.assertEqual(result['failure']['code'], 'ACTUAL_APP_BINDING_UNPROVED')
    def test_packet_stops_later_cases_and_preflight_failure_preserves_metadata(self):
        port = MockPort(self.packet['races'][0], 'wrong-state'); port.packet = self.packet; saved = []
        result = P['run_packet'](self.packet, port, saved.append)
        self.assertEqual(len(result['results']), 1); self.assertTrue(result['subsequent_cases_stopped']); self.assertEqual(port.cases_started, 1)
        port = MockPort(mode='existing-namespace'); saved = []
        result = P['run_packet'](self.packet, port, saved.append)
        self.assertEqual(result['failure']['code'], 'PREFLIGHT_UNPROVED'); self.assertEqual(port.events, ['preflight']); self.assertTrue(saved)
    def test_missing_contracts_remain_explicit_not_run_not_dummy_codecs(self):
        matrix = self.packet['remaining_concurrency_matrix']; cas = [row for row in matrix if row['case_id'] == 'P0C-CAS-01']
        self.assertEqual(len(cas), 4)
        self.assertTrue(all(row['status'] == 'NOT_RUN' and row['execution_dependencies'] for row in cas))
        self.assertTrue(any(M['GATE'] in row['execution_dependencies'] for row in cas))
        self.assertTrue(any(row['case_id'] == 'P0C-TRACK-01' and row['disposition'] == 'SOURCE_PREPARABLE_SEPARATE_LEASE_PACKET_REQUIRED_NOT_RUN' for row in matrix))
    def test_barrier_sql_binds_both_real_tuple_identities_without_exposing_handles(self):
        tuples = {side: {'login': 'wa_app_runtime', 'current_user': 'wa_app_runtime', 'database': 'wa_p0c_rehearsal', 'isolation': 'read committed',
                         'pid': str(100 + index), 'xid': str(500 + index), 'started': '2026-11-17 01:00:00+00'} for index, side in enumerate(('A', 'B'))}
        text = P['barrier_sql'](tuples); self.assertTrue(parse_sql(text))
        self.assertIn('pg_blocking_pids(pid)=ARRAY[100]', text); self.assertIn("wait_event='transactionid'", text)
        self.assertIn('backend_start=', text); self.assertNotIn('backend_xid', text)
        for field, bad in (('pid', "100; SELECT '" + CANARY + "'"), ('started', CANARY), ('login', 'postgres')):
            value = deepcopy(tuples); value['B'][field] = bad
            with self.assertRaises(P['ProtocolStop']) as caught: P['barrier_sql'](value)
            self.assertNotIn(CANARY, str(caught.exception))
    def test_exact_native_duplicate_parser_expects_rls_suppressed_detail(self):
        expected = self.packet['races'][0]['native_duplicate_diagnostic']
        raw = 'ERROR:  23505: ' + expected['exact_message'] + '\nSCHEMA NAME:  platform\nTABLE NAME:  runtime_command_receipt\nCONSTRAINT NAME:  ' + M['CONSTRAINT'] + '\nLOCATION:  _bt_check_unique, nbtinsert.c:638\n'
        self.assertTrue(P['duplicate_diagnostic'](raw, expected)['matched'])
        self.assertTrue(P['duplicate_diagnostic'](raw.replace('\n', '\r\n'), expected)['matched'])
        for value in (raw.replace('23505', 'P0001'), raw.replace('nbtinsert.c', 'pl_exec.c'), raw.replace('SCHEMA NAME:  platform', 'SCHEMA NAME:  app'),
                      raw.replace(M['CONSTRAINT'], 'another_unique_index'), raw + 'DETAIL: Key ' + CANARY + ' already exists.\n', raw + 'ERROR malformed\n', raw + '\x1b]0;' + CANARY + '\x07', raw + '\r'):
            result = P['duplicate_diagnostic'](value, expected); self.assertFalse(result['matched']); self.assertNotIn(CANARY, json.dumps(result))
    def test_fresh_fixture_ids_disjoint_from_existing_packets(self):
        ours = {value for race in self.packet['races'] for participant in race['participants'].values() for value in participant['source_case']['ids'].values()}
        old = json.loads((ROOT / 'review-output/customer-control-rehearsal/fixtures.json').read_bytes())
        theirs = {value for case in old['cases'] for value in case['ids'].values()}
        for path in ('worker-control-rehearsal', 'context-control-rehearsal'):
            old = json.loads((ROOT / ('review-output/' + path + '/fixtures.json')).read_bytes()); theirs |= set(old['source_customer']['ids'].values())
        self.assertFalse(ours & theirs)
    def test_source_pins_checked_before_helper_and_help_is_dormant(self):
        pins = deepcopy(self.packet['source_files_sha256']); pins[M['ACL']] = '0' * 64
        with patch.dict(M['build'].__globals__, helper=lambda _: (_ for _ in ()).throw(AssertionError('UNVERIFIED_HELPER'))):
            with self.assertRaisesRegex(ValueError, 'before helper import'): M['build'](expected_sha256=pins)
        path = ROOT / 'scripts/prepare-unique-control-rehearsal.py'; namespace = {'__file__': str(path), '__name__': 'unique_dormant'}
        with patch.object(M['importlib'].util, 'spec_from_file_location', side_effect=AssertionError('UNVERIFIED_HELPER')):
            exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
            with patch.object(sys, 'argv', [str(path), '--help']), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as found: namespace['main']()
            self.assertEqual(found.exception.code, 0)
    def test_source_byte_reproduction_and_packet_hashes(self):
        files, packet = M['build'](expected_sha256=self.packet['source_files_sha256']); self.assertEqual(files, self.files)
        for name, digest in packet['prepared_files_sha256'].items(): self.assertEqual(hashlib.sha256(files[name].encode()).hexdigest(), digest)
        if M['OUT'].exists():
            self.assertEqual({path.name for path in M['OUT'].iterdir()}, set(files))
            for name, text in files.items(): self.assertEqual((M['OUT'] / name).read_bytes(), text.encode())


if __name__ == '__main__': unittest.main(verbosity=2)
