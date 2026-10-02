# Messaging Module Implementation Plan

> **Module ID:** `messaging`  
> **Module name:** Messaging Module  
> **Primary Cluster:** CL-07 — Messaging & Notification Rail  
> **Companion architecture:** [Messaging architecture](<messaging-module-architecture.md>)\
> **Plan status:** implementation sequence subordinate to [CL-07 build plan](<../messaging-notification-rail-build-plan.md>); decision-gated where architecture remains unresolved\
> **Total numbered features:** 9

---

## Core Principle

Implement Messaging through narrow, verifiable vertical slices:

```text
public/observable behavior
→ validated command/query
→ Messaging-owned policy
→ authoritative Thread/Participant/Message write/read
→ canonical shared-operation calls
→ realtime / Notification / Audit / Privacy / Moderation effect where applicable
→ tests
→ exit gate
```

Messaging should become usable before external delivery, moderation, privacy orchestration, or healthcare-sensitive administration are fully wired. This plan follows the Messaging portions of the CL-07 build plan and does not independently reorder Notification work.

## Build Rules

1. Follow root architecture, code standards, Canonical Shared Operations, CL-07 architecture, and CL-07 build plan.
2. Messaging owns only its declared conversation truth.
3. Consume neighboring truth through approved public contracts, not cross-domain repositories.
4. Reuse canonical auth, authorization, idempotency, audit, realtime, telemetry, Media, Privacy, Moderation, and Notification operations.
5. Do not create Module-local copies of shared infrastructure.
6. Every mutation is runtime-validated, authenticated where interactive, and authorized server-side.
7. RLS is defense in depth and must agree with Role / Authority.
8. Mutations are transaction-safe and concurrency-aware.
9. `deletedAt` and `erasedAt` remain distinct.
10. Realtime publication happens after authoritative commit and never becomes truth.
11. Notification handoff happens after Message commit; alert failure does not roll back Messaging.
12. Attachments use Media / File Access; Messaging stores no bytes/object keys/permanent private URLs.
13. Healthcare policy is consumed, not authored here.
14. Privacy owns request/job/exemption orchestration; Messaging owns only local executor behavior.
15. Moderation owns Report/Case/Action truth; Messaging resolves targets/executes approved action.
16. No private Messaging data enters public Search.
17. No local premium/entitlement booleans or quotas.
18. Every feature ends with tests and an explicit exit gate.
19. Stop at unresolved architecture boundaries rather than inventing Thread statuses, edit history, new contexts, participant history, or erasure semantics.
20. Completion reports must identify shared operations reused and confirm no prohibited duplicate helper/service was added.

## Preconditions

**Shared Operations status:** references marked **Proposed ruling** are planning dependencies only, not approval for shared schema/API commitment or a generic service. Independently justified owner-specific interfaces do not approve a proposed shared operation globally. Realtime remains post-commit, authorized, and rebuildable; Moderation integration consumes approved contracts. Canonical metadata and reusable boundaries remain controlled by the Shared Operations registry.

**CL-07-R007 — Observability persistence boundary:** CL-07 consumes approved public capabilities for failure recording, queue telemetry, health, structured logging, metrics, and exception capture. `IntegrationFailure`, `QueueJob`, `OpsIncident`, and `SystemEvent` are not current Prisma models. CL-09 owns its unresolved persistence/status design. CL-07 must not create local substitutes or couple Messaging/Notification business status to any future operational record.

### Hard platform dependencies

Must exist before the feature that consumes them exits:

- Prisma/PostgreSQL migration workflow;
- root runtime validation convention;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction` and Role/RLS conventions;
- canonical SH-044 `executeIdempotentCommand`;
- request/correlation context;
- telemetry sanitization and SH-033 `writeStructuredLog` for direct structured operational logging;
- approved realtime adapter before Feature 04 exits;
- Audit SH-030 `recordSensitiveAccess` before Feature 07 enables sensitive production reads;
- Privacy handler protocol before Feature 08 exits.

If missing, implement the canonical prerequisite in its owning scope or pause the feature. Never create a Messaging-only substitute.

### Interfaces that may initially be stubbed

Contract fakes are allowed for Order, Gig/GigResponse/GigAssignment, JobApplication, JobInterview owner facts, Media readiness/access, Notification SH-041 `requestNotification`, Healthcare view decision, Moderation, and Privacy. Fakes must mirror public contracts only and must not become local source truth.

### Shared Operation reference metadata

Only referenced operations are listed. Invocation, local policy, and integration proof remain in the relevant features; canonical boundaries remain in the Shared Operations registry.

| ID / canonical name | Canonical owner | Classification | Status |
| --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | Platform capability | Confirmed |
| SH-002 `authorizeResourceAction` | Role / Authority | Cross-cutting capability | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Each source Module | Shared contract; separate implementations | Proposed ruling |
| SH-026 `authorizeContextualResourceAccess` | Relevant context owner | Shared contract; separate implementations | Confirmed |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Platform audit capability | Confirmed |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Cross-cutting capability | Confirmed |
| SH-032 `createRequestContext` | Observability / platform infrastructure | Platform primitive | Confirmed |
| SH-033 `writeStructuredLog` | Observability / Ops | Platform capability | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | Cross-cutting capability | Confirmed |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Cross-cutting capability | Confirmed |
| SH-041 `requestNotification` | Notification | Platform notification capability | Confirmed |
| SH-044 `executeIdempotentCommand` | Platform application infrastructure | Platform primitive | Confirmed |
| SH-046 `publishDomainEvent` | Platform event/outbox infrastructure | Platform primitive | Confirmed |
| SH-071 `publishRealtimeChange` (Proposed ruling) | Platform realtime adapter; Messaging is primary consumer | Infrastructure adapter | Proposed ruling |
| SH-090 `attachValidatedMedia` | Contextual domain Module; Media owns asset truth | Shared contract; separate contextual truth | Confirmed |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | Cross-cutting protocol | Confirmed |
| SH-096 `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | Cross-cutting protocol | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | Cross-cutting protocol | Confirmed |
| SH-101 `submitModerationReport` | Content Moderation & Legal Notice | Module public interface | Confirmed |
| SH-102 `resolveModerationTarget` (Proposed ruling) | Target registry contract; each owner supplies resolver | Cross-cutting capability | Proposed ruling |
| SH-103 `executeModerationDecision` | Moderation owns decision; each target owner executes | Cross-cutting protocol | Confirmed |
| SH-113 `ensureContextThread` | Messaging | Module public interface | Confirmed |
| SH-123 `validateOwnedTargetReference` | Target owner | Shared contract; separate implementations | Confirmed |

