# Messaging & Notification Rail Build Plan

> **Cluster ID:** CL-07  
> **Cluster:** Messaging & Notification Rail  
> **Companion architecture:** `messaging-notification-rail/architecture.md`  
> **Purpose:** ordered implementation sequence for the `messaging` and `notification` Deep Modules and their approved bridges  
> **Rule:** this plan implements the architecture. It does not redefine ownership, lifecycle, provider, privacy, or policy decisions.

---

## Core Principle

Build CL-07 as two cooperating vertical capabilities:

```text
Conversation intent
→ authenticated/authorized Messaging service
→ durable Thread/Message truth
→ safe realtime update
→ optional Notification request

Business alert intent
→ canonical Notification request
→ durable Notification truth
→ privacy-safe rendering/routing
→ durable delivery work
→ provider-normalized delivery evidence
```

Use vertical, testable slices wherever practical:

```text
usable/observable behavior
→ owning domain/application service
→ authoritative database state
→ public contracts
→ permissions/compliance
→ events/jobs/integrations
→ tests
→ exit gate
```

Do not front-load a generic “communications platform.” Build the smallest Messaging truth that can support a real context-bound conversation, then the smallest Notification truth that can support a real in-app alert, then add external transport, governance, privacy, and cross-Cluster bridges.

A capability does not need artificial UI to qualify as a vertical slice. Provider callback handling, privacy executors, and cross-Module contracts may be proven through an administrative surface, contract harness, worker result, or other observable result.

---

## Build Rules

- Follow root `project-overview.md`, root `architecture.md`, root `code-standards.md`, Canonical Shared Operations, and CL-07 `architecture.md`.
- Do not expand CL-07 into CRM, marketing campaigns, support-case management, public search, or a generic omnichannel platform.
- Do not redesign Deep Module ownership for implementation convenience.
- Messaging and Notification remain separate persisted truths.
- Canonical Shared Operations must be reused rather than reimplemented.
- Every mutation validates runtime input and authorizes server-side.
- RLS is defense in depth and must agree with Role / Authority decisions.
- No source Module calls email, SMS, Web Push, FCM, OneSignal, WonderPush, SES, or other notification providers directly.
- Every external provider is isolated behind Notification-owned provider-neutral ports and adapters.
- Every asynchronous operation is idempotent, correlated, retry-bounded, and observable.
- Every provider callback is authenticated before parsing/state mutation and deduplicated before side effects.
- Message attachments use Media / File Access; Messaging never owns file bytes or signed URL mechanics.
- Privacy / Data Erasure owns request orchestration. CL-07 only enumerates and executes against its own records.
- Content Moderation owns case/decision truth. Messaging only resolves targets and executes approved actions.
- Audit and Observability remain separate from business lifecycle truth.
- Track Subscription & Entitlement remains commercial policy truth. CL-07 does not create local premium flags.
- No private Message/Thread/Notification data enters public Search.
- Every numbered feature ends with tests and a concrete exit gate. Do not begin the next feature until the current exit gate passes.
- If a feature depends on an Unresolved Decision, stop at the decision boundary. Do not encode an assumption merely to keep the sequence moving.
- If a binding decision legitimately changes, update CL-07 `architecture.md` first, then this plan and the target Module context.

---

## Dependencies and Preconditions

### Root/platform prerequisites

CL-07 assumes the repository already provides or will provide the canonical platform mechanisms defined outside this Cluster:

- Supabase Auth-backed authenticated actor resolution;
- Prisma/PostgreSQL and migration workflow;
- Role / Authority decision API plus aligned RLS conventions;
- Zod or root-approved runtime validation;
- canonical idempotency infrastructure;
- transactional outbox/event infrastructure if event contracts are used;
- one reliable queue/worker framework;
- retry/backoff and dead-letter behavior;
- request/correlation context;
- structured logging, metrics, exception capture, IntegrationFailure, and queue telemetry;
- centralized cryptography for encryption/HMAC;
- generic AuditEvent and AccessAuditLog interfaces.

If one of these platform primitives is not yet implemented, build the minimum canonical prerequisite in its owning platform/shared scope. Do not build a CL-07-local substitute.

### Upstream Module prerequisites

- Identity & Access: `resolveAuthenticatedActor`.
- Role / Authority: `authorizeResourceAction` and ability to consume owner facts.
- Media / File Access: ready-asset validation and contextual signed-access interface before MessageMedia delivery is enabled.
- Consent & Disclosure: `queryConsentProof` before production consent-dependent Web Push setup.
- Privacy / Data Erasure: handler protocol before production erasure fulfillment is enabled.
- Audit / Event Ledger: `appendAuditEvent`; `recordSensitiveAccess` before sensitive-production access.

### Source-workflow dependencies that can be stubbed initially

Context/recipient contracts may use fixtures or owner-interface fakes until their source Modules are implemented:

- Order / Gig / GigResponse / GigAssignment;
- JobApplication / JobInterview;
- Organization member/settings recipient facts;
- Booking / Video events;
- Track subscription/entitlement lifecycle events;
- Moderation and Healthcare decisions.

Stubs must mimic public contracts only; they must not be promoted into CL-07 copies of source truth.

### Decisions that must be closed before particular features

- Production push credential storage: U-CL07-18 / PR-N04 before Feature 07 exits.
- Production multi-channel aggregate/retry model: U-CL07-10 through U-CL07-15 before Features 09 and 15 exit.
- Organization-target routing: U-CL07-09 before Feature 10 exits.
- Production external payload catalog: U-CL07-20 and U-CL07-21 before Feature 08 exits to production-enabled channels.
- SMS/MFA provider boundary: U-CL07-16 before production SMS is enabled.
- Push provider selection: U-CL07-17 before production Web Push is enabled.
- Healthcare/audit policy: U-CL07-06 and U-CL07-07 before Feature 12 enables healthcare-sensitive production reads.
- Destructive retention/erasure rules: U-CL07-08 before Feature 13 enables destructive production erasure for affected categories.

---

## Phase 1 — Conversation Rail Core

### 01 Context-Bound Thread Foundation

Create the first real Messaging vertical slice: an approved business Module can ensure one context-bound Thread and retrieve it through Messaging without inserting Messaging rows directly.

#### Objective

Make `Thread` and context binding usable as a single Messaging-owned source of truth for the currently modeled typed contexts.

#### User-visible / Observable Result

A developer or authorized workflow can request a Thread for an Order, Gig, GigResponse, GigAssignment, JobApplication, or JobInterview fixture/context and receive the same Thread on safe retries. An internal proof page or contract test harness can display the Thread ID, context type, context reference, sensitivity, and participants.

#### Owning Module(s)

- Messaging owns Thread truth.
- Source context Modules own the referenced business-object truth.

#### Dependencies

- Prisma schema containing `Thread` and `ThreadContextType`.
- `resolveAuthenticatedActor` for user-triggered calls.
- `authorizeResourceAction` for protected calls.
- source-owner facts contract or fixture.
- canonical `executeIdempotentCommand`.

#### Shared Operations Used

- `resolveAuthenticatedActor` — Identity owns actor resolution; Messaging requires it for user-triggered thread access. Do not build a Messaging session helper.
- `authorizeResourceAction` — Role owns permission interpretation; Messaging supplies source/participant context. Do not encode a universal permission policy here.
- `queryOwnerFacts` — source Module supplies minimum context existence/participant facts. Do not import source repositories.
- `executeIdempotentCommand` — shared mechanism ensures retries converge; Messaging defines semantic identity as the typed canonical context.
- `acquireAggregateLock` or equivalent canonical transaction/constraint mechanism only if needed to resolve concurrent creation.

#### Data / Schema

Use existing:

- `Thread`;
- `ThreadContextType`;
- typed foreign keys and existing `@unique` constraints;
- `contextType`, `contextId`, `dataSensitivity`, `erasedAt`.

Do not add Booking/Dispute/Review context types. Do not remove generic/typed context fields in this feature. Add database/domain validation needed to prevent detectable context drift only if it is consistent with current schema and approved migration discipline.

#### Public Interfaces

- `ensureContextThread`.
- `resolveThreadContext`.
- owner-facts DTO contract per supported source Module.

#### Logic

- validate context type and canonical owner reference;
- ensure generic/typed fields do not contradict each other;
- use current unique constraints to converge concurrent creation;
- persist sensitivity supplied/validated through approved context policy;
- return existing Thread on semantic retry;
- never mutate source business state.

#### UI / Administrative Surface

A production UI is optional. Provide either:

- a protected development/contract harness; or
- a minimal context-thread proof surface inside whichever source workflow is available first.

The surface must show that the Thread is Messaging-owned and source object state is unchanged.

#### Authorization / Compliance

- actor must be authenticated for interactive use;
- Role / Authority must approve the requested thread action;
- source context owner supplies relationship facts;
- no healthcare-sensitive message content is introduced yet.

