"""Prepare or run a separately reviewed, disposable source8 lease-renewal owner."""

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


ROOT = recipe.ROOT
HERE = Path(__file__).resolve().parent.relative_to(ROOT).as_posix()
TWO = "scripts/sql-review/cloud-two-history-owned-v2"
MECHANISM = {
    "basis.py": "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af",
    "plan.py": "c308295d97ab1d794cf3a7a8b2f241b1c7266b8cb606704ada6f2c3de9c1decb",
    "operation.py": "8680611ab98322a192a70c72f373b1fb4858ddbbd184c1dc4f450bb98823b0c0",
}
FILES = ("README.md", "OWNING.md", "prepare.py", "test_prepare.py", "child.py", "operation.py", "test_operation.py")
SCHEMA = "workinants.cloud-lease-renew-source8-owned-operation.v1"
SOURCE_REVIEW = "workinants.cloud-lease-renew-source8-source-review.v1"
LITERAL_REVIEW = "workinants.cloud-lease-renew-source8-literal-review.v1"
EXECUTE = "--execute-reviewed-cloud-lease-renew-source8-v1"
AUTHOR = "/root/cloud_review_prep"
SOURCE_SCOPES = ["exact_accepted_two_app_worker_and_unchanged_source8", "four_historical_mutations_and_renewal_only_ceiling",
                 "exact_roles_issuer_fence_and_current_live_reserves", "rollback_sticky_closure_and_post_scope"]
LITERAL_SCOPES = ["fresh_exact_daemon_image_resources_and_committed_source", "reviewed_real_tool_and_source8_reproduction",
                  "original_grantor_current_auth_and_full8_before_child", "actual_live_deadline_and_four_finite_operations",
                  "complete_state_native_ledger_closure_and_exact_cleanup"]
SEAM = ("NOOP", "PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER")
POST = "LEASE_RENEW_AFTER"
POST_PASS = "PASS_NATIVE_AND_FULL8_LEDGER_UNCHANGED"
CODES = {"LEASE_RENEW_FRESH_SOURCE8_UNPROVED", "LEASE_RENEW_CHILD_RECEIPT_UNCONFIRMED", "LEASE_RENEW_POST_PARITY_UNCONFIRMED"}


def mechanism():
    modules, names = [], []
    try:
        for leaf, digest in MECHANISM.items():
            name = "_workinants_lease_two_owner" if leaf == "operation.py" else leaf.removesuffix(".py")
            path = ROOT / TWO / leaf
            info = path.lstat()
            recipe.require(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                           and info.st_size <= 128 * 1024 and name not in sys.modules, "LEASE_RENEW_FIXED_TWO_SOURCE")
            with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
                opened = os.fstat(stream.fileno())
                raw = stream.read(128 * 1024 + 1)
            recipe.require(opened == info and len(raw) == info.st_size and recipe.sha(raw) == digest, "LEASE_RENEW_FIXED_TWO_SOURCE")
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            names.append(name)
            exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
            modules.append(module)
    finally:
        for name in names:
            del sys.modules[name]
    return tuple(modules)


def exact_seam(raw):
    statements = ast.parse(raw).body
    main = child.select(statements, {"main"})[0]
    tries = [item for item in main.body if isinstance(item, ast.Try) and item.finalbody]
    if len(tries) != 1:
        return False

    def calls(terms, name):
        return [node for item in terms for node in ast.walk(item) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == name]

    observed = [node for node in calls(tries[0].body, "event") if len(node.args) == 2 and all(
        isinstance(arg, ast.Constant) and arg.value == expected for arg, expected in zip(node.args, SEAM, strict=True))]
    cleanup = calls(tries[0].finalbody, "cleanup")
    return len(observed) == len(cleanup) == 1 and not cleanup[0].args and not cleanup[0].keywords


