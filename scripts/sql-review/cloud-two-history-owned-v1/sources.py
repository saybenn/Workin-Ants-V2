"""Closed sources and immutable historical review provenance for Cloud TWO."""

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.relative_to(ROOT).as_posix()
ARCHIVE = "context/reconciliation/local-f0-operation-sources/runtime-lease-two-history-owned-v1"
VALIDATION = "context/reconciliation/local-f0-runtime-lease-two-history-owned-v1-source-validation.json"
AUTHORITY = "context/reconciliation/directives/cloud-phase0-standing-authority-2026-11-27.md"
PRIMITIVE = ARCHIVE + "/primitive11/lease88_independent_closed_actual_audit_20261123.json"
OPERATOR = ARCHIVE + "/execute_local_f0_runtime_lease_two_history_owned_v1_20261123.py.txt"
STEPS = ARCHIVE + "/local_f0_runtime_lease_two_history_owned_v1_operation_steps.py.txt"
NATIVE = "scripts/prepare-native-runtime-lease-history-v1-review.py"
NATIVE_REVIEW = "review-output/native-runtime-lease-history-v1"
HOST_PREFIX = "scripts/sql-review/cloud-f0-v1"
INNER_PREFIX = "scripts/sql-review/cloud-runtime-lease-history-v1"
TOOL_CLOSURE = "context/reconciliation/local-f0-tooling/cloud-v2/prisma-tools-closure.json"
EXPECTED = "cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4"
HISTORICAL_PINS = {
    VALIDATION: "fef3049671dc7770c9768d70d4152c2d152ae307cb91ebbef0bae4ac86bd3b30",
    ARCHIVE + "/source-inputs.json": "284c0491484b7b1268a85f1628b2403da8a2fb61ce11236ecc63dbf04dd6b838",
    AUTHORITY: "6b7904c37ebab7867f30c00e1a556c387fd3fc63115a86955594ff8dc07b56c4",
    PRIMITIVE: "76b2911680a7eeb1a61c809981caedfedc36759386d7d15b40fdff739ccc3013",
    OPERATOR: "c473c555d0d25056252e8a4d0bf5f7bb4f8adda56b455589853ef361c1ad10ad",
    STEPS: "f7505b51fd207a0e8c07d9bc7cc2a3887c3719773096b0caad97770453fe0f44",
}
HOST_FILES = (
    f"{HOST_PREFIX}/guard.py", f"{HOST_PREFIX}/profile.json",
    f"{INNER_PREFIX}/prepare.py", f"{INNER_PREFIX}/guard-platform.mjs.txt",
    f"{BASE}/sources.py", f"{BASE}/packet.py", f"{BASE}/bridge.py", f"{BASE}/test_packet.py",
    f"{BASE}/README.md",
    TOOL_CLOSURE,
)
HASH = re.compile("[0-9a-f]{64}")
HEX40 = re.compile("[0-9a-f]{40}")


class Held(RuntimeError):
    """An allowlisted, source-stage refusal."""


def require(value, code):
    if not value:
        raise Held(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def unique_json(raw, *, historical=False):
    def pairs(entries):
        out = dict(entries)
        require(len(out) == len(entries), "DUPLICATE_JSON")
        return out

    def reject_number(_):
        raise Held("JSON_NUMBER")

    def check(value, depth=0):
        require(depth <= 48, "JSON_DEPTH")
        if type(value) is dict:
            for child in value.values():
                check(child, depth + 1)
        elif type(value) is list:
            for child in value:
                check(child, depth + 1)
        else:
            require(value is None or type(value) in (str, int, bool), "JSON_TYPE")

    require(type(raw) is bytes and 0 < len(raw) <= 16 * 1024 * 1024, "JSON_SIZE")
    try:
        options = {"object_pairs_hook": pairs, "parse_constant": reject_number}
        if not historical:
            options["parse_float"] = reject_number
        value = json.loads(raw.decode("utf-8"), **options)
        if not historical:
            check(value)
        return value
    except (UnicodeError, RecursionError, ValueError):
        raise Held("JSON_INVALID") from None


def valid_name(name):
    return type(name) is str and not any(c in name for c in (":", "\\", "\n", "\r", "\0")) and all(
        part not in ("", ".", "..") for part in name.split("/")
    )


def identity(st):
    return st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def absolute(path):
    require(path.is_absolute() and path.resolve(strict=True) == path, "PATH_ALIAS")
    return path


def read(path, cap=16 * 1024 * 1024):
    path = absolute(Path(path))
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= cap,
            "SOURCE_FILE_SHAPE")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        opened = os.fstat(stream.fileno())
        require(identity(before) == identity(opened), "SOURCE_FILE_OPEN_DRIFT")
        raw = stream.read(cap + 1)
        finished = os.fstat(stream.fileno())
    require(identity(finished) == identity(before) == identity(path.lstat())
            and len(raw) == before.st_size, "SOURCE_FILE_DRIFT")
    return raw


