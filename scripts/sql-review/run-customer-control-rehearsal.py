"""Dormant reviewed Customer subset coordinator; no runtime on import/--help.

--execute-reviewed-customer-controls requires an independently reviewed external
run plan and the fixed b59 Customer packet. No provisioning/migrate/reset/worker
or owner UPDATE/CAS runs here. Existing first-rehearsal and migration packets
remain immutable. Every selected control stays NOT_RUN in the evidence report.
"""
import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import queue
import re
import runpy
import secrets
import subprocess
import threading
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT.parent
PACKET = ROOT / "review-output/customer-control-rehearsal"
PACKET_SHA256 = "b59ab33ba26a29d2d82ee4f7f289d26e95300b7afb8ce7eaf7806fd5fb08a9c3"
API_PATH = "scripts/sql-review/run-first-rehearsal.py"
HOST_PATH = "scripts/sql-review/run-local-f0-migrate.py"
COLLECTOR = "scripts/sql-review/collect_native_catalog.sql"
SOURCE_MODULES = ("scripts/sql-review/run-customer-control-rehearsal.py", API_PATH, HOST_PATH,
                  "scripts/sql-review/rehearsal-diagnostics.py", "scripts/prepare-local-f0-history.py", COLLECTOR)
# Import/--help are helper-free. The complete transitive runpy chain is pinned
# and verified before either namespace may execute in load_helpers().
API = {}
HOST = {}
ACK = "WA_CUSTOMER_COORDINATOR_COMMIT_ACK"
TUPLE_PREFIX = "WA_CUSTOMER_COORDINATOR_TUPLE|"
ROLES = {"postgres", "wa_context_issuer", "wa_app_runtime"}
HEADER = re.compile(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)')
FRAME = re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function ([a-z_][a-z_0-9]*\.[a-z_][a-z_0-9]*)\(\) line ([1-9][0-9]{0,3}) at (IF|assignment|RETURN|SQL statement|PERFORM|RAISE)')
STATES = {"42501", "42703", "P0001", "P0002", "23514", "23505", "23503", "22012"}


class HeldFailure(Exception):
    def __init__(self, code): self.code = code; super().__init__(code)


def require(value, code):
    if not value: raise HeldFailure(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",", ":"))
def quote(value): return "'" + str(value).replace("'", "''") + "'"


def unique_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def external_file(value):
    path = Path(value)
    require(path.is_absolute(), "ABSOLUTE_EXTERNAL_PATH_REQUIRED")
    path = path.resolve()
    require(path.is_relative_to(TASK) and not path.is_relative_to(ROOT), "TASK_EXTERNAL_PATH_REQUIRED")
    return path


def packet_file(relative):
    require(type(relative) is str and Path(relative).name == relative and relative not in ("", ".", ".."), "PACKET_FILE_NAME")
    return PACKET / relative


def verified_sql_text(path, expected):
    """Hash and execute/decode the SAME bytes, including every mid-run read.

    Initial load pins are admission checks, not permission to re-read arbitrary
    later disk contents as postgres or as a restricted operation.
    """
    require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected), "SQL_SOURCE_PIN_REQUIRED")
    try: raw = path.read_bytes()
    except Exception: raise HeldFailure("SQL_SOURCE_UNREADABLE") from None
    require(sha(raw) == expected, "SQL_SOURCE_DRIFT")
    try: return raw.decode("utf8")
    except UnicodeError: raise HeldFailure("SQL_SOURCE_ENCODING") from None


def packet_sql(packet, relative):
    return verified_sql_text(packet_file(relative), packet["files_sha256"].get(relative))


def application_sql(packet):
    relative = "review-output/foundation-application.review.sql"
    return verified_sql_text(ROOT / relative, packet["source_inputs_sha256"].get(relative))


def verify_source_modules(pins):
    require(type(pins) is dict and set(pins) == set(SOURCE_MODULES) and
            all(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) for value in pins.values()), "COORDINATOR_MODULE_PINS")
    try: matched = all(pins[path] == sha((ROOT / path).read_bytes()) for path in SOURCE_MODULES)
    except Exception: raise HeldFailure("COORDINATOR_SOURCE_UNREADABLE") from None
    require(matched, "COORDINATOR_SOURCE_DRIFT")


