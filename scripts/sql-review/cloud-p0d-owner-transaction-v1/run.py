"""Prepare or run the reviewed disposable P0-D owner-transaction smoke test."""

import argparse
import hashlib
import json
from pathlib import Path
import os
import re
import signal
import sys
import uuid

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent.relative_to(ROOT).as_posix()
RENEW = "scripts/sql-review/cloud-lease-renew-source8-v1"
RENEW_PINS = {
    "operation.py": "1e9e5f3fac3a2d868e24cbaaaaeab622acac3d94b350bffb1d4b9d9907548532",
    "child.py": "1255285e9a462ac30b5e3ba766b04f38e5fa41bf8c425c6306fbf11fc6d4a394",
    "prepare.py": "dfcbc5fab2feb941806d4d23f6275978702b6698802aba8645b8015b0470fd54",
}
ENTRY = "context/reconciliation/cloud-phase0-evidence/2026-11-27/p0d-bounded-entry/acceptance.json"
ENTRY_SHA = "968f10aebc657eaf6653303d5ea6d56b9aaaf6a1746012a52768927e30d49987"
APP_SQL = "review-output/app-write-two-guard-observation-v2"
IDENTITY_SEED = f"{APP_SQL}/independent-user-fixtures.sql"
IDENTITY_SEED_SHA = "ce281631c3dcee36c6e1b8e24182cf8041bb86aae5b2caf8f8902d278bf0663a"
OWNER_SOURCE = "server/platform/persistence/owner-transaction.ts"
TEST_MAIN = "owner-transaction-smoke.ts"
OBSERVE_SQL = f"{HERE}/observe-smoke.sql"
FIXTURE_INPUTS = f"{HERE}/fixture-sources.json"
FILES = {"owner-transaction.ts": OWNER_SOURCE, TEST_MAIN: f"{HERE}/{TEST_MAIN}.txt",
         "fixture.ts": f"{HERE}/fixture.ts.txt", "package.json": f"{HERE}/package.json"}
TEST_INPUTS = (IDENTITY_SEED, OBSERVE_SQL, FIXTURE_INPUTS, *FILES.values(), f"{HERE}/run.py", f"{HERE}/README.md",
               f"{HERE}/test_run.py")
SOURCE_SCHEMA = "workinants.cloud-p0d-owner-transaction-source-review.v1"
LITERAL_SCHEMA = "workinants.cloud-p0d-owner-transaction-literal-review.v1"
PACKET_SCHEMA = "workinants.cloud-p0d-owner-transaction-operation.v1"
EXECUTE = "--execute-reviewed-cloud-p0d-owner-transaction-v1"
STAGE = "P0D_OWNER_TRANSACTION"
POST = f"{STAGE}_AFTER"
PASS = "PASS_SCOPED_OWNER_TRANSACTION_SMOKE"
NODE_PASS = "PASS_KNOWN_OWNER_TRANSACTION_SMOKE_ONLY"
NODE_SCHEMA = "workinants.p0d-owner-node-smoke-result.v1"
NODE_STAGES = {"ENTRY", "DRIVER", "CUSTOMER_SOURCE_COMMIT", "WORK_SCHEDULE_COMMIT", "CUSTOMER_COMPLETE_SCOPE",
               "STALE_SECURITY_GENERATION", "SAME_POOL_CONTEXT_ABSENT", "MISSING_CUSTOMER_REVISION", "SAME_POOL_REBOUND",
               "LOCAL_PHYSICAL_ROLLBACK", "SWALLOWED_DRIVER_FAILURE", "POOL_CLOSE"}
XIDS = {"source", "schedule", "complete", "unbound", "missing_revision", "rebound", "local_rollback", "latched_rollback"}
XID = re.compile(r"[1-9][0-9]{0,19}")
REMOTE_SOURCE = "/run/wa-f0-application"
NODE = "/run/wa-f0-tools/node/bin/node"
DRIVER = "/run/wa-f0-tools/node_modules/postgres/src/index.js"
SOURCE_SCOPES = ["accepted_bounded_p0d_entry_and_exact_source8", "exact_parameter_bound_node_app_issuer_transactions",
                 "known_customer_work_fixture_and_rollback_only", "closed_process_and_native_full_ledger_parity"]
