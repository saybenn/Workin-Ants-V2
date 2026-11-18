// Dormant in-container Prisma launcher. Importing this module runs no process.
import fs from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { ATTESTATION, PRIVATE_ROOT, TOOLS_ROOT, HeldFailure, requireLocal,
  validateAttestation, loadLocalF0Config, readNoFollow, sha256 } from "./local-f0-migrate-guard.mjs";

export function validateRecovery(attestation) {
  const recovery = attestation.recovery;
  const proof = recovery?.proof;
  requireLocal(recovery && /^[0-9a-f]{64}$/.test(recovery.proof_sha256), "REVIEWED_ROLLBACK_PROOF_REQUIRED");
  requireLocal(proof?.schema === "workinants.local-f0-reviewed-rollback.v1" &&
    proof.run_id === attestation.planned.run_id && proof.container_id === attestation.observed.container_id &&
    proof.migration_id === attestation.planned.migration.id &&
    proof.source_sql_sha256 === attestation.planned.source.integrated_sql_sha256, "ROLLBACK_PROOF_IDENTITY");
  requireLocal(proof.disposition === "REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK" &&
    proof.backend_closed === true && proof.application_transaction_rolled_back === true &&
    proof.application_object_count === 0 && proof.failed_migration_rows === 1 &&
    proof.finished_migration_rows === 0 && proof.rolled_back_migration_rows === 0 &&
    proof.failed_row_checksum === attestation.planned.source.integrated_sql_sha256 &&
    /^[0-9a-f]{64}$/.test(proof.catalog_evidence_sha256) &&
    /^[0-9a-f]{64}$/.test(proof.ledger_evidence_sha256), "INDEPENDENT_ROLLBACK_REVIEW_REQUIRED");
  return proof;
}

export function prismaArguments(operation, local, attestation) {
  requireLocal(["deploy", "status", "resolve-rolled-back"].includes(operation), "OPERATION_DENIED");
  if (operation === "resolve-rolled-back") {
    validateRecovery(attestation);
    return [local.cli, "migrate", "resolve", "--rolled-back", local.migrationId, "--config", local.config];
  }
  return [local.cli, "migrate", operation, "--config", local.config];
}

export function childEnvironment(local) {
  // Rebuild instead of filtering: no parent DB URL, password, proxy, Node loader,
  // root dotenv, config override or additional Prisma binary can enter a child.
  return {PATH: TOOLS_ROOT + "/node/bin:/usr/bin:/bin", HOME: PRIVATE_ROOT,
    XDG_CACHE_HOME: PRIVATE_ROOT + "/cache", LANG: "C.UTF-8", CI: "1",
    NO_COLOR: "1", NODE_DISABLE_COLORS: "1", TERM: "dumb",
    CHECKPOINT_DISABLE: "1", PRISMA_HIDE_UPDATE_MESSAGE: "1",
    PRISMA_SCHEMA_ENGINE_BINARY: local.engine};
}

const PRISMA_CODES = new Set("P1000 P1001 P1002 P1003 P1008 P1010 P1011 P1012 P1013 P1014 P1015 P1016 P1017 P3000 P3001 P3002 P3003 P3004 P3005 P3006 P3007 P3008 P3009 P3010 P3011 P3012 P3013 P3014 P3015 P3016 P3017 P3018 P3019 P3020 P3021 P3022".split(" "));
const SQLSTATES = new Set(["42501", "42703", "22012", "P0001", "23503", "23505", "23514"]);

