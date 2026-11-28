"""Verify the committed independently accepted owner-transaction prerequisite."""

from pathlib import PurePosixPath
import re
from types import SimpleNamespace
import uuid

CODE = "P0D_CUSTOMER_PRIOR_OWNER_SMOKE_UNPROVEN"
BASE = "context/reconciliation/cloud-phase0-evidence/2026-11-27"
ACCEPTANCE = re.compile(re.escape(BASE) + r"/owner-([0-9a-f]{8})/acceptance\.json")
SCHEMA = "workinants.cloud-p0d-owner-transaction-acceptance.v1"
DECISION = "ACCEPT_EXACT_DISPOSABLE_OWNER_TRANSACTION_SMOKE"
AUDIT_SCHEMA = "workinants.cloud-p0d-owner-transaction-independent-closure.v1"
AUDIT_DECISION = "EXACT_DISPOSABLE_OWNER_TRANSACTION_SMOKE_AND_CLEANUP_VERIFIED"
FILE_NAMES = {
    "operation.json", "operation-exit.json", "created-container.json", "created-volume.json",
    "evidence/run-evidence.json", "evidence/noop-owner-transaction-node.json",
    "evidence/noop-owner-transaction-observation.json", "evidence/noop-owner-transaction-fixture.json",
    "evidence/noop-owner-transaction-ledger.json", "independent-closure.json",
}
CLEAN = "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
OUTER_PASS = "PASS_MACHINERY_SUBSET_ONLY"


def verify_independent(audit, bound, S):
    expected = {**bound, "schema": AUDIT_SCHEMA, "decision": AUDIT_DECISION, "cleanup_verified": True,
                "operator_exit_code": 0, "outer_status": OUTER_PASS}
    S.require(type(audit) is dict and S.encode({key: audit.get(key) for key in expected}) == S.encode(expected), CODE)


