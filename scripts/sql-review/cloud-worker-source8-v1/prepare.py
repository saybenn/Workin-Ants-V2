"""Bind the published Worker packet to the effective Source 8 frames offline."""

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
BASELINE = "532445ed1f861211978dd8b2e9ae12d4b5e6e180"
TWO_COMMIT = "464caba083c2c53dd158af027df2af933a0bdc18"
TWO_TREE = "61a1036e0e7cd059c9aa6a02e9f4214886fe49b4"
ACCEPTANCE_COMMIT = "df057ab329625fcab57df61fc5023f6b0ae02e78"
RECON = "context/reconciliation"
PACKET = "review-output/worker-recovery-control-rehearsal"
FIXTURE = f"{PACKET}/fixtures.json"
PROTOCOL = "scripts/worker_recovery_control_protocol.py"
ACL = "review-output/runtime-lease-branch-v1/worker-acl32.json"
INITIAL = "review-output/foundation-application.review.sql"
APPEND = ("review-output/runtime-lease-branch-v1/history-source-artifact/migrations/"
          "20261120000100_f0_runtime_lease_branch_v1/migration.sql")
EXPECTED = "review-output/native-runtime-lease-history-v1/expected.json"
VALIDATION = f"{RECON}/local-f0-worker-recovery-core-guard-observation-v3-source-validation.json"
OWNER_VALIDATION = f"{RECON}/local-f0-worker-recovery-owned-guard-observation-v2-source-validation.json"
WINDOWS_STOP = f"{RECON}/local-f0-worker-c820e39-6282f5ad-execution.json"
WINDOWS_ADAPTER = f"{RECON}/local-f0-worker-b42-evidence-adapter-confined-v2-source-validation.json"
PLAN = (f"{RECON}/local-f0-operation-sources/worker-recovery-core-clock-count-v2/reviews/"
        "remaining-worker-protected-transitions-finite-source-plan-v2-20261119.json")
COMMON = "scripts/sql-review/cloud-two-history-owned-v1/sources.py"
COMMON_SHA = "9651ed26b7d5a1b72bb6bd7c609ddb43a95fc1599b59745f78a30f5e4acff43a"
TWO_OWNER = "scripts/sql-review/cloud-two-history-owned-v2/operation.py"
TWO_CLOSURE = f"{RECON}/cloud-phase0-evidence/2026-11-27/two-2f71c365"
ACCEPTANCE = f"{TWO_CLOSURE}/acceptance.json"
AUDIT = f"{TWO_CLOSURE}/independent-closure.json"
GENERIC_PINS = {
    FIXTURE: "497275a81de4c06bef1033a461f8cc3ada6d6b42bc1899ae77a7a1f0ca7678f0",
    PLAN: "1a6b3bfe380aba7250fd8dfbf900ab260fab5668c0e4352c0624b850a6bd612b",
    VALIDATION: "147eecd1f37f1127ed360b391f4164b9bc5b5eb218a1011d83fc2cbc2da4197c",
    OWNER_VALIDATION: "45dd7d9b71c128addad8991e2e70b3fee215ecf7604d9455d956a77e64f1ef1f",
    WINDOWS_STOP: "a96842de6d0a214e0df1e67eda1ec6d8be0fa29f0f62f43a6f1ac17e6b90f771",
    WINDOWS_ADAPTER: "bc91da514b250591a30d2f973518b6c8af5b9c4d31833bfb3f3daf739681f13c",
    ACL: "6909f3cd9e2a795d1f39379b7f81db4c24f9526e235e802deea5ce1a2da8e5a3",
    INITIAL: "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad",
    APPEND: "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7",
    EXPECTED: "4f0fabc35968074f5d00e14c69771343d4e3efe118c92824c503ada0b9bdbc09",
}
TWO_PINS = {TWO_OWNER: "8680611ab98322a192a70c72f373b1fb4858ddbbd184c1dc4f450bb98823b0c0", COMMON: COMMON_SHA}
ACCEPTED_PINS = {
    ACCEPTANCE: "9ecf3628b388ef11c504def7422bf53c1d67926820a6662d60a44dbc0fe61d76",
    AUDIT: "2aa3d5178e406f42ae617c77ffe0e72f8b472e1c42b51fccbb261e3a781f0992",
}
CONTENT = "2998e875c76c676b9328b1c4a5edb0a0ff7cd8c5eb10b1cdff526abeacafea9c"
CATALOG = "cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4"
RUNTIME_FRAME = ("dee63b1c682a3cdef8a125df691fa2d4a2ee163b7afc43f740ce04f8f41ae965", 74)
OLD_FRAME = ("10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038", 72)
TRACK_FRAME = "1fec48baf827823dcb077f79c507120e91cbf8179d77fb550fbf8be635d9f865"
ROLES = ("postgres", "wa_context_issuer", "wa_identity_service_authority", "wa_app_runtime", "wa_worker")
SOURCE_LINES = {
    "nonnull-effect-relink-denied": 15,
    "null-pointer-foreign-same-fence-effect-denied": 15,
    "valid-current-Free-selection-survives-duplicate-attempt": 7,
    "terminal-work-trigger-denial-rolls-back-completion": 11,
}


