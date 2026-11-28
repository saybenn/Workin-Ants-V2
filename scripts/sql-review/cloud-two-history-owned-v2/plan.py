"""Prepare a held, exact-source Cloud TWO plan without opening Docker."""

import argparse
from pathlib import Path
import sys
import uuid

from basis import ROOT, PROBE, CAPABILITY, INNER, S, P, capture, capability, safe_code


SCHEMA = "workinants.cloud-f0-two-history-owned-operation.v2"
SOURCE_REVIEW = "workinants.cloud-f0-two-history-source-review.v2"
LITERAL_REVIEW = "workinants.cloud-f0-two-history-literal-review.v2"
LITERAL_SCOPES = [
    "actual_socket_daemon_image_and_target_names",
    "mounted_storage_and_stdin_bootstrap_only",
    "exact_packet_tool_parser_and_sql_inputs",
    "real_migration_scope_auth_and_original_grantor",
    "closed_clients_and_controlled_exclusive_cleanup",
]
SOURCE_SCOPES = P.SOURCE_SCOPES


def compose(tool_archive, run_id, *, draft=False, root=ROOT):
    blobs, historical = capture(root)
    identity = None if draft else S.verify_committed(root, blobs)
    probe, result, audit = capability(blobs)
    inner = S.module(root, f"{INNER}/prepare.py", blobs[f"{INNER}/prepare.py"])
    S.require(inner.RUN_SCHEMA.endswith(".v2") and inner.CLOSURE_PATH == S.TOOL_CLOSURE,
              "MOUNTLESS_V2_INNER_REQUIRED")
    manifest, manifest_raw, files = inner.build(root, run_id, probe["daemon"], tool_archive)
    target = manifest["target"]
    prior_names = [probe["target"]["container"], probe["target"]["volume"]]
    S.require(run_id != probe["run_id"] and target["container_name"] not in prior_names
              and target["volume_name"] not in prior_names and target["bootstrap"] == inner.BOOTSTRAP
              and "bootstrap_secret_host_path" not in target,
              "FRESH_V2_ONLY_RESOURCE_IDENTITY")
    archive = inner.archive_source(files)
    directory = P.SCRATCH / f"wa-cloud-f0-two-history-{run_id}"
    profile = S.unique_json(blobs[f"{PROBE}/profile.json"])
    S.require(profile["bootstrap_file"] == target["bootstrap"]["container_path"]
              and profile["bootstrap_transport"] == target["bootstrap"]["transport"], "BOOTSTRAP_PROFILE_MATCH")
    profile["credential_tmpfs_options"] = target["bootstrap"]["tmpfs_options"]
    pins = {name: S.sha(raw) for name, raw in blobs.items()}
    native_files = S.reproduce_native(root, blobs)
    operation = {
        "schema": SCHEMA, "status": "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_REVIEW",
        "run_id": run_id, "source": identity,
        "source_pins": pins, "source_aggregate_sha256": S.aggregate(pins),
        "historical_source_reviews": historical, "historical_reviews_supply_execution_authority": False,
        "capability_prerequisite": {
            "run_id": probe["run_id"], "result_sha256": pins[f"{CAPABILITY}/result.json"],
            "closure_sha256": pins[f"{CAPABILITY}/independent-closure.json"],
            "reviewer": audit["reviewer"], "cleanup": result["cleanup"],
        },
        "nested_manifest": P.bind(directory / "run-manifest.json", manifest_raw),
        "archive": P.bind(directory / "source8.tar", archive),
        "tools": {"path": str(tool_archive), "sha256": inner.TOOL_TAR_SHA,
                  "bytes": inner.TOOL_TAR_SIZE, "files": 10300},
        "source8": {name: S.sha(data) for name, data in files.items()},
        "profile": profile, "daemon": probe["daemon"], "image": probe["cached_image"],
        "target": target, "database": "wa_p0c_rehearsal", "runtime_cases": dict.fromkeys(P.RUNTIME_STAGES, "NOT_RUN"),
        "native_expected_sha256": S.EXPECTED, "native_files_sha256": native_files,
        "expected_expression_count": 416, "parser": P.parser_pin(),
        "posture": "D", "assertion_promotions": 0, "candidate_adoption": False,
    }
    return directory, operation, blobs, inner, manifest, manifest_raw, files, archive