#### Events / Jobs / Integrations

None required. Do not introduce an outbox just to satisfy a pattern.

#### Failure Behavior

- invalid or mismatched context → typed validation/invariant error;
- source object unavailable → not-found/denied result from owner contract;
- concurrent duplicate create → return winning existing Thread;
- authorization denial → no Thread write.

#### Tests

- unit: context-binding validator;
- contract: owner-facts DTOs;
- integration: one Thread per current unique typed context;
- concurrency: simultaneous ensure calls converge;
- authorization/RLS: cross-user/source denial;
- negative: no direct cross-Module mutation.

#### Out of Scope

- direct/support threads;
- message persistence;
- attachments;
- realtime;
- notifications;
- Booking/Dispute/Review context decisions;
- Thread close/archive/freeze lifecycle.

#### Exit Gate

- Every currently supported typed context can be validated through an owner contract or fixture.
- Repeating or racing `ensureContextThread` produces one Thread under current schema.
- No source business table is mutated by Messaging.
- Authorization and RLS denial tests pass.
- Context drift tests reject contradictory typed/generic bindings.
- Typecheck, lint, unit, integration, and build checks pass.

---

### 02 Participant Authority and Thread Inbox

Add Messaging-owned participant membership, Role-owned permission interpretation, thread listing, and monotonic read-cursor behavior.

#### Objective

Allow current ThreadParticipants to discover and open authorized Threads while proving the structural split between participation truth and permission policy.

#### User-visible / Observable Result

An authenticated User sees only Threads in which they currently participate (or separately authorized admin/support views), can open Thread metadata, and can advance their read cursor without another actor changing it.

#### Owning Module(s)

- Messaging owns `ThreadParticipant` and read cursor.
- Role / Authority owns access decisions.

#### Dependencies

- Feature 01.
- Role / Authority public decision contract.
- RLS policy deployment/testing convention.

#### Shared Operations Used

- `resolveAuthenticatedActor`.
- `authorizeResourceAction` — Messaging supplies `getThreadParticipantFacts`; Role returns decision.
- `queryOwnerFacts` where source context affects invitation/participant eligibility.
- `appendAuditEvent` only for administrator/support membership changes if policy requires.

#### Data / Schema

Use existing `ThreadParticipant(threadId, userId, joinedAt, lastReadAt)`.

No participant status/history columns are added without architecture approval. If removal is exposed, current-state semantics must be explicit; historical membership is not silently claimed.

#### Public Interfaces

- `getThreadParticipantFacts`.
- `addThreadParticipant`.
- `removeThreadParticipant` only if approved for the first context workflow; otherwise keep internal/deferred.
- `listThreadParticipants`.
- `listThreadsForUser`.
- `getThread` metadata query.
- `markThreadRead`.
- unread-state query derived from `lastReadAt` once messages exist; before Feature 03 it may return zero/metadata only.

#### Logic

- participant membership is persisted only by Messaging;
- Role checks platform/admin/support/participant scope using owner facts;
- `lastReadAt` is monotonic and cannot move backward;
- list queries are pagination-safe and do not expose unrelated thread metadata;
- no `OrganizationMember` or `UserRole` rows are copied into Messaging.

#### UI / Administrative Surface

Minimal inbox/thread list with:

- authorized thread rows;
- source context label/reference;
- participant list where permitted;
- read state placeholder/metadata;
- loading, empty, error, denied states.

#### Authorization / Compliance

- only authorized participants/admin/support actors can query protected thread data;
- membership mutation requires a named Role action and source-context eligibility;
- no health-sensitive full content yet.

#### Events / Jobs / Integrations

No background job required.

#### Failure Behavior

- stale `markThreadRead` request → no regression; return current cursor;
- unauthorized add/remove → deny with no mutation;
- user not participant → thread does not appear in ordinary inbox;
- removed participant loses subsequent participant access under current-state semantics.

#### Tests

- unit: participant/current-user fact serialization;
- integration: add/list/remove current membership;
- contract: Role consumes Messaging facts without writing them;
- RLS: direct SQL/API attempts cannot read another user's Thread;
- concurrency: read cursor remains max(current, requested);
- E2E: two fixture participants see thread, third does not.

#### Out of Scope

- historical participant removal ledger;
- direct-thread dedupe;
- message content;
- healthcare view policy;
- moderation restrictions.

#### Exit Gate

- `ThreadParticipant` is the only conversation-membership truth used by Messaging.
- Role / Authority decisions and RLS agree for participant read/write paths.
- A User cannot discover an unrelated Thread through list/detail URL manipulation.
- `lastReadAt` cannot regress under stale/concurrent requests.
- No duplicate local permission engine exists.

---

### 03 Message Send, Edit, Delete, Read, and Realtime

Persist real messages and expose committed conversation changes through the approved realtime adapter.

#### Objective

Make context-bound text conversation usable end to end without external notification or file dependencies.

#### User-visible / Observable Result

Two authorized participants can open a Thread, send messages, see committed messages update in near real time, edit according to policy, product-delete a message, and see unread/read state update after refresh or realtime delivery.

#### Owning Module(s)

Messaging.

#### Dependencies

- Features 01–02.
- canonical idempotency.
- platform realtime adapter or approved Supabase Realtime integration.

#### Shared Operations Used

- `resolveAuthenticatedActor`.
- `authorizeResourceAction`.
- `executeIdempotentCommand` for `sendMessage`.
- `publishRealtimeChange` — platform adapter; Messaging defines audience and safe payload. Do not use Realtime as source truth.
- `sanitizeTelemetryMetadata` for errors/telemetry.
- `appendAuditEvent` only where root policy requires, not for every ordinary Message by default.

#### Data / Schema

Use existing:

- `Message` with `content`, `createdAt`, `editedAt`, `deletedAt`, `erasedAt`, nullable `senderId`;
- `ThreadParticipant.lastReadAt`.

Do not add MessageStatus or edit-history table in this feature.

#### Public Interfaces

- `sendMessage`.
- `editMessage`.
- `deleteMessage`.
- `listThreadMessages`.
- `markThreadRead` completed for real Message cursors.
- unread derived query.

#### Logic

- validate content size/shape according to root code standards and safe messaging policy;
- verify current participant/Role decision before all reads/writes;
- semantic idempotency prevents duplicate messages after client retries;
- edit changes content and `editedAt`; it does not fabricate revision history;
- delete sets `deletedAt`/display treatment; it does not set `erasedAt`;
- realtime event is published only after committed write and is safe to miss because client can refetch;
- unread state derives from messages newer than participant cursor rather than a new mutable unread boolean.

#### UI / Administrative Surface

Thread view with:

- paginated messages;
- composer;
- send pending/error retry state;
- edited marker;
- product-deleted presentation;
- unread/read update;
- realtime reconnect/fallback behavior.

#### Authorization / Compliance

- sender must be authorized participant or separately permitted actor;
- edit/delete action vocabulary must be defined in Messaging and interpreted by Role;
- do not expose raw deleted/erased content to ordinary clients;
- private bodies must not enter logs/analytics.

#### Events / Jobs / Integrations

- Realtime post-commit publication.
- No Notification integration yet; that is Feature 04/05.
- No confirmed domain outbox event is required in this feature.

#### Failure Behavior

- realtime outage → persisted Message still succeeds; client falls back to refetch;
- duplicate send → original result replayed;
- edit/delete conflict with already erased record → reject according to current owner invariant;
- authorization change between load and mutation → server rechecks and denies.

#### Tests

- unit: message serialization/deletion display;
- integration: send/edit/delete/list;
- idempotency: duplicate client submission one row;
- RLS/authorization denial;
- realtime adapter contract and safe audience;
- E2E: two-party text conversation and refresh recovery;
- privacy-safe telemetry fixture asserting body absent.

#### Out of Scope

- attachments;
- Notification delivery;
- edit revisions;
- retention cleanup;
- moderation freeze state;
- healthcare admin redaction.

#### Exit Gate

- Authorized participants exchange persistent messages end to end.
- Realtime loss does not lose or create Message truth.
- Duplicate send retries do not duplicate Message rows.
- Product deletion does not set privacy erasure state.
- Unread/read state is correct after refresh and concurrent cursor updates.
- Private bodies are absent from telemetry fixtures.

---

### 04 Message Media and Safe Notification Handoff

Attach validated MediaAssets to messages and establish the one-way Messaging → Notification handoff without yet enabling external providers.

#### Objective

Complete Messaging's core collaboration boundaries: Media owns files; Notification owns alerts; Messaging owns only the conversation and safe event metadata.

#### User-visible / Observable Result

A participant can attach an approved private file/image to a Message, authorized participants can request a short-lived Media access result through Media, and a Message send emits/requests a safe new-message notification intent containing no private body.

#### Owning Module(s)

