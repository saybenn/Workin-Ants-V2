"""Cloud resource and transport adapters for the pinned Customer owning steps."""

import ast
import json
import os
from pathlib import Path, PurePosixPath
import re
import select
import secrets
import subprocess
import time
from types import SimpleNamespace

import prepare
import source7


ROOT = prepare.ROOT
ENDPOINT = "unix:///var/run/docker.sock"
PROFILE_DIR = "scripts/sql-review/cloud-f0-v1"
KERNEL_TMPFS_OPTIONS = "rw,nosuid,nodev,noexec,mode=0700,size=8m"
IMAGE_HELPER = "scripts/sql-review/local_image_identity.py"
IMAGE_MANIFEST = "scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json"
CONTEXT_HELPER = "scripts/sql-review/run-context-control-rehearsal.py"
AUTH_HELPER = "scripts/sql-review/run-first-rehearsal.py"
RESULT_HELPER = "scripts/sql-review/run-local-f0-migrate.py"
PROTOCOL = "scripts/customer_stale_predecessor_v1_protocol.py"
DB = "wa_p0c_rehearsal"
ROLES = ("postgres", "wa_migrator", "wa_context_issuer", "wa_identity_service_authority", "wa_app_runtime", "wa_worker")
POSTGRES_OPTIONS = (
    "-c", "listen_addresses=127.0.0.1", "-c", "password_encryption=scram-sha-256",
    "-c", "log_statement=none", "-c", "log_min_error_statement=panic",
    "-c", "log_error_verbosity=terse", "-c", "log_line_prefix=WA_F0_DIAG|%e|%u|%d|",
    "-c", "lc_messages=C", "-c", "log_min_messages=warning",
)
INITDB = "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256 --locale=C --encoding=UTF8"
COPIED_SOURCE = "/run/wa-f0-source"
COPIED_NODE = "/run/wa-f0-tools/node/bin/node"


def probe_literals(raw):
    wanted = {"KERNEL_PROBE": bytes, "START_CONTROL": str, "WRITE_BOOTSTRAP": str}
    result = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in wanted:
                value = ast.literal_eval(node.value)
                prepare.require(name not in result and type(value) is wanted[name], "CSP_PROBE_LITERAL_SHAPE")
                result[name] = value
    prepare.require(set(result) == set(wanted), "CSP_REQUIRED_PROBE_LITERALS")
    return result


def validate_copied_inventory(raw, files):
    """Check the exact candidate tree through the pinned image's native find."""
    expected_files = {f"{COPIED_SOURCE}/{name}": len(data) for name, data in files.items()}
    expected_dirs = {str(parent) for name in expected_files for parent in PurePosixPath(name).parents
                     if str(parent).startswith(COPIED_SOURCE)}
    actual_files, actual_dirs = {}, set()
    for line in raw.splitlines():
        kind, path, size, uid, gid, mode, links = line.split("|")
        prepare.require(uid == gid == "0" and re.fullmatch("[0-7]{3,4}", mode),
                        "CSP_CLOUD_COPIED_OWNER_OR_MODE")
        if kind == "d":
            prepare.require(path not in actual_dirs and not (int(mode, 8) & 0o7022),
                            "CSP_CLOUD_COPIED_DIRECTORY_MODE")
            actual_dirs.add(path)
        else:
            prepare.require(kind == "f" and mode == "444" and links == "1"
                            and path not in actual_files and re.fullmatch("[0-9]+", size),
                            "CSP_CLOUD_COPIED_FILE_TYPE_OR_MODE")
            actual_files[path] = int(size)
    prepare.require(actual_files == expected_files and actual_dirs == expected_dirs,
                    "CSP_CLOUD_EXACT_COPIED_INVENTORY")


