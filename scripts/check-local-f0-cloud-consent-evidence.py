"""Offline checks for the one-assertion Consent evidence reader."""

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import local_f0_cloud_consent_evidence as consent


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'context/reconciliation/local-f0-assertion-evidence.json'
INVENTORY = 'context/reconciliation/local-f0-assertions.json'


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf8')


class ConsentEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = consent.derive_bytes(ROOT)
        cls.record = consent.document(cls.raw)
        ledger = consent.document((ROOT / LEDGER).read_bytes())
        cls.previous = {**ledger, **{kind: [row for row in ledger[kind] if not consent.is_reference(row)]
                                     for kind in ('assertions', 'executions')}}
        cls.proposal = consent.propose_ledger_delta(encoded(cls.previous), cls.raw)
        cls.row = cls.proposal['assertions'][-1]

    def fixture(self):
        folder = tempfile.TemporaryDirectory(prefix='wa-consent-evidence-test-')
        self.addCleanup(folder.cleanup)
        root = Path(folder.name).resolve()
        audit = consent.document((ROOT / consent.ASSET / consent.AUDIT).read_bytes())
        for name in (*audit['file_sha256'], consent.AUDIT, consent.ACCEPTANCE):
            relative = f'{consent.ASSET}/{name}'
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        (root / consent.DERIVED).write_bytes(self.raw)
        return root

    def test_derives_only_selected_assertion_with_actual_scope_limit(self):
        self.assertEqual(consent.sha(self.raw), consent.DERIVED_SHA)
        self.assertEqual(len(self.record['input_files_sha256']), 43)
        self.assertEqual(self.record['database_posture'], 'D')
        [claim] = self.record['claims']
        self.assertEqual((claim['case_id'], claim['assertion_id'], claim['status']), (consent.CASE, consent.ASSERTION, 'PASS'))
        controls = claim['matched_rollback_controls']
        self.assertEqual([row['case'] for row in controls], consent.CASES)
        self.assertEqual([row['issued_grants_exact'] for row in controls], [3, 6])
        self.assertTrue(all(row['exact_consent_residue_zero'] is True and row['diagnostic']['sqlstate'] == 'P0001' for row in controls))
        self.assertIn('Per-table application fingerprints were unretained.', claim['qualification_limit'])
        self.assertEqual(self.record['native_and_ledger']['post_consent_oracle_evidence_scope'], 'INITIAL_416_REUSED_AFTER_EXACT_NATIVE_PARITY')
        inventory = consent.document((ROOT / INVENTORY).read_bytes())
        [registered] = [row for case in inventory['cases'] if case['id'] == consent.CASE
                        for row in case['assertions'] if row['id'] == consent.ASSERTION]
        self.assertEqual(claim['expected_assertion_sha256'], consent.sha(registered['expected_assertion'].encode('utf8')))

    def test_proposal_appends_one_link_and_preserves_arbitrary_existing_history(self):
        previous = copy.deepcopy(self.previous)
        previous['preserved_future_metadata'] = {'version': 2, 'nested': [True, None]}
        modified = consent.propose_ledger_delta(encoded(previous), self.raw)
        self.assertEqual({**modified, 'assertions': modified['assertions'][:-1], 'executions': modified['executions'][:-1]}, previous)
        self.assertEqual(modified['assertions'][-1], self.row)
        self.assertEqual(self.row['json_pointer'], '/claims/0')
        self.assertEqual(sum(consent.is_reference(row) for row in modified['executions']), 1)
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_APPEND_NEW_ASSERTION_AND_EXECUTION_ONLY'):
            consent.propose_ledger_delta(encoded(modified), self.raw)
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_NORMALIZED_BYTES'):
            consent.propose_ledger_delta(encoded(previous), self.raw + b' ')

    def test_both_exact_rollbacks_and_all_typed_grants_are_required(self):
        original = consent.document((ROOT / consent.ASSET / consent.CHILD).read_bytes())
        changed = copy.deepcopy(original)
        changed['results'] = changed['results'][:1]
        wrong_grant = copy.deepcopy(original)
        next(op for op in wrong_grant['operations'] if op['stage'] == 'ISSUER_RETENTION')['grants_exact'] = True
        wrong_source = copy.deepcopy(original)
        wrong_source['results'][1]['diagnostic']['source_body_line'] = 18
        for value in (changed, wrong_grant, wrong_source):
            with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_48_OPERATIONS_AND_BOTH_ROLLBACKS'):
                consent._child(value)

    def test_exact_row_and_source_cannot_be_aliased_to_vector(self):
        root = self.fixture()
        bad = copy.deepcopy(self.proposal)
        bad['assertions'][-1]['assertion_id'] = 'vector.CONSENT-EMPTY.adversarial'
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_ONE_LEDGER_ROW'):
            consent.QualificationBatch(root, bad)
        bad = copy.deepcopy(self.proposal)
        bad['executions'].append({**bad['executions'][-1], 'evidence_path': 'other.json', 'run_id': 'other-run', 'actual_result': 'OTHER_KIND'})
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_ONE_EXECUTION'):
            consent.QualificationBatch(root, bad)
        batch = consent.QualificationBatch(root, self.proposal)
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_ASSERTION_ROW_AND_POINTER'):
            batch.validate_claim(self.record, {**self.row, 'json_pointer': '/claims/00'})
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EXACT_ASSERTION_ROW_AND_POINTER'):
            batch.verify_unchanged()

    def test_final_barrier_rechecks_the_closed_raw_graph(self):
        root = self.fixture()
        batch = consent.QualificationBatch(root, self.proposal)
        self.assertTrue(batch.validate_claim(self.record, self.row))
        self.assertTrue(batch.verify_unchanged())
        batch = consent.QualificationBatch(root, self.proposal)
        self.assertTrue(batch.validate_claim(self.record, self.row))
        path = root / consent.ASSET / 'evidence/noop-consent-native-after.json'
        raw = path.read_bytes()
        path.write_bytes(raw[:-1] + b' ')
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EVIDENCE_BYTES_DRIFT'):
            batch.verify_unchanged()
        path.write_bytes(raw)
        with self.assertRaisesRegex(consent.EvidenceFailure, 'CONSENT_EVIDENCE_BYTES_DRIFT'):
            batch.verify_unchanged()


if __name__ == '__main__':
    unittest.main(verbosity=2)
