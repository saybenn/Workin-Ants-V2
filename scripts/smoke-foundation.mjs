import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { mkdir, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import path from "node:path";
import { setTimeout as delay } from "node:timers/promises";

const root = process.cwd();
const results = [];
const canary = `foundation-test-only-${randomUUID()}`;
const active = new Set();

async function freePort() {
  const socket = createServer();
  await new Promise((resolve, reject) => {
    socket.once("error", reject);
    socket.listen(0, "127.0.0.1", resolve);
  });
  const address = socket.address();
  assert(address && typeof address === "object");
  await new Promise((resolve) => socket.close(resolve));
  return address.port;
}

async function stop(server) {
  if (server.child.exitCode === null && server.child.signalCode === null) {
    server.child.kill("SIGTERM");
    const finished = await Promise.race([
      server.closed.then(() => true),
      delay(5000).then(() => false),
    ]);
    if (!finished) {
      server.child.kill("SIGKILL");
      await server.closed;
    }
  }
  active.delete(server);
}

async function start(mode) {
  const port = await freePort();
  const args = mode === "development" ? ["dev"] : ["start"];
  const child = spawn(
    process.execPath,
    [path.join(root, "node_modules/next/dist/bin/next"), ...args, "--hostname", "127.0.0.1", "--port", String(port)],
    {
      cwd: root,
      env: {
        ...process.env,
        NODE_ENV: mode,
        NEXT_TELEMETRY_DISABLED: "1",
        // Deliberately misleading public flag: it must not grant diagnostics.
        NEXT_PUBLIC_APP_ENV: mode === "production" ? "development" : "production",
        SUPABASE_SERVICE_ROLE_KEY: canary,
        STRIPE_SECRET_KEY: canary,
        DATABASE_URL: "postgresql://unused:unused@127.0.0.1:1/no_database_used",
      },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  const server = { child, url: `http://127.0.0.1:${port}`, logs: "", closed: new Promise((resolve) => child.once("close", resolve)) };
  active.add(server);
  child.stdout.on("data", (chunk) => { server.logs += chunk.toString(); });
  child.stderr.on("data", (chunk) => { server.logs += chunk.toString(); });
  for (let tries = 0; tries < 120; tries++) {
    if (child.exitCode !== null || child.signalCode !== null) {
      throw new Error(`Next ${mode} exited before readiness: ${server.logs.replaceAll(canary, "[test-canary]")}`);
    }
    try {
      const response = await fetch(`${server.url}/api/health`, { signal: AbortSignal.timeout(2000) });
      if (response.status === 200) return server;
    } catch { /* Local listener/first compile may still be starting. */ }
    await delay(250);
  }
  throw new Error(`Next ${mode} readiness timed out`);
}

async function check(server, mode, label, pathname, expected, options = {}, verify) {
  const response = await fetch(server.url + pathname, { ...options, signal: AbortSignal.timeout(30000) });
  const body = await response.text();
  assert.equal(response.status, expected, `${mode}: ${label}`);
  assert(!body.includes(canary), `${mode}: secret canary exposed`);
  if (mode === "production") {
    assert(!body.includes("Development diagnostics"), `${label}: development page leaked`);
  }
  if (verify) verify(body, response);
  results.push({ mode, case: label, method: options.method ?? "GET", path: pathname, status: response.status, result: "PASS" });
}

try {
  for (const mode of ["development", "production"]) {
    const server = await start(mode);
    try {
      await check(server, mode, "root shell", "/", 200, {}, (body) => assert(body.includes("Workin Ants")));
      await check(server, mode, "process liveness only", "/api/health", 200, {}, (body, response) => {
        assert.deepEqual(JSON.parse(body), { status: "ok", service: "workin-ants", check: "process" });
        assert.equal(response.headers.get("cache-control"), "no-store");
      });
      await check(server, mode, "health HEAD", "/api/health", 200, { method: "HEAD" }, (body) => assert.equal(body, ""));
      await check(server, mode, "health has no mutation", "/api/health", 405, { method: "POST" });
      await check(server, mode, "unknown route", "/unregistered-foundation-route", 404);
      await check(server, mode, "old page filename is not a route", "/page", 404);
      await check(server, mode, "old diagnostic filename is not a route", "/dev/status/page", 404);
      await check(server, mode, "old handler filename is not a route", "/api/debug/env-check/route", 404);
      await check(server, mode, "development page execution-mode gate", "/dev/status", mode === "development" ? 200 : 404, {}, (body) => {
        if (mode === "development") assert(body.includes("Development diagnostics"));
      });
      await check(server, mode, "development page HEAD gate", "/dev/status", mode === "development" ? 200 : 404, { method: "HEAD" });
      await check(server, mode, "query/header cannot change execution mode", "/dev/status?NODE_ENV=development", mode === "development" ? 200 : 404, { headers: { "x-node-env": "development", "x-forwarded-env": "development" } });
      for (const method of ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]) {
        const expected = mode === "production" ? 404 : ["GET", "HEAD"].includes(method) ? 200 : 405;
        await check(server, mode, "debug endpoint method/mode gate", "/api/debug/env-check", expected, { method }, (body, response) => {
          assert.equal(response.headers.get("cache-control"), "no-store");
          if (method === "GET" && mode === "development") assert.deepEqual(JSON.parse(body), { status: "ok", mode: "development", check: "process" });
        });
      }
      if (mode === "production") {
        await check(server, mode, "debug query/header cannot enable route", "/api/debug/env-check?NEXT_PUBLIC_APP_ENV=development", 404, { headers: { "x-node-env": "development" } });
        await check(server, mode, "trailing slash remains denied", "/api/debug/env-check/", 404);
        const rootResponse = await fetch(server.url);
        const html = await rootResponse.text();
        const scripts = [...html.matchAll(/<script[^>]*src="([^"]+)"/g)].map((match) => match[1]).filter((src) => src.startsWith("/_next/"));
        assert(scripts.length > 0);
        for (const src of new Set(scripts)) {
          const response = await fetch(server.url + src);
          assert.equal(response.status, 200);
          assert(!(await response.text()).includes(canary), "test secret in client bundle");
        }
        results.push({ mode, case: "root client scripts do not contain secret canary", assets_checked: new Set(scripts).size, result: "PASS" });
      }
    } finally {
      await stop(server);
    }
  }
  const restarted = await start("production");
  try {
    await check(restarted, "production", "restart same build health recovery", "/api/health", 200);
    await check(restarted, "production", "restart preserves diagnostic denial", "/api/debug/env-check", 404);
  } finally { await stop(restarted); }
  const report = { status: "PASS", total: results.length, tests: results, limits: "Real local Next development/production HTTP and client-asset smoke only. No DB/provider/owner contract/runtime, full browser accessibility or deployed hosting qualification." };
  const outputIndex = process.argv.indexOf("--output");
  if (outputIndex !== -1) {
    const output = process.argv[outputIndex + 1];
    assert(output);
    await mkdir(path.dirname(output), { recursive: true });
    await writeFile(output, JSON.stringify(report, null, 2) + "\n");
  }
  console.log(JSON.stringify(report, null, 2));
} finally {
  for (const server of active) await stop(server);
}
