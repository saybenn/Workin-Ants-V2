"""Prepare, verify or operate the independently reviewed Cloud Consent owner."""

import argparse
import ast
import os
from pathlib import Path
import re
import signal
import stat
import sys
from types import ModuleType
import uuid

import child
import prepare as recipe
import protocol


ROOT = recipe.ROOT
HERE = Path(__file__).resolve().parent.relative_to(ROOT).as_posix()
ENVIRONMENT = "context/reconciliation/cloud-phase0-evidence/2026-11-27"
TWO = "scripts/sql-review/cloud-two-history-owned-v2"
TWO_RUN = "2f71c365-4c31-4000-837c-cdd72ac163ae"
TWO_ACCEPTED = f"{ENVIRONMENT}/two-2f71c365/acceptance.json"
TWO_ACCEPTED_SHA = "9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76"
APP_RUN = "2e59e073-ef6e-4895-bf05-f920767d8543"
APP_SOURCE = {"commit": "9fd12ffb882fd7704ab7b428c2073a6fead03296", "tree": "a1b2974622afa55cf41b5416ccf24195d6956f22"}
APP_EVIDENCE = f"{ENVIRONMENT}/app-2e59e073"
APP_CLOSURE = "independent-closure.json"
APP_CLOSURE_SHA256 = "39eb70917db0bffe61f2f6e0fb6f4f0741f7292d00ca4b73e31387ed7b71329a"
APP_ACCEPTANCE = "acceptance.json"
APP_ACCEPTANCE_SHA256 = "af7258881decbf7d78f1c413a4283f64d7b0235d48c3c7f2200f8b683a69f7cc"
APP_RAW = {
    "operation.json": "7495da1a762f3e25e7fe6e1a6d35a729dc535ba34dffa62444131d9d1fdfc49a",
    "evidence/run-evidence.json": "426bf87e47346532fc3f0998d71e415b131b103d56959c2a1757841f3a8e5e8c",
    "evidence/app-source8/app-write-two-results.json": "00e0746f1f32c76dd7246a51192482c5647cef0f10c960c18478dc73b3a24f1a",
    "operation-exit.json": "4a8165503726b33722de649d38ad279bd5dfac1692368455b39094d2991ce027",
}
MECHANISM = {
    "basis.py": "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af",
    "plan.py": "c308295d97ab1d794cf3a7a8b2f241b1c7266b8cb606704ada6f2c3de9c1decb",
    "operation.py": "8680611ab98322a192a70c72f373b1fb4858ddbbd184c1dc4f450bb98823b0c0",
}
OWNER_FILES = ("README.md", "OWNING.md", "prepare.py", "protocol.py", "child.py", "operation.py", "test_prepare.py", "test_operation.py")
SCHEMA = "workinants.cloud-f0-consent-immutable-owned-operation.v1"
SOURCE_REVIEW = "workinants.cloud-f0-consent-immutable-owned-source-review.v1"
LITERAL_REVIEW = "workinants.cloud-f0-consent-immutable-owned-literal-review.v1"
SOURCE_AUTHOR = "/root/cloud_review_prep"
EXECUTE = "--execute-reviewed-cloud-f0-consent-immutable-owned-v1"
STAGE = "CONSENT_IMMUTABLE"
SEAM = ("NOOP", "PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER")
POST_RESULT = "PASS_CATALOG_AND_FULL_LEDGER_AFTER_CONSENT"
SOURCE_SCOPES = ["exact_unchanged_source8_and_proven_cloud_transport", "two_named_rollback_only_consent_controls",
                 "synthetic_identity_only_and_exact_issuer_grants", "first_failure_sticky_closure_and_complete_state_parity"]
LITERAL_SCOPES = ["exact_live_socket_daemon_image_and_fresh_owned_target", "exact_source8_tool_archive_and_two_control_recipes",
                  "actual_app_issuer_and_separate_postgres_before_live_child", "post_case_full42_native_and_ledger_parity",
                  "bounded_sanitized_evidence_and_exact_independent_cleanup"]


