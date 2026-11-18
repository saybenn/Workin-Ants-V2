"""Prepare bounded, dormant direct-SQL worker proposals; never execute a process.

This is neither a worker loop nor a P0-D adapter. Existing selected control IDs
remain NOT_RUN. No existing packet is rewritten. --prepare creates new files
exclusively. Root must independently review the packet and its execution wrapper.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review-output/worker-control-rehearsal"
OWNER = "track_subscription_entitlement"
ACTION = "assignDefaultFreeTrack.v1"
RESULT = "urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerResult"
ACL = "context/reconciliation/foundation-sql-draft-access.json"
SELECTED = ["P0C-TRACK-01", "P0C-EVIDENCE-01", "P0C-CTX-02"]
NS = uuid.UUID("ce494d76-d0c0-47f5-b9a8-6bfd3d4304fb")
INPUTS = ("scripts/prepare-customer-control-rehearsal.py", "scripts/prepare-worker-control-rehearsal.py", "scripts/test-worker-control-rehearsal.py", ACL,
          "review-output/foundation-application.review.sql", "prisma/review/foundation-candidate.prisma",
          "scripts/assemble-foundation-sql-review.py", "scripts/sql-review/foundation-verification.sql",
          "scripts/sql-review/foundation-invariants.sql", "scripts/sql-review/foundation-service-authority.sql",
          "context/reconciliation/foundation-sql-scope-policy.json", "context/reconciliation/database-candidate-tests.json",
          "contracts/database-review/foundation-payloads.v1.schema.json",
          "contracts/database-review/owner-mutation-evidence.v1.schema.json", "contracts/shared/SH-004.v1.schema.json",
          "contracts/shared/SH-114.v1.schema.json", "contracts/shared/types.v1.schema.json",
          "context/shared/contracts/SH-114.md", "context/reconciliation/platform-architecture-rulings.md",
          "context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-module-architecture.md",
          "context/clusters/identity, authority, & consent/Track Subscription & Entitlement Module/track-subscription-entitlement-implementation-plan.md",
          "context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-module-architecture.md",
          "context/clusters/identity, authority, & consent/Customer Buyer Profile Module/customer-buyer-profile-implementation-plan.md",
          "context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md",
          "context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-implementation-plan.md")


def uid(key): return str(uuid.uuid5(NS, key))
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def js(value): return quote(json.dumps(value, separators=(",", ":"))) + "::jsonb"
def digest(value): return "encode(sha256(convert_to(" + js(value) + "::text,'UTF8')),'hex')"
def sha(value): return hashlib.sha256(value).hexdigest()
def insert(table, values): return "INSERT INTO " + table + " (" + ",".join('"' + key + '"' for key in values) + ") VALUES (" + ",".join(values.values()) + ");"
def sql(lines): return "\n".join(lines) + "\n"


def customer_module(root):
    spec = importlib.util.spec_from_file_location("worker_customer_fixture_source", Path(root) / INPUTS[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capabilities(acl, role, objects, operations, revisions=None):
    """Finite source-register fields; @row is a separate UPDATE row gate."""
    result = set()
    for row in acl:
        model, verb = row["model"], row["operation"]
        if row["role"] != role or model not in objects or verb not in operations.get(model, ()):
            continue
        fields = row["fields"]
        if verb == "UPDATE":
            fields = operations[model][verb]
            if not set(fields) <= set(row["fields"]): raise ValueError("UPDATE exceeds original ACL")
            fields = ["@row"] + list(fields)
        for row_id in objects[model]:
            result.update(model + "/" + row_id + "/" + verb + "/" + field for field in fields)
    for model, values in (revisions or {}).items():
        for row_id, revision in values:
            result.add(model + "/" + row_id + "/revision/" + str(revision))
    if not result or any("*" in value for value in result): raise ValueError("empty/wildcard capabilities")
    return sorted(result)


def grant(name, login, owner, action, purpose, work, fields, source_generation, service=None, user=None):
    return {"id": uid("grant/" + name), "database_login_role": login, "owner_module_id": owner,
            "action": action, "purpose": purpose, "target_kind": "RuntimeWorkItem", "target_id": work,
            "principal_user_id": user, "service_principal": service, "source_generation": str(source_generation),
            "security_generation": "0", "allowed_fields": fields, "status": "NOT_RUN",
            "issuer_service": "wa_context_issuer", "policy_version": "worker-control-fixture.v1",
            "runtime_only": ["fresh 256-bit context secret and its SHA256 hash", "actual login/backend PID/xid tuple", "expires_at no later than 5 minutes"],
            "issuance_order": "Capture tuple on the actual restricted READ COMMITTED connection before protected reads; separate actual issuer INSERT+COMMIT; then bind on that same still-open connection. No SET ROLE."}


def build(root=ROOT):
    root = Path(root)
    acl = json.loads((root / ACL).read_text(encoding="utf8"))
    worker_acl = [row for row in acl if row["role"] == "wa_worker"]
    if len(worker_acl) != 32: raise ValueError("reviewed 32-row worker ACL ceiling changed")
    cm = customer_module(root)
    registry = cm.FixtureRegistry(root)
    for path in ("contracts/database-review/foundation-payloads.v1.schema.json", "contracts/database-review/owner-mutation-evidence.v1.schema.json"):
        doc = json.loads((root / path).read_text(encoding="utf8")); registry.documents[doc["$id"]] = doc
    source, source_sql, source_observe = cm.create_case("worker-source-customer", "valid", acl, registry)
    c, u, outbox = [source["ids"][key] for key in ("CustomerProfile", "user", "free")]
    ids = {key: uid(key) for key in ("work", "attempt", "command", "effect", "inbox", "plan", "definition", "benefit", "subscription", "selection", "grant", "history", "enrollment", "subscription-evidence", "selection-evidence", "grant-evidence", "identity-bootstrap", "identity-rotate", "identity-revoke", "identity-recover")}
    service = "worker-control-fixture.v1"
    semantic = source["fixture_values"]["free_command"]["semanticKey"]
    fingerprint = digest(source["fixture_values"]["free_command"])
    plan_version = "worker-control-synthetic.v1"
    plan_hash = sha(b"synthetic Customer Free catalog: one boolean benefit=true; not product policy")
    result = {"outcome": "enrolled", "selectionRevision": "0", "receipt": ids["enrollment"]}
    payload_doc = registry.documents["urn:workinants:database-review:foundation-payloads:v1"]
    if registry.errors(result, payload_doc["$defs"]["assignDefaultFreeTrackCustomerResult"], payload_doc): raise ValueError("invalid registered Track result")
    tables = {"RuntimeWorkItem": "platform.runtime_work_item", "RuntimeAttempt": "platform.runtime_attempt",
              "RuntimeCommandReceipt": "platform.runtime_command_receipt", "RuntimeEffectReceipt": "platform.runtime_effect_receipt",
              "RuntimeInboxReceipt": "platform.runtime_inbox_receipt", "TrackSubscription": "app.track_subscriptions",
              "TrackBaseSelection": "app.track_base_selection", "TrackEntitlementGrant": "app.track_entitlement_grants",
              "TrackSubscriptionEvent": "app.track_subscription_events", "TrackEnrollmentReceipt": "app.track_enrollment_receipt"}
    object_ids = {model: [ids[key]] for model, key in (("RuntimeWorkItem", "work"), ("RuntimeAttempt", "attempt"), ("RuntimeCommandReceipt", "command"),
                  ("RuntimeEffectReceipt", "effect"), ("RuntimeInboxReceipt", "inbox"), ("TrackPlan", "plan"), ("TrackEntitlementDefinition", "definition"),
                  ("TrackPlanEntitlement", "benefit"), ("TrackSubscription", "subscription"), ("TrackBaseSelection", "selection"),
                  ("TrackEntitlementGrant", "grant"), ("TrackSubscriptionEvent", "history"), ("TrackEnrollmentReceipt", "enrollment"))}
    object_ids.update(RuntimeOutboxMessage=[outbox], OwnerMutationEvidence=[ids[key] for key in ("subscription-evidence", "selection-evidence", "grant-evidence")])
    processing_ops = {model: {"SELECT": []} for model in object_ids}
    for model in ("RuntimeAttempt", "RuntimeCommandReceipt", "RuntimeEffectReceipt", "RuntimeInboxReceipt", "OwnerMutationEvidence",
                  "TrackSubscription", "TrackBaseSelection", "TrackEntitlementGrant", "TrackSubscriptionEvent", "TrackEnrollmentReceipt"):
        processing_ops[model]["INSERT"] = []
    processing_ops["RuntimeWorkItem"] = {"SELECT": [], "UPDATE": ["effectReceiptId", "state"]}
    processing_fields = capabilities(acl, "wa_worker", object_ids, processing_ops,
        {model: [(row_id, 1 if model in ("RuntimeWorkItem", "RuntimeEffectReceipt", "RuntimeAttempt") else 0) for row_id in object_ids[model]]
         for model in ("RuntimeWorkItem", "RuntimeEffectReceipt", "RuntimeAttempt", "TrackPlan", "TrackEntitlementDefinition", "TrackPlanEntitlement", "TrackSubscription", "TrackBaseSelection", "TrackEntitlementGrant")})
    processing_fields += ["CustomerProfile/" + c + "/revision/0", "RuntimeWorkItem/" + ids["work"] + "/effect/" + ids["effect"],
                          "RuntimeWorkItem/" + ids["work"] + "/command/" + ids["command"], "TrackPlan/" + ids["plan"] + "/version/" + plan_version,
                          "TrackPlan/" + ids["plan"] + "/contentHash/" + plan_hash]
    processing_fields = sorted(set(processing_fields))
    work_objects = {"RuntimeWorkItem": [ids["work"]]}
    schedule = grant("schedule", "wa_app_runtime", "platform_integration_owner", "runtime.schedule_work.v1", "work.schedule", ids["work"],
        capabilities(acl, "wa_app_runtime", work_objects, {"RuntimeWorkItem": {"INSERT": [], "SELECT": []}}, {"RuntimeWorkItem": [(ids["work"], 0)]}), 0, user=u)
    claim = grant("claim", "wa_worker", "platform_integration_owner", "runtime.claim_work.v1", "work.claim", ids["work"],
        capabilities(acl, "wa_worker", work_objects, {"RuntimeWorkItem": {"SELECT": [], "UPDATE": ["state", "fence", "leaseTokenHash", "leaseExpiresAt", "attemptCount"]}}, {"RuntimeWorkItem": [(ids["work"], 0)]}), 0, service=service)
    process = grant("process", "wa_worker", OWNER, ACTION, "default_free_enrollment", ids["work"], processing_fields, 1, service=service)
    currentness_fields = capabilities(acl, "wa_worker", work_objects, {"RuntimeWorkItem": {"SELECT": []}}, {"RuntimeWorkItem": [(ids["work"], 1)]})
    currentness_grants = {}
    for name, generation in (("baseline-current", 0), ("bound-before-rotate", 0), ("old-after-rotate", 0), ("fresh-after-rotate", 1),
                             ("bound-before-revoke", 1), ("revoked-current-generation", 2), ("old-after-recover", 1),
                             ("fresh-after-recover", 3), ("issuer-revocation", 3)):
        value = grant("currentness/" + name, "wa_worker", "platform_integration_owner", "runtime.claim_work.v1", "work.claim", ids["work"], currentness_fields, 1, service=service)
        value["security_generation"] = str(generation)
        value["operation_limit"] = "SELECT-only retained completed exact work at fence1; no claim/reclaim UPDATE token and no new work. Run only after enroll COMMIT/backend closure."
        currentness_grants[name] = value
    files = {"source-customer.sql": source_sql, "source-customer-observe.sql": source_observe}
    # Only deferred owner proof is bypassed for independent synthetic prerequisites.
    # Physical guards, FK/check constraints, RLS configuration and all worker guards stay installed.
    fixture_tables = ["app.users", "app.user_security_profiles", "app.track_plans", "app.track_entitlement_definitions", "app.track_plan_entitlements"]
    fixtures = ["-- TRUSTED INDEPENDENT SYNTHETIC FACTS ONLY; never owner runtime/effect proof.", "BEGIN;"]
    fixtures += ["ALTER TABLE " + table + " DISABLE TRIGGER owner_commit;" for table in fixture_tables]
    fixtures += [insert("app.users", {"id": quote(u), "is_public": "false", "revision": "0", "privacy_generation": "0", "created_at": "clock_timestamp()", "updated_at": "clock_timestamp()"}),
        insert("app.user_security_profiles", {"id": quote(uid("user-security")), "user_id": quote(u), "revision": "0", "security_generation": "0", "created_at": "clock_timestamp()", "updated_at": "clock_timestamp()"}),
        insert("app.track_plans", {"id": quote(ids["plan"]), "track": "'customer'", "key": "'worker-control-synthetic-free'", "name": "'Synthetic SQL test only'", "status": "'active'", "billing_model": "'free'", "version": quote(plan_version), "content_hash": quote(plan_hash), "updated_at": "clock_timestamp()"}),
        insert("app.track_entitlement_definitions", {"id": quote(ids["definition"]), "key": "'worker-control-synthetic-boolean'", "label": "'Synthetic SQL test only'", "value_type": "'boolean'", "track": "'customer'", "is_active": "true", "updated_at": "clock_timestamp()"}),
        insert("app.track_plan_entitlements", {"id": quote(ids["benefit"]), "plan_id": quote(ids["plan"]), "entitlement_id": quote(ids["definition"]), "value_type": "'boolean'", "boolean_value": "true", "updated_at": "clock_timestamp()"})]
    fixtures += ["ALTER TABLE " + table + " ENABLE TRIGGER owner_commit;" for table in reversed(fixture_tables)] + ["COMMIT;"]
    files["independent-fixtures.sql"] = sql(fixtures)
    files["fixture-guards-observe.sql"] = "SELECT jsonb_build_object('owner_guards_reenabled',(SELECT count(*)=5 AND bool_and(t.tgenabled='O') FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='app' AND c.relname IN ('users','user_security_profiles','track_plans','track_entitlement_definitions','track_plan_entitlements') AND t.tgname='owner_commit'),'no_project_user_trigger_disabled',NOT EXISTS(SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('app','platform','platform_private') AND NOT t.tgisinternal AND t.tgenabled<>'O'));\n"
    files["identity-bootstrap.sql"] = sql(["-- Actual separate wa_identity_service_authority login; synthetic authorization prerequisite only.", "BEGIN;",
        insert("platform_private.identity_service_receipt", {"id": quote(ids["identity-bootstrap"]), "service_principal": quote(service), "security_generation": "0", "transition": "'bootstrap'", "identity_authorization_ref": "'synthetic-worker-fixture-authorization.v1'"}),
        insert("platform_private.identity_service_authorization", {"service_principal": quote(service), "security_generation": "0", "identity_receipt_id": quote(ids["identity-bootstrap"])}), "COMMIT;"])
    files["schedule.sql"] = sql(["-- Actual bound wa_app_runtime; issuer already committed.", insert(tables["RuntimeWorkItem"], {"id": quote(ids["work"]), "outbox_message_id": quote(outbox), "handler_name": quote(ACTION), "semantic_work_key": quote(semantic), "state": "'pending'", "fence": "0", "attempt_count": "0"}), "SELECT 'WA_WORKER_SCHEDULE_READY';", "COMMIT;"])
    files["claim.sql"] = sql(["-- Actual bound wa_worker; 256-bit preimage is runtime memory only, never a stored hash used as secret.",
        "UPDATE platform.runtime_work_item SET state='leased',fence=fence+1,attempt_count=attempt_count+1,lease_token_hash=encode(sha256(decode(current_setting('wa.lease_secret'),'hex')),'hex'),lease_expires_at=clock_timestamp()+interval '2 minutes' WHERE id=" + quote(ids["work"]) + " AND fence=0 AND state='pending';",
        "SELECT 'WA_WORKER_CLAIM_READY';", "COMMIT;"])
    files["currentness-read.sql"] = "SELECT jsonb_build_object('visible_exact_work',count(*)) FROM platform.runtime_work_item WHERE id=" + quote(ids["work"]) + ";\n"
    files["identity-currentness-observe.sql"] = "SELECT jsonb_build_object('service_rows',(SELECT count(*) FROM platform_private.identity_service_authorization WHERE service_principal=" + quote(service) + "),'generation',(SELECT security_generation FROM platform_private.identity_service_authorization WHERE service_principal=" + quote(service) + "),'revoked',(SELECT revoked_at IS NOT NULL FROM platform_private.identity_service_authorization WHERE service_principal=" + quote(service) + "),'exact_receipt_link',EXISTS(SELECT 1 FROM platform_private.identity_service_authorization a JOIN platform_private.identity_service_receipt r ON r.id=a.identity_receipt_id AND r.service_principal=a.service_principal AND r.security_generation=a.security_generation AND r.revoked_at IS NOT DISTINCT FROM a.revoked_at AND r.mutation_transaction_id=a.mutation_transaction_id WHERE a.service_principal=" + quote(service) + "));\n"
    snapshots = {"TrackSubscription": {"id": ids["subscription"], "userId": u, "track": "customer", "status": "active", "provider": "none", "revision": "0"},
                 "TrackEntitlementGrant": {"id": ids["grant"], "userId": u, "track": "customer", "status": "active", "valueType": "boolean", "revision": "0"},
                 "TrackBaseSelection": {"id": ids["selection"], "userId": u, "track": "customer", "customerProfileId": c, "candidateProfileId": None, "professionalProfileId": None, "subscriptionId": ids["subscription"], "revision": "0", "sourceGeneration": "0"}}
    evidence = {model: {"schema": "database-owner-evidence.v1", "owner": OWNER, "model": model, "primaryKey": {"id": snap["id"]}, "prior": None, "committed": snap, "decisionRef": "worker-control-fixture.v1"} for model, snap in snapshots.items()}
    evidence_doc = registry.documents["urn:workinants:database-review:owner-evidence:v1"]
    for model, value in evidence.items():
        if registry.errors(value, evidence_doc["$defs"][model], evidence_doc): raise ValueError("invalid evidence: " + model)
    typed_profile = {"user_id": quote(u), "track": "'customer'", "customer_profile_id": quote(c), "candidate_profile_id": "NULL", "professional_profile_id": "NULL"}
    lines = ["-- Actual wa_worker, new tuple-bound processing grant, same connection/xid through COMMIT.", "SET LOCAL wa.fence='1';",
        insert(tables["RuntimeCommandReceipt"], {"id": quote(ids["command"]), "owner_module_id": quote(OWNER), "operation": quote(ACTION), "subject_scope": quote("CustomerProfile:" + c), "semantic_key": quote(semantic), "fingerprint": fingerprint, "state": "'committed'", "source_revision": "0", "result_schema_id": quote(RESULT), "result_schema_version": "'1'", "result_digest": digest(result), "result_body": js(result)}),
        insert(tables["RuntimeEffectReceipt"], {"id": quote(ids["effect"]), "command_receipt_id": quote(ids["command"]), "owner_module_id": quote(OWNER), "operation": quote(ACTION), "subject_scope": quote("CustomerProfile:" + c), "semantic_effect_key": quote(semantic), "fingerprint": fingerprint, "state": "'committed'", "source_revision": "0", "fence": "1", "result_schema_id": quote(RESULT), "result_hash": digest(result), "committed_at": "clock_timestamp()"}),
        insert(tables["RuntimeInboxReceipt"], {"id": quote(ids["inbox"]), "outbox_message_id": quote(outbox), "consumer_owner": quote(OWNER), "handler_name": quote(ACTION), "payload_hash": fingerprint, "effect_receipt_id": quote(ids["effect"])}),
        "UPDATE platform.runtime_work_item SET effect_receipt_id=" + quote(ids["effect"]) + " WHERE id=" + quote(ids["work"]) + " AND fence=1 AND state='leased' AND effect_receipt_id IS NULL;",
        "SELECT 'WA_WORKER_EFFECT_LINKED';",
        insert(tables["TrackSubscription"], {"id": quote(ids["subscription"]), **typed_profile, "plan_id": quote(ids["plan"]), "status": "'active'", "provider": "'none'"}),
        insert(tables["TrackBaseSelection"], {"id": quote(ids["selection"]), **typed_profile, "subscription_id": quote(ids["subscription"]), "source_generation": "0"}),
        insert(tables["TrackSubscriptionEvent"], {"id": quote(ids["history"]), "subscription_id": quote(ids["subscription"]), "plan_id": quote(ids["plan"]), "user_id": quote(u), "name": "'synthetic-default-free-enrolled.v1'", "from_status": "NULL", "to_status": "'active'", "provider": "'none'"}),
        insert(tables["TrackEntitlementGrant"], {"id": quote(ids["grant"]), **typed_profile, "subscription_id": quote(ids["subscription"]), "entitlement_id": quote(ids["definition"]), "status": "'active'", "value_type": "'boolean'", "boolean_value": "true", "starts_at": "clock_timestamp()", "source_plan_id": quote(ids["plan"]), "source_event_id": quote(ids["history"])}),
        insert(tables["TrackEnrollmentReceipt"], {"id": quote(ids["enrollment"]), "user_id": quote(u), "track": "'customer'", "profile_id": quote(c), "source_owner": "'customer_buyer_profile'", "source_creation_revision": "0", "selection_id": quote(ids["selection"]), "selection_revision": "0", "semantic_key": quote(semantic), "fingerprint": fingerprint, "result_code": "'enrolled'", "effect_receipt_id": quote(ids["effect"])})]
    for model, key in (("TrackSubscription", "subscription-evidence"), ("TrackBaseSelection", "selection-evidence"), ("TrackEntitlementGrant", "grant-evidence")):
        lines.append(insert("platform.owner_mutation_evidence", {"id": quote(ids[key]), "command_receipt_id": quote(ids["command"]), "owner_module_id": quote(OWNER), "aggregate_kind": quote(model), "aggregate_id": quote(snapshots[model]["id"]), "committed_revision": "0", "action": quote(ACTION), "decision_ref": "'worker-control-fixture.v1'", "evidence_schema_id": quote("urn:workinants:database-review:owner-evidence:v1#/$defs/" + model), "evidence_schema_version": "'1'", "evidence_digest": digest(evidence[model]), "evidence_body": js(evidence[model])}))
    lines += [insert(tables["RuntimeAttempt"], {"id": quote(ids["attempt"]), "work_item_id": quote(ids["work"]), "attempt_number": "1", "fence": "1", "worker_id": quote(service), "result": "'committed'", "reason_code": "'synthetic-worker-control-enrolled'", "started_at": "clock_timestamp()-interval '1 millisecond'", "finished_at": "clock_timestamp()"}),
        "UPDATE platform.runtime_work_item SET state='completed' WHERE id=" + quote(ids["work"]) + " AND fence=1 AND state='leased' AND effect_receipt_id=" + quote(ids["effect"]) + ";",
        "SELECT 'WA_WORKER_GROUP_STAGED';", "SET CONSTRAINTS ALL IMMEDIATE;", "SELECT 'WA_WORKER_CONSTRAINTS_CHECKED';", "COMMIT;"]
    files["enroll.sql"] = sql(lines)
    direct = []
    for model, snap in snapshots.items():
        direct.append("SELECT jsonb_build_object('model'," + quote(model) + ",'exact_reverse',platform_private.worker_evidence_source_matches(" + quote(model) + "," + quote(snap["id"]) + ",0,pg_current_xact_id()::text," + js(snap) + "),'wrong_xid',platform_private.worker_evidence_source_matches(" + quote(model) + "," + quote(snap["id"]) + ",0,'0'," + js(snap) + "));" )
    files["in-transaction-reverse-probes.sql"] = sql(["-- Insert before SET CONSTRAINTS on the original worker connection only; exact=true/wrong_xid=false."] + direct)
    # Independent observer emits only fixed counts/Boolean facts, never bodies, handles or arbitrary errors.
    counts = {model: "(SELECT count(*) FROM " + table + " WHERE id=" + quote(object_ids[model][0]) + ")" for model, table in tables.items()}
    coherent = ["q.result_body=" + js(result), "q.result_digest=encode(sha256(convert_to(q.result_body::text,'UTF8')),'hex')", "q.result_schema_id=" + quote(RESULT), "q.state='committed'", "q.owner_module_id=" + quote(OWNER), "q.operation=" + quote(ACTION), "q.subject_scope=" + quote("CustomerProfile:" + c), "q.semantic_key=" + quote(semantic), "q.source_revision=0", "q.result_schema_version='1'", "e.owner_module_id=q.owner_module_id", "e.operation=q.operation", "e.subject_scope=q.subject_scope", "e.semantic_effect_key=q.semantic_key", "e.source_revision=0", "e.result_hash=q.result_digest", "e.result_schema_id=q.result_schema_id", "e.command_receipt_id=q.id", "e.state='committed'", "e.fence=1", "e.fingerprint=q.fingerprint", "q.fingerprint=o.payload_hash", "o.id=" + quote(outbox), "o.payload_hash=encode(sha256(convert_to(o.payload::text,'UTF8')),'hex')", "o.command_receipt_id=" + quote(source["ids"]["RuntimeCommandReceipt"]), "w.handler_name=" + quote(ACTION), "w.state='completed'", "w.fence=1", "w.attempt_count=1", "w.effect_receipt_id=e.id", "w.outbox_message_id=o.id", "w.semantic_work_key=q.semantic_key", "i.consumer_owner=q.owner_module_id", "i.handler_name=q.operation", "i.effect_receipt_id=e.id", "i.outbox_message_id=o.id", "i.payload_hash=o.payload_hash", "s.id=b.subscription_id", "s.plan_id=" + quote(ids["plan"]), "s.user_id=b.user_id", "s.user_id=" + quote(u), "s.customer_profile_id=b.customer_profile_id", "s.customer_profile_id=" + quote(c), "s.track='customer'", "b.track=s.track", "s.provider='none'", "s.provider_customer_id IS NULL", "s.provider_subscription_id IS NULL", "s.provider_price_id IS NULL", "s.current_period_start IS NULL", "s.current_period_end IS NULL", "s.ended_at IS NULL", "s.candidate_profile_id IS NULL", "s.professional_profile_id IS NULL", "b.candidate_profile_id IS NULL", "b.professional_profile_id IS NULL", "s.status='active'", "s.revision=0", "b.revision=0", "b.source_generation=0", "r.selection_id=b.id", "r.selection_revision=b.revision", "r.effect_receipt_id=e.id", "r.user_id=b.user_id", "r.track=b.track", "r.source_owner='customer_buyer_profile'", "r.source_creation_revision=0", "r.profile_id=b.customer_profile_id", "r.fingerprint=q.fingerprint", "r.semantic_key=q.semantic_key", "r.result_code='enrolled'", "q.result_body->>'receipt'=r.id::text", "q.result_body->>'selectionRevision'=r.selection_revision::text", "q.result_body->>'outcome'=r.result_code", "h.subscription_id=s.id", "h.plan_id=s.plan_id", "h.user_id=s.user_id", "h.from_status IS NULL", "h.to_status='active'", "h.provider='none'", "a.work_item_id=w.id", "a.attempt_number=1", "a.fence=1", "a.worker_id=" + quote(service), "a.result='committed'", "g.subscription_id=s.id", "g.user_id=s.user_id", "g.customer_profile_id=s.customer_profile_id", "g.candidate_profile_id IS NULL", "g.professional_profile_id IS NULL", "g.track='customer'", "g.status='active'", "g.revision=0", "g.expires_at IS NULL", "g.revoked_at IS NULL", "g.entitlement_id=" + quote(ids["definition"]), "g.source_plan_id=s.plan_id", "g.source_event_id=h.id", "g.value_type='boolean'", "g.boolean_value=true", "g.int_value IS NULL", "g.decimal_value IS NULL", "g.string_value IS NULL", "g.json_value IS NULL"]
    for alias in ("e", "i", "w", "s", "b", "r", "h", "g", "a"): coherent.append(alias + ".mutation_transaction_id=q.mutation_transaction_id")
    query = "EXISTS(SELECT 1 FROM platform.runtime_command_receipt q,platform.runtime_effect_receipt e,platform.runtime_work_item w,platform.runtime_outbox_message o,platform.runtime_inbox_receipt i,app.track_subscriptions s,app.track_base_selection b,app.track_enrollment_receipt r,app.track_subscription_events h,app.track_entitlement_grants g,platform.runtime_attempt a WHERE "
    aliases = {"q": "command", "e": "effect", "w": "work", "i": "inbox", "s": "subscription", "b": "selection", "r": "enrollment", "h": "history", "g": "grant", "a": "attempt"}
    query += " AND ".join(alias + ".id=" + quote(ids[key]) for alias, key in aliases.items()) + " AND " + " AND ".join(coherent) + ")"
    evidence_checks = []
    for model, key in (("TrackSubscription", "subscription-evidence"), ("TrackBaseSelection", "selection-evidence"), ("TrackEntitlementGrant", "grant-evidence")):
        evidence_checks.append("EXISTS(SELECT 1 FROM platform.owner_mutation_evidence v JOIN platform.runtime_command_receipt q ON q.id=v.command_receipt_id WHERE v.id=" + quote(ids[key]) + " AND q.id=" + quote(ids["command"]) + " AND v.evidence_body=" + js(evidence[model]) + " AND v.evidence_digest=encode(sha256(convert_to(v.evidence_body::text,'UTF8')),'hex') AND v.mutation_transaction_id=q.mutation_transaction_id AND v.previous_revision IS NULL AND v.committed_revision=0)")
    files["enroll-observe.sql"] = "SELECT jsonb_build_object(" + ",".join(quote(key) + "," + value for key, value in counts.items()) + ",'coherent'," + query + ",'exact_evidence',(" + " AND ".join(evidence_checks) + "),'evidence_count',(SELECT count(*) FROM platform.owner_mutation_evidence WHERE command_receipt_id=" + quote(ids["command"]) + "));\n"
    for step, previous, generation in (("rotate", "bootstrap", 1), ("revoke", "rotate", 2), ("recover", "revoke", 3)):
        revoked = "clock_timestamp()" if step == "revoke" else "NULL"
        current_revoked = "(SELECT revoked_at FROM platform_private.identity_service_receipt WHERE id=" + quote(ids["identity-" + step]) + ")"
        files["identity-" + step + ".sql"] = sql(["-- Separate actual Identity service login; exact previous receipt, fixture-only upstream authorization.", "BEGIN;",
            insert("platform_private.identity_service_receipt", {"id": quote(ids["identity-" + step]), "service_principal": quote(service), "previous_generation": str(generation - 1), "previous_receipt_id": quote(ids["identity-" + previous]), "security_generation": str(generation), "transition": quote(step), "revoked_at": revoked, "identity_authorization_ref": quote("synthetic-worker-fixture-" + step + ".v1")}),
            "UPDATE platform_private.identity_service_authorization SET security_generation=" + str(generation) + ",identity_receipt_id=" + quote(ids["identity-" + step]) + ",revoked_at=" + current_revoked + " WHERE service_principal=" + quote(service) + " AND security_generation=" + str(generation - 1) + " AND identity_receipt_id=" + quote(ids["identity-" + previous]) + ";", "COMMIT;"])
    scope_observers = ["app.track_plans", "app.track_entitlement_definitions", "app.track_plan_entitlements", "app.track_usage_events", "app.track_usage_counters", "app.track_usage_reservation"]
    files["catalog-usage-fingerprint.sql"] = "SELECT jsonb_build_object(" + ",".join(quote(table) + ",(SELECT jsonb_build_object('count',count(*),'sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY x.id),'[]'::jsonb)::text,'UTF8')),'hex')) FROM " + table + " x)" for table in scope_observers) + ");\n"
    control_tests = json.loads((root / "context/reconciliation/database-candidate-tests.json").read_text(encoding="utf8"))["tests"]
    source_definitions = [deepcopy(row) for row in control_tests if row["id"] in SELECTED]
    if {row["id"] for row in source_definitions} != set(SELECTED): raise ValueError("selected source IDs missing")
    scenarios = [
        {"name": "one-complete-default-free", "control_ids": ["P0C-TRACK-01", "P0C-EVIDENCE-01"], "vectors": ["LEASE-ATTACH", "WORKER-REVERSE-PROOF", "EVIDENCE-CODEC"], "steps": ["independent fixture setup+guard verification", "restricted source-customer.sql + independent coherent source observation", "separate Identity fixture bootstrap", "actual app scheduler grant+schedule.sql", "actual worker claim grant+claim.sql", "new actual worker processing grant+enroll.sql with same connection lease preimage and fence1", "in-transaction-reverse-probes.sql before SET CONSTRAINTS", "COMMIT acknowledgement, close backend, independent full observer+unchanged catalog/usage+guard checks"], "expected_commit": True, "sql": "enroll.sql", "observer": "enroll-observe.sql", "grant": process},
        {"name": "direct-source-snapshot-controls", "control_ids": ["P0C-TRACK-01", "P0C-EVIDENCE-01"], "vectors": ["DIRECT-TRACK-SNAPSHOT", "WORKER-REVERSE-PROOF"], "prepared_sql": "in-transaction-reverse-probes.sql", "coverage_limit": "Three reverse-proof positive/wrong-xid branches only; every exposed Boolean branch, base-selection UPDATE and complete foreign snapshots remain separately NOT_RUN. Do not count false malformed calls as complete adversarial coverage."},
        {"name": "worker-service-currentness", "control_ids": ["P0C-CTX-02"], "vectors": ["SERVICE-REVOKE"], "steps": ["after enrollment COMMIT/backend closure, use baseline-current fence1/generation0 SELECT-only grant: currentness-read.sql returns visible_exact_work1, then close that control backend", "A fresh actual worker READ COMMITTED transaction, capture tuple; issuer COMMIT bound-before-rotate exact SELECT-only grant; A binds only (no protected read/action/source lock)", "independent Identity rotate COMMIT generation0->1; A next currentness-read.sql must return visible_exact_work0 and mutate0; close A", "old-after-rotate grant cannot bind; fresh-after-rotate generation1 grant returns visible_exact_work1 then closes", "repeat separate A bound-before-revoke with service revoke generation1->2; zero disclosure/mutation; revoked-current-generation2 cannot bind", "recover generation2->3 using exact predecessor receipt; fresh-after-recover generation3 grant returns visible_exact_work1; old-after-recover generation1 cannot bind"], "grants": currentness_grants, "read_sql": "currentness-read.sql", "identity_observer": "identity-currentness-observe.sql", "binding_denial_allowlist": {"sqlstate": "42501", "exact_message": "invalid, stale or unsupported context", "source_function": "platform_private.bind_request_context"}, "synchronization": "Identity transition COMMIT must finish before A's first protected statement. No lock-held wait/sleep or privileged row update substitutes.", "identity_upstream_limit": "Only specialized Identity SQL transition/currentness is exercised; synthetic authorization refs do not qualify real Identity authorization.", "read_columns": next(row["columns"] for row in worker_acl if row["model"] == "RuntimeWorkItem" and row["operation"] == "SELECT")},
        {"name": "worker-grant-revocation", "control_ids": ["P0C-CTX-02"], "grant": currentness_grants["issuer-revocation"], "read_sql": "currentness-read.sql", "steps": ["after Identity recovery generation3, A same tuple issuance/bind-only as service currentness using issuer-revocation SELECT-only grant", "R actual issuer UPDATE only its own exact grant revoked_at NULL->clock_timestamp then COMMIT", "A original context next exact work SELECT returns0; original persisted work unchanged; close A before independent observer"], "expected": "Exact forbidden disclosure/mutation absent, separately committed issuer revocation retained."},
        {"name": "worker-source-generation", "control_ids": ["P0C-CTX-02"], "execution_dependencies": ["CUSTOMER_UPDATE_RECEIPT_NO_RESULT_IDENTITY_AND_CODEC_NOT_REGISTERED"], "runtime_eligibility": "BLOCKED_OWNER_SOURCE_MUTATION_RESULT", "expected": "Actual Customer owner update must COMMIT with its own fresh grant, CAS/history/evidence/one event before A's first protected read; no privileged revision edits."},
        {"name": "worker-user-security-generation", "control_ids": ["P0C-CTX-02"], "execution_dependencies": ["IDENTITY_USER_SECURITY_PROFILE_OWNER_TRANSITION_RESULT_NOT_REGISTERED"], "runtime_eligibility": "BLOCKED_OWNER_SOURCE_MUTATION_RESULT", "expected": "UserSecurityProfile mutation is not substituted for the worker service-principal currentness protocol."}]
    for case in scenarios:
        case["status"] = "NOT_RUN"
        case.setdefault("runtime_eligibility", "PENDING_INDEPENDENT_PACKET_AND_WRAPPER_REVIEW")
        case.setdefault("execution_dependencies", ["FRESH_EXACT_DISPOSABLE_TARGET", "AUTH_PREFLIGHT_ALL_RESTRICTED_LOGINS", "EXACT_SOURCE_AND_NATIVE_CATALOG_PARITY", "SOURCE_CUSTOMER_RESTRICTED_CREATION_PROOF", "FIXTURE_GUARDS_REENABLED", "ROOT_REVIEWED_FINITE_EXECUTION_WRAPPER"])
    manifest = {"schema": "workinants.worker-control-fixtures.v1", "status": "NOT_RUN", "database_posture": "D", "database_contacted": False, "sql_executed": False,
        "selected_control_ids": SELECTED, "source_control_definitions": source_definitions, "ids": ids, "source_customer": source, "semantic_key": semantic,
        "source_files_sha256": {path: sha((root / path).read_bytes()) for path in INPUTS}, "worker_acl_ceiling_rows": worker_acl,
        "worker_acl_ceiling_sha256": sha(json.dumps(worker_acl, sort_keys=True, separators=(",", ":")).encode()),
        "grants": {"source_customer": source["grant"], "schedule": schedule, "claim": claim, "process": process},
        "fixture_values": {"result": result, "evidence": evidence, "plan_version": plan_version, "plan_hash": plan_hash, "service_principal": service},
        "fixture_conventions_requiring_review": {"wire_result_receipt": "For this synthetic SQL-only experiment receipt equals the actual TrackEnrollmentReceipt.id; owner contract does not normatively choose command-versus-enrollment ID. Observer checks this explicit fixture convention; no owner/API mapping qualification is claimed.", "event_name": "synthetic-default-free-enrolled.v1 is a test history label; no new registered outbound event is emitted.", "approved_catalog": "The hash identifies a single synthetic boolean=true benefit; not approved product pricing/catalog publication."},
        "setup_bypasses": [{"table": table, "exact_trigger": "owner_commit", "status": "NOT_RUN", "reason": "Seed independent synthetic prerequisite only; all other triggers/constraints remain enabled", "restore": "ENABLE TRIGGER owner_commit before COMMIT; independently require exact5 present+O and zero disabled project user triggers before restricted source or worker cases"} for table in fixture_tables],
        "finite_caps": {"jobs": 1, "source_customer_creation_groups": 1, "worker_claims": 1, "worker_processing_transactions": 1, "business_enrollments": 1, "lease_seconds": 120, "grant_seconds_max": 300, "identity_transitions": ["bootstrap", "rotate", "revoke", "recover"], "polling_or_worker_loop": False,
                        "wrapper_timeouts_required_ms": {"statement_timeout": 5000, "lock_timeout": 1000, "idle_in_transaction_session_timeout": 30000}},
        "scenarios": scenarios, "positive_observer_expected": {**{model: 1 for model in tables}, "coherent": True, "exact_evidence": True, "evidence_count": 3},
        "mandatory_unprepared_vectors": [{"vector": vector, "control_id": control, "status": "NOT_RUN", "reason": reason} for vector, control, reason in [
            ("LEASE-RENEW", "P0C-TRACK-01", "Separate exact renew/reclaim/concurrent-higher-fence statement plan required; no elapsed-expiry success invented."),
            ("LEASE-RECOVERY", "P0C-TRACK-01", "Needs a retained committed effect followed by controlled higher-fence reclaim; not the one-success path."),
            ("FULL-DIRECT-TRACK-SNAPSHOT", "P0C-TRACK-01", "Every exposed branch and complete foreign/minus-cap snapshots require separately reviewed SQL variants."),
            ("BASE-SELECTION-UPDATE", "P0C-EVIDENCE-01", "Needs authentic noncurrent prior selection and exact previous evidence; no direct worker grants widened."),
            ("ALL-EVIDENCE-NEGATIVES", "P0C-EVIDENCE-01", "Wrong enum/PK/revision/extra keys and source-transaction variants require exact diagnostic+marker/full rollback observers, not generic P0001 acceptance.")]],
        "preserved_gates": ["P0E_TRACK_APP_PROFILE_AND_PLAN_FACT_PORT", "P0D_TRACK_USAGE_PERIOD_RECONCILIATION", "P0F_PRIVACY_INSTRUCTION_DISPOSITION_AND_RESTORE_PORTS", "NO_WORKER_RESERVATION_ROUTE", "NO_APP_WORKER_ENROLLMENT_OR_HISTORY_BYPASS"],
        "failure_contract": "Stop this and all later behavioral scenarios on unexpected result. Persist only completed stage names, allowlisted comparison Booleans/counts/SQLSTATE+exact source diagnostic class and safe failure class. Close the affected operation backend before observations. No passwords, handles, raw stderr, raw probe dictionaries, statement bodies or lease preimages in evidence. Retain controlled cleanup identity and exact resource ownership boundaries.",
        "qualification_limits": ["Source proposal only: every dependency/case remains NOT_RUN; no selected control or94/451 promotion.", "Independent fixture facts never establish real owner authorization/catalog publication or source/worker behavior.", "Actual app source creation, app schedule, worker claim and worker enrollment must happen through their actual restricted logins; privileged observers cannot provide these proofs.", "No canonical SQL/fixtures/ACL/source packet edits, usage writes, Privacy execution, provider calls, P0-D adapter, normal network delivery or deployment."]}
    files["README.md"] = """Bounded worker-control source proposal — every runtime case NOT_RUN

