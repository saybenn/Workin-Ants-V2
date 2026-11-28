"""Run the published finite App protocol on a verified living source8 owner."""

import ast
from copy import deepcopy
import datetime
import hashlib
import json
import os
import re
import secrets
import subprocess
import uuid

from host_session import APP_ROLES, BoundedSession, SessionStop
from prepare import APPEND, COORDINATOR, INITIAL, PACKET, PROTOCOL, RUNTIME_TRANSITION, json_bytes, sha


CONTEXT = "scripts/sql-review/run-context-control-rehearsal.py"
SCOPED_READ = "scripts/sql-review/run-scoped-read-companion-rehearsal.py"
COLLECTOR = "scripts/sql-review/collect_native_catalog.sql"
APP_PASS = "PASS_FINITE_TWO_APP_WRITE_CRITERIA_ONLY"
CLOSED_ERRORS = frozenset((
    "APP_LOGIN_SCOPE", "APP_SESSION_START_UNCONFIRMED", "APP_SESSION_DEADLINE", "APP_SESSION_EXIT_UNCONFIRMED",
    "APP_SESSION_ACK_BOUNDARY", "APP_SESSION_TRUNCATED_OUTPUT", "APP_SESSION_OUTPUT_LIMIT",
    "APP_SESSION_RECORD_LIMIT", "APP_SESSION_INPUT_LIMIT", "APP_SESSION_CALL_SCOPE", "APP_SESSION_IO_UNCONFIRMED",
    "APP_SESSION_CLOSURE_UNCONFIRMED", "APP_TRANSPORT_UNKNOWN", "APP_SOCKET_IDENTITY", "APP_RAW_SQL_UNCONFIRMED",
    "EXACT_BACKEND_STILL_LIVE", "SESSION_BEGIN_UNCONFIRMED", "CAPTURE_ACTUAL_IDENTITY", "CAPTURE_FIELDS",
    "CAPTURE_OUTPUT_REQUIRED", "CAPTURE_TUPLE_FORMAT", "SESSION_BACKEND_CHANGED", "SEPARATE_ISSUER_COMMIT_UNCONFIRMED",
    "ISSUER_CREATED_AT_RETURN_REJECTED", "ISSUER_CREATED_AT_RETURN_REQUIRED", "ISSUER_CREATED_AT_TIMESTAMP_REQUIRED",
    "APP_ACTIVE_AUTH_RECEIPTS", "APP_TARGET_IDENTITY", "APP_SECRET_EVIDENCE",
    "APP_PSQL_REVIEWED_ARGUMENTS", "APP_RESTRICTED_GRANTS_ONLY",
))


def require(value, code):
    if not value:
        raise SessionStop(code)


def execute_ast(nodes, relative, namespace):
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, relative, "exec", dont_inherit=True), namespace)
    return namespace


def exact_nodes(raw, names, relative):
    tree = ast.parse(raw, filename=relative)
    nodes = [node for node in tree.body if getattr(node, "name", None) in names]
    require(len(nodes) == len(names) and {node.name for node in nodes} == set(names), "APP_REVIEWED_SOURCE_SURFACE")
    return nodes


def render_protocol(blobs, source8):
    raw = blobs[PROTOCOL].decode()
    prior = "declarations=list(re.finditer(r'CREATE FUNCTION platform_private\\.'+name+r'\\(\\).*?AS\\s+(\\$[a-z_0-9]*\\$)(.*?)\\1;',application,re.S))"
    replacement = (
        "source,creation=_frame_source(identity,application)\n "
        "declarations=list(re.finditer(re.escape(creation+identity)+r'.*?AS\\s+(\\$[a-z_0-9]*\\$)(.*?)\\1;',source,re.S))"
    )
    require(raw.count(prior) == 1 and raw.count("workinants.app-unexpected-business-diagnostic.v3") == 2,
            "APP_DIAGNOSTIC_SOURCE_PATCH")

    def frame_source(identity, initial):
        if identity == RUNTIME_TRANSITION:
            return blobs[APPEND].decode(), "CREATE OR REPLACE FUNCTION "
        return initial, "CREATE FUNCTION "

    namespace = {"_frame_source": frame_source}
    raw = raw.replace(prior, replacement).replace("workinants.app-unexpected-business-diagnostic.v3",
                                                  "workinants.cloud-app-source8-unexpected-diagnostic.v1")
    exec(compile(raw, PROTOCOL, "exec", dont_inherit=True), namespace)
    namespace["UNEXPECTED_SOURCE_FRAMES"] = {
        name: (frame["body_sha256"], frame["lines"]) for name, frame in source8["effective_diagnostic_frames"].items()
    }
    return namespace


