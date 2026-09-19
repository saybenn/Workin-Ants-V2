# Messaging Module Architecture

> **Module ID:** `messaging`  
> **Module name:** Messaging Module  
> **Module type:** `capability`  
> **Build status:** `mvp_active`  
> **Primary Cluster:** CL-07 — Messaging & Notification Rail  
> **Document status:** Implementation-grade Module architecture; binding where stated as Confirmed or Architecture Ruling; non-binding where marked Proposed Ruling; unresolved items are decision gates  
> **Audience:** coding agents, developers, reviewers, maintainers, privacy/compliance reviewers, architecture agents  
> **Update rule:** update this file when a binding Messaging ownership, lifecycle, public-contract, privacy, authorization, moderation, or realtime decision changes. Build progress must not silently redefine architecture.

---

## 1. Module Header

Messaging is one of two Deep Modules in CL-07. The Cluster coordinates Messaging and Notification but owns no persisted lifecycle truth. Root Workin Ants architecture remains authoritative for platform identity, authorization, privacy orchestration, audit, observability, file mechanics, shared operations, provider rules, and coding standards. CL-07 architecture governs rail-level separation and sequencing. This document narrows those decisions to Messaging.

### Source reconciliation

- Historical registry evidence listed `ThreadParticipant` under Role / Authority, while the Messaging registry, glossary, Module extract, and CL-07 architecture assign the row/lifecycle to Messaging and permission interpretation to Role / Authority. **Architecture Ruling:** Messaging owns `ThreadParticipant`; Role consumes participant facts.
- File-adjacent evidence can make `MessageMedia` look Media-owned. The glossary and CL-07 architecture define contextual joins as contextual-Module truth. **Architecture Ruling:** Messaging owns `MessageMedia`; Media / File Access owns `MediaAsset`, upload/scan/storage/access mechanics.

## 2. Purpose, Goal, and Transformation

### Purpose
Maintain reusable, context-bound conversations between authorized Workin Ants actors.

### Goal
Provide one secure conversation source of truth so Order, Gig, hiring, support, privacy, moderation, and other workflows do not create separate chat tables, participant records, attachment joins, read cursors, or conversation-specific authorization systems.

### Inputs
- authenticated User/system actor context;
- approved `ThreadContextType` and canonical context ID;
- source-owner relationship/participant facts;
- initial/subsequent participant IDs;
- message content;
- optional validated `MediaAsset` references;
- Thread data-sensitivity classification;
- Role / Authority decision;
- Healthcare allow/redact/block decision when applicable;
- Moderation decision when applying enforcement;
- Privacy instruction for owner-local disposition/export;
- correlation and idempotency context.

### Outputs
- `Thread`;
- `ThreadParticipant` membership and `lastReadAt`;
- `Message`;
- contextual `MessageMedia` joins;
- safe authorized Thread/Message views;
- post-commit realtime updates;
- safe Notification requests;
- privacy/moderation execution results;
- audit/sensitive-access requests where required.

```text
conversation intent
+ actor
+ source-owner facts
+ external authority/compliance decisions
→ Messaging-owned mutation/query
→ committed conversation truth
→ optional realtime / Notification / Audit / Privacy / Moderation effect
```

Messaging deserves its own Module because conversation truth is durable and reused across unrelated business domains while remaining independent from the business lifecycle that caused the conversation.

## 3. Owned Truth

| Record / enum | Meaning | Ownership |
| --- | --- | --- |
| `Thread` | Canonical conversation and context binding. | Confirmed |
| `ThreadContextType` | `order`, `gig`, `gig_response`, `gig_assignment`, `job_application`, `job_interview`, `direct`, `support`. | Confirmed |
| `ThreadParticipant` | Current User membership in a Thread plus join/read timestamps. | Architecture Ruling |
| `Message` | Message body and create/edit/product-delete/privacy-erasure markers. | Confirmed |
| `MessageMedia` | Contextual relationship between Message and MediaAsset. | Architecture Ruling |

`DataSensitivity` is stored on `Thread`, but Messaging does not own the shared sensitivity vocabulary or Healthcare policy that interprets it.

### Lifecycles owned
- Thread creation/context binding and existence under the current schema;
- current participant admission/removal behavior;
- monotonic participant read cursor;
- Message create/edit/product-delete/privacy-erasure application;
- MessageMedia attach/detach context.

Messaging currently owns no `ThreadStatus`, `MessageStatus`, participant-history lifecycle, message-revision ledger, or moderation-state lifecycle because none is established in supplied evidence.

### Source-of-truth meaning
- `Thread` answers: what conversation exists and what approved context is it bound to?
- `ThreadParticipant` answers: who is currently a participant and where is their read cursor?
- `Message` answers: what message exists and what current edit/delete/erase markers apply?
- `MessageMedia` answers: why is this MediaAsset attached to this Message?

### Events, projections, proof
No Messaging-specific domain event ledger or access-proof ledger is currently modeled. Potential lifecycle events are facts only if later registered. Inbox/unread state may initially be derived from Messaging truth; any later persisted projection remains rebuildable. Generic `AuditEvent` and `AccessAuditLog` remain Audit-owned.

### Policies/invariants owned
Messaging uses owner-specific SH-123 `validateOwnedTargetReference` when validating a cross-Module context target; source existence/relationship facts remain with that owner. Messaging owns context-binding rules, current membership semantics, Messaging action vocabulary, message content/edit/delete rules, read-cursor monotonicity, MessageMedia contextual policy, deleted-vs-erased meaning, safe serialization after external decisions, and safe metadata passed to realtime/Notification.

## 4. Explicit Non-Ownership

