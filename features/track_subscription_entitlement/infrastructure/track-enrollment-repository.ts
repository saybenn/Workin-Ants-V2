import type { OwnerQuery } from "../../../server/platform/persistence/owner-transaction";
import { readCommandReceipt, type CommandIdentity } from "../../../server/platform/runtime/command-receipts";
import {
  customerOwner, enrollmentAction, enrollmentCommandSchema, enrollmentResultSchema, trackOwner,
  type KnownFirstFreeEnrollment,
} from "./track-enrollment-scope";

const resultSchema = { id: enrollmentResultSchema, version: "1" };

type LiveWork = { effectReceiptId: string | null; attemptCount: number; startedAt: string };

export type EnrolledResult = Readonly<{ outcome: "enrolled"; selectionRevision: "0"; receipt: string }>;

function requireOne(rows: readonly Record<string, unknown>[], id: string) {
  if (rows.length !== 1 || rows[0]?.id !== id) throw new Error("unconfirmed_track_write");
}

export async function readLiveWork(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  semanticKey: string,
): Promise<LiveWork | undefined> {
  const { lease, source } = input;
  const binding = await query`
    SELECT pg_catalog.set_config('wa.lease_secret', ${lease.token}, true) IS NOT NULL AS secret_bound,
           pg_catalog.set_config('wa.fence', ${lease.fence.toString()}, true) IS NOT NULL AS fence_bound
  `;
  if (binding.length !== 1 || binding[0]?.secret_bound !== true || binding[0]?.fence_bound !== true) {
    throw new Error("unconfirmed_track_lease_binding");
  }

  const rows = await query`
    SELECT id::text, effect_receipt_id::text, attempt_count, pg_catalog.clock_timestamp() AS started_at
    FROM platform.runtime_work_item
    WHERE id = ${lease.workId}::uuid AND outbox_message_id = ${source.outboxId}::uuid
      AND handler_name = ${enrollmentAction} AND semantic_work_key = ${semanticKey}
      AND fence = ${lease.fence.toString()}::bigint AND state = 'leased'
      AND lease_expires_at > pg_catalog.clock_timestamp()
      AND platform_private.lease_secret_matches(lease_token_hash::text)
  `;
  const row = rows[0];
  if (rows.length !== 1 || row?.id !== lease.workId || typeof row.attempt_count !== "number"
      || !Number.isSafeInteger(row.attempt_count) || row.attempt_count < 1
      || !(row.started_at instanceof Date) || !Number.isFinite(row.started_at.getTime())
      || !(row.effect_receipt_id === null || typeof row.effect_receipt_id === "string")) return undefined;
  return { effectReceiptId: row.effect_receipt_id, attemptCount: row.attempt_count, startedAt: row.started_at.toISOString() };
}

const sha256 = /^[0-9a-f]{64}$/;

export async function readExactIntent(
  query: OwnerQuery,
  { customer, source }: KnownFirstFreeEnrollment,
  semanticKey: string,
): Promise<string | undefined> {
  const rows = await query`
    SELECT id::text, payload, payload_hash::text,
           pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(payload::text, 'UTF8')), 'hex')
             = payload_hash AS hash_matches
    FROM platform.runtime_outbox_message
    WHERE id = ${source.outboxId}::uuid AND kind = 'command' AND producer_owner = ${customerOwner}
      AND name = ${enrollmentAction} AND schema_version = '1' AND payload_schema_id = ${enrollmentCommandSchema}
      AND aggregate_kind = 'CustomerProfile' AND aggregate_id = ${customer.customerProfileId}
      AND source_revision = 0 AND source_generation = ${source.privacyGeneration}::bigint
      AND command_receipt_id = ${source.creationReceiptId}::uuid AND ordinal = 1
  `;
  const row = rows[0];
  if (rows.length !== 1 || row?.id !== source.outboxId || row.hash_matches !== true
      || typeof row.payload_hash !== "string" || !sha256.test(row.payload_hash)
      || typeof row.payload !== "object" || row.payload === null || Array.isArray(row.payload)) return undefined;

  const wanted = {
    sourceOwner: customerOwner, userId: customer.userId, track: "customer", customerProfileId: customer.customerProfileId,
    sourceCreationRevision: "0", sourceCreationReceipt: source.creationReceiptId, semanticKey,
  };
  const payload = row.payload as Record<string, unknown>;
  if (Object.keys(payload).length !== Object.keys(wanted).length
      || !Object.entries(wanted).every(([key, value]) => Object.hasOwn(payload, key) && payload[key] === value)) return undefined;
  return row.payload_hash;
}

