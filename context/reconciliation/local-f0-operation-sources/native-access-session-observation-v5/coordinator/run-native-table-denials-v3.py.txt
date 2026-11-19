"""Dormant finite native-DENY coordinator. No resource/credential provisioning.

Import/help use stdlib only. Runtime requires an independently approved external
plan, exact source/helper/packet pins, a source-qualified native PASS snapshot,
and already provisioned authenticated local roles on one owned immutable ID.
"""
import argparse
from copy import deepcopy
import hashlib
import ipaddress
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
PACKET = ROOT / 'review-output/native-table-denials-v2'
PACKET_SHA = '8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
EXPECTED_SOURCE = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
DATABASE = 'wa_p0c_rehearsal'
API = 'scripts/sql-review/run-first-rehearsal.py'
HOST = 'scripts/sql-review/run-local-f0-migrate.py'
COLLECTOR = 'scripts/sql-review/collect_native_catalog.sql'
MODULES = ('scripts/sql-review/run-native-table-denials-v3.py', API, HOST, COLLECTOR,
           'scripts/sql-review/rehearsal-diagnostics.py', 'scripts/prepare-local-f0-history.py',
           'review-output/first-rehearsal/diagnostic-identifiers.json')
PROVIDERS = ('anon', 'authenticated', 'service_role')
PROBES = (*PROVIDERS, 'wa_app_runtime', 'wa_worker', 'wa_context_issuer')
AUTH_ROLES = ('postgres', 'wa_migrator', 'wa_context_issuer', 'wa_identity_service_authority', 'wa_app_runtime', 'wa_worker', *PROVIDERS)
HEADER = re.compile(r'(?:psql:<stdin>:[1-9][0-9]*: )?ERROR:\s+([0-9A-Z]{5}):\s+(.*)')
LOCATION = re.compile(r'LOCATION:\s+(aclcheck_error|aclcheck_error_col), aclchk\.c:([1-9][0-9]{0,5})')
PRIMARY_RULE = 'https://raw.githubusercontent.com/postgres/postgres/REL_17_11/src/backend/catalog/aclchk.c'
TUPLE = 'WA_NATIVE_DENY_TUPLE|'


class HeldFailure(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)


def need(value, code):
    if not value: raise HeldFailure(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)
def digest(value): return sha(canonical(value).encode())
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def ident(value): return '"' + value.replace('"', '""') + '"'
def table(value): return '.'.join(ident(part) for part in value.split('.'))


def native_pass_counts(value):
    return (type(value) is dict and 'PASS' in value and set(value) <= {'PASS', 'FAIL', 'INCOMPLETE'} and
            all(type(count) is int for count in value.values()) and value['PASS'] > 0 and
            value.get('FAIL', 0) == value.get('INCOMPLETE', 0) == 0)


def unique_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'DUPLICATE_JSON_KEY'); result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))


def source_path(relative):
    need(type(relative) is str and '\\' not in relative and not Path(relative).is_absolute() and all(p not in ('', '.', '..') for p in relative.split('/')), 'SOURCE_PATH')
    path = (ROOT / relative).resolve(); need(path.is_relative_to(ROOT), 'SOURCE_PATH'); return path


def external_path(value):
    path = Path(value); need(path.is_absolute(), 'EXTERNAL_ABSOLUTE_PATH')
    path = path.resolve(); need(path.is_relative_to(TASK) and not path.is_relative_to(ROOT), 'EXTERNAL_TASK_PATH'); return path


def clean_text(value):
    value = value.replace('\r\n', '\n')
    return value if all(c in ('\n', '\t') or c.isprintable() for c in value) else None


def source_position_matches(position, caret, sql):
    """Exact ASCII libpq17.11 reportErrorPosition projection, never raw evidence.

    REL_17_11 fe-protocol3.c: DISPLAY_SIZE=60/MIN_RIGHT_CUT=10. All pinned
    probe DML is ASCII without tabs. Unsupported rendering fails closed.
    """
    match = re.fullmatch(r'LINE ([1-9][0-9]{0,3}): (.*)', position)
    if not match or int(match[1]) > len(sql.splitlines()) + 1 or not re.fullmatch(r' *\^', caret): return False
    prefix = 'LINE ' + match[1] + ': '
    for line in sql.splitlines():
        if not re.match(r'^(SELECT|INSERT|UPDATE|DELETE)\b', line) or not line.isascii() or '\t' in line: continue
        for cursor in range(len(line) + 1):
            start, end = 0, len(line)
            if end > 60:
                if 60 >= cursor + 10: end = 60
                else: end = min(end, cursor + 10); start = max(0, end - 60)
            left, right = '...' if start else '', '...' if end < len(line) else ''
            if match[2] == left + line[start:end] + right and caret == ' ' * (len(prefix) + len(left) + cursor - start) + '^': return True
    return False


def native_diagnostic(stderr, case, metadata, sql=''):
    """Fixed native PG17.11 messages + C location; no trigger/code-only passes.

    The message templates and routines are source-bound in REL_17_11 aclchk.c.
    Column denial is about the observed referenced column, not isolation of the
    generator's selected forbidden column. Earlier schema/table gates may win.
    """
    text = clean_text(stderr)
    result = {'matched': False, 'sqlstate': None, 'observed_gate': None, 'native_location': None,
              'native_object': None, 'native_column': None, 'source_position_verified': False, 'selected_column_isolation_claimed': False}
    if text is None: return result
    lines = [line for line in text.split('\n') if line]
    headers = [m for line in lines if (m := HEADER.fullmatch(line))]
    severities = [line for line in lines if re.search(r'\b(?:ERROR|FATAL|PANIC)\b', line)]
    locations = [m for line in lines if (m := LOCATION.fullmatch(line))]
    if len(headers) != 1 or len(severities) != 1 or len(locations) != 1 or headers[0][1] != '42501': return result
    # A parser/native ACL failure may include libpq's exact pinned-source
    # LINE/caret projection. Never accept arbitrary body/frame/detail output.
    if len(lines) == 4:
        if not HEADER.fullmatch(lines[0]) or not LOCATION.fullmatch(lines[-1]) or not source_position_matches(lines[1], lines[2], sql): return result
        result['source_position_verified'] = True
    elif len(lines) != 2 or not HEADER.fullmatch(lines[0]) or not LOCATION.fullmatch(lines[-1]): return result
    schema, relation = case['table'].split('.')
    message, routine = headers[0][2], locations[0][1]
    if message == 'permission denied for schema ' + schema and routine == 'aclcheck_error' and metadata['schema_usage'] is False:
        gate, object_, column = 'SCHEMA', schema, None
    elif message == 'permission denied for table ' + relation and routine == 'aclcheck_error' and metadata['schema_usage'] is True and metadata['required_permission_missing'] is True:
        gate, object_, column = 'TABLE', case['table'], None
    else:
        match = re.fullmatch(r'permission denied for column "([a-z_][a-z_0-9]*)" of relation "' + re.escape(relation) + '"', message)
        if not (match and routine == 'aclcheck_error_col' and metadata['schema_usage'] is True and match[1] in metadata['missing_referenced_columns']): return result
        gate, object_, column = 'COLUMN', case['table'], match[1]
    return {**result, 'matched': True, 'sqlstate': '42501', 'observed_gate': gate, 'native_location': routine + '@aclchk.c', 'native_object': object_, 'native_column': column}