LITERAL_SCOPES = ["fresh_exact_daemon_image_and_resources", "committed_app_source_and_closed_node_driver_tools",
                  "genuine_migrations_and_current_restricted_authority", "finite_stdin_only_owner_smoke",
                  "full_client_closure_and_exact_owned_cleanup"]
CODES = {
    "P0D_ENTRY_UNPROVEN", "P0D_INPUTS_CHANGED", "P0D_NODE_COPY_UNCONFIRMED", "P0D_CHILD_RESULT_UNCONFIRMED",
    "P0D_SCOPE_OBSERVATION_UNCONFIRMED", "P0D_NATIVE_LEDGER_PARITY_UNCONFIRMED",
}
COPY = ('umask 022; set -C; /bin/cat > "$1"; /bin/chmod 0444 "$1"; '
        'test "$(/usr/bin/stat -c \'%u:%g:%a:%h\' -- "$1")" = 0:0:444:1')


def mechanism():
    directory = ROOT / RENEW
    for file, digest in RENEW_PINS.items():
        path = directory / file
        if path.resolve(strict=True) != path or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("P0D_INPUTS_CHANGED")
    sys.path.insert(0, str(directory))
    try:
        import operation as renewal
        if any(Path(sys.modules[name].__file__).resolve() != directory / leaf
               for name, leaf in (("operation", "operation.py"), ("child", "child.py"), ("prepare", "prepare.py"))):
            raise ValueError("P0D_INPUTS_CHANGED")
        return renewal, renewal.mechanism()
    finally:
        sys.path.pop(0)


def compose(tool_archive, run_id, *, draft):
    renewal, (basis, plan, two) = mechanism()
    S, P = basis.S, basis.P
    S.require(str(uuid.UUID(run_id)) == run_id and uuid.UUID(run_id).version == 4, "P0D_INPUTS_CHANGED")
    _two_directory, packet, blobs, inner, manifest, nested, files, archive = plan.compose(tool_archive, run_id, draft=True)
    S.require(renewal.exact_seam(blobs[S.STEPS]), "P0D_INPUTS_CHANGED")
    blobs[ENTRY] = S.pinned(ROOT, ENTRY, ENTRY_SHA)
    entry = S.unique_json(blobs[ENTRY])
    S.require(entry["decision"] == "ACCEPT_EXACT_SOURCE8_DATABASE_ENTRY_FOR_BOUNDED_P0D_IMPLEMENTATION"
              and entry["posture"] == "D" and entry["p0d_runtime_qualified"] is False, "P0D_ENTRY_UNPROVEN")
    for path in (*TEST_INPUTS, *(f"{RENEW}/{leaf}" for leaf in RENEW_PINS)):
        content = S.read(ROOT / path)
        S.require(path not in blobs or blobs[path] == content, "P0D_INPUTS_CHANGED")
        blobs[path] = content
    S.require(S.sha(blobs[IDENTITY_SEED]) == IDENTITY_SEED_SHA, "P0D_INPUTS_CHANGED")
    fixture = S.unique_json(blobs[FIXTURE_INPUTS])
    S.require(fixture["status"] == "PREPARED_NOT_RUN" and fixture["source_files"]["identity_setup"]["path"] == IDENTITY_SEED,
              "P0D_INPUTS_CHANGED")
    for item in fixture["source_files"].values():
        path = item["path"]
        raw = S.pinned(ROOT, path, item["sha256"])
        S.require(path.startswith(APP_SQL + "/") and len(raw) == item["bytes"] and (path not in blobs or raw == blobs[path]),
                  "P0D_INPUTS_CHANGED")
        blobs[path] = raw
    driver_pins = {name: sha for name, sha in manifest["tools"]["files_sha256"].items()
                   if name.startswith("node_modules/postgres/")}
    S.require(len(driver_pins) == 37 and DRIVER.removeprefix("/run/wa-f0-tools/") in driver_pins,
              "P0D_INPUTS_CHANGED")
    directory = P.SCRATCH / f"wa-cloud-p0d-owner-transaction-{run_id}"
    pins = {name: S.sha(raw) for name, raw in blobs.items()}
    packet.update(schema=PACKET_SCHEMA, source=None if draft else S.verify_committed(ROOT, blobs),
                  status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_OWNER_TRANSACTION_REVIEWS",
                  source_pins=pins, source_aggregate_sha256=S.aggregate(pins),
                  nested_manifest=P.bind(directory / "run-manifest.json", nested),
                  archive=P.bind(directory / "source8.tar", archive),
                  owner_transaction={"status": "NOT_RUN", "entry_sha256": ENTRY_SHA,
                                     "driver_files": len(driver_pins), "driver_sha256": S.aggregate(driver_pins),
                                     "source_files": {leaf: pins[repo] for leaf, repo in FILES.items()},
                                     "roles": ["wa_app_runtime", "wa_context_issuer"]})
    return (directory, packet, blobs, inner, manifest, nested, files, archive), renewal, (basis, plan, two)


