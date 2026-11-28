"""Prepare or operate a fresh, independently reviewed Cloud App source8 packet."""

import argparse
import ast
import os
from pathlib import Path
import re
import signal
import sys
from types import ModuleType
import uuid

import app_child
import prepare as held


ROOT = held.ROOT
HERE = held.HERE.relative_to(ROOT).as_posix()
TWO = "scripts/sql-review/cloud-two-history-owned-v2"
TWO_COMMIT = "464caba083c2c53dd158af027df2af933a0bdc18"
TWO_RUN = "2f71c365-4c31-4000-837c-cdd72ac163ae"
RECEIPTS = "context/reconciliation/cloud-phase0-evidence/2026-11-27"
TWO_EVIDENCE = f"{RECEIPTS}/two-2f71c365"
HELD_REVIEW = f"{RECEIPTS}/app-source8-preparation-review.json"
TWO_RESULT = "evidence/two-history-results.json"
TWO_REPORT = "evidence/run-evidence.json"
TWO_AUDIT = "independent-closure.json"
TWO_ADMISSION = "acceptance.json"
APP_OWNER_SCHEMA = "workinants.cloud-f0-app-source8-owned-operation.v1"
EXECUTE = "--execute-reviewed-cloud-f0-app-source8-v1"
STAGE = "CLOUD_APP_SOURCE8"
SEAM_EVENT = ("NOOP", "PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER")
MECHANISM = {
    "basis.py": "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af",
    "plan.py": "c308295d97ab1d794cf3a7a8b2f241b1c7266b8cb606704ada6f2c3de9c1decb",
    "operation.py": "8680611ab98322a192a70c72f373b1fb4858ddbbd184c1dc4f450bb98823b0c0",
}
SUPPORT = {
    app_child.CONTEXT: "5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33",
    app_child.SCOPED_READ: "4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15",
    HELD_REVIEW: "c328f1f7314c9aa9541844cb951013cffb1614b65bfe4813ee80a86a673bd213",
}
PRIOR = {
    "operation.json": "ad689dc962febeeb72b5f7583598cef559d475b2fe7227d097e57558625cef30",
    TWO_ADMISSION: "9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76",
    TWO_AUDIT: "2aa3d5178e406f42ae617c77ffe0e72f8b472e1c42b51fccbb261e3a781f0992",
    TWO_RESULT: "81d04362aa00e52bcb7161899cf3711c644cd7abb7237c2d1f0a33f0cb41115c",
    TWO_REPORT: "3c2c4e75b6414d8a4cb62bb7356274628481e3e679a84e0494c79869409dfbf3",
}
OWNER_FILES = ("README.md", "OPERATION.md", "prepare.py", "operation.py", "host_session.py", "app_child.py", "test_operation.py")
SOURCE_SCOPES = ["accepted_prior_two_machinery_and_fresh_same_run_source8", "effective_app14_protocol_and_frames",
                 "finite_role_sessions_issuer_retention_and_strict_closure", "unchanged_catalog_and_full_ledger"]
LITERAL_SCOPES = ["exact_current_socket_daemon_and_fresh_target", "reviewed_source_and_real_tool_closure",
                  "observed_two_before_app_and_live_original_grantor", "app14_and_actual_restricted_schedule_only",
                  "closure_evidence_and_exact_cleanup"]


def mechanism():
    modules = []
    registered = []
    try:
        for leaf, pin in MECHANISM.items():
            relative = f"{TWO}/{leaf}"
            raw = held.source(ROOT, relative, pin)
            held.need(raw == held.git_blob(ROOT, relative, TWO_COMMIT), "APP_TWO_EXECUTED_SOURCE_DRIFT")
            name = "_workinants_app_owned_mechanism" if leaf == "operation.py" else leaf.removesuffix(".py")
            held.need(name not in sys.modules, "APP_MODULE_NAMESPACE_COLLISION")
            module = ModuleType(name)
            module.__file__ = str(ROOT / relative)
            sys.modules[name] = module
            registered.append(name)
            exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
            modules.append(module)
    finally:
        for name in registered:
            del sys.modules[name]
    return tuple(modules)