def load_helpers(pins):
    """Verify the whole helper chain before its first executable import.

    run-first imports rehearsal-diagnostics; the host coordinator imports history
    preparation. Both transitive dependencies appear in SOURCE_MODULES. Helper
    namespaces are assigned only after both reviewed imports finish silently.
    All failure text/output stays in memory and is discarded.
    """
    API.clear(); HOST.clear()
    verify_source_modules(pins)
    output, errors = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(output), redirect_stderr(errors):
            api = runpy.run_path(str(ROOT / API_PATH))
            host = runpy.run_path(str(ROOT / HOST_PATH))
    except BaseException: raise HeldFailure("REVIEWED_HELPER_LOAD_FAILED") from None
    require(not output.getvalue() and not errors.getvalue(), "REVIEWED_HELPER_OUTPUT_REJECTED")
    require(all(callable(api.get(name)) for name in ("psql", "run", "grant_sql", "authentication_preflight", "HeldFailure")) and
            all(callable(host.get(name)) for name in ("validate_manifest", "docker_json", "inspect_live", "verify_image", "HeldFailure")), "REVIEWED_HELPER_API_INVALID")
    API.update(api); HOST.update(host)


def failure_code(error):
    if isinstance(error, HeldFailure): return error.code
    for namespace, code in ((API, "AUTHENTICATION_OR_SQL_HELPER_REFUSED"), (HOST, "RESOURCE_GUARD_REFUSED")):
        kind = namespace.get("HeldFailure")
        if isinstance(kind, type) and isinstance(error, kind): return code
    if isinstance(error, KeyboardInterrupt): return "INTERRUPTED"
    if isinstance(error, (subprocess.TimeoutExpired, queue.Empty)): return "TIMEOUT"
    return "INVALID_IO_RESPONSE_OR_INTERNAL"


def load_inputs(plan):
    require(type(plan) is dict and set(plan) == {"schema", "scope", "reviewed_packet_sha256", "source_modules_sha256", "target_manifest", "native_snapshot", "native_comparison", "scenario_names"}, "RUN_PLAN_FIELDS")
    require(plan["schema"] == "workinants.customer-control-run.v1" and plan["scope"] == "REVIEWED_LOCAL_CUSTOMER_CREATE_SUBSET_ONLY", "RUN_PLAN_SCOPE")
    require(plan["reviewed_packet_sha256"] == PACKET_SHA256, "REVIEWED_PACKET_REQUIRED")
    pins = plan["source_modules_sha256"]
    verify_source_modules(pins)
    raw = (PACKET / "fixtures.json").read_bytes()
    require(sha(raw) == PACKET_SHA256, "CUSTOMER_PACKET_DRIFT")
    packet = unique_json(raw.decode("utf8"))
    require(packet["schema"] == "workinants.customer-control-fixtures.v1" and packet["status"] == "NOT_RUN", "CUSTOMER_PACKET_SCOPE")
    for path, expected in packet["source_inputs_sha256"].items():
        require(sha((ROOT / path).read_bytes()) == expected, "CUSTOMER_SOURCE_INPUT_DRIFT")
    for path, expected in (("scripts/prepare-customer-control-rehearsal.py", packet["generator_source_sha256"]), ("scripts/check-customer-control-rehearsal.py", packet["focused_check_source_sha256"])):
        require(sha((ROOT / path).read_bytes()) == expected, "CUSTOMER_SOURCE_INPUT_DRIFT")
    for path, expected in packet["files_sha256"].items():
        require(sha(packet_file(path).read_bytes()) == expected, "CUSTOMER_SQL_DRIFT")
    names = plan["scenario_names"]
    available = [case["name"] for case in packet["cases"]]
    require(type(names) is list and names and len(names) == len(set(names)) and [name for name in available if name in names] == names, "APPROVED_CASE_SUBSET_ORDER")
    load_helpers(pins)
    target = HOST["validate_manifest"](plan["target_manifest"])
    require(target["source"]["integrated_sql_sha256"] == packet["source_inputs_sha256"]["review-output/foundation-application.review.sql"], "TARGET_SQL_SOURCE_MISMATCH")
    loaded = {}
    for key in ("native_snapshot", "native_comparison"):
        entry = plan[key]
        fields = {"path", "sha256", "source_expected_sha256"} if key == "native_comparison" else {"path", "sha256"}
        require(type(entry) is dict and set(entry) == fields, "NATIVE_REVIEW_FILE_FIELDS")
        value = external_file(entry["path"]).read_bytes()
        require(sha(value) == entry["sha256"], "NATIVE_REVIEW_FILE_DRIFT")
        loaded[key] = unique_json(value.decode("utf8"))
    snapshot, comparison = loaded["native_snapshot"], loaded["native_comparison"]
    require(snapshot.get("format") == "workinants.native-catalog.v1" and snapshot.get("server_version_num") == 170011 and snapshot.get("read_only") is True and snapshot.get("collected_as") == "postgres" and snapshot.get("collector_is_superuser") is True, "REVIEWED_NATIVE_SNAPSHOT_REQUIRED")
    source_expected = plan["native_comparison"]["source_expected_sha256"]
    require(type(source_expected) is str and re.fullmatch("[0-9a-f]{64}", source_expected) and comparison.get("source_expected_sha256") == source_expected, "REVIEWED_NATIVE_SOURCE_BINDING_REQUIRED")
    require(comparison.get("format") == "workinants.catalog-comparison.v1" and comparison.get("status") == "PASS" and comparison.get("native_snapshot_sha256") == sha(canonical(snapshot).encode("utf8")), "REVIEWED_NATIVE_PARITY_PASS_REQUIRED")
    return packet, snapshot, [case for case in packet["cases"] if case["name"] in names]