| Adjacent owner | Messaging must not own |
| --- | --- |
| Identity & Access | authentication, sessions, MFA/passkeys, recovery, actor resolution |
| Role / Authority | platform/org/participant/ownership/admin permission interpretation |
| Transaction / Order | Order lifecycle, payment/refund/agreement/dispute truth |
| Gig / Demand | Gig/GigResponse/GigAssignment lifecycle |
| Candidate Application & Resume Privacy | CandidateProfile, JobApplication, resume privacy/application lifecycle |
| Job Interview | JobInterview lifecycle/scheduling truth |
| Review / Dispute | Review/Dispute case lifecycle |
| Media / File Access | bytes, MediaAsset lifecycle, upload/scan/storage, grants, signed URLs |
| Healthcare / Regulated Services | healthcare lane/boundary/redaction decision |
| Privacy / Data Erasure | PrivacyRequest, job/target/exemption lifecycle and orchestration |
| Content Moderation & Legal Notice | Report, ModerationCase, ModerationAction, legal notice lifecycle |
| Audit / Event Ledger | AuditEvent, AccessAuditLog |
| Notification | Notification truth, templates, routing, delivery attempts, provider adapters |
| Observability / Ops | public failure/queue/incident capabilities and any future Ops-owned persistence |
| Search / Public Visibility | SearchUpsertEvent, Typesense projection, public query |
| Track Subscription & Entitlement | plan/entitlement/quota/premium truth |

Concrete prohibited duplicates include `OrderChat`, `GigChat`, `ApplicationChat`, `InterviewChat`, `MessageAccessLog`, Messaging-owned privacy jobs, local general permission engines, file-storage/signed-URL services, email/SMS/push SDKs, healthcare policy engines, moderation case tables, local premium flags, and private-message public search indexes.

## 5. Module Architecture Principles

1. Postgres Messaging records are truth; realtime is transport.
2. Context binding must be validated; generic/typed context identifiers may not contradict each other.
3. Messaging references but never mutates source business lifecycles.
4. Messaging owns participant facts; Role / Authority interprets permission.
5. Every protected read/write is server-authorized; RLS is defense in depth and must agree.
6. `deletedAt` is product deletion; `erasedAt` is privacy/legal processing.
7. `MessageMedia` is contextual truth; Media owns file truth/mechanics.
8. Healthcare policy is consumed, not reimplemented.
9. Moderation decides; Messaging executes approved target actions only.
10. Privacy orchestrates; Messaging executes against only Messaging truth.
11. Notification/realtime failure must not roll back committed Message truth.
12. Message bodies are private by default and excluded from generic telemetry, outward Notification payloads, and public Search.
13. Idempotency/locking/queues/audit/crypto/telemetry are shared mechanisms, not local frameworks.
14. Database constraints/transactions handle concurrency; no in-memory lock truth.
15. Unresolved architecture remains unresolved rather than being invented in code.

## 6. Proposed Folder / Code Structure

Follow root code standards if equivalent paths differ.

```text
src/modules/messaging/
├── domain/
│   ├── thread-context-policy.ts
│   ├── participant-policy.ts
│   ├── message-policy.ts
│   ├── read-cursor-policy.ts
│   └── types.ts
├── application/
│   ├── commands/
│   ├── queries/
│   └── services/
├── contracts/
│   ├── public-commands.ts
│   ├── public-queries.ts
│   ├── owner-facts.ts
│   ├── healthcare-view.ts
│   ├── media-context.ts
│   ├── privacy-executor.ts
│   ├── moderation-target.ts
│   └── notification-handoff.ts
├── infrastructure/
│   ├── persistence/
│   └── realtime/
├── presentation/
│   ├── actions/
│   ├── queries/
│   └── components/
├── privacy/
│   ├── enumerate-subject-data.ts
│   ├── execute-privacy-instruction.ts
│   └── export-messaging-data.ts
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── authorization/
    ├── privacy/
    └── e2e/
```

Do not create Messaging-local provider, generic queue, crypto, audit-persistence, search, healthcare-policy, or moderation-case folders. Add `workers/` only when a real Messaging-owned asynchronous responsibility is approved.

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Presentation/UI | inbox, Thread view, composer, read state, safe attachments/redacted states | permission policy, Prisma writes, signed URLs, Notification delivery |
| Server actions/routes | runtime validation, actor resolution call, app-service invocation, result mapping | domain lifecycle, provider SDKs, cross-Module repositories |
| Application commands | Messaging mutation orchestration and dependency calls | another Module's mutation |
| Application queries | authorized/safe read composition | reconstructing source/Healthcare policy |
| Domain policies | context, membership, message, read-cursor local rules | authentication, generic authorization, legal retention, file safety |
| Repositories | Messaging-owned tables only | normal direct cross-domain Prisma access |
| Realtime adapter | publish committed safe deltas | Message storage/permission policy |
| Contracts | stable public interfaces/dependency ports | provider-specific or raw Prisma cross-Module coupling |
| Privacy handlers | Messaging subject inventory/export/disposition | PrivacyRequest lifecycle/legal decision |
| Moderation adapter | target resolution and approved action execution | Report/Case/Action lifecycle |

## 8. Data Model

### `Thread`
Purpose: canonical conversation/context. Key fields: `id`, `contextType`, optional `contextId`, typed FKs, `dataSensitivity`, timestamps, `erasedAt`. Typed FKs to Order/Gig/GigResponse/GigAssignment/JobApplication/JobInterview are each `@unique`, so the current schema permits at most one Thread per typed source record. Concurrency-sensitive SH-113 `ensureContextThread` must converge under these constraints. `erasedAt` is privacy processing evidence, not closure.

### `ThreadParticipant`
Purpose: current membership plus read cursor. Authoritative fields: `threadId`, `userId`, `joinedAt`, `lastReadAt`. Composite PK prevents duplicate membership. `lastReadAt` must advance atomically and never regress. Removing a row loses historical membership evidence; no history model is currently approved.

### `Message`
Purpose: durable message body/current lifecycle markers. Fields: `id`, `threadId`, nullable `senderId`, `content`, `createdAt`, `editedAt`, `deletedAt`, `erasedAt`. Indexes support `(threadId, createdAt)` and `senderId`. Duplicate send, edit/delete/erase races, and pagination ordering are concurrency-sensitive. `content` is non-null, so destructive erasure treatment is decision-gated.

### `MessageMedia`
Purpose: contextual association of Message and MediaAsset. Composite PK `(messageId, mediaId)` prevents duplicate join. Detach must not delete MediaAsset. Privacy may require separate Messaging and Media owner executors.

## 9. Enums, Statuses, and Lifecycles

