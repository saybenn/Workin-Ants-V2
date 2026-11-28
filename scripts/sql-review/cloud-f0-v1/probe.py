"""Prepare and run the independently reviewed Cloud F0 capability probe."""

import argparse
import datetime
import os
from pathlib import Path
import re
import secrets
import signal
import subprocess
import sys
import time
import uuid

from guard import (
    BASE, ROOT, Docker, Stop, encode, file_from_snapshot, parse, private_directory,
    private_file, require, sha256, source_snapshot, stable_file, verify_container, verify_volume,
)


DATABASE = "wa_f0_cloud_probe"
LIMITED = "wa_probe_limited"
PURPOSE = "CLOUD_F0_CAPABILITY_PROBE_ONLY"
REVIEW_SCHEMA = "workinants.cloud-f0-literal-review.v1"
PLAN_SCHEMA = "workinants.cloud-f0-capability-plan.v1"
RESULT_SCHEMA = "workinants.cloud-f0-capability-result.v1"
APPROVALS = [
    "exact_committed_sources_and_tooling",
    "local_image_daemon_and_mounts",
    "synthetic_scram_roles_and_transactions",
    "controlled_crash_and_exact_cleanup",
]

KERNEL_PROBE = b"""
set -eu
refuse() { printf '%s\n' "$1"; exit 42; }
test "$(stat -c '%u:%g:%a' /run/wa-secrets)" = '0:0:700' || refuse SECRET_TMPFS_METADATA
test "$(stat -c '%u:%a' /run/bootstrap-password)" = '0:600' || refuse BOOTSTRAP_FILE_METADATA
awk '$5 == "/run/wa-secrets" {
  if ($6 ~ /(^|,)rw(,|$)/ && $6 ~ /(^|,)nodev(,|$)/ &&
      $6 ~ /(^|,)nosuid(,|$)/ && $6 ~ /(^|,)noexec(,|$)/ && $0 ~ / - tmpfs /) n++
}
END { exit n != 1 }' /proc/self/mountinfo || refuse SECRET_TMPFS_KERNEL_FLAGS
awk -F: 'NR > 2 { gsub(/ /, "", $1); if ($1 != "lo") exit 1; n++ }
END { if (n != 1) exit 1 }' /proc/net/dev || refuse KERNEL_NETWORK_INTERFACES
awk '$5 == "/run/bootstrap-password" && $6 ~ /(^|,)ro(,|$)/ { n++ }
END { exit n != 1 }' /proc/self/mountinfo || refuse BOOTSTRAP_BIND_KERNEL_FLAGS
printf 'cloud-private-mount-and-loopback\n'
"""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_new(path, raw):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


def get_profile(source):
    return parse(file_from_snapshot(f"{BASE}/profile.json", source))


def packet_directory(profile, run_id):
    parsed = uuid.UUID(run_id)
    require(parsed.version == 4 and str(parsed) == run_id, "INVALID_RUN_ID")
    return Path(profile["scratch_root"]) / f"wa-cloud-f0-probe-{run_id}"


def target_for(packet, run_id):
    name = f"wa-p0c-cloud-probe-{run_id}"
    return {"container": name, "volume": name + "-data", "database": DATABASE,
            "bootstrap_file": str(packet / "private" / "bootstrap"),
            "labels": {"workinants.rehearsal": "p0c-cloud-f0-probe-v1",
                       "workinants.rehearsal.run": run_id}}


def new_client_config(packet):
    config = packet / "docker-client"
    config.mkdir(mode=0o700)
    # A private empty client config prevents injection of CLI proxy variables
    # when creating an offline container. The image must already be cached.
    write_new(config / "config.json", b"{}\n")
    return config


def docker_for(profile, packet):
    config = packet / "docker-client"
    private_file(config / "config.json")
    require(stable_file(config / "config.json") == b"{}\n", "DOCKER_CLIENT_CONFIG_DRIFT")
    return Docker(profile, config)


