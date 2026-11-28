import type { OwnerQuery } from "../../../server/platform/persistence/owner-transaction";
import { appendOutboxMessage } from "../../../server/platform/runtime/outbox";

export type CustomerProvisionRows = Readonly<{
  userId: string;
  customerProfileId: string;
  receiptId: string;
  lifecycleEventId: string;
  evidenceId: string;
  lifecycleOutboxId: string;
  defaultFreeIntentId: string;
  decisionRef: string;
}>;

const owner = "customer_buyer_profile";
const revision = "0";
const lifecycleEvent = "customer.lifecycle_changed.v1";
const defaultFreeCommand = "assignDefaultFreeTrack.v1";

export async function insertDefaultCustomer(query: OwnerQuery, rows: CustomerProvisionRows, correlationId: string) {
  await query`
    INSERT INTO app.customer_profiles (id, user_id, status, revision, privacy_generation)
    VALUES (${rows.customerProfileId}::uuid, ${rows.userId}::uuid, 'active', 0, 0)
  `;
  await query`
    INSERT INTO app.customer_profile_lifecycle_event (
      id, customer_profile_id, command_receipt_id, source_revision, from_status, to_status, name, actor_user_id
    ) VALUES (
      ${rows.lifecycleEventId}::uuid, ${rows.customerProfileId}::uuid, ${rows.receiptId}::uuid, 0,
      NULL, 'active', ${lifecycleEvent}, ${rows.userId}::uuid
    )
  `;
  const body = {
    schema: "database-owner-evidence.v1", owner, model: "CustomerProfile", primaryKey: { id: rows.customerProfileId },
    prior: null,
    committed: {
      id: rows.customerProfileId, userId: rows.userId, status: "active", revision, privacyGeneration: "0",
    },
    decisionRef: rows.decisionRef,
  };
  await query`
    WITH evidence AS (SELECT ${JSON.stringify(body)}::jsonb AS body)
    INSERT INTO platform.owner_mutation_evidence (
      id, command_receipt_id, owner_module_id, aggregate_kind, aggregate_id, previous_revision, committed_revision,
      action, decision_ref, evidence_schema_id, evidence_schema_version, evidence_digest, evidence_body
    ) SELECT ${rows.evidenceId}::uuid, ${rows.receiptId}::uuid, ${owner}, 'CustomerProfile', ${rows.customerProfileId},
             NULL, 0, 'SH-004.v1', ${rows.decisionRef}, 'urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile', '1',
             pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(evidence.body::text, 'UTF8')), 'hex'), evidence.body
      FROM evidence
  `;
  const source = {
    commandReceiptId: rows.receiptId, producerOwner: owner, aggregateKind: "CustomerProfile",
    aggregateId: rows.customerProfileId, sourceRevision: revision, sourceGeneration: "0", schemaVersion: "1", correlationId,
  };
  await appendOutboxMessage(query, {
    ...source,
    id: rows.lifecycleOutboxId, kind: "event", ordinal: 0, name: lifecycleEvent,
    payloadSchemaId: "urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1",
    payload: {
      eventName: lifecycleEvent, customerProfileId: rows.customerProfileId, userId: rows.userId,
      lifecycleRevision: revision, safeState: "active",
    },
  });
  await appendOutboxMessage(query, {
    ...source,
    id: rows.defaultFreeIntentId, kind: "command", ordinal: 1, name: defaultFreeCommand,
    payloadSchemaId: "urn:workinants:database-review:foundation-payloads:v1#/$defs/assignDefaultFreeTrackCustomerCommand",
    payload: {
      sourceOwner: owner, userId: rows.userId, track: "customer", customerProfileId: rows.customerProfileId,
      sourceCreationRevision: revision, sourceCreationReceipt: rows.receiptId,
      semanticKey: `${owner}/${rows.customerProfileId}/default-free-enrollment/v1`,
    },
  });
}
