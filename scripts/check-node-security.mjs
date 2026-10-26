// Pure runtime/TLS boundary checks; no sockets, credentials or database access.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { checkServerIdentity } from "node:tls";

const pin = (await readFile(new URL("../.node-version", import.meta.url), "utf8")).trim();
assert.equal(process.versions.node, pin, "Use the pinned security runtime");
const checks = [{ case: "actual runtime matches security pin", result: "PASS" }];
const dnsOnly = { subject: { CN: "127.0.0.1" }, subjectaltname: "DNS:127.0.0.1, DNS:87.0.0.1" };
for (const host of ["127.0.0.1", "0177.0.0.1", "0x7f.0.0.1", "2130706433", "127.1", "0127.0.0.1", "１２７.0.0.1"]) {
  assert.equal(checkServerIdentity(host, dnsOnly)?.code, "ERR_TLS_CERT_ALTNAME_INVALID");
  checks.push({ case: "DNS-only certificate cannot authorize IP spelling", host, result: "PASS" });
}
assert.equal(checkServerIdentity("127.0.0.1", { subjectaltname: "IP Address:127.0.0.1" }), undefined);
assert.equal(checkServerIdentity("example.test", { subjectaltname: "DNS:example.test" }), undefined);
checks.push({ case: "matching IP and DNS certificate controls accepted", result: "PASS" });
console.log(JSON.stringify({ status: "PASS", node: process.version, total: checks.length, checks,
  limits: "Synthetic certificate identity invariants only; these are not a full TLS handshake, proof of exploit reproduction on every older release, or exhaustive tests of the October Node advisories." }, null, 2));
