"""Pure adapter for 132 independently audited, completed local ACL denials.

Only eleven models' three local provider simulations and four verbs qualify.
The stopped operation, RLS-empty probes, issuer umbrellas, owner workflows and
whole cases remain outside this adapter. No project code or process is run.
"""
import hashlib
import json
from pathlib import Path
import re

RECORD = 'context/reconciliation/local-f0-native-access-0a29cf6-495976eb-execution.json'
RECORD_SHA = 'e47ecfcc00064e22f2731c6a1e24ddc64df672690c2eabbb821d45c3aa5a6bdf'
AUDIT = 'context/reconciliation/local-f0-native-495976-independent-audit.json'
AUDIT_SHA = 'be88371125db2c00e35deefb9455980ae256de01cfef23774f907796b965dffd'
LINKS = 'context/reconciliation/local-f0-native-495976-exact132-links.json'
LINKS_SHA = '70f424c34a9bea67b1d740297819da5a1dd79157267d8658aa7447838fb90887'
INVENTORY = 'context/reconciliation/local-f0-assertions.json'
INVENTORY_SHA = '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558'
FINITE = 'review-output/native-table-denials-v2/packet.json'
FINITE_SHA = '8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'
COMMIT = '0a29cf607d320b96c7fad88bec8b97dde778e75c'
TREE = 'a950232d13a039fd2237e59e204399ebcc8293a4'
PACKET = '69c61577e538276b0c01eea7b24abe826fe5196fb5b996c1efff598abeab1baa'
SQL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

class EvidenceFailure(Exception):
    """Contains a fixed safe classification only."""

