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
  → source-context validation through owner API    [Order/Gig/Hiring/etc.]
  → Messaging application service
       → transaction: Thread / Participant / Message / MessageMedia
       → appendAuditEvent or recordSensitiveAccess when policy requires
       → publishRealtimeChange after commit
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
- Provider SDKs exist only under Notification provider adapters or approved platform integration shells.
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
| Media / File Access | MediaAsset/file safety/storage/grants/signed URLs | Messaging contextual attachment facts | MessageMedia contextual meaning; Message content |
| Healthcare / Regulated Services | sensitivity/redaction/block policy | Messaging targets/sensitivity facts | Message or Thread lifecycle |
| Privacy / Data Erasure | PrivacyRequest/DataErasureJob/Target/RetentionExemption orchestration | CL-07 enumerate/execute handlers | direct CL-07 table mutation |
| Content Moderation & Legal Notice | Report, case, legal notice, moderation decision/action | Messaging target resolver/executor; Notification delivery | Message lifecycle as case truth; notification delivery as legal decision |
| Audit / Event Ledger | AuditEvent and AccessAuditLog | safe CL-07 action context | Thread/Message/Notification/Delivery lifecycle |
| Observability / Ops | logs, metrics, IntegrationFailure, QueueJob/incident visibility | CL-07 technical events | business or delivery lifecycle truth |
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
| `IntegrationFailure`, `QueueJob`, `OpsIncident` | Observability / Ops | operational evidence only |
| `TrackSubscriptionEvent`, `TrackEntitlementGrant` | Track Subscription & Entitlement | may trigger notification; never CL-07 policy truth |

### Ownership conflicts resolved by this architecture

**ThreadParticipant conflict.** One Deep Module Registry entry lists `ThreadParticipant` under Role / Authority's owned schemas, while the Messaging registry, Ubiquitous Language, Module extract, and Canonical Shared Operations explicitly define Messaging as the row/lifecycle owner and Role / Authority as permission interpreter. **Architecture Ruling:** Messaging owns `ThreadParticipant`; Role / Authority consumes participant facts and never mutates the row as its own truth.

**MessageMedia conflict.** Some source material can be read as Media owning message attachment records. Ubiquitous Language and canonical `attachValidatedMedia` separation establish that the contextual join belongs to the contextual Module while Media owns `MediaAsset`. **Architecture Ruling:** Messaging owns `MessageMedia`; Media owns file truth and access mechanics.

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
| `ensureContextThread` | Order, Gig, Candidate Application, Job Interview and other approved context owners | Return/create the one currently schema-permitted Thread for a typed business context | actor/system context; `ThreadContextType`; owner-issued context ID; initial participant IDs; sensitivity | Thread ID; context binding; current participants | source truth | source business status; permission policy |
| `getThreadParticipantFacts` | Role / Authority, Media, Healthcare, Admin Review | Expose current participant/context facts | Thread ID; actor User ID | participant exists; joinedAt; lastReadAt; context type/id; safe sensitivity metadata | truth | authorization decision |
| `listThreadsForUser` | UI/client | Authorized inbox/thread list | actor; pagination; optional allowed context filter | safe thread summaries | truth/derived summary | business object lifecycle |
| `getThread` | UI/consumers | Authorized thread metadata | actor; Thread ID; view purpose | full/redacted/metadata-only result | truth + external decision effect | healthcare policy |
| `listThreadMessages` | UI/consumers | Authorized paginated message retrieval | actor; Thread ID; cursor/page size | messages after deletion/erasure/redaction policy | truth | sensitive access policy |
| `sendMessage` | authorized participants | Persist a new Message | actor; Thread ID; content; optional MediaAsset IDs; idempotency key | Message ID, timestamp, safe realtime/notification metadata | truth | Notification delivery |
| `editMessage` | sender/admin per Role policy | Edit current message content | actor; Message ID; replacement content | updated message + `editedAt` | truth | edit-history proof that does not exist |
| `deleteMessage` | authorized actor | Product-delete/hide message | actor; Message ID; reason | updated deletion marker | truth | privacy erasure or moderation decision |
| `markThreadRead` | participant | Advance read cursor | actor; Thread ID; bounded read cursor/timestamp | new `lastReadAt` | truth | Notification read state |
| `attachValidatedMedia` (shared contract, contextual execution) | Messaging UI/services | Attach ready file context | actor; Message ID; MediaAsset ID | MessageMedia join | truth | MediaAsset readiness or signed URL entitlement |
| `enumerateSubjectData` handler | Privacy | Enumerate Messaging-held subject records | subject; cursor | target descriptors/dispositions | evidence/facts | PrivacyRequest orchestration |
| `executePrivacyInstruction` handler | Privacy | Execute owner-approved disposition | target/action/idempotency/retention instruction | completed/retained/skipped/failed result | execution evidence | privacy-request completion |
| moderation target resolver/executor | Moderation | Resolve Message/Thread safely and apply approved enforcement action | case/action envelope; target | minimized snapshot / execution acknowledgement | evidence/execution result | ModerationCase lifecycle |