def render_context(blobs, safe_code, register_secret):
    shared = dict(deepcopy=deepcopy, datetime=datetime, hashlib=hashlib, json=json, re=re, uuid=uuid, secrets=secrets,
                  safe_code=safe_code, _register_secret=register_secret)
    leaf = {"HeldFailure", "require", "sha", "quote", "unique_json", "returned_created_at", "Session", "Coordinator"}
    nodes = exact_nodes(blobs[CONTEXT], leaf, CONTEXT)
    captured = ast.parse(blobs[CONTEXT], filename=CONTEXT).body
    names = {"DATABASE", "TUPLE", "GRANT_COLUMNS"}
    constants = [node for node in captured if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names]
    require(len(constants) == len(names), "APP_REVIEWED_CONTEXT_CONSTANTS")
    for class_name, methods in (("Session", {"begin", "capture"}),
                                ("Coordinator", {"record", "commit", "grant_values", "issue"})):
        original = next(node for node in nodes if node.name == class_name)
        original.body = [node for node in original.body if isinstance(node, ast.FunctionDef) and node.name in methods]
        require({node.name for node in original.body} == methods, "APP_REVIEWED_CONTEXT_METHODS")
        for method in original.body:
            if method.name in {"commit", "issue"}:
                attempts = [node for node in method.body if isinstance(node, ast.Try) and node.finalbody and not node.handlers]
                require(len(attempts) == 1, "APP_CONTEXT_FIRST_FAILURE_SEAM")
                handler = ast.parse("try:\n pass\nexcept BaseException as error:\n self.evidence.stop(safe_code(error))\n raise")
                attempts[0].handlers = handler.body[0].handlers
            if method.name == "issue":
                points = [index for index, node in enumerate(method.body) if ast.unparse(node) == "token_hash = sha(bytes.fromhex(secret))"]
                require(len(points) == 1, "APP_CONTEXT_CREDENTIAL_EXCLUSION_SEAM")
                method.body.insert(points[0] + 1, ast.parse("_register_secret(secret, token_hash)").body[0])
    return execute_ast([*constants, *nodes], CONTEXT, shared)


