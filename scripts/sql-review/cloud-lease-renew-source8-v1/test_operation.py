from contextlib import redirect_stdout
import io
import json
from types import SimpleNamespace
import unittest
from unittest import mock

import child
import operation
import prepare as source
from test_prepare import FIXTURE


class Model:
    def __init__(self, packet, assets, *, expiry=False, out_of_reserve=False, wrong_diag=False, unclosed=False):
        self.packet, self.assets = packet, assets
        self.expiry, self.out_of_reserve, self.wrong_diag, self.unclosed = expiry, out_of_reserve, wrong_diag, unclosed
        self.calls, self.sessions, self.failures = [], [], []
        self.phase, self.tick, self.known_xid = "fresh", 0, None
        self.native = {"modeled_catalog": True}
        self.program = SimpleNamespace(all_secrets=[], save=mock.Mock(), digest=lambda data: source.sha(source.canonical(data)),
                                       record_failure=lambda stage, code: self.failures.append((stage, code)), write_safe=self.write)
        blobs = {path: (source.ROOT / path).read_bytes()
                 for path in (child.PIPE, child.APP_CHILD, child.WORKER_CHILD, child.CONTEXT, source.COLLECTOR)}
        resources = SimpleNamespace(cid="a" * 64, volume_birth="2026-11-28T05:25:30Z")
        self.owner = SimpleNamespace(
            blobs=blobs, program=self.program, name="modeled-volume", root=source.ROOT, raw=b"OFFLINE_ONLY", resources=resources,
            operation={"run_id": "1fb9ecec-90c2-41de-86c0-9d892b9ab896", "source": source.WORKER_SOURCE},
            report={"lease_renew": {}, "authentication": [
                {"role": role, "correct_password": "PASS_SCRAM", "wrong_password": "PASS_REJECTED",
                 "actual_connection_closed": True} for role in child.ROLES],
                "auth_comparisons": [{"role": role, "checks": dict.fromkeys(child.AUTH_FIELDS, True)} for role in child.ROLES]},
            transport=SimpleNamespace(unknown=False), docker=SimpleNamespace(origin="model", socket_identity=lambda: "model", remote_unknown=False),
            observed_target=lambda: {"container_id": resources.cid, "volume_created_at": resources.volume_birth},
            psql_args=lambda name, role: ["exec", "-i", resources.cid, "psql", "SHOW_CONTEXT=never", "-U", role],
            exact_container_exec=self.raw,
        )

    def write(self, leaf, payload):
        self.written = json.loads(source.canonical(payload))
        return {"path": "noop-" + leaf, "sha256": source.sha(source.canonical(payload))}

    def raw(self, *args, input, **kwargs):
        text, role = input.decode(), args[-1]
        self.calls.append(("observer", role))
        if text == child.GLOBAL:
            output = "0"
        elif text == self.assets["all100-trigger-observe.sql"]:
            output = json.dumps(child.TRIGGERS)
        elif text == self.owner.blobs[source.COLLECTOR].decode():
            output = json.dumps(self.native)
        elif text == self.assets["source-lease-observe.sql"]:
            output = json.dumps(self.packet["expected_restricted_customer_source"])
        elif text.startswith("SELECT jsonb_build_object('exact',count(*)=1)"):
            output = '{"exact":true}'
        elif "retained;" in text:
            output = json.dumps({"count": text.count("g.token_hash IS NOT DISTINCT"), "exact": True})
        elif text.startswith("SELECT jsonb_agg(jsonb_build_object('table'"):
            rows = []
            for table in self.packet["full42_table_order"]:
                count = 0 if self.phase == "fresh" else child.EXPECTED_SETUP.get(table, 0)
                version = {"claimed": "b", "renewed": "c"}.get(self.phase, "a") if table == "platform.runtime_work_item" else "a"
                rows.append({"table": table, "count": count, "sha256": version * 64})
            output = json.dumps(rows)
        elif "'domain_sha256'" in text:
            state = {"deadline": "2026-11-28T05:25:42.000000Z" if self.phase == "claimed" else "2026-11-28T05:27:19.000000Z",
                     "live": True, "mutation_xid": self.known_xid,
                     "domain_sha256": "a" * 64, "row_sha256": ("b" if self.phase == "claimed" else "c") * 64}
            output = json.dumps(state)
        else:
            raise AssertionError("unmodeled observer recipe")
        return SimpleNamespace(returncode=0, stdout=output.encode(), stderr=b"")

    def run(self):
        model = self
        actual_transport = child.shared_transport

        class Pipe:
            def __init__(self, role, coordinator):
                self.role, self.coordinator = role, coordinator
                self.active = self.closed = False
                self.backend = self.exit_code = None
                self.case = None
                self.idx = len(model.sessions) + 30
                self.process = SimpleNamespace(poll=lambda: self.exit_code)
                model.sessions.append(self)

            def call(self, text):
                if text.startswith("BEGIN ISOLATION LEVEL READ COMMITTED;"):
                    return [], True, ""
                if text.startswith("SELECT 'WA_CTX01_TUPLE|'"):
                    record = {"login": self.role, "current_user": self.role, "database": "wa_p0c_rehearsal", "isolation": "read committed",
                              "pid": str(self.idx), "xid": str(self.idx + 100), "started": "2026-11-28 05:25:30+00",
                              "clock": "2026-11-28 05:25:30+00"}
                    return ["WA_CTX01_TUPLE|" + json.dumps(record)], True, ""
                if text.startswith("INSERT INTO platform.database_action_grant "):
                    model.calls.append(("issuer-commit", self.role))
                    return ['{"created_at":"2026-11-28T05:25:31+00:00"}'], True, ""
                if text.startswith("SELECT platform_private.bind_request_context("):
                    model.calls.append(("bind", self.role))
                    return [], True, ""
                if text.startswith("SET LOCAL wa.lease_secret="):
                    self.modeled_matches = model.program.all_secrets[0] in text
                    model.calls.append(("set-lease-material", self.role))
                    return [], True, ""
                if text.lstrip().startswith("ALTER TABLE app.users DISABLE TRIGGER owner_commit;"):
                    model.calls.append(("identity-seed", self.role))
                    return [], True, ""
                if text.lstrip().startswith("INSERT INTO platform_private.identity_service_receipt "):
                    model.phase = "ready"
                    model.calls.append(("service-bootstrap", self.role))
                    return [], True, ""
                if text == model.assets["source-lease.sql"]:
                    return ["WA_CUSTOMER_CONTROL_READY_TO_COMMIT"], True, ""
                if text == model.assets["schedule-lease.sql"]:
                    return ["WA_LR_SCHEDULE_READY"], True, ""
                if "minimum_server_reserve" in text:
                    model.calls.append(("pre-action-scope", self.role))
                    return [json.dumps({"visible_work": 1, "exact_route": True, "minimum_server_reserve": not model.out_of_reserve,
                                        "matches_preimage": self.modeled_matches})], True, ""
                for name in source.CASES:
                    if text != model.assets[name + ".sql"]:
                        continue
                    self.case = name
                    model.calls.append((name, self.role))
                    rows = [source.marker(name, "BEFORE")]
                    if name in source.DENIALS:
                        self.exit_code = 3
                        raw = (f"ERROR:  P0001: {source.MESSAGE}\nCONTEXT:  PL/pgSQL function {source.GUARD} line 31 at RAISE\n"
                               "LOCATION:  exec_stmt_raise, pl_exec.c:3911\n")
                        return rows, False, "DETAIL: raw-source-canary\n" if model.wrong_diag else raw
                    model.phase = "claimed" if name == source.CASES[0] else "renewed"
                    model.known_xid = str(self.idx + 100)
                    if model.expiry and name == source.CASES[0]:
                        model.tick = 12
                    return rows + ['{"changed":1}', source.marker(name, "AFTER")], True, ""
                raise AssertionError("unmodeled session recipe")

            def close(self):
                model.calls.append(("close", self.role))
                if model.unclosed and self.case in source.DENIALS:
                    raise RuntimeError("unclosed raw source canary")
                self.closed = True
                return 0 if self.exit_code is None else self.exit_code

        def transport(*args):
            _, error, endpoint, context = actual_transport(*args)
            return Pipe, error, endpoint, context

        with mock.patch.object(child, "shared_transport", side_effect=transport):
            return child.coordinate(self.owner, self.native, self.packet, self.assets, clock=lambda: self.tick)[1]


class OwningOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet, cls.assets = source.assemble(FIXTURE)

    def test_one_positive_and_two_denials_with_six_bound_grants_and_closed_state(self):
        model = Model(self.packet, self.assets)
        value = model.run()
        self.assertTrue(operation.passes(value), value["first_failure"])
        self.assertEqual(model.written, value)
        self.assertEqual(model.calls.count(("bind", "wa_worker")), 4)
        self.assertEqual(model.calls.count(("issuer-commit", "wa_context_issuer")), 6)
        self.assertEqual(model.calls.count(("pre-action-scope", "wa_worker")), 3)
        self.assertEqual([row["case"] for row in value["results"]], list(source.CASES))
        self.assertTrue(all(material.encode() not in source.canonical(value) for material in model.program.all_secrets))

    def test_expired_or_missing_server_reserve_blocks_dispatch(self):
        for flags, reason in (({"expiry": True}, "LEASE_RENEW_LIVE_WINDOW"),
                              ({"out_of_reserve": True}, "LEASE_RENEW_PRE_ACTION_ROUTE_UNCONFIRMED")):
            model = Model(self.packet, self.assets, **flags)
            actual = model.run()
            self.assertEqual(actual["first_failure"]["code"], reason)
            self.assertNotIn(("current-holder-renew", "wa_worker"), model.calls)
            self.assertTrue(actual["complete_final_client_closure"])
            self.assertFalse(actual["remote_outcome_unconfirmed"])

    def test_first_denial_failure_preserved_and_unclosed_transport_suppresses_later_reads(self):
        model = Model(self.packet, self.assets, wrong_diag=True, unclosed=True)
        actual = model.run()
        self.assertEqual(actual["first_failure"], {"stage": "shorten-renew-denied", "code": "LEASE_RENEW_ORIGINAL_CASE_UNCONFIRMED"})
        self.assertTrue(actual["remote_outcome_unconfirmed"] and model.owner.docker.remote_unknown)
        self.assertFalse(actual["complete_final_client_closure"])
        self.assertEqual(model.calls[-1], ("close", "wa_worker"))
        self.assertNotIn(("copied-hash-renew-denied", "wa_worker"), model.calls)
        self.assertNotIn(b"raw-source-canary", source.canonical(actual))

    def test_exact_precleanup_hook_and_explicit_execution_gate(self):
        S = operation.mechanism()[0].S
        self.assertTrue(operation.exact_seam(S.read(source.ROOT / S.STEPS)))
        self.assertFalse(operation.exact_seam(b"def main():\n try:\n  event()\n finally:\n  cleanup()\n"))
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.object(operation, "read_closed") as read:
            self.assertEqual(operation.main(["execute", "--packet", "/absent/operation.json"]), 1)
        read.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())["code"], "LEASE_RENEW_EXPLICIT_EXECUTION_REQUIRED")

    def outer(self):
        model = Model(self.packet, self.assets)
        outcome = model.run()
        leaf = "noop-" + child.LEAF
        reference = {"path": leaf, "sha256": source.sha(source.canonical(outcome))}
        basis, two_plan, _ = operation.mechanism()
        klass = operation.owner_type((basis, two_plan, SimpleNamespace(Owner=object)))
        owner = klass.__new__(klass)
        owner.raw, owner.name, owner.resources = model.owner.raw, model.owner.name, model.owner.resources
        owner.operation = model.owner.operation | {"lease_renew": {"recipe_sha256": outcome["recipe_sha256"], "recipe": self.packet,
                                                                   "prior_closed_worker_cid": "b" * 64}}
        owner.renewal_assets, owner.transport = self.assets, SimpleNamespace(unknown=False)
        ledger, fingerprints = {"applied": 2}, {"verified": True}
        owner.artifact = {leaf: outcome, "noop-native-before.json": model.native, "noop-ledger-observation.json": ledger,
                          "initial-after-noop-fingerprints.json": fingerprints}.__getitem__
        owner.report = {"lease_renew": {"status": "NOT_RUN"},
                        "targets": {owner.name: {"finalization": "PASS", "volume_created_at": owner.resources.volume_birth}},
                        "migration_results": [{"operation": name, "exit_code": 0, "no_pending_message_observed": index == 2,
                                               "container_id": owner.resources.cid, "run_id": owner.operation["run_id"],
                                               "packet_sha256": source.sha(owner.raw)}
                                              for index, name in enumerate(("deploy", "status", "deploy"))],
                        "native_results": {name: {"native_sha256": model.program.digest(model.native), "applied_rows": 2,
                                                  "catalog_check_counts": {"PASS": 29089}, "ledger_checks": 22,
                                                  "oracle_expressions": 416} for name in ("initial", "noop")}}
        owner.program = SimpleNamespace(
            STATE=dict.fromkeys(("first_deploy_closed_success", "finalization_verified", "two_applied_verified", "activated"), True),
            digest=model.program.digest, save=mock.Mock(), collect_native=mock.Mock(return_value=model.native),
            ledger_observation=mock.Mock(return_value=({}, ledger)), compare_ledger=mock.Mock(return_value=({"checks": [0] * 22}, {})),
            fingerprints=mock.Mock(return_value=fingerprints), write_safe=mock.Mock(), event=mock.Mock(),
            CATALOG={"two": SimpleNamespace(compare_noop=mock.Mock(return_value={"all_eight_columns_unchanged": True}))},
        )
        return owner, reference, outcome

    def test_child_requires_same_run_auth_and_complete_post_parity(self):
        owner, reference, outcome = self.outer()
        with mock.patch.object(child, "coordinate", return_value=(reference, outcome)) as execute:
            owner.program.STATE["activated"] = False
            with self.assertRaisesRegex(RuntimeError, "LEASE_RENEW_FRESH_SOURCE8_UNPROVED"):
                owner.run_renewal()
            execute.assert_not_called()
            owner.program.STATE["activated"] = True
            owner.run_renewal()
        self.assertEqual(owner.report["lease_renew"]["postcheck"], operation.POST_PASS)
        self.assertEqual(owner.program.collect_native.call_count, 2)
        owner.program.CATALOG["two"].compare_noop.assert_called_once()
        owner.program.event.assert_called_once_with(child.STAGE, child.PASS)

    def test_ledger_drift_stops_and_sticky_closure_suppresses_all_post_sql(self):
        owner, reference, outcome = self.outer()
        owner.program.ledger_observation.return_value = ({}, {"applied": 3})
        with mock.patch.object(child, "coordinate", return_value=(reference, outcome)):
            with self.assertRaisesRegex(RuntimeError, "LEASE_RENEW_POST_PARITY_UNCONFIRMED"):
                owner.run_renewal()
        owner.program.event.assert_not_called()
        owner, reference, outcome = self.outer()

        def uncertain(*_):
            owner.transport.unknown = True
            outcome.update(remote_outcome_unconfirmed=True, complete_final_client_closure=False, status=child.STOP)
            return reference, outcome

        with mock.patch.object(child, "coordinate", side_effect=uncertain):
            with self.assertRaisesRegex(RuntimeError, "LEASE_RENEW_CHILD_RECEIPT_UNCONFIRMED"):
                owner.run_renewal()
        owner.program.collect_native.assert_not_called()
        owner.program.ledger_observation.assert_not_called()
