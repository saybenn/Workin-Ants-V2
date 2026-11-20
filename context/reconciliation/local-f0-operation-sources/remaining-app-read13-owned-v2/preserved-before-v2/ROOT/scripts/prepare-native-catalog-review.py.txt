"""Prepare deterministic native-catalog review assets; never execute SQL.

Import/help use only stdlib. An independently reviewed caller must prehash this
generator before calling load_catalog_tools. Every executable helper (including
the optional masked-ledger validator), all eight source inputs and both SQL
collectors are then verified before any helper executes. pglast==7.21 is the
separately installed offline parser dependency, not a database connection.
"""
import argparse
import builtins
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
MODULE_FILES = (
    'scripts/sql-review/catalog_manifest.py',
    'scripts/sql-review/pg17_catalog_rules.py',
    'scripts/sql-review/prisma_ledger_proof.py',
    'scripts/sql-review/compare_native_catalog.py',
    'scripts/sql-review/catalog_expression_oracle.py',
    'scripts/sql-review/migration_server_diagnostics.py',
)
INPUT_FILES = (
    'review-output/foundation-bootstrap.review.sql',
    'review-output/foundation-application.review.sql',
    'review-output/foundation-bootstrap-finalize.review.sql',
    'scripts/sql-review/foundation-bootstrap-finalize.sql',
    'prisma/review/foundation-candidate.prisma',
    'context/reconciliation/foundation-sql-draft-models.json',
    'context/reconciliation/foundation-sql-draft-access.json',
    'context/reconciliation/foundation-sql-verifier-access.json',
)
COLLECTOR_FILES = ('scripts/sql-review/collect_native_catalog.sql', 'scripts/sql-review/collect_prisma_ledger.sql')
REQUIRED_FILES = MODULE_FILES + INPUT_FILES + COLLECTOR_FILES
ARTIFACT_FILES = ('source-pins.json', 'expected.json', 'expression-oracle-plan.json',
                  'expression-oracle.sql', 'public-schema-registration.json', 'README.md')
PUBLIC_MODULES = tuple(Path(path).stem for path in MODULE_FILES[:5])
STANDARD_IMPORTS = {'__future__', 'argparse', 'collections', 'hashlib', 'json', 'pathlib', 're',
                    'subprocess', 'unicodedata', 'uuid'}
DATABASE = 'wa_p0c_rehearsal'
GRANTOR = 'postgres'
PUBLIC_OWNER = 'pg_database_owner'
EXPECTED_CATALOG_SHA256 = '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433'


class PreparationFailure(Exception):
    """Only fixed codes may leave this environment-free preparation boundary."""
    def __init__(self, code): self.code = code; super().__init__(code)


def require(value, code):
    if not value: raise PreparationFailure(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf8')


def unique_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'DUPLICATE_JSON_FIELD'); value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def verified_sources(root, pins):
    root = Path(root).resolve()
    require(type(pins) is dict and set(pins) == set(REQUIRED_FILES) and
            all(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) for value in pins.values()), 'COMPLETE_CLOSED_SOURCE_PINS_REQUIRED')
    blobs = {}
    for relative in REQUIRED_FILES:
        path = (root / relative).resolve()
        require(path.is_relative_to(root), 'SOURCE_PATH_ESCAPES_ROOT')
        try: raw = path.read_bytes()
        except Exception: raise PreparationFailure('SOURCE_INPUT_UNREADABLE') from None
        require(sha(raw) == pins[relative], 'SOURCE_INPUT_HASH_MISMATCH')
        blobs[relative] = raw
    return root, blobs


def _execute_module(code, module):
    exec(code, module.__dict__)


