"""The two rollback-only Consent cases inside an already verified Cloud owner."""

import ast
from copy import deepcopy
import datetime
import hashlib
import json
import re
import secrets
import subprocess
from types import ModuleType
import uuid

import prepare
import protocol


APP_CHILD = "scripts/sql-review/cloud-app-source8-v1/app_child.py"
APP_CHILD_SHA256 = "5f3a616745ba26ad6baae8266bbb254b4d791510289a1ba290bb30002fc5acfc"
RESULT_SCHEMA = "workinants.cloud-f0-consent-empty-context-result.v1"
RESULT_LEAF = "consent-immutable-results.json"
PASS = "PASS_TWO_EMPTY_CONTEXT_ROLLBACK_DENIALS_ONLY"
STOP = "STOPPED_OR_UNCONFIRMED"
ROLES = ("postgres", "wa_context_issuer", "wa_app_runtime")
FAILURES = frozenset({
    "CONSENT_CHILD_UNCONFIRMED", "CONSENT_CHILD_EVIDENCE_UNCONFIRMED", "CONSENT_CHILD_SECRET_EVIDENCE",
    "CONSENT_AUTHENTICATION_UNCONFIRMED", "CONSENT_TARGET_IDENTITY", "CONSENT_RECIPE_DRIFT",
    "CONSENT_APP_TUPLE_DRIFT", "CONSENT_CONTEXT_BIND_UNCONFIRMED", "CONSENT_IDENTITY_NAMESPACE_UNCONFIRMED",
    "CONSENT_IDENTITY_SEED_UNCONFIRMED", "CONSENT_UNCOMMITTED_PREFIX_UNCONFIRMED",
    "CONSENT_PROOF_PREREQUISITES_UNCONFIRMED", "CONSENT_EXPECTED_GUARD_UNCONFIRMED",
    "CONSENT_APP_BACKEND_CLOSURE_UNCONFIRMED", "CONSENT_ALL_CLIENT_CLOSURE_UNCONFIRMED",
    "CONSENT_TRIGGER_PARITY_UNCONFIRMED", "CONSENT_NATIVE_PARITY_UNCONFIRMED",
    "CONSENT_GRANT_RETENTION_UNCONFIRMED", "CONSENT_ROLLBACK_PARITY_UNCONFIRMED",
    "CONSENT_EXACT_RESIDUE_UNCONFIRMED", "CONSENT_STICKY_TRANSPORT_UNCERTAINTY",
    "ISSUER_TERMINAL_EXIT_UNEXPECTED", "SESSION_BEGIN_STATE", "CAPTURE_REQUIRES_LIVE_TRANSACTION",
    "PRIVILEGED_TRANSACTION_SHAPE", "ISSUER_OR_PRIVILEGED_COMMIT_UNCONFIRMED", "PRIVILEGED_TERMINAL_EXIT_UNEXPECTED",
    "DECLARED_GRANT_LOGIN", "EXACT_ISSUER_TUPLE", "CAPTURED_GRANT_TUPLE_FORMAT", "CAPTURED_ISSUER_CLOCK_FORMAT",
    "FRESH_GRANT_ID_AND_HASH_REQUIRED", "FINITE_CAPABILITIES_REQUIRED", "ONE_GRANT_PRINCIPAL_REQUIRED",
    "GRANT_COLUMN_CLOSURE", "FINITE_GRANT_INSTANCE_LIMIT",
})