This packet proposes one real restricted Customer creation, one actual app
scheduler insert, one actual worker claim and one actual worker enrollment.
It creates no worker loop and implements no owner/API adapter. Posture D stays.

Root must independently review every input/output hash, the wrapper, target,
authentication, exact32 worker ACL rows and native catalog before any operation.
No SQL is executed by the generator or its tests. All SQL is dormant source.

Independent setup only disables the five exact owner_commit triggers named in
fixtures.json. It leaves physical/typed/FK/worker guards installed, re-enables
those exact triggers before COMMIT and requires independent presence+enabled
verification. On any setup failure the wrapper must close/rollback that setup
connection and prove restored trigger state; never assume restoration occurred.
Setup never inserts a Customer source/outbox or a Track enrollment/history.

Do not reuse a context handle or PID/xid tuple. Every restricted operation opens
READ COMMITTED, captures its actual login/backend/xid, waits for a separately
committed issuer grant, binds on that same connection, and finishes or closes
before independent observations. Lease preimages/context secrets remain runtime
memory only. Require row-count1 for schedule/claim/link/complete/Identity updates,
per-statement markers, actual SET CONSTRAINTS and COMMIT acknowledgement.

The positive worker writes one closed assignDefaultFreeTrack result body and a
non-NULL PostgreSQL jsonb storage digest. Its receipt=enrollment-receipt-ID mapping
and history label are explicit synthetic conventions, not normative owner/API
mapping certification. The independent observer checks actual result/revision/
receipt/effect/inbox/source/state coherence and all same-transaction groups.

