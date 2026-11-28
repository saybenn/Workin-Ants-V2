import type { OwnerQuery } from "../persistence/owner-transaction";

export type OutboxMessage = Readonly<{
  id: string;
  commandReceiptId: string;
  kind: "event" | "command";
  producerOwner: string;
  aggregateKind: string;
  aggregateId: string;
  sourceRevision: string;
  sourceGeneration: string;
  ordinal: number;
  name: string;
  schemaVersion: string;
  payloadSchemaId: string;
  payload: object;
  correlationId: string;
}>;

export async function appendOutboxMessage(query: OwnerQuery, message: OutboxMessage): Promise<void> {
  await query`
    WITH payload AS (SELECT ${JSON.stringify(message.payload)}::jsonb AS body)
    INSERT INTO platform.runtime_outbox_message (
      id, command_receipt_id, kind, producer_owner, aggregate_kind, aggregate_id,
      source_revision, source_generation, ordinal, name, schema_version, payload_schema_id,
      payload_hash, payload, correlation_id, causation_id, occurred_at, effective_at
    ) SELECT ${message.id}::uuid, ${message.commandReceiptId}::uuid, ${message.kind}::platform.runtime_message_kind,
             ${message.producerOwner}, ${message.aggregateKind}, ${message.aggregateId}, ${message.sourceRevision}::bigint,
             ${message.sourceGeneration}::bigint, ${message.ordinal}::integer, ${message.name}, ${message.schemaVersion},
             ${message.payloadSchemaId}, pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(payload.body::text, 'UTF8')), 'hex'),
             payload.body, ${message.correlationId}, ${message.commandReceiptId}, pg_catalog.transaction_timestamp(),
             pg_catalog.transaction_timestamp()
      FROM payload
  `;
}