class BoundedInput:
    """Bound the inherited interactive Session's pipe writes and record uncertainty."""

    def __init__(self, stream, uncertain):
        self.stream = stream
        self.uncertain = uncertain
        os.set_blocking(stream.fileno(), False)

    def write(self, text):
        raw = memoryview(text.encode("utf-8"))
        deadline = time.monotonic() + 10
        try:
            if len(raw) > 1024 * 1024:
                raise OSError("CSP_INTERACTIVE_PAYLOAD_LIMIT")
            while raw:
                pending = deadline - time.monotonic()
                if pending <= 0 or not select.select([], [self.stream.fileno()], [], pending)[1]:
                    raise OSError("CSP_INTERACTIVE_WRITE_DEADLINE")
                try:
                    count = os.write(self.stream.fileno(), raw)
                except BlockingIOError:
                    continue
                if count == 0:
                    raise OSError("CSP_INTERACTIVE_WRITE_STOP")
                raw = raw[count:]
        except BaseException:
            self.uncertain("CSP_CLOUD_CHILD_STDIN_UNCONFIRMED")
            raise
        return len(text)

    def flush(self):
        # The descriptor above performs unbuffered writes.
        pass

    def close(self):
        self.stream.close()


class OwnedSessionProcess:
    def __init__(self, process, uncertain):
        self.process = process
        self.uncertain = uncertain
        self.stdin = BoundedInput(process.stdin, uncertain)
        self.stdout = process.stdout
        self.stderr = process.stderr

    @property
    def returncode(self):
        return self.process.returncode

    def poll(self):
        code = self.process.poll()
        if code is not None and not 0 <= code < 125:
            self.uncertain("CSP_CLOUD_CHILD_EXIT_UNCONFIRMED")
        return code

    def wait(self, timeout=None):
        try:
            return self.process.wait(timeout=timeout)
        except BaseException:
            self.uncertain("CSP_CLOUD_CHILD_WAIT_UNCONFIRMED")
            raise

    def terminate(self):
        self.uncertain("CSP_CLOUD_CHILD_TERMINATED")
        self.process.terminate()

    def kill(self):
        self.uncertain("CSP_CLOUD_CHILD_KILLED")
        self.process.kill()