Run reverse proof queries before SET CONSTRAINTS on the original worker backend.
Only the three prepared exact/wrong-xid branches are covered by that draft.
The unprepared foreign-source, lease renew/recovery, base-selection UPDATE and
all evidence-negative variants remain explicit NOT_RUN obligations. They cannot
be reported as PASS from successful counts or a generic denied call.

Currentness is ordered after the positive worker closes at retained fence1.
Fresh SELECT-only grants pin that fence and the declared service generation.
Bind the stale session before the separate Identity transition; make its first
protected read only after that transition COMMITs. Fresh controls return one
safe count; stale/revoked controls return zero or the exact allowlisted binder
failure. Never disclose the readable stored lease hash in retained evidence.
Fixture Identity authorization references qualify no upstream owner adapter.

Customer source-generation and UserSecurityProfile owner generation mutations
remain blocked by missing registered owner result/receipt contracts. Usage,
Privacy and application Track prerequisite-port gates remain in force. No
privileged data edit, SQL NULL digest or borrowed SH-114 result may bypass them.

Any unexpected result stops all subsequent behavioral cases, retains sanitized
partial stage/comparison evidence, closes the affected backend before observer
queries, and follows root's reviewed exact-resource cleanup wrapper. Nothing in
this packet changes the resource/image/cleanup authority of that wrapper.

