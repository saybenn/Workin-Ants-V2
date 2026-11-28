"""Closed Customer receipts and independent state transitions."""

from datetime import datetime
import re

MODES = ("create-replay", "rollback", "retry")
PHASES = ("unborn", "seeded", *MODES)
NODE_SCHEMA = "workinants.p0d-customer-proof-result.v1"
NODE_PASS = "PASS_FINITE_CUSTOMER_MODE_ONLY"
RESPONSE = "P0D_CUSTOMER_CHILD_RESULT_UNCONFIRMED"
OBSERVATION = "P0D_CUSTOMER_SCOPE_OBSERVATION_UNCONFIRMED"
FULL42 = "P0D_CUSTOMER_FULL42_UNCONFIRMED"
NODE_STAGES = {
    "create-replay": {"COMPETING_KNOWN_CREATE", "EXACT_AND_METADATA_REPLAY", "FOREIGN_REQUEST_PRINCIPAL"},
    "rollback": {"FINAL_FREE_INTENT_RLS_ROLLBACK"}, "retry": {"ORIGINAL_KEY_RETRY"},
}
SYNTHETIC_STEPS = ("READ_EMPTY", "CLOCK_DATE", "RECEIPT_INSERTED", "CUSTOMER_INSERTED", "HISTORY_INSERTED",
                   "EVIDENCE_INSERTED", "LIFECYCLE_INSERTED", "FREE_INTENT_INSERTED")
CASE_EXPECTATIONS = {
    "create-replay": {
        "created": ("created", SYNTHETIC_STEPS),
        "contender": ("replay", ("READ_EMPTY", "CLOCK_DATE", "RECEIPT_CONFLICT_EMPTY", "READ_ROW")),
        "identical_replay": ("replay", ("READ_ROW",)), "metadata_replay": ("replay", ("READ_ROW",)),
        "foreign_principal": ("denied", ()),
    },
    "rollback": {"rejected": ("rolled_back", (*SYNTHETIC_STEPS[:-1], "FREE_INTENT_RLS_DENIED"))},
    "retry": {"retried": ("created", SYNTHETIC_STEPS)},
}
XID = re.compile(r"[1-9][0-9]{0,19}")
EPOCH = re.compile(r"[1-9][0-9]{0,11}\.[0-9]{6}")
STAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z")
CUSTOMER_TABLES = {
    "app.customer_profiles": 1, "app.customer_profile_lifecycle_event": 1,
    "platform.owner_mutation_evidence": 1, "platform.runtime_command_receipt": 1,
    "platform.runtime_outbox_message": 2,
}
GRANTS = "platform.database_action_grant"
IDENTITY = {"app.users": 2, "app.user_security_profiles": 2}
COUNTERS = {"users": "app.users", "security_profiles": "app.user_security_profiles", "grants": GRANTS,
            "customers": "app.customer_profiles", "receipts": "platform.runtime_command_receipt",
            "history": "app.customer_profile_lifecycle_event", "evidence": "platform.owner_mutation_evidence",
            "outbox": "platform.runtime_outbox_message", "work": "platform.runtime_work_item",
            "effects": "platform.runtime_effect_receipt"}
DELTAS = {"seeded": IDENTITY, "create-replay": {**CUSTOMER_TABLES, GRANTS: 4},
          "rollback": {GRANTS: 1}, "retry": {**CUSTOMER_TABLES, GRANTS: 1}}
EMPTY_GROUP = {"count": 0, "distinct_xids": 0, "xid": None, "rows_sha256": None,
               "coherent": False, "result_digest": None, "recorded_at": None}


def same(actual, expected, S, code):
    S.require(S.encode(actual) == S.encode(expected), code)


