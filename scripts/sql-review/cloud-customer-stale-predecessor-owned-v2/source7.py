"""Prepare the Cloud CSP single-migration runtime archive without contacting a database."""

import gzip
import hashlib
import io
import json
from pathlib import Path
import runpy
import tarfile
import uuid


ROOT = Path(__file__).resolve().parents[3]
BASE = "scripts/sql-review/cloud-customer-stale-predecessor-owned-v2"
SHARED = "scripts/sql-review/cloud-runtime-lease-history-v1"
SCRATCH = Path("/workspace/scratch")
CONFIG = "prisma.local-f0.config.mjs"
GUARD = "scripts/sql-review/local-f0-migrate-guard.mjs"
RUNNER = "scripts/sql-review/local-f0-migrate-runner.mjs"
SCHEMA = "prisma/review/foundation-candidate.prisma"
APPLICATION = "review-output/foundation-application.review.sql"
HISTORY = "prisma/foundation/migrations"
HISTORY_MANIFEST = "prisma/foundation/history-manifest.json"
MIGRATION = "20261117000100_f0_local_initial"
MIGRATION_FILE = f"{HISTORY}/{MIGRATION}/migration.sql"
LABEL = "p0c-cloud-f0-csp-v2"
PURPOSE = "CLOUD_F0_CSP_INITIAL_MIGRATION_V2"
OPERATION_FLAG = "--execute-reviewed-cloud-csp-initial-v2"
IMAGE = "docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1"
INITIAL_SHA = "5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad"
SCHEMA_SHA = "de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723"
PINNED = {
    CONFIG: "ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684",
    GUARD: "7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b",
    RUNNER: "7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd",
    APPLICATION: INITIAL_SHA,
    MIGRATION_FILE: INITIAL_SHA,
    SCHEMA: SCHEMA_SHA,
}


def require(good, code):
    if not good:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def pinned(root, relative):
    raw = (root / relative).read_bytes()
    require(sha(raw) == PINNED[relative], "CSP_LEGACY_SOURCE_CHANGED")
    return raw


def replace(text, before, after):
    require(text.count(before) == 1, "CSP_EXACT_RENDER_ANCHOR")
    return text.replace(before, after)


def section(text, start, end, replacement):
    require(text.count(start) == text.count(end) == 1, "CSP_EXACT_SECTION_ANCHORS")
    left = text.index(start)
    right = text.index(end, left + len(start))
    return text[:left] + replacement + text[right:]


def shared(root):
    return runpy.run_path(str(root / SHARED / "prepare.py"))