def supports(blobs):
    for name, digest in ((APP_CHILD, APP_CHILD_SHA256), (prepare.APP_TRANSPORT, prepare.PINS[prepare.APP_TRANSPORT]),
                         (prepare.CONTEXT, prepare.PINS[prepare.CONTEXT])):
        protocol.require(protocol.sha(blobs[name]) == digest, "CONSENT_REVIEWED_APP_SOURCE_DRIFT")
    transport = ModuleType("_workinants_consent_app_session")
    exec(compile(blobs[prepare.APP_TRANSPORT], prepare.APP_TRANSPORT, "exec", dont_inherit=True), transport.__dict__)
    tree = ast.parse(blobs[APP_CHILD], filename=APP_CHILD)
    names = {"require", "execute_ast", "exact_nodes", "render_context"}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    declarations = [node for node in tree.body if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "CLOSED_ERRORS"]
    outer = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "coordinate")
    classes = [node for node in outer.body if isinstance(node, ast.ClassDef) and node.name == "CloudContext"]
    protocol.require({node.name for node in nodes} == names and len(nodes) == len(names)
                     and len(classes) == len(declarations) == 1 and transport.APP_ROLES == ROLES,
                     "CONSENT_REVIEWED_APP_ADAPTER_SURFACE")
    endpoint = classes[0]
    methods = {"socket_checked", "psql", "spawn", "raw", "require_backend_absent"}
    endpoint.body = [node for node in endpoint.body if isinstance(node, ast.FunctionDef) and node.name in methods]
    protocol.require({node.name for node in endpoint.body} == methods and len(endpoint.body) == len(methods),
                     "CONSENT_REVIEWED_APP_ENDPOINT_SURFACE")
    endpoint.bases = []
    namespace = dict(ast=ast, CONTEXT=prepare.CONTEXT, deepcopy=deepcopy, datetime=datetime, hashlib=hashlib, json=json,
                     re=re, secrets=secrets, uuid=uuid, APP_ROLES=ROLES, SessionStop=transport.SessionStop,
                     subprocess=subprocess)
    module = ast.fix_missing_locations(ast.Module(body=[*declarations, *nodes, endpoint], type_ignores=[]))
    exec(compile(module, APP_CHILD, "exec", dont_inherit=True), namespace)
    return transport, namespace


class Evidence:
    def __init__(self, owner, packet_hash, fixture_run_id, source8_native_sha256):
        operation = owner.operation
        self.owner = owner
        self.program = owner.program
        self.state = owner.report["consent_immutable"]
        self.safe_codes = FAILURES
        self.value = {
            "schema": RESULT_SCHEMA, "status": "IN_PROGRESS", "run_id": operation["run_id"],
            "fixture_run_id": fixture_run_id, "container_id": owner.resources.cid,
            "volume_created_at": owner.resources.volume_birth, "source_commit": operation["source"]["commit"],
            "source_tree": operation["source"]["tree"], "packet_sha256": protocol.sha(owner.raw),
            "consent_recipe_sha256": packet_hash, "full_native_baseline_sha256": source8_native_sha256,
            "case_id": prepare.CASE_ID, "assertion_id": prepare.ASSERTION, "case_order": list(protocol.CASES),
            "operations": [], "results": [], "first_failure": None, "current_stage": "AUTH",
            "current_case": None, "complete_final_client_closure": False, "evidence_complete": True,
            "assertion_promotions": 0, "posture": "D",
        }

    def allowed(self, error):
        code = getattr(error, "code", None)
        if code is None and type(error) is protocol.Held and error.args:
            code = error.args[0]
        return code if type(code) is str and code in self.safe_codes else "CONSENT_CHILD_UNCONFIRMED"

    def stop(self, code):
        safe_code = code if type(code) is str and code in self.safe_codes else "CONSENT_CHILD_UNCONFIRMED"
        failure = {"stage": self.value["current_stage"], "case": self.value["current_case"], "code": safe_code}
        self.value["status"] = STOP
        if self.value["first_failure"] is None:
            self.value["first_failure"] = failure
            self.program.record_failure("CONSENT_IMMUTABLE", safe_code)

    def save(self):
        raw = protocol.canonical(self.value)
        if len(raw) > 256 * 1024 or any(value.encode() in raw for value in self.program.all_secrets):
            self.state.pop("child_trace", None)
            self.value["evidence_complete"] = False
            self.stop("CONSENT_CHILD_SECRET_EVIDENCE")
            raise protocol.Held("CONSENT_CHILD_SECRET_EVIDENCE")
        try:
            self.state["child_trace"] = self.value
            self.program.save()
        except BaseException:
            self.value["evidence_complete"] = False
            self.stop("CONSENT_CHILD_EVIDENCE_UNCONFIRMED")
            raise protocol.Held("CONSENT_CHILD_EVIDENCE_UNCONFIRMED") from None

    def stage(self, stage, case=None):
        self.value.update(current_stage=stage, current_case=case)
        self.save()

    def finish(self):
        self.save()
        try:
            leaf = self.program.write_safe(RESULT_LEAF, self.value)
        except BaseException:
            self.value["evidence_complete"] = False
            self.stop("CONSENT_CHILD_EVIDENCE_UNCONFIRMED")
            raise protocol.Held("CONSENT_CHILD_EVIDENCE_UNCONFIRMED") from None
        self.state.pop("child_trace")
        return leaf, self.value


