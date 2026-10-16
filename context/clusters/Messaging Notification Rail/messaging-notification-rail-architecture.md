# Messaging & Notification Rail Architecture

> **Cluster ID:** CL-07  
> **Cluster name:** Messaging & Notification Rail  
> **Cluster type:** cross-cutting communication rail  
> **Document status:** Target cluster architecture for the Workin Ants MVP; binding where marked Confirmed or Architecture Ruling, non-binding where marked Proposed Ruling, and intentionally incomplete where marked Unresolved Decision  
> **Audience:** coding agents, developers, reviewers, maintainers, and architecture reviewers  
> **Update rule:** change this file whenever a binding CL-07 ownership, lifecycle, contract, provider, privacy, or cross-Module decision changes. Build progress must not silently redefine this file.

---

## 1. Document Status and Scope

CL-07 coordinates two Deep Modules:

- `messaging` — Messaging Module
- `notification` — Notification Module

This Cluster is a planning, integration, and controlled-context boundary. It **does not own either Module's lifecycle truth** and does not create a third “communications” aggregate above them.

The root Workin Ants architecture remains authoritative for platform-wide identity, authorization, consent, entitlements, privacy, moderation, audit, observability, media, search, and provider-mechanism rules. The Prisma schema remains executable schema evidence. The Module architectures remain authoritative for Module-local policy. This Cluster document explains how Messaging and Notification collaborate with each other and the rest of Workin Ants without ownership leakage.

### Binding source-of-truth posture

1. `Thread`, `ThreadParticipant`, `Message`, and the contextual meaning of `MessageMedia` are Messaging truth.
2. `Notification`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` are Notification truth.
3. A business event that causes a conversation or alert remains owned by the source Module.
4. A Message is not a Notification, and neither may be generalized into one persisted “communication” record.
5. Provider delivery evidence is not business-event truth and is not proof of user attention.
6. Realtime transport is not Messaging truth; persisted PostgreSQL records are truth.
7. Consent proof, browser permission, reachability, and delivery are four separate facts.
8. Audit and observability record evidence about execution; neither replaces Messaging or Notification lifecycle records.

---

## 2. Cluster Purpose, Goal, and Transformation

### Purpose

Carry human conversation and system alerts across Workin Ants while preserving the business lifecycle that caused the communication.

### Goal

Provide one reusable conversation capability and one reusable notification-delivery capability so Order, Gig, Booking, Hiring, Verification, Moderation, Subscription, Security, Privacy, and other Modules do not create local chat tables, provider SDK integrations, delivery queues, push-token stores, or notification state machines.

### What enters the Cluster

```text
Authenticated actor context
+ owner-issued business context facts or notification intent
+ authorized participant / recipient facts
+ message text or validated safe template variables
+ optional MediaAsset references for messages
+ sensitivity / privacy classification
+ external policy decisions where required
+ correlation / idempotency context
```

### What leaves the Cluster

```text
Messaging path:
Thread
+ ThreadParticipant membership
+ Message
+ MessageMedia contextual joins
+ read cursor
+ authorized realtime change
+ notification request when appropriate

Notification path:
Notification
+ channel-specific delivery attempt(s)
+ provider-normalized delivery result
+ push subscription / permission / service-worker evidence
+ read/dismiss/click/open/close evidence where modeled
+ operational failure / audit evidence where applicable
```

### Major transformation

```text
Source-owned workflow event or actor conversation intent
→ communication eligibility and authority checks
→ Messaging or Notification authoritative write
→ optional asynchronous delivery/realtime work
→ supporting audit/observability/privacy/moderation effects
```

### Explicitly not owned by CL-07

CL-07 does not own:

- authentication or session truth;
- platform or organization permission interpretation;
- Order, Gig, Booking, Job, JobApplication, JobInterview, Dispute, ModerationCase, ComplianceHold, VerificationCheck, TrackSubscription, or TrackEntitlementGrant lifecycles;
- healthcare policy decisions;
- PrivacyRequest, DataErasureJob, or DataRetentionExemption orchestration;
- MediaAsset bytes, malware scanning, object storage, or signed-file URL mechanics;
- search projection truth;
- general marketing campaigns or email marketing strategy;
- provider cloud state as Workin Ants truth;
- proof that a user understood or completed the workflow referenced by an alert.

---

## 3. Module Inventory

| Module ID | Module name | Module type | Purpose | Owned truth | Primary responsibility in CL-07 | Major inbound dependencies | Major outbound consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `messaging` | Messaging Module | capability | Maintain reusable, context-bound conversations between authorized Workin Ants actors. | `Thread`, `ThreadContextType`, `ThreadParticipant`, `Message`, contextual `MessageMedia`, participant read cursor, message product-deletion/erasure markers | Create/retrieve context threads, control participant membership, persist messages, attach validated media context, apply external access/redaction decisions, expose realtime-safe changes, request new-message notifications | Identity & Access; Role / Authority; source business Modules; Media / File Access; Healthcare / Regulated Services; Privacy / Data Erasure; Audit / Event Ledger; Content Moderation & Legal Notice; Notification | Order; Gig; Candidate Application; Job Interview; Review/Dispute; Media; Role/Authority; Healthcare; Privacy; Moderation; Notification; Admin Review |
| `notification` | Notification Module | capability | Persist, route, deliver, and record system alerts intended for Users or Organizations. | `Notification`, notification status/channel/priority vocabulary, `NotificationSubscription`, `NotificationDelivery`, `NotificationSubscriptionEvent`, provider-result translation, reachability/device state | Accept one canonical notification request, render privacy-safe content, resolve recipients, enqueue/deliver through channel adapters, record attempts/results, maintain web-push subscription lifecycle | Identity & Access; Role / Authority; Consent & Disclosure; source Modules; Organization Hiring recipient facts; shared queue/crypto/ops; provider adapters; Privacy | All workflow Modules; Users; Organization actors; Audit/Ops; support/admin workflows |

### Module-separation rule

Messaging may request Notification after a committed Message. Notification may retain only the safe metadata needed for delivery. Notification must not become a read-through repository for private message bodies or participant policy.

---

## 4. Cluster Architecture Principles

1. **Two Modules, two truths.** Conversation truth and alert-delivery truth remain separate.
2. **Source event meaning stays upstream.** Notification records “an alert about X was requested/delivered,” not “X happened.”
3. **Messaging owns participation; Role interprets permission.** `ThreadParticipant` is relationship truth. Role / Authority returns allow/deny decisions using Messaging-supplied facts.
4. **Message attachments are contextual joins.** `MessageMedia` says why a MediaAsset belongs to a Message. Media / File Access owns the file lifecycle and signed access.
5. **Notification owns transport policy, not domain policy.** Notification selects and executes eligible channels from source-approved intent and owner-supplied recipient facts.
6. **Privacy-safe payloads are mandatory at every outward boundary.** Private message bodies, PHI, OTPs, financial/tax data, raw resume details, identity documents, and contract text must not enter push payloads, telemetry, or generic audit metadata.
7. **Browser permission is not ConsentLog.** Consent & Disclosure owns versioned platform disclosure proof; browser permission is device state; subscription is reachability state; Delivery is attempt/result state.
8. **Provider state is normalized before it becomes Notification truth.** Vendor status strings and payloads remain adapter-local.
9. **No local queue or idempotency frameworks.** Messaging and Notification reuse canonical application, event, queue, retry, request-context, and observability operations.
10. **No private-message search projection by default.** CL-07 has no public-search responsibility.
11. **No entitlement leakage.** Track Subscription events may trigger notifications, but Messaging and Notification do not create local premium flags or reconstruct entitlement policy.
12. **Current Prisma constraints are executable evidence.** Where business intent is unresolved but the schema already enforces a constraint, implementation must respect the current schema until an approved migration changes it.

---

## 5. Runtime / Collaboration Topology

### Synchronous messaging path

```text
Browser / Server Action / internal Module command
  → resolveAuthenticatedActor                       [Identity]
  → authorizeResourceAction                        [Role / Authority]
       ↑ owner facts: ThreadParticipant/context     [Messaging]
  → source-context validation through owner API    [SH-123 validateOwnedTargetReference; Order/Gig/Hiring/etc.]
  → Messaging application service
       → transaction: Thread / Participant / Message / MessageMedia
       → appendAuditEvent or recordSensitiveAccess when policy requires
       → publishRealtimeChange [SH-071; Proposed ruling] after commit
       → requestNotification with safe metadata after commit
  → response
```

### Notification path

```text
Source Module or Messaging
  → requestNotification                             [Notification public interface]
  → executeIdempotentCommand                        [platform primitive]
  → source-owned recipient-facts query              [owner public interface]
  → resolveNotificationRecipients                   [shared contract]
  → queryConsentProof when channel requires it      [Consent]
  → Notification-owned eligibility/payload policy
  → Notification authoritative record(s)
  → enqueueReliableJob                              [shared queue]
  → Notification delivery worker
       → renderNotificationTemplate
       → channel adapter
       → external provider
       → translateProviderStatus                    [Notification adapter]
       → NotificationDelivery authoritative update
       → recordIntegrationFailure / telemetry on technical failure
```

### Provider callback path

```text
Provider callback
  → verifyProviderWebhookSignature                  [shared shell + adapter]
  → deduplicateProviderEvent                        [shared mechanism, Notification-owned truth]
  → translateProviderStatus                         [Notification adapter]
  → update NotificationDelivery / subscription state [Notification]
  → audit/ops effects as required
```

The callback path is **architecturally required** for providers that expose asynchronous receipts, but the current Prisma schema does not contain a confirmed Notification-owned processed-provider-event record. See Unresolved Decisions.

### Cross-Module database rule

No CL-07 application service should import another Module's repository as the default integration mechanism. Use public commands/queries or stable event contracts. Database foreign keys may exist for integrity, but a foreign key is not permission to interpret or mutate the referenced Module's lifecycle.

---

## 6. Folder / Code Organization

The exact repository root must remain consistent with root `code-standards.md`. If root code standards prescribe a different equivalent path, follow them without changing the ownership described here.

### Proposed module-first placement

```text
src/
  modules/
    messaging/
      domain/
        thread-policy.ts
        message-policy.ts
        types.ts
      application/
        commands/
        queries/
        services/
      contracts/
        public-commands.ts
        public-queries.ts
        owner-facts.ts
        privacy-executor.ts
        moderation-target.ts
      infrastructure/
        persistence/
        realtime/
      presentation/
        actions/
        queries/
        components/
      tests/
        unit/
        contract/
        integration/

    notification/
      domain/
        routing-policy.ts
        payload-policy.ts
        delivery-policy.ts
        types.ts
      application/
        commands/
        queries/
        services/
      contracts/
        request-notification.ts
        recipient-facts.ts
        provider-port.ts
        privacy-executor.ts
      templates/
        registry.ts
        schemas/
      infrastructure/
        persistence/
        providers/
          email/
          sms/
          web-push/
        workers/
        webhooks/
      presentation/
        actions/
        queries/
        components/
        service-worker/
      tests/
        unit/
        contract/
        integration/
        provider/

  platform/                         # only existing approved shared primitives
    auth/
    authorization/
    events/
    jobs/
    observability/
    crypto/
    realtime/
