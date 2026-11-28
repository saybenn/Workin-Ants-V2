"""Validate finite Node receipts before the owning host runs separate observers."""
import json
import re

SCHEMA = "workinants.p0d-known-work-node.v1"
PHASES = ("INIT","SOURCE","SCHEDULE","REPLAY","CLAIM","LIVE_RECLAIM","RENEW","COPIED_HASH_RENEW","RECLAIM","STALE_RENEW","FINISH")
OUTCOMES = {"SOURCE":"created","SCHEDULE":"scheduled","REPLAY":"already_scheduled","CLAIM":"claimed",
            "LIVE_RECLAIM":"unavailable","RENEW":"renewed","COPIED_HASH_RENEW":"unavailable","RECLAIM":"claimed","STALE_RENEW":"unavailable"}
CLOCK_OFFSETS = {"CLAIM":18000,"LIVE_RECLAIM":18000,"RENEW":26000,
                 "COPIED_HASH_RENEW":42000,"RECLAIM":18000,"STALE_RENEW":42000}
FENCES = {"CLAIM":1,"RENEW":1,"RECLAIM":2}
CODES = {
    "DRIVER_IDENTITY","INPUT_FORMAT","CREDENTIAL_FORMAT","PHASE_ORDER","CLOCK_SAMPLE_OUT_OF_RANGE","FIXTURE_UNCONFIRMED",
    "LEASE_RESULT_UNCONFIRMED","LEASE_TRANSITION_UNCONFIRMED","SOURCE_RESULT_UNCONFIRMED","SCHEDULE_RESULT_UNCONFIRMED",
    "POOL_CLOSE_UNCONFIRMED","OUTCOME_UNCONFIRMED","SESSION_DEADLINE","OWNER_TARGET_MISMATCH","OWNER_CONTEXT_DENIED",
    "OWNER_TRANSACTION_CLOSED","OWNER_ROLLED_BACK","OWNER_DATABASE_UNAVAILABLE","OWNER_COMMIT_UNCONFIRMED","UNEXPECTED_FAILURE",
}
ENTRY_CODES = {"DRIVER_IDENTITY", "FIXTURE_UNCONFIRMED", "UNEXPECTED_FAILURE"}
INIT_CODES = {"CREDENTIAL_FORMAT", "INPUT_FORMAT", "SESSION_DEADLINE", "UNEXPECTED_FAILURE"}
UNCERTAIN = {"OWNER_DATABASE_UNAVAILABLE","OWNER_COMMIT_UNCONFIRMED","UNEXPECTED_FAILURE"}
HASH = re.compile(r"[0-9a-f]{64}")
XID = re.compile(r"[1-9][0-9]{0,19}")


class Held(ValueError):
    pass


def need(ok):
    if not ok:
        raise Held("P0D_WORK_RESULT_UNCONFIRMED")


def parse(raw):
    def record(items):
        value = dict(items)
        need(len(value) == len(items))
        return value

    def invalid(_):
        raise Held("P0D_WORK_RESULT_UNCONFIRMED")

    need(type(raw) is bytes and 0 < len(raw) <= 2048 and b"\x00" not in raw and raw.isascii())
    try:
        return json.loads(raw, object_pairs_hook=record, parse_constant=invalid)
    except (TypeError, ValueError):
        raise Held("P0D_WORK_RESULT_UNCONFIRMED") from None


def phase_message(step, server_ms=None):
    need(step in PHASES)
    args = {"phase":step}
    if step in CLOCK_OFFSETS:
        need(type(server_ms) is int and 10**12 <= server_ms < 10**13)
        args["server_ms"] = server_ms
    else:
        need(server_ms is None)
    need(step != "INIT")
    return (json.dumps(args,separators=(",",":"))+"\n").encode()