- Messaging owns `MessageMedia`.
- Media / File Access owns MediaAsset/access mechanics.
- Notification will own resulting alert records beginning Feature 05.

#### Dependencies

- Feature 03.
- Media public readiness/access interfaces.
- canonical `attachValidatedMedia` contract.
- `requestNotification` contract available as Notification-owned interface or temporary contract stub.

#### Shared Operations Used

- `attachValidatedMedia` — contextual join pattern; Media remains file owner.
- `authorizeContextualResourceAccess` pattern through Messaging/Media owner-specific contracts where applicable.
- `recordSensitiveAccess` when Media/message sensitivity policy requires.
- `requestNotification` — Messaging supplies safe preview metadata only; must not call provider SDKs.
- `executeIdempotentCommand` for message/attachment mutation.

#### Data / Schema

Use `MessageMedia(messageId, mediaId)` only. No duplicate attachment bytes/URL fields are added to Message.

#### Public Interfaces

- `attachMediaToMessage` / `detachMediaFromMessage` implemented through the canonical attach contract.
- Messaging attachment-context query for Media.
- safe `requestNewMessageNotification` adapter to canonical `requestNotification`.

#### Logic

- require ready/non-erased/non-frozen Media status through Media API;
- require Messaging participant/attachment authorization;
- create/remove only contextual join;
- preview/download obtains signed access through Media, never raw object key;
- new-message notification metadata may include Thread ID, Message ID, sender-safe display reference, and authenticated action route, but not private Message body;
- Notification request occurs after Message commit; failure never rolls back Message.

#### UI / Administrative Surface

- attachment picker/upload integration using Media-owned UI/contract;
- attachment loading/denied/expired/error states;
- no permanent file URLs in rendered markup;
- notification handoff visible in integration test/admin trace if in-app Notification not yet implemented.

#### Authorization / Compliance

- participant authorization + Media access gate;
- healthcare/sensitivity gate placeholder may deny unsupported sensitive attachment paths until Feature 12;
- sensitive access proof as required.

#### Events / Jobs / Integrations

- optional post-commit `requestNotification`; no provider job yet.
- Realtime Message update references attachment metadata only after commit.

#### Failure Behavior

- unsafe/not-ready Media → Message attachment rejected without altering Media;
- signed URL expiry → reauthorize/reissue through Media;
- Notification intake unavailable → Message remains committed and operational error is visible;
- notification request validation rejects private body variables.

#### Tests

- contract: Media readiness and Messaging contextual fact exchange;
- integration: MessageMedia join creation/deletion does not delete MediaAsset;
- access: nonparticipant cannot get signed access through message context;
- safe-notification fixture rejects private content;
- E2E: authorized attachment upload/attach/view through short-lived access.

#### Out of Scope

- Notification records/delivery;
- provider email/SMS/push;
- healthcare-sensitive full implementation;
- moderation evidence snapshot.

#### Exit Gate

- No Messaging code stores bytes, storage keys, or permanent private URLs.
- MessageMedia cannot bypass Media readiness/access policy.
- Safe notification handoff contains no private Message body in contract tests.
- Notification failure does not roll back Message truth.
- Cross-participant attachment access tests pass.

---

## Phase 2 — Notification Rail Core

### 05 Canonical In-App Notification Intake and Center

Implement the first Notification vertical slice entirely inside Workin Ants: an authorized source requests an in-app User notification and the User can list, read, and dismiss it.

#### Objective

Establish `requestNotification` as the only alert intake path and prove Notification truth before adding external channels.

#### User-visible / Observable Result

An authenticated User sees an in-app notification center populated by a representative source event (including new-message intent), opens an authenticated action route, marks the alert read, and dismisses it without changing the source workflow.

#### Owning Module(s)

Notification owns notification truth. The source Module owns the triggering event.

#### Dependencies

- Feature 04 safe handoff.
- canonical idempotency.
- Identity/Role interfaces.
- existing Notification schema.

#### Shared Operations Used

- `requestNotification` — implemented by Notification.
- `resolveAuthenticatedActor` / `authorizeResourceAction` for user center actions.
- `executeIdempotentCommand` for intake and read/dismiss mutations.
- `createRequestContext`, `sanitizeTelemetryMetadata`.
- `appendAuditEvent` only for sensitive/admin actions, not every ordinary read by default.

#### Data / Schema

Use existing `Notification` and `NotificationStatus`.

For this first slice:

- target a concrete `userId` only;
- set `channel=in_app`;
- do not use Organization-target fan-out until U-CL07-09 is closed;
- do not claim multi-channel aggregate semantics;
- record in-app availability according to the approved owner service using existing status fields.

Do not add a new recipient table in this feature.

#### Public Interfaces

- `requestNotification`.
- `listNotifications`.
- `getUnreadNotificationCount`.
- `markNotificationRead`.
- `dismissNotification`.

#### Logic

- validate source type/id, template key placeholder/contract, priority, sensitivity, action route, safe variables, and idempotency key;
- create Notification only after request passes owner routing/payload checks;
- User can mutate only targeted notifications;
- read/dismiss never invokes source completion;
- unread count is Notification-specific and not Message unread state;
- expired behavior is not implemented beyond suppressing obviously stale display if architecture permits; no new expired status is invented.

#### UI / Administrative Surface

In-app notification center:

- unread/read states;
- priority indication;
- safe title/body;
- source-aware authenticated action link;
- read/dismiss actions;
- loading/empty/error states.

#### Authorization / Compliance

- User can view/mutate only own User-target notifications;
- server validates action route;
- no sensitive payload leakage;
- organization notifications deferred.

#### Events / Jobs / Integrations

No external provider job required. Notification may be made available synchronously after authoritative write.

#### Failure Behavior

- duplicate request idempotency key → original result;
- invalid action route/sensitivity variables → reject before write;
- source request succeeds but client center load fails → record remains durable;
- read/dismiss conflict → owner state machine returns deterministic result.

#### Tests

- unit: request validation and User target;
- integration: create/list/read/dismiss/count;
- idempotency duplicate intake;
- authorization/RLS cross-user denial;
- contract: Messaging safe request creates in-app alert;
- E2E: Message send → recipient in-app alert → click Thread → Message still source truth.

#### Out of Scope

- Organization targets;
- external email/SMS/push;
- push subscriptions;
- multi-channel aggregate status;
- provider callbacks.

#### Exit Gate

- At least one representative source Module can create an in-app alert only through `requestNotification`.
- Duplicate requests do not duplicate the semantic alert.
- User A cannot view/read/dismiss User B's notifications.
- Read/dismiss does not mutate the source business record.
- New-message alert carries safe metadata only.
- Notification center E2E passes.

---

### 06 Template Registry, Payload Safety, and Action Routes

Make notification content a controlled, versioned contract rather than arbitrary strings/JSON from source Modules.

#### Objective

Centralize transport rendering and privacy-safety rules before any content leaves Workin Ants.

#### User-visible / Observable Result

A developer/admin contract catalog shows the approved notification keys, versions, channels, variable schemas, sensitivity classification, and action-route builders. Invalid or sensitive variables cannot be rendered or persisted through the canonical intake path.

#### Owning Module(s)

- Notification owns rendering/transport schema enforcement.
- source legal/business Modules approve semantic meaning and source facts.

#### Dependencies

- Feature 05.
- PR-N05 or equivalent approved template-registry ruling.
- U-CL07-20/U-CL07-21 must be closed for production external channels; in-app development may proceed with a limited approved catalog.

#### Shared Operations Used

- `renderNotificationTemplate` — Notification canonical capability; do not build per-source renderers.
- `sanitizeTelemetryMetadata` — not a substitute for payload policy, but required for diagnostics.
- `hashCanonicalPayload` if template/version integrity hashing is adopted by root security standards.

#### Data / Schema

Prefer a code/config registry for MVP unless architecture approves a persisted template lifecycle.

Existing `Notification.name`, `title`, `body`, `payload`, `payloadSensitivity`, `safePreviewOnly` remain snapshot/output fields. `name` must be validated against the registry rather than treated as uncontrolled vocabulary.

#### Public Interfaces

- `renderNotificationTemplate` internal/public-to-Notification only.
- typed template-key/version schema exported for source callers.
- approved action-route builder/validator contract.

#### Logic

Each template definition specifies:

- stable key and version;
- permitted channels;
- typed safe variable schema;
- sensitivity category;
- whether body preview is allowed;
- locale fallback policy where applicable;
- approved action-route builder;
- channel length/content constraints;
- fields prohibited from provider payload.

Source Modules provide safe variables, not HTML/provider payloads.

#### UI / Administrative Surface

No end-user UI required. Provide an internal registry viewer or generated test catalog if useful.

#### Authorization / Compliance

- payload policy must reject PHI/private Message bodies/OTP/financial/tax/resume/contract raw text from outward templates;
- security/legal templates may show minimal safe instruction and require authenticated app access for details;
- action routes must be allowlisted authenticated routes and HTTPS in external rendering.