### Notification public interfaces

| Interface | Consumers | Purpose | Minimum input | Minimum output | Returns | Consumers must not infer/recreate |
| --- | --- | --- | --- | --- | --- | --- |
| `requestNotification` | all workflow Modules, Messaging, Audit/Ops | Submit one authorized alert intent through canonical delivery | source Module/type/id; recipient target/group contract; template key+version; priority; sensitivity; safe variables; action route; idempotency key | accepted/rejected result; notification request reference | decision + Notification truth reference | provider dispatch or source business state |
| `renderNotificationTemplate` | Notification internally | Render channel-safe versioned content | template key/version; locale; channel; validated safe variables | title/body/provider payload | derived artifact | business/legal decision |
| `resolveNotificationRecipients` | Notification + source owner | Resolve group/relationship to User IDs without moving owner policy | typed recipient request | concrete User IDs + routing metadata | owner facts / routing result | membership/participant lifecycle |
| `listNotifications` | authenticated User/UI | In-app notification list | actor; pagination/status filter | safe notification summaries | truth | source workflow status |
| `getUnreadNotificationCount` | authenticated User/UI | Count unread in-app alerts | actor | count | projection/derived query | Message unread state |
| `markNotificationRead` | targeted User | Mark in-app alert read | actor; Notification ID | updated status/readAt | truth | workflow completion |
| `dismissNotification` | targeted User | Dismiss an in-app alert | actor; Notification ID | updated status | truth | source action completion |
| `recordNotificationInteraction` | authenticated/client/provider callback | Record click/open/close evidence | notification/delivery; interaction; safe URL; actor/device context | interaction evidence | evidence | user understanding/completion |
| `recordNotificationPermissionState` | client | Persist observed browser permission | actor; platform/device context; permission status | updated reachability state/event | truth/evidence | ConsentLog acceptance |
| `upsertPushSubscription` / `refreshPushSubscription` / `revokePushSubscription` | authenticated client/account settings | Manage device/browser reachability | actor; provider/platform; encrypted/hashed endpoint/token material; service-worker metadata | subscription state | truth | identity/authentication |
| `listNotificationSubscriptions` | account settings | List connected devices without secrets | actor | device/reachability summaries | truth | OS notification settings |
| `enumerateSubjectData` handler | Privacy | Enumerate notification-owned personal data | subject/cursor | notification/subscription/delivery targets | evidence/facts | PrivacyRequest orchestration |
| `executePrivacyInstruction` handler | Privacy | Execute approved local data disposition | target/action/idempotency | result | execution evidence | retention decision |

---

## 11. Canonical Shared Operations Used by This Cluster

The current Canonical Shared Operations document supplies canonical **names**, but no numeric SH IDs in the registry table. CL-07 references the canonical names rather than inventing IDs.

