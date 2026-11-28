"""Pure three-history receipts and a modeled owning sequence. No host transport."""

import re
from types import SimpleNamespace

import candidate_profile as candidate


S = candidate.S
DATABASE = "wa_p0c_rehearsal"
LEAVES = ("wa_customer_verifier", "wa_private_helper_owner", "wa_track_verifier")
SCRAM_ROLES = ("postgres", "wa_migrator", "wa_context_issuer", "wa_identity_service_authority", "wa_app_runtime", "wa_worker")
FUNCTIONS = (
    "platform_private.track_atomic_valid(pg_catalog.text,pg_catalog.jsonb,pg_catalog.jsonb)",
    "platform_private.track_binding()",
    "platform_private.track_enrollment_commit()",
)
RESULT_COMPLETE = "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS"
AUTH_REF = "scram-sha-256:postgres"
AUTHORITY_FLAGS = {"grantor": "postgres", "admin": False, "inherit": False, "set": True}
MODELED_BOOTSTRAP = {"owned_bootstrap": True, "business_roles_inactive": True, "closed": True}
MODELED_CLOSED = {"all_other_clients_absent": True}
MODELED_CLEANUP = {"full_container_id_absent": True, "container_name_absent": True, "volume_absent": True,
                   "private_runtime_path_absent": True}
LEDGER_TOOL_PINS = {
    "node_modules/@prisma/engines-version/package.json": "2dd9793255d6bbb5c399a624ecbfb6323d39233860863d172946b7f750f528bd",
    "node_modules/prisma/package.json": "6cdfef6df08d9a37f28908855797fe8bfc97a2d3d886a8d5cbe2e502d6848151",
    candidate.LEDGER_COLLECTOR: "6dfa02fa375da4a126b996fc547dfff063c61b41c854db6b07ea62f52d63286b",
    "scripts/sql-review/prisma_ledger_proof.py": "1cb05b1d82b67580671cccf5f9289fbc481fef2d77532b049658912428604b21",
}


AUTHORITY_SQL = """BEGIN READ ONLY;
SET LOCAL search_path=pg_catalog;
SELECT jsonb_build_object(
 'database',current_database(),'login',session_user,'effective_login',current_user,'authentication',system_user,
 'server_version_num',current_setting('server_version_num')::int,'read_only',current_setting('transaction_read_only')='on',
 'other_client_backends',(SELECT count(*) FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()),
 'temporary_memberships',(SELECT coalesce(jsonb_agg(jsonb_build_object('role',r.rolname,'grantor',g.rolname,
   'admin',m.admin_option,'inherit',m.inherit_option,'set',m.set_option) ORDER BY r.rolname),'[]'::jsonb)
   FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.roleid JOIN pg_roles g ON g.oid=m.grantor
   WHERE m.member='wa_schema_owner'::regrole AND r.rolname IN ('wa_customer_verifier','wa_private_helper_owner','wa_track_verifier')),
 'permanent_migrator_owner',(SELECT coalesce(jsonb_agg(jsonb_build_object('grantor',g.rolname,
   'admin',m.admin_option,'inherit',m.inherit_option,'set',m.set_option) ORDER BY g.rolname),'[]'::jsonb)
   FROM pg_auth_members m JOIN pg_roles g ON g.oid=m.grantor
   WHERE m.member='wa_migrator'::regrole AND m.roleid='wa_schema_owner'::regrole),
 'migrator_can_set_owner',pg_has_role('wa_migrator','wa_schema_owner','SET'),
 'migrator_can_set_track_verifier',pg_has_role('wa_migrator','wa_track_verifier','SET'),
 'temporary_leaf_schema_create',jsonb_build_object(
   'wa_customer_verifier',has_schema_privilege('wa_customer_verifier','platform_private','CREATE'),
   'wa_private_helper_owner',has_schema_privilege('wa_private_helper_owner','platform_private','CREATE'),
   'wa_track_verifier',has_schema_privilege('wa_track_verifier','platform_private','CREATE')),
 'functions',(SELECT coalesce(jsonb_object_agg(w.name,jsonb_build_object('owner',pg_get_userbyid(p.proowner),
   'body_sha256',encode(sha256(convert_to(p.prosrc,'UTF8')),'hex'),'security_definer',p.prosecdef)),'{}'::jsonb)
   FROM unnest(ARRAY['platform_private.track_atomic_valid(pg_catalog.text,pg_catalog.jsonb,pg_catalog.jsonb)',
     'platform_private.track_binding()','platform_private.track_enrollment_commit()']) w(name)
   JOIN pg_proc p ON p.oid=to_regprocedure(w.name)));
COMMIT;
"""


