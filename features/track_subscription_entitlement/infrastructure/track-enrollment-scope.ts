import type { KnownWorkLease } from "../../../server/platform/runtime/work-leases";

export const trackOwner = "track_subscription_entitlement";
export const customerOwner = "customer_buyer_profile";
export const enrollmentAction = "assignDefaultFreeTrack.v1";
export const enrollmentPurpose = "default_free_enrollment";
const payloadSchema = "urn:workinants:database-review:foundation-payloads:v1#/$defs/";
export const enrollmentCommandSchema = `${payloadSchema}assignDefaultFreeTrackCustomerCommand`;
export const enrollmentResultSchema = `${payloadSchema}assignDefaultFreeTrackCustomerResult`;

export type EnrollmentRows = Readonly<{
  command: string;
  effect: string;
  inbox: string;
  subscription: string;
  selection: string;
  grant: string;
  history: string;
  enrollment: string;
  subscriptionEvidence: string;
  selectionEvidence: string;
  grantEvidence: string;
  attempt: string;
}>;

/** The trusted platform call supplies the existing lease and resolves both owner inputs before opening PostgreSQL. */
export type KnownFirstFreeEnrollment = Readonly<{
  lease: KnownWorkLease;
  customer: Readonly<{
    variant: "customer_buyer_profile.authority_facts.v1";
    sourceToken: "0";
    asOf: string;
    customerProfileId: string;
    userId: string;
    lifecycle: "active";
  }>;
  source: Readonly<{
    outboxId: string;
    creationReceiptId: string;
    privacyGeneration: "0";
  }>;
  catalog: Readonly<{
    planId: string;
    planKey: string;
    planVersion: string;
    planContentHash: string;
    definitionId: string;
    definitionKey: string;
    membershipId: string;
    value: boolean;
    usagePeriod: string | null;
  }>;
  rows: EnrollmentRows;
  decisionRef: string;
  historyName: string;
  attemptReasonCode: string;
}>;

const workSelect = [
  "attemptCount", "createdAt", "effectReceiptId", "fence", "handlerName", "id", "leaseExpiresAt",
  "leaseTokenHash", "mutationTransactionId", "nextAttemptAt", "outboxMessageId", "semanticWorkKey", "state",
];
const outboxSelect = [
  "aggregateId", "aggregateKind", "causationId", "commandReceiptId", "correctionOfId", "correlationId",
  "createdAt", "effectiveAt", "id", "kind", "mutationTransactionId", "name", "occurredAt", "ordinal",
  "payload", "payloadHash", "payloadSchemaId", "producerOwner", "schemaVersion", "sourceGeneration", "sourceRevision",
];
const commandInsert = [
  "fingerprint", "id", "operation", "ownerModuleId", "resultBody", "resultDigest", "resultSchemaId",
  "resultSchemaVersion", "semanticKey", "sourceRevision", "state", "subjectScope",
];
const effectInsert = [
  "commandReceiptId", "committedAt", "fence", "fingerprint", "id", "operation", "ownerModuleId",
  "resultHash", "resultSchemaId", "semanticEffectKey", "sourceRevision", "state", "subjectScope",
];
const inboxInsert = ["consumerOwner", "effectReceiptId", "handlerName", "id", "outboxMessageId", "payloadHash"];
const evidenceInsert = [
  "action", "aggregateId", "aggregateKind", "commandReceiptId", "committedRevision", "decisionRef",
  "evidenceBody", "evidenceDigest", "evidenceSchemaId", "evidenceSchemaVersion", "id", "ownerModuleId", "previousRevision",
];
const attemptInsert = ["attemptNumber", "fence", "finishedAt", "id", "reasonCode", "result", "startedAt", "workItemId", "workerId"];
const typedSubject = ["candidateProfileId", "customerProfileId", "id", "professionalProfileId", "track", "userId"];
const subscriptionInsert = [...typedSubject, "planId", "provider", "status"];
const selectionInsert = [...typedSubject, "sourceGeneration", "subscriptionId"];
const grantInsert = [
  ...typedSubject, "booleanValue", "decimalValue", "entitlementId", "intValue", "sourceEventId",
  "sourcePlanId", "startsAt", "status", "stringValue", "subscriptionId", "valueType",
];
const enrollmentInsert = [
  "effectReceiptId", "fingerprint", "id", "profileId", "resultCode", "selectionId", "selectionRevision",
  "semanticKey", "sourceCreationRevision", "sourceOwner", "track", "userId",
];

const fields = (model: string, id: string, operation: string, keys: readonly string[]) =>
  keys.map((key) => `${model}/${id}/${operation}/${key}`);
const withTimestamps = (keys: readonly string[]) => [...keys, "createdAt", "mutationTransactionId"];

