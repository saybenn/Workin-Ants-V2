"""Closed Customer receipts and independent state transitions."""

from datetime import datetime
import re

MODES = ("create-replay", "rollback", "retry")
PHASES = ("unborn", "seeded", *MODES)
NODE_SCHEMA = "workinants.p0d-customer-proof-result.v1"
NODE_PASS = "PASS_FINITE_CUSTOMER_MODE_ONLY"
STOP_SCHEMA = "workinants.p0d-customer-proof-stop-diagnostic.v1"
SQLSTATES = {"08000", "08003", "08006", "22003", "22007", "22012", "22023", "22P02",
             "23502", "23503", "23505", "23514", "25P02", "28P01", "40001", "40P01", "42501", "42601",
             "42703", "42804", "42883", "42P01", "42P18", "55P03", "57014", "57P01", "P0001", "P0002", "XX000"}
OWNER_CODES = {"target_mismatch", "context_denied", "transaction_closed", "rolled_back",
               "database_unavailable", "commit_unconfirmed"}
CASE_RESULTS = {"created", "replay", "denied", "conflict", "unavailable", "rolled_back"}
QUERY_KINDS = ("BACKEND", "BIND", "READ", "CLOCK", "RECEIPT", "CUSTOMER", "HISTORY", "EVIDENCE", "LIFECYCLE", "FREE_INTENT")
ATTEMPT_STEPS = {"CONTEXT_INPUT", "APP_BEGIN", "ISSUER_BEGIN", "APP_QUERY_SHAPE", "APP_COMMIT_BUILD", "APP_ROLLBACK_BUILD",
                 "ISSUER_COMMIT_BUILD", "ISSUER_ROLLBACK_BUILD", "ISSUER_SQL_GRANT", "ISSUER_SQL_BACKEND", "ISSUER_SQL_OTHER",
                 "CASE_RESULT_CHECK", "WAIT_PEER_FIRST_READ", "WAIT_PRIMARY_FIRST_READ", "WAIT_PRIMARY_RECEIPT_ACK",
                 "WAIT_PEER_RECEIPT_BUILD"} | {f"APP_{family}_{kind}" for family in ("SQL", "RESULT") for kind in QUERY_KINDS}
HARNESS_STEPS = {"HARNESS_ENTRY", "PINNED_IMPORT", "DRIVER", "POOL_CLOSE", "RACE_PREPARATION", "RACE_PAIR_SETTLED",
                 "RACE_CREATED_VALUE", "RACE_REPLAY_VALUE_AND_PEER_BUILD", "RACE_DISTINCT_BACKENDS", "EXACT_AND_METADATA_REPLAY",
                 "FOREIGN_REQUEST_PRINCIPAL", "FINAL_FREE_INTENT_RLS_ROLLBACK", "ORIGINAL_KEY_RETRY"}
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


def stop_stage(value, mode):
    return type(value) is str and value in NODE_STAGES[mode] | {"ENTRY", "PINNED_IMPORT", "DRIVER", "POOL_CLOSE"}


def diagnostic_origin(value, sides, S):
    S.require(type(value) is dict and set(value) == {"side", "step", "sqlstate"}
              and type(value["side"]) is str and value["side"] in sides
              and type(value["step"]) is str and value["step"] in (HARNESS_STEPS if value["side"] == "harness" else ATTEMPT_STEPS)
              and (value["sqlstate"] is None or type(value["sqlstate"]) is str and value["sqlstate"] in SQLSTATES), RESPONSE)


def check_stop_diagnostic(value, mode, S):
    S.require(set(value) == {"schema", "status", "stage", "first_failure", "attempts", "pools"}
              and value["status"] == "STOPPED" and stop_stage(value["stage"], mode)
              and type(value["pools"]) is str and value["pools"] in {"NOT_OPENED", "END_RESOLVED", "END_UNCONFIRMED"}, RESPONSE)
    attempts = value["attempts"]
    S.require(type(attempts) is dict and set(attempts) == {"primary", "peer"}
              and (mode == "create-replay" or attempts["peer"] is None)
              and (value["pools"] != "NOT_OPENED" or all(attempt is None for attempt in attempts.values())), RESPONSE)
    first = value["first_failure"]
    diagnostic_origin(first, {"harness", "primary", "peer"}, S)
    known_steps = set(SYNTHETIC_STEPS) | {"READ_ROW", "RECEIPT_CONFLICT_EMPTY", "FREE_INTENT_RLS_DENIED", "UNEXPECTED_DRIVER_QUERY_FAILURE"}
    for side, attempt in attempts.items():
        if attempt is None:
            S.require(first["side"] != side, RESPONSE)
            continue
        S.require(type(attempt) is dict and set(attempt) == {"phase", "last", "failure", "owner_failure", "outcome",
                  "completed_steps", "terminal_builds"} and type(attempt["phase"]) is str and attempt["phase"] in NODE_STAGES[mode]
                  and type(attempt["last"]) is str and attempt["last"] in ATTEMPT_STEPS
                  and (attempt["owner_failure"] is None or type(attempt["owner_failure"]) is str and attempt["owner_failure"] in OWNER_CODES)
                  and (attempt["outcome"] is None or type(attempt["outcome"]) is str and attempt["outcome"] in CASE_RESULTS), RESPONSE)
        for key, allowed, limit in (("completed_steps", known_steps, 12), ("terminal_builds", {"commit", "rollback"}, 4)):
            S.require(type(attempt[key]) is list and len(attempt[key]) <= limit
                      and all(type(item) is str and item in allowed for item in attempt[key]), RESPONSE)
        if attempt["failure"] is not None:
            diagnostic_origin(attempt["failure"], {side}, S)
        if first["side"] == side:
            same(first, attempt["failure"], S, RESPONSE)


def node_receipt(reply, mode, S, secrets):
    S.require(mode in MODES and type(reply.returncode) is int and reply.returncode in (0, 1)
              and reply.stderr == b"" and type(reply.stdout) is bytes and 0 < len(reply.stdout) <= 8192
              and not any(secret.encode() in reply.stdout for secret in secrets), RESPONSE)
    value = S.unique_json(reply.stdout)
    S.require(type(value) is dict, RESPONSE)
    if reply.returncode == 1:
        if value.get("schema") == STOP_SCHEMA:
            check_stop_diagnostic(value, mode, S)
        else:
            S.require(value.get("schema") == NODE_SCHEMA and set(value) == {"schema", "status", "stage"}
                      and value["status"] == "STOPPED" and stop_stage(value["stage"], mode), RESPONSE)
        return value
    S.require(value.get("schema") == NODE_SCHEMA, RESPONSE)
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
