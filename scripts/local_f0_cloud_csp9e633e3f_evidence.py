"""Read-only admission of the single assertion supported by the closed Cloud CSP run."""

import copy
import hashlib
import json
import math
import os
import re
import stat
from pathlib import Path
from types import MappingProxyType


ASSET = 'context/reconciliation/cloud-phase0-evidence/2026-11-27/csp-9e633e3f'
DERIVED = f'{ASSET}/qualified-evidence.json'
FROZEN = 'context/reconciliation/local-f0-source-followups/695-privilege44-admission-20261123'
PLAN = f'{FROZEN}/CSP-maxone-admission-plan.FROZEN.json'
ACK = f'{FROZEN}/CSP-maxone-admission-Root-ACK.json'
INVENTORY = 'context/reconciliation/local-f0-assertions.json'
LEDGER = 'context/reconciliation/local-f0-assertion-evidence.json'
BOARD = 'context/reconciliation/local-f0-qualification-status.json'
BUILDER = 'scripts/prepare-local-f0-status.py'
BASELINE_LEDGER = '8c285f6ac5cf6579d9ee58e480d64a75fe67034c22661fa1984c35125f9f12d7'
BASELINE_BOARD = 'a3a09332a1e8d34c56cd4f85bd2fe30c5665a5c73c49907d9715874a4b08c27a'
BASELINE_BUILDER = '977ccb4b26d2bcbd3ff8c4bd84e9a7e741dbf642e8c8fb558c423f8d634ad83f'
RUN = '9e633e3f-9c60-4c6d-a90d-85a368d71500'
FIXTURE = '75642d48-a698-4a69-84f9-d1fe013d097a'
COMMIT = 'a3318b28977740be397d5663880f94c52d05c7dd'
TREE = '24a012554f2fec2578417080e8c9d4592a24887f'
PACKET = '7f47db109ade8949285466d6971327c64e60a1bec4f9d8e5c74a378560fd0728'
CONTAINER_ID = 'ecd715047a298c715c90dbdf4ea1bef1a479a5b72acdbb219c909c5fead177ab'
TARGET = f'wa-p0c-cloud-csp-{RUN}'
VOLUME = f'{TARGET}-data'
DATABASE = 'wa_p0c_rehearsal'
APPLICATION = 'review-output/foundation-application.review.sql'
APP_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
SOURCE_EXPECTED = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'
NATIVE = '7f183bd1a745933de51f5d3f1798fbc01885ad7a2cde34c347160e61a8199303'
REGISTRATION = '46cab64842c4ecac62286cf3537ed499240624bb25ef520384339c80671164ad'
INSTALLER = '2030b10e5c0ecc7657d41b44707196b265d08055fa901eb7a58a64e941c72524'
STATE = 'fafe945d42fd8108bc468719861aa05d73c032b3c2b1b2c66e1b3ab58e58aefa'
ENGINE = 'd1b3f377ca835d73fd50954a5e22128b9ebdd6b8'
TOOL_ARCHIVE = '5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5'
CASE = 'P0C-CAS-01'
ASSERTION = 'control.stale_predecessor'
EXPECTED = '72f2d75ee3f9af764982f379f5dc82805531d09dc85f0925f8d7c6ab69795d3e'
KIND = 'DERIVED_REVIEWED_CLOUD_CSP_THREE_ROLLBACK_CONTROLS_ONE_ASSERTION_ONLY'
RAW_PASS = 'PASS_CSP1_THREE_ROLLBACK_CONTROLS_ONLY'
SCOPE = 'Cloud rehearsal of the three rollback-only Customer predecessor controls.'
LIMIT = 'THREE_ROLLBACK_CONTROLS_ONLY'
CONTROLS = ('wrong-predecessor', 'skipped-revision', 'same-grant-second-source-update')
ROLES = ('postgres', 'wa_migrator', 'wa_context_issuer', 'wa_identity_service_authority', 'wa_app_runtime', 'wa_worker')
CHILD = 'evidence/customer-stale-component/customer-stale-predecessor-results.json'
PARENT = 'evidence/run-evidence.json'
MAX_FILE = 3 * 1024 * 1024
MAX_BUNDLE = 15 * 1024 * 1024

_ASSET_PINS = MappingProxyType({
    'attempt.json': 'd9f266154df6ae84efb2c5fde329bed3e62292fb8e61879dd2718a15f76c6bc9',
    'evidence/acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
    'evidence/catalog-comparison.json': 'edae18fa298beff66f2df65cfc7131904aeed6f8a89e6dddb8b89cd53006f633',
    CHILD: '95fd029dcb26bedb56270a2c356a30e0aaf98a06e5076b26e5cc48f0bc4d59ae',
    'evidence/customer-stale-component-summary.json': '4a1ad30c7943591c2916408de7797c23d38c5136902dfbeaac64eb7f95dcc8e6',
    'evidence/customer-stale-native-attestation.json': 'a9f405395ae21c9b31dd43eb5bca1f4fb745c8ba87e987f2881619ac992ea540',
    'evidence/customer-stale-run-plan.json': '13e5796fc9467365c342f8f3a08356cc87be3592022427cfe6ec42601698c5a4',
    'evidence/ledger-evidence.json': 'bd506b9f3156e5e5b912af8c96c698c85b001a259a5abe0b7097b6da7fdd9519',
    'evidence/ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
    'evidence/ledger-registration.json': 'e4be1754c7f7b217e65f114b9c8b54418b79c73386a0be9936b840ff3caa186d',
    'evidence/native-after-ledger.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/native-after-oracle.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/native-before.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
    'evidence/oracle-evidence.json': '0bd7c39f920c7088adcdc77658022e2b78ca49ae6f84b3de205ab696f5827b12',
    'evidence/oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
    'evidence/oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
    'evidence/post-catalog-comparison.json': 'edae18fa298beff66f2df65cfc7131904aeed6f8a89e6dddb8b89cd53006f633',
    'evidence/post-ledger-evidence.json': 'bd506b9f3156e5e5b912af8c96c698c85b001a259a5abe0b7097b6da7fdd9519',
    'evidence/post-ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
    'evidence/post-native-after-ledger.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/post-native-after-oracle.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/post-native-before.json': '24cf2f60e9c6a396d53b8f897b0aa6feea6b8498a1f231eb0241fc6e157d0eb0',
    'evidence/post-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
    'evidence/post-oracle-evidence.json': '0bd7c39f920c7088adcdc77658022e2b78ca49ae6f84b3de205ab696f5827b12',
    'evidence/post-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
    'evidence/post-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
    'evidence/post-state-after.json': '351255690b80a99b342a3e9407e22ff2c8ddd3d0dbd6e8a4965dfd127748ee3f',
    'evidence/post-state-before.json': '351255690b80a99b342a3e9407e22ff2c8ddd3d0dbd6e8a4965dfd127748ee3f',
    PARENT: '151b1d325ece9dc74769d5ed3d960150635c430e4863151f96902da9df245169',
    'evidence/text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
    'independent-closure.json': 'ff6b0908716d895cdfc7bcad3a665484b35d529d0cfbb0c5f3e5d55d08511310',
    'independent-review.json': 'be82d00220579561f3a1a880afc60de61047cccbdbe66c742aafda3ca953f068',
    'operation-exit.json': 'd826b746e29d7f86ce564c07d81ff1640010b8619ad0b25364a5edc845edd42d',
    'operation-plan.json': 'eca80490adb8b2831e69d901d5c6c48fe2bdcacc491aca5fff8ee1d7dd5b57e3',
})
RAW_PINS = MappingProxyType({
    **{f'{ASSET}/{name}': sha256 for name, sha256 in _ASSET_PINS.items()},
    PLAN: '0594e9baab44c381f2907643d7b4f65d28ac79268719f8342ad35dd6113dc120',
    ACK: '80ed0c1db758ddf5db1a6dbef7a10f8fd609e5d6dae6b01277455a3e9846d4b0',
    INVENTORY: '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558',
})
DERIVED_SHA = 'd88498700eccfd4e3bd1b3bf5bd99203e1b7122b11fb3dc847e2cb6af477de38'


