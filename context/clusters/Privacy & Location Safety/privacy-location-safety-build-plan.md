# Privacy & Location Safety Build Plan

> **Repository location:** `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`<br>
> **Cluster ID:** CL-08  
> **Cluster:** Privacy & Location Safety  
> **Companion architecture:** `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`<br>
> **Plan status:** Implementation sequence; decision-gated where architecture/legal policy is unresolved  
> **Total numbered features:** 11

**Shared Operation status:** References use permanent IDs and canonical names from `context/shared/shared-operations.md`; that registry controls owner, classification, status, and reusable boundary. SH-003 queryOwnerFacts remains **Proposed ruling** and is not an unconditional prerequisite or an approved universal DTO/API. Adoption requires separate Shared Operations approval before API/schema commitment. Existing source-owner-specific public queries may be consumed within their approved contracts; direct cross-domain Prisma/repository reads remain prohibited. SH-069 geocodeAddress remains **Proposed ruling** wherever referenced; this pass does not approve it.

### Current context paths and missing artifact roles

Read `context/context-map.md` first for authority by concern, then the existing artifacts relevant to the feature:

- Overview: `context/project-overview-v3.md`.
- Shared Operations: `context/shared/shared-operations.md`.
- Cluster architecture: `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`.
- Cluster build plan: `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`.
- Member Module pairs: use the Privacy / Data Erasure and Location Safety paths in `context/context-map.md`.

Root/repository-root and context-root `architecture.md`, `build-plan.md`, `code-standards.md`, and dedicated `progress-tracker.md` are currently **missing**. References to those global artifacts below describe future roles, not loadable files or current authority. Do not create local substitutes or infer global approval. Apply existing concern owners through the context map; stop work that needs a missing global decision. Until a dedicated tracker is available, report progress/blockers in the task completion report; progress does not approve architecture.

---

## Core Principle

Build CL-08 as a set of vertical, testable privacy and safety controls without turning the Cluster into a third source-of-truth layer.

The implementation pattern is:

```text
observable behavior
→ owning Module application service
→ authoritative Module records
→ public contracts
→ authentication / authorization / compliance gates
→ shared operations
→ owner-specific events / jobs / provider adapters
→ tests
→ exit gate
```

The Cluster coordinates two separate ownership domains:

```text
Privacy / Data Erasure
→ owns privacy request + fulfillment proof

Location Safety
→ owns safe public-location projection + exact-reveal policy/proof
```

A feature may coordinate both Modules, but it must never merge their lifecycles.

Infrastructure work is allowed only where later slices require it. Each infrastructure-oriented feature must produce a concrete observable result such as a public contract test harness, self-service request surface, admin diagnostic view, safe public projection, worker result, or cross-Module integration proof.

Decision-gated features must remain blocked rather than filling missing legal/safety rules with implementation guesses.

---

## Build Rules

1. Follow the CL-08 `architecture.md`.
2. Use `context/context-map.md` for existing concern owners; root architecture/code standards are currently missing.
3. Do not expand CL-08 into a generic compliance framework, identity system, storage system, search system, or map system.
4. Do not redesign Deep Module ownership for implementation convenience.
5. Reuse Canonical Shared Operations. Do not create duplicate auth, authorization, queues, idempotency, audit, crypto, search, file, or provider infrastructure.
6. Every mutation validates runtime input, authenticated actor where applicable, and authorization.
7. Every asynchronous operation is idempotent, retry-safe, correlated, and observable.
8. `DataErasureJob` remains Privacy business truth; generic queue state is operational only.
9. `LocationReveal` remains Location Safety reveal truth; `AccessAuditLog` is separate evidence.
10. Provider SDKs stay behind the provider-owning Module's adapter.
11. Search changes go through Search-owned interfaces.
12. Media object access/deletion goes through Media-owned interfaces.
13. No public location payload contains exact private location.
14. No exact-location result is returned from cached frontend eligibility.
15. Do not implement automated privacy legal deadlines, rejection grounds, retention periods, or reveal predicates until approved.
16. Do not treat Proposed Rulings as approved without an explicit approved architecture decision from the concern owner identified in `context/context-map.md`. Progress records may cite that decision but cannot approve architecture.
17. Every numbered feature ends with automated tests and a concrete exit gate.
18. Do not start the next numbered feature until the current exit gate passes, except when the current feature is explicitly marked **Decision-Gated** and the project owner chooses to pause CL-08 rather than invent the decision.
19. Build-plan progress cannot silently change architecture. Update architecture first when a binding decision changes.
20. Record unresolved blockers in the progress tracker.

---

## Dependencies and Preconditions

### Root/platform prerequisites

CL-08 assumes the root platform can supply, or will supply before the relevant feature:

- Prisma/PostgreSQL migrations and transactions;
- authenticated actor resolution;
- Role / Authority decisions;
- canonical idempotency;
- transactional outbox/inbox;
- reliable jobs and retry/dead-letter handling;
- request/correlation context;
- SH-036 emitMetric and SH-038 recordQueueTelemetry through their canonical Ops/queue owners; consumers retain domain state and safe dimension policy;
- structured logging and telemetry redaction;
- Audit / Event Ledger append interfaces;
- shared encryption and keyed hashing;
- standardized validation/error contracts.

### Shared-operation prerequisites

The following canonical operations are major dependencies:

```text
resolveAuthenticatedActor # SH-001 resolveAuthenticatedActor
authorizeResourceAction # SH-002 authorizeResourceAction
evaluateComplianceHold # SH-011 evaluateComplianceHold
authorizeContextualResourceAccess # SH-026 authorizeContextualResourceAccess
appendAuditEvent # SH-029 appendAuditEvent
recordSensitiveAccess # SH-030 recordSensitiveAccess
executeIdempotentCommand # SH-044 executeIdempotentCommand
publishDomainEvent # SH-046 publishDomainEvent
deduplicateDomainEvent # SH-045 deduplicateDomainEvent
enqueueReliableJob # SH-047 enqueueReliableJob
orchestrateWorkflowSteps # SH-049 orchestrateWorkflowSteps
reconcileWorkflowStatus # SH-050 reconcileWorkflowStatus
transitionLifecycleState # SH-053 transitionLifecycleState
acquireAggregateLock # SH-051 acquireAggregateLock
withOptimisticConcurrency # SH-052 withOptimisticConcurrency
runDeadlineExpiration # SH-055 runDeadlineExpiration
encryptSensitiveValue # SH-075 encryptSensitiveValue
normalizeAndHashIdentifier # SH-076 normalizeAndHashIdentifier
requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
requestMediaAccess # SH-127 requestMediaAccess
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
orchestratePrivacyFulfillment # SH-099 orchestratePrivacyFulfillment
createPrivacyExportArtifact # SH-100 createPrivacyExportArtifact
resolveLocationReveal # SH-027 resolveLocationReveal
applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
validateOwnedTargetReference # SH-123 validateOwnedTargetReference
```

For Confirmed operations, implementation belongs in the canonical owner before the consuming feature. Proposed operations require separate architecture approval before API/schema commitment; SH-003 queryOwnerFacts is not an unconditional prerequisite. Approved narrow source-owner queries remain usable. Do not create a CL-08-only substitute.

### Existing CL-08 schema prerequisites

Current Prisma evidence already defines:

- `PrivacyRequest`
- `DataErasureJob`
- `DataErasureTarget`
- `DataRetentionExemption`
- `DataExportBundle`
- `FuzzyLocationCache`
- `LocationReveal`
- the related enums/statuses.

The build plan must preserve ownership of those records.

### Upstream Module prerequisites

By the time integration features run, the following public interfaces must exist or be testable through approved stubs:

- Identity & Access actor and privacy-verification boundary;
- Role / Authority decisions;
- Booking gate/source-location facts;
- Order gate/participant facts;
- Media delete/export/signed-access interface;
- Search projection refresh interface;
- Audit append/sensitive-access interface;
- Notification request interface;
- privacy executor interfaces in participating data owners.

### Providers

Providers may be stubbed behind ports initially:

- geocoder: provider undecided;
- R2: accessed through Media only;
- Typesense: accessed through Search only;
- Daily/Mux/Agora: accessed through Video only;
- Stripe/payment references: Payment owner;
- subscription billing provider: Track owner;
- Cronofy/calendar: Booking owner.

Provider choice should not block contract/domain tests unless the feature's exit gate explicitly requires production provider verification.

### Unresolved decision gates

The following may not be guessed:

- privacy identity-verification proof model;
- access vs export semantics;
- correction/restriction proof;
- request cancellation/rejection policy;
- statutory due-date/jurisdiction policy;
- retained-target aggregation semantics;
- active-request concurrency policy;
- final User disposition and backup policy;
- exact-location source ownership reconciliation;
- Booking duplicate location fields;
- reveal context, directionality, predicate, revocation, uniqueness, and audit transaction boundary;
- fuzzy production radius/stability/expiry policy;
- Location privacy retention policy.

The first five buildable features deliberately stop before these unresolved outcomes.

---

# Phase 1 — Safe Cluster Foundations

## 01 Privacy Request Intake and Status Surface

Create the first real Privacy / Data Erasure vertical slice: an authenticated User can submit a formal privacy request and read its current status without the system pretending the request has already been legally verified or fulfilled.

### Objective

Make `PrivacyRequest` a real, user-visible source-of-truth record with safe self-service creation and read access.

### User-visible / Observable Result

- Authenticated User can submit one of the modeled request types.
- User can view a request detail and request-history list.
- Request displays its actual source-of-truth status and timestamps.
- Admin/support can view a request only through explicit authority.
- No UI claims verification, legal deadline, erasure, or export completion before those workflows exist.

### Owning Module(s)

- **Privacy / Data Erasure** — owns all business truth in this feature.

### Dependencies

- `PrivacyRequest` schema and enums.
- Identity actor resolution.
- Role / Authority.
- runtime validation.
- Audit / Event Ledger.
- root error/result conventions.

### Shared Operations Used

- `SH-001 resolveAuthenticatedActor` — Identity owner; establishes requester. Privacy supplies no alternate auth helper.
- `SH-002 authorizeResourceAction` — Role / Authority owner; Privacy supplies request ownership/admin context. Do not build `privacyAuth`.
- `SH-044 executeIdempotentCommand` — platform owner; used for submission retry safety. Privacy supplies semantic request fingerprint; do not build local idempotency storage.
- `SH-029 appendAuditEvent` — Audit owner; records sanitized submission/admin actions. Do not create a privacy audit table.
- `SH-032 createRequestContext` / `SH-033 writeStructuredLog` / `SH-034 sanitizeTelemetryMetadata` — platform/Ops; no request-body dumping.

