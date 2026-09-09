# Admin Review / Compliance Hold Module Implementation Plan

## Core Principle

Implement the Module through narrow, verifiable slices:

```text
public or observable behavior
  -> validated command/query
  -> Hold-owned policy
  -> authoritative ComplianceHold write/read
  -> canonical shared-operation calls
  -> event/audit/notification effects
  -> tests
  -> exit gate
```

This plan is subordinate to the CL-09 `build-plan.md`. It does not change Cluster feature order or ownership. The base observable result is the canonical hold command/query contract and persisted lifecycle. A protected admin surface is introduced only where CL-09 Feature 08 requires it. No provider integration or artificial user-facing UI is invented.

The plan implements the confirmed base lifecycle `active -> released`. Automatic expiry, durable review claims/escalation, candidate/resume applicability, and immutable decision-history/snapshot scope remain conditional or deferred until the architecture decisions identified in `module-architecture.md` are accepted.

---

## Build Rules

1. Follow root architecture, root code standards, Canonical Shared Operations, CL-09 architecture/build plan, and this Module's architecture.
2. Own only `ComplianceHold`, its reason/status vocabulary, hold applicability, hold lifecycle, release proof meaning, and Hold-specific review policy.
3. Consume source facts and target validation through approved public interfaces; never query or mutate foreign Prisma tables for convenience.
4. Reuse canonical actor, authority, step-up, idempotency, locking, lifecycle, outbox/inbox, audit, notification, privacy, queue, and observability operations.
5. Do not create local copies of shared infrastructure or consumer-local block truth.
6. Validate every command/query DTO at runtime. TypeScript types alone are not an input boundary.
7. Authorize server-side using trusted actor/system context and owner-supplied relationship facts.
8. Make lifecycle transitions and required side effects transaction-safe. Released/expired holds are terminal unless architecture explicitly changes.
9. Make command, event, job, audit, and notification effects idempotent under retries.
10. Fail closed when mandatory target/source validation, hold evaluation, release readiness, authority, or required evidence is unavailable.
11. Keep provider details behind provider-owning Modules. This Module owns no provider adapter or credential.
12. Use durable, retryable, observable jobs only for approved asynchronous behavior. No expiration worker exists until U-13 is accepted.
13. Every feature ends with exact tests and an exit gate. Do not begin the next feature until the gate passes or an accepted deferral is recorded.
14. Surface unresolved architecture rather than inventing target types, action scopes, review tables, expiry, permission keys, event names, or retention periods.
15. Update architecture only when a binding decision legitimately changes; update progress after every completed feature.

---

## Preconditions

### Hard platform dependencies

- Next.js/TypeScript/Prisma/PostgreSQL/Supabase foundation defined by root context.
- Current Prisma and migration history available for inspection.
- `resolveAuthenticatedActor` from Identity & Access.
- `authorizeResourceAction` from Role / Authority, or a contract-compatible test fake for isolated Module tests.
- canonical request/correlation context and safe structured logging.
- `executeIdempotentCommand`, approved database locking/CAS primitive, lifecycle transition plumbing, and transactional outbox.
- CL-09 Feature 01 audit interfaces `appendAuditEvent` and `recordSensitiveAccess` before production hold mutations/review reads.
- CL-09 Feature 02 operational context/telemetry interfaces before production operations.

### Blocking architecture decisions before Feature 01

CL-09 Feature 04 explicitly requires resolution of:

- PR-CL09-04 / U-10: one approved typed target representation, vocabulary, cardinality, and migration strategy;
- U-12: creation/requester/source/evidence/release provenance representation;
- U-14: semantic equivalence, idempotency, active uniqueness, and duplicate-race result;
- stable action/scope contract and reason/scope/action applicability policy sufficient for `evaluateComplianceHold`.

Feature 01 must not write a migration until these decisions are accepted in architecture. The physical schema may differ from the logical requirements, but a coding agent may not invent it.

### Neighbor interfaces

Production integration eventually requires owner contracts from:

- Identity & Access and Role / Authority;
- Audit / Event Ledger, Notification, Observability / Ops, and Privacy / Data Erasure;
- Payment / Payout / Tax;
- Trust Verification / Screening and Professional Eligibility;
- Job Compliance and Organization Hiring;
- Content Moderation & Legal Notice;
- Review / Dispute and Transaction / Order;
- Healthcare / Regulated Services;
- Sweepstakes / Prize and Gamification / Rewards;
- Candidate Application & Resume Privacy after U-15;
- Media / File Access for protected evidence where applicable;
- source public-readiness owners and Search for indirect projection reaction.

Owner interfaces may be represented by strict contract fakes during isolated Features 01-06. Fakes must use the published owner DTO and must not normalize an unresolved interface into permanent Module architecture.

### Conditional dependencies

- `claimWorkItem` and a Hold-owned review persistence ruling are required only for Feature 07's implementation branch.
- Privacy target vocabulary and approved retention rules under U-24 are required for Feature 08 production exit.
- Permanent event type names require the platform event contract/registry decision before they are frozen.
- No direct provider setup is required because this Module owns no provider.

---

# Implementation Phases

## Phase 1 - Source-of-Truth and Contract Foundation

### 01 Approved Hold Target, Provenance, and Idempotency Foundation

#### Objective

Align the `ComplianceHold` schema and versioned public contract foundation with the accepted CL-09 target, provenance, action-scope, and semantic duplicate rulings.

#### Observable Result

- Prisma validation and migration tests prove every new hold has one valid approved primary target.
- The schema can store required requester/source/evidence/idempotency and complete release provenance without raw sensitive payloads.
- Concurrent semantic duplicates can be prevented by the accepted database strategy.
- Versioned command/query DTOs can represent target, scope, source, actor/system, evidence references, and safe results.

#### Cluster Build-Plan Link

Supports CL-09 Feature 04, "Reusable Compliance Hold Gate," specifically its blocking decisions PR-CL09-04, U-10, U-12, and U-14. It depends on the audit/request-correlation and telemetry spine established by CL-09 Features 01-02.

#### Dependencies

- Explicit acceptance of the four blocking architecture decisions listed in Preconditions.
- Current Prisma schema and migration history.
- Root migration standards.
- `executeIdempotentCommand`, database constraint/lock support, and common command/decision envelope contracts.
- Target-owner validation contract shape.

#### In Scope

- inspect existing nullable `userId`, `professionalProfileId`, `orderId` and consumer `blockedByHoldId` relations;
- implement the accepted target/cardinality migration and safe compatibility/backfill path;
- add approved logical provenance: requesting Module, actor/system, source decision/record/event, evidence references, requested scope, idempotency/semantic identity, release reason/source decision, and concurrency/version support;
- create required indexes and database constraints;
- define versioned internal/public DTO schemas for request, release, get/list, and gate evaluation;
- document how consumer associations relate to central target truth;
- add schema and contract tests.

#### Out of Scope

- hold creation/evaluation/release application behavior beyond contract/repository scaffolding;
- automatic expiry or `expiresAt` without U-13;
- review assignment/claim/escalation fields without U-11;
- candidate/resume target support without U-15;
- provider fields/statuses, raw evidence payloads, foreign domain state, universal target repository;
- adding new hold reasons merely to match a provider/source status.

#### Module-Owned Data

- `ComplianceHold` physical schema and approved fields/relations;
- existing `ComplianceHoldReason` and `ComplianceHoldStatus` unchanged unless separately approved;
- approved uniqueness/index/concurrency representation;
- no new Hold history/review/snapshot model unless a separate ruling explicitly authorizes it.

#### Public Interfaces

- DTO/validation schemas for `requestComplianceHold`, `releaseComplianceHold`, `getComplianceHold`, `listActiveComplianceHolds`, and `evaluateComplianceHold`;
- typed primary target, source/evidence reference, scope/action, safe hold view, command result, and gate decision contracts;
- target-owner `validateOwnedTargetReference` port consumed by later features.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `executeIdempotentCommand` | Platform application infrastructure | Contract includes key/fingerprint/result; Hold defines semantic identity and conflict | `holdIdempotency` store |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Shared persistence | Schema supports accepted lock/CAS strategy; Hold defines key/conflict | In-memory mutex/custom CAS |
| `validateOwnedTargetReference` | Target owner | Port shape represents approved target validation; Hold controls allowed target/action classes | Cross-domain Prisma lookup |
| `returnDecisionResult` | Shared contract, if accepted | Align safe gate result; Hold retains policy | Universal readiness engine |
| `sanitizeTelemetryMetadata` | Observability/Audit policy | Validate bounded/safe source/evidence metadata | Local redactor |