class Cases:
    def __init__(self, owner, native, evidence, packet, assets):
        self.owner, self.native, self.evidence, self.recipe, self.assets = owner, native, evidence, packet, assets
        self.baseline = None

    def asset(self, leaf):
        text = self.assets[leaf]
        protocol.require(protocol.sha(text.encode()) == self.recipe["source_asset_sha256"][leaf], "CONSENT_RECIPE_DRIFT")
        return text

    def auth(self):
        report = self.owner.report
        active = {row["role"]: row for row in report["authentication"] if row["correct_password"] == "PASS_SCRAM"}
        checks = {row["role"]: row["checks"] for row in report["auth_comparisons"]}
        protocol.require(all(role in active and role in checks and active[role]["wrong_password"] == "PASS_REJECTED"
                             and active[role]["actual_connection_closed"] is True and bool(checks[role])
                             and all(value is True for value in checks[role].values()) for role in ROLES),
                         "CONSENT_AUTHENTICATION_UNCONFIRMED")
        self.record({"stage": "ACTUAL_AUTHENTICATION", "roles": list(ROLES), "exact_current_login_controls": True})

    def closed(self):
        protocol.require(self.raw("postgres", protocol.GLOBAL_CLIENTS) == "0", "CONSENT_ALL_CLIENT_CLOSURE_UNCONFIRMED")
        self.record({"stage": "GLOBAL_CLIENT_CLOSURE", "zero_other_clients": True})

    def integrity(self):
        self.closed()
        triggers = protocol.strict_json(self.raw("postgres", self.asset("trigger-observer.sql")))
        protocol.require(protocol.canonical(triggers) == protocol.canonical(protocol.TRIGGERS), "CONSENT_TRIGGER_PARITY_UNCONFIRMED")
        sql = self.owner.blobs[prepare.NATIVE_COLLECTOR]
        protocol.require(protocol.sha(sql) == prepare.PINS[prepare.NATIVE_COLLECTOR], "CONSENT_RECIPE_DRIFT")
        protocol.require(self.owner.program.digest(protocol.strict_json(self.raw("postgres", sql.decode()))) ==
                         self.owner.program.digest(self.native), "CONSENT_NATIVE_PARITY_UNCONFIRMED")
        self.record({"stage": "UNCHANGED_NATIVE_AND_TRIGGERS", "native_catalog_unchanged": True, "all_triggers_verified": 100})

    def snapshot(self, ids=()):
        text = protocol.state_observer_sql(self.asset("full42-state.sql"), ids)
        return protocol.strict_json(self.raw("postgres", text))

    def bind(self, session, backend, template):
        instance = self.instances[self.issue(template, backend)]
        same = session.capture() == backend == instance["backend"]
        self.record({"stage": "APP_TUPLE_RECAPTURE", "same_backend_transaction": same})
        protocol.require(same, "CONSENT_APP_TUPLE_DRIFT")
        rows, ack, errors = session.call("SELECT platform_private.bind_request_context(" + prepare.quoted(instance["secret"]) + ");")
        protocol.require(rows == [] and ack is True and errors == "", "CONSENT_CONTEXT_BIND_UNCONFIRMED")
        self.record({"stage": "SCOPED_GRANT_BIND", "action": template["action"], "acknowledged": True})

    def retain(self, expected_count):
        ids = tuple(value["id"] for value in self.instances.values())
        protocol.require(len(ids) == expected_count and len(set(ids)) == len(ids), "CONSENT_GRANT_RETENTION_UNCONFIRMED")
        statements = []
        for value in self.instances.values():
            fields = " AND ".join(f"g.{name} IS NOT DISTINCT FROM ({value['values'][name]})" for name in self.columns)
            statements.append("SELECT (" + fields + ") AS exact,g.issuer_service=session_user::text AS issuer_owned, "
                              "g.revoked_at IS NULL AS revoked_false,g.expires_at>clock_timestamp() AS unexpired "
                              "FROM platform.database_action_grant g WHERE g.id=" + value["values"]["id"])
        text = ("SELECT jsonb_build_object('exact_count',count(*),'all_immutable_fields_equal',coalesce(bool_and(exact),false),"
                "'issuer_owned',coalesce(bool_and(issuer_owned),false),'revoked_false',coalesce(bool_and(revoked_false),false),"
                "'unexpired',coalesce(bool_and(unexpired),false)) FROM (" + " UNION ALL ".join(statements) + ") observed;")
        actual = protocol.strict_json(self.raw("wa_context_issuer", text))
        protocol.require(protocol.issuer_retention_matches(actual, expected_count), "CONSENT_GRANT_RETENTION_UNCONFIRMED")
        self.record({"stage": "ISSUER_RETENTION", "grants_exact": expected_count, "all_21_columns_verified": True})
        return ids

    def setup(self):
        self.auth()
        self.evidence.stage("IDENTITY_SETUP")
        self.integrity()
        protocol.require(self.raw("postgres", self.asset("fresh-namespace.sql")) == "t", "CONSENT_IDENTITY_NAMESPACE_UNCONFIRMED")
        before_seed = self.snapshot()
        protocol.require(protocol.state_matches(before_seed, before_seed, self.recipe["full42_tables"]),
                         "CONSENT_ROLLBACK_PARITY_UNCONFIRMED")
        self.commit("postgres", self.asset("identity-seed.sql"), "TRUSTED_IDENTITY_SEED_ONLY")
        self.integrity()
        protocol.require(self.raw("postgres", self.asset("identity-present.sql")) == "t", "CONSENT_IDENTITY_SEED_UNCONFIRMED")
        self.baseline = self.snapshot()
        protocol.require(protocol.identity_only_delta(before_seed, self.baseline, self.recipe["full42_tables"]),
                         "CONSENT_IDENTITY_SEED_UNCONFIRMED")
        self.record({"stage": "IDENTITY_BASELINE", "synthetic_identity_only": True, "tables_observed": 42,
                     "only_two_expected_rows_added": True})


    def case(self, case, index):
        name = case["name"]
        self.evidence.stage("BEGIN_APP_TRANSACTION", name)
        session = self.session("wa_app_runtime")
        denied = None
        try:
            session.begin("read committed")
            backend = session.capture()
            self.record({"stage": "FRESH_APP_TUPLE_CAPTURE", "actual_read_committed": True})
            for leaf, template in zip(("publisher.sql", "presentation.sql", "preread.sql"), case["grants_in_order"], strict=True):
                self.evidence.stage(leaf, name)
                self.bind(session, backend, template)
                expected = protocol.PREREAD_OBSERVATION if leaf == "preread.sql" else protocol.PREFIX_OBSERVATION
                matched = protocol.acknowledged_observation(*session.call(self.asset(f"{name}/{leaf}")), expected)
                self.record({"stage": leaf, "exact_acknowledged_observation": matched, "consent_owner_committed": False})
                protocol.require(matched, "CONSENT_PROOF_PREREQUISITES_UNCONFIRMED" if leaf == "preread.sql"
                                 else "CONSENT_UNCOMMITTED_PREFIX_UNCONFIRMED")
            self.evidence.stage("EXPECTED_CONSENT_GUARD", name)
            rows, ack, errors = session.call(self.asset(f"{name}/deny.sql"))
            denied = protocol.denial_receipt(name, session.process.poll(), rows, ack, errors)
            self.record({"stage": "EXPECTED_CONSENT_GUARD", **denied})
            protocol.require(denied["exact_source_diagnostic"], "CONSENT_EXPECTED_GUARD_UNCONFIRMED")
        except BaseException as error:
            self.evidence.stop(self.evidence.allowed(error))
            raise
        finally:
            try:
                exit_code = session.close()
                closed = session.closed is True and type(exit_code) is int and exit_code in (0, 3)
                if denied is not None and denied["exact_source_diagnostic"]:
                    closed = closed and exit_code == 3
                protocol.require(closed, "CONSENT_APP_BACKEND_CLOSURE_UNCONFIRMED")
            except BaseException as error:
                self.uncertain(self.evidence.allowed(error))
                raise
            self.record({"stage": "APP_BACKEND_CLOSURE", "backend_absence_observed": True, "exit_code": exit_code})
        self.evidence.stage("ROLLBACK_POSTCHECKS", name)
        self.integrity()
        ids = self.retain((index + 1) * 3)
        self.closed()
        protocol.require(self.raw("postgres", self.asset(f"{name}/zero-case-residue.sql")) == "t", "CONSENT_EXACT_RESIDUE_UNCONFIRMED")
        protocol.require(protocol.state_matches(self.baseline, self.snapshot(ids), self.recipe["full42_tables"]),
                         "CONSENT_ROLLBACK_PARITY_UNCONFIRMED")
        self.closed()
        self.evidence.value["results"].append({"case": name, "status": "PASS_EXACT_DENIED_ROLLBACK_ONLY", "diagnostic": denied,
                                              "app_and_issuer_closed": True, "tables_unchanged": 42,
                                              "original_triggers_verified": 100, "issued_grants_exact": len(ids),
                                              "exact_consent_residue_zero": True, "native_catalog_unchanged": True})
        self.evidence.save()

    def run(self):
        try:
            self.setup()
            for index, case in enumerate(self.recipe["cases"]):
                self.case(case, index)
        except BaseException as error:
            self.evidence.stop(self.evidence.allowed(error))
        finally:
            if not self.owner.transport.unknown:
                try:
                    self.closed()
                    self.evidence.value["complete_final_client_closure"] = True
                except BaseException as error:
                    self.uncertain(self.evidence.allowed(error))
        if len(self.evidence.value["results"]) == 2 and self.evidence.value["first_failure"] is None:
            self.evidence.value.update(status=PASS, current_stage="COMPLETE", current_case=None)
        self.evidence.value["remote_outcome_unconfirmed"] = self.owner.transport.unknown
        return self.evidence.finish()