def actual_prior(blobs, S):
    previous, acceptance, audit, candidate, report = (S.unique_json(blobs[f"{TWO_EVIDENCE}/{name}"]) for name in (
        "operation.json", TWO_ADMISSION, TWO_AUDIT, TWO_RESULT, TWO_REPORT,
    ))
    scope = acceptance["actual_evidence"]
    expected_source = {"commit": acceptance["source_commit"], "tree": acceptance["source_tree"]}
    cleanup = audit["cleanup_verified"]
    S.require(acceptance["decision"] == "ACCEPT_EXACT_DISPOSABLE_MIGRATION_MACHINERY"
              and audit["decision"] == "EXACT_MACHINERY_SUBSET_AND_CLEANUP_VERIFIED"
              and previous["source"] == expected_source == {"commit": audit["source_commit"], "tree": audit["source_tree"]}
              and expected_source["commit"] == candidate["source_commit"] == TWO_COMMIT
              and expected_source["tree"] == candidate["source_tree"]
              and acceptance["operation_run_id"] == audit["run_id"] == candidate["run_id"] == report["run_id"]
              == previous["run_id"] == TWO_RUN and candidate["container_id"] == audit["created_container_id"]
              == report["container_id"] and candidate["packet_sha256"] == audit["packet_sha256"]
              == report["approved_packet_sha256"] == PRIOR["operation.json"] and acceptance["operator_exit_code"] == 0
              and acceptance["independent_reviewer"] == audit["reviewer"]
              and acceptance["files_sha256"][TWO_AUDIT] == PRIOR[TWO_AUDIT]
              and acceptance["files_sha256"][TWO_RESULT] == audit["file_sha256"][TWO_RESULT] == PRIOR[TWO_RESULT]
              and acceptance["files_sha256"][TWO_REPORT] == audit["file_sha256"][TWO_REPORT] == PRIOR[TWO_REPORT],
              "APP_PRIOR_TWO_IDENTITY_AND_AUTHORITATIVE_ACCEPTANCE")
    S.require(candidate["status"] == audit["status"] == report["status"] == "PASS_MACHINERY_SUBSET_ONLY"
              and candidate["source_expected_sha256"] == audit["native_expected_sha256"] == held.EXPECTED_CATALOG
              and candidate["original_grantor_finalized"] is True
              and candidate["full8_noop"]["all_eight_columns_unchanged"] is True
              and type(candidate["business_assertions_qualified"]) is int and candidate["business_assertions_qualified"] == 0
              and acceptance["Posture"] == audit["posture"] == candidate["Posture"] == "D"
              and scope["immutable_source8_history"] == [held.PINS[held.INITIAL], held.PINS[held.APPEND]]
              and scope["genuine_applied_rows"] == 2 and scope["new_ledger_rows_on_repeat"] == 0
              and scope["ledger_columns_fingerprinted"] == 8 and scope["initial_native_checks"] == 29089
              and scope["initial_expression_rollback_checks"] == 416 and scope["ledger_checks_each_observation"] == 22
              and scope["second_deploy"] == "PASS_NO_PENDING" and scope["prisma_status"] == "PASS"
              and report["transport"]["unknown_closure"] is False and report["cleanup_full_container_identity_absent"] is True
              and len(cleanup) == 8 and all(flag is True for flag in cleanup.values()), "APP_PRIOR_TWO_PROOF_AND_CLOSURE")
    return previous, audit


def exact_cleanup_seam(raw):
    mains = [node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    attempts = [node for node in mains[0].body if isinstance(node, ast.Try) and node.finalbody] if len(mains) == 1 else []
    return len(attempts) == 1 and sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                                     and node.func.id == "cleanup" and not node.args and not node.keywords
                                     for statement in attempts[0].finalbody for node in ast.walk(statement)) == 1