def function_bodies(application):
    result = {}
    pattern = r'CREATE FUNCTION ([a-z_][a-z_0-9]*\.[a-z_][a-z_0-9]*)\(\)\s+RETURNS\b[^;]*?\bAS\s+(\$[a-z_0-9]*\$)(.*?)\2;'
    for match in re.finditer(pattern, application, re.S):
        require(match[1] not in result, "DUPLICATE_SOURCE_FUNCTION")
        result[match[1]] = match[3]
    return result


def expected_frame(case, bodies):
    intended = case["intended_diagnostic"]
    if not intended or not intended["required_source_function"]: return None
    name = intended["required_source_function"]
    require(name in bodies, "EXPECTED_SOURCE_FRAME_UNAVAILABLE")
    body = bodies[name]
    if intended["sqlstate"] == "P0002":
        require(case["variation"] in ("missing-evidence", "missing-history") and name == "platform_private.customer_atomic", "P0002_SOURCE_OBLIGATION_UNREGISTERED")
        variable = "e" if case["variation"] == "missing-evidence" else "h"
        matches = [index for index, line in enumerate(body.split("\n"), 1) if re.search(r'\bSELECT \* INTO STRICT ' + variable + r' FROM\b', line)]
        operation = "SQL statement"
    else:
        message = "RAISE EXCEPTION " + quote(intended["exact_source_message"])
        matches = [index for index, line in enumerate(body.split("\n"), 1) if message in line]
        operation = "RAISE"
    require(len(matches) == 1, "EXPECTED_SOURCE_FRAME_AMBIGUOUS")
    return {"function": name, "body_line": matches[0], "operation": operation, "body_sha256": sha(body.encode("utf8"))}


