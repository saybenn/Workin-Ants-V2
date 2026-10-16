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

## WA-R057 — Privacy owner inventory and private export handoff

Classification: AI_RESOLVED_WITH_TRADEOFF; external activation and implementation qualification gates below remain explicit. This ruling supersedes conflicting historical proposals only for its stated scope.

Each owner implements WA-R020 versioned enumerateSubjectData/evaluateRetentionRequirement/executePrivacyInstruction descriptors. Inventory is explicit, paginated with completion evidence and stable target/version identity; no generic other target or assumed database cascade can count as coverage. Messaging covers Thread, participant current state/history, Message/revisions/restrictions and MessageMedia joins. Notification covers Notification/interaction evidence, NotificationSubscription/credential generations, Delivery attempts and SubscriptionEvent. Location covers FuzzyLocationCache, reveal/revocation evidence and its provider references; exact source facts remain inventoried by their source owner. Restricted proof is accounted even when excluded from requester disclosure. Owner field/action matrices must identify erase, minimize, retain, export or restrict disposition with policy basis and executor receipts before destructive activation.

Privacy owns an immutable export manifest: subject/request/job/generation, owner contribution IDs and versions, authorized field scope, safely stated exclusions with disposition evidence, assembly completion, byte hash/algorithm, creation time and actor/correlation. Exact Location subject data may be included only under approved access policy after removing other parties' data; encryption keys, provider credentials and access tokens are never export content. Record opaque key-version/storage evidence where required, never keys. A complete manifest describes actual serialized bytes, not promised future contributions.

Use Media's WA-R050 createMediaUploadSession→bounded upload→completeMediaUpload→getMediaUploadStatus/getMediaReadiness protocol, with Privacy job/bundle revision as semantic key and purpose-bound private artifact authorization. Same key and bytes replay; changed bytes require a new revision or conflict. Upload acknowledgment never means ready. Require exact immutable ready Media version, matching hash/size and completed manifest before bundle ready. Bind through an explicit Privacy-owned MediaAsset/version reference, not polymorphic ownership. Failed scan/partial assembly keeps download unavailable. Terminal upload retry uses a linked Media attempt per WA-R050 while preserving bundle-generation lineage.

At download, Privacy rechecks requester/action/scope and current generation; Media rechecks asset safety/revocation and issues bounded access through SH-127. Commit required access evidence before protected disclosure. Superseded/expired/revoked generations cannot receive fresh access even if cleanup worker is late. Retain prior manifest/status evidence under approved retention while deleting bytes through Media's executor when authorized. No stored public URL, direct storage SDK or convenience export endpoint may bypass owner gates. Audit exports use the same Media mechanism but an Audit-owned manifest; this ruling does not transfer Audit export ownership.

Legal retention/exemption duration, backup-expiry representation and final retained shell require approved external policy. Location's geocoder/account/region/purpose and key lifecycle qualification remain external activation gates; consumers cannot choose their own geocoder or crypto. Verify omitted child inventory, partial serializer, hash mismatch, scan failure, changed-byte retry, stale generation access, retained shared Media references and provider-deletion uncertainty. Concrete schema, executor field matrices and bilateral fixtures remain implementation qualification, not unresolved architecture permission.


### WA-R065 — Sensitivity catalog convergence

Role & Authority owns the versioned category/purpose access-policy catalog. The source owner supplies context and Healthcare determines regulated applicability. Categories are not an ordered ranking: enforce every applicable restriction, field mask, evidence and qualified-provider requirement together. Unknown classification or missing purpose denies protected disclosure. Media enforces this intersection for exact asset versions and grants; Audit preserves declared classification and enforces scoped queries; Messaging applies the intersection to Thread and item disclosures. None owns a competing catalog. Changed classification invalidates stale access/projections; normal never implies public. Implementation must exercise mixed-category and unknown-policy denial before interface qualification. Retention remains Privacy/policy-owned.


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