#### Events / Jobs / Integrations

None required.

#### Failure Behavior

- unknown template/version → reject request;
- wrong variable shape → reject before Notification write;
- channel not allowed → skipped/denied routing result, not provider call;
- unsafe variable detected → fail closed and record safe operational diagnostics.

#### Tests

- schema fixtures for every template/version/channel;
- prohibited-field injection tests;
- action-route allowlist tests;
- snapshot tests for safe rendering without copying sensitive source data;
- source contract tests fail if caller invents arbitrary `name`.

#### Out of Scope

- marketing campaign editor;
- mutable WYSIWYG template CMS;
- provider SDKs;
- source workflow legal decision rules.

#### Exit Gate

- Every notification created by Feature 05 uses a registered typed template key/version.
- Arbitrary JSON/body injection from source Modules is rejected.
- Prohibited sensitive fixtures cannot appear in rendered provider-safe output.
- Action URLs cannot point to arbitrary external destinations.
- Template tests cover all currently approved CL-07 source intents.

---

### 07 Web Push Permission and Subscription Lifecycle

Implement secure, user-controlled browser/PWA reachability before sending Web Push.

#### Objective

Make browser permission, consent proof, service-worker readiness, encrypted/hash subscription credentials, device listing, refresh, and revocation reliable Notification truth.

#### User-visible / Observable Result

A User can view push disclosure, request browser permission, register a supported browser/PWA subscription after permission is granted, see the connected device in account settings, refresh/rotate it, and revoke it.

#### Owning Module(s)

- Notification owns browser permission/subscription state.
- Consent & Disclosure owns versioned disclosure proof.
- Identity owns User/session truth.

#### Dependencies

- Feature 06.
- `queryConsentProof`.
- platform crypto `encryptSensitiveValue` and `normalizeAndHashIdentifier`.
- U-CL07-18 / PR-N04 approved before live credentials are stored.

#### Shared Operations Used

- `resolveAuthenticatedActor`.
- `authorizeResourceAction`.
- `queryConsentProof` — do not duplicate ConsentLog.
- `encryptSensitiveValue` — encrypt recoverable endpoint/token/key material.
- `normalizeAndHashIdentifier` — stable nonplaintext matching.
- `executeIdempotentCommand` for create/refresh/revoke.
- `appendAuditEvent` for device revocation/security-significant changes if root policy requires.

#### Data / Schema

Use:

- `NotificationSubscription`;
- `NotificationPermissionStatus`;
- `NotificationSubscriptionStatus`;
- `NotificationPlatform`;
- `PwaInstallStatus`;
- `NotificationSubscriptionEvent` and event type enum.

Apply approved migration/security policy so plaintext credential fields are not competing truth. Add/check database/application invariant that active Web Push subscription requires `permissionStatus=granted` if approved by migration standards.

Do not invent a second User device table solely for push.

#### Public Interfaces

- `recordNotificationPermissionState`.
- `recordServiceWorkerRegistrationState`.
- `upsertPushSubscription`.
- `refreshPushSubscription`.
- `revokePushSubscription`.
- `handlePushSubscriptionChange`.
- `recordPwaInstallReadiness`.
- `listNotificationSubscriptions`.

#### Logic

- consent proof is checked before platform-defined push onboarding where required;
- browser permission is observed, not fabricated by server;
- active subscription cannot be created on denied/unsupported permission;
- endpoint/token matching uses hashes; response never returns secrets;
- stale token-rotation events cannot overwrite newer state;
- revocation is idempotent and disables future delivery;
- iOS PWA readiness is capability metadata, not account status.

#### UI / Administrative Surface

Account notification settings:

- disclosure/permission state;
- browser/PWA guidance;
- connected device/subscription summaries;
- last seen/failure-safe metadata;
- revoke action;
- unsupported/denied guidance without dark patterns.

#### Authorization / Compliance

- User may manage only own subscriptions;
- ConsentLog remains separate;
- OS/browser permission is not proof of consent;
- no endpoint/token/key is displayed or logged.

#### Events / Jobs / Integrations

- service worker and browser client callbacks;
- no outbound Web Push required yet.

#### Failure Behavior

- denied permission → record state; no active subscription;
- unsupported browser/PWA → safe unsupported result;
- duplicate subscription → idempotent upsert by approved hash identity;
- refresh race → newest valid rotation wins;
- revocation failure in browser → server marks local state according to confirmed evidence and surfaces recovery guidance; do not claim OS state changed if unknown.

#### Tests

- unit: permission/status transitions;
- integration: create/refresh/revoke/list without plaintext credential exposure;
- crypto tests: stored authoritative credentials follow approved encrypted/hash rules;
- authorization/RLS cross-user denial;
- client/service-worker event contract tests;
- E2E on supported browser test environment where practical.

#### Out of Scope

- external push send;
- FCM/OneSignal/WonderPush selection;
- general notification preference center beyond confirmed reachability controls;
- native app device management.

#### Exit Gate

- Live subscription writes do not maintain plaintext credential authority.
- Active Web Push subscription cannot exist through the application path without granted permission.
- Consent proof and permission proof are demonstrably separate records.
- User can list and revoke only own connected notification devices.
- Token rotation is idempotent and stale-update safe.
- No provider secret or endpoint/token appears in client response/log fixtures.

---

### 08 Durable External Delivery Worker and Channel Ports

Add the durable Notification delivery pipeline with provider-neutral email, SMS, and Web Push ports; enable only providers whose selection/policy is approved.

#### Objective

Turn a safe Notification into durable asynchronous delivery work without spreading provider SDKs into source Modules.

#### User-visible / Observable Result

A test/admin surface shows queued → sending → sent/delivered/failed/skipped Delivery records. At least one approved external channel can be exercised in a nonproduction or production-safe environment; unselected channels use stubs/disabled adapters and return explicit unavailable/skipped outcomes.

#### Owning Module(s)

Notification.

#### Dependencies

- Features 05–07.
- canonical reliable queue/retry/observability primitives.
- U-CL07-20/U-CL07-21 closed for channels enabled in production.
- current root provider configuration for email; SMS/push production enablement waits for provider rulings.

#### Shared Operations Used

- `enqueueReliableJob` — one shared queue shell; do not create a Notification queue framework.
- `executeRetryWithBackoff` — technical retry only; Notification adapter classifies retryability.
- `recordQueueTelemetry`.
- `createRequestContext`.
- `renderNotificationTemplate`.
- `recordIntegrationFailure`.
- `captureException`, `emitMetric`, `sanitizeTelemetryMetadata`.

#### Data / Schema

Use `NotificationDelivery`.

Do not yet solve multi-attempt history if PR-N03/U-CL07-13 is unapproved. The worker may execute a single attempt per Delivery for this feature; production retries requiring preserved attempt history are Feature 09.

The current push-specific `NotificationSubscriptionProvider` must not be used to falsely label email/SMS providers. Provider-neutral result DTOs may include adapter key in operational metadata until the schema vocabulary is approved, but do not create misleading domain truth.

#### Public Interfaces

Internal Notification interfaces:

- `enqueueNotificationDeliveries`.
- `dispatchNotificationDelivery`.
- email provider port.
- SMS provider port.
- Web Push provider port.
- `recordProviderDeliveryResult`.
- Notification-owned `translateProviderStatus` implementation per adapter.

#### Logic

- intake creates authoritative Notification before queue work;
- route eligible channel(s) only under currently approved channel model;
- worker loads Notification snapshot and renders safe channel content;
- provider adapter receives normalized transport command;
- response is validated/translated to canonical delivery result;
- business source is never mutated;
- dead/invalid push response can set `shouldDisableSubscription` for a later owner transition;
- external provider outage does not lose Notification truth.

#### UI / Administrative Surface

Internal delivery inspector:

- Notification/source reference;
- channel;
- Delivery status/timestamps;
- normalized provider message ID when safe;
- safe failure code/category;
- retryability/disabled state;
- correlation ID;
- manual retry control only if permitted by worker policy.

#### Authorization / Compliance

- delivery inspector is restricted to authorized admin/support roles;
- sensitive payload/body is redacted in ops UI;
- legal/security content follows approved template/payload rules;
- SMS/push are disabled in production until provider/boundary approvals exist.

#### Events / Jobs / Integrations

- shared queue worker;
- email adapter — current root evidence may use AWS SES behind Notification port;
- SMS adapter — stub/disabled until U-CL07-16 approved;
- Web Push adapter — stub/disabled until U-CL07-17 approved;
- provider callbacks deferred to Feature 15.

#### Failure Behavior

- transient provider failure → visible failed/retryable execution; preserved Notification truth;
- permanent invalid destination → failed/skipped and subscription-health signal if applicable;
- queue failure/dead-letter → operational record plus Delivery remains truthful;
- provider unavailable → no source lifecycle rollback;
- unknown provider status → fail safe as unmapped/operational failure, never guess canonical success.

