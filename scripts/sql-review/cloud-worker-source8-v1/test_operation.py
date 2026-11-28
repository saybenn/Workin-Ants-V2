"""Exercise the exact Worker owner seam and child with pipes and a SQL model."""

from copy import deepcopy
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import operation
import prepare
import worker_child as child


CID = "a" * 64
BIRTH = "2026-11-28T04:20:00Z"
RUN = "d546522f-cf32-4d59-a8e6-61b5b1aabb09"
WIRE = """import sys
line = sys.stdin.readline().strip()
if line == 'DENY':
    print('typed benign test refusal', file=sys.stderr)
    sys.exit(3)
if line == 'NO_REMOTE_RECEIPT':
    sys.exit(125)
"""


def offline_session_file():
    return (prepare.ROOT / child.PIPE).read_bytes()


class Pipes(unittest.TestCase):
    def modeled_session(self, role):
        session, stopped = child.pipe_class({child.PIPE: offline_session_file()})
        coordinator = SimpleNamespace(
            spawn=mock.Mock(side_effect=lambda _: subprocess.Popen(
                [sys.executable, "-u", "-c", WIRE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, bufsize=0, shell=False)),
            socket_checked=mock.Mock(), uncertain=mock.Mock(), require_backend_absent=mock.Mock(),
        )
        self.coordinator = coordinator
        value = session(role, coordinator)
        value.backend = {"pid": "31", "login": role, "started": "2026-11-28 04:20:00+00"}
        return value, stopped

    def test_known_code3_closes_but_unknown_exit_never_becomes_a_verdict(self):
        session, _ = self.modeled_session("wa_worker")
        self.assertEqual(session.call("DENY"), ([], False, "typed benign test refusal\n"))
        self.assertEqual(session.close(), 3)
        self.coordinator.require_backend_absent.assert_called_once_with("wa_worker", session.backend)
        self.coordinator.uncertain.assert_not_called()

        session, stopped = self.modeled_session("wa_worker")
        with self.assertRaisesRegex(stopped, "APP_SESSION_EXIT_UNCONFIRMED"):
            session.call("NO_REMOTE_RECEIPT")
        self.coordinator.uncertain.assert_called_once()
        self.coordinator.require_backend_absent.assert_not_called()
        self.assertFalse(session.closed)
        self.assertTrue(all(stream.closed for stream in (session.process.stdin, session.process.stdout, session.process.stderr)))

    def test_migrator_cannot_spawn_and_identity_bootstrap_has_its_own_scope(self):
        with self.assertRaisesRegex(RuntimeError, "APP_LOGIN_SCOPE"):
            self.modeled_session("wa_migrator")
        self.coordinator.spawn.assert_not_called()
        worker = SimpleNamespace(role="wa_worker", closed=False)
        c = SimpleNamespace(sessions=[worker], concurrent_old=worker, identity_scope=False,
                            evidence=SimpleNamespace(value={"current_case": None}))
        with self.assertRaisesRegex(child.Hold, "WORKER_IDENTITY_SETUP_SCOPE"):
            child.admit_slot(c, "wa_identity_service_authority")
        with self.assertRaisesRegex(child.Hold, "WORKER_UNDECLARED_OVERLAP"):
            child.admit_slot(c, "wa_worker")
        c.evidence.value["current_case"] = "real-higher-fence-reclaim-with-retained-effect"
        child.admit_slot(c, "wa_worker")
        c.sessions = [worker, SimpleNamespace(role="wa_worker", closed=False),
                      SimpleNamespace(role="wa_context_issuer", closed=False)]
        with self.assertRaisesRegex(child.Hold, "WORKER_SESSION_CAP"):
            child.admit_slot(c, "postgres")

    def test_only_exact_worker_clock_accepts_fractional_timeout(self):
        basis, _, two = operation.mechanism()
        S = basis.S
        leaves = {name: (prepare.ROOT / name).read_bytes() for name in (S.OPERATOR, S.STEPS, f"{prepare.PACKET}/A-clock.sql")}
        p = two.reviewed_program(prepare.ROOT, leaves)
        io = p.NativeIO()
        io.Popen = mock.Mock(side_effect=lambda *_args, **_options: subprocess.Popen(
            [sys.executable, "-u", "-c", "import sys; sys.stdin.buffer.read(); print('clock observer model')"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, shell=False))
        owner = SimpleNamespace(name="modeled", program=p, blobs=leaves, transport=p.Transport(prepare.ROOT, io),
            docker=SimpleNamespace(argv=lambda *args: ["gitless-clock-model", "--config", "/modeled", "--host",
                                                        "unix:///var/run/docker.sock", *args]),
            psql_args=lambda _, role: ["exec", "-i", CID, "psql", "-v", "SHOW_CONTEXT=never", "-U", role])
        operation.install_clock_transport(owner, S)
        args = owner.psql_args(owner.name, "postgres")
        args[args.index("SHOW_CONTEXT=never")] = "SHOW_CONTEXT=errors"
        exact = owner.docker.argv(*args)
        sql = leaves[f"{prepare.PACKET}/A-clock.sql"]
        for bad_args, payload, timeout, profile in ((exact, b"foreign", 0.55, "control"),
                (exact, sql, 0.55, "metadata_tools"), (exact, sql, 5.1, "control"),
                ([*exact, "extra"], sql, 1.0, "control"), (exact, sql, float("nan"), "control")):
            with self.assertRaisesRegex(S.Held, "WORKER_CLOCK_LITERAL_SCOPE"):
                owner.transport.binary(bad_args, payload, timeout, profile)
        io.Popen.assert_not_called()
        self.assertEqual(owner.transport.binary(exact, sql, 1.25).stdout, b"clock observer model\n")
        self.assertTrue(owner.transport.observations[-1]["remote_exec_attempted"])
        self.assertTrue(owner.transport.observations[-1]["closure_confirmed"])
        self.assertFalse(owner.transport.unknown)


class LiveGate(unittest.TestCase):
    def test_fresh_same_owner_full8_boundary_and_unknown_veto(self):
        source = prepare.common(prepare.ROOT)
        raw = b"MODELED_PACKET"
        native = {"applied_rows": 2, "catalog_check_counts": {"PASS": 29089}, "ledger_checks": 22,
                  "oracle_expressions": 416, "native_sha256": "c" * 64}
        receipts = [{"operation": verb, "exit_code": 0, "container_id": CID, "run_id": RUN,
                     "packet_sha256": source.sha(raw), "no_pending_message_observed": verb == "deploy"}
                    for verb in ("deploy", "status", "deploy")]
        owner = SimpleNamespace(
            raw=raw, name="modeled", resources=SimpleNamespace(cid=CID, volume_birth=BIRTH),
            transport=SimpleNamespace(unknown=False),
            program=SimpleNamespace(STATE=dict.fromkeys(("first_deploy_closed_success", "finalization_verified",
                                                         "two_applied_verified", "activated"), True)),
            operation={"run_id": RUN, "worker_source8": {"prior_closed_cid": "e" * 64,
                        "held_proof": {"prior_closed_machinery": {"run_id": "historical"}}}},
            report={"worker_source8": {"status": "NOT_RUN"}, "migration_results": receipts,
                    "native_results": {"initial": native, "noop": deepcopy(native)},
                    "targets": {"modeled": {"finalization": "PASS", "volume_created_at": BIRTH}}},
        )
        self.assertEqual(operation.require_fresh(owner, source), (receipts[0], native["native_sha256"]))
        for key, value in (("container_id", "f" * 64), ("packet_sha256", "b" * 64), ("exit_code", True)):
            changed = deepcopy(owner)
            changed.report["migration_results"][2][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(source.Held, "WORKER_FRESH_SOURCE8_NOT_PROVED"):
                operation.require_fresh(changed, source)
        owner.operation["worker_source8"]["prior_closed_cid"] = CID
        with self.assertRaises(source.Held):
            operation.require_fresh(owner, source)
        owner.operation["worker_source8"]["prior_closed_cid"] = "e" * 64
        owner.transport.unknown = True
        with self.assertRaises(source.Held):
            operation.require_fresh(owner, source)

    def test_no_matching_review_stops_before_owner_construction(self):
        with mock.patch.object(operation, "read_closed") as read:
            self.assertEqual(operation.main(["execute", "--packet", "/tmp/not-an-owner"]), 1)
        read.assert_not_called()

    def test_closed_child_birth_and_first_failure_are_checked_before_global_closure(self):
        source = prepare.common(prepare.ROOT)
        P = SimpleNamespace(private_path=lambda path, file: path)
        Owner = operation.owner_type((SimpleNamespace(S=source, P=P), None, SimpleNamespace(Owner=object)))
        native_hash, raw = "f" * 64, b"MODELED_LITERAL"
        identity = {"run_id": RUN, "container_id": CID, "volume_created_at": BIRTH, "source_commit": "c" * 40,
                    "source_tree": "d" * 40, "packet_sha256": source.sha(raw)}
        comparison = {"status": "PASS", "check_counts": {"PASS": 29089}, "findings": [],
                      "source_expected_sha256": prepare.CATALOG, "native_snapshot_sha256": native_hash}
        for mode in ("WRONG_BIRTH", "MISSING_BIRTH", "STOPPED"):
            with self.subTest(mode=mode):
                owner = Owner()
                owner.operation = {"run_id": RUN, "source": {"commit": "c" * 40, "tree": "d" * 40}}
                owner.raw, owner.name = raw, "modeled"
                owner.resources = SimpleNamespace(cid=CID, volume_birth=BIRTH)
                owner.observed_target = lambda: identity.copy()
                owner.report = {"worker_source8": {}, "stage": operation.STAGE}
                owner.transport = SimpleNamespace(unknown=False)
                owner.previous_artifact = lambda leaf: (comparison if leaf.endswith("catalog-comparison.json") else {}, native_hash)
                retained = {**identity, "schema": child.RESULT_SCHEMA, "status": child.PASS, "results": []}
                if mode == "MISSING_BIRTH":
                    del retained["volume_created_at"]
                elif mode == "WRONG_BIRTH":
                    retained["volume_created_at"] = "2000-01-01T00:00:00Z"
                else:
                    retained["status"] = child.STOPPED
                    retained["unexpected"] = [{"stage": "FINITE_WORKER_PROTOCOL", "code": "INTENDED_SOURCE_GUARD_REQUIRED"}]
                trail = []

                def close(_, stage):
                    owner.report["stage"] = "REQUIRED_GLOBAL_BACKEND_CLOSURE"
                    trail.append(("close", stage))
                    if stage == "WORKER_POST_CHILD":
                        raise source.Held("MODELED_UNCONFIRMED_CLOSE")

                p = SimpleNamespace(
                    OUT=Path("/tmp/modeled-worker"), STATE={"origins": {}}, digest=lambda _: native_hash,
                    write_safe=mock.Mock(), save=mock.Mock(), best_effort_save=mock.Mock(), Stop=child.Hold,
                    closed_bytes=lambda path: (source.encode(retained), "MODELED_ORIGIN"), closed_backends=close,
                    _latch_first_failure=lambda stage, code: trail.append(("latch", stage, code)),
                    record_failure=lambda stage, code: trail.append(("secondary", stage, code)),
                )
                owner.program = p
                first = "WORKER_CHILD_STOPPED" if mode == "STOPPED" else "WORKER_CHILD_REFERENCE_UNCONFIRMED"
                with mock.patch.object(operation, "require_fresh", return_value=({}, native_hash)), \
                        mock.patch.object(child, "coordinate", return_value=retained), \
                        mock.patch.object(child, "verify_complete") as verify, self.assertRaisesRegex(child.Hold, first):
                    owner.run_worker()
                verify.assert_not_called()
                self.assertEqual(trail, [("close", "WORKER_PRE_CHILD"), ("latch", operation.STAGE, first),
                                         ("close", "WORKER_POST_CHILD"),
                                         ("secondary", "WORKER_POST_CHILD", "WORKER_CHILD_CLOSURE_UNCONFIRMED")])
                self.assertEqual(owner.report["stage"], operation.STAGE)
                self.assertIs(owner.report["worker_source8"]["global_client_closure"], False)
                if mode == "STOPPED":
                    self.assertEqual(owner.report["worker_source8"]["child"]["sha256"], source.sha(source.encode(retained)))
                else:
                    self.assertEqual(owner.report["worker_source8"]["child_reference"], "UNCONFIRMED")

    def test_verified_source_postcheck_keeps_transport_uncertainty_separate(self):
        source = prepare.common(prepare.ROOT)
        Owner = operation.owner_type((SimpleNamespace(S=source, P=None), None, SimpleNamespace(Owner=object)))
        owner = Owner()
        owner.directory, owner.operation, owner.raw, owner.reviews = Path("/tmp/modeled"), {}, b"literal", {}
        owner.report = {"status": "PASS_MACHINERY_SUBSET_ONLY", "worker_source8": {"status": child.PASS}}
        owner.transport = SimpleNamespace(unknown=True)
        owner.program = SimpleNamespace(record_failure=mock.Mock())
        with mock.patch.object(operation, "read_closed", return_value=((None, {}), None, b"literal")), \
                mock.patch.object(operation, "reviews_for", return_value={}):
            owner.postchecks()
        self.assertEqual(owner.report["immutable_source_postcheck"], "PASS")
        self.assertIs(owner.report["postcheck_remote_uncertainty_retained"], True)
        owner.program.record_failure.assert_called_once_with("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")

    def test_postproof_observes_fresh_parity_and_vetoes_each_drift(self):
        native, ledger, state, fingerprints = object(), object(), object(), object()
        checks = {"applied_rows": 2, "catalog_check_counts": {"PASS": 29089}, "ledger_checks": 22,
                  "oracle_expressions": 416}
        for after_native, after_ledger, after_state in ((native, ledger, state), (object(), ledger, state),
                                                       (native, object(), state), (native, ledger, object())):
            fresh = mock.Mock(return_value=(after_native, after_ledger))
            compare = mock.Mock(return_value={"full8": "MODELED"})
            owner = SimpleNamespace(
                program=SimpleNamespace(qualify=fresh, fingerprints=mock.Mock(return_value=fingerprints),
                                        CATALOG={"two": SimpleNamespace(compare_noop=compare)}),
                report={"native_results": {operation.POST: checks}},
            )
            with mock.patch.object(operation, "state_observation", side_effect=[state, after_state]) as observe:
                if after_native is native and after_ledger is ledger and after_state is state:
                    self.assertEqual(operation.qualify_after(owner, "installed", {}, {}, native, ledger, fingerprints),
                                     (checks, {"full8": "MODELED"}))
                else:
                    with self.assertRaisesRegex(child.Hold, "WORKER_POST_NATIVE_LEDGER_DRIFT"):
                        operation.qualify_after(owner, "installed", {}, {}, native, ledger, fingerprints)
            self.assertEqual(observe.call_count, 2)
            fresh.assert_called_once_with("installed", operation.POST)
            compare.assert_called_once_with(fingerprints, fingerprints)


class FiniteChild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof, _ = prepare.build()
        cls.source = prepare.common(prepare.ROOT)
        cls.blobs = {relative: (prepare.ROOT / relative).read_bytes()
                     for relative in {*cls.proof["published_worker_files_sha256"],
                                      *cls.proof["preparation_source_files_sha256"], *child.PINS}}
        cls.packet = cls.source.unique_json(cls.blobs[prepare.FIXTURE])
        cls.model = runpy.run_path(str(prepare.ROOT / "scripts/check-worker-recovery-control-coordinator.py"))
        cls.native = {"triggers": [{"table_name": table, "name": "owner_commit", "enabled": "O", "internal": False}
                                   for table in cls.packet["fixture_tables"]]}

    def project(self, fail_case=None):
        model = self.model["Transport"](self.packet)
        model.fail_case = fail_case
        source = self.source
        p = SimpleNamespace(all_secrets=[], digest=self.model["P"].digest, exact=self.model["P"].exact)
        report = {"authentication": [], "auth_comparisons": [], "effective_hba_selections": [
            {"role": role, "address": address, "rule_number": 5, "method": "scram-sha-256"}
            for role in child.AUTH_ROLES for address in ("127.0.0.1", "::1")
        ]}

        def auth_roles(roles, active):
            self.assertIs(active, True)
            for role in roles:
                report["authentication"].append({"role": role, "correct_password": "PASS_SCRAM",
                                                 "wrong_password": "PASS_REJECTED", "actual_connection_closed": True})
                report["auth_comparisons"].append({"role": role, "checks": dict.fromkeys(child.AUTH_FIELDS, True)})

        p.hba_preflight = mock.Mock()
        p.auth_roles = auth_roles

        def raw(*args, input, timeout, **_):
            result = model.raw(["exec", *args], input=input.decode(), timeout=timeout)
            return SimpleNamespace(returncode=result.returncode, stdout=result.stdout.encode(), stderr=result.stderr.encode())

        class ModeledSession:
            def __new__(cls, role, coordinator):
                child.admit_slot(coordinator, role)
                return model.session(role, coordinator)

        owner = SimpleNamespace(
            blobs=self.blobs, program=p, operation={"worker_source8": {"held_proof": self.proof}, "run_id": RUN,
                "source_pins": {name: source.sha(data) for name, data in self.blobs.items()},
                "source": {"commit": "c" * 40, "tree": "d" * 40}},
            name="modeled", read_source=self.blobs.__getitem__, target={}, raw=b"MODELED_ONLY",
            resources=SimpleNamespace(cid=CID, volume_birth=BIRTH), report=report, transport=SimpleNamespace(unknown=False),
            docker=SimpleNamespace(socket_identity=lambda: "MODELED_SOCKET", origin="MODELED_SOCKET"),
            psql_args=lambda _, role: ["exec", "-i", CID, "psql", "-v", "SHOW_CONTEXT=never", "-U", role],
            exact_container_exec=raw, observed_target=lambda: {"container_id": CID, "volume_created_at": BIRTH},
        )
        columns = runpy.run_path(str(prepare.ROOT / child.CONTEXT))["GRANT_COLUMNS"]
        real = child.compiled

        def capture(nodes, label, namespace):
            result = real(nodes, label, namespace)
            if label == child.COORDINATOR:
                original = result["coordinator_type"]

                def wrapped(context, base):
                    class Tracked(original(context, base)):
                        def __init__(self, *args):
                            super().__init__(*args)
                            self.context_columns = columns
                            model.coordinator = self

                    return Tracked

                result["coordinator_type"] = wrapped
            return result

        with tempfile.TemporaryDirectory() as work, mock.patch.object(child, "compiled", side_effect=capture), \
                mock.patch.object(child, "pipe_class", return_value=(ModeledSession, child.Hold)), \
                mock.patch.object(child, "time", SimpleNamespace(monotonic=model.clock, sleep=model.sleep)), \
                mock.patch.object(subprocess, "Popen", side_effect=AssertionError("PROCESS_FORBIDDEN")), \
                mock.patch.object(socket.socket, "connect", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            path = Path(work) / "modeled-worker"
            value = child.coordinate(owner, self.native, path, source)
            raw_value = (path / "worker-recovery-results.json").read_bytes()
            self.assertEqual(source.unique_json(raw_value), value)
            self.assertNotIn(self.model["CANARY"].encode(), raw_value)
        return owner, model, value

    def test_all21_model_controls_and_closed_guard_observations(self):
        owner, model, value = self.project()
        self.assertEqual(value["status"], child.PASS, value.get("unexpected"))
        self.assertEqual([case["case"] for case in value["results"]], self.proof["ordered_cases"])
        self.assertTrue(all(session.closed for session in model.sessions))
        self.assertEqual(sum(session.role == "wa_identity_service_authority" for session in model.sessions), 1)
        self.assertGreater(model.clock_calls, 0)
        self.assertEqual(value["volume_created_at"], BIRTH)
        summary = child.verify_complete(owner, value, self.model["P"].digest(self.native), self.source)
        self.assertEqual(summary["completed_protocols"], 21)
        self.assertEqual(summary["grants_retained"], 33)
        self.assertEqual(summary["component_report_sha256"], self.model["P"].digest(value))
        with self.assertRaisesRegex(child.Hold, "WORKER_CHILD_REFERENCE_UNCONFIRMED"):
            child.verify_complete(owner, {**value, "volume_created_at": "2000-01-01T00:00:00Z"},
                                  self.model["P"].digest(self.native), self.source)

    def test_discard_unexpected_response_and_stop_later_cases(self):
        _, model, value = self.project(fail_case=self.proof["ordered_cases"][1])
        self.assertEqual(value["status"], child.STOPPED)
        self.assertTrue(value["subsequent_cases_stopped"])
        self.assertEqual(len(value["results"]), 1)
        self.assertTrue(all(session.closed for session in model.sessions))
        self.assertEqual(model.clock_calls, 0)


if __name__ == "__main__":
    unittest.main()
