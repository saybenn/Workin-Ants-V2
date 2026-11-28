"""Pure recipe observations for the two held Consent empty-context denials."""

import hashlib
import json
import re
import uuid


CASES = ("null-context", "empty-context")
FUNCTION = "platform_private.consent_guard()"
BODY_SHA256 = "61dc444ce22f462fbbfcfa706f0cfdce5a7e16a028592b51d1fec07fa219e7ae"
BODY_LINE = 17
SQLSTATE = "P0001"
MESSAGE = "exact consent binding required"
GRANT_EXCLUSION = "__EXCLUDED_GRANT_IDS__"
TRIGGERS = {"expected": 100, "actual": 100, "exact": True, "enabled": True}
PREFIX_OBSERVATION = {"one_exact_prefix": True}
PREREAD_OBSERVATION = {"exact_prerequisite_rows": 1, "all_other_binding_predicates_exact": True,
                       "global_registry_admits": False}
GLOBAL_CLIENTS = (
    "SELECT count(*) FROM pg_catalog.pg_stat_activity "
    "WHERE backend_type='client backend' AND pid<>pg_catalog.pg_backend_pid();\n"
)


class Held(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise Held(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "CONSENT_DUPLICATE_JSON_FIELD")
            result[key] = value
        return result

    def nonfinite(_):
        raise Held("CONSENT_NONFINITE_JSON")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def uuid4(value):
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", value) is None:
        return False
    identifier = uuid.UUID(hex=value)
    return str(identifier) == value and identifier.version == 4


def markers(case):
    require(case in CASES, "CONSENT_CASE_SCOPE")
    label = case.upper().replace("-", "_")
    return f"WA_CE_{label}_BEFORE", f"WA_CE_{label}_AFTER"


def diagnostic(stderr):
    header = r"(?:psql:(?:<stdin>|-):[1-9][0-9]{0,5}: )?ERROR:[ \t]+"
    source = rf"CONTEXT:[ \t]+PL/pgSQL function {re.escape(FUNCTION)} line {BODY_LINE} at RAISE"
    location = r"LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}"
    return (
        type(stderr) is str and len(stderr) <= 512
        and re.fullmatch(f"{header}{SQLSTATE}: [ ]*{MESSAGE}\n{source}\n{location}\n",
                         stderr.replace("\r\n", "\n")) is not None
    )


def denial_receipt(case, exit_code, rows, acknowledged, stderr):
    before, _ = markers(case)
    exact = (type(exit_code) is int and exit_code == 3 and acknowledged is False
             and rows == [before] and diagnostic(stderr))
    return {
        "terminal_client_exit_3": type(exit_code) is int and exit_code == 3,
        "before_marker_only": rows == [before],
        "no_success_acknowledgment": acknowledged is False,
        "exact_source_diagnostic": exact,
        "sqlstate": SQLSTATE if exact else None,
        "source_body_sha256": BODY_SHA256 if exact else None,
        "source_body_line": BODY_LINE if exact else None,
    }


def acknowledged_observation(rows, acknowledged, stderr, expected):
    if acknowledged is not True or stderr != "" or type(rows) is not list or len(rows) != 1:
        return False
    if type(rows[0]) is not str or len(rows[0]) > 512:
        return False
    try:
        actual = strict_json(rows[0])
    except (TypeError, ValueError):
        return False
    return canonical(actual) == canonical(expected)


def state_observer_sql(template, grant_ids):
    require(type(grant_ids) is tuple and len(grant_ids) in (0, 3, 6)
            and all(uuid4(item) for item in grant_ids) and len(set(grant_ids)) == len(grant_ids),
            "CONSENT_PRECISE_ISSUER_EXCLUSIONS")
    require(template.count(GRANT_EXCLUSION) == 1, "CONSENT_STATE_OBSERVATION_SOURCE")
    expr = "ARRAY[" + ",".join(f"'{grant_id}'::uuid" for grant_id in grant_ids) + "]::uuid[]"
    return template.replace(GRANT_EXCLUSION, expr)


def state_matches(before, after, tables):
    def valid(value):
        return type(value) is list and len(value) == 42 and all(
            type(row) is dict and set(row) == {"table", "count", "sha256"}
            and type(row["count"]) is int and row["count"] >= 0
            and type(row["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
            for row in value
        ) and [row["table"] for row in value] == tables

    return type(tables) is list and len(tables) == len(set(tables)) == 42 and valid(before) and valid(after) and before == after


def identity_only_delta(before, seeded, tables):
    if not (state_matches(before, before, tables) and state_matches(seeded, seeded, tables)):
        return False
    fixtures = {"app.users", "app.user_security_profiles"}
    return all(
        (new["count"] == old["count"] + 1 and new["sha256"] != old["sha256"]) if old["table"] in fixtures else new == old
        for old, new in zip(before, seeded, strict=True)
    )


def issuer_retention_matches(value, count):
    return type(count) is int and count in (3, 6) and canonical(value) == canonical({
        "exact_count": count, "all_immutable_fields_equal": True, "issuer_owned": True,
        "revoked_false": True, "unexpired": True,
    })