def unexpected_operation_metadata(stderr, native, application_sha, metadata=None, declared=None):
    """Pure diagnostic projection only; no return value can qualify a verdict.

    Native identifiers come solely from the previously full-comparator-approved
    snapshot, with constraint/column-to-relation association. Primary messages,
    DETAIL/HINT/SQL/positions and C locations are never projected. Optional
    source_metadata frames must also match the cached declaration and native
    no-argument function identity/body. Unknown values become fixed classes.
    """
    result = {'classification': 'UNRECOGNIZED', 'sqlstate': None,
              'identifier_classification': 'NOT_RETAINED', 'frame_classification': 'NOT_RETAINED'}
    if type(stderr) is not str or len(stderr) > 16384:
        result['classification'] = 'OUTPUT_LIMIT_OR_TYPE'; return result
    text = clean_text(stderr)
    if text is None:
        result['classification'] = 'CONTROL_CHARACTERS'; return result
    lines = [line for line in text.split('\n') if line]
    if len(lines) > 128 or any(len(line) > 2048 for line in lines):
        result['classification'] = 'OUTPUT_LIMIT_OR_TYPE'; return result
    header = re.compile(r'(?:psql:<stdin>:[1-9][0-9]{0,5}: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+.+')
    headers = [match for line in lines if (match := header.fullmatch(line))]
    # Count severity/header shapes, not bare words in discarded row DETAIL.
    # Include malformed line-start headers and a second verbose header even
    # when appended to the same physical line as the first primary message.
    severities = {match.start('severity') for match in re.finditer(
        r'(?m)^(?:psql:<stdin>:[1-9][0-9]{0,5}: )?(?P<severity>ERROR|FATAL|PANIC)(?::|\s|$)', text)}
    severities.update(match.start('severity') for match in re.finditer(r'\b(?P<severity>ERROR|FATAL|PANIC):\s+[0-9A-Z]{5}:', text))
    if len(headers) != 1 or len(severities) != 1 or not lines or not header.fullmatch(lines[0]):
        result['classification'] = 'NO_SINGLE_VALID_ERROR'; return result
    state = headers[0][1]
    # A single exact five-character state is safe observation for any error,
    # including input/datatype/syntax errors. It is never a negative verdict.
    result.update(classification='SQLSTATE_ONLY', sqlstate=state)
    identifier = r'[a-z_][a-z0-9_]{0,62}'
    fields = {}
    for label in ('SCHEMA', 'TABLE', 'COLUMN', 'CONSTRAINT'):
        candidates = [line for line in lines if line.startswith(label + ' NAME:')]
        match = re.fullmatch(label + r' NAME:\s+(' + identifier + ')', candidates[0]) if len(candidates) == 1 else None
        if candidates and not match:
            result['identifier_classification'] = 'REDACTED_IDENTIFIERS'; break
        if match: fields[label] = match[1]
    else:
        relations = {row['object'] for row in native.get('relations', []) if type(row) is dict and
                     type(row.get('object')) is str and re.fullmatch(identifier + r'\.' + identifier, row['object']) and row.get('kind') == 'r'}
        relation = fields.get('SCHEMA', '') + '.' + fields.get('TABLE', '')
        if fields:
            result['identifier_classification'] = 'REDACTED_IDENTIFIERS'
            associated = relation in relations
            if 'COLUMN' in fields:
                associated = associated and any(type(row) is dict and row.get('table_name') == relation and row.get('name') == fields['COLUMN']
                    and (state != '23502' or row.get('nullable') is False) for row in native.get('columns', []))
            if 'CONSTRAINT' in fields:
                kinds = {'23514': {'c'}, '23503': {'f'}, '23505': {'p', 'u'}}.get(state, set())
                associated = associated and any(type(row) is dict and row.get('table_name') == relation and row.get('name') == fields['CONSTRAINT']
                    and row.get('kind') in kinds and re.fullmatch(identifier, row['name']) for row in native.get('constraints', []))
            useful = ('CONSTRAINT' in fields and state in {'23514', '23503', '23505'}) or ('COLUMN' in fields and state == '23502')
            if associated and useful:
                result.update(classification='NATIVE_IDENTIFIER_METADATA', identifier_classification='SOURCE_KNOWN_ASSOCIATION', native_object=relation)
                if 'COLUMN' in fields: result['native_column'] = fields['COLUMN']
                if 'CONSTRAINT' in fields: result['native_constraint'] = fields['CONSTRAINT']
    # The helper's return dictionary is untrusted at this retention boundary.
    # Check the complete allowed shape before copying a single frame field.
    if any('CONTEXT:' in line or 'PL/pgSQL function ' in line for line in lines):
        result['frame_classification'] = 'REDACTED_CONTEXT'
    if type(metadata) is not dict or type(declared) is not dict: return result
    base = {'classification', 'frame_classification'}
    classification = metadata.get('classification')
    if type(classification) is not str: return result
    if classification == 'RECORD_FIELD_MISSING': base |= {'record_alias', 'column', 'source_sha256'}
    elif classification not in {'UNRECOGNIZED', 'RECORD_FIELD_MISSING_REDACTED'}: return result
    if metadata.get('frame_classification') != 'SOURCE_BOUND_FRAME' or set(metadata) != base | {'frame'}: return result
    canonical_sha = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
    if application_sha != canonical_sha or declared.get('source') != 'review-output/foundation-application.review.sql' or declared.get('source_sha256') != canonical_sha: return result
    if classification == 'RECORD_FIELD_MISSING' and (metadata['record_alias'] not in ('new', 'old') or type(metadata['column']) is not str or
            metadata['column'] not in declared.get('columns', []) or metadata['source_sha256'] != canonical_sha): return result
    frame = metadata.get('frame')
    if type(frame) is not dict or set(frame) != {'schema', 'function', 'body_line', 'body_sha256', 'source_sha256'}: return result
    if not all(type(frame[key]) is str and re.fullmatch(identifier, frame[key]) for key in ('schema', 'function')): return result
    frame_lines = [line for line in lines if 'PL/pgSQL function ' in line]
    frame_pattern = r'(?:CONTEXT:\s+|\s*)PL/pgSQL function (' + identifier + r')\.(' + identifier + r')\(\) line ([1-9][0-9]{0,3}) at (IF|assignment|RETURN|SQL statement|PERFORM|RAISE)'
    actual_frame = re.fullmatch(frame_pattern, frame_lines[0]) if len(frame_lines) == 1 else None
    if not actual_frame or (actual_frame[1], actual_frame[2], int(actual_frame[3])) != (frame['schema'], frame['function'], frame['body_line']): return result
    name = frame['schema'] + '.' + frame['function']
    functions = declared.get('no_argument_plpgsql_functions')
    known = functions.get(name) if type(functions) is dict else None
    if type(known) is not dict or set(known) != {'schema', 'function', 'body_sha256', 'max_body_line'}: return result
    if (known['schema'] != frame['schema'] or known['function'] != frame['function'] or type(known['max_body_line']) is not int or
            not 1 <= known['max_body_line'] <= 9999 or type(frame['body_line']) is not int or not 1 <= frame['body_line'] <= known['max_body_line'] or
            type(frame['body_sha256']) is not str or not re.fullmatch('[0-9a-f]{64}', frame['body_sha256']) or
            known['body_sha256'] != frame['body_sha256'] or frame['source_sha256'] != canonical_sha): return result
    matches = [row for row in native.get('functions', []) if type(row) is dict and row.get('name') == name and row.get('object') == name + '()' and
               row.get('kind') == 'f' and row.get('language') == 'plpgsql' and row.get('parameters') == [] and row.get('body_sha256') == frame['body_sha256']]
    if len(matches) == 1:
        result.update(frame_classification='SOURCE_BOUND_FRAME', frame={key: frame[key] for key in ('schema', 'function', 'body_line', 'body_sha256', 'source_sha256')})
    return result