def make_packet(archive, *, draft):
    prepared, _, (basis, _, _) = compose(archive, str(uuid.uuid4()), draft=draft)
    directory, packet, _, _, _, nested, files, source_archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    P.write_new(directory / "run-manifest.json", nested)
    P.write_new(directory / "source8.tar", source_archive)
    P.write_source(directory / "source8", files)
    raw = S.encode(packet)
    path = directory / "operation.json"
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    _, (basis, _, _) = mechanism()
    P, S = basis.P, basis.S
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    packet = S.unique_json(raw)
    prepared, renewal, modules = compose(Path(packet["tools"]["path"]), packet["run_id"], draft=draft)
    directory, rebuilt, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(rebuilt), "P0D_INPUTS_CHANGED")
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, renewal, modules, raw


def review_bindings(packet, raw, plan):
    details = packet["owner_transaction"]
    return {**plan.review_bindings(packet, raw), "entry_sha256": ENTRY_SHA,
            "owner_and_test_source_sha256": details["source_files"], "driver_sha256": details["driver_sha256"]}


def exact_reviews(directory, packet, raw, modules):
    basis, plan, _ = modules
    bindings = review_bindings(packet, raw, plan)
    source, source_hash = basis.P.read_review(directory / "source-review.json", schema=SOURCE_SCHEMA,
                                              bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = basis.P.read_review(directory / "literal-review.json", schema=LITERAL_SCHEMA,
                                                bindings={**bindings, "source_review_sha256": source_hash},
                                                scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"] == "/root", "P0D_INPUTS_CHANGED")
    return {"source": source_hash, "literal": literal_hash,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def node_receipt(reply, S, known_secrets):
    S.require(type(reply.returncode) is int and reply.returncode in (0, 1) and reply.stderr == b""
              and type(reply.stdout) is bytes and 0 < len(reply.stdout) <= 8192
              and not any(secret.encode() in reply.stdout for secret in known_secrets), "P0D_CHILD_RESULT_UNCONFIRMED")
    value = S.unique_json(reply.stdout)
    S.require(type(value) is dict and value.get("schema") == NODE_SCHEMA, "P0D_CHILD_RESULT_UNCONFIRMED")
    if reply.returncode == 1:
        S.require(set(value) == {"schema", "status", "stage"} and value["status"] == "STOPPED"
                  and value["stage"] in NODE_STAGES, "P0D_CHILD_RESULT_UNCONFIRMED")
        return value
    expected = {
        "schema": NODE_SCHEMA, "status": NODE_PASS, "pools_ended": True,
        "customer_visibility": {"complete": 1, "unbound": 0, "missing_revision": 0, "rebound": 1},
        "stale_generation": {"failure": "context_denied", "callback_count": 0},
        "local_rollback": {"failure": "rolled_back", "changed": 1, "actual_mutation_xid_verified": True},
        "latched_failure": {"query_failure": "rolled_back", "transaction_failure": "rolled_back", "changed": 1,
                            "callback_completed": True, "commit_dispatched": False, "subsequent_query_dispatches": 0},
    }
    variable = {"transaction_xids", "runtime_backend", "scheduled_work_full_row_sha256"}
    S.require(set(value) == set(expected) | variable and S.encode({key: value[key] for key in expected}) == S.encode(expected),
              "P0D_CHILD_RESULT_UNCONFIRMED")
    backend, xids, work_digest = value["runtime_backend"], value["transaction_xids"], value["scheduled_work_full_row_sha256"]
    S.require(type(backend) is dict and set(backend) == {"pid", "backend_start_epoch"}
              and type(backend["pid"]) is int and backend["pid"] > 0
              and type(backend["backend_start_epoch"]) is str and re.fullmatch(r"[1-9][0-9]{0,11}\.[0-9]{6}", backend["backend_start_epoch"])
              and type(xids) is dict and set(xids) == XIDS and all(type(xid) is str and XID.fullmatch(xid) for xid in xids.values())
              and len(set(xids.values())) == len(XIDS) and type(work_digest) is str and S.HASH.fullmatch(work_digest),
              "P0D_CHILD_RESULT_UNCONFIRMED")
    return value


def validate_observation(observed, result, S):
    xids = result["transaction_xids"]
    shapes = observed.get("grant_shapes") if type(observed) is dict else None
    stale = shapes.get("stale") if type(shapes) is dict else None
    S.require(type(stale) is list and len(stale) == 1 and type(stale[0]) is str and XID.fullmatch(stale[0])
              and stale[0] not in xids.values(), "P0D_SCOPE_OBSERVATION_UNCONFIRMED")
    expected = {"source_count": 7, "source_distinct_xids": 1, "source_xid": xids["source"], "work_count": 1,
                "work": {"full_row_sha256": result["scheduled_work_full_row_sha256"], "scheduled_xid": xids["schedule"],
                         "known_pending_original": True},
                "restricted_sessions": 0, "grant_total": 8, "grant_count": 8, "runtime_pid": result["runtime_backend"]["pid"],
                "runtime_pids": 1, "separate_issuer_transactions": 8, "grant_ids_distinct": True, "grant_hashes_distinct": True,
                "grant_runtime_xids_distinct": 8, "issuer_and_runtime_xids_disjoint": True, "grant_metadata_exact": True,
                "grant_shapes": {"source": [xids["source"]], "schedule": [xids["schedule"]], "stale": stale,
                                 "complete": sorted((xids["complete"], xids["rebound"])), "missing_revision": [xids["missing_revision"]],
                                 "work_update": sorted((xids["local_rollback"], xids["latched_rollback"]))}}
    S.require(S.encode(observed) == S.encode(expected), "P0D_SCOPE_OBSERVATION_UNCONFIRMED")


def owner_type(renewal, modules):
    basis, _, two = modules
    S = basis.S

    class Owner(two.Owner):
        def configure_program(self):
            super().configure_program()
            self.report.update(schema="workinants.cloud-p0d-owner-transaction-run-evidence.v1",
                               owner_transaction={"status": "NOT_RUN", "integrated_runtime_qualified": False})
            p = self.program
            p.SAFE_FAILURE_STAGES |= {STAGE, f"{STAGE}_CHILD_CLOSED", f"NATIVE_{POST}", f"LEDGER_{POST}",
                                      "LEDGER_FINGERPRINT_owner-transaction-after"}
            p.SAFE_FAILURE_CODES |= CODES
            emit = p.event

            def event(stage, status, **values):
                emit(stage, status, **values)
                if (stage, status) == renewal.SEAM:
                    self.report["stage"] = STAGE
                    self.report["owner_transaction"]["status"] = "IN_PROGRESS"
                    p.save()
                    try:
                        self.run_child()
                    except BaseException:
                        self.report["owner_transaction"]["status"] = "STOPPED"
                        raise

            p.event = event

        def closed_sql(self, source):
            p = self.program
            result = self.command(self.psql_args(self.name, "postgres"), self.blobs[source].decode())
            p.need(type(result.returncode) is int and result.returncode == 0 and result.stderr == "",
                   "P0D_SCOPE_OBSERVATION_UNCONFIRMED")
            return result.stdout

        def closed_record(self, source):
            return S.unique_json(self.closed_sql(source).encode("utf-8"))

        def copy_sources(self):
            cid = self.resources.cid
            self.exact_container_exec("--user", "0", cid, "/usr/bin/mkdir", "-m", "0755", "--", REMOTE_SOURCE)
            for leaf, repo in FILES.items():
                path = f"{REMOTE_SOURCE}/{leaf}"
                raw = self.blobs[repo]
                written = self.exact_container_exec("-i", "--user", "0", cid, "/bin/sh", "-ceu", COPY,
                                                    "wa-copy-owner-source", path, input=raw)
                observed = self.exact_container_exec(cid, "/usr/bin/sha256sum", "--", path)
                S.require(written.stdout == b"" and observed.stdout == f"{S.sha(raw)}  {path}\n".encode(),
                          "P0D_NODE_COPY_UNCONFIRMED")

        def artifact(self, leaf):
            p = self.program
            return S.unique_json(p.closed_bytes(p.OUT / leaf, origin=p.STATE["origins"][leaf])[0])

        def run_child(self):
            p = self.program
            state = self.report["owner_transaction"]
            migrations = self.report["migration_results"]
            S.require(renewal.native_gate(self.report["native_results"]) and migrations[-1]["no_pending_message_observed"] is True
                      and not self.transport.unknown and self.report["targets"][self.name]["finalization"] == "PASS"
                      and p.STATE.get("activated") is True, "P0D_ENTRY_UNPROVEN")
            observed = self.observed_target()
            cid = self.resources.cid
            S.require(observed["container_id"] == cid and observed["network"] == "none"
                      and observed["published_ports"] is False, "P0D_ENTRY_UNPROVEN")
            native = self.artifact("noop-native-before.json")
            baseline_ledger = self.artifact("noop-ledger-observation.json")
            baseline_fingerprints = self.artifact("initial-after-noop-fingerprints.json")
            self.copy_sources()
            with p._RequiredSafetyBoundary("CLOSE", self.name, f"{STAGE}_CHILD_CLOSED"):
                S.require(self.closed_sql(IDENTITY_SEED) == "", "P0D_SCOPE_OBSERVATION_UNCONFIRMED")
                observed = p.collect_native(self.name, f"NATIVE_{POST}", "owner-transaction-native-after-seed.json")
                S.require(observed == native, "P0D_NATIVE_LEDGER_PARITY_UNCONFIRMED")
                passwords = p.passwords[self.name]
                credentials = json.dumps({"app": passwords["wa_app_runtime"], "issuer": passwords["wa_context_issuer"]},
                                         separators=(",", ":")).encode()
                try:
                    reply = self.exact_container_exec(
                        "-i", "--user", "65534:65534", cid, "/usr/bin/env", "-i", NODE,
                        f"{REMOTE_SOURCE}/{TEST_MAIN}", DRIVER,
                        input=credentials, timeout=90, allow_fail=True,
                    )
                    result = node_receipt(reply, S, p.all_secrets)
                except BaseException:
                    self.transport.unknown = self.docker.remote_unknown = True
                    raise
                state["node"] = p.write_safe("owner-transaction-node.json", result)
                S.require(result["status"] == NODE_PASS, "P0D_CHILD_RESULT_UNCONFIRMED")
            observation = self.closed_record(OBSERVE_SQL)
            validate_observation(observation, result, S)
            state["observation"] = p.write_safe("owner-transaction-observation.json", observation)
            fixture = S.unique_json(self.blobs[FIXTURE_INPUTS])
            proof = {}
            for name in ("identity_coherence_observer", "customer_observer", "effect_observer"):
                proof[name] = self.closed_record(fixture["source_files"][name]["path"])
                S.require(S.encode(proof[name]) == S.encode(fixture[f"{name}_expected"]), "P0D_SCOPE_OBSERVATION_UNCONFIRMED")
            state["fixture"] = p.write_safe("owner-transaction-fixture.json", proof)
            post = p.collect_native(self.name, f"NATIVE_{POST}", "owner-transaction-native-after.json")
            registration, ledger = p.ledger_observation(migrations[0], POST)
            final = p.collect_native(self.name, f"NATIVE_{POST}", "owner-transaction-native-after-ledger.json")
            comparisons, ledger_proof = p.compare_ledger(registration, ledger, final)
            after = p.fingerprints("owner-transaction-after")
            S.require(post == final == native and ledger == baseline_ledger and len(comparisons["checks"]) == 22,
                      "P0D_NATIVE_LEDGER_PARITY_UNCONFIRMED")
            state.update(status=PASS, container_id=cid, volume_created_at=self.resources.volume_birth,
                         post_ledger=p.write_safe("owner-transaction-ledger.json", ledger_proof),
                         full8=p.CATALOG["two"].compare_noop(baseline_fingerprints, after), native_sha256=p.digest(final))
            p.event(STAGE, PASS)

        def postchecks(self):
            prepared, _, runtime, raw = read_closed(self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation
                      and exact_reviews(self.directory, self.operation, raw, runtime) == self.reviews,
                      "P0D_INPUTS_CHANGED")
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                S.require(self.report["owner_transaction"]["status"] == PASS and not self.transport.unknown,
                          "P0D_CHILD_RESULT_UNCONFIRMED")
            self.report["immutable_source_postcheck"] = "PASS"

    return Owner


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="action", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--tool-archive", type=Path, required=True)
    prepare.add_argument("--draft", action="store_true")
    verify = commands.add_parser("verify")
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--draft", action="store_true")
    execute = commands.add_parser("execute")
    execute.add_argument("--packet", type=Path, required=True)
    execute.add_argument(EXECUTE, action="store_true", dest="approved")
    options = cli.parse_args(argv)
    try:
        if options.action == "prepare":
            print(json.dumps(make_packet(options.tool_archive, draft=options.draft)))
            return 0
        if options.action == "execute" and not options.approved:
            raise ValueError("P0D_EXPLICIT_EXECUTION_REQUIRED")
        prepared, renewal, modules, raw = read_closed(options.packet, draft=getattr(options, "draft", False))
        directory, packet = prepared[:2]
        basis, _, two = modules
        owner = owner_type(renewal, modules)
        basis.S.require(callable(two.interrupt), "P0D_INPUTS_CHANGED")
        if options.action == "verify":
            print(basis.S.encode({"sha256": basis.S.sha(raw), "runtime": "NOT_RUN", "state": "HELD_VERIFIED"}).decode(), end="")
            return 0
        reviews = exact_reviews(directory, packet, raw, modules)
        os.umask(0o077)
        basis.P.write_new(directory / "attempt.json", basis.S.encode({"run_id": packet["run_id"],
                          "packet_sha256": basis.S.sha(raw), "reviews": reviews}))
        signal.signal(signal.SIGTERM, two.interrupt)
        signal.signal(signal.SIGHUP, two.interrupt)
        return owner(prepared, raw, reviews).run()
    except BaseException as error:
        code = getattr(error, "code", str(error))
        print(code if type(code) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", code) else "P0D_OWNER_TRANSACTION_HELD")
        return 1


if __name__ == "__main__":
    sys.exit(main())
