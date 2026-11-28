"""Read the pinned, independently accepted physical Track machinery run."""

from pathlib import Path
import re
import uuid

import business_proof as proof


SCHEMA = 'workinants.cloud-f0-track-retained-base-machinery-acceptance.v1'
DECISION = 'ACCEPT_EXACT_TRACK_THREE_MIGRATION_MACHINERY'
CLOSURE_DECISION = 'EXACT_TRACK_THREE_MIGRATION_MACHINERY_AND_CLEANUP_VERIFIED'
PASS = 'PASS_TRACK_THREE_MIGRATION_MACHINERY_ONLY'
PLAN_SCHEMA = 'workinants.cloud-f0-track-retained-base-owned-operation.v1'
RESULT_SCHEMA = 'workinants.cloud-f0-track-retained-base-owned-result.v1'
RUN_SCHEMA = 'workinants.cloud-f0-track-retained-base-owned-run-evidence.v1'
SOURCE_BASE = 'scripts/sql-review/cloud-track-retained-base-v1'
CANDIDATE_COMMIT = 'd25792e0524a70af763c31cc0c64605d737cc915'
REQUIRED_FILES = ('operation.json', 'operation-exit.json', 'created-container.json', 'created-volume.json',
                  'evidence/run-evidence.json', 'evidence/noop-track-retained-base-results.json', 'independent-closure.json')
CLEANUP = {'approved_image_retained', 'container_full_id_absent', 'container_labels_absent', 'container_name_absent',
           'private_host_path_absent', 'same_daemon', 'volume_labels_absent', 'volume_name_absent'}
SHA40 = re.compile('[0-9a-f]{40}')
ACTOR = re.compile('[a-zA-Z0-9_/.-]{1,100}')
ARCHIVE_PATH = re.compile(r'context/reconciliation/cloud-phase0-evidence/\d{4}-\d{2}-\d{2}/track-[0-9a-f]{8}/acceptance\.json')
ACCEPTANCE_FIELDS = {'schema', 'decision', 'posture', 'assertion_promotions', 'business_cases', 'run_id', 'container_id',
                     'volume_created_at', 'source_commit', 'source_tree', 'candidate_commit', 'candidate_catalog_sha256',
                     'ordered_migration_sha256', 'operator_exit_code', 'reviewer', 'source_author', 'files_sha256'}


def pin(value, pattern=proof.HASH):
    return type(value) is str and pattern.fullmatch(value) is not None


def acceptance_shape(value):
    proof.need(type(value) is dict and set(value) == ACCEPTANCE_FIELDS and value['schema'] == SCHEMA
               and value['decision'] == DECISION and value['posture'] == 'D' and value['business_cases'] == 'NOT_RUN'
               and type(value['assertion_promotions']) is int and value['assertion_promotions'] == 0
               and type(value['operator_exit_code']) is int and value['operator_exit_code'] == 0
               and proof.canonical_uuid(value['run_id']) and uuid.UUID(value['run_id']).version == 4
               and pin(value['container_id']) and pin(value['volume_created_at'], re.compile('[0-9TZ:.+\\-]{20,64}'))
               and pin(value['source_commit'], SHA40) and pin(value['source_tree'], SHA40)
               and value['candidate_commit'] == CANDIDATE_COMMIT and value['candidate_catalog_sha256'] == proof.CATALOG_SHA
               and value['ordered_migration_sha256'] == list(proof.MIGRATION_SHA)
               and pin(value['source_author'], ACTOR) and pin(value['reviewer'], ACTOR) and value['source_author'] != value['reviewer']
               and type(value['files_sha256']) is dict and set(value['files_sha256']) == set(REQUIRED_FILES)
               and all(pin(digest) for digest in value['files_sha256'].values()), 'TRACK_INDEPENDENT_ACTUAL_ACCEPTANCE_SHAPE')