def need(value, code):
    if not value:
        raise EvidenceFailure(code)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def same(actual, expected, code):
    need(canonical(actual) == canonical(expected), code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read(root, relative, wanted):
    need(type(relative) is str and not Path(relative).is_absolute() and ':' not in relative and '\\' not in relative and all(p not in ('', '.', '..') for p in relative.split('/')), 'NATIVE_PREFIX_SAFE_PATH')
    path = root / relative
    need(not path.is_symlink() and path.resolve(strict=True).is_relative_to(root), 'NATIVE_PREFIX_SOURCE_PATH')
    raw = path.read_bytes()
    need(digest(raw) == wanted, 'NATIVE_PREFIX_PIN_DRIFT')
    return raw

def pointer(value, text):
    need(type(text) is str and text.startswith('/'), 'NATIVE_PREFIX_POINTER')
    for key in text[1:].split('/'):
        if type(value) is list:
            need(re.fullmatch('0|[1-9][0-9]*', key) is not None and int(key) < len(value), 'NATIVE_PREFIX_POINTER')
            value = value[int(key)]
        else:
            need(type(value) is dict and key in value, 'NATIVE_PREFIX_POINTER')
            value = value[key]
    return value

def validate_facet(link, facet, operation, control):
    """Typed mandatory observations; earlier schema ACL is the precise gate."""
    case = link['case_id']
    parts = link['assertion_id'].split('.')
    need(len(parts) == 3 and parts[0] == 'denial' and parts[1] in ('anon', 'authenticated', 'service_role') and parts[2] in ('select', 'insert', 'update', 'delete'), 'NATIVE_PREFIX_PROVIDER_CLAIM')
    role, verb = parts[1], parts[2].upper()
    need(type(facet) is dict and facet.get('case_id') == case and facet.get('role') == role and facet.get('verb') == verb, 'NATIVE_PREFIX_FACET_IDENTITY')
    need(facet.get('status') == 'PASS_OBSERVED_NATIVE_GATE_ONLY' and facet.get('whole_case_promoted') is False, 'NATIVE_PREFIX_FACET_SCOPE')
    same(facet.get('post_probe_observers'), {'operation_backend_absent': True, 'all_100_trigger_functions_restored': True, 'all_205_native_facts_unchanged': True}, 'NATIVE_PREFIX_POST_OBSERVERS')
    diagnostic = facet.get('diagnostic')
    need(type(diagnostic) is dict and diagnostic.get('matched') is True and diagnostic.get('sqlstate') == '42501' and diagnostic.get('observed_gate') == 'SCHEMA' and diagnostic.get('native_location') == 'aclcheck_error@aclchk.c' and diagnostic.get('selected_column_isolation_claimed') is False, 'NATIVE_PREFIX_INTENDED_NATIVE_GATE')
    need(type(operation) is dict and operation.get('closed_before_observers') is True and operation.get('actual_login_context_absent') is True and operation.get('source_sql_sha256') == link['finite_source_probe_sha256'], 'NATIVE_PREFIX_OPERATION_CLOSURE')
    need(operation.get('name') == 'deny-' + case.removeprefix('P0C-TABLE-').removesuffix('-DENY') + '-' + role + '-' + verb and operation.get('role') == role and type(operation.get('exit_code')) is int and operation['exit_code'] == 3 and operation.get('acknowledgement') is False, 'NATIVE_PREFIX_OPERATION_IDENTITY')
    same(operation.get('native_diagnostic'), diagnostic, 'NATIVE_PREFIX_OPERATION_DIAGNOSTIC')
    projection = operation.get('source_native_privilege_projection')
    need(type(projection) is dict and projection.get('schema_usage') is False and projection.get('required_permission_missing') is True and diagnostic.get('source_position_verified') is True, 'NATIVE_PREFIX_NATIVE_PRIVILEGES')
    same(control, {'case_id': case, 'status': 'NATIVE_CONSTRAINT_FIXTURE_VALIDITY_ONLY', 'insert_one': True, 'update_controls_one': 1, 'delete_one': True, 'rollback_and_restoration_proven': True}, 'NATIVE_PREFIX_NATIVE_CONTROL')

def validate_claim(case_id, assertion_id, status, execution, root, json_pointer=None):
    try:
        need(all(type(v) is str for v in (case_id, assertion_id, status)) and status == 'PASS', 'NATIVE_PREFIX_CLAIM_FIELDS')
        need(assertion_id.split('.')[0] == 'denial' and any(assertion_id.startswith('denial.' + role + '.') for role in ('anon', 'authenticated', 'service_role')), 'NATIVE_PREFIX_UNSUPPORTED_CLAIM')
        base = Path(root).resolve(strict=True)
        links = json.loads(read(base, LINKS, LINKS_SHA))['links']
        need(type(links) is list and len(links) == 132, 'NATIVE_PREFIX_CLOSED132')
        matches = [v for v in links if (v['case_id'], v['assertion_id']) == (case_id, assertion_id)]
        need(len(matches) == 1, 'NATIVE_PREFIX_UNSUPPORTED_CLAIM')
        link = matches[0]
        same(json_pointer, link['record_context_json_pointer'], 'NATIVE_PREFIX_CLAIM_POINTER')
        audit = json.loads(read(base, AUDIT, AUDIT_SHA))
        need(audit['mapping_counts'] == {'PASS': 132, 'PARTIAL': 0, 'whole_cases': 0}, 'NATIVE_PREFIX_AUDIT_SCOPE')
        original = json.loads(read(base, RECORD, RECORD_SHA))
        same(execution, original, 'NATIVE_PREFIX_EXACT_RETAINED_RECORD')
        need(execution['actual_result'] == 'STOPPED_ATTEMPT_PRESERVED', 'NATIVE_PREFIX_STOPPED_RECORD')
        same([execution[k] for k in ('source_commit', 'source_tree', 'packet_sha256')], [COMMIT, TREE, PACKET], 'NATIVE_PREFIX_SOURCE_CHECKPOINT')
        assets = {name: json.loads(read(base, name, h)) for name, h in execution['snapshot_files_sha256'].items()}
        need(len(assets) == 25, 'NATIVE_PREFIX_ASSET_SET')
        inventory = json.loads(read(base, INVENTORY, INVENTORY_SHA))
        source = [item for case in inventory['cases'] if case['id'] == case_id for item in case['assertions'] if item['id'] == assertion_id]
        need(len(source) == 1 and digest(source[0]['expected_assertion'].encode()) == link['expected_assertion_sha256'], 'NATIVE_PREFIX_ASSERTION_TEXT')
        need(digest(canonical(source[0]).encode()) == link['complete_source_assertion_sha256'], 'NATIVE_PREFIX_COMPLETE_ASSERTION')
        report = execution['sanitized_report']
        pins = report['source_verification']['files_sha256']
        need(len(pins) == 182 and digest(''.join(p + '\0' + pins[p] + '\n' for p in sorted(pins)).encode()) == PACKET, 'NATIVE_PREFIX_FULL_PACKET')
        for name, h in pins.items():
            read(base, name, h)
        need(report['packet_unchanged_after_run'] is True and report['tool_source_data_unchanged_after_run'] is True, 'NATIVE_PREFIX_SOURCE_PRESERVED')
        summary = report['cleanup_summary']
        need(summary['private_directory_absent'] is True and all(type(v) is bool and v is False for v in summary['resource_presence_after'].values()), 'NATIVE_PREFIX_CLEANUP_ABSENCE')
        need(report['catalog_comparison']['status'] == 'PASS' and report['ledger_comparison']['status'] == 'PASS', 'NATIVE_PREFIX_NATIVE_GATES')
        document = assets[link['facet_asset_path']]
        same(digest((json.dumps(document, indent=2) + '\n').encode()), link['facet_asset_sha256'], 'NATIVE_PREFIX_FACET_ASSET')
        facet, operation, control = [pointer(document, link[name]) for name in ('facet_json_pointer', 'operation_json_pointer', 'native_control_json_pointer')]
        validate_facet(link, facet, operation, control)
        packet = json.loads(read(base, FINITE, FINITE_SHA))
        cases = [v for v in packet['cases'] if v['id'] == case_id]
        need(len(cases) == 1, 'NATIVE_PREFIX_SOURCE_CASE')
        probes = [v for v in cases[0]['probes'] if v['role'] == facet['role'] and v['verb'] == facet['verb']]
        need(len(probes) == 1 and probes[0]['sql_sha256'] == link['finite_source_probe_sha256'], 'NATIVE_PREFIX_VALID_SOURCE_PROBE')
        need(digest((base/'review-output/foundation-application.review.sql').read_bytes()) == SQL, 'NATIVE_PREFIX_CANONICAL_SQL')
        return True
    except EvidenceFailure:
        raise
    except BaseException:
        raise EvidenceFailure('NATIVE_PREFIX_EVIDENCE_REJECTED') from None