### Data / Schema

Use existing:

- `PrivacyRequest`
- `PrivacyRequestType`
- `PrivacyRequestStatus`

Required indexes already evidenced:

- `[userId, status]`
- `[type, status]`
- `[dueAt]`

Do **not** add a uniqueness constraint for active requests until U-08-07 is resolved.

Do **not** populate `dueAt` from guessed law. It may remain null until an approved policy supplies it.

### Public Interfaces

Implement/complete:

```ts
submitPrivacyRequest(...)
getPrivacyRequest(...)
listUserPrivacyRequests(...)
```

Minimum response fields:

- ID;
- type;
- status;
- `requestedAt`;
- `verifiedAt`;
- `dueAt`;
- `completedAt`;
- safe rejection summary when authorized;
- safe export-bundle summary when later available.

### Logic

- Validate request type against `PrivacyRequestType`.
- Create request at `submitted`.
- Scope read queries to request owner unless authority explicitly permits broader access.
- Preserve server-owned timestamps.
- Do not auto-transition to `verifying_identity` or `verified` until the verification contract exists.
- If repeated network submission uses same idempotency key and same request fingerprint, return original result.
- If same key is reused with a different fingerprint, return idempotency conflict.

### UI / Administrative Surface

Self-service:

- privacy request form;
- request history;
- request detail/status timeline;
- neutral "submitted / processing / completed" copy driven by actual status;
- clear generic state for unresolved/awaiting verification.

Admin/support:

- authorized request list/detail;
- no unrestricted export-content view;
- admin note only if authority policy allows it.

### Authorization / Compliance

- User may read own requests.
- Admin/support access is capability-gated.
- No consent check is used as permission to exercise a privacy right.
- No Track entitlement gates request creation.
- No ComplianceHold is assumed to block request creation.
- Sensitive admin access uses audit policy.

### Events / Jobs / Integrations

No fulfillment job yet.

If root event registry approves PR-08-03, publish `privacy.request.submitted` through the canonical outbox. Otherwise do not invent an event transport.

### Failure Behavior

- invalid request type → validation error;
- anonymous actor → authentication denial;
- unauthorized request ID → not-found/forbidden according to root anti-enumeration policy;
- idempotency conflict → deterministic conflict;
- audit operational failure → follow root audit criticality policy; do not falsely mark request failed unless domain policy says so.

### Tests

Unit:

- request creation defaults;
- safe serialization.

Integration:

- authenticated owner create/read/list;
- admin authorization;
- cross-user denial;
- idempotent submit.

E2E:

- submit request → request appears in history → detail shows `submitted`.

Privacy/security:

- telemetry contains no unnecessary request details;
- no `dueAt` is guessed.

### Out of Scope

- identity verification completion;
- request rejection/cancellation;
- automatic due-date calculation;
- data inventory;
- erasure;
- export generation;
- correction/restriction;
- User hard deletion.

### Exit Gate

Feature 01 passes only when:

- a real `PrivacyRequest` is created through the owning application service;
- the owner can read it and another normal User cannot;
- request history uses authoritative database state;
- duplicate same-key submissions do not create duplicate rows;
- no local auth/audit/idempotency implementation was added;
- no legal deadline or rejection/cancellation policy was invented;
- typecheck, lint, unit, integration, and privacy-request E2E tests pass.

---

## 02 Privacy Executor Protocol and Subject-Data Inventory

Define and prove the cross-Module protocol that lets Privacy discover and instruct personal-data owners without taking ownership of their repositories.

### Objective

Give Privacy a stable, typed way to ask: "What data do you hold about this subject, what dispositions do you support, must any of it be retained, and can you execute this instruction?"

### User-visible / Observable Result

Developer/admin diagnostic surface can run a **dry-run subject inventory** for a test subject and show:

- executor owner;
- target type;
- stable target reference;
- supported privacy actions;
- sensitivity;
- retention-candidate flag;
- cursor/progress;
- errors without exposing raw sensitive payloads.

This is an implementation proof surface, not a legal fulfillment screen.

### Owning Module(s)

- **Privacy / Data Erasure** owns the protocol and inventory orchestration.
- Each participating data-owning Module owns its executor implementation and record meaning.

### Dependencies

- Feature 01.
- Canonical Shared Operations privacy protocol.
- target owner public interfaces.
- request/correlation context.
- validation.
- approved test fixtures.

### Shared Operations Used

- `SH-096 enumerateSubjectData` — each owner implements; Privacy defines protocol. No global DB crawler.
- `SH-097 evaluateRetentionRequirement` — owner supplies facts; Privacy does not encode tax/contract/etc. logic.
- `SH-095 executePrivacyInstruction` — typed execution protocol; no owner creates PrivacyRequest.
- `SH-123 validateOwnedTargetReference` — target owner validates existence/context.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — narrow owner DTOs only.
- `SH-044 executeIdempotentCommand` — used by executor commands.
- `SH-032 createRequestContext`, `SH-033 writeStructuredLog`, `SH-034 sanitizeTelemetryMetadata`.

### Data / Schema

No ownership changes.

Define typed target descriptor containing at minimum:

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

The descriptor is a contract object, not a new universal database table unless root architecture later approves one.

`DataErasureTargetType.other` must require explicit owner identity and may not authorize generic deletion.

### Public Interfaces

Define the canonical protocol contracts:

```ts
enumerateSubjectData(request) // SH-096 enumerateSubjectData
evaluateRetentionRequirement(request) // SH-097 evaluateRetentionRequirement
executePrivacyInstruction(request) // SH-095 executePrivacyInstruction
```

Define normalized result categories:

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

Correction/restriction-specific terminal proof remains decision-gated.

### Logic

- Register executor implementations explicitly by owner Module and supported target types.
- Inventory must be cursorable and bounded.
- Inventory must not include secrets or raw provider payloads.
- Privacy stores only the target references needed for orchestration.
- Owner executor must revalidate target at execution time.
- Provider resources are executed through the provider-owning Module.
- Dry-run does not mutate owner state.

### UI / Administrative Surface

Internal diagnostic page or developer route:

- executor registry status;
- dry-run inventory counts by owner/type;
- unsupported target warnings;
- pagination/cursor state;
- safe failure reasons.

No raw exports or exact-location values on the diagnostic surface.

### Authorization / Compliance

- Diagnostic inventory is admin/developer restricted.
- Subject access follows Role / Authority.
- No executor may expose a target owned by another tenant/subject without owner validation.
- Retention "candidate" is not a final legal exemption.

### Events / Jobs / Integrations

Use `SH-047 enqueueReliableJob` only if inventory size requires async execution; otherwise synchronous dry-run is acceptable for test fixtures.

No provider calls are required in dry-run.

### Failure Behavior

- unknown executor → explicit unsupported-owner failure;
- invalid target type → validation failure;
- cursor failure → retryable operational failure;
- owner timeout → safe retryable result;
- one owner failure does not cause Privacy to guess that no data exists.

### Tests

Contract tests:

- reference fake owner implementation;
- pagination/cursor behavior;
- owner validation;
- result-schema validation;
- unknown target types.

Security tests:

- no cross-owner direct Prisma access;
- no raw secrets in descriptors/logs.

Integration tests:

- at least two owner executors enumerate different records for the same subject.

### Out of Scope

- full executor implementation across all Clusters;
- legal retention rules;
- target mutation;
- exact location reveal;
- final privacy request completion.

### Exit Gate

- protocol types are stable and documented;
- a dry-run inventory spans at least two owner Modules through public interfaces;
- no generic cross-domain repository exists;
- owner executors can be registered without editing Privacy domain policy;
- unsupported owner/type failures are explicit;
- contract/security tests pass.

---

## 03 Fuzzy Public Location Projection

Build the first Location Safety vertical slice: public consumers can receive a safe approximate location backed by `FuzzyLocationCache`, while exact location remains inaccessible.

### Objective

Make `SH-028 applyFuzzyPublicLocation` and `FuzzyLocationCache` real source-backed Location Safety behavior.

### User-visible / Observable Result

A supported public listing/test target can display an approximate map/search location. A developer/admin inspection shows:

- target;
- fuzzy coordinates;
- radius;
- generated time;
- expiry;
- source version/policy version where available.

The exact input location is never returned by the public interface.

### Owning Module(s)

- **Location Safety** owns the projection and precision policy.
- Source Module continues to own the source location.

### Dependencies

- `FuzzyLocationCache`.
- `LocationPrecision`.
- owner-fact interface for the selected test target.
- shared validation/idempotency/concurrency.
- optional stub geocoder.
- Search refresh interface may be mocked until cross-cluster phase.

### Shared Operations Used

