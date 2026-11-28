"""Assemble a source-bound Cloud CSP packet. Preparation has no Docker or database edge."""

import argparse
import json
import os
from pathlib import Path
import re
import runpy
import stat
import subprocess
import uuid

import source7 as initial


ROOT = initial.ROOT
BASE = initial.BASE
SCRATCH = initial.SCRATCH
OWNED = "context/reconciliation/local-f0-operation-sources/customer-stale-predecessor-owned-v1"
OWNED_VALIDATION = "context/reconciliation/local-f0-customer-stale-predecessor-owned-v1-source-validation.json"
HISTORICAL_CATALOG = f"{OWNED}/author-history/first-pending-preparation-inputs/operation-manifest.json"
OPERATORS = (
    "execute_local_f0_customer_stale_predecessor_v1_20261120.py",
    "local_f0_customer_stale_predecessor_v1_operation_steps.py",
)
OPERATOR_PINS = (
    "b587b5da671680eb9edc9445c0ad876a86bdc814b850debbe5296a72bed3afe8",
    "6518f86457b63269668ad7241c8841f351bc117e0965899c5667c84e61a3ec10",
)
OWNED_VALIDATION_SHA = "f6b6965d9e153e3433225d924bc7c35b6ff251e90d55f99cb2192f32698c4772"
HISTORICAL_FIXTURE = "36e9cae1-53fc-44a7-b90f-b91fb6e8d2b5"
HISTORICAL_RUN = "73292a8f-838e-4d92-be2e-42170dd5ec6a"
CHILD = "scripts/sql-review/cloud-customer-stale-predecessor-v2"
CHILD_CORE = "scripts/sql-review/run-customer-stale-predecessor-v1.py"
CHILD_VALIDATION = "context/reconciliation/customer-stale-predecessor-v1-source-validation.json"
CLOSURE = "context/reconciliation/local-f0-tooling/cloud-v2/prisma-tools-closure.json"
PROFILE = "scripts/sql-review/cloud-f0-v1"
CAPABILITY = "context/reconciliation/cloud-phase0-evidence/2026-11-27/probe-862971a5"
CAPABILITY_PINS = {
    f"{CAPABILITY}/result.json": "35ee05063bd654bd182dc2bd92e2462a736a813cebf4596f539806e302e5f4ed",
    f"{CAPABILITY}/independent-closure.json": "fdb7c6c89c4a90e9036b6a67cd0950622a3e2dd959a46267e1544f71147c75ff",
}
AUTHOR = "Codex Cloud CSP owning composition"
REVIEW_SCOPES = ("source", "owned_resource", "safety_sql", "binary_transport", "operational_literals")
FILE_SET = (
    "README.md", "initial-attestation.mjs.txt", "source7.py", "prepare.py",
    "operate.py", "cloud_host.py", "test_prepare.py",
)
HASH = r"[a-f0-9]{64}"
HISTORICAL_SOURCE_GATES = (
    "independent_source_review", "independent_owned_resource_review",
    "independent_safety_sql_review", "independent_binary_transport_review", "Root_source_review",
)

require = initial.require
sha = initial.sha
encode = initial.encode


def parse(raw):
    def unique(items):
        value = dict(items)
        require(len(value) == len(items), "CSP_JSON_DUPLICATE_FIELD")
        return value

    def reject(_):
        raise ValueError("CSP_JSON_NONFINITE")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject)


def stable_file(path, max_bytes=16 * 1024 * 1024):
    path = Path(path)
    require(path.is_absolute() and path.resolve(strict=True) == path, "CSP_SOURCE_PATH_ALIAS")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as handle:
        before = os.fstat(handle.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= max_bytes,
                "CSP_FILE_TYPE_OR_BOUND")
        raw = handle.read(max_bytes + 1)
        after = os.fstat(handle.fileno())
    left = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
    for item in (after, path.lstat()):
        require(left == (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns),
                "CSP_FILE_IDENTITY_CHANGED")
    require(len(raw) == before.st_size, "CSP_FILE_READ_INCOMPLETE")
    return raw


def source_file(root, relative):
    require(type(relative) is str and not relative.startswith("/") and ":" not in relative
            and "\\" not in relative and all(part not in ("", ".", "..") for part in relative.split("/")),
            "CSP_RELATIVE_SOURCE_PATH")
    return stable_file(root / relative)


def git(root, *args, input=None):
    result = subprocess.run(["git", "-C", str(root), "--no-optional-locks", *args],
                            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=120, check=False)
    require(result.returncode == 0 and result.stderr == b"", "CSP_GIT_PROVENANCE_UNCONFIRMED")
    return result.stdout