## WA-R067 — Typed moderation execution and normalized receipts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-103 remains the existing cross-cutting execution protocol; no new Shared Operation ID or schema change is authorized. Each instruction carries authorized decision/action ID, case/cycle, typed owner target ID and expected owner revision, approved effect, actor/service authority, purpose/policy/evidence references, semantic effect key and correlation. Owners validate target/action compatibility and current authority before mutation. The following versioned ports name existing owner handlers, not new lifecycle ownership or permission.

| Existing primary target / typed downstream effect | Owner port v1 | Allowed effect and guard |
| --- | --- | --- |
| job, organization | Hiring applyHiringModerationDecision.v1 | Publication suppression/eligible restoration under R047; compliance, lifecycle and all restrictions still apply |
| candidate_profile, with owned current search projection reference | Candidate applyCandidateModerationDecision.v1 | Search-projection suppression/eligible restoration only; current explicit opt-in/readiness required. No application mutation or new Candidate Hold target |
| thread, message | Messaging applyMessagingModerationDecision.v1 | Persistent content restriction/authorized restoration under R054; current membership, sensitivity and all restriction sources still apply |
| media_asset, media_access_grant | Media executeMediaModerationInstruction.v1 | Existing asset freeze, public exposure/grant revocation, evidence preservation and eligible file exposure restoration; source context and safety remain required |
| digital_download_asset, affected owned grant references | Digital Goods applyDigitalModerationDecision.v1 | Disable/restore asset and revoke affected grants; current Order entitlement/Media safety/purchased policy required, no revival of terminal grant |
| course_video_asset, affected owned playback grant references | Video applyVideoModerationDecision.v1 | Disable/restore asset and revoke affected playback grants; current entitlement/safety/provider evidence required |
| review | Review applyReviewModerationDecision.v1 | Existing hide/remove/authorized restoration under R026; restore current eligible accepted revision and adjust original reputation contribution exactly once |
| offering | Marketplace applyOfferingModerationDecision.v1 | Valid moderation restriction/clearance under R035; clearance returns to draft, fresh publish remains separate |

Existing unversioned Media/Digital/Video handler names become aliases of their listed v1 contract and must not create duplicate effects. CandidateSearchProjection, DigitalDownloadGrant and playback-grant references are owner-local downstream effects under existing primary targets, not new ModerationTargetType values. The owner validates their parent/target relationship. Each port returns semantic effect key, source decision/action, target/revision, effect state, safe outcome/retry classification and durable receipt identity. No secret/provider payload or private evidence is returned.

| Local result | Canonical effect state | Required semantics |
| --- | --- | --- |
| accepted/queued | acknowledged | Durable acceptance only; mutation/provider effect not yet proved |
| applied | completed | Exact requested effect durable, resulting owner revision and proof retained |
| restoration applied | restored | New authorized linked restoration completed; original restriction/history untouched |
| already-applied | Original receipt state | Replay exact stored receipt, including pending state; dedupe alone is not completion |
| unsupported/denied/stale conflict | failed with terminal or reevaluate classification | No mutation; conflict requires fresh facts and applicable authorized decision, never silent overwrite |
| known retryable failure | failed with retryable classification | Retry the same semantic effect identity |
| uncertain owner/provider outcome | acknowledged with reconcile_required outcome | Durable unknown-state evidence; reconcile original effect before redispatch, never claim completed/restored |

Multi-owner work retains per-step receipts; Report/Case action_taken requires every required successful effect under R058. Search refresh and provider request acknowledgments do not prove de-indexing or revocation. Restoration is a new effect linked to the original, not an edit of the original receipt. Partial bulk revocation remains incomplete until its target inventory is accounted.

Order/payout reusable stops use Hold's registered typed action/command boundary per CL-09-R007/R059, not direct Moderation writes to Order/Payment. Release triggers current owner reevaluation, never financial execution, content restoration, service completion or review eligibility. Candidate Hold types absent from the typed Hold schema remain disabled. CL-01 has no generic moderation executor under R063: only separately named authorized security/entitlement/Hold/lifecycle commands may act. Enumeration of user or profile targets is not permission. Other target/effect families not listed here must have an existing explicit owner registration before activation; this scoped matrix does not invent their semantics or silently delete their historical proposals. Unsupported combinations return unsupported, with no fallback mutation.