def pinned(root, name, pin):
    require(valid_name(name) and type(pin) is str and HASH.fullmatch(pin), "SOURCE_PIN_SHAPE")
    raw = read(root / name)
    require(sha(raw) == pin, "SOURCE_FILE_PIN")
    return raw


def aggregate(pins):
    return sha("".join(f"{name}\0{digest}\n" for name, digest in sorted(pins.items())).encode())


def historical_sources(root):
    """Verify all historical bytes. Read only the reviewed receipt's typed projection."""
    validation = unique_json(pinned(root, VALIDATION, HISTORICAL_PINS[VALIDATION]))
    registry = unique_json(pinned(root, ARCHIVE + "/source-inputs.json", HISTORICAL_PINS[ARCHIVE + "/source-inputs.json"]))
    closed = validation["archive_files_sha256"]
    found = {path.relative_to(root).as_posix() for path in (root / ARCHIVE).rglob("*") if path.is_file()}
    require(set(closed) == found and len(closed) == 65, "HISTORICAL_ARCHIVE_CLOSURE")
    pins = {**closed, **registry["files_sha256"], VALIDATION: HISTORICAL_PINS[VALIDATION]}
    require(len(pins) == 435 and all(pins[name] == digest for name, digest in closed.items()),
            "HISTORICAL_SOURCE_CLOSURE")
    blobs = {name: pinned(root, name, digest) for name, digest in pins.items()}
    operator_pins = validation["operator_sources_sha256"]
    source_pins = validation["source_files_sha256"]
    require(len(operator_pins) == 5 and len(source_pins) == 374 and all(
        sha(blobs[f"{ARCHIVE}/{name}.txt"]) == digest for name, digest in operator_pins.items()
    ) and all(pins.get(name) == digest for name, digest in source_pins.items()),
            "HISTORICAL_REVIEWED_RUNTIME_CLOSURE")
    require(all(sha(blobs[name]) == HISTORICAL_PINS[name] for name in (OPERATOR, STEPS, PRIMITIVE)),
            "HISTORICAL_REVIEW_ORIGIN")
    approvals = ("SafetySQL_review", "binary_transport_review", "independent_source_review",
                 "resource_review", "source_gate_and_pinner_review")
    projections = {}
    for review_name in ("independent_source_review", "Root_source_review", "Root_admission"):
        ref = validation[review_name]
        raw = blobs[ref["path"]]
        require(sha(raw) == ref["sha256"], "HISTORICAL_REVIEW_PIN")
        review = unique_json(raw, historical=review_name == "independent_source_review")
        require(review["decision"] == "SOURCE_APPROVED" and review["operator_sources_sha256"] == operator_pins
                and review["Posture"] == "D", "HISTORICAL_REVIEW_SCOPE")
        if review_name == "independent_source_review":
            require(review["independent_of_source_author"] is True and review["findings"] == []
                    and review["runtime"] == "NOT_RUN"
                    and set(review["decisions"]) == set(approvals) | {"Root_source_admission", "runtime_authorization"}
                    and all(review["decisions"][gate] == "SOURCE_APPROVED" for gate in approvals)
                    and review["decisions"]["runtime_authorization"] is False
                    and review["current_closure_maps"]["closed_runtime_sources_sha256"] == source_pins,
                    "HISTORICAL_INDEPENDENT_REVIEW_SCOPE")
        else:
            require(review["source_files_sha256"] == source_pins and review["assertion_promotions"] == 0
                    and review["runtime"] in ("NOT_RUN", "NOT_RUN_SOURCE_ADMISSION_ONLY"),
                    "HISTORICAL_ROOT_REVIEW_SCOPE")
        projections[review_name] = ref["sha256"]
    primitive = unique_json(blobs[PRIMITIVE], historical=True)
    require(primitive["decision"] == "ACTUAL_SYNTHETIC_MECHANISM_SUBSET_SUPPORTED"
            and primitive["findings"] == [], "HISTORICAL_PRIMITIVE_UNPROVED")
    return blobs, projections