def check_committed(root, files):
    head = git(root, "rev-parse", "HEAD").decode().strip()
    tree = git(root, "rev-parse", f"{head}^{{tree}}").decode().strip()
    require(all(re.fullmatch("[a-f0-9]{40}", ref) for ref in (head, tree)), "CSP_COMMIT_TREE_IDENTITY")
    names = sorted(files)
    query = "".join(f"{head}:{name}\n" for name in names).encode()
    raw = git(root, "cat-file", "--batch", input=query)
    index = 0
    for name in names:
        end = raw.index(b"\n", index)
        kind = raw[index:end].split()
        data = files[name]
        require(len(kind) == 3 and kind[1:] == [b"blob", str(len(data)).encode()],
                "CSP_COMMITTED_FILE_IDENTITY")
        index = end + 1
        require(raw[index:index + len(data) + 1] == data + b"\n", "CSP_COMMITTED_BYTES_MISMATCH")
        index += len(data) + 1
    require(index == len(raw) and git(root, "rev-parse", "HEAD").decode().strip() == head,
            "CSP_COMMITTED_MAP_CHANGED")
    return head, tree


def closed_files(root):
    def read(name):
        return source_file(root, name)

    validation = read(OWNED_VALIDATION)
    require(sha(validation) == OWNED_VALIDATION_SHA, "CSP_HISTORICAL_SOURCE_VALIDATION_CHANGED")
    owned = parse(validation)
    expected = owned["archive_files_sha256"].copy()
    actual = {file.relative_to(root).as_posix() for file in (root / OWNED).rglob("*") if file.is_file()}
    require(actual == set(expected), "CSP_HISTORICAL_ARCHIVE_INVENTORY")
    for key in HISTORICAL_SOURCE_GATES:
        review = owned[key]
        require(review["decision"] == "SOURCE_APPROVED" and review["path"].startswith(f"{OWNED}/reviews/")
                and expected.get(review["path"]) == review["sha256"]
                and review["operator_sources_sha256"] == owned["operator_sources_sha256"],
                "CSP_HISTORICAL_REVIEW_BINDING")
    for past, pinned in zip(OPERATORS, OPERATOR_PINS, strict=True):
        require(owned["operator_sources_sha256"][past] == pinned
                and expected[f"{OWNED}/{past}.txt"] == pinned, "CSP_HISTORICAL_OPERATOR_IDENTITY")
    for filename in ("fixed-catalog-source-map.json", "fixed-child-current-map.json"):
        path = f"{OWNED}/{filename}"
        raw = read(path)
        require(sha(raw) == expected[path], "CSP_HISTORICAL_MAP_DRIFT")
        for name, wanted in parse(raw).items():
            require(name not in expected or expected[name] == wanted, "CSP_INCONSISTENT_SOURCE_MAP")
            expected[name] = wanted
    child_validation = read(CHILD_VALIDATION)
    require(sha(child_validation) == expected[CHILD_VALIDATION], "CSP_HISTORICAL_CHILD_VALIDATION_DRIFT")
    for name, wanted in parse(child_validation)["source_files_sha256"].items():
        require(name not in expected or expected[name] == wanted, "CSP_INCONSISTENT_CHILD_SOURCE_MAP")
        expected[name] = wanted
    expected.update(CAPABILITY_PINS)
    required = {
        *initial.PINNED, f"{initial.HISTORY}/migration_lock.toml",
        *(f"{BASE}/{name}" for name in FILE_SET),
        *(f"{CHILD}/{name}" for name in ("README.md", "prepare.py", "test_prepare.py", "test_parser.py")),
        *(f"{initial.SHARED}/{name}" for name in ("prepare.py", "guard-platform.mjs.txt")),
        f"{PROFILE}/profile.json", f"{PROFILE}/guard.py", f"{PROFILE}/probe.py",
        "scripts/sql-review/local_image_identity.py",
        "scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json",
        "context/reconciliation/directives/cloud-phase0-standing-authority-2026-11-27.md",
        OWNED_VALIDATION, CLOSURE, "package.json", "package-lock.json", CHILD_CORE, CHILD_VALIDATION,
    }
    files = {name: read(name) for name in sorted(set(expected) | required)}
    require(all(sha(files[name]) == wanted for name, wanted in expected.items()), "CSP_HISTORICAL_SOURCE_DRIFT")
    return files