#### Domain Logic

- Exactly one approved primary target is required.
- Target type/ID is opaque to the repository except for accepted validation/indexing; foreign lifecycle truth is not imported.
- Semantic identity follows the accepted U-14 rule and must distinguish genuinely different source decisions/scopes.
- Same idempotency key with a different normalized fingerprint is a conflict.
- `reason` is not the blocked action; scope/action applicability is separately represented.
- `admin_hold`/`other` require structured source/provenance.
- Released proof must be representable without rewriting source-domain truth.

#### Authorization / Compliance

No direct client write path is introduced. DTOs carry typed actor/system context only from server resolution. Provenance/evidence fields are minimized and sensitivity-classified. Schema must not force PHI, tax details, identity documents, resumes, message bodies, provider payloads, or secrets into Hold records.

#### Database / Transaction Behavior

- migration includes safe forward/backfill/rollback-or-forward-fix plan;
- enforce target cardinality at the database boundary where feasible plus domain validation;
- enforce idempotency and accepted active semantic uniqueness at the database boundary;
- add target + status and queue-filter indexes;
- add version/CAS support if accepted;
- preserve existing hold IDs/history and validate ambiguous legacy rows before enforcing constraints;
- no destructive cleanup of ambiguous rows without an approved remediation report.

#### Events / Jobs

No event is emitted and no worker is added in this schema slice. Migration/backfill tooling is bounded, cursor-based, dry-run first, idempotent, and observable if needed.

#### Provider Integration

None. Reject provider-native fields/types.

#### UI / Admin Surface

None.

#### Failure Behavior

- architecture decision missing -> feature blocked, no migration;
- legacy zero/multi-target row -> report for manual remediation, do not guess;
- duplicate legacy semantic holds -> deterministic report, no silent merge/delete;
- migration constraint/index failure -> rollback/forward-fix according to reviewed plan;
- unsupported target/source type -> contract validation failure.

#### Tests

- Prisma schema validation and migration apply/rollback-or-forward-fix tests;
- legacy backfill dry-run/idempotency fixtures;
- database target-cardinality and uniqueness tests;
- DTO parsing/rejection/size-limit tests;
- same-key/different-payload contract test;
- public DTO privacy/redaction snapshot tests;
- ensure consumer-owned foreign rows are not mutated.

#### Documentation Updates

- record accepted PR-CL09-04/U-10/U-12/U-14 rulings in root/CL-09/Module architecture;
- update Prisma ownership map and public contract documentation;
- record migration/backfill decisions and progress.

#### Acceptance Criteria

1. The accepted schema represents one primary target, scope, source, requester, idempotency, and release proof.
2. No ambiguous target can be newly persisted.
3. The database participates in duplicate/concurrency prevention.
4. Existing holds are preserved or explicitly quarantined for reviewed remediation.
5. Public contracts contain no foreign/provider/raw-sensitive types.

#### Exit Gate

Run and pass repository-standard format/lint/typecheck, Prisma validate/generate, migration tests on an empty and representative legacy database, contract tests, and schema ownership review. Do not begin Feature 02 until architecture updates and migration review are approved.

---

### 02 Hold Lifecycle, Applicability Policy, and Repository

#### Objective

Implement the Module-owned domain policies and repository primitives needed to create, evaluate, and release holds without exposing public mutations yet.

#### Observable Result

Tests can construct an approved hold request, persist one active hold through the repository, resolve applicable holds for a target/action, and enforce `active -> released` while rejecting every prohibited transition.

#### Cluster Build-Plan Link

Supports CL-09 Feature 04's lifecycle, reason/scope/action mapping, duplicate semantics, and release-is-not-approval requirements.

#### Dependencies

- Feature 01 exit gate.
- Accepted reason/scope/action applicability matrix and safe reason exposure policy.
- shared lifecycle, idempotency, and database concurrency primitives.

#### In Scope

- `validateHoldRequestPolicy`;
- `deriveHoldSemanticKey` using the accepted rule;
- `imposeComplianceHold` domain construction;
- `resolveApplicableActiveHolds` and `buildHoldGateDecision`;
- `assertHoldReleasePolicy` and `transitionComplianceHold`;
- repository methods scoped only to `ComplianceHold`;
- safe DTO mapping/redaction;
- unit and database tests.

#### Out of Scope

- public server actions/routes;
- foreign source adjudication;
- audit/notification delivery implementations;
- expiry, reopen, claim/escalation;
- direct manipulation of `blockedByHoldId` associations;
- global lifecycle/readiness engine.

#### Module-Owned Data

- `ComplianceHold` read/write behavior;
- Hold reason/scope/action policy and stable Hold-safe reason namespace;
- no additional model.

#### Public Interfaces

Internal repository/domain interfaces only in this feature. Public DTOs from Feature 01 remain unchanged.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `transitionLifecycleState` | Shared mechanism | Hold supplies `active -> released` and terminal rules | Direct status setter/global policy table |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Shared persistence | Repository uses accepted strategy; Hold defines conflicts | Process lock |
| `executeIdempotentCommand` | Platform | Domain service integration seam; semantic key remains Hold-owned | Module store |
| `returnDecisionResult` | Shared contract if accepted | Map applicability to stable result | Universal compliance evaluator |

#### Domain Logic

- only `active` holds block;
- exact target and action/scope must match approved applicability policy;
- source reason alone is never enough to infer scope;
- a missing mandatory dependency produces unavailable, not allowed;
- released/expired are terminal;
- release requires a structurally valid source decision and does not update/approve it;
- equivalent replay preserves original proof.

#### Authorization / Compliance

Domain policy accepts already resolved actor/authority decisions; it does not read roles. Safe mapper redacts sensitive reason/source/note fields according to viewer context.

#### Database / Transaction Behavior

- repository exposes transaction-bound create, lookup, applicable-active query, and compare-and-set transition;
- no cross-domain joins;
- target/status query uses Feature 01 indexes;
- transition update predicates on active/current version and returns current row on conflict;
- test transaction rollback leaves no partial hold/outbox placeholder.

#### Events / Jobs

Define internal event fact objects only if needed for later outbox wiring; do not freeze permanent event identifiers. No worker.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- invalid reason/target/scope/source -> validation result;
- semantic duplicate -> existing/replay or conflict per accepted policy;
- stale/terminal transition -> typed conflict;
- mandatory policy/version unavailable -> unavailable/manual review;
- unexpected repository failure -> sanitized internal/retryable classification.

#### Tests

- table-driven reason/scope/action applicability;
- every allowed and forbidden transition;
- release-is-not-source-approval test with foreign contract fake;
- terminal/reopen prohibition;
- safe DTO exposure by viewer class;
- repository indexes/query correctness;
- concurrent compare-and-set tests;
- no foreign repository imports.

#### Documentation Updates

Update Module architecture only if accepted policy changes target/action or lifecycle rulings; publish Hold reason-code/action-scope contract documentation and progress.

#### Acceptance Criteria

1. All lifecycle transitions go through one Hold-owned policy.
2. Applicability is deterministic, versioned, and unit-tested.
3. Repository reads/writes only Hold-owned data.
4. Released hold remains historical and cannot block/reopen.
5. No foreign source status is interpreted inside Hold policy.

#### Exit Gate

Pass domain unit, transition matrix, repository integration, concurrency, privacy/redaction, typecheck, and lint checks. A reviewer confirms no public path or foreign ownership leak exists.

---

## Phase 2 - Canonical Public Hold Lifecycle

### 03 Idempotent Hold Request Command

#### Objective

Expose `requestComplianceHold` as the only authorized path for source Modules/admin systems to create an active hold.

#### Observable Result

