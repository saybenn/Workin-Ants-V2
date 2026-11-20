"""Prepare NEW Customer F0 source-only fixtures. Never execute SQL or a process.

Existing first-rehearsal files are read-only provenance. Full update/CAS commits
remain gated: current SQL has no registered update result/no-result receipt
identity/codec. No schema ID or digest is invented to bypass that boundary.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import uuid

from contract_schema import Registry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review-output/customer-control-rehearsal"
OWNER = "customer_buyer_profile"
APPLICATION = "review-output/foundation-application.review.sql"
ACL = "context/reconciliation/foundation-sql-draft-access.json"
INPUTS = (APPLICATION, ACL, "contracts/shared/SH-004.v1.schema.json", "contracts/shared/types.v1.schema.json",
          "contracts/database-review/foundation-payloads.v1.schema.json",
          "contracts/database-review/owner-mutation-evidence.v1.schema.json",
          "context/reconciliation/database-candidate-tests.json", "review-output/first-rehearsal/fixtures.json")
CONTROLS = ["P0C-BOOT-01", "P0C-ATOMIC-01", "P0C-UNIQUE-01", "P0C-CAS-01"]
NAMESPACE = uuid.UUID("c536619a-924a-451a-b48c-e0320ee407d6")
GATE = "CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED"


class FixtureRegistry(Registry):
    """Offline-only union support required by the existing evidence document."""
    def errors(self, value, schema, current=None, path="$"):
        if isinstance(schema.get("type"), list):
            variants = [{**schema, "type": kind} for kind in schema["type"]]
            return [] if any(not self.errors(value, variant, current or schema, path) for variant in variants) else [path + ": type union failed"]
        return super().errors(value, schema, current, path)


def quote(value): return "'" + str(value).replace("'", "''") + "'"
def json_sql(value): return quote(json.dumps(value, separators=(",", ":"))) + "::jsonb"
def digest_sql(value): return "encode(sha256(convert_to(" + json_sql(value) + "::text,'UTF8')),'hex')"
def uid(name): return str(uuid.uuid5(NAMESPACE, name))
def insert(table, values): return "INSERT INTO " + table + " (" + ",".join('"' + key + '"' for key in values) + ") VALUES (" + ",".join(values.values()) + ");"
def sha(raw): return hashlib.sha256(raw).hexdigest()


def fixture_trigger_restoration(application_sql):
    tables = ("app.users", "app.user_security_profiles")
    triggers = []
    for match in re.finditer(r'CREATE\s+(?:CONSTRAINT\s+)?TRIGGER\s+"?([a-z_][a-z_0-9]*)"?\s+([^;]*);', application_sql, re.S):
        table = re.search(r'\bON\s+((?:"?[a-z_][a-z_0-9]*"?\.)"?[a-z_][a-z_0-9]*"?)', match[2])
        if not table or table[1].replace('"', '') not in tables: continue
        function = re.search(r'EXECUTE\s+FUNCTION\s+([a-z_][a-z_0-9]*\.[a-z_][a-z_0-9]*)\(\)', match[2])
        if not function: raise ValueError("unsupported fixture trigger restoration shape")
        triggers.append({"table": table[1].replace('"', ''), "trigger": match[1], "function": function[1], "enabled": "O"})
    triggers.sort(key=lambda row: (row["table"], row["trigger"]))
    if any(not any(row["table"] == table and row["trigger"] == "owner_commit" for row in triggers) for table in tables):
        raise ValueError("fixture source owner guard omitted")
    values = ",".join("(" + ",".join(quote(row[key]) for key in ("table", "trigger", "function", "enabled")) + ")" for row in triggers)
    sql = "WITH expected(table_name,name,function_name,enabled) AS (VALUES " + values + "),actual AS (SELECT n.nspname||'.'||c.relname,t.tgname::text,fn.nspname||'.'||p.proname,t.tgenabled::text FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace fn ON fn.oid=p.pronamespace WHERE n.nspname='app' AND c.relname IN ('users','user_security_profiles') AND NOT t.tgisinternal) SELECT jsonb_build_object('expected_user_trigger_count'," + str(len(triggers)) + ",'actual_user_trigger_count',(SELECT count(*) FROM actual),'exact_user_trigger_set_and_states',NOT EXISTS((SELECT * FROM expected EXCEPT SELECT * FROM actual) UNION ALL (SELECT * FROM actual EXCEPT SELECT * FROM expected)),'no_project_user_trigger_disabled',NOT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('app','platform','platform_private') AND NOT t.tgisinternal AND t.tgenabled<>'O'));\n"
    return triggers, sql


def diagnostic(sqlstate, *, message=None, constraint=None, function=None):
    return {"sqlstate": sqlstate, "exact_source_message": message,
            "source_constraint": constraint, "required_source_function": function,
            "unknown_diagnostic_disposition": "STOP_UNCLASSIFIED_NOT_EXPECTED_PASS"}


def capability_set(acl, ids, *, update=False, extra_commands=(), extra_message=False):
    row_ids = {model: [ids[model]] for model in ("CustomerProfile", "RuntimeCommandReceipt", "CustomerProfileLifecycleEvent", "OwnerMutationEvidence")}
    row_ids["RuntimeCommandReceipt"] += list(extra_commands)
    row_ids["RuntimeOutboxMessage"] = [ids["event"]] + ([ids["free"]] if not update or extra_message else []) + ([ids["extra"]] if extra_message and not update else [])
    tokens = set()
    for row in acl:
        if row["role"] != "wa_app_runtime" or row["model"] not in row_ids: continue
        verbs = ("SELECT", "INSERT") if not update or row["model"] != "CustomerProfile" else ("SELECT",)
        if row["operation"] in verbs:
            for row_id in row_ids[row["model"]]:
                tokens.update(row["model"] + "/" + row_id + "/" + row["operation"] + "/" + field for field in row["fields"])
    if update:
        # @row is the explicit RLS row gate, not a field wildcard. Physical
        # changed-field guard also requires each exact updated field token.
        tokens.update("CustomerProfile/" + ids["CustomerProfile"] + "/UPDATE/" + field
                      for field in ("@row", "displayName", "revision", "updatedAt"))
    tokens.add("CustomerProfile/" + ids["CustomerProfile"] + "/revision/0")
    return sorted(tokens)


def create_case(name, variation, acl, registry, *, semantic=None):
    ids = {key: uid(name + "/" + key) for key in ("CustomerProfile", "RuntimeCommandReceipt", "CustomerProfileLifecycleEvent", "OwnerMutationEvidence", "event", "free", "extra", "duplicate", "user", "grant")}
    c, q, h, e, u = [ids[key] for key in ("CustomerProfile", "RuntimeCommandReceipt", "CustomerProfileLifecycleEvent", "OwnerMutationEvidence", "user")]
    semantic = semantic or "customer-controls-" + name
    fingerprint = sha(("synthetic-intent:" + semantic).encode("utf8"))
    event = {"eventName": "customer.lifecycle_changed.v1", "customerProfileId": c, "userId": u, "lifecycleRevision": "0", "safeState": "active"}
    free = {"sourceOwner": OWNER, "userId": u, "track": "customer", "customerProfileId": c, "sourceCreationRevision": "0", "sourceCreationReceipt": q, "semanticKey": OWNER + "/" + c + "/default-free-enrollment/v1"}
    evidence = {"schema": "database-owner-evidence.v1", "owner": OWNER, "model": "CustomerProfile", "primaryKey": {"id": c}, "prior": None,
                "committed": {"id": c, "userId": u, "status": "active", "revision": "0", "privacyGeneration": "0"}, "decisionRef": "customer-controls-v1"}
    response = {"contract": "SH-004.v1", "requestId": name, "status": "ok", "value": {"customerProfileId": c, "userId": u, "lifecycle": "active", "sourceToken": "0",
                "receipt": {"owner": OWNER, "id": q, "semanticKey": semantic, "fingerprint": fingerprint, "sourceToken": "0", "recordedAt": "2026-11-17T00:00:00Z"}}}
    types = registry.documents["urn:workin-ants:types:v1"]
    payloads = registry.documents["urn:workinants:database-review:foundation-payloads:v1"]
    owner_evidence = registry.documents["urn:workinants:database-review:owner-evidence:v1"]
    baseline_errors = (registry.check("SH-004", "response", response) +
                       registry.errors(event, types["$defs"]["EventPayload_customer_lifecycle_changed_v1"], types) +
                       registry.errors(free, payloads["$defs"]["assignDefaultFreeTrackCustomerCommand"], payloads) +
                       registry.errors(evidence, owner_evidence["$defs"]["CustomerProfile"], owner_evidence))
    if baseline_errors: raise ValueError("baseline fixture violates registered closed schema")
    expected = None
    if variation == "missing-event-user":
        event.pop("userId"); expected = diagnostic("P0001", message="unregistered or incoherent F0 message", function="platform_private.message_json_guard")
    elif variation == "wrong-event-user":
        event["userId"] = uid("foreign-user"); expected = diagnostic("P0001", message="missing atomic Customer lifecycle fact", function="platform_private.customer_atomic")
    elif variation == "missing-result-receipt":
        response["value"].pop("receipt"); expected = diagnostic("23514", constraint="result_json_boundary")
    elif variation == "result-version": expected = diagnostic("23514", constraint="result_version_registered")
    elif variation == "missing-evidence-status":
        evidence["committed"].pop("status"); expected = diagnostic("23514", constraint="closed_evidence_json")
    elif variation == "create-predecessor": expected = diagnostic("23514", constraint="evidence_identity")
    elif variation in ("missing-evidence", "missing-history"):
        expected = diagnostic("P0002", message="query returned no rows", function="platform_private.customer_atomic")
    elif variation == "missing-event": expected = diagnostic("P0001", message="missing atomic Customer lifecycle fact", function="platform_private.customer_atomic")
    elif variation == "missing-free": expected = diagnostic("P0001", message="missing durable default-Free intent", function="platform_private.customer_atomic")
    elif variation == "extra-free": expected = diagnostic("P0001", message="extra or missing Customer messages", function="platform_private.customer_atomic")
    elif variation == "wrong-history-actor": expected = diagnostic("P0001", message="missing atomic Customer lifecycle fact", function="platform_private.customer_atomic")
    elif variation in ("duplicate-semantic", "changed-fingerprint"):
        expected = diagnostic("23505", constraint="runtime_command_receipt_owner_module_id_operation_subject_s_key")
    elif variation != "valid": raise ValueError("unsupported exact fixture variation")

    command = {"id": quote(q), "owner_module_id": quote(OWNER), "operation": quote("SH-004.v1"), "subject_scope": quote("CustomerProfile:" + c), "semantic_key": quote(semantic), "fingerprint": quote(fingerprint), "state": quote("committed"), "source_revision": "0", "result_schema_id": quote("SH-004.v1#/$defs/response"), "result_schema_version": quote("2" if variation == "result-version" else "1"), "result_digest": digest_sql(response), "result_body": json_sql(response)}
    statements = [insert("platform.runtime_command_receipt", command)]
    stages = ["COMMAND_INSERT"]
    if variation in ("duplicate-semantic", "changed-fingerprint"):
        duplicate = {**command, "id": quote(ids["duplicate"])}
        if variation == "changed-fingerprint": duplicate["fingerprint"] = quote(sha(b"different synthetic intent"))
        statements.append(insert("platform.runtime_command_receipt", duplicate))
        stages.append("DUPLICATE_COMMAND_INSERT")
    statements.append(insert("app.customer_profiles", {"id": quote(c), "user_id": quote(u), "status": quote("active"), "revision": "0", "privacy_generation": "0"}))
    stages.append("CUSTOMER_INSERT")
    if variation != "missing-history":
        statements.append(insert("app.customer_profile_lifecycle_event", {"id": quote(h), "customer_profile_id": quote(c), "command_receipt_id": quote(q), "source_revision": "0", "from_status": "NULL", "to_status": quote("active"), "name": quote("customer.lifecycle_changed.v1"), "actor_user_id": quote(uid("foreign-user") if variation == "wrong-history-actor" else u)}))
        stages.append("HISTORY_INSERT")
    if variation != "missing-evidence":
        statements.append(insert("platform.owner_mutation_evidence", {"id": quote(e), "command_receipt_id": quote(q), "owner_module_id": quote(OWNER), "aggregate_kind": quote("CustomerProfile"), "aggregate_id": quote(c), "previous_revision": "0" if variation == "create-predecessor" else "NULL", "committed_revision": "0", "action": quote("SH-004.v1"), "decision_ref": quote("customer-controls-v1"), "evidence_schema_id": quote("urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile"), "evidence_schema_version": quote("1"), "evidence_digest": digest_sql(evidence), "evidence_body": json_sql(evidence)}))
        stages.append("EVIDENCE_INSERT")
    messages = [(0, event, "event", "customer.lifecycle_changed.v1", "urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1", ids["event"]),
                (1, free, "command", "assignDefaultFreeTrack.v1", "urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand", ids["free"])]
    if variation == "extra-free": messages.append((2, free, "command", "assignDefaultFreeTrack.v1", messages[1][4], ids["extra"]))
    for ordinal, body, kind, message, schema, row_id in messages:
        if variation == "missing-event" and ordinal == 0 or variation == "missing-free" and ordinal == 1: continue
        statements.append(insert("platform.runtime_outbox_message", {"id": quote(row_id), "command_receipt_id": quote(q), "kind": quote(kind), "producer_owner": quote(OWNER), "aggregate_kind": quote("CustomerProfile"), "aggregate_id": quote(c), "source_revision": "0", "source_generation": "0", "ordinal": str(ordinal), "name": quote(message), "schema_version": quote("1"), "payload_schema_id": quote(schema), "payload_hash": digest_sql(body), "payload": json_sql(body), "correlation_id": quote(name), "causation_id": quote(q), "occurred_at": "clock_timestamp()", "effective_at": "clock_timestamp()"}))
        stages.append("EVENT_INSERT" if ordinal == 0 else "FREE_INSERT" if ordinal == 1 else "EXTRA_FREE_INSERT")
    ready = "WA_CUSTOMER_CONTROL_READY_TO_COMMIT"
    marker_plan = {"expected_failure_stage": None, "expected_failure_timing": None, "expected_completed_markers": [ready], "forbidden_markers": [], "commit_acknowledgement_required": expected is None}
    if expected is not None:
        immediate = {"missing-result-receipt": "COMMAND_INSERT", "result-version": "COMMAND_INSERT", "create-predecessor": "EVIDENCE_INSERT", "missing-evidence-status": "EVIDENCE_INSERT", "missing-event-user": "EVENT_INSERT", "duplicate-semantic": "DUPLICATE_COMMAND_INSERT", "changed-fingerprint": "DUPLICATE_COMMAND_INSERT"}
        failure_stage = immediate.get(variation, "COMMIT")
        staged, expected_markers, forbidden = [], [], []
        seen_failure = False
        for stage, statement in zip(stages, statements):
            before, after = "WA_CUSTOMER_CONTROL_BEFORE_" + stage, "WA_CUSTOMER_CONTROL_AFTER_" + stage
            staged += ["SELECT " + quote(before) + ";", statement, "SELECT " + quote(after) + ";"]
            if seen_failure: forbidden += [before, after]
            elif stage == failure_stage:
                expected_markers.append(before); forbidden.append(after); seen_failure = True
            else: expected_markers += [before, after]
        before_commit = "WA_CUSTOMER_CONTROL_BEFORE_COMMIT"
        if failure_stage == "COMMIT": expected_markers += [ready, before_commit]
        else: forbidden += [ready, before_commit]
        statements = staged + ["SELECT " + quote(ready) + ";", "SELECT " + quote(before_commit) + ";", "COMMIT;"]
        marker_plan = {"expected_failure_stage": failure_stage, "expected_failure_timing": "IMMEDIATE_STATEMENT" if failure_stage != "COMMIT" else "DEFERRED_COMMIT", "expected_completed_markers": expected_markers, "forbidden_markers": forbidden, "commit_acknowledgement_required": False, "earlier_error_rule": "Matching SQLSTATE/diagnostic without every expected marker at the exact stage is unexpected; stop rather than count PASS."}
    else:
        statements += ["SELECT 'WA_CUSTOMER_CONTROL_READY_TO_COMMIT';", "COMMIT;"]
    case = {"name": name, "variation": variation, "status": "NOT_RUN", "runtime_eligibility": "PENDING_INDEPENDENT_SOURCE_PACKET_AND_RUN_REVIEW", "control_ids": ["P0C-BOOT-01", "P0C-ATOMIC-01"] if variation == "valid" else ["P0C-UNIQUE-01"] if variation in ("duplicate-semantic", "changed-fingerprint") else ["P0C-ATOMIC-01"],
            "grant": {"id": ids["grant"], "principal_user_id": u, "database_login_role": "wa_app_runtime", "owner_module_id": OWNER, "action": "SH-004.v1", "purpose": "provision", "target_kind": "CustomerProfile", "target_id": c, "source_generation": "0", "security_generation": "0", "allowed_fields": capability_set(acl, ids, extra_commands=[ids["duplicate"]] if variation in ("duplicate-semantic", "changed-fingerprint") else [], extra_message=variation == "extra-free")},
            "ids": ids, "semantic_key": semantic, "fixture_values": {"response": response, "event": event, "free_command": free, "evidence": evidence},
            "expected_commit": expected is None, "intended_diagnostic": expected,
            "stage_marker_oracle": marker_plan,
            "observer_expected": {"customer": int(expected is None), "command": int(expected is None), "history": int(expected is None), "evidence": int(expected is None), "outbox": 2 if expected is None else 0, "track_enrollments": 0, "coherent": expected is None},
            "transaction_sql": name + ".sql", "observer_sql": name + "-observe.sql",
            "transaction_contract": "Root opens actual app READ COMMITTED transaction, captures login/pid/xid before business locks, issuer independently commits fresh handle hash + exact finite caps, then app binds handle. SQL contains neither handle nor issuer writes. Failure requires client/backend closure before independent observer; never treat command count as a commit proof.",
            "diagnostic_limit": "For P0002 require source-bound customer_atomic frame; state alone does not identify missing history/evidence. Unlisted diagnostics stop. 23505 proves native duplicate rejection only, not a production semantic-idempotency adapter."}
    observe = "SELECT jsonb_build_object('customer',(SELECT count(*) FROM app.customer_profiles WHERE id=" + quote(c) + "),'command',(SELECT count(*) FROM platform.runtime_command_receipt WHERE id IN (" + quote(q) + "," + quote(ids["duplicate"]) + ")), 'history',(SELECT count(*) FROM app.customer_profile_lifecycle_event WHERE customer_profile_id=" + quote(c) + "),'evidence',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE aggregate_kind='CustomerProfile' AND aggregate_id=" + quote(c) + "),'outbox',(SELECT count(*) FROM platform.runtime_outbox_message WHERE command_receipt_id IN (" + quote(q) + "," + quote(ids["duplicate"]) + ")),'track_enrollments',(SELECT count(*) FROM app.track_enrollment_receipt WHERE profile_id=" + quote(c) + "));\n"
    coherent = f'''EXISTS(SELECT 1 FROM app.customer_profiles c
 JOIN platform.runtime_command_receipt q ON q.id={quote(q)} AND q.owner_module_id={quote(OWNER)} AND q.operation='SH-004.v1'
  AND q.subject_scope='CustomerProfile:'||c.id::text AND q.semantic_key={quote(semantic)} AND q.fingerprint={quote(fingerprint)}
  AND q.state='committed' AND q.source_revision=0 AND q.result_schema_id='SH-004.v1#/$defs/response' AND q.result_schema_version='1'
  AND q.result_body={json_sql(response)} AND q.result_digest=encode(sha256(convert_to(q.result_body::text,'UTF8')),'hex')
 JOIN app.customer_profile_lifecycle_event h ON h.id={quote(h)} AND h.customer_profile_id=c.id AND h.command_receipt_id=q.id
  AND h.source_revision=0 AND h.from_status IS NULL AND h.to_status=c.status AND h.actor_user_id=c.user_id AND h.name='customer.lifecycle_changed.v1'
 JOIN platform.owner_mutation_evidence e ON e.id={quote(e)} AND e.command_receipt_id=q.id AND e.owner_module_id=q.owner_module_id
  AND e.aggregate_kind='CustomerProfile' AND e.aggregate_id=c.id::text AND e.previous_revision IS NULL AND e.committed_revision=0
  AND e.action=q.operation AND e.decision_ref='customer-controls-v1' AND e.evidence_schema_version='1'
  AND e.evidence_schema_id='urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile'
  AND e.evidence_body={json_sql(evidence)} AND e.evidence_digest=encode(sha256(convert_to(e.evidence_body::text,'UTF8')),'hex')
 WHERE c.id={quote(c)} AND c.user_id={quote(u)} AND c.status='active' AND c.revision=0 AND c.privacy_generation=0
  AND c.display_name IS NULL AND c.avatar_media_id IS NULL AND c.city IS NULL AND c.state IS NULL AND c.country IS NULL AND c.archived_at IS NULL
  AND q.mutation_transaction_id=c.mutation_transaction_id AND h.mutation_transaction_id=c.mutation_transaction_id AND e.mutation_transaction_id=c.mutation_transaction_id
  AND (SELECT count(*) FROM platform.runtime_outbox_message o WHERE o.command_receipt_id=q.id AND o.producer_owner=q.owner_module_id
   AND o.aggregate_kind='CustomerProfile' AND o.aggregate_id=c.id::text AND o.source_revision=0 AND o.source_generation=0 AND o.schema_version='1'
   AND o.causation_id=q.id::text AND o.correlation_id={quote(name)} AND o.mutation_transaction_id=c.mutation_transaction_id
   AND o.payload_hash=encode(sha256(convert_to(o.payload::text,'UTF8')),'hex')
   AND ((o.id={quote(ids['event'])} AND o.ordinal=0 AND o.kind='event' AND o.name='customer.lifecycle_changed.v1'
    AND o.payload_schema_id='urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1' AND o.payload={json_sql(event)})
    OR (o.id={quote(ids['free'])} AND o.ordinal=1 AND o.kind='command' AND o.name='assignDefaultFreeTrack.v1'
    AND o.payload_schema_id='urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand' AND o.payload={json_sql(free)})))=2)'''
    observe = observe.removesuffix(");\n") + ",'coherent'," + coherent + ");\n"
    return case, "\n".join(statements) + "\n", observe


def update_plan(base, acl):
    c, user = base["ids"]["CustomerProfile"], base["ids"]["user"]
    ids = {key: uid("update/" + c + "/" + key) for key in base["ids"]}
    ids["CustomerProfile"], ids["user"] = c, user
    root_sql = "UPDATE app.customer_profiles SET display_name='Customer control revision one', revision=revision+1 WHERE id=" + quote(c) + " AND revision=0 RETURNING id,revision;\n"
    plan = {"name": "create-then-fresh-update", "status": "NOT_RUN", "control_ids": ["P0C-BOOT-01", "P0C-ATOMIC-01"], "execution_dependencies": [GATE], "baseline_case": base["name"],
        "runtime_eligibility": "COMPLETE_COMMIT_GROUP_BLOCKED_SOURCE_RECEIPT_CONTRACT", "source_root_mutation_sql": root_sql, "ids": ids,
        "grant": {"principal_user_id": user, "database_login_role": "wa_app_runtime", "owner_module_id": OWNER, "action": "updateCustomerProfileIdentity.v1", "purpose": "profile_update", "target_kind": "CustomerProfile", "target_id": c, "source_generation": "0", "security_generation": "0", "allowed_fields": capability_set(acl, ids, update=True)},
        "required_group": {"command_operation": "updateCustomerProfileIdentity.v1", "expected_previous_revision": "0", "committed_revision": "1", "evidence_prior": deepcopy(base["fixture_values"]["evidence"]["committed"]), "evidence_committed": {**base["fixture_values"]["evidence"]["committed"], "revision": "1"}, "history_from_status": "active", "history_to_status": "active", "event_ordinal": 0, "event_revision": "1", "exact_message_count": 1, "free_command_count": 0},
        "receipt_gate": {"non_null_update_body_rejected_by": "result_json_boundary", "sql_null_body": "Bypasses result_storage_digest and is permitted by committed_result for this operation, but no update/no-result schema identity or SQLNULL digest codec is registered.", "forbidden_shortcuts": ["invent schema ID", "relabel SH004 result", "arbitrary digest", "equate JSON null hash with source-defined SQLNULL absence codec"]},
        "after_gate_variations": [
            {"name": "missing-exact-prior", "status": "NOT_RUN", "intended_diagnostic": diagnostic("23514", constraint="evidence_identity"), "mutation": "Omit prior object while previous_revision0/committed_revision1; immediate evidence_identity rejects before deferred owner proof."},
            {"name": "stale-predecessor-in-evidence", "status": "NOT_RUN", "intended_diagnostic": diagnostic("23514", constraint="evidence_identity"), "mutation": "Supply previous_revision1 beside committed_revision1 under actual OLD0; immediate evidence_identity rejects skipped predecessor relation."},
            {"name": "skipped-source-revision", "status": "NOT_RUN", "intended_diagnostic": diagnostic("P0001", message="CAS revision must increment once", function="platform_private.guard_customerprofile")},
            {"name": "same-transaction-second-update", "status": "NOT_RUN", "intended_diagnostic": diagnostic("42501", message="field or CAS scope denied", function="platform_private.guard_customerprofile"), "prerequisite": "Second source UPDATE targets revision1 under unchanged grant authorizing only predecessor0, after first source UPDATE and before commit."},
            {"name": "extra-free-on-update", "status": "NOT_RUN", "intended_diagnostic": diagnostic("P0001", message="extra or missing Customer messages", function="platform_private.customer_atomic"), "prerequisite": "Otherwise exact one-event update group plus typed extra Free command ordinal1; no invented update result."},
            {"name": "wrong-history-actor", "status": "NOT_RUN", "intended_diagnostic": diagnostic("P0001", message="missing atomic Customer lifecycle fact", function="platform_private.customer_atomic")}],
        "permitted_isolated_current_probe": "A separately reviewed app root UPDATE can RETURN one id/revision under its own fresh grant, followed unconditionally by ROLLBACK; this is not a positive committed owner proof or typed API result."}
    for vector in plan["after_gate_variations"]:
        vector["grant"] = {**plan["grant"], "allowed_fields": capability_set(acl, ids, update=True, extra_message=vector["name"] == "extra-free-on-update")}
        vector["baseline_rule"] = "Run against the named baseline still at revision0, with distinct fresh tuple-bound grant; every adversarial group must fully roll back before the next. Execute the successful revision1 group last, or use a separate independently created baseline."
    return plan


def build(root=ROOT):
    root = Path(root)
    acl = json.loads((root / ACL).read_text(encoding="utf8"))
    registry = FixtureRegistry(root)
    for path in ("contracts/database-review/foundation-payloads.v1.schema.json", "contracts/database-review/owner-mutation-evidence.v1.schema.json"):
        doc = json.loads((root / path).read_text(encoding="utf8")); registry.documents[doc["$id"]] = doc
    variations = ["valid", "missing-history", "missing-evidence", "missing-event", "missing-free", "create-predecessor", "missing-event-user", "wrong-event-user", "wrong-history-actor", "missing-result-receipt", "result-version", "missing-evidence-status", "extra-free", "duplicate-semantic", "changed-fingerprint"]
    files, cases = {}, []
    for index, variation in enumerate(variations):
        case, sql, observe = create_case("customer-" + str(index).zfill(2) + "-" + variation, variation, acl, registry)
        cases.append(case); files[case["transaction_sql"]] = sql; files[case["observer_sql"]] = observe
    for label in ("a", "b"):
        case, sql, observe = create_case("unique-distinct-scope-" + label, "valid", acl, registry, semantic="customer-controls-shared-identical-text-key")
        case["control_ids"] = ["P0C-UNIQUE-01"]
        cases.append(case); files[case["transaction_sql"]] = sql; files[case["observer_sql"]] = observe
    seed = ["-- TRUSTED SYNTHETIC IDENTITY SETUP ONLY; not restricted Identity mutation proof.", "BEGIN;", "ALTER TABLE app.users DISABLE TRIGGER owner_commit;", "ALTER TABLE app.user_security_profiles DISABLE TRIGGER owner_commit;"]
    for u in [case["ids"]["user"] for case in cases] + [uid("foreign-user")]:
        seed += [insert("app.users", {"id": quote(u), "is_public": "false", "revision": "0", "privacy_generation": "0", "created_at": "clock_timestamp()", "updated_at": "clock_timestamp()", "mutation_transaction_id": "pg_current_xact_id()::text"}),
                 insert("app.user_security_profiles", {"id": quote(uid(u + "/security")), "user_id": quote(u), "revision": "0", "security_generation": "0", "created_at": "clock_timestamp()", "updated_at": "clock_timestamp()", "mutation_transaction_id": "pg_current_xact_id()::text"})]
    seed += ["ALTER TABLE app.user_security_profiles ENABLE TRIGGER owner_commit;", "ALTER TABLE app.users ENABLE TRIGGER owner_commit;", "COMMIT;"]
    files["trusted-identity-fixtures.sql"] = "\n".join(seed) + "\n"
    expected_triggers, restoration_sql = fixture_trigger_restoration((root / APPLICATION).read_text(encoding="utf8"))
    files["trusted-identity-trigger-restore-observe.sql"] = restoration_sql
    update = update_plan(cases[0], acl)
    cas_update = update_plan(cases[-1], acl)
    second_ids = {key: uid("cas-b/" + cas_update["ids"]["CustomerProfile"] + "/" + key) for key in cas_update["ids"]}
    second_ids["CustomerProfile"], second_ids["user"] = cas_update["ids"]["CustomerProfile"], cas_update["ids"]["user"]
    participants = [{"session": "A", "ids": cas_update["ids"], "grant": cas_update["grant"], "source_update_sql": cas_update["source_root_mutation_sql"]},
                    {"session": "B", "ids": second_ids, "grant": {**cas_update["grant"], "allowed_fields": capability_set(acl, second_ids, update=True)}, "source_update_sql": cas_update["source_root_mutation_sql"].replace("revision one", "revision one loser")}]
    cas = {"name": "two-real-app-session-cas", "status": "NOT_RUN", "control_ids": ["P0C-CAS-01"], "execution_dependencies": [GATE], "runtime_eligibility": "RETAINED_WINNER_BLOCKED_UNTIL_COMPLETE_UPDATE_RECEIPT_GROUP_REGISTERED", "steps": [
        "Commit the valid create revision0 group and independently observe its exact values.",
        "Open app A and B as distinct real authenticated wa_app_runtime backends in READ COMMITTED; capture each immutable pid/xid before business reads/locks. Issuer separately commits two fresh handles bound to those exact tuples, same principal/root expected revision0; distinct command/history/evidence/event IDs and semantic keys, exact finite caps per session.",
        "Bind both handles. A executes UPDATE ... WHERE id=target AND revision=0 RETURNING id,revision; require exactly one row revision1. Keep A open holding its row/source locks.",
        "B starts its own same-predicate UPDATE; independently confirm it waits on A, rather than inferring overlap from launch order. A appends its exact reviewed command/history/closed prior+committed evidence/event-only group, then commits once the receipt dependency is resolved.",
        "After A commits, B resumes; require exactly zero returned rows. Explicitly ROLLBACK B. B must append no command/history/evidence/messages. Do not treat zero rows as a committed result or retry with fresh revision in this case.",
        "Close both clients and independently confirm exact backend absence; privileged observer requires source revision1 and winner field, one update history/evidence/command/event, no loser group, no update Free command; creation group still retained. Audit any timeout/deadlock/42501 or other unlisted result as stopped, not an expected CAS success."],
        "participants": participants, "baseline_case": cas_update["baseline_case"], "separate_baseline_reason": "CAS uses the distinct-scope-b Customer so a successful BOOT update cannot consume its revision0 precondition.",
        "partial_probe_limit": "A/B contention with both rolled back can prove waiting and rollback only; it cannot satisfy the retained one-winner P0C-CAS-01 assertion.",
        "mandatory_blocked_vectors": [{"vector": "OWNER-REVISIONS", "models": ["TrackUsageReservation", "PrivacyRestoreMarker"], "execution_dependencies": ["P0D_TRACK_USAGE_PERIOD_RECONCILIATION", "P0F_PRIVACY_RESTORE_GENERATION_PORT"], "status": "NOT_RUN"}]}
    manifest = {"schema": "workinants.customer-control-fixtures.v1", "status": "NOT_RUN", "database_posture": "D", "database_contacted": False, "sql_executed": False, "selected_control_ids": CONTROLS,
        "generator_source_sha256": sha(Path(__file__).read_bytes()), "focused_check_source_sha256": sha((root / "scripts/check-customer-control-rehearsal.py").read_bytes()),
        "source_inputs_sha256": {path: sha((root / path).read_bytes()) for path in INPUTS}, "cases": cases, "update_plan": update, "cas_plan": cas,
        "trusted_setup_trigger_contract": {"status": "NOT_RUN", "bypassed": [{"table": table, "trigger": "owner_commit"} for table in ("app.users", "app.user_security_profiles")], "physical_guards_retained": True, "expected_user_triggers": expected_triggers, "observer_sql": "trusted-identity-trigger-restore-observe.sql", "observer_expected": {"expected_user_trigger_count": len(expected_triggers), "actual_user_trigger_count": len(expected_triggers), "exact_user_trigger_set_and_states": True, "no_project_user_trigger_disabled": True}, "ordering": "Independently verify exact enabled state before setup and after setup COMMIT, or after failure backend closure/rollback, BEFORE any restricted case. Unexpected/missing/disabled trigger means stop. Never infer restoration from an ENABLE statement or a count alone."},
        "scope_limits": ["17 prepared CREATE/duplicate/scoped cases are nested scenario proposals, not new selected test IDs or 94/451 PASS claims.", "No request/result/auth/provider adapter qualification. Synthetic setup, no worker enrollment or protected source execution by fixture generator.", "Distinct legitimate subject scope is prepared. Distinct owner/economic effect scopes are not exercised by Customer fixtures.", "Independent observers compare exact counts, values, optional-null fields, source/history/receipt/evidence/message links, SQL storage digests and transaction coherence. Harness still must prove correct target/login/backend closure and real per-statement/COMMIT outcomes.", "Original first3 artifacts are input hashes only; generation does not modify them."],
        "files_sha256": {name: sha(value.encode("utf8")) for name, value in sorted(files.items())}}
    files["fixtures.json"] = json.dumps(manifest, indent=2) + "\n"
    return files, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    files, manifest = build()
    if not args.prepare:
        print(json.dumps({"status": "PLAN_ONLY_NOT_RUN", "cases": len(manifest["cases"]), "blocked_update_and_retained_cas": GATE})); return
    OUT.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        with (OUT / name).open("x", encoding="utf8", newline="\n") as file: file.write(value)
    print(json.dumps({"status": "PREPARED_NOT_RUN", "cases": len(manifest["cases"]), "files": len(files), "database_contacted": False}))


if __name__ == "__main__": main()