| Canonical operation | Plain-English meaning | Canonical owner | CL-07 consumers | Reusable mechanism | CL-07 policy that stays local | Invocation point | Must not duplicate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Resolve provider session/system credential to trusted actor context | Identity & Access | Messaging, Notification | typed authenticated actor middleware | what messaging/notification action is requested | every protected command/query | `chatAuth`, `notificationCurrentUser`, feature-local session helpers |
| `authorizeResourceAction` | Decide permission for named action using owner-supplied relationship facts | Role / Authority | Messaging, Notification | decision API + aligned RLS/route enforcement | Thread/Notification-specific relationship facts/action vocabulary | before protected read/mutation | local permission engines |
| `queryOwnerFacts` | Read minimum owner relationship facts without source-truth transfer | each source Module | Messaging, Notification | owner-specific DTO pattern | context/participant/recipient facts | context validation and recipient resolution | cross-domain Prisma repositories |
| `queryConsentProof` | Return proof of required accepted version | Consent & Disclosure | Notification | versioned consent query | whether web-push disclosure is required for this channel/action | before establishing/using consent-dependent push capability | `pushConsent` tables/services |
| `appendAuditEvent` | Append generic important-action proof | Audit / Event Ledger | Messaging, Notification | insert-only AuditEvent command | which CL-07 actions merit generic audit | after or transactionally adjacent to important actions | local generic audit logs |
| `recordSensitiveAccess` | Append protected-data access proof | Audit / Event Ledger | Messaging primarily; Notification for sensitive admin/device actions if policy says | AccessAuditLog command | sensitivity, target, decision, purpose | sensitive Message/Thread access and protected delivery/access events | `MessageAccessLog`, mutable admin view log |
| `createRequestContext` | Propagate correlation/request/actor IDs | platform/Observability | both | async request context | none beyond safe CL-07 labels | entrypoint and async dispatch | local correlation systems |
| `sanitizeTelemetryMetadata` | Strip secrets and sensitive data from telemetry/audit metadata | Observability/Ops + Audit policy | both | allowlisted serializer/redactor | CL-07 sensitivity labels and safe fields | before logs, metrics, failures, audit metadata | local ad hoc redactors |
| `recordIntegrationFailure` | Persist normalized provider/worker failure evidence | Observability / Ops | Notification; Messaging realtime integration if degraded | IntegrationFailure interface | business state remains in CL-07 owner | provider/worker failure | treating IntegrationFailure as Delivery status |
| `recordQueueTelemetry` | Record queue attempts/retries/dead-letter execution | shared queue/Ops | Notification workers | worker instrumentation | delivery job payload and business completion remain Notification-owned | all async delivery jobs | per-Module queue ledgers |
| `requestNotification` | Submit alert through canonical interface | Notification | Messaging and every source Module | canonical command | Notification routing/payload policy; source meaning stays upstream | after source event commit | direct provider calls in sources |
| `renderNotificationTemplate` | Render validated localized channel content | Notification | Notification | central template registry | safe variables/channel limits | delivery planning/worker | per-Module email/SMS/push renderers |
| `resolveNotificationRecipients` | Resolve owner groups to concrete Users | source owner + Notification | Notification | shared request/result contract | owner controls membership/recipient facts; Notification fan-out/dedupe | intake/routing | universal recipient repository |
| `executeIdempotentCommand` | Make retried command yield one effect | platform app infrastructure | `sendMessage`, `ensureContextThread`, `requestNotification`, subscription mutation | atomic idempotency claim/result | semantic key/conflict behavior belongs to owner | mutation boundaries | local idempotency tables/helpers unless canonical storage requires owner key |
| `deduplicateDomainEvent` | Prevent duplicate consumer side effects | platform event infrastructure | Notification consumers; any future Messaging event consumers | inbox claim | handler identity and side effect are consumer-specific | event-triggered requests | custom event dedupe frameworks |
| `publishDomainEvent` | Reliably publish versioned event after source transaction | platform outbox | future Messaging lifecycle events if approved; source business Modules | transactional outbox | event semantics/privacy fields owned by publisher | post-commit integration | ad hoc fire-and-forget event buses |
| `enqueueReliableJob` | Persist durable async work with retries/leases/DLQ | shared queue | Notification | common queue client/worker shell | Delivery job semantics/status remain Notification-owned | after authoritative enqueueable write | local worker framework |
| `executeRetryWithBackoff` | Bounded retry transient technical failures | shared queue | Notification delivery/provider callbacks | retry strategy primitive | Notification adapter classifies retryability | delivery and callback handling | provider-specific retry loops scattered across adapters |
| `verifyProviderWebhookSignature` | Verify raw callback authenticity before parsing/side effects | shared integration-security shell | Notification provider callbacks | common verifier interface | provider algorithm/secret/tolerance local to adapter | webhook edge | bespoke route verification patterns |
| `deduplicateProviderEvent` | Claim callback once | provider owner using shared primitive | Notification when callbacks exist | atomic provider-event claim | Notification keeps its own processed-event truth | after signature verification | reusing Stripe/Calendar/Video processed-event tables |
| `translateProviderStatus` | Map provider status/error to owner vocabulary | Notification adapter | Notification | provider-adapter contract | mapping to NotificationDelivery/Subscription statuses | provider response/callback | global cross-provider status mapper |
| `reconcileProviderState` | Compare Workin Ants truth to provider and repair safely | Notification | Notification | shared reconciliation worker pattern | repairability and authoritative mapping remain Notification-owned | scheduled/admin repair | generic global provider reconciler with domain policy |
| `publishRealtimeChange` | Publish committed safe changes to authorized clients | platform realtime adapter; Messaging primary consumer | Messaging | authorized realtime transport | audience/payload based on Thread/participant facts | after commit | treating Realtime as message storage |
| `encryptSensitiveValue` | Encrypt recoverable secret with managed/versioned keys | platform crypto | NotificationSubscription | envelope encryption | which endpoint/token fields require recovery and rotation | subscription create/refresh | notification-local crypto |
| `normalizeAndHashIdentifier` | Create non-plaintext stable comparison identifier | platform crypto | NotificationSubscription | keyed HMAC/normalization | endpoint/token normalization purpose | subscription dedupe/lookup | plaintext endpoint matching as sole identity |
| `attachValidatedMedia` | Attach ready MediaAsset through context-owned join | contextual owner; Media owns asset | Messaging | shared contract | message attachment authorization/role remains Messaging | message attachment | custom upload/storage pipeline |
| `executePrivacyInstruction` | Execute approved privacy disposition in owner records | Privacy orchestrates; owner executes | both | cross-cutting protocol | exact CL-07 field mutations and invariants | Privacy target execution | local PrivacyRequest workflow |
| `enumerateSubjectData` | List owner-held subject data and supported dispositions | each data owner | both | privacy handler protocol | Messaging/Notification know their records | Privacy inventory | global Privacy direct DB crawler |
| `evaluateRetentionRequirement` | Supply owner facts for retention decision; Privacy records exemption | data owner + Privacy | both | retention protocol | source facts only; legal decision is not invented locally | privacy planning | local exemption tables |
| `submitModerationReport` | Submit typed abuse/legal allegation | Content Moderation & Legal Notice | Messaging | moderation intake interface | Messaging supplies target/evidence only | user report action | local message report/case table |
| `executeModerationDecision` | Apply authoritative moderation action in target owner | Moderation decides; Messaging executes | Messaging | enforcement protocol | Messaging maps approved action to conversation behavior | after ModerationAction | Moderation directly mutating messaging DB |

