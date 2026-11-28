"""Exercise the prepared source8 with real tool bytes and modeled runtime edges."""

import argparse
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


def test_archive(source, files):
    with tarfile.open(fileobj=io.BytesIO(source), mode="r:") as archive:
        entries = archive.getmembers()
        assert len(entries) == len(files) == 8
        assert {item.name for item in entries} == set(files)
        for item in entries:
            assert item.isreg() and item.uid == item.gid == item.mtime == 0 and item.mode == 0o444
            with archive.extractfile(item) as file:
                assert file.read() == files[item.name]


def copy_verified_tools(archive, tool_root, file_sizes):
    seen = set()
    with prepare.regular(archive, prepare.TOOL_TAR_SIZE) as (stream, _):
        # Validate the exact archive again on the same descriptor used to unpack.
        import hashlib
        assert hashlib.file_digest(stream, "sha256").hexdigest() == prepare.TOOL_TAR_SHA
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r|gz") as members:
            for member in members:
                assert member.isreg() and member.name not in seen and file_sizes[member.name] == member.size
                path = tool_root / member.name
                assert path.resolve().is_relative_to(tool_root)
                path.parent.mkdir(parents=True, exist_ok=True)
                with members.extractfile(member) as contents, path.open("xb") as output:
                    shutil.copyfileobj(contents, output)
                path.chmod(member.mode)
                seen.add(member.name)
    assert seen == set(file_sizes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-archive", required=True, type=Path)
    args = parser.parse_args()
    manifest, raw, files = prepare.build(prepare.ROOT, RUN, DAEMON, args.tool_archive)
    test_archive(prepare.archive_source(files), files)
    assert len(manifest["tools"]["file_sizes"]) == 10300
    assert manifest["tools"]["file_sizes"]["node/bin/node"] == 126879696
    assert manifest["tools"]["file_sizes"]["schema-engine"] == 23516472
    assert prepare.strict_json(raw) == manifest
    assert prepare.sha(files[prepare.ORDERED[0]["path"]]) == prepare.INITIAL
    assert prepare.sha(files[prepare.ORDERED[1]["path"]]) == prepare.APPEND
    assert prepare.sha(files[prepare.SCHEMA]) == prepare.SCHEMA_SHA

    target = manifest["target"]
    observed = {key: target[key] for key in ("container_name", "volume_name", "image", "network",
                                            "labels", "bootstrap_secret_host_path")}
    observed.update(endpoint=prepare.ENDPOINT, daemon=DAEMON, container_id="b" * 64,
                    volume_created_at="2026-11-28T05:18:51Z", image_id=prepare.IMAGE_IDS[0],
                    published_ports=False, bootstrap_readonly=True)
    attestation = prepare.attest(manifest, observed, "deploy")
    fixtures = {
        "source8_count": len(files),
        "source8_archive_sha256": prepare.sha(prepare.archive_source(files)),
        "migration_and_schema_bytes_preserved": True,
        "archive_files_sha256_rechecked": 10300,
        "tool_archive_sha256": manifest["tools"]["archive_sha256"],
        "attestation_bytes": len(attestation),
    }
    with tempfile.TemporaryDirectory(prefix="wa-two-history-offline-") as temporary:
        directory = Path(temporary).resolve()
        source_root = directory / "source8"
        tools_root = directory / "tools"
        tools_root.mkdir()
        for name, contents in files.items():
            path = source_root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        copy_verified_tools(args.tool_archive, tools_root, manifest["tools"]["file_sizes"])
        attestation_file = directory / "attestation.json"
        attestation_file.write_bytes(attestation)
        # The verified Node executable runs only the test. The modeled spawn and
        # attestation storage inside the test never launch Prisma or create a DB.
        result = subprocess.run([str(tools_root / "node/bin/node"), str(prepare.HERE / "test-guard.mjs"),
                                 str(source_root), str(tools_root), str(attestation_file)],
                                check=True, capture_output=True, text=True, timeout=90)
        print(json.dumps(fixtures | json.loads(result.stdout), indent=2))


if __name__ == "__main__":
    main()
