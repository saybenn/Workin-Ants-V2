"""Build a fresh, held Cloud source8 packet without Docker or database I/O."""

import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import tarfile
import uuid


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "scripts/sql-review/cloud-runtime-lease-history-v1"
SCRATCH = Path("/workspace/scratch")
ENDPOINT = "unix:///var/run/docker.sock"
IMAGE = "docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1"
IMAGE_IDS = (IMAGE.rsplit("@", 1)[1], "sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d")
SCHEMA = "prisma/review/foundation-candidate.prisma"
SCHEMA_SHA = "de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723"
HISTORY = "prisma/local-f0-runtime-lease-history-v1/migrations"
HISTORY_MANIFEST = "prisma/local-f0-runtime-lease-history-v1/history-manifest.json"
EFFECTIVE = "cfb1c1cc9855e72978eadcd9e4902174e2e97a39383d480a71133c1fb07360c4"
INITIAL = "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad"
APPEND = "49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7"
INITIAL_PATH = "review-output/foundation-application.review.sql"
APPEND_PATH = "review-output/runtime-lease-branch-v1/history-source-artifact/migrations/20261120000100_f0_runtime_lease_branch_v1/migration.sql"
LEGACY_GUARD = "scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs"
LEGACY_RUNNER = "scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs"
LEGACY_CONFIG = "prisma.local-f0-runtime-lease-history-v1.config.mjs"
FILES = ("config.mjs", "guard.mjs", "runner.mjs")
RUNTIME = tuple(f"{BASE}/{name}" for name in FILES)
RUN_SCHEMA = "workinants.cloud-f0-runtime-lease-history-run.v1"
HISTORY_SCHEMA = "workinants.cloud-f0-runtime-lease-history.v1"
ATTESTATION_SCHEMA = "workinants.cloud-f0-runtime-lease-history-live-attestation.v1"
RESULT_SCHEMA = "workinants.cloud-f0-runtime-lease-history-migrate-result.v1"
PURPOSE = "CLOUD_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL"
LABEL = "p0c-cloud-f0-two-history-v1"
OP_ARG = "--execute-reviewed-cloud-f0-runtime-lease-history-v1"
CLOSURE_PATH = "context/reconciliation/local-f0-tooling/cloud-v2/prisma-tools-closure.json"
TOOL_TAR_SHA = "5a5deaff7aa721dd3b26be84f3ab1e9da1c1880ad902bced3be39dd5cc9e15f5"
TOOL_TAR_SIZE = 113920987
FILE_MAP_SHA = "e774defdbcec4bd038e131aa2f60bc2d982a2e069ed16230b4cc6ec2ac982310"
SIZE_MAP_SHA = "a9cd4e93518a3ef74e781b99cf6dc5f1a4755ed271974459c517016a25db2798"
TOOL_BINARY = ("node/bin/node", "schema-engine")
ORDERED = [
    {"id": name, "path": f"{HISTORY}/{name}/migration.sql", "sha256": digest}
    for name, digest in (("20261117000100_f0_local_initial", INITIAL),
                         ("20261120000100_f0_runtime_lease_branch_v1", APPEND))
]
PINNED = {
    SCHEMA: SCHEMA_SHA,
    INITIAL_PATH: INITIAL,
    APPEND_PATH: APPEND,
    LEGACY_GUARD: "805c336d46f79b7f54180963ee88fd2c98e9bab8b29d53459995dc7792100f1b",
    LEGACY_RUNNER: "ed77c44be1d368e708a48703ec515d05977e4ba6ed1ef22956427108dfb9e695",
    LEGACY_CONFIG: "6435bc0a4a9488e1cad3812ee09fa51298e0008407c1eb890b97cc7bc1d42bd8",
    CLOSURE_PATH: "81377e308966e93cb98f45d2d5482fd9d5ea7a6188895c6a882a3eedbc9de76c",
}


class Held(ValueError):
    """A fixed diagnostic without underlying private paths or I/O text."""


