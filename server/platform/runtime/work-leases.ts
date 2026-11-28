import { runOwnerTransaction, type DatabaseActionContext, type OwnerDatabase, type OwnerQuery } from "../persistence/owner-transaction";

const handler = "assignDefaultFreeTrack.v1";
const uuid = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/;
const insertFields = ["attemptCount", "effectReceiptId", "fence", "handlerName", "id", "leaseExpiresAt", "leaseTokenHash",
  "nextAttemptAt", "outboxMessageId", "semanticWorkKey", "state"];
const selectFields = [...insertFields, "createdAt", "mutationTransactionId"].sort();

export type KnownDefaultFreeIntent = Readonly<{
  workId: string;
  outboxMessageId: string;
  customerProfileId: string;
  userId: string;
}>;

export type KnownWorkScheduleOutcome =
  | { status: "scheduled" | "already_scheduled"; workId: string }
  | { status: "denied" | "conflict" | "unavailable" };

function hasScheduleFields(context: DatabaseActionContext, workId: string): boolean {
  const prefix = `RuntimeWorkItem/${workId}`;
  const expected = [
    ...insertFields.map((field) => `${prefix}/INSERT/${field}`),
    ...selectFields.map((field) => `${prefix}/SELECT/${field}`),
    `${prefix}/revision/0`,
  ];
  return context.sourceGeneration === BigInt(0) && context.allowedFields.length === expected.length
    && expected.every((field, index) => context.allowedFields[index] === field);
}

async function existingWork(
  query: OwnerQuery,
  intent: KnownDefaultFreeIntent,
  key: string,
): Promise<KnownWorkScheduleOutcome | undefined> {
  const rows = await query`
    SELECT id::text, outbox_message_id::text, handler_name, semantic_work_key
    FROM platform.runtime_work_item
    WHERE id = ${intent.workId}::uuid
  `;
  const row = rows[0];
  if (rows.length === 0) return undefined;
  if (rows.length !== 1 || row?.id !== intent.workId) return { status: "unavailable" };
  if (row.outbox_message_id !== intent.outboxMessageId || row.handler_name !== handler || row.semantic_work_key !== key) {
    return { status: "conflict" };
  }
  return { status: "already_scheduled", workId: intent.workId };
}

/** The trusted owner supplies the committed intent and stable work identity after the source transaction closes. */
export async function scheduleKnownDefaultFreeWork(
  database: OwnerDatabase,
  context: DatabaseActionContext,
  known: KnownDefaultFreeIntent,
): Promise<KnownWorkScheduleOutcome> {
  const intent = { ...known };
  const identities = [intent.workId, intent.outboxMessageId, intent.customerProfileId, intent.userId];
  if (database.runtimeLogin !== "wa_app_runtime" || !("userId" in context.principal)
      || context.principal.userId !== intent.userId || context.owner !== "platform_integration_owner"
      || context.action !== "runtime.schedule_work.v1" || context.purpose !== "work.schedule"
      || context.targetKind !== "RuntimeWorkItem" || context.targetId !== intent.workId
      || !identities.every((id) => typeof id === "string" && uuid.test(id))
      || !hasScheduleFields(context, intent.workId)) {
    return { status: "denied" };
  }

  const key = `customer_buyer_profile/${intent.customerProfileId}/default-free-enrollment/v1`;
  return runOwnerTransaction(database, context, async (query) => {
    const current = await existingWork(query, intent, key);
    if (current) return current;
    const rows = await query`
      INSERT INTO platform.runtime_work_item (id, outbox_message_id, handler_name, semantic_work_key, state, fence, attempt_count)
      VALUES (${intent.workId}::uuid, ${intent.outboxMessageId}::uuid, ${handler}, ${key}, 'pending', 0, 0)
      ON CONFLICT DO NOTHING
      RETURNING id::text
    `;
    if (rows.length === 0) return (await existingWork(query, intent, key)) ?? { status: "unavailable" };
    if (rows.length !== 1 || rows[0]?.id !== intent.workId) throw new Error("work_schedule_unconfirmed");
    return { status: "scheduled", workId: intent.workId };
  });
}