def validate(value, files, *, corrected_source_pins):
    """Corroborate the acceptance against the actual archived receipts and result."""
    acceptance_shape(value)
    proof.need(set(files) == set(REQUIRED_FILES) and value['files_sha256'] == {name: proof.sha(raw) for name, raw in files.items()},
               'TRACK_PRIOR_EXACT_EVIDENCE_BYTES')
    plan, exit_row, container, volume, report, result, audit = (proof.unique_json(files[name]) for name in REQUIRED_FILES)
    run, cid, birth = (value[key] for key in ('run_id', 'container_id', 'volume_created_at'))
    packet_sha = value['files_sha256']['operation.json']
    source = {key: value['source_' + key] for key in ('commit', 'tree')}
    target = plan['target']
    proof.need(plan['schema'] == PLAN_SCHEMA and plan['source'] == source and target['network'] == 'none'
               and plan['native_expected_sha256'] == proof.CATALOG_SHA and plan['posture'] == 'D'
               and plan['candidate_adoption'] is False and plan['business_tests_executed'] is False
               and plan['candidate_commit'] == value['candidate_commit']
               and [row['sha256'] for row in plan['ledger_expected']] == list(proof.MIGRATION_SHA)
               and all(plan['source_pins'].get(name) == digest for name, digest in corrected_source_pins.items())
               and all(row['run_id'] == run for row in (plan, exit_row, container, volume, report, result, audit)),
               'TRACK_PRIOR_CORRECTED_RUN_SOURCE_AND_POSTURE')
    own = report['targets'][target['container_name']]
    proof.need(container['id'] == own['container_id'] == result['container_id'] == cid
               and container['name'] == target['container_name'] and volume['name'] == target['volume_name']
               and volume['created_at'] == own['volume_created_at'] == birth
               and container['labels'] == volume['labels'] == own['labels'] == target['labels']
               and own['finalization'] == 'PASS' and report['actual_daemon'] == plan['daemon'] == audit['daemon']
               and report['image'] == plan['image'] == audit['image'], 'TRACK_PRIOR_EXACT_RESOURCE_IDENTITY')
    proof.need(exit_row['method'] == 'ACTUAL_OPERATING_PROCESS_EXIT' and type(exit_row['exit_code']) is int
               and exit_row['exit_code'] == 0 and exit_row['stdout_status'] == PASS and exit_row['evidence_complete'] is True
               and exit_row.get('first_reported_failure') is None and exit_row['source_commit'] == source['commit']
               and exit_row['outer_evidence_sha256'] == value['files_sha256']['evidence/run-evidence.json']
               and exit_row['packet_sha256'] == result['packet_sha256'] == report['approved_packet_sha256'] == packet_sha
               and report['approved_commit'] == result['source_commit'] == source['commit']
               and report['approved_tree'] == result['source_tree'] == source['tree']
               and report['schema'] == RUN_SCHEMA and result['schema'] == RESULT_SCHEMA
               and report['status'] == result['status'] == PASS and report['unexpected'] == [] and 'primary_failure' not in report
               and result['Posture'] == 'D' and type(result['business_assertions_qualified']) is int
               and result['business_assertions_qualified'] == 0 and result['original_grantor_finalized'] is True
               and result['source_expected_sha256'] == proof.CATALOG_SHA, 'TRACK_PRIOR_ACTUAL_EXIT_AND_RESULT')
    native = result['native']
    proof.need(native == report['native_results'] and set(native) == {'initial', 'noop'}
               and native['initial']['native_sha256'] == native['noop']['native_sha256']
               and pin(native['noop']['native_sha256'])
               and all(proof.canonical((row['applied_rows'], row['oracle_expressions'], row['catalog_check_counts'], row['ledger_checks']))
                       == proof.canonical((3, 416, {'PASS': 29089}, 22)) for row in native.values())
               and result['full8_noop']['all_eight_columns_compared'] is True and result['full8_noop']['history_count'] == 3
               and result['full8_noop']['status'] == 'PASS_EXACT_THREE_ROW_HASH_PRESERVATION_ONLY'
               and result['track']['finalization_and_noop_preserved_all_eight_ledger_columns'] is True
               and result['track']['three_applied_historical_order'] == plan['ledger_expected']
               and result['track']['business_cases'] == 'NOT_RUN', 'TRACK_PRIOR_NATIVE_LEDGER_NOOP_PROOF')
    authority = result['track']['authority']
    proof.need(set(authority) == {'PRE_DEPLOY', 'PRE_FINALIZATION', 'POST_FINALIZATION', 'POST_NOOP'}
               and authority == report['track_authority']
               and all(row['phase'] == phase and row['exact_role_options'] is True and row['leaf_create_absent'] is True
                       and row['candidate_function_bodies_verified'] is (phase != 'PRE_DEPLOY') for phase, row in authority.items())
               and result['track']['pre_finalization']['applied_rows'] == 3
               and result['track']['pre_finalization']['ledger_checks'] == 22, 'TRACK_PRIOR_ACTUAL_AUTHORITY_PROOF')
    receipts = report['migration_results']
    proof.need([row['operation'] for row in receipts] == ['deploy', 'status', 'deploy']
               and receipts[-1]['no_pending_message_observed'] is True
               and all(row['run_id'] == run and row['container_id'] == cid and row['packet_sha256'] == packet_sha
                       and type(row['exit_code']) is int and row['exit_code'] == 0
                       and row['status'] == 'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS'
                       and row['track_retained_sql_sha256'] == proof.MIGRATION_SHA[-1] for row in receipts),
               'TRACK_PRIOR_REAL_DEPLOY_STATUS_NOOP')
    proof.need(report['cleanup'] == 'EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT'
               and report['cleanup_full_container_identity_absent'] is True and report['transport']['unknown_closure'] is False
               and report['cleanup_steps'] == dict.fromkeys(('docker_resources', 'local_client', 'private_files'), 'CONFIRMED')
               and report['immutable_source_postcheck'] == 'PASS' and report['final_original_references_verified'] is True
               and audit['decision'] == CLOSURE_DECISION and audit['reviewer'] == value['reviewer']
               and audit['created_container'] == container and audit['created_volume'] == volume
               and audit['cleanup_verified'] == dict.fromkeys(CLEANUP, True)
               and all(audit['file_sha256'][name] == value['files_sha256'][name] for name in REQUIRED_FILES if name != 'independent-closure.json'),
               'TRACK_PRIOR_INDEPENDENT_EXACT_CLOSURE')
    return {'run_id': run, 'container_id': cid, 'volume_created_at': birth,
            'daemon': plan['daemon'], 'image': plan['image'], 'reviewer': value['reviewer']}


def load(path, expected_sha, root, *, corrected_source_pins):
    path = Path(path)
    proof.need(path.is_absolute() and path.is_relative_to(root), 'TRACK_PRIOR_ACCEPTANCE_CANONICAL_LOCATION')
    relative = path.relative_to(root).as_posix()
    proof.need(ARCHIVE_PATH.fullmatch(relative) is not None and pin(expected_sha), 'TRACK_PRIOR_ACCEPTANCE_PIN_REQUIRED')
    raw = proof.path_hash(path, expected_sha)
    value = proof.unique_json(raw)
    acceptance_shape(value)
    proof.need(path.parent.name == 'track-' + value['run_id'][:8], 'TRACK_PRIOR_ACCEPTANCE_DIRECTORY_BINDING')
    files = {name: proof.path_hash(path.parent / name, digest) for name, digest in value['files_sha256'].items()}
    inputs = {relative: raw, **{(path.parent / name).relative_to(root).as_posix(): data for name, data in files.items()}}
    return validate(value, files, corrected_source_pins=corrected_source_pins), inputs