def output_matches(lines, expected):
    if type(lines) is not list or type(expected) is not list or len(lines) != len(expected): return False
    for actual, wanted in zip(lines, expected):
        if type(wanted) is str:
            if actual != wanted: return False
        else:
            try:
                if canonical(unique_json(actual)) != canonical(wanted): return False
            except (ValueError, HeldFailure): return False
    return True


def execute_verified_helpers(modules):
    """Compile only cached prehashed bytes, including nested helper imports."""
    original = runpy.run_path
    def load(path, *args, **kwargs):
        resolved = Path(path).resolve()
        matches = [name for name in modules if source_path(name) == resolved]
        need(len(matches) == 1 and matches[0].endswith('.py'), 'UNREVIEWED_HELPER_IMPORT')
        namespace = {'__file__': str(resolved), '__name__': '<native-deny-verified-helper>'}
        exec(compile(modules[matches[0]], str(resolved), 'exec'), namespace)
        return namespace
    try:
        runpy.run_path = load
        return load(source_path(API)), load(source_path(HOST))
    finally: runpy.run_path = original


def packet_sql(packet, name, blobs):
    need(name in packet['files_sha256'] and name in blobs, 'UNREVIEWED_PACKET_FILE'); return blobs[name].decode('utf8')


def captured_tail(text):
    # capture() already opens the real transaction. Remove only the first exact
    # reviewed BEGIN; all remaining source SQL bytes are preserved in order.
    match = re.match(r'(?:(?:--[^\n]*\n)|\s)*BEGIN;', text)
    need(match is not None, 'INITIAL_BEGIN_REQUIRED')
    begin = text.rfind('BEGIN;', 0, match.end())
    return text[:begin] + text[begin + len('BEGIN;'):]


def provider_flags():
    return [{'name': role, 'login': True, 'inherit': False, 'superuser': False, 'createdb': False, 'createrole': False,
             'replication': False, 'bypassrls': role == 'service_role', 'memberships': 0, 'connect': True, 'create': False, 'temp': False} for role in PROVIDERS]


def load_inputs(plan):
    fields = {'schema', 'scope', 'run_id', 'source_commit', 'source_tree', 'packet_sha256', 'source_modules_sha256',
              'target_manifest', 'immutable_container_id', 'native_snapshot', 'native_comparison', 'provider_preinstall_proof', 'selected_case_ids'}
    need(type(plan) is dict and set(plan) == fields and plan['schema'] == 'workinants.native-deny-run.v1' and plan['scope'] == 'FINITE_NATIVE_DENIAL_FACETS_ONLY', 'PLAN_SCOPE')
    need(re.fullmatch('[0-9a-f-]{36}', plan['run_id']) and re.fullmatch('[0-9a-f]{40}', plan['source_commit']) and re.fullmatch('[0-9a-f]{40}', plan['source_tree']) and re.fullmatch('[0-9a-f]{64}', plan['immutable_container_id']), 'PLAN_IDENTITY')
    need(plan['packet_sha256'] == PACKET_SHA, 'REVIEWED_NATIVE_PACKET_REQUIRED')
    pins = plan['source_modules_sha256']; need(type(pins) is dict and set(pins) == set(MODULES), 'HELPER_PIN_SET')
    modules = {name: source_path(name).read_bytes() for name in MODULES}
    need(all(sha(raw) == pins[name] for name, raw in modules.items()), 'HELPER_SOURCE_DRIFT')
    raw = (PACKET / 'packet.json').read_bytes(); need(sha(raw) == PACKET_SHA, 'PACKET_SOURCE_DRIFT'); packet = unique_json(raw)
    need(packet['schema'] == 'workinants.native-table-denials.v1' and packet['selected_count'] == 40 and len(packet['cases']) == 40 and
         len(packet['files_sha256']) == 83 and len(packet['preparation_blocks']) == 4 and packet['expected_native_catalog_sha256'] == EXPECTED_SOURCE, 'PACKET_BOUNDS')
    need(plan['selected_case_ids'] == packet['selected_case_ids'] == [case['id'] for case in packet['cases']] and
         all(case['status'] == 'NOT_RUN' and len(case['probes']) == 24 and all(probe['status'] == 'NOT_RUN' for probe in case['probes']) for case in packet['cases']), 'EXACT_FORTY_CASES_REQUIRED')
    inputs = {path: source_path(path).read_bytes() for path in packet['source_inputs_sha256']}
    for path, expected in packet['source_inputs_sha256'].items(): need(sha(inputs[path]) == expected, 'PACKET_INPUT_DRIFT')
    blobs = {}
    for name, expected in packet['files_sha256'].items():
        need(Path(name).name == name and name.endswith('.sql'), 'PACKET_SQL_NAME')
        raw = (PACKET / name).read_bytes(); need(sha(raw) == expected, 'PACKET_SQL_DRIFT'); blobs[name] = raw
    documents = {}
    for name in ('native_snapshot', 'native_comparison', 'provider_preinstall_proof'):
        item = plan[name]; need(type(item) is dict and set(item) == {'path', 'sha256'}, 'REVIEW_ASSET_FIELDS')
        raw = external_path(item['path']).read_bytes(); need(sha(raw) == item['sha256'], 'REVIEW_ASSET_DRIFT'); documents[name] = unique_json(raw)
    native, report, provider = [documents[key] for key in ('native_snapshot', 'native_comparison', 'provider_preinstall_proof')]
    need(native.get('format') == 'workinants.native-catalog.v1' and type(native.get('server_version_num')) is int and native['server_version_num'] == 170011 and
         native.get('read_only') is True and native.get('collected_as') == 'postgres' and native.get('collector_is_superuser') is True, 'NATIVE_SNAPSHOT_REQUIRED')
    need(report.get('format') == 'workinants.catalog-comparison.v1' and report.get('status') == 'PASS' and report.get('source_expected_sha256') == EXPECTED_SOURCE and
         report.get('native_snapshot_sha256') == digest(native) and native_pass_counts(report.get('check_counts')) and report.get('findings') == [], 'FULL_NATIVE_PARITY_PASS_REQUIRED')
    sql_sha = packet['source_inputs_sha256']['review-output/foundation-application.review.sql']
    wanted = {'schema': 'workinants.native-deny-provider-preinstall.v1', 'run_id': plan['run_id'], 'container_id': plan['immutable_container_id'],
        'source_commit': plan['source_commit'], 'source_tree': plan['source_tree'], 'packet_sha256': PACKET_SHA, 'application_sql_sha256': sql_sha,
        'roles': provider_flags(), 'all_nine_schema_usage_sentinels_before_install': True, 'canonical_install_removed_all_nine': True,
        'genuine_prisma_one_applied_migration': True, 'original_grantor_finalized': True, 'local_simulation_only': True, 'hosted_parity_claimed': False}
    need(canonical(provider) == canonical(wanted), 'PROVIDER_PREINSTALL_SOURCE_PROOF_REQUIRED')
    # Every helper-chain, packet, source input and independently reviewed native
    # proof is verified above using stdlib only, before helper code can execute.
    api, host = execute_verified_helpers(modules)
    host['validate_manifest'](plan['target_manifest'])
    need(plan['target_manifest']['run_id'] == plan['run_id'] and plan['target_manifest']['source']['integrated_sql_sha256'] == sql_sha, 'TARGET_SOURCE_IDENTITY')
    blobs['__models'] = inputs['context/reconciliation/foundation-sql-draft-models.json']; blobs['__collector'] = modules[COLLECTOR]
    blobs['__diagnostic_identifiers'] = modules['review-output/first-rehearsal/diagnostic-identifiers.json']
    return packet, blobs, native, api, host


