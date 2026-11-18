"""Finite source-only coordinator proposal; no database/process transport exists.

An eventual independently reviewed adapter must implement the named operations
using actual app/issuer connections and pinned SQL. Mocking this protocol proves
only its scheduling/stop/evidence rules; every database assertion stays NOT_RUN.
"""
from copy import deepcopy
import re

NAMES = ('same-fingerprint-holder-commit', 'same-fingerprint-holder-rollback',
         'changed-fingerprint-holder-commit', 'changed-fingerprint-holder-rollback',
         'different-subjects-identical-text-key')
CODES = {'PREFLIGHT_UNPROVED', 'FIXTURE_SETUP_UNPROVED', 'ACTUAL_APP_BINDING_UNPROVED', 'GROUP_NOT_READY',
         'BEFORE_COMMAND_NOT_PROVEN', 'CONCURRENT_WAIT_UNPROVEN', 'TRANSACTION_END_UNPROVEN', 'DUPLICATE_GUARD_UNPROVEN',
         'WAITING_COMMAND_DID_NOT_COMPLETE', 'COMPLETE_STATE_UNPROVEN', 'OPERATION_CLOSURE_UNCONFIRMED', 'PACKET_SCOPE'}


class ProtocolStop(Exception):
    def __init__(self, code):
        self.code = code if code in CODES else 'PACKET_SCOPE'; super().__init__(self.code)


def require(value, code):
    if not value: raise ProtocolStop(code)


def exact_booleans(value, expected):
    return type(value) is dict and set(value) == set(expected) and all(type(value[key]) is bool and value[key] is wanted for key, wanted in expected.items())


def barrier_sql(tuples):
    """Build a fixed Boolean-only synchronization observer; tuples stay in RAM."""
    require(type(tuples) is dict and set(tuples) == {'A', 'B'}, 'PACKET_SCOPE')
    for value in tuples.values():
        require(type(value) is dict and set(value) == {'login', 'current_user', 'database', 'isolation', 'pid', 'xid', 'started'} and
                value['login'] == value['current_user'] == 'wa_app_runtime' and value['database'] == 'wa_p0c_rehearsal' and value['isolation'] == 'read committed' and
                type(value['pid']) is str and re.fullmatch('[1-9][0-9]{0,9}', value['pid']) and type(value['xid']) is str and re.fullmatch('[1-9][0-9]{0,19}', value['xid']) and
                type(value['started']) is str and re.fullmatch(r'[0-9T:+. \-]{1,64}', value['started']), 'PACKET_SCOPE')
    require(tuples['A']['pid'] != tuples['B']['pid'] and tuples['A']['xid'] != tuples['B']['xid'], 'PACKET_SCOPE')
    def row(side):
        value = tuples[side]
        return "SELECT pid,state,wait_event_type,wait_event FROM pg_stat_activity WHERE pid=" + value['pid'] + " AND backend_start='" + value['started'] + "'::timestamptz AND usename='wa_app_runtime' AND datname='wa_p0c_rehearsal'"
    # backend_xid is a 32-bit xid. Do not compare it to the captured full xid8:
    # each full xid remains bound through its independent issuer grant instead.
    return "WITH a AS (" + row('A') + "),b AS (" + row('B') + ") SELECT jsonb_build_object('A_idle_in_transaction',coalesce((SELECT state='idle in transaction' FROM a),false),'B_active',coalesce((SELECT state='active' FROM b),false),'B_wait_event_type_lock',coalesce((SELECT wait_event_type='Lock' FROM b),false),'B_wait_event_transactionid',coalesce((SELECT wait_event='transactionid' FROM b),false),'B_blocked_only_by_A',coalesce((SELECT pg_blocking_pids(pid)=ARRAY[" + tuples['A']['pid'] + "] FROM b),false));\n"


def duplicate_diagnostic(stderr, expected):
    """PG17.11 native unique error only; RLS suppresses key DETAIL entirely."""
    result = {'matched': False, 'sqlstate': None, 'schema_table_constraint_exact': False, 'native_location_exact': False, 'detail_absent': False}
    normalized = stderr.replace('\r\n', '\n')
    if not all(char in ('\t', '\n') or char.isprintable() for char in normalized): return result
    lines = [line for line in normalized.split('\n') if line]
    if len(lines) != 5 or sum(bool(re.search(r'\b(?:ERROR|FATAL|PANIC)\b', line)) for line in lines) != 1: return result
    header = re.fullmatch(r'(?:psql:<stdin>:[1-9][0-9]*: )?ERROR:\s+23505:\s+(.*)', lines[0])
    if header is None or header[1] != expected['exact_message']: return result
    fields = {}
    for line in lines[1:]:
        item = re.fullmatch(r'(SCHEMA NAME|TABLE NAME|CONSTRAINT NAME|LOCATION):\s+(.*)', line)
        if item is None or item[1] in fields: return result
        fields[item[1]] = item[2]
    if set(fields) != {'SCHEMA NAME', 'TABLE NAME', 'CONSTRAINT NAME', 'LOCATION'}: return result
    exact = (fields['SCHEMA NAME'], fields['TABLE NAME'], fields['CONSTRAINT NAME']) == (expected['schema'], expected['table'], expected['constraint'])
    location = re.fullmatch(re.escape(expected['native_routine']) + ', ' + re.escape(expected['native_file']) + ':[1-9][0-9]{0,5}', fields['LOCATION']) is not None
    matched = exact and location and expected.get('detail_expected') == 'ABSENT_RLS_ENABLED' and expected.get('row_security_enabled_required') is True
    return {'matched': matched, 'sqlstate': '23505' if matched else None, 'schema_table_constraint_exact': exact, 'native_location_exact': location, 'detail_absent': True}