### Cluster sequencing map

- Features 01–05 support CL-07 Features 01–04.
- Feature 06 completes the Messaging-to-Notification boundary required by CL-07 Features 04–05.
- Feature 07 aligns with CL-07 Feature 12.
- Feature 08 aligns with CL-07 Feature 13.
- Feature 09 aligns with CL-07 Features 14 and 16 and the Cluster hardening phase.

### Decision gates

Do not resolve inside implementation:

- direct-thread uniqueness/deduplication;
- support-case linkage;
- Booking/Dispute/Review context types;
- participant removal history/invitation lifecycle;
- Thread close/archive/freeze state;
- Message edit revisions;
- moderation restriction persistence when current fields are insufficient;
- destructive erasure mechanics for non-null Message content;
- legal retention/audit-frequency policy.

---

# IMPLEMENTATION PHASES

## Phase 1 — Contracts and Source-of-Truth Foundation

### 01 Messaging Contracts, Repositories, and Context Invariants

#### Objective
Establish the Module boundary, persistence layer, contract types, and executable context invariants.

#### Observable Result
A contract/integration harness validates every currently typed Thread context, can read/write Messaging records through Messaging repositories, and rejects contradictory context bindings. No neighboring repository is imported.

#### Cluster Build-Plan Link
Supports CL-07 Feature 01 — **Context-Bound Thread Foundation**.

#### Dependencies
- current Prisma Messaging models/enums;
- root folder/code standards;
- runtime validation;
- owner-facts contract shape;
- request context and telemetry sanitization.

#### In Scope
- `src/modules/messaging` structure;
- public command/query contract types;
- owner-facts ports for current typed contexts;
- Messaging-only repositories;
- `validateThreadContextBinding`;
- stable result/error vocabulary;
- fixtures for each typed context;
- explicit code-boundary ownership for `ThreadParticipant` and `MessageMedia`.

#### Out of Scope
SH-113 `ensureContextThread`, direct/support creation, participant UI, messages, realtime, Media access, Notification, privacy, moderation, healthcare.

#### Module-Owned Data
`Thread`, `ThreadContextType`, `ThreadParticipant`, `Message`, `MessageMedia` repository foundation. No migration unless current schema cannot be applied.

#### Public Interfaces
Define signatures/types for SH-113 `ensureContextThread`, `resolveThreadContext`, `getThreadParticipantFacts`, `listThreadsForUser`, `getThread`, `listThreadMessages`, `sendMessage`, `markThreadRead`, `attachMediaToMessage`, SH-096 `enumerateSubjectData`, SH-095 `executePrivacyInstruction`.

#### Shared Operations Used
- SH-032 `createRequestContext` — platform correlation contract.
- SH-034 `sanitizeTelemetryMetadata` — safe error/telemetry serializer.
- SH-003 `queryOwnerFacts` (Proposed ruling) — contract shape only, fixture-backed.

**Prohibited duplicate:** `crossDomainThreadRepository`, generic `chatUtils` owning shared concerns.

#### Domain Logic
For typed contexts: exactly the matching typed FK may be set; `contextId`, when present, equals canonical owner ID; other typed FKs are null; unsupported context fails closed. `direct`/`support` are recognized but not fully created.

#### Authorization / Compliance
No user mutation yet. Contracts include actor/purpose where future protected operations require it. Repositories contain no permission policy.

#### Database / Transaction Behavior
Repositories touch Messaging tables only. Preserve unique typed FKs and composite PKs. Test setup may seed owner records externally, but Messaging application code does not mutate them.

#### Events / Jobs
None.

#### Provider Integration
None.

#### UI / Admin Surface
Optional protected developer harness only.

#### Failure Behavior
Invalid shape → `validation_error`; unsupported context → `unsupported_context`; contradictory fields → `context_mismatch`; DB constraints normalize to `conflict` without raw Prisma leakage.

#### Tests
Unit context matrix; contract owner DTOs; repository boundary integration; schema constraint checks; telemetry fixture proving Message content is excluded.

#### Documentation Updates
Update architecture only if schema evidence contradicts a binding invariant. Record direct/support uncertainty in progress tracker.

#### Acceptance Criteria
Messaging folder/repositories are ownership-safe; all typed contexts validated; contradictory bindings fail; no cross-domain repository/provider SDK; public contracts compile.

#### Exit Gate
Typecheck, lint, unit, contract, and DB integration tests pass; architecture review confirms no neighboring lifecycle/shared infrastructure absorbed.

---

### 02 Idempotent Context-Bound Thread Creation

#### Objective
Implement SH-113 `ensureContextThread` so current typed contexts receive one Thread and safe retries/races converge.

#### Observable Result
Order, Gig, GigResponse, GigAssignment, JobApplication, and JobInterview fixtures return the same Thread under repeat/concurrent calls with source records unchanged.

#### Cluster Build-Plan Link
Implements Messaging work in CL-07 Feature 01.

#### Dependencies
Feature 01; actor resolution; Role authorization; source owner-facts contracts/fakes; canonical idempotency; approved DB locking/constraint strategy.

