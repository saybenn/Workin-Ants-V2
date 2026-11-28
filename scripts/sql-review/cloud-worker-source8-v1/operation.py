"""Prepare or execute the separately reviewed disposable Cloud Worker Source 8 owner."""

import argparse
import ast
import json
import os
from pathlib import Path
import signal
import sys
from types import ModuleType
import uuid

import prepare
import worker_child as child


ROOT = prepare.ROOT
HERE = Path(__file__).resolve().parent.relative_to(ROOT).as_posix()
SHARED_OWNER = "scripts/sql-review/cloud-two-history-owned-v2"
SHARED_APP_COMMIT = "9fd12ffb882fd7704ab7b428c2073a6fead03296"
SHARED_APP = f"{prepare.RECON}/cloud-phase0-evidence/2026-11-27/app-2e59e073"
APP_PLAN = f"{SHARED_APP}/operation.json"
APP_REVIEW = f"{SHARED_APP}/source-review.json"
APP_PINS = {
    APP_PLAN: "7495da1a762f3e25e7fe6e1a6d35a729dc535ba34dffa62444131d9d1fdfc49a",
    APP_REVIEW: "0893d66b31dda2499baf6d740d737f1e578cb072b9dfa9ca3c392053b1685ca4",
}
MECHANISM = {
    f"{SHARED_OWNER}/basis.py": "e19319429a5b97fc594f91b882229f767964e4f9dd96891a9b9ebcaa9a4280af",
    f"{SHARED_OWNER}/plan.py": "c308295d97ab1d794cf3a7a8b2f241b1c7266b8cb606704ada6f2c3de9c1decb",
    prepare.TWO_OWNER: prepare.TWO_PINS[prepare.TWO_OWNER],
}
FILES = ("README.md", "prepare.py", "test_prepare.py", "worker_child.py", "operation.py", "test_operation.py")
SCHEMA = "workinants.cloud-f0-worker-source8-owned-operation.v1"
EXECUTE = "--execute-reviewed-cloud-f0-worker-source8-v1"
STAGE = "CLOUD_WORKER_SOURCE8"
POST = "worker-after"
OWNER_CODES = {"WORKER_FRESH_SOURCE8_NOT_PROVED", "WORKER_SAME_RUN_ATTESTATION", "WORKER_CHILD_STOPPED",
               "WORKER_CHILD_REFERENCE_UNCONFIRMED", "WORKER_CHILD_CLOSURE_UNCONFIRMED", "WORKER_FINAL_STATE_DRIFT",
               "WORKER_POST_NATIVE_LEDGER_DRIFT", "WORKER_IMMUTABLE_PACKET_DRIFT", "WORKER_CLOCK_LITERAL_SCOPE"}
SOURCE_SCOPES = ["prior_accepted_two_and_exact_worker_100_source_files", "worker21_controls_worker32_acl_five_fixture_guards",
                 "effective_diagnostics_and_exact_terminal_exit", "shared_pipe_source_worker_session_and_closure",
                 "independent_post_worker_native_oracle_ledger"]
LITERAL_SCOPES = ["actual_local_socket_daemon_and_fresh_owned_volume", "current_committed_packet_tools_and_private_credentials",
                  "same_live_noop_before_worker_and_original_grantor", "exact_worker_fixture_roles_and_finite_reclaim",
                  "value_free_evidence_and_exact_cleanup"]
SAFE_CHILD_STATES = frozenset((child.PASS, child.STOPPED))


def mechanism():
    source = prepare.common(ROOT)
    blobs = prepare.anchored(source, ROOT, prepare.TWO_COMMIT, MECHANISM)
    modules = []
    registered = []
    try:
        for relative in MECHANISM:
            name = Path(relative).stem if relative != prepare.TWO_OWNER else "_cloud_worker_reviewed_two_owner"
            source.require(name not in sys.modules, "WORKER_SHARED_MODULE_COLLISION")
            module = ModuleType(name)
            module.__file__ = str(ROOT / relative)
            sys.modules[name] = module
            registered.append(name)
            exec(compile(blobs[relative], module.__file__, "exec", dont_inherit=True), module.__dict__)
            modules.append(module)
    finally:
        for name in registered:
            del sys.modules[name]
    return tuple(modules)


