"""Build the selected F0 assertion inventory from local source, never a database.

This is a coverage plan, not a test runner or a substitute for owner contracts.
It preserves all 94 selected case IDs. Every new assertion starts NOT_RUN, even
when an earlier packet has evidence for a similar assertion. A declared ALLOW
without a complete path remains visible; no denial is relabeled a positive.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "context/reconciliation/local-f0-assertions.json"
INPUTS = (
    "context/reconciliation/database-candidate-corrections-first-replay-selection.json",
    "context/reconciliation/database-candidate-tests.json",
    "context/reconciliation/database-candidate-access-matrix.json",
    "context/reconciliation/foundation-sql-draft-replay-map.json",
    "context/reconciliation/foundation-sql-draft-access.json",
    "context/reconciliation/foundation-sql-draft-models.json",
    "context/reconciliation/foundation-sql-scope-policy.json",
    "context/reconciliation/foundation-sql-verifier-access.json",
    "context/reconciliation/database-candidate-migration-plan.md",
    "prisma/review/foundation-candidate.prisma",
    "contracts/database-review/owner-mutation-evidence.v1.schema.json",
    "review-output/foundation-structure.sql",
    "review-output/foundation-bootstrap.review.sql",
    "review-output/foundation-bootstrap-finalize.review.sql",
    "review-output/foundation-application.review.sql",
    "scripts/prepare-local-f0-assertions.py",
)


def read(path):
    return (ROOT / path).read_text(encoding="utf8")


def data(path):
    return json.loads(read(path))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def normalized_name(name):
    return name.replace('"', "")


def guard_inventory(sql):
    """Identify concrete generated trigger/function source, without SQL execution."""
    identifier = r'(?:"[^"]+"|[a-z_][a-z_0-9]*)'
    qualified = identifier + r'\.' + identifier
    functions = {}
    pattern = re.compile(
        r"CREATE\s+FUNCTION\s+(" + qualified + r")\s*\(.*?\)\s+RETURNS\b.*?"
        r"\bAS\s+(\$[a-z_0-9]*\$)(.*?)\2\s*;", re.I | re.S,
    )
    for match in pattern.finditer(sql):
        functions[normalized_name(match[1])] = {
            "source_line": sql.count("\n", 0, match.start()) + 1,
            "body_sha256": hashlib.sha256(match[3].encode("utf8")).hexdigest(),
        }
    triggers = {}
    pattern = re.compile(
        r"CREATE\s+(CONSTRAINT\s+)?TRIGGER\s+(" + identifier + r")\s+"
        r"([^;]*?)\bON\s+(" + qualified + r")\s+([^;]*?)"
        r"\bEXECUTE\s+FUNCTION\s+(" + qualified + r")\s*\([^;]*\)\s*;",
        re.I | re.S,
    )
    for match in pattern.finditer(sql):
        function = normalized_name(match[6])
        assert function in functions, "Trigger function source missing: " + function
        triggers.setdefault(normalized_name(match[4]), []).append({
            "trigger": normalized_name(match[2]),
            "function": function,
            "constraint_trigger": bool(match[1]),
            "initially_deferred": "INITIALLY DEFERRED" in match[5].upper(),
            "source_line": sql.count("\n", 0, match.start()) + 1,
            "function_source": functions[function],
        })
    return triggers


def assertion(identifier, outcome, expectation, availability="CANDIDATE_LOCAL_SQL_PATH",
              dependencies=(), **details):
    return {
        "id": identifier,
        "mandatory_for_case": True,
        "expected_outcome": outcome,
        "expected_assertion": expectation,
        "availability": availability,
        "dependency_ids": list(dependencies),
        "status": "NOT_RUN",
        **details,
    }


# These are the existing fourteen control cases, expanded into separately
# observable obligations. Existing register vectors are also retained below.
CONTROL_ASSERTIONS = {
    "P0C-INSTALL-01": (
        ("empty_deploy", "Actual pinned Prisma deploy applies the single integrated history from empty application state as wa_migrator; bootstrap/finalization stay separate."),
        ("private_ledger", "Actual public._prisma_migrations is migrator-owned/private; successful migration name, file checksum, finished state and applied-step evidence match the reviewed history."),
        ("second_deploy", "A genuine second Prisma deployment has no pending migration, unchanged applied checksums and no duplicate objects or application DDL changes."),
        ("success_cleanup", "After successful install connection closes, original grantor finalizes; temporary memberships and leaf CREATE privileges are independently zero."),
    ),
    "P0C-INSTALL-02": (
        ("intended_failure", "Prisma applies a recorded immutable failure-history snapshot; the intended injected database failure is distinguished from connection/parser/permission failures."),
        ("failed_ledger", "The genuine Prisma ledger retains its failed migration record/checksum while all transactional application objects roll back."),
        ("failed_cleanup", "Original grantor cleanup runs after failure; no active install connection, temporary membership or leaf CREATE remains."),
        ("recovery", "Only after exact rollback/catalog verification, use the reviewed pinned migration recovery command; retain failure history, deploy reviewed valid bytes and prove the recovered ledger and second no-op deploy."),
        ("immutable_applied_history", "Never edit an applied migration/checksum, mark absent objects applied, reset, db push or directly manipulate the ledger."),
    ),
    "P0C-CATALOG-01": tuple((name, text) for name, text in (
        ("relations_columns", "Exact 40 models plus two private Identity relations; names, ordered columns, native types, defaults and nullability match expected source."),
        ("enums", "Enum namespaces and ordered labels match the approved structural source."),
        ("constraints", "PK/unique/FK/CHECK constraints, FK actions, validation and deferral match; no missing or extra semantic constraint."),
        ("indexes", "Index expressions, uniqueness, predicates and validity match the reviewed source."),
        ("functions", "Every signature, normalized body/hash, owner, definer/invoker mode, search_path and EXECUTE ACL matches."),
        ("triggers", "Trigger events/timing/row mode, constraint deferral, target function and enabled state match."),
        ("views", "Any expected view, its definition, owner, ACL and security_invoker setting match; unexpected views reject."),
        ("roles_memberships", "Actual login/inherit/superuser/BYPASSRLS/DDL flags and exact memberships match; no runtime/helper/issuer owner escalation."),
        ("all_acl_levels", "Schema/table/COLUMN/sequence/function/type/default privileges match, including the private Prisma-ledger exception."),
        ("rls_policies", "ENABLE/FORCE RLS and all USING/WITH CHECK expressions, roles and commands match, not merely policy counts."),
        ("extensions", "Only independently recorded native/extension prerequisites exist; local provider simulations and hosted-parity exclusions are explicit."),
        ("visibility", "Unknown/missing catalog visibility is a gap. Normalize only documented representation/OID differences, never delete semantic mismatches."),
    )),
    "P0C-CTX-01": (
        ("fresh_tuple", "Fresh actual login/backend/xid READ COMMITTED context binds; same-live-transaction rebind is idempotent."),
        ("rollback_lifetime", "Full rollback, savepoint rollback and failed bind leave the issuer-committed old tuple unable to authorize a later xid."),
        ("backend_pool_lifetime", "Commit/reuse on the same backend and a different backend reject old handles; a newly authorized grant for the same semantic command can succeed."),
        ("wrong_isolation", "Non-READ-COMMITTED context fails, without exposing a raw grant row."),
        ("no_authority_from_transport", "Actor IDs, copied hash/GUC values, wrong purpose/root/field and malformed grants cannot manufacture authority."),
    ),
    "P0C-CTX-02": (
        ("revocation_schedule", "For app and worker separately: bind without a protected action lock; issuer revocation COMMIT precedes A's next protected statement and that statement denies."),
        ("security_generation_schedule", "A separate authorized Identity owner mutation with its own fresh tuple/evidence commits before A acts; stale security context denies."),
        ("source_generation_schedule", "A separate authorized Customer source update commits before A acts; the stale app path or worker's Customer-validation port denies."),
        ("role_appropriate_positive", "Each subject first has a meaningful fresh positive: app Customer operation; worker registered Track path/Boolean port, never direct Customer access."),
        ("independent_service_currentness", "Only the actual narrow Identity authority changes service epochs with immutable receipts; stale/revoked grants deny and fresh independently authorized generation can succeed."),
    ),
    "P0C-PRIV-01": (
        ("issuer_ceiling", "Actual issuer issues/selects own grants and performs one-way revoke only; tuple/scope rewrite, delete, self-attested currentness and business writes deny."),
        ("runtime_escalation", "App/worker direct grant CRUD, TRUNCATE, CREATE and SET ROLE issuer/helper/verifier/schema owner deny."),
        ("helper_ceiling", "NOLOGIN helper/verifiers are exercised only through named functions; no login, raw body output, business DML or broader inherited privilege."),
        ("browser_simulation", "Explicitly labeled local browser/service-role simulations cannot execute protected helpers or access internal schemas; no hosted Data API parity inferred."),
        ("direct_ports", "Every directly exposed verifier has a same-job positive and independent foreign customer/job/source/plan/version/transaction/capability denials; private actual-row ports are not worker-executable."),
    ),
    "P0C-BOOT-01": (
        ("nonrecursive_create", "Customer creation at revision zero/null predecessor commits its exact source/history/command/evidence/messages without Ops startup or recursive proof-about-proof."),
        ("create_then_update", "A fresh scoped Customer update proves predecessor zero and revision one with the correct update-only message set."),
        ("missing_piece_denial", "Missing required proof/history/outbox and invalid first predecessor deny; backend closure precedes zero-residue observation."),
    ),
    "P0C-ATOMIC-01": (
        ("complete_group", "Actual app transaction commits one Customer, exact history/evidence/command and precisely required messages."),
        ("omit_each_piece", "Independently omit command/history/evidence/event/Free intent; each intended guard denies and the complete business group rolls back."),
        ("message_reverse", "Wrong source/user/history/revision/ordinal/count, extra Free intent on update and wrong result version each reject."),
    ),
    "P0C-UNIQUE-01": (
        ("same_semantic_identity", "Actual restricted same-scope repeated semantic key cannot create a second retained command/effect."),
        ("changed_fingerprint", "Same semantic identity with changed fingerprint conflicts; a storage uniqueness error is not reported as a production adapter response."),
        ("different_scope", "Identical text key in a separately permitted owner/subject scope succeeds with that scope's complete proof."),
    ),
    "P0C-CAS-01": (
        ("concurrent_customer_update", "Two actual app sessions with the same predecessor race under barriers: exactly one next Customer revision/history/evidence/message group commits."),
        ("stale_predecessor", "Wrong predecessor, skipped revision and same-grant second source update deny, without duplicate state."),
    ),
    "P0C-IMMUTABLE-01": (
        ("consent_chain", "Named publisher/presentation/proof/disposition paths commit exact immutable content/subject/action/context/hash relationships."),
        ("foreign_consent", "Cross-user/content/action/context/rendered hash and missing relationship capability deny independently."),
        ("empty_context", "The actual empty global registry denies null/empty contexts; do not change the registry to invent a global positive."),
        ("append_only", "Age/source/effect/Consent retained evidence rejects update/delete; valid separate append/withdrawal remains possible."),
        ("replay_conflict", "Same-key identical replay and changed-fingerprint storage conflict are distinguished without qualifying production owner adapters."),
    ),
    "P0C-TRACK-01": (
        ("actual_worker_enrollment", "Actual worker under current job/lease/Customer/approved Free plan commits the exact new subscription, typed grants, selection, receipt/history/effect/inbox once."),
        ("preserve_valid_selection", "Existing valid Free/paid selection and original semantic receipt survive delayed/duplicate Free handling without new history/grants."),
        ("worker_ceiling", "Worker catalog writes, all usage access, standalone history SELECT and immutable rewrites deny; setup/usage observer are separate principals."),
        ("typed_relations", "Wrong user/profile/track/plan revision/hash/benefit type, duplicate current selection and changed semantic fingerprint deny."),
        ("lease_transitions", "Current-secret claim/renew/attach/complete succeeds; expiry, stale fence, copied hash, relink, attempt-only mutation and foreign receipt deny."),
        ("concurrent_fence", "Real concurrent sessions demonstrate current-holder fencing and reclaim, without implementing a production worker loop."),
        ("reservation_outcomes", "App reservation active-to-commit and active-to-unknown-to-release require one exact protected effect attachment; foreign receipt/identity and unknown-to-active bypass deny."),
    ),
    "P0C-EVIDENCE-01": (
        ("closed_codec", "Creation prior=null/revision0 and update exact prior/committed snapshot, Int numbers and BigInt strings use the actual SQL storage digest codec."),
        ("invented_evidence", "Extra/private JSON keys, wrong enum/PK/revision/decision/source/transaction/digest and missing prior reject with intended diagnostics."),
        ("worker_reverse", "Actual worker reverse source proof and selection predecessor verification pass only for exact same-job actual rows; fabricated snapshots/capability omissions deny."),
    ),
    "P0C-RESTORE-01": (
        ("real_backup", "Create a protected real synthetic backup with artifact digest/tool/source/target identities and a manifested fresh restore target."),
        ("restored_parity", "Actual restore preserves expected schema, ownership, ledger/checksums and synthetic data; no simultaneous raw-structure/migration application."),
        ("restored_authority", "Keep target quarantined; independent Identity epoch/revocation/credential procedures precede service activation; stale restored grants fail actual SQL checks."),
        ("privacy_reapplication", "Actual owner Privacy restriction/restore-marker generation is reapplied before serving; manually seeded markers or a closed harness are not proof of the missing owner port."),
    ),
}


def operation_name(operation):
    return operation["operation"] if isinstance(operation, dict) else operation.split("_", 1)[0]


def path_for(model, role, verb, setup, acl_rows, scopes):
    """Conservative source-path classification; runtime must establish success."""
    explicit = next((p for p in setup.get("operation_dispositions", [])
                     if p["role"] == role and p["verb"] == verb), None)
    if explicit:
        return ("DEPENDENCY_BLOCKED" if explicit["dependency_ids"] else "CANDIDATE_LOCAL_SQL_PATH",
                explicit["dependency_ids"], explicit)
    if model == "DatabaseActionGrant":
        return "CANDIDATE_NAMED_GRANT_PROTOCOL", [], {
            "read_owner_rule": "NOLOGIN helper via named DEFINER only; app/worker no direct grant access",
            "issuer_rule": "Own grant INSERT/SELECT and one-way revoked_at UPDATE only",
        }
    if role == "wa_private_helper_owner":
        return "CANDIDATE_NAMED_DEFINER_ONLY", [], {"direct_login_allowed": False}
    actual = [a for a in acl_rows if a["role"] == role and a["operation"] == verb]
    if verb in ("SELECT", "INSERT", "UPDATE") and not actual:
        return "SPECIFICATION_CONFLICT", [], {
            "reason": "Declared ALLOW operation has no actual generated role/verb ACL. Preserve the declaration for independent reconciliation; never widen permission to make it pass.",
        }
    if role == "wa_worker":
        if model == "RuntimeWorkItem" and verb == "INSERT":
            return "SPECIFICATION_CONFLICT", [], {
                "reason": "runtime_transition requires actual wa_app_runtime scheduler for INSERT; generic worker ceiling is not a permitted scheduling path.",
            }
        return "CANDIDATE_LOCAL_SQL_PATH", [], {
            "scope": "Exact current RuntimeWorkItem/default-Free handler; claim and renew use separate registered platform scopes",
            "constraints": "Current Customer, approved plan, lease secret/fence, exact source fields and atomic effect/inbox/receipt required",
        }
    if model in ("RuntimeAttempt", "RuntimeInboxReceipt"):
        return "SOURCE_PATH_REVIEW_REQUIRED", [], {
            "reason": "Generic app ACL ceiling is not a registered app path; mutation guard invokes actual-worker lease/effect validation. Identify a complete already-authorized path or reconcile the declaration, without creating an app worker bypass.",
        }
    if model in ("RuntimeCommandReceipt", "RuntimeOutboxMessage", "RuntimeEffectReceipt", "OwnerMutationEvidence"):
        return "CANDIDATE_LOCAL_SQL_PATH", [], {
            "scope": "Only as exact companion of a registered source transaction or approved runtime reservation; no standalone arbitrary root",
            "constraints": "All command/source/proof/message/terminal guards and per-row field capabilities required",
        }
    if model == "RuntimeWorkItem":
        return "CANDIDATE_LOCAL_SQL_PATH", [], {
            "scope": "runtime.schedule_work.v1/work.schedule on exact RuntimeWorkItem",
            "constraints": "App may schedule pending work; no app claim/completion through worker-only checks. UPDATE needs a valid permitted pending scheduling field path, not a no-op counted as worker qualification.",
        }
    if model == "CustomerProfileLifecycleEvent":
        return "CANDIDATE_LOCAL_SQL_PATH", [], {
            "scope": "Exact child of Customer SH-004 provision or registered Customer update; never independent invented history",
        }
    matching = [s for s in scopes if s["root_kind"] == model and verb in s["verbs"]]
    if matching:
        return "CANDIDATE_LOCAL_SQL_PATH", [], {"scope_registration_indices": [scopes.index(s) for s in matching]}
    return "SOURCE_PATH_REVIEW_REQUIRED", [], {
        "reason": "No complete root/verb registration found in current source registry; do not turn an ACL ceiling into a positive or manufacture authority.",
    }


def table_case(case, model_source, access, acl_rows, scopes, guards):
    case_id = case["id"]
    model, direction = case_id[len("P0C-TABLE-"):].rsplit("-", 1)
    setup = case["setup"]
    rows = [r for r in acl_rows if r["model"] == model]
    result = {
        "id": case_id, "kind": "TABLE_" + direction, "model": model,
        "source_register_status": case["status"], "status": "NOT_RUN",
        "requirement_ids": case["requirement"],
        "source": {
            "object": model_source["object"], "business_owner": model_source["owner"],
            "actual_generated_acl": rows,
            "registered_root_scope_indices": [i for i, s in enumerate(scopes) if s["root_kind"] == model],
            "sql_trigger_guards": guards[model_source["object"]],
            "source_register": "database-candidate-tests.json#" + case_id,
        },
        "assertions": [],
    }
    assertions = result["assertions"]
    if direction == "ALLOW":
        assert setup["operations_by_role"] == access["operations_by_role"], case_id + ": role ceiling drift"
        for role, operations in setup["operations_by_role"].items():
            for operation in operations:
                verb = operation_name(operation)
                availability, dependencies, path = path_for(model, role, verb, setup, rows, scopes)
                assertions.append(assertion(
                    "positive." + role + "." + verb.lower(), "ALLOW_COMPLETE_REGISTERED_PATH",
                    "Actual intended role completes this declared permitted operation with exact context/capabilities/prerequisite reads and every applicable source/proof/terminal guard.",
                    availability, dependencies, role=role, declared_operation=operation,
                    path_review=path,
                ))
                if dependencies or availability in ("SPECIFICATION_CONFLICT", "SOURCE_PATH_REVIEW_REQUIRED"):
                    assertions.append(assertion(
                        "separate_gate_denial." + role + "." + verb.lower(), "DENY_MISSING_REGISTERED_PATH",
                        "Exercise the applicable exact gate denial separately. A denial never satisfies or promotes the declared positive above; retain unresolved source-path conflicts.",
                        "CANDIDATE_GATE_DENIAL_ONLY", role=role,
                        positive_assertion="positive." + role + "." + verb.lower(),
                    ))
        for path in setup.get("operation_dispositions", []):
            if path["verb"] != "UPDATE_COMPLETION_STATES":
                continue
            assertions.append(assertion(
                "positive.wa_app_runtime.privacy_completion", "ALLOW_COMPLETE_REGISTERED_PATH",
                path["atomic_proof"], "DEPENDENCY_BLOCKED", path["dependency_ids"],
                role=path["role"], path_review=path,
            ))
            assertions.append(assertion(
                "separate_gate_denial.wa_app_runtime.privacy_completion", "DENY_UNQUALIFIED_COMPLETION",
                "Actual completed/partially_completed request mutation remains denied by the explicit owner-accounting gate, separately from ordinary open-state positives.",
                "CANDIDATE_GATE_DENIAL_ONLY", role="wa_app_runtime",
            ))
    else:
        assert setup["direct_denials_by_role"] == access["direct_denials_by_role"], case_id + ": denials drift"
        for role, operations in setup["direct_denials_by_role"].items():
            for operation in operations:
                assertions.append(assertion(
                    "denial." + role + "." + operation.lower(), "DENY_OR_AUTHORIZED_NONENUMERATING_FILTER",
                    "Attempt the specified denial using a valid existing synthetic target/statement. Require the intended ACL/policy/guard result, not syntax/type/FK errors, nonexistent rows or missing objects.",
                    "CANDIDATE_LOCAL_DENIAL", role=role, declared_operation=operation,
                    simulation="Explicit local provider/browser role simulation only" if role in ("anon", "authenticated", "service_role") else None,
                    helper_rule="No helper-owner LOGIN or SET ROLE is used to prove a business positive; NOLOGIN/escalation denials are explicit controls.",
                ))
        for operation in setup.get("additional_denials", []):
            assertions.append(assertion(
                "denial.context." + operation.lower(), "DENY_WRONG_AUTHORITY_OR_FIELDS",
                "Use a complete otherwise-valid scoped target and isolate this substitution; observe no protected disclosure or retained effect.",
                "CANDIDATE_LOCAL_DENIAL", declared_operation=operation,
            ))
    # The register's targeted vectors add requirements beyond generic ACL verbs.
    # Keep their exact definitions, including future fields/status/dependencies,
    # and expose both branches. In a DENY case the positive branch establishes
    # the valid control fixture; it is not mislabeled as the denied operation.
    result["source_vectors"] = case.get("p0c03a_vectors", [])
    for index, vector in enumerate(result["source_vectors"]):
        dependencies = vector.get("execution_dependencies", [])
        for branch in ("positive", "adversarial"):
            positive = branch == "positive"
            outcome = (
                "ALLOW_COMPLETE_REGISTERED_VECTOR" if direction == "ALLOW" else
                "ESTABLISH_VALID_POSITIVE_CONTROL_FOR_DENIAL"
            ) if positive else "DENY_REGISTERED_VECTOR_SUBSTITUTION"
            assertions.append(assertion(
                "vector." + vector["id"] + "." + branch,
                outcome, vector[branch],
                "DEPENDENCY_BLOCKED" if dependencies else
                "CANDIDATE_LOCAL_SQL_PATH" if positive else "CANDIDATE_LOCAL_DENIAL",
                dependencies,
                source_vector_id=vector["id"], source_vector_branch=branch,
                source_vector_status=vector["status"],
                source_vector_reference=("database-candidate-tests.json#" + case_id +
                                         "/p0c03a_vectors/" + str(index)),
                vector_expected=vector["expected"],
            ))
    return result


def control_case(case):
    assertions = []
    for name, expectation in CONTROL_ASSERTIONS[case["id"]]:
        dependencies = ["P0F_PRIVACY_RESTORE_GENERATION_PORT"] if name == "privacy_reapplication" else []
        assertions.append(assertion(
            "control." + name, "REQUIRE_EXACT_OBSERVED_RESULT", expectation,
            "DEPENDENCY_BLOCKED" if dependencies else "CANDIDATE_LOCAL_SQL_PATH", dependencies,
        ))
    for vector in case.get("p0c03a_vectors", []):
        dependencies = vector.get("execution_dependencies", [])
        # A gate reached before the intended predecessor/restore guard cannot
        # prove that deeper negative. Preserve both requirements as blocked.
        for direction, key in (("positive", "positive"), ("adversarial", "adversarial")):
            scope_limit = None
            if vector["id"] == "CONSENT-EMPTY":
                scope_limit = "Keep the current global registry empty. The attainable positive is the exact nonempty context; a hypothetical separately reviewed global tuple is not current authority or required permission widening."
            assertions.append(assertion(
                "vector." + vector["id"] + "." + direction,
                "REQUIRE_REGISTERED_VECTOR_" + direction.upper(), vector[key],
                "DEPENDENCY_BLOCKED" if dependencies else "CANDIDATE_LOCAL_SQL_PATH", dependencies,
                vector_expected=vector["expected"],
                source_scope_limit=scope_limit,
            ))
    return {
        "id": case["id"], "kind": "FOUNDATION_CONTROL", "model": None,
        "source_register_status": case["status"], "status": "NOT_RUN",
        "requirement_ids": case["requirement"],
        "source_register": "database-candidate-tests.json#" + case["id"],
        "assertions": assertions,
    }


def build():
    selection = data(INPUTS[0])["first_p0c_replay"]["ids"]
    register = {r["id"]: r for r in data(INPUTS[1])["tests"]}
    matrix = {r["model"]: r for r in data(INPUTS[2])["objects"] if r.get("model")}
    replay = data(INPUTS[3])["tests"]
    acl_rows = data(INPUTS[4])
    models = {r["model"]: r for r in data(INPUTS[5])}
    scope_policy = data(INPUTS[6])
    guards = guard_inventory(read("review-output/foundation-application.review.sql"))
    assert len(selection) == len(set(selection)) == 94
    assert {r["id"] for r in replay} == set(selection), "Selected replay identity drift"
    assert len(models) == 40 and all(m["object"] in guards for m in models.values())
    cases = []
    for case_id in selection:
        case = register[case_id]
        if case_id.startswith("P0C-TABLE-"):
            model = case_id[len("P0C-TABLE-"):].rsplit("-", 1)[0]
            cases.append(table_case(case, models[model], matrix[model], acl_rows,
                                    scope_policy["domain_scopes"], guards))
        else:
            cases.append(control_case(case))
    assert sum(c["kind"].startswith("TABLE_") for c in cases) == 80
    assert sum(c["kind"] == "FOUNDATION_CONTROL" for c in cases) == 14
    assertions = []
    for case in cases:
        ids = [a["id"] for a in case["assertions"]]
        assert ids and len(ids) == len(set(ids)), "Missing/duplicate assertion in " + case["id"]
        if case["kind"].startswith("TABLE_"):
            source_vectors = register[case["id"]].get("p0c03a_vectors", [])
            assert case["source_vectors"] == source_vectors, "Table vector definition drift"
            actual_vectors = [a for a in case["assertions"] if "source_vector_id" in a]
            assert len(actual_vectors) == 2 * len(source_vectors), "Missing table vector branch"
            for vector in source_vectors:
                for branch in ("positive", "adversarial"):
                    matches = [a for a in actual_vectors
                               if a["source_vector_id"] == vector["id"] and
                               a["source_vector_branch"] == branch]
                    assert len(matches) == 1, "Missing/duplicate table vector: " + vector["id"]
                    item = matches[0]
                    assert item["expected_assertion"] == vector[branch]
                    assert item["vector_expected"] == vector["expected"]
                    assert item["source_vector_status"] == vector["status"]
                    assert item["dependency_ids"] == vector.get("execution_dependencies", [])
        assertions.extend(case["assertions"])
    assert all(a["status"] == "NOT_RUN" for a in assertions)
    source_hashes = {path: sha(path) for path in sorted(INPUTS)}
    source_digest = hashlib.sha256("".join(
        path + "\0" + digest + "\n" for path, digest in source_hashes.items()
    ).encode("utf8")).hexdigest()
    return {
        "schema": "workinants.local-f0-assertion-inventory.v1",
        "status": "PLAN_ALL_ASSERTIONS_NOT_RUN",
        "scope": "Existing selected 94 IDs only; assertion inventory is not execution, qualification, a new suite, an owner adapter or permission authority.",
        "selection_path": INPUTS[0], "register_path": INPUTS[1],
        "source_provenance": {
            "files_sha256": source_hashes,
            "aggregate_sha256": source_digest,
            "aggregate_recipe": "SHA256 UTF8(sorted path + NUL + lowercase file SHA256 + LF)",
            "self_hash_rule": "The builder is fingerprinted; the generated output is not self-hashed.",
            "sql_guard_extraction": "Generated CREATE TRIGGER and corresponding CREATE FUNCTION dollar-quoted source; no SQL parser/server/harness/process invoked.",
        },
        "completion_rule": "A case cannot PASS while any mandatory positive/negative/assertion is failed, NOT_RUN, dependency-blocked or unresolved. Independent gate-denial evidence never substitutes for a blocked positive. Record unique assertions separately from repeated executions.",
        "counting_rule": "Counts describe case/assertion obligations extracted from the existing selection, not extra suites or a required number of experiments. One reviewed execution may witness several exact obligations; retain those links and count repeated executions separately.",
        "execution_requirements": [
            "Review exact packet/fixtures/run manifest independently before changed security-sensitive SQL execution.",
            "Use actual restricted logins, finite exact capabilities and meaningful source fixtures; setup/observer privilege is not behavioral proof.",
            "All 94 identities remain; later 357 register IDs are excluded. Local provider simulations never establish hosted Supabase parity.",
            "Stop one attempt on unexpected results, preserve sanitized evidence and closure/cleanup, then diagnose/review/correct under standing local authority.",
            "Keep historical applied migration checksums and June history immutable, root write aliases blocked, Posture D and P0-D/E/F/G boundaries intact.",
        ],
        "special_scope_sources": {
            key: scope_policy[key] for key in ("worker_scope", "runtime_work_scopes", "reservation_scope", "registered_global_consent_contexts")
        },
        "domain_scope_registrations": scope_policy["domain_scopes"],
        "summary": {
            "selected_case_ids": 94, "table_direction_cases": 80,
            "foundation_control_cases": 14, "models": 40,
            "mandatory_assertions": len(assertions),
            "table_source_vectors": sum(len(c.get("source_vectors", [])) for c in cases),
            "table_vector_branch_assertions": sum("source_vector_id" in a for a in assertions),
            "by_availability": dict(sorted(Counter(a["availability"] for a in assertions).items())),
            "all_assertions_not_run": True,
        },
        "cases": cases,
    }


if __name__ == "__main__":
    inventory = build()
    (ROOT / OUTPUT).write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf8", newline="\n")
    print(json.dumps(inventory["summary"], sort_keys=True))
