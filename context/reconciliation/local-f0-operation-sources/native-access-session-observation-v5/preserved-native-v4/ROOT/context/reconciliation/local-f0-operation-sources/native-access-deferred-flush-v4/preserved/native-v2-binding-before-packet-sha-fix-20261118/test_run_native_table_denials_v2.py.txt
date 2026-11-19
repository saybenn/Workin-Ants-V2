"""Pure source checks and subprocess mocks. Every Docker/DB boundary is mocked."""
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
from types import FunctionType, SimpleNamespace
import unittest
from unittest.mock import patch
import sys

from pglast import ast, parse_sql

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/sql-review'))
import catalog_manifest
import compare_native_catalog

M = runpy.run_path(str(ROOT / 'scripts/sql-review/run-native-table-denials-v2.py'))['main'].__globals__
PACKET = json.loads((M['PACKET'] / 'packet.json').read_bytes())
EXPECTED = catalog_manifest.build_manifest()['expected']
LOCAL = runpy.run_path(str(ROOT / 'scripts/check-local-f0-migrate.py'))['fixture']
CID = 'b' * 64
RUN = '941ae300-a3eb-4807-b47b-d46902372c98'
CANARY = 'SECRET_PASSWORD_HANDLE_SQL_NOT_TO_RETAIN'


def diagnostic_native():
    """Minimal source-known catalog slice; no runtime or learned error values."""
    return {'relations': [{'object': name, 'kind': 'r'} for name in ('app.access_audit_logs', 'app.audit_events')],
            'columns': [{'table_name': 'app.access_audit_logs', 'name': 'id', 'nullable': False},
                        {'table_name': 'app.access_audit_logs', 'name': 'actor_user_id', 'nullable': True}],
            'constraints': [{'table_name': 'app.access_audit_logs', 'name': 'access_audit_logs_actor_user_id_fkey', 'kind': 'f'},
                            {'table_name': 'app.access_audit_logs', 'name': 'access_audit_logs_pkey', 'kind': 'p'},
                            {'table_name': 'app.audit_events', 'name': 'f0_null_metadata', 'kind': 'c'}],
            'functions': [{'name': 'platform_private.runtime_transition', 'object': 'platform_private.runtime_transition()',
                           'kind': 'f', 'language': 'plpgsql', 'parameters': [],
                           'body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038'}]}


def unexpected_stderr(state='23503', relation='access_audit_logs', constraint='access_audit_logs_actor_user_id_fkey', column=None):
    # Match psql VERBOSITY verbose: the message/details may contain secrets and
    # the separate structured identifier fields are the only native projection.
    text = 'psql:<stdin>:159: ERROR:  ' + state + ': ' + CANARY + '\nDETAIL:  Failing row contains (' + CANARY + ', postgresql://u:' + CANARY + '@example/db)\n'
    text += 'HINT: SELECT ' + CANARY + ';\nSCHEMA NAME:  app\nTABLE NAME:  ' + relation + '\n'
    if column is not None: text += 'COLUMN NAME:  ' + column + '\n'
    if constraint is not None: text += 'CONSTRAINT NAME:  ' + constraint + '\n'
    return text + 'LOCATION:  ExecConstraints, execMain.c:2058\n'


def diagnostic(case, gate='SCHEMA', column=None, routine=None):
    schema, relation = case['table'].split('.')
    if gate == 'SCHEMA': message = 'permission denied for schema ' + schema
    elif gate == 'TABLE': message = 'permission denied for table ' + relation
    else: message = 'permission denied for column "' + column + '" of relation "' + relation + '"'
    return 'ERROR:  42501: ' + message + '\nLOCATION:  ' + (routine or ('aclcheck_error_col' if gate == 'COLUMN' else 'aclcheck_error')) + ', aclchk.c:2841\n'


class MemoryEvidence:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=False)
        self.value = {'current_stage': 'ENTRY', 'current': {}, 'operations': [], 'native_controls': [], 'facets': [], 'authentication': [],
                      'selected_cases': [], 'database_posture': 'D', 'cleanup_required': True, 'subsequent_cases_stopped': False}
        self.saves = 0; self.completed_before_failure = None
    def save(self):
        self.saves += 1
        if self.value.get('status') == 'STOPPED': self.completed_before_failure = len(self.value['facets'])
    def stage(self, value): self.value['current_stage'] = value; self.save()


class FakeSession:
    def __init__(self, world, role, cid, api, raw):
        assert cid == CID and role in M['AUTH_ROLES']
        self.world, self.role, self.closed = world, role, False
        world.sessions.append(self); world.events.append(('open', role))
    def capture(self): self.world.events.append(('capture', self.role))
    def finish(self, text):
        world = self.world; world.events.append(('execute', self.role))
        assert 'bind_request_context' not in text and 'SET ROLE' not in text
        if 'all-native-fact-setup-triggers-restored' in text:
            assert self.role == 'postgres' and text.count('DISABLE TRIGGER') == 60
            world.seeded = True
            if world.mode == 'setup-error': return 3, [], False, world.unexpected_error or 'ERROR:  23503: ' + CANARY
            return 0, [json.dumps({'control': 'all-native-fact-setup-triggers-restored', 'all_declared_user_triggers_restored': True})], True, ''
        if "'native-control-" in text:
            assert self.role == 'postgres' and 'COMMIT;' not in text and '\nROLLBACK;' in text
            model = re.search("'native-control-([A-Za-z0-9]+)'", text)[1]
            if world.mode == 'native-invalid' or world.mode == 'native-late' and world.controls == 1:
                return 3, [], False, world.unexpected_error or 'ERROR:  23503: ' + CANARY
            world.controls += 1
            return 0, ['t'] * (text.count('AS native_update_one') + 2) + [json.dumps({'control': 'native-control-' + model, 'all_declared_user_triggers_restored': True})], True, ''
        if "'own_row'" in text:
            assert self.role == 'wa_context_issuer'
            world.issuer_seen = True
            return 0, [json.dumps({'own_row': 0 if world.mode == 'issuer-own-hidden' else 1, 'foreign_row': 0})], True, ''
        case = world.current_case(); probe = world.current_probe(case)
        assert probe['role'] == self.role
        world.restricted += 1
        if world.mode == 'unexpected-late' and world.restricted == 3: raise RuntimeError(CANARY)
        if probe['facet'].startswith('RLS_'):
            return 0, ['1' if world.mode == 'rls-readable' else '0'], True, ''
        metadata = world.privileges(case, self.role)
        gate = 'SCHEMA' if metadata['schema_usage'] is False else 'TABLE'
        errors = diagnostic(case, gate)
        if world.mode == 'trigger-42501': errors = errors.replace('LOCATION:  aclcheck_error, aclchk.c:2841', 'CONTEXT:  PL/pgSQL function platform_private.guard_x() line 1 at RAISE')
        if world.mode == 'unrelated-P0001': errors = errors.replace('42501', 'P0001')
        if world.mode == 'extra-error': errors += 'ERROR: malformed ' + CANARY + '\n'
        if world.mode == 'terminal-control': errors += '\x1b]0;' + CANARY + '\x07'
        code = 2 if world.mode == 'wrong-exit' else 3
        return code, [], False, errors
    def close(self):
        self.world.events.append(('close', self.role)); self.closed = True
        if self.world.mode == 'backend-live' and self.world.restricted:
            raise M['HeldFailure']('OPERATION_BACKEND_STILL_LIVE')