A contract consumer can request an approved hold, receive the created or replayed hold ID/status/scope, and prove that retries or concurrent equivalent requests do not create uncontrolled duplicates.

#### Cluster Build-Plan Link

Implements the request half of CL-09 Feature 04 and enables Moderation/Payment/Verification/Dispute/Prize/Reward integrations used by CL-09 Features 05-07 and 11.

#### Dependencies

- Features 01-02.
- `resolveAuthenticatedActor`, `authorizeResourceAction`, target-owner validation.
- canonical idempotency/lock/outbox infrastructure.
- audit interface from CL-09 Feature 01 and telemetry from Feature 02.

#### In Scope

- runtime DTO validation;
- trusted actor/system resolution and authorization;
- target-owner validation and minimized source-reference validation;
- idempotent/transaction-safe active hold creation;
- safe command result;
- required audit and created-event outbox intent;
- optional policy-driven notification request after commit;
- command contract tests with at least one source-owner fake.

#### Out of Scope

- rechecking KYC, tax, background, moderation, dispute, healthcare, prize, reward, or security facts;
- direct consumer association writes;
- admin review UI;
- release, expiry, claim/escalation;
- provider or notification delivery code.

#### Module-Owned Data

- `ComplianceHold(active)` and approved creation provenance;
- hold-created event fact/outbox payload once event identifier is approved.

#### Public Interfaces

- `requestComplianceHold` command and versioned request/result/error contract.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity & Access | Entry resolution; Hold identifies request action | Local session helper |
| `authorizeResourceAction` | Role / Authority | Before target write; Hold supplies source/target facts | Admin guard |
| `validateOwnedTargetReference` | Target owner | Before persistence; Hold controls supported types | Foreign lookup |
| `executeIdempotentCommand` | Platform | Wrap normalized command/transaction | Hold idempotency store |
| lock/CAS primitive | Shared persistence | Serialize semantic key | Mutex |
| `appendAuditEvent` | Audit | Record safe creation proof | Hold audit table |
| `publishDomainEvent` | Outbox | Publish created fact transactionally | Fire-and-forget emitter |
| `requestNotification` | Notification | Optional post-commit alert | Direct sender |
| telemetry operations | Observability | Safe outcome/timing/failure | Local logger/Sentry |

#### Domain Logic

1. Resolve actor/system and validate request schema.
2. Authorize hold request for target/source context.
3. Ask target owner to validate the approved target and source version.
4. Validate reason/scope/source/evidence shape without adjudicating the foreign fact.
5. Derive semantic key and run idempotent transaction.
6. Create one active hold or replay approved equivalent result.
7. Persist required outbox; request audit/notification using approved coupling.

#### Authorization / Compliance

Only approved source Modules/system actors or authorized admins may request. `admin_hold`/`other` need structured provenance. Sensitive reason/source detail is omitted from unauthorized results, events, logs, and notifications.

#### Database / Transaction Behavior

Idempotency claim/result, semantic lock/constraint, hold insert, and required outbox commit atomically. A target/source/audit failure before commit creates no hold. Post-commit optional notification failure does not duplicate the hold and is retried through its owner.

#### Events / Jobs

Emit the approved hold-created event via outbox. No Module worker. Event consumers deduplicate independently.

#### Provider Integration

None; source owners translate provider state before calling.

#### UI / Admin Surface

No UI. Server/admin actions later call this command.

#### Failure Behavior

- invalid/unsupported target, reason, scope, source, evidence -> reject;
- unauthenticated/forbidden -> reject without existence leakage;
- target owner unavailable -> retryable unavailable, no hold;
- same idempotency key/different payload -> conflict;
- equivalent concurrent create -> replay/existing or deterministic conflict;
- audit/outbox required failure -> roll back according to approved coupling;
- notification failure -> committed hold remains, delivery retry/ops visibility.

#### Tests

- DTO/security/authorization tests;
- target-owner contract tests;
- same-key replay/different-payload conflict;
- simultaneous equivalent create integration test;
- transaction rollback and outbox atomicity;
- audit payload minimization;
- no source-domain mutation;
- E2E-style contract test from one source Module fake.

#### Documentation Updates

Publish finalized command contract/event identifier and update progress; update architecture only if accepted implementation changes a binding contract.

#### Acceptance Criteria

1. Direct client/foreign repository inserts are unnecessary and denied.
2. One request produces one authoritative active hold.
3. Equivalent retries replay safely.
4. Source evidence is referenced, not copied.
5. Audit/event/notification effects are safe and correlated.

#### Exit Gate

Pass command unit/integration/contract, concurrency, authorization, privacy payload, outbox/audit, typecheck, lint, and production build checks applicable to the repository. Demonstrate a source-owner fake requesting and replaying a hold.

---

### 04 Authoritative Hold Evaluation Queries

#### Objective

Expose Hold truth reads and `evaluateComplianceHold` so every consuming workflow can obtain a safe authoritative action-gate decision without raw-table access.

#### Observable Result

A consumer receives allowed while no applicable active hold exists, denied with safe hold references while one applies, and unavailable when mandatory evaluation cannot be completed. Released holds no longer block.

#### Cluster Build-Plan Link

Implements the evaluation half of CL-09 Feature 04 and the central anti-duplication rule used by CL-09 Features 11-12.

#### Dependencies

- Features 01-03.
- accepted applicability/action-scope policy.
- actor/authority for protected truth reads; trusted internal caller policy for gate decisions.
- target-owner/source-version query only where the approved contract requires it.

#### In Scope

- `evaluateComplianceHold`;
- protected `getComplianceHold`;
- protected `listActiveComplianceHolds` with bounded cursor/filtering;
- safe DTO/redaction and decision/error contracts;
- consumer contract package and tests;
- telemetry for latency/outcomes without sensitive dimensions.

#### Out of Scope

- consumer lifecycle changes;
- local `isBlocked` cache/boolean;
- public Search indexing of holds;
- review queue/detail context;
- source compliance re-evaluation;
- consumer `blockedByHoldId` synchronization.

#### Module-Owned Data

Read-only use of `ComplianceHold`; no new record/projection.

#### Public Interfaces

- `evaluateComplianceHold`;
- `getComplianceHold`;
- `listActiveComplianceHolds`.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity | Protected reads/internal context | Local actor helper |
| `authorizeResourceAction` | Role / Authority | Hold detail/list and sensitive reason access | Raw role check |
| `returnDecisionResult` | Shared contract if accepted | Safe allowed/denied/unavailable envelope | Local incompatible readiness shape |
| `queryOwnerFacts` | Source owners | Only if required for target/source validation/version | Foreign joins |
| request context/log/metric | Observability | Latency/outcome/correlation | Local telemetry |

#### Domain Logic

- match approved primary target and named action/scope;
- consider only authoritative `active` holds;
- apply versioned Hold-owned reason/scope/action mapping;
- return safe reason codes/hold IDs appropriate to caller;
- do not infer source facts or source resolution;
- mandatory dependency/evaluation failure returns unavailable, not allowed;
- `get/list` truth reads are not substitutes for action evaluation.

#### Authorization / Compliance

Internal consumers receive only the fields needed to gate their action. Admin/source detail requires separate permission. Sensitive source/reason/note fields are redacted. Avoid existence leakage in not-found/forbidden behavior.

#### Database / Transaction Behavior

- indexed target/status/applicability query;
- bounded cursor pagination;
- no unbounded cross-domain join;
- evaluation provides aggregate/policy/source version for consumer consistency where approved;
- document consumer responsibility to compose evaluation with its own transaction closely enough to prevent TOCTOU bypass.

#### Events / Jobs

None. Evaluation is a read. High-volume denials may emit metrics, not domain events. Material access/denial audit is policy-driven, not automatic audit spam.

#### Provider Integration

None.

#### UI / Admin Surface

None in this feature.

#### Failure Behavior

- unsupported target/action -> validation denial;
- unauthorized detail/list -> forbidden;
- mandatory repository/owner dependency unavailable -> unavailable/retryable;
- malformed/stale policy version -> manual review/unavailable;
- no applicable active hold -> allowed, never inferred from consumer association alone.

#### Tests