def run_race(race, port, save):
    """Use a dependency-injected PROPOSAL adapter; return safe metadata only."""
    record = {'name': race['name'], 'assertion_id': race['assertion_id'], 'status': 'IN_PROGRESS_PROTOCOL_ONLY', 'stage': 'ENTRY',
              'bindings': {}, 'closed': {'A': False, 'B': False}, 'comparisons': {}, 'runtime_assertion_status': 'NOT_RUN'}
    opened = set(); failure = None
    def stage(name): record['stage'] = name; save(deepcopy(record))
    def close(side):
        value = port.close(side)
        good = exact_booleans(value, {'client_exited': True, 'backend_absent': True})
        record['closed'][side] = good; save(deepcopy(record)); require(good, 'OPERATION_CLOSURE_UNCONFIRMED')
    def end(side, outcome):
        stage('END_' + side + '_' + outcome)
        value = port.end_transaction(side, outcome)
        good = type(value) is dict and set(value) == {'exit_code', 'acknowledged', 'transaction_ended'} and type(value['exit_code']) is int and value['exit_code'] == 0 and value['acknowledged'] is True and value['transaction_ended'] is True
        record['comparisons'][side + '_transaction_end'] = good; save(deepcopy(record)); require(good, 'TRANSACTION_END_UNPROVEN')
        close(side)
    def ready(side, remainder=False):
        stage('GROUP_' + side + '_READY')
        value = port.complete_remainder(side, race['participants'][side]) if remainder else port.stage_group(side, race['participants'][side])
        good = exact_booleans(value, {'markers_exact': True, 'constraints_checked': True, 'group_ready': True, 'transaction_open': True})
        record['comparisons'][side + '_group_ready'] = good; save(deepcopy(record)); require(good, 'GROUP_NOT_READY')
    try:
        # Capture/bind BOTH exact real connections before A's protected work.
        for side in ('A', 'B'):
            stage('OPEN_BIND_' + side); opened.add(side)
            value = port.open_bound(side, race['participants'][side])
            good = exact_booleans(value, {'actual_app_identity_and_tuple': True, 'independent_issuer_commit': True, 'issuer_backend_closed': True, 'bound_same_connection': True})
            record['bindings'][side] = good; save(deepcopy(record)); require(good, 'ACTUAL_APP_BINDING_UNPROVED')
        ready('A')
        if race['different_subject_scope']:
            ready('B'); end('A', 'COMMIT'); end('B', 'COMMIT')
        else:
            stage('B_COMMAND_SENT_BEFORE_MARKER')
            good = exact_booleans(port.start_waiting_command('B', race['participants']['B']), {'before_marker_exact': True, 'command_sent': True, 'after_marker_absent': True})
            record['comparisons']['B_before_command'] = good; save(deepcopy(record)); require(good, 'BEFORE_COMMAND_NOT_PROVEN')
            stage('OBSERVE_NATIVE_WAIT_B_ON_A')
            value = port.observe_barrier(race['barrier'])
            wanted = race['barrier']['expected']
            good = (type(value) is dict and set(value) == set(wanted) | {'observations', 'within_deadline'} and
                    all(type(value[key]) is bool and value[key] is flag for key, flag in wanted.items()) and
                    type(value['observations']) is int and 1 <= value['observations'] <= race['barrier']['limits']['max_observations'] and value['within_deadline'] is True)
            record['comparisons']['actual_wait_barrier'] = good
            if type(value) is dict and type(value.get('observations')) is int and 0 <= value['observations'] <= 40: record['barrier_observations'] = value['observations']
            save(deepcopy(record)); require(good, 'CONCURRENT_WAIT_UNPROVEN')
            end('A', race['holder_outcome'])
            if race['holder_outcome'] == 'COMMIT':
                stage('B_EXPECT_NATIVE_DUPLICATE')
                value = port.finish_duplicate('B', race['native_duplicate_diagnostic'])
                keys = {'exit_code', 'acknowledged', 'sqlstate', 'schema_table_constraint_exact', 'native_location_exact', 'before_only_marker_exact', 'extra_output_absent'}
                good = (type(value) is dict and set(value) == keys and type(value['exit_code']) is int and value['exit_code'] == 3 and value['acknowledged'] is False and value['sqlstate'] == '23505' and
                        all(value[key] is True for key in ('schema_table_constraint_exact', 'native_location_exact', 'before_only_marker_exact', 'extra_output_absent')))
                record['comparisons']['native_unique_guard'] = good; record['B_exit_code'] = 3 if good else None; record['B_acknowledged'] = False if good else None
                save(deepcopy(record)); require(good, 'DUPLICATE_GUARD_UNPROVEN'); close('B')
            else:
                stage('B_COMMAND_RELEASED_AFTER_A_ROLLBACK')
                good = exact_booleans(port.finish_waiting_command('B'), {'before_after_markers_exact': True, 'acknowledged': True, 'transaction_open': True})
                record['comparisons']['B_waiting_command_released'] = good; save(deepcopy(record)); require(good, 'WAITING_COMMAND_DID_NOT_COMPLETE')
                ready('B', remainder=True); end('B', 'COMMIT')
        stage('COMPLETE_STATE_AFTER_BOTH_CLOSURES')
        value = port.observe_complete(race)
        wanted = {'counts': race['observer_expected'], 'winner_groups_coherent': True, 'winner_transaction_ids_match': True, 'all_triggers_restored': True, 'native_catalog_unchanged': True, 'issuer_grants_immutable': True}
        good = (type(value) is dict and set(value) == set(wanted) and type(value.get('counts')) is dict and set(value['counts']) == set(wanted['counts']) and
                all(type(value['counts'][key]) is int and value['counts'][key] == count for key, count in wanted['counts'].items()) and
                all(value[key] is True for key in wanted if key != 'counts'))
        record['comparisons']['complete_state'] = good; save(deepcopy(record)); require(good, 'COMPLETE_STATE_UNPROVEN')
        record['status'] = 'PROTOCOL_COMPLETED_NOT_RUNTIME_QUALIFICATION'; stage('COMPLETE')
    except (Exception, KeyboardInterrupt) as error:
        failure = error.code if isinstance(error, ProtocolStop) else 'UNEXPECTED_EXCEPTION'
    finally:
        if failure is not None:
            failed_stage = record['stage']; stage('CLOSE_REMAINING_AFTER_FAILURE')
            for side in ('B', 'A'):
                if side in opened and not record['closed'][side]:
                    try: close(side)
                    except Exception: failure = 'OPERATION_CLOSURE_UNCONFIRMED'
            if all(record['closed'][side] for side in opened):
                # A completed COMMIT may remain on an unexpected later failure.
                # Retain safe actual counts, never declare zero by assumption.
                try:
                    actual = port.observe_partial(race)
                    if type(actual) is dict and set(actual) == set(race['observer_expected']) and all(type(v) is int and 0 <= v <= 4 for v in actual.values()):
                        record['partial_counts'] = actual
                    else: record['partial_observation'] = 'UNSUPPORTED_DISCARDED'
                except Exception: record['partial_observation'] = 'UNAVAILABLE'
            record.update(status='STOPPED_PROTOCOL_ONLY', failure={'code': failure, 'stage': failed_stage}, subsequent_cases_stopped=True); save(deepcopy(record))
    return record