#### Tests

- queue job durability and idempotency;
- adapter contract tests;
- provider success/failure translation fixtures;
- source Module contains no provider imports;
- telemetry redaction;
- delivery worker crash/replay safe for one attempt;
- E2E nonproduction external test for each enabled adapter.

#### Out of Scope

- provider delivery callbacks;
- full retry attempt ledger;
- organization routing;
- marketing/bulk campaign delivery;
- provider-specific business logic outside Notification.

#### Exit Gate

- A safe Notification can produce a durable Delivery job and authoritative Delivery result.
- No source Module imports or calls provider SDKs.
- Queue retry/dead-letter/telemetry uses canonical infrastructure.
- Unknown/provider error states never become source business status.
- Production-enabled channels have approved payload catalog and provider selection; unapproved channels remain explicitly disabled/stubbed.
- Provider IDs/errors exposed to ops are normalized/redacted.

---

### 09 Delivery Attempt, Expiry, Interaction, and Aggregate Semantics

Close Notification's ambiguous delivery model before broad multi-channel production use.

#### Objective

Implement approved rules for retry attempt history, Notification aggregate status, expiry, dismissal timestamp/proof, and interaction canonicality.

#### User-visible / Observable Result

Admins can inspect a complete delivery attempt history; Users see consistent read/dismiss behavior; stale notifications do not send after expiry; interaction evidence is recorded in one approved canonical way; aggregate status is deterministic.

#### Owning Module(s)

Notification.

#### Dependencies

- Feature 08.
- Approved resolutions for U-CL07-10 through U-CL07-15 and U-CL07-19.
- PR-N02/PR-N03 if adopted.

#### Shared Operations Used

- `executeIdempotentCommand`.
- `enqueueReliableJob`.
- `executeRetryWithBackoff`.
- `deduplicateProviderEvent` later used by callbacks; callback processing itself Feature 15.
- `appendAuditEvent` where manual retry/admin intervention requires proof.

#### Data / Schema

Apply approved migration(s), potentially including only those explicitly ruled necessary:

- recipient/cardinality constraint;
- channel consistency rule;
- delivery attempt correlation/attempt number/idempotency fields;
- truthful provider vocabulary for non-push channels;
- `dismissedAt` and/or expiry representation;
- canonical interaction record/fields;
- notification aggregate reducer inputs.

Do not add fields speculatively beyond approved rulings.

#### Public Interfaces

- finalized delivery-state query for admin/owner callers with legitimate need;
- finalized `recordNotificationInteraction`;
- finalized retry/expiry worker commands;
- `markNotificationRead` / `dismissNotification` semantics updated only as approved.

#### Logic

- each attempt preserves history if PR-N03 approved;
- retry creates no duplicate Notification intent;
- expiry prevents late send and records approved skipped/expired evidence;
- aggregate status is computed by channel-specific approved policy;
- click/open/close never completes source workflow;
- manual retry uses same semantic Delivery/attempt model and is audited.

#### UI / Administrative Surface

Update delivery inspector to show attempt timeline and aggregate reason. Update notification center to show reliable dismissal/read behavior.

#### Authorization / Compliance

- admin retry cannot bypass payload safety or recipient eligibility;
- expired security/legal notices follow source-owner requirements; Notification does not decide legal deadline consequences;
- interactions are minimized and not used for covert behavioral tracking beyond approved product evidence.

#### Events / Jobs / Integrations

- expiry scan job;
- retry scheduling using shared queue;
- dead-subscription disable command where provider evidence supports it.

#### Failure Behavior

- max attempts reached → terminal Delivery failure + dead-letter/ops visibility;
- Notification aggregate remains deterministic under mixed attempts;
- expired item cannot be re-sent unless a new source-approved Notification intent is created or authorized manual action is explicitly supported;
- duplicate interaction callback → idempotent evidence.

#### Tests

- lifecycle transition matrix;
- retry/attempt history;
- expiry race with queued worker;
- mixed attempt aggregate cases;
- dismissal/read/click/open semantics;
- concurrency/idempotency;
- migration/backfill fixtures.

#### Out of Scope

- provider callbacks/reconciliation implementation (Feature 15);
- organization recipient routing;
- source business completion analytics.

#### Exit Gate

- All U-CL07-10 through U-CL07-15 decisions required by the implemented model are documented as Architecture Rulings.
- Retry history cannot be lost by overwriting one failure repeatedly.
- Expired notifications cannot deliver after the approved cutoff.
- Provider vocabulary is truthful for every enabled channel.
- Aggregate status is deterministic under all tested attempt combinations.
- Interaction evidence cannot be mistaken for source workflow completion in code/tests/UI copy.

---

## Phase 3 — Governance and Rail Collaboration

### 10 Organization Recipient Routing and Hiring Alerts

Prove Notification can route organization-scoped alert intent using Organization Hiring facts without owning membership or settings.

#### Objective

Support Organization/Hiring notifications through owner-specific recipient queries and `OrganizationNotificationSetting` consumption.

#### User-visible / Observable Result

An Organization hiring action can request an approved alert; eligible organization members receive in-app and enabled external notifications according to Organization-owned settings, while changing membership/settings immediately affects future routing without copying those records into Notification.

#### Owning Module(s)

- Organization Hiring owns Organization, OrganizationMember, OrganizationNotificationSetting.
- Notification owns resolved alert/delivery records.
- Role / Authority interprets org-scoped permissions.

#### Dependencies

- Features 05–09.
- Organization Hiring public recipient-facts interface.
- U-CL07-09 recipient/cardinality/fan-out ruling approved.

#### Shared Operations Used

- `resolveNotificationRecipients` — shared contract; Organization owns membership/settings facts, Notification dedupes/fans out.
- `queryOwnerFacts`.
- `requestNotification`.
- `authorizeResourceAction` for admin/user notification settings access.
- `executeIdempotentCommand`.

#### Data / Schema

Use Notification models according to approved recipient model. Do not move `OrganizationNotificationSetting` into Notification and do not duplicate it.

#### Public Interfaces

- Organization-owned `resolveOrganizationNotificationRecipients` or equivalent owner-facts query consistent with `resolveNotificationRecipients` contract.
- `requestNotification` accepts organization/group recipient descriptor per approved contract.

#### Logic

- source Job/Application/Interview Module requests semantic alert;
- Organization owner resolves member roles/settings to User IDs;
- Notification dedupes Users and applies channel reachability/payload policy;
- no Notification code interprets `OrganizationRole` itself beyond owner result;
- membership changes affect future alerts through owner query.

#### UI / Administrative Surface

- Organization Notification settings remain in Organization Hiring UI.
- Notification center remains User-facing.
- optional admin trace shows source organization, resolved User count, channel plan without exposing unnecessary membership data.

#### Authorization / Compliance

- Organization settings updates remain Organization-authorized operations;
- resume/application details must not leak into push payloads;
- hiring/FCRA notice semantics remain with Job Compliance / Candidate / Trust Verification owners.

#### Events / Jobs / Integrations

External delivery uses existing Notification workers/adapters.

#### Failure Behavior

- organization has no eligible recipients → explicit skipped/no-recipient result, not orphan Notification;
- one recipient/provider failure does not prevent other recipients from retaining their own Delivery truth under approved fan-out model;
- stale membership is not cached as source truth beyond any explicitly approved snapshot.

#### Tests

- contract: Organization recipient query;
- role/settings permutations;
- duplicate member resolution dedupe;
- no direct OrganizationMember writes from Notification;
- hiring E2E with safe notification payload;
- cross-organization denial.

#### Out of Scope

- hiring lifecycle changes;
- candidate resume access;
- organization membership management itself.

#### Exit Gate

- Organization-target notification routing has an approved cardinality/fan-out model and passing schema constraints.
- Notification does not own or mutate OrganizationMember/OrganizationNotificationSetting.
- Hiring alert E2E delivers only to owner-resolved eligible Users.
- Resume/private application fields are absent from outward payload fixtures.

---

### 11 Source-Module Notification Contract Pack

Standardize representative notification intents across the Workin Ants workflow landscape without importing those lifecycles into Notification.

#### Objective

Prove `requestNotification` is reusable for marketplace, hiring, scheduling, security, moderation/hold, subscription, and incentive sources with typed safe contracts.

#### User-visible / Observable Result

Representative real or fixture workflows can generate consistent in-app/external alerts through one Notification capability, and coding agents have a typed catalog rather than inventing provider calls or free-form Notification names.

#### Owning Module(s)

Notification owns delivery; each source Module owns its event meaning.

#### Dependencies

- Features 06–10.
- public source Module contracts/events as available.

#### Shared Operations Used

- `requestNotification`.
- `renderNotificationTemplate`.
- `resolveNotificationRecipients`.
- `publishDomainEvent` / `deduplicateDomainEvent` only where an owner chooses event-driven integration.
- `executeIdempotentCommand`.

