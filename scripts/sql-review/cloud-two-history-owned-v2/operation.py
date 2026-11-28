"""Reviewed Cloud TWO execution entry. The historical database proof stays intact."""

import argparse
import ast
from datetime import datetime, timezone
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import signal
import subprocess
import sys
import threading
import time

from basis import ROOT, S, P, B, exact_shadow_modules, safe_code
from plan import compare_source8, exact_reviews, read_closed


AUTH = "scripts/sql-review/run-first-rehearsal.py"
CONTROL_APPROVAL = "--execute-reviewed-cloud-f0-two-history-owned-v2"
DATABASE = "wa_p0c_rehearsal"
ROLES = ("postgres", "wa_migrator", "wa_context_issuer", "wa_identity_service_authority",
         "wa_app_runtime", "wa_worker")
NATIVE_PINS = f"{S.NATIVE_REVIEW}/source-pins.json"
ROLE_LEAVES = ("wa_private_helper_owner", "wa_customer_verifier", "wa_track_verifier")
START_RECIPE = ("umask 077; set -C; cat > \"$1\"; "
                "test \"$(stat -c '%u:%g:%a:%h' -- \"$1\")\" = '0:0:600:1'")
EXTRACT_RECIPE = 'umask 022; exec /usr/bin/tar "$1" "$2" -C "$3"'
TREE_FORMAT = "%y|%p|%s|%U|%G|%m|%n\n"
TREE_INVENTORY_LIMIT = 4 * 1024 * 1024
TOOL_EXECUTABLES = frozenset(("node/bin/node", "schema-engine"))
REFUSAL_PHASES = ("ARGUMENTS", "INPUT", "ATTESTATION", "PRIVATE_STORE", "LOCAL_GUARD", "DISPATCH", "RESULT")
EXCLUDED_CORE = {
    "initialize", "docker", "inventory", "owned", "inspect_container", "inspect_volume", "psql_args",
    "secure_private_directory", "preflight", "create_resources", "cleanup",
    "admit_command", "command", "source13_process", "entry_source_gate", "ensure_image", "launch",
}
EXCLUDED_STEPS = {
    "verify_packet", "inspect_owned", "prestart_private_metadata", "provision_tools", "migrate", "postchecks",
}


class CloudIO:
    Thread = staticmethod(threading.Thread)
    monotonic = staticmethod(time.monotonic)

    @staticmethod
    def Popen(args, **options):
        return subprocess.Popen(args, env={"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C"}, **options)


def reviewed_program(root, blobs):
    """Retain exact logical stages and replace identifiable platform boundaries."""
    raw = blobs[S.OPERATOR]
    S.require(S.sha(raw) == S.HISTORICAL_PINS[S.OPERATOR], "CLOSED_OPERATION_ORIGIN")
    old = b"""remote_exec=args[:4]==['docker','--context','desktop-linux','exec'];attempted=False"""
    new = b"""remote_exec=len(args)>5 and args[1]=='--config' and args[3:6]==['--host','unix:///var/run/docker.sock','exec'];attempted=False"""
    S.require(raw.count(old) == 1, "REMOTE_CLASSIFIER_SOURCE_SHAPE")
    source = ast.parse(raw.replace(old, new), filename=S.OPERATOR)
    excluded = {node.name for node in source.body if isinstance(node, ast.FunctionDef) and node.name in EXCLUDED_CORE}
    S.require(excluded == EXCLUDED_CORE, "OPERATION_PORT_SURFACE")
    source.body = [node for node in source.body if not (isinstance(node, ast.FunctionDef) and node.name in excluded)
                   and not isinstance(node, ast.If)]
    program = S.module(root, S.OPERATOR, ast.unparse(source).encode())

    reviewed = blobs[S.STEPS]
    S.require(S.sha(reviewed) == S.HISTORICAL_PINS[S.STEPS], "CLOSED_STEPS_ORIGIN")
    stages = ast.parse(reviewed, filename=S.STEPS)
    excluded_steps = {node.name for node in stages.body if isinstance(node, ast.FunctionDef)
                      and node.name in EXCLUDED_STEPS}
    S.require(excluded_steps == EXCLUDED_STEPS, "STEP_PORT_SURFACE")
    stages.body = [node for node in stages.body
                   if not isinstance(node, ast.FunctionDef) or node.name not in excluded_steps]
    result_schema = [value for value in ast.walk(stages) if isinstance(value, ast.Constant)
                     and value.value == "workinants.runtime-lease-two-history-owned-results.v1"]
    S.require(len(result_schema) == 1, "RESULT_SCHEMA_SOURCE_SHAPE")
    result_schema[0].value = "workinants.cloud-two-history-owned-results.v2"
    exec(compile(stages, str(root / S.STEPS), "exec"), program.__dict__)
    return program


