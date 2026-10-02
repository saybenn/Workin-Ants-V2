# Content Moderation & Legal Notice Module Implementation Plan

## Core Principle

Implement this Module through narrow, verifiable slices:

```text
public/observable behavior
  -> validated command/query
  -> Module-owned moderation/legal policy
  -> authoritative Report / LegalNotice / ModerationCase / ModerationAction write/read
  -> canonical shared-operation calls
  -> target-owner / Audit / Notification / Ops effects
  -> tests
  -> exit gate
```

This plan is subordinate to the CL-09 build plan. It does not reorder CL-09 and does not authorize implementation of a Proposed Ruling or unresolved legal/schema decision merely because a later feature needs it.

The Module has genuine UI responsibilities for report/legal intake and protected moderation review. It does **not** need UI for every capability: contract, worker, privacy-executor, and reconciliation features are observable through their public interfaces and persisted behavior.

---

## Build Rules

1. Follow root architecture and code standards when present, then CL-09 architecture/build plan, then this Module architecture and plan.
2. This Module writes only `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction`, and explicitly approved future Moderation-owned records.
3. Consume other Modules only through public interfaces, events, or approved protocols.
4. Reuse Canonical Shared Operations; do not create Module-local copies of auth, authorization, idempotency, outbox, queue, retry, locking, hashing, request context, audit, search, notification, provider, or privacy infrastructure.
5. Every mutation validates actor/source, input, typed target, expected state, and idempotency where replay is possible.
6. Lifecycle transitions are DB-transaction-safe and use the owner transition graph; enum order is not a transition graph.
7. `ModerationAction` is decision truth, not execution status.
8. External target effects are owner-local, idempotent, correlated, retry-bounded, and observable.
9. Search stays a projection; Media stays file/storage owner; Notification stays delivery owner.
10. Provider clients stay in provider-owning Modules. This Module owns no direct R2, Typesense, SES/SMS/push, payment, or video provider adapter.
11. Privacy / Data Erasure owns privacy orchestration; this Module only enumerates and executes instructions against its own records.
12. Evidence-sensitive destructive/public-removal effects fail closed if required preservation proof cannot be obtained.
13. Legal sufficiency, deadlines, retention duration, repeat-infringer policy, and fingerprint thresholds are approved/versioned policy or remain disabled.
14. Every numbered feature has exact tests, documentation updates, acceptance criteria, and an exit gate.
15. A failed dependency must not be bypassed with a foreign Prisma read/write.
16. Current supplied Prisma fixes the earlier `ModerationTargetType` mapping concern; migrations still verify deployed DB history.
17. Do not use `media_access_grant` omission in older Cluster docs as a reason to remove the current enum value.
18. Feature completion reports must record assumptions, known failures, deferred architecture decisions, and exit-gate status.

---

## Preconditions

**CL-09-R016 — Protected evidence access.** The relevant context owner supplies SH-026 `authorizeContextualResourceAccess`; only after the required contextual authorization succeeds may Media / File Access provide SH-087 `issueSignedMediaUrl` for protected short-lived delivery. Where sensitivity/action policy requires proof, use SH-030 `recordSensitiveAccess`. Signing is not permission logic. CL-09 must not implement a signer, object-storage access service, or generic evidence-access bypass.

Protected-evidence feature tests must prove contextual authorization precedes signed delivery, required sensitive-access proof is requested, and no Moderation-owned signer or storage bypass exists.

### Hard platform prerequisites