```

### Placement rules

- `messaging/domain` contains Messaging-only invariants; it must not import provider SDKs.
- `notification/domain` contains Notification-only routing/payload/delivery rules; it must not import source business repositories.
- Generic alert-delivery SDKs exist only under Notification provider adapters or approved platform integration shells; Identity verification-provider SDKs remain in Identity.
- Shared idempotency, queue, webhook-security, encryption, logging, metrics, and request-context code lives in approved platform infrastructure, not CL-07 local “utils.”
- `MessageMedia` persistence remains in Messaging. MediaAsset access calls go through Media's public interface.
- Notification templates may be a versioned code/config registry until a separate persisted template lifecycle is explicitly approved. Do not add a `NotificationTemplate` table solely for convenience.
- No `shared/communications` domain folder should contain Message and Notification lifecycle logic.

---

## 7. System and Module Boundaries

| Area / Module | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| Messaging | Thread context binding; current participant membership; message content/lifecycle; message attachment context; read cursor | Identity actor; Role decision; business-context facts; Media readiness/access; Healthcare view decision; Privacy instruction; Moderation decision; Notification request; realtime adapter | Authentication; general permission policy; source business lifecycle; MediaAsset; signed URLs; healthcare policy; PrivacyRequest; Report/ModerationCase; Notification delivery |
| Notification | Alert intent record after accepted request; channel/routing execution; delivery attempts/results; push subscription/permission/service-worker/PWA evidence; safe payload shaping | Identity destinations; Role decision; Consent proof; owner recipient facts; queue/retry; crypto; provider adapters; audit/ops; Privacy instruction | Source business status; organization membership; Thread/Message content truth; consent versions; OTP/recovery lifecycle; holds/moderation/FCRA legal decisions; Track entitlement truth |
| Identity & Access | authenticated actor, security/recovery/challenge lifecycles | Notification delivery capability | notification delivery truth; message truth |
| Role / Authority | permission interpretation | ThreadParticipant and resource-owner facts | ThreadParticipant lifecycle; organization membership lifecycle; message lifecycle |
| Consent & Disclosure | versioned consent/disclosure proof | notification context | browser permission, subscription state, delivery state |
| Organization Hiring | OrganizationMember and OrganizationNotificationSetting lifecycle | requestNotification | NotificationDelivery, push subscriptions |
| Media / File Access | MediaAsset/file safety/storage/grants/signed URLs | Messaging SH-026 contextual access decision | MessageMedia contextual meaning; Message content |
| Healthcare / Regulated Services | sensitivity/redaction/block policy | Messaging targets/sensitivity facts | Message or Thread lifecycle |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/Target/RetentionExemption orchestration | CL-07 enumerate/execute handlers | direct CL-07 table mutation |
| Content Moderation & Legal Notice | Report, case, legal notice, moderation decision/action | Messaging target resolver/executor; Notification delivery | Message lifecycle as case truth; notification delivery as legal decision |
| Audit / Event Ledger | AuditEvent and AccessAuditLog | safe CL-07 action context | Thread/Message/Notification/Delivery lifecycle |
| Observability / Ops | public logging, metrics, failure, queue, and incident capabilities; persistence remains unresolved | CL-07 technical events | business or delivery lifecycle truth |
| Track Subscription & Entitlement | subscription/entitlement/usage policy truth | requestNotification on lifecycle changes | local CL-07 premium flags or quotas |

---

## 8. Data Ownership

### Messaging-owned models and enums

| Record / enum | Owner | Meaning / lifecycle notes |
| --- | --- | --- |
| `Thread` | Messaging | Conversation/context truth. Holds `contextType`, optional generic `contextId`, typed foreign keys, `dataSensitivity`, `erasedAt`. |
| `ThreadContextType` | Messaging | `order`, `gig`, `gig_response`, `gig_assignment`, `job_application`, `job_interview`, `direct`, `support`. No Booking, Review, or Dispute context exists today. |
| `ThreadParticipant` | Messaging | Current participant membership and `lastReadAt`. Role / Authority interprets access using these facts. |
| `Message` | Messaging | Message body and create/edit/product-delete/privacy-erasure markers. `deletedAt` is not legal erasure. |
| `MessageMedia` | Messaging | Contextual relationship between Message and MediaAsset. Media owns the actual file. |
| `DataSensitivity` on Thread | Shared vocabulary consumed by Messaging | Messaging stores the classification; Healthcare/other policy owners interpret access effects where applicable. |

### Notification-owned models and enums

| Record / enum | Owner | Meaning / lifecycle notes |
| --- | --- | --- |
| `Notification` | Notification | Workin Ants alert record with target, channel, name, priority, title/body/action route, source reference, status, sensitivity, expiry. |
| `NotificationStatus` | Notification | Current values: `queued`, `sent`, `read`, `dismissed`, `failed`. Aggregate semantics require a ruling before multi-channel fan-out is implemented. |
| `NotificationChannel` | Notification | `in_app`, `email`, `sms`, `web_push`. Shared use by OrganizationNotificationSetting does not transfer ownership. |
| `NotificationPriority` | Notification | `low`, `normal`, `high`, `urgent`. Urgency does not bypass privacy/consent/authorization. |
| `NotificationSubscription` | Notification | User/device/browser push reachability and permission/service-worker/PWA metadata. |
| `NotificationSubscriptionStatus` | Notification | `active`, `revoked`, `expired`, `failed`, `disabled`. |
| `NotificationPermissionStatus` | Notification | Observed browser permission state, separate from ConsentLog. |
| `NotificationPlatform` | Notification | `web`, `android`, `ios_pwa`, `macos`, `windows`, `unknown`. |
| `NotificationSubscriptionProvider` | Notification | Current enum is push-specific: `fcm`, `onesignal`, `wonderpush`, `web_push`. It must not be reused as a truthful email/SMS provider vocabulary. |
| `PwaInstallStatus` | Notification | PWA capability/readiness evidence. |
| `NotificationDelivery` | Notification | One transport attempt/result record. Current retry/attempt semantics are incomplete. |
| `NotificationDeliveryStatus` | Notification | `queued`, `sending`, `sent`, `delivered`, `failed`, `skipped`. |
| `NotificationSubscriptionEvent` | Notification | Device/permission/subscription evidence; current enum also includes click/close interactions, creating an acknowledged modeling overlap. |
| `NotificationSubscriptionEventType` | Notification | Permission/service-worker/subscription/PWA/token events plus click/close values. |
| `NotificationPayloadSensitivity` | Notification | `safe`, `private_metadata`, `sensitive`, `healthcare`, `financial`, `security`, `legal`. Classification is a gate input, not proof that unrestricted JSON is safe. |

### External records referenced but not owned

| Record | Owner | CL-07 use |
| --- | --- | --- |
| `User` | Identity & Access | actor/recipient identity |
| `Organization`, `OrganizationMember`, `OrganizationNotificationSetting` | Organization Hiring for lifecycle; Role interprets authority | organization routing facts |
| Order/Gig/GigResponse/GigAssignment/JobApplication/JobInterview | respective business Modules | Thread context and participant facts; notification source references |
| `MediaAsset` and Media grant records | Media / File Access | message attachments and signed access |
| `ConsentLog` | Consent & Disclosure | web-push disclosure/version proof |
| `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption` | Privacy / Data Erasure | orchestrates CL-07 privacy execution |
| `AuditEvent`, `AccessAuditLog` | Audit / Event Ledger | generic action/sensitive-access proof |
| Observability public capabilities (no current Ops Prisma models assumed) | Observability / Ops | failure, queue, health, and incident visibility; persistence remains CL-09 decision-gated |
| `TrackSubscriptionEvent`, `TrackEntitlementGrant` | Track Subscription & Entitlement | may trigger notification; never CL-07 policy truth |

### Ownership conflicts resolved by this architecture

**ThreadParticipant conflict.** Historical Deep Module Registry evidence listed `ThreadParticipant` under Role / Authority's owned schemas, while the Messaging registry, Ubiquitous Language, Module extract, and Canonical Shared Operations explicitly define Messaging as the row/lifecycle owner and Role / Authority as permission interpreter. **Architecture Ruling:** Messaging owns `ThreadParticipant`; Role / Authority consumes participant facts and never mutates the row as its own truth.

**MessageMedia conflict.** Some source material can be read as Media owning message attachment records. Ubiquitous Language and canonical SH-090 `attachValidatedMedia` separation establish that the contextual join belongs to the contextual Module while Media owns `MediaAsset`. **Architecture Ruling:** Messaging owns `MessageMedia`; Media owns file truth and access mechanics.

---

## 9. Lifecycle Ownership

### 9.1 Thread lifecycle — Messaging

Current schema represents:

```text
create/context-bind
→ active conversation by existence
→ optional privacy erasure marker (`erasedAt`)
```

There is no `ThreadStatus`, close/archive/freeze status, or moderation status. Coding agents must not invent one. Moderation integration must use an approved external-decision enforcement representation rather than overloading `deletedAt` or `erasedAt`.

**Transition authority:** Messaging application services only.

**May request/react:** Order, Gig, Candidate Application, Job Interview, Review/Dispute, support/admin flows may request or retrieve threads through Messaging interfaces.

**Must not be confused with:** source business object lifecycle, ModerationCase, PrivacyRequest.

### 9.2 ThreadParticipant lifecycle — Messaging

Current schema represents current membership:

```text
admit participant
→ participant may read/write subject to Role decision
→ read cursor advances (`lastReadAt`)
→ removal currently implies row removal if implemented
```

Historical left/revoked state is not modeled. Do not add participant-status fields without an architecture decision.

### 9.3 Message lifecycle — Messaging

```text
created
→ optionally edited (`editedAt`)
→ optionally product-deleted (`deletedAt`)
→ optionally privacy-erased (`erasedAt` plus owner-executed data treatment)
```

There is no Message status enum and no edit-revision ledger. `deletedAt` must not be treated as PrivacyRequest completion or moderation case truth.

### 9.4 MessageMedia lifecycle — Messaging + Media boundary

```text
MediaAsset reaches Media-approved ready state
→ Messaging authorizes Message context
→ MessageMedia join is created
→ access requires both Thread/Message context and Media access decision
→ detaching join does not delete MediaAsset
```

### 9.5 Notification lifecycle — Notification

Current enum supports:

```text
queued
→ sent
→ read OR dismissed

queued/sent
→ failed
```

The exact relationship of `read`, `dismissed`, click/open evidence, expiry, and multiple deliveries is unresolved. Until the aggregate ruling is approved, implementation must not infer “all channels delivered,” “user saw it,” or “workflow completed” from `Notification.status`.

### 9.6 NotificationDelivery lifecycle — Notification

```text
queued
→ sending
→ sent
→ delivered

queued/sending/sent
→ failed

