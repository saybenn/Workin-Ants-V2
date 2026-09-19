# Notification Module Implementation Plan

> **Module ID:** `notification`  
> **Module:** Notification Module  
> **Primary Cluster:** CL-07 — Messaging & Notification Rail  
> **Companion Module architecture:** [Notification architecture](<notification-module-architecture.md>)\
> **Parent build plan:** [CL-07 build plan](<../messaging-notification-rail-build-plan.md>)\
> **Status:** implementation sequence for the Notification Deep Module; subordinate to root and CL-07 architecture  
> **Rule:** this plan implements approved architecture. It does not independently settle Unresolved Decisions, change ownership, or broaden CL-07 product scope.

---

## Core Principle

Implement Notification through narrow, verifiable slices:

```text
public/observable behavior
→ validated Notification command/query
→ Notification-owned routing/payload/lifecycle policy
→ authoritative Notification write/read
→ canonical shared-operation calls
→ optional durable delivery/provider effect
→ audit/observability/privacy effect where required
→ tests
→ exit gate
```

The first usable slice is deliberately **User-targeted in-app Notification truth**, not a generic omnichannel platform. External delivery, Organization fan-out, provider callbacks, privacy execution, and hardening are added only after the required boundaries are proven.

A capability does not require artificial end-user UI. The observable result of a later feature may be a contract harness, worker result, protected admin inspector, provider callback trace, or Privacy execution result.

---

## Build Rules

1. Follow [project overview V3](<../../../project-overview-v3.md>), root `architecture.md`, root `code-standards.md`, Canonical Shared Operations, [CL-07 architecture](<../messaging-notification-rail-architecture.md>), and [Notification architecture](<notification-module-architecture.md>).
2. Notification owns only `Notification`, `NotificationSubscription`, `NotificationDelivery`, `NotificationSubscriptionEvent`, their approved lifecycle policy, safe rendering/routing, provider delivery, and provider-result translation.
3. The source Module owns the event, legal/business meaning, source state, and decision that an alert is required.
4. Every source uses SH-041 `requestNotification`; no source directly inserts Notification rows or calls notification provider SDKs.
5. Consume other Modules through approved public interfaces/events. Foreign keys are not permission to import their repositories.
6. Reuse canonical Shared Operations. Do not create Notification-local authentication, authorization, idempotency, queue, retry, dead-letter, webhook-security, cryptography, audit, or observability infrastructure.
7. Every public mutation is runtime-validated, server-authorized where applicable, and semantically idempotent when retries are possible.
8. RLS is defense in depth and must agree with Role / Authority.
9. Lifecycle changes are transaction-safe; stale/concurrent operations return deterministic results.
10. External delivery work is durable, correlated, retry-bounded, observable, and independent of source business transaction success.
11. Provider-specific types, secrets, status strings, callbacks, and error mappings stay behind Notification provider adapters.
12. Provider callbacks authenticate before parsing/state mutation and dedupe before side effects.
13. Consent proof, browser permission, Subscription reachability, Delivery evidence, and interaction evidence remain separate.
14. Privacy / Data Erasure owns request/job/target/exemption/export orchestration. Notification only enumerates/executes against its own records/provider resources.
15. Audit/Event Ledger owns generic AuditEvent/AccessAuditLog. Observability owns public failure/queue telemetry capabilities; their persistence remains CL-09-gated. Neither replaces Notification truth.
16. Track Subscription & Entitlement remains commercial policy truth; no local premium or `canNotify` entitlement flag.
17. Notification has no public Search responsibility.
18. Private Message bodies, PHI, OTP/recovery tokens, financial/tax details, raw resume data, identity documents, contract text, and provider credentials are prohibited from unsafe outward payloads and generic telemetry.
19. Do not add speculative schema columns/tables to “solve” an Unresolved Decision. Close the decision in architecture first.
20. Every numbered feature ends with tests and an explicit exit gate. Do not begin the next Module feature until the current exit gate passes, except where the parent Cluster plan explicitly permits parallel work and dependencies are satisfied.
21. If implementation settles a previously unresolved binding decision, update CL-07 architecture first, then Module architecture and this plan, then code.

---

**Approved SMS ownership boundary (CL-07-R002):** generic business SMS alerts use Notification through SH-041 `requestNotification`; source Modules must not dispatch generic SMS directly. Identity & Access may use an Identity-owned verification provider whose protocol delivers an OTP or challenge. Identity retains challenge generation, expiry, attempts, verification outcome, assurance result, and provider protocol truth. Notification must not independently generate, validate, resend, or implement a parallel OTP/MFA transport/verification workflow. This verification-provider transport is not a second generic notification rail. Only initial production generic SMS provider selection remains unresolved under U-CL07-16.

Source-provider import checks in this plan cover generic alert delivery and must permit the Identity-owned verification-provider protocol.

## Preconditions

**Shared Operations status:** references marked **Proposed ruling** are planning dependencies only, not approval for shared schema/API commitment or a generic service. Independently justified owner-specific interfaces do not approve a proposed shared operation globally. Realtime remains post-commit, authorized, and rebuildable; Moderation integration consumes approved contracts. Canonical metadata and reusable boundaries remain controlled by the Shared Operations registry.

**CL-07-R007 — Observability persistence boundary:** CL-07 consumes approved public capabilities for failure recording, queue telemetry, health, structured logging, metrics, and exception capture. `IntegrationFailure`, `QueueJob`, `OpsIncident`, and `SystemEvent` are not current Prisma models. CL-09 owns its unresolved persistence/status design. CL-07 must not create local substitutes or couple Messaging/Notification business status to any future operational record.

### Hard platform prerequisites

The following must exist in canonical owner/shared scope before dependent Notification features exit:

- Prisma/PostgreSQL migration workflow;
- runtime schema validation using the root-approved validation library;
- SH-001 `resolveAuthenticatedActor` from Identity & Access;
- SH-002 `authorizeResourceAction` from Role / Authority, with aligned RLS conventions;
- canonical SH-044 `executeIdempotentCommand` infrastructure;
- canonical request/correlation context;
- one reliable queue/worker framework;
- retry/backoff/dead-letter mechanics;
- SH-033 `writeStructuredLog`, metrics, exception capture, SH-037 `recordIntegrationFailure`, and queue telemetry interfaces;
- centralized cryptography for encryption/HMAC;
- generic SH-029 `appendAuditEvent` and SH-030 `recordSensitiveAccess` interfaces;
- transactional outbox/inbox only when an implemented source/event contract uses events.

If a platform primitive is missing, implement the minimum canonical prerequisite in its owning shared/platform scope. Do not create a Notification-local substitute.

### Hard Module-interface prerequisites

- Identity & Access: authenticated actor context.
- Role / Authority: protected action decision.
- Consent & Disclosure: SH-008 `queryConsentProof` before production consent-dependent push onboarding/use.
- Privacy / Data Erasure: privacy handler protocol before production privacy fulfillment.
- Audit / Event Ledger: generic audit/access proof interface before a policy requiring those proofs is production-enabled.
- Organization Hiring: owner recipient/settings query before Organization routing exits.

### Source-workflow interfaces that may initially be stubbed

Typed fixtures/fakes may represent owner public contracts until those source Modules exist:

- Messaging new-message intent;
- Gig / Order alert intent;
- Booking/scheduling alert intent;
- Candidate Application / Job Interview alert intent;
- Track Subscription/Entitlement lifecycle alert intent;
- Moderation/Hold/FCRA/DMCA notice intent;
- Prize/Reward alert intent;
- Identity security/recovery delivery intent.

A stub must mimic the eventual public contract only. It must never become a local copy of the source schema or business lifecycle.

**PR-N04 — Approved target credential authority (CL-07-R010).** Production recoverable provider credential material uses approved encrypted storage through SH-075 `encryptSensitiveValue`; stable comparison/identity uses normalized purpose-bound hashes through SH-076 `normalizeAndHashIdentifier`. Plaintext `endpoint`, `token`, `p256dh`, and `auth` must not remain parallel authoritative representations after migration, and code must not treat plaintext and encrypted/hash values as equal source truth. U-CL07-18 remains unresolved for exact provider/platform/hash composite uniqueness, backfill, rotation during cutover, replacement order of plaintext uniqueness constraints, and any temporary compatibility period. This approval is not a migration design or permission to change current schema/constraints without separate review.

### Architecture blockers by Cluster decision

| Decision | Must be closed before |
| --- | --- |
| U-CL07-09 — recipient/cardinality/fan-out | Feature 06 Organization Recipient Routing exits |
| U-CL07-10/11/12/13/15/19 — channel/aggregate/expiry/retry/provider/interactions | Feature 05 Delivery Semantics exits; broad production multi-channel delivery |
| U-CL07-14 — Notification processed-provider-event schema | Feature 10 Provider Callbacks exits |
| U-CL07-16 — generic SMS provider selection; Identity verification ownership resolved | production generic SMS enablement |
| U-CL07-17 — Web Push provider | production Web Push enablement |
| U-CL07-18 — migration/uniqueness implementing approved PR-N04 | Feature 03 live credential storage exits |
| U-CL07-20/21 — template governance + safe payload catalog | Feature 02 production external-channel readiness and Feature 04 production-enabled external channels |
| Privacy retention decisions relevant to Notification | Feature 08 destructive production privacy execution |

### Shared Operation reference metadata

Only referenced operations are listed. Invocation, local policy, and integration proof remain in the relevant features; canonical boundaries remain in the Shared Operations registry.

