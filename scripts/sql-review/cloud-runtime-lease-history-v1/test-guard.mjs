// Offline test. Actual extracted source and tool files with simulated
// container metadata, mount table, private URL and process boundaries.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {pathToFileURL} from "node:url";

const [source, tools, attestationPath] = process.argv.slice(2);
const base = path.join(source, "scripts/sql-review/cloud-runtime-lease-history-v1");
const guard = await import(pathToFileURL(path.join(base, "guard.mjs")));
const runner = await import(pathToFileURL(path.join(base, "runner.mjs")));
const raw = fs.readFileSync(attestationPath);
const attestation = JSON.parse(raw);
const identity = {platform: "linux", arch: "x64", node: process.version, hostname: "b".repeat(12), uid: 0};
const mountInfo = '11 10 0:5 / /run/wa-secrets rw,nodev,nosuid,noexec - tmpfs tmpfs rw,mode=700\n'
  + '12 10 0:6 /example /run/bootstrap-password ro,relatime - ext4 /dev/loop1 rw\n';
const url = "postgresql://wa_migrator:private-canary@127.0.0.1:5432/wa_p0c_rehearsal?schema=public&sslmode=disable";
const execFlag = "--execute-reviewed-cloud-f0-runtime-lease-history-v1";

function realPath(filename) {
  for (const [container, local] of [[guard.SOURCE_ROOT, source], [guard.TOOLS_ROOT, tools]]) {
    if (filename === container || filename.startsWith(container + "/")) {
      const target = path.join(local, filename.slice(container.length));
      assert.equal(fs.realpathSync(target), target);
      return target;
    }
  }
  throw Error("unexpected virtual path");
}

function filesUnder(absolute, prefix = "") {
  const result = [];
  for (const info of fs.readdirSync(absolute, {withFileTypes: true})) {
    const relative = prefix + info.name;
    if (info.isDirectory()) result.push(...filesUnder(path.join(absolute, info.name), relative + "/"));
    else {
      assert(info.isFile());
      result.push(relative);
    }
  }
  return result;
}

let checks = 0;
let realToolHashes = 0;
const pass = (check) => { check(); checks++; };
const io = {
  mountInfo: () => mountInfo,
  loopbackOnly: () => true,
  read: filename => fs.readFileSync(realPath(filename)),
  readPrivate(filename) { assert.equal(filename, guard.URL_FILE); return Buffer.from(url); },
  listFiles: directory => filesUnder(realPath(directory)),
  toolHash(filename, relative, size) {
    realToolHashes++;
    return guard.hashStableTool(realPath(filename), relative, size, process.getuid());
  },
};
let local;
pass(() => {
  local = guard.verifyInputs(guard.strictJson(raw), io, identity);
  assert.equal(local.databaseUrl, url);
  assert.equal(realToolHashes, 10300);
  assert.equal(local.engine, guard.TOOLS_ROOT + "/schema-engine");
  assert.equal(local.migrations, guard.SOURCE_ROOT + "/" + guard.HISTORY);
});

for (const [kind, modify] of [
  ["wrong endpoint", a => { a.observed.endpoint = "tcp://localhost:2375"; }],
  ["legacy endpoint", a => { a.observed.endpoint = "npipe:////./pipe/dockerDesktopLinuxEngine"; }],
  ["forged daemon", a => { a.observed.daemon.daemon_id = "another-daemon"; }],
  ["changed socket", a => { a.observed.daemon.socket.inode++; }],
  ["changed image", a => { a.observed.image_id = "sha256:" + "c".repeat(64); }],
  ["wrong volume", a => { a.observed.volume_name += "-other"; }],
  ["published ports", a => { a.observed.published_ports = true; }],
  ["wrong network", a => { a.planned.target.network = "host"; }],
  ["mutable secret bind", a => { a.observed.bootstrap_readonly = false; }],
  ["other run's secret", a => { a.planned.target.bootstrap_secret_host_path = "/workspace/scratch/other-secret"; }],
  ["alias path", a => { a.planned.target.bootstrap_secret_host_path = "/workspace/scratch/../ok-bootstrap-password"; }],
  ["old manifest schema", a => { a.planned.schema = "workinants.local-f0-runtime-lease-history-run.v1"; }],
  ["wrong review pin", a => { a.planned.source.effective_expected_sha256 = "a".repeat(64); }],
  ["wrong manifest digest", a => { a.run_manifest_sha256 = "a".repeat(64); }],
  ["changed executable length", a => { a.planned.tools.file_sizes["node/bin/node"]++; }],
  ["changed executable hash", a => { a.planned.tools.files_sha256["schema-engine"] = "a".repeat(64); }],
  ["truncated closure", a => { delete a.planned.tools.files_sha256["schema-engine"]; }],
]) {
  pass(() => {
    const changed = structuredClone(attestation);
    modify(changed);
    assert.throws(() => guard.validateAttestation(changed), guard.HeldFailure, kind);
  });
}