def render_runtime(root):
    platform = (root / SHARED / "guard-platform.mjs.txt").read_text()
    platform = section(platform, "export function privateMounts(raw) {", "function sameStat(a, b) {",
                       '''export function privateMounts(raw) {
  const mounts = raw.split("\\n").map(line => line.split(" "));
  requireLocal(mounts.every(fields => fields[4] !== "/run/bootstrap-password"), "HOST_SECRET_MOUNT_DENIED");
  const found = mounts.filter(fields => fields[4] === PRIVATE_ROOT);
  requireLocal(found.length === 1, "PRIVATE_MOUNT_REQUIRED");
  const fields = found[0];
  const separator = fields.indexOf("-", 6);
  requireLocal(separator >= 6 && fields[separator + 1] === "tmpfs"
    && ["rw", "nosuid", "nodev", "noexec"].every(option => fields[5].split(",").includes(option)),
    "PRIVATE_MOUNT_OPTIONS");
}

''')
    attestation = (root / BASE / "initial-attestation.mjs.txt").read_text()
    guard = pinned(root, GUARD).decode()
    guard = replace(guard, "const HASH = /^[0-9a-f]{64}$/;", r"const HASH = /^[0-9a-f]{64}(?![\s\S])/;")
    guard = section(guard, "export function validateAttestation(value) {",
                    "export function validateUrl(raw) {", platform + "\n" + attestation + "\n")
    guard = section(guard, "export function readNoFollow(filename, privateFile = false) {\n  let descriptor;",
                    "function listFiles(directory) {", "")
    guard = replace(guard, "if (info.isFile()) result.push(relative);",
                    'if (info.isFile()) { requireLocal(info.nlink === 1, "TREE_SINGLE_LINK_ONLY"); result.push(relative); }')
    guard = replace(guard, '  requireLocal(io.mountInfo().split("\\n").some(line => line.split(" ")[4] === PRIVATE_ROOT && line.includes(" - tmpfs ")), "PRIVATE_TMPFS_REQUIRED");',
                    '  requireLocal(identity.uid === 0 && io.loopbackOnly(), "CONTAINER_LOOPBACK_ONLY");\n  privateMounts(io.mountInfo());')
    guard = replace(guard, '"workinants.local-f0-history.v1"', '"workinants.cloud-csp-initial-history.v2"')
    guard = replace(guard, 'sha256(io.read(TOOLS_ROOT + "/" + sourceFile(relative))) === expected',
                    'io.toolHash(TOOLS_ROOT + "/" + sourceFile(relative), relative, planned.tools.file_sizes[relative]) === expected')
    guard = replace(guard, '  const databaseUrl = validateUrl(',
                    '''  const effect = JSON.parse(io.read(TOOLS_ROOT + "/node_modules/effect/package.json").toString("utf8"));
  requireLocal(effect.version === "3.22.1", "PATCHED_EFFECT_VERSION");
  const databaseUrl = validateUrl(''')
    guard = replace(guard, '    return verifyInputs(attestation,\n      {read:',
                    '''    const networks = os.networkInterfaces();
    const loopbackOnly = () => Object.keys(networks).length === 1 && Array.isArray(networks.lo) &&
      networks.lo.some(address => address.internal && address.address === "127.0.0.1");
    verifyBootstrapAbsent();
    return verifyInputs(attestation,
      {toolHash: hashStableTool, loopbackOnly, read:''')
    guard = replace(guard, "hostname: os.hostname()", "hostname: os.hostname(), uid: process.getuid()")
    guard = replace(guard, 'url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432"',
                    r'/^postgresql:\/\/wa_migrator:[a-f0-9]{64}@127\.0\.0\.1:5432\//.test(raw) && url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432"')
    guard = replace(guard, '"/wa-local-f0-attestation.json"', '"/wa-cloud-csp-initial-v2-attestation.json"')
    guard = replace(guard, '"/wa-local-f0-migrator-url"', '"/wa-cloud-csp-initial-v2-migrator-url"')

    runner = pinned(root, RUNNER).decode()
    runner = replace(runner, "  validateAttestation, loadLocalF0Config,", "  privateMounts, readAttestationStdin, verifyBootstrapAbsent, validateAttestation, loadLocalF0Config,")
    runner = section(runner, "export function validateRecovery(attestation) {",
                     "export function childEnvironment(local) {",
                     '''export function prismaArguments(operation, local) {
  requireLocal(operation === "deploy", "CLOUD_CSP_DEPLOY_ONLY");
  return [local.cli, "migrate", "deploy", "--config", local.config];
}

''')
    runner = replace(runner, '  requireLocal(fs.readFileSync("/proc/self/mountinfo", "utf8").split("\\n").some(line => line.split(" ")[4] === PRIVATE_ROOT && line.includes(" - tmpfs ")), "PRIVATE_TMPFS_REQUIRED");',
                     '  privateMounts(fs.readFileSync("/proc/self/mountinfo", "utf8"));\n  verifyBootstrapAbsent();')
    runner = section(runner, "  // Attestation contains no credential.", "  const descriptor =",
                     '  requireLocal(!fs.existsSync(ATTESTATION), "CLOUD_CSP_SINGLE_ATTESTATION");\n')
    runner = replace(runner, "--execute-reviewed-local-f0 --operation deploy|status|resolve-rolled-back",
                     OPERATION_FLAG + " --operation deploy")
    runner = replace(runner, 'argv[0] === "--execute-reviewed-local-f0" && argv[1] === "--operation" && ["deploy", "status", "resolve-rolled-back"].includes(argv[2])',
                     f'argv[0] === "{OPERATION_FLAG}" && argv[1] === "--operation" && argv[2] === "deploy"')
    runner = replace(runner, 'const raw = (dependencies.readStdin || (() => fs.readFileSync(0)))();',
                     'const raw = (dependencies.readStdin || readAttestationStdin)();')
    runner = replace(runner, "    summary.container_id = attestation.observed.container_id;",
                     "    summary.container_id = attestation.observed.container_id;\n    summary.daemon_id = attestation.observed.daemon.daemon_id;")
    return {CONFIG: pinned(root, CONFIG), GUARD: guard.encode(), RUNNER: runner.encode()}