- table-driven applicability and safe reason exposure;
- allowed/denied/unavailable decision contracts;
- active versus released/expired behavior;
- target/action mismatch;
- authorization and IDOR/existence-leak tests;
- pagination/index/query performance tests;
- consumer contract test proving no raw Hold table access;
- evaluation under concurrent release/create transaction fixtures.

#### Documentation Updates

Freeze gate decision/reason code contract and consumer integration guidance; update progress and any approved policy version.

#### Acceptance Criteria

1. Gate decision is authoritative, deterministic, safe, and versioned.
2. Released holds never block.
3. Consumers need no raw Prisma access or local block boolean.
4. Dependency failure cannot silently allow a mandatory action.
5. Query paths are bounded and indexed.

#### Exit Gate

Pass unit, contract, database, authorization, concurrency/read-consistency, performance-budget, typecheck, lint, and build checks. Demonstrate a consumer allowed -> held/denied -> released/allowed flow using public contracts only after Feature 05 is complete; at this gate, prove active/released fixtures.

---

### 05 Authorized Hold Release, Proof, and Event Effects

#### Objective

Expose `releaseComplianceHold` as the sole idempotent transition from active to released, with complete approved proof and no foreign source mutation.

#### Observable Result

An authorized source/admin supplies a release-ready source decision and receives release actor/reason/time/source proof; gate evaluation changes from denied to allowed; replay is stable and conflicting terminal transitions are rejected.

#### Cluster Build-Plan Link

Completes CL-09 Feature 04 and supplies the release path verified in CL-09 Feature 11. Uses audit/telemetry from Cluster Features 01-02.

#### Dependencies

- Features 01-04.
- approved release authority/readiness contract and physical proof fields.
- actor/authority; optional step-up only if policy approved.
- idempotency, lock/CAS, lifecycle, outbox, audit, notification interfaces.

#### In Scope

- runtime release DTO validation;
- hold/source lookup through owner interfaces;
- authority and optional approved step-up;
- idempotent, concurrency-safe `active -> released` transition;
- release proof persistence;
- hold-released outbox fact, audit request, safe optional notification;
- gate result verification after release.

#### Out of Scope

- changing or approving source state;
- admin override without approved conditions;
- reopen/replacement automation;
- expiry;
- provider calls;
- direct consumer link/status update.

#### Module-Owned Data

- `ComplianceHold.status=released`;
- approved release actor/system, time, reason, source decision reference/version;
- hold-released event fact/outbox.

#### Public Interfaces

- `releaseComplianceHold` command/result/error;
- approved hold-released event contract;
- existing queries reflect terminal state.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| actor/authority/step-up | Identity; Role | Resolve, authorize, optionally assure; Hold defines release context | Local admin/MFA checks |
| `queryOwnerFacts` or source readiness port | Source owner | Confirm release-ready decision/reference | Hold re-adjudication/direct DB read |
| idempotency + lock/CAS | Platform/shared DB | Serialize hold ID and replay result | Local store/mutex |
| `transitionLifecycleState` | Shared mechanism | Hold supplies active->released proof rules | Direct update |
| `appendAuditEvent` | Audit | Safe release proof | Hold audit table |
| `publishDomainEvent` | Outbox | Transactional released fact | Fire-and-forget |
| `requestNotification` | Notification | Safe status alert | Direct delivery |
| telemetry/failure | Observability | Dependency/transition outcome | Local failure/log table |

#### Domain Logic

- source owner decides that its condition permits release; Hold verifies the signed/typed decision reference and policy requirements;
- authorized admin may release only under explicitly approved source/override policy;
- same semantic release against released hold returns original result;
- different release basis or release against expired hold returns conflict;
- no transition reactivates a terminal hold;
- if a new stop is needed, requester creates a new hold with new provenance.

#### Authorization / Compliance

Release permission is distinct from view/request. Step-up is not assumed; use it only when the approved matrix says so. Source decision and reason detail are minimized in public/audit/notification output.

#### Database / Transaction Behavior

Use hold-ID lock or versioned CAS. Idempotency claim/result, status/proof update, and required outbox commit atomically. Required audit coupling follows the approved Audit contract. Exactly one terminal transition wins in release/expiry tests, even though expiry remains disabled.

#### Events / Jobs

Emit approved hold-released event via outbox. Notification delivery may be queued by its owner. No Hold worker.

#### Provider Integration

None. Provider/source outage becomes owner-interface unavailable.

#### UI / Admin Surface

No UI in this feature; admin action integration is Feature 06.

#### Failure Behavior

- missing/invalid source decision -> validation/not-release-ready;
- unauthorized/step-up required -> denial;
- source owner unavailable -> retryable failure, hold remains active;
- stale version or competing terminal transition -> conflict with current safe state;
- same semantic replay -> success with original proof;
- audit/outbox required failure -> transaction fails/rolls back;
- notification failure -> release remains committed and delivery retries separately.

#### Tests

- release authority/source-readiness contracts;
- release-is-not-source-approval assertion;
- same-key replay/different-basis conflict;
- two concurrent releases;
- simulated release/expiry race policy (expiry path cannot run until approved);
- transaction/outbox/audit coupling;
- safe event/audit/notification payloads;
- evaluation denied before and allowed after release;
- no consumer/source foreign mutation.

#### Documentation Updates

Freeze release DTO/event contract, authority/readiness rules, audit mapping, and progress. Record any deferred admin override/step-up issue.

#### Acceptance Criteria

1. Only Hold owner changes status.
2. Complete approved release proof is stored.
3. Source truth is unchanged.
4. Retry/concurrency behavior is deterministic.
5. Gate result stops blocking after commit.

#### Exit Gate

Run full request/evaluate/release workflow, unit/integration/contract/concurrency/authorization/audit/event/notification payload tests, Prisma validation, typecheck, lint, and build. Demonstrate no local consumer block state.

---

## Phase 3 - Protected Hold Review Surface

### 06 Safe Hold Queue, Detail, and Admin Actions

#### Objective

Provide the Hold-owned portion of the CL-09 admin experience: bounded active/released hold lists, safe detail/review context, and authorized request/release actions without claiming a universal or persistent review lifecycle.

#### Observable Result

An authorized reviewer can filter/view holds, see source-owner minimized context or an explicit unavailable state, request/release through public commands, and produce sensitive-access/audit proof. Unauthorized users cannot enumerate or reveal sensitive hold/source details.

#### Cluster Build-Plan Link

Implements the Admin Review / Compliance Hold portion of CL-09 Feature 08, "Moderation, Hold, and Audit Administrative Review Surfaces."

#### Dependencies

- Features 01-05.
- CL-09 Features 01, 02, 04 and Role / Authority policies.
- owner-safe summary/redaction contracts for the target/source types displayed.
- Media signed-access contract only when evidence files are required.
- `recordSensitiveAccess` and audit viewer linkage.

#### In Scope

- protected server-rendered/route admin list and detail surfaces following repository conventions;
- `listComplianceReviewQueue` as bounded projection over holds;
- `assembleComplianceReviewContext` using owner public interfaces;
- safe loading/empty/unavailable/redacted/conflict/error states;
- request/release actions invoking public Module commands;
- pagination/filter indexes verification;
- audit/sensitive-access and telemetry;
- accessibility and component/E2E tests.

#### Out of Scope

- universal admin shell outside Module/Cluster responsibility;
- durable assignment, claim, lease, escalation, SLA, priority lifecycle without Feature 07 acceptance;
- cross-domain Prisma joins;
- raw PHI, tax/KYC, resume, private message, identity document, provider payload, or full legal evidence display;
- direct file URLs/provider clients;
- audit viewer implementation owned by Audit.

#### Module-Owned Data

No new source model. Queue is a read projection over `ComplianceHold`. Public admin actions mutate through Features 03/05 only.

#### Public Interfaces