export async function readApprovedFreeCatalog(query: OwnerQuery, input: KnownFirstFreeEnrollment): Promise<boolean> {
  const { catalog } = input;
  const rows = await query`
    SELECT p.id::text AS plan_id, d.id::text AS definition_id, b.id::text AS membership_id
    FROM app.track_plans p
    JOIN app.track_plan_entitlements b ON b.plan_id = p.id
    JOIN app.track_entitlement_definitions d ON d.id = b.entitlement_id
    WHERE p.id = ${catalog.planId}::uuid AND p.key = ${catalog.planKey}
      AND p.track = 'customer' AND p.status = 'active' AND p.billing_model = 'free'
      AND p.version = ${catalog.planVersion} AND p.content_hash = ${catalog.planContentHash} AND p.revision = 0
      AND d.id = ${catalog.definitionId}::uuid AND d.key = ${catalog.definitionKey}
      AND d.is_active AND (d.track IS NULL OR d.track = 'customer') AND d.value_type = 'boolean' AND d.revision = 0
      AND b.id = ${catalog.membershipId}::uuid AND b.value_type = 'boolean'
      AND b.boolean_value = ${catalog.value}::boolean AND b.revision = 0
      AND b.int_value IS NULL AND b.decimal_value IS NULL AND b.string_value IS NULL
      AND b.usage_period::text IS NOT DISTINCT FROM ${catalog.usagePeriod}::text
  `;
  return rows.length === 1 && rows[0]?.plan_id === catalog.planId
    && rows[0].definition_id === catalog.definitionId && rows[0].membership_id === catalog.membershipId;
}

function enrollmentResult(input: KnownFirstFreeEnrollment): EnrolledResult {
  return { outcome: "enrolled", selectionRevision: "0", receipt: input.rows.enrollment };
}

export function enrollmentCommand(
  input: KnownFirstFreeEnrollment,
  semanticKey: string,
  fingerprint: string,
): CommandIdentity {
  return {
    owner: trackOwner, operation: enrollmentAction, receiptId: input.rows.command,
    subjectScope: `CustomerProfile:${input.customer.customerProfileId}`, semanticKey, fingerprint,
  };
}

async function exactEffectMatches(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  requireLink: boolean,
): Promise<boolean> {
  const rows = await query`
    SELECT platform_private.worker_effect_matches(
      ${input.lease.workId}::uuid, ${input.rows.effect}::uuid, ${requireLink}::boolean
    ) AS exact_match
  `;
  return rows.length === 1 && rows[0]?.exact_match === true;
}

/** This is a read by the still-current lease holder. It is not terminal recovery after Work completion. */
export async function readAttachedEnrollment(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  command: CommandIdentity,
): Promise<EnrolledResult | undefined> {
  if (!await exactEffectMatches(query, input, true)) return undefined;

  const recorded = await readCommandReceipt(query, command, resultSchema, "0");
  const expected = enrollmentResult(input);
  if (recorded.status !== "committed" || typeof recorded.body !== "object"
      || recorded.body === null || Array.isArray(recorded.body)) return undefined;
  const body = recorded.body as Record<string, unknown>;
  if (Object.keys(body).length !== 3 || body.outcome !== expected.outcome
      || body.selectionRevision !== expected.selectionRevision || body.receipt !== expected.receipt) return undefined;

  const { customer, rows, source } = input;
  const proof = await query`
    SELECT e.id::text
    FROM platform.runtime_effect_receipt e
    JOIN platform.runtime_command_receipt c ON c.id = e.command_receipt_id
    JOIN platform.runtime_inbox_receipt i ON i.effect_receipt_id = e.id
    JOIN app.track_enrollment_receipt r ON r.effect_receipt_id = e.id
    WHERE e.id = ${rows.effect}::uuid AND c.id = ${rows.command}::uuid
      AND e.source_revision = 0 AND e.result_schema_id = ${enrollmentResultSchema}
      AND e.result_hash = c.result_digest AND c.result_body->>'receipt' = r.id::text
      AND i.id = ${rows.inbox}::uuid AND i.outbox_message_id = ${source.outboxId}::uuid
      AND r.id = ${rows.enrollment}::uuid AND r.user_id = ${customer.userId}::uuid
      AND r.track = 'customer' AND r.profile_id = ${customer.customerProfileId}::uuid
      AND r.source_owner = ${customerOwner} AND r.source_creation_revision = 0
      AND r.selection_id = ${rows.selection}::uuid AND r.selection_revision = 0 AND r.result_code = 'enrolled'
      AND r.semantic_key = ${command.semanticKey} AND r.fingerprint = ${command.fingerprint}
  `;
  return proof.length === 1 && proof[0]?.id === rows.effect ? expected : undefined;
}