| ID / canonical name | Canonical owner | Classification | Status |
| --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | Cross-cutting capability | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Each source Module | Shared contract; separate implementations | Proposed ruling |
| SH-008 `queryConsentProof` | Consent & Disclosure | Platform consent capability | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Platform audit capability | Confirmed |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` | Observability / platform infrastructure | Platform primitive | Confirmed |
| SH-033 `writeStructuredLog` | Observability / Ops | Platform capability | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | Cross-cutting capability | Confirmed |
| SH-035 `captureException` | Observability / Ops | Provider adapter | Confirmed |
| SH-036 `emitMetric` | Observability / Ops | Platform capability | Confirmed |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Cross-cutting capability | Confirmed |
| SH-038 `recordQueueTelemetry` | Observability / Ops / queue infrastructure | Cross-cutting capability | Confirmed |
| SH-039 `checkServiceHealth` | Observability / Ops coordinates; owner supplies check | Cross-cutting capability | Confirmed |
| SH-041 `requestNotification` | Notification | Platform notification capability | Confirmed |
| SH-042 `renderNotificationTemplate` | Notification | Cross-cutting capability | Confirmed |
| SH-043 `resolveNotificationRecipients` | Source context owner plus Notification | Shared contract; separate policy | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | Platform primitive | Confirmed |
| SH-045 `deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox | Platform primitive | Confirmed |
| SH-046 `publishDomainEvent` | Platform event/outbox infrastructure | Platform primitive | Confirmed |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | Platform primitive | Confirmed |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform infrastructure | Platform primitive | Confirmed |
| SH-051 `acquireAggregateLock` | Shared persistence infrastructure | Platform primitive | Confirmed |
| SH-052 `withOptimisticConcurrency` | Shared persistence infrastructure | Platform primitive | Confirmed |
| SH-053 `transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy | Shared mechanism; separate truth | Confirmed |
| SH-055 `runDeadlineExpiration` | Shared scheduler/queue infrastructure | Cross-cutting capability | Confirmed |
| SH-059 `verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm | Provider-adapter contract | Confirmed |
| SH-060 `deduplicateProviderEvent` | Provider-owning Module using shared primitive | Shared mechanism; separate truth | Confirmed |
| SH-061 `translateProviderStatus` | Provider-owning adapter | Provider-adapter contract | Confirmed |
| SH-062 `reconcileProviderState` | Each provider-owning Module using shared worker framework | Shared mechanism; separate policy | Confirmed |
| SH-066 `validateStructuredProviderOutput` | Shared validation primitive; consuming Module owns schema | Cross-cutting capability | Confirmed |
| SH-070 `deleteProviderResource` | Provider-owning Module | Provider-adapter contract | Confirmed |
| SH-072 `hashCanonicalPayload` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-075 `encryptSensitiveValue` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-076 `normalizeAndHashIdentifier` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | Cross-cutting protocol | Confirmed |
| SH-096 `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | Cross-cutting protocol | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | Cross-cutting protocol | Confirmed |
| SH-098 `anonymizePersonalFields` | Shared primitive; record owner supplies mapping | Cross-cutting capability | Confirmed |

### Parent Cluster sequencing

This Module plan begins at the Notification portion of CL-07. CL-07 Features 01–04 are Messaging work. Notification Feature 01 below requires the **safe Notification handoff contract from Cluster Feature 04** or an equivalent approved fixture. This plan does not reimplement Messaging features.

---

# IMPLEMENTATION PHASES

## Phase 1 — Canonical Intake and Safe In-App Truth

### 01 Canonical In-App Notification Intake and Center

#### Objective

Establish SH-041 `requestNotification` as the single Notification intake path and prove durable User-targeted `in_app` Notification truth before external providers or Organization fan-out are introduced.

#### Observable Result

An authenticated User receives a representative in-app alert created through SH-041 `requestNotification`, can list it in a Notification center, see a correct unread count, open an approved authenticated action route, mark it read, and dismiss it. The referenced source workflow is unchanged by read/dismiss behavior.

#### Cluster Build-Plan Link

- Supports **CL-07 Feature 05 — Canonical In-App Notification Intake and Center**.
- Depends on the safe handoff established by **CL-07 Feature 04 — Message Media and Safe Notification Handoff** or an equivalent approved source-contract fixture.

#### Dependencies

- current Prisma `Notification` and `NotificationStatus`;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-032 `createRequestContext`;
- SH-034 `sanitizeTelemetryMetadata`;
- source/Messaging safe SH-041 `requestNotification` fixture/contract.

No external provider is required.

#### In Scope

- Notification request DTO and runtime validation;
- User-targeted `channel=in_app` intake only;
- semantic idempotency for request creation;
- Notification repository/application service;
- `listNotifications`;
- `getUnreadNotificationCount`;
- `markNotificationRead`;
- `dismissNotification` using existing schema semantics only;
- protected in-app Notification center with loading/empty/error states;
- approved internal action-route validation for the first templates/fixtures;
- RLS/server authorization agreement for User-target access;
- safe correlation/telemetry.

#### Out of Scope

- Organization targets/fan-out;
- external email/SMS/Web Push;
- push subscriptions;
- multi-channel aggregate status;
- retry attempt history;
- provider callbacks/reconciliation;
- mutable template database;
- marketing/broadcast notification behavior;
- an expired status or `dismissedAt` field that has not been approved.

#### Module-Owned Data

- `Notification`;
- `NotificationStatus`;
- `NotificationChannel.in_app`;
- `NotificationPriority`;
- `NotificationPayloadSensitivity` as intake classification.

For this feature, create a concrete `userId` target only and do not use Organization routing.

#### Public Interfaces

Introduce/stabilize:

- SH-041 `requestNotification`;
- `listNotifications`;
- `getUnreadNotificationCount`;
- `markNotificationRead`;
- `dismissNotification`.

The request response must distinguish accepted/rejected and include a Notification reference without exposing provider concepts.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | all User center commands/queries | target Notification action | local `notificationCurrentUser` helper | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | before list/read/dismiss | Notification supplies targeted-user facts | Notification RBAC/permission engine | Cross-cutting capability | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | request intake, read/dismiss when retryable | semantic request key/replay behavior | local idempotency table/service | Platform primitive | Confirmed |
| SH-032 `createRequestContext` | Observability / platform infrastructure | request entry | safe correlation labels | local correlation framework | Platform primitive | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | before logs/errors | allow only safe Notification IDs/template key/status | ad hoc payload scrubber | Cross-cutting capability | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | only if a sensitive/admin action policy requires it | ordinary User read need not be audited by default | `NotificationAuditLog` | Platform audit capability | Confirmed |

SH-041 `requestNotification` itself is the Notification-owned canonical capability being implemented, not a shared helper to import from elsewhere.

#### Domain Logic

1. Validate source Module/type/id reference format, recipient target, priority, sensitivity, safe variables, action route, and idempotency key.
2. Accept only a concrete User target for this slice.
3. Accept only `in_app` channel for this slice.
4. Persist the Notification after validation and idempotency claim.
5. Treat `Notification` as alert truth only; do not query source tables to reconstruct the source event.
6. User list/read/dismiss operations are scoped to the targeted User.
7. Read/dismiss changes Notification truth only.
8. Unread count is derived from Notification state and must not be reused as Messaging unread state.
9. If `expiresAt` is present, do not invent an expired lifecycle status. Display suppression may occur only if consistent with current CL-07 architecture and must not claim a completed expiry lifecycle.
10. Safe new-message fixtures contain Thread/Message IDs or safe display reference only, never the private Message body.

#### Authorization / Compliance

- authenticated User required for User-facing reads/mutations;
- Role / Authority must approve ownership-scoped action;
- User A cannot read/mutate User B Notification;
- client-provided `userId` is not authority;
- action route must be approved/authenticated;
- no private source data enters generic logs;
- no Organization notification yet.

#### Database / Transaction Behavior

- claim idempotency and create Notification atomically according to canonical primitive;
- duplicate semantic request returns original result/effect;
- read/dismiss transition updates only the intended row under authorized scope;
- transaction must not touch source workflow tables;
- use current indexes; do not add speculative projection/counter table;
- respect current schema even though target cardinality is unresolved globally.

#### Events / Jobs

No external delivery job required. No new Notification event catalog is introduced. If a source test uses an event, the source event must already have an approved contract and the consumer must use canonical inbox dedupe.

#### Provider Integration

None.

#### UI / Admin Surface

Notification center:

- unread/read state;
- priority indicator;
- safe title/body snapshot;
- authenticated source action link;
- read/dismiss actions;
- pagination/cursor pattern per root standards;
- loading, empty, error, retry states.

Do not expose raw `payload` if it contains internal-only metadata.

#### Failure Behavior

- invalid request/template placeholder/route/sensitivity shape → reject before write;
- duplicate idempotency key with same semantic fingerprint → original result;
- conflicting duplicate fingerprint → explicit conflict per canonical idempotency contract;
- unauthorized read/dismiss → deny without leaking existence;
- source remains committed if Notification intake is unavailable;
- center load failure does not destroy persisted Notification;
- concurrent read/dismiss returns deterministic current/conflict result.

#### Tests

- unit: request validation, User-target restriction, route validation, sensitivity rules;
- unit: read/dismiss transition behavior using current enum;
- integration: create/list/read/dismiss/count;
- integration: no source-table mutation;
- idempotency: duplicate intake creates one semantic effect;
- authorization/RLS: cross-User denial;
- contract: Messaging safe request creates in-app alert;
- E2E: Message commit → recipient in-app alert → action opens Thread → Message remains source truth;
- telemetry fixture scan for private body/secrets.

#### Documentation Updates

- record any implemented public DTO/reason-code names in this Module architecture if they become binding;
- update progress tracker;
- do not update U-CL07 decisions merely because this limited User/in-app slice works.

#### Acceptance Criteria

- all alerts in the slice enter through SH-041 `requestNotification`;
- User-target in-app Notification persists durably;
- list/unread/read/dismiss work only for authorized User;
- duplicate requests do not duplicate semantic alert effect;
- read/dismiss never changes source state;
- new-message safe fixture contains no private body;
- no external provider SDK or queue is introduced.

#### Exit Gate

Run root-required typecheck/lint/build plus Notification unit/integration/contract/E2E tests. Exit only when:

- one representative source creates an in-app alert exclusively through SH-041 `requestNotification`;
- duplicate request replay converges;
- cross-User authorization/RLS tests pass;
- source-state isolation test passes;
- safe new-message payload test passes;
- Notification center E2E passes.

---

### 02 Template Registry, Payload Safety, and Action Routes

#### Objective

Replace free-form alert content contracts with a controlled, typed, versioned Notification rendering boundary before any production external channel is enabled.

#### Observable Result

A developer/admin contract catalog can enumerate approved Notification template keys/versions, permitted channels, variable schemas, sensitivity, safe-preview rule, and action-route builder. Invalid or prohibited variables cannot be rendered or persisted through canonical intake.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 06 — Template Registry, Payload Safety, and Action Routes**.

#### Dependencies

- Feature 01;
- SH-042 `renderNotificationTemplate` canonical capability;
- PR-N05 or an approved equivalent before treating the registry design as binding;
- U-CL07-20 and U-CL07-21 closed before production external-channel integrations rely on the catalog;
- root validation standards.

A limited in-app-only development catalog may proceed while U-CL07-20/21 remain unresolved if it is explicitly temporary and does not claim production external-channel approval.

#### In Scope

- code/config template registry if PR-N05 is approved;
- typed template key + version contract;
- per-template/per-channel safe variable schemas;
- permitted channel list;
- sensitivity classification;
- safe-preview policy;
- locale/fallback behavior only where product/root evidence supports it;
- approved action-route builders/validators;
- channel length/content constraints;
- prohibited-field checks;
- render result DTO;
- update Feature 01 intake to validate template key/version instead of arbitrary `name`.

#### Out of Scope

- mutable database `NotificationTemplate` lifecycle without architecture approval;
- WYSIWYG template editor;
- marketing/newsletter templates and campaign strategy;
- source legal/business decision logic;
- provider SDK calls;
- arbitrary caller-supplied HTML/provider payloads.

#### Module-Owned Data

No new persisted model is required by default. Existing `Notification.name`, `title`, `body`, `payload`, `payloadSensitivity`, `safePreviewOnly` are output/snapshot fields. `name` becomes validated vocabulary under the approved registry rather than caller-controlled free text.

#### Public Interfaces

- SH-042 `renderNotificationTemplate` — internal to Notification application/delivery path but canonical Notification capability;
- typed `NotificationTemplateKey`/version input contract exported to approved source callers;
- approved action-route builder/validator contract.

Source Modules provide safe variables, not final HTML, SMS text, push payload, or provider-specific JSON.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-042 `renderNotificationTemplate` | Notification | intake/delivery render | variable/channel/sensitivity policy | source-specific renderers | Cross-cutting capability | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | rendering failure diagnostics | safe template key/version/reason only | logging rendered sensitive payload | Cross-cutting capability | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | request path inherited from Feature 01 | semantic Notification identity | local dedupe helper | Platform primitive | Confirmed |
| SH-072 `hashCanonicalPayload` if root standards define/use it | Shared security/cryptography capability | optional integrity/version proof | Notification decides whether a hash is needed | local hash implementation | Platform primitive | Confirmed |

SH-072 `hashCanonicalPayload` exists as SH-072 (Confirmed). Its use here remains conditional on an approved integrity requirement; the reference does not invent a local hashing policy.

#### Domain Logic

Every template definition must specify, when applicable:

- stable key;
- explicit version;
- permitted channel(s);
- typed safe variable schema;
- output sensitivity;
- whether preview/body content is allowed;
- action-route builder;
- channel size/content constraints;
- prohibited source fields;
- locale/fallback only if implemented.

Fail closed for:

- unknown key/version;
- wrong variable schema;
- channel not permitted;
- prohibited sensitive field;
- invalid action route;
- unsafe rendered output.

Notification does not decide whether an FCRA/DMCA/security notice is legally required; the source owner supplies the approved semantic intent/template contract.

#### Authorization / Compliance

- template catalog administration, if any, is not a mutable production business surface in this feature;
- outward-safe rules prohibit private Message body, PHI, OTP/recovery token, financial/tax data, raw resume/identity documents, contract text, provider credentials;
- security/legal external alerts use minimal instruction and authenticated app route for details;
- action routes cannot become arbitrary external redirects.

#### Database / Transaction Behavior

- no schema migration by default;
- validation/rendering occurs before Notification write for source-supplied variables;
- persisted snapshot must be the safe rendered result or approved safe metadata, not the raw unsafe source object;
- do not persist unvalidated arbitrary JSON merely because `payload` accepts JSON.

#### Events / Jobs

None required.

#### Provider Integration

None. The renderer produces provider-neutral/channel-safe output only.

#### UI / Admin Surface

No end-user UI required beyond Feature 01. An internal read-only template catalog/harness may show:

- key/version;
- permitted channels;
- variable schema names;
- sensitivity;
- action-route type;
- sample **non-sensitive** fixture render.

#### Failure Behavior

- unknown key/version → reject;
- variable mismatch → reject before write;
- prohibited field → fail closed and record safe diagnostic reason;
- unsupported channel → skip/deny before provider call;
- renderer exception → safe `unavailable`/terminal validation result, no source-state mutation.

#### Tests

- schema fixtures for every implemented key/version/channel;
- injection of every prohibited sensitive field class;
- action-route allowlist/parameter validation;
- rendered snapshot tests with safe fixtures;
- caller cannot invent arbitrary Notification `name`;
- telemetry redaction for render failures;
- source contract tests for Messaging and one non-Messaging source.

#### Documentation Updates

- if PR-N05 is approved, update Module/Cluster architecture decision status;
- record template governance/versioning convention once binding;
- update progress tracker.

#### Acceptance Criteria

- every Notification created by the implemented slice uses a registered typed key/version;
- caller cannot pass arbitrary provider payload/HTML;
- prohibited sensitive fixtures never appear in safe channel output;
- action routes are constrained to approved authenticated app routes;
- no database template lifecycle was invented.

#### Exit Gate

- all implemented template/channel fixtures pass;
- arbitrary free-form `name`/payload injection is rejected;
- payload safety tests pass for prohibited classes;
- action-route tests pass;
- U-CL07-20/21 are either approved for production-enabled external channels or those channels remain explicitly disabled.

---

## Phase 2 — Reachability and External Delivery

### 03 Web Push Permission and Subscription Lifecycle

#### Objective

Implement secure, User-controlled browser/PWA push reachability: consent proof, observed browser permission, service-worker state, encrypted/hash credential handling, device listing, refresh/rotation, and revocation.

#### Observable Result

A User can review the required disclosure, request browser permission, create a supported push subscription only after grant, see a safe connected-device summary, refresh/rotate it, observe PWA readiness, and revoke it without ever receiving raw subscription secrets back from account APIs.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 07 — Web Push Permission and Subscription Lifecycle**.

#### Dependencies

- Feature 02;
- SH-008 `queryConsentProof` from Consent & Disclosure;
- SH-075 `encryptSensitiveValue`;
- SH-076 `normalizeAndHashIdentifier`;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- U-CL07-18 migration/uniqueness approval implementing binding PR-N04 before live production credential storage exits.

#### In Scope

- `recordNotificationPermissionState`;
- `recordServiceWorkerRegistrationState`;
- `upsertPushSubscription`;
- `refreshPushSubscription`;
- `revokePushSubscription`;
- `handlePushSubscriptionChange`;
- `recordPwaInstallReadiness`;
- `listNotificationSubscriptions`;
- append `NotificationSubscriptionEvent` evidence;
- own-device account settings UI;
- stale rotation protection;
- local failure/health metadata;
- approved credential migration/authority behavior.

#### Out of Scope

- actual Web Push send;
- production push provider selection;
- general notification preference center beyond confirmed reachability controls;
- native mobile device management;
- identity/session management;
- ConsentLog creation/version lifecycle;
- a second User-device identity table solely for push.

#### Module-Owned Data

- `NotificationSubscription`;
- `NotificationSubscriptionEvent`;
- `NotificationPermissionStatus`;
- `NotificationSubscriptionStatus`;
- `NotificationPlatform`;
- `NotificationSubscriptionProvider` for push only;
- `PwaInstallStatus`.

#### Public Interfaces

- `recordNotificationPermissionState`;
- `recordServiceWorkerRegistrationState`;
- `upsertPushSubscription`;
- `refreshPushSubscription`;
- `revokePushSubscription`;
- `handlePushSubscriptionChange`;
- `recordPwaInstallReadiness`;
- `listNotificationSubscriptions`.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | all account/device mutations/queries | own Subscription target | client user ID authority | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | list/revoke/manage | ownership/action facts | local device permissions engine | Cross-cutting capability | Confirmed |
| SH-008 `queryConsentProof` | Consent & Disclosure | before consent-dependent push onboarding | decide if proof is sufficient | local ConsentLog/pushConsent table | Platform consent capability | Confirmed |
| SH-075 `encryptSensitiveValue` | Shared security/cryptography capability | store recoverable endpoint/token/key | fields/rotation/retention | local crypto helper | Platform primitive | Confirmed |
| SH-076 `normalizeAndHashIdentifier` | Shared security/cryptography capability | match endpoint/token without plaintext | purpose/domain normalization | raw-token equality as sole identity | Platform primitive | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | create/refresh/revoke | subscription semantic key/replay | local idempotency | Platform primitive | Confirmed |
| SH-052 `withOptimisticConcurrency` or approved transaction strategy | Shared persistence infrastructure | refresh/rotation | newest valid rotation wins | in-memory mutex | Platform primitive | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | revoke/security-significant admin changes if policy requires | safe device reference only | NotificationAuditLog | Platform audit capability | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | client/provider error logging | no secrets/user-agent beyond allowed | raw endpoint/token logging | Cross-cutting capability | Confirmed |

#### Domain Logic

1. Consent proof and browser permission are separate checks/evidence.
2. Browser permission is observed from client/browser; server cannot invent `granted`.
3. Active Web Push subscription creation requires `permissionStatus=granted` through application path.
4. Unsupported/denied/dismissed permission returns safe state; no active subscription is created.
5. Endpoint/token matching uses approved hashes after PR-N04/U-CL07-18 migration.
6. Recoverable credentials use managed encryption only where necessary.
7. List APIs return device/provider/platform/health summaries, never endpoint/token/key material.
8. Refresh is stale-write safe; older `pushsubscriptionchange` input cannot restore superseded credentials.
9. Revocation is idempotent and prevents future local delivery routing.
10. PWA install state is capability metadata, not User/account status.
11. Dead-token cleanup is not triggered merely by a browser/UI failure; provider-authoritative evidence is required for automatic disable.

#### Authorization / Compliance

- User manages only own subscriptions;
- browser permission does not equal ConsentLog acceptance;
- no raw credential in UI/log/audit metadata;
- consent disclosure/version remains Consent-owned;
- provider/token is not authentication;
- iOS guidance is informative; do not use dark patterns or claim unsupported OS state changes.

#### Database / Transaction Behavior

- create/refresh/revoke command is idempotent;
- preserve append-only event evidence for relevant transitions;
- apply approved migration so plaintext and encrypted/hash credential fields are not competing truths;
- current plaintext unique constraints must be reconciled only through approved migration; do not silently remove constraints in feature code;
- enforce application/database consistency for active + granted permission if migration is approved;
- update credential set atomically with rotation metadata and current status.

#### Events / Jobs

- browser/service-worker callbacks only;
- no outbound push job yet;
- append local `NotificationSubscriptionEvent` for approved observed events;
- no Notification domain event catalog introduced.

#### Provider Integration

No outbound provider selected. Client/browser Web Push APIs may be integrated behind presentation/service-worker boundary. Production provider choice remains U-CL07-17.

#### UI / Admin Surface

Account Notification settings:

- current disclosure/permission state;
- browser/PWA readiness/guidance;
- safe connected-device summaries;
- last-seen/health metadata when safe;
- revoke control;
- unsupported/denied states;
- never display endpoint/token/key.

#### Failure Behavior

- denied/unsupported permission → record safe state, no active subscription;
- duplicate upsert → converge on existing semantic subscription;
- stale refresh → reject/no overwrite of newer credentials;
- browser unsubscribe failure → update only what Workin Ants can truthfully know and show recovery guidance; do not claim OS state changed;
- crypto unavailable → fail closed for live credential write;
- consent unavailable/invalid where required → no production subscription activation.

#### Tests

- unit permission/status transition matrix;
- integration create/refresh/revoke/list;
- cross-User RLS/authorization denial;
- crypto storage assertion: no authoritative plaintext after approved migration;
- API/log fixture secret scan;
- duplicate upsert idempotency;
- stale rotation/concurrency;
- service-worker callback contract;
- PWA state behavior;
- browser E2E where practical.

#### Documentation Updates

- preserve PR-N04 as approved target authority; mark U-CL07-18 resolved only after separate approval of exact migration/uniqueness details;
- document credential migration/backfill/rollback procedure;
- progress tracker.

#### Acceptance Criteria

- live Subscription path cannot create active Web Push without granted permission;
- Consent proof and permission evidence remain separate;
- API never returns credentials;
- production storage has one approved credential authority, not plaintext + encrypted duplicates;
- refresh/revoke are idempotent and stale-safe;
- User can manage only own reachability records.

#### Exit Gate

- credential migration ruling is approved for production storage;
- no live write maintains competing plaintext credential truth;
- active/granted invariant passes application/database tests;
- token rotation concurrency tests pass;
- account settings E2E passes;
- telemetry/client response secret scan passes.

---

### 04 Durable External Delivery Worker and Channel Ports

#### Objective

Add durable asynchronous delivery through provider-neutral email, SMS, and Web Push ports while enabling only channels/providers whose architecture and payload rules are approved.

#### Observable Result

A protected delivery inspector shows a safe Notification producing a durable `NotificationDelivery` with `queued → sending → sent/delivered/failed/skipped` behavior. At least one approved external channel can be exercised in a safe environment; unapproved providers are explicitly disabled/stubbed.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 08 — Durable External Delivery Worker and Channel Ports**.

#### Dependencies

- Features 01–03;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-038 `recordQueueTelemetry`;
- SH-037 `recordIntegrationFailure`;
- request context/metrics/exception/telemetry sanitization;
- SH-042 `renderNotificationTemplate`;
- U-CL07-20/21 closed for any channel enabled in production;
- email provider configuration if email enabled;
- SMS and Web Push remain disabled until U-CL07-16/17 respectively.

#### In Scope

- `NotificationDelivery` persistence;
- delivery planning for currently approved channel model only;
- shared queue job submission;
- `dispatchNotificationDelivery` worker;
- provider-neutral email/SMS/Web Push ports;
- selected/approved adapters only;
- disabled/stub adapter for unapproved channels;
- `recordProviderDeliveryResult`;
- Notification-owned SH-061 `translateProviderStatus` per adapter;
- provider retryability classification;
- dead-token signal `shouldDisableSubscription` where supported;
- protected delivery inspector;
- safe observability.

#### Out of Scope

- provider callbacks/reconciliation;
- full preserved retry-attempt history if U-CL07-13 is unresolved;
- Organization fan-out;
- marketing/bulk campaigns;
- source-specific provider business logic;
- inventing email/SMS provider enum values in the push-specific enum.

#### Module-Owned Data

- `NotificationDelivery`;
- `NotificationDeliveryStatus`;
- Notification/Subscription health fields involved in an approved result.

Until U-CL07-13 is closed, this feature may execute a **single logical attempt per Delivery** for test/proof purposes. Do not claim production retry-history completeness.

#### Public Interfaces

Internal Notification interfaces:

- `enqueueNotificationDeliveries`;
- `dispatchNotificationDelivery`;
- email port;
- SMS port;
- Web Push port;
- `recordProviderDeliveryResult`;
- SH-061 `translateProviderStatus` implementation per adapter.

No provider SDK/types become part of SH-041 `requestNotification`.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | after authoritative Delivery plan/write | job payload/completion semantics | `notificationQueue` framework | Platform primitive | Confirmed |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform infrastructure | technical provider failure | adapter classifies retryable/permanent | provider-local retry loops | Platform primitive | Confirmed |
| SH-038 `recordQueueTelemetry` | Observability / Ops / queue infrastructure | worker attempt/heartbeat/result | safe Delivery ref/status | custom queue ledger | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` | Observability / platform infrastructure | worker propagation | safe correlation | local request-context system | Platform primitive | Confirmed |
| SH-042 `renderNotificationTemplate` | Notification | immediately before send if required | channel-safe output | per-source renderers | Cross-cutting capability | Confirmed |
| SH-061 `translateProviderStatus` | Provider-owning adapter | provider response | explicit Notification mapping | global provider status mapper | Provider-adapter contract | Confirmed |
| SH-037 `recordIntegrationFailure` | Observability / Ops | meaningful degradation | Delivery remains domain truth | NotificationFailure substitute | Cross-cutting capability | Confirmed |
| SH-035 `captureException` / SH-036 `emitMetric` / SH-034 `sanitizeTelemetryMetadata` | SH-035: Observability / Ops<br>SH-036: Observability / Ops<br>SH-034: Observability / Ops and Audit payload policy | worker/provider boundary | safe bounded dimensions | raw provider payload logs | SH-035: Provider adapter<br>SH-036: Platform capability<br>SH-034: Cross-cutting capability | SH-035: Confirmed<br>SH-036: Confirmed<br>SH-034: Confirmed |

