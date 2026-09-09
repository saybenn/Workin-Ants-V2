# Privacy & Location Safety Build Plan

> **Repository location:** `context/privacy-location-safety/build-plan.md`  
> **Cluster ID:** CL-08  
> **Cluster:** Privacy & Location Safety  
> **Companion architecture:** `context/privacy-location-safety/architecture.md`  
> **Plan status:** Implementation sequence; decision-gated where architecture/legal policy is unresolved  
> **Total numbered features:** 11

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
2. Follow root Workin Ants `architecture.md` and `code-standards.md`.
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
16. Do not treat Proposed Rulings in the architecture as approved unless the progress tracker or root architecture explicitly records approval.
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
- structured logging and telemetry redaction;
- Audit / Event Ledger append interfaces;
- shared encryption and keyed hashing;
- standardized validation/error contracts.

### Shared-operation prerequisites

The following canonical operations are major dependencies:

```text
resolveAuthenticatedActor
authorizeResourceAction
queryOwnerFacts
evaluateComplianceHold
authorizeContextualResourceAccess
appendAuditEvent
recordSensitiveAccess
executeIdempotentCommand
publishDomainEvent
deduplicateDomainEvent
enqueueReliableJob
orchestrateWorkflowSteps
reconcileWorkflowStatus
transitionLifecycleState
acquireAggregateLock
withOptimisticConcurrency
runDeadlineExpiration
encryptSensitiveValue
normalizeAndHashIdentifier
requestSearchProjectionRefresh
issueSignedMediaUrl
enumerateSubjectData
evaluateRetentionRequirement
executePrivacyInstruction
orchestratePrivacyFulfillment
createPrivacyExportArtifact
resolveLocationReveal
applyFuzzyPublicLocation
validateOwnedTargetReference
```

If a canonical operation has not yet been implemented, implement or schedule it in its canonical owner. Do not create a CL-08-only substitute.

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

- `resolveAuthenticatedActor` — Identity owner; establishes requester. Privacy supplies no alternate auth helper.
- `authorizeResourceAction` — Role / Authority owner; Privacy supplies request ownership/admin context. Do not build `privacyAuth`.
- `executeIdempotentCommand` — platform owner; used for submission retry safety. Privacy supplies semantic request fingerprint; do not build local idempotency storage.
- `appendAuditEvent` — Audit owner; records sanitized submission/admin actions. Do not create a privacy audit table.
- `createRequestContext` / `writeStructuredLog` / `sanitizeTelemetryMetadata` — platform/Ops; no request-body dumping.

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

- `enumerateSubjectData` — each owner implements; Privacy defines protocol. No global DB crawler.
- `evaluateRetentionRequirement` — owner supplies facts; Privacy does not encode tax/contract/etc. logic.
- `executePrivacyInstruction` — typed execution protocol; no owner creates PrivacyRequest.
- `validateOwnedTargetReference` — target owner validates existence/context.
- `queryOwnerFacts` — narrow owner DTOs only.
- `executeIdempotentCommand` — used by executor commands.
- `createRequestContext`, `writeStructuredLog`, `sanitizeTelemetryMetadata`.

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
enumerateSubjectData(request)
evaluateRetentionRequirement(request)
executePrivacyInstruction(request)
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

Use `enqueueReliableJob` only if inventory size requires async execution; otherwise synchronous dry-run is acceptable for test fixtures.

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

Make `applyFuzzyPublicLocation` and `FuzzyLocationCache` real source-backed Location Safety behavior.

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

- `applyFuzzyPublicLocation` — Location Safety canonical public interface; no consumer-side fuzzing.
- `queryOwnerFacts` / `validateOwnedTargetReference` — get source location safely.
- `executeIdempotentCommand` — duplicate refresh safety.
- `acquireAggregateLock` or `withOptimisticConcurrency` — one projection per target.
- `geocodeAddress` — only behind Location-owned port if needed; provider may be stubbed.
- `requestSearchProjectionRefresh` — invoked through Search contract, not direct index call.
- `publishDomainEvent` / `enqueueReliableJob` only if approved for refresh/expiry.
- `sanitizeTelemetryMetadata` — exact location omitted from logs.

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
applyFuzzyPublicLocation(...)
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

Expiry worker may use `runDeadlineExpiration` when policy exists.

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

- `orchestratePrivacyFulfillment` — Privacy-owned workflow.
- `enumerateSubjectData` — inventory.
- `evaluateRetentionRequirement` — owner facts.
- `executePrivacyInstruction` — owner mutation.
- `anonymizePersonalFields` — owner-specific field map.
- `orchestrateWorkflowSteps` / `reconcileWorkflowStatus` — mechanism only.
- `enqueueReliableJob` / `executeRetryWithBackoff`.
- `executeIdempotentCommand`.
- `appendAuditEvent` / `recordSensitiveAccess` where applicable.
- `recordIntegrationFailure`.

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
- encryption/hash primitives if approved by export artifact contract.
- Audit.