def prepare(tool_archive, *, draft=False):
    directory, operation, _, _, _, nested, files, archive = compose(
        tool_archive, str(uuid.uuid4()), draft=draft
    )
    directory.mkdir(mode=0o700)
    P.private_path(directory, file=False)
    P.write_new(directory / "run-manifest.json", nested)
    P.write_new(directory / "source8.tar", archive)
    P.write_source(directory / "source8", files)
    path = directory / "operation.json"
    raw = S.encode(operation)
    P.write_new(path, raw)
    return {"packet": str(path), "sha256": S.sha(raw), "state": operation["status"],
            "source_files": len(operation["source_pins"]), "runtime": "NOT_RUN"}


def read_closed(path, *, draft=False):
    P.private_path(path.parent, file=False)
    raw = S.read(P.private_path(path, file=True))
    value = S.unique_json(raw)
    S.require(value["schema"] == SCHEMA and value["status"] == (
        "SOURCE_DRAFT_NOT_RUN" if draft else "HELD_PENDING_EXACT_REVIEW"
    ), "EXACT_COMMITTED_PLAN_REQUIRED")
    prepared = compose(Path(value["tools"]["path"]), value["run_id"], draft=draft)
    directory, expected, _, _, _, nested, files, archive = prepared
    S.require(path == directory / "operation.json" and raw == S.encode(expected), "PACKET_CLOSURE_CHANGED")
    compare_source8(directory, nested, files, archive)
    return prepared, raw


def compare_source8(directory, nested, files, archive):
    S.require(S.read(P.private_path(directory / "run-manifest.json", file=True)) == nested
              and S.read(P.private_path(directory / "source8.tar", file=True)) == archive,
              "SOURCE8_ARCHIVE_OR_MANIFEST_DRIFT")
    root = P.private_path(directory / "source8", file=False)
    inventory = tuple(root.rglob("*"))
    S.require(all(not path.is_symlink() and (path.is_file() or path.is_dir()) for path in inventory),
              "SOURCE8_INVENTORY_SHAPE")
    leafs = {path.relative_to(root).as_posix(): path for path in inventory if path.is_file()}
    directories = {P.private_path(path, file=False).relative_to(root) for path in inventory if path.is_dir()}
    S.require(set(leafs) == set(files) and directories == {
        parent for name in files for parent in Path(name).parents if parent != Path(".")
    } and all(S.read(P.private_path(path, file=True)) == files[name] for name, path in leafs.items()),
              "FULL_SOURCE8_READBACK")


def review_bindings(operation, raw):
    return {
        "packet_sha256": S.sha(raw), "source_commit": operation["source"]["commit"],
        "source_tree": operation["source"]["tree"], "operation_run_id": operation["run_id"],
        "all_sources_sha256": operation["source_aggregate_sha256"],
        "nested_plan_sha256": operation["nested_manifest"]["sha256"],
        "source_archive_sha256": operation["archive"]["sha256"],
        "tool_archive_sha256": operation["tools"]["sha256"],
    }


def exact_reviews(directory, operation, raw):
    bindings = review_bindings(operation, raw)
    source, source_hash = P.read_review(directory / "source-review.json", schema=SOURCE_REVIEW,
                                        bindings=bindings, scopes=SOURCE_SCOPES)
    literal, literal_hash = P.read_review(
        directory / "literal-review.json", schema=LITERAL_REVIEW,
        bindings={**bindings, "source_review_sha256": source_hash}, scopes=LITERAL_SCOPES,
    )
    S.require(literal["source_author"] == source["source_author"], "REVIEWED_AUTHOR_IDENTITY_DRIFT")
    return {"source": source_hash, "literal": literal_hash,
            "source_reviewer": source["reviewer"], "literal_reviewer": literal["reviewer"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    make = sub.add_parser("prepare")
    make.add_argument("--tool-archive", type=Path, required=True)
    make.add_argument("--draft", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("packet", type=Path)
    verify.add_argument("--draft", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "prepare":
            value = prepare(args.tool_archive, draft=args.draft)
        else:
            prepared, raw = read_closed(args.packet, draft=args.draft)
            value = {"sha256": S.sha(raw), "source_files": len(prepared[1]["source_pins"]), "state": "HELD_VERIFIED",
                     "runtime": "NOT_RUN"}
        print(S.encode(value).decode(), end="")
        return 0
    except Exception as error:
        print(S.encode({"status": "HELD", "code": safe_code(error), "runtime": "NOT_RUN"}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
