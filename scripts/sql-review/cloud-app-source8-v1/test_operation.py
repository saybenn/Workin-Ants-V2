"""Offline closed transport, App protocol and owner boundary tests."""

import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import app_child
import host_session
import operation
import prepare


TRANSCRIPT = r"""
import re, sys, time
for line in sys.stdin:
    if line == 'OK\n':
        print('one record', flush=True)
    elif line == 'DENY\n':
        print('ERROR:  42501: reviewed test refusal', file=sys.stderr, flush=True)
        sys.exit(3)
    elif line == 'OVERFLOW\n':
        print('x' * 65537, flush=True)
    elif line == 'STALL\n':
        time.sleep(30)
    elif line == '\\q\n':
        sys.exit(0)
    else:
        ack = re.fullmatch(r"SELECT '(WA_CLOUD_APP_ACK\|[a-f0-9]{32})';\n", line)
        if ack:
            print(ack[1], flush=True)
"""


class Pipes(unittest.TestCase):
    def session(self, role="wa_app_runtime"):
        self.transport = SimpleNamespace(
            spawn=mock.Mock(side_effect=lambda _: subprocess.Popen(
                [sys.executable, "-u", "-c", TRANSCRIPT], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, bufsize=0, shell=False)),
            socket_checked=mock.Mock(), uncertain=mock.Mock(), require_backend_absent=mock.Mock(),
        )
        session = host_session.BoundedSession(role, self.transport)
        session.backend = {"pid": "23", "login": role, "started": "2026-11-28 04:20:00+00"}
        return session

    def test_app_transport_refuses_worker_and_migrator_before_spawn(self):
        for role in ("wa_worker", "wa_migrator", "wa_identity_service_authority"):
            with self.assertRaisesRegex(host_session.SessionStop, "APP_LOGIN_SCOPE"):
                self.session(role)
            self.transport.spawn.assert_not_called()

    def test_acknowledged_output_then_exact_backend_observer(self):
        session = self.session()
        self.assertEqual(session.call("OK"), (["one record"], True, ""))
        self.assertEqual(session.close(), 0)
        self.transport.require_backend_absent.assert_called_once_with(session.role, session.backend)
        self.transport.uncertain.assert_not_called()

    def test_terminal_refusal_carries_bounded_complete_stderr_in_memory(self):
        session = self.session()
        self.assertEqual(session.call("DENY"), ([], False, "ERROR:  42501: reviewed test refusal\n"))
        self.assertEqual(session.close(), 3)
        self.assertTrue(session.closed)
        self.transport.require_backend_absent.assert_called_once()

    def test_overflow_and_stall_latch_unknown_and_prohibit_new_queries(self):
        for payload, code in (("OVERFLOW", "APP_SESSION_OUTPUT_LIMIT"), ("STALL", "APP_SESSION_DEADLINE")):
            with self.subTest(code=code), mock.patch.object(host_session, "CALL_SECONDS", 0.15):
                session = self.session()
                with self.assertRaisesRegex(host_session.SessionStop, code):
                    session.call(payload)
                self.transport.uncertain.assert_called_once_with(code)
                with self.assertRaisesRegex(host_session.SessionStop, code):
                    session.call("OK")
                with self.assertRaisesRegex(host_session.SessionStop, code):
                    session.close()
                self.transport.require_backend_absent.assert_not_called()
                self.assertIsNotNone(session.process.poll())

    def test_no_local_exit_substitutes_for_an_actual_backend_check(self):
        session = self.session()
        session.call("OK")
        self.transport.require_backend_absent.side_effect = host_session.SessionStop("EXACT_BACKEND_STILL_LIVE")
        with self.assertRaisesRegex(host_session.SessionStop, "EXACT_BACKEND_STILL_LIVE"):
            session.close()
        self.assertFalse(session.closed)
        self.transport.uncertain.assert_called_once_with("EXACT_BACKEND_STILL_LIVE")

    def test_failure_evidence_exception_cannot_bypass_local_pipe_and_process_cleanup(self):
        session = self.session()
        self.transport.uncertain.side_effect = OSError("first failure recorder unavailable in model")
        with self.assertRaisesRegex(host_session.SessionStop, "APP_SESSION_OUTPUT_LIMIT"):
            session.call("OVERFLOW")
        self.assertIsNotNone(session.process.poll())
        self.assertTrue(all(stream.closed for stream in (session.process.stdin, session.process.stdout, session.process.stderr)))


class AppProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = prepare.prepare()
        cls.files = {relative: (prepare.ROOT / relative).read_bytes()
                     for relative in {*cls.proof["source_files_sha256"], app_child.CONTEXT,
                                      app_child.SCOPED_READ, app_child.COLLECTOR}}
        cls.packet = json.loads(cls.files[f"{prepare.PACKET}/fixtures.json"])
        cls.native = json.loads((prepare.ROOT / operation.TWO_EVIDENCE / "evidence/noop-native-before.json").read_bytes())
        cls.model = runpy.run_path(str(prepare.ROOT / "scripts/check-app-write-two-unexpected-diagnostic-v3-coordinator.py"))

    def test_effective_diagnostic_admits_74_and_discards_raw_text(self):
        protocol = app_child.render_protocol(self.files, self.proof)
        response = ("ERROR:  23514: APP_UNPERSISTED_DIAGNOSTIC_CANARY\n"
                    "CONTEXT:  PL/pgSQL function platform_private.runtime_transition() line 74 at RAISE\n")
        value = protocol["unexpected_business_diagnostic"](response, self.files[prepare.INITIAL].decode())
        self.assertEqual(protocol["validate_unexpected_diagnostic"](value)["source_frame"], {
            "function": prepare.RUNTIME_TRANSITION, "source_body_sha256": prepare.NEW_FRAME[0], "source_body_line": 74,
        })
        self.assertNotIn("CANARY", json.dumps(value))
        self.assertIsNone(protocol["unexpected_business_diagnostic"](response.replace("line 74", "line 75"),
                         self.files[prepare.INITIAL].decode())["source_frame"])

    def project(self, failed=None):
        model = self.model["Transport"](self.packet)
        model.business_error_placement = failed
        cid, birth = "b" * 64, "2000-01-01T00:00:00Z"
        socket = "MODELED_OFFLINE_SOCKET"
        report = {
            "authentication": [{"role": role, "correct_password": "PASS_SCRAM", "wrong_password": "PASS_REJECTED",
                                "actual_connection_closed": True} for role in app_child.APP_ROLES],
            "auth_comparisons": [{"role": role, "checks": {"modeled": True}} for role in app_child.APP_ROLES],
        }

        def raw(*args, input, **_):
            result = model.raw(["exec", *args], input=input.decode())
            return SimpleNamespace(returncode=result.returncode, stdout=result.stdout.encode(), stderr=result.stderr.encode())

        class ModeledSession:
            def __new__(cls, role, coordinator):
                return model.model(role, coordinator)

        owner = SimpleNamespace(
            blobs=self.files, program=SimpleNamespace(strict_json=json.loads, all_secrets=[]),
            operation={"app_source8": {"held_source_proof": self.proof}, "run_id": str(operation.TWO_RUN),
                       "source_pins": {name: prepare.sha(raw) for name, raw in self.files.items()},
                       "source": {"commit": "c" * 40, "tree": "d" * 40}},
            name="offline", read_source=self.files.__getitem__, target={}, raw=b"OFFLINE_ONLY", root=prepare.ROOT,
            resources=SimpleNamespace(cid=cid, volume_birth=birth), report=report, transport=SimpleNamespace(unknown=False),
            docker=SimpleNamespace(socket_identity=lambda: socket, origin=socket), exact_container_exec=raw,
            psql_args=lambda _, role: ["exec", "-i", cid, "psql", "-v", "SHOW_CONTEXT=never", "-U", role],
            observed_target=lambda: {"container_id": cid, "volume_created_at": birth},
        )
        # Reuse the published SQL projection model before exercising any Linux pipe code.
        # The model needs its coordinator even for observations before the first session.
        real = app_child.execute_ast

        def track(nodes, relative, namespace):
            result = real(nodes, relative, namespace)
            if relative == prepare.COORDINATOR:
                original = result["coordinator_type"]

                def bound(*args):
                    cls = original(*args)

                    class Coordinator(cls):
                        def __init__(self, *options, **kwargs):
                            super().__init__(*options, **kwargs)
                            model.coordinator = self

                    return Coordinator

                result["coordinator_type"] = bound
            return result

        with (tempfile.TemporaryDirectory() as root,
              mock.patch.object(app_child, "BoundedSession", ModeledSession),
              mock.patch.object(app_child, "execute_ast", side_effect=track)):
            result = app_child.coordinate(owner, self.native, Path(root) / "app-source8")
        return result, model

    def test_full_production_protocol_keeps_order_and_exact_claims_offline(self):
        value, model = self.project()
        self.assertEqual(value["status"], app_child.APP_PASS, value.get("first_failure"))
        self.assertTrue(operation.receipt_scope(value, self.proof))
        self.assertTrue(all(session.closed for session in model.models))
        operations = value["operations"]
        stages = {row.get("case"): index for index, row in enumerate(operations)
                  if row["stage"] == "RESTRICTED_APP_TRANSACTION"}
        schedule = next(index for index, row in enumerate(operations) if row["stage"] == "GENUINE_APP_SCHEDULE_PREREQUISITE")
        self.assertLess(stages[prepare.R1], stages[prepare.READS[0]])
        self.assertLess(stages[prepare.READS[-1]], schedule)
        self.assertLess(schedule, stages[prepare.R2])

    def test_terminal_app_failure_preserves_r2_boundary_and_raw_output_exclusion(self):
        value, model = self.project("commit")
        self.assertEqual(len(value["results"]), 13)
        self.assertEqual(value["first_failure"]["code"], "ACKNOWLEDGED_SOURCE_COMMIT_REQUIRED")
        self.assertEqual(value["first_failure"]["case"], prepare.R2)
        self.assertTrue(all(session.closed for session in model.models))
        self.assertNotIn("CANARY", json.dumps(value))
        self.assertFalse(operation.receipt_scope(value, self.proof))