def capture(root=ROOT):
    original, refs = historical_sources(root)
    sources = {**original, **{name: read(root / name) for name in HOST_FILES}}
    sources[AUTHORITY] = pinned(root, AUTHORITY, HISTORICAL_PINS[AUTHORITY])
    return sources, refs


def git(root, *args, payload=None):
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1"}
    result = subprocess.run(["git", "-C", str(root), *args], input=payload or b"",
                            capture_output=True, env=env, timeout=35, check=False)
    require(result.returncode == 0 and result.stderr == b"", "GIT_SOURCE_READ_FAILED")
    return result.stdout


def verify_committed(root, blobs, *, expected=None):
    commit = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    require(HEX40.fullmatch(commit), "COMMIT_IDENTITY")
    tree = git(root, "rev-parse", "--verify", f"{commit}^{{tree}}").decode().strip()
    require(HEX40.fullmatch(tree) and (expected is None or expected == {"commit": commit, "tree": tree}),
            "TREE_IDENTITY")
    request = "".join(f"{commit}:{name}\n" for name in sorted(blobs)).encode()
    require(len(request) <= 256 * 1024 and sum(map(len, blobs.values())) <= 64 * 1024 * 1024,
            "GIT_BATCH_SIZE")
    actual = git(root, "cat-file", "--batch", payload=request)
    pos = 0
    for name in sorted(blobs):
        body = blobs[name]
        size = str(len(body)).encode()
        oid = hashlib.sha1(b"blob " + size + b"\0" + body).hexdigest().encode()
        item = oid + b" blob " + size + b"\n"
        require(actual[pos:pos + len(item)] == item, "GIT_BATCH_HEADER")
        pos += len(item)
        require(actual[pos:pos + len(body) + 1] == body + b"\n", "GIT_COMMITTED_BYTE_DRIFT")
        pos += len(body) + 1
    require(pos == len(actual) and git(root, "rev-parse", "--verify", "HEAD").strip() == commit.encode(),
            "HEAD_CHANGED_OR_TRAILING_GIT_BYTES")
    return {"commit": commit, "tree": tree}


def module(root, name, raw):
    key = "_cloud_two_" + Path(name).stem.replace("-", "_")
    require(key not in sys.modules, "MODULE_CACHE_COLLISION")
    loaded = ModuleType(key)
    loaded.__file__ = str(root / name)
    # Dataclasses in the historical transport resolve their module here.
    sys.modules[key] = loaded
    try:
        exec(compile(raw, loaded.__file__, "exec", dont_inherit=True), loaded.__dict__)
    finally:
        del sys.modules[key]
    return loaded


def reproduce_native(root, blobs):
    parser = sys.modules.get("pglast")
    require(parser is None or parser.__version__ == "v7.21", "PINNED_PARSER_REQUIRED")
    compiler = module(root, NATIVE, blobs[NATIVE])
    pins = unique_json(blobs[f"{NATIVE_REVIEW}/source-pins.json"])
    require(pins == {name: sha(blobs[name]) for name in compiler.REQUIRED_FILES} and len(pins) == 36,
            "NATIVE_COMPILER_GRAPH")
    files, summary = compiler.prepare(root, pins)
    require(summary["source_expected_sha256"] == EXPECTED and summary["expression_count"] == 416
            and len(files) == 6, "NATIVE_EXPECTATION_SCOPE")
    for name, raw in files.items():
        require(raw == blobs[f"{NATIVE_REVIEW}/{name}"], "NATIVE_ASSET_REPRODUCTION")
    return {name: sha(raw) for name, raw in sorted(files.items())}
