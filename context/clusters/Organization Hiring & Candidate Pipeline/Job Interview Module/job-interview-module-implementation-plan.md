# Job Interview Module Implementation Plan

> **Module ID:** `job_interview`  
> **Module name:** Job Interview Module  
> **Primary Cluster:** CL-06 — Organization Hiring & Candidate Pipeline  
> **Authority:** subordinate to `job_interview/module-architecture.md` and the CL-06 build plan  
> **Purpose:** ordered, testable implementation work inside the Job Interview Module only

## Core Principle

Implement Job Interview through narrow, verifiable slices:

```text
public / observable behavior
→ runtime-validated command/query
→ Job Interview-owned policy
→ authoritative JobInterview / JobInterviewEvent write or read
→ canonical shared-operation calls
→ owner-issued domain event / outbox
→ downstream owner requests
→ tests
→ hard exit gate
```

The Module must work as a valid hiring-interview source of truth before Video, Calendar, Messaging, or Notification integrations are allowed to complicate the lifecycle. Provider failure must never become the source of interview truth.

This plan is intentionally narrower than the CL-06 build plan. It does not independently reorder Cluster work or implement neighboring Modules.

## Build Rules

1. Follow root architecture/code standards, CL-06 architecture/build plan, and `job_interview/module-architecture.md`.
2. Job Interview owns only its declared source truth.
3. Use other Modules through approved public interfaces/events or versioned fixtures when the CL-06 build plan explicitly permits fixtures.
4. Reuse Canonical Shared Operations; do not create local auth, permission, idempotency, queue, audit, retry, concurrency, provider, privacy, messaging, notification, media, or search infrastructure.
5. Every mutation is runtime-validated, actor-resolved, server-authorized, context-validated, transaction-safe, and concurrency-protected.
6. Every successful interview lifecycle mutation appends `JobInterviewEvent` in the same transaction.
7. Every retryable command uses canonical idempotency and returns the original result on replay.
8. External effects start only from committed source truth and are durable/retryable/observable.
9. Job Interview never directly mutates `JobApplication.status` or `JobApplication.stage`.
10. Job Interview never becomes Booking.
11. Video and calendar provider details remain behind their canonical owners.
12. Notification owns delivery; Messaging owns Thread/Message; Candidate Application owns resume authorization/proof; Audit owns generic access logs.
13. Privacy / Data Erasure owns privacy orchestration; Job Interview only enumerates and executes against its own records.
14. Search remains projection and is not required for Job Interview source reads.
15. Domain denial, authorization denial, stale conflict, dependency unavailable, provider failure, retry exhaustion, and privacy retention are distinct outcomes.
16. No unresolved architecture question is resolved implicitly in code.
17. Every numbered feature ends with tests and a hard exit gate. A failed gate stops sequential execution.
18. Documentation changes are part of feature completion when implementation settles an approved deferred decision.

## Preconditions

### Cluster sequencing precondition

The CL-06 build plan places Job Interview core work at Cluster Feature 09, after recruiter application/pipeline Feature 06. Production implementation of this Module must not begin ahead of that sequence unless the Cluster build plan is explicitly revised.

### Hard platform/shared prerequisites

The following must exist as real platform capabilities before production Job Interview mutation code ships:

- `resolveAuthenticatedActor`;
- `authorizeResourceAction` plus RLS parity support;
- runtime validation standard;
- Prisma/Postgres transaction layer;
- `executeIdempotentCommand`;
- `withOptimisticConcurrency` and/or `acquireAggregateLock` according to root persistence standards;
- `appendDomainLifecycleEvent` conventions;
- transactional `publishDomainEvent` outbox and `deduplicateDomainEvent` inbox;
- `enqueueReliableJob` / retry/dead-letter infrastructure;
- structured logging/request/correlation IDs;
- `appendAuditEvent` / `recordSensitiveAccess` where required.

If any platform primitive is not implemented yet, the Module may define/compile against a versioned contract fixture only where the Cluster coordinator allows it. The Job Interview Module must never implement the missing generic primitive locally.

### Hard dependency interfaces for core lifecycle

Before Feature 02:

- Organization Hiring owner-fact interface sufficient to establish Organization/Job relationship;
- Candidate Application interface sufficient to return an interviewable `JobApplication` context with candidate/organization/job IDs and source state/version;
- Role / Authority decision interface using source-owner facts.

### Dependencies that may initially be fixtures

These can be contract fixtures until their dedicated Module feature:

- Notification for Feature 02/03;
- Messaging for Feature 06;
- Video Infrastructure for Feature 06;
- Calendar capability for Feature 07 only after U-CL06-16 is resolved;
- Privacy protocol for Feature 08 if Privacy implementation lags, provided the contract is frozen by CL-06/Privacy architecture.

### Explicit architecture blockers

- **U-CL06-14 / U-JI-01:** participant ownership/removal/candidate invariant — blocks Feature 04.
- **U-CL06-15 / U-JI-02:** transition/reschedule semantics — at minimum the transition subset used by Feature 02 must be approved; advanced rescheduling blocks Feature 05.
- **U-CL06-16 / U-JI-03:** calendar capability ownership — blocks Feature 07.
- **U-JI-04:** `externalMeetingUrl` semantics — blocks use as credential-bearing meeting link.
- **U-JI-05:** parent application-state effects — blocks full application/interview synchronization in Feature 05.
- **U-JI-06/U-JI-07:** retention/privacy target semantics — block destructive production privacy execution in Feature 08.
- **U-JI-08:** concurrency token/root strategy — must be resolved enough to implement stale-write detection in Feature 02.
- **U-JI-09:** event name registry — must be approved before external consumers freeze event names in Feature 09.
- **U-CL06-17/U-JI-12:** current Prisma structural defect — must be cleared before migrations if root schema validation is affected.

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Job Interview Boundary, Runtime Contracts, and Persistence Foundation

### Objective

Establish the Job Interview Module boundary, validated public contract shapes, owner-only repository layer, error taxonomy, and testable persistence access without yet implementing the full lifecycle or any provider integration.

### Observable Result

The repository contains a compilable `job-interview` Module with:

- public command/query type contracts;
- runtime validation schemas;
- dependency ports that use owner DTOs rather than cross-domain repositories;
- Job Interview-owned repositories for `JobInterview` and `JobInterviewEvent`;
- explicit unsupported/blocking results for participant, advanced reschedule, and calendar operations whose architecture is unresolved;
- persistence/contract tests proving neighboring tables are not written.

No user-facing interview can yet be scheduled unless the next feature is complete.

### Cluster Build-Plan Link

Supports **CL-06 Feature 09 — Core JobInterview Proposal and Scheduling**, specifically its source-of-truth/public-contract foundation. It may begin only when CL-06 sequencing permits Feature 09.

### Dependencies

- CL-06 Feature 06 exit gate passed or Cluster plan explicitly revised;
- current Prisma schema available and parseable;
- root runtime validation/error conventions;
- `resolveAuthenticatedActor`, `authorizeResourceAction`, `queryOwnerFacts` contract shapes;
- canonical shared operations registry;
- current U-CL06/U-JI decision register.

### In Scope

- create/align the approved Module folder structure;
- define runtime input schemas for core commands and queries without making unresolved transition decisions;
- define stable public DTOs for `JobInterview` source reads;
- define dependency ports for Organization Hiring and Candidate Application owner facts;
- define Job Interview-specific error categories/reason-code namespace aligned to root conventions;
- implement Job Interview-owned repository reads/writes needed by later features;
- implement insert-only `JobInterviewEvent` persistence adapter compatible with `appendDomainLifecycleEvent`;
- implement context assembly interfaces but not final transition policy;
- add schema verification tests for currently owned fields/indexes/relations;
- document current schema concerns (`externalMeetingUrl`, calendar fields, cascade deletion, no explicit version).

### Out of Scope

- participant repository writes;
- reschedule behavior;
- interview state transition matrix beyond test scaffolding;
- UI;
- Messaging/Notification/Video/Calendar integration;
- Privacy destructive execution;
- provider SDKs/webhooks;
- JobApplication mutation;
- schema changes that assign participant ownership or change reschedule cardinality without architecture approval.

### Module-Owned Data

- `JobInterview` read/persistence mapping;
- `JobInterviewEvent` insert-only persistence mapping;
- `JobInterviewStatus`, `JobInterviewLocationType`, `JobInterviewEventActor` in public/domain types.

`JobInterviewParticipant` remains read-only/unused until U-CL06-14 approval.

### Public Interfaces

Introduce contract definitions, not necessarily fully enabled mutations:

- `proposeInterview` request/result;
- `scheduleInterview` request/result;
- `cancelInterview` request/result;
- `completeInterview` request/result;
- `markInterviewNoShow` request/result;
- `getInterview`;
- `listApplicationInterviews`;
- `listOrganizationInterviews`;
- `listCandidateInterviews`;
- `getInterviewTimeline`;
- Job Interview owner-fact query for Role / Authority;
- versioned domain event envelope types.

