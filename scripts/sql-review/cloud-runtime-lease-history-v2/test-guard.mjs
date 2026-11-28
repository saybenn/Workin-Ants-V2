// Real closed source and tool bytes with modeled Docker, kernel and Prisma.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {pathToFileURL} from "node:url";

const [source, tools, attestationPath] = process.argv.slice(2);
const base = path.join(source, "scripts/sql-review/cloud-runtime-lease-history-v2");
const guard = await import(pathToFileURL(path.join(base, "guard.mjs")));
const runner = await import(pathToFileURL(path.join(base, "runner.mjs")));
const raw = fs.readFileSync(attestationPath);
const attestation = guard.strictJson(raw);
const id = {platform: "linux", arch: "x64", node: process.version, hostname: "b".repeat(12), uid: 0};
const mounts = '11 10 0:5 / /run/wa-secrets rw,nodev,nosuid,noexec - tmpfs tmpfs rw,size=8192k,mode=700\n'
  + '12 10 0:6 /example /var/lib/postgresql/data rw,relatime - ext4 /dev/loop1 rw\n';
const url = "postgresql://wa_migrator:private-canary@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&sslmode=disable";

function translate(filename) {
  for (const [root, local] of [[guard.SOURCE_ROOT, source], [guard.TOOLS_ROOT, tools]]) {
    if (filename === root || filename.startsWith(root + "/")) {
      const target = path.join(local, filename.slice(root.length));
      assert.equal(fs.realpathSync(target), target);
      return target;
    }
  }
  throw Error("unexpected virtual path");
}

function filesUnder(directory, prefix = "") {
  const result = [];
  for (const entry of fs.readdirSync(directory, {withFileTypes: true})) {
    if (entry.isDirectory()) result.push(...filesUnder(path.join(directory, entry.name), prefix + entry.name + "/"));
    else {
      assert(entry.isFile());
      result.push(prefix + entry.name);
    }
  }
  return result;
}

const missing = () => { throw Object.assign(new Error("model"), {code: "ENOENT"}); };
const authorization = attestation.authorization;
let checks = 0;
let hashes = 0;
const check = f => { f(); checks++; };
const io = {
  mountInfo: () => mounts,
  loopbackOnly: () => true,
  bootstrapAbsent: () => guard.privateBootstrapAbsent(missing),
  listFiles: directory => filesUnder(translate(directory)),
  read: filename => fs.readFileSync(translate(filename)),
  readPrivate(filename) { assert.equal(filename, guard.URL_FILE); return Buffer.from(url); },
  toolHash(filename, relative, size) {
    hashes++;
    return guard.hashStableTool(translate(filename), relative, size, process.getuid());
  },
};
let local;
check(() => {
  local = guard.verifyInputs(attestation, io, id);
  assert.equal(hashes, 10300);
  assert.equal(local.databaseUrl, url);
  assert.equal(guard.RUNTIME.length, 3);
});

for (const mutate of [
  value => { value.schema = "workinants.cloud-f0-runtime-lease-history-live-attestation.v1"; },
  value => { value.planned.target.bootstrap_secret_host_path = "/workspace/scratch/old"; },
  value => { value.observed.bootstrap_readonly = true; },
  value => { value.observed.bootstrap_removed = false; },
  value => { value.observed.mount_destinations.push("/run/bootstrap-password"); },
  value => { value.observed.bootstrap.startup_gate_sha256 = "a".repeat(64); },
  value => { value.planned.target.bootstrap.tmpfs_options = "rw,nosuid,nodev,noexec,mode=0700,size=1m"; },
  value => { value.observed.daemon.daemon_id = "other-daemon"; },
  value => { value.authorization.packet_sha256 = "c".repeat(63); },
  value => { delete value.authorization.literal_review_sha256; },
  value => { value.run_manifest_sha256 = "a".repeat(64); },
]) check(() => {
  const edited = structuredClone(attestation);
  mutate(edited);
  assert.throws(() => guard.validateAttestation(edited), guard.HeldFailure);
});