def verify(root, relative, digest, packet, blobs, smoke, renewal, S):
    named = ACCEPTANCE.fullmatch(relative) if type(relative) is str else None
    S.require(named is not None and type(digest) is str and S.HASH.fullmatch(digest), CODE)
    raw = S.pinned(root, relative, digest)
    accepted = S.unique_json(raw)
    S.require(type(accepted) is dict and accepted.get("schema") == SCHEMA and accepted.get("decision") == DECISION
              and accepted.get("posture") == "D" and accepted.get("integrated_runtime_qualified") is False
              and type(accepted.get("operator_exit_code")) is int and accepted["operator_exit_code"] == 0, CODE)
    run_id, commit, tree = [accepted[key] for key in ("run_id", "source_commit", "source_tree")]
    container_id, volume_time, reviewer = [accepted[key] for key in ("container_id", "volume_created_at", "reviewer")]
    S.require(type(run_id) is str and str(uuid.UUID(run_id)) == run_id and uuid.UUID(run_id).version == 4
              and run_id[:8] == named[1] and run_id != packet["run_id"]
              and all(type(item) is str and S.HEX40.fullmatch(item) for item in (commit, tree))
              and type(container_id) is str and S.HASH.fullmatch(container_id)
              and type(volume_time) is str and 1 <= len(volume_time) <= 64
              and type(reviewer) is str and re.fullmatch(r"/root/[a-z0-9_]{1,80}", reviewer)
              and accepted["owner_source_sha256"] == S.sha(blobs[smoke.OWNER_SOURCE]), CODE)
    files = accepted["file_sha256"]
    S.require(type(files) is dict and set(files) == FILE_NAMES, CODE)
    content, records = {}, {}
    for leaf, pin in files.items():
        path = str(PurePosixPath(relative).parent / leaf)
        content[path] = S.pinned(root, path, pin)
        records[leaf] = S.unique_json(content[path])
    earlier = records["operation.json"]
    container = records["created-container.json"]
    volume = records["created-volume.json"]
    exit_record = records["operation-exit.json"]
    report = records["evidence/run-evidence.json"]
    audit = records["independent-closure.json"]
    S.require(earlier["schema"] == smoke.PACKET_SCHEMA and earlier["run_id"] == container["run_id"] == volume["run_id"] == run_id
              and earlier["source"] == {"commit": commit, "tree": tree} and container["id"] == container_id
              and volume["created_at"] == volume_time and earlier["target"]["container_name"] == container["name"]
              and earlier["target"]["volume_name"] == volume["name"]
              and all(earlier["target"][key] != packet["target"][key] for key in ("container_name", "volume_name"))
              and all(earlier[key] == packet[key] for key in ("daemon", "image"))
              and earlier["tools"]["sha256"] == packet["tools"]["sha256"]
              and earlier["owner_transaction"]["source_files"]["owner-transaction.ts"] == accepted["owner_source_sha256"], CODE)
    outer_sha, packet_sha = files["evidence/run-evidence.json"], files["operation.json"]
    node_sha = files["evidence/noop-owner-transaction-node.json"]
    S.require(type(exit_record.get("exit_code")) is int and exit_record["exit_code"] == 0
              and exit_record["method"] == "ACTUAL_OPERATING_PROCESS_EXIT"
              and exit_record["run_id"] == run_id and exit_record["source_commit"] == commit
              and exit_record["outer_evidence_sha256"] == outer_sha and exit_record["packet_sha256"] == packet_sha
              and exit_record["node_result_sha256"] == node_sha and exit_record["node_status"] == smoke.NODE_PASS
              and exit_record["evidence_complete"] is True and exit_record["stdout_status"] == OUTER_PASS, CODE)
    S.require(report["status"] == OUTER_PASS and report["run_id"] == run_id and report["approved_commit"] == commit
              and report["approved_tree"] == tree and report["approved_packet_sha256"] == packet_sha
              and report["container_id"] == container_id and report["volume_created_at"] == volume_time
              and report["cleanup"] == CLEAN and report["cleanup_full_container_identity_absent"] is True
              and report["transport"]["unknown_closure"] is False and report["unexpected"] == []
              and report["immutable_source_postcheck"] == "PASS" and renewal.native_gate(report["native_results"])
              and report["migration_results"][-1]["no_pending_message_observed"] is True
              and report["owner_transaction"]["status"] == smoke.PASS
              and report["owner_transaction"]["integrated_runtime_qualified"] is False, CODE)
    verify_independent(audit, {"run_id": run_id, "reviewer": reviewer, "source_commit": commit, "source_tree": tree,
                              "container_id": container_id, "volume_created_at": volume_time,
                              "daemon": earlier["daemon"], "image": earlier["image"], "packet_sha256": packet_sha,
                              "outer_evidence_sha256": outer_sha,
                              "operator_exit_receipt_sha256": files["operation-exit.json"]}, S)
    base = str(PurePosixPath(relative).parent)
    leaf = "noop-owner-transaction-node.json"
    value = smoke.node_receipt(SimpleNamespace(returncode=0, stderr=b"", stdout=content[f"{base}/evidence/{leaf}"]), S, ())
    smoke.validate_observation(records["evidence/noop-owner-transaction-observation.json"], value, S)
    fixture = S.unique_json(blobs[smoke.FIXTURE_INPUTS])
    expected_fixture = {name: fixture[f"{name}_expected"]
                        for name in ("identity_coherence_observer", "customer_observer", "effect_observer")}
    S.require(S.encode(records["evidence/noop-owner-transaction-fixture.json"]) == S.encode(expected_fixture), CODE)
    for key, suffix in (("node", "node"), ("observation", "observation"), ("fixture", "fixture"), ("post_ledger", "ledger")):
        path = f"evidence/noop-owner-transaction-{suffix}.json"
        reference = report["owner_transaction"][key]
        S.require(reference == {"path": PurePosixPath(path).name, "sha256": files[path],
                                "bytes": len(content[f"{base}/{path}"])}, CODE)
    for name, data in {relative: raw, **content}.items():
        S.require(name not in blobs or blobs[name] == data, CODE)
        blobs[name] = data
    return {"path": relative, "sha256": digest, "run_id": run_id, "source_commit": commit, "source_tree": tree,
            "container_id": container_id, "cleanup_sha256": files["independent-closure.json"], "reviewer": reviewer}