#### Domain Logic

1. Notification exists before external work is enqueued.
2. Delivery is created/planned only for currently eligible channel/destination.
3. Queue payload contains stable record references and minimal execution facts, not a second source-of-truth body copy unless root queue contract requires an approved snapshot.
4. Worker reloads authoritative Notification/Delivery and rechecks any time-sensitive owner-local conditions before side effect.
5. Render safe channel output through central template registry.
6. Invoke provider-neutral adapter.
7. Validate/normalize provider result.
8. Translate to canonical Delivery status/error/retryability.
9. Update only Notification-owned state.
10. Provider outage never rolls back source business transaction.
11. Unknown provider status never maps to success.
12. Invalid/dead push response may signal Subscription disable, but automatic transition requires approved adapter evidence.

#### Authorization / Compliance

- worker uses trusted system context;
- admin delivery inspector requires Role / Authority;
- sensitive Notification content is redacted in inspector;
- production channel only if payload catalog + provider/boundary approved;
- legal/security content remains source-approved;
- SMS/Web Push explicitly disabled until their rulings are approved.

#### Database / Transaction Behavior

- authoritative Notification/Delivery write commits before provider side effect;
- queue enqueue uses canonical reliable pattern/outbox if required by platform queue architecture;
- one worker claim per Delivery/attempt;
- result application is idempotent;
- current push-specific `NotificationSubscriptionProvider` must not be populated with false email/SMS provider identity;
- no retry-attempt schema migration until Feature 05 ruling.