def require(ok, code):
    if not ok:
        raise Held(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def encoded(value):
    return canonical(value) + b"\n"


def strict_json(raw):
    def pairs(items):
        value = dict(items)
        require(len(value) == len(items), "DUPLICATE_JSON")
        return value

    def invalid(_):
        raise Held("JSON_NUMBER_NOT_INTEGER")

    require(0 < len(raw) <= 4 * 1024 * 1024, "JSON_SIZE")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_float=invalid, parse_constant=invalid)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


@contextmanager
def regular(path, max_bytes):
    require(path.is_absolute() and path.resolve(strict=True) == path, "NONCANONICAL_FILE")
    before = path.lstat()
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1
                and not info.st_mode & 0o7022 and info.st_size <= max_bytes
                and identity(before) == identity(info), "FILE_OWNER_MODE_SIZE")
        yield stream, info
        require(identity(info) == identity(os.fstat(stream.fileno())) == identity(path.lstat()),
                "FILE_IDENTITY_CHANGED")


def read(path, max_bytes=4 * 1024 * 1024):
    with regular(path, max_bytes) as (stream, info):
        raw = stream.read(max_bytes + 1)
        require(len(raw) == info.st_size, "FILE_SIZE_CHANGED")
        return raw


def pinned(root, relative):
    raw = read(root / relative)
    require(sha(raw) == PINNED[relative], "HISTORICAL_SOURCE_DRIFT")
    return raw


def inspect_tools(root, archive):
    closure = strict_json(pinned(root, CLOSURE_PATH))
    hashes = closure["tools_files_sha256"]
    expected_sizes = closure["tools_file_sizes"]
    require(closure["archive_bytes"] == TOOL_TAR_SIZE and closure["archive_sha256"] == TOOL_TAR_SHA
            and [package["version"] for package in closure["packages"] if package["name"] == "effect"] == ["3.22.1"],
            "VETTED_CLOUD_TOOL_CLOSURE")
    require(len(hashes) == closure["file_count"] == 10300 and sha(canonical(hashes)) == FILE_MAP_SHA,
            "TOOL_HASH_MAP_DRIFT")
    require(set(expected_sizes) == set(hashes) and sha(canonical(expected_sizes)) == SIZE_MAP_SHA,
            "TOOL_SIZE_MAP_DRIFT")
    require(archive.is_relative_to(SCRATCH), "TOOL_ARCHIVE_OUTSIDE_SCRATCH")
    sizes = {}
    with regular(archive, TOOL_TAR_SIZE) as (stream, info):
        require(info.st_size == TOOL_TAR_SIZE and hashlib.file_digest(stream, "sha256").hexdigest() == TOOL_TAR_SHA,
                "EXACT_TOOL_ARCHIVE_REQUIRED")
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r|gz") as members:
            for member in members:
                name = member.name
                require(member.isreg() and name in hashes and name not in sizes
                        and member.mode == (0o755 if name in TOOL_BINARY else 0o644)
                        and member.uid == member.gid == member.mtime == 0
                        and member.pax_headers in ({}, {"path": name})
                        and 0 <= member.size <= (126879696 if name in TOOL_BINARY else 16 * 1024 * 1024)
                        and member.size == expected_sizes[name],
                        "TOOL_ARCHIVE_MEMBER")
                with members.extractfile(member) as blob:
                    digest = hashlib.file_digest(blob, "sha256").hexdigest()
                require(digest == hashes[name], "TOOL_MEMBER_HASH")
                sizes[name] = member.size
    require(sizes == expected_sizes, "TOOL_SIZE_MAP_DRIFT")
    return {
        "node_version": closure["node_version"],
        "prisma_version": closure["prisma_version"],
        "engine_commit": closure["engine_commit"],
        "archive_sha256": TOOL_TAR_SHA,
        "files_sha256": hashes,
        "file_sizes": sizes,
    }


def replace(text, old, new):
    require(text.count(old) == 1, "EXACT_RENDER_ANCHOR")
    return text.replace(old, new)


