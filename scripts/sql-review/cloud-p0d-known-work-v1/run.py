"""Prepare or run the exact bounded P0-D Node known-work owner."""

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
import time
from types import ModuleType
import uuid

import node_session

SCRIPT = Path(__file__).resolve().parent
HERE = "scripts/sql-review/cloud-p0d-known-work-v1"
CHILD = HERE + "/child"
SMOKE = "scripts/sql-review/cloud-p0d-owner-transaction-v1/run.py"
SMOKE_SHA = "da73ebb0eff61387da7548a9f4b48f9d22cc22c449652f83ac9d9805fbb22cef"
PRIOR = "scripts/sql-review/cloud-p0d-known-customer-v1/prior.py"
PRIOR_SHA = "004de86f46de7429a8d01a77ef0333517cefdb831a1c2731fe693779b0eceea7"
OWNER_ACCEPTANCE = "context/reconciliation/cloud-phase0-evidence/2026-11-27/owner-716a1162/acceptance.json"
OWNER_ACCEPTANCE_SHA = "e913b361e228f277e3a2af392d894ddd03ebfcd66a2e6df76cd0b53dd2e085b3"
ENTRY_SHA = "968f10aebc657eaf6653303d5ea6d56b9aaaf6a1746012a52768927e30d49987"
CHILD_MANIFEST_SHA = "8f1f7aba261f6310ce2120f2220cdd9aa67f84ce4e0f3784407481a43cfbc9de"
APP = "review-output/app-write-two-guard-observation-v2"
SERVICE = "review-output/lease-revoke-control-rehearsal/identity-worker-bootstrap.sql"
APP_FIXTURE, FULL42, SOURCE_SQL, IDENTITY_SQL = (f"{APP}/{name}" for name in (
    "fixtures.json", "complete-state-observe.sql", "source-customer-observe.sql", "user-coherence-observe.sql"))
OWN_FILES = {"run.py", "node_session.py", "observe-setup.sql", "README.md", "test_run.py"}
COMPILED = {"fixture/fixture.js", "package.json", "server/platform/runtime/work-leases.js", "server/platform/persistence/owner-transaction.js"}
PHASES = ("INIT", "SOURCE", "SCHEDULE", "REPLAY", "CLAIM", "LIVE_RECLAIM", "RENEW", "COPIED_HASH_RENEW", "RECLAIM", "STALE_RENEW", "FINISH")
PACKET = "workinants.cloud-p0d-known-work-operation.v1"
SOURCE_SCHEMA = "workinants.cloud-p0d-known-work-source-review.v1"
LITERAL_SCHEMA = "workinants.cloud-p0d-known-work-literal-review.v1"
SOURCE_SCOPES = ["exact_716a_owner_acceptance_and_same_source8", "committed_node_work_source_and_compiled_child_closure",
                 "actual_known_source_schedule_claim_renew_reclaim_only", "phase_closed_backend_full42_and_source8_parity"]
LITERAL_SCOPES = ["fresh_managed_daemon_image_and_exact_owned_absence", "exact_packet_tool_and_child_source_bindings",
                  "bounded_one_node_stdin_phase_protocol_and_server_clock", "sticky_failure_and_exclusive_resource_cleanup"]
PASS = "PASS_FINITE_KNOWN_WORK_LEASE_MECHANICS_ONLY"
STAGE = "P0D_KNOWN_WORK"
POST = f"{STAGE}_AFTER"
INPUT = f"{STAGE}_INPUTS_CHANGED"
ENTRY = f"{STAGE}_ENTRY_UNPROVEN"
COPY = f"{STAGE}_RUNTIME_COPY_UNCONFIRMED"
STATE = f"{STAGE}_STATE_UNCONFIRMED"
CLOSE = f"{STAGE}_BACKEND_CLOSURE_UNCONFIRMED"
CLOCK = f"{STAGE}_CLOCK_UNCONFIRMED"
STOP = f"{STAGE}_TYPED_NODE_STOP"
PARITY = f"{STAGE}_NATIVE_LEDGER_PARITY_UNCONFIRMED"
VALIDATION = "P0D_WORK_RESULT_UNCONFIRMED"
EXECUTE = "--execute-reviewed-cloud-p0d-known-work-v1"
AUTHOR = "/root/foundation_gates"
GRANTS, WORK = "platform.database_action_grant", "platform.runtime_work_item"
SOURCE_DELTA = {"app.customer_profiles": 1, "app.customer_profile_lifecycle_event": 1, "platform.runtime_command_receipt": 1,
                "platform.owner_mutation_evidence": 1, "platform.runtime_outbox_message": 2}