Unresolved commands should return/compile as explicitly unavailable until their feature is authorized; do not expose a misleading working implementation.

### Shared Operations Used

- `queryOwnerFacts` — each source owner; define small dependency DTOs. **Local policy:** required relationship facts. **Prohibited duplicate:** cross-domain Prisma repositories.
- `appendDomainLifecycleEvent` — shared persistence mechanism; wire repository convention only. **Local policy:** event fields/vocabulary. **Prohibited duplicate:** universal event table.
- root runtime validation primitive if named separately by root standards.

### Domain Logic

Implement only pure invariants already binding:

- interview IDs/relationship DTO shape;
- `startsAt < endsAt` validator;
- known location-type enum validation;
- source DTO consistency checks that do not invent application interviewability policy;
- safe metadata/event payload allowlist primitives.

Do not implement the unresolved lifecycle graph.

### Authorization / Compliance

Authorization is represented as a port/contract and tested as required, but actual command effects are not enabled until Feature 02. Define action vocabulary centrally; do not encode OrganizationRole interpretation in this Module.

### Database / Transaction Behavior

- repository access must be scoped to Job Interview-owned tables;
- verify existing indexes support intended list queries;
- no new participant/reschedule constraints yet;
- confirm whole Prisma schema validation before migration work;
- do not rely on cascade delete for privacy semantics;
- no cross-domain writes in transactions.

### Events / Jobs

No background worker yet. Define outbox event contract hook but do not publish lifecycle events until Feature 02 has real mutations.

### Provider Integration

None. No provider package/import should appear under `src/modules/job-interview`.

### UI / Admin Surface

None required.

### Failure Behavior

- schema/contract mismatch fails tests/build;
- unresolved architecture returns explicit unsupported result rather than permissive implementation;
- dependency port unavailable is represented explicitly;
- whole-schema validation failure due U-CL06-17 blocks migration generation and is reported.

### Tests

- runtime schema validation tests for public inputs;
- repository ownership tests showing only Job Interview-owned Prisma delegates are used;
- Prisma model/index mapping tests or integration query smoke tests;
- error/result contract tests;
- owner-fact DTO contract tests with fixtures;
- sensitive event metadata allowlist/redaction unit tests;
- architecture lint/review check for forbidden imports/provider clients if repository tooling supports it.

### Documentation Updates

- update this Module architecture only if repository/root standards force a different public contract or folder placement;
- record any discovered current-schema mismatch in progress tracker;
- do not resolve U-JI blockers in documentation as “done” without explicit architecture approval.

### Acceptance Criteria

1. Module boundary compiles under strict TypeScript/root standards.
2. All core command/query inputs have runtime validation definitions.
3. No neighboring repository or provider SDK is imported.
4. `JobInterview` and `JobInterviewEvent` persistence is isolated to this Module.
5. Participant/reschedule/calendar unresolved behavior is visibly blocked.
6. Event metadata shaping excludes sensitive raw payloads.
7. Current schema validation status is known and recorded.

### Exit Gate

PASS only if repository-standard typecheck/lint pass; targeted contract/persistence tests pass; Prisma schema validation or documented blocker check passes; forbidden direct cross-domain writes/provider imports are absent; and the Cluster coordinator confirms Feature 09 may proceed.

# Phase 2 — Core Provider-Independent Interview Lifecycle

## 02 Proposal, Scheduling, and Core Terminal Transitions

### Objective

Implement the approved provider-independent `JobInterview` lifecycle subset so authorized actors can propose/schedule and record core terminal outcomes with one coherent hiring context and immutable interview-domain history.

### Observable Result

Against a real or versioned Candidate Application/Organization fixture:

```text
authorized actor
→ valid interviewable application context
→ propose/schedule/cancel/complete/no-show command
→ JobInterview authoritative state
→ exactly one JobInterviewEvent per successful mutation
→ versioned domain event in outbox
```

No Video, Calendar, Messaging, or direct Notification provider behavior is required for correctness.

### Cluster Build-Plan Link

Direct implementation of **CL-06 Feature 09 — Core JobInterview Proposal and Scheduling**.

### Dependencies

- Feature 01;
- approved minimal transition subset from U-CL06-15/U-JI-02;
- U-JI-08 concurrency strategy resolved enough for stale-write protection;
- Organization Hiring owner-fact interface/fixture;
- Candidate Application interviewability owner-fact interface/fixture;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- idempotency/concurrency/event/outbox primitives;
- optional Notification contract fixture only for post-commit request tests.

### In Scope

- `validateInterviewContext`;
- `validateInterviewTimeRange`;
- approved `validateInterviewTransition` subset;
- `proposeInterview`;
- `scheduleInterview`;
- `cancelInterview`;
- `completeInterview`;
- `markInterviewNoShow`;
- terminal timestamps;
- source transaction + `JobInterviewEvent` + outbox atomicity;
- authorized reads needed to confirm mutation result;
- local safe event-name registry for only approved core events;
- optional `interview.expired` only if U-JI-10 is approved within this feature; otherwise defer.

### Out of Scope

- participants beyond any minimum source context already required by existing schema reads;
- reschedule successor semantics;
- application-stage updates;
- Messaging/Video/Calendar integration;
- resume access;
- provider callbacks;
- advanced reminder/expiry behavior not yet approved.

### Module-Owned Data

- create/update `JobInterview`;
- append `JobInterviewEvent`;
- outbox event payload owned in meaning by Job Interview, stored by platform event infrastructure.

### Public Interfaces

Enable:

- `proposeInterview`;
- `scheduleInterview`;
- `cancelInterview`;
- `completeInterview`;
- `markInterviewNoShow`;
- `getInterview` minimally for mutation receipts if Feature 03 has not yet completed full reads.

### Shared Operations Used

- `resolveAuthenticatedActor` — actor context before every command. **Prohibited duplicate:** feature current-user helper.
- `authorizeResourceAction` — permission decision. **Local policy:** interview action/context. **Prohibited duplicate:** OrganizationRole switch.
- `queryOwnerFacts` — Organization/Candidate source facts. **Prohibited duplicate:** direct repositories.
- `evaluateComplianceHold` — only when Cluster/root says applicable to the action. **Local policy:** block effect. **Prohibited duplicate:** local hold flag.
- `executeIdempotentCommand` — command replay. **Local policy:** semantic fingerprint. **Prohibited duplicate:** ad-hoc key table.
- `withOptimisticConcurrency` / `acquireAggregateLock` — stale/conflicting transition safety. **Local policy:** interview lock/conflict rules. **Prohibited duplicate:** in-memory mutex.
- `transitionLifecycleState` — plumbing only. **Local policy:** approved transition graph.
- `appendDomainLifecycleEvent` — append JobInterviewEvent in transaction.
- `publishDomainEvent` — transactional outbox.

### Domain Logic

- resolve source context and reject mismatch before write;
- enforce `startsAt < endsAt`;
- store absolute timestamps; timezone strings remain display/context data;
- apply only architecture-approved transitions;
- set `cancelledAt`, `completedAt`, `noShowAt` only for corresponding transitions;
- use stable reason codes for denials/conflicts;
- never infer or update JobApplication stage/status;
- provider-independent scheduled state is valid truth even before downstream integrations exist.

### Authorization / Compliance

- org-side actions require Role / Authority with Organization/interview facts;
- candidate-side mutations only if explicitly allowed by approved action matrix; do not assume;
- candidate/org reads are relationship-scoped;
- support/admin requires platform authority, not generic bypass;
- use `recordSensitiveAccess` only for sensitive paths specified by root/Cluster policy; ordinary interview source reads do not automatically become AccessAuditLog without policy.

### Database / Transaction Behavior

One owner transaction per mutation:

1. claim idempotency command;
2. obtain required aggregate lock or compare-and-set token;
3. re-read authoritative current state;
4. validate transition/context;
5. mutate `JobInterview`;
6. append `JobInterviewEvent`;
7. persist domain outbox event;
8. commit;
9. persist idempotency result according to platform primitive.

No downstream provider/network call occurs inside this source transaction.

### Events / Jobs

Emit only approved core facts:

- `interview.proposed`;
- `interview.scheduled`;
- `interview.cancelled`;
- `interview.completed`;
- `interview.no_show`.

Outbox delivery retries outside the source transaction. No Job Interview worker yet unless proposal expiry is approved.

### Provider Integration

None. Video/calendar failures cannot affect this feature because no provider call exists here.

### UI / Admin Surface

No full UI required yet; server contract/integration tests are sufficient. A minimal internal proof route may be used only if repository test conventions require it, but Feature 03 owns the normal product read/UI surface.

### Failure Behavior

