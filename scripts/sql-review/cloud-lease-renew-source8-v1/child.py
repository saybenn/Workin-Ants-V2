"""Finite lease proof within a live reviewed source8 owner."""

import ast
from copy import deepcopy
import datetime
import hashlib
import json
import re
import secrets
import subprocess
import time
import uuid

import prepare as source


PIPE = f"{source.APP}/host_session.py"
APP_CHILD = f"{source.APP}/app_child.py"
WORKER_CHILD = f"{source.WORKER}/worker_child.py"
CONTEXT = "scripts/sql-review/run-context-control-rehearsal.py"
ROLES = ("postgres", "wa_context_issuer", "wa_identity_service_authority", "wa_app_runtime", "wa_worker")
AUTH_FIELDS = {"json_parsed", "object", "fields", "string_fields", "login", "scram_identity", "database",
               "client_loopback", "server_loopback"}
PASS = "PASS_ONE_LIVE_LEASE_EXTENSION_AND_TWO_DENIALS_ONLY"
STOP = "STOPPED_OR_UNCONFIRMED"
STAGE = "LEASE_RENEW_SOURCE8"
LEAF = "lease-renew-results.json"
SCHEMA = "workinants.cloud-lease-renew-source8-result.v1"
GLOBAL = "SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid();"
TRIGGERS = {"actual": 100, "enabled": True, "exact": True, "expected": 100}
EXPECTED_SETUP = {
    "app.users": 1, "app.user_security_profiles": 1, "app.customer_profiles": 1,
    "app.customer_profile_lifecycle_event": 1, "platform.owner_mutation_evidence": 1,
    "platform.runtime_command_receipt": 1, "platform.runtime_outbox_message": 2, "platform.runtime_work_item": 1,
    "platform_private.identity_service_authorization": 1, "platform_private.identity_service_receipt": 1,
}
FAILURE_CODES = frozenset({
    "LEASE_RENEW_CHILD_UNCONFIRMED", "LEASE_RENEW_RECIPE_DRIFT", "LEASE_RENEW_FRESH_TARGET", "LEASE_RENEW_ROLE_SCOPE",
    "LEASE_RENEW_EVIDENCE_UNCONFIRMED", "LEASE_RENEW_SECRET_EVIDENCE", "LEASE_RENEW_AUTH", "LEASE_RENEW_LIVE_WINDOW",
    "LEASE_RENEW_CONTEXT", "LEASE_RENEW_PRIVILEGED_SETUP", "LEASE_RENEW_CLIENT_CLOSURE", "LEASE_RENEW_ORIGINAL_CASE_UNCONFIRMED",
    "LEASE_RENEW_ISSUER_RETENTION", "LEASE_RENEW_ALL_TRIGGER_PARITY", "LEASE_RENEW_SETUP_OBSERVATION",
    "LEASE_RENEW_STATE_OBSERVATION", "LEASE_RENEW_POSITIVE_DELTA", "LEASE_RENEW_NEGATIVE_RESIDUE", "WORKER_TRANSPORT_UNCERTAIN",
    "LEASE_RENEW_PRE_ACTION_ROUTE_UNCONFIRMED",
    "LEASE_RENEW_UNCHANGED_NATIVE_UNCONFIRMED", "LEASE_RENEW_CLAIM_DELTA_UNCONFIRMED",
    "WORKER_SOCKET_IDENTITY", "WORKER_CURRENT_TARGET_REQUIRED", "WORKER_RESTRICTED_LOGIN_SCOPE",
    "WORKER_RAW_SQL_UNCONFIRMED", "WORKER_EXACT_BACKEND_STILL_LIVE", "SEPARATE_ISSUER_COMMIT_UNCONFIRMED",
    "ISSUER_CREATED_AT_RETURN_REQUIRED", "ISSUER_CREATED_AT_RETURN_REJECTED", "ISSUER_CREATED_AT_TIMESTAMP_REQUIRED",
    "ISSUER_TERMINAL_EXIT_UNEXPECTED", "FINITE_CAPABILITIES_REQUIRED", "ONE_GRANT_PRINCIPAL_REQUIRED",
})


def quote(value):
    return "'" + value.replace("'", "''") + "'"