- `SH-028 applyFuzzyPublicLocation` — Location Safety canonical public interface; no consumer-side fuzzing.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` / `SH-123 validateOwnedTargetReference` — get source location safely.
- `SH-044 executeIdempotentCommand` — duplicate refresh safety.
- `SH-051 acquireAggregateLock` or `SH-052 withOptimisticConcurrency` — one projection per target.
- `SH-069 geocodeAddress (Proposed ruling; adoption gated)` — only behind Location-owned port if needed; provider may be stubbed.
- `SH-091 requestSearchProjectionRefresh` — invoked through Search contract, not direct index call.
- `SH-046 publishDomainEvent` / `SH-047 enqueueReliableJob` only if approved for refresh/expiry.
- `SH-034 sanitizeTelemetryMetadata` — exact location omitted from logs.

### Data / Schema

Use existing `FuzzyLocationCache`:

- unique `[targetType, targetId]`;
- `fuzzyLat`;
- `fuzzyLng`;
- `radiusMeters`;
- `generatedAt`;
- `expiresAt`.

Do not add a broad `LocationTargetType` enum until U-08-18 is resolved.

Implementation must use an explicit supported-target registry in application configuration/tests. Unsupported target types fail closed.

### Public Interfaces

Implement/complete:

```ts
applyFuzzyPublicLocation(...) // SH-028 applyFuzzyPublicLocation
getPublicLocationProjection(...)
refreshFuzzyLocationProjection(...)
invalidateFuzzyLocationProjection(...)
```

`getPublicLocationProjection` never returns exact/source location.

### Logic

- Require source owner to supply location or protected location reference.
- Apply only an explicitly configured Location Safety policy.
- If no approved production policy exists for a target type, return `policy_not_configured` and do not write a production projection.
- Test/staging may use explicit fixtures to prove mechanics.
- Refresh replaces the single target projection atomically.
- Invalidate removes/marks unavailable according to approved repository behavior.
- Search refresh is requested after successful source-of-truth commit.

### UI / Administrative Surface

- internal projection inspector;
- public map/list fixture using fuzzy payload only;
- explicit unavailable state when policy is not configured.

### Authorization / Compliance

- public query returns only safe projection.
- admin diagnostic may see metadata, not exact coordinates unless separately authorized.
- no frontend precision override.
- no map provider receives exact private coordinates for public rendering.

### Events / Jobs / Integrations

Optional approved events:

```text
location.public_projection.updated
location.public_projection.invalidated
```

Expiry worker may use `SH-055 runDeadlineExpiration` when policy exists.

Geocoder is stubbed/provider-neutral for this feature.

### Failure Behavior

- missing source facts → no projection;
- unsupported target type → fail closed;
- policy missing → no production projection;
- geocoder timeout → retryable operational failure, no stale replacement;
- concurrent refresh → lock/CAS behavior; last valid source version wins according to approved concurrency strategy;
- Search refresh failure → projection remains valid Location truth; integration failure is recorded and retry queued.

### Tests

Unit:

- fuzzing utility with deterministic seeded fixture;
- public payload excludes exact input;
- policy-not-configured failure.

Integration:

- upsert unique projection;
- concurrent refresh;
- invalidation;
- Search-refresh command mock.

Property/privacy:

- logs exclude exact input;
- unsupported target type fails closed.

E2E:

- public fixture renders approximate location only.

### Out of Scope

- exact reveal;
- Booking/Order reveal gate;
- production geocoder selection;
- final radius/stability/expiry policy;
- broad multi-source target support.

### Exit Gate

- one supported test target produces exactly one `FuzzyLocationCache` row;
- public API/UI returns only fuzzy payload;
- exact location is absent from response, search request, analytics, and logs;
- repeated same-version refresh is idempotent;
- unsupported/unconfigured target fails closed;
- Search refresh uses its public contract;
- unit/integration/E2E tests pass.

---

# Phase 2 — Core Privacy Fulfillment

## 04 Erasure Orchestration, Target Disposition, and Retention Proof

Build the durable privacy-erasure worker flow for requests that have already reached an authoritative `verified` state.

### Objective

Execute a verified erasure request across registered owner executors while preserving target-level outcome and retention proof.

### User-visible / Observable Result

For a verified test request, an authorized requester/admin can see:

- processing state;
- erasure job;
- target counts;
- completed/failed/retained target summaries;
- safe failure status;
- no false claim of final request completion where aggregate semantics remain unresolved.

### Owning Module(s)

- **Privacy / Data Erasure** owns request/job/target/exemption truth.
- Source Modules own actual record/provider mutations.

### Dependencies

- Features 01–02.
- seeded/test `PrivacyRequest.status=verified` or approved verification path if available.
- reliable jobs/idempotency.
- at least two owner executors.
- Audit and Observability.

### Shared Operations Used

- `SH-099 orchestratePrivacyFulfillment` — Privacy-owned workflow.
- `SH-096 enumerateSubjectData` — inventory.
- `SH-097 evaluateRetentionRequirement` — owner facts.
- `SH-095 executePrivacyInstruction` — owner mutation.
- `SH-098 anonymizePersonalFields` — owner-specific field map.
- `SH-049 orchestrateWorkflowSteps` / `SH-050 reconcileWorkflowStatus` — mechanism only.
- `SH-047 enqueueReliableJob` / `SH-048 executeRetryWithBackoff`.
- `SH-044 executeIdempotentCommand`.
- `SH-029 appendAuditEvent` / `SH-030 recordSensitiveAccess` where applicable.
- `SH-037 recordIntegrationFailure`.

No provider adapter is rebuilt in Privacy.

### Data / Schema

Use existing:

- `DataErasureJob`
- `DataErasureTarget`
- `DataRetentionExemption`
- related enums.

Target registration stores stable type/reference, external provider/ref where appropriate, status, result text, and timestamps.

Do not add a generic queue-status field to replace `DataErasureJob.status`.

### Public Interfaces

Internal:

```ts
startVerifiedErasure(...)
discoverAndRegisterTargets(...)
processErasureTarget(...)
retryErasureTarget(...)
reconcileErasureWork(...)
```

External dependencies use the Feature 02 executor protocol.

### Logic

1. Refuse to start unless `PrivacyRequest.type=erasure` and status is authoritative `verified`.
2. Create one idempotent `DataErasureJob`.
3. Enumerate owner data.
4. Register targets.
5. For each target:
   - ask owner for retention facts;
   - if required, create `DataRetentionExemption`;
   - execute permitted anonymization or retain result through owner;
   - otherwise dispatch owner erasure;
   - record typed result on target.
6. Retry only retryable technical failures.
7. Never retry permanent legal/manual-review outcomes indefinitely.
8. Preserve evidence that already-completed target action occurred.
9. Do not finalize ambiguous mixed-retention `PrivacyRequest` semantics before U-08-04 is resolved.

### UI / Administrative Surface

Requester:

- processing/target-count summary without internal system names or sensitive details.

Admin:

- job/target inspector;
- owner Module;
- safe reason codes;
- retryable/terminal distinction;
- retention exemption reason and `retainUntil` where authorized;
- retry action through canonical job mechanism.

### Authorization / Compliance

- requester sees own safe summary.
- admin detail is capability-gated.
- retention exemption requires owner-supplied facts.
- no administrator can choose arbitrary `legal_obligation` without an approved owner/legal basis.
- generic hold state does not replace target status.

### Events / Jobs / Integrations

Jobs:

- discovery;
- per-target execution;
- retry;
- aggregation/reconciliation.

Potential events only after root registration:

```text
privacy.erasure_job.queued
privacy.target.resolved
```

Provider deletion occurs behind owner adapters.

### Failure Behavior

- one target retryable failure → target remains visibly failed/retryable according to worker metadata and Privacy status policy; no silent completion;
- owner returns retained without basis → reject result and route manual review;
- provider absent → owner may return `not_found`/equivalent typed result; Privacy maps only according to approved contract;
- worker crash → QueueJob retries; `DataErasureJob` remains business truth;
- duplicate target command → replay prior idempotent result.

### Tests

Unit:

- target result mapping;
- exemption creation rules;
- retry classification;
- no direct provider execution.

Integration:

- two owner executors;
- one retained target;
- one erased target;
- retryable failure;
- duplicate worker delivery.

Concurrency:

- two workers cannot apply same target twice.

Compliance:

- retained target has exemption;
- audit does not substitute target;
- generic QueueJob does not close privacy job.

E2E:

- verified seeded request enters processing and visibly resolves target rows.

### Out of Scope

- how request becomes verified;
- correction/restriction;
- access request;
- final mixed-retention request aggregation;
- User hard deletion;
- backup policy;
- all production owner executors.

### Exit Gate

- verified erasure request creates durable job and target rows;
- at least two owner executors run without direct cross-Module DB mutation;
- retained target requires documented exemption;
- duplicate execution produces one owner effect;
- provider-specific clients are absent from Privacy;
- retry/dead-letter behavior is visible;
- unresolved final aggregation is surfaced, not guessed;
- required tests pass.

---

## 05 Privacy Export Bundle and Secure Delivery

Build the export path for requests explicitly typed `export`, using owner serializers and Media-owned private delivery mechanics.

Production export is gated until SH-100 createPrivacyExportArtifact is fully satisfied: manifest and per-owner sections, archive hash/encryption, protected MediaAccessGrant/access, expiry and cleanup, and sensitive-access audit. A bare `DataExportBundle.mediaAssetId` is not sufficient production proof. The Media handoff, integrity/persistence representation, algorithm, and key-management implementation remain unresolved; this requirement does not approve them.

### Objective

Produce a private, expiring `DataExportBundle` without turning Privacy into a storage provider or exposing permanent URLs.

### User-visible / Observable Result

For a verified export request:

- export status progresses `queued → generating → ready`;
- requester receives a short-lived authorized download action;
- expired bundle is unavailable;
- access is auditable.

### Owning Module(s)

- **Privacy / Data Erasure** owns export content policy and `DataExportBundle`.
- **Media / File Access** owns file/object mechanics and signed access.

### Dependencies

- Features 01–02.
- verified export request test fixture or approved verification path.
- Media private asset creation/finalization.
- signed Media access.
- approved shared encryption/hash implementation satisfying mandatory SH-100 createPrivacyExportArtifact protections; production remains gated until available.
- Audit.

### Shared Operations Used

- `SH-100 createPrivacyExportArtifact` — Privacy owns bundle; Media owns storage.
- `SH-096 enumerateSubjectData` — owner export sections.
- `SH-127 requestMediaAccess` — Media owner.
- `SH-072 hashCanonicalPayload` — mandatory artifact/manifest integrity for SH-100 createPrivacyExportArtifact.
- `SH-075 encryptSensitiveValue` or an approved shared archive encryption mechanism — mandatory archive protection for SH-100 createPrivacyExportArtifact; implementation remains decision-gated.
- `SH-030 recordSensitiveAccess` — issuance/download.
- `SH-047 enqueueReliableJob` — generation/expiry cleanup.
- `SH-055 runDeadlineExpiration` — bundle expiry.
- `SH-044 executeIdempotentCommand`.
- `SH-034 sanitizeTelemetryMetadata`.

### Data / Schema

Use:

- `DataExportBundle`
- `DataExportStatus`
- `mediaAssetId`
- `expiresAt`
- `generatedAt`
- `failureReason`

PR-08-04 proposes explicit Media referential integrity. Until approved:

- application service must verify referenced Media asset exists and is private;
- no orphan `mediaAssetId` may be created intentionally;
- do not invent a cross-owned Prisma relation if root schema review has not approved it.

### Public Interfaces

```ts
generateDataExportBundle(...)
getPrivacyExportStatus(...)
authorizePrivacyExportDownload(...)
expireDataExportBundle(...)
```

Actual file delivery calls Media's signed-access interface.

### Logic

- accept only `PrivacyRequest.type=export`;
- require authoritative verified state;
- call owner export serializers;
- omit secrets/credentials/nonexportable security material;
- assemble manifest using owner sections;
- store artifact privately through Media;
- set bundle ready only after Media finalization succeeds;
- access checks requester ownership, bundle ready state, and expiry;
- expiry marks bundle expired and requests Media cleanup;
- signed URL is short-lived and not persisted as entitlement truth.

### UI / Administrative Surface

Requester:

- export generation status;
- ready download button;
- expired state with policy-approved regeneration guidance.

Admin:

- generation failure/retry metadata;
- no default content preview.

### Authorization / Compliance

- requester ownership required;
- admin download of another user's export is not implied by admin role;
- sensitive access is audited;
- no entitlement gating;
- no browser-local export assembly.

### Events / Jobs / Integrations

Jobs:

- bundle generation;
- expiry cleanup.

Notification:

- `SH-041 requestNotification` may notify requester when ready/failed if approved template exists.

No direct R2 client in Privacy.

### Failure Behavior

- one owner serializer fails → bundle fails or waits according to approved export policy; do not silently omit owner data;
- Media upload failure → bundle `failed`;
- signed URL issuance failure → bundle remains ready; access attempt fails and is observable;
- expired bundle → deny even if stale URL UI remains;
- cleanup failure → bundle remains expired and Ops records retryable cleanup failure.

### Tests

Production acceptance tests must prove the full SH-100 createPrivacyExportArtifact protection chain; missing integrity, encryption, grant/access, cleanup, or audit protection cannot pass the production gate.

Unit:

- export section filtering;
- bundle lifecycle;
- expiry authorization.

Integration:

- Media artifact creation;
- signed access;
- cleanup request;
- audit.

Security:

- no permanent URL;
- no export content in logs;
- cross-user denial.

E2E:

- verified export request → ready → short-lived download → expired denial.

### Out of Scope

- `access` request semantics;
- legal deadline calculation;
- custom archive format beyond approved contract;
- automatic regeneration after expiry;
- direct object-storage implementation.

### Exit Gate

- production export satisfies the complete SH-100 createPrivacyExportArtifact protection chain; unresolved representation or Media handoff blocks the gate;
- ready bundle references a valid private Media asset;
- requester can obtain short-lived access and another User cannot;
- access is audited;
- expiry blocks further issuance;
- Media, not Privacy, owns storage/signed URL;
- failure does not produce a false ready state;
- all tests pass.

---

# Phase 3 — Decision-Gated Domain Completion

## 06 Complete Privacy Request Semantics

**Decision-Gated Feature. Do not start until the required CL-08 unresolved decisions are approved and architecture is updated.**

### Objective

Complete all declared privacy request types and final lifecycle behavior so a real request can move from submission through verified fulfillment to a legally supported terminal state.

### User-visible / Observable Result

Users can exercise:

- access;
- export;
- erasure;
- correction;
- restriction;

and receive accurate status, deadlines/communications where approved, and terminal outcomes.

Authorized admins can review/reject/cancel only under approved policy.

### Owning Module(s)

- **Privacy / Data Erasure**.
- Identity owns verification proof mechanics.
- Source Modules execute their own corrections/restrictions.

### Dependencies

Features 01, 02, 04, 05.

Must resolve at minimum:

- U-08-01 identity proof;
- U-08-02 access vs export;
- U-08-03 correction/restriction target proof;
- U-08-04 retained aggregation;
- U-08-05 cancel/reject;
- U-08-06 due date/jurisdiction;
- U-08-07 active request concurrency;
- U-08-08 User disposition as required for erasure completion;
- U-08-09 backup representation if completion wording depends on it.

### Shared Operations Used

- `SH-001 resolveAuthenticatedActor`
- `SH-002 authorizeResourceAction`
- `SH-014 requireStepUpForSensitiveAction` only if approved policy requires it
- `SH-099 orchestratePrivacyFulfillment`
- `SH-053 transitionLifecycleState`
- `SH-050 reconcileWorkflowStatus`
- `SH-096 enumerateSubjectData`
- `SH-097 evaluateRetentionRequirement`
- `SH-095 executePrivacyInstruction`
- `SH-041 requestNotification`
- `SH-029 appendAuditEvent`
- `SH-030 recordSensitiveAccess`
- `SH-044 executeIdempotentCommand`
- `SH-047 enqueueReliableJob`

No local substitutes.

### Data / Schema

Apply only migrations approved by the updated architecture, potentially including:

- durable identity-verification reference;
- request jurisdiction/policy version;
- deadline extension proof;
- target-level corrected/restricted result model;
- active-request concurrency constraints;
- completion metadata.

Do not choose exact columns until the ruling is approved.

### Public Interfaces

Complete:

```text
verifyPrivacyRequestIdentity
cancelPrivacyRequest
rejectPrivacyRequest
processDataAccessRequest
processDataCorrectionRequest
processDataRestrictionRequest
completePrivacyRequest
```

Any interface name changed by approved Module architecture supersedes this plan.

### Logic

Implement the approved transition graph exactly.

The service must:

- distinguish request types;
- validate verification proof;
- calculate deadlines only from approved policy/version;
- apply approved concurrency policy;
- aggregate retained/failed/skipped results according to approved semantics;
- never call one target's `erasedAt` equivalent sufficient proof of request completion;
- preserve proof that erasure occurred without preserving unnecessary personal data.

### UI / Administrative Surface

Requester:

- accurate request-specific steps;
- due date only if authoritative;
- correction/restriction result;
- safe explanation for rejection/cancellation when legally permitted.

Admin/legal review:

- authority-gated decision controls;
- policy version/basis;
- target/exemption summary;
- no unrestricted sensitive content.

### Authorization / Compliance

- Identity verification follows approved standard.
- Rejection/cancellation authority follows approved Role / Authority policy.
- Privacy rights cannot be gated by Track subscription.
- Holds apply only if approved legal policy explicitly says so.
- retention exemptions require owner evidence.

### Events / Jobs / Integrations

Complete approved privacy event contracts.

Notification templates must be versioned and privacy-safe.

### Failure Behavior

- insufficient identity proof → remain/revert according to approved state graph; do not process;
- missed deadline → surface operational/legal exception; do not falsify date;
- owner unsupported correction/restriction → explicit unresolved/failed target result according to approved model;
- conflicting active request → apply approved conflict result, not silent merge.

### Tests

- transition matrix;
- each request type;
- identity proof;
- deadline policy;
- cancellation/rejection authority;
- retained aggregation;
- correction/restriction proof;
- concurrent requests;
- E2E for each request type.

### Out of Scope

- changing source Module retention law;
- universal admin override;
- hard-delete strategy not approved;
- backup semantics not approved.

### Exit Gate

- all U-08 decisions required by this feature are recorded as approved architecture;
- every request type has target-level and aggregate proof;
- illegal transitions are rejected;
- deadlines are policy-versioned, not hardcoded ad hoc;
- cancellation/rejection paths are authorized and tested;
- all privacy E2E journeys pass;
- no unresolved privacy semantics remain hidden in code.

---

## 07 Exact Location Reveal and Viewer-Specific Lifecycle

**Decision-Gated Feature. Do not start until exact-location ownership and reveal policy are approved.**

### Objective

Implement `SH-027 resolveLocationReveal` as the single exact-location disclosure decision and `LocationReveal` as viewer/context reveal truth.

### User-visible / Observable Result

An authorized eligible participant can request exact location and receive it only after a fresh server-side decision. An unauthorized/ineligible actor receives no exact data. Reveal status is visible without exposing the value.

### Owning Module(s)

- **Location Safety** owns decision and reveal lifecycle.
- Booking/Order/source Module owns supporting facts and exact source location record.
- Role / Authority owns permission interpretation.
- Audit owns generic sensitive-access proof.

### Dependencies

Features 03 and root shared operations.

Resolve at minimum:

- U-08-10 exact source owner outside Booking as applicable;
- U-08-11 Booking duplicate location fields;
- U-08-12 Booking/Order context rule;
- U-08-13 reveal predicate;
- U-08-14 directionality;
- U-08-15 revocation triggers;
- U-08-16 audit fail-closed behavior;
- U-08-19 reveal uniqueness/current-state model;
- U-08-20 production crypto implementation where exact source is stored encrypted.

### Shared Operations Used

- `SH-027 resolveLocationReveal` — Location Safety owner.
- `SH-001 resolveAuthenticatedActor`.
- `SH-002 authorizeResourceAction`.
- `SH-026 authorizeContextualResourceAccess`.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)`.
- `SH-011 evaluateComplianceHold` only if approved predicate uses it.
- `SH-075 encryptSensitiveValue` for approved exact storage/decryption.
- `SH-076 normalizeAndHashIdentifier` for IP/request proof.
- `SH-044 executeIdempotentCommand`.
- `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency`.
- `SH-030 recordSensitiveAccess`.
- `SH-029 appendAuditEvent`.
- `SH-034 sanitizeTelemetryMetadata`.

