# Privacy / Data Erasure Module Implementation Plan

> **Module ID:** `privacy_data_erasure`  
> **Canonical module name:** Privacy / Data Erasure Module  
> **Primary Cluster:** CL-08 Privacy & Location Safety  
> **Companion Module architecture:** `context/privacy-location-safety/privacy_data_erasure/module-architecture.md`  
> **Plan status:** Implementation sequence; decision-gated where architecture/legal policy is unresolved  
> **Subordination rule:** This plan is subordinate to the CL-08 `build-plan.md` and may not independently reorder Cluster work or redefine ownership.  
> **Total numbered features:** 9

---

## Core Principle

Implement Privacy / Data Erasure through narrow, verifiable slices:

```text
public/observable behavior
→ validated command/query
→ Privacy-owned policy
→ Privacy-owned authoritative write/read
→ canonical shared-operation calls
→ source-owner privacy executor calls
→ event/audit/notification effects
→ durable jobs where required
→ tests
→ exit gate
```

Privacy owns the legal/request workflow and aggregate proof. It does **not** own every Module's data, provider clients, Search index, Media storage mechanics, authorization system, audit ledger, queue infrastructure, Notification delivery, or legal retention law.

The Module must become executable without becoming a universal "delete user" service.

---

## Build Rules

1. Follow root Workin Ants architecture and code standards.
2. Follow CL-08 architecture and build sequence.
3. Follow this Module architecture.
4. Implement only Privacy / Data Erasure's declared truth.
5. Consume neighboring Modules through approved public interfaces.
6. Use Canonical Shared Operations; do not create local copies.
7. Validate every command/query at runtime.
8. Resolve authenticated actors and authorize protected operations server-side.
9. Lifecycle transitions are Privacy-owned and transaction-safe.
10. Destructive external effects are idempotent and owner-executed.
11. `DataErasureJob` remains business truth; generic `QueueJob` is operational only.
12. `DataErasureTarget` remains Privacy disposition truth; provider/owner status does not replace it.
13. Retention exemptions require authoritative owner facts.
14. Provider details stay behind provider-owning Modules.
15. Search changes go through Search.
16. Media storage/signed access goes through Media.
17. Audit/AccessAuditLog remain Audit-owned.
18. Notification owns channel delivery.
19. Jobs use canonical queue/retry/dead-letter mechanisms.
20. Events use the canonical transactional outbox only after event names/contracts are approved.
21. Never populate `dueAt`, approve/reject a request, transition to `verified`, decide `access` semantics, or complete correction/restriction from guessed policy.
22. Never hard-delete `User` as a shortcut before U-08-08 is resolved.
23. Never claim backup purge before U-08-09 is resolved.
24. Every numbered feature has tests and an exit gate.
25. Do not start the next numbered feature until the current exit gate passes, unless the feature is decision-gated and the project owner intentionally pauses that path.
26. When implementation settles a binding deferred decision, update architecture first and record the ruling.
27. Record unresolved blockers rather than hiding them behind feature flags, TODOs, generic `other` logic, or silent partial behavior.

---

## Preconditions

### Hard platform dependencies

The following must exist before the feature that invokes them:

- Prisma/PostgreSQL migrations and transaction support;
- runtime schema validation;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- DB-backed `acquireAggregateLock` and/or approved optimistic-concurrency primitive;
- `enqueueReliableJob` and bounded retry/dead-letter behavior;
- request/correlation context;
- structured logging with telemetry sanitization;
- Audit / Event Ledger append interfaces;
- standardized root result/error contract.

If one is not implemented, schedule it in its canonical owner. Do not create a Privacy-only substitute.

### Public interfaces that may initially be stubbed

Contract tests may use approved fakes/stubs for:

- Identity privacy-verification result;
- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- `validateOwnedTargetReference`;
- Media private artifact creation/finalization;
- `issueSignedMediaUrl`;
- Search `requestSearchProjectionRefresh`;
- Notification `requestNotification`;
- Audit `appendAuditEvent` / `recordSensitiveAccess`;
- Observability `recordIntegrationFailure`;
- provider deletion results returned through owner executors.

Stubs must match the canonical contracts and may not implement neighboring lifecycle truth inside Privacy.

### Existing schema

Current Prisma already contains:

- `PrivacyRequest`
- `DataErasureJob`
- `DataErasureTarget`
- `DataRetentionExemption`
- `DataExportBundle`
- all related enums.

Only migrations explicitly approved by updated architecture may be added.

### Decision gates

Do not implement production behavior dependent on:

- U-08-01 identity-verification proof;
- U-08-02 access vs export semantics;
- U-08-03 correction/restriction proof;
- U-08-04 retained-target aggregation;
- U-08-05 cancellation/rejection policy;
- U-08-06 jurisdiction/deadline policy;
- U-08-07 active-request concurrency policy;
- U-08-08 final User disposition;
- U-08-09 backup representation;
- U-08-21 Location retention under privacy;
- U-08-22 export Media relation/manifest hardening;
- U-08-23 explicit Location Safety target types;
- PR-08-03 domain event family;
- PR-08-04 Media referential-integrity change;
- PR-08-05 Location target-type addition;

until they are approved in architecture/progress context.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Privacy Request Intake and Status Surface

### Objective

Create the first working Privacy-owned vertical slice: an authenticated User can submit a modeled privacy request and read its authoritative status without the platform pretending that identity verification, legal deadlines, fulfillment, or completion already exist.

### Observable Result

- authenticated User submits `access`, `export`, `erasure`, `correction`, or `restriction`;
- one `PrivacyRequest(status=submitted)` is created per idempotent command;
- User sees request history and detail;
- another normal User cannot read the request;
- explicitly authorized admin/support can read the permitted metadata;
- no surface claims `verified`, legal due date, erasure completion, export readiness, or correction/restriction completion.

### Cluster Build-Plan Link

Supports CL-08 **Feature 01 — Privacy Request Intake and Status Surface**.

This Module feature must satisfy the Privacy portion of the Cluster exit gate before Module Feature 02 begins.

### Dependencies

- current PrivacyRequest schema/enums;
- `resolveAuthenticatedActor`;
- `authorizeResourceAction`;
- `executeIdempotentCommand`;
- `appendAuditEvent`;
- request context/structured logging/sanitization;
- root runtime validation and result conventions.

### In Scope

- request DTO/schema validation;
- `submitPrivacyRequest`;
- `getPrivacyRequest`;
- `listUserPrivacyRequests`;
- Privacy repository for request model only;
- owner-scoped query policies;
- safe self-service request form/status UI if application UI is part of the current root delivery pattern;
- narrow admin/support list/detail if CL-08 admin surfaces are active;
- request submission audit;
- idempotency tests;
- telemetry redaction.

### Out of Scope

- identity-verification completion;
- transition to `verifying_identity` or `verified`;
- `dueAt` calculation;
- request cancellation/rejection;
- erasure job creation;
- export generation;
- target inventory;
- correction/restriction execution;
- hard-delete/anonymized User strategy;
- provider calls;
- local Notification delivery.

### Module-Owned Data

- `PrivacyRequest`
- `PrivacyRequestType`
- `PrivacyRequestStatus`

No schema change is required.

Do not add active-request uniqueness while U-08-07 is unresolved.

### Public Interfaces

Introduce/complete:

```ts
submitPrivacyRequest(...)
getPrivacyRequest(...)
listUserPrivacyRequests(...)
```

Minimum safe response:

```text
id
type
status
requestedAt
verifiedAt
dueAt
completedAt
safe rejection summary when authorized
safe export-bundle summary only after later features
```

Do not return unrestricted `adminNote`.

### Shared Operations Used

#### `resolveAuthenticatedActor`
- **Owner:** Identity & Access
- **Invocation:** before every protected command/query
- **Local policy:** which Privacy resource/action is being requested
- **Prohibited duplicate:** `requireUser`, local session parser

#### `authorizeResourceAction`
- **Owner:** Role / Authority
- **Invocation:** before request read/list/admin view
- **Local policy:** request owner/admin action facts
- **Prohibited duplicate:** `privacyAuth.ts`, local admin matrix

