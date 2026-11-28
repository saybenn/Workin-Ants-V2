"""Assemble the held empty-context proof from exact source8 without database access."""

import argparse
from pathlib import Path
import re
import uuid

from protocol import (BODY_LINE, BODY_SHA256, CASES, FUNCTION, MESSAGE, SQLSTATE, canonical,
                      markers, require, sha, state_observer_sql, strict_json, uuid4)


ROOT = Path(__file__).resolve().parents[3]
INITIAL = "review-output/foundation-application.review.sql"
MIGRATIONS = "prisma/local-f0-runtime-lease-history-v1/migrations"
INITIAL_HISTORY = f"{MIGRATIONS}/20261117000100_f0_local_initial/migration.sql"
APPEND = f"{MIGRATIONS}/20261120000100_f0_runtime_lease_branch_v1/migration.sql"
NATIVE_EXPECTED = "review-output/native-runtime-lease-history-v1/expected.json"
NATIVE_COLLECTOR = "scripts/sql-review/collect_native_catalog.sql"
CONTEXT = "scripts/sql-review/run-context-control-rehearsal.py"
APP_TRANSPORT = "scripts/sql-review/cloud-app-source8-v1/host_session.py"
CASE_PLAN = ("context/reconciliation/local-f0-source-followups/"
             "0ff-read1161-install6850-reviewed-V6-V8-20261120/Remaining-immutable-CAS-source-facts-PLAN.json")
POLICY = "context/reconciliation/foundation-sql-scope-policy.json"
PACKET = "review-output/customer-stale-predecessor-v1"
FIXTURE = f"{PACKET}/fixtures.json"
SEED = f"{PACKET}/trusted-identity-setup.sql"
TRIGGERS = f"{PACKET}/all100-trigger-observe.sql"
STATE = f"{PACKET}/full42-state-observe.sql"
SH_CONTRACT = "contracts/shared/SH-007.v1.schema.json"
SHA_INITIAL = "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad"
SHA_APPEND = "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7"
SHA_CATALOG = "cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4"
PINS = {
    INITIAL: SHA_INITIAL,
    INITIAL_HISTORY: SHA_INITIAL,
    APPEND: SHA_APPEND,
    NATIVE_EXPECTED: "4f0fabc35968074f5d00e14c69771343d4e3efe118c92824c503ada0b9bdbc09",
    NATIVE_COLLECTOR: "9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f",
    CONTEXT: "5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33",
    APP_TRANSPORT: "0149b82add667b485a2d6e044ee252f5f30add8db8ea87df9147cf9181fe3757",
    CASE_PLAN: "1b6985236eba944177f6055aec5408199f1e2fb5c8ec73218f75a3cea4980d2d",
    POLICY: "a1c56896b12e15e03eb04bef6d5c9254692cdc3918167e024e54006b6fa38b1b",
    FIXTURE: "c2074a45f80147833e958d1f02b5d3840b32eb13a46033ebc7f1e75c322eb10b",
    SEED: "4591ad24fab48064e3b51a310b82a47f8b525df81efb20a24a6b15271bb00bbb",
    TRIGGERS: "1d46c9826a023fc320cf2837689f7c37f4edcd9e07a9f6861e6ab9d0b3503f26",
    STATE: "9734d1ac9ac7488aa6b680168ba2e1949df42e8631fac9345c51a93023fdb06d",
    SH_CONTRACT: "ffa0c78ff33cf30e524ed2186fe1cde7fabe180ac3cd0ecc6f060598f9ff169f",
}
CASE_ID = "P0C-IMMUTABLE-01"
ASSERTION = "control.empty_context"
ASSERTION_SHA = "d66b619c87e226d08fa575c71b4485f1a6dff355bb8bca2478fca3e77a237fcd"
OWNER = "consent_disclosure"
PREFIX = (
    ("ConsentContentRevision", "consent_content_revision", "publishConsentVersion.v1", "consent.publish_version"),
    ("ConsentPresentation", "consent_presentation", "recordConsentPresentation.v1", "consent.record_presentation"),
    ("ConsentLog", "consent_logs", "SH-007.v1", "owner:recordConsentProof"),
)
CONTENT = "Synthetic Consent source text for a rollback-only database guard check."
RENDERED = "Synthetic Consent presentation for a rollback-only database guard check."
SCHEMA = "workinants.cloud-consent-empty-context-held.v1"
STATE_AGGREGATE = "SELECT jsonb_agg(jsonb_build_object('table',table_name,'count',row_count,'sha256',row_sha)"
PARENT_STATE_PREFIX = STATE_AGGREGATE + " ORDER BY table_name) FROM ("
CLOUD_STATE_PREFIX = STATE_AGGREGATE + ' ORDER BY table_name COLLATE "C") FROM ('