No Booking/Order-specific reveal helper may duplicate policy.

### Data / Schema

Use `LocationReveal` and `LocationRevealStatus`.

Apply approved migrations for:

- Booking/Order referential integrity;
- context constraint;
- uniqueness/current-state model;
- timestamp consistency;
- source/policy/gate version if approved;
- Booking duplicate field reconciliation.

Do not invent schema before architecture approval.

### Public Interfaces

Complete:

```text
resolveLocationReveal(...) # SH-027 resolveLocationReveal
getLocationRevealStatus(...)
revokeLocationReveal(...)
listLocationRevealHistory(...)
```

If architecture separates decision from value issuance, expose distinct safe interfaces and keep the same owner.

### Logic

- fresh actor and authority check;
- fresh owner gate facts;
- exact reveal predicate evaluated only inside Location Safety;
- source exact value obtained through owner interface;
- decrypt only after allow decision;
- create/update viewer/context reveal proof atomically;
- sensitive-access audit according to approved transaction boundary;
- return exact data once only through protected response;
- never cache exact value in public/search projection.

### UI / Administrative Surface

Protected Booking/Order UI:

- hidden state;
- eligible "show exact location" action;
- revealed view;
- revoked/denied state;
- no exact value in page source before action when policy requires on-demand reveal.

Admin/compliance:

- reveal history metadata only unless separate authority permits data view.

### Authorization / Compliance

- actor must be authorized participant/admin according to policy;
- paid/provider state alone is insufficient;
- consent alone is insufficient;
- Track entitlement alone is insufficient;
- relevant ComplianceHold is evaluated only if approved.

### Events / Jobs / Integrations

Potential approved events:

```text
location.reveal.eligible
location.revealed
location.reveal.revoked
```

No external provider should receive exact location merely to render a public map.

### Failure Behavior

