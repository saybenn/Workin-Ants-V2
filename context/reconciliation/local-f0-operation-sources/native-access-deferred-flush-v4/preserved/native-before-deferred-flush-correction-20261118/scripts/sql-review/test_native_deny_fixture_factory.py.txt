"""Environment-free source/fixture checks only; no DB/Docker/SQL execution."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest

from pglast import ast, parse_sql, parse_plpgsql
from pglast.stream import RawStream

import catalog_manifest as source
import compare_native_catalog as compare
import native_deny_fixture_factory as factory

ROOT = source.ROOT
sys.path.insert(0, str(ROOT / "scripts"))
generator = runpy.run_path(str(ROOT / "scripts/prepare-native-table-denials.py"))


class NativeDenyFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = source.build_manifest()["expected"]
        cls.schemas = factory.registry(ROOT)
        cls.rows = factory.make_rows(cls.expected, "test-baseline", cls.schemas)
        cls.graph = factory.dependencies(cls.expected, cls.rows)
        cls.files, cls.packet = generator["build"]()

    def test_exact_selected_forty_ids_no_status_or_positive_promotion(self):
        selected = json.loads((ROOT / generator["SELECTION"]).read_text(encoding="utf8"))["first_p0c_replay"]["ids"]
        wanted = [value for value in selected if value.startswith("P0C-TABLE-") and value.endswith("-DENY")]
        self.assertEqual(self.packet["selected_case_ids"], wanted)
        self.assertEqual(len(self.packet["cases"]), 40)
        self.assertTrue(all(case["status"] == "NOT_RUN" for case in self.packet["cases"]))
        self.assertTrue(all(case["source_allow_case"]["status"] == "NOT_RUN" for case in self.packet["cases"]))
        self.assertFalse(self.packet["database_contacted"] or self.packet["sql_executed"])
        self.assertEqual(sum(len(case["probes"]) for case in self.packet["cases"]), 960)
        self.assertEqual(len(self.packet["preparation_blocks"]), 4)

    def test_all42_rows_have_exact_native_columns_required_values_and_enums(self):
        self.assertEqual(set(self.rows), set(self.expected["tables"]))
        self.assertEqual(len(self.rows), 42)
        for table, row in self.rows.items():
            columns = self.expected["tables"][table]["columns"]
            self.assertEqual(set(row), set(columns))
            for column, info in columns.items():
                if not info["nullable"]: self.assertIsNotNone(row[column])
                if row[column] is not None and info["type"]["name"] in self.expected["enums"]:
                    self.assertIn(row[column], self.expected["enums"][info["type"]["name"]]["labels"])
            self.assertTrue(parse_sql(factory.insert_sql(table, row, self.expected)))

    def test_every_required_fk_tuple_resolves_before_child(self):
        ordered = factory.ordered(self.graph)
        self.assertEqual(len(ordered), 42)
        for table, parents in self.graph.items():
            for parent in parents: self.assertLess(ordered.index(parent), ordered.index(table))
        for table in self.rows:
            closure = factory.parent_closure(self.graph, table)
            self.assertNotIn(table, closure)
            self.assertTrue(self.graph[table] <= closure)
        altered = deepcopy(self.rows)
        altered["app.customer_profiles"]["user_id"] = "00000000-0000-4000-8000-000000000001"
        with self.assertRaises(factory.PreparationBlocked): factory.dependencies(self.expected, altered)

    def test_native_unique_projection_catches_duplicates_and_setup_has_no_conflicts(self):
        facts = list(self.rows.items())
        self.assertEqual(factory.validate_unique(self.expected, facts)["projected_setup_rows"], 42)
        with self.assertRaises(factory.PreparationBlocked): factory.validate_unique(self.expected, facts + [facts[0]])
        self.assertEqual(self.packet["offline_native_key_derivation"]["projected_setup_rows"], 205)
        self.assertEqual(self.packet["offline_native_key_derivation"]["native_execution"], "NOT_RUN")

    def test_all93_real_source_check_asts_have_concrete_derivations(self):
        results = factory.validate_checks(self.expected, self.rows, self.schemas)
        self.assertEqual(len(results), 93)
        self.assertTrue(all(row["native_execution"] == "NOT_RUN" for row in results))
        for table, column, value in (("platform.runtime_attempt", "fence", 0),
                                     ("platform.runtime_reservation", "quantity", 0),
                                     ("app.track_usage_events", "period_end", factory.START),
                                     ("app.track_plan_entitlements", "boolean_value", None),
                                     ("platform.runtime_command_receipt", "result_schema_version", "2"),
                                     ("app.consent_content_revision", "content_hash", "not-a-hash")):
            with self.subTest(table=table, column=column):
                rows = deepcopy(self.rows); rows[table][column] = value
                with self.assertRaises(factory.PreparationBlocked): factory.validate_checks(self.expected, rows, self.schemas)

    def test_closed_json_and_real_storage_codecs_fail_mutations(self):
        rows = deepcopy(self.rows)
        rows["platform.owner_mutation_evidence"]["evidence_body"]["committed"].pop("status")
        with self.assertRaises(factory.PreparationBlocked): factory.validate_checks(self.expected, rows, self.schemas)
        text = factory.sql_value(factory.StorageDigest("x", "text"), {"name": "pg_catalog.bpchar", "array_dimensions": 0})
        self.assertIn("convert_to('x','UTF8')", text)
        self.assertNotIn("jsonb", text)
        jsonb = factory.sql_value(factory.StorageDigest({"x": 1}), {"name": "pg_catalog.bpchar", "array_dimensions": 0})
        self.assertIn("::jsonb::text", jsonb)
        with self.assertRaises(factory.PreparationBlocked): factory.sql_value(factory.StorageDigest("x", "unreviewed"), {"name": "pg_catalog.bpchar", "array_dimensions": 0})

    def test_unknown_shape_default_cast_function_and_parent_cycle_block(self):
        for sql in ("unknown_function()", "'x'::app.unknown_type"):
            with self.subTest(sql=sql), self.assertRaises(factory.PreparationBlocked):
                factory.evaluate(compare.expression_ast(sql), {}, self.schemas)
        with self.assertRaises(factory.PreparationBlocked): factory.default_literal(compare.expression_ast("other.pg_current_xact_id()"))
        with self.assertRaises(factory.PreparationBlocked): factory.ordered({"a": {"b"}, "b": {"a"}})
        with self.assertRaises(factory.PreparationBlocked): factory.parent_closure({"a": {"a"}}, "a")

    def test_setup_never_disables_native_constraints_or_internal_ri(self):
        text = self.files["native-fact-setup.sql"]
        statements = parse_sql(text)
        self.assertNotIn("DISABLE TRIGGER USER", text)
        self.assertNotIn("DISABLE TRIGGER ALL", text)
        self.assertNotIn("session_replication_role", text)
        self.assertNotIn("DROP CONSTRAINT", text)
        self.assertEqual(len(self.packet["setup_bypassed_user_triggers"]), 60)
        self.assertEqual(len(self.packet["setup_retained_user_triggers"]), 40)
        all_bypassed = {row["identity"] for row in self.packet["setup_bypassed_user_triggers"]}
        all_retained = {row["identity"] for row in self.packet["setup_retained_user_triggers"]}
        self.assertFalse(all_bypassed & all_retained)
        self.assertEqual(all_bypassed | all_retained, set(self.expected["triggers"]))
        for row in self.packet["setup_bypassed_user_triggers"]:
            self.assertIn(generator["trigger_sql"](row, False), text)
            self.assertIn(generator["trigger_sql"](row, True), text)
        self.assertIsInstance(statements[-1].stmt, ast.TransactionStmt)
        self.assertEqual(statements[-1].stmt.kind.name, "TRANS_STMT_COMMIT")

    def test_controls_are_rollback_only_and_delete_leaf_has_no_children(self):
        for case in self.packet["cases"]:
            statements = parse_sql(self.files[case["native_controls"]])
            transactions = [row.stmt.kind.name for row in statements if isinstance(row.stmt, ast.TransactionStmt)]
            self.assertNotIn("TRANS_STMT_COMMIT", transactions)
            self.assertIn("TRANS_STMT_ROLLBACK", transactions)
            self.assertIn("TRANS_STMT_ROLLBACK_TO", transactions)
            self.assertNotIn(case["table"], case["insert_required_parent_tables"])
            self.assertNotIn(case["table"], case["delete_leaf_parent_tables"])
            for parent in case["delete_leaf_parent_tables"]:
                # Construction chooses only ancestors, never child dependants.
                self.assertNotEqual(parent, case["table"])
            for probe in case["probes"]:
                if probe["verb"] == "UPDATE" and probe["native_forbidden_column"]:
                    self.assertIn(probe["native_forbidden_column"], case["native_update_control_columns"])

    def test_every_ready_probe_is_typed_parseable_no_bypass_or_fake_identity(self):
        ready = 0
        for case in self.packet["cases"]:
            for probe in case["probes"]:
                self.assertEqual(probe["status"], "NOT_RUN")
                if probe["preparation"] == "BLOCKED":
                    self.assertNotIn("sql_text", probe); continue
                ready += 1
                sql = probe["sql_text"]
                self.assertTrue(parse_sql(sql))
                self.assertEqual(hashlib.sha256(sql.encode("utf8")).hexdigest(), probe["sql_sha256"])
                self.assertNotIn("ALTER TABLE", sql)
                self.assertNotIn("GRANT ", sql)
                self.assertNotIn("SET ROLE", sql)
                self.assertNotIn("bind_request_context", sql)
                if probe["expected_sqlstate"]:
                    self.assertEqual(probe["expected_sqlstate"], "42501")
                else:
                    self.assertTrue(probe["facet"].startswith("RLS_"))
                    self.assertEqual(probe["expected_rows"], 0)
        self.assertEqual(ready, 956)

    def test_provider_simulation_is_explicit_local_stressor_before_install(self):
        text = self.files["provider-role-simulation-before-migrate.sql"]
        statements = parse_sql(text)
        roles = [row.stmt for row in statements if isinstance(row.stmt, ast.CreateRoleStmt)]
        for row in statements:
            if isinstance(row.stmt, ast.DoStmt): self.assertEqual(len(parse_plpgsql(RawStream()(row))), 1)
        self.assertEqual([row.role for row in roles], ["anon", "authenticated", "service_role"])
        self.assertIn("service_role LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION BYPASSRLS", text)
        self.assertNotIn("wa_app_runtime", text)
        self.assertNotIn("wa_worker", text)
        self.assertNotIn("PASSWORD", text)
        self.assertFalse(self.packet["provider_role_simulation"]["hosted_supabase_parity"])
        self.assertIn("Never create roles after install", self.packet["provider_role_simulation"]["sequence"])

    def test_issuer_own_row_is_visible_and_foreign_row_denial_is_not_a_missing_row(self):
        case = next(row for row in self.packet["cases"] if row["model"] == "DatabaseActionGrant")
        controls = case["issuer_ownership_controls"]
        self.assertEqual((controls["own_expected_count"], controls["foreign_expected_count"]), (1, 0))
        foreign = self.packet["synthetic_facts"]["foreign-issuer-negative-only"]["platform.database_action_grant"]
        self.assertEqual(foreign["issuer_service"], "native-foreign-issuer-no-authority")
        self.assertEqual(foreign["backend_pid"], 0)
        self.assertIsNotNone(foreign["revoked_at"])
        probe = next(row for row in case["probes"] if row["role"] == "wa_context_issuer" and row["verb"] == "SELECT")
        self.assertIn(foreign["id"], probe["sql_text"])
        self.assertEqual(probe["facet"], "RLS_ISSUER_FOREIGN_ROW_EXISTING_DENIED")
        self.assertEqual(probe["expected_rows"], 0)
        self.assertIn(foreign["id"], self.files["native-fact-setup.sql"])
        self.assertTrue(parse_sql(controls["sql_text"]))
        self.assertTrue(parse_sql(controls["independent_fixture_observer_sql"]))

    def test_all_artifact_hashes_and_precise_fact_count(self):
        self.assertEqual(self.packet["baseline_table_count"], 42)
        self.assertEqual(self.packet["setup_additional_parent_or_leaf_rows"], 162)
        for name, expected in self.packet["files_sha256"].items():
            self.assertEqual(hashlib.sha256(self.files[name].encode("utf8")).hexdigest(), expected)
        for name, value in self.files.items():
            if name.endswith(".sql"): self.assertTrue(parse_sql(value))


if __name__ == "__main__": unittest.main(verbosity=2)
