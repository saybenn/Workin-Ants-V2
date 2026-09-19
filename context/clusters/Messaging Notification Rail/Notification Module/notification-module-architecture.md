# Notification Module Architecture

> **Module ID:** `notification`  
> **Module name:** Notification Module  
> **Module type:** capability  
> **Build status:** `mvp_active`  
> **Primary Cluster:** CL-07 — Messaging & Notification Rail  
> **Document status:** Implementation-grade Module architecture. Confirmed and Cluster Architecture Ruling material is binding; Proposed Rulings remain non-binding until approved; Unresolved Decisions are explicit implementation boundaries.  
> **Intended audience:** coding agents, developers, reviewers, maintainers, architecture reviewers  
> **Relationship to root architecture:** subordinate to Workin Ants [project overview V3](<../../../project-overview-v3.md>), root `architecture.md`, root `code-standards.md`, and the Canonical Shared Operations Architecture. Root rules control platform-wide identity, authorization, privacy, audit, observability, queueing, cryptography, provider infrastructure, and source-of-truth conventions.\
> **Relationship to Cluster architecture:** this file specializes [CL-07 architecture](<../messaging-notification-rail-architecture.md>) for the Notification Deep Module. It may narrow Cluster decisions but may not contradict or silently broaden them.\
> **Update rule:** update this file whenever a binding Notification ownership, lifecycle, public-contract, provider, privacy, persistence, or security decision changes. Build progress must never silently redefine architecture.

---

## 1. Module Header

### 1.1 Authority and evidence posture

This document is synthesized from the current Workin Ants evidence set:

1. [project overview V3](<../../../project-overview-v3.md>);
2. Deep Module Registry;
3. Cluster Registry v2.3;
4. current Prisma schema;
5. Ubiquitous Language / Compliance Inventory;
6. Canonical Shared Operations Architecture;
7. [CL-07 architecture](<../messaging-notification-rail-architecture.md>);
8. [CL-07 build plan](<../messaging-notification-rail-build-plan.md>);
9. the standardized Notification Module Architecture Extract in this architecture thread.

The repository copies of root `architecture.md`, root `code-standards.md`, and `progress-tracker.md` were not part of the attached evidence set used to generate this file. They remain required implementation context and take precedence where they define platform-wide conventions not contradicted by a higher-order ownership ruling.

### 1.2 Decision labels

- **Confirmed** — directly supported by current registry/schema/glossary/canonical shared-operation evidence.
- **Architecture Ruling** — binding decision already stated by the governing CL-07 architecture.
- **Proposed Ruling** — strong current recommendation from CL-07, but not binding until approved.
- **Unresolved Decision** — evidence establishes the issue but does not authorize implementation to choose an answer.

### 1.3 Conflict handling

When historical evidence conflicts:

1. preserve one owner per lifecycle;
2. prefer explicit root/Cluster Architecture Rulings over older ambiguous ownership lists;
3. treat the current Prisma schema as executable evidence until an approved migration changes it;
4. do not convert a Proposed Ruling into code merely because it is convenient;
5. stop at an Unresolved Decision when the requested feature depends on it.

---

## 2. Purpose, Goal, and Transformation

### Purpose

The Notification Module persists, routes, delivers, and records system alerts intended for Workin Ants Users or Organization-related recipients without taking ownership of the business event that caused the alert.

### Goal

Provide one canonical alert-delivery capability so Messaging, Order, Gig, Booking, Hiring, Verification, Moderation, Holds, Subscription/Entitlement, Security, Rewards, Prize, and other workflow Modules do not create their own notification tables, push-token stores, delivery queues, provider SDK integrations, retry loops, or delivery state machines.

### What enters

```text
source-owned alert intent
+ source Module/type/id reference
+ typed recipient target or owner-resolved recipient facts
+ registered template key/version
+ safe validated variables
+ priority
+ payload sensitivity
+ approved action route
+ channel requirements
+ correlation/idempotency context
+ consent/permission/reachability facts when required
```

### What leaves

```text
Notification source truth
+ channel-specific delivery attempt/result truth
+ push subscription / permission / service-worker / PWA evidence
+ read/dismiss/click/open/close evidence where currently modeled
+ provider-normalized outcomes
+ dead-subscription effects
+ privacy-execution result when instructed
+ audit/observability evidence where required
```

### Capability transformation

```text
source Module commits its own truth
→ source requests a notification
→ Notification validates semantic request boundary
→ recipient facts are resolved through their owner
→ Notification applies channel/payload/reachability policy
→ Notification writes authoritative alert truth
→ external work is queued through canonical infrastructure
→ Notification renders a safe channel payload
→ Notification-owned provider adapter sends it
→ provider result is normalized into NotificationDelivery truth
```

### Why this is its own Module boundary

Notification owns a distinct set of lifecycles and policies that recur across unrelated business domains: alert intent records, channel routing, device/browser reachability, provider delivery attempts, payload minimization, provider status translation, dead-token handling, and notification interaction evidence. Keeping these in one Module prevents each business domain from rebuilding delivery mechanics while preserving the rule that the source business Module continues to own the meaning and lifecycle of the event being communicated.

---

## 3. Owned Truth

### 3.1 Schemas/models owned

| Record | Meaning |
| --- | --- |
| `Notification` | Workin Ants record that an alert was accepted for a resolved target/channel context. It stores source reference, template/output snapshot, priority, sensitivity, action route, lifecycle state, and expiry metadata. |
| `NotificationSubscription` | User/device/browser push reachability state, including provider/platform, observed permission, service-worker/PWA metadata, credential references, health, and revocation/failure state. It is not User identity. |
| `NotificationDelivery` | A provider/channel delivery attempt/result record. It is transport evidence, not proof the User paid attention or completed the source workflow. Current retry-attempt semantics are incomplete and gated by U-CL07-13. |
| `NotificationSubscriptionEvent` | Append-only Notification-owned evidence of permission, service-worker, subscription, token, PWA, and some interaction observations. It does not replace current Subscription or Delivery state. |

### 3.2 Enums/status vocabularies owned

- `NotificationStatus`
- `NotificationChannel`
- `NotificationPriority`
- `NotificationSubscriptionProvider`
- `NotificationPlatform`
- `NotificationSubscriptionStatus`
- `NotificationDeliveryStatus`
- `NotificationPermissionStatus`
- `NotificationSubscriptionEventType`
- `PwaInstallStatus`
- `NotificationPayloadSensitivity`

`NotificationChannel` is reused by `OrganizationNotificationSetting`; shared enum use does not transfer that model's lifecycle ownership to Notification.

### 3.3 Lifecycles owned

Notification owns state transitions for:

1. `Notification`;
2. `NotificationDelivery`;
3. `NotificationSubscription`;
4. append-only `NotificationSubscriptionEvent` evidence.

It does **not** own the event lifecycle referenced by `sourceType`/`sourceId`.

### 3.4 Local domain evidence and proof

Notification-owned proof includes:

- accepted alert record;
- notification read/dismiss timestamps where modeled;
- provider delivery attempt/result evidence;
- browser permission observations;
- service-worker registration observations;
- push-subscription creation/refresh/revocation/failure observations;
- token/endpoint rotation and dead-token evidence;
- PWA installation-readiness evidence;
- click/open/close evidence where modeled;
- supporting delivery proof for source-owned legal/security workflows.

### 3.5 Projections

No persistent Notification projection beyond the current source records is confirmed. `getUnreadNotificationCount` is a derived query over Notification truth, not a separate source-of-truth counter. Do not introduce an unread-count projection until measured performance and an explicit architecture decision justify it.

### 3.6 Compliance proof role

Confirmed compliance/proof participation:

- **Primary:** Web Push background notification delivery — `Notification`, `NotificationSubscription`, `NotificationDelivery`, `NotificationSubscriptionEvent`.
- **Primary:** Push notification permission proof — `NotificationSubscription`, `NotificationSubscriptionEvent`, with `ConsentLog` remaining Consent-owned proof.
- **Supporting:** iOS PWA push readiness — `NotificationSubscription`, `NotificationSubscriptionEvent`.
- **Primary:** privacy-safe notification payloads — `Notification`, `NotificationDelivery`.
- **Supporting:** DMCA takedown/counter-notice delivery — `Notification`, `NotificationDelivery`; legal decision remains Content Moderation & Legal Notice-owned.
- **Supporting:** FCRA notice delivery — `Notification`, `NotificationDelivery`; screening/adverse-action decision remains with its owner.

Historical registry entries also name security-alert notification, recovery email delivery, and SMS MFA delivery. Their triggering security/recovery/challenge truth remains Identity & Access-owned. Identity verification-provider transport follows the approved boundary in Section 20.3; generic SMS provider selection remains unresolved.

### 3.7 Policies/invariants owned locally

Notification owns:

- payload safety and channel-safe rendering;
- validation of Notification template keys/versions once the template registry ruling is approved;
- approved action-route validation;
- routing/fan-out after owner-provided recipient facts;
- deduplication of resolved User recipients;
- channel eligibility based on Notification-owned reachability plus externally owned gates;
- provider status/error translation into Notification vocabularies;
- dead/revoked subscription handling after authoritative provider evidence;
- semantic idempotency identity for Notification commands;
- delivery retryability classification at the Notification/provider boundary;
- aggregate/lifecycle rules only after the relevant unresolved decisions are approved.

---

## 4. Explicit Non-Ownership

The Notification Module must not own or reconstruct the following.

| Adjacent owner | Truth/responsibility that stays outside Notification |
| --- | --- |
| Identity & Access | `User`, session/authentication, OTP challenge lifecycle, MFA verification, recovery-token issuance/validation/expiry, account recovery state, phone-number update state, security event truth. Notification may deliver owner-generated generic security/recovery alerts; Identity verification-provider transport remains outside Notification under Section 20.3. |
| Role / Authority | Platform, organization, participant, and ownership permission interpretation. Notification supplies recipient/subscription relationship facts and requested action. |
| Consent & Disclosure | `ConsentLog`, accepted consent/disclosure version, consent validity/version lifecycle. Browser permission and subscription state remain separate Notification truths. |
| Messaging | `Thread`, `ThreadParticipant`, `Message`, `MessageMedia`, participant policy, private message content. Notification may persist only safe metadata required for delivery. |
| Organization Hiring | `Organization`, `OrganizationMember`, `OrganizationRole`, `OrganizationNotificationSetting`, organization member/settings lifecycle and recipient-role interpretation. |
| Transaction / Order and Gig / Demand | Order/Gig/GigResponse/GigAssignment state and the decision that an alert should be requested. |
| Booking & Calendar / Video | Booking/session state and provider/calendar/video truth. |
| Candidate Application / Job Interview / Job Compliance | application/interview/job state, resume data, FCRA/job compliance decisions. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle and whether a hold should be created/released. |
| Content Moderation & Legal Notice | report/case/legal-notice/DMCA lifecycle, notice requirement, legal deadlines, legal content approval. |
| Trust Verification / Screening | screening result, FCRA workflow and adverse-action decision. |
| Track Subscription & Entitlement | `TrackSubscription`, `TrackEntitlementGrant`, usage, premium/plan/entitlement policy. Entitlement changes may trigger alerts only. |
| Sweepstakes / Prize, Gamification / Rewards | prize/reward eligibility, result, fulfillment, tax decision. |
| Healthcare / Regulated Services | healthcare sensitivity/redaction/block policy. Notification consumes only safe payload constraints/approved facts. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, export orchestration, legal retention decision, overall completion. |
| Audit / Event Ledger | generic `AuditEvent` and `AccessAuditLog`. Notification keeps domain delivery/subscription evidence separate. |
| Observability / Ops | public failure recording, queue telemetry, incidents, metrics/logging infrastructure; persistence remains CL-09-owned and unresolved. These capabilities do not replace Notification status. |
| Search / Public Visibility | Typesense/public search projections and `SearchUpsertEvent`. Notification is not a public-search entity. |
| Media / File Access | `MediaAsset`, upload/storage/scanning/signed URLs. Notification has no attachment model in current evidence. |
| Provider clouds / operating system | provider cloud internals, OS notification settings, or provider-native status as Workin Ants truth. |