- protected `listComplianceReviewQueue`;
- protected `assembleComplianceReviewContext`;
- existing `get/request/release` contracts;
- owner-specific review-summary ports.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| actor/authority/step-up | Identity; Role | Route, query, action, evidence authorization | UI-only guard/local MFA |
| `queryOwnerFacts` / `validateOwnedTargetReference` | Source/target owners | Bounded minimized review summaries | Cross-domain repository |
| `recordSensitiveAccess` | Audit | Allow/deny/redact/block protected reads | Screen-specific log |
| `appendAuditEvent` | Audit | Reviewer mutations through commands | Admin audit helper |
| Media access interface | Media | Short-lived access after owner authorization | Signed URL/storage code |
| `requestNotification` | Notification | Optional review status alerts | Direct sender |
| telemetry operations | Observability | Safe UI/server error diagnostics | Local logger |

#### Domain Logic

- queue shows active/released status and approved safe filters; it does not imply an assignment claim;
- detail starts from Hold source truth and composes owner summaries independently;
- owner unavailable is displayed as unavailable; no direct DB fallback;
- reason/source/note/evidence fields follow viewer-specific redaction;
- request/release forms submit to canonical commands and surface stale conflicts.

#### Authorization / Compliance

Protect routes and server actions separately. General admin capability is insufficient for source-sensitive material; source owner authorizes/redacts. Sensitive reads call `recordSensitiveAccess`, including denied/redacted outcomes where policy requires. Export/download is separately authorized and audited.

#### Database / Transaction Behavior

Queries are cursor-paginated, bounded, indexed, and do not join foreign tables. Mutations reuse Feature 03/05 transactions. No UI-specific source table/cache is created.

#### Events / Jobs

No new Hold event/job. Existing request/release effects apply. Owner-summary calls are synchronous or use existing owner projections; no custom fan-out queue.

#### Provider Integration

None.

#### UI / Admin Surface

- queue/list: status, safe reason category, approved target label/type, age, source Module, release state, safe filters;
- detail: hold/provenance/release proof, owner-safe target/source summaries, redaction/unavailable state, correlated audit link if authorized;
- actions: request/release with confirmation and conflict refresh;
- no claim/assignee/escalation controls unless Feature 07 implements them.

#### Failure Behavior

- not found/forbidden are presented without unsafe existence leakage;
- owner summary unavailable -> partial safe page with unavailable marker;
- stale hold -> conflict and refresh, no blind retry;
- sensitive access log failure follows approved fail-closed policy for protected evidence;
- command failure preserves current truth and displays safe correlated error.

#### Tests

- route/server-action authorization and IDOR;
- component states and redaction;
- owner-summary contract/unavailable behavior;
- sensitive-access audit completeness;
- pagination/filter/index behavior;
- accessibility/keyboard/focus/destructive confirmation;
- E2E reviewer list -> detail -> release -> refreshed status;
- test that no assignment/lease claim is shown or stored.

#### Documentation Updates

Document admin routes/actions, redaction matrix, owner-summary contracts, and progress. Update architecture only for accepted exposure/authority decisions.

#### Acceptance Criteria

1. Every admin write uses a public Hold command.
2. Every foreign context read uses an owner contract.
3. Sensitive views are owner-authorized/redacted and audited.
4. Queue/detail is bounded and accurately describes derived state.
5. No universal admin/review truth exists.

#### Exit Gate

Pass component, route/action authorization, contract, sensitive-access, accessibility, E2E, typecheck, lint, and build checks. Manually verify empty/loading/unavailable/redacted/conflict states.

---

### 07 Review Claim and Escalation Decision Gate

#### Objective

Resolve the claimed manual review assignment/escalation capability without inventing a universal review schema: either implement an approved Hold-owned claim/escalation lifecycle using the shared mechanism, or explicitly defer it and preserve the derived queue from Feature 06.

#### Observable Result

One of two recorded outcomes exists:

1. **Accepted implementation:** eligible reviewers can atomically claim/reassign/escalate a Hold review with persisted proof and concurrency protection; or
2. **Accepted deferral:** the product clearly exposes only an unassigned derived queue and no interface claims lease/assignment/escalation behavior.

#### Cluster Build-Plan Link

Supports CL-09 Feature 08 and PR-CL09-06/U-11; hardening is later verified in CL-09 Feature 12.

#### Dependencies

- Feature 06.
- Explicit architecture decision on U-11: review record owner/model/status/priority/assignment/escalation/due semantics.
- Acceptance of `claimWorkItem` for shared claim/lease mechanics if implemented.
- Role / Authority reviewer-eligibility contract and Notification for assignment/escalation alerts.

#### In Scope

If accepted: approved schema/migration, claim/release/reassign/escalate commands, queue/detail projection changes, optimistic/lease conflict behavior, audit/notification/events if approved, and tests. If deferred: remove/disable any ambiguous UI/API, document the limitation, and add tests proving no false assignment/claim semantics.

#### Out of Scope

- universal `AdminReviewCase`;
- merging ModerationCase, JobComplianceCheck, healthcare, verification, dispute, or foreign review truth;
- invented SLA/deadline/priority/escalation policy;
- automatic expiry of the underlying hold;
- source compliance adjudication.

#### Module-Owned Data

Only the explicitly approved Hold-specific review record/fields. The shared claim/lease mechanism remains infrastructure. If deferred, no new data.

#### Public Interfaces

If accepted: Hold-specific claim, release/reassign, escalate, and query contract names approved with the ruling. Exact names must not be invented by this plan. If deferred: no new interface.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `claimWorkItem` | Proposed shared work-queue/locking | Atomic claim/lease; Hold owns eligibility/duration/escalation | `claimReview`, `lockHold` |
| lock/CAS/lifecycle | Shared persistence | Review version/transition races; Hold owns graph | Ad hoc locks |
| actor/authority | Identity; Role | Reviewer eligibility/actions | Local reviewer-role check |
| audit/notification | Audit; Notification | Claim/reassign/escalation proof/alerts | Local log/direct sender |
| telemetry | Observability | Claim conflicts/age/escalation operation | Local queue telemetry |

#### Domain Logic

Implementation branch must define valid review states/transitions, lease expiry, same-reviewer replay, reassignment authority, escalation destination, and relation to active/released hold. Releasing a hold must not be implied by closing/escalating review. Deferral branch must use no placeholder state that suggests persistence.

#### Authorization / Compliance

Reviewer eligibility and escalation permission are distinct. Source-sensitive context remains owner-authorized. Claiming review grants no automatic access to PHI/financial/resume/private evidence.

#### Database / Transaction Behavior

If implemented, claim/update uses database uniqueness/row lock/CAS and audit/outbox in the approved transaction pattern. No in-memory lease. Migration/backfill is safe for existing holds. If deferred, no migration.

#### Events / Jobs

Only approved claim-expiry/escalation job/event contracts. Claim lease expiry may use the shared scheduler but must not expire the `ComplianceHold`. Dead letters remain observable.

#### Provider Integration

None.

#### UI / Admin Surface

If implemented: visible assignee/lease/version/escalation state and conflict refresh. If deferred: no claim/assignee/escalation controls or misleading labels.

#### Failure Behavior

- missing architecture approval -> deferral outcome, not improvised implementation;
- ineligible/stale/double claim -> typed denial/conflict;
- notification failure -> review truth remains committed, retry externally;
- released hold while review claimed -> approved transition/closure behavior, never silent hold rewrite;
- owner context unavailable -> review may remain claimed but evidence access shows unavailable.

#### Tests

If implemented: lifecycle unit tests, two-reviewer claim race, lease/reassign/escalation, authority, audit/notification, migration, UI/E2E. If deferred: contract/UI tests prove absent claim/escalation semantics and derived queue remains accurate.

#### Documentation Updates

Record the accepted U-11/PR-CL09-06 outcome in CL-09 and Module architecture/build/progress files. Publish review contracts only if implemented.

#### Acceptance Criteria

1. The architecture outcome is explicit.
2. No universal review record is created.
3. Implemented claims are database-concurrency-safe and do not grant source-data access.
4. Review state never replaces or releases the hold automatically without the release command.
5. Deferred UI/contracts make no false capability claim.

#### Exit Gate

Architecture review approves either implementation or deferral. For implementation, pass migration, transition, concurrency, authorization, audit/notification, UI/E2E, typecheck, lint, and build. For deferral, pass absence/derived-queue tests and record the accepted deferral before Feature 08.

---

## Phase 4 - Privacy, Retention, and Export Participation

### 08 Hold Privacy Enumerator, Retention Facts, and Executor