#### Data / Schema

No new source lifecycle tables. Notification stores only source reference and safe snapshot fields required by its own truth.

#### Public Interfaces

Add/validate typed source intents for representative families:

- Messaging: new message;
- Order: paid/status action requiring user alert;
- Booking: confirmed/rescheduled/cancelled;
- Hiring: application/interview alerts;
- Track: subscription plan/entitlement lifecycle alert;
- Hold/Moderation: user/admin notice request;
- Prize/Reward: result/fulfillment alert;
- Identity: security/recovery delivery request only under the approved provider boundary.

#### Logic

- each source decides whether/when alert is required;
- source provides safe variable DTO and approved action route;
- Notification validates template and sensitivity;
- event-driven consumers dedupe event IDs; direct commands use semantic idempotency key;
- no source result is inferred from delivery success.

#### UI / Administrative Surface

No new general UI required beyond existing notification center and delivery inspector. Add integration fixtures/admin trace as needed.

#### Authorization / Compliance

- DMCA/FCRA/security alerts use source-approved legal/security content contract;
- no source sends PHI/private body/OTP/raw resume/contract text;
- notification channel eligibility does not bypass Consent/permission or owner policy.

#### Events / Jobs / Integrations

May add versioned event consumers only for source Modules that explicitly publish them. Do not create event names in this feature without source-owner approval.

#### Failure Behavior

- unknown source/template contract → reject;
- duplicate event → no duplicate notification effect;
- Notification unavailable → source business transaction remains committed; owner may retry through canonical mechanism;
- one channel failure does not mutate source state.

#### Tests

- contract tests per representative source family;
- event dedupe tests where used;
- source-repository isolation tests;
- sensitive payload lint/fixtures;
- one E2E from at least marketplace and hiring lanes.

#### Out of Scope

- source business UI/lifecycle implementation;
- generic marketing/broadcast platform;
- “notify all users” bulk campaign semantics.

#### Exit Gate

- At least one representative source from marketplace and one from hiring uses the same `requestNotification` contract.
- No source Module contains provider SDK dispatch.
- Duplicate direct/event requests do not duplicate alert effects.
- Template/source vocabulary is typed and versioned, not free-form.
- Source business state remains unchanged by Notification delivery outcomes.

---

### 12 Healthcare, Moderation, and Sensitive Access Messaging

Integrate the guardrail Modules required for protected conversations without moving their policy into Messaging.

#### Objective

Make private/healthcare conversation access and abuse-reporting enforce external decisions correctly and audibly.

#### User-visible / Observable Result

An authorized participant sees normal content; an admin/support actor receives full, redacted, metadata-only, or denied output according to Healthcare policy; a user can report a Message/Thread to Moderation; sensitive accesses create required AccessAuditLog proof.

#### Owning Module(s)

- Messaging owns Thread/Message output and target execution.
- Healthcare owns redaction/block decision.
- Content Moderation owns Report/Case/Action truth.
- Audit owns AccessAuditLog.

#### Dependencies

- Features 03–04.
- approved Healthcare view-decision contract (U-CL07-06).
- approved sensitive-access audit policy (U-CL07-07).
- Moderation public report/decision contracts.

#### Shared Operations Used

- `authorizeResourceAction`.
- Healthcare owner public interface (not a CL-07 shared operation).
- `recordSensitiveAccess`.
- `submitModerationReport`.
- `resolveModerationTarget` if approved by global architecture.
- `executeModerationDecision` for approved enforcement.
- `appendAuditEvent` for enforcement acknowledgement where required.

#### Data / Schema

Use existing Messaging records. Do not add local HealthcarePolicy, Report, ModerationCase, or AccessAuditLog replacements.

If moderation requires persisted Messaging restriction state beyond existing fields, U-CL07-05 must be resolved before implementing that enforcement type. Basic report submission can proceed without local restriction fields.

#### Public Interfaces

- safe Messaging target resolver for Healthcare/Moderation;
- `reportMessageOrThread` adapter to Moderation;
- moderation execution handler for only approved actions;
- `getThread`/`listThreadMessages` output supports full/redacted/metadata-only/denied result.

#### Logic

- base Role authorization runs first;
- Healthcare policy decides sensitive view behavior;
- Messaging applies decision without reconstructing policy;
- sensitive read attempts generate AccessAuditLog according to approved policy, including denied/redacted attempts where required;
- report creates Moderation-owned Report only;
- enforcement applies only signed/authorized Moderation decision and returns acknowledgement.

#### UI / Administrative Surface

- redacted/denied message states with safe explanation codes;
- report action and confirmation/reference;
- restricted admin/support view;
- no display of internal PHI policy details beyond safe reason codes.

#### Authorization / Compliance

This feature is compliance-heavy. Production healthcare-sensitive access must remain disabled until owner contracts/audit policy are approved and tests pass.

#### Events / Jobs / Integrations

Moderation orchestration/notification remains Moderation-owned; Notification may deliver source-requested notices through Feature 11.

#### Failure Behavior

- Healthcare decision unavailable → fail closed for sensitive admin/support content according to owner contract; ordinary participant path follows approved policy;
- Audit append failure for required sensitive access → follow Audit policy; do not silently return sensitive data if proof is mandatory;
- Moderation service unavailable → preserve local report submission intent only if canonical intake supports durable retry; do not create local case.

#### Tests

- healthcare allow/redact/block matrix;
- Role + Healthcare composition;
- AccessAuditLog proof for required actions;
- report creates Moderation target, not local row;
- enforcement cannot use `deletedAt` unless approved action explicitly maps to it;
- private body absent from audit/ops metadata.

#### Out of Scope

- healthcare policy authoring;
- moderation case UI/lifecycle;
- legal retention policy;
- automatic content classification/moderation.

#### Exit Gate

- Healthcare policy is consumed through owner interface and is not reimplemented in Messaging.
- Required sensitive reads create AccessAuditLog evidence with minimized payload.
- Message/Thread reports create Moderation-owned truth only.
- No moderation enforcement overloads deletion/erasure without an approved mapping.
- Sensitive payload redaction tests pass.

---

### 13 Privacy Enumeration and Execution

Register Messaging and Notification as proper Privacy targets without creating independent privacy workflows.

#### Objective

Allow Privacy / Data Erasure to inventory, export, erase, anonymize, detach, revoke, or retain CL-07-owned data through stable owner handlers.

#### User-visible / Observable Result

A Privacy test/admin workflow can discover CL-07 data for a subject, request owner-approved dispositions, observe explicit completed/retained/skipped/failed target results, and verify that CL-07 never marks the overall PrivacyRequest complete itself.

#### Owning Module(s)

- Privacy owns request/job/target/exemption/export lifecycle.
- Messaging and Notification own local execution against their records.

#### Dependencies

- Features 03–09.
- canonical Privacy handler protocol.
- U-CL07-08 retention rules approved before destructive production behavior for affected data classes.

#### Shared Operations Used

- `enumerateSubjectData`.
- `evaluateRetentionRequirement`.
- `executePrivacyInstruction`.
- `anonymizePersonalFields` if root Privacy architecture uses it.
- `deleteProviderResource` for Notification provider-side revocation/deletion where applicable.
- `executeIdempotentCommand`.
- `appendAuditEvent` for fulfillment evidence as directed by Privacy/Audit policy.

#### Data / Schema

Messaging targets:

- Thread/participant/message/message-media records and erasure markers.

Notification targets:

- Notification/Delivery/Subscription/SubscriptionEvent personal data and provider references.

Do not add PrivacyRequest/DataErasureJob/DataRetentionExemption columns or parallel workflow tables in CL-07.

#### Public Interfaces

- Messaging `enumerateSubjectData` and `executePrivacyInstruction` handlers.
- Notification equivalents.
- export serializer(s) returning owner-held subject data in Privacy-defined format.

#### Logic

- enumerate stable owner targets with supported dispositions;
- return retention facts, not invented legal conclusions;
- execute exactly the disposition instructed;
- wipe/anonymize Message content/sender only as approved;
- revoke/delete push subscriptions/provider resources when instructed;
- preserve relationships/required evidence according to retention instruction;
- return explicit result to Privacy.

#### UI / Administrative Surface

No separate CL-07 privacy UI. Use Privacy-owned admin/request surface and target execution trace.

#### Authorization / Compliance

- only Privacy-authorized orchestration invokes destructive handlers;
- handlers are idempotent and target-bound;
- export/sensitive data access follows AccessAuditLog rules;
- retention exemptions remain Privacy-owned records.

#### Events / Jobs / Integrations

- Privacy's queue/orchestration invokes handlers;
- Notification may call provider deletion/revocation adapter;
- CL-07 does not schedule its own global erasure worker.

#### Failure Behavior

