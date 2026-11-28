"""Closed offline stage, receipt, and Cloud capability tests."""

from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import basis
import operation


S = basis.S


class LogicalPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs, _ = S.historical_sources(basis.ROOT)
        for name in basis.CAPABILITY_FILES:
            path = f"{basis.CAPABILITY}/{name}"
            cls.blobs[path] = S.read(basis.ROOT / path)

    def test_actual_capability_scoped_and_closed(self):
        source, result, audit = basis.capability(self.blobs)
        self.assertEqual(source["purpose"], "CLOUD_F0_CAPABILITY_PROBE_ONLY")
        self.assertEqual(source["source"]["commit"], "fc5b5879abb5bd764fc0e5f5c1a03f95e2b0b7c8")
        self.assertEqual(result["assertion_promotions"], 0)
        self.assertTrue(audit["absent_after"]["container_id"])
        modified = dict(self.blobs)
        modified[f"{basis.CAPABILITY}/result.json"] = S.encode({**result, "remote_outcome_unconfirmed": True})
        with self.assertRaisesRegex(S.Held, "ACTUAL_CAPABILITY_AND_INDEPENDENT_CLOSURE_REQUIRED"):
            basis.capability(modified)

    def model(self, temporary, fail=False):
        program = operation.reviewed_program(basis.ROOT, self.blobs)
        outer_names = {"preflight", "create_resources", "cleanup", "launch", "source13_process"}
        self.assertTrue(outer_names.isdisjoint(program.__dict__))
        history = []
        snapshot = {"native": "frozen"}
        witness = {"history_expected": [1, 2]}
        ledger = {"observation": "same"}
        result = {"no_pending_message_observed": True}

        def visit(stage, value=None):
            def run(*args):
                history.append(stage)
                return value
            return run

        def migrate(action, label):
            history.append(label)
            if fail:
                raise program.Stop("GENUINE_PRISMA_OPERATION_FAILED")
            return result

        def collect(name, stage, filename):
            self.assertEqual(name, "synthetic-target")
            history.append(stage)
            return snapshot

        def qualify(*_):
            history.append("qualify")
            program.report["native_results"] = {"initial": {"native_checks": 29089}}
            return snapshot, ledger

        def finalize():
            if "finalized" not in history:
                history.append("finalized")
            program.STATE["finalization_verified"] = True

        def activate():
            self.assertTrue(program.STATE["first_deploy_closed_success"])
            self.assertTrue(program.STATE["finalization_verified"])
            self.assertTrue(program.STATE["two_applied_verified"])
            history.append("activate")

        program.__dict__.update(
            OUT=temporary / "evidence", report={"stage": "ENTRY", "status": "IN_PROGRESS", "events": [], "unexpected": []},
            EXPECTED_SHA=S.EXPECTED, TARGETS=[{"name": "synthetic-target"}], RUN_ID="synthetic-run",
            COMMIT="a" * 40, TREE="b" * 40, PACKET="c" * 64, all_secrets=[],
            created_containers={"synthetic-target": "d" * 64}, bootstrap_attempted={"synthetic-target"},
            FIRST_OPERATION_FAILURE=None, TRANSPORT=SimpleNamespace(observations=[], unknown=False),
            verify_packet=visit("verify_packet"), preflight=visit("preflight"), ensure_image=visit("ensure_image"),
            create_resources=visit("create_resources"), provision_tools=visit("provision_tools"),
            bootstrap=visit("bootstrap"), migrate=migrate, ensure_cleanup=finalize, collect_native=collect,
            ledger_observation=visit("initial_ledger", (witness, ledger)),
            compare_ledger=visit("compare_ledger", ({"checks": [1]}, {})),
            write_safe=visit("artifact"), activate_runtime=activate, qualify=qualify,
            fingerprints=lambda prefix: visit(prefix, {"same": True})(),
            qualify_noop=visit("qualify_noop", (snapshot, ledger)), secret_scan=visit("sanitization"),
            cleanup=visit("cleanup"), postchecks=visit("postchecks"), verify_references=visit("verify_references"),
        )
        program.CATALOG["two"] = SimpleNamespace(compare_noop=visit("compare_noop", {"complete": True}))
        return program, history

    def test_inherited_sequence_gates_activation_and_repeat_deploy(self):
        with tempfile.TemporaryDirectory() as directory:
            p, history = self.model(Path(directory))
            with mock.patch("builtins.print"):
                self.assertEqual(p.main(), 0)
            self.assertEqual(history, [
                "verify_packet", "preflight", "ensure_image", "create_resources", "provision_tools", "bootstrap",
                "GENUINE_TWO_FILE_DEPLOY", "finalized", "NATIVE_INITIAL_LEDGER_BEFORE", "initial_ledger",
                "NATIVE_INITIAL_LEDGER_AFTER", "compare_ledger", "artifact", "activate", "qualify", "before-noop",
                "GENUINE_STATUS", "GENUINE_SECOND_DEPLOY", "after-noop", "compare_noop", "qualify_noop", "artifact",
                "sanitization", "cleanup", "postchecks", "verify_references",
            ])

    def test_first_failure_keeps_required_cleanup_and_prevents_later_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            p, history = self.model(Path(directory), fail=True)
            with mock.patch("builtins.print"):
                self.assertEqual(p.main(), 1)
            self.assertEqual(p.report["primary_failure"]["code"], "GENUINE_PRISMA_OPERATION_FAILED")
            self.assertEqual(history[-5:], ["finalized", "sanitization", "cleanup", "postchecks", "verify_references"])
            self.assertNotIn("activate", history)
            self.assertNotIn("GENUINE_SECOND_DEPLOY", history)

    def test_unknown_client_closure_vetoes_every_later_sql_request(self):
        owner = object.__new__(operation.Owner)
        owner.program = operation.reviewed_program(basis.ROOT, self.blobs)
        owner.program.report = {"stage": "ENTRY"}
        owner.transport = SimpleNamespace(unknown=True)
        owner.docker = mock.Mock()
        with self.assertRaisesRegex(owner.program.Stop, "FINALIZATION_UNKNOWN_TRANSPORT"):
            owner.command([], "SELECT 1")
        owner.docker.run.assert_not_called()

    def test_cleanup_name_absence_does_not_hide_a_renamed_owned_id(self):
        owner = object.__new__(operation.Owner)
        owner.report = {"steps": {}}
        owner.program = SimpleNamespace(event=mock.Mock())
        owner.resources = SimpleNamespace(cid="e" * 64, cleanup=mock.Mock(), require_daemon=mock.Mock())
        owner.docker = SimpleNamespace(container_create_dispatched=True,
                                      run=mock.Mock(return_value=SimpleNamespace(stdout=b"e" * 64 + b"\n")))
        with self.assertRaisesRegex(S.Held, "FULL_CONTAINER_ABSENCE_UNCONFIRMED"):
            owner.cleanup()
        owner.program.event.assert_not_called()
        self.assertEqual(owner.report["cleanup"], "FULL_CONTAINER_ABSENCE_UNCONFIRMED")
        owner.docker.run.assert_called_once_with("container", "ls", "-a", "--no-trunc", "--format", "{{.ID}}")

    def test_explicit_and_exact_approval_precede_owner_construction(self):
        with mock.patch.object(operation, "read_closed", side_effect=S.Held("EXACT_COMMITTED_PLAN_REQUIRED")) as reader:
            with mock.patch.object(operation, "Owner") as owner, mock.patch("builtins.print"):
                self.assertEqual(operation.main(["--packet", "/workspace/scratch/test"]), 1)
                reader.assert_not_called()
                self.assertEqual(operation.main([operation.CONTROL_APPROVAL,
                                                 "--packet", "/workspace/scratch/test"]), 1)
                reader.assert_called_once()
                owner.assert_not_called()

    def test_copied_tree_proves_implicit_directories_and_file_modes(self):
        path = "/run/wa-f0-source/scripts/a.mjs"
        rows = ("d|/run/wa-f0-source|0|0|0|755|3\n"
                "d|/run/wa-f0-source/scripts|0|0|0|755|2\n"
                "f|/run/wa-f0-source/scripts/a.mjs|4|0|0|444|1\n").encode()
        expected = {path: (4, "444")}
        self.assertEqual(operation.validate_inventory(rows, expected), {"regular_files": 1, "directories": 2})
        with self.assertRaisesRegex(S.Held, "CLOUD_COPIED_INVENTORY_METADATA"):
            operation.validate_inventory(rows.replace(b"|755|2", b"|775|2"), expected)
        with self.assertRaisesRegex(S.Held, "CLOUD_COPIED_INVENTORY_METADATA"):
            operation.validate_inventory(rows.replace(b"|755|2\n", b"|755|2\r\n"), expected)
        with self.assertRaisesRegex(S.Held, "CLOUD_COPIED_INVENTORY_DRIFT"):
            operation.validate_inventory(rows.replace(b"a.mjs", b"b.mjs"), expected)

    def test_terminal_refusal_preserves_only_validated_fixed_provenance(self):
        code = "TREE_OWNER_MODE"
        inner = SimpleNamespace(REFUSAL_SCHEMA="workinants.cloud-f0-runtime-lease-history-refusal.v2",
                                CLOSED_REFUSAL_PHASE_CODES={"LOCAL_GUARD": (code,)},
                                REFUSAL_CAUSE_CODES={"OTHER": "INVALID_LOCAL_INPUT_OR_IO"})
        manifest = {"run_id": "run"}
        observed = {"container_id": "c" * 64, "daemon": {"daemon_id": "actual-daemon"}}
        raw = b"private exact typed attestation source"
        authorization = {"packet_sha256": "p" * 64, "literal_review_sha256": "b" * 64}
        complete = {
            "schema": inner.REFUSAL_SCHEMA, "status": "REFUSED_OR_INCOMPLETE", "phase": "LOCAL_GUARD",
            "cause_family": "HELD_GUARD", "code": code, "child_dispatch": "NOT_ATTEMPTED",
            "operation": "deploy", "raw_output_discarded": True, "database_qualification_claimed": False,
            "attestation_sha256": S.sha(raw), "run_id": "run", "container_id": "c" * 64, "daemon_id": "actual-daemon",
            **authorization,
        }

        def invoke(value, stderr=b""):
            result = SimpleNamespace(returncode=1, stderr=stderr, stdout=S.encode(value))
            return operation.validate_result(result, None, manifest, observed, "deploy", raw, authorization, inner)

        with self.assertRaises(operation.InnerRefusal) as caught:
            invoke(complete)
        self.assertEqual(caught.exception.receipt, {
            "phase": "LOCAL_GUARD", "cause_family": "HELD_GUARD", "code": code,
            "reported_child_dispatch": "NOT_ATTEMPTED", "transport_uncertainty_cleared": False,
            "verified_receipt_fields": ["attestation_sha256", "container_id", "daemon_id", "literal_review_sha256",
                                        "packet_sha256", "run_id"],
        })
        with self.assertRaisesRegex(S.Held, "CLOUD_INNER_REFUSAL_BINDING"):
            invoke({**complete, "packet_sha256": "x" * 64})
        with self.assertRaisesRegex(S.Held, "CLOUD_INNER_REFUSAL_RESPONSE_SHAPE"):
            invoke({**complete, "code": "ATTACKER_SUPPLIED_DETAIL"})
        with self.assertRaisesRegex(S.Held, "CLOUD_RUNNER_RESPONSE"):
            invoke(complete, stderr=b"raw diagnostic is not eligible")

    def test_validated_inner_refusal_vetoes_actual_safety_sql_and_later_stages(self):
        receipt = {"phase": "LOCAL_GUARD", "code": "TREE_OWNER_MODE"}
        cid = "d" * 64
        with tempfile.TemporaryDirectory() as directory:
            p, history = self.model(Path(directory))
            owner = object.__new__(operation.Owner)
            owner.program, owner.report, owner.transport = p, p.report, p.TRANSPORT
            owner.name, owner.directory, owner.raw = "synthetic-target", Path(directory), b"packet"
            owner.nested, owner.files, owner.archive, owner.manifest = b"manifest", {}, b"archive", {}
            owner.reviews, owner.receipt_validator = {"literal": "e" * 64}, None
            owner.inner = SimpleNamespace(BASE="test", OP_ARG="--test", attest=mock.Mock(return_value=b"stdin"))
            owner.observed_target = mock.Mock(return_value={"container_id": cid})
            owner.exact_container_exec, owner.docker = mock.Mock(), mock.Mock()
            p.migrate, p.command = owner.migrate, owner.command
            p.RESOURCE_CONTAINERS = (owner.name,)
            p.psql_args = mock.Mock(return_value=[cid, "-U", "postgres"])
            p.ensure_cleanup = lambda: p.finalize(owner.name)
            p.SAFE_FAILURE_CODES |= {"CLOUD_INNER_TERMINAL_REFUSAL", "FINALIZATION_UNKNOWN_TRANSPORT"}
            owner.manifest["tools"] = {"files_sha256": {"node/bin/node": "f" * 64}}
            with (mock.patch.object(operation, "compare_source8"),
                  mock.patch.object(operation.B, "copied_paths", return_value={}),
                  mock.patch.object(operation.B, "verify_source_copy"),
                  mock.patch.object(operation.B, "verify_source_lengths"),
                  mock.patch.object(operation, "validate_result", side_effect=operation.InnerRefusal(receipt)),
                  mock.patch("builtins.print")):
                self.assertEqual(p.main(), 1)
            self.assertEqual(p.report["primary_failure"], {
                "stage": "GENUINE_TWO_FILE_DEPLOY", "code": "CLOUD_INNER_TERMINAL_REFUSAL",
            })
            self.assertEqual(p.report["inner_cli_closure"]["bounded_terminal_refusal"], receipt)
            self.assertNotIn("migration_results", p.report)
            self.assertTrue(p.TRANSPORT.unknown)
            self.assertFalse(p.report["backend_closures"][-1]["observation_completed"])
            self.assertEqual(owner.exact_container_exec.call_count, 3)
            owner.docker.run.assert_not_called()
            self.assertEqual(history[-4:], ["sanitization", "cleanup", "postchecks", "verify_references"])
            self.assertNotIn("activate", history)

    def test_postcheck_does_not_conflate_source_integrity_and_runtime_uncertainty(self):
        owner = object.__new__(operation.Owner)
        owner.directory, owner.raw, owner.operation, owner.reviews = Path("/held"), b"held", {"v": 2}, {"v": 2}
        owner.report = {"status": "STOPPED_ATTEMPT_PRESERVED"}
        owner.transport = SimpleNamespace(unknown=True)
        owner.program = SimpleNamespace(record_failure=mock.Mock())
        with (mock.patch.object(operation, "read_closed", return_value=((Path("/held"), {"v": 2}), b"held")),
              mock.patch.object(operation, "exact_reviews", return_value={"v": 2})):
            owner.postchecks()
        owner.program.record_failure.assert_not_called()
        self.assertTrue(owner.transport.unknown)
        self.assertEqual(owner.report["immutable_source_postcheck"], "PASS")
        self.assertTrue(owner.report["postcheck_remote_uncertainty_retained"])


if __name__ == "__main__":
    unittest.main()