#### Events / Jobs

- reliable delivery queue job;
- shared retry/backoff/DLQ;
- no provider callback job yet;
- dead-subscription follow-up may be queued only when local policy has authoritative evidence.

#### Provider Integration

- **Email:** use provider-neutral port; SES may be enabled where root configuration confirms current email transport.
- **SMS:** port/stub only until U-CL07-16.
- **Web Push:** port/stub only until U-CL07-17; requires Feature 03 Subscription truth.
- provider credentials stay server-side;
- adapter returns normalized result envelope.

#### UI / Admin Surface

Protected delivery inspector shows:

- Notification/source reference;
- channel;
- canonical Delivery status/timestamps;
- safe provider message reference;
- normalized safe failure category/code;
- retryability/disabled state;
- correlation ID;
- manual retry control only if later approved semantics support it.

No raw endpoint/token/payload/provider secret.

#### Failure Behavior

- queue unavailable → authoritative Notification remains; operational failure visible;
- transient provider failure → bounded retry according to current supported attempt model;
- permanent invalid destination → canonical failed/skipped + Subscription health signal if relevant;
- retry exhaustion → DLQ/ops evidence; never source state change;
- provider unavailable/unconfigured → explicit unavailable/skipped, not fake success;
- unmapped status → safe failure/manual review, no guess.

#### Tests

- queue durability and job idempotency;
- worker crash/replay safety;
- adapter contract tests;
- success/transient/permanent/unmapped fixtures;
- telemetry redaction;
- no provider SDK imports outside adapter boundary;
- no provider SDK imports in source Modules;
- nonproduction E2E for every enabled adapter;
- provider-disabled behavior for unapproved channels.

#### Documentation Updates

- document enabled/disabled providers in progress/context;
- update provider library notes if root process requires;
- architecture update before any provider selection becomes binding;
- progress tracker.

#### Acceptance Criteria

- safe Notification creates durable Delivery work/result;
- provider details remain behind ports;
- source Module contains no notification provider SDK call;
- queue/retry/DLQ/telemetry are canonical shared mechanisms;
- unapproved provider paths are disabled, not guessed;
- provider errors exposed to ops are normalized/redacted.

#### Exit Gate

- one approved external adapter succeeds in safe environment or, if no provider is yet approved, the provider-neutral worker/adapter contract is proven with disabled/test adapter while production external delivery remains gated;
- worker crash/replay and queue failure tests pass;
- source-provider import scan passes;
- production-enabled channels have approved U-CL07-20/21 payload rules and provider selection;
- no misleading email/SMS provider truth is written.

---

### 05 Delivery Attempt, Expiry, Interaction, and Aggregate Semantics

#### Objective

Close the ambiguous Notification/Delivery lifecycle model before broad production multi-channel/retry behavior is enabled.

#### Observable Result

After required architecture rulings, Delivery attempt history is preserved, expiry prevents late send, read/dismiss and interaction evidence are consistent, provider vocabulary is truthful, and Notification aggregate status is deterministic under all tested combinations.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 09 — Delivery Attempt, Expiry, Interaction, and Aggregate Semantics**.

#### Dependencies

- Feature 04;
- approved resolutions for U-CL07-10, U-CL07-11, U-CL07-12, U-CL07-13, U-CL07-15, U-CL07-19;
- PR-N02 and PR-N03 only if explicitly approved;
- migration/backfill/rollback discipline.

This feature is **blocked at the decision boundary** until those implemented semantics are approved.

#### In Scope

Only approved changes, potentially including:

- recipient/cardinality/channel constraint needed by final model;
- Delivery attempt number/correlation/idempotency fields;
- truthful provider vocabulary for email/SMS;
- preserved attempt history;
- `dismissedAt` and/or expiry representation;
- canonical interaction record/fields;
- aggregate reducer inputs/policy;
- expiry worker;
- retry scheduler behavior;
- manual retry semantics/audit;
- dead-subscription transition behavior;
- delivery-state query/inspector timeline.

#### Out of Scope

- speculative fields not required by approved rulings;
- provider callback implementation (Feature 10);
- Organization routing;
- source workflow completion analytics;
- behavior-tracking product scope beyond approved Notification interaction evidence.

#### Module-Owned Data

- `Notification`;
- `NotificationDelivery`;
- `NotificationSubscriptionEvent` only as approved interaction model requires;
- related enums/approved new provider/attempt schema.

#### Public Interfaces

Finalize as approved:

- delivery-state query;
- `recordNotificationInteraction`;
- retry command/admin control if permitted;
- expiry owner command/worker;
- `markNotificationRead` / `dismissNotification` semantics.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | retry/manual interaction/read/dismiss | semantic effect identity | local dedupe | Platform primitive | Confirmed |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | retry/expiry work | job completion status | local scheduler/queue | Platform primitive | Confirmed |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform infrastructure | transient provider retries | retryability/max outcome semantics | hand-coded adapter loops | Platform primitive | Confirmed |
| SH-055 `runDeadlineExpiration` or root scheduler equivalent | Shared scheduler/queue infrastructure | find expired items and invoke owner command | Notification expiry transition | generic scheduler owning statuses | Cross-cutting capability | Confirmed |
| SH-053 `transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy | state transition | Notification graph | generic lifecycle policy table | Shared mechanism; separate truth | Confirmed |
| SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency` | SH-051: Shared persistence infrastructure<br>SH-052: Shared persistence infrastructure | conflicting Delivery/Notification updates | lock/version key and conflict | in-memory lock | SH-051: Platform primitive<br>SH-052: Platform primitive | SH-051: Confirmed<br>SH-052: Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | manual retry/admin intervention | which admin action needs proof | local audit table | Platform audit capability | Confirmed |

#### Domain Logic

Binding behavior must be copied from the approved rulings, not inferred here. At minimum the implementation must guarantee:

- retry never creates a duplicate Notification intent;
- retry evidence is not silently overwritten if one-row-per-attempt is approved;
- expiry check occurs before provider side effect and prevents late send after cutoff;
- aggregate Notification status is deterministic and separate from queue operational status;
- Delivery provider identity is truthful for every enabled channel;
- click/open/close/read/dismiss are distinct according to approved model;
- interaction never completes source workflow;
- manual retry reuses the same payload safety/recipient eligibility rules and is audited if required.

#### Authorization / Compliance

- admin retry cannot bypass payload safety, consent/permission/reachability, or recipient rules;
- expired security/legal notices follow source-owner legal/business policy; Notification does not determine deadline consequence;
- interaction collection is minimized and limited to approved product evidence, not covert behavioral tracking.

#### Database / Transaction Behavior

- apply only approved migrations;
- backfill existing rows deterministically;
- provide rollback/recovery for destructive/provider-vocabulary changes;
- Delivery/aggregate transition uses one transaction with concurrency protection;
- retry/interaction idempotency keys have DB-backed uniqueness/claim semantics through canonical primitive;
- no in-memory locking.

#### Events / Jobs

- expiry scan/scheduler;
- retry jobs;
- dead-subscription owner command;
- no provider callback processing yet.

#### Provider Integration

No new provider selection. Existing adapters consume the approved attempt/provider model.

#### UI / Admin Surface

Update delivery inspector to show:

- attempt timeline;
- canonical provider identity;
- aggregate result/reason;
- expiry/skipped evidence;
- safe interactions;
- manual retry result if supported.

Update Notification center to show consistent read/dismiss behavior only.

#### Failure Behavior

- max attempts → terminal Delivery failure + DLQ/ops visibility;
- mixed attempts → deterministic aggregate result;
- expired item → no late provider side effect;
- duplicate interaction → one evidence effect;
- stale transition → conflict/current-state result;
- migration ambiguity → fail deployment/require explicit remediation, not silent coercion.

#### Tests

- exhaustive state transition matrix;
- retry/attempt history;
- expiry vs queued-worker race;
- mixed attempt aggregate table;
- provider vocabulary fixtures per enabled channel;
- read/dismiss/click/open/close matrix;
- concurrency/idempotency;
- migration/backfill/rollback fixtures;
- admin retry authorization/audit.

#### Documentation Updates

Mandatory:

- update CL-07 architecture with every approved U-CL07 ruling implemented;
- update Module architecture lifecycle/data model;
- update this plan if feature semantics change;
- record migration runbook and progress.

#### Acceptance Criteria

- no implemented semantic depends on an unresolved decision;
- retry evidence is preserved as approved;
- expiry is enforceable and testable;
- provider identity is truthful;
- aggregate status is deterministic;
- interaction proof cannot be read as workflow completion.

#### Exit Gate

