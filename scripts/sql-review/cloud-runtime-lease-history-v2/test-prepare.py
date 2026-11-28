"""Verify the Cloud v2 packet and guarded runner without Docker or Prisma."""

import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

import prepare


RUN = "d5f4e7da-9e09-4cc2-9def-75aa7caaf931"
DAEMON = {
    "daemon_id": "synthetic-test-daemon",
    "version": "29.9.2",
    "os": "linux",
    "architecture": "amd64",
    "rootless": True,
    "socket": {"real_path": "/run/docker.sock", "device": 1, "inode": 7, "uid": 1000, "gid": 1000, "mode": 0o660},
    "docker_binary_sha256": "a" * 64,
}
PROBE_COMMIT = "fc5b5879abb5bd764fc0e5f5c1a03f95e2b0b7c8"


def test_probe_anchors():
    raw = subprocess.check_output(
        ["git", "show", PROBE_COMMIT + ":scripts/sql-review/cloud-f0-v1/probe.py"],
        cwd=prepare.ROOT, timeout=10,
    )
    names = {"START_CONTROL": "startup_gate_sha256", "WRITE_BOOTSTRAP": "write_gate_sha256"}
    checked = set()
    for node in ast.parse(raw).body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                key = names[target.id]
                assert prepare.sha(ast.literal_eval(node.value).encode()) == prepare.BOOTSTRAP[key]
                checked.add(key)
    assert checked == set(names.values())


def test_source_archive(archive, files):
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
        entries = source.getmembers()
        assert len(entries) == 8 and {member.name for member in entries} == set(files)
        for member in entries:
            assert member.isreg() and member.mode == 0o444 and member.uid == member.gid == member.mtime == 0
            with source.extractfile(member) as content:
                assert content.read() == files[member.name]


def extract_pinned_tools(archive, destination, sizes):
    seen = set()
    with prepare.v1.regular(archive, prepare.TOOL_TAR_SIZE) as (stream, _):
        assert hashlib.file_digest(stream, "sha256").hexdigest() == prepare.TOOL_TAR_SHA
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r|gz") as members:
            for member in members:
                assert member.isreg() and member.name not in seen and sizes[member.name] == member.size
                path = destination / member.name
                assert path.resolve().is_relative_to(destination)
                path.parent.mkdir(parents=True, exist_ok=True)
                with members.extractfile(member) as contents, path.open("xb") as output:
                    shutil.copyfileobj(contents, output)
                path.chmod(member.mode)
                seen.add(member.name)
    assert seen == set(sizes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-archive", required=True, type=Path)
    args = parser.parse_args()
    test_probe_anchors()
    manifest, raw, files = prepare.build(prepare.ROOT, RUN, DAEMON, args.tool_archive)
    archive = prepare.archive_source(files)
    test_source_archive(archive, files)
    assert prepare.strict_json(raw) == manifest
    assert prepare.sha(files[prepare.ORDERED[0]["path"]]) == prepare.INITIAL
    assert prepare.sha(files[prepare.ORDERED[1]["path"]]) == prepare.APPEND
    assert prepare.sha(files[prepare.SCHEMA]) == prepare.SCHEMA_SHA
    history = prepare.strict_json(files[prepare.HISTORY_MANIFEST])
    assert history["ordered"] == prepare.ORDERED
    assert history["effective_expected_sha256"] == prepare.EFFECTIVE
    assert history["run_manifest_sha256"] == prepare.sha(raw)

    target = manifest["target"]
    observed = {key: target[key] for key in ("container_name", "volume_name", "image", "network", "labels", "bootstrap")}
    observed.update(endpoint=prepare.ENDPOINT, daemon=DAEMON, container_id="b" * 64, published_ports=False,
                    volume_created_at="2026-11-28T05:18:51Z", image_id=prepare.IMAGE_IDS[0],
                    bootstrap_removed=True, mount_destinations=list(prepare.MOUNT_DESTINATIONS))
    attestation = prepare.attest(manifest, observed, "deploy", packet_sha256="c" * 64, literal_review_sha256="d" * 64)
    try:
        prepare.attest(manifest, dict(observed, bootstrap_removed=False), "deploy",
                       packet_sha256="c" * 64, literal_review_sha256="d" * 64)
    except prepare.Held as error:
        assert str(error) == "LIVE_RESOURCE_IDENTITY"
    else:
        raise AssertionError("retained bootstrap credential accepted")
    assert len(attestation) > 1024 * 1024 and len(attestation) < 4 * 1024 * 1024

    with tempfile.TemporaryDirectory(prefix="wa-two-history-cloud-v2-offline-") as temporary:
        directory = Path(temporary).resolve()
        source_root = directory / "source8"
        tool_root = directory / "tools"
        for name, content in files.items():
            path = source_root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        extract_pinned_tools(args.tool_archive, tool_root, manifest["tools"]["file_sizes"])
        attestation_file = directory / "attestation.json"
        attestation_file.write_bytes(attestation)
        result = subprocess.run([str(tool_root / "node/bin/node"), str(prepare.HERE / "test-guard.mjs"),
                                 str(source_root), str(tool_root), str(attestation_file)],
                                check=True, capture_output=True, text=True, timeout=90)
        print(json.dumps({
            "source8_files": len(files), "source8_archive_sha256": prepare.sha(archive),
            "exact_probe_gate_bindings": 2, "migration_and_schema_bytes_preserved": True,
            "tar_member_hashes": len(manifest["tools"]["files_sha256"]), "attestation_bytes": len(attestation),
            "tool_archive_sha256": manifest["tools"]["archive_sha256"],
        } | json.loads(result.stdout), indent=2))


if __name__ == "__main__":
    main()