Also prohibited inside this Module:

- email marketing campaigns, newsletters, CRM sequences, audience marketing automation;
- a generic “communications” aggregate merging Message and Notification;
- a global provider-event ledger shared with Stripe, Calendar, Video, or other provider-owning Modules;
- a global privacy crawler or privacy-request workflow;
- local authentication, authorization, queue, retry, dead-letter, crypto, audit, or observability frameworks.

---

## 5. Module Architecture Principles

1. **Alert truth is not source-event truth.** A Notification says an alert was accepted/delivered about a source; it does not prove the source event happened unless the source owner says so.
2. **One canonical intake.** Workflow Modules use SH-041 `requestNotification`; they do not write Notification rows or call delivery providers directly.
3. **Notification owns transport policy, not domain policy.** Source owners decide whether/when an alert is semantically required and provide safe facts.
4. **Consent, permission, reachability, delivery, and interaction are separate evidence.** Never collapse them into one `canNotify` boolean.
5. **Outward payloads are minimal.** Private Message bodies, PHI, OTPs, recovery tokens, tax/financial details, raw resume data, identity documents, contract text, and provider credentials must not enter outward push payloads or generic telemetry.
6. **Provider state is normalized.** Provider-native status strings are adapter input only; Workin Ants truth is the Notification-owned status after validation/translation/application.
7. **External delivery is asynchronous.** Source transactions do not wait for or roll back because a provider is unavailable.
8. **No local infrastructure copies.** Use canonical idempotency, queue, retry, event, webhook verification, cryptography, audit, request-context, and observability operations.
9. **Owner facts stay with owners.** Organization membership, Thread participants, Order parties, and other recipient relationships are resolved through owner interfaces.
10. **Current schema is honored until migration approval.** Do not silently “fix” unresolved Notification cardinality, provider vocabulary, retry, or interaction issues in feature code.
11. **Provider selections may be disabled.** Provider-neutral ports allow in-app and stubbed integration work without inventing a production provider choice.
12. **No public search.** Notification records, subscriptions, deliveries, and device metadata are never sent to public Search by default.
13. **Privacy orchestrates; Notification executes locally.** Notification may erase/anonymize/revoke only its own records/resources under an approved Privacy instruction.
14. **Delivery does not equal attention.** `delivered`, click, open, or close evidence must not complete a source workflow.

---

## 6. Proposed Folder / Code Structure

Exact repository placement must follow root `code-standards.md`. If root standards prescribe equivalent paths, keep these responsibilities and change only the placement convention.

```text
src/
  modules/
    notification/
      domain/
        routing-policy.ts
        payload-policy.ts
        delivery-policy.ts
        subscription-policy.ts
        lifecycle-policy.ts
        types.ts

      application/
        commands/
          request-notification.ts
          mark-notification-read.ts
          dismiss-notification.ts
          record-notification-interaction.ts
          record-permission-state.ts
          record-service-worker-state.ts
          upsert-push-subscription.ts
          refresh-push-subscription.ts
          revoke-push-subscription.ts
          handle-push-subscription-change.ts
          record-pwa-readiness.ts
        queries/
          list-notifications.ts
          get-unread-notification-count.ts
          list-notification-subscriptions.ts
          get-delivery-state.ts              # only after semantics are approved
        services/
          notification-intake-service.ts
          recipient-resolution-service.ts
          delivery-planning-service.ts
          provider-result-service.ts

      contracts/
        request-notification.ts
        notification-queries.ts
        recipient-facts.ts
        provider-port.ts
        provider-result.ts
        privacy-executor.ts

      templates/
        registry.ts                          # PR-N05 / approved equivalent
        schemas/
        action-routes.ts

      infrastructure/
        persistence/
          notification-repository.ts
          subscription-repository.ts
          delivery-repository.ts
          subscription-event-repository.ts
          processed-provider-event-repository.ts  # only after U-CL07-14 ruling
        providers/
          email/
          sms/
          web-push/
        workers/
          delivery-worker.ts
          expiry-worker.ts                   # only after U-CL07-12 ruling
          reconciliation-worker.ts
          dead-subscription-worker.ts
        webhooks/
          provider-callback-handler.ts

      privacy/
        enumerate-subject-data.ts
        execute-privacy-instruction.ts

      presentation/
        actions/
        queries/
        components/
          notification-center/
          notification-settings/
          delivery-inspector/                # admin/support only
        service-worker/

      tests/
        unit/
        contract/
        integration/
        provider/
        privacy/
        e2e/
```

Shared platform mechanisms remain outside `src/modules/notification/`, for example:

```text
src/platform/
  auth/
  authorization/
  events/
  jobs/
  observability/
  crypto/
```

Do not create empty folders preemptively. Add a folder only when a real responsibility in this architecture is implemented.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Presentation / client | Notification center, connected-device settings, permission/service-worker callbacks, approved admin delivery inspector | permission interpretation, provider secrets, source business decisions, direct Prisma writes |
| Application commands | command orchestration, validation, idempotency boundary, calls to owner/shared interfaces, transaction coordination | generic auth/queue/crypto frameworks, source Module repositories |
| Application queries | authorized reads and derived summaries over Notification truth | cross-domain joins used to reconstruct source business status |
| Domain policy | routing, payload safety, Notification lifecycle, subscription consistency, retryability and provider-result semantics | organization-role policy, consent lifecycle, legal/FCRA/DMCA decisions, entitlement policy |
| Persistence adapters | read/write only Notification-owned records | writes to User, OrganizationMember, ConsentLog, source workflow tables, AuditEvent, IntegrationFailure |
| Workers | owner-local delivery/expiry/dead-token/reconciliation execution using shared queue/scheduler | custom queue engine, global sagas, business workflow rollback |
| Provider adapters | provider request/response mapping, callback parser, adapter-local secret/config handling, Notification status translation | source business status, generic provider status vocabulary for other Modules |
| Contracts | stable Notification command/query DTOs, owner-recipient contract, provider-neutral ports, privacy handler contract | universal cross-domain repository contracts |
| Templates | controlled Notification transport rendering and variable schemas | business/legal decision logic; per-source provider dispatch |
| Privacy executor | owner-local enumeration and execution against Notification data/provider resources | PrivacyRequest lifecycle, retention exemption creation, global erasure orchestration |
| Tests | Module policy, persistence, public contracts, adapter behavior, integration boundaries | tests that rely on forbidden cross-domain repository access |

---

## 8. Data Model

### 8.1 `Notification`

**Purpose:** authoritative Workin Ants alert record after Notification accepts a request.

**Key relationships:** optional `userId`; optional `organizationId`; many `NotificationDelivery`; optional linkage from `NotificationSubscriptionEvent`; source object reference by `sourceType`/`sourceId`.

**Authoritative fields:**

- `channel`
- `name`
- `priority`
- `title`, `body`, `payload` as Notification-owned rendered/snapshot output, subject to safe-payload policy
- `actionUrl`
- `status`
- `payloadSensitivity`
- `safePreviewOnly`
- `sourceType`, `sourceId`
- `expiresAt`
- `readAt`, `clickedAt` where current model uses them

**Lifecycle fields:** `status`, `createdAt`, `readAt`, `clickedAt`, `expiresAt`.

**Current constraints/indexes:** indexes support recipient/status/created time, channel/status, name/time, source reference, sensitivity, expiry. There is no current uniqueness/idempotency constraint at this model level.

**Known data-model gaps:**

- both `userId` and `organizationId` are nullable; exactly-one target is not enforced;
- both could currently be populated;
- parent `channel` overlaps Delivery `channel` semantics;
- no `dismissedAt`;
- no explicit expired status;
- aggregate status across multiple attempts/channels is undefined;
- `name` is a free string until template governance is approved;
- `payload` is unrestricted JSON and must never be assumed safe by type alone.

**Privacy/retention:** user/org references, title/body/payload, action route, source references, and interaction timestamps may be personal data. Privacy instructions must define erase/anonymize/retain behavior; Notification must not invent statutory retention periods.

### 8.2 `NotificationSubscription`

**Purpose:** current User/device/browser push reachability state.

**Key relationships:** belongs to `User`; has many `NotificationDelivery`; has many `NotificationSubscriptionEvent`.

**Authoritative categories:**

- provider/platform/status;
- observed permission state and timestamps;
- service-worker scope/version and VAPID key reference;
- PWA readiness fields;
- endpoint/token hashes for matching;
- encrypted recoverable endpoint/token/key material where approved;
- failure/health metadata;
- revoke/unsubscribe state.

**Concurrency-sensitive fields:** endpoint/token identity, `updatedAt`, token rotation, status, permission state, failure counters, `lastDeliveryAttemptAt`.

**Current uniqueness:** `@@unique([provider, endpoint])` and `@@unique([provider, token])`; hash indexes also exist. These current constraints require an approved migration to implement PR-N04 target authority; exact uniqueness/backfill/cutover details remain U-CL07-18.

**Security conflict:** plaintext `endpoint`, `token`, `p256dh`, and `auth` currently coexist with encrypted/hash fields. Production implementation must not maintain two active credential truths. PR-N04 target authority is approved; U-CL07-18 still gates exact uniqueness/backfill/cutover.

**Policy invariant:** application paths must not create an active Web Push subscription when `permissionStatus != granted`.

**Privacy/retention:** endpoint/token/key material, user-agent/device labels, service-worker metadata, IP-linked event evidence, and failure metadata are personal/device data. Never expose raw credentials in list/query responses or logs.

### 8.3 `NotificationDelivery`