def mechanism():
    modules = []
    registered = []
    try:
        for leaf, digest in MECHANISM.items():
            name = "_workinants_consent_two_owner" if leaf == "operation.py" else leaf.removesuffix(".py")
            path = ROOT / TWO / leaf
            info = path.lstat()
            protocol.require(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode)
                             and info.st_nlink == 1 and info.st_size <= 128 * 1024 and name not in sys.modules,
                             "CONSENT_FIXED_TWO_SOURCE_SHAPE")
            with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
                actual = os.fstat(stream.fileno())
                raw = stream.read(128 * 1024 + 1)
            protocol.require(actual == info and len(raw) == info.st_size and protocol.sha(raw) == digest,
                             "CONSENT_FIXED_TWO_SOURCE_DRIFT")
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            registered.append(name)
            exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
            modules.append(module)
    finally:
        for name in registered:
            del sys.modules[name]
    return tuple(modules)


def owning_seam(raw):
    tree = ast.parse(raw)
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    tries = [node for node in main.body if isinstance(node, ast.Try) and node.finalbody]
    if len(tries) != 1:
        return False
    protected = tries[0]

    def calls(statements, name):
        return [node for statement in statements for node in ast.walk(statement)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name]

    events = [node for node in calls(protected.body, "event") if len(node.args) == len(SEAM)
              and all(isinstance(arg, ast.Constant) and arg.value == expected for arg, expected in zip(node.args, SEAM, strict=True))]
    cleanup = calls(protected.finalbody, "cleanup")
    return len(events) == len(cleanup) == 1 and not cleanup[0].args and not cleanup[0].keywords


def prior_app(blobs, S):
    info, report, component, exit_record = (S.unique_json(blobs[f"{APP_EVIDENCE}/{name}"]) for name in APP_RAW)
    pins = info["source_pins"]
    state = report["app_source8"]
    app_pass = "PASS_FINITE_TWO_APP_WRITE_CRITERIA_ONLY"
    S.require(info["source"] == APP_SOURCE and report["approved_commit"] == component["source_commit"] == APP_SOURCE["commit"]
              and report["approved_tree"] == component["source_tree"] == APP_SOURCE["tree"]
              and info["run_id"] == report["run_id"] == component["run_id"] == APP_RUN
              and report["approved_packet_sha256"] == component["packet_sha256"] == APP_RAW["operation.json"]
              and pins[child.APP_CHILD] == child.APP_CHILD_SHA256
              and pins[recipe.APP_TRANSPORT] == recipe.PINS[recipe.APP_TRANSPORT] and pins[recipe.CONTEXT] == recipe.PINS[recipe.CONTEXT]
              and report["status"] == "PASS_MACHINERY_SUBSET_ONLY" and state["status"] == component["status"] == app_pass
              and report["container_id"] == state["cid"] == component["container_id"]
              and report["volume_created_at"] == state["volume_created_at"] == component["volume_created_at"]
              and state["full8"]["all_eight_columns_unchanged"] is True and component["evidence_complete"] is True
              and state["child_evidence_sha256"] == APP_RAW["evidence/app-source8/app-write-two-results.json"]
              and report["cleanup"] == "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
              and report["cleanup_full_container_identity_absent"] is True and report["transport"]["unknown_closure"] is False
              and exit_record["exit_code"] == 0, "CONSENT_PROVEN_APP_TRANSPORT_IDENTITY")
    closure, acceptance = (S.unique_json(blobs[f"{APP_EVIDENCE}/{name}"]) for name in (APP_CLOSURE, APP_ACCEPTANCE))
    n = acceptance["actual"]
    absence = closure["cleanup_verified"]
    S.require(acceptance["decision"] == "ACCEPT_EXACT_SCOPED_APP_SQL_CRITERIA_AND_CLEANUP"
              and closure["decision"] == "EXACT_APP_FINITE_TWO_WRITE_CRITERIA_AND_CLEANUP_VERIFIED"
              and acceptance["source_commit"] == closure["source_commit"] == APP_SOURCE["commit"]
              and acceptance["source_tree"] == closure["source_tree"] == APP_SOURCE["tree"]
              and acceptance["run_id"] == closure["run_id"] == APP_RUN
              and acceptance["operator_exit_code"] == closure["operator_exit_code"] == 0
              and acceptance["independent_reviewer"] == closure["reviewer"] != SOURCE_AUTHOR
              and acceptance["independent_closure_sha256"] == APP_CLOSURE_SHA256
              and acceptance["packet_sha256"] == closure["packet_sha256"] == APP_RAW["operation.json"]
              and all(acceptance["archived_files_sha256"][leaf] == closure["file_sha256"][leaf] == digest
                      for leaf, digest in APP_RAW.items() if leaf != "operation-exit.json")
              and closure["created_container_id"] == report["container_id"]
              and closure["created_volume"]["created_at"] == report["volume_created_at"]
              and closure["created_volume"]["name"] == info["target"]["volume_name"]
              and closure["daemon"] == info["daemon"] and closure["image"] == info["image"]
              and n["native_checks"] == 29089 and n["ledger_checks"] == 22 and n["expression_observations"] == 416
              and n["genuine_migration_rows"] == 2 and n["unchanged_full8_ledger_fingerprints"] is True
              and n["independent_cleanup"] is True and len(absence) == 9 and all(value is True for value in absence.values()),
              "CONSENT_INDEPENDENT_APP_CLOSURE_IDENTITY")
    return info, report


