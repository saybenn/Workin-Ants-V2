"""Reproduce or run the separately reviewed Cloud CSP owning packet."""

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
from types import ModuleType

import prepare
import source7


REVIEW = "workinants.cloud-customer-stale-predecessor-owned-review.v2"
DECISION = "APPROVED_EXACT_CLOUD_CSP_PACKET"


def read_review(raw, plan, plan_bytes):
    value = prepare.parse(raw)
    expected = {"schema", "decision", "plan_sha256", "source_commit", "packet_sha256",
                "run_id", "reviewer", "scopes", "findings"}
    prepare.require(type(value) is dict and set(value) == expected, "CSP_REVIEW_FIELDS")
    prepare.require(value["schema"] == REVIEW and value["decision"] == DECISION
                    and value["plan_sha256"] == prepare.sha(plan_bytes)
                    and value["source_commit"] == plan["source_commit"]
                    and value["packet_sha256"] == plan["packet_sha256"] and value["run_id"] == plan["run_id"],
                    "CSP_REVIEW_EXACT_PLAN_BINDING")
    reviewer = value["reviewer"]
    prepare.require(type(reviewer) is str and 4 <= len(reviewer) <= 128 and reviewer == reviewer.strip()
                    and reviewer.casefold() != plan["author"].casefold()
                    and all(32 <= ord(char) < 127 for char in reviewer), "CSP_INDEPENDENT_REVIEWER_REQUIRED")
    prepare.require(value["scopes"] == dict.fromkeys(prepare.REVIEW_SCOPES, "APPROVED")
                    and value["findings"] == [], "CSP_REVIEW_SCOPE_OR_FINDINGS")
    return value


def verify_plan(root, path):
    raw = prepare.stable_file(path)
    plan = prepare.parse(raw)
    prepare.require(prepare.encode(plan) == raw, "CSP_CANONICAL_OPERATION_PLAN")
    archive = Path(plan["migration_tool_archive"])
    folder, expected, files = prepare.build(
        root, plan["run_id"], plan["fixture_run_id"], plan["daemon"], archive,
    )
    prepare.require(path == folder / "operation-plan.json" and expected == plan, "CSP_EXACT_REBUILT_PLAN")
    for name, data in files.items():
        prepare.require(prepare.stable_file(folder / name) == data, "CSP_EXACT_PREPARED_ASSET")
    blobs = prepare.closed_files(root)
    prepare.require({name: prepare.sha(data) for name, data in blobs.items()} == plan["packet_files_sha256"],
                    "CSP_CLOSED_CURRENT_SOURCE_MAP")
    return plan, raw, files, blobs


def controller(blobs):
    """Load the exact inherited algorithms with the Cloud literal deltas."""
    mod = ModuleType("_workinants_cloud_csp_inherited")
    mod.__file__ = __file__
    for index, name in enumerate(prepare.OPERATORS):
        location = f"{prepare.OWNED}/{name}.txt"
        raw = blobs[location]
        prepare.require(prepare.sha(raw) == prepare.OPERATOR_PINS[index], "CSP_HISTORICAL_OPERATOR_DRIFT")
        text = raw.decode()
        if index == 1:
            directories = "'mkdir','-p','/run/wa-f0-tools','/run/wa-f0-source'"
            create = "umask 022; exec /usr/bin/mkdir -p -- /run/wa-f0-tools /run/wa-f0-source"
            text = source7.replace(text, directories, "'/bin/sh','-ceu'," + repr(create))
            for basename in ("tools", "source"):
                directory = f"/run/wa-f0-{basename}"
                archive = f"{directory}.tar.gz"
                extract = f"'tar','-xzf','{archive}','-C','{directory}'"
                preserve = f"umask 022; exec /usr/bin/tar --same-permissions -xzf {archive} -C {directory}"
                text = source7.replace(text, extract, "'/bin/sh','-ceu'," + repr(preserve))
            text = source7.replace(text, "env = os.environ.copy()\n        env['PGPASSWORD'] = secrets.token_hex(32)",
                                   "env = {'PGPASSWORD': secrets.token_hex(32)}")
            text = source7.replace(text, "need(MANIFEST['review_status']=='APPROVED_LOCAL_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V1_ATTEMPT','CSP1_EXACT_OPERATION_NOT_REVIEWED')",
                                   "need(MANIFEST['review_status']=='APPROVED_CLOUD_CSP_OWNED_V2','CSP_CLOUD_EXACT_OPERATION_NOT_REVIEWED')")
            text = source7.replace(text, "unique_json(read_pinned(CSP_CHILD_VALIDATION))['packet_files_sha256']",
                                   "CSP_STATE['child_artifact_hashes']")
            old_url = "/run/wa-secrets/wa-local-f0-migrator-url"
            prepare.require(text.count(old_url) == 3, "CSP_SECRET_RECIPE_ANCHORS")
            text = text.replace(old_url, "/run/wa-secrets/wa-cloud-csp-initial-v2-migrator-url")
            text = source7.replace(text, "name='wa-p0c-'+RUN_ID[:8]+'-customer-stale'",
                                   "name=RESOURCE_CONTAINERS[0]")
            text = source7.replace(text, "OUT.mkdir(exist_ok=False)", "OUT.mkdir(mode=0o700,exist_ok=False)")
            text = source7.replace(text,
                                   "MANIFEST['packet_files_sha256']['scripts/sql-review/run-local-f0-migrate.py'],'runner_sha256':MANIFEST['packet_files_sha256']['scripts/sql-review/local-f0-migrate-runner.mjs']",
                                   f"MANIFEST['packet_files_sha256']['{prepare.BASE}/cloud_host.py'],"
                                   f"'runner_sha256':MANIFEST['migration_targets']['ok']['source_files_sha256']['{source7.RUNNER}']")
        exec(compile(text, location, "exec"), mod.__dict__)
    return mod