queued
→ skipped
```

Provider-native statuses are adapter input only. The Notification adapter owns translation to this enum.

### 9.7 NotificationSubscription lifecycle — Notification

```text
permission observed
→ subscription created/refreshed
→ active
→ revoked | expired | failed | disabled
```

An active web-push subscription requires `permissionStatus=granted` by policy even though the database does not currently enforce it.

### 9.8 NotificationSubscriptionEvent ledger — Notification

Append-only evidence records observed permission, service-worker, subscription, token, PWA and certain interaction events. It does not replace current `NotificationSubscription` state or `NotificationDelivery` truth.

---

## 10. Public Module Interfaces

Interface names below are stable architecture names where supplied by canonical evidence. Owner-local operation names from Module extracts remain candidates where no canonical name exists.

### Messaging public interfaces

| Interface | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- |
| SH-113 `ensureContextThread` | Order, Gig, Candidate Application, Job Interview and other approved context owners | Return/create the one currently schema-permitted Thread for a typed business context | actor/system context; `ThreadContextType`; owner-issued context ID; initial participant IDs; sensitivity | Thread ID; context binding; current participants | source truth | source business status; permission policy |
| `getThreadParticipantFacts` | Role / Authority, Media, Healthcare, Admin Review | Expose current participant/context facts | Thread ID; actor User ID | participant exists; joinedAt; lastReadAt; context type/id; safe sensitivity metadata | truth | authorization decision |
| SH-026 `authorizeContextualResourceAccess` (Messaging owner implementation) | Media / File Access | Decide contextual MessageMedia access | actor; Thread; Message; MediaAsset; requested action | allow/deny and safe evidence bound to those inputs | contextual decision | Media readiness, grants, TTL, or signed URL issuance |
| `listThreadsForUser` | UI/client | Authorized inbox/thread list | actor; pagination; optional allowed context filter | safe thread summaries | truth/derived summary | business object lifecycle |
| `getThread` | UI/consumers | Authorized thread metadata | actor; Thread ID; view purpose | full/redacted/metadata-only result | truth + external decision effect | healthcare policy |
| `listThreadMessages` | UI/consumers | Authorized paginated message retrieval | actor; Thread ID; cursor/page size | messages after deletion/erasure/redaction policy | truth | sensitive access policy |
| `sendMessage` | authorized participants | Persist a new Message | actor; Thread ID; content; optional MediaAsset IDs; idempotency key | Message ID, timestamp, safe realtime/notification metadata | truth | Notification delivery |
| `editMessage` | sender/admin per Role policy | Edit current message content | actor; Message ID; replacement content | updated message + `editedAt` | truth | edit-history proof that does not exist |
| `deleteMessage` | authorized actor | Product-delete/hide message | actor; Message ID; reason | updated deletion marker | truth | privacy erasure or moderation decision |
| `markThreadRead` | participant | Advance read cursor | actor; Thread ID; bounded read cursor/timestamp | new `lastReadAt` | truth | Notification read state |
| SH-090 `attachValidatedMedia` (shared contract, contextual execution) | Messaging UI/services | Attach ready file context | actor; Message ID; MediaAsset ID | MessageMedia join | truth | MediaAsset readiness or signed URL entitlement |
| SH-096 `enumerateSubjectData` handler | Privacy | Enumerate Messaging-held subject records | subject; cursor | target descriptors/dispositions | evidence/facts | PrivacyRequest orchestration |
| SH-097 `evaluateRetentionRequirement` | Privacy | Evaluate owner-held retention requirements under approved policy | subject/owner target; policy context | required; reason; basis; retainUntil; minimum fields; permitted anonymization; source reference | owner facts | exemption creation or final Privacy workflow completion |
| SH-095 `executePrivacyInstruction` handler | Privacy | Execute owner-approved disposition | target/action/idempotency/retention instruction | completed/retained/skipped/failed result | execution evidence | privacy-request completion |
| moderation target resolver/executor | Moderation | Resolve Message/Thread safely and apply approved enforcement action | case/action envelope; target | minimized snapshot / execution acknowledgement | evidence/execution result | ModerationCase lifecycle |

### Organization recipient collaboration

Organization Hiring exposes `resolveOrganizationNotificationRecipientFacts` as its owner-specific public query supporting SH-043 `resolveNotificationRecipients`. It accepts an Organization-scoped notification context, evaluates Organization-owned membership and `OrganizationNotificationSetting` facts, and returns eligible concrete User IDs plus only safe routing facts. An empty eligible-recipient set is valid; unavailable and unauthorized results are distinct from that empty result. Notification consumes the result, deduplicates recipients, applies its own reachability/channel eligibility, and performs fan-out. Notification must not reconstruct Organization role/settings policy from raw tables. U-CL07-09 still gates Notification recipient cardinality/fan-out persistence semantics.

**U-CL07-19 remains unresolved.** Notification must not select or introduce canonical durable click/open/close persistence before approval. Overlapping fields on `Notification`, `NotificationDelivery`, and `NotificationSubscriptionEvent` do not establish a canonical owner. Provider/client callbacks may be validated or handled operationally without establishing durable canonical interaction truth. `markNotificationRead` and `dismissNotification` are separate lifecycle commands and are not blocked by U-CL07-19.

### Notification public interfaces

| Interface | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- |
| SH-041 `requestNotification` | all workflow Modules, Messaging, Audit/Ops | Submit one authorized alert intent through canonical delivery | source Module/type/id; recipient target/group contract; template key+version; priority; sensitivity; safe variables; action route; idempotency key | accepted/rejected result; notification request reference | decision + Notification truth reference | provider dispatch or source business state |
| SH-042 `renderNotificationTemplate` | Notification internally | Render channel-safe versioned content | template key/version; locale; channel; validated safe variables | title/body/provider payload | derived artifact | business/legal decision |
| SH-043 `resolveNotificationRecipients` | Notification + source owner | Resolve group/relationship to User IDs without moving owner policy | typed recipient request | concrete User IDs + routing metadata | owner facts / routing result | membership/participant lifecycle |
| `listNotifications` | authenticated User/UI | In-app notification list | actor; pagination/status filter | safe notification summaries | truth | source workflow status |
| `getUnreadNotificationCount` | authenticated User/UI | Count unread in-app alerts | actor | count | projection/derived query | Message unread state |
| `markNotificationRead` | targeted User | Mark in-app alert read | actor; Notification ID | updated status/readAt | truth | workflow completion |
| `dismissNotification` | targeted User | Dismiss an in-app alert | actor; Notification ID | updated status | truth | source action completion |
| `recordNotificationInteraction` | authenticated/client/provider callback | Record click/open/close evidence only after U-CL07-19 approval | notification/delivery; interaction; safe URL; actor/device context | interaction evidence | evidence | user understanding/completion |
| `recordNotificationPermissionState` | client | Persist observed browser permission | actor; platform/device context; permission status | updated reachability state/event | truth/evidence | ConsentLog acceptance |
| `upsertPushSubscription` / `refreshPushSubscription` / `revokePushSubscription` | authenticated client/account settings | Manage device/browser reachability | actor; provider/platform; encrypted/hashed endpoint/token material; service-worker metadata | subscription state | truth | identity/authentication |
| `listNotificationSubscriptions` | account settings | List connected devices without secrets | actor | device/reachability summaries | truth | OS notification settings |
| SH-096 `enumerateSubjectData` handler | Privacy | Enumerate notification-owned personal data | subject/cursor | notification/subscription/delivery targets | evidence/facts | PrivacyRequest orchestration |
| SH-097 `evaluateRetentionRequirement` | Privacy | Evaluate owner-held retention requirements under approved policy | subject/owner target; policy context | required; reason; basis; retainUntil; minimum fields; permitted anonymization; source reference | owner facts | exemption creation or final Privacy workflow completion |
| SH-095 `executePrivacyInstruction` handler | Privacy | Execute approved local data disposition | target/action/idempotency | result | execution evidence | retention decision |

---

## 11. Canonical Shared Operations Used by This Cluster

**Shared Operations status:** references marked **Proposed ruling** are planning dependencies only, not approval for shared schema/API commitment or a generic service. Independently justified owner-specific interfaces do not approve a proposed shared operation globally. Realtime remains post-commit, authorized, and rebuildable; Moderation integration consumes approved contracts. Canonical metadata and reusable boundaries remain controlled by the Shared Operations registry.

Canonical SH IDs, names, owners, classifications, and statuses come from `context/shared/shared-operations.md`. The local table describes CL-07 use; the registry controls reusable boundaries.

| Canonical operation | Plain-English meaning | Canonical owner | CL-07 consumers | Reusable mechanism | CL-07 policy that stays local | Invocation point | Must not duplicate | Classification | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Resolve provider session/system credential to trusted actor context | Identity & Access | Messaging, Notification | typed authenticated actor middleware | what messaging/notification action is requested | every protected command/query | `chatAuth`, `notificationCurrentUser`, feature-local session helpers | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Decide permission for named action using owner-supplied relationship facts | Role / Authority | Messaging, Notification | decision API + aligned RLS/route enforcement | Thread/Notification-specific relationship facts/action vocabulary | before protected read/mutation | local permission engines | Cross-cutting capability | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Read minimum owner relationship facts without source-truth transfer | Each source Module | Messaging, Notification | owner-specific DTO pattern | context/participant/recipient facts | context validation and recipient resolution | cross-domain Prisma repositories | Shared contract; separate implementations | Proposed ruling |
| SH-008 `queryConsentProof` | Return proof of required accepted version | Consent & Disclosure | Notification | versioned consent query | whether web-push disclosure is required for this channel/action | before establishing/using consent-dependent push capability | `pushConsent` tables/services | Platform consent capability | Confirmed |
| SH-029 `appendAuditEvent` | Append generic important-action proof | Audit / Event Ledger | Messaging, Notification | insert-only AuditEvent command | which CL-07 actions merit generic audit | after or transactionally adjacent to important actions | local generic audit logs | Platform audit capability | Confirmed |
| SH-030 `recordSensitiveAccess` | Append protected-data access proof | Audit / Event Ledger | Messaging primarily; Notification for sensitive admin/device actions if policy says | AccessAuditLog command | sensitivity, target, decision, purpose | sensitive Message/Thread access and protected delivery/access events | `MessageAccessLog`, mutable admin view log | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` | Propagate correlation/request/actor IDs | Observability / platform infrastructure | both | async request context | none beyond safe CL-07 labels | entrypoint and async dispatch | local correlation systems | Platform primitive | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Strip secrets and sensitive data from telemetry/audit metadata | Observability / Ops and Audit payload policy | both | allowlisted serializer/redactor | CL-07 sensitivity labels and safe fields | before logs, metrics, failures, audit metadata | local ad hoc redactors | Cross-cutting capability | Confirmed |
| SH-037 `recordIntegrationFailure` | Persist normalized provider/worker failure evidence | Observability / Ops | Notification; Messaging realtime integration if degraded | public operational failure interface; persistence-agnostic | business state remains in CL-07 owner | provider/worker failure | treating IntegrationFailure as Delivery status | Cross-cutting capability | Confirmed |
| SH-038 `recordQueueTelemetry` | Record queue attempts/retries/dead-letter execution | Observability / Ops / queue infrastructure | Notification workers | worker instrumentation | delivery job payload and business completion remain Notification-owned | all async delivery jobs | per-Module queue ledgers | Cross-cutting capability | Confirmed |
| SH-041 `requestNotification` | Submit alert through canonical interface | Notification | Messaging and every source Module | canonical command | Notification routing/payload policy; source meaning stays upstream | after source event commit | direct provider calls in sources | Platform notification capability | Confirmed |
| SH-042 `renderNotificationTemplate` | Render validated localized channel content | Notification | Notification | central template registry | safe variables/channel limits | delivery planning/worker | per-Module email/SMS/push renderers | Cross-cutting capability | Confirmed |
| SH-043 `resolveNotificationRecipients` | Resolve owner groups to concrete Users | Source context owner plus Notification | Notification | shared request/result contract | owner controls membership/recipient facts; Notification fan-out/dedupe | intake/routing | universal recipient repository | Shared contract; separate policy | Confirmed |
| SH-044 `executeIdempotentCommand` | Make retried command yield one effect | Platform application infrastructure | `sendMessage`, SH-113 `ensureContextThread`, SH-041 `requestNotification`, subscription mutation | atomic idempotency claim/result | semantic key/conflict behavior belongs to owner | mutation boundaries | local idempotency tables/helpers unless canonical storage requires owner key | Platform primitive | Confirmed |
| SH-045 `deduplicateDomainEvent` | Prevent duplicate consumer side effects | Platform event infrastructure; consumer owns inbox | Notification consumers; any future Messaging event consumers | inbox claim | handler identity and side effect are consumer-specific | event-triggered requests | custom event dedupe frameworks | Platform primitive | Confirmed |
| SH-046 `publishDomainEvent` | Reliably publish versioned event after source transaction | Platform event/outbox infrastructure | future Messaging lifecycle events if approved; source business Modules | transactional outbox | event semantics/privacy fields owned by publisher | post-commit integration | ad hoc fire-and-forget event buses | Platform primitive | Confirmed |
| SH-047 `enqueueReliableJob` | Persist durable async work with retries/leases/DLQ | Shared queue infrastructure | Notification | common queue client/worker shell | Delivery job semantics/status remain Notification-owned | after authoritative enqueueable write | local worker framework | Platform primitive | Confirmed |
| SH-048 `executeRetryWithBackoff` | Bounded retry transient technical failures | Shared queue/platform infrastructure | Notification delivery/provider callbacks | retry strategy primitive | Notification adapter classifies retryability | delivery and callback handling | provider-specific retry loops scattered across adapters | Platform primitive | Confirmed |
| SH-059 `verifyProviderWebhookSignature` | Verify raw callback authenticity before parsing/side effects | Shared integration-security shell; provider adapter supplies algorithm | Notification provider callbacks | common verifier interface | provider algorithm/secret/tolerance local to adapter | webhook edge | bespoke route verification patterns | Provider-adapter contract | Confirmed |
| SH-060 `deduplicateProviderEvent` | Claim callback once | Provider-owning Module using shared primitive | Notification when callbacks exist | atomic provider-event claim | Notification keeps its own processed-event truth | after signature verification | reusing Stripe/Calendar/Video processed-event tables | Shared mechanism; separate truth | Confirmed |
| SH-061 `translateProviderStatus` | Map provider status/error to owner vocabulary | Provider-owning adapter | Notification | provider-adapter contract | mapping to NotificationDelivery/Subscription statuses | provider response/callback | global cross-provider status mapper | Provider-adapter contract | Confirmed |
| SH-062 `reconcileProviderState` | Compare Workin Ants truth to provider and repair safely | Each provider-owning Module using shared worker framework | Notification | shared reconciliation worker pattern | repairability and authoritative mapping remain Notification-owned | scheduled/admin repair | generic global provider reconciler with domain policy | Shared mechanism; separate policy | Confirmed |
| SH-071 `publishRealtimeChange` (Proposed ruling) | Publish committed safe changes to authorized clients | Platform realtime adapter; Messaging is primary consumer | Messaging | authorized realtime transport | audience/payload based on Thread/participant facts | after commit | treating Realtime as message storage | Infrastructure adapter | Proposed ruling |
| SH-075 `encryptSensitiveValue` | Encrypt recoverable secret with managed/versioned keys | Shared security/cryptography capability | NotificationSubscription | envelope encryption | which endpoint/token fields require recovery and rotation | subscription create/refresh | notification-local crypto | Platform primitive | Confirmed |
| SH-076 `normalizeAndHashIdentifier` | Create non-plaintext stable comparison identifier | Shared security/cryptography capability | NotificationSubscription | keyed HMAC/normalization | endpoint/token normalization purpose | subscription dedupe/lookup | plaintext endpoint matching as sole identity | Platform primitive | Confirmed |
| SH-090 `attachValidatedMedia` | Attach ready MediaAsset through context-owned join | Contextual domain Module; Media owns asset truth | Messaging | shared contract | message attachment authorization/role remains Messaging | message attachment | custom upload/storage pipeline | Shared contract; separate contextual truth | Confirmed |
| SH-095 `executePrivacyInstruction` | Execute approved privacy disposition in owner records | Privacy orchestrates; each data owner executes | both | cross-cutting protocol | exact CL-07 field mutations and invariants | Privacy target execution | local PrivacyRequest workflow | Cross-cutting protocol | Confirmed |
| SH-096 `enumerateSubjectData` | List owner-held subject data and supported dispositions | Each data-owning Module through Privacy-defined interface | both | privacy handler protocol | Messaging/Notification know their records | Privacy inventory | global Privacy direct DB crawler | Cross-cutting protocol | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Supply owner facts for retention decision; Privacy records exemption | Data owner supplies facts; Privacy records exemption | both | retention protocol | source facts only; legal decision is not invented locally | privacy planning | local exemption tables | Cross-cutting protocol | Confirmed |
| SH-101 `submitModerationReport` | Submit typed abuse/legal allegation | Content Moderation & Legal Notice | Messaging | moderation intake interface | Messaging supplies target/evidence only | user report action | local message report/case table | Module public interface | Confirmed |
| SH-103 `executeModerationDecision` | Apply authoritative moderation action in target owner | Moderation owns decision; each target owner executes | Messaging | enforcement protocol | Messaging maps approved action to conversation behavior | after ModerationAction | Moderation directly mutating messaging DB | Cross-cutting protocol | Confirmed |

### Classification reminders

- SH-041 `requestNotification` is a Platform notification capability owned by Notification.
- SH-071 `publishRealtimeChange` (Proposed ruling) is an Infrastructure adapter with Proposed ruling status. Idempotency, queueing, and crypto use their registered Platform primitives; SH-059 `verifyProviderWebhookSignature` is a Provider-adapter contract.
- `getThreadParticipantFacts` is a Messaging public interface, **not** a platform shared operation.
- Healthcare message view/redaction decisions are Healthcare public interfaces, **not** Notification/Messaging policy.
- Provider adapters share a port pattern; provider mapping truth stays Notification-local.

---

## 12. Cross-Module Data Flows

### 12.1 Source workflow requests a notification

```text
Trigger: source Module commits business truth
→ source Module constructs typed safe notification intent
→ executeIdempotentCommand
→ Notification.requestNotification
→ resolveNotificationRecipients using owner facts
→ channel eligibility / consent / reachability checks
→ Notification authoritative write
→ enqueueReliableJob for external channels
→ worker renders template and invokes adapter
→ NotificationDelivery update
→ operational telemetry / recordIntegrationFailure if needed
→ optional AuditEvent
```

**Owner at each step:** source owns meaning; Notification owns alert/delivery; Consent owns consent proof; recipient-owner owns relationship facts; shared queue owns execution mechanics; Observability owns operational failure record.

### 12.2 Send a message and alert other participants

```text
Trigger: participant calls Messaging.sendMessage
→ Identity resolves actor
→ Messaging returns participant/context facts
→ Role authorizes `message.send`
→ Healthcare decision applied if sensitivity requires it
→ Media readiness checked for any attachments
→ Messaging transaction writes Message + MessageMedia
→ post-commit realtime publication
→ Messaging requests Notification with safe preview metadata only
→ Notification resolves eligible recipients excluding sender when source policy requests
→ Notification delivery proceeds independently
```