class EvidenceFailure(Exception):
    """A fixed rejection code without raw evidence or environment details."""


def require(condition, code):
    if not condition:
        raise EvidenceFailure(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def _digest(value):
    return sha(_canonical(value).encode('utf8'))


def _encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf8')


def _same(value, expected, code):
    require(_canonical(value) == _canonical(expected), code)


def _fields(value, expected, code):
    _same({key: value[key] for key in expected}, expected, code)


def _flags(*keys):
    return dict.fromkeys(keys, True)


def _object_hash(value):
    return type(value) is str and re.fullmatch('[a-f0-9]{64}', value) is not None


def document(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_FILE, 'CSP_JSON_SIZE')

    def unique_pairs(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), 'CSP_DUPLICATE_JSON')
        return result

    def reject_constant(_):
        raise EvidenceFailure('CSP_NONFINITE_JSON')

    def check_types(value, depth=0):
        require(depth <= 48, 'CSP_JSON_DEPTH')
        if type(value) is dict:
            children = value.values()
        elif type(value) is list:
            children = value
        else:
            require(value is None or type(value) in (str, bool)
                    or type(value) is int and -(2**63) <= value < 2**63
                    or type(value) is float and math.isfinite(value), 'CSP_JSON_TYPE')
            return
        for child in children:
            check_types(child, depth + 1)

    try:
        value = json.loads(raw.decode('utf8'), object_pairs_hook=unique_pairs, parse_constant=reject_constant)
        check_types(value)
        return value
    except EvidenceFailure:
        raise
    except (ValueError, RecursionError):
        raise EvidenceFailure('CSP_MALFORMED_JSON') from None


def _root(path):
    path = Path(path).absolute()
    require(path.resolve(strict=True) == path and path.is_dir(), 'CSP_ROOT_PATH')
    return path