- Next.js/TypeScript/Prisma/Supabase foundation according to root context.
- Database migration/test environment.
- Canonical Shared Operations registry available to coding agents.
- Request/correlation context and shared queue/event primitives available by the feature that first needs them.
- Cluster Feature 01 Audit interfaces (SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess`) available before evidence/admin review production integration.
- Cluster Feature 02 Observability interfaces available before durable async enforcement production integration.
- Identity & Access actor resolution.
- Role / Authority decision interface.
- Published or contract-compatible target-owner validation/fact interfaces for the target types enabled in each feature.

### Hard Module architecture decisions

The following must be settled before affected production features:

| Decision | Required before |
| --- | --- |
| `M-01` / `M-02` — approved Report and ModerationCase transition matrices | Features 02 and later transitions |
| `M-03` / `U-05` — legal-notice validation transition/provenance policy | Any transition to `valid`/`invalid` claiming legal sufficiency |
| `PR-CL09-02` / `U-04` — immutable moderation evidence proof/reference | Feature 04 evidence-sensitive decision path |
| `U-02` / CL-09-R007 — approved owner-local effect mappings, with primary targets kept separate | Feature 05 enables only supported owner effects; Order/payout blocking uses Holds and grant effects do not require an enum extension |
| `PR-CL09-03` / `U-06` — durable enforcement run/step correlation | Feature 05 production reconciliation |
| deterministic counter-notice/original-notice relationship policy; schema change only if approved | Feature 06 |
| `U-25` — approved legal deadline calculation/outcome policy | Feature 07 |
| `U-24` — Privacy target vocabulary + retention policy | Feature 09 production privacy behavior |
| `M-04` / CL-09-R009 — physical retention-safe deletion/FK strategy | Retained action cascade deletion is prohibited now; approve a replacement strategy before any case hard-delete/FK change |
| `M-05` — production external legal-intake identity/anti-abuse policy | Feature 03 public production launch |

### Dependencies that may initially be stubbed

For local Module slices, typed fakes may stand in for:

- Search SH-091 `requestSearchProjectionRefresh`;
- Media evidence/freeze/public-URL/signed-access contracts;
- Notification SH-041 `requestNotification`;
- Digital Goods / Video / Messaging / Marketplace / Gig / Hiring target-owner execution handlers;
- Admin Review / Compliance Hold commands;
- Observability failure/queue calls.

A stub must match the published owner contract. It must never emulate the neighbor by directly touching its tables.

### Explicitly not prerequisites

Do not wait for:

- repeat-infringer automation;
- content fingerprinting;
- legal correspondence center;
- a universal manual-review claim system.

Those are unresolved/deferred and are not required for the core moderation/legal MVP.

---

# IMPLEMENTATION PHASES

## Phase 1 — Contracts, Source Truth, and Intake

### 01 Module Contract and Lifecycle Foundation

#### Objective

Establish executable Module boundaries, DTOs, repositories, current-schema alignment, and approved transition-policy scaffolding without implementing downstream enforcement.

#### Observable Result

- The Module has versioned public/internal contract types for its current commands and queries.
- Repositories can read/write only `Report`, `LegalNotice`, `ModerationCase`, and `ModerationAction`.
- Current `ModerationTargetType` is verified as `@@map("moderation_target_type")` in the supplied schema and includes `media_access_grant`.
- A target-type/action policy registry exists at the domain level without foreign DB access.
- Report and ModerationCase transition matrices are explicitly documented/approved before mutation code relies on them.
- Tests prove foreign Module repositories/clients are not introduced.

#### Cluster Build-Plan Link

Preparation for **CL-09 Feature 03 — Moderation Report, Legal Notice, and Case Intake**. Must not advance Cluster sequencing beyond Feature 03 readiness.

#### Dependencies

- current Prisma schema;
- root code standards if present;
- Canonical Shared Operations;
- CL-09 architecture/build plan;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-123 `validateOwnedTargetReference` contract shape;
- SH-053 `transitionLifecycleState`;
- SH-052 `withOptimisticConcurrency`.

#### In Scope

- Module folder skeleton;
- public contract versioning convention;
- domain input schemas;
- repository interfaces/implementations for four owned models;
- safe DTO mapping;
- target/action compatibility table for current, confirmed target/action vocabulary;
- transition-policy files;
- migration-history check for `ModerationTargetType` before any migration;
- current schema evidence: CL-09-R017 corrects the earlier U-01 snapshot; migration compatibility remains separate;
- tests.

#### Out of Scope

- report/legal intake UI;
- downstream owner effects;
- evidence snapshot schema;
- enforcement run/step schema;
- repeat-infringer/fingerprint records;
- new target enum values;
- foreign Module repository implementations.

#### Module-Owned Data

- `Report`
- `LegalNotice`
- `ModerationCase`
- `ModerationAction`
- all eight owned enums, read as current schema facts

No schema change is required merely to create the Module boundary.

#### Public Interfaces

Define typed contracts, without necessarily exposing all routes yet:

- SH-101 `submitModerationReport`
- `getReportStatus`
- `submitLegalNotice`
- `getLegalNoticeStatus`
- `triageReport`
- `openModerationCase`
- `assignModerationCase`
- `getModerationCase`
- `listModerationQueue`
- `recordModerationAction`
- `queryActiveModerationRestriction`

Define internal contracts for:

- `evaluateModerationCase`
- `validateLegalNotice`
- `processCounterNotice`
- `deriveEnforcementPlan`

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-053 `transitionLifecycleState` | shared state-machine plumbing | transition service | Module transition graph | local generic state machine |
| SH-052 `withOptimisticConcurrency` | shared persistence | repository mutation | retry/conflict semantics | custom stale-write framework |
| SH-123 `validateOwnedTargetReference` | target owner | contract definition/tests | supported target/action set | universal target repository |
| SH-015 `returnDecisionResult` | proposed shared contract | DTO pattern only | moderation reason codes | global policy engine |

#### Domain Logic

- Treat `Report`, `LegalNotice`, `ModerationCase`, and `ModerationAction` as separate aggregates/history.
- Build target/action policy from confirmed enum values.
- Apply CL-09-R007: `pause_payout`/`freeze_order` use Holds where blocking is required; grant revocations are Digital Goods/Video owner-local effects. Enable only effects with approved owner mappings, without treating affected records as new primary moderation targets.
- Do not infer lifecycle edges from enum ordering.
- Preserve `ModerationAction` as append-style truth.

#### Authorization / Compliance

No protected operation is executed yet, but contract inputs must reserve trusted actor/context rather than client-supplied privilege fields.

#### Database / Transaction Behavior

- repositories expose only owner tables;
- no generic `deleteModerationCase` repository method;
- no case hard-delete path;
- use `updatedAt` as the available optimistic token unless a version-field architecture change is separately approved;
- document CL-09-R009: current `ModerationAction` cascade behavior is invalid for retained proof; require a later schema correction without choosing or implementing the replacement strategy here.

#### Events / Jobs

Define versioned event envelope dependency, but do not emit production events until source mutation features.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- contract/schema mismatch => fail build/tests;
- unresolved transition => no implementation of that transition;
- migration history mismatch => stop migration and document schema reconciliation.

#### Tests

- repository ownership tests;
- enum snapshot tests against current Prisma generation;
- contract serialization/version tests;
- target/action policy tests;
- transition policy rejects all unspecified transitions;
- no foreign Prisma model imports in Module repository layer where architecture linting permits.

#### Documentation Updates

- update this architecture only if current schema/migration history disproves the documented mapping;
- record approved transition matrices under Module architecture.

#### Acceptance Criteria

1. Four owner repositories exist and no foreign owner repository exists.
2. Public/internal DTOs do not expose raw Prisma records.
3. Current target enum/mapping is verified.
4. Transition policy is explicit, not enum-order driven.
5. Unsupported action/target combinations fail deterministically.
6. typecheck/lint/unit/schema checks pass.

#### Exit Gate

Feature 01 is complete only when the contract/repository/test boundary is stable and `M-01`/`M-02` are either approved for the transitions needed by Feature 02 or Feature 02 is explicitly blocked.

---

### 02 Report Intake, Triage, and Case Opening

#### Objective

Implement the first end-to-end report workflow: report submission -> source truth -> triage -> case open/assignment -> protected case/queue queries.

#### Observable Result

- A valid reporter/source Module can submit a report and receive ID/status.
- An authorized reviewer can triage it and open/assign a ModerationCase.
- `getReportStatus`, `getModerationCase`, and `listModerationQueue` return safe DTOs.
- Target validation occurs through owner contracts, not direct foreign Prisma.

#### Cluster Build-Plan Link

Implements the report/case portion of **CL-09 Feature 03**.

#### Dependencies

- Module Feature 01;
- CL-09 Feature 01/02 contracts or compatible fakes for Audit/Ops;
- Identity actor resolution;
- Role / Authority;
- target-owner validation contract;
- shared idempotency/request context.

#### In Scope

- SH-101 `submitModerationReport`;
- `getReportStatus`;
- `triageReport`;
- `openModerationCase`;
- `assignModerationCase`;
- `getModerationCase`;
- `listModerationQueue`;
- basic user report intake UI/API where product context supports it;
- admin moderation queue/case shell;
- audit/event hooks.

#### Out of Scope

- formal legal notice workflow except shared case data;
- evidence snapshot;
- ModerationAction;
- Search/Media enforcement;
- multi-report aggregation;
- repeat-infringer/fingerprint.

#### Module-Owned Data

- creates/updates `Report`;
- creates/updates `ModerationCase`;
- no new Module model.

#### Public Interfaces

- SH-101 `submitModerationReport`
- `getReportStatus`
- `triageReport`
- `openModerationCase`
- `assignModerationCase`
- `getModerationCase`
- `listModerationQueue`

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | report/reviewer protected entry | source compatibility | local auth |
| SH-002 `authorizeResourceAction` | Role / Authority | triage/open/assign/read | moderation action facts | `isModerator` |
| SH-123 `validateOwnedTargetReference` | target owner | before report/case persist | reportable targets | foreign DB lookup |
| SH-044 `executeIdempotentCommand` | platform | report/case create | semantic identity | local dedupe table |
| SH-053 `transitionLifecycleState` | shared | triage/case transitions | approved graph | ad hoc status writes |
| SH-052 `withOptimisticConcurrency` | shared | triage/assignment | stale behavior | manual timestamp check utility |
| SH-029 `appendAuditEvent` | Audit | reviewer/admin actions | safe refs | moderation audit table |
| SH-032 `createRequestContext` / SH-033 `writeStructuredLog` | Ops | entry/diagnostics | safe dimensions | local logger |
| SH-046 `publishDomainEvent` | platform outbox | report/case facts | event meaning | fire-and-forget |

#### Domain Logic

- `ReportSource` privilege values are assigned only by trusted server paths.
- `targetType + targetId` must be owner-validated.
- One current case may reference one optional triggering report. Do not aggregate multiple reports until `U-03`.
- `assignedAdminUserId` means assignment only; no lease/claim semantics.
- Case view obtains target summary through owner facts contract.
- Report and case transitions follow approved matrices only.

#### Authorization / Compliance

- ordinary User report path may require authentication according to product route;
- system/admin/law-enforcement sources cannot be selected by arbitrary clients;
- reviewer operations are server-authorized;
- rate limit intake;
- sensitive target summary may require SH-030 `recordSensitiveAccess`.

#### Database / Transaction Behavior

- report create + outbox event in one transaction where event is required;
- case create uses idempotent command boundary;
- triage/assignment uses optimistic concurrency;
- indexes already support target/status/assignee query patterns; verify query plans before adding indexes.

#### Events / Jobs

Potential outbox facts:

- report created;
- report triaged;
- case opened;
- case assigned.

Exact wire names/version are specified in feature implementation spec.

#### Provider Integration

None.

#### UI / Admin Surface

- basic report form/API;
- moderation queue;
- case detail shell with safe target summary and source records;
- no destructive action controls yet.

#### Failure Behavior

- invalid/unsupported target => validation error;
- owner unavailable => retryable dependency result or policy-approved unresolved-target path only if explicitly decided;
- duplicate idempotency key same fingerprint => replay;
- stale triage/assignment => conflict;
- unauthorized reviewer => deny without evidence leakage.

#### Tests

- unit report/source/target validation;
- contract target-owner resolver;
- integration report -> triage -> case;
- authorization;
- idempotency;
- concurrency;
- pagination/redaction;
- E2E report -> admin case visible.

#### Documentation Updates

- record approved report/case transition matrices;
- document any supported target-type subset narrower than enum.

#### Acceptance Criteria

1. Report intake persists only Report truth.
2. Case open/assignment uses only Module tables.
3. Target validation uses owner contract.
4. Queue/case view is protected and redacted.
5. Current single-report case limitation is explicit.
6. audit/event hooks use shared interfaces.
7. all tests pass.

#### Exit Gate

A report can be submitted, triaged, opened into a case, assigned, and reviewed safely with no foreign table access and no lifecycle transition outside the approved matrix.

---

### 03 Formal Legal Notice Intake and Structural Validation

#### Objective

Implement controlled formal notice intake and safe notice-status querying while keeping legal sufficiency/versioned legal rules explicitly gated.

#### Observable Result

- A controlled submitter/admin can create `LegalNotice(received)`.
- `getLegalNoticeStatus` exposes a safe status view.
- Structural validation can identify missing/malformed fields without claiming a notice is legally valid.
- Notice can be linked to a case using currently approved relationship rules.
- Production external intake is enabled only after `M-05`.

#### Cluster Build-Plan Link

Completes the legal-notice intake portion of **CL-09 Feature 03**.

#### Dependencies

- Module Features 01–02;
- target-owner validation;
- request context/idempotency;
- Notification receipt contract if acknowledgement is enabled;
- `M-05` for public external intake launch;
- `M-03/U-05` only for transitions claiming legal sufficiency, not for `received`.

#### In Scope

- `submitLegalNotice`;
- `getLegalNoticeStatus`;
- `validateLegalNoticeStructure`;
- controlled intake UI/API;
- optional case linkage/opening under approved cardinality;
- safe receipt notification request.

#### Out of Scope

- legal advice;
- automated `valid`/`invalid` based on guessed law;
- statutory deadlines;
- counter-notice restoration;
- legal correspondence timeline.

#### Module-Owned Data

- create `LegalNotice`;
- optional relation to `ModerationCase`;
- no new model.

#### Public Interfaces

- `submitLegalNotice`
- `getLegalNoticeStatus`
- internal `validateLegalNoticeStructure`
- `validateLegalNotice` remains policy-gated for legal sufficiency.

#### Shared Operations Used

- SH-123 `validateOwnedTargetReference`
- SH-044 `executeIdempotentCommand`
- SH-032 `createRequestContext`
- SH-034 `sanitizeTelemetryMetadata`
- SH-029 `appendAuditEvent` where required
- SH-041 `requestNotification` for receipt
- SH-046 `publishDomainEvent`

**Prohibited duplicates:** inbox-only legal handling, separate legal-report table, direct email delivery service.

#### Domain Logic

- notice type determines structural field schema;
- `dmca_counter_notice` is still a LegalNotice type, not a generic Report;
- no notice is declared legally valid without approved versioned policy/reviewer decision;
- `actionDueAt` remains unset or policy-driven; never calculate from hardcoded internet knowledge;
- submitter User is not required by current schema; external identity policy is separate.

#### Authorization / Compliance

- controlled intake anti-abuse/rate-limit;
- privileged internal notice sources are server-controlled;
- personal contact data is minimized and protected;
- no legal-advice copy generated by system beyond approved templates.

#### Database / Transaction Behavior

- LegalNotice create + outbox/receipt intent transaction as appropriate;
- idempotency at intake command;
- target validation before persist unless explicitly approved unresolved-target intake policy exists.

#### Events / Jobs

- notice received event class;
- no deadline worker;
- optional receipt Notification request.

#### Provider Integration

None directly.

#### UI / Admin Surface

- controlled legal notice form;
- safe status lookup for authorized submitter/admin;
- clear distinction from report form.

#### Failure Behavior

- structurally invalid => validation result;
- legal policy unavailable => intake may stay `received`; do not promote to `valid`;
- ambiguous target => reject/manual review per approved policy;
- Notification failure does not erase notice truth.

#### Tests

- notice type/structural schemas;
- external/internal source spoofing;
- idempotency;
- PII redaction in logs;
- status query authorization;
- report-vs-notice separation;
- E2E legal intake -> notice visible to reviewer.

#### Documentation Updates

- document external-intake policy when `M-05` approved;
- document validation policy/version if `U-05` resolved.

#### Acceptance Criteria

1. LegalNotice is persisted separately from Report.
2. Legal intake does not depend on email inbox state.
3. Structural validation does not claim legal sufficiency.
4. no deadline is invented.
5. target and personal-data security tests pass.

#### Exit Gate

Formal notice intake is production-safe at the structural/source-truth level; transitions requiring legal sufficiency remain disabled until approved policy exists.

---

## Phase 2 — Adjudication and Evidence

### 04 Evidence-Preserving Moderation Decisions

#### Objective

Allow an authorized reviewer to inspect safe case context, preserve required evidence, evaluate a case, and record a `ModerationAction` without claiming downstream execution completion.

#### Observable Result

- Reviewer sees case + owner-composed target summary + protected evidence.
- Evidence-required actions cannot be committed/dispatched until preservation proof exists.
- A new `ModerationAction` records the decision.
- `queryActiveModerationRestriction` exposes the resulting moderation decision to consumers.
- Evidence remains privately accessible to authorized reviewer after a target is hidden in test fixtures.

#### Cluster Build-Plan Link

Implements **CL-09 Feature 05 — Evidence-Preserving Moderation Decisions**. Cluster Feature 04 Hold must already be available if the selected decision requests a hold.

#### Dependencies

- Module Features 01–03;
- Cluster Audit/Ops/Hold interfaces;
- accepted `PR-CL09-02/U-04` or an explicit approved alternative evidence proof;
- Media private evidence storage/access contract;
- SH-072 `hashCanonicalPayload`;
- approved action/evidence-required matrix;
- approved legal policy only for decisions that claim legal sufficiency.

#### In Scope

- `evaluateModerationCase`;
- evidence-required policy;
- approved evidence snapshot/reference implementation;
- `recordModerationAction`;
- `queryActiveModerationRestriction`;
- protected reviewer decision UI;
- Audit/sensitive-access hooks;
- outbox enqueue point for Feature 05.

#### Out of Scope

- multi-owner enforcement result tracking;
- repeat-infringer automation;
- fingerprinting;
- automatic deadlines.

#### Module-Owned Data

- append `ModerationAction`;
- update Report/LegalNotice/Case only through approved transitions;
- add Moderation evidence proof/reference model **only if PR-CL09-02 is explicitly accepted with schema spec**.

#### Public Interfaces

- `recordModerationAction`
- `queryActiveModerationRestriction`
- protected `getModerationCase`
- evidence reference read/create contract
- internal `evaluateModerationCase`

#### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-102 `resolveModerationTarget` | proposed registry/owner resolvers | reviewer context | visible fields/actions | universal repo |
| SH-104 `preserveEvidenceSnapshot` | proposed evidence mechanism | pre-action gate | what evidence proves | Audit blob |
| SH-072 `hashCanonicalPayload` | shared crypto | snapshot | canonical fields | local SHA |
| SH-030 `recordSensitiveAccess` | Audit | evidence read | sensitivity/outcome | local access log |
| SH-002 `authorizeResourceAction` | Role | reviewer/action | allowed moderation action | ad hoc admin checks |
| SH-014 `requireStepUpForSensitiveAction` | Identity | if designated | high-risk action matrix | local MFA |
| SH-053 `transitionLifecycleState` | shared | status changes | owner graph | raw status assignment |
| SH-052 `withOptimisticConcurrency` / SH-051 `acquireAggregateLock` | shared | decision race | conflict semantics | in-memory lock |
| SH-029 `appendAuditEvent` | Audit | decision proof | safe refs | moderation audit table |
| SH-046 `publishDomainEvent` / SH-047 `enqueueReliableJob` | platform | post-decision | event/job meaning | fire-and-forget |

#### Domain Logic

- evaluate action target compatibility;
- calculate evidence requirement from Module policy;
- preservation occurs before irreversible/public-removal dispatch;
- record action before downstream effect;
- prior action history is immutable;
- restoration/reversal is later action;
- `queryActiveModerationRestriction` composes current case/action truth and safe reason codes without exposing legal evidence.

#### Authorization / Compliance

- reviewer authorization;
- evidence view access audit;
- step-up only under approved security matrix;
- no AI final legal decision;
- legal-policy version required where legal sufficiency is asserted.

#### Database / Transaction Behavior

- evidence proof/reference and action transaction follows approved schema;
- case expected version checked;
- action append + allowed source status transition + outbox record in one transaction;
- no foreign state write.

#### Events / Jobs

- moderation action recorded fact;
- enqueue enforcement job for next feature;
- evidence preservation failure emits Ops technical failure, not action success.

#### Provider Integration

Media operations are called through Media public interface. No R2 SDK.

#### UI / Admin Surface

- reviewer decision controls;
- rationale;
- evidence references;
- explicit "preservation incomplete" block;
- protected evidence viewer through Media.

#### Failure Behavior

- evidence preservation unavailable => block evidence-sensitive action;
- stale case/target => conflict and re-evaluate;
- unauthorized evidence => deny + appropriate access evidence;
- unapproved legal policy => manual review/policy-not-configured.

#### Tests

- evidence-required matrix;
- snapshot/hash contract;
- stale case conflict;
- action immutability;
- access audit;
- no foreign mutation;
- E2E preserve -> action -> evidence remains private.

#### Documentation Updates

- accept/document PR-CL09-02 schema/contract before migration;
- update Module architecture with evidence proof meaning/retention fields.

#### Acceptance Criteria

1. Evidence-sensitive action cannot be recorded for dispatch without preservation proof.
2. action is immutable source truth.
3. evidence bytes remain Media-owned.
4. sensitive evidence access is audited.
5. active restriction query returns stable safe decision.
6. all tests pass.

#### Exit Gate

Feature 04 is green only when evidence proof architecture is accepted, action recording is concurrency-safe, and no destructive downstream dispatch can occur without required preservation.

---

## Phase 3 — Cross-Module Enforcement and Legal Restoration

### 05 Cross-Module Enforcement and Reconciliation

#### Objective

Reliably dispatch one recorded ModerationAction to the correct target owners and reconcile acknowledgments without copying their lifecycle truth.

#### Observable Result

For an approved action, the reviewer/system can determine which required effects are pending, acknowledged, completed, retrying, terminal/manual-review, or restored as **moderation orchestration correlation**, while each target owner's actual state remains authoritative.

#### Cluster Build-Plan Link

Implements **CL-09 Feature 06 — Cross-Module Moderation Enforcement and Reconciliation**.

#### Dependencies

- Module Feature 04;
- accepted `PR-CL09-03/U-06`;
- CL-09-R007 primary-target/effect separation and an approved owner contract for every enabled effect;
- shared workflow runner/outbox/queue/retry/idempotency;
- target-owner SH-103 `executeModerationDecision` handlers;
- Search, Media, Hold, Audit, Notification, Ops contracts.

**CL-09-R003 — Organization Hiring executor.** Moderation issues the decision; Organization Hiring executes supported effects against `Job` and `Organization` through SH-103 `executeModerationDecision` and returns execution evidence. Hiring validates owner-local transitions and retains every mutation to those records. Its retry-safe result must distinguish accepted, rejected, idempotently already applied, retryable failure, and terminal failure as supported by the eventual contract, within the canonical acknowledged/completed/failed/restored evidence boundary. Exact effect/result encoding remains for the owner contract; this does not create a competing operation or permit CL-09 database writes to Hiring.

The Organization Hiring provider-side contract/handler is a prerequisite for enabling Job/Organization effects in Module Feature 05 / CL-09 Feature 06, with bilateral proof in CL-09 Feature 11; no direct foreign-table fallback is permitted.

#### In Scope

- approved enforcement run/step correlation model/record if accepted;
- `deriveEnforcementPlan`;
- moderation enforcement worker;
- reconciliation worker;
- Search/Media/Messaging/Marketplace/Gig/Hiring/Digital Goods/Video/Hold dispatch contracts;
- partial-failure/admin visibility;
- restoration-compatible correlation.

#### Out of Scope

- foreign owner state machines;
- provider webhooks;
- direct Search/R2/payment/video operations;
- unruled repeat-infringer/fingerprint.

#### Module-Owned Data

- `ModerationAction` unchanged;
- approved enforcement run/step correlation only if PR-CL09-03 accepted;
- no copies of target status fields.

#### Public Interfaces

- dispatch entry point;
- SH-103 `executeModerationDecision` protocol envelope;
- enforcement status/query projection;
- reconciliation entry point.

#### Shared Operations Used

- SH-103 `executeModerationDecision`
- SH-105 `correlateEnforcementResult` — proposed, must be accepted
- SH-049 `orchestrateWorkflowSteps`
- SH-050 `reconcileWorkflowStatus`
- SH-046 `publishDomainEvent`
- SH-045 `deduplicateDomainEvent`
- SH-047 `enqueueReliableJob`
- SH-048 `executeRetryWithBackoff`
- SH-044 `executeIdempotentCommand`
- SH-091 `requestSearchProjectionRefresh`
- SH-012 `requestComplianceHold`
- SH-029 `appendAuditEvent`
- SH-041 `requestNotification`
- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`

**Prohibited duplicates:** direct foreign writes, local Search/R2 clients, local failure tables, custom queue/retry framework.

#### Domain Logic

- action -> required owner/effect mapping is Module policy;
- each step carries action ID, case ID, typed target, effect, source reason/reference, idempotency/correlation;
- target handler returns normalized result and owner state/evidence reference;
- correlation stores only execution evidence/status of the step, not copied business fields;
- required-step success rules are Module-specific;
- partial completion remains unresolved until reconciled/manual reviewed;
- restoration uses a new action and corresponding inverse/restore effects.

#### Authorization / Compliance

- dispatch originates only from a valid recorded action;
- no worker can invent an action;
- hold requests use Hold interface;
- sensitive target effects use owner authorization/context as required.

#### Database / Transaction Behavior

- action already committed before workflow dispatch;
- outbox/job creation durable;
- step correlation writes are idempotent;
- worker locks by run/step or action/effect key;
- no distributed transaction with target owner.

#### Events / Jobs

- enforcement worker;
- retry/backoff;
- dead-letter/manual-review;
- reconciliation worker;
- optional step-completed facts with minimized payload.

#### Provider Integration

None directly. Provider failures are normalized by target owner.

#### UI / Admin Surface

- case shows orchestration correlation separate from source target state;
- clearly label pending/partial/failed/restored;
- link to owner state where authorized.

#### Failure Behavior

- owner unavailable => retry if safe;
- owner terminal rejection => manual review/terminal step, not fabricated success;
- queue dead-letter => Ops-visible, case/action preserved;
- partial completion => do not mark overall effect complete unless Module reconciliation policy says required steps are satisfied;
- ambiguous owner-local effect mapping => feature cannot enable that effect; CL-09-R007 does not authorize inferring a new primary target.

#### Tests

- target-owner contract suite;
- duplicate dispatch;
- retry after partial success;
- dead-letter;
- Search de-index and Media freeze integration;
- hold request integration;
- no foreign Prisma write;
- reconciliation replay;
- restoration-ready correlation.

#### Documentation Updates

- document PR-CL09-03 accepted schema/contract;
- document approved owner-local mappings under CL-09-R007 without extending primary target vocabulary.

#### Acceptance Criteria

1. Every enabled effect is routed through an owner handler.
2. `ModerationAction` is unchanged after dispatch.
3. target owner is source truth for execution.
4. retries are idempotent.
5. technical failures are observable.
6. partial execution is explicit.
7. no direct provider/foreign DB access exists.

#### Exit Gate

All enabled enforcement actions pass owner-contract, retry, dedupe, partial-failure, and reconciliation tests. Any effect without an approved owner-local mapping remains disabled; CL-09-R007 resolves the primary-target/effect distinction only.

---

### 06 Counter-Notice and Restoration

#### Objective

Implement a deterministic counter-notice/restoration path that preserves original takedown/action history and uses the same owner-local enforcement protocol for restoration.

#### Observable Result

- A counter-notice can be submitted/processed against a deterministically identified original legal/case context.
- Reviewer can place the case/notice into approved waiting/review state.
- An approved restoration creates a new ModerationAction.
- Search/Media/other owner restoration effects are idempotent and reconciled.
- Original takedown evidence/actions remain visible.

#### Cluster Build-Plan Link

Implements the manual/approved-policy portion of **CL-09 Feature 07 — Counter-Notice, Restoration, and Approved Deadlines**.

#### Dependencies

- Module Features 03–05;
- deterministic original notice/case linkage ruling;
- approved counter-notice structural/transition policy;
- Notification;
- enforcement/restoration protocol;
- legal deadline policy is **not** required for manual approved restoration.

#### In Scope

- counter-notice submission/status contract;
- `processCounterNotice`;
- approved waiting/review transitions;
- restoration/rejection/escalation commands;
- restoration action/plan;
- notifications;
- admin timeline using existing notice/action/case records.

#### Out of Scope

- general legal correspondence;
- automated deadline calculation/expiry;
- repeat-infringer;
- legal advice.

#### Module-Owned Data

- additional `LegalNotice` of `dmca_counter_notice` type or approved relationship model if explicitly accepted;
- Case/Notice status transitions;
- new restoration/reject/escalate `ModerationAction`.

#### Public Interfaces

- counter-notice submission/status;
- `processCounterNotice`;
- `restoreModeratedContent`;
- reject/escalate command(s).

#### Shared Operations Used

- target validation;
- idempotent command;
- lifecycle transition;
- optimistic concurrency/lock;
- SH-103 executeModerationDecision;
- enforcement correlation;
- SH-091 requestSearchProjectionRefresh;
- SH-041 requestNotification;
- SH-029 appendAuditEvent;
- SH-047 enqueueReliableJob/retry.

#### Domain Logic

- never fuzzy-match a counter-notice to original notice;
- relationship must be deterministic through approved case/notice linkage;
- restoration does not delete or relabel original action;
- new restoration action drives owner restore commands;
- case/notice transition uses approved legal policy only.

#### Authorization / Compliance

- controlled submitter access;
- legal reviewer authorization;
- restricted case evidence hidden from submitter;
- notification delivery is not automatically legal receipt proof.

#### Database / Transaction Behavior

- counter-notice create/process idempotent;
- state transitions optimistic;
- restoration action + outbox atomic within this Module;
- no foreign mutation.

#### Events / Jobs

- counter-notice received/processed facts;
- restoration action dispatch;
- Notification requests.

#### Provider Integration

None directly.

#### UI / Admin Surface

- counter-notice intake/status;
- case timeline;
- restoration/reject/escalate controls;
- no deadline countdown until Feature 07 policy.

#### Failure Behavior

- ambiguous/no original relationship => reject/manual review;
- duplicate counter-notice => deterministic replay/conflict;
- partial restoration => unresolved correlation + retry/manual review;
- stale case => conflict.

#### Tests

- deterministic linkage;
- transition guards;
- idempotency;
- original action immutability;
- restoration owner handlers;
- E2E takedown -> counter -> restoration with Search/Media fixture.

#### Documentation Updates

- record approved counter-notice relation semantics;
- add schema only if explicitly ruled necessary.

#### Acceptance Criteria

1. Counter-notice relationship is deterministic.
2. original history remains immutable.
3. restoration uses owner contracts.
4. partial failure remains visible.
5. legal-policy assumptions are explicit/versioned.

#### Exit Gate

Manual/approved-policy counter-notice and restoration journey passes without requiring unapproved statutory timing.

---

### 07 Approved Legal Deadline Worker

#### Objective

Enable scheduled legal deadline handling only after `U-25` supplies approved policy for `actionDueAt` calculation and deadline outcomes.

#### Observable Result

With an approved policy fixture:

- notices receive policy-derived `actionDueAt`;
- scheduled scans identify due records;
- owner command is invoked idempotently;
- retry/dead-letter is visible;
- no legal rule exists inside scheduler plumbing.

If policy is absent, the worker remains disabled and tests prove it cannot run.

#### Cluster Build-Plan Link

Completes the automated-deadline portion of **CL-09 Feature 07**.

#### Dependencies

- Module Feature 06;
- `U-25` approved policy;
- shared scheduler/queue;
- Notification/Ops;
- approved LegalNotice transition matrix.

#### In Scope

- policy adapter/interface for deadline calculation;
- `actionDueAt` assignment under approved policy;
- legal deadline worker;
- retries/dead-letter;
- admin due/overdue indicator;
- policy-version correlation.

#### Out of Scope

- inventing statutory times;
- legal advice;
- generic scheduler framework;
- correspondence center.

#### Module-Owned Data

- `LegalNotice.actionDueAt`;
- allowed LegalNotice/Case transitions;
- no new job truth model.

#### Public Interfaces

- internal deadline-calculation decision;
- worker entry point;
- protected due-notice query if needed.

#### Shared Operations Used

- SH-055 `runDeadlineExpiration`
- SH-047 `enqueueReliableJob`
- SH-048 `executeRetryWithBackoff`
- SH-044 `executeIdempotentCommand`
- SH-053 `transitionLifecycleState`
- SH-041 `requestNotification`
- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`
- SH-029 `appendAuditEvent`

#### Domain Logic

- legal policy computes deadline and owner command meaning;
- scheduler only finds due records and dispatches;
- clock is injectable/test-controlled;
- manual override/change requires approved policy and audit.

#### Authorization / Compliance

- only approved policy version may schedule legal deadline;
- admin cannot arbitrarily backdate deadline without explicit command/policy.

#### Database / Transaction Behavior

- index/query by status + `actionDueAt` verified;
- worker claim/idempotency prevents double transition;
- state transition checks expected status/version.

#### Events / Jobs

- scheduled worker;
- bounded cursor batches;
- retries/dead-letter;
- operator alert on terminal failure.

#### Provider Integration

None.

#### UI / Admin Surface

- safe due/overdue indicator and policy version/reference.

#### Failure Behavior

- policy missing => disabled/policy_not_configured;
- stale notice => no automatic transition; re-evaluate;
- transient dependency => retry;
- terminal policy/data issue => manual review.

#### Tests

- clock-controlled deadline computation;
- due scan boundaries;
- duplicate worker execution;
- stale state;
- dead-letter;
- policy-missing disabled path.

#### Documentation Updates

- record U-25 policy/version source;
- update architecture with legal transition/deadline rules.

#### Acceptance Criteria

1. no hardcoded legal durations outside approved policy;
2. scheduler is generic plumbing;
3. deadline transition is idempotent and state-checked;
4. terminal failures are observable;
5. missing policy disables automation.

#### Exit Gate

Deadline automation is green only when approved policy fixtures and worker fault tests pass. Otherwise Feature 07 remains intentionally disabled without blocking manual Feature 06 workflows.

---

## Phase 4 — Review Surface and Privacy Participation

### 08 Moderation Administrative Review Surface

#### Objective

Provide the Module-owned moderator/legal review experience over source truth and owner-supplied context without creating a generic cross-platform admin repository or review lifecycle.

#### Observable Result

Authorized reviewers can:

- list/search moderation cases;
- inspect safe report/legal/action history;
- inspect protected evidence through owner access;
- assign case;
- record permitted decisions;
- see enforcement correlation/partial failures if enabled;
- process counter-notice/restoration;
- see deadline indicators if enabled.

#### Cluster Build-Plan Link

Implements the moderation-specific portion of **CL-09 Feature 08 — Moderation, Hold, and Audit Administrative Review Surfaces**.

#### Dependencies

- Module Features 02–07 as enabled;
- Role / Authority;
- Audit sensitive access;
- target-owner summary/evidence contracts;
- Hold/Audit screens remain owned by their Modules and are linked, not duplicated.

#### In Scope

- admin moderation queue;
- case detail;
- report/legal/action timeline;
- assignment;
- safe target summary;
- evidence viewer launch;
- decision/restoration controls;
- orchestration status display.

#### Out of Scope

- generic CL-09 admin shell if owned elsewhere;
- hold lifecycle UI implementation;
- audit viewer implementation;
- ops dashboard;
- universal review claim/lease model;
- legal correspondence center.

#### Module-Owned Data

Read/write current Module models through public commands only.

#### Public Interfaces

UI consumes existing Module commands/queries. No direct repository use from components.

#### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`
- SH-002 `authorizeResourceAction`
- SH-014 `requireStepUpForSensitiveAction` where approved
- SH-030 `recordSensitiveAccess`
- SH-029 `appendAuditEvent`
- request context/logging

#### Domain Logic

UI renders source truth and stable reason codes; it does not derive business decisions from raw neighboring data.

#### Authorization / Compliance

- server-side authorization on every route/action;
- evidence redaction;
- step-up for designated sensitive export/high-impact action;
- no hidden broad admin bypass.

#### Database / Transaction Behavior

None from UI directly; all mutations call application commands.

#### Events / Jobs

Display existing status; no new job framework.

#### Provider Integration

None.

#### UI / Admin Surface

This feature is the admin surface.

Required states:

- loading;
- empty;
- forbidden;
- target unavailable;
- stale/conflict;
- evidence unavailable;
- partial enforcement;
- retry/manual-review;
- policy-not-configured.

#### Failure Behavior

- stale action => refresh/re-evaluate;
- target owner unavailable => show degraded context, do not guess;
- evidence access denied => safe denial + audit;
- dependency version mismatch => fail safely.

#### Tests

- component/RTL;
- route/action authorization;
- redaction;
- sensitive-access audit completeness;
- owner target-summary contracts;
- Playwright reviewer journey.

#### Documentation Updates

- UI route/action map if root UI registry exists;
- permission action vocabulary.

#### Acceptance Criteria

1. components never access Prisma directly;
2. sensitive views are audited;
3. no generic cross-domain admin repository;
4. no unsupported claim/lease semantics;
5. reviewer E2E passes.

#### Exit Gate

Reviewer can execute all enabled Module workflows safely through public commands/queries, with access/redaction/concurrency behavior proven.

---

### 09 Privacy, Retention, and Export Executor

#### Objective

Make this Module a compliant participant in Privacy-owned workflows: enumerate moderation/legal subject data, provide retention facts, and execute approved erase/anonymize/export/retain instructions.

#### Observable Result

A Privacy integration test can:

- find a subject's Report/LegalNotice/Case/Action personal data;
- receive explicit retention facts;
- anonymize/erase allowed fields;
- retain required legal/security proof only via Privacy-owned exemption;
- export approved data;
- delegate evidence Media deletion/access changes.

#### Cluster Build-Plan Link

Implements this Module's portion of **CL-09 Feature 10 — CL-09 Privacy, Retention, and Export Executors**.

#### Dependencies

- Module source workflows;
- `U-24` approved privacy target vocabulary and retention policy;
- Privacy public contracts;
- Media privacy/deletion contract for evidence refs;
- Audit privacy proof.

#### In Scope

- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-095 `executePrivacyInstruction`;
- export serializer;
- field-level anonymization mapping;
- tests.

#### Out of Scope

- PrivacyRequest/job/exemption orchestration;
- inventing retention duration;
- direct R2 deletion;
- global DB crawling.

#### Module-Owned Data

- Report reporter/free-text metadata;
- LegalNotice submitter/rights-owner/contact/statement metadata;
- Case opener/assignee/summary/resolution;
- Action actor/note;
- approved evidence-reference metadata if present.

#### Public Interfaces

Implement Privacy-defined owner executor contracts.

#### Shared Operations Used

- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement`
- SH-095 `executePrivacyInstruction`
- SH-098 `anonymizePersonalFields`
- SH-029 `appendAuditEvent`
- SH-030 `recordSensitiveAccess`
- Media deletion/access owner contract

#### Domain Logic

- distinguish legal evidence required for retention from convenience data;
- return facts, not create exemption;
- anonymization must not falsify required action/case proof;
- if safe anonymization is impossible, return retention/manual-review fact;
- do not use `other` target vocabulary as a silent permanent architecture.

#### Authorization / Compliance

Only authenticated/authorized Privacy orchestration can invoke executor.

#### Database / Transaction Behavior

- owner-local mutations only;
- idempotent privacy instruction;
- preserve referential integrity;
- no case/action hard-delete while retained proof requires them.

#### Events / Jobs

Privacy owns orchestration/job. Module may emit owner-execution result/audit proof.

#### Provider Integration

Evidence/provider deletion delegated to Media/provider owner.

#### UI / Admin Surface

None required.

#### Failure Behavior

- unapproved retention basis => manual review, not invented exemption;
- anonymization breaks proof => retain/manual-review;
- Media deletion failure => return partial/retryable result to Privacy.

#### Tests

- enumeration completeness;
- erase/anonymize/retain fixtures;
- idempotency;
- export minimization;
- unauthorized executor call;
- evidence Media partial failure.

#### Documentation Updates

- record U-24 target vocabulary and approved retention policy;
- architecture field-level disposition matrix.

#### Acceptance Criteria

1. no local PrivacyRequest/Job/Exemption;
2. all Module-owned subject data is enumerable;
3. retention requires approved basis;
4. export is safe;
5. partial owner/provider failure is explicit.

#### Exit Gate

Privacy orchestration can complete this Module's approved targets with deterministic outcomes and no local privacy lifecycle.

---

## Phase 5 — Integration Proof and Production Hardening

### 10 Cross-Module Contract Verification

#### Objective

Replace contract fakes with production owner interfaces and prove launch-critical moderation/legal journeys end-to-end without foreign database access.

#### Observable Result

At minimum these journeys pass:

1. Report -> Case -> Action -> Search de-index acknowledgment.
2. Action -> Media freeze/public URL removal -> protected evidence remains available.
3. Action -> ComplianceHold -> affected owner action is blocked.
4. Digital asset action -> Digital Goods owner disable/revoke.
5. Course action -> Video owner disable/revoke.
6. Message/thread action -> Messaging owner restriction.
7. Counter-notice -> restoration -> Search/Media owner restore.
8. Privacy request -> Module executor -> retention/anonymization result.
9. Technical owner/worker failure -> Ops failure/queue visibility without changing moderation decision truth.

#### Cluster Build-Plan Link

Implements this Module's part of **CL-09 Feature 11 — Cross-Cluster Integration Verification**.

#### Dependencies

- Module Features 01–09;
- real owner interfaces for enabled target types;
- Cluster Audit/Hold/Ops;
- Notification/Privacy;
- approved event/queue versions.

#### In Scope

- production contract wiring;
- contract version compatibility;
- E2E/fault tests;
- remove test fakes from production path;
- integration documentation.

#### Out of Scope

- rebuilding owner logic;
- unsupported unresolved target/action effects;
- new providers/features.

#### Module-Owned Data

No new cross-Cluster source table.

#### Public Interfaces

Freeze/verify versions for:

- moderation commands/queries;
- SH-103 executeModerationDecision protocol;
- Search/Media/Hold/Notification/Audit/Ops/Privacy dependencies.

#### Shared Operations Used

- actor/authority;
- SH-091 `requestSearchProjectionRefresh`;
- SH-103 `executeModerationDecision`;
- SH-012 `requestComplianceHold`;
- audit/access;
- Notification;
- Ops;
- Privacy;
- idempotency/outbox/inbox/queue/retry.

#### Domain Logic

- one owner contract at a time;
- owner response semantics must map to documented Module orchestration statuses;
- no fallback to direct DB access if contract unavailable.

#### Authorization / Compliance

End-to-end actor/permission/evidence access checks. No privilege widening across boundaries.

#### Database / Transaction Behavior

No distributed transaction. Verify source decision and owner effects remain separately committed/reconciled.

#### Events / Jobs

Exercise outbox/inbox/retry/dead-letter in production-equivalent process boundaries.

#### Provider Integration

Indirect only through owner Modules.

#### UI / Admin Surface

Use existing moderation admin surface to inspect integrated state.

#### Failure Behavior

- owner unavailable => retry/manual review;
- contract version mismatch => fail deployment/contract tests;
- provider failure => target owner/Ops evidence, not direct moderation state rewrite.

#### Tests

- cross-Module contract suites;
- Playwright moderation E2E;
- async retry/dead-letter;
- privacy;
- owner provider-failure simulation.

#### Documentation Updates

- dependency contract versions;
- supported target/action matrix;
- production readiness checklist.

#### Acceptance Criteria

1. all launch-critical bridges use owner contracts;
2. no integration test uses foreign Prisma writes;
3. source decision and target execution truth remain separate;
4. retries/partial failures are observable;
5. enabled journeys pass.

#### Exit Gate

Production-equivalent integration suite is green for every target/action enabled for launch. Unsupported unresolved effects remain disabled.

---

### 11 Security, Concurrency, Reconciliation, and Launch Hardening

#### Objective

Harden this Module against destructive-action mistakes, stale decisions, replay, abuse, sensitive-data leakage, dependency degradation, and migration/retention risk without adding new domain scope.

#### Observable Result

- moderation/legal workflows remain correct under concurrency, retries, partial failures, and dependency outage;
- intake resists abuse/source spoofing;
- reviewer evidence is protected/audited;
- reconciliation can safely repair incomplete owner effects;
- migrations/backfills are dry-run tested;
- unresolved legal/product features are disabled rather than guessed.

#### Cluster Build-Plan Link

Implements this Module's portion of **CL-09 Feature 12 — CL-09 Security, Concurrency, Reconciliation, and Launch Hardening**.

#### Dependencies

All prior Module features and Cluster Feature 12 prerequisites.

#### In Scope

- final permission/step-up review;
- target IDOR review;
- input/JSON limits;
- rate limiting;
- stale-state/concurrency tests;
- idempotency/replay tests;
- queue lease/dead-letter tests;
- reconciliation dry run;
- migration safety;
- index/query performance;
- privacy/retention validation;
- telemetry redaction;
- E2E/fault injection.

#### Out of Scope

- repeat-infringer automation unless separately approved;
- content fingerprinting unless separately approved;
- general legal correspondence;
- new provider selection.

#### Module-Owned Data

Review all four current models plus accepted evidence/enforcement correlation records, if any.

#### Public Interfaces

Freeze versioned contracts and add compatibility/deprecation tests.

#### Shared Operations Used

- SH-002 `authorizeResourceAction`
- SH-014 `requireStepUpForSensitiveAction`
- SH-044 `executeIdempotentCommand`
- SH-051 `acquireAggregateLock`
- SH-052 `withOptimisticConcurrency`
- queue/retry/outbox/inbox
- telemetry sanitizer
- Audit/Access
- Search/Media/Notification/Hold/Privacy owner interfaces

#### Domain Logic

Security/concurrency checklist:

- duplicate report/legal intake;
- two reviewer transitions;
- double action;
- takedown/restoration overlap;
- case close with incomplete required effects;
- replay after partial completion;
- counter-notice replay;
- deadline worker replay if enabled.

#### Authorization / Compliance

- full action-permission matrix;
- step-up matrix;
- evidence redaction/export;
- legal policy/version availability;
- privacy retention approval;
- no launch path depends on U-07/U-08/U-09 or any other unresolved item.

#### Database / Transaction Behavior

- verify indexes for status/target/assignee/deadline/case action history;
- migration dry run and rollback/forward-fix;
- check current enum mapping against deployed DB;
- enforce CL-09-R009 as a hardening exit gate: tests must prove case hard deletion cannot cascade-delete retained `ModerationAction` proof; replacement FK/deletion design remains separate schema work;
- no unbounded joins/pagination.

#### Events / Jobs

- retry/backoff/dead-letter thresholds;
- worker lease/concurrency;
- outbox/inbox cleanup;
- reconciliation dry-run/bounded cursor;
- alert path through Notification/Ops.

#### Provider Integration

Faults injected through owner Module adapters, not direct clients.

#### UI / Admin Surface

- confirm destructive-action confirmation;
- stale/conflict/partial failure states;
- safe copy/download;
- accessibility;
- no accidental evidence leakage.

#### Failure Behavior

- fail closed for evidence-required destructive action and mandatory authorization/hold gates;
- optional telemetry may degrade without claiming success;
- missing legal policy => disable automated behavior;
- dependency degradation never authorizes direct DB bypass.

#### Tests

- full unit/integration/contract;
- security/authorization;
- concurrency/load;
- retry/dead-letter/replay;
- privacy retention;
- migration dry run;
- critical Playwright journeys;
- production build.

#### Documentation Updates

- progress tracker;
- architecture only for legitimate accepted decisions;
- dependency/public-interface version map;
- completion report;
- remaining unresolved/deferred register.

#### Acceptance Criteria

1. all prior gates green;
2. no launch behavior depends on an unresolved legal/schema decision;
3. migration/schema checks pass against production-like DB;
4. target/action permissions and IDOR tests pass;
5. action/enforcement concurrency/idempotency tests pass;
6. evidence privacy/audit tests pass;
7. queues and terminal failures are actionable;
8. privacy executor is approved/tested;
9. all critical E2E passes;
10. typecheck/lint/unit/integration/Playwright/schema/build pass.

#### Exit Gate

The Module is launch-ready only when all acceptance criteria pass and unresolved repeat-infringer, fingerprinting, correspondence, or unapproved legal automation remain explicitly disabled/deferred.

CL-09-R009 is also an explicit exit gate: tests must prove no case hard-delete path removes retained `ModerationAction` proof. A replacement FK/deletion strategy requires separate approval; this documentation pass does not change the current cascade.

---

# MODULE INTEGRATION PHASE

Module **Feature 10** is the dedicated integration phase.

It proves:

- target validation occurs through owner contracts;
- Search changes only through Search;
- Media/file effects only through Media;
- Messaging, Marketplace, Gig, Hiring, Digital Goods, Video and profile effects only through their owners;
- reusable stop signs only through Admin Review / Compliance Hold;
- generic audit/access proof only through Audit;
- Notification only through Notification;
- technical failure/queue visibility only through Observability/shared queue;
- Privacy orchestrates while this Module executes only its own records.

Contract failures are fixed at the owner boundary. They are never temporarily bypassed with direct foreign database access.

---

# MODULE HARDENING PHASE

Module **Feature 11** is the dedicated hardening phase.

Relevant hardening includes:

- report/legal intake abuse prevention;
- target IDOR/polymorphic reference validation;
- reviewer privilege escalation prevention;
- evidence access/redaction;
- lifecycle transition races;
- idempotency and replay;
- action/restoration overlap;
- enforcement reconciliation;
- queue retry/dead-letter;
- dependency/provider outage through owner Modules;
- privacy/retention;
- audit completeness;
- telemetry safety;
- migration/backfill/enum mapping;
- query/index performance.

It explicitly does **not** authorize unresolved repeat-infringer or duplicate-content fingerprinting.

---

# PHASE SUMMARY

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts, Source Truth, and Intake | 01 Module Contract and Lifecycle Foundation; 02 Report Intake, Triage, and Case Opening; 03 Formal Legal Notice Intake and Structural Validation |
| 2 | Adjudication and Evidence | 04 Evidence-Preserving Moderation Decisions |
| 3 | Cross-Module Enforcement and Legal Restoration | 05 Cross-Module Enforcement and Reconciliation; 06 Counter-Notice and Restoration; 07 Approved Legal Deadline Worker |
| 4 | Review Surface and Privacy Participation | 08 Moderation Administrative Review Surface; 09 Privacy, Retention, and Export Executor |
| 5 | Integration Proof and Production Hardening | 10 Cross-Module Contract Verification; 11 Security, Concurrency, Reconciliation, and Launch Hardening |

**Total numbered Module features: 11.**

These features are Module-local decomposition. They remain subordinate to the CL-09 feature order: Cluster 03 -> 05 -> 06 -> 07 -> 08 -> 10 -> 11 -> 12, with Cluster 01/02/04/09 supplied by sibling Modules.

---

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root project overview.
2. Read root architecture and code standards if present.
3. Read Canonical Shared Operations.
4. Read CL-09 architecture and build plan.
5. Read this Module architecture and plan.
6. Read public-interface sections for direct dependencies used by this feature.
7. Confirm the relevant CL-09 prior exit gate and this Module prior exit gate.
8. Check the unresolved/proposed-ruling table for blockers.
9. Produce the feature implementation specification below.
10. Implement only the numbered feature.
11. Run required typecheck/lint/tests/schema/build checks.
12. Verify observable workflow/contracts.
13. Update progress.
14. Update architecture only if a binding decision legitimately changed.
15. Record assumptions, failures, risks, and deferred work.

Do not begin the next numbered feature unless the current exit gate passes or an architecture owner explicitly records an exception.

---

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a numbered feature, the coding agent must produce:

- **Feature**
- **Objective**
- **Observable result**
- **Cluster build-plan link**
- **Dependencies**
- **Blocking unresolved/proposed rulings**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Schema/migration changes**
- **Public contracts**
- **Shared operations consumed**
- **Permissions / Role / Authority actions**
- **Compliance/legal policy inputs**
- **Primary workflow**
- **UI/admin states if applicable**
- **Provider integration** — normally "none directly" for this Module
- **Jobs/events/outbox/inbox**
- **Idempotency/concurrency**
- **Error/partial-completion behavior**
- **Privacy/retention**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Exit-gate commands/checks**

Do not pre-generate implementation specifications for later features. Re-read current context immediately before each feature because accepted rulings may change the specification.

---

# REQUIRED COMPLETION REPORT

After implementing each numbered feature, report:

- Feature completed
- Cluster feature supported
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Module public interfaces added/changed
- Dependency contracts added/changed
- Shared operations reused
- Events/outbox/inbox changes
- Jobs/workers added
- Provider adapter changes — should normally be none inside this Module
- Tests added/changed
- Commands run
- Manual/contract/E2E verification
- Documentation updated
- Assumptions
- Accepted rulings relied on
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

If implementation discovered a conflict with architecture, record it and update architecture only after the decision is explicitly accepted. Do not silently normalize the code around it.

---

# FINAL QUALITY CHECK

Before declaring the Module plan complete or any production milestone ready, verify:

1. Report, LegalNotice, ModerationCase, and ModerationAction each have exactly one owner.
2. No neighboring Module truth was absorbed.
3. Report and LegalNotice remain separate.
4. ModerationAction remains distinct from AuditEvent and downstream execution.
5. Every shared operation is consumed rather than duplicated.
6. Cross-Module reads use owner contracts.
7. Cross-Module writes use owner commands/protocols.
8. Provider adapters do not become moderation truth and are not implemented here.
9. Audit, domain facts/events, orchestration correlation, and Observability remain distinct.
10. Privacy orchestration remains Privacy-owned.
11. Search remains projection and Media remains file owner.
12. ComplianceHold remains the reusable stop sign.
13. Evidence preservation gates destructive/public-removal actions where required.
14. Lifecycle transitions are explicit and concurrency-safe.
15. Idempotency/replay semantics are tested.
16. Legal timing/retention/sufficiency rules are approved or disabled.
17. Repeat-infringer and fingerprint features remain deferred until ruled.
18. Current Prisma target enum/mapping is reconciled with migration history before migration changes.
19. Every numbered feature has tests and an exit gate.
20. Cluster feature order has not been changed.
21. A coding agent can implement each enabled feature without inventing architecture.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.

## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

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

## WA-R034 — Search work, protected transport and completion evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Search remains rebuildable projection. Source owners supply opaque currentness tokens, purpose-limited field allowlists and a currentness query; do not compare arbitrary tokens lexicographically or rely on wall-clock updatedAt alone. Search assigns a monotonic per-target work generation under a target lock and records all relevant source/visibility/Track/Location/Moderation evidence versions. Before writing and before exposing protected results, re-evaluate current source authorization and projection applicability. An older job cannot supersede a newer generation; deletion/restriction tombstones take precedence until current owner evidence explicitly permits publication again. Provider-native conditional writes are not assumed: adapters must prove their serialization/reconciliation behavior, and server query filtering prevents stale provider data from becoming an authority bypass.

Evolve SearchUpsertEvent into Search-owned durable work with request/command identity, typed target/source owner, expected tokens, generation, operation/purpose, pending/processing/completed/failed/superseded state, outcome and attempt/provider correlation. Shared queue leases/retries are separate. pending→processing; processing→completed/failed or pending for technical retry; stale work→superseded with successor correlation. Completed outcomes are upserted/removed/no_op/skipped with explicit reason and confirmed generation. A privacy removal cannot be marked completed from skipped/unavailable source facts. Same request/fingerprint replays the same work/result. Exact Prisma columns/indexes follow coordinated schema ownership, not a second queue.

All Search queries are server-mediated at launch, including public queries. No browser receives privileged or public Typesense credentials. Use independently versioned per-entity public collections with controlled alias cutover after full validated rebuild; protected Candidate collections/credentials are separate and never part of public federated queries or public counts/facets/autocomplete. Admin write credentials remain distinct from scoped server query credentials. Verify actual provider configuration/capabilities before activation; no current provider feature is presumed from these architectural requirements. Schema migration builds a new generation, validates completeness/currentness, then atomically changes the serving configuration; retain rollback generation without restoring revoked projections.

Protected Candidate search composes authenticated actor, current Organization membership/action authority, applicable Organization commercial permission, Candidate owner-approved searchable projection/visibility, applicable Hold/Moderation restrictions and field-level access policy. A result cannot imply permission to open a resume: resume access uses Candidate and Media separately. Search revalidates each returned Candidate's current projection/permission before disclosure; deny/unavailable removes that result rather than returns stale sensitive fields. Suppress provider totals/facets that expose filtered protected populations. Record one durable access batch proof before each protected response with requesting actor/Org/purpose, query fingerprint, permitted result target/version references and outcome; do not log raw sensitive query text. Resume/detail access produces its own required proof. If mandatory proof cannot commit, withhold the response under WA-R023.

Public results also obey current source restrictions; query sanitization and bounded result sizes apply before provider access. Basic relevance plus a stable target-ID tie-breaker is the launch ranking baseline. Advanced trust/recency/featured weighting is deferred versioned tuning, not a new premium benefit. Candidate's approved subscription boost follows WA-R030 (1.15 after eligibility, non-metered); it never changes privacy/eligibility. Generic User and CustomerProfile public indexing stay disabled; reserved enum values do not authorize publication. Search receives accepted source facts only, not raw AI suggestions or AI diagnostic history.

Source enumeration uses opaque stable cursors, snapshot/high-watermark identity, target/source token and explicit end-of-snapshot completeness. Each contextual owner enumerates its own records/joins. Incremental iteration cannot prove an unobserved target is deleted. Orphan removal requires a complete comparable source snapshot or an explicit owner deletion/tombstone receipt; cursor interruption never means empty source. Taxonomy changes request affected-owner enumeration and each source requests refresh through Search; neither Taxonomy nor Search scans foreign joins. Required per-target projection/AI/authority DTO field lists remain owner-specific and need bilateral qualification; the common mechanics do not approve arbitrary fields.

SH-091 returns accepted work identity, not completion. Search exposes a versioned completion receipt/query bound to request/work identity, typed target, requested generation/policy and verified outcome. Privacy/Moderation require removed/no_op-absent proof for their exact instruction; missing/timeout/provider uncertainty remains pending/unavailable. Receipt persists provider acknowledgement and reconciliation observation; tombstone prevents late stale jobs from resurrecting removed content. A superseded work receipt points to its successor, whose qualifying outcome is required before external fulfillment completes. Search never closes Privacy/Moderation's own workflow.

Start reconciliation/maintenance through authorized bounded manual commands; automatic cadence is versioned operational configuration added only with run budgets/coverage evidence. No periodic AI reclassification, end-user notification, query-history analytics store or speculative provider callback is implied. Per-action request/backfill/model cost limits use SH-132 and shared execution with explicit configured budgets and fail posture; never substitute Track commercial metering. No intrinsic Taxonomy cron or extra business-run table is required for normal maintenance. Operational telemetry is minimized and separate from domain completion evidence. Legal retention for subject-linked work/access receipts and actual provider configuration remain external requirements.

Required implementation checks: delayed stale upsert after deletion, provider write uncertainty, current-source denial at query time, protected collection isolation/totals, audit failure, incomplete enumeration, interrupted generation cutover, duplicate refresh, superseded removal receipt and consumer completion correlation. These contracts require adapter and bilateral fixture evidence before parallel-interface promotion; this architecture pass does not execute provider/schema/runtime tests.
