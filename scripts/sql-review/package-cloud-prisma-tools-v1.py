"""Reproduce and verify the existing Linux Prisma tool archive from a pinned npm install."""

import argparse
import base64
import gzip
import hashlib
import json
import os
import stat
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "context/reconciliation/local-f0-tooling"
CLOSURE_SHA256 = "610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b"
TOOLING_SHA256 = "e8fcce8f3ed4eaad0f7834e908166a0947b997e75513d589078f0d79c9a940d0"
EXECUTABLES = {"node/bin/node", "schema-engine"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pinned_json(path, expected):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, f"record digest mismatch: {path.name}")
    return json.loads(data)


@contextmanager
def regular_file(path):
    require(path.resolve(strict=True) == path, f"linked input path: {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as source:
        info = os.fstat(source.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, f"non-regular input: {path}")
        yield source, info


def verify_registry_packages(closure, lock, cache):
    inventories = {package["path"]: {} for package in closure["packages"]}
    for name, expected in closure["tools_files_sha256"].items():
        if name in EXECUTABLES:
            continue
        member = PurePosixPath(name)
        for parent in member.parents:
            if parent.as_posix() in inventories:
                inventories[parent.as_posix()][member.relative_to(parent).as_posix()] = expected
                break
        else:
            raise ValueError(f"archive member outside locked closure: {name}")

    for package in closure["packages"]:
        name = package["path"]
        entry = lock[name]
        sri = package["lock_integrity"]
        url = urlsplit(entry["resolved"])
        require(entry["version"] == package["version"] and entry["integrity"] == sri,
                f"registry lock differs: {name}")
        require(url.scheme == "https" and url.netloc == "registry.npmjs.org",
                f"unexpected registry source: {name}")
        algorithm, encoded = sri.split("-", 1)
        digest = base64.b64decode(encoded, validate=True)
        require(algorithm == "sha512" and len(digest) == 64, f"invalid lock integrity: {name}")
        hex_digest = digest.hex()
        blob = cache / "_cacache/content-v2/sha512" / hex_digest[:2] / hex_digest[2:4] / hex_digest[4:]
        require(blob.is_file(), f"missing locked registry blob: {name}")
        remaining = inventories[name]
        require(bool(remaining), f"locked package has no recorded file members: {name}")
        with regular_file(blob) as (source, _):
            require(hashlib.file_digest(source, "sha512").digest() == digest,
                    f"registry blob digest mismatch: {name}")
            source.seek(0)
            verify_registry_members(source, remaining, name)


def verify_registry_members(source, remaining, name):
    observed = set()
    with tarfile.open(fileobj=source, mode="r|gz") as registry:
        for info in registry:
            # Some upstream tarballs use a package-specific first path component.
            _, _, relative = info.name.partition("/")
            if relative in remaining:
                require(relative not in observed and info.isreg(),
                        f"ambiguous registry member: {name}/{relative}")
                with registry.extractfile(info) as member:
                    require(hashlib.file_digest(member, "sha256").hexdigest() == remaining[relative],
                            f"registry member digest mismatch: {name}/{relative}")
                observed.add(relative)
    missing = remaining.keys() - observed
    require(not missing, f"missing registry members: {name}: {', '.join(sorted(missing))}")


def archive_mode(name):
    return 0o755 if name in EXECUTABLES else 0o644


def write_archive(raw, paths):
    with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for name, path in sorted(paths.items()):
                with regular_file(path) as (source, file_info):
                    info = tarfile.TarInfo(name)
                    info.size = file_info.st_size
                    info.mode = archive_mode(name)
                    archive.addfile(info, source)


def verify_archive(raw, closure):
    expected = closure["tools_files_sha256"]
    names = []
    raw.seek(0)
    with tarfile.open(fileobj=raw, mode="r|gz") as archive:
        for info in archive:
            name = info.name
            require(name in expected and info.isreg(), f"unexpected archive member: {name}")
            require((info.mode, info.uid, info.gid, info.mtime) == (archive_mode(name), 0, 0, 0),
                    f"archive member metadata differs: {name}")
            with archive.extractfile(info) as source:
                require(hashlib.file_digest(source, "sha256").hexdigest() == expected[name],
                        f"archive member digest mismatch: {name}")
            names.append(name)
    require(names == sorted(expected) and len(names) == closure["file_count"],
            "archive member order or inventory differs")
    raw.seek(0)
    digest = hashlib.file_digest(raw, "sha256").hexdigest()
    size = os.fstat(raw.fileno()).st_size
    require((digest, size) == (closure["archive_sha256"], closure["archive_bytes"]),
            f"archive encoding differs after matching all members: {size} bytes, sha256 {digest}")
    return digest, size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT,
                        help="checkout with the frozen pre-Cloud lock and its pinned npm ci")
    parser.add_argument("--npm-cache", required=True, type=Path, help="cache from the pinned npm ci")
    parser.add_argument("--node", required=True, type=Path, help="pinned Linux x64 Node executable")
    parser.add_argument("--schema-engine", required=True, type=Path, help="pinned Debian OpenSSL 3 engine")
    parser.add_argument("--output", required=True, type=Path, help="new archive path outside the checkout")
    args = parser.parse_args()
    output = args.output.absolute()
    try:
        source_root = args.source_root.resolve(strict=True)
        require(not any(output.resolve().is_relative_to(root) for root in (ROOT, source_root)),
                "archive destination is inside a checkout")
        require(not os.path.lexists(output), f"archive destination already exists: {output}")
        closure = pinned_json(RECORDS / "prisma-tools-closure.json", CLOSURE_SHA256)
        tooling = pinned_json(RECORDS / "linux-tooling-manifest.json", TOOLING_SHA256)
        lock = pinned_json(source_root / "package-lock.json", closure["root_package_lock_sha256"])["packages"]
        expected = closure["tools_files_sha256"]
        tools = {
            "node/bin/node": (args.node.absolute(), tooling["node_binary_sha256"]),
            "schema-engine": (args.schema_engine.absolute(), tooling["engine_binary_sha256"]),
        }
        paths = {name: source_root / name for name in expected if name not in EXECUTABLES}
        for name, (path, digest) in tools.items():
            with regular_file(path) as (source, _):
                require(hashlib.file_digest(source, "sha256").hexdigest() == digest == expected[name],
                        f"tool digest mismatch: {name}")
            paths[name] = path
        verify_registry_packages(closure, lock, args.npm_cache.absolute())
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".prisma-tools-") as archive:
            write_archive(archive, paths)
            archive.flush()
            digest, size = verify_archive(archive, closure)
            os.link(archive.name, output)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, f"Cloud Prisma tool archive refused: {error}\n")
    print(json.dumps({
        "archive": str(output),
        "archive_bytes": size,
        "archive_sha256": digest,
        "files_sha256_verified": len(expected),
        "registry_packages_integrity_verified": len(closure["packages"]),
    }))


if __name__ == "__main__":
    main()