class Evidence:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=False); self.path = directory / 'native-denial-results.json'
        self.value = {'schema': 'workinants.native-denial-evidence.v1', 'status': 'IN_PROGRESS', 'database_posture': 'D', 'current_stage': 'ENTRY',
                      'current_case': None, 'current_probe': None, 'current': {}, 'operations': [], 'native_controls': [], 'facets': [], 'authentication': [],
                      'selected_cases': [], 'source_packet_sha256': PACKET_SHA, 'cleanup_required': True, 'subsequent_cases_stopped': False,
                      'coverage_limit': 'Observed native gates/RLS emptiness and synthetic native validity only; no whole DENY/ALLOW/94/451 or owner qualification.'}
        self.save()

    def save(self):
        temporary = self.path.with_suffix('.tmp')
        with temporary.open('w', encoding='utf8', newline='\n') as handle:
            handle.write(json.dumps(self.value, indent=2) + '\n'); handle.flush(); os.fsync(handle.fileno())
        temporary.replace(self.path)

    def stage(self, value): self.value['current_stage'] = value; self.save()


class Session:
    """Actual restricted login, bounded outputs and exact backend-absence proof."""
    def __init__(self, role, cid, api, raw, construction_observer=None):
        need(role in AUTH_ROLES and re.fullmatch('[0-9a-f]{64}', cid), 'SESSION_IDENTITY')
        self.role, self.raw, self.backend = role, raw, None
        self.queue = queue.Queue(maxsize=256); self.errors = []; self.invalid = threading.Event()
        self.process = None; self.readers = []; self.readers_started = []
        self.capture_completed = self.finish_completed = False
        self.backend_absence_query_attempted = self.backend_absence_confirmed = False
        def output():
            try:
                while line := self.process.stdout.readline(65537):
                    if len(line) > 65536: self.invalid.set(); continue
                    if clean_text(line) is None: self.invalid.set(); continue
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
        try:
            self.process = subprocess.Popen(api['psql'](role, cid), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, shell=False)
            self.readers = [threading.Thread(target=output, daemon=True), threading.Thread(target=errors, daemon=True)]
            self.readers_started = [False] * len(self.readers)
            for index, reader in enumerate(self.readers): reader.start(); self.readers_started[index] = True
        except (Exception, KeyboardInterrupt) as error:
            # Assignment to the caller has not returned. Retain only fixed
            # observations, then reap this owned process without claiming a
            # backend-absence proof when no validated tuple was captured.
            if construction_observer is not None:
                try: construction_observer('BEFORE_REAP', self, error)
                except (Exception, KeyboardInterrupt): pass
            reap_error = None
            try: self.reap_owned_process()
            except (Exception, KeyboardInterrupt) as close_error: reap_error = close_error
            for reader in self.readers:
                try:
                    if reader.ident is not None: reader.join(timeout=5)
                except (Exception, KeyboardInterrupt): pass
            if construction_observer is not None:
                try: construction_observer('AFTER_REAP', self, reap_error)
                except (Exception, KeyboardInterrupt): pass
            raise

    def send(self, text): self.process.stdin.write(text); self.process.stdin.flush()

    def capture(self):
        self.send("BEGIN ISOLATION LEVEL READ COMMITTED; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='1s'; SET LOCAL idle_in_transaction_session_timeout='30s'; SELECT " + quote(TUPLE) + "||jsonb_build_object('login',session_user,'current_user',current_user,'database',current_database(),'isolation',current_setting('transaction_isolation'),'pid',pg_backend_pid()::text,'xid',pg_current_xact_id()::text,'started',(SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()),'context_absent',coalesce(current_setting('wa.context_hash',true),'')='')::text;\n")
        line = self.queue.get(timeout=15); need(line.startswith(TUPLE), 'SESSION_TUPLE')
        value = unique_json(line[len(TUPLE):])
        need(type(value) is dict and set(value) == {'login', 'current_user', 'database', 'isolation', 'pid', 'xid', 'started', 'context_absent'} and
             value['login'] == value['current_user'] == self.role and value['database'] == DATABASE and value['isolation'] == 'read committed' and value['context_absent'] is True and
             type(value['pid']) is str and re.fullmatch('[1-9][0-9]{0,9}', value['pid']) and type(value['xid']) is str and re.fullmatch('[1-9][0-9]{0,19}', value['xid']) and
             type(value['started']) is str and len(value['started']) <= 64 and re.fullmatch(r'[0-9T:+. \-]+', value['started']), 'SESSION_TUPLE')
        self.backend = value; self.capture_completed = True

    def finish(self, text):
        token = 'WA_NATIVE_DENY_ACK|' + secrets.token_hex(16); self.send(text + '\nSELECT ' + quote(token) + ';\n')
        lines, ack, deadline = [], False, time.monotonic() + 20
        while time.monotonic() < deadline:
            try: line = self.queue.get(timeout=.1)
            except queue.Empty:
                if self.process.poll() is not None: break
                continue
            if line == token: ack = True; break
            if line: lines.append(line)
        if self.process.poll() is None and ack: self.send('\\q\n'); self.process.stdin.close()
        self.process.wait(timeout=10)
        for reader in self.readers: reader.join(timeout=5)
        need(not self.invalid.is_set() and not any(reader.is_alive() for reader in self.readers), 'SESSION_OUTPUT_LIMIT_OR_INCOMPLETE')
        need(not any(self.queue.get_nowait() for _ in range(self.queue.qsize())), 'UNEXPECTED_TRAILING_OUTPUT')
        self.finish_completed = True
        return self.process.returncode, lines, ack, ''.join(self.errors)

    def reap_owned_process(self):
        if self.process is None: return
        if self.process.poll() is None:
            try:
                if not self.process.stdin.closed: self.send('ROLLBACK;\n\\q\n'); self.process.stdin.close()
                self.process.wait(timeout=10)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                self.process.terminate()
                try: self.process.wait(timeout=10)
                except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(timeout=10)

    def close(self):
        self.reap_owned_process()
        need(self.process.poll() is not None and self.backend is not None, 'SESSION_CLOSURE_UNCONFIRMED')
        query = 'SELECT count(*) FROM pg_stat_activity WHERE pid=' + self.backend['pid'] + ' AND backend_start=' + quote(self.backend['started']) + '::timestamptz AND usename=' + quote(self.role) + ' AND datname=' + quote(DATABASE) + ';'
        self.backend_absence_query_attempted = True
        self.backend_absence_confirmed = self.raw('postgres', query).strip() == '0'
        need(self.backend_absence_confirmed, 'OPERATION_BACKEND_STILL_LIVE')
        for reader in self.readers: reader.join(timeout=5)
        need(not any(reader.is_alive() for reader in self.readers), 'SESSION_READER_STILL_LIVE')


SESSION_FAILURE_CODES = frozenset({'SESSION_IDENTITY', 'SESSION_TUPLE', 'SESSION_OUTPUT_LIMIT_OR_INCOMPLETE',
    'UNEXPECTED_TRAILING_OUTPUT', 'SESSION_CLOSURE_UNCONFIRMED', 'OPERATION_BACKEND_STILL_LIVE', 'SESSION_READER_STILL_LIVE',
    'DUPLICATE_JSON_KEY', 'NONFINITE_JSON', 'INITIAL_BEGIN_REQUIRED',
    'INTENDED_NATIVE_GATE_NOT_PROVEN', 'EXACT_OPERATION_RESULT_REQUIRED', 'OPERATION_EVIDENCE_INCOMPLETE'})
SESSION_PHASES = frozenset({'CONSTRUCT', 'CAPTURE', 'FINISH', 'VERDICT', 'CLOSE', 'CONSTRUCTOR_REAP'})