### `ThreadContextType`
```text
order
gig
gig_response
gig_assignment
job_application
job_interview
direct
support
```
No Booking, Review, or Dispute context may be added without architecture approval and migration.

### Thread
```text
not present
→ ensure/create
→ exists and is usable subject to external gates
→ optional owner-local privacy erasure treatment + erasedAt
```
No close/archive/freeze status exists. Do not invent one.

### Participant
```text
not participant
→ addThreadParticipant
→ current participant
   ↳ lastReadAt monotonically advances
→ removeThreadParticipant (current-state semantics only)
→ no current row
```
No `leftAt`, removal actor/reason, pending invitation, or historical status exists.

### Message
```text
created
→ edited* via editedAt
→ product-deleted via deletedAt
or
→ privacy-erased via approved owner-local treatment + erasedAt
```
No revision ledger or undelete/reopen semantics are currently approved. Erased content must not be re-exposed or edited.

### MessageMedia
```text
MediaAsset ready + authorized context
→ MessageMedia created
→ access requires Messaging + Media decisions
→ MessageMedia detached
```

## 10. Commands

| Command | Purpose / key rules | Writes | Shared/public dependencies | Idempotency/failure |
| --- | --- | --- | --- | --- |
| SH-113 `ensureContextThread` | create/return current-schema single Thread for typed source context; validate owner facts and context consistency | Thread + initial participants | actor, Role, SH-003 `queryOwnerFacts` (Proposed ruling), idempotency, DB lock/constraint | replay same semantic result; unique-race fetch winner; context mismatch/denial fail |
| `createDirectThread` | create direct conversation | Thread + participants | actor, Role | **decision-gated** participant-set identity/dedupe |
| `createSupportThread` | create support conversation | Thread + participants | actor, Role | **decision-gated** support-case semantics |
| `addThreadParticipant` | add current membership | ThreadParticipant | actor, Role, owner facts, idempotency | duplicate add returns current state |
| `removeThreadParticipant` | remove current membership | delete ThreadParticipant | actor, Role | only where current-state deletion is acceptable; no history claim |
| `sendMessage` | persist authorized message; attachments optional after Media approval | Message + optional MessageMedia | actor, Role, idempotency, Media, realtime, Notification | duplicate send one Message; downstream realtime/Notification failure does not roll back |
| `editMessage` | change current content, set `editedAt` | Message | actor, Role | reject erased/stale/forbidden state |
| `deleteMessage` | product-delete/hide | `deletedAt` | actor, Role | never substitute for erasure/moderation case truth |
| `markThreadRead` | advance read cursor | `lastReadAt` | actor, Role | atomic max/current replay |
| `attachMediaToMessage` | attach ready asset context | MessageMedia | Role, Media, idempotency | composite-key retry-safe; no file mutation |
| `detachMediaFromMessage` | remove contextual join | MessageMedia delete | Role | no MediaAsset deletion |
| `reportMessageOrThread` | submit target to Moderation | none locally | SH-101 `submitModerationReport` | Moderation owns Report/Case |
| SH-103 `executeModerationDecision` | execute approved target action | only supported Messaging fields | Moderation decision, audit if required | unsupported action fails explicitly |
| SH-095 `executePrivacyInstruction` | execute Privacy-directed owner-local disposition | Messaging records only | Privacy protocol, idempotency, audit if required | returns typed owner result; never completes PrivacyRequest |

## 11. Queries / Decisions

| Query | Consumers | Result kind | Consumer must not infer |
| --- | --- | --- | --- |
| `resolveThreadContext` | source Modules, UI, Privacy, Moderation | source/context truth | source lifecycle or permission |
| `getThreadParticipantFacts` | Role, Media, Healthcare, Admin | source/context facts | authorization decision |
| SH-026 `authorizeContextualResourceAccess` (Messaging owner implementation) | Media | contextual allow/deny and safe evidence bound to actor/Thread/Message/MediaAsset/action | Media readiness, grants, TTL, or signed access |
| `listThreadsForUser` | inbox UI | source truth + derived summary | source business lifecycle |
| `getThread` | UI/admin/support | full/redacted/metadata-only/denied view | Healthcare policy internals |
| `listThreadMessages` | UI/protected consumers | paginated source-truth view | edit history that does not exist |
| `listThreadParticipants` | authorized consumers | current participants | historical membership |
| `getUnreadThreadState` | inbox UI | derived count/boolean | Notification unread state |
| SH-096 `enumerateSubjectData` | Privacy | owner target evidence | final legal disposition |
| SH-097 `evaluateRetentionRequirement` | Privacy | owner retention facts under SH-097 | exemption creation or Privacy workflow completion |
| `exportMessagingSubjectData` | Privacy | owner export section | global export completion |

Stable view/error reasons should include `allowed`, `not_participant`, `authorization_denied`, `sensitive_redacted`, `sensitive_blocked`, `erased`, `not_found`, `context_mismatch`, and dependency errors as appropriate.

## 12. Public Module Interface

### Public commands
```text
ensureContextThread
createDirectThread            [decision-gated]
createSupportThread           [decision-gated]
addThreadParticipant
removeThreadParticipant       [current-state only]
sendMessage
editMessage
deleteMessage
markThreadRead
attachMediaToMessage
detachMediaFromMessage
reportMessageOrThread
executeModerationDecision     [approved actions only]
executePrivacyInstruction
```

### Public queries
```text
resolveThreadContext
getThreadParticipantFacts
authorizeContextualResourceAccess [SH-026 owner implementation]
listThreadsForUser
getThread
listThreadMessages
listThreadParticipants
getUnreadThreadState
enumerateSubjectData
evaluateRetentionRequirement
exportMessagingSubjectData
```

### Emitted events
No event is binding until registered. If approved, likely facts are `messaging.thread.created`, `messaging.participant.added/removed`, `messaging.message.sent/edited/deleted`. Payloads must be versioned/minimized and omit private message body by default.

### Privacy executor
Messaging implements SH-096 `enumerateSubjectData`, SH-097 `evaluateRetentionRequirement`, SH-095 `executePrivacyInstruction`, and an export serializer compatible with Privacy's protocol.

