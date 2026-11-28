"""Source, daemon, image, and disposable-resource checks for Cloud F0."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
BASE = "scripts/sql-review/cloud-f0-v1"
IMAGE_HELPER = "scripts/sql-review/local_image_identity.py"
IMAGE_MANIFEST = "scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json"
FILES = (
    f"{BASE}/profile.json",
    f"{BASE}/guard.py",
    f"{BASE}/probe.py",
    f"{BASE}/test_guard.py",
    IMAGE_HELPER,
    IMAGE_MANIFEST,
)
HEX_ID = re.compile(r"[0-9a-f]{64}")
KERNEL_FAILURES = {
    b"SECRET_TMPFS_METADATA\n": "SECRET_TMPFS_METADATA",
    b"BOOTSTRAP_FILE_METADATA\n": "BOOTSTRAP_FILE_METADATA",
    b"SECRET_TMPFS_KERNEL_FLAGS\n": "SECRET_TMPFS_KERNEL_FLAGS",
    b"KERNEL_NETWORK_INTERFACES\n": "KERNEL_NETWORK_INTERFACES",
    b"BOOTSTRAP_BIND_KERNEL_FLAGS\n": "BOOTSTRAP_BIND_KERNEL_FLAGS",
}


class Stop(RuntimeError):
    """An allowlisted failure with no process output or credential data."""


def require(condition, code):
    if not condition:
        raise Stop(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def parse(raw):
    def pairs(items):
        result = dict(items)
        require(len(result) == len(items), "DUPLICATE_JSON_KEYS")
        return result

    def invalid(_):
        raise Stop("NONFINITE_JSON")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    except (UnicodeError, ValueError):
        raise Stop("INVALID_JSON") from None


def exact_path(path):
    require(path.is_absolute() and path.resolve(strict=True) == path, "PATH_ALIAS")


def stable_file(path, max_bytes=65536):
    exact_path(path)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as handle:
        begin = os.fstat(handle.fileno())
        require(stat.S_ISREG(begin.st_mode) and begin.st_nlink == 1
                and begin.st_size <= max_bytes, "FILE_TYPE_OR_SIZE")
        raw = handle.read(max_bytes + 1)
        end = os.fstat(handle.fileno())
    require(identity(begin) == identity(end) == identity(path.lstat())
            and len(raw) == begin.st_size, "FILE_IDENTITY_CHANGED")
    return raw


def identity(st):
    return (st.st_dev, st.st_ino, st.st_ctime_ns, st.st_size, st.st_mode, st.st_uid, st.st_nlink)


def private_directory(path):
    exact_path(path)
    st = path.lstat()
    require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid()
            and stat.S_IMODE(st.st_mode) == 0o700, "PRIVATE_DIRECTORY_MODE_OR_OWNER")


def private_file(path):
    private_directory(path.parent)
    st = path.lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid()
            and stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1,
            "PRIVATE_FILE_MODE_OR_OWNER")
    return identity(st)


def git(*args):
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args],
                                       stderr=subprocess.DEVNULL, timeout=20)
    except subprocess.SubprocessError:
        raise Stop("GIT_SOURCE_UNCONFIRMED") from None


def source_snapshot():
    commit = git("rev-parse", "HEAD").decode().strip()
    tree = git("rev-parse", f"{commit}^{{tree}}").decode().strip()
    files = {}
    for path in FILES:
        raw = stable_file(ROOT / path)
        require(raw == git("show", f"{commit}:{path}"), "DIRTY_SOURCE_INPUT")
        files[path] = sha256(raw)
    require(git("rev-parse", "HEAD").decode().strip() == commit, "HEAD_CHANGED_DURING_SNAPSHOT")
    return {"commit": commit, "tree": tree, "files_sha256": files}


def file_from_snapshot(path, source):
    raw = stable_file(ROOT / path)
    require(sha256(raw) == source["files_sha256"][path], "SOURCE_FILE_DRIFT")
    return raw


def safe_refusal(result, operation):
    """Retain only destination-independent classifications after command exit."""
    if (operation == "KERNEL_ISOLATION" and result.returncode == 42
            and result.stdout in KERNEL_FAILURES and not result.stderr):
        diagnostic = KERNEL_FAILURES[result.stdout]
    else:
        stderr = result.stderr.lower()
        diagnostic = "UNLISTED"
        for token, code in (
            (b"bind source path does not exist", "BIND_SOURCE_ABSENT_AT_DAEMON"),
            (b"error mounting", "OCI_MOUNT_FAILURE"),
            (b"operation not permitted", "KERNEL_OPERATION_NOT_PERMITTED"),
            (b"permission denied", "PERMISSION_DENIED"),
            (b"not running", "CONTAINER_NOT_RUNNING"),
            (b"oci runtime create failed", "OCI_RUNTIME_START_FAILED"),
        ):
            if token in stderr:
                diagnostic = code
                break
    return {"operation": operation, "exit_code": result.returncode, "diagnostic": diagnostic}


class Docker:
    def __init__(self, profile, config):
        require(sys.platform == "linux" and os.getuid() != 0, "LINUX_UNPRIVILEGED_TASK_REQUIRED")
        self.profile = profile
        self.config = config
        binary = shutil.which("docker")
        require(binary is not None, "DOCKER_BINARY_MISSING")
        self.binary = Path(binary).resolve(strict=True)
        require(self.binary.is_file() and os.access(self.binary, os.X_OK), "DOCKER_BINARY_UNUSABLE")
        self.binary_hash = sha256(self.binary.read_bytes())
        self.socket = Path(profile["docker_socket"])
        self.origin = self.socket_identity()
        self.env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C"}
        self.remote_unknown = False
        self.last_refusal = None

    def socket_identity(self):
        sock = self.socket.stat()
        require(stat.S_ISSOCK(sock.st_mode) and os.access(self.socket, os.W_OK)
                and not sock.st_mode & stat.S_IWOTH, "DOCKER_SOCKET_UNSAFE_OR_UNUSABLE")
        return {"real_path": str(self.socket.resolve(strict=True)), "device": sock.st_dev,
                "inode": sock.st_ino, "uid": sock.st_uid, "gid": sock.st_gid,
                "mode": stat.S_IMODE(sock.st_mode)}

    def argv(self, *args):
        require(self.socket_identity() == self.origin, "DOCKER_SOCKET_CHANGED")
        return [str(self.binary), "--config", str(self.config), "--host",
                f"unix://{self.socket}", *args]

    def run(self, *args, stdin=None, timeout=20, allow_fail=False, operation="DOCKER_METADATA_OR_RESOURCE"):
        command = self.argv(*args)
        try:
            result = subprocess.run(command, input=stdin or b"",
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=self.env, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired):
            self.remote_unknown = True
            raise Stop("DOCKER_PROCESS_OUTCOME_UNKNOWN") from None
        except BaseException:
            self.remote_unknown = True
            raise
        if not 0 <= result.returncode <= 255:
            self.remote_unknown = True
            raise Stop("DOCKER_PROCESS_OUTCOME_UNKNOWN")
        require(self.socket_identity() == self.origin, "DOCKER_SOCKET_CHANGED")
        if not allow_fail and (result.returncode != 0 or result.stderr):
            self.last_refusal = safe_refusal(result, operation)
            raise Stop("DOCKER_COMMAND_REFUSED")
        return result

    def observe(self):
        data = parse(self.run("info", "--format", "{{json .}}").stdout)
        version = parse(self.run("version", "--format", "{{json .Server}}").stdout)
        require(type(data.get("ID")) is str and re.fullmatch(r"[a-zA-Z0-9:._-]{1,128}", data["ID"])
                and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version.get("Version", "")),
                "DAEMON_IDENTITY_MISSING")
        require(data.get("OSType") == version.get("Os") == self.profile["docker_server_os"]
                and version.get("Arch") == self.profile["docker_server_architecture"]
                and data.get("Architecture") in ("x86_64", "amd64")
                and "name=rootless" in data.get("SecurityOptions", [])
                and self.profile["docker_server_rootless"] is True, "DAEMON_PLATFORM_OR_ISOLATION")
        return {"daemon_id": data["ID"], "version": version["Version"],
                "os": version["Os"], "architecture": version["Arch"],
                "rootless": True, "socket": self.origin, "docker_binary_sha256": self.binary_hash}

    def cached_image(self, source):
        inspected = parse(self.run("image", "inspect", self.profile["database_image"]).stdout)
        helper = ModuleType("pinned_image_helper")
        exec(compile(file_from_snapshot(IMAGE_HELPER, source), IMAGE_HELPER, "exec"), helper.__dict__)
        try:
            return helper.validate_cached_image(inspected, file_from_snapshot(IMAGE_MANIFEST, source))
        except helper.ImageIdentityError as error:
            raise Stop(error.code) from None

    def names(self):
        containers = self.run("container", "ls", "-a", "--format", "{{.Names}}")
        volumes = self.run("volume", "ls", "--format", "{{.Name}}")
        return (set(containers.stdout.decode().splitlines()), set(volumes.stdout.decode().splitlines()))

    def inspect(self, kind, name):
        data = parse(self.run(kind, "inspect", name).stdout)
        require(type(data) is list and len(data) == 1 and type(data[0]) is dict,
                "RESOURCE_INSPECTION_SHAPE")
        return data[0]


def verify_volume(volume, target, created_at=None):
    value = volume.get("CreatedAt")
    require(volume.get("Name") == target["volume"] and volume.get("Labels") == target["labels"]
            and volume.get("Driver") == volume.get("Scope") == "local"
            and not volume.get("Options") and type(value) is str and 0 < len(value) <= 64
            and (created_at is None or value == created_at), "VOLUME_IDENTITY_MISMATCH")
    return value


def verify_container(data, profile, target, volume, cid, image_id, running=None):
    host = data.get("HostConfig", {})
    config = data.get("Config", {})
    network = data.get("NetworkSettings", {})
    observed_ports = network.get("Ports") or {}
    require(HEX_ID.fullmatch(cid) and data.get("Id") == cid
            and data.get("Name") == "/" + target["container"] and data.get("Image") == image_id
            and config.get("Image") == profile["database_image"] and data.get("Platform") == "linux"
            and config.get("Labels") == target["labels"]
            and (running is None or data.get("State", {}).get("Running") is running),
            "CONTAINER_IDENTITY_MISMATCH")
    require(host.get("NetworkMode") == profile["network_mode"] == "none"
            and profile["published_ports"] == [] and not host.get("PortBindings")
            and host.get("PublishAllPorts") is False
            and all(value is None for value in observed_ports.values())
            and set(network.get("Networks", {})).issubset({"none"})
            and host.get("Privileged") is False and not host.get("Devices")
            and not host.get("CapAdd") and not host.get("PidMode")
            and host.get("IpcMode") in ("", "private") and not host.get("Links")
            and host.get("RestartPolicy", {}).get("Name") == "no"
            and host.get("LogConfig", {}).get("Type") == "none",
            "CONTAINER_ISOLATION_MISMATCH")
    tmpfs = profile["credential_tmpfs"]
    require(host.get("Tmpfs") == {tmpfs: profile["credential_tmpfs_options"]},
            "CONTAINER_TMPFS_MISMATCH")
    mounts = data.get("Mounts", [])
    by_dest = {mount["Destination"]: mount for mount in mounts}
    required = {profile["data_mount"], profile["bootstrap_mount"]}
    require(len(by_dest) == len(mounts) and set(by_dest) in (required, required | {tmpfs}),
            "MOUNT_INVENTORY_MISMATCH")
    if tmpfs in by_dest:
        require(by_dest[tmpfs].get("Type") == "tmpfs" and by_dest[tmpfs].get("RW") is True,
                "TMPFS_MOUNT_MISMATCH")
    storage = by_dest[profile["data_mount"]]
    require(storage.get("Type") == "volume" and storage.get("Name") == target["volume"]
            and storage.get("Driver") == "local" and storage.get("RW") is True
            and storage.get("Source") == volume["Mountpoint"], "DATA_MOUNT_MISMATCH")
    secret = by_dest[profile["bootstrap_mount"]]
    require(secret.get("Type") == "bind" and secret.get("Source") == target["bootstrap_file"]
            and secret.get("RW") is False and secret.get("Propagation") == "rprivate",
            "BOOTSTRAP_MOUNT_MISMATCH")