### Classification reminders

- `requestNotification` is a canonical cross-cutting capability owned by Notification.
- `publishRealtimeChange`, idempotency, queueing, crypto, and webhook verification are platform/infrastructure primitives.
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
→ operational telemetry / IntegrationFailure if needed
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
   Messaging supplies context facts
   → Media issues short-lived signed URL after its own gates
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
→ each CL-07 Module returns retention candidates and supported actions
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
| CL-01 Identity | CL-07 | actor/session context | Identity | `resolveAuthenticatedActor` | CL-07 user/session helpers |
| CL-01 Role / Authority | CL-07 | access decision | Role / Authority | `authorizeResourceAction` using CL-07 owner facts | Role mutating ThreadParticipant or Notification target |
| CL-01 Consent | Notification | push disclosure proof | Consent | `queryConsentProof` | Notification creating ConsentLog |
| CL-01 Track Entitlement | Notification | subscription/plan/entitlement lifecycle alert intent | Track | `requestNotification` / domain event | CL-07 interpreting entitlement grants |
| CL-03/04 Marketplace and Order | Messaging | context/participant facts; thread creation request | source Module + Messaging | owner facts + `ensureContextThread` | source Module inserting Thread rows |
| CL-04 Order/Dispute | Notification | order/dispute alert intent | source Module | `requestNotification` | Notification inferring refund/dispute state |
| CL-05 Booking/Video/Media | Messaging | Media readiness/access; booking-associated conversation request if approved | Media/Booking | public interfaces | Messaging storage provider access; inventing Booking context type |
| CL-05 Booking/Video | Notification | schedule/session alerts | source Module | `requestNotification` | Notification changing Booking/Video state |
| CL-06 Hiring | Messaging | JobApplication/JobInterview context and participants | Candidate Application / Job Interview | owner facts + `ensureContextThread` | Messaging reading resume or hiring status directly |
| CL-06 Organization Hiring | Notification | org membership and OrganizationNotificationSetting routing facts | Organization Hiring | owner recipient query | Notification owning membership/settings |
| CL-08 Privacy | both | privacy target execution | Privacy orchestrates, CL-07 executes | `enumerateSubjectData`, `executePrivacyInstruction` | Privacy direct CL-07 repository mutations |
| CL-09 Moderation | Messaging | report/decision/enforcement envelope | Moderation | `submitModerationReport`, `executeModerationDecision` | local MessageReport/ModerationCase |
| CL-09 Holds | Notification | hold-created/released alert intent | Hold Module | `requestNotification` | Notification interpreting/clearing hold |
| CL-09 Audit | both | generic/sensitive proof | Audit | `appendAuditEvent`, `recordSensitiveAccess` | CL-07 generic audit tables |
| CL-09 Observability | both | technical failures/queue telemetry | Observability | canonical ops | using IntegrationFailure as delivery/message status |
| CL-10 Rewards/Prize | Notification | reward/prize alert intent | source Module | `requestNotification` | Notification eligibility/tax decisions |

