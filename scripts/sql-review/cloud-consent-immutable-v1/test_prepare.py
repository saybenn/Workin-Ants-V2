import json
import unittest
import uuid

import prepare
import protocol


FIXTURE_RUN = "13572468-1246-4ad8-9c12-02468ace2468"
EXACT_DIAGNOSTIC = (
    "psql:<stdin>:9: ERROR:  P0001: exact consent binding required\n"
    "CONTEXT:  PL/pgSQL function platform_private.consent_guard() line 17 at RAISE\n"
    "LOCATION:  exec_stmt_raise, pl_exec.c:3911\n"
)


class ConsentSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.assets = prepare.assemble(FIXTURE_RUN)

    def test_exact_source8_immutable_scope_rebuilds(self):
        self.assertEqual((self.packet, self.assets), prepare.assemble(FIXTURE_RUN))
        self.assertEqual(self.packet["case_id"], "P0C-IMMUTABLE-01")
        self.assertEqual(self.packet["assertion_id"], "control.empty_context")
        self.assertEqual(self.packet["runtime"], "NOT_RUN")
        self.assertEqual(self.packet["execution_entry"], "HELD_NO_CONSENT_OWNER_COMPOSITION")
        self.assertEqual(self.packet["assertion_promotions"], 0)
        self.assertEqual(len(self.packet["full42_tables"]), 42)
        self.assertEqual(len(self.packet["source_asset_sha256"]), 15)

    def test_coherent_null_and_empty_rollback_recipes_with_closed_grants(self):
        pg = prepare.parser()
        grant_targets = set()
        for case, expected_null in zip(self.packet["cases"], (True, False), strict=True):
            key = case["name"]
            actions = case["grants_in_order"]
            self.assertEqual([g["action"] for g in actions],
                             ["publishConsentVersion.v1", "recordConsentPresentation.v1", "SH-007.v1"])
            self.assertEqual([len(g["allowed_fields"]) for g in actions], [24, 38, 64])
            for grant in actions:
                self.assertEqual(grant["database_login_role"], "wa_app_runtime")
                self.assertEqual(grant["allowed_fields"], sorted(set(grant["allowed_fields"])))
                self.assertFalse(any("*" in leaf or "/UPDATE/" in leaf for leaf in grant["allowed_fields"]))
                grant_targets.add(grant["target_id"])
            publisher, presentation, proof = [grant["target_id"] for grant in actions]
            self.assertIn(f"ConsentPresentation/{presentation}/contentRevision/{publisher}", actions[1]["allowed_fields"])
            self.assertIn(f"ConsentLog/{proof}/presentation/{presentation}", actions[2]["allowed_fields"])
            self.assertIn(f"ConsentLog/{proof}/contentRevision/{publisher}", actions[2]["allowed_fields"])
            present = pg.parse_sql(self.assets[f"{key}/presentation.sql"])[0].stmt
            attempt = pg.parse_sql(self.assets[f"{key}/deny.sql"])
            proof_insert = attempt[1].stmt
            present_context = present.selectStmt.valuesLists[0][-1]
            proof_context = proof_insert.selectStmt.targetList[11].val
            self.assertEqual(proof_context, present_context)
            self.assertIs(present_context.isnull, expected_null)
            if not expected_null:
                self.assertEqual(present_context.val.sval, "")
            self.assertEqual(attempt[-1].stmt.kind.name, "TRANS_STMT_ROLLBACK")
            self.assertTrue(all("COMMIT;" not in self.assets[f"{key}/{name}"] for name in (
                "publisher.sql", "presentation.sql", "preread.sql", "deny.sql")))
        self.assertEqual(len(grant_targets), 6)

    def test_unexpected_diagnostic_and_unclosed_success_never_qualify(self):
        name = protocol.CASES[0]
        before, after = protocol.markers(name)
        success = protocol.denial_receipt(name, 3, [before], False, EXACT_DIAGNOSTIC)
        self.assertTrue(success["exact_source_diagnostic"])
        self.assertEqual(success["source_body_line"], 17)
        for rc, rows, ack, stderr in (
            (3, [before], False, EXACT_DIAGNOSTIC.replace("P0001", "42501")),
            (3, [before], False, EXACT_DIAGNOSTIC.replace("line 17", "line 4")),
            (3, [before], False, EXACT_DIAGNOSTIC + "DETAIL: discarded-raw-canary\n"),
            (3, [before, after], False, EXACT_DIAGNOSTIC),
            (3, [before], True, EXACT_DIAGNOSTIC),
            (0, [before], False, EXACT_DIAGNOSTIC),
        ):
            value = protocol.denial_receipt(name, rc, rows, ack, stderr)
            self.assertFalse(value["exact_source_diagnostic"])
            self.assertNotIn("discarded-raw-canary", json.dumps(value))

    def test_preread_requires_typed_complete_coherence_and_empty_registry(self):
        expected = protocol.PREREAD_OBSERVATION
        for field, wrong in (("exact_prerequisite_rows", True), ("all_other_binding_predicates_exact", False),
                             ("global_registry_admits", True)):
            rows = [json.dumps(expected | {field: wrong})]
            self.assertFalse(protocol.acknowledged_observation(rows, True, "", expected))
        self.assertTrue(protocol.acknowledged_observation([json.dumps(expected)], True, "", expected))
        self.assertFalse(protocol.acknowledged_observation(
            ['{"one_exact_prefix":true,"one_exact_prefix":true}'], True, "", protocol.PREFIX_OBSERVATION))

    def test_zero_residue_state_and_exact_issuer_exclusions(self):
        tables = self.packet["full42_tables"]
        before = [{"table": name, "count": 0, "sha256": "f" * 64} for name in tables]
        changed = [dict(row) for row in before]
        changed[7]["count"] = 1
        self.assertTrue(protocol.state_matches(before, before, tables))
        self.assertFalse(protocol.state_matches(before, changed, tables))
        self.assertFalse(protocol.state_matches(before, before[:-1], tables))
        ids = tuple(str(uuid.uuid4()) for _ in range(6))
        text = protocol.state_observer_sql(self.assets["full42-state.sql"], ids)
        self.assertEqual(len(prepare.parser().parse_sql(text)), 1)
        self.assertTrue(all(text.count(key) == 1 for key in ids))
        with self.assertRaisesRegex(protocol.Held, "CONSENT_PRECISE_ISSUER_EXCLUSIONS"):
            protocol.state_observer_sql(self.assets["full42-state.sql"], ids[:5])
        with self.assertRaisesRegex(protocol.Held, "CONSENT_PRECISE_ISSUER_EXCLUSIONS"):
            protocol.state_observer_sql(self.assets["full42-state.sql"], (ids[0],) * 6)
        self.assertFalse(protocol.issuer_retention_matches({"exact_count": 6}, 6))

    def test_full_state_uses_c_order_matching_all_42_sql_table_labels(self):
        pg = prepare.parser()
        candidate = self.assets["full42-state.sql"]
        parent = (prepare.ROOT / prepare.STATE).read_text()
        self.assertEqual(candidate.replace(' ORDER BY table_name COLLATE "C") FROM (', ' ORDER BY table_name) FROM (', 1), parent)
        statements = pg.parse_sql(protocol.state_observer_sql(candidate, ()))
        self.assertEqual(len(statements), 1)
        outer = statements[0].stmt
        aggregate = outer.targetList[0].val
        self.assertEqual([part.sval for part in aggregate.funcname], ["jsonb_agg"])
        self.assertEqual(len(aggregate.agg_order), 1)
        order = aggregate.agg_order[0]
        self.assertEqual(order.sortby_dir.name, "SORTBY_DEFAULT")
        self.assertIsInstance(order.node, pg.ast.CollateClause)
        self.assertEqual([part.sval for part in order.node.collname], ["C"])
        self.assertEqual([part.sval for part in order.node.arg.fields], ["table_name"])

        def labels(branch):
            if branch.op.name == "SETOP_UNION":
                self.assertIs(branch.all, True)
                return labels(branch.larg) + labels(branch.rarg)
            self.assertEqual(branch.op.name, "SETOP_NONE")
            self.assertEqual(branch.targetList[0].name, "table_name")
            return [branch.targetList[0].val.val.sval]

        tables = labels(outer.fromClause[0].subquery)
        self.assertEqual(len(tables), len(set(tables)))
        self.assertTrue(all(name.isascii() for name in tables))
        self.assertEqual(sorted(tables, key=str.encode), self.packet["full42_tables"])

    def test_seed_preserves_only_previously_reviewed_trigger_exceptions(self):
        expected = ["app.users", "app.user_security_profiles"]
        self.assertEqual([rule["table"] for rule in self.packet["setup_only_trigger_exceptions"]], expected)
        for rule in self.packet["setup_only_trigger_exceptions"]:
            self.assertEqual(rule["trigger"], "owner_commit")
            self.assertIs(rule["setup_only"], True)
        seed = self.assets["identity-seed.sql"]
        self.assertIn("DISABLE TRIGGER owner_commit", seed)
        self.assertEqual(seed.count("DISABLE TRIGGER"), 2)
        self.assertEqual(seed.count("ENABLE TRIGGER"), 2)
        self.assertNotIn("consent_", seed)
