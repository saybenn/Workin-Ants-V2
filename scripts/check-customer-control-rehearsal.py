"""Focused environment-free fixture checks; no process or database invocation."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import unittest

from pglast import ast, parse_sql
from contract_schema import Registry

ROOT = Path(__file__).resolve().parents[1]
generator = runpy.run_path(str(ROOT / "scripts/prepare-customer-control-rehearsal.py"))


class CustomerControlFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.manifest = generator["build"]()
        cls.cases = {row["variation"]: row for row in cls.manifest["cases"]}
        cls.source = (ROOT / generator["APPLICATION"]).read_text(encoding="utf8")
        cls.registry = generator["FixtureRegistry"](ROOT)
        for path in ("contracts/database-review/foundation-payloads.v1.schema.json", "contracts/database-review/owner-mutation-evidence.v1.schema.json"):
            doc = json.loads((ROOT / path).read_text(encoding="utf8")); cls.registry.documents[doc["$id"]] = doc

    def test_selected_ids_status_counts_and_original_packet_preserved(self):
        self.assertEqual(self.manifest["selected_control_ids"], ["P0C-BOOT-01", "P0C-ATOMIC-01", "P0C-UNIQUE-01", "P0C-CAS-01"])
        self.assertEqual(len(self.manifest["cases"]), 17)
        self.assertTrue(all(row["status"] == "NOT_RUN" for row in self.manifest["cases"]))
        self.assertFalse(self.manifest["database_contacted"] or self.manifest["sql_executed"])
        original = "review-output/first-rehearsal/fixtures.json"
        self.assertEqual(self.manifest["source_inputs_sha256"][original], hashlib.sha256((ROOT / original).read_bytes()).hexdigest())
        self.assertTrue(all("first-rehearsal" not in name for name in self.files))

    def test_all_proposals_parse_without_privilege_network_or_process_code(self):
        total = 0
        for name, text in self.files.items():
            if not name.endswith(".sql"): continue
            statements = parse_sql(text); total += len(statements)
            self.assertFalse(any(isinstance(row.stmt, (ast.GrantStmt, ast.GrantRoleStmt, ast.CreatedbStmt, ast.CreateRoleStmt, ast.DropStmt)) for row in statements))
            if name.endswith("-observe.sql"):
                self.assertEqual(len(statements), 1)
                self.assertIsInstance(statements[0].stmt, ast.SelectStmt)
        self.assertGreater(total, 150)

    def test_every_source_message_constraint_and_frame_is_registered(self):
        for case in self.manifest["cases"]:
            diagnostic = case["intended_diagnostic"]
            if not diagnostic: continue
            if diagnostic["exact_source_message"] and diagnostic["sqlstate"] != "P0002":
                self.assertIn("RAISE EXCEPTION '" + diagnostic["exact_source_message"] + "'", self.source)
            if diagnostic["source_constraint"]:
                self.assertIn(diagnostic["source_constraint"], self.source)
            if diagnostic["required_source_function"]:
                self.assertIn("CREATE FUNCTION " + diagnostic["required_source_function"] + "(", self.source)
            self.assertEqual(diagnostic["unknown_diagnostic_disposition"], "STOP_UNCLASSIFIED_NOT_EXPECTED_PASS")

    def test_valid_payloads_are_closed_and_targeted_omissions_reject(self):
        valid = next(row for row in self.manifest["cases"] if row["variation"] == "valid")
        self.assertFalse(self.registry.check("SH-004", "response", valid["fixture_values"]["response"]))
        self.assertTrue(self.registry.check("SH-004", "response", self.cases["missing-result-receipt"]["fixture_values"]["response"]))
        types = self.registry.documents["urn:workin-ants:types:v1"]
        schema = types["$defs"]["EventPayload_customer_lifecycle_changed_v1"]
        self.assertFalse(self.registry.errors(valid["fixture_values"]["event"], schema, types))
        self.assertTrue(self.registry.errors(self.cases["missing-event-user"]["fixture_values"]["event"], schema, types))
        evidence = self.registry.documents["urn:workinants:database-review:owner-evidence:v1"]
        self.assertTrue(self.registry.errors(self.cases["missing-evidence-status"]["fixture_values"]["evidence"], evidence["$defs"]["CustomerProfile"], evidence))

    def test_caps_are_finite_complete_source_row_fields_and_no_extra_message(self):
        for case in self.manifest["cases"]:
            caps = case["grant"]["allowed_fields"]
            self.assertEqual(caps, sorted(set(caps)))
            self.assertFalse(any("*" in value for value in caps))
            self.assertIn("CustomerProfile/" + case["ids"]["CustomerProfile"] + "/revision/0", caps)
            self.assertEqual(case["grant"]["action"], "SH-004.v1")
            self.assertEqual(case["grant"]["purpose"], "provision")
            extra = "RuntimeOutboxMessage/" + case["ids"]["extra"] + "/"
            self.assertEqual(any(value.startswith(extra) for value in caps), case["variation"] == "extra-free")

    def test_exact_create_message_counts_and_omission_sql(self):
        for case in self.manifest["cases"]:
            text = self.files[case["transaction_sql"]]
            inserts = [row.stmt for row in parse_sql(text) if isinstance(row.stmt, ast.InsertStmt)]
            messages = [row for row in inserts if row.relation.relname == "runtime_outbox_message"]
            wanted = 3 if case["variation"] == "extra-free" else 1 if case["variation"] in ("missing-event", "missing-free") else 2
            self.assertEqual(len(messages), wanted)
            self.assertIn("COMMIT;", text)
            self.assertNotIn("bind_request_context", text)
            self.assertNotIn("database_action_grant", text)
            if case["variation"] == "missing-history": self.assertNotIn("INSERT INTO app.customer_profile_lifecycle_event", text)
            if case["variation"] == "missing-evidence": self.assertNotIn("INSERT INTO platform.owner_mutation_evidence", text)

    def test_native_uniqueness_is_scoped_without_adapter_claim(self):
        duplicate = self.cases["duplicate-semantic"]
        changed = self.cases["changed-fingerprint"]
        for case in (duplicate, changed):
            text = self.files[case["transaction_sql"]]
            commands = [row.stmt for row in parse_sql(text) if isinstance(row.stmt, ast.InsertStmt) and row.stmt.relation.relname == "runtime_command_receipt"]
            self.assertEqual(len(commands), 2)
            self.assertEqual(case["intended_diagnostic"]["sqlstate"], "23505")
            self.assertIn("not a production", case["diagnostic_limit"])
        scopes = [row for row in self.manifest["cases"] if row["name"].startswith("unique-distinct-scope")]
        self.assertEqual(scopes[0]["semantic_key"], scopes[1]["semantic_key"])
        self.assertNotEqual(scopes[0]["grant"]["target_id"], scopes[1]["grant"]["target_id"])
        self.assertNotEqual(scopes[0]["grant"]["principal_user_id"], scopes[1]["grant"]["principal_user_id"])

    def test_update_and_retained_cas_are_explicitly_gated_not_null_bypasses(self):
        update, cas = self.manifest["update_plan"], self.manifest["cas_plan"]
        self.assertEqual(update["execution_dependencies"], [generator["GATE"]])
        self.assertEqual(cas["execution_dependencies"], [generator["GATE"]])
        self.assertEqual(update["grant"]["source_generation"], "0")
        self.assertEqual(update["required_group"]["committed_revision"], "1")
        self.assertEqual(update["required_group"]["exact_message_count"], 1)
        self.assertEqual(update["required_group"]["free_command_count"], 0)
        self.assertNotIn("result_schema_id", update["required_group"])
        joined = " ".join(cas["steps"])
        self.assertIn("distinct real authenticated", joined)
        self.assertIn("exactly zero returned rows", joined)
        self.assertIn("Explicitly ROLLBACK B", joined)
        self.assertIn("independently confirm it waits on A", joined)
        self.assertTrue(all(value["status"] == "NOT_RUN" for value in cas["mandatory_blocked_vectors"]))
        self.assertEqual([row["session"] for row in cas["participants"]], ["A", "B"])
        a, b = cas["participants"]
        self.assertEqual(a["grant"]["target_id"], b["grant"]["target_id"])
        self.assertNotEqual(a["ids"]["RuntimeCommandReceipt"], b["ids"]["RuntimeCommandReceipt"])
        self.assertNotEqual(a["grant"]["allowed_fields"], b["grant"]["allowed_fields"])
        self.assertNotEqual(update["grant"]["target_id"], a["grant"]["target_id"])
        for vector in update["after_gate_variations"]:
            self.assertEqual(vector["status"], "NOT_RUN")
            if vector["intended_diagnostic"]["exact_source_message"]:
                self.assertIn("RAISE EXCEPTION '" + vector["intended_diagnostic"]["exact_source_message"] + "'", self.source)
            else:
                self.assertIn("ADD CONSTRAINT " + vector["intended_diagnostic"]["source_constraint"], self.source)
            free_prefix = "RuntimeOutboxMessage/" + update["ids"]["free"] + "/"
            self.assertEqual(any(value.startswith(free_prefix) for value in vector["grant"]["allowed_fields"]), vector["name"] == "extra-free-on-update")

    def test_foreign_history_actor_has_trusted_fk_fixture_and_all_hashes_match(self):
        self.assertIn(generator["uid"]("foreign-user"), self.files["trusted-identity-fixtures.sql"])
        self.assertIn("ENABLE TRIGGER owner_commit", self.files["trusted-identity-fixtures.sql"])
        self.assertNotIn("DISABLE TRIGGER USER", self.files["trusted-identity-fixtures.sql"])
        for path, expected in self.manifest["files_sha256"].items():
            self.assertEqual(hashlib.sha256(self.files[path].encode("utf8")).hexdigest(), expected)

    def test_exact_independent_fixture_trigger_restoration(self):
        contract = self.manifest["trusted_setup_trigger_contract"]
        self.assertEqual(len(contract["bypassed"]), 2)
        self.assertEqual(len(contract["expected_user_triggers"]), 4)
        self.assertTrue(contract["physical_guards_retained"])
        self.assertEqual(contract["status"], "NOT_RUN")
        observer = self.files[contract["observer_sql"]]
        self.assertEqual(len(parse_sql(observer)), 1)
        for trigger in contract["expected_user_triggers"]:
            self.assertIn(trigger["table"], observer)
            self.assertIn(trigger["trigger"], observer)
            self.assertIn(trigger["function"], observer)
        self.assertIn("EXCEPT", observer)
        self.assertIn("no_project_user_trigger_disabled", observer)

    def test_negative_markers_prove_immediate_or_deferred_failure_stage(self):
        for case in self.manifest["cases"]:
            oracle = case["stage_marker_oracle"]
            if case["expected_commit"]: continue
            text = self.files[case["transaction_sql"]]
            self.assertFalse(oracle["commit_acknowledgement_required"])
            for marker in oracle["expected_completed_markers"] + oracle["forbidden_markers"]:
                self.assertIn("SELECT " + generator["quote"](marker) + ";", text)
            self.assertFalse(set(oracle["expected_completed_markers"]) & set(oracle["forbidden_markers"]))
            if case["variation"] in ("create-predecessor", "missing-evidence-status"):
                self.assertEqual(oracle["expected_failure_stage"], "EVIDENCE_INSERT")
                self.assertEqual(oracle["expected_failure_timing"], "IMMEDIATE_STATEMENT")
            if case["variation"] in ("missing-result-receipt", "result-version"):
                self.assertEqual(oracle["expected_failure_stage"], "COMMAND_INSERT")
            if case["variation"] in ("missing-history", "missing-evidence", "missing-event", "missing-free", "extra-free", "wrong-history-actor", "wrong-event-user"):
                self.assertEqual(oracle["expected_failure_stage"], "COMMIT")
                self.assertEqual(oracle["expected_completed_markers"][-1], "WA_CUSTOMER_CONTROL_BEFORE_COMMIT")


if __name__ == "__main__": unittest.main(verbosity=2)