async function stageEffect(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  command: CommandIdentity,
  result: EnrolledResult,
) {
  const { rows, lease, source } = input;
  requireOne(await query`
    INSERT INTO platform.runtime_command_receipt (
      id, owner_module_id, operation, subject_scope, semantic_key, fingerprint, state, source_revision,
      result_schema_id, result_schema_version, result_digest, result_body
    ) VALUES (
      ${command.receiptId}::uuid, ${trackOwner}, ${enrollmentAction}, ${command.subjectScope}, ${command.semanticKey},
      ${command.fingerprint}, 'pending', 0, ${enrollmentResultSchema}, '1', NULL, NULL
    ) RETURNING id::text
  `, rows.command);

  const committed = await query`
    WITH result AS (SELECT ${JSON.stringify(result)}::text::jsonb AS body)
    UPDATE platform.runtime_command_receipt AS c
    SET state = 'committed', result_body = result.body,
        result_digest = pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(result.body::text, 'UTF8')), 'hex')
    FROM result
    WHERE c.id = ${command.receiptId}::uuid AND c.state = 'pending'
    RETURNING c.id::text, c.result_digest::text
  `;
  requireOne(committed, rows.command);
  const digest = committed[0]?.result_digest;
  if (typeof digest !== "string" || !sha256.test(digest)) throw new Error("unconfirmed_track_result_digest");

  await query`
    INSERT INTO platform.runtime_effect_receipt (
      id, command_receipt_id, owner_module_id, operation, subject_scope, semantic_effect_key, fingerprint, state,
      source_revision, fence, result_schema_id, result_hash, committed_at
    ) VALUES (
      ${rows.effect}::uuid, ${rows.command}::uuid, ${trackOwner}, ${enrollmentAction}, ${command.subjectScope},
      ${command.semanticKey}, ${command.fingerprint}, 'committed', 0, ${lease.fence.toString()}::bigint,
      ${enrollmentResultSchema}, ${digest}, pg_catalog.clock_timestamp()
    )
  `;
  await query`
    INSERT INTO platform.runtime_inbox_receipt (id, outbox_message_id, consumer_owner, handler_name, payload_hash, effect_receipt_id)
    VALUES (${rows.inbox}::uuid, ${source.outboxId}::uuid, ${trackOwner}, ${enrollmentAction},
            ${command.fingerprint}, ${rows.effect}::uuid)
  `;
  if (!await exactEffectMatches(query, input, false)) throw new Error("unconfirmed_track_effect_before_attachment");

  requireOne(await query`
    UPDATE platform.runtime_work_item
    SET effect_receipt_id = ${rows.effect}::uuid
    WHERE id = ${lease.workId}::uuid AND outbox_message_id = ${source.outboxId}::uuid
      AND state = 'leased' AND fence = ${lease.fence.toString()}::bigint AND effect_receipt_id IS NULL
      AND lease_expires_at > pg_catalog.clock_timestamp()
      AND platform_private.lease_secret_matches(lease_token_hash::text)
    RETURNING id::text
  `, lease.workId);
}

