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
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import sys

from pglast import ast, parse_sql

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/sql-review'))
import catalog_manifest
import compare_native_catalog

M = runpy.run_path(str(ROOT / 'scripts/sql-review/run-native-table-denials.py'))['main'].__globals__
PACKET = json.loads((M['PACKET'] / 'packet.json').read_bytes())
EXPECTED = catalog_manifest.build_manifest()['expected']
LOCAL = runpy.run_path(str(ROOT / 'scripts/check-local-f0-migrate.py'))['fixture']
CID = 'b' * 64
RUN = '941ae300-a3eb-4807-b47b-d46902372c98'
CANARY = 'SECRET_PASSWORD_HANDLE_SQL_NOT_TO_RETAIN'


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
            if world.mode == 'setup-error': return 3, [], False, 'ERROR:  23503: ' + CANARY
            return 0, [json.dumps({'control': 'all-native-fact-setup-triggers-restored', 'all_declared_user_triggers_restored': True})], True, ''
        if "'native-control-" in text:
            assert self.role == 'postgres' and 'COMMIT;' not in text and '\nROLLBACK;' in text
            model = re.search("'native-control-([A-Za-z0-9]+)'", text)[1]
            if world.mode == 'native-invalid': return 3, [], False, 'ERROR:  23503: ' + CANARY
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
    def __init__(self, mode='normal', subset=None):
        self.mode, self.subset, self.sessions, self.events, self.evidence = mode, subset, [], [], None
        self.seeded = False; self.controls = self.restricted = 0; self.issuer_seen = False; self.passwords = []
        self.target, _, _, _, self.context, self.container, self.volume = LOCAL()
        self.target['run_id'] = RUN
        self.target['target']['labels']['workinants.rehearsal.run'] = RUN
        self.target['source']['integrated_sql_sha256'] = PACKET['source_inputs_sha256']['review-output/foundation-application.review.sql']
        self.container['Id'] = CID; self.container['Config']['Labels']['workinants.rehearsal.run'] = RUN; self.volume['Labels']['workinants.rehearsal.run'] = RUN
        self.image = {'Id': self.container['Image'], 'Os': 'linux', 'Architecture': 'amd64', 'RepoDigests': [self.target['target']['image']]}
        self.native = {'format': 'workinants.native-catalog.v1', 'server_version_num': 170011, 'read_only': True, 'collected_as': 'postgres', 'collector_is_superuser': True,
                       'nonowner_acl': compare_native_catalog._acl_expected(EXPECTED, 'pg_database_owner')}
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
        if 'AS rows_sha256' in text:
            rows = [{'object': name, 'row_count': self.counts[name] if self.seeded else 0, 'rows_sha256': 'a' * 64} for name in self.counts]
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
    def exercise(self, mode='normal', subset=None):
        world = World(mode, subset)
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
        path = ROOT / 'scripts/sql-review/run-native-table-denials.py'
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


if __name__ == '__main__': unittest.main(verbosity=2)