**Purpose:** transport-attempt/result truth.

**Key relationships:** belongs to Notification; optionally belongs to push Subscription; may link to SubscriptionEvents.

**Authoritative fields:** channel, canonical Delivery status, normalized provider message reference, safe provider error category/code, timestamps, interaction timestamps, subscription-disable signal.

**Known data-model gaps:**

- `provider` uses `NotificationSubscriptionProvider`, a push-specific enum, and cannot truthfully identify email/SMS providers;
- attempt number/correlation/idempotency fields are absent;
- retry history semantics are unresolved;
- multiple interaction fields overlap parent/Event evidence.

**Concurrency-sensitive behavior:** one worker/attempt must not double-apply provider outcomes; callback and synchronous response races must converge on valid transitions.

**Privacy/retention:** provider IDs, error metadata, clicked URLs, and timestamps may be personal. Raw provider payloads should not be retained by default.

### 8.4 `NotificationSubscriptionEvent`

**Purpose:** append-only evidence for Notification device/reachability observations and certain notification interactions.

**Key relationships:** optional Subscription, Notification, Delivery; required User.

**Authoritative fields:** event type, provider/platform, permission/PWA state, service-worker metadata, endpoint/token hashes, minimized request evidence, timestamp.

**Known modeling overlap:** `notification_clicked` and `notification_closed` live in a subscription event enum even though they describe notification interaction, while parent Notification and Delivery also contain interaction fields. U-CL07-19 must resolve the canonical interaction record before analytics/evidence normalization.

**Privacy/retention:** `ipHash`, `userAgent`, endpoint/token hashes, metadata, and user linkage require minimization and Privacy executor coverage.

### 8.5 Externally owned model used for routing

`OrganizationNotificationSetting` uses `NotificationChannel`, but its lifecycle belongs to Organization Hiring. Notification may consume an owner-issued recipient/settings result; it must not write, own, or interpret OrganizationRole directly.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Notification lifecycle

Current schema:

```text
queued
  ├─→ sent ─→ read
  │        └─→ dismissed
  └─→ failed

sent ─→ failed     # represented by enum possibility; exact legality must be policy-tested
```

**Transition owner:** Notification application/domain services only.

**Triggers:** accepted intake; in-app availability; external delivery result; User read/dismiss action.

**Terminal/reversal:** exact terminality and reopen/reversal rules are not fully specified. `read` and `dismissed` must not be reset casually. No code may infer source workflow completion.

**Concurrency:** read/dismiss must be deterministic under repeated/concurrent requests. Intake must be idempotent.

**History proof:** current model stores timestamps but no full Notification transition ledger. Generic AuditEvent must not be used as a replacement for missing domain history.

**Unresolved:** U-CL07-10, U-CL07-11, U-CL07-12, U-CL07-19.

### 9.2 Delivery lifecycle

```text
queued
  ├─→ sending ─→ sent ─→ delivered
  │      └──────────────→ failed
  ├─────────────────────→ failed
  └─→ skipped
```

**Transition owner:** Notification delivery application service/worker after provider-neutral result translation.

**Provider rule:** provider-native values do not directly write `NotificationDeliveryStatus`.

**Retry/reversal:** unresolved. Production retry history must not overwrite evidence repeatedly once U-CL07-13 is resolved.

**Concurrency:** worker claim and provider callback must be replay-safe. Unknown provider statuses fail safely; they never map to success by guesswork.

### 9.3 Subscription lifecycle

```text
permission observed
→ subscription created/refreshed
→ active
→ revoked | expired | failed | disabled
```

**Transition owner:** Notification.

**Precondition:** active Web Push requires observed `permissionStatus=granted` through application policy.

**Reactivation:** a revoked/expired/failed/disabled record may only return to active under an explicitly valid create/refresh/recovery policy; do not clear state merely because a client resubmits old credentials.

**Concurrency:** token/endpoint refresh is stale-write sensitive. Newer valid rotation must not be overwritten by an older callback.

**Evidence:** append `NotificationSubscriptionEvent` for relevant observed transitions; the event ledger does not replace current state.

### 9.4 Permission lifecycle

Current vocabulary:

```text
not_requested
→ prompt_required
→ granted | denied | dismissed | unsupported | revoked
```

Browser permission is observed device state. Server code must not fabricate a browser grant. ConsentLog remains separate proof.

### 9.5 PWA readiness

Current vocabulary:

```text
not_prompted → prompt_shown → dismissed | installed
                         ↘ unsupported
unknown may precede a resolved state
```

`isIosPwa`, `appInstalled`, and `pwaInstallStatus` overlap. Their canonical derivation/authority is not fully specified; do not create further duplicate flags.

---

## 10. Commands

### 10.1 SH-041 `requestNotification`

- **Purpose:** canonical intake for a business/security/compliance/operational alert.
- **Actor/context:** authenticated User/system/service actor context as appropriate; caller identity and source Module must be trusted server-side.
- **Authoritative inputs:** source Module/type/id; recipient target/group descriptor; template key/version; priority; sensitivity; safe variables; action route; channel requirements; idempotency key; correlation context.
- **Preconditions:** valid contract; registered template/version for implemented path; valid source-owned recipient contract; payload/action-route policy; required consent/permission/reachability gates for relevant channels.
- **Writes:** one or more Notification-owned records only according to approved target/channel model.
- **Shared operations:** SH-044 `executeIdempotentCommand`, SH-003 `queryOwnerFacts` (Proposed ruling)/SH-043 `resolveNotificationRecipients`, SH-008 `queryConsentProof` when required, SH-032 `createRequestContext`, SH-034 `sanitizeTelemetryMetadata`, SH-047 `enqueueReliableJob` for external channels.
- **Effects:** may enqueue delivery work; may append audit/ops evidence only where policy requires.
- **Idempotency:** required. Duplicate semantic request returns original accepted result/effect.
- **Failure modes:** invalid request, unsafe variable, invalid action route, unknown template/version, no eligible recipient, channel unavailable, unresolved production provider/policy.

### 10.2 `markNotificationRead`

- **Purpose:** mark an in-app alert read.
- **Actor/context:** authenticated targeted User; Role / Authority decision using Notification recipient facts.
- **Input:** Notification ID plus optional expected version/update marker if concurrency scheme uses one.
- **Preconditions:** target ownership; allowed lifecycle transition.
- **Writes:** Notification `status/readAt` only.
- **Idempotency:** repeated read is safe and returns current truth.
- **Must not:** mark Thread read, complete source workflow, or infer source state.

### 10.3 `dismissNotification`

- **Purpose:** remove/dismiss the alert from active user attention without mutating the source workflow.
- **Actor/context:** authenticated targeted User.
- **Writes:** current status representation; `dismissedAt` only if an approved migration adds it.
- **Idempotency:** repeated dismissal is safe.
- **Unresolved:** timestamp representation under U-CL07-12.

### 10.4 `recordNotificationInteraction`

- **Purpose:** persist approved click/open/close evidence.
- **Actor/context:** authenticated client or verified provider callback, depending interaction source.
- **Preconditions:** target Delivery/Notification association is valid; event is runtime-validated; duplicate event identity is replay-safe.
- **Writes:** only the canonical interaction representation approved under U-CL07-19.
- **Must not:** assert attention, understanding, purchase, acceptance, or source workflow completion.

### 10.5 `recordNotificationPermissionState`

- **Purpose:** persist the browser permission state observed by the client.
- **Actor/context:** authenticated User managing own device/subscription context.
- **Writes:** Notification-owned permission state and append-only event evidence.
- **Rule:** browser result is observed, not server-invented.

### 10.6 `recordServiceWorkerRegistrationState`

- **Purpose:** record service-worker registration success/failure and approved version/scope metadata.
- **Actor/context:** authenticated client.
- **Writes:** Subscription/service-worker fields and event proof.
- **Must not:** treat service-worker existence as consent or delivery proof.

### 10.7 `upsertPushSubscription`

- **Purpose:** create or converge a User's valid browser/device push reachability record.
- **Actor/context:** authenticated User, own device context.
- **Preconditions:** permission granted; required Consent proof present; credential storage policy approved; runtime input valid.
- **Writes:** `NotificationSubscription` plus event evidence.
- **Shared operations:** SH-008 `queryConsentProof`, SH-075 `encryptSensitiveValue`, SH-076 `normalizeAndHashIdentifier`, SH-044 `executeIdempotentCommand`, authorization/audit as required.
- **Concurrency:** duplicate same subscription converges; no plaintext secret exposure.

### 10.8 `refreshPushSubscription`

- **Purpose:** safely rotate endpoint/token/key material.
- **Preconditions:** current ownership and valid new subscription material.
- **Concurrency:** stale rotation must not overwrite a newer state; use canonical optimistic concurrency/transaction semantics.
- **Writes:** encrypted/hash credentials, health/update metadata, append-only refresh event.

### 10.9 `revokePushSubscription`

- **Purpose:** disable future delivery to a User-controlled subscription.
- **Actor/context:** authenticated owner or specifically authorized admin/support path.
- **Writes:** subscription revoke/disable metadata and event evidence.
- **Audit:** revocation/security-significant admin action may call SH-029 `appendAuditEvent` according to root policy.
- **Idempotency:** repeated revoke succeeds safely.

### 10.10 `handlePushSubscriptionChange`

- **Purpose:** process browser `pushsubscriptionchange` or equivalent client token rotation.
- **Rule:** treat callback as an input to owner command, not authority to bypass user/subscription association checks.

### 10.11 `recordPwaInstallReadiness`

- **Purpose:** persist PWA/install guidance capability evidence.
- **Rule:** PWA readiness is device capability metadata, not account identity/status.

### 10.12 `dispatchNotificationDelivery` — internal

