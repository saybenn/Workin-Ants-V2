"""Prepare a NEW native-fact/selected-DENY review packet, never execute it.

All fixture facts are synthetic. Privileged setup/native controls deliberately
prove native shape/ACL prerequisites only, never owner lifecycles or adapters.
No existing source/runtime/selected-register file is changed by this generator.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/sql-review"))
import catalog_manifest as source
import native_deny_fixture_factory as factory

OUT = ROOT / "review-output/native-table-denials"
SELECTION = "context/reconciliation/database-candidate-corrections-first-replay-selection.json"
MODELS = "context/reconciliation/foundation-sql-draft-models.json"
REGISTER = "context/reconciliation/database-candidate-tests.json"
ROLES = ("anon", "authenticated", "service_role", "wa_app_runtime", "wa_worker", "wa_context_issuer")
PROVIDER_ROLES = ROLES[:3]


def digest(raw): return hashlib.sha256(raw).hexdigest()


def grants(expected, table, role, privilege):
    result = set()
    for row in expected["nonowner_acl"]:
        if row["kind"] != "TABLE" or row["object"] != table or row["grantee"] not in (role, "PUBLIC") or row["privilege"] != privilege: continue
        if row["scope"] == "object": return set(expected["tables"][table]["columns"])
        if row["scope"] != "columns": raise factory.PreparationBlocked("unsupported native ACL scope")
        result.update(row["columns"])
    return result


def trigger_sql(trigger, enable):
    return "ALTER TABLE " + factory.table_sql(trigger["table"]) + (" ENABLE" if enable else " DISABLE") + " TRIGGER " + factory.ident(trigger["name"]) + ";"


def trigger_closure_sql(triggers, label):
    values = ",".join("(" + factory.quote(row["table"]) + "," + factory.quote(row["name"]) + "," + factory.quote(row["original_enabled"]) + ")" for row in triggers)
    return "SELECT jsonb_build_object('control'," + factory.quote(label) + ",'all_declared_user_triggers_restored',NOT EXISTS(SELECT 1 FROM (VALUES " + values + ") e(table_name,name,enabled) LEFT JOIN pg_trigger t ON t.tgrelid=to_regclass(e.table_name) AND t.tgname=e.name WHERE t.oid IS NULL OR t.tgisinternal OR t.tgenabled::text IS DISTINCT FROM e.enabled));"


def existing_observer(table, row, expected):
    condition = factory.predicate(table, row, expected)
    return "SELECT jsonb_build_object('row_count',(SELECT count(*) FROM " + factory.table_sql(table) + " WHERE " + condition + "));\n"


def provider_simulation_sql():
    lines = ["-- LOCAL DISPOSABLE PROVIDER-ROLE SIMULATION ONLY. Not hosted Supabase parity.",
             "-- Run AFTER fresh approved bootstrap creates schemas, BEFORE genuine Prisma application install.",
             "-- No passwords/URLs here. Separate reviewed private-tmpfs SCRAM provisioning is required.",
             "BEGIN;", "DO $local_provider_presence$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role')) THEN RAISE EXCEPTION 'local provider simulation requires absent role names'; END IF; END $local_provider_presence$;"]
    for role in PROVIDER_ROLES:
        lines.append("CREATE ROLE " + role + " LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION " + ("BYPASSRLS" if role == "service_role" else "NOBYPASSRLS") + ";")
    lines += ["-- Narrow local schema-USAGE sentinel only: source install's managed-role REVOKE must actually remove it.",
              "GRANT USAGE ON SCHEMA app,platform,platform_private TO anon,authenticated,service_role;", "COMMIT;"]
    return "\n".join(lines) + "\n"


def build(root=ROOT):
    root = Path(root)
    manifest = source.build_manifest(root)
    expected = manifest["expected"]
    models = json.loads((root / MODELS).read_text(encoding="utf8"))
    selected = json.loads((root / SELECTION).read_text(encoding="utf8"))["first_p0c_replay"]["ids"]
    deny_ids = [identity for identity in selected if identity.startswith("P0C-TABLE-") and identity.endswith("-DENY")]
    by_model = {row["model"]: row for row in models}
    register = {row["id"]: row for row in json.loads((root / REGISTER).read_text(encoding="utf8"))["tests"]}
    if len(deny_ids) != 40 or len(models) != 40: raise factory.PreparationBlocked("exact forty selected table-DENY identities required")
    schemas = factory.registry(root)
    baseline = factory.make_rows(expected, "baseline", schemas)
    checks = factory.validate_checks(expected, baseline, schemas)
    graph = factory.dependencies(expected, baseline)
    bypass, retained = factory.trigger_sets(expected, (root / "review-output/foundation-application.review.sql").read_text(encoding="utf8"))
    all_triggers = sorted(bypass + retained, key=lambda row: row["identity"])
    setup = ["-- SOURCE-ONLY NATIVE ACL FIXTURE FACTS. No owner-positive/Privacy/Track/adapter proof.",
             "-- Root verifies target, source/native manifest, role simulation and fresh separate fixture namespace before use.",
             "BEGIN;", "SET LOCAL search_path=pg_catalog;", "SET LOCAL log_statement='none';", "SET LOCAL log_min_error_statement='panic';"]
    setup.extend(trigger_sql(row, False) for row in bypass)
    setup.extend(factory.insert_sql(table, baseline[table], expected) + ";" for table in factory.ordered(graph))
    projected_setup_facts = [(table, baseline[table]) for table in factory.ordered(graph)]
    facts = {"baseline": factory.serializable(baseline)}
    foreign_issuer = deepcopy(baseline["platform.database_action_grant"])
    foreign_issuer.update(id=factory.uuid_value("foreign-issuer-negative-row", "platform.database_action_grant"),
                         token_hash=factory.fingerprint("foreign-issuer-negative-row"), issuer_service="native-foreign-issuer-no-authority")
    # No issuer authorization is asserted: this is a separately identified,
    # revoked/expired/backend0 native fact for the existing issuer ownership RLS.
    if foreign_issuer["revoked_at"] is None or foreign_issuer["backend_pid"] != 0:
        raise factory.PreparationBlocked("foreign issuer negative fact must remain inert")
    foreign_check_rows = deepcopy(baseline)
    foreign_check_rows["platform.database_action_grant"] = foreign_issuer
    factory.validate_checks(expected, foreign_check_rows, schemas)
    setup.append(factory.insert_sql("platform.database_action_grant", foreign_issuer, expected) + ";")
    projected_setup_facts.append(("platform.database_action_grant", foreign_issuer))
    facts["foreign-issuer-negative-only"] = factory.serializable({"platform.database_action_grant": foreign_issuer})
    files, cases, seen_setup = {}, [], set()
    preparation_blocks = []
    for case_id in deny_ids:
        model = case_id[len("P0C-TABLE-"):-len("-DENY")]
        table = by_model[model]["object"]
        ordinal = len(cases)
        leaf = factory.make_rows(expected, "delete-leaf/" + model, schemas)
        candidate = factory.make_rows(expected, "insert-candidate/" + model, schemas)
        leaf_graph = factory.dependencies(expected, leaf)
        candidate_graph = factory.dependencies(expected, candidate)
        leaf_closure = factory.parent_closure(leaf_graph, table) | {table}
        insert_closure = factory.parent_closure(candidate_graph, table)
        # Parents are separate native-valid facts; no child references the DELETE
        # leaf. The INSERT candidate itself stays absent until rollback control.
        for label, rows, dependency_graph, closure in (("delete-leaf/" + model, leaf, leaf_graph, leaf_closure),
                                                       ("insert-candidate/" + model, candidate, candidate_graph, insert_closure)):
            for parent in factory.ordered(dependency_graph, closure):
                key = (label, parent)
                if key in seen_setup: raise factory.PreparationBlocked("duplicate synthetic setup identity")
                seen_setup.add(key); setup.append(factory.insert_sql(parent, rows[parent], expected) + ";")
                projected_setup_facts.append((parent, rows[parent]))
            factory.validate_checks(expected, rows, schemas)
            facts[label] = factory.serializable({parent: rows[parent] for parent in sorted(closure | {table})})
        predicate = factory.predicate(table, baseline[table], expected)
        leaf_predicate = factory.predicate(table, leaf[table], expected)
        columns = list(expected["tables"][table]["columns"])
        update_columns = sorted({next((column for column in columns if column not in grants(expected, table, role, "UPDATE")), columns[0]) for role in ROLES})
        control_triggers = [row for row in all_triggers if row["table"] == table]
        control = ["-- PRIVILEGED NATIVE SHAPE CONTROL ONLY; all target USER triggers temporarily bypassed.",
                   "-- FK/CHECK/UNIQUE/internal RI triggers remain active. Roll back every mutation and trigger DDL.",
                   "BEGIN;", "SET LOCAL search_path=pg_catalog;", "SET LOCAL log_statement='none';", "SET LOCAL log_min_error_statement='panic';"]
        control.extend(trigger_sql(row, False) for row in control_triggers)
        control += ["SAVEPOINT native_control;", "WITH changed AS (" + factory.insert_sql(table, candidate[table], expected) + " RETURNING 1) SELECT count(*)=1 AS native_insert_one FROM changed;", "ROLLBACK TO SAVEPOINT native_control;"]
        for update_column in update_columns:
            control += ["WITH changed AS (UPDATE " + factory.table_sql(table) + " SET " + factory.ident(update_column) + "=" + factory.sql_value(leaf[table][update_column], expected["tables"][table]["columns"][update_column]["type"]) + " WHERE " + leaf_predicate + " RETURNING 1) SELECT count(*)=1 AS native_update_one FROM changed;", "ROLLBACK TO SAVEPOINT native_control;"]
        control += ["WITH changed AS (DELETE FROM " + factory.table_sql(table) + " WHERE " + leaf_predicate + " RETURNING 1) SELECT count(*)=1 AS native_delete_one FROM changed;", "ROLLBACK TO SAVEPOINT native_control;", "ROLLBACK;",
                    trigger_closure_sql(control_triggers, "native-control-" + model)]
        control_name = str(ordinal).zfill(2) + "-" + model + "-native-controls.sql"
        files[control_name] = "\n".join(control) + "\n"
        probes = []
        for role in ROLES:
            for verb in ("SELECT", "INSERT", "UPDATE", "DELETE"):
                allowed = grants(expected, table, role, verb)
                forbidden = [column for column in columns if column not in allowed]
                selected_column = forbidden[0] if forbidden else None
                statement = None
                facet = "NATIVE_SCHEMA_TABLE_OR_COLUMN_CEILING"
                blocked = None
                if verb == "SELECT":
                    if table == "platform.database_action_grant" and role == "wa_context_issuer":
                        statement = "SELECT count(*) FROM " + factory.table_sql(table) + " WHERE " + factory.predicate(table, foreign_issuer, expected)
                        facet = "RLS_ISSUER_FOREIGN_ROW_EXISTING_DENIED"
                    elif selected_column:
                        statement = "SELECT count(" + factory.ident(selected_column) + ") FROM " + factory.table_sql(table) + " WHERE " + predicate
                    else:
                        statement = "SELECT count(*) FROM " + factory.table_sql(table) + " WHERE " + predicate
                        facet = "RLS_NO_BOUND_CONTEXT_EXISTING_ROW_EMPTY"
                elif verb == "INSERT":
                    if selected_column: statement = factory.insert_sql(table, candidate[table], expected)
                    else: blocked = "NO_NATIVE_INSERT_COLUMN_CEILING_SOURCE_OWNS_BEHAVIOR_GUARD"
                elif verb == "UPDATE":
                    if selected_column:
                        statement = "UPDATE " + factory.table_sql(table) + " SET " + factory.ident(selected_column) + "=" + factory.sql_value(leaf[table][selected_column], expected["tables"][table]["columns"][selected_column]["type"]) + " WHERE " + leaf_predicate + " RETURNING 1"
                    else: blocked = "NO_NATIVE_UPDATE_COLUMN_CEILING_SOURCE_OWNS_BEHAVIOR_GUARD"
                elif verb == "DELETE":
                    # Table DELETE grants have no column scope.
                    if not allowed: statement = "DELETE FROM " + factory.table_sql(table) + " WHERE " + leaf_predicate + " RETURNING 1"
                    else: blocked = "NO_NATIVE_DELETE_CEILING_SOURCE_OWNS_BEHAVIOR_GUARD"
                probe = {"role": role, "verb": verb, "status": "NOT_RUN", "facet": facet,
                         "preparation": "BLOCKED" if blocked else "SOURCE_PREPARED_NATIVE_CONTROLS_AND_REENABLE_REQUIRED", "preparation_blocker": blocked,
                         "expected_sqlstate": None if blocked or facet.startswith("RLS_") else "42501", "expected_rows": 0 if facet.startswith("RLS_") else None,
                         "native_forbidden_column": selected_column,
                         "cause_limit": "42501 must occur at the native schema/table/column gate established by independent has_* privilege observations; do not label a trigger-raised42501 or a type/FK/missing row failure as ACL proof. A denied composite statement does not isolate one privilege from all earlier failed gates."}
                if statement:
                    probe_sql = "-- Fresh actual authenticated role connection; no context handle/bind or fixture bypass. Stop/close on unexpected output.\nBEGIN;\nSET LOCAL search_path=pg_catalog;\n" + statement + ";\nROLLBACK;\n"
                    probe["sql_text"] = probe_sql
                    probe["sql_sha256"] = digest(probe_sql.encode("utf8"))
                else: preparation_blocks.append({"case_id": case_id, "role": role, "verb": verb, "blocker": blocked, "status": "NOT_RUN"})
                probes.append(probe)
        observer_name = str(ordinal).zfill(2) + "-" + model + "-existing-observe.sql"
        files[observer_name] = existing_observer(table, baseline[table], expected)
        issuer_controls = None
        if table == "platform.database_action_grant":
            foreign_condition = factory.predicate(table, foreign_issuer, expected)
            issuer_controls = {"role": "wa_context_issuer", "status": "NOT_RUN", "source_policy": "grant_issuer_select", "own_expected_count": 1, "foreign_expected_count": 0,
                               "sql_text": "BEGIN;\nSELECT jsonb_build_object('own_row',(SELECT count(*) FROM platform.database_action_grant WHERE " + predicate + "),'foreign_row',(SELECT count(*) FROM platform.database_action_grant WHERE " + foreign_condition + "));\nROLLBACK;\n",
                               "scope_limit": "Own-row visibility is legitimate issuer audit access, even when the fixture grant is revoked/expired. This is a positive ownership-control assertion, not denial of the own row and not real issuer issuance/ALLOW qualification.",
                               "independent_fixture_observer_sql": "SELECT jsonb_build_object('own_exists',(SELECT count(*) FROM platform.database_action_grant WHERE " + predicate + "),'foreign_exists',(SELECT count(*) FROM platform.database_action_grant WHERE " + foreign_condition + "));\n"}
        cases.append({"id": case_id, "model": model, "table": table, "status": "NOT_RUN", "native_controls": control_name, "existing_row_observer": observer_name,
                      "source_allow_case": {"id": case_id.removesuffix("-DENY") + "-ALLOW", "status": register[case_id.removesuffix("-DENY") + "-ALLOW"]["status"],
                                            "execution_dependencies": register[case_id.removesuffix("-DENY") + "-ALLOW"].get("execution_dependencies", []),
                                            "operation_dependency_gates": register[case_id.removesuffix("-DENY") + "-ALLOW"].get("operation_dependency_gates", [])},
                      "baseline_primary_key_predicate": predicate, "delete_leaf_primary_key_predicate": leaf_predicate,
                      "insert_required_parent_tables": factory.ordered(candidate_graph, insert_closure), "delete_leaf_parent_tables": factory.ordered(leaf_graph, leaf_closure - {table}),
                      "control_bypassed_user_triggers": control_triggers, "probes": probes,
                      "issuer_ownership_controls": issuer_controls,
                      "native_update_control_columns": update_columns,
                      "positive_dependency_boundary": "These are synthetic native-valid confidentiality/ACL facts. They qualify no ALLOW case, owner lifecycle/group/API result/adapter, later Track/Privacy execution, or unavailable producer/consumer port."})
    setup.extend(trigger_sql(row, True) for row in reversed(bypass))
    setup += [trigger_closure_sql(all_triggers, "all-native-fact-setup-triggers-restored"), "COMMIT;"]
    files["native-fact-setup.sql"] = "\n".join(setup) + "\n"
    files["provider-role-simulation-before-migrate.sql"] = provider_simulation_sql()
    files["all-user-trigger-closure.sql"] = trigger_closure_sql(all_triggers, "independent-before-every-denial") + "\n"
    inputs = {**manifest["inputs_sha256"], SELECTION: digest((root / SELECTION).read_bytes()), REGISTER: digest((root / REGISTER).read_bytes()),
              "contracts/database-review/owner-mutation-evidence.v1.schema.json": digest((root / "contracts/database-review/owner-mutation-evidence.v1.schema.json").read_bytes()),
              "contracts/database-review/foundation-payloads.v1.schema.json": digest((root / "contracts/database-review/foundation-payloads.v1.schema.json").read_bytes()),
              "scripts/sql-review/native_deny_fixture_factory.py": digest((root / "scripts/sql-review/native_deny_fixture_factory.py").read_bytes()),
              "scripts/sql-review/test_native_deny_fixture_factory.py": digest((root / "scripts/sql-review/test_native_deny_fixture_factory.py").read_bytes()),
              "scripts/prepare-native-table-denials.py": digest(Path(__file__).read_bytes())}
    for relative in ("scripts/sql-review/catalog_manifest.py", "scripts/sql-review/compare_native_catalog.py", "scripts/sql-review/pg17_catalog_rules.py", "scripts/contract_schema.py",
                     "contracts/shared/SH-004.v1.schema.json", "contracts/shared/SH-114.v1.schema.json", "contracts/shared/types.v1.schema.json"):
        inputs[relative] = digest((root / relative).read_bytes())
    result = {"schema": "workinants.native-table-denials.v1", "status": "ALL_SELECTED_CASES_NOT_RUN_SOURCE_PACKET_ONLY", "database_posture": "D", "database_contacted": False, "sql_executed": False,
              "selected_case_ids": deny_ids, "selected_count": 40, "original94_ids_unchanged": True, "original451_statuses_unchanged": True,
              "source_inputs_sha256": inputs, "expected_native_catalog_sha256": manifest["expected_sha256"],
              "offline_parser": manifest["parser"], "offline_derivation_limit": "The local CHECK interpreter supports only explicit source AST forms and registered closed JSON. It is not PostgreSQL; native controls and exact observed server/catalog remain mandatory.",
              "native_fact_scope": "Native scalar/enum/FK/CHECK/closed-JSON facts only; no owner/producer/consumer/service authority. 42 base rows + independent required parent closures; no polymorphic/media/provider/new result contracts.",
              "baseline_table_count": len(baseline), "baseline_fk_order": factory.ordered(graph), "offline_source_check_derivations": checks,
              "offline_native_key_derivation": factory.validate_unique(expected, projected_setup_facts),
              "setup_bypassed_user_triggers": bypass, "setup_retained_user_triggers": retained, "setup_additional_parent_or_leaf_rows": len(seen_setup),
              "setup_additional_inert_foreign_issuer_rows": 1,
              "provider_role_simulation": {"local_only": True, "hosted_supabase_parity": False, "role_names": list(PROVIDER_ROLES), "login": True, "inherit": False, "superuser": False, "createdb": False, "createrole": False, "replication": False,
                   "bypassrls": {"anon": False, "authenticated": False, "service_role": True}, "service_role_limit": "Local native-ACL stressor with BYPASSRLS; even bypass cannot supply absent schema/table/column privileges. This does not represent hosted JWT/API/managed-role parity.",
                   "sequence": "Fresh isolated run only: bootstrap schemas; exact proposed role simulation with narrow schema-USAGE sentinels; independently observe those flags/USAGE; genuine Prisma application install executes existing managed-role revocations; independently verify schema-USAGE/table/function grants removed before fixture facts/probes. Never create roles after install then claim install revocation was exercised.",
                   "unchanged_runtime_roles": ["wa_app_runtime", "wa_worker"], "credential_transport": "Existing reviewed private-tmpfs SCRAM files only, never source/argv/env/log; no passwords in this packet.", "cleanup": "Exact run-owned local resources/role state removed by integration operator; no hosted alteration or reset."},
              "mandatory_runtime_contract": ["Independent source/SQL/run-manifest review before execution; current packet is not execution approval.",
                   "Actual isolated target/image/source/native catalog identity; frozen applied migration checksums; no raw integrated source reapplication.",
                   "Source CHECK derivation is offline reasoning, not native acceptance. Every actual native INSERT/UPDATE/DELETE control must affect exactly one row and roll back with all native FK/CHECK/UNIQUE/internal triggers active.",
                   "Restore/verify every exact USER trigger before restricted probes. Do not disable any trigger or change privileges during a denial. Preserve native catalog pre/post fingerprints.",
                   "Actual fresh authenticated login/session_user/current_user for each named role; SCRAM positive/wrong-password controls; no SET ROLE or fake identity GUC substitution. No bound context handle in the denial backend.",
                   "Privileged independent observer proves the selected row exists before SELECT, INSERT candidate absent with valid required parents, DELETE leaf exists and has no child reference, all trigger states restored, expected role/schema/table/column privilege metadata.",
                   "A type, NOT NULL, enum, nativeCHECK, FK, missing-row, trigger-raised error or unavailable role is not the expected native ACL denial. Stop and classify; do not convert toPASS.",
                   "On each denial/unexpected outcome close the exact client/backend before independent unchanged-row/row-count/native-catalog observations; never export arbitrary row or diagnostic bytes.",
                   "Unavailable owner positives and blocked native-ceiling facets remain separate NOT_RUN obligations; no 40/94/451 PASS inference from packet presence or repeated statements."],
              "cases": cases, "preparation_blocks": preparation_blocks, "synthetic_facts": facts,
              "files_sha256": {name: digest(value.encode("utf8")) for name, value in sorted(files.items())}}
    files["packet.json"] = json.dumps(result, indent=2) + "\n"
    return files, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    try:
        files, packet = build()
    except factory.PreparationBlocked as error:
        print(json.dumps({"status": "PREPARATION_BLOCKED", "reason": str(error), "database_contacted": False})); return 1
    if args.prepare:
        OUT.mkdir(parents=True, exist_ok=False)
        for name, value in files.items():
            with (OUT / name).open("x", encoding="utf8", newline="\n") as file: file.write(value)
    print(json.dumps({"status": "PREPARED_NOT_RUN" if args.prepare else "PLAN_ONLY_NOT_RUN", "selected_cases": 40, "base_tables": 42, "native_checks": len(packet["offline_source_check_derivations"]), "files": len(files), "blocked_native_facets": len(packet["preparation_blocks"]), "database_contacted": False}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