### Review/Dispute and Booking thread bridge warning

The current `ThreadContextType` contains no `review`, `dispute`, or `booking`. Do not silently add them. Until an architecture ruling is approved, consumers must not assume a separate context thread exists. The likely options are reuse of an existing Order thread or schema expansion, but this file does not choose between them.

---

## 14. Authentication and Authorization

### Authentication dependency

Every user-facing CL-07 command/query begins with `resolveAuthenticatedActor`. Client-provided `userId`, `senderId`, organization membership, or subscription ownership is never trusted as authority.

### Role / Authority dependency

`authorizeResourceAction` interprets permission. CL-07 supplies contextual facts:

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

Step-up requirements are not established for ordinary messaging/notification actions. If root architecture or owner Module declares an action sensitive enough for step-up, CL-07 consumes `requireStepUpForSensitiveAction`; it must not invent local MFA.

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

Identity owns OTP/challenge/recovery token issuance, expiry, attempt limits, validation, and security events. Notification may transport owner-generated safe delivery content and record delivery proof. The exact SMS MFA provider boundary remains unresolved; duplicate Identity and Notification OTP delivery implementations are prohibited.

---

## 16. Events, Queues, Jobs, and Workflow Orchestration

### Messaging events

No Messaging integration event catalog or outbox is confirmed in the current schema. Likely candidates such as `MessageSent` are useful, especially for Notification, but they are not binding until approved.

