"""Dormant finite direct-SQL worker coordinator. Import/--help contact no runtime.

Root supplies a separately reviewed external run plan and immutable created
container ID. No provisioning/migration/cleanup/worker loop/adapter lives here.
The reviewed six proposals include two blocked NOT_RUN owner-generation paths.
Every selected control and every unprepared vector remains NOT_RUN as a whole.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import runpy
import secrets
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT.parent
PACKET = ROOT / 'review-output/worker-control-rehearsal'
PACKET_SHA256 = '6e3f126fd014c91f1c2ac519e77635eef2d2232bca2b609c90023495d626aff2'
CONTENT_SHA256 = '65003efc621a3552059504a8b78530d2d921f8caee17fd51f3c92eb9ad6f9ba7'
EXPECTED_CATALOG_SOURCE = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
API_PATH = 'scripts/sql-review/run-first-rehearsal.py'
HOST_PATH = 'scripts/sql-review/run-local-f0-migrate.py'
COLLECTOR = 'scripts/sql-review/collect_native_catalog.sql'
SOURCE_MODULES = ('scripts/sql-review/run-worker-control-rehearsal.py', API_PATH, HOST_PATH,
    'scripts/sql-review/rehearsal-diagnostics.py', 'scripts/prepare-local-f0-history.py', COLLECTOR,
    'review-output/first-rehearsal/diagnostic-identifiers.json')
DATABASE = 'wa_p0c_rehearsal'
ROLES = ('postgres', 'wa_app_runtime', 'wa_worker', 'wa_context_issuer', 'wa_identity_service_authority')
NAMES = ('one-complete-default-free', 'direct-source-snapshot-controls', 'worker-service-currentness',
         'worker-grant-revocation', 'worker-source-generation', 'worker-user-security-generation')
MODELS = ('TrackSubscription', 'TrackEntitlementGrant', 'TrackBaseSelection')
TUPLE = 'WA_WORKER_COORDINATOR_TUPLE|'
HEADER = re.compile(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)')
FRAME = re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function platform_private\.bind_request_context\(text\) line ([1-9][0-9]{0,3}) at RAISE')


class HeldFailure(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)


def require(value, code):
    if not value: raise HeldFailure(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def digest(value): return sha(canonical(value).encode('utf8'))
def quote(value): return "'" + str(value).replace("'", "''") + "'"


def native_pass_counts(value):
    # compare_native_catalog serializes Counter directly: clean reports may
    # omit zero FAIL/INCOMPLETE keys. Only typed positive PASS is mandatory.
    return (type(value) is dict and 'PASS' in value and set(value) <= {'PASS', 'FAIL', 'INCOMPLETE'} and
            all(type(count) is int for count in value.values()) and value['PASS'] > 0 and
            value.get('FAIL', 0) == value.get('INCOMPLETE', 0) == 0)


def unique_json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, 'DUPLICATE_JSON_KEY'); value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=unique)


def external_file(value):
    path = Path(value)
    require(path.is_absolute(), 'ABSOLUTE_EXTERNAL_PATH_REQUIRED')
    path = path.resolve()
    require(path.is_relative_to(TASK) and not path.is_relative_to(ROOT), 'TASK_EXTERNAL_PATH_REQUIRED')
    return path


def source_file(relative):
    require(type(relative) is str and '\\' not in relative and not Path(relative).is_absolute() and
            all(part not in ('', '.', '..') for part in relative.split('/')), 'SOURCE_RELATIVE_PATH')
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), 'SOURCE_PATH_ESCAPES_ROOT')
    return path


def packet_file(relative):
    require(type(relative) is str and Path(relative).name == relative and relative not in ('', '.', '..'), 'PACKET_FILE_NAME')
    return PACKET / relative


def load_inputs(plan):
    expected = {'schema', 'scope', 'reviewed_packet_sha256', 'reviewed_content_sha256', 'source_modules_sha256',
                'target_manifest', 'immutable_container_id', 'native_snapshot', 'native_comparison', 'scenario_names'}
    require(type(plan) is dict and set(plan) == expected, 'RUN_PLAN_FIELDS')
    require(plan['schema'] == 'workinants.worker-control-run.v1' and plan['scope'] == 'REVIEWED_LOCAL_WORKER_SQL_SUBSET_ONLY', 'RUN_PLAN_SCOPE')
    require(plan['reviewed_packet_sha256'] == PACKET_SHA256 and plan['reviewed_content_sha256'] == CONTENT_SHA256, 'REVIEWED_PACKET_REQUIRED')
    require(type(plan['immutable_container_id']) is str and re.fullmatch('[0-9a-f]{64}', plan['immutable_container_id']), 'CREATED_IMMUTABLE_ID_REQUIRED')
    pins = plan['source_modules_sha256']
    require(type(pins) is dict and set(pins) == set(SOURCE_MODULES) and
            all(pins[name] == sha(source_file(name).read_bytes()) for name in SOURCE_MODULES), 'COORDINATOR_SOURCE_DRIFT')
    raw = (PACKET / 'fixtures.json').read_bytes()
    require(sha(raw) == PACKET_SHA256, 'WORKER_PACKET_DRIFT')
    packet = unique_json(raw.decode('utf8'))
    require(packet['schema'] == 'workinants.worker-control-fixtures.v1' and packet['status'] == 'NOT_RUN' and
            packet['source_only_packet_sha256'] == CONTENT_SHA256 and packet['database_posture'] == 'D', 'WORKER_PACKET_SCOPE')
    require([row['name'] for row in packet['scenarios']] == list(NAMES) and plan['scenario_names'] == list(NAMES), 'FINITE_SIX_PROPOSALS_REQUIRED')
    require(all(row['status'] == 'NOT_RUN' for row in packet['scenarios']) and len(packet['worker_acl_ceiling_rows']) == 32 and
            len(packet['grants']['process']['allowed_fields']) == 355, 'WORKER_BOUNDS_DRIFT')
    require(digest({key: packet[key] for key in ('source_files_sha256', 'prepared_files_sha256')}) == CONTENT_SHA256, 'PACKET_AGGREGATE_DRIFT')
    for path, expected_hash in packet['source_files_sha256'].items():
        require(sha(source_file(path).read_bytes()) == expected_hash, 'WORKER_SOURCE_INPUT_DRIFT')
    for path, expected_hash in packet['prepared_files_sha256'].items():
        require(sha(packet_file(path).read_bytes()) == expected_hash, 'WORKER_SQL_DRIFT')
    documents = {}
    for key in ('native_snapshot', 'native_comparison'):
        entry = plan[key]
        require(type(entry) is dict and set(entry) == {'path', 'sha256'}, 'NATIVE_REVIEW_FILE_FIELDS')
        raw = external_file(entry['path']).read_bytes()
        require(sha(raw) == entry['sha256'], 'NATIVE_REVIEW_FILE_DRIFT')
        documents[key] = unique_json(raw.decode('utf8'))
    native, report = documents['native_snapshot'], documents['native_comparison']
    require(native.get('format') == 'workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num'] == 170011 and
            native.get('read_only') is True and native.get('collected_as') == 'postgres' and native.get('collector_is_superuser') is True, 'REVIEWED_NATIVE_SNAPSHOT_REQUIRED')
    require(report.get('format') == 'workinants.catalog-comparison.v1' and report.get('status') == 'PASS' and
            report.get('native_snapshot_sha256') == digest(native) and report.get('source_expected_sha256') == EXPECTED_CATALOG_SOURCE and
            native_pass_counts(report.get('check_counts')) and report.get('findings') == [], 'REVIEWED_NATIVE_PARITY_PASS_REQUIRED')
    # Every approved module and packet/input/output/review prehash is verified
    # above using stdlib data operations, before any helper chain can execute.
    api = runpy.run_path(str(source_file(API_PATH)))
    host = runpy.run_path(str(source_file(HOST_PATH)))
    target = host['validate_manifest'](plan['target_manifest'])
    require(target['source']['integrated_sql_sha256'] == packet['source_files_sha256']['review-output/foundation-application.review.sql'], 'TARGET_SQL_SOURCE_MISMATCH')
    return packet, native, api, host


def binder_diagnostic(stderr, application):
    """One exact header and exact source-bound argument-bearing PL frame only."""
    pattern = r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\)\s+RETURNS\b[^;]*?\bAS\s+(\$[a-z_0-9]*\$)(.*?)\1;'
    bodies = list(re.finditer(pattern, application, re.S))
    require(len(bodies) == 1, 'BINDER_SOURCE_BODY_UNAVAILABLE')
    body = bodies[0][2]
    message = "invalid, stale or unsupported context"
    lines = [index for index, line in enumerate(body.split('\n'), 1) if 'RAISE EXCEPTION ' + quote(message) in line]
    require(len(lines) == 1, 'BINDER_SOURCE_LINE_AMBIGUOUS')
    # CRLF is the only accepted transport normalization. Bare CR, terminal
    # controls (including OSC), and malformed extra severity candidates cannot
    # be hidden by splitlines() or omitted from the count of verbose headers.
    normalized = stderr.replace('\r\n', '\n')
    clean = all(character in ('\n', '\t') or character.isprintable() for character in normalized)
    diagnostic_lines = normalized.split('\n')
    headers = [match for line in diagnostic_lines if (match := HEADER.fullmatch(line))]
    candidates = [line for line in diagnostic_lines if re.search(r'\b(?:ERROR|FATAL|PANIC)\b', line)]
    frames = [line for line in diagnostic_lines if 'PL/pgSQL function ' in line]
    match = FRAME.fullmatch(frames[0]) if len(frames) == 1 else None
    matched = clean and len(candidates) == len(headers) == 1 and headers[0][1] == '42501' and headers[0][2] == message and match is not None and int(match[1]) == lines[0]
    return {'matched': matched, 'classification': 'EXPECTED_STALE_BINDER' if matched else 'UNLISTED_OR_INCOMPLETE_DISCARDED',
        'sqlstate': '42501' if matched else None, 'source_frame_verified': bool(match and int(match[1]) == lines[0]),
        'body_sha256': sha(body.encode('utf8')) if matched else None, 'body_line': lines[0] if matched else None}


class Evidence:
    def __init__(self, directory, packet):
        directory.mkdir(parents=True, exist_ok=False)
        self.path = directory / 'worker-control-results.json'
        self.value = {'schema': 'workinants.worker-control-evidence.v1', 'status': 'IN_PROGRESS', 'current_stage': 'ENTRY',
            'current_case': None, 'current': {}, 'results': [], 'operations': [], 'authentication': [], 'cleanup_required': True,
            'subsequent_cases_stopped': False, 'reviewed_packet_sha256': PACKET_SHA256, 'reviewed_content_sha256': CONTENT_SHA256,
            'selected_controls': [{'id': value, 'status': 'NOT_RUN'} for value in packet['selected_control_ids']],
            'proposals': [{'name': row['name'], 'status': 'NOT_RUN', 'execution_dependencies': row['execution_dependencies']} for row in packet['scenarios']],
            'unprepared_vectors': deepcopy(packet['mandatory_unprepared_vectors']), 'database_posture': 'D',
            'coverage_limits': ['Synthetic SQL fixtures, not owner/API/runner qualification.', 'Currentness covers only exact work SELECT under transport claim scope.',
                'Only three prepared reverse-proof exact/wrong-xid branches; broader source substitutions and all owner-generation positives remain NOT_RUN.']}
        with self.path.open('x', encoding='utf8', newline='\n') as handle: handle.write(json.dumps(self.value, indent=2) + '\n')

    def save(self):
        temporary = self.path.with_suffix('.json.tmp')
        with temporary.open('w', encoding='utf8', newline='\n') as handle:
            handle.write(json.dumps(self.value, indent=2) + '\n'); handle.flush(); os.fsync(handle.fileno())
        temporary.replace(self.path)

    def stage(self, name): self.value['current_stage'] = name; self.save()


class Session:
    """A bounded actual-login connection. Tuple/secret/output stay in memory."""
    def __init__(self, role, container, api, raw):
        require(role in ROLES and re.fullmatch('[0-9a-f]{64}', container), 'EXACT_RUNTIME_SESSION_IDENTITY')
        self.role, self.container, self.api, self.raw = role, container, api, raw
        self.backend = None; self.queue = queue.Queue(maxsize=256); self.errors = []; self.invalid = threading.Event()
        self.process = subprocess.Popen(api['psql'](role, container), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1, shell=False)
        def output():
            try:
                while line := self.process.stdout.readline(65537):
                    if len(line) > 65536: self.invalid.set(); continue
                    try: self.queue.put_nowait(line.rstrip('\r\n'))
                    except queue.Full: self.invalid.set()
            except Exception: self.invalid.set()
        def errors():
            size = 0
            try:
                while chunk := self.process.stderr.read(4096):
                    size += len(chunk)
                    if size <= 65536: self.errors.append(chunk)
                    else: self.invalid.set()
            except Exception: self.invalid.set()
        self.readers = [threading.Thread(target=output, daemon=True), threading.Thread(target=errors, daemon=True)]
        for reader in self.readers: reader.start()

    def send(self, text): self.process.stdin.write(text); self.process.stdin.flush()

    def receive(self, token, timeout=15):
        lines, deadline = [], time.monotonic() + timeout
        while time.monotonic() < deadline:
            try: line = self.queue.get(timeout=.1)
            except queue.Empty:
                if self.process.poll() is not None: break
                continue
            if line == token: return lines, True
            if line: lines.append(line)
        return lines, False

    def capture(self):
        self.send("BEGIN ISOLATION LEVEL READ COMMITTED; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='1s'; SET LOCAL idle_in_transaction_session_timeout='30s'; SELECT " + quote(TUPLE) +
            "||jsonb_build_object('login',session_user,'current_user',current_user,'database',current_database(),'isolation',current_setting('transaction_isolation'),'pid',pg_backend_pid()::text,'xid',pg_current_xact_id()::text,'started',(SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()))::text;\n")
        line = self.queue.get(timeout=15)
        require(line.startswith(TUPLE), 'RUNTIME_TUPLE_INVALID')
        value = unique_json(line.removeprefix(TUPLE))
        require(type(value) is dict and set(value) == {'login', 'current_user', 'database', 'isolation', 'pid', 'xid', 'started'} and
            value['login'] == value['current_user'] == self.role and value['database'] == DATABASE and value['isolation'] == 'read committed' and
            all(type(value[key]) is str for key in ('pid', 'xid', 'started')) and re.fullmatch('[1-9][0-9]{0,9}', value['pid']) and
            re.fullmatch('[1-9][0-9]{0,19}', value['xid']) and len(value['started']) <= 64 and re.fullmatch(r'[0-9T:+. \-]+', value['started']), 'RUNTIME_TUPLE_INVALID')
        self.backend = value
        return value

    def call(self, text):
        token = 'WA_WORKER_COORDINATOR_ACK|' + secrets.token_hex(16)
        self.send(text + '\nSELECT ' + quote(token) + ';\n')
        lines, acknowledged = self.receive(token)
        if not acknowledged:
            self.process.wait(timeout=10)
            for reader in self.readers: reader.join(timeout=5)
        require(not self.invalid.is_set(), 'OPERATION_OUTPUT_LIMIT')
        return lines, acknowledged, ''.join(self.errors)

    def finish(self, text):
        require(text.rstrip().endswith(('COMMIT;', 'ROLLBACK;')), 'EXACT_TERMINAL_TRANSACTION_REQUIRED')
        lines, ack, errors = self.call(text)
        if self.process.poll() is None:
            self.send('\\q\n'); self.process.stdin.close(); self.process.wait(timeout=10)
        for reader in self.readers: reader.join(timeout=5)
        require(not self.invalid.is_set() and not any(reader.is_alive() for reader in self.readers), 'OPERATION_OUTPUT_INCOMPLETE')
        trailing = []
        while not self.queue.empty():
            line = self.queue.get_nowait()
            if line: trailing.append(line)
        require(not trailing, 'UNEXPECTED_TRAILING_OUTPUT')
        return self.process.returncode, lines, ack, ''.join(self.errors)

    def close(self):
        if self.process.poll() is None:
            try:
                if not self.process.stdin.closed: self.send('ROLLBACK;\n\\q\n'); self.process.stdin.close()
                self.process.wait(timeout=10)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                self.process.terminate()
                try: self.process.wait(timeout=10)
                except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(timeout=10)
        require(self.process.poll() is not None and self.backend is not None, 'OPERATION_CLOSURE_UNCONFIRMED')
        query = ("SELECT count(*) FROM pg_stat_activity WHERE pid=" + self.backend['pid'] + ' AND backend_start=' + quote(self.backend['started']) +
            "::timestamptz AND usename=" + quote(self.role) + ' AND datname=' + quote(DATABASE) + ';')
        require(self.raw('postgres', query).strip() == '0', 'OPERATION_BACKEND_STILL_LIVE')
        for reader in self.readers: reader.join(timeout=5)
        require(not any(reader.is_alive() for reader in self.readers), 'OPERATION_READER_STILL_LIVE')


def grant_sql(grant, backend, token_hash):
    require(backend['login'] == grant['database_login_role'] and backend['current_user'] == backend['login'] and
            re.fullmatch('[1-9][0-9]{0,9}', backend['pid']) and re.fullmatch('[1-9][0-9]{0,19}', backend['xid']) and
            re.fullmatch('[0-9a-f]{64}', token_hash), 'GRANT_RUNTIME_TUPLE_REQUIRED')
    fields = grant['allowed_fields']
    require(type(fields) is list and fields and fields == sorted(set(fields)) and len(fields) <= 1024 and
            all(type(field) is str and '*' not in field for field in fields), 'FINITE_EXACT_CAPABILITIES_REQUIRED')
    principal, service = grant.get('principal_user_id'), grant.get('service_principal')
    require((principal is None) != (service is None), 'EXACT_PRINCIPAL_KIND_REQUIRED')
    values = [quote(grant['id']), quote(token_hash), "'wa_context_issuer'", 'NULL' if principal is None else quote(principal),
        'NULL' if service is None else quote(service), quote(grant['database_login_role']), quote(grant['owner_module_id']),
        quote(grant['action']), quote(grant['purpose']), quote(grant['target_kind']), quote(grant['target_id']),
        'ARRAY[' + ','.join(quote(field) for field in fields) + ']::text[]', quote(grant.get('policy_version', 'worker-control-fixture.v1')),
        str(int(grant['security_generation'])), str(int(grant['source_generation'])), backend['pid'], quote(backend['xid']), "clock_timestamp()+interval '5 minutes'"]
    return 'INSERT INTO platform.database_action_grant (id,token_hash,issuer_service,principal_user_id,service_principal,database_login_role,owner_module_id,action,purpose,target_kind,target_id,allowed_fields,policy_version,security_generation,source_generation,backend_pid,transaction_id,expires_at) VALUES (' + ','.join(values) + ');\nCOMMIT;'


def remove_redundant_begin(text):
    matches = list(re.finditer(r'^BEGIN;\r?$', text, re.M))
    require(len(matches) == 1 and len(re.findall(r'^COMMIT;\r?$', text, re.M)) == 1 and text.rstrip().endswith('COMMIT;'), 'PACKET_TRANSACTION_WRAPPER_CHANGED')
    match = matches[0]
    return text[:match.start()] + text[match.end():]


def comparison_outcomes(values, expected):
    """Fixed minimized outcomes; never retain an arbitrary result dictionary."""
    allowed = {'model', 'exact_reverse', 'wrong_xid', 'visible_exact_work', 'revoked'}
    outcomes = []
    for index, wanted in enumerate(expected):
        require(type(wanted) is dict and set(wanted) <= allowed, 'UNREGISTERED_OUTPUT_EXPECTATION')
        actual = values[index] if index < len(values) else None
        item = {'object': type(actual) is dict, 'fields': type(actual) is dict and set(actual) == set(wanted), 'comparisons': {}, 'values': {}}
        for key, wanted_value in wanted.items():
            value = actual.get(key) if type(actual) is dict else None
            item['comparisons'][key] = canonical(value) == canonical(wanted_value)
            valid = (key == 'model' and value in MODELS) if type(value) is str else (key in ('exact_reverse', 'wrong_xid') and type(value) is bool) or (key in ('visible_exact_work', 'revoked') and type(value) is int and value in (0, 1))
            item['values'][key] = value if valid else None
        outcomes.append(item)
    return {'row_count_matches': len(values) == len(expected), 'rows': outcomes}


class Coordinator:
    def __init__(self, plan, packet, snapshot, api, host, evidence):
        self.plan, self.packet, self.snapshot, self.api, self.host, self.evidence = plan, packet, snapshot, api, host, evidence
        self.container = plan['immutable_container_id']; self.lease = None
        name = 'review-output/foundation-application.review.sql'
        self.application = self.source_text(name, packet['source_files_sha256'][name], 'CANONICAL_DIAGNOSTIC_SOURCE_DRIFT')

    def source_text(self, name, expected, code):
        # Hash exactly the bytes returned to the caller. A separate text read
        # could execute changed SQL between the approved load and a later use.
        raw = source_file(name).read_bytes()
        require(sha(raw) == expected, code)
        return raw.decode('utf8')

    def raw(self, role, text): return self.api['run'](role, text, self.container)

    def json(self, text, expected=None):
        value = unique_json(self.raw('postgres', text))
        if expected is not None: require(canonical(value) == canonical(expected), 'INDEPENDENT_OBSERVER_MISMATCH')
        return value

    def text(self, name):
        require(name in self.packet['prepared_files_sha256'], 'UNREVIEWED_PACKET_SQL_NAME')
        raw = packet_file(name).read_bytes()
        require(sha(raw) == self.packet['prepared_files_sha256'][name], 'WORKER_SQL_PACKET_DRIFT')
        return raw.decode('utf8')

    def observe(self, name, text, expected):
        self.evidence.stage('OBSERVE_' + name)
        value = self.json(text, expected)
        self.evidence.value['current'][name] = value; self.evidence.save()
        return value

    def guards(self):
        return self.observe('FIXTURE_GUARDS', self.text('fixture-guards-observe.sql'), {'owner_guards_reenabled': True, 'no_project_user_trigger_disabled': True})

    def native(self):
        self.evidence.stage('FRESH_NATIVE_PARITY')
        text = self.source_text(COLLECTOR, self.plan['source_modules_sha256'][COLLECTOR], 'WORKER_COLLECTOR_SOURCE_DRIFT')
        value = unique_json(self.raw('postgres', text))
        require(digest(value) == digest(self.snapshot), 'NATIVE_CATALOG_DRIFT')
        self.evidence.value['current']['native_catalog_unchanged'] = True; self.evidence.save()

    def resource(self):
        self.evidence.stage('EXACT_RESOURCE_PREFLIGHT')
        def inspect(args):
            raw = subprocess.check_output(['docker', '--context', 'desktop-linux', *args], text=True, timeout=30, shell=False)
            values = unique_json(raw); require(type(values) is list and len(values) == 1, 'RESOURCE_METADATA_SHAPE'); return values[0]
        context = inspect(['context', 'inspect', 'desktop-linux'])
        container = inspect(['inspect', self.container])
        volume = inspect(['volume', 'inspect', self.plan['target_manifest']['target']['volume_name']])
        image = inspect(['image', 'inspect', container.get('Image', '')])
        observed = self.host['inspect_live'](self.plan['target_manifest'], context, container, volume)
        require(observed['container_id'] == self.container, 'CREATED_CONTAINER_ID_MISMATCH')
        self.host['verify_image'](self.plan['target_manifest'], container, image)
        self.evidence.value['resource'] = {key: observed[key] for key in ('container_id', 'container_name', 'volume_name', 'image', 'network', 'published_ports', 'labels')}; self.evidence.save()

    def preflight(self):
        self.resource(); self.native()
        require(self.raw('postgres', "SELECT current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';").strip() == 't', 'SERVER_SETTINGS_REQUIRED')
        self.api['authentication_preflight'](self.evidence, self.container)
        self.evidence.stage('FINALIZATION_PREFLIGHT')
        require(self.raw('postgres', "SELECT count(*) FROM pg_auth_members WHERE roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole) AND member='wa_schema_owner'::regrole;").strip() == '0', 'TEMPORARY_AUTHORITY_REMAINS')
        require(self.raw('postgres', "SELECT bool_and(NOT has_schema_privilege(r,n,'CREATE')) FROM unnest(ARRAY['wa_private_helper_owner','wa_customer_verifier','wa_track_verifier']) r CROSS JOIN unnest(ARRAY['app','platform','platform_private']) n;").strip() == 't', 'LEAF_CREATE_REMAINS')
        self.guards()
        checks = []
        ids, source = self.packet['ids'], self.packet['source_customer']['ids']
        for table, column, values in (
            ('app.users', 'id', [source['user']]), ('app.user_security_profiles', 'user_id', [source['user']]),
            ('app.customer_profiles', 'id', [source['CustomerProfile']]), ('platform.runtime_outbox_message', 'command_receipt_id', [source['RuntimeCommandReceipt']]),
            ('platform.runtime_command_receipt', 'id', [source['RuntimeCommandReceipt'], ids['command']]),
            ('app.track_plans', 'id', [ids['plan']]), ('app.track_entitlement_definitions', 'id', [ids['definition']]),
            ('app.track_plan_entitlements', 'id', [ids['benefit']]), ('platform.runtime_work_item', 'id', [ids['work']]),
            ('app.track_subscriptions', 'id', [ids['subscription']]), ('app.track_base_selection', 'id', [ids['selection']]),
            ('app.track_entitlement_grants', 'id', [ids['grant']]), ('app.track_subscription_events', 'id', [ids['history']]),
            ('platform.runtime_effect_receipt', 'id', [ids['effect']]), ('platform.runtime_inbox_receipt', 'id', [ids['inbox']]),
            ('platform.runtime_attempt', 'id', [ids['attempt']]), ('app.customer_profile_lifecycle_event', 'id', [source['CustomerProfileLifecycleEvent']]),
            ('platform.owner_mutation_evidence', 'id', [source['OwnerMutationEvidence'], ids['subscription-evidence'], ids['selection-evidence'], ids['grant-evidence']]),
            ('platform_private.identity_service_receipt', 'id', [ids['identity-' + step] for step in ('bootstrap', 'rotate', 'revoke', 'recover')]),
            ('platform.database_action_grant', 'id', sorted({value['id'] for value in list(self.packet['grants'].values()) + list(self.packet['scenarios'][2]['grants'].values())})),
            ('app.track_enrollment_receipt', 'profile_id', [source['CustomerProfile']]),
            ('platform_private.identity_service_authorization', 'service_principal', [self.packet['fixture_values']['service_principal']])):
            checks.append('NOT EXISTS(SELECT 1 FROM ' + table + ' WHERE ' + column + ' IN (' + ','.join(quote(value) for value in values) + '))')
        require(self.raw('postgres', 'SELECT ' + ' AND '.join(checks) + ';').strip() == 't', 'FRESH_FIXTURE_NAMESPACE_REQUIRED')

    def operation(self, name, role, body, grant=None, *, expected_markers=(), expected_json=(), stale_bind=False, lease=False, before_finish=None):
        record = {'operation_closed': False, 'stage_markers': [], 'executed_sql_sha256': sha(body.encode('utf8'))}
        self.evidence.value['current_case'] = name; self.evidence.value['current'] = record; self.evidence.stage('OPEN_' + name)
        session = None; result = None; failure = None; failed_stage = None
        try:
            session = Session(role, self.container, self.api, self.raw)
            backend = session.capture()
            self.evidence.value['current']['actual_login_verified'] = True; self.evidence.save()
            if grant is not None:
                secret = secrets.token_hex(32)
                self.evidence.stage('ISSUE_' + name)
                self.issue(grant, backend, sha(bytes.fromhex(secret)))
                self.evidence.stage('BIND_' + name)
                lines, ack, errors = session.call('SELECT platform_private.bind_request_context(' + quote(secret) + ');')
                if stale_bind:
                    diagnostic = binder_diagnostic(errors, self.application)
                    exit_code = session.process.poll()
                    self.evidence.value['current']['diagnostic'] = diagnostic
                    self.evidence.value['current']['exit_code'] = exit_code
                    self.evidence.value['current']['acknowledgement'] = ack
                    self.evidence.save()
                    require(not ack and exit_code == 3 and not lines and diagnostic['matched'], 'INTENDED_BINDER_GUARD_NOT_PROVEN')
                    result = {'stale_bind_rejected': True}
                else: require(ack and not lines and not errors, 'CONTEXT_BIND_FAILED')
            require(not stale_bind or grant is not None, 'STALE_BIND_REQUIRES_ISSUANCE')
            if not stale_bind:
                if lease:
                    require(self.lease is not None, 'LEASE_PREIMAGE_REQUIRED')
                    lines, ack, errors = session.call('SET LOCAL wa.lease_secret=' + quote(self.lease) + ';')
                    require(ack and not lines and not errors, 'LEASE_GUC_FAILED')
                if before_finish is not None:
                    try: before_finish()
                    finally:
                        self.evidence.value['current_case'] = name; self.evidence.value['current'] = record; self.evidence.save()
                self.evidence.stage('EXECUTE_' + name)
                code, lines, acknowledged, errors = session.finish(body)
                markers = [line for line in lines if line.startswith('WA_')]
                values = [unique_json(line) for line in lines if not line.startswith('WA_')]
                self.evidence.value['current']['stage_markers'] = [marker for marker in markers if marker in expected_markers]
                self.evidence.value['current']['commit_or_rollback_acknowledged'] = acknowledged
                self.evidence.value['current']['output_comparisons'] = comparison_outcomes(values, expected_json)
                self.evidence.value['current']['exit_code'] = code
                if errors:
                    headers = [match for line in errors.splitlines() if (match := HEADER.fullmatch(line))]
                    states = {'42501', '42703', 'P0001', 'P0002', '23503', '23505', '23514', '22012', '25P02', '0A000', '57014'}
                    self.evidence.value['current']['unexpected_diagnostic'] = {'single_error_header': len(headers) == 1,
                        'sqlstate': headers[0][1] if len(headers) == 1 and headers[0][1] in states else None,
                        'classification': 'UNEXPECTED_NOT_GUARD_PROOF', 'source_metadata': self.api['source_metadata'](errors)}
                self.evidence.save()
                require(code == 0 and acknowledged and not errors, 'UNEXPECTED_OPERATION_RESULT')
                require(markers == list(expected_markers) and canonical(values) == canonical(list(expected_json)), 'EXACT_STAGE_OR_RESULT_MISMATCH')
                result = {'markers': markers, 'comparisons': values, 'transaction': dict(backend)}
        except (Exception, KeyboardInterrupt) as error:
            failure, failed_stage = error, self.evidence.value['current_stage']
        finally:
            self.evidence.value['current_case'] = name; self.evidence.value['current'] = record
            self.evidence.stage('CLOSE_' + name)
            if session is not None:
                try: session.close(); self.evidence.value['current']['operation_closed'] = True
                except Exception:
                    self.evidence.value['current']['closure_failure'] = 'UNCONFIRMED'
                    failure = HeldFailure('OPERATION_CLOSURE_UNCONFIRMED'); failed_stage = 'CLOSE_' + name
            self.evidence.value['operations'].append({'name': name, 'login': role,
                'status': 'EXPECTED_BIND_REJECT' if result is not None and stale_bind else 'SQL_COMPLETED' if result is not None else 'STOPPED',
                'failure_code': failure.code if isinstance(failure, HeldFailure) else 'UNEXPECTED_EXCEPTION' if failure is not None else None,
                'failure_stage': failed_stage,
                **deepcopy(record)})
            self.evidence.save()
        if failure is not None:
            self.evidence.stage(failed_stage); raise failure
        return result

    def issue(self, grant, backend, token_hash):
        # Separate actual issuer COMMIT and closure complete before consumer bind.
        issuer = Session('wa_context_issuer', self.container, self.api, self.raw)
        try:
            issuer.capture()
            code, lines, ack, errors = issuer.finish(grant_sql(grant, backend, token_hash))
            require(code == 0 and ack and not lines and not errors, 'ISSUER_COMMIT_NOT_PROVEN')
        finally: issuer.close()

    def trusted(self, name, filename, role='postgres'):
        text = remove_redundant_begin(self.text(filename))
        try:
            result = self.operation(name, role, text)
        except (Exception, KeyboardInterrupt):
            failed_stage = self.evidence.value['current_stage']
            if self.evidence.value['current'].get('operation_closed'): self.guards()
            self.evidence.stage(failed_stage)
            raise
        self.guards()
        return result

    def fingerprint(self):
        value = self.json(self.text('catalog-usage-fingerprint.sql'))
        tables = {'app.track_plans', 'app.track_entitlement_definitions', 'app.track_plan_entitlements',
                  'app.track_usage_events', 'app.track_usage_counters', 'app.track_usage_reservation'}
        require(type(value) is dict and set(value) == tables and all(type(row) is dict and set(row) == {'count', 'sha256'} and
            type(row['count']) is int and row['count'] >= 0 and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) for row in value.values()), 'FINGERPRINT_SHAPE_INVALID')
        return value

    def record(self, name, status):
        self.evidence.value['results'].append({'component': name, 'status': status, **deepcopy(self.evidence.value['current'])})
        self.evidence.save()

    def source_observe(self, enrolled=False):
        expected = deepcopy(self.packet['source_customer']['observer_expected']); expected['track_enrollments'] = int(enrolled)
        self.observe('SOURCE_CUSTOMER', self.text('source-customer-observe.sql'), expected)

    def work_witness(self, stage, backend):
        ids = self.packet['ids']; expected = {'scheduled': ('pending', 0, 0), 'claimed': ('leased', 1, 1)}[stage]
        state, fence, attempts = expected
        text = ("SELECT jsonb_build_object('exact_work_state',EXISTS(SELECT 1 FROM platform.runtime_work_item WHERE id=" + quote(ids['work']) + ' AND state=' + quote(state) +
            ' AND fence=' + str(fence) + ' AND attempt_count=' + str(attempts) + ' AND effect_receipt_id IS NULL AND mutation_transaction_id=' + quote(backend['xid']) + ")) ;")
        self.observe('WORK_' + stage.upper(), text, {'exact_work_state': True})

    def identity_observe(self, generation, revoked):
        return self.observe('IDENTITY_CURRENTNESS', self.text('identity-currentness-observe.sql'),
            {'service_rows': 1, 'generation': generation, 'revoked': revoked, 'exact_receipt_link': True})

    def complete_state(self):
        self.observe('WORKER_COMPLETE_STATE', self.text('enroll-observe.sql'), self.packet['positive_observer_expected'])
        self.source_observe(True); self.guards(); self.native()
        current = self.fingerprint()
        require(canonical(current) == canonical(self.baseline_catalog_usage), 'CATALOG_OR_USAGE_CHANGED')
        self.evidence.value['current']['catalog_and_usage_unchanged'] = True; self.evidence.save()

    def read_control(self, name, *, expected=1, stale_bind=False, transition=None):
        scenario = self.packet['scenarios'][2]
        grant = scenario['grants'][name]
        result = self.operation('currentness-' + name, 'wa_worker', self.text('currentness-read.sql') + '\nROLLBACK;', grant,
            stale_bind=stale_bind, expected_json=() if stale_bind else ({'visible_exact_work': expected},), before_finish=transition)
        self.complete_state()
        self.record('currentness-' + name, 'PASS_PREPARED_SQL_SCOPE_ONLY')
        return result

    def run(self):
        self.preflight()
        self.trusted('independent-fixtures', 'independent-fixtures.sql')
        self.native()
        self.baseline_catalog_usage = self.fingerprint()
        self.evidence.value['catalog_usage_baseline'] = self.baseline_catalog_usage; self.evidence.save()
        source = self.operation('source-customer', 'wa_app_runtime', self.text('source-customer.sql'), self.packet['grants']['source_customer'], expected_markers=('WA_CUSTOMER_CONTROL_READY_TO_COMMIT',))
        self.source_observe()
        self.observe('SOURCE_TRANSACTION', "SELECT jsonb_build_object('source_uses_captured_transaction',EXISTS(SELECT 1 FROM app.customer_profiles WHERE id=" +
            quote(self.packet['source_customer']['ids']['CustomerProfile']) + ' AND mutation_transaction_id=' + quote(source['transaction']['xid']) + '));', {'source_uses_captured_transaction': True})
        self.record('restricted-Customer-source-creation', 'PASS_COMPONENT_ONLY')
        self.trusted('identity-bootstrap', 'identity-bootstrap.sql', 'wa_identity_service_authority'); self.identity_observe(0, False)
        scheduled = self.operation('schedule', 'wa_app_runtime', self.text('schedule.sql'), self.packet['grants']['schedule'], expected_markers=('WA_WORKER_SCHEDULE_READY',))
        self.work_witness('scheduled', scheduled['transaction']); self.record('actual-app-schedule', 'PASS_COMPONENT_ONLY')
        self.lease = secrets.token_hex(32)
        claimed = self.operation('claim', 'wa_worker', self.text('claim.sql'), self.packet['grants']['claim'], lease=True, expected_markers=('WA_WORKER_CLAIM_READY',))
        self.work_witness('claimed', claimed['transaction']); self.record('actual-worker-claim', 'PASS_COMPONENT_ONLY')
        text = self.text('enroll.sql'); require(text.count('SET CONSTRAINTS ALL IMMEDIATE;') == 1, 'CONSTRAINT_INSERTION_POINT_CHANGED')
        text = text.replace('SET CONSTRAINTS ALL IMMEDIATE;', self.text('in-transaction-reverse-probes.sql') + '\nSET CONSTRAINTS ALL IMMEDIATE;')
        expected = [{'model': model, 'exact_reverse': True, 'wrong_xid': False} for model in MODELS]
        processed = self.operation('worker-enroll', 'wa_worker', text, self.packet['grants']['process'], lease=True,
            expected_markers=('WA_WORKER_EFFECT_LINKED', 'WA_WORKER_GROUP_STAGED', 'WA_WORKER_CONSTRAINTS_CHECKED'), expected_json=expected)
        self.complete_state()
        self.observe('WORKER_TRANSACTION', "SELECT jsonb_build_object('worker_uses_captured_transaction',EXISTS(SELECT 1 FROM platform.runtime_command_receipt WHERE id=" +
            quote(self.packet['ids']['command']) + ' AND mutation_transaction_id=' + quote(processed['transaction']['xid']) + '));', {'worker_uses_captured_transaction': True})
        self.record(NAMES[0], 'PASS_PREPARED_SQL_SCOPE_ONLY'); self.record(NAMES[1], 'PASS_THREE_REVERSE_BRANCHES_ONLY')
        self.lease = None
        self.read_control('baseline-current')
        def rotate(): self.trusted('identity-rotate', 'identity-rotate.sql', 'wa_identity_service_authority')
        self.read_control('bound-before-rotate', expected=0, transition=rotate); self.identity_observe(1, False)
        self.read_control('old-after-rotate', stale_bind=True); self.read_control('fresh-after-rotate')
        def revoke(): self.trusted('identity-revoke', 'identity-revoke.sql', 'wa_identity_service_authority')
        self.read_control('bound-before-revoke', expected=0, transition=revoke); self.identity_observe(2, True)
        self.read_control('revoked-current-generation', stale_bind=True)
        self.trusted('identity-recover', 'identity-recover.sql', 'wa_identity_service_authority'); self.identity_observe(3, False)
        self.read_control('old-after-recover', stale_bind=True); self.read_control('fresh-after-recover')
        self.record(NAMES[2], 'PASS_READONLY_WORK_SERVICE_CURRENTNESS_ONLY')
        grant = self.packet['scenarios'][3]['grant']
        def revoke_grant():
            body = "WITH revoked AS (UPDATE platform.database_action_grant SET revoked_at=clock_timestamp() WHERE id=" + quote(grant['id']) + " AND issuer_service=session_user::text AND revoked_at IS NULL RETURNING 1) SELECT jsonb_build_object('revoked',count(*)) FROM revoked;\nCOMMIT;"
            self.operation('issuer-revoke', 'wa_context_issuer', body, expected_json=({'revoked': 1},))
        self.operation('bound-before-issuer-revoke', 'wa_worker', self.text('currentness-read.sql') + '\nROLLBACK;', grant,
            expected_json=({'visible_exact_work': 0},), before_finish=revoke_grant)
        self.complete_state(); self.record(NAMES[3], 'PASS_READONLY_WORK_GRANT_REVOCATION_ONLY')
        self.evidence.value['status'] = 'PREPARED_FINITE_SUBSET_COMPLETED_NOT_FULL_CONTROL_QUALIFICATION'
        self.evidence.stage('FINITE_WORKER_SUBSET_COMPLETE')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-reviewed-worker-controls', action='store_true')
    parser.add_argument('--run-plan', type=Path)
    parser.add_argument('--evidence-directory', type=Path)
    args = parser.parse_args(argv)
    if not args.execute_reviewed_worker_controls: parser.error('EXECUTION HELD: explicit reviewed worker run plan required; no process call performed')
    if args.run_plan is None or args.evidence_directory is None: parser.error('external run plan and fresh external evidence directory are required')
    evidence = None
    try:
        raw = (PACKET / 'fixtures.json').read_bytes()
        require(sha(raw) == PACKET_SHA256, 'WORKER_PACKET_DRIFT')
        seed = unique_json(raw.decode('utf8'))
        evidence = Evidence(external_file(args.evidence_directory), seed)
        evidence.stage('VERIFY_REVIEWED_INPUTS')
        plan = unique_json(external_file(args.run_plan).read_text(encoding='utf8'))
        packet, native, api, host = load_inputs(plan)
        coordinator = Coordinator(plan, packet, native, api, host, evidence)
        coordinator.run()
        return 0
    except (Exception, KeyboardInterrupt) as error:
        if evidence is not None:
            evidence.value.update(status='STOPPED_UNEXPECTED_RESULT', subsequent_cases_stopped=True,
                failure={'class': 'HELD_FAILURE' if isinstance(error, HeldFailure) else 'UNEXPECTED_EXCEPTION',
                         'code': error.code if isinstance(error, HeldFailure) else 'UNEXPECTED_EXCEPTION', 'stage': evidence.value['current_stage']})
            evidence.save()
        else:
            print(json.dumps({'status': 'HELD_BEFORE_RUNTIME', 'failure': 'SOURCE_PLAN_OR_FRESH_EVIDENCE_PATH_REQUIRED'}))
        return 2


if __name__ == '__main__': raise SystemExit(main())