def exact(actual, expected, code):
    S.require(S.encode(actual) == S.encode(expected), code)


class RemoteUnconfirmed(S.Held):
    """A modeled callback could not close its remote work."""


def authority(value, expected_catalog, *, timing):
    S.require(timing in ("PRE_DEPLOY", "PRE_FINALIZATION", "POST_FINALIZATION", "POST_NOOP"),
              "TRACK_AUTHORITY_PHASE")
    temporary = timing in ("PRE_DEPLOY", "PRE_FINALIZATION")
    functions = expected_catalog["expected"]["functions"]
    expected = {
        "database": DATABASE, "login": "postgres", "effective_login": "postgres", "authentication": AUTH_REF,
        "server_version_num": 170011, "read_only": True, "other_client_backends": 0,
        "temporary_memberships": [{"role": role, **AUTHORITY_FLAGS} for role in LEAVES] if temporary else [],
        "permanent_migrator_owner": [AUTHORITY_FLAGS],
        "temporary_leaf_schema_create": dict.fromkeys(LEAVES, False), "migrator_can_set_owner": True,
        "migrator_can_set_track_verifier": temporary,
        "functions": {} if timing == "PRE_DEPLOY" else {
            name: {key: functions[name][key] for key in ("owner", "body_sha256", "security_definer")} for name in FUNCTIONS
        },
    }
    S.require(functions[FUNCTIONS[0]]["owner"] == "wa_track_verifier"
              and all(functions[name]["owner"] == "wa_schema_owner" for name in FUNCTIONS[1:]),
              "STABLE_CANDIDATE_FUNCTION_OWNERS")
    exact(value, expected, "TRACK_LEAF_MEMBERSHIP_OR_RESTORATION_DRIFT")
    return {"phase": timing, "exact_role_options": True, "leaf_create_absent": True,
            "candidate_function_bodies_verified": bool(expected["functions"])}


def attestation(manifest, observation, operation, *, packet_sha256, literal_review_sha256):
    """Render the closed stdin shape after an owning adapter observes live identity."""
    parent = candidate.reviewed_parent()
    target = manifest["target"]
    fields = {"endpoint", "daemon", "container_id", "container_name", "volume_name", "volume_created_at",
              "image", "image_id", "network", "published_ports", "labels", "bootstrap", "bootstrap_removed",
              "mount_destinations"}
    S.require(type(observation) is dict and set(observation) == fields and operation in ("deploy", "status")
              and manifest["schema"] == candidate.RUN_SCHEMA and manifest["purpose"] == candidate.PURPOSE
              and S.encode(target) == S.encode(candidate.target_for(parent, manifest["run_id"]))
              and manifest["history"] == {"path": candidate.HISTORY, "ordered": candidate.history_rows()}
              and parent.exact_daemon(observation["daemon"]) == manifest["daemon"] and observation["endpoint"] == parent.ENDPOINT
              and all(observation[name] == target[name] for name in ("container_name", "volume_name", "image", "network",
                                                                     "labels", "bootstrap"))
              and observation["image_id"] in parent.IMAGE_IDS
              and observation["mount_destinations"] == list(parent.MOUNT_DESTINATIONS)
              and observation["bootstrap_removed"] is True and observation["published_ports"] is False
              and type(observation["container_id"]) is str and re.fullmatch(r"[a-f0-9]{64}", observation["container_id"])
              and type(observation["volume_created_at"]) is str
              and re.fullmatch(r"[0-9TZ:.+\-]{20,64}", observation["volume_created_at"]), "EXACT_TRACK_LIVE_OBSERVATION")
    authorization = {"packet_sha256": packet_sha256, "literal_review_sha256": literal_review_sha256}
    S.require(all(type(pin) is str and re.fullmatch(r"[a-f0-9]{64}", pin) for pin in authorization.values()),
              "EXACT_TRACK_LIVE_AUTHORIZATION")
    raw = parent.encoded({"schema": candidate.ATTESTATION_SCHEMA, "planned": manifest, "observed": observation,
                          "operation": operation, "authorization": authorization,
                          "run_manifest_sha256": S.sha(parent.encoded(manifest))})
    S.require(0 < len(raw) <= 4 * 1024 * 1024, "TRACK_ATTESTATION_SIZE")
    return raw