SEED_DELTA = {"app.users": 2, "app.user_security_profiles": 2, "platform_private.identity_service_authorization": 1,
              "platform_private.identity_service_receipt": 1}
CHECKPOINT_DELTAS = {"SEEDED": SEED_DELTA, "INIT": {}, "SOURCE": {**SOURCE_DELTA, GRANTS: 1},
                     "SCHEDULE": {WORK: 1, GRANTS: 1}, "REPLAY": {GRANTS: 1}, "CLAIM": {WORK: 0, GRANTS: 1},
                     "LIVE_RECLAIM": {GRANTS: 1}, "RENEW": {WORK: 0, GRANTS: 1}, "COPIED_HASH_RENEW": {GRANTS: 1},
                     "RECLAIM": {WORK: 0, GRANTS: 1}, "STALE_RENEW": {GRANTS: 1}, "FINISH": {}}
WORK_COUNT_FIELDS = {"work_total", "restricted_clients", "work_attempts", "runtime_inbox", "track_effects", "track_enrollments"}
SOURCE_FIELDS = ("source_count", "source_distinct_xids", "source_xid")


def checkout(override, *, draft):
    if override is not None:
        if draft and override.is_absolute() and override.resolve(strict=True) == override:
            return override
    elif SCRIPT == SCRIPT.parents[2] / HERE:
        return SCRIPT.parents[2]
    raise ValueError(INPUT)


def load_smoke(root):
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid, value.st_nlink,
                value.st_size, value.st_mtime_ns, value.st_ctime_ns)

    path = root / SMOKE
    before = path.lstat()
    if path.resolve(strict=True) != path or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError(INPUT)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(128 * 1024 + 1)
        finished = os.fstat(stream.fileno())
    if (not identity(before) == identity(opened) == identity(finished) == identity(path.lstat()) or len(raw) != before.st_size
            or hashlib.sha256(raw).hexdigest() != SMOKE_SHA):
        raise ValueError(INPUT)
    loaded = ModuleType("_workinants_known_work_smoke")
    loaded.__file__ = str(path)
    exec(compile(raw, str(path), "exec", dont_inherit=True), loaded.__dict__)
    return loaded


def store(blobs, path, raw, S):
    S.require(path not in blobs or blobs[path] == raw, INPUT)
    blobs[path] = raw


def logical_path(name):
    return name + ".txt" if name.endswith((".js", ".mjs", ".cjs", ".ts")) else name


def capture_child(root, blobs, S):
    manifest = S.read(SCRIPT / "child/manifest.json", 128 * 1024)
    S.require(S.sha(manifest) == CHILD_MANIFEST_SHA, INPUT)
    store(blobs, f"{CHILD}/manifest.json", manifest, S)
    packet = S.unique_json(manifest)
    S.require(packet["schema"] == "workinants.p0d-known-work-child-source-manifest.v1"
              and packet["author"] == "/root/pending_packets" and packet["execution"] == "NOT_RUN"
              and packet["posture"] == "D" and type(packet["assertion_promotions"]) is int and packet["assertion_promotions"] == 0
              and packet["compiled"]["version"] == "5.9.3" and set(packet["compiled"]["files"]) == COMPILED,
              INPUT)
    inputs = packet["source_pins"]
    S.require({APP_FIXTURE, FULL42, SOURCE_SQL, SERVICE, "server/platform/runtime/work-leases.ts",
               "server/platform/persistence/owner-transaction.ts", "package-lock.json"} <= inputs.keys(), INPUT)
    for name, pin in inputs.items():
        # The freeze records exact compiler bytes separately. Only repository sources are Git inputs.
        raw = S.pinned(root, name, pin)
        if not name.startswith("node_modules/"):
            store(blobs, name, raw, S)
    runtime = {node_session.ENTRY: packet["child"], "worker-fixture.json": packet["worker_fixture"],
               **{f"compiled/{path}": value for path, value in packet["compiled"]["files"].items()}}
    S.require(runtime == packet["runtime_files"] and {"validate.py", "observe-work.sql", "observe-grants.sql"}
              <= packet["support_files"].keys() and not (runtime.keys() & packet["support_files"].keys()), INPUT)
    assets = {**runtime, **packet["support_files"], "projected-source-fixture.ts": packet["projected_source_fixture"]}
    for name, expected in assets.items():
        stored = logical_path(name)
        raw = S.read(SCRIPT / "child" / stored, 128 * 1024)
        S.require(expected == {"bytes": len(raw), "sha256": S.sha(raw)}, INPUT)
        store(blobs, f"{CHILD}/{stored}", raw, S)
    # The known protocol and grants are verified again at every response boundary.
    validation = S.module(root, f"{CHILD}/validate.py", blobs[f"{CHILD}/validate.py"])
    S.require(validation.PHASES == PHASES and {"CLAIM", "LIVE_RECLAIM", "RENEW", "COPIED_HASH_RENEW", "RECLAIM", "STALE_RENEW"}
              == set(validation.CLOCK_OFFSETS), INPUT)
    return packet, runtime, validation