- invalid input → validation error, no write;
- unauthorized → no write/event;
- source context mismatch → deterministic context error;
- application not interviewable → dependency denial;
- dependency unavailable → explicit unavailable, no permissive fallback;
- stale/concurrent transition → conflict with current safe state/version;
- idempotency replay → original result, no duplicate event/outbox;
- outbox publisher outage after commit → source state remains truthful; event delivery retries.

### Tests

- pure transition tests for every approved and illegal transition;
- context consistency tests;
- time/timezone invariant tests;
- authorization/cross-org/candidate tests;
- aggregate+event+outbox transaction rollback tests;
- idempotent replay tests;
- concurrent schedule/cancel and complete/no-show tests;
- RLS/server parity tests if RLS is active;
- explicit proof that JobApplication row is unchanged;
- event payload privacy tests.

### Documentation Updates

If the approved minimal transition subset differs from `module-architecture.md` Proposed Ruling, update architecture first, then this plan/progress. Record concurrency strategy used by root primitives if U-JI-08 is settled.

### Acceptance Criteria

1. Core interview lifecycle works without any external provider.
2. Every successful mutation produces exactly one JobInterviewEvent.
3. No successful mutation can occur with mismatched application/org/candidate facts.
4. JobApplication does not change.
5. Concurrent conflicting transitions cannot both win.
6. Same idempotency key/fingerprint replays one result.
7. Domain event publication is durable through outbox.

### Exit Gate

PASS only if root typecheck/lint pass; Job Interview domain/integration/authorization/concurrency/idempotency suites pass; source transaction atomicity is proven; no provider/Booking/application mutation code exists; and the CL-06 Feature 09 source-truth exit conditions are satisfied.

# Phase 3 — Public Reads and Hiring Dashboard Surface

## 03 Interview Queries, Timeline, and Minimum Product Surface

### Objective

Expose privacy-shaped interview reads and the minimum recruiter/candidate interview UI needed to use the core lifecycle without leaking dependency truth or sensitive metadata.

### Observable Result

Authorized recruiters and candidates can:

- view interview list/detail;
- see approved schedule/location-mode/status information;
- see an appropriately filtered timeline;
- perform core Feature 02 commands through validated server actions if product UI is in scope;
- receive deterministic empty/error/conflict states.

### Cluster Build-Plan Link

Completes the user-visible/query portion of **CL-06 Feature 09**.

### Dependencies

- Feature 02;
- repository UI conventions (Next.js/shadcn/etc. from root/project overview);
- Role / Authority/RLS;
- owner-fact query contracts;
- root error/loading/accessibility patterns if present.

### In Scope

- `getInterview`;
- `listApplicationInterviews`;
- `listOrganizationInterviews`;
- `listCandidateInterviews`;
- `getInterviewTimeline`;
- privacy-shaped DTOs;
- pagination/time/status filters;
- recruiter/candidate list/detail and core command surfaces;
- safe event metadata rendering;
- conflict refresh/retry UX;
- explicit indicator that provider/video/calendar features are unavailable when not implemented rather than fake links.

### Out of Scope

- participant management;
- reschedule UI;
- Messaging/Video/Calendar integration;
- resume viewer;
- generic organization ATS dashboard beyond interview-specific views;
- admin ops dashboard.

### Module-Owned Data

Read-only access to `JobInterview` and `JobInterviewEvent`. No new source tables.

### Public Interfaces

Finalize stable read DTOs and pagination contracts for the five queries. The UI must call public application/query services rather than importing repositories.

### Shared Operations Used

- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `queryOwnerFacts` as needed for Role facts;
- `recordSensitiveAccess` only for paths specifically classified sensitive;
- root UI/error primitives if applicable.

### Domain Logic

- organization lists only interviews belonging to the authorized organization;
- candidate lists only interviews linked to the actor’s CandidateProfile;
- timeline metadata is filtered through an allowlist and must not reveal provider errors/secrets or private internal/admin data;
- `rescheduledFromInterviewId` is displayed only as raw history reference until reschedule semantics are approved;
- `externalMeetingUrl` is not rendered as an active reusable link without U-JI-04 approval.

### Authorization / Compliance

- cross-org and cross-candidate reads deny;
- candidate access is based on CandidateProfile/user relationship, not possession of interview ID;
- support/admin least privilege;
- no resume access is implied by interview read permission.

### Database / Transaction Behavior

Queries use indexed access paths and pagination. No write transaction except commands delegated to Feature 02 services. Avoid N+1 cross-domain reads; use owner DTO batching or approved read-model composition if root architecture provides it.

### Events / Jobs

No new domain events for ordinary page reads. If sensitive access audit is required, that is generic Audit-owned evidence, not JobInterviewEvent.

### Provider Integration

None.

### UI / Admin Surface

Minimum Module-owned/Cluster-approved UI:

- organization interview list/calendar-style list if already part of hiring dashboard design;
- interview detail;
- candidate interview list/detail;
- propose/schedule/cancel/complete/no-show controls only where actor/action policy permits;
- timeline;
- loading/empty/error/stale-conflict states.

Do not invent a general ATS calendar or marketplace booking UI.

### Failure Behavior

- unauthorized/not found are shaped safely without data leakage;
- stale command conflict instructs refresh/retry;
- dependency unavailable for owner facts is explicit;
- malformed event metadata is omitted/flagged rather than raw-rendered.

### Tests

- query authorization/cross-org/cross-candidate;
- pagination/filter/index integration tests;
- DTO redaction tests;
- timeline metadata allowlist;
- component tests for empty/error/conflict states;
- Playwright: recruiter schedules → candidate sees same source truth;
- test that meeting URL/provider fields are not exposed before approved integration rules.

### Documentation Updates

Update UI registry/rules only if repository uses them and this feature adds named screens/components. Update public-interface docs if DTO fields change.

### Acceptance Criteria

1. Authorized org/candidate users can retrieve only their interview records.
2. Timeline is ordered and safely shaped.
3. No resume/video/calendar permission is inferred from interview read.
4. Core user journey is usable without provider integrations.
5. No direct repository imports from UI/server actions.

### Exit Gate

PASS only if root typecheck/lint, targeted UI/unit/integration tests, authorization/RLS tests, and critical Playwright provider-independent interview journey pass; no unresolved provider/participant feature is faked in UI.

# Phase 4 — Participant and Reschedule Domain Expansion

## 04 Interview Participant Lifecycle

### Objective

After U-CL06-14 is explicitly approved, implement interview-local participant invitation and response truth without turning participants into OrganizationMembers or Messaging ThreadParticipants.

### Observable Result

Authorized hiring actors can add approved participant roles, participants can respond, duplicates are impossible, and removal/revocation follows one documented durable policy. Downstream Messaging/Video access is not yet implemented here.

### Cluster Build-Plan Link

Implements the participant portion of **CL-06 Feature 10 — Interview Participants, Rescheduling, and Application Synchronization**.

### Dependencies

- Features 01–03;
- U-CL06-14/U-JI-01 fully resolved and architecture updated;
- Role / Authority;
- Organization Hiring/Candidate Application facts needed by approved role assignment policy;
- canonical idempotency/concurrency/event operations.

### In Scope

- formally adopt participant model/enums if approved;
- `validateParticipantAssignment`;
- `addInterviewParticipant`;
- `removeInterviewParticipant` or approved revoke command;
- `respondToInterviewInvitation`;
- candidate participant invariant;
- participant list/query on interview detail;
- participant event history/domain events;
- participant-specific authorization facts for Role / Authority;
- downstream recipient facts contract for later Notification/Messaging.

### Out of Scope

- Messaging ThreadParticipant mutation;
- Video join token issuance;
- calendar attendee sync;
- reschedule;
- application-stage mutation;
- new Organization membership/invitation lifecycle.

### Module-Owned Data

After architecture approval:

- `JobInterviewParticipant`;
- `JobInterviewParticipantRole`;
- `JobInterviewParticipantStatus`;
- related JobInterviewEvent rows.

### Public Interfaces

- `addInterviewParticipant`;
- approved remove/revoke command;
- `respondToInterviewInvitation`;
- participant list included in `getInterview` or separate query according to public DTO rules.

### Shared Operations Used