def quoted(value):
    return "'" + value.replace("'", "''") + "'"


def source_inputs(root):
    blobs = {path: (root / path).read_bytes() for path in PINS}
    require(all(sha(blobs[path]) == digest for path, digest in PINS.items()), "CONSENT_PINNED_SOURCE_DRIFT")
    source = blobs[INITIAL].decode()
    append = blobs[APPEND].decode()
    require(blobs[INITIAL] == blobs[INITIAL_HISTORY]
            and re.findall(r"CREATE OR REPLACE FUNCTION ([^(]+)\(", append) == ["platform_private.runtime_transition"],
            "CONSENT_SOURCE8_WRITER_HISTORY")

    def function_body(name):
        bodies = re.findall(rf"CREATE FUNCTION platform_private\.{name}\(.*?AS (\$wa\$)(.*?)\1;", source, re.S)
        require(len(bodies) == 1, "CONSENT_PINNED_FUNCTION_DECLARATION")
        return bodies[0][1]

    guard = function_body("consent_guard")
    require(sha(guard.encode()) == BODY_SHA256
            and "RAISE EXCEPTION 'exact consent binding required'" in guard.split("\n")[BODY_LINE - 1]
            and function_body("global_context_registered").strip() == "SELECT false;"
            and "GRANT EXECUTE ON FUNCTION platform_private.global_context_registered(text,text,text,text) TO wa_app_runtime,wa_worker;" in source,
            "CONSENT_PINNED_GUARD_SCOPE")
    plan = strict_json(blobs[CASE_PLAN])
    assertions = [row for row in plan["exact_selected_assertions"] if row["assertion_id"] == ASSERTION]
    require(len(assertions) == 1 and assertions[0]["case_id"] == CASE_ID
            and assertions[0]["expected_assertion_sha256"] == ASSERTION_SHA
            and assertions[0]["actual_status"] == "NOT_RUN", "CONSENT_CASE_PLAN_SCOPE")
    native = strict_json(blobs[NATIVE_EXPECTED])
    require(native["expected_sha256"] == SHA_CATALOG, "CONSENT_EFFECTIVE_CATALOG_DRIFT")
    return blobs


def fields(source, model, table, verb):
    prefix = rf'CREATE POLICY "p_app_runtime_{verb.lower()}" ON "app"\."{table}".*?'
    pattern = prefix + rf"row_allowed\('{OWNER}','{model}',\"id\"::text,'{verb}',ARRAY\[(.*?)\]::text\[\]"
    matches = re.findall(pattern, source)
    require(len(matches) == 1, "CONSENT_RLS_FIELD_SCOPE")
    leaves = re.findall(r"'([A-Za-z][A-Za-z0-9]*)'", matches[0])
    require(leaves and len(leaves) == len(set(leaves)) and ",".join(map(quoted, leaves)) == matches[0],
            "CONSENT_RLS_FIELD_SCOPE")
    return leaves