- stale/missing Booking/Order facts → deny;
- decrypt failure → do not reveal; record operational failure;
- audit failure → follow approved U-08-16 policy;
- concurrent revoke and reveal → lock/CAS ensures approved winner;
- duplicate reveal request → idempotent replay without duplicate domain effect;
- source location changed between decision and read → re-evaluate or reject according to approved version rule.

### Tests

- reveal predicate matrix;
- actor directionality;
- participant denial;
- hold/dispute/refund/cancel scenarios as approved;
- concurrency reveal vs revoke;
- timestamp/constraint tests;
- no exact value in logs/search/public payload;
- E2E authorized reveal and denied reveal.

### Out of Scope

- general map UI;
- directions/routing;
- service-area calculation;
- logistics;
- address collection UI ownership.

### Exit Gate

- every required reveal decision is approved in architecture;
- one authoritative `LocationReveal` state exists per approved context model;
- Booking/Order cannot reveal exact location without Location Safety;
- exact value is returned only after fresh server-side allow;
- deny/revoke paths never leak exact data;
- sensitive-access proof satisfies approved transaction policy;
- concurrency and E2E tests pass.

---

## 08 Location Revocation, Privacy Executor, and Gate-Change Reconciliation

Complete Location Safety's long-lived behavior after source state changes and make Location Safety a first-class Privacy executor.

### Objective

Ensure stale public projections and stale exact-reveal grants do not survive source, privacy, or business-gate changes.

### User-visible / Observable Result

- cancellation/refund/reschedule/source-location change causes the approved location reaction;
- revoked viewers can no longer retrieve exact location;
- privacy workflow can enumerate and disposition Location Safety records;
- public projection disappears or refreshes after privacy/source changes.

### Owning Module(s)

- **Location Safety** owns location reactions and its privacy executor.
- **Privacy / Data Erasure** owns privacy instruction/request truth.
- Booking/Order/source owners own triggering facts.

### Dependencies

Features 03 and 07.

Resolve U-08-21 and U-08-23 before production privacy disposition of location records.

### Shared Operations Used

- `SH-045 deduplicateDomainEvent`
- `SH-046 publishDomainEvent`
- `SH-047 enqueueReliableJob`
- `SH-048 executeRetryWithBackoff`
- `SH-027 resolveLocationReveal`
- `SH-028 applyFuzzyPublicLocation`
- `SH-091 requestSearchProjectionRefresh`
- `SH-096 enumerateSubjectData`
- `SH-097 evaluateRetentionRequirement`
- `SH-095 executePrivacyInstruction`
- `SH-030 recordSensitiveAccess`
- `SH-029 appendAuditEvent`

### Data / Schema

- `FuzzyLocationCache`
- `LocationReveal`
- approved explicit location privacy target types if PR-08-05 is accepted.

Potential retention fields are added only if approved architecture requires them.

### Public Interfaces

Location Privacy executor implements:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
```

Event handlers consume approved source events for:

- location changed;
- source hidden/deleted;
- Booking/Order gate changed;
- privacy instruction.

### Logic

- dedupe source events;
- load fresh owner facts;
- refresh/invalidate fuzzy cache;
- revoke reveals when approved predicate no longer passes;
- privacy erasure/anonymization only according to Location retention policy;
- do not erase safety proof that must be retained; record exemption through Privacy;
- do not preserve unnecessary exact/request metadata.

### UI / Administrative Surface

- Location reconciliation/admin diagnostic:
  - stale projection count;
  - pending revocation count;
  - privacy executor result;
  - retry/dead-letter state;
  - safe identifiers only.

### Authorization / Compliance

- event/system actor uses approved system authority.
- manual revocation requires explicit authority.
- privacy retention is not decided by arbitrary admin action.

### Events / Jobs / Integrations

Jobs:

- projection refresh;
- expiry scan;
- reveal re-evaluation;
- privacy execution.

Search refresh follows successful location truth change.

### Failure Behavior

- source owner unavailable → retry; do not assume reveal remains safe forever if approved policy requires fail-closed behavior;
- Search unavailable → record integration failure and retry projection request;
- privacy disposition conflicts with retention → return retained with owner facts to Privacy;
- duplicate source event → no duplicate reveal/projection side effect.

### Tests

- Booking/Order event dedupe;
- revocation on approved triggers;
- location change refresh;
- privacy enumeration;
- privacy erase/anonymize/retain;
- Search refresh failure;
- no cross-Module direct writes.

### Out of Scope

- changing Booking/Order source state;
- Search indexing implementation;
- PrivacyRequest completion policy;
- new map provider.

### Exit Gate

- approved gate-change events produce deterministic location outcomes;
- revoked reveal cannot be used afterward;
- Location Safety implements Privacy executor contract;
- explicit target types/retention policy are approved and tested for production;
- stale Search projection is retried through Search interface;
- no direct Booking/Order/Search/Privacy table mutation crosses ownership boundaries;
- tests pass.

---

# Phase 4 — Cross-Cluster Integration

## 09 Search, Media, Audit, Notification, and Ops Bridges

Prove CL-08 against the cross-cutting infrastructure owners it depends on.

### Objective

Replace mocks used in earlier features with real public interfaces for projection, file delivery/deletion, audit, notifications, and operations.

### User-visible / Observable Result

- fuzzy location changes appear/disappear in public Search correctly;
- privacy erasure removes Search projections through Search;
- export files are delivered/expired through Media;
- privacy/location sensitive accesses appear in the canonical audit surface;
- approved request-status notifications are delivered through Notification;
- failed jobs/integrations appear in Ops without changing domain truth.

### Owning Module(s)

- Privacy and Location own their business causes.
- Search, Media, Audit, Notification, and Ops own their mechanics/truth.

### Dependencies

Features 03–08 as applicable.
Neighbor Module public interfaces must be implementation-ready.

### Shared Operations Used

- `SH-091 requestSearchProjectionRefresh`
- `SH-127 requestMediaAccess`
- `SH-070 deleteProviderResource` through provider owners
- `SH-029 appendAuditEvent`
- `SH-030 recordSensitiveAccess`
- `SH-041 requestNotification`
- `SH-037 recordIntegrationFailure`
- `SH-032 createRequestContext`
- `SH-034 sanitizeTelemetryMetadata`
- `SH-047 enqueueReliableJob`
- `SH-044 executeIdempotentCommand`

### Data / Schema

No ownership transfer.

Validate:

- `SearchUpsertEvent` remains Search-owned;
- `MediaAsset`/`MediaAccessGrant` remain Media-owned;
- `AuditEvent`/`AccessAuditLog` remain Audit-owned;
- `Notification`/`NotificationDelivery` remain Notification-owned;
- `IntegrationFailure`/`QueueJob` remain Ops-owned.

Apply PR-08-04 relation only if approved.

### Public Interfaces

Integrate real implementations for:

```text
requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
requestMediaAccess # SH-127 requestMediaAccess
Media privacy executor
appendAuditEvent # SH-029 appendAuditEvent
recordSensitiveAccess # SH-030 recordSensitiveAccess
requestNotification # SH-041 requestNotification
recordIntegrationFailure # SH-037 recordIntegrationFailure
```

### Logic

- propagate correlation/causation IDs;
- owner transaction commits before downstream projection/notification dispatch;
- dedupe downstream event handling;
- retry transient failures;
- do not roll back Privacy/Location truth merely because a nonauthoritative notification fails;
- SH-091 requestSearchProjectionRefresh acceptance is pending progress, not deletion completion; a Privacy target requiring Search removal remains non-successful until Search supplies completion evidence under the approved executor contract;
- Location may complete its own cache/projection-source mutation independently; durable Search completion-receipt representation remains unresolved.

### UI / Administrative Surface

- Ops diagnostic links from privacy job/location projection to correlation ID;
- audit viewer safe references;
- notification delivery status where root admin UI exposes it.

### Authorization / Compliance

- audit/ops admin access is separately authorized;
- export signed access still requires Privacy authorization;
- Search gets only safe location payload;
- notifications do not contain sensitive export or exact-location data.

### Events / Jobs / Integrations

Real outbox/inbox/queue integration.

Provider operations remain behind owner adapters.

### Failure Behavior

- Search failure → CL-08 truth stays committed, projection marked pending through Search/Ops retry;
- Notification failure → request truth unchanged;
- Audit critical failure → follow root audit policy; exact reveal follows approved U-08-16;
- Media deletion failure → privacy target cannot be falsely marked erased;
- Ops failure record is supplemental.

### Tests

Contract/integration:

- Search refresh;
- Media signed URL/delete;
- Audit append;
- Notification request;
- IntegrationFailure.

E2E:

- privacy erasure removes public search result;
- fuzzy projection update reaches search;
- export download audit exists.

### Out of Scope

- implementing neighbor Module lifecycle internals;
- direct provider SDKs;
- redesigning Search/Media/Audit/Notification.

### Exit Gate

- all five bridges use owner public interfaces;
- Search receives no exact location;
- Media failure prevents false privacy erasure;
- audit records are separate from CL-08 domain rows;
- notification failure does not corrupt domain status;
- correlation IDs link domain work to ops evidence;
- integration/E2E tests pass.

---

## 10 Full Data-Owner Executor Coverage and Booking/Order Location Contracts

Prove the Cluster's meaningful inbound/outbound contracts across neighboring business Clusters without importing their source truth.

### Objective

Reach production-ready contract coverage for the owner Modules explicitly represented in the current privacy target vocabulary and for the Booking/Order/source-location facts required by Location Safety.

### User-visible / Observable Result

An authorized admin can run a privacy coverage diagnostic showing every required executor as:

```text
implemented
unsupported by policy
decision-gated
or failed
```

Location diagnostic shows Booking/Order contracts and supported public-location target types without direct database coupling.

### Owning Module(s)

- Privacy owns executor coverage requirements.
- Location Safety owns location fact requirements.
- Each neighbor Module owns its contract implementation.

### Dependencies

Features 02, 04–09.
Relevant neighbor Module architectures/implementation plans.

### Shared Operations Used

- `SH-096 enumerateSubjectData`
- `SH-097 evaluateRetentionRequirement`
- `SH-095 executePrivacyInstruction`
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)`
- `SH-123 validateOwnedTargetReference`
- `SH-025 authorizeOrderEntitlement` where delivery/order entitlement facts are required by an owner, not as privacy truth
- `SH-027 resolveLocationReveal`
- `SH-028 applyFuzzyPublicLocation`
- `SH-091 requestSearchProjectionRefresh`
- provider deletion contract through owner Modules.

### Data / Schema

Cover current `DataErasureTargetType` owners:

