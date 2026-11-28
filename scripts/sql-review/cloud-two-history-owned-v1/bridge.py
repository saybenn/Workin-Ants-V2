"""Pure Cloud-specific dispatch construction for the closed two-history launcher.

Calls require a later owning controller's verified resource observation and
bounded transport. The bridge never opens a subprocess or a database itself.
"""

import ast
import json
import re

from sources import Held, module, require, sha, unique_json


HISTORICAL_COORDINATOR = "scripts/sql-review/run-local-f0-runtime-lease-history-v1.py"
NODE = "/run/wa-f0-tools/node/bin/node"
SOURCE = "/run/wa-f0-source"
LEGACY_RESULT = "workinants.local-f0-runtime-lease-history-migrate-result.v1"
CLOUD_RESULT = "workinants.cloud-f0-runtime-lease-history-migrate-result.v1"


def result_validator(root, blobs):
    """Reuse the reviewed receipt checks with a separately versioned schema."""
    name = HISTORICAL_COORDINATOR
    tree = ast.parse(blobs[name].decode("utf-8"), filename=name)
    names = {"unique_json", "safe_result", "runner_succeeded", "require", "HeldFailure"}
    constants = {"PRISMA_CODES", "DIAGNOSTIC_FLAGS"}
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            selected.append(node)
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants for target in node.targets
        ):
            selected.append(node)
    require(len(selected) == len(names) + len(constants), "RECEIPT_VALIDATOR_SOURCE_SHAPE")
    safe = next(n for n in selected if isinstance(n, ast.FunctionDef) and n.name == "safe_result")
    schema = [n for n in ast.walk(safe) if isinstance(n, ast.Constant) and n.value == LEGACY_RESULT]
    require(len(schema) == 1, "RECEIPT_VALIDATOR_SCHEMA_ORIGIN")
    schema[0].value = CLOUD_RESULT
    # No historical target/context validation or execution code is selected.
    rendered = ("import json, re\n" + ast.unparse(ast.Module(body=selected, type_ignores=[]))).encode()
    return module(root, name, rendered)


def copied_paths(inner, manifest, source8):
    require(set(source8) == {
        inner.SCHEMA, inner.HISTORY_MANIFEST, *inner.RUNTIME,
        f"{inner.HISTORY}/migration_lock.toml", *(row["path"] for row in inner.ORDERED),
    }, "CLOUD_SOURCE8_INVENTORY")
    require(all(sha(source8[name]) == digest for name, digest in manifest["source"]["runtime_files_sha256"].items()),
            "CLOUD_RUNTIME_SOURCE_DRIFT")
    require(all(sha(source8[row["path"]]) == row["sha256"] for row in inner.ORDERED),
            "CLOUD_MIGRATION_SOURCE_DRIFT")
    return {f"{SOURCE}/{name}": raw for name, raw in source8.items()}


def required_execs(inner, manifest, source8, observed, operation):
    """Return only the three immutable command requests in inspected scope."""
    raw = inner.attest(manifest, observed, operation)
    paths = copied_paths(inner, manifest, source8)
    cid = observed["container_id"]
    commands = [
        ("exec", cid, "/usr/bin/sha256sum", "--", *sorted([*paths, NODE])),
        ("exec", cid, "/usr/bin/stat", "--format=%s", "--", *sorted(paths)),
        ("exec", "-i", "--user", "0", cid, "/usr/bin/env", "-i", NODE,
         f"{SOURCE}/{inner.BASE}/runner.mjs", inner.OP_ARG, "--operation", operation),
    ]
    return commands, raw


def verify_source_copy(result, paths, node_pin):
    require(result.returncode == 0 and result.stderr == b"" and type(result.stdout) is bytes
            and len(result.stdout) <= 16384, "CLOUD_SOURCE_COPY_HASH_READ")
    actual = {}
    for line in result.stdout.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (/run/wa-f0-(?:source|tools)/[^\r\n]+)", line)
        require(match is not None and match[2] not in actual, "CLOUD_SOURCE_COPY_HASH_SHAPE")
        actual[match[2]] = match[1]
    require(actual == {**{name: sha(raw) for name, raw in paths.items()}, NODE: node_pin},
            "CLOUD_SOURCE_COPY_HASH_DRIFT")


def verify_source_lengths(result, paths):
    expected = "".join(f"{len(paths[name])}\n" for name in sorted(paths)).encode()
    require(result.returncode == 0 and result.stderr == b"" and result.stdout == expected, "CLOUD_SOURCE_COPY_LENGTHS")


def validate_receipt(result, validator, manifest, observed, operation, raw):
    require(result.returncode in (0, 1) and type(result.returncode) is int and result.stderr == b""
            and type(result.stdout) is bytes and 1 <= len(result.stdout) <= 65536, "CLOUD_RUNNER_RESPONSE")
    evidence = unique_json(result.stdout)
    require(evidence.get("schema") == CLOUD_RESULT
            and evidence.get("daemon_id") == observed["daemon"]["daemon_id"],
            "CLOUD_RUNNER_DAEMON_RECEIPT")
    receipt_fields = {name: value for name, value in evidence.items() if name != "daemon_id"}
    # These remain the Cloud schema and exact original result fields. The
    # daemon field has already been checked against the live Cloud observation.
    validator.safe_result(json.dumps(receipt_fields), manifest, observed, operation)
    require(evidence["attestation_sha256"] == sha(raw), "CLOUD_RUNNER_ATTESTATION_RECEIPT")
    require(result.returncode == (0 if validator.runner_succeeded(evidence) else 1), "CLOUD_RUNNER_OUTER_EXIT")
    return evidence


def migrate(inner, validator, manifest, source8, observed, operation, *, process, latch_unknown, post_source_check):
    commands, raw = required_execs(inner, manifest, source8, observed, operation)
    paths = copied_paths(inner, manifest, source8)
    verify_source_copy(process(commands[0], None, 30), paths, manifest["tools"]["files_sha256"]["node/bin/node"])
    verify_source_lengths(process(commands[1], None, 30), paths)
    try:
        evidence = validate_receipt(
            process(commands[2], raw, 150), validator, manifest, observed, operation, raw
        )
        if evidence["status"] == "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE":
            raise Held("REPORTED_INNER_CLI_CLOSURE_UNCONFIRMED")
        post_source_check()
        return evidence
    except BaseException:
        # A closed Docker CLI is not a substitute for a validated and closed
        # inner Node/Prisma result. Once dispatched, uncertainty stays latched.
        latch_unknown()
        raise