If Notification is unavailable, the Message remains committed truth. Delivery failure must not roll back the Message.

### 12.3 Read sensitive healthcare conversation

```text
Trigger: authorized/admin actor opens Thread
→ Identity resolves actor
→ Role authorizes base resource action
→ Messaging supplies target/sensitivity facts
→ Healthcare owner returns allow/redact/block decision
→ Messaging applies result
→ Audit.recordSensitiveAccess captures safe evidence
→ response returns full/redacted/metadata-only/denied result
```

Healthcare policy remains external; Messaging never derives PHI visibility from `dataSensitivity` alone.

### 12.4 Attach media to message

```text
Trigger: participant submits MediaAsset ID with Message
→ Messaging authorizes thread/message action
→ Media public interface confirms asset readiness and caller/context eligibility
→ Messaging creates MessageMedia join transactionally
→ later preview/download:
   Messaging returns actor/Thread/Message/MediaAsset/action-bound SH-026 contextual decision
   → Media requestMediaAccess applies its own readiness/grant/TTL gates and SH-087 signed URL issuance internally
   → sensitive access evidence as policy requires
```

### 12.5 Push subscription registration

```text
Trigger: authenticated client requests push setup
→ Consent query for required disclosure proof
→ client/browser permission observed
→ Notification records permission event
→ only if permission=granted, create/refresh subscription
→ normalize/hash identifiers
→ encrypt recoverable endpoint/token material
→ NotificationSubscription becomes active
→ account settings can list/revoke it without exposing credentials
```

### 12.6 Provider delivery callback

```text
Trigger: provider callback
→ verify signature
→ deduplicate provider event
→ translate provider result
→ update NotificationDelivery and, if appropriate, subscription health
→ record operational failure if degraded
→ never update source Order/Job/Message/etc.
```

### 12.7 Privacy erasure/export

```text
Privacy owner verifies request and creates targets
→ enumerateSubjectData on Messaging/Notification
→ each CL-07 Module returns inventory and supported actions
→ evaluateRetentionRequirement on each data owner returns retention facts
→ Privacy determines/records DataRetentionExemption where required
→ executePrivacyInstruction on each owner
→ CL-07 mutates only its own records / delegates provider deletion through its own adapter where applicable
→ result returned to Privacy
→ Privacy aggregates overall request completion
```

### 12.8 Moderation report on a message

```text
User reports Message
→ Messaging validates target/actor
→ Content Moderation.submitModerationReport
→ Moderation owns case/decision
→ if enforcement required, Moderation sends executeModerationDecision envelope
→ Messaging applies approved conversation restriction using approved representation
→ Search is not involved because messages are not public-indexed
→ Notification may deliver legal/user notice when Moderation requests it
```

---

## 13. Cross-Cluster Bridges