#### `executeIdempotentCommand`
- **Owner:** platform application infrastructure
- **Invocation:** request submission
- **Local policy:** semantic request fingerprint and conflict behavior
- **Prohibited duplicate:** Privacy idempotency table/service

#### `appendAuditEvent`
- **Owner:** Audit / Event Ledger
- **Invocation:** successful submit and sensitive admin actions
- **Local policy:** safe event meaning/metadata
- **Prohibited duplicate:** PrivacyAuditLog

#### request/log sanitization operations
- **Owner:** platform/Ops
- **Invocation:** all endpoints
- **Local policy:** Privacy sensitive-field classification
- **Prohibited duplicate:** local unstructured logger

### Domain Logic

- accept only modeled `PrivacyRequestType` values;
- request begins at `submitted`;
- User ID comes from server actor/authorized subject context, never client truth;
- `requestedAt`, created/updated timestamps are server-owned;
- `dueAt` remains null unless approved later;
- no automatic verification transition;
- no consent or entitlement gate;
- no ComplianceHold assumption;
- same idempotency key + same semantic fingerprint returns original result;
- same key + different fingerprint returns deterministic conflict.

### Authorization / Compliance

- normal User may submit for self;
- normal User may read own request;
- cross-user access denied;
- admin/support only through named Role / Authority action;
- no blanket admin export/content access is implied;
- privacy right intake is not premium;
- generic privacy-policy consent is not a prerequisite to create the request.

### Database / Transaction Behavior

- validate before transaction;
- `executeIdempotentCommand` atomically claims command and writes `PrivacyRequest`;
- no client-supplied status;
- indexes already present should support owner/history/status reads;
- if `appendAuditEvent` is not in same database transaction, follow root audit criticality policy; do not invent local rollback semantics.

### Events / Jobs

No fulfillment worker.

If PR-08-03 has been approved and root event registry contains `privacy.request.submitted`, write its outbox record transactionally. Otherwise emit no domain event.

### Provider Integration

None.

### UI / Admin Surface

Self-service UI, if UI is in scope:

- request-type selection;
- submit;
- request list;
- request detail;
- status copy driven from source truth;
- neutral "submitted" messaging.

Admin/support:

- metadata list/detail;
- no raw target or export contents;
- access controlled by Role / Authority.

### Failure Behavior

- invalid type → validation denial;
- unauthenticated → auth denial;
- unauthorized ID → root anti-enumeration behavior;
- idempotency conflict → deterministic conflict;
- DB failure → no request created;
- audit/log failure → root criticality behavior, never fabricated Privacy status;
- unsupported UI path → explicit unavailable/decision-gated state.

### Tests

**Unit**
- request type validation;
- safe serializer;
- default `submitted`.

**Integration**
- authenticated create;
- owner read/list;
- cross-user denial;
- authorized admin read;
- idempotent replay;
- idempotency conflict.

**Security/privacy**
- no request details in telemetry;
- no arbitrary `adminNote`;
- no guessed `dueAt`.

**E2E**
- submit → history → detail shows same authoritative request.

### Documentation Updates

- update Module public-interface documentation if names/result shapes change;
- update progress tracker;
- update architecture only if a binding ownership/transition decision changes;
- do not mark unresolved U-08 items complete.

### Acceptance Criteria

- `PrivacyRequest` is the sole request truth;
- request starts at `submitted`;
- owner isolation is enforced;
- no local auth/idempotency/audit infrastructure;
- no legal semantics invented;
- public contract is documented and tested.

### Exit Gate

Before Feature 02:

- typecheck passes;
- lint/format checks pass;
- unit/integration/E2E tests pass;
- duplicate same-key submit creates one request;
- cross-user read fails;
- no unapproved status transition occurs;
- CL-08 Feature 01 Privacy exit criteria are met;
- progress tracker records Feature 01 complete.

---

## 02 Privacy Executor Protocol and Subject-Data Inventory

### Objective

Define and prove the cross-Module protocol that lets Privacy discover data owners, enumerate subject data, receive retention facts, and request owner-local execution without direct cross-domain repositories.

### Observable Result

An authorized internal diagnostic can perform a **dry-run subject inventory** for test data and display:

```text
owner Module
target type
stable target reference
supported actions
sensitivity
retention-candidate flag
export serializer version
cursor/progress
safe error/result
```

At least two different source Modules participate through the same protocol shape.

### Cluster Build-Plan Link

Supports CL-08 **Feature 02 — Privacy Executor Protocol and Subject-Data Inventory**.

### Dependencies

