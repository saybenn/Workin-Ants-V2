"""Compose the frozen finite Worker child with the reviewed Cloud pipe transport."""

import ast
from copy import deepcopy
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import time
from types import SimpleNamespace
import uuid

import prepare


COORDINATOR = "scripts/sql-review/run-worker-recovery-control-rehearsal.py"
CONTEXT = "scripts/sql-review/run-context-control-rehearsal.py"
SCOPED = "scripts/sql-review/run-scoped-read-companion-rehearsal.py"
COLLECTOR = "scripts/sql-review/collect_native_catalog.sql"
OPERATOR = (f"{prepare.RECON}/local-f0-operation-sources/worker-recovery-owned-guard-observation-v2/"
            "local_f0_worker_recovery_guard_observation_v2_operation_steps.py.txt")
SHARED = "scripts/sql-review/cloud-app-source8-v1"
PIPE = f"{SHARED}/host_session.py"
CONTEXT_RENDERER = f"{SHARED}/app_child.py"
PINS = {
    PIPE: "0149b82add667b485a2d6e044ee252f5f30add8db8ea87df9147cf9181fe3757",
    CONTEXT_RENDERER: "5f3a616745ba26ad6baae8266bbb254b4d791510289a1ba290bb30002fc5acfc",
    OPERATOR: "654319c0676ae37dd7a23ae2c4bc253ddcc5c58850d959d3bf5c450d45e0e071",
}
ROLES = prepare.ROLES
AUTH_ROLES = ("postgres", "wa_migrator", *ROLES[1:])
RESULT_SCHEMA = "workinants.cloud-worker-source8-result.v1"
PASS = "PASS_FINITE_WORKER_RECOVERY_CORE_ONLY"
STOPPED = "STOPPED_PARTIAL_EVIDENCE_PRESERVED"
LIMIT = 16 * 1024 * 1024
AUTH_FIELDS = {"json_parsed", "object", "fields", "string_fields", "login", "scram_identity", "database",
               "client_loopback", "server_loopback"}
ERRORS = frozenset({"WORKER_TRANSPORT_UNCERTAIN", "WORKER_IDENTITY_SETUP_SCOPE", "WORKER_SOCKET_IDENTITY",
                    "WORKER_CURRENT_TARGET_REQUIRED", "WORKER_RESTRICTED_LOGIN_SCOPE", "WORKER_SESSION_CAP",
                    "WORKER_UNDECLARED_OVERLAP", "WORKER_EXACT_BACKEND_STILL_LIVE", "WORKER_CLOCK_CALL_SCOPE",
                    "WORKER_RAW_SQL_UNCONFIRMED", "WORKER_AUTH_RECEIPTS", "WORKER_EVIDENCE_IO_UNCONFIRMED",
                    "WORKER_SECRET_EVIDENCE", "SOURCE_FILE_DRIFT", "PREPARED_SQL_DRIFT"})


class Hold(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def require(condition, code):
    if not condition:
        raise Hold(code)


def selected(raw, names, label):
    nodes = [node for node in ast.parse(raw, filename=label).body if getattr(node, "name", None) in names]
    require(len(nodes) == len(names) and {node.name for node in nodes} == set(names), "WORKER_REVIEWED_METHODS")
    return nodes


def compiled(nodes, label, binding):
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, label, "exec", dont_inherit=True), binding)
    return binding


def pipe_class(blobs):
    raw = blobs[PIPE]
    require(hashlib.sha256(raw).hexdigest() == PINS[PIPE], "WORKER_PIPE_SOURCE_DRIFT")
    old = b'APP_ROLES = ("postgres", "wa_context_issuer", "wa_app_runtime")'
    ack = b'"WA_CLOUD_APP_ACK|"'
    require(raw.count(old) == raw.count(ack) == 1, "WORKER_PIPE_DECLARATION")
    raw = raw.replace(old, b"APP_ROLES = " + repr(ROLES).encode()).replace(ack, b'"WA_CLOUD_WORKER_ACK|"')
    scope = {}
    exec(compile(raw, PIPE, "exec", dont_inherit=True), scope)
    return scope["BoundedSession"], scope["SessionStop"]


