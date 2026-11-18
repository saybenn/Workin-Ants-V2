"""Offline coordinator checks: ALL subprocess entry points are mocked/refused."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from pglast import ast, parse_sql

ROOT = Path(__file__).resolve().parents[2]
MODULE = runpy.run_path(str(ROOT / "scripts/sql-review/run-customer-control-rehearsal.py"))
M = MODULE["main"].__globals__
PACKET = json.loads((M["PACKET"] / "fixtures.json").read_text(encoding="utf8"))
APPLICATION = (ROOT / "review-output/foundation-application.review.sql").read_text(encoding="utf8")
BODIES = M["function_bodies"](APPLICATION)
ACK = M["ACK"]
CANARY = "RAW_SECRET_OR_ROW_CANARY_DO_NOT_SAVE"


def error_text(case):
    intended = case["intended_diagnostic"]
    if intended is None: return ""
    state, constraint = intended["sqlstate"], intended["source_constraint"]
    if constraint:
        if state == "23505": message = 'duplicate key value violates unique constraint "' + constraint + '"'
        else:
            table = "runtime_command_receipt" if constraint in ("result_json_boundary", "result_version_registered") else "owner_mutation_evidence"
            message = 'new row for relation "' + table + '" violates check constraint "' + constraint + '"'
    else: message = intended["exact_source_message"]
    output = "psql:<stdin>:88: ERROR:  " + state + ":  " + message + "\n"
    frame = M["expected_frame"](case, BODIES)
    if frame: output += "CONTEXT:  PL/pgSQL function " + frame["function"] + "() line " + str(frame["body_line"]) + " at " + frame["operation"] + "\n"
    return output + "DETAIL:  " + CANARY + "\nLOCATION:  fixed_native_routine, native_source.c:1\n"


class MemoryEvidence:
    def __init__(self):
        self.value = {"status": "IN_PROGRESS", "current_stage": "ENTRY", "current": {}, "results": [], "authentication": [], "transactions": {}}
        self.value["source_modules_sha256"] = {M["COLLECTOR"]: M["sha"]((ROOT / M["COLLECTOR"]).read_bytes())}
        self.saved, self.stages = [], []
    def save(self): self.saved.append(deepcopy(self.value))
    def stage(self, name): self.value["current_stage"] = name; self.stages.append(name); self.save()


class FakeSession:
    def __init__(self, runtime, role): self.runtime, self.role = runtime, role
    def capture(self):
        self.runtime.events.append((self.role, "capture"))
        return {"login": self.role, "pid": "8123", "xid": "987654", "started": "2026-11-17 00:00:00+00"}
    def finish(self, sql):
        self.runtime.events.append((self.role, "finish"))
        self.runtime.submitted.append((self.role, sql))
        if self.role != "wa_app_runtime":
            if self.runtime.privileged_error: raise M["HeldFailure"]("MOCK_PRIVILEGED_FAILURE")
            return self.runtime.privileged_result
        case = next(case for case in PACKET["cases"] if sql.endswith((M["PACKET"] / case["transaction_sql"]).read_text(encoding="utf8")))
        self.runtime.active = case
        if self.runtime.app_error: raise self.runtime.app_error
        lines = list(case["stage_marker_oracle"]["expected_completed_markers"]) + ([ACK] if case["expected_commit"] else [])
        return self.runtime.app_result or (0 if case["expected_commit"] else 3, lines, "" if case["expected_commit"] else error_text(case))
    def close(self):
        self.runtime.events.append((self.role, "close"))
        if self.role == self.runtime.close_failure: raise M["HeldFailure"]("OPERATION_CLOSURE_UNCONFIRMED")


class FakeRuntime:
    container = "b" * 64
    def __init__(self):
        self.events, self.submitted = [], []
        self.active = None
        self.snapshot = {"format": "offline-native-snapshot"}
        self.privileged_result, self.privileged_error = (0, [ACK], ""), False
        self.app_result, self.app_error, self.close_failure = None, None, None
        self.restore_good, self.native_good, self.fresh, self.shape_good = True, True, True, True
    def session(self, role): self.events.append((role, "open")); return FakeSession(self, role)
    def run(self, role, sql):
        if sql == (ROOT / M["COLLECTOR"]).read_text(encoding="utf8"):
            self.events.append((role, "native_observer")); return json.dumps(self.snapshot if self.native_good else {"drift": True})
        contract = PACKET["trusted_setup_trigger_contract"]
        if sql == (M["PACKET"] / contract["observer_sql"]).read_text(encoding="utf8"):
            self.events.append((role, "restoration_observer"))
            value = deepcopy(contract["observer_expected"])
            if not self.restore_good: value["exact_user_trigger_set_and_states"] = False
            return json.dumps(value)
        for case in PACKET["cases"]:
            if sql == (M["PACKET"] / case["observer_sql"]).read_text(encoding="utf8"):
                self.events.append((role, "case_observer"))
                value = deepcopy(case["observer_expected"])
                if not self.shape_good: value[next(iter(value))] = "wrong-type-" + CANARY
                return json.dumps(value)
        if sql.startswith("SELECT NOT EXISTS(SELECT 1 FROM app.customer_profile_lifecycle_event"):
            self.events.append((role, "fresh_observer")); return "t" if self.fresh else "f"
        self.events.append((role, "preflight")); return "t"


class CustomerCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.no_run = patch.object(subprocess, "run", side_effect=AssertionError("UNMOCKED_PROCESS_FORBIDDEN")); self.no_run.start()
        self.no_popen = patch.object(subprocess, "Popen", side_effect=AssertionError("UNMOCKED_PROCESS_FORBIDDEN")); self.no_popen.start()
        self.addCleanup(self.no_run.stop); self.addCleanup(self.no_popen.stop)
        M["load_helpers"]({path: M["sha"]((ROOT / path).read_bytes()) for path in M["SOURCE_MODULES"]})

    def test_every_midrun_observer_and_canonical_read_rejects_drift_before_sql(self):
        original = Path.read_bytes
        restore_file = M["packet_file"](PACKET["trusted_setup_trigger_contract"]["observer_sql"])
        for path, operation in (
            (ROOT / M["COLLECTOR"], lambda runtime, evidence: M["native_observation"]({}, runtime, evidence)),
            (restore_file, lambda runtime, evidence: M["restore_observation"](PACKET, runtime, evidence)),
            (M["packet_file"]("trusted-identity-fixtures.sql"), lambda runtime, evidence: M["fresh_fixture_sql"](PACKET)),
            (ROOT / "review-output/foundation-application.review.sql", lambda runtime, evidence: M["application_sql"](PACKET))):
            runtime, evidence = Mock(), MemoryEvidence()
            def changed(candidate, target=path): return CANARY.encode() if candidate == target else original(candidate)
            with self.subTest(path=path.name), patch.object(Path, "read_bytes", changed):
                with self.assertRaises(M["HeldFailure"]) as found: operation(runtime, evidence)
                self.assertEqual(found.exception.code, "SQL_SOURCE_DRIFT")
            runtime.run.assert_not_called(); runtime.session.assert_not_called()

    def test_midrun_transaction_drift_never_submits_changed_app_sql(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence(); case = PACKET["cases"][0]
        target, original = M["packet_file"](case["transaction_sql"]), Path.read_bytes
        def changed(path): return CANARY.encode() if path == target else original(path)
        with patch.object(Path, "read_bytes", changed), self.assertRaises(M["HeldFailure"]) as found:
            M["execute_case"](case, PACKET, BODIES, runtime, evidence)
        self.assertEqual(found.exception.code, "SQL_SOURCE_DRIFT")
        self.assertNotIn(("wa_app_runtime", "finish"), runtime.events)
        self.assertIn(("wa_app_runtime", "close"), runtime.events)
        self.assertFalse(any(role == "wa_app_runtime" or CANARY in sql for role, sql in runtime.submitted))
        self.assertEqual(evidence.value["results"], [])

    def test_midrun_case_observer_drift_never_executes_changed_privileged_query(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence(); case = PACKET["cases"][0]
        target, original = M["packet_file"](case["observer_sql"]), Path.read_bytes
        def changed(path): return CANARY.encode() if path == target else original(path)
        with patch.object(Path, "read_bytes", changed), self.assertRaises(M["HeldFailure"]) as found:
            M["execute_case"](case, PACKET, BODIES, runtime, evidence)
        self.assertEqual(found.exception.code, "SQL_SOURCE_DRIFT")
        self.assertIn(("wa_app_runtime", "close"), runtime.events)
        self.assertNotIn(("postgres", "case_observer"), runtime.events)
        self.assertEqual(evidence.value["results"], [])

    def test_sql_is_decoded_from_exact_single_verified_byte_read(self):
        raw = b"SELECT 'reviewed';\n"
        path = Mock(); path.read_bytes.side_effect = [raw, CANARY.encode()]
        self.assertEqual(M["verified_sql_text"](path, M["sha"](raw)), raw.decode())
        path.read_bytes.assert_called_once_with(); path.read_text.assert_not_called()
        for expected in (None, "a", "X" * 64):
            bad = Mock()
            with self.assertRaises(M["HeldFailure"]): M["verified_sql_text"](bad, expected)
            bad.read_bytes.assert_not_called()

    def test_midrun_unreadable_sql_failure_discards_exception_canary(self):
        path = Mock(); path.read_bytes.side_effect = OSError(CANARY)
        with self.assertRaises(M["HeldFailure"]) as found: M["verified_sql_text"](path, "a" * 64)
        self.assertEqual(found.exception.code, "SQL_SOURCE_UNREADABLE")
        self.assertNotIn(CANARY, str(found.exception))

    def test_dormant_help_and_missing_authority_never_open_process(self):
        original = runpy.run_path
        with patch.object(runpy, "run_path", side_effect=AssertionError("HELPER_IMPORT_FORBIDDEN")) as helper:
            fresh = original(str(ROOT / "scripts/sql-review/run-customer-control-rehearsal.py"))
            self.assertEqual(fresh["API"], {}); self.assertEqual(fresh["HOST"], {})
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as result: fresh["main"](["--help"])
                self.assertEqual(result.exception.code, 0)
                self.assertEqual(fresh["main"]([]), 1)
            helper.assert_not_called()

    def test_each_drifted_throwing_transitive_helper_rejects_before_runpy_or_canary(self):
        pins = {path: M["sha"]((ROOT / path).read_bytes()) for path in M["SOURCE_MODULES"]}
        original = Path.read_bytes
        for relative in (M["API_PATH"], M["HOST_PATH"], "scripts/sql-review/rehearsal-diagnostics.py", "scripts/prepare-local-f0-history.py"):
            def read(path):
                return ("print('" + CANARY + "'); raise RuntimeError('" + CANARY + "')").encode() if path == ROOT / relative else original(path)
            output = io.StringIO()
            with self.subTest(source=relative), patch.object(Path, "read_bytes", read), patch.object(runpy, "run_path") as execute, redirect_stdout(output):
                with self.assertRaises(M["HeldFailure"]) as result: M["load_helpers"](pins)
                self.assertEqual(result.exception.code, "COORDINATOR_SOURCE_DRIFT")
                execute.assert_not_called()
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(M["API"], {}); self.assertEqual(M["HOST"], {})

    def test_unreadable_source_and_invalid_pin_shapes_reject_before_import(self):
        pins = {path: M["sha"]((ROOT / path).read_bytes()) for path in M["SOURCE_MODULES"]}
        with patch.object(Path, "read_bytes", side_effect=OSError(CANARY)), patch.object(runpy, "run_path") as execute:
            with self.assertRaises(M["HeldFailure"]) as result: M["load_helpers"](pins)
            self.assertEqual(result.exception.code, "COORDINATOR_SOURCE_UNREADABLE"); execute.assert_not_called()
            self.assertNotIn(CANARY, str(result.exception))
        for broken in ({}, {**pins, M["API_PATH"]: True}, {**pins, M["API_PATH"]: "A" * 64}):
            with patch.object(runpy, "run_path") as execute:
                with self.assertRaises(M["HeldFailure"]): M["load_helpers"](broken)
                execute.assert_not_called()

    def test_helper_load_errors_and_unexpected_output_never_escape_sanitization(self):
        pins = {path: M["sha"]((ROOT / path).read_bytes()) for path in M["SOURCE_MODULES"]}
        original_api, original_host = dict(M["API"]), dict(M["HOST"])
        def throwing(path):
            print(CANARY)
            raise RuntimeError(CANARY)
        output = io.StringIO()
        with patch.object(runpy, "run_path", side_effect=throwing), redirect_stdout(output):
            with self.assertRaises(M["HeldFailure"]) as result: M["load_helpers"](pins)
            self.assertEqual(result.exception.code, "REVIEWED_HELPER_LOAD_FAILED")
        self.assertEqual(output.getvalue(), ""); self.assertNotIn(CANARY, str(result.exception))
        self.assertEqual(M["API"], {}); self.assertEqual(M["HOST"], {})
        def noisy(path): print(CANARY); return original_api if path == str(ROOT / M["API_PATH"]) else original_host
        with patch.object(runpy, "run_path", side_effect=noisy), redirect_stdout(output):
            with self.assertRaises(M["HeldFailure"]) as result: M["load_helpers"](pins)
            self.assertEqual(result.exception.code, "REVIEWED_HELPER_OUTPUT_REJECTED")
        self.assertEqual(output.getvalue(), ""); self.assertEqual(M["API"], {}); self.assertEqual(M["HOST"], {})

    def test_unknown_helper_failure_codes_are_fixed_classes(self):
        self.assertEqual(M["failure_code"](M["API"]["HeldFailure"](CANARY)), "AUTHENTICATION_OR_SQL_HELPER_REFUSED")
        self.assertEqual(M["failure_code"](M["HOST"]["HeldFailure"](CANARY)), "RESOURCE_GUARD_REFUSED")
        with patch.dict(M, {"API": {}, "HOST": {}}):
            self.assertEqual(M["failure_code"](RuntimeError(CANARY)), "INVALID_IO_RESPONSE_OR_INTERNAL")

    def test_packet_and_all_existing_statuses_remain_exact(self):
        self.assertEqual(M["sha"]((M["PACKET"] / "fixtures.json").read_bytes()), M["PACKET_SHA256"])
        self.assertEqual(len(PACKET["cases"]), 17)
        self.assertTrue(all(case["status"] == "NOT_RUN" for case in PACKET["cases"]))
        self.assertEqual(PACKET["update_plan"]["execution_dependencies"], PACKET["cas_plan"]["execution_dependencies"])
        self.assertIn("NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED", PACKET["update_plan"]["execution_dependencies"][0])

    def test_source_bound_diagnostic_for_every_prepared_negative(self):
        for case in PACKET["cases"]:
            with self.subTest(case=case["name"]):
                value = M["diagnostic"]("" if case["expected_commit"] else error_text(case), case, BODIES)
                self.assertTrue(value["matched"])
                self.assertNotIn(CANARY, json.dumps(value))
                if case["variation"] in ("missing-evidence", "missing-history"):
                    self.assertEqual(value["sqlstate"], "P0002")
                    self.assertEqual(value["source_frame"]["operation"], "SQL statement")

    def test_diagnostics_reject_wrong_state_message_frame_duplicates_and_controls(self):
        case = next(case for case in PACKET["cases"] if case["variation"] == "missing-history")
        good = error_text(case)
        for bad in (good.replace("P0002", "P0001"), good.replace("query returned no rows", "other failure"),
                    good.replace("customer_atomic", "foreign_function"), good.replace("line 7", "line 8"),
                    good + good, good.replace("ERROR:", "ERROR[malformed]:"), "'" + good.splitlines()[0] + "'\n",
                    good.replace("ERROR:", "\x1b[31mERROR:"), good + "\x1b]0;" + CANARY + "\x07",
                    good + "WARNING:  " + CANARY + "\n", good.replace("CONTEXT:", "CONTEXT_BAD:")):
            with self.subTest(bad=bad[:45]): self.assertFalse(M["diagnostic"](bad, case, BODIES)["matched"])
        self.assertTrue(M["diagnostic"](good.replace("\n", "\r\n"), case, BODIES)["matched"])
        positive = PACKET["cases"][0]
        self.assertFalse(M["diagnostic"](CANARY, positive, BODIES)["matched"])

    def test_only_reviewed_outer_begin_is_removed_and_commit_retained(self):
        setup = (M["PACKET"] / "trusted-identity-fixtures.sql").read_text(encoding="utf8")
        tail = M["captured_transaction_tail"](setup)
        self.assertNotIn("\nBEGIN;", tail)
        self.assertTrue(tail.endswith("COMMIT;\n"))
        self.assertEqual(tail.count("DISABLE TRIGGER owner_commit"), 2)
        self.assertEqual(tail.count("ENABLE TRIGGER owner_commit"), 2)
        for value in ("SELECT 1;", "BEGIN; SELECT 1;", "BEGIN; BEGIN; COMMIT;", "BEGIN; ROLLBACK;", "BEGIN; COMMIT; SELECT 1;"):
            with self.subTest(value=value):
                with self.assertRaises(M["HeldFailure"]): M["captured_transaction_tail"](value)

    def test_freshness_observer_is_readonly_and_covers_all_fixture_ids(self):
        query = M["fresh_fixture_sql"](PACKET)
        statement = parse_sql(query)
        self.assertEqual(len(statement), 1); self.assertIsInstance(statement[0].stmt, ast.SelectStmt)
        for case in PACKET["cases"]:
            self.assertTrue(all(identity in query for key, identity in case["ids"].items() if key != "user"))
        self.assertIn("FROM app.user_security_profiles", query); self.assertIn("FROM app.users", query)
        self.assertNotIn("DISABLE", query)

    def test_each_case_has_separate_committed_issuer_and_close_before_observe(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence()
        for case in PACKET["cases"]:
            runtime.events = []
            M["execute_case"](case, PACKET, BODIES, runtime, evidence)
            events = runtime.events
            self.assertLess(events.index(("wa_app_runtime", "capture")), events.index(("wa_context_issuer", "open")))
            self.assertLess(events.index(("wa_context_issuer", "close")), events.index(("wa_app_runtime", "finish")))
            self.assertLess(events.index(("wa_app_runtime", "close")), events.index(("postgres", "restoration_observer")))
            self.assertLess(events.index(("postgres", "restoration_observer")), events.index(("postgres", "case_observer")))
        self.assertEqual(len(evidence.value["results"]), 17)
        self.assertTrue(all(row["status"] == "PASS_SCENARIO_ONLY_NOT_SELECTED_CONTROL" for row in evidence.value["results"]))
        encoded = json.dumps(evidence.value)
        for forbidden in (CANARY, "8123", "987654", "token_hash", "INSERT INTO", "RAISE EXCEPTION"):
            self.assertNotIn(forbidden, encoded)

    def test_issuer_no_ack_stops_before_bind_but_closes_app_and_checks_restoration(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence()
        runtime.privileged_result = (0, [], "")
        with self.assertRaises(M["HeldFailure"]): M["execute_case"](PACKET["cases"][0], PACKET, BODIES, runtime, evidence)
        self.assertNotIn(("wa_app_runtime", "finish"), runtime.events)
        self.assertIn(("wa_app_runtime", "close"), runtime.events)
        self.assertIn(("postgres", "restoration_observer"), runtime.events)
        self.assertNotIn(("postgres", "case_observer"), runtime.events)
        self.assertFalse(evidence.value["transactions"][PACKET["cases"][0]["name"] + "/issuer"]["commit_acknowledged"])

    def test_unexpected_app_exception_closes_before_restoration_no_counts_or_leak(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence()
        runtime.app_error = subprocess.TimeoutExpired(CANARY, 1)
        with self.assertRaises(subprocess.TimeoutExpired): M["execute_case"](PACKET["cases"][0], PACKET, BODIES, runtime, evidence)
        self.assertTrue(evidence.value["current"]["operation_closed"])
        self.assertIn(("postgres", "restoration_observer"), runtime.events)
        self.assertNotIn(("postgres", "case_observer"), runtime.events)
        self.assertNotIn(CANARY, json.dumps(evidence.value))

    def test_unconfirmed_app_closure_prevents_restoration_and_counts(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence(); runtime.close_failure = "wa_app_runtime"
        with self.assertRaises(M["HeldFailure"]): M["execute_case"](PACKET["cases"][0], PACKET, BODIES, runtime, evidence)
        self.assertFalse(evidence.value["current"]["operation_closed"])
        self.assertNotIn(("postgres", "restoration_observer"), runtime.events)
        self.assertNotIn(("postgres", "case_observer"), runtime.events)

    def test_exact_marker_ack_exit_and_observer_oracles_fail_closed(self):
        positive, negative = PACKET["cases"][:2]
        for case, result in ((positive, (0, positive["stage_marker_oracle"]["expected_completed_markers"], "")),
                             (positive, (0, positive["stage_marker_oracle"]["expected_completed_markers"] + [ACK, ACK], "")),
                             (negative, (3, negative["stage_marker_oracle"]["expected_completed_markers"] + [ACK, ACK], error_text(negative))),
                             (negative, (3, negative["stage_marker_oracle"]["expected_completed_markers"][:-1], error_text(negative))),
                             (negative, (2, negative["stage_marker_oracle"]["expected_completed_markers"], error_text(negative))),
                             (positive, (0, positive["stage_marker_oracle"]["expected_completed_markers"] + [ACK, CANARY], ""))):
            with self.subTest(case=case["name"], result=result[0]):
                runtime, evidence = FakeRuntime(), MemoryEvidence(); runtime.app_result = result
                with self.assertRaises(M["HeldFailure"]): M["execute_case"](case, PACKET, BODIES, runtime, evidence)
                self.assertEqual(evidence.value["results"], [])
                self.assertNotIn(CANARY, json.dumps(evidence.value))
        runtime, evidence = FakeRuntime(), MemoryEvidence(); runtime.shape_good = False
        with self.assertRaises(M["HeldFailure"]): M["execute_case"](positive, PACKET, BODIES, runtime, evidence)
        self.assertNotIn(CANARY, json.dumps(evidence.value))

    def test_full_subset_is_bounded_and_authentication_preflight_is_not_skipped(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence()
        with patch.dict(M["API"], {"authentication_preflight": lambda *args: evidence.value["authentication"].append({"mock_only": True})}):
            M["run_subset"](PACKET, runtime.snapshot, PACKET["cases"], runtime, evidence)
        self.assertEqual(len(evidence.value["results"]), 17)
        self.assertEqual(evidence.value["status"], "PASS_PREPARED_CREATE_SUBSET_ONLY_CONTROLS_NOT_RUN")
        self.assertTrue(evidence.value["authentication"])
        self.assertTrue(evidence.value["fresh_synthetic_ids_verified"])
        self.assertEqual(runtime.events.count(("postgres", "native_observer")), 2)

    def test_native_or_freshness_failure_stops_before_setup(self):
        for flag in ("native_good", "fresh"):
            runtime, evidence = FakeRuntime(), MemoryEvidence(); setattr(runtime, flag, False)
            with patch.dict(M["API"], {"authentication_preflight": lambda *args: None}):
                with self.assertRaises(M["HeldFailure"]): M["run_subset"](PACKET, runtime.snapshot, PACKET["cases"], runtime, evidence)
            self.assertFalse(any(event[1] == "open" for event in runtime.events))

    def test_setup_error_requires_confirmed_close_before_restoration(self):
        for close_failure in (None, "postgres"):
            runtime, evidence = FakeRuntime(), MemoryEvidence(); runtime.privileged_error = True; runtime.close_failure = close_failure
            with patch.dict(M["API"], {"authentication_preflight": lambda *args: None}):
                with self.assertRaises(M["HeldFailure"]): M["run_subset"](PACKET, runtime.snapshot, PACKET["cases"], runtime, evidence)
            self.assertEqual(runtime.events.count(("postgres", "restoration_observer")), 2 if close_failure is None else 1)
            self.assertNotIn(("wa_app_runtime", "open"), runtime.events)

    def test_first_unexpected_case_stops_all_later_cases(self):
        runtime, evidence = FakeRuntime(), MemoryEvidence(); runtime.app_result = (3, [], CANARY)
        with patch.dict(M["API"], {"authentication_preflight": lambda *args: None}):
            with self.assertRaises(M["HeldFailure"]): M["run_subset"](PACKET, runtime.snapshot, PACKET["cases"], runtime, evidence)
        self.assertEqual(runtime.events.count(("wa_app_runtime", "open")), 1)
        self.assertEqual(evidence.value["results"], [])

    def test_real_transport_uses_immutable_id_tuple_and_independent_closure(self):
        class Input(io.StringIO):
            def close(self): self.saved = self.getvalue(); super().close()
        class Process:
            def __init__(self):
                self.stdin = Input(); self.returncode = None
                self.stdout = io.StringIO(M["TUPLE_PREFIX"] + json.dumps({"login": "wa_app_runtime", "pid": "8123", "xid": "987654", "started": "2026-11-17 00:00:00+00"}) + "\n" + ACK + "\n")
                self.stderr = io.StringIO("")
            def wait(self, timeout): self.returncode = 0; return 0
            def poll(self): return self.returncode
        process, checks = Process(), []
        with patch.object(subprocess, "Popen", return_value=process) as start:
            session = M["Session"]("wa_app_runtime", "b" * 64, lambda role, sql: checks.append((role, sql)) or "0")
            backend = session.capture(); self.assertEqual(backend["pid"], "8123")
            self.assertEqual(session.finish("COMMIT;"), (0, [ACK], "")); session.close()
        argv = start.call_args.args[0]
        self.assertIn("b" * 64, argv); self.assertIn("PGPASSFILE=/run/wa-secrets/pgpass", argv)
        self.assertNotIn("PGPASSWORD", argv); self.assertIn("ON_ERROR_STOP=1", argv)
        self.assertEqual(len(checks), 1); self.assertIn("backend_start=", checks[0][1]); self.assertIn("pid=8123", checks[0][1])
        self.assertLess(process.stdin.saved.index("COMMIT;"), process.stdin.saved.index(ACK))

    def test_unlisted_or_nonimmutable_transport_refused_before_process(self):
        for role, container in (("service_role", "b" * 64), ("wa_worker", "b" * 64), ("wa_app_runtime", "wa-p0c-name"), ("wa_app_runtime", "b" * 12)):
            with self.assertRaises(M["HeldFailure"]): M["Session"](role, container, lambda *args: "0")

    def test_reviewed_plan_pins_and_source_binding_are_required(self):
        helper = runpy.run_path(str(ROOT / "scripts/check-local-f0-migrate.py"))
        target = helper["fixture"]()[0]
        target["source"]["integrated_sql_sha256"] = PACKET["source_inputs_sha256"]["review-output/foundation-application.review.sql"]
        snapshot = {"format": "workinants.native-catalog.v1", "server_version_num": 170011, "read_only": True, "collected_as": "postgres", "collector_is_superuser": True}
        comparison = {"format": "workinants.catalog-comparison.v1", "status": "PASS", "source_expected_sha256": "a" * 64, "native_snapshot_sha256": M["sha"](M["canonical"](snapshot).encode())}
        with tempfile.TemporaryDirectory(prefix="offline-customer-plan-", dir=ROOT.parent) as folder:
            folder = Path(folder); sp, cp = folder / "native.json", folder / "comparison.json"
            sp.write_text(json.dumps(snapshot), encoding="utf8"); cp.write_text(json.dumps(comparison), encoding="utf8")
            plan = {"schema": "workinants.customer-control-run.v1", "scope": "REVIEWED_LOCAL_CUSTOMER_CREATE_SUBSET_ONLY", "reviewed_packet_sha256": M["PACKET_SHA256"],
                    "source_modules_sha256": {path: M["sha"]((ROOT / path).read_bytes()) for path in M["SOURCE_MODULES"]}, "target_manifest": target,
                    "native_snapshot": {"path": str(sp), "sha256": M["sha"](sp.read_bytes())}, "native_comparison": {"path": str(cp), "sha256": M["sha"](cp.read_bytes()), "source_expected_sha256": "a" * 64},
                    "scenario_names": [case["name"] for case in PACKET["cases"]]}
            self.assertEqual(len(M["load_inputs"](plan)[2]), 17)
            variants = []
            for key, value in (("scope", "UNKNOWN"), ("reviewed_packet_sha256", "0" * 64), ("scenario_names", list(reversed(plan["scenario_names"]))), ("scenario_names", [PACKET["update_plan"]["name"]])):
                changed = deepcopy(plan); changed[key] = value; variants.append(changed)
            changed = deepcopy(plan); changed["source_modules_sha256"][M["API_PATH"]] = "0" * 64; variants.append(changed)
            changed = deepcopy(plan); changed["native_comparison"]["source_expected_sha256"] = "0" * 64; variants.append(changed)
            changed = deepcopy(plan); changed["native_snapshot"]["sha256"] = "0" * 64; variants.append(changed)
            changed = deepcopy(plan); changed["source_modules_sha256"]["unknown"] = "0" * 64; variants.append(changed)
            for changed in variants:
                with self.assertRaises(M["HeldFailure"]): M["load_inputs"](changed)

    def test_main_retains_sanitized_stop_and_never_overwrites_evidence(self):
        with tempfile.TemporaryDirectory(prefix="offline-customer-stop-", dir=ROOT.parent) as folder:
            folder = Path(folder); plan_path = folder / "plan.json"; evidence_path = folder / "evidence"
            plan = {"target_manifest": {}, "source_modules_sha256": {}, "scenario_names": ["mock"], "native_snapshot": {"sha256": "a" * 64}, "native_comparison": {"sha256": "b" * 64}}
            plan_path.write_text(json.dumps(plan), encoding="utf8")
            events = []
            def stop(*args):
                events.append("run_subset")
                evidence = args[-1]; evidence.stage("MOCK_BOUNDARY")
                raise RuntimeError(CANARY)
            dependencies = {"load_inputs": lambda plan: (PACKET, {}, []), "resource_identity": lambda target: "b" * 64, "runtime": lambda identity: object(), "run_subset": stop}
            argv = ["--execute-reviewed-customer-controls", "--reviewed-run-plan", str(plan_path), "--evidence-directory", str(evidence_path)]
            output = io.StringIO()
            with redirect_stdout(output): self.assertEqual(M["main"](argv, dependencies), 1)
            data = json.loads((evidence_path / "customer-control-results.json").read_text(encoding="utf8"))
            self.assertEqual(data["failure"], {"code": "INVALID_IO_RESPONSE_OR_INTERNAL", "stage": "MOCK_BOUNDARY"})
            self.assertTrue(data["subsequent_cases_stopped"]); self.assertTrue(data["cleanup_required"])
            self.assertTrue(all(row["status"] == "NOT_RUN" for row in data["selected_controls"]))
            self.assertNotIn(CANARY, output.getvalue() + json.dumps(data))
            before = (evidence_path / "customer-control-results.json").read_bytes()
            with redirect_stdout(io.StringIO()): self.assertEqual(M["main"](argv, dependencies), 1)
            self.assertEqual(events, ["run_subset"])
            self.assertEqual((evidence_path / "customer-control-results.json").read_bytes(), before)


if __name__ == "__main__": unittest.main()