- all U-CL07-10/11/12/13/15/19 decisions used by production behavior are Architecture Rulings;
- transition/aggregate/expiry/retry/concurrency suites pass;
- migration/backfill rehearsal passes;
- retry history cannot be lost by repeated overwrite under approved model;
- provider vocabulary is correct for every enabled channel;
- interaction UI/copy/tests preserve the “not workflow completion” boundary.

---

## Phase 3 — Routing and Source-Module Contracts

### 06 Organization Recipient Routing and Hiring Alerts

#### Objective

Route Organization-scoped notification intent using Organization Hiring-owned membership/settings facts without moving Organization truth into Notification.

#### Observable Result

A hiring workflow can request an approved alert; Organization Hiring resolves eligible User recipients/settings; Notification deduplicates recipients, creates its own alert/delivery records, and delivers only to owner-resolved Users. Future membership/settings changes affect future routing without a copied Notification membership table.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 10 — Organization Recipient Routing and Hiring Alerts**.

#### Dependencies

- Features 01–05 as relevant to enabled channel behavior;
- Organization Hiring owner public recipient-facts query;
- Role / Authority;
- approved U-CL07-09 recipient/cardinality/fan-out model;
- approved schema constraints if required.

#### In Scope

- typed Organization/group recipient descriptor in SH-041 `requestNotification`;
- integration with owner query `resolveOrganizationNotificationRecipientFacts` supporting SH-043 `resolveNotificationRecipients`;
- Notification recipient dedupe/fan-out/channel routing;
- owner-settings consumption without local mutation;
- hiring alert contract fixture/E2E;
- cross-organization authorization tests;
- safe admin trace of routing count/result.

#### Out of Scope

- OrganizationMember/OrganizationRole lifecycle;
- OrganizationNotificationSetting update UI/commands;
- candidate resume access;
- job/application/interview lifecycle changes;
- FCRA/job compliance decisions;
- stale copied member cache as source truth.

#### Module-Owned Data

Notification models only, according to the approved target/fan-out model. `OrganizationNotificationSetting` remains externally owned.

#### Public Interfaces

- SH-041 `requestNotification` with approved Organization/group recipient descriptor;
- shared SH-043 `resolveNotificationRecipients` contract;
- consumed Organization-owned `resolveOrganizationNotificationRecipientFacts`.

Organization Hiring exposes `resolveOrganizationNotificationRecipientFacts` as its owner-specific public query supporting SH-043 `resolveNotificationRecipients`. It accepts an Organization-scoped notification context, evaluates Organization-owned membership and `OrganizationNotificationSetting` facts, and returns eligible concrete User IDs plus only safe routing facts. An empty eligible-recipient set is valid; unavailable and unauthorized results are distinct from that empty result. Notification consumes the result, deduplicates recipients, applies its own reachability/channel eligibility, and performs fan-out. Notification must not reconstruct Organization role/settings policy from raw tables.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-043 `resolveNotificationRecipients` | Source context owner plus Notification | intake routing | dedupe/fan-out/channel eligibility | local Organization role resolver | Shared contract; separate policy | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Each source Module | owner recipient query | minimum facts only | direct OrganizationMember repository read | Shared contract; separate implementations | Proposed ruling |
| SH-041 `requestNotification` | Notification | hiring source intake | local Notification routing/payload | source writing Delivery rows | Platform notification capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | any interactive org/admin settings/inspection path | Notification target/action facts | local org RBAC | Cross-cutting capability | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | intake/fan-out effect | recipient semantic identity | local dedupe | Platform primitive | Confirmed |

#### Domain Logic

1. Source Hiring Module decides event timing/semantic alert need.
2. Organization Hiring resolves member roles/settings to concrete eligible User IDs.
3. Notification does not interpret `OrganizationRole` from raw rows.
4. Notification deduplicates resolved User IDs.
5. Notification applies its own channel reachability/payload policy.
6. Membership/settings changes affect future calls through owner query.
7. No eligible recipient produces explicit safe skipped/no-recipient result, not an orphan Notification.
8. One recipient/provider failure does not rewrite another recipient's Notification/Delivery truth under approved fan-out model.
9. Resume/application private fields never enter outward payload.

#### Authorization / Compliance

- settings mutation remains Organization-authorized elsewhere;
- Notification only uses owner-returned eligible recipients;
- cross-organization requests are denied;
- hiring/FCRA semantics remain source-owned;
- external payload catalog applies.

#### Database / Transaction Behavior

- implement approved exactly-one/recipient fan-out constraints from U-CL07-09;
- fan-out must be idempotent under duplicate source request;
- do not persist OrganizationMember snapshot unless an explicit architecture ruling requires a historical recipient snapshot; if no snapshot is approved, keep only Notification-owned resolved target facts necessary for its truth.

#### Events / Jobs

External delivery reuses Feature 04/05 workers. No new source event is invented; use direct command or already-approved source event contract.

#### Provider Integration

No new provider integration; routing feeds existing channel ports.

#### UI / Admin Surface

- Organization notification settings stay in Organization Hiring UI;
- User Notification center remains Notification UI;
- optional protected routing trace: source organization reference, recipient count, channel plan, safe reason codes — no unnecessary membership details.

#### Failure Behavior

- owner query unavailable → safe unavailable/no direct DB fallback;
- no eligible recipients → explicit skipped/no-recipient;
- duplicate recipients → one resolved effect per approved recipient/channel model;
- provider failure for one User → other User delivery truth remains intact;
- stale/cached membership must not override fresh owner facts outside an approved snapshot policy.

#### Tests

- Organization recipient contract;
- role/settings permutations in owner fixture;
- duplicate member dedupe;
- no Notification write to OrganizationMember/Setting;
- hiring E2E with safe payload;
- cross-organization denial;
- no resume/private application fields in outward fixtures;
- idempotent fan-out.

#### Documentation Updates

- U-CL07-09 must be updated to Architecture Ruling before feature exits;
- Module architecture target/cardinality section updated to approved model;
- progress tracker.

#### Acceptance Criteria

- Organization routing has a documented/approved cardinality model;
- Notification consumes owner query only;
- Notification never writes Organization membership/settings;
- hiring E2E reaches only eligible owner-resolved Users;
- sensitive hiring fields absent from payloads.

#### Exit Gate

- U-CL07-09 closed and schema/contract tests pass;
- no cross-domain repository import exists;
- no OrganizationRole interpretation exists in Notification domain policy;
- routing/fan-out idempotency and cross-org tests pass;
- hiring payload safety E2E passes.

---

### 07 Source-Module Notification Contract Pack

#### Objective

Standardize representative typed Notification intents across Workin Ants so source Modules reuse one alert capability without importing their lifecycles into Notification.

#### Observable Result

Representative marketplace, hiring, scheduling, security, moderation/hold, subscription/entitlement, and incentive sources can request consistent Notification behavior through typed safe contracts. Coding agents have no reason to invent free-form Notification names or source-specific provider clients.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 11 — Source-Module Notification Contract Pack**.

#### Dependencies

- Features 02–06 as applicable;
- source Module public contracts/events as available;
- approved template catalog/safe payload rules for production external channels;
- Generic SMS provider selection under U-CL07-16 before production generic SMS alerts; Identity verification-provider transport is outside Notification.

#### In Scope

Typed request families for representative sources, without source lifecycle code:

- Messaging — new message;
- Order/Gig — paid/status/action alert;
- Booking — confirmed/rescheduled/cancelled alert;
- Hiring — application/interview alert;
- Track Subscription & Entitlement — plan/subscription/entitlement lifecycle alert;
- Hold/Moderation — user/admin notice intent;
- Prize/Reward — result/fulfillment alert;
- Identity — security/recovery delivery intent only within approved boundary.

Also:

- source-specific safe variable DTOs that map into Notification templates;
- source reference/action-route contracts;
- direct command idempotency pattern;
- event consumer dedupe only for already-approved source events;
- isolation/import checks.

#### Out of Scope

- source business UI/state machine;
- source database tables/repositories;
- creation of a universal event catalog;
- bulk “notify all users” semantics;
- marketing campaigns;
- legal/security policy authoring;
- raw source object serialization into Notification.

#### Module-Owned Data

No new source lifecycle model. Notification stores only its own source reference and safe snapshot/output fields.

#### Public Interfaces

- SH-041 `requestNotification` remains the one intake;
- typed template/source-intent contracts layered on the same command;
- event consumer adapters only where source event exists and is approved.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-041 `requestNotification` | Notification | every source family | Notification routing/payload | source provider dispatch | Platform notification capability | Confirmed |
| SH-042 `renderNotificationTemplate` | Notification | source intent render | safe variables/channel policy | source email/SMS HTML builders | Cross-cutting capability | Confirmed |
| SH-043 `resolveNotificationRecipients` | Source context owner plus Notification | group/relationship targets | dedupe/fan-out | source relationship copy | Shared contract; separate policy | Confirmed |
| SH-046 `publishDomainEvent` | Platform event/outbox infrastructure | source only if event contract exists | source event meaning | CL-07 invented event name | Platform primitive | Confirmed |
| SH-045 `deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox | Notification event consumer | handler/effect identity | custom event dedupe | Platform primitive | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | direct command intake | source semantic key | local duplicate service | Platform primitive | Confirmed |

#### Domain Logic

- source decides whether/when alert is required;
- source supplies safe variables and approved action context;
- Notification validates key/version/sensitivity/channel;
- direct requests use semantic idempotency;
- event requests use event inbox dedupe plus Notification semantic idempotency where appropriate;
- no delivery result is used to infer source result;
- Notification failure is independently observable from source transaction;
- no source Module gets provider details from Notification contract.

#### Authorization / Compliance

- source/server call must be trusted/authorized under its own domain action before requesting an alert;
- Notification validates its own request boundary, not the source business authorization rule;
- FCRA/DMCA/security content comes from approved owner contract;
- prohibited sensitive raw data is rejected;
- channel eligibility still respects Consent/permission/reachability/local safety.

#### Database / Transaction Behavior

- no new source tables;
- source reference fields are references only;
- duplicate direct/event requests converge on one semantic Notification effect under approved fan-out model;
- source transaction and Notification write are not one cross-domain transaction; post-commit request/event is preferred.

#### Events / Jobs

- versioned event consumer only for source-owned published event;
- canonical outbox/inbox used where event-driven;
- do not invent `OrderPaidNotificationEvent` or similar if source has not approved it;
- external delivery continues through existing jobs.

#### Provider Integration

No source-specific provider adapter. All source families converge on existing Notification provider ports.

#### UI / Admin Surface

No new general UI. Add contract catalog/trace fixtures showing:

- source family;
- template key/version;
- safe variable schema;
- source reference;
- recipient descriptor;
- correlation/idempotency result.

#### Failure Behavior

- unknown source/template contract → reject;
- source event replay → no duplicate Notification effect;
- Notification unavailable → source transaction remains committed; source/canonical event may retry;
- one channel/provider failure → source state unchanged;
- missing owner facts → safe no-recipient/unavailable, never direct DB fallback.

#### Tests

- contract tests for each representative source family implemented;
- marketplace + hiring E2E minimum;
- event dedupe tests where event integration exists;
- source repository isolation/import rules;
- provider SDK import scan in sources;
- prohibited payload fixtures per source family;
- source-state isolation under Notification/provider failure.

#### Documentation Updates

- document each approved source intent/template in contract catalog;
- update dependency public-interface references as source Modules mature;
- do not add source event names to architecture until their owners approve them;
- progress tracker.

#### Acceptance Criteria

- marketplace and hiring sources use the same canonical SH-041 `requestNotification` command shape;
- source/template vocabulary is typed/versioned;
- no source provider dispatch exists;
- duplicates converge;
- source state is independent of delivery result;
- sensitive source data does not leak.

#### Exit Gate

- at least one marketplace and one hiring real/fixture source pass contract/E2E tests;
- provider SDK/import scan shows Notification-only ownership;
- duplicate direct/event requests produce one semantic effect;
- source-state isolation tests pass;
- all implemented source templates have payload-safety coverage.

---

## Phase 4 — Privacy and Cross-Cluster Proof

### 08 Notification Privacy Enumeration and Execution

#### Objective

Register Notification as a proper Privacy data owner that can enumerate/export/erase/anonymize/revoke/retain its own data under Privacy-owned orchestration.

#### Observable Result

A Privacy test/admin workflow can enumerate Notification subject data, issue an approved target disposition, observe an explicit owner execution result, and verify that Notification never creates or completes the overall PrivacyRequest.

#### Cluster Build-Plan Link

Implements the **Notification slice of CL-07 Feature 13 — Privacy Enumeration and Execution**. CL-07 Feature 12 is Messaging-focused; Notification's only participation there is delivery of source-requested notices through Feature 07 contracts, so this Module plan does not duplicate Feature 12.

#### Dependencies

- Features 01–05 for relevant data models;
- canonical Privacy handler protocol;
- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-095 `executePrivacyInstruction`;
- root Privacy-defined export format;
- retention rules approved before destructive production action for each affected data class;
- provider deletion/revocation contract where applicable.

#### In Scope

Notification privacy inventory/handler for:

- Notification recipient/source/content/payload/action metadata;
- NotificationDelivery provider IDs, safe failure metadata, interactions where erasable;
- NotificationSubscription reachability/device metadata and credentials;
- NotificationSubscriptionEvent personal/device metadata;
- provider-side revocation/deletion where supported and instructed;
- export serializer excluding secrets;
- idempotent target result mapping;
- safe audit/operational evidence as governed.

#### Out of Scope

- PrivacyRequest/DataErasureJob/DataRetentionExemption schema/lifecycle;
- legal retention-period definition;
- erasing source Module records;
- generic privacy UI;
- audit-log destruction;
- Notification deciding a retention exemption.

#### Module-Owned Data

- `Notification`;
- `NotificationDelivery`;
- `NotificationSubscription`;
- `NotificationSubscriptionEvent`;
- provider resources owned through Notification adapter.

#### Public Interfaces

- Notification SH-096 `enumerateSubjectData`;
- Notification SH-097 `evaluateRetentionRequirement` — owner-side retention query;
- Notification SH-095 `executePrivacyInstruction`;
- Notification export serializer(s) in Privacy-defined format.

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-096 `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | privacy inventory | Notification target types/dispositions | Privacy global DB crawler | Cross-cutting protocol | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | planning | factual Notification retention context | local legal exemption logic | Cross-cutting protocol | Confirmed |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | target fulfillment | exact field/provider mutation | local PrivacyRequest workflow | Cross-cutting protocol | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | destructive/retryable target execution | target+disposition semantic key | local privacy dedupe | Platform primitive | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | fulfillment proof if policy says | minimized result only | Notification privacy audit table | Platform audit capability | Confirmed |
| SH-070 `deleteProviderResource` | Provider-owning Module | provider-side cleanup | Notification resource mapping | custom global erasure worker | Provider-adapter contract | Confirmed |