#### In Scope
SH-113 `ensureContextThread`; typed owner-facts adapters; initial participant creation; sensitivity persistence from approved facts; idempotency fingerprint; concurrency-safe create/fetch-winner; `resolveThreadContext`.

#### Out of Scope
Direct/support, participant removal, messages, Booking/Dispute/Review contexts, Thread closure/status.

#### Module-Owned Data
`Thread` and initial `ThreadParticipant` rows.

#### Public Interfaces
SH-113 `ensureContextThread`, `resolveThreadContext`.

#### Shared Operations Used
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-003 `queryOwnerFacts` (Proposed ruling);
- SH-044 `executeIdempotentCommand`;
- canonical aggregate lock/transaction primitive only if needed.

**Prohibited duplicate:** source-local `findOrCreateChatThread`; Messaging-local idempotency store/framework.

#### Domain Logic
Source existence and relationship eligibility are validated through owner-specific SH-123 `validateOwnedTargetReference`; context type matches owner DTO; initial participants are valid/eligible; typed unique FK means one current Thread per source object; unique-race fetches/validates winner; source state is never mutated.

#### Authorization / Compliance
Interactive calls authenticate. Trusted source calls use root system actor. Role approves `thread.ensure` or equivalent. No sensitive message body yet.

#### Database / Transaction Behavior
Transaction covers canonical idempotency claim/replay, Thread insert/fetch-winner, initial participant inserts, and canonical replay result. Unique conflict is expected race handling, not a 500.

#### Events / Jobs
None required.

#### Provider Integration
None.

#### UI / Admin Surface
Contract harness or first available source workflow proof showing Thread ID/context/sensitivity/participants.

#### Failure Behavior
Source unavailable → `not_found`/owner denial; Role deny → no write; mismatch → `context_mismatch`; same key/different fingerprint → `idempotency_conflict`; race → winning Thread returned.

#### Tests
Each typed context; same-key replay; different-key same-context convergence; concurrent race; participant initialization; source unchanged; authorization/RLS denial.

#### Documentation Updates
If generic/typed context consistency cannot be safely enforced, surface architecture decision before migration.

#### Acceptance Criteria
All typed contexts can ensure a Thread; retries/races create one; source unchanged; participants are Messaging truth; no direct source repositories.

#### Exit Gate
CL-07 Feature-01-compatible contract/concurrency/auth/RLS tests plus typecheck/lint/build pass.

---

## Phase 2 — Participant and Message Lifecycle

### 03 Participant Membership, Inbox, and Monotonic Read Cursor

#### Objective
Implement current participant membership, participant-facts interface, authorized Thread discovery, and monotonic read state.

#### Observable Result
A User sees only Threads where they are current participant or separately authorized admin/support actor; current participants can be listed; read cursor advances but never regresses.

#### Cluster Build-Plan Link
Implements CL-07 Feature 02 — **Participant Authority and Thread Inbox**.

#### Dependencies
Feature 02; Role decision API; RLS conventions/tests; owner-facts for participant eligibility.

#### In Scope
`getThreadParticipantFacts`, `addThreadParticipant`, context-approved `removeThreadParticipant`, `listThreadParticipants`, `listThreadsForUser`, `getThread` metadata, `markThreadRead`, minimal inbox UI if source surface exists.

#### Out of Scope
Invitation/pending lifecycle, historical removal ledger, real Message unread, healthcare content, moderation restriction.

#### Module-Owned Data
`ThreadParticipant` and Thread metadata reads.

#### Public Interfaces
`getThreadParticipantFacts`, `addThreadParticipant`, `removeThreadParticipant` current-state-only, `listThreadParticipants`, `listThreadsForUser`, `getThread`, `markThreadRead`.

#### Shared Operations Used
Actor resolution; Role authorization; SH-003 `queryOwnerFacts` (Proposed ruling); canonical idempotency for membership; SH-029 `appendAuditEvent` only when admin/support membership policy requires.

**Prohibited duplicate:** local general thread permission engine or copied OrganizationMember/UserRole state.

#### Domain Logic
Messaging owns current membership; Role interprets it. Duplicate add is idempotent. Removal deletes current row only and makes no history claim. `lastReadAt = max(current, requested)`. List/detail queries are pagination-safe and anti-enumeration-safe.

#### Authorization / Compliance
Role decision required for participant reads/mutations; source eligibility required when context controls admission; nonparticipant cannot discover Thread.

#### Database / Transaction Behavior
Composite PK handles duplicate add; atomic conditional/max update for cursor; membership mutation and required audit follow root transaction/audit policy.

#### Events / Jobs
None required.

#### Provider Integration
None.

#### UI / Admin Surface
Minimal inbox/thread metadata with loading/empty/denied states.

#### Failure Behavior
Stale cursor no-op/current result; duplicate add current state; unauthorized mutation no write; removed User denied thereafter.

#### Tests
Participant serialization; add/list/remove integration; Role contract proves read-only facts; RLS cross-user denial; cursor concurrency; E2E two participants see Thread/third does not.

#### Documentation Updates
If real workflow requires historical membership, stop and resolve architecture before adding fields.

#### Acceptance Criteria
`ThreadParticipant` is sole current membership truth; Role/RLS agree; unrelated Users cannot discover Threads; cursor never regresses.

#### Exit Gate
Participant contract/integration/RLS/concurrency suites pass with no duplicate authorization engine/history claim.

---

### 04 Text Message Lifecycle and Realtime

#### Objective
Make persistent text conversation usable with send, edit, product delete, paginated reads, unread derivation, and safe realtime propagation.

#### Observable Result
Two authorized participants exchange durable messages, see updates in realtime or after refresh, edit/delete according to policy, and maintain correct read state even when realtime is unavailable.

