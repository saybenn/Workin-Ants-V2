"""Offline regression checks against the retained Cloud CSP evidence."""

import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import local_f0_cloud_csp9e633e3f_evidence as csp


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ledger = csp.document((ROOT / csp.LEDGER).read_bytes())
        cls.baseline = {**ledger, 'assertions': ledger['assertions'][:730], 'executions': ledger['executions'][:15]}
        cls.baseline_raw = (json.dumps(cls.baseline, indent=2, ensure_ascii=False) + '\n').encode('utf8')
        cls.raw = csp.derive_bytes(ROOT)
        cls.record = csp.document(cls.raw)
        cls.proposal = csp.propose_ledger_delta(cls.baseline_raw, cls.raw)
        cls.row = cls.proposal['assertions'][-1]

    def fixture(self):
        temp = tempfile.TemporaryDirectory(prefix='wa-csp-admission-test-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name).resolve()
        for relative in csp.RAW_PINS:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        (root / csp.DERIVED).write_bytes(self.raw)
        return root

    @staticmethod
    def get(name):
        return csp.document((ROOT / csp.ASSET / name).read_bytes())

    def validate(self, batch, root, **changes):
        values = {'case_id': csp.CASE, 'assertion_id': csp.ASSERTION, 'status': 'PASS',
                  'execution': self.record, 'root': root, 'json_pointer': '/claims/0', 'ledger_row': self.row}
        return batch.validate_claim(**{**values, **changes})

    def test_exact_raw_graph_and_one_normalized_claim(self):
        self.assertEqual(len(csp.RAW_PINS), 38)
        self.assertEqual(csp.sha(self.raw), csp.DERIVED_SHA)
        [claim] = self.record['claims']
        self.assertEqual((claim['case_id'], claim['assertion_id'], claim['status']), (csp.CASE, csp.ASSERTION, 'PASS'))
        self.assertEqual(claim['controls'], list(csp.CONTROLS))
        self.assertEqual(self.record['raw_runtime_result'], csp.RAW_PASS)
        self.assertEqual(self.record['database_posture'], 'D')
        self.assertTrue(all(value is False for value in self.record['limits'].values()))
        proof = self.record['proof']
        self.assertIs(type(proof['actual_executor_exit_code']), int)
        self.assertEqual(proof['actual_executor_exit_code'], 0)
        self.assertTrue(proof['independent_cleanup_verified'])
        self.assertEqual(proof['separately_committed_current_issuer_grants'], 4)
        self.assertTrue(proof['restricted_sh004_create_prerequisite'])
        self.assertFalse(proof['same_target_post_proof']['second_deploy'])

    def test_proposal_preserves_every_previous_row_and_execution(self):
        self.assertEqual(csp.sha(self.baseline_raw), csp.BASELINE_LEDGER)
        self.assertEqual(len(self.proposal['assertions']), 731)
        self.assertEqual(len(self.proposal['executions']), 16)
        self.assertEqual(self.proposal['assertions'][:-1], self.baseline['assertions'])
        self.assertEqual(self.proposal['executions'][:-1], self.baseline['executions'])
        self.assertEqual(self.proposal['scope'], self.baseline['scope'])
        self.assertEqual(self.row['json_pointer'], '/claims/0')
        self.assertNotIn('previous_evidence', self.row)
        self.assertEqual(sum(csp.is_reference(row) for row in self.proposal['assertions']), 1)
        self.assertEqual(sum(csp.is_reference(row) for row in self.proposal['executions']), 1)
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_EXACT_PRIOR_730_LEDGER'):
            csp.propose_ledger_delta(self.baseline_raw + b' ', self.raw)
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_EXACT_NORMALIZED_RECORD'):
            csp.propose_ledger_delta(self.baseline_raw, self.raw + b' ')

    def test_strict_json_rejects_duplicate_nonfinite_or_malformed(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e900}', b'\xff', b'[' * 50 + b']' * 50):
            with self.subTest(raw=raw), self.assertRaises(csp.EvidenceFailure):
                csp.document(raw)

    def test_child_rejects_incomplete_wrong_marker_commit_and_missing_grant(self):
        raw = self.get(csp.CHILD)
        self.assertEqual(len(raw['operations']), 82)
        for name in ('incomplete', 'wrong_sqlstate', 'committed_update', 'missing_grant', 'untyped_rows'):
            child = copy.deepcopy(raw)
            if name == 'incomplete':
                child['evidence_complete'] = False
            elif name == 'wrong_sqlstate':
                child['results'][1]['receipt']['diagnostic']['sqlstate'] = '42501'
            elif name == 'committed_update':
                next(row for row in child['operations'] if 'committed' in row)['committed'] = True
            elif name == 'missing_grant':
                child['operations'].remove(next(row for row in child['operations']
                                                if row['stage'] == 'ALL_ISSUER_GRANTS_IMMUTABLE_AND_CURRENT'))
            else:
                next(row for row in child['operations'] if row.get('rows') == 1)['rows'] = True
            with self.subTest(name=name), self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_EXACT_CHILD_ROLLBACK_TRANSCRIPT'):
                csp._child(child)

    def test_exact_executor_exit_and_post_cleanup_observations_are_required(self):
        parent, audit, plan = (self.get(name) for name in (csp.PARENT, 'independent-closure.json', 'operation-plan.json'))
        def wrong_exit(name):
            value = self.get(name)
            if name == 'operation-exit.json':
                value['exit_code'] = False
            return value
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_OBSERVED_PROCESS_EXIT'):
            csp._source(wrong_exit, parent, audit)
        audit['cleanup_verified']['volume_name_absent'] = False
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_INDEPENDENT_CLEANUP'):
            csp._parent(parent, plan, audit)
        parent['customer_stale']['post_proof']['second_deploy'] = True
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_ONE_READ_ONLY_POST_PROOF_NO_SECOND_INSTALL'):
            csp._post_proof(self.get, parent)

    def test_batch_binds_exact_row_execution_and_pointer_then_finalizes(self):
        root = self.fixture()
        batch = csp.prepare_batch(root, self.proposal)
        self.assertTrue(self.validate(batch, root))
        self.assertTrue(batch.verify_unchanged())
        self.assertTrue(batch.require_finalized())

    def test_batch_requires_exactly_one_link_and_execution(self):
        root = self.fixture()
        for key in ('assertions', 'executions'):
            for count in (0, 2):
                ledger = copy.deepcopy(self.proposal)
                original = ledger[key].pop()
                ledger[key].extend([original] * count)
                with self.subTest(key=key, count=count), self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_EXACT_ONE_'):
                    csp.prepare_batch(root, ledger)
        for changed_binding in ('actual_result', 'evidence_sha256'):
            ledger = copy.deepcopy(self.proposal)
            alternate = {**ledger['executions'][-1], 'run_id': 'other-run', 'evidence_path': 'other-evidence.json',
                         changed_binding: 'other-value'}
            ledger['executions'].append(alternate)
            with self.subTest(changed_binding=changed_binding), self.assertRaisesRegex(csp.EvidenceFailure,
                                                                                     'CSP_EXACT_ONE_EXECUTION_ENTRY'):
                csp.prepare_batch(root, ledger)

    def test_claim_rejections_are_sticky_and_exact_one_use(self):
        root = self.fixture()
        for changes in ({'json_pointer': '/claims/00'}, {'case_id': 'P0C-PRIV-01'}, {'status': 'PARTIAL'},
                        {'assertion_id': 'control.concurrent_customer_update'},
                        {'execution': {**self.record, 'claims': []}},
                        {'ledger_row': {**self.row, 'previous_evidence': {}}}):
            batch = csp.prepare_batch(root, self.proposal)
            with self.subTest(keys=changes.keys()), self.assertRaises(csp.EvidenceFailure) as failure:
                self.validate(batch, root, **changes)
            for later in (lambda: self.validate(batch, root), batch.verify_unchanged, batch.require_finalized):
                with self.assertRaises(csp.EvidenceFailure) as repeated:
                    later()
                self.assertEqual(str(repeated.exception), str(failure.exception))
        batch = csp.prepare_batch(root, self.proposal)
        self.assertTrue(self.validate(batch, root))
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_BATCH_ALREADY_USED'):
            self.validate(batch, root)

    def test_final_barrier_reads_all_bytes_again(self):
        root = self.fixture()
        batch = csp.prepare_batch(root, self.proposal)
        self.assertTrue(self.validate(batch, root))
        path = root / csp.ASSET / 'evidence/post-native-after-oracle.json'
        original = path.read_bytes()
        path.write_bytes(original[:-1] + b' ')
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_INPUT_SHA256'):
            batch.verify_unchanged()
        path.write_bytes(original)
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_INPUT_SHA256'):
            batch.require_finalized()

    def test_requires_final_barrier_and_rejects_linked_input(self):
        root = self.fixture()
        batch = csp.prepare_batch(root, self.proposal)
        self.assertTrue(self.validate(batch, root))
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_FINAL_FRESH_INPUT_BARRIER_REQUIRED'):
            batch.require_finalized()
        path = root / csp.ASSET / 'operation-exit.json'
        shadow = path.with_suffix('.shadow')
        os.link(path, shadow)
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_REGULAR_SINGLE_LINK_SIZE'):
            csp.prepare_batch(root, self.proposal)
        path.unlink()
        try:
            path.symlink_to(shadow)
        except OSError:
            self.skipTest('The operating system does not permit test symlinks.')
        with self.assertRaisesRegex(csp.EvidenceFailure, 'CSP_INPUT_PATH'):
            csp.prepare_batch(root, self.proposal)


if __name__ == '__main__':
    unittest.main(verbosity=2)