def receipt(raw, expected, *, acknowledged, process_exit, server_ms=None):
    """The bridge supplies verified ack/EOF and actual process poll, never fabricated markers."""
    need(expected in PHASES and type(acknowledged) is bool)
    body = parse(raw)
    base = {"schema","phase","sequence","status","pools_closed"}
    need(type(body) is dict and base <= body.keys() and body["schema"] == SCHEMA
         and type(body["sequence"]) is int and type(body["pools_closed"]) is bool)
    if body["status"] == "STOPPED":
        need(set(body) == base | {"code","outcome_unconfirmed"} and not acknowledged
             and type(process_exit) is int and process_exit == 1 and type(body["code"]) is str and body["code"] in CODES
             and type(body["outcome_unconfirmed"]) is bool)
        if body["phase"] == "ENTRY":
            need(expected == "INIT" and body["sequence"] == 0 and body["code"] in ENTRY_CODES
                 and body["pools_closed"] and not body["outcome_unconfirmed"])
        else:
            # An absolute session timeout can close after an already-sent phase ACK.
            need(body["phase"] == expected and body["sequence"] == PHASES.index(expected))
            if expected == "INIT":
                need(body["code"] in INIT_CODES and body["pools_closed"])
            need(body["outcome_unconfirmed"] is (not body["pools_closed"] or body["code"] in UNCERTAIN))
        return body
    need(body["phase"] == expected and body["sequence"] == PHASES.index(expected) and body["pools_closed"] is True)
    if expected == "INIT":
        need(set(body) == base and body["status"] == "READY" and acknowledged and process_exit is None)
    elif expected == "FINISH":
        need(set(body) == base | {"assertion_promotions"} and body["status"] == "PASS" and not acknowledged
             and type(process_exit) is int and process_exit == 0
             and type(body["assertion_promotions"]) is int and body["assertion_promotions"] == 0)
    else:
        need(set(body) == base | {"outcome","lease"} and body["status"] == "PHASE_PASS" and acknowledged
             and process_exit is None and body["outcome"] == OUTCOMES[expected])
        lease = body["lease"]
        if expected in FENCES:
            need(type(server_ms) is int and type(lease) is dict and set(lease) == {"fence","deadline_ms","lease_digest_sha256"}
                 and type(lease["fence"]) is int and lease["fence"] == FENCES[expected] and type(lease["deadline_ms"]) is int
                 and lease["deadline_ms"] == server_ms + CLOCK_OFFSETS[expected]
                 and type(lease["lease_digest_sha256"]) is str and HASH.fullmatch(lease["lease_digest_sha256"]))
        else:
            need(lease is None)
    return body


def check_work_row(work):
    """Validate the independent WorkItem projection before comparing values."""
    need(type(work) is dict and set(work) == {"count","identity_exact","state","fence","attempt","deadline_ms",
         "lease_digest_sha256","mutation_xid","row_sha256","without_deadline_xid_sha256","identity_sha256"})
    need(type(work["count"]) is int and work["count"] == 1 and work["identity_exact"] is True
         and type(work["mutation_xid"]) is str and XID.fullmatch(work["mutation_xid"])
         and all(type(work[name]) is str and HASH.fullmatch(work[name])
                 for name in ("row_sha256","without_deadline_xid_sha256","identity_sha256"))
         and type(work["fence"]) is int and type(work["attempt"]) is int)
    need(type(work["state"]) is str and work["state"] in ("pending", "leased"))
    if work["state"] == "pending":
        need(work["fence"] == work["attempt"] == 0
             and work["deadline_ms"] is None and work["lease_digest_sha256"] is None)
    else:
        need(work["fence"] == work["attempt"] and work["fence"] in (1, 2)
             and type(work["deadline_ms"]) is int and 10**12 <= work["deadline_ms"] < 10**13
             and type(work["lease_digest_sha256"]) is str and HASH.fullmatch(work["lease_digest_sha256"]))


def work_observation(phase, work, previous, grant_xid, node_lease, pre_server_ms, post_server_ms):
    """Compare the separately observed exact one-row WorkItem projection to the prior committed phase."""
    need(phase in OUTCOMES and type(grant_xid) is str and XID.fullmatch(grant_xid))
    if phase == "SOURCE":
        need(work is None and previous is None and node_lease is None)
        return
    check_work_row(work)
    if phase == "SCHEDULE":
        need(previous is None and work["state"] == "pending" and work["mutation_xid"] == grant_xid)
        return
    check_work_row(previous)
    need(work["identity_sha256"] == previous["identity_sha256"])
    if phase in FENCES:
        need(type(node_lease) is dict and set(node_lease) == {"fence", "deadline_ms", "lease_digest_sha256"}
             and work["state"] == "leased" and work["fence"] == FENCES[phase]
             and work["mutation_xid"] == grant_xid and grant_xid != previous["mutation_xid"]
             and all(type(node_lease[name]) is type(work[name]) and node_lease[name] == work[name]
                     for name in ("fence", "deadline_ms", "lease_digest_sha256"))
             and type(post_server_ms) is int and work["deadline_ms"] > post_server_ms and work["row_sha256"] != previous["row_sha256"])
        if phase == "RENEW":
            need(work["deadline_ms"] > previous["deadline_ms"] and type(pre_server_ms) is int and previous["deadline_ms"] > pre_server_ms
                 and work["without_deadline_xid_sha256"] == previous["without_deadline_xid_sha256"])
        elif phase == "RECLAIM":
            need(type(pre_server_ms) is int and previous["deadline_ms"] <= pre_server_ms and previous["lease_digest_sha256"] != work["lease_digest_sha256"])
        return
    need(work == previous and node_lease is None and grant_xid != previous["mutation_xid"])
    if phase in {"LIVE_RECLAIM","COPIED_HASH_RENEW","STALE_RENEW"}:
        need(type(post_server_ms) is int and work["deadline_ms"] > post_server_ms)


