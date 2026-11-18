"""Dormant local-only Prisma coordinator. Never provisions, pulls or resets.

This NEW config/history path is provisional rehearsal tooling. Before execution,
the integration operator supplies the reviewed source/run manifest, provisions
the pinned tool closure, and writes an owner-only migrator URL to private tmpfs.
The URL is never an argument, environment variable, captured log or evidence.
Importing this module, --help, and the offline checks contact no runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
preparation = runpy.run_path(str(ROOT / "scripts/prepare-local-f0-history.py"))
HeldFailure = preparation["HeldFailure"]
require = preparation["require"]
validate_manifest = preparation["validate_manifest"]
ENDPOINT = "npipe:////./pipe/dockerDesktopLinuxEngine"
SOURCE_ROOT = "/run/wa-f0-source"
TOOLS_ROOT = "/run/wa-f0-tools"
PRIVATE_ROOT = "/run/wa-secrets"
MOUNT_CHECKS = ('metadata_list','one_data_volume','one_bootstrap_bind','bootstrap_source','bootstrap_destination','bootstrap_readonly','only_declared_mounts','source_exact_windows','source_exact_desktop')


def bootstrap_source_comparison(actual, expected):
    """Only the exact planned Windows path or observed Desktop translation.

    No suffix/case folding, alternate host prefixes, URI decoding or general
    path normalization. The manifest's Windows path is validated first.
    """
    try: preparation['validate_bootstrap_secret_path'](expected)
    except HeldFailure:return False, False
    if type(actual) is not str:return False, False
    windows=PureWindowsPath(expected)
    desktop='/run/desktop/mnt/host/'+windows.drive[0].lower()+'/'+'/'.join(windows.parts[1:])
    return actual==expected, actual==desktop


def private_mount_comparison(target, mounts):
    checks=dict.fromkeys(MOUNT_CHECKS,False)
    if type(mounts) is not list or not all(type(m) is dict for m in mounts):return checks
    checks['metadata_list']=True
    data=[m for m in mounts if m.get('Type')=='volume' and m.get('Name')==target['volume_name'] and m.get('Destination')=='/var/lib/postgresql/data' and m.get('RW') is True]
    binds=[m for m in mounts if m.get('Type')=='bind']
    checks['one_data_volume']=len(data)==1;checks['one_bootstrap_bind']=len(binds)==1
    secret=[]
    if len(binds)==1:
        bind=binds[0]
        windows,desktop=bootstrap_source_comparison(bind.get('Source'),target['bootstrap_secret_host_path'])
        checks.update(source_exact_windows=windows,source_exact_desktop=desktop,bootstrap_source=windows or desktop,bootstrap_destination=bind.get('Destination')=='/run/bootstrap-password',bootstrap_readonly=bind.get('RW') is False)
        if checks['bootstrap_source'] and checks['bootstrap_destination'] and checks['bootstrap_readonly']:secret=[bind]
    checks['only_declared_mounts']=all(m in data or m in secret or m.get('Type')=='tmpfs' and m.get('Destination')==PRIVATE_ROOT for m in mounts)
    return checks


def mount_failure_comparison(error):
    value=getattr(error,'mount_comparison',None)
    return value if type(value) is dict and set(value)==set(MOUNT_CHECKS) and all(type(v) is bool for v in value.values()) else None


def unique_json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "DUPLICATE_JSON_KEY")
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=unique)


def inspect_live(manifest, context, container, volume):
    """Pure metadata comparator; does not invoke Docker or contact Postgres."""
    target = manifest["target"]
    require(context.get("Name") == "desktop-linux" and
            context.get("Endpoints", {}).get("docker", {}).get("Host") == ENDPOINT,
            "LOCAL_DOCKER_ENDPOINT_REQUIRED")
    require(re.fullmatch(r"[0-9a-f]{64}", container.get("Id", "")), "CONTAINER_ID")
    require(container.get("Name") == "/" + target["container_name"] and
            container.get("Config", {}).get("Image") == target["image"] and
            container.get("Platform") == "linux" and container.get("State", {}).get("Running") is True,
            "LIVE_PINNED_CONTAINER_REQUIRED")
    labels = container.get("Config", {}).get("Labels", {})
    require(all(labels.get(key) == value for key, value in target["labels"].items()), "LIVE_RUN_LABELS")
    host = container.get("HostConfig", {})
    ports = container.get("NetworkSettings", {}).get("Ports") or {}
    require(host.get("NetworkMode") == "none" and not host.get("PortBindings") and
            type(ports) is dict and all(value is None for value in ports.values()) and
            host.get("Privileged") is False and not host.get("PidMode") and
            host.get("IpcMode") in ("", "private") and
            not host.get("Devices") and not host.get("CapAdd"), "PRIVATE_CONTAINER_REQUIRED")
    mounts = container.get("Mounts", [])
    checks=private_mount_comparison(target,mounts)
    if not all(checks[name] for name in MOUNT_CHECKS[:7]):
        error=HeldFailure('EXACT_PRIVATE_MOUNTS_REQUIRED');error.mount_comparison=checks
        raise error
    require(volume.get("Name") == target["volume_name"] and volume.get("Driver") == "local" and
            not volume.get("Options") and volume.get("Scope") == "local" and
            all(volume.get("Labels", {}).get(key) == value for key, value in target["labels"].items()), "RUN_OWNED_VOLUME_REQUIRED")
    tmpfs = host.get("Tmpfs", {})
    options = set(tmpfs.get(PRIVATE_ROOT, "").split(","))
    require(set(tmpfs) == {PRIVATE_ROOT} and {"noexec", "nosuid", "nodev"}.issubset(options) and
            bool(options.intersection({"mode=0700", "mode=700"})), "PRIVATE_SECRET_TMPFS_REQUIRED")
    return {"endpoint": ENDPOINT, "context": "desktop-linux", "container_id": container["Id"],
            "container_name": target["container_name"], "volume_name": target["volume_name"],
            "image": target["image"], "network": "none", "published_ports": False,
            "labels": target["labels"], "bootstrap_secret_host_path": target["bootstrap_secret_host_path"]}


def verify_image(manifest, container, image):
    digest = manifest["target"]["image"].split("@", 1)[1]
    require(type(image.get("Id")) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", image["Id"]) and
            container.get("Image") == image["Id"] and image.get("Os") == "linux" and
            image.get("Architecture") == "amd64" and
            any(type(value) is str and value.rsplit("@", 1)[-1] == digest for value in image.get("RepoDigests", [])),
            "ACTUAL_PINNED_IMAGE_REQUIRED")


def copied_entrypoint_preflight(manifest, observed, runtime_sources, process):
    """Use the trusted pinned-image utility BEFORE copied Node/JS can execute."""
    require(set(runtime_sources) == set(preparation["RUNTIME_FILES"]), "RUNTIME_SOURCE_FILES")
    reviewed = manifest["source"]["runtime_files_sha256"]
    require({name: hashlib.sha256(raw).hexdigest() for name, raw in runtime_sources.items()} == reviewed, "REVIEWED_RUNTIME_DRIFT")
    expected = {TOOLS_ROOT + "/node/bin/node": manifest["tools"]["files_sha256"]["node/bin/node"],
                **{SOURCE_ROOT + "/" + name: value for name, value in reviewed.items()}}
    result = process(["docker", "--context", "desktop-linux", "exec", observed["container_id"],
                      "/usr/bin/sha256sum", "--", *sorted(expected)],
                     text=True, capture_output=True, timeout=30, shell=False)
    require(result.returncode == 0, "COPIED_ENTRYPOINT_HASH_CHECK_FAILED")
    actual = {}
    for line in result.stdout.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (/run/wa-f0-(?:source|tools)/[^\r\n]+)", line)
        require(match is not None and match[2] not in actual, "COPIED_ENTRYPOINT_HASH_OUTPUT")
        actual[match[2]] = match[1]
    require(actual == expected, "COPIED_ENTRYPOINT_DRIFT")


def validate_rollback(proof, manifest, observed):
    """Require an operator-reviewed independent catalog/ledger evidence summary.

    This validates its binding; it does not itself prove the database assertions.
    Fresh real catalog/ledger observations must precede the standard resolve.
    """
    require(proof.get("schema") == "workinants.local-f0-reviewed-rollback.v1" and
            proof.get("run_id") == manifest["run_id"] and proof.get("container_id") == observed["container_id"] and
            proof.get("migration_id") == manifest["migration"]["id"] and
            proof.get("source_sql_sha256") == manifest["source"]["integrated_sql_sha256"], "ROLLBACK_PROOF_IDENTITY")
    require(proof.get("disposition") == "REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK" and
            proof.get("backend_closed") is True and proof.get("application_transaction_rolled_back") is True and
            type(proof.get("application_object_count")) is int and proof["application_object_count"] == 0 and
            type(proof.get("failed_migration_rows")) is int and proof["failed_migration_rows"] == 1 and
            type(proof.get("finished_migration_rows")) is int and proof["finished_migration_rows"] == 0 and
            type(proof.get("rolled_back_migration_rows")) is int and proof["rolled_back_migration_rows"] == 0 and
            proof.get("failed_row_checksum") == manifest["source"]["integrated_sql_sha256"] and
            all(type(proof.get(key)) is str and re.fullmatch(r"[0-9a-f]{64}", proof[key])
                for key in ("catalog_evidence_sha256", "ledger_evidence_sha256")), "INDEPENDENT_ROLLBACK_REVIEW_REQUIRED")


def safe_result(raw, manifest, observed, operation):
    value = unique_json(raw)
    require(type(value) is dict and value.get("schema") == "workinants.local-f0-migrate-result.v1", "RUNNER_RESULT_SCHEMA")
    permitted = {"schema", "operation", "status", "exit_code", "prisma_codes", "sqlstates", "no_pending_message_observed",
                 "raw_output_discarded", "database_qualification_claimed", "run_id", "container_id", "source_sql_sha256", "attestation_sha256"}
    require(set(value) == permitted and value["operation"] == operation and
            value["run_id"] == manifest["run_id"] and value["container_id"] == observed["container_id"] and
            value["source_sql_sha256"] == manifest["source"]["integrated_sql_sha256"] and
            value["raw_output_discarded"] is True and value["database_qualification_claimed"] is False,
            "RUNNER_RESULT_IDENTITY")
    require(value["status"] in {"CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS", "CLI_FAILED_STOP_AND_INSPECT", "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE"} and
            (value["exit_code"] is None or type(value["exit_code"]) is int and 0 <= value["exit_code"] <= 255) and
            type(value["no_pending_message_observed"]) is bool and
            type(value["prisma_codes"]) is list and all(type(code) is str and re.fullmatch(r"P[13][0-9]{3}", code) for code in value["prisma_codes"]) and
            type(value["sqlstates"]) is list and set(value["sqlstates"]).issubset({"42501", "42703", "22012", "P0001", "23503", "23505", "23514"}) and
            type(value["attestation_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", value["attestation_sha256"]), "RUNNER_RESULT_VALUES")
    return value


def docker_json(arguments, process):
    result = process(["docker", "--context", "desktop-linux", *arguments],
                     text=True, capture_output=True, timeout=30, shell=False)
    require(result.returncode == 0, "LOCAL_RUNTIME_INSPECTION_FAILED")
    value = unique_json(result.stdout)
    require(type(value) is list and len(value) == 1 and type(value[0]) is dict, "RUNTIME_INSPECTION_SCHEMA")
    return value[0]


def coordinate(manifest_bytes, operation, proof_bytes=None, process=subprocess.run, runtime_sources=None):
    manifest = validate_manifest(unique_json(manifest_bytes.decode("utf8")))
    context = docker_json(["context", "inspect", "desktop-linux"], process)
    container = docker_json(["inspect", manifest["target"]["container_name"]], process)
    volume = docker_json(["volume", "inspect", manifest["target"]["volume_name"]], process)
    observed = inspect_live(manifest, context, container, volume)
    image = docker_json(["image", "inspect", manifest["target"]["image"]], process)
    verify_image(manifest, container, image)
    if runtime_sources is None:
        runtime_sources = {path: (ROOT / path).read_bytes() for path in preparation["RUNTIME_FILES"]}
    copied_entrypoint_preflight(manifest, observed, runtime_sources, process)
    attestation = {"schema": "workinants.local-f0-live-attestation.v1", "planned": manifest,
                   "run_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(), "observed": observed}
    require(operation in ("deploy", "status", "resolve-rolled-back"), "OPERATION_DENIED")
    if operation == "resolve-rolled-back":
        require(proof_bytes is not None, "REVIEWED_ROLLBACK_PROOF_REQUIRED")
        proof = unique_json(proof_bytes.decode("utf8"))
        validate_rollback(proof, manifest, observed)
        attestation["recovery"] = {"proof": proof, "proof_sha256": hashlib.sha256(proof_bytes).hexdigest()}
    else:
        require(proof_bytes is None, "UNEXPECTED_RECOVERY_PROOF")
    raw = json.dumps(attestation, separators=(",", ":"))
    # Exact observed immutable ID, never a name lookup after inspection. No secret
    # or URL is transported in arguments/environment/stdin; only public metadata.
    result = process(["docker", "--context", "desktop-linux", "exec", "-i", observed["container_id"],
                      TOOLS_ROOT + "/node/bin/node", SOURCE_ROOT + "/scripts/sql-review/local-f0-migrate-runner.mjs",
                      "--execute-reviewed-local-f0", "--operation", operation],
                     input=raw, text=True, capture_output=True, timeout=150, shell=False)
    value = safe_result(result.stdout, manifest, observed, operation)
    require(value["attestation_sha256"] == hashlib.sha256(raw.encode("utf8")).hexdigest(), "ATTESTATION_RESULT_MISMATCH")
    require((result.returncode == 0) == (value["exit_code"] == 0), "RUNNER_EXIT_MISMATCH")
    return value


def main(argv=None, process=subprocess.run):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-reviewed-local-f0", action="store_true")
    parser.add_argument("--run-manifest", type=Path)
    parser.add_argument("--operation", choices=("deploy", "status", "resolve-rolled-back"))
    parser.add_argument("--reviewed-rollback-proof", type=Path)
    parser.add_argument("--evidence-file", type=Path)
    args = parser.parse_args(argv)
    try:
        require(args.execute_reviewed_local_f0 and args.run_manifest is not None and args.operation is not None, "EXPLICIT_EXECUTION_REQUIRED")
        if args.evidence_file is not None:
            evidence = args.evidence_file.resolve()
            require(not evidence.is_relative_to(ROOT.resolve()) and not evidence.exists(), "FRESH_EXTERNAL_EVIDENCE_REQUIRED")
        raw = args.run_manifest.read_bytes()
        require(len(raw) <= 4 * 1024 * 1024, "RUN_MANIFEST_SIZE")
        proof = args.reviewed_rollback_proof.read_bytes() if args.reviewed_rollback_proof else None
        value = coordinate(raw, args.operation, proof, process)
        if args.evidence_file is not None:
            with args.evidence_file.open("x", encoding="utf8", newline="\n") as file:
                file.write(json.dumps(value, indent=2) + "\n")
        print(json.dumps(value))
        return 0 if value["exit_code"] == 0 else 1
    except Exception as error:
        # Never print a subprocess exception, raw engine output, input document,
        # URL, error detail or environment value.
        comparison=mount_failure_comparison(error)
        print(json.dumps({"schema": "workinants.local-f0-migrate-result.v1", "status": "REFUSED_OR_INCOMPLETE",
                          "code": error.code if isinstance(error, HeldFailure) else "INVALID_INPUT_IO_OR_UNCONFIRMED_PROCESS",
                          **({'mount_comparison':comparison} if comparison is not None else {}),
                          "raw_output_discarded": True, "database_qualification_claimed": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
