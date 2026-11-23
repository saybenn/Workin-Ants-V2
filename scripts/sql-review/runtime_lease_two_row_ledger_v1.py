"""Narrow two-applied-row policy around the unchanged genuine ledger proof.

No database/process/I/O APIs are imported. Registration delegates source-file
verification to the caller-supplied pinned proof module. No observations are
ever used to construct expectations.
"""
import hashlib
import json
import re
import uuid

HISTORY = 'prisma/local-f0-runtime-lease-history-v1/migrations'
ORDERED = (
    ('20261117000100_f0_local_initial', '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'),
    ('20261120000100_f0_runtime_lease_branch_v1', '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7'))
HASH = re.compile('[0-9a-f]{64}')
TOOL_METADATA = {
    'node_modules/prisma/package.json': '6cdfef6df08d9a37f28908855797fe8bfc97a2d3d886a8d5cbe2e502d6848151',
    'node_modules/@prisma/engines-version/package.json': '2dd9793255d6bbb5c399a624ecbfb6323d39233860863d172946b7f750f528bd'}


def require(ok, code):
    if not ok:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def registration(proof, *, root, run_id, target_attestation_sha256, source_expected_sha256):
    require(type(run_id) is str and str(uuid.UUID(run_id)) == run_id and uuid.UUID(run_id).version == 4,
            'EXACT_UUID4_RUN')
    rows = [{'path': HISTORY + '/' + name + '/migration.sql', 'migration_name': name,
             'sha256': h, 'state': 'applied', 'count': 1} for name, h in ORDERED]
    before = proof._tool_pins()
    require(all(before.get(p) == h for p, h in TOOL_METADATA.items()), 'EXACT_TWO_TOOL_METADATA')
    value = proof.build_registration(rows, root=root, run_id=run_id,
        target_attestation_sha256=target_attestation_sha256,
        source_expected_sha256=source_expected_sha256)
    after = proof._tool_pins()
    require(before == after == value['tool_source_files_sha256'],
            'TOOL_METADATA_CHANGED_DURING_REGISTRATION')
    require(value['migrations'] == rows and len(value['history_expected']) == 2
            and all(r['finished'] is True and r['rolled_back'] is False and
                    type(r['steps']) is int and r['steps'] == 1 and r['logs_state'] == 'NULL'
                    for r in value['history_expected']), 'EXACT_TWO_GENUINE_APPLIED_EXPECTATIONS')
    return value


def fingerprint_shape(value):
    keys = {'schema', 'server_version_num', 'database', 'collected_as',
            'collector_is_superuser', 'read_only', 'history_count', 'rows'}
    require(type(value) is dict and set(value) == keys, 'FINGERPRINT_FIELDS')
    require(value['schema'] == 'workinants.runtime-lease-history-fingerprints.v1'
            and type(value['server_version_num']) is int and value['server_version_num'] == 170011
            and value['database'] == 'wa_p0c_rehearsal' and value['collected_as'] == 'postgres'
            and value['collector_is_superuser'] is True and value['read_only'] is True
            and type(value['history_count']) is int and value['history_count'] == 2,
            'FINGERPRINT_SOURCE_CONTEXT')
    expected = sorted((sha(name.encode()), sha(h.encode())) for name, h in ORDERED)
    rows = value['rows']
    require(type(rows) is list and len(rows) == 2, 'TWO_FULL_ROW_FINGERPRINTS')
    observed = []
    for row in rows:
        require(type(row) is dict and set(row) == {'name_sha256', 'checksum_sha256', 'row_sha256'}
                and all(type(h) is str and HASH.fullmatch(h) for h in row.values()),
                'FINGERPRINT_ROW_FIELDS')
        observed.append((row['name_sha256'], row['checksum_sha256']))
    require(observed == expected, 'FINGERPRINT_EXACT_SOURCE_IDENTITIES')
    return value


def compare_noop(before, after):
    fingerprint_shape(before)
    fingerprint_shape(after)
    require(json.dumps(before, sort_keys=True, separators=(',', ':'), allow_nan=False) ==
            json.dumps(after, sort_keys=True, separators=(',', ':'), allow_nan=False),
            'NOOP_CHANGED_A_FULL_LEDGER_ROW')
    return {'schema': 'workinants.runtime-lease-noop-full-ledger-proof.v1',
            'status': 'PASS_EXACT_TWO_ROW_HASH_PRESERVATION_ONLY',
            'history_count': 2, 'all_eight_columns_unchanged': True,
            'database_qualification_claimed': False}