#### Objective

Make Hold-owned data participate in Privacy-owned discovery, retention, erasure/anonymization, and export without creating a local privacy workflow or inventing retention law.

#### Observable Result

A Privacy job can enumerate a subject's target/requester/releaser-linked holds, receive explicit approved retention facts, execute an allowed disposition idempotently, and obtain a minimized result/export contribution.

#### Cluster Build-Plan Link

Implements the Hold portion of CL-09 Feature 10, "CL-09 Privacy, Retention, and Export Executors."

#### Dependencies

- Features 01-07 outcome.
- Privacy / Data Erasure protocol and authorized job/system actor.
- resolution of U-24 Privacy target vocabulary and approved Hold retention/anonymization policy for production exit.
- shared anonymization and queue/idempotency primitives.
- Audit interfaces; Media/source-owner executor contracts if references/assets are involved.

#### In Scope

- `enumerateSubjectData` for Hold relations;
- `evaluateRetentionRequirement` returning approved owner facts;
- `executePrivacyInstruction` for Hold-owned fields/records;
- safe Hold export serializer;
- field-level mapping/version, idempotency, cursoring, result proof;
- contract/integration/privacy tests.

#### Out of Scope

- `PrivacyRequest`, job/target/exemption/bundle orchestration;
- choosing legal retention periods;
- hard-deleting required fraud/security/financial/legal proof;
- direct Media/source/provider deletion;
- global database crawler;
- modifying Audit records or foreign source evidence.

#### Module-Owned Data

- `ComplianceHold` personal/provenance fields under approved disposition;
- no local privacy job/exemption model.

#### Public Interfaces

- Hold implementation of `enumerateSubjectData`;
- Hold `evaluateRetentionRequirement`;
- Hold `executePrivacyInstruction`;
- Hold export serializer.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| `enumerateSubjectData` | Each owner via Privacy | Cursor through target/requester/releaser/source-subject links | Global crawler |
| `evaluateRetentionRequirement` | Hold facts + Privacy exemption truth | Return required/basis/until/minimum/anonymization | Local exemption/retain flag |
| `executePrivacyInstruction` | Privacy orchestrates; Hold executes | Validate job/target/idempotency; mutate only Hold | Local PrivacyRequest workflow |
| `anonymizePersonalFields` | Shared primitive | Apply approved versioned Hold field map | Ad hoc scrub SQL |
| idempotency/queue | Platform/shared | Replay executor result, durable batch execution | Local job framework |
| audit/access | Audit | Privacy action/export proof | Local privacy audit |

#### Domain Logic

- enumerate all approved subject relationships without leaking other subjects;
- return retention fact only from approved policy/source basis;
- unknown basis -> manual review/blocked, not invented exemption;
- preserve minimum relational/lifecycle proof when retained;
- anonymization must not falsify release/hold meaning or approved integrity evidence;
- export only subject-relevant safe fields and explain status/reason at an approved disclosure level.

#### Authorization / Compliance

Only authenticated/authorized Privacy orchestration may call executor mutations. Retention requires owner fact plus Privacy-owned exemption reference. Export/download remains protected, private, and access-audited.

#### Database / Transaction Behavior

- cursor-based enumeration with target/requester/releaser indexes as needed;
- idempotent compare-and-set privacy mutation;
- no delete cascade into foreign data;
- transaction stores approved result proof/outbox as required;
- dry-run mode before bulk mutation;
- retain/restrict behavior does not create a second lifecycle state unless explicitly approved.

#### Events / Jobs

Privacy owns orchestration/job. Hold may emit a minimized owner-execution fact only if the Privacy protocol requires it; exact name follows Privacy/event registry. Queue retry/dead-letter uses shared infrastructure.

#### Provider Integration

None. Media/source/provider resources are returned as references for their owners' executors.

#### UI / Admin Surface

No Hold-specific privacy UI.

#### Failure Behavior

- unauthorized caller -> denial;
- unsupported target/disposition -> terminal result;
- unapproved/unknown retention basis -> manual review/blocked;
- transient DB/dependency -> retryable failure;
- anonymization threatens proof/integrity -> retained/manual-review result;
- partial foreign/provider work -> explicit references/results handled by Privacy, not hidden.

#### Tests

- enumerator relationship/cursor coverage;
- retained/anonymized/erased/restricted/skipped/retryable/terminal fixtures under approved policy;
- idempotent executor replay;
- unauthorized caller and cross-subject isolation;
- export redaction/minimization;
- no local exemption/job truth;
- integration with Privacy contract fake/real interface;
- migration/index performance if new subject indexes are required.

#### Documentation Updates

Record U-24 target vocabulary/retention policy, field mapping version, executor/export contract, and progress. Update Module data inventory.

#### Acceptance Criteria

1. Privacy discovers all approved Hold subject relationships.
2. Hold returns facts; Privacy owns exemption/orchestration.
3. Mutations affect only Hold-owned data and preserve invariants.
4. Export does not leak unrelated/sensitive source data.
5. Unknown legal policy never becomes silent erase or permanent retention.

#### Exit Gate

Pass Privacy contract, enumerator/executor, retention, authorization, idempotency, export, performance, typecheck, lint, and build tests. Production exit additionally requires accepted U-24 policy; otherwise record an explicit non-production deferral.

---

## Phase 5 - Module Integration Proof

### 09 Cross-Module Hold Request, Gate, Release, and Review Contracts

#### Objective

Prove the Module works through real or production-equivalent public contracts with its most important source owners, consumers, and support rails without direct foreign data access.

#### Observable Result

Integrated workflows demonstrate source request -> active hold -> consumer denial -> source resolution -> authorized release -> consumer allowed, plus safe admin review and Privacy participation. Audit, notification, and observability effects are correlated and separately owned.

#### Cluster Build-Plan Link

Implements the Hold-specific journeys in CL-09 Feature 11, while re-verifying Cluster Features 04, 08, and 10.

#### Dependencies

- Features 01-08.
- production contracts or production-equivalent adapters for at least:
  - one financial/verification source and consumer;
  - Content Moderation & Legal Notice;
  - one Prize/Reward or Dispute workflow;
  - Audit, Notification, Observability, Privacy;
  - Role / Authority and Identity.
- Candidate/Resume integration remains excluded until U-15.

#### In Scope

- contract compatibility suites;
- source-owner request/release readiness flows;
- consumer gate integration without raw tables/local booleans;
- moderation-action-to-hold flow;
- at least one consumer association (`blockedByHoldId`) verified as non-authoritative linkage if used;
- admin safe context and access audit;
- event/outbox/inbox and notification/ops failure paths;
- Privacy executor integration;
- E2E fixtures and trace/correlation proof.

#### Out of Scope

- implementing neighboring Module business logic;
- provider/webhook adapters;
- direct consumer status/link mutations from Hold;
- candidate/resume flow before U-15;
- automatic expiry or unapproved review escalation;
- Search/Media direct operations.

#### Module-Owned Data

- `ComplianceHold` created/released by public commands;
- Hold events/outbox and approved review/privacy behavior;
- no cross-Module source record.

#### Public Interfaces

Verify `requestComplianceHold`, `evaluateComplianceHold`, `releaseComplianceHold`, get/list/review queries, events, and Privacy executor against consumers/owners.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| Hold request/evaluate/release | This Module | End-to-end canonical stop sign | Per-feature holds/raw reads/direct writes |
| actor/authority/step-up | Identity; Role | All entries | Integration auth bypass |
| owner target/source facts | Each owner | Validate/request/release/review | Foreign DB access |
| audit/access | Audit | Important actions/sensitive reviews | Local evidence logs |
| notification | Notification | Safe alerts | Direct provider delivery |
| outbox/inbox/idempotency | Platform | Reliable effectively-once events/effects | Fire-and-forget/ad hoc dedupe |
| telemetry/failure/queue | Observability | Correlated failure/retry/dead-letter | Local failures/queue truth |
| Privacy protocol | Privacy + Hold executor | Subject workflow | Local privacy orchestration |

#### Domain Logic