def common(root):
    path = root / COMMON
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != COMMON_SHA:
        raise ValueError("WORKER_COMMON_SOURCE_DRIFT")
    module = ModuleType("_cloud_worker_source_review")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def anchored(source, root, commit, pins):
    checked = {name: source.pinned(root, name, wanted) for name, wanted in pins.items()}
    query = "".join(f"{commit}:{name}\n" for name in sorted(checked)).encode()
    raw = source.git(root, "cat-file", "--batch", payload=query)
    offset = 0
    for name in sorted(checked):
        body = checked[name]
        end = raw.index(b"\n", offset)
        source.require(raw[offset:end].split()[1:] == [b"blob", str(len(body)).encode()], "WORKER_GIT_BLOB")
        offset = end + 1
        source.require(raw[offset:offset + len(body) + 1] == body + b"\n", "WORKER_GIT_BYTES")
        offset += len(body) + 1
    source.require(offset == len(raw), "WORKER_GIT_BATCH")
    return checked


def frame(source, sql, function, replacement=False):
    declaration = ("CREATE OR REPLACE FUNCTION " if replacement else "CREATE FUNCTION ")
    declaration += f"platform_private.{function}()"
    matches = list(re.finditer(re.escape(declaration) + r".*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;", sql, re.S))
    source.require(len(matches) == 1, "WORKER_EXACT_FRAME_DECLARATION")
    return matches[0][2].split("\n")


def effective_protocol(source, protocol, initial, append, native):
    initial_text, append_text = initial.decode(), append.decode()
    old_runtime = frame(source, initial_text, "runtime_transition")
    runtime = frame(source, append_text, "runtime_transition", replacement=True)
    track = frame(source, initial_text, "track_binding")

    def identity(lines):
        return source.sha("\n".join(lines).encode()), len(lines)

    source.require(identity(old_runtime) == OLD_FRAME and identity(runtime) == RUNTIME_FRAME
                   and identity(track)[0] == TRACK_FRAME, "WORKER_EFFECTIVE_BODY_IDENTITY")
    source.require(set(protocol.DIAGNOSTICS) == set(SOURCE_LINES), "WORKER_EXACT_DIAGNOSTIC_CASES")
    functions = native["expected"]["functions"]
    frames = {}
    for name, (state, message, function) in protocol.DIAGNOSTICS.items():
        prior, effective = (old_runtime, runtime) if function == "runtime_transition" else (track, track)
        body_hash, line_count = identity(effective)
        location = [index for index, line in enumerate(effective, 1) if "RAISE EXCEPTION " + protocol.quote(message) in line]
        prior_location = [index for index, line in enumerate(prior, 1) if "RAISE EXCEPTION " + protocol.quote(message) in line]
        key = f"platform_private.{function}()"
        source.require(state == "P0001" and location == prior_location == [SOURCE_LINES[name]]
                       and functions[key]["body_sha256"] == body_hash, "WORKER_EXACT_EFFECTIVE_GUARD")
        frames[name] = {
            "sqlstate": state, "function": key, "body_sha256": body_hash, "body_lines": line_count,
            "raise_line": location[0], "source": APPEND if function == "runtime_transition" else INITIAL,
        }

    previous_diagnostic = protocol.diagnostic

    def diagnostic(name, stderr, application):
        result = previous_diagnostic(name, stderr, application)
        if result["matched"]:
            guard = frames[name]
            source.require(result["source_body_line"] == guard["raise_line"], "WORKER_EXACT_OBSERVED_LINE")
            result["source_body_sha256"] = guard["body_sha256"]
        return result

    protocol.diagnostic = diagnostic
    return frames