def section(text, start, end, replacement):
    require(text.count(start) == text.count(end) == 1, "EXACT_RENDER_SECTION")
    offset = text.index(start)
    stop = text.index(end, offset + len(start))
    return text[:offset] + replacement + text[stop:]


def render_guard(root):
    guard = pinned(root, LEGACY_GUARD).decode()
    platform = read(root / BASE / "guard-platform.mjs.txt").decode()
    guard = replace(guard, "// Local-only migration target guard.", "// Cloud-only migration target guard.")
    guard = replace(guard, 'const HASH = /^[0-9a-f]{64}$/;', r'const HASH = /^[0-9a-f]{64}(?![\s\S])/;')
    guard = replace(guard, f'export const CONFIG = "{LEGACY_CONFIG}";', f'export const CONFIG = "{RUNTIME[0]}";')
    guard = replace(guard, f'export const RUNTIME = [CONFIG, "{LEGACY_GUARD}", "{LEGACY_RUNNER}"];',
                    f'export const RUNTIME = [CONFIG, "{RUNTIME[1]}", "{RUNTIME[2]}"];')
    guard = replace(guard, 'const OLD_EXPECTED = "3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433";',
                    f'const EFFECTIVE_EXPECTED = "{EFFECTIVE}";')
    guard = replace(guard, 'function equal(a,b) { return JSON.stringify(a) === JSON.stringify(b); }',
                    'function equal(a,b) { return canonicalJson(a) === canonicalJson(b); }')
    guard = section(guard, "export function validateManifest(planned) {", "  keys(planned.history,",
                    platform + "\n" + r'''export function validateManifest(planned) {
  keys(planned,["schema","run_id","purpose","daemon","target","source","history","tools"],"RUN_FIELDS");
  requireLocal(planned.schema==="workinants.cloud-f0-runtime-lease-history-run.v1" &&
    planned.purpose==="CLOUD_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL","CLOUD_RUN_MANIFEST");
  const run = planned.run_id;
  requireLocal(typeof run==="string" && /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}(?![\s\S])/.test(run),"UUID4_RUN_REQUIRED");
  validateDaemon(planned.daemon);
  const target=planned.target, source=planned.source;
  keys(target,["container_name","volume_name","database","image","network","labels","bootstrap_secret_host_path"],"TARGET_FIELDS");
  const name = "wa-p0c-cloud-two-history-" + run;
  requireLocal(target.container_name===name && target.volume_name===name+"-data"
    && target.image===IMAGE && target.database==="wa_p0c_rehearsal" && target.network==="none","CLOUD_TARGET");
  requireLocal(target.bootstrap_secret_host_path==="/workspace/scratch/wa-cloud-f0-two-history-"+run+"/private/ok-bootstrap-password",
    "EXACT_NEW_POSIX_SECRET_PATH");
  keys(target.labels,["workinants.rehearsal","workinants.rehearsal.run"],"LABEL_FIELDS");
  requireLocal(target.labels["workinants.rehearsal"]==="p0c-cloud-f0-two-history-v1"
    && target.labels["workinants.rehearsal.run"]===run,"EXACT_RUN_LABELS");
''')
    guard = replace(guard, 'typeof source.effective_expected_sha256==="string" && HASH.test(source.effective_expected_sha256) && source.effective_expected_sha256!==OLD_EXPECTED',
                    'source.effective_expected_sha256===EFFECTIVE_EXPECTED')
    guard = section(guard, "  keys(planned.tools,", "export function validateUrl(raw) {", '''  validateToolMap(planned.tools);
  return planned;
}

export function validateAttestation(value) {
  keys(value,["schema","planned","run_manifest_sha256","operation","observed"],"ATTESTATION_FIELDS");
  requireLocal(value.schema==="workinants.cloud-f0-runtime-lease-history-live-attestation.v1"
    && ["deploy","status"].includes(value.operation),"CLOUD_ATTESTATION_SCHEMA_OPERATION");
  const planned=validateManifest(value.planned), observed=value.observed;
  keys(observed,["endpoint","daemon","container_id","container_name","volume_name","volume_created_at","image","image_id","network","published_ports","labels","bootstrap_secret_host_path","bootstrap_readonly"],"OBSERVATION_FIELDS");
  validateDaemon(observed.daemon);
  requireLocal(observed.endpoint===ENDPOINT && equal(observed.daemon,planned.daemon),"CLOUD_ENDPOINT_AND_DAEMON");
  requireLocal(typeof observed.container_id==="string" && HASH.test(observed.container_id)
    && observed.container_name===planned.target.container_name && observed.volume_name===planned.target.volume_name
    && typeof observed.volume_created_at==="string" && observed.volume_created_at===observed.volume_created_at.trim()
    && /^[0-9TZ:.+-]{20,64}$/.test(observed.volume_created_at),"LIVE_RESOURCE_IDENTITY");
  requireLocal(observed.image===IMAGE && [IMAGE_MANIFEST,IMAGE_CONFIG].includes(observed.image_id)
    && observed.network==="none" && observed.published_ports===false,"LIVE_PRIVATE_TARGET");
  requireLocal(observed.bootstrap_secret_host_path===planned.target.bootstrap_secret_host_path
    && observed.bootstrap_readonly===true,"LIVE_BOOTSTRAP_SECRET_BIND");
  requireLocal(equal(observed.labels,planned.target.labels),"LIVE_RUN_LABELS");
  requireLocal(value.run_manifest_sha256===sha256(canonicalJson(planned)+"\\n"),"RUN_MANIFEST_HASH_MISMATCH");
  return value;
}

''')
    guard = replace(guard, 'url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432"',
                    r'/^postgresql:\/\/wa_migrator:[^@/?#\\]+@127\.0\.0\.1:5432\//.test(raw) && url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432"')
    guard = section(guard, "export function readNoFollow(filename, privateFile = false) {\n  let descriptor;",
                    "function listFiles(directory) {", "")
    guard = replace(guard, 'if (info.isFile()) result.push(relative);',
                    'if (info.isFile()) { requireLocal(info.nlink === 1, "TREE_SINGLE_LINK_ONLY"); result.push(relative); }')
    guard = replace(guard, 'requireLocal(io.mountInfo().split("\\n").some(line=>line.split(" ")[4]===PRIVATE_ROOT && line.includes(" - tmpfs ")),"PRIVATE_TMPFS_REQUIRED");',
                    'requireLocal(identity.uid===0 && io.loopbackOnly(),"CONTAINER_LOOPBACK_ONLY");\n  privateMounts(io.mountInfo());')
    guard = replace(guard, 'history.schema==="workinants.local-f0-runtime-lease-history.v1" && history.scope==="PROVISIONAL_LOCAL_ONLY_NOT_HOSTED_ADOPTION"',
                    f'history.schema==="{HISTORY_SCHEMA}" && history.scope==="PROVISIONAL_CLOUD_ONLY_NOT_HOSTED_ADOPTION"')
    guard = replace(guard, 'sha256(io.read(TOOLS_ROOT+"/"+sourceFile(relative)))===h',
                    'io.toolHash(TOOLS_ROOT+"/"+sourceFile(relative),relative,planned.tools.file_sizes[relative])===h')
    guard = replace(guard, '  const databaseUrl=validateUrl(io.readPrivate(URL_FILE).toString("utf8"));',
                    '  requireLocal(strictJson(io.read(TOOLS_ROOT+"/node_modules/effect/package.json")).version==="3.22.1","VETTED_EFFECT_VERSION");\n'
                    '  const databaseUrl=validateUrl(io.readPrivate(URL_FILE).toString("utf8"));')
    guard = replace(guard, '    return verifyInputs(attestation,\n      {read:',
                    '''    const interfaces = os.networkInterfaces();
    const loopbackOnly = () => equal(Object.keys(interfaces),["lo"])
      && interfaces.lo.some(address => address.internal && address.address==="127.0.0.1");
    return verifyInputs(attestation,
      {toolHash: hashStableTool, loopbackOnly, read:''')
    guard = replace(guard, "hostname: os.hostname()", "hostname: os.hostname(), uid: process.getuid()")
    return guard.encode()