for (const [label, failedIo, failedIdentity, wanted] of [
  ["not actual short hostname", io, {...identity, hostname: "other"}, /CONTAINER_HOSTNAME/],
  ["non-root user", io, {...identity, uid: 1000}, /CONTAINER_LOOPBACK_ONLY/],
  ["second interface", {...io, loopbackOnly: () => false}, identity, /CONTAINER_LOOPBACK_ONLY/],
  ["no tmpfs", {...io, mountInfo: () => mountInfo.replace(" - tmpfs ", " - ext4 ")}, identity, /PRIVATE_MOUNT_OPTIONS/],
  ["missing nosuid", {...io, mountInfo: () => mountInfo.replace(",nosuid", "")}, identity, /PRIVATE_MOUNT_OPTIONS/],
  ["mutable bootstrap", {...io, mountInfo: () => mountInfo.replace("ro,relatime", "rw,relatime")}, identity, /PRIVATE_MOUNT_OPTIONS/],
  ["extra source", {...io, listFiles: root => root === guard.SOURCE_ROOT ? [...io.listFiles(root), "unexpected.sql"] : io.listFiles(root)}, identity, /EXACT_SOURCE8_CLOSURE/],
  ["source bytes changed", {...io, read: file => file === guard.SOURCE_ROOT + "/" + guard.SCHEMA ? Buffer.from("changed") : io.read(file)}, identity, /SOURCE_FILE_DRIFT/],
  ["bad streamed tool hash", {...io, toolHash: () => "c".repeat(64)}, identity, /TOOL_FILE_DRIFT/],
  ["obsolete Effect", {...io, toolHash: (_, relative) => attestation.planned.tools.files_sha256[relative],
    read: file => file === guard.TOOLS_ROOT + "/node_modules/effect/package.json"
      ? Buffer.from('{"version":"3.20.0"}') : io.read(file)}, identity, /VETTED_EFFECT_VERSION/],
]) pass(() => assert.throws(() => guard.verifyInputs(attestation, failedIo, failedIdentity), wanted, label));

for (const candidate of [
  url.replace("127.0.0.1", "127.1"), url.replace("127.0.0.1", "coincidental.example.com"),
  url.replace("wa_migrator", "postgres"), url + "&schema=public", url + "&extra=value",
]) pass(() => assert.throws(() => guard.validateUrl(candidate), guard.HeldFailure));
for (const invalid of ['{"x":1,"x":2}', '{"x":NaN}', '{"x":1e400}', '{"x":true}null']) {
  pass(() => assert.throws(() => guard.strictJson(Buffer.from(invalid)), guard.HeldFailure));
}