Plain English: We prepare one small job. The real worker must do its own work
with its own limited key. Setup facts are pretend facts, never pretend success.
Missing owner forms stay missing, and every test stays unrun until reviewed.
"""
    manifest["prepared_files_sha256"] = {name: sha(value.encode("utf8")) for name, value in files.items()}
    manifest["packet_digest_recipe"] = "SHA256 of UTF8 json.dumps({'source_files_sha256': source_files_sha256, 'prepared_files_sha256': prepared_files_sha256},sort_keys=True,separators=(',',':')); fixtures.json excluded to avoid self-reference"
    manifest["source_only_packet_sha256"] = sha(json.dumps({key: manifest[key] for key in ("source_files_sha256", "prepared_files_sha256")}, sort_keys=True, separators=(",", ":")).encode("utf8"))
    files["fixtures.json"] = json.dumps(manifest, indent=2) + "\n"
    return files, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    files, manifest = build()
    if args.prepare:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, value in files.items():
            with (OUT / name).open("x", encoding="utf8", newline="\n") as handle: handle.write(value)
    print(json.dumps({"status": "PREPARED_NOT_RUN" if args.prepare else "PLAN_ONLY_NOT_RUN", "files": len(files), "scenarios": len(manifest["scenarios"]), "worker_acl_rows": len(manifest["worker_acl_ceiling_rows"]), "database_contacted": False}))


if __name__ == "__main__": main()