async function stageEnrollment(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  command: CommandIdentity,
) {
  const { rows, customer, catalog, source, historyName } = input;
  const { userId, customerProfileId } = customer;
  await query`
    INSERT INTO app.track_subscriptions (
      id, user_id, track, customer_profile_id, candidate_profile_id, professional_profile_id, plan_id, status, provider
    ) VALUES (
      ${rows.subscription}::uuid, ${userId}::uuid, 'customer', ${customerProfileId}::uuid,
      NULL, NULL, ${catalog.planId}::uuid, 'active', 'none'
    )
  `;
  await query`
    INSERT INTO app.track_base_selection (
      id, user_id, track, customer_profile_id, candidate_profile_id, professional_profile_id, subscription_id, source_generation
    ) VALUES (
      ${rows.selection}::uuid, ${userId}::uuid, 'customer', ${customerProfileId}::uuid,
      NULL, NULL, ${rows.subscription}::uuid, ${source.privacyGeneration}::bigint
    )
  `;
  await query`
    INSERT INTO app.track_subscription_events (id, subscription_id, plan_id, user_id, name, from_status, to_status, provider)
    VALUES (
      ${rows.history}::uuid, ${rows.subscription}::uuid, ${catalog.planId}::uuid, ${userId}::uuid,
      ${historyName}, NULL, 'active', 'none'
    )
  `;
  await query`
    INSERT INTO app.track_entitlement_grants (
      id, user_id, track, customer_profile_id, candidate_profile_id, professional_profile_id,
      subscription_id, entitlement_id, status, value_type, boolean_value, starts_at, source_plan_id, source_event_id
    ) VALUES (
      ${rows.grant}::uuid, ${userId}::uuid, 'customer', ${customerProfileId}::uuid, NULL, NULL,
      ${rows.subscription}::uuid, ${catalog.definitionId}::uuid, 'active', 'boolean', ${catalog.value}::boolean,
      pg_catalog.clock_timestamp(), ${catalog.planId}::uuid, ${rows.history}::uuid
    )
  `;
  await query`
    INSERT INTO app.track_enrollment_receipt (
      id, user_id, track, profile_id, source_owner, source_creation_revision, selection_id, selection_revision,
      semantic_key, fingerprint, result_code, effect_receipt_id
    ) VALUES (
      ${rows.enrollment}::uuid, ${userId}::uuid, 'customer', ${customerProfileId}::uuid, ${customerOwner},
      0, ${rows.selection}::uuid, 0, ${command.semanticKey}, ${command.fingerprint}, 'enrolled', ${rows.effect}::uuid
    )
  `;
}

async function stageOwnerEvidence(query: OwnerQuery, input: KnownFirstFreeEnrollment) {
  const { rows, customer, source, decisionRef } = input;
  const subject = { userId: customer.userId, track: "customer", revision: "0" };
  const evidence = [
    { id: rows.subscriptionEvidence, model: "TrackSubscription", primaryKey: { id: rows.subscription },
      committed: { id: rows.subscription, ...subject, status: "active", provider: "none" } },
    { id: rows.selectionEvidence, model: "TrackBaseSelection", primaryKey: { id: rows.selection },
      committed: { id: rows.selection, ...subject, customerProfileId: customer.customerProfileId,
        candidateProfileId: null, professionalProfileId: null, subscriptionId: rows.subscription,
        sourceGeneration: source.privacyGeneration } },
    { id: rows.grantEvidence, model: "TrackEntitlementGrant", primaryKey: { id: rows.grant },
      committed: { id: rows.grant, ...subject, status: "active", valueType: "boolean" } },
  ];
  for (const { id, model, primaryKey, committed } of evidence) {
    const body = { schema: "database-owner-evidence.v1", owner: trackOwner, model, primaryKey, prior: null, committed, decisionRef };
    const schema = `urn:workinants:database-review:owner-evidence:v1#/$defs/${model}`;
    await query`
      WITH e AS (SELECT ${JSON.stringify(body)}::text::jsonb AS body)
      INSERT INTO platform.owner_mutation_evidence (
        id, command_receipt_id, owner_module_id, aggregate_kind, aggregate_id, committed_revision, action,
        decision_ref, evidence_schema_id, evidence_schema_version, evidence_digest, evidence_body
      ) SELECT ${id}::uuid, ${rows.command}::uuid, ${trackOwner}, ${model}, ${primaryKey.id}, 0, ${enrollmentAction},
               ${decisionRef}, ${schema}, '1',
               pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(e.body::text, 'UTF8')), 'hex'), e.body
        FROM e
    `;
  }
}

export async function commitFirstFreeEnrollment(
  query: OwnerQuery,
  input: KnownFirstFreeEnrollment,
  command: CommandIdentity,
  work: LiveWork,
  servicePrincipal: string,
): Promise<EnrolledResult> {
  const result = enrollmentResult(input);
  await stageEffect(query, input, command, result);
  await stageEnrollment(query, input, command);
  await stageOwnerEvidence(query, input);

  const { rows, lease, attemptReasonCode } = input;
  await query`
    INSERT INTO platform.runtime_attempt (id, work_item_id, attempt_number, fence, worker_id, result, reason_code, started_at, finished_at)
    VALUES (
      ${rows.attempt}::uuid, ${lease.workId}::uuid, ${work.attemptCount}::integer, ${lease.fence.toString()}::bigint,
      ${servicePrincipal}, 'committed', ${attemptReasonCode}, ${work.startedAt}::timestamptz, pg_catalog.clock_timestamp()
    )
  `;
  if (!await readAttachedEnrollment(query, input, command)) throw new Error("unconfirmed_track_enrollment");
  return result;
}