SH-098 `anonymizePersonalFields` and SH-070 `deleteProviderResource` are Confirmed in the registry. Use them only where the approved Privacy disposition/provider contract calls for them.

#### Domain Logic

1. Enumerate stable owner targets with sensitivity, supported dispositions, provider references, retention candidates, export capability.
2. Return facts to Privacy, not legal conclusions.
3. Execute exactly the instructed disposition.
4. Preserve required relationship/evidence according to Privacy's retention instruction.
5. Remove/revoke provider Notification resources only through Notification provider boundary.
6. Existing/absent target replays are idempotent.
7. Partial failure returns explicit retryable/terminal result; Notification never marks overall PrivacyRequest complete.
8. Export excludes encrypted credentials/raw tokens/keys and obeys sensitivity/retention rules.

#### Authorization / Compliance

- destructive handler callable only by Privacy-authorized orchestration identity/context;
- interactive export/admin access uses Role + AccessAuditLog policy as applicable;
- retention exemptions remain Privacy-owned;
- no statutory retention assumption in Notification.

#### Database / Transaction Behavior

- target-bound transaction mutates only Notification-owned records;
- provider side effect and local record mutation follow Privacy protocol's retry/order semantics;
- no direct Privacy repository write into Notification;
- if provider revocation succeeds but local transaction fails, replay/reconciliation must converge safely;
- destructive field behavior must be documented before production enablement.

#### Events / Jobs

- Privacy's orchestration/queue invokes the handler;
- Notification does not schedule global erasure work;
- provider deletion/revocation may use existing adapter/job if Privacy protocol allows;
- owner result returns to Privacy.

#### Provider Integration

Only provider resources that Notification owns may be deleted/revoked. Failure is normalized and returned to Privacy; raw provider data not persisted in result.

#### UI / Admin Surface

No separate Notification privacy UI. Use Privacy-owned admin/request surface with owner target/execution trace.

#### Failure Behavior

- `retained` instruction → no destructive change; explicit retained result;
- unsupported disposition → explicit skipped/terminal according to protocol;
- provider retryable failure → return retryable result;
- target already absent → idempotent completed/absent result;
- partial owner failure → no overall Privacy completion;
- missing retention ruling → destructive production path remains disabled.

#### Tests

- enumeration coverage for all four Notification models;
- export excludes secrets;
- idempotent erase/anonymize/revoke/retain fixtures;
- provider revocation/deletion stub/retry;
- no Privacy direct repository mutation;
- no local PrivacyRequest/Exemption table;
- access audit where required;
- partial failure/retry behavior.

#### Documentation Updates

- record approved field-level disposition/retention rules in Module architecture;
- update Privacy owner-handler registry if one exists;
- progress tracker;
- architecture first if a new retention decision changes binding behavior.

#### Acceptance Criteria

- Privacy can enumerate Notification targets through public handler;
- handler mutates only Notification truth/provider resources;
- result categories are explicit and idempotent;
- export contains no credentials/secrets;
- Notification cannot complete PrivacyRequest or create exemption;
- destructive production actions only enabled for approved retention rules.

#### Exit Gate

- Privacy contract/integration tests pass;
- all representative Notification target types enumerate correctly;
- idempotent disposition tests pass;
- provider cleanup failure/retry path passes;
- no local Privacy orchestration implementation exists;
- retention blockers are resolved or corresponding destructive paths stay disabled.

---

### 09 Cross-Cluster Notification Contract Proof

#### Objective

Prove Notification functions as a reusable rail across marketplace, hiring, scheduling, and entitlement workflows through public contracts/events only, without importing neighboring truth.

#### Observable Result

Representative Workin Ants workflows create safe alerts through Notification while their source records remain independently authoritative:

1. Messaging/Gig/Order path produces safe Notification;
2. hiring path produces candidate/organization alerts;
3. Booking/scheduling event produces Notification without leaking exact protected location;
4. Track lifecycle event produces alert without local entitlement interpretation.

#### Cluster Build-Plan Link

Implements the **Notification slice of CL-07 Feature 14 — Marketplace, Hiring, Scheduling, and Entitlement Contract Proof**.

#### Dependencies

- Features 01–08;
- neighboring Module public interfaces/events available or owner-contract fixtures;
- Organization routing if Organization target is used;
- production provider/payload rulings for any external-channel E2E.

#### In Scope

Contract/integration proof with at least:

- Gig / Demand;
- Transaction / Order;
- Messaging;
- Candidate Application & Resume Privacy;
- Job Interview / Organization Hiring;
- Booking & Calendar notification request;
- Track Subscription & Entitlement notification request.

Also source/provider import scans and failure-isolation tests.

#### Out of Scope

- implementing missing source Module business features;
- Booking/Dispute thread model decisions;
- source repository access;
- public Search;
- entitlement evaluation inside Notification;
- exact-location data copy;
- source transaction orchestration by Notification.

#### Module-Owned Data

Only Notification-owned records created through public intake. Source foreign keys/references remain references.

#### Public Interfaces

- SH-041 `requestNotification`;
- SH-043 `resolveNotificationRecipients` as needed;
- approved source event consumers, if any;
- existing Notification queries for proof.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Each source Module | source/recipient validation | minimum safe facts | cross-domain repository | Shared contract; separate implementations | Proposed ruling |
| SH-002 `authorizeResourceAction` | Role / Authority | user/admin interactions | Notification target facts | duplicated source permissions | Cross-cutting capability | Confirmed |
| SH-041 `requestNotification` | Notification | every workflow alert | local routing/payload | direct provider calls | Platform notification capability | Confirmed |
| SH-043 `resolveNotificationRecipients` | Source context owner plus Notification | group targets | dedupe/fan-out | copied membership/party data | Shared contract; separate policy | Confirmed |
| SH-046 `publishDomainEvent` / SH-045 `deduplicateDomainEvent` | SH-046: Platform event/outbox infrastructure<br>SH-045: Platform event infrastructure; consumer owns inbox | only approved event bridges | event meaning stays owner | CL-07 invented event catalog | SH-046: Platform primitive<br>SH-045: Platform primitive | SH-046: Confirmed<br>SH-045: Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | command bridge | semantic effect | local dedupe | Platform primitive | Confirmed |

#### Domain Logic

- source owner determines event timing and recipient semantics;
- Notification accepts only typed safe intent;
- Messaging → Notification is post-commit and contains no private Message body;
- Notification does not synchronously read private Message to render an alert;
- hiring resume details excluded;
- Booking exact location/other sensitive context remains owner-protected;
- Track event is trigger only, not entitlement input;
- communication failure and source failure are separately observable;
- missing owner facts returns safe unavailable/no-recipient, not repository fallback.

#### Authorization / Compliance

- source authorization remains source-owned;
- Notification user/admin actions remain Identity/Role authorized;
- sensitive payload constraints apply across all bridge fixtures;
- no source role, entitlement, compliance, or location policy reconstructed.

#### Database / Transaction Behavior

- no source table writes from Notification;
- source transaction commits independently;
- Notification idempotency protects repeated bridge requests/events;
- event integrations use outbox/inbox only if source already defines them.

#### Events / Jobs

Representative events may be exercised only if already approved by source. External delivery uses existing workers. Do not create a cross-platform Notification event catalog to make tests convenient.

#### Provider Integration

Existing Notification adapters only. Source Modules have zero generic Notification provider SDK imports/calls for alerts; Identity verification-provider protocol is separate.

#### UI / Admin Surface

Use existing real source workflow screens when available plus protected correlation trace. Do not build a duplicate test UI for each source if contract/E2E proof can use the source surface.

#### Failure Behavior

- Notification/provider down → source truth stays committed;
- source request/event replay → one semantic Notification effect;
- missing recipient facts → safe no-recipient/unavailable;
- source removed/changed after alert → Notification keeps only its safe historical source reference/snapshot and does not reconstruct current source truth.

#### Tests

- contract/integration per bridge;
- marketplace E2E;
- hiring E2E;
- Booking notification flow;
- Track lifecycle alert flow;
- Messaging safe post-commit alert flow;
- source-provider import scan;
- cross-domain repository import scan;
- source-state isolation under delivery failure;
- payload safety per source.

#### Documentation Updates

- update source-interface references as real contracts replace fixtures;
- record integration proof in progress tracker;
- no ownership change unless architecture updated first.

#### Acceptance Criteria

- marketplace and hiring critical journeys use Notification without ownership theft;
- at least one scheduling and one entitlement source prove Notification-only rail behavior;
- no source directly writes Notification tables or calls provider SDKs;
- no Notification service imports source repository;
- provider failure leaves source truth intact.

#### Exit Gate

- all required bridge contract tests use owner interfaces/events only;
- source-provider and cross-domain repository import scans pass;
- marketplace/hiring/scheduling/entitlement test matrix passes;
- source-state isolation passes;
- payload safety passes.