def render_runtime(root):
    runner = pinned(root, LEGACY_RUNNER).decode()
    runner = replace(runner, '"./local-f0-runtime-lease-history-v1-guard.mjs"', '"./guard.mjs"')
    runner = replace(runner, "  validateAttestation, loadLocalF0Config,", "  privateMounts, readAttestationStdin, validateAttestation, loadLocalF0Config,")
    require(runner.count("--execute-reviewed-local-f0-runtime-lease-history-v1") == 2, "EXACT_RUNNER_OPERATION_ANCHORS")
    runner = runner.replace("--execute-reviewed-local-f0-runtime-lease-history-v1", OP_ARG)
    require(runner.count("workinants.local-f0-runtime-lease-history-migrate-result.v1") == 2, "EXACT_RESULT_SCHEMA_ANCHORS")
    runner = runner.replace("workinants.local-f0-runtime-lease-history-migrate-result.v1", RESULT_SCHEMA)
    runner = replace(runner, '    const raw = (dependencies.readStdin || (() => fs.readFileSync(0)))();',
                     '    const raw = (dependencies.readStdin || readAttestationStdin)();')
    runner = replace(runner, '    validateAttestation(attestation);\n    (dependencies.store',
                     '    validateAttestation(attestation);\n    requireLocal(attestation.operation===argv[2],"ATTESTED_OPERATION");\n    (dependencies.store')
    runner = replace(runner, '  requireLocal(fs.readFileSync("/proc/self/mountinfo", "utf8").split("\\n").some(line => line.split(" ")[4] === PRIVATE_ROOT && line.includes(" - tmpfs ")), "PRIVATE_TMPFS_REQUIRED");',
                     '  privateMounts(fs.readFileSync("/proc/self/mountinfo", "utf8"));')
    runner = replace(runner, 'previous.observed?.container_id === attestation.observed.container_id,',
                     'previous.observed?.container_id === attestation.observed.container_id && previous.run_manifest_sha256 === attestation.run_manifest_sha256,')
    runner = replace(runner, '    summary.container_id = attestation.observed.container_id;',
                     '    summary.container_id = attestation.observed.container_id;\n    summary.daemon_id = attestation.observed.daemon.daemon_id;')
    config = replace(pinned(root, LEGACY_CONFIG).decode(), '"./scripts/sql-review/local-f0-runtime-lease-history-v1-guard.mjs"', '"./guard.mjs"')
    guard = render_guard(root).decode()
    for old, new in (
        ('"/wa-runtime-lease-history-v1-attestation.json"', '"/wa-cloud-runtime-lease-history-v1-attestation.json"'),
        ('"/wa-runtime-lease-history-v1-migrator-url"', '"/wa-cloud-runtime-lease-history-v1-migrator-url"'),
    ):
        guard = replace(guard, old, new)
    return dict(zip(RUNTIME, (config.encode(), guard.encode(), runner.encode()), strict=True))


