// Environment-free guard tests: injected byte maps/process mocks only.
import assert from "node:assert/strict";
import { HeldFailure, IMAGE, SOURCE_ROOT, TOOLS_ROOT, URL_FILE, sha256, validateUrl,
  verifyInputs } from "./local-f0-migrate-guard.mjs";
import { childEnvironment, main, prismaArguments, summarizeProcess } from "./local-f0-migrate-runner.mjs";

let checks = 0;
function check(name, callback) { callback(); checks += 1; }
function refuses(callback, code) { assert.throws(callback, error => error instanceof HeldFailure && error.code === code); }
const clone = value => structuredClone(value);
const run = "12345678-1234-1234-1234-123456789abc";
const container = "a".repeat(64);
const migration = "20261117000000_local_f0_initial";

function fixture() {
  const schema = Buffer.from("schema fixture");
  const sql = Buffer.from("integrated fixture");
  const sources = {
    "prisma.local-f0.config.mjs": Buffer.from("config fixture"),
    "scripts/sql-review/local-f0-migrate-guard.mjs": Buffer.from("guard fixture"),
    "scripts/sql-review/local-f0-migrate-runner.mjs": Buffer.from("runner fixture"),
    "prisma/review/foundation-candidate.prisma": schema,
    "prisma/foundation/migrations/migration_lock.toml": Buffer.from('provider = "postgresql"\n'),
    ["prisma/foundation/migrations/" + migration + "/migration.sql"]: sql,
  };
  const tools = Object.fromEntries(["node/bin/node", "schema-engine", "node_modules/prisma/build/index.js", "node_modules/prisma/build/cli.js", "node_modules/prisma/config.js"].map(name => [name, Buffer.from(name)]));
  tools["node_modules/prisma/package.json"] = Buffer.from('{"version":"7.10.1"}');
  const planned = {schema: "workinants.local-f0-run.v1", run_id: run, purpose: "LOCAL_F0_MIGRATION_REHEARSAL",
    target: {image: IMAGE, database: "wa_p0c_rehearsal", network: "none", container_name: "wa-p0c-offline", volume_name: "wa-p0c-offline-data",
      bootstrap_secret_host_path: "C:\\task\\external-secret\\bootstrap-password",
      labels: {"workinants.rehearsal": "p0c-local-f0", "workinants.rehearsal.run": run}},
    migration: {id: migration, history: "prisma/foundation/migrations"},
    source: {integrated_sql_sha256: sha256(sql), foundation_schema_sha256: sha256(schema),
      runtime_files_sha256: Object.fromEntries(["prisma.local-f0.config.mjs", "scripts/sql-review/local-f0-migrate-guard.mjs", "scripts/sql-review/local-f0-migrate-runner.mjs"].map(name => [name, sha256(sources[name])]))},
    tools: {node_version: "v24.22.1", prisma_version: "7.10.1", engine_commit: "d1b3f377ca835d73fd50954a5e22128b9ebdd6b8",
      files_sha256: Object.fromEntries(Object.entries(tools).map(([name, bytes]) => [name, sha256(bytes)]))}};
  const attestation = {schema: "workinants.local-f0-live-attestation.v1", planned,
    run_manifest_sha256: "b".repeat(64), observed: {endpoint: "npipe:////./pipe/dockerDesktopLinuxEngine", context: "desktop-linux",
      container_id: container, container_name: planned.target.container_name, volume_name: planned.target.volume_name,
      image: IMAGE, network: "none", published_ports: false, labels: clone(planned.target.labels), bootstrap_secret_host_path: planned.target.bootstrap_secret_host_path}};
  const history = {schema: "workinants.local-f0-history.v1", run_id: run, run_manifest_sha256: attestation.run_manifest_sha256,
    migration_id: migration, migrations: planned.migration.history, foundation_schema: "prisma/review/foundation-candidate.prisma",
    source_sql_sha256: planned.source.integrated_sql_sha256,
    files_sha256: Object.fromEntries(Object.entries(sources).map(([name, bytes]) => [name, sha256(bytes)]))};
  const identity = {platform: "linux", arch: "x64", node: "v24.22.1", hostname: container.slice(0, 12)};
  const io = {mountInfo: () => "1 2 0:3 / /run/wa-secrets rw - tmpfs tmpfs rw\n",
    readPrivate: filename => {assert.equal(filename, URL_FILE); return Buffer.from("postgresql://wa_migrator:CANARY@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&sslmode=disable");},
    listFiles: root => root === TOOLS_ROOT ? Object.keys(tools) : [migration + "/migration.sql", "migration_lock.toml"],
    read: filename => {
      if (filename === SOURCE_ROOT + "/prisma/foundation/history-manifest.json") return Buffer.from(JSON.stringify(history));
      const map = filename.startsWith(SOURCE_ROOT + "/") ? sources : tools;
      const key = filename.slice((filename.startsWith(SOURCE_ROOT + "/") ? SOURCE_ROOT : TOOLS_ROOT).length + 1);
      assert.ok(map[key], "unlisted fixture read"); return map[key];
    }};
  return {attestation, history, sources, tools, identity, io};
}