- source owner supplies why/when to request or release;
- Hold validates and owns status/applicability;
- consumer owns blocked-action behavior and any local association;
- released event prompts recomputation but never commands business approval;
- support rail failure does not transfer ownership or cause duplicate lifecycle effects;
- all integrated DTOs remain minimized and owner-versioned.

#### Authorization / Compliance

Verify source system actor identity, admin permissions, safe reason exposure, sensitive context owner authorization, access logging, and no blanket admin bypass. Hold gate is composed with consumer's other readiness/entitlement/consent checks, not substituted for them.

#### Database / Transaction Behavior

No cross-Cluster source table. Verify Hold transaction/outbox atomicity and consumer inbox/idempotency. Test consumer action transaction against hold decision according to approved consistency pattern. Foreign association changes, if any, occur only in consumer transactions.

#### Events / Jobs

- hold-created/released events delivered through outbox/inbox with duplicate delivery tests;
- optional notification work through Notification;
- technical failures/dead letters visible through Observability;
- no Hold provider job.

#### Provider Integration

No direct provider integration. Use source-owner normalized domain results and simulate provider-owner unavailable/retryable outcomes.

#### UI / Admin Surface

Verify Feature 06 reviewer journey against real owner summaries and access audit. Feature 07 claim/escalation appears only if implemented.

#### Failure Behavior

- source/target owner outage -> create/release unavailable and gate fail-closed where mandatory;
- duplicate event -> one consumer effect;
- Notification/telemetry outage -> no Hold truth corruption;
- consumer cannot reach gate -> consumer applies its approved fail-closed policy;
- owner contract version mismatch -> explicit incompatible/unavailable result, not raw DB fallback;
- partial integrated flow remains traceable by correlation ID.

#### Tests

- public contract compatibility for every selected neighbor;
- E2E source request/consumer deny/release/allow;
- moderation action -> hold -> consumer block;
- payout/prize/reward/dispute association non-authority test as selected;
- audit/event/notification separation and payload minimization;
- duplicate event/job replay;
- source/target/notification/observability outage fault injection;
- admin sensitive review -> AccessAuditLog;
- Privacy job -> Hold executor result;
- architecture test/lint prohibiting foreign Prisma imports if repository supports it.

#### Documentation Updates

Publish dependency compatibility matrix, event/DTO versions, selected integration fixtures, known unsupported targets/actions, and progress. Update owner public-interface docs where compatibility required a legitimate binding change.

#### Acceptance Criteria

1. Major workflows use only public contracts.
2. One owner exists for hold, source fact, consumer lifecycle, audit, notification, privacy, and operations truth.
3. Failure/replay paths are safe and traceable.
4. No consumer requires raw Hold access or a new block model.
5. Unsupported/unresolved integrations are explicit.

#### Exit Gate

Pass selected neighbor contract suites, integrated database tests, event replay/fault injection, reviewer/Privacy E2Es, typecheck, lint, schema validation, and production build. Architecture review confirms no direct foreign write/read or provider leakage.

---

## Phase 6 - Module Hardening and Production Verification

### 10 Hold Security, Concurrency, Privacy, and Launch Hardening

#### Objective

Harden the complete Module under retries, races, authorization attacks, sensitive-data constraints, dependency degradation, migration/backfill risk, and production load without adding new domain scope.

#### Observable Result

The hold lifecycle remains correct under concurrent requests/releases, duplicate event/job delivery, stale admin actions, source outages, unauthorized access, and privacy operations; operators can diagnose failures without seeing prohibited data; migrations/backfills have dry-run and recovery plans.

#### Cluster Build-Plan Link

Implements the Admin Review / Compliance Hold portion of CL-09 Feature 12, "CL-09 Security, Concurrency, Reconciliation, and Launch Hardening."

#### Dependencies

- Features 01-09.
- all launch-target decisions accepted or affected scope explicitly disabled/deferred.
- production-like database, queue/outbox/inbox, Audit, Notification, Observability, Privacy, and selected neighbor contracts.

#### In Scope

- final authorization/step-up/RLS review;
- DTO/IDOR/target-reference/security abuse testing;
- duplicate request/release and transition-race load/fault tests;
- outbox/inbox/audit/notification replay and partial-failure verification;
- source/target dependency outage/fail-closed behavior;
- admin redaction/sensitive-access completeness;
- privacy/retention/export verification;
- query/index/pagination/load testing;
- migration/backfill dry-run and recovery plan;
- contract version freeze/deprecation rules;
- production health/alerts/runbook for Hold operations;
- final E2E journeys.

#### Out of Scope

- automatic expiry unless U-13 was separately approved and implemented;
- durable review claim/escalation unless Feature 07 implementation branch passed;
- candidate/resume integration unless U-15 resolved;
- repeat-infringer, fingerprinting, or legal-policy automation;
- new provider selection or adapter;
- redesign of foreign lifecycle truth.

#### Module-Owned Data

- final `ComplianceHold` schema/index/constraint/version behavior;
- Hold policies/contracts/events/privacy mappings implemented in prior features;
- no new model solely to satisfy hardening.

#### Public Interfaces

Freeze/version all implemented commands, queries, events, review and Privacy contracts. Add compatibility tests and explicit deprecation policy for changed versions.

#### Shared Operations Used

| Operation | Owner | Invocation / local policy | Prohibited duplicate |
| --- | --- | --- | --- |
| idempotency, lock/CAS, lifecycle | Platform/shared DB | Fault/load verification of Hold semantic keys and transitions | Local fallback locks/stores |
| outbox/inbox/queue/retry | Platform/shared | Replay/dead-letter/lease verification | Module queue/event frameworks |
| actor/authority/step-up | Identity; Role | Final action/assurance matrix | Local auth bypass |
| audit/access | Audit | Completeness/immutability and sensitive read sampling | Local proof store |
| telemetry/failure/health | Observability | Safe diagnostics/alerts/runbook | Local logger/failure table |
| notification | Notification | Alert replay/no storm | Direct provider |
| privacy operations | Privacy + Hold | Retention/erasure/export proof | Local orchestration |
| `runDeadlineExpiration` | Shared scheduler | Only if U-13 implementation exists | Ad hoc cron |
| `claimWorkItem` | Shared review mechanism | Only if Feature 07 implemented | Competing claim lock |

#### Domain Logic

- no launch path depends on unresolved target/provenance/semantic uniqueness/action scope;
- all mandatory gate unavailability fails closed according to consumer policy;
- terminal hold history cannot be rewritten/reopened;
- a new source condition produces a new hold;
- safe reason/detail exposure is consistent across API/UI/event/audit/notification/telemetry;
- disabled unresolved features are unreachable and clearly documented.

#### Authorization / Compliance

- review logical action/permission matrix with Role / Authority;
- review step-up decisions with Identity/Security;
- verify service actors cannot bypass invariants;
- penetration-style IDOR/target probing, mass assignment, injection, oversized JSON, and unauthorized source Module tests;
- sample every sensitive review/export path for `AccessAuditLog` and redaction;
- verify retention policy and Privacy-owned exemptions.

#### Database / Transaction Behavior

- load-test target/status indexes and queue filters;
- verify semantic unique constraints under concurrency;
- verify CAS/lock and one terminal transition;
- verify idempotency/outbox atomicity and cleanup/retention policy;
- run migrations/backfills on production-like snapshot in dry-run then execution mode;
- document rollback/forward-fix, checkpoint, resume, and ambiguous-row manual remediation;
- no unbounded queries or cross-domain joins.

#### Events / Jobs

- duplicate/out-of-order event delivery and consumer idempotency;
- queue lease/retry/dead-letter tests only for implemented workers/executors;
- operational alerts route through Notification without recursive storms;
- if expiry exists, validate clock-controlled due selection, release/expiry race, retries, and dead letter;
- dead-letter/manual review never mutates hold unless owner command committed.

#### Provider Integration

None. Fault injection targets owner public interfaces and support rails, not raw providers.

#### UI / Admin Surface

Verify empty/loading/error/unavailable/redacted/stale/conflict states, accessibility, destructive confirmation, bounded export, session timeout, and no sensitive copy/download leakage. Claim/escalation controls are absent unless Feature 07 implemented.

#### Failure Behavior

