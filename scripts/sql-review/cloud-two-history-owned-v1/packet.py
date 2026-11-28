"""Assemble and verify a held TWO Cloud source packet. Database operations are absent."""

import argparse
import os
from pathlib import Path
import re
import stat
import sys
import uuid

from sources import (
    BASE, ROOT, EXPECTED, HEX40, INNER_PREFIX, HOST_PREFIX, TOOL_CLOSURE, Held,
    absolute, aggregate, capture, encode, module, read, reproduce_native, require, sha,
    unique_json, verify_committed,
)
from bridge import required_execs, result_validator


SCRATCH = Path("/workspace/scratch")
SCHEMA = "workinants.cloud-f0-two-history-owned-source-packet.v1"
SOURCE_REVIEW = "workinants.cloud-f0-two-history-source-review.v1"
LITERAL_REVIEW = "workinants.cloud-f0-two-history-literal-review.v1"
SOURCE_SCOPES = [
    "immutable_ordered_migrations_and_catalog_expectations",
    "committed_cloud_source_closure",
    "strict_cloud_result_and_transport",
    "candidate_resource_and_cleanup_controls",
    "patched_tool_closure",
]
RUNTIME_STAGES = [
    "VerifyDaemonImageAndExactAbsence",
    "VerifyClaimedContainerVolumeKernelAndTmpfs",
    "VerifyToolsAndBootstrapAuthority",
    "DeployTwoMigrationsViaRestrictedMigrator",
    "CloseAllClientsAndFinalizeWithOriginalGrantor",
    "VerifyActualTwoRowsBeforeActivation",
    "ActivateAndVerifyExactScramLogins",
    "VerifyNativeCatalogExpressionOracleAndLedger",
    "ObserveStatusAndSecondDeployNoPendingMarker",
    "ProveAllEightLedgerColumnsAndNativeParity",
    "VerifyExactCleanupAndImmutableSources",
]


def private_path(path, *, file):
    absolute(path)
    info = path.lstat()
    require(info.st_uid == os.getuid(), "PRIVATE_OWNER")
    if file:
        require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
                and info.st_nlink == 1, "PRIVATE_FILE")
    else:
        require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700, "PRIVATE_DIRECTORY")
    return path


def parser_pin():
    import pglast
    from pglast import parser

    require(pglast.__version__ == "v7.21", "PGLAST_VERSION_MISMATCH")
    origin = absolute(Path(pglast.__file__))
    native = absolute(Path(parser.__file__))
    require(native.parent == origin.parent and native.name.endswith(".so"), "PGLAST_NATIVE_IDENTITY")
    paths = sorted(p for p in origin.parent.rglob("*") if p.is_file() and p.suffix in (".py", ".so"))
    require(origin in paths and native in paths and len(paths) <= 64, "PGLAST_FILE_SCOPE")
    files = {p.relative_to(origin.parent).as_posix(): sha(read(p, 32 * 1024 * 1024 if p == native else 1024 * 1024))
             for p in paths}
    return {"version": pglast.__version__, "root": str(origin.parent),
            "files_sha256": files, "files_aggregate_sha256": aggregate(files),
            "python": ".".join(map(str, sys.version_info[:3]))}


def bind(path, raw):
    return {"path": str(path), "bytes": len(raw), "sha256": sha(raw)}


def write_new(path, raw):
    with os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600), "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def write_source(directory, files):
    directory.mkdir(mode=0o700)
    for name, raw in files.items():
        leaf = directory / name
        leaf.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_new(leaf, raw)


def pending_runtime_shape(inner, manifest, paths, image_id):
    target = manifest["target"]
    # An explicitly non-authoritative sizing placeholder. It is neither
    # persisted as an observed target nor accepted by the host's live checks.
    placeholder = {
        "endpoint": inner.ENDPOINT,
        "daemon": manifest["daemon"],
        "container_id": "0" * 64,
        "container_name": target["container_name"], "volume_name": target["volume_name"],
        "volume_created_at": "2000-01-01T00:00:00.000000000Z",
        "image": target["image"], "image_id": image_id,
        "network": "none", "published_ports": False, "labels": target["labels"],
        "bootstrap_secret_host_path": target["bootstrap_secret_host_path"],
        "bootstrap_readonly": True,
    }
    sizes = {}
    for operation in ("deploy", "status"):
        _, raw = required_execs(inner, manifest, paths, placeholder, operation)
        require(len(raw) < 4 * 1024 * 1024, "PRIVATE_ATTESTATION_INPUT_BOUND")
        sizes[operation] = len(raw)
    return sizes