def owning_seam(source, operation, stages):
    owner = next(node for node in ast.parse(operation).body if isinstance(node, ast.ClassDef) and node.name == "Owner")
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == "run")
    main = next(node for node in ast.parse(stages).body if isinstance(node, ast.FunctionDef) and node.name == "main")
    body = next(node for node in main.body if isinstance(node, ast.Try))
    steps = [ast.unparse(node) for node in body.body]
    noop = steps.index("event('NOOP', 'PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER')")
    cleanup = any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "cleanup"
                  for part in body.finalbody for node in ast.walk(part))
    source.require(ast.unparse(method.body[0]) == "return self.program.main()"
                   and any(step.startswith("write_safe('two-history-results.json'") for step in steps[noop + 1:])
                   and any("qualify_noop(installed, first)" in step for step in steps[:noop])
                   and any("NOOP_NATIVE_CHANGED" in step for step in steps[:noop])
                   and any("NOOP_LEDGER_CHANGED" in step for step in steps[:noop])
                   and cleanup, "WORKER_FRESH_OWNER_INSERTION")
    return {
        "after": "same fresh owner's NOOP PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER",
        "before": "same fresh owner's success record and finally cleanup",
        "bound_identity": ["run_id", "source_commit", "source_tree", "packet_sha256", "container_id", "volume_birth"],
        "previous_target_reuse": "DENIED",
        "roles": list(ROLES),
        "maximum_live_sessions": 3,
        "maximum_live_worker_sessions": 2,
        "overlap_case": "real-higher-fence-reclaim-with-retained-effect",
        "unknown_transport_or_backend_closure": "HOLD_AND_CLEANUP",
    }