def compose(tool_archive, run_id, *, draft=False):
    basis, two_plan, two_owner = mechanism()
    S, P = basis.S, basis.P
    base = two_plan.compose(tool_archive, run_id, draft=True)
    _, operation, blobs, inner, manifest, nested, files, archive = base
    S.require(exact_cleanup_seam(blobs[S.STEPS]), "APP_EXACT_OWNED_CLEANUP_SEAM")
    proof = held.prepare()
    pins = {**proof["source_files_sha256"], **SUPPORT,
            **{f"{TWO_EVIDENCE}/{name}": pin for name, pin in PRIOR.items()}}
    pins.pop(held.TWO)
    for name, pin in pins.items():
        data = held.source(ROOT, name, pin)
        S.require(name not in blobs or blobs[name] == data, "APP_SHARED_SOURCE_GRAPH_COLLISION")
        blobs[name] = data
    blobs.update({f"{HERE}/{name}": S.read(ROOT / HERE / name) for name in OWNER_FILES})
    previous, audit = actual_prior(blobs, S)
    held_review = S.unique_json(blobs[HELD_REVIEW])
    S.require(held_review["decision"] == "APPROVE_HELD_SOURCE_PREPARATION" and held_review["runtime"] == "NOT_RUN"
              and held_review["held_proof_sha256"] == S.sha(held.json_bytes(proof)), "APP_HELD_SOURCE_REVIEW_BINDING")
    S.require(run_id != TWO_RUN and operation["target"]["container_name"] != previous["target"]["container_name"]
              and operation["target"]["volume_name"] != previous["target"]["volume_name"]
              and operation["daemon"] == audit["daemon"] and operation["image"] == audit["image"], "APP_FRESH_TARGET_SAME_PROFILE")
    source_pins = {name: S.sha(raw) for name, raw in blobs.items()}
    directory = P.SCRATCH / f"wa-cloud-f0-app-source8-{run_id}"
    operation.update(
        schema=APP_OWNER_SCHEMA, status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_APP_REVIEW",
        source=None if draft else S.verify_committed(ROOT, blobs), source_pins=source_pins,
        source_aggregate_sha256=S.aggregate(source_pins), nested_manifest=P.bind(directory / "run-manifest.json", nested),
        archive=P.bind(directory / "source8.tar", archive),
        app_source8={"held_source_proof": proof, "prior_accepted_two_run": TWO_RUN,
                     "prior_acceptance_sha256": PRIOR[TWO_ADMISSION], "prior_closure_sha256": PRIOR[TWO_AUDIT],
                     "prior_closed_cid": audit["created_container_id"],
                     "fresh_live_noop_required": True, "status": "NOT_RUN", "app_login_roles": list(app_child.APP_ROLES)},
    )
    return (directory, operation, blobs, inner, manifest, nested, files, archive), (basis, two_plan, two_owner)


def prepare(tool_archive, *, draft=False):
    prepared, (basis, _, _) = compose(tool_archive, str(uuid.uuid4()), draft=draft)
    directory, operation, _, _, _, nested, files, archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.write_new(directory / "run-manifest.json", nested)
    P.write_new(directory / "source8.tar", archive)
    P.write_source(directory / "source8", files)
    path = directory / "operation.json"
    raw = S.encode(operation)
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "source_files": len(operation["source_pins"]), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    _, preliminary, _ = mechanism()
    P, S = preliminary.P, preliminary.S
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == APP_OWNER_SCHEMA and value["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_APP_REVIEW"), "APP_OWNING_PACKET_REQUIRED")
    prepared, modules = compose(Path(value["tools"]["path"]), value["run_id"], draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), "APP_OWNING_PACKET_DRIFT")
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, modules, raw


def review_bindings(operation, raw, two_plan):
    return {**two_plan.review_bindings(operation, raw), "accepted_two_sha256": PRIOR[TWO_ADMISSION],
            "app_held_proof_sha256": held.sha(held.json_bytes(operation["app_source8"]["held_source_proof"]))}


