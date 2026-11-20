"""Environment-free source tests. No Docker/database/process execution."""
import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from pglast import parse_sql

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("worker_control_proposal", ROOT / "scripts/prepare-worker-control-rehearsal.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkerProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.manifest = module.build()
        cls.acl = json.loads((ROOT / module.ACL).read_text(encoding="utf8"))

    def test_all_sql_parses_without_execution(self):
        sql_files = {name: value for name, value in self.files.items() if name.endswith(".sql")}
        self.assertEqual(len(sql_files), 16)
        for name, value in sql_files.items():
            with self.subTest(name=name): self.assertGreater(len(parse_sql(value)), 0)

    def test_selected_ids_and_all_statuses_stay_not_run(self):
        self.assertEqual(set(self.manifest["selected_control_ids"]), {"P0C-TRACK-01", "P0C-EVIDENCE-01", "P0C-CTX-02"})
        self.assertEqual({row["id"] for row in self.manifest["source_control_definitions"]}, set(module.SELECTED))
        self.assertFalse(self.manifest["database_contacted"])
        self.assertFalse(self.manifest["sql_executed"])
        for case in self.manifest["scenarios"] + self.manifest["mandatory_unprepared_vectors"] + self.manifest["setup_bypasses"]:
            self.assertEqual(case["status"], "NOT_RUN")
        self.assertEqual(self.manifest["database_posture"], "D")

    def test_existing_source_bytes_are_unchanged_and_output_deterministic(self):
        before = {path: module.sha((ROOT / path).read_bytes()) for path in module.INPUTS}
        second, manifest = module.build()
        self.assertEqual(second, self.files)
        self.assertEqual(before, manifest["source_files_sha256"])

    def test_exact_original_worker_acl_ceiling(self):
        rows = [row for row in self.acl if row["role"] == "wa_worker"]
        self.assertEqual(len(rows), 32)
        self.assertEqual(rows, self.manifest["worker_acl_ceiling_rows"])
        processing = self.manifest["grants"]["process"]["allowed_fields"]
        self.assertEqual(processing, sorted(set(processing)))
        self.assertFalse(any("*" in token for token in processing))
        for token in processing:
            parts = token.split("/")
            if len(parts) < 4 or parts[2] not in ("SELECT", "INSERT", "UPDATE"): continue
            model, _, operation, field = parts
            if field == "@row":
                self.assertEqual(operation, "UPDATE"); continue
            self.assertTrue(any(row["model"] == model and row["operation"] == operation and field in row["fields"] for row in rows), token)
        self.assertFalse(any(token.startswith(("RuntimeOutboxMessage/", "TrackPlan/", "TrackEntitlementDefinition/", "TrackPlanEntitlement/")) and "/INSERT/" in token for token in processing))

    def test_update_capability_cannot_expand_columns(self):
        with self.assertRaisesRegex(ValueError, "exceeds original ACL"):
            module.capabilities(self.acl, "wa_worker", {"TrackBaseSelection": [module.uid("selection")]}, {"TrackBaseSelection": {"UPDATE": ["userId"]}})

    def test_fence_bearing_selected_rows_have_exact_revision_one_capabilities(self):
        processing = self.manifest["grants"]["process"]["allowed_fields"]
        for model, key in (("RuntimeWorkItem", "work"), ("RuntimeEffectReceipt", "effect"), ("RuntimeAttempt", "attempt")):
            prefix = model + "/" + self.manifest["ids"][key] + "/revision/"
            self.assertEqual([token for token in processing if token.startswith(prefix)], [prefix + "1"])
            self.assertTrue(any(token.startswith(model + "/" + self.manifest["ids"][key] + "/SELECT/") for token in processing))

    def test_finite_protected_transaction_and_issuer_order(self):
        caps = self.manifest["finite_caps"]
        self.assertEqual((caps["jobs"], caps["worker_claims"], caps["worker_processing_transactions"], caps["business_enrollments"]), (1, 1, 1, 1))
        self.assertFalse(caps["polling_or_worker_loop"])
        for name in ("schedule", "claim", "process"):
            grant = self.manifest["grants"][name]
            self.assertIn("separate actual issuer INSERT+COMMIT", grant["issuance_order"])
            self.assertIn("same still-open connection", grant["issuance_order"])
            self.assertNotIn("token_hash", grant)
            self.assertNotIn("backend_pid", grant)
        self.assertEqual(self.manifest["grants"]["process"]["source_generation"], "1")

    def test_fixture_bypass_is_only_five_named_owner_guards(self):
        text = self.files["independent-fixtures.sql"]
        self.assertEqual(text.count("DISABLE TRIGGER owner_commit;"), 5)
        self.assertEqual(text.count("ENABLE TRIGGER owner_commit;"), 5)
        for forbidden in ("TRIGGER USER", "TRIGGER ALL", "DISABLE ROW LEVEL SECURITY", "session_replication_role", "app.customer_profiles", "app.track_subscriptions", "app.track_base_selection", "app.track_enrollment_receipt"):
            self.assertNotIn(forbidden, text)
        self.assertIn("count(*)=5 AND bool_and(t.tgenabled='O')", self.files["fixture-guards-observe.sql"])

    def test_effect_inbox_link_and_all_writes_precede_forced_constraints(self):
        text = self.files["enroll.sql"]
        command = text.index("INSERT INTO platform.runtime_command_receipt")
        effect = text.index("INSERT INTO platform.runtime_effect_receipt")
        inbox = text.index("INSERT INTO platform.runtime_inbox_receipt")
        link = text.index("UPDATE platform.runtime_work_item SET effect_receipt_id=")
        subscription = text.index("INSERT INTO app.track_subscriptions")
        selection = text.index("INSERT INTO app.track_base_selection")
        receipt = text.index("INSERT INTO app.track_enrollment_receipt")
        constraints = text.index("SET CONSTRAINTS ALL IMMEDIATE;")
        self.assertTrue(command < effect < inbox < link < subscription < selection < receipt < constraints < text.index("COMMIT;"))
        self.assertEqual(text.count("INSERT INTO platform.owner_mutation_evidence"), 3)
        for forbidden in ("DISABLE TRIGGER", "SET ROLE", "INSERT INTO app.track_usage", "INSERT INTO app.privacy", "INSERT INTO platform.runtime_reservation"):
            self.assertNotIn(forbidden, text)

    def test_registered_closed_result_and_exact_evidence_codec(self):
        cm = module.customer_module(ROOT)
        registry = cm.FixtureRegistry(ROOT)
        for path in ("contracts/database-review/foundation-payloads.v1.schema.json", "contracts/database-review/owner-mutation-evidence.v1.schema.json"):
            doc = json.loads((ROOT / path).read_text(encoding="utf8")); registry.documents[doc["$id"]] = doc
        doc = registry.documents["urn:workinants:database-review:foundation-payloads:v1"]
        schema = doc["$defs"]["assignDefaultFreeTrackCustomerResult"]
        value = self.manifest["fixture_values"]["result"]
        self.assertEqual(registry.errors(value, schema, doc), [])
        for mutated in ({key: val for key, val in value.items() if key != "receipt"}, {**value, "arbitrary": "private"}, {**value, "selectionRevision": 0}):
            self.assertTrue(registry.errors(mutated, schema, doc))
        text = self.files["enroll.sql"]
        self.assertIn(module.RESULT, text)
        self.assertIn("encode(sha256(convert_to(", text)
        self.assertNotIn("SH-114", text)
        self.assertNotIn('"result_digest") VALUES (NULL', text)
        for model, evidence in self.manifest["fixture_values"]["evidence"].items():
            evidence_doc = registry.documents["urn:workinants:database-review:owner-evidence:v1"]
            self.assertEqual(registry.errors(evidence, evidence_doc["$defs"][model], evidence_doc), [])
            self.assertIsNone(evidence["prior"])
            self.assertEqual(evidence["committed"]["revision"], "0")

    def test_observer_checks_result_relation_and_full_same_transaction_group(self):
        text = self.files["enroll-observe.sql"]
        for required in ("q.result_body->>'receipt'=r.id::text", "q.result_body->>'selectionRevision'=r.selection_revision::text", "q.result_body->>'outcome'=r.result_code", "e.result_hash=q.result_digest", "q.fingerprint=o.payload_hash", "w.effect_receipt_id=e.id", "v.evidence_body=", "v.evidence_digest=encode(sha256(", "'evidence_count'"):
            self.assertIn(required, text)
        for alias in ("e", "i", "w", "s", "b", "r", "h", "g", "a"):
            self.assertIn(alias + ".mutation_transaction_id=q.mutation_transaction_id", text)
        self.assertIn("owner contract does not normatively choose", self.manifest["fixture_conventions_requiring_review"]["wire_result_receipt"])

    def test_currentness_is_independent_committed_identity_change(self):
        for generation, step, previous in ((1, "rotate", "bootstrap"), (2, "revoke", "rotate"), (3, "recover", "revoke")):
            text = self.files["identity-" + step + ".sql"]
            self.assertIn(module.quote(self.manifest["ids"]["identity-" + previous]), text)
            self.assertIn("security_generation=" + str(generation), text)
            self.assertIn("revoked_at=(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id=", text)
            self.assertTrue(text.endswith("COMMIT;\n"))
        case = next(row for row in self.manifest["scenarios"] if row["name"] == "worker-service-currentness")
        self.assertIn("before A's first protected statement", case["synchronization"])
        self.assertIn("no protected read/action/source lock", " ".join(case["steps"]))
        self.assertIn("synthetic authorization refs", case["identity_upstream_limit"])
        for name, generation in (("baseline-current", 0), ("bound-before-rotate", 0), ("fresh-after-rotate", 1), ("bound-before-revoke", 1), ("revoked-current-generation", 2), ("fresh-after-recover", 3)):
            grant = case["grants"][name]
            self.assertEqual(grant["source_generation"], "1")
            self.assertEqual(grant["security_generation"], str(generation))
            self.assertTrue(all("/SELECT/" in token or "/revision/1" in token for token in grant["allowed_fields"]))
        self.assertIn("count(*)", self.files["currentness-read.sql"])
        self.assertNotIn("lease_token_hash", self.files["currentness-read.sql"])

    def test_generation_and_usage_privacy_gates_remain_explicit(self):
        blocked = {row["name"]: row for row in self.manifest["scenarios"] if row["runtime_eligibility"].startswith("BLOCKED")}
        self.assertEqual(set(blocked), {"worker-source-generation", "worker-user-security-generation"})
        self.assertIn("CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED", blocked["worker-source-generation"]["execution_dependencies"])
        self.assertIn("P0D_TRACK_USAGE_PERIOD_RECONCILIATION", self.manifest["preserved_gates"])
        self.assertIn("P0E_TRACK_APP_PROFILE_AND_PLAN_FACT_PORT", self.manifest["preserved_gates"])
        self.assertGreaterEqual(len(self.manifest["mandatory_unprepared_vectors"]), 5)

    def test_generator_has_no_runtime_process_or_network_api(self):
        tree = ast.parse((ROOT / "scripts/prepare-worker-control-rehearsal.py").read_text(encoding="utf8"))
        imports = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
        self.assertFalse(imports & {"subprocess", "socket", "requests", "psycopg", "psycopg2", "docker", "os"})
        for name, text in self.files.items():
            self.assertNotRegex(text, r"[0-9a-f]{64}.*(?:PGPASSWORD|password=)")
        self.assertIn("No passwords, handles, raw stderr", self.manifest["failure_contract"])


if __name__ == "__main__": unittest.main()