def compose(tool_archive, run_id, *, draft=False):
    modules = mechanism()
    basis, plan, _ = modules
    S, P = basis.S, basis.P
    _, operation, blobs, inner, manifest, nested, files, archive = plan.compose(tool_archive, run_id, draft=True)
    proof, _ = prepare.build()
    shared_helpers = {name: child.PINS[name] for name in (child.PIPE, child.CONTEXT_RENDERER)}
    additional = {**proof["preparation_source_files_sha256"], **proof["published_worker_files_sha256"],
                  **child.PINS, **APP_PINS}
    prepare.anchored(S, ROOT, SHARED_APP_COMMIT, shared_helpers)
    for name, digest in additional.items():
        raw = S.pinned(ROOT, name, digest)
        S.require(name not in blobs or blobs[name] == raw, "WORKER_SOURCE_GRAPH_COLLISION")
        blobs[name] = raw
    app, app_review = (S.unique_json(blobs[name]) for name in (APP_PLAN, APP_REVIEW))
    bound = app_review["bindings"]
    S.require(app_review["schema"] == "workinants.cloud-f0-app-source8-source-review.v1"
              and app_review["decision"] == "APPROVE" and app_review["reviewer"] != app_review["source_author"]
              and "finite_role_sessions_issuer_retention_and_strict_closure" in app_review["scopes"]
              and bound["packet_sha256"] == APP_PINS[APP_PLAN]
              and bound["source_commit"] == app["source"]["commit"] == SHARED_APP_COMMIT
              and bound["source_tree"] == app["source"]["tree"]
              and bound["all_sources_sha256"] == app["source_aggregate_sha256"] == S.aggregate(app["source_pins"])
              and {name: app["source_pins"][name] for name in shared_helpers} == shared_helpers,
              "WORKER_SHARED_APP_TRANSPORT_REVIEW")
    for leaf in FILES:
        blobs[f"{HERE}/{leaf}"] = S.read(ROOT / HERE / leaf)
    prior = S.unique_json(blobs[prepare.AUDIT])
    target = operation["target"]
    S.require(run_id != prior["run_id"] and target["container_name"] != prior["target"]["container_name"]
              and target["volume_name"] != prior["target"]["volume_name"]
              and operation["daemon"] == prior["daemon"] and operation["image"] == prior["image"],
              "WORKER_FRESH_TARGET_SAME_CLOUD_PROFILE")
    source_pins = {name: S.sha(raw) for name, raw in blobs.items()}
    directory = P.SCRATCH / f"wa-cloud-f0-worker-source8-{run_id}"
    operation.update(schema=SCHEMA, status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_WORKER_REVIEW",
                     source=None if draft else S.verify_committed(ROOT, blobs), source_pins=source_pins,
                     source_aggregate_sha256=S.aggregate(source_pins), nested_manifest=P.bind(directory / "run-manifest.json", nested),
                     archive=P.bind(directory / "source8.tar", archive),
                     worker_source8={"held_proof": proof, "prior_closed_cid": prior["created_container_id"],
                                     "shared_pipe_source_commit": SHARED_APP_COMMIT,
                                     "shared_pipe_source_review_sha256": APP_PINS[APP_REVIEW],
                                     "fresh_live_noop_required": True, "runtime": "NOT_RUN"})
    return (directory, operation, blobs, inner, manifest, nested, files, archive), modules


def prepare_packet(tool_archive, *, draft=False):
    prepared, (basis, _, _) = compose(tool_archive, str(uuid.uuid4()), draft=draft)
    directory, operation, _, _, _, nested, files, archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.write_new(directory / "run-manifest.json", nested)
    P.write_new(directory / "source8.tar", archive)
    P.write_source(directory / "source8", files)
    raw = S.encode(operation)
    path = directory / "operation.json"
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "source_files": len(operation["source_pins"]), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    basis, _, _ = mechanism()
    S, P = basis.S, basis.P
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == SCHEMA and value["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_WORKER_REVIEW"), "WORKER_OPERATION_PACKET_REQUIRED")
    prepared, modules = compose(Path(value["tools"]["path"]), value["run_id"], draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), "WORKER_IMMUTABLE_PACKET_DRIFT")
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, modules, raw