def qualified_migration_result(raw, outer_exit, stderr, manifest, observed, operation, stdin, *, packet_sha256,
                               literal_review_sha256, historical_validator):
    """Recognize the new full result and compare the inherited diagnostic fields."""
    S.require(type(raw) is bytes and 0 < len(raw) <= 65536 and stderr == b"" and type(outer_exit) is int
              and outer_exit in (0, 1), "CLOSED_TRACK_WRAPPER_EXIT")
    receipt = S.unique_json(raw)
    fields = {"schema": candidate.RESULT_SCHEMA, "daemon_id": manifest["daemon"]["daemon_id"],
              "packet_sha256": packet_sha256, "literal_review_sha256": literal_review_sha256,
              "track_retained_sql_sha256": candidate.CANDIDATE_SHA, "attestation_sha256": S.sha(stdin)}
    S.require(type(receipt) is dict and all(receipt.get(k) == v for k, v in fields.items()), "TRACK_MIGRATION_RESULT_BINDING")
    retained = {name: value for name, value in receipt.items() if name not in fields or name == "attestation_sha256"}
    retained["schema"] = candidate.basis.B.CLOUD_RESULT
    historical_validator.safe_result(S.encode(retained).decode(), manifest, observed, operation)
    S.require(outer_exit == (0 if historical_validator.runner_succeeded(receipt) else 1), "TRACK_WRAPPER_RESULT_EXIT")
    if receipt["status"] == "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE":
        raise RemoteUnconfirmed("TRACK_REPORTED_CHILD_CLOSURE_UNCONFIRMED")
    return receipt


def registration(proof, ordered, *, source_root, run_id, attestation_sha256):
    exact(ordered, candidate.history_rows(), "EXACT_THREE_MIGRATION_REGISTRATION")
    rows = [{"path": row["path"], "migration_name": row["id"], "sha256": row["sha256"], "state": "applied", "count": 1}
            for row in ordered]
    exact(proof._tool_pins(), LEDGER_TOOL_PINS, "EXACT_PREVIOUSLY_REVIEWED_LEDGER_TOOL_METADATA")
    evidence = proof.build_registration(rows, root=source_root, run_id=run_id, target_attestation_sha256=attestation_sha256,
                                        source_expected_sha256=candidate.CATALOG_SHA)
    S.require(evidence["migrations"] == rows and len(evidence["history_expected"]) == 3
              and proof._tool_pins() == LEDGER_TOOL_PINS == evidence["tool_source_files_sha256"], "EXACT_THREE_APPLIED_ROWS")
    return evidence


def verify_ledger(proof, registered, observation, before, after, source_root):
    exact(before, after, "NATIVE_SCHEMA_DRIFT_DURING_LEDGER_OBSERVATION")
    evidence = {"format": proof.EVIDENCE_FORMAT, "registration_sha256": proof.digest(registered),
                "collector_sql_sha256": registered["tool_source_files_sha256"][proof.COLLECTOR],
                "run_id": registered["run_id"], "target_attestation_sha256": registered["target_attestation_sha256"],
                "native_catalog_before_sha256": proof.digest(before), "native_catalog_after_sha256": proof.digest(after),
                "observation": observation}
    result = proof.compare_proof(registered, evidence, before, bootstrap_grantor="postgres",
                                 source_expected_sha256=candidate.CATALOG_SHA, root=source_root)
    S.require(result["status"] == "PASS" and len(result["checks"]) == 22
              and all(row["status"] == "PASS" for row in result["checks"]), "TRACK_NATIVE_THREE_ROW_LEDGER_REFUSED")
    return evidence, result


def fingerprints(value, ordered):
    exact(ordered, candidate.history_rows(), "TRACK_FINGERPRINT_MIGRATION_ORDER")
    header = {"schema": "workinants.runtime-lease-history-fingerprints.v1", "server_version_num": 170011,
              "database": DATABASE, "collected_as": "postgres", "collector_is_superuser": True,
              "read_only": True, "history_count": 3}
    S.require(type(value) is dict and set(value) == {*header, "rows"}, "TRACK_FINGERPRINT_FIELDS")
    exact({name: value[name] for name in header}, header, "TRACK_FINGERPRINT_CONTEXT")
    rows = value["rows"]
    S.require(type(rows) is list and len(rows) == 3 and all(type(row) is dict
              and set(row) == {"name_sha256", "checksum_sha256", "row_sha256"}
              and all(type(pin) is str and re.fullmatch(r"[a-f0-9]{64}", pin) for pin in row.values()) for row in rows),
              "EXACT_THREE_FULL_ROW_FINGERPRINTS")
    wanted = sorted((S.sha(row["id"].encode()), S.sha(row["sha256"].encode())) for row in ordered)
    S.require([(row["name_sha256"], row["checksum_sha256"]) for row in rows] == wanted, "TRACK_FINGERPRINT_EXACT_HISTORY")
    return value