R026 already settles explicitly authorized Review restoration; old unresolved base text is superseded. R042 settles Booking Professional reports, authorized support adjudication and Customer contest, with no automatic consequence; R052 completed/no_show aliases are performance-report facts, not final financial/review truth. These are existing rulings, not new product decisions. Contract adapters/fixtures, typed receipt persistence and coordinated migrations remain implementation qualification.


## WA-R068 / WA-R069 — Authority facts and committed event obligations

This Module adopts its `messaging` action/fact row and specifically registered producer/consumer effects in `context/reconciliation/authority-event-contracts.md`. Role interprets the catalog; this owner retains facts and lifecycle. Register each concrete protected port before activation; a grouped port row does not authorize unspecified commands.

Owner action scope: `createDirectThread / removeThreadParticipant / getThreadParticipantFacts`. Permitted relationships: current contextual participant; registered context owner manages derived membership. Required owner facts: Thread/context binding, participant membership revision, per-action restrictions, Message revision, historical-access policy. Assurance: ordinary B; restricted evidence A; privileged restoration S. These facts include typed target, source revision, subject relationship, purpose/action and evaluation time; missing/stale/unavailable facts cannot authorize, and current revisions are checked again at effect. B/S/A have the precise appendix meanings; source services cannot invent human assurance.

Producer obligations:

- `messaging.message_created.v1 / messaging.message_revised.v1 / messaging.message_hidden.v1 / messaging.membership_changed.v1`: Thread revision plus affected Message/membership reference/revision. Registered effect: authorized realtime invalidation only; Notification gets separate message.new.v1 intent.

Consumer obligations:

- `application.lifecycle_changed.v1`: consume only the effect naming this Module — Interview: cancel nonterminal interviews when non-interviewable; Messaging reevaluates explicit context membership.
- `booking.confirmed.v1 / booking.rescheduled.v1 / booking.cancelled.v1`: consume only the effect naming this Module — Video/Location/Messaging: fresh scope reevaluation; Notification via separate source intent; Calendar owner handles provider.
- `organization.membership_changed.v1`: consume only the effect naming this Module — Candidate/Interview/Messaging: revoke derived access; all protected requests use current membership.
- `interview.participant_changed.v1`: consume only the effect naming this Module — Video/Calendar/Messaging if context exists: reevaluate current authorized audience.

Each audience receives only its needed fields. Obtain fresh source facts before protected decisions; invalidation is not authority.

Persist source history and outbox intent atomically; use event identity/fingerprint deduplication, source-revision watermarks, tombstones and correction lineage as specified by WA-R069. Delayed facts cannot restore revoked exposure; gaps require owner replay/current snapshot. Registered Hold applicability may prompt current reevaluation only for existing typed targets/actions; release is never automatic restoration or financial execution. Source events cannot substitute for explicit Privacy/Moderation/provider effect commands or WA-R066 notification intents.


## WA-R074 — Contextual Customer display and Gig participation requirements

