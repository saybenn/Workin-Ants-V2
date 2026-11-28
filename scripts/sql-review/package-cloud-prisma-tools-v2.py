"""Reproduce the Cloud F0 Prisma tools archive with exact Effect 3.22.1 bytes."""

import argparse
import hashlib
import json
import os
import runpy
import tarfile
import tempfile
from pathlib import Path

V1 = runpy.run_path(str(Path(__file__).with_name("package-cloud-prisma-tools-v1.py")))
RECORDS = V1["RECORDS"]
CLOSURE_SHA256 = "81377e308966e93cb98f45d2d5482fd9d5ea7a6188895c6a882a3eedbc9de76c"
EFFECT = "node_modules/effect"
pinned_json = V1["pinned_json"]
require = V1["require"]


def map_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def verify_successor(closure, frozen, lock):
    require(closure["schema"] == "workinants.cloud-f0-prisma-tools-v2"
            and closure["platform"] == "linux/amd64", "unexpected Cloud tool profile")
    require(closure["base_archive_sha256"] == frozen["archive_sha256"]
            and closure["base_archive_bytes"] == frozen["archive_bytes"]
            and closure["base_file_count"] == frozen["file_count"]
            and closure["base_closure_sha256"] == V1["CLOSURE_SHA256"]
            and closure["base_tooling_manifest_sha256"] == V1["TOOLING_SHA256"],
            "frozen archive binding differs")
    for key in ("node_version", "prisma_version", "engine_commit",
                "excluded_windows_binaries", "missing_optional_or_platform_dependencies"):
        require(closure[key] == frozen[key], f"unreviewed tool property change: {key}")

    old_packages = {row["path"]: row for row in frozen["packages"]}
    packages = {row["path"]: row for row in closure["packages"]}
    require(packages.keys() == old_packages.keys()
            and len(packages) == len(closure["packages"]), "registry package inventory differs")
    require({path for path in packages if packages[path] != old_packages[path]} == {EFFECT},
            "registry package changes exceed Effect")
    delta = closure["delta"]
    dependency = delta["registry_package"]
    require(dependency["path"] == EFFECT
            and dependency["before_version"] == old_packages[EFFECT]["version"] == "3.20.0"
            and dependency["after_version"] == packages[EFFECT]["version"] == "3.22.1"
            and dependency["exact_runtime_dependencies"] == lock[EFFECT]["dependencies"],
            "Effect package identity or dependency graph differs")

    before = frozen["tools_files_sha256"]
    expected = closure["tools_files_sha256"]
    sizes = closure["tools_file_sizes"]
    require(before.keys() == expected.keys() == sizes.keys()
            and len(expected) == closure["file_count"], "member inventory differs")
    require(all(type(value) is int and value >= 0 for value in sizes.values()),
            "invalid archive member size")
    changed = sorted(name for name in expected if expected[name] != before[name])
    require(changed and all(name.startswith(EFFECT + "/") for name in changed),
            "archive changes exceed Effect package bytes")
    require(delta["file_changes"] == {"added": 0, "modified": len(changed), "removed": 0}
            and delta["file_changes_path_map_sha256"] == map_sha256({
                "added": [], "modified": changed, "removed": [],
            }), "archive path delta differs")
    require(closure["tools_files_sha256_map_sha256"] == map_sha256(expected)
            and closure["tools_file_sizes_map_sha256"] == map_sha256(sizes),
            "archive member map digests differ")


def verify_sizes(raw, sizes):
    raw.seek(0)
    with tarfile.open(fileobj=raw, mode="r|gz") as archive:
        require({info.name: info.size for info in archive} == sizes,
                "archive member size map differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True,
                        help="checkout with the exact successor lock and its pinned npm ci")
    parser.add_argument("--npm-cache", type=Path, required=True,
                        help="cache used by the pinned npm ci")
    parser.add_argument("--node", type=Path, required=True,
                        help="pinned Linux x64 Node executable")
    parser.add_argument("--output", type=Path, required=True,
                        help="new archive path outside both checkouts")
    args = parser.parse_args()
    try:
        source = args.source_root.resolve(strict=True)
        output = args.output.absolute()
        destination = output.resolve()
        require(not (destination.is_relative_to(source) or destination.is_relative_to(V1["ROOT"])),
                "archive destination is inside a checkout")
        require(not os.path.lexists(output), f"archive destination already exists: {output}")

        frozen = pinned_json(RECORDS / "prisma-tools-closure.json", V1["CLOSURE_SHA256"])
        tooling = pinned_json(RECORDS / "linux-tooling-manifest.json", V1["TOOLING_SHA256"])
        closure = pinned_json(RECORDS / "cloud-v2/prisma-tools-closure.json", CLOSURE_SHA256)
        pinned_json(source / "package.json", closure["root_package_json_sha256"])
        lock = pinned_json(source / "package-lock.json", closure["root_package_lock_sha256"])["packages"]
        verify_successor(closure, frozen, lock)
        V1["verify_registry_packages"](closure, lock, args.npm_cache.absolute())

        expected = closure["tools_files_sha256"]
        paths = {name: source / name for name in expected if name not in V1["EXECUTABLES"]}
        paths["node/bin/node"] = args.node.absolute()
        paths["schema-engine"] = source / "node_modules/@prisma/engines/schema-engine-debian-openssl-3.0.x"
        for name, key in (("node/bin/node", "node_binary_sha256"),
                          ("schema-engine", "engine_binary_sha256")):
            with V1["regular_file"](paths[name]) as (binary, _):
                digest = hashlib.file_digest(binary, "sha256").hexdigest()
                require(digest == tooling[key] == expected[name], f"tool digest mismatch: {name}")

        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".prisma-tools-cloud-v2-") as archive:
            V1["write_archive"](archive, paths)
            archive.flush()
            digest, size = V1["verify_archive"](archive, closure)
            verify_sizes(archive, closure["tools_file_sizes"])
            os.link(archive.name, output)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, f"Cloud F0 Prisma tools v2 refused: {error}\n")

    print(json.dumps({
        "archive": str(output),
        "archive_sha256": digest,
        "archive_bytes": size,
        "closure_sha256": CLOSURE_SHA256,
        "files_sha256_and_size_verified": len(expected),
        "registry_packages_integrity_verified": len(closure["packages"]),
    }))


if __name__ == "__main__":
    main()
