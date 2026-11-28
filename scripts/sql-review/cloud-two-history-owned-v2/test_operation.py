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


if __name__ == "__main__":
    unittest.main()