def compose(tool_archive, run_id, fixture_id, *, draft=False):
    recipe.require(all(type(value) is str and recipe.UUID.fullmatch(value) and uuid.UUID(value).version == 4
                       for value in (run_id, fixture_id)) and run_id != fixture_id, "LEASE_RENEW_FRESH_PACKET_IDENTITIES")
    modules = mechanism()
    basis, two_plan, _ = modules
    S, P = basis.S, basis.P
    _, packet, blobs, inner, manifest, nested, files, archive = two_plan.compose(tool_archive, run_id, draft=True)
    S.require(exact_seam(blobs[S.STEPS]), "LEASE_RENEW_PRE_CLEANUP_SEAM")
    proof, assets = recipe.assemble(fixture_id)
    for name, digest in proof["source_pins"].items():
        raw = S.pinned(ROOT, name, digest)
        S.require(name not in blobs or blobs[name] == raw, "LEASE_RENEW_SOURCE_COLLISION")
        blobs[name] = raw
    blobs.update({f"{HERE}/{leaf}": S.read(ROOT / HERE / leaf) for leaf in FILES})
    past = S.unique_json(blobs[f"{recipe.PRIOR_WORKER}/operation.json"])
    audit = S.unique_json(blobs[recipe.WORKER_CLOSURE])
    two = S.unique_json(blobs[f"{recipe.EVIDENCE}/two-2f71c365/acceptance.json"])
    S.require(run_id not in (recipe.WORKER_RUN, two["operation_run_id"])
              and all(packet["target"][leaf] != past["target"][leaf] for leaf in ("container_name", "volume_name"))
              and packet["daemon"] == past["daemon"] == audit["daemon"] and packet["image"] == past["image"] == audit["image"]
              and packet["native_expected_sha256"] == proof["native_expected_sha256"], "LEASE_RENEW_CURRENT_DAEMON_OR_TARGET")
    directory = P.SCRATCH / f"wa-cloud-f0-lease-renew-source8-{run_id}"
    pins = {name: S.sha(value) for name, value in blobs.items()}
    packet.update(schema=SCHEMA, status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_LEASE_RENEW_REVIEWS",
                  source=None if draft else S.verify_committed(ROOT, blobs), source_pins=pins, source_aggregate_sha256=S.aggregate(pins),
                  nested_manifest=P.bind(directory / "run-manifest.json", nested), archive=P.bind(directory / "source8.tar", archive),
                  lease_renew={"recipe": proof, "recipe_sha256": recipe.sha(recipe.canonical(proof)), "status": "NOT_RUN",
                               "prior_closed_worker_cid": audit["container_id"], "roles": list(child.ROLES)})
    return (directory, packet, blobs, inner, manifest, nested, files, archive), modules, assets


def make_packet(tool_archive, *, draft=False):
    prepared, (basis, _, _), _ = compose(tool_archive, str(uuid.uuid4()), str(uuid.uuid4()), draft=draft)
    directory, packet, _, _, _, nested, files, archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    for name, raw in (("run-manifest.json", nested), ("source8.tar", archive)):
        P.write_new(directory / name, raw)
    P.write_source(directory / "source8", files)
    raw = S.encode(packet)
    path = directory / "operation.json"
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "source_files": len(packet["source_pins"]), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    basis, _, _ = mechanism()
    S, P = basis.S, basis.P
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    record = S.unique_json(raw)
    S.require(record["schema"] == SCHEMA and record["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_LEASE_RENEW_REVIEWS"), "LEASE_RENEW_COMMITTED_PACKET_REQUIRED")
    prepared, modules, assets = compose(Path(record["tools"]["path"]), record["run_id"],
                                         record["lease_renew"]["recipe"]["fixture_run_id"], draft=draft)
    directory, value, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(value), "LEASE_RENEW_IMMUTABLE_PACKET_DRIFT")
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, modules, raw, assets


def review_bindings(packet, raw, two_plan):
    details = packet["lease_renew"]
    return {**two_plan.review_bindings(packet, raw), "fixture_run_id": details["recipe"]["fixture_run_id"],
            "lease_renew_recipe_sha256": details["recipe_sha256"], "accepted_worker_sha256": recipe.PINS[recipe.WORKER_ACCEPTED]}