def current_auth(owner, evidence, cid):
    require(cid == owner.resources.cid, "WORKER_CURRENT_TARGET_REQUIRED")
    p = owner.program
    rows_from = len(owner.report.get("authentication", ()))
    checks_from = len(owner.report.get("auth_comparisons", ()))
    p.hba_preflight(AUTH_ROLES)
    p.auth_roles(AUTH_ROLES, True)
    rows = owner.report["authentication"][rows_from:]
    checks = owner.report["auth_comparisons"][checks_from:]
    require(tuple(row["role"] for row in rows) == tuple(row["role"] for row in checks) == AUTH_ROLES
            and all(row == {"role": role, "correct_password": "PASS_SCRAM", "wrong_password": "PASS_REJECTED",
                            "actual_connection_closed": True} for role, row in zip(AUTH_ROLES, rows, strict=True))
            and all(set(row["checks"]) == AUTH_FIELDS and all(flag is True for flag in row["checks"].values())
                    for row in checks), "WORKER_AUTH_RECEIPTS")
    evidence.value.update(authentication=[{"role": role, "transport": "TCP_127.0.0.1_5432",
                                           "correct_password": "PASS_SCRAM", "wrong_password": "PASS_REJECTED",
                                           "wrong_password_exit_code": 2} for role in AUTH_ROLES],
                          current_auth_role="wa_worker", authentication_comparison=checks[-1]["checks"],
                          effective_hba_selections=owner.report["effective_hba_selections"])
    evidence.save()


def admit_slot(coordinator, role):
    active = [session for session in coordinator.sessions if not session.closed]
    workers = [session for session in active if session.role == "wa_worker"]
    require(role in ROLES and len(active) < 3 and len(workers) <= 2, "WORKER_SESSION_CAP")
    if role == "wa_worker" and workers:
        require(len(workers) == 1 and workers[0] is coordinator.concurrent_old
                and coordinator.evidence.value["current_case"] == "real-higher-fence-reclaim-with-retained-effect",
                "WORKER_UNDECLARED_OVERLAP")
    if role == "wa_identity_service_authority":
        require(coordinator.identity_scope, "WORKER_IDENTITY_SETUP_SCOPE")


