"""Closed source and capability bindings for the mounted-storage-only TWO controller."""

import hashlib
import os
from pathlib import Path
import re
import stat
import sys
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.relative_to(ROOT).as_posix()
V1 = "scripts/sql-review/cloud-two-history-owned-v1"
INNER = "scripts/sql-review/cloud-runtime-lease-history-v2"
PROBE = "scripts/sql-review/cloud-f0-v1"
CAPABILITY = "context/reconciliation/cloud-phase0-evidence/2026-11-27/probe-862971a5"
CAPABILITY_FILES = ("manifest.json", "review.json", "result.json", "independent-closure.json",
                    "created-container.json", "created-volume.json")
PINNED_V1 = {
    "sources": "9651ed26b7d5a1b72bb6bd7c609ddb43a95fc1599b59745f78a30f5e4acff43a",
    "bridge": "db3381ae85e2897ce33a7ae0794f5674b1cd1c916be901f5892385b9f790283a",
    "packet": "2a6f67184eb9bc877ad76f72d9adcb1e74ab8252183fdf5f1a0c0de7e297e0c1",
}
PROBE_PINS = {
    f"{PROBE}/probe.py": "3ffb812b29c643ce119e209a79e8b55ea011d34e3c112e4c58563a92651a1a85",
    f"{PROBE}/guard.py": "00c3b91295db01c2f692f97c2f4ff4484ac4bc27733bc1229d577436aa927d2b",
    f"{PROBE}/profile.json": "55d94434981828b49f03983c050bea0b6d9df7af51f68ad4fb3e079c49ea7c97",
}


def fixed_source(relative, digest):
    path = ROOT / relative
    path_info = path.lstat()
    if path.resolve(strict=True) != path or not stat.S_ISREG(path_info.st_mode):
        raise ValueError("FIXED_SOURCE_PATH")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(1024 * 1024 + 1)
    if (not len(raw) <= 1024 * 1024 or opened.st_nlink != 1 or
            hashlib.sha256(raw).hexdigest() != digest):
        raise ValueError("FIXED_SOURCE_SHA")
    return raw


def v1_helpers():
    """Compile only SHA-confirmed v1 modules for their pure helpers."""
    imported = {}
    try:
        for name, digest in PINNED_V1.items():
            if name in sys.modules:
                raise ValueError("FIXED_SOURCE_MODULE_COLLISION")
            relative = f"{V1}/{name}.py"
            loaded = ModuleType(name)
            loaded.__file__ = str(ROOT / relative)
            imported[name] = loaded
            sys.modules[name] = loaded
            exec(compile(fixed_source(relative, digest), loaded.__file__, "exec"), loaded.__dict__)
    finally:
        for name in imported:
            del sys.modules[name]
    return imported["sources"], imported["packet"], imported["bridge"]


S, P, B = v1_helpers()


def capture(root=ROOT):
    blobs, reviews = S.capture(root)
    names = [
        *PROBE_PINS, f"{INNER}/prepare.py", f"{INNER}/kernel-guard.mjs.txt",
        *(f"{CAPABILITY}/{name}" for name in CAPABILITY_FILES),
        *(f"{BASE}/{name}" for name in ("basis.py", "plan.py", "operation.py", "test_operation.py", "README.md")),
    ]
    for name in names:
        blobs[name] = S.read(root / name)
    S.require(all(S.sha(blobs[name]) == digest for name, digest in PROBE_PINS.items()),
              "ACTUAL_PROBE_SOURCE_DRIFT")
    return blobs, reviews


def capability(blobs):
    raw = lambda name: blobs[f"{CAPABILITY}/{name}"]
    manifest, result, review, audit, container, volume = (
        S.unique_json(raw(name)) for name in ("manifest.json", "result.json", "review.json",
                                               "independent-closure.json", "created-container.json",
                                               "created-volume.json")
    )
    S.require(
        manifest["purpose"] == "CLOUD_F0_CAPABILITY_PROBE_ONLY"
        and manifest["candidate_migrations"] is False
        and manifest["source"]["commit"] == "fc5b5879abb5bd764fc0e5f5c1a03f95e2b0b7c8"
        and all(manifest["source"]["files_sha256"][name] == digest for name, digest in PROBE_PINS.items())
        and manifest["run_id"] == result["run_id"] == audit["run_id"]
        and manifest["daemon"] == result["daemon"] == audit["daemon"]
        and manifest["cached_image"] == result["image"] == audit["image"]
        and manifest["target"] == result["target"] == audit["target"]
        and manifest["source"] == result["source"] == audit["source"],
        "CAPABILITY_SOURCE_AND_RESOURCE_IDENTITY",
    )
    S.require(
        result["status"] == audit["result_status"] == "PASS_CAPABILITY_SUBSET_ONLY"
        and result["completed_capability_checks"] is True and result["remote_outcome_unconfirmed"] is False
        and result["assertion_promotions"] == audit["assertion_promotions"] == 0
        and "bootstrap_only_through_owned_container_tmpfs" in result["checks"]
        and result["checks"] == audit["runner_checks_observed"]
        and result["cleanup"] == "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
        and audit["decision"] == "EXACT_CLEANUP_AND_SYNTHETIC_CAPABILITY_SUBSET_SUPPORTED"
        and audit["same_live_daemon_socket_and_binary_verified"] is True
        and audit["pinned_image_retained"] is True
        and audit["absent_after"] == dict.fromkeys(("container_id", "container_name", "volume_name",
                                                   "private_host_path"), True)
        and container == audit["created_container"] and volume == audit["created_volume"]
        and result["container_id"] == container["id"] and result["volume_created_at"] == volume["created_at"],
        "ACTUAL_CAPABILITY_AND_INDEPENDENT_CLOSURE_REQUIRED",
    )
    S.require(
        review["decision"] == "APPROVE" and review["reviewer"] == result["reviewer"]
        and review["manifest_sha256"] == result["manifest_sha256"] == S.sha(raw("manifest.json"))
        and result["review_sha256"] == S.sha(raw("review.json"))
        and all(S.sha(raw(name)) == audit["file_sha256"][name] for name in CAPABILITY_FILES
                if name != "independent-closure.json"),
        "CAPABILITY_APPROVAL_AND_RECEIPT_HASHES",
    )
    return manifest, result, audit


def exact_shadow_modules(root, blobs):
    """Load the actual verified Linux probe under a private import name."""
    S.require("guard" not in sys.modules, "GUARD_IMPORT_COLLISION")
    guard = S.module(root, f"{PROBE}/guard.py", blobs[f"{PROBE}/guard.py"])
    sys.modules["guard"] = guard
    try:
        probe = S.module(root, f"{PROBE}/probe.py", blobs[f"{PROBE}/probe.py"])
    finally:
        del sys.modules["guard"]
    return guard, probe


def safe_code(error):
    for value in (getattr(error, "code", None), str(error)):
        if type(value) is str and re.fullmatch(r"[A-Z0-9_]{1,100}", value):
            return value
    return "CLOUD_TWO_OPERATION_UNCONFIRMED"
