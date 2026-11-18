"""Offline mutations over the independently audited, retained actual 23bd run.

No Docker/database/Prisma/Git/network process is invoked. Positive inputs are
copied from the exact real record, rather than generated from parser constants.
Only an exclusively created temporary fixture tree is written or removed.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('catalog_evidence', ROOT / 'scripts/local_f0_catalog_evidence.py')
API = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API)
RECORD = ROOT / 'context/reconciliation/local-f0-catalog-b9703d7-23bd8979-execution.json'
RECORD_SHA = 'bbf604e3eb2c7a066f2287a2f2f2ab825582d366dc5330394170b33a0fd22de8'
CANARY = 'postgresql://secret_canary_password@unknown.invalid/private'


class CatalogEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RECORD.read_bytes()
        if hashlib.sha256(raw).hexdigest() != RECORD_SHA:
            raise AssertionError('Reviewed actual fixture bytes changed')
        cls.execution = json.loads(raw)
        cls.temp = tempfile.TemporaryDirectory(prefix='wa-offline-catalog-evidence-')
        cls.root = Path(cls.temp.name).resolve()
        cls.temp_parent = Path(tempfile.gettempdir()).resolve()
        if cls.root.parent != cls.temp_parent or not cls.root.name.startswith('wa-offline-catalog-evidence-'):
            raise AssertionError('Temporary fixture boundary changed')
        manifest = cls.execution['sanitized_report']['run_manifest']
        paths = set(manifest['packet_files_sha256']) | set(cls.execution['snapshot_files_sha256']) | set(API.TOOL_PACKAGES)
        paths.add('context/reconciliation/local-f0-assertions.json')
        for relative in paths:
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())

    @classmethod
    def tearDownClass(cls):
        if cls.root.parent != cls.temp_parent or not cls.root.name.startswith('wa-offline-catalog-evidence-'):
            raise AssertionError('Refusing cleanup outside exclusive fixture directory')
        cls.temp.cleanup()

    def validate(self, execution=None, case='P0C-CATALOG-01', assertion='control.visibility', status='PASS'):
        return API.validate_claim(case, assertion, status, self.execution if execution is None else execution, self.root)

    def rejects(self, change, code):
        execution = copy.deepcopy(self.execution)
        change(execution)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            with self.assertRaises(API.EvidenceFailure) as caught:
                self.validate(execution)
        self.assertEqual(str(caught.exception), code)
        self.assertNotIn(CANARY, str(caught.exception))
        self.assertEqual(output.getvalue(), '')

    def test_actual_fourteen_assertions_only_without_process_or_network(self):
        expected = {('P0C-CATALOG-01', 'control.' + name): 'PASS' for name in ('relations_columns', 'enums', 'constraints', 'indexes', 'functions', 'triggers', 'views', 'roles_memberships', 'all_acl_levels', 'rls_policies', 'extensions', 'visibility')}
        expected[('P0C-CATALOG-01', 'vector.CATALOG-LEAVES.positive')] = 'PASS'
        expected[('P0C-INSTALL-01', 'control.private_ledger')] = 'PASS'
        self.assertEqual(API.CLAIMS, expected)
        before = copy.deepcopy(self.execution)
        with patch.object(subprocess, 'Popen', side_effect=AssertionError('PROCESS_FORBIDDEN')) as proc, patch.object(socket, 'socket', side_effect=AssertionError('NETWORK_FORBIDDEN')) as network, patch.object(os, 'system', side_effect=AssertionError('SHELL_FORBIDDEN')) as shell:
            for (case, assertion), status in expected.items():
                with self.subTest(case=case, assertion=assertion):
                    self.assertTrue(self.validate(case=case, assertion=assertion, status=status))
            proc.assert_not_called(); network.assert_not_called(); shell.assert_not_called()
        self.assertEqual(self.execution, before)
        self.assertEqual(self.execution['limits']['independent_actual_evidence_review'], 'PENDING')

    def test_adversarial_whole_case_and_other_install_claims_reject_before_read(self):
        claims = [('P0C-CATALOG-01', 'vector.CATALOG-LEAVES.adversarial'), ('P0C-CATALOG-01', 'PASS'), ('P0C-INSTALL-01', 'control.empty_deploy'), ('P0C-INSTALL-01', 'control.second_deploy'), ('P0C-INSTALL-01', 'vector.INSTALL-CLEANUP.positive'), ('P0C-INSTALL-02', 'control.failed_ledger')]
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('UNSUPPORTED_CLAIM_READ')):
            for case, assertion in claims:
                with self.subTest(case=case, assertion=assertion), self.assertRaisesRegex(API.EvidenceFailure, '^CATALOG_CLAIM_NOT_SUPPORTED$'):
                    self.validate(case=case, assertion=assertion)
        for status in ('PARTIAL', 'FAILED', 'NOT_RUN', True, None):
            with self.subTest(status=status), self.assertRaises(API.EvidenceFailure):
                self.validate(status=status)

    def test_forged_pass_label_and_old_execution_kind_are_insufficient(self):
        for value in ({'actual_result': API.RESULT}, {'actual_result': 'PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY'}, [], None):
            with self.subTest(kind=type(value).__name__), self.assertRaises(API.EvidenceFailure):
                API.validate_claim('P0C-CATALOG-01', 'control.visibility', 'PASS', value, self.root)

    def test_unknown_fields_and_secret_payloads_are_not_retained_or_echoed(self):
        self.rejects(lambda d: d.update(error_body=CANARY), 'CATALOG_RECORD_FIELDS')
        self.rejects(lambda d: d.update(unexpected=[CANARY]), 'CATALOG_UNEXPECTED')
        self.rejects(lambda d: d['sanitized_report'].update(arbitrary_stderr=CANARY), 'CATALOG_RETAINED_REPORT_HASH')

    def test_exact_commit_tree_packet_run_and_sql(self):
        for key in ('run_id', 'source_commit', 'source_tree', 'packet_sha256', 'application_sql_sha256'):
            with self.subTest(key=key):
                self.rejects(lambda d, k=key: d.update({k: '0' * 64}), 'CATALOG_SOURCE_IDENTITY')
        self.rejects(lambda d: d['sanitized_report'].update(approved_commit='0' * 40), 'CATALOG_REPORT_IDENTITY')

    def test_all_twelve_pipeline_steps_and_no_unexpected_outcome(self):
        for key in API.STEPS:
            with self.subTest(key=key):
                self.rejects(lambda d, k=key: d['sanitized_report']['steps'].update({k: 'NOT_RUN'}), 'CATALOG_STEPS')
        self.rejects(lambda d: d['sanitized_report'].update(unexpected=[{'code': CANARY}]), 'CATALOG_UNEXPECTED')
        self.rejects(lambda d: d['actual_steps'].update({'CATALOG-COMPARE': True}), 'CATALOG_STEPS')

    def test_scope_and_typed_source_counts(self):
        self.rejects(lambda d: d['sanitized_report']['limits'].update(posture='A'), 'CATALOG_SCOPE_HOLD')
        self.rejects(lambda d: d['sanitized_report']['limits'].update(hosted_changes=0), 'CATALOG_SCOPE_HOLD')
        for value in (77, 79, 78.0, True):
            with self.subTest(value=value):
                self.rejects(lambda d, v=value: d['sanitized_report']['source_verification'].update(file_count=v), 'CATALOG_SOURCE_VERIFICATION')
        self.rejects(lambda d: d['sanitized_report'].update(packet_unchanged_after_run=False), 'CATALOG_SOURCE_PRESERVATION')
        self.rejects(lambda d: d['sanitized_report'].update(tool_source_data_unchanged_after_run=False), 'CATALOG_SOURCE_PRESERVATION')

    def test_source_asset_and_junction_package_drift_reject(self):
        original = Path.read_bytes
        cases = [('review-output/foundation-application.review.sql', 'CATALOG_EVIDENCE_FILE_HASH'), (API.ASSETS + '/native-before.json', 'CATALOG_EVIDENCE_FILE_HASH'), ('node_modules/prisma/package.json', 'CATALOG_TOOL_PACKAGE_HASH')]
        for relative, code in cases:
            target = self.root / relative
            def changed(path, *args, **kwargs):
                raw = original(path, *args, **kwargs)
                return raw + b'\nSECRET_CANARY\n' if path == target else raw
            with self.subTest(relative=relative), patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(API.EvidenceFailure, '^' + code + '$'):
                self.validate()

    def test_changed_assertion_requirement_cannot_reuse_evidence(self):
        original = Path.read_bytes
        target = self.root / 'context/reconciliation/local-f0-assertions.json'
        def changed(path, *args, **kwargs):
            raw = original(path, *args, **kwargs)
            if path == target:
                value = json.loads(raw)
                next(a for c in value['cases'] if c['id'] == 'P0C-CATALOG-01' for a in c['assertions'] if a['id'] == 'control.visibility')['expected_assertion'] += CANARY
                return json.dumps(value).encode()
            return raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(API.EvidenceFailure, '^CATALOG_ASSERTION_REQUIREMENT$'):
            self.validate()

    def test_no_traversal_or_forged_snapshot_hash_map(self):
        self.rejects(lambda d: d['snapshot_files_sha256'].update({'../SECRET_CANARY': '0' * 64}), 'CATALOG_SNAPSHOT_BINDING')
        for relative in ('../SECRET_CANARY', '/SECRET_CANARY', 'C:/SECRET_CANARY', 'a\\SECRET_CANARY'):
            with self.subTest(relative=relative), self.assertRaisesRegex(API.EvidenceFailure, '^CATALOG_EVIDENCE_PATH$'):
                API._read(self.root, relative, '0' * 64)

    def test_all_three_exact_native_snapshots_are_required(self):
        self.rejects(lambda d: d['identical_native_snapshot_files_sha256'].pop('native-after-oracle.json'), 'CATALOG_NATIVE_PRESERVATION')
        self.rejects(lambda d: d['sanitized_report']['native_snapshots'][2].update(native_sha256='0' * 64), 'CATALOG_NATIVE_PRESERVATION')
        self.rejects(lambda d: d['sanitized_report'].update(qualified_native_snapshot_sha256='0' * 64), 'CATALOG_NATIVE_IDENTITY')

    def test_comparator_pass_counts_cannot_override_failures_or_unknowns(self):
        for change in (lambda c: c.update(status='INCOMPLETE'), lambda c: c.update(findings=[{'raw': CANARY}]), lambda c: c.update(check_counts={'PASS': 29090}), lambda c: c.update(native_snapshot_sha256='0' * 64)):
            self.rejects(lambda d, fn=change: fn(d['sanitized_report']['catalog_comparison']), 'CATALOG_COMPARATOR_BINDING')

    def test_private_ledger_requires_complete_hash_bound_proof(self):
        self.rejects(lambda d: d['sanitized_report']['ledger_comparison']['checks'].pop(), 'CATALOG_LEDGER_PROOF')
        self.rejects(lambda d: d['sanitized_report']['ledger_comparison']['checks'][0].update(status='INCOMPLETE'), 'CATALOG_LEDGER_PROOF')
        self.rejects(lambda d: d['sanitized_report']['ledger_comparison']['checks'][-1].update(actual_sha256='0' * 64), 'CATALOG_LEDGER_PROOF')

    def test_install_finalization_and_every_backend_closure(self):
        self.rejects(lambda d: d['sanitized_report']['migration_operations'][0].update(exit_code=False), 'CATALOG_INSTALLATION_BINDING')
        self.rejects(lambda d: d['sanitized_report']['migration_operations'].append({}), 'CATALOG_OPERATION_SET')
        self.rejects(lambda d: d['sanitized_report']['targets'][API.TARGET]['finalization_observation'].update(remaining_memberships=1), 'CATALOG_FINALIZATION')
        for i in range(7):
            with self.subTest(index=i):
                self.rejects(lambda d, n=i: d['sanitized_report']['backend_closures'][n].update(tagged_clients_zero=False), 'CATALOG_BACKEND_CLOSURE')
        self.rejects(lambda d: d['sanitized_report']['catalog_operations'][0].update(client_exited=1), 'CATALOG_QUERY_CLOSURE')

    def test_cleanup_resource_identity_absence_and_secret_scan(self):
        self.rejects(lambda d: d['sanitized_report']['cleanup'][API.TARGET].update(verified_id='0' * 64), 'CATALOG_CLEANUP_IDENTITY')
        self.rejects(lambda d: d['sanitized_report']['cleanup_summary']['resource_presence_after'].update({API.TARGET: True}), 'CATALOG_CLEANUP_ABSENCE')
        self.rejects(lambda d: d['sanitized_report']['host_secret_cleanup'].update(private_directory_absent=False), 'CATALOG_SECRET_CLEANUP')
        self.rejects(lambda d: d['sanitized_report']['sanitization'].update(actual_password_values_found=True), 'CATALOG_SANITIZATION')

    def test_unmodeled_record_and_report_changes_still_reject(self):
        self.rejects(lambda d: d.update(historical_distinction=CANARY), 'CATALOG_RETAINED_EXECUTION_HASH')
        self.rejects(lambda d: d['sanitized_report']['image'].update(removed=True), 'CATALOG_RETAINED_REPORT_HASH')

    def test_missing_files_and_malformed_input_use_fixed_secret_free_errors(self):
        target = self.root / (API.ASSETS + '/ledger-evidence.json')
        original = Path.read_bytes
        def missing(path, *args, **kwargs):
            if path == target:
                raise OSError(CANARY)
            return original(path, *args, **kwargs)
        output = io.StringIO()
        with patch.object(Path, 'read_bytes', missing), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output), self.assertRaisesRegex(API.EvidenceFailure, '^CATALOG_EVIDENCE_REJECTED$') as caught:
            self.validate()
        self.assertEqual(output.getvalue(), '')
        self.assertNotIn(CANARY, str(caught.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