def grants(blobs, principal, roots):
    scopes = strict_json(blobs[POLICY])["domain_scopes"]
    source = blobs[INITIAL].decode()
    models = {model: table for model, table, _, _ in PREFIX}
    expected_relations = ({}, {"ConsentContentRevision": "contentRevision"},
                          {"ConsentPresentation": "presentation", "ConsentContentRevision": "contentRevision"})
    values = []
    for (model, table, action, purpose), relations in zip(PREFIX, expected_relations, strict=True):
        matches = [row for row in scopes if (row["owner"], row["action"], row["purpose"], row["root_kind"])
                   == (OWNER, action, purpose, model)]
        require(len(matches) == 1 and set(matches[0]["verbs"]) >= {"SELECT", "INSERT"}
                and matches[0].get("related_reads", {}) == relations, "CONSENT_ACTION_SCOPE")
        root = roots[model]
        tokens = [f"{model}/{root}/{verb}/{leaf}" for verb in ("INSERT", "SELECT")
                  for leaf in fields(source, model, table, verb)]
        for related, relation in relations.items():
            tokens.append(f"{model}/{root}/{relation}/{roots[related]}")
            tokens.extend(f"{related}/{roots[related]}/SELECT/{leaf}"
                          for leaf in fields(source, related, models[related], "SELECT"))
        require(len(tokens) == len(set(tokens)) and len(tokens) <= 64, "CONSENT_FINITE_CAPABILITIES")
        values.append({
            "principal_user_id": principal, "service_principal": None, "database_login_role": "wa_app_runtime",
            "owner_module_id": OWNER, "action": action, "purpose": purpose, "target_kind": model,
            "target_id": root, "allowed_fields": sorted(tokens), "policy_version": "cloud-consent-empty-context-fixture.v1",
            "security_generation": 0, "source_generation": 0,
        })
    return values


def identity_seed(blobs, user, security):
    previous = strict_json(blobs[FIXTURE])
    old_user = previous["baseline"]["grant"]["principal_user_id"]
    old_security = previous["identity_security_profile_id"]
    raw = blobs[SEED].decode()
    require(raw.count(old_user) == 2 and raw.count(old_security) == 1, "CONSENT_SYNTHETIC_IDENTITY_SEED_BOUNDARY")
    return raw.replace(old_user, user).replace(old_security, security)


def digest_sql(text):
    return f"encode(sha256(convert_to({text},'UTF8')),'hex')"


def case_sql(case, user, roots, label):
    uid, key = quoted(user), quoted(label)
    content_id, presentation_id, proof_id = (quoted(roots[model]) for model, *_ in PREFIX)
    context = "NULL" if case == CASES[0] else "''"
    content, rendered = quoted(CONTENT), quoted(RENDERED)
    content_hash, rendered_hash = digest_sql(content), digest_sql(rendered)
    before, after = map(quoted, markers(case))

    publish = f"""INSERT INTO app.consent_content_revision
    (id,type,version,locale,jurisdiction_scope,content_text,content_hash,review_state,effective_from,effective_until)
VALUES ({content_id},'terms',{key},'en','synthetic',{content},{content_hash},'test_only',
    transaction_timestamp() - interval '1 day',transaction_timestamp() + interval '1 day')
RETURNING jsonb_build_object('one_exact_prefix',id={content_id}::uuid AND type='terms'
    AND version={key} AND content_text={content} AND content_hash={content_hash}
    AND review_state='test_only' AND legal_approval_ref IS NULL);
"""
    present = f"""INSERT INTO app.consent_presentation
    (id,content_revision_id,user_id,action_owner,action,render_version,rendered_text,rendered_hash,context_owner,context_kind,context_id)
VALUES ({presentation_id},{content_id},{uid},'{OWNER}','SH-007.v1','cloud-consent-empty-context.v1',
    {rendered},{rendered_hash},'{OWNER}','ConsentLog',{context})
RETURNING jsonb_build_object('one_exact_prefix',id={presentation_id}::uuid AND content_revision_id={content_id}::uuid
    AND user_id={uid}::uuid AND rendered_text={rendered} AND rendered_hash={rendered_hash}
    AND context_id IS NOT DISTINCT FROM {context});
"""
    preread = f"""SELECT jsonb_build_object(
    'exact_prerequisite_rows',count(*),
    'all_other_binding_predicates_exact',coalesce(bool_and(
        p.user_id={uid}::uuid AND c.type='terms' AND c.version={key} AND c.review_state='test_only'
        AND p.rendered_hash={rendered_hash} AND p.action_owner='{OWNER}' AND p.action='SH-007.v1'
        AND p.context_owner='{OWNER}' AND p.context_kind='ConsentLog'
        AND p.context_id IS NOT DISTINCT FROM {context}
        AND p.created_at>=c.effective_from AND p.created_at<c.effective_until
        AND platform_private.context_subject({uid}::uuid)),false),
    'global_registry_admits',coalesce(bool_or(platform_private.global_context_registered(
        p.action_owner,p.action,p.context_owner,p.context_kind)),true))
FROM app.consent_presentation p JOIN app.consent_content_revision c ON c.id=p.content_revision_id
WHERE p.id={presentation_id}::uuid AND c.id={content_id}::uuid;
"""
    denial = f"""SELECT {before};
INSERT INTO app.consent_logs
    (id,user_id,type,version,accepted_at,acceptance_key,fingerprint,action_owner,action,
     context_owner,context_kind,context_id,presentation_hash,content_revision_id,presentation_id)
SELECT {proof_id}::uuid,{uid}::uuid,'terms'::app.consent_type,{key},p.created_at,{key},{digest_sql(key)},
    '{OWNER}','SH-007.v1','{OWNER}','ConsentLog',{context},{rendered_hash},{content_id}::uuid,p.id
FROM app.consent_presentation p WHERE p.id={presentation_id}::uuid;
SELECT {after};
ROLLBACK;
"""
    absent = f"""NOT EXISTS (SELECT FROM app.consent_content_revision WHERE id={content_id}::uuid OR version={key})
AND NOT EXISTS (SELECT FROM app.consent_presentation WHERE id={presentation_id}::uuid)
AND NOT EXISTS (SELECT FROM app.consent_logs WHERE id={proof_id}::uuid OR (user_id={uid}::uuid AND acceptance_key={key}))"""
    return {"publisher.sql": publish, "presentation.sql": present, "preread.sql": preread,
            "deny.sql": denial, "zero-case-residue.sql": f"SELECT {absent};\n"}