def exact_reviews(directory, operation, raw, modules):
    basis, two_plan, _ = modules
    bindings = review_bindings(operation, raw, two_plan)
    source, source_hash = basis.P.read_review(directory / "source-review.json",
        schema="workinants.cloud-f0-app-source8-source-review.v1", bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = basis.P.read_review(directory / "literal-review.json",
        schema="workinants.cloud-f0-app-source8-literal-review.v1",
        bindings={**bindings, "source_review_sha256": source_hash}, scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"], "APP_REVIEW_AUTHOR_MISMATCH")
    return {"source": source_hash, "literal": literal_hash,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def native_proof(receipts):
    fields = ("applied_rows", "catalog_check_counts", "ledger_checks", "oracle_expressions")
    return (type(receipts) is dict and set(receipts) == {"initial", "noop"}
            and receipts["initial"]["native_sha256"] == receipts["noop"]["native_sha256"]
            and all(tuple(receipt[name] for name in fields) == (2, {"PASS": 29089}, 22, 416) for receipt in receipts.values()))


def receipt_scope(value, proof):
    results = value["results"]
    return (value["status"] == app_child.APP_PASS and value["database_posture"] == "D"
            and value["evidence_complete"] is True and value["fixture_owner_bypass_restored"] is True
            and value["source_packet_unchanged_after"] is True and not value["unexpected"]
            and [row["case"] for row in results] == proof["fixture_proof"]["ordered_cases"]
            and [row["claim"] for row in results if row["claim"] is not None] == proof["fixture_proof"]["claim_ceilings"]
            and all(row["complete_record_sequence_match"] is True and row["operation_closed_before_observers"] is True
                    and row["tables_observed"] == 42 and row["all_other_tables_unchanged"] is True for row in results)
            and results[-1]["grants_retained"] == 15
            and [(row["case"], row["read_counts"]) for row in results if "read_counts" in row]
            == [(held.READS[0], {"existing_customer": 1}), (held.READS[1], {"existing_customer": 0})]
            and value["sanitization"] == {"context_secrets_or_hashes_found": False,
                                          "raw_errors_handles_statement_bodies_or_row_values_retained": False}
            and sum(row["stage"] == "GENUINE_APP_SCHEDULE_PREREQUISITE" and row.get("actual_app_committed") is True
                    for row in value["operations"]) == 1)


def owner_type(modules):
    basis, _, two = modules
    S, P = basis.S, basis.P

    class Owner(two.Owner):
        root = ROOT

        def read_source(self, relative):
            return S.read(ROOT / relative)

        def configure_program(self):
            super().configure_program()
            self.report["schema"] = "workinants.cloud-app-source8-owned-run-evidence.v1"
            self.report["app_source8"] = {"status": "NOT_RUN", "assertion_promotions": 0}
            p = self.program
            p.SAFE_FAILURE_STAGES |= {STAGE, "NATIVE_APP_AFTER", "LEDGER_APP_AFTER", "LEDGER_FINGERPRINT_app-after"}
            p.SAFE_FAILURE_CODES |= {"APP_FRESH_SOURCE8_NOT_PROVED", "APP_SCOPED_RECEIPT_NOT_CLOSED", "APP_POST_LEDGER_DRIFT"}
            original = p.event

            def observe(stage, status, **safe):
                original(stage, status, **safe)
                if (stage, status) == SEAM_EVENT:
                    self.report["stage"] = STAGE
                    p.save()
                    try:
                        self.run_app()
                    except BaseException:
                        if self.report["app_source8"]["status"] in ("NOT_RUN", "IN_PROGRESS"):
                            self.report["app_source8"]["status"] = "STOPPED_OR_UNCONFIRMED"
                        raise

            p.event = observe

        def prior_artifact(self, leaf):
            p = self.program
            raw, _ = p.closed_bytes(p.OUT / leaf, origin=p.STATE["origins"][leaf])
            return S.unique_json(raw)

        def run_app(self):
            p = self.program
            state = self.report["app_source8"]
            receipts = self.report["migration_results"]
            S.require(state["status"] == "NOT_RUN" and not self.transport.unknown
                      and all(p.STATE.get(key) is True for key in (
                          "first_deploy_closed_success", "finalization_verified", "two_applied_verified", "activated"))
                      and self.report["targets"][self.name]["finalization"] == "PASS"
                      and [r["operation"] for r in receipts] == ["deploy", "status", "deploy"]
                      and receipts[2]["no_pending_message_observed"] is True
                      and all(r["exit_code"] == 0 and r["container_id"] == self.resources.cid
                              and r["run_id"] == self.operation["run_id"] and r["packet_sha256"] == S.sha(self.raw)
                              for r in receipts)
                      and native_proof(self.report["native_results"]), "APP_FRESH_SOURCE8_NOT_PROVED")
            if self.resources.cid is None or self.resources.cid == self.operation["app_source8"].get("prior_closed_cid"):
                raise S.Held("APP_FRESH_SOURCE8_NOT_PROVED")
            native = self.prior_artifact("noop-native-before.json")
            before_ledger = self.prior_artifact("noop-ledger-observation.json")
            before_fingerprints = self.prior_artifact("initial-after-noop-fingerprints.json")
            S.require(p.digest(native) == self.report["native_results"]["noop"]["native_sha256"], "APP_FRESH_SOURCE8_NOT_PROVED")
            state.update(status="IN_PROGRESS", entered_after_same_live_full8_noop=True,
                         cid=self.resources.cid, volume_created_at=self.resources.volume_birth)
            p.save()
            location = p.OUT / "app-source8"
            value = app_child.coordinate(self, native, location)
            child_file = location / "app-write-two-results.json"
            raw, origin = p.closed_bytes(P.private_path(child_file, file=True))
            S.require(value == S.unique_json(raw), "APP_SCOPED_RECEIPT_NOT_CLOSED")
            expected_receipt = {
                "schema": "workinants.cloud-app-source8-result.v1", "run_id": self.operation["run_id"],
                "container_id": self.resources.cid, "volume_created_at": self.resources.volume_birth,
                "source_commit": self.operation["source"]["commit"], "source_tree": self.operation["source"]["tree"],
                "packet_sha256": S.sha(self.raw), "reviewed_content_sha256": held.FIXTURE_CONTENT,
                "reviewed_packet_sha256": self.operation["source_pins"][f"{held.PACKET}/fixtures.json"],
            }
            S.require(all(value.get(key) == wanted for key, wanted in expected_receipt.items()),
                      "APP_SCOPED_RECEIPT_NOT_CLOSED")
            p.STATE["origins"][child_file.relative_to(p.OUT).as_posix()] = origin
            state.update(child_status=value["status"], child_evidence_sha256=S.sha(raw),
                         cases_observed=len(value.get("results", [])))
            if "first_failure" in value:
                state["first_failure"] = value["first_failure"]
            S.require(not self.transport.unknown and receipt_scope(value, self.operation["app_source8"]["held_source_proof"]),
                      "APP_SCOPED_RECEIPT_NOT_CLOSED")
            after_native = p.collect_native(self.name, "NATIVE_APP_AFTER", "app-native-after.json")
            reg, after_ledger = p.ledger_observation(receipts[0], "APP_AFTER")
            _, ledger_evidence = p.compare_ledger(reg, after_ledger, after_native)
            after_fingerprints = p.fingerprints("app-after")
            S.require(native == after_native and before_ledger == after_ledger, "APP_POST_LEDGER_DRIFT")
            full8 = p.CATALOG["two"].compare_noop(before_fingerprints, after_fingerprints)
            p.write_safe("app-after-ledger-evidence.json", ledger_evidence)
            state.update(status=app_child.APP_PASS, full8=full8, native_sha256=p.digest(after_native))
            p.event(STAGE, app_child.APP_PASS)

        def postchecks(self):
            prepared, actual, raw = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation
                      and exact_reviews(self.directory, self.operation, self.raw, actual) == self.reviews,
                      "CLOUD_OWNING_SOURCE_REVIEW_DRIFT")
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True
                if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                    self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                S.require(self.report["app_source8"]["status"] == app_child.APP_PASS, "APP_SCOPED_RECEIPT_NOT_CLOSED")

    return Owner


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    actions = cli.add_subparsers(dest="action", required=True)
    make = actions.add_parser("prepare")
    make.add_argument("--draft", action="store_true")
    make.add_argument("--tool-archive", type=Path, required=True)
    verify = actions.add_parser("verify")
    verify.add_argument("--draft", action="store_true")
    verify.add_argument("--packet", type=Path, required=True)
    execute = actions.add_parser("execute")
    execute.add_argument(EXECUTE, action="store_true", dest="approved")
    execute.add_argument("--packet", type=Path, required=True)
    opts = cli.parse_args(argv)
    try:
        if opts.action == "prepare":
            print(held.json_bytes(prepare(opts.tool_archive, draft=opts.draft)).decode(), end="")
            return 0
        if opts.action == "verify":
            prepared, _, raw = read_closed(opts.packet, draft=opts.draft)
            print(held.json_bytes({"state": "HELD_VERIFIED", "sha256": held.sha(raw),
                                   "source_files": len(prepared[1]["source_pins"]), "runtime": "NOT_RUN"}).decode(), end="")
            return 0
        held.need(opts.approved, "EXPLICIT_APP_EXECUTION_REQUIRED")
        prepared, modules, raw = read_closed(opts.packet)
        basis, _, two = modules
        reviews = exact_reviews(prepared[0], prepared[1], raw, modules)
        os.umask(0o077)
        basis.P.write_new(prepared[0] / "attempt.json", basis.S.encode({
            "run_id": prepared[1]["run_id"], "packet_sha256": basis.S.sha(raw), "reviews": reviews,
        }))
        signal.signal(signal.SIGTERM, two.interrupt)
        signal.signal(signal.SIGHUP, two.interrupt)
        return owner_type(modules)(prepared, raw, reviews).run()
    except BaseException as error:
        observed = getattr(error, "code", None) or str(error)
        code = observed if type(observed) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", observed) else "APP_OWNING_OPERATION_HELD"
        print(held.json_bytes({"status": "HELD_OR_STOPPED", "code": code, "runtime_pass_claimed": False}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