def recorded_at(value):
    if type(value) is not str or not STAMP.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def tuple_fields(value):
    return (type(value) is dict and set(value) == {"pid", "xid", "backend_start_epoch"}
            and type(value["pid"]) is int and 0 < value["pid"] <= 2**31 - 1
            and type(value["xid"]) is str and XID.fullmatch(value["xid"])
            and type(value["backend_start_epoch"]) is str and EPOCH.fullmatch(value["backend_start_epoch"]))


def node_receipt(reply, mode, S, secrets):
    S.require(mode in MODES and type(reply.returncode) is int and reply.returncode in (0, 1)
              and reply.stderr == b"" and type(reply.stdout) is bytes and 0 < len(reply.stdout) <= 8192
              and not any(secret.encode() in reply.stdout for secret in secrets), RESPONSE)
    value = S.unique_json(reply.stdout)
    S.require(type(value) is dict and value.get("schema") == NODE_SCHEMA, RESPONSE)
    if reply.returncode == 1:
        S.require(set(value) == {"schema", "status", "stage"} and value["status"] == "STOPPED"
                  and type(value["stage"]) is str and value["stage"] in NODE_STAGES[mode] | {
                      "ENTRY", "PINNED_IMPORT", "DRIVER", "POOL_CLOSE"}, RESPONSE)
        return value
    expected = CASE_EXPECTATIONS[mode]
    S.require(set(value) == {"schema", "status", "mode", "cases", "pools_ended"}
              and value["status"] == NODE_PASS and value["pools_ended"] is True and value["mode"] == mode
              and type(value["cases"]) is dict and set(value["cases"]) == set(expected), RESPONSE)
    cases = value["cases"]
    for name, (status, steps) in expected.items():
        case = cases[name]
        with_value = status in ("created", "replay")
        optional = {"value_sha256", "recorded_at"} if with_value else set()
        S.require(type(case) is dict and set(case) == {"status", "steps", "tuple"} | optional
                  and case["status"] == status and case["steps"] == list(steps)
                  and (case["tuple"] is None if status == "denied" else tuple_fields(case["tuple"]))
                  and (not with_value or (type(case["value_sha256"]) is str and S.HASH.fullmatch(case["value_sha256"])
                                         and recorded_at(case["recorded_at"]))), RESPONSE)
    if mode == "create-replay":
        rows = [case for case in cases.values() if case["tuple"] is not None]
        first = cases["created"]["tuple"]
        second = cases["contender"]["tuple"]
        S.require(first["pid"] != second["pid"] and len({row["tuple"]["xid"] for row in rows}) == 4
                  and len({(row["recorded_at"], row["value_sha256"]) for row in rows}) == 1, RESPONSE)
    return value


def use_bound_tuple(case):
    return {key: case["tuple"][key] for key in ("pid", "xid")}


def grant_groups(nodes):
    groups = {}
    if "create-replay" in nodes:
        groups["primary"] = sorted((use_bound_tuple(case) for case in nodes["create-replay"]["cases"].values()
                                    if case["tuple"] is not None), key=lambda case: case["xid"])
    if "rollback" in nodes:
        groups["rollback_without_intent"] = [use_bound_tuple(nodes["rollback"]["cases"]["rejected"])]
    if "retry" in nodes:
        groups["rollback"] = [use_bound_tuple(nodes["retry"]["cases"]["retried"])]
    return groups


def count(value):
    return type(value) is int and 0 <= value <= 8192


def check_full42_shape(snapshot, keys, S):
    S.require(type(snapshot) is dict and len(keys) == 42 and set(snapshot) == set(keys), FULL42)
    for entry in snapshot.values():
        S.require(type(entry) is dict and set(entry) == {"count", "rows_sha256"}
                  and count(entry["count"])
                  and type(entry["rows_sha256"]) is str and S.HASH.fullmatch(entry["rows_sha256"]), FULL42)