### Provider-facing interfaces
None. Supabase Realtime is consumed through the platform realtime adapter; Messaging owns no external communication/storage/search provider lifecycle.

## 13. Inbound Dependencies

| Owning Module/capability | Interface consumed | Why required | Minimum information | May block? | Messaging must not copy |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | trusted actor context | actor/system ID, session/assurance context | yes | auth/session helpers |
| Role / Authority | SH-002 `authorizeResourceAction` | permission interpretation | action + Messaging/source relationship facts | yes | permission matrix/engine |
| Source context owner | owner-specific SH-003 `queryOwnerFacts` (Proposed ruling) DTO | validate context/participants | canonical ID, existence, relationship/participant facts | yes | source repositories/lifecycle reconstruction |
| Media / File Access | ready-asset + contextual access/signed-access interfaces | attachment safety/access | MediaAsset ID, readiness/access result | yes for attach/access | upload/scan/storage/signed URLs |
| Healthcare / Regulated Services | healthcare message/thread view decision | sensitive view composition | target/sensitivity/viewer purpose | yes for sensitive reads | healthcare policy/boundary truth |
| Privacy / Data Erasure | privacy executor protocol | receive authoritative disposition | target/action/retention/idempotency/correlation | yes for destructive action | PrivacyRequest/job/exemption lifecycle |
| Content Moderation & Legal Notice | report + decision interfaces | route report/execute approved action | target/evidence/action/reason | yes for enforcement | report/case/action truth |
| Audit / Event Ledger | SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess` | generic/sensitive proof | actor/action/target/decision/minimized metadata | policy-dependent | local audit tables |
| Notification | SH-041 `requestNotification` | alert after committed Message | recipients, safe source IDs/template/action route | no for Message truth | Notification/provider state |
| Observability / Ops | request context, telemetry sanitation, failure recording | safe diagnostics | correlation IDs/safe metadata | no | Ops business records |
| Platform realtime | SH-071 `publishRealtimeChange` (Proposed ruling) | near-realtime client updates | committed delta + audience | no | realtime storage/source truth |

Current typed source contexts: Order, Gig, GigResponse, GigAssignment, JobApplication, JobInterview. `direct` and `support` are Messaging contexts without typed source FKs.

## 14. Outbound Consumers and Effects

| Consumer | Consumes | Allowed effect | Prohibited coupling |
| --- | --- | --- | --- |
| Transaction / Order | Thread/context conversation contract | ensure/retrieve Thread | direct Messaging-row mutation |
| Gig / Demand | Gig/GigResponse/GigAssignment conversations | ensure/retrieve/use Messaging API | custom gig chat tables |
| Candidate Application & Resume Privacy | JobApplication conversation | ensure/retrieve/message | candidate-message persistence outside Messaging |
| Job Interview | interview conversation | ensure/retrieve/message | using interview event ledger as Message truth |
| Review / Dispute | approved Order-linked conversation | reuse approved Thread | inventing Dispute context |
| Role / Authority | participant/context facts | return permission decision | mutate ThreadParticipant |
| Media / File Access | Messaging SH-026 contextual decision | apply independent file readiness/grant/TTL checks and issue signed access | reconstruct Messaging participant policy or own MessageMedia lifecycle |
| Healthcare | target/sensitivity facts | return view decision | mutate Message/Thread |
| Privacy | inventory/executor | orchestrate disposition | direct Prisma mutation |
| Moderation | safe target/executor | case/action lifecycle and approved request | treat deletedAt as moderation truth |
| Notification | safe Message intent | create/deliver alert | read Message body as notification repository |
| Admin/support | authorized/redacted view | read permitted content | broad bypass |

Messaging has no public Search projection. A committed Message may request Notification after commit using only safe IDs, recipient intent, route, sensitivity, priority/template metadata, and correlation/idempotency. Message body, PHI, resume text, tax/financial data, contract text, signed URLs, object keys, and secrets are prohibited.

## 15. Canonical Shared Operations Used

**Shared Operations status:** references marked **Proposed ruling** are planning dependencies only, not approval for shared schema/API commitment or a generic service. Independently justified owner-specific interfaces do not approve a proposed shared operation globally. Realtime remains post-commit, authorized, and rebuildable; Moderation integration consumes approved contracts. Canonical metadata and reusable boundaries remain controlled by the Shared Operations registry.

Use the existing SH IDs and canonical metadata in `context/shared/shared-operations.md`; local usage does not redefine reusable boundaries.

| Canonical operation | Classification | Owner | Messaging use / invocation | Local policy retained | Expected result | Prohibited duplicates | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Platform capability | Identity & Access | every protected entrypoint | Messaging action/context | trusted actor | `chatAuth`, `messagingSession` | Confirmed |
| SH-002 `authorizeResourceAction` | Cross-cutting capability | Role / Authority | before protected read/write | Messaging action vocabulary + facts | allow/deny/reasons | `threadPermissions`, local auth engine | Confirmed |
| SH-003 `queryOwnerFacts` (Proposed ruling) | Shared contract; separate implementations | Each source Module | context/participant validation | exact facts needed | narrow owner DTO | cross-domain repository | Proposed ruling |
| SH-044 `executeIdempotentCommand` | Platform primitive | Platform application infrastructure | retryable commands | semantic key/fingerprint/replay | claim/replay/conflict | local idempotency table/cache | Confirmed |
| SH-071 `publishRealtimeChange` (Proposed ruling) | Infrastructure adapter | Platform realtime adapter; Messaging is primary consumer | after committed safe change | audience/payload | publication ack/failure | chat socket store | Proposed ruling |
| SH-041 `requestNotification` | Platform notification capability | Notification | after committed Message | recipients + safe source metadata | accepted/rejected | email/SMS/push service | Confirmed |
| SH-090 `attachValidatedMedia` | Shared contract; separate contextual truth | Contextual domain Module; Media owns asset truth | attachment creation | Thread/Message attachment context | validated Media ref | upload/storage service | Confirmed |
| SH-026 `authorizeContextualResourceAccess` | Shared contract; separate implementations | Relevant context owner | attachment view/download composition | actor/Thread/Message/MediaAsset/action-bound contextual decision, composed from owner facts and applicable external gates | allow/deny/evidence | local signed-url policy | Confirmed |
| SH-030 `recordSensitiveAccess` | Cross-cutting capability | Audit / Event Ledger | sensitive/admin reads | target/action/sensitivity/purpose | audit ack | MessageAccessLog | Confirmed |
| SH-029 `appendAuditEvent` | Platform audit capability | Audit / Event Ledger | important participant/privacy/moderation actions | sanitized context | audit ack | chat audit table | Confirmed |
| SH-032 `createRequestContext` | Platform primitive | Observability / platform infrastructure | entrypoint/post-commit correlation | safe labels | context | local correlation system | Confirmed |
| SH-034 `sanitizeTelemetryMetadata` | Cross-cutting capability | Observability / Ops and Audit payload policy | before logs/errors/audit metadata | Messaging-sensitive fields | safe metadata | local redactor framework | Confirmed |
| SH-037 `recordIntegrationFailure` | Cross-cutting capability | Observability / Ops | realtime/Notification/Media dependency failure | Messaging truth unchanged | failure ref | local failure table | Confirmed |
| SH-046 `publishDomainEvent` | Platform primitive | Platform event/outbox infrastructure | only if Messaging event approved | event meaning/version/payload | durable outbox result | ad hoc event bus | Confirmed |
| SH-045 `deduplicateDomainEvent` | Platform primitive | Platform event infrastructure; consumer owns inbox | future consumers | handler effect | claim/replay | custom inbox framework | Confirmed |
| SH-096 `enumerateSubjectData` | Cross-cutting protocol | Each data-owning Module through Privacy-defined interface | Privacy inventory | Messaging targets/dispositions | cursorable descriptors | global DB crawler | Confirmed |
| SH-097 `evaluateRetentionRequirement` | Cross-cutting protocol | Data owner supplies facts; Privacy records exemption | privacy planning | Messaging relational facts only | retention facts | local exemption table | Confirmed |
| SH-095 `executePrivacyInstruction` | Cross-cutting protocol | Privacy orchestrates; each data owner executes | privacy target execution | exact owner-local field treatment | typed disposition | local Privacy workflow | Confirmed |
| SH-101 `submitModerationReport` | Module public interface | Content Moderation & Legal Notice | report action | target/evidence context | Report ref | local report/case | Confirmed |
| SH-103 `executeModerationDecision` | Cross-cutting protocol | Moderation owns decision; each target owner executes | approved action | target-to-owner mutation map | acknowledgement | Moderation direct DB write | Confirmed |

Conditional only when an approved policy applies: SH-014 `requireStepUpForSensitiveAction` and SH-011 `evaluateComplianceHold`. They are not default Messaging gates.

## 16. Module-Internal Operations

| Operation | Purpose | Input → output | Truth affected | Why local |
| --- | --- | --- | --- | --- |
| `validateThreadContextBinding` | ensure generic/typed context consistency | context fields → valid/error | none | encodes Thread semantics |
| `resolveInitialThreadParticipants` | map owner facts to proposed members | owner facts → User IDs | none until command | Messaging admission policy |
| `serializeThreadForViewer` | apply external decisions to Thread result | Thread + decisions → safe DTO | none | owner serialization |
| `serializeMessageForViewer` | hide deleted/erased/redacted content | Message + view decision → safe DTO | none | Message presentation semantics |
| `calculateUnreadState` | derive unread | cursor + messages → count/boolean | none | derived Messaging truth |
| `advanceReadCursor` | atomic monotonic cursor | participant + requested cursor → persisted max | ThreadParticipant | Messaging cursor semantics |
| `buildNewMessageNotificationIntent` | create body-free alert intent | Message/Thread IDs + recipients → safe request | none | Messaging knows source meaning |
| `buildRealtimeConversationDelta` | create minimized realtime payload | committed change → delta | none | Messaging owns safe conversation delta |
| `mapPrivacyInstructionToMessagingMutation` | owner-local privacy translation | target/action/retention → mutation plan | Messaging records | Privacy cannot know relational details |
| `mapModerationDecisionToMessagingAction` | owner-local enforcement translation | action envelope → supported action/unsupported | Messaging target | separate decision from execution |

## 17. Shared Mechanism / Separate Truth Rules

- Role authorization mechanism is shared; `ThreadParticipant` remains Messaging truth.
- Audit append is shared; Thread/Message are not AuditEvent/AccessAuditLog.
- Realtime transport is shared; Message remains Postgres truth.
- Media grants/signed URLs are Media truth; MessageMedia remains Messaging truth.
- Privacy orchestrates request/job/target; Messaging owns owner-local disposition.
- Moderation owns Report/Case/Action; Messaging owns target truth and execution mapping.
- Idempotency/locking/outbox mechanics are shared; Thread/Message lifecycle remains local.
- Any inbox/unread performance projection is rebuildable and never a second lifecycle owner.

## 18. Authentication and Authorization

All interactive Messaging operations require SH-001 `resolveAuthenticatedActor`; trusted workers use the root system-actor contract, never a bypass boolean. SH-002 `authorizeResourceAction` interprets named actions using Messaging-supplied facts such as participant state, Thread context, Message sender relation, and source-owner relationship facts.

Ordinary Thread read/write requires current participation unless separately authorized admin/support policy applies. Organization membership is never copied into Messaging; Hiring owner facts and Role interpretation are used. Admin/support access must compose Role authorization, Healthcare decision where applicable, and SH-030 `recordSensitiveAccess` where policy requires. No general Messaging step-up requirement is approved; step-up is added only to a specifically approved sensitive action.

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Owner | Operation | Gated Messaging action | Local composition/result |
| --- | --- | --- | --- | --- |
| authority | Role / Authority | SH-002 `authorizeResourceAction` | all protected reads/writes | supply facts → allow/deny |
| healthcare view | Healthcare | approved view decision | sensitive Thread/Message views | apply full/redact/metadata/block |
| file readiness/access | Media | ready/access interface | attach/view MessageMedia | require both context + Media decision |
| privacy disposition | Privacy | executor envelope | erase/anonymize/retain/export | execute only local mutation, return typed result |
| moderation enforcement | Moderation | approved action | target restriction/delete where mapped | execute supported action or fail unsupported |
| ComplianceHold | Hold owner | SH-011 `evaluateComplianceHold` only when approved | specific action only | no local blocked boolean |

No Messaging entitlement/premium/quota gate is currently confirmed. Do not call SH-005 `resolveEntitlement` unless later architecture explicitly makes a Messaging action track-dependent.

## 20. Provider Integrations

Messaging owns no external provider lifecycle. Supabase Realtime may be consumed through the approved platform adapter. Email/SMS/Web Push/FCM/OneSignal/WonderPush, R2/S3, Typesense, Stripe, Cronofy, and Video provider clients/webhooks do not belong here.

## 21. Events and Outbox

No Messaging domain event is required for the first core slices. If approved later, event names should be versioned facts such as `messaging.thread.created.v1`, `messaging.participant.added.v1`, `messaging.message.sent.v1`, etc. Payloads include stable IDs, aggregate/version/correlation metadata, timestamp, source/context IDs, and omit Message body by default.

Reliable events use the canonical transactional outbox. Consumers use canonical dedupe. Events describe facts and must not encode disguised commands such as “send email” or “change Order status.”

## 22. Background Jobs / Scheduled Work

No Module-owned worker is required for core Messaging. Realtime is post-commit transport; Notification workers are Notification-owned; Privacy workers are Privacy-owned and invoke Messaging; Media processing is Media-owned. A future Messaging retention/backfill/projection worker requires an approved owner-local need and must use shared queue/retry/telemetry primitives.

## 23. Concurrency and Idempotency

Prevent races for duplicate context Thread creation, duplicate Message sends, duplicate membership/MessageMedia joins, read-cursor regression, edit/delete/erase conflicts, and participant removal racing with send/read.

Suggested semantic keys:

```text
thread:{contextType}:{contextId}
thread:{threadId}
message:{messageId}
thread:{threadId}:participant:{userId}
message:{messageId}:media:{mediaId}
```

These are semantic scopes, not permission to implement in-memory locks. Use DB unique constraints, transactions, optimistic/CAS or approved aggregate locking. SH-113 `ensureContextThread` transactionally claims idempotency/create/fetch-winner/initial participants. `sendMessage` claims idempotency and writes Message plus owner-local joins; realtime/Notification are post-commit. `markThreadRead` is atomic max. Privacy execution revalidates current target in transaction.

Same idempotency key + same semantic fingerprint returns original result; same key + different fingerprint returns deterministic conflict. Replay must not duplicate downstream semantic effects.

## 24. Media / Storage

`MessageMedia` means “this MediaAsset is attached to this Message.” Messaging owns that business attachment meaning. Media owns upload session, binary/MIME validation, malware scan, processing/EXIF handling, object storage, MediaAsset readiness/frozen/erased state, grants, and signed URLs.

```text
Media upload/processing
→ ready MediaAsset
→ Messaging authorizes Thread/Message context
→ MessageMedia join
→ viewer request
→ Messaging returns actor/Thread/Message/MediaAsset/action-bound SH-026 decision
→ Media requestMediaAccess applies its own gates and issues short-lived access
```

No permanent private URL/object key belongs in Messaging. Sensitive access uses SH-030 `recordSensitiveAccess` when policy requires; no local attachment-access ledger is created.

For MessageMedia access, Messaging exposes its owner-specific SH-026 `authorizeContextualResourceAccess` decision bound to the actor, Thread, Message, MediaAsset, and requested action. It returns the contextual allow/deny decision and safe evidence; `ThreadParticipant` or `MessageMedia` facts alone are not authorization. Media consumes that decision through `requestMediaAccess`, independently applies MediaAsset readiness, safety/freeze/erasure, grant, and TTL rules, and owns downstream SH-087 `issueSignedMediaUrl`. Media must not reconstruct Messaging participant/access policy; Messaging must not issue signed URLs or call SH-087 directly.

## 25. Search / Projection

Messaging owns no public Search projection. Thread and Message bodies are private by default. No Typesense client, `SearchUpsertEvent`, or public indexing path belongs in Messaging. If private conversation search is ever approved, it requires separate access-scoped architecture and must not be inferred from current public Search infrastructure.

Inbox summaries and unread state are Messaging-local derived views. A future persisted projection must remain rebuildable from Messaging truth.

## 26. Notification

A committed Message may trigger a Notification request. Messaging supplies only source meaning and safe metadata: Thread ID, Message ID, safe sender display reference if approved, recipient IDs/target contract, safe authenticated action route, sensitivity, priority, template key/version, correlation/idempotency.

Messaging must never send private Message body, PHI, resume text, financial/tax data, contract text, signed URLs, storage keys, or provider-specific payloads to Notification. Message commit is authoritative; Notification failure is downstream and must not roll back Messaging truth.

## 27. Audit and Sensitive Access

Message timestamps/lifecycle markers are Messaging truth, not an audit ledger. Audit / Event Ledger owns generic `AuditEvent` and `AccessAuditLog`.

Messaging may call:

- SH-029 `appendAuditEvent` for important participant administration, moderation execution, privacy execution, or other actions required by root policy;
- SH-030 `recordSensitiveAccess` for protected Thread/Message reads and admin/support access according to approved policy.

No Messaging-specific `MessageAccessLog` or `ThreadOpenLog` is approved. If policy requires audit proof before sensitive data can be returned, audit failure must fail closed. Do not infer that every ordinary participant read requires append-only audit.

## 28. Privacy and Retention

### Subject-data inventory
Messaging can hold subject data in Thread context/participant metadata, Message sender/content/timestamps, MessageMedia association data, and direct/support context metadata.

### Privacy interfaces
```text
enumerateSubjectData
evaluateRetentionRequirement
executePrivacyInstruction
exportMessagingSubjectData
```

Privacy / Data Erasure owns requester verification, `PrivacyRequest`, erasure job/target lifecycle, retention exemptions, aggregate completion, and export-bundle lifecycle.

Messaging and Notification participate through SH-096 `enumerateSubjectData`, expose owner-side SH-097 `evaluateRetentionRequirement`, and execute approved dispositions through SH-095 `executePrivacyInstruction`. Retention evaluation returns required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference under approved policy. Privacy owns `DataRetentionExemption` creation and final workflow completion; it must not directly rewrite CL-07 tables.

**CL-07-R005 — unresolved Privacy target mapping:** inventory must cover `ThreadParticipant`, `MessageMedia`, `NotificationSubscription`, `NotificationDelivery`, and `NotificationSubscriptionEvent` as well as Thread, Message, and Notification. How those child records become `DataErasureTarget` entries remains a Privacy-owned architecture decision. Do not silently omit them, invent enum values, select an ad hoc untyped `other` mapping, or assume parent erasure determines every child disposition. Destructive workflows depending on this mapping remain gated until it is approved.

### Owner-local dispositions
Messaging may, only under approved Privacy instruction:

- erase/anonymize Message content;
- null/pseudonymize sender reference where approved;
- erase/anonymize Thread metadata;
- detach/remove participant identity where relationally safe and approved;
- detach MessageMedia joins;
- retain records under authoritative retention instruction;
- export subject-owned Messaging data.

`Message.content` is currently non-null. The exact production erasure treatment must be approved before destructive behavior is enabled. An `erasedAt` timestamp alone is not sufficient if personal content remains. Messaging supplies retention facts but does not invent legal retention periods. Media/provider resources are handled by their respective owner executors.

## 29. Observability

Emit structured operational logs through SH-033 `writeStructuredLog`. Safe structured dimensions include operation name, pseudonymous Thread/Message IDs where root policy permits, context type, safe decision/error code, latency, dependency, request/correlation ID, and idempotency replay indicator.

Never log Message body, PHI, private attachment URL/object key, resume text, financial/tax data, auth secrets, or provider tokens.

Realtime/Notification/Media dependency failures use Observability / Ops SH-037 `recordIntegrationFailure` and other approved telemetry interfaces; their persistence is not assumed and they do not change Message/Thread lifecycle.

Recommended metrics: Thread ensure latency/conflict rate, Message send success/error latency, idempotency replay/conflict rate, inbox/message query latency, realtime publish failures, Notification handoff failures, authorization denials, privacy executor outcomes, moderation executor failures.

**CL-07-R007 — Observability persistence boundary:** CL-07 consumes approved public capabilities for failure recording, queue telemetry, health, structured logging, metrics, and exception capture. `IntegrationFailure`, `QueueJob`, `OpsIncident`, and `SystemEvent` are not current Prisma models. CL-09 owns its unresolved persistence/status design. CL-07 must not create local substitutes or couple Messaging/Notification business status to any future operational record.

## 30. Security Boundaries

1. Runtime-validate all public inputs.
2. Resolve actor server-side; never trust client-supplied actor IDs.
3. Authorize every protected read/write server-side.
4. Keep RLS aligned with Role / Authority and test both.
5. Treat Message body as sensitive UGC; exclude it from logs/analytics/Notification/public Search.
6. Enforce server-owned content limits and validation.
7. Use Media validation/access for attachments; never trust client MIME/file metadata alone.
8. Never persist permanent private file URLs in Messaging.
9. Re-check authorization at mutation/read time, not just when UI loaded.
10. Fail closed for sensitive admin/support content when required Healthcare/audit decision is unavailable.
11. Use root/shared rate-limit/abuse/security primitives; do not build a Messaging security framework.
12. Store no provider credentials or webhook secrets.

## 31. Error / Decision Result Pattern

Stable public categories should include:

```text
ok
validation_error
authentication_required
authorization_denied
not_found
context_mismatch
unsupported_context
already_exists
idempotency_conflict
conflict
stale_state
sensitive_redacted
sensitive_blocked
media_not_ready
media_access_denied
privacy_restricted
moderation_restricted
dependency_unavailable
retryable_failure
terminal_failure
unsupported_action
```

Decision-like results should use a stable envelope such as `result`, `reasonCode`, `safeMessage`, optional minimized `evidenceRefs`, `evaluatedAt`, optional owner-supplied `policyVersion`, and `retryable`. Never leak raw Prisma/provider errors to consumers.

## 32. Testing Architecture

Required suites:

- **Domain unit:** context binding, participant semantics, message validation/edit/delete, deleted-vs-erased serialization, read-cursor monotonicity, safe Notification intent, safe realtime delta.
- **Lifecycle:** Thread ensure, participant current-state transitions, Message create/edit/delete/erase conflicts, MessageMedia attach/detach, privacy executor results.
- **Public contracts:** source owner facts, Role, Media, Healthcare, Notification, Privacy, Moderation.
- **Database/integration:** one Thread per typed context, mismatch rejection, composite-key behavior, stable pagination, transaction rollback.
- **Authorization/RLS:** participant allowed, unrelated User denied, removed User denied, admin/support does not bypass external policy, service/RLS agreement.
- **Compliance:** Healthcare allow/redact/block, sensitive audit critical path, moderation boundaries, deletedAt vs erasedAt.
- **Concurrency/idempotency:** racing Thread ensure, duplicate send, duplicate attach, stale cursor, edit/delete/erase races.
- **Privacy:** subject enumeration, export, idempotent erase/anonymize/retain where approved, Messaging never completes PrivacyRequest.
- **Realtime adapter:** safe audience/payload, reconnect/refetch behavior.
- **E2E:** source context → Thread → two participants → Message → third-user denial → read cursor → safe Notification handoff → authorized attachment.

No external provider adapter tests are required in Messaging beyond realtime adapter contract tests.

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Thread`, `ThreadParticipant`, `Message`, and contextual `MessageMedia` are Messaging-owned truth.
2. Role / Authority interprets permission; it does not mutate `ThreadParticipant`.
3. Foreign keys do not authorize Messaging to mutate source business lifecycles.
4. Business Modules use Messaging public interfaces; they do not create custom chat tables/direct Messaging writes as normal application behavior.
5. `ThreadContextType` may contain only approved values; do not invent Booking/Review/Dispute contexts.
6. Typed context fields and generic context identifiers may not contradict one another.
7. Current typed unique constraints mean at most one Thread per typed source record until approved migration changes it.
8. Realtime is transport, never Message truth.
9. Only authorized participants or separately approved admin/support actors may access protected conversation data.
10. RLS and application authorization must agree.
11. `lastReadAt` never moves backward.
12. Duplicate send retries must not create duplicate Messages.
13. `deletedAt` is product deletion; `erasedAt` is privacy/legal processing.
14. Product deletion never completes a privacy request.
15. `erasedAt` alone is not sufficient if personal content remains.
16. Attachments must pass Media readiness/access; Messaging stores no bytes or permanent private URLs.
17. Detaching MessageMedia does not delete MediaAsset.
18. Healthcare policy remains Healthcare-owned.
19. Moderation Report/Case/Action truth remains Moderation-owned.
20. PrivacyRequest/DataErasureJob/DataRetentionExemption remain Privacy-owned.
21. AuditEvent/AccessAuditLog remain Audit-owned.
22. Notification delivery remains Notification-owned; Message commit does not depend transactionally on provider delivery.
23. Private Message body/PHI/resume/financial/tax/contract content and secrets do not enter generic telemetry, outward Notification payloads, or public Search.
24. Messaging owns no email/SMS/push/storage/search/payment/calendar/video provider client.
25. Shared idempotency/locking/audit/crypto/queue/telemetry/realtime primitives are consumed, not copied.
26. No local premium/entitlement boolean or quota is introduced without approved Track policy.
27. Moderation restriction is not represented by `deletedAt`/`erasedAt` unless the approved action specifically requires it.
28. Unresolved direct/support, participant-history, edit-history, retention, moderation-state, and erasure questions are not silently decided in code.

