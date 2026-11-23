"""Prepare a NEW ordered-source native checklist; never execute SQL/processes.

The original one-history generator and catalog helpers are not changed. All
new and old source bytes are pinned before any helper compilation, and the
original private loader still rejects preloaded helper caches.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SELF = 'scripts/prepare-native-runtime-lease-history-v1-review.py'
OLD_PREPARER = 'scripts/prepare-native-catalog-review.py'
CATALOG = 'scripts/sql-review/runtime_lease_effective_catalog_v1.py'
LEDGER = 'scripts/sql-review/runtime_lease_two_row_ledger_v1.py'
PATCH = 'review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql'
OLD_REQUIRED = (
    'scripts/sql-review/catalog_manifest.py', 'scripts/sql-review/pg17_catalog_rules.py',
    'scripts/sql-review/prisma_ledger_proof.py', 'scripts/sql-review/compare_native_catalog.py',
    'scripts/sql-review/catalog_expression_oracle.py', 'scripts/sql-review/migration_server_diagnostics.py',
    'review-output/foundation-bootstrap.review.sql', 'review-output/foundation-application.review.sql',
    'review-output/foundation-bootstrap-finalize.review.sql', 'scripts/sql-review/foundation-bootstrap-finalize.sql',
    'prisma/review/foundation-candidate.prisma', 'context/reconciliation/foundation-sql-draft-models.json',
    'context/reconciliation/foundation-sql-draft-access.json', 'context/reconciliation/foundation-sql-verifier-access.json',
    'scripts/sql-review/collect_native_catalog.sql', 'scripts/sql-review/collect_prisma_ledger.sql')
CODE_FILES = (
    'scripts/prepare-local-f0-runtime-lease-history-v1.py',
    'prisma.local-f0-runtime-lease-history-v1.config.mjs',
    'scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs',
    'scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs',
    'scripts/sql-review/run-local-f0-runtime-lease-history-v1.py', CATALOG, SELF, LEDGER,
    'scripts/sql-review/collect_runtime_lease_history_fingerprints_v1.sql',
    'scripts/check-local-f0-runtime-lease-history-v1.py',
    'scripts/sql-review/check-local-f0-runtime-lease-history-v1-guard.mjs',
    'scripts/sql-review/test_runtime_lease_effective_catalog_v1.py',
    'scripts/sql-review/RUNTIME-LEASE-HISTORY-V1.md')
SAFETY_FILES = ('scripts/sql-review/local_image_identity.py', 'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json', 'context/reconciliation/local-f0-tooling/prisma-tools-closure.json')
TOOL_METADATA = {
    'node_modules/prisma/package.json': ('prisma-package.json', '6cdfef6df08d9a37f28908855797fe8bfc97a2d3d886a8d5cbe2e502d6848151'),
    'node_modules/@prisma/engines-version/package.json': ('engines-version-package.json', '2dd9793255d6bbb5c399a624ecbfb6323d39233860863d172946b7f750f528bd')}
TOOL_SNAPSHOT_ROOT = 'context/reconciliation/local-f0-operation-sources/runtime-lease-two-history-v1/tool-source-metadata/'
REQUIRED_FILES = tuple(dict.fromkeys((*OLD_REQUIRED, OLD_PREPARER, *CODE_FILES, PATCH, *SAFETY_FILES,
                                    *(TOOL_SNAPSHOT_ROOT + leaf for leaf, _ in TOOL_METADATA.values()))))
ASSETS = ('source-pins.json', 'expected.json', 'expression-oracle-plan.json',
          'expression-oracle.sql', 'public-schema-registration.json', 'README.md')


class PreparationFailure(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise PreparationFailure(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def unique_json(raw):
    def pairs(items):
        value = {}
        for k, v in items:
            require(k not in value, 'DUPLICATE_JSON')
            value[k] = v
        return value
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(PreparationFailure('NONFINITE_JSON')))


def verified_sources(root, pins):
    root = Path(root).resolve()
    require(type(pins) is dict and set(pins) == set(REQUIRED_FILES) and
            all(type(h) is str and re.fullmatch('[0-9a-f]{64}', h) for h in pins.values()),
            'COMPLETE_NEW_CLOSED_SOURCE_MAP')
    blobs = {}
    for relative in REQUIRED_FILES:
        path = root / relative
        require(path.resolve().is_relative_to(root), 'SOURCE_PATH_CONFINEMENT')
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and not path.is_symlink() and info.st_nlink == 1
                and type(info.st_size) is int and 0 <= info.st_size <= 16 * 1024 * 1024,
                'REGULAR_BOUNDED_SOURCE_REQUIRED')
        with path.open('rb') as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
        require(len(raw) <= 16 * 1024 * 1024 and sha(raw) == pins[relative], 'SOURCE_BYTES_DRIFT')
        blobs[relative] = raw
    tool_metadata_closure(root, blobs)
    return root, blobs


def tool_metadata_closure(root, blobs):
    """Only two pinned installed metadata files may resolve outside the checkout.

    Their committed snapshots and the10300 archive map independently bind
    bytes. A node_modules junction is a tooling location, never a general
    source-path escape exception. No other ignored path is read here.
    """
    closure = unique_json(blobs['context/reconciliation/local-f0-tooling/prisma-tools-closure.json'])
    for relative, (leaf, wanted) in TOOL_METADATA.items():
        expected = blobs[TOOL_SNAPSHOT_ROOT + leaf]
        require(sha(expected) == wanted == closure['tools_files_sha256'].get(relative),
                'PINNED_TWO_TOOL_SNAPSHOTS')
        path = root / relative
        before = path.lstat()
        require(not path.is_symlink() and stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1 and 0 < before.st_size <= 1024 * 1024,
                'TWO_TOOL_METADATA_REGULAR_FILES')
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            require((opened.st_dev, opened.st_ino, opened.st_size) ==
                    (before.st_dev, before.st_ino, before.st_size),
                    'TWO_TOOL_METADATA_OPEN_IDENTITY')
            raw = stream.read(1024 * 1024 + 1)
            final = os.fstat(stream.fileno())
        after = path.lstat()
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
                and (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) ==
                    (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns)
                and raw == expected and sha(raw) == wanted, 'TWO_TOOL_METADATA_BYTES')


def compile_verified(relative, raw, root):
    module = ModuleType('_ordered_source_' + Path(relative).stem.replace('-', '_'))
    module.__file__ = str(root / relative)
    exec(compile(raw, module.__file__, 'exec', dont_inherit=True), module.__dict__)
    return module


def load_tools(root, pins):
    root, blobs = verified_sources(root, pins)
    require(not any(name in sys.modules for name in (
        'runtime_lease_effective_catalog_v1', 'runtime_lease_two_row_ledger_v1')),
        'NEW_HELPER_CACHE_REJECTED')
    original = compile_verified(OLD_PREPARER, blobs[OLD_PREPARER], root)
    require(tuple(original.REQUIRED_FILES) == OLD_REQUIRED, 'UNCHANGED_ORIGINAL_GRAPH')
    tools = original.load_catalog_tools(root, {p: pins[p] for p in OLD_REQUIRED})
    effective = compile_verified(CATALOG, blobs[CATALOG], root)
    ledger = compile_verified(LEDGER, blobs[LEDGER], root)
    return original, tools, effective, ledger, blobs


def prepare(root, pins):
    root = Path(root).resolve()
    original, tools, effective, ledger, blobs = load_tools(root, pins)
    source, oracle = tools['catalog_manifest'], tools['catalog_expression_oracle']
    inputs = {p: blobs[p] for p in (*source.INPUTS, PATCH)}
    manifest = effective.build_manifest(source, inputs, pins)
    require(manifest['expected_sha256'] != effective.OLD_EXPECTED and
            manifest['ordered_source']['new_body_sha256'] == effective.NEW_BODY,
            'DISTINCT_EFFECTIVE_SOURCE_REQUIRED')
    plan = oracle.build_plan(manifest, root)
    require(plan['server_version_num'] == 170011 and plan['expected_tables'] == 42 and
            plan['expected_columns'] == 600 and type(plan['expression_count']) is int and
            plan['expression_count'] > 0, 'MEASURED_COMPLETE_ORACLE_REQUIRED')
    sql = oracle.emit_sql(manifest, plan, database='wa_p0c_rehearsal', grantor='postgres').encode()
    public = original.public_registration(manifest, source)
    readme = b'''NEW ordered initial+append expected catalog. All runtime outcomes NOT_RUN.
Posture D. Never apply this expectation/projection as SQL. Apply only the exact
two numbered migration files through the separately reviewed genuine Prisma
deploy/status path. No old initial-only expected hash or single-ledger proof
admits this family. Existing collectors/comparators remain unchanged.

The full source-derived manifest changes only runtime_transition body and its
explicit source AST/append statement provenance; owners, invoker/proconfig,
ACLs/RLS/defaults,100guards and32workerACL remain exact. Native oracle/TEMP
ROLLBACK, original-grantor finalization, source8/tools, exact public baseline,
two genuine applied ledger rows, immutable no-op row hashes, fresh run/CID and
closed backend proof are separate mandatory future observations.

The isolated11-case native mechanism must be reviewed/exercised before any
corrected App or affected Worker qualification. No business claim is made.
Plain English: this is the new checklist, not proof the building was built.
'''
    files = {'source-pins.json': encoded(pins), 'expected.json': encoded(manifest),
        'expression-oracle-plan.json': encoded(plan), 'expression-oracle.sql': sql,
        'public-schema-registration.json': encoded(public), 'README.md': readme}
    verified_sources(root, pins)
    summary = {'schema': 'workinants.runtime-lease-native-preparation.v1', 'status': 'NOT_RUN',
        'source_expected_sha256': manifest['expected_sha256'],
        'expected_file_sha256': sha(files['expected.json']),
        'initial_sql_sha256': effective.INITIAL, 'append_sql_sha256': effective.PATCH,
        'function_body_sha256': effective.NEW_BODY,
        'counts': manifest['counts'], 'expression_count': plan['expression_count'],
        'expression_by_operation': plan['by_operation'],
        'files_sha256': {k: sha(v) for k, v in files.items()},
        'database_contacted': False, 'sql_executed': False,
        'Posture': 'D', 'source_review': 'PENDING'}
    return files, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pins', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-source-assets', action='store_true')
    args = parser.parse_args(argv)
    require(args.prepare_source_assets, 'EXPLICIT_SOURCE_PREPARATION_REQUIRED')
    files, summary = prepare(ROOT, unique_json(args.pins.read_bytes()))
    output = args.output.resolve()
    require(output.is_relative_to(ROOT.resolve()) and not output.exists(), 'FRESH_PRIVATE_ASSET_DIRECTORY')
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in files.items():
        (output / name).open('xb').write(raw)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