def build(root=ROOT):
    root = Path(root).resolve(strict=True)
    source = common(root)
    blobs = anchored(source, root, BASELINE, GENERIC_PINS)
    value = source.unique_json(blobs[FIXTURE])
    review = source.unique_json(blobs[VALIDATION])
    owner_review = source.unique_json(blobs[OWNER_VALIDATION])
    source.require(review["runtime"] == owner_review["runtime"] == value["status"] == "NOT_RUN"
                   and value["database_contacted"] is value["sql_executed"] is False
                   and value["database_posture"] == "D" and value["approved_plan_sha256"] == GENERIC_PINS[PLAN]
                   and owner_review["child_validation"] == {"path": VALIDATION, "sha256": GENERIC_PINS[VALIDATION]}
                   and all(review[key]["decision"] == "SOURCE_APPROVED"
                           and review[key]["source_files_sha256"] == review["source_files_sha256"]
                           for key in ("independent_source_review", "Root_source_review"))
                   and review["original_6282_exit_ACK_SQLSTATE_diagnostic_and_complete_cause"] == "UNOBSERVED",
                   "WORKER_HISTORICAL_SOURCE_LIMITS")
    leaves = value["prepared_files_sha256"]
    graph = {**value["source_files_sha256"], **{f"{PACKET}/{name}": pin for name, pin in leaves.items()},
             FIXTURE: GENERIC_PINS[FIXTURE]}
    worker_content = {key: value[key] for key in ("source_files_sha256", "prepared_files_sha256")}
    source.require(len(value["source_files_sha256"]) == 59 and len(leaves) == 40 and len(graph) == 100
                   and all(name.endswith(".sql") for name in leaves)
                   and graph == review["full100_source_and_artifact_files_sha256"]
                   and value["source_only_packet_sha256"] == CONTENT
                   and set(leaves) | {"fixtures.json"} == {p.name for p in (root / PACKET).iterdir()},
                   "WORKER_EXACT_PUBLISHED_PACKET")
    blobs.update(anchored(source, root, BASELINE, graph))
    protocol = source.module(root, PROTOCOL, blobs[PROTOCOL])
    cases = value["cases"]
    ceilings = value["assertion_ceilings"]
    caps = value["finite_caps"]
    source.require(protocol.digest(worker_content) == CONTENT and protocol.PLAN_SHA == GENERIC_PINS[PLAN]
                   and tuple(case["name"] for case in cases) == protocol.CASE_NAMES
                   and len(cases) == 21 and all(case["sql"] in leaves and case["status"] == "NOT_RUN" for case in cases)
                   and Counter(row["maximum_after_actual_evidence_and_review"] for row in ceilings)
                   == {"PASS": 13, "PARTIAL": 4} and all(row["status"] == "NOT_RUN" for row in ceilings)
                   and caps == {"case_count": 21, "jobs": 3, "business_groups": 2, "audit_attempts": 3,
                                "grant_instances_max": 80, "clock_wait_seconds_max": 150,
                                "simultaneous_worker_sessions_max": 2, "worker_loop": False},
                   "WORKER_EXACT_FINITE_CONTROL_AND_SCOPE")
    native = source.unique_json(blobs[EXPECTED])
    ordered = native["ordered_source"]
    source.require(value["worker_acl_rows"] == source.unique_json(blobs[ACL]) and len(value["worker_acl_rows"]) == 32
                   and ordered["worker_acl_rows"] == 32 and ordered["external_trigger_count"] == 100
                   and ordered["initial_sha256"] == GENERIC_PINS[INITIAL] and ordered["append_sha256"] == GENERIC_PINS[APPEND]
                   and native["expected_sha256"] == protocol.digest(native["expected"]) == CATALOG,
                   "WORKER_UNCHANGED_ACL_AND_EFFECTIVE_CATALOG")
    frames = effective_protocol(source, protocol, blobs[INITIAL], blobs[APPEND], native)
    next_blobs = anchored(source, root, TWO_COMMIT, {**TWO_PINS, source.STEPS: source.HISTORICAL_PINS[source.STEPS]})
    accepted_blobs = anchored(source, root, ACCEPTANCE_COMMIT, ACCEPTED_PINS)
    accepted, audit = (source.unique_json(accepted_blobs[path]) for path in (ACCEPTANCE, AUDIT))
    source.require(accepted["decision"] == "ACCEPT_EXACT_DISPOSABLE_MIGRATION_MACHINERY"
                   and audit["decision"] == "EXACT_MACHINERY_SUBSET_AND_CLEANUP_VERIFIED"
                   and accepted["source_tree"] == audit["source_tree"] == TWO_TREE
                   and accepted["source_commit"] == audit["source_commit"] == TWO_COMMIT
                   and accepted["operation_run_id"] == audit["run_id"]
                   and accepted["files_sha256"]["independent-closure.json"] == ACCEPTED_PINS[AUDIT]
                   and accepted["assertion_promotions"] == audit["assertion_promotions"] == 0
                   and all(audit["cleanup_verified"].values()) and audit["native_expected_sha256"] == CATALOG,
                   "WORKER_PRIOR_MACHINERY_ONLY_ACCEPTANCE")
    proof = {
        "schema": "workinants.cloud-worker-source8-held-proof.v1",
        "status": "HELD_PENDING_WORKER_OWNING_SOURCE_AND_LITERAL_REVIEW",
        "posture": "D", "runtime": "NOT_RUN", "assertion_promotions": 0,
        "published_worker_commit": BASELINE, "published_worker_files_sha256": graph,
        "fixture_sha256": GENERIC_PINS[FIXTURE], "fixture_content_sha256": CONTENT, "plan_sha256": GENERIC_PINS[PLAN],
        "ordered_cases": [case["name"] for case in cases], "sql_files_sha256": leaves,
        "finite_caps": caps, "published_assertion_ceilings": ceilings, "worker_acl32_sha256": GENERIC_PINS[ACL],
        "ordered_migration_source_sha256": [GENERIC_PINS[INITIAL], GENERIC_PINS[APPEND]],
        "effective_native_catalog_sha256": CATALOG, "effective_guard_frames": frames,
        "historical_6282_complete_cause": "UNOBSERVED", "private_source_overlay": "UNAVAILABLE",
        "prior_closed_machinery": {"source_commit": TWO_COMMIT, "source_tree": TWO_TREE,
                                   "run_id": audit["run_id"], "files_sha256": ACCEPTED_PINS},
        "owning_transport_seam": owning_seam(source, next_blobs[TWO_OWNER], next_blobs[source.STEPS]),
        "preparation_source_files_sha256": {**GENERIC_PINS, **TWO_PINS, **ACCEPTED_PINS,
                                            source.STEPS: source.HISTORICAL_PINS[source.STEPS]},
    }
    return proof, protocol


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        proof, _ = build()
    except (KeyError, IndexError, OSError, RuntimeError, StopIteration, TypeError, ValueError):
        print('{"status":"HELD_WORKER_SOURCE_PROOF_UNCONFIRMED"}', file=sys.stderr)
        return 1
    print(json.dumps(proof, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