class Boundaries(unittest.TestCase):
    def test_finalization_call_cannot_substitute_for_resource_cleanup(self):
        source = (prepare.ROOT / prepare.TWO_STEPS).read_bytes()
        self.assertTrue(operation.exact_cleanup_seam(source))
        self.assertFalse(operation.exact_cleanup_seam(source.replace(b"try:cleanup()", b"try:ensure_cleanup()")))

    def test_no_owner_construction_without_exact_approval_switch(self):
        with (mock.patch.object(operation, "read_closed") as reader, mock.patch("builtins.print"),
              mock.patch.object(operation, "owner_type") as owner):
            self.assertEqual(operation.main(["execute", "--packet", "/workspace/scratch/missing"]), 1)
        reader.assert_not_called()
        owner.assert_not_called()

    def test_source8_exact_event_is_only_first_entry_point(self):
        class Base:
            def configure_program(self):
                self.program = SimpleNamespace(event=mock.Mock(), save=mock.Mock(), SAFE_FAILURE_CODES=set(),
                                               SAFE_FAILURE_STAGES=set())

        owner = operation.owner_type((SimpleNamespace(S=None, P=None), None, SimpleNamespace(Owner=Base)))()
        owner.report = {}
        owner.run_app = mock.Mock(side_effect=host_session.SessionStop("APP_FRESH_SOURCE8_NOT_PROVED"))
        owner.configure_program()
        owner.program.event("NOOP", "UNCONFIRMED")
        owner.program.event("STATUS", "PASS_CLOSED_CLI_NOT_NOOP_PROOF")
        owner.run_app.assert_not_called()
        with self.assertRaisesRegex(host_session.SessionStop, "APP_FRESH_SOURCE8_NOT_PROVED"):
            owner.program.event(*operation.SEAM_EVENT)
        owner.run_app.assert_called_once()
        self.assertEqual(owner.report["app_source8"]["status"], "STOPPED_OR_UNCONFIRMED")


if __name__ == "__main__":
    unittest.main()