This owner adopts its source/consumer obligations in `context/reconciliation/context-query-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.

## WA-R081–083 — Gate 4 bridge obligations

This owner adopts the scoped contracts in `context/reconciliation/bridge-contract-bindings.md` and the following reviewed bridge responsibilities. The named owner retains truth; another owner's query/event/receipt does not authorize a local transition. R068/069/075 and existing approved rulings remain binding. These are architecture obligations, with executable/schema/provider qualification still required before activation.

| Family | Role in current boundary | Contract and local obligation |
|---|---|---|
| BF-007 | consumer/composer | getCustomerContextDisplay.v1. Display is contextual to a currently authorized source relationship; it is not a public Customer profile. Safe template fallback may omit the display; denied/unavailable never leaks identity. |
| BF-017 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-026 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-027 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-033 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-048 | Producer/source | validateOwnedTargetReference; getClassificationSourceDescriptor.v1 where AI applies. Typed owner existence/relationship/currentness is distinct from authorization. AI receives only registered target-purpose descriptors; delivery and rail callers receive bounded target facts. No UUID existence probe, generic repository loader or cross-owner content dump. |
| BF-063 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-065 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-066 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-082 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-083 | consumer/composer | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-084 | consumer/composer | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-102 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-115 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-116 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-117 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-123 | consumer/composer | queryGigOwnerFacts; queryOrderParticipantFacts; ensureContextThread. Messaging uses current participants/source applicability; P19 Order conversation receives Booking/case navigation without wider membership. Source relationship facts are not standalone access authorization; no universal Thread admission. |
| BF-131 | Producer/source | appendAuditEvent; recordSensitiveAccess; separate recordDomainAccessEvent. Owner supplies registered safe action/target/purpose/outcome, not content. Mandatory durable domain/control/access proof precedes critical mutation or disclosure; generic audit transport can retry only after required durable proof. No universal rollback or success on absent mandatory evidence; owner ledgers remain distinct. |
| BF-152 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-153 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-154 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-155 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-156 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-157 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-158 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-159 | consumer/composer | Owner executePrivacyInstruction and adapter delete/reconcile. Privacy routes instructions by actual record/resource owner, with retention scope first. Provider already-absent, deleted, retained, pending and failed are distinct; uncertainty remains incomplete. No direct foreign SDK/cascade cleanup or claim that local disconnect erased provider data. |
| BF-160 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-162 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-163 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-164 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-175 | consumer/composer | getMediaReadiness; canMediaAssetBeAttached; attachValidatedMedia. Media validates ready/clean/non-frozen exact version and permitted use; contextual owner creates explicit join/role after current target authority. Detach is not byte deletion; private originals/EXIF are not public renditions. Candidate resume/cover-letter roles and actual parser/upload limits require fixtures. |
| BF-176 | Producer/source | authorizeContextualResourceAccess; requestMediaAccess. Exact actor/context/asset-version/action/purpose authorization precedes independent Media safety/grant/TTL. Participant facts alone are not permission. Candidate logs resume access separately; Privacy authorizes current bundle generation. No general admin or possession-of-media-ID bypass. |
| BF-177 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-183 | consumer/composer | R068 owner facts; R069 membership/application/interview changes; ensureContextThread. Current Organization membership is necessary for named hiring actions but not universal Thread access. Messaging rechecks context/participants and revokes audience; Role reads owner facts directly, with no speculative replicated membership event cache. |
| BF-196 | consumer/composer | evaluateHealthcareVendorReadiness; resolveEffectiveHealthcareBoundary; sensitivity field policy. Enforce every applicable category/purpose and exact ancestry before serialization/provider call. Messaging applies current restriction/mask; Notification only approved channel-safe variables and no PHI/body. Unenforceable redaction/unknown provider coverage denies; urgency/admin role cannot bypass. |
| BF-198 | Producer/source | Owner exportPrivacyContribution/serializer; Privacy manifest and Media artifact protocol. Versioned complete subject inventory and field dispositions precede serialization. Exclude third parties/secrets/restricted proof from requester bytes while accounting for retained categories. Privacy binds exact contribution hashes/versions into completed manifest; partial source/scan failure cannot become ready export. |
| BF-203 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-204 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-205 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-206 | Producer/source and consumer/composer | publishRealtimeChange. Post-commit authorized minimal delta/invalidation; current Thread audience rechecked before emission, revoked subscriptions terminate and reconnect refetches owner truth. No overbroadcast fallback; provider qualification remains separate from event semantics. |
| BF-210 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-211 | consumer/composer | getNotificationDeliveryState; validateNotificationActionRoute. Source receives normalized delivery uncertainty, never legal/domain success. Catalog permits only approved internal/allowlisted HTTPS contextual route with safe refs; opening reauthenticates and reauthorizes at source. No bearer token/file URL/raw destination in generic intent or evidence. |
| BF-212 | Producer/source | Explicit non-indexing boundary. Private Message/Notification contents are absent from public Search. Baseline bounded inbox/unread queries remain Messaging/Notification-owned; future private search is disabled and not a core rail dependency. |
| BF-224 | consumer/composer | Owner executePrivacyInstruction and adapter delete/reconcile. Privacy routes instructions by actual record/resource owner, with retention scope first. Provider already-absent, deleted, retained, pending and failed are distinct; uncertainty remains incomplete. No direct foreign SDK/cascade cleanup or claim that local disconnect erased provider data. |
| BF-230 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-231 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-232 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-234 | consumer/composer | SH-132 rate-limit policy and shared validation/error transport. Role governs named action/purpose policy; shared runtime enforces bounded request/error/rate mechanics. Sensitive endpoints use non-enumerating external errors with restricted internal diagnostics. Missing enabled-action budget/assurance policy denies activation; no invented limits or feature-local limiter. |
| BF-240 | consumer/composer | queryActiveModerationRestriction. Current typed restriction/case/effect evidence is a required local gate; unavailable cannot restore. Owner executes supported effect and preserves imposed provenance; no consumer re-adjudication or raw legal evidence dump. |
| BF-242 | Producer/source and consumer/composer | requestMediaAccess (SH-127); Media-internal issueSignedMediaUrl. External caller uses composite SH-127, never SH-087 signer. Bind exact ready version, current purpose/context and proof before disclosure. URL issuance is not read/completion; reusable grants remain bounded and revoked generations deny. No credentials in Message/events/audit; clean document is not verified identity. |
| BF-249 | consumer/composer | queryAuditEvents; querySensitiveAccessHistory. Bounded paginated authorized redacted evidence queries, with proof/step-up where required. Audit is retained evidence, not current source permission or foreign repository expansion; no operator dashboard becomes mutation authority. |
| BF-256 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-257 | consumer/composer | Versioned canonical hashing, tokens, envelope encryption, normalization, structured validation; owner adapters. Mechanisms retain permanent SH identities; owners select exact purpose/input/version and retain proof meaning. Key/provider choices and rotation/expiry fixtures precede live use. SH-073 optional chain fields remain unpopulated absent owner partition/sequence/canonicalization qualification; no universal chain/tamper-proof claim or plaintext fallback. |
| BF-266 | consumer/composer | SH-044–058 durable commands/outbox/inbox/queue/locks/CAS/reservations; owner lifecycle and proof mechanisms. Shared infrastructure provides durable claims/leases/fences/retry/semantic fingerprint and owner-local transaction hooks. Owner chooses aggregate keys, transitions, deadlines, effect/compensation identities and access rules. No shared business lifecycle, distributed transaction or exactly-once transport; unknown result reconciles before reservation release. Runtime placement/implementation is Gate5/8 work, not a new Module. |
| BF-268 | Producer/source | Owner exportPrivacyContribution/serializer; Privacy manifest and Media artifact protocol. Versioned complete subject inventory and field dispositions precede serialization. Exclude third parties/secrets/restricted proof from requester bytes while accounting for retained categories. Privacy binds exact contribution hashes/versions into completed manifest; partial source/scan failure cannot become ready export. |


## WA-R085–087 — Platform convergence

This current owner review applies WA-R085 terminating facts and WA-R086 shared-runtime placement. It preserves the prior lifecycle rulings and R068/R069 registrations; historical proposed event names or resolved unknown-owner labels above do not authorize an additional stream or reopen a settled decision.

**Authoritative lifecycle.** Typed-context thread uniqueness; participant current state plus immutable history; send/edit/hide/read and contextual attachments.

**Incoming source facts.** Current Order/Gig/Application/Interview participant facts; Media readiness/access; Healthcare field-category constraints.

**Action checks.** P19 Booking/Dispute communication uses Order context; direct pair and group identity differ; private body outside Search/events; no role implies thread membership.

**Consumer and recovery obligations.** Commit Message before notification/invalidation; reauthorize audience on subscribe/emission/reconnect; removal revokes future access according to owner history policy; no source lifecycle mutation on delivery.

**Terminating contracts.** R085 source-fact branches validate narrowly registered service/purpose/target/field scope and current source tokens without re-entering the composed authorization/readiness/access decision. User-facing protected queries still enforce full Role and owner checks. Unregistered purposes deny. Sensitive disclosure still requires durable proof; no generic service bypass or source projection as permission.

The platform action matrix records this owner plus its specific coordinated action slices. Actual DTO/failure/replay/freshness fixtures and all applicable external gates remain prerequisites before activation; no contract is FROZEN_FOR_IMPLEMENTATION.