- **Purpose:** perform one durable delivery attempt through a channel-neutral port.
- **Actor/context:** trusted queue worker context.
- **Preconditions:** authoritative Notification exists; not expired under approved policy; eligible channel; safe rendered content; valid destination; valid attempt identity.
- **Writes:** `NotificationDelivery` result and potentially Subscription health signal.
- **Shared operations:** SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`, SH-038 `recordQueueTelemetry`, SH-037 `recordIntegrationFailure`, request context/telemetry sanitization.
- **Must not:** mutate source business state.

### 10.13 `recordProviderDeliveryResult` — internal

- **Purpose:** apply normalized provider result to Notification-owned Delivery/subscription state.
- **Rule:** only provider-neutral normalized result enters application/domain layer.
- **Unknown status:** explicit unsupported/unmapped failure; never guessed success.

### 10.14 `disableDeadNotificationSubscription` — internal

- **Purpose:** disable reachability after provider-confirmed invalid/dead endpoint/token evidence.
- **Rule:** do not disable User identity; append local event proof; execution is idempotent.

### 10.15 SH-095 `executePrivacyInstruction`

- **Purpose:** execute a Privacy-owned disposition against Notification-owned records/provider resources.
- **Actor/context:** Privacy-authorized orchestration context, not ordinary User route.
- **Input:** stable target, disposition, retention instruction, idempotency/correlation.
- **Writes:** only Notification-owned records/provider resources as instructed.
- **Output:** explicit owner execution result; never overall PrivacyRequest completion.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result type | Consumer must not infer |
| --- | --- | --- | --- | --- |
| `listNotifications` | User-facing notification center | authenticated actor; cursor/pagination; safe status filters | Notification source truth / safe summaries | source workflow status; Message unread state |
| `getUnreadNotificationCount` | User UI | authenticated actor | derived count over Notification truth | a persisted quota/counter or Message unread count |
| `listNotificationSubscriptions` | account settings | authenticated actor | own device/reachability summaries with secrets removed | OS state beyond observed evidence; authentication identity |
| SH-043 `resolveNotificationRecipients` | Notification routing + source owner | typed recipient descriptor | owner-issued User IDs/routing metadata plus Notification dedupe result | Organization membership, participant lifecycle, source authorization policy |
| `evaluateNotificationEligibility` | Notification internal routing | resolved User/channel/sensitivity/reachability + external gate facts | allow/skip/deny with local reason code | underlying consent or owner policy truth |
| `getNotificationDeliveryState` | authorized admin/support or legitimate source caller | Notification/delivery reference | canonical Delivery evidence, safe failure reason, aggregate reason once approved | user attention or source business success |
| SH-096 `enumerateSubjectData` | Privacy | subject/cursor | stable target descriptors, supported dispositions, retention candidates/export facts | legal retention decision or Privacy completion |
| SH-097 `evaluateRetentionRequirement` | Privacy | subject/owner target and approved policy context | owner retention facts under SH-097 | exemption creation or final Privacy completion |
| SH-062 `reconcileProviderState` report/query | authorized ops/admin | provider/time window/cursor/dry-run | discrepancy report and approved repair results | provider state as source business truth |

### Stable local reason-code families

Public interfaces should return stable, owner-local categories rather than raw provider errors. At minimum design reason-code namespaces for:

- request validation;
- target/recipient resolution;
- channel unavailable/skipped;
- template/version/variable invalid;
- payload blocked by sensitivity policy;
- action route invalid;
- permission/consent/reachability unavailable;
- lifecycle conflict/stale transition;
- provider unavailable/unmapped/permanent destination failure;
- privacy retained/skipped/retryable/terminal result.

The exact codes should be defined with the implementing feature and versioned as public-contract behavior.

---

## 12. Public Module Interface

### Public commands

- SH-041 `requestNotification`
- `markNotificationRead`
- `dismissNotification`
- `recordNotificationInteraction`
- `recordNotificationPermissionState`
- `recordServiceWorkerRegistrationState`
- `upsertPushSubscription`
- `refreshPushSubscription`
- `revokePushSubscription`
- `handlePushSubscriptionChange`
- `recordPwaInstallReadiness`

### Public queries

- `listNotifications`
- `getUnreadNotificationCount`
- `listNotificationSubscriptions`
- finalized delivery-state query after delivery semantics are approved

### Shared/owner recipient contract

- SH-043 `resolveNotificationRecipients` — shared request/result contract. Source owner returns its own recipient relationship facts; Notification deduplicates/fans out and applies channel policy.

### Privacy executor

- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement` — owner-side retention query
- SH-095 `executePrivacyInstruction`
- export serializer in Privacy-defined format where required

### Provider-facing interfaces owned by Notification

Provider-neutral ports only:

- email delivery port;
- SMS delivery port;
- Web Push delivery port;
- provider callback parser/status-mapper interface;
- reconciliation adapter interface where supported.

Provider-specific SDK/types must not leak through the public business interface.

### Emitted domain events

No binding Notification integration-event catalog is defined by the current Cluster architecture. The root overview includes an illustrative `notification.delivered` name, but no authoritative payload/version/emission contract is supplied here. If Notification events become required, define them explicitly and publish through SH-046 `publishDomainEvent`; do not invent event names in implementation code and do not treat provider callbacks as domain events.

---

## 13. Inbound Dependencies

| Owning Module/capability | Interface consumed | Why required | Minimum information | May block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor for protected commands/queries | actor ID/type, session assurance, safe request context | yes | session/user-current helpers, OTP/recovery lifecycle |
| Role / Authority | SH-002 `authorizeResourceAction` | permission for view/read/dismiss/device/admin actions | action, Notification-owned ownership/recipient/subscription facts | yes | permission engine/RBAC interpretation |
| Consent & Disclosure | SH-008 `queryConsentProof` | required disclosure proof for production push onboarding/use where policy requires | proof ID/type/version/acceptedAt/validity | yes for consent-dependent action | ConsentLog table/service |
| Source workflow Modules | SH-003 `queryOwnerFacts` (Proposed ruling) or source-specific command/event contracts | validate source reference and recipient relationship without reading source repository | stable source ID/type, minimum recipient/relationship/sensitivity facts | yes/no-recipient | source repositories/lifecycle rules |
| Organization Hiring | `resolveOrganizationNotificationRecipientFacts` supporting SH-043 `resolveNotificationRecipients` | organization member/settings routing | concrete eligible User IDs + safe routing metadata | yes/no-recipient | OrganizationMember, OrganizationRole, OrganizationNotificationSetting logic |
| Healthcare / Regulated Services | approved safe-payload/view constraints where relevant | prevent unsafe sensitive output | classification/allow/redact/block or safe-payload contract, not PHI | yes for sensitive channels | healthcare policy |
| Privacy / Data Erasure | Privacy handler protocol | execute owner-local privacy targets | target/action/retention instruction/idempotency | yes for destructive action | PrivacyRequest/job/exemption lifecycle |
| Audit / Event Ledger | SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess` when policy requires | generic action/access proof | minimized actor/action/target/correlation facts | may fail closed if governing policy says proof mandatory | local AuditEvent/AccessAuditLog |
| Observability / Ops | request context, telemetry, failure, metrics, health interfaces | diagnose provider/queue failures safely | correlation + safe operational dimensions | no business block except explicit platform health policy | logging/metrics/IntegrationFailure systems |
| Shared queue/jobs | SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`, SH-038 `recordQueueTelemetry` | durable external work | owner job payload reference, idempotency, correlation | external delivery may be delayed/failed | notification-specific queue framework |
| Platform crypto | SH-075 `encryptSensitiveValue`, SH-076 `normalizeAndHashIdentifier` | protect push credential material | value/purpose/key metadata | yes for live credential storage | local encryption/hash helpers |
| Shared provider security | SH-059 `verifyProviderWebhookSignature`, validation primitive | authenticate callbacks | raw bytes/signature/timestamp/provider adapter config | yes | bespoke route verifier framework |

---

## 14. Outbound Consumers and Effects

### Primary consumers

- Messaging — requests safe new-message alerts after Message commit.
- Transaction / Order and Gig / Demand — request order/gig alerts while retaining business truth.
- Booking & Calendar / Video Session — request scheduling/session alerts.
- Organization Hiring / Candidate Application / Job Interview — request hiring alerts; Organization owner supplies routing facts.
- Trust Verification / Screening / Job Compliance — request FCRA-related notices while retaining legal workflow truth.
- Content Moderation & Legal Notice — request DMCA/moderation notices.
- Admin Review / Compliance Hold — request hold-created/released alerts without transferring hold state.
- Track Subscription & Entitlement — request plan/subscription/entitlement lifecycle alerts without transferring policy truth.
- Identity & Access — may request generic security/recovery alerts; Identity-owned verification-provider transport remains within Identity.
- Sweepstakes / Prize and Gamification / Rewards — request result/fulfillment alerts without transferring eligibility/tax truth.
- Users and authorized organization actors — consume Notification source truth through UI/queries.
- Privacy — consumes Notification privacy inventory/executor.
- Audit/Ops — consumes safe execution evidence, not Notification lifecycle ownership.

### Effects allowed

Notification may:

- create/update its own Notification, Delivery, Subscription, and SubscriptionEvent records;
- enqueue owner-local delivery work through shared queue infrastructure;
- invoke selected provider adapters;
- call generic audit/observability interfaces;
- revoke/delete provider-side Notification resources when instructed by Privacy or dead-token policy;
- emit approved versioned domain events if/when a binding contract is defined.

Notification may **not** update a source Module's business state as a side effect of sending, delivery, read, click, open, close, or provider failure.

---

## 15. Canonical Shared Operations Used

**Shared Operations status:** references marked **Proposed ruling** are planning dependencies only, not approval for shared schema/API commitment or a generic service. Independently justified owner-specific interfaces do not approve a proposed shared operation globally. Realtime remains post-commit, authorized, and rebuildable; Moderation integration consumes approved contracts. Canonical metadata and reusable boundaries remain controlled by the Shared Operations registry.

Use existing SH IDs and canonical metadata from `context/shared/shared-operations.md`. Notification-specific policy and invocation details below do not redefine reusable boundaries.