def parser():
    import pglast
    from pglast import parser as native

    require(pglast.__version__ == "v7.21"
            and sha(Path(pglast.__file__).read_bytes()) == "e085f1a529eedc4e9ddeecbd406255ed8580f4cef00b13a33e7fd056d8374084"
            and sha(Path(native.__file__).read_bytes()) == "c2ab2648a942b314ffcd7ab38f25c052ca08adc323fa556b0ed68b727320e711",
            "CONSENT_PINNED_PGLAST_REQUIRED")
    return pglast


def inspect_sql(assets):
    pg = parser()

    def shape(text):
        return tuple(type(item.stmt).__name__ for item in pg.parse_sql(text))

    require(shape(assets["identity-seed.sql"]) == ("TransactionStmt", "AlterTableStmt", "AlterTableStmt", "InsertStmt",
                                                  "InsertStmt", "ConstraintsSetStmt", "AlterTableStmt", "AlterTableStmt",
                                                  "ConstraintsSetStmt", "TransactionStmt"), "CONSENT_IDENTITY_SEED_SQL_SHAPE")
    require(shape(assets["fresh-namespace.sql"]) == shape(assets["identity-present.sql"]) == ("SelectStmt",),
            "CONSENT_NAMESPACE_OBSERVER_SQL_SHAPE")
    require(shape(state_observer_sql(assets["full42-state.sql"], ())) == ("SelectStmt",)
            and shape(assets["trigger-observer.sql"]) == ("SelectStmt",), "CONSENT_CLOSED_STATE_OBSERVER_SHAPE")
    for case in CASES:
        for leaf, table in (("publisher.sql", "consent_content_revision"), ("presentation.sql", "consent_presentation"),
                            ("deny.sql", "consent_logs")):
            nodes = [item.stmt for item in pg.parse_sql(assets[f"{case}/{leaf}"])]
            if leaf == "deny.sql":
                require(tuple(type(item).__name__ for item in nodes) == (
                    "SelectStmt", "InsertStmt", "SelectStmt", "TransactionStmt")
                    and nodes[-1].kind.name == "TRANS_STMT_ROLLBACK", "CONSENT_DENIAL_ONLY_SQL_SHAPE")
                statement = nodes[1]
            else:
                require(len(nodes) == 1 and type(nodes[0]).__name__ == "InsertStmt", "CONSENT_PREFIX_ONLY_SQL_SHAPE")
                statement = nodes[0]
            require((statement.relation.schemaname, statement.relation.relname) == ("app", table)
                    and statement.onConflictClause is None, "CONSENT_RESTRICTED_INSERT_TARGET")
        for leaf in ("preread.sql", "zero-case-residue.sql"):
            require(shape(assets[f"{case}/{leaf}"]) == ("SelectStmt",), "CONSENT_ROLLBACK_OBSERVER_SQL_SHAPE")