#### Cluster Build-Plan Link
Implements CL-07 Feature 03 — **Message Send, Edit, Delete, Read, and Realtime**.

#### Dependencies
Feature 03; canonical idempotency; separately approved platform realtime adapter; telemetry sanitization. SH-071 `publishRealtimeChange` (Proposed ruling) is not confirmed infrastructure or approval to commit its shared API/schema.

#### In Scope
`sendMessage` text-only; `editMessage`; `deleteMessage`; `listThreadMessages`; stable pagination; unread query; realtime post-commit publication; Thread view/composer UI.

#### Out of Scope
Attachments, Notification handoff, edit revision ledger, privacy executor, moderation freeze, healthcare admin redaction.

#### Module-Owned Data
`Message`; `ThreadParticipant.lastReadAt`.

#### Public Interfaces
`sendMessage`, `editMessage`, `deleteMessage`, `listThreadMessages`, `getUnreadThreadState`, `markThreadRead`.

#### Shared Operations Used
SH-001 `resolveAuthenticatedActor`, SH-002 `authorizeResourceAction`, SH-044 `executeIdempotentCommand`, SH-071 `publishRealtimeChange` (Proposed ruling), SH-034 `sanitizeTelemetryMetadata`, SH-037 `recordIntegrationFailure` for degraded realtime when required.

**Prohibited duplicate:** websocket/message store or local retry/idempotency cache.

#### Domain Logic
Validate content server-side; sender authorized at mutation time; retry one Message; edit updates current content/`editedAt` without fake revisions; delete sets `deletedAt` only; erased content never re-exposed/edited; pagination uses `(createdAt,id)` until changed by architecture; unread derives from messages newer than read cursor; realtime payload minimized and refetch-safe.

#### Authorization / Compliance
Private body absent from telemetry/analytics. Sensitive admin/support path may remain disabled/metadata-only until Feature 07.

#### Database / Transaction Behavior
`sendMessage`: canonical idempotency claim + Message insert; post-commit realtime. Edit/delete revalidate current state and return deterministic conflicts. Cursor update remains atomic max.

#### Events / Jobs
No worker. No domain event unless root event registry requires it.

#### Provider Integration
Realtime only via platform adapter.

#### UI / Admin Surface
Paginated Thread view, composer, pending/error retry, edited marker, product-deleted presentation, read state, realtime reconnect/refetch fallback.

#### Failure Behavior
Duplicate send replays; realtime outage does not undo Message; changed authorization denies; erased target returns stale/privacy restriction; DB failure emits no downstream realtime.

#### Tests
Serialization/content rules; send/edit/delete/list; idempotent send; stable pagination ties; authorization/RLS; realtime adapter/reconnect E2E; body-absence telemetry; concurrent read cursor correctness.

#### Documentation Updates
If a sequence field is needed for performance/correctness, raise architecture decision rather than adding silently.

#### Acceptance Criteria
Persistent conversation works; realtime remains transport; deletion ≠ erasure; duplicate sends one row; body absent from telemetry.

#### Exit Gate
CL-07 Feature-03-equivalent E2E/unit/integration/RLS/idempotency/realtime tests pass.

---

## Phase 3 — Media and Rail Handoff

### 05 MessageMedia and Media Access Boundary

#### Objective
Allow ready private MediaAssets to be attached/accessed without moving file lifecycle into Messaging.

#### Observable Result
Authorized participant attaches a ready file/image; authorized participants obtain short-lived access through Media; nonparticipants cannot leverage Message context to access it.

#### Cluster Build-Plan Link
Implements the Media portion of CL-07 Feature 04 — **Message Media and Safe Notification Handoff**.

#### Dependencies
Feature 04; Media ready-asset validation; SH-090 `attachValidatedMedia`; contextual access/signed-access interface; sensitive access audit where required.

#### In Scope
`attachMediaToMessage`, `detachMediaFromMessage`, MessageMedia repository, attachment-context facts query, UI integration using Media-owned upload flow, safe attachment serialization.

#### Out of Scope
Upload/scan/storage/signed-url implementation, MediaAsset deletion, Notification handoff, unapproved healthcare-sensitive attachment flow.

#### Module-Owned Data
`MessageMedia` only.

#### Public Interfaces
`attachMediaToMessage`, `detachMediaFromMessage`, and Messaging-owned SH-026 `authorizeContextualResourceAccess`. Attachment facts may support the decision but are not an authorization contract.

For MessageMedia access, Messaging exposes its owner-specific SH-026 `authorizeContextualResourceAccess` decision bound to the actor, Thread, Message, MediaAsset, and requested action. It returns the contextual allow/deny decision and safe evidence; `ThreadParticipant` or `MessageMedia` facts alone are not authorization. Media consumes that decision through `requestMediaAccess`, independently applies MediaAsset readiness, safety/freeze/erasure, grant, and TTL rules, and owns downstream SH-087 `issueSignedMediaUrl`. Media must not reconstruct Messaging participant/access policy; Messaging must not issue signed URLs or call SH-087 directly.

#### Shared Operations Used
SH-002 `authorizeResourceAction`, SH-090 `attachValidatedMedia`, SH-026 `authorizeContextualResourceAccess`, SH-044 `executeIdempotentCommand`, SH-030 `recordSensitiveAccess` when required.

**Prohibited duplicate:** `chat-storage`, `message-signed-url`, upload validators, malware scanner.

#### Domain Logic
Message/Thread exist and actor authorized; Media reports ready/non-erased/non-frozen; join create is idempotent via composite PK plus canonical idempotency; detach removes join only; access requires Messaging context + Media decision; no permanent URL/object key stored.

#### Authorization / Compliance
Participant must have attachment authority; nonparticipant cannot use known media ID; unapproved sensitive attachment path fails closed.