| Canonical operation | Canonical owner | Why Notification uses it | Invocation point | Notification-local policy | Prohibited duplicate examples | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | establish trusted actor | every user-facing command/query | requested Notification action/target | `notificationCurrentUser`, `notification-auth.ts`, `requireNotificationUser` | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | decide protected resource action | before view/read/dismiss/revoke/admin inspection | recipient/subscription ownership facts and action vocabulary | `notificationPermissions.ts`, local RBAC engine | Cross-cutting capability | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Each source Module | obtain minimal source/relationship facts | source validation and recipient resolution | only Notification-safe facts requested | cross-domain Prisma repositories | Shared contract; separate implementations | Proposed ruling |
| SH-008 `queryConsentProof` | Consent & Disclosure | check required push disclosure proof | push onboarding/use where policy requires | decide whether proof is sufficient for Notification action | `pushConsentService`, local ConsentLog query/table | Platform consent capability | Confirmed |
| SH-041 `requestNotification` | Notification | canonical intake owned here | source/Messaging post-commit alert request | routing, persistence, payload policy | feature-local `sendEmail`, `sendPush`, `dispatchWorkflowNotification` | Platform notification capability | Confirmed |
| SH-042 `renderNotificationTemplate` | Notification | centralized validated rendering | intake/delivery planning/worker | template variables, channel constraints, payload safety | per-Module HTML/email/push renderer | Cross-cutting capability | Confirmed |
| SH-043 `resolveNotificationRecipients` | Source context owner plus Notification | convert owner groups into concrete User IDs | intake/routing | dedupe/fan-out/channel eligibility | universal recipient repository; org role interpretation | Shared contract; separate policy | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | retries converge to one effect | request intake, read/dismiss, subscription mutation, privacy/callback apply | semantic key, conflict/replay behavior | local idempotency table/helper/framework | Platform primitive | Confirmed |
| SH-045 `deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox | prevent duplicate event-triggered alert effects | only approved event consumers | handler identity/effect | custom event dedupe framework | Platform primitive | Confirmed |
| SH-046 `publishDomainEvent` | Platform event/outbox infrastructure | publish approved Notification fact after commit | only when binding event contract exists | names/payload/privacy owned by Notification | fire-and-forget event bus | Platform primitive | Confirmed |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | durable async delivery/reconciliation | after authoritative write | job payload/completion semantics | `notificationQueue`, local DLQ engine | Platform primitive | Confirmed |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform infrastructure | bounded retry technical failures | provider delivery/callback/reconciliation | retryability classification | adapter-local retry loops | Platform primitive | Confirmed |
| SH-051 `acquireAggregateLock` / approved transactional equivalent | Shared persistence infrastructure | serialize conflicting owner operations if needed | delivery apply, subscription rotation, aggregate transition | lock key/conflict semantics | in-memory mutex | Platform primitive | Confirmed |
| SH-052 `withOptimisticConcurrency` | Shared persistence infrastructure | reject stale subscription/lifecycle updates where adopted | token rotation/admin updates | retry/merge/conflict behavior | ad hoc version checks scattered in routes | Platform primitive | Confirmed |
| SH-053 `transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy | reuse state-machine plumbing | Notification/Delivery/Subscription transitions | transition graph remains Notification-owned | generic status table owning Notification semantics | Shared mechanism; separate truth | Confirmed |
| SH-059 `verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm | authenticate callbacks | raw webhook edge before parse | provider algorithm/secret/tolerance | bespoke webhook verification route | Provider-adapter contract | Confirmed |
| SH-060 `deduplicateProviderEvent` | Provider-owning Module using shared primitive | replay-proof callback | after signature verification | Notification-owned event record/result | reuse ProcessedStripe/Calendar/Video event tables | Shared mechanism; separate truth | Confirmed |
| SH-061 `translateProviderStatus` | Provider-owning adapter | canonicalize provider outcome | sync provider response/callback | NotificationDelivery/Subscription mappings | global cross-domain provider-status mapper | Provider-adapter contract | Confirmed |
| SH-062 `reconcileProviderState` | Each provider-owning Module using shared worker framework | detect/repair missed provider effects | schedule/admin command | which discrepancies are safe to repair | global provider reconciler with Notification policy | Shared mechanism; separate policy | Confirmed |
| SH-066 `validateStructuredProviderOutput` | Shared validation primitive; consuming Module owns schema | validate callback/provider structured data | before owner state mutation | exact adapter schema and semantic checks | trusting provider JSON directly | Cross-cutting capability | Confirmed |
| SH-075 `encryptSensitiveValue` | Shared security/cryptography capability | encrypt recoverable push credentials | subscription create/refresh | which values require recovery/rotation | `notificationCrypto`, local AES helper | Platform primitive | Confirmed |
| SH-076 `normalizeAndHashIdentifier` | Shared security/cryptography capability | stable nonplaintext endpoint/token matching | subscription create/lookup/rotation | normalization purpose/domain separation | plaintext-only lookup / local hash helper | Platform primitive | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | important action proof | revocation/admin retry/privacy execution as policy requires | which actions merit generic audit | `NotificationAuditLog` | Platform audit capability | Confirmed |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | protected admin/device access where policy requires | sensitive inspection | safe target/purpose metadata | local access ledger | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` | Observability / platform infrastructure | correlation propagation | command entry and async worker | safe Notification labels only | local correlation ID framework | Platform primitive | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | remove sensitive fields | before logs/errors/audit metadata | Notification sensitivity allowlist | ad hoc redactors | Cross-cutting capability | Confirmed |
| SH-037 `recordIntegrationFailure` | Observability / Ops | normalized provider/worker failure | provider/queue degradation | Delivery truth remains local | `NotificationFailure` replacing domain status | Cross-cutting capability | Confirmed |
| SH-038 `recordQueueTelemetry` | Observability / Ops / queue infrastructure | worker attempt/retry/DLQ evidence | every async job | owner completion remains Delivery truth | custom queue ledger | Cross-cutting capability | Confirmed |
| SH-035 `captureException` / SH-036 `emitMetric` / SH-039 `checkServiceHealth` | SH-035: Observability / Ops<br>SH-036: Observability / Ops<br>SH-039: Observability / Ops coordinates; owner supplies check | safe monitoring | provider/worker/API boundaries | safe dimensions/health semantics | provider-specific logging stacks | SH-035: Provider adapter<br>SH-036: Platform capability<br>SH-039: Cross-cutting capability | SH-035: Confirmed<br>SH-036: Confirmed<br>SH-039: Confirmed |
| SH-096 `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | privacy inventory | Privacy orchestration | Notification target definitions/dispositions | global Privacy DB crawler | Cross-cutting protocol | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | return owner facts for retention decision | privacy planning | only factual retention context | local exemption decision/table | Cross-cutting protocol | Confirmed |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | apply disposition locally | Privacy target execution | Notification field/provider mutation | local PrivacyRequest workflow | Cross-cutting protocol | Confirmed |

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `evaluateNotificationEligibility` | combine Notification-owned channel/reachability policy with externally supplied gate facts | resolved User, channel, sensitivity, subscription, consent result, source requirements | allow/skip/deny + local reason | none until accepted write | channel eligibility is Notification transport policy |
| `validateNotificationActionRoute` | enforce approved authenticated route contract | template key, route params, requested destination | safe internal/HTTPS action route or rejection | none | Notification owns outward navigation safety |
| `shapePrivacySafePayload` | ensure only minimum safe content enters channel payload | rendered content, channel, sensitivity | safe payload | Notification rendered snapshot | outward transport minimization is Notification policy |
| `planNotificationDeliveries` | create eligible channel attempt plan | Notification truth + reachability/channel policy | delivery plan | future Delivery rows | source Modules must never create Delivery rows |
| `enqueueNotificationDeliveries` | persist/enqueue owner work after truth exists | Notification/Delivery refs | queue job refs | Delivery queued state | owner job semantics are Notification-specific |
| `dispatchNotificationDelivery` | execute one planned attempt | Delivery ID | normalized result | Delivery | provider transport is Notification-owned |
| `recordProviderDeliveryResult` | apply normalized outcome safely | Delivery ID + provider result | updated Delivery/subscription health | Delivery/Subscription | mapping and lifecycle policy are local |
| `disableDeadNotificationSubscription` | stop future use of provider-confirmed dead reachability | Subscription ID + evidence | disabled/revoked local state + event | Subscription/Event | dead-token policy belongs to Notification |
| `expireNotification` | prevent stale send and record approved expiry outcome | Notification/Delivery ref, clock | approved expired/skipped representation | Notification/Delivery | blocked until U-CL07-12 ruling |
| `reduceNotificationAggregateStatus` | deterministically derive parent state from attempts | Notification + attempts | canonical aggregate state/reason | Notification | blocked until U-CL07-10/11/13/15 rulings |
| `mapNotificationInteraction` | apply click/open/close evidence to canonical record | validated interaction | evidence write | Notification/Delivery/Event | blocked for full canonicality by U-CL07-19 |
| `reconcileNotificationProviderState` | compare provider and local delivery truth | provider cursor/time window | discrepancies + safe repair commands | Delivery/Subscription | repair policy remains Notification-owned |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Idempotency:** reuse SH-044 `executeIdempotentCommand`; Notification defines request/subscription/callback semantic identity and stores its own effect.
2. **Queueing/retry:** reuse queue/retry infrastructure; `NotificationDelivery` remains transport truth and queue/DLQ telemetry remains operational evidence without assuming a QueueJob table.
3. **Provider webhook dedupe:** reuse atomic dedupe mechanics; Notification requires its own processed-provider-event truth if callbacks are enabled. Never reuse `ProcessedStripeEvent`, `ProcessedCalendarEvent`, or `ProcessedVideoProviderEvent`.
4. **Provider status translation:** reuse provider-port/result envelope shape; Notification maintains its own mapping table/version to Notification statuses.
5. **Lifecycle plumbing:** shared transition helper may enforce compare/update/event hooks; Notification owns its status graph and reason semantics.
6. **Cryptography:** use central encryption/HMAC; Notification owns which credential values exist, are recoverable, rotate, and are erased.
7. **Audit:** generic AuditEvent/AccessAuditLog stay Audit-owned; Delivery and SubscriptionEvent remain separate Notification domain evidence.
8. **Privacy:** shared handler protocol; Privacy owns request orchestration and exemptions; Notification owns local mutation execution.
9. **Recipient resolution:** shared request/result contract; each source owner retains relationship truth; Notification performs final dedupe/fan-out/routing.
10. **Reconciliation:** shared cursor/dry-run/worker pattern; Notification alone decides safe repairs to Notification truth.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

Every user-facing Notification command/query begins with SH-001 `resolveAuthenticatedActor`. Client-supplied `userId`, `organizationId`, subscription ID, or provider token is a reference, never proof of authority.

### Role / Authority use

Call SH-002 `authorizeResourceAction` for protected actions such as:

- `notification.list` / `notification.read` / `notification.dismiss`;
- `notification.subscription.list` / `notification.subscription.revoke`;
- admin/support delivery inspection;
- manual retry/reconciliation actions;
- privacy/sensitive administrative access where an interactive actor is involved.

Notification supplies contextual facts:

- targeted `userId` relationship;
- subscription `userId` ownership;
- organization target/reference where applicable;
- sensitivity;
- requested action;
- safe source reference if needed.

Role / Authority interprets permission. Notification must not implement independent role matrices.

### RLS

RLS is defense in depth. It must agree with server-side Role / Authority decisions for User-target Notification and User-owned Subscription access. RLS must not become a separate business-policy engine.

### Organization context

Notification does not interpret `OrganizationRole`. Organization Hiring exposes `resolveOrganizationNotificationRecipientFacts` as its owner-specific public query supporting SH-043 `resolveNotificationRecipients`. It accepts an Organization-scoped notification context, evaluates Organization-owned membership and `OrganizationNotificationSetting` facts, and returns eligible concrete User IDs plus only safe routing facts. An empty eligible-recipient set is valid; unavailable and unauthorized results are distinct from that empty result. Notification consumes the result, deduplicates recipients, applies its own reachability/channel eligibility, and performs fan-out. Notification must not reconstruct Organization role/settings policy from raw tables. Role / Authority controls any organization-admin action.

### Admin/support

Admin/support does not imply unrestricted access to sensitive payloads or raw provider credentials. Delivery inspectors must redact content/secrets and may require sensitive-access proof according to governing policy.

### Step-up

No ordinary Notification action currently has a binding step-up requirement. If root/Identity policy declares an admin/device/security action sensitive enough, consume SH-014 `requireStepUpForSensitiveAction`; do not add local MFA.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate/proof | Underlying owner | Notification action gated | Local composition |
| --- | --- | --- | --- |
| Authentication | Identity & Access | protected User/admin commands/queries | require trusted actor before authorization |
| Permission | Role / Authority | read/dismiss/revoke/inspect/retry | provide Notification facts; obey allow/deny |
| Push disclosure consent | Consent & Disclosure | production push onboarding/use where required | SH-008 `queryConsentProof`; Notification decides if channel may proceed |
| Browser permission | Notification | push subscription activation/delivery | active subscription path requires observed granted permission |
| Reachability | Notification | Web Push route eligibility | use active Subscription; do not equate with consent |
| Healthcare/sensitivity constraint | Healthcare / source owner | outward safe payload / sensitive admin handling | consume safe decision/facts; fail closed when required |
| ComplianceHold | Admin Review / Compliance Hold | only if source/owner declares communication action gated | consume owner decision; never local `isBlocked` |
| FCRA/DMCA notice requirement | screening/legal owner | notice delivery | Notification transports after owner request; never decides legal need/deadline |
| Security/recovery/MFA state | Identity & Access | generic security/recovery alert delivery; Identity verification protocol remains external | Identity owns challenge/token and verification-provider transport; Notification only records its own generic alert delivery |
| Entitlement | Track Subscription & Entitlement | no general Notification gate confirmed | entitlement changes may trigger alerts; no local premium flags |

Urgent priority never bypasses privacy, authorization, consent, permission, or source-owner policy.

---

## 20. Provider Integrations

### 20.1 Provider-neutral port

```text
Notification application service
→ provider-neutral channel port
→ selected adapter
→ external provider
→ validated normalized ProviderResult
→ Notification-owned translation/application
```

The provider port should expose only normalized inputs/outputs required by Notification, not vendor SDK types.

### 20.2 Email

**Architecture Ruling:** CL-07 treats AWS SES as the current Workin Ants email transport where root provider configuration confirms it, while keeping an email provider-neutral port. Historical registry text that lists AWS SES as “compliance” is classification noise; the provider is infrastructure, not compliance proof.

### 20.3 SMS

**Approved SMS ownership boundary (CL-07-R002):** generic business SMS alerts use Notification through SH-041 `requestNotification`; source Modules must not dispatch generic SMS directly. Identity & Access may use an Identity-owned verification provider whose protocol delivers an OTP or challenge. Identity retains challenge generation, expiry, attempts, verification outcome, assurance result, and provider protocol truth. Notification must not independently generate, validate, resend, or implement a parallel OTP/MFA transport/verification workflow. This verification-provider transport is not a second generic notification rail. Only initial production generic SMS provider selection remains unresolved under U-CL07-16.

### 20.4 Web Push

**Unresolved U-CL07-17:** schema/evidence lists Web Push, FCM, OneSignal, and WonderPush, but no single production MVP adapter is selected. Implement the port; enable only an approved adapter.

### 20.5 AWS Lambda note

The registry/Project Overview mentions “AWS Lambda for notifications” / a developer override note. Canonical CL-07 architecture requires shared reliable queue/worker infrastructure and does not make Lambda-specific code a Notification domain concern. If the platform worker runtime is deployed on Lambda, that is a platform/deployment implementation detail behind the shared worker mechanism, not Notification source truth or a reason to build a Module-local Lambda framework.

### 20.6 Credentials

- provider secret credentials remain server-side and outside client responses;
- push subscription endpoint/token/key material follows PR-N04/U-CL07-18 before production storage;
- use SH-075 `encryptSensitiveValue` and SH-076 `normalizeAndHashIdentifier`;
- never log raw endpoints/tokens/auth keys;
- VAPID public material may be client-safe only as designed; private keys remain server-only.

### 20.7 Webhooks

For any callback-capable provider:

1. read raw bytes;
2. verify signature/timestamp through SH-059 `verifyProviderWebhookSignature` before parsing/state mutation;
3. validate structured envelope;
4. atomically dedupe through shared mechanism using Notification-owned event truth;
5. map provider IDs to Delivery/Subscription;
6. SH-061 `translateProviderStatus`;
7. idempotently apply allowed local transition;
8. record safe operational evidence;
9. mark processed-event result.

**Unresolved U-CL07-14:** exact Notification processed-provider-event schema is not yet approved.

### 20.8 Reconciliation

Where provider APIs support readback, use SH-062 `reconcileProviderState` through a Notification-owned reconciliation service. Repairs may change only Notification-owned truth and only when the discrepancy is safe/approved. Reconciliation must not mutate Order, Job, Booking, Message, or other source state.

### 20.9 Provider status/error translation

- explicit mapping table/version per adapter;
- normalized retryability and safe error category;
- unknown provider values become unsupported/unmapped/manual-review/operational failure, never success;
- current `NotificationSubscriptionProvider` is push-specific and must not be falsely used to label email/SMS providers (U-CL07-15).

---

## 21. Events and Outbox

### Binding position

No complete Notification-owned integration-event catalog is currently approved. Events describe facts that occurred; they must not be disguised commands to another Module.

### If/when Notification emits domain events

Use canonical SH-046 `publishDomainEvent` with:

- stable `eventId`;
- `eventType` and schema version;
- source Module `notification`;
- aggregate type/ID/version where available;
- occurred time;
- correlation/causation IDs;
- safe actor/system context;
- privacy classification;
- minimized payload.

The event must be emitted transactionally with the Notification-owned state change through the platform outbox. Consumers use canonical inbox/deduplication.

### Provider callbacks are not domain events

A provider callback becomes usable Notification evidence only after signature verification, deduplication, validation, translation, and owner application.

### Source events consumed

Notification may consume source Module domain events only where the source Module has an approved event contract. CL-07 must not invent source event names. Direct SH-041 `requestNotification` remains the safe default boundary.

### Payload minimization

Event payloads must not carry private source body content, PHI, OTP/recovery token, raw resume, financial/tax detail, contract text, or provider credentials.

---

## 22. Background Jobs / Scheduled Work

### 22.1 Delivery worker

- **Purpose:** execute one Notification Delivery attempt.
- **Input:** stable Notification/Delivery reference; no unnecessary content duplication in queue payload.
- **Owner:** Notification; shared queue provides execution mechanics.
- **Idempotency:** Delivery/attempt identity under current approved model.
- **Retryable:** provider timeouts, throttling, transient network/provider failures when adapter marks retryable.
- **Permanent:** invalid destination, blocked payload, unsupported provider/status, revoked subscription.
- **Dead-letter:** shared DLQ/ops visibility after bounded attempts; Delivery remains truthful.
- **Truth updated:** NotificationDelivery; Subscription health when authoritative evidence supports it.
- **Telemetry:** correlation, queue attempt, latency, safe status/error category; no payload secrets.

### 22.2 Dead-subscription cleanup worker

- **Purpose:** apply disable/revoke state to provider-confirmed dead endpoints/tokens.
- **Idempotency key:** Subscription ID + evidence/event identity.
- **Rule:** provider evidence must be authoritative enough under adapter policy; do not infer dead state from arbitrary client errors.

### 22.3 Expiry worker

- **Purpose:** prevent stale queued notifications from sending after approved cutoff.
- **Blocker:** U-CL07-12 must define expiry representation and transition semantics before production worker exits.
- **Clock:** use injectable/controlled time in tests.

### 22.4 Reconciliation worker

- **Purpose:** compare local Delivery/Subscription truth to supported provider state.
- **Input:** provider/time window/cursor/dry-run.
- **Retry:** shared retry; discrepancy repair is owner-local/idempotent.
- **Manual review:** unsafe/unmapped discrepancies produce ops evidence/incident, not guessed repair.

### 22.5 Provider callback follow-up jobs

Only for callback providers and only after U-CL07-14. Callback processing is replay-safe and may queue owner-local follow-up/reconciliation work.

Generic queue scheduling, leases, heartbeat, backoff, DLQ, metrics, and worker hosting are shared infrastructure and must not be implemented in this Module.

---

## 23. Concurrency and Idempotency

### 23.1 Notification intake

- semantic key is supplied/derived under SH-041 `requestNotification` contract;
- use SH-044 `executeIdempotentCommand` so duplicate retries return/replay the original effect;
- do not rely solely on frontend request suppression;
- if source events are consumed, additionally use SH-045 `deduplicateDomainEvent` keyed by event ID + handler/version.

### 23.2 Read/dismiss

- only owner-valid transitions;
- repeated identical command returns current result;
- stale conflicting transitions return deterministic conflict/current-state result rather than silently regressing state.

### 23.3 Subscription upsert/rotation

- match using approved nonplaintext hash identity;
- one active semantic subscription per approved identity after U-CL07-18 migration;
- stale refresh must not overwrite newer credential material;
- use transaction/constraint plus optimistic or aggregate locking as root standards dictate;
- no in-memory locks.

### 23.4 Delivery workers

- one worker claim per Delivery/attempt through queue lease/idempotency;
- provider request idempotency should be used when provider supports it;
- replay after process crash must not create duplicate semantic alert or lose attempt truth.

### 23.5 Provider callback

- provider event uniqueness is Notification-owned truth using shared dedupe mechanics;
- callback and synchronous provider result may race; transition policy must converge on one valid canonical state;
- duplicate callback produces no duplicate side effect.

### 23.6 Expiry race

Worker must check authoritative expiry immediately before external side effect under approved lifecycle rules. A queued item that becomes expired must not deliver after the approved cutoff.

### 23.7 Current unresolved constraints

Do not add speculative lock/version/attempt columns until the related architecture ruling approves the required schema. Use current schema and safe limited behavior for earlier slices.

---

## 24. Media / Storage

Notification has no attachment model in current evidence.

Rules:

- do not attach MediaAsset bytes or permanent file URLs directly to email/SMS/push by bypassing Media / File Access;
- use an authenticated `actionUrl` to the owning application context for private files/content;
- if a future Notification attachment requirement is approved, business attachment meaning and Media file mechanics must remain separate and receive a specific architecture ruling;
- no raw object key/storage credential belongs in Notification payload or telemetry.

---

## 25. Search / Projection

Notification has **no public Search responsibility**.

- `Notification`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` are private operational/user records.
- ordinary Notification lifecycle changes do not create `SearchUpsertEvent`.
- Typesense/public Search must not index Notification or device/subscription data.
- unread counts are a Notification query, not Search projection.
- any future private notification search requires a separate authorized projection design; do not reuse public-search assumptions.

