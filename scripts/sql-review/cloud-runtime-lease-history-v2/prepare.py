"""Build the held Cloud source8 packet for the proven stdin-to-tmpfs profile."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "scripts/sql-review/cloud-runtime-lease-history-v2"
PARENT = "scripts/sql-review/cloud-runtime-lease-history-v1"
PARENT_PIN = {
    f"{PARENT}/prepare.py": "6b9717e061a556be93bcb5cf5f7c9685e1ec8e60d3a5d281f36801043d1efe45",
    f"{PARENT}/guard-platform.mjs.txt": "839112338962212e6903348d471f524d67e2980615ac1816862efb1c8b06bd5b",
}
RUNTIME = tuple(f"{BASE}/{name}" for name in ("config.mjs", "guard.mjs", "runner.mjs"))
RUN_SCHEMA = "workinants.cloud-f0-runtime-lease-history-run.v2"
HISTORY_SCHEMA = "workinants.cloud-f0-runtime-lease-history.v2"
ATTESTATION_SCHEMA = "workinants.cloud-f0-runtime-lease-history-live-attestation.v2"
RESULT_SCHEMA = "workinants.cloud-f0-runtime-lease-history-migrate-result.v2"
REFUSAL_SCHEMA = "workinants.cloud-f0-runtime-lease-history-refusal.v2"
OP_ARG = "--execute-reviewed-cloud-f0-runtime-lease-history-v2"
LABEL = "p0c-cloud-f0-two-history-v2"
BOOTSTRAP = {
    "transport": "exact_container_stdin_to_private_tmpfs",
    "container_path": "/run/wa-secrets/bootstrap-password",
    "tmpfs_options": "rw,nosuid,nodev,noexec,mode=0700,size=8m",
    "startup_gate_sha256": "2cbfda9bca8a7f2f4970eb49cbec3270dfc12310adfec5ef5dd6c4870a96793b",
    "write_gate_sha256": "7402460740b59686578fd8389a713fd5ce237c07452d64d8a2b017fbabcd37da",
}
MOUNT_DESTINATIONS = ("/run/wa-secrets", "/var/lib/postgresql/data")
AUTHORIZATION_FIELDS = ("packet_sha256", "literal_review_sha256")
JSON_CODES = (
    "DUPLICATE_JSON", "JSON_ARRAY", "JSON_BOUNDS", "JSON_ENCODING", "JSON_OBJECT",
    "JSON_SIZE_ENCODING", "JSON_STRING", "JSON_TRAILING", "JSON_VALUE", "NONFINITE_JSON",
)
MOUNT_CODES = (
    "BOOTSTRAP_ABSENCE_UNCONFIRMED", "BOOTSTRAP_CREDENTIAL_RETAINED", "DATA_VOLUME_NOT_WRITABLE",
    "EXACT_RUNTIME_MOUNTS", "PRIVATE_DIRECTORY_OWNER_MODE", "PRIVATE_TMPFS_FLAGS_OR_SIZE",
    "UNDECLARED_BOOTSTRAP_OR_DATA_MOUNT",
)
FILE_CODES = (
    "FILE_IDENTITY_CHANGED", "FILE_OVERSIZED_READ", "FILE_OWNER_MODE_SIZE", "FILE_SHORT_READ",
    "FILE_UNAVAILABLE", "NONCANONICAL_FILE",
)
ATTESTATION_CODES = (
    "ATTESTATION_FIELDS", "AUTHORIZATION_FIELDS", "CLOUD_ATTESTATION_SCHEMA_OPERATION",
    "CLOUD_DAEMON_IDENTITY", "CLOUD_ENDPOINT_AND_DAEMON", "CLOUD_RUN_MANIFEST",
    "CLOUD_SOCKET_IDENTITY", "CLOUD_TARGET", "DAEMON_FIELDS", "EXACT_AUTHORIZATION_DIGESTS",
    "EXACT_BOOTSTRAP_TRANSPORT", "EXACT_RUN_LABELS", "EXACT_RUNTIME3",
    "EXACT_TOOL_ARCHIVE_INVENTORY", "EXACT_TWO_HISTORY_REQUIRED", "EXACT_TWO_SOURCE_PINS",
    "HISTORY_FIELDS", "LABEL_FIELDS", "LIVE_BOOTSTRAP_REMOVED_AND_MOUNTS", "LIVE_PRIVATE_TARGET",
    "LIVE_RESOURCE_IDENTITY", "LIVE_RUN_LABELS", "OBSERVATION_FIELDS", "PINNED_TOOLS",
    "RUNTIME_HASH_FIELDS", "RUN_FIELDS", "RUN_MANIFEST_HASH_MISMATCH", "SOCKET_FIELDS",
    "SOURCE_FIELDS", "TARGET_FIELDS", "TOOLS_FIELDS", "TOOL_MAP_SHAPE", "UUID4_RUN_REQUIRED",
)
CLOSED_REFUSAL_PHASE_CODES = {
    phase: tuple(sorted(set(codes) | {"UNLISTED_GUARD_CODE"}))
    for phase, codes in {
        "ARGUMENTS": ("EXPLICIT_EXECUTION_REQUIRED",),
        "INPUT": ("ATTESTATION_SIZE",),
        "ATTESTATION": JSON_CODES + ATTESTATION_CODES + ("ATTESTED_OPERATION",),
        "PRIVATE_STORE": JSON_CODES + ATTESTATION_CODES + MOUNT_CODES + FILE_CODES + (
            "ATTESTATION_CROSS_RUN_DENIED", "ATTESTATION_SIZE",
        ),
        "LOCAL_GUARD": JSON_CODES + ATTESTATION_CODES + MOUNT_CODES + FILE_CODES + (
            "CONTAINER_HOSTNAME", "CONTAINER_LOOPBACK_ONLY", "EXACT_NEW_HISTORY_PROVENANCE",
            "EXACT_ORDERED_TWO_HISTORY", "EXACT_PROVIDER_LOCK", "EXACT_SEVEN_DECLARED_SOURCES",
            "EXACT_SOURCE8_CLOSURE", "EXACT_TOOL_CLOSURE_REQUIRED", "HISTORY_RUN_IDENTITY",
            "INVALID_LOCAL_CONFIGURATION", "LINUX_PINNED_NODE_REQUIRED", "LOOPBACK_ONLY",
            "MIGRATOR_DATABASE_ONLY", "NEW_HISTORY_FIELDS", "OPERATION_DENIED", "PRISMA_VERSION",
            "PRIVATE_LEDGER_SCHEMA", "PRIVATE_URL_SHAPE", "RELATIVE_PATH", "REVIEWED_RUNTIME_SQL_SCHEMA",
            "SOURCE_FILE_DRIFT", "TOOL_EXACT_SIZE_REQUIRED", "TOOL_FILE_DRIFT", "TOOL_FILE_MAP",
            "TOOL_SIZE_BOUND", "TREE_OWNER_MODE", "TREE_REGULAR_FILES_ONLY", "TREE_SINGLE_LINK_ONLY",
            "UNLISTED_HISTORY_DENIED", "URL_OPTIONS_DENIED", "VETTED_EFFECT_VERSION",
        ),
        "DISPATCH": (),
        "RESULT": (),
    }.items()
}
REFUSAL_CAUSE_CODES = {
    "IO": "LOCAL_IO_ERROR",
    "TYPE": "LOCAL_INPUT_TYPE_ERROR",
    "SYNTAX": "LOCAL_SYNTAX_ERROR",
    "RANGE": "LOCAL_INPUT_RANGE_ERROR",
    "OTHER": "INVALID_LOCAL_INPUT_OR_IO",
}


def load_parent(root):
    sources = {}
    for relative, digest in PARENT_PIN.items():
        file = root / relative
        if file.resolve(strict=True) != file:
            raise ValueError("PARENT_COMPILER_PATH_ALIAS")
        raw = file.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("PARENT_COMPILER_DRIFT")
        sources[relative] = raw
    module = ModuleType("_pinned_cloud_runtime_lease_history_v1")
    relative = f"{PARENT}/prepare.py"
    module.__file__ = str(root / relative)
    exec(compile(sources[relative], module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


v1 = load_parent(ROOT)
(
    SCRATCH, ENDPOINT, IMAGE, IMAGE_IDS, SCHEMA, SCHEMA_SHA, HISTORY,
    HISTORY_MANIFEST, EFFECTIVE, INITIAL, APPEND, ORDERED, PURPOSE,
    CLOSURE_PATH, TOOL_TAR_SHA, TOOL_TAR_SIZE,
) = (
    v1.SCRATCH, v1.ENDPOINT, v1.IMAGE, v1.IMAGE_IDS, v1.SCHEMA, v1.SCHEMA_SHA, v1.HISTORY,
    v1.HISTORY_MANIFEST, v1.EFFECTIVE, v1.INITIAL, v1.APPEND, v1.ORDERED, v1.PURPOSE,
    v1.CLOSURE_PATH, v1.TOOL_TAR_SHA, v1.TOOL_TAR_SIZE,
)
Held = v1.Held
require = v1.require
encoded = v1.encoded
canonical = v1.canonical
sha = v1.sha
strict_json = v1.strict_json
read = v1.read
exact_daemon = v1.exact_daemon
inspect_tools = v1.inspect_tools
archive_source = v1.archive_source


def patch_platform(root, guard):
    """Render the independently versioned no-host-bind kernel helpers."""
    kernel = v1.read(root / BASE / "kernel-guard.mjs.txt").decode()
    return v1.section(guard, "export function privateMounts(raw) {", "function sameStat(",
                      "const BOOTSTRAP = " + canonical(BOOTSTRAP).decode() + ";\n"
                      "const MOUNT_DESTINATIONS = " + canonical(MOUNT_DESTINATIONS).decode() + ";\n"
                      + kernel + "\n\n")


def with_refusal_receipt(root, runner):
    replace, section = v1.replace, v1.section
    helper = read(root / BASE / "refusal.mjs.txt").decode()
    definitions = (
        f"const REFUSAL_SCHEMA = {json.dumps(REFUSAL_SCHEMA)};\n"
        f"const CLOSED_REFUSAL_PHASE_CODES = {canonical(CLOSED_REFUSAL_PHASE_CODES).decode()};\n"
        f"const REFUSAL_CAUSE_CODES = {canonical(REFUSAL_CAUSE_CODES).decode()};\n"
    )
    runner = replace(runner, "export function main(", definitions + helper + "\nexport function main(")
    for prior, current in (
        ("  try {\n    requireLocal(argv.length",
         '  const state = {phase: "ARGUMENTS", operation: null, inputSha: null, attested: {}};\n'
         "  try {\n    requireLocal(argv.length"),
        ("    const raw = (dependencies.readStdin || readAttestationStdin)();",
         '    state.operation = argv[2];\n    state.phase = "INPUT";\n'
         "    const raw = (dependencies.readStdin || readAttestationStdin)();\n"
         '    requireLocal(Buffer.isBuffer(raw) && raw.length > 0 && raw.length <= 4 * 1024 * 1024, "ATTESTATION_SIZE");\n'
         '    state.inputSha = sha256(raw);\n    state.phase = "ATTESTATION";'),
        ("    (dependencies.store || storeAttestation)(raw, attestation);",
         '''    state.attested = {
      run_id: attestation.planned.run_id,
      container_id: attestation.observed.container_id,
      daemon_id: attestation.observed.daemon.daemon_id,
      packet_sha256: attestation.authorization.packet_sha256,
      literal_review_sha256: attestation.authorization.literal_review_sha256,
    };
    state.phase = "PRIVATE_STORE";
    (dependencies.store || storeAttestation)(raw, attestation);
    state.phase = "LOCAL_GUARD";'''),
        ("    const result = (dependencies.spawn || spawnSync)",
         '    state.phase = "DISPATCH";\n    const result = (dependencies.spawn || spawnSync)'),
        ("    const summary = summarizeProcess(result, argv[2]);",
         '    state.phase = "RESULT";\n    const summary = summarizeProcess(result, argv[2]);'),
    ):
        runner = replace(runner, prior, current)
    return section(runner, "  } catch (error) {\n    (dependencies.emit", "\n}\n\nif (process.argv[1]",
                   '''  } catch (error) {
    (dependencies.emit || (value => process.stdout.write(JSON.stringify(value) + "\\n")))(refusal(state, error));
    return 1;
  }''')


def render_runtime(root):
    parent = load_parent(root)
    old = parent.render_runtime(root)
    replace, section = parent.replace, parent.section
    config = old[parent.RUNTIME[0]]
    guard = old[parent.RUNTIME[1]].decode()
    runner = old[parent.RUNTIME[2]].decode()
    for prior, current in (
        (parent.RUNTIME[0], RUNTIME[0]),
        (f'"{parent.RUNTIME[1]}", "{parent.RUNTIME[2]}"', f'"{RUNTIME[1]}", "{RUNTIME[2]}"'),
        (parent.RUN_SCHEMA, RUN_SCHEMA),
        (parent.HISTORY_SCHEMA, HISTORY_SCHEMA),
        (parent.ATTESTATION_SCHEMA, ATTESTATION_SCHEMA),
        (parent.LABEL, LABEL),
        ("wa-cloud-runtime-lease-history-v1-attestation.json", "wa-cloud-runtime-lease-history-v2-attestation.json"),
        ("wa-cloud-runtime-lease-history-v1-migrator-url", "wa-cloud-runtime-lease-history-v2-migrator-url"),
        ('"labels","bootstrap_secret_host_path"],"TARGET_FIELDS"', '"labels","bootstrap"],"TARGET_FIELDS"'),
        ('"run_manifest_sha256","operation","observed"],"ATTESTATION_FIELDS"',
         '"run_manifest_sha256","operation","observed","authorization"],"ATTESTATION_FIELDS"'),
        ('"labels","bootstrap_secret_host_path","bootstrap_readonly"],"OBSERVATION_FIELDS"',
         '"labels","bootstrap","bootstrap_removed","mount_destinations"],"OBSERVATION_FIELDS"'),
    ):
        guard = replace(guard, prior, current)
    guard = patch_platform(root, guard)
    guard = section(guard, "  requireLocal(target.bootstrap_secret_host_path", "  keys(target.labels,",
                    '  requireLocal(equal(target.bootstrap, BOOTSTRAP),"EXACT_BOOTSTRAP_TRANSPORT");\n')
    guard = section(guard, "  requireLocal(observed.bootstrap_secret_host_path", "  requireLocal(equal(observed.labels,",
                    '''  requireLocal(equal(observed.bootstrap, planned.target.bootstrap) && observed.bootstrap_removed===true
    && equal(observed.mount_destinations, MOUNT_DESTINATIONS),"LIVE_BOOTSTRAP_REMOVED_AND_MOUNTS");
  const authorization = value.authorization;
  keys(authorization, ["packet_sha256", "literal_review_sha256"], "AUTHORIZATION_FIELDS");
  requireLocal(Object.values(authorization).every(digest => typeof digest === "string" && HASH.test(digest)),
    "EXACT_AUTHORIZATION_DIGESTS");
''')
    guard = replace(guard, '  privateMounts(io.mountInfo());',
                    '  privateMounts(io.mountInfo());\n  io.bootstrapAbsent();')
    guard = replace(guard, '{toolHash: hashStableTool, loopbackOnly, read:',
                    '{toolHash: hashStableTool, loopbackOnly, bootstrapAbsent: privateBootstrapAbsent, read:')
    for prior, current in (
        ("  privateMounts, readAttestationStdin,", "  privateBootstrapAbsent, privateMounts, readAttestationStdin,"),
        ('  privateMounts(fs.readFileSync("/proc/self/mountinfo", "utf8"));',
         '  privateMounts(fs.readFileSync("/proc/self/mountinfo", "utf8"));\n  privateBootstrapAbsent();'),
        ("previous.run_manifest_sha256 === attestation.run_manifest_sha256,",
         "previous.run_manifest_sha256 === attestation.run_manifest_sha256 &&\n"
         "      previous.authorization?.packet_sha256 === attestation.authorization.packet_sha256 &&\n"
         "      previous.authorization?.literal_review_sha256 === attestation.authorization.literal_review_sha256,"),
        ("    summary.daemon_id = attestation.observed.daemon.daemon_id;",
         "    summary.daemon_id = attestation.observed.daemon.daemon_id;\n"
         "    summary.packet_sha256 = attestation.authorization.packet_sha256;\n"
         "    summary.literal_review_sha256 = attestation.authorization.literal_review_sha256;"),
    ):
        runner = replace(runner, prior, current)
    require(runner.count(parent.OP_ARG) == runner.count(parent.RESULT_SCHEMA) == 2, "PARENT_RUNNER_IDENTITIES")
    runner = with_refusal_receipt(root, runner.replace(parent.OP_ARG, OP_ARG).replace(parent.RESULT_SCHEMA, RESULT_SCHEMA))
    return dict(zip(RUNTIME, (config, guard.encode(), runner.encode()), strict=True))


def target_for(run_id):
    target = v1.target_for(run_id)
    target.pop("bootstrap_secret_host_path")
    target["labels"]["workinants.rehearsal"] = LABEL
    target["bootstrap"] = dict(BOOTSTRAP)
    return target


def packet_dir(run_id):
    target_for(run_id)
    return SCRATCH / f"wa-cloud-f0-two-history-{run_id}"


def build(root, run_id, daemon, tool_archive):
    target = target_for(run_id)
    daemon = exact_daemon(daemon)
    tools = inspect_tools(root, tool_archive)
    runtime = render_runtime(root)
    files = {
        **runtime,
        SCHEMA: v1.pinned(root, SCHEMA),
        ORDERED[0]["path"]: v1.pinned(root, v1.INITIAL_PATH),
        ORDERED[1]["path"]: v1.pinned(root, v1.APPEND_PATH),
        f"{HISTORY}/migration_lock.toml": b'provider = "postgresql"\n',
    }
    manifest = {
        "schema": RUN_SCHEMA,
        "run_id": run_id,
        "purpose": PURPOSE,
        "daemon": daemon,
        "target": target,
        "source": {
            "initial_sql_sha256": INITIAL,
            "append_sql_sha256": APPEND,
            "ordered_history_sha256": sha(canonical(ORDERED)),
            "effective_expected_sha256": EFFECTIVE,
            "foundation_schema_sha256": SCHEMA_SHA,
            "runtime_files_sha256": {name: sha(raw) for name, raw in runtime.items()},
        },
        "history": {"path": HISTORY, "ordered": ORDERED},
        "tools": tools,
    }
    raw_manifest = encoded(manifest)
    files[HISTORY_MANIFEST] = encoded({
        "schema": HISTORY_SCHEMA,
        "scope": "PROVISIONAL_CLOUD_ONLY_NOT_HOSTED_ADOPTION",
        "run_id": run_id,
        "run_manifest_sha256": sha(raw_manifest),
        "migrations": HISTORY,
        "ordered": ORDERED,
        "ordered_history_sha256": manifest["source"]["ordered_history_sha256"],
        "effective_expected_sha256": EFFECTIVE,
        "foundation_schema": SCHEMA,
        "files_sha256": {name: sha(raw) for name, raw in files.items()},
        "database_contacted": False,
        "ledger_created_or_modified": False,
        "raw_structure_applied_separately": False,
        "public_source_archive_file_count": 8,
        "applied_history_rule": "Both exact applied checksums immutable; no resolve/baseline/direct ledger mutation in this family.",
    })
    require(len(files) == 8, "EXACT_SOURCE8")
    return manifest, raw_manifest, files


def attest(manifest, observed, operation, *, packet_sha256, literal_review_sha256):
    """Encode one operation with the exact host source and approval bindings."""
    require(operation in ("deploy", "status"), "OPERATION_DENIED")
    require(manifest["schema"] == RUN_SCHEMA and manifest["target"] == target_for(manifest["run_id"]),
            "EXACT_V2_TARGET")
    require(type(observed) is dict and set(observed) == {
        "endpoint", "daemon", "container_id", "container_name", "volume_name", "volume_created_at",
        "image", "image_id", "network", "published_ports", "labels", "bootstrap", "bootstrap_removed",
        "mount_destinations",
    }, "OBSERVATION_FIELDS")
    require(observed["endpoint"] == ENDPOINT and exact_daemon(observed["daemon"]) == manifest["daemon"],
            "CLOUD_ENDPOINT_AND_DAEMON")
    target = manifest["target"]
    require(all(observed[key] == target[key] for key in ("container_name", "volume_name", "image", "network",
            "labels", "bootstrap")) and observed["image_id"] in IMAGE_IDS
            and observed["published_ports"] is False and observed["bootstrap_removed"] is True
            and observed["mount_destinations"] == list(MOUNT_DESTINATIONS)
            and type(observed["container_id"]) is str and re.fullmatch("[0-9a-f]{64}", observed["container_id"])
            and type(observed["volume_created_at"]) is str
            and re.fullmatch("[0-9TZ:.+-]{20,64}", observed["volume_created_at"]), "LIVE_RESOURCE_IDENTITY")
    authorization = dict(zip(AUTHORIZATION_FIELDS, (packet_sha256, literal_review_sha256), strict=True))
    require(all(type(digest) is str and re.fullmatch("[0-9a-f]{64}", digest) for digest in authorization.values()),
            "EXACT_AUTHORIZATION_DIGESTS")
    return encoded({"schema": ATTESTATION_SCHEMA, "operation": operation, "planned": manifest,
                    "observed": observed, "authorization": authorization, "run_manifest_sha256": sha(encoded(manifest))})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--daemon-observation", required=True, type=Path)
    parser.add_argument("--tool-archive", required=True, type=Path)
    args = parser.parse_args()
    try:
        require(SCRATCH.resolve(strict=True) == SCRATCH and args.daemon_observation.is_relative_to(SCRATCH),
                "SCRATCH_CONFINEMENT")
        daemon = strict_json(read(args.daemon_observation))
        manifest, raw_manifest, files = build(ROOT, args.run_id, daemon, args.tool_archive)
        output = packet_dir(args.run_id)
        out_tar = archive_source(files)
        binding = {
            "status": "HELD_NOT_RUN",
            "run_id": manifest["run_id"],
            "run_manifest_sha256": sha(raw_manifest),
            "source8_tar_sha256": sha(out_tar),
            "source8_files_sha256": {name: sha(raw) for name, raw in files.items()},
            "tool_archive_sha256": TOOL_TAR_SHA,
            "independent_operation_review": "PENDING",
        }
        output.mkdir(mode=0o700)
        for name, raw in {"run-manifest.json": raw_manifest, "source8.tar": out_tar,
                          "binding.json": encoded(binding)}.items():
            with os.fdopen(os.open(output / name, os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_WRONLY, 0o600), "wb") as stream:
                stream.write(raw)
        print(encoded(binding).decode(), end="")
        return 0
    except Held as error:
        print(json.dumps({"status": "HELD_NOT_RUN", "code": str(error)}))
        return 1
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print(json.dumps({"status": "HELD_NOT_RUN", "code": "PREPARATION_UNCONFIRMED"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