### Shared Operations Used

- `createPrivacyExportArtifact` — Privacy owns bundle; Media owns storage.
- `enumerateSubjectData` — owner export sections.
- `issueSignedMediaUrl` — Media owner.
- `hashCanonicalPayload` — artifact/manifest integrity if required.
- `encryptSensitiveValue` or approved archive encryption mechanism where root security contract requires it.
- `recordSensitiveAccess` — issuance/download.
- `enqueueReliableJob` — generation/expiry cleanup.
- `runDeadlineExpiration` — bundle expiry.
- `executeIdempotentCommand`.
- `sanitizeTelemetryMetadata`.

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

- `requestNotification` may notify requester when ready/failed if approved template exists.

No direct R2 client in Privacy.

### Failure Behavior

- one owner serializer fails → bundle fails or waits according to approved export policy; do not silently omit owner data;
- Media upload failure → bundle `failed`;
- signed URL issuance failure → bundle remains ready; access attempt fails and is observable;
- expired bundle → deny even if stale URL UI remains;
- cleanup failure → bundle remains expired and Ops records retryable cleanup failure.

### Tests

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

- `resolveAuthenticatedActor`
- `authorizeResourceAction`
- `requireStepUpForSensitiveAction` only if approved policy requires it
- `orchestratePrivacyFulfillment`
- `transitionLifecycleState`
- `reconcileWorkflowStatus`
- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `requestNotification`
- `appendAuditEvent`
- `recordSensitiveAccess`
- `executeIdempotentCommand`
- `enqueueReliableJob`

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

Implement `resolveLocationReveal` as the single exact-location disclosure decision and `LocationReveal` as viewer/context reveal truth.

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

- `resolveLocationReveal` — Location Safety owner.
- `resolveAuthenticatedActor`.
- `authorizeResourceAction`.
- `authorizeContextualResourceAccess`.
- `queryOwnerFacts`.
- `evaluateComplianceHold` only if approved predicate uses it.
- `encryptSensitiveValue` for approved exact storage/decryption.
- `normalizeAndHashIdentifier` for IP/request proof.
- `executeIdempotentCommand`.
- `acquireAggregateLock` / `withOptimisticConcurrency`.
- `recordSensitiveAccess`.
- `appendAuditEvent`.
- `sanitizeTelemetryMetadata`.

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
resolveLocationReveal(...)
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

- `deduplicateDomainEvent`
- `publishDomainEvent`
- `enqueueReliableJob`
- `executeRetryWithBackoff`
- `resolveLocationReveal`
- `applyFuzzyPublicLocation`
- `requestSearchProjectionRefresh`
- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `recordSensitiveAccess`
- `appendAuditEvent`

### Data / Schema

- `FuzzyLocationCache`
- `LocationReveal`
- approved explicit location privacy target types if PR-08-05 is accepted.

Potential retention fields are added only if approved architecture requires them.

### Public Interfaces

Location Privacy executor implements:

```text
enumerateSubjectData
evaluateRetentionRequirement
executePrivacyInstruction
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

- `requestSearchProjectionRefresh`
- `issueSignedMediaUrl`
- `deleteProviderResource` through provider owners
- `appendAuditEvent`
- `recordSensitiveAccess`
- `requestNotification`
- `recordIntegrationFailure`
- `createRequestContext`
- `sanitizeTelemetryMetadata`
- `enqueueReliableJob`
- `executeIdempotentCommand`

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
requestSearchProjectionRefresh
issueSignedMediaUrl
Media privacy executor
appendAuditEvent
recordSensitiveAccess
requestNotification
recordIntegrationFailure
```

### Logic

- propagate correlation/causation IDs;
- owner transaction commits before downstream projection/notification dispatch;
- dedupe downstream event handling;
- retry transient failures;
- do not roll back Privacy/Location truth merely because a nonauthoritative notification fails;
- do not mark Search projection successful until Search acknowledges its own work.

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

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- `queryOwnerFacts`
- `validateOwnedTargetReference`
- `authorizeOrderEntitlement` where delivery/order entitlement facts are required by an owner, not as privacy truth
- `resolveLocationReveal`
- `applyFuzzyPublicLocation`
- `requestSearchProjectionRefresh`
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

- `executeIdempotentCommand`
- `deduplicateDomainEvent`
- `enqueueReliableJob`
- `executeRetryWithBackoff`
- `reconcileWorkflowStatus`
- `reconcileProviderState` through provider owners
- `reconcileSearchProjection`
- `runDeadlineExpiration`
- `acquireAggregateLock`
- `withOptimisticConcurrency`
- `recordIntegrationFailure`
- `checkServiceHealth`
- `correlateOpsIncident`
- `sanitizeTelemetryMetadata`
- `appendAuditEvent`
- `recordSensitiveAccess`.

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
- exports are private, short-lived, audited, and cleaned up;
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