**Current safe default:** core Messaging writes are synchronous and may call `requestNotification` after commit. If event-driven decoupling is introduced, use `publishDomainEvent` and `deduplicateDomainEvent`; do not create a Messaging-specific event bus.

### Notification jobs

External delivery is asynchronous. A Notification worker must reuse:

- `enqueueReliableJob`;
- `executeRetryWithBackoff`;
- `recordQueueTelemetry`;
- `createRequestContext`;
- `recordIntegrationFailure`.

### Idempotency

The following operations require semantic idempotency:

- `ensureContextThread` for typed contexts;
- `sendMessage` when clients may retry;
- `requestNotification`;
- push subscription create/refresh/revoke;
- provider callback application;
- privacy execution;
- moderation enforcement execution.

Canonical idempotency mechanics are reused; each owner defines the semantic key and conflict behavior.

### Concurrency

- Typed Thread foreign keys are currently unique, so concurrent `ensureContextThread` calls must converge on one row.
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

Source Modules never import email, SMS, Web Push, FCM, OneSignal, WonderPush, SES, or similar provider SDKs directly.

### Email

The current Project Overview names AWS SES for email. The Notification registry also contains generic “Email provider” / “Transactional email provider” evidence and flags AWS SES as an inconsistent compliance item. **Architecture Ruling:** treat SES as the current Workin Ants email transport choice where root provider configuration confirms it, but keep a Notification-owned provider-neutral email port. The provider is a rail, not Notification truth.

### SMS

The current evidence is inconsistent: the Project Overview phrase “AWS SES for Email and SMS” is technically not a coherent SMS provider assignment, while Identity/Notification evidence references an SMS provider and Twilio Verify or equivalent for OTP. **Unresolved Decision:** general notification SMS provider and the Identity MFA transport boundary must be approved before production SMS delivery.

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

Providers with query APIs should support scheduled/admin reconciliation using `reconcileProviderState`. Automatic repair must be limited to discrepancies Notification can safely resolve without changing source business truth.

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

CL-07 may supply facts to `evaluateRetentionRequirement`, but Privacy records `DataRetentionExemption`. Audit proof necessary to prove privacy execution may remain according to Audit/Privacy policy; CL-07 must not delete the proof ledger directly.

### Product deletion vs erasure

- `Message.deletedAt` = normal product deletion/hiding.
- `Message.erasedAt` = owner execution marker within a Privacy-controlled workflow.
- `Thread.erasedAt` = local erasure marker, not PrivacyRequest completion.
- Notification deletion/erasure semantics are not currently modeled by dedicated fields; privacy handler behavior must be explicit and idempotent.

---

## 21. Audit and Observability

### Audit

Use `appendAuditEvent` for important actions where generic action proof is required, such as subscription revocation, administrative delivery intervention, or moderation/privacy execution acknowledgement.

Use `recordSensitiveAccess` for protected data access, such as approved healthcare/private message reads/download gates when policy requires it.

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
- structured safe logs;
- metrics for queue depth, latency, attempts, delivery outcomes, subscription failures;
- exceptions through the single monitoring adapter;
- `IntegrationFailure` for meaningful provider/worker degradation;
- dead-letter visibility.

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
5. **Plaintext conflict:** current `NotificationSubscription` contains plaintext endpoint/token/`p256dh`/`auth` alongside encrypted/hash fields. Production implementation must not treat both as authoritative. See Proposed Ruling PR-N04.
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