for (const [bad, failure] of [
  [mounts.replace("size=8192k", "size=1024k"), /PRIVATE_TMPFS_FLAGS_OR_SIZE/],
  [mounts.replace(",noexec", ""), /PRIVATE_TMPFS_FLAGS_OR_SIZE/],
  [mounts.replace("tmpfs tmpfs", "ext4 tmpfs"), /PRIVATE_TMPFS_FLAGS_OR_SIZE/],
  [mounts.replace("data rw,relatime", "data ro,relatime"), /DATA_VOLUME_NOT_WRITABLE/],
  [mounts.replace("/var/lib/postgresql/data", "/some/other/data"), /EXACT_RUNTIME_MOUNTS/],
  [mounts + '13 10 0:6 /x /run/bootstrap-password ro - ext4 /dev/loop1 rw\n', /UNDECLARED_BOOTSTRAP_OR_DATA_MOUNT/],
  [mounts + '13 10 0:6 /x /run/wa-secrets/elsewhere ro - ext4 /dev/loop1 rw\n', /UNDECLARED_BOOTSTRAP_OR_DATA_MOUNT/],
]) check(() => assert.throws(() => guard.privateMounts(bad), failure));

check(() => assert.throws(() => guard.privateBootstrapAbsent(() => ({})), /BOOTSTRAP_CREDENTIAL_RETAINED/));
check(() => assert.throws(() => guard.privateBootstrapAbsent(file => {
  if (file.endsWith("/bootstrap-password")) missing();
  return {};
}), /BOOTSTRAP_CREDENTIAL_RETAINED/));
check(() => assert.throws(() => guard.privateBootstrapAbsent(() => {
  throw Object.assign(new Error("model"), {code: "EACCES"});
}), /BOOTSTRAP_ABSENCE_UNCONFIRMED/));
check(() => assert.throws(() => guard.verifyInputs(attestation, {...io, loopbackOnly: () => false}, id),
  /CONTAINER_LOOPBACK_ONLY/));

const flag = "--execute-reviewed-cloud-f0-runtime-lease-history-v2";
for (const operation of ["deploy", "status"]) check(() => {
  const input = Buffer.from(JSON.stringify({...attestation, operation}));
  const events = [];
  let receipt;
  const code = runner.main([flag, "--operation", operation], {
    readStdin() { events.push("stdin"); return input; },
    store() { events.push("model-private-store"); },
    load() { events.push("verified-inputs"); return local; },
    spawn(binary, args, options) {
      events.push("model-prisma");
      assert.equal(binary, guard.TOOLS_ROOT + "/node/bin/node");
      assert.deepEqual(args, [local.cli, "migrate", operation, "--config", local.config]);
      assert.equal(options.env.DATABASE_URL, undefined);
      assert.equal(options.env.NODE_OPTIONS, undefined);
      assert.equal(options.shell, false);
      assert(!JSON.stringify({args, options}).includes("canary"));
      return {status: 0, stdout: operation === "deploy" ? "No pending migrations to apply.\n" : "", stderr: "raw-canary"};
    },
    emit(value) { events.push("emit"); receipt = value; },
  });
  assert.equal(code, 0);
  assert.deepEqual(events, ["stdin", "model-private-store", "verified-inputs", "model-prisma", "emit"]);
  assert.equal(receipt.schema, "workinants.cloud-f0-runtime-lease-history-migrate-result.v2");
  assert.equal(receipt.packet_sha256, authorization.packet_sha256);
  assert.equal(receipt.literal_review_sha256, authorization.literal_review_sha256);
  assert.equal(receipt.attestation_sha256, guard.sha256(input));
  assert.equal(receipt.daemon_id, attestation.observed.daemon.daemon_id);
  assert.equal(receipt.no_pending_message_observed, operation === "deploy");
  assert.equal(receipt.database_qualification_claimed, false);
  assert(!JSON.stringify(receipt).includes("canary"));
});

