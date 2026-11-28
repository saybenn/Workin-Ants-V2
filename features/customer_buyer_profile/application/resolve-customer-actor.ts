import { createHash } from "node:crypto";
import { runOwnerTransaction, type DatabaseActionContext, type OwnerDatabase } from
  "../../../server/platform/persistence/owner-transaction";
import { insertCommandResult, readCommandReceipt, type CommandIdentity, type CommandReceiptRead } from
  "../../../server/platform/runtime/command-receipts";
import { insertDefaultCustomer, type CustomerProvisionRows } from "../infrastructure/customer-repository";

const owner = "customer_buyer_profile";
const operation = "SH-004.v1";
const sourceToken = "0";
const resultSchema = { id: `${operation}#/$defs/response`, version: "1" };
const key = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const uuid = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/;

function isKey(value: unknown): value is string {
  return typeof value === "string" && key.test(value);
}

type CustomerProvisionRequest = Readonly<{
  userId: string;
  purpose: "provision";
  semanticKey: string;
  requestId: string;
  correlationId: string;
}>;

type CustomerProvisionValue = {
  customerProfileId: string;
  userId: string;
  lifecycle: "active";
  sourceToken: string;
  receipt: {
    owner: typeof owner;
    id: string;
    semanticKey: string;
    fingerprint: string;
    sourceToken: string;
    recordedAt: string;
  };
};

export type CustomerProvisionOutcome =
  | { status: "created" | "replay"; value: CustomerProvisionValue }
  | { status: "denied" | "conflict" | "unavailable" };

function record(value: unknown, fields: readonly string[]): Record<string, unknown> | undefined {
  if (typeof value !== "object" || value === null || Array.isArray(value)
      || Object.keys(value).length !== fields.length || !fields.every((field) => Object.hasOwn(value, field))) {
    return undefined;
  }
  return value as Record<string, unknown>;
}

function provisionValue(rows: CustomerProvisionRows, command: CommandIdentity, recordedAt: string): CustomerProvisionValue {
  return {
    customerProfileId: rows.customerProfileId, userId: rows.userId, lifecycle: "active", sourceToken,
    receipt: {
      owner, id: rows.receiptId, semanticKey: command.semanticKey, fingerprint: command.fingerprint, sourceToken, recordedAt,
    },
  };
}

function replay(stored: CommandReceiptRead, command: CommandIdentity, target: CustomerProvisionRows): CustomerProvisionOutcome {
  if (stored.status === "conflict") return { status: "conflict" };
  if (stored.status !== "committed") return { status: "unavailable" };
  const envelope = record(stored.body, ["contract", "requestId", "status", "value"]);
  const saved = record(envelope?.value, ["customerProfileId", "userId", "lifecycle", "sourceToken", "receipt"]);
  const receipt = record(saved?.receipt, ["owner", "id", "semanticKey", "fingerprint", "sourceToken", "recordedAt"]);
  const at = receipt?.recordedAt;
  if (envelope?.contract !== operation || envelope.status !== "ok" || !isKey(envelope.requestId)
      || saved?.customerProfileId !== target.customerProfileId || saved.userId !== target.userId
      || saved.lifecycle !== "active" || saved.sourceToken !== sourceToken || receipt?.owner !== owner
      || receipt.id !== target.receiptId || receipt.semanticKey !== command.semanticKey || receipt.fingerprint !== command.fingerprint
      || receipt.sourceToken !== sourceToken || typeof at !== "string" || !Number.isFinite(Date.parse(at))) {
    return { status: "unavailable" };
  }
  return { status: "replay", value: provisionValue(target, command, at) };
}

/** Provision a known target under trusted authority. A replay returns the original command value. */
export async function provisionKnownCustomerProfile(
  database: OwnerDatabase,
  context: DatabaseActionContext,
  request: CustomerProvisionRequest,
  target: CustomerProvisionRows,
): Promise<CustomerProvisionOutcome> {
  const input = { ...request };
  const rows = { ...target };
  const ids = [rows.userId, rows.customerProfileId, rows.receiptId, rows.lifecycleEventId, rows.evidenceId,
    rows.lifecycleOutboxId, rows.defaultFreeIntentId];
  if (database.runtimeLogin !== "wa_app_runtime" || !("userId" in context.principal)
      || context.principal.userId !== rows.userId || input.userId !== rows.userId || context.action !== operation
      || context.owner !== owner || context.purpose !== "provision" || input.purpose !== "provision"
      || context.targetKind !== "CustomerProfile" || context.targetId !== rows.customerProfileId
      || context.sourceGeneration !== BigInt(0) || !ids.every((id) => typeof id === "string" && uuid.test(id))
      || ![input.semanticKey, input.requestId, input.correlationId, rows.decisionRef].every(isKey)) {
    return { status: "denied" };
  }

  const subjectScope = `CustomerProfile:${rows.customerProfileId}`;
  const fingerprint = createHash("sha256")
    .update(JSON.stringify([owner, operation, subjectScope, input.userId, input.purpose])).digest("hex");
  const command: CommandIdentity = { receiptId: rows.receiptId, owner, operation, subjectScope, semanticKey: input.semanticKey, fingerprint };
  return runOwnerTransaction(database, context, async (query) => {
    const existing = await readCommandReceipt(query, command, resultSchema, sourceToken);
    if (existing.status !== "unobserved") return replay(existing, command, rows);
    const stamp = (await query`SELECT pg_catalog.transaction_timestamp() AS occurred`)[0]?.occurred;
    if (!(stamp instanceof Date) || !Number.isFinite(stamp.getTime())) throw new Error("customer_transaction_clock_unavailable");
    const value = provisionValue(rows, command, stamp.toISOString());
    const inserted = await insertCommandResult(query, command, resultSchema, sourceToken, {
      contract: operation, requestId: input.requestId, status: "ok", value,
    });
    if (!inserted) return replay(await readCommandReceipt(query, command, resultSchema, sourceToken), command, rows);
    await insertDefaultCustomer(query, rows, input.correlationId);
    return { status: "created", value };
  });
}