class World:
    def __init__(self, mode='normal', subset=None, unexpected_error=None):
        self.mode, self.subset, self.sessions, self.events, self.evidence = mode, subset, [], [], None
        self.unexpected_error = unexpected_error
        self.seeded = False; self.controls = self.restricted = 0; self.issuer_seen = False; self.passwords = []
        self.target, _, _, _, self.context, self.container, self.volume = LOCAL()
        self.target['run_id'] = RUN
        self.target['target']['labels']['workinants.rehearsal.run'] = RUN
        self.target['source']['integrated_sql_sha256'] = PACKET['source_inputs_sha256']['review-output/foundation-application.review.sql']
        self.container['Id'] = CID; self.container['Config']['Labels']['workinants.rehearsal.run'] = RUN; self.volume['Labels']['workinants.rehearsal.run'] = RUN
        self.image = {'Id': self.container['Image'], 'Os': 'linux', 'Architecture': 'amd64', 'RepoDigests': [self.target['target']['image']]}
        self.native = {'format': 'workinants.native-catalog.v1', 'server_version_num': 170011, 'read_only': True, 'collected_as': 'postgres', 'collector_is_superuser': True,
                       'nonowner_acl': compare_native_catalog._acl_expected(EXPECTED, 'pg_database_owner'), **diagnostic_native()}
        self.acl = {(row['kind'], row['object'], row['grantee'], row['privilege'], row.get('column')) for row in self.native['nonowner_acl']}
        setup = (M['PACKET'] / 'native-fact-setup.sql').read_text(encoding='utf8')
        self.counts = {name: len(re.findall('^INSERT INTO ' + re.escape(M['table'](name)) + r'\(', setup, re.M)) for name in sorted(PACKET['synthetic_facts']['baseline'])}
    def current_case(self): return next(case for case in PACKET['cases'] if case['id'] == self.evidence.value['current_case'])
    def current_probe(self, case):
        current = self.evidence.value['current_probe']; return next(probe for probe in case['probes'] if probe['role'] == current['role'] and probe['verb'] == current['verb'])
    def privileges(self, case, role):
        name = case['table']; schema = name.split('.')[0]; columns = sorted(EXPECTED['tables'][name]['columns'])
        def allowed(kind, privilege, column=None):
            object_ = schema if kind == 'SCHEMA' else name
            return any((kind, object_, grantee, privilege, scoped_column) in self.acl for grantee in (role, 'PUBLIC') for scoped_column in ((None,) if column is None else (None, column)))
        return {'schema_usage': allowed('SCHEMA', 'USAGE'), 'table': {verb: allowed('TABLE', verb) for verb in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')},
                'columns': {column: {verb: allowed('TABLE', verb, column) for verb in ('SELECT', 'INSERT', 'UPDATE')} for column in columns}}
    def raw(self, role, text):
        assert not any(not session.closed for session in self.sessions), 'observer before operation backend closure'
        self.events.append(('observer', role))
        if "'workinants.native-catalog.v1'" in text: return json.dumps(self.native)
        if 'exact_trigger_function_body_state_set' in text:
            return json.dumps({'expected_count': 100, 'actual_count': 100, 'exact_trigger_function_body_state_set': not (self.mode == 'guards-disabled' and self.controls)})
        if 'workinants.native-fingerprint-order.v1' in text:
            nodes = parse_sql(text)
            assert [type(n.stmt).__name__ for n in nodes] == ['TransactionStmt', 'SelectStmt', 'TransactionStmt']
            assert text.startswith('BEGIN READ ONLY;') and text.endswith('ROLLBACK;') and 'ORDER BY name COLLATE "C"' in text
            value = {'format': 'workinants.native-fingerprint-order.v1', 'server_version_num': 170011, 'collected_as': 'postgres', 'read_only': True, 'known_name_count': 42, 'c_order_matches_source': True, 'default_order_matches_source': self.mode == 'order-default-already-C'}
            if self.mode == 'order-bad-flag': value['c_order_matches_source'] = CANARY
            if self.mode == 'order-unknown-role': value['collected_as'] = CANARY
            if self.mode == 'order-extra-field': value['stderr'] = CANARY
            if self.mode == 'order-bool-count': value['known_name_count'] = True
            if self.mode == 'order-C-false': value['c_order_matches_source'] = False
            return json.dumps(value)
        if 'AS rows_sha256' in text:
            # Emulate a non-C default that ignores punctuation. The reply
            # depends on the actual SQL projection, never the desired result.
            names = sorted(self.counts) if 'ORDER BY object COLLATE "C"' in text else sorted(self.counts, key=lambda name: name.replace('.', '').replace('_', ''))
            assert names == sorted(self.counts) or 'ORDER BY object COLLATE "C"' not in text
            rows = [{'object': name, 'row_count': self.counts[name] if self.seeded else 0, 'rows_sha256': 'a' * 64} for name in names]
            if self.mode == 'fingerprint-not-list': return json.dumps({'value': CANARY})
            if self.mode == 'fingerprint-extra-key': rows[0]['unknown'] = CANARY
            if self.mode == 'fingerprint-unknown-name': rows[0]['object'] = CANARY
            if self.mode == 'fingerprint-duplicate-name': rows[0]['object'] = rows[1]['object']
            if self.mode == 'fingerprint-bool-count': rows[0]['row_count'] = True
            if self.mode == 'fingerprint-float-count': rows[0]['row_count'] = 0.0
            if self.mode == 'fingerprint-bad-digest': rows[0]['rows_sha256'] = CANARY
            if self.mode == 'fingerprint-short': rows.pop()
            if self.mode == 'fingerprint-nested-row': rows[0] = [CANARY]
            if self.mode == 'facts-changed' and self.restricted: rows[0]['rows_sha256'] = 'c' * 64
            return json.dumps(rows)
        if "current_user='postgres'" in text: return 't'
        if 'FROM pg_hba_file_rules' in text:
            return json.dumps([{'rule_number': n, 'type': 'host', 'database': ['all'], 'user_name': ['all'], 'address': addr, 'netmask': mask, 'auth_method': 'scram-sha-256', 'error': None}
                               for n, addr, mask in ((1, '127.0.0.1', '255.255.255.255'), (2, '::1', 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'))])
        if 'FROM pg_authid' in text: return json.dumps(dict.fromkeys(M['AUTH_ROLES'], True))
        if "jsonb_build_object('login',session_user" in text:
            assert 'host(inet_client_addr())' in text and 'host(inet_server_addr())' in text
            return json.dumps({'login': CANARY if self.mode == 'provider-wrong-login' and role == 'anon' else role, 'auth': 'scram-sha-256:' + role, 'database': M['DATABASE'], 'client': '127.0.0.1', 'server': '127.0.0.1'})
        if 'SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members' in text: return 't'
        if "'memberships'" in text:
            value = sorted(M['provider_flags'](), key=lambda row: row['name'])
            if self.mode == 'provider-temp': value[0]['temp'] = True
            return json.dumps(value)
        if "'own_exists'" in text: return json.dumps({'own_exists': 1, 'foreign_exists': 1})
        if "'row_count'" in text: return json.dumps({'row_count': 0 if self.mode == 'missing-existing' else 1})
        if "'schema_usage'" in text:
            case = self.current_case(); target_role = re.search(r"has_schema_privilege\('([^']+)'", text)[1]
            return json.dumps(self.privileges(case, target_role))
        raise AssertionError('Unmodeled observer boundary')
    def run(self, args, *, input, **kwargs):
        assert args[:5] == ['docker', '--context', 'desktop-linux', 'exec', '-i'] and args[args.index('psql') - 1] == CID
        role = args[args.index('-U') + 1]
        assert args[args.index('-h') + 1] == '127.0.0.1' and args[args.index('-d') + 1] == M['DATABASE']
        if 'PGPASSFILE=/dev/null' in args:
            self.passwords.append(kwargs['env']['PGPASSWORD'])
            return SimpleNamespace(returncode=2, stdout='', stderr='FATAL:  password authentication failed for user "' + role + '"\n')
        return SimpleNamespace(returncode=0, stdout=self.raw(role, input), stderr='')
    def check_output(self, args, **kwargs):
        assert args[:3] == ['docker', '--context', 'desktop-linux']; suffix = args[3:]
        if suffix == ['context', 'inspect', 'desktop-linux']: value = self.context
        elif suffix == ['inspect', CID]: value = self.container
        elif suffix == ['volume', 'inspect', self.volume['Name']]: value = self.volume
        elif suffix == ['image', 'inspect', self.container['Image']]: value = self.image
        else: raise AssertionError('Unmodeled resource boundary')
        if self.mode == 'wrong-container' and suffix == ['inspect', CID]: value = {**value, 'Id': 'd' * 64}
        return json.dumps([value])


class QueueOutput:
    def __init__(self): self.queue = queue.Queue()
    def readline(self, limit=None): return self.queue.get(timeout=3)
    def read(self, limit=None): return self.queue.get(timeout=3)


class PipeProcess:
    def __init__(self, args, **kwargs):
        assert args[:5] == ['docker', '--context', 'desktop-linux', 'exec', '-i'] and CID in args
        self.role = args[args.index('-U') + 1]; self.returncode = None; self.stdout, self.stderr = QueueOutput(), QueueOutput(); self.writes = []
        self.stdin = SimpleNamespace(write=self.write, flush=lambda: None, close=lambda: setattr(self.stdin, 'closed', True), closed=False)
    def write(self, text):
        self.writes.append(text)
        if M['TUPLE'] in text:
            self.stdout.queue.put(M['TUPLE'] + json.dumps({'login': self.role, 'current_user': self.role, 'database': M['DATABASE'], 'isolation': 'read committed', 'pid': '123', 'xid': '456', 'started': '2026-11-17 01:00:00+00', 'context_absent': True}) + '\n')
        elif '\\q' in text: self.end()
        else:
            token = re.search(r"SELECT '(WA_NATIVE_DENY_ACK\|[0-9a-f]+)';", text)[1]
            self.stdout.queue.put('0\n'); self.stdout.queue.put(token + '\n')
    def end(self):
        if self.returncode is None: self.returncode = 0; self.stdout.queue.put(''); self.stderr.queue.put('')
    def wait(self, timeout=None): return self.returncode
    def poll(self): return self.returncode
    def terminate(self): self.end()
    def kill(self): self.end()


class NativeCoordinatorTests(unittest.TestCase):
    def setUp(self):
        for name in ('run', 'Popen', 'check_output'):
            guard = patch.object(subprocess, name, side_effect=AssertionError('UNMOCKED_PROCESS_FORBIDDEN')); guard.start(); self.addCleanup(guard.stop)
    def exercise(self, mode='normal', subset=None, unexpected_error=None):
        world = World(mode, subset, unexpected_error)
        with tempfile.TemporaryDirectory(prefix='native-deny-offline-', dir=M['TASK']) as temporary:
            directory = Path(temporary)
            report = {'format': 'workinants.catalog-comparison.v1', 'status': 'PASS', 'source_expected_sha256': M['EXPECTED_SOURCE'], 'native_snapshot_sha256': M['digest'](world.native), 'check_counts': {'PASS': 1}, 'findings': []}
            proof = {'schema': 'workinants.native-deny-provider-preinstall.v1', 'run_id': RUN, 'container_id': CID, 'source_commit': 'a' * 40, 'source_tree': 'c' * 40,
                     'packet_sha256': M['PACKET_SHA'], 'application_sql_sha256': PACKET['source_inputs_sha256']['review-output/foundation-application.review.sql'], 'roles': M['provider_flags'](),
                     'all_nine_schema_usage_sentinels_before_install': True, 'canonical_install_removed_all_nine': True, 'genuine_prisma_one_applied_migration': True, 'original_grantor_finalized': True, 'local_simulation_only': True, 'hosted_parity_claimed': False}
            plan = {'schema': 'workinants.native-deny-run.v1', 'scope': 'FINITE_NATIVE_DENIAL_FACETS_ONLY', 'run_id': RUN, 'source_commit': 'a' * 40, 'source_tree': 'c' * 40,
                    'packet_sha256': M['PACKET_SHA'], 'source_modules_sha256': {name: M['sha']((ROOT / name).read_bytes()) for name in M['MODULES']},
                    'target_manifest': world.target, 'immutable_container_id': CID, 'selected_case_ids': PACKET['selected_case_ids']}
            for name, value in (('native_snapshot', world.native), ('native_comparison', report), ('provider_preinstall_proof', proof)):
                path = directory / (name + '.json'); path.write_text(json.dumps(value), encoding='utf8'); plan[name] = {'path': str(path), 'sha256': M['sha'](path.read_bytes())}
            if mode == 'source-drift': plan['source_modules_sha256'][M['API']] = '0' * 64
            if mode == 'native-incomplete':
                report['status'] = 'INCOMPLETE'; path = directory / 'native_comparison.json'; path.write_text(json.dumps(report), encoding='utf8'); plan['native_comparison']['sha256'] = M['sha'](path.read_bytes())
            path = directory / 'plan.json'; path.write_text(json.dumps(plan), encoding='utf8')
            original_coordinator = M['Coordinator']
            def coordinator(*args):
                result = original_coordinator(*args); world.evidence = result.evidence
                if subset is not None:
                    result.packet = deepcopy(result.packet); result.packet['cases'] = [case for case in result.packet['cases'] if case['model'] in subset]
                return result
            memories = []
            def evidence(output): value = MemoryEvidence(output); memories.append(value); return value
            with patch.dict(M, Session=lambda *args: FakeSession(world, *args), Coordinator=coordinator, Evidence=evidence), patch.object(subprocess, 'run', side_effect=world.run), patch.object(subprocess, 'check_output', side_effect=world.check_output):
                code = M['main'](['--execute-reviewed-native-denials', '--run-plan', str(path), '--evidence-directory', str(directory / 'evidence')])
            value = memories[0].value
            retained = json.dumps(value); self.assertFalse(CANARY in retained, 'Secret canary retained')
            for secret in world.passwords: self.assertFalse(secret in retained, 'Password retained')
            for forbidden in ('"backend_start":', '"transaction_id":', '"pid":', '"xid":', 'INSERT INTO', 'raw_stderr', 'PGPASSWORD'):
                self.assertFalse(forbidden in retained, 'Runtime handle or raw content retained: ' + forbidden)
            return code, value, world, memories[0]

    def test_full_forty_finite_facets_preserve_not_run_and_four_blocks(self):
        code, data, world, memory = self.exercise()
        self.assertEqual(code, 0, data.get('failure')); self.assertEqual(world.controls, 40); self.assertEqual(len(data['facets']), 960)
        self.assertEqual(sum(row['status'] == 'NOT_RUN' for row in data['facets']), 4)
        self.assertEqual(len(data['authentication']), 9); self.assertTrue(world.issuer_seen)
        self.assertTrue(all(row['status'] == row['source_vectors_status'] == row['allow_case_status'] == 'NOT_RUN' for row in data['selected_cases']))
        self.assertTrue(all(row['closed_before_observers'] for row in data['operations'])); self.assertGreater(memory.saves, 960)
        self.assertTrue(all(row.get('whole_case_promoted') is False for row in data['facets'] if row['status'] != 'NOT_RUN'))

    def test_actual_projection_rejects_restored_default_collation(self):
        method = M['Coordinator'].fingerprint
        original = 'SELECT jsonb_agg(to_jsonb(x) ORDER BY object COLLATE "C") FROM ('
        self.assertIn(original, method.__code__.co_consts)
        constants = tuple(c.replace('ORDER BY object COLLATE "C"', 'ORDER BY object') if type(c) is str else c for c in method.__code__.co_consts)
        mutant = FunctionType(method.__code__.replace(co_consts=constants), method.__globals__)
        with patch.object(M['Coordinator'], 'fingerprint', mutant):
            code, data, world, _ = self.exercise(subset=['ConsentLog'])
        self.assertEqual(code, 2); self.assertFalse(world.seeded); self.assertFalse(world.restricted)
        self.assertEqual(data['failure'], {'code': 'DATA_FINGERPRINT_SHAPE', 'stage': 'EMPTY_DATA_FINGERPRINT'})
        self.assertTrue(data['current']['fingerprint_checks']['known_name_set'])
        self.assertFalse(data['current']['fingerprint_checks']['source_name_order'])

    def test_corrected_projection_and_default_already_C_are_both_valid(self):
        for mode in ('normal', 'order-default-already-C'):
            code, data, world, _ = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 0, data.get('failure'))
            self.assertTrue(data['fingerprint_order_control']['c_order_matches_source'])
            self.assertEqual(data['fingerprint_order_control']['default_order_matches_source'], mode == 'order-default-already-C')

    def test_fingerprint_shape_failures_keep_only_fixed_checks_and_stop_before_setup(self):
        for suffix in ('not-list', 'extra-key', 'unknown-name', 'duplicate-name', 'bool-count', 'float-count', 'bad-digest', 'short', 'nested-row'):
            with self.subTest(suffix=suffix):
                code, data, world, _ = self.exercise('fingerprint-' + suffix, ['ConsentLog'])
                self.assertEqual(code, 2); self.assertFalse(world.seeded); self.assertFalse(world.restricted)
                self.assertEqual(data['failure'], {'code': 'DATA_FINGERPRINT_SHAPE', 'stage': 'EMPTY_DATA_FINGERPRINT'})
                checks = data['current']['fingerprint_checks']
                self.assertEqual(set(checks), {'list','exact_row_count','objects','fields','known_name_set','source_name_order','typed_bounded_counts','digest_shape'})
                self.assertTrue(all(type(v) is bool for v in checks.values())); self.assertFalse(all(checks.values()))
                self.assertNotIn('data_projection', data['current'])

    def test_order_control_shape_and_unknowns_stop_before_data_or_setup(self):
        for mode in ('order-bad-flag','order-unknown-role','order-extra-field','order-bool-count','order-C-false'):
            code, data, world, _ = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 2); self.assertFalse(world.seeded); self.assertFalse(world.restricted)
            self.assertEqual(data['failure']['stage'], 'SOURCE_NAME_COLLATION_CONTROL')
            self.assertEqual(data['failure']['code'], 'FINGERPRINT_C_ORDER_REQUIRED' if mode == 'order-C-false' else 'FINGERPRINT_ORDER_CONTROL_SHAPE')
            self.assertTrue(all(type(v) is bool for v in data['fingerprint_order_comparisons'].values()))

    def test_hash_and_object_order_are_explicit_C_in_emitted_sql(self):
        queries = []
        original = World.raw
        def capture(world, role, text):
            if 'AS rows_sha256' in text: queries.append(text)
            return original(world, role, text)
        with patch.object(World, 'raw', capture):
            code, data, _, _ = self.exercise(subset=['ConsentLog'])
        self.assertEqual(code, 0, data.get('failure')); self.assertTrue(queries)
        for text in set(queries):
            self.assertEqual(text.count('COLLATE "C"'),43)
            self.assertIn('ORDER BY object COLLATE "C"', text)
            self.assertEqual(len(parse_sql(text)),1)

    def test_native_state_routine_extra_errors_controls_and_exit_two_reject(self):
        for mode in ('trigger-42501', 'unrelated-P0001', 'extra-error', 'terminal-control', 'wrong-exit'):
            with self.subTest(mode=mode):
                code, data, world, memory = self.exercise(mode, ['ConsentLog'])
                self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'INTENDED_NATIVE_GATE_NOT_PROVEN')
                self.assertEqual(world.restricted, 1); self.assertEqual(data['facets'], []); self.assertTrue(data['subsequent_cases_stopped'])

    def test_partial_evidence_persists_and_later_probes_stop_on_unexpected(self):
        code, data, world, memory = self.exercise('unexpected-late', ['ConsentLog', 'ConsentContentRevision'])
        self.assertEqual(code, 2); self.assertEqual(world.restricted, 3); self.assertEqual(len(data['facets']), 2)
        self.assertEqual(memory.completed_before_failure, 2); self.assertEqual(world.controls, 1)
        self.assertEqual(data['failure']['code'], 'UNEXPECTED_EXCEPTION')

    def test_native_invalid_or_restoration_failure_never_reaches_restricted_probe(self):
        for mode in ('native-invalid', 'guards-disabled'):
            code, data, world, memory = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 2); self.assertEqual(world.restricted, 0); self.assertTrue(data['operations'][-1]['closed_before_observers'])

    def test_closure_existing_row_and_mutation_watch_fail_closed(self):
        for mode in ('backend-live', 'missing-existing', 'facts-changed', 'rls-readable'):
            code, data, world, memory = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 2); self.assertTrue(data['subsequent_cases_stopped'])
            self.assertLess(world.restricted, 24)

    def test_provider_identity_and_temp_boundary_fail_before_setup(self):
        for mode in ('provider-wrong-login', 'provider-temp', 'wrong-container'):
            code, data, world, memory = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 2); self.assertFalse(world.seeded); self.assertEqual(world.restricted, 0)

    def test_source_and_native_pass_checked_before_helpers_or_processes(self):
        for mode in ('source-drift', 'native-incomplete'):
            with patch.dict(M, execute_verified_helpers=lambda _: (_ for _ in ()).throw(AssertionError('UNVERIFIED_HELPER'))):
                code, data, world, memory = self.exercise(mode, ['ConsentLog'])
            self.assertEqual(code, 2); self.assertFalse(world.events); self.assertFalse(world.sessions)
            self.assertIn(data['failure']['code'], ('HELPER_SOURCE_DRIFT', 'FULL_NATIVE_PARITY_PASS_REQUIRED'))

    def test_issuer_own_visibility_is_mandatory_positive_control(self):
        code, data, world, memory = self.exercise('issuer-own-hidden', ['DatabaseActionGrant'])
        self.assertEqual(code, 2); self.assertTrue(world.issuer_seen); self.assertEqual(world.restricted, 0)

    def test_native_diagnostics_bind_observed_schema_table_and_any_missing_referenced_column(self):
        case = PACKET['cases'][0]; metadata = {'schema_usage': False, 'required_permission_missing': True, 'missing_referenced_columns': ['id', 'user_id']}
        result = M['native_diagnostic'](diagnostic(case), case, metadata)
        self.assertTrue(result['matched']); self.assertEqual(result['observed_gate'], 'SCHEMA')
        metadata['schema_usage'] = True
        self.assertTrue(M['native_diagnostic'](diagnostic(case, 'TABLE'), case, metadata)['matched'])
        result = M['native_diagnostic'](diagnostic(case, 'COLUMN', 'user_id'), case, metadata)
        self.assertTrue(result['matched']); self.assertEqual(result['native_column'], 'user_id'); self.assertIs(result['selected_column_isolation_claimed'], False)
        self.assertFalse(M['native_diagnostic'](diagnostic(case, 'COLUMN', 'created_at'), case, metadata)['matched'])
        metadata['required_permission_missing'] = False
        self.assertFalse(M['native_diagnostic'](diagnostic(case, 'TABLE'), case, metadata)['matched'])

    def test_diagnostic_rejects_bare_cr_osc_del_extra_malformed_headers_and_wrong_location(self):
        case = PACKET['cases'][0]; metadata = {'schema_usage': False, 'required_permission_missing': True, 'missing_referenced_columns': ['id']}
        valid = diagnostic(case)
        self.assertTrue(M['native_diagnostic'](valid.replace('\n', '\r\n'), case, metadata)['matched'])
        for text in (valid + '\r', valid + '\x1b]0;' + CANARY + '\x07', valid + '\x7f', valid + '\x85', valid + 'ERROR malformed\n', valid + 'DETAIL: ' + CANARY,
                     valid.replace('42501', 'P0001'), valid.replace('aclchk.c', 'pl_exec.c'), valid.replace('aclcheck_error', 'exec_stmt_raise'), valid + valid):
            result = M['native_diagnostic'](text, case, metadata)
            self.assertFalse(result['matched']); self.assertNotIn(CANARY, json.dumps(result))

    def test_source_position_accepts_only_exact_libpq_source_projection(self):
        case = PACKET['cases'][0]; probe = case['probes'][0]; statement = next(line for line in probe['sql_text'].splitlines() if line.startswith('SELECT'))
        position = 'LINE 1: ' + statement[:60] + '...'; caret = ' ' * (len('LINE 1: ') + 32) + '^'
        text = diagnostic(case).splitlines(); raw = text[0] + '\n' + position + '\n' + caret + '\n' + text[1] + '\n'
        metadata = {'schema_usage': False, 'required_permission_missing': True, 'missing_referenced_columns': ['id']}
        result = M['native_diagnostic'](raw, case, metadata, probe['sql_text'])
        self.assertTrue(result['matched']); self.assertTrue(result['source_position_verified'])
        self.assertFalse(M['native_diagnostic'](raw.replace(position, 'LINE 1: ' + CANARY), case, metadata, probe['sql_text'])['matched'])
        self.assertFalse(M['native_diagnostic'](raw.replace(caret, '^'), case, metadata, probe['sql_text'])['matched'])

    def test_packet_bypass_scopes_and_native_constraints_are_exact_source_sql(self):
        self.assertEqual(M['sha']((M['PACKET'] / 'packet.json').read_bytes()), M['PACKET_SHA'])
        setup = parse_sql((M['PACKET'] / 'native-fact-setup.sql').read_text(encoding='utf8'))
        changes = [row.stmt for row in setup if isinstance(row.stmt, ast.AlterTableStmt)]
        self.assertEqual(len(changes), 120)
        for case in PACKET['cases']:
            text = (M['PACKET'] / case['native_controls']).read_text(encoding='utf8'); statements = parse_sql(text)
            alters = [row.stmt for row in statements if isinstance(row.stmt, ast.AlterTableStmt)]
            self.assertEqual(len(alters), len(case['control_bypassed_user_triggers']))
            self.assertTrue(all(row.relation.schemaname + '.' + row.relation.relname == case['table'] for row in alters))
            self.assertNotIn('COMMIT;', text); self.assertEqual(text.count('\nROLLBACK;'), 1)
            self.assertNotIn('DISABLE TRIGGER ALL', text); self.assertNotIn('session_replication_role', text)

    def test_actual_comparator_counter_shape_and_invalid_counts(self):
        comparison = compare_native_catalog.Comparison(EXPECTED); comparison.record('test', 'test', 'test', 'PASS')
        self.assertEqual(dict(comparison.totals), {'PASS': 1}); self.assertTrue(M['native_pass_counts'](dict(comparison.totals)))
        for value in ({}, {'PASS': True}, {'PASS': 1, 'FAIL': False}, {'PASS': 1, 'OTHER': 0}, {'PASS': 1, 'INCOMPLETE': 1}):
            self.assertFalse(M['native_pass_counts'](value))

    def test_help_import_execute_no_helper_chain_and_no_process(self):
        path = ROOT / 'scripts/sql-review/run-native-table-denials-v2.py'
        with patch.object(runpy, 'run_path', side_effect=AssertionError('UNVERIFIED_HELPER')):
            namespace = {'__file__': str(path), '__name__': 'native_import_test'}
            exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
            with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as found: namespace['main'](['--help'])
            self.assertEqual(found.exception.code, 0)

    def test_real_transport_immutable_id_provider_login_and_closure_order(self):
        processes = []; api = {'psql': runpy.run_path(str(ROOT / M['API']))['psql']}
        def popen(*args, **kwargs): value = PipeProcess(*args, **kwargs); processes.append(value); return value
        def observer(role, text): self.assertIsNotNone(processes[0].poll()); self.assertIn('backend_start', text); return '0'
        with patch.object(subprocess, 'Popen', side_effect=popen):
            session = M['Session']('anon', CID, api, observer); session.capture()
            self.assertEqual(session.finish('SELECT 0;\nROLLBACK;')[:3], (0, ['0'], True)); session.close()
        self.assertIn('session_user', processes[0].writes[0]); self.assertIn('context_absent', processes[0].writes[0])

    def test_incremental_evidence_preserves_prior_stage_and_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory(prefix='native-evidence-offline-', dir=M['TASK']) as temporary:
            path = Path(temporary) / 'evidence'; value = M['Evidence'](path)
            value.stage('SAFE_COMPLETED_STAGE'); value.value['operations'].append({'closed_before_observers': True}); value.save()
            retained = json.loads(value.path.read_bytes()); self.assertEqual(retained['current_stage'], 'SAFE_COMPLETED_STAGE')
            self.assertTrue(retained['operations'][0]['closed_before_observers'])
            with self.assertRaises(FileExistsError): M['Evidence'](path)

    def safe_unexpected(self, text, native=None, metadata=None, declared=None, application_sha=None):
        declaration = json.loads((ROOT / 'review-output/first-rehearsal/diagnostic-identifiers.json').read_bytes())
        result = M['unexpected_operation_metadata'](text, native or diagnostic_native(), application_sha or declaration['source_sha256'], metadata,
                                                    declaration if declared is None else declared)
        self.assertNotIn(CANARY, json.dumps(result))
        self.assertNotIn('matched', result)
        return result

    def test_unexpected_known_native_constraint_and_not_null_metadata_is_diagnostic_only(self):
        for state, relation, constraint, column in (('23503', 'access_audit_logs', 'access_audit_logs_actor_user_id_fkey', None),
                ('23505', 'access_audit_logs', 'access_audit_logs_pkey', None), ('23514', 'audit_events', 'f0_null_metadata', None),
                ('23502', 'access_audit_logs', None, 'id')):
            with self.subTest(state=state):
                result = self.safe_unexpected(unexpected_stderr(state, relation, constraint, column))
                self.assertEqual(result['classification'], 'NATIVE_IDENTIFIER_METADATA')
                self.assertEqual(result['sqlstate'], state); self.assertEqual(result['native_object'], 'app.' + relation)
                self.assertEqual(result.get('native_constraint'), constraint); self.assertEqual(result.get('native_column'), column)

    def test_unexpected_unknown_or_misassociated_identifiers_are_redacted(self):
        samples = [unexpected_stderr(relation='audit_events'), unexpected_stderr(constraint=CANARY),
                   unexpected_stderr().replace('SCHEMA NAME:  app', 'SCHEMA NAME:  ' + CANARY),
                   unexpected_stderr(relation=CANARY), unexpected_stderr('23502', constraint=None, column=CANARY),
                   unexpected_stderr('23502', constraint=None, column='actor_user_id'),
                   unexpected_stderr('23514'), unexpected_stderr() + 'CONSTRAINT NAME:  access_audit_logs_pkey\n',
                   unexpected_stderr().replace('TABLE NAME:  access_audit_logs', 'TABLE NAME:  postgresql://' + CANARY)]
        for text in samples:
            result = self.safe_unexpected(text)
            self.assertEqual(result['identifier_classification'], 'REDACTED_IDENTIFIERS')
            self.assertFalse(set(result) & {'native_object', 'native_column', 'native_constraint'})

    def test_unexpected_caps_controls_and_multiple_or_malformed_headers_fail_closed(self):
        valid = unexpected_stderr()
        cases = [(valid + valid, 'NO_SINGLE_VALID_ERROR'), (valid.replace(CANARY, CANARY + ' ERROR:  23505: x', 1), 'NO_SINGLE_VALID_ERROR'),
                 (valid + 'ERROR malformed ' + CANARY, 'NO_SINGLE_VALID_ERROR'),
                 (valid.replace('ERROR:  23503:', 'ERROR: malformed'), 'NO_SINGLE_VALID_ERROR'),
                 ('DETAIL: ' + CANARY + '\n' + valid, 'NO_SINGLE_VALID_ERROR'),
                 (valid + '\x1b]0;' + CANARY + '\x07', 'CONTROL_CHARACTERS'), (valid + '\r', 'CONTROL_CHARACTERS'),
                 (valid + '\x7f', 'CONTROL_CHARACTERS'), (valid + '\x85', 'CONTROL_CHARACTERS'),
                 (valid + 'x' * 16385, 'OUTPUT_LIMIT_OR_TYPE'), (valid + 'x' * 2049, 'OUTPUT_LIMIT_OR_TYPE'),
                 (valid + '\n'.join(['DETAIL: x'] * 129), 'OUTPUT_LIMIT_OR_TYPE'), (None, 'OUTPUT_LIMIT_OR_TYPE')]
        for text, classification in cases:
            with self.subTest(classification=classification):
                result = self.safe_unexpected(text); self.assertEqual(result['classification'], classification)
                self.assertIsNone(result['sqlstate']); self.assertFalse(set(result) & {'frame', 'native_object'})
        self.assertEqual(self.safe_unexpected(valid.replace('\n', '\r\n'))['native_constraint'], 'access_audit_logs_actor_user_id_fkey')
        self.assertEqual(self.safe_unexpected(valid.replace('ERROR:', 'FATAL:'))['sqlstate'], '23503')

    def test_unexpected_any_formatted_sqlstate_survives_private_bad_input_but_still_stops(self):
        for state in ('22P02', '42804', '42601', 'XX999', 'ZZZZZ'):
            text = 'ERROR:  ' + state + ': invalid input syntax for uuid: "' + CANARY + '"\n'
            text += 'DETAIL: Failing row contains (ERROR, FATAL, PANIC, ' + CANARY + ')\nHINT: SELECT ' + CANARY + ';\n'
            safe = self.safe_unexpected(text)
            self.assertEqual(safe, {'classification': 'SQLSTATE_ONLY', 'sqlstate': state,
                                  'identifier_classification': 'NOT_RETAINED', 'frame_classification': 'NOT_RETAINED'})
            code, data, world, _ = self.exercise('setup-error', ['ConsentLog'], text)
            self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'EXACT_OPERATION_RESULT_REQUIRED')
            self.assertEqual(data['operations'][-1]['unexpected_operation_diagnostic'], safe)
            self.assertTrue(data['operations'][-1]['closed_before_observers']); self.assertFalse(world.restricted)
            self.assertFalse(data['facets']); self.assertFalse(world.controls)
            # Known-looking structured fields do not grant an unknown state's
            # error body any native-constraint association or verdict.
            safe = self.safe_unexpected(unexpected_stderr(state))
            self.assertEqual(safe['sqlstate'], state); self.assertEqual(safe['classification'], 'SQLSTATE_ONLY')
            self.assertEqual(safe['identifier_classification'], 'REDACTED_IDENTIFIERS')

    def test_unexpected_generic_guard_states_never_qualify_expected_denial(self):
        case = PACKET['cases'][0]; privilege = {'schema_usage': False, 'required_permission_missing': True, 'missing_referenced_columns': ['id']}
        for state in ('P0001', '42501'):
            text = unexpected_stderr(state)
            result = self.safe_unexpected(text); self.assertEqual(result['classification'], 'SQLSTATE_ONLY')
            self.assertFalse(M['native_diagnostic'](text, case, privilege)['matched'])
            code, data, world, _ = self.exercise('setup-error', ['ConsentLog'], text)
            self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'EXACT_OPERATION_RESULT_REQUIRED')
            self.assertFalse(data['facets']); self.assertFalse(world.controls); self.assertFalse(world.restricted)

    def test_unexpected_frame_requires_exact_source_native_body_identity_and_typed_bounds(self):
        text = 'ERROR:  P0001: ' + CANARY + '\nCONTEXT:  PL/pgSQL function platform_private.runtime_transition() line 2 at IF\n'
        helper = runpy.run_path(str(ROOT / 'scripts/sql-review/rehearsal-diagnostics.py'))['source_metadata']
        metadata = helper(text)
        result = self.safe_unexpected(text, metadata=metadata)
        self.assertEqual(result['frame_classification'], 'SOURCE_BOUND_FRAME'); self.assertEqual(result['frame']['body_line'], 2)
        self.assertEqual(set(result['frame']), {'schema', 'function', 'body_line', 'body_sha256', 'source_sha256'})
        mutants = []
        for key, value in (('body_line', True), ('body_line', 2.0), ('body_line', 0), ('body_line', 10000), ('schema', CANARY),
                           ('function', CANARY), ('body_sha256', CANARY), ('source_sha256', CANARY)):
            item = deepcopy(metadata); item['frame'][key] = value; mutants.append(item)
        for key, value in (('extra', CANARY), ('classification', [CANARY]), ('frame', {CANARY: CANARY})):
            item = deepcopy(metadata); item[key] = value; mutants.append(item)
        for item in mutants:
            self.assertEqual(self.safe_unexpected(text, metadata=item)['frame_classification'], 'REDACTED_CONTEXT')
        for key, value in (('body_sha256', '0' * 64), ('object', 'platform_private.runtime_transition(pg_catalog.text)'),
                           ('parameters', [{'name': CANARY}]), ('language', 'sql'), ('kind', 'p')):
            native = diagnostic_native(); native['functions'][0][key] = value
            self.assertEqual(self.safe_unexpected(text, native=native, metadata=metadata)['frame_classification'], 'REDACTED_CONTEXT')
        declaration = json.loads((ROOT / 'review-output/first-rehearsal/diagnostic-identifiers.json').read_bytes())
        for key, value in (('source_sha256', CANARY), ('source', CANARY)):
            item = deepcopy(declaration); item[key] = value
            self.assertEqual(self.safe_unexpected(text, metadata=metadata, declared=item)['frame_classification'], 'REDACTED_CONTEXT')
        self.assertEqual(self.safe_unexpected(text, metadata=metadata, application_sha='0' * 64)['frame_classification'], 'REDACTED_CONTEXT')
        native = diagnostic_native(); native['functions'] *= 2
        self.assertEqual(self.safe_unexpected(text, native=native, metadata=metadata)['frame_classification'], 'REDACTED_CONTEXT')

    def test_unexpected_unknown_malformed_multiple_and_sql_expression_frames_never_export_context(self):
        helper = runpy.run_path(str(ROOT / 'scripts/sql-review/rehearsal-diagnostics.py'))['source_metadata']
        header = 'ERROR:  42703: record "new" has no field "' + CANARY + '"\n'
        known = 'PL/pgSQL function platform_private.runtime_transition() line 2 at IF'
        for context in ('CONTEXT: ' + CANARY, 'CONTEXT: PL/pgSQL function platform_private.' + CANARY + '() line 2 at IF',
                        'CONTEXT: ' + known + '\n' + known, 'CONTEXT: ' + known.replace('()', '(text)'),
                        'CONTEXT: ' + known.replace('line 2', 'line 9999'), 'CONTEXT: ' + known + CANARY):
            text = header + context + '\n'
            result = self.safe_unexpected(text, metadata=helper(text)); self.assertEqual(result['frame_classification'], 'REDACTED_CONTEXT')
        # A valid single source frame may coexist with an ignored SQL-expression
        # context. Its SQL, record-field value and DETAIL never cross retention.
        text = header + 'CONTEXT: SQL expression "SELECT ' + CANARY + '"\n' + known + '\nDETAIL: ' + CANARY + '\n'
        result = self.safe_unexpected(text, metadata=helper(text)); self.assertEqual(result['frame_classification'], 'SOURCE_BOUND_FRAME')

    def test_unexpected_setup_and_late_control_keep_metadata_partial_facets_and_stop(self):
        for mode in ('setup-error', 'native-invalid', 'native-late'):
            code, data, world, memory = self.exercise(mode, ['ConsentLog', 'ConsentContentRevision'], unexpected_stderr())
            self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'EXACT_OPERATION_RESULT_REQUIRED')
            last = data['operations'][-1]; safe = last['unexpected_operation_diagnostic']
            self.assertEqual(safe['native_constraint'], 'access_audit_logs_actor_user_id_fkey')
            self.assertEqual(last['role'], 'postgres'); self.assertRegex(last['source_sql_sha256'], r'^[0-9a-f]{64}$')
            self.assertTrue(last['closed_before_observers']); self.assertTrue(data['subsequent_cases_stopped'])
            self.assertEqual(len(data['facets']), 24 if mode == 'native-late' else 0)
            self.assertEqual(memory.completed_before_failure, len(data['facets']))
            self.assertEqual(len(data['native_controls']), 1 if mode == 'native-late' else 0)
            for i, event in enumerate(world.events):
                if event[0] == 'execute': self.assertEqual(world.events[i + 1][0], 'close')

    def test_unexpected_diagnostic_never_observes_after_unconfirmed_backend_closure(self):
        def unconfirmed(session):
            session.world.events.append(('close-unconfirmed', session.role))
            raise M['HeldFailure']('OPERATION_BACKEND_STILL_LIVE')
        with patch.object(FakeSession, 'close', unconfirmed):
            code, data, world, _ = self.exercise('setup-error', ['ConsentLog'], unexpected_stderr())
        self.assertEqual(code, 2); self.assertEqual(data['failure']['code'], 'BACKEND_CLOSURE_UNCONFIRMED')
        last = data['operations'][-1]; self.assertFalse(last['closed_before_observers'])
        self.assertEqual(last['unexpected_operation_diagnostic']['sqlstate'], '23503')
        self.assertEqual(world.events[-1][0], 'close-unconfirmed'); self.assertFalse(data['facets']); self.assertFalse(world.restricted)

    def real_source_error(self, text):
        processes, events = [], []
        class ErrorProcess(PipeProcess):
            def write(process, value):
                if M['TUPLE'] in value: return super().write(value)
                process.writes.append(value)
                process.stderr.queue.put(text); process.stderr.queue.put(''); process.stdout.queue.put(''); process.returncode = 3
        def popen(*args, **kwargs):
            value = ErrorProcess(*args, **kwargs); processes.append(value); return value
        def observer(role, query):
            self.assertEqual(processes[0].poll(), 3); events.append('closure-observer'); return '0'
        def after():
            self.assertEqual(events[-1], 'closure-observer'); events.append('rollback-guard-observer')
        api = runpy.run_path(str(ROOT / M['API']))
        with tempfile.TemporaryDirectory(prefix='native-error-transport-offline-', dir=M['TASK']) as temporary:
            evidence = MemoryEvidence(Path(temporary) / 'evidence'); evidence.value['facets'] = [{'status': 'PRIOR_FACET_RETAINED'}]
            original_save = evidence.save
            def save():
                if 'unexpected_operation_diagnostic' in evidence.value['current'] and not evidence.value['current']['closed_before_observers']:
                    events.append('safe-metadata-persisted-before-close')
                original_save()
            evidence.save = save
            coor = M['Coordinator'].__new__(M['Coordinator']); coor.cid, coor.api, coor.evidence = CID, api, evidence
            coor.native, coor.packet = diagnostic_native(), PACKET
            coor.blobs = {'__diagnostic_identifiers': (ROOT / 'review-output/first-rehearsal/diagnostic-identifiers.json').read_bytes()}
            coor.raw, coor.guards, coor.fingerprint = observer, after, lambda: []
            with patch.object(subprocess, 'Popen', side_effect=popen), self.assertRaises(M['HeldFailure']) as found:
                coor.operation('native-fact-setup', 'postgres', 'BEGIN;\nSELECT 1;\nCOMMIT;', expected=['never'])
            self.assertEqual(found.exception.code, 'EXACT_OPERATION_RESULT_REQUIRED')
            self.assertLess(events.index('safe-metadata-persisted-before-close'), events.index('closure-observer'))
            self.assertLess(events.index('closure-observer'), events.index('rollback-guard-observer'))
            self.assertEqual(evidence.value['facets'], [{'status': 'PRIOR_FACET_RETAINED'}])
            self.assertTrue(evidence.value['operations'][-1]['closed_before_observers'])
            self.assertNotIn(CANARY, json.dumps(evidence.value))
            return evidence.value['operations'][-1]['unexpected_operation_diagnostic']

    def test_real_session_source_error_persists_before_close_then_observes_and_still_stops(self):
        self.assertEqual(self.real_source_error(unexpected_stderr())['native_constraint'], 'access_audit_logs_actor_user_id_fkey')
        self.assertEqual(self.real_source_error(unexpected_stderr('23502', constraint=None, column='id'))['native_column'], 'id')
        frame = 'ERROR:  P0001: ' + CANARY + '\nCONTEXT:  PL/pgSQL function platform_private.runtime_transition() line 2 at IF\n'
        self.assertEqual(self.real_source_error(frame)['frame_classification'], 'SOURCE_BOUND_FRAME')
        for text, classification in ((unexpected_stderr(constraint=CANARY), 'SQLSTATE_ONLY'),
                (unexpected_stderr() + unexpected_stderr(), 'NO_SINGLE_VALID_ERROR'),
                (unexpected_stderr() + '\x1b]0;' + CANARY + '\x07', 'CONTROL_CHARACTERS'),
                (unexpected_stderr() + 'x' * 17000, 'OUTPUT_LIMIT_OR_TYPE')):
            self.assertEqual(self.real_source_error(text)['classification'], classification)


if __name__ == '__main__': unittest.main(verbosity=2)
