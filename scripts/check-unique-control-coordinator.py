"""Environment-free UNIQUE transport mocks; all process/network boundaries mocked.

Queue streams exercise the actual pinned Session readers and asynchronous waiter
adapter. The simulated engine proves orchestration only, never PostgreSQL or any
of the 94 selected runtime cases. Every original control remains NOT_RUN.
"""
import builtins
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import queue
import re
import runpy
import socket
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts/sql-review/run-unique-control-rehearsal.py'
M = runpy.run_path(str(PATH))
P = runpy.run_path(str(ROOT / M['PROTOCOL']))
RUN = '719dffcb-a5f9-4a93-bffe-7faf83f7a914'
CID = 'c' * 64
CANARY = 'postgresql://UNLISTED_PASSWORD_HANDLE@unlisted.invalid/RAW_STATEMENT'


class Stream:
    def __init__(self): self.items = queue.Queue()
    def put(self, value): self.items.put(value)
    def readline(self, size=-1): return self.items.get(timeout=10)
    def read(self, size=-1): return self.items.get(timeout=10)


class Pipe:
    def __init__(self, process): self.process = process
    def write(self, text): self.process.engine.sql(self.process, text)
    def flush(self): pass
    def close(self): pass


class Process:
    def __init__(self, engine, args, **kwargs):
        assert kwargs == {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 'text': True, 'bufsize': 1, 'shell': False}
        self.engine = engine; self.role = args[args.index('-U') + 1]; self.returncode = None; self.stdout = Stream(); self.stderr = Stream(); self.stdin = Pipe(self)
        self.pid = str(600000 + len(engine.processes)); self.xid = str(900000 + len(engine.processes)); self.backend = None; self.participant = None; self.pending = None; self.outcome = None
        self.waited = threading.Event(); engine.processes.append(self); engine.calls.append(('Popen', tuple(args)))
    def poll(self): return self.returncode
    def wait(self, timeout=None):
        if not self.waited.wait(timeout): raise subprocess.TimeoutExpired('MOCKED', timeout)
        return self.returncode
    def exit(self, code=0, error=''):
        if self.returncode is None:
            if error: self.stderr.put(error)
            self.returncode = code; self.stdout.put(''); self.stderr.put(''); self.waited.set()
    def terminate(self): self.exit(143)
    def kill(self): self.exit(137)
    def row(self, value): self.stdout.put(value + '\n')


