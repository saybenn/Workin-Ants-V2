"""Close source8 lease-renewal recipes and offline verdicts for a future Cloud owner."""

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import uuid


ROOT = Path(__file__).resolve().parents[3]
LEGACY = "review-output/lease-revoke-control-rehearsal"
CUSTOMER = "review-output/customer-stale-predecessor-v1"
HISTORY = "prisma/local-f0-runtime-lease-history-v1/migrations"
INITIAL = f"{HISTORY}/20261117000100_f0_local_initial/migration.sql"
APPEND = f"{HISTORY}/20261120000100_f0_runtime_lease_branch_v1/migration.sql"
EXPECTED = "review-output/native-runtime-lease-history-v1/expected.json"
COLLECTOR = "scripts/sql-review/collect_native_catalog.sql"
ACL = "review-output/runtime-lease-branch-v1/worker-acl32.json"
POLICY = "context/reconciliation/foundation-sql-scope-policy.json"
APP = "scripts/sql-review/cloud-app-source8-v1"
WORKER = "scripts/sql-review/cloud-worker-source8-v1"
EVIDENCE = "context/reconciliation/cloud-phase0-evidence/2026-11-27"
PRIOR_WORKER = f"{EVIDENCE}/worker-fbcb03f7"
WORKER_ACCEPTED = f"{PRIOR_WORKER}/acceptance.json"
WORKER_CLOSURE = f"{PRIOR_WORKER}/independent-closure.json"
WORKER_RUN = "fbcb03f7-78f1-4f60-8516-5085dce1dcb3"
WORKER_SOURCE = {"commit": "0dbc8f11eb1bfc3a5bebb6bf7db4a154590eebab", "tree": "51b62b073c1d006f52dad0b9aca48a7eefb53ede"}
GUARD = "platform_private.runtime_transition()"
GUARD_SHA = "dee63b1c682a3cdef8a125df691fa2d4a2ee163b7afc43f740ce04f8f41ae965"
GUARD_LINE = 31
MESSAGE = "renewal requires current secret and extends live lease"
CASES = ("worker-claim", "current-holder-renew", "shorten-renew-denied", "copied-hash-renew-denied")
DENIALS = CASES[2:]
HASH = re.compile(r"[0-9a-f]{64}")
XID = re.compile(r"[1-9][0-9]{0,19}")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")
ISOTIME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z")
LEGACY_PINS = {
    "fixtures.json": "fe59a9867093f1cbab01741fa7d4f1fd727090e410374e663bbbd0796903c7e5",
    "source-lease.sql": "3debd8756886b1a4e7ad67aa2e8e1c32e4b58bca1b13f6d6d9d976a250cd05e7",
    "source-lease-observe.sql": "a9a4cfb353e2523b6230158c8d3b05169238a84f6ac72b452397aa7d45294858",
    "schedule-lease.sql": "f04abc17f549dc7a372b8c87294c4749fea757b5e9a5848fdcea6c85074bde79",
    "identity-worker-bootstrap.sql": "ec7afe38adcae4f5352048bd9fe1e5f0675b6851ab0734029719e309d158e452",
    "worker-claim.sql": "5573e8eec3c175e5b9da27165e4fb3af4eda1e4efa7d429f618dddb40d5ae5ed",
    "worker-renew.sql": "4ef30b44a6dd0a1ab86e09593603b72d70d7b5a1751ce49d8be804d0b802091f",
    "current-holder-renew.sql": "a6fa47f8f429b59a4283d9982c364bf9c3154c43d0040dcce5ad09568d48c901",
    "shorten-renew-denied.sql": "74a5d45f0d526ea6293c9fae7c84d3cd6de6279ba4981e3f705df2c018c22a7c",
    "copied-hash-renew-denied.sql": "fd0941f524cfe6c59b5114c03106a603ace1c02a64bc27e109ac2cba76bffedf",
}
PINS = {
    INITIAL: "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad",
    APPEND: "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7",
    EXPECTED: "4f0fabc35968074f5d00e14c69771343d4e3efe118c92824c503ada0b9bdbc09",
    COLLECTOR: "9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f",
    ACL: "6909f3cd9e2a795d1f39379b7f81db4c24f9526e235e802deea5ce1a2da8e5a3",
    POLICY: "a1c56896b12e15e03eb04bef6d5c9254692cdc3918167e024e54006b6fa38b1b",
    f"{CUSTOMER}/fixtures.json": "c2074a45f80147833e958d1f02b5d3840b32eb13a46033ebc7f1e75c322eb10b",
    f"{CUSTOMER}/trusted-identity-setup.sql": "4591ad24fab48064e3b51a310b82a47f8b525df81efb20a24a6b15271bb00bbb",
    f"{CUSTOMER}/all100-trigger-observe.sql": "1d46c9826a023fc320cf2837689f7c37f4edcd9e07a9f6861e6ab9d0b3503f26",
    f"{CUSTOMER}/full42-state-observe.sql": "9734d1ac9ac7488aa6b680168ba2e1949df42e8631fac9345c51a93023fdb06d",
    f"{APP}/host_session.py": "0149b82add667b485a2d6e044ee252f5f30add8db8ea87df9147cf9181fe3757",
    f"{APP}/app_child.py": "5f3a616745ba26ad6baae8266bbb254b4d791510289a1ba290bb30002fc5acfc",
    f"{WORKER}/worker_child.py": "433df6d90d62fa9ea23d2c16f5a880d66b243ea4d56810b8e2866a3c33b2145b",
    f"{WORKER}/operation.py": "b357edc5da987885bb09a049abee77da09eff1002dc73013a11c15defc07fe7e",
    "scripts/sql-review/run-context-control-rehearsal.py": "5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33",
    "scripts/lease_revoke_control_protocol.py": "df6754f7a01b721d9c4ca300956626c3798014cff1d4e117e4c1aba2a9745394",
    f"{EVIDENCE}/two-2f71c365/acceptance.json": "9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76",
    f"{EVIDENCE}/app-2e59e073/acceptance.json": "af7258881decbf7d78f1c413a4283f64d7b0235d48c3c7f2200f8b683a69f7cc",
    f"{PRIOR_WORKER}/operation.json": "9b68dd75d15cca5c7d4d0582ed42b1e48fc3b33677982834422de22508343afe",
    f"{PRIOR_WORKER}/operation-exit.json": "803c9069715b9e1a3c10bde5c4bd226336fc49e3be1a0399c5051ba49d471d35",
    f"{PRIOR_WORKER}/evidence/run-evidence.json": "b05e9524b97d9776434fca78aaef4417e33e5ae8f3e8c392e57f0df96c5e0296",
    f"{PRIOR_WORKER}/evidence/worker-source8/worker-recovery-results.json": "d643f46fa8b602efcc38e2c91142e274c3c9eadac36f077443cbf30aeed8a6c6",
    WORKER_ACCEPTED: "a3cdf096bb6ba19cb18c72e70b8758818e3dbc75664c4348f662b579a7ff794e",
    WORKER_CLOSURE: "10506bbc94c8581b671a2e583296bb9c5b372b804112bc5b57c1e7bcfe445176",
    **{f"{LEGACY}/{leaf}": value for leaf, value in LEGACY_PINS.items()},
}