def compose(tool_archive, run_id, fixture_id, *, draft=False):
    protocol.require(protocol.uuid4(run_id) and protocol.uuid4(fixture_id) and run_id != fixture_id, "CONSENT_FRESH_RUN_IDENTITIES")
    basis, two_plan, two_owner = mechanism()
    S, P = basis.S, basis.P
    _, operation, blobs, inner, manifest, nested, files, archive = two_plan.compose(tool_archive, run_id, draft=True)
    S.require(owning_seam(blobs[S.STEPS]), "CONSENT_EXACT_OWNER_PRE_CLEANUP_SEAM")
    proof, assets = recipe.assemble(fixture_id)
    pins = {**proof["source_pins"], TWO_ACCEPTED: TWO_ACCEPTED_SHA, child.APP_CHILD: child.APP_CHILD_SHA256,
            **{f"{APP_EVIDENCE}/{name}": value for name, value in APP_RAW.items()},
            f"{APP_EVIDENCE}/{APP_CLOSURE}": APP_CLOSURE_SHA256,
            f"{APP_EVIDENCE}/{APP_ACCEPTANCE}": APP_ACCEPTANCE_SHA256}
    for name, digest in pins.items():
        raw = S.pinned(ROOT, name, digest)
        S.require(name not in blobs or blobs[name] == raw, "CONSENT_SOURCE_GRAPH_COLLISION")
        blobs[name] = raw
    blobs.update({f"{HERE}/{name}": S.read(ROOT / HERE / name) for name in OWNER_FILES})
    app, app_report = prior_app(blobs, S)
    two_acceptance = S.unique_json(blobs[TWO_ACCEPTED])
    two_scope = two_acceptance["actual_evidence"]
    S.require(two_acceptance["operation_run_id"] == TWO_RUN
              and two_acceptance["decision"] == "ACCEPT_EXACT_DISPOSABLE_MIGRATION_MACHINERY"
              and two_acceptance["operator_exit_code"] == 0 and two_acceptance["assertion_promotions"] == 0
              and two_scope["immutable_source8_history"] == proof["source8_history_sha256"]
              and two_scope["genuine_applied_rows"] == 2 and two_scope["new_ledger_rows_on_repeat"] == 0
              and two_scope["ledger_columns_fingerprinted"] == 8
              and two_scope["controlled_cleanup"] == "INDEPENDENT_EXACT_CONTAINER_VOLUME_AND_PRIVATE_ABSENCE"
              and operation["native_expected_sha256"] == recipe.SHA_CATALOG
              and run_id not in (TWO_RUN, APP_RUN) and run_id != fixture_id
              and operation["daemon"] == app["daemon"] and operation["image"] == app["image"]
              and all(operation["target"][leaf] != app["target"][leaf] for leaf in ("container_name", "volume_name")),
              "CONSENT_FRESH_OWNER_AND_PROVEN_TWO_HISTORY")
    directory = P.SCRATCH / f"wa-cloud-f0-consent-immutable-{run_id}"
    sources = {name: S.sha(value) for name, value in blobs.items()}
    operation.update(
        schema=SCHEMA, status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_CONSENT_REVIEWS",
        source=None if draft else S.verify_committed(ROOT, blobs), source_pins=sources,
        source_aggregate_sha256=S.aggregate(sources), nested_manifest=P.bind(directory / "run-manifest.json", nested),
        archive=P.bind(directory / "source8.tar", archive),
        consent_immutable={"recipe": proof, "recipe_sha256": protocol.sha(protocol.canonical(proof)),
                           "status": "NOT_RUN", "active_child_roles": list(child.ROLES),
                           "prior_app_run_id": APP_RUN, "prior_app_cid": app_report["container_id"],
                           "prior_app_independent_closure_sha256": APP_CLOSURE_SHA256, "prior_two_acceptance_sha256": TWO_ACCEPTED_SHA,
                           "fresh_live_noop_required": True},
    )
    return (directory, operation, blobs, inner, manifest, nested, files, archive), (basis, two_plan, two_owner), assets