check("exact local fixture accepted", () => { const f = fixture(); const value = verifyInputs(f.attestation, f.io, f.identity); assert.equal(value.migrationId, migration); assert.equal(value.configLibrary, TOOLS_ROOT + "/node_modules/prisma/config.js"); });
for (const url of [
  "postgresql://wa_migrator:x@db.supabase.co:5432/wa_p0c_rehearsal?schema=public",
  "postgresql://wa_migrator:x@localhost:5432/wa_p0c_rehearsal?schema=public",
  "postgresql://wa_migrator:x@127.0.0.1/wa_p0c_rehearsal?schema=public",
  "postgresql://postgres:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public",
  "postgresql://wa_migrator@127.0.0.1:5432/wa_p0c_rehearsal?schema=public",
  "postgresql://wa_migrator:x@127.0.0.1:5432/other?schema=public",
  "postgresql://wa_migrator:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=app",
  "postgresql://wa_migrator:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&host=remote",
  "postgresql://wa_migrator:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&schema=public",
  "postgresql://wa_migrator:x@127.0.0.1:5432/wa_p0c_rehearsal?schema=public\n",
]) check("unsafe URL refused", () => assert.throws(() => validateUrl(url), HeldFailure));

for (const [mutate, code] of [
  [f => {f.identity.platform = "win32";}, "LINUX_PINNED_NODE_REQUIRED"],
  [f => {f.identity.arch = "arm64";}, "LINUX_PINNED_NODE_REQUIRED"],
  [f => {f.identity.node = "v24.18.1";}, "LINUX_PINNED_NODE_REQUIRED"],
  [f => {f.identity.hostname = "different";}, "CONTAINER_HOSTNAME"],
  [f => {f.attestation.observed.endpoint = "ssh://remote";}, "LOCAL_ENDPOINT"],
  [f => {f.attestation.observed.volume_name = "other";}, "LIVE_RESOURCE_IDENTITY"],
  [f => {f.attestation.observed.image = "postgres:latest";}, "LIVE_PRIVATE_TARGET"],
  [f => {f.attestation.observed.network = "bridge";}, "LIVE_PRIVATE_TARGET"],
  [f => {f.attestation.observed.bootstrap_secret_host_path = "C:\\wrong\\secret";}, "LIVE_BOOTSTRAP_SECRET_BIND"],
  [f => {f.attestation.observed.published_ports = true;}, "LIVE_PRIVATE_TARGET"],
  [f => {f.attestation.observed.labels["workinants.rehearsal.run"] = "wrong";}, "LIVE_RUN_LABELS"],
  [f => {f.io.mountInfo = () => "1 2 0:3 / /run/wa-secrets rw - ext4 /dev/x rw\n";}, "PRIVATE_TMPFS_REQUIRED"],
  [f => {f.history.run_id = "wrong";}, "HISTORY_RUN_IDENTITY"],
  [f => {f.history.source_sql_sha256 = "c".repeat(64);}, "SOURCE_PIN_REQUIRED"],
  [f => {f.history.foundation_schema = "../other";}, "FOUNDATION_SCHEMA_ONLY"],
  [f => {f.attestation.planned.source.runtime_files_sha256["prisma.local-f0.config.mjs"] = "c".repeat(64);}, "REVIEWED_RUNTIME_DRIFT"],
  [f => {f.attestation.planned.source.runtime_files_sha256 = {};}, "REVIEWED_RUNTIME_DRIFT"],
  [f => {f.sources["prisma.local-f0.config.mjs"] = Buffer.from("changed");}, "SOURCE_FILE_DRIFT"],
  [f => {f.tools["schema-engine"] = Buffer.from("changed");}, "TOOL_FILE_DRIFT"],
  [f => {f.io.listFiles = root => root === TOOLS_ROOT ? Object.keys(f.tools) : [migration + "/migration.sql", "migration_lock.toml", "unreviewed/migration.sql"];}, "UNLISTED_HISTORY_DENIED"],
  [f => {f.io.listFiles = root => root === TOOLS_ROOT ? [...Object.keys(f.tools), "unlisted.js"] : [migration + "/migration.sql", "migration_lock.toml"];}, "EXACT_TOOL_CLOSURE_REQUIRED"],
]) check(code, () => {const f = fixture(); mutate(f); refuses(() => verifyInputs(f.attestation, f.io, f.identity), code);});