---

## 26. Notification

Because Notification is the Target Module, this section states its trigger/content contract rather than delegating delivery elsewhere.

### Source trigger contract

The source Module owns:

- whether an alert should exist;
- what source event/decision it represents;
- source-safe recipient relationship descriptor;
- business/legal semantic meaning;
- safe variable values;
- approved next-action context.

Notification owns:

- validating the canonical request;
- target resolution/fan-out using owner facts;
- template/channel rendering;
- outward payload safety;
- channel/reachability eligibility;
- Notification/Delivery persistence;
- provider dispatch and status normalization;
- Subscription lifecycle and dead-token handling.

### New-message trigger

Messaging calls SH-041 `requestNotification` only after Message commit, with safe metadata. Notification must not fetch private Message body inside the delivery transaction. Notification failure never rolls back Message truth.

### Safe action intent

External alert content should normally tell the User that an action/update exists and route into the authenticated Workin Ants application, where the source owner can authorize and render the true details.

---

## 27. Audit and Sensitive Access

### Domain evidence

- `NotificationDelivery` remains delivery-attempt truth.
- `NotificationSubscriptionEvent` remains device/subscription evidence.
- Notification read/click timestamps remain Notification truth where modeled.

These must not be collapsed into AuditEvent.

### Generic audit

Use SH-029 `appendAuditEvent` for actions requiring generic proof, such as:

- device/subscription revocation when root security policy requires it;
- admin/manual delivery retry or reconciliation repair;
- privacy execution acknowledgement;
- other security-sensitive administrative changes defined by Audit policy.

### Sensitive access

Use SH-030 `recordSensitiveAccess` when governing Audit/Healthcare policy says viewing sensitive notification failure/device metadata or related private content requires access proof.

### Prohibitions

Do not create `NotificationAuditLog`, mutable “last admin viewed” flags, or a Notification-local `AccessAuditLog` substitute.

---

## 28. Privacy and Retention

### Subject-data inventory

Notification-held subject data may include:

- User/Organization target references;
- source references;
- title/body/payload/action route snapshots;
- read/click/interaction timestamps;
- provider message IDs and safe failure metadata;
- push subscription provider/platform/device/user-agent metadata;
- encrypted endpoint/token/key material and hashes;
- permission/service-worker/PWA metadata;
- SubscriptionEvent IP hash/user-agent/device metadata.

### Privacy executor

Notification must expose:

- SH-096 `enumerateSubjectData` — stable target descriptors, supported dispositions, sensitivity, retention candidates, provider references, export serializer facts;
- SH-095 `executePrivacyInstruction` — exact owner-approved erase/anonymize/revoke/retain/export/detach behavior with explicit result and idempotency.

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

### Provider resources

When Privacy instructs deletion/revocation and the provider supports it, Notification calls its own provider adapter or canonical provider-resource deletion mechanism. Provider failure returns a retryable/terminal result to Privacy; it does not mark the PrivacyRequest complete.

### Retention

Notification exposes owner-side SH-097 `evaluateRetentionRequirement` for factual retention evaluation. Privacy owns `DataRetentionExemption` and the final retention/legal decision. No statutory period is invented here.

### Current gap

Notification does not currently have dedicated `erasedAt` fields. Field-level erase/anonymize/delete/retain semantics must be explicitly defined by the Privacy instruction and approved retention policy before destructive production execution.

---

## 29. Observability

Every Notification API/worker/provider path should have:

- request/correlation/trace IDs;
- structured safe logs through SH-033 `writeStructuredLog`;
- queue depth/lag/attempt/retry/DLQ telemetry;
- delivery latency and canonical outcomes;
- subscription failure/dead-token metrics;
- callback verification/dedupe outcomes;
- provider availability/timeout/error-rate metrics;
- SH-037 `recordIntegrationFailure` for meaningful provider/worker degradation through the public capability;
- health checks for enabled provider adapters and worker dependencies;
- exception capture through the single approved monitoring adapter.

**CL-07-R007 — Observability persistence boundary:** CL-07 consumes approved public capabilities for failure recording, queue telemetry, health, structured logging, metrics, and exception capture. `IntegrationFailure`, `QueueJob`, `OpsIncident`, and `SystemEvent` are not current Prisma models. CL-09 owns its unresolved persistence/status design. CL-07 must not create local substitutes or couple Messaging/Notification business status to any future operational record.

### Safe dimensions

Prefer provider adapter key, channel, canonical status, safe failure category, template key/version, environment, queue name, and bounded latency buckets. Avoid user-level high-cardinality metrics unless explicitly approved.

### Redaction

Never put private Message bodies, PHI, OTPs/recovery tokens, raw endpoints/tokens/keys, tax/financial details, resumes, contract text, identity documents, or raw unnecessary provider payloads into generic telemetry.

Operational records do not replace Notification status or Delivery truth.

---

## 30. Security Boundaries

1. Runtime-validate every command, query input, client callback, template variable set, action route, provider response, and webhook body.
2. Resolve authenticated actor server-side; never trust client `userId` as authority.
3. Call Role / Authority for protected resource actions; align RLS as defense in depth.
4. Never use a push token/endpoint as authentication.
5. Enforce approved encrypted/hash credential storage; do not keep plaintext and encrypted values as competing truths.
6. Raw provider credentials and secret VAPID material remain server-only.
7. Outward action routes are approved authenticated Workin Ants routes; external arbitrary redirects are prohibited.
8. External payloads use minimum safe data and fetch source truth after authentication.
9. Webhook signatures/timestamps are verified before parsing or side effects.
10. Callback replay protection is mandatory.
11. Provider result/status is runtime validated and explicitly mapped; unknown means unsupported/unavailable, not success.
12. Rate-limit abuse-prone notification intake and permission/subscription mutation according to root policy.
13. Admin/support delivery inspectors redact content, endpoints, tokens, keys, PHI, and other secrets.
14. Notification must not fetch private Message or resume content merely to render an alert.
15. No local cryptography, auth, or authorization helper may bypass the canonical platform operation.

---

## 31. Error / Decision Result Pattern

Public Module interfaces should use a stable result envelope consistent with the Canonical Shared Operations architecture.

### Command/decision categories

At minimum:

- `allowed` / `accepted`
- `denied`
- `skipped`
- `conflict`
- `unavailable`
- `retryable_failure`
- `terminal_failure`

Where a general shared DecisionResult package is adopted, use its standard allow/deny/warning/review/step-up/unavailable categories without transferring Notification policy ownership.

### Result fields

Use only fields relevant to the operation, such as:

- stable reason code;
- human-safe explanation;
- Notification/Delivery/Subscription reference;
- evidence references;
- evaluated/occurred time;
- retryability;
- remediation/next action;
- correlation ID.

### Provider result envelope

Provider-facing adapters return normalized fields such as:

- adapter/provider key and adapter version;
- safe provider request/message/event reference;
- canonical status/result;
- retryability;
- safe error category/code;
- occurred/received time;
- mapping version;
- correlation ID;
- payload hash only where justified.

Raw provider payloads/errors must not leak to business consumers.

---

## 32. Testing Architecture

### Domain unit tests

- request validation and semantic idempotency identity;
- recipient resolution/dedupe;
- channel eligibility;
- template variable schemas and version lookup;
- payload sensitivity/allowlist behavior;
- action-route allowlist;
- Notification/Delivery/Subscription transition matrices;
- permission/status consistency;
- stale token rotation behavior;
- provider status mapping and unknown status;
- aggregate status only after ruling approval.

### Public contract tests

- SH-041 `requestNotification` with Messaging and representative source Modules;
- Organization recipient-facts contract;
- SH-008 `queryConsentProof` boundary;
- Role authorization using Notification-owned facts;
- Privacy enumeration, SH-097 `evaluateRetentionRequirement`, and execution protocol;
- provider-port normalized result contract.

### Database/integration tests

- create/list/read/dismiss/count;
- RLS cross-user denial;
- subscription upsert/refresh/revoke without secret exposure;
- unique/hash migration behavior once approved;
- Notification intake duplicate/concurrent behavior;
- Delivery worker persistence under crash/replay;
- callback dedupe concurrency;
- expiry race;
- migration/backfill fixtures.

### Authorization tests

- User A cannot view/mutate User B Notification/Subscription;
- organization recipient routing honors owner-returned facts only;
- admin/support access is explicit and redacted;
- RLS and server Role decisions agree.

### Compliance tests

- consent proof remains separate from browser permission;
- active push subscription cannot be created through application path without granted permission;
- DMCA/FCRA delivery proof never mutates legal workflow state;
- generic security/recovery alert delivery never mutates Identity truth or implements a parallel OTP/MFA transport/verification workflow;
- private Message body/PHI/OTP/financial/tax/resume/contract fixtures are rejected from unsafe outward channels.

### Provider adapter tests

- adapter contract success/failure;
- transient/permanent retry classification;
- signature verification/replay/timestamp failure;
- unknown provider status;
- provider-invalid-token result causes only approved Subscription health transition;
- reconciliation dry-run and safe repair boundary.

### Privacy tests

- enumerate all representative Notification subject records;
- export excludes secrets;
- erase/anonymize/revoke/retain behavior is idempotent;
- provider deletion failure returns to Privacy correctly;
- Notification never completes overall PrivacyRequest;
- no direct Privacy mutation of Notification repository in integration test.

### E2E participation tests