| Source | Destination | Information / command | Authoritative owner | Interface/event | Forbidden coupling |
| --- | --- | --- | --- | --- | --- |
| CL-01 Identity | CL-07 | actor/session context | Identity | SH-001 `resolveAuthenticatedActor` | CL-07 user/session helpers |
| CL-01 Role / Authority | CL-07 | access decision | Role / Authority | SH-002 `authorizeResourceAction` using CL-07 owner facts | Role mutating ThreadParticipant or Notification target |
| CL-01 Consent | Notification | push disclosure proof | Consent | SH-008 `queryConsentProof` | Notification creating ConsentLog |
| CL-01 Track Entitlement | Notification | subscription/plan/entitlement lifecycle alert intent | Track | SH-041 `requestNotification` / domain event | CL-07 interpreting entitlement grants |
| CL-03/04 Marketplace and Order | Messaging | context/participant facts; thread creation request | source Module + Messaging | owner facts + SH-113 `ensureContextThread` | source Module inserting Thread rows |
| CL-04 Order/Dispute | Notification | order/dispute alert intent | source Module | SH-041 `requestNotification` | Notification inferring refund/dispute state |
| CL-05 Booking/Video/Media | Messaging | Media readiness/access; booking-associated conversation request if approved | Media/Booking | public interfaces | Messaging storage provider access; inventing Booking context type |
| CL-05 Booking/Video | Notification | schedule/session alerts | source Module | SH-041 `requestNotification` | Notification changing Booking/Video state |
| CL-06 Hiring | Messaging | JobApplication/JobInterview context and participants | Candidate Application / Job Interview | owner facts + SH-113 `ensureContextThread` | Messaging reading resume or hiring status directly |
| CL-06 Organization Hiring | Notification | eligible User IDs and safe routing facts | Organization Hiring | `resolveOrganizationNotificationRecipientFacts` supporting SH-043 `resolveNotificationRecipients` | Notification reconstructing or owning membership/settings policy |
| CL-08 Privacy | both | privacy inventory, retention evaluation, and execution | Privacy orchestrates, CL-07 executes | SH-096 `enumerateSubjectData`, SH-097 `evaluateRetentionRequirement`, SH-095 `executePrivacyInstruction` | Privacy direct CL-07 repository mutations |
| CL-09 Moderation | Messaging | report/decision/enforcement envelope | Moderation | SH-101 `submitModerationReport`, SH-103 `executeModerationDecision` | local MessageReport/ModerationCase |
| CL-09 Holds | Notification | hold-created/released alert intent | Hold Module | SH-041 `requestNotification` | Notification interpreting/clearing hold |
| CL-09 Audit | both | generic/sensitive proof | Audit | SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess` | CL-07 generic audit tables |
| CL-09 Observability | both | technical failures/queue telemetry | Observability | canonical ops | using IntegrationFailure as delivery/message status |
| CL-10 Rewards/Prize | Notification | reward/prize alert intent | source Module | SH-041 `requestNotification` | Notification eligibility/tax decisions |

### Review/Dispute and Booking thread bridge warning

The current `ThreadContextType` contains no `review`, `dispute`, or `booking`. Do not silently add them. Until an architecture ruling is approved, consumers must not assume a separate context thread exists. The likely options are reuse of an existing Order thread or schema expansion, but this file does not choose between them.

---

## 14. Authentication and Authorization

### Authentication dependency

Every user-facing CL-07 command/query begins with SH-001 `resolveAuthenticatedActor`. Client-provided `userId`, `senderId`, organization membership, or subscription ownership is never trusted as authority.

### Role / Authority dependency

SH-002 `authorizeResourceAction` interprets permission. CL-07 supplies contextual facts:

- Messaging: ThreadParticipant existence, source context reference, sender ownership, target Message ownership, sensitivity metadata.
- Notification: recipient ownership, subscription ownership, organization target/reference, requested action such as read/dismiss/revoke.

### RLS

PostgreSQL RLS must align with server decisions as defense in depth. RLS must not become an independent business-policy engine that conflicts with Role / Authority. Contract tests must prove server authorization and RLS agree for participant and recipient boundaries.

### Sensitive/admin actions

Potential sensitive actions include:

- support/admin access to private/healthcare Threads;
- access to message attachment signed URLs;
- viewing device/subscription metadata beyond a user's own account;
- operational inspection of sensitive notification failures.

Step-up requirements are not established for ordinary messaging/notification actions. If root architecture or owner Module declares an action sensitive enough for step-up, CL-07 consumes SH-014 `requireStepUpForSensitiveAction`; it must not invent local MFA.

---

## 15. Compliance and Readiness Composition

CL-07 is a communication rail; it composes external facts only where communication requires them.

| Gate / proof | Owner | CL-07 usage |
| --- | --- | --- |
| Authentication | Identity | actor prerequisite |
| Permission | Role / Authority | read/write/manage/revoke decision |
| ConsentLog | Consent & Disclosure | web-push disclosure/version proof where required |
| Browser permission | Notification | device-level push permission evidence |
| NotificationSubscription | Notification | reachability state |
| Healthcare decision | Healthcare / Regulated Services | allow/redact/block Message/Thread view or safe notification payload constraints |
| ComplianceHold | Admin Review / Compliance Hold | only if an owner declares hold applies to communication action; CL-07 does not invent local blocked flags |
| Entitlement | Track Subscription & Entitlement | no general Messaging/Notification entitlement is confirmed. Subscription events may trigger alerts only. |
| Job/FCRA/DMCA decision | owning compliance Module | Notification carries required notice only after owner requests it |

### FCRA and DMCA

Notification supports delivery proof for FCRA adverse-action notices and DMCA/counter-notice communications. Trust Verification / Screening and Content Moderation & Legal Notice respectively own the legal workflow, content requirements, deadlines, and decision truth. Notification does not determine that a notice is legally required.

### Security/recovery/MFA

**Approved SMS ownership boundary (CL-07-R002):** generic business SMS alerts use Notification through SH-041 `requestNotification`; source Modules must not dispatch generic SMS directly. Identity & Access may use an Identity-owned verification provider whose protocol delivers an OTP or challenge. Identity retains challenge generation, expiry, attempts, verification outcome, assurance result, and provider protocol truth. Notification must not independently generate, validate, resend, or implement a parallel OTP/MFA transport/verification workflow. This verification-provider transport is not a second generic notification rail. Only initial production generic SMS provider selection remains unresolved under U-CL07-16.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Messaging events

No Messaging integration event catalog or outbox is confirmed in the current schema. Likely candidates such as `MessageSent` are useful, especially for Notification, but they are not binding until approved.

**Current safe default:** core Messaging writes are synchronous and may call SH-041 `requestNotification` after commit. If event-driven decoupling is introduced, use SH-046 `publishDomainEvent` and SH-045 `deduplicateDomainEvent`; do not create a Messaging-specific event bus.

### Notification jobs

External delivery is asynchronous. A Notification worker must reuse:

- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-038 `recordQueueTelemetry`;
- SH-032 `createRequestContext`;
- SH-037 `recordIntegrationFailure`.

### Idempotency

The following operations require semantic idempotency:

- SH-113 `ensureContextThread` for typed contexts;
- `sendMessage` when clients may retry;
- SH-041 `requestNotification`;
- push subscription create/refresh/revoke;
- provider callback application;
- privacy execution;
- moderation enforcement execution.

Canonical idempotency mechanics are reused; each owner defines the semantic key and conflict behavior.

### Concurrency

- Typed Thread foreign keys are currently unique, so concurrent SH-113 `ensureContextThread` calls must converge on one row.
- `markThreadRead` must be monotonic; stale requests must not move `lastReadAt` backward.
- Notification request dedupe must prevent duplicate alert creation for the same semantic source event/idempotency key.
- Subscription refresh must not allow stale token rotation events to overwrite a newer active credential set.

Use transactions/constraints and canonical locking/idempotency primitives, not in-memory mutexes.

### Dead-letter behavior

Provider deliveries exceeding retry policy enter shared dead-letter visibility. Notification domain status and Delivery truth remain explicit. A DLQ record is not a `NotificationDeliveryStatus` substitute.

### Scheduled work

Potential Notification scheduled work:

- disable confirmed dead subscriptions;
- expire stale queued notifications according to the approved expiry ruling;
- reconcile provider state where provider APIs support it.

No Messaging retention cleanup schedule is approved. Do not create one until retention policy exists.

### Saga boundaries

CL-07 should not own global business sagas. Notification delivery is a local asynchronous workflow. Privacy and Moderation own their cross-Module orchestration and invoke CL-07 handlers.

---

## 17. Provider Integrations

### Provider-neutral rule

```text
Notification owner
→ provider-neutral channel port
→ selected adapter
→ external provider
→ verified/normalized result
→ NotificationDelivery / NotificationSubscription transition
```

Source Modules must not import generic Notification provider SDKs for email, SMS, or push alert delivery; Identity verification-provider transport is governed by Section 15.

### Email

The current Project Overview names AWS SES for email. The Notification registry also contains generic “Email provider” / “Transactional email provider” evidence and flags AWS SES as an inconsistent compliance item. **Architecture Ruling:** treat SES as the current Workin Ants email transport choice where root provider configuration confirms it, but keep a Notification-owned provider-neutral email port. The provider is a rail, not Notification truth.

### SMS

The Project Overview phrase “AWS SES for Email and SMS” does not establish a generic SMS provider. **U-CL07-16 remains unresolved only for initial production generic SMS provider selection.** Identity verification-provider transport follows the approved boundary in Section 15.

### Web Push

Schema/provider vocabulary supports `web_push`, `fcm`, `onesignal`, and `wonderpush`, but no single MVP push strategy is selected. **Unresolved Decision:** select the initial web-push provider strategy before production external push. The adapter boundary must allow one initial provider without requiring all optional adapters.

### Webhook verification

For any provider callbacks:

1. verify raw signature before parsing;
2. dedupe provider event through Notification-owned processed-event truth using shared mechanics;
3. validate structured payload;
4. translate provider status in Notification adapter;
5. apply idempotent Notification transition;
6. log/metric/failure with redacted metadata.

### Provider-event truth

Do not reuse `ProcessedStripeEvent`, `ProcessedCalendarEvent`, or `ProcessedVideoProviderEvent`. Notification needs its own provider-event truth if asynchronous callbacks are implemented. The exact schema is unresolved.

### Reconciliation

Providers with query APIs should support scheduled/admin reconciliation using SH-062 `reconcileProviderState`. Automatic repair must be limited to discrepancies Notification can safely resolve without changing source business truth.

---

## 18. Search / Projection Boundaries

CL-07 has no public-search projection responsibility.

Binding rules:

- private Thread and Message content must not be sent to Typesense/public Search;
- Notification records and device subscriptions are not public-search entities;
- no `SearchUpsertEvent` should be generated for ordinary CL-07 lifecycle transitions;
- if a future private inbox search feature is approved, it must be designed as a private authorized projection and must not reuse public-search assumptions without an architecture decision.

Realtime inbox updates and unread counts are not Search projections.

---

## 19. Media / File Boundaries

### Context ownership

`MessageMedia(messageId, mediaId)` is Messaging truth. It means “this already-safe MediaAsset is attached to this Message.” It does not make the file safe or accessible by itself.

### Media ownership

Media / File Access owns:

- upload policy/session;
- object key generation;
- binary validation;
- malware scanning;
- image processing/metadata scrubbing;
- MediaAsset readiness/freeze/erasure;
- storage provider interaction;
- MediaAccessGrant;
- signed URL issuance and access events.

### Access composition

A message attachment read requires:

```text
Identity actor
+ Role/Thread participation authorization
+ Messaging contextual attachment fact
+ Healthcare/sensitivity decision if applicable
+ MediaAsset readiness/freeze/erasure checks
+ Media grant/signed URL mechanics
```

Messaging must never return raw storage keys or permanent private file URLs.

For MessageMedia access, Messaging exposes its owner-specific SH-026 `authorizeContextualResourceAccess` decision bound to the actor, Thread, Message, MediaAsset, and requested action. It returns the contextual allow/deny decision and safe evidence; `ThreadParticipant` or `MessageMedia` facts alone are not authorization. Media consumes that decision through `requestMediaAccess`, independently applies MediaAsset readiness, safety/freeze/erasure, grant, and TTL rules, and owns downstream SH-087 `issueSignedMediaUrl`. Media must not reconstruct Messaging participant/access policy; Messaging must not issue signed URLs or call SH-087 directly.

### Notification payloads

Notification has no attachment model in current evidence. Do not attach files directly to push/email/SMS by bypassing Media. Use authenticated action routes to the owning application context.

---

## 20. Privacy / Retention

### Privacy ownership

Privacy / Data Erasure owns request verification, request/job/target lifecycle, target ordering, retention exemptions, export orchestration, and final completion.

### Messaging privacy executor responsibilities

Messaging must be able to enumerate and execute instructions for:

- `Thread` metadata and `erasedAt`;
- `ThreadParticipant` subject links where legally/relationally permitted;
- `Message.content`;
- nullable `Message.senderId` anonymization where instructed;
- `Message.deletedAt` versus `Message.erasedAt` distinction;
- `MessageMedia` contextual joins when detachment/deletion is instructed.

The exact field-level retention/anonymization policy for ordinary, disputed, healthcare, support, and legally preserved conversations is **unresolved legal/policy input**. Implementation must execute an approved disposition; it must not invent statutory retention periods.

### Notification privacy executor responsibilities

Notification must enumerate/execute against:

- Notification user/organization references and content/payload fields;
- NotificationDelivery provider IDs/failure metadata where erasable;
- NotificationSubscription device/reachability metadata and credentials;
- NotificationSubscriptionEvent personal/device metadata;
- provider-side deletion/revocation through Notification's provider adapter when supported and instructed.

### Retention facts

Each CL-07 owner exposes SH-097 `evaluateRetentionRequirement`; Privacy records `DataRetentionExemption`. Audit proof necessary to prove privacy execution may remain according to Audit/Privacy policy; CL-07 must not delete the proof ledger directly.

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

### Product deletion vs erasure

- `Message.deletedAt` = normal product deletion/hiding.
- `Message.erasedAt` = owner execution marker within a Privacy-controlled workflow.
- `Thread.erasedAt` = local erasure marker, not PrivacyRequest completion.
- Notification deletion/erasure semantics are not currently modeled by dedicated fields; privacy handler behavior must be explicit and idempotent.

---

## 21. Audit and Observability

### Audit

Use SH-029 `appendAuditEvent` for important actions where generic action proof is required, such as subscription revocation, administrative delivery intervention, or moderation/privacy execution acknowledgement.

Use SH-030 `recordSensitiveAccess` for protected data access, such as approved healthcare/private message reads/download gates when policy requires it.

Do not create:

- `MessageAccessLog` as a substitute for `AccessAuditLog`;
- `NotificationAuditLog` as a generic audit system;
- mutable “last admin viewed” flags as compliance proof.

### Domain evidence remains local

- Message lifecycle timestamps remain Messaging truth.
- NotificationDelivery remains transport attempt truth.
- NotificationSubscriptionEvent remains Notification device/event evidence.
- These records must not be merged into AuditEvent.

### Observability

Every worker/provider path should include:

- correlation/request IDs;
- structured safe logs through SH-033 `writeStructuredLog`;
- metrics for queue depth, latency, attempts, delivery outcomes, subscription failures;
- exceptions through the single monitoring adapter;
- SH-037 `recordIntegrationFailure` for meaningful provider/worker degradation through the public capability;
- dead-letter visibility.

**CL-07-R007 — Observability persistence boundary:** CL-07 consumes approved public capabilities for failure recording, queue telemetry, health, structured logging, metrics, and exception capture. `IntegrationFailure`, `QueueJob`, `OpsIncident`, and `SystemEvent` are not current Prisma models. CL-09 owns its unresolved persistence/status design. CL-07 must not create local substitutes or couple Messaging/Notification business status to any future operational record.

### Telemetry redaction

Never put the following into generic logs/metrics/error metadata:

- private Message bodies;
- PHI;
- OTPs/recovery tokens;
- raw push endpoints/tokens/keys;
- tax/financial details;
- resumes;
- contract text;
- raw provider payloads containing unnecessary personal data.

---

## 22. Security Boundaries

1. **Server-side validation:** all commands, client callbacks, webhook payloads, template variables, action routes, and provider results are runtime-validated.
2. **Authorization:** every protected resource operation passes Identity + Role/Authority; client IDs are references, not authority.
3. **RLS:** align RLS with participant/recipient scope as defense in depth.
4. **Credential storage:** push endpoint/token/key material must use hashed identifiers for matching and encrypted values only when recovery is necessary.
5. **Plaintext conflict:** current `NotificationSubscription` contains plaintext endpoint/token/`p256dh`/`auth` alongside encrypted/hash fields. Production implementation must not treat both as authoritative. See approved target-authority ruling PR-N04; migration details remain U-CL07-18.
6. **Action routes:** external notification action routes must be HTTPS and restricted to an approved authenticated application route contract; arbitrary URLs are prohibited.
7. **Payload minimization:** outward channels get minimum safe data. Authentication page fetches source truth after click.
8. **Webhook authentication:** verify raw signatures before parsing or side effects.
9. **Replay protection:** use canonical idempotency and provider-event dedupe.
10. **Rate limits:** message send, direct/support thread creation, notification intake exposed to broad callers, permission/subscription mutation, and report actions require abuse-aware rate limits according to root policy.
11. **No provider secrets in client:** VAPID/public keys may be client-safe as designed; secret provider credentials remain server-only.
12. **No push token as auth:** NotificationSubscription is reachability, never authentication.
13. **No provider callback as domain event:** callback becomes Notification truth only after verification/dedupe/translation/application.

---

## 23. Testing Architecture

### Module unit tests

Messaging:

- Thread context binding validation;
- participant membership/current-user facts;
- send/edit/delete rules;
- monotonic read cursor;
- MessageMedia contextual checks;
- safe serialization/redaction application.

Notification:

- request validation;
- recipient resolution contract;
- channel eligibility;
- template variable schemas;
- payload sensitivity rules;
- action-route allowlist;
- subscription permission/status consistency;
- provider status mapping;
- delivery aggregate behavior once approved.

### Public-interface contract tests

- SH-113 `ensureContextThread` owner-facts contracts for each supported context;
- `getThreadParticipantFacts` with Role / Authority;
- Media attachment facts/access bridge;
- SH-041 `requestNotification` typed contract used by representative source Modules;
- organization recipient-facts query;
- Privacy enumeration, SH-097 `evaluateRetentionRequirement`, and execution protocols;
- Moderation target/execute protocols.

### Lifecycle transition tests

- Message create/edit/delete/erasure markers do not collapse into one state;
- Notification and Delivery transitions reject illegal regressions;
- Subscription status and permission changes follow approved invariants;
- dead token handling disables reachability without disabling User identity.

### Cross-Module integration tests

- Message commit succeeds even if Notification delivery fails;
- Role decision uses Messaging participant facts, not duplicate policy;
- attachment access requires both Messaging and Media gates;
- healthcare admin view returns allow/redact/block and access audit proof;
- Notification uses Organization-owned routing facts without mutating membership/settings.

### Provider tests

- adapter contract tests with mocked provider responses;
- signature verification fixtures;
- unknown provider status handling;
- idempotent callbacks;
- transient/permanent failure classification;
- token-invalid response disables subscription only after adapter-confirmed condition;
- reconciliation dry-run and repair boundaries.

### Idempotency/concurrency tests

- concurrent ensureContextThread converges under unique FK;
- duplicate `sendMessage` idempotency key creates one Message;
- stale read cursor cannot move backward;
- duplicate notification request creates one semantic effect;
- duplicate provider callback has one side effect;
- token refresh race does not restore stale endpoint.

### Compliance/privacy tests

- no prohibited sensitive fields in external payload fixtures;
- browser permission and ConsentLog remain separate;
- product delete differs from legal erasure;
- Privacy handler mutates only CL-07 records and returns explicit outcomes;
- sensitive message access records AccessAuditLog where required;
- DMCA/FCRA delivery proof does not mutate legal workflow state.

### E2E critical journeys

1. Order/Gig/Application participant opens context Thread, sends Message, other participant receives safe in-app alert.
2. Message attachment remains private and requires authorized signed access.
3. User grants push permission, creates subscription, receives safe test alert, then revokes device.
4. Provider delivery fails transiently, retries, and surfaces operational evidence without duplicating source alert.
5. Privacy target erases/anonymizes approved Messaging/Notification data without marking the entire privacy request complete inside CL-07.

---

## 24. Invariants

### Rules coding agents must never violate

1. A `Message` is not a `Notification`.
2. Messaging owns `Thread`, `ThreadParticipant`, `Message`, and contextual `MessageMedia` truth.
3. Role / Authority interprets permissions but must not own or mutate ThreadParticipant lifecycle truth.
4. Media / File Access owns `MediaAsset`, file validation, storage, grants, and signed URL mechanics; Messaging only owns attachment context.
5. Notification owns `Notification`, `NotificationDelivery`, `NotificationSubscription`, and `NotificationSubscriptionEvent` truth.
6. Generic business email/SMS/push alerts must use SH-041 `requestNotification`; the Identity-owned verification-provider protocol is the explicit exception described in Section 15.
7. Notification may not update the Order, Booking, Job, Message, ComplianceHold, ModerationCase, Subscription, Entitlement, Security, FCRA, or DMCA lifecycle that caused the alert.
8. Provider status is not Notification truth until verified, deduplicated, translated, and applied by Notification.
9. Delivery success is not proof of user attention; click/open is not proof of source workflow completion.
10. ConsentLog is versioned disclosure proof; browser permission is device state; NotificationSubscription is reachability; NotificationDelivery is delivery evidence.
11. Realtime transport never replaces persisted Thread/Message truth.
12. No source Module may insert or update Thread/Message records directly to “save a call.”
13. No CL-07 code may create a feature-local authentication or authorization system.
14. No CL-07 code may create a local PrivacyRequest, DataErasureJob, DataRetentionExemption, Report, ModerationCase, ComplianceHold, AuditEvent substitute, or IntegrationFailure substitute.
15. Privacy orchestrates; Messaging and Notification execute only against their own truth.
16. Audit evidence and observability records do not replace Messaging/Notification lifecycle records.
17. Message attachments must pass both conversation-context access and Media access/readiness gates.
18. Private Message bodies, PHI, OTPs, financial/tax details, raw resume details, identity documents, contract text, and raw provider credentials must not appear in outward push payloads or generic telemetry.
19. `Message.deletedAt` must never be treated as legal erasure completion.
20. `Message.erasedAt` or `Thread.erasedAt` must never be treated as PrivacyRequest completion.
21. Search must not index private Message, Thread, Notification, Subscription, or Delivery truth by default.
22. Track Subscription & Entitlement remains commercial policy truth. CL-07 must not create local “premium messaging,” “premium notifications,” or entitlement booleans without an explicit owner rule.
23. Current unique typed Thread foreign keys must be respected until an approved migration changes them.
24. No Booking/Dispute/Review ThreadContextType may be added silently.
25. Notification's push-provider enum must not be reused as an email/SMS provider enum.
26. Duplicate notification delivery/queue/idempotency frameworks are prohibited.
27. A Notification action URL must not be an arbitrary external redirect.
28. Push endpoint/token values must not be logged, exposed in account responses, or used as authentication.
29. Provider callbacks must authenticate and replay-protect before state mutation.
30. Unresolved provider, retry, recipient, aggregate-status, and privacy-policy questions must not be “solved” inside feature code without updating this architecture.

---

## 25. Prohibited Duplicate Implementations

Coding agents must not create CL-07-local substitutes for canonical operations or neighboring Module truth. High-risk duplicate names/patterns include:

- `chat-auth.ts`, `message-auth.ts`, `notification-auth.ts`, `current-user-for-chat.ts`;
- `chat-permissions.ts`, `thread-permissions.ts`, `notification-permissions.ts` as independent policy engines;
- `OrderChat`, `GigChat`, `ApplicationChat`, `InterviewChat`, `BookingChat`, `DisputeChat` tables;
- a generic `Communication` table merging Message and Notification;
- `MessageAttachment` byte-storage service parallel to Media / File Access;
- Messaging-owned email/SMS/push clients;
- source-Module generic-alert SES/Twilio/FCM/OneSignal calls (Identity verification-provider protocol excluded);
- `pushConsent`, `webPushConsent`, or subscription-owned consent tables replacing ConsentLog;
- `MessageAccessLog` or `ThreadAudit` replacing AccessAuditLog;
- `NotificationAuditLog` replacing AuditEvent;
- `NotificationFailure` replacing IntegrationFailure while also duplicating Delivery failure truth;
- `notificationQueue`, `messageQueue`, custom retry scheduler, or custom dead-letter framework parallel to canonical queue primitives;
- global provider-status mapper mixing Notification, Payment, Calendar, Video, Verification, or Subscription status semantics;
- Notification use of `ProcessedStripeEvent`/`ProcessedCalendarEvent`/`ProcessedVideoProviderEvent`;
- feature-local encryption/hash helpers for push credentials;
- private-message Typesense index or public-search updater;
- Messaging-owned PrivacyRequest worker or Notification-owned global privacy crawler;
- local `isBlocked`, `isPremium`, `canNotify`, or similar flags substituting for owner decisions where no CL-07 lifecycle owns them.

---

## 26. Deferred / Unresolved Decisions

Unresolved issues are explicit blockers only for the work identified below. Coding agents must not silently settle them.

| ID | Question | Why unresolved | Missing evidence / decision | Blocks |
| --- | --- | --- | --- | --- |
| U-CL07-01 | Does each typed business object permanently have exactly one Thread? | Prisma typed FK fields are `@unique`, but Module extract questions whether this is intended product policy. | explicit product/Module ruling | schema changes that would permit multiple threads per context; current implementation must honor unique schema |
| U-CL07-02 | Does Booking or Review/Dispute reuse an Order Thread or need new ThreadContextType values? | consumers exist, but enum lacks those contexts | owner workflow decision | booking/dispute-specific thread creation |
| U-CL07-03 | What identifies duplicate direct Threads / group direct conversations? | no canonical participant-set key | direct-thread product semantics | direct-thread dedupe; direct threads may be deferred |
| U-CL07-04 | Is `support` Thread itself sufficient or must it link to a support-case lifecycle? | enum exists; no support-case model | support architecture | support-case tooling, not basic messaging |
| U-CL07-05 | How are moderation hidden/frozen/restricted states represented without misusing deletion? | no Thread/Message moderation status | Moderation enforcement contract/schema | production moderation enforcement on messages |
| U-CL07-06 | What exact healthcare lookup granularity applies to Thread/Message reads? | sensitivity exists; inheritance/materialization unclear | Healthcare public-interface contract | production healthcare-sensitive messaging |
| U-CL07-07 | Which Message/Thread reads require AccessAuditLog? | access actions exist, exact policy not supplied | compliance/audit policy | production sensitive-access logging policy |
| U-CL07-08 | What retention/anonymization rules apply by conversation type? | legal policy not specified | Privacy/legal retention inventory | destructive production privacy execution / retention cleanup |
| U-CL07-09 | What is the canonical Notification recipient model for User vs Organization targets? | both FKs optional; push subscriptions are User-only; no snapshot model | recipient cardinality/fan-out ruling and possible schema constraint | organization-target notification routing |
| U-CL07-10 | Is one Notification channel-specific or a multi-channel parent? | channel exists on both parent and Delivery | aggregate/channel ruling | multi-channel notification production behavior |
| U-CL07-11 | How is Notification aggregate status computed across Delivery attempts? | enum lacks explicit aggregate policy | status ruling | final multi-delivery status reducer |
| U-CL07-12 | How are expiry and dismissal time represented? | `expiresAt` exists; no expired status; dismissed has no timestamp | schema/lifecycle ruling | expiry worker and complete dismissal evidence |
| U-CL07-13 | Does each retry create a new Delivery row, and what fields correlate attempts? | current Delivery lacks attempt metadata | retry proof/schema ruling | production retry history |
| U-CL07-14 | What Notification-owned processed provider-event record is used for callbacks? | canonical rule says separate truth; no schema exists | provider-event schema | async provider receipts/webhooks |
| U-CL07-15 | Which provider vocabulary represents email and SMS deliveries? | current Delivery provider enum is push-specific | schema/provider vocabulary decision | trustworthy provider reporting for email/SMS |
| U-CL07-16 | Which initial generic SMS provider is used? | production generic SMS provider remains unselected; Identity verification-provider ownership is resolved by CL-07-R002 | Notification generic SMS provider selection | production generic SMS alerts |
| U-CL07-17 | Which initial Web Push adapter is selected? | multiple optional providers are listed | provider selection | production web-push adapter |
| U-CL07-18 | What exact uniqueness/backfill/rotation/cutover contract implements approved PR-N04? | target authority is settled; current plaintext constraints coexist with encrypted/hash fields | provider/platform/hash key, backfill, rotation, constraint replacement order, temporary compatibility if any | production subscription credential migration/storage |
| U-CL07-19 | What is the canonical Notification interaction record? | click/open/close overlap across parent, Delivery, SubscriptionEvent | interaction ownership ruling | selection or durable writes of canonical click/open/close evidence; read/dismiss commands remain separate established behavior |
| U-CL07-20 | What are the controlled Notification template-name catalog and versioning governance rules? | canonical op exists; `name` is free string; no persisted template schema | template registry approval process | production source-template integrations |
| U-CL07-21 | What exact safe payload schema applies per sensitivity × channel? | labels exist but JSON is unrestricted | payload allowlist catalog | all external production delivery |

### Ruling Status

PR-N04 is approved only for target credential authority as stated below. All other Proposed Rulings in this section retain their existing status and become binding only when explicitly approved.

**PR-N01 — Notification request fan-out is explicit.** SH-041 `requestNotification` accepts semantic intent plus recipients/channel requirements; Notification performs fan-out. Source Modules never create Delivery rows.

**PR-N02 — Prefer channel-specific Notification records.** Because `Notification.channel` exists and read/dismiss semantics are naturally in-app-specific, treat each Notification row as one resolved target/channel semantic alert, with `NotificationDelivery` rows representing attempts for that same channel. A single request may create multiple Notification rows. Approval should be accompanied by target/cardinality constraints.

**PR-N03 — One Delivery row per attempt.** Preserve attempt history by creating a new `NotificationDelivery` per provider attempt rather than overwriting repeated failures. Add correlation/attempt/idempotency fields if required by migration. Aggregate Notification status is derived by channel-specific policy rather than queue state.

**PR-N04 — Approved target credential authority (CL-07-R010).** Production recoverable provider credential material uses approved encrypted storage through SH-075 `encryptSensitiveValue`; stable comparison/identity uses normalized purpose-bound hashes through SH-076 `normalizeAndHashIdentifier`. Plaintext `endpoint`, `token`, `p256dh`, and `auth` must not remain parallel authoritative representations after migration, and code must not treat plaintext and encrypted/hash values as equal source truth. U-CL07-18 remains unresolved for exact provider/platform/hash composite uniqueness, backfill, rotation during cutover, replacement order of plaintext uniqueness constraints, and any temporary compatibility period. This approval is not a migration design or permission to change current schema/constraints without separate review.

**PR-N05 — Controlled code-based notification template registry for MVP.** Use typed keys, explicit versions, per-channel variable schemas, sensitivity classification, and safe action-route builders. Do not create a mutable database template lifecycle until product requirements justify it.

**PR-M01 — Current typed-context uniqueness is binding until changed.** SH-113 `ensureContextThread` must converge on the single row allowed by current `@unique` constraints. This does not decide whether future architecture should support multiple threads.

**PR-M02 — Realtime event emission is post-commit only.** Realtime payloads derive from committed Messaging truth and may be safely dropped/recovered by refetch; they must not participate in the database transaction as source truth.

---

## 27. Architecture Decision Summary

1. CL-07 is a communication rail, not a lifecycle-owning super-domain.
2. Messaging owns conversation records; Notification owns alert/delivery/reachability records.
3. `ThreadParticipant` is Messaging truth; Role / Authority owns permission interpretation.
4. `MessageMedia` is Messaging contextual truth; Media / File Access owns MediaAsset/file mechanics.
5. Source Modules use SH-041 `requestNotification` for generic alerts; Identity verification-provider transport remains Identity-owned.
6. Notification owns safe rendering, routing, delivery attempts, provider status translation, and dead-subscription handling.
7. Consent, browser permission, subscription reachability, provider delivery, and user interaction remain separate evidence.
8. Messaging requests Notification using safe metadata after Message commit; Notification must not read private Message bodies in the delivery transaction.
9. Shared queue, idempotency, event, webhook, retry, crypto, audit, and observability primitives are reused and not rebuilt locally.
10. Privacy owns orchestration; CL-07 Modules expose enumerate/execute handlers over their own records.
11. Moderation owns case/decision truth; Messaging executes approved enforcement through a public contract.
12. CL-07 has no public-search projection responsibility.
13. Current schema constraints are honored until approved migrations change them.
14. Provider selection and several Notification aggregate/schema issues remain explicit unresolved decisions; provider-neutral ports allow core work to proceed with stubs/in-app delivery without inventing policy.

---

## 28. Coding-Agent Usage

Before changing CL-07, an implementation agent must read, in this order:

1. [project overview V3](<../../project-overview-v3.md>);
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry;
5. this [CL-07 architecture](<messaging-notification-rail-architecture.md>);
6. this [CL-07 build plan](<messaging-notification-rail-build-plan.md>);
7. the target Module's `module-architecture.md`;
8. the target Module's `implementation-plan.md`;
9. relevant dependency Module public-interface sections, especially Identity, Role / Authority, Consent, Media, Healthcare, Privacy, Moderation, Audit, Organization Hiring, and the business context owner;
10. `progress-tracker.md`.

Before implementation, the agent must also check the Unresolved Decisions table. If the requested feature depends on an unresolved decision, stop and obtain the architecture ruling rather than encoding an assumption in code. If implementation discovers a binding conflict with this file, update architecture first, then adjust the build plan; never let build progress silently become architecture.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.


## WA-R021 — Notification recipient and attempt model

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R021 contract](../../reconciliation/platform-architecture-rulings.md#wa-r021--notification-recipient-and-attempt-model) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one logical Notification per resolved User recipient and semantic source intent; channels are deliveries of that notification. Organization is source/context, not an inbox principal. Hiring supplies the authorized recipient set and source-policy version; Notification expands/deduplicates User recipients and snapshots the resolved routing context. Revalidate current sensitive access before including protected payload or dereferencing context; a historical fan-out snapshot grants no future access. Source Modules own recipient eligibility and message meaning; Notification owns safe rendering, channel routing and provider mechanics.

Each delivery attempt has its own immutable attempt identity and correlation to logical notification, recipient, channel, destination generation and semantic send key. Retrying unknown provider outcomes reconciles before resending. Provider acceptance is not confirmed delivery or user interaction. Notification summary separately tracks pending/in-progress, partial success, all required routable deliveries successful, or exhausted failure; dismiss/read state remains independent and never alters source workflow status. The database pass must provide a representation for partial delivery rather than mapping it to total success. Policy may mark a channel optional; that requirement is snapshotted before dispatch, not rewritten to hide failure.

Persist dismissedAt/expiresAt when these actions/policies apply. User interaction is Notification-owned append-only evidence separate from Delivery receipts. Template versions are immutable and schema-validated; source supplies a registered semantic template intent plus allowlisted variables. Generic external channels carry minimal safe summaries/deep links, never raw message bodies, financial/tax documents, exact addresses or regulated data by default. Identity challenge-provider transport stays Identity-owned. Concrete provider selection/configuration and legally sufficient notice delivery remain external prerequisites.

Tradeoff: explicit parent/attempt representation needs schema alignment but avoids multiple inbox items per channel and false completion. Acceptance: organization fan-out dedupe, removed member sensitive access, duplicate send, partial channel failure, expiry/dismissal independence, callback before/after retry, unsupported channel and secret redaction.

## WA-R027 — Identity mapping, assurance concurrency and security evidence

Classification: AI_RESOLVED_WITH_TRADEOFF. Applies to Identity and Role contracts; provider capability and legal retention remain scoped external requirements.

Use a stable local Workin Ants User UUID, independent of provider subject. Resolve every authenticated provider subject through an Identity-owned linkage keyed by adapter issuer/tenant plus normalized subject; uniquely bind that identity to one local User. Existing UUIDs are preserved, including any that happen to equal provider UUIDs. Migration must inventory existing bindings and quarantine collisions rather than remap foreign keys or assume equality. RLS resolves the verified provider subject to local actor through the same mapping contract; clients cannot supply their own local actor identity. This accepts PR-IA-05 and resolves U-IA-01 without claiming current nullable/index-only Prisma constraints already enforce it.

User.email is the locally selected verified account contact; AuthProviderAccount.email is provider evidence, not an automatic overwrite source. An explicit email-change flow verifies control of the new address, checks uniqueness under lock, requires action-bound assurance for the existing account, records evidence and notifies the prior verified channel. A changed provider claim alone never changes the canonical contact. Linking requires fresh proof of control of both the current local account and new provider identity; matching email never merges accounts. Conflicts return a non-enumerating review result; no automatic merge or reassignment. Actual account consolidation is unsupported until a separate owner-reviewed migration contract exists.

Age eligibility must precede local User creation. OAuth starts with a short-lived single-use server-bound pre-account attempt carrying nonce/state, intended provider, redirect allowlist and age-policy proof reference. The callback validates provider/state and rechecks proof applicability before atomically consuming the attempt and creating/linking User. A provider-created shadow identity is not a local User or access authorization. Provider auto-provision triggers that bypass this contract must be disabled before OAuth activation. Persist the evaluated policy version, jurisdiction source/version, applicable threshold, decision/reason and evaluated timestamp alongside minimized subject binding. Legal thresholds, eligible regions and proof retention require approved policy; no numerical policy is invented. AgeGateBlock requires at least one usable approved hashed matching identifier (PR-IA-04).

Identity owns StepUpActionType registration and assurance mechanics; each domain owner proposes a namespaced action/target/purpose and Role binds its permission and required assurance. Unknown or unregistered `other` actions cannot authorize sensitive work. Keep OTP verification provider-managed at launch; store provider challenge reference and terminal evidence, not local OTP/hash verification state. A local OTP verifier would require a separate security design. Existing five-minute SMS OTP and fifteen-minute recovery email-token policies are not changed by this ruling. Exact sensitive-action grant TTL/attempt thresholds are versioned security configuration, bounded by actual provider capability and tested before activation.

Allow at most one pending challenge per actor/action/target/purpose. Same command key replays it; a conflicting new request does not silently invalidate another challenge. An explicit authorized replacement cancels the old challenge and invalidates its unconsumed assurance under the same lock. Different independent scopes may coexist; proof cannot cross scopes. Allow at most one nonterminal recovery per User; identical initiation replays and a different initiation returns conflict without exposing account existence. Cancellation followed by a newly authorized initiation creates a new request. Terminal recovery/challenge records are immutable; no reopening them into success. Recovery manual review records reviewer, authority, reason, evidence versions and disposition in Identity-owned security history, and resumes only the next evidence-supported stage. Review approval cannot substitute for required possession/verification proof. ComplianceHold is requested separately only for a registered protective action; it is not recovery truth.

Containment matrix: compromise, completed recovery and verified phone replacement revoke all prior sensitive-action grants and invalidate pre-change sessions via a local security epoch before access can resume. Compromised credentials remain terminal. Revoking a single uncompromised passkey revokes that credential and its dependent grants/sessions; if the provider cannot reliably identify session dependency, invalidate all prior sessions. Privileged role changes invalidate authorization/assurance snapshots; permission removal takes effect on the next protected request regardless of provider session lifetime. Each protected request checks current local epoch/revocation and current Role facts, so provider revocation latency never retains local privilege. Queue and reconcile provider-wide revocation separately, recording failures; do not claim the provider has revoked until it acknowledges.

Security tiers describe account-security risk only: versioned Identity policy may escalate standard→elevated/high_risk or elevated→high_risk on an authenticated incident; de-escalation requires an authorized security review with resolved evidence and a new history entry. A successful ordinary login/OTP does not de-escalate risk or clear a lock. No automatic risk scoring thresholds are invented. Local locks have their own reason/effective window; neither tier nor lock mutates business compliance lifecycles. Credential revoked/compromised states are terminal; create a fresh verified credential/linkage with supersession evidence for subsequent access. `passkeysEnabled`, `smsMfaEnabled`, `backupPasswordConfigured` and `lastStepUpAt` remain summaries; backup password verification belongs to the authentication provider, never local password storage (PR-IA-02/03).

Identity retains account-level display defaults and private account contact/location text; Customer, Candidate, Professional and Organization own their contextual display and publication projections. Generic User.isPublic never authorizes discovery, exact-location disclosure or a profile's visibility. Profile/avatar Media use stays behind the contextual owner and Media validation/access contracts. Accept append-only UserSecurityEvent and versioned transactional outbox separation (PR-IA-07/08). Provider receipt/effect records follow WA-R018; exact table naming is a migration detail, not an unresolved ownership decision. Required security/age/recovery retention and new consent categories remain externally gated; do not infer them from technical fields.

Acceptance before implementation activation: duplicate provider provisioning, conflicting issuer/subject link, equal-email takeover attempt, OAuth callback replay/cross-provider swap, unsupported pre-account trigger, concurrent challenge/recovery initiation, revoked epoch on existing provider session, permission removal with stale authorization cache, manual review lacking required proof and unavailable provider revocation. Test the local containment decision independently from transport success. This amendment supersedes the named U-IA technical alternatives; it does not certify adapter capabilities, migration provenance or legal policy.

## WA-R031 — Authority policy, Customer lifecycle and shared review claims

Classification: AI_RESOLVED_WITH_TRADEOFF. Role interprets authority, Identity/Hiring/Messaging retain role/membership/participant lifecycle. No general admin bypass is created.

Use a versioned code-first Role action/resource policy catalog with explicit owner, accepted actor scopes, minimal owner-facts contract, allowed relationships, freshness/version requirements, sensitive-access proof and step-up obligations. Each protected owner public command/query registers one canonical action before activation; unknown/unregistered action denies. Human-readable action names derive from the owning interface rather than a new generic Cluster service. Roles alone never waive source lifecycle, Hold, commercial, Healthcare or privacy checks. An admin may perform only explicitly registered admin actions; support is limited to authorized support views/intake and attributed on-behalf actions, not role assignment, money movement, restoration or unrestricted evidence access by virtue of support role alone. Financial/adjudication/security operators require the specifically granted action and fresh assurance. Additional access needs a catalog amendment, not `isAdmin` fallback.

Organization matrix: owner may manage membership/administrators, transfer ownership through Hiring's checked workflow, and manage hiring resources; admin may manage ordinary hiring resources and recruiter membership, but cannot replace/remove the owner, self-promote or grant owner authority; recruiter may manage assigned Jobs/applications/interviews subject to Hiring/Candidate/Interview facts, but not organization ownership, membership administration or billing. Member/viewer values remain inactive/deny-by-default until a separately defined action set exists. Current relationship facts are queried from Hiring; removed membership takes effect on the next protected request. Thread membership is Messaging truth, never inferred from having an Organization role. Identity appends immutable UserSecurityEvent/Audit intent for platform-role assignment/revocation in the same mutation transaction; no second Role-owned role table.

Server services enforce Role policy before owner operations. Use handwritten reviewed RLS/SQL implementations where database-side policy applies, with one shared semantic fixture matrix comparing server/RLS allowed and denied cases. Do not generate SQL from arbitrary executable application predicates. Baseline protected domain tables deny direct anonymous/authenticated client CRUD; exposed read models require a separately reviewed allowlist and RLS policy. Server credentials do not eliminate owner checks. Enumerate every table/view/function exposed to API/database roles in the migration review; no unreviewed relation becomes public by default. Add identity-map-aware policies under WA-R027 rather than assuming provider subject equals User.id. This is the parity/coverage method; actual grants/RLS/schema replay stay under database readiness. Keep authorization cache and Role domain events absent at launch; add caching only with proven revocation/version invalidation, and events only for a real consumer.

Return the same safe public response for missing versus unauthorized private targets where existence is sensitive. Preserve distinct internal reason classes unknown_action, insufficient_authority, missing_relationship, stale_or_unavailable_facts, step_up_required and policy_unavailable for diagnostics and authorized UI handling. Never make outage equivalent to allowed. Resource owners choose a purpose-limited safe denial message; internal IDs, evidence and reason details are not automatically public. WA-R023 durability still governs protected disclosure. Concrete owner DTO field sets remain bilateral qualification work; no universal `queryOwnerFacts` DTO is adopted.

CustomerProfile lifecycle: normal idempotent provisioning produces active after Identity eligibility. Optional draft can activate only through Customer validation; self-service active↔paused controls new buyer participation. Customer owner may archive active/paused/draft after checking obligations; archiving stops new buyer actions and retains access needed to fulfill existing Orders, Bookings, disputes, refunds and statutory requests under those owners' current permissions. Archive does not cancel a transaction, discharge debt, erase proof or hide an active restriction. Restoration of archived returns to draft for current eligibility checks; suspension is a separate authorized owner action with reason/history, not a mirrored Hold. Only an authorized owner/moderation restoration with current checks may leave suspended; self-service pause/archive/restore cannot clear it. Privacy deletion/anonymization is its own approved executor path. No automatic status transition on receipt of a generic Hold event.

Persist append-only Customer lifecycle evidence (typed owner event record or retained lifecycle journal) alongside the state change because archive/restoration and obligations now require reconstructible history; outbox dispatch retention alone is insufficient. This specifically supersedes the prior no-dedicated-history-unless-required proposal by supplying the requirement, without requiring a second generic platform ledger. Customer's contextual display fields override account display defaults only within Customer views. Copy defaults once on provisioning with provenance; do not synchronize later edits bidirectionally. Customer remains absent from public discovery; this does not change Candidate/Professional public projections. Customer avatar is an explicit Customer-owned MediaAsset FK/reference with retention-safe deletion and Media validation, not a polymorphic attachment repository. Existing legacy buyer User references backfill through the one-profile-per-User owner resolver; preserve original attribution and quarantine mismatches, never choose by display name/email. Review/Dispute bind the authoritative Order participant identities under WA-R026.

Adopt feature/Module-first logical domain/application/contracts/infrastructure/workers/privacy separation where relevant; adapters/routes are thin. These are ownership boundaries, not permission to reorganize current code or create a generic CL-01 domain service. A Module references another owner's public contract, not foreign repository/entity ownership. Remove obsolete Identity `TrackEntitlement` schema reference: Identity's actual documented dependency is supplying User facts to Track, not reading either entitlement definitions or grants. Do not guess a replacement schema or create the obsolete model.

SH-054 shared work claiming is a persistence capability: claim by work-kind/owner item ID with holder, lease deadline, monotonically increasing fencing token and expected owner version; renew/release/complete compare token. Expired holder cannot commit a decision or acknowledge another holder's work. Manual reviewers obtain Role authority and domain evidence separately; a lease does not approve a case. Review workflow truth remains in the owning Module. Use the shared Postgres transaction/locking layer, not a new generic moderation/recovery case. Capability activation requires concurrent claim, stale holder, renewal failure and crash/reclaim tests. Proposed registry status remains until concrete shared API qualification; technical placement is resolved.

Acceptance: public/client table access denied unless explicitly reviewed; server/RLS parity; stale membership and private-target denial; support cannot escalate; owner transfer cannot lose the final owner; profile archive preserves outstanding obligations; suspension cannot be self-restored; buyer backfill conflict quarantined; stale review lease cannot commit. Per-resource action registration/fixtures, legal retention and actual DB grants remain explicit implementation requirements, not claims of completed runtime validation.

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P19

Booking and participant-facing Dispute discussion associated with the same Order reuse that Order's conversation. Context labels/session/case references aid navigation, but do not create duplicate buyer/seller threads. Messaging resolves the canonical Order thread and current membership through its public interface; source owners supply authoritative context and participant facts. Reuse does not automatically enroll a reviewer/support actor or expose unrelated history.

Private adjudication notes, reviewer deliberation, restricted evidence, internal support/moderation material and decision-making records remain separate from the participant conversation under their owning access/audit boundaries. No generic attachment forwarding or notification may leak those records into the thread. Sharing a conversation transfers none of Booking, Dispute, Messaging, Moderation or Order lifecycle ownership.

## WA-R053 — Messaging context identity and durable history

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

SH-113 ensureContextThread accepts typed source owner/type/id, source revision, source-approved participant facts and logical command identity. Messaging validates current source applicability and Role authority, then converges under source-identity uniqueness to one Thread. Order is the participant conversation for its Booking sessions and commercial Dispute under P19/WA-R042; retain session/case navigation references without granting extra membership. Other existing typed Gig, response, assignment, application and interview contexts remain independently keyed to their actual source, not automatically merged by participant overlap. A typed FK is context truth; generic contextId is derived compatibility metadata and must equal that FK. Exactly the matching typed context reference is populated; mismatches block migration/creation, never select whichever field was read first.

Direct two-person identity is the sorted distinct local User pair under a uniqueness lock. Explicit group requests have their own stable Messaging conversation identity and logical create key; do not dedupe a group by mutable membership or silently convert a pair conversation into a group. Support remains a Messaging context with explicit purpose and authorized participant scope; no new support-case lifecycle is created. These identity mechanics do not authorize unsolicited enrollment. Immediate admission requires current source-authorized relationship or explicit authorized conversation request; arbitrary client-supplied recipient arrays fail. Any future invitation product requires its own approved policy. Per-user archive is a viewing preference; no global Thread closed/frozen business lifecycle is added. Restrictions and privacy erasure independently control use.

Persist current ThreadParticipant separately from immutable membership addition/removal history: actor, subject, time, source/policy revision, reason and command identity. Removal invalidates subsequent reads, subscriptions and file authorization; historical presence is not current permission. Concurrent ensure/admission uses current owner version and same-command fingerprint conflict detection. A re-add requires fresh authority and a new membership episode; no inherited access from the old episode.

Persist immutable Message revisions with original sender, revision author, edit time, parent Message identity, content/sensitivity revision and command provenance. Update current revision using expected-version comparison; product deletion hides the Message and cannot be reversed through editing. Do not invent an undelete function. Stable pagination uses (createdAt,id) with a deterministic tie-breaker; no cross-domain sequence service. Historical revisions are subject to approved Privacy disposition, not an exemption from erasure. Where non-null content requires a tombstone, replace authorized erased text with a fixed nonpersonal marker and remove superseded personal revision content through the executor; erasedAt alone is insufficient. Pseudonymization of sender/history follows accepted retention disposition, not ordinary message deletion.

Verification must cover duplicate context creation, conflicting typed/generic IDs, pair/group identity, stale source admission, membership remove/re-add, concurrent edit, deleted/erased edit denial, and cursor ties. Forward schema and applicable retention schedules remain implementation/external prerequisites.

## WA-R054 — Messaging restrictions and authorized realtime

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Messaging owns persistent Thread/Message restrictions and their immutable imposition/restoration evidence. SH-103 execution binds an authorized Moderation decision, exact typed target/action, expected target version and semantic effect key; repeated identical instruction returns its original receipt. Record accepted versus completed execution distinctly. A restoration requires a fresh authorized owner decision and current applicable gates; an edit, new participant episode or generic Hold release cannot clear a restriction. Moderation owns the case/decision and Messaging owns enforcement on its records.

Role checks precede disclosure. Healthcare evaluates applicable ancestry, purpose and each Message/attachment sensitivity under WA-R036; Thread protection enforces the intersection of all applicable category/purpose controls under WA-R065; categories are not ranked, and no item may be downgraded. A new high-sensitivity item strengthens the serving boundary before disclosure. Unknown policy/ancestry fails closed. Source-owned field masks apply before serialization, Media access and notification intent rendering. Protected message/attachment views and exports require durable scoped access evidence under WA-R023; safe inbox metadata follows its separately registered access policy. Sensitive bulk export requires registered authority and fresh action-bound assurance, never a commercial entitlement substitute.

Register messaging.message_created.v1, messaging.message_revised.v1, messaging.message_hidden.v1 and messaging.membership_changed.v1 as minimal owner facts: eventId, Thread ID/revision, affected Message or membership ID/revision, occurredAt, causation/correlation and safe actor reference. Commit history and outbox with owner mutation. Do not include content, attachment URLs or private evidence in the event. Realtime carries only authorized minimal invalidation/delta after commit, never a source of truth. Authenticate subscriptions against current Thread membership/restrictions; revalidate on membership/restriction changes and before protected emission, terminate revoked audiences, and re-query owner truth on reconnect. An event being queued is not proof it was delivered. Provider/channel implementation of SH-071 remains qualified separately; no provider permission is inferred from event names.

Private Message search, Notification attachments and durable unread projections remain deferred optional capabilities. Bounded owner inbox/unread queries are the baseline. Retention/backfill jobs use shared durable execution only after owner policy is approved. Verify removal between subscription and emit, sensitive item in ordinary Thread, masked attachment access, edit-restoration bypass, duplicate enforcement and unavailable audit before interface freeze.

## WA-R055 — Notification intents and credential generations

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Extend WA-R021 without creating another business lifecycle. SH-041 intake binds source owner, source aggregate/revision, immutable semantic intent ID, template/schema version, owner-resolved User recipients, safe context route, sensitivity and channel requirements. Deduplicate on source intent plus resolved User, not display text or provider ID. A changed payload under the same intent fingerprint is a conflict. Recipient resolution comes from the source owner's authorized facts; Notification never scans foreign memberships or application tables. Current access is rechecked for protected context before rendering or route dereference.

Register only concrete source outcomes: Messaging committed new-message fact requests a minimal new-message alert to other currently eligible participants; Order/Booking participant-visible outcome or schedule changes use the source-selected participants; Hiring uses its authorized application/interview recipient facts; Privacy requests verification-needed, terminal-outcome or export-ready intents only after its own corresponding durable transition. Material proposal change visibility is source-owned under P14; private adjudication records never become generic alert variables. Optional viewed/shortlisted, Location notices and unrelated new business triggers remain disabled absent an approved owner trigger. Failed notification delivery cannot roll back source truth. Source legal owners determine legally sufficient notice; transport acceptance, open/click or retry success never proves legal service.

Notification owns append-only interaction evidence (recipient/notification, action, occurrence/received times, command/source evidence) independently of provider attempts. Browser observations are untrusted interaction evidence until validated and do not establish completed domain action. Template versions and channel-safe variable schemas are immutable. Source intent carries safe references rather than raw messages, resumes, exact locations, legal documents or credentials. Consent selects the currently applicable content/version for push acceptance and binds the actual presented version; client-supplied version or browser permission alone is not Consent proof.

Each live push credential is uniquely bound by provider/account/environment and credential fingerprint to one authorized recipient/device generation. Raw endpoint/token stays in protected Notification credential storage; logs/audit contain only safe references. Rotation atomically supersedes the old generation and records actor/provenance; dispatch checks current generation immediately before send. A delayed failure/revocation callback may affect only its matching generation, never disable the replacement. Migration inventories collisions and quarantines ambiguous ownership; no last-write or arbitrary winner. Provider uncertain outcomes reconcile the same attempt before resend under WA-R021.

Notification owns generic email/SMS/Web Push adapter configuration; Identity challenge delivery remains Identity-owned. Selected provider/account/environment, consent/payload permission, capability, callback verification and actual send/recovery evidence are EXTERNAL_REQUIREMENT per enabled channel. No enum activates a vendor. Verify duplicate source intents, revoked recipients, raw-payload rejection, partial channel failure, same token across accounts, late old-generation callback and rotation/send race. These fixtures plus the final source/template matrix gate deployment.

## WA-R057 — Privacy owner inventory and private export handoff

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Each owner implements WA-R020 versioned enumerateSubjectData/evaluateRetentionRequirement/executePrivacyInstruction descriptors. Inventory is explicit, paginated with completion evidence and stable target/version identity; no generic other target or assumed database cascade can count as coverage. Messaging covers Thread, participant current state/history, Message/revisions/restrictions and MessageMedia joins. Notification covers Notification/interaction evidence, NotificationSubscription/credential generations, Delivery attempts and SubscriptionEvent. Location covers FuzzyLocationCache, reveal/revocation evidence and its provider references; exact source facts remain inventoried by their source owner. Restricted proof is accounted even when excluded from requester disclosure. Owner field/action matrices must identify erase, minimize, retain, export or restrict disposition with policy basis and executor receipts before destructive activation.

Privacy owns an immutable export manifest: subject/request/job/generation, owner contribution IDs and versions, authorized field scope, safely stated exclusions with disposition evidence, assembly completion, byte hash/algorithm, creation time and actor/correlation. Exact Location subject data may be included only under approved access policy after removing other parties' data; encryption keys, provider credentials and access tokens are never export content. Record opaque key-version/storage evidence where required, never keys. A complete manifest describes actual serialized bytes, not promised future contributions.

Use Media's WA-R050 createMediaUploadSession→bounded upload→completeMediaUpload→getMediaUploadStatus/getMediaReadiness protocol, with Privacy job/bundle revision as semantic key and purpose-bound private artifact authorization. Same key and bytes replay; changed bytes require a new revision or conflict. Upload acknowledgment never means ready. Require exact immutable ready Media version, matching hash/size and completed manifest before bundle ready. Bind through an explicit Privacy-owned MediaAsset/version reference, not polymorphic ownership. Failed scan/partial assembly keeps download unavailable. Terminal upload retry uses a linked Media attempt per WA-R050 while preserving bundle-generation lineage.

At download, Privacy rechecks requester/action/scope and current generation; Media rechecks asset safety/revocation and issues bounded access through SH-127. Commit required access evidence before protected disclosure. Superseded/expired/revoked generations cannot receive fresh access even if cleanup worker is late. Retain prior manifest/status evidence under approved retention while deleting bytes through Media's executor when authorized. No stored public URL, direct storage SDK or convenience export endpoint may bypass owner gates. Audit exports use the same Media mechanism but an Audit-owned manifest; this ruling does not transfer Audit export ownership.

Legal retention/exemption duration, backup-expiry representation and final retained shell require approved external policy. Location's geocoder/account/region/purpose and key lifecycle qualification remain external activation gates; consumers cannot choose their own geocoder or crypto. Verify omitted child inventory, partial serializer, hash mismatch, scan failure, changed-byte retry, stale generation access, retained shared Media references and provider-deletion uncertainty. Concrete schema, executor field matrices and bilateral fixtures remain implementation qualification, not unresolved architecture permission.


## WA-R066 — Finite Notification source and recipient contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-041 uses the following finite versioned semantic-intent/template registrations. These are architecture contracts, not implemented renderers, selected delivery vendors or proof of delivery. Sources emit an intent only after the corresponding durable owner transition. Every intent binds source owner, typed aggregate ID/revision, immutable semantic intent ID, template key/version, owner-resolved local User recipients, safe authenticated route, sensitivity and event kind. Notification owns channel consent, current endpoint generation, eligible delivery, attempts and receipts. Sources never ask Notification to scan foreign memberships or reconstruct business state.

| Intent/template | Committed source and recipients | Safe additional content |
| --- | --- | --- |
| message.new.v1 | Messaging messaging.message_created.v1; other currently eligible Thread participants selected by Messaging, excluding sender | Thread/Message references only; no message body or attachment URL |
| order.outcome.v1 | Order order.outcome_changed.v1; currently authorized Order participants selected by Order for its source kind | Safe operational outcome code and Order link; no financial consequence implied |
| booking.schedule.v1 | Booking confirmed/rescheduled/cancelled facts; currently authorized affected Booking participants | Safe change kind and authenticated schedule link; no exact address or meeting credential |
| interview.invitation.v1 | Interview invitation/current schedule revision; invited eligible Candidate and authorized Organization participants selected by Interview | Interview reference and safe proposed/scheduled kind |
| interview.schedule.v1 | Interview cancellation/reschedule/replacement; currently authorized affected participants selected by Interview | Safe change kind and authorized predecessor/successor references; no new removed-user notice |
| application.status.v1 | Candidate accepted_offer or withdrawn: current authorized hiring Organization recipients selected by Candidate through Hiring facts; Candidate rejected or hired: the application Candidate User | Application reference and exactly accepted_offer/withdrawn/rejected/hired change code; no view/stage alert or general Candidate exposure |
| privacy.verification_needed.v1 | Privacy durable request transition requiring verification; request subject through Privacy/Identity-authorized route | Request reference and safe action-needed code; no verification secret |
| privacy.outcome.v1 | Privacy accounted terminal outcome; currently authorized request subject/representative | Safe terminal category and link; no restricted exemption evidence or other parties' data |
| privacy.export_ready.v1 | Privacy complete manifest and ready exact Media version/current generation; currently authorized export requester | Request/bundle reference; no signed credential or stored public URL |
| security.notice.v1 | Identity committed security intent; affected local User only | Generic change and authenticated-context link; no OTP, recovery token, precise IP or factor details |
| supply.status.v1 | Professional/Marketplace committed status/remediation intent under R035; owner-resolved Professional User | Generic status/remediation code; no Healthcare/provider/Hold detail |

Candidate registers `candidate.application_status_changed.v1` with eventId, application ID/revision, committed time, semantic command identity, old/new status, authorized actor reference and safe typed Candidate/Organization subject references. This event contains no resume, message, employer notes or protected evidence. The source owner derives notification recipients from current Hiring authority. Only the four listed successful status transitions may create application.status.v1 at launch; application views, recruiter stages and retry transport do not. Candidate acceptance must already satisfy R045 current-offer proof, and withdrawal does not restore quota. Sending a notification never makes an application or Candidate publicly discoverable.

Deduplicate one semantic intent × resolved User; channel attempts are children of that intent. Changed payload under the same fingerprint conflicts. Retries preserve identity. Current protected-context access is rechecked before rendering/dereference; loss of membership suppresses the protected notice. Do not create a removed-user notice without its own approved source policy. Delayed invitation links must recheck P18/current schedule. Notification failure never rolls back source truth. No message bodies, resumes, exact locations, raw provider failures, adjudication evidence or credentials may enter generic variables.

Material proposal changes remain visibly surfaced by Gig's current-revision presentation under P14; a delivered notice is not evidence the latest terms were presented for acceptance. Participant-facing Dispute updates reuse Order conversation under P19, but a Review fact cannot be relabeled as an Order event; any separate Review alert remains disabled until registered. Optional viewed/shortlisted, Location, Interview completion/no-show and other undeclared alerts remain disabled. This finite registration does not provide legally sufficient notice policy. Exact copy, renderer/schema fixtures, provider/account/channel qualification and delivery recovery proof remain activation prerequisites. Existing broad notification suggestions are narrowed by this explicit source/recipient matrix for these intents.

## WA-R081–083 — Gate 4 bridge obligations

Coordinate the Module-owned contracts in `context/reconciliation/bridge-contract-bindings.md` and the complete inventory. Source facts, semantic commands and completion receipts are separate. Optional disabled paths do not become Cluster prerequisites. Retain all existing P01–P19, permanent SH identities, source lifecycles and external gates. No contract is frozen.

Reviewed directional families touching this Cluster: BF-007, BF-017, BF-020, BF-026, BF-027, BF-033, BF-034, BF-048, BF-063, BF-065, BF-066, BF-082, BF-083, BF-084, BF-099, BF-102, BF-115, BF-116, BF-117, BF-123, BF-131, BF-152, BF-153, BF-154, BF-155, BF-156, BF-157, BF-158, BF-159, BF-160, BF-162, BF-163, BF-164, BF-175, BF-176, BF-177, BF-183, BF-192, BF-196, BF-198, BF-203, BF-204, BF-205, BF-206, BF-207, BF-208, BF-209, BF-210, BF-211, BF-212, BF-224, BF-230, BF-231, BF-232, BF-234, BF-240, BF-242, BF-249, BF-256, BF-257, BF-266, BF-268.

Integrate current R068/069/075; Media invalidation uses R082 only for registered Customer/Candidate subscribers. Privacy field/action fixtures remain required despite source enumeration reconciliation. Cluster sequencing must use contract/foundation dependencies, not whole neighboring-Cluster completion.


## WA-R085–087 — Platform convergence

Current platform reconciliation covers `messaging`, `notification`. Module owners retain all lifecycles and source facts. R085 separates terminating fact inputs from composed permissions, readiness, credential issuance and Hold release; R086 locates one shared execution capability and bootstrap dependencies; R087 routes Organization commercial schema responsibility to Track without enabling monetized ATS.

Coordinate required ports and semantic fixtures before actual adapters; do not require complete upstream Clusters from a contract edge. Source commits precede outbox delivery and downstream projection/Notification/provider setup. Recovery reuses stable effect identity and cannot infer completion from acknowledgment, telemetry or a read model. The platform dependency graph records typed edges and critical cycle dispositions; action-specific external gates remain scoped.

Root architecture synthesis is conditional on the recorded Gate 5 exit and Gate 6 posture confirmation. A root build plan, runtime choice, database migration, interface freeze and parallel implementation lanes remain later prerequisites. No such implementation approval is made by this coordination appendix.