def load_catalog_tools(root, pins):
    """Return five tools; all helper imports use exact prehashed source bytes.

    No helper is installed in global sys.modules. A preexisting named helper
    cache is rejected rather than silently reused. Local imports are isolated;
    the ledger's sole runpy path returns the already compiled diagnostic module
    and never opens or executes the on-disk helper a second time.
    """
    root, blobs = verified_sources(root, pins)
    paths = {Path(relative).stem: relative for relative in MODULE_FILES}
    require(not any(name in sys.modules for name in paths), 'PRELOADED_HELPER_CACHE_REJECTED')
    try:
        import pglast
        require(pglast.__version__ == 'v7.21', 'PINNED_OFFLINE_PARSER_REQUIRED')
        code = {name: compile(blobs[relative], str(root / relative), 'exec', dont_inherit=True)
                for name, relative in paths.items()}
    except PreparationFailure: raise
    except Exception: raise PreparationFailure('PARSER_OR_HELPER_COMPILE_FAILED') from None
    modules = {name: ModuleType(name) for name in paths}
    states = dict.fromkeys(paths, 'UNLOADED')
    ordinary_import = builtins.__import__

    def load(name):
        if states[name] == 'LOADED': return modules[name]
        require(states[name] == 'UNLOADED', 'CIRCULAR_HELPER_IMPORT_REJECTED')
        states[name] = 'LOADING'
        module = modules[name]
        module.__file__ = str(root / paths[name]); module.__package__ = ''
        module.__dict__['__builtins__'] = {**vars(builtins), '__import__': pinned_import}
        output, errors = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(errors): _execute_module(code[name], module)
        except PreparationFailure: raise
        except BaseException: raise PreparationFailure('PINNED_HELPER_LOAD_FAILED') from None
        require(not output.getvalue() and not errors.getvalue(), 'PINNED_HELPER_OUTPUT_REJECTED')
        states[name] = 'LOADED'
        return module

    def closed_run_path(path, init_globals=None, run_name=None):
        require(init_globals is None and run_name is None and
                Path(path).resolve() == (root / MODULE_FILES[-1]).resolve(), 'UNREGISTERED_RUNPY_PATH_REJECTED')
        return dict(load('migration_server_diagnostics').__dict__)

    runpy_shim = ModuleType('runpy')
    runpy_shim.run_path = closed_run_path

    def pinned_import(name, globals=None, locals=None, fromlist=(), level=0):
        require(level == 0, 'RELATIVE_HELPER_IMPORT_REJECTED')
        if name in paths: return load(name)
        if name == 'runpy': return runpy_shim
        base = name.split('.')[0]
        require(base in STANDARD_IMPORTS or base == 'pglast', 'UNREGISTERED_HELPER_IMPORT_REJECTED')
        return ordinary_import(name, globals, locals, fromlist, level)

    for name in paths: load(name)
    source = modules['catalog_manifest']
    require(tuple(source.INPUTS) == INPUT_FILES, 'CATALOG_INPUT_CHAIN_CHANGED')
    require(tuple(modules['catalog_expression_oracle'].SOURCE_MODULES) == (
        MODULE_FILES[0], MODULE_FILES[3], MODULE_FILES[1], MODULE_FILES[4], COLLECTOR_FILES[0]), 'ORACLE_HELPER_CHAIN_CHANGED')
    require(modules['prisma_ledger_proof'].DIAGNOSTICS == MODULE_FILES[-1] and
            modules['prisma_ledger_proof'].COLLECTOR == COLLECTOR_FILES[1], 'LEDGER_HELPER_CHAIN_CHANGED')
    return {name: modules[name] for name in PUBLIC_MODULES}


def public_registration(manifest, source):
    baseline = [{'grantee': grantee, 'grantor': PUBLIC_OWNER, 'privilege': privilege, 'grant_option': False}
                for grantee, privilege in ((PUBLIC_OWNER, 'CREATE'), (PUBLIC_OWNER, 'USAGE'), ('PUBLIC', 'USAGE'))]
    added = []
    for row in manifest['expected']['nonowner_acl']:
        if row['kind'] == 'SCHEMA' and row['object'] == 'public':
            require(row['scope'] == 'object' and row['columns'] == [] and row['grantor'] == source.PUBLIC_SCHEMA_OWNER,
                    'PUBLIC_SOURCE_GRANT_RECIPE_CHANGED')
            added.append({'grantee': row['grantee'], 'grantor': PUBLIC_OWNER, 'privilege': row['privilege'], 'grant_option': row['grant_option']})
    added.sort(key=canonical)
    expected_added = [{'grantee': 'wa_migrator', 'grantor': PUBLIC_OWNER, 'privilege': privilege, 'grant_option': False}
                      for privilege in ('CREATE', 'USAGE')]
    require(added == expected_added, 'PUBLIC_SOURCE_GRANT_RECIPE_CHANGED')
    return {'format': 'workinants.public-schema-registration.v1', 'owner': PUBLIC_OWNER,
            'requires_prebootstrap_verification': True, 'baseline_acl': baseline,
            'source_added_acl': added, 'full_acl': baseline + added}


