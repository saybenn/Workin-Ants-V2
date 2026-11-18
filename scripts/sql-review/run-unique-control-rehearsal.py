"""Dormant actual transport for the five reviewed UNIQUE SQL races.

Import/help are stdlib-only. No resource, credential, install, permission repair,
worker loop or cleanup exists here. An exact external source/target/native PASS
plan and separate execution review are required. Original controls stay NOT_RUN.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import secrets
import subprocess
import time
from types import ModuleType
import uuid

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT.parent
PACKET = ROOT / 'review-output/unique-control-rehearsal'
FIXTURES_SHA = '5eb0ae5413e917cd50ab35d1e3be2b9f0b38006c2ce93241f589b863647c6875'
CONTENT_SHA = 'bbb26d95da0f0592f542fb6e9e23e963519a5a8a6a5effb9c07870cecc82f79a'
CTX_PATH = 'scripts/sql-review/run-context-control-rehearsal.py'
CTX_SHA = '5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33'
PROTOCOL = 'scripts/unique_control_protocol.py'
PROTOCOL_SHA = '1857419b052c7bfc797b03204337b6fabe866e4cbeaf96206754f388b86d0b67'
API_PATH = 'scripts/sql-review/run-first-rehearsal.py'
HOST_PATH = 'scripts/sql-review/run-local-f0-migrate.py'
COLLECTOR = 'scripts/sql-review/collect_native_catalog.sql'
APPLICATION = 'review-output/foundation-application.review.sql'
MODULES = ('scripts/sql-review/run-unique-control-rehearsal.py', CTX_PATH, PROTOCOL, API_PATH, HOST_PATH,
           'scripts/sql-review/rehearsal-diagnostics.py', 'scripts/prepare-local-f0-history.py', COLLECTOR)
EXPECTED_NATIVE = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
DATABASE = 'wa_p0c_rehearsal'
NAMES = ('same-fingerprint-holder-commit', 'same-fingerprint-holder-rollback', 'changed-fingerprint-holder-commit',
         'changed-fingerprint-holder-rollback', 'different-subjects-identical-text-key')


class HeldFailure(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)


def need(value, code):
    if not value: raise HeldFailure(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
def digest(value): return sha(canonical(value).encode())
def quote(value): return "'" + str(value).replace("'", "''") + "'"


def unique_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            need(key not in result, 'DUPLICATE_JSON_FIELD'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))


def source_file(relative):
    need(type(relative) is str and '\\' not in relative and not Path(relative).is_absolute() and all(p not in ('', '.', '..') for p in relative.split('/')), 'SOURCE_PATH')
    path = (ROOT / relative).resolve(); need(path.is_relative_to(ROOT), 'SOURCE_PATH'); return path


def external_file(value):
    path = Path(value); need(path.is_absolute(), 'EXTERNAL_ABSOLUTE_PATH')
    path = path.resolve(); need(path.is_relative_to(TASK) and not path.is_relative_to(ROOT), 'EXTERNAL_TASK_PATH'); return path


def clean_text(text):
    normalized = text.replace('\r\n', '\n')
    return normalized if all(c in ('\t', '\n') or c.isprintable() for c in normalized) else None


def native_counts(counts):
    return (type(counts) is dict and 'PASS' in counts and set(counts) <= {'PASS', 'FAIL', 'INCOMPLETE'} and
            all(type(value) is int for value in counts.values()) and counts['PASS'] > 0 and counts.get('FAIL', 0) == counts.get('INCOMPLETE', 0) == 0)


def compile_cached(path, raw):
    module = ModuleType('_unique_verified_' + Path(path).stem); module.__file__ = str(ROOT / path)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__); return module.__dict__


def load_inputs(plan):
    fields = {'schema', 'scope', 'run_id', 'source_commit', 'source_tree', 'packet_sha256', 'reviewed_packet_sha256', 'reviewed_content_sha256',
              'source_modules_sha256', 'target_manifest', 'immutable_container_id', 'native_snapshot', 'native_comparison', 'native_attestation', 'race_names'}
    need(type(plan) is dict and set(plan) == fields and plan['schema'] == 'workinants.unique-control-run.v1' and plan['scope'] == 'FIVE_FINITE_UNIQUE_SQL_STORAGE_RACES_ONLY', 'PLAN_SCOPE')
    need(str(uuid.UUID(plan['run_id'])) == plan['run_id'] and uuid.UUID(plan['run_id']).version == 4 and
         all(type(plan[key]) is str and re.fullmatch('[0-9a-f]{40}', plan[key]) for key in ('source_commit', 'source_tree')) and
         type(plan['packet_sha256']) is str and re.fullmatch('[0-9a-f]{64}', plan['packet_sha256']) and
         type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}', plan['immutable_container_id']), 'PLAN_IDENTITY')
    need(plan['reviewed_packet_sha256'] == FIXTURES_SHA and plan['reviewed_content_sha256'] == CONTENT_SHA and tuple(plan['race_names']) == NAMES, 'FIVE_REVIEWED_RACES_REQUIRED')
    pins = plan['source_modules_sha256']; need(type(pins) is dict and set(pins) == set(MODULES), 'CLOSED_HELPER_PINS_REQUIRED')
    modules = {path: source_file(path).read_bytes() for path in MODULES}
    need(all(sha(raw) == pins[path] for path, raw in modules.items()) and pins[CTX_PATH] == CTX_SHA and pins[PROTOCOL] == PROTOCOL_SHA, 'REVIEWED_HELPER_SOURCE_DRIFT')
    raw = (PACKET / 'fixtures.json').read_bytes(); need(sha(raw) == FIXTURES_SHA, 'REVIEWED_PACKET_DRIFT'); packet = unique_json(raw)
    need(packet['schema'] == 'workinants.unique-control-fixtures.v1' and packet['status'] == 'NOT_RUN' and packet['database_posture'] == 'D' and
         packet['selected_control_ids'] == ['P0C-UNIQUE-01'] and tuple(race['name'] for race in packet['races']) == NAMES and len(packet['prepared_files_sha256']) == 50 and
         digest({key: packet[key] for key in ('source_files_sha256', 'prepared_files_sha256')}) == CONTENT_SHA == packet['source_only_packet_sha256'], 'PACKET_SCOPE')
    for path, expected in packet['source_files_sha256'].items(): need(sha(source_file(path).read_bytes()) == expected, 'PACKET_SOURCE_INPUT_DRIFT')
    for name, expected in packet['prepared_files_sha256'].items():
        need(type(name) is str and Path(name).name == name, 'PACKET_FILE_NAME')
        need(sha((PACKET / name).read_bytes()) == expected, 'PACKET_FILE_DRIFT')
    documents = {}
    for key in ('native_snapshot', 'native_comparison', 'native_attestation'):
        item = plan[key]; need(type(item) is dict and set(item) == {'path', 'sha256'}, 'NATIVE_ASSET_FIELDS')
        raw = external_file(item['path']).read_bytes(); need(sha(raw) == item['sha256'], 'NATIVE_ASSET_DRIFT'); documents[key] = unique_json(raw)
    native, comparison = documents['native_snapshot'], documents['native_comparison']
    need(native.get('format') == 'workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num'] == 170011 and native.get('read_only') is True and
         native.get('collected_as') == 'postgres' and native.get('collector_is_superuser') is True and comparison.get('format') == 'workinants.catalog-comparison.v1' and
         comparison.get('status') == 'PASS' and comparison.get('source_expected_sha256') == EXPECTED_NATIVE and comparison.get('native_snapshot_sha256') == digest(native) and
         comparison.get('findings') == [] and native_counts(comparison.get('check_counts')), 'FULL_NATIVE_PASS_REQUIRED')
    wanted = {'schema': 'workinants.unique-native-attestation.v1', 'run_id': plan['run_id'], 'container_id': plan['immutable_container_id'], 'source_commit': plan['source_commit'],
        'source_tree': plan['source_tree'], 'packet_sha256': plan['packet_sha256'], 'collector_sha256': pins[COLLECTOR], 'source_expected_sha256': EXPECTED_NATIVE,
        'native_snapshot_sha256': digest(native), 'native_comparison_file_sha256': plan['native_comparison']['sha256'], 'original_grantor_finalized': True, 'operation_backends_absent': True, 'comparison_status': 'PASS'}
    need(canonical(documents['native_attestation']) == canonical(wanted), 'SAME_RUN_CID_NATIVE_ATTESTATION_REQUIRED')
    # No helper code executes until the complete module/packet/input/asset graph
    # and the independently reviewed same-run native PASS have been verified.
    ctx = compile_cached(CTX_PATH, modules[CTX_PATH]); protocol = compile_cached(PROTOCOL, modules[PROTOCOL])
    need(set(ctx['SOURCE_MODULES']) <= set(modules), 'TRANSITIVE_HELPER_CLOSURE')
    ctx['load_helpers']({path: modules[path] for path in ctx['SOURCE_MODULES']})
    target = ctx['HOST']['validate_manifest'](plan['target_manifest'])
    need(target['run_id'] == plan['run_id'] and target['source']['integrated_sql_sha256'] == packet['source_files_sha256'][APPLICATION], 'TARGET_SOURCE_RUN_IDENTITY')
    return packet, native, target, ctx, protocol


class Evidence:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=False); self.path = directory / 'unique-control-results.json'
        self.value = {'schema': 'workinants.unique-control-evidence.v1', 'status': 'IN_PROGRESS', 'database_posture': 'D', 'current_stage': 'ENTRY',
                      'current_case': None, 'current': {}, 'operations': [], 'results': [], 'authentication': [], 'protocol_snapshots': [], 'committed_groups': [],
                      'cleanup_required': True, 'subsequent_cases_stopped': False, 'selected_controls': [{'id': 'P0C-UNIQUE-01', 'status': 'NOT_RUN'}],
                      'scope': 'FIVE_FINITE_SQL_STORAGE_RACES_ONLY_NOT_API_OR_CAS_QUALIFICATION'}
        self.save()
    def save(self):
        temporary = self.path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf8', newline='\n') as handle:
            handle.write(json.dumps(self.value, indent=2) + '\n'); handle.flush(); os.fsync(handle.fileno())
        temporary.replace(self.path)
    def stage(self, name): self.value['current_stage'] = name; self.save()


class Adapter:
    def __init__(self, plan, packet, native, target, ctx, protocol, evidence, session_factory=None):
        self.plan, self.packet, self.native, self.target, self.ctx, self.protocol, self.evidence = plan, packet, native, target, ctx, protocol, evidence
        self.cid = plan['immutable_container_id']; self.sessions = {}; self.pending = {}; self.current_race = None; self.case_instances = []; self.total_apps = 0
        self.session_factory = session_factory or ctx['Session']; self.expected_exits = {}; self.cleanup_mode = False; self.protocol_stage = 'ENTRY'
        issuer_packet = {'source_files_sha256': packet['source_files_sha256'], 'finite_caps': {'grant_instances_max': 10}}
        self.issuer = ctx['Coordinator'](plan, issuer_packet, native, target, evidence, session_factory=self.session_factory)
        self.issuer.psql = self.psql; self.issuer.raw = self.raw
    def psql(self, role):
        need(role in ('postgres', 'wa_context_issuer', 'wa_app_runtime'), 'ACTUAL_REGISTERED_ROLE_REQUIRED')
        args = self.ctx['API']['psql'](role, self.cid); index = args.index(self.cid)
        return args[:index] + ['-e', 'PGAPPNAME=wa-unique-' + self.plan['run_id']] + args[index:]
    def raw(self, role, text, timeout=60):
        result = subprocess.run(self.psql(role), input=text, text=True, capture_output=True, timeout=timeout, shell=False)
        need(type(result.returncode) is int and result.returncode == 0 and result.stderr == '' and len(result.stdout.encode()) <= 16 * 1024 * 1024, 'INDEPENDENT_SQL_UNPROVEN')
        return result.stdout.strip()
    def record(self, stage, **values): self.evidence.value['operations'].append({'stage': stage, **values}); self.evidence.save()
    def sql(self, name):
        need(name in self.packet['prepared_files_sha256'] and Path(name).name == name, 'UNREVIEWED_PACKET_SQL')
        raw = (PACKET / name).read_bytes(); need(sha(raw) == self.packet['prepared_files_sha256'][name], 'PACKET_SQL_SOURCE_DRIFT'); return raw.decode('utf8')
    def native_same(self):
        self.evidence.stage('VERIFY_COLLECTOR_SOURCE'); raw = source_file(COLLECTOR).read_bytes()
        need(sha(raw) == self.plan['source_modules_sha256'][COLLECTOR], 'COLLECTOR_SOURCE_DRIFT')
        value = unique_json(self.raw('postgres', raw.decode('utf8'))); good = digest(value) == digest(self.native)
        self.record('NATIVE_CATALOG', unchanged=good); need(good, 'NATIVE_CATALOG_DRIFT'); return True
    def observe(self, name, text, expected):
        self.evidence.stage(name); value = unique_json(self.raw('postgres', text)); good = canonical(value) == canonical(expected)
        outcomes = self.ctx['bounded_outcomes'](value, expected)
        self.record(name, matches=good, observation=outcomes); need(good, 'EXACT_STATE_OBSERVER_REQUIRED'); return value
    def guards(self):
        expected = {'expected_user_trigger_count': 4, 'actual_user_trigger_count': 4, 'exact_user_trigger_set_and_states': True, 'no_project_user_trigger_disabled': True}
        self.observe('FIXTURE_TRIGGER_RESTORATION', self.sql('fixture-trigger-restore-observe.sql'), expected); return True
    def resource(self):
        host = self.ctx['HOST']; self.evidence.stage('IMMUTABLE_RESOURCE_IDENTITY')
        context = host['docker_json'](['context', 'inspect', 'desktop-linux'], subprocess.run)
        container = host['docker_json'](['inspect', self.cid], subprocess.run)
        volume = host['docker_json'](['volume', 'inspect', self.target['target']['volume_name']], subprocess.run)
        observed = host['inspect_live'](self.target, context, container, volume); need(observed['container_id'] == self.cid, 'CREATED_CID_MISMATCH')
        image = host['docker_json'](['image', 'inspect', self.target['target']['image']], subprocess.run); host['verify_image'](self.target, container, image)
        self.record('RESOURCE_IDENTITY', exact_created_container=True)
    def preflight(self, packet):
        self.resource(); self.native_same(); self.ctx['API']['authentication_preflight'](self.evidence, self.cid)
        need(self.raw('postgres', "SELECT session_user='postgres' AND current_user='postgres' AND current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';") == 't', 'ORIGINAL_GRANTOR_SAFE_SETTINGS_REQUIRED')
        need(self.raw('postgres', "SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');") == 't', 'INDEPENDENT_FINALIZATION_REQUIRED')
        self.guards()
        tables = {'CustomerProfile': 'app.customer_profiles', 'RuntimeCommandReceipt': 'platform.runtime_command_receipt', 'CustomerProfileLifecycleEvent': 'app.customer_profile_lifecycle_event',
                  'OwnerMutationEvidence': 'platform.owner_mutation_evidence', 'event': 'platform.runtime_outbox_message', 'free': 'platform.runtime_outbox_message', 'extra': 'platform.runtime_outbox_message',
                  'duplicate': 'platform.runtime_command_receipt', 'user': 'app.users', 'grant': 'platform.database_action_grant'}
        checks = set()
        for race in packet['races']:
            for participant in race['participants'].values():
                for key, value in participant['source_case']['ids'].items(): checks.add('NOT EXISTS(SELECT 1 FROM ' + tables[key] + ' WHERE id=' + quote(value) + '::uuid)')
        for user in packet['namespace_policy']['users']:
            checks.add('NOT EXISTS(SELECT 1 FROM app.user_security_profiles WHERE user_id=' + quote(user) + '::uuid)')
            checks.add('NOT EXISTS(SELECT 1 FROM platform.database_action_grant WHERE principal_user_id=' + quote(user) + '::uuid)')
        for identity in packet['namespace_policy']['security_profiles']:
            checks.add('NOT EXISTS(SELECT 1 FROM app.user_security_profiles WHERE id=' + quote(identity) + '::uuid)')
        need(self.raw('postgres', 'SELECT ' + ' AND '.join(sorted(checks)) + ';') == 't', 'FRESH_UNIQUE_NAMESPACE_REQUIRED')
        return {'source_and_packet_pins': True, 'immutable_target_identity': True, 'auth_finalization_native_parity': True, 'fresh_namespace': True, 'fixture_triggers_restored': True}
    def seed_identity(self, packet):
        self.evidence.stage('TRUSTED_IDENTITY_FIXTURES')
        try: self.issuer.commit('postgres', self.sql('trusted-identity-fixtures.sql'), 'TRUSTED_UNIQUE_IDENTITY_FIXTURES')
        finally:
            need(getattr(self.issuer, 'last_transaction', {}).get('operation_closed') is True, 'IDENTITY_SETUP_CLOSURE_UNPROVEN')
            self.guards()
        return {'source_sql_exact': True, 'committed': True, 'backend_closed': True, 'all_triggers_restored': True}
    def protocol_save(self, record):
        if 'name' in record: self.evidence.value['current_case'] = record['name']
        if 'stage' in record: self.protocol_stage = record['stage']; self.cleanup_mode = record['stage'] == 'CLOSE_REMAINING_AFTER_FAILURE'
        self.evidence.value['protocol_snapshots'].append(deepcopy(record)); self.evidence.save()
    def participant(self, side, participant):
        matches = [race for race in self.packet['races'] if canonical(race['participants'][side]) == canonical(participant)]
        need(len(matches) == 1, 'UNREVIEWED_PARTICIPANT')
        race = matches[0]
        if side == 'A':
            need(all(session.closed for session in self.sessions.values()), 'PREVIOUS_OPERATION_NOT_CLOSED')
            self.current_race = race; self.sessions = {}; self.pending = {}; self.case_instances = []; self.expected_exits = {}; self.cleanup_mode = False
        else: need(race is self.current_race, 'MIXED_RACE_PARTICIPANTS')
        return race
    def open_bound(self, side, participant):
        self.participant(side, participant); self.evidence.stage('OPEN_BIND_' + side)
        need(side not in self.sessions and self.total_apps < 10, 'FINITE_APP_CONNECTION_LIMIT'); self.total_apps += 1
        session = self.session_factory('wa_app_runtime', self); self.sessions[side] = session
        session.begin('read committed'); backend = session.capture()
        if side == 'B': need(backend['pid'] != self.sessions['A'].backend['pid'] and backend['xid'] != self.sessions['A'].backend['xid'], 'DISTINCT_ACTUAL_TUPLES_REQUIRED')
        rows, ack, errors = session.call("SET LOCAL statement_timeout='10s'; SET LOCAL lock_timeout='5s'; SET LOCAL idle_in_transaction_session_timeout='30s';")
        need(ack is True and rows == [] and errors == '', 'FINITE_SESSION_TIMEOUTS_REQUIRED')
        key = self.issuer.issue(participant['source_case']['grant'], backend); self.case_instances.append(key)
        secret = self.issuer.instances[key]['secret']; rows, ack, errors = session.call('SELECT platform_private.bind_request_context(' + quote(secret) + ');')
        need(ack is True and rows == [] and errors == '', 'SAME_CONNECTION_BIND_UNPROVEN')
        self.record('ACTUAL_APP_BOUND', side=side, issuer_commit_and_closure_verified=True, same_tuple=True)
        return {'actual_app_identity_and_tuple': True, 'independent_issuer_commit': True, 'issuer_backend_closed': True, 'bound_same_connection': True}
    def group(self, side, participant, file_key, markers):
        self.guards(); self.evidence.stage('GROUP_READY_' + side)
        rows, ack, errors = self.sessions[side].call(self.sql(participant[file_key]))
        good = rows == markers and ack is True and errors == '' and self.sessions[side].active is True
        self.record('GROUP_CONSTRAINTS_CHECKED', side=side, markers_exact=rows == markers, acknowledged=ack is True, errors_absent=errors == '')
        need(good, 'COMPLETE_GROUP_READY_UNPROVEN')
        return {'markers_exact': True, 'constraints_checked': True, 'group_ready': True, 'transaction_open': True}
    def stage_group(self, side, participant):
        marker = participant['markers']; return self.group(side, participant, 'hold_ready_sql', [marker['before_command'], marker['after_command'], marker['group_ready']])
    def complete_remainder(self, side, participant): return self.group(side, participant, 'remainder_sql', [participant['markers']['group_ready']])
    def drain_available(self, session):
        rows = []
        while not session.lines.empty():
            value = session.lines.get_nowait()
            if value: rows.append(value)
        return rows
    def start_waiting_command(self, side, participant):
        need(side == 'B' and side not in self.pending, 'ASYNC_COMMAND_STATE'); self.guards()
        self.evidence.stage('SEND_ASYNC_B_COMMAND')
        session = self.sessions[side]; token = 'WA_UNIQUE_ASYNC_ACK|' + secrets.token_hex(16)
        need(session.process.poll() is None and session.active is True and session.last_errors == '', 'ASYNC_LIVE_TRANSACTION_REQUIRED')
        session.process.stdin.write(self.sql(participant['command_sql']) + '\nSELECT ' + quote(token) + ';\n'); session.process.stdin.flush()
        line = session.lines.get(timeout=15)
        need(line == participant['markers']['before_command'] and not session.invalid.is_set(), 'ASYNC_BEFORE_MARKER_REQUIRED')
        need(self.drain_available(session) == [], 'WAITER_COMPLETED_BEFORE_BARRIER')
        self.pending[side] = {'ack': token, 'before_seen': True, 'participant': participant}
        self.record('WAITER_COMMAND_SENT', before_marker_exact=True, later_output_absent=True)
        return {'before_marker_exact': True, 'command_sent': True, 'after_marker_absent': True}
    def observe_barrier(self, contract):
        self.evidence.stage('OBSERVE_B_WAITING_ON_A'); wanted = contract['expected']; start = time.monotonic(); last = dict.fromkeys(wanted, False); count = 0
        tuples = {side: {key: value for key, value in session.backend.items() if key != 'clock'} for side, session in self.sessions.items()}
        text = self.protocol['barrier_sql'](tuples)
        for count in range(1, contract['limits']['max_observations'] + 1):
            remaining = contract['limits']['deadline_seconds'] - (time.monotonic() - start)
            if remaining <= 0: break
            need(self.sessions['A'].process.poll() is None and self.sessions['B'].process.poll() is None and self.drain_available(self.sessions['B']) == [], 'WAITER_LEFT_BARRIER_UNEXPECTEDLY')
            # Bound the subprocess as well as the polling loop. These fixed
            # read-only metadata probes must not outlive the two-second barrier.
            value = unique_json(self.raw('postgres', "SET statement_timeout='500ms'; SET lock_timeout='500ms';\n" + text, timeout=min(remaining, 1)))
            shape = type(value) is dict and set(value) == set(wanted) and all(type(value[key]) is bool for key in wanted)
            self.record('NATIVE_WAIT_OBSERVATION', attempt=count, shape_matches=shape, comparisons=self.ctx['bounded_outcomes'](value, wanted))
            need(shape, 'BARRIER_RESPONSE_SHAPE'); last = value
            within = time.monotonic() - start <= contract['limits']['deadline_seconds']
            if all(value.values()) and within: return {**value, 'observations': count, 'within_deadline': True}
            if not within: break
            time.sleep(.02)
        return {**last, 'observations': count, 'within_deadline': False}
    def finish_pending(self, side, expected_ack):
        session = self.sessions[side]; pending = self.pending[side]; rows = []; ack = False; deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try: line = session.lines.get(timeout=.1)
            except queue.Empty:
                if session.process.poll() is not None: break
                continue
            if line == pending['ack']: ack = True; break
            if line: rows.append(line)
        if not ack:
            session.process.wait(timeout=10)
            for reader in session.readers: reader.join(timeout=5)
            rows.extend(self.drain_available(session))
            need(not any(reader.is_alive() for reader in session.readers), 'ASYNC_READERS_NOT_FINISHED')
        else: rows.extend(self.drain_available(session))
        need(not session.invalid.is_set(), 'ASYNC_OUTPUT_INCOMPLETE')
        errors = ''.join(session.errors); session.last_errors = errors
        if expected_ack: need(session.process.poll() is None and ack is True, 'WAITING_COMMAND_ACK_UNPROVEN')
        return rows, ack, errors
    def finish_duplicate(self, side, expected):
        rows, ack, errors = self.finish_pending(side, False); session = self.sessions[side]; code = session.process.poll()
        result = self.protocol['duplicate_diagnostic'](errors, expected)
        before_only = self.pending[side]['before_seen'] is True and rows == [] and ack is False
        good = type(code) is int and code == 3 and before_only and result['matched']
        self.record('NATIVE_DUPLICATE_VERDICT', exit_code=code if type(code) is int else None, acknowledgement=ack is True, before_only=before_only, diagnostic=result)
        if good: session.expected_failure = True; self.expected_exits[side] = 3
        return {'exit_code': code if type(code) is int else None, 'acknowledged': ack, 'sqlstate': result['sqlstate'], 'schema_table_constraint_exact': result['schema_table_constraint_exact'],
                'native_location_exact': result['native_location_exact'], 'before_only_marker_exact': before_only, 'extra_output_absent': rows == [] and result['matched']}
    def finish_waiting_command(self, side):
        rows, ack, errors = self.finish_pending(side, True); expected = [self.pending[side]['participant']['markers']['after_command']]
        good = rows == expected and ack is True and errors == '' and self.sessions[side].active is True
        self.record('WAITING_COMMAND_RELEASED', after_marker_exact=rows == expected, acknowledged=ack is True, errors_absent=errors == '')
        need(good, 'WAITING_COMMAND_RELEASE_UNPROVEN'); del self.pending[side]
        return {'before_after_markers_exact': True, 'acknowledged': True, 'transaction_open': True}
    def end_transaction(self, side, outcome):
        need(outcome in ('COMMIT', 'ROLLBACK'), 'TRANSACTION_OUTCOME_REQUIRED'); text = self.sql(outcome.lower() + '.sql')
        need(text == outcome + ';\n', 'TERMINAL_SQL_SHAPE')
        rows, ack, errors = self.sessions[side].call(text); good = rows == [] and ack is True and errors == '' and self.sessions[side].active is False
        self.record('TRANSACTION_END', side=side, outcome=outcome, acknowledged=ack is True, exact_output=rows == [] and errors == '')
        if good:
            self.expected_exits[side] = 0
            if outcome == 'COMMIT': self.evidence.value['committed_groups'].append({'race': self.current_race['name'], 'side': side, 'commit_acknowledged': True}); self.evidence.save()
        return {'exit_code': 0 if good else None, 'acknowledged': ack is True, 'transaction_ended': good}
    def close(self, side):
        session = self.sessions.get(side)
        if session is None: return {'client_exited': False, 'backend_absent': False}
        code = session.close()
        good = session.closed is True and type(code) is int and (self.cleanup_mode or code == self.expected_exits.get(side, 0))
        self.record('OPERATION_CLOSURE', side=side, exact_backend_absent=session.closed is True, exit_code=code if type(code) is int else None, expected_exit=good)
        return {'client_exited': good, 'backend_absent': good}
    def all_closed(self): need(self.sessions and all(session.closed for session in self.sessions.values()), 'BUSINESS_OBSERVER_BEFORE_CLOSURE')
    def xid_witness(self, race, side):
        ids = race['participants'][side]['source_case']['ids']; xid = quote(self.sessions[side].backend['xid'])
        parts = {'source_xid_matches': "EXISTS(SELECT 1 FROM app.customer_profiles WHERE id=" + quote(ids['CustomerProfile']) + ' AND mutation_transaction_id=' + xid + ')',
                 'command_xid_matches': "EXISTS(SELECT 1 FROM platform.runtime_command_receipt WHERE id=" + quote(ids['RuntimeCommandReceipt']) + ' AND mutation_transaction_id=' + xid + ')',
                 'history_xid_matches': "EXISTS(SELECT 1 FROM app.customer_profile_lifecycle_event WHERE id=" + quote(ids['CustomerProfileLifecycleEvent']) + ' AND mutation_transaction_id=' + xid + ')',
                 'evidence_xid_matches': "EXISTS(SELECT 1 FROM platform.owner_mutation_evidence WHERE id=" + quote(ids['OwnerMutationEvidence']) + ' AND mutation_transaction_id=' + xid + ')',
                 'outbox_xid_matches': "(SELECT count(*)=2 AND bool_and(mutation_transaction_id=" + xid + ') FROM platform.runtime_outbox_message WHERE command_receipt_id=' + quote(ids['RuntimeCommandReceipt']) + ')'}
        query = 'SELECT jsonb_build_object(' + ','.join(quote(key) + ',' + value for key, value in parts.items()) + ');'
        self.observe('WINNER_ACTUAL_TRANSACTION_' + side, query, dict.fromkeys(parts, True))
    def observe_complete(self, race):
        self.all_closed(); counts = self.observe('EXACT_COMPLETE_GROUP_COUNTS', self.sql(race['observer_sql']), race['observer_expected'])
        for side in race['required_coherent_participants']:
            participant = race['participants'][side]; self.observe('WINNER_COHERENCE_' + side, self.sql(participant['observer_sql']), participant['source_case']['observer_expected']); self.xid_witness(race, side)
        self.guards(); self.native_same(); self.issuer.retention(self.case_instances)
        return {'counts': counts, 'winner_groups_coherent': True, 'winner_transaction_ids_match': True, 'all_triggers_restored': True, 'native_catalog_unchanged': True, 'issuer_grants_immutable': True}
    def observe_partial(self, race):
        self.all_closed(); value = unique_json(self.raw('postgres', self.sql(race['observer_sql']))); expected = race['observer_expected']
        self.record('PARTIAL_COMPLETE_GROUP_COUNTS', observation=self.ctx['bounded_outcomes'](value, expected))
        need(type(value) is dict and set(value) == set(expected) and all(type(count) is int and 0 <= count <= 4 for count in value.values()), 'PARTIAL_COUNT_SHAPE')
        self.guards(); self.native_same(); self.issuer.retention(self.case_instances); return value
    def run(self):
        result = self.protocol['run_packet'](self.packet, self, self.protocol_save)
        self.evidence.value['results'] = result['results']; self.evidence.value['subsequent_cases_stopped'] = result['subsequent_cases_stopped']; self.evidence.save()
        need(result['status'] == 'SOURCE_PROTOCOL_ONLY' and result['subsequent_cases_stopped'] is False and len(result['results']) == 5 and self.total_apps == 10 and len(self.issuer.instances) == 10, 'FIVE_ACTUAL_RACES_INCOMPLETE')
        self.issuer.retention(list(self.issuer.instances)); self.native_same()
        need(all(sha(source_file(path).read_bytes()) == value for path, value in self.plan['source_modules_sha256'].items()) and
             sha((PACKET / 'fixtures.json').read_bytes()) == FIXTURES_SHA and all(sha(source_file(path).read_bytes()) == value for path, value in self.packet['source_files_sha256'].items()) and
             all(sha((PACKET / name).read_bytes()) == value for name, value in self.packet['prepared_files_sha256'].items()), 'POST_RUN_SOURCE_PRESERVATION_REQUIRED')
        self.evidence.value.update(status='COMPLETED_FIVE_SQL_STORAGE_RACES_ONLY_ASSERTIONS_NOT_RUN', source_packet_unchanged=True); self.evidence.stage('COMPLETE_PENDING_EVIDENCE_REVIEW')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--execute-reviewed-unique-controls', action='store_true', required=True)
    parser.add_argument('--reviewed-run-plan', type=Path, required=True); parser.add_argument('--evidence-directory', type=Path, required=True); args = parser.parse_args(argv)
    evidence = None
    try:
        directory = external_file(args.evidence_directory); need(not directory.exists(), 'FRESH_EVIDENCE_DIRECTORY_REQUIRED'); evidence = Evidence(directory); evidence.stage('VERIFY_REVIEWED_INPUTS')
        raw = external_file(args.reviewed_run_plan).read_bytes(); plan = unique_json(raw)
        packet, native, target, ctx, protocol = load_inputs(plan)
        evidence.value.update(run_id=plan['run_id'], container_id=plan['immutable_container_id'], source_commit=plan['source_commit'], source_tree=plan['source_tree'], packet_sha256=plan['packet_sha256'], reviewed_run_plan_sha256=sha(raw)); evidence.save()
        Adapter(plan, packet, native, target, ctx, protocol, evidence).run(); return 0
    except (Exception, KeyboardInterrupt) as error:
        if evidence is not None:
            evidence.value.update(status='STOPPED_RETAINED_FOR_CONTROLLED_CLEANUP', subsequent_cases_stopped=True,
                                  failure={'code': error.code if isinstance(error, HeldFailure) else 'VERIFIED_TRANSPORT_OR_HELPER_REFUSED', 'stage': evidence.value['current_stage']}); evidence.save()
        return 2


if __name__ == '__main__': raise SystemExit(main())