def cloud_docker(guard, transport, profile, config):
    """Use the reviewed bounded process transport for every Cloud Docker request."""
    class BoundedDocker(guard.Docker):
        container_create_dispatched = False

        def run(self, *args, stdin=None, timeout=20, allow_fail=False,
                operation="DOCKER_METADATA_OR_RESOURCE", profile="metadata_tools"):
            command = self.argv(*args)
            if args[:2] == ("container", "create"):
                self.container_create_dispatched = True
            try:
                result = transport.binary(command, stdin, timeout, profile)
                if not 0 <= result.returncode <= 255:
                    transport.unknown = True
                    raise S.Held("REMOTE_PROCESS_EXIT_UNCONFIRMED")
            except BaseException:
                self.remote_unknown = transport.unknown = True
                raise
            S.require(self.socket_identity() == self.origin, "DOCKER_SOCKET_CHANGED")
            if not allow_fail and (result.returncode != 0 or result.stderr != b""):
                self.last_refusal = guard.safe_refusal(result, operation)
                raise S.Held("DOCKER_COMMAND_REFUSED")
            return result

    return BoundedDocker(profile, config)


class Owner:
    def __init__(self, prepared, raw, reviews, docker_factory=cloud_docker):
        directory, operation, blobs, inner, manifest, nested, files, archive = prepared
        self.prepared, self.directory, self.operation, self.blobs = prepared, directory, operation, blobs
        self.inner, self.manifest, self.nested, self.files, self.archive = inner, manifest, nested, files, archive
        self.raw, self.reviews = raw, reviews
        self.target = manifest["target"]
        self.name = self.target["container_name"]
        self.volume = self.target["volume_name"]
        self.bootstrap_removed = False
        self.report = {
            "schema": "workinants.cloud-two-history-owned-run-evidence.v2",
            "started_at": datetime.now(timezone.utc).isoformat(), "status": "IN_PROGRESS", "stage": "ENTRY",
            "run_id": operation["run_id"], "approved_commit": operation["source"]["commit"],
            "approved_tree": operation["source"]["tree"], "approved_packet_sha256": S.sha(raw),
            "independent_source_review_sha256": reviews["source"], "literal_review_sha256": reviews["literal"],
            "events": [], "steps": {}, "targets": {}, "unexpected": [], "cleanup": {}, "checks": [],
            "limits": {"posture": "D", "business_assertions_qualified": 0, "candidate_adopted": False,
                       "hosted_changes": False, "worker_loop": False, "production_readiness": False},
        }
        self.program = reviewed_program(ROOT, blobs)
        self.transport = self.program.Transport(ROOT, io=CloudIO())
        self.guard, probe = exact_shadow_modules(ROOT, blobs)
        S.require(S.sha(probe.START_CONTROL.encode()) == self.target["bootstrap"]["startup_gate_sha256"]
                  and S.sha(probe.WRITE_BOOTSTRAP.encode()) == self.target["bootstrap"]["write_gate_sha256"],
                  "EXACT_WITNESSED_STARTUP_RECIPES")
        probe.DATABASE = DATABASE
        probe.SERVER_FLAGS = [
            *probe.SERVER_FLAGS, "-c", "password_encryption=scram-sha-256",
            "-c", "log_line_prefix=WA_F0_DIAG|%e|%u|%d|", "-c", "lc_messages=C",
            "-c", "log_min_messages=warning",
        ]
        config = probe.new_client_config(directory)
        self.docker = docker_factory(self.guard, self.transport, operation["profile"], config)
        self.resources = probe.Probe(
            {**operation, "source": {"files_sha256": operation["source_pins"]}, "cached_image": operation["image"],
             "target": {"container": self.name, "volume": self.volume, "labels": self.target["labels"],
                        "bootstrap_container_path": self.target["bootstrap"]["container_path"],
                        "private_host_path": str(directory / "private")}},
            operation["profile"], directory, self.docker, self.report,
        )
        B.CLOUD_RESULT = inner.RESULT_SCHEMA
        self.receipt_validator = B.result_validator(ROOT, blobs)
        self.configure_program()

    def configure_program(self):
        namespace = self.program.__dict__
        operation = self.operation
        namespace.update(
            ROOT=ROOT, TASK=self.directory, OUT=self.directory / "evidence", PRIVATE=self.directory / "private",
            MANIFEST={"packet_files_sha256": operation["source_pins"], "migration_target": {
                "source_snapshot": str(self.directory / "source8"),
            }},
            MANIFEST_PATH=self.directory / "operation.json", COMMIT=operation["source"]["commit"],
            TREE=operation["source"]["tree"], PACKET=S.sha(self.raw), DB=DATABASE, RUN_ID=operation["run_id"],
            IMAGE=self.target["image"], report=self.report, TRANSPORT=self.transport,
            CONNECTION_TAG="wa-first-" + operation["run_id"], ROLES=ROLES, LEAVES=ROLE_LEAVES,
            TARGETS=[{"name": self.name, "volume": self.volume, "kind": "ok"}],
            RESOURCE_CONTAINERS=(self.name,), RESOURCE_VOLUMES=(self.volume,),
            all_secrets=[], passwords={}, created_containers={}, bootstrap_attempted=set(), bootstrapped=set(),
            finalization_attempted=set(), finalized=set(), FIRST_OPERATION_FAILURE=None,
            verify_packet=self.verify_packet, preflight=self.preflight, ensure_image=self.ensure_image,
            create_resources=self.provision, provision_tools=self.stage_tools, psql_args=self.psql_args,
            command=self.command, migrate=self.migrate, cleanup=self.cleanup, postchecks=self.postchecks,
        )
        _, namespace["MANIFEST_ORIGIN"] = self.program.closed_bytes(namespace["MANIFEST_PATH"])
        self.program.SAFE_FAILURE_CODES |= frozenset({
            "DOCKER_COMMAND_REFUSED", "DOCKER_SOCKET_CHANGED", "REMOTE_PROCESS_EXIT_UNCONFIRMED",
            "FINALIZATION_UNKNOWN_TRANSPORT", "EXACT_START_CONTROL_REQUIRED", "CLOUD_RUNNER_RESPONSE",
            "CLOUD_RUNNER_AUTHORIZATION_BINDING", "CLOUD_RUNNER_TARGET_CID", "BOOTSTRAP_FILE_NOT_REMOVED",
            "CLOUD_OWNING_SOURCE_REVIEW_DRIFT", "CLOUD_TOOL_COPY_IDENTITY", "CLOUD_SOURCE_COPY_HASH_DRIFT",
            "CLOUD_SOURCE_COPY_LENGTHS", "UNSAFE_PSQL_COMMAND", "UNEXPECTED_PSQL_STDERR",
            "FULL_CONTAINER_ABSENCE_UNCONFIRMED",
            "CLOUD_COPIED_INVENTORY_SHAPE", "CLOUD_COPIED_INVENTORY_METADATA", "CLOUD_COPIED_INVENTORY_DRIFT",
            "CLOUD_INNER_TERMINAL_REFUSAL", "CLOUD_INNER_REFUSAL_RESPONSE_SHAPE",
            "CLOUD_INNER_REFUSAL_BINDING", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY",
        })

    def verify_packet(self):
        p = self.program
        p.STATE.update(captured=self.blobs, origins={}, finalization_verified=False)
        native = p.compile_captured(S.NATIVE, self.blobs[S.NATIVE])
        pins = S.unique_json(self.blobs[NATIVE_PINS])
        p.need(pins == {name: self.operation["source_pins"][name] for name in native.REQUIRED_FILES},
               "EXACT36_NATIVE_SOURCES")
        files, summary = native.prepare(ROOT, pins)
        p.need(summary["source_expected_sha256"] == S.EXPECTED and summary["expression_count"] == 416,
               "NEW_EFFECTIVE_EXPECTED")
        p.need({name: S.sha(raw) for name, raw in files.items()} == self.operation["native_files_sha256"],
               "SIX_NATIVE_ASSETS_REPRODUCE")
        _, tools, effective, two, blobs = native.load_tools(ROOT, pins)
        expected = effective.build_manifest(tools["catalog_manifest"], {
            name: blobs[name] for name in (*tools["catalog_manifest"].INPUTS, effective.PATCH_PATH)
        }, pins)
        p.CATALOG.update(generator=native, pins=pins, tools=tools, two=two, expected=expected,
                         plan=S.unique_json(files["expression-oracle-plan.json"]),
                         public=S.unique_json(files["public-schema-registration.json"]),
                         oracle_sql=files["expression-oracle.sql"].decode("utf-8"))
        p.CATALOG["strings"], p.CATALOG["generated_names"] = p.metadata_allowlist(expected, tools)
        # Import exactly the two historical pure authentication functions.
        auth = ast.parse(self.blobs[AUTH].decode("utf-8"), filename=AUTH)
        names = {"hba_matches", "authentication_comparison", "HeldFailure", "require"}
        selected = [node for node in auth.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                    and node.name in names]
        declared = [node for node in auth.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id in {
                        "DATABASE", "AUTH_TCP_ADDRESS", "AUTH_TCP_PORT", "AUTH_HBA_ADDRESS", "AUTH_HBA_NETMASK",
                    } for target in node.targets)]
        data = ("import json, re, ipaddress\n" + ast.unparse(ast.Module(body=[*declared, *selected], type_ignores=[]))).encode()
        auth_pure = S.module(ROOT, AUTH, data)
        auth_pure.DATABASE, auth_pure.ROLES = DATABASE, ROLES[1:]
        p.STATE["auth"] = auth_pure
        self.report["source_verification"] = {
            "source_count": len(self.blobs), "native_sha256": S.EXPECTED, "prior_primitive_and_capability": True,
        }
        p.event("SOURCE", "PASS")

    def preflight(self):
        self.resources.require_daemon()
        self.resources.require_absent()
        self.resources.cleanup_private()
        self.report["actual_daemon"] = self.docker.observe()
        self.program.event("LOCAL_PREFLIGHT", "PASS", all_created_names_absent=True)

    def ensure_image(self):
        image = self.docker.cached_image({"files_sha256": self.operation["source_pins"]})
        S.require(image == self.operation["image"], "PINNED_IMAGE_DRIFT")
        self.report["image"] = image
        self.program.event("PINNED_IMAGE", "PASS", pulled=False)

    def provision(self):
        p = self.program
        self.report["stage"] = "RESOURCE_PRESTART"
        p.passwords[self.name] = {role: secrets.token_hex(32) for role in ROLES}
        initial = p.passwords[self.name]
        p.all_secrets.extend(initial.values())
        self.resources.provision(initial["postgres"])
        self.bootstrap_removed = True
        p.created_containers[self.name] = self.resources.cid
        self.report["targets"][self.name] = {
            "container_id": self.resources.cid, "volume_created_at": self.resources.volume_birth,
            "volume": self.volume, "labels": self.target["labels"], "network_mode": "none",
            "published_ports": False, "bootstrap": "NOT_RUN", "application": "NOT_RUN", "finalization": "NOT_RUN",
        }
        pgpass = "".join(f"127.0.0.1:5432:{DATABASE}:{role}:{password}\n" for role, password in initial.items())
        self.write_private("/run/wa-secrets/pgpass", pgpass)
        p.event("RESOURCE_READY", "PASS", target=self.name)

    def exact_container_exec(self, *args, input=None, timeout=30, allow_fail=False, profile="control"):
        cid = self.resources.cid
        S.require(type(cid) is str and re.fullmatch(r"[0-9a-f]{64}", cid) and args.count(cid) == 1,
                  "UNOWNED_EXEC")
        return self.docker.run("exec", *args, stdin=input, timeout=timeout, allow_fail=allow_fail, profile=profile)

    def write_private(self, path, payload):
        prefix = "/run/wa-secrets"
        allowed = {f"{prefix}/pgpass", f"{prefix}/wa-cloud-runtime-lease-history-v2-migrator-url",
                   *(f"{prefix}/wrong-{role}.pgpass" for role in ROLES)}
        S.require(path in allowed and type(payload) is str and 0 < len(payload) <= 2048,
                  "EXACT_PRIVATE_CREDENTIAL_DESTINATION")
        result = self.exact_container_exec("-i", "--user", "0", self.resources.cid, "sh", "-ceu", START_RECIPE,
                                           "wa-write-private", path, input=payload.encode())
        S.require(result.stdout == b"", "PRIVATE_CREDENTIAL_WRITE_UNCONFIRMED")

    def stage_tools(self):
        p = self.program
        cid = self.resources.cid
        self.resources.check_target(True)
        root_exec = ("--user", "0", cid)
        self.exact_container_exec(*root_exec, "/usr/bin/mkdir", "-p", "-m", "0755",
                                  "/run/wa-f0-tools", "/run/wa-f0-source")
        paths = ((self.operation["tools"], "/run/wa-f0-tools.tar.gz", "tools", "-xzf"),
                 (self.operation["archive"], "/run/wa-f0-source.tar", "source", "-xf"))
        for record, dest, purpose, flags in paths:
            self.docker.run("cp", record["path"], f"{cid}:{dest}", timeout=120)
            measured = self.exact_container_exec(cid, "/usr/bin/sha256sum", "--", dest, timeout=120)
            S.require(measured.stdout == f"{record['sha256']}  {dest}\n".encode(), "CLOUD_TOOL_COPY_IDENTITY")
            self.exact_container_exec(*root_exec, "/bin/sh", "-ceu", EXTRACT_RECIPE, "wa-extract",
                                      flags, dest, f"/run/wa-f0-{purpose}", timeout=120)
            self.exact_container_exec(cid, "rm", "--", dest)
        tool_metadata = {
            f"/run/wa-f0-tools/{name}": (size, "755" if name in TOOL_EXECUTABLES else "644")
            for name, size in self.manifest["tools"]["file_sizes"].items()
        }
        source_metadata = {f"/run/wa-f0-source/{name}": (len(raw), "444") for name, raw in self.files.items()}
        inventory = self.exact_container_exec(
            *root_exec, "/usr/bin/find", "-P", "/run/wa-f0-tools", "/run/wa-f0-source", "-printf", TREE_FORMAT,
            timeout=60, profile="metadata_tools",
        )
        self.report["verified_copied_inventory_counts"] = validate_inventory(
            inventory.stdout, {**tool_metadata, **source_metadata})
        hashes = "".join(f"{digest}  /run/wa-f0-tools/{name}\n"
                         for name, digest in sorted(self.manifest["tools"]["files_sha256"].items()))
        verified = self.exact_container_exec("-i", cid, "/usr/bin/sha256sum", "--check", "--strict", "--status",
                                             input=hashes.encode(), timeout=120)
        S.require(verified.stdout == b"", "CLOUD_TOOL_COPY_IDENTITY")
        for file, version in (("/run/wa-f0-tools/node/bin/node", b"v24.22.1"),
                              ("/run/wa-f0-tools/schema-engine", b"d1b3f377ca835d73fd50954a5e22128b9ebdd6b8")):
            result = self.exact_container_exec(cid, file, "--version")
            S.require(version in result.stdout, "CLOUD_TOOL_COPY_IDENTITY")
        url = ("postgresql://wa_migrator:" + p.passwords[self.name]["wa_migrator"]
               + "@127.0.0.1:5432/" + DATABASE + "?schema=public&sslmode=disable")
        self.write_private("/run/wa-secrets/wa-cloud-runtime-lease-history-v2-migrator-url", url)
        for role in ROLES:
            wrong = secrets.token_hex(32)
            p.all_secrets.append(wrong)
            self.write_private(f"/run/wa-secrets/wrong-{role}.pgpass", f"127.0.0.1:5432:{DATABASE}:{role}:{wrong}\n")
        p.event("TOOLS", "PASS", members=10300)

    def psql_args(self, target, role):
        S.require(target == self.name and role in ROLES and self.resources.cid is not None, "UNSAFE_PSQL_COMMAND")
        return [
            "exec", "-i", "-e", "PGPASSFILE=/run/wa-secrets/pgpass", "-e", "PGSSLMODE=disable",
            "-e", "PGGSSENCMODE=disable", "-e", "PGAPPNAME=" + self.program.CONNECTION_TAG,
            self.resources.cid, "psql", "-X", "-w", "-qAt", "-v", "ON_ERROR_STOP=1",
            "-v", "VERBOSITY=verbose", "-v", "SHOW_CONTEXT=never", "-h", "127.0.0.1", "-p", "5432",
            "-U", role, "-d", DATABASE,
        ]

    def command(self, args, text, timeout=60):
        p = self.program
        p.need(not self.transport.unknown, "FINALIZATION_UNKNOWN_TRANSPORT")
        allowed = []
        for role in ROLES:
            correct = self.psql_args(self.name, role)
            allowed.extend((correct, [item.replace("PGPASSFILE=/run/wa-secrets/pgpass",
                                                   f"PGPASSFILE=/run/wa-secrets/wrong-{role}.pgpass")
                                      for item in correct]))
        p.need(args in allowed and type(text) is str and len(text.encode()) <= 4194304
               and type(timeout) is int and 0 < timeout <= 120, "UNSAFE_PSQL_COMMAND")
        result = self.exact_container_exec(*args[1:], input=text.encode(), timeout=timeout, allow_fail=True,
                                           profile="native_oracle" if self.report["stage"].startswith(
                                               ("NATIVE", "ORACLE", "LEDGER")) else "control")
        if result.returncode == 0 and result.stderr:
            # Historical SQL success may emit notices. Nothing from that
            # channel is retained. Strict observers also check their own exact
            # status and shape at the reviewed logical stage.
            p.need(self.report["stage"] == "ORIGINAL_BOOTSTRAP", "UNEXPECTED_PSQL_STDERR")
        return p.Result(result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8"))

    def observed_target(self):
        self.resources.require_daemon()
        self.resources.check_target(True)
        cid = self.resources.cid
        S.require(self.bootstrap_removed, "BOOTSTRAP_FILE_NOT_REMOVED")
        for leaf in ("bootstrap-password", "bootstrap-pending"):
            self.exact_container_exec(cid, "test", "!", "-e", f"/run/wa-secrets/{leaf}")
            self.exact_container_exec(cid, "test", "!", "-L", f"/run/wa-secrets/{leaf}")
        return {
            "endpoint": self.inner.ENDPOINT, "daemon": self.docker.observe(), "container_id": cid,
            "container_name": self.name, "volume_name": self.volume, "volume_created_at": self.resources.volume_birth,
            "image": self.target["image"], "image_id": self.operation["image"]["image_id"],
            "network": "none", "published_ports": False, "labels": self.target["labels"],
            "bootstrap": self.target["bootstrap"], "bootstrap_removed": True,
            "mount_destinations": ["/run/wa-secrets", "/var/lib/postgresql/data"],
        }

    def migrate(self, operation, label):
        p = self.program
        self.report["stage"] = label
        p.save()
        dispatched = False
        with p._RequiredSafetyBoundary("CLOSE", self.name, label + "_CLOSED"):
            try:
                compare_source8(self.directory, self.nested, self.files, self.archive)
                observed = self.observed_target()
                paths = B.copied_paths(self.inner, self.manifest, self.files)
                cid = observed["container_id"]
                probe = self.exact_container_exec(cid, "/usr/bin/sha256sum", "--", *sorted([*paths, B.NODE]))
                B.verify_source_copy(probe, paths, self.manifest["tools"]["files_sha256"]["node/bin/node"])
                probe = self.exact_container_exec(cid, "/usr/bin/stat", "--format=%s", "--", *sorted(paths))
                B.verify_source_lengths(probe, paths)
                authorization = {"packet_sha256": S.sha(self.raw), "literal_review_sha256": self.reviews["literal"]}
                raw = self.inner.attest(self.manifest, observed, operation, **authorization)
                dispatched = True
                result = self.exact_container_exec(
                    "-i", "--user", "0", cid, "/usr/bin/env", "-i", B.NODE,
                    f"{B.SOURCE}/{self.inner.BASE}/runner.mjs", self.inner.OP_ARG, "--operation", operation,
                    input=raw, timeout=150, allow_fail=True,
                )
                receipt = validate_result(result, self.receipt_validator, self.manifest, observed,
                                          operation, raw, authorization, self.inner)
                if receipt["status"] == "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE":
                    raise S.Held("REPORTED_INNER_CLI_CLOSURE_UNCONFIRMED")
            except BaseException as original:
                if dispatched:
                    self.transport.unknown = True
                    self.report["inner_cli_closure"] = {"node_dispatch_attempted": True, "validated_closed": False}
                    if isinstance(original, InnerRefusal):
                        self.report["inner_cli_closure"]["bounded_terminal_refusal"] = original.receipt
                p._required_safety_first_exception(original, label)
                raise
            self.report.setdefault("migration_results", []).append(receipt)
            p.save()
            p.need(self.receipt_validator.runner_succeeded(receipt), "GENUINE_PRISMA_OPERATION_FAILED")
        return receipt

    def cleanup(self):
        # The accepted probe checks daemon, original create receipts, labels,
        # exact names and final absence. Its own finalizers run independently.
        self.resources.cleanup()
        self.report["cleanup"] = "FULL_CONTAINER_ABSENCE_UNCONFIRMED"
        self.resources.require_daemon(check_image=False)
        if self.docker.container_create_dispatched:
            result = self.docker.run("container", "ls", "-a", "--no-trunc", "--format", "{{.ID}}")
            identities = result.stdout.decode("ascii").splitlines()
            cid = self.resources.cid
            S.require(type(cid) is str and re.fullmatch("[0-9a-f]{64}", cid)
                      and all(re.fullmatch("[0-9a-f]{64}", item) for item in identities)
                      and cid not in identities, "FULL_CONTAINER_ABSENCE_UNCONFIRMED")
        self.report["cleanup_full_container_identity_absent"] = True
        self.report["cleanup"] = "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"
        self.program.event("CONTROLLED_CLEANUP", "PASS", exact_absence=True)
        self.report["steps"]["TWO-HISTORY-CLEANUP"] = "PASS"

    def postchecks(self):
        prepared, raw = read_closed(self.directory / "operation.json")
        S.require(raw == self.raw and prepared[1] == self.operation
                  and exact_reviews(self.directory, self.operation, self.raw) == self.reviews,
                  "CLOUD_OWNING_SOURCE_REVIEW_DRIFT")
        self.report["immutable_source_postcheck"] = "PASS"
        if self.transport.unknown:
            # The stopped runtime and the read-only source recheck have
            # separate outcomes. This preserves uncertainty without
            # reporting invented drift of archive bytes or typed reviews.
            self.report["postcheck_remote_uncertainty_retained"] = True
            if self.report["status"] == "PASS_MACHINERY_SUBSET_ONLY":
                self.program.record_failure("POSTCHECKS", "CLOUD_STICKY_TRANSPORT_UNCERTAINTY")

    def run(self):
        return self.program.main()


def validate_inventory(raw, expected):
    """Prove both copied trees before Node, without recording their raw listing."""
    dirs = {str(parent) for name in expected for parent in PurePosixPath(name).parents
            if str(parent) not in ("/", "/run")}
    files, actual_dirs = {}, set()
    S.require(type(raw) is bytes and 0 < len(raw) <= TREE_INVENTORY_LIMIT
              and raw.isascii() and raw.endswith(b"\n"), "CLOUD_COPIED_INVENTORY_SHAPE")
    for line in raw[:-1].decode("ascii").split("\n"):
        row = line.split("|")
        S.require(len(row) == 7, "CLOUD_COPIED_INVENTORY_SHAPE")
        kind, name, size, uid, gid, mode, links = row
        S.require(uid == gid == "0" and re.fullmatch(r"[0-9]{1,12}", size)
                  and re.fullmatch(r"[1-9][0-9]{0,11}", links)
                  and name not in actual_dirs and name not in files, "CLOUD_COPIED_INVENTORY_METADATA")
        if kind == "d":
            S.require(mode == "755", "CLOUD_COPIED_INVENTORY_METADATA")
            actual_dirs.add(name)
        else:
            S.require(kind == "f" and links == "1" and mode in ("444", "644", "755"),
                      "CLOUD_COPIED_INVENTORY_METADATA")
            files[name] = (int(size), mode)
    S.require(files == expected and actual_dirs == dirs, "CLOUD_COPIED_INVENTORY_DRIFT")
    return {"regular_files": len(files), "directories": len(dirs)}


class InnerRefusal(S.Held):
    def __init__(self, receipt):
        self.receipt = receipt
        super().__init__("CLOUD_INNER_TERMINAL_REFUSAL")


def validate_refusal(value, result, manifest, observed, operation, raw, authorization, inner):
    common = {"schema", "status", "phase", "cause_family", "code", "child_dispatch",
              "operation", "raw_output_discarded", "database_qualification_claimed"}
    phase = value.get("phase")
    S.require(result.returncode == 1 and value.get("status") == "REFUSED_OR_INCOMPLETE"
              and type(phase) is str and phase in REFUSAL_PHASES and value.get("raw_output_discarded") is True
              and value.get("database_qualification_claimed") is False,
              "CLOUD_INNER_REFUSAL_RESPONSE_SHAPE")
    ordinal = REFUSAL_PHASES.index(phase)
    required = {"attestation_sha256": S.sha(raw)} if ordinal >= 2 else {}
    if ordinal >= 3:
        required.update(run_id=manifest["run_id"], container_id=observed["container_id"],
                        daemon_id=observed["daemon"]["daemon_id"], **authorization)
    S.require(set(value) == common | set(required)
              and all(value[name] == wanted for name, wanted in required.items())
              and value["operation"] == (None if ordinal == 0 else operation),
              "CLOUD_INNER_REFUSAL_BINDING")
    cause, code = value["cause_family"], value["code"]
    S.require(type(cause) is str and type(code) is str
              and (code in inner.CLOSED_REFUSAL_PHASE_CODES[phase] if cause == "HELD_GUARD"
                   else inner.REFUSAL_CAUSE_CODES.get(cause) == code)
              and value["child_dispatch"] == ("NOT_ATTEMPTED" if ordinal < 5 else "UNCONFIRMED"),
              "CLOUD_INNER_REFUSAL_RESPONSE_SHAPE")
    # Keep only the approved finite projection. Even the complete echo does
    # not authorize the outer controller to clear descendant uncertainty.
    raise InnerRefusal({
        "phase": phase, "cause_family": cause, "code": code,
        "reported_child_dispatch": value["child_dispatch"],
        "verified_receipt_fields": sorted(required),
        "transport_uncertainty_cleared": False,
    })


def validate_result(result, validator, manifest, observed, operation, raw, authorization, inner):
    S.require(type(result.returncode) is int and result.returncode in (0, 1)
              and result.stderr == b"" and type(result.stdout) is bytes and 1 <= len(result.stdout) <= 65536,
              "CLOUD_RUNNER_RESPONSE")
    value = S.unique_json(result.stdout)
    S.require(type(value) is dict, "CLOUD_RUNNER_RESPONSE")
    if value.get("schema") == inner.REFUSAL_SCHEMA:
        validate_refusal(value, result, manifest, observed, operation, raw, authorization, inner)
    S.require(all(value.get(key) == wanted for key, wanted in authorization.items()),
              "CLOUD_RUNNER_AUTHORIZATION_BINDING")
    parent_result = type(result)(result.returncode, S.encode({
        key: val for key, val in value.items() if key not in authorization
    }), result.stderr)
    B.validate_receipt(parent_result, validator, manifest, observed, operation, raw)
    return value


def interrupt(_signal, _frame):
    raise S.Held("OPERATOR_INTERRUPTED")


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(CONTROL_APPROVAL, action="store_true", dest="execute")
    cli.add_argument("--packet", type=Path, required=True)
    args = cli.parse_args(argv)
    try:
        S.require(args.execute, "EXPLICIT_CLOUD_TWO_EXECUTION_REQUIRED")
        prepared, raw = read_closed(args.packet)
        reviews = exact_reviews(prepared[0], prepared[1], raw)
        os.umask(0o077)
        P.write_new(prepared[0] / "attempt.json", S.encode({
            "run_id": prepared[1]["run_id"], "packet_sha256": S.sha(raw), "reviews": reviews,
        }))
        signal.signal(signal.SIGTERM, interrupt)
        signal.signal(signal.SIGHUP, interrupt)
        return Owner(prepared, raw, reviews).run()
    except BaseException as error:
        print(S.encode({"status": "HELD_OR_STOPPED", "code": safe_code(error),
                        "runtime_pass_claimed": False}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