def assemble(daemon, tool_archive, run_id, *, draft=False, root=ROOT):
    sources, historical_reviews = capture(root)
    identity = None if draft else verify_committed(root, sources)
    pins = {name: sha(raw) for name, raw in sources.items()}
    pinned_parser = parser_pin()
    immutable_native = reproduce_native(root, sources)
    inner_name = f"{INNER_PREFIX}/prepare.py"
    inner = module(root, inner_name, sources[inner_name])
    closure = unique_json(sources[TOOL_CLOSURE])
    require(inner.CLOSURE_PATH == TOOL_CLOSURE
            and closure["archive_sha256"] == inner.TOOL_TAR_SHA
            and closure["archive_bytes"] == inner.TOOL_TAR_SIZE, "PATCHED_CLOUD_TOOL_CLOSURE")
    run_manifest, manifest_raw, source8 = inner.build(root, run_id, daemon, tool_archive)
    # Compile the selected strict receipt validator now, before any operation.
    result_validator(root, sources)
    source_tar = inner.archive_source(source8)
    packet = SCRATCH / f"wa-cloud-f0-two-history-{run_id}"
    target = run_manifest["target"]
    require(Path(target["bootstrap_secret_host_path"]) == packet / "private/ok-bootstrap-password",
            "BOOTSTRAP_SECRET_SCOPE")
    profile = unique_json(sources[f"{HOST_PREFIX}/profile.json"])
    require(profile["credential_tmpfs_options"].endswith(",size=1m"), "CLOUD_PROFILE_BASE_PIN")
    # The validated inner attestation includes all tool paths and sizes. TWO
    # keeps the same private mount/options and needs a larger bounded tmpfs.
    profile = {**profile, "credential_tmpfs_options": "rw,nosuid,nodev,noexec,mode=0700,size=8m"}
    capsule = {
        "schema": SCHEMA,
        "status": "HELD_DRAFT_NOT_COMMITTED" if draft else "HELD_PENDING_INDEPENDENT_REVIEW",
        "run_id": run_id,
        "source_root": str(root),
        "review_state": {"source": "PENDING", "operational_literal": "PENDING"},
        "runtime_release": "HELD_PENDING_WITNESSED_CLOUD_BOOTSTRAP_AND_OWNING_CONTROLLER",
        "runtime": dict.fromkeys(RUNTIME_STAGES, "NOT_RUN"),
        "identity": identity,
        "source_pins": pins,
        "source_aggregate_sha256": aggregate(pins),
        "historical_reviews": historical_reviews,
        "historical_reviews_supply_runtime_authority": False,
        "daemon": daemon,
        "profile": profile,
        "target": target,
        "tool_archive": {"path": str(tool_archive), "bytes": closure["archive_bytes"],
                         "sha256": closure["archive_sha256"], "members": closure["file_count"]},
        "manifest": bind(packet / "run-manifest.json", manifest_raw),
        "source_archive": bind(packet / "public-source8.tar", source_tar),
        "source8_files_sha256": {name: sha(raw) for name, raw in source8.items()},
        "native_expected_sha256": EXPECTED,
        "native_artifacts_sha256": immutable_native,
        "expression_oracle_expected_count": 416,
        "attestation_size_estimate_bytes": pending_runtime_shape(inner, run_manifest, source8, inner.IMAGE_IDS[1]),
        "parser": pinned_parser,
        "posture": "D",
        "assertion_promotions": 0,
        "limits": {"candidate_baseline_adopted": False, "hosted_contact": False,
                   "business_assertions_qualified": False, "worker_execution": False},
    }
    return packet, capsule, manifest_raw, source_tar, source8


def prepare(daemon_path, tool_archive, *, draft=False):
    daemon = unique_json(read(daemon_path, 65536))
    packet, capsule, manifest_raw, source_tar, source8 = assemble(
        daemon, tool_archive, str(uuid.uuid4()), draft=draft
    )
    packet.mkdir(mode=0o700)
    private_path(packet, file=False)
    write_new(packet / "run-manifest.json", manifest_raw)
    write_new(packet / "public-source8.tar", source_tar)
    write_source(packet / "source8", source8)
    output = encode(capsule)
    write_new(packet / "operation-source-packet.json", output)
    return {"path": str(packet / "operation-source-packet.json"), "sha256": sha(output),
            "sources": len(capsule["source_pins"]), "runtime": "NOT_RUN", "status": capsule["status"]}


