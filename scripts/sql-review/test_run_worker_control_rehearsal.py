"""Environment-free orchestration/transport mocks; ALL processes are refused or mocked."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import queue
import re
import runpy
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pglast import ast, parse_sql

ROOT = Path(__file__).resolve().parents[2]
M = runpy.run_path(str(ROOT / 'scripts/sql-review/run-worker-control-rehearsal.py'))['main'].__globals__
PACKET = json.loads((M['PACKET'] / 'fixtures.json').read_text(encoding='utf8'))
APPLICATION = (ROOT / 'review-output/foundation-application.review.sql').read_text(encoding='utf8')
FIRST = runpy.run_path(str(ROOT / M['API_PATH']))
LOCAL_FIXTURE = runpy.run_path(str(ROOT / 'scripts/check-local-f0-migrate.py'))['fixture']
CID = 'b' * 64
CANARY = 'SECRET_PASSWORD_HANDLE_SQL_DO_NOT_RETAIN'


def binder_error(state='42501', message='invalid, stale or unsupported context', delta=0):
    body = re.search(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\)\s+RETURNS\b[^;]*?\bAS\s+(\$[a-z_0-9]*\$)(.*?)\1;', APPLICATION, re.S)[2]
    line = next(index for index, text in enumerate(body.split('\n'), 1) if "RAISE EXCEPTION 'invalid, stale or unsupported context'" in text)
    return 'ERROR:  ' + state + ': ' + message + '\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line ' + str(line + delta) + ' at RAISE\nDETAIL: ' + CANARY + '\n'


def literal(value):
    if isinstance(value, ast.A_Const):
        if value.isnull: return None
        if isinstance(value.val, ast.String): return value.val.sval
        if isinstance(value.val, ast.Integer): return value.val.ival
    if isinstance(value, ast.TypeCast): return literal(value.arg)
    if isinstance(value, ast.A_ArrayExpr): return [literal(item) for item in value.elements]
    return '<runtime expression>'


def inserted(sql, table):
    item = next(row.stmt for row in parse_sql(sql) if isinstance(row.stmt, ast.InsertStmt) and row.stmt.relation.relname == table)
    return dict(zip([column.name for column in item.cols], [literal(value) for value in item.selectStmt.valuesLists[0]]))


class FakeSession:
    def __init__(self, world, role, container, api, raw):
        self.world, self.role, self.container, self.raw = world, role, container, raw
        self.closed, self.backend, self.bound, self.lease, self.code = False, None, None, None, None
        self.process = SimpleNamespace(poll=lambda: self.code)
        world.sessions.append(self); world.events.append(('open', role))

    def capture(self):
        self.backend = {'login': self.role, 'current_user': self.role, 'database': M['DATABASE'], 'isolation': 'read committed',
            'pid': str(1000 + len(self.world.sessions)), 'xid': str(5000 + len(self.world.sessions)), 'started': '2026-11-17 00:00:00+00'}
        self.world.events.append(('capture', self.role, self.backend['pid']))
        return self.backend

    def call(self, sql):
        if 'bind_request_context' in sql:
            grant = self.world.grants[self.backend['pid']]
            self.assert_issuer_closed(grant)
            self.bound = grant
            self.world.events.append(('bind', self.role, self.backend['pid']))
            valid = grant['service_principal'] is None or (grant['security_generation'] == self.world.generation and not self.world.revoked)
            if not valid:
                self.code = 3
                if self.world.mode == 'unrelated-42501': return [], False, binder_error(message=CANARY)
                if self.world.mode == 'unrelated-P0001': return [], False, binder_error(state='P0001')
                if self.world.mode.startswith('binder-exit-'):
                    self.code = int(self.world.mode.removeprefix('binder-exit-'))
                if self.world.mode == 'binder-extra-malformed': return [], False, binder_error() + 'ERROR: malformed ' + CANARY + '\n'
                if self.world.mode == 'binder-osc': return [], False, binder_error() + '\x1b]0;' + CANARY + '\x07'
                if self.world.mode == 'binder-bare-cr': return [], False, binder_error() + '\r' + CANARY
                return [], False, binder_error()
            return [], True, ''
        if sql.startswith('SET LOCAL wa.lease_secret='):
            self.lease = re.search("='([0-9a-f]{64})'", sql)[1]
            return [], True, ''
        raise AssertionError('Unmodeled interactive SQL')

    def assert_issuer_closed(self, grant):
        assert grant['_issuer'].closed, 'consumer bound before actual issuer closure'
        assert grant['backend_pid'] == int(self.backend['pid']) and grant['transaction_id'] == self.backend['xid']

    def finish(self, sql):
        assert sql.rstrip().endswith(('COMMIT;', 'ROLLBACK;'))
        self.world.events.append(('finish', self.role, self.backend['pid']))
        if 'INSERT INTO platform.database_action_grant' in sql:
            if self.world.mode == 'issuer-failure' and self.world.scheduled: raise RuntimeError(CANARY)
            grant = inserted(sql, 'database_action_grant'); grant['_issuer'] = self
            assert grant['database_login_role'] in ('wa_app_runtime', 'wa_worker')
            assert len(grant['allowed_fields']) == len(set(grant['allowed_fields']))
            self.world.grants[str(grant['backend_pid'])] = grant
            self.world.events.append(('issuer-commit', str(grant['backend_pid'])))
            result = (0, [], True, '')
        elif 'SET revoked_at=clock_timestamp()' in sql:
            assert self.role == 'wa_context_issuer'
            self.world.grant_revoked = True
            result = (0, [json.dumps({'revoked': 1})], True, '')
        elif 'DISABLE TRIGGER owner_commit' in sql:
            assert self.role == 'postgres' and 'TRIGGER USER' not in sql
            self.world.seeded = True
            if self.world.mode == 'setup-failure': raise RuntimeError(CANARY)
            result = (0, [], True, '')
        elif 'identity_service_receipt' in sql:
            assert self.role == 'wa_identity_service_authority'
            row = inserted(sql, 'identity_service_receipt')
            assert row['security_generation'] == (0 if row['transition'] == 'bootstrap' else self.world.generation + 1)
            self.world.generation = row['security_generation']; self.world.revoked = row['transition'] == 'revoke'
            self.world.transitions.append(row['transition'])
            result = (0, [], True, '')
        elif 'INSERT INTO app.customer_profiles' in sql:
            assert self.role == 'wa_app_runtime' and self.bound and self.world.seeded
            self.world.source_created = True; self.world.source_session = self
            result = (0, ['WA_CUSTOMER_CONTROL_READY_TO_COMMIT'], True, '')
        elif 'WA_WORKER_SCHEDULE_READY' in sql:
            assert self.role == 'wa_app_runtime' and self.bound['action'] == 'runtime.schedule_work.v1'
            self.world.scheduled = True
            result = (0, ['WA_WORKER_SCHEDULE_READY'], True, '')
        elif 'WA_WORKER_CLAIM_READY' in sql:
            assert self.role == 'wa_worker' and self.bound['action'] == 'runtime.claim_work.v1' and self.lease
            self.world.claimed = True; self.world.lease = self.lease
            result = (0, ['WA_WORKER_CLAIM_READY'], True, '')
        elif 'WA_WORKER_CONSTRAINTS_CHECKED' in sql:
            assert self.role == 'wa_worker' and self.lease == self.world.lease and self.bound['action'] == 'assignDefaultFreeTrack.v1'
            assert sql.index('worker_evidence_source_matches') < sql.index('SET CONSTRAINTS ALL IMMEDIATE;')
            self.world.worker_done = True
            values = [json.dumps({'model': model, 'exact_reverse': True, 'wrong_xid': False}) for model in M['MODELS']]
            if self.world.mode == 'wrong-probe': values[0] = json.dumps({'model': 'TrackSubscription', 'exact_reverse': False, 'wrong_xid': False})
            markers = ['WA_WORKER_EFFECT_LINKED', 'WA_WORKER_GROUP_STAGED', 'WA_WORKER_CONSTRAINTS_CHECKED']
            if self.world.mode == 'missing-marker': markers.pop()
            result = (0, markers + values, True, '')
        elif 'visible_exact_work' in sql:
            assert self.role == 'wa_worker' and self.bound and self.bound['source_generation'] == 1
            visible = self.bound['security_generation'] == self.world.generation and not self.world.revoked and not self.world.grant_revoked
            if self.world.mode == 'stale-readable' and self.bound['security_generation'] != self.world.generation: visible = True
            result = (0, [json.dumps({'visible_exact_work': int(visible)})], True, '')
        else: raise AssertionError('Unmodeled packet SQL')
        self.code = result[0]
        return result

    def close(self):
        self.world.events.append(('close', self.role, self.backend['pid']))
        self.closed = True
        if self.world.mode == 'backend-live' and self.world.claimed and not self.world.worker_done and self.role == 'wa_worker':
            raise M['HeldFailure']('OPERATION_BACKEND_STILL_LIVE')


class World:
    def __init__(self, mode='normal'):
        self.mode, self.events, self.sessions, self.grants, self.transitions = mode, [], [], {}, []
        self.seeded = self.source_created = self.scheduled = self.claimed = self.worker_done = self.revoked = self.grant_revoked = False
        self.source_session, self.generation, self.counter, self.secrets = None, -1, 0, []
        self.target, _, _, _, self.context, self.container, self.volume = LOCAL_FIXTURE()
        self.target['source']['integrated_sql_sha256'] = PACKET['source_files_sha256']['review-output/foundation-application.review.sql']
        self.container['Id'] = CID
        self.image = {'Id': self.container['Image'], 'Os': 'linux', 'Architecture': 'amd64', 'RepoDigests': [self.target['target']['image']]}
        self.native = {'format': 'workinants.native-catalog.v1', 'server_version_num': 170011, 'read_only': True, 'collected_as': 'postgres', 'collector_is_superuser': True}

    def token_hex(self, size):
        self.counter += 1; value = format(self.counter, '0' + str(2 * size) + 'x'); self.secrets.append(value); return value

    def session(self, role, container, api, raw):
        assert container == CID
        return FakeSession(self, role, container, api, raw)

    def check_output(self, args, **kwargs):
        assert args[:3] == ['docker', '--context', 'desktop-linux']
        suffix = args[3:]
        if suffix == ['context', 'inspect', 'desktop-linux']: value = self.context
        elif suffix == ['inspect', CID]: value = self.container
        elif suffix == ['volume', 'inspect', self.volume['Name']]: value = self.volume
        elif suffix == ['image', 'inspect', self.container['Image']]: value = self.image
        else: raise AssertionError('Unmodeled metadata boundary')
        if self.mode == 'wrong-container' and suffix == ['inspect', CID]: value = {**value, 'Id': 'c' * 64}
        return json.dumps([value])

    def run(self, args, *, input, **kwargs):
        assert args[:5] == ['docker', '--context', 'desktop-linux', 'exec', '-i']
        assert args[args.index('psql') - 1] == CID and args[args.index('-h') + 1] == '127.0.0.1'
        role = args[args.index('-U') + 1]; text = input
        if 'PGPASSWORD' in args:
            assert 'PGPASSWORD=' not in ' '.join(args)
            return subprocess.CompletedProcess(args, 2, '', 'FATAL:  password authentication failed for user "' + role + '"\n')
        if 'pg_hba_file_rules' in text:
            value = [{'rule_number': n, 'type': 'host', 'database': ['all'], 'user_name': ['all'], 'address': address, 'netmask': mask, 'auth_method': 'scram-sha-256', 'error': None}
                for n, address, mask in ((1, '127.0.0.1', '255.255.255.255'), (2, '::1', 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'))]
        elif 'pg_authid' in text: value = dict.fromkeys(('postgres', *FIRST['ROLES']), True)
        elif 'system_user' in text:
            value = {'login': role, 'auth': 'scram-sha-256:' + role, 'database': M['DATABASE'],
                'client': '127.0.0.1' if 'host(inet_client_addr())' in text else '127.0.0.1/32',
                'server': '127.0.0.1' if 'host(inet_server_addr())' in text else '127.0.0.1/32'}
        elif text == (ROOT / M['COLLECTOR']).read_text(encoding='utf8'): value = self.native
        elif 'pg_auth_members' in text: return subprocess.CompletedProcess(args, 0, '0', '')
        elif 'has_schema_privilege' in text or text.startswith('SELECT current_setting'): return subprocess.CompletedProcess(args, 0, 't', '')
        elif text.startswith('SELECT NOT EXISTS'):
            return subprocess.CompletedProcess(args, 0, 'f' if self.mode == 'namespace-conflict' else 't', '')
        elif 'owner_guards_reenabled' in text:
            value = {'owner_guards_reenabled': not (self.mode == 'guards-disabled' and self.seeded), 'no_project_user_trigger_disabled': True}
        elif 'catalog-usage' in text: raise AssertionError('Unexpected filename as SQL')
        elif 'jsonb_agg(to_jsonb(x)' in text:
            value = {table: {'count': 1 if 'usage' not in table else 0, 'sha256': 'd' * 64}
                for table in ('app.track_plans', 'app.track_entitlement_definitions', 'app.track_plan_entitlements', 'app.track_usage_events', 'app.track_usage_counters', 'app.track_usage_reservation')}
        elif 'source_uses_captured_transaction' in text: value = {'source_uses_captured_transaction': True}
        elif 'worker_uses_captured_transaction' in text: value = {'worker_uses_captured_transaction': True}
        elif 'exact_work_state' in text: value = {'exact_work_state': True}
        elif 'service_rows' in text:
            value = {'service_rows': 1, 'generation': self.generation, 'revoked': self.revoked, 'exact_receipt_link': True}
        elif text == (M['PACKET'] / 'source-customer-observe.sql').read_text(encoding='utf8'):
            assert self.source_session.closed
            value = deepcopy(PACKET['source_customer']['observer_expected']); value['track_enrollments'] = int(self.worker_done)
        elif text == (M['PACKET'] / 'enroll-observe.sql').read_text(encoding='utf8'):
            assert self.worker_done and all(session.closed for session in self.sessions)
            value = deepcopy(PACKET['positive_observer_expected'])
            if self.mode == 'partial-state': value['evidence_count'] = 2
        else: raise AssertionError('Unmodeled database observation: ' + text[:70])
        return subprocess.CompletedProcess(args, 0, json.dumps(value), '')


class QueueStream:
    def __init__(self): self.queue = queue.Queue()
    def readline(self, size=None): return self.queue.get(timeout=5)
    def read(self, size=None): return self.queue.get(timeout=5)


class PipeProcess:
    """Real Session transport mock, separate from the behavioral FSM above."""
    def __init__(self, args, **kwargs):
        assert args[args.index('psql') - 1] == CID
        self.role, self.writes, self.returncode = args[args.index('-U') + 1], [], None
        self.stdout, self.stderr = QueueStream(), QueueStream()
        self.stdin = SimpleNamespace(write=self.write, flush=lambda: None, close=self.close_input, closed=False)
    def write(self, text):
        self.writes.append(text)
        if M['TUPLE'] in text:
            value = {'login': self.role, 'current_user': self.role, 'database': M['DATABASE'], 'isolation': 'read committed',
                'pid': '12345', 'xid': '98765', 'started': '2026-11-17 00:00:00+00'}
            self.stdout.queue.put(M['TUPLE'] + json.dumps(value) + '\n')
        elif '\\q' in text: self.end()
        else:
            token = re.search(r"SELECT '(WA_WORKER_COORDINATOR_ACK\|[0-9a-f]{32})';", text)[1]
            self.stdout.queue.put(token + '\n')
    def close_input(self): self.stdin.closed = True
    def end(self):
        if self.returncode is None: self.returncode = 0; self.stdout.queue.put(''); self.stderr.queue.put('')
    def poll(self): return self.returncode
    def wait(self, timeout=None): return self.returncode
    def terminate(self): self.end()
    def kill(self): self.end()


class WorkerCoordinatorTests(unittest.TestCase):
    def setUp(self):
        for name in ('run', 'check_output', 'Popen'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN')); guard.start(); self.addCleanup(guard.stop)

    def exercise(self, mode='normal'):
        world = World(mode)
        with tempfile.TemporaryDirectory(prefix='worker-coordinator-offline-', dir=M['TASK']) as temp:
            directory = Path(temp); self.assertTrue(directory.resolve().is_relative_to(M['TASK']))
            snapshot, report = directory / 'native.json', directory / 'report.json'
            snapshot.write_text(json.dumps(world.native), encoding='utf8')
            report.write_text(json.dumps({'format': 'workinants.catalog-comparison.v1', 'status': 'PASS', 'native_snapshot_sha256': M['digest'](world.native),
                'source_expected_sha256': M['EXPECTED_CATALOG_SOURCE'], 'check_counts': {'PASS': 1}, 'findings': []}), encoding='utf8')
            plan = {'schema': 'workinants.worker-control-run.v1', 'scope': 'REVIEWED_LOCAL_WORKER_SQL_SUBSET_ONLY',
                'reviewed_packet_sha256': M['PACKET_SHA256'], 'reviewed_content_sha256': M['CONTENT_SHA256'],
                'source_modules_sha256': {name: M['sha']((ROOT / name).read_bytes()) for name in M['SOURCE_MODULES']},
                'target_manifest': world.target, 'immutable_container_id': CID,
                'native_snapshot': {'path': str(snapshot), 'sha256': M['sha'](snapshot.read_bytes())},
                'native_comparison': {'path': str(report), 'sha256': M['sha'](report.read_bytes())}, 'scenario_names': list(M['NAMES'])}
            if mode == 'source-pin-drift': plan['source_modules_sha256'][M['API_PATH']] = '0' * 64
            path = directory / 'plan.json'; path.write_text(json.dumps(plan), encoding='utf8')
            output = directory / 'evidence'
            with (patch.object(subprocess, 'run', side_effect=world.run), patch.object(subprocess, 'check_output', side_effect=world.check_output),
                 patch.dict(M, Session=world.session), patch.object(M['secrets'], 'token_hex', side_effect=world.token_hex)):
                code = M['main'](['--execute-reviewed-worker-controls', '--run-plan', str(path), '--evidence-directory', str(output)])
            data = json.loads((output / 'worker-control-results.json').read_text(encoding='utf8'))
            retained = json.dumps(data)
            self.assertNotIn(CANARY, retained)
            for value in world.secrets: self.assertNotIn(value, retained)
            for value in ('backend_start', 'transaction_id', 'INSERT INTO', 'PGPASSWORD', 'raw_stderr'): self.assertNotIn(value, retained)
            return code, data, world

    def test_dormant_help_and_missing_execute_flag_never_open_process(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as found: M['main'](['--help'])
            self.assertEqual(found.exception.code, 0)
            with self.assertRaises(SystemExit): M['main']([])

    def test_import_and_help_execute_no_helper_chain(self):
        path = ROOT / 'scripts/sql-review/run-worker-control-rehearsal.py'
        namespace = {'__file__': str(path), '__name__': 'worker_import_offline'}
        with patch.object(runpy, 'run_path', side_effect=AssertionError('UNVERIFIED_HELPER_EXECUTION')):
            exec(compile(path.read_text(encoding='utf8'), str(path), 'exec'), namespace)
            with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as found: namespace['main'](['--help'])
            self.assertEqual(found.exception.code, 0)

    def test_full_finite_fsm_preserves_boundaries_and_blocked_statuses(self):
        code, data, world = self.exercise()
        self.assertEqual(code, 0, data.get('failure'))
        self.assertEqual(world.transitions, ['bootstrap', 'rotate', 'revoke', 'recover'])
        self.assertTrue(data['cleanup_required'])
        self.assertTrue(all(row['status'] == 'NOT_RUN' for row in data['selected_controls'] + data['proposals'] + data['unprepared_vectors']))
        self.assertEqual(len([row for row in data['operations'] if row['name'] == 'worker-enroll']), 1)
        self.assertTrue(all(row['operation_closed'] for row in data['operations']))
        self.assertTrue(any(row['component'] == 'direct-source-snapshot-controls' and row['status'] == 'PASS_THREE_REVERSE_BRANCHES_ONLY' for row in data['results']))

    def test_every_grant_commits_and_issuer_closes_before_consumer_bind(self):
        code, data, world = self.exercise()
        self.assertEqual(code, 0)
        for index, event in enumerate(world.events):
            if event[0] != 'bind': continue
            commit = world.events.index(('issuer-commit', event[2]))
            issuer = world.grants[event[2]]['_issuer']
            closure = world.events.index(('close', 'wa_context_issuer', issuer.backend['pid']))
            self.assertLess(commit, closure); self.assertLess(closure, index)

    def test_wrong_resource_or_existing_namespace_stops_before_setup(self):
        for mode in ('wrong-container', 'namespace-conflict'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertFalse(world.seeded); self.assertFalse(world.sessions)

    def test_source_drift_records_safe_failure_before_any_runtime(self):
        code, data, world = self.exercise('source-pin-drift')
        self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'COORDINATOR_SOURCE_DRIFT')
        self.assertEqual(data['failure']['stage'], 'VERIFY_REVIEWED_INPUTS')
        self.assertFalse(world.sessions)

    def test_unexpected_partial_state_missing_marker_or_probe_stops_later_behavior(self):
        for mode in ('partial-state', 'missing-marker', 'wrong-probe'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertTrue(data['subsequent_cases_stopped'])
            self.assertEqual(world.transitions, ['bootstrap'])
            self.assertTrue(any(row['component'] == 'restricted-Customer-source-creation' for row in data['results']))
            if mode == 'wrong-probe':
                operation = next(row for row in data['operations'] if row['name'] == 'worker-enroll')
                self.assertFalse(operation['output_comparisons']['rows'][0]['comparisons']['exact_reverse'])
                self.assertIs(operation['output_comparisons']['rows'][0]['values']['exact_reverse'], False)

    def test_unrelated_42501_and_p0001_do_not_pass_binder_verdict(self):
        for mode in ('unrelated-42501', 'unrelated-P0001'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertEqual(world.transitions, ['bootstrap', 'rotate'])
            self.assertEqual(data['failure']['code'], 'INTENDED_BINDER_GUARD_NOT_PROVEN')

    def test_stale_disclosure_or_unconfirmed_closure_stops_and_preserves_partial(self):
        for mode in ('stale-readable', 'backend-live'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertTrue(data['subsequent_cases_stopped'])
            self.assertNotIn('revoke', world.transitions)

    def test_setup_and_issuer_failures_keep_safe_incremental_evidence(self):
        for mode in ('setup-failure', 'guards-disabled', 'issuer-failure'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertFalse(world.worker_done)
            self.assertTrue(data['operations']); self.assertTrue(data['subsequent_cases_stopped'])

    def test_source_bound_binder_diagnostic_rejects_wrong_frames_or_multiple_errors(self):
        self.assertTrue(M['binder_diagnostic'](binder_error(), APPLICATION)['matched'])
        self.assertTrue(M['binder_diagnostic'](binder_error().replace('\n', '\r\n'), APPLICATION)['matched'])
        for raw in (binder_error(delta=1), binder_error(message=CANARY), binder_error(state='P0001'), binder_error() + 'ERROR:  42501: unrelated\n',
                    binder_error() + 'ERROR: malformed ' + CANARY + '\n', binder_error() + 'ERROR malformed ' + CANARY + '\n',
                    binder_error() + '\x1b]0;' + CANARY + '\x07', binder_error() + '\r' + CANARY,
                    binder_error() + '\x7f' + CANARY, binder_error() + '\x85' + CANARY):
            result = M['binder_diagnostic'](raw, APPLICATION)
            self.assertFalse(result['matched']); self.assertNotIn(CANARY, json.dumps(result))

    def test_binder_guard_requires_psql_three_and_rejects_malformed_or_control_output(self):
        for mode in ('binder-exit-0', 'binder-exit-1', 'binder-exit-2', 'binder-exit--9',
                     'binder-extra-malformed', 'binder-osc', 'binder-bare-cr'):
            code, data, world = self.exercise(mode)
            self.assertEqual(code, 2); self.assertEqual(world.transitions, ['bootstrap', 'rotate'])
            self.assertEqual(data['failure']['code'], 'INTENDED_BINDER_GUARD_NOT_PROVEN')
            record = next(row for row in data['operations'] if row['name'] == 'currentness-old-after-rotate')
            self.assertIs(record['acknowledgement'], False)
            self.assertEqual(record['exit_code'], int(mode.removeprefix('binder-exit-')) if mode.startswith('binder-exit-') else 3)
            self.assertNotIn(CANARY, json.dumps(data))

    def test_successful_stale_binder_records_exact_exit_and_no_acknowledgement(self):
        code, data, world = self.exercise()
        self.assertEqual(code, 0)
        records = [row for row in data['operations'] if row['status'] == 'EXPECTED_BIND_REJECT']
        self.assertEqual(len(records), 3)
        self.assertTrue(all(row['exit_code'] == 3 and row['acknowledgement'] is False for row in records))

    def test_output_comparisons_are_fixed_typed_and_exclude_arbitrary_probe_values(self):
        wanted = [{'model': 'TrackSubscription', 'exact_reverse': True, 'wrong_xid': False}]
        value = M['comparison_outcomes']([{'model': CANARY, 'exact_reverse': CANARY, 'wrong_xid': 0, 'raw_secret': CANARY}], wanted)
        self.assertFalse(value['rows'][0]['fields'])
        self.assertTrue(all(item is None for item in value['rows'][0]['values'].values()))
        self.assertNotIn(CANARY, json.dumps(value))

    def test_native_pass_counts_accept_actual_comparator_counter_shape_and_reject_invalid(self):
        comparison = runpy.run_path(str(ROOT / 'scripts/sql-review/compare_native_catalog.py'))['Comparison'](
            {name: {} for name in ('tables', 'functions', 'enums', 'explicit_indexes', 'schemas', 'roles', 'policies', 'triggers')})
        comparison.record('test', 'test', 'test', 'PASS')
        actual = dict(comparison.totals)
        self.assertEqual(actual, {'PASS': 1}); self.assertTrue(M['native_pass_counts'](actual))
        for value in ({'PASS': 1, 'FAIL': 0}, {'PASS': 1, 'INCOMPLETE': 0}, {'PASS': 1, 'FAIL': 0, 'INCOMPLETE': 0}):
            self.assertTrue(M['native_pass_counts'](value))
        for value in (None, [], {}, {'FAIL': 0}, {'PASS': 0}, {'PASS': True}, {'PASS': 1.0}, {'PASS': 1, 'FAIL': False},
                      {'PASS': 1, 'FAIL': 1}, {'PASS': 1, 'INCOMPLETE': 1}, {'PASS': 1, 'INCOMPLETE': -1}, {'PASS': 1, 'OTHER': 0}):
            self.assertFalse(M['native_pass_counts'](value))

    def test_real_session_transport_uses_exact_id_and_confirms_backend_closure(self):
        processes = []
        def popen(args, **kwargs):
            result = PipeProcess(args, **kwargs); processes.append(result); return result
        api = {'psql': FIRST['psql']}
        observed = []
        def raw(role, sql):
            self.assertEqual(role, 'postgres'); self.assertIsNotNone(processes[0].poll()); observed.append(sql); return '0'
        with patch.object(subprocess, 'Popen', side_effect=popen):
            session = M['Session']('wa_worker', CID, api, raw)
            backend = session.capture(); self.assertEqual(backend['login'], 'wa_worker')
            self.assertEqual(session.finish('ROLLBACK;')[:3], (0, [], True)); session.close()
        self.assertEqual(len(processes), 1); self.assertEqual(len(observed), 1)
        self.assertIn('current_user', processes[0].writes[0])

    def test_real_session_rejects_trailing_output_after_ack_and_still_closes(self):
        processes = []
        def popen(args, **kwargs):
            result = PipeProcess(args, **kwargs)
            original = result.end
            def extra():
                if result.returncode is None: result.stdout.queue.put(CANARY + '\n')
                original()
            result.end = extra; processes.append(result); return result
        with patch.object(subprocess, 'Popen', side_effect=popen):
            session = M['Session']('wa_worker', CID, {'psql': FIRST['psql']}, lambda role, text: '0')
            session.capture()
            with self.assertRaises(M['HeldFailure']) as found: session.finish('ROLLBACK;')
            self.assertEqual(found.exception.code, 'UNEXPECTED_TRAILING_OUTPUT')
            session.close()

    def test_source_packet_and_customer_namespaces_remain_frozen_and_disjoint(self):
        self.assertEqual(M['sha']((M['PACKET'] / 'fixtures.json').read_bytes()), M['PACKET_SHA256'])
        customer = json.loads((ROOT / 'review-output/customer-control-rehearsal/fixtures.json').read_text(encoding='utf8'))
        own = set(PACKET['source_customer']['ids'].values())
        theirs = {value for case in customer['cases'] for value in case['ids'].values()}
        self.assertFalse(own & theirs)

    def read_guard_coordinator(self):
        evidence = SimpleNamespace(value={'current': {}, 'current_stage': 'READ_GUARD_TEST'}, stage=lambda name: None, save=lambda: None)
        plan = {'immutable_container_id': CID, 'source_modules_sha256': {M['COLLECTOR']: M['sha']((ROOT / M['COLLECTOR']).read_bytes())}}
        calls = []
        native = {'format': 'workinants.native-catalog.v1'}
        api = {'run': lambda role, text, container: calls.append((role, text, container)) or json.dumps(native)}
        return M['Coordinator'](plan, PACKET, native, api, {}, evidence), calls

    def test_midrun_packet_and_collector_drift_refuse_before_sql_or_session_boundary(self):
        coordinator, calls = self.read_guard_coordinator()
        original = Path.read_bytes
        for path, code, action in (
            (M['PACKET'] / 'independent-fixtures.sql', 'WORKER_SQL_PACKET_DRIFT', lambda: coordinator.trusted('DRIFT', 'independent-fixtures.sql')),
            (ROOT / M['COLLECTOR'], 'WORKER_COLLECTOR_SOURCE_DRIFT', coordinator.native)):
            def changed(candidate, target=path): return ('SELECT ' + repr(CANARY) + ';').encode() if candidate == target else original(candidate)
            with patch.object(Path, 'read_bytes', changed), patch.dict(M, Session=lambda *args: self.fail('Drift reached an operation session')):
                with self.assertRaises(M['HeldFailure']) as found: action()
            self.assertEqual(found.exception.code, code)
            self.assertFalse(calls)
            self.assertNotIn(CANARY, json.dumps(coordinator.evidence.value))

    def test_diagnostic_canonical_source_is_rehashed_at_construction_before_runtime(self):
        original = Path.read_bytes
        target = ROOT / 'review-output/foundation-application.review.sql'
        def changed(path): return ('SELECT ' + repr(CANARY) + ';').encode() if path == target else original(path)
        with patch.object(Path, 'read_bytes', changed), self.assertRaises(M['HeldFailure']) as found:
            self.read_guard_coordinator()
        self.assertEqual(found.exception.code, 'CANONICAL_DIAGNOSTIC_SOURCE_DRIFT')

    def test_sql_uses_the_exact_once_read_hashed_bytes_without_text_reopen(self):
        original = Path.read_text
        guarded = {ROOT / M['COLLECTOR'], ROOT / 'review-output/foundation-application.review.sql', M['PACKET'] / 'claim.sql'}
        def trap(path, *args, **kwargs):
            if path in guarded: raise AssertionError('UNVERIFIED_TEXT_REOPEN')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', trap):
            coordinator, calls = self.read_guard_coordinator()
            self.assertEqual(coordinator.text('claim.sql').encode(), (M['PACKET'] / 'claim.sql').read_bytes())
            coordinator.native()
        self.assertEqual(len(calls), 1)
        self.assertEqual(M['sha'](calls[0][1].encode()), coordinator.plan['source_modules_sha256'][M['COLLECTOR']])


if __name__ == '__main__': unittest.main(verbosity=2)