- Module Feature 01;
- canonical `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- `validateOwnedTargetReference`;
- `queryOwnerFacts`;
- `executeIdempotentCommand`;
- request/correlation/logging;
- approved fake executors for at least two owners.

### In Scope

- `contracts/privacy-executor.ts`;
- target descriptor and normalized result schemas;
- executor registry;
- bounded/cursorable enumeration orchestration;
- dry-run diagnostic;
- owner registration/coverage checks;
- reference fake executors;
- contract tests;
- safe retention-result contract;
- safe export-section contract.

### Out of Scope

- full production executor implementation for all Modules;
- destructive target execution;
- DataErasureJob creation;
- final retention exemption writes;
- legal retention rules;
- direct provider deletion;
- correction/restriction terminal proof;
- universal polymorphic database table.

### Module-Owned Data

No mandatory Prisma write.

Contract descriptor should include:

```text
ownerModule
targetType
targetId or externalRef
subjectId
supportedActions
sensitivity
sourceVersion
retentionCandidate
exportSerializerVersion
```

This descriptor is not a new universal truth table.

### Public Interfaces

Define canonical protocol types for:

```ts
enumerateSubjectData(request)
evaluateRetentionRequirement(request)
executePrivacyInstruction(request)
serializePrivacyExportSection(request)
```

Normalized result vocabulary:

```text
erased
anonymized
retained
skipped
failed_retryable
failed_terminal
not_found
unsupported_action
```

Do not add corrected/restricted terminal statuses until U-08-03.

### Shared Operations Used

#### `enumerateSubjectData`
- **Owner:** each data owner through Privacy-defined interface
- **Invocation:** inventory
- **Local policy:** required descriptor shape, coverage, cursor rules
- **Prohibited duplicate:** global data crawler

#### `evaluateRetentionRequirement`
- **Owner:** source owner supplies facts; Privacy records exemption later
- **Invocation:** protocol contract and dry-run
- **Local policy:** standardized proof fields
- **Prohibited duplicate:** tax/contract retention engine

#### `executePrivacyInstruction`
- **Owner:** source owner executes
- **Invocation:** contract only; destructive calls wait for Feature 03
- **Local policy:** supported action/result vocabulary
- **Prohibited duplicate:** direct source repositories

#### `validateOwnedTargetReference`
- **Owner:** target owner
- **Invocation:** registry/contract validation
- **Local policy:** what Privacy relation needs validation
- **Prohibited duplicate:** direct cross-Module `findUnique`

#### `queryOwnerFacts`
- **Owner:** source Module
- **Invocation:** minimal supplemental facts if needed
- **Local policy:** DTO minimization
- **Prohibited duplicate:** polymorphic owner repository

#### `executeIdempotentCommand`
- **Owner:** platform
- **Invocation:** executor command contract requirements
- **Local policy:** owner action idempotency key
- **Prohibited duplicate:** local executor dedupe store

### Domain Logic

- executors register explicitly by owner Module and supported target types;
- unsupported owner/type is visible, never silently ignored;
- inventory is cursorable/bounded;
- descriptors contain references, not raw sensitive data;
- source Module defines its schema mapping and export meaning;
- owner must validate target again at execution;
- `other` must identify explicit executor owner and cannot select generic deletion;
- dry-run performs no mutation;
- Privacy must not edit registry policy to understand another Module's internal tables.

### Authorization / Compliance

- diagnostic is developer/admin-only;
- executor itself must enforce subject/owner context through its owner;
- retentionCandidate is not final exemption;
- no admin universal raw-data read;
- no raw provider credentials/results.

### Database / Transaction Behavior

No cross-Module DB transaction.

Executor registry can be static/configured at application composition layer but must not become source truth for owner lifecycle.

If inventory output is temporarily cached for diagnostics, it must be ephemeral/non-authoritative and contain no raw payload.

### Events / Jobs

For large inventory, allow `enqueueReliableJob` using cursor checkpoints.

Dry-run fixture may stay synchronous.

No domain events required.

### Provider Integration

None directly.

### UI / Admin Surface

Internal coverage/inventory diagnostic:

- owner;
- target type;
- protocol version;
- cursor;
- count;
- supported actions;
- retention policy status;
- error category.

No raw subject data.

### Failure Behavior

- owner not registered → explicit `OWNER_NOT_REGISTERED`;
- invalid target type → validation;
- owner timeout → `DEPENDENCY_RETRYABLE`;
- owner says unsupported → explicit unsupported;
- one owner fails → inventory is incomplete and visibly failed; do not infer "no data";
- ambiguous owner for `postgres_profile`/`other` → decision-gated or explicit diagnostic failure.

### Tests

**Contract**
- target descriptor schema;
- pagination/cursor;
- stable normalized results;
- owner validation;
- export-section schema;
- invalid/unknown result rejection.

**Integration**
- at least two fake/real owner executors enumerate same subject;
- one owner failure remains visible.

**Security**
- descriptors exclude raw content/secrets;
- no direct cross-owner Prisma repository.

### Documentation Updates

- add protocol/version to Module architecture if finalized;
- dependency Module interface docs must reference the contract;
- progress tracker lists which executors are fake/real;
- if durable ownerModule persistence becomes required, architecture must be updated before schema migration.

### Acceptance Criteria

- one canonical protocol shape;
- at least two owners pass contract suite;
- inventory is bounded;
- no generic database crawler;
- `other` cannot execute generically;
- missing owner cannot be hidden.

### Exit Gate

- contract schemas documented;
- executor registry test passes;
- two-owner dry-run succeeds;
- unknown owner/type tests fail safely;
- telemetry is payload-safe;
- no ownership boundary violation;
- CL-08 Feature 02 exit criteria pass.

---

# Phase 2 — Core Lifecycle and Fulfillment

## 03 Verified Erasure Orchestration and Retention Proof

### Objective

Build the durable erasure workflow for a request that is already authoritatively `verified`, proving cross-Module target registration, retention proof, owner-local execution, retry safety, and Privacy-owned disposition.

### Observable Result

For an approved fixture/authoritative verified request:

- one erasure job is created;
- target inventory is persisted;
- at least two owner executors run;
- one target can erase successfully;
- one target can be retained with a documented exemption;
- retryable failures remain visible and retry safely;
- requester/admin can read safe job/target summary;
- request is not falsely declared complete while U-08-04 remains unresolved.

### Cluster Build-Plan Link

Supports CL-08 **Feature 04 — Erasure Orchestration, Target Disposition, and Retention Proof**.

CL-08 Feature 03 is Location-only and is not duplicated in this Module plan.

### Dependencies

- Module Features 01–02;
- authoritative test/approved `PrivacyRequest(status=verified, type=erasure)`;
- `enqueueReliableJob`;
- `executeRetryWithBackoff`;
- `orchestrateWorkflowSteps`;
- `reconcileWorkflowStatus`;
- DB aggregate locking;
- Audit/Ops interfaces;
- at least two executor implementations/fakes;
- owner retention result contract.

### In Scope

- `startVerifiedErasure`;
- `discoverAndRegisterTargets`;
- `processErasureTarget`;
- `recordDataRetentionExemption`;
- `resolveErasureTarget`;
- `reconcileErasureJobOutcome` without guessing final request result;
- erasure workers;
- target/job admin summary;
- retry/dead-letter visibility;
- cross-owner contract calls;
- normalized target result mapping.

### Out of Scope

- how request becomes `verified`;
- `access`;
- correction/restriction;
- cancellation/rejection;
- User final hard delete;
- backup deletion;
- final request `completed` vs `partially_completed` for mixed retention;
- direct provider SDK;
- all production executors.

### Module-Owned Data

- `DataErasureJob`
- `DataErasureTarget`
- `DataRetentionExemption`
- `PrivacyRequest` may transition to `processing` only through the approved build-safe verified→processing rule.

No schema migration required for the initial slice.

### Public Interfaces

Internal application/worker interfaces:

```ts
startVerifiedErasure(...)
discoverAndRegisterTargets(...)
processErasureTarget(...)
retryErasureTarget(...)
reconcileErasureJobOutcome(...)
getErasureJobSummary(...)
getErasureTargetSummary(...)
```

External owner calls use Feature 02 contracts.

### Shared Operations Used

#### `orchestratePrivacyFulfillment`
- **Owner:** Privacy
- **Invocation:** coordinates erasure sequence
- **Local policy:** Privacy ordering/target/result semantics
- **Prohibited duplicate:** feature-module GDPR workflow

#### `enumerateSubjectData`
- owner inventory.

#### `evaluateRetentionRequirement`
- owner supplies required retention facts.

#### `executePrivacyInstruction`
- owner performs actual mutation.

#### `anonymizePersonalFields`
- used by source owner, not as global Privacy mutation.

#### `orchestrateWorkflowSteps` / `reconcileWorkflowStatus`
- shared mechanics; `DataErasureJob` remains truth.

#### `enqueueReliableJob` / `executeRetryWithBackoff`
- durable worker execution; no Privacy queue framework.

#### `executeIdempotentCommand`
- job start, target registration/execution result recording.

#### `acquireAggregateLock`
- request/job/target race control.

#### `transitionLifecycleState`
- Privacy status plumbing.

#### `appendAuditEvent`
- erasure start/retention/admin actions.

#### `recordIntegrationFailure`
- operational failures only.

### Domain Logic

1. Refuse start unless request:
   - exists;
   - `type=erasure`;
   - `status=verified`.
2. Acquire request aggregate lock.
3. Use idempotent start command to find/create semantic `DataErasureJob(status=queued)`.
4. Queue discovery.
5. Inventory all registered in-scope executors.
6. Register target references while the job registration lock prevents duplicates.
7. For each target:
   - validate through owner;
   - call retention interface;
   - if retention required:
     - validate controlled reason/basis;
     - create `DataRetentionExemption`;
     - request owner anonymization when permitted/required;
     - record final returned target disposition;
   - otherwise call owner `executePrivacyInstruction(erasure)`;
   - record normalized target result.
8. Retry only retryable technical failures.
9. Never infer successful erasure from queued provider work.
10. Preserve already successful target proof under replay.
11. Reconcile `DataErasureJob`.
12. Do not set aggregate `PrivacyRequest` terminal state until U-08-04 is approved.

### Authorization / Compliance

- requester sees safe own summary;
- detailed target/exemption view is authorized admin/compliance only;
- no arbitrary admin can choose `legal_obligation`;
- no Track entitlement gate;
- ComplianceHold is evaluated only if approved for a specific operation;
- source owner remains authoritative for retained record facts.

### Database / Transaction Behavior

**Start**
- request lock;
- check request status/type;
- create/fetch semantic job;
- transition request to `processing` only if approved in current architecture;
- enqueue after commit/outbox pattern.

**Target registration**
- lock erasure job;
- prevent duplicate tuple under the job using semantic registry comparison;
- do not add schema uniqueness without architecture approval.

**Target resolution**
- lock target row;
- if already terminal with same semantic owner result, replay;
- if conflicting terminal result, invariant conflict/manual review;
- write target status + exemption in one Privacy transaction where applicable.

**Reconciliation**
- lock job;
- compute from persisted target states;
- do not use queue states.

### Events / Jobs

Jobs:

```text
privacy inventory/discovery
per-target erasure
target retry
erasure reconciliation
```

If PR-08-03 is approved:

```text
privacy.erasure_job.queued
privacy.target.resolved
```

use outbox.

Dead-letter:

- operational record in Ops;
- Privacy job/target remains visibly unresolved/failed according to policy;
- no false completion.

### Provider Integration

No direct provider clients.

Owner executors may internally use `deleteProviderResource`.

### UI / Admin Surface

Requester-safe status:

- request processing;
- target totals;
- completed/retained/failed counts;
- generic pending/manual-review message.

Admin:

- job/target list;
- owner Module;
- target type;
- safe result;
- retryable/terminal indicator from worker/Ops;
- retention reason/basis reference where authorized;
- retry action routed through canonical queue/idempotency.

### Failure Behavior

- inventory owner timeout → job remains incomplete; retry;
- unknown executor → explicit unresolved target coverage;
- retained without basis → invariant violation/manual review;
- owner returns retryable → queue retry; do not mark erased;
- retry exhaustion → terminal failure/manual-review path, no false completion;
- duplicate delivery → idempotent replay;
- provider unavailable → owner normalized retryable result;
- Audit/Notification failure does not become target success.

### Tests

**Unit**
- target result mapping;
- retention requirement validation;
- exemption creation;
- job aggregation mechanics without final request policy;
- retry classification.

**Integration**
- two owner executors;
- erased target;
- retained target + exemption;
- anonymized retained target where fake owner supports it;
- retryable then success;
- terminal failure.

**Concurrency**
- duplicate erasure start;
- two registration workers;
- two target workers;
- late duplicate owner result.

**Compliance**
- no retained target without exemption;
- no direct provider client;
- no QueueJob-as-business-status.

**E2E**
- seeded verified request → processing → visible target results.

### Documentation Updates

- progress tracker records executor set and fixtures;
- if target-owner persistence gap blocks an owner, record decision rather than patching schema;
- architecture update required before any new target status/uniqueness/provider ownership decision.

### Acceptance Criteria

- job/target/exemption truth is durable;
- at least two owners participate through public executor contracts;
- retained target has exemption;
- same target effect occurs once under replay;
- provider mechanics remain outside Privacy;
- final aggregate request is not guessed.

### Exit Gate

- CL-08 Feature 04 Privacy exit criteria pass;
- concurrency tests pass;
- retry/dead-letter path visible;
- target status cannot be falsely successful;
- typecheck/lint/unit/integration/E2E pass;
- progress tracker records unresolved U-08-04.

---

## 04 Privacy Export Bundle and Secure Delivery

### Objective

Generate, store, authorize, deliver, expire, and clean up a private `DataExportBundle` for an authoritatively verified `export` request while leaving object storage and signed access with Media.

### Observable Result

For a verified export fixture/approved request:

```text
queued → generating → ready → expired
```

Requester can obtain short-lived access while ready/unexpired; another User cannot. Sensitive access is audited. Expired bundle stops issuing access.

### Cluster Build-Plan Link

Supports CL-08 **Feature 05 — Privacy Export Bundle and Secure Delivery**.

### Dependencies

- Module Features 01–02;
- authoritative verified `export` request;
- owner export serializers;
- Media private artifact create/finalize;
- `issueSignedMediaUrl`;
- canonical queue/expiry;
- Audit;
- approved encryption/hash primitive if root export contract requires it.

### In Scope

- `generateDataExportBundle`;
- `getPrivacyExportStatus`;
- `authorizePrivacyExportDownload`;
- `expireDataExportBundle`;
- export generation worker;
- expiry worker;
- owner section assembly;
- private Media handoff;
- short-lived signed access handoff;
- access audit;
- ready/failed/expired UI;
- cleanup reconciliation.

### Out of Scope

- `access` request semantics;
- production manifest fields not approved under U-08-22;
- direct R2/S3 calls;
- custom encryption stack;
- permanent URL;
- browser-local data aggregation;
- automatic legal deadline logic;
- admin unrestricted content preview.

### Module-Owned Data

- `DataExportBundle`
- `DataExportStatus`

Current fields:

```text
privacyRequestId
userId
status
mediaAssetId
expiresAt
generatedAt
failureReason
```

Do not add Media relation/manifest/hash fields until PR-08-04/U-08-22 are approved.

### Public Interfaces

```ts
generateDataExportBundle(...)
getPrivacyExportStatus(...)
authorizePrivacyExportDownload(...)
expireDataExportBundle(...)
```

Actual file issuance:

```text
Privacy authorize
→ Media issueSignedMediaUrl
```

### Shared Operations Used

#### `createPrivacyExportArtifact`
- **Owner:** Privacy owns bundle/content policy; Media owns storage
- **Invocation:** export worker
- **Local policy:** owner sections, completeness, expiry
- **Prohibited duplicate:** R2 archive/signed delivery stack

#### `enumerateSubjectData`
- obtain exportable owner sections/references.

#### `issueSignedMediaUrl`
- **Owner:** Media
- **Invocation:** after fresh Privacy access allow
- **Local policy:** bundle ready/unexpired and requester authorization
- **Prohibited duplicate:** local presign

#### `hashCanonicalPayload`
- only when approved for manifest/integrity.

#### `encryptSensitiveValue` or approved archive encryption
- use shared security mechanism, never local crypto.

#### `recordSensitiveAccess`
- signed access issuance/download as required.

#### `enqueueReliableJob`
- generation/cleanup.

#### `runDeadlineExpiration`
- expiry scan.

#### `executeIdempotentCommand`
- generation/finalization/expiry.

#### `appendAuditEvent`
- generation/expiry lifecycle proof.

#### `requestNotification`
- optional approved ready/failure notice.

### Domain Logic

1. request must be `type=export`, `status=verified`;
2. create/fetch semantic bundle at `queued`;
3. transition to `generating`;
4. enumerate owner export serializers;
5. if required owner section cannot be produced, fail/wait according to approved export completeness policy; do not silently omit;
6. assemble approved artifact/manifest;
7. ask Media to store/finalize private asset;
8. verify returned Media reference through owner interface;
9. only then set `mediaAssetId`, `generatedAt`, `expiresAt`, `status=ready`;
10. download decision rechecks actor ownership, bundle status, expiry;
11. Media issues short-lived access;
12. expiry sets bundle `expired` and requests Media cleanup;
13. Media cleanup failure remains operational/retryable; bundle does not become accessible again.

### Authorization / Compliance

- requester owns bundle;
- admin role alone does not grant download;
- sensitive admin access is separately authorized;
- signed URL issuance is audited;
- no entitlement gate;
- export contents must exclude nonexportable secrets/credentials/security material according to owner serializer;
- telemetry redacts contents.

### Database / Transaction Behavior

- request/bundle lock during generation claim;
- Media network/storage call outside DB transaction;
- final `ready` write only after valid Media result;
- bundle status + Media ref/timestamps transactionally written;
- expiry row lock prevents generation/expiry conflict;
- outbox event, if approved, written with `ready` commit.

### Events / Jobs

Jobs:

- export generation;
- expiry;
- cleanup retry/reconciliation.

Proposed event if approved:

```text
privacy.export.ready
```

Notification after source commit only.

### Provider Integration

No direct provider.

Media may call R2/S3 behind its adapter.

### UI / Admin Surface

Requester:

- generation status;
- ready download control;
- expired state;
- failure state with approved retry/support guidance.

Admin:

- safe generation failure/attempt metadata;
- no default file-content preview.

### Failure Behavior

- owner serializer retryable failure → job retry;
- owner serializer terminal/unsupported → bundle not `ready`;
- Media create/finalize failure → bundle not `ready`;
- signed URL issuance failure → bundle can remain `ready`, access attempt fails and is observable;
- expired bundle → deny new issuance;
- cleanup failure → retry; bundle remains expired;
- stale UI button → server still denies.

### Tests

**Unit**
- lifecycle;
- expiry;
- access decision;
- safe section filtering.

**Contract**
- owner export serializer;
- Media artifact result;
- signed URL handoff.

**Integration**
- ready bundle has valid Media reference;
- signed access;
- cleanup request;
- audit;
- Notification request does not own state.

**Security**
- cross-user denial;
- no permanent URL;
- no signed URL/log payload;
- no export body telemetry.

**E2E**
- verified export → ready → download access → expired denial.

### Documentation Updates

- progress tracker;
- if PR-08-04/U-08-22 approved during implementation, update architecture first then add migration;
- record export serializer coverage.

### Acceptance Criteria

- Privacy owns bundle state, Media owns artifact;
- bundle ready only after Media finalization;
- access re-authorized at issuance;
- access short-lived/audited;
- expiry blocks future access;
- no direct object storage code.

### Exit Gate

- CL-08 Feature 05 exit criteria pass;
- all tests pass;
- no orphan Media ref intentionally created;
- no false `ready`;
- unresolved U-08-22 remains explicitly recorded if not approved.

---

# Phase 3 — Decision-Gated Domain Completion

## 05 Complete Privacy Request Semantics

> **Decision-Gated Feature:** do not start until the required CL-08 decisions are approved and the Module/Cluster architecture is updated.

### Objective

Complete production semantics for all declared request types and the full `PrivacyRequest` lifecycle.

### Observable Result

Supported users can complete approved workflows for:

- access;
- export;
- erasure;
- correction;
- restriction;

with accurate verification, deadlines where required, cancellation/rejection where allowed, target-level proof, and aggregate terminal status.

### Cluster Build-Plan Link

Supports CL-08 **Feature 06 — Complete Privacy Request Semantics**.

### Dependencies

Module Features 01–04.

Required approved decisions:

- U-08-01;
- U-08-02;
- U-08-03;
- U-08-04;
- U-08-05;
- U-08-06;
- U-08-07;
- U-08-08 as needed for erasure completion;
- U-08-09 if completion wording depends on backup state.

### In Scope

Only after decisions:

- Identity verification orchestration;
- full transition graph;
- request cancellation/rejection;
- access-request behavior;
- correction executor/results;
- restriction executor/results;
- approved due date/jurisdiction/version logic;
- approved aggregate completion;
- active-request conflict behavior;
- final User handoff if part of approved erasure;
- updated user/admin UI;
- approved notifications/events.

### Out of Scope

- changing source Module retention law;
- generic legal decision engine;
- universal admin override;
- backup semantics not approved;
- creating source-module correction/restriction repositories inside Privacy.

### Module-Owned Data

Current Privacy records plus only approved migrations, potentially:

- identity-verification evidence reference;
- jurisdiction/policy version;
- deadline extension proof;
- correction/restriction target proof/status model;
- active-request conflict constraints;
- completion metadata.

Do not choose columns merely because this plan lists the concepts.

### Public Interfaces

Complete only as approved:

```ts
verifyPrivacyRequestIdentity(...)
cancelPrivacyRequest(...)
rejectPrivacyRequest(...)
processDataAccessRequest(...)
processDataCorrectionRequest(...)
processDataRestrictionRequest(...)
completePrivacyRequest(...)
```

Existing submit/read/export interfaces remain.

### Shared Operations Used

- `resolveAuthenticatedActor`
- `authorizeResourceAction`
- approved Identity privacy-verification interface
- `requireStepUpForSensitiveAction` only if approved
- `transitionLifecycleState`
- `executeIdempotentCommand`
- `orchestratePrivacyFulfillment`
- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `reconcileWorkflowStatus`
- `enqueueReliableJob`
- `requestNotification`
- `appendAuditEvent`
- `recordSensitiveAccess`
- `publishDomainEvent` only for registered event names.

No local replacements.

### Domain Logic

Implement the **approved** transition matrix exactly.

The resulting design must define:

- what proof moves `submitted/verifying_identity` to `verified`;
- access request result vs export artifact;
- target/result model for correction/restriction;
- what retained targets mean for request completion;
- cancellation/rejection eligibility/authority;
- due date source/version;
- active conflicting request behavior;
- final account disposition;
- what is communicated about backup persistence.

### Authorization / Compliance

- self-service identity verification is separate from ordinary login;
- admin rejection/cancellation is explicitly authorized and policy-bound;
- no entitlement gate;
- Consent does not substitute for identity proof;
- ComplianceHold interaction follows approved legal policy;
- correction/restriction remains owner-executed.

### Database / Transaction Behavior

- implement approved constraints/migrations only;
- request transition uses aggregate lock/CAS;
- active-request uniqueness enforced only if approved;
- verification reference and transition written atomically where possible;
- target proof model transactionally records correction/restriction result;
- final request completion transaction verifies child-state invariants.

### Events / Jobs

Approved request-type workers.

If PR-08-03 has been approved and registered, events may include:

```text
privacy.request.verified
privacy.request.completed
```

Deadline worker only after U-08-06.

### Provider Integration

Identity provider verification remains Identity-owned.

All data/provider execution remains source-owner-owned.

### UI / Admin Surface

Requester:

- verification step;
- request-specific result;
- authoritative due date if applicable;
- correction/restriction status;
- safe rejection/cancellation explanation where approved.

Admin/legal:

- policy-versioned controls;
- explicit authority;
- no unrestricted personal payload.

### Failure Behavior

- verification failure → approved state/reason, not invented;
- conflicting active request → approved conflict/merge behavior;
- missed deadline → approved escalation, not hidden;
- correction/restriction unsupported by owner → explicit unresolved/partial per approved policy;
- retained target → approved aggregation;
- admin action without authority → deny.

### Tests

**Transition matrix**
- every legal/illegal transition.

**Request type**
- access, export, erasure, correction, restriction.

**Verification**
- valid/invalid/stale proof.

**Deadline**
- jurisdiction/policy/version.

**Authority**
- cancellation/rejection matrix.

**Aggregation**
- erased/anonymized/retained/skipped/failed combinations.

**Concurrency**
- duplicate/conflicting requests.

**E2E**
- each enabled request type.

### Documentation Updates

Mandatory:

- update Module architecture with each approved decision;
- update CL-08 architecture/build plan if sequencing/contract changed;
- update Prisma/schema docs;
- update public dependency contracts;
- progress tracker includes approval references.

### Acceptance Criteria

- no hidden unresolved semantics;
- every request type has explicit target/aggregate proof;
- final state is derivable from approved rules;
- legal deadline logic is versioned;
- cancellation/rejection is authorized;
- source ownership remains intact.

### Exit Gate

- all required U-08 decisions approved in architecture;
- all enabled request types pass E2E;
- no direct cross-Module mutation;
- no guessed legal policy remains;
- CL-08 Feature 06 exit gate passes.

---

# Phase 4 — Module Integration

## 06 Location Safety Privacy Executor Integration

### Objective

Integrate Location Safety as a first-class participant in Privacy subject inventory and disposition without absorbing Location Safety truth.

### Observable Result

Privacy coverage diagnostics can show Location Safety records for a subject/context and can execute the approved privacy disposition through Location Safety's executor. Public fuzzy projection changes/removal propagate through Search via Location Safety/Search ownership.

### Cluster Build-Plan Link

Supports the Privacy half of CL-08 **Feature 08 — Location Revocation, Privacy Executor, and Gate-Change Reconciliation**, and contributes to Feature 10 coverage.

This Module feature cannot force CL-08 Feature 08 to start before Location Safety's prerequisites/decision gates.

### Dependencies

- Module Feature 02;
- Module Feature 03 for real target orchestration;
- Location Safety Feature 03/07 as required by CL-08 sequencing;
- Location Safety implementation of:
  - `enumerateSubjectData`
  - `evaluateRetentionRequirement`
  - `executePrivacyInstruction`
- approved U-08-21 retention policy;
- approved U-08-23 target-type strategy for production.

### In Scope

- register Location Safety executor;
- contract tests;
- include Location Safety inventory in coverage;
- dispatch Privacy instruction;
- record Privacy-owned target/exemption result;
- verify Search effect occurs through Location Safety/Search public interfaces;
- correlation/ops linkage.

### Out of Scope

- Location fuzzing algorithm;
- exact reveal decision;
- revocation policy;
- Booking/Order gate logic;
- direct `FuzzyLocationCache`/`LocationReveal` repository access;
- direct Search mutation;
- guessing location retention.

### Module-Owned Data

Privacy:

- `DataErasureTarget`
- `DataRetentionExemption`
- job/request aggregate records as applicable.

Location-owned records remain external.

If PR-08-05 is approved, schema migration for explicit target types belongs to approved schema change; Privacy then recognizes them.

### Public Interfaces

Consume Location executor contracts only.

No new location public API is defined here.

### Shared Operations Used

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `validateOwnedTargetReference`
- `executeIdempotentCommand`
- `enqueueReliableJob`
- `appendAuditEvent`
- `recordIntegrationFailure`
- Search refresh remains through Search/Location path.

### Domain Logic

- Location executor advertises supported target types/actions;
- Privacy inventories through it;
- owner returns retention facts;
- Privacy records exemption if required;
- owner performs erase/anonymize/revoke/invalidate action;
- Privacy maps normalized result to target status;
- if Search projection must change, Location/Search owners perform that work;
- no exact location value enters Privacy target descriptor/log.

### Authorization / Compliance

- system executor call is authorized by the privacy workflow;
- manual admin access remains separately authorized;
- retention must follow U-08-21;
- no arbitrary deletion of safety proof;
- no exact location in audit/telemetry.

### Database / Transaction Behavior

- Privacy target/exemption transaction only after Location result;
- no cross-Module transaction;
- replay-safe target execution;
- if Location result is retryable, Privacy does not claim terminal success.

### Events / Jobs

Use canonical job and retry.

Location may publish its own approved events; Privacy consumes only when explicitly required.

### Provider Integration

None in Privacy.

### UI / Admin Surface

Coverage diagnostic:

```text
Location Safety
target types
protocol version
retention-policy status
executor implemented/decision-gated/failed
```

No exact coordinates or addresses.

### Failure Behavior

- U-08-21/23 unresolved → production path shows `decision_gated`;
- Location unavailable → retryable;
- Location says retained → exemption required;
- Search failure behind Location/Search → Privacy target cannot be falsely successful if Search deletion is part of required owner result contract;
- unsupported target → explicit coverage failure.

### Tests

- Location executor contract;
- inventory;
- erase/anonymize/retain result;
- no direct Location Prisma access;
- no exact location payload;
- Search failure propagation as normalized owner result;
- idempotent replay.

### Documentation Updates

- mark U-08-21/23 approved only with architecture change;
- update coverage matrix;
- progress tracker;
- dependency interface docs.

### Acceptance Criteria

- Location participates through canonical privacy protocol;
- Privacy never owns Location tables/policy;
- retained Location target has Privacy exemption;
- public projection cleanup remains Search/Location-owned;
- exact location never enters Privacy payload/log.

### Exit Gate

- required Location decisions approved for production, or path remains explicitly disabled;
- contract/integration tests pass;
- CL-08 Feature 08 Privacy executor criteria pass.

---

## 07 Search, Media, Audit, Notification, and Ops Bridge Integration

### Objective

Replace early mocks with real cross-cutting owner interfaces so Privacy-driven de-indexing, Media deletion/export access, audit proof, notifications, and operational failures work end to end.

### Observable Result

- erasure can remove a public Search projection through Search;
- Media erasure failure prevents false target success;
- export uses real private Media artifact/signed access;
- Privacy sensitive access appears in Audit;
- approved status notification is delivered through Notification;
- failed owner/provider work appears in Ops;
- correlation IDs connect the chain without moving source truth.

### Cluster Build-Plan Link

Supports CL-08 **Feature 09 — Search, Media, Audit, Notification, and Ops Bridges**.

### Dependencies

- Module Features 03–04;
- real Search interface;
- real Media privacy executor/artifact/signed access;
- real Audit interfaces;
- real Notification request interface;
- real Ops failure interface;
- canonical outbox/jobs if events are enabled.

### In Scope

- integration adapters/clients to **Module public interfaces**, not provider SDKs;
- Search privacy refresh/de-index contract;
- Media privacy executor and export artifact;
- Audit append/sensitive access;
- Notification request;
- Ops failure/correlation;
- integration and E2E tests.

### Out of Scope

- Search internals;
- Media storage/scanning internals;
- Audit table design;
- Notification provider configuration;
- Sentry/Ops platform internals;
- direct Typesense/R2/SES calls.

### Module-Owned Data

No new ownership.

Validate boundaries:

- SearchUpsertEvent stays Search;
- MediaAsset/MediaAccessGrant stay Media;
- AuditEvent/AccessAuditLog stay Audit;
- Notification/Delivery stay Notification;
- QueueJob/IntegrationFailure stay Ops.

### Public Interfaces

Consume:

```text
requestSearchProjectionRefresh
Media privacy executor
Media private artifact create/finalize
issueSignedMediaUrl
appendAuditEvent
recordSensitiveAccess
requestNotification
recordIntegrationFailure
```

### Shared Operations Used

All above plus:

- `executeIdempotentCommand`;
- `enqueueReliableJob`;
- `publishDomainEvent`/`deduplicateDomainEvent` only for approved events;
- request/correlation/telemetry operations.

### Domain Logic

- owner truth commits before nonauthoritative notification;
- Search acknowledgement is not owner-data erasure;
- Media deletion is part of Media target success and must succeed before Privacy marks that target erased;
- export bundle `ready` only after Media artifact valid;
- audit proof remains separate from target/request state;
- Notification failure does not change request status;
- Ops failure is supplemental;
- all cross-Module calls carry correlation/causation where supported.

### Authorization / Compliance

- export access authorization remains Privacy + Role;
- Media only receives authorized access request;
- admin Audit/Ops view has its own authority;
- notification payload minimized;
- Search receives target/projection intent, not private payload;
- no personal export body in Ops.

### Database / Transaction Behavior

- Privacy source transaction completes before asynchronous Search/Notification dispatch;
- event/outbox if approved;
- target status waits for required synchronous owner-executor result or reconciled async result according to contract;
- no distributed transaction across Modules/providers.

### Events / Jobs

Real reliable jobs/inbox/outbox.

Search and provider reconciliation remain in their owners.

Privacy may run its own target/job reconciliation only.

### Provider Integration

None in Privacy.

### UI / Admin Surface

- job detail links correlation ID;
- safe Audit references;
- safe Ops failure status;
- Notification delivery status only if root admin UI exposes it;
- no provider payload dump.

### Failure Behavior

- Search unavailable → retry via Search/Ops; required projection target not falsely complete;
- Media delete unavailable → target stays unresolved/failed;
- Media signed URL unavailable → bundle may remain ready but access fails;
- Notification failure → Privacy truth unchanged;
- Audit failure → follow root criticality policy;
- Ops recording failure → no business-state substitution.

### Tests

**Contract/integration**
- Search refresh;
- Media delete/artifact/signed access;
- Audit append;
- sensitive access;
- Notification request;
- IntegrationFailure.

**E2E**
- erasure removes representative public Search result;
- export ready/download audit;
- Media deletion failure does not produce target erased.

**Security**
- no provider clients in Privacy package;
- no exact/sensitive payload in notifications/logs.

### Documentation Updates

- dependency public interfaces;
- progress tracker;
- architecture only if bridge semantics change;
- PR-08-04 migration only if approved.

### Acceptance Criteria

- all five owner bridges are real public-interface calls;
- no direct provider calls;
- state/evidence ownership remains separate;
- correlation preserved;
- failure semantics are correct.

### Exit Gate

- CL-08 Feature 09 Privacy criteria pass;
- integration/E2E tests pass;
- provider-import lint/architecture check finds no forbidden SDK in Privacy;
- no source-of-truth transfer.

---

## 08 Full Data-Owner Executor Coverage

### Objective

Reach production-ready executor coverage for every currently modeled Privacy target family and make missing/decision-gated coverage impossible to hide.

### Observable Result

Authorized developer/admin diagnostic reports each current `DataErasureTargetType` as:

```text
implemented
unsupported_by_policy
decision_gated
or failed
```

with explicit owner Module, protocol version, retention-policy status, provider dependency, and contract-test status.

Representative full erasure spans several Clusters using only public contracts.

### Cluster Build-Plan Link

Supports the Privacy half of CL-08 **Feature 10 — Full Data-Owner Executor Coverage and Booking/Order Location Contracts**.

This Module does not implement the Booking/Order Location contracts themselves; Location Safety consumes those. Privacy only requires Location Safety's privacy executor.

### Dependencies

- Module Features 02–07;
- relevant neighboring Module architectures/public interfaces;
- production executor implementations or explicit decision gates.

### In Scope

Coverage for current target owners:

- Identity & Access;
- Customer / Buyer Profile;
- Track Subscription & Entitlement;
- Messaging;
- Notification;
- Media / File Access;
- Search / Public Visibility;
- Video Infrastructure;
- Payment / Payout / Tax;
- Booking & Calendar;
- Digital Goods Access;
- Transaction / Order/Agreement;
- Location Safety once U-08-21/23 approved.

Also:

- startup/CI executor registry completeness check;
- protocol-version compatibility;
- representative owner retention decisions;
- representative provider deletion normalized results;
- bounded inventory/performance checks.

### Out of Scope

- new target families not evidenced in schema/registry;
- refactoring neighbor lifecycles;
- universal polymorphic FK;
- generic privacy crawler;
- direct provider SDK;
- making `postgres_profile` ambiguity disappear without approved owner mapping.

### Module-Owned Data

No new domain model required for the coverage dashboard unless root architecture approves a rebuildable diagnostic projection. The source is executor registration/config plus test results.

`DataErasureTargetType` remains Privacy-owned vocabulary.

### Public Interfaces

Prove for each target family:

```text
enumerateSubjectData
evaluateRetentionRequirement
executePrivacyInstruction
validateOwnedTargetReference
export serializer where applicable
```

### Shared Operations Used

- all privacy executor protocol operations;
- `deleteProviderResource` through owners;
- `executeIdempotentCommand`;
- `enqueueReliableJob`;
- `queryOwnerFacts`;
- `recordIntegrationFailure`;
- `requestSearchProjectionRefresh` where owner result requires it;
- Media/Audit interfaces.

### Domain Logic

- every target type maps to exactly one executor owner for a given descriptor;
- ambiguous families require explicit descriptor owner and cannot execute if owner is not durable/validated;
- `other` has no generic handler;
- coverage check fails CI for required production target with no owner;
- executor versions are explicit;
- inventory is paginated/bounded;
- owner result evidence is normalized;
- Privacy never reconstructs provider status itself.

### Authorization / Compliance

- coverage diagnostic is developer/admin-only;
- diagnostic contains no raw subject data;
- owner executor still validates subject/target authority;
- retention basis is owner-provided;
- no support/admin universal read.

### Database / Transaction Behavior

No cross-owner writes.

Representative integration fixtures may seed neighbor data through their public test fixtures or approved setup APIs. Do not write neighbor tables from Privacy tests as implementation behavior.

### Events / Jobs

Cross-cluster contract suite runs in CI.

Large representative erasure journey uses normal jobs/retries.

### Provider Integration

Provider owner contract tests may use sandbox/fakes in their own Modules. Privacy only tests normalized results.

### UI / Admin Surface

Coverage matrix:

```text
target type
owner Module
protocol version
enumeration
retention
execution
export
provider dependency
status
blocker ID
last contract-test status
```

No raw subject data.

### Failure Behavior

- missing owner → CI/diagnostic failure;
- unsupported policy → explicit supported state, not silent skip;
- decision-gated → explicit blocker ID;
- executor version mismatch → fail closed;
- ambiguous target owner → fail closed;
- provider unavailable → normalized retryable result;
- owner reports target absent → map according to approved target contract, not automatic erase.

### Tests

**Contract**
- one suite per owner/target family;
- protocol version;
- normalized error/result.

**Coverage**
- every enum value mapped or explicitly decision-gated;
- `other` has no generic delete handler.

**Integration**
- representative erasure spanning Identity/Customer/Media/Search/Messaging plus other approved set;
- retained financial/contract example;
- provider deletion result translation.

**Performance**
- pagination/large inventory;
- batch target registration.

**Security**
- no raw payload in diagnostic.

### Documentation Updates

- target owner matrix;
- progress tracker;
- dependency interface status;
- if schema needs durable `ownerModule`/target fingerprint fields, update architecture before migration.

### Acceptance Criteria

- no current target type is silently unsupported;
- each production-required owner passes contract suite;
- missing executor is visible in CI;
- provider deletion remains owner-controlled;
- direct cross-Module database access does not exist.

### Exit Gate

- CL-08 Feature 10 Privacy criteria pass;
- all required target types implemented or explicitly decision-gated;
- representative cross-cluster erasure E2E passes;
- coverage dashboard/CI cannot hide gaps.

---

# Phase 5 — Hardening and Production Verification

## 09 Security, Reconciliation, Concurrency, and Production Hardening

### Objective

Prove Privacy / Data Erasure remains correct under retries, duplicate delivery, concurrency, stale target state, dependency/provider outages, export expiry/cleanup failure, migrations, and sensitive-data access.

### Observable Result

- destructive effects are replay-safe;
- stuck jobs/targets are visible and reconcilable;
- no hidden partial success;
- retained target proof is complete;
- export access cannot outlive Privacy expiry;
- public Search cleanup is reconciled through Search;
- operators have safe diagnostic/manual-review paths;
- legal-gated request types remain disabled unless their decisions are approved;
- launch checklist records exact enabled capabilities and remaining blockers.

### Cluster Build-Plan Link

Supports the Privacy portion of CL-08 **Feature 11 — Security, Reconciliation, Privacy, and Production Hardening**.

### Dependencies

- Module Features 01–08;
- all production-bound required U-08 decisions approved or affected paths disabled;
- production shared operations;
- real owner executors;
- root health/incident/security policy;
- approved migration/backfill plan if schema changes exist.

### In Scope

#### Privacy reconciliation
- stalled request/job/target diagnostics;
- target replay/reconciliation;
- export orphan/cleanup reconciliation;
- executor version compatibility;
- retention-exemption completeness scan;
- Search-required target reconciliation through Search owner;
- owner/provider result mismatch detection;
- manual-review routing.

#### Concurrency/idempotency
- duplicate web submit;
- duplicate erasure start;
- duplicate target;
- duplicate owner result;
- two target workers;
- two reconcilers;
- duplicate export generation;
- generation/expiry race;
- late result after terminal state.

#### Security/privacy
- authorization/RLS where applicable;
- service-role scope;
- telemetry redaction;
- signed URL leakage checks;
- secret/import boundary check;
- rate limiting through root mechanism;
- destructive command confirmation/idempotency;
- admin sensitive-access policy.

#### Migration/backfill
- only approved schema changes;
- dry run;
- rollback;
- verification before destructive cleanup.

### Out of Scope

- unapproved new privacy laws;
- provider families not represented in architecture;
- redesigning neighbor Modules;
- enabling a decision-gated workflow just to satisfy launch tests;
- generic legal automation.

### Module-Owned Data

Review/index current models.

Approved migrations may include only decisions already recorded, such as:

- explicit Media relation;
- approved verification/policy fields;
- approved correction/restriction proof;
- approved uniqueness/version fields;
- approved target types.

No migration is justified solely by this hardening feature.

### Public Interfaces

No broad new API.

May add authorized diagnostics:

```text
getPrivacyReconciliationStatus
retryPrivacyWork
getExecutorCoverage
```

Retry/manual actions must call existing idempotent workflows and preserve authority.

### Shared Operations Used

Especially:

- `executeIdempotentCommand`
- `deduplicateDomainEvent`
- `enqueueReliableJob`
- `executeRetryWithBackoff`
- `reconcileWorkflowStatus`
- `acquireAggregateLock`
- `withOptimisticConcurrency`
- `runDeadlineExpiration`
- `recordIntegrationFailure`
- `checkServiceHealth`
- `correlateOpsIncident`
- `sanitizeTelemetryMetadata`
- `appendAuditEvent`
- `recordSensitiveAccess`
- Search/provider reconciliation through their owners.

### Domain Logic

#### Stalled work

Classify:

```text
awaiting approved decision
awaiting owner
retryable dependency
dead-letter/manual review
terminal domain failure
ready for reconciliation
```

Do not map all stalled work to `failed`.

#### Target reconciliation

- revalidate owner target;
- query owner evidence/result if protocol supports reconciliation;
- never repeat destructive call unless idempotency identity proves safe;
- target state changes only through Privacy transition policy.

#### Export reconciliation

- bundle ready must point to valid private Media artifact;
- expired bundle must not issue access;
- orphan Media artifact cleanup requested through Media;
- missing artifact for `ready` bundle is invariant failure/manual repair, not silent regeneration.

#### Retention completeness

Every `retained` target must have at least one valid exemption based on owner facts.

#### Search

If privacy requires a Search projection removal and Search reports stale/missing execution, request/reconcile through Search. Do not call provider.

#### User/backups

Enforce only approved U-08-08/09 behavior. If unresolved, destructive final account/backup claims remain disabled.

### Authorization / Compliance

Explicit review:

- self-service vs admin Privacy access;
- export content access;
- retained legal records;
- Audit/Ops access;
- service-role scope;
- provider secret boundary;
- rate limiting;
- data minimization;
- irreversible action safety;
- enabled legal request types and approved policy versions.

### Database / Transaction Behavior

- stress DB locks;
- detect deadlocks/timeouts and safe retry;
- verify no duplicate target/business effect;
- use bounded batch/cursor scans;
- approved migrations staged;
- destructive backfill has dry-run and rollback;
- parent cascade behavior tested so Privacy proof cannot be accidentally deleted.

### Events / Jobs

- reconciliation worker;
- stuck-work scanner;
- export expiry/cleanup reconciliation;
- target retry/dead-letter;
- approved deadline scanner only if U-08-06 resolved.

Outbox/inbox replay tests if events enabled.

### Provider Integration

None directly.

Provider outage simulations arrive through owner executor normalized responses.

### UI / Admin Surface

Production diagnostics:

- request/job/target state;
- retry/dead-letter/manual review;
- owner executor status;
- retention proof status;
- export artifact/access state;
- correlation ID;
- safe dependency health.

No raw export/private content.

### Failure Behavior

- provider owner unavailable → bounded retry, no false success;
- owner contract unavailable → job/target remains unresolved;
- repeated terminal failure → manual review/terminal Privacy state per approved policy;
- Search unavailable → owner/source erasure truth preserved; required Search target remains unresolved until Search acknowledgement;
- Media unavailable → required Media target/bundle cannot be falsely successful;
- Audit unavailable → approved root criticality behavior;
- migration anomaly → stop destructive phase;
- security/key issue → deny sensitive access.

### Tests

**Security**
- authorization;
- admin access matrix;
- signed URL leakage;
- telemetry redaction;
- secret/provider import boundary;
- rate-limit behavior if configured;
- service-role scope.

**Concurrency/idempotency**
- duplicate request;
- duplicate jobs;
- duplicate events;
- target workers;
- reconciliation overlap;
- export race.

**Privacy/compliance**
- retained target exemption;
- no hidden target failure;
- no soft-delete shortcut;
- no User hard-delete if unresolved;
- no backup false claim;
- export expiry;
- target-owner coverage.

**Failure/reconciliation**
- provider/owner outage;
- Search lag/failure;
- Media deletion failure;
- orphan bundle;
- dead-letter recovery;
- owner result replay.

**Performance**
- large subject inventory pagination;
- large target job batching;
- worker scan indexes;
- admin diagnostic bounds.

**E2E**
- full approved erasure journey;
- export journey;
- access/correction/restriction only if enabled;
- representative multi-cluster owner coverage.

### Documentation Updates

- final progress tracker status;
- enabled/disabled legal-gated capabilities;
- approved decision IDs/versions;
- migrations/backfills;
- residual risks;
- runbooks/ops references where root context supports them;
- architecture changes only for actual binding decisions.

### Acceptance Criteria

- no enabled path relies on unresolved architecture;
- all destructive work is idempotent and observable;
- all retained targets have proof;
- no required owner/provider failure is hidden;
- export is private, short-lived, audited, and cleaned/reconciled;
- cross-Module ownership preserved;
- production diagnostics are safe;
- all required quality checks pass.

### Exit Gate

Module production readiness passes only when:

- all enabled request types have approved lifecycle/policy and E2E tests;
- Features 01–08 exit gates passed;
- coverage matrix has no hidden production gaps;
- typecheck passes;
- lint/format passes;
- unit tests pass;
- contract tests pass;
- integration tests pass;
- database/migration tests pass;
- concurrency/idempotency tests pass;
- security/privacy/compliance tests pass;
- critical E2E tests pass;
- provider-boundary checks pass;
- progress tracker records remaining disabled decision-gated features and risks.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --------- | -------- | ------------ |
| Phase 1 | Contracts and Source-of-Truth Foundation | 01 Privacy Request Intake and Status Surface; 02 Privacy Executor Protocol and Subject-Data Inventory |
| Phase 2 | Core Lifecycle and Fulfillment | 03 Verified Erasure Orchestration and Retention Proof; 04 Privacy Export Bundle and Secure Delivery |
| Phase 3 | Decision-Gated Domain Completion | 05 Complete Privacy Request Semantics |
| Phase 4 | Module Integration | 06 Location Safety Privacy Executor Integration; 07 Search, Media, Audit, Notification, and Ops Bridge Integration; 08 Full Data-Owner Executor Coverage |
| Phase 5 | Hardening and Production Verification | 09 Security, Reconciliation, Concurrency, and Production Hardening |

**Total features: 9**

### Cluster sequencing correspondence

| Module feature | CL-08 feature(s) |
|---|---|
| 01 | CL-08 01 |
| 02 | CL-08 02 |
| 03 | CL-08 04 |
| 04 | CL-08 05 |
| 05 | CL-08 06 |
| 06 | CL-08 08 and 10 Privacy participation |
| 07 | CL-08 09 |
| 08 | CL-08 10 Privacy participation |
| 09 | CL-08 11 Privacy participation |

CL-08 Features 03 and 07 are Location Safety-owned and are intentionally not duplicated here.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root `project-overview.md`.
2. Read root architecture.
3. Read root `code-standards.md`.
4. Read Canonical Shared Operations Registry.
5. Read CL-08 architecture.
6. Read CL-08 build plan.
7. Read this Module architecture.
8. Read this Module implementation plan.
9. Read direct dependency public-interface sections for the current feature.
10. Read current progress tracker.
11. Confirm the prior Module exit gate and the corresponding Cluster sequence.
12. Check all required U-08/Proposed Ruling decision gates.
13. Write the concise feature implementation specification.
14. Implement only that feature.
15. Run required quality checks.
16. Verify public contracts and ownership boundaries.
17. Update progress.
18. Update architecture first if a binding decision legitimately changed.
19. Record unresolved risks and deferred work.
20. Start the next feature only after the exit gate passes.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- **Feature number/name**
- **Objective**
- **Observable result**
- **Cluster build-plan link**
- **Dependencies**
- **Required approved decision gates**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Schema/migration impact**
- **Public contracts**
- **Shared operations consumed**
- **Permissions/compliance**
- **Primary workflow**
- **Provider integration**
- **Jobs/events**
- **Idempotency/concurrency**
- **Database transaction boundaries**
- **Error/failure behavior**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**
- **Exit gate**

Do not generate detailed specifications for all future features at once. The implementation plan establishes binding sequence and boundaries; the next-feature specification converts only the current feature into coding tasks.

---

# Required Completion Report

After implementing each numbered feature, report:

- **Feature completed**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Shared operations reused**
- **Events/jobs added**
- **Provider adapter changes**
- **Neighbor Module interfaces consumed**
- **Tests added/changed**
- **Commands run**
- **Manual/contract verification**
- **Authorization/compliance verification**
- **Documentation updated**
- **Architecture decisions consumed**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Deferred work**
- **Exit-gate result**

A feature is not complete because code compiles. The exit gate must pass, the public contract must be proven, source-of-truth boundaries must remain intact, and unresolved legal/architecture questions must remain explicit.

---

# Final Quality Check

Before marking the Module implementation plan complete, verify:

1. `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, and `DataExportBundle` each have exactly one owner.
2. No neighboring Module truth was absorbed.
3. Every shared operation is consumed rather than duplicated.
4. Shared mechanism/separate truth boundaries are explicit in code placement and tests.
5. Public commands and queries are owned by Privacy.
6. Data owners are accessed through executor/public interfaces.
7. No provider adapter lives in Privacy.
8. Audit, domain events, and observability remain distinct.
9. Privacy orchestration remains Privacy-owned.
10. Search remains projection and Search-owned.
11. Media remains file/object/signed-access owner.
12. Retention facts come from source owners; Privacy owns exemptions.
13. Feature order matches CL-08 sequencing.
14. Every numbered feature has automated tests and an exit gate.
15. Decision-gated semantics are disabled rather than guessed.
16. A coding agent can implement the next feature without inventing ownership, provider placement, lifecycle truth, or cross-Module access patterns.