def read_review(path, *, schema, bindings, scopes):
    private_path(path, file=True)
    raw = read(path, 65536)
    review = unique_json(raw)
    require(type(review) is dict and set(review) == {
        "schema", "decision", "reviewer", "source_author", "bindings", "scopes",
    } and review["schema"] == schema and review["decision"] == "APPROVE"
            and all(type(review[field]) is str and re.fullmatch(r"[a-zA-Z0-9_/.-]{1,100}", review[field])
                    for field in ("reviewer", "source_author"))
            and review["reviewer"] != review["source_author"]
            and review["bindings"] == bindings and review["scopes"] == scopes,
            "FRESH_TYPED_REVIEW_REQUIRED")
    return review, sha(raw)


def verify(path, *, draft=False):
    private_path(path.parent, file=False)
    raw = read(private_path(path, file=True))
    value = unique_json(raw)
    if draft:
        require(value["status"] == "HELD_DRAFT_NOT_COMMITTED" and value["identity"] is None,
                "HELD_DRAFT_REQUIRED")
    else:
        require(value["status"] == "HELD_PENDING_INDEPENDENT_REVIEW"
                and type(value["identity"]) is dict and HEX40.fullmatch(value["identity"]["commit"]),
                "COMMITTED_PACKET_REQUIRED")
    require(value["schema"] == SCHEMA, "CLOUD_SOURCE_PACKET_SCHEMA")
    packet, expected, manifest, archive, files = assemble(
        value["daemon"], Path(value["tool_archive"]["path"]), value["run_id"], draft=draft
    )
    require(path == packet / "operation-source-packet.json" and encode(expected) == raw,
            "HELD_COMPOSITION_BYTE_DRIFT")
    require(read(private_path(packet / "run-manifest.json", file=True)) == manifest
            and read(private_path(packet / "public-source8.tar", file=True)) == archive,
            "HELD_CHILD_ARCHIVE_DRIFT")
    source8_path = private_path(packet / "source8", file=False)
    inventory = tuple(source8_path.rglob("*"))
    require(all(not leaf.is_symlink() and (leaf.is_file() or leaf.is_dir()) for leaf in inventory),
            "HELD_SOURCE8_FILE_OR_DIRECTORY_REQUIRED")
    directories = {p for name in files for p in Path(name).parents if p != Path(".")}
    found_directories = {private_path(leaf, file=False).relative_to(source8_path)
                         for leaf in inventory if leaf.is_dir()}
    require(found_directories == directories, "HELD_SOURCE8_DIRECTORY_DRIFT")
    found = {leaf.relative_to(source8_path).as_posix() for leaf in inventory if leaf.is_file()}
    require(found == set(files) and all(read(private_path(source8_path / name, file=True)) == body
                                        for name, body in files.items()), "HELD_SOURCE8_CLOSURE_DRIFT")
    return {"sha256": sha(raw), "sources": len(expected["source_pins"]),
            "status": "VERIFIED_HELD_DRAFT_ONLY" if draft else "VERIFIED_HELD_SOURCES_ONLY",
            "runtime": "NOT_RUN"}


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="action", required=True)
    new = commands.add_parser("prepare")
    new.add_argument("--daemon-observation", type=Path, required=True)
    new.add_argument("--tool-archive", type=Path, required=True)
    new.add_argument("--draft", action="store_true")
    check = commands.add_parser("verify")
    check.add_argument("packet", type=Path)
    check.add_argument("--draft", action="store_true")
    args = cli.parse_args(argv)
    try:
        output = (prepare(args.daemon_observation, args.tool_archive, draft=args.draft)
                  if args.action == "prepare" else verify(args.packet, draft=args.draft))
    except (Held, KeyError, TypeError, ValueError, OSError) as error:
        code = str(error)
        if not re.fullmatch(r"[A-Z0-9_]{1,100}", code):
            code = "HELD_SOURCE_COMPOSITION_REFUSED"
        print(encode({"status": "HELD", "code": code, "runtime": "NOT_RUN"}).decode(), end="")
        return 1
    print(encode(output).decode(), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