def diagnostic(stderr, case, bodies):
    stderr = stderr.replace("\r\n", "\n")
    format_valid = all(character in "\n\t" or unicodedata.category(character) not in ("Cc", "Cf", "Cs", "Zl", "Zp") for character in stderr)
    headers = [match for line in stderr.splitlines() if (match := HEADER.fullmatch(line))]
    header_candidates = sum(bool(re.match(r'(?:psql:[^\n]*?: )?(?:ERROR|FATAL|WARNING|PANIC):', line)) for line in stderr.splitlines())
    frames, malformed = [], False
    for line in stderr.splitlines():
        if "PL/pgSQL function " not in line: continue
        match = FRAME.fullmatch(line)
        if not match: malformed = True
        else: frames.append({"function": match[1], "body_line": int(match[2]), "operation": match[3]})
    intended = case["intended_diagnostic"]
    expected = expected_frame(case, bodies)
    state = headers[0][1] if len(headers) == 1 and headers[0][1] in STATES else None
    matched = False
    if intended is None:
        matched = not stderr.strip()
    elif len(headers) == 1 and state == intended["sqlstate"]:
        if intended["source_constraint"]:
            constraint = intended["source_constraint"]
            if state == "23505": message = 'duplicate key value violates unique constraint "' + constraint + '"'
            else:
                table = "runtime_command_receipt" if constraint in ("result_json_boundary", "result_version_registered") else "owner_mutation_evidence"
                message = 'new row for relation "' + table + '" violates check constraint "' + constraint + '"'
        else: message = intended["exact_source_message"]
        matched = headers[0][2] == message
    format_valid = format_valid and header_candidates == len(headers)
    frame_verified = not malformed and (frames == [{key: expected[key] for key in ("function", "body_line", "operation")}] if expected else not frames)
    return {"sqlstate": state, "classification": "EXPECTED_SOURCE_DIAGNOSTIC" if matched and frame_verified and format_valid else "UNLISTED_OR_INCOMPLETE_DISCARDED",
            "single_error_header": len(headers) == 1, "diagnostic_format_valid": format_valid, "source_frame_verified": frame_verified,
            "source_frame": expected if expected and frame_verified else None,
            "matched": matched and frame_verified and format_valid}


class Evidence:
    def __init__(self, directory, packet):
        directory.mkdir(parents=True, exist_ok=False)
        self.path = directory / "customer-control-results.json"
        self.value = {"schema": "workinants.customer-control-evidence.v1", "status": "IN_PROGRESS", "current_stage": "ENTRY", "current_case": None, "current": {}, "results": [], "authentication": [], "transactions": {}, "cleanup_required": True, "subsequent_cases_stopped": False,
                      "reviewed_packet_sha256": PACKET_SHA256, "selected_controls": [{"id": value, "status": "NOT_RUN"} for value in packet["selected_control_ids"]],
                      "blocked_plans": [{"name": packet[key]["name"], "status": "NOT_RUN", "execution_dependencies": packet[key]["execution_dependencies"]} for key in ("update_plan", "cas_plan")]}
        with self.path.open("x", encoding="utf8", newline="\n") as file: file.write(json.dumps(self.value, indent=2) + "\n")

    def save(self):
        temporary = self.path.with_suffix(".json.tmp")
        with temporary.open("w", encoding="utf8", newline="\n") as file:
            file.write(json.dumps(self.value, indent=2) + "\n"); file.flush(); os.fsync(file.fileno())
        temporary.replace(self.path)

    def stage(self, name): self.value["current_stage"] = name; self.save()