def coordinate(owner, native, evidence_dir, source):
    blobs, p = owner.blobs, owner.program
    volume_birth = owner.resources.volume_birth
    require(type(volume_birth) is str and 0 < len(volume_birth) <= 256, "WORKER_CURRENT_TARGET_REQUIRED")
    pins = owner.operation["source_pins"]
    proof = owner.operation["worker_source8"]["held_proof"]
    packet = source.unique_json(blobs[prepare.FIXTURE])
    require(all(template["database_login_role"] in ("wa_app_runtime", "wa_worker")
                for template in packet["grants"].values()), "WORKER_RESTRICTED_LOGIN_SCOPE")
    proto = source.module(prepare.ROOT, prepare.PROTOCOL, blobs[prepare.PROTOCOL])
    frames = prepare.effective_protocol(source, proto, blobs[prepare.INITIAL], blobs[prepare.APPEND],
                                        source.unique_json(blobs[prepare.EXPECTED]))
    require(frames == proof["effective_guard_frames"], "WORKER_EFFECTIVE_FRAME_DRIFT")
    bounded, session_stop = pipe_class(blobs)
    values = dict(deepcopy=deepcopy, hashlib=hashlib, json=json, os=os, re=re, time=time, secrets=secrets)
    names = {"HeldFailure", "need", "sha", "canonical", "digest", "quote", "unique_json", "Evidence", "coordinator_type",
             "safe_code", "coordinate"}
    runtime = compiled(selected(blobs[COORDINATOR], names, COORDINATOR), COORDINATOR, values)
    historical_safe = runtime["safe_code"]

    def safe_code(error):
        code = getattr(error, "code", None)
        if isinstance(error, session_stop):
            return "WORKER_TRANSPORT_UNCERTAIN"
        return code if type(code) is str and code in ERRORS else historical_safe(error)

    def checked_source(relative, expected):
        raw = blobs[relative]
        require(source.sha(raw) == expected[relative] and raw == owner.read_source(relative), "SOURCE_FILE_DRIFT")
        return raw

    def checked_sql(fixture, leaf):
        require(fixture is packet and leaf in packet["prepared_files_sha256"], "PREPARED_SQL_DRIFT")
        raw = checked_source(f"{prepare.PACKET}/{leaf}", pins)
        require(source.sha(raw) == packet["prepared_files_sha256"][leaf], "PREPARED_SQL_DRIFT")
        return raw.decode()

    def external(path):
        require(path == evidence_dir and path.parent.resolve(strict=True) == path.parent, "WORKER_EVIDENCE_PATH")
        return path

    reference = blobs[CONTEXT_RENDERER]
    require(source.sha(reference) == PINS[CONTEXT_RENDERER], "WORKER_CONTEXT_RENDERER_DRIFT")
    context_render = compiled(selected(reference, {"exact_nodes", "execute_ast", "render_context"}, CONTEXT_RENDERER),
                              CONTEXT_RENDERER, {**values, "ast": ast, "uuid": uuid, "datetime": datetime,
                                                 "CONTEXT": CONTEXT, "require": require})["render_context"]
    context = context_render(blobs, safe_code, lambda *private: p.all_secrets.extend(private))

    class Session(bounded, context["Session"]):
        pass

    class CloudContext(context["Coordinator"]):
        def __init__(self, plan, fixture, native_value, target, evidence, session_factory):
            self.plan, self.packet, self.native, self.target, self.evidence = plan, fixture, native_value, target, evidence
            self.container, self.session_factory = plan["immutable_container_id"], session_factory
            self.application = checked_source(prepare.INITIAL, pins).decode()
            self.instances, self.sequence = {}, 0
            self.identity_scope = self.identity_attempted = False

        def resource(self):
            observed = owner.observed_target()
            require(observed["container_id"] == self.container and observed["volume_created_at"] == owner.resources.volume_birth,
                    "WORKER_CURRENT_TARGET_REQUIRED")
            self.record({"stage": "RESOURCE_PREFLIGHT", "immutable_created_CID_verified": True})

        def commit(self, role, text, label):
            if role != "wa_identity_service_authority":
                require(role == "postgres", "WORKER_RESTRICTED_LOGIN_SCOPE")
                return super().commit(role, text, label)
            require(not self.identity_attempted and label == "INDEPENDENT_SYNTHETIC_SERVICE_BOOTSTRAP"
                    and text == checked_sql(packet, "identity-bootstrap.sql"), "WORKER_IDENTITY_SETUP_SCOPE")
            self.identity_scope = self.identity_attempted = True
            try:
                return super().commit(role, text, label)
            finally:
                self.identity_scope = False

        def socket_checked(self):
            socket_checked()

        def uncertain(self, _code):
            owner.transport.unknown = owner.docker.remote_unknown = True
            self.evidence.stop("WORKER_TRANSPORT_UNCERTAIN")

        def psql(self, role):
            return psql(role)

        def spawn(self, role):
            admit_slot(self, role)
            self.socket_checked()
            return owner.transport.io.Popen(owner.docker.argv(*self.psql(role)), cwd=str(prepare.ROOT), shell=False,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        def raw(self, role, text):
            result = read_only(role, text, 90, "native_oracle")
            require(type(result.returncode) is int and result.returncode == 0 and result.stderr == "",
                    "WORKER_RAW_SQL_UNCONFIRMED")
            return result.stdout.strip()

        def require_backend_absent(self, role, backend):
            require(role in ROLES and role == backend["login"] and re.fullmatch(r"[1-9][0-9]{0,9}", backend["pid"])
                    and re.fullmatch(r"[0-9T:+. \-]{1,64}", backend["started"]), "WORKER_EXACT_BACKEND_STILL_LIVE")
            quote = runtime["quote"]
            query = ("SELECT count(*) FROM pg_stat_activity WHERE pid=" + backend["pid"] + " AND backend_start="
                     + quote(backend["started"]) + "::timestamptz AND usename=" + quote(role)
                     + " AND datname=" + quote(context["DATABASE"]) + ";")
            require(self.raw("postgres", query) == "0", "WORKER_EXACT_BACKEND_STILL_LIVE")

    def socket_checked():
        require(not owner.transport.unknown, "WORKER_TRANSPORT_UNCERTAIN")
        try:
            require(owner.docker.socket_identity() == owner.docker.origin, "WORKER_SOCKET_IDENTITY")
        except BaseException:
            owner.transport.unknown = owner.docker.remote_unknown = True
            raise Hold("WORKER_SOCKET_IDENTITY") from None

    def psql(role):
        require(role in ROLES, "WORKER_RESTRICTED_LOGIN_SCOPE")
        args = owner.psql_args(owner.name, role)
        require(args[0] == "exec" and args.count(owner.resources.cid) == args.count("SHOW_CONTEXT=never") == 1,
                "WORKER_CURRENT_TARGET_REQUIRED")
        args[args.index("SHOW_CONTEXT=never")] = "SHOW_CONTEXT=errors"
        return args

    def read_only(role, text, timeout, profile):
        socket_checked()
        require(role in {"postgres", "wa_context_issuer"} and type(text) is str
                and 0 < len(text.encode()) <= 4 * 1024 * 1024, "WORKER_RAW_SQL_UNCONFIRMED")
        args = psql(role)
        try:
            result = owner.exact_container_exec(*args[1:], input=text.encode(), timeout=timeout,
                                                allow_fail=True, profile=profile)
            require(type(result.returncode) is int and 0 <= result.returncode <= 3, "WORKER_TRANSPORT_UNCERTAIN")
            socket_checked()
            return subprocess.CompletedProcess(args, result.returncode, result.stdout.decode(), result.stderr.decode())
        except BaseException:
            owner.transport.unknown = owner.docker.remote_unknown = True
            raise Hold("WORKER_TRANSPORT_UNCERTAIN") from None

    def clock_run(args, *, input, text, capture_output, timeout, shell):
        require(args == psql("postgres") and input == checked_sql(packet, "A-clock.sql") and text is True
                and capture_output is True and shell is False and type(timeout) is float and 0 < timeout <= 5,
                "WORKER_CLOCK_CALL_SCOPE")
        return read_only("postgres", input, timeout, "control")

    class Evidence(runtime["Evidence"]):
        def save(self):
            self.value.update(schema=RESULT_SCHEMA, volume_created_at=volume_birth)
            encoded = source.encode(self.value)
            if len(encoded) > LIMIT or any(secret.encode() in encoded for secret in p.all_secrets):
                self.value = {key: self.value[key] for key in ("schema", "run_id", "database_posture", "volume_created_at")}
                self.value.update(current_stage="SANITIZATION", current_case=None, results=[], operations=[],
                                  unexpected=[], evidence_complete=False)
                self.stop("WORKER_SECRET_EVIDENCE")
                self.failed = True
                super().save()
                if not self.finalizing:
                    raise Hold("WORKER_SECRET_EVIDENCE")
                return False
            return super().save()

    context.update(Coordinator=CloudContext, Session=Session,
                   API={"authentication_preflight": lambda evidence, cid: current_auth(owner, evidence, cid)})
    scope = selected(blobs[SCOPED], {"coordinator_type"}, SCOPED)[0]
    methods = {"__init__", "session", "global_closure", "native_parity", "retention", "fixture_commit"}
    require(isinstance(scope.body[0], ast.ClassDef) and scope.body[0].name == "Coordinator", "WORKER_SCOPED_METHODS")
    scope.body[0].body = [node for node in scope.body[0].body if isinstance(node, ast.FunctionDef) and node.name in methods]
    require({node.name for node in scope.body[0].body} == methods, "WORKER_SCOPED_METHODS")
    runtime.update(checked_source=checked_source, checked_sql=checked_sql, external=external, safe_code=safe_code,
                   COLLECTOR=COLLECTOR, subprocess=SimpleNamespace(run=clock_run, TimeoutExpired=subprocess.TimeoutExpired))
    base = compiled([scope], SCOPED, dict(runtime))
    original_type = runtime["coordinator_type"]

    def coordinator_type(ctx, source_base):
        class Worker(original_type(ctx, source_base)):
            def __init__(self, *args):
                super().__init__(*args)
                private = list(self.leases.values())
                p.all_secrets.extend([*private, *(source.sha(bytes.fromhex(value)) for value in private)])

        return Worker

    plan = {"run_id": owner.operation["run_id"], "immutable_container_id": owner.resources.cid,
            "source_commit": owner.operation["source"]["commit"], "source_tree": owner.operation["source"]["tree"],
            "packet_sha256": source.sha(owner.raw), "packet_files_sha256": pins,
            "reviewed_packet_sha256": pins[prepare.FIXTURE], "reviewed_content_sha256": prepare.CONTENT}
    runtime.update(Evidence=Evidence, coordinator_type=coordinator_type,
                   load_inputs=lambda _: (packet, native, owner.target, vars(proto), context, base))
    return runtime["coordinate"](plan, evidence_dir)


def verify_complete(owner, value, native_hash, source):
    birth = owner.resources.volume_birth
    require(type(value) is dict and type(birth) is str and birth and value.get("volume_created_at") == birth,
            "WORKER_CHILD_REFERENCE_UNCONFIRMED")
    raw = owner.blobs[OPERATOR]
    require(source.sha(raw) == PINS[OPERATOR], "WORKER_RESULT_VERIFIER_SOURCE_DRIFT")
    nodes = selected(raw, {"verify_worker_operations", "verify_worker_result"}, OPERATOR)
    for before, after in ((prepare.OLD_FRAME[0], prepare.RUNTIME_FRAME[0]), ("workinants.worker-recovery-evidence.v1", RESULT_SCHEMA)):
        matches = [item for function in nodes for item in ast.walk(function)
                   if isinstance(item, ast.Constant) and item.value == before]
        require(len(matches) == 1, "WORKER_RESULT_VERIFIER_ANCHOR")
        matches[0].value = after
    p = owner.program
    verify = compiled(nodes, OPERATOR, dict(
        re=re, need=require, exact=p.exact, digest=p.digest, WORKER_FIXTURES=source.unique_json(owner.blobs[prepare.FIXTURE]),
        WORKER_FIXTURES_SHA=prepare.GENERIC_PINS[prepare.FIXTURE], WORKER_CONTENT_SHA=prepare.CONTENT,
        RUN_ID=owner.operation["run_id"], COMMIT=owner.operation["source"]["commit"], TREE=owner.operation["source"]["tree"],
        PACKET=source.sha(owner.raw), TARGETS=[{"name": owner.name}], created_containers={owner.name: owner.resources.cid},
        ROLES=AUTH_ROLES, report={"qualified_native_snapshot_sha256": native_hash},
    ))["verify_worker_result"]
    historical_shape = dict(value)
    del historical_shape["volume_created_at"]
    summary = verify(historical_shape, None)
    summary["component_report_sha256"] = p.digest(value)
    return summary