- retained instruction → no forbidden destructive change; return retained result;
- provider deletion retryable → return retryable failure to Privacy orchestration;
- target already absent/erased → idempotent completed/absent result per protocol;
- partial owner failure does not mark PrivacyRequest complete.

#### Tests

- enumerate coverage for representative subject records;
- idempotent erase/anonymize/retain fixtures;
- deletedAt vs erasedAt distinction;
- provider subscription revocation/deletion stub;
- no direct Privacy mutation of CL-07 repositories in integration test;
- export excludes secrets and follows retention/sensitivity rules.

#### Out of Scope

- defining legal retention periods;
- PrivacyRequest UI/lifecycle;
- erasing neighboring Module records;
- audit-log destruction.

#### Exit Gate

- Privacy can enumerate both Messaging and Notification owner targets through public handlers.
- CL-07 handlers mutate only CL-07 truth and return explicit execution results.
- Product deletion and privacy erasure remain distinguishable in tests.
- No local PrivacyRequest/DataErasureJob/RetentionExemption implementation exists.
- Destructive production cases are enabled only for retention rules explicitly approved.

---

## Phase 4 — Cross-Cluster Integration

### 14 Marketplace, Hiring, Scheduling, and Entitlement Contract Proof

Prove the most important inbound/outbound CL-07 contracts with neighboring Clusters using real Module interfaces/events where available.

#### Objective

Demonstrate that CL-07 functions as a rail across the platform without pulling neighboring source truth into its repository or service layer.

#### User-visible / Observable Result

Representative critical workflows complete with communication effects:

1. Gig/Order context → Thread → Message → safe alert.
2. JobApplication/JobInterview context → Thread/Message and hiring alert.
3. Booking or scheduling event → Notification alert, while thread behavior respects the unresolved Booking-context ruling.
4. Track subscription/entitlement lifecycle event → Notification alert with no local entitlement interpretation.

#### Owning Module(s)

All participating Modules retain their own truth. Messaging/Notification own only communication records.

#### Dependencies

- Features 01–13.
- neighboring Module public interfaces available.
- U-CL07-02 must be resolved before creating any Booking-specific Thread context. If unresolved, prove Booking → Notification only.

#### Shared Operations Used

- `queryOwnerFacts`.
- `authorizeResourceAction`.
- `requestNotification`.
- `resolveNotificationRecipients`.
- `publishDomainEvent`/`deduplicateDomainEvent` only for approved event bridges.
- `attachValidatedMedia` for message attachments.

#### Data / Schema

No duplicate source records. CL-07 foreign keys/references remain references only.

#### Public Interfaces

Prove contracts with at least:

- Gig / Demand;
- Transaction / Order;
- Candidate Application & Resume Privacy;
- Job Interview / Organization Hiring;
- Booking & Calendar notification request;
- Track Subscription & Entitlement notification request.

#### Logic

- source owner determines participants/recipients and event timing;
- Messaging creates context Thread only through its own command;
- Notification accepts source alert only through canonical request/event consumer;
- source failure and communication failure are independently observable;
- no circular same-transaction callbacks: Messaging → Notification uses safe post-commit handoff; Notification does not synchronously read private Message body.

#### UI / Administrative Surface

Use the real available source workflow screens. Add correlation/diagnostic trace only for authorized internal testing.

#### Authorization / Compliance

- source role/owner rules remain source-owned;
- hiring resume details excluded from alerts;
- track entitlement event is alert trigger only, not local permission;
- Booking exact location and other sensitive context stays owner-protected.

#### Events / Jobs / Integrations

Representative event bridges should use the canonical outbox/inbox only when the source Module already defines an event. Do not invent a new event catalog solely in CL-07.

#### Failure Behavior

- Communication failure does not rollback source transaction.
- Source event retry does not duplicate Message/Notification effect under semantic idempotency.
- Missing owner facts returns safe deny/no-recipient, not cross-domain direct query fallback.

#### Tests

- contract and integration tests per bridge;
- E2E marketplace flow;
- E2E hiring flow;
- booking notification flow;
- subscription lifecycle alert flow;
- source-provider import scan ensuring no direct notification provider usage.

#### Out of Scope

- implementing missing source Module business features;
- resolving Booking/Dispute thread model inside CL-07;
- public Search.

#### Exit Gate

- Marketplace and Hiring critical journeys prove Messaging + Notification without ownership theft.
- At least one scheduling and one entitlement source proves Notification-only rail behavior.
- Communication provider failure leaves source truth intact.
- No source Module directly writes CL-07 tables or calls provider SDKs.
- All bridge contract tests use owner interfaces/events rather than cross-domain repositories.

---

### 15 Provider Callbacks, Deduplication, and Reconciliation

Complete the external delivery lifecycle for providers that emit asynchronous receipts and state changes.

#### Objective

Make provider callbacks authenticated, replay-safe, provider-normalized, reconcilable, and operationally visible while preserving Notification-owned provider-event truth.

#### User-visible / Observable Result

An admin can observe an externally delivered/failure callback update the correct Delivery once, see duplicate callbacks ignored safely, and run a reconciliation dry-run/report for a supported provider.

#### Owning Module(s)

Notification owns provider callback interpretation and local provider-event truth. Shared infrastructure owns signature/dedupe mechanics.

#### Dependencies

- Features 08–09.
- approved U-CL07-14 processed-provider-event schema.
- selected providers that actually support callbacks/query reconciliation.

#### Shared Operations Used

- `verifyProviderWebhookSignature`.
- `deduplicateProviderEvent`.
- `validateStructuredProviderOutput`.
- Notification-owned `translateProviderStatus`.
- `reconcileProviderState`.
- `recordIntegrationFailure`.
- `enqueueReliableJob` / `executeRetryWithBackoff` for callback follow-up/reconciliation.
- `createRequestContext`, `sanitizeTelemetryMetadata`.

#### Data / Schema

Add only the approved Notification-owned processed-provider-event record with:

- provider/event identity uniqueness;
- payload hash/version;
- processing result/status;
- safe references/correlation;
- timestamps needed by canonical dedupe pattern.

Do not reuse other Modules' processed-event tables.

#### Public Interfaces

- provider webhook Route Handler → Notification callback application service;
- reconciliation command/admin query;
- provider adapter callback parser/status mapper.

#### Logic

1. read raw body;
2. verify signature/timestamp;
3. validate event envelope;
4. atomically dedupe event;
5. map provider IDs to Notification-owned Delivery/subscription;
6. translate status;
7. idempotently apply transition;
8. record safe operational evidence;
9. mark processed-event outcome.

Reconciliation compares provider state to Notification truth and issues only safe owner-local repair commands.

#### UI / Administrative Surface

Provider callback/reconciliation inspector:

- provider/event reference;
- dedupe outcome;
- mapped Delivery/subscription;
- canonical transition;
- safe error;
- reconciliation discrepancy and repair result.

#### Authorization / Compliance

- webhook routes authenticate provider, not User;
- admin reconciliation requires Role authorization;
- raw payload is minimized/not retained unless approved and never logged wholesale;
- security/legal payload content remains protected.

#### Events / Jobs / Integrations

- provider webhooks;
- scheduled reconciliation for supported providers;
- shared queue for retries/repair jobs.

#### Failure Behavior

- invalid signature → reject before parse/side effect;
- duplicate event → acknowledged/ignored with no duplicate state change;
- unknown mapping → operational failure/manual review, no guessed success;
- missed callback found by reconciliation → idempotent owner-local repair when policy permits;
- unsafe discrepancy → incident/manual review, not automatic source business mutation.

#### Tests

- signature fixtures including replay/timestamp failure;
- duplicate callback concurrency;
- unknown status/provider event;
- processed-event uniqueness;
- reconciliation dry-run and allowed repair;
- raw-payload redaction/retention tests;
- provider sandbox E2E where available.

#### Out of Scope

- payment/calendar/video provider callback truth;
- global provider-event table;
- provider reconciliation changing source Order/Job/etc.

#### Exit Gate

- Every enabled callback provider verifies signature before state mutation.
- Duplicate callbacks produce one Notification side effect.
- Notification uses its own processed-provider-event truth rather than another Module's ledger.
- Unknown callback statuses fail safely and surface operationally.
- Reconciliation can detect/repair approved Notification discrepancies without touching source business truth.

---

## Phase 5 — Hardening and Production Readiness

### 16 CL-07 Security, Reliability, Privacy, and Performance Hardening

Perform the production-readiness pass after core Messaging, Notification, governance, privacy, and provider bridges are proven.

#### Objective

Close CL-07-specific security, failure, concurrency, privacy, observability, migration, and scale risks without expanding product scope.

#### User-visible / Observable Result

Messaging and Notification remain usable under provider degradation, duplicate/reordered requests, realtime loss, queue retries, dead subscriptions, large inbox histories, and privacy/moderation controls; operators can diagnose failures without seeing sensitive payloads.