#### Database / Transaction Behavior
Join write only after Media approval; duplicate join converges; Messaging never mutates MediaAsset.

#### Events / Jobs
None.

#### Provider Integration
None in Messaging.

#### UI / Admin Surface
Attachment picker/preview/download through Media interfaces with expired/denied recovery states.

#### Failure Behavior
Not ready → `media_not_ready`; denied → `media_access_denied`; expired signed access → reauthorize; repeated detach → idempotent absent state.

#### Tests
Media contract including actor/Thread/Message/MediaAsset/action binding, denial and unavailable decision with no grant/URL, and rejection of facts-only authorization; join create/delete without deleting MediaAsset; nonparticipant access denial; duplicate attach; no object key/permanent URL; E2E attachment.

#### Documentation Updates
If Media requires new contextual facts, update public contracts rather than adding direct repository access.

#### Acceptance Criteria
MessageMedia remains contextual truth; Media owns mechanics; access composes both owners; retries safe.

#### Exit Gate
Media contract/security/integration/E2E tests pass and no storage/provider helper exists in Messaging.

### 06 Safe New-Message Notification Handoff

#### Objective
Establish a one-way Messaging → Notification boundary after Message commit without implementing Notification delivery internals.

#### Observable Result
A committed Message produces a canonical SH-041 `requestNotification` call for intended recipients using body-free safe metadata. Notification outage/rejection does not undo the Message and is observable.

#### Cluster Build-Plan Link
Completes Messaging work in CL-07 Feature 04 and supplies the source contract used by CL-07 Feature 05.

#### Dependencies
Feature 05; Notification SH-041 `requestNotification` contract or approved stub; request/correlation context; telemetry sanitization; integration-failure recording.

#### In Scope
`buildNewMessageNotificationIntent`; post-commit Notification adapter; recipient calculation from current participants; safe Thread action route; idempotent downstream intent key tied to Message/event identity.

#### Out of Scope
Notification row/status/template rendering, email/SMS/push, delivery retries, organization routing.

#### Module-Owned Data
No new Messaging model.

#### Public Interfaces
`sendMessage` remains source command; Messaging calls Notification SH-041 `requestNotification` after commit.

#### Shared Operations Used
- SH-041 `requestNotification` — Notification owner;
- SH-032 `createRequestContext` — correlation;
- SH-034 `sanitizeTelemetryMetadata`;
- SH-037 `recordIntegrationFailure` on post-commit intake failure;
- SH-046 `publishDomainEvent` only if CL-07 later approves event-based handoff.

**Prohibited duplicate:** `messageEmailService`, `chatPush`, `smsNewMessage`, direct Notification repository write.

#### Domain Logic
Message must already be committed. Recipients are current eligible participants other than sender unless approved policy says otherwise. Intent contains Thread ID, Message ID, safe sender reference, template key/version, action route, sensitivity, correlation/idempotency. Message body and attachment access secrets are prohibited. Same Message must not create duplicate semantic alert intent.

#### Authorization / Compliance
Messaging does not decide provider/channel eligibility. For sensitive/healthcare Threads, Notification decides whether a channel/template is allowed; Messaging supplies sensitivity and safe source facts only.

#### Database / Transaction Behavior
Message transaction completes before Notification call. Do not transactionally couple Message persistence to provider state. If reliable outbox is later required, update architecture/event contract first.

#### Events / Jobs
None owned by Messaging.

#### Provider Integration
None.

#### UI / Admin Surface
No new UI; prove via contract trace and, once available, Notification center integration.

#### Failure Behavior
Unsafe payload rejected → Message remains; Notification unavailable → Message remains + operational failure; duplicate handoff → downstream idempotency prevents duplicate alert.

#### Tests
Safe payload schema rejects body/PHI/sensitive fields; Message survives Notification failure; recipient dedupe/exclusion; idempotent handoff; end-to-end Message → Notification contract when Notification core exists.

#### Documentation Updates
If CL-07 chooses outbox event over direct command, update CL-07 architecture before code.

#### Acceptance Criteria
No private body in Notification request; no provider/Notification persistence code in Messaging; Message remains authoritative on Notification failure; handoff traceable by Message/correlation ID.

#### Exit Gate
Contract/security/integration tests pass and prohibited payload fixture fields are absent.

---

## Phase 4 — Governance and Compliance Integration

### 07 Healthcare, Moderation, and Sensitive Access Composition

#### Objective
Apply external Healthcare, Moderation, Role, and Audit decisions to protected Messaging views/actions without transferring their lifecycles into Messaging.

#### Observable Result
Authorized participant receives permitted content; admin/support receives full/redacted/metadata-only/denied result according to Healthcare policy; required sensitive access creates `AccessAuditLog`; users can report Thread/Message; approved Moderation actions execute only through supported Messaging mappings.

#### Cluster Build-Plan Link
Implements Messaging work in CL-07 Feature 12 — **Healthcare, Moderation, and Sensitive Access Messaging**.

#### Dependencies
Features 04–06; approved Healthcare view-decision contract; approved sensitive-access audit policy; Moderation report/action contracts; SH-030 `recordSensitiveAccess`. SH-102 `resolveModerationTarget` (Proposed ruling) requires separate approval before committing its shared API/schema; this feature does not approve it.

#### In Scope
Role + Healthcare access composer; safe `getThread`/`listThreadMessages`; sensitive-access audit call; `reportMessageOrThread`; owner-specific Moderation target support through approved contracts; approved SH-103 `executeModerationDecision` mappings that fit existing Messaging fields.

#### Out of Scope
Healthcare policy authoring; Moderation case lifecycle; automatic content moderation; invented Thread freeze/status fields; arbitrary use of `deletedAt` for moderation.

#### Module-Owned Data
Existing Thread/Message data only; no local policy/case/audit tables.