def unchanged_noop(before, after, ordered):
    exact(fingerprints(before, ordered), fingerprints(after, ordered), "NOOP_CHANGED_A_FULL_TRACK_LEDGER_ROW")
    return {"rows": 3, "all_eight_columns_compared": True}


def model_owned_sequence(model, plan, native_manifest):
    """Exercise the future adapter's required order against an explicit offline model."""
    S.require(type(model) is SimpleNamespace and getattr(model, "offline_model", False) is True
              and plan["schema"] == candidate.PACKET_SCHEMA and plan["runtime_authority"] is False,
              "OFFLINE_TRACK_OWNER_MODEL_REQUIRED")
    exact(plan["ledger_expected"], candidate.history_rows(), "EXACT_THREE_MIGRATION_REGISTRATION")
    S.require(native_manifest["expected_sha256"] == candidate.CATALOG_SHA, "EXACT_CANDIDATE_NATIVE_EXPECTATION")
    stages = []
    first, uncertain, bootstrap_attempted, finalizer_attempted = None, False, False, False
    cleanup_complete = False

    def visit(stage, *args):
        stages.append(stage)
        return model.responses[stage](*args)

    def migration(stage, operation):
        nonlocal uncertain
        uncertain = True
        value = visit(stage)
        S.require(type(value) is dict and set(value) == {"closed", "operation", "status", "exit_code",
                                                          "no_pending_message_observed"}
                  and value["closed"] is True and value["operation"] == operation
                  and value["status"] in (RESULT_COMPLETE, "CLI_FAILED_STOP_AND_INSPECT")
                  and type(value["exit_code"]) is int and 0 <= value["exit_code"] <= 255
                  and type(value["no_pending_message_observed"]) is bool
                  and (value["status"] == RESULT_COMPLETE) == (value["exit_code"] == 0)
                  and (not value["no_pending_message_observed"] or operation == "deploy" and value["exit_code"] == 0),
                  "TRACK_WRAPPER_CLOSURE_UNCONFIRMED")
        exact(visit(stage + "_ALL_CLIENTS_ABSENT"), MODELED_CLOSED, "TRACK_ALL_CLIENT_BACKENDS_NOT_CLOSED")
        uncertain = False
        S.require(value["status"] == RESULT_COMPLETE, "TRACK_PRISMA_OPERATION_STOPPED")
        return value

    def native(stage):
        value = visit(stage)
        S.require(type(value) is dict and set(value) == {"expected_sha256", "snapshot_sha256", "catalog_checks",
                                                          "oracle_expressions", "ledger_checks", "applied_rows"}
                  and value["expected_sha256"] == candidate.CATALOG_SHA
                  and type(value["snapshot_sha256"]) is str and re.fullmatch(r"[a-f0-9]{64}", value["snapshot_sha256"])
                  and all(type(value[key]) is int and value[key] == count for key, count in (
                      ("catalog_checks", 29089), ("oracle_expressions", 416), ("ledger_checks", 22), ("applied_rows", 3))),
                  "TRACK_NATIVE_LEDGER_ORACLE_UNCONFIRMED")
        return value

    finalizer = {"grantor": "postgres", "temporary_leaves_absent": True, "leaf_create_absent": True, "closed": True}
    three_rows = {"applied_rows": 3, "ledger_checks": 22, "native_unchanged": True}
    try:
        exact(visit("FRESH_OWNED_RESOURCE"), {"owned": True, "isolated": True, "no_host_bind": True},
              "TRACK_FRESH_RESOURCE_UNCONFIRMED")
        bootstrap_attempted = True
        uncertain = True
        exact(visit("OWNED_BOOTSTRAP"), MODELED_BOOTSTRAP, "TRACK_BOOTSTRAP_UNCONFIRMED")
        uncertain = False
        exact(visit("AUTHENTICATION_BEFORE_DEPLOY"), {"authenticated_roles": list(SCRAM_ROLES[:2]),
                                                     "inactive_roles_rejected": list(SCRAM_ROLES[2:]),
                                                     "all_clients_closed": True, "loopback_only": True},
              "TRACK_RESTRICTED_PRE_DEPLOY_AUTHENTICATION_UNCONFIRMED")
        authority(visit("PRE_DEPLOY"), native_manifest, timing="PRE_DEPLOY")
        migration("DEPLOY_THREE", "deploy")
        authority(visit("PRE_FINALIZATION"), native_manifest, timing="PRE_FINALIZATION")
        exact(visit("THREE_ROW_LEDGER_BEFORE_FINALIZATION"), three_rows, "TRACK_PRE_FINALIZATION_LEDGER_UNCONFIRMED")
        before_finalizer = fingerprints(visit("PRE_FINALIZATION_THREE_APPLIED_ROW_FINGERPRINTS"), plan["ledger_expected"])
        finalizer_attempted = True
        uncertain = True
        exact(visit("ORIGINAL_GRANTOR_FINALIZATION"), finalizer, "TRACK_ORIGINAL_GRANTOR_FINALIZER_UNCONFIRMED")
        uncertain = False
        authority(visit("POST_FINALIZATION"), native_manifest, timing="POST_FINALIZATION")
        exact(visit("THREE_ROW_LEDGER_BEFORE_ACTIVATION"), three_rows, "TRACK_PRE_ACTIVATION_LEDGER_UNCONFIRMED")
        uncertain = True
        exact(visit("ACTIVATE_ISOLATED_LOGINS_AND_VERIFY_SCRAM"),
              {"roles": list(SCRAM_ROLES), "loopback_only": True, "all_clients_closed": True,
               "wrong_passwords_rejected": True, "business_cases": "NOT_RUN"}, "TRACK_ISOLATED_AUTHENTICATION_UNCONFIRMED")
        uncertain = False
        initial_native = native("INITIAL_NATIVE_ORACLE_AND_THREE_ROW_LEDGER")
        before = fingerprints(visit("BEFORE_NOOP_FULL_ROWS"), plan["ledger_expected"])
        exact(before_finalizer, before, "TRACK_GRANTOR_FINALIZER_LEDGER_DRIFT")
        migration("STATUS", "status")
        S.require(migration("REDEPLOY", "deploy")["no_pending_message_observed"] is True, "TRACK_REAL_NO_PENDING_REQUIRED")
        unchanged_noop(before, visit("AFTER_NOOP_FULL_ROWS"), plan["ledger_expected"])
        exact(initial_native, native("COMPLETE_NATIVE_AND_LEDGER_PARITY"), "TRACK_NATIVE_NOOP_DRIFT")
        authority(visit("POST_NOOP"), native_manifest, timing="POST_NOOP")
    except BaseException as error:
        first = {"stage": stages[-1], "code": report_code(error)}
        uncertain = uncertain or isinstance(error, RemoteUnconfirmed)
    finally:
        if bootstrap_attempted and not finalizer_attempted and not uncertain:
            try:
                exact(visit("FAILURE_PATH_ALL_CLIENTS_ABSENT"), MODELED_CLOSED, "TRACK_FAILURE_PATH_BACKENDS_UNCONFIRMED")
                uncertain = True
                exact(visit("FAILURE_PATH_ORIGINAL_GRANTOR_FINALIZATION"), finalizer,
                      "TRACK_FAILURE_PATH_ORIGINAL_GRANTOR_FINALIZER_UNCONFIRMED")
                uncertain = False
            except BaseException as error:
                uncertain = uncertain or isinstance(error, RemoteUnconfirmed)
                first = first or {"stage": stages[-1], "code": report_code(error)}
        try:
            exact(visit("EXACT_OWNED_CLEANUP"), MODELED_CLEANUP, "TRACK_EXACT_RESOURCE_ABSENCE_UNCONFIRMED")
            cleanup_complete = True
        except BaseException as error:
            uncertain = uncertain or isinstance(error, RemoteUnconfirmed)
            first = first or {"stage": stages[-1], "code": report_code(error)}
    return {"status": "MODEL_COMPLETE" if first is None else "MODEL_STOPPED", "runtime": "NOT_RUN", "stages": stages,
            "first_failure": first, "sticky_remote_uncertainty": uncertain, "cleanup_complete": cleanup_complete,
            "assertion_promotions": 0}


def report_code(error):
    code = str(error)
    return code if re.fullmatch(r"[A-Z0-9_]{1,100}", code) else "TRACK_OWNER_MODEL_UNCONFIRMED"