def coordinate(owner, native, evidence_dir):
    """Run only the frozen recipes and return a sanitized closed App receipt."""
    blobs = owner.blobs
    source8 = owner.operation["app_source8"]["held_source_proof"]
    program = owner.program
    packet = program.strict_json(blobs[f"{PACKET}/fixtures.json"])
    require(all(template["database_login_role"] == "wa_app_runtime" for template in packet["grants"].values()),
            "APP_RESTRICTED_GRANTS_ONLY")
    runtime = dict(deepcopy=deepcopy, hashlib=hashlib, json=json, os=os, re=re)
    app_names = {"HeldFailure", "need", "sha", "canonical", "digest", "quote", "unique_json", "Evidence",
                 "coordinator_type", "safe_code", "coordinate"}
    execute_ast(exact_nodes(blobs[COORDINATOR], app_names, COORDINATOR), COORDINATOR, runtime)
    historical_safe_code = runtime["safe_code"]

    def safe_code(error):
        code = getattr(error, "code", None)
        return code if type(code) is str and code in CLOSED_ERRORS else historical_safe_code(error)

    def checked_source(relative, source_pins):
        raw = blobs[relative]
        require(sha(raw) == source_pins[relative] == sha(owner.read_source(relative)), "SOURCE_FILE_DRIFT")
        return raw

    def checked_sql(checked_packet, leaf):
        require(checked_packet is packet and leaf in packet["prepared_files_sha256"], "PREPARED_SQL_DRIFT")
        raw = checked_source(f"{PACKET}/{leaf}", owner.operation["source_pins"])
        require(sha(raw) == packet["prepared_files_sha256"][leaf], "PREPARED_SQL_DRIFT")
        return raw.decode()

    def external(value):
        require(value == evidence_dir and value.parent.resolve(strict=True) == value.parent,
                "APP_EVIDENCE_DIRECTORY_IDENTITY")
        return value

    runtime.update(safe_code=safe_code, checked_source=checked_source, checked_sql=checked_sql, external=external,
                   COLLECTOR=COLLECTOR)
    context = render_context(blobs, safe_code, lambda *values: program.all_secrets.extend(values))
    protocol = render_protocol(blobs, source8)

    class Session(BoundedSession, context["Session"]):
        pass

    class Evidence(runtime["Evidence"]):
        def stop(self, code, stage=None):
            super().stop(code, stage)
            self.value.setdefault("first_failure", dict(self.value["unexpected"][0]))

        def save(self):
            self.value["schema"] = "workinants.cloud-app-source8-result.v1"
            self.value["volume_created_at"] = owner.resources.volume_birth
            raw = json_bytes(self.value)
            if len(raw) > 16 * 1024 * 1024 or any(secret.encode() in raw for secret in program.all_secrets):
                self.failed = True
                self.value = {"schema": self.value["schema"], "run_id": self.value["run_id"],
                              "current_stage": "SANITIZATION", "current_case": None, "unexpected": [],
                              "evidence_complete": False, "database_posture": "D"}
                self.stop("APP_SECRET_EVIDENCE")
                if not self.finalizing:
                    super().save()
                    raise SessionStop("APP_SECRET_EVIDENCE")
            return super().save()

    def app_authentication(evidence, container):
        require(container == owner.resources.cid, "APP_TARGET_IDENTITY")
        active = {row["role"]: row for row in owner.report["authentication"] if row["correct_password"] == "PASS_SCRAM"}
        checks = {row["role"]: row["checks"] for row in owner.report["auth_comparisons"]}
        require(all(role in active and role in checks and active[role]["wrong_password"] == "PASS_REJECTED"
                    and active[role]["actual_connection_closed"] is True and checks[role]
                    and all(value is True for value in checks[role].values()) for role in APP_ROLES),
                "APP_ACTIVE_AUTH_RECEIPTS")
        evidence.value["authentication"] = [active[role] for role in APP_ROLES]
        evidence.save()

    class CloudContext(context["Coordinator"]):
        def __init__(self, plan, packet, native, target, evidence, session_factory):
            self.plan, self.packet, self.native, self.target, self.evidence = plan, packet, native, target, evidence
            self.container, self.session_factory = plan["immutable_container_id"], session_factory
            self.instances, self.sequence = {}, 0
            self.application = checked_source(INITIAL, plan["packet_files_sha256"]).decode()

        def resource(self):
            observed = owner.observed_target()
            require(observed["container_id"] == self.container and observed["volume_created_at"] == owner.resources.volume_birth,
                    "APP_TARGET_IDENTITY")
            self.record({"stage": "RESOURCE_PREFLIGHT", "immutable_created_CID_verified": True})

        def socket_checked(self):
            require(not owner.transport.unknown, "APP_TRANSPORT_UNKNOWN")
            try:
                require(owner.docker.socket_identity() == owner.docker.origin, "APP_SOCKET_IDENTITY")
            except BaseException:
                self.uncertain("APP_SOCKET_IDENTITY")
                raise SessionStop("APP_SOCKET_IDENTITY") from None

        def uncertain(self, code):
            owner.transport.unknown = True
            owner.docker.remote_unknown = True
            self.evidence.stop(code)

        def psql(self, role):
            require(role in APP_ROLES, "APP_LOGIN_SCOPE")
            args = owner.psql_args(owner.name, role)
            require(args.count("SHOW_CONTEXT=never") == 1, "APP_PSQL_REVIEWED_ARGUMENTS")
            args[args.index("SHOW_CONTEXT=never")] = "SHOW_CONTEXT=errors"
            return args

        def spawn(self, role):
            self.socket_checked()
            return owner.transport.io.Popen(owner.docker.argv(*self.psql(role)), cwd=str(owner.root), shell=False,
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        def raw(self, role, text):
            self.socket_checked()
            require(type(text) is str and 0 < len(text.encode()) <= 4 * 1024 * 1024, "APP_RAW_SQL_UNCONFIRMED")
            args = self.psql(role)
            try:
                result = owner.exact_container_exec(*args[1:], input=text.encode(), timeout=90,
                                                    allow_fail=True, profile="native_oracle")
                require(type(result.returncode) is int and result.returncode == 0 and result.stderr == b"",
                        "APP_RAW_SQL_UNCONFIRMED")
                return result.stdout.decode("utf-8").strip()
            except BaseException:
                self.uncertain("APP_RAW_SQL_UNCONFIRMED")
                raise SessionStop("APP_RAW_SQL_UNCONFIRMED") from None

        def require_backend_absent(self, role, backend):
            require(role in APP_ROLES and role == backend["login"] and re.fullmatch(r"[1-9][0-9]{0,9}", backend["pid"])
                    and re.fullmatch(r"[0-9T:+. \-]{1,64}", backend["started"]), "APP_SESSION_CLOSURE_UNCONFIRMED")
            query = ("SELECT count(*) FROM pg_stat_activity WHERE pid=" + backend["pid"] + " AND backend_start="
                     + runtime["quote"](backend["started"]) + "::timestamptz AND usename=" + runtime["quote"](role)
                     + " AND datname=" + runtime["quote"](context["DATABASE"]) + ";")
            require(self.raw("postgres", query) == "0", "EXACT_BACKEND_STILL_LIVE")

    context.update(Coordinator=CloudContext, Session=Session, API={"authentication_preflight": app_authentication})
    scoped_methods = {"__init__", "session", "global_closure", "native_parity", "retention", "fixture_commit"}
    scope = exact_nodes(blobs[SCOPED_READ], {"coordinator_type"}, SCOPED_READ)[0]
    scoped_class = scope.body[0]
    require(isinstance(scoped_class, ast.ClassDef) and scoped_class.name == "Coordinator", "APP_SCOPED_SOURCE_SURFACE")
    scoped_class.body = [node for node in scoped_class.body if isinstance(node, ast.FunctionDef)
                         and node.name in scoped_methods]
    require({node.name for node in scoped_class.body} == scoped_methods, "APP_SCOPED_SOURCE_METHODS")
    base = execute_ast([scope], SCOPED_READ, dict(runtime))
    plan = {
        "run_id": owner.operation["run_id"], "immutable_container_id": owner.resources.cid,
        "source_commit": owner.operation["source"]["commit"], "source_tree": owner.operation["source"]["tree"],
        "packet_sha256": sha(owner.raw), "packet_files_sha256": owner.operation["source_pins"],
        "reviewed_packet_sha256": sha(blobs[f"{PACKET}/fixtures.json"]),
        "reviewed_content_sha256": packet["source_only_packet_sha256"],
    }
    runtime.update(Evidence=Evidence, load_inputs=lambda checked: (packet, native, owner.target, protocol, context, base))
    return runtime["coordinate"](plan, evidence_dir)
