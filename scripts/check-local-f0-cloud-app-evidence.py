"""Regression coverage for the exact two-row Cloud App admission."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import local_f0_cloud_app_evidence as app


ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'context/reconciliation/local-f0-assertion-evidence.json'


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in app.PINS:
            source = Path(app.ASSET) / name
            leaf = self.root / source
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_bytes((ROOT / source).read_bytes())
        self.derived = app.derive_bytes(self.root)
        (self.root / app.DERIVED).write_bytes(self.derived)
        self.rows, self.execution = app.links()
        self.ledger = {'assertions': copy.deepcopy(self.rows), 'executions': [copy.deepcopy(self.execution)]}

    def test_closed_record_contains_only_the_reviewed_claims(self):
        self.assertEqual(app.sha(self.derived), app.DERIVED_SHA)
        claims = json.loads(self.derived)['claims']
        self.assertEqual([row['observation']['case'] for row in claims],
                         ['genuine-sh004-effect-insert', 'pending-work-next-attempt-update'])
        batch = app.QualificationBatch(self.root, self.ledger)
        for row in self.rows:
            batch.validate_claim(json.loads(self.derived), row)
        batch.verify_unchanged()

    def test_unrecognized_or_extra_row_rejects(self):
        self.ledger['assertions'].append({**self.rows[0], 'evidence_path': 'other.json'})
        with self.assertRaisesRegex(app.EvidenceFailure, 'exactly two rows'):
            app.QualificationBatch(self.root, self.ledger)

    def test_wrong_pointer_and_missing_claim_reject(self):
        batch = app.QualificationBatch(self.root, self.ledger)
        with self.assertRaisesRegex(app.EvidenceFailure, 'reference mismatch'):
            batch.validate_claim(json.loads(self.derived), {**self.rows[0], 'json_pointer': '/claims/1'})
        batch.validate_claim(json.loads(self.derived), self.rows[0])
        with self.assertRaisesRegex(app.EvidenceFailure, 'claims or closed evidence changed'):
            batch.verify_unchanged()

    def test_replaced_child_rejects(self):
        child = self.root / app.ASSET / app.CHILD
        child.write_bytes(child.read_bytes() + b'\n')
        with self.assertRaisesRegex(app.EvidenceFailure, 'digest mismatch'):
            app.QualificationBatch(self.root, self.ledger)

    def test_candidate_preserves_all_old_rows(self):
        raw = (ROOT / LEDGER).read_bytes()
        previous = json.loads(raw)
        if app.sha(raw) != app.BASELINE_LEDGER:
            # Retain the published prefix that preceded this App admission.
            previous['assertions'] = previous['assertions'][:731]
            previous['executions'] = previous['executions'][:16]
            raw = (json.dumps(previous, indent=2, ensure_ascii=False) + '\n').encode('utf8')
        result = app.propose_ledger_delta(raw, self.derived)
        self.assertEqual(result['assertions'], previous['assertions'] + self.rows)
        self.assertEqual(result['executions'], previous['executions'] + [self.execution])


if __name__ == '__main__':
    unittest.main(verbosity=2)