def prepare(tool_archive, *, draft=False):
    prepared, (basis, _, _), _ = compose(tool_archive, str(uuid.uuid4()), str(uuid.uuid4()), draft=draft)
    directory, operation, _, _, _, nested, files, archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    for leaf, raw in (("run-manifest.json", nested), ("source8.tar", archive), ("operation.json", S.encode(operation))):
        P.write_new(directory / leaf, raw)
    P.write_source(directory / "source8", files)
    return {"packet": str(directory / "operation.json"), "sha256": S.sha(S.encode(operation)),
            "source_files": len(operation["source_pins"]), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    basis, _, _ = mechanism()
    P, S = basis.P, basis.S
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == SCHEMA and value["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_CONSENT_REVIEWS"), "CONSENT_EXACT_OWNING_PACKET_REQUIRED")
    prepared, modules, assets = compose(Path(value["tools"]["path"]), value["run_id"],
                                         value["consent_immutable"]["recipe"]["fixture_run_id"], draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), "CONSENT_OWNING_PACKET_DRIFT")
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, modules, raw, assets


def review_bindings(operation, raw, two_plan):
    details = operation["consent_immutable"]
    return {**two_plan.review_bindings(operation, raw), "consent_recipe_sha256": details["recipe_sha256"],
            "fixture_run_id": details["recipe"]["fixture_run_id"], "accepted_two_sha256": TWO_ACCEPTED_SHA,
            "independent_app_closure_sha256": details["prior_app_independent_closure_sha256"]}