for (const name of ["node/bin/node", "schema-engine"]) {
  const filename = path.join(tools, name);
  const length = attestation.planned.tools.file_sizes[name];
  assert(length > 16 * 1024 * 1024);
  pass(() => assert.throws(() => guard.hashStableTool(filename, name, length - 1, process.getuid()), /FILE_OWNER_MODE_SIZE/));
  pass(() => assert.throws(() => guard.hashStableTool(filename, "unrelated", length, process.getuid()), /TOOL_SIZE_BOUND/));
}
pass(() => {
  // Fail before hashing if the underlying real inode gains another name.
  const pathActual = path.join(tools, "schema-engine");
  const hardLink = path.join(tools, "test-only-hardlink");
  fs.linkSync(pathActual, hardLink);
  try {
    assert.throws(() => guard.hashStableTool(pathActual, "schema-engine", 23516472, process.getuid()), /FILE_OWNER_MODE_SIZE/);
  } finally {
    fs.unlinkSync(hardLink);
  }
});
pass(() => {
  const original = path.join(tools, "schema-engine");
  const alias = path.join(tools, "test-only-alias");
  fs.symlinkSync(original, alias);
  try {
    assert.throws(() => guard.hashStableTool(alias, "schema-engine", 23516472, process.getuid()), /NONCANONICAL_FILE/);
  } finally {
    fs.unlinkSync(alias);
  }
});

for (const operation of ["deploy", "status"]) {
  pass(() => {
    const forOperation = Buffer.from(JSON.stringify({...attestation, operation}));
    const events = [];
    let value;
    const result = runner.main([execFlag, "--operation", operation], {
      readStdin() { events.push("read"); return forOperation; },
      store() { events.push("store"); },
      load() { events.push("verified-inputs-fixture"); return local; },
      spawn(binary, args, options) {
        events.push("modeled-process");
        assert.equal(binary, guard.TOOLS_ROOT + "/node/bin/node");
        assert.deepEqual(args, [local.cli, "migrate", operation, "--config", local.config]);
        assert.equal(options.shell, false);
        assert.equal(options.cwd, guard.SOURCE_ROOT);
        for (const blocked of ["DATABASE_URL", "NODE_OPTIONS", "PGPASSWORD", "HTTP_PROXY", "DOCKER_HOST"]) {
          assert.equal(options.env[blocked], undefined);
        }
        assert(!JSON.stringify({args, options}).includes("private-canary"));
        return {status: 0, stdout: operation === "deploy" ? "No pending migrations to apply.\n" : "", stderr: "raw-canary"};
      },
      emit(summary) { events.push("emit"); value = summary; },
    });
    assert.equal(result, 0);
    assert.deepEqual(events, ["read", "store", "verified-inputs-fixture", "modeled-process", "emit"]);
    assert.equal(value.daemon_id, "synthetic-test-daemon");
    assert.equal(value.attestation_sha256, guard.sha256(forOperation));
    assert.equal(value.no_pending_message_observed, operation === "deploy");
    assert.equal(value.database_qualification_claimed, false);
    assert(!JSON.stringify(value).includes("canary"));
  });
}
for (const [flag, operation] of [
  [execFlag, "resolve"], [execFlag, "reset"], [execFlag, "db push"],
  ["--execute-reviewed-local-f0-runtime-lease-history-v1", "deploy"],
]) pass(() => {
  let advanced = false;
  assert.equal(runner.main([flag, "--operation", operation], {readStdin() { advanced = true; }, emit() {}}), 1);
  assert.equal(advanced, false);
});
pass(() => {
  let advanced = false;
  let receipt;
  assert.equal(runner.main([execFlag, "--operation", "status"], {
    readStdin: () => raw, store() { advanced = true; }, emit(value) { receipt = value; },
  }), 1);
  assert.equal(advanced, false);
  assert.equal(receipt.code, "ATTESTED_OPERATION");
});
pass(() => {
  const summary = runner.summarizeProcess({error: Error("secret-canary"), status: null, stderr: "raw-canary"}, "deploy");
  assert.equal(summary.status, "CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE");
  assert.equal(summary.exit_code, null);
  assert(!JSON.stringify(summary).includes("canary"));
});

console.log(JSON.stringify({status: "PASS_OFFLINE", focused_checks: checks, real_tool_member_hashes: realToolHashes,
  node: process.version, container_identity_modeled: true, client_process_modeled: true,
  prisma_spawned: false, database_contacted: false, qualification: "NOT_RUN"}));