def session_failure_metadata(error, phase):
    """Fixed labels only: exception strings, args and unrecognized codes stay in RAM."""
    phase = phase if type(phase) is str and phase in SESSION_PHASES else 'UNKNOWN_PHASE'
    code = error.code if isinstance(error, HeldFailure) and type(error.code) is str and error.code in SESSION_FAILURE_CODES else None
    classification = ('SOURCE_HELD_FAILURE' if code is not None else 'UNRECOGNIZED_HELD_FAILURE' if isinstance(error, HeldFailure) else
                      'QUEUE_EMPTY' if isinstance(error, queue.Empty) else 'PROCESS_TIMEOUT' if isinstance(error, subprocess.TimeoutExpired) else
                      'OS_ERROR' if isinstance(error, OSError) else 'VALUE_ERROR' if isinstance(error, ValueError) else
                      'INTERRUPTED' if isinstance(error, KeyboardInterrupt) else 'UNEXPECTED_EXCEPTION')
    return {'phase': phase, 'classification': classification, 'code': code}


def session_observation(session):
    """No backend identity, raw streams, SQL, reader errors or process exit number."""
    def flag(name):
        value = getattr(session, name, None)
        return value if type(value) is bool else None
    process = getattr(session, 'process', None)
    exit_class = 'UNAVAILABLE'; process_exit_confirmed = False
    if process is not None:
        try:
            code = process.poll()
            process_exit_confirmed = type(code) is int
            exit_class = ('RUNNING' if code is None else 'EXITED_ZERO' if type(code) is int and code == 0 else
                          'EXITED_NONZERO' if type(code) is int and code > 0 else 'SIGNAL_OR_OTHER')
        except (Exception, KeyboardInterrupt): pass
    readers = getattr(session, 'readers', [])
    started = getattr(session, 'readers_started', [])
    finished = []
    for index in range(2):
        value = None
        if type(readers) is list and type(started) is list and index < len(readers) and index < len(started) and started[index] is True:
            try: value = not readers[index].is_alive()
            except (Exception, KeyboardInterrupt): pass
        finished.append(value)
    invalid = None
    try:
        event = getattr(session, 'invalid', None)
        if event is not None: invalid = bool(event.is_set())
    except (Exception, KeyboardInterrupt): pass
    return {'process_created': process is not None, 'backend_tuple_present': getattr(session, 'backend', None) is not None,
            'capture_completed': flag('capture_completed'), 'finish_completed': flag('finish_completed'),
            'process_exit_class': exit_class, 'process_exit_confirmed': process_exit_confirmed,
            'stdout_reader_finished': finished[0], 'stderr_reader_finished': finished[1], 'readers_finished': all(value is True for value in finished),
            'output_invalid': invalid, 'backend_absence_query_attempted': flag('backend_absence_query_attempted'),
            'backend_absence_confirmed': flag('backend_absence_confirmed')}