- actor/authority;
- owner facts;
- idempotency;
- participant-row concurrency lock;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`;
- `requestNotification` may be fixture-only until Feature 06.

**Prohibited duplicates:** local Organization membership policy, local Messaging participant table, custom invitation queue.

### Domain Logic

Implement exactly the approved U-JI-01 decisions:

- permitted roles and who may assign them;
- whether candidate row is mandatory and unique;
- relation of interviewer/coordinator/observer to Organization membership;
- response transitions;
- durable removal/revocation semantics;
- whether removed participant can be re-invited and what history is retained.

Use composite `(interviewId,userId)` uniqueness; do not allow duplicate participant records.

### Authorization / Compliance

- organization actor authority server-side;
- candidate can respond only for own participant identity;
- participant record does not imply organization-wide authority;
- participant access does not imply resume access;
- sensitive participant/admin reads follow audit policy.

### Database / Transaction Behavior

- if schema changes are required for removal/revocation, they must be architecture-approved first;
- add participant and event/outbox atomically;
- response and event/outbox atomically;
- participant lock key `(interviewId,userId)`;
- duplicate add with same idempotency key replays; duplicate without same semantic command returns deterministic already-participant/conflict outcome.

### Events / Jobs

Emit approved participant facts:

- `interview.participant_invited`;
- `interview.participant_responded`;
- approved participant removed/revoked event.

No reminder/expiry worker unless U-JI-10 defines it.

### Provider Integration

None. Do not sync calendar attendees or Video roles yet.

### UI / Admin Surface

- participant list;
- invite/add control for authorized org actor;
- participant accept/decline/tentative controls;
- approved remove/revoke control;
- candidate participant status display.

### Failure Behavior

- unresolved policy → feature remains disabled, no guessed fallback;
- invalid role/source relationship → domain denial;
- duplicate participant → deterministic conflict/idempotent replay;
- concurrent response/removal → one transaction wins, loser receives conflict/current state;
- notification unavailable does not corrupt participant truth.

### Tests

- participant role/assignment matrix;
- candidate invariant;
- composite uniqueness;
- response transition matrix;
- removal/reinvite semantics;
- cross-org/candidate authorization;
- response/remove concurrency;
- event/outbox atomicity;
- no ThreadParticipant/OrganizationMember direct mutation.

### Documentation Updates

Mandatory: once U-CL06-14 is approved, update Module/Cluster architecture decision registers and data ownership table before implementation. Record any schema migration and participant removal rule.

### Acceptance Criteria

1. Participant ownership is explicitly approved and reflected in architecture.
2. Every participant state change is owner-only, authorized, evented, and idempotent.
3. Duplicate participants are impossible.
4. Candidate/organization authority boundaries remain separate from participation.
5. No downstream communication/video/calendar source truth is created.

### Exit Gate

PASS only if U-CL06-14/U-JI-01 is resolved; schema/migration validation passes if changed; participant unit/integration/authorization/concurrency tests pass; no adjacent participant lifecycle is duplicated; and CL-06 Feature 10 participant requirements are satisfied.

## 05 Rescheduling and Parent Application Synchronization

### Objective

After U-CL06-15 and U-JI-05 are resolved, implement deterministic reschedule history and owner-safe reaction to Candidate Application lifecycle changes without cross-writing application truth.

### Observable Result

- a recruiter can reschedule under one approved mutate/successor model;
- concurrent reschedules cannot create ambiguous active history;
- Candidate Application changes are consumed idempotently and produce only approved Job Interview-local effects;
- any request to move application stage crosses Candidate Application’s public interface/event boundary.

### Cluster Build-Plan Link

Completes **CL-06 Feature 10**.

### Dependencies

- Feature 04 if participant transfer/revocation is part of reschedule semantics, otherwise Feature 03 minimum;
- U-CL06-15/U-JI-02 resolved;
- U-JI-05 resolved for parent-state effects;
- Candidate Application event/command contract;
- domain event outbox/inbox;
- concurrency primitive capable of enforcing the approved active-successor invariant.

### In Scope

- `rescheduleInterview`;
- predecessor/successor or approved mutate semantics;
- active-interview determination;
- event/timeline history;
- downstream handoff intents for later features (do not execute providers yet);
- `handleApplicationStateChanged`;
- idempotent reaction to withdrawal/rejection/closed/hired events according to approved policy;
- optional request to Candidate Application `transitionApplicationStage` only through its public command where policy requires.

### Out of Scope

- direct JobApplication writes;
- calendar/video/thread implementation;
- provider resource migration;
- automatic hiring decision;
- unapproved terminal-state reopen.

### Module-Owned Data

- `JobInterview` including `rescheduledFromInterviewId` and approved status changes;
- `JobInterviewEvent`;
- participant rows only if approved and reschedule policy requires participant carry-forward.

### Public Interfaces

- `rescheduleInterview`;
- `handleApplicationStateChanged` inbound event handler;
- active/current interview query if the approved reschedule model requires it;
- Candidate Application outbound stage-transition request/event contract where explicitly approved.

### Shared Operations Used

- actor/authority;
- `executeIdempotentCommand`;
- `acquireAggregateLock`/`withOptimisticConcurrency`;
- `transitionLifecycleState`;
- `appendDomainLifecycleEvent`;
- `publishDomainEvent`;
- `deduplicateDomainEvent` for application-state events;
- reliable job/retry only for downstream owner requests.

### Domain Logic

Implement the exact approved reschedule model. If successor-based:

- predecessor and successor must represent one deterministic chain;
- predecessor status/event history becomes immutable after successful reschedule except explicitly allowed administrative correction;
- enforce one effective active successor through database/transaction design;
- define participant carry-forward/reinvite behavior;
- do not copy provider room/calendar event truth as source data;
- new schedule is authoritative only on the successor.

Application synchronization:

- consume only Candidate Application-owned facts;
- withdrawn/rejected/closed/hired effect is explicit per architecture;
- no owner-local effect may change application truth;
- if Candidate Application denies a requested stage transition, record/return that downstream result without rewriting interview history.

### Authorization / Compliance

Reschedule is organization/candidate authorized only according to approved action matrix. Parent application event handler runs as trusted system event consumer and still validates event schema/source/version.

### Database / Transaction Behavior

- lock predecessor/current aggregate during reschedule;
- if one-active-successor invariant is approved, enforce in DB/serializable transaction, not only pre-check;
- predecessor/successor/event/outbox changes are atomic;
- inbound application event is inbox-deduped;
- app-stage command is out-of-transaction cross-Module request after interview commit when needed.

### Events / Jobs

Emit `interview.rescheduled` and approved local event for application-driven cancellation/expiry where it actually occurs. Do not emit an event claiming Candidate Application state changed unless Candidate Application itself emits it.

### Provider Integration

No direct provider call. Produce durable downstream intents/event facts that Feature 06/07 consumers can handle.

### UI / Admin Surface

- reschedule flow/history;
- display predecessor/current relation according to approved semantics;
- clear stale/conflict UX;
- application-closed/withdrawn effect visible without collapsing application/interview statuses.

### Failure Behavior

- concurrent reschedule → deterministic conflict, no multiple active successors;
- stale predecessor → current-chain response;
- Candidate Application command denial/unavailable → explicit downstream result; no direct DB fallback;
- duplicate application event → no duplicate cancellation/effect;
- provider integrations absent → reschedule source truth still valid.

### Tests

- complete reschedule matrix/cardinality;
- concurrent reschedule race;
- stale predecessor/current resolution;
- participant carry-forward/revocation rules if applicable;
- application event contract/dedupe;
- parent withdrawal/rejection/close/hire effects;
- explicit test that JobApplication table is never written by Job Interview;
- outbox/inbox atomicity.

### Documentation Updates

Mandatory architecture update when U-CL06-15/U-JI-02 and U-JI-05 are resolved. Document any schema constraint/index added for successor cardinality.

### Acceptance Criteria

1. Exactly one approved reschedule model exists in code and architecture.
2. History is deterministic under concurrency.
3. Job Interview never directly writes application state.
4. Parent-state events are deduped and produce only approved local effects.
5. No provider truth is copied during reschedule.

### Exit Gate

PASS only if U-CL06-15/U-JI-02/U-JI-05 are resolved, all reschedule/application contract/concurrency tests pass, no ambiguous successor can be produced, and CL-06 Feature 10 exit conditions are satisfied.

# Phase 5 — Collaboration and Delivery Handoffs

## 06 Messaging, Notification, Resume Review, and Video Handoffs

### Objective

Connect committed interview truth to Messaging, Notification, Candidate resume access, and Video Infrastructure through typed owner contracts while preserving all downstream source-of-truth boundaries.

### Observable Result

A scheduled interview can:

- create/retrieve a Messaging-owned context Thread;
- request safe notifications;
- initiate interview-related resume review through Candidate Application/Media;
- request a Video-owned `JobInterviewVideoRoom` and participant join access;
- survive downstream outages without losing or falsifying interview state.

### Cluster Build-Plan Link

Direct implementation of **CL-06 Feature 11 — Interview Messaging, Notification, Resume Review, and Video Handoffs**.

### Dependencies

- Feature 05 or Feature 03 minimum depending approved participant/reschedule sequencing;
- CL-06 Feature 07 resume-access contract available;
- Messaging `ensureContextThread`;
- Notification `requestNotification` and recipient contract;
- Video Infrastructure JobInterview room/join contract;
- Audit `recordSensitiveAccess`;
- reliable job/retry/Ops integration.

### In Scope

- `ensureInterviewThread` orchestration wrapper using Messaging public API;
- interview notification trigger matrix for implemented events;
- `authorizeInterviewResumeReview` delegation using Candidate Application reason=`interview_review`;
- Video room request/update/cancel owner command after source commit;
- normalized Video room status/result handler;
- Video join action that delegates token/grant decision to Video owner;
- retry/reconciliation of failed downstream requests through shared queue;
- integration failure telemetry;
- UI links/actions that use owner-issued references/tokens, never stored permanent credentials.

### Out of Scope

- calendar sync;
- direct SES/SMS/Web Push;
- custom Thread/Message tables;
- resume signed URL generation or ResumeAccessLog writing;
- Daily/Agora SDK or webhook handling;
- storing provider tokens in JobInterview;
- healthcare-specific video policy unless another approved lane explicitly applies to hiring later.

### Module-Owned Data

No new downstream source tables. Job Interview may store only architecture-approved local handoff receipt/reference data. `JobInterviewVideoRoom`, Thread, Notification, ResumeAccessLog, MediaAccessGrant, AccessAuditLog remain external.

### Public Interfaces

Job Interview-side operations:

- `ensureInterviewThread`;
- `requestInterviewNotifications` internal orchestration by event;
- `authorizeInterviewResumeReview` delegation facade if useful to UI;
- `requestInterviewVideoRoom`;
- `handleInterviewVideoRoomResult`;
- join-context query/command that calls Video public interface.

Do not expose provider-native room APIs.

### Shared Operations Used

- `ensureContextThread` — Messaging owner. **Local policy:** context/participant facts. **Prohibited duplicate:** local chat.
- `requestNotification` — Notification owner. **Local policy:** business trigger/safe variables. **Prohibited duplicate:** delivery client.
- `resolveNotificationRecipients` — source context + Notification. **Local policy:** interview recipient group. **Prohibited duplicate:** Notification owning participant truth.
- Candidate `authorizeContextualResourceAccess`/resume public interface — Candidate Application owner. **Local policy:** interview context only. **Prohibited duplicate:** local resume permission.
- `recordSensitiveAccess` — Audit owner for configured resume/video/admin access.
- `publishDomainEvent`, `deduplicateDomainEvent`, `enqueueReliableJob`, `executeRetryWithBackoff` — reliable handoffs.
- `recordIntegrationFailure` — Ops.
- Video owner internally uses canonical `invokeVideoProvider`; Job Interview must not.

### Domain Logic

- source interview commit precedes downstream request;
- Thread context uses `ThreadContextType.job_interview` and owner-approved participants;
- participant row does not automatically mutate ThreadParticipant; send approved participant set to Messaging;
- notifications use safe templates/route to authenticated app;
- resume path validates exact application/interview relationship then delegates; resume denial issues no Media grant;
- video location triggers Video room request; phone/in-person does not;
- Video result affects local integration readiness/UX only, not arbitrary interview lifecycle;
- participant removal/reschedule/cancel sends revocation/update intent according to approved policy after local commit.

### Authorization / Compliance

- interview action authorized first;
- resume review must also pass Candidate Application contextual authorization;
- Video join request includes participant/interview/time context but Video makes token/grant decision;
- sensitive resume/video/admin accesses use `recordSensitiveAccess` as required;
- notification variables are privacy-minimized.

### Database / Transaction Behavior

- no cross-owner writes in Job Interview transaction;
- outbox records downstream intent atomically with source event when needed;
- downstream worker uses idempotency key `{interview/sourceEvent}:{integration}:{operation}`;
- local handoff receipt updates use optimistic concurrency but never substitute downstream source state;
- duplicate normalized Video result is inbox-deduped.

### Events / Jobs

- existing interview domain events drive notification/thread/video consumers;
- integration retry worker handles transient Messaging/Notification/Video failures;
- exhausted failures create Ops evidence/dead-letter and remain visible;
- no provider webhook job in Job Interview.

### Provider Integration

Only through Video Infrastructure. Provider-specific tests, signature verification, dedupe, translation, and reconciliation live there. Job Interview contract tests consume normalized fixtures.

### UI / Admin Surface

- thread link after Messaging confirms Thread;
- resume-review action using Candidate/Media grant flow;
- video join action only when Video grants it;
- integration unavailable/retry indicator without exposing provider payload;
- no permanent meeting URL copied into UI state.

### Failure Behavior

- Messaging failure → interview remains truthful; retry thread creation;
- Notification failure → interview remains truthful; retry delivery request;
- resume denied → no signed URL/grant;
- Video unavailable → scheduled interview remains scheduled; video capability shows unavailable/retryable;
- access-audit failure follows root required-evidence policy; never silently claim audited access;
- retry exhaustion → IntegrationFailure/Ops reference.

### Tests

- Messaging/Notification/Candidate/Video contract tests;
- no duplicate Thread/Notification/Video rows in Job Interview;
- downstream idempotency/retry;
- Video outage/degradation;
- normalized Video result dedupe;
- resume access exact-context denial/success with expected Candidate/Media/Audit proof fixtures;
- sensitive payload redaction;
- cancellation/participant-removal revocation intent where approved;
- Playwright: scheduled video interview with owner fixtures/real interfaces.

### Documentation Updates

Freeze/version dependency contract references. If `externalMeetingUrl` is affected, resolve/update U-JI-04 before using it. Update integration diagrams if owner APIs differ from the architecture-neutral names.

### Acceptance Criteria

1. Job Interview owns no Thread, Notification, ResumeAccessLog, Media grant, AccessAuditLog, or VideoRoom truth.
2. Every downstream effect originates from committed interview truth and is retry/idempotency safe.
3. Video outage does not corrupt interview lifecycle.
4. Resume access cannot bypass Candidate Application.
5. Sensitive notification/log/event payloads are minimized.

### Exit Gate

PASS only if all four owner contract suites pass; integration outage/retry/idempotency tests pass; sensitive-access proof path passes; no provider SDK/direct downstream repository write exists; and CL-06 Feature 11 exit conditions are satisfied.

# Phase 6 — Calendar Integration

## 07 Interview Calendar Sync and Reconciliation

### Objective

After U-CL06-16 is resolved, synchronize interview schedule changes to the canonical calendar owner through a provider-neutral contract, persist only approved local attachment state, and reconcile failures without making calendar provider state the interview source of truth.

### Observable Result

Schedule/reschedule/cancel can request corresponding calendar create/update/cancel actions; normalized results update the approved local sync attachment state; duplicate callbacks do not repeat effects; provider outage leaves the interview truthful and surfaces retry/reconciliation state.

### Cluster Build-Plan Link

Direct implementation of **CL-06 Feature 12 — Interview Calendar Sync and Reconciliation**.

### Dependencies

- Feature 05;
- U-CL06-16/U-JI-03 resolved and architecture updated;
- U-JI-04 resolved if external meeting/calendar details overlap;
- calendar owner public port;
- provider owner webhook verification/dedupe/status/reconciliation capability;
- canonical reliable queue/Ops;
- any required calendar consent/connection policy exposed by calendar owner.

### In Scope

- request create calendar event after schedule commit;
- request update after reschedule under approved model;
- request cancel after interview cancellation where applicable;
- normalized result handler;
- local `externalCalendarEventId/provider/syncStatus/syncError` only if architecture confirms these are Job Interview-local attachment fields;
- local reconciliation of handoff/reference mismatch using calendar owner query, not direct provider API;
- safe event description/payload minimization;
- UI sync status/retry surface.

### Out of Scope

- availability engine redesign;
- BusyWindow/CalendarConnection ownership;
- direct Cronofy/Nylas SDK;
- raw webhook receiver;
- `ProcessedInterviewCalendarEvent`;
- using Booking lifecycle;
- storing full external event description/attendee payload as interview truth.

### Module-Owned Data

Only the approved local sync attachment fields on `JobInterview`. Provider event/connection state remains calendar-owner truth.

### Public Interfaces

- internal `requestInterviewCalendarCreate/Update/Cancel` orchestration;
- `handleInterviewCalendarSyncResult` normalized handler;
- optional local `getInterviewCalendarSyncState` query derived from approved fields.

### Shared Operations Used

Job Interview calls the calendar owner’s public interface. The calendar owner uses:

- `invokeCalendarProvider`;
- `verifyProviderWebhookSignature`;
- `deduplicateProviderEvent`;
- `translateProviderStatus`;
- `reconcileProviderState`.

Job Interview itself uses:

- `publishDomainEvent`/outbox;
- `deduplicateDomainEvent` for normalized result;
- `enqueueReliableJob`/`executeRetryWithBackoff` for handoff retries;
- `recordIntegrationFailure` for visible degradation;
- idempotency/concurrency for local sync-state updates.

### Domain Logic

- interview schedule is committed first;
- calendar call is a downstream effect;
- local sync state tracks request/result, not calendar truth;
- duplicate normalized provider result is no-op/idempotent;
- unknown provider status is mapped by calendar owner to explicit normalized unsupported/review result;
- provider outage does not cancel interview automatically;
- reschedule/cancel use the same external event reference rules defined by the calendar owner/approved reschedule model;
- private participant/application data is not embedded unnecessarily in calendar event metadata.

### Authorization / Compliance

User-facing calendar connection/consent lives outside Job Interview. Job Interview may request sync only when calendar owner reports the required authorized connection/context. Do not infer consent from a stored provider ID.

### Database / Transaction Behavior

- source schedule transaction and calendar request outbox are atomic;
- local sync-result update is compare-and-set/idempotent against interview/reference/request version;
- no provider callback transaction touches Job Interview before provider-owner verification/dedupe;
- no local provider-event dedupe table.

### Events / Jobs

- calendar request jobs from committed source event;
- normalized result event consumed through inbox;
- reconciliation may enqueue idempotent repair request to calendar owner;
- exhausted failure creates Ops evidence/manual retry surface.

### Provider Integration

Owned by calendar capability, not Job Interview. Project overview currently names Cronofy, but Job Interview public/domain types must not mention Cronofy unless the calendar owner’s generic result references a provider enum approved at the boundary.

### UI / Admin Surface

- sync state: pending/synced/failed/cancelled/rescheduled only through approved normalized/local vocabulary;
- safe error/retry indicator;
- no raw provider payload or secret;
- interview remains usable even when external calendar is degraded according to product policy.

### Failure Behavior

- owner/provider unavailable → retryable sync state/ops reference;
- duplicate callback → no duplicate event/update;
- stale result for old schedule/reschedule generation → ignored/conflict-safe;
- unknown status → explicit unsupported/review, not guessed success;
- retry exhaustion → source interview remains truthful; operational failure visible.

### Tests

- calendar owner contract/fixture tests;
- create/update/cancel idempotency;
- old/stale sync result after reschedule;
- duplicate normalized callback;
- provider outage;
- unknown status;
- reconciliation drift/repair request;
- no direct provider SDK or ProcessedInterviewCalendarEvent;
- privacy payload minimization;
- E2E with calendar fixture/real owner depending availability.

### Documentation Updates

Mandatory architecture update when U-CL06-16 is resolved. Document whether calendar fields remain on `JobInterview`, their meaning, and provider-neutral owner contract. If schema fields move, update migration/context before code.

### Acceptance Criteria

1. Calendar owner is explicitly settled.
2. Job Interview does not verify/dedupe provider webhooks itself.
3. Calendar outage cannot overwrite interview source truth.
4. Duplicate/stale results are harmless.
5. Local sync fields, if retained, are clearly attachment state only.

### Exit Gate

PASS only if U-CL06-16/U-JI-03 is resolved, calendar contract/provider-owner tests pass, duplicate/stale/outage/reconciliation paths pass, no direct provider code/dedupe truth exists in Job Interview, and CL-06 Feature 12 exit conditions are satisfied.

# Phase 7 — Privacy, Retention, Audit, and Evidence

## 08 Job Interview Privacy Executor and Evidence Completion

### Objective

Make Job Interview a complete participant in the Privacy target protocol and verify domain-history, generic audit, and sensitive-access evidence remain distinct and retention-safe.

### Observable Result

Privacy can enumerate a data subject’s Job Interview-held records and issue an idempotent owner instruction that returns accurate erased/anonymized/restricted/retained/failed results while linked provider/message/video deletion is delegated to their owners. Required interview-domain and generic access proof remains correctly separated.

### Cluster Build-Plan Link

Job Interview portion of **CL-06 Feature 13 — Privacy Executors, Retention, and Search/Media Erasure Handoffs**.

### Dependencies

- Features 02–07 as enabled;
- Privacy `enumerateSubjectData`, `executePrivacyInstruction`, `evaluateRetentionRequirement` protocol;
- U-JI-06 retention/cascade policy resolved before destructive production execution;
- U-JI-07 canonical target vocabulary resolved or versioned protocol explicitly supports generic owner targets;
- Audit/Ops interfaces;
- Messaging/Video/Calendar deletion/revocation owner contracts as applicable.

### In Scope

- enumerate interview records by candidate User/profile, participant User, scheduling actor where required by privacy definition;
- inventory `JobInterview`, participants, events, local meeting/calendar references;
- owner-local erase/anonymize/restrict/retain mapping;
- `evaluateRetentionRequirement` facts;
- `anonymizePersonalFields` mapping;
- delegate Thread/message, Video room/provider, Calendar provider resource deletion/revocation;
- idempotent rerun behavior;
- partial-failure reporting;
- audit/access proof completeness review;
- cascade-delete safety tests/migration changes only if architecture approves them.

### Out of Scope

- creating PrivacyRequest/DataErasureJob/DataRetentionExemption;
- direct deletion of Messaging/Video/Calendar provider resources;
- legal determination of retention periods by implementation convenience;
- erasing required Audit proof without Privacy/retention approval.

### Module-Owned Data

Potentially:

- `JobInterview` personal/reference fields;
- `JobInterviewParticipant` if owned;
- `JobInterviewEvent` actor/reason/metadata fields;
- approved local calendar/meeting references.

### Public Interfaces

- Job Interview implementation of `enumerateSubjectData`;
- Job Interview implementation of `executePrivacyInstruction`;
- Job Interview owner facts for `evaluateRetentionRequirement`;
- optional export serializer for privacy bundle contribution if Privacy protocol requires it.

### Shared Operations Used

- `enumerateSubjectData`;
- `executePrivacyInstruction`;
- `evaluateRetentionRequirement`;
- `anonymizePersonalFields`;
- `executeIdempotentCommand`/reliable jobs for repeatable execution;
- `appendAuditEvent` for destructive privacy execution if policy requires;
- `recordSensitiveAccess` for protected privacy/admin reads where policy requires;
- `recordIntegrationFailure` for delegated deletion failure.

### Domain Logic

- product cancellation/archive is not legal erasure;
- evaluate retention before destructive mutation;
- retained result must cite Privacy-owned exemption/evidence reference supplied by orchestrator;
- minimize retained event metadata/actor fields where allowed;
- do not falsify JobInterviewEvent history by rewriting status facts to indicate an event never happened;
- delegate external resources to their owners;
- repeated instruction returns same safe result/no duplicate destructive effect;
- partial downstream deletion cannot be reported completed.

### Authorization / Compliance

Privacy executor runs only for scoped trusted system/service actor under Privacy-owned orchestration. No user-facing direct delete endpoint is introduced here. Sensitive logs/exports remain minimized.

### Database / Transaction Behavior

- execute one target/disposition transaction at a time according to Privacy protocol;
- avoid uncontrolled cascade delete;
- if cascade policies are changed, migration must preserve relational integrity and required proof;
- idempotent target result is persisted by canonical Privacy/platform mechanism, not a local privacy job table;
- provider deletion occurs outside DB transaction through owner requests.

### Events / Jobs

Privacy orchestrator owns scheduling. Job Interview may emit owner-local completion/audit facts as protocol allows. Delegated provider/message/video deletion requests use reliable queue and return results to Privacy.

### Provider Integration

No direct provider deletion. Video/Calendar owners handle their providers; Messaging handles message/thread data; Media is not directly involved unless a future interview-owned attachment is introduced.

### UI / Admin Surface

None required in Job Interview. Privacy/admin UI remains Privacy-owned. Job Interview may expose safe operational target details to Privacy tools through contracts.

### Failure Behavior

- retention required → return retained with basis/reference, not failure;
- unsupported target disposition → explicit unsupported/manual review;
- partial downstream failure → partial/retryable result;
- retry exhaustion → visible Ops/Privacy failure, never false completion;
- missing target after prior successful erase → idempotent success according to protocol.

### Tests

- subject inventory completeness for candidate/participant/actor roles;
- erase/anonymize/retain mapping;
- retained event proof minimization;
- cascade safety;
- idempotent rerun;
- delegated Video/Calendar/Messaging deletion fixtures;
- partial failure/retry exhaustion;
- export redaction if applicable;
- Audit/Access separation;
- sensitive telemetry/log tests.

### Documentation Updates

Mandatory when U-JI-06/U-JI-07 are resolved. Update Module data model/retention tables and migrations before destructive behavior ships.

### Acceptance Criteria

1. Privacy remains sole orchestrator.
2. Job Interview only mutates its own records.
3. Retained records have explicit retention basis/exemption reference.
4. External resources are delegated to owners.
5. Reruns are idempotent and partial failures visible.
6. Domain history, AuditEvent, and AccessAuditLog remain separate.

### Exit Gate

PASS only if retention/target blockers for enabled destructive behavior are resolved; privacy unit/integration/delegation/idempotency tests pass; no local Privacy workflow exists; cascade behavior is safe; and Job Interview satisfies its portion of CL-06 Feature 13.

# Phase 8 — Module Integration Contract Proof

## 09 Job Interview Cross-Module Contract Proof

### Objective

Freeze and prove the Job Interview Module’s complete public boundary against every critical neighboring owner without direct repository access or permissive fallback.

### Observable Result

A contract/integration test suite can execute the hiring-interview path with real dependencies where available and versioned fixtures otherwise:

```text
application interviewable
→ interview proposed/scheduled
→ participant/reschedule policy if enabled
→ Messaging/Notification/Resume/Video
→ Calendar if enabled
→ parent application event
→ Privacy instruction
```

Each unavailable/deny/retry/duplicate/stale case produces a defined outcome while preserving ownership.

### Cluster Build-Plan Link

Job Interview portion of **CL-06 Feature 14 — Cross-Cluster Hiring Contract Proof**.

### Dependencies

- all enabled prior Module features;
- CL-06 Feature 14 may use versioned fixtures for unimplemented neighbors;
- event/outbox/inbox infrastructure;
- frozen event-name registry U-JI-09 before external consumers are treated as stable;
- final public DTO/error conventions from root standards.

### In Scope

- freeze/version public commands and queries;
- freeze owner-fact DTO for Role / Authority;
- freeze Candidate Application interviewability and application-state event contracts;
- freeze resume-review delegation contract;
- freeze Messaging/Notification/Video/Calendar contracts for enabled features;
- freeze Privacy executor contract;
- freeze domain event names/payload schema;
- add contract fixtures for every unavailable dependency;
- exercise unavailable/deny/retry/duplicate/stale-version cases;
- prove no cross-domain repository fallback.

### Out of Scope

- implementing missing neighbor internals;
- inventing a new generic shared operation for tests;
- new user features;
- resolving unrelated CL-06 blockers.

### Module-Owned Data

No ownership change. Existing Job Interview source records only.

### Public Interfaces

Stabilize/version all enabled interfaces from Sections 10–12 of Module architecture. Introduce explicit contract versioning where root event/API standards require it.

### Shared Operations Used

Exercise all previously approved operations used by Job Interview. No new shared primitive may be created solely to simplify test setup.

### Domain Logic

Contract proof must confirm:

- interview context comes from owners, not copied repositories;
- authority comes from Role / Authority;
- application stage/status remains external;
- provider results are normalized;
- downstream failures do not corrupt source truth;
- event consumers are idempotent;
- privacy executor mutates only owner data;
- unsupported unresolved behavior fails closed/explicitly unavailable.

### Authorization / Compliance

Cross-org isolation, candidate isolation, participant scope, resume privacy, sensitive access proof, admin/support least privilege, and RLS/server parity are mandatory contract cases.

### Database / Transaction Behavior

No new source schema. Integration tests inspect effects only through public interfaces where possible. Test fixtures may seed prerequisite owner records through test factories owned by their Modules, not by importing production repositories across boundaries.

### Events / Jobs

- outbox event schema/version contract tests;
- inbox dedupe tests;
- downstream retry/dead-letter contract tests;
- privacy target execution tests;
- no fire-and-forget behavior.

### Provider Integration

Use provider-owner normalized fixtures. Do not mock raw provider payloads inside Job Interview tests except to prove they are rejected/not accepted by its public interface.

### UI / Admin Surface

No new product UI required.

### Failure Behavior

Neighbor unavailable → explicit unavailable/retry/deny according to contract. Never direct DB fallback. Fixture version mismatch fails test/build rather than silently adapting.

### Tests

- public API/schema compatibility tests;
- consumer-driven contract tests if repository standard supports them;
- full cross-org/candidate authorization;
- application owner boundary;
- Messaging/Notification/Video/Calendar degraded cases;
- resume access proof;
- event duplicate/stale/version cases;
- privacy target cases;
- critical Playwright path through enabled interfaces.

### Documentation Updates

Freeze public interface/event contract section in Module architecture. Record contract versions in dependency/public interface docs and progress tracker.

### Acceptance Criteria

1. Every dependency has a typed real interface or versioned fixture.
2. No direct cross-domain repository read/write is required for normal production behavior.
3. Unavailable dependencies never become permissive bypass.
4. Event contracts are stable/versioned and privacy-minimized.
5. Critical hiring interview journey passes with ownership preserved.

### Exit Gate

PASS only if all Job Interview contract/integration/RLS/idempotency/privacy/degradation suites pass; dependency fixture versions match; no direct cross-domain repository fallback exists; and the Job Interview portion of CL-06 Feature 14 is complete.

# Phase 9 — Hardening and Production Verification

## 10 Concurrency, Replay, Reconciliation, Security, and Production Hardening

### Objective

Harden all production-enabled Job Interview behavior for state races, idempotency/replay, provider/rail outages, reconciliation, privacy/retention, audit completeness, telemetry safety, migration behavior, and query performance without adding new business ownership.

### Observable Result

The production-enabled Job Interview Module survives duplicate requests/events, concurrent transitions, dependency outages, provider drift, worker retry exhaustion, privacy reruns, migration/backfill rehearsals, and authorization attacks while source truth remains correct and operational failures remain visible.

### Cluster Build-Plan Link

Job Interview portion of **CL-06 Feature 15 — CL-06 Security, Reconciliation, Backfill, and Production Hardening**.

### Dependencies

- all enabled prior Module features;
- every U-JI/U-CL06 decision affecting enabled production behavior resolved and reflected in architecture;
- production queue/outbox/inbox/Audit/Ops infrastructure;
- root security/RLS/telemetry standards;
- provider-owner reconciliation for Video/Calendar enabled where relevant.

### In Scope

- comprehensive transition race testing;
- idempotency replay matrix;
- stale-write UX/API behavior;
- outbox/inbox replay and dead-letter recovery;
- interview integration reconciliation;
- proposal-expiry worker if approved;
- provider degradation and stale-result handling;
- sensitive-access audit completeness;
- telemetry redaction review;
- privacy rerun/retention enforcement;
- index/query-plan review for organization/candidate/time/status lists;
- migration rehearsal and backfill safety for any approved schema changes;
- operational/manual recovery surface only for failed interview integration jobs/privacy targets;
- rate limiting inherited from root where abuse risk warrants it;
- cleanup of deprecated/unapproved fields only through architecture-approved migration.

### Out of Scope

- new ATS features;
- new participant roles/lifecycles;
- new interview monetization/Track entitlements;
- new provider ownership;
- automated hiring scoring;
- Booking integration;
- generic workflow/state/event/retry frameworks.

### Module-Owned Data

Review all enabled Job Interview-owned models and indexes. No ownership transfer. Any backfill must preserve source history and event invariants.

### Public Interfaces

Stabilize/version existing interfaces; only hardening-compatible additions such as safe current-version/conflict metadata or operational retry receipt may be added if root conventions permit. No new source-of-truth API is introduced solely for operations.

### Shared Operations Used

- `executeIdempotentCommand`;
- `acquireAggregateLock`;
- `withOptimisticConcurrency`;
- `publishDomainEvent` / `deduplicateDomainEvent`;
- `enqueueReliableJob` / `executeRetryWithBackoff`;
- `recordIntegrationFailure` and Ops incident correlation;
- `appendAuditEvent` / `recordSensitiveAccess`;
- Privacy protocol;
- provider-owner `reconcileProviderState` indirectly for Video/Calendar;
- `runDeadlineExpiration` if proposal expiry approved.

No new generic Job Interview infrastructure is permitted.

### Domain Logic

Hardening must prove:

- no lifecycle command can create impossible status/timestamp combinations;
- concurrent reschedule/cancel/complete/no-show behavior is deterministic;
- participant responses/removals are deterministic if enabled;
- duplicate commands/events/handoffs have one business effect;
- stale provider results cannot overwrite newer schedule/integration state;
- dependency unavailable never triggers direct repository fallback;
- privacy/retention reruns cannot falsely erase/retain or lose proof;
- operational failure never becomes arbitrary lifecycle overwrite;
- no raw sensitive data enters logs/events/notifications/analytics.

### Authorization / Compliance

- full RLS/server parity review;
- least privilege for org/candidate/participant/admin/support;
- sensitive access matrix verified;
- no admin broad resume/interview bypass;
- root step-up policy applied if required;
- privacy destructive execution restricted to Privacy service actor;
- provider/webhook secret boundary verified in owner Modules.

### Database / Transaction Behavior

- inspect query plans/index use for list/detail/timeline;
- stress test conditional updates/locks;
- ensure deadlocks are bounded/retried safely where root DB standard allows;
- verify one-event-per-mutation under race;
- rehearse migrations against realistic data;
- run dry-run/checkpointed backfills where schema normalization is required;
- verify foreign-key/cascade behavior against approved retention policy;
- no destructive migration before reversible backup/compatibility strategy from root standards.

### Events / Jobs

- outbox publisher restart/replay;
- inbox duplicate/replay;
- queue lease expiry/worker crash;
- retry exhaustion/dead-letter/manual retry;
- proposal expiry lag if enabled;
- integration reconciliation;
- privacy target retries;
- operational alerting for repeated interview integration failure.

### Provider Integration

Test only through owner interfaces:

- Video provider outage/stale callback/reconciliation;
- Calendar provider outage/stale callback/reconciliation if enabled;
- unknown normalized provider statuses;
- no raw provider credentials/payload types in Job Interview package.

### UI / Admin Surface

Only operational support required for:

- failed/dead-lettered interview integration step;
- calendar/video degraded state;
- privacy-target failure reference;
- manual retry when owner policy permits.

These are operational views, not source truth and not a generic operations center owned by Job Interview.

### Failure Behavior

- no silent loss;
- no permissive fallback;
- no source-state overwrite from Ops/provider failures;
- retry exhaustion records an operational reference and stable user-safe state;
- dependency contract break fails build/test;
- migration/backfill anomaly stops rollout.

### Tests

Required final matrix:

- full domain/state unit suite;
- persistence/integration suite;
- public contract suite;
- RLS/security suite;
- concurrency stress suite;
- idempotency/replay suite;
- outbox/inbox/queue/dead-letter suite;
- provider degradation/reconciliation suite for enabled integrations;
- privacy/retention suite;
- telemetry redaction suite;
- migration/backfill rehearsal;
- query/load/performance tests for interview list/timeline;
- critical Playwright journeys across org and candidate roles.

### Documentation Updates

- update Module architecture if any binding contract/schema/security decision changed;
- update this plan only for sequencing/exit-gate changes approved by Cluster plan;
- update progress tracker with enabled features, unresolved deferred behavior, migration status, and production checks;
- record final contract versions and provider-owner assumptions.

### Acceptance Criteria

1. All production-enabled U-JI blockers are resolved.
2. No lifecycle has two owners.
3. No canonical shared operation is duplicated locally.
4. Conflicting transitions cannot corrupt state.
5. Duplicate commands/events/handoffs produce one effect.
6. Video/Calendar degradation cannot falsify interview source truth.
7. Privacy reruns and retention are correct/idempotent.
8. Required domain/audit/access evidence is complete and separated.
9. Sensitive telemetry is redacted.
10. Query/index performance is acceptable under repository-defined launch thresholds.
11. Migration/backfill rehearsal is safe.
12. Documentation/progress agree with production code.

### Exit Gate

PASS only if repository-standard full typecheck/lint/build succeeds; all Job Interview unit/integration/contract/E2E/RLS/security/concurrency/idempotency/privacy/provider-degradation/reconciliation/migration/performance suites pass; enabled architecture blockers are closed; no forbidden duplicate/provider/cross-domain repository code exists; and the CL-06 Feature 15 production-hardening gate passes.

# Module Integration Phase

Features **06–09** are the explicit Module integration phase. They prove Job Interview works correctly with its most important neighboring owners while keeping public contracts as the boundary.

Minimum bridges to prove:

```text
Identity actor
→ Role / Authority
→ Organization/Candidate owner facts
→ JobInterview source write
→ JobInterviewEvent + outbox
→ Candidate Application event/command boundary
→ Messaging ensureContextThread
→ Notification requestNotification
→ Candidate resume authorization → Media grant
→ Video Infrastructure JobInterviewVideoRoom
→ Calendar owner after U-CL06-16
→ Audit sensitive-access proof
→ Privacy owner executor
→ Ops failure visibility
```

Contract tests should prefer real interfaces when implemented. When the CL-06 build plan permits a fixture for an unavailable neighbor, the fixture must be versioned to the owner’s public contract and must not recreate the owner’s policy inside Job Interview.

# Module Hardening Phase

Feature **10** covers only Job Interview production risk. It must not become a vehicle for new product scope or generic infrastructure.

Hardening areas:

- schedule/cancel/complete/no-show/reschedule races;
- participant response/removal races if enabled;
- idempotent command replay;
- event/inbox replay;
- outbox/queue crash recovery;
- Video/Calendar outage and stale-result reconciliation;
- dependency unavailable/deny behavior;
- sensitive data access/audit;
- privacy/retention/cascade safety;
- telemetry redaction;
- migration/backfill compatibility;
- query/index performance;
- operational dead-letter/manual retry.

# Phase Summary

| **Phase** | **Name** | **Features** |
|---|---|---|
| 1 | Contracts and Source-of-Truth Foundation | 01 |
| 2 | Core Provider-Independent Interview Lifecycle | 02 |
| 3 | Public Reads and Hiring Dashboard Surface | 03 |
| 4 | Participant and Reschedule Domain Expansion | 04–05 |
| 5 | Collaboration and Delivery Handoffs | 06 |
| 6 | Calendar Integration | 07 |
| 7 | Privacy, Retention, Audit, and Evidence | 08 |
| 8 | Module Integration Contract Proof | 09 |
| 9 | Hardening and Production Verification | 10 |

**Total numbered features: 10**

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview.
2. Read root architecture and code standards if present.
3. Read Canonical Shared Operations Architecture/Registry.
4. Read CL-06 architecture and build plan.
5. Read `job_interview/module-architecture.md` and this implementation plan.
6. Read public-interface sections for every direct dependency used by the feature.
7. Read current Prisma schema/migrations and progress tracker.
8. Confirm all U-JI/U-CL06 blockers relevant to the feature are resolved or explicitly deferred outside the feature.
9. Confirm the previous Module feature exit gate passed and Cluster sequencing permits work.
10. Write the concise Required Feature Implementation Specification below for **this feature only**.
11. Implement only the feature’s In Scope work.
12. Run repository-standard quality checks and targeted tests.
13. Verify workflow/contracts without direct neighbor repository fallbacks.
14. Update progress.
15. Update architecture only when a binding decision legitimately changed.
16. Record unresolved risks/deferred work.
17. Stop if the exit gate fails.

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a short implementation specification containing:

- **Feature:** number and name;
- **Objective**;
- **Observable result**;
- **Cluster build-plan link**;
- **Dependencies**;
- **In scope**;
- **Out of scope**;
- **Owned data affected**;
- **Public contracts introduced/changed**;
- **Shared operations consumed**;
- **Permissions/compliance gates**;
- **Primary workflow**;
- **Provider integration** — owner and contract, or `none`;
- **Jobs/events/outbox/inbox**;
- **Idempotency/concurrency strategy**;
- **Error/failure behavior**;
- **Tests to add/run**;
- **Acceptance criteria**;
- **Documentation updates**;
- **Unresolved blockers**.

Do not generate all future feature specifications in advance. The current repository/progress state and latest architecture decisions must be consulted immediately before each feature.

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed:** number/name and result;
- **Files added**;
- **Files changed**;
- **Database changes**;
- **Migrations**;
- **Dependencies/packages added**;
- **Module public interfaces added/changed**;
- **Dependency public interfaces consumed**;
- **Canonical shared operations reused**;
- **Events/outbox/inbox/jobs added or changed**;
- **Provider adapter changes:** normally `none` in Job Interview; name owner if external Module changed through separate approved work;
- **Tests added/changed**;
- **Commands/checks run:** use repository-standard exact commands;
- **Manual/contract verification**;
- **Authorization/RLS verification**;
- **Privacy/audit verification** where applicable;
- **Documentation updated**;
- **Assumptions**;
- **Known failures**;
- **Remaining risks**;
- **Deferred work**;
- **Unresolved decisions encountered**;
- **Exit-gate result:** PASS/FAIL with evidence.

A completion report must not say PASS when required tests were skipped or a blocker was bypassed with a local implementation.

# Final Quality Check

Before treating the Module plan as implementation-ready, verify:

1. `JobInterview`/`JobInterviewEvent` have one owner.
2. Participant ownership is not treated as binding until U-CL06-14 is approved.
3. Exact transition/reschedule semantics are not invented around U-CL06-15.
4. Calendar implementation is blocked until U-CL06-16 is settled.
5. Job Interview never writes JobApplication lifecycle truth.
6. Job Interview is never implemented through Booking.
7. Video room/provider mechanics remain Video-owned.
8. Messaging/Notification/Resume/Media/Audit/Privacy/Ops truth remains with those owners.
9. Every canonical shared operation is consumed, not duplicated.
10. Shared mechanism / separate truth boundaries are explicit.
11. Every public mutation is validated, authorized, transaction-safe, concurrency-safe, and idempotent when retryable.
12. Every successful lifecycle mutation appends domain history.
13. Domain events, generic audit, sensitive access, and observability remain distinct.
14. External effects are post-commit, durable, retryable, and observable.
15. Provider adapters never become interview truth.
16. Privacy orchestration remains Privacy-owned.
17. Search remains projection and is not used for interview authority/source reads.
18. Every numbered feature has tests, acceptance criteria, and an exit gate.
19. Cluster sequencing links are explicit.
20. A coding agent can implement one feature without inventing ownership or generic infrastructure.

