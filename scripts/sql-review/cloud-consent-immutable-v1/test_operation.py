from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import child
import operation
import prepare
import protocol
from test_prepare import EXACT_DIAGNOSTIC, FIXTURE_RUN


class OfflineChild:
    def __init__(self, packet, assets, *, wrong_diagnostic=False, unclosed=False, residue=False):
        self.packet, self.assets = packet, assets
        self.wrong_diagnostic, self.unclosed, self.residue = wrong_diagnostic, unclosed, residue
        self.identity_seeded = False
        self.calls, self.failures, self.sessions = [], [], []
        self.native = {"modeled_catalog": True}
        self.program = SimpleNamespace(all_secrets=[], save=mock.Mock(), digest=lambda value: protocol.sha(protocol.canonical(value)),
                                       record_failure=lambda stage, code: self.failures.append((stage, code)),
                                       write_safe=self.write)
        identity = {"run_id": "3d7742e7-b9be-43c2-8972-ecd75f32e524", "source": operation.APP_SOURCE}
        self.resources = SimpleNamespace(cid="a" * 64, volume_birth="2026-11-28T05:10:10Z")
        blobs = {name: (prepare.ROOT / name).read_bytes() for name in (
            child.APP_CHILD, prepare.APP_TRANSPORT, prepare.CONTEXT, prepare.NATIVE_COLLECTOR)}
        self.owner = SimpleNamespace(
            root=prepare.ROOT, name="modeled-container", operation=identity, program=self.program, blobs=blobs,
            raw=b"OFFLINE_TEST_ONLY", resources=self.resources,
            report={"consent_immutable": {}, "authentication": [
                {"role": role, "correct_password": "PASS_SCRAM", "wrong_password": "PASS_REJECTED",
                 "actual_connection_closed": True} for role in child.ROLES],
                "auth_comparisons": [{"role": role, "checks": {"modeled_exact": True}} for role in child.ROLES]},
            transport=SimpleNamespace(unknown=False), docker=SimpleNamespace(origin="model", socket_identity=lambda: "model",
                                                                            remote_unknown=False),
            observed_target=lambda: {"container_id": self.resources.cid, "volume_created_at": self.resources.volume_birth},
            psql_args=lambda name, role: ["exec", "-i", self.resources.cid, "psql", "SHOW_CONTEXT=never", "-U", role],
            exact_container_exec=self.raw,
        )

    def write(self, leaf, payload):
        self.written = deepcopy(payload)
        return {"path": "noop-" + leaf, "sha256": protocol.sha(protocol.canonical(payload))}

    def raw(self, *args, input, **keywords):
        text, role = input.decode(), args[-1]
        self.calls.append(("observer", role))
        if text == protocol.GLOBAL_CLIENTS:
            output = "0"
        elif text == self.assets["trigger-observer.sql"]:
            output = json.dumps(protocol.TRIGGERS)
        elif text == self.owner.blobs[prepare.NATIVE_COLLECTOR].decode():
            output = json.dumps(self.native)
        elif text in [self.assets[name] for name in ("fresh-namespace.sql", "identity-present.sql")] or any(
                text == self.assets[f"{name}/zero-case-residue.sql"] for name in protocol.CASES):
            output = "t"
        elif "all_immutable_fields_equal" in text:
            self.calls.append(("issuer-retention", role))
            output = json.dumps({"exact_count": text.count("g.token_hash IS NOT DISTINCT"), "all_immutable_fields_equal": True,
                                 "issuer_owned": True, "revoked_false": True, "unexpired": True})
        elif text.startswith("SELECT jsonb_agg(jsonb_build_object('table'"):
            self.calls.append(("observe42", role))
            contaminate = self.residue and "ARRAY[]::uuid[]" not in text
            state = []
            for name in self.packet["full42_tables"]:
                changed = ((self.identity_seeded and name in ("app.users", "app.user_security_profiles"))
                           or (contaminate and name == "app.consent_logs"))
                state.append({"table": name, "count": int(changed), "sha256": ("a" if changed else "f") * 64})
            output = json.dumps(state)
        else:
            raise AssertionError("unknown modeled observer recipe")
        return SimpleNamespace(returncode=0, stdout=output.encode(), stderr=b"")

    def run(self):
        model = self
        transport, adapter = child.supports(self.owner.blobs)

        class Pipe:
            def __init__(self, role, coordinator):
                self.role, self.coordinator = role, coordinator
                self.active = self.closed = False
                self.backend = self.exit_code = None
                self.index = len(model.sessions) + 10
                self.process = SimpleNamespace(poll=lambda: self.exit_code)
                model.sessions.append(self)

            def call(self, text):
                if text.startswith("BEGIN ISOLATION LEVEL READ COMMITTED;"):
                    return [], True, ""
                if text.startswith("SELECT 'WA_CTX01_TUPLE|'"):
                    value = {"login": self.role, "current_user": self.role, "database": "wa_p0c_rehearsal",
                             "isolation": "read committed", "pid": str(self.index), "xid": str(self.index + 100),
                             "started": "2026-11-28 04:50:00+00", "clock": "2026-11-28 04:50:01+00"}
                    return ["WA_CTX01_TUPLE|" + json.dumps(value)], True, ""
                if text.startswith("INSERT INTO platform.database_action_grant "):
                    model.calls.append(("issuer-commit", self.role))
                    return [json.dumps({"created_at": "2026-11-28T04:50:02+00:00"})], True, ""
                if text.startswith("SELECT platform_private.bind_request_context("):
                    model.calls.append(("bind", self.role))
                    return [], True, ""
                if text.strip().startswith("ALTER TABLE app.users DISABLE TRIGGER owner_commit;"):
                    model.calls.append(("identity-setup", self.role))
                    model.identity_seeded = True
                    return [], True, ""
                for name in protocol.CASES:
                    for leaf, value in [("publisher.sql", protocol.PREFIX_OBSERVATION),
                                        ("presentation.sql", protocol.PREFIX_OBSERVATION),
                                        ("preread.sql", protocol.PREREAD_OBSERVATION)]:
                        if text == model.assets[f"{name}/{leaf}"]:
                            model.calls.append((leaf, self.role))
                            return [json.dumps(value)], True, ""
                    if text == model.assets[f"{name}/deny.sql"]:
                        model.calls.append((name, self.role))
                        self.exit_code = 3
                        errors = EXACT_DIAGNOSTIC if not model.wrong_diagnostic else "DETAIL: discarded-credential-canary\n"
                        return [protocol.markers(name)[0]], False, errors
                raise AssertionError("unknown modeled positive recipe")

            def close(self):
                model.calls.append(("backend-close", self.role))
                if self.role == "wa_app_runtime" and model.unclosed:
                    raise transport.SessionStop("EXACT_BACKEND_STILL_LIVE")
                self.closed = True
                return 0 if self.exit_code is None else self.exit_code

        transport.BoundedSession = Pipe
        with mock.patch.object(child, "supports", return_value=(transport, adapter)):
            return child.coordinate(self.owner, self.native, self.packet, self.assets)[1]


class OwnerOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.assets = prepare.assemble(FIXTURE_RUN)

    def test_exact_child_models_six_bound_grants_and_two_distinct_transactions(self):
        model = OfflineChild(self.packet, self.assets)
        actual = model.run()
        self.assertTrue(operation.child_passes(actual))
        self.assertEqual(actual, model.written)
        self.assertEqual(model.failures, [])
        self.assertEqual([row["issued_grants_exact"] for row in actual["results"]], [3, 6])
        self.assertEqual(model.calls.count(("issuer-commit", "wa_context_issuer")), 6)
        self.assertEqual(model.calls.count(("bind", "wa_app_runtime")), 6)
        self.assertEqual(model.calls.count(("backend-close", "wa_app_runtime")), 2)
        self.assertEqual(model.calls.count(("identity-setup", "postgres")), 1)
        self.assertEqual(model.calls.count(("observe42", "postgres")), 4)
        self.assertEqual(len([session for session in model.sessions if session.role == "wa_app_runtime"]), 2)
        self.assertFalse(model.owner.transport.unknown)
        data = protocol.canonical(actual)
        self.assertTrue(all(secret.encode() not in data for secret in model.program.all_secrets))
        observed = deepcopy(actual)
        observed["results"][0]["tables_unchanged"] = 41
        self.assertFalse(operation.child_passes(observed))

    def test_exact_first_failure_survives_sticky_unconfirmed_session(self):
        model = OfflineChild(self.packet, self.assets, wrong_diagnostic=True, unclosed=True)
        actual = model.run()
        self.assertFalse(operation.child_passes(actual))
        self.assertEqual(actual["first_failure"], {"stage": "EXPECTED_CONSENT_GUARD", "case": "null-context",
                                                   "code": "CONSENT_EXPECTED_GUARD_UNCONFIRMED"})
        self.assertTrue(actual["remote_outcome_unconfirmed"] and model.owner.docker.remote_unknown)
        self.assertFalse(actual["complete_final_client_closure"])
        self.assertEqual(model.calls[-1], ("backend-close", "wa_app_runtime"))
        self.assertNotIn(("empty-context", "wa_app_runtime"), model.calls)
        self.assertNotIn(b"discarded-credential-canary", protocol.canonical(actual))

    def test_known_transport_but_changed_full_state_stops_second_case(self):
        model = OfflineChild(self.packet, self.assets, residue=True)
        result = model.run()
        self.assertEqual(result["first_failure"]["code"], "CONSENT_ROLLBACK_PARITY_UNCONFIRMED")
        self.assertFalse(result["remote_outcome_unconfirmed"])
        self.assertTrue(result["complete_final_client_closure"])
        self.assertNotIn(("empty-context", "wa_app_runtime"), model.calls)

    def test_proven_app_owner_independent_acceptance_and_two_cleanup_seam(self):
        basis, _, _ = operation.mechanism()
        S = basis.S
        blobs = {f"{operation.APP_EVIDENCE}/{name}": S.read(prepare.ROOT / operation.APP_EVIDENCE / name)
                 for name in (*operation.APP_RAW, operation.APP_ACCEPTANCE, operation.APP_CLOSURE)}
        info, _ = operation.prior_app(blobs, S)
        self.assertEqual(info["source"], operation.APP_SOURCE)
        self.assertTrue(operation.owning_seam(S.read(prepare.ROOT / S.STEPS)))
        self.assertFalse(operation.owning_seam(b"def main():\n try:\n  event()\n finally:\n  cleanup()\n"))

    def test_execute_without_explicit_gate_never_attempts_packet_or_docker(self):
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.object(operation, "read_closed") as packet:
            self.assertEqual(operation.main(["execute", "--packet", "/nonexistent/operation.json"]), 1)
        packet.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())["code"], "CONSENT_EXPLICIT_REVIEWED_EXECUTION_REQUIRED")

    def outer(self):
        model = OfflineChild(self.packet, self.assets)
        result = model.run()
        reference = {"path": "noop-" + child.RESULT_LEAF, "sha256": protocol.sha(protocol.canonical(result))}
        basis, two_plan, _ = operation.mechanism()
        cls = operation.owner_type((basis, two_plan, SimpleNamespace(Owner=object)))
        owner = cls.__new__(cls)
        owner.raw = model.owner.raw
        owner.operation = model.owner.operation | {"consent_immutable": {
            "prior_app_cid": "b" * 64, "recipe": self.packet, "recipe_sha256": protocol.sha(protocol.canonical(self.packet)),
        }}
        owner.resources, owner.name, owner.consent_assets = model.resources, model.owner.name, self.assets
        owner.transport = SimpleNamespace(unknown=False)
        native, ledger, full8 = model.native, {"verified_rows": 2}, {"all_eight_columns_unchanged": True}
        owner.report = {"consent_immutable": {"status": "NOT_RUN"},
                        "targets": {owner.name: {"finalization": "PASS"}}, "migration_results": [
                            {"operation": name, "no_pending_message_observed": index == 2, "exit_code": 0,
                             "container_id": owner.resources.cid, "run_id": owner.operation["run_id"],
                             "packet_sha256": protocol.sha(owner.raw)} for index, name in enumerate(("deploy", "status", "deploy"))],
                        "native_results": {step: {"native_sha256": model.program.digest(native), "applied_rows": 2,
                                                  "catalog_check_counts": {"PASS": 29089}, "ledger_checks": 22,
                                                  "oracle_expressions": 416} for step in ("initial", "noop")}}
        owner.artifact = {"noop-native-before.json": native, "noop-ledger-observation.json": ledger,
                          "initial-after-noop-fingerprints.json": full8, reference["path"]: result}.__getitem__
        owner.program = SimpleNamespace(
            STATE=dict.fromkeys(("first_deploy_closed_success", "finalization_verified", "two_applied_verified", "activated"), True),
            digest=model.program.digest, save=mock.Mock(), collect_native=mock.Mock(return_value=native),
            ledger_observation=mock.Mock(return_value=({}, ledger)), compare_ledger=mock.Mock(return_value=({"checks": [0] * 22}, {})),
            fingerprints=mock.Mock(return_value=full8), CATALOG={"two": SimpleNamespace(compare_noop=mock.Mock(return_value=full8))},
            write_safe=mock.Mock(), event=mock.Mock(),
        )
        return owner, reference, result

    def test_enclosing_already_installed_gate_and_post_native_and_eight_field_ledger(self):
        owner, reference, result = self.outer()
        with mock.patch.object(child, "coordinate", return_value=(reference, result)) as coordinate:
            owner.program.STATE["activated"] = False
            with self.assertRaisesRegex(RuntimeError, "CONSENT_FRESH_SOURCE8_NOT_PROVED"):
                owner.run_consent()
            coordinate.assert_not_called()
            owner.program.STATE["activated"] = True
            owner.run_consent()
        self.assertEqual(owner.report["consent_immutable"]["postcheck"], operation.POST_RESULT)
        self.assertEqual(owner.program.collect_native.call_count, 2)
        owner.program.CATALOG["two"].compare_noop.assert_called_once()
        owner.program.event.assert_called_once_with(operation.STAGE, child.PASS)

    def test_encloser_rejects_ledger_change_and_sticky_child_skips_all_post_sql(self):
        owner, reference, result = self.outer()
        owner.program.ledger_observation.return_value = ({}, {"verified_rows": 3})
        with mock.patch.object(child, "coordinate", return_value=(reference, result)):
            with self.assertRaisesRegex(RuntimeError, "CONSENT_POST_LEDGER_DRIFT"):
                owner.run_consent()
        owner.program.event.assert_not_called()
        owner, reference, result = self.outer()

        def unclosed(*_):
            owner.transport.unknown = True
            result.update(status=child.STOP, remote_outcome_unconfirmed=True, complete_final_client_closure=False)
            return reference, result

        with mock.patch.object(child, "coordinate", side_effect=unclosed):
            with self.assertRaisesRegex(RuntimeError, "CONSENT_CHILD_RESULT_NOT_CLOSED"):
                owner.run_consent()
        owner.program.collect_native.assert_not_called()
        owner.program.ledger_observation.assert_not_called()
