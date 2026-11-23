"""Prepare exactly two reviewed local migration files; no process/database I/O.

This separate namespace cannot overwrite/adopt the original initial history.
The original initial SQL and append SQL retain their own transaction envelopes.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
HISTORY = 'prisma/local-f0-runtime-lease-history-v1/migrations'
MANIFEST = 'prisma/local-f0-runtime-lease-history-v1/history-manifest.json'
SCHEMA = 'prisma/review/foundation-candidate.prisma'
INITIAL_PATH = 'review-output/foundation-application.review.sql'
PATCH_PATH = 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql'
INITIAL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
PATCH = '49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7'
SCHEMA_SHA = 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723'
ORDERED = (('20261117000100_f0_local_initial', INITIAL),
           ('20261120000100_f0_runtime_lease_branch_v1', PATCH))
RUNTIME_FILES = ('prisma.local-f0-runtime-lease-history-v1.config.mjs',
    'scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs',
    'scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs')
IMAGE = 'docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'
HASH = re.compile('[0-9a-f]{64}')


class HeldFailure(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise HeldFailure(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def unique_json(raw):
    def pairs(items):
        value = {}
        for k, v in items:
            require(k not in value, 'DUPLICATE_JSON')
            value[k] = v
        return value
    require(type(raw) in (bytes,str) and 0 < len(raw) <= 4*1024*1024, 'BOUNDED_JSON')
    value=json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(HeldFailure('NONFINITE_JSON')))
    def typed(v,depth=0):
        require(depth <= 48,'JSON_DEPTH')
        if type(v)is dict:
            for x in v.values():typed(x,depth+1)
        elif type(v)is list:
            for x in v:typed(x,depth+1)
        else:require(v is None or type(v)in(str,bool,int),'STRICT_JSON_TYPES')
    typed(value);return value


def ordered_rows():
    return [{'id': name, 'path': HISTORY + '/' + name + '/migration.sql', 'sha256': h}
            for name, h in ORDERED]


def validate_bootstrap_secret_path(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z]:\\[^\x00-\x1f<>"|?*]+', value)
            and '/' not in value and ':' not in value[2:] and
            all(p and p not in ('.', '..') and not p.endswith((' ', '.')) for p in value[3:].split('\\')),
            'ABSOLUTE_WINDOWS_SECRET_PATH_REQUIRED')
    path, task, checkout = PureWindowsPath(value), PureWindowsPath(str(ROOT.parent)), PureWindowsPath(str(ROOT))
    require(path.is_absolute() and path.is_relative_to(task) and not path.is_relative_to(checkout)
            and len(path.parts) >= len(task.parts) + 2, 'TASK_OWNED_EXTERNAL_SECRET_PATH_REQUIRED')
    return value


def validate_manifest(value):
    require(type(value) is dict and set(value) == {'schema', 'run_id', 'purpose', 'target', 'source', 'history', 'tools'}, 'NEW_RUN_FIELDS')
    require(value['schema'] == 'workinants.local-f0-runtime-lease-history-run.v1'
            and value['purpose'] == 'LOCAL_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL', 'NEW_HISTORY_SCHEMA_REQUIRED')
    run = value['run_id']
    require(type(run) is str and str(uuid.UUID(run)) == run and uuid.UUID(run).version == 4, 'UUID4_RUN_REQUIRED')
    target = value['target']
    require(type(target) is dict and set(target) == {'container_name', 'volume_name', 'database', 'image', 'network', 'labels', 'bootstrap_secret_host_path'}, 'TARGET_FIELDS')
    validate_bootstrap_secret_path(target['bootstrap_secret_host_path'])
    for key in ('container_name', 'volume_name'):
        require(type(target[key]) is str and re.fullmatch('wa-p0c-[a-z0-9][a-z0-9-]{0,110}', target[key]), 'RESOURCE_NAME')
    require(target['database'] == 'wa_p0c_rehearsal' and target['image'] == IMAGE and target['network'] == 'none', 'PINNED_PRIVATE_TARGET')
    require(target['labels'] == {'workinants.rehearsal': 'p0c-local-f0', 'workinants.rehearsal.run': run}, 'EXACT_RUN_LABELS')
    history = value['history']
    require(type(history) is dict and set(history) == {'path', 'ordered'} and history['path'] == HISTORY
            and history['ordered'] == ordered_rows(), 'EXACT_ORDERED_TWO_HISTORY')
    source = value['source']
    require(type(source) is dict and set(source) == {'initial_sql_sha256', 'append_sql_sha256',
        'ordered_history_sha256', 'effective_expected_sha256', 'foundation_schema_sha256', 'runtime_files_sha256'}, 'SOURCE_FIELDS')
    require(source['initial_sql_sha256'] == INITIAL and source['append_sql_sha256'] == PATCH
            and source['foundation_schema_sha256'] == SCHEMA_SHA and
            source['ordered_history_sha256'] == sha(canonical(ordered_rows()).encode()) and
            type(source['effective_expected_sha256']) is str and HASH.fullmatch(source['effective_expected_sha256'])
            and source['effective_expected_sha256'] != '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433',
            'DISTINCT_ORDERED_SOURCE_PINS')
    runtime = source['runtime_files_sha256']
    require(type(runtime) is dict and set(runtime) == set(RUNTIME_FILES)
            and all(type(h) is str and HASH.fullmatch(h) for h in runtime.values()), 'EXACT_NEW_RUNTIME3')
    tools = value['tools']
    require(type(tools) is dict and set(tools) == {'node_version', 'prisma_version', 'engine_commit', 'files_sha256'}
            and tools['node_version'] == 'v24.22.1' and tools['prisma_version'] == '7.10.1'
            and tools['engine_commit'] == 'd1b3f377ca835d73fd50954a5e22128b9ebdd6b8', 'PINNED_TOOLCHAIN')
    files = tools['files_sha256']
    require(type(files) is dict and len(files) == 10300 and all(p in files for p in (
        'node/bin/node', 'schema-engine', 'node_modules/prisma/build/index.js', 'node_modules/prisma/build/cli.js',
        'node_modules/prisma/config.js', 'node_modules/prisma/package.json')), 'COMPLETE10300_TOOLS')
    require(all(type(p) is str and ':' not in p and '\\' not in p and not p.startswith('/')
        and all(x not in ('', '.', '..') for x in p.split('/')) and type(h) is str and HASH.fullmatch(h)
        for p, h in files.items()), 'SAFE_EXACT_TOOL_MAP')
    return value


def prepare_plan(manifest, manifest_bytes, initial, append, schema, runtime_files):
    validate_manifest(manifest)
    require(unique_json(manifest_bytes) == manifest, 'SAME_RAW_RUN_MANIFEST')
    require(type(initial) is bytes and sha(initial) == INITIAL and type(append) is bytes and sha(append) == PATCH,
            'UNCHANGED_INITIAL_AND_EXACT_APPEND')
    require(type(schema) is bytes and sha(schema) == SCHEMA_SHA, 'UNCHANGED_SCHEMA_DECLARATION')
    require(type(runtime_files) is dict and set(runtime_files) == set(RUNTIME_FILES) and
            {p: sha(raw) for p, raw in runtime_files.items()} == manifest['source']['runtime_files_sha256'], 'NEW_RUNTIME_BYTES')
    files = {HISTORY + '/migration_lock.toml': b'provider = "postgresql"\n',
             ordered_rows()[0]['path']: initial, ordered_rows()[1]['path']: append}
    declared = {**{p: sha(raw) for p, raw in files.items()}, SCHEMA: sha(schema),
                **{p: sha(raw) for p, raw in runtime_files.items()}}
    require(len(declared) == 7, 'SEVEN_DECLARED_PLUS_MANIFEST')
    history = {'schema': 'workinants.local-f0-runtime-lease-history.v1',
        'scope': 'PROVISIONAL_LOCAL_ONLY_NOT_HOSTED_ADOPTION', 'run_id': manifest['run_id'],
        'run_manifest_sha256': sha(manifest_bytes), 'migrations': HISTORY,
        'ordered': ordered_rows(), 'ordered_history_sha256': manifest['source']['ordered_history_sha256'],
        'effective_expected_sha256': manifest['source']['effective_expected_sha256'],
        'foundation_schema': SCHEMA, 'files_sha256': declared,
        'database_contacted': False, 'ledger_created_or_modified': False,
        'raw_structure_applied_separately': False, 'public_source_archive_file_count': 8,
        'applied_history_rule': 'Both exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family.'}
    return files, history


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-reviewed-two-history', action='store_true')
    parser.add_argument('--run-manifest', required=True, type=Path)
    args = parser.parse_args(argv)
    require(args.prepare_reviewed_two_history, 'EXPLICIT_NEW_HISTORY_PREPARATION')
    raw = args.run_manifest.read_bytes()
    value = unique_json(raw)
    files, history = prepare_plan(value, raw, (ROOT / INITIAL_PATH).read_bytes(),
        (ROOT / PATCH_PATH).read_bytes(), (ROOT / SCHEMA).read_bytes(),
        {p: (ROOT / p).read_bytes() for p in RUNTIME_FILES})
    directory = ROOT / HISTORY
    require(not directory.exists() and not (ROOT / MANIFEST).exists(), 'NEW_HISTORY_ALREADY_EXISTS_NO_REWRITE')
    directory.mkdir(parents=True, exist_ok=False)
    for p, blob in files.items():
        path = ROOT / p
        path.parent.mkdir(parents=True, exist_ok=True)
        path.open('xb').write(blob)
    (ROOT / MANIFEST).open('x', encoding='utf8', newline='\n').write(json.dumps(history, indent=2) + '\n')
    print(json.dumps({'status': 'NEW_SOURCE8_PREPARED_NOT_EXECUTED', 'run_id': value['run_id'], 'file_count': 8}))


if __name__ == '__main__':
    main()