for (const [command, operation] of [
  [flag, "reset"], [flag, "resolve"], [flag, "db push"],
  ["--execute-reviewed-cloud-f0-runtime-lease-history-v1", "deploy"],
]) check(() => {
  let used = false;
  assert.equal(runner.main([command, "--operation", operation], {readStdin() { used = true; }, emit() {}}), 1);
  assert.equal(used, false);
});
check(() => {
  let used = false;
  let receipt;
  assert.equal(runner.main([flag, "--operation", "status"], {
    readStdin: () => raw, store() { used = true; }, emit(value) { receipt = value; },
  }), 1);
  assert.equal(used, false);
  assert.equal(receipt.code, "ATTESTED_OPERATION");
});
check(() => {
  const receipt = runner.summarizeProcess({error: Error("secret-canary"), status: null}, "deploy");
  assert.equal(receipt.status, "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE");
  assert(!JSON.stringify(receipt).includes("canary"));
});

const baseRefusal = {
  schema: "workinants.cloud-f0-runtime-lease-history-refusal.v2",
  status: "REFUSED_OR_INCOMPLETE",
  raw_output_discarded: true,
  database_qualification_claimed: false,
};
const boundRefusal = {
  attestation_sha256: guard.sha256(raw),
  run_id: attestation.planned.run_id,
  container_id: attestation.observed.container_id,
  daemon_id: attestation.observed.daemon.daemon_id,
  packet_sha256: authorization.packet_sha256,
  literal_review_sha256: authorization.literal_review_sha256,
};
const ioError = () => { throw Object.assign(new Error("secret-canary"), {code: "EIO"}); };
const guardError = code => () => { throw new guard.HeldFailure(code); };
function checkRefusal(args, options, expected) {
  let receipt;
  const defaults = {
    readStdin: () => raw,
    store() {},
    load: () => local,
    spawn() { assert.fail("Unexpected child spawn"); },
    emit(value) { assert.equal(receipt, undefined); receipt = value; },
  };
  assert.equal(runner.main(args, {...defaults, ...options}), 1);
  assert.deepEqual(receipt, {...baseRefusal, ...expected});
  assert(!JSON.stringify(receipt).includes("canary"));
}
const exactArgs = [flag, "--operation", "deploy"];
check(() => checkRefusal([flag, "--operation", "canary"], {}, {
  phase: "ARGUMENTS", cause_family: "HELD_GUARD", code: "EXPLICIT_EXECUTION_REQUIRED",
  child_dispatch: "NOT_ATTEMPTED", operation: null,
}));
check(() => checkRefusal(exactArgs, {readStdin: ioError}, {
  phase: "INPUT", cause_family: "IO", code: "LOCAL_IO_ERROR",
  child_dispatch: "NOT_ATTEMPTED", operation: "deploy",
}));
check(() => {
  const malformed = Buffer.from('{"canary":1,"canary":2}');
  checkRefusal(exactArgs, {readStdin: () => malformed}, {
    phase: "ATTESTATION", cause_family: "HELD_GUARD", code: "DUPLICATE_JSON",
    child_dispatch: "NOT_ATTEMPTED", operation: "deploy", attestation_sha256: guard.sha256(malformed),
  });
});
for (const [phase, dependency, failure, family, code, child] of [
  ["PRIVATE_STORE", "store", ioError, "IO", "LOCAL_IO_ERROR", "NOT_ATTEMPTED"],
  ["LOCAL_GUARD", "load", guardError("TREE_OWNER_MODE"), "HELD_GUARD", "TREE_OWNER_MODE", "NOT_ATTEMPTED"],
  ["LOCAL_GUARD", "load", guardError("secret-canary"), "HELD_GUARD", "UNLISTED_GUARD_CODE", "NOT_ATTEMPTED"],
  ["DISPATCH", "spawn", ioError, "IO", "LOCAL_IO_ERROR", "UNCONFIRMED"],
  ["RESULT", "spawn", () => null, "TYPE", "LOCAL_INPUT_TYPE_ERROR", "UNCONFIRMED"],
]) check(() => checkRefusal(exactArgs, {[dependency]: failure}, {
  phase, cause_family: family, code, child_dispatch: child, operation: "deploy", ...boundRefusal,
}));

console.log(JSON.stringify({
  status: "PASS_OFFLINE", checks, real_tool_member_hashes: hashes, node: process.version,
  kernel_and_processes_modeled: true, prisma_spawned: false, database_contacted: false,
  qualification: "NOT_RUN",
}));