def assemble(fixture_run_id, root=ROOT):
    require(uuid4(fixture_run_id), "CONSENT_FIXTURE_UUID4_REQUIRED")
    blobs = source_inputs(root)
    run = uuid.UUID(fixture_run_id)
    user, security = (str(uuid.uuid5(run, name)) for name in ("synthetic-user", "synthetic-user-security"))
    source = strict_json(blobs[FIXTURE])
    state_sql = blobs[STATE].decode()
    require(state_sql.startswith(PARENT_STATE_PREFIX) and state_sql.count(PARENT_STATE_PREFIX) == 1,
            "CONSENT_PINNED_STATE_ORDER")
    assets = {
        "identity-seed.sql": identity_seed(blobs, user, security),
        "trigger-observer.sql": blobs[TRIGGERS].decode(),
        "full42-state.sql": CLOUD_STATE_PREFIX + state_sql.removeprefix(PARENT_STATE_PREFIX),
        "identity-present.sql": ("SELECT count(*)=1 FROM app.users u JOIN app.user_security_profiles s ON s.user_id=u.id "
                                 f"WHERE u.id='{user}'::uuid AND s.id='{security}'::uuid AND NOT u.is_public "
                                 "AND u.revision=0 AND u.privacy_generation=0 AND s.revision=0 AND s.security_generation=0;\n"),
    }
    cases = []
    for case in CASES:
        roots = {model: str(uuid.uuid5(run, f"{case}/{model}")) for model, *_ in PREFIX}
        generated = case_sql(case, user, roots, f"cloud-consent-empty.{run.hex}.{case}")
        assets.update({f"{case}/{leaf}": body for leaf, body in generated.items()})
        cases.append({"name": case, "grants_in_order": grants(blobs, user, roots), "status": "NOT_RUN"})
    assets["fresh-namespace.sql"] = (
        f"SELECT NOT EXISTS (SELECT FROM app.users WHERE id='{user}'::uuid)\n"
        f"AND NOT EXISTS (SELECT FROM app.user_security_profiles WHERE id='{security}'::uuid OR user_id='{user}'::uuid)\n"
        f"AND NOT EXISTS (SELECT FROM platform.database_action_grant WHERE principal_user_id='{user}'::uuid)\n"
        + "\n".join("AND (" + assets[f"{case}/zero-case-residue.sql"].strip().removeprefix("SELECT ").removesuffix(";") + ")"
                    for case in CASES) + ";\n"
    )
    inspect_sql(assets)
    packet = {
        "schema": SCHEMA, "runtime": "NOT_RUN", "posture": "D", "assertion_promotions": 0,
        "execution_entry": "HELD_NO_CONSENT_OWNER_COMPOSITION", "case_id": CASE_ID, "assertion_id": ASSERTION,
        "assertion_expected_sha256": ASSERTION_SHA, "fixture_run_id": fixture_run_id,
        "source_pins": PINS, "source8_history_sha256": [SHA_INITIAL, SHA_APPEND],
        "expected_native_catalog_sha256": SHA_CATALOG,
        "grants_maximum": 6, "setup_only_trigger_exceptions": source["fixture_bypasses"],
        "full42_tables": source["full42_tables"], "cases": cases,
        "diagnostic": {"sqlstate": SQLSTATE, "message": MESSAGE, "function": FUNCTION,
                       "source_body_sha256": BODY_SHA256, "source_body_line": BODY_LINE,
                       "terminal_exit_code": 3},
        "source_asset_sha256": {leaf: sha(text.encode()) for leaf, text in sorted(assets.items())},
    }
    return packet, assets


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--fixture-run-id", required=True)
    args = cli.parse_args()
    packet, _ = assemble(args.fixture_run_id)
    print(canonical(packet).decode())


if __name__ == "__main__":
    main()
