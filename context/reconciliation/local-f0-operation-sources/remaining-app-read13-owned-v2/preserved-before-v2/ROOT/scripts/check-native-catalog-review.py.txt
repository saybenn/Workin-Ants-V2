"""Environment-free catalog asset/loader tests; all process/network calls refused."""
import builtins
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from pglast import ast, parse_sql, parse_plpgsql
from pglast.stream import RawStream

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'scripts/prepare-native-catalog-review.py'
M = runpy.run_path(str(PATH))['prepare'].__globals__
CANARY = 'SOURCE_EXCEPTION_SQL_SECRET_CANARY_DO_NOT_EXPORT'


def pins(root=ROOT): return {name: M['sha']((root / name).read_bytes()) for name in M['REQUIRED_FILES']}


def copy_source(root):
    for name in M['REQUIRED_FILES']:
        destination = root / name; destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())


class CatalogPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        for name in ('run', 'Popen', 'check_output', 'check_call'):
            stack.enter_context(patch.object(subprocess, name, side_effect=AssertionError('PROCESS_FORBIDDEN')))
        stack.enter_context(patch.object(socket, 'create_connection', side_effect=AssertionError('NETWORK_FORBIDDEN')))
        cls.pins = pins()
        cls.files, cls.summary = M['prepare'](ROOT, cls.pins)

    def test_import_help_and_missing_flag_execute_no_helpers_or_parser(self):
        ordinary = builtins.__import__
        helper_names = {Path(name).stem for name in M['MODULE_FILES']}
        def import_guard(name, *args, **kwargs):
            if name.split('.')[0] in helper_names | {'pglast'}: raise AssertionError('UNVERIFIED_IMPORT_FORBIDDEN')
            return ordinary(name, *args, **kwargs)
        namespace = {'__file__': str(PATH), '__name__': 'catalog_preparation_help'}
        with patch.object(builtins, '__import__', side_effect=import_guard):
            exec(compile(PATH.read_bytes(), str(PATH), 'exec'), namespace)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result: namespace['main'](['--help'])
                self.assertEqual(result.exception.code, 0)
                self.assertEqual(namespace['main']([]), 2)

    def test_closed_complete_six_module_eight_input_two_collector_pin_sets(self):
        self.assertEqual((len(M['MODULE_FILES']), len(M['INPUT_FILES']), len(M['COLLECTOR_FILES'])), (6, 8, 2))
        self.assertEqual(len(set(M['REQUIRED_FILES'])), 16)
        self.assertEqual(set(json.loads(self.files['source-pins.json'])), set(M['REQUIRED_FILES']))
        tools = M['load_catalog_tools'](ROOT, self.pins)
        self.assertEqual(set(tools), set(M['PUBLIC_MODULES']))
        self.assertFalse(any(name in sys.modules for name in set(M['PUBLIC_MODULES']) | {'migration_server_diagnostics'}))
        self.assertIs(tools['pg17_catalog_rules'].source, tools['catalog_manifest'])
        self.assertIs(tools['catalog_expression_oracle'].compare, tools['compare_native_catalog'])

    def test_missing_extra_bad_or_drifted_pins_stop_before_any_helper_execution(self):
        for relative in M['REQUIRED_FILES']:
            for mode in ('missing', 'drift'):
                changed = dict(self.pins)
                if mode == 'missing': del changed[relative]
                else: changed[relative] = '0' * 64
                with self.subTest(path=relative, mode=mode), patch.dict(M, _execute_module=lambda *args: self.fail('helper executed before source verification')):
                    with self.assertRaises(M['PreparationFailure']): M['load_catalog_tools'](ROOT, changed)
        for changed in ({**self.pins, 'unknown.py': 'a' * 64}, {**self.pins, M['MODULE_FILES'][0]: True}):
            with self.assertRaises(M['PreparationFailure']): M['load_catalog_tools'](ROOT, changed)

    def test_drifted_throwing_transitive_code_is_never_executed_or_printed(self):
        original = Path.read_bytes
        for relative in M['MODULE_FILES']:
            def read(path): return ("print('" + CANARY + "'); raise RuntimeError('" + CANARY + "')").encode() if path == ROOT / relative else original(path)
            output = io.StringIO()
            with self.subTest(module=relative), patch.object(Path, 'read_bytes', read), patch.dict(M, _execute_module=lambda *args: self.fail('drift executed')), redirect_stdout(output):
                with self.assertRaises(M['PreparationFailure']) as result: M['load_catalog_tools'](ROOT, self.pins)
                self.assertEqual(result.exception.code, 'SOURCE_INPUT_HASH_MISMATCH')
            self.assertNotIn(CANARY, output.getvalue())

    def test_unexpected_preloaded_helper_cache_is_not_reused(self):
        for relative in M['MODULE_FILES']:
            name = Path(relative).stem
            with self.subTest(name=name), patch.dict(sys.modules, {name: ModuleType(name)}), patch.dict(M, _execute_module=lambda *args: self.fail('preloaded cache accepted')):
                with self.assertRaises(M['PreparationFailure']) as result: M['load_catalog_tools'](ROOT, self.pins)
                self.assertEqual(result.exception.code, 'PRELOADED_HELPER_CACHE_REJECTED')

    def test_unknown_imports_and_helper_output_or_exceptions_are_sanitized(self):
        for suffix, expected in (('\nimport invented_catalog_dependency\n', 'UNREGISTERED_HELPER_IMPORT_REJECTED'),
                                 ("\nprint('" + CANARY + "')\n", 'PINNED_HELPER_OUTPUT_REJECTED'),
                                 ("\nraise RuntimeError('" + CANARY + "')\n", 'PINNED_HELPER_LOAD_FAILED')):
            with tempfile.TemporaryDirectory(prefix='offline-catalog-source-', dir=ROOT.parent) as folder:
                copied = Path(folder); copy_source(copied)
                path = copied / M['MODULE_FILES'][0]; path.write_bytes(path.read_bytes() + suffix.encode())
                output = io.StringIO()
                with redirect_stdout(output), self.assertRaises(M['PreparationFailure']) as result: M['load_catalog_tools'](copied, pins(copied))
                self.assertEqual(result.exception.code, expected)
                self.assertNotIn(CANARY, str(result.exception) + output.getvalue())

    def test_exact_verified_bytes_and_diagnostic_namespace_survive_disk_replacement(self):
        with tempfile.TemporaryDirectory(prefix='offline-catalog-bytes-', dir=ROOT.parent) as folder:
            copied = Path(folder); copy_source(copied); approved = pins(copied)
            original = M['_execute_module']; swapped = False
            def execute(code, module):
                nonlocal swapped
                if not swapped:
                    swapped = True
                    (copied / M['MODULE_FILES'][-1]).write_text("print('" + CANARY + "'); raise RuntimeError('" + CANARY + "')", encoding='utf8')
                original(code, module)
            output = io.StringIO()
            with patch.dict(M, _execute_module=execute), redirect_stdout(output): tools = M['load_catalog_tools'](copied, approved)
            diagnostic = tools['prisma_ledger_proof'].runpy.run_path(str(copied / M['MODULE_FILES'][-1]))
            self.assertTrue(callable(diagnostic['validate_proof']))
            self.assertNotIn(CANARY, output.getvalue())
            with self.assertRaises(M['PreparationFailure']): tools['prisma_ledger_proof'].runpy.run_path(str(copied / 'arbitrary.py'))
            with self.assertRaises(M['PreparationFailure']): tools['prisma_ledger_proof'].runpy.run_path(str(copied / M['MODULE_FILES'][-1]), init_globals={})

    def test_preparation_is_byte_reproducible_and_all_runtime_statuses_unrun(self):
        again, summary = M['prepare'](ROOT, self.pins)
        self.assertEqual(again, self.files); self.assertEqual(summary, self.summary)
        self.assertEqual(set(again), set(M['ARTIFACT_FILES']))
        self.assertEqual(summary['status'], 'NOT_RUN'); self.assertEqual(summary['server_version_num'], 170011)
        self.assertFalse(summary['database_contacted'] or summary['sql_executed'])
        self.assertEqual(summary['source_actor'], {'database': 'wa_p0c_rehearsal', 'bootstrap_grantor': 'postgres', 'requires_original_superuser': True})
        expected = json.loads(again['expected.json']); plan = json.loads(again['expression-oracle-plan.json'])
        self.assertEqual(expected['expected_sha256'], M['EXPECTED_CATALOG_SHA256'])
        self.assertEqual(expected['approval_binding'], 'ALL_INPUT_HASHES_VERIFIED')
        self.assertEqual(plan['expression_count'], summary['expression_count'])
        self.assertEqual((plan['expression_count'], plan['expected_tables'], plan['expected_columns']), (416, 42, 600))
        self.assertFalse(plan['database_contacted'] or plan['sql_executed'])
        self.assertEqual(plan['status'], 'DRAFT_PENDING_INDEPENDENT_REVIEW')

    def test_generated_sql_and_all_do_bodies_parse_but_never_execute(self):
        statements = parse_sql(self.files['expression-oracle.sql'].decode())
        self.assertEqual(len(statements), 475)
        transactions = [row.stmt.kind.name for row in statements if isinstance(row.stmt, ast.TransactionStmt)]
        self.assertEqual(transactions, ['TRANS_STMT_BEGIN', 'TRANS_STMT_ROLLBACK'])
        forbidden = (ast.InsertStmt, ast.UpdateStmt, ast.DeleteStmt, ast.CreateSchemaStmt, ast.DropStmt, ast.GrantRoleStmt)
        self.assertFalse(any(isinstance(row.stmt, forbidden) for row in statements))
        tables, functions, gates = 0, 0, 0
        for row in statements:
            item = row.stmt
            if isinstance(item, ast.CreateStmt): self.assertEqual(item.relation.relpersistence, 't'); tables += 1
            if isinstance(item, ast.CreateFunctionStmt):
                self.assertEqual(item.funcname[0].sval, 'pg_temp'); functions += 1
            if isinstance(item, ast.DoStmt): self.assertEqual(len(parse_plpgsql(RawStream()(row))), 1); gates += 1
        self.assertEqual((tables, functions, gates), (42, 4, 1))
        self.assertIn("current_database()='wa_p0c_rehearsal'", self.files['expression-oracle.sql'].decode())

    def test_public_recipe_is_exact_predeclared_three_plus_two_five_rows(self):
        registration = json.loads(self.files['public-schema-registration.json'])
        self.assertEqual(set(registration), {'format', 'owner', 'requires_prebootstrap_verification', 'baseline_acl', 'source_added_acl', 'full_acl'})
        self.assertEqual(registration['format'], 'workinants.public-schema-registration.v1')
        self.assertEqual(registration['owner'], 'pg_database_owner'); self.assertIs(registration['requires_prebootstrap_verification'], True)
        self.assertEqual(registration['baseline_acl'], [{'grantee': who, 'grantor': 'pg_database_owner', 'privilege': privilege, 'grant_option': False}
                         for who, privilege in (('pg_database_owner', 'CREATE'), ('pg_database_owner', 'USAGE'), ('PUBLIC', 'USAGE'))])
        self.assertEqual(registration['source_added_acl'], [{'grantee': 'wa_migrator', 'grantor': 'pg_database_owner', 'privilege': privilege, 'grant_option': False} for privilege in ('CREATE', 'USAGE')])
        self.assertEqual(registration['full_acl'], registration['baseline_acl'] + registration['source_added_acl'])
        self.assertEqual(len(registration['full_acl']), 5)

    def test_public_recipe_never_learns_an_extra_source_or_observed_acl(self):
        tools = M['load_catalog_tools'](ROOT, self.pins); source = tools['catalog_manifest']
        manifest = json.loads(self.files['expected.json'])
        row = next(row for row in manifest['expected']['nonowner_acl'] if row['object'] == 'public')
        row['grant_option'] = True
        with self.assertRaises(M['PreparationFailure']): M['public_registration'](manifest, source)

    def test_output_writes_once_preserves_identical_and_refuses_any_different_bytes(self):
        with tempfile.TemporaryDirectory(prefix='offline-catalog-output-', dir=ROOT.parent) as folder:
            output = Path(folder) / 'assets'
            self.assertTrue(M['write_assets'](output, self.files))
            self.assertFalse(M['write_assets'](output, self.files))
            (output / 'README.md').write_bytes(b'preserved local work')
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            with self.assertRaises(M['PreparationFailure']): M['write_assets'](output, self.files)
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})
            unknown = dict(self.files); unknown['unknown.txt'] = b'new'
            with self.assertRaises(M['PreparationFailure']): M['write_assets'](Path(folder) / 'other', unknown)
            self.assertFalse((Path(folder) / 'other').exists())

    def test_cli_explicit_prepare_writes_only_six_source_assets_and_safe_summary(self):
        with tempfile.TemporaryDirectory(prefix='offline-catalog-cli-', dir=ROOT.parent) as folder:
            directory = Path(folder); path = directory / 'pins.json'; path.write_bytes(M['encoded'](self.pins))
            output, stdout = directory / 'assets', io.StringIO()
            with redirect_stdout(stdout): code = M['main'](['--prepare-review-assets', '--pins', str(path), '--output-dir', str(output)])
            self.assertEqual(code, 0)
            summary = json.loads(stdout.getvalue()); self.assertTrue(summary['assets_written'])
            self.assertEqual(summary['status'], 'NOT_RUN')
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, self.files)

    def test_read_errors_and_unexpected_cli_exceptions_never_export_messages(self):
        with patch.object(Path, 'read_bytes', side_effect=OSError(CANARY)):
            with self.assertRaises(M['PreparationFailure']) as result: M['load_catalog_tools'](ROOT, self.pins)
            self.assertEqual(result.exception.code, 'SOURCE_INPUT_UNREADABLE'); self.assertNotIn(CANARY, str(result.exception))
        output = io.StringIO()
        with patch.object(Path, 'read_text', side_effect=OSError(CANARY)), redirect_stdout(output):
            self.assertEqual(M['main'](['--prepare-review-assets', '--pins', 'missing']), 2)
        self.assertNotIn(CANARY, output.getvalue())


if __name__ == '__main__': unittest.main(verbosity=2)