def run_packet(packet, port, save):
    report = {'status': 'SOURCE_PROTOCOL_ONLY', 'stage': 'ENTRY', 'database_assertions': 'NOT_RUN', 'results': [], 'subsequent_cases_stopped': False}
    save(deepcopy(report))
    try:
        require(type(packet) is dict and packet.get('schema') == 'workinants.unique-control-fixtures.v1' and packet.get('status') == 'NOT_RUN' and
                packet.get('selected_control_ids') == ['P0C-UNIQUE-01'] and tuple(race['name'] for race in packet.get('races', [])) == NAMES, 'PACKET_SCOPE')
        report['stage'] = 'PREFLIGHT'; save(deepcopy(report))
        required = {'source_and_packet_pins': True, 'immutable_target_identity': True, 'auth_finalization_native_parity': True, 'fresh_namespace': True, 'fixture_triggers_restored': True}
        require(exact_booleans(port.preflight(packet), required), 'PREFLIGHT_UNPROVED')
        report['stage'] = 'SYNTHETIC_IDENTITY_SETUP'; save(deepcopy(report))
        require(exact_booleans(port.seed_identity(packet), {'source_sql_exact': True, 'committed': True, 'backend_closed': True, 'all_triggers_restored': True}), 'FIXTURE_SETUP_UNPROVED')
        for race in packet['races']:
            result = run_race(race, port, save); report['results'].append(result)
            if result['status'] == 'STOPPED_PROTOCOL_ONLY': report['subsequent_cases_stopped'] = True; break
        report['stage'] = 'FINISHED_PROTOCOL_ONLY'; save(deepcopy(report))
    except (Exception, KeyboardInterrupt) as error:
        report.update(status='STOPPED_PROTOCOL_ONLY', subsequent_cases_stopped=True, failure={'code': error.code if isinstance(error, ProtocolStop) else 'UNEXPECTED_EXCEPTION', 'stage': report['stage']})
        save(deepcopy(report))
    return report