def prepare():
    source = source_snapshot()
    profile = get_profile(source)
    run_id = str(uuid.uuid4())
    packet = packet_directory(profile, run_id)
    packet.mkdir(mode=0o700)
    private_directory(packet)
    new_client_config(packet)
    docker = docker_for(profile, packet)
    target = target_for(packet, run_id)
    containers, volumes = docker.names()
    require(target["container"] not in containers and target["volume"] not in volumes,
            "TARGET_NAMES_IN_USE")
    manifest = {"schema": PLAN_SCHEMA, "purpose": PURPOSE, "run_id": run_id,
                "source": source, "target": target, "daemon": docker.observe(),
                "cached_image": docker.cached_image(source),
                "database_cases": ["scram_correct_and_wrong_password", "restricted_select_and_write_denial",
                                   "two_connections", "container_crash_and_transaction_recovery"],
                "candidate_migrations": False, "assertion_promotions": 0}
    raw = encode(manifest)
    write_new(packet / "manifest.json", raw)
    print(encode({"manifest": str(packet / "manifest.json"), "sha256": sha256(raw)}).decode(), end="")


def read_plan(path):
    private_file(path)
    raw = stable_file(path)
    manifest = parse(raw)
    require(manifest["schema"] == PLAN_SCHEMA and manifest["purpose"] == PURPOSE
            and manifest["candidate_migrations"] is False and manifest["assertion_promotions"] == 0
            and manifest["database_cases"] == [
                "scram_correct_and_wrong_password", "restricted_select_and_write_denial",
                "two_connections", "container_crash_and_transaction_recovery"],
            "MANIFEST_SCOPE")
    source = source_snapshot()
    require(manifest["source"] == source, "MANIFEST_SOURCE_DRIFT")
    profile = get_profile(source)
    packet = packet_directory(profile, manifest["run_id"])
    require(path == packet / "manifest.json", "MANIFEST_LOCATION")
    private_directory(packet)
    require(manifest["target"] == target_for(packet, manifest["run_id"]), "MANIFEST_TARGET_DRIFT")
    return raw, manifest, profile, packet


def read_review(path, manifest_raw):
    private_file(path)
    raw = stable_file(path)
    review = parse(raw)
    require(set(review) == {"schema", "decision", "reviewer", "manifest_sha256", "checks"}
            and review["schema"] == REVIEW_SCHEMA and review["decision"] == "APPROVE"
            and type(review["reviewer"]) is str and re.fullmatch(r"[a-zA-Z0-9_/-]{1,80}", review["reviewer"])
            and review["manifest_sha256"] == sha256(manifest_raw)
            and review["checks"] == APPROVALS, "EXACT_LITERAL_REVIEW_REQUIRED")
    return review["reviewer"], sha256(raw)


def refusal(raw, role):
    marker = ('password authentication failed for user "' + role + '"').encode()
    return raw.startswith(b"psql: error: connection to server at \"127.0.0.1\"") and raw.count(marker) == 1