---

## Phase 5 — Provider Completion and Production Hardening

### 10 Provider Callbacks, Deduplication, and Reconciliation

#### Objective

Complete the external delivery lifecycle for enabled providers that expose asynchronous receipts/state changes, with authenticated callbacks, replay-safe provider-event truth, normalized status application, and bounded reconciliation.

#### Observable Result

A protected admin/provider test can submit a valid provider callback that updates the correct Delivery exactly once, replay the callback with no duplicate effect, reject invalid signatures, display an unknown status as safe operational failure, and run a reconciliation dry-run/report for a supported provider.

#### Cluster Build-Plan Link

Supports **CL-07 Feature 15 — Provider Callbacks, Deduplication, and Reconciliation**.

#### Dependencies

- Features 04–05;
- selected enabled provider(s) with callback/query capabilities;
- approved U-CL07-14 Notification processed-provider-event schema;
- truthful provider vocabulary U-CL07-15 for enabled channels;
- SH-059 `verifyProviderWebhookSignature`;
- SH-060 `deduplicateProviderEvent`;
- SH-066 `validateStructuredProviderOutput`;
- SH-062 `reconcileProviderState`;
- canonical queue/retry/observability.

#### In Scope

- Notification-owned processed-provider-event record **only after approved schema**;
- provider webhook route/handler;
- raw-body signature/timestamp verification;
- structured event validation;
- atomic provider-event dedupe;
- provider ID → Delivery/Subscription mapping;
- adapter callback parser/status mapper;
- idempotent local state transition;
- callback safe evidence/result;
- reconciliation dry-run/report;
- only approved automatic owner-local repair;
- provider callback/reconciliation inspector.

#### Out of Scope

- global provider-event table;
- reuse of Stripe/Calendar/Video processed-event truth;
- reconciliation changing source Order/Job/Booking/etc.;
- raw webhook payload retention without approved need;
- provider callback as a source-domain event;
- automatic repair for unsafe/unmapped discrepancies.

#### Module-Owned Data

- `NotificationDelivery`;
- `NotificationSubscription` as appropriate;
- approved new Notification processed-provider-event record;
- no other Module's processed-event record.

Minimum approved processed-event fields should follow canonical dedupe pattern:

- provider/event identity uniqueness;
- payload hash/version where justified;
- processing result/status;
- safe Notification/Delivery/Subscription correlation references;
- received/processed timestamps;
- safe failure category.

Exact schema comes from U-CL07-14 ruling, not this plan.

#### Public Interfaces

- provider webhook Route Handler → Notification callback application service;
- adapter callback parser/status mapper;
- reconciliation command/query for authorized admin/system use.

#### Shared Operations Used

| Operation | Canonical owner | Invocation | Local policy | Prohibited duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SH-059 `verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm | raw webhook entry | provider algorithm/secret/tolerance | bespoke verifier logic outside adapter shell | Provider-adapter contract | Confirmed |
| SH-060 `deduplicateProviderEvent` | Provider-owning Module using shared primitive | after signature verification | Notification event identity/result | reuse Stripe/Calendar/Video ledger | Shared mechanism; separate truth | Confirmed |
| SH-066 `validateStructuredProviderOutput` | Shared validation primitive; consuming Module owns schema | after raw auth | adapter event schema/semantic checks | trusting provider JSON | Cross-cutting capability | Confirmed |
| SH-061 `translateProviderStatus` | Provider-owning adapter | callback mapping | Delivery/Subscription status mapping/version | global provider mapper | Provider-adapter contract | Confirmed |
| SH-062 `reconcileProviderState` | Each provider-owning Module using shared worker framework | schedule/admin | safe discrepancy repair rules | global reconciler | Shared mechanism; separate policy | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | callback state application/repair | local aggregate command identity | local callback dedupe helper | Platform primitive | Confirmed |
| SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` | SH-047: Shared queue infrastructure<br>SH-048: Shared queue/platform infrastructure | follow-up/reconciliation | local job meaning/retryability | custom callback queue | SH-047: Platform primitive<br>SH-048: Platform primitive | SH-047: Confirmed<br>SH-048: Confirmed |
| SH-037 `recordIntegrationFailure` | Observability / Ops | callback/reconcile degradation | safe refs | local failure table | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` / SH-034 `sanitizeTelemetryMetadata` | SH-032: Observability / platform infrastructure<br>SH-034: Observability / Ops and Audit payload policy | callback/worker trace | safe metadata only | raw webhook logging | SH-032: Platform primitive<br>SH-034: Cross-cutting capability | SH-032: Confirmed<br>SH-034: Confirmed |

#### Domain Logic

Callback path:

```text
raw request
→ verify signature/timestamp
→ validate envelope
→ atomically claim provider event
→ map provider object to Notification Delivery/Subscription
→ translate provider status
→ idempotently apply allowed local transition
→ record safe ops/audit evidence
→ mark processed-provider-event result
```

Reconciliation:

- compare provider state to Notification truth only;
- support dry-run report;
- repair only explicitly safe discrepancies;
- use idempotent owner-local repair command;
- unknown/unsafe discrepancy becomes operational incident/manual review;
- never infer or alter source workflow state.

#### Authorization / Compliance

- webhook authenticates provider, not User;
- admin reconciliation requires Role / Authority;
- raw payload minimized/not retained by default;
- no sensitive payload in logs/inspector;
- legal/security source content remains protected;
- provider event ID/hash not used as business source truth.

#### Database / Transaction Behavior

- unique provider+event identity claim;
- dedupe claim and local state application follow approved atomic pattern;
- duplicate callback acknowledges/ignores without repeated transition;
- callback vs synchronous provider response race converges on legal state;
- reconciliation repair idempotent;
- processed-event record is append/evidence truth and not a global event ledger.

#### Events / Jobs

- provider webhook input;
- reconciliation scheduled/admin job;
- shared queue follow-up/repair jobs as needed;
- optional approved Notification domain event only if separately defined; callback itself is not one.

#### Provider Integration

Implement only for enabled providers that actually expose callbacks/query APIs. Adapter owns:

- signature algorithm/config;
- callback schema;
- provider object ID mapping;
- status mapping/version;
- retryability/unknown classification;
- reconciliation query.

#### UI / Admin Surface

Protected callback/reconciliation inspector:

- provider/event reference;
- signature/dedupe result;
- mapped Delivery/Subscription;
- canonical transition;
- safe failure;
- reconciliation discrepancy/dry-run/repair result;
- no raw body/secrets.

#### Failure Behavior

- invalid signature/timestamp → reject before parse/side effect;
- duplicate event → safe acknowledge/ignore, no second transition;
- unmapped object/status → operational failure/manual review;
- missed callback found by reconciliation → safe idempotent repair if approved;
- unsafe discrepancy → incident/manual review;
- provider query unavailable → retry/degraded report, no local guess.

#### Tests

- valid/invalid signature fixtures;
- timestamp/replay failure;
- duplicate callback concurrency;
- processed-event uniqueness;
- unknown status/object mapping;
- callback/sync result race;
- raw-payload retention/redaction;
- reconciliation dry-run;
- allowed repair and forbidden cross-source mutation;
- provider sandbox E2E where available.

#### Documentation Updates

- U-CL07-14 architecture ruling and schema documented before migration;
- provider callback/reconciliation capability documented per enabled adapter;
- mapping version/runbook documented;
- progress tracker.

#### Acceptance Criteria

- every enabled callback provider is authenticated before state mutation;
- duplicate callbacks have one side effect;
- Notification uses its own processed-provider-event truth;
- unknown statuses fail safely;
- reconciliation detects/repairs only approved Notification discrepancies;
- source business truth is untouched.

#### Exit Gate

- U-CL07-14 closed and migration tests pass;
- signature/dedupe/race/reconciliation test suites pass;
- raw-payload/secret scan passes;
- provider sandbox callback succeeds for each enabled callback adapter where practical;
- no reused processed-event table or cross-domain mutation exists.

---

### 11 Notification Security, Reliability, Privacy, and Performance Hardening

#### Objective

Perform the Notification-specific production-readiness pass after core intake, reachability, delivery, routing, privacy, cross-Cluster contracts, and provider callbacks are proven.

#### Observable Result

Notification remains correct under duplicate/reordered requests, queue retry/dead-letter, provider degradation, callback lag, stale token rotation, dead subscriptions, large inbox history, privacy execution, and admin operations; operators can diagnose failures without seeing sensitive content or credentials.

#### Cluster Build-Plan Link

Implements the **Notification slice of CL-07 Feature 16 — CL-07 Security, Reliability, Privacy, and Performance Hardening**.

#### Dependencies

- Module Features 01–10;
- all production-blocking Notification unresolved decisions approved or corresponding capability explicitly disabled;
- root production targets and operational standards;
- provider runbooks/configuration for enabled channels.

#### In Scope

- authorization/RLS matrix;
- rate limiting/abuse controls for broad notification intake and subscription mutation;
- runtime fuzz validation;
- cross-domain repository/provider-import scans;
- provider timeout/circuit breaker behavior;
- queue lag/retry/DLQ/manual retry safety;
- stale/dead subscription cleanup;
- intake/delivery/callback concurrency load tests;
- payload-sensitivity sweep across every approved template/channel;
- privacy partial-failure/retry and retention gates;
- audit/sensitive access completeness for approved actions;
- telemetry redaction/secret scan;
- indexes/query plans/pagination performance;
- provider callback reconciliation under missed events;
- health checks/alerts;
- destructive/credential/provider migration rehearsal and recovery/rollback.

#### Out of Scope

- marketing automation;
- CRM/contact center;
- native mobile app unless separately architected;
- speculative analytics warehouse;
- public/private full-text Notification search without separate architecture;
- new provider/channel feature solely because hardening found an opportunity;
- new recipient/business semantics.

#### Module-Owned Data

Review existing Notification indexes/constraints and approved migrations only. Potential tuning areas:

- User/status/created pagination;
- Organization/status/created after Organization model approval;
- Subscription status/provider/platform/hash lookups;
- Delivery status/provider/subscription/reconciliation queries;
- processed-provider-event uniqueness/indexes if implemented;
- approved target/cardinality/channel/permission constraints.

Do not add an unread counter projection solely in anticipation. Add a rebuildable projection only if measured performance demonstrates need and architecture approves it.

#### Public Interfaces

Stabilize versions, reason codes, runtime schemas, pagination, and failure contracts. Breaking changes require coordinated source-owner updates and architecture review.

#### Shared Operations Used

All previously used canonical operations, with explicit review of:

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-044 `executeIdempotentCommand`;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-059 `verifyProviderWebhookSignature`;
- SH-060 `deduplicateProviderEvent`;
- SH-062 `reconcileProviderState`;
- SH-075 `encryptSensitiveValue`;
- SH-076 `normalizeAndHashIdentifier`;
- SH-029 `appendAuditEvent`;
- SH-030 `recordSensitiveAccess`;
- SH-034 `sanitizeTelemetryMetadata`;
- SH-037 `recordIntegrationFailure`;
- SH-038 `recordQueueTelemetry`;
- SH-035 `captureException`;
- SH-036 `emitMetric`;
- SH-039 `checkServiceHealth`;
- Privacy executor protocols.

No new Notification-local infrastructure is permitted during hardening.

#### Domain Logic

Hardening checklist:

1. Every public command/query rejects malformed/fuzzed input without unsafe logs.
2. Source/provider direct coupling scans are clean.
3. Duplicate/reordered SH-041 `requestNotification` calls converge.
4. Read/dismiss/interactions cannot illegally regress state.
5. Subscription refresh cannot revive stale credential state.
6. Dead token is disabled only after approved authoritative evidence.
7. Provider timeouts/circuit-breakers do not corrupt Delivery truth.
8. Queue retry/DLQ is observable and does not create duplicate source effect.
9. Callback lag/missed event can be recovered by supported reconciliation.
10. Every approved template/channel/sensitivity combination passes prohibited-data scan.
11. Privacy handler partial failures remain retryable/partial in Privacy orchestration.
12. Admin/support inspector is role-restricted and redacted.
13. No unresolved decision materially changes semantics of any production-enabled capability.

#### Authorization / Compliance

Run full matrices for:

- own Notification read/dismiss;
- cross-User denial;
- own Subscription list/revoke;
- organization recipient/admin context;
- admin/support delivery inspection/manual retry;
- sensitive/legal/security notification evidence;
- privacy/export execution;
- any step-up requirement declared by root policy.

Verify “admin/support” never means unrestricted sensitive content or credential access.

#### Database / Transaction Behavior

- concurrency/load tests on intake, read/dismiss, subscription rotation, Delivery apply, callback dedupe;
- query plans on representative volume;
- cursor pagination correctness/stability;
- safe backfill dry-run for credential/provider/attempt/event migrations;
- rollback/recovery runbook for destructive migrations;
- constraint violations produce explicit safe errors;
- no in-memory locks introduced.

#### Events / Jobs

- load/retry/DLQ testing;
- provider degradation simulations;
- reconciliation with missed callbacks;
- dead-subscription cleanup;
- expiry worker if approved;
- health checks/alert thresholds;
- no high-cardinality/sensitive metrics.

#### Provider Integration

For every enabled provider:

- health/readiness check;
- timeout/retry/circuit behavior;
- secret/config validation;
- normalized mapping version;
- callback verification if supported;
- reconciliation if supported;
- incident/runbook behavior;
- disablement behavior when provider is unavailable.

#### UI / Admin Surface

- Notification center stable loading/empty/error/pagination states;
- connected-device settings handle revoked/stale/dead subscriptions;
- delivery/provider inspector usable without secrets/sensitive body;
- reconciliation/manual retry controls explicit and authorized;
- no raw provider payload view by default.

#### Failure Behavior

Every degraded state must have explicit behavior:

- provider down → source workflow intact; Delivery retry/failed; ops visible;
- queue down/lag → authoritative Notification retained; ops visible;
- Audit required proof unavailable → follow governing fail-closed policy for that protected action;
- Privacy target transient failure → Privacy remains partial/retryable;
- dead push token → disable only after authoritative evidence;
- callback lag → supported reconciliation may recover;
- unknown provider status → no guessed success;
- credential crypto unavailable → fail closed for write/decrypt-dependent send;
- permission/consent unavailable → do not bypass to send.

#### Tests

- complete unit/integration/contract suites;
- critical Playwright journeys;
- authorization/RLS matrix;
- fuzz/property tests for public DTOs;
- concurrency/load tests for intake, read/dismiss, rotation, Delivery, callback dedupe;
- queue retry/DLQ and provider degradation;
- callback/reconciliation;
- privacy/destructive fixtures;
- telemetry/secret/sensitive-data scanning;
- provider import and cross-domain repository import scans;
- migration/backfill/rollback rehearsal;
- notification center pagination/performance benchmark;
- enabled provider sandbox smoke tests.

#### Documentation Updates

- production runbooks for enabled providers and queue failures;
- migration recovery procedures;
- public contract versions/reason codes;
- health/alert ownership;
- progress tracker;
- architecture updates for any final approved rulings before code enablement.

#### Acceptance Criteria

- no production-enabled path is semantically dependent on an unresolved architecture decision;
- all quality suites pass;
- no cross-User/organization leakage;
- prohibited sensitive/credential scans are clean;
- duplicate/reordered requests/callbacks/retries do not duplicate business effects;
- queue/provider failures are observable/recoverable without source corruption;
- privacy handlers are idempotent and cannot complete PrivacyRequest;
- destructive/credential migrations have rehearsed recovery;
- performance meets root production targets at representative volume.

#### Exit Gate

Notification is production-ready only when:

- typecheck, lint, build, unit, integration, contract, provider, privacy, authorization/RLS, and critical E2E suites pass;
- every production-enabled provider/channel has an approved selection/boundary/payload model;
- every relevant U-CL07 decision is closed or the dependent capability is explicitly disabled;
- sensitive payload/telemetry/credential scans pass;
- concurrency/replay tests pass;
- provider/queue degradation and reconciliation tests pass;
- migration/backfill/rollback drills pass;
- measured pagination/delivery worker performance meets root targets.

---

# MODULE INTEGRATION PHASE

Module Features 06–09 constitute Notification's primary integration phase. They must prove public contracts rather than database reach-through.

Required integration evidence before Notification is considered platform-integrated:

```text
Identity & Access
→ trusted actor for Notification UI/device/admin actions

