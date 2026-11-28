"""Offline integration of the exact inherited owner, typed receipts and stage ordering."""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest import mock

import operation as O
import test_profile as fixture


S, P, C = O.S, O.P, O.candidate
TWO_NATIVE_FIXTURES = {
    "initial-native-before.json": "2d32f31aed413327dbb8d4476233268f5fb8b5029eb7bdd76308a7d4ac0d891a",
    "initial-oracle-preflight.json": "cef8ce63dddadfc4dda47ffa928cd942e97a0639a213d5383e0dcb032c64bfc5",
    "initial-oracle-results.json": "c0997279c5d95544aeb998da487ea4771bab08238a36e8d63ff2a62378c2c14a",
    "initial-oracle-closure.json": "37600f840b4c617ff853558baa8902773e645ce937e2f19318513649c29ab112",
}


class TrackOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prepared, _, cls.steps, cls.native = O.compose(fixture.RUNTIME_ARCHIVE, fixture.RUN_ID, draft=True)

    def local_packet(self, directory):
        _, plan, blobs, inner, manifest, nested, files, archive = self.prepared
        # A directly injected constructor model. The production entry rejects
        # this packet state and these illustrative Git identities.
        plan = {**plan, "status": "OFFLINE_CONSTRUCTOR_MODEL", "source": {"commit": "a" * 40, "tree": "b" * 40}}
        P.write_new(directory / "operation.json", S.encode(plan))
        P.write_new(directory / "run-manifest.json", nested)
        P.write_new(directory / "source9.tar", archive)
        P.write_source(directory / "source9", files)
        P.write_source(directory / "native", self.native)
        return (directory, plan, blobs, inner, manifest, nested, files, archive)

    def initialize(self, directory):
        presented = self.local_packet(directory)
        module = O.mechanisms(presented[2])
        factory = mock.Mock(return_value=SimpleNamespace())
        owner = O.owner_type(module, self.steps, self.native)(presented, S.encode(presented[1]),
                    {"source": "a" * 64, "literal": "b" * 64}, docker_factory=factory)
        owner.program.OUT.mkdir()
        self.assertEqual(factory.call_count, 1)
        return owner, module

    def test_real_source9_owner_packet_and_native_preflight(self):
        directory, plan, blobs, _, manifest, nested, files, archive = self.prepared
        self.assertEqual(directory.parent, P.SCRATCH)
        self.assertEqual(plan["schema"], O.SCHEMA)
        self.assertEqual(plan["status"], "SOURCE_DRAFT_NOT_RUN")
        self.assertIsNone(plan["source"])
        self.assertEqual(len(plan["source_pins"]), 479)
        self.assertEqual(len(files), 9)
        self.assertEqual(plan["source_pins"], {name: S.sha(raw) for name, raw in blobs.items()})
        self.assertEqual(manifest["history"]["ordered"], C.history_rows())
        self.assertEqual(S.sha(nested), plan["nested_manifest"]["sha256"])
        self.assertEqual(S.sha(archive), plan["archive"]["sha256"])
        with TemporaryDirectory() as scratch, mock.patch("builtins.print"):
            owner, _ = self.initialize(Path(scratch))
            owner.verify_packet()
            self.assertEqual(owner.program.EXPECTED_SHA, C.CATALOG_SHA)
            self.assertEqual(owner.program.CATALOG["expected"]["expected_sha256"], C.CATALOG_SHA)
            self.assertEqual(owner.program.CATALOG["plan"]["expression_count"], 416)
            oracle = owner.program.CATALOG["tools"]["catalog_expression_oracle"]
            closed_manifest = owner.program.CATALOG["expected"]
            recreated_plan = oracle.build_plan(closed_manifest, C.ROOT)
            self.assertEqual(S.encode(recreated_plan), self.native["expression-oracle-plan.json"])
            self.assertEqual(oracle.emit_sql(closed_manifest, recreated_plan, database="wa_p0c_rehearsal",
                                             grantor="postgres").encode(), self.native["expression-oracle.sql"])
            self.assertEqual(owner.program._required_safety_text("ORIGINAL_GRANTOR_FINALIZATION").encode(),
                             blobs[C.ORIGINAL_FINALIZER])
            self.assertEqual(owner.report["events"][-1]["stage"], "TRACK_SOURCE")
            self.assertEqual(owner.program.MANIFEST["migration_target"]["source_snapshot"], str(Path(scratch) / "source9"))
            ledger = owner.program.CATALOG["tools"]["prisma_ledger_proof"]
            registered = owner.program.CATALOG["two"].registration(ledger, root=Path(scratch) / "source9",
                run_id=plan["run_id"], target_attestation_sha256="a" * 64, source_expected_sha256=C.CATALOG_SHA)
            self.assertEqual(len(registered["history_expected"]), 3)
            self.assertFalse(owner.transport.unknown)
            self.assertEqual(owner.transport.observations, [])

    def test_owning_track_observer_uses_exact_read_only_query_and_rejects_leftover_authority(self):
        with TemporaryDirectory() as scratch, mock.patch("builtins.print"):
            owner, _ = self.initialize(Path(scratch))
            owner.verify_packet()
            owner.resources.cid = "d" * 64
            p = owner.program
            model = fixture.ThreeHistoryTests()
            model.native = p.CATALOG["expected"]
            waiting = model.authority(True)
            restored = model.authority(False)
            rows = [waiting, waiting, restored]
            executed = []

            def query(name, text, stage):
                executed.append(stage)
                self.assertEqual(name, owner.name)
                self.assertEqual(text, O.proof.AUTHORITY_SQL)
                self.assertTrue(text.startswith("BEGIN READ ONLY;"))
                return p.Result(0, json.dumps(rows.pop(0)) + "\n", "")

            p.run_catalog_query = query
            self.assertTrue(owner.track_authority("PRE_FINALIZATION")["candidate_function_bodies_verified"])
            with self.assertRaisesRegex(S.Held, "TRACK_AUTHORITY_OBSERVATION_CONTEXT"):
                owner.track_authority("POST_FINALIZATION")
            p.STATE["finalization_verified"] = True
            with self.assertRaisesRegex(S.Held, "TRACK_LEAF_MEMBERSHIP_OR_RESTORATION_DRIFT"):
                owner.track_authority("POST_FINALIZATION")
            self.assertTrue(owner.track_authority("POST_FINALIZATION")["leaf_create_absent"])
            self.assertEqual(executed, ["TRACK_PRE_FINALIZATION", "TRACK_POST_FINALIZATION", "TRACK_POST_FINALIZATION"])

    def test_initial_and_noop_full_comparison_use_private_ledger_and_repo_oracle(self):
        with TemporaryDirectory() as scratch, mock.patch("builtins.print"):
            owner, _ = self.initialize(Path(scratch))
            owner.verify_packet()
            p = owner.program
            catalog = p.CATALOG
            prior = {name: p.unique_json(S.pinned(C.ROOT, f"{C.PRIOR}/evidence/{name}", digest))
                     for name, digest in TWO_NATIVE_FIXTURES.items()}
            # These are modeled collector replies, never operational evidence.
            # The exact archived TWO native and oracle values are the fixture
            # basis. Only the three source-approved track bodies and bindings
            # are projected to the distinct candidate and current test run.
            snapshot = prior["initial-native-before.json"]
            expected_functions = catalog["expected"]["expected"]["functions"]
            projected = set()
            for row in snapshot["functions"]:
                if row["object"] in O.proof.FUNCTIONS:
                    row["body_sha256"] = expected_functions[row["object"]]["body_sha256"]
                    projected.add(row["object"])
            self.assertEqual(projected, set(O.proof.FUNCTIONS))
            records = [prior[f"initial-oracle-{name}.json"] for name in ("preflight", "results", "closure")]
            for row in records:
                row["plan_sha256"] = catalog["plan"]["plan_sha256"]
            records[1].update(source_expected_sha256=C.CATALOG_SHA,
                              source_inputs_aggregate_sha256=catalog["expected"]["inputs_aggregate_sha256"])
            ledger = catalog["tools"]["prisma_ledger_proof"]
            installed = {"attestation_sha256": "a" * 64}
            registration = catalog["two"].registration(ledger, root=Path(scratch) / "source9", run_id=owner.operation["run_id"],
                target_attestation_sha256=installed["attestation_sha256"], source_expected_sha256=C.CATALOG_SHA)
            observation = {**ledger.schema_expectation(), "history": registration["history_expected"], "history_ids_unique": True,
                           "format": ledger.NATIVE_FORMAT, "server_version_num": 170011, "database": O.proof.DATABASE,
                           "read_only": True, "isolation": "repeatable read", "collected_as": "postgres", "session_user": "postgres",
                           "collector_is_superuser": True}
            queries = []

            def collector(name, text, stage):
                queries.append(stage)
                if stage == "ORACLE_initial":
                    self.assertEqual(text, catalog["oracle_sql"])
                    return p.Result(0, "\n".join(json.dumps(row) for row in records) + "\n", "")
                self.assertEqual(text, owner.blobs[C.LEDGER_COLLECTOR].decode())
                return p.Result(0, json.dumps(observation) + "\n", "")

            p.collect_native = lambda *_: deepcopy(snapshot)
            p.run_catalog_query = collector
            p.observe_public_baseline = p.acl_compatibility_preflight = p.text_compatibility_preflight = lambda *_: None
            initial, initial_ledger = p.qualify(installed, "initial")
            noop, noop_ledger = p.qualify_noop(installed, initial)
            self.assertEqual((initial, initial_ledger), (noop, noop_ledger))
            self.assertEqual(queries, ["ORACLE_initial", "LEDGER_initial", "LEDGER_NOOP"])
            for result in owner.report["native_results"].values():
                self.assertEqual((result["catalog_check_counts"], result["applied_rows"], result["ledger_checks"], result["oracle_expressions"]),
                                 ({"PASS": 29089}, 3, 22, 416))

            third = Path(scratch) / "source9" / owner.operation["ledger_expected"][-1]["path"]
            third.write_bytes(third.read_bytes() + b"\n-- deliberate modeled source9 drift\n")
            typed_ledger_evidence = p.unique_json((p.OUT / "initial-ledger-evidence.json").read_bytes())
            failure = catalog["tools"]["compare_native_catalog"].compare_manifest(
                catalog["expected"], initial, bootstrap_grantor="postgres", bootstrap_superuser=True,
                public_schema_owner="pg_database_owner", public_acl_registration=catalog["public"]["full_acl"],
                ledger_registration=registration, ledger_evidence=typed_ledger_evidence,
                expression_oracle_evidence=p.STATE["initial_oracle_evidence"], oracle_database=O.proof.DATABASE, root=C.ROOT)
            self.assertEqual([(row["category"], row["field"], row["status"]) for row in failure["findings"]],
                             [("ledger", "source-bound-registration", "FAIL")])

    def test_exact_separate_reviews_bound_to_this_packet(self):
        plan = {**self.prepared[1], "source": {"commit": "a" * 40, "tree": "b" * 40}}
        raw = S.encode(plan)
        base = O.review_bindings(plan, raw)
        first = {"schema": "workinants.cloud-f0-track-retained-base-source-review.v1", "decision": "APPROVE",
                 "reviewer": "offline-review-model", "source_author": "offline-author-model", "bindings": base,
                 "scopes": O.SOURCE_SCOPES}
        second = {**first, "schema": "workinants.cloud-f0-track-retained-base-literal-review.v1", "scopes": O.LITERAL_SCOPES,
                  "bindings": {**base, "source_review_sha256": S.sha(S.encode(first))}}
        with TemporaryDirectory() as scratch:
            directory = Path(scratch)
            P.write_new(directory / "source-review.json", S.encode(first))
            P.write_new(directory / "literal-review.json", S.encode(second))
            reviews = O.exact_reviews(directory, plan, raw)
            self.assertEqual(reviews["literal"], S.sha(S.encode(second)))
            changed = {**plan, "run_id": "20000000-0000-4000-8000-000000000000"}
            with self.assertRaisesRegex(S.Held, "FRESH_TYPED_REVIEW_REQUIRED"):
                O.exact_reviews(directory, changed, S.encode(changed))

    def test_entry_refuses_unapproved_or_draft_before_owner(self):
        with mock.patch.object(O, "read_closed", side_effect=AssertionError("attempted packet access")):
            with self.assertRaisesRegex(S.Held, "EXPLICIT_TRACK_OWNED_EXECUTION_REQUIRED"):
                O.execute(Path("/not-an-owned-path"), explicitly_reviewed=False)
        # Test draft state refusal independently of an expensive second reconstruction.
        with TemporaryDirectory() as scratch:
            directory = Path(scratch)
            with mock.patch.object(P, "SCRATCH", directory.parent), mock.patch.object(O, "compose") as compose:
                P.write_new(directory / "operation.json", S.encode(self.prepared[1]))
                with self.assertRaisesRegex(S.Held, "TRACK_COMMITTED_OWNED_PACKET_REQUIRED"):
                    O.read_closed(directory / "operation.json")
                compose.assert_not_called()

    def runner_model(self, owner, module, mode):
        plan = owner.operation
        parent = C.reviewed_parent()
        scope = {name: deepcopy(owner.target[name]) for name in ("container_name", "volume_name", "image", "network", "labels", "bootstrap")}
        scope.update(endpoint=parent.ENDPOINT, daemon=owner.manifest["daemon"], container_id="c" * 64,
                     volume_created_at="2000-01-01T00:00:00.000000000Z", image_id=plan["image"]["image_id"],
                     published_ports=False, bootstrap_removed=True, mount_destinations=list(parent.MOUNT_DESTINATIONS))
        owner.observed_target = lambda: scope
        operations = []

        def local_result(*args, input=None, **_):
            if "/usr/bin/sha256sum" in args:
                operations.append("source_hashes")
                expected = {**{f"{module.B.SOURCE}/{name}": S.sha(raw) for name, raw in owner.files.items()},
                            module.B.NODE: owner.manifest["tools"]["files_sha256"]["node/bin/node"]}
                return SimpleNamespace(returncode=0, stderr=b"", stdout="".join(f"{h}  {path}\n" for path, h in expected.items()).encode())
            if "/usr/bin/stat" in args:
                operations.append("source_lengths")
                return SimpleNamespace(returncode=0, stderr=b"", stdout="".join(f"{len(raw)}\n" for _, raw in sorted(owner.files.items())).encode())
            self.assertIn(C.OP_ARG, args)
            operations.append("modeled_node_dispatch")
            attestation = S.unique_json(input)
            exact = {"operation": "deploy", "run_id": owner.manifest["run_id"], "container_id": scope["container_id"],
                     "daemon_id": scope["daemon"]["daemon_id"], **attestation["authorization"], "attestation_sha256": S.sha(input),
                     "raw_output_discarded": True, "database_qualification_claimed": False}
            if mode == "refusal":
                envelope = {**exact, "schema": C.REFUSAL_SCHEMA, "status": "REFUSED_OR_INCOMPLETE", "phase": "LOCAL_GUARD",
                            "cause_family": "HELD_GUARD", "code": "EXACT_ORDERED_THREE_HISTORY", "child_dispatch": "NOT_ATTEMPTED"}
                return Result(1, S.encode(envelope), b"")
            if mode == "malformed":
                return Result(0, b'{"schema":"unconfirmed"}\n', b"")
            envelope = {**exact, "schema": C.RESULT_SCHEMA, "status": O.proof.RESULT_COMPLETE, "exit_code": 0, "prisma_codes": [],
                        "sqlstates": [], "no_pending_message_observed": False,
                        "diagnostic_format": {field: field in ("text_valid", "headers_valid")
                                              for field in owner.receipt_validator.DIAGNOSTIC_FLAGS}}
            envelope.update({name: attestation["planned"]["source"][name] for name in ("initial_sql_sha256", "append_sql_sha256",
                "track_retained_sql_sha256", "ordered_history_sha256", "effective_expected_sha256")})
            return Result(0, S.encode(envelope), b"")

        def close(_name, _stage):
            if owner.transport.unknown:
                operations.append("closure_blocked_without_sql")
                raise owner.program.Stop("FINALIZATION_UNKNOWN_TRANSPORT")
            operations.append("all_clients_independently_closed")

        owner.exact_container_exec = local_result
        owner.program.closed_backends = close
        return operations

    def test_inherited_migration_receipt_and_sticky_refusals(self):
        for mode in ("success", "refusal", "malformed"):
            with self.subTest(mode=mode), TemporaryDirectory() as scratch, mock.patch("builtins.print"):
                owner, module = self.initialize(Path(scratch))
                operations = self.runner_model(owner, module, mode)
                if mode == "success":
                    record = owner.migrate("deploy", O.PREFINAL)
                    self.assertEqual(record["track_retained_sql_sha256"], C.CANDIDATE_SHA)
                    self.assertEqual(operations[-1], "all_clients_independently_closed")
                    self.assertFalse(owner.transport.unknown)
                else:
                    with self.assertRaises((S.Held, module.S.Held)):
                        owner.migrate("deploy", O.PREFINAL)
                    self.assertTrue(owner.transport.unknown)
                    self.assertEqual(operations[-1], "closure_blocked_without_sql")
                    self.assertEqual(owner.report.get("migration_results", []), [])
                    expected = "CLOUD_INNER_TERMINAL_REFUSAL" if mode == "refusal" else "TRACK_MIGRATION_RESULT_BINDING"
                    self.assertEqual(owner.program.FIRST_OPERATION_FAILURE, {"stage": O.PREFINAL, "code": expected})
                    if mode == "refusal":
                        detail = owner.report["inner_cli_closure"]["bounded_terminal_refusal"]
                        self.assertEqual(detail["code"], "EXACT_ORDERED_THREE_HISTORY")
                        self.assertIs(detail["transport_uncertainty_cleared"], False)
                self.assertEqual(operations[:3], ["source_hashes", "source_lengths", "modeled_node_dispatch"])

    def mounted_pipeline(self, directory, *, failure=False):
        owner, _ = self.initialize(directory)
        p = owner.program
        p.OUT.rmdir()  # The inherited main exclusively makes this directory.
        visits = []
        fake_snapshot = {"simulated_native": True}
        fake_rows = {"simulated_ledger": True}

        def visit(name, result=None):
            def observe(*_):
                visits.append(name)
                return result
            return observe

        def prefinal(_record):
            visits.append("prefinal_track_and_three")
            if failure:
                p.report["stage"] = "TRACK_PRE_FINALIZATION"
                raise S.Held("TRACK_PRE_FINALIZATION_LEDGER_DRIFT")

        def finish_installation():
            visits.append("eligible_completed_installation_cleanup")
            if failure:
                p.report["stage"] = "FINALIZATION"
                raise p.Stop("FINALIZATION_VERIFICATION_FAILED")
            p.STATE["finalization_verified"] = True

        def activate():
            self.assertTrue(all(p.STATE[name] for name in ("three_applied_verified", "first_deploy_closed_success", "finalization_verified")))
            self.assertNotIn("two_applied_verified", p.STATE)
            visits.append("activate_synthetic_scram")

        def capture(name, value):
            visits.append(name)
            if name == O.RESULT_FILE:
                self.assertEqual(value["schema"], O.RESULT_SCHEMA)
                self.assertEqual(value["status"], O.PASS)
                self.assertEqual(value["track"], {"modeled_only": True})

        def qualify(*_):
            p.report["native_results"] = {"modeled_only": True}
            return visit("initial_native_and_oracle", (fake_snapshot, fake_rows))()

        p.CATALOG["two"] = SimpleNamespace(compare_noop=visit("compare_full_rows", {"modeled_only": True}))
        p.__dict__.update(verify_packet=visit("verify"), preflight=visit("preflight"), ensure_image=visit("image"),
            create_resources=visit("create"), provision_tools=visit("tools"), track_pre_deploy=visit("pre_deploy_authority"),
            track_pre_finalization=prefinal, ensure_cleanup=finish_installation, track_post_finalization=visit("restored_authority"),
            collect_native=visit("read_only_native", fake_snapshot), ledger_observation=visit("native_ledger", ({"history_expected": [1, 2, 3]}, fake_rows)),
            compare_ledger=visit("compare_22", ({"checks": list(range(22))}, {})), write_safe=capture, activate_runtime=activate,
            qualify=qualify, fingerprints=lambda label: visit(label, {})(),
            qualify_noop=visit("noop_native", (fake_snapshot, fake_rows)), track_terminal=visit("terminal_scope", {"modeled_only": True}),
            secret_scan=visit("sanitization"), cleanup=visit("exact_cleanup"), postchecks=visit("postchecks"), verify_references=visit("references"))
        p.__dict__["migrate"] = lambda operation, label: visit(label, {"no_pending_message_observed": True})()
        p.__dict__["bootstrap"] = lambda: (visits.append("bootstrap"), p.bootstrap_attempted.add(owner.name))
        p.created_containers[owner.name] = "a" * 64
        return p, visits

    def test_rendered_actual_main_retains_full_order_and_independent_cleanup(self):
        with TemporaryDirectory() as scratch, mock.patch("builtins.print"):
            p, visits = self.mounted_pipeline(Path(scratch))
            self.assertEqual(p.main(), 0)
        self.assertEqual(visits, ["verify", "preflight", "image", "create", "tools", "bootstrap", "pre_deploy_authority", O.PREFINAL,
            "prefinal_track_and_three", "eligible_completed_installation_cleanup", "restored_authority", "read_only_native",
            "native_ledger", "read_only_native", "compare_22", "pre-activation-ledger-evidence.json", "activate_synthetic_scram",
            "initial_native_and_oracle", "before-noop", "GENUINE_STATUS", "GENUINE_SECOND_DEPLOY", "after-noop", "compare_full_rows",
            "noop_native", "terminal_scope", O.RESULT_FILE, "eligible_completed_installation_cleanup", "sanitization", "exact_cleanup",
            "postchecks", "references"])

    def test_prefinal_first_failure_survives_secondary_finalization_failure(self):
        with TemporaryDirectory() as scratch, mock.patch("builtins.print"):
            p, visits = self.mounted_pipeline(Path(scratch), failure=True)
            self.assertEqual(p.main(), 1)
        self.assertEqual(p.FIRST_OPERATION_FAILURE, {"stage": "TRACK_PRE_FINALIZATION", "code": "TRACK_PRE_FINALIZATION_LEDGER_DRIFT"})
        self.assertEqual(visits[-5:], ["eligible_completed_installation_cleanup", "sanitization", "exact_cleanup", "postchecks", "references"])
        self.assertNotIn("activate_synthetic_scram", visits)
        self.assertNotIn("GENUINE_SECOND_DEPLOY", visits)


class Result:
    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


if __name__ == "__main__":
    unittest.main()