class Session:
    def __init__(self, role, container, run):
        require(role in ROLES and re.fullmatch(r"[0-9a-f]{64}", container), "EXACT_RUNTIME_SESSION_IDENTITY")
        self.role, self.container, self.run = role, container, run
        self.backend = None; self.lines = queue.Queue(maxsize=256); self.errors = []; self.invalid = threading.Event()
        self.process = subprocess.Popen(API["psql"](role, container), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        def output():
            try:
                while line := self.process.stdout.readline(65537):
                    if len(line) > 65536: self.invalid.set(); continue
                    try: self.lines.put_nowait(line.removesuffix("\n").removesuffix("\r"))
                    except queue.Full: self.invalid.set()
            except Exception: self.invalid.set()
        def errors():
            size = 0
            try:
                while chunk := self.process.stderr.read(65536):
                    size += len(chunk)
                    if size <= 1048576: self.errors.append(chunk)
                    else: self.invalid.set()
            except Exception: self.invalid.set()
        self.readers = [threading.Thread(target=output, daemon=True), threading.Thread(target=errors, daemon=True)]
        for reader in self.readers: reader.start()

    def send(self, text): self.process.stdin.write(text); self.process.stdin.flush()

    def capture(self):
        self.send("BEGIN ISOLATION LEVEL READ COMMITTED; SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='1s'; SET LOCAL idle_in_transaction_session_timeout='30s'; SELECT " + quote(TUPLE_PREFIX) + "||jsonb_build_object('login',session_user,'pid',pg_backend_pid()::text,'xid',pg_current_xact_id()::text,'started',(SELECT backend_start::text FROM pg_stat_activity WHERE pid=pg_backend_pid()))::text;\n")
        line = self.lines.get(timeout=15)
        require(line.startswith(TUPLE_PREFIX), "RUNTIME_TUPLE_INVALID")
        captured = unique_json(line.removeprefix(TUPLE_PREFIX))
        require(type(captured) is dict and set(captured) == {"login", "pid", "xid", "started"} and captured["login"] == self.role and
                all(type(captured[key]) is str for key in ("pid", "xid", "started")) and
                re.fullmatch(r"[0-9]+", captured["pid"]) and re.fullmatch(r"[0-9]+", captured["xid"]) and re.fullmatch(r"[0-9T:+. \-]+", captured["started"]), "RUNTIME_TUPLE_INVALID")
        self.backend = captured
        return captured

    def finish(self, text):
        self.send(text + "\nSELECT " + quote(ACK) + ";\n\\q\n")
        self.process.stdin.close()
        code = self.process.wait(timeout=45)
        for reader in self.readers: reader.join(timeout=5)
        require(not self.invalid.is_set() and not any(reader.is_alive() for reader in self.readers), "OPERATION_OUTPUT_INCOMPLETE")
        lines = []
        while not self.lines.empty():
            line = self.lines.get_nowait()
            if line: lines.append(line)
        return code, lines, "".join(self.errors)

    def close(self):
        if self.process.poll() is None:
            try:
                if not self.process.stdin.closed:
                    self.process.stdin.write("ROLLBACK;\n\\q\n"); self.process.stdin.close()
                self.process.wait(timeout=10)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                self.process.terminate()
                try: self.process.wait(timeout=10)
                except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(timeout=10)
        require(self.process.poll() is not None and self.backend is not None, "OPERATION_CLOSURE_UNCONFIRMED")
        backend = self.backend
        check = "SELECT count(*) FROM pg_stat_activity WHERE pid=" + backend["pid"] + " AND backend_start=" + quote(backend["started"]) + "::timestamptz AND usename=" + quote(self.role) + " AND datname='wa_p0c_rehearsal';"
        require(self.run("postgres", check) == "0", "OPERATION_BACKEND_STILL_LIVE")


class Runtime:
    def __init__(self, container): self.container = container
    def run(self, role, text): return API["run"](role, text, self.container)
    def session(self, role): return Session(role, self.container, self.run)


def restore_observation(packet, runtime, evidence):
    contract = packet["trusted_setup_trigger_contract"]
    actual = unique_json(runtime.run("postgres", packet_sql(packet, contract["observer_sql"])))
    expected = contract["observer_expected"]
    exact = type(actual) is dict and set(actual) == set(expected) and all(type(actual[key]) is type(expected[key]) and actual[key] == expected[key] for key in expected)
    evidence.value["trigger_restoration_verified"] = exact; evidence.save()
    require(exact, "TRIGGER_RESTORATION_NOT_PROVEN")


def native_observation(snapshot, runtime, evidence):
    expected = evidence.value.get("source_modules_sha256", {}).get(COLLECTOR)
    current = unique_json(runtime.run("postgres", verified_sql_text(ROOT / COLLECTOR, expected)))
    exact = sha(canonical(current).encode("utf8")) == sha(canonical(snapshot).encode("utf8"))
    evidence.value["native_catalog_unchanged"] = exact; evidence.save()
    require(exact, "NATIVE_CATALOG_DRIFT")


def captured_transaction_tail(text):
    """The captured session already began; remove only the pinned outer BEGIN.

    Trusted setup and the legacy issuer adapter each have exactly one outer
    BEGIN/COMMIT. The business SQL and its final COMMIT bytes remain unchanged.
    Sending BEGIN twice would produce a warning and obscure the commit verdict.
    """
    match = re.match(r'\A(?P<comments>(?:\s|--[^\n]*\n)*)BEGIN\s*;', text)
    require(match is not None and re.search(r'\bCOMMIT;\s*\Z', text) is not None, "OUTER_TRANSACTION_WRAPPER_REQUIRED")
    require(len(re.findall(r'\b(?:BEGIN|COMMIT|ROLLBACK)\s*;', text)) == 2, "TRANSACTION_WRAPPER_AMBIGUOUS")
    return match["comments"] + text[match.end():]


def committed_transaction(role, text, runtime, evidence, key):
    text = captured_transaction_tail(text)
    record = {"role": role, "operation_closed": False, "commit_acknowledged": False}
    evidence.value["transactions"][key] = record; evidence.save()
    session = runtime.session(role)
    try:
        session.capture()
        code, lines, stderr = session.finish(text)
        record.update(exit_code=code, commit_ack_count=min(lines.count(ACK), 2), stderr_empty=not stderr.strip(),
                      unexpected_stdout=any(line != ACK for line in lines), commit_acknowledged=code == 0 and lines == [ACK] and not stderr.strip()); evidence.save()
        require(code == 0 and lines == [ACK] and not stderr.strip(), "PRIVILEGED_OR_ISSUER_COMMIT_NOT_PROVEN")
    finally:
        session.close()
        record["operation_closed"] = True; evidence.save()


def execute_case(case, packet, bodies, runtime, evidence):
    evidence.value.update(current_case=case["name"], current={"operation_closed": False, "authenticated_login": None, "stage_markers": [], "issuer_committed": False,
                          "expected_failure_stage": case["stage_marker_oracle"]["expected_failure_stage"], "expected_failure_timing": case["stage_marker_oracle"]["expected_failure_timing"]})
    evidence.stage("OPEN_APP_OPERATION")
    app = runtime.session("wa_app_runtime")
    failure = None
    try:
        backend = app.capture()
        evidence.value["current"]["authenticated_login"] = "wa_app_runtime"
        evidence.stage("ISSUE_SEPARATE_GRANT")
        grant = case["grant"]
        require(grant["action"] == "SH-004.v1" and grant["purpose"] == "provision" and grant["owner_module_id"] == "customer_buyer_profile" and grant["target_kind"] == "CustomerProfile" and grant["source_generation"] == "0" and grant["target_id"] == case["ids"]["CustomerProfile"], "UNSUPPORTED_CUSTOMER_GRANT")
        secret = secrets.token_hex(32)
        legacy = {"grant_id": grant["id"], "principal_user_id": grant["principal_user_id"], "allowed_fields": grant["allowed_fields"], "ids": case["ids"]}
        statement = API["grant_sql"](legacy, backend["login"], backend["pid"], backend["xid"], sha(bytes.fromhex(secret)))
        committed_transaction("wa_context_issuer", statement, runtime, evidence, case["name"] + "/issuer")
        evidence.value["current"]["issuer_committed"] = True; evidence.save()
        evidence.stage("PROTECTED_BEHAVIOR")
        code, lines, stderr = app.finish("SELECT platform_private.bind_request_context(" + quote(secret) + ");\n" + packet_sql(packet, case["transaction_sql"]))
        oracle = case["stage_marker_oracle"]
        permitted = set(oracle["expected_completed_markers"] + oracle["forbidden_markers"] + [ACK])
        safe_lines = [line for line in lines if line in permitted]
        evidence.value["current"].update(exit_code=code, stage_markers=[line for line in safe_lines if line != ACK], commit_acknowledged=safe_lines.count(ACK) == 1, commit_ack_count=min(safe_lines.count(ACK), 2),
                                         unexpected_stdout=any(line not in permitted for line in lines), diagnostic=diagnostic(stderr, case, bodies))
        evidence.save()
    except (Exception, KeyboardInterrupt) as error:
        failure = error
        evidence.value["current"]["failed_stage"] = evidence.value["current_stage"]; evidence.save()
    finally:
        evidence.stage("CLOSE_APP_OPERATION")
        app.close()
        evidence.value["current"]["operation_closed"] = True; evidence.save()
    evidence.stage("VERIFY_TRIGGER_RESTORATION")
    restore_observation(packet, runtime, evidence)
    if failure is not None: raise failure
    evidence.stage("OBSERVE_COMPLETE_GROUP")
    actual = unique_json(runtime.run("postgres", packet_sql(packet, case["observer_sql"])))
    expected = case["observer_expected"]
    require(type(actual) is dict and set(actual) == set(expected) and all(type(actual[key]) is type(expected[key]) for key in expected), "OBSERVER_SHAPE_INVALID")
    evidence.value["current"]["counts"] = actual; evidence.save()
    current = evidence.value["current"]
    evidence.stage("CHECK_SOURCE_STAGE_AND_GROUP_VERDICT")
    require(not current["unexpected_stdout"] and current["stage_markers"] == case["stage_marker_oracle"]["expected_completed_markers"], "INTENDED_STAGE_NOT_PROVEN")
    require(current["exit_code"] == (0 if case["expected_commit"] else 3) and current["commit_ack_count"] == (1 if case["expected_commit"] else 0), "SCENARIO_COMMIT_OUTCOME_UNEXPECTED")
    require(current["diagnostic"]["matched"], "INTENDED_SOURCE_DIAGNOSTIC_NOT_PROVEN")
    require(actual == expected, "FULL_GROUP_STATE_MISMATCH")
    evidence.value["results"].append({"name": case["name"], "status": "PASS_SCENARIO_ONLY_NOT_SELECTED_CONTROL", **current})
    evidence.stage("SCENARIO_COMPLETE")


def resource_identity(target, process=subprocess.run):
    context = HOST["docker_json"](["context", "inspect", "desktop-linux"], process)
    container = HOST["docker_json"](["inspect", target["target"]["container_name"]], process)
    volume = HOST["docker_json"](["volume", "inspect", target["target"]["volume_name"]], process)
    observed = HOST["inspect_live"](target, context, container, volume)
    image = HOST["docker_json"](["image", "inspect", target["target"]["image"]], process)
    HOST["verify_image"](target, container, image)
    return observed["container_id"]


def fresh_fixture_sql(packet):
    """Source-pinned IDs only; observe all synthetic identities and case rows.

    No setup is attempted over a prior run, even when the reviewed catalog has
    the same shape. The query exports one Boolean and never existing row data.
    """
    setup = packet_sql(packet, "trusted-identity-fixtures.sql")
    identities = re.findall(r'INSERT INTO (app\.users|app\.user_security_profiles) \("id",[^\n]*?VALUES \(\'([0-9a-f-]{36})\'', setup)
    require(len(identities) == setup.count("INSERT INTO ") and identities, "FIXTURE_IDENTITY_SOURCE_SHAPE")
    rows = {}
    for table, identity in identities: rows.setdefault(table, set()).add(identity)
    tables = {"CustomerProfile": "app.customer_profiles", "RuntimeCommandReceipt": "platform.runtime_command_receipt",
              "duplicate": "platform.runtime_command_receipt", "CustomerProfileLifecycleEvent": "app.customer_profile_lifecycle_event",
              "OwnerMutationEvidence": "platform.owner_mutation_evidence", "event": "platform.runtime_outbox_message",
              "free": "platform.runtime_outbox_message", "extra": "platform.runtime_outbox_message", "grant": "platform.database_action_grant"}
    for case in packet["cases"]:
        for field, table in tables.items():
            identity = case["ids"][field]
            require(type(identity) is str and re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", identity), "FIXTURE_ID_SOURCE_SHAPE")
            rows.setdefault(table, set()).add(identity)
    return "SELECT " + " AND ".join("NOT EXISTS(SELECT 1 FROM " + table + " WHERE id=ANY(ARRAY[" + ",".join(quote(identity) for identity in sorted(ids)) + "]::uuid[]))" for table, ids in sorted(rows.items())) + ";"


def run_subset(packet, snapshot, cases, runtime, evidence):
    evidence.stage("SERVER_PREFLIGHT")
    require(runtime.run("postgres", "SELECT current_setting('server_version_num')::integer=170011 AND current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('password_encryption')='scram-sha-256';") == "t", "SERVER_SETTINGS_NOT_PROVEN")
    evidence.stage("AUTHENTICATION_PREFLIGHT")
    API["authentication_preflight"](evidence, runtime.container)
    evidence.stage("FINALIZATION_PREFLIGHT")
    require(runtime.run("postgres", "SELECT NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member='wa_schema_owner'::regrole AND roleid=ANY(ARRAY['wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole])) AND NOT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') AND NOT has_schema_privilege('wa_customer_verifier','platform_private','CREATE') AND NOT has_schema_privilege('wa_track_verifier','platform_private','CREATE');") == "t", "FINALIZATION_NOT_PROVEN")
    native_observation(snapshot, runtime, evidence)
    restore_observation(packet, runtime, evidence)
    evidence.stage("FRESH_SYNTHETIC_IDS_PREFLIGHT")
    fresh = runtime.run("postgres", fresh_fixture_sql(packet)) == "t"
    evidence.value["fresh_synthetic_ids_verified"] = fresh; evidence.save()
    require(fresh, "SYNTHETIC_IDS_ALREADY_PRESENT")
    evidence.stage("TRUSTED_FIXTURE_SETUP")
    try: committed_transaction("postgres", packet_sql(packet, "trusted-identity-fixtures.sql"), runtime, evidence, "trusted-identity-setup")
    finally:
        if evidence.value["transactions"].get("trusted-identity-setup", {}).get("operation_closed") is True:
            evidence.stage("VERIFY_SETUP_RESTORATION")
            restore_observation(packet, runtime, evidence)
    for case in cases: execute_case(case, packet, function_bodies(application_sql(packet)), runtime, evidence)
    native_observation(snapshot, runtime, evidence)
    evidence.value.update(status="PASS_PREPARED_CREATE_SUBSET_ONLY_CONTROLS_NOT_RUN", current_stage="COMPLETE")
    evidence.save()


def main(argv=None, dependencies=None):
    dependencies = dependencies or {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-reviewed-customer-controls", action="store_true")
    parser.add_argument("--reviewed-run-plan", type=Path)
    parser.add_argument("--evidence-directory", type=Path)
    args = parser.parse_args(argv)
    evidence = None
    try:
        require(args.execute_reviewed_customer_controls and args.reviewed_run_plan is not None and args.evidence_directory is not None, "EXPLICIT_REVIEWED_EXECUTION_REQUIRED")
        plan_raw = external_file(str(args.reviewed_run_plan)).read_bytes()
        plan = unique_json(plan_raw.decode("utf8"))
        packet, snapshot, cases = (dependencies.get("load_inputs") or load_inputs)(plan)
        directory = external_file(str(args.evidence_directory))
        require(not directory.exists(), "FRESH_EXTERNAL_EVIDENCE_DIRECTORY_REQUIRED")
        evidence = (dependencies.get("evidence") or Evidence)(directory, packet)
        evidence.value.update(reviewed_run_plan_sha256=sha(plan_raw), source_modules_sha256=plan["source_modules_sha256"], approved_scenario_names=plan["scenario_names"], reviewed_native_snapshot_sha256=plan["native_snapshot"]["sha256"], reviewed_native_comparison_sha256=plan["native_comparison"]["sha256"]); evidence.save()
        evidence.stage("RESOURCE_PREFLIGHT")
        container = (dependencies.get("resource_identity") or resource_identity)(plan["target_manifest"])
        require(re.fullmatch(r"[0-9a-f]{64}", container), "IMMUTABLE_CONTAINER_ID_REQUIRED")
        evidence.value["container_id"] = container; evidence.save()
        runtime = (dependencies.get("runtime") or Runtime)(container)
        (dependencies.get("run_subset") or run_subset)(packet, snapshot, cases, runtime, evidence)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        code = failure_code(error)
        if evidence is not None:
            failure = {"code": code, "stage": evidence.value["current_stage"]}
            if evidence.value.get("current", {}).get("failed_stage"):
                failure["operation_failure_stage"] = evidence.value["current"]["failed_stage"]
            evidence.value.update(status="STOPPED_RETAINED_FOR_CONTROLLED_CLEANUP", subsequent_cases_stopped=True, failure=failure)
            evidence.save()
        print(json.dumps({"schema": "workinants.customer-control-summary.v1", "status": "REFUSED_OR_STOPPED", "code": code, "raw_output_discarded": True}))
        return 1


if __name__ == "__main__": raise SystemExit(main())