#### Public Interfaces
`getThread`, `listThreadMessages`, `reportMessageOrThread`, planned SH-102 `resolveModerationTarget` (Proposed ruling; separate approval required), SH-103 `executeModerationDecision`.

#### Shared Operations Used
SH-002 `authorizeResourceAction`; Healthcare owner interface; SH-030 `recordSensitiveAccess`; SH-101 `submitModerationReport`; SH-103 `executeModerationDecision` protocol; SH-029 `appendAuditEvent` where required; SH-034 `sanitizeTelemetryMetadata`.

**Prohibited duplicate:** `hipaa-chat-policy`, local `MessageAccessLog`, local moderation-case table.

#### Domain Logic
Role authorization runs first. Healthcare decides sensitive view. Messaging serializes returned result without reconstructing policy. Required access audit is recorded, including denied/redacted attempts when policy says so. Report creates Moderation-owned truth only. Executor validates target/action envelope and returns `unsupported_action` instead of inventing a mutation.

#### Authorization / Compliance
Healthcare-sensitive admin/support production reads remain disabled until Healthcare and Audit policy contracts are approved and tested. Admin role alone never bypasses redaction/blocking.

#### Database / Transaction Behavior
Protected reads are read-only plus external audit write where mandatory. If audit proof is mandatory before return, audit failure fails closed. Moderation execution revalidates target current state in transaction.

#### Events / Jobs
Moderation orchestration remains external; no Messaging worker.

#### Provider Integration
None.

#### UI / Admin Surface
Redacted/blocked states with safe reason codes; report action/confirmation; protected admin/support view.

#### Failure Behavior
Healthcare dependency unavailable → fail closed for sensitive admin/support view; mandatory audit failure → do not return protected data; Moderation unavailable → canonical unavailable/retry path, no local case; unsupported action → no mutation.

#### Tests
Role+Healthcare matrix; AccessAuditLog critical path; report creates external truth only; unsupported enforcement no mutation; deletion/erasure not overloaded; body absent from audit/ops metadata.

#### Documentation Updates
If a Moderation action needs persistent restriction state, architecture/schema must be updated before implementation.

#### Acceptance Criteria
External policy owners stay authoritative; sensitive views are safe/auditable; no local healthcare/moderation/audit truth; enforcement mapping explicit.

#### Exit Gate
Healthcare composition, audit, moderation, authorization, and telemetry tests pass; production-sensitive path enabled only where decisions are closed.

---

### 08 Privacy Inventory, Export, and Owner-Local Disposition

#### Objective
Register Messaging as a Privacy data owner that can enumerate, export, erase/anonymize, or retain its own records without owning PrivacyRequest workflow.

#### Observable Result
Privacy can discover representative Messaging data for a subject, request an approved disposition, receive explicit result, and verify Messaging never marks overall PrivacyRequest complete.

#### Cluster Build-Plan Link
Implements Messaging work in CL-07 Feature 13 — **Privacy Enumeration and Execution**.

#### Dependencies
Features 04–07; canonical Privacy protocol; approved retention instruction shape; destructive Message-content erasure ruling before production destructive behavior.

#### In Scope
SH-096 `enumerateSubjectData`, SH-097 `evaluateRetentionRequirement`, `exportMessagingSubjectData`, SH-095 `executePrivacyInstruction`, Thread/participant/Message/MessageMedia target descriptors, idempotent erased/anonymized/retained/skipped/not-found results, deleted-vs-erased proof, safe export filtering.

#### Out of Scope
PrivacyRequest/DataErasureJob/DataRetentionExemption ownership, legal retention periods, MediaAsset deletion, Audit destruction, source-record erasure, guessed non-null Message erasure semantics.

#### Module-Owned Data
Thread, ThreadParticipant, Message, MessageMedia.

#### Public Interfaces
SH-096 `enumerateSubjectData`, SH-097 `evaluateRetentionRequirement`, `exportMessagingSubjectData`, SH-095 `executePrivacyInstruction`.

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

#### Shared Operations Used
Privacy SH-096 `enumerateSubjectData`, SH-097 `evaluateRetentionRequirement`, SH-095 `executePrivacyInstruction`; canonical idempotency; Audit operations where policy requires. Media/provider privacy execution remains with those owners via Privacy orchestration.

**Prohibited duplicate:** `gdprChatService`, local privacy job/queue/exemption table.

#### Domain Logic
Inventory is cursorable/subject-bound. Target descriptors identify owner `messaging` and an approved stable type/id; unresolved child-record mappings are reported as decision-gated rather than invented. Executor revalidates target. Retained instruction performs no forbidden destructive change. Already-erased/absent target returns idempotent canonical result. Product deletion is not erasure. Destructive content treatment remains disabled until approved. Export includes only subject-related owner data and excludes secrets/unowned provider data.

#### Authorization / Compliance
Only trusted Privacy orchestration invokes destructive handlers. User-facing privacy workflow remains Privacy-owned.

#### Database / Transaction Behavior
Each target execution is idempotent and transactionally revalidates state. Partial target failure returns explicit owner result and never aggregates request completion.

#### Events / Jobs
Privacy worker invokes Messaging handlers; no Messaging global erasure worker.

#### Provider Integration
None; Media/provider resources are separate owner targets.

#### UI / Admin Surface
No Messaging privacy UI; use Privacy-owned surfaces/harness.

#### Failure Behavior
Unresolved destructive policy → decision-gated/unsupported; retained → no destructive mutation; already absent/erased → replay-safe result; DB failure → retryable/terminal protocol result; partial failure does not complete request.

#### Tests
Subject inventory coverage; export filtering; idempotent dispositions where approved; `deletedAt` vs `erasedAt`; no Privacy rows created; no direct Media deletion; duplicate executor delivery; audit/telemetry minimization.

#### Documentation Updates
When destructive erasure is approved, update Module architecture Section 28 and schema first if required.

