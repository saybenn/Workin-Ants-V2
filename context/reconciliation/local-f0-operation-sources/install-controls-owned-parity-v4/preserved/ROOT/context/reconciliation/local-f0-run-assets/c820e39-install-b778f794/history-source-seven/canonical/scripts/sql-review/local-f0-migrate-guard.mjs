// Local-only migration target guard. No database connection or child process.
import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";

export const SOURCE_ROOT = "/run/wa-f0-source";
export const TOOLS_ROOT = "/run/wa-f0-tools";
export const PRIVATE_ROOT = "/run/wa-secrets";
export const ATTESTATION = PRIVATE_ROOT + "/wa-local-f0-attestation.json";
export const URL_FILE = PRIVATE_ROOT + "/wa-local-f0-migrator-url";
export const IMAGE = "docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1";
const HASH = /^[0-9a-f]{64}$/;

export class HeldFailure extends Error {
  constructor(code) { super(code); this.code = code; }
}
export function requireLocal(value, code) {
  if (!value) throw new HeldFailure(code);
}
export function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }

export function validateAttestation(value) {
  requireLocal(value?.schema === "workinants.local-f0-live-attestation.v1", "ATTESTATION_SCHEMA");
  const planned = value.planned;
  const observed = value.observed;
  requireLocal(planned?.schema === "workinants.local-f0-run.v1" && planned.purpose === "LOCAL_F0_MIGRATION_REHEARSAL", "RUN_MANIFEST");
  requireLocal(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(planned.run_id), "RUN_ID");
  requireLocal(planned.target?.image === IMAGE && planned.target.database === "wa_p0c_rehearsal" && planned.target.network === "none", "LOCAL_TARGET");
  for (const key of ["container_name", "volume_name"]) requireLocal(/^wa-p0c-[a-z0-9][a-z0-9-]{0,110}$/.test(planned.target[key]), "RESOURCE_NAME");
  requireLocal(typeof planned.target.bootstrap_secret_host_path === "string" && /^[A-Za-z]:\\[^\x00-\x1f<>"|?*]+$/.test(planned.target.bootstrap_secret_host_path) &&
    !planned.target.bootstrap_secret_host_path.includes("/") && !planned.target.bootstrap_secret_host_path.slice(2).includes(":") &&
    planned.target.bootstrap_secret_host_path.slice(3).split("\\").every(part => part && part !== "." && part !== ".." && !/[ .]$/.test(part)), "ABSOLUTE_WINDOWS_SECRET_PATH_REQUIRED");
  requireLocal(observed?.endpoint === "npipe:////./pipe/dockerDesktopLinuxEngine" && observed.context === "desktop-linux", "LOCAL_ENDPOINT");
  requireLocal(HASH.test(observed.container_id) && observed.container_name === planned.target.container_name && observed.volume_name === planned.target.volume_name, "LIVE_RESOURCE_IDENTITY");
  requireLocal(observed.image === IMAGE && observed.network === "none" && observed.published_ports === false, "LIVE_PRIVATE_TARGET");
  requireLocal(observed.bootstrap_secret_host_path === planned.target.bootstrap_secret_host_path, "LIVE_BOOTSTRAP_SECRET_BIND");
  const labels = {"workinants.rehearsal": "p0c-local-f0", "workinants.rehearsal.run": planned.run_id};
  for (const [key, expected] of Object.entries(labels)) requireLocal(planned.target.labels?.[key] === expected && observed.labels?.[key] === expected, "LIVE_RUN_LABELS");
  requireLocal(HASH.test(value.run_manifest_sha256), "RUN_MANIFEST_HASH");
  requireLocal(planned.tools?.node_version === "v24.22.1" && planned.tools.prisma_version === "7.10.1" && planned.tools.engine_commit === "d1b3f377ca835d73fd50954a5e22128b9ebdd6b8", "PINNED_TOOLS");
  return value;
}

export function validateUrl(raw) {
  requireLocal(typeof raw === "string" && raw.length > 0 && raw.length < 4096 && raw === raw.trim(), "PRIVATE_URL_SHAPE");
  let url;
  try { url = new URL(raw); } catch { throw new HeldFailure("PRIVATE_URL_SHAPE"); }
  requireLocal(url.protocol === "postgresql:" && url.hostname === "127.0.0.1" && url.port === "5432", "LOOPBACK_ONLY");
  requireLocal(url.username === "wa_migrator" && url.password.length > 0 && url.pathname === "/wa_p0c_rehearsal" && !url.hash, "MIGRATOR_DATABASE_ONLY");
  const entries = [...url.searchParams];
  requireLocal(entries.length >= 1 && entries.length <= 2 && url.searchParams.getAll("schema").length === 1 && url.searchParams.get("schema") === "public", "PRIVATE_LEDGER_SCHEMA");
  requireLocal(entries.every(([key, value]) => key === "schema" && value === "public" || key === "sslmode" && value === "disable") && url.searchParams.getAll("sslmode").length <= 1, "URL_OPTIONS_DENIED");
  return raw;
}

export function readNoFollow(filename, privateFile = false) {
  let descriptor;
  try {
    descriptor = fs.openSync(filename, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
    const info = fs.fstatSync(descriptor);
    requireLocal(info.isFile() && info.uid === 0 && (info.mode & 0o022) === 0 && (!privateFile || (info.mode & 0o777) === 0o600), "FILE_OWNER_MODE");
    return fs.readFileSync(descriptor);
  } catch (error) {
    throw error instanceof HeldFailure ? error : new HeldFailure("FILE_UNAVAILABLE");
  } finally { if (descriptor !== undefined) fs.closeSync(descriptor); }
}

function listFiles(directory) {
  const result = [];
  function walk(current, relative) {
    const info = fs.lstatSync(current);
    requireLocal(info.uid === 0 && !info.isSymbolicLink() && (info.mode & 0o022) === 0, "TREE_OWNER_MODE");
    if (info.isFile()) result.push(relative);
    else {
      requireLocal(info.isDirectory(), "TREE_REGULAR_FILES_ONLY");
      for (const entry of fs.readdirSync(current)) walk(current + "/" + entry, relative ? relative + "/" + entry : entry);
    }
  }
  walk(directory, "");
  return result.sort();
}

function sourceFile(relative) {
  requireLocal(typeof relative === "string" && relative.length > 0 && !relative.includes("\\") && !relative.startsWith("/") && relative.split("/").every(part => part && part !== "." && part !== ".."), "RELATIVE_PATH");
  return relative;
}

export function verifyInputs(attestation, io, identity) {
  validateAttestation(attestation);
  requireLocal(identity.platform === "linux" && identity.arch === "x64" && identity.node === "v24.22.1", "LINUX_PINNED_NODE_REQUIRED");
  requireLocal(identity.hostname === attestation.observed.container_id.slice(0, 12), "CONTAINER_HOSTNAME");
  requireLocal(io.mountInfo().split("\n").some(line => line.split(" ")[4] === PRIVATE_ROOT && line.includes(" - tmpfs ")), "PRIVATE_TMPFS_REQUIRED");
  const planned = attestation.planned;
  const history = JSON.parse(io.read(SOURCE_ROOT + "/prisma/foundation/history-manifest.json").toString("utf8"));
  requireLocal(history.schema === "workinants.local-f0-history.v1" && history.run_id === planned.run_id && history.run_manifest_sha256 === attestation.run_manifest_sha256, "HISTORY_RUN_IDENTITY");
  requireLocal(history.migrations === "prisma/foundation/migrations" && history.migration_id === planned.migration?.id && /^[0-9]{14}_[a-z][a-z0-9_]{0,79}$/.test(history.migration_id), "ONE_HISTORY_REQUIRED");
  requireLocal(history.source_sql_sha256 === planned.source?.integrated_sql_sha256, "SOURCE_PIN_REQUIRED");
  requireLocal(history.foundation_schema === "prisma/review/foundation-candidate.prisma", "FOUNDATION_SCHEMA_ONLY");
  const files = history.files_sha256;
  requireLocal(files && typeof files === "object" && !Array.isArray(files), "HISTORY_FILE_MAP");
  const reviewedRuntime = planned.source.runtime_files_sha256;
  const runtimePaths = ["prisma.local-f0.config.mjs", "scripts/sql-review/local-f0-migrate-guard.mjs", "scripts/sql-review/local-f0-migrate-runner.mjs"];
  requireLocal(reviewedRuntime && !Array.isArray(reviewedRuntime) &&
    JSON.stringify(Object.keys(reviewedRuntime).sort()) === JSON.stringify(runtimePaths.sort()) &&
    runtimePaths.every(relative => HASH.test(reviewedRuntime[relative]) && files[relative] === reviewedRuntime[relative]), "REVIEWED_RUNTIME_DRIFT");
  for (const [relative, expected] of Object.entries(files)) {
    requireLocal(HASH.test(expected), "SOURCE_FILE_HASH");
    requireLocal(sha256(io.read(SOURCE_ROOT + "/" + sourceFile(relative))) === expected, "SOURCE_FILE_DRIFT");
  }
  const migrationFile = history.migrations + "/" + history.migration_id + "/migration.sql";
  requireLocal(files[migrationFile] === history.source_sql_sha256 && files[history.foundation_schema] === planned.source.foundation_schema_sha256, "REVIEWED_SQL_SCHEMA_REQUIRED");
  for (const required of ["prisma.local-f0.config.mjs", "scripts/sql-review/local-f0-migrate-guard.mjs", "scripts/sql-review/local-f0-migrate-runner.mjs", "prisma/foundation/migrations/migration_lock.toml"]) requireLocal(HASH.test(files[required]), "RUNTIME_SOURCE_MAP_INCOMPLETE");
  const expectedSources = [migrationFile, history.foundation_schema, "prisma.local-f0.config.mjs", "scripts/sql-review/local-f0-migrate-guard.mjs", "scripts/sql-review/local-f0-migrate-runner.mjs", history.migrations + "/migration_lock.toml"].sort();
  requireLocal(JSON.stringify(Object.keys(files).sort()) === JSON.stringify(expectedSources), "EXACT_SOURCE_CUT_REQUIRED");
  requireLocal(JSON.stringify(io.listFiles(SOURCE_ROOT + "/" + history.migrations).sort()) === JSON.stringify([history.migration_id + "/migration.sql", "migration_lock.toml"].sort()), "UNLISTED_HISTORY_DENIED");
  const tools = planned.tools.files_sha256;
  requireLocal(tools && typeof tools === "object" && !Array.isArray(tools), "TOOL_FILE_MAP");
  for (const required of ["node/bin/node", "schema-engine", "node_modules/prisma/build/index.js", "node_modules/prisma/build/cli.js", "node_modules/prisma/config.js", "node_modules/prisma/package.json"]) requireLocal(HASH.test(tools[required]), "TOOL_FILE_MAP");
  requireLocal(JSON.stringify(io.listFiles(TOOLS_ROOT).sort()) === JSON.stringify(Object.keys(tools).sort()), "EXACT_TOOL_CLOSURE_REQUIRED");
  for (const [relative, expected] of Object.entries(tools)) requireLocal(HASH.test(expected) && sha256(io.read(TOOLS_ROOT + "/" + sourceFile(relative))) === expected, "TOOL_FILE_DRIFT");
  const prisma = JSON.parse(io.read(TOOLS_ROOT + "/node_modules/prisma/package.json").toString("utf8"));
  requireLocal(prisma.version === "7.10.1", "PRISMA_VERSION");
  const databaseUrl = validateUrl(io.readPrivate(URL_FILE).toString("utf8"));
  return {schema: path.posix.join(SOURCE_ROOT, history.foundation_schema),
    migrations: path.posix.join(SOURCE_ROOT, history.migrations), databaseUrl,
    migrationId: history.migration_id, config: SOURCE_ROOT + "/prisma.local-f0.config.mjs",
    cli: TOOLS_ROOT + "/node_modules/prisma/build/index.js", engine: TOOLS_ROOT + "/schema-engine",
    configLibrary: TOOLS_ROOT + "/node_modules/prisma/config.js"};
}

export function loadLocalF0Config() {
  try {
    const privateDirectory = fs.lstatSync(PRIVATE_ROOT);
    requireLocal(privateDirectory.isDirectory() && !privateDirectory.isSymbolicLink() && privateDirectory.uid === 0 && (privateDirectory.mode & 0o777) === 0o700, "PRIVATE_DIRECTORY_OWNER_MODE");
    const attestation = JSON.parse(readNoFollow(ATTESTATION, true).toString("utf8"));
    return verifyInputs(attestation,
      {read: filename => readNoFollow(filename), readPrivate: filename => readNoFollow(filename, true), listFiles, mountInfo: () => fs.readFileSync("/proc/self/mountinfo", "utf8")},
      {platform: process.platform, arch: process.arch, node: process.version, hostname: os.hostname()});
  } catch (error) { throw error instanceof HeldFailure ? error : new HeldFailure("INVALID_LOCAL_CONFIGURATION"); }
}