def select(nodes, names):
    result = [node for node in nodes if getattr(node, "name", None) in names]
    source.require(len(result) == len(names) and {node.name for node in result} == names, "LEASE_RENEW_REVIEWED_ADAPTER_SURFACE")
    return result


def compile_slice(nodes, label, namespace):
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, label, "exec", dont_inherit=True), namespace)


def shared_transport(owner, evidence):
    blobs = owner.blobs
    for path in (PIPE, APP_CHILD, WORKER_CHILD, CONTEXT):
        source.require(source.sha(blobs[path]) == source.PINS[path], "LEASE_RENEW_REVIEWED_PIPE_DRIFT")
    worker_nodes = ast.parse(blobs[WORKER_CHILD], filename=WORKER_CHILD).body
    scoped = dict(ast=ast, deepcopy=deepcopy, datetime=datetime, hashlib=hashlib, json=json, re=re, secrets=secrets,
                  uuid=uuid, subprocess=subprocess, owner=owner, ROLES=ROLES, PIPE=PIPE, PINS=source.PINS, CONTEXT=CONTEXT)
    compile_slice(select(worker_nodes, {"Hold", "require", "pipe_class"}), WORKER_CHILD, scoped)
    pipe, session_stop = scoped["pipe_class"](blobs)
    app_nodes = ast.parse(blobs[APP_CHILD], filename=APP_CHILD).body
    compile_slice(select(app_nodes, {"execute_ast", "exact_nodes", "render_context"}), APP_CHILD, scoped)
    context = scoped["render_context"](blobs, evidence.code, lambda *private: owner.program.all_secrets.extend(private))
    entry = select(worker_nodes, {"coordinate"})[0]
    endpoint = select(entry.body, {"CloudContext"})[0]
    endpoint.bases = []
    endpoint.body = select(endpoint.body, {"socket_checked", "psql", "spawn", "raw", "require_backend_absent"})
    scoped.update(runtime={"quote": context["quote"]}, context=context, prepare=source,
                  admit_slot=lambda driver, role: driver.admit_slot(role))
    compile_slice([*select(entry.body, {"socket_checked", "psql", "read_only"}), endpoint], WORKER_CHILD, scoped)
    return pipe, session_stop, scoped["CloudContext"], context


class Evidence:
    def __init__(self, owner, packet, native):
        self.owner = owner
        self.p = owner.program
        self.outer = owner.report["lease_renew"]
        self.value = {
            "schema": SCHEMA, "status": "IN_PROGRESS", "stage": "ENTRY", "first_failure": None,
            "run_id": owner.operation["run_id"], "fixture_run_id": packet["fixture_run_id"],
            "source": owner.operation["source"], "packet_sha256": source.sha(owner.raw),
            "recipe_sha256": source.sha(source.canonical(packet)), "native_baseline_sha256": self.p.digest(native),
            "container_id": owner.resources.cid, "volume_created_at": owner.resources.volume_birth,
            "operations": [], "results": [], "posture": "D", "assertion_promotions": 0,
            "complete_final_client_closure": False, "evidence_complete": True,
        }

    def code(self, error):
        try:
            code = getattr(error, "code", None) or (error.args[0] if type(error) is ValueError else None)
        except BaseException:
            code = None
        return code if type(code) is str and code in FAILURE_CODES else "LEASE_RENEW_CHILD_UNCONFIRMED"

    def stop(self, code):
        self.value["status"] = STOP
        if self.value["first_failure"] is None:
            self.value["first_failure"] = {"stage": self.value["stage"], "code": code}
            self.p.record_failure(STAGE, code)

    def save(self):
        raw = source.canonical(self.value)
        if len(raw) > 256 * 1024 or any(value.encode() in raw for value in self.p.all_secrets):
            self.outer.pop("child_trace", None)
            self.value["evidence_complete"] = False
            self.stop("LEASE_RENEW_SECRET_EVIDENCE")
            raise ValueError("LEASE_RENEW_SECRET_EVIDENCE")
        try:
            self.outer["child_trace"] = self.value
            self.p.save()
        except BaseException:
            self.value["evidence_complete"] = False
            self.stop("LEASE_RENEW_EVIDENCE_UNCONFIRMED")
            raise ValueError("LEASE_RENEW_EVIDENCE_UNCONFIRMED") from None

    def stage(self, value):
        self.value["stage"] = value
        self.save()

    def finish(self):
        self.save()
        try:
            reference = self.p.write_safe(LEAF, self.value)
        except BaseException:
            self.value["evidence_complete"] = False
            self.stop("LEASE_RENEW_EVIDENCE_UNCONFIRMED")
            raise ValueError("LEASE_RENEW_EVIDENCE_UNCONFIRMED") from None
        self.outer.pop("child_trace")
        return reference, self.value