def prepare(root, pins):
    root = Path(root).resolve()
    tools = load_catalog_tools(root, pins)
    try:
        source, oracle = tools['catalog_manifest'], tools['catalog_expression_oracle']
        manifest = source.build_manifest(root, pins)
        require(manifest['expected_sha256'] == EXPECTED_CATALOG_SHA256 and
                manifest['approval_binding'] == 'ALL_INPUT_HASHES_VERIFIED', 'EXPECTED_SOURCE_CATALOG_CHANGED')
        plan = oracle.build_plan(manifest, root)
        require(plan['server_version_num'] == 170011 and plan['expression_count'] == 416 and
                plan['expected_tables'] == 42 and plan['expected_columns'] == 600 and
                plan['by_operation'] == {'check-not-valid': 93, 'column-default': 144, 'function-default-list': 4, 'policy': 175}, 'ORACLE_SOURCE_SCOPE_CHANGED')
        sql = oracle.emit_sql(manifest, plan, database=DATABASE, grantor=GRANTOR).encode('utf8')
        registration = public_registration(manifest, source)
    except PreparationFailure: raise
    except BaseException: raise PreparationFailure('CATALOG_ASSET_PREPARATION_FAILED') from None
    verified_sources(root, pins)  # Inputs and code must remain pinned throughout preparation.
    readme = '''Native catalog review assets — all runtime assertions NOT_RUN

These assets are source expectations and a dormant expression oracle. Posture D
remains. Preparation executes no SQL and contacts no database, Docker or network.
The caller independently prehashes this generator and all runtime packet files.
The offline parser is pglast7.21; the actual target must be PostgreSQL17.11.

The root operator must verify the exact fresh local run/container/image/storage,
SCRAM logins, original postgres bootstrap authority, finalization, source pins,
genuine applied migration ledger and independent catalog provenance. Existing
94/451 cases are not promoted by preparing or parsing these files.

public-schema-registration.json is a predeclared recipe, never an observed
post-install baseline. Before bootstrap, verify public owner pg_database_owner
and EXACTLY its CREATE+USAGE plus PUBLIC USAGE, all grant_option=false. Canonical
bootstrap adds ONLY wa_migrator CREATE+USAGE recorded with pg_database_owner as
grantor. Compare the resulting EXACT five rows; do not learn from observed ACLs.

expression-oracle.sql is dormant. Its checked preflight, empty TEMP objects,
source-only expressions and final ROLLBACK require a separately reviewed root
execution wrapper. Retain only bounded booleans/identities/hashes, confirm exact
backend closure/TEMP absence and recollect unchanged native catalogs. Source
definitions and observed catalogs are distinct evidence. No generic error passes.

The loader uses isolated prehashed helper namespaces. Named preloaded helper
caches are rejected. The optional masked-ledger validator can use only its
already compiled pinned diagnostic module; arbitrary runpy paths are denied.
The default catalog pipeline has one genuinely applied initial migration only.

Plain English: This packet is the checklist, not a passing test. Check the room
before moving in; do not copy the room afterward and call that the checklist.
'''
    files = {'source-pins.json': encoded(pins), 'expected.json': encoded(manifest),
             'expression-oracle-plan.json': encoded(plan), 'expression-oracle.sql': sql,
             'public-schema-registration.json': encoded(registration), 'README.md': readme.encode('utf8')}
    summary = {'format': 'workinants.native-catalog-review-preparation.v1', 'status': 'NOT_RUN',
               'database_posture': 'D', 'database_contacted': False, 'sql_executed': False,
               'source_actor': {'database': DATABASE, 'bootstrap_grantor': GRANTOR, 'requires_original_superuser': True},
               'source_expected_sha256': manifest['expected_sha256'], 'server_version_num': 170011,
               'expression_count': plan['expression_count'], 'source_pins_sha256': sha(files['source-pins.json']),
               'files_sha256': {name: sha(value) for name, value in sorted(files.items())},
               'limits': 'Source-only assets; native/ledger/expression/runtime outcomes all NOT_RUN. Independent live prebootstrap public ACL verification required.'}
    return files, summary


def write_assets(directory, files):
    directory = Path(directory).resolve()
    require(type(files) is dict and set(files) == set(ARTIFACT_FILES) and
            all(type(value) is bytes for value in files.values()), 'FIXED_ARTIFACT_NAMES_REQUIRED')
    if directory.exists():
        require(directory.is_dir() and {p.name for p in directory.iterdir()} == set(files), 'EXISTING_OUTPUT_SET_DIFFERS')
        require(all((directory / name).is_file() and not (directory / name).is_symlink() and
                    (directory / name).read_bytes() == value for name, value in files.items()), 'EXISTING_OUTPUT_BYTES_DIFFER')
        return False
    directory.mkdir(parents=True, exist_ok=False)
    for name, raw in sorted(files.items()):
        with (directory / name).open('xb') as handle: handle.write(raw)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-review-assets', action='store_true')
    parser.add_argument('--pins', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'review-output/native-catalog')
    args = parser.parse_args(argv)
    try:
        require(args.prepare_review_assets and args.pins is not None, 'EXPLICIT_PREPARATION_AND_PINS_REQUIRED')
        pins = unique_json(args.pins.read_text(encoding='utf8'))
        files, summary = prepare(ROOT, pins)
        created = write_assets(args.output_dir, files)
        print(json.dumps({**summary, 'assets_written': created, 'existing_identical_assets_preserved': not created}, sort_keys=True))
        return 0
    except BaseException as error:
        print(json.dumps({'format': 'workinants.native-catalog-review-preparation.v1', 'status': 'REFUSED',
                          'code': error.code if isinstance(error, PreparationFailure) else 'UNEXPECTED_PREPARATION_FAILURE',
                          'database_contacted': False, 'sql_executed': False}, sort_keys=True))
        return 2


if __name__ == '__main__': raise SystemExit(main())