def grant_observation(phase, observation, previous, worker_fixture):
    """Require one append-only grant for this exact phase and bind its runtime XID."""
    from hashlib import sha256
    from uuid import UUID

    need(phase in OUTCOMES)
    index = PHASES.index(phase)
    need(type(observation) is dict and set(observation)=={"count","distinct_hashes","grants"}
         and type(observation["count"]) is int and type(observation["distinct_hashes"]) is int
         and observation["count"] == observation["distinct_hashes"] == index and type(observation["grants"]) is list
         and len(observation["grants"]) == index)
    need(type(previous) is list and len(previous) == index-1)
    index_by_id = {}
    keys = {"id","issuer_service","role","owner","action","purpose","target_kind","target_id","security_generation",
            "source_generation","policy","pid","runtime_xid","issuer_xid","fields_sha256","identity_exact","metadata_exact","row_sha256"}
    for row in observation["grants"]:
        need(type(row) is dict and set(row) == keys and type(row["id"]) is str)
        try:
            identity = UUID(row["id"])
        except ValueError:
            raise Held("P0D_WORK_RESULT_UNCONFIRMED") from None
        need(identity.version == 4 and str(identity) == row["id"] and row["id"] not in index_by_id
             and type(row["pid"]) is int and 0 < row["pid"] < 2**31
             and all(type(row[name]) is str and XID.fullmatch(row[name]) for name in ("runtime_xid","issuer_xid"))
             and all(type(row[name]) is str and HASH.fullmatch(row[name]) for name in ("fields_sha256","row_sha256"))
             and row["identity_exact"] is row["metadata_exact"] is True)
        index_by_id[row["id"]] = row
    need(all(index_by_id.get(row["id"]) == row for row in previous))
    runtime_xids = {row["runtime_xid"] for row in index_by_id.values()}
    issuer_xids = {row["issuer_xid"] for row in index_by_id.values()}
    need(len(runtime_xids)==len(issuer_xids)==index and not runtime_xids & issuer_xids)
    new = [row for key,row in index_by_id.items() if key not in {old["id"] for old in previous}]
    need(len(new) == 1)
    row = new[0]
    need(type(row["security_generation"]) is int and row["security_generation"] == 0
         and type(row["source_generation"]) is int and row["issuer_service"] == "wa_context_issuer"
         and row["policy"] == "wa-p0d-known-work.v1")
    if phase == "SOURCE":
        expected = ("wa_app_runtime","customer_buyer_profile","SH-004.v1","provision","CustomerProfile",
                    "cdfa190f-3235-5c98-b217-bf27a5d03d66",0,"684bc408a16638003b12e3a6b19e5dc17e0da1d7f728d12af237c0e396e6f3ec")
    elif phase in ("SCHEDULE","REPLAY"):
        expected = ("wa_app_runtime","platform_integration_owner","runtime.schedule_work.v1","work.schedule","RuntimeWorkItem",
                    "530db9d1-b945-53ec-bb0c-6d91c914b5fc",0,"6fcd1458f8cdf7f054e097f8cd3a39c81dded57b9c687268a52986ab9e7d5dbc")
    else:
        names = {"CLAIM":"claim-0","LIVE_RECLAIM":"claim-1","RENEW":"renew-1","COPIED_HASH_RENEW":"renew-1",
                 "RECLAIM":"claim-1","STALE_RENEW":"renew-1"}
        template = worker_fixture["grants"][names[phase]]
        expected = (template["login"],template["owner"],template["action"],template["purpose"],template["targetKind"],
                    template["targetId"],int(template["sourceGeneration"]),sha256("\n".join(template["allowedFields"]).encode()).hexdigest())
    actual = tuple(row[key] for key in ("role","owner","action","purpose","target_kind","target_id","source_generation","fields_sha256"))
    need(actual == expected)
    return row["runtime_xid"]