def state_shape(rows, tables):
    return type(rows) is list and len(rows) == len(tables) == 42 and all(
        type(row) is dict and set(row) == {"table", "count", "sha256"} and row["table"] == table
        and type(row["count"]) is int and row["count"] >= 0 and type(row["sha256"]) is str and source.HASH.fullmatch(row["sha256"])
        for row, table in zip(rows, tables, strict=True)
    )


def scoped_delta(before, after):
    return all((old["count"] == new["count"] == 1 and old["sha256"] != new["sha256"])
               if old["table"] == "platform.runtime_work_item" else old == new
               for old, new in zip(before, after, strict=True))


class Runner:
    def __init__(self, owner, native, packet, assets, evidence, context, session_type, clock):
        self.owner, self.native, self.recipe, self.assets = owner, native, packet, assets
        self.evidence, self.context, self.session_type, self.clock = evidence, context, session_type, clock
        self.packet = {"finite_caps": {"grant_instances_max": 6}}
        self.sequence, self.instances, self.sessions = 0, {}, []
        self.window = None
        self.identity = packet["identity"]
        self.secret = secrets.token_hex(32)
        self.lease_hash = source.sha(bytes.fromhex(self.secret))
        self.owner.program.all_secrets.extend((self.secret, self.lease_hash))

    def text(self, leaf):
        raw = self.assets[leaf]
        source.require(source.sha(raw.encode()) == self.recipe["asset_sha256"][leaf], "LEASE_RENEW_RECIPE_DRIFT")
        return raw

    def admit_slot(self, role):
        open_roles = [session.role for session in self.sessions if not session.closed]
        if role == "wa_context_issuer":
            admitted = open_roles in (["wa_app_runtime"], ["wa_worker"])
        else:
            admitted = (not open_roles and role in ROLES and
                        (role != "postgres" or self.evidence.value["stage"] == "IDENTITY_SEED") and
                        (role != "wa_identity_service_authority" or self.evidence.value["stage"] == "SERVICE_BOOTSTRAP"))
        source.require(admitted and not self.owner.transport.unknown, "LEASE_RENEW_ROLE_SCOPE")

    def session(self, role):
        self.admit_slot(role)
        actual = self.session_type(role, self)
        self.sessions.append(actual)
        return actual

    def uncertain(self, code):
        self.owner.transport.unknown = self.owner.docker.remote_unknown = True
        self.evidence.stop(code if code in FAILURE_CODES else "WORKER_TRANSPORT_UNCERTAIN")

    def closure(self):
        source.require(all(value.closed is True for value in self.sessions) and self.raw("postgres", GLOBAL) == "0",
                       "LEASE_RENEW_CLIENT_CLOSURE")
        self.record({"stage": "GLOBAL_CLOSURE", "all_other_clients_absent": True})

    def deadline(self):
        source.require(self.window is None or self.clock() < self.window, "LEASE_RENEW_LIVE_WINDOW")

    def closed_reply(self, role, leaf, *, template=None, case=None, preimage=None, fence=None, commit_marker=None):
        session = self.session(role)
        expected_exit = 0
        verdict = None
        try:
            session.begin("read committed")
            backend = session.capture()
            text = self.text(leaf)
            if template is not None:
                grant = self.recipe["grant_templates"][template]
                key = self.issue(grant, backend)
                item = self.instances[key]
                source.require(session.capture() == backend == item["backend"], "LEASE_RENEW_CONTEXT")
                rows, ack, stderr = session.call("SELECT platform_private.bind_request_context(" + quote(item["secret"]) + ");")
                source.require(rows == [] and ack is True and stderr == "", "LEASE_RENEW_CONTEXT")
            if preimage is not None:
                source.require(role == "wa_worker" and source.HASH.fullmatch(preimage) and fence in (0, 1), "LEASE_RENEW_ROLE_SCOPE")
                rows, ack, stderr = session.call(f"SET LOCAL wa.lease_secret='{preimage}'; SET LOCAL wa.fence='{fence}';")
                source.require(rows == [] and ack is True and stderr == "", "LEASE_RENEW_CONTEXT")
                self.deadline()
            if template == "renew-1":
                preflight = source.work_observer_sql(self.text("restricted-renew-preflight.sql"), self.lease_hash)
                rows, ack, stderr = session.call(preflight)
                expected = {"visible_work": 1, "exact_route": True, "minimum_server_reserve": True,
                            "matches_preimage": case != "copied-hash-renew-denied"}
                valid = len(rows) == 1 and ack is True and stderr == "" and source.canonical(json.loads(rows[0])) == source.canonical(expected)
                self.record({"stage": "RESTRICTED_LIVE_RENEW_SCOPE", "case": case, "exact_compared_to_step": valid})
                source.require(valid, "LEASE_RENEW_PRE_ACTION_ROUTE_UNCONFIRMED")
                self.deadline()
            if role in ("postgres", "wa_identity_service_authority"):
                wrapper = re.match(r"\A(?:(?:\s|--[^\n]*\n)*)BEGIN;", text)
                source.require(wrapper is not None and text.rstrip().endswith("COMMIT;"), "LEASE_RENEW_PRIVILEGED_SETUP")
                text = text[wrapper.end():]
            if case == "worker-claim":
                self.window = self.clock() + 12
            if case == "current-holder-renew":
                self.renewed_window = self.clock() + 90
            rows, ack, stderr = session.call(text)
            if case in source.DENIALS:
                verdict = source.diagnostic_receipt(case, session.process.poll(), rows, ack, stderr)
                expected_exit = 3 if verdict["exact_denial"] else 0
                source.require(verdict["exact_denial"], "LEASE_RENEW_ORIGINAL_CASE_UNCONFIRMED")
            elif case in source.CASES:
                verdict = source.commit_receipt(case, 0, rows, ack, stderr)
                source.require(verdict["exact_committed_work_change"], "LEASE_RENEW_ORIGINAL_CASE_UNCONFIRMED")
            else:
                expected_rows = [] if commit_marker is None else [commit_marker]
                source.require(rows == expected_rows and ack is True and stderr == "", "LEASE_RENEW_SETUP_OBSERVATION")
        except BaseException as error:
            self.evidence.stop(self.evidence.code(error))
            raise
        finally:
            try:
                code = session.close()
                source.require(session.closed is True and type(code) is int and code in (0, 3), "LEASE_RENEW_CLIENT_CLOSURE")
            except BaseException as error:
                self.uncertain(self.evidence.code(error))
                raise
        source.require(code == expected_exit, "LEASE_RENEW_ORIGINAL_CASE_UNCONFIRMED")
        self.record({"stage": "CLOSED_SQL", "leaf": leaf, "role": role, "exact_backend_absence": True,
                     "mode": "DENIED" if expected_exit == 3 else "COMMITTED"})
        return backend["xid"], verdict

    def auth(self):
        pairs = {row["role"]: row for row in self.owner.report["authentication"] if row["correct_password"] == "PASS_SCRAM"}
        checks = {row["role"]: row["checks"] for row in self.owner.report["auth_comparisons"]}
        source.require(all(role in pairs and pairs[role] == {"role": role, "correct_password": "PASS_SCRAM",
                       "wrong_password": "PASS_REJECTED", "actual_connection_closed": True} and role in checks
                       and set(checks[role]) == AUTH_FIELDS and all(flag is True for flag in checks[role].values())
                       for role in ROLES), "LEASE_RENEW_AUTH")
        self.record({"stage": "CURRENT_ROLE_AUTH", "correct_wrong_pairs": len(ROLES), "exact": True})

    def observe(self, sql, expected, code="LEASE_RENEW_SETUP_OBSERVATION"):
        actual = json.loads(self.raw("postgres", sql))
        source.require(source.canonical(actual) == source.canonical(expected), code)

    def all_triggers(self):
        self.observe(self.text("all100-trigger-observe.sql"), TRIGGERS, "LEASE_RENEW_ALL_TRIGGER_PARITY")
        self.record({"stage": "EXACT_TRIGGERS", "verified": 100})

    def native_after_seed(self):
        raw = self.owner.blobs[source.COLLECTOR]
        source.require(source.sha(raw) == self.recipe["source_pins"][source.COLLECTOR], "LEASE_RENEW_RECIPE_DRIFT")
        self.observe(raw.decode(), self.native, "LEASE_RENEW_UNCHANGED_NATIVE_UNCONFIRMED")
        self.record({"stage": "NATIVE_AFTER_IDENTITY_SEED", "unchanged": True})

    def state(self, count):
        ids = tuple(item["id"] for item in self.instances.values())
        source.require(len(ids) == count, "LEASE_RENEW_ISSUER_RETENTION")
        sql = source.full_state_observer_sql(self.text("full42-state-observe.sql"), ids)
        rows = json.loads(self.raw("postgres", sql))
        source.require(state_shape(rows, self.recipe["full42_table_order"]), "LEASE_RENEW_STATE_OBSERVATION")
        return rows

    def retain(self, count):
        source.require(len(self.instances) == count, "LEASE_RENEW_ISSUER_RETENTION")
        joins = []
        for item in self.instances.values():
            values = item["values"]
            checked = " AND ".join(f"g.{name} IS NOT DISTINCT FROM ({values[name]})" for name in self.context["GRANT_COLUMNS"])
            joins.append("SELECT (" + checked + ") AND g.issuer_service=session_user::text AND g.expires_at>clock_timestamp() "
                         "AS exact FROM platform.database_action_grant g WHERE g.id=" + values["id"])
        sql = ("SELECT jsonb_build_object('count',count(*),'exact',coalesce(bool_and(exact),false)) FROM ("
               + " UNION ALL ".join(joins) + ") retained;")
        actual = json.loads(self.raw("wa_context_issuer", sql))
        source.require(source.canonical(actual) == source.canonical({"count": count, "exact": True}), "LEASE_RENEW_ISSUER_RETENTION")
        self.record({"stage": "ISSUER_RETENTION", "grants": count, "fields": 21, "exact": True})

    def setup(self):
        self.auth()
        self.closure()
        self.all_triggers()
        source.require(all(row["count"] == 0 for row in self.state(0)), "LEASE_RENEW_FRESH_TARGET")
        self.evidence.stage("IDENTITY_SEED")
        self.closed_reply("postgres", "identity-seed.sql")
        self.all_triggers()
        self.native_after_seed()
        self.evidence.stage("RESTRICTED_CUSTOMER_SOURCE")
        self.closed_reply("wa_app_runtime", "source-lease.sql", template="source-lease", commit_marker="WA_CUSTOMER_CONTROL_READY_TO_COMMIT")
        self.observe(self.text("source-lease-observe.sql"), self.recipe["expected_restricted_customer_source"])
        self.evidence.stage("RESTRICTED_APP_SCHEDULE")
        xid, _ = self.closed_reply("wa_app_runtime", "schedule-lease.sql", template="schedule-lease", commit_marker="WA_LR_SCHEDULE_READY")
        work, message = self.identity["work_id"], self.identity["outbox_id"]
        sql = ("SELECT jsonb_build_object('exact',count(*)=1) FROM platform.runtime_work_item "
               f"WHERE id='{work}'::uuid AND outbox_message_id='{message}'::uuid AND handler_name='assignDefaultFreeTrack.v1' "
               f"AND state='pending' AND fence=0 AND attempt_count=0 AND mutation_transaction_id='{xid}' "
               "AND lease_token_hash IS NULL AND lease_expires_at IS NULL AND effect_receipt_id IS NULL;")
        self.observe(sql, {"exact": True})
        self.evidence.stage("SERVICE_BOOTSTRAP")
        xid, _ = self.closed_reply("wa_identity_service_authority", "identity-worker-bootstrap.sql")
        service, receipt = self.identity["worker_service"], self.identity["worker_service_receipt"]
        authorization_ref = self.identity["worker_service_authorization_ref"]
        sql = ("SELECT jsonb_build_object('exact',count(*)=1) FROM platform_private.identity_service_authorization a "
               "JOIN platform_private.identity_service_receipt r ON r.id=a.identity_receipt_id AND r.service_principal=a.service_principal "
               f"WHERE a.service_principal='{service}' AND a.identity_receipt_id='{receipt}'::uuid AND a.security_generation=0 "
               f"AND r.security_generation=0 AND r.transition='bootstrap' AND r.mutation_transaction_id='{xid}' "
               f"AND r.identity_authorization_ref='{authorization_ref}' AND r.previous_generation IS NULL AND r.previous_receipt_id IS NULL "
               "AND a.mutation_transaction_id=r.mutation_transaction_id AND a.revoked_at IS NULL AND r.revoked_at IS NULL;")
        self.observe(sql, {"exact": True})
        self.closure()
        self.retain(2)
        baseline = self.state(2)
        source.require(all(row["count"] == EXPECTED_SETUP.get(row["table"], 0) for row in baseline), "LEASE_RENEW_SETUP_OBSERVATION")
        self.record({"stage": "EXACT_RESTRICTED_SETUP_STATE", "tables": 42, "work_rows": 1, "current_service_generation": 0})
        return baseline

    def work_state(self):
        self.deadline()
        sql = source.work_observer_sql(self.text("work-state-observe.sql"), self.lease_hash)
        result = json.loads(self.raw("postgres", sql))
        self.deadline()
        return result

    def run(self):
        try:
            pending = self.setup()
            claim, renew, *denials = source.CASES
            self.evidence.stage(claim)
            claim_xid, claim_receipt = self.closed_reply("wa_worker", claim + ".sql", template="claim-0",
                                                        case=claim, preimage=self.secret, fence=0)
            before = self.work_state()
            source.require(source.live_state(before, claim_xid), "LEASE_RENEW_LIVE_WINDOW")
            before_state = self.state(3)
            source.require(scoped_delta(pending, before_state), "LEASE_RENEW_CLAIM_DELTA_UNCONFIRMED")
            self.result(claim, claim_receipt, live_fence=1, exact_captured_claim_xid=True, other_tables_unchanged=True)
            self.evidence.stage(renew)
            renew_xid, receipt = self.closed_reply("wa_worker", renew + ".sql", template="renew-1",
                                                  case=renew, preimage=self.secret, fence=1)
            self.window = self.renewed_window
            after = self.work_state()
            baseline = self.state(4)
            source.require(source.renewal_delta(before, after, claim_xid, renew_xid) and scoped_delta(before_state, baseline),
                           "LEASE_RENEW_POSITIVE_DELTA")
            self.retain(4)
            self.result(renew, receipt, live_fence=1, all_other_domain_fields_unchanged=True, tables_observed=42)
            for count, name in enumerate(denials, 5):
                self.evidence.stage(name)
                self.deadline()
                supplied = self.secret if name == "shorten-renew-denied" else self.lease_hash
                _, receipt = self.closed_reply("wa_worker", name + ".sql", template="renew-1", case=name, preimage=supplied, fence=1)
                source.require(source.exact_negative_state(after, self.work_state(), renew_xid) and self.state(count) == baseline,
                               "LEASE_RENEW_NEGATIVE_RESIDUE")
                self.retain(count)
                self.result(name, receipt, unchanged_live_renewed_row=True, tables_unchanged=42)
            self.all_triggers()
        except BaseException as error:
            self.evidence.stop(self.evidence.code(error))
        finally:
            if not self.owner.transport.unknown:
                try:
                    self.closure()
                    self.evidence.value["complete_final_client_closure"] = True
                except BaseException as error:
                    self.uncertain(self.evidence.code(error))
        if tuple(row["case"] for row in self.evidence.value["results"]) == source.CASES and self.evidence.value["first_failure"] is None:
            self.evidence.value.update(status=PASS, stage="COMPLETE")
        self.evidence.value["remote_outcome_unconfirmed"] = self.owner.transport.unknown
        return self.evidence.finish()

    def result(self, case, receipt, **safe):
        self.evidence.value["results"].append({"case": case, **receipt, **safe})
        self.evidence.save()


def coordinate(owner, native, packet, assets, *, clock=time.monotonic):
    current = owner.observed_target()
    source.require(current["container_id"] == owner.resources.cid and current["volume_created_at"] == owner.resources.volume_birth,
                   "LEASE_RENEW_FRESH_TARGET")
    evidence = Evidence(owner, packet, native)
    pipe, _, endpoint, context = shared_transport(owner, evidence)

    class Session(pipe, context["Session"]):
        pass

    class BoundRunner(Runner, endpoint, context["Coordinator"]):
        pass

    return BoundRunner(owner, native, packet, assets, evidence, context, Session, clock).run()
