import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import { inferType, mergeUserTypes } from "../../../../node_modules/postgres/src/types.js";

const root = new URL("../../../../", import.meta.url);

test("Postgres.js sends serialized JSON objects through text parameters", async () => {
  const body = { value: { name: 'Fixed "synthetic" profile', revision: "0" } };
  const serialized = JSON.stringify(body);
  const { serializers } = mergeUserTypes({});
  assert.equal(inferType(serialized), 0);
  assert.equal(JSON.parse(serializers[3802](serialized)), serialized);
  assert.deepEqual(JSON.parse(serializers[25](serialized)), body);

  const writers = [
    ["server/platform/runtime/command-receipts.ts", "body"],
    ["server/platform/runtime/outbox.ts", "message.payload"],
    ["features/customer_buyer_profile/infrastructure/customer-repository.ts", "body"],
  ];
  for (const [path, value] of writers) {
    const source = await readFile(new URL(path, root), "utf8");
    assert.ok(source.includes(`SELECT \${JSON.stringify(${value})}::text::jsonb AS body`), path);
  }
});