#### Acceptance Criteria
Privacy can inventory/execute through public handler; Messaging mutates only its truth; overall request remains Privacy-owned; deletion and erasure distinct; unresolved destructive cases remain disabled.

#### Exit Gate
Privacy contract/idempotency/DB/security tests pass; destructive production behavior enabled only for approved dispositions.

---

## Phase 5 — Cross-Module Integration and Hardening

### 09 Cross-Cluster Contract Proof and Production Hardening

#### Objective
Prove Messaging works as a reusable rail across marketplace/hiring and harden authorization, concurrency, privacy, realtime, telemetry, and performance without absorbing source truth.

#### Observable Result
Representative flows demonstrate:
1. Order/Gig → Thread → participants → Message → safe Notification intent.
2. JobApplication/JobInterview → Thread → participants → Message.
3. MessageMedia through Media access.
4. Healthcare/admin path applies owner decision/audit where enabled.
5. Privacy inventories/executes through Messaging handlers.
6. Source lifecycle records remain unchanged except through their own owners.

#### Cluster Build-Plan Link
Supports CL-07 Feature 14 and Messaging portions of Feature 16.

#### Dependencies
Features 01–08; real source interfaces where available; Notification core contract; Media interface; production Role/RLS; enabled Privacy/Healthcare/Audit/Moderation interfaces.

#### In Scope
Real marketplace and hiring contract wiring; source-to-Messaging interface proof; RLS penetration/anti-enumeration; concurrency stress; idempotency replay; realtime reconnect/refetch; query/index performance; telemetry redaction review; privacy coverage; approved migration/backfill verification; production-readiness checklist.

#### Out of Scope
Inventing Booking/Dispute/Review contexts, Notification provider code, Search indexing, CRM/support-case expansion, legal retention rules, new Thread status/edit history without architecture decision.

#### Module-Owned Data
All existing Messaging-owned models may be exercised; no new record solely for hardening.

#### Public Interfaces
All implemented Messaging public commands/queries/privacy/moderation interfaces are treated as stable/versioned boundaries. Breaking changes require context updates.

#### Shared Operations Used
All previously integrated shared operations, especially actor resolution, Role authorization, idempotency, realtime, sensitive audit, telemetry sanitation, integration-failure recording, Notification handoff, Privacy, and Moderation protocols.

**Prohibited duplicate:** hardening-specific local auth/cache/lock/retry frameworks.

#### Domain Logic
Owner facts remain minimized/versioned; one Thread per current typed context; permission rechecked at read/mutation; replay returns same semantic result; pagination stable; private body never leaks to Notification, telemetry, audit metadata, or Search; downstream failures never corrupt Messaging truth.

#### Authorization / Compliance
Run full participant/admin/support/healthcare matrix for enabled paths. Verify sensitive-access proof/fail-closed requirements. Confirm no entitlement/hold logic was added without explicit policy.

#### Database / Transaction Behavior
Stress simultaneous Thread ensure; same/different-key send; participant add/remove vs send; concurrent cursor updates; edit/delete/erase races; attachment races; migration/backfill safety for approved changes only.

#### Events / Jobs
If Messaging events have been approved by this point, verify outbox atomicity and consumer dedupe. If not, do not invent events during hardening.

#### Provider Integration
Realtime adapter failure/recovery only.

#### UI / Admin Surface
Playwright critical flows for inbox/thread/composer/attachment/redacted/denied/report states where owned.

#### Failure Behavior
Dependency outage returns stable error; realtime degrades to refetch; Notification outage leaves Message valid; mandatory audit failure fails closed; concurrent conflict deterministic; unsupported privacy/moderation action explicit; no partial local mutation.

#### Tests
Real/fake contract suites; load/performance inbox/messages; RLS/security/anti-enumeration; concurrency/idempotency stress; privacy/healthcare/moderation/audit matrices; E2E marketplace/hiring conversation, attachment, Notification handoff; telemetry sensitive-data scan; migration tests if applicable.

#### Documentation Updates
Update progress tracker; Module architecture if binding decision changed; CL-07 architecture/build plan first for Cluster contract changes; Canonical Shared Operations only for actual shared-contract changes.

#### Acceptance Criteria
At least one marketplace and one hiring source use Messaging only through public contracts; no source direct Messaging inserts as normal behavior; Role/RLS agree; known races deterministic; private data absent from telemetry/Notification/Search; guardrail boundaries respected; downstream failure does not corrupt truth; benchmark baseline/threshold recorded.

#### Exit Gate
Full Module suite, CL-07 Messaging integration suite, Playwright journeys, typecheck/lint/build, RLS/security, privacy, concurrency/idempotency tests pass; unresolved architecture remains documented, not encoded as assumptions.

---

# MODULE INTEGRATION PHASE

Feature 09 is the final integration proof, but every earlier boundary requires contract tests.

| Boundary | Minimum proof |
| --- | --- |
| Identity → Messaging | anonymous protected call denied; trusted actor accepted |
| Messaging ↔ Role | Role consumes participant facts; service/RLS agree; Role never writes membership |
| Order/Gig → Messaging | source requests Thread through SH-113 `ensureContextThread`; source status unchanged |
| Hiring → Messaging | JobApplication/JobInterview Thread through public contract |
| Messaging ↔ Media | MessageMedia only after ready/access; Media issues signed access |
| Messaging → Notification | committed Message produces body-free SH-041 `requestNotification` |
| Messaging ↔ Healthcare | owner decision applied, not copied |
| Messaging ↔ Audit | required sensitive access proof through Audit contract |
| Messaging ↔ Moderation | report/case external; executor target-bound |
| Privacy → Messaging | inventory/executor handlers; Privacy remains orchestrator |

No integration test should depend on Messaging application code mutating neighboring production repositories directly.

# MODULE HARDENING PHASE