def require(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()


def checked_inputs(root):
    blobs = {name: (root / name).read_bytes() for name in PINS}
    require(all(sha(blobs[name]) == digest for name, digest in PINS.items()), "LEASE_RENEW_PINNED_SOURCE_DRIFT")
    return blobs


def worker_reference(blobs):
    operation, report, component, terminal = (json.loads(blobs[f"{PRIOR_WORKER}/{leaf}"]) for leaf in (
        "operation.json", "evidence/run-evidence.json", "evidence/worker-source8/worker-recovery-results.json", "operation-exit.json"))
    names = [row["case"] for row in component["results"]]
    shared = (f"{APP}/app_child.py", f"{APP}/host_session.py", f"{WORKER}/worker_child.py", f"{WORKER}/operation.py")
    require(operation["source"] == WORKER_SOURCE and operation["run_id"] == report["run_id"] == component["run_id"]
            == terminal["run_id"] == WORKER_RUN and terminal["exit_code"] == 0
            and component["packet_sha256"] == report["approved_packet_sha256"] == PINS[f"{PRIOR_WORKER}/operation.json"]
            and all(operation["source_pins"][name] == PINS[name] for name in shared)
            and component["status"] == report["worker_source8"]["status"] == "PASS_FINITE_WORKER_RECOVERY_CORE_ONLY"
            and component["evidence_complete"] is True and report["worker_source8"]["global_client_closure"] is True
            and report["worker_source8"]["complete42_unchanged"] is True and report["cleanup_full_container_identity_absent"] is True
            and report["cleanup"] == "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
            and report["transport"]["unknown_closure"] is False and len(names) == 21 and len(set(names)) == 21
            and not any("renew" in name.lower() for name in names), "LEASE_RENEW_PRIOR_WORKER_SCOPE")
    acceptance, closure = json.loads(blobs[WORKER_ACCEPTED]), json.loads(blobs[WORKER_CLOSURE])
    require(acceptance["decision"] == "ACCEPT_EXACT_SCOPED_WORKER_SQL_CORE_AND_CLEANUP"
            and closure["decision"] == "EXACT_FINITE_WORKER_SQL_CORE_AND_CLEANUP_VERIFIED"
            and acceptance["run_id"] == closure["run_id"] == WORKER_RUN
            and acceptance["source_commit"] == closure["source_commit"] == WORKER_SOURCE["commit"]
            and acceptance["source_tree"] == closure["source_tree"] == WORKER_SOURCE["tree"]
            and acceptance["independent_reviewer"] == closure["reviewer"]
            and acceptance["independent_closure_sha256"] == PINS[WORKER_CLOSURE]
            and acceptance["operator_exit_code"] == closure["operator_exit_code"] == 0
            and acceptance["authenticated_case_count"] == len(names)
            and acceptance["postchecks"]["native_and_ledger_identical_through_worker"] is True
            and len(closure["cleanup_verified"]) == 8 and all(value is True for value in closure["cleanup_verified"].values())
            and all(acceptance["archived_files_sha256"][leaf] == closure["file_sha256"][leaf] == PINS[f"{PRIOR_WORKER}/{leaf}"]
                    for leaf in ("operation.json", "operation-exit.json", "evidence/run-evidence.json",
                                 "evidence/worker-source8/worker-recovery-results.json")), "LEASE_RENEW_INDEPENDENT_PRIOR_WORKER_CLOSURE")
    return {"run_id": WORKER_RUN, "source": WORKER_SOURCE, "actual_prior_cases": 21, "dedicated_renewal_observed": False,
            "transports_sha256": {name: PINS[name] for name in shared}, "acceptance_sha256": PINS[WORKER_ACCEPTED],
            "independent_closure_sha256": PINS[WORKER_CLOSURE]}


def guard_reference(blobs):
    append = blobs[APPEND].decode()
    body = re.findall(r"CREATE OR REPLACE FUNCTION platform_private\.runtime_transition\(\).*?AS\s+(\$wa\$)(.*?)\1;", append, re.S)
    native = json.loads(blobs[EXPECTED])
    require(len(body) == 1 and sha(body[0][1].encode()) == native["expected"]["functions"][GUARD]["body_sha256"] == GUARD_SHA
            and len(body[0][1].split("\n")) == 74
            and f"RAISE EXCEPTION '{MESSAGE}'" in body[0][1].split("\n")[GUARD_LINE - 1], "LEASE_RENEW_SOURCE8_GUARD_DRIFT")
    return {"sqlstate": "P0001", "message": MESSAGE, "function": GUARD, "body_line": GUARD_LINE, "body_sha256": GUARD_SHA}


def splice(value, replacements):
    pattern = "|".join(re.escape(key) for key in sorted(replacements, key=len, reverse=True))
    return re.sub(pattern, lambda match: replacements[match[0]], value)


def marker(name, where):
    require(name in CASES and where in ("BEFORE", "AFTER"), "LEASE_RENEW_CASE_SCOPE")
    return "WA_LR_" + where + "_" + name.upper().replace("-", "_")


def commit_receipt(name, rc, rows, acknowledged, stderr):
    require(name in CASES[:2], "LEASE_RENEW_COMMIT_SCOPE")
    good = (type(rc) is int and rc == 0 and type(rows) is list and len(rows) == 3 and acknowledged is True and stderr == ""
            and rows[0] == marker(name, "BEFORE") and rows[2] == marker(name, "AFTER")
            and type(rows[1]) is str and re.fullmatch(r'\{[ \t]*"changed"[ \t]*:[ \t]*1[ \t]*\}', rows[1]) is not None)
    return {"exact_committed_work_change": good, "changed_rows": 1 if good else None}


def diagnostic_receipt(name, rc, rows, acknowledged, stderr):
    require(name in DENIALS, "LEASE_RENEW_DENIAL_SCOPE")
    header = r"(?:psql:(?:<stdin>|-):[1-9][0-9]{0,5}: )?ERROR:[ \t]+P0001: "
    frame = rf"CONTEXT:[ \t]+PL/pgSQL function {re.escape(GUARD)} line {GUARD_LINE} at RAISE\n"
    location = r"LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}\n"
    good = (type(rc) is int and rc == 3 and rows == [marker(name, "BEFORE")] and acknowledged is False
            and type(stderr) is str and len(stderr) <= 512
            and re.fullmatch(header + MESSAGE + "\n" + frame + location, stderr.replace("\r\n", "\n")) is not None)
    return {"exact_denial": good, "sqlstate": "P0001" if good else None, "body_line": GUARD_LINE if good else None,
            "body_sha256": GUARD_SHA if good else None}


def live_state(state, xid):
    return (type(state) is dict and set(state) == {"deadline", "live", "domain_sha256", "row_sha256", "mutation_xid"}
            and state["live"] is True and state["mutation_xid"] == xid and XID.fullmatch(xid) is not None
            and all(type(state[key]) is str and HASH.fullmatch(state[key]) is not None for key in ("domain_sha256", "row_sha256"))
            and type(state["deadline"]) is str and ISOTIME.fullmatch(state["deadline"]) is not None)


def renewal_delta(before, after, claim_xid, renew_xid):
    if not (type(claim_xid) is str and type(renew_xid) is str and claim_xid != renew_xid
            and live_state(before, claim_xid) and live_state(after, renew_xid)):
        return False
    try:
        increased = datetime.fromisoformat(after["deadline"]) > datetime.fromisoformat(before["deadline"])
    except ValueError:
        return False
    return increased and before["domain_sha256"] == after["domain_sha256"] and before["row_sha256"] != after["row_sha256"]


def exact_negative_state(after_renew, after_denial, renewal_xid):
    return (type(renewal_xid) is str and live_state(after_renew, renewal_xid) and live_state(after_denial, renewal_xid)
            and canonical(after_renew) == canonical(after_denial))


def observe_work(work_id, outbox_id, semantic):
    return f"""SELECT jsonb_build_object(
    'deadline',to_char(lease_expires_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'live',lease_expires_at>clock_timestamp(), 'mutation_xid',mutation_transaction_id,
    'domain_sha256',encode(sha256(convert_to((to_jsonb(w)-ARRAY['lease_expires_at','mutation_transaction_id'])::text,'UTF8')),'hex'),
    'row_sha256',encode(sha256(convert_to(to_jsonb(w)::text,'UTF8')),'hex'))
FROM platform.runtime_work_item w WHERE id='{work_id}'::uuid AND outbox_message_id='{outbox_id}'::uuid
    AND handler_name='assignDefaultFreeTrack.v1' AND semantic_work_key='{semantic}'
    AND state='leased' AND fence=1 AND attempt_count=1 AND effect_receipt_id IS NULL
    AND lease_token_hash='__ACTUAL_LEASE_HASH__';
"""


def restricted_renew_preflight(work_id):
    return f"""SELECT jsonb_build_object(
    'visible_work',count(*), 'exact_route',
    platform_private.context_allows('platform_integration_owner','runtime.renew_work.v1','RuntimeWorkItem','{work_id}','work.renew'),
    'minimum_server_reserve',coalesce(bool_and(lease_expires_at>clock_timestamp()+interval '2 seconds'),false),
    'matches_preimage',coalesce(bool_and(platform_private.lease_secret_matches(lease_token_hash::text)),false))
FROM platform.runtime_work_item WHERE id='{work_id}'::uuid AND state='leased' AND fence=1 AND attempt_count=1
    AND effect_receipt_id IS NULL AND lease_token_hash='__ACTUAL_LEASE_HASH__';
"""


def work_observer_sql(template, actual_hash):
    marker = "__ACTUAL_LEASE_HASH__"
    require(type(actual_hash) is str and HASH.fullmatch(actual_hash) and template.count(marker) == 1,
            "LEASE_RENEW_EXACT_WORK_HASH_BINDING")
    return template.replace(marker, actual_hash)


def full_state_observer_sql(template, grant_ids):
    marker = "__EXCLUDED_GRANT_IDS__"
    require(type(grant_ids) is tuple and len(grant_ids) <= 6 and all(
        type(value) is str and UUID.fullmatch(value) and uuid.UUID(value).version == 4 for value in grant_ids
    ) and len(set(grant_ids)) == len(grant_ids) and template.count(marker) == 1, "LEASE_RENEW_EXACT_GRANT_EXCLUSIONS")
    bindings = "ARRAY[" + ",".join(f"'{value}'::uuid" for value in grant_ids) + "]::uuid[]"
    return template.replace(marker, bindings)


def worker_grants(fixture, blobs, replacements, work_id):
    catalog = json.loads(blobs[ACL])
    acl = {row["operation"]: set(row["fields"]) for row in catalog if row["model"] == "RuntimeWorkItem"}
    policy = json.loads(blobs[POLICY])["runtime_work_scopes"]
    require(len(catalog) == fixture["worker_acl_rows"] == 32, "LEASE_RENEW_WORKER_ACL_SCOPE")
    values = {}
    for key in ("source-lease", "schedule-lease", "claim-0", "renew-1"):
        original = fixture["grants"][key]
        remapped = json.loads(splice(canonical(original).decode(), replacements))
        fields = remapped["allowed_fields"]
        require(len(fields) == len(set(fields)) == len(original["allowed_fields"]), "LEASE_RENEW_GRANT_CAPABILITIES")
        remapped["allowed_fields"] = sorted(fields)
        values[key] = remapped
    for key, generation, changed in (("claim-0", "0", {"state", "fence", "attemptCount", "leaseTokenHash", "leaseExpiresAt"}),
                                      ("renew-1", "1", {"leaseExpiresAt"})):
        grant = values[key]
        root = f"RuntimeWorkItem/{work_id}/"
        expected = {root + "SELECT/" + name for name in acl["SELECT"]} | {root + "UPDATE/" + name for name in changed | {"@row"}}
        expected.add(root + "revision/" + generation)
        require(changed <= acl["UPDATE"] and set(grant["allowed_fields"]) == expected
                and str(grant["source_generation"]) == generation and grant["target_id"] == work_id and grant["database_login_role"] == "wa_worker"
                and {"owner": grant["owner_module_id"], "action": grant["action"], "purpose": grant["purpose"]} in policy,
                "LEASE_RENEW_PREDECESSOR_FIELD_SCOPE")
    return values


def source_assets(blobs, fixture, run):
    source = fixture["sources"]["lease"]
    old_work = fixture["work_ids"]["lease"]
    old_receipt = fixture["identity_receipts"]["worker"]["bootstrap"]
    old_service = fixture["services"]["worker"]
    fresh_worker = f"lease-renew-cloud-{run.hex}.v1"
    old_semantic = source["semantic_key"]
    new_semantic = f"customer-controls-lease-renew-cloud-{run.hex}"
    old_fingerprint, new_fingerprint = (sha(("synthetic-intent:" + value).encode()) for value in (old_semantic, new_semantic))
    remap = {value: str(uuid.uuid5(run, name)) for name, value in (source["ids"] | {"work": old_work, "service-receipt": old_receipt}).items()}
    work_id, outbox = remap[old_work], remap[source["ids"]["free"]]
    remap.update({old_semantic: new_semantic, "lease-revoke-lease": f"lease-renew-cloud-{run.hex}", old_fingerprint: new_fingerprint,
                  old_service: fresh_worker, "synthetic-lease-revoke-worker-bootstrap.v1": f"synthetic-{fresh_worker}"})
    outputs = {}
    for leaf in ("source-lease.sql", "source-lease-observe.sql", "schedule-lease.sql", "identity-worker-bootstrap.sql",
                 *(name + ".sql" for name in CASES)):
        original = blobs[f"{LEGACY}/{leaf}"].decode()
        require(fixture["prepared_files_sha256"][leaf] == LEGACY_PINS[leaf], "LEASE_RENEW_HISTORICAL_LEAF_DRIFT")
        text = splice(original, remap)
        if leaf.removesuffix(".sql") in DENIALS:
            require(text.endswith("\nCOMMIT;\n") and text.count("COMMIT;") == 1, "LEASE_RENEW_NEGATIVE_ROLLBACK_SEAM")
            text = text.removesuffix("COMMIT;\n") + "ROLLBACK;\n"
        outputs[leaf] = text
    customer = json.loads(blobs[f"{CUSTOMER}/fixtures.json"])
    user = remap[source["ids"]["user"]]
    seed = {customer["baseline"]["grant"]["principal_user_id"]: user,
            customer["identity_security_profile_id"]: str(uuid.uuid5(run, "security-profile"))}
    outputs["identity-seed.sql"] = splice(blobs[f"{CUSTOMER}/trusted-identity-setup.sql"].decode(), seed)
    outputs["all100-trigger-observe.sql"] = blobs[f"{CUSTOMER}/all100-trigger-observe.sql"].decode()
    full = blobs[f"{CUSTOMER}/full42-state-observe.sql"].decode()
    leaf = " ORDER BY table_name) FROM ("
    require(full.count(leaf) == 1, "LEASE_RENEW_EXACT_OUTER_SORT")
    outputs["full42-state-observe.sql"] = full.replace(leaf, ' ORDER BY table_name COLLATE "C") FROM (', 1)
    semantic = splice(source["fixture_values"]["free_command"]["semanticKey"], remap)
    outputs["work-state-observe.sql"] = observe_work(work_id, outbox, semantic)
    outputs["restricted-renew-preflight.sql"] = restricted_renew_preflight(work_id)
    identity = {"work_id": work_id, "outbox_id": outbox, "worker_service": fresh_worker, "worker_service_receipt": remap[old_receipt],
                "worker_service_authorization_ref": f"synthetic-{fresh_worker}",
                "customer_id": remap[source["ids"]["CustomerProfile"]], "synthetic_user_id": user,
                "synthetic_security_id": seed[customer["identity_security_profile_id"]]}
    return outputs, worker_grants(fixture, blobs, remap, work_id), identity, customer["full42_tables"]


def assemble(fixture_id, root=ROOT):
    require(type(fixture_id) is str and UUID.fullmatch(fixture_id) and uuid.UUID(fixture_id).version == 4, "LEASE_RENEW_FRESH_FIXTURE_ID")
    blobs = checked_inputs(root)
    legacy = json.loads(blobs[f"{LEGACY}/fixtures.json"])
    assets, grants, identity, tables = source_assets(blobs, legacy, uuid.UUID(fixture_id))
    packet = {
        "schema": "workinants.cloud-lease-renew-source8-held.v1", "runtime": "NOT_RUN", "posture": "D", "assertion_promotions": 0,
        "fixture_run_id": fixture_id, "source_pins": PINS, "asset_sha256": {leaf: sha(text.encode()) for leaf, text in assets.items()},
        "identity": identity, "grant_templates": grants, "statement_order": list(CASES), "full42_table_order": tables,
        "expected_restricted_customer_source": legacy["sources"]["lease"]["observer_expected"],
        "claim": {"qualified_ceiling_if_independently_proven": "P0C-TRACK-01/vector.LEASE-RENEW.positive",
                  "two_partial_adversarial_controls": list(DENIALS), "whole_adversarial_vector": "NOT_RUN"},
        "route": {"worker_queued_claim_only": True, "fresh_renew_grant_for_each_step": True, "service_generation": 0,
                  "work_fence": 1, "initial_lease_seconds": 12, "renewal_seconds": 90, "work_attempt_count": 1,
                  "maximum_issuer_grants": 6, "one_open_worker_at_a_time": True, "minimum_pre_action_server_reserve_seconds": 2},
        "native_expected_sha256": json.loads(blobs[EXPECTED])["expected_sha256"], "guard": guard_reference(blobs),
        "prior_worker_transport": worker_reference(blobs), "executable_owning_composition": "HELD_NOT_PREPARED",
    }
    return packet, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-run-id", required=True)
    packet, _ = assemble(parser.parse_args().fixture_run_id)
    print(canonical(packet).decode())


if __name__ == "__main__":
    main()
