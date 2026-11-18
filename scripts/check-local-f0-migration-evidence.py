"""Offline regression checks over the retained actual 196c evidence.

No SQL, Docker, Git, Prisma or network is invoked. Filesystem mutations affect
only a newly created temporary copy of the evidence inputs, never the repository.
The positive oracle is the independently reviewed actual record, not a synthetic
record generated from the validator's expected values.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('migration_evidence', ROOT / 'scripts/local_f0_migration_evidence.py')
API = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(API)
RECORD = ROOT / 'context/reconciliation/local-f0-migration-6b8910d-execution.json'
RECORD_SHA = 'e657bd4de3c288acbd86faa7ae9514f59e76566e1bba170a6ef19f7770c91158'
CANARY = 'postgresql://secret_canary_password@unknown.invalid/private'


class MigrationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = RECORD.read_bytes()
        if hashlib.sha256(raw).hexdigest() != RECORD_SHA:
            raise AssertionError('Reviewed positive fixture bytes changed')
        cls.execution = json.loads(raw)
        cls.temp = tempfile.TemporaryDirectory(prefix='wa-offline-evidence-')
        cls.root = Path(cls.temp.name).resolve()
        sources = cls.execution['operator_raw_safe_report']['source_verification']['files_sha256']
        paths = list(sources) + [API.ASSETS + '/' + name for name in cls.execution['snapshot_files_sha256']]
        for relative in paths:
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def validate(self, execution=None, case='P0C-INSTALL-01', assertion='control.empty_deploy', status='PASS'):
        return API.validate_claim(case, assertion, status, execution if execution is not None else self.execution, self.root)

    def rejects(self, change, code, *, status='PASS', assertion='control.empty_deploy'):
        value = copy.deepcopy(self.execution)
        change(value)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            with self.assertRaises(API.EvidenceFailure) as caught:
                self.validate(value, assertion=assertion, status=status)
        self.assertEqual(str(caught.exception), code)
        self.assertEqual(out.getvalue(), '')
        self.assertNotIn(CANARY, str(caught.exception))

    def test_actual_five_pass_and_three_partial_only(self):
        expected = {
            ('P0C-INSTALL-01', 'control.empty_deploy'): 'PASS',
            ('P0C-INSTALL-01', 'control.second_deploy'): 'PASS',
            ('P0C-INSTALL-02', 'control.failed_ledger'): 'PASS',
            ('P0C-INSTALL-02', 'control.recovery'): 'PASS',
            ('P0C-INSTALL-02', 'control.immutable_applied_history'): 'PASS',
            ('P0C-INSTALL-01', 'control.private_ledger'): 'PARTIAL',
            ('P0C-INSTALL-01', 'vector.INSTALL-CLEANUP.positive'): 'PARTIAL',
            ('P0C-INSTALL-02', 'control.intended_failure'): 'PARTIAL',
        }
        self.assertEqual(API.CLAIMS, expected)
        with patch('subprocess.run', side_effect=AssertionError('No processes allowed')):
            for (case, assertion), status in expected.items():
                with self.subTest(case=case, assertion=assertion):
                    self.assertIs(self.validate(case=case, assertion=assertion, status=status), True)

    def test_partial_cannot_be_promoted_and_unrun_cases_cannot_borrow_run(self):
        cases = [('P0C-INSTALL-01', 'control.private_ledger'), ('P0C-INSTALL-01', 'vector.INSTALL-CLEANUP.positive'), ('P0C-INSTALL-02', 'control.intended_failure'), ('P0C-INSTALL-01', 'vector.INSTALL-CLEANUP.adversarial'), ('P0C-INSTALL-01', 'vector.FUNCTION-ACL-AUTHORITY.adversarial'), ('P0C-INSTALL-02', 'vector.FUNCTION-ACL-FAILURE-CLEANUP.adversarial'), ('P0C-CUSTOMER-01', 'control.empty_deploy'), ('P0C-INSTALL-01', 'control.CAS'), ('P0C-INSTALL-01', 'control.success_cleanup')]
        for case, assertion in cases:
            with self.subTest(case=case, assertion=assertion):
                with self.assertRaisesRegex(API.EvidenceFailure, '^MIGRATION_CLAIM_NOT_SUPPORTED$'):
                    self.validate(case=case, assertion=assertion)
        for status in ('PARTIAL', 'FAILED', 'NOT_RUN', True, None):
            with self.subTest(status=status):
                with self.assertRaises(API.EvidenceFailure):
                    self.validate(status=status)

    def test_partial_requires_actual_structured_evidence(self):
        for value in ({'actual_result': API.RESULT}, {'actual_result': API.RESULT, 'error_body': CANARY}, [], None):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(API.EvidenceFailure):
                    API.validate_claim('P0C-INSTALL-01', 'control.private_ledger', 'PARTIAL', value, self.root)

    def test_record_kind_scope_and_unknown_body_fail_closed(self):
        self.rejects(lambda d: d.update(actual_result='PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY'), 'MIGRATION_RECORD_KIND')
        self.rejects(lambda d: d.update(posture='A'), 'MIGRATION_RECORD_SCOPE')
        self.rejects(lambda d: d.update(error_body=CANARY), 'MIGRATION_RECORD_FIELDS')
        self.rejects(lambda d: d.update(unexpected=[CANARY]), 'MIGRATION_UNEXPECTED')

    def test_exact_source_and_run_identity(self):
        for key in ('run_id', 'source_commit', 'source_tree', 'packet_sha256'):
            with self.subTest(key=key):
                self.rejects(lambda d, k=key: d.update({k: CANARY}), 'MIGRATION_IDENTITY')
        self.rejects(lambda d: d.update(application_sql_sha256='0' * 64), 'MIGRATION_SQL_IDENTITY')

    def test_source_report_requires_exact45_and_typed_count(self):
        for value in (44, 46, 45.0, True):
            with self.subTest(value=value):
                self.rejects(lambda d, v=value: d['operator_raw_safe_report']['source_verification'].update(file_count=v), 'MIGRATION_SOURCE_VERIFICATION')
        self.rejects(lambda d: d['operator_raw_safe_report']['source_verification']['files_sha256'].pop('scripts/check-trigger-row-shapes.py'), 'MIGRATION_SOURCE_VERIFICATION')
        self.rejects(lambda d: d['operator_raw_safe_report'].update(packet_unchanged_after_run=False), 'MIGRATION_SOURCE_PRESERVATION')

    def test_all_pipeline_steps_are_required(self):
        self.rejects(lambda d: d['actual_steps'].update({'MIGRATE-RETRY': 'NOT_RUN'}), 'MIGRATION_STEPS')
        self.rejects(lambda d: d['operator_raw_safe_report']['steps'].update({'MIGRATE-RESOLVE': True}), 'MIGRATION_STEPS')

    def test_all_six_cli_operations_and_closed_exit_status(self):
        report = 'operator_raw_safe_report'
        self.rejects(lambda d: d[report]['migration_operations'].pop(), 'MIGRATION_OPERATION_SET')
        for index in (0, 1, 3, 4, 5):
            with self.subTest(index=index):
                self.rejects(lambda d, i=index: d[report]['migration_operations'][i].update(status='CLI_OUTPUT_REJECTED_STOP_AND_INSPECT'), 'MIGRATION_OPERATION_STATUS')
                self.rejects(lambda d, i=index: d[report]['migration_operations'][i].update(exit_code=False), 'MIGRATION_OPERATION_CLOSURE')
        self.rejects(lambda d: d[report]['migration_operations'][2].update(exit_code=0), 'MIGRATION_OPERATION_CLOSURE')

    def test_cli_identity_no_pending_and_no_invented_p3018(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][1].update(no_pending_message_observed=False), 'MIGRATION_NOOP_MESSAGE')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][4].update(source_sql_sha256='0' * 64), 'MIGRATION_OPERATION_IDENTITY')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][2].update(prisma_codes=['P3018']), 'MIGRATION_OPERATION_IDENTITY')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][2].update(error_body=CANARY), 'MIGRATION_OPERATION_FIELDS')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][0]['diagnostic_format'].update(text_valid=1), 'MIGRATION_CLI_FORMAT')

    def test_empty_baseline_is_real_and_typed(self):
        for value in (1, False, '0'):
            with self.subTest(value=value):
                self.rejects(lambda d, v=value: d['operator_raw_safe_report']['targets'][API.OK]['baseline'].update(application_relations=v), 'MIGRATION_EMPTY_BASELINE')

    def test_failed_ledger_is_one_unfinished_row_and_all_object_kinds_zero(self):
        def failed(d):
            return d['operator_raw_safe_report']['targets'][API.FAIL]['ledger_observations'][0]
        for key in ('application_relations', 'application_functions', 'application_types', 'application_enums', 'application_tables', 'active_migrators'):
            with self.subTest(key=key):
                self.rejects(lambda d, k=key: failed(d).update({k: 1}), 'MIGRATION_LEDGER_STATE')
        self.rejects(lambda d: failed(d).update(application_types=False), 'MIGRATION_LEDGER_STATE')
        self.rejects(lambda d: failed(d)['rows'].append(copy.deepcopy(failed(d)['rows'][0])), 'MIGRATION_LEDGER_STATE')
        for key, value in [('finished', True), ('rolled_back', True), ('steps', False), ('checksum', '0' * 64), ('logs_state', 'NONEMPTY')]:
            with self.subTest(key=key):
                self.rejects(lambda d, k=key, v=value: failed(d)['rows'][0].update({k: v}), 'MIGRATION_LEDGER_STATE')

    def test_recovery_retains_failure_and_requires_same_checksum_noop(self):
        for index, change in [(1, lambda x: x['rows'][0].update(finished=True)), (2, lambda x: x['rows'].pop(0)), (2, lambda x: x['rows'][1].update(checksum='0' * 64)), (3, lambda x: x['rows'][0].update(rolled_back=False))]:
            with self.subTest(index=index):
                self.rejects(lambda d, i=index, fn=change: fn(d['operator_raw_safe_report']['targets'][API.FAIL]['ledger_observations'][i]), 'MIGRATION_LEDGER_STATE')

    def test_schema_fingerprints_and_safe_projection_must_match(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'][API.OK]['second_deploy_schema_comparison']['second'].update(sha256='0' * 64), 'MIGRATION_SCHEMA_NOOP')
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'][API.FAIL]['second_deploy_schema_comparison'].update(identical=1), 'MIGRATION_SCHEMA_NOOP')

    def test_original_grantor_and_backend_privilege_finalization(self):
        for name in (API.OK, API.FAIL):
            with self.subTest(name=name):
                self.rejects(lambda d, n=name: d['operator_raw_safe_report']['targets'][n]['connections_before_finalization'].update(migrator=1), 'MIGRATION_BACKEND_CLOSURE')
                self.rejects(lambda d, n=name: d['operator_raw_safe_report']['targets'][n]['finalization_observation'].update(grantor='wa_migrator'), 'MIGRATION_FINALIZATION')
                self.rejects(lambda d, n=name: d['operator_raw_safe_report']['targets'][n]['finalization_observation']['leaf_create'].update(wa_customer_verifier=True), 'MIGRATION_FINALIZATION')
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'][API.FAIL]['intentional_setup_fault'].update(remaining_two=True), 'MIGRATION_FAULT_BOUNDARY')

    def test_actual_server_proof_is_rebuilt_instead_of_trusting_pass(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'][API.FAIL]['server_error_observations'][1]['counts'].update(expected_set_role_42501=0), 'MIGRATION_EVIDENCE_REJECTED')
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'][API.FAIL]['failure_diagnostic_proof'].update(container_id='0' * 64), 'MIGRATION_SERVER_PROOF_BINDING')
        self.rejects(lambda d: d['actual_failure_diagnostic'].update(retained_P3018_claimed=True), 'MIGRATION_FAILURE_SCOPE')

    def test_exact_recovery_approval_cannot_be_reused_or_self_asserted(self):
        self.rejects(lambda d: d['recovery_review'].update(run_id='0' * 36), 'MIGRATION_RECOVERY_APPROVAL')
        self.rejects(lambda d: d['operator_raw_safe_report']['recovery_review'].update(proof_sha256='0' * 64), 'MIGRATION_RECOVERY_APPROVAL')

    def test_sql_process_closure_and_independent_review_order(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['events'][20].update(client_exited=1), 'MIGRATION_SQL_OPERATION_CLOSURE')
        self.rejects(lambda d: d['operator_raw_safe_report']['events'][35].update(status='PASS'), 'MIGRATION_REVIEW_HOLD')
        def swap(d):
            events = d['operator_raw_safe_report']['events']
            events[35], events[37] = events[37], events[35]
        self.rejects(swap, 'MIGRATION_RECOVERY_SEQUENCE')

    def test_exact_cleanup_identity_secret_deletion_and_independent_absence(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['cleanup'][API.FAIL].update(verified_id='0' * 64), 'MIGRATION_CLEANUP_IDENTITY')
        self.rejects(lambda d: d['operator_raw_safe_report']['cleanup_summary']['resource_presence_after'].update({API.OK: True}), 'MIGRATION_RESOURCE_ABSENCE')
        self.rejects(lambda d: d['independent_absence']['resource_presence'].update({API.FAIL: 0}), 'MIGRATION_INDEPENDENT_ABSENCE')
        self.rejects(lambda d: d['independent_absence'].update(host_private_absent=False), 'MIGRATION_SECRET_CLEANUP')
        self.rejects(lambda d: d['operator_raw_safe_report']['sanitization'].update(actual_password_values_found=CANARY), 'MIGRATION_SANITIZATION')

    def test_retained_raw_report_prevents_unreviewed_metadata_or_body(self):
        self.rejects(lambda d: d['operator_raw_safe_report'].update(error_body=CANARY), 'MIGRATION_RETAINED_REPORT_HASH')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][0].update(attestation_sha256='0' * 64), 'MIGRATION_RETAINED_REPORT_HASH')
        self.rejects(lambda d: d.update(limits=[CANARY]), 'MIGRATION_RETAINED_EXECUTION_HASH')
        self.rejects(lambda d: d.update(historical_distinction='Old0c cause now known'), 'MIGRATION_RETAINED_EXECUTION_HASH')

    def test_current_source_bytes_are_required_even_with_passed_record(self):
        relative = 'review-output/foundation-application.review.sql'
        path = self.root / relative
        raw = path.read_bytes()
        try:
            path.write_bytes(raw + b'\n-- drift')
            with self.assertRaisesRegex(API.EvidenceFailure, '^MIGRATION_EVIDENCE_FILE_HASH$'):
                self.validate()
        finally:
            path.write_bytes(raw)

    def test_changed_helper_is_rejected_before_any_import_or_output(self):
        path = self.root / API.DIAGNOSTICS
        raw = path.read_bytes()
        out = io.StringIO()
        try:
            path.write_text('print(' + repr(CANARY) + ')\nraise SystemExit(' + repr(CANARY) + ')\n', encoding='utf8')
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out), patch.object(API, '_load_diagnostics', side_effect=AssertionError('Should not load')) as loader:
                with self.assertRaisesRegex(API.EvidenceFailure, '^MIGRATION_EVIDENCE_FILE_HASH$'):
                    self.validate()
                loader.assert_not_called()
            self.assertEqual(out.getvalue(), '')
        finally:
            path.write_bytes(raw)

    def test_artifact_hashes_cannot_be_redeclared_by_evidence(self):
        self.rejects(lambda d: d['snapshot_files_sha256'].update({'server-error-proof.json': '0' * 64}), 'MIGRATION_SNAPSHOT_BINDING')
        self.rejects(lambda d: d['external_json_artifacts_sha256'].update({'run-evidence.json': '0' * 64}), 'MIGRATION_EXTERNAL_ARTIFACT_BINDING')
        path = self.root / API.ASSETS / 'operator-snapshot.py.txt'
        raw = path.read_bytes()
        try:
            path.write_text('print(' + repr(CANARY) + ')', encoding='utf8')
            with self.assertRaisesRegex(API.EvidenceFailure, '^MIGRATION_EVIDENCE_FILE_HASH$'):
                self.validate()
        finally:
            path.write_bytes(raw)

    def test_missing_files_and_nonjson_values_have_fixed_errors(self):
        self.rejects(lambda d: d['operator_raw_safe_report']['targets'].update({API.OK: None}), 'MIGRATION_EVIDENCE_REJECTED')
        self.rejects(lambda d: d['operator_raw_safe_report']['migration_operations'][0].update(exit_code=float('nan')), 'MIGRATION_EVIDENCE_REJECTED')
        with tempfile.TemporaryDirectory(prefix='wa-empty-evidence-') as root:
            with self.assertRaisesRegex(API.EvidenceFailure, '^MIGRATION_EVIDENCE_REJECTED$'):
                API.validate_claim('P0C-INSTALL-01', 'control.empty_deploy', 'PASS', self.execution, root)


if __name__ == '__main__':
    unittest.main()
