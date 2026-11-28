"""Prepare the held source8 App proof. Reads Git and source bytes only."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = "532445ed1f861211978dd8b2e9ae12d4b5e6e180"
TWO_REVIEWED_COMMIT = "7c1cc1c0bd67a5d191f6b04e452d974c28747100"
RECON = "context/reconciliation"
PACKET = "review-output/app-write-two-guard-observation-v2"
VALIDATION = f"{RECON}/local-f0-app-write-two-unexpected-diagnostic-v3-source-validation.json"
OLD_OWNER = f"{RECON}/local-f0-app-write-two-unexpected-diagnostic-v3-owned-source-validation.json"
OLD_ATTEMPT = f"{RECON}/local-f0-app-write-two-fcab2e9-8f2aa922-execution.json"
DIAGNOSTIC_ATTEMPT = f"{RECON}/local-f0-app-write-two-0ff2a91-0a02569b-execution.json"
SOURCE_PROGRESS = f"{RECON}/local-f0-CSP-C-two-history-reviewed-source-progress-20261124.json"
PROTOCOL = "scripts/app_write_two_unexpected_diagnostic_v3_protocol.py"
COORDINATOR = "scripts/sql-review/run-app-write-two-unexpected-diagnostic-v3.py"
TWO = "scripts/sql-review/cloud-two-history-owned-v2/operation.py"
TWO_STEPS = (f"{RECON}/local-f0-operation-sources/runtime-lease-two-history-owned-v1/"
             "local_f0_runtime_lease_two_history_owned_v1_operation_steps.py.txt")
INITIAL = "review-output/foundation-application.review.sql"
APPEND = ("review-output/runtime-lease-branch-v1/history-source-artifact/migrations/"
          "20261120000100_f0_runtime_lease_branch_v1/migration.sql")
EXPECTED = "review-output/native-runtime-lease-history-v1/expected.json"
RUNTIME_TRANSITION = "platform_private.runtime_transition()"
OLD_FRAME = ("10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038", 72)
NEW_FRAME = ("dee63b1c682a3cdef8a125df691fa2d4a2ee163b7afc43f740ce04f8f41ae965", 74)
EXPECTED_CATALOG = "cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4"
FIXTURE_CONTENT = "43c3278d935cb437e35c91d2692f6543deb14d02c105578c18701f0bb6d1d4f6"
PINS = {
    VALIDATION: "20b1cd1f8af62b5d3e1143e14fc280b440f1f7297a336c4b2ce08c1e36714e32",
    OLD_OWNER: "e4df5fcd0f2dd036bf770536176fc9656b0dbbd8e841eb7be9183fb410e70e51",
    OLD_ATTEMPT: "928effb819f748af248db53dd824a465948f5a8e51dbcde0ac8136ac80930483",
    DIAGNOSTIC_ATTEMPT: "23d31951f6b28433df4420ff935a99c6dfc376c14bebda4f7b85e80efd8ce91b",
    SOURCE_PROGRESS: "67f5ff9ff62fad942b227e65257a8d6f4fcb73dda75bb21ea8e7a685dce6c36c",
    INITIAL: "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad",
    APPEND: "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7",
    EXPECTED: "4f0fabc35968074f5d00e14c69771343d4e3efe118c92824c503ada0b9bdbc09",
    TWO: "ac9da0ceb1fb94b30bfa3238e84709fcee9d71101ff3965228f73fa300760619",
    TWO_STEPS: "f7505b51fd207a0e8c07d9bc7cc2a3887c3719773096b0caad97770453fe0f44",
}
R1 = "genuine-sh004-effect-insert"
READS = ("customer-existing-complete-revision-read", "customer-existing-missing-revision-read")
R2 = "pending-work-next-attempt-update"
CLAIMS = (
    "P0C-TABLE-RuntimeEffectReceipt-ALLOW|positive.wa_app_runtime.insert",
    "P0C-TABLE-RuntimeWorkItem-ALLOW|positive.wa_app_runtime.update",
)


class Held(ValueError):
    """Fixed hold metadata only."""


def need(condition, code):
    if not condition:
        raise Held(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def digest(value):
    return sha(json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False,
                          allow_nan=False).encode())


def json_read(raw):
    def unique(items):
        value = dict(items)
        need(len(value) == len(items), "DUPLICATE_JSON")
        return value
    return json.loads(raw, object_pairs_hook=unique)


def source(root, relative, expected):
    need(type(relative) is str and all(part not in ("", ".", "..") for part in relative.split("/"))
         and not any(c in relative for c in ("\\", ":", "\r", "\n", "\0")), "SOURCE_RELATIVE_PATH")
    path = root / relative
    need(path.resolve(strict=True) == path, "SOURCE_PATH_ALIAS")

    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
                value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as handle:
        info = os.fstat(handle.fileno())
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= 16 * 1024 * 1024,
             "REGULAR_BOUNDED_SOURCE")
        raw = handle.read(info.st_size + 1)
        need(identity(info) == identity(os.fstat(handle.fileno())) == identity(path.lstat()),
             "SOURCE_IDENTITY_CHANGED")
    need(len(raw) == info.st_size and sha(raw) == expected, "SOURCE_FINGERPRINT_CHANGED")
    return raw


def git_blob(root, relative, commit=BASELINE):
    result = subprocess.run(["/usr/bin/git", "-C", str(root), "show", f"{commit}:{relative}"],
                            env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
                                 "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_NO_REPLACE_OBJECTS": "1",
                                 "GIT_NO_LAZY_FETCH": "1"},
                            capture_output=True, timeout=10, check=False)
    need(result.returncode == 0 and result.stderr == b"" and len(result.stdout) <= 16 * 1024 * 1024,
         "HISTORICAL_GIT_BYTES_UNAVAILABLE")
    return result.stdout


def assigned(module, key):
    matches = [node.value for node in module.body if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == key for target in node.targets)]
    need(len(matches) == 1, "CLOSED_SOURCE_DECLARATION")
    return ast.literal_eval(matches[0])


def function_body(sql, identity, *, replacement):
    create = "CREATE OR REPLACE FUNCTION " if replacement else "CREATE FUNCTION "
    declarations = list(re.finditer(re.escape(create + identity) + r".*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;", sql, re.S))
    need(len(declarations) == 1, "EXACT_SOURCE_FRAME_DECLARATION")
    body = declarations[0][2]
    return sha(body.encode()), len(body.split("\n"))


def effective_frames(protocol, initial, append, expected):
    table = assigned(ast.parse(protocol), "UNEXPECTED_SOURCE_FRAMES")
    need(len(table) == 4 and table[RUNTIME_TRANSITION] == OLD_FRAME, "EXACT_HISTORICAL_FRAME_MAP")
    unchanged = {name: function_body(initial, name, replacement=False) for name in table}
    need(table == unchanged, "EXACT_HISTORICAL_FRAME_HASHES")
    new = function_body(append, RUNTIME_TRANSITION, replacement=True)
    need(new == NEW_FRAME, "EFFECTIVE_REPLACEMENT_FRAME")
    projected = {**unchanged, RUNTIME_TRANSITION: new}
    catalog = expected["expected"]
    need(expected["expected_sha256"] == digest(catalog) == EXPECTED_CATALOG
         and len(catalog["tables"]) == 42 and len(catalog["triggers"]) == 100
         and expected["ordered_source"]["worker_acl_rows"] == 32
         and expected["ordered_source"]["initial_sha256"] == PINS[INITIAL]
         and expected["ordered_source"]["append_sha256"] == PINS[APPEND],
         "SOURCE8_EFFECTIVE_CATALOG_BINDING")
    for name, (body_sha, _) in projected.items():
        need(catalog["functions"][name]["body_sha256"] == body_sha, "EFFECTIVE_FRAME_CATALOG_BODY_DRIFT")
    return {
        name: {"body_sha256": body_sha, "lines": lines,
               "source": APPEND if name == RUNTIME_TRANSITION else INITIAL}
        for name, (body_sha, lines) in sorted(projected.items())
    }


def fixture_proof(fixture, leaves, protocol, coordinator):
    protocol_ast = ast.parse(protocol)
    names = assigned(protocol_ast, "CASE_NAMES")
    need(assigned(protocol_ast, "CLAIMS") == CLAIMS, "PUBLISHED_EXACT_TWO_CEILINGS")
    cases = fixture["cases"]
    grants = fixture["finite_caps"]
    need(tuple(x["name"] for x in cases) == names and len(cases) == 14 and all(
        x["status"] == "NOT_RUN" and x["sql"] in leaves for x in cases
    ) and len({case["sql"] for case in cases}) == 14, "EXACT_ORDERED_CASE_BODIES")
    need(tuple(x["case_id"] + "|" + x["assertion_id"] for x in fixture["claim_ceilings"]) == CLAIMS
         and [(case["name"], case["claim"]) for case in cases if case["claim"]] ==
         [(R1, CLAIMS[0]), (R2, CLAIMS[1])]
         and grants["business_claims"] == 2 and grants["case_count"] == 14
         and grants["genuine_customer_groups"] == 1
         and grants["grant_instances_max"] == 15 and grants["simultaneous_app_sessions_max"] == 1
         and grants["scheduled_work"] == 1 and grants["worker_loop"] is False
         and len(fixture["worker_acl_rows"]) == 32, "EXACT_TWO_CEILINGS_AND_FINITE_CAPS")
    methods = {}
    for node in ast.walk(ast.parse(coordinator)):
        if isinstance(node, ast.FunctionDef) and node.name in ("schedule", "run_case", "execute"):
            need(node.name not in methods, "EXACT_COORDINATOR_METHOD")
            methods[node.name] = node
    need(set(methods) == {"schedule", "run_case", "execute"}, "EXACT_COORDINATOR_METHODS")
    need(ast.unparse(methods["run_case"].body[0]) ==
         "if case['phase'] == 'update' and (not self.scheduled):\n    self.schedule()",
         "SCHEDULE_AT_FIRST_UPDATE_BOUNDARY")
    schedule = ast.unparse(methods["schedule"])
    need("self.source_committed and (not self.scheduled)" in schedule
         and "'sql': 'schedule.sql'" in schedule and "self.operation(case)" in schedule
         and "self.work_observer(False, backend['xid'])" in schedule, "ACTUAL_APP_SCHEDULE_REQUIRED")
    before = [case for case in cases if case["phase"] != "update"]
    after = [case for case in cases if case["phase"] == "update"]
    need(cases == [*before, *after] and tuple(case["name"] for case in before[-3:]) == (R1, *READS)
         and after[-1]["name"] == R2, "R1_THEN_PAIRED_READS_THEN_SCHEDULE_THEN_R2")
    need(all(case["kind"] == "read-support" and case["allowed_changed_tables"] == []
             and case["claim"] is None and case["expected_records"][1] == {"existing_customer": count}
             for case, count in zip(before[-2:], (1, 0), strict=True))
         and after[-1]["allowed_changed_tables"] == ["platform.runtime_work_item"]
         and after[-1]["expected_records"][1] == {"changed": 1, "server_not_before_future": True},
         "EXACT_PAIRED_READ_AND_NEXT_ATTEMPT_CRITERIA")
    return {
        "ordered_cases": list(names),
        "read_support_after_r1": list(READS),
        "real_schedule_after": before[-1]["name"],
        "real_schedule_before": after[0]["name"],
        "restricted_role": "wa_app_runtime",
        "file_sha256_by_case": {case["name"]: leaves[case["sql"]] for case in cases},
        "actual_schedule_sql_sha256": leaves["schedule.sql"],
        "claim_ceilings": list(CLAIMS),
    }


def insertion_seam(two, steps):
    owner = [node for node in ast.parse(two).body if isinstance(node, ast.ClassDef) and node.name == "Owner"]
    need(len(owner) == 1 and sum(isinstance(node, ast.FunctionDef) and node.name == "run"
                                and ast.unparse(node.body[0]) == "return self.program.main()"
                                for node in owner[0].body) == 1, "REVIEWED_CLOUD_OWNING_CONTROLLER")
    main = [node for node in ast.parse(steps).body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    need(len(main) == 1, "EXACT_HISTORICAL_MAIN")
    attempt = next(node for node in main[0].body if isinstance(node, ast.Try))
    nodes = [ast.unparse(node) for node in attempt.body]
    noop = [i for i, line in enumerate(nodes) if line.startswith("event('NOOP', 'PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER'")]
    evidence = [i for i, line in enumerate(nodes) if line.startswith("write_safe('two-history-results.json'")]
    need(len(noop) == len(evidence) == 1 and noop[0] < evidence[0]
         and any("qualify_noop(installed, first)" in line for line in nodes[:noop[0]])
         and any("NOOP_NATIVE_CHANGED" in line for line in nodes[:noop[0]])
         and any("NOOP_LEDGER_CHANGED" in line for line in nodes[:noop[0]])
         and any("cleanup()" in ast.unparse(node) for node in attempt.finalbody),
         "SOURCE8_NOOP_PROOF_BEFORE_OWNED_CLEANUP")
    return {
        "owner": "fresh App-owned source8 composition",
        "after": "NOOP PASS_FULL8_AND_COMPLETE_NATIVE_LEDGER before component final success",
        "before": "same fresh App owner finally cleanup",
        "proof_domain": "same current run, source commit/tree/packet, exact CID and volume birth",
        "prior_independent_machinery_acceptance_required": True,
        "prior_closed_target_reusable": False,
        "owning_controller_source_anchor": TWO_REVIEWED_COMMIT,
        "shared_mechanism_source_binding": {TWO: PINS[TWO], TWO_STEPS: PINS[TWO_STEPS]},
    }


def prepare(root=ROOT):
    files = {name: source(root, name, wanted) for name, wanted in PINS.items() if name != TWO}
    files[TWO] = git_blob(root, TWO, TWO_REVIEWED_COMMIT)
    need(sha(files[TWO]) == PINS[TWO], "HISTORICAL_CLOUD_OWNING_CONTROLLER_DRIFT")
    review = json_read(files[VALIDATION])
    old_owner = json_read(files[OLD_OWNER])
    old_attempt = json_read(files[OLD_ATTEMPT])
    diagnostic = json_read(files[DIAGNOSTIC_ATTEMPT])
    progress = json_read(files[SOURCE_PROGRESS])
    need(review["runtime"] == old_owner["runtime"] == "NOT_RUN"
         and old_owner["child_validation_sha256"] == PINS[VALIDATION]
         and review["actual8f2a_database_cause"] == old_owner["actual8f2a_database_cause"] == "UNOBSERVED"
         and old_attempt["actual_wrapper_status"] == diagnostic["actual_wrapper_status"] == "STOPPED_ATTEMPT_PRESERVED",
         "HISTORICAL_LIMITS_UNCHANGED")
    need("App effective-source/versioned composition plan is private, no runtimecode admitted."
         in progress["parallel_source_only"], "HISTORICAL_EFFECTIVE_COMPOSITION_DISPOSITION")
    reviewed = review["generated_artifacts_sha256"]
    inventory = {path.relative_to(root).as_posix() for path in (root / PACKET).iterdir()}
    need(len(reviewed) == 24 and set(reviewed) == inventory
         and len([name for name in reviewed if name.endswith(".sql")]) == 22, "EXACT_24_APP_PACKET")
    for name, wanted in {**reviewed, **review["root_sources_sha256"]}.items():
        files[name] = source(root, name, wanted)
        need(files[name] == git_blob(root, name), "PUBLISHED_APP_BYTE_DRIFT")
    fixture = json_read(files[f"{PACKET}/fixtures.json"])
    leaves = {name.removeprefix(PACKET + "/"): found for name, found in reviewed.items()
              if not name.endswith("/fixtures.json")}
    need(fixture["prepared_files_sha256"] == leaves and fixture["source_only_packet_sha256"] == FIXTURE_CONTENT
         and digest({name: fixture[name] for name in ("source_files_sha256", "prepared_files_sha256")})
         == FIXTURE_CONTENT, "EXACT_FIXTURE_PREPARED_FILES")
    sql = {name: pin for name, pin in leaves.items() if name.endswith(".sql")}
    need(fixture["schema"] == "workinants.app-write-two-fixtures.v1" and fixture["database_posture"] == "D"
         and fixture["status"] == "NOT_RUN" and fixture["sql_executed"] is False and fixture["database_contacted"] is False,
         "SOURCE_FIXTURE_RUNTIME_LIMITS")
    files_sha = {name: sha(raw) for name, raw in files.items()}
    return {
        "schema": "workinants.cloud-app-source8-held-proof.v1",
        "status": "HELD_PENDING_INDEPENDENT_EFFECTIVE_APP_REVIEW_AND_RUNTIME_ADMISSION",
        "posture": "D",
        "assertion_promotions": 0,
        "runtime": "NOT_RUN",
        "source_git_anchor": BASELINE,
        "source_files_sha256": dict(sorted(files_sha.items())),
        "all_24_published_packet_files_sha256": reviewed,
        "fixture_content_sha256": FIXTURE_CONTENT,
        "sql_files_sha256": sql,
        "fixture_proof": fixture_proof(fixture, sql, files[PROTOCOL], files[COORDINATOR]),
        "source8": [PINS[INITIAL], PINS[APPEND]],
        "effective_expected_catalog_sha256": EXPECTED_CATALOG,
        "effective_diagnostic_frames": effective_frames(files[PROTOCOL], files[INITIAL].decode(),
                                                        files[APPEND].decode(), json_read(files[EXPECTED])),
        "historical_runtime_transition_frame": {"body_sha256": OLD_FRAME[0], "lines": OLD_FRAME[1]},
        "prior_8f2a_cause": "UNOBSERVED",
        "historical_effective_composition": "PRIVATE_SOURCE_ONLY_NO_RUNTIME_ADMISSION",
        "insertion_seam": insertion_seam(files[TWO], files[TWO_STEPS]),
        "pending": [
            "fresh source8 App diagnostic/protocol and validation replacing only effective frame authority",
            "Cloud exact interactive app/issuer/observer transport with bounded closure and tuple proof",
            "fresh independently reviewed composed owner and literal operational approvals",
            "separate independently accepted TWO actual machinery result",
            "same-fresh-run source8 installation and complete pre/post catalog and ledger proof",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        sys.stdout.write(json_bytes(prepare()).decode())
        return 0
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, StopIteration) as error:
        code = str(error) if isinstance(error, Held) else "SOURCE_PROOF_UNCONFIRMED"
        sys.stdout.write(json_bytes({"status": "HELD", "code": code, "runtime": "NOT_RUN"}).decode())
        return 1


if __name__ == "__main__":
    sys.exit(main())