def exact_daemon(value):
    require(type(value) is dict and set(value) == {"daemon_id", "version", "os", "architecture",
            "rootless", "socket", "docker_binary_sha256"}, "DAEMON_FIELDS")
    require(type(value["daemon_id"]) is str and re.fullmatch("[a-zA-Z0-9:._-]{1,128}", value["daemon_id"])
            and type(value["version"]) is str and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["version"])
            and value["os"] == "linux" and value["architecture"] == "amd64" and value["rootless"] is True
            and type(value["docker_binary_sha256"]) is str and re.fullmatch("[0-9a-f]{64}", value["docker_binary_sha256"]),
            "CLOUD_DAEMON_IDENTITY")
    socket = value["socket"]
    require(type(socket) is dict and set(socket) == {"real_path", "device", "inode", "uid", "gid", "mode"}
            and socket["real_path"] in ("/run/docker.sock", "/var/run/docker.sock", "/run/codex-docker/docker.sock")
            and all(type(socket[key]) is int and 0 <= socket[key] <= 2**53 - 1 for key in ("device", "inode", "uid", "gid", "mode"))
            and socket["inode"] > 0 and socket["mode"] in (0o600, 0o660), "CLOUD_SOCKET_IDENTITY")
    return value


def target_for(run_id):
    parsed = uuid.UUID(run_id)
    require(parsed.version == 4 and str(parsed) == run_id, "UUID4_RUN_REQUIRED")
    container = f"wa-p0c-cloud-two-history-{run_id}"
    return {
        "container_name": container,
        "volume_name": f"{container}-data",
        "database": "wa_p0c_rehearsal",
        "image": IMAGE,
        "network": "none",
        "labels": {"workinants.rehearsal": LABEL, "workinants.rehearsal.run": run_id},
        "bootstrap_secret_host_path": str(SCRATCH / f"wa-cloud-f0-two-history-{run_id}" / "private/ok-bootstrap-password"),
    }