class Engine:
    """No SQL parser/database: matches the pinned fixture commands literally."""
    def __init__(self, packet, native, ctx):
        self.packet, self.native, self.ctx = packet, native, ctx; self.processes = []; self.calls = []; self.events = []; self.created = {}; self.adapter = None
        self.mode = 'normal'; self.observer_calls = 0; self.barrier_calls = 0; self.participant_by_file = {}; self.statements = []
        for race in packet['races']:
            for side, participant in race['participants'].items():
                for key in ('hold_ready_sql', 'command_sql', 'remainder_sql'): self.participant_by_file[participant[key]] = (race, side, participant, key)
    def popen(self, args, **kwargs): return Process(self, args, **kwargs)
    def acknowledgements(self, text): return re.findall(r"SELECT '((?:WA_CTX01_ACK|WA_UNIQUE_ASYNC_ACK)\|[0-9a-f]{32})';", text)
    def sql(self, process, text):
        if process.returncode is not None: raise BrokenPipeError('MOCKED_PROCESS_CLOSED')
        ack = self.acknowledgements(text); terminal = text.split('\nSELECT ')[0].strip()
        if '\\q' in text: self.events.append(('close', process.role, process.pid)); process.exit(); return
        self.statements.append(text)
        if self.ctx['TUPLE'] in text:
            process.backend = {'login': process.role, 'current_user': process.role, 'database': M['DATABASE'], 'isolation': 'read committed', 'pid': process.pid, 'xid': process.xid,
                               'started': '2026-11-18 05:00:00+00', 'clock': '2026-11-18 05:00:01+00'}
            process.row(self.ctx['TUPLE'] + json.dumps(process.backend))
        elif 'INSERT INTO platform.database_action_grant (' in text:
            identity = re.search(r"VALUES \('([0-9a-f-]{36})'::uuid", text)[1]; stamp = '2026-11-18T05:00:02.123456+00:00'; self.created[identity] = stamp
            assert "RETURNING pg_catalog.jsonb_build_object('created_at',created_at)" in text
            process.row(json.dumps({'created_at': CANARY if self.mode == 'bad-issued-time' else stamp})); self.events.append(('issuer_commit', process.pid))
        elif 'bind_request_context(' in text:
            secret = re.search(r"bind_request_context\('([^']*)'\)", text)[1]
            instance = next(value for value in self.adapter.issuer.instances.values() if value['secret'] == secret)
            assert instance['backend']['pid'] == process.pid and instance['backend']['xid'] == process.xid
            assert all(p.returncode is not None for p in self.processes if p.role == 'wa_context_issuer')
            self.events.append(('bind', process.pid))
        elif terminal in ('COMMIT;', 'ROLLBACK;'):
            process.outcome = terminal[:-1]; self.events.append((process.outcome, process.pid))
            # A's terminal transaction releases B's simulated native index wait.
            for waiting in self.processes:
                if waiting.pending is None: continue
                race, side, participant, token = waiting.pending
                if process.participant is not race['participants']['A']: continue
                waiting.pending = None
                if process.outcome == 'COMMIT':
                    expected = race['native_duplicate_diagnostic']; error = diagnostic(expected)
                    if self.mode == 'wrong-duplicate': error = error.replace('23505:', 'P0001:')
                    elif self.mode == 'extra-duplicate': error += 'ERROR: malformed ' + CANARY + '\n'
                    elif self.mode == 'duplicate-detail': error += 'DETAIL: ' + CANARY + '\n'
                    elif self.mode == 'osc-duplicate': error += '\x1b]0;' + CANARY + '\x07'
                    elif self.mode == 'extra-stdout': waiting.row(CANARY)
                    waiting.exit(2 if self.mode == 'wrong-exit' else 3, error)
                else:
                    waiting.row(participant['markers']['after_command']); waiting.row(token)
        else:
            for filename, (race, side, participant, key) in self.participant_by_file.items():
                payload = (M['PACKET'] / filename).read_text(encoding='utf8')
                if not text.startswith(payload): continue
                process.participant = participant
                marker = participant['markers']
                if key == 'command_sql' and side == 'B':
                    process.row(marker['before_command']); process.pending = (race, side, participant, ack[-1]); self.events.append(('async_sent', process.pid)); return
                if key == 'hold_ready_sql':
                    process.row(marker['before_command']); process.row(marker['after_command'])
                process.row(marker['group_ready']); self.events.append(('ready', process.pid)); break
        if ack:
            if self.mode == 'missing-commit-ack' and terminal == 'COMMIT;': process.exit(); return
            process.row(ack[-1])
    def run(self, args, **kwargs):
        assert kwargs.get('shell') is False and kwargs['text'] is True and kwargs['capture_output'] is True
        assert args.count(CID) == 1 and args[args.index('-U') + 1] in ('postgres', 'wa_context_issuer', 'wa_app_runtime')
        text = kwargs['input']; self.calls.append(('run', tuple(args), kwargs['timeout'])); output = None
        self.statements.append(text)
        if 'pg_blocking_pids' in text:
            self.barrier_calls += 1; assert 0 < kwargs['timeout'] <= 1
            assert "SET statement_timeout='500ms'" in text
            waiting = next(p for p in self.processes if p.pending is not None)
            race = waiting.pending[0]; self.events.append(('barrier', waiting.pid))
            if self.mode == 'barrier-secret': output = {'UNLISTED': CANARY}
            else: output = {k: self.mode != 'no-wait' for k in race['barrier']['expected']}
        elif 'FROM pg_stat_activity WHERE pid=' in text: output = '0' if self.mode != 'backend-present' else '1'
        elif 'all_immutable_fields_equal' in text:
            ids = re.findall(r"WHERE g.id='([0-9a-f-]{36})'::uuid", text)
            stamps = all('g.created_at IS NOT DISTINCT FROM (' + M['quote'](self.created[key]) + '::timestamptz)' in text for key in ids)
            output = {'exact_count': len(ids), 'all_immutable_fields_equal': stamps and self.mode != 'retention-drift', 'issuer_owned': True, 'revoked_false': True, 'unexpired': True}
        elif 'workinants.native-catalog.v1' in text: output = self.native if self.mode != 'native-drift' else {**self.native, 'UNLISTED': CANARY}
        elif 'exact_user_trigger_set_and_states' in text:
            output = {'expected_user_trigger_count': 4, 'actual_user_trigger_count': 4, 'exact_user_trigger_set_and_states': self.mode != 'trigger-not-restored', 'no_project_user_trigger_disabled': True}
        elif 'source_xid_matches' in text: output = dict.fromkeys(('source_xid_matches', 'command_xid_matches', 'history_xid_matches', 'evidence_xid_matches', 'outbox_xid_matches'), self.mode != 'wrong-winner-xid')
        else:
            for race in self.packet['races']:
                if text == (M['PACKET'] / race['observer_sql']).read_text(encoding='utf8'):
                    live = [p for p in self.processes if p.role == 'wa_app_runtime' and p.returncode is None]; assert live == [], 'BUSINESS_OBSERVER_BEFORE_CLOSURE'
                    self.observer_calls += 1; self.events.append(('observe', race['name']))
                    relevant = [p for p in self.processes if any(p.participant is v for v in race['participants'].values())]
                    winners = sum(p.outcome == 'COMMIT' for p in relevant)
                    output = {'customers': winners, 'commands': winners, 'history': winners, 'evidence': winners, 'outbox': 2 * winners, 'effects': 0, 'track_enrollments': 0}; break
                for participant in race['participants'].values():
                    if text == (M['PACKET'] / participant['observer_sql']).read_text(encoding='utf8'): output = participant['source_case']['observer_expected']; break
                if output is not None: break
        if output is None:
            if text.startswith('SELECT NOT EXISTS') or "current_setting('server_version_num')" in text: output = 't'
            else: raise AssertionError('UNREGISTERED_MOCK_OBSERVER')
        return subprocess.CompletedProcess(args, 0, output if type(output) is str else json.dumps(output), '')