def compose(root, archive, run_id, *, draft):
    smoke = load_smoke(root)
    old, renewal, modules = smoke.compose(archive, run_id, draft=True)
    _directory, packet, blobs, inner, manifest, nested, source8, bundle = old
    basis, _, _ = modules
    S, P = basis.S, basis.P
    S.require(S.sha(blobs[SMOKE]) == SMOKE_SHA and smoke.ENTRY_SHA == ENTRY_SHA, INPUT)
    for name, digest in ((PRIOR, PRIOR_SHA), (node_session.APP_PIPE, node_session.APP_PIPE_SHA)):
        store(blobs, name, S.pinned(root, name, digest), S)
    prior = S.module(root, PRIOR, blobs[PRIOR]).verify(root, OWNER_ACCEPTANCE, OWNER_ACCEPTANCE_SHA, packet, blobs, smoke, renewal, S)
    for leaf in sorted(OWN_FILES):
        store(blobs, f"{HERE}/{leaf}", S.read(SCRIPT / leaf, 128 * 1024), S)
    store(blobs, IDENTITY_SQL, S.pinned(root, IDENTITY_SQL, "14000b439a0175ac3b458eb5d87d778013624b54d0f3b77d32202ca71ad87305"), S)
    child, runtime, validation = capture_child(root, blobs, S)
    tool_files = manifest["tools"]["files_sha256"]
    postgres = {name: digest for name, digest in tool_files.items() if name.startswith("node_modules/postgres/")}
    initial = packet.pop("owner_transaction")
    S.require(len(postgres) == 37 and S.aggregate(postgres) == initial["driver_sha256"]
              and child["rehearsal_tool_archive_sha256"] == packet["tools"]["sha256"]
              and child["node"]["sha256"] == tool_files["node/bin/node"], INPUT)
    directory = P.SCRATCH / f"wa-cloud-p0d-known-work-{run_id}"
    pins = {name: S.sha(raw) for name, raw in blobs.items()}
    packet.update(schema=PACKET, source=None if draft else S.verify_committed(root, blobs),
                  status="SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_KNOWN_WORK_REVIEWS",
                  source_pins=pins, source_aggregate_sha256=S.aggregate(pins),
                  nested_manifest=P.bind(directory / "run-manifest.json", nested), archive=P.bind(directory / "source8.tar", bundle),
                  known_work={"status": "NOT_RUN", "prior_owner": prior, "entry_sha256": ENTRY_SHA, "phases": list(PHASES),
                              "child_manifest_sha256": pins[f"{CHILD}/manifest.json"], "runtime_files": runtime,
                              "node_sha256": child["node"]["sha256"], "driver_members": postgres,
                              "driver_sha256": S.aggregate(postgres), "fixture_setup_only": True,
                              "database": "wa_p0c_rehearsal", "node_roles": ["wa_app_runtime", "wa_worker", "wa_context_issuer"]})
    return (directory, packet, blobs, inner, manifest, nested, source8, bundle), smoke, renewal, modules, validation


def make_packet(root, archive, *, draft):
    prepared, _, _, (basis, _, _), _ = compose(root, archive, str(uuid.uuid4()), draft=draft)
    directory, packet, _, _, _, nested, source8, bundle = prepared
    P, S = basis.P, basis.S
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    for name, raw in (("run-manifest.json", nested), ("source8.tar", bundle)):
        P.write_new(directory / name, raw)
    P.write_source(directory / "source8", source8)
    raw = S.encode(packet)
    P.write_new(directory / "operation.json", raw)
    return {"packet": str(directory / "operation.json"), "sha256": S.sha(raw), "sources": len(packet["source_pins"]),
            "runtime": "NOT_RUN", "state": packet["status"]}