def _read(root, relative, wanted):
    path = root / relative

    def metadata():
        require(path.resolve(strict=True) == path and path.is_relative_to(root), 'CSP_INPUT_PATH')
        value = path.lstat()
        require(stat.S_ISREG(value.st_mode) and value.st_nlink == 1 and 0 < value.st_size <= MAX_FILE,
                'CSP_REGULAR_SINGLE_LINK_SIZE')
        return value

    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink, value.st_size,
                value.st_mtime_ns, value.st_ctime_ns)

    def once(prior=None):
        before = metadata()
        current = identity(before)
        require(prior is None or current == prior, 'CSP_INPUT_CHANGED')
        def nofollow(name, flags):
            return os.open(name, flags | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
        with open(path, 'rb', opener=nofollow) as handle:
            opened = os.fstat(handle.fileno())
            # ctime is compared within each API, since Windows may report it differently.
            require(identity(opened)[:-1] == current[:-1], 'CSP_INPUT_OPEN_CHANGED')
            raw = handle.read(MAX_FILE + 1)
            require(identity(os.fstat(handle.fileno())) == identity(opened), 'CSP_INPUT_HANDLE_CHANGED')
        require(identity(metadata()) == current and len(raw) == before.st_size, 'CSP_INPUT_PATH_CHANGED')
        require(sha(raw) == wanted, 'CSP_INPUT_SHA256')
        return raw, current

    try:
        first, first_identity = once()
        fresh, _ = once(first_identity)
        require(fresh == first, 'CSP_INPUT_BYTES_CHANGED')
        return fresh
    except OSError:
        raise EvidenceFailure('CSP_INPUT_UNAVAILABLE') from None


def _capture(root, include_derived=False):
    pins = {**RAW_PINS, **({DERIVED: DERIVED_SHA} if include_derived else {})}
    blobs = {path: _read(root, path, wanted) for path, wanted in pins.items()}
    require(sum(map(len, blobs.values())) <= MAX_BUNDLE, 'CSP_INPUT_BUNDLE_SIZE')
    return blobs


def _identity():
    return {'run_id': RUN, 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET}


def _claim():
    return {
        'case_id': CASE, 'assertion_id': ASSERTION, 'status': 'PASS',
        'expected_assertion_sha256': EXPECTED, 'qualification_limit': LIMIT,
        'controls': list(CONTROLS),
    }


def _eligibility(blobs):
    plan, ack, inventory = (document(blobs[path]) for path in (PLAN, ACK, INVENTORY))
    _fields(plan, {'Posture': 'D'}, 'CSP_FROZEN_PLAN_POSTURE')
    _fields(plan['scope'], {'case_id': CASE, 'assertion_id': ASSERTION,
                           'expected_assertion_sha256': EXPECTED, 'maximum_assertion_rows': 1}, 'CSP_FROZEN_CEILING')
    require(sha(plan['scope']['expected_assertion'].encode('utf8')) == EXPECTED, 'CSP_FROZEN_ASSERTION')
    _fields(ack, {'Posture': 'D', 'plan_sha256': RAW_PINS[PLAN], 'assertion_promotions': 0,
                  'decision': 'SOURCE_EXPECTATION_PLAN_APPROVED_NO_EVIDENCE_LINK_OR_RUNTIME_APPROVAL'}, 'CSP_ROOT_PLAN_ACK')
    _fields(ack['maximum'], {'case_id': CASE, 'assertion_id': ASSERTION, 'expected_assertion_sha256': EXPECTED,
                            'rows': 1, 'conditional_ceiling': 'PASS_ONLY_ON_INDEPENDENTLY_AUDITED_COMPLETE_ACTUAL_PROOF'},
            'CSP_ACK_CEILING')
    require(len(inventory['cases']) == 94 and inventory['summary']['mandatory_assertions'] == 1034,
            'CSP_FROZEN_INVENTORY_SIZE')
    require(inventory['source_provenance']['files_sha256'][APPLICATION] == APP_SHA, 'CSP_INVENTORY_SOURCE_SQL')
    [target] = [row for case in inventory['cases'] if case['id'] == CASE
                for row in case['assertions'] if row['id'] == ASSERTION]
    _fields(target, {'mandatory_for_case': True, 'availability': 'CANDIDATE_LOCAL_SQL_PATH',
                     'expected_assertion': plan['scope']['expected_assertion']}, 'CSP_INVENTORY_ASSERTION')


def _source(get, parent, audit):
    plan = get('operation-plan.json')
    plan_sha = _ASSET_PINS['operation-plan.json']
    review_sha = _ASSET_PINS['independent-review.json']
    review = get('independent-review.json')
    reviewer = '/root/cloud_review_prep'
    _fields(plan, {**_identity(), 'fixture_run_id': FIXTURE, 'Posture': 'D', 'runtime': 'NOT_RUN',
                   'review_status': 'PENDING_INDEPENDENT_OPERATIONAL_REVIEW',
                   'schema': 'workinants.cloud-customer-stale-predecessor-owned-plan.v2',
                   'migration_tool_archive_sha256': TOOL_ARCHIVE,
                   'platform_gate': 'CLOUD_TMPFS_V2_CAPABILITY_BOUND_FRESH_OPERATIONAL_REVIEW_REQUIRED'}, 'CSP_EXECUTED_PLAN')
    source = plan['packet_files_sha256']
    source_encoded = (json.dumps(source, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)
                      + '\n').encode('utf8')
    require(len(source) == 392 and all(map(_object_hash, source.values()))
            and sha(source_encoded) == PACKET and source[APPLICATION] == APP_SHA
            and source[INVENTORY] == RAW_PINS[INVENTORY], 'CSP_EXECUTED_SOURCE_PACKET')
    _same(parent['source_verification'], {'commit': COMMIT, 'tree': TREE, 'packet_sha256': PACKET,
                                          'files_sha256': source}, 'CSP_RUNTIME_SOURCE_VERIFICATION')
    _fields(audit, {'verified_committed_packet_files': 392, 'verified_generated_assets': 21}, 'CSP_AUDITED_SOURCE_FILES')
    _same(review, {'schema': 'workinants.cloud-customer-stale-predecessor-owned-review.v2',
                   'decision': 'APPROVED_EXACT_CLOUD_CSP_PACKET', 'findings': [], 'run_id': RUN, 'source_commit': COMMIT,
                   'packet_sha256': PACKET, 'plan_sha256': plan_sha, 'reviewer': reviewer,
                   'scopes': dict.fromkeys(('source', 'owned_resource', 'safety_sql', 'binary_transport',
                                            'operational_literals'), 'APPROVED')}, 'CSP_EXACT_OPERATIONAL_REVIEW')
    _same(get('attempt.json'), {'plan_sha256': plan_sha, 'review_sha256': review_sha, 'reviewer': reviewer,
                                'run_id': RUN, 'state_at_creation': 'BEFORE_ANY_RESOURCE_CREATION'}, 'CSP_EXACT_ATTEMPT')
    _same(get('operation-exit.json'), {'schema': 'workinants.cloud-csp-operation-exit-observation.v1', 'observer': '/root',
                                     'method': 'ACTUAL_OPERATING_PROCESS_EXIT', 'run_id': RUN, 'source_commit': COMMIT,
                                     'plan_sha256': plan_sha, 'outer_evidence_sha256': _ASSET_PINS[PARENT], 'exit_code': 0,
                                     'stdout_status': RAW_PASS, 'evidence_complete': True}, 'CSP_OBSERVED_PROCESS_EXIT')
    _fields(parent, {'approved_commit': COMMIT, 'approved_tree': TREE, 'approved_packet_sha256': PACKET,
                     'approved_operation_plan_sha256': plan_sha, 'review': 'INDEPENDENT_RECEIPT_VERIFIED', 'review_sha256': review_sha},
            'CSP_RUNTIME_REVIEW_BINDING')
    run_plan = get('evidence/customer-stale-run-plan.json')
    native = get('evidence/customer-stale-native-attestation.json')
    child_identity = {**_identity(), 'fixture_run_id': FIXTURE, 'container_id': CONTAINER_ID,
                      'native_sha256': NATIVE, 'actual_native_checks': 29089, 'oracle_expressions': 416,
                      'ledger_checks': 22, 'original_grantor_finalized': True, 'all_other_clients_absent': True,
                      'whole_case_promoted': False}
    _same(native, {'schema': 'workinants.customer-stale-owned-native-attestation.v1', **child_identity},
          'CSP_CHILD_NATIVE_IDENTITY')
    _fields(run_plan, {'schema': 'workinants.customer-stale-owned-run-plan.v1', **child_identity,
                       'cases': list(CONTROLS)}, 'CSP_EXACT_CHILD_SOURCE_BINDING')
    child_source = run_plan['child_source_files_sha256']
    generated = plan['generated_files_sha256']
    require(len(child_source) == 23 and all(source.get(name) == pin for name, pin in child_source.items())
            and len(generated) == 21 and all(map(_object_hash, generated.values())), 'CSP_CHILD_SOURCE_PACKET')
    _same(run_plan['child_artifacts_sha256'], {path.removeprefix('child/'): pin for path, pin in generated.items()
                                             if path.startswith('child/')}, 'CSP_CHILD_SQL_AND_FIXTURES')
    require(run_plan['fixture_sha256'] == generated['child/fixtures.json'], 'CSP_CHILD_FIXTURE_BINDING')
    return plan


def _parent(parent, plan, audit):
    _fields(parent, {'schema': 'workinants.cloud-customer-stale-predecessor-owned-result.v2', 'run_id': RUN,
                     'status': RAW_PASS, 'stage': 'CONTROLLED_CLEANUP', 'unexpected': [],
                     'persistence_failure': False, 'output_complete': True, 'evidence_complete': True,
                     'transport_closure': {'transport_closure_unconfirmed': False, 'first_unconfirmed_closure': None},
                     'limits': {'posture': 'D', 'hosted_changes': False, 'migration_adoption': False,
                                'whole_case_promoted': False, 'independent_evidence_admission': 'PENDING'},
                     **_flags('bootstrap_removed_in_container', 'cleanup_actions_confirmed', 'packet_unchanged_after_run',
                              'tool_source_data_unchanged_after_run', 'external_sources_unchanged_after_run',
                              'external_inputs_unchanged_after_run')}, 'CSP_CLOSED_PASS_PARENT')
    _same(parent['steps'], {'CATALOG-SETUP': 'PASS', 'CATALOG-AUTH': 'PASS', 'CATALOG-TOOLS': 'PASS',
                            'CATALOG-INSTALL': 'PASS', 'CATALOG-ACL-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
                            'CATALOG-TEXT-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
                            'CATALOG-NATIVE': 'PASS_OBSERVED_NOT_QUALIFIED',
                            'CATALOG-ORACLE': 'PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE',
                            'CATALOG-LEDGER': 'PASS_SOURCE_BOUND_NATIVE_SUBSET',
                            'CATALOG-COMPARE': 'PASS_SOURCE_BOUND_NATIVE_CATALOG_ONLY', 'CATALOG-SANITIZED_EXPORT': 'NOT_RUN',
                            'CATALOG-CLEANUP': 'PASS', 'CSP1-REVIEW': 'PASS_REVIEWED_CLOUD_SOURCE_ONLY',
                            'CSP1-COMPONENT': 'PASS_THREE_ROLLBACK_CONTROLS_ONLY'}, 'CSP_COMPLETED_REVIEWED_SEQUENCE')
    _same(parent['sanitization'], {'files_scanned': 30, 'actual_password_values_found': False,
                                  'unrestricted_subprocess_output_persisted': False, 'raw_context_handles_persisted': False,
                                  'coordinator_evidence_uses_reviewed_allowlist': True}, 'CSP_SANITIZED_REPORT')
    target = plan['target']
    _fields(target, {'container_name': TARGET, 'volume_name': VOLUME, 'network': 'none', 'database': DATABASE},
            'CSP_TARGET_PRIVATE_IDENTITY')
    _same(audit['target'], target, 'CSP_AUDITED_TARGET')
    _same(parent['daemon'], plan['daemon'], 'CSP_ACTUAL_DAEMON')
    _same(audit['daemon'], parent['daemon'], 'CSP_AUDITED_DAEMON')
    _fields(parent['image'], {'reference': target['image'], 'removed': False, 'os': 'linux', 'architecture': 'amd64',
                              'pg_version': '17.11-1.pgdg13+2',
                              **_flags('manifest_content_hash_verified', 'pinned_repo_digest_verified')}, 'CSP_PINNED_IMAGE')
    _same(audit['image'], parent['image'], 'CSP_AUDITED_IMAGE')
    _fields(parent['created_volume'], {'name': VOLUME, 'labels': target['labels']}, 'CSP_OWNED_VOLUME')
    _same(audit['created_volume'], parent['created_volume'], 'CSP_AUDITED_VOLUME')
    require(set(parent['targets']) == {TARGET}, 'CSP_SINGLE_EXECUTED_TARGET')
    executed = parent['targets'][TARGET]
    _fields(executed, {'container_id': CONTAINER_ID, 'volume': VOLUME,
                       'volume_created_at': parent['created_volume']['created_at'], 'labels': target['labels'],
                       'network_mode': 'none', 'published_ports': False, 'bootstrap': 'PASS', 'finalization': 'PASS',
                       'application': 'NOT_RUN', 'connections_before_finalization': {'migrator': 0, 'other_client_backends': 0},
                       'finalization_observation': audit['reviewed_runner_prefix']['original_grantor_finalization'],
                       'finalization_observation_status': 'OBSERVED_NOT_QUALIFIED'}, 'CSP_EXECUTED_PRIVATE_TARGET')
    _same(parent['cleanup'], {TARGET: {'removed': True, 'verified_id': CONTAINER_ID, 'name_and_both_labels_verified': True},
                              VOLUME: {'removed': True, 'name_labels_creation_identity_verified': True}}, 'CSP_EXACT_CLEANUP')
    _same(parent['cloud_cleanup'], {**_flags('container_id_absent', 'container_name_absent', 'volume_absent'),
                                    'host_secret_files_created': False}, 'CSP_CLOUD_CLEANUP')
    _same(audit['cleanup_verified'], _flags('approved_image_retained', 'container_id_absent', 'container_name_absent',
                                           'private_host_paths_absent', 'same_daemon', 'volume_name_absent'),
          'CSP_INDEPENDENT_CLEANUP')
    _fields(parent['copied_runtime_preflight'], {'checked': 7, 'node_verified': True, 'immutable_container_id': CONTAINER_ID,
                                               'metadata': 'PASS_EXACT_ROOT_OWNED_TREE', 'command_exit': 0,
                                               'command_stderr_present': False}, 'CSP_INSTALLED_TOOL_CHECKS')
    _same(audit['reviewed_runner_prefix']['tool_compatibility'], {'engine_commit': ENGINE, 'node': 'v24.22.1',
                                                                'preexec_hashes_verified': True}, 'CSP_AUDITED_TOOL_CHECKS')
    _same(parent['migration_operations'], [{'target': TARGET, 'stage': 'CATALOG_GENUINE_INITIAL_DEPLOY',
                                           'status': 'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS',
                                           'exit_code': 0, 'attestation_sha256': INSTALLER,
                                           'inner_terminal_receipt': True}], 'CSP_ONE_INITIAL_DEPLOY')
    require(parent['migration_attempted'] is True, 'CSP_INITIAL_DEPLOY_ATTEMPTED')


def _authentication(parent, audit):
    _same(parent['authentication'], [{'role': role, 'transport': 'TCP_127.0.0.1_5432', 'correct_password': 'PASS_SCRAM',
                                     'wrong_password': 'PASS_REJECTED', 'wrong_password_exit_code': 2}
                                    for role in ROLES * 2], 'CSP_TWELVE_SCRAM_PAIRS')
    _same(parent['effective_hba_selections'], [{'role': role, 'address': address, 'rule_number': number, 'method': 'scram-sha-256'}
                                               for address, number in (('127.0.0.1', 2), ('::1', 3)) for role in ROLES],
          'CSP_EFFECTIVE_SCRAM_HBA')
    phases = ('AUTH_HBA', 'AUTH_HBA') + ('AUTH_CORRECT_PASSWORD', 'AUTH_WRONG_PASSWORD') * 6
    _same(parent['authentication_process_receipts'], [
        {'phase': phase, **_flags('call_attempted', 'completion_returned', 'normal_byte_api_returned',
                                  'closure_receipt_received', 'process_exited', 'pipes_closed', 'threads_closed',
                                  'client_closure_confirmed', 'remote_exec_attempted'), 'remote_exec_exit_unconfirmed': False}
        for phase in phases * 2], 'CSP_AUTH_PROCESSES_CLOSED')
    closures = parent['backend_closures']
    require(len(closures) == 20 and all(type(row['stage']) is str for row in closures), 'CSP_BACKEND_CLOSURES')
    for row in closures:
        _same(row, {'stage': row['stage'], 'scope': 'ALL_DATABASES_ALL_ROLES_ALL_TAGS',
                    **_flags('observation_completed', 'counts_valid', 'migrator_zero', 'other_clients_zero',
                             'all_other_client_backends_absent')}, 'CSP_GLOBAL_BACKEND_CLOSURE')
    finalized = parent['customer_stale']['pre_child_finalization_preflight']
    _fields(finalized, {'selector': 'FINALIZATION_RESULT', 'selector_field_count': 5,
                        **_flags('response_observed', 'current_source_bytes_rechecked'),
                        'comparisons': _flags('original_postgres_grantor', 'scram_postgres_identity',
                                              'zero_temporary_memberships', 'false_leaf_CREATE', 'zero_install_clients')},
            'CSP_RESTORED_ORIGINAL_GRANTOR')
    _fields(finalized['permanent_edge_fresh_native_proof'], {'native_sha256': NATIVE, 'source_commit': COMMIT,
                                                            'source_tree': TREE, 'packet_sha256': PACKET, 'edge_matches': True,
                                                            'proof_phase': 'FRESH_NATIVE_QUALIFICATION_BEFORE_REPEATED_AUTH'},
            'CSP_FINALIZATION_BEFORE_REPEATED_AUTH')
    _same(audit['reviewed_runner_prefix']['original_grantor_finalization'], {
        'active_install_connections': 0, 'auth': 'scram-sha-256:postgres', 'grantor': 'postgres',
        'leaf_create': dict.fromkeys(('wa_customer_verifier', 'wa_private_helper_owner', 'wa_track_verifier'), False),
        'remaining_memberships': 0,
    }, 'CSP_AUDITED_ORIGINAL_GRANTOR')


def _child(value):
    def operation(stage, **fields):
        return {'stage': stage, **fields}

    def response(stage, rows):
        return operation(stage, **_flags('response_received', 'shape_valid', 'acknowledged', 'stderr_empty'), rows=rows)

    def retain(count):
        return operation('ALL_ISSUER_GRANTS_IMMUTABLE_AND_CURRENT', count=count, exact=True)

    closed = operation('OWNED_OPERATION_CLOSE', **_flags('attempted', 'backend_tuple_present', 'closed'))
    global_closed = operation('ALL_CLIENT_CLOSURE', scope='ALL_DATABASES_ROLES_TAGS',
                              **_flags('attempted', 'shape_valid', 'zero', 'confirmed'))
    triggers = operation('ALL100_TRIGGER_RESTORATION', exact_typed_comparison=True)
    native = operation('NATIVE_SNAPSHOT_PRESERVATION', same=True)
    full_state = operation('FULL42_STATE', shape_valid=True, table_count=42)
    grant = [response('ISSUER_INSERT_AND_COMMIT', 1), closed,
             operation('SEPARATE_ISSUER_COMMIT', **_flags('acknowledged', 'created_at_verified', 'closed')),
             operation('SAME_ACTUAL_APP_TUPLE_AFTER_ISSUER_COMMIT', same=True), response('BIND_CURRENT_CONTEXT', 0)]
    operations = [global_closed, triggers, native, response('TRUSTED_IDENTITY_SETUP', 0), closed,
                  global_closed, triggers, native, *grant, response('GENUINE_APP_SH004_CREATE', 1), closed, global_closed,
                  triggers, native, retain(1), operation('COMPLETE_ONE_HISTORY_BASELINE', exact_typed_comparison=True), full_state]
    results = []
    for count, (case, sqlstate) in enumerate(zip(CONTROLS, (None, 'P0001', '42501'), strict=True), start=2):
        diagnostic = None if sqlstate is None else {
            'sqlstate': sqlstate, **_flags('matched', 'exact_primary', 'source_function', 'source_body', 'raise_line', 'bounded_shape'),
        }
        receipt = {'diagnostic': diagnostic, **_flags('response_received', 'shape_valid', 'acknowledged',
                                                     'exact_output', 'rollback_acknowledged')}
        results.append({'name': case, 'status': 'PASS_ROLLBACK_CONTROL_ONLY', 'receipt': receipt})
        operations.extend([*grant, response('INITIAL_RESTRICTED_VISIBILITY', 1), operation('VISIBLE_REVISION0_AND_OWNER', exact=True)])
        if case == 'same-grant-second-source-update':
            operations.extend([response('FIRST_UNCOMMITTED_PLUS_ONE', 1),
                               operation('FIRST_UNCOMMITTED_PLUS_ONE', exact=True, committed=False)])
        operations.extend([response('INTENDED_NEGATIVE_AND_EXPLICIT_ROLLBACK', 4), closed,
                           operation('EXPECTED_RESPONSE_AFTER_OWNED_EXIT', **_flags('reader_complete', 'stderr_observed_after_exit', 'closed')),
                           operation('PRE_VERDICT_ALLOWLISTED_COMPARISONS', case=case, **receipt), global_closed, global_closed,
                           triggers, native, retain(count), operation('ORIGINAL_ONE_HISTORY_CREATE_GROUP', exact_typed_comparison=True),
                           full_state, operation('FULL42_ROLLBACK_PARITY', exact=True)])
    operations.extend([global_closed, global_closed])
    _same(value, {'schema': 'workinants.customer-stale-predecessor-results.v1',
                  'status': 'PASS_THREE_STALE_PREDECESSOR_ROLLBACK_CONTROLS_ONLY', 'stage': 'ORIGINAL_ONE_HISTORY_CREATE_GROUP',
                  'first_failure': None, 'current_case': None, 'evidence_complete': True, 'operations': operations,
                  'results': results}, 'CSP_EXACT_CHILD_ROLLBACK_TRANSCRIPT')
    return results


def _component(get, blobs, parent, audit):
    selected = parent['customer_stale']
    _fields(selected, {'prepared_protocols': 3, 'completed_controls': 3, 'fixture_run_id': FIXTURE,
                       'selected_assertions': 'NOT_PROMOTED_PENDING_EVIDENCE_REVIEW', 'owner_api_policy_qualified': False,
                       **_flags('constructor_attempted', 'run_attempted', 'component_closure_confirmed',
                                'component_owned_clients_closed', 'component_global_backends_absent', 'component_closure_attempted')},
            'CSP_COMPLETE_NOT_YET_ADMITTED')
    child_sha = _ASSET_PINS[CHILD]
    _same(selected['component_report_reference'], {'artifact': CHILD.removeprefix('evidence/'), 'present': True,
                                                  'read_status': 'CLOSED_BOUNDED_BYTES', 'closed_recheck_match': True,
                                                  'integrity_recheck_match': True, 'bytes': len(blobs[f'{ASSET}/{CHILD}']),
                                                  'sha256': child_sha}, 'CSP_EXACT_RETAINED_CHILD')
    _same(get('evidence/customer-stale-component-summary.json'), {
        'schema': 'workinants.customer-stale-owned-summary.v1', 'run_id': RUN, 'fixture_run_id': FIXTURE,
        'raw_child_sha256': child_sha, 'completed_rollback_controls': 3, 'prospective_assertion': f'{CASE}/{ASSERTION}',
        'assertion_promoted': False,
    }, 'CSP_RAW_COMPONENT_SUMMARY')
    results = _child(get(CHILD))
    _same(audit['child_observations'], {
        **_flags('all100_trigger_and_native_parity', 'constructor_and_run_attempted',
                 'one_restricted_sh004_create_and_history_confirmed', 'owned_and_global_closure', 'trusted_identity_setup_acknowledged'),
        'cases': results, 'issuer_commits_with_created_at_and_exact_closed_clients': 4, 'post_proof': selected['post_proof'],
        'retained_case_result_count': 3, 'retained_sha256': child_sha,
    }, 'CSP_AUDITED_EXACT_CHILD')
    return results


def _native_and_ledger(get, blobs, parent, plan, audit):
    native = get('evidence/native-before.json')
    _fields(native, {'format': 'workinants.native-catalog.v1', 'server_version_num': 170011,
                     'collected_as': 'postgres', 'read_only': True, 'collector_is_superuser': True}, 'CSP_NATIVE_COLLECTOR')
    require(_digest(native) == NATIVE, 'CSP_NATIVE_CANONICAL_SHA256')
    prefix_snapshots = (('NATIVE_BEFORE_ORACLE', 'native-before.json'), ('NATIVE_AFTER_ORACLE', 'native-after-oracle.json'),
                        ('NATIVE_AFTER_LEDGER', 'native-after-ledger.json'))
    snapshots = (*prefix_snapshots, *((f'SCOPED_POST_{stage}', f'post-{name}') for stage, name in prefix_snapshots))
    _same(parent['native_snapshots'], [{'stage': stage, 'artifact': name, 'native_sha256': NATIVE,
                                        'artifact_sha256': _ASSET_PINS[f'evidence/{name}'], 'status': 'OBSERVED_NOT_QUALIFIED'}
                                       for stage, name in snapshots], 'CSP_SIX_SAME_TARGET_NATIVE_SNAPSHOTS')
    require(all(blobs[f'{ASSET}/evidence/{name}'] == blobs[f'{ASSET}/evidence/native-before.json'] for _, name in snapshots),
            'CSP_SIX_NATIVE_BYTE_PARITY')
    for name, key in (('acl-preflight', 'acl_compatibility_preflight'), ('text-preflight', 'text_compatibility_preflight')):
        _same(parent[key], get(f'evidence/{name}.json'), 'CSP_SOURCE_COMPATIBILITY_PREFLIGHT')
    _fields(plan['catalog'], {'source_expected_sha256': SOURCE_EXPECTED, 'bootstrap_grantor': 'postgres'}, 'CSP_CATALOG_SOURCE')
    comparison = get('evidence/catalog-comparison.json')
    _same(parent['catalog_comparison'], comparison, 'CSP_PREFIX_NATIVE_COMPARISON')
    _fields(comparison, {'status': 'PASS', 'source_expected_sha256': SOURCE_EXPECTED, 'native_snapshot_sha256': NATIVE,
                         'check_counts': {'PASS': 29089}, 'findings': [], 'database_contacted_by_comparator': False,
                         'database_posture': 'D'}, 'CSP_EXACT_NATIVE_29089')
    oracle = get('evidence/oracle-evidence.json')
    _fields(oracle, {'database': DATABASE, 'connection_closed_before_observation': True, 'pre_oracle_catalog_sha256': NATIVE,
                     'post_rollback_catalog_sha256': NATIVE}, 'CSP_ORACLE_TRANSACTION_CLOSURE')
    for name in ('preflight', 'results', 'closure'):
        _same(oracle[name], get(f'evidence/oracle-{name}.json'), 'CSP_ORACLE_ARTIFACT_IDENTITY')
    results = oracle['results']
    plan_sha = results['plan_sha256']
    _fields(results, {'source_expected_sha256': SOURCE_EXPECTED, 'server_version_num': 170011, 'expression_count': 416},
            'CSP_EXACT_ORACLE_416')
    require(type(results['expressions']) is list and len(results['expressions']) == 416, 'CSP_EXACT_ORACLE_EXPRESSION_COUNT')
    _fields(oracle['preflight'], {'plan_sha256': plan_sha, 'outcomes': _flags(
        'read_committed', 'target_identity', 'no_event_triggers', 'table_set_and_owners', 'no_restricted_clients',
        'columns_and_native_types', 'enum_set_owners_and_labels', 'no_preexisting_temp_objects',
        'original_grantor_finalization', 'function_set_headers_and_bodies',
    )}, 'CSP_ORACLE_PREFLIGHT')
    _fields(oracle['closure'], {'plan_sha256': plan_sha, 'all_oracle_tables_absent': True, 'all_oracle_functions_absent': True},
            'CSP_ORACLE_ROLLBACK_CLOSURE')
    registration = get('evidence/ledger-registration.json')
    migration = '20261117000100_f0_local_initial'
    _fields(registration, {'run_id': RUN, 'database': DATABASE, 'target_attestation_sha256': INSTALLER,
                           'source_expected_sha256': SOURCE_EXPECTED, 'engine_commit': ENGINE, 'prisma_version': '7.10.1',
                           'migrations': [{'path': f'prisma/foundation/migrations/{migration}/migration.sql',
                                           'migration_name': migration, 'state': 'applied', 'count': 1, 'sha256': APP_SHA}]},
            'CSP_ONE_SOURCE_CHECKSUM_INSTALLATION')
    require(_digest(registration) == REGISTRATION == parent['ledger_registration_sha256'], 'CSP_SAME_FIRST_LEDGER_REGISTRATION')
    marker = get('evidence/ledger-evidence.json')
    observation = get('evidence/ledger-observation.json')
    _fields(marker, {'registration_sha256': REGISTRATION, 'target_attestation_sha256': INSTALLER, 'run_id': RUN,
                     'native_catalog_before_sha256': NATIVE, 'native_catalog_after_sha256': NATIVE, 'observation': observation},
            'CSP_SAME_TARGET_LEDGER_RECEIPT')
    _fields(observation, {'database': DATABASE, 'server_version_num': 170011, 'read_only': True, 'collected_as': 'postgres',
                          'isolation': 'repeatable read', 'history_ids_unique': True, 'history': registration['history_expected']},
            'CSP_READ_ONLY_SINGLE_HISTORY_OBSERVATION')
    [history] = observation['history']
    _same(history, {'name_sha256': sha(migration.encode('ascii')), 'checksum_sha256': sha(APP_SHA.encode('ascii')),
                    'checksum_format_valid': True, 'id_is_uuid_v4': True, 'started': True, 'finished': True,
                    'rolled_back': False, 'time_order_valid': True, 'steps': 1, 'logs_state': 'NULL'}, 'CSP_ONE_COMPLETE_HISTORY_ROW')
    require(_digest(observation) == parent['ledger_observation_sha256'], 'CSP_PREFIX_LEDGER_OBSERVATION')
    checks = parent['ledger_comparison']['checks']
    require(parent['ledger_comparison']['status'] == 'PASS' and len(checks) == 22
            and len({check['field'] for check in checks}) == 22
            and all(check['status'] == 'PASS' and _object_hash(check['expected_sha256'])
                    and check['expected_sha256'] == check['actual_sha256'] for check in checks), 'CSP_EXACT_LEDGER_PASS22')
    for name in ('catalog-comparison', 'ledger-evidence', 'ledger-observation', 'oracle-closure', 'oracle-evidence',
                 'oracle-preflight', 'oracle-results'):
        require(blobs[f'{ASSET}/evidence/{name}.json'] == blobs[f'{ASSET}/evidence/post-{name}.json'], 'CSP_POST_OBSERVATION_BYTE_PARITY')
    _same(audit['recomputed_native_prefix'], {
        'native_canonical_sha256': NATIVE, 'native_comparator_exact_pass': 29089, 'oracle_exact_replay': 416,
        'ledger_exact_pass': 22, 'migration_ledger_rows': 1, 'source_expected_sha256': SOURCE_EXPECTED,
        'target_attestation_sha256': INSTALLER, 'three_catalog_snapshots_byte_equal': True,
        'comparison_contacted_database': False,
    }, 'CSP_INDEPENDENT_NATIVE_ORACLE_LEDGER_AUDIT')


def _post_proof(get, parent):
    state = get('evidence/post-state-before.json')
    _same(get('evidence/post-state-after.json'), state, 'CSP_READ_ONLY_POST_FULL_STATE_PARITY')
    require(type(state) is list and len(state) == 42 and _digest(state) == STATE
            and len({row['table'] for row in state}) == 42,
            'CSP_POST_STATE_42_SOURCE_DEFINED_TABLES')
    for row in state:
        require(set(row) == {'table', 'count', 'sha256'} and type(row['table']) is str
                and type(row['count']) is int and row['count'] >= 0 and _object_hash(row['sha256']), 'CSP_POST_STATE_TYPED_ROW')
    # The source-defined business-row projection omits the four separately audited issuer grants.
    _same({row['table']: row['count'] for row in state if row['count']}, {
        'app.customer_profile_lifecycle_event': 1, 'app.customer_profiles': 1, 'app.user_security_profiles': 1,
        'app.users': 1, 'platform.owner_mutation_evidence': 1, 'platform.runtime_command_receipt': 1,
        'platform.runtime_outbox_message': 2,
    }, 'CSP_POST_PRESERVED_ONE_HISTORY_GROUP')
    proof = parent['customer_stale']['post_proof']
    _same(proof, {'status': 'PASS_READ_ONLY_SOURCE_BOUND_SUBSET', 'same_first_install_registration_sha256': REGISTRATION,
                  'same_installer_attestation_sha256': INSTALLER, 'native_sha256': NATIVE, 'native_checks': 29089,
                  'oracle_expressions': 416, 'ledger_checks': 22, 'independent_tables': 42, 'before_state_sha256': STATE,
                  'after_state_sha256': STATE, 'child_final_state_sha256': STATE, 'second_deploy': False},
          'CSP_ONE_READ_ONLY_POST_PROOF_NO_SECOND_INSTALL')
    return proof


def _audit(audit, blobs):
    _fields(audit, {**_identity(), 'schema': 'workinants.cloud-csp-independent-closure-audit.v2', 'fixture_run_id': FIXTURE,
                    'decision': 'EXACT_CLEANUP_AND_SINGLE_STALE_PREDECESSOR_ASSERTION_SUPPORTED', 'status': RAW_PASS,
                    'reviewer': '/root/cloud_review_prep', 'created_container_id': CONTAINER_ID,
                    'admitted_assertion_changes': 0, 'outer_exit_code_supported_by_exact_pass_return_path': 0,
                    'qualified_assertion': {'case_id': CASE, 'assertion_id': ASSERTION, 'status': 'PASS', 'maximum_scope': LIMIT}},
            'CSP_INDEPENDENT_EXACT_CEILING_AND_IDENTITY')
    primary = ('operation-plan.json', 'independent-review.json', 'attempt.json', PARENT, CHILD)
    _same(audit['file_sha256'], {path: _ASSET_PINS[path] for path in primary}, 'CSP_AUDITED_PRIMARY_BYTES')
    prefix, post = {}, {}
    for path in _ASSET_PINS:
        if not path.startswith('evidence/') or path in (PARENT, CHILD):
            continue
        name = path.removeprefix('evidence/')
        group = post if name.startswith('post-') or name == 'customer-stale-component-summary.json' else prefix
        group[name] = {'sha256': _ASSET_PINS[path], 'bytes': len(blobs[f'{ASSET}/{path}'])}
    _same(audit['prefix_file_sha256'], prefix, 'CSP_AUDITED_FIFTEEN_PREFIX_INPUTS')
    _same(audit['post_file_sha256'], post, 'CSP_AUDITED_THIRTEEN_POST_INPUTS')


def expected_record(blobs):
    """Validate the exact retained inputs and project the only supported assertion."""
    require(set(blobs) == set(RAW_PINS), 'CSP_CLOSED_RAW_INPUTS')
    require(all(type(raw) is bytes and len(raw) <= MAX_FILE and sha(raw) == RAW_PINS[path] for path, raw in blobs.items()),
            'CSP_RAW_INPUT_HASHES')

    def get(name):
        return document(blobs[f'{ASSET}/{name}'])

    try:
        _eligibility(blobs)
        parent = get(PARENT)
        audit = get('independent-closure.json')
        _audit(audit, blobs)
        plan = _source(get, parent, audit)
        _parent(parent, plan, audit)
        _authentication(parent, audit)
        results = _component(get, blobs, parent, audit)
        _native_and_ledger(get, blobs, parent, plan, audit)
        proof = _post_proof(get, parent)
    except (KeyError, TypeError, ValueError, IndexError):
        raise EvidenceFailure('CSP_SEMANTIC_SHAPE') from None
    return {
        'schema': 'workinants.cloud-csp9e633e3f-qualified-evidence.v1', **_identity(), 'fixture_run_id': FIXTURE,
        'application_sql_sha256': APP_SHA, 'database_posture': 'D', 'actual_result': KIND, 'raw_runtime_result': RAW_PASS,
        'derivation': 'ONE_ASSERTION_FROM_EXISTING_INDEPENDENTLY_AUDITED_CLOUD_REHEARSAL',
        'input_files_sha256': dict(RAW_PINS),
        'prior_accepted_board': {
            'source_commit': COMMIT, 'assertion_ledger_path': LEDGER, 'assertion_ledger_sha256': BASELINE_LEDGER,
            'status_path': BOARD, 'status_sha256': BASELINE_BOARD, 'builder_path': BUILDER, 'builder_sha256': BASELINE_BUILDER,
            'assertion_rows': 730, 'linked_executions': 15, 'mandatory_assertions': 1034,
        },
        'proof': {'restricted_sh004_create_prerequisite': True, 'separately_committed_current_issuer_grants': 4,
                  'completed_rollback_controls': results, 'actual_executor_exit_code': 0,
                  'independent_cleanup_verified': True, 'same_target_post_proof': proof},
        'claims': [_claim()],
        'limits': {
            'committed_customer_update': False, 'concurrent_winner_qualified': False, 'update_result_or_codec_qualified': False,
            'whole_case_qualified': False, 'owner_api_qualified': False, 'worker_or_track_qualified': False,
            'migration_adoption': False, 'hosted_or_production_qualified': False, 'deployment_or_release': False,
        },
    }


def derive_bytes(root):
    """Build the separate normalized record in memory. The caller owns any admission."""
    try:
        return _encoded(expected_record(_capture(_root(root))))
    except OSError:
        raise EvidenceFailure('CSP_INPUT_UNAVAILABLE') from None


def _expected_row():
    return {
        'case_id': CASE, 'assertion_id': ASSERTION, 'status': 'PASS', 'expected_assertion_sha256': EXPECTED, **_identity(),
        'application_sql_sha256': APP_SHA, 'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA, 'json_pointer': '/claims/0',
        'qualification_scope': SCOPE, 'qualification_limit': LIMIT,
    }


def _expected_execution():
    return {**_identity(), 'evidence_path': DERIVED, 'evidence_sha256': DERIVED_SHA,
            'actual_result': KIND, 'qualification_scope': SCOPE}


def is_reference(row):
    return (row.get('evidence_path') == DERIVED or row.get('run_id') == RUN
            or row.get('actual_result') == KIND or row.get('evidence_sha256') == DERIVED_SHA)


def propose_ledger_delta(current_raw, execution_raw):
    """Append exactly one row and its execution to the accepted baseline in memory."""
    require(type(current_raw) is bytes and sha(current_raw) == BASELINE_LEDGER, 'CSP_EXACT_PRIOR_730_LEDGER')
    require(type(execution_raw) is bytes and sha(execution_raw) == DERIVED_SHA, 'CSP_EXACT_NORMALIZED_RECORD')
    record = document(execution_raw)
    _same(record['claims'], [_claim()], 'CSP_ONLY_ONE_SUPPORTED_CLAIM')
    current = document(current_raw)
    rows, executions = current['assertions'], current['executions']
    identities = {(row['case_id'], row['assertion_id']) for row in rows}
    require(len(rows) == len(identities) == 730 and len(executions) == 15, 'CSP_EXACT_PRIOR_730_AND_15')
    require((CASE, ASSERTION) not in identities and not any(map(is_reference, [*rows, *executions])), 'CSP_NEW_ROW_ONLY')
    result = copy.deepcopy(current)
    result['assertions'].append(_expected_row())
    result['executions'].append(_expected_execution())
    return result


class QualificationBatch:
    """Bind one complete ledger row to the exact raw and normalized record bytes."""

    def __init__(self, root, ledger):
        self._root = _root(root)
        self._blobs = _capture(self._root, include_derived=True)
        record = expected_record({path: self._blobs[path] for path in RAW_PINS})
        require(self._blobs[DERIVED] == _encoded(record), 'CSP_EXACT_REDERIVED_RECORD')
        self._record = _canonical(record)
        _same([row for row in ledger['assertions'] if is_reference(row)], [_expected_row()], 'CSP_EXACT_ONE_LEDGER_ROW')
        _same([row for row in ledger['executions'] if is_reference(row)], [_expected_execution()], 'CSP_EXACT_ONE_EXECUTION_ENTRY')
        self._seen = False
        self._failure = None
        self._finalized = False

    def _reject(self, code):
        if self._failure is None:
            self._failure = code
        raise EvidenceFailure(self._failure) from None

    def validate_claim(self, case_id, assertion_id, status, execution, root, json_pointer=None, ledger_row=None):
        try:
            require(self._failure is None and not self._seen and not self._finalized, 'CSP_BATCH_ALREADY_USED')
            _same((case_id, assertion_id, status, json_pointer), (CASE, ASSERTION, 'PASS', '/claims/0'), 'CSP_EXACT_CLAIM_POINTER')
            require(_root(root) == self._root, 'CSP_WRONG_BATCH_ROOT')
            require(_canonical(execution) == self._record, 'CSP_EXACT_EXECUTION_DOCUMENT')
            _same(ledger_row, _expected_row(), 'CSP_EXACT_FULL_LEDGER_ROW')
            self._seen = True
            return True
        except EvidenceFailure as error:
            self._reject(str(error))
        except (TypeError, ValueError, OSError, RecursionError):
            self._reject('CSP_CLAIM_REJECTED')

    def verify_unchanged(self):
        try:
            require(self._failure is None and self._seen and not self._finalized, 'CSP_EXACT_UNSEEN_BATCH_REQUIRED')
            require(_capture(self._root, include_derived=True) == self._blobs, 'CSP_FRESH_ALL_INPUT_BYTES_CHANGED')
            self._blobs = None
            self._finalized = True
            return True
        except EvidenceFailure as error:
            self._reject(str(error))

    def require_finalized(self):
        require(self._failure is None, self._failure)
        if not self._finalized:
            self._reject('CSP_FINAL_FRESH_INPUT_BARRIER_REQUIRED')
        return True


def prepare_batch(root, ledger):
    try:
        return QualificationBatch(root, ledger)
    except (OSError, TypeError, ValueError, KeyError, AttributeError, RecursionError):
        raise EvidenceFailure('CSP_BATCH_REJECTED') from None