#### Owning Module(s)

Messaging and Notification for their truth; platform owners for shared mechanisms.

#### Dependencies

- Features 01–15.
- all production-blocking Unresolved Decisions either approved or the dependent capability explicitly disabled.

#### Shared Operations Used

All previously used canonical operations, with special review of:

- `sanitizeTelemetryMetadata`;
- `recordIntegrationFailure`;
- `recordQueueTelemetry`;
- `checkServiceHealth`;
- `captureException`;
- `emitMetric`;
- `reconcileProviderState`;
- `encryptSensitiveValue`;
- `normalizeAndHashIdentifier`;
- `recordSensitiveAccess`;
- Privacy/Moderation protocols.

No new CL-07 duplicate infrastructure is permitted during hardening.

#### Data / Schema

Review and, only when justified by measured needs/approved rulings:

- indexes for thread list/message pagination;
- notification center/status/source queries;
- subscription lookup/failure cleanup;
- delivery/reconciliation queries;
- constraints for target/cardinality/channel/permission consistency;
- backfill safety for credential/provider/retry migrations;
- destructive migration rollback strategy.

No unread-count/latest-message projection is added solely by anticipation. Add a projection only if measured performance requires it and define it explicitly as rebuildable derived state.

#### Public Interfaces

Stabilize versions/contracts. Breaking changes require coordinated owner updates and architecture review.

#### Logic

Hardening checklist:

- rate-limit abuse-prone endpoints;
- fuzz/validate all public command payloads;
- verify no cross-Module direct repository imports;
- provider timeout/circuit-breaker behavior;
- dead-letter and manual retry safety;
- stale token cleanup;
- concurrency tests under load;
- realtime reconnect/refetch fallback;
- pagination and N+1 review;
- safe notification content under every sensitivity class;
- privacy handler partial failure/retry behavior;
- sensitive access audit completeness;
- moderation/healthcare fail-closed behavior where required;
- backfill dry runs and recovery plan;
- health checks and alert thresholds.

#### UI / Administrative Surface

- delivery/provider failure inspector is usable without secrets;
- connected-device management handles stale/dead subscriptions;
- notification center and thread inbox have stable loading/empty/error/retry states;
- operational admin tools are role-restricted and redact content.

#### Authorization / Compliance

Run formal cross-role matrices for participant, organization, admin, support, and own-device access. Verify no “support/admin means unrestricted” assumption exists for private/healthcare data.

#### Events / Jobs / Integrations

- load/retry/dead-letter testing for queue;
- provider sandbox degradation simulations;
- reconciliation under missed callback scenarios;
- alerting on queue lag/failure spikes without high-cardinality user dimensions.

#### Failure Behavior

Every meaningful degraded state must have an explicit user/admin/system behavior:

- realtime degraded → refetch/poll fallback;
- Notification provider down → source workflow intact, Delivery retry/failed, ops visible;
- Audit mandatory proof unavailable → sensitive path follows approved fail-closed policy;
- Privacy target transient failure → Privacy retries; overall request remains partial;
- invalid/dead push token → subscription disabled only after authoritative provider evidence;
- provider callback lag → reconciliation can recover supported states.

#### Tests

- full unit/integration/contract suites;
- Playwright critical journeys;
- authorization/RLS matrix;
- property/account/user boundary tests as defined by root architecture;
- concurrency/load tests for send, read cursor, notification intake, delivery, callback dedupe;
- provider degradation and reconciliation;
- privacy/destructive-action fixtures;
- telemetry secret/sensitive-data scanning;
- migration/backfill rehearsal;
- performance benchmarks for thread/message and notification pagination.

#### Out of Scope

- marketing automation;
- general CRM/contact center;
- native mobile app;
- private full-text Message search unless separately architected;
- new thread context types without owner ruling;
- speculative analytics warehouse.

#### Exit Gate

- Every production-enabled CL-07 capability has no unresolved architecture decision that materially changes its semantics.
- Typecheck, lint, unit, integration, contract, provider, and critical E2E suites pass.
- Authorization and RLS matrices show no cross-user/organization/participant leakage.
- Sensitive payload scanning finds no private message bodies, PHI, OTPs, credentials, tax/resume/contract raw text in telemetry or outward unsafe channels.
- Duplicate/reordered requests, provider callbacks, and worker retries do not duplicate business effects.
- Queue/provider failures are observable and recoverable without corrupting source business truth.
- Privacy handlers are idempotent and cannot complete PrivacyRequest outside Privacy.
- Backfill/migration rollback or recovery procedures are documented and rehearsed for all destructive/credential migrations.
- Delivery and thread inbox performance meet root production targets on representative data volume.

---

## Cross-Cluster Integration Phase

Phase 4 is the dedicated cross-Cluster integration phase. Its purpose is to prove contracts, not to absorb neighboring data.

Required proof before CL-07 is considered integrated:

```text
CL-01 Identity/Role/Consent
→ CL-07 Messaging/Notification authorization and consent gates

CL-03/04 marketplace/order
→ Messaging context thread + Notification alert

CL-06 hiring
→ application/interview thread + organization/candidate notification

CL-05 scheduling/media
→ MessageMedia secure file access + booking/session notification

CL-08 Privacy
→ enumerate/execute handlers

CL-09 Moderation/Audit/Ops
→ report/enforcement, AccessAuditLog, IntegrationFailure/queue evidence

CL-01 Track Subscription & Entitlement
→ lifecycle alert only; no CL-07 entitlement truth
```

No bridge may be “proven” by importing and mutating the neighboring Module's Prisma repository from CL-07.

---

## Hardening Phase

Phase 5 includes only CL-07-relevant hardening:

- participant/recipient authorization and RLS;
- credential encryption/hash migration;
- provider degradation/callback/reconciliation;
- queue retries/dead letters;
- Message/Notification idempotency and concurrency;
- privacy execution/retention gates;
- sensitive access audit completeness;
- telemetry redaction;
- notification payload safety;
- rate limits/abuse controls;
- pagination/performance;
- backfills/destructive migration safety;
- production health/ops readiness.

Hardening must not become a feature-expansion phase.

---

## Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Conversation Rail Core | 01 Context-Bound Thread Foundation; 02 Participant Authority and Thread Inbox; 03 Message Send/Edit/Delete/Read/Realtime; 04 Message Media and Safe Notification Handoff |
| 2 | Notification Rail Core | 05 Canonical In-App Notification Intake and Center; 06 Template Registry/Payload Safety/Action Routes; 07 Web Push Permission and Subscription Lifecycle; 08 Durable External Delivery Worker and Channel Ports; 09 Delivery Attempt/Expiry/Interaction/Aggregate Semantics |
| 3 | Governance and Rail Collaboration | 10 Organization Recipient Routing and Hiring Alerts; 11 Source-Module Notification Contract Pack; 12 Healthcare/Moderation/Sensitive Access Messaging; 13 Privacy Enumeration and Execution |
| 4 | Cross-Cluster Integration | 14 Marketplace/Hiring/Scheduling/Entitlement Contract Proof; 15 Provider Callbacks/Deduplication/Reconciliation |
| 5 | Hardening and Production Readiness | 16 CL-07 Security, Reliability, Privacy, and Performance Hardening |

**Total numbered features: 16.**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required context.
2. Confirm the previous exit gate.
3. Check CL-07 Unresolved Decisions and verify the feature is not crossing an unapproved boundary.
4. Write the feature implementation specification.
5. Confirm schemas, contracts, permissions, shared operations, providers, and tests.
6. Implement only that feature.
7. Run typecheck, lint, unit/integration/contract tests, and build as applicable.
8. Perform the workflow verification named in the feature.
9. Update `progress-tracker.md`.
10. Update architecture first if a binding decision legitimately changed.
11. Record risks, assumptions, disabled provider capabilities, and deferred work.

Do not start the next numbered feature merely because most code for the current feature exists. The exit gate is the completion boundary.

---

## Required Feature Specification

Immediately before implementation, every numbered feature receives a concise specification containing:

- Objective
- Observable result
- Dependencies
- In scope
- Out of scope
- Owning Module
- Data records affected
- Public interfaces
- Shared operations consumed
- Permissions
- Primary workflow
- UI/admin states if applicable
- Provider integrations
- Jobs/events
- Idempotency/concurrency
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation updates

The specification must name any Unresolved Decision the feature depends on and whether that decision has been approved. Do not pre-write giant low-level specifications for all future features; specify the next feature at implementation time against the then-current architecture.

---

## Required Completion Report

After each feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Shared operations reused
- Public interfaces added/changed
- Events/jobs added
- Provider adapters added/enabled/disabled
- Tests added/changed
- Commands run
- Manual/workflow verification
- Documentation updated
- Architecture rulings consumed
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

If the exit gate does not pass, report it as failed/blocked. Do not mark the feature complete or move to the next feature.