- Identity;
- Customer;
- Track;
- Messaging;
- Notification;
- Media;
- Search;
- Video;
- Payment;
- Booking/Calendar;
- Digital Goods;
- Transaction/Agreement.

Include Location Safety target types once approved.

Do not introduce a universal polymorphic FK table.

### Public Interfaces

Prove:

- every current target type maps to one explicit executor owner;
- `other` requires explicit owner and cannot run generic deletion;
- Booking exposes minimal location/gate facts;
- Order exposes minimal participant/transaction gate facts;
- source Modules expose source-location version/reference for fuzzy projection where supported.

### Logic

- executor registry completeness check at startup/test time;
- unsupported target type causes explicit diagnostic failure;
- privacy inventory is bounded/cursorable;
- cross-Module owner DTOs are minimal;
- Location does not infer Booking/Order lifecycle from raw fields outside their interfaces;
- source owners do not calculate fuzzy coordinates themselves.

### UI / Administrative Surface

Internal CL-08 coverage dashboard:

- target type;
- executor owner;
- protocol version;
- test status;
- provider dependency;
- retention policy status;
- location target support;
- blocker ID.

No raw subject data.

### Authorization / Compliance

- coverage diagnostics are admin/developer-only;
- executor calls still enforce owner context and subject identity;
- no support/admin universal data read.

### Events / Jobs / Integrations

Cross-cluster contract test suite runs in CI.

Backfill/reconciliation jobs may be introduced for already-existing records only if needed and approved.

### Failure Behavior

- missing executor → release gate failure;
- protocol version mismatch → fail closed;
- stale owner facts → retry/reload;
- unsupported provider deletion → target cannot be marked erased;
- missing location source contract → public location remains unavailable rather than guessed.

### Tests

Contract tests for every mapped executor owner.

Booking/Order:

- participant facts;
- state facts;
- no direct Prisma access from Location.

Privacy:

- target coverage matrix;
- retained owner examples;
- provider-deletion result translation.

E2E:

- representative cross-cluster erasure journey spanning Identity/Customer/Media/Search/Messaging or equivalent approved set;
- representative Booking/Order location decision journey.

### Out of Scope

- new target families not evidenced in current registry/schema;
- migrating neighbor lifecycles;
- generic privacy crawler;
- unsupported location-bearing records without source-owner architecture.

### Exit Gate

- every current target type has an explicit owner mapping and contract status;
- required production executors have passing contract tests or are explicitly decision-gated;
- Booking/Order facts are consumed through public interfaces;
- no cross-cluster direct database ownership theft exists;
- Search/Media/provider deletion remains owner-controlled;
- coverage dashboard/CI check makes missing executor impossible to hide.

---

# Phase 5 — Hardening and Production Readiness

## 11 Security, Reconciliation, Privacy, and Production Hardening

Harden CL-08 for production only after the relevant decision-gated features and cross-cluster contracts pass.

### Objective

Prove that CL-08 remains correct under retries, concurrency, provider degradation, stale projections, destructive privacy operations, and security-sensitive exact-location access.

### User-visible / Observable Result

- privacy workflows recover from transient failures without duplicate destruction;
- stuck work is visible;
- stale search/location projections are reconciled;
- expired export access is denied;
- exact-location access follows approved security/audit requirements;
- operators have safe diagnostic and manual-review paths;
- production launch checklist explicitly records any legal-gated features still disabled.

### Owning Module(s)

- Privacy / Data Erasure for privacy hardening.
- Location Safety for location hardening.
- shared owners for infrastructure.

### Dependencies

Features 01–10.
All production-bound unresolved decisions must be approved or the affected path remains disabled behind an approved feature/config gate.

### Shared Operations Used

All CL-08-relevant canonical operations, especially:

- `SH-044 executeIdempotentCommand`
- `SH-045 deduplicateDomainEvent`
- `SH-047 enqueueReliableJob`
- `SH-048 executeRetryWithBackoff`
- `SH-050 reconcileWorkflowStatus`
- `SH-062 reconcileProviderState` through provider owners
- `SH-093 reconcileSearchProjection`
- `SH-055 runDeadlineExpiration`
- `SH-051 acquireAggregateLock`
- `SH-052 withOptimisticConcurrency`
- `SH-037 recordIntegrationFailure`
- `SH-039 checkServiceHealth`
- `SH-040 correlateOpsIncident`
- `SH-034 sanitizeTelemetryMetadata`
- `SH-029 appendAuditEvent`
- `SH-030 recordSensitiveAccess`.

### Data / Schema

Review and, only with approved architecture, add:

- constraints for reveal context/uniqueness/timestamps;
- approved target-type additions;
- approved privacy proof fields;
- explicit DataExportBundle media relation;
- indexes required by worker scans;
- policy/source version columns where approved.

Destructive migrations require staged deployment/backfill and rollback plan.

### Logic

#### Privacy hardening

- stalled request/job/target reconciliation;
- retry caps/dead-letter;
- export cleanup reconciliation;
- target result replay;
- owner executor version compatibility;
- retention exemption completeness checks;
- orphan export detection;
- no false completion on partial provider deletion;
- backup-policy wording and operational proof as approved.

#### Location hardening

- fuzzy projection reconciliation against owner source version;
- stale/orphan projection removal;
- reveal/revoke race tests;
- source location changed during request;
- revoked reveal denial;
- key rotation compatibility;
- geocoder degradation;
- public payload privacy invariant monitoring.

### UI / Administrative Surface

Production admin tools:

- stalled privacy work;
- failed target retries;
- export cleanup failures;
- stale fuzzy projections;
- reveal reconciliation failures;
- incident correlation;
- manual-review queue;
- decision-gated feature status.

Tools must minimize sensitive payloads.

### Authorization / Compliance

Perform explicit review of:

- self-service vs admin privacy access;
- exact-location access;
- audit-log access;
- export file access;
- retained legal records;
- service-role worker scope;
- provider secrets;
- key management;
- rate limiting;
- data minimization;
- telemetry redaction;
- irreversible destructive commands.

### Events / Jobs / Integrations

Reconciliation:

- Search projection reconciliation remains Search-owned.
- provider reconciliation remains provider-owner-owned.
- CL-08 reconciles its own business truth against typed owner results.

Scheduled work:

- export expiry;
- stalled privacy checks;
- fuzzy expiry/refresh;
- reveal re-evaluation where approved.

### Failure Behavior

- provider unavailable → retry/circuit-break; no false terminal success;
- repeated terminal failure → dead-letter/manual review + domain failure state where appropriate;
- audit/ops unavailable → follow approved criticality policy;
- key unavailable → deny exact reveal, never return plaintext fallback;
- search unavailable → keep exact data private and queue projection repair;
- migration/backfill anomaly → stop destructive phase and preserve source data.

### Tests

Security:

- authorization/RLS where applicable;
- exact-location exfiltration attempts;
- signed URL leakage;
- telemetry redaction;
- secret handling;
- rate limits;
- replay attacks.

Concurrency/idempotency:

- duplicate web requests;
- duplicate events;
- duplicate job deliveries;
- provider callback/reconciliation overlap;
- reveal vs revoke;
- privacy target retry.

Privacy/compliance:

- retention proof;
- export expiry;
- no hidden target failure;
- location privacy executor;
- Search de-index;
- audit completeness.

Performance:

- large subject inventory pagination;
- large target-job batching;
- projection refresh batching;
- admin diagnostics bounded.

E2E:

- full approved erasure journey;
- export journey;
- correction/restriction/access journeys if enabled;
- fuzzy location public journey;
- exact reveal + revocation journey if enabled.

### Out of Scope

- new privacy laws not represented in approved policy;
- new geolocation product features;
- new provider families;
- refactoring neighboring Modules for style;
- removing unresolved feature gates without approval.

### Exit Gate

Feature 11 and CL-08 production readiness pass only when:

- all enabled privacy request types have approved lifecycle/policy and passing E2E tests;
- no enabled path depends on an unresolved U-08 decision;
- all destructive privacy work is idempotent and observable;
- every retained target has approved exemption proof;
- production exports satisfy the complete SH-100 createPrivacyExportArtifact protection chain, including manifest, per-owner sections, archive hash/encryption, MediaAccessGrant/access, expiry/cleanup, and sensitive-access audit;
- public search cannot expose exact location;
- exact reveal is fail-safe under stale state, concurrency, and crypto/provider failure;
- Search/Media/Audit/Ops/provider reconciliations preserve ownership;
- required backfills/migrations have rollback and verification;
- typecheck, lint, unit, integration, contract, concurrency, security, privacy, and critical Playwright tests pass;
- progress tracker records enabled/disabled legal-gated capabilities and remaining risks.

---

## Phase Summary

| Phase | Name | Features |
|---|---|---|
| Phase 1 | Safe Cluster Foundations | 01 Privacy Request Intake and Status Surface; 02 Privacy Executor Protocol and Subject-Data Inventory; 03 Fuzzy Public Location Projection |
| Phase 2 | Core Privacy Fulfillment | 04 Erasure Orchestration, Target Disposition, and Retention Proof; 05 Privacy Export Bundle and Secure Delivery |
| Phase 3 | Decision-Gated Domain Completion | 06 Complete Privacy Request Semantics; 07 Exact Location Reveal and Viewer-Specific Lifecycle; 08 Location Revocation, Privacy Executor, and Gate-Change Reconciliation |
| Phase 4 | Cross-Cluster Integration | 09 Search, Media, Audit, Notification, and Ops Bridges; 10 Full Data-Owner Executor Coverage and Booking/Order Location Contracts |
| Phase 5 | Hardening and Production Readiness | 11 Security, Reconciliation, Privacy, and Production Hardening |

**Total numbered features: 11**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required root, Cluster, Module, and dependency context.
2. Confirm the previous feature exit gate passed.
3. Check the feature's unresolved-decision dependencies.
4. If a required decision is unresolved, stop and record the blocker rather than inventing it.
5. Write the concise feature implementation specification.
6. Confirm schemas, public contracts, permissions, shared operations, provider boundaries, and tests.
7. Implement only the numbered feature.
8. Run typecheck, lint, tests, migrations/build checks as applicable.
9. Perform the feature's manual/workflow verification.
10. Review cross-Module ownership and anti-duplication boundaries.
11. Update the progress tracker.
12. Update architecture first if a binding architectural decision legitimately changed.
13. Record risks and deferred work.
14. Start the next feature only after the exit gate passes.

---

## Required Feature Specification