def coordinate(owner, native, recipe, assets):
    transport, adapter = supports(owner.blobs)
    actual = owner.observed_target()
    protocol.require(actual["container_id"] == owner.resources.cid and actual["volume_created_at"] == owner.resources.volume_birth,
                     "CONSENT_TARGET_IDENTITY")
    evidence = Evidence(owner, protocol.sha(protocol.canonical(recipe)), recipe["fixture_run_id"], owner.program.digest(native))
    evidence.safe_codes |= adapter["CLOSED_ERRORS"]
    context = adapter["render_context"](owner.blobs, evidence.allowed, lambda *values: owner.program.all_secrets.extend(values))
    adapter.update(owner=owner, runtime={"quote": context["quote"]}, context=context)

    class Session(transport.BoundedSession, context["Session"]):
        pass

    class Runner(Cases, adapter["CloudContext"], context["Coordinator"]):
        def __init__(self):
            super().__init__(owner, native, evidence, recipe, assets)
            self.packet = {"finite_caps": {"grant_instances_max": 6}}
            self.instances, self.sequence = {}, 0
            self.columns = context["GRANT_COLUMNS"]

        def session(self, role):
            return Session(role, self)

        def uncertain(self, code):
            self.owner.transport.unknown = True
            self.owner.docker.remote_unknown = True
            self.evidence.stop(code)

    return Runner().run()