def build(root, run_id, fixture_id, daemon, tool_archive):
    folder, target = initial.run_target(run_id)
    fixture = uuid.UUID(fixture_id)
    require(fixture.version == 4 and str(fixture) == fixture_id
            and len({run_id, fixture_id, HISTORICAL_FIXTURE, HISTORICAL_RUN}) == 4,
            "CSP_DISTINCT_NEW_RUNS_REQUIRED")
    files = closed_files(root)
    head, tree = check_committed(root, files)
    capability = parse(files[f"{CAPABILITY}/result.json"])
    audit = parse(files[f"{CAPABILITY}/independent-closure.json"])
    require(capability["status"] == "PASS_CAPABILITY_SUBSET_ONLY"
            and capability["completed_capability_checks"] is True and capability["remote_outcome_unconfirmed"] is False
            and capability["cleanup"] == "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
            and capability["run_id"] == audit["run_id"] and run_id != capability["run_id"]
            and daemon == capability["daemon"] == audit["daemon"]
            and audit["decision"] == "EXACT_CLEANUP_AND_SYNTHETIC_CAPABILITY_SUBSET_SUPPORTED"
            and audit["same_live_daemon_socket_and_binary_verified"] is True
            and audit["file_sha256"]["result.json"] == sha(files[f"{CAPABILITY}/result.json"])
            and set(audit["absent_after"]) == {"container_id", "container_name", "private_host_path", "volume_name"}
            and all(value is True for value in audit["absent_after"].values())
            and capability["assertion_promotions"] == audit["assertion_promotions"] == 0
            and capability["target"]["bootstrap_container_path"] == target["bootstrap_container_path"],
            "CSP_INDEPENDENT_CLOUD_CAPABILITY_BINDING")
    for fname in ("probe.py", "guard.py", "profile.json"):
        relative = f"{PROFILE}/{fname}"
        require(capability["source"]["files_sha256"][relative] == sha(files[relative]),
                "CSP_CAPABILITY_IMPLEMENTATION_CHANGED")
    migration, source = initial.build(root, run_id, daemon, tool_archive)
    closure = parse(files[CLOSURE])
    require(migration["tools"]["archive_sha256"] == closure["archive_sha256"]
            and migration["tools"]["files_sha256"] == closure["tools_files_sha256"]
            and migration["tools"]["file_sizes"] == closure["tools_file_sizes"]
            and sha(files["package-lock.json"]) == closure["root_package_lock_sha256"]
            and sha(files["package.json"]) == closure["root_package_json_sha256"],
            "CSP_PATCHED_TOOL_CLOSURE_REQUIRED")
    generator = runpy.run_path(str(root / CHILD / "prepare.py"))
    child, fixture_packet = generator["build"](root, fixture_id)
    require(len(child) == 12, "CSP_EXACT_CHILD12")
    assets = {f"child/{name}": text.encode() for name, text in child.items()}
    assets.update({f"source7/{name}": raw for name, raw in source.items()})
    assets["migration-manifest.json"] = encode(migration)
    assets["source7.tar.gz"] = initial.archive(source)
    pins = {name: sha(raw) for name, raw in files.items()}
    old_catalog = parse(files[HISTORICAL_CATALOG])["catalog"]
    new_catalog = {**old_catalog, "tool_source_files_sha256": {
        name: migration["tools"]["files_sha256"][name] for name in old_catalog["tool_source_files_sha256"]
    }}
    return folder, {
        "schema": "workinants.cloud-customer-stale-predecessor-owned-plan.v2",
        "purpose": "CLOUD_F0_CUSTOMER_STALE_PREDECESSOR_OWNED_V2",
        "authority": "context/reconciliation/directives/cloud-phase0-standing-authority-2026-11-27.md",
        "run_id": run_id, "fixture_run_id": fixture_id, "author": AUTHOR,
        "source_commit": head, "source_tree": tree, "packet_files_sha256": pins,
        "packet_sha256": sha(encode(pins)),
        "generated_files_sha256": {name: sha(raw) for name, raw in assets.items()},
        "migration_tool_archive": str(tool_archive), "migration_tool_archive_sha256": closure["archive_sha256"],
        "target": target, "daemon": migration["daemon"], "catalog": new_catalog,
        "evidence_directory": str(folder / "evidence"),
        "fixture_content_sha256": fixture_packet["content_sha256"],
        "platform_gate": "CLOUD_TMPFS_V2_CAPABILITY_BOUND_FRESH_OPERATIONAL_REVIEW_REQUIRED",
        "capability_receipt_sha256": sha(files[f"{CAPABILITY}/result.json"]),
        "runtime": "NOT_RUN", "review_status": "PENDING_INDEPENDENT_OPERATIONAL_REVIEW",
        "Posture": "D",
    }, assets


def write_new(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daemon-evidence", type=Path, required=True)
    parser.add_argument("--tool-archive", type=Path, required=True)
    options = parser.parse_args()
    try:
        require(options.tool_archive.is_absolute() and options.tool_archive.resolve(strict=True) == options.tool_archive,
                "CSP_TOOL_ARCHIVE_PATH_ALIAS")
        daemon = parse(stable_file(options.daemon_evidence))
        run_id = str(uuid.uuid4())
        folder, plan, assets = build(ROOT, run_id, str(uuid.uuid4()), daemon, options.tool_archive)
        folder.mkdir(mode=0o700)
        for name, raw in assets.items():
            write_new(folder / name, raw)
        raw = encode(plan)
        write_new(folder / "operation-plan.json", raw)
        print(json.dumps({"status": "PREPARED_NOT_RUN", "plan_sha256": sha(raw),
                          "plan_path": str(folder / "operation-plan.json"), "run_id": run_id}))
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError):
        print(json.dumps({"status": "HELD", "code": "CSP_CLOUD_PREPARATION_REFUSED"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