## 34. Prohibited Duplicate Implementations

Prohibited names or equivalents include:

```text
chat-auth.ts
messaging-session.ts
current-user-for-chat.ts
thread-permissions.ts
chat-authorization.ts
message-access-log.ts
thread-view-log.ts
messaging-audit-repository.ts
message-upload.ts
chat-file-service.ts
message-signed-url.ts
attachment-download-service.ts
chat-storage.ts
message-email.service.ts
chat-push.ts
sms-new-message.ts
message-notifier-provider.ts
gdpr-chat-service.ts
message-erasure-worker.ts
message-report-case.ts
chat-moderation-case.ts
hipaa-chat-policy.ts
messaging-entitlement.ts
premium-chat.ts
chat-typesense.ts
message-search-indexer.ts
thread-mutex.ts
chat-retry-cache.ts
```

A similarly named file is acceptable only when its scope is genuinely Messaging-local and does not duplicate external/shared ownership; e.g. a safe serializer may *apply* a Healthcare decision but may not decide Healthcare policy.

## 35. Unresolved Decisions

1. May a typed source record ever have more than one Thread?
2. Should generic `contextId` coexist long-term with typed FKs, and what DB invariant enforces consistency?
3. Does Review/Dispute reuse Order Thread or need a future `dispute` context?
4. Does Booking reuse Order Thread or need a future `booking` context?
5. How are direct Thread uniqueness and group-direct identity defined?
6. Is `support` sufficient as Thread context, or must it link to a separate support case?
7. Is deleting `ThreadParticipant` sufficient, or is historical removal/revocation proof required?
8. Is participant admission immediate or does invitation/pending state exist?
9. Does Thread need close/archive/freeze lifecycle?
10. How are moderation restrictions persisted if current fields are insufficient?
11. What exact erasure treatment removes non-null `Message.content`?
12. When may `senderId` be nulled/pseudonymized?
13. Is immutable message edit history required?
14. What canonical idempotency storage/claim implementation is used in production?
15. Is `(createdAt, id)` sufficient ordering or is per-Thread sequence required?
16. Which reads/actions require `AccessAuditLog`?
17. What retention/anonymization policies apply to ordinary, disputed, healthcare, support, and legally preserved conversations?
18. Is Healthcare decision Thread-level, Message-level, or inherited?
19. Which Messaging domain events are registered/versioned/outbox-backed?
20. What exact realtime audience/channel authorization scheme is canonical?