class Probe:
    def __init__(self, manifest, profile, packet, docker, report):
        self.manifest = manifest
        self.profile = profile
        self.packet = packet
        self.docker = docker
        self.report = report
        self.target = manifest["target"]
        self.secret = Path(self.target["bootstrap_file"])
        self.cid = None
        self.volume_birth = None
        self.secret_identity = None
        self.background = None
        self.attempted = False
        self.remote_unknown = False

    def require_daemon(self, check_image=True):
        require(self.docker.observe() == self.manifest["daemon"], "MANIFEST_DAEMON_DRIFT")
        if check_image:
            require(self.docker.cached_image(self.manifest["source"]) == self.manifest["cached_image"],
                    "MANIFEST_IMAGE_DRIFT")

    def require_absent(self):
        containers, volumes = self.docker.names()
        require(self.target["container"] not in containers and self.target["volume"] not in volumes,
                "TARGET_ABSENCE_UNCONFIRMED")

    def own_container(self):
        require(self.cid is not None, "CONTAINER_ID_UNCONFIRMED")
        value = self.docker.inspect("container", self.cid)
        require(value.get("Id") == self.cid and value.get("Name") == "/" + self.target["container"]
                and value.get("Config", {}).get("Labels") == self.target["labels"],
                "CLEANUP_CONTAINER_OWNERSHIP")
        return value

    def check_target(self, running):
        data = self.own_container()
        volume = self.docker.inspect("volume", self.target["volume"])
        verify_volume(volume, self.target, self.volume_birth)
        verify_container(data, self.profile, self.target, volume, self.cid,
                         self.manifest["cached_image"]["image_id"], running)
        require(private_file(self.secret) == self.secret_identity, "BOOTSTRAP_FILE_DRIFT")
        if running:
            status = self.docker.run("exec", "-i", self.cid, "sh", "-s", stdin=KERNEL_PROBE,
                                     operation="KERNEL_ISOLATION")
            require(status.stdout == b"cloud-private-mount-and-loopback\n", "KERNEL_ISOLATION_UNCONFIRMED")
        return data

    def provision(self, bootstrap_password):
        self.require_daemon()
        self.require_absent()
        self.secret.parent.mkdir(mode=0o700)
        write_new(self.secret, (bootstrap_password + "\n").encode())
        self.secret_identity = private_file(self.secret)
        labels = [arg for k, v in sorted(self.target["labels"].items()) for arg in ("--label", k + "=" + v)]
        self.attempted = True
        result = self.docker.run("volume", "create", "--driver", "local", *labels, self.target["volume"])
        require(result.stdout == (self.target["volume"] + "\n").encode(), "VOLUME_CREATION_RECEIPT")
        volume = self.docker.inspect("volume", self.target["volume"])
        self.volume_birth = verify_volume(volume, self.target)
        self.report["volume_created_at"] = self.volume_birth
        write_new(self.packet / "created-volume.json", encode({
            "name": self.target["volume"], "labels": self.target["labels"],
            "created_at": self.volume_birth, "run_id": self.manifest["run_id"],
        }))
        p = self.profile
        data_mount = f"type=volume,src={self.target['volume']},dst={p['data_mount']}"
        secret_mount = f"type=bind,src={self.secret},dst={p['bootstrap_mount']},readonly"
        result = self.docker.run(
            "container", "create", "--pull", "never", "--platform", "linux/amd64", "--network", "none",
            "--restart", "no", "--log-driver", "none", "--name", self.target["container"], *labels,
            "--mount", data_mount, "--mount", secret_mount, "--tmpfs",
            p["credential_tmpfs"] + ":" + p["credential_tmpfs_options"],
            "-e", "POSTGRES_DB=" + DATABASE, "-e", "POSTGRES_PASSWORD_FILE=" + p["bootstrap_mount"],
            "-e", "POSTGRES_HOST_AUTH_METHOD=scram-sha-256",
            "-e", "POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256 --locale=C --encoding=UTF8",
            p["database_image"], "-c", "listen_addresses=127.0.0.1", "-c", "log_statement=none",
            "-c", "log_min_error_statement=panic", "-c", "log_error_verbosity=terse", timeout=30,
        )
        cid = result.stdout.decode().strip()
        require(re.fullmatch(r"[0-9a-f]{64}", cid), "CONTAINER_CREATION_RECEIPT")
        self.cid = cid
        self.report["container_id"] = cid
        self.own_container()
        write_new(self.packet / "created-container.json", encode({
            "id": cid, "name": self.target["container"], "labels": self.target["labels"],
            "run_id": self.manifest["run_id"],
        }))
        self.check_target(False)
        self.docker.run("container", "start", self.cid, timeout=30, operation="FIRST_START")
        self.wait_ready()
        self.check_target(True)
        self.report["checks"].append("exact_mounts_loopback_and_cache")

    def wait_ready(self):
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            result = self.docker.run("exec", self.cid, "pg_isready", "-q", "-h", "127.0.0.1",
                                     "-p", "5432", "-t", "1", "-U", "postgres", "-d", DATABASE,
                                     timeout=5, allow_fail=True)
            if result.returncode == 0:
                return
            time.sleep(0.25)
        raise Stop("SERVER_READY_UNCONFIRMED")

    def password_files(self, admin, limited, wrong):
        args = ["exec", "-i", self.cid, "sh", "-ceu",
                "umask 077; set -C; cat > \"$1\"; test \"$(stat -c %u:%a \"$1\")\" = 0:600",
                "sh"]
        for name, values in (("correct", (admin, limited)), ("wrong", (wrong, wrong))):
            contents = "".join(f"127.0.0.1:5432:{DATABASE}:{role}:{password}\n"
                               for role, password in zip(("postgres", LIMITED), values))
            self.docker.run(*args, f"/run/wa-secrets/{name}.pgpass", stdin=contents.encode())

    def psql(self, role, password="correct", name="wa-cloud-f0-probe"):
        require(role in ("postgres", LIMITED) and password in ("correct", "wrong"),
                "UNREGISTERED_PSQL_PROFILE")
        return ("exec", "-i", "-e", f"PGPASSFILE=/run/wa-secrets/{password}.pgpass",
                "-e", "PGSSLMODE=disable", "-e", "PGGSSENCMODE=disable", "-e", f"PGAPPNAME={name}",
                self.cid, "psql", "-X", "-w", "-qAt", "-v", "ON_ERROR_STOP=1",
                "-v", "VERBOSITY=sqlstate", "-v", "SHOW_CONTEXT=never",
                "-h", "127.0.0.1", "-p", "5432", "-d", DATABASE, "-U", role)

    def query(self, role, sql, expected):
        result = self.docker.run(*self.psql(role), stdin=sql.encode(), operation="DATABASE_QUERY")
        require(result.stdout == expected.encode(), "UNEXPECTED_DATABASE_RESULT")

    def check_auth(self, roles):
        for role in roles:
            self.query(role, "SELECT session_user || '|' || system_user || '|' || "
                       "host(inet_client_addr()) || '|' || host(inet_server_addr());",
                       f"{role}|scram-sha-256:{role}|127.0.0.1|127.0.0.1\n")
            wrong = self.docker.run(*self.psql(role, "wrong"), stdin=b"SELECT 1;",
                                    allow_fail=True)
            require(wrong.returncode == 2 and not wrong.stdout and refusal(wrong.stderr, role),
                    "WRONG_PASSWORD_REJECTION_UNCONFIRMED")

    def check_database(self, admin, limited, wrong):
        self.password_files(admin, limited, wrong)
        self.check_auth(("postgres",))
        self.query("postgres",
                   "SELECT current_setting('server_version_num') || '|' || "
                   "(SELECT datcollate FROM pg_database WHERE datname=current_database()) || '|' || "
                   "current_setting('server_encoding') || '|' || "
                   "current_setting('password_encryption') || '|' || "
                   "(SELECT (count(*)>0 AND bool_and(auth_method='scram-sha-256' AND error IS NULL))::text "
                   "FROM pg_hba_file_rules WHERE type LIKE 'host%');", "170011|C|UTF8|scram-sha-256|true\n")
        self.query("postgres", f"""
BEGIN;
CREATE ROLE {LIMITED} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS
    PASSWORD '{limited}';
REVOKE CONNECT ON DATABASE {DATABASE} FROM PUBLIC;
GRANT CONNECT ON DATABASE {DATABASE} TO {LIMITED};
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO {LIMITED};
CREATE TABLE public.wa_probe (marker text PRIMARY KEY);
INSERT INTO public.wa_probe VALUES ('committed');
GRANT SELECT ON public.wa_probe TO {LIMITED};
COMMIT;
""", "")
        self.query("postgres", "SELECT (NOT (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR "
                   "rolbypassrls OR rolinherit) AND rolpassword LIKE 'SCRAM-SHA-256$%')::text "
                   f"FROM pg_authid WHERE rolname='{LIMITED}';", "true\n")
        self.check_auth((LIMITED,))
        self.report["checks"].append("scram_correct_and_wrong_password")
        self.query(LIMITED, "SELECT marker FROM public.wa_probe;", "committed\n")
        denied = self.docker.run(*self.psql(LIMITED), stdin=b"INSERT INTO public.wa_probe VALUES ('denied');",
                                 allow_fail=True)
        require(denied.returncode == 3 and not denied.stdout and
                re.fullmatch(rb"ERROR: +42501\n", denied.stderr),
                "RESTRICTED_WRITE_DENIAL_UNCONFIRMED")
        self.query(LIMITED, "SELECT marker FROM public.wa_probe;", "committed\n")
        self.report["checks"].append("restricted_select_and_write_denial")

    def launch_crash_session(self):
        args = self.psql("postgres", name="wa-cloud-f0-crash-writer")
        try:
            self.background = subprocess.Popen(self.docker.argv(*args), env=self.docker.env,
                                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except BaseException:
            self.remote_unknown = True
            raise
        self.background.stdin.write(b"BEGIN; INSERT INTO public.wa_probe VALUES ('uncommitted'); "
                                    b"SELECT pg_sleep(180); COMMIT;")
        self.background.stdin.close()
        self.background.stdin = None
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            result = self.docker.run(*self.psql("postgres"), stdin=b"SELECT count(*) FROM pg_stat_activity "
                                     b"WHERE application_name='wa-cloud-f0-crash-writer' AND pid <> pg_backend_pid() "
                                     b"AND backend_xid IS NOT NULL AND wait_event='PgSleep';", timeout=5)
            if result.stdout == b"1\n":
                return
            time.sleep(0.1)
        raise Stop("INDEPENDENT_BACKGROUND_TRANSACTION_UNCONFIRMED")

    def crash_and_recover(self, admin, limited, wrong):
        self.launch_crash_session()
        self.query(LIMITED, "SELECT marker FROM public.wa_probe;", "committed\n")
        self.report["checks"].append("independent_connections_and_uncommitted_visibility")
        self.require_daemon()
        self.check_target(True)
        self.docker.run("container", "kill", "--signal", "KILL", self.cid)
        deadline = time.monotonic() + 10
        while self.own_container()["State"]["Running"] is True and time.monotonic() < deadline:
            time.sleep(0.1)
        stopped = self.check_target(False)
        require(stopped["State"]["ExitCode"] == 137, "CONTROLLED_CRASH_EXIT_UNCONFIRMED")
        try:
            self.background.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            self.remote_unknown = True
            raise Stop("CRASH_CLIENT_CLOSURE_UNCONFIRMED") from None
        require(self.background.returncode in (1, 2, 137), "CRASH_CLIENT_EXIT_UNCONFIRMED")
        self.background = None
        self.docker.run("container", "start", self.cid, timeout=30, operation="RECOVERY_START")
        self.wait_ready()
        self.check_target(True)
        # Restart may clear the operating system's private tmpfs.
        self.docker.run("exec", self.cid, "test", "!", "-e", "/run/wa-secrets/correct.pgpass")
        self.docker.run("exec", self.cid, "test", "!", "-e", "/run/wa-secrets/wrong.pgpass")
        self.password_files(admin, limited, wrong)
        self.query(LIMITED, "SELECT marker FROM public.wa_probe;", "committed\n")
        self.check_auth((LIMITED,))
        self.report["checks"].append("same_storage_crash_recovery_and_rollback")

    def cleanup_resources(self):
        self.require_daemon(check_image=False)
        containers, volumes = self.docker.names()
        if self.attempted and self.target["container"] in containers:
            self.own_container()
            self.docker.run("container", "rm", "-f", self.cid)
        if self.attempted and self.target["volume"] in volumes:
            volume = self.docker.inspect("volume", self.target["volume"])
            require(self.volume_birth is not None, "CLEANUP_VOLUME_CREATION_UNCONFIRMED")
            verify_volume(volume, self.target, self.volume_birth)
            self.docker.run("volume", "rm", self.target["volume"])
        self.require_absent()

    def cleanup_client(self):
        if self.background is not None:
            if self.background.poll() is None:
                self.background.kill()
            self.background.communicate(timeout=10)
            self.background = None

    def cleanup_private(self):
        if self.secret_identity is not None:
            require(private_file(self.secret) == self.secret_identity, "CLEANUP_SECRET_OWNERSHIP")
            self.secret.unlink()
            self.secret.parent.rmdir()
        require(not self.secret.parent.exists() and not self.secret.parent.is_symlink(),
                "PRIVATE_SECRET_ABSENCE_UNCONFIRMED")

    def cleanup(self):
        self.report["cleanup_steps"] = {}
        for name, operation in (("docker_resources", self.cleanup_resources),
                                ("local_client", self.cleanup_client),
                                ("private_files", self.cleanup_private)):
            try:
                operation()
                self.report["cleanup_steps"][name] = "CONFIRMED"
            except BaseException as error:
                self.report["cleanup_steps"][name] = str(error) if type(error) is Stop else "UNCONFIRMED"
        require(set(self.report["cleanup_steps"].values()) == {"CONFIRMED"}, "CLEANUP_UNCONFIRMED")
        self.report["cleanup"] = "EXACT_CONTAINER_VOLUME_AND_PRIVATE_SECRET_ABSENT"


def execute(path, review_path):
    raw, manifest, profile, packet = read_plan(path)
    require(review_path == packet / "review.json", "REVIEW_LOCATION")
    reviewer, approval_hash = read_review(review_path, raw)
    docker = docker_for(profile, packet)
    report = {"schema": RESULT_SCHEMA, "status": "STOPPED", "started_at": now(),
              "manifest_sha256": sha256(raw), "review_sha256": approval_hash, "reviewer": reviewer,
              "source": manifest["source"], "target": manifest["target"], "daemon": manifest["daemon"],
              "image": manifest["cached_image"], "run_id": manifest["run_id"], "checks": [],
              "assertion_promotions": 0, "database_scope": "disposable synthetic capability probe",
              "cleanup": "UNCONFIRMED"}
    result = packet / "result.json"
    # The exclusive start record makes an attempted plan single-use.
    write_new(packet / "attempt.json", encode(report))
    probe = Probe(manifest, profile, packet, docker, report)
    try:
        admin, limited, wrong = (secrets.token_hex(32) for _ in range(3))
        report["stage"] = "PROVISION"
        probe.provision(admin)
        report["stage"] = "AUTH_AND_ROLE"
        probe.check_database(admin, limited, wrong)
        report["stage"] = "CONCURRENCY_CRASH_AND_RECOVERY"
        probe.crash_and_recover(admin, limited, wrong)
        report["completed_capability_checks"] = True
    except BaseException as error:
        report["first_stop"] = str(error) if type(error) is Stop else "UNEXPECTED_OPERATION_STOP"
        if docker.last_refusal is not None:
            report["docker_refusal"] = docker.last_refusal
        probe.remote_unknown = probe.remote_unknown or probe.background is not None
    finally:
        try:
            probe.cleanup()
            require(stable_file(path) == raw and read_review(review_path, raw) == (reviewer, approval_hash)
                    and source_snapshot() == manifest["source"], "FINAL_INPUT_DRIFT")
        except BaseException as error:
            report["cleanup_or_final_check_stop"] = str(error) if type(error) is Stop else "CLEANUP_UNCONFIRMED"
    report["remote_outcome_unconfirmed"] = probe.remote_unknown or docker.remote_unknown
    if (report.get("completed_capability_checks") and not report.get("cleanup_or_final_check_stop")
            and not report["remote_outcome_unconfirmed"]):
        report["status"] = "PASS_CAPABILITY_SUBSET_ONLY"
    report["finished_at"] = now()
    write_new(result, encode(report))
    print(encode({"status": report["status"], "result": str(result),
                  "first_stop": report.get("first_stop"),
                  "cleanup_or_final_check_stop": report.get("cleanup_or_final_check_stop")}).decode(), end="")
    return 0 if report["status"] == "PASS_CAPABILITY_SUBSET_ONLY" else 1


def interrupt(_number, _frame):
    raise Stop("OPERATOR_INTERRUPTED")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="action", required=True)
    commands.add_parser("prepare")
    run = commands.add_parser("execute")
    run.add_argument("--manifest", required=True, type=Path)
    run.add_argument("--review", required=True, type=Path)
    args = cli.parse_args()
    try:
        if args.action == "prepare":
            prepare()
            return 0
        signal.signal(signal.SIGTERM, interrupt)
        signal.signal(signal.SIGHUP, interrupt)
        return execute(args.manifest, args.review)
    except BaseException as error:
        code = str(error) if type(error) is Stop else "SETUP_OR_IO_UNCONFIRMED"
        print(encode({"status": "REFUSED_OR_INCOMPLETE", "code": code}).decode(), end="")
        return 1


if __name__ == "__main__":
    sys.exit(main())