def read_closed(root, path, *, draft):
    smoke = load_smoke(root)
    _, (basis, _, _) = smoke.mechanism()
    P, S = basis.P, basis.S
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    packet = S.unique_json(raw)
    S.require(packet["schema"] == PACKET and packet["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_KNOWN_WORK_REVIEWS"), INPUT)
    assembled = compose(root, Path(packet["tools"]["path"]), packet["run_id"], draft=draft)
    prepared, _, _, modules, _ = assembled
    directory, expected, _, _, _, nested, source8, bundle = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), INPUT)
    modules[1].compare_source8(directory, nested, source8, bundle)
    return (*assembled, raw)


def bindings(packet, raw, plan):
    work = packet["known_work"]
    return {**plan.review_bindings(packet, raw), "prior_owner_acceptance_sha256": work["prior_owner"]["sha256"],
            "entry_sha256": work["entry_sha256"], "child_manifest_sha256": work["child_manifest_sha256"],
            "node_sha256": work["node_sha256"], "driver_sha256": work["driver_sha256"], "runtime_files": work["runtime_files"]}


def reviews(directory, packet, raw, modules):
    basis, plan, _ = modules
    details = bindings(packet, raw, plan)
    source, source_sha = basis.P.read_review(directory / "source-review.json", schema=SOURCE_SCHEMA, bindings=details, scopes=SOURCE_SCOPES)
    literal, literal_sha = basis.P.read_review(directory / "literal-review.json", schema=LITERAL_SCHEMA,
        bindings={**details, "source_review_sha256": source_sha}, scopes=LITERAL_SCOPES)
    allowed_authors = {AUTHOR, "/root/pending_packets"}
    basis.S.require(source["source_author"] == literal["source_author"] == AUTHOR and source["reviewer"] not in allowed_authors
                    and literal["reviewer"] not in allowed_authors, INPUT)
    return {"source": source_sha, "literal": literal_sha, "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def count(value):
    return type(value) is int and 0 <= value <= 8192


def full42(value, tables, S):
    S.require(type(value) is dict and len(tables) == 42 and set(value) == set(tables)
              and all(type(row) is dict and set(row) == {"count", "rows_sha256"} and count(row["count"])
                      and type(row["rows_sha256"]) is str and S.HASH.fullmatch(row["rows_sha256"]) for row in value.values()), STATE)


def compare42(value, previous, phase, S):
    if previous is None:
        S.require(phase == "UNBORN" and all(row == {"count": 0, "rows_sha256": S.sha(b"[]")} for row in value.values()), STATE)
        return
    S.require(phase in CHECKPOINT_DELTAS, STATE)
    deltas = CHECKPOINT_DELTAS[phase]
    for key, row in value.items():
        before = previous[key]
        if key in deltas:
            S.require(row["count"] == before["count"] + deltas[key] and row["rows_sha256"] != before["rows_sha256"], STATE)
        else:
            S.require(row == before, STATE)


def observed_work(value, S, validation):
    S.require(type(value) is dict and set(value) == WORK_COUNT_FIELDS | {"server_ms", "work", *SOURCE_FIELDS}
              and all(count(value[key]) for key in WORK_COUNT_FIELDS) and type(value["server_ms"]) is int
              and 10**12 <= value["server_ms"] < 10**13, STATE)
    S.require(count(value["source_count"]) and count(value["source_distinct_xids"])
              and (value["source_xid"] is None or type(value["source_xid"]) is str and validation.XID.fullmatch(value["source_xid"])), STATE)
    row = value["work"]
    if row is not None:
        S.require(type(row) is dict and type(row.get("identity_exact")) is bool, STATE)
        validation.check_work_row({**row, "identity_exact": True})
    return value


def scoped_counts(value, S):
    S.require(all(value[key] == 0 for key in WORK_COUNT_FIELDS - {"work_total"})
              and value["work_total"] == (0 if value["work"] is None else 1), STATE)


def grant_readback(value, S, validation):
    if (type(value) is not dict or set(value) != {"count", "distinct_hashes", "grants"}
            or not count(value["count"]) or not count(value["distinct_hashes"])
            or type(value["grants"]) is not list or len(value["grants"]) > len(validation.OUTCOMES)):
        return None
    keys = ("role", "runtime_xid", "issuer_xid", "fields_sha256", "row_sha256", "identity_exact", "metadata_exact")
    safe = []
    for row in value["grants"]:
        if (type(row) is not dict or not set(keys) <= row.keys() or row["role"] not in ("wa_app_runtime", "wa_worker")
                or not all(type(row[key]) is str and validation.XID.fullmatch(row[key]) for key in ("runtime_xid", "issuer_xid"))
                or not all(type(row[key]) is str and S.HASH.fullmatch(row[key]) for key in ("fields_sha256", "row_sha256"))
                or not all(type(row[key]) is bool for key in ("identity_exact", "metadata_exact"))):
            return None
        safe.append({key: row[key] for key in keys})
    return {"count": value["count"], "distinct_hashes": value["distinct_hashes"], "grants": safe}


def source_proof(value):
    return tuple(value[key] for key in SOURCE_FIELDS)


def phase_file(phase, kind):
    return f"known-work-{phase.lower().replace('_', '-')}-{kind}.json"


def owner_type(root, smoke, renewal, modules, validation):
    basis, _, two = modules
    S = basis.S

    class Owner(smoke.owner_type(renewal, modules)):
        def configure_program(self):
            two.Owner.configure_program(self)
            self.active_node = None
            self.report.update(schema="workinants.cloud-p0d-known-work-run-evidence.v1", known_work={
                "status": "NOT_RUN", "phases": {phase: {"status": "NOT_RUN"} for phase in PHASES},
                "checkpoints": {}, "closure_probes": {}, "prior_owner_acceptance_sha256": OWNER_ACCEPTANCE_SHA,
                "business_dispatch_qualified": False, "assertion_promotions": 0})
            p = self.program
            p.SAFE_FAILURE_CODES |= {INPUT, ENTRY, COPY, STATE, CLOSE, CLOCK, STOP, PARITY, VALIDATION} | smoke.CODES | node_session.CODES
            stages = {STAGE, f"NATIVE_{POST}", f"LEDGER_{POST}", "LEDGER_FINGERPRINT_known-work-after", f"{STAGE}_FIXTURE"}
            stages |= {f"{STAGE}_{phase}{ending}" for phase in ("UNBORN", "SEEDED", *PHASES) for ending in ("", "_NODE", "_CLOCK")}
            p.SAFE_FAILURE_STAGES |= stages | {name + "_CLOSED" for name in stages}
            emit = p.event

            def event(stage, status, **safe):
                emit(stage, status, **safe)
                if (stage, status) == renewal.SEAM:
                    self.report["known_work"]["status"] = "IN_PROGRESS"
                    self.stage(STAGE)
                    try:
                        self.run_child()
                    except BaseException:
                        self.report["known_work"]["status"] = "STOPPED"
                        raise

            p.event = event

        def stage(self, name):
            self.report["stage"] = name
            self.program.save()

        def sticky(self):
            self.transport.unknown = self.docker.remote_unknown = True

        def check_socket(self, code):
            try:
                S.require(not self.transport.unknown and self.docker.socket_identity() == self.docker.origin, code)
            except BaseException:
                self.sticky()
                raise S.Held(code) from None

        def exact_container_exec(self, *args, input=None, timeout=30, allow_fail=False, profile="control"):
            if self.active_node is not None and not self.active_node.closed:
                timeout = min(timeout, int(self.active_node.limit(1)))
            return super().exact_container_exec(*args, input=input, timeout=timeout, allow_fail=allow_fail, profile=profile)

        @contextmanager
        def closed(self, stage):
            name = f"{stage}_CLOSED"
            before = len(self.report.get("backend_closures", []))
            completed = False
            try:
                with self.program._RequiredSafetyBoundary("CLOSE", self.name, name):
                    yield
                completed = True
            finally:
                expected = {"stage": name, "scope": "ALL_DATABASES_ALL_ROLES_ALL_TAGS", "observation_completed": True,
                            "counts_valid": True, "migrator_zero": True, "other_clients_zero": True,
                            "all_other_client_backends_absent": True}
                new = [row for row in self.report.get("backend_closures", [])[before:] if row["stage"] == name]
                confirmed = new == [expected]
                self.report["known_work"]["closure_probes"][stage] = confirmed
                if not confirmed:
                    self.sticky()
                    if completed:
                        raise S.Held(CLOSE)

        def runtime_sources(self):
            plan = self.operation["known_work"]
            cid, remote = self.resources.cid, node_session.REMOTE
            runtime = {f"{remote}/{leaf}": info for leaf, info in plan["runtime_files"].items()}
            directories = {str(parent) for path in runtime for parent in PurePosixPath(path).parents if str(parent) not in ("/", "/run")}
            for path in sorted(directories, key=lambda name: (name.count("/"), name)):
                reply = self.exact_container_exec("--user", "0", cid, "/usr/bin/mkdir", "-m", "0755", "--", path)
                S.require(reply.stdout == b"", COPY)
            for leaf in sorted(plan["runtime_files"]):
                reply = self.exact_container_exec("-i", "--user", "0", cid, "/bin/sh", "-ceu", smoke.COPY,
                    "wa-copy-known-work", f"{remote}/{leaf}", input=self.blobs[f"{CHILD}/{logical_path(leaf)}"])
                S.require(reply.stdout == b"", COPY)
            result = self.exact_container_exec("--user", "0", cid, "/usr/bin/find", remote, "-xdev", "-printf", two.TREE_FORMAT)
            layout = two.validate_inventory(result.stdout, {path: (info["bytes"], "444") for path, info in runtime.items()})
            hashes = {path: info["sha256"] for path, info in runtime.items()}
            hashes.update({f"/run/wa-f0-tools/{leaf}": digest for leaf, digest in plan["driver_members"].items()})
            hashes[node_session.NODE] = plan["node_sha256"]
            result = self.exact_container_exec("--user", "0", cid, "/usr/bin/sha256sum", "--", *sorted(hashes))
            S.require(result.stdout == "".join(f"{hashes[path]}  {path}\n" for path in sorted(hashes)).encode(), COPY)
            return {**layout, "node_verified": True, "driver_members": 37}

        def observe(self, phase, tables, prior, worker, node=None, before_ms=None):
            name = f"{STAGE}_{phase}"
            self.stage(name)
            with self.closed(name):
                values = self.closed_record(FULL42)
                raw_scope = self.closed_record(f"{CHILD}/observe-work.sql")
                grants = self.closed_record(f"{CHILD}/observe-grants.sql")
                fact = self.closed_record(f"{HERE}/observe-setup.sql") if phase == "SEEDED" else None
                source = self.closed_record(SOURCE_SQL) if phase == "SOURCE" else None
            readback = {"full42_sha256": S.sha(S.encode(values)), "scope_sha256": S.sha(S.encode(raw_scope)),
                        "grants_sha256": S.sha(S.encode(grants)), "fixture_sha256": S.sha(S.encode(fact)),
                        "source_sha256": S.sha(S.encode(source))}
            try:
                full42(values, tables, S)
                readback["full42"] = values
            except S.Held:
                pass
            try:
                readback["scope"] = observed_work(raw_scope, S, validation)
            except (S.Held, validation.Held):
                pass
            safe_grants = grant_readback(grants, S, validation)
            if safe_grants is not None:
                readback["grants"] = safe_grants
            state = self.report["known_work"]["checkpoints"]
            state[phase] = {"readback": self.program.write_safe(phase_file(phase, "readback"), readback)}
            self.program.save()
            S.require({"full42", "scope", "grants"} <= readback.keys(), STATE)
            scoped = readback["scope"]
            scoped_counts(scoped, S)
            before = prior["full42"] if prior else None
            compare42(values, before, phase, S)
            old_work = prior["scope"]["work"] if prior else None
            old_grants = prior["grants"]["grants"] if prior else []
            old_source = source_proof(prior["scope"]) if prior else (0, 0, None)
            S.require((prior is None or scoped["server_ms"] >= prior["scope"]["server_ms"])
                      and (before_ms is None or scoped["server_ms"] >= before_ms), CLOCK)
            if phase in validation.OUTCOMES:
                xid = validation.grant_observation(phase, grants, old_grants, worker)
                validation.work_observation(phase, scoped["work"], old_work, xid, node["lease"], before_ms, scoped["server_ms"])
            else:
                expected_grants = prior["grants"] if prior else {"count": 0, "distinct_hashes": 0, "grants": []}
                S.require(S.encode(grants) == S.encode(expected_grants) and scoped["work"] == old_work, STATE)
            S.require(values[GRANTS]["count"] == grants["count"] and values[WORK]["count"] == scoped["work_total"], STATE)
            if phase == "SEEDED":
                S.require(S.encode(fact) == S.encode({"worker_service_exact": True}), STATE)
            if phase == "SOURCE":
                app = S.unique_json(self.blobs[APP_FIXTURE])
                S.require(source_proof(scoped) == (6, 1, xid)
                          and S.encode(source) == S.encode(app["source_customer"]["observer_expected"]), STATE)
            else:
                S.require(source_proof(scoped) == old_source, STATE)
            value = {"full42": values, "scope": scoped, "grants": grants, "fixture": fact, "source": source}
            state[phase]["observation"] = self.program.write_safe(phase_file(phase, "observation"), value)
            self.program.save()
            return value

        def clock(self, phase, current):
            name = f"{STAGE}_{phase}_CLOCK"
            self.stage(name)

            def sample():
                with self.closed(name):
                    measured = observed_work(self.closed_record(f"{CHILD}/observe-work.sql"), S, validation)
                scoped_counts(measured, S)
                S.require({key: value for key, value in measured.items() if key != "server_ms"}
                          == {key: value for key, value in current["scope"].items() if key != "server_ms"}
                          and measured["server_ms"] >= current["scope"]["server_ms"], CLOCK)
                return measured["server_ms"]

            server = sample()
            before = server
            if phase == "RECLAIM":
                remaining = current["scope"]["work"]["deadline_ms"] - server
                S.require(remaining <= 26000, CLOCK)
                if remaining > 0:
                    delay = (remaining + 250) / 1000
                    self.active_node.limit(delay + 1)
                    time.sleep(delay)
                    server = sample()
                S.require(server >= current["scope"]["work"]["deadline_ms"] and server >= before, CLOCK)
            elif phase != "CLAIM":
                S.require(current["scope"]["work"]["deadline_ms"] - server >= 2000, CLOCK)
            return before, server

        def invoke(self, session, phase, payload, server_ms=None):
            stage = f"{STAGE}_{phase}_NODE"
            self.stage(stage)
            state = self.report["known_work"]["phases"][phase]
            state["status"] = "DISPATCH_PENDING"
            self.program.save()
            with self.closed(stage):
                result = session.advance(phase, payload, server_ms)
                stopped = result["status"] == "STOPPED"
                if stopped:
                    if result["outcome_unconfirmed"] or not result["pools_closed"]:
                        self.sticky()
                    self.program._required_safety_first_exception(S.Held(STOP), stage)
                    state["status"] = "CHILD_TERMINAL_STOP"
                elif phase == "FINISH":
                    state["status"] = "CHILD_TERMINAL_PASS_PENDING_OBSERVATION"
                else:
                    state["status"] = "ACKNOWLEDGED_PENDING_OBSERVATION"
                state["node"] = self.program.write_safe(phase_file(phase, "node"), result)
                self.program.save()
                S.require(not stopped, STOP)
            return result

        def setup(self, native):
            stage = f"{STAGE}_FIXTURE"
            p = self.program
            self.stage(stage)
            with self.closed(stage):
                S.require(self.closed_sql(smoke.IDENTITY_SEED) == ""
                          and S.encode(self.closed_record(IDENTITY_SQL)) == S.encode({"users": 2, "coherent": True}), STATE)
                response = self.command(self.psql_args(self.name, "wa_identity_service_authority"), self.blobs[SERVICE].decode())
                S.require(type(response.returncode) is int and response.returncode == 0 and response.stdout == "" and response.stderr == "", STATE)
            after_seed = p.collect_native(self.name, f"NATIVE_{POST}", "known-work-native-after-seed.json")
            S.require(after_seed == native, PARITY)

        def run_child(self):
            p = self.program
            state = self.report["known_work"]
            migrations = self.report["migration_results"]
            S.require(renewal.native_gate(self.report["native_results"]) and migrations[-1]["no_pending_message_observed"] is True
                      and not self.transport.unknown and self.report["targets"][self.name]["finalization"] == "PASS"
                      and p.STATE.get("activated") is True, ENTRY)
            target = self.observed_target()
            S.require(target["container_id"] == self.resources.cid and target["network"] == "none" and target["published_ports"] is False, ENTRY)
            native = self.artifact("noop-native-before.json")
            old_ledger = self.artifact("noop-ledger-observation.json")
            old_rows = self.artifact("initial-after-noop-fingerprints.json")
            state["runtime_readback"] = self.runtime_sources()
            tables = S.unique_json(self.blobs[APP_FIXTURE])["setup_expected_counts"]
            worker = S.unique_json(self.blobs[f"{CHILD}/worker-fixture.json"])
            current = self.observe("UNBORN", tables, None, worker)
            self.setup(native)
            current = self.observe("SEEDED", tables, current, worker)
            self.stage(f"{STAGE}_INIT_NODE")
            session = node_session.session_type(self.blobs[node_session.APP_PIPE], root, S, validation)(self)
            self.active_node = session
            try:
                values = p.passwords[self.name]
                credentials = {label: values[role] for label, role in (("app", "wa_app_runtime"), ("worker", "wa_worker"), ("issuer", "wa_context_issuer"))}
                S.require(len(set(credentials.values())) == 3 and all(type(value) is str and S.HASH.fullmatch(value) for value in credentials.values()), ENTRY)
                for phase in PHASES:
                    server_ms = None
                    if phase in validation.CLOCK_OFFSETS:
                        first, server_ms = self.clock(phase, current)
                        state["phases"][phase]["db_clock_samples"] = {"first_ms": first, "send_ms": server_ms}
                    payload = ((json.dumps({"phase": "INIT", **credentials}, separators=(",", ":")) + "\n").encode() if phase == "INIT"
                               else validation.phase_message(phase, server_ms))
                    response = self.invoke(session, phase, payload, server_ms)
                    current = self.observe(phase, tables, current, worker, response, server_ms)
                    state["phases"][phase]["status"] = "PASS"
                    p.save()
                S.require(session.closed and session.index == len(PHASES) and not self.transport.unknown, CLOSE)
            except BaseException as error:
                p._required_safety_first_exception(error, self.report["stage"])
                try:
                    session.terminate_unconfirmed()
                except BaseException:
                    pass
                raise
            finally:
                self.active_node = None
            before = p.collect_native(self.name, f"NATIVE_{POST}", "known-work-native-after.json")
            registration, ledger = p.ledger_observation(migrations[0], POST)
            after = p.collect_native(self.name, f"NATIVE_{POST}", "known-work-native-after-ledger.json")
            comparisons, evidence = p.compare_ledger(registration, ledger, after)
            fingerprints = p.fingerprints("known-work-after")
            S.require(before == after == native and ledger == old_ledger and len(comparisons["checks"]) == 22, PARITY)
            state.update(status=PASS, container_id=self.resources.cid, volume_created_at=self.resources.volume_birth,
                         post_ledger=p.write_safe("known-work-ledger.json", evidence),
                         full8=p.CATALOG["two"].compare_noop(old_rows, fingerprints), native_sha256=p.digest(after))
            p.event(STAGE, PASS)

        def postchecks(self):
            prepared, _, _, runtime, _, raw = read_closed(root, self.directory / "operation.json", draft=False)
            S.require(raw == self.raw and prepared[1] == self.operation
                      and reviews(self.directory, self.operation, raw, runtime) == self.reviews, INPUT)
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                state = self.report["known_work"]
                S.require(state["status"] == PASS and all(row["status"] == "PASS" for row in state["phases"].values())
                          and not self.transport.unknown, CLOSE)
            self.report["immutable_source_postcheck"] = "PASS"
            if self.transport.unknown:
                self.report["postcheck_remote_uncertainty_retained"] = True

    return Owner


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="operation", required=True)
    for action in ("prepare", "verify", "execute"):
        current = commands.add_parser(action)
        current.add_argument("--tool-archive" if action == "prepare" else "--packet", type=Path, required=True)
        if action == "execute":
            current.add_argument(EXECUTE, action="store_true", dest="approved")
        else:
            current.add_argument("--draft", action="store_true")
            current.add_argument("--draft-checkout", type=Path)
    args = cli.parse_args(argv)
    try:
        draft = getattr(args, "draft", False)
        root = checkout(getattr(args, "draft_checkout", None), draft=draft)
        if args.operation == "prepare":
            print(json.dumps(make_packet(root, args.tool_archive, draft=draft)))
            return 0
        if args.operation == "execute" and not args.approved:
            raise ValueError(f"{STAGE}_EXPLICIT_EXECUTION_REQUIRED")
        prepared, smoke, renewal, modules, validation, raw = read_closed(root, args.packet, draft=draft)
        directory, packet = prepared[:2]
        basis, _, two = modules
        if args.operation == "verify":
            print(basis.S.encode({"sha256": basis.S.sha(raw), "runtime": "NOT_RUN", "state": "HELD_VERIFIED"}).decode(), end="")
            return 0
        approved = reviews(directory, packet, raw, modules)
        os.umask(0o077)
        basis.P.write_new(directory / "attempt.json", basis.S.encode({"run_id": packet["run_id"],
                          "packet_sha256": basis.S.sha(raw), "reviews": approved}))
        signal.signal(signal.SIGTERM, two.interrupt)
        signal.signal(signal.SIGHUP, two.interrupt)
        return owner_type(root, smoke, renewal, modules, validation)(prepared, raw, approved).run()
    except BaseException as error:
        code = getattr(error, "code", str(error))
        print(code if type(code) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", code) else f"{STAGE}_HELD")
        return 1


if __name__ == "__main__":
    sys.exit(main())