def run_target(run_id):
    parsed = uuid.UUID(run_id)
    require(parsed.version == 4 and str(parsed) == run_id, "CSP_FRESH_UUID4_REQUIRED")
    name = f"wa-p0c-cloud-csp-{run_id}"
    folder = SCRATCH / f"wa-cloud-f0-csp-{run_id}"
    return folder, {
        "container_name": name, "volume_name": name + "-data", "database": "wa_p0c_rehearsal",
        "image": IMAGE, "network": "none", "labels": {
            "workinants.rehearsal": LABEL, "workinants.rehearsal.run": run_id,
        },
        "bootstrap_container_path": "/run/wa-secrets/bootstrap-password",
    }


def build(root, run_id, daemon, tool_archive):
    library = shared(root)
    daemon = library["exact_daemon"](daemon)
    tools = library["inspect_tools"](root, Path(tool_archive))
    _, target = run_target(run_id)
    runtime = render_runtime(root)
    manifest = {
        "schema": "workinants.cloud-csp-initial-run.v2", "purpose": PURPOSE, "run_id": run_id,
        "target": target, "daemon": daemon, "tools": tools,
        "source": {
            "integrated_sql_sha256": INITIAL_SHA, "foundation_schema_sha256": SCHEMA_SHA,
            "runtime_files_sha256": {name: sha(raw) for name, raw in runtime.items()},
        },
        "migration": {"id": MIGRATION, "history": HISTORY},
    }
    application = pinned(root, APPLICATION)
    require(application == pinned(root, MIGRATION_FILE), "CSP_CANONICAL_INITIAL_MISMATCH")
    lock = (root / HISTORY / "migration_lock.toml").read_bytes()
    require(lock == b'provider = "postgresql"\n', "CSP_MIGRATION_LOCK_MISMATCH")
    files = {**runtime, MIGRATION_FILE: application, f"{HISTORY}/migration_lock.toml": lock,
             SCHEMA: pinned(root, SCHEMA)}
    history = {
        "schema": "workinants.cloud-csp-initial-history.v2", "run_id": run_id,
        "run_manifest_sha256": sha(encode(manifest)), "migrations": HISTORY, "migration_id": MIGRATION,
        "source": APPLICATION, "source_sql_sha256": INITIAL_SHA, "foundation_schema": SCHEMA,
        "files_sha256": {name: sha(raw) for name, raw in files.items()},
        "database_contacted": False, "ledger_created_or_modified": False, "raw_structure_applied_separately": False,
    }
    files[HISTORY_MANIFEST] = encode(history)
    return manifest, files


def archive(files):
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=buffer, mode="wb", mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, raw in sorted(files.items()):
                member = tarfile.TarInfo(name)
                member.size = len(raw)
                member.mode = 0o444
                tar.addfile(member, io.BytesIO(raw))
    return buffer.getvalue()