def interrupted(_signal, _frame):
    raise KeyboardInterrupt


def execute(path, review_path, plan, raw, assets, blobs):
    import cloud_host

    folder = path.parent
    relative = f"{prepare.PROFILE}/guard.py"
    guard = ModuleType("_cloud_csp_proven_platform_guard")
    guard.__file__ = str(prepare.ROOT / relative)
    exec(compile(blobs[relative], relative, "exec"), guard.__dict__)
    guard.private_directory(folder)
    guard.private_file(path)
    guard.private_file(review_path)
    prepare.require(review_path.parent == folder and review_path.name == "independent-review.json",
                    "CSP_REVIEW_BOUND_LOCATION")
    guard.private_file(Path(plan["migration_tool_archive"]))
    review_raw = prepare.stable_file(review_path)
    review = read_review(review_raw, plan, raw)
    review_hash = prepare.sha(review_raw)
    profile = prepare.parse(blobs[f"{prepare.PROFILE}/profile.json"])
    prepare.require(profile["schema"] == "workinants.cloud-f0-profile.v2"
                    and profile["bootstrap_transport"] == "exact_container_stdin_to_private_tmpfs"
                    and profile["bootstrap_file"] == plan["target"]["bootstrap_container_path"],
                    "CSP_REVIEWED_PROFILE_REQUIRED")
    prepare.require(not os.path.lexists(plan["evidence_directory"]), "CSP_EXCLUSIVE_ATTEMPT_REQUIRED")
    prepare.write_new(folder / "attempt.json", prepare.encode({
        "run_id": plan["run_id"], "plan_sha256": prepare.sha(raw), "review_sha256": review_hash,
        "reviewer": review["reviewer"], "state_at_creation": "BEFORE_ANY_RESOURCE_CREATION",
    }))
    config = folder / "docker-client"
    config.mkdir(mode=0o700)
    prepare.write_new(config / "config.json", b"{}\n")
    guard.private_file(config / "config.json")
    docker = guard.Docker(profile, config)
    prepare.require(docker.observe() == plan["daemon"], "CSP_FRESH_CLOUD_DAEMON")
    host = cloud_host.bind(controller(blobs), plan, assets, blobs, guard, docker, folder, raw, review_hash)
    handlers = {number: signal.signal(number, interrupted) for number in (signal.SIGTERM, signal.SIGHUP)}
    old_umask = os.umask(0o077)
    try:
        return host.main()
    finally:
        os.umask(old_umask)
        for number, handler in handlers.items():
            signal.signal(number, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--execute-reviewed-cloud-csp", action="store_true")
    options = parser.parse_args()
    try:
        prepare.require(not options.execute_reviewed_cloud_csp or options.review is not None,
                        "CSP_INDEPENDENT_LITERAL_REVIEW_REQUIRED")
        plan, raw, files, blobs = verify_plan(prepare.ROOT, options.plan)
        reviewed = False
        if options.review is not None:
            read_review(prepare.stable_file(options.review), plan, raw)
            reviewed = True
        if options.execute_reviewed_cloud_csp:
            return execute(options.plan, options.review, plan, raw, files, blobs)
        controller(blobs)
        print(json.dumps({"status": "REPRODUCED_OFFLINE_NOT_RUN", "plan_sha256": prepare.sha(raw),
                          "repo_files": len(blobs), "generated_files": len(files), "review_bound": reviewed,
                          "operational_hold": plan["platform_gate"]}))
        return 0
    except (ValueError, OSError, KeyError, TypeError, SyntaxError, RuntimeError, subprocess.SubprocessError):
        print(json.dumps({"status": "HELD", "code": "CSP_CLOUD_PACKET_REFUSED"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