check("no execution before exact opt-in", () => { let touched = false, result; const rc = main([], {readStdin: () => {touched = true; throw Error("CANARY");}, emit: value => {result = value;}}); assert.equal(rc, 1); assert.equal(touched, false); assert.equal(result.code, "EXPLICIT_EXECUTION_REQUIRED"); });
check("no environment secret or force-color inheritance", () => { const previous = process.env.FORCE_COLOR; process.env.FORCE_COLOR = "CANARY"; try { const result = childEnvironment({engine: "/fixed/engine"}); assert.equal(result.DATABASE_URL, undefined); assert.equal(result.NODE_OPTIONS, undefined); assert.equal(result.PGPASSWORD, undefined); assert.equal(result.FORCE_COLOR, undefined); assert.equal(result.PRISMA_SCHEMA_ENGINE_BINARY, "/fixed/engine"); assert.equal(result.NO_COLOR, "1"); assert.equal(result.NODE_DISABLE_COLORS, "1"); assert.equal(result.TERM, "dumb"); } finally {if (previous === undefined) delete process.env.FORCE_COLOR; else process.env.FORCE_COLOR = previous;} });
check("standard deploy args only", () => { const f = fixture(); const local = verifyInputs(f.attestation, f.io, f.identity); const args = prismaArguments("deploy", local, f.attestation); assert.deepEqual(args.slice(1, 3), ["migrate", "deploy"]); assert.equal(args.join(" ").includes("CANARY"), false); refuses(() => prismaArguments("reset", local, f.attestation), "OPERATION_DENIED"); refuses(() => prismaArguments("resolve-rolled-back", local, f.attestation), "REVIEWED_ROLLBACK_PROOF_REQUIRED"); });
check("standard reviewed recovery args", () => { const f = fixture(); f.attestation.recovery = {proof_sha256: "c".repeat(64), proof: {schema: "workinants.local-f0-reviewed-rollback.v1", run_id: run, container_id: container, migration_id: migration, source_sql_sha256: f.attestation.planned.source.integrated_sql_sha256, disposition: "REVIEWED_FOR_STANDARD_RESOLVE_ROLLED_BACK", backend_closed: true, application_transaction_rolled_back: true, application_object_count: 0, failed_migration_rows: 1, finished_migration_rows: 0, rolled_back_migration_rows: 0, failed_row_checksum: f.attestation.planned.source.integrated_sql_sha256, catalog_evidence_sha256: "d".repeat(64), ledger_evidence_sha256: "e".repeat(64)}}; const local = verifyInputs(f.attestation, f.io, f.identity); assert.deepEqual(prismaArguments("resolve-rolled-back", local, f.attestation).slice(1, 5), ["migrate", "resolve", "--rolled-back", migration]); f.attestation.recovery.proof.application_object_count = 1; refuses(() => prismaArguments("resolve-rolled-back", local, f.attestation), "INDEPENDENT_ROLLBACK_REVIEW_REQUIRED"); });
check("raw process errors discarded", () => {const value = summarizeProcess({status: 1, stdout: "CANARY postgresql://secret@host", stderr: "Error: P3018\nDatabase error code: 42703\npassword CANARY"}, "deploy"); assert.deepEqual(value.prisma_codes, ["P3018"]); assert.deepEqual(value.sqlstates, ["42703"]); assert.equal(JSON.stringify(value).includes("CANARY"), false);});
check("arbitrary substrings never supply diagnostics", () => {const value = summarizeProcess({status: 1, stdout: "password P3018 42703", stderr: "query contains P0001"}, "deploy"); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []);});
check("complete SGR-only colored CRLF headers are decoded in memory", () => {const value = summarizeProcess({status: 1, stdout: "CANARY postgresql://private@host\r\n", stderr: "\x1b[1;31mError:\x1b[0m \x1b[38:2::255:0:0mP3018\x1b[m\r\n\tDatabase error code: \x1b[33m42703\x1b[0m\r\n"}, "deploy"); assert.deepEqual(value.prisma_codes, ["P3018"]); assert.deepEqual(value.sqlstates, ["42703"]); assert.deepEqual(value.diagnostic_format, {text_valid: true, sgr_stripped: true, headers_valid: true, prisma_header_present: true, prisma_header_unique: true, database_header_present: true, database_header_unique: true}); assert.equal(value.schema, "workinants.local-f0-migrate-result.v2"); assert.equal(JSON.stringify(value).includes("CANARY"), false); assert.equal(JSON.stringify(value).includes("private@host"), false);});
check("inline Prisma header suffix is discarded", () => {const value = summarizeProcess({status: 1, stderr: "Error: P1001: CANARY private database name\n"}, "deploy"); assert.deepEqual(value.prisma_codes, ["P1001"]); assert.equal(JSON.stringify(value).includes("CANARY"), false);});
for (const line of ['"Error: P3018"', "'Database error code: 42703'", "> Error: P3018", "| Database error code: 42703", "SELECT 'Error: P3018'", "\\u001b[31mError: P3018", "prefix Error: P3018", '"No pending migrations to apply."']) check("quoted or embedded line cannot become a diagnostic header", () => {const value = summarizeProcess({status: 0, stdout: "\x1b[31m" + line + "\x1b[0m\n"}, "deploy"); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []); assert.equal(value.no_pending_message_observed, false); assert.equal(value.diagnostic_format.prisma_header_present, false); assert.equal(value.diagnostic_format.database_header_present, false);});
for (const control of ["\x1b[2J", "\x1b[1A", "\x1b]0;CANARY\x07", "\x1b]8;;https://CANARY\x1b\\", "\x1b[31", "\x1b[?25m", "\x1b[31X", "\x1b", "\x9b31m", "\x00", "\x08", "\x0b", "\x7f", "\r", "\u202e", "\u2028", "\ufffd"]) check("non-SGR, malformed or other control rejects all output claims", () => {const value = summarizeProcess({status: 0, stdout: "\x1b[31mNo pending migrations to apply.\x1b[0m\n", stderr: "Error: P3018\nDatabase error code: 42703\n" + control}, "deploy"); assert.equal(value.diagnostic_format.text_valid, false); assert.equal(value.diagnostic_format.headers_valid, false); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []); assert.equal(value.no_pending_message_observed, false); assert.equal(value.status, "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT"); assert.equal(value.exit_code, 0); assert.equal(JSON.stringify(value).includes("CANARY"), false);});
check("partial SGR is not completed across separate streams", () => {const value = summarizeProcess({status: 1, stdout: "\x1b[31", stderr: "mError: P3018\x1b[0m\nDatabase error code: 42703\n"}, "deploy"); assert.equal(value.diagnostic_format.text_valid, false); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []);});
for (const text of ["Error: P3018\nError: P3018\nDatabase error code: 42703\n", "Error: P3018\nDatabase error code: 42703\nDatabase error code: 42501\n"]) check("duplicate headers remain explicit ambiguity instead of set deduplication", () => {const value = summarizeProcess({status: 1, stderr: text}, "deploy"); assert.equal(value.diagnostic_format.text_valid, true); assert.equal(value.diagnostic_format.headers_valid, true); assert.equal(value.diagnostic_format.prisma_header_unique && value.diagnostic_format.database_header_unique, false); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []); assert.equal(value.status, "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT");});
for (const text of ["Error: P3018garbage\n", "Error: P3018 CANARY\n", "Database error code: 42703 trailing CANARY\n"]) check("malformed header shape rejects code claims without retaining a message", () => {const value = summarizeProcess({status: 1, stderr: text}, "deploy"); assert.equal(value.diagnostic_format.text_valid, true); assert.equal(value.diagnostic_format.headers_valid, false); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []); assert.equal(JSON.stringify(value).includes("CANARY"), false);});
check("unsupported header codes do not escape the fixed allowlists", () => {const value = summarizeProcess({status: 1, stderr: "Error: P1999\nDatabase error code: XX999\n"}, "deploy"); assert.equal(value.diagnostic_format.headers_valid, true); assert.equal(value.diagnostic_format.prisma_header_unique, true); assert.equal(value.diagnostic_format.database_header_unique, true); assert.deepEqual(value.prisma_codes, []); assert.deepEqual(value.sqlstates, []);});
check("colored no-pending requires one clean exact line and no error header", () => {const value = summarizeProcess({status: 0, stdout: "\x1b[32mNo pending migrations to apply.\x1b[0m\r\n"}, "deploy"); assert.equal(value.no_pending_message_observed, true); assert.equal(value.diagnostic_format.sgr_stripped, true); for (const stdout of ["No pending migrations to apply.\nNo pending migrations to apply.\n", "No pending migrations to apply.\nError: P3018\n"]) assert.equal(summarizeProcess({status: 0, stdout}, "deploy").no_pending_message_observed, false);});
check("invalid output returns wrapper failure despite preserved CLI exit0", () => {const f = fixture(); const emitted = []; const rc = main(["--execute-reviewed-local-f0", "--operation", "deploy"], {readStdin: () => Buffer.from(JSON.stringify(f.attestation)), store: () => {}, load: () => verifyInputs(f.attestation, f.io, f.identity), spawn: () => ({status: 0, stdout: "No pending migrations to apply.\x1b[2J"}), emit: value => emitted.push(value)}); assert.equal(rc, 1); assert.equal(emitted[0].exit_code, 0); assert.equal(emitted[0].status, "CLI_OUTPUT_REJECTED_STOP_AND_INSPECT");});
check("timeout never claims closure", () => {const value = summarizeProcess({status: null, error: Error("CANARY"), signal: "SIGTERM"}, "deploy"); assert.equal(value.exit_code, null); assert.equal(value.status, "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE"); assert.equal(JSON.stringify(value).includes("CANARY"), false);});
check("safe mocked execution result", () => { const f = fixture(), emitted = []; let spawned; const rc = main(["--execute-reviewed-local-f0", "--operation", "deploy"], {readStdin: () => Buffer.from(JSON.stringify(f.attestation)), store: () => {}, load: () => verifyInputs(f.attestation, f.io, f.identity), spawn: (binary, args, options) => {spawned = {binary, args, options}; return {status: 0, stdout: "No pending migrations to apply.\n", stderr: ""};}, emit: value => emitted.push(value)}); assert.equal(rc, 0); assert.equal(emitted[0].no_pending_message_observed, true); assert.equal(JSON.stringify(spawned).includes("CANARY"), false); });

console.log(JSON.stringify({status: "PASS_ENVIRONMENT_FREE_ONLY", checks, database_contacted: false, process_executed: false}));