- unauthorized/malformed/probing request -> safe denial;
- stale/duplicate/conflicting command -> deterministic replay/conflict;
- source/target outage -> unavailable/fail closed;
- optional telemetry outage -> business path follows approved degraded policy, never reports false success;
- required audit/evidence failure -> transaction/operation fails closed;
- notification outage -> durable retry/ops visibility without lifecycle rollback unless policy explicitly requires it;
- retry exhaustion -> visible dead letter/manual intervention with hold/source/correlation refs;
- migration anomaly -> stop/checkpoint/manual remediation, no guess.

#### Tests

- full unit, transition, contract, database, authorization/RLS, privacy, UI, and E2E suites;
- high-concurrency equivalent create and release races;
- same-key/different-payload and duplicate event/job replay;
- source/target/Audit/Notification/Observability/Privacy fault injection;
- redaction/secrets/PHI/tax/resume/provider payload fixtures;
- query/load/index/pagination tests;
- migration/backfill dry-run/resume/recovery;
- production build and schema validation;
- architecture boundary test for prohibited imports/duplicate helpers where feasible.

#### Documentation Updates

- freeze contract/event/policy versions;
- update architecture for accepted binding decisions only;
- update progress tracker and production runbook;
- record disabled/deferred unresolved scope;
- produce the required feature completion report with commands and evidence.

#### Acceptance Criteria

1. All prior feature gates are green or explicitly deferred by accepted architecture.
2. No launch path depends on unresolved target/provenance/uniqueness/action-scope/retention decisions.
3. Hold commands pass concurrency, idempotency, replay, and fault injection.
4. Admin/sensitive paths pass authority, redaction, access-audit, and accessibility checks.
5. Privacy/retention behavior is approved and tested.
6. Migrations/backfills are dry-run tested and recoverable.
7. Operational failures are actionable without replacing Hold truth or leaking sensitive data.
8. Critical source -> hold -> consumer -> release journeys pass.

#### Exit Gate

The Module is production-ready only when repository-standard formatting, lint, typecheck, unit, integration, contract, authorization/RLS, concurrency/load, privacy, Playwright/E2E, Prisma schema/migration, production build, and migration dry-run/recovery checks pass; the CL-09 Feature 12 gate is green; architecture/progress/runbook/completion report are updated; and every unresolved launch-affecting item is accepted or disabled.

---

## Module Integration Phase

Phase 5 Feature 09 is the dedicated integration phase. It must prove contracts rather than database reach-through.

Required integration evidence:

1. A source owner requests a hold through `requestComplianceHold` with typed source/target/version/evidence references.
2. A consumer calls `evaluateComplianceHold` and applies the result to its own action without creating hold truth.
3. The source owner later supplies release-ready proof; `releaseComplianceHold` alone changes status.
4. The consumer proceeds after re-evaluation and does not infer source approval.
5. Moderation can request a stop sign without replacing `ModerationCase`/`ModerationAction`.
6. A financial/prize/reward/dispute association, if used, is demonstrably non-authoritative.
7. Hold admin review uses owner-safe summaries and records sensitive access.
8. Audit, notification, operational telemetry, and Privacy results remain separately owned.
9. Duplicate commands/events/jobs and dependency outages preserve effectively-once Hold truth.

Any failed contract is fixed at the owning boundary. It is never bypassed by a direct Prisma read/write or provider call.

---

## Module Hardening Phase

Phase 6 Feature 10 is the dedicated hardening phase. It covers only relevant Module risks:

- target/cardinality and IDOR attacks;
- semantic duplicate creation;
- release/terminal transition races;
- idempotency and replay;
- event/outbox/inbox and optional job retry/dead-letter behavior;
- source/target/support-rail outage behavior;
- admin/service authority and optional approved step-up;
- sensitive reason/evidence redaction and access audit;
- Privacy enumeration, retention, anonymization, erasure, and export;
- telemetry payload safety;
- migration/backfill/legacy ambiguity;
- index/query/pagination performance;
- review claim/expiry hardening only when those conditional features exist.

Hardening does not authorize unresolved product, legal, retention, target, review, or expiry scope.

---

## Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Source-of-Truth and Contract Foundation | 01 Approved Hold Target, Provenance, and Idempotency Foundation; 02 Hold Lifecycle, Applicability Policy, and Repository |
| 2 | Canonical Public Hold Lifecycle | 03 Idempotent Hold Request Command; 04 Authoritative Hold Evaluation Queries; 05 Authorized Hold Release, Proof, and Event Effects |
| 3 | Protected Hold Review Surface | 06 Safe Hold Queue, Detail, and Admin Actions; 07 Review Claim and Escalation Decision Gate |
| 4 | Privacy, Retention, and Export Participation | 08 Hold Privacy Enumerator, Retention Facts, and Executor |
| 5 | Module Integration Proof | 09 Cross-Module Hold Request, Gate, Release, and Review Contracts |
| 6 | Module Hardening and Production Verification | 10 Hold Security, Concurrency, Privacy, and Launch Hardening |

**Total numbered features: 10.** Feature 07 has an explicit implementation-or-deferral gate because current evidence does not authorize persistent review claim/escalation truth.

---

## Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read Canonical Shared Operations.
3. Read CL-09 architecture and build plan.
4. Read this Module architecture and implementation plan.
5. Read public-interface sections for direct dependencies.
6. Confirm the prior Module and Cluster exit gates.
7. Confirm required Proposed Rulings are accepted or scope is explicitly deferred.
8. Write the concise feature implementation specification.
9. Implement only the numbered feature.
10. Run required quality checks.
11. Verify workflow and public contracts.
12. Update progress.
13. Update architecture only when a binding decision legitimately changed.
14. Record assumptions, known failures, remaining risks, and deferred work.

Do not begin the next feature after a failed gate unless the architecture owner records an explicit accepted exception or deferral.

---

## Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- Objective
- Observable result
- Cluster build-plan link
- Dependencies and prior exit gate
- In scope
- Out of scope
- Owned data affected
- Public contracts
- Shared operations consumed
- Permissions/compliance
- Primary workflow
- Provider integration, explicitly `none` for this Module unless architecture changes
- Jobs/events
- Idempotency/concurrency
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation updates
- Unresolved decisions and explicit deferrals

Generate this specification only for the feature about to be implemented. Do not pre-author specifications for all features.

---

## Required Completion Report

After implementing each numbered feature, report:

- Feature completed
- Cluster build-plan feature supported
- Files added
- Files changed
- Database changes
- Migrations and backfill behavior
- Dependencies added
- Module public interfaces added/changed
- Shared operations reused
- Events/jobs added
- Provider adapter changes, expected to be `none` unless architecture changes
- Tests added/changed
- Commands run
- Manual/contract/E2E verification
- Documentation updated
- Assumptions
- Accepted rulings relied upon
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

The report must distinguish a passed gate, a failed gate, and an explicitly accepted deferral. It must not describe an unavailable check as passed.

---

## Final Quality Check

Before declaring the Module plan complete or a feature production-ready, verify:

1. `ComplianceHold` and its lifecycle have exactly one owner.
2. No KYC, tax, payout, verification, healthcare, job-compliance, moderation, dispute, prize, reward, identity/security, candidate, or Order truth was absorbed.
3. Every shared operation is consumed rather than duplicated.
4. Shared lifecycle, locking, idempotency, outbox, audit, queue, review-claim, privacy, and snapshot mechanisms preserve separate Hold truth.
5. Request, evaluate, release, review, event, and Privacy contracts have clear ownership.
6. Cross-Module reads use owner interfaces and writes use owner commands/events.
7. No provider type/client/status became Hold truth.
8. `ComplianceHold`, domain events, `AuditEvent`, `AccessAuditLog`, and Observability records remain distinct.
9. Privacy orchestration/exemption truth remains Privacy-owned.
10. Search remains a projection and does not interpret raw hold reasons.
11. Module features align with CL-09 Features 04, 08, 10, 11, and 12.
12. Every numbered feature specifies tests, acceptance criteria, documentation, and an exit gate.
13. Conditional review/expiry/candidate/retention scope is accepted or explicitly disabled, never guessed.
14. A coding agent can execute the next approved feature without inventing architecture.