def diagnostic(expected):
    return 'ERROR:  23505: ' + expected['exact_message'] + '\nSCHEMA NAME:  ' + expected['schema'] + '\nTABLE NAME:  ' + expected['table'] + '\nCONSTRAINT NAME:  ' + expected['constraint'] + '\nLOCATION:  ' + expected['native_routine'] + ', ' + expected['native_file'] + ':638\n'


class CoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((M['PACKET'] / 'fixtures.json').read_bytes())
        cls.native = {'format': 'workinants.native-catalog.v1', 'server_version_num': 170011, 'read_only': True, 'collected_as': 'postgres', 'collector_is_superuser': True}
        cls.ctx = M['compile_cached'](M['CTX_PATH'], (ROOT / M['CTX_PATH']).read_bytes())
        cls.ctx['load_helpers']({p: (ROOT / p).read_bytes() for p in cls.ctx['SOURCE_MODULES']})
    def setUp(self):
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('NETWORK_FORBIDDEN')))
        for name in ('check_call', 'check_output'): self.stack.enter_context(patch.object(subprocess, name, side_effect=AssertionError('PROCESS_FORBIDDEN')))
        self.temporary = self.stack.enter_context(tempfile.TemporaryDirectory(dir=M['TASK']))
        self.evidence = M['Evidence'](Path(self.temporary) / 'evidence')
        self.plan = {'run_id': RUN, 'source_commit': 'a' * 40, 'source_tree': 'b' * 40, 'packet_sha256': 'd' * 64, 'immutable_container_id': CID,
                     'source_modules_sha256': {p: M['sha']((ROOT / p).read_bytes()) for p in M['MODULES']}}
        self.engine = Engine(self.packet, self.native, self.ctx)
        self.stack.enter_context(patch.object(subprocess, 'Popen', side_effect=self.engine.popen)); self.stack.enter_context(patch.object(subprocess, 'run', side_effect=self.engine.run))
        self.adapter = M['Adapter'](self.plan, self.packet, self.native, {}, self.ctx, P, self.evidence); self.engine.adapter = self.adapter
        self.adapter.resource = lambda: self.adapter.record('MOCKED_RESOURCE', exact_created_container=True)
        self.auth_calls = []
        self.stack.enter_context(patch.dict(self.ctx['API'], {'authentication_preflight': lambda evidence, cid: self.auth_calls.append(cid)}))
    def safe(self):
        text = json.dumps(self.evidence.value)
        for forbidden in (CANARY, 'INSERT INTO', 'raw_stderr', '"pid":', '"xid":', '"started":'):
            self.assertNotIn(forbidden, text)
        for process in self.engine.processes:
            if process.backend:
                for key in ('pid', 'xid', 'clock', 'started'): self.assertNotIn(process.backend[key], text)
        for instance in self.adapter.issuer.instances.values():
            for key in ('secret', 'token_hash', 'id'): self.assertNotIn(instance[key], text)
        self.assertEqual(self.evidence.value['selected_controls'], [{'id': 'P0C-UNIQUE-01', 'status': 'NOT_RUN'}])
    def race(self, index=0): return P['run_race'](self.packet['races'][index], self.adapter, self.adapter.protocol_save)
    def test_all_five_races_actual_session_subprocess_boundaries(self):
        self.adapter.run(); self.safe()
        self.assertEqual(self.auth_calls, [CID]); self.assertEqual(self.engine.barrier_calls, 4); self.assertEqual(len(self.evidence.value['committed_groups']), 6)
        self.assertEqual(len(self.adapter.issuer.instances), 10); self.assertEqual(self.adapter.total_apps, 10)
        self.assertTrue(all(p.returncode is not None for p in self.engine.processes))
        self.assertEqual(self.evidence.value['status'], 'COMPLETED_FIVE_SQL_STORAGE_RACES_ONLY_ASSERTIONS_NOT_RUN')
        self.assertTrue(all(row['runtime_assertion_status'] == 'NOT_RUN' for row in self.evidence.value['results']))
        self.assertTrue(all(CID in call[1] and 'PGAPPNAME=wa-unique-' + RUN in call[1] for call in self.engine.calls))
    def test_async_wait_precedes_a_commit_and_b_close_precedes_observation(self):
        result = self.race(); self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION')
        labels = [row[0] for row in self.engine.events]; self.assertLess(labels.index('barrier'), labels.index('COMMIT')); self.assertLess(max(i for i, x in enumerate(labels) if x == 'close'), labels.index('observe'))
        verdict = next(row for row in self.evidence.value['operations'] if row['stage'] == 'NATIVE_DUPLICATE_VERDICT')
        self.assertEqual(verdict['exit_code'], 3); self.assertIs(verdict['acknowledgement'], False); self.safe()
    def test_a_rollback_releases_b_then_complete_winner(self):
        result = self.race(1); self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION'); self.safe()
        self.assertEqual(self.evidence.value['committed_groups'], [{'race': self.packet['races'][1]['name'], 'side': 'B', 'commit_acknowledged': True}])
    def test_distinct_subjects_both_ready_before_first_commit(self):
        result = self.race(4); self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION')
        events = [row[0] for row in self.engine.events]; self.assertEqual(events[:events.index('COMMIT')].count('ready'), 2); self.assertNotIn('barrier', events); self.safe()
    def test_issuer_generated_created_at_all21_fields_and_commit_before_bind(self):
        self.race(); self.assertTrue(self.adapter.issuer.instances)
        for instance in self.adapter.issuer.instances.values():
            self.assertEqual(set(instance['values']), set(self.ctx['GRANT_COLUMNS'])); self.assertIn(self.engine.created[instance['id']], instance['values']['created_at'])
            self.assertNotEqual(instance['values']['created_at'], M['quote']('2026-11-18 05:00:01+00') + '::timestamptz')
        self.safe()
    def test_expected_native_state_requires_exact_exit_and_no_detail_extra_or_controls(self):
        for mode in ('wrong-exit', 'wrong-duplicate', 'extra-duplicate', 'duplicate-detail', 'osc-duplicate', 'extra-stdout'):
            with self.subTest(mode=mode):
                self.engine.processes.clear(); self.adapter.total_apps = 0; self.adapter.issuer.sequence = 0; self.adapter.issuer.instances.clear()
                self.engine.mode = mode; result = self.race(); self.assertEqual(result['status'], 'STOPPED_PROTOCOL_ONLY'); self.assertEqual(result['failure']['code'], 'DUPLICATE_GUARD_UNPROVEN')
                self.assertEqual(result['partial_counts']['customers'], 1); self.safe()
    def test_unexpected_after_a_commit_stops_later_cases_preserves_winner(self):
        self.engine.mode = 'extra-duplicate'
        with self.assertRaises(M['HeldFailure']): self.adapter.run()
        self.assertEqual(len(self.evidence.value['results']), 1); self.assertEqual(len(self.evidence.value['committed_groups']), 1)
        self.assertEqual(self.evidence.value['results'][0]['partial_counts']['customers'], 1); self.assertTrue(self.evidence.value['subsequent_cases_stopped']); self.safe()
    def test_barrier_wrong_shape_sanitized_then_close_both_and_stop(self):
        self.engine.mode = 'barrier-secret'; result = self.race()
        self.assertEqual(result['status'], 'STOPPED_PROTOCOL_ONLY'); self.assertTrue(all(result['closed'].values())); self.assertEqual(result['partial_counts']['customers'], 0); self.safe()
    def test_wrong_winner_transaction_and_retention_never_complete(self):
        for mode in ('wrong-winner-xid', 'retention-drift'):
            with self.subTest(mode=mode):
                self.engine.mode = mode; result = self.race(); self.assertEqual(result['status'], 'STOPPED_PROTOCOL_ONLY'); self.assertFalse(result['comparisons'].get('complete_state', False)); self.safe()
    def test_bad_created_at_stops_before_bind_and_excludes_secret(self):
        self.engine.mode = 'bad-issued-time'; result = self.race()
        self.assertEqual(result['status'], 'STOPPED_PROTOCOL_ONLY'); self.assertFalse(any(row[0] == 'bind' for row in self.engine.events)); self.safe()
    def test_restore_failure_prevents_restricted_sql_and_later_cases(self):
        self.engine.mode = 'trigger-not-restored'
        with self.assertRaises(M['HeldFailure']): self.adapter.run()
        self.assertEqual(self.engine.processes, []); self.safe()
    def test_business_observer_refuses_live_connections(self):
        self.adapter.open_bound('A', self.packet['races'][0]['participants']['A'])
        with self.assertRaises(M['HeldFailure']) as error: self.adapter.observe_complete(self.packet['races'][0])
        self.assertEqual(error.exception.code, 'BUSINESS_OBSERVER_BEFORE_CLOSURE'); self.adapter.cleanup_mode = True; self.adapter.close('A'); self.safe()
    def test_sparse_native_counts_and_bad_types(self):
        self.assertTrue(M['native_counts']({'PASS': 200})); self.assertTrue(M['native_counts']({'PASS': 1, 'FAIL': 0, 'INCOMPLETE': 0}))
        for value in ({}, {'PASS': True}, {'PASS': 0}, {'PASS': 1, 'FAIL': True}, {'PASS': 1, 'FAIL': 1}, {'PASS': 1, 'other': 0}): self.assertFalse(M['native_counts'](value))
    def test_import_help_are_stdlib_only_and_execute_flag_mandatory(self):
        original = builtins.__import__
        def imports(name, *args, **kwargs):
            if name == 'runpy': raise AssertionError('HELPER_EXECUTION_BEFORE_PINS')
            return original(name, *args, **kwargs)
        space = {'__name__': 'unique_import', '__file__': str(PATH)}
        with patch.object(builtins, '__import__', side_effect=imports): exec(compile(PATH.read_bytes(), str(PATH), 'exec'), space)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result: space['main'](['--help'])
            self.assertEqual(result.exception.code, 0)
            with self.assertRaises(SystemExit) as result: space['main']([])
            self.assertEqual(result.exception.code, 2)
    def test_packet_and_collector_drift_reject_before_any_process(self):
        original = Path.read_bytes
        for selected in (M['PACKET'] / self.packet['races'][0]['observer_sql'], ROOT / M['COLLECTOR']):
            before = len(self.engine.calls)
            with patch.object(Path, 'read_bytes', lambda path: CANARY.encode() if path == selected else original(path)):
                with self.assertRaises(M['HeldFailure']):
                    self.adapter.sql(selected.name) if selected.parent == M['PACKET'] else self.adapter.native_same()
            self.assertEqual(len(self.engine.calls), before); self.safe()
    def test_packet_and_collector_execute_same_verified_read(self):
        original = Path.read_bytes; calls = {}
        def once(path):
            calls[path] = calls.get(path, 0) + 1
            if calls[path] > 1 and path in (ROOT / M['COLLECTOR'], M['PACKET'] / 'commit.sql'): raise AssertionError('SECOND_READ')
            return original(path)
        with patch.object(Path, 'read_bytes', once): self.assertEqual(self.adapter.sql('commit.sql'), 'COMMIT;\n'); self.adapter.native_same()
        self.assertEqual(calls[ROOT / M['COLLECTOR']], 1); self.assertEqual(calls[M['PACKET'] / 'commit.sql'], 1)
    def test_no_actual_wait_never_qualifies_and_deadline_bounds_subprocess(self):
        self.engine.mode = 'no-wait'; result = self.race()
        self.assertEqual(result['failure']['code'], 'CONCURRENT_WAIT_UNPROVEN'); self.assertLessEqual(self.engine.barrier_calls, 40)
        self.assertEqual(result['partial_counts']['customers'], 0); self.safe()
    def test_unknown_backend_closure_suppresses_state_observers(self):
        self.engine.mode = 'backend-present'; result = self.race()
        self.assertEqual(result['failure']['code'], 'OPERATION_CLOSURE_UNCONFIRMED'); self.assertEqual(self.engine.observer_calls, 0)
        self.assertNotIn('partial_counts', result); self.safe()
    def full_plan(self):
        directory = Path(self.temporary)
        comparison = {'format': 'workinants.catalog-comparison.v1', 'status': 'PASS', 'source_expected_sha256': M['EXPECTED_NATIVE'], 'native_snapshot_sha256': M['digest'](self.native), 'check_counts': {'PASS': 100}, 'findings': []}
        assets = {}
        for name, value in (('native_snapshot', self.native), ('native_comparison', comparison)):
            raw = json.dumps(value).encode(); path = directory / (name + '.json'); path.write_bytes(raw); assets[name] = {'path': str(path), 'sha256': M['sha'](raw)}
        plan = {**self.plan, **assets, 'schema': 'workinants.unique-control-run.v1', 'scope': 'FIVE_FINITE_UNIQUE_SQL_STORAGE_RACES_ONLY', 'reviewed_packet_sha256': M['FIXTURES_SHA'],
                'reviewed_content_sha256': M['CONTENT_SHA'], 'race_names': list(M['NAMES']), 'target_manifest': {'run_id': RUN, 'source': {'integrated_sql_sha256': self.packet['source_files_sha256'][M['APPLICATION']]}}}
        attestation = {'schema': 'workinants.unique-native-attestation.v1', 'run_id': RUN, 'container_id': CID, 'source_commit': plan['source_commit'], 'source_tree': plan['source_tree'], 'packet_sha256': plan['packet_sha256'],
                       'collector_sha256': plan['source_modules_sha256'][M['COLLECTOR']], 'source_expected_sha256': M['EXPECTED_NATIVE'], 'native_snapshot_sha256': M['digest'](self.native),
                       'native_comparison_file_sha256': assets['native_comparison']['sha256'], 'original_grantor_finalized': True, 'operation_backends_absent': True, 'comparison_status': 'PASS'}
        raw = json.dumps(attestation).encode(); path = directory / 'attestation.json'; path.write_bytes(raw); plan['native_attestation'] = {'path': str(path), 'sha256': M['sha'](raw)}
        return plan
    def test_complete_modules_packet_sources_and_native_assets_prehashed_before_helpers(self):
        plan = self.full_plan(); original = Path.read_bytes
        selection = [ROOT / path for path in M['MODULES']] + [M['PACKET'] / 'fixtures.json', M['PACKET'] / 'commit.sql', ROOT / M['APPLICATION'], Path(plan['native_comparison']['path'])]
        for selected in selection:
            with self.subTest(path=str(selected)), patch.object(Path, 'read_bytes', lambda path: CANARY.encode() if path == selected else original(path)), patch.dict(M['load_inputs'].__globals__, {'compile_cached': lambda *args: self.fail('HELPER_BEFORE_PINS')}):
                with self.assertRaises(M['HeldFailure']): M['load_inputs'](plan)
        self.assertEqual(self.engine.calls, [])
    def test_same_run_cid_source_native_attestation_required_before_helper_execution(self):
        for field, wrong in (('run_id', '42f9a7cc-203c-41bb-a3b8-03706de2e74a'), ('container_id', 'f' * 64), ('source_commit', 'e' * 40), ('original_grantor_finalized', False)):
            plan = self.full_plan(); path = Path(plan['native_attestation']['path']); value = json.loads(path.read_bytes()); value[field] = wrong; raw = json.dumps(value).encode(); path.write_bytes(raw); plan['native_attestation']['sha256'] = M['sha'](raw)
            with self.subTest(field=field), patch.dict(M['load_inputs'].__globals__, {'compile_cached': lambda *args: self.fail('HELPER_BEFORE_ATTESTATION')}):
                with self.assertRaises(M['HeldFailure']) as error: M['load_inputs'](plan)
                self.assertEqual(error.exception.code, 'SAME_RUN_CID_NATIVE_ATTESTATION_REQUIRED')
    def test_same_verified_native_asset_bytes_are_parsed_without_second_read(self):
        plan = self.full_plan(); counts = {}; original = Path.read_bytes
        selected = {Path(plan[k]['path']) for k in ('native_snapshot', 'native_comparison', 'native_attestation')}
        def once(path):
            if path in selected:
                counts[path] = counts.get(path, 0) + 1
                if counts[path] > 1: raise AssertionError('ASSET_SECOND_READ')
            return original(path)
        compile_calls = []
        fake = {'SOURCE_MODULES': self.ctx['SOURCE_MODULES'], 'load_helpers': lambda blobs: compile_calls.append(set(blobs)), 'HOST': {'validate_manifest': lambda target: target}}
        with patch.object(Path, 'read_bytes', once), patch.dict(M['load_inputs'].__globals__, {'compile_cached': lambda path, raw: fake if path == M['CTX_PATH'] else P}):
            packet, native, target, ctx, protocol = M['load_inputs'](plan)
        self.assertEqual(packet, self.packet); self.assertEqual(native, self.native); self.assertEqual(len(compile_calls), 1); self.assertTrue(all(counts[path] == 1 for path in selected))
    def test_canonical_diagnostic_source_constructor_checks_same_bytes_before_sessions(self):
        original = Path.read_bytes
        with patch.object(Path, 'read_bytes', lambda path: CANARY.encode() if path == ROOT / M['APPLICATION'] else original(path)):
            with self.assertRaises(self.ctx['HeldFailure']): M['Adapter'](self.plan, self.packet, self.native, {}, self.ctx, P, self.evidence)
        self.assertEqual(self.engine.calls, [])
    def test_main_unexpected_failure_persists_safe_current_stage_and_stops(self):
        plan = self.full_plan(); path = Path(self.temporary) / 'plan.json'; path.write_text(json.dumps(plan)); directory = Path(self.temporary) / 'main-evidence'
        fake = SimpleNamespace(run=lambda: (_ for _ in ()).throw(RuntimeError(CANARY)))
        with patch.dict(M['main'].__globals__, {'load_inputs': lambda value: (self.packet, self.native, {}, self.ctx, P), 'Adapter': lambda *args: fake}):
            result = M['main'](['--execute-reviewed-unique-controls', '--reviewed-run-plan', str(path), '--evidence-directory', str(directory)])
        value = json.loads((directory / 'unique-control-results.json').read_bytes())
        self.assertEqual(result, 2); self.assertEqual(value['status'], 'STOPPED_RETAINED_FOR_CONTROLLED_CLEANUP'); self.assertTrue(value['subsequent_cases_stopped'])
        self.assertEqual(value['failure'], {'code': 'VERIFIED_TRANSPORT_OR_HELPER_REFUSED', 'stage': 'VERIFY_REVIEWED_INPUTS'}); self.assertNotIn(CANARY, json.dumps(value)); self.assertEqual(self.engine.calls, [])
    def test_actual_emitted_session_issuer_wait_and_observer_sql_parses(self):
        from pglast import parse_sql
        result = self.race(); self.assertEqual(result['status'], 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION')
        for source in ('pg_blocking_pids', 'source_xid_matches', "RETURNING pg_catalog.jsonb_build_object('created_at',created_at)", 'all_immutable_fields_equal'):
            self.assertTrue(any(source in statement for statement in self.engine.statements))
        for statement in self.engine.statements: self.assertTrue(parse_sql(statement))
        self.safe()


if __name__ == '__main__': unittest.main(verbosity=2)