def exact_reviews(directory, operation, raw, modules):
    basis, two_plan, _ = modules
    bindings = review_bindings(operation, raw, two_plan)
    source, source_sha = basis.P.read_review(directory / "source-review.json", schema=SOURCE_REVIEW,
                                             bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_sha = basis.P.read_review(directory / "literal-review.json", schema=LITERAL_REVIEW,
                                               bindings={**bindings, "source_review_sha256": source_sha}, scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"] == SOURCE_AUTHOR, "CONSENT_REVIEW_AUTHOR_MISMATCH")
    return {"source": source_sha, "literal": literal_sha,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def native_proof(results):
    return (type(results) is dict and set(results) == {"initial", "noop"}
            and results["initial"]["native_sha256"] == results["noop"]["native_sha256"]
            and all((row["applied_rows"], row["catalog_check_counts"], row["ledger_checks"], row["oracle_expressions"])
                    == (2, {"PASS": 29089}, 22, 416) for row in results.values()))


def child_passes(value):
    if (value.get("status") != child.PASS or value.get("first_failure") is not None
            or value.get("complete_final_client_closure") is not True or value.get("evidence_complete") is not True
            or value.get("remote_outcome_unconfirmed") is not False or value.get("posture") != "D"
            or type(value.get("assertion_promotions")) is not int or value["assertion_promotions"] != 0):
        return False
    diagnostic = {"terminal_client_exit_3": True, "before_marker_only": True, "no_success_acknowledgment": True,
                  "exact_source_diagnostic": True, "sqlstate": protocol.SQLSTATE,
                  "source_body_sha256": protocol.BODY_SHA256, "source_body_line": protocol.BODY_LINE}
    expected = [{"case": name, "status": "PASS_EXACT_DENIED_ROLLBACK_ONLY", "diagnostic": diagnostic,
                 "app_and_issuer_closed": True, "tables_unchanged": 42, "original_triggers_verified": 100,
                 "issued_grants_exact": (index + 1) * 3, "exact_consent_residue_zero": True,
                 "native_catalog_unchanged": True} for index, name in enumerate(protocol.CASES)]
    return protocol.canonical(value.get("results")) == protocol.canonical(expected)


def owner_type(modules):
    basis, _, two = modules
    S, P = basis.S, basis.P

    class Owner(two.Owner):
        root = ROOT

        def __init__(self, prepared, raw, reviews, assets):
            self.consent_assets = assets
            super().__init__(prepared, raw, reviews)

        def configure_program(self):
            super().configure_program()
            self.report.update(schema="workinants.cloud-f0-consent-immutable-owned-run-evidence.v1",
                               consent_immutable={"status": "NOT_RUN", "assertion_promotions": 0})
            p = self.program
            _, adapter = child.supports(self.blobs)
            p.SAFE_FAILURE_STAGES |= {STAGE, "NATIVE_CONSENT_AFTER", "LEDGER_CONSENT_AFTER", "LEDGER_FINGERPRINT_consent-after"}
            p.SAFE_FAILURE_CODES |= child.FAILURES | adapter["CLOSED_ERRORS"] | {
                "CONSENT_FRESH_SOURCE8_NOT_PROVED", "CONSENT_CHILD_RESULT_NOT_CLOSED", "CONSENT_POST_LEDGER_DRIFT",
            }
            original = p.event

            def observe(stage, status, **safe):
                original(stage, status, **safe)
                if (stage, status) == SEAM:
                    self.report["stage"] = STAGE
                    p.save()
                    try:
                        self.run_consent()
                    except BaseException:
                        state = self.report["consent_immutable"]
                        if state["status"] in ("NOT_RUN", "IN_PROGRESS"):
                            state["status"] = child.STOP
                        raise

            p.event = observe

        def artifact(self, leaf):
            p = self.program
            return S.unique_json(p.closed_bytes(p.OUT / leaf, origin=p.STATE["origins"][leaf])[0])

        def run_consent(self):
            p = self.program
            state = self.report["consent_immutable"]
            receipts = self.report["migration_results"]
            cid = self.resources.cid
            details = self.operation["consent_immutable"]
            proof = details["recipe"]
            S.require(state["status"] == "NOT_RUN" and not self.transport.unknown and type(cid) is str
                      and re.fullmatch(r"[0-9a-f]{64}", cid) and cid != details["prior_app_cid"]
                      and all(p.STATE.get(key) is True for key in ("first_deploy_closed_success", "finalization_verified",
                                                                   "two_applied_verified", "activated"))
                      and self.report["targets"][self.name]["finalization"] == "PASS"
                      and [record["operation"] for record in receipts] == ["deploy", "status", "deploy"]
                      and receipts[2]["no_pending_message_observed"] is True
                      and all(record["exit_code"] == 0 and record["container_id"] == cid
                              and record["run_id"] == self.operation["run_id"] and record["packet_sha256"] == S.sha(self.raw)
                              for record in receipts) and native_proof(self.report["native_results"]), "CONSENT_FRESH_SOURCE8_NOT_PROVED")
            native = self.artifact("noop-native-before.json")
            before_ledger = self.artifact("noop-ledger-observation.json")
            before_fingerprints = self.artifact("initial-after-noop-fingerprints.json")
            S.require(p.digest(native) == self.report["native_results"]["noop"]["native_sha256"], "CONSENT_FRESH_SOURCE8_NOT_PROVED")
            state.update(status="IN_PROGRESS", entered_after_same_live_full8_noop=True, cid=cid, volume_created_at=self.resources.volume_birth)
            p.save()
            reference, result = child.coordinate(self, native, proof, self.consent_assets)
            path = reference["path"]
            S.require(path == "noop-" + child.RESULT_LEAF and self.artifact(path) == result, "CONSENT_CHILD_RESULT_NOT_CLOSED")
            identity = {"schema": child.RESULT_SCHEMA, "run_id": self.operation["run_id"], "fixture_run_id": proof["fixture_run_id"],
                        "container_id": cid, "volume_created_at": self.resources.volume_birth,
                        "source_commit": self.operation["source"]["commit"], "source_tree": self.operation["source"]["tree"],
                        "packet_sha256": S.sha(self.raw), "consent_recipe_sha256": details["recipe_sha256"],
                        "full_native_baseline_sha256": p.digest(native), "case_id": recipe.CASE_ID,
                        "assertion_id": recipe.ASSERTION, "case_order": list(protocol.CASES)}
            S.require(all(result.get(key) == value for key, value in identity.items()), "CONSENT_CHILD_RESULT_NOT_CLOSED")
            state.update(child_status=result["status"], child_receipt=reference, cases_observed=len(result["results"]))
            if result["first_failure"] is not None:
                state["first_failure"] = result["first_failure"]
            if not self.transport.unknown and result["complete_final_client_closure"] is True:
                after_native = p.collect_native(self.name, "NATIVE_CONSENT_AFTER", "consent-native-after.json")
                reg, after_ledger = p.ledger_observation(receipts[0], "CONSENT_AFTER")
                final_native = p.collect_native(self.name, "NATIVE_CONSENT_AFTER", "consent-native-after-ledger.json")
                result_ledger, ledger_evidence = p.compare_ledger(reg, after_ledger, final_native)
                after_fingerprints = p.fingerprints("consent-after")
                S.require(native == after_native == final_native and before_ledger == after_ledger
                          and len(result_ledger["checks"]) == 22, "CONSENT_POST_LEDGER_DRIFT")
                full8 = p.CATALOG["two"].compare_noop(before_fingerprints, after_fingerprints)
                p.write_safe("consent-after-ledger-evidence.json", ledger_evidence)
                state.update(postcheck=POST_RESULT, full8=full8, native_sha256=p.digest(final_native))
            S.require(not self.transport.unknown and state.get("postcheck") == POST_RESULT and child_passes(result),
                      "CONSENT_CHILD_RESULT_NOT_CLOSED")
            state["status"] = child.PASS
            p.event(STAGE, child.PASS)

        def postchecks(self):
            prepared, actual, raw, assets = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation and assets == self.consent_assets
                      and exact_reviews(self.directory, self.operation, self.raw, actual) == self.reviews,
                      "CLOUD_OWNING_SOURCE_REVIEW_DRIFT")
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True
                if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                    self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                result = self.report["consent_immutable"]
                S.require(result["status"] == child.PASS and result["postcheck"] == POST_RESULT, "CONSENT_CHILD_RESULT_NOT_CLOSED")

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
            print(protocol.canonical(prepare(opts.tool_archive, draft=opts.draft)).decode())
            return 0
        if opts.action == "verify":
            prepared, _, raw, _ = read_closed(opts.packet, draft=opts.draft)
            print(protocol.canonical({"state": "HELD_VERIFIED", "sha256": protocol.sha(raw),
                                      "source_files": len(prepared[1]["source_pins"]), "runtime": "NOT_RUN"}).decode())
            return 0
        protocol.require(opts.approved, "CONSENT_EXPLICIT_REVIEWED_EXECUTION_REQUIRED")
        prepared, modules, raw, assets = read_closed(opts.packet)
        basis, _, two = modules
        reviews = exact_reviews(prepared[0], prepared[1], raw, modules)
        os.umask(0o077)
        basis.P.write_new(prepared[0] / "attempt.json", basis.S.encode({
            "run_id": prepared[1]["run_id"], "packet_sha256": basis.S.sha(raw), "reviews": reviews,
        }))
        signal.signal(signal.SIGHUP, two.interrupt)
        signal.signal(signal.SIGTERM, two.interrupt)
        return owner_type(modules)(prepared, raw, reviews, assets).run()
    except BaseException as error:
        code = getattr(error, "code", None) or str(error)
        safe = code if type(code) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", code) else "CONSENT_OWNER_UNCONFIRMED"
        print(protocol.canonical({"status": "HELD_OR_STOPPED", "code": safe, "runtime_pass_claimed": False}).decode())
        return 1


if __name__ == "__main__":
    sys.exit(main())