function normalizeDiagnosticText(value) {
  if (value === null || value === undefined) value = "";
  if (typeof value !== "string") return {valid: false, stripped: false, text: ""};
  let stripped = false;
  // Consume only complete seven-bit Select Graphic Rendition sequences. Do not
  // repair a partial ESC/CSI, concatenate streams, or strip another control.
  const text = value.replace(/\x1b\[[0-9;:]*m/g, () => {stripped = true; return "";}).replace(/\r\n/g, "\n");
  const rejected = /[\p{Cc}\p{Cf}\p{Zl}\p{Zp}\ud800-\udfff\ufffd]/u.test(text.replace(/[\t\n]/g, ""));
  return {valid: !rejected, stripped, text: rejected ? "" : text};
}

export function summarizeProcess(result, operation) {
  const streams = [normalizeDiagnosticText(result.stdout), normalizeDiagnosticText(result.stderr)];
  const textValid = streams.every(stream => stream.valid);
  const lines = textValid ? streams.flatMap(stream => stream.text.split("\n")) : [];
  const prismaHeaders = lines.filter(line => /^[ \t]*(?:Error:|Error code:)/.test(line));
  const databaseHeaders = lines.filter(line => /^[ \t]*Database error code:/.test(line));
  const prismaMatches = prismaHeaders.map(line => line.match(/^[ \t]*(?:Error:|Error code:)[ \t]*(P[0-9]{4})(?:[ \t]*|:[ \t]+[^\r\n]*)$/));
  const databaseMatches = databaseHeaders.map(line => line.match(/^[ \t]*Database error code:[ \t]*([0-9A-Z]{5})[ \t]*$/));
  const format = {text_valid: textValid, sgr_stripped: streams.some(stream => stream.stripped),
    headers_valid: textValid && [...prismaMatches, ...databaseMatches].every(Boolean),
    prisma_header_present: prismaHeaders.length > 0, prisma_header_unique: prismaHeaders.length === 1,
    database_header_present: databaseHeaders.length > 0, database_header_unique: databaseHeaders.length === 1};
  const accepted = format.text_valid && format.headers_valid && prismaHeaders.length <= 1 && databaseHeaders.length <= 1;
  const prismaCode = accepted && prismaMatches[0]?.[1];
  const sqlstate = accepted && databaseMatches[0]?.[1];
  const knownCodes = prismaCode && PRISMA_CODES.has(prismaCode) ? [prismaCode] : [];
  const sqlstates = sqlstate && SQLSTATES.has(sqlstate) ? [sqlstate] : [];
  const closed = !result.error && !result.signal && Number.isInteger(result.status);
  return {schema: "workinants.local-f0-migrate-result.v2", operation,
    status: !closed ? "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE" : !accepted ? "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT" : result.status === 0 ? "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS" : "CLI_FAILED_STOP_AND_INSPECT",
    exit_code: closed ? result.status : null, prisma_codes: knownCodes, sqlstates,
    diagnostic_format: format,
    no_pending_message_observed: accepted && closed && operation === "deploy" && result.status === 0 && prismaHeaders.length === 0 && databaseHeaders.length === 0 && lines.filter(line => /^[ \t]*No pending migrations to apply\.[ \t]*$/.test(line)).length === 1,
    raw_output_discarded: true, database_qualification_claimed: false};
}

function storeAttestation(raw, attestation) {
  requireLocal(raw.length > 0 && raw.length <= 4 * 1024 * 1024, "ATTESTATION_SIZE");
  validateAttestation(attestation);
  const directory = fs.lstatSync(PRIVATE_ROOT);
  requireLocal(directory.isDirectory() && !directory.isSymbolicLink() && directory.uid === 0 && (directory.mode & 0o777) === 0o700, "PRIVATE_DIRECTORY_OWNER_MODE");
  requireLocal(fs.readFileSync("/proc/self/mountinfo", "utf8").split("\n").some(line => line.split(" ")[4] === PRIVATE_ROOT && line.includes(" - tmpfs ")), "PRIVATE_TMPFS_REQUIRED");
  // Attestation contains no credential. Same run may replace an earlier reviewed
  // recovery attestation; symlinks, wrong owners/modes and cross-run files reject.
  if (fs.existsSync(ATTESTATION)) {
    const previous = JSON.parse(readNoFollow(ATTESTATION, true).toString("utf8"));
    requireLocal(previous.planned?.run_id === attestation.planned.run_id && previous.observed?.container_id === attestation.observed.container_id, "ATTESTATION_CROSS_RUN_DENIED");
    fs.unlinkSync(ATTESTATION);
  }
  const descriptor = fs.openSync(ATTESTATION, fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_WRONLY | fs.constants.O_NOFOLLOW, 0o600);
  try { fs.writeFileSync(descriptor, raw); } finally { fs.closeSync(descriptor); }
}

export function main(argv = process.argv.slice(2), dependencies = {}) {
  if (argv.length === 1 && argv[0] === "--help") {
    process.stdout.write("Dormant local F0 launcher; requires --execute-reviewed-local-f0 --operation deploy|status|resolve-rolled-back and verified attestation on stdin. No hosted target or credential arguments.\n");
    return 0;
  }
  try {
    requireLocal(argv.length === 3 && argv[0] === "--execute-reviewed-local-f0" && argv[1] === "--operation" && ["deploy", "status", "resolve-rolled-back"].includes(argv[2]), "EXPLICIT_EXECUTION_REQUIRED");
    const raw = (dependencies.readStdin || (() => fs.readFileSync(0)))();
    const attestation = JSON.parse(raw.toString("utf8"));
    (dependencies.store || storeAttestation)(raw, attestation);
    const local = (dependencies.load || loadLocalF0Config)();
    const arguments_ = prismaArguments(argv[2], local, attestation);
    const result = (dependencies.spawn || spawnSync)(TOOLS_ROOT + "/node/bin/node", arguments_, {
      cwd: "/run/wa-f0-source", env: childEnvironment(local), encoding: "utf8",
      shell: false, timeout: 120000, maxBuffer: 8 * 1024 * 1024,
    });
    const summary = summarizeProcess(result, argv[2]);
    summary.run_id = attestation.planned.run_id;
    summary.container_id = attestation.observed.container_id;
    summary.source_sql_sha256 = attestation.planned.source.integrated_sql_sha256;
    summary.attestation_sha256 = sha256(raw);
    (dependencies.emit || (value => process.stdout.write(JSON.stringify(value) + "\n")))(summary);
    return summary.exit_code === 0 && summary.status === "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS" ? 0 : 1;
  } catch (error) {
    (dependencies.emit || (value => process.stdout.write(JSON.stringify(value) + "\n")))({
      schema: "workinants.local-f0-migrate-result.v2", status: "REFUSED_OR_INCOMPLETE",
      code: error instanceof HeldFailure ? error.code : "INVALID_LOCAL_INPUT_OR_IO", raw_output_discarded: true,
      database_qualification_claimed: false,
    });
    return 1;
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) process.exitCode = main();