Immediately before implementation, each numbered feature must receive a concise implementation specification containing:

- Objective
- Observable result
- Dependencies
- Required approved decision gates
- In scope
- Out of scope
- Owning Module
- Data records affected
- Schema/migration impact
- Public interfaces
- Shared operations consumed
- Permissions
- Compliance/retention/privacy rules
- Primary workflow
- UI/admin states if applicable
- Provider integrations
- Jobs/events
- Idempotency/concurrency
- Error/failure behavior
- Tests
- Acceptance criteria
- Documentation updates
- Exit gate

Do not pre-write a giant implementation specification for every later feature. The build plan defines sequence and constraints; the next feature specification defines the concrete implementation slices.

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
- Provider adapters used
- Tests added/changed
- Commands run
- Manual/workflow verification
- Authorization/compliance verification
- Documentation updated
- Assumptions
- Approved decisions consumed
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result

A feature is not complete when its code merely compiles. The exit gate must pass, ownership boundaries must remain intact, and any required architectural decision must already be approved.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Privacy persists an immutable target descriptor with request identity, owner Module ID, registered owner target kind, opaque source ID/version, permitted action and descriptor/executor schema version. Each owner validates its own reference and field map. Typed child targets may be enumerated separately or included in an explicit versioned parent executor contract listing all covered child kinds; arbitrary `other`, a crawler or assumed cascade never supplies coverage. Deduplicate by request+owner+target-kind+source-id+action+source-version; preserve a new generation when re-evaluation changes an instruction. This is Privacy dispatch metadata, not polymorphic Media ownership.

Persist per-target attempts and final owner receipts independently of queue telemetry. A receipt names target/instruction identity, source version observed, action/outcome, executor version, completion time, evidence reference and any owner retention basis. Correction/restriction are explicit outcomes, never mislabeled deletion. Search acceptance is pending until Search returns its actual required projection outcome; Media artifact readiness similarly requires actual finalize/readiness proof. Retention is complete only when Privacy accepts an evidence-backed lawful exemption, not merely because an owner requested one.

Aggregate completion means every required target has either verified execution or an accepted lawful disposition. Summaries/exports disclose retained or restricted categories and reasons safely; `completed` never means all data was erased. Outstanding/failed targets prevent completed. A lawful fully accounted exemption does not by itself mean technical partial failure. An incomplete export stays pending/retryable or failed; no silent serializer omission or ready download. Any future deliberate partial-export product must explicitly distinguish partial from complete. This chooses correctness over premature delivery.

One request may have multiple execution/artifact generations for retries or refreshes; generations are immutable, correlated and only the current authorized ready artifact is offered. Revoke superseded access. Per-subject conflicting mutations serialize and re-evaluate owner state; do not reject or erase a legal request merely because another exists. Statutory verification, deadlines, restriction entitlement, backup completion wording, retention schedules and final User disposition remain EXTERNAL_REQUIREMENT. Identity markers are projections of Privacy outcomes, not a second rights lifecycle. Exact target enums/schema fields are deferred implementation constrained by this protocol.

Acceptance: restart routing, duplicate targets, changed source version, missing child coverage, failed serializer, lawful exemption versus unproven retention, Search queue acknowledgment versus completion, stale bundle access and concurrent conflicting instructions. No blanket claim of complete privacy coverage is authorized until all owner target/field matrices are reviewed.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.

## WA-R033 — Taxonomy semantics, history and AI proposal boundaries

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Taxonomy owns canonical term meaning and validation; contextual owners own accepted assignment joins. Join `verified` means an explicitly recorded authorized classification review, never Trust/KYC/Healthcare verification. Mere accepted attachment is not reviewed verification. Do not infer reviewed=true for legacy rows with unknown provenance; preserve them as unknown/unreviewed pending owner correction. Store reviewer/action/evidence/version when review is asserted. AI confidence is nullable integer basis points 0..10000 on the proposal, with model/prompt/output-schema/version provenance; it is model confidence, not calibrated correctness or authority. User/admin-authored assignments have no fabricated confidence. Accepted joins may retain a proposal reference and immutable provenance snapshot, but confidence never becomes a permission gate or competing current score. Legacy Float values are not auto-rescaled without proving their source scale. Candidate-authored tags use TagSource.user with CandidateProfile/User attribution; no new candidate source enum is required.

Adopt no normal hard-delete command for Domain/Category/Tag. Effective activity includes every ancestor's activity; ancestor reactivation does not rewrite child records. New assignments require effective-active terms. Historical accepted assignments retain term/version evidence even if the term later becomes inactive. Existing boolean active/inactive is sufficient for that lifecycle. A Tag must match the target's declared accepted Category at launch; multi-category assignment requires an explicit versioned compatibility policy, not arbitrary cross-category attachment. Parent IDs are immutable through ordinary edits. Exceptional reparent/merge runs require preflight affected-owner enumeration, compatibility review and controlled migration, never foreign join writes.

Persist immutable Taxonomy revisions/change records for labels, hierarchy, activity and represented compliance-trigger facts. Use stable term IDs and monotonically advancing owner revisions; updatedAt plus generic Audit is insufficient for historical interpretation. An alias points to exactly one stable canonical term within the same domain/type/locale normalization scope; alias cycles and conflicting normalized keys reject. Merge creates a durable from/to/version decision and alias/retirement mapping, preserves the source record, and requests each contextual owner to revalidate/repoint its own references with expected versions. Preserve original term/version in historical decision snapshots. Do not declare merge complete until required owner acknowledgments reconcile. No generic cross-owner migration service owns assignments.

Normalize term comparison keys using an explicitly versioned Unicode NFKC plus full case-fold and trimmed/collapsed Unicode whitespace; preserve punctuation and diacritics rather than conflating legally distinct terms. Include normalized locale and parent/type scope. Labels remain original display text. Alias registration is explicit, not automatic semantic synonym generation. Detect collision before creating or upgrading a normalization version; an algorithm change requires a dry-run collision report and owner migration. Slugs are owner-scoped stable public identifiers: use the shared primitive, uniqueness constraints and deterministic collision suffix; label edit does not silently rename an existing slug. Historical redirects/aliases are explicit owner records. Exact approved production seed content is an external reference-data requirement; no invented vocabulary is approved by this mechanism.

Additional license/background/location/Healthcare triggers use a versioned mapping owned by the interpreting requirement owner (Trust, Healthcare, Location or Job Compliance), keyed to Taxonomy term/revision and supported action/jurisdiction. Taxonomy supplies represented facts and change references, not clearance. Absent unsupported mappings do not imply readiness. DataSensitivity vocabulary follows Ubiquitous Language/compliance authority; source owners classify their own data and Healthcare separately owns explicit Healthcare boundaries. No generic scanner/AI inference can clear a sensitivity label.

Adopt the AI owner's two-record design: AiClassificationLog for a run and AiSuggestion for proposals, with append-only transition evidence. Run identity binds target owner/type/id/source version, allowed purpose, requester, model/prompt/normalization/output-schema versions and a semantic command identity. Keep queued→running→completed/failed/cancelled; queued may cancel. Cooperative cancellation prevents any late response from applying, even if provider work cannot be stopped; record late attempt outcome separately. Terminal runs never reopen; rerun is a new explicitly authorized run. Suggestions have unique run+candidateKey, exactly one value shape, and proposed→accepted/rejected/superseded/invalidated. Accepted requires a durable contextual-owner mutation receipt, never provider confidence or reviewer intent alone. Accepted/rejected dispositions are immutable; later assignment changes belong to the contextual owner.

Initial AI targets are ProfessionalProfile, Offering, Organization, Job and CandidateProfile; purposes are taxonomy_suggestion and skill_extraction. Gig AI is deferred because no bilateral target contract is established; ordinary Gig taxonomy assignment still works. Existing active canonical IDs only for taxonomy suggestions. Novel terms remain review-only and cannot be created by accepting an AI suggestion; independent authorized Taxonomy creation follows ordinary validation. Store logical term ID plus immutable term revision/label/path snapshot validated by Taxonomy; no cascading FK from proposal deletion into accepted truth. Keep normalized suggestions, validation result, canonical output hash and minimal provenance, not full raw provider bodies or source text. Provider/legal retention remains external; deleting AI evidence never deletes accepted assignments.

Use immutable code/config prompt versions with hashes at launch; no new database prompt publisher or first-class AiBackfill business model without a real additional lifecycle requirement. Bounded per-target runs and shared queue checkpoints suffice. Source adapters return purpose-limited normalized approved fields; Candidate supplies normalized skills/experience categories, never raw resume/application text at launch. Healthcare-sensitive transmission is disabled until source/Healthcare purpose-specific authorization and qualified provider/BAA evidence exist. No fallback model, region or logging change may silently widen the approved data boundary. Bedrock model/account/region/logging/retention configuration is external activation evidence, not selected by this architecture ruling.

Contextual owner commits accepted assignment and an immutable acceptance receipt/outbox fact atomically after fresh Taxonomy and source-version checks. AI consumes the receipt idempotently to record disposition; a timeout queries the contextual owner receipt rather than repeats the mutation with a new key. This is recoverable choreography over owner truth, not a generic CL-02 saga. Taxonomy admin composition may display proposal evidence and route assignment decisions through the actual context owner; shared review leases use WA-R031 and do not confer approval. No baseline AI→Search proposal feed or end-user classification notification. Broad backfill/configuration/merge and sensitive evidence exports require registered Role actions and fresh step-up under WA-R023/031; low confidence never creates a Hold by itself.

Required implementation checks: confidence source/range, unaudited verified claim, ancestor inactivity, normalization collision, alias cycle, stale assignment/term version, merge owner failure, late cancelled response, disposition-before-mutation rejection, duplicate acceptance receipt and raw/sensitive provider input rejection. Physical migrations, per-target DTO field allowlists, approved seeds, legal retention and provider capability are still separately qualified before activation.

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

## WA-R036 — Healthcare boundary history and effective evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Healthcare boundary and access policy records require append-only revisions, effective intervals, actor/reason/source proof and expected version. Retirement is an explicit authorized classification correction, never hard deletion. Resource owners supply typed parent ancestry; inherit the most restrictive applicable active boundary/policy over the validated ancestry. Explicit child policy may strengthen but never weaken an active ancestor. Clearing a mistaken boundary requires authorized Healthcare review and evidence, reevaluation of descendants and acknowledgments of affected projections. It does not erase historical classifications or authorize provider deletion. Existing-boundary schema must evolve before these mutations activate.

