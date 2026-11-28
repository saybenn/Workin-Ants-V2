"""Check the corrected templates through the original source-pinned grant validator."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import re
import unittest
import uuid


CONTEXT = 'scripts/sql-review/run-context-control-rehearsal.py'
CONTEXT_SHA = '5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33'
PREVIOUS_PROOF_SHA = '9e08ceec61b05073863c60bf74d6445b423a836e04b97f8c09ff82646cad5d75'
CASE_NAMES = {'retained-free', 'retained-paid-shape'}
STAGE_NAMES = {'source-customer', 'schedule', 'claim', 'retained-effect'}


def original_validator(checkout):
    raw = (checkout / CONTEXT).read_bytes()
    if sha256(raw).hexdigest() != CONTEXT_SHA:
        raise ValueError('Original context validator drift')
    code = ast.parse(raw, filename=CONTEXT)
    [coordinator] = [node for node in code.body if isinstance(node, ast.ClassDef) and node.name == 'Coordinator']
    [method] = [node for node in coordinator.body if isinstance(node, ast.FunctionDef) and node.name == 'grant_values']
    definitions = [node for node in code.body if getattr(node, 'name', None) in {'HeldFailure', 'require', 'quote'}]
    [columns] = [node for node in code.body if isinstance(node, ast.Assign)
                 and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id == 'GRANT_COLUMNS']
    namespace = {'__name__': 'pinned_grant_values', 're': re, 'uuid': uuid}
    module = ast.Module(body=[columns, *definitions, method], type_ignores=[])
    exec(compile(module, CONTEXT, 'exec', dont_inherit=True), namespace)
    return namespace


class GrantValuesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        previous = cls.previous_path.read_bytes()
        if sha256(previous).hexdigest() != PREVIOUS_PROOF_SHA:
            raise ValueError('Preserved previous proof drift')
        cls.previous = json.loads(previous)['cases']
        current = json.loads(cls.current_path.read_bytes())
        if current['source_pins'][CONTEXT] != CONTEXT_SHA or current['runtime'] != 'NOT_RUN':
            raise ValueError('Current proof authority drift')
        cls.current = current['cases']
        cls.original = original_validator(cls.checkout)

    def validate_template(self, template):
        role = template['database_login_role']
        backend = {'pid': '100', 'xid': '210', 'login': role, 'current_user': role}
        issuer = {'pid': '101', 'xid': '211', 'login': 'wa_context_issuer', 'clock': '2026-11-28 04:00:00+00'}
        return self.original['grant_values'](None, template, backend, issuer,
                                               '00000000-0000-4000-8000-000000000001', '0' * 64)

    def test_old_source_customer_templates_fail_the_original_validator(self):
        for case, data in self.previous.items():
            with self.subTest(case=case):
                with self.assertRaisesRegex(self.original['HeldFailure'], '^FINITE_CAPABILITIES_REQUIRED$'):
                    self.validate_template(data['grants']['source-customer'])

    def test_exact_remapped_membership_and_other_template_fields_are_preserved(self):
        self.assertEqual(set(self.previous), CASE_NAMES)
        self.assertEqual(set(self.current), CASE_NAMES)
        for case, data in self.current.items():
            self.assertEqual(set(data['grants']), STAGE_NAMES)
            self.assertEqual(set(self.previous[case]['grants']), STAGE_NAMES)
            for stage, template in data['grants'].items():
                with self.subTest(case=case, stage=stage):
                    previous = self.previous[case]['grants'][stage]
                    self.assertEqual(len(previous['allowed_fields']), len(set(previous['allowed_fields'])))
                    self.assertEqual(template, {**previous, 'allowed_fields': sorted(previous['allowed_fields'])})

    def test_original_validator_accepts_all_eight_corrected_templates(self):
        validated = 0
        for case, data in self.current.items():
            for stage, template in data['grants'].items():
                with self.subTest(case=case, stage=stage):
                    values = self.validate_template(template)
                    stored_fields = 'ARRAY[' + ','.join(self.original['quote'](field)
                                                       for field in template['allowed_fields']) + ']::text[]'
                    self.assertEqual(values['allowed_fields'], stored_fields)
                    self.assertEqual(set(values), set(self.original['GRANT_COLUMNS']))
                    validated += 1
        self.assertEqual(validated, 8)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--checkout', required=True, type=Path)
    cli.add_argument('--previous', required=True, type=Path)
    cli.add_argument('--current', required=True, type=Path)
    args = cli.parse_args()
    GrantValuesTests.checkout = args.checkout.resolve(strict=True)
    GrantValuesTests.previous_path = args.previous.resolve(strict=True)
    GrantValuesTests.current_path = args.current.resolve(strict=True)
    unittest.main(argv=[__file__], verbosity=2)


if __name__ == '__main__':
    main()