def bind(host, plan, assets, blobs, guard, docker, folder, plan_raw, review_sha):
    v = host.__dict__
    image_source = {"files_sha256": plan["packet_files_sha256"]}
    migration = prepare.parse(assets["migration-manifest.json"])
    arch = folder / "source7.tar.gz"
    manifest_path = folder / "migration-manifest.json"
    fixture = prepare.parse(assets["child/fixtures.json"])
    outcome = folder / "evidence"
    private = outcome / "private"
    reviewed_target = plan["target"]
    name, volume = reviewed_target["container_name"], reviewed_target["volume_name"]
    target = {"container": name, "volume": volume,
              "bootstrap_container_path": reviewed_target["bootstrap_container_path"],
              "labels": reviewed_target["labels"]}
    layout = {**docker.profile, "credential_tmpfs_options": KERNEL_TMPFS_OPTIONS}
    literal = probe_literals(blobs[f"{PROFILE_DIR}/probe.py"])
    bootstrap_path = target["bootstrap_container_path"]
    start = ["-ceu", literal["START_CONTROL"], "wa-cloud-bootstrap", *POSTGRES_OPTIONS]
    labels = [entry for key, value in sorted(target["labels"].items()) for entry in ("--label", f"{key}={value}")]
    child_artifacts = {rel.removeprefix("child/"): prepare.sha(raw) for rel, raw in assets.items() if rel.startswith("child/")}
    source_files = {rel.removeprefix("source7/"): raw for rel, raw in assets.items() if rel.startswith("source7/")}
    v.update({
        "TASK": folder, "ROOT": ROOT, "MANIFEST_PATH": folder / "operation-plan.json",
        "OUT": outcome, "PRIVATE": private, "COMMIT": plan["source_commit"], "TREE": plan["source_tree"],
        "PACKET": plan["packet_sha256"], "IMAGE": source7.IMAGE, "DB": DB, "LABEL": source7.LABEL,
        "RUN_ID": plan["run_id"], "CONNECTION_TAG": "wa-cloud-csp-" + plan["run_id"],
        "ROLES": ROLES, "LEAVES": ("wa_private_helper_owner", "wa_customer_verifier", "wa_track_verifier"),
        "TARGETS": [{"name": name, "volume": volume, "kind": "ok"}],
        "RESOURCE_CONTAINERS": (name,), "RESOURCE_VOLUMES": (volume,),
        "CATALOG": {}, "CSP_STATE": {"admitted": blobs},
        "CSP_FIXTURE_RUN": fixture["fixture_run_id"], "CSP_FIXTURES_SHA": child_artifacts["fixtures.json"],
        "passwords": {}, "secret_paths": [], "all_secrets": [], "created_containers": {},
        "created_volumes": {}, "attempted_containers": set(), "attempted_volumes": set(),
        "bootstrap_attempted": set(), "bootstrapped": set(), "finalization_attempted": set(), "finalized": set(),
    })
    v["MANIFEST"] = {
        **plan, "review_status": "APPROVED_CLOUD_CSP_OWNED_V2",
        "tool_archive": plan["migration_tool_archive"], "tool_archive_sha256": plan["migration_tool_archive_sha256"],
        "migration_targets": {"ok": {
            "manifest_path": str(manifest_path), "manifest_sha256": prepare.sha(assets["migration-manifest.json"]),
            "source_snapshot": str(folder / "source7"), "source_archive": str(arch),
            "source_archive_sha256": prepare.sha(assets["source7.tar.gz"]),
            "source_files_sha256": {rel.removeprefix("source7/"): prepare.sha(raw) for rel, raw in assets.items()
                                    if rel.startswith("source7/")},
        }},
        "customer_stale": {"external_files_sha256": plan["generated_files_sha256"]},
    }
    v["report"] = {
        "schema": "workinants.cloud-customer-stale-predecessor-owned-result.v2",
        "run_id": plan["run_id"], "status": "IN_PROGRESS", "stage": "ENTRY",
        "approved_commit": plan["source_commit"], "approved_tree": plan["source_tree"],
        "approved_packet_sha256": plan["packet_sha256"], "approved_operation_plan_sha256": prepare.sha(plan_raw),
        "daemon": plan["daemon"], "review": "INDEPENDENT_RECEIPT_VERIFIED", "review_sha256": review_sha,
        "evidence_complete": True, "persistence_failure": False, "output_complete": True,
        "steps": dict.fromkeys(
            ("CATALOG-SETUP", "CATALOG-AUTH", "CATALOG-TOOLS", "CATALOG-INSTALL",
             "CATALOG-ACL-COMPAT", "CATALOG-TEXT-COMPAT", "CATALOG-NATIVE", "CATALOG-ORACLE",
             "CATALOG-LEDGER", "CATALOG-COMPARE", "CATALOG-SANITIZED_EXPORT", "CATALOG-CLEANUP",
             "CSP1-REVIEW", "CSP1-COMPONENT"), "NOT_RUN"
        ),
        "events": [], "targets": {}, "unexpected": [], "cleanup": {},
        "customer_stale": {"prepared_protocols": 3, "selected_assertions": "NOT_RUN", "owner_api_policy_qualified": False},
        "limits": {"posture": "D", "hosted_changes": False, "migration_adoption": False,
                   "whole_case_promoted": False, "independent_evidence_admission": "PENDING"},
        "transport_closure": {"transport_closure_unconfirmed": False, "first_unconfirmed_closure": None},
    }
    need = host.need
    expected_prefix_length = len(docker.argv())
    original_binary = host.binary_process
    original_cleanup = host.cleanup

    def docker_arguments(args):
        return args[:expected_prefix_length] == docker.argv()

    def owned_exec(args):
        if not docker_arguments(args):
            return False
        coordinates = args[expected_prefix_length:]
        return coordinates[:1] == ["exec"] and any(
            len(cid) == 64 and cid in coordinates[1:] for cid in host.created_containers.values()
        )

    def binary_process(args, *parameters, env=None, **options):
        need(docker_arguments(args), "CSP_CLOUD_COMMAND_BOUNDARY")
        extra = {} if env is None else env
        need(type(extra) is dict and set(extra) <= {"PGPASSWORD"}
             and all(re.fullmatch("[a-f0-9]{64}", value) for value in extra.values()),
             "CSP_CLOUD_WRONG_PASSWORD_ONLY")
        result = original_binary(args, *parameters, env={**docker.env, **extra}, **options)
        need(docker_arguments(args), "CSP_CLOUD_DOCKER_SOCKET_CHANGED")
        if owned_exec(args) and not 0 <= result.returncode < 125:
            state = host.report["transport_closure"]
            state.update(transport_closure_unconfirmed=True, remote_exec_exit_unconfirmed=True)
            host.remember_failure(host.report["stage"], "CSP_CLOUD_EXEC_EXIT_UNCONFIRMED")
            raise host.Stop("CSP_CLOUD_EXEC_EXIT_UNCONFIRMED")
        return result

    def command(args, stdin=None, timeout=60):
        raw = binary_process(args, None if stdin is None else stdin.encode("utf-8"), timeout)
        return subprocess.CompletedProcess(
            args, raw.returncode, host.strict_process_text(raw.stdout), host.strict_process_text(raw.stderr)
        )

    def docker_run(args, input=None, timeout=60):
        return command(docker.argv(*args), input, timeout)

    def psql_for_cid(role, cid, wrong_password=False, diagnostic=True):
        need(cid == host.created_containers.get(name) and re.fullmatch("[a-f0-9]{64}", cid)
             and role in ROLES, "CSP_CLOUD_EXACT_PSQL_COORDINATES")
        credentials = (["-e", "PGPASSFILE=/dev/null", "-e", "PGPASSWORD"] if wrong_password
                       else ["-e", "PGPASSFILE=/run/wa-secrets/pgpass"])
        return docker.argv("exec", "-i", *credentials, "-e", "PGSSLMODE=disable", "-e", "PGGSSENCMODE=disable",
                           "-e", "PGAPPNAME=" + host.CONNECTION_TAG, cid,
                           "psql", "-X", "-w", "-qAt", "-v", "ON_ERROR_STOP=1", "-v", "VERBOSITY=verbose",
                           "-v", "SHOW_CONTEXT=" + ("errors" if diagnostic else "never"), "-h", "127.0.0.1",
                           "-p", "5432", "-U", role, "-d", DB)

    def psql_args(target_name, role):
        need(target_name == name, "CSP_CLOUD_PSQL_TARGET")
        return psql_for_cid(role, host.created_containers[name], diagnostic=False)

    def fresh_daemon():
        need(docker.observe() == plan["daemon"], "CSP_CLOUD_DAEMON_CHANGED")

    def preflight():
        fresh_daemon()
        containers, volumes = host.inventory()
        need(name not in containers and volume not in volumes, "CSP_CLOUD_RESOURCE_NAME_CONFLICT")
        host.report["local_preflight"] = {"endpoint": ENDPOINT, "daemon": plan["daemon"],
                                          "target_name_absent": True, "volume_name_absent": True}
        host.event("CLOUD_PREFLIGHT", "PASS_EXACT_LOCAL_DAEMON")

    def ensure_image():
        fresh_daemon()
        try:
            identity = docker.cached_image(image_source)
        except guard.Stop as failure:
            raise host.Stop("CSP_CLOUD_PINNED_IMAGE_REFUSED") from failure
        host.report["image"] = identity
        host.event("CLOUD_PINNED_IMAGE", "PASS", image_id=identity["image_id"])

    def inspect_owner(target_name, running=True):
        need(target_name == name, "CSP_CLOUD_OWNED_NAME")
        fresh_daemon()
        cid = host.created_containers[name]
        data = host.inspect_container(name)
        disk = host.inspect_volume(volume)
        need(data is not None and disk is not None, "CSP_CLOUD_OWNED_RESOURCES_MISSING")
        guard.verify_volume(disk, target, host.created_volumes[volume])
        guard.verify_container(data, layout, target, disk, cid, host.report["image"]["image_id"], running)
        need(data["Config"]["Entrypoint"] == ["/bin/sh"] and data["Config"]["Cmd"] == start,
             "CSP_CLOUD_EXACT_START_CONTROL")
        env = data["Config"]["Env"]
        need(env.count(f"POSTGRES_PASSWORD_FILE={bootstrap_path}") == 1
             and env.count(INITDB) == 1 and not any(entry.startswith("POSTGRES_PASSWORD=") for entry in env),
             "CSP_CLOUD_BOOTSTRAP_ENVIRONMENT")
        if running:
            result = binary_process(docker.argv("exec", "-i", cid, "sh", "-s"), literal["KERNEL_PROBE"], 30)
            need(result.returncode == 0 and result.stdout == b"cloud-private-mount-and-loopback\n" and result.stderr == b"",
                 "CSP_CLOUD_KERNEL_ISOLATION")
        host.event("CLOUD_OWNERSHIP", "PASS", running=running, image_id=data["Image"])
        return data

    def ready():
        cid = host.created_containers[name]
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            result = docker_run(["exec", cid, "pg_isready", "-q", "-h", "127.0.0.1", "-p", "5432",
                                 "-t", "1", "-U", "postgres", "-d", DB], timeout=5)
            if result.returncode == 0:
                return
            time.sleep(0.25)
        raise host.Stop("CSP_CLOUD_SERVER_READY_UNCONFIRMED")

    def exact_call(args, code, input=None, timeout=30, output=""):
        result = docker_run(args, input, timeout)
        need(result.returncode == 0 and result.stderr == "" and (output is None or result.stdout == output), code)

    def bootstrap_absent():
        cid = host.created_containers[name]
        exact_call(["exec", cid, "sh", "-ceu", 'test ! -e "$1" && test ! -L "$1"', "sh", bootstrap_path],
                   "CSP_CLOUD_BOOTSTRAP_ABSENCE")

    def copied_runtime_preflight(cid):
        inventory = docker_run(["exec", cid, "/usr/bin/find", COPIED_SOURCE,
                                "-maxdepth", "12", "-printf", "%y|%p|%s|%U|%G|%m|%n\\n"], timeout=30)
        need(inventory.returncode == 0 and inventory.stderr == "" and len(inventory.stdout) <= 16384,
             "CSP_CLOUD_COPIED_INVENTORY_UNCONFIRMED")
        try:
            validate_copied_inventory(inventory.stdout, source_files)
        except (ValueError, TypeError):
            raise host.Stop("CSP_CLOUD_COPIED_INVENTORY_UNCONFIRMED") from None
        lines = "".join(f"{prepare.sha(data)}  {COPIED_SOURCE}/{relative}\n"
                        for relative, data in sorted(source_files.items()))
        lines += f"{migration['tools']['files_sha256']['node/bin/node']}  {COPIED_NODE}\n"
        exact_call(["exec", "-i", cid, "/usr/bin/sha256sum", "--check", "--strict", "--status"],
                   "CSP_CLOUD_COPIED_RUNTIME_CHANGED", lines)
        exact_call(["exec", cid, "/usr/bin/stat", "--printf", "%u:%g:%a:%h:%s", "--", COPIED_NODE],
                   "CSP_CLOUD_COPIED_NODE_IDENTITY",
                   output=f"0:0:755:1:{migration['tools']['file_sizes']['node/bin/node']}")
        host.report["copied_runtime_preflight"] = {
            "checked": len(source_files), "node_verified": True, "immutable_container_id": cid,
            "source_map_sha256": prepare.sha(prepare.encode(host.MANIFEST["migration_targets"]["ok"]["source_files_sha256"])),
        }
        host.save()

    def create_resources():
        fresh_daemon()
        containers, volumes = host.inventory()
        need(name not in containers and volume not in volumes, "CSP_CLOUD_LATE_RESOURCE_CONFLICT")
        host.passwords[name] = {role: secrets.token_hex(32) for role in ROLES}
        host.all_secrets.extend(host.passwords[name].values())
        host.attempted_volumes.add(volume)
        exact_call(["volume", "create", "--driver", "local", *labels, volume], "CSP_CLOUD_VOLUME_CREATE",
                   output=volume + "\n")
        disk = host.inspect_volume(volume)
        host.created_volumes[volume] = guard.verify_volume(disk, target)
        host.report["created_volume"] = {"name": volume, "labels": target["labels"], "created_at": disk["CreatedAt"]}
        host.save()
        host.attempted_containers.add(name)
        command = [
            "container", "create", "--pull", "never", "--platform", "linux/amd64", "--network", "none",
            "--restart", "no", "--log-driver", "none", "--name", name, *labels,
            "--mount", f"type=volume,src={volume},dst={layout['data_mount']}",
            "--tmpfs", layout["credential_tmpfs"] + ":" + layout["credential_tmpfs_options"],
            "-e", f"POSTGRES_DB={DB}", "-e", f"POSTGRES_PASSWORD_FILE={bootstrap_path}",
            "-e", "POSTGRES_HOST_AUTH_METHOD=scram-sha-256", "-e", INITDB,
            "--entrypoint", "/bin/sh", layout["database_image"], *start,
        ]
        result = docker_run(command, timeout=30)
        cid = result.stdout.strip()
        need(result.returncode == 0 and result.stderr == "" and re.fullmatch("[a-f0-9]{64}", cid),
             "CSP_CLOUD_CONTAINER_CREATION_RECEIPT")
        host.created_containers[name] = cid
        host.report["targets"][name] = {"container_id": cid, "volume": volume,
                                        "volume_created_at": disk["CreatedAt"], "labels": target["labels"],
                                        "network_mode": "none", "published_ports": False,
                                        "bootstrap": "NOT_RUN", "application": "NOT_RUN", "finalization": "NOT_RUN"}
        host.save()
        inspect_owner(name, running=False)
        exact_call(["container", "start", cid], "CSP_CLOUD_CONTAINER_START", output=None)
        inspect_owner(name)
        exact_call(["exec", "-i", cid, "sh", "-ceu", literal["WRITE_BOOTSTRAP"]],
                   "CSP_CLOUD_BOOTSTRAP_TRANSPORT", host.passwords[name]["postgres"] + "\n")
        ready()
        exact_call(["exec", cid, "cat", "/proc/1/comm"], "CSP_CLOUD_SERVER_PID_ONE", output="postgres\n")
        exact_call(["exec", cid, "rm", "--", bootstrap_path], "CSP_CLOUD_BOOTSTRAP_UNLINK")
        bootstrap_absent()
        pgpass = "".join(f"127.0.0.1:5432:{DB}:{role}:{password}\n"
                         for role, password in host.passwords[name].items())
        exact_call(["exec", "-i", cid, "sh", "-ceu",
                    'umask 077; set -C; cat > /run/wa-secrets/pgpass; stat -c "%u:%g:%a:%h" /run/wa-secrets/pgpass'],
                   "CSP_CLOUD_PGPASS_MODE", pgpass, output="0:0:600:1\n")
        host.report["steps"]["CATALOG-SETUP"] = "PASS"
        host.report["bootstrap_removed_in_container"] = True
        host.event("RESOURCE_READY", "PASS_BOUND_PRIVATE_BOOTSTRAP")

    def migrate(checked_target, operation, stage, proof=None):
        need(checked_target == host.TARGETS[0] and operation == "deploy" and proof is None,
             "CSP_CLOUD_SINGLE_DEPLOY_ONLY")
        need(not host.report.get("migration_attempted"), "CSP_CLOUD_SINGLE_DEPLOY_ONLY")
        host.report["stage"] = stage
        inspect_owner(name)
        bootstrap_absent()
        host.report["stage"] = stage
        cid = host.created_containers[name]
        copied_runtime_preflight(cid)
        observed = {
            **reviewed_target, "endpoint": ENDPOINT, "daemon": plan["daemon"], "container_id": cid,
            "volume_created_at": host.created_volumes[volume], "image_id": host.report["image"]["image_id"],
            "published_ports": False, "bootstrap_file_absent": True, "private_tmpfs_verified": True,
        }
        observed.pop("database")
        attestation = prepare.encode({
            "schema": "workinants.cloud-csp-initial-live-attestation.v2",
            "planned": migration, "operation": "deploy", "observed": observed,
            "run_manifest_sha256": prepare.sha(assets["migration-manifest.json"]),
        })
        host.report["migration_attempted"] = True
        host.save()
        try:
            args = docker.argv("exec", "-i", cid, COPIED_NODE, COPIED_SOURCE + "/" + source7.RUNNER,
                               source7.OPERATION_FLAG, "--operation", "deploy")
            result = binary_process(args, attestation, 150, output_limit=65536)
            candidate = prepare.parse(result.stdout)
            need(type(candidate) is dict and result.stderr == b""
                 and candidate.pop("daemon_id", None) == plan["daemon"]["daemon_id"],
                 "CSP_CLOUD_INNER_DAEMON_RECEIPT")
            validator = host.load_reviewed_helper(RESULT_HELPER)
            value = validator["safe_result"](prepare.encode(candidate).decode("utf-8"), migration, observed, operation)
            need(value["attestation_sha256"] == prepare.sha(attestation)
                 and result.returncode == (0 if validator["runner_succeeded"](value) else 1),
                 "CSP_CLOUD_INNER_ATTESTATION_RECEIPT")
            if value["exit_code"] is None:
                host.csp_latch_inner_uncertainty(stage, "VALIDATED_NULL_EXIT")
                raise host.Stop("CSP_CLOUD_INNER_CLIENT_CLOSURE_UNKNOWN")
            need(type(value["exit_code"]) is int and 0 <= value["exit_code"] < 125,
                 "CSP_CLOUD_INNER_CLIENT_CLOSURE_UNKNOWN")
        except BaseException as error:
            code = error.code if isinstance(error, host.Stop) else "CSP_CLOUD_INNER_RECEIPT_INVALID"
            host.remember_failure(stage, code)
            host.csp_latch_inner_uncertainty(stage, "NO_VALIDATED_INNER_EXIT_RECEIPT")
            raise host.Stop(code) from None
        host.report["migration_operations"] = [{
            "target": name, "stage": stage, "status": value["status"], "exit_code": value["exit_code"],
            "attestation_sha256": value["attestation_sha256"], "inner_terminal_receipt": True,
        }]
        host.save()
        need(result.returncode == value["exit_code"] == 0
             and value["status"] == "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS"
             and value["no_pending_message_observed"] is False and value["prisma_codes"] == value["sqlstates"] == [],
             "CSP_CLOUD_INITIAL_DEPLOY_FAILED")
        return value

    def verify_tool_data():
        pinned = prepare.parse(blobs[prepare.CLOSURE])
        source_data = plan["catalog"]["tool_source_files_sha256"]
        need(set(source_data) == host.TOOL_DATA
             and all(migration["tools"]["files_sha256"][rel] == pinned["tools_files_sha256"][rel] == digest
                     for rel, digest in source_data.items()), "CSP_CLOUD_TOOL_SOURCE_BINDING")

    def check_assets():
        for rel, raw in assets.items():
            need(prepare.stable_file(folder / rel) == raw, "CSP_CLOUD_PREPARED_ASSET_CHANGED")

    def verify_common_packet():
        check_assets()
        host.report["source_verification"] = {"commit": plan["source_commit"], "tree": plan["source_tree"],
                                               "files_sha256": plan["packet_files_sha256"],
                                               "packet_sha256": plan["packet_sha256"]}
        host.event("SOURCE_VERIFICATION", "PASS_COMMITTED_AND_PREPARED_BYTES", files=len(blobs))

    def child_run(args, *, input, text, capture_output, timeout, shell):
        need(owned_exec(args) and text is True and capture_output is True and shell is False,
             "CSP_CLOUD_CHILD_PSQL_PROFILE")
        return command(args, input, timeout)

    def child_spawn(args, **options):
        need(owned_exec(args) and options == {
            "stdin": subprocess.PIPE, "stdout": subprocess.PIPE, "stderr": subprocess.PIPE,
            "text": True, "bufsize": 1, "shell": False,
        }, "CSP_CLOUD_CHILD_SESSION_PROFILE")
        def uncertain(code):
            host.report["transport_closure"]["transport_closure_unconfirmed"] = True
            host.report["transport_closure"]["remote_exec_exit_unconfirmed"] = True
            host.remember_failure(host.report["stage"], code)
            host.persist_best_effort("CSP_CLOUD_CHILD_UNCERTAINTY")
        # The inherited Session verifies concrete terminal status and exact
        # backend disappearance before its result is used.
        process = None
        try:
            process = subprocess.Popen(args, env=docker.env, encoding="utf-8", **options)
            return OwnedSessionProcess(process, uncertain)
        except BaseException:
            uncertain("CSP_CLOUD_CHILD_SPAWN_OR_PIPE_UNCONFIRMED")
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            raise

    def verify_csp_packet():
        host.verify_catalog_packet()
        module = host.load_reviewed_helper(prepare.CHILD_CORE)
        ctx = host.load_reviewed_helper(CONTEXT_HELPER)
        protocol = host.load_reviewed_helper(PROTOCOL)
        ctx["load_helpers"]({rel: blobs[rel] for rel in ctx["SOURCE_MODULES"]})
        ctx["API"]["psql"] = psql_for_cid
        module["subprocess"] = SimpleNamespace(run=child_run)
        ctx["subprocess"] = SimpleNamespace(Popen=child_spawn, TimeoutExpired=subprocess.TimeoutExpired,
                                            PIPE=subprocess.PIPE)
        protocol["source_guard"](blobs[source7.APPLICATION])
        need(fixture["status"] == "NOT_RUN" and fixture["database_posture"] == "D"
             and fixture["database_contacted"] is False and fixture["sql_executed"] is False
             and fixture["case_order"] == list(protocol["CASE_ORDER"])
             and fixture["fixture_run_id"] == plan["fixture_run_id"], "CSP_CLOUD_CHILD_FIXTURE")
        sql = {leaf: assets[f"child/{leaf}"].decode("utf-8") for leaf in fixture["prepared_files_sha256"]}
        need(fixture["prepared_files_sha256"] == {
            key: prepare.sha(value.encode("utf-8")) for key, value in sql.items()
        }, "CSP_CLOUD_CHILD_EXACT_SQL")
        safe_codes = set()
        for rel in (*ctx["SOURCE_MODULES"], prepare.CHILD_CORE, PROTOCOL):
            if rel.endswith(".py"):
                safe_codes.update(node.value for node in ast.walk(ast.parse(blobs[rel]))
                                  if isinstance(node, ast.Constant) and type(node.value) is str
                                  and re.fullmatch("[A-Z][A-Z0-9_]{0,95}", node.value))
        host.CSP_STATE.update(child_module=module, child_admission=(fixture, sql, blobs, ctx, protocol),
                              safe_codes=safe_codes, child_artifact_hashes=child_artifacts)
        host.SAFE_FILES.update({
            "customer-stale-native-attestation.json", "customer-stale-run-plan.json",
            "customer-stale-component-summary.json", "post-state-before.json", "post-state-after.json",
            "post-native-before.json", "post-native-after-oracle.json", "post-native-after-ledger.json",
            "post-oracle-evidence.json", "post-ledger-observation.json", "post-ledger-evidence.json",
            "post-catalog-comparison.json", "post-oracle-preflight.json", "post-oracle-results.json",
            "post-oracle-closure.json",
        })
        host.report["steps"]["CSP1-REVIEW"] = "PASS_REVIEWED_CLOUD_SOURCE_ONLY"
        host.report["customer_stale"]["fixture_run_id"] = fixture["fixture_run_id"]
        host.save()

    def verify_external_input_preservation():
        check_assets()
        tools = source7.shared(ROOT)["inspect_tools"](ROOT, Path(plan["migration_tool_archive"]))
        need(tools == migration["tools"], "CSP_CLOUD_TOOL_ARCHIVE_CHANGED")

    def cleanup():
        if host.attempted_containers or host.attempted_volumes:
            fresh_daemon()
        original_cleanup()
        cid = host.created_containers.get(name)
        if cid is not None:
            exact_call(["container", "ls", "-aq", "--no-trunc", "--filter", "id=" + cid],
                       "CSP_CLOUD_CLEANUP_EXACT_ID_ABSENCE")
        host.report["cloud_cleanup"] = {"container_id_absent": True if cid is not None else None, "container_name_absent": True,
                                         "volume_absent": True, "host_secret_files_created": False}
        host.save()

    original_load = host.load_reviewed_helper

    def load_reviewed_helper(relative):
        module = original_load(relative)
        if relative == AUTH_HELPER:
            module["psql"] = psql_for_cid
        return module

    v.update({
        "binary_process": binary_process, "command": command, "docker": docker_run,
        "_csp_authorized_remote_exec": owned_exec, "psql_args": psql_args,
        "preflight": preflight, "ensure_image": ensure_image, "create_resources": create_resources,
        "inspect_owner": inspect_owner, "migrate": migrate, "verify_tool_data": verify_tool_data,
        "verify_common_packet": verify_common_packet, "verify_csp_packet": verify_csp_packet,
        "verify_external_input_preservation": verify_external_input_preservation, "cleanup": cleanup,
        "load_reviewed_helper": load_reviewed_helper,
    })
    return host
