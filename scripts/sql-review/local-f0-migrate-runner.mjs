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
    CHECKPOINT_DISABLE: "1", PRISMA_HIDE_UPDATE_MESSAGE: "1",
    PRISMA_SCHEMA_ENGINE_BINARY: local.engine};
}

export function summarizeProcess(result, operation) {
  const output = String(result.stdout || "") + "\n" + String(result.stderr || "");
  const knownCodes = [...new Set(output.split("\n").map(line => line.match(/^\s*(?:Error:|Error code:)\s*(P(?:1000|1001|1002|1003|1008|1010|1011|1012|1013|1014|1015|1016|1017|3000|3001|3002|3003|3004|3005|3006|3007|3008|3009|3010|3011|3012|3013|3014|3015|3016|3017|3018|3019|3020|3021|3022))(?::|\s|$)/)?.[1]).filter(Boolean))].sort();
  // Only the engine's explicit diagnostic header counts. SQL, passwords or
  // arbitrary messages containing five-character strings supply no SQLSTATE.
  const sqlstates = [...new Set(output.split("\n").map(line => line.match(/^\s*Database error code:\s*(42501|42703|22012|P0001|23503|23505|23514)\s*$/)?.[1]).filter(Boolean))].sort();
  const closed = !result.error && !result.signal && Number.isInteger(result.status);
  return {schema: "workinants.local-f0-migrate-result.v1", operation,
    status: closed ? (result.status === 0 ? "CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS" : "CLI_FAILED_STOP_AND_INSPECT") : "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE",
    exit_code: closed ? result.status : null, prisma_codes: knownCodes, sqlstates,
    no_pending_message_observed: operation === "deploy" && result.status === 0 && /(?:^|\n)No pending migrations to apply\.\s*(?:\n|$)/.test(output),
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
    return summary.exit_code === 0 ? 0 : 1;
  } catch (error) {
    (dependencies.emit || (value => process.stdout.write(JSON.stringify(value) + "\n")))({
      schema: "workinants.local-f0-migrate-result.v1", status: "REFUSED_OR_INCOMPLETE",
      code: error instanceof HeldFailure ? error.code : "INVALID_LOCAL_INPUT_OR_IO", raw_output_discarded: true,
      database_qualification_claimed: false,
    });
    return 1;
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) process.exitCode = main();