## 36. Architecture Decision Summary

### Binding
- Messaging owns Thread, ThreadContextType, ThreadParticipant, Message, and contextual MessageMedia.
- Role owns permission interpretation; Messaging exposes participant/context facts.
- Media owns file truth and signed access; Messaging owns attachment context.
- Source Modules own Order/Gig/Application/Interview lifecycles and use Messaging public interfaces.
- Healthcare owns sensitive-view policy; Messaging applies it.
- Privacy owns request/job/retention orchestration; Messaging exposes owner-local inventory/export/executor.
- Moderation owns report/case/action truth; Messaging resolves targets and executes approved actions only.
- Audit owns generic and sensitive-access ledgers.
- Notification owns alert/delivery truth; Message commits before Notification handoff.
- Realtime is transport, not truth.
- No public private-message Search projection exists by default.
- Canonical shared operations are reused, not duplicated.

### Proposed rulings carried forward
- Source Modules should call SH-113 `ensureContextThread`, not insert Thread rows directly.
- `getThreadParticipantFacts` is the stable owner-facts boundary for Role and contextual consumers.
- Initial unread state should derive from `lastReadAt` and Message timestamps.
- Stable pagination should use `(createdAt, id)` unless a later sequence ruling supersedes it.

### Decision-gated
Direct/support deduplication, participant history, Thread status, moderation restriction persistence, destructive erasure mechanics, edit revisions, retention periods, and new context enum values.

## 37. Coding-Agent Usage

Before implementing Messaging, read:

1. root project overview;
2. root architecture;
3. code standards;
4. Canonical Shared Operations Registry;
5. CL-07 architecture;
6. CL-07 build plan;
7. this Module architecture;
8. this Module implementation plan;
9. relevant dependency public-interface sections (Identity, Role, source context owner, Media, Healthcare, Privacy, Moderation, Audit, Notification, Observability);
10. current progress tracker.

Before each feature, confirm the prior exit gate. If implementation reveals a binding architectural change, update architecture first; do not hide it only in code or progress notes.