def build(root, run_id, daemon, tool_archive):
    target = target_for(run_id)
    daemon = exact_daemon(daemon)
    tools = inspect_tools(root, tool_archive)
    runtime = render_runtime(root)
    files = {
        **runtime,
        SCHEMA: pinned(root, SCHEMA),
        ORDERED[0]["path"]: pinned(root, INITIAL_PATH),
        ORDERED[1]["path"]: pinned(root, APPEND_PATH),
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
            "runtime_files_sha256": {path: sha(raw) for path, raw in runtime.items()},
        },
        "history": {"path": HISTORY, "ordered": ORDERED},
        "tools": tools,
    }
    raw_manifest = encoded(manifest)
    history = {
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
    }
    files[HISTORY_MANIFEST] = encoded(history)
    require(len(files) == 8, "EXACT_SOURCE8")
    return manifest, raw_manifest, files


def archive_source(files):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name, raw in sorted(files.items()):
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            member.mode = 0o444
            member.uid = member.gid = member.mtime = 0
            archive.addfile(member, io.BytesIO(raw))
    return buffer.getvalue()


def attest(manifest, observed, operation):
    """Encode one operation for the host's reviewed, re-inspected target."""
    require(operation in ("deploy", "status"), "OPERATION_DENIED")
    require(type(observed) is dict and set(observed) == {
        "endpoint", "daemon", "container_id", "container_name", "volume_name", "volume_created_at",
        "image", "image_id", "network", "published_ports", "labels", "bootstrap_secret_host_path", "bootstrap_readonly",
    }, "OBSERVATION_FIELDS")
    require(observed["endpoint"] == ENDPOINT and exact_daemon(observed["daemon"]) == manifest["daemon"], "CLOUD_ENDPOINT_AND_DAEMON")
    target = manifest["target"]
    require(all(observed[key] == target[key] for key in ("container_name", "volume_name", "image", "network",
            "labels", "bootstrap_secret_host_path")) and observed["image_id"] in IMAGE_IDS
            and observed["published_ports"] is False and observed["bootstrap_readonly"] is True
            and type(observed["container_id"]) is str and re.fullmatch("[0-9a-f]{64}", observed["container_id"])
            and type(observed["volume_created_at"]) is str
            and re.fullmatch("[0-9TZ:.+-]{20,64}", observed["volume_created_at"]), "LIVE_RESOURCE_IDENTITY")
    return encoded({"schema": ATTESTATION_SCHEMA, "operation": operation, "planned": manifest,
                    "observed": observed, "run_manifest_sha256": sha(encoded(manifest))})


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
        output = Path(manifest["target"]["bootstrap_secret_host_path"]).parents[1]
        out_tar = archive_source(files)
        binding = {
            "status": "HELD_NOT_RUN",
            "run_id": args.run_id,
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
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError, RecursionError):
        print(json.dumps({"status": "HELD_NOT_RUN", "code": "PREPARATION_UNCONFIRMED"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