Hardening centers on Feature 09.

### State-transition races
Context Thread creation, participant add/remove vs send, edit/delete/erase, cursor regression, attachment duplicates.

### Idempotency/replay
Same key+fingerprint replay; same key+different fingerprint conflict; Notification handoff dedupe by Message source identity; Privacy executor duplicate delivery.

### Provider outage
Realtime adapter only. Degrade to refetch; record operational failure; do not alter Message truth.

### Security
RLS/anti-enumeration, server-side auth, no client actor trust, root rate limits, no permanent private URLs.

### Sensitive access
Healthcare composition, Audit criticality, minimized admin/support output, no sensitive telemetry.

### Privacy/retention
Inventory completeness, deletion-vs-erasure, decision-gated destructive behavior, retained-result compliance, no Privacy ownership leakage.

### Audit completeness
Audit policy must explicitly define which actions require AuditEvent/AccessAuditLog. Do not infer “audit every read” from enum vocabulary.

### Telemetry safety
Automated fixtures scan logs/error metadata for Message bodies, PHI, resume text, object keys, signed URLs, tokens, and other prohibited fields.

### Backfill/migration
Any future context, participant-history, erasure, or moderation-state migration requires architecture update plus migration/backfill tests.

### Performance
Benchmark Thread inbox pagination, message pagination, unread derivation, participant-facts lookup, and Thread ensure under contention. Add projections/indexes only from evidence and keep them rebuildable.

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
| --------- | -------- | ------------ |
| 1 | Contracts and Source-of-Truth Foundation | 01–02 |
| 2 | Participant and Message Lifecycle | 03–04 |
| 3 | Media and Rail Handoff | 05–06 |
| 4 | Governance and Compliance Integration | 07–08 |
| 5 | Cross-Module Integration and Hardening | 09 |

**Total features: 9**

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read Canonical Shared Operations.
3. Read CL-07 architecture and build plan.
4. Read this Module architecture and plan.
5. Read direct dependency public-interface sections.
6. Confirm prior exit gate.
7. Write the concise implementation specification for this feature.
8. Implement only this feature.
9. Run required quality checks.
10. Verify workflow/contracts.
11. Update progress.
12. Update architecture first if a binding decision legitimately changed.
13. Record unresolved risks.

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a feature, produce:

- Objective
- Observable result
- Dependencies
- In scope
- Out of scope
- Owned data affected
- Public contracts
- Shared operations consumed
- Permissions/compliance
- Primary workflow
- Provider integration
- Jobs/events
- Idempotency/concurrency
- Error behavior
- Tests
- Acceptance criteria
- Documentation updates

Do not generate all later feature specifications in advance; use current repository/interface state.

# REQUIRED COMPLETION REPORT

After each feature report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Events/jobs added
- Provider adapter changes
- Tests added/changed
- Commands run
- Manual/contract verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

Also state whether any prohibited duplicate helper/service was introduced. Expected result: none; exceptions require architecture review.

# FINAL QUALITY CHECK

Before declaring this plan complete verify:

1. Messaging exclusively owns Thread/ThreadParticipant/Message/contextual MessageMedia truth.
2. Role interprets permission without mutating participant truth.
3. Source business lifecycles remain outside Messaging.
4. Media owns file truth/signed access.
5. Healthcare owns sensitive-view policy.
6. Privacy orchestration remains Privacy-owned.
7. Moderation case/action truth remains Moderation-owned.
8. Audit ledgers remain Audit-owned.
9. Notification delivery remains Notification-owned.
10. Realtime remains transport.
11. No private Messaging data enters public Search.
12. Canonical shared operations are consumed, not duplicated.
13. Mutations are validated, authorized, transaction-safe, idempotent where retryable.
14. Every feature has tests and exit gate.
15. Feature order stays subordinate to CL-07 build sequence.
16. Decision-gated areas remain blocked rather than guessed.
17. A coding agent can execute the plan without inventing architecture.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.


## WA-R021 — Notification recipient and attempt model

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R021 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r021--notification-recipient-and-attempt-model) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one logical Notification per resolved User recipient and semantic source intent; channels are deliveries of that notification. Organization is source/context, not an inbox principal. Hiring supplies the authorized recipient set and source-policy version; Notification expands/deduplicates User recipients and snapshots the resolved routing context. Revalidate current sensitive access before including protected payload or dereferencing context; a historical fan-out snapshot grants no future access. Source Modules own recipient eligibility and message meaning; Notification owns safe rendering, channel routing and provider mechanics.

Each delivery attempt has its own immutable attempt identity and correlation to logical notification, recipient, channel, destination generation and semantic send key. Retrying unknown provider outcomes reconciles before resending. Provider acceptance is not confirmed delivery or user interaction. Notification summary separately tracks pending/in-progress, partial success, all required routable deliveries successful, or exhausted failure; dismiss/read state remains independent and never alters source workflow status. The database pass must provide a representation for partial delivery rather than mapping it to total success. Policy may mark a channel optional; that requirement is snapshotted before dispatch, not rewritten to hide failure.

Persist dismissedAt/expiresAt when these actions/policies apply. User interaction is Notification-owned append-only evidence separate from Delivery receipts. Template versions are immutable and schema-validated; source supplies a registered semantic template intent plus allowlisted variables. Generic external channels carry minimal safe summaries/deep links, never raw message bodies, financial/tax documents, exact addresses or regulated data by default. Identity challenge-provider transport stays Identity-owned. Concrete provider selection/configuration and legally sufficient notice delivery remain external prerequisites.

Tradeoff: explicit parent/attempt representation needs schema alignment but avoids multiple inbox items per channel and false completion. Acceptance: organization fan-out dedupe, removed member sensitive access, duplicate send, partial channel failure, expiry/dismissal independence, callback before/after retry, unsupported channel and secret redaction.

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