def review_bindings(operation, raw, modules):
    basis, plan, _ = modules
    return {**plan.review_bindings(operation, raw), "accepted_two_sha256": prepare.ACCEPTED_PINS[prepare.ACCEPTANCE],
            "worker_held_proof_sha256": basis.S.sha(basis.S.encode(operation["worker_source8"]["held_proof"])),
            "shared_worker_pipe_source_sha256": child.PINS[child.PIPE],
            "shared_worker_pipe_source_review_sha256": APP_PINS[APP_REVIEW]}


def reviews_for(directory, operation, raw, modules):
    basis, _, _ = modules
    bindings = review_bindings(operation, raw, modules)
    source, source_sha = basis.P.read_review(directory / "source-review.json",
        schema="workinants.cloud-f0-worker-source8-source-review.v1", bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_sha = basis.P.read_review(directory / "literal-review.json",
        schema="workinants.cloud-f0-worker-source8-literal-review.v1",
        bindings={**bindings, "source_review_sha256": source_sha}, scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"], "WORKER_REVIEW_AUTHOR_DRIFT")
    return {"source": source_sha, "literal": literal_sha,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def native_gate(record):
    return (type(record) is dict and type(record.get("applied_rows")) is int and record["applied_rows"] == 2
            and type(record.get("catalog_check_counts")) is dict and set(record["catalog_check_counts"]) == {"PASS"}
            and type(record["catalog_check_counts"]["PASS"]) is int and record["catalog_check_counts"]["PASS"] == 29089
            and type(record.get("ledger_checks")) is int
            and record["ledger_checks"] == 22 and type(record.get("oracle_expressions")) is int
            and record["oracle_expressions"] == 416)


def install_clock_transport(owner, S):
    """Retain the exact bounded reader with a fractional deadline for one command."""
    p = owner.program
    raw = owner.blobs[S.OPERATOR]
    S.require(S.sha(raw) == S.HISTORICAL_PINS[S.OPERATOR], "WORKER_CLOCK_TRANSPORT_ORIGIN")
    klass = child.selected(raw, {"Transport"}, S.OPERATOR)[0]
    methods = [method for method in klass.body if isinstance(method, ast.FunctionDef) and method.name == "binary"]
    S.require(len(methods) == 1, "WORKER_CLOCK_TRANSPORT_ORIGIN")
    literal = ast.unparse(methods[0])
    remote = "remote_exec = args[:4] == ['docker', '--context', 'desktop-linux', 'exec']"
    integer = "type(timeout) is int and (0 < timeout <= 150)"
    S.require(literal.count(remote) == literal.count(integer) == 1, "WORKER_CLOCK_TRANSPORT_ORIGIN")
    literal = literal.replace(remote, "remote_exec = len(args) > 5 and args[1] == '--config' and "
                              "args[3:6] == ['--host', 'unix:///var/run/docker.sock', 'exec']")
    literal = literal.replace(integer, "type(timeout) is float and (0 < timeout <= 5)")
    entry = compile(literal, S.OPERATOR, "exec", dont_inherit=True)
    namespace = dict(p.__dict__)
    exec(entry, namespace)
    fractional = namespace["binary"]
    original = owner.transport.binary

    def binary(args, payload=None, timeout=30, profile="control", batch=None):
        if type(timeout) is int:
            return original(args, payload, timeout, profile, batch)
        psql = owner.psql_args(owner.name, "postgres")
        S.require(psql.count("SHOW_CONTEXT=never") == 1, "WORKER_CLOCK_LITERAL_SCOPE")
        psql[psql.index("SHOW_CONTEXT=never")] = "SHOW_CONTEXT=errors"
        S.require(type(timeout) is float and 0 < timeout <= 5 and profile == "control" and batch is None
                  and args == owner.docker.argv(*psql) and payload == owner.blobs[f"{prepare.PACKET}/A-clock.sql"],
                  "WORKER_CLOCK_LITERAL_SCOPE")
        return fractional(owner.transport, args, payload, timeout, profile, batch)

    owner.transport.binary = binary


def require_fresh(owner, S):
    p = owner.program
    phase = p.STATE
    cid, birth, run_id = owner.resources.cid, owner.resources.volume_birth, owner.operation["run_id"]
    proof = owner.operation["worker_source8"]
    prior = proof["held_proof"]["prior_closed_machinery"]
    receipts = owner.report.get("migration_results", [])
    native = owner.report.get("native_results", {})
    S.require(owner.report["worker_source8"]["status"] == "NOT_RUN" and owner.transport.unknown is False
              and type(cid) is str and S.HASH.fullmatch(cid) and cid != proof["prior_closed_cid"]
              and type(birth) is str and 0 < len(birth) <= 256 and run_id != prior["run_id"]
              and all(phase.get(key) is True for key in ("first_deploy_closed_success", "finalization_verified",
                                                       "two_applied_verified", "activated"))
              and owner.report["targets"][owner.name]["finalization"] == "PASS"
              and owner.report["targets"][owner.name]["volume_created_at"] == birth
              and [row["operation"] for row in receipts] == ["deploy", "status", "deploy"]
              and receipts[-1]["no_pending_message_observed"] is True
              and all(type(row["exit_code"]) is int and row["exit_code"] == 0 and row["container_id"] == cid
                      and row["run_id"] == run_id and row["packet_sha256"] == S.sha(owner.raw) for row in receipts)
              and set(native) == {"initial", "noop"} and all(native_gate(row) for row in native.values())
              and native["initial"]["native_sha256"] == native["noop"]["native_sha256"], "WORKER_FRESH_SOURCE8_NOT_PROVED")
    return receipts[0], native["noop"]["native_sha256"]


def state_observation(owner, fixture, summary):
    p = owner.program
    sql = owner.blobs[f"{prepare.PACKET}/complete-state-observe.sql"].decode()
    result = p.run_catalog_query(owner.name, sql, "WORKER_FINAL_STATE")
    p.successful_query(result)
    rows = p.records(result.stdout)
    wanted = {**fixture["final_expected_counts"], "platform.database_action_grant": summary["grants_retained"]}
    child.require(type(rows) is list and len(rows) == 1 and type(rows[0]) is dict and len(rows[0]) == 42
                  and set(rows[0]) == set(wanted), "WORKER_FINAL_STATE_DRIFT")
    for table, row in rows[0].items():
        child.require(type(row) is dict and set(row) == {"count", "rows_sha256"} and type(row["count"]) is int
                      and row["count"] == wanted[table] and type(row["rows_sha256"]) is str
                      and all(char in "0123456789abcdef" for char in row["rows_sha256"]) and len(row["rows_sha256"]) == 64,
                      "WORKER_FINAL_STATE_DRIFT")
    child.require(p.digest(rows[0]) == summary["complete_state_sha256"], "WORKER_FINAL_STATE_DRIFT")
    return rows[0]


def qualify_after(owner, installed, fixture, summary, native, before_ledger, before_fingerprints):
    p = owner.program
    before_state = state_observation(owner, fixture, summary)
    after_native, after_ledger = p.qualify(installed, POST)
    checks = owner.report["native_results"].pop(POST)
    fingerprints = p.fingerprints(POST)
    full8 = p.CATALOG["two"].compare_noop(before_fingerprints, fingerprints)
    after_state = state_observation(owner, fixture, summary)
    child.require(native_gate(checks) and after_native == native and after_ledger == before_ledger
                  and after_state == before_state, "WORKER_POST_NATIVE_LEDGER_DRIFT")
    return checks, full8


def owner_type(modules):
    basis, _, two = modules
    S, P = basis.S, basis.P

    class Owner(two.Owner):
        def read_source(self, relative):
            return S.read(ROOT / relative)

        def configure_program(self):
            super().configure_program()
            install_clock_transport(self, S)
            self.report["schema"] = "workinants.cloud-worker-source8-owned-run-evidence.v1"
            self.report["worker_source8"] = {"status": "NOT_RUN", "assertion_promotions": 0}
            p = self.program
            p.SAFE_FAILURE_STAGES |= {STAGE, "WORKER_FINAL_STATE", "WORKER_PRE_CHILD", "WORKER_POST_CHILD",
                                      "NATIVE_" + POST, "ORACLE_" + POST, "NATIVE_AFTER_ORACLE_" + POST,
                                      "LEDGER_" + POST, "NATIVE_AFTER_LEDGER_" + POST, "LEDGER_FINGERPRINT_" + POST}
            p.SAFE_FAILURE_CODES |= OWNER_CODES
            emit = p.event

            def event(stage, status, **safe):
                emit(stage, status, **safe)
                if (stage, status) == ("NOOP", "PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER"):
                    self.report["stage"] = STAGE
                    try:
                        self.run_worker()
                    except BaseException:
                        self.report["worker_source8"]["status"] = "STOPPED_OR_UNCONFIRMED"
                        p.best_effort_save()
                        raise

            p.event = event

        def previous_artifact(self, name):
            p = self.program
            raw, _ = p.closed_bytes(p.OUT / name, origin=p.STATE["origins"][name])
            return S.unique_json(raw), S.sha(raw)

        def run_worker(self):
            p = self.program
            installed, native_hash = require_fresh(self, S)
            native, native_file = self.previous_artifact("noop-native-before.json")
            comparison, comparison_file = self.previous_artifact("noop-catalog-comparison.json")
            before_ledger, _ = self.previous_artifact("noop-ledger-observation.json")
            before_fingerprints, _ = self.previous_artifact("initial-after-noop-fingerprints.json")
            p.closed_backends(self.name, "WORKER_PRE_CHILD")
            self.report["stage"] = STAGE
            observed = self.observed_target()
            S.require(p.digest(native) == comparison["native_snapshot_sha256"] == native_hash
                      and comparison["source_expected_sha256"] == prepare.CATALOG and comparison["findings"] == []
                      and comparison["status"] == "PASS" and comparison["check_counts"] == {"PASS": 29089}
                      and observed["container_id"] == self.resources.cid and observed["volume_created_at"] == self.resources.volume_birth,
                      "WORKER_SAME_RUN_ATTESTATION")
            identity = {"run_id": self.operation["run_id"], "container_id": self.resources.cid, "volume_created_at": self.resources.volume_birth,
                        "source_commit": self.operation["source"]["commit"], "source_tree": self.operation["source"]["tree"],
                        "packet_sha256": S.sha(self.raw)}
            p.ARTIFACT_PREFIX = ""
            p.write_safe("worker-native-attestation.json", {**identity, "schema": "workinants.cloud-worker-native-attestation.v1",
                        "source_expected_sha256": prepare.CATALOG, "native_file_sha256": native_file,
                        "candidate_comparison_sha256": comparison_file, "native_catalog_sha256": native_hash,
                        "original_grantor_finalized": True, "operation_backends_absent": True, "fresh_full8_noop": True})
            state = self.report["worker_source8"]
            state.update(status="IN_PROGRESS", **identity)
            p.save()
            location = p.OUT / "worker-source8"
            failure = value = None
            origin_stage = STAGE

            def retain_failure(error, default, stage=STAGE):
                nonlocal failure, origin_stage
                code = getattr(error, "code", None)
                if type(code) is not str or code not in OWNER_CODES:
                    args = getattr(error, "args", ())
                    code = (args[0] if type(args) is tuple and len(args) == 1 and type(args[0]) is str
                            and args[0] in OWNER_CODES else default)
                if failure is None:
                    failure, origin_stage = p.Stop(code), stage
                    p._latch_first_failure(stage, code)
                else:
                    p.record_failure(stage, code)

            try:
                value = child.coordinate(self, native, location, S)
                S.require(value["status"] == child.PASS and self.transport.unknown is False, "WORKER_CHILD_STOPPED")
            except BaseException as error:
                retain_failure(error, "WORKER_CHILD_STOPPED")
            try:
                file = P.private_path(location / "worker-recovery-results.json", file=True)
                raw, origin = p.closed_bytes(file)
                retained = S.unique_json(raw)
                S.require((value is None or value == retained) and retained["schema"] == child.RESULT_SCHEMA
                          and retained["status"] in SAFE_CHILD_STATES
                          and all(retained.get(key) == expected for key, expected in identity.items()),
                          "WORKER_CHILD_REFERENCE_UNCONFIRMED")
                relative = file.relative_to(p.OUT).as_posix()
                p.STATE["origins"][relative] = origin
                state["child"] = {"artifact": relative, "sha256": S.sha(raw), "status": retained["status"],
                                  "cases_observed": len(retained["results"])}
            except BaseException as error:
                state["child_reference"] = "UNCONFIRMED"
                retain_failure(error, "WORKER_CHILD_REFERENCE_UNCONFIRMED")
            finally:
                try:
                    p.closed_backends(self.name, "WORKER_POST_CHILD")
                    state["global_client_closure"] = True
                except BaseException as error:
                    state["global_client_closure"] = False
                    retain_failure(error, "WORKER_CHILD_CLOSURE_UNCONFIRMED", "WORKER_POST_CHILD")
                p.best_effort_save()
            if failure is not None:
                self.report["stage"] = origin_stage
                raise failure from None
            self.report["stage"] = STAGE
            summary = child.verify_complete(self, value, native_hash, S)
            fixture = S.unique_json(self.blobs[prepare.FIXTURE])
            checks, full8 = qualify_after(self, installed, fixture, summary, native, before_ledger, before_fingerprints)
            p.ARTIFACT_PREFIX = ""
            p.write_safe("worker-source8-result.json", {**identity, **summary, "schema": "workinants.cloud-worker-source8-summary.v1",
                        "post_native_oracle_ledger": checks, "full8": full8, "full42_state_unchanged_by_postproof": True,
                        "assertion_promotions": 0})
            state.update(status=child.PASS, post_native_oracle_ledger=checks, full8=full8, complete42_unchanged=True)
            p.event(STAGE, child.PASS)

        def postchecks(self):
            prepared, actual, raw = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation
                      and reviews_for(self.directory, self.operation, self.raw, actual) == self.reviews,
                      "WORKER_IMMUTABLE_PACKET_DRIFT")
            self.report["immutable_source_postcheck"] = "PASS"
            apparent_pass = self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True
                if apparent_pass:
                    self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")
            elif apparent_pass and self.report["worker_source8"]["status"] != child.PASS:
                self.program.record_failure("POSTCHECKS", "WORKER_CHILD_STOPPED")

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
    args = cli.parse_args(argv)
    try:
        if args.action == "prepare":
            print(json.dumps(prepare_packet(args.tool_archive, draft=args.draft), sort_keys=True))
            return 0
        child.require(args.action != "execute" or args.approved, "WORKER_EXPLICIT_EXECUTION_REQUIRED")
        prepared, modules, raw = read_closed(args.packet, draft=getattr(args, "draft", False))
        basis, _, two = modules
        if args.action == "verify":
            print(basis.S.encode({"status": "HELD_VERIFIED", "sha256": basis.S.sha(raw), "runtime": "NOT_RUN"}).decode(), end="")
            return 0
        directory, operation = prepared[:2]
        approvals = reviews_for(directory, operation, raw, modules)
        os.umask(0o077)
        basis.P.write_new(directory / "attempt.json", basis.S.encode({"run_id": operation["run_id"],
                            "packet_sha256": basis.S.sha(raw), "reviews": approvals}))
        signal.signal(signal.SIGTERM, two.interrupt)
        signal.signal(signal.SIGHUP, two.interrupt)
        return owner_type(modules)(prepared, raw, approvals).run()
    except BaseException as error:
        code = getattr(error, "code", None)
        allowed = OWNER_CODES | {"WORKER_EXPLICIT_EXECUTION_REQUIRED"}
        tag = code if type(code) is str and code in allowed else "WORKER_OWNING_PACKET_HELD"
        print('{"status":"HELD_OR_STOPPED","code":"' + tag + '","runtime_pass_claimed":false}')
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