def validate_full42(snapshot, keys, phase, previous, S):
    check_full42_shape(snapshot, keys, S)
    if previous is None:
        empty = S.sha(b"[]")
        for entry in snapshot.values():
            same(entry, {"count": 0, "rows_sha256": empty}, S, FULL42)
        S.require(phase == "unborn", FULL42)
        return
    delta = DELTAS[phase]
    for name, current in snapshot.items():
        before = previous[name]
        if name in delta:
            S.require(current["count"] == before["count"] + delta[name]
                      and current["rows_sha256"] != before["rows_sha256"], FULL42)
        else:
            same(current, before, S, FULL42)


def check_observation_shape(observed, S):
    S.require(type(observed) is dict and set(observed) == {"scope_groups", "physical_counts", "grants_ok",
              "grant_groups", "restricted_sessions"} and type(observed["scope_groups"]) is dict
              and set(observed["scope_groups"]) == {"primary", "rollback"}
              and type(observed["grants_ok"]) is bool and count(observed["restricted_sessions"]), OBSERVATION)
    physical = observed["physical_counts"]
    S.require(type(physical) is dict and set(physical) == set(COUNTERS)
              and all(count(value) for value in physical.values()), OBSERVATION)
    for group in observed["scope_groups"].values():
        S.require(type(group) is dict and set(group) == set(EMPTY_GROUP) and count(group["count"])
                  and count(group["distinct_xids"]) and type(group["coherent"]) is bool
                  and (group["xid"] is None or type(group["xid"]) is str and XID.fullmatch(group["xid"]))
                  and (group["recorded_at"] is None or recorded_at(group["recorded_at"]))
                  and all(group[name] is None or type(group[name]) is str and S.HASH.fullmatch(group[name])
                          for name in ("rows_sha256", "result_digest")), OBSERVATION)
    grants = observed["grant_groups"]
    S.require(type(grants) is dict and set(grants) <= {"primary", "rollback", "rollback_without_intent", "unexpected"}, OBSERVATION)
    for group in grants.values():
        S.require(type(group) is list and len(group) <= 32, OBSERVATION)
        for row in group:
            S.require(type(row) is dict and set(row) == {"pid", "xid"} and type(row["pid"]) is int
                      and 0 < row["pid"] <= 2**31 - 1 and type(row["xid"]) is str and XID.fullmatch(row["xid"]), OBSERVATION)


def validate_observation(observed, full, nodes, previous, S):
    check_observation_shape(observed, S)
    S.require(observed["grants_ok"] is True, OBSERVATION)
    same(observed["restricted_sessions"], 0, S, OBSERVATION)
    same(observed["physical_counts"], {name: full[table]["count"] for name, table in COUNTERS.items()}, S, OBSERVATION)
    tracked = grant_groups(nodes)
    all_grants = [row for rows in tracked.values() for row in rows]
    S.require(len({row["xid"] for row in all_grants}) == full[GRANTS]["count"] == len(all_grants), OBSERVATION)
    same(observed["grant_groups"], tracked, S, OBSERVATION)
    present = {}
    if "create-replay" in nodes:
        present["primary"] = nodes["create-replay"]["cases"]["created"]
    if "retry" in nodes:
        present["rollback"] = nodes["retry"]["cases"]["retried"]
    for key, group in observed["scope_groups"].items():
        if key not in present:
            same(group, EMPTY_GROUP, S, OBSERVATION)
            continue
        case = present[key]
        S.require(type(group) is dict and set(group) == set(EMPTY_GROUP)
                  and all(type(group[name]) is str and S.HASH.fullmatch(group[name])
                          for name in ("rows_sha256", "result_digest")), OBSERVATION)
        expected = {"count": 6, "distinct_xids": 1, "xid": case["tuple"]["xid"], "coherent": True,
                    "recorded_at": case["recorded_at"]}
        same({key: group[key] for key in expected}, expected, S, OBSERVATION)
        if previous is not None and previous["scope_groups"][key]["coherent"] is True:
            same(group, previous["scope_groups"][key], S, OBSERVATION)