def exact_reviews(directory, packet, raw, modules):
    basis, plan, _ = modules
    bindings = review_bindings(packet, raw, plan)
    source, source_hash = basis.P.read_review(directory / "source-review.json", schema=SOURCE_REVIEW,
                                              bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = basis.P.read_review(directory / "literal-review.json", schema=LITERAL_REVIEW,
                                                bindings={**bindings, "source_review_sha256": source_hash}, scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"] == AUTHOR, "LEASE_RENEW_REVIEW_AUTHOR")
    return {"source": source_hash, "literal": literal_hash, "source_reviewer": source["reviewer"],
            "literal_reviewer": literal["reviewer"]}


def native_gate(observed):
    return (type(observed) is dict and set(observed) == {"initial", "noop"}
            and observed["initial"]["native_sha256"] == observed["noop"]["native_sha256"]
            and all((row["applied_rows"], row["catalog_check_counts"], row["ledger_checks"], row["oracle_expressions"])
                    == (2, {"PASS": 29089}, 22, 416) for row in observed.values()))


def passes(result):
    if (result.get("status") != child.PASS or result.get("first_failure") is not None
            or result.get("complete_final_client_closure") is not True or result.get("evidence_complete") is not True
            or result.get("remote_outcome_unconfirmed") is not False or result.get("posture") != "D"
            or type(result.get("assertion_promotions")) is not int or result["assertion_promotions"] != 0):
        return False
    claim, renew, *denials = recipe.CASES
    case_shape = [{"case": claim, "exact_committed_work_change": True, "changed_rows": 1,
                   "live_fence": 1, "exact_captured_claim_xid": True, "other_tables_unchanged": True},
                  {"case": renew, "exact_committed_work_change": True, "changed_rows": 1, "live_fence": 1,
                   "all_other_domain_fields_unchanged": True, "tables_observed": 42}]
    case_shape.extend({"case": name, "exact_denial": True, "sqlstate": "P0001", "body_line": recipe.GUARD_LINE,
                       "body_sha256": recipe.GUARD_SHA, "unchanged_live_renewed_row": True, "tables_unchanged": 42}
                      for name in denials)
    operations = result.get("operations", ())
    scope = [(row["case"], row["exact_compared_to_step"]) for row in operations if row["stage"] == "RESTRICTED_LIVE_RENEW_SCOPE"]
    retention = [row["grants"] for row in operations if row["stage"] == "ISSUER_RETENTION" and row["exact"] is True]
    return (recipe.canonical(result.get("results")) == recipe.canonical(case_shape)
            and scope == [(name, True) for name in (renew, *denials)] and retention == [2, 4, 5, 6])


def owner_type(modules):
    basis, _, two = modules
    S = basis.S

    class Owner(two.Owner):
        root = ROOT

        def __init__(self, prepared, raw, reviews, assets):
            self.renewal_assets = assets
            super().__init__(prepared, raw, reviews)

        def configure_program(self):
            super().configure_program()
            self.report.update(schema="workinants.cloud-lease-renew-source8-owned-run-evidence.v1",
                               lease_renew={"status": "NOT_RUN", "assertion_promotions": 0})
            p = self.program
            p.SAFE_FAILURE_STAGES |= {child.STAGE, f"NATIVE_{POST}", f"LEDGER_{POST}", "LEDGER_FINGERPRINT_lease-renew-after"}
            p.SAFE_FAILURE_CODES |= child.FAILURE_CODES | CODES
            emit = p.event

            def event(stage, status, **safe):
                emit(stage, status, **safe)
                if (stage, status) == SEAM:
                    self.report["stage"] = child.STAGE
                    p.save()
                    try:
                        self.run_renewal()
                    except BaseException:
                        self.report["lease_renew"]["status"] = child.STOP
                        raise

            p.event = event

        def artifact(self, leaf):
            p = self.program
            return S.unique_json(p.closed_bytes(p.OUT / leaf, origin=p.STATE["origins"][leaf])[0])

        def run_renewal(self):
            p = self.program
            state = self.report["lease_renew"]
            plan = self.operation["lease_renew"]
            cid, birth = self.resources.cid, self.resources.volume_birth
            receipts = self.report["migration_results"]
            S.require(state["status"] == "NOT_RUN" and not self.transport.unknown and type(cid) is str and S.HASH.fullmatch(cid)
                      and cid != plan["prior_closed_worker_cid"] and type(birth) is str and 0 < len(birth) <= 256
                      and self.report["targets"][self.name]["volume_created_at"] == birth
                      and self.report["targets"][self.name]["finalization"] == "PASS"
                      and all(p.STATE.get(key) is True for key in ("first_deploy_closed_success", "finalization_verified", "two_applied_verified", "activated"))
                      and [item["operation"] for item in receipts] == ["deploy", "status", "deploy"]
                      and receipts[-1]["no_pending_message_observed"] is True
                      and all(type(item["exit_code"]) is int and item["exit_code"] == 0 and item["container_id"] == cid
                              and item["run_id"] == self.operation["run_id"] and item["packet_sha256"] == S.sha(self.raw) for item in receipts)
                      and native_gate(self.report["native_results"]), "LEASE_RENEW_FRESH_SOURCE8_UNPROVED")
            native = self.artifact("noop-native-before.json")
            before_ledger = self.artifact("noop-ledger-observation.json")
            fingerprints = self.artifact("initial-after-noop-fingerprints.json")
            S.require(p.digest(native) == self.report["native_results"]["noop"]["native_sha256"], "LEASE_RENEW_FRESH_SOURCE8_UNPROVED")
            state.update(status="IN_PROGRESS", container_id=cid, volume_created_at=birth, entered_after_same_run_full8_noop=True)
            p.save()
            reference, outcome = child.coordinate(self, native, plan["recipe"], self.renewal_assets)
            path = reference["path"]
            identity = {"schema": child.SCHEMA, "run_id": self.operation["run_id"], "fixture_run_id": plan["recipe"]["fixture_run_id"],
                        "source": self.operation["source"], "packet_sha256": S.sha(self.raw), "recipe_sha256": plan["recipe_sha256"],
                        "native_baseline_sha256": p.digest(native), "container_id": cid, "volume_created_at": birth}
            S.require(path == "noop-" + child.LEAF and outcome == self.artifact(path)
                      and all(outcome.get(key) == value for key, value in identity.items()), "LEASE_RENEW_CHILD_RECEIPT_UNCONFIRMED")
            state.update(child_receipt=reference, cases_observed=len(outcome["results"]), first_failure=outcome["first_failure"])
            if outcome["complete_final_client_closure"] is True and not self.transport.unknown:
                post = p.collect_native(self.name, f"NATIVE_{POST}", "lease-renew-native-after.json")
                registered, ledger = p.ledger_observation(receipts[0], POST)
                final_native = p.collect_native(self.name, f"NATIVE_{POST}", "lease-renew-native-after-ledger.json")
                report, ledger_proof = p.compare_ledger(registered, ledger, final_native)
                after = p.fingerprints("lease-renew-after")
                S.require(post == native == final_native and before_ledger == ledger and len(report["checks"]) == 22,
                          "LEASE_RENEW_POST_PARITY_UNCONFIRMED")
                full = p.CATALOG["two"].compare_noop(fingerprints, after)
                p.write_safe("lease-renew-after-ledger-evidence.json", ledger_proof)
                state.update(postcheck=POST_PASS, full8=full, native_sha256=p.digest(final_native))
            S.require(not self.transport.unknown and state.get("postcheck") == POST_PASS and passes(outcome),
                      "LEASE_RENEW_CHILD_RECEIPT_UNCONFIRMED")
            state["status"] = child.PASS
            p.event(child.STAGE, child.PASS)

        def postchecks(self):
            prepared, modules, raw, assets = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation and assets == self.renewal_assets
                      and exact_reviews(self.directory, self.operation, self.raw, modules) == self.reviews,
                      "CLOUD_OWNING_SOURCE_REVIEW_DRIFT")
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True
                if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                    self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                state = self.report["lease_renew"]
                S.require(state["status"] == child.PASS and state["postcheck"] == POST_PASS, "LEASE_RENEW_CHILD_RECEIPT_UNCONFIRMED")

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
    run = actions.add_parser("execute")
    run.add_argument(EXECUTE, action="store_true", dest="approved")
    run.add_argument("--packet", type=Path, required=True)
    opts = cli.parse_args(argv)
    try:
        if opts.action == "prepare":
            print(recipe.canonical(make_packet(opts.tool_archive, draft=opts.draft)).decode())
            return 0
        recipe.require(opts.action != "execute" or opts.approved, "LEASE_RENEW_EXPLICIT_EXECUTION_REQUIRED")
        prepared, modules, raw, assets = read_closed(opts.packet, draft=getattr(opts, "draft", False))
        basis, _, two = modules
        if opts.action == "verify":
            print(recipe.canonical({"state": "HELD_VERIFIED", "sha256": basis.S.sha(raw), "runtime": "NOT_RUN"}).decode())
            return 0
        directory, packet = prepared[:2]
        reviews = exact_reviews(directory, packet, raw, modules)
        os.umask(0o077)
        basis.P.write_new(directory / "attempt.json", basis.S.encode({
            "run_id": packet["run_id"], "packet_sha256": basis.S.sha(raw), "reviews": reviews,
        }))
        signal.signal(signal.SIGHUP, two.interrupt)
        signal.signal(signal.SIGTERM, two.interrupt)
        return owner_type(modules)(prepared, raw, reviews, assets).run()
    except BaseException as error:
        code = getattr(error, "code", None) or str(error)
        safe = code if type(code) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", code) else "LEASE_RENEW_OWNING_OPERATION_UNCONFIRMED"
        print(recipe.canonical({"status": "HELD_OR_STOPPED", "code": safe, "runtime_pass_claimed": False}).decode())
        return 1


if __name__ == "__main__":
    sys.exit(main())