1. Message commit → safe in-app alert → click authenticated Thread; Message remains source truth.
2. User grants browser permission → push subscription is stored safely → receives approved test alert → revokes device.
3. Provider fails transiently → shared retry occurs → Delivery evidence remains correct → source workflow remains intact.
4. Organization Hiring alert resolves recipients through Organization owner facts and leaks no resume details.
5. Privacy instruction removes/revokes approved Notification data without creating a local privacy workflow.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Notification`, `NotificationDelivery`, `NotificationSubscription`, and `NotificationSubscriptionEvent` have one owner: Notification.
2. The source business event that caused an alert remains owned by its source Module.
3. A Message is not a Notification and must never be generalized into one persisted Communication record.
4. Source Modules must call SH-041 `requestNotification`; they must not write Notification tables directly.
5. Source Modules must not call generic Notification providers directly; Identity-owned OTP/challenge verification-provider transport is the explicit Section 20.3 exception.
6. Notification must never mutate Order, Gig, Booking, Job, Application, Interview, Message, ComplianceHold, ModerationCase, FCRA, DMCA, Subscription/Entitlement, Prize/Reward, or security/recovery lifecycle truth because delivery succeeded or failed.
7. Provider state is not Notification truth until validated, normalized, and applied by Notification.
8. Delivery success is not proof of User attention.
9. Click/open/close is not proof of source workflow completion.
10. ConsentLog proof, browser permission, Subscription reachability, Delivery evidence, and interaction evidence remain separate facts.
11. An active Web Push subscription cannot be created through the application path without observed granted permission.
12. A push endpoint/token may never be used as authentication.
13. Raw push endpoint/token/key values must never appear in account responses or generic logs.
14. Production credential storage must not keep plaintext and encrypted/hash values as competing authoritative truths.
15. `NotificationSubscriptionProvider` must not be used as a false email/SMS provider vocabulary.
16. Private Message bodies, PHI, OTP/recovery tokens, financial/tax details, resume details, identity documents, contract text, and raw provider credentials must not enter unsafe outward payloads or generic telemetry.
17. Notification action routes must use the approved authenticated route contract; arbitrary external redirects are prohibited.
18. Organization membership/settings remain Organization Hiring truth; Notification consumes owner-resolved recipient facts.
19. Notification must not interpret `OrganizationRole` to decide organization recipients.
20. Identity owns OTP/recovery challenge and verification-provider protocol truth, including provider transport. Notification must not independently generate, validate, resend, or implement a parallel OTP workflow.
21. Legal/FCRA/DMCA owners decide notice requirement/content/deadlines; Notification only records delivery evidence.
22. Track Subscription & Entitlement remains commercial-policy truth; no `isPremium`, `canNotify`, or local entitlement boolean may be introduced.
23. Privacy / Data Erasure owns orchestration and retention exemptions; Notification executes only its own targets.
24. Generic AuditEvent/AccessAuditLog remain Audit-owned; Delivery/SubscriptionEvent remain Notification evidence.
25. Public failure/queue telemetry capabilities provide operational evidence and never replace Delivery status; no Ops Prisma table is assumed.
26. Notification generates no public Search projection for ordinary lifecycle state.
27. Provider callbacks authenticate before parsing/state mutation and dedupe before side effects.
28. Notification uses its own processed-provider-event truth if callbacks are enabled; no reuse of Stripe/Calendar/Video event ledgers.
29. Shared idempotency, queue, retry, webhook, crypto, request-context, audit, and observability infrastructure must not be rebuilt locally.
30. Notification intake, subscription mutations, provider callbacks, and privacy execution are semantically idempotent.
31. Token refresh/rotation cannot allow stale state to overwrite newer valid credentials.
32. In-memory locks are prohibited for database-owned concurrency.
33. Expired notifications may not be sent after the approved cutoff once expiry semantics are implemented.
34. Retry history may not be silently destroyed once the approved attempt model is implemented.
35. Unresolved decisions U-CL07-09 through U-CL07-21 must not be settled inside feature code without an architecture update.
36. PR-N04 target credential authority is approved; its migration details remain U-CL07-18. PR-N01/02/03/05 remain non-binding until explicitly approved.
37. Provider-neutral ports may be implemented while unapproved production providers remain disabled/stubbed.

---

## 34. Prohibited Duplicate Implementations

Do not create any of the following as independent implementations inside Notification:

- `notification-auth.ts`, `notificationCurrentUser`, `requireNotificationUser`;
- `notification-permissions.ts`, `canReadNotification.ts`, local RBAC/role engine;
- `pushConsent`, `webPushConsent`, Notification-owned ConsentLog table/service;
- `organizationRecipientRepository` that directly queries/interprets OrganizationMember/OrganizationRole;
- `NotificationAuditLog` or Notification-specific generic access ledger;
- `NotificationFailure` used as a substitute for `IntegrationFailure` or Delivery truth;
- `notificationQueue`, custom worker framework, custom retry scheduler, custom dead-letter system;
- local `withIdempotency`, idempotency database/table parallel to canonical platform infrastructure;
- local encryption/hash/KMS helpers such as `notificationCrypto`, `hashPushToken`;
- global provider-status mapper shared with Payment/Calendar/Video/etc.;
- reuse of `ProcessedStripeEvent`, `ProcessedCalendarEvent`, `ProcessedVideoProviderEvent`;
- source-specific `orderEmailService`, `bookingSmsService`, `jobPushService`, `messageFcmClient`;
- source-module generic-alert SES/Twilio/FCM/OneSignal/WonderPush SDK calls (Identity verification-provider protocol excluded);
- a generic `Communication` table merging Notification and Message;
- a mutable `NotificationTemplate` database lifecycle solely for convenience before such a lifecycle is approved;
- Notification-owned marketing campaign/newsletter/CRM system;
- private Notification Typesense/public-search indexer;
- Notification-owned global privacy crawler or PrivacyRequest/DataErasureJob tables;
- local `isBlocked`, `isPremium`, `canNotify`, `isConsented` booleans replacing owner decisions;
- a second device identity table solely for push;
- a second OTP/MFA challenge or recovery token implementation.

---

## 35. Unresolved Decisions

These are explicit architecture blockers. Do not guess.

| ID | Unresolved question | Blocks |
| --- | --- | --- |
| `U-CL07-09` | Canonical Notification recipient model for User vs Organization targets; exact cardinality/fan-out/snapshot behavior | organization-target routing and associated schema constraints |
| `U-CL07-10` | Is a Notification row channel-specific or a multi-channel parent? | production multi-channel semantics |
| `U-CL07-11` | How is aggregate Notification status derived across Delivery attempts? | final status reducer |
| `U-CL07-12` | How are expiry and dismissal time represented? | expiry worker and complete dismissal evidence |
| `U-CL07-13` | Does each retry create a new Delivery row; what correlates attempts? | preserved production retry history |
| `U-CL07-14` | What Notification-owned processed provider-event record is used? | async provider callback/reconciliation feature |
| `U-CL07-15` | What provider vocabulary truthfully represents email and SMS deliveries? | trustworthy provider reporting for enabled non-push channels |
| `U-CL07-16` | Initial generic SMS provider selection; Identity verification-provider ownership resolved by CL-07-R002 | production generic SMS alerts |
| `U-CL07-17` | Initial Web Push adapter/provider strategy | production Web Push |
| `U-CL07-18` | Exact provider/platform/hash uniqueness, backfill, rotation, constraint replacement and cutover implementing approved PR-N04 | live production credential migration/storage |
| `U-CL07-19` | Canonical click/open/close interaction record | normalized interaction evidence/analytics |
| `U-CL07-20` | Controlled Notification template-name catalog and version-governance rules | production source-template integrations |
| `U-CL07-21` | Exact allowed payload schema by sensitivity × channel | all production external delivery |

### Ruling status from CL-07 — PR-N04 target authority approved; other proposals remain unapproved

- **PR-N01 — Explicit fan-out:** SH-041 `requestNotification` accepts semantic intent and recipient/channel requirements; Notification performs fan-out. Source Modules never create Delivery rows.
- **PR-N02 — Prefer channel-specific Notification rows:** one row per resolved target/channel semantic alert; Deliveries are attempts for that channel; one request may create multiple Notifications.
- **PR-N03 — One Delivery row per attempt:** preserve retry history with attempt/correlation/idempotency fields.
- **PR-N04 — Approved target credential authority (CL-07-R010).** Production recoverable provider credential material uses approved encrypted storage through SH-075 `encryptSensitiveValue`; stable comparison/identity uses normalized purpose-bound hashes through SH-076 `normalizeAndHashIdentifier`. Plaintext `endpoint`, `token`, `p256dh`, and `auth` must not remain parallel authoritative representations after migration, and code must not treat plaintext and encrypted/hash values as equal source truth. U-CL07-18 remains unresolved for exact provider/platform/hash composite uniqueness, backfill, rotation during cutover, replacement order of plaintext uniqueness constraints, and any temporary compatibility period. This approval is not a migration design or permission to change current schema/constraints without separate review.
- **PR-N05 — Code-based template registry for MVP:** typed key/version, per-channel variable schemas, sensitivity, safe action routes; no mutable DB template lifecycle yet.

### Historical evidence conflicts that remain governed

1. Registry/overview lists AWS Lambda as notification infrastructure. CL-07 requires canonical shared queue/worker infrastructure; Lambda, if used, is hosting/deployment detail rather than Module architecture.
2. Project Overview says “AWS SES for Email and SMS,” while current CL-07 ruling treats SES only as current email transport where root configuration confirms it and leaves SMS unresolved.
3. Registry lists AWS SES/AWS Lambda among “compliance” items, but these are infrastructure choices, not proof records.

---

## 36. Architecture Decision Summary

### Binding decisions

1. Notification is the single owner of alert, delivery, push reachability, and Notification subscription-event truth.
2. Source Modules retain the event/business/legal meaning that causes an alert.
3. SH-041 `requestNotification` is the canonical generic alert intake; direct source-provider dispatch for generic alerts is prohibited. Identity-owned verification-provider transport follows the Section 20.3 exception.
4. Notification owns safe rendering, routing, delivery attempts/results, provider status translation, and dead-subscription handling.
5. Organization recipient relationships/settings remain Organization Hiring-owned; Notification consumes owner facts.
6. Consent proof, browser permission, reachability, delivery, and interaction remain separate evidence.
7. Identity owns MFA/recovery/security lifecycle and verification-provider transport. Notification may deliver generic security/recovery alerts; it must not independently generate, validate, resend, or implement a parallel OTP/MFA transport/verification workflow.
8. Shared queue, idempotency, retry, events, webhook verification, crypto, audit, request-context, and observability operations are reused, not rebuilt.
9. Provider adapters remain behind Notification-owned provider-neutral ports.
10. Provider-native state is never business truth; unknown provider states fail safely.
11. Privacy owns request/orchestration/retention exemption; Notification exposes inventory, SH-097 `evaluateRetentionRequirement`, and execution over its own truth.
12. Audit and observability do not replace Notification lifecycle records.
13. Notification has no public Search responsibility.
14. Current Prisma constraints are honored until approved migrations change them.
15. Provider selection and Notification recipient/channel/retry/interaction/schema issues remain explicit unresolved decisions where listed.

### Safe implementation posture while decisions remain open

- implement User-target `in_app` Notification intake first;
- implement typed provider-neutral contracts/adapters without enabling unapproved production channels;
- do not introduce speculative schema fields/tables to solve U-CL07 decisions;
- explicitly disable/stub production generic SMS/Web Push paths until their provider-selection rulings are approved; Identity verification-provider ownership is already settled;
- stop a feature at its stated architecture blocker rather than inventing semantics.

---

## 37. Coding-Agent Usage

Before implementing or modifying Notification, the coding agent must read, in order:

1. [project overview V3](<../../../project-overview-v3.md>);
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry/Architecture;
5. [CL-07 architecture](<../messaging-notification-rail-architecture.md>);
6. [CL-07 build plan](<../messaging-notification-rail-build-plan.md>);
7. this [Notification architecture](<notification-module-architecture.md>);
8. [Notification implementation plan](<notification-module-implementation-plan.md>);
9. relevant public-interface sections for direct dependencies, especially Identity & Access, Role / Authority, Consent & Disclosure, Organization Hiring, Privacy / Data Erasure, Audit / Event Ledger, Observability / Ops, Healthcare / Regulated Services, Messaging, and the current source workflow owner;
10. `progress-tracker.md`.

Before coding a feature, also inspect the CL-07 Unresolved Decisions that gate it. If implementation discovers a real binding conflict, update architecture first and then the plan; do not let code silently become the new architecture.