Role denial returns denied and terminates before Healthcare payload treatment. After Role allows, Healthcare returns allowed, redacted or blocked; blocked means authorized action but no payload disclosure under Healthcare policy. Failure or unknown ancestry/policy is blocked/unavailable, never allow. Policies use versioned resource-specific field-path masks: allowed field set, removed paths, masked paths with approved transform identifiers, policyRevision and boundary references. Source owners apply masks before serialization, attachments, exports and notifications; unknown field/path/version fails closed. No raw sensitive payload is sent to an admin client for client-side masking. Admin policy changes, boundary retirement, evidence export and BAA manual verification require fresh scoped step-up plus registered authority.

Maintain an explicit effective BAA reference per Healthcare profile and covered scope. A candidate replacement does not displace a still valid effective BAA before verified activation. Activation compares expected current reference, parties/scope/document version, required signatures, effective dates and validity. Overlapping inconsistent scopes require review; never latest-row-wins. BAA graph: draft→sent→signed→verified; draft/sent/signed→rejected with immutable reason/evidence; sent/signed/verified→revoked when authorized; applicable elapsed agreements→expired. Rejected/revoked/expired are terminal for that agreement; reissue creates a new linked agreement. Corrections cannot rewrite signed evidence. Healthcare profile summaries are derived from effective evidence plus profile-level restriction: not_applicable→pending_baa on accepted applicability; pending_baa→baa_sent→baa_signed from effective workflow; baa_signed→verified only after all Healthcare checks; applicable states→rejected/suspended under authorized decision. Rejected/suspended may return to the currently justified pending_baa/baa_sent/baa_signed/verified state only through authorized remediation and full current evaluation; no self-service restore. Missing/expired/revoked BAA never leaves verified readiness active.

lockedHealthcareFlag is a derived UI/edit restriction indicator only; source policy and revision must be queried for authority. It does not replace a boundary, BAA, Hold or readiness. BAA proof contains agreement/scope, party legal identifiers and represented authority, document version and canonical bytes hash, signer/countersigner identities/roles, signature intent and timestamp, provider envelope/reference and verified evidence provenance. Required legal parties, signature sufficiency, text, effective terms and retention are EXTERNAL_REQUIREMENT before live Healthcare contracting. Technical storage of those fields is not legal approval. documentMediaId becomes an explicit Healthcare-owned evidence attachment relation to MediaAsset with immutable evidence version/hash; Media lifecycle cannot overwrite executed bytes. No public/eager signed URL in BAA DTOs.

Healthcare-owned provider event effects follow WA-R018 with unique provider/account/event/handler version, payload fingerprint, agreement target, received time, processing status, attempt history, verified normalized outcome, effect receipt and reconcile status. Event arrival is not BAA execution. Unknown provider states stay unresolved. Provider-specific e-sign selection/capability, storage and video BAA coverage must come from actual qualified provider/account/region/configuration evidence through the corresponding provider owner; Healthcare evaluates it. No provider brand implies coverage. Required tests include ancestor restriction precedence, unknown mask denial, replacement race, late signed callback after revocation, and summary rebuild; provider/legal qualification remains separate.

## WA-R056 — Privacy verification and request execution history

Implement the corresponding owner architecture contract before consumers. First align the forward schema/constraints and immutable evidence representation under the database integration owner; then implement owner commands/queries and shared execution adapters; then qualify consumer fixtures. Historical decision gates covered by this ruling are resolved at architecture level only.

Privacy alone owns request transition decisions. Identity supplies immutable verification evidence bound to request subject, requested action/purpose, assurance, method, issuer, verifiedAt, expiry and logical attempt. Privacy verifies applicability against its approved policy revision before submitted→verifying_identity→verified. Failed verification may remain verifying for a permitted new attempt or receive authorized rejection; no guessed legal deadline or attempt limit. Verified→processing dispatches only an immutable execution generation with target inventory and policy/source versions under WA-R020.

Access and export share owner-provided subject-data inventory but differ in output: access is a scoped authorized rights response; export creates a portable private artifact. Neither authorizes another participant's data. Correction/restriction executors acknowledge accepted work separately from completed effect; only verified owner receipts advance completion. Serialize conflicting subject mutations and re-evaluate current policy/source state before each effect. Identity privacy flags project Privacy's outcome; they cannot drive request completion. Search removal requires its qualifying target/generation receipt, not queue acknowledgment.

Cancellation is an authorized request decision for eligible nonterminal work: record actor/reason/version, prevent new dispatch, reconcile in-flight effects and preserve all completed receipts. It never reverses erasure or manufactures rollback. Late receipts remain attached to the cancelled generation and are disclosed in its accounted outcome. Rejection records controlled policy reason, authority, source evidence and applied policy revision, not free-text notes alone. Reopening starts a linked new execution generation after fresh verification/eligibility as required; prior terminal history and effects remain immutable. Notes are minimized append-only annotations with author/time, separate from decision proof. No terminal row overwrite or automatic reexecution of prior completed effects.

Privacy completion follows WA-R020: all targets must have confirmed effect or valid accepted exemption; pending/failed targets cannot be hidden by aggregate completed. A lawful accounted exemption is not automatically technical partial failure. Export readiness requires complete contribution inventory. Exact statutory verification sufficiency, rejection grounds, deadlines, retention periods, backup treatment and final identity disposition remain EXTERNAL_REQUIREMENT, supplied as approved jurisdiction/version policy before the affected path activates. Hold existence alone is not a statutory exemption. Verify stale verification proof, concurrent requests, cancellation during effect, late receipt, reopen after erasure and incomplete export before enabling execution.

Record actual fixture, replay, concurrency and access evidence before interface freeze. Legal/provider activation gates remain scoped; no runtime completion is claimed by this plan.

## WA-R057 — Privacy owner inventory and private export handoff

Implement the corresponding owner architecture contract before consumers. First align the forward schema/constraints and immutable evidence representation under the database integration owner; then implement owner commands/queries and shared execution adapters; then qualify consumer fixtures. Historical decision gates covered by this ruling are resolved at architecture level only.

Each owner implements WA-R020 versioned enumerateSubjectData/evaluateRetentionRequirement/executePrivacyInstruction descriptors. Inventory is explicit, paginated with completion evidence and stable target/version identity; no generic other target or assumed database cascade can count as coverage. Messaging covers Thread, participant current state/history, Message/revisions/restrictions and MessageMedia joins. Notification covers Notification/interaction evidence, NotificationSubscription/credential generations, Delivery attempts and SubscriptionEvent. Location covers FuzzyLocationCache, reveal/revocation evidence and its provider references; exact source facts remain inventoried by their source owner. Restricted proof is accounted even when excluded from requester disclosure. Owner field/action matrices must identify erase, minimize, retain, export or restrict disposition with policy basis and executor receipts before destructive activation.

Privacy owns an immutable export manifest: subject/request/job/generation, owner contribution IDs and versions, authorized field scope, safely stated exclusions with disposition evidence, assembly completion, byte hash/algorithm, creation time and actor/correlation. Exact Location subject data may be included only under approved access policy after removing other parties' data; encryption keys, provider credentials and access tokens are never export content. Record opaque key-version/storage evidence where required, never keys. A complete manifest describes actual serialized bytes, not promised future contributions.

Use Media's WA-R050 createMediaUploadSession→bounded upload→completeMediaUpload→getMediaUploadStatus/getMediaReadiness protocol, with Privacy job/bundle revision as semantic key and purpose-bound private artifact authorization. Same key and bytes replay; changed bytes require a new revision or conflict. Upload acknowledgment never means ready. Require exact immutable ready Media version, matching hash/size and completed manifest before bundle ready. Bind through an explicit Privacy-owned MediaAsset/version reference, not polymorphic ownership. Failed scan/partial assembly keeps download unavailable. Terminal upload retry uses a linked Media attempt per WA-R050 while preserving bundle-generation lineage.

At download, Privacy rechecks requester/action/scope and current generation; Media rechecks asset safety/revocation and issues bounded access through SH-127. Commit required access evidence before protected disclosure. Superseded/expired/revoked generations cannot receive fresh access even if cleanup worker is late. Retain prior manifest/status evidence under approved retention while deleting bytes through Media's executor when authorized. No stored public URL, direct storage SDK or convenience export endpoint may bypass owner gates. Audit exports use the same Media mechanism but an Audit-owned manifest; this ruling does not transfer Audit export ownership.

Legal retention/exemption duration, backup-expiry representation and final retained shell require approved external policy. Location's geocoder/account/region/purpose and key lifecycle qualification remain external activation gates; consumers cannot choose their own geocoder or crypto. Verify omitted child inventory, partial serializer, hash mismatch, scan failure, changed-byte retry, stale generation access, retained shared Media references and provider-deletion uncertainty. Concrete schema, executor field matrices and bilateral fixtures remain implementation qualification, not unresolved architecture permission.

Record actual fixture, replay, concurrency and access evidence before interface freeze. Legal/provider activation gates remain scoped; no runtime completion is claimed by this plan.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Sequence the named owner contract amendments before dependent adapters. Location owns closed purpose-qualified source catalog and current disclosure decisions. Service and interview purposes have distinct authorized fields/participants. Source owners provide current facts; revoked/stale/unsupported inputs deny, exact fields stay out of public/notification payloads. Numerical policies, legal retention and provider qualification remain explicit gates. Require bilateral denial, stale-revision and replay fixtures before activation; this pass supplies architecture, not executed qualification.

## Domain bridge qualification — 2026-10-15

For WA-R077; WA-R080, sequence the relevant owner contract/DTO fixtures, shared durable mechanism qualification and bilateral negative/replay/currentness checks before dependent consumer activation. Use the exact Module architecture ports and source scopes. Database posture D and policy/provider requirements gate their affected slices; no broad product implementation or parallel lane is authorized by this reconciliation. R079 creates no required Order-to-Sweepstakes dependency. Do not treat a successful queue dispatch, enumerator page or provider response as completion of the originating lifecycle.

## WA-R081–083 — Integrated bridge sequence

Follow Module owner contracts and the complete bridge inventory before cross-Cluster integration. CONTRACT_ONLY work may establish schemas/fakes; FOUNDATION_CAPABILITY is required before actual effects; executable bilateral and external evidence precede freeze/activation. R081 named queries/receipts, R082 Media invalidation, and R083 disabled optional paths supersede only the corresponding historical open labels. Keep current source checks at action/disclosure boundaries. Do not begin whole-Cluster parallel work, root synthesis or runtime implementation from source-coverage counts alone.
