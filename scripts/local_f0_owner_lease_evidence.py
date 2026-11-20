"""Pure qualification of the exact Owner20 and Lease8 independently audited links.

The two builder records are explicitly derived wrappers around immutable raw
runtime reports. This adapter reads and compares bytes/JSON only. It runs no
project source, process, SQL or network operation. All unlisted outcomes remain
unqualified, including missing clock observations and compound revocation.
"""
import hashlib
import json
from pathlib import Path
import re
from collections import Counter

ARCHIVE = 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1'

AUDIT_PINS = {'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/catalog-audit-source.py.txt': '43996e8a33c10f5197164a548d5dfb411f988bdbdb2bd18eb228c900b30fae54',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/catalog-evidence-checks.json': 'b0eeb268da4a6cf4276a155902f9bf2e8981e768a69fa5d0b0fb8dae9665b3ad',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/catalog-proposal.json': 'c48230229e42eb91ec6a51392d80e10fffa4fd39d4b7bfcdc7b27f43c80102a3',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/catalog-review.json': '06b726d92c93f677b0ff8f6c474ecae8725bfed5d9f82129dbf5a4332404743d',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-approved-links.json': 'e42686608d376f64e16ec1315d876af5c346820412b467e565d166d1610dd330',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-audit-source.py.txt': '0b1e023bd5d8f55c936eead92e184a0f80d562d13515a1be0794ea4d1fb370f1',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-checks.json': '600c698f73f2a80151ffef8a3338dc73a658cf5eae8888b8bea7d51025510d2e',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-review.json': 'dd26a616fbc996ff9242ba09d73f1701fa1e81e3a7048f4dcf3ed83c331a74ed',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-source-scope-findings.json': '94e471d89a37f50f3a36c3508fa2e53855e6b0104c7db46dda0c9387bdafa1ea',
 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/preserved/assertion-evidence.before.json': '052207497a484b64a16cd8069a51e25e38ab82f516807c853f41c3737057fc44'}

FAMILIES = {'lease': {'actual_result': 'DERIVED_REVIEWED_LEASE8_FINITE_ASSERTIONS_ONLY',
           'asset_base': 'context/reconciliation/local-f0-run-assets/da5ad66-lease-a560e05b',
           'claims': 8,
           'component_relative': 'lease-revoke/lease-revoke-results.json',
           'component_sha256': 'a4cc2e14808ad6926fe687e441a02fb4a684446b40ad315b7e4d330889caa160',
           'container_id': 'e3a18552ebe176980d4b3873f6c1c6685e47884309cf89cbd6111fe710fdb37a',
           'counts': {'PARTIAL': 4, 'PASS': 4},
           'derived_record': 'context/reconciliation/local-f0-lease-da5ad66-a560e05b-qualified-evidence.json',
           'derived_sha256': '33a356710320b9ec5381085354b3ed0199e146685d12364c618e27cd7e9772bc',
           'manifest_sha256': '02d43c6029f3254f881076aaf2d5c3b0242e7d4c68d90f8041327cba02b545a5',
           'mapping': 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/catalog-proposal.json',
           'mapping_sha256': 'c48230229e42eb91ec6a51392d80e10fffa4fd39d4b7bfcdc7b27f43c80102a3',
           'packet_files': 167,
           'packet_sha256': '244bf11660a17697af91921f6d26e8c39fb3f4c98aaaaaa267e816d57c65302c',
           'raw_record': 'context/reconciliation/local-f0-lease-da5ad66-a560e05b-execution.json',
           'raw_record_sha256': 'c9e01ae2c1e6aaf0e9d054ac5b689a09bbc65ac2d5ed65893d8f90374cc0edbd',
           'run_id': 'a560e05b-7683-4780-9f59-a427b8f22edc',
           'source_commit': 'da5ad66cfc2bcb8aa64a453d10e29baeedb74a65',
           'source_tree': '6c28cd218487cac448805dee8a407f78056a0e22',
           'wrapper_result': 'PASS_FINITE_LEASE_AND_APP_CURRENTNESS_ONLY_CASES_NOT_RUN',
           'wrapper_sha256': 'c8619b46195d322902b512c9e2cce79a9f330363cf7fa1dd6954fd36a73237ca'},
 'owner': {'actual_result': 'DERIVED_REVIEWED_OWNER20_FINITE_ASSERTIONS_ONLY',
           'asset_base': 'context/reconciliation/local-f0-run-assets/da5ad66-owner-72934689',
           'claims': 20,
           'component_relative': 'owner-read-component/owner-read-results.json',
           'component_sha256': 'dbbb70ada0ce147f3803afaa5468bddd3d53edd219a5104f3eb02580dccffd38',
           'container_id': '34e993b9b3439d7f1e2bb4dddb8efa5d5a4542a8755558bf60ff760c1855310c',
           'counts': {'PARTIAL': 4, 'PASS': 16},
           'derived_record': 'context/reconciliation/local-f0-owner-da5ad66-72934689-qualified-evidence.json',
           'derived_sha256': '0effdedc5c26449d81eb49fa3581f54d57c13eb6e7ac889ce355fc3518f63c24',
           'manifest_sha256': 'd8ea014f725d6daa0e72e8b4e7a3ab22b82d138d81fc9311588b873c1ecda620',
           'mapping': 'context/reconciliation/local-f0-operation-sources/owner-lease-da5-evidence-adapter-v1/owner-approved-links.json',
           'mapping_sha256': 'e42686608d376f64e16ec1315d876af5c346820412b467e565d166d1610dd330',
           'packet_files': 635,
           'packet_sha256': 'd501acda503df1c17049a60a011e5d2487c24cb25cfcfd5d1c5178d1b5a710a3',
           'raw_record': 'context/reconciliation/local-f0-owner-da5ad66-72934689-execution.json',
           'raw_record_sha256': 'f9e20b2da4af9ec2bf9981f7ecd0fdca9392d91b8b242be75d72e54eadb7390b',
           'run_id': '72934689-cad5-4bee-beb4-1733224a51fb',
           'source_commit': 'da5ad66cfc2bcb8aa64a453d10e29baeedb74a65',
           'source_tree': '6c28cd218487cac448805dee8a407f78056a0e22',
           'wrapper_result': 'PASS_LOCAL_OWNER_READ_SQL_SUBSET_ONLY',
           'wrapper_sha256': 'c3550a19f089332727e7688324446e0315671e6a65ecf5cf69940c3b2b96e8be'}}

CLOSED_CLAIMS = {('P0C-CTX-01', 'vector.READ-PURPOSE-NO-WRITE.adversarial'): ('owner', 15, 'PASS'),
 ('P0C-CTX-01', 'vector.READ-PURPOSE-NO-WRITE.positive'): ('owner', 14, 'PARTIAL'),
 ('P0C-CTX-02', 'control.independent_service_currentness'): ('lease', 5, 'PASS'),
 ('P0C-CTX-02', 'control.revocation_schedule'): ('lease', 4, 'PARTIAL'),
 ('P0C-CTX-02', 'vector.SERVICE-REVOKE.adversarial'): ('lease', 7, 'PASS'),
 ('P0C-CTX-02', 'vector.SERVICE-REVOKE.positive'): ('lease', 6, 'PASS'),
 ('P0C-TABLE-CandidateProfile-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 1, 'PASS'),
 ('P0C-TABLE-ConsentContentRevision-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 7, 'PASS'),
 ('P0C-TABLE-ConsentContentRevision-ALLOW', 'vector.CONSENT-CONTENT-SCOPE.adversarial'): ('owner', 16, 'PARTIAL'),
 ('P0C-TABLE-ConsentLog-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 9, 'PASS'),
 ('P0C-TABLE-ConsentLog-ALLOW', 'vector.CONSENT-SCOPE-CHAIN.adversarial'): ('owner', 18, 'PARTIAL'),
 ('P0C-TABLE-ConsentPresentation-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 8, 'PASS'),
 ('P0C-TABLE-ConsentPresentation-ALLOW', 'vector.CONSENT-PRESENTATION-SCOPE.adversarial'): ('owner', 17, 'PARTIAL'),
 ('P0C-TABLE-PrivacyRequest-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 10, 'PASS'),
 ('P0C-TABLE-PrivacyRequest-ALLOW', 'separate_gate_denial.wa_app_runtime.privacy_completion'): ('owner', 19, 'PASS'),
 ('P0C-TABLE-ProfessionalProfile-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 0, 'PASS'),
 ('P0C-TABLE-TrackEntitlementDefinition-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 5, 'PASS'),
 ('P0C-TABLE-TrackEntitlementDefinition-ALLOW', 'positive.wa_worker.select'): ('owner', 12, 'PASS'),
 ('P0C-TABLE-TrackPlan-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 4, 'PASS'),
 ('P0C-TABLE-TrackPlan-ALLOW', 'positive.wa_worker.select'): ('owner', 11, 'PASS'),
 ('P0C-TABLE-TrackPlanEntitlement-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 6, 'PASS'),
 ('P0C-TABLE-TrackPlanEntitlement-ALLOW', 'positive.wa_worker.select'): ('owner', 13, 'PASS'),
 ('P0C-TABLE-User-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 2, 'PASS'),
 ('P0C-TABLE-UserSecurityProfile-ALLOW', 'positive.wa_app_runtime.select'): ('owner', 3, 'PASS'),
 ('P0C-TRACK-01', 'control.concurrent_fence'): ('lease', 3, 'PARTIAL'),
 ('P0C-TRACK-01', 'control.lease_transitions'): ('lease', 2, 'PARTIAL'),
 ('P0C-TRACK-01', 'vector.LEASE-RENEW.adversarial'): ('lease', 1, 'PARTIAL'),
 ('P0C-TRACK-01', 'vector.LEASE-RENEW.positive'): ('lease', 0, 'PASS')}

INVENTORY = 'context/reconciliation/local-f0-assertions.json'

INVENTORY_SHA = '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558'

SQL_PATH = 'review-output/foundation-application.review.sql'

SQL_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

ACCESS_PATH = 'context/reconciliation/foundation-sql-draft-access.json'

ACCESS_SHA = 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea'

LEASE_OPERATION_CONTRACTS = [('worker-claim',
  'wa_worker',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_WORKER_CLAIM', 'WA_LR_AFTER_WORKER_CLAIM']}),
 ('worker-renew',
  'wa_worker',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_WORKER_RENEW', 'WA_LR_AFTER_WORKER_RENEW']}),
 ('live-reclaim-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 23,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_LIVE_RECLAIM_DENIED']}),
 ('expired-renew-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 31,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_EXPIRED_RENEW_DENIED']}),
 ('concurrent-reclaim-stale-holder',
  'wa_worker',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_CONCURRENT_RECLAIM_STALE_HOLDER', 'WA_LR_AFTER_CONCURRENT_RECLAIM_STALE_HOLDER']}),
 ('concurrent-reclaim-stale-holder',
  'wa_worker',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_CONCURRENT_RECLAIM_STALE_HOLDER', 'WA_LR_AFTER_CONCURRENT_RECLAIM_STALE_HOLDER']}),
 ('current-holder-renew',
  'wa_worker',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_CURRENT_HOLDER_RENEW', 'WA_LR_AFTER_CURRENT_HOLDER_RENEW']}),
 ('shorten-renew-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 31,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_SHORTEN_RENEW_DENIED']}),
 ('copied-hash-renew-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 31,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_COPIED_HASH_RENEW_DENIED']}),
 ('old-secret-renew-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 31,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_OLD_SECRET_RENEW_DENIED']}),
 ('hash-change-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 23,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_HASH_CHANGE_DENIED']}),
 ('attempt-only-denied',
  'wa_worker',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 25,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_ATTEMPT_ONLY_DENIED']}),
 ('app-bound-before-rotate',
  'wa_app_runtime',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 8,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_APP_BOUND_BEFORE_ROTATE']}),
 ('app-bound-before-revoke',
  'wa_app_runtime',
  {'acknowledged': False,
   'diagnostic': {'classification': 'SOURCE_EXACT_GUARD',
                  'matched': True,
                  'source_body_line': 8,
                  'source_body_sha256': '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038',
                  'source_guard': 'runtime_transition',
                  'sqlstate': 'P0001'},
   'exit_code': 3,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_APP_BOUND_BEFORE_REVOKE']}),
 ('app-fresh-after-recover',
  'wa_app_runtime',
  {'acknowledged': True,
   'comparisons': {'row_count_matches': True, 'shape_and_values_match': True},
   'exit_code': 0,
   'matched': True,
   'stage_markers': ['WA_LR_BEFORE_APP_FRESH_AFTER_RECOVER', 'WA_LR_AFTER_APP_FRESH_AFTER_RECOVER']})]

class EvidenceFailure(Exception):
    """A fixed classification, never input values, probe text or file names."""


def need(value, code):
    if not value:
        raise EvidenceFailure('OWNER_LEASE_' + code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def same(actual, expected, code):
    need(canonical(actual) == canonical(expected), code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'JSON_DUPLICATE_KEY')
        result[key] = value
    return result


def document(raw):
    def invalid(_):
        raise EvidenceFailure('OWNER_LEASE_JSON_NONFINITE')
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=invalid)


def read(root, relative, wanted):
    need(type(relative) is str and relative and ':' not in relative and '\\' not in relative
         and all(part not in ('', '.', '..') for part in relative.split('/')),
         'SAFE_PATH')
    need(type(wanted) is str and re.fullmatch('[0-9a-f]{64}', wanted) is not None, 'HASH_TYPE')
    path = root
    for part in relative.split('/'):
        path = path / part
        need(not path.is_symlink(), 'SOURCE_PATH')
    need(path.resolve(strict=True).is_relative_to(root) and path.is_file(), 'SOURCE_PATH')
    need(path.stat().st_size <= 32 * 1024 * 1024, 'SOURCE_SIZE')
    raw = path.read_bytes()
    need(digest(raw) == wanted, 'PIN_DRIFT')
    return raw


def pointer(value, text):
    need(type(text) is str and text.startswith('/'), 'POINTER')
    for key in text[1:].split('/'):
        # The closed audit pointers contain no JSON Pointer escapes or aliases.
        if type(value) is list:
            need(re.fullmatch('0|[1-9][0-9]*', key) is not None and int(key) < len(value), 'POINTER')
            value = value[int(key)]
        else:
            need(type(value) is dict and key in value, 'POINTER')
            value = value[key]
    return value


def _identity(value, cfg, packet_key):
    same([value[k] for k in ('run_id', 'source_commit', 'source_tree')],
         [cfg[k] for k in ('run_id', 'source_commit', 'source_tree')], 'RUN_SOURCE_IDENTITY')
    same(value[packet_key], cfg['packet_sha256'], 'PACKET_IDENTITY')


def _authentication(component):
    roles = ['postgres', 'wa_migrator', 'wa_context_issuer', 'wa_identity_service_authority', 'wa_app_runtime', 'wa_worker']
    same(component['authentication'], [dict(role=role, transport='TCP_127.0.0.1_5432',
         correct_password='PASS_SCRAM', wrong_password='PASS_REJECTED', wrong_password_exit_code=2)
         for role in roles], 'AUTHENTICATION')
    same(component['effective_hba_selections'], [dict(role=role, address=address,
         rule_number=number, method='scram-sha-256') for address, number in [('127.0.0.1', 2), ('::1', 3)]
         for role in roles], 'HBA')
    same(component['authentication_comparison'], {key: True for key in
         ('json_parsed', 'object', 'fields', 'string_fields', 'login', 'scram_identity', 'database', 'client_loopback', 'server_loopback')},
         'AUTH_COMPARISONS')


def _common(raw, wrapper, component, cfg):
    """Typed local source/run/CID, finalization, native, closure and cleanup gates."""
    _identity(raw, cfg, 'operation_packet_sha256')
    _identity(component, cfg, 'packet_sha256')
    need(component['container_id'] == cfg['container_id'], 'CID')
    need(raw['actual_wrapper_status'] == cfg['wrapper_result'], 'RAW_STATUS')
    need(component['database_posture'] == 'D' and component['current_stage'] == 'COMPLETE'
         and component['subsequent_cases_stopped'] is False, 'COMPLETE_FINITE_SCOPE')
    same([wrapper[k] for k in ('run_id', 'approved_commit', 'approved_tree', 'approved_packet_sha256')],
         [cfg[k] for k in ('run_id', 'source_commit', 'source_tree', 'packet_sha256')], 'WRAPPER_IDENTITY')
    need(wrapper['unexpected'] == [] and wrapper['persistence_failure'] is False, 'WRAPPER_COMPLETE')
    need(wrapper['packet_unchanged_after_run'] is True and wrapper['tool_source_data_unchanged_after_run'] is True,
         'SOURCE_PRESERVATION')
    comparison = wrapper['catalog_comparison']
    need(comparison['status'] == 'PASS' and comparison['findings'] == [] and
         type(comparison['check_counts']['PASS']) is int and comparison['check_counts']['PASS'] == 29089,
         'NATIVE_CATALOG')
    need(wrapper['ledger_comparison']['status'] == 'PASS' and len(wrapper['ledger_comparison']['checks']) == 22
         and all(row['status'] == 'PASS' and row['expected_sha256'] == row['actual_sha256']
                 for row in wrapper['ledger_comparison']['checks']), 'LEDGER')
    targets = list(wrapper['targets'].values())
    need(len(targets) == 1, 'TARGET_SET')
    target = targets[0]
    need(target['container_id'] == cfg['container_id'] and target['labels']['workinants.rehearsal.run'] == cfg['run_id']
         and target['network_mode'] == 'none' and target['published_ports'] is False, 'TARGET_IDENTITY')
    same(target['finalization_observation'], dict(auth='scram-sha-256:postgres', grantor='postgres',
         leaf_create=dict(wa_track_verifier=False, wa_customer_verifier=False, wa_private_helper_owner=False),
         remaining_memberships=0, active_install_connections=0), 'ORIGINAL_GRANTOR_FINALIZATION')
    need(wrapper['backend_closures'] and all(row['scope'] == 'ALL_DATABASES_ALL_ROLES_ALL_TAGS'
         and all(row[key] is True for key in ('observation_completed', 'counts_valid', 'migrator_zero',
         'other_clients_zero', 'all_other_client_backends_absent')) for row in wrapper['backend_closures']), 'BACKEND_CLOSURE')
    summary = wrapper['cleanup_summary']
    need(summary['private_directory_absent'] is True and summary['image_removed'] is False
         and summary['unrelated_resources_changed'] is False and len(summary['resource_presence_after']) == 2
         and all(value is False for value in summary['resource_presence_after'].values()), 'CLEANUP')
    _authentication(component)


def _owner(component, fixture):
    need(component['status'] == 'PASS_FINITE_OWNER_READ_SQL_SUBSET_ONLY' and component['unexpected'] == []
         and component['current_case'] is None and component['fixture_owner_bypass_restored'] is True
         and component['source_packet_unchanged_after'] is True, 'OWNER_COMPLETION')
    results, operations = component['results'], component['operations']
    need(len(results) == len(fixture['cases']) == 121 and len(operations) == 964, 'OWNER_FINITE_SET')
    counts = Counter(row['stage'] for row in operations)
    same({key: counts[key] for key in ('BOUND_OPERATION', 'SEPARATE_ISSUER_COMMIT',
         'IMMUTABLE_ISSUER_RETENTION', 'GLOBAL_BACKEND_CLOSURE')},
         dict(BOUND_OPERATION=128, SEPARATE_ISSUER_COMMIT=128, IMMUTABLE_ISSUER_RETENTION=378, GLOBAL_BACKEND_CLOSURE=294),
         'OWNER_OPERATION_COUNTS')
    baseline = component['baseline']['tables']
    need(len(baseline) == 41 and digest(canonical(baseline).encode()) == component['baseline']['sha256'] ==
         '588bed280aa2d86b2e38b2f698201912db90303d5ca6cf33452a47846bacb28f', 'OWNER_BASELINE')
    after = json.loads(canonical(baseline))
    after['platform.runtime_work_item']['rows_sha256'] = '1cd41e252afbd1cd08994a817f1d87eb2b47e69318b0d8f21b138e73e63aee5e'
    worker_baseline = digest(canonical(after).encode())
    need(worker_baseline == 'bba1316967019fe2fee6be93e759da11e397d191a0b39050819ae026b2caec59', 'OWNER_WORKER_BASELINE')
    for result, case in zip(results, fixture['cases']):
        need(result['case'] == case['name'] and result['actual_login'] == case['actual_login']
             and result['actual_login'] in ('wa_app_runtime', 'wa_worker'), 'OWNER_ACTUAL_ROLE')
        need(result['status'] == 'PASS_PREPARED_SQL_SUBSET_ONLY' and result['operation_closed_before_observation'] is True
             and result['complete_result_match'] is True and type(result['tables_observed']) is int
             and result['tables_observed'] == 41, 'OWNER_COMPLETE_STATE')
        need(result['complete_state_sha256'] == (worker_baseline if case['actual_login'] == 'wa_worker' else component['baseline']['sha256']),
             'OWNER_COMPLETE_STATE_BASELINE')
        need(type(result['grants_retained']) is int and 7 <= result['grants_retained'] <= 128, 'OWNER_ISSUER_COUNT')
        guard = result['expected_guard']
        same(result['stage_markers'], dict(before=True, after=guard is None), 'OWNER_STAGE_MARKERS')
        if guard is None:
            same(result['counts'], case['expected'], 'OWNER_RESULT_COUNTS')
        else:
            name = result['case']
            need(name in ('presentation-query-insert', 'content-query-insert', 'privacy-completion-gate'), 'OWNER_GUARD_NAME')
            same(guard, dict(matched=True, sqlstate='0A000' if name == 'privacy-completion-gate' else '42501',
                 classification=name, source_frame_verified=name == 'privacy-completion-gate',
                 body_sha256='82a218fcb0bc0ac023b75411a44697545ca77016e9d3cb6fa80402b8220a670b' if name == 'privacy-completion-gate' else None,
                 body_line=26 if name == 'privacy-completion-gate' else None), 'OWNER_INTENDED_DIAGNOSTIC')
    need(results[-1]['grants_retained'] == 128, 'OWNER_RETAINED_GRANTS')
    for operation in operations:
        stage = operation['stage']
        if stage == 'BOUND_OPERATION':
            need(operation['actual_login'] in ('wa_app_runtime', 'wa_worker')
                 and type(operation['terminal_exit']) is int and operation['terminal_exit'] in (0, 3)
                 and all(operation[key] is True for key in ('issuer_committed', 'same_tuple_verified', 'operation_closed', 'result_validated')),
                 'OWNER_BOUND_TUPLE_CLOSURE')
        elif stage == 'SEPARATE_ISSUER_COMMIT':
            need(all(operation[key] is True for key in ('issuer_committed', 'commit_acknowledged', 'created_at_return_verified', 'operation_closed')),
                 'OWNER_ISSUER_COMMIT')
        elif stage == 'IMMUTABLE_ISSUER_RETENTION':
            need(type(operation['instances']) is int and operation['instances'] > 0
                 and all(operation[key] is True for key in ('all_21_fields_match', 'issuer_owned', 'unrevoked'))
                 and (operation['unexpired_required'] is False or operation['current_unexpired_match'] is True), 'OWNER_ISSUER_RETENTION')
        elif stage == 'GLOBAL_BACKEND_CLOSURE':
            need(operation['other_clients_zero'] is True, 'OWNER_GLOBAL_CLOSURE')


def _lease(component):
    need(component['status'] == 'COMPLETED_FINITE_LEASE_AND_APP_CURRENTNESS_ONLY_CASES_NOT_RUN'
         and component['source_packet_unchanged_after_run'] is True, 'LEASE_COMPLETION')
    need(len(component['results']) == 19 and len(component['operations']) == 327, 'LEASE_FINITE_SET')
    need(all(row['status'] == 'PASS_FINITE_SQL_PROTOCOL_ONLY_SELECTED_CASE_NOT_RUN' for row in component['results']), 'LEASE_RESULT_SCOPE')
    counts = Counter(row['stage'] for row in component['operations'])
    same({key: counts[key] for key in ('ACTUAL_OPERATION', 'SEPARATE_ISSUER_COMMIT', 'ISSUER_RETENTION',
         'NO_ATTEMPTS_OR_TRACK_EFFECTS', 'WORK_COMPLETE_STATE', 'NATIVE_CATALOG_PRESERVATION', 'GLOBAL_CLIENT_CLOSURE')},
         dict(ACTUAL_OPERATION=15, SEPARATE_ISSUER_COMMIT=25, ISSUER_RETENTION=19, NO_ATTEMPTS_OR_TRACK_EFFECTS=19,
         WORK_COMPLETE_STATE=47, NATIVE_CATALOG_PRESERVATION=20, GLOBAL_CLIENT_CLOSURE=20), 'LEASE_OPERATION_COUNTS')
    actual_operations = [operation for operation in component['operations'] if operation['stage'] == 'ACTUAL_OPERATION']
    same([(operation['name'], operation['actual_login'], operation['outcome']) for operation in actual_operations],
         LEASE_OPERATION_CONTRACTS, 'LEASE_EXACT_OPERATION_CONTRACTS')
    for operation in component['operations']:
        stage = operation['stage']
        if stage == 'ACTUAL_OPERATION':
            need(operation['actual_login'] in ('wa_worker', 'wa_app_runtime') and operation['operation_closed'] is True, 'LEASE_ACTUAL_ROLE_CLOSURE')
            outcome = operation['outcome']
            need(type(outcome['exit_code']) is int and outcome['exit_code'] in (0, 3)
                 and outcome['matched'] is True and type(outcome['stage_markers']) is list and outcome['stage_markers'], 'LEASE_OUTCOME')
            need(outcome['acknowledged'] is (outcome['exit_code'] == 0), 'LEASE_ACKNOWLEDGEMENT')
            if outcome['exit_code'] == 3:
                diagnostic = outcome['diagnostic']
                need(diagnostic['matched'] is True and diagnostic['sqlstate'] == 'P0001'
                     and type(diagnostic['source_body_line']) is int
                     and diagnostic['classification'] == 'SOURCE_EXACT_GUARD', 'LEASE_INTENDED_DIAGNOSTIC')
        elif stage == 'SEPARATE_ISSUER_COMMIT':
            need(all(operation[key] is True for key in ('issuer_committed', 'commit_acknowledged', 'created_at_return_verified', 'operation_closed')), 'LEASE_ISSUER_COMMIT')
        elif stage == 'ISSUER_RETENTION':
            need(type(operation['count']) is int and 1 <= operation['count'] <= 25 and operation['exact_fields_and_declared_revocations'] is True, 'LEASE_ISSUER_RETENTION')
        elif stage == 'NATIVE_CATALOG_PRESERVATION':
            need(operation['unchanged'] is True, 'LEASE_NATIVE_PARITY')
        elif stage == 'GLOBAL_CLIENT_CLOSURE':
            need(operation['scope'] == 'ALL_DATABASES_ALL_ROLES_ALL_TAGS' and operation['observation_completed'] is True
                 and operation['all_other_client_backends_absent'] is True, 'LEASE_GLOBAL_CLOSURE')
        elif stage == 'ALL_OWNED_OPERATION_CLOSURES':
            need(operation['all_original_sessions_closed'] is True, 'LEASE_OWNED_CLOSURE')
        elif stage == 'TRIGGER_RESTORATION':
            need(operation['shape_and_values_match'] is True and operation['observation']['fields_match'] is True
                 and operation['observation']['values']['no_project_user_trigger_disabled'] is True, 'LEASE_TRIGGER_RESTORATION')
        elif stage == 'APP_ISSUER_REVOCATION':
            same(operation, dict(stage=stage, issuer_commit_before_protected_statement=True,
                 protected_rows_disclosed=0, operation_closed=True), 'LEASE_APP_REVOCATION_ONLY')


def _claim_projection(row, family, cfg, mapping_index):
    result = dict(case_id=row['case_id'], assertion_id=row['assertion_id'],
         status=row['proposed_exact_evidence_classification'], expected_assertion_sha256=row['expected_assertion_sha256'],
         complete_source_assertion_sha256=row['exact_assertion_snapshot_sha256'],
         independent_mapping=dict(path=cfg['mapping'], sha256=cfg['mapping_sha256'], json_pointer='/rows/' + str(mapping_index)),
         component=dict(path=cfg['asset_base'] + '/evidence/' + cfg['component_relative'], sha256=cfg['component_sha256']),
         source_case_results=row['source_case_results'], source_operation_pointers=row['source_operation_pointers'],
         remaining_limits=row['remaining_limits'], whole_case_promoted=False)
    if family == 'owner':
        result['actual_bound_operation_pointers'] = row['actual_bound_operation_pointers']
    return result


def _validate_claims(execution, mapping, family, cfg, inventory, component):
    source_items = {(case['id'], item['id']): item for case in inventory['cases'] for item in case['assertions']}
    rows = [(index, row) for index, row in enumerate(mapping['rows']) if family == 'owner' or row['family'] == 'lease']
    need(len(rows) == cfg['claims'] == len(execution['claims']), 'CLOSED_CLAIM_COUNT')
    same(Counter(claim['status'] for claim in execution['claims']), cfg['counts'], 'PARTIAL_CAPS')
    for index, ((mapping_index, row), claim) in enumerate(zip(rows, execution['claims'])):
        key = (claim['case_id'], claim['assertion_id'])
        need(CLOSED_CLAIMS.get(key) == (family, index, claim['status']), 'CLOSED_CLAIM_STATUS')
        same(claim, _claim_projection(row, family, cfg, mapping_index), 'AUDITED_CLAIM_PROJECTION')
        item = source_items[key]
        need(digest(item['expected_assertion'].encode()) == claim['expected_assertion_sha256']
             and digest(canonical(item).encode()) == claim['complete_source_assertion_sha256'], 'EXACT_REQUIREMENT')
        for case_pointer in claim['source_case_results']:
            result = pointer(component, case_pointer['json_pointer'])
            need(result.get('case', result.get('name')) == case_pointer['source_case_name'], 'RESULT_POINTER')
        for operation_pointer in claim['source_operation_pointers']:
            need(type(pointer(component, operation_pointer)) is dict, 'OPERATION_POINTER')
        if family == 'owner':
            for bound in claim['actual_bound_operation_pointers']:
                operation = pointer(component, bound['json_pointer'])
                need(operation['stage'] == 'BOUND_OPERATION' and operation['case'] == bound['source_case_name'], 'BOUND_OPERATION_POINTER')


def validate_claim(case_id, assertion_id, status, execution, root, json_pointer=None):
    """Admit one of exactly 28 capped, independently reviewed assertion links."""
    try:
        need(all(type(value) is str for value in (case_id, assertion_id, status)), 'CLAIM_FIELDS')
        selected = CLOSED_CLAIMS.get((case_id, assertion_id))
        need(selected is not None, 'UNSUPPORTED_CLAIM')
        family, index, cap = selected
        need(status == cap, 'STATUS_CAP')
        need(json_pointer == '/claims/' + str(index), 'CLAIM_POINTER')
        cfg = FAMILIES[family]
        base = Path(root).resolve(strict=True)
        retained = document(read(base, cfg['derived_record'], cfg['derived_sha256']))
        same(execution, retained, 'EXACT_DERIVED_RECORD')
        _identity(execution, cfg, 'packet_sha256')
        need(execution['actual_result'] == cfg['actual_result'] and execution['raw_record_fields_invented'] is False
             and execution['derivation'] == 'EXPLICIT_DERIVED_WRAPPER_NOT_A_RAW_RUNTIME_REPORT', 'DERIVED_IDENTITY')
        same(execution['limits'], dict(Posture='D', whole_case_or451_promotion=False,
             unlisted_runtime_outcomes_qualified=False, fixture_setup_writes_qualified=False,
             worker_plus_app_dual_record_revocation_combined=False, missing_clock_facts_invented=False), 'FINITE_LIMITS')
        same(execution['independent_audit_artifacts_sha256'], AUDIT_PINS, 'AUDIT_SET')
        audits = {name: read(base, name, wanted) for name, wanted in AUDIT_PINS.items()}
        owner_review = document(audits[ARCHIVE + '/owner-review.json'])
        catalog_review = document(audits[ARCHIVE + '/catalog-review.json'])
        need(owner_review['decision'] == 'ACCEPT_EXACT20_OWNER_ASSERTION_LINKS_WITH_EXPLICIT_FINITE_LIMITS'
             and catalog_review['decisions']['lease'] == 'INDEPENDENT_FINITE_ACTUAL_EVIDENCE_ACCEPTED_WITH_EXPLICIT_CLOCK_AND_COMPOUND_LIMITS', 'INDEPENDENT_DECISIONS')
        raw = document(read(base, cfg['raw_record'], cfg['raw_record_sha256']))
        need('actual_result' not in raw and 'packet_sha256' not in raw, 'IMMUTABLE_RAW_SCHEMA')
        same(execution['source_record'], dict(path=cfg['raw_record'], sha256=cfg['raw_record_sha256'],
             raw_wrapper_status=cfg['wrapper_result'], packet_field_in_raw_record='operation_packet_sha256'), 'RAW_REFERENCE')
        assets = {name: read(base, name, wanted) for name, wanted in raw['assets_sha256'].items()}
        need(len(assets) == (27 if family == 'owner' else 26), 'ASSET_SET')
        manifest = document(assets[cfg['asset_base'] + '/manifest/operation-manifest.json'])
        need(digest(assets[cfg['asset_base'] + '/manifest/operation-manifest.json']) == cfg['manifest_sha256'], 'MANIFEST_HASH')
        _identity(manifest, cfg, 'packet_sha256')
        pins = manifest['packet_files_sha256']
        need(len(pins) == cfg['packet_files'] and digest(''.join(name + '\0' + pins[name] + '\n'
             for name in sorted(pins)).encode()) == cfg['packet_sha256'], 'COMPLETE_PACKET')
        for name, wanted in pins.items():
            read(base, name, wanted)
        inventory = document(read(base, INVENTORY, INVENTORY_SHA))
        read(base, SQL_PATH, SQL_SHA)
        read(base, 'prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql', SQL_SHA)
        read(base, ACCESS_PATH, ACCESS_SHA)
        wrapper_raw = assets[cfg['asset_base'] + '/evidence/run-evidence.json']
        component_raw = assets[cfg['asset_base'] + '/evidence/' + cfg['component_relative']]
        need(digest(wrapper_raw) == cfg['wrapper_sha256'] and digest(component_raw) == cfg['component_sha256'], 'COMPONENT_WRAPPER_PINS')
        wrapper, component = document(wrapper_raw), document(component_raw)
        _common(raw, wrapper, component, cfg)
        if family == 'owner':
            fixture = document(read(base, 'review-output/owner-read-control-rehearsal/fixtures.json',
                 '7f8d292ddc8ca11e12ae91e94ac62cca6cdd09d0c1f8a427ac5eefa414e66aca'))
            _owner(component, fixture)
        else:
            _lease(component)
        _validate_claims(execution, document(audits[cfg['mapping']]), family, cfg, inventory, component)
        return True
    except EvidenceFailure:
        raise
    except Exception:
        raise EvidenceFailure('OWNER_LEASE_EVIDENCE_REJECTED') from None