class Coordinator:
    def __init__(self, plan, packet, blobs, native, api, host, evidence):
        self.plan, self.packet, self.blobs, self.native, self.api, self.host, self.evidence = plan, packet, blobs, native, api, host, evidence
        self.cid = plan['immutable_container_id']; self.seeded = False; self.baseline = None
        self.models = {row['object']: row for row in unique_json(blobs['__models'])}
        self.acl = {(row['kind'], row['object'], row['grantee'], row['privilege'], row.get('column')) for row in native['nonowner_acl']}
        self.triggers = sorted(packet['setup_bypassed_user_triggers'] + packet['setup_retained_user_triggers'], key=lambda row: row['identity'])
        need(len(self.triggers) == 100 and len(packet['setup_bypassed_user_triggers']) == 60 and len(packet['setup_retained_user_triggers']) == 40, 'TRIGGER_SOURCE_COUNTS')
        self.tables = sorted(packet['synthetic_facts']['baseline'])
        setup = self.text('native-fact-setup.sql')
        self.setup_counts = {name: len(re.findall(r'^INSERT INTO ' + re.escape(table(name)) + r'\(', setup, re.M)) for name in self.tables}
        need(len(self.tables) == 42 and sum(self.setup_counts.values()) == 205 and all(self.setup_counts.values()), 'FIXTURE_SOURCE_COUNTS')
        self.evidence.value['selected_cases'] = [{'id': case['id'], 'status': 'NOT_RUN', 'source_vectors_status': 'NOT_RUN', 'allow_case_status': 'NOT_RUN'} for case in packet['cases']]

    def text(self, name): return packet_sql(self.packet, name, self.blobs)
    def raw(self, role, text): return self.api['run'](role, text, self.cid)
    def json(self, text): return unique_json(self.raw('postgres', text))

    def resource(self):
        self.evidence.stage('RESOURCE_IDENTITY')
        def inspect(args):
            value = unique_json(subprocess.check_output(['docker', '--context', 'desktop-linux', *args], text=True, timeout=30, shell=False))
            need(type(value) is list and len(value) == 1, 'RESOURCE_METADATA'); return value[0]
        context = inspect(['context', 'inspect', 'desktop-linux']); container = inspect(['inspect', self.cid])
        volume = inspect(['volume', 'inspect', self.plan['target_manifest']['target']['volume_name']]); image = inspect(['image', 'inspect', container.get('Image', '')])
        observed = self.host['inspect_live'](self.plan['target_manifest'], context, container, volume)
        need(observed['container_id'] == self.cid, 'IMMUTABLE_CONTAINER_CHANGED'); self.host['verify_image'](self.plan['target_manifest'], container, image)
        self.evidence.value['resource'] = {key: observed[key] for key in ('container_id', 'container_name', 'volume_name', 'image', 'network', 'published_ports', 'labels')}; self.evidence.save()

    def catalog(self):
        self.evidence.stage('SOURCE_QUALIFIED_NATIVE_CATALOG')
        current = self.json(self.blobs['__collector'].decode('utf8'))
        need(digest(current) == digest(self.native), 'NATIVE_CATALOG_CHANGED')
        self.evidence.value['current']['native_catalog_unchanged'] = True; self.evidence.save()

    def guards(self):
        values = ','.join('(' + ','.join(quote(row[key]) for key in ('table', 'name', 'function', 'original_enabled', 'body_sha256')) + ')' for row in self.triggers)
        query = "WITH expected(table_name,name,function_name,enabled,body_sha256) AS (VALUES " + values + "),actual AS (SELECT n.nspname||'.'||c.relname,t.tgname::text,fn.nspname||'.'||p.proname,t.tgenabled::text,encode(sha256(convert_to(p.prosrc,'UTF8')),'hex') FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace fn ON fn.oid=p.pronamespace WHERE n.nspname IN ('app','platform','platform_private') AND NOT t.tgisinternal) SELECT jsonb_build_object('expected_count',100,'actual_count',(SELECT count(*) FROM actual),'exact_trigger_function_body_state_set',NOT EXISTS((SELECT * FROM expected EXCEPT SELECT * FROM actual) UNION ALL (SELECT * FROM actual EXCEPT SELECT * FROM expected)));"
        value = self.json(query); good = canonical(value) == canonical({'expected_count': 100, 'actual_count': 100, 'exact_trigger_function_body_state_set': True})
        self.evidence.value['current']['all_100_trigger_functions_restored'] = good; self.evidence.save(); need(good, 'EXACT_TRIGGER_RESTORATION_FAILED')

    def fingerprint_order_control(self):
        self.evidence.stage('SOURCE_NAME_COLLATION_CONTROL')
        names = ','.join('(' + quote(name) + '::text)' for name in self.tables)
        expected = 'to_jsonb(ARRAY[' + ','.join(quote(name) for name in self.tables) + ']::text[])'
        query = 'BEGIN READ ONLY; WITH names(name) AS (VALUES ' + names + ") SELECT jsonb_build_object('format','workinants.native-fingerprint-order.v1','server_version_num',current_setting('server_version_num')::integer,'collected_as',current_user,'read_only',current_setting('transaction_read_only')='on','known_name_count',count(*),'c_order_matches_source',jsonb_agg(name ORDER BY name COLLATE \"C\")=" + expected + ",'default_order_matches_source',jsonb_agg(name ORDER BY name)=" + expected + ') FROM names; ROLLBACK;'
        value = self.json(query)
        fields = {'format', 'server_version_num', 'collected_as', 'read_only', 'known_name_count', 'c_order_matches_source', 'default_order_matches_source'}
        checks = {'object': type(value) is dict}
        checks['fields'] = checks['object'] and set(value) == fields
        checks['identity'] = checks['fields'] and value['format'] == 'workinants.native-fingerprint-order.v1' and value['collected_as'] == 'postgres'
        checks['typed_version_and_count'] = checks['fields'] and type(value['server_version_num']) is int and value['server_version_num'] == 170011 and type(value['known_name_count']) is int and value['known_name_count'] == 42
        checks['typed_flags'] = checks['fields'] and all(type(value[k]) is bool for k in ('read_only', 'c_order_matches_source', 'default_order_matches_source'))
        self.evidence.value['fingerprint_order_comparisons'] = checks; self.evidence.save()
        need(all(checks.values()), 'FINGERPRINT_ORDER_CONTROL_SHAPE')
        self.evidence.value['fingerprint_order_control'] = value; self.evidence.save()
        need(value['read_only'] is True and value['c_order_matches_source'] is True, 'FINGERPRINT_C_ORDER_REQUIRED')

    def fingerprint(self):
        self.evidence.stage('SEEDED_DATA_FINGERPRINT' if self.seeded else 'EMPTY_DATA_FINGERPRINT')
        parts = ["SELECT " + quote(name) + " AS object,count(*)::integer AS row_count,encode(sha256(convert_to(coalesce(string_agg(encode(sha256(convert_to(to_jsonb(t)::text,'UTF8')),'hex'),'' ORDER BY encode(sha256(convert_to(to_jsonb(t)::text,'UTF8')),'hex') COLLATE \"C\"),''),'UTF8')),'hex') AS rows_sha256 FROM " + table(name) + ' t' for name in self.tables]
        rows = self.json('SELECT jsonb_agg(to_jsonb(x) ORDER BY object COLLATE "C") FROM (' + ' UNION ALL '.join(parts) + ') x;')
        checks = {'list': type(rows) is list}
        checks['exact_row_count'] = checks['list'] and len(rows) == 42
        checks['objects'] = checks['exact_row_count'] and all(type(row) is dict for row in rows)
        checks['fields'] = checks['objects'] and all(set(row) == {'object', 'row_count', 'rows_sha256'} for row in rows)
        checks['known_name_set'] = checks['fields'] and all(type(row['object']) is str for row in rows) and set(row['object'] for row in rows) == set(self.tables)
        checks['source_name_order'] = checks['known_name_set'] and [row['object'] for row in rows] == self.tables
        checks['typed_bounded_counts'] = checks['fields'] and all(type(row['row_count']) is int and 0 <= row['row_count'] <= 1000000000 for row in rows)
        checks['digest_shape'] = checks['fields'] and all(type(row['rows_sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['rows_sha256']) is not None for row in rows)
        self.evidence.value['current']['fingerprint_checks'] = checks; self.evidence.save()
        need(all(checks.values()), 'DATA_FINGERPRINT_SHAPE')
        self.evidence.value['current']['data_projection'] = rows; self.evidence.save()
        expected = self.setup_counts if self.seeded else dict.fromkeys(self.tables, 0)
        need({row['object']: row['row_count'] for row in rows} == expected, 'EXACT_NATIVE_FACT_COUNTS')
        if self.baseline is not None: need(canonical(rows) == canonical(self.baseline), 'NATIVE_FACTS_CHANGED')
        return rows

    def observe_closed(self):
        self.evidence.stage('CLOSED_OPERATION_OBSERVATIONS'); self.guards()
        current = self.fingerprint(); self.evidence.value['current']['all_native_facts_unchanged'] = True; self.evidence.save(); return current

    def operation(self, name, role, text, expected=None, denial=None):
        record = {'name': name, 'role': role, 'source_sql_sha256': sha(text.encode()), 'closed_before_observers': False, 'evidence_complete': True}
        self.evidence.value['current'] = record
        session = None; failure = None; stage = None; result = None; phase = 'CONSTRUCT'
        def persist(stage_value=None):
            if stage_value is not None: self.evidence.value['current_stage'] = stage_value
            try: self.evidence.save(); return True
            except (Exception, KeyboardInterrupt):
                record['evidence_complete'] = False; self.evidence.value['evidence_complete'] = False
                return False
        def constructor_observation(point, partial, error):
            if point == 'BEFORE_REAP':
                record['original_operation_failure'] = session_failure_metadata(error, 'CONSTRUCT')
                record['constructor_before_reap'] = session_observation(partial)
            elif point == 'AFTER_REAP':
                record['constructor_after_reap'] = session_observation(partial)
                if error is not None: record['constructor_reap_failure'] = session_failure_metadata(error, 'CONSTRUCTOR_REAP')
            persist()
        try:
            need(persist('OPEN_' + name), 'OPERATION_EVIDENCE_INCOMPLETE')
            session = Session(role, self.cid, self.api, self.raw, constructor_observation)
            record['session_after_constructor'] = session_observation(session)
            phase = 'CAPTURE'; session.capture()
            record['session_after_capture'] = session_observation(session)
            record['actual_login_context_absent'] = True
            need(persist('EXECUTE_' + name), 'OPERATION_EVIDENCE_INCOMPLETE')
            phase = 'FINISH'
            code, lines, ack, errors = session.finish(captured_tail(text))
            record.update(exit_code=code, acknowledgement=ack, session_after_finish=session_observation(session))
            phase = 'VERDICT'
            if denial is not None:
                diagnostic = native_diagnostic(errors, denial[0], denial[1], text); record['native_diagnostic'] = diagnostic
                record['source_native_privilege_projection'] = deepcopy(denial[1]); need(persist(), 'OPERATION_EVIDENCE_INCOMPLETE')
                need(code == 3 and ack is False and lines == [] and diagnostic['matched'], 'INTENDED_NATIVE_GATE_NOT_PROVEN')
                result = diagnostic
            else:
                # Raw output is compared in memory, never copied into evidence.
                record['exact_output_matches'] = output_matches(lines, expected)
                exact = code == 0 and ack is True and errors == '' and record['exact_output_matches']
                if not exact and (name == 'native-fact-setup' or name in {'native-control-' + case['model'] for case in self.packet['cases']}):
                    # Unexpected setup/control metadata explains only this stop.
                    # No raw helper dictionary or arbitrary exception crosses it.
                    metadata = None
                    if type(errors) is str and len(errors) <= 16384 and clean_text(errors) is not None:
                        try: metadata = self.api['source_metadata'](errors)
                        except Exception: pass
                    record['unexpected_operation_diagnostic'] = unexpected_operation_metadata(errors, self.native,
                        self.packet['source_inputs_sha256']['review-output/foundation-application.review.sql'], metadata,
                        unique_json(self.blobs['__diagnostic_identifiers']))
                    record['diagnostic_stage'] = 'UNEXPECTED_NATIVE_SETUP' if name == 'native-fact-setup' else 'UNEXPECTED_NATIVE_CONTROL'
                need(persist(), 'OPERATION_EVIDENCE_INCOMPLETE'); need(exact, 'EXACT_OPERATION_RESULT_REQUIRED')
                result = True
        except (Exception, KeyboardInterrupt) as error:
            failure, stage = error, self.evidence.value['current_stage']
            record.setdefault('original_operation_failure', session_failure_metadata(error, phase))
            persist()
        finally:
            persist('CLOSE_' + name)
            if session is not None:
                record['session_before_close'] = session_observation(session); persist()
                try: session.close(); record['closed_before_observers'] = True
                except (Exception, KeyboardInterrupt) as error:
                    record['close_failure'] = session_failure_metadata(error, 'CLOSE')
                    failure, stage = HeldFailure('BACKEND_CLOSURE_UNCONFIRMED'), 'CLOSE_' + name
                record['session_after_close'] = session_observation(session)
            if not record['evidence_complete'] and failure is None:
                failure, stage = HeldFailure('OPERATION_EVIDENCE_INCOMPLETE'), 'CLOSE_' + name
            self.evidence.value['operations'].append(record); persist()
            if not record['evidence_complete'] and failure is None:
                failure, stage = HeldFailure('OPERATION_EVIDENCE_INCOMPLETE'), 'CLOSE_' + name
        if failure is not None:
            if record['closed_before_observers'] and record['evidence_complete']:
                # No repair or ENABLE here. Transaction rollback/closure must
                # restore the original state independently; mismatch stays held.
                try: self.guards(); self.fingerprint(); record['post_failure_observation_verified'] = True
                except (Exception, KeyboardInterrupt):
                    record['post_failure_observation_verified'] = False
                    record['evidence_complete'] = False; self.evidence.value['evidence_complete'] = False
            persist(stage)
            if isinstance(failure, HeldFailure) and failure.code not in SESSION_FAILURE_CODES | {'BACKEND_CLOSURE_UNCONFIRMED'}:
                raise HeldFailure('SESSION_FAILURE_UNRECOGNIZED') from None
            raise failure
        return result

    def privileges(self, case, probe):
        model = self.models[case['table']]; columns = sorted(model['fields'].values()); role = probe['role']; name = case['table']; schema = name.split('.')[0]
        rows = ','.join('(' + quote(column) + ')' for column in columns)
        query = "SELECT jsonb_build_object('schema_usage',has_schema_privilege(" + quote(role) + ',' + quote(schema) + ",'USAGE'),'table',jsonb_build_object(" + ','.join(quote(verb) + ',has_table_privilege(' + quote(role) + ',' + quote(name) + ',' + quote(verb) + ')' for verb in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')) + "),'columns',(SELECT jsonb_object_agg(column_name,jsonb_build_object(" + ','.join(quote(verb) + ',has_column_privilege(' + quote(role) + ',' + quote(name) + ',column_name,' + quote(verb) + ')' for verb in ('SELECT', 'INSERT', 'UPDATE')) + ')) FROM (VALUES ' + rows + ') v(column_name)));'
        actual = self.json(query)
        def allowed(kind, privilege, column=None):
            object_ = schema if kind == 'SCHEMA' else name
            return any((kind, object_, grantee, privilege, scoped_column) in self.acl for grantee in (role, 'PUBLIC') for scoped_column in ((None,) if column is None else (None, column)))
        expected = {'schema_usage': allowed('SCHEMA', 'USAGE'), 'table': {verb: allowed('TABLE', verb) for verb in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')},
                    'columns': {column: {verb: allowed('TABLE', verb, column) for verb in ('SELECT', 'INSERT', 'UPDATE')} for column in columns}}
        need(canonical(actual) == canonical(expected), 'NATIVE_PRIVILEGE_PROJECTION_CHANGED')
        verb = probe['verb']; required = [(column, 'SELECT') for field, column in model['fields'].items() if field in model['pk']]
        if verb == 'SELECT' and probe['native_forbidden_column']: required.append((probe['native_forbidden_column'], 'SELECT'))
        if verb == 'INSERT': required = [(column, 'INSERT') for column in columns]
        if verb == 'UPDATE': required.append((probe['native_forbidden_column'], 'UPDATE'))
        missing = sorted({column for column, operation in required if column is not None and actual['columns'][column][operation] is False})
        return {'schema_usage': actual['schema_usage'], 'required_permission_missing': bool(missing) or verb == 'DELETE' and actual['table']['DELETE'] is False,
                'missing_referenced_columns': missing}

    def authentication(self):
        self.evidence.stage('SCRAM_PREFLIGHT')
        rows = self.json("SELECT coalesce(jsonb_agg(jsonb_build_object('rule_number',rule_number,'type',type,'database',database,'user_name',user_name,'address',address,'netmask',netmask,'auth_method',auth_method,'error',error) ORDER BY rule_number),'[]'::jsonb) FROM pg_hba_file_rules;")
        need(type(rows) is list and rows and all(row['error'] is None for row in rows), 'HBA_PARSE')
        for address in ('127.0.0.1', '::1'):
            for role in AUTH_ROLES:
                matched = None
                for row in sorted(rows, key=lambda row: row['rule_number']):
                    if row['type'] == 'local': continue
                    need(row['type'] == 'host' and all(value in ('all', 'replication', DATABASE) for value in row['database']) and all(value in ('all', *AUTH_ROLES) for value in row['user_name']), 'HBA_UNSUPPORTED')
                    if not ('all' in row['database'] or DATABASE in row['database']) or not ('all' in row['user_name'] or role in row['user_name']): continue
                    mask = ipaddress.ip_address(row['netmask']); bits = bin(int(mask))[2:].zfill(mask.max_prefixlen)
                    need('01' not in bits, 'HBA_MASK'); network = ipaddress.ip_network(row['address'] + '/' + str(bits.count('1')), strict=False)
                    if ipaddress.ip_address(address) in network: matched = row; break
                need(matched is not None and matched['auth_method'] == 'scram-sha-256', 'HBA_SCRAM_REQUIRED')
        verifiers = self.json("SELECT jsonb_object_agg(rolname,rolcanlogin AND rolpassword LIKE 'SCRAM-SHA-256$%') FROM pg_authid WHERE rolname IN (" + ','.join(quote(role) for role in AUTH_ROLES) + ');')
        need(canonical(verifiers) == canonical(dict.fromkeys(AUTH_ROLES, True)), 'SCRAM_VERIFIERS_REQUIRED')
        for role in AUTH_ROLES:
            self.evidence.value['current_auth_role'] = role; self.evidence.stage('SCRAM_CORRECT_PASSWORD')
            output = self.raw(role, "SELECT jsonb_build_object('login',session_user,'auth',system_user,'database',current_database(),'client',host(inet_client_addr()),'server',host(inet_server_addr()));")
            comparison = self.api['authentication_comparison'](output, role); self.evidence.value['authentication_comparisons'] = comparison; self.evidence.save()
            need(all(comparison.values()), 'AUTHENTICATED_SCRAM_REQUIRED')
            self.evidence.stage('SCRAM_WRONG_PASSWORD')
            env = os.environ.copy(); env['PGPASSWORD'] = secrets.token_hex(32)
            result = subprocess.run(self.api['psql'](role, self.cid, True), input='SELECT 1;\n', text=True, capture_output=True, timeout=30, env=env)
            text = clean_text(result.stderr)
            pattern = r'(?:psql: error: connection to server at "127\.0\.0\.1", port 5432 failed: )?FATAL:\s+password authentication failed for user "' + re.escape(role) + '"\n?'
            good = result.returncode == 2 and result.stdout == '' and text is not None and re.fullmatch(pattern, text) is not None
            self.evidence.value['authentication'].append({'role': role, 'correct_password': 'PASS_SCRAM', 'wrong_password_rejected': good, 'wrong_password_exit_code': result.returncode}); self.evidence.save()
            need(good, 'WRONG_PASSWORD_CONTROL_REQUIRED')

    def preflight(self):
        self.resource(); self.catalog(); self.guards()
        need(self.raw('postgres', "SELECT current_user='postgres' AND session_user='postgres' AND current_setting('server_version_num')='170011' AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256' AND (SELECT rolsuper FROM pg_roles WHERE rolname=current_user);").strip() == 't', 'ORIGINAL_GRANTOR_AND_LOGGING_REQUIRED')
        self.authentication()
        leaves = "ARRAY['wa_private_helper_owner','wa_customer_verifier','wa_track_verifier']"
        need(self.raw('postgres', "SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE roleid IN (SELECT oid FROM pg_roles WHERE rolname=ANY(" + leaves + ")) AND member='wa_schema_owner'::regrole) AND (SELECT bool_and(NOT has_schema_privilege(r,n,'CREATE')) FROM unnest(" + leaves + ") r CROSS JOIN unnest(ARRAY['app','platform','platform_private']) n);").strip() == 't', 'FINALIZATION_REQUIRED')
        flags = self.json("SELECT jsonb_agg(jsonb_build_object('name',rolname,'login',rolcanlogin,'inherit',rolinherit,'superuser',rolsuper,'createdb',rolcreatedb,'createrole',rolcreaterole,'replication',rolreplication,'bypassrls',rolbypassrls,'memberships',(SELECT count(*) FROM pg_auth_members m WHERE m.member=r.oid OR m.roleid=r.oid),'connect',has_database_privilege(rolname,current_database(),'CONNECT'),'create',has_database_privilege(rolname,current_database(),'CREATE'),'temp',has_database_privilege(rolname,current_database(),'TEMP')) ORDER BY rolname) FROM pg_roles r WHERE rolname IN ('anon','authenticated','service_role');")
        need(canonical(flags) == canonical(sorted(provider_flags(), key=lambda row: row['name'])), 'LOCAL_PROVIDER_ROLE_BOUNDARY')
        self.evidence.value['provider_roles'] = provider_flags(); self.evidence.save()
        self.fingerprint_order_control()
        self.fingerprint()

    def run(self):
        self.preflight(); self.evidence.stage('EXACT_NATIVE_FACT_SETUP')
        setup_expected = [{'control': 'all-native-fact-setup-triggers-restored', 'all_declared_user_triggers_restored': True}]
        self.operation('native-fact-setup', 'postgres', self.text('native-fact-setup.sql'), expected=setup_expected)
        self.seeded = True; self.guards(); self.baseline = self.fingerprint(); self.catalog()
        self.evidence.value['native_fact_projection'] = deepcopy(self.baseline); self.evidence.save()
        for case in self.packet['cases']:
            self.evidence.value['current_case'] = case['id']; self.evidence.stage('CASE_NATIVE_VALIDITY')
            self.guards()
            # Exact packet contract: only this target's USER triggers bypassed;
            # the transaction has no COMMIT and its final ROLLBACK restores DDL.
            text = self.text(case['native_controls'])
            need('\nCOMMIT;' not in text and text.count('\nROLLBACK;') == 1 and all(row['table'] == case['table'] for row in case['control_bypassed_user_triggers']), 'ROLLBACK_ONLY_TARGET_CONTROL_REQUIRED')
            expected = ['t'] * (2 + len(case['native_update_control_columns'])) + [{'control': 'native-control-' + case['model'], 'all_declared_user_triggers_restored': True}]
            self.operation('native-control-' + case['model'], 'postgres', text, expected=expected)
            self.observe_closed(); self.catalog()
            self.evidence.value['native_controls'].append({'case_id': case['id'], 'status': 'NATIVE_CONSTRAINT_FIXTURE_VALIDITY_ONLY', 'insert_one': True, 'update_controls_one': len(case['native_update_control_columns']), 'delete_one': True, 'rollback_and_restoration_proven': True}); self.evidence.save()
            if case['issuer_ownership_controls'] is not None:
                control = case['issuer_ownership_controls']; need(self.json(control['independent_fixture_observer_sql']) == {'own_exists': 1, 'foreign_exists': 1}, 'ISSUER_BOTH_EXISTING_ROWS_REQUIRED')
                self.guards(); self.operation('issuer-own-and-foreign', 'wa_context_issuer', control['sql_text'], expected=[{'own_row': 1, 'foreign_row': 0}]); self.observe_closed()
            for probe in case['probes']:
                self.evidence.value['current_probe'] = {'role': probe['role'], 'verb': probe['verb']}; self.evidence.stage('PROBE_PREREQUISITES')
                if probe['preparation'] == 'BLOCKED':
                    self.evidence.value['facets'].append({'case_id': case['id'], 'role': probe['role'], 'verb': probe['verb'], 'status': 'NOT_RUN', 'blocker': probe['preparation_blocker']}); self.evidence.save(); continue
                self.guards(); self.fingerprint()
                need(self.json(self.text(case['existing_row_observer'])) == {'row_count': 1}, 'EXISTING_ROW_POSITIVE_REQUIRED')
                metadata = self.privileges(case, probe)
                self.evidence.value['current']['privilege_metadata_compared_to_source_native_pass'] = True; self.evidence.save()
                expected = ['0'] if probe['facet'].startswith('RLS_') else None
                result = self.operation('deny-' + case['model'] + '-' + probe['role'] + '-' + probe['verb'], probe['role'], probe['sql_text'], expected=expected,
                                        denial=(case, metadata) if expected is None else None)
                self.observe_closed()
                self.evidence.value['facets'].append({'case_id': case['id'], 'role': probe['role'], 'verb': probe['verb'],
                    'status': 'PASS_OBSERVED_NATIVE_GATE_ONLY' if expected is None else 'PASS_EXISTING_ROW_EMPTY_ONLY', 'facet': probe['facet'],
                    **({'diagnostic': result} if expected is None else {'existing_row_count': 1, 'restricted_count': 0}),
                    'post_probe_observers': {'operation_backend_absent': True, 'all_100_trigger_functions_restored': True, 'all_205_native_facts_unchanged': True},
                    'whole_case_promoted': False}); self.evidence.save()
            self.catalog()
        self.evidence.value['status'] = 'COMPLETED_PREPARED_FACETS_ONLY_CASES_STILL_NOT_RUN'; self.evidence.stage('FINISHED')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-reviewed-native-denials', action='store_true', required=True)
    parser.add_argument('--run-plan', type=Path, required=True); parser.add_argument('--evidence-directory', type=Path, required=True)
    args = parser.parse_args(argv)
    evidence = None
    try:
        directory = external_path(args.evidence_directory); need(not directory.exists(), 'FRESH_EVIDENCE_DIRECTORY_REQUIRED')
        evidence = Evidence(directory); evidence.stage('VERIFY_REVIEWED_INPUTS')
        raw = external_path(args.run_plan).read_bytes(); plan = unique_json(raw)
        packet, blobs, native, api, host = load_inputs(plan)
        evidence.value['run_id'] = plan['run_id']; evidence.value['source_commit'] = plan['source_commit']; evidence.value['source_tree'] = plan['source_tree']; evidence.value['run_plan_sha256'] = sha(raw); evidence.save()
        Coordinator(plan, packet, blobs, native, api, host, evidence).run(); return 0
    except (Exception, KeyboardInterrupt) as error:
        if evidence is not None:
            evidence.value.update(status='STOPPED', subsequent_cases_stopped=True, failure={'code': error.code if isinstance(error, HeldFailure) else 'UNEXPECTED_EXCEPTION', 'stage': evidence.value['current_stage']})
            try: evidence.save()
            except (Exception, KeyboardInterrupt): evidence.value['evidence_complete'] = False
        return 2


if __name__ == '__main__': raise SystemExit(main())