Role / Authority
→ recipient/subscription/admin permission decisions

Consent & Disclosure
→ push disclosure proof without duplicating ConsentLog

Messaging
→ safe post-commit new-message Notification request

Organization Hiring / Hiring Modules
→ owner-resolved organization recipients and safe hiring alerts

Order / Gig
→ source-owned commercial alerts

Booking / Scheduling
→ Notification-only alert without exact protected context leakage

Track Subscription & Entitlement
→ lifecycle alert only; no entitlement interpretation

Privacy / Data Erasure
→ enumerate/execute Notification-owned targets

Audit / Observability
→ generic proof/ops evidence without replacing Notification truth
```

Integration is invalid if proven by:

- importing another Module's Prisma repository;
- source Module writing Notification tables;
- source Module calling a generic Notification provider SDK for alerts;
- Notification interpreting source lifecycle fields to reconstruct event meaning;
- copying Organization membership/settings into a Notification-owned truth table.

---

# MODULE HARDENING PHASE

Feature 11 is the dedicated Notification hardening phase. Hardening is limited to existing approved Notification capability:

- state transition races;
- semantic idempotency/replay;
- queue/provider outage/dead-letter;
- callback verification/dedupe/reconciliation;
- credential security;
- payload/telemetry redaction;
- authorization/RLS;
- privacy/retention execution;
- audit completeness where required;
- pagination/performance;
- migration/backfill safety;
- operational health.

Hardening must not become an excuse to add marketing automation, a generic omnichannel platform, source workflow logic, new providers, or speculative analytics.

---

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Canonical Intake and Safe In-App Truth | 01 Canonical In-App Notification Intake and Center; 02 Template Registry, Payload Safety, and Action Routes |
| 2 | Reachability and External Delivery | 03 Web Push Permission and Subscription Lifecycle; 04 Durable External Delivery Worker and Channel Ports; 05 Delivery Attempt, Expiry, Interaction, and Aggregate Semantics |
| 3 | Routing and Source-Module Contracts | 06 Organization Recipient Routing and Hiring Alerts; 07 Source-Module Notification Contract Pack |
| 4 | Privacy and Cross-Cluster Proof | 08 Notification Privacy Enumeration and Execution; 09 Cross-Cluster Notification Contract Proof |
| 5 | Provider Completion and Production Hardening | 10 Provider Callbacks, Deduplication, and Reconciliation; 11 Notification Security, Reliability, Privacy, and Performance Hardening |

**Total Module features: 11.**

### Parent Cluster mapping

| Module Feature | CL-07 Build-Plan Feature |
| --- | --- |
| 01 | 05 |
| 02 | 06 |
| 03 | 07 |
| 04 | 08 |
| 05 | 09 |
| 06 | 10 |
| 07 | 11 |
| — | 12 is Messaging/Healthcare/Moderation-focused; no duplicate Notification feature |
| 08 | Notification slice of 13 |
| 09 | Notification slice of 14 |
| 10 | 15 |
| 11 | Notification slice of 16 |

This mapping preserves Cluster sequencing rather than creating a competing plan.

---

# MODULE EXECUTION PATTERN

Before implementing each numbered Module feature:

1. Read [project overview V3](<../../../project-overview-v3.md>) and root architecture/standards.
2. Read Canonical Shared Operations.
3. Read CL-07 architecture and build plan.
4. Read [Notification architecture](<notification-module-architecture.md>) and this plan.
5. Read public-interface sections for direct dependencies/source owners.
6. Confirm the prior Module exit gate and the relevant parent Cluster prerequisite.
7. Check every U-CL07 decision named by the feature and verify its current status.
8. Write a concise implementation specification for **this feature only**.
9. Implement only this feature and any minimum canonical prerequisite in its owning scope.
10. Run root-required quality checks plus the feature's tests.
11. Perform the named contract/E2E/manual verification.
12. Update `progress-tracker.md`.
13. Update architecture first if a binding decision legitimately changed.
14. Record assumptions, provider capabilities disabled, failures, and deferred work.

Do not move to the next feature because most code exists. The exit gate is the completion boundary.

---

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a numbered feature, the coding agent must produce a concise implementation specification containing:

- **Feature / Cluster link**
- **Objective**
- **Observable result**
- **Dependencies**
- **Architecture rulings / unresolved decisions consumed**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Public contracts introduced/changed**
- **Shared operations consumed**
- **Permissions/compliance gates**
- **Primary workflow**
- **Provider integration**
- **Jobs/events**
- **Database/transaction behavior**
- **Idempotency/concurrency**
- **Error/failure behavior**
- **UI/admin surface, if any**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Exit gate**

The specification must name any unresolved decision that would block the feature and state whether the decision is approved. Do not pre-generate low-level specifications for all future features because architecture, provider selection, and source interfaces may legitimately change before those features are reached.

---

# REQUIRED COMPLETION REPORT

After implementing each numbered feature, the coding agent must report:

- **Feature completed**
- **Cluster feature supported**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Backfills/recovery steps**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Shared operations reused**
- **Events/jobs added**
- **Provider adapters added/enabled/disabled**
- **Tests added/changed**
- **Commands run**
- **Manual/contract/E2E verification**
- **Documentation updated**
- **Architecture rulings consumed/changed**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Deferred work**
- **Exit-gate result: passed / failed / blocked**

If the exit gate does not pass, the feature is not complete. Report it as failed or blocked and do not proceed silently.

---

# FINAL QUALITY CHECK

Before treating the Notification Module plan as complete or production-ready, verify:

1. `Notification`, `NotificationDelivery`, `NotificationSubscription`, and `NotificationSubscriptionEvent` remain Notification-owned truth.
2. No neighboring Module lifecycle has been absorbed.
3. Every source uses SH-041 `requestNotification`; provider SDK calls are isolated to Notification adapters.
4. Canonical shared operations are consumed rather than duplicated.
5. Shared mechanism/separate truth boundaries remain explicit for idempotency, provider dedupe, status translation, reconciliation, audit, privacy, and cryptography.
6. All cross-Module reads use owner public interfaces/events rather than direct repositories.
7. Provider adapters never become business truth.
8. Audit, Notification domain evidence, and Observability are separate.
9. Privacy orchestration and retention exemptions remain Privacy-owned.
10. Search remains uninvolved in ordinary Notification lifecycle.
11. Implementation features remain aligned to CL-07 Feature 05–16 sequencing and do not duplicate Messaging-only work.
12. Every numbered Module feature has explicit tests, acceptance criteria, and exit gate.
13. Every production-enabled capability has its required U-CL07 decisions approved.
14. Generic SMS and Web Push alerts remain disabled if their provider selection is unresolved; Identity verification-provider transport follows the approved CL-07-R002 boundary.
15. Push credential storage has one approved encrypted/hash authority and does not expose secrets.
16. Payload safety is proven for every template/channel/sensitivity combination enabled in production.
17. Delivery/retry/callback behavior is idempotent and concurrency-safe.
18. Delivery/read/click/open/close never implies source workflow completion.
19. Organization routing uses Organization-owned membership/settings facts.
20. A coding agent can implement the next feature without inventing ownership, provider, lifecycle, privacy, or shared-infrastructure architecture.