- `ensureContextThread` owner-facts contracts for each supported context;
- `getThreadParticipantFacts` with Role / Authority;
- Media attachment facts/access bridge;
- `requestNotification` typed contract used by representative source Modules;
- organization recipient-facts query;
- Privacy enumerate/execute protocols;
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
6. No business Module may call email/SMS/push providers directly; it must use `requestNotification`.
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
- source-Module SES/Twilio/FCM/OneSignal calls;
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
| U-CL07-16 | Which initial SMS provider is used, and who transports MFA OTPs? | overview/registry/provider notes conflict | Identity + Notification provider boundary | production SMS/MFA transport |
| U-CL07-17 | Which initial Web Push adapter is selected? | multiple optional providers are listed | provider selection | production web-push adapter |
| U-CL07-18 | Are plaintext push credential fields removed, ignored, or retained temporarily during migration? | plaintext and encrypted/hash copies coexist | security migration ruling | production subscription credential storage |
| U-CL07-19 | What is the canonical Notification interaction record? | click/open/close overlap across parent, Delivery, SubscriptionEvent | interaction ownership ruling | analytics/evidence normalization; basic interaction can be recorded conservatively without claiming canonicality |
| U-CL07-20 | What are the controlled Notification template-name catalog and versioning governance rules? | canonical op exists; `name` is free string; no persisted template schema | template registry approval process | production source-template integrations |
| U-CL07-21 | What exact safe payload schema applies per sensitivity × channel? | labels exist but JSON is unrestricted | payload allowlist catalog | all external production delivery |

### Proposed Rulings

These are strong architectural recommendations derived from current evidence. They become binding only when approved.

**PR-N01 — Notification request fan-out is explicit.** `requestNotification` accepts semantic intent plus recipients/channel requirements; Notification performs fan-out. Source Modules never create Delivery rows.

**PR-N02 — Prefer channel-specific Notification records.** Because `Notification.channel` exists and read/dismiss semantics are naturally in-app-specific, treat each Notification row as one resolved target/channel semantic alert, with `NotificationDelivery` rows representing attempts for that same channel. A single request may create multiple Notification rows. Approval should be accompanied by target/cardinality constraints.

**PR-N03 — One Delivery row per attempt.** Preserve attempt history by creating a new `NotificationDelivery` per provider attempt rather than overwriting repeated failures. Add correlation/attempt/idempotency fields if required by migration. Aggregate Notification status is derived by channel-specific policy rather than queue state.

**PR-N04 — Encrypted/hash credential fields replace plaintext authority.** Use `endpointHash`/`tokenHash` for matching and encrypted endpoint/token/key material only where recovery is required. Remove or stop writing plaintext `endpoint`, `token`, `p256dh`, `auth` after migration. Do not maintain two active truths.

**PR-N05 — Controlled code-based notification template registry for MVP.** Use typed keys, explicit versions, per-channel variable schemas, sensitivity classification, and safe action-route builders. Do not create a mutable database template lifecycle until product requirements justify it.

**PR-M01 — Current typed-context uniqueness is binding until changed.** `ensureContextThread` must converge on the single row allowed by current `@unique` constraints. This does not decide whether future architecture should support multiple threads.

**PR-M02 — Realtime event emission is post-commit only.** Realtime payloads derive from committed Messaging truth and may be safely dropped/recovered by refetch; they must not participate in the database transaction as source truth.

---

## 27. Architecture Decision Summary

1. CL-07 is a communication rail, not a lifecycle-owning super-domain.
2. Messaging owns conversation records; Notification owns alert/delivery/reachability records.
3. `ThreadParticipant` is Messaging truth; Role / Authority owns permission interpretation.
4. `MessageMedia` is Messaging contextual truth; Media / File Access owns MediaAsset/file mechanics.
5. Source Modules use `requestNotification`; they never call providers directly.
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

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry;
5. this CL-07 `architecture.md`;
6. this CL-07 `build-plan.md`;
7. the target Module's `module-architecture.md`;
8. the target Module's `implementation-plan.md`;
9. relevant dependency Module public-interface sections, especially Identity, Role / Authority, Consent, Media, Healthcare, Privacy, Moderation, Audit, Organization Hiring, and the business context owner;
10. `progress-tracker.md`.

Before implementation, the agent must also check the Unresolved Decisions table. If the requested feature depends on an unresolved decision, stop and obtain the architecture ruling rather than encoding an assumption in code. If implementation discovers a binding conflict with this file, update architecture first, then adjust the build plan; never let build progress silently become architecture.