/** Derive the finite, positive-only field list. This neither issues a grant nor resolves authority. */
export function firstFreeEnrollmentFields({ rows, lease, source, customer, catalog }: KnownFirstFreeEnrollment): string[] {
  return [
    `CustomerProfile/${customer.customerProfileId}/revision/${customer.sourceToken}`,
    ...fields("RuntimeWorkItem", lease.workId, "SELECT", workSelect),
    ...fields("RuntimeWorkItem", lease.workId, "UPDATE", ["@row", "effectReceiptId"]),
    `RuntimeWorkItem/${lease.workId}/revision/${lease.fence}`,
    `RuntimeWorkItem/${lease.workId}/command/${rows.command}`,
    `RuntimeWorkItem/${lease.workId}/effect/${rows.effect}`,
    ...fields("RuntimeOutboxMessage", source.outboxId, "SELECT", outboxSelect),
    ...fields("RuntimeCommandReceipt", rows.command, "INSERT", commandInsert),
    ...fields("RuntimeCommandReceipt", rows.command, "SELECT", withTimestamps(commandInsert)),
    ...fields("RuntimeCommandReceipt", rows.command, "UPDATE", ["@row", "resultBody", "resultDigest", "state"]),
    ...fields("RuntimeEffectReceipt", rows.effect, "INSERT", effectInsert),
    ...fields("RuntimeEffectReceipt", rows.effect, "SELECT", withTimestamps(effectInsert)),
    `RuntimeEffectReceipt/${rows.effect}/revision/${lease.fence}`,
    ...fields("RuntimeInboxReceipt", rows.inbox, "INSERT", inboxInsert),
    ...fields("RuntimeInboxReceipt", rows.inbox, "SELECT", withTimestamps(inboxInsert)),
    ...fields("TrackPlan", catalog.planId, "SELECT", ["billingModel", "contentHash", "id", "key", "revision", "status", "track", "version"]),
    `TrackPlan/${catalog.planId}/revision/0`,
    `TrackPlan/${catalog.planId}/version/${catalog.planVersion}`,
    `TrackPlan/${catalog.planId}/contentHash/${catalog.planContentHash}`,
    ...fields("TrackEntitlementDefinition", catalog.definitionId, "SELECT", ["id", "isActive", "key", "revision", "track", "valueType"]),
    `TrackEntitlementDefinition/${catalog.definitionId}/revision/0`,
    ...fields("TrackPlanEntitlement", catalog.membershipId, "SELECT", [
      "booleanValue", "decimalValue", "entitlementId", "id", "intValue",
      "planId", "revision", "stringValue", "usagePeriod", "valueType",
    ]),
    `TrackPlanEntitlement/${catalog.membershipId}/revision/0`,
    ...fields("TrackSubscription", rows.subscription, "INSERT", subscriptionInsert),
    ...fields("TrackSubscription", rows.subscription, "SELECT", [
      ...subscriptionInsert, "currentPeriodEnd", "currentPeriodStart", "endedAt", "revision",
    ]),
    `TrackSubscription/${rows.subscription}/revision/0`,
    ...fields("TrackBaseSelection", rows.selection, "INSERT", selectionInsert),
    ...fields("TrackBaseSelection", rows.selection, "SELECT", [...selectionInsert, "revision"]),
    `TrackBaseSelection/${rows.selection}/revision/0`,
    ...fields("TrackSubscriptionEvent", rows.history, "INSERT", [
      "fromStatus", "id", "name", "planId", "provider", "subscriptionId", "toStatus", "userId",
    ]),
    ...fields("TrackEntitlementGrant", rows.grant, "INSERT", grantInsert),
    ...fields("TrackEntitlementGrant", rows.grant, "SELECT", [...grantInsert, "expiresAt", "revokedAt", "revision"]),
    `TrackEntitlementGrant/${rows.grant}/revision/0`,
    ...fields("TrackEnrollmentReceipt", rows.enrollment, "INSERT", enrollmentInsert),
    ...fields("TrackEnrollmentReceipt", rows.enrollment, "SELECT", enrollmentInsert),
    ...[rows.subscriptionEvidence, rows.selectionEvidence, rows.grantEvidence].flatMap((id) => [
      ...fields("OwnerMutationEvidence", id, "INSERT", evidenceInsert),
      ...fields("OwnerMutationEvidence", id, "SELECT", withTimestamps(evidenceInsert)),
    ]),
    ...fields("RuntimeAttempt", rows.attempt, "INSERT", attemptInsert),
    ...fields("RuntimeAttempt", rows.attempt, "SELECT", withTimestamps(attemptInsert)),
    `RuntimeAttempt/${rows.attempt}/revision/${lease.fence}`,
  ].sort();
}
