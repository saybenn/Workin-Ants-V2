import {
  OwnerTransactionFailure, runOwnerTransaction, type DatabaseActionContext, type OwnerDatabase,
} from "../../../server/platform/persistence/owner-transaction";
import {
  commitFirstFreeEnrollment, enrollmentCommand, readApprovedFreeCatalog, readAttachedEnrollment,
  readExactIntent, readLiveWork, type EnrolledResult,
} from "../infrastructure/track-enrollment-repository";
import {
  customerOwner, enrollmentAction, enrollmentPurpose, firstFreeEnrollmentFields, trackOwner,
  type KnownFirstFreeEnrollment,
} from "../infrastructure/track-enrollment-scope";

const uuid = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/;
const key = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const sha256 = /^[0-9a-f]{64}$/;
const maxGeneration = BigInt("9223372036854775807");

export type FirstFreeEnrollmentOutcome =
  | { status: "enrolled" | "replay"; value: EnrolledResult }
  | { status: "denied" | "unavailable" | "rolled_back" | "unconfirmed" };

function acceptsKnownInput(input: KnownFirstFreeEnrollment): boolean {
  const { customer, source, catalog, lease } = input;
  const ids = [customer.customerProfileId, customer.userId, source.outboxId, source.creationReceiptId,
    catalog.planId, catalog.definitionId, catalog.membershipId, lease.workId, ...Object.values(input.rows)];
  const ownerKeys = [catalog.planKey, catalog.planVersion, catalog.definitionKey,
    input.decisionRef, input.historyName, input.attemptReasonCode];
  return ids.every((id) => typeof id === "string" && uuid.test(id)) && new Set(ids).size === ids.length
    && customer.variant === "customer_buyer_profile.authority_facts.v1"
    && customer.lifecycle === "active" && customer.sourceToken === "0" && source.privacyGeneration === "0"
    && typeof customer.asOf === "string" && Number.isFinite(Date.parse(customer.asOf))
    && ownerKeys.every((value) => typeof value === "string" && key.test(value))
    && typeof catalog.planContentHash === "string" && sha256.test(catalog.planContentHash)
    && typeof catalog.value === "boolean" && (catalog.usagePeriod === null || key.test(catalog.usagePeriod))
    && typeof lease.fence === "bigint" && lease.fence > BigInt(0) && lease.fence <= maxGeneration
    && typeof lease.token === "string" && sha256.test(lease.token)
    && lease.expiresAt instanceof Date && Number.isFinite(lease.expiresAt.getTime());
}

/**
 * The trusted server caller supplies a registered Worker action, current Customer owner facts
 * and the approved complete one-binding Free catalog before invoking this known-lease path.
 * Processing commits the attached effect. Work acknowledgment remains a separate lease action.
 */
export async function assignDefaultFreeTrack(
  database: OwnerDatabase,
  context: DatabaseActionContext,
  input: KnownFirstFreeEnrollment,
): Promise<FirstFreeEnrollmentOutcome> {
  const known = {
    ...input,
    lease: { ...input.lease, expiresAt: new Date(input.lease.expiresAt) },
    customer: { ...input.customer },
    source: { ...input.source },
    catalog: { ...input.catalog },
    rows: { ...input.rows },
  };
  if (!acceptsKnownInput(known) || database.runtimeLogin !== "wa_worker" || !("servicePrincipal" in context.principal)
      || !key.test(context.principal.servicePrincipal) || context.owner !== trackOwner || context.action !== enrollmentAction
      || context.purpose !== enrollmentPurpose || context.targetKind !== "RuntimeWorkItem"
      || context.targetId !== known.lease.workId || context.sourceGeneration !== known.lease.fence) return { status: "denied" };
  const expectedFields = firstFreeEnrollmentFields(known);
  if (context.allowedFields.length !== expectedFields.length
      || !expectedFields.every((field, index) => context.allowedFields[index] === field)) return { status: "denied" };

  const semanticKey = `${customerOwner}/${known.customer.customerProfileId}/default-free-enrollment/v1`;
  const worker = context.principal.servicePrincipal;
  try {
    return await runOwnerTransaction<FirstFreeEnrollmentOutcome>(database, context, async (query) => {
      const work = await readLiveWork(query, known, semanticKey);
      if (!work) return { status: "unavailable" };
      const fingerprint = await readExactIntent(query, known, semanticKey);
      if (!fingerprint) return { status: "unavailable" };

      const command = enrollmentCommand(known, semanticKey, fingerprint);
      if (work.effectReceiptId !== null) {
        if (work.effectReceiptId !== known.rows.effect) return { status: "unavailable" };
        const value = await readAttachedEnrollment(query, known, command);
        return value ? { status: "replay", value } : { status: "unavailable" };
      }
      if (!await readApprovedFreeCatalog(query, known)) return { status: "unavailable" };

      const value = await commitFirstFreeEnrollment(query, known, command, work, worker);
      return { status: "enrolled", value };
    });
  } catch (error) {
    if (!(error instanceof OwnerTransactionFailure)) throw error;
    if (error.code === "context_denied") return { status: "denied" };
    if (error.code === "commit_unconfirmed") return { status: "unconfirmed" };
    if (error.code === "rolled_back") return { status: "rolled_back" };
    return { status: "unavailable" };
  }
}
