"""Prepare or run the exact bounded Cloud P0-D known-Customer main proof."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import sys
from types import ModuleType
import uuid

import prior
import proof

SCRIPT = Path(__file__).resolve().parent
HERE = "scripts/sql-review/cloud-p0d-known-customer-v1"
SMOKE = "scripts/sql-review/cloud-p0d-owner-transaction-v1/run.py"
SMOKE_SHA = "da73ebb0eff61387da7548a9f4b48f9d22cc22c449652f83ac9d9805fbb22cef"
PROOF = f"{HERE}/proof"
PROOF_SHA = "61ced5e133c70822e2676d4d990977a9bb057cf6dead14a0f2e03374ea6264e4"
EMIT_SHA = "99fd4f115e3b8c98fe3150142b11a3c7c5c4de0f5f40f8479e81cf754c14252b"
SCHEMA = "workinants.cloud-p0d-known-customer-operation.v1"
SOURCE_SCHEMA = "workinants.cloud-p0d-known-customer-source-review.v1"
LITERAL_SCHEMA = "workinants.cloud-p0d-known-customer-literal-review.v1"
AUTHOR = "/root/foundation_gates"
EXECUTE = "--execute-reviewed-cloud-p0d-known-customer-v1"
PASS = "PASS_FINITE_KNOWN_CUSTOMER_MAIN_ONLY"
POST = "P0D_CUSTOMER_AFTER"
REMOTE = "/run/wa-f0-known-customer"
NODE_MAIN = "customer-proof.cjs"
COMPILED = {"features/customer_buyer_profile/application/resolve-customer-actor.js",
            "features/customer_buyer_profile/infrastructure/customer-repository.js",
            "server/platform/persistence/owner-transaction.js", "server/platform/runtime/command-receipts.js",
            "server/platform/runtime/outbox.js", "package.json"}
SOURCE_FILES = {"run.py", "proof.py", "prior.py", "test_run.py", "README.md"}
STAGES = {phase: "P0D_CUSTOMER_" + phase.replace("-", "_").upper() for phase in proof.PHASES}
SOURCE_SCOPES = ["prior_independent_owner_acceptance_and_exact_same_source8",
                 "committed_production_customer_compiler_driver_and_capability_bytes",
                 "actual_known_create_receipt_replay_late_rls_and_original_retry_only",
                 "closed_node_and_independent_full42_native_full8_observations"]
LITERAL_SCOPES = ["fresh_exact_daemon_image_target_and_private_names",
                  "verified_committed_inputs_and_all_prior_acceptance_artifacts",
                  "same_run_genuine_source8_original_grantor_and_restricted_auth",
                  "exact_three_stdin_only_node_modes_unborn_and_between_mode_state",
                  "sticky_remote_uncertainty_and_exact_owned_cleanup"]
INPUT = "P0D_CUSTOMER_INPUTS_CHANGED"
ENTRY = "P0D_CUSTOMER_ENTRY_UNPROVEN"
COPY = "P0D_CUSTOMER_RUNTIME_COPY_UNCONFIRMED"
CLOSURE = "P0D_CUSTOMER_CLIENT_CLOSURE_UNCONFIRMED"
STOP = "P0D_CUSTOMER_KNOWN_NODE_STOP"
PARITY = "P0D_CUSTOMER_NATIVE_LEDGER_PARITY_UNCONFIRMED"
CODES = {INPUT, ENTRY, COPY, CLOSURE, STOP, PARITY, prior.CODE, proof.RESPONSE, proof.OBSERVATION, proof.FULL42}


def checkout(override=None, *, draft):
    if override is not None:
        if not draft or not override.is_absolute() or override.resolve(strict=True) != override:
            raise ValueError(INPUT)
        return override
    root = SCRIPT.parents[2]
    if SCRIPT != root / HERE:
        raise ValueError(INPUT)
    return root


def load_smoke(root):
    path = root / SMOKE
    before = path.lstat()
    if path.resolve(strict=True) != path or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError(INPUT)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(128 * 1024 + 1)
        finished = os.fstat(stream.fileno())
    if before != opened or before != finished or before != path.lstat() or len(raw) != before.st_size:
        raise ValueError(INPUT)
    if hashlib.sha256(raw).hexdigest() != SMOKE_SHA:
        raise ValueError(INPUT)
    loaded = ModuleType("_workinants_p0d_smoke_owner")
    loaded.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True), loaded.__dict__)
    return loaded


def add(blobs, name, raw, S):
    S.require(name not in blobs or blobs[name] == raw, INPUT)
    blobs[name] = raw


def check_raw(raw, entry, S):
    S.require(type(entry) is dict and set(entry) == {"bytes", "sha256"}
              and type(entry["bytes"]) is int and len(raw) == entry["bytes"] and S.sha(raw) == entry["sha256"], INPUT)


def stored_name(leaf):
    return leaf + ".txt" if leaf.endswith((".js", ".cjs")) else leaf


def capture_proof(root, blobs, S):
    raw = S.read(SCRIPT / "proof/MANIFEST.json")
    S.require(S.sha(raw) == PROOF_SHA, INPUT)
    add(blobs, f"{PROOF}/MANIFEST.json", raw, S)
    manifest = S.unique_json(raw)
    S.require(manifest["state"] == "PREPARED_NOT_RUN" and manifest["main_modes"] == list(proof.MODES)
              and manifest["separate_held_modes"] == ["prior-fingerprint"], INPUT)
    expected = {"README.md", "compile-customer-v1.mjs", "compile-inputs.json", NODE_MAIN, "fixture.json",
                "observe-customer-proof.sql", "compiled/emit-manifest.json"} | {f"compiled/{leaf}" for leaf in COMPILED}
    S.require(set(manifest["files"]) == expected, INPUT)
    for leaf in sorted(expected):
        stored = stored_name(leaf)
        raw = S.read(SCRIPT / "proof" / stored, 128 * 1024)
        check_raw(raw, manifest["files"][leaf], S)
        add(blobs, f"{PROOF}/{stored}", raw, S)
    for leaf in sorted(SOURCE_FILES):
        add(blobs, f"{HERE}/{leaf}", S.read(SCRIPT / leaf, 128 * 1024), S)
    emit = blobs[f"{PROOF}/compiled/emit-manifest.json"]
    S.require(S.sha(emit) == EMIT_SHA, INPUT)
    compile_inputs = S.unique_json(blobs[f"{PROOF}/compile-inputs.json"])
    compiled = S.unique_json(emit)
    S.require(compiled["compilerVersion"] == compile_inputs["version"] == "5.9.3"
              and compile_inputs["nodeVersion"] == "v24.22.1"
              and compiled["compilerSha256"] == compile_inputs["compiler"]["sha256"]
              and set(compiled["files"]) == COMPILED, INPUT)
    for leaf, info in compiled["files"].items():
        check_raw(blobs[f"{PROOF}/compiled/{stored_name(leaf)}"], info, S)
    source_names = {name.removesuffix(".js") + ".ts" for name in COMPILED - {"package.json"}}
    S.require(len(compile_inputs["sources"]) == 5 and {item["path"] for item in compile_inputs["sources"]} == source_names
              and compile_inputs["lock"]["path"] == "package-lock.json", INPUT)
    for item in [compile_inputs["lock"], *compile_inputs["sources"]]:
        path = item["path"]
        raw = S.pinned(root, path, item["sha256"])
        S.require(len(raw) == item["bytes"], INPUT)
        add(blobs, path, raw, S)
    lock = S.unique_json(blobs["package-lock.json"])
    entry = lock["packages"]["node_modules/typescript"]
    S.require(entry["integrity"] == compile_inputs["npmIntegrity"] and entry["version"] == "5.9.3", INPUT)
    fixture = S.unique_json(blobs[f"{PROOF}/fixture.json"])
    S.require(fixture["schema"] == "workinants.p0d-customer-proof-fixture.v1" and fixture["database"] == "wa_p0c_rehearsal"
              and fixture["priorFingerprint"]["state"] == "HELD_SEPARATE_TARGET", INPUT)
    for item in fixture["sourceInputs"].values():
        path = item["path"]
        raw = S.pinned(root, path, item["sha256"])
        S.require(len(raw) == item["bytes"], INPUT)
        add(blobs, path, raw, S)
    return manifest, fixture


def compose(root, tool_archive, run_id, prior_relative=None, prior_sha=None, *, draft):
    smoke = load_smoke(root)
    prepared, renewal, modules = smoke.compose(tool_archive, run_id, draft=True)
    basis, _, _ = modules
    S, P = basis.S, basis.P
    _, packet, blobs, inner, manifest, nested, files, archive = prepared
    S.require(S.sha(blobs[SMOKE]) == SMOKE_SHA, INPUT)
    proof_manifest, _fixture = capture_proof(root, blobs, S)
    prior_summary = None
    if prior_relative is not None or prior_sha is not None:
        prior_summary = prior.verify(root, prior_relative, prior_sha, packet, blobs, smoke, renewal, S)
    S.require(draft or prior_summary is not None, prior.CODE)
    directory = P.SCRATCH / f"wa-cloud-p0d-known-customer-{run_id}"
    pins = {path: S.sha(raw) for path, raw in blobs.items()}
    original = packet.pop("owner_transaction")
    tool_paths = manifest["tools"]["files_sha256"]
    driver = {name: sha for name, sha in tool_paths.items() if name.startswith("node_modules/postgres/")}
    S.require(len(driver) == 37 and original["driver_sha256"] == S.aggregate(driver)
              and smoke.DRIVER.removeprefix("/run/wa-f0-tools/") in driver, INPUT)
    runtime = {"fixture.json", NODE_MAIN} | {f"compiled/{leaf}" for leaf in COMPILED}
    packet.update(schema=SCHEMA, source=None if draft else S.verify_committed(root, blobs),
                  status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_KNOWN_CUSTOMER_REVIEWS",
                  source_pins=pins, source_aggregate_sha256=S.aggregate(pins),
                  nested_manifest=P.bind(directory / "run-manifest.json", nested), archive=P.bind(directory / "source8.tar", archive),
                  known_customer={"status": "NOT_RUN", "modes": list(proof.MODES), "prior_fingerprint": "HELD_SEPARATE_TARGET",
                                  "prior_smoke": prior_summary, "entry_sha256": smoke.ENTRY_SHA, "proof_sha256": PROOF_SHA,
                                  "emit_sha256": EMIT_SHA, "node_sha256": tool_paths["node/bin/node"],
                                  "driver_sha256": S.aggregate(driver), "driver_members": driver,
                                  "runtime_files": {leaf: proof_manifest["files"][leaf] for leaf in sorted(runtime)},
                                  "database": "wa_p0c_rehearsal", "roles": ["wa_app_runtime", "wa_context_issuer"]})
    return (directory, packet, blobs, inner, manifest, nested, files, archive), smoke, renewal, modules


def make_packet(root, tool_archive, prior_relative, prior_sha, *, draft):
    prepared, _, _, (basis, _, _) = compose(root, tool_archive, str(uuid.uuid4()), prior_relative, prior_sha, draft=draft)
    directory, packet, _, _, _, nested, files, archive = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    P.write_new(directory / "run-manifest.json", nested)
    P.write_new(directory / "source8.tar", archive)
    P.write_source(directory / "source8", files)
    raw = S.encode(packet)
    path = directory / "operation.json"
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "sources": len(packet["source_pins"]),
            "runtime": "NOT_RUN", "state": packet["status"]}


def read_closed(root, path, *, draft=False):
    smoke = load_smoke(root)
    _, (basis, _, _) = smoke.mechanism()
    P, S = basis.P, basis.S
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    packet = S.unique_json(raw)
    S.require(packet["schema"] == SCHEMA and packet["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_KNOWN_CUSTOMER_REVIEWS"), INPUT)
    prior_pin = packet["known_customer"]["prior_smoke"]
    prior_args = () if prior_pin is None else (prior_pin["path"], prior_pin["sha256"])
    prepared, smoke, renewal, modules = compose(root, Path(packet["tools"]["path"]), packet["run_id"], *prior_args, draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), INPUT)
    modules[1].compare_source8(directory, nested, files, archive)
    return prepared, smoke, renewal, modules, raw


def review_bindings(packet, raw, plan):
    details = packet["known_customer"]
    return {**plan.review_bindings(packet, raw), "prior_independently_accepted_owner_sha256": details["prior_smoke"]["sha256"],
            "bounded_entry_sha256": details["entry_sha256"], "proof_sha256": details["proof_sha256"],
            "compiled_manifest_sha256": details["emit_sha256"], "node_sha256": details["node_sha256"],
            "driver_sha256": details["driver_sha256"], "runtime_files": details["runtime_files"]}


def exact_reviews(directory, packet, raw, modules):
    basis, plan, _ = modules
    bindings = review_bindings(packet, raw, plan)
    source, source_hash = basis.P.read_review(directory / "source-review.json", schema=SOURCE_SCHEMA,
                                             bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = basis.P.read_review(directory / "literal-review.json", schema=LITERAL_SCHEMA,
                                               bindings={**bindings, "source_review_sha256": source_hash}, scopes=LITERAL_SCOPES)
    basis.S.require(source["source_author"] == literal["source_author"] == AUTHOR, INPUT)
    return {"source": source_hash, "literal": literal_hash, "source_reviewer": source["reviewer"],
            "literal_reviewer": literal["reviewer"]}


def owner_type(root, smoke, renewal, modules):
    basis, _, two = modules
    S = basis.S

    class Owner(smoke.owner_type(renewal, modules)):
        def configure_program(self):
            # Reuse the exact smoke owner and replace only its smoke-specific event hook and evidence.
            two.Owner.configure_program(self)
            self.report.update(schema="workinants.cloud-p0d-known-customer-run-evidence.v1", known_customer={
                "status": "NOT_RUN", "integrated_runtime_qualified": False,
                "prior_fingerprint": "HELD_SEPARATE_TARGET",
                "prior_smoke_sha256": self.operation["known_customer"]["prior_smoke"]["sha256"],
                "modes": {mode: {"status": "NOT_RUN"} for mode in proof.MODES}, "checkpoints": {}, "closure_probes": {}})
            p = self.program
            p.SAFE_FAILURE_CODES |= CODES | smoke.CODES
            prefixes = {"P0D_CUSTOMER", "P0D_CUSTOMER_IDENTITY_SEED", f"NATIVE_{POST}", f"LEDGER_{POST}",
                        "LEDGER_FINGERPRINT_customer-after", *STAGES.values()}
            p.SAFE_FAILURE_STAGES |= prefixes | {f"{name}_CLOSED" for name in prefixes}
            emit = p.event

            def event(stage, status, **values):
                emit(stage, status, **values)
                if (stage, status) == renewal.SEAM:
                    self.report["stage"] = "P0D_CUSTOMER"
                    self.report["known_customer"]["status"] = "IN_PROGRESS"
                    p.save()
                    try:
                        self.run_child()
                    except BaseException:
                        self.report["known_customer"]["status"] = "STOPPED"
                        raise

            p.event = event

        def sticky(self):
            self.transport.unknown = self.docker.remote_unknown = True

        @contextmanager
        def closed_boundary(self, stage):
            p = self.program
            name = f"{stage}_CLOSED"
            start = len(self.report.get("backend_closures", []))
            completed = False
            try:
                with p._RequiredSafetyBoundary("CLOSE", self.name, name):
                    yield
                completed = True
            finally:
                proofs = [item for item in self.report.get("backend_closures", [])[start:] if item["stage"] == name]
                valid = len(proofs) == 1 and proofs[0] == {
                    "stage": name, "scope": "ALL_DATABASES_ALL_ROLES_ALL_TAGS", "observation_completed": True,
                    "counts_valid": True, "migrator_zero": True, "other_clients_zero": True,
                    "all_other_client_backends_absent": True,
                }
                self.report["known_customer"]["closure_probes"][stage] = valid
                if not valid:
                    self.sticky()
                    if completed:
                        raise S.Held(CLOSURE)

        def set_stage(self, stage):
            self.report["stage"] = stage
            self.program.save()

        def copy_sources(self):
            cid = self.resources.cid
            runtime = self.operation["known_customer"]["runtime_files"]
            directories = {str(parent) for leaf in runtime for parent in PurePosixPath(f"{REMOTE}/{leaf}").parents
                           if str(parent) not in ("/run", "/")}
            for path in sorted(directories, key=lambda item: (item.count("/"), item)):
                reply = self.exact_container_exec("--user", "0", cid, "/usr/bin/mkdir", "-m", "0755", "--", path)
                S.require(reply.stdout == b"", COPY)
            for leaf in sorted(runtime):
                raw = self.blobs[f"{PROOF}/{stored_name(leaf)}"]
                reply = self.exact_container_exec("-i", "--user", "0", cid, "/bin/sh", "-ceu", smoke.COPY,
                                                  "wa-copy-known-customer", f"{REMOTE}/{leaf}", input=raw)
                S.require(reply.stdout == b"", COPY)
            self.check_runtime_sources()

        def check_runtime_sources(self):
            cid = self.resources.cid
            details = self.operation["known_customer"]
            runtime = {f"{REMOTE}/{leaf}": info for leaf, info in details["runtime_files"].items()}
            inventory = self.exact_container_exec("--user", "0", cid, "/usr/bin/find", REMOTE, "-xdev", "-printf",
                                                   "%y|%p|%s|%U|%G|%m|%n\n")
            meta = two.validate_inventory(inventory.stdout, {path: (info["bytes"], "444") for path, info in runtime.items()})
            hashes = {path: info["sha256"] for path, info in runtime.items()}
            hashes.update({f"/run/wa-f0-tools/{leaf}": digest for leaf, digest in details["driver_members"].items()})
            hashes[smoke.NODE] = details["node_sha256"]
            result = self.exact_container_exec("--user", "0", cid, "/usr/bin/sha256sum", "--", *sorted(hashes))
            expected = "".join(f"{hashes[path]}  {path}\n" for path in sorted(hashes)).encode()
            S.require(result.stdout == expected and meta["regular_files"] == len(runtime), COPY)
            return {**meta, "node": "PASS", "driver_members": len(details["driver_members"])}

        def observe(self, phase, fixture, known_tables, nodes, previous):
            p = self.program
            stage = STAGES[phase]
            self.set_stage(stage)
            with self.closed_boundary(stage):
                rows = self.closed_record(fixture["sourceInputs"]["complete-state-observe.sql"]["path"])
                scoped = self.closed_record(f"{PROOF}/observe-customer-proof.sql")
            proof.check_full42_shape(rows, known_tables, S)
            proof.check_observation_shape(scoped, S)
            state = self.report["known_customer"]["checkpoints"]
            state[phase] = {"status": "OBSERVED_PENDING_COMPARISON", "full42": p.write_safe(f"customer-{phase}-full42.json", rows),
                            "scope": p.write_safe(f"customer-{phase}-scope.json", scoped),
                            "before_sha256": None if previous is None else p.digest(previous[0]), "after_sha256": p.digest(rows)}
            p.save()
            proof.validate_full42(rows, known_tables, phase, None if previous is None else previous[0], S)
            proof.validate_observation(scoped, rows, nodes, None if previous is None else previous[1], S)
            state[phase]["status"] = "PASS"
            p.save()
            return rows, scoped

        def invoke(self, mode):
            p = self.program
            stage = f"{STAGES[mode]}_NODE"
            p.SAFE_FAILURE_STAGES |= {stage, f"{stage}_CLOSED"}
            self.set_stage(stage)
            state = self.report["known_customer"]["modes"][mode]
            target = self.observed_target()
            cid = self.resources.cid
            S.require(not self.transport.unknown and target["container_id"] == cid and target["network"] == "none"
                      and target["published_ports"] is False, ENTRY)
            state["runtime_readback"] = self.check_runtime_sources()
            passwords = p.passwords[self.name]
            credentials = json.dumps({"app": passwords["wa_app_runtime"], "issuer": passwords["wa_context_issuer"]},
                                     separators=(",", ":")).encode()
            state["status"] = "DISPATCH_PENDING"
            p.save()
            with self.closed_boundary(stage):
                try:
                    reply = self.exact_container_exec("-i", "--user", "65534:65534", cid, "/usr/bin/env", "-i", smoke.NODE,
                                                      f"{REMOTE}/{NODE_MAIN}", mode, smoke.DRIVER, input=credentials,
                                                      timeout=90, allow_fail=True)
                    typed = proof.node_receipt(reply, mode, S, p.all_secrets)
                except BaseException:
                    self.sticky()
                    state["status"] = "CHILD_RESULT_UNCONFIRMED"
                    raise
                stopped = typed["status"] == "STOPPED"
                state["status"] = "CHILD_TERMINAL_STOP" if stopped else "CHILD_PASS_PENDING_OBSERVATION"
                if stopped:
                    p._required_safety_first_exception(S.Held(STOP), stage)
                    if typed.get("pools") == "END_UNCONFIRMED":
                        self.sticky()
                state["node"] = p.write_safe(f"customer-{mode}-node.json", typed)
                p.save()
                S.require(not stopped, STOP)
            return typed

        def run_child(self):
            p = self.program
            state = self.report["known_customer"]
            migrations = self.report["migration_results"]
            S.require(state["prior_smoke_sha256"] is not None and renewal.native_gate(self.report["native_results"])
                      and migrations[-1]["no_pending_message_observed"] is True and not self.transport.unknown
                      and self.report["targets"][self.name]["finalization"] == "PASS" and p.STATE.get("activated") is True, ENTRY)
            target = self.observed_target()
            S.require(target["container_id"] == self.resources.cid and target["network"] == "none"
                      and target["published_ports"] is False, ENTRY)
            native = self.artifact("noop-native-before.json")
            baseline_ledger = self.artifact("noop-ledger-observation.json")
            baseline_fingerprints = self.artifact("initial-after-noop-fingerprints.json")
            fixture = S.unique_json(self.blobs[f"{PROOF}/fixture.json"])
            accepted = S.unique_json(self.blobs[fixture["sourceInputs"]["fixtures.json"]["path"]])
            known_tables = accepted["setup_expected_counts"]
            self.copy_sources()
            nodes = {}
            previous = self.observe("unborn", fixture, known_tables, nodes, None)
            self.set_stage("P0D_CUSTOMER_IDENTITY_SEED")
            with self.closed_boundary("P0D_CUSTOMER_IDENTITY_SEED"):
                S.require(self.closed_sql(smoke.IDENTITY_SEED) == "", proof.OBSERVATION)
                seeded = self.closed_record(fixture["sourceInputs"]["user-coherence-observe.sql"]["path"])
                proof.same(seeded, {"users": 2, "coherent": True}, S, proof.OBSERVATION)
                state["identity_setup"] = p.write_safe("customer-identity-projection.json", seeded)
                installed = p.collect_native(self.name, f"NATIVE_{POST}", "customer-native-after-seed.json")
                S.require(installed == native, PARITY)
            previous = self.observe("seeded", fixture, known_tables, nodes, previous)
            for mode in proof.MODES:
                nodes[mode] = self.invoke(mode)
                previous = self.observe(mode, fixture, known_tables, nodes, previous)
                state["modes"][mode]["status"] = "PASS"
                p.save()
            incoming = p.collect_native(self.name, f"NATIVE_{POST}", "customer-native-after.json")
            registration, ledger = p.ledger_observation(migrations[0], POST)
            final = p.collect_native(self.name, f"NATIVE_{POST}", "customer-native-after-ledger.json")
            comparisons, evidence = p.compare_ledger(registration, ledger, final)
            after = p.fingerprints("customer-after")
            S.require(incoming == final == native and ledger == baseline_ledger and len(comparisons["checks"]) == 22, PARITY)
            state.update(status=PASS, container_id=self.resources.cid, volume_created_at=self.resources.volume_birth,
                         post_ledger=p.write_safe("customer-ledger.json", evidence),
                         full8=p.CATALOG["two"].compare_noop(baseline_fingerprints, after), native_sha256=p.digest(final))
            p.event("P0D_CUSTOMER", PASS)

        def postchecks(self):
            prepared, _, _, runtime, raw = read_closed(root, self.directory / "operation.json")
            S.require(raw == self.raw and prepared[1] == self.operation
                      and exact_reviews(self.directory, self.operation, raw, runtime) == self.reviews, INPUT)
            state = self.report["known_customer"]
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                S.require(state["status"] == PASS and set(state["checkpoints"]) == set(proof.PHASES)
                          and all(item["status"] == "PASS" for item in state["modes"].values()) and not self.transport.unknown,
                          proof.RESPONSE)
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True

    return Owner


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    actions = cli.add_subparsers(dest="action", required=True)
    prepare = actions.add_parser("prepare")
    prepare.add_argument("--tool-archive", type=Path, required=True)
    prepare.add_argument("--owner-smoke")
    prepare.add_argument("--owner-smoke-sha256")
    prepare.add_argument("--draft", action="store_true")
    prepare.add_argument("--draft-checkout", type=Path)
    verify = actions.add_parser("verify")
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--draft", action="store_true")
    verify.add_argument("--draft-checkout", type=Path)
    execute = actions.add_parser("execute")
    execute.add_argument("--packet", type=Path, required=True)
    execute.add_argument(EXECUTE, action="store_true", dest="approved")
    args = cli.parse_args(argv)
    try:
        draft = getattr(args, "draft", False)
        root = checkout(getattr(args, "draft_checkout", None), draft=draft)
        if args.action == "prepare":
            result = make_packet(root, args.tool_archive, args.owner_smoke, args.owner_smoke_sha256, draft=draft)
            print(json.dumps(result))
            return 0
        if args.action == "execute" and not args.approved:
            raise ValueError("P0D_CUSTOMER_EXPLICIT_EXECUTION_REQUIRED")
        prepared, smoke, renewal, modules, raw = read_closed(root, args.packet, draft=draft)
        directory, packet = prepared[:2]
        basis, _, two = modules
        if args.action == "verify":
            print(basis.S.encode({"sha256": basis.S.sha(raw), "runtime": "NOT_RUN", "state": "HELD_VERIFIED"}).decode(), end="")
            return 0
        reviews = exact_reviews(directory, packet, raw, modules)
        os.umask(0o077)
        basis.P.write_new(directory / "attempt.json", basis.S.encode({"run_id": packet["run_id"],
                          "packet_sha256": basis.S.sha(raw), "reviews": reviews}))
        signal.signal(signal.SIGTERM, two.interrupt)
        signal.signal(signal.SIGHUP, two.interrupt)
        return owner_type(root, smoke, renewal, modules)(prepared, raw, reviews).run()
    except BaseException as error:
        code = getattr(error, "code", str(error))
        print(code if type(code) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", code) else "P0D_CUSTOMER_HELD")
        return 1


if __name__ == "__main__":
    sys.exit(main())
