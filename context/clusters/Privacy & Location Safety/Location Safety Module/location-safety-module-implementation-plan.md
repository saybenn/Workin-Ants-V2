# Location Safety Module Implementation Plan

> **Module ID:** `location_safety`  
> **Module:** Location Safety Module  
> **Primary Cluster:** CL-08 Privacy & Location Safety  
> **Companion architecture:** `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`<br>
> **Plan status:** Ordered Module implementation plan; decision-gated where CL-08 safety/privacy decisions remain unresolved  
> **Relationship to Cluster plan:** Subordinate to `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`. This plan decomposes only the Location Safety work inside CL-08 Features 03, 07, 08, 09, 10, and 11. It does not change Cluster sequencing, legal gates, or ownership.

**Shared Operation status:** References use permanent IDs and canonical names from `context/shared/shared-operations.md`; that registry controls owner, classification, status, and reusable boundary. SH-003 queryOwnerFacts remains **Proposed ruling** and is not an unconditional prerequisite or an approved universal DTO/API. Adoption requires separate Shared Operations approval before API/schema commitment. Existing source-owner-specific public queries may be consumed within their approved contracts; direct cross-domain Prisma/repository reads remain prohibited. SH-015 returnDecisionResult and SH-069 geocodeAddress remain **Proposed ruling** wherever referenced; this pass does not approve them.

### Current context paths and missing artifact roles

Read `context/context-map.md` first for authority by concern, then the existing artifacts relevant to the feature:

- Overview: `context/project-overview-v3.md`.
- Shared Operations: `context/shared/shared-operations.md`.
- Cluster architecture: `context/clusters/Privacy & Location Safety/privacy-location-safety-architecture.md`.
- Cluster build plan: `context/clusters/Privacy & Location Safety/privacy-location-safety-build-plan.md`.
- Module architecture: `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`.
- Module implementation plan: `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-implementation-plan.md`.

Root/repository-root and context-root `architecture.md`, `build-plan.md`, `code-standards.md`, and dedicated `progress-tracker.md` are currently **missing**. References to those global artifacts below describe future roles, not loadable files or current authority. Do not create local substitutes or infer global approval. Apply existing concern owners through the context map; stop work that needs a missing global decision. Until a dedicated tracker is available, report progress/blockers in the task completion report; progress does not approve architecture.

---

## Core Principle

Implement Location Safety through narrow, verifiable slices:

```text
public / observable behavior
→ validated command or query
→ Location Safety-owned policy
→ authoritative FuzzyLocationCache / LocationReveal write or read
→ canonical shared-operation calls
→ Search / Audit / Ops / Privacy effects through owner interfaces
→ tests
→ exit gate
```

The Module does not own a general map or address-management UI. Its observable outputs are primarily:

- a safe public-location projection;
- a persisted fuzzy projection;
- an exact-location reveal decision and proof;
- reveal revocation behavior;
- a Location-owned privacy executor result;
- durable refresh/reconciliation workers;
- public integration contracts;
- bounded administrative diagnostics where root/Cluster admin architecture permits them.

Do not invent map rendering, directions, service-area calculation, dispatch, logistics, or address-collection UI to create a visible surface for this Module.

---

## Build Rules

1. Follow the CL-08 architecture and build plan within `context/context-map.md` authority by concern; root architecture/code standards are currently missing.
2. Location Safety owns only its declared truth: `FuzzyLocationCache`, `LocationReveal`, `LocationPrecision`, `LocationRevealStatus`, and the policies governing safe precision/fuzzing and exact reveal.
3. Source Modules remain owners of exact/source location facts and source-object lifecycles.
4. Booking, Order, source, Search, Audit, Privacy, Identity, Role / Authority, Compliance Hold, and Ops truth must be consumed through approved public interfaces.
5. Reuse Canonical Shared Operations. Never create local auth, authorization, audit, crypto, hashing, queue, idempotency, lock, Search, rate-limit, or observability frameworks.
6. Every mutation uses runtime validation and server-side authorization when actor-driven.
7. Every retryable mutation defines semantic idempotency behavior.
8. Every concurrency-sensitive lifecycle write uses database-backed shared locking or optimistic concurrency.
9. Exact location is never returned from cached frontend eligibility.
10. Exact location is never sent to public Search, ordinary logs, analytics, ordinary domain-event payloads, notifications, or public map rendering.
11. Search changes occur through Search-owned interfaces; Location Safety must not write `SearchUpsertEvent` or call Typesense directly.
12. `LocationReveal` remains separate from `AccessAuditLog` and `AuditEvent`.
13. Privacy / Data Erasure owns `PrivacyRequest`, privacy jobs/targets, retention exemptions, and aggregate fulfillment. Location Safety implements only its own executor.
14. Provider details stay behind a provider-neutral geocoding port if and only if geocoder adapter ownership/provider choice is approved.
15. Location-owned jobs are durable, retryable, correlated, and observable through canonical shared infrastructure, including `SH-038 recordQueueTelemetry`.
16. No production fuzzy radius, stability, expiry, reveal predicate, directionality, revocation rule, retention period, context uniqueness rule, or provider choice may be guessed.
17. Every numbered feature ends with automated tests and an explicit exit gate.
18. If a decision-gated feature depends on unresolved architecture, stop that feature and record the blocker. Do not make tests green by inventing policy.
19. Build progress may not silently reinterpret Booking's duplicate location fields.
20. Architecture must be updated before a binding ownership, lifecycle, schema, security, or public-contract decision changes.
21. A downstream integration failure must not silently change Location Safety source truth.
22. A public consumer may receive only Location Safety-approved public projection data and must never perform its own fuzzing from exact input.

---

## Preconditions

### Hard platform dependencies

Before production Location Safety work reaches the relevant slice, the platform must supply or schedule in its canonical owner:

- Prisma/PostgreSQL migrations and transactions;
- canonical authenticated actor resolution;
- Role / Authority decision API;
- canonical idempotent command mechanism;
- canonical aggregate lock and/or optimistic concurrency mechanism;
- transactional outbox/inbox if Location domain events are enabled;
- reliable queue, retry, and dead-letter mechanism;
- request/correlation context;
- structured logging and telemetry redaction;
- Audit / Event Ledger append and sensitive-access interfaces;
- shared encryption and keyed-hashing implementation;
- standardized runtime validation and error/decision-result conventions;
- root rate-limit mechanism where rate limiting is required.

These are hard architectural dependencies. They may not be reimplemented inside Location Safety.

### Required owner interfaces

The following may initially be represented by approved fakes/stubs for contract tests, but real interfaces are required before the corresponding production exit gate:

- Booking location/gate facts;
- Order participant/transaction gate facts;
- source-owner target validation and source-location facts;
- Search projection refresh/removal request;
- Audit generic event/sensitive-access append;
- Privacy executor protocol;
- ComplianceHold query if an approved reveal policy uses holds;
- Observability / Ops integration-failure and correlation interfaces.

### Existing schema foundation

Current Prisma already defines:

- `FuzzyLocationCache`;
- `LocationReveal`;
- `LocationPrecision`;
- `LocationRevealStatus`.

The current Booking schema also physically contains:

- `Booking.locationPrecision`;
- `Booking.locationRevealStatus`;
- `Booking.exactAddressEncrypted`;
- `Booking.fuzzyLat`;
- `Booking.fuzzyLng`.

Those Booking fields are not automatically Location Safety truth. Do not migrate, synchronize, reinterpret, or remove them until the approved Booking/Location reconciliation decision exists.

### Provider setup

The geocoder provider is undecided. Contract/domain tests may use a fake provider-neutral adapter. Production provider activation waits for U-08-20 and approval of adapter ownership/provider choice.

### Decision gates

The following are hard production blockers:

```text
U-08-10 canonical exact-location owner outside Booking
U-08-11 semantic status of Booking duplicate location fields
U-08-12 LocationReveal context model
U-08-13 exact reveal predicate
U-08-14 viewer directionality
U-08-15 reveal revocation triggers
U-08-16 audit fail-open / fail-closed transaction boundary
U-08-17 fuzzy radius / stability / expiry / regeneration / algorithm policy
U-08-18 controlled target vocabulary for FuzzyLocationCache.targetType
U-08-19 LocationReveal uniqueness / current-state / history model
U-08-20 geocoder and KMS/key-management implementation
U-08-21 LocationReveal / fuzzy-cache privacy retention policy
U-08-23 explicit Location Safety privacy target types
```

### Work that may proceed before those decisions

Agents may safely build:

- typed public contracts;
- owner-local repositories;
- safe public projection mechanics with explicitly nonproduction policies;
- fail-closed target/policy handling;
- safe status/history reads;
- shared-operation integration;
- provider-neutral ports and fake adapters;
- event/job plumbing that does not enable unapproved outcomes;
- observability/redaction;
- contract/concurrency harnesses.

They may not invent production legal/safety values.

---

# Phase 1 — Contracts and Public Projection Foundation

## 01 Location Safety Contract and Repository Foundation

### Objective

Establish the Module boundary, typed public contracts, owner-local repositories, runtime validation, and safe result types without activating unresolved production safety policy.

### Observable Result

- Location Safety exposes typed contracts for fuzzy projection, reveal status/decision, revocation, history, source-owner facts, and Privacy executor participation.
- Repositories read/write only Location Safety-owned records.
- Direct cross-Module Prisma access is structurally absent.
- Contract tests can invoke safe fake dependencies and receive provider-neutral result categories.
- Decision-gated exact reveal cannot accidentally return exact location.

### Cluster Build-Plan Link

Supports:

- CL-08 Feature 03 — Fuzzy Public Location Projection;
- CL-08 Feature 07 — Exact Location Reveal contract groundwork;
- CL-08 Feature 10 — Booking/Order Location Contracts.

### Dependencies

- current Prisma schema;
- root runtime validation/error conventions;
- Canonical Shared Operations definitions;
- `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`;
- owner-fact interface placeholders or contract fakes.

### In Scope

- `contracts/public.ts`;
- `contracts/owner-facts.ts`;
- `contracts/privacy-executor.ts`;
- `contracts/geocoding-port.ts` as a provider-neutral interface only;
- runtime schemas/validators for public command/query inputs and outputs;
- repository interfaces and implementations for `FuzzyLocationCache` and `LocationReveal` only;
- stable safe DTOs that cannot serialize exact location on public projection reads;
- a supported-target registry abstraction with no broad production target list beyond explicit approved/test fixtures;
- test doubles for owner-fact interfaces;
- stable safe error/decision categories consistent with root patterns.

### Out of Scope

- production fuzzing radius/stability/expiry;
- actual exact-location disclosure;
- Booking/Order direct reads;
- Search implementation;
- Audit implementation;
- geocoder provider selection;
- schema migration for reveal uniqueness/context;
- Privacy target enum migration;
- general map or address UI.

### Module-Owned Data

- `FuzzyLocationCache`;
- `LocationReveal`;
- `LocationPrecision`;
- `LocationRevealStatus`.

No new source truth is introduced.

### Public Interfaces

Declare and validate:

```text
applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
getPublicLocationProjection
refreshFuzzyLocationProjection
invalidateFuzzyLocationProjection
resolveLocationReveal # SH-027 resolveLocationReveal
getLocationRevealStatus
revokeLocationReveal
listLocationRevealHistory
```

Declare Location Safety's implementation shape for the Privacy executor protocol:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
```

`SH-027 resolveLocationReveal` and privacy mutation paths remain disabled/decision-gated until later features.

### Shared Operations Used

- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — owned by each source Module; proposed shared contract only. Use already-approved owner-specific queries; do not shape or commit a universal DTO from this proposal. Location policy remains local. **Do not build:** a universal cross-domain repository.
- `SH-123 validateOwnedTargetReference` — source target owner; validates source identity/context. **Do not build:** direct target-existence Prisma helpers.
- `SH-015 returnDecisionResult (Proposed ruling; adoption gated)` — shared contract if/when root adopts it; used only for normalized response shape. Location owns reason/policy semantics. **Do not build:** a second generic decision framework.
- `SH-032 createRequestContext` / `SH-034 sanitizeTelemetryMetadata` — platform/Ops; used in contract tests and delivery boundaries. Location owns which fields are sensitive. **Do not build:** Location-specific request tracing or telemetry sanitizer framework.

### Domain Logic

- Public projection DTOs structurally exclude exact/source address and exact coordinates.
- Unsupported target types fail closed.
- Public callers cannot choose `exact_private` or force precision.
- Reveal result types clearly separate safe decision metadata from an exact-value payload that can exist only on an approved protected allow path.
- Provider-specific error/status objects do not cross the geocoding port.
- `LocationReveal` and `FuzzyLocationCache` repositories expose owner-local persistence only.

### Authorization / Compliance

No protected business mutation is activated yet.

Contract requirements must make actor/context fields explicit for protected operations. Anonymous public reads are permitted only where the returned shape is guaranteed to be safe projection data.

### Database / Transaction Behavior

- Preserve `FuzzyLocationCache` unique `[targetType, targetId]`.
- Preserve existing LocationReveal indexes.
- Do not add reveal uniqueness, context, FK, timestamp, or version constraints before architecture approval.
- No direct writes to Booking, Order, Search, Audit, Privacy, User, or provider-owned records.

### Events / Jobs

Contracts may define internal payload shapes only when they do not commit to unapproved domain-event names or policies.

Do not publish Location domain events unless PR-08-03/root event registration has been approved.

### Provider Integration

Define a fake/in-memory `GeocodingPort` implementation for tests only. Add no production provider SDK or credentials.

### UI / Admin Surface

No user-facing UI is required.

A developer test harness may be used only if root standards allow it and it contains no real sensitive location data.

### Failure Behavior

- invalid input → stable validation error;
- unsupported target → fail closed;
- decision-gated operation → explicit `policy_not_configured` / feature-disabled result;
- owner-fact contract unavailable → typed unavailable/retryable result;
- no fallback direct database read;
- no provider-specific exception leakage.

### Tests

- request/result schema contract tests;
- runtime validation tests;
- public DTO exact-field exclusion tests;
- repository ownership boundary tests;
- unsupported target tests;
- decision-gated reveal tests;
- provider-neutral error normalization tests;
- static dependency/import checks where repository tooling permits them.

### Documentation Updates

Update Module architecture only if implementation proves a binding public-contract change is required.

Record any missing dependency contract in the progress tracker.

### Acceptance Criteria

- all declared interfaces have runtime-validatable request/result shapes;
- public projection result structurally cannot expose exact location;
- only Location-owned repositories are present;
- decision-gated exact reveal cannot execute;
- provider-specific types are absent from domain/public contracts;
- no direct cross-Module repository exists.

### Exit Gate

Before Feature 02:

- repository-defined typecheck and lint commands pass;
- Location contract/unit tests pass;
- static ownership/dependency checks pass where configured;
- no new Prisma ownership outside Location models was introduced;
- progress tracker records any dependency contracts still represented by fakes.

---

## 02 Fuzzy Public Location Vertical Slice

### Objective

Implement the first working Location Safety behavior: a supported test/source target produces one safe fuzzy projection backed by `FuzzyLocationCache`, while exact input never leaves protected server scope.

### Observable Result

- A supported fixture/source target can request a fuzzy projection.
- Exactly one `FuzzyLocationCache` row exists per `targetType + targetId`.
- `getPublicLocationProjection` returns fuzzy coordinates/radius/freshness only.
- Unsupported or production-unconfigured targets return no projection.
- Exact source location is absent from response, analytics, logs, and downstream mock payloads.

### Cluster Build-Plan Link

Directly implements the Location Safety portion of CL-08 Feature 03 — Fuzzy Public Location Projection.

### Dependencies

- Feature 01;
- `FuzzyLocationCache` schema;
- owner-fact fake or approved real interface for one test target;
- canonical idempotency and DB concurrency mechanism.

### In Scope

- local precision policy interface;
- local `fuzzCoordinates` operation;
- explicit deterministic **nonproduction** safety-policy fixture;
- `SH-028 applyFuzzyPublicLocation`;
- `getPublicLocationProjection`;
- `refreshFuzzyLocationProjection`;
- owner-local cache upsert;
- safe serializer;
- semantic idempotent same-source refresh behavior;
- fail-closed supported-target/policy checks.

### Out of Scope

- production radius/stability/expiry values;
- broad `LocationTargetType` enum;
- exact reveal;
- production geocoder;
- real Typesense/Search indexing;
- general map UI;
- non-approved multi-source target support.

### Module-Owned Data

`FuzzyLocationCache`.

### Public Interfaces

Activate:

```text
applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
getPublicLocationProjection
refreshFuzzyLocationProjection
```

`invalidateFuzzyLocationProjection` may be implemented owner-locally but downstream Search behavior is completed in Feature 03.

### Shared Operations Used

- `SH-044 executeIdempotentCommand` — platform owner; wraps semantic projection mutation. Local policy defines target/source/policy fingerprint. **Do not build:** Location idempotency table/service.
- `SH-051 acquireAggregateLock` or `SH-052 withOptimisticConcurrency` — shared persistence; protects one current projection per target. Local policy defines aggregate key. **Do not build:** in-memory mutex.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` / `SH-123 validateOwnedTargetReference` — source owner; provide source input/reference. Local policy defines what data is required. **Do not build:** direct source repository.
- `SH-034 sanitizeTelemetryMetadata` — Ops/platform; removes unsafe fields according to Location sensitivity policy. **Do not build:** ad hoc logging sanitizer framework.

### Domain Logic

- Fuzzy projection is derived from protected source input.
- Production target without an approved policy returns `policy_not_configured` and does not write a production projection.
- Test/staging fixtures must be explicitly labeled nonproduction.
- One current cache row exists per target pair.
- Same semantic source/policy refresh replays the existing effect rather than creating duplicate truth.
- Public result includes no exact source address or coordinates.
- Fuzzy result is not evidence of source visibility, Booking eligibility, or exact-reveal eligibility.

### Authorization / Compliance

- public read returns safe projection only;
- source refresh command is system/source-owner authorized;
- no frontend precision override;
- no exact data is serialized into client state;
- no Track entitlement or consent is interpreted as a location reveal permission.

### Database / Transaction Behavior

Within the Location write transaction:

1. validate the target and protected source input;
2. acquire shared lock/CAS as appropriate;
3. create/replace `FuzzyLocationCache`;
4. commit Location truth.

Preserve the unique target-pair constraint.

Do not invent `sourceVersion` or `policyVersion` columns before approval; test semantics may carry those values in contract fixtures without migrating production schema.

### Events / Jobs

No domain event is required for the first vertical slice.

No scheduled expiry is activated yet.

### Provider Integration

The source fixture supplies coordinates directly. A fake geocoder may be tested, but no production provider is necessary.

### UI / Admin Surface

Optional bounded projection inspector may show:

- target type;
- safe target reference;
- fuzzy coordinates;
- radius;
- generated/expiry timestamps;
- policy configured/unconfigured.

It must not display exact source data.

### Failure Behavior

- unsupported target → fail closed;
- policy not configured → no production row written;
- missing source facts → no projection;
- concurrent refresh → deterministic shared DB conflict/retry behavior;
- persistence failure → no public result claiming successful projection;
- stale source handling remains decision-gated if source-version semantics are unavailable.

### Tests

Unit:

- precision classification with fixtures;
- deterministic nonproduction fuzzing;
- exact-field exclusion;
- unsupported/policy-not-configured behavior.

Integration:

- unique upsert;
- concurrent refresh;
- idempotent replay;
- safe query read.

Privacy/security:

- logs and analytics contain no exact input;
- public response contains no exact fields.

E2E:

- public fixture renders approximate location only.

### Documentation Updates

If a target type or production policy becomes approved while implementing this feature, update architecture first before enabling it.

### Acceptance Criteria

- one supported test target creates exactly one cache row;
- public query returns only safe projection;
- repeated semantic request does not create duplicate effect;
- unsupported/unconfigured target remains unavailable;
- exact input is absent from response/log/analytics surfaces.

### Exit Gate

- repository-defined typecheck/lint pass;
- Location fuzzy unit/integration/E2E fixture tests pass;
- exact-input leakage checks pass;
- no production radius/target policy was invented;
- CL-08 Feature 03 mechanical projection behavior is demonstrable.

---

## 03 Projection Invalidation, Search Request, and Expiry Worker

### Objective

Complete long-lived fuzzy projection mechanics so source/privacy changes can invalidate or refresh Location Safety truth and safely request downstream Search updates.

### Observable Result

- `invalidateFuzzyLocationProjection` makes a target's public projection unavailable.
- A successful Location commit causes Search refresh/removal through Search's public interface.
- Search failure does not corrupt Location truth and is retryable/observable.
- Expiry worker mechanics can be proven with explicit test policy without inventing production expiry duration.

### Cluster Build-Plan Link

Supports:

- CL-08 Feature 03 — projection refresh/invalidation;
- CL-08 Feature 09 — Search/Ops bridge;
- CL-08 Feature 11 — fuzzy expiry/reconciliation hardening.

### Dependencies

- Features 01–02;
- Search `SH-091 requestSearchProjectionRefresh` contract;
- shared reliable-job, scheduler, and observability operations;
- approved source-change events if event-driven refresh is used.

### In Scope

- `invalidateFuzzyLocationProjection`;
- Search public-interface client/adapter, not provider client;
- post-commit Search refresh/removal dispatch;
- Search retry job;
- fuzzy refresh worker payload/handler;
- expiry worker using canonical scheduler;
- safe `IntegrationFailure` reporting;
- request/correlation propagation;
- dedupe when approved source events are consumed.

### Out of Scope

- direct Typesense client;
- direct `SearchUpsertEvent` writes;
- production expiry/radius policy U-08-17;
- exact reveal;
- source visibility lifecycle;
- generic queue or cron framework.

### Module-Owned Data

`FuzzyLocationCache`.

Optional Location domain events remain disabled unless root event registration approves them.

### Public Interfaces

Complete:

```text
refreshFuzzyLocationProjection
invalidateFuzzyLocationProjection
```

Consume:

```text
requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
```

### Shared Operations Used

- `SH-091 requestSearchProjectionRefresh` — Search owner; invoked after Location commit. Local policy supplies only safe fuzzy payload/reason. **Do not build:** direct Typesense/SearchUpsertEvent writer.
- `SH-047 enqueueReliableJob` — shared queue; dispatches retryable refresh/removal. Local policy supplies business idempotency/correlation. **Do not build:** `locationQueue`.
- `SH-055 runDeadlineExpiration` — shared scheduler; invokes cache-expiry work. Local policy defines expiry semantics only after approval. **Do not build:** custom cron scheduler.
- `SH-044 executeIdempotentCommand` — platform; protects repeated invalidation/refresh.
- `SH-045 deduplicateDomainEvent` — platform inbox; used only for approved source events. **Do not build:** per-worker dedupe table.
- `SH-037 recordIntegrationFailure` — Ops; records Search/source-provider operational failure. **Do not build:** Location-owned ops failure table.
- `SH-032 createRequestContext` / `SH-034 sanitizeTelemetryMetadata` — correlation/redaction.

### Domain Logic

- Location truth commits before downstream Search work is considered complete.
- Search receives only Location Safety-approved fuzzy data.
- Invalidation is idempotent.
- Search failure becomes pending/retryable; it does not restore an unsafe/stale Location projection.
- Location may complete its own cache/projection-source mutation independently. SH-091 requestSearchProjectionRefresh acceptance does not prove completed Search deletion for a required Privacy target; that target needs Search-owned completion evidence. The durable receipt representation remains unresolved.
- Expiry acts only under explicit approved/test policy.
- If source-version evidence exists, stale events cannot overwrite newer projection state.
- If version semantics are absent, do not invent a production last-writer policy beyond safe transactional conflict handling.

### Authorization / Compliance

- system/source events use approved system authority;
- manual invalidation requires explicit administrative authority;
- public callers cannot invoke arbitrary invalidation;
- Search command payload contains no exact location.

### Database / Transaction Behavior

- cache mutation transaction is Location-local;
- downstream Search work follows root outbox/job pattern;
- no distributed transaction writes Search tables;
- aggregate key remains `targetType + targetId`.

### Events / Jobs

Jobs:

- fuzzy refresh;
- Search refresh/removal retry;
- expiry scan/dispatch.

Optional root-approved events:

```text
location.public_projection.updated
location.public_projection.invalidated
```

Event payloads must be exact-location free.

### Provider Integration

None. Search's Typesense adapter remains Search-owned.

### UI / Admin Surface

Bounded diagnostics may show:

- stale/expired cache count;
- Search refresh pending/failure count;
- correlation ID;
- safe target type/reference;
- retry/dead-letter state.

### Failure Behavior

- Search unavailable → record failure + retry; Location truth remains authoritative;
- source owner unavailable → retry refresh; do not generate from guessed data;
- unsupported target → terminal safe unavailable;
- duplicate source event/job → no duplicate domain effect;
- retry exhaustion → shared dead-letter/manual-review path with safe metadata.

### Tests

- invalidation idempotency;
- Search payload contains fuzzy data only;
- Search failure/retry;
- duplicate event/job dedupe;
- expiry fixture behavior;
- no direct Search provider/import;
- correlation propagation;
- telemetry redaction;
- refresh vs invalidation concurrency.

### Documentation Updates

If production expiry semantics are approved, update U-08-17 decisions in architecture before enabling scheduled production expiry.

If Location domain events are approved, register the root event contracts before enabling publication.

### Acceptance Criteria

- invalidation makes public projection unavailable deterministically;
- Search is invoked only through its owner contract;
- Search failure is observable and retryable;
- exact data never enters Search command/event/job payloads;
- workers use shared queue/scheduler primitives.

### Exit Gate

- targeted unit/integration/worker tests pass;
- Search contract test passes;
- telemetry redaction test passes;
- no direct Typesense or Search table write exists;
- fuzzy projection slice is ready for cross-Cluster integration.


# Phase 2 — Exact Reveal Contract and Lifecycle

## 04 Reveal Status, History, and Decision Contract Foundation

### Objective

Implement the safe read surface and exact-reveal decision scaffolding without returning exact location or inventing the unresolved reveal predicate.

### Observable Result

- `getLocationRevealStatus` can read existing authoritative reveal metadata without returning exact location.
- `listLocationRevealHistory` is capability-gated and returns minimized metadata.
- `SH-027 resolveLocationReveal` request/result validation exists, but production execution returns an explicit decision-gated result until required architecture is approved.
- Booking/Order consumers cannot treat their own status fields as Location Safety reveal authority.

### Cluster Build-Plan Link

Prepares CL-08 Feature 07 — Exact Location Reveal and Viewer-Specific Lifecycle while respecting its decision gate.

### Dependencies

- Feature 01;
- Identity actor interface;
- Role / Authority interface;
- existing `LocationReveal` schema;
- root anti-enumeration/error conventions;
- canonical audit policy for protected history access if applicable.

### In Scope

- `getLocationRevealStatus`;
- `listLocationRevealHistory`;
- safe reveal-history DTO;
- reveal command request/result validators;
- explicit feature-disabled / policy-not-configured result;
- actor and Role / Authority integration for protected reads;
- safe reason-code namespace that does not settle eligibility policy;
- conflict detection for ambiguous current state where current schema permits multiple rows.

### Out of Scope

- exact source retrieval or decryption;
- creating `eligible` or `revealed` state;
- reveal predicate;
- viewer directionality;
- revocation triggers;
- context/uniqueness/FK migration;
- audit fail-open/fail-closed decision;
- Booking duplicate-field synchronization.

### Module-Owned Data

Read-only access to `LocationReveal` in this feature.

### Public Interfaces

Activate:

```text
getLocationRevealStatus
listLocationRevealHistory
```

Scaffold but keep production-disabled:

```text
resolveLocationReveal # SH-027 resolveLocationReveal
revokeLocationReveal
```

### Shared Operations Used

- `SH-001 resolveAuthenticatedActor` — Identity & Access; establishes viewer/admin. Location owns requested reveal/history purpose. **Do not build:** current-user helper.
- `SH-002 authorizeResourceAction` — Role / Authority; decides permission to read status/history. Location owns reveal safety semantics. **Do not build:** `locationPermissionService`.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — source owners; contract types may be wired but no reveal decision yet. **Do not build:** Booking/Order repositories.
- `SH-030 recordSensitiveAccess` — Audit owner; use for protected history access only if canonical audit policy requires it. **Do not build:** Location history audit table.
- `SH-032 createRequestContext` / `SH-034 sanitizeTelemetryMetadata` — platform/Ops.

### Domain Logic

- Status queries never return exact/source value.
- History excludes exact address/coordinates and unsafe source payloads.
- A row's `status` is Location truth; Booking's `locationRevealStatus` is not consulted as authoritative truth.
- If current schema yields conflicting candidate rows for the same conceptual context, return a stable conflict/diagnostic result rather than selecting a winner by guess.
- The reveal command contract requires fresh actor/context/owner-fact inputs but does not define an allow predicate until architecture is approved.

### Authorization / Compliance

- protected status/history reads require authenticated actor;
- normal users may see only authorized viewer/context status;
- admin/support history access requires explicit capability;
- admin/support role does not imply exact-location access;
- do not add step-up unless root security policy explicitly requires it.

### Database / Transaction Behavior

Read-only queries in this feature.

Do not add uniqueness, FK, context, timestamp, source-version, or policy-version constraints until U-08-12/U-08-19 and related decisions are approved.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

Only if root admin patterns already exist, add a bounded safe history surface showing:

- reveal ID;
- Booking/Order context IDs;
- viewer safe identifier;
- status;
- created/revealed/revoked timestamps;
- safe reason;
- safe audit/correlation references where available.

Never display the exact address/coordinates in this diagnostic.

### Failure Behavior

- unauthenticated → authentication denial;
- unauthorized → root-standard forbidden/not-found behavior;
- ambiguous/conflicting current rows → explicit model conflict;
- unknown context → safe not-found/unavailable;
- production reveal request → explicit decision-gated result, never partial disclosure;
- audit/ops failure on a read follows root criticality policy and does not create reveal truth.

### Tests

- cross-user status/history denial;
- authorized own-context read;
- admin capability tests;
- safe serialization/exact-field absence;
- ambiguous-row handling;
- reveal command remains disabled;
- Booking duplicate status is not treated as truth;
- telemetry redaction.

### Documentation Updates

If U-08-12/U-08-19 are approved during implementation, update Module and Cluster architecture before any migration or lifecycle behavior is added.

### Acceptance Criteria

- safe status/history reads work through Location's public interface;
- exact source read does not occur;
- unresolved schema ambiguity is surfaced explicitly;
- protected read authorization is canonical;
- reveal mutation remains impossible while policy is unresolved.

### Exit Gate

- status/history contract and authorization tests pass;
- exact-leakage tests pass;
- no exact retrieval path exists;
- required U-08 blockers for Feature 05 are explicitly recorded in the progress tracker.

---

## 05 Exact Location Reveal and Viewer-Specific Lifecycle

Reuse `SH-088 manageTemporaryAccessGrant` for common temporary reveal mechanics and `SH-089 revokeTemporaryAccessGrant` for revocation mechanics where invoked. Location Safety alone owns `LocationReveal` policy, transitions, and proof; production remains subject to the existing decision gates.

**Decision-Gated Feature. Do not implement production behavior until every decision required by the enabled reveal context is approved and architecture is updated.**

### Objective

Implement `SH-027 resolveLocationReveal` as the single authoritative exact-location disclosure decision and `LocationReveal` as viewer/context reveal truth.

### Observable Result

An eligible, authorized viewer can request exact location and receive it only after a fresh server-side decision. An ineligible or unauthorized viewer receives no exact data. The committed Location Safety state and required sensitive-access proof are visible through safe status/history interfaces.

### Cluster Build-Plan Link

Directly implements the Location Safety portion of CL-08 Feature 07 — Exact Location Reveal and Viewer-Specific Lifecycle.

### Dependencies

- Features 01 and 04;
- Feature 02/03 only where fuzzy/source-version behavior is part of the approved context;
- real or approved-stub Identity actor interface;
- Role / Authority interface;
- Booking facts interface;
- Order facts interface;
- exact source-location owner interface;
- Audit interfaces;
- shared crypto/key-management;
- shared idempotency/concurrency.

Hard architecture approvals include, as applicable:

- U-08-10 — exact source owner;
- U-08-11 — Booking duplicate fields;
- U-08-12 — reveal context model;
- U-08-13 — reveal predicate;
- U-08-14 — directionality;
- U-08-15 — at least the lifecycle/revocation semantics necessary to make reveal state safe;
- U-08-16 — audit transaction boundary;
- U-08-19 — uniqueness/current-state/history model;
- U-08-20 — crypto/KMS implementation where exact data is encrypted.

### In Scope

- approved reveal transition model;
- approved context/uniqueness/FK/timestamp migration;
- approved source/policy/gate-version proof fields if required;
- fresh owner-fact composition;
- exact source retrieval through owner interface;
- canonical decryption boundary;
- Location Safety final allow/deny decision;
- `LocationReveal` write;
- sensitive-access/audit ordering under U-08-16;
- protected exact-value response;
- semantic idempotent replay;
- concurrency control;
- exact-location leak prevention.

### Out of Scope

- Booking/Order lifecycle mutation;
- direct payment/refund/dispute mutation;
- general map UI;
- directions/routing/logistics;
- service-area computation;
- address collection UI;
- client-side caching/prefetch of exact location;
- notification delivery unless a separate binding trigger is approved.

### Module-Owned Data

- `LocationReveal`;
- `LocationRevealStatus`.

Apply only migrations already approved in architecture.

### Public Interfaces

Activate:

```text
resolveLocationReveal # SH-027 resolveLocationReveal
getLocationRevealStatus
listLocationRevealHistory
```

If approved architecture separates decision from value issuance, expose separate commands/queries but preserve Location Safety as the owner and preserve the same security invariants.

### Shared Operations Used

- `SH-001 resolveAuthenticatedActor` — Identity; fresh viewer identity. Local policy defines requested reveal action. **Prohibited duplicate:** local session helper.
- `SH-002 authorizeResourceAction` — Role / Authority; general permission. Local policy remains the final reveal safety decision. **Prohibited duplicate:** Location generic permission engine.
- `SH-026 authorizeContextualResourceAccess` — relevant context owner/shared contract; returns contextual access facts/decision shape. Location remains final reveal owner. **Prohibited duplicate:** one universal entitlement/access engine.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — Booking/Order/source owners; fresh minimal facts. **Prohibited duplicate:** cross-domain Prisma queries.
- `SH-011 evaluateComplianceHold` — Hold owner, only when U-08-13 makes a hold relevant. Location maps applicable holds into reveal policy. **Prohibited duplicate:** `revealBlocked` flag.
- `SH-075 encryptSensitiveValue` / approved decrypt operation — shared crypto; protects reversible exact data. Location owns when decryption is permitted. **Prohibited duplicate:** `addressCrypto`.
- `SH-076 normalizeAndHashIdentifier` — shared crypto; produces non-plaintext IP/request evidence where required. **Prohibited duplicate:** local HMAC/IP hash helper.
- `SH-044 executeIdempotentCommand` — platform; duplicate reveal safety. Location supplies semantic input fingerprint. **Prohibited duplicate:** local idempotency table.
- `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency` — persistence primitive; protects reveal aggregate. Location defines aggregate key after U-08-12/U-08-19. **Prohibited duplicate:** in-memory reveal mutex.
- `SH-053 transitionLifecycleState` — shared state-machine mechanism; Location supplies the approved transition matrix. **Prohibited duplicate:** generic global policy table.
- `SH-030 recordSensitiveAccess` — Audit owner; records exact-location access decision/result according to U-08-16. **Prohibited duplicate:** LocationAccessLog.
- `SH-029 appendAuditEvent` — Audit owner; records important reveal/review/admin action where required. **Prohibited duplicate:** generic Location audit table.
- `SH-034 sanitizeTelemetryMetadata` — Ops/platform; exact fields removed according to local sensitivity policy.

### Domain Logic

Implement the approved matrix exactly. The intended sequencing is:

1. resolve authenticated actor;
2. authorize the protected resource action;
3. load fresh Booking/Order/source owner facts;
4. validate the approved reveal context and source/gate versions;
5. evaluate applicable ComplianceHold facts if the approved predicate uses them;
6. compose the Location Safety reveal decision;
7. on deny, return safe denial without exact data;
8. on allow, obtain exact source value through the source-owner interface;
9. decrypt only after allow;
10. acquire/validate the reveal aggregate state;
11. write the approved `LocationReveal` state/proof transactionally;
12. satisfy the approved audit criticality/ordering rule;
13. return exact data through the protected response only;
14. never persist the exact value in `LocationReveal`, Search, ordinary logs, analytics, ordinary events, or notifications unless a later approved schema explicitly requires a protected Location-owned value.

Paid state, Booking state, general role permission, consent, or Track entitlement alone never constitutes the Location Safety allow decision.

### Authorization / Compliance

- authenticated viewer is mandatory;
- participant/admin relationship follows Role / Authority and source-owner facts;
- exact reveal predicate is evaluated server-side inside Location Safety;
- paid/provider state alone is insufficient;
- consent alone is insufficient;
- Track entitlement alone is insufficient;
- step-up is consumed only if root policy explicitly requires it;
- stale/missing owner facts fail closed;
- exact reveal must be limited to approved directionality/purpose/context.

### Database / Transaction Behavior

Apply only approved schema changes, potentially including:

- Booking/Order/source referential integrity;
- exactly-one/allowed-context constraints;
- viewer/context current-state uniqueness or append-only history model;
- timestamp consistency;
- source/policy/gate-version fields.

A single Location transaction must protect the LocationReveal lifecycle write. The exact value must not be returned if the approved lifecycle write/required proof does not satisfy the approved transaction boundary.

Use a database-backed aggregate lock/CAS. Do not rely on process memory.

### Events / Jobs

Potential root-approved facts:

```text
location.reveal.eligible
location.revealed
```

If emitted:

- publish through canonical transactional outbox after the owning commit;
- minimize payload;
- never include exact address/coordinates;
- include correlation/causation and source/policy versions where approved.

No async job may bypass the fresh reveal gate to precompute/cache exact data for a viewer.

### Provider Integration

No geocoder/map provider is required on the exact reveal path unless the approved source owner contract requires a protected geocoding step.

Shared KMS/crypto is infrastructure, not Location business truth.

### UI / Admin Surface

Consuming Booking/Order UI may expose only states supplied by Location Safety:

- hidden;
- eligible "show exact location" action;
- revealed;
- revoked/denied.

The exact value must not appear in page source, hydration data, prefetch caches, analytics, or public map data before the protected reveal action where on-demand reveal is the approved model.

Admin/compliance surfaces default to reveal metadata only. Exact admin view requires a separately approved authority/safety path.

### Failure Behavior

- unauthenticated → deny;
- unauthorized → deny;
- stale/missing Booking/Order/source facts → deny;
- predicate not satisfied → deny with stable safe reason;
- source missing → deny/unavailable;
- crypto/key unavailable → no reveal; record operational failure;
- audit failure → follow approved U-08-16 policy;
- duplicate reveal → idempotent replay without duplicate domain effect;
- reveal state conflict → deterministic concurrency conflict/retry;
- source changed between gate and exact read → reject/re-evaluate per approved source-version rule;
- provider error strings never reach caller.

### Tests

Domain:

- approved reveal predicate matrix;
- directionality matrix;
- transition matrix;
- safe reason codes;
- source/gate version behavior.

Authorization:

- cross-user denial;
- participant scope;
- admin/support explicit capability;
- entitlement/consent/paid-state-alone insufficiency.

Integration:

- Booking facts;
- Order facts;
- source location owner;
- Audit;
- crypto.

Concurrency/idempotency:

- duplicate reveal;
- simultaneous reveal attempts;
- stale source;
- reveal write conflict.

Security/privacy:

- no exact in logs/Search/events/analytics/notification payloads;
- no exact in prefetch/hydration where prohibited;
- protected response only.

E2E:

- authorized reveal;
- ineligible reveal;
- unauthorized reveal;
- stale/context-changed denial.

### Documentation Updates

Before coding, update Cluster and Module architecture with every resolved U-08 decision and approved migration.

After completion, update progress tracker with enabled contexts, directionality, audit policy, and any still-disabled reveal cases.

### Acceptance Criteria

- exactly one authoritative reveal state/history model exists per approved context;
- exact value is returned only after a fresh Location Safety allow;
- Booking/Order cannot bypass Location Safety;
- denial/error paths never leak exact data;
- audit behavior matches approved U-08-16;
- idempotency/concurrency produce deterministic one-effect behavior.

### Exit Gate

- all required U-08 decisions for the enabled reveal context are approved in architecture;
- approved migration tests pass;
- domain/contract/integration/concurrency/security/E2E reveal tests pass;
- no provider/client/log/Search path exposes exact location;
- CL-08 Feature 07 exit criteria for Location Safety are satisfied.

---

## 06 Revocation and Gate-Change Reconciliation

Reuse `SH-088 manageTemporaryAccessGrant` for common temporary reveal mechanics and `SH-089 revokeTemporaryAccessGrant` for revocation mechanics where invoked. Location Safety alone owns `LocationReveal` policy, transitions, and proof; production remains subject to the existing decision gates.

**Decision-Gated Feature. Requires approved revocation triggers, reveal state model, and source event/fact contracts.**

### Objective

Ensure a previously eligible/revealed viewer cannot continue to obtain exact location after approved source, transaction, schedule, hold, time, location, or privacy conditions invalidate access.

### Observable Result

- approved Booking/Order/source changes deterministically re-evaluate affected reveals;
- `revokeLocationReveal` changes Location Safety truth under the approved lifecycle;
- revoked viewers cannot retrieve exact location afterward;
- duplicate source events do not duplicate revocation side effects;
- reconciliation failures are visible without leaking location data.

### Cluster Build-Plan Link

Implements the reveal-reconciliation portion of CL-08 Feature 08 — Location Revocation, Privacy Executor, and Gate-Change Reconciliation.

### Dependencies

- Feature 05;
- approved U-08-15 revocation trigger matrix;
- approved U-08-19 current-state/history model;
- approved source event contracts or equivalent owner-fact change triggers;
- canonical event dedupe/job infrastructure;
- approved fail-closed behavior for owner-fact outages where required.

### In Scope

- `revokeLocationReveal`;
- `evaluateRevealRevocation`;
- handlers for approved source/gate events;
- event dedupe;
- fresh owner-fact reload;
- reveal reconciliation worker;
- safe audit/access evidence;
- post-revocation exact-access denial;
- source-location-change coordination with fuzzy refresh when required.

### Out of Scope

- changing Booking/Order/source lifecycle state;
- defining new ComplianceHold reasons;
- generic event bus/inbox;
- Search indexing implementation;
- Privacy erasure/retention policy;
- adding unsupported source event families.

### Module-Owned Data

`LocationReveal`.

`FuzzyLocationCache` may be refreshed/invalidated as a separate Location truth when the source location itself changes; reveal and fuzzy state must not be merged.

### Public Interfaces

Activate:

```text
revokeLocationReveal
getLocationRevealStatus
```

Consume approved source events/fact queries.

### Shared Operations Used

- `SH-045 deduplicateDomainEvent` — event infrastructure; one source event causes one Location effect. Local policy maps event to affected reveals. **Do not build:** local processed-event table.
- `SH-047 enqueueReliableJob` — shared queue; durable re-evaluation. Local policy supplies affected context. **Do not build:** Location queue framework.
- `SH-048 executeRetryWithBackoff` if canonical operation exists in root shared registry; used for transient owner-fact/integration failures. **Do not build:** custom retry loop framework.
- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — Booking/Order/source owners; reload fresh facts. **Do not build:** direct event-payload lifecycle interpretation as truth when owner query is required.
- `SH-044 executeIdempotentCommand` — duplicate revoke safety.
- aggregate lock/CAS — reveal vs revoke serialization.
- `SH-030 recordSensitiveAccess` / `SH-029 appendAuditEvent` — Audit owner; safe evidence.
- `SH-037 recordIntegrationFailure` / telemetry operations — Ops owner.

### Domain Logic

- consume only approved event types;
- dedupe before business effect according to root inbox pattern;
- reload authoritative owner facts instead of trusting an old event payload as complete current state;
- evaluate the approved revocation policy;
- transition once under the approved lifecycle;
- repeated revoke is idempotent;
- subsequent exact retrieval still runs the fresh reveal gate and honors revoked/current-cycle semantics;
- source location change may require reveal re-evaluation plus fuzzy refresh, but these are separate truth changes;
- a stale event must not revoke or restore a newer valid state incorrectly.

### Authorization / Compliance

- system/event actor uses approved system context;
- manual revocation requires explicit Role / Authority capability;
- admin may not create an arbitrary permanent local block; reusable stop signs remain `ComplianceHold` truth;
- exact value is not needed to perform revocation.

### Database / Transaction Behavior

- use reveal row/current-context lock or CAS under the approved aggregate key;
- apply approved timestamp constraints;
- event dedupe + Location effect follow root transaction/outbox/inbox pattern;
- no direct Booking/Order/source writes;
- no fuzzy cache/reveal transaction is made cross-owner distributed.

### Events / Jobs

Worker: reveal reconciliation.

Potential root-approved fact:

```text
location.reveal.revoked
```

Retry transient owner-fact failures. Repeated terminal failures go to shared dead-letter/manual review with safe metadata only.

### Provider Integration

None.

### UI / Admin Surface

Safe reconciliation diagnostic may show:

- affected reveal count;
- pending/retry/dead-letter count;
- source event type/version;
- safe reason code;
- correlation ID.

No exact location.

### Failure Behavior

- source owner unavailable → retry; exact retrieval continues to follow the approved fail-closed policy;
- duplicate event → replay/no-op;
- stale event → ignore or reload/re-evaluate according to approved version rule;
- illegal transition → conflict/manual review;
- audit failure → approved U-08-16/criticality policy;
- worker retry exhaustion → shared dead-letter/manual review;
- source location changed while worker runs → use current owner version before commit.

### Tests

- every approved revocation trigger;
- duplicate event;
- stale/out-of-order event;
- reveal vs revoke race;
- repeated revoke;
- post-revoke exact denial;
- source-location-change coordination;
- no direct Booking/Order/source writes;
- dead-letter safe metadata;
- telemetry redaction.

### Documentation Updates

Record the approved revocation trigger matrix, source event contracts, and stale-event policy in architecture before implementation.

### Acceptance Criteria

- every approved trigger has a deterministic Location outcome;
- revoked state blocks subsequent access according to the approved lifecycle;
- retries/deduplication do not create duplicate effects;
- source lifecycles remain source-owned;
- exact location is not present in event/job/diagnostic payloads.

### Exit Gate

- revocation matrix tests pass;
- concurrency/event-dedupe tests pass;
- post-revocation exact-access E2E passes;
- audit/telemetry remain safe;
- CL-08 Feature 08 revocation criteria are satisfied.


# Phase 3 — Privacy and Long-Lived Location Data

## 07 Location Safety Privacy Executor

**Decision-Gated for production disposition until Location retention and Privacy target-type decisions are approved.**

### Objective

Make Location Safety a first-class Privacy / Data Erasure executor without transferring Privacy request, job, target, or retention-exemption ownership into this Module.

### Observable Result

Privacy can:

- enumerate Location Safety subject-linked records;
- ask Location Safety for retention facts;
- instruct approved erase/anonymize/retain behavior;
- receive a typed disposition result;
- cause the public fuzzy projection to disappear from Location truth and request Search removal where required.

### Cluster Build-Plan Link

Implements the Privacy-executor portion of CL-08 Feature 08 and contributes to CL-08 Feature 10 executor coverage.

### Dependencies

- Features 02–03;
- Feature 05 if production `LocationReveal` rows exist;
- Privacy / Data Erasure executor protocol;
- Search refresh/removal interface;
- shared idempotency/concurrency;
- U-08-21 Location retention/privacy policy;
- U-08-23 / PR-08-05 explicit Location privacy target model for first-class production execution.

### In Scope

- `privacy/location-privacy-executor.ts`;
- subject-data enumeration for Location-owned records;
- stable/minimized Location target descriptors;
- owner-local retention fact response;
- approved erase/anonymize/retain execution;
- fuzzy invalidation/deletion and Search removal request;
- idempotent privacy execution;
- safe result/evidence mapping;
- concurrency with refresh/reveal/revoke;
- executor coverage diagnostics.

### Out of Scope

- creating/updating `PrivacyRequest`;
- creating/updating `DataErasureJob` or `DataErasureTarget` directly;
- creating `DataRetentionExemption`;
- deciding GDPR/CCPA/legal retention law;
- generic subject-data crawler;
- provider deletion outside Location-owned provider resources;
- deleting source Module exact-location records directly.

### Module-Owned Data

- `FuzzyLocationCache`;
- `LocationReveal`.

Potential additions to `DataErasureTargetType` remain Privacy-owned schema changes even when they name Location targets.

### Public Interfaces

Implement the Privacy-owned protocol as Location Safety's owner implementation:

```text
enumerateSubjectData # SH-096 enumerateSubjectData
evaluateRetentionRequirement # SH-097 evaluateRetentionRequirement
executePrivacyInstruction # SH-095 executePrivacyInstruction
```

Location Safety does not expose a competing Privacy request API.

### Shared Operations Used

- `SH-096 enumerateSubjectData` — Privacy-defined contract / owner implementation; Location enumerates only Location truth. **Prohibited duplicate:** global privacy crawler.
- `SH-097 evaluateRetentionRequirement` — owner-facts contract; Location supplies safety/security retention facts. Privacy owns final exemption record. **Prohibited duplicate:** Location retention-exemption table.
- `SH-095 executePrivacyInstruction` — owner command contract; Location mutates only its own records. **Prohibited duplicate:** local PrivacyRequest workflow.
- `SH-123 validateOwnedTargetReference` — target owner; validates any source linkage needed to identify the subject safely.
- `SH-044 executeIdempotentCommand` — privacy retry/replay safety.
- aggregate lock/CAS — protects privacy action against refresh/reveal/revoke races.
- `SH-091 requestSearchProjectionRefresh` — Search owner; remove/update downstream public projection after Location commit.
- `SH-030 recordSensitiveAccess` / `SH-029 appendAuditEvent` — Audit owner where privacy execution/access policy requires proof.
- `SH-037 recordIntegrationFailure` / telemetry operations — Ops owner.

### Domain Logic

- Enumerate only Location-owned records tied to the data subject under the approved subject-link mapping.
- Target descriptors must not include exact third-party location or unnecessary personal data.
- Retention facts come from approved Location safety/security policy, not arbitrary administrator choice.
- A retained result returns basis/facts to Privacy; Privacy records `DataRetentionExemption`.
- Erase/anonymize only fields allowed by the approved retention matrix.
- Removing/invalidation of a fuzzy projection must request Search removal.
- Do not claim `erased` while a required Location-owned effect remains incomplete.
- Do not directly erase exact location stored by Booking/source Modules; Privacy dispatches separate instructions to those owners.
- Operational audit/queue success does not substitute for the typed privacy disposition result.

### Authorization / Compliance

- system instruction carries Privacy request/target identity and canonical idempotency context;
- executor revalidates target/subject linkage at execution time;
- no support/admin force-delete bypasses retention policy;
- no entitlement or consent is required to exercise the Privacy instruction itself;
- retention conflicts are returned explicitly as owner facts/results.

### Database / Transaction Behavior

- each privacy command is idempotent;
- lock/CAS Location rows when concurrent reveal/refresh/revoke is possible;
- local disposition commits in Location transaction;
- Search request follows Location commit;
- no cross-owner distributed transaction;
- immutable external Privacy proof is not stored as a duplicate Location lifecycle.

### Events / Jobs

Privacy execution may run through `SH-047 enqueueReliableJob` under Privacy/owner coordination.

Location may emit approved Location projection/reveal facts if root event contracts already exist, but it must not emit a fake Privacy completion event.

### Provider Integration

No persistent geocoder resource is currently assumed. If a selected provider later stores user-specific persistent resources, update architecture and provider privacy behavior before execution support is added.

### UI / Admin Surface

Safe Privacy coverage diagnostic may show:

- Location target type;
- executor status: implemented / policy-unsupported / decision-gated / failed;
- retention policy status;
- safe disposition result;
- retry/dead-letter state;
- Search removal status.

No raw location payload.

### Failure Behavior

- retention policy unresolved → decision-gated/unsupported, never guessed delete;
- unknown target → explicit not-found/unsupported;
- target/subject mismatch → deny/fail terminally;
- Search failure after cache removal → Location disposition remains committed; Search removal is retryable/observable;
- concurrent reveal/refresh → lock/conflict/retry;
- owner/source unavailable during validation → retryable failure, not silent erasure;
- repeated instruction → replay prior result.

### Tests

- subject enumeration;
- target descriptor minimization;
- target/subject validation;
- retained/anonymized/erased outcomes after approval;
- idempotent replay;
- refresh/reveal/revoke versus privacy races;
- Search removal request/retry;
- no `PrivacyRequest`/`DataRetentionExemption` direct write;
- no source Module exact-location deletion;
- privacy telemetry redaction.

### Documentation Updates

Approve and record U-08-21/U-08-23 before production disposition is enabled.

Update the Cluster executor coverage matrix/progress tracker with actual Location target types and supported actions.

### Acceptance Criteria

- Privacy inventories Location records through the standard owner contract;
- every enabled disposition has approved retention semantics;
- retained outcomes return owner facts rather than creating local exemption truth;
- public projection is removed when required;
- no Privacy lifecycle ownership moves into Location Safety;
- source exact-location records remain source-owned.

### Exit Gate

- Privacy executor contract tests pass;
- enabled disposition integration tests pass;
- Search removal/retry tests pass;
- concurrency/privacy tests pass;
- U-08-21/U-08-23 are approved for production or affected disposition paths remain explicitly disabled;
- CL-08 Feature 08 privacy-executor criteria for Location Safety are satisfied.

---

# Phase 4 — Module Integration

## 08 Booking, Order, Source, Search, Audit, and Ops Contract Integration

### Objective

Replace Location Safety's test doubles with real public owner interfaces and prove the important cross-Module boundaries without direct database coupling or lifecycle reinterpretation.

### Observable Result

- Location Safety obtains Booking/Order/source facts only through typed owner APIs.
- Fuzzy projection changes reach the real Search interface.
- Exact reveal, when enabled, records canonical sensitive-access proof through Audit.
- Operational failures appear through Ops with correlation.
- Cross-Cluster tests prove source → Location → Search and Booking/Order → Location reveal behavior without ownership theft.

### Cluster Build-Plan Link

Supports:

- CL-08 Feature 09 — Search, Media, Audit, Notification, and Ops Bridges, limited to Location-relevant bridges;
- CL-08 Feature 10 — Booking/Order Location Contracts and supported source-location contracts.

### Dependencies

- Features 03–07 for the paths being enabled;
- implementation-ready dependency public interfaces;
- root request/correlation and contract-version conventions;
- approved reveal/privacy decision gates for any enabled protected path.

### In Scope

- real Search `SH-091 requestSearchProjectionRefresh` integration;
- real Audit `SH-029 appendAuditEvent` / `SH-030 recordSensitiveAccess` integration;
- real Booking minimal location/gate facts DTO;
- real Order minimal participant/transaction gate facts DTO;
- real source-location facts DTO for approved target types;
- real Observability/Ops integration;
- contract version/compatibility tests;
- correlation/causation propagation;
- coverage checks that detect missing owner interfaces.

### Out of Scope

- Search internals or Typesense;
- Booking/Order lifecycle implementation;
- Media file mechanics/EXIF handling;
- Notification unless a binding Location Safety business trigger has been approved;
- neighboring Module refactors for style;
- direct cross-Module Prisma reads as a shortcut.

### Module-Owned Data

No ownership change.

This feature validates use of:

- `FuzzyLocationCache`;
- `LocationReveal` for enabled reveal path.

### Public Interfaces

Verify/freeze compatible versions for Location outputs:

```text
applyFuzzyPublicLocation # SH-028 applyFuzzyPublicLocation
getPublicLocationProjection
refreshFuzzyLocationProjection
invalidateFuzzyLocationProjection
resolveLocationReveal          # if enabled # SH-027 resolveLocationReveal
getLocationRevealStatus
revokeLocationReveal           # if enabled
listLocationRevealHistory
```

Inbound dependency contracts:

```text
Booking owner facts
Order owner facts
source-location facts
requestSearchProjectionRefresh # SH-091 requestSearchProjectionRefresh
appendAuditEvent # SH-029 appendAuditEvent
recordSensitiveAccess # SH-030 recordSensitiveAccess
recordIntegrationFailure / request context # SH-037 recordIntegrationFailure
```

### Shared Operations Used

- `SH-003 queryOwnerFacts (Proposed ruling; adoption gated)` — each owner; real owner DTOs replace fakes. Local Location policy remains separate. **Prohibited duplicate:** direct neighboring repositories.
- `SH-123 validateOwnedTargetReference` — source owner; target validation.
- `SH-091 requestSearchProjectionRefresh` — Search owner; safe projection only.
- `SH-029 appendAuditEvent` / `SH-030 recordSensitiveAccess` — Audit owner; generic proof only.
- `SH-032 createRequestContext`, `SH-033 writeStructuredLog`, `SH-034 sanitizeTelemetryMetadata`, `SH-037 recordIntegrationFailure` — Ops/platform.
- idempotency/event/job/concurrency primitives already introduced in prior features.

### Domain Logic

- Owner DTOs are minimal and purpose-specific.
- Location Safety does not infer Booking/Order lifecycle from raw database fields outside those interfaces.
- Source owners provide source location/reference/version; they do not calculate fuzzy coordinates on Location's behalf.
- Search receives safe public projection only.
- Audit receives target/action/decision/safe context only, not exact payload.
- Ops evidence never changes `LocationReveal` or `FuzzyLocationCache` state.
- A missing or incompatible owner contract fails closed rather than triggering direct database access.

### Authorization / Compliance

Contract/integration tests must cover:

- participant relationship;
- unauthorized actor;
- stale source/gate facts;
- admin/support scope;
- reveal enabled/disabled configuration;
- exact-value redaction at every boundary.

### Database / Transaction Behavior

- no cross-Module transaction writes another owner's tables;
- downstream effects use owner commands/acknowledgements and root outbox/job patterns;
- Location's own transaction boundaries remain local;
- direct Prisma data coupling is prohibited.

### Events / Jobs

Wire real canonical queue/outbox/inbox paths for enabled Location workers.

Do not import neighbor provider SDKs or provider-specific event tables.

### Provider Integration

None directly except an approved geocoder port. Search's provider remains behind Search; Booking's calendar provider remains behind Booking; Audit storage remains Audit-owned.

### UI / Admin Surface

Integration diagnostics may show:

- dependency contract version/status;
- last successful safe correlation;
- pending Search/Audit/Ops failures;
- supported Location target types;
- reveal/privacy path enabled/decision-gated state.

No exact location.

### Failure Behavior

- missing owner contract → fail closed and release-gate failure;
- protocol/version mismatch → explicit incompatibility;
- Search failure → Location truth remains committed, downstream pending;
- Audit failure → exact reveal follows approved U-08-16;
- Ops failure-record write failure does not become Location business success/failure by itself;
- stale owner facts → reload/reject according to owner/version contract;
- no fallback direct Prisma read.

### Tests

Contract:

- Booking facts;
- Order facts;
- source-location facts;
- Search refresh;
- Audit append/access;
- Ops correlation/failure record.

Integration/E2E:

- approved source location → fuzzy cache → Search safe projection;
- source invalidation → Search removal;
- Booking/Order reveal decision journey if enabled;
- sensitive-access proof if exact reveal enabled;
- Privacy → Location executor if enabled.

Static architecture:

- no dependency on neighbor repository implementation;
- no direct Search/Audit/Booking/Order write;
- exact-location payload is absent from Search/Audit/Ops external metadata.

### Documentation Updates

If actual approved dependency interface names/versions differ from planning names, update Module architecture/public-interface references before treating the integration as stable.

### Acceptance Criteria

- every real cross-Module dependency uses the owner interface;
- Search sees no exact location;
- Audit remains separate truth;
- no direct Booking/Order/source read/write exists;
- contract mismatch fails visibly;
- correlation links Location work to downstream operational evidence without logging exact data.

### Exit Gate

- all Location-relevant CL-08 Feature 09/10 contract tests pass;
- representative cross-Cluster fuzzy E2E passes;
- exact reveal integration E2E passes if enabled;
- Privacy executor integration passes if enabled;
- ownership/static-boundary checks pass;
- progress tracker records every still decision-gated dependency.

---

# Phase 5 — Provider and Production Policy Activation

## 09 Geocoding Adapter and Production Fuzzy Policy Activation

**Decision-Gated for production activation.**

### Objective

Activate provider-backed fuzzy projection only after the supported target vocabulary, fuzzy safety policy, and geocoder/security choices are approved.

### Observable Result

For each approved production target type:

- source location can be converted through a provider-neutral geocoder when coordinates are required;
- Location Safety applies an approved versioned fuzzy policy;
- cache freshness/expiry/regeneration behavior is deterministic;
- provider outage does not expose exact data or replace safe projection with unsafe output;
- downstream Search continues to receive fuzzy-only data.

### Cluster Build-Plan Link

Completes production aspects of CL-08 Feature 03 and supports CL-08 Feature 11 production hardening.

### Dependencies

- Features 02–03 and 08;
- U-08-17 fuzzy policy;
- U-08-18 controlled target vocabulary;
- U-08-20 geocoder selection;
- explicit architecture approval that Location Safety owns the geocoder adapter for canonical `SH-069 geocodeAddress (Proposed ruling; adoption gated)`;
- approved policy/source version representation if production reconciliation requires it;
- secret-management/provider configuration.

### In Scope

- production supported-target registry;
- approved radius/stability/regeneration/expiry algorithm policy;
- approved policy-version representation;
- selected geocoder adapter;
- credential/secret configuration through root mechanisms;
- timeout/retry/rate-limit translation;
- provider response normalization;
- projection reconciliation against source/policy versions when modeled;
- production expiry/refresh worker activation;
- provider health/failure telemetry;
- backfill plan for already-supported targets if needed.

### Out of Scope

- map UI/rendering;
- directions/routing;
- service area or logistics;
- changing source address ownership;
- provider output as source truth;
- exact reveal policy;
- selecting a second provider without architecture update.

### Module-Owned Data

`FuzzyLocationCache`.

Apply only approved schema additions such as source/policy version fields or worker-scan indexes if architecture explicitly requires them.

### Public Interfaces

No new business interface is required. Existing fuzzy operations become production-configured for approved targets.

Provider-neutral port becomes active:

```text
geocodeAddress # SH-069 geocodeAddress (Proposed ruling; adoption gated)
```

### Shared Operations Used

- `SH-069 geocodeAddress (Proposed ruling; adoption gated)` — Location Safety provider-adapter pattern once approved; adapter normalizes provider result. Local Location policy performs fuzzing. **Prohibited duplicate:** provider SDK calls in Search/Booking/business Modules.
- `SH-047 enqueueReliableJob` / shared retry-backoff — durable provider/refresh work. **Prohibited duplicate:** custom queue/retry framework.
- `SH-037 recordIntegrationFailure` — Ops owner; provider failures. **Prohibited duplicate:** provider failure as cache status truth.
- `SH-044 executeIdempotentCommand` + lock/CAS — projection write correctness.
- `SH-091 requestSearchProjectionRefresh` — Search owner after commit.
- `SH-034 sanitizeTelemetryMetadata` — provider request/response redaction.

### Domain Logic

- provider result is input, not source truth;
- only explicitly approved target types/policy versions are enabled;
- no public caller supplies arbitrary radius/precision;
- bad/ambiguous/no-result provider response cannot create an unsafe projection;
- transient geocoder failure does not silently replace a valid safe projection with exact or guessed data;
- expired/untrusted projection follows the approved public-unavailable/regeneration policy;
- source/policy version downgrade is rejected when version semantics are modeled;
- map rendering continues to receive fuzzy coordinates only.

### Authorization / Compliance

- provider calls are server-side only;
- credentials remain in approved secret management;
- geocoding input uses `SH-078 minimizeAndRedactProviderInput` with source-owner policy and purpose-bound field allowlists;
- provider telemetry excludes exact address/coordinate payload where not necessary;
- public endpoints cannot expose the underlying provider request or source exact location.

### Database / Transaction Behavior

- apply approved migrations only;
- staged backfill is resumable/idempotent;
- backfill never overwrites source location;
- cache update remains one current target projection;
- Search request occurs after Location commit;
- rollback path must preserve safe public behavior.

### Events / Jobs

- production fuzzy expiry/refresh;
- stale source/policy reconciliation;
- geocoder retry jobs;
- Search refresh after successful Location commit.

Optional Location events remain subject to root registration.

### Provider Integration

Selected adapter contract tests must cover:

- request normalization/minimization;
- successful geocode;
- no result;
- ambiguous result;
- invalid provider response;
- timeout;
- rate limit;
- transient failure;
- terminal authentication/configuration failure;
- response/error redaction.

### UI / Admin Surface

Safe provider/policy diagnostic may show:

- supported target type;
- policy version;
- generated/expiry time;
- provider health;
- retry/failure category;
- stale projection count.

Never show exact geocoding input or raw provider payload.

### Failure Behavior

- provider outage → retry/retain or invalidate according to approved freshness policy, never unsafe fallback;
- bad provider output → reject, no cache update;
- secret/config missing → provider unavailable/terminal configuration failure;
- policy version unknown → fail closed;
- source version stale → reject/reload;
- Search failure → downstream retry;
- backfill anomaly → stop and preserve existing source/safe state.

### Tests

- production target registry;
- policy-version matrix;
- property tests for approved fuzzing bounds/stability;
- geocoder adapter normalization/failures;
- timeout/rate-limit/retry;
- expiry/regeneration;
- stale source/policy reconciliation;
- exact telemetry redaction;
- batch worker performance;
- backfill idempotency/rollback;
- public/Search fuzzy-only E2E.

### Documentation Updates

Before activation, record:

- selected geocoder/provider;
- adapter ownership;
- supported target vocabulary;
- policy versions;
- radius/stability/expiry/regeneration rules;
- provider configuration/secret requirements in library docs where appropriate;
- migration/backfill and rollback plan.

### Acceptance Criteria

- no production target is enabled without explicit policy;
- provider adapter is isolated behind the port;
- cache behavior is deterministic under approved policy;
- provider degradation cannot cause exact-location exposure;
- Search/public output remains fuzzy only.

### Exit Gate

- U-08-17/U-08-18/U-08-20 and geocoder ownership are approved;
- provider adapter contract/integration tests pass;
- production policy unit/property tests pass;
- migration/backfill verification passes;
- Search/public leakage tests pass;
- production fuzzy policy is enabled only for the approved target set.

---

# Phase 6 — Module Hardening and Production Verification

## 10 Security, Concurrency, Reconciliation, Privacy, and Production Hardening

### Objective

Prove Location Safety remains correct under retries, races, stale owner facts, source changes, provider degradation, privacy instructions, Search failure, audit failure, and security-sensitive exact-location access.

### Observable Result

- stale/orphan fuzzy projections are detected and repaired or removed;
- duplicate web requests/jobs/events do not duplicate domain effects;
- reveal/revoke races are deterministic when reveal is enabled;
- revoked access cannot be reused;
- key/geocoder/Search/Audit failures follow approved fail-safe behavior;
- Privacy execution is replay-safe when enabled;
- operators have bounded, safe diagnostics/manual-review visibility;
- every production-enabled path has no unresolved decision dependency.

### Cluster Build-Plan Link

Implements the Location Safety portion of CL-08 Feature 11 — Security, Reconciliation, Privacy, and Production Hardening.

### Dependencies

- Features 01–09 for all production-enabled paths;
- all required root shared operations in production form;
- all required decision gates approved, or affected feature remains explicitly disabled;
- production dependency contracts from Feature 08.

### In Scope

- fuzzy source/policy-version reconciliation;
- orphan/stale cache detection;
- projection backfill verification;
- refresh/invalidation race hardening;
- reveal/revoke race hardening if enabled;
- stale owner-fact defense;
- source location change during request;
- key rotation/decrypt compatibility if exact reveal enabled;
- geocoder outage behavior if provider enabled;
- Search retry/reconciliation handoff;
- Audit criticality behavior if exact reveal enabled;
- Privacy executor replay/concurrency if enabled;
- root rate-limit integration for abuse-sensitive endpoints;
- security/privacy test suite;
- safe health/diagnostics and `SH-036 emitMetric` operational metrics;
- migration rollback verification;
- performance bounds for workers/queries;
- release checklist recording disabled decision-gated capabilities.

### Out of Scope

- new location product features;
- new source target families not approved;
- new privacy laws/retention bases;
- new provider families;
- refactoring neighboring Modules for style;
- bypassing unresolved decisions;
- converting Search/Audit/Ops into Location-owned infrastructure.

### Module-Owned Data

Review and harden:

- `FuzzyLocationCache`;
- `LocationReveal`;
- any explicitly approved version/constraint fields.

No generic ops, audit, or queue table is added.

### Public Interfaces

Freeze/document versioned production contracts for every enabled operation.

Disabled decision-gated operations must return explicit safe disabled/policy-not-configured behavior rather than partially working.

### Shared Operations Used

All relevant canonical operations, especially:

- `SH-044 executeIdempotentCommand` — duplicate command replay;
- `SH-045 deduplicateDomainEvent` — duplicate source-event replay;
- `SH-047 enqueueReliableJob` — durable work;
- canonical retry/backoff operation — transient dependency handling;
- `SH-055 runDeadlineExpiration` — fuzzy expiry scheduling;
- `SH-051 acquireAggregateLock` / `SH-052 withOptimisticConcurrency` — race control;
- `SH-091 requestSearchProjectionRefresh` and Search-owned reconciliation interface — downstream projection repair;
- `SH-037 recordIntegrationFailure`, service-health/incident correlation, telemetry sanitizer — Ops;
- `SH-029 appendAuditEvent` / `SH-030 recordSensitiveAccess` — Audit;
- shared crypto/key management — exact-location protection;
- root rate-limit primitive — abuse control.

No duplicate implementations are allowed.

### Domain Logic

#### Fuzzy projection hardening

- compare cache to authoritative source/policy version where modeled;
- remove or invalidate orphan targets through owner validation;
- prevent stale refresh rollback;
- batch expiry safely;
- preserve one current projection per target pair;
- never synthesize a projection from stale public/search data.

#### Reveal hardening

When enabled:

- refresh owner facts on every exact disclosure;
- serialize reveal versus revoke;
- detect source change during request;
- deny revoked/no-longer-eligible access;
- replay duplicate command without duplicate domain effect;
- prohibit client-side exact prefetch/cache outside approved protected response;
- key unavailable → deny;
- Audit unavailable → U-08-16 approved behavior;
- rate-limited/abusive requests return no exact data.

#### Privacy hardening

When enabled:

- duplicate Privacy instruction replays prior result;
- retention/anonymize/delete matrix is complete;
- fuzzy Search removal is reconciled;
- no executor failure is hidden as success;
- audit/Ops proof remains separate from Privacy disposition.

### Authorization / Compliance

Perform explicit review of:

- public versus protected endpoints;
- exact reveal authority;
- reveal history/admin access;
- service/system worker scope;
- Privacy executor authority;
- key management and rotation;
- provider secrets;
- rate limits;
- data minimization;
- telemetry/analytics redaction;
- irreversible Privacy actions;
- break-glass/admin behavior if any, which must be explicitly approved rather than inferred.

### Database / Transaction Behavior

- all Location lifecycle writes are transaction-safe;
- approved constraints/indexes are verified under real migration;
- no in-memory lock provides correctness;
- destructive migrations/backfills are staged, resumable, and have rollback/verification;
- no partial commit may return exact data after a failed required reveal transition/proof;
- worker scans use appropriate indexes and bounded batches;
- transaction boundaries do not extend into neighboring owner tables.

### Events / Jobs

Reconciliation jobs may include:

- fuzzy projection reconciliation;
- reveal re-evaluation;
- Privacy execution;
- Search repair request dispatch.

Dead-letter/manual-review tooling uses safe metadata and canonical queue mechanisms.

### Provider Integration

If geocoder is enabled:

- provider health/degradation tests;
- retry/circuit-break behavior according to root integration patterns;
- no provider output becomes source truth.

If exact reveal is enabled:

- key rotation/decrypt compatibility;
- key unavailable fails closed;
- secret access remains server-side.

### UI / Admin Surface

Production diagnostics may show:

- stale/orphan projection count;
- projection retry/dead-letter count;
- reveal reconciliation failures;
- provider health;
- Search/Audit/Ops integration status;
- Privacy executor status;
- decision-gated capability matrix;
- last safe correlation/request ID.

Exact location is not displayed by default in diagnostics.

### Failure Behavior

- Search unavailable → exact remains private; queue downstream repair;
- geocoder unavailable → no unsafe fallback;
- key unavailable → no exact reveal;
- Audit unavailable → approved U-08-16 behavior;
- source owner unavailable → deny exact and retry reconciliation;
- duplicate input → deterministic replay;
- concurrency conflict → safe retry/denial rather than last-writer leakage;
- migration/backfill anomaly → stop/rollback, preserve source/safe state;
- repeated terminal worker failure → shared dead-letter/manual review;
- Ops failure recording does not overwrite domain truth.

### Tests

Security:

- exact-location exfiltration attempts;
- authorization bypass;
- admin/support overreach;
- root rate-limit behavior;
- telemetry/analytics exact-location scanning;
- secret/key leakage;
- replay attacks;
- public map/Search payload inspection.

Concurrency/idempotency:

- duplicate web requests;
- duplicate source events;
- duplicate job delivery;
- refresh versus invalidation;
- stale refresh ordering;
- reveal versus revoke if enabled;
- source change during reveal if enabled;
- Privacy versus reveal/refresh if enabled.

Integration/reconciliation:

- Search outage/recovery;
- geocoder outage/recovery if enabled;
- Audit failure according to policy if reveal enabled;
- source-owner contract stale/unavailable;
- orphan target removal;
- cache backfill/rollback.

Privacy:

- Location executor retention matrix if enabled;
- Search removal;
- no hidden executor failure;
- retained result proof path to Privacy.

Performance:

- projection refresh batches;
- expiry scan/index behavior;
- reveal history query bounds;
- admin diagnostic bounds;
- provider-call timeout ceilings.

E2E:

- fuzzy public journey;
- exact reveal + revoke journey if enabled;
- Location Privacy disposition journey if enabled.

### Documentation Updates

- update Module/Cluster architecture decision status;
- update provider/library docs for approved geocoder/crypto configuration;
- record migration/backfill runbook;
- update progress tracker;
- record enabled/disabled production capability matrix and remaining risks.

### Acceptance Criteria

- every production-enabled path depends only on approved decisions;
- no exact location appears in public/telemetry surfaces;
- concurrency/idempotency prove one domain effect;
- stale source/gate state cannot silently reopen access;
- downstream owner failures are visible without corrupting Location truth;
- migration/backfill rollback is tested;
- disabled paths fail closed and are explicitly documented.

### Exit Gate

Location Safety production readiness passes only when:

- every enabled path has approved architecture decisions;
- repository-defined typecheck/lint commands pass;
- full Location unit/contract/integration/concurrency/security/privacy suites pass;
- critical fuzzy public E2E passes;
- exact reveal/revocation E2E passes if enabled;
- Privacy executor E2E passes if enabled;
- provider/reconciliation tests pass for enabled provider path;
- migration/backfill rollback verification passes;
- no prohibited duplicate implementation exists;
- progress tracker records all remaining disabled decision-gated capabilities and risks.

---

# Module Integration Phase

The primary Module integration proof is Feature 08, with integration behavior also exercised in Features 03, 05, 06, and 07.

The required boundaries are:

```text
source owner → Location Safety
Booking → Location Safety
Order → Location Safety
Location Safety → Search
Location Safety → Audit
Location Safety → Observability / Ops
Privacy / Data Erasure → Location Safety privacy executor
```

Integration tests must exercise public contracts rather than neighboring database tables.

Where exact reveal or Privacy disposition remains decision-gated, the integration test must verify explicit disabled/fail-closed behavior until policy is approved. No test should require Location Safety to import a neighboring repository to make the workflow pass.

### Required integration proof

- one approved source target supplies protected source-location facts to Location Safety;
- Location Safety produces fuzzy truth and Search receives only the safe projection;
- source invalidation removes/invalidates Location truth and requests Search removal;
- Booking/Order facts are consumed through owner APIs;
- exact reveal decision is integrated only if approved;
- Audit receives separate generic/sensitive-access proof;
- Privacy calls Location through the standard executor contract when that path is approved;
- request/correlation identity survives the cross-Module workflow.

---

# Module Hardening Phase

Feature 10 is the binding Module hardening feature.

Hardening must cover only relevant Location Safety risks:

- fuzzy refresh/invalidate races;
- reveal/revoke races;
- idempotent replay;
- stale source and gate facts;
- source version changes during actions;
- geocoder/provider outage;
- Search outage/reconciliation;
- Audit criticality;
- key rotation/unavailability;
- sensitive access;
- Privacy retention/disposition;
- telemetry/analytics redaction;
- migration/backfill safety;
- bounded worker/query performance.

A generic statement that "all tests passed" is insufficient. The completion report must identify which decision-gated paths were enabled, which remained disabled, and which exact safety/retention/provider decisions governed the enabled paths.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --------- | -------- | ------------ |
| Phase 1 | Contracts and Public Projection Foundation | 01 Contract and Repository Foundation; 02 Fuzzy Public Location Vertical Slice; 03 Projection Invalidation, Search Request, and Expiry Worker |
| Phase 2 | Exact Reveal Contract and Lifecycle | 04 Reveal Status, History, and Decision Contract Foundation; 05 Exact Location Reveal and Viewer-Specific Lifecycle; 06 Revocation and Gate-Change Reconciliation |
| Phase 3 | Privacy and Long-Lived Location Data | 07 Location Safety Privacy Executor |
| Phase 4 | Module Integration | 08 Booking, Order, Source, Search, Audit, and Ops Contract Integration |
| Phase 5 | Provider and Production Policy Activation | 09 Geocoding Adapter and Production Fuzzy Policy Activation |
| Phase 6 | Module Hardening and Production Verification | 10 Security, Concurrency, Reconciliation, Privacy, and Production Hardening |

**Total numbered features: 10**

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read `context/context-map.md` and `context/project-overview-v3.md`; root architecture/code standards are currently missing.
2. Read the Canonical Shared Operations Registry.
3. Read CL-08 architecture and build plan.
4. Read `context/clusters/Privacy & Location Safety/Location Safety Module/location-safety-module-architecture.md`.
5. Read this implementation plan.
6. Read public-interface sections for every direct dependency used by the feature.
7. Confirm the prior feature exit gate.
8. Check every U-08 decision dependency listed for the feature.
9. If a required decision is unresolved, stop the feature and record the blocker rather than inventing policy.
10. Write the concise Feature Implementation Specification.
11. Implement only the numbered feature.
12. Run repository-defined typecheck, lint, targeted tests, migration/build checks, and applicable E2E checks.
13. Perform contract/workflow verification.
14. Review cross-Module ownership and prohibited-duplicate boundaries.
15. Verify exact-location redaction across responses, logs, analytics, events, jobs, Search, and diagnostics.
16. Update the progress tracker.
17. Update architecture first if a binding decision legitimately changed.
18. Record assumptions, known failures, remaining risks, deferred work, and enabled/disabled decision-gated paths.
19. Start the next feature only after the exit gate passes, except where the CL-08 build plan explicitly permits an independent path around a blocked decision-gated feature.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise implementation specification containing:

- Objective
- Observable result
- Cluster Build-Plan Link
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

Do not generate every Feature Implementation Specification in advance. The numbered feature definition in this plan is binding planning context; the pre-coding specification must reflect the actual repository/dependency state at implementation time.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

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
- Decision gates encountered
- Enabled/disabled capability status
- Exit-gate result

The completion report must also explicitly state:

- whether any direct cross-Module database access was introduced;
- whether any local duplicate of a canonical shared mechanism was introduced;
- whether any exact-location value appeared in logs, analytics, Search, events, notification payloads, job diagnostics, or public responses.

The expected result for all three is **no**.

---

# Final Quality Check

Before declaring this Module plan complete or a production slice ready, verify:

1. `FuzzyLocationCache` has exactly one owner: Location Safety.
2. `LocationReveal` has exactly one owner: Location Safety.
3. Exact/source location records remain source-Module truth unless a later approved architecture explicitly transfers a particular record.
4. Booking and Order truth were not absorbed into this Module.
5. Booking duplicate location fields were not silently promoted to Location truth.
6. Search remains downstream projection and performs no coordinate fuzzing.
7. `AccessAuditLog` and `AuditEvent` remain Audit-owned and separate from Location domain proof.
8. Privacy orchestration and `DataRetentionExemption` remain Privacy-owned.
9. Media EXIF/GPS/file mechanics remain Media-owned.
10. Every shared operation is consumed rather than duplicated.
11. Cross-Module reads use public owner interfaces.
12. Provider adapters never become business truth.
13. Exact location never enters public Search, ordinary telemetry, analytics, ordinary events, notification payloads, or public map data.
14. Exact reveal, if enabled, is freshly gated server-side.
15. Concurrency and idempotency use database/shared primitives rather than in-memory correctness mechanisms.
16. Decision-gated safety, retention, context, uniqueness, or provider rules were not invented.
17. Every numbered feature has automated tests and an explicit exit gate.
18. Module features align with CL-08 Features 03, 07, 08, 09, 10, and 11 without changing Cluster sequencing.
19. Disabled decision-gated paths are explicit in configuration/progress, not hidden in incomplete behavior.
20. A coding agent can execute every enabled feature without inventing architecture.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R017 — Owner facts and decision contracts

**Applied architecture ruling (AI_RESOLVED), 2026-09-30.** The [WA-R017 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r017--owner-facts-and-decision-contracts) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

SH-003 is a family of small owner-specific queries, not a mandatory universal DTO. Each query takes authenticated caller/purpose and a typed owner resource reference, exposes only required authorized facts with an owner-issued source token, and distinguishes unavailable/stale from absence or denial. Consumers do not load foreign Prisma records. SH-015 remains a reusable result pattern, not a universal domain enum: carry a decision category, stable owner reason code, evidence/source token and evaluation time; payload variants remain owner-specific. Domain outcomes such as Job Compliance warning/review_required and Healthcare redacted/blocked retain their distinct meaning. An unavailable prerequisite never becomes allow. Exact wire names/runtime schemas are DEFERRED_IMPLEMENTATION_DETAIL inside these constraints and must be fixed in producer/consumer fixtures before parallel integration.

Adopt this interpretation for all references that formerly treated SH-003/015 proposal status as an unconditional blocker on owner-specific interfaces. Neither SH status is promoted. New generic repositories, universal authorization or generic business-policy dispatch are forbidden. Grouped owner-specific contracts do not become interchangeable because their envelopes look similar.


## WA-R020 — Privacy executor identity and truthful completion

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R020 contract](../../../reconciliation/platform-architecture-rulings.md#wa-r020--privacy-executor-identity-and-truthful-completion) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

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

## WA-R057 — Privacy owner inventory and private export handoff

Implement the corresponding owner architecture contract before consumers. First align the forward schema/constraints and immutable evidence representation under the database integration owner; then implement owner commands/queries and shared execution adapters; then qualify consumer fixtures. Historical decision gates covered by this ruling are resolved at architecture level only.

Each owner implements WA-R020 versioned enumerateSubjectData/evaluateRetentionRequirement/executePrivacyInstruction descriptors. Inventory is explicit, paginated with completion evidence and stable target/version identity; no generic other target or assumed database cascade can count as coverage. Messaging covers Thread, participant current state/history, Message/revisions/restrictions and MessageMedia joins. Notification covers Notification/interaction evidence, NotificationSubscription/credential generations, Delivery attempts and SubscriptionEvent. Location covers FuzzyLocationCache, reveal/revocation evidence and its provider references; exact source facts remain inventoried by their source owner. Restricted proof is accounted even when excluded from requester disclosure. Owner field/action matrices must identify erase, minimize, retain, export or restrict disposition with policy basis and executor receipts before destructive activation.

Privacy owns an immutable export manifest: subject/request/job/generation, owner contribution IDs and versions, authorized field scope, safely stated exclusions with disposition evidence, assembly completion, byte hash/algorithm, creation time and actor/correlation. Exact Location subject data may be included only under approved access policy after removing other parties' data; encryption keys, provider credentials and access tokens are never export content. Record opaque key-version/storage evidence where required, never keys. A complete manifest describes actual serialized bytes, not promised future contributions.

Use Media's WA-R050 createMediaUploadSession→bounded upload→completeMediaUpload→getMediaUploadStatus/getMediaReadiness protocol, with Privacy job/bundle revision as semantic key and purpose-bound private artifact authorization. Same key and bytes replay; changed bytes require a new revision or conflict. Upload acknowledgment never means ready. Require exact immutable ready Media version, matching hash/size and completed manifest before bundle ready. Bind through an explicit Privacy-owned MediaAsset/version reference, not polymorphic ownership. Failed scan/partial assembly keeps download unavailable. Terminal upload retry uses a linked Media attempt per WA-R050 while preserving bundle-generation lineage.

At download, Privacy rechecks requester/action/scope and current generation; Media rechecks asset safety/revocation and issues bounded access through SH-127. Commit required access evidence before protected disclosure. Superseded/expired/revoked generations cannot receive fresh access even if cleanup worker is late. Retain prior manifest/status evidence under approved retention while deleting bytes through Media's executor when authorized. No stored public URL, direct storage SDK or convenience export endpoint may bypass owner gates. Audit exports use the same Media mechanism but an Audit-owned manifest; this ruling does not transfer Audit export ownership.

Legal retention/exemption duration, backup-expiry representation and final retained shell require approved external policy. Location's geocoder/account/region/purpose and key lifecycle qualification remain external activation gates; consumers cannot choose their own geocoder or crypto. Verify omitted child inventory, partial serializer, hash mismatch, scan failure, changed-byte retry, stale generation access, retained shared Media references and provider-deletion uncertainty. Concrete schema, executor field matrices and bilateral fixtures remain implementation qualification, not unresolved architecture permission.

Record actual fixture, replay, concurrency and access evidence before interface freeze. Legal/provider activation gates remain scoped; no runtime completion is claimed by this plan.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Register the closed source/purpose catalog and implement version-bound fresh owner queries before reveal/project surfaces. Test mismatched Order/Booking, stale/replayed allow after revocation, missing policy/facts, support scope, participant changes, Candidate opt-out, public/notification exact-data absence and proof failure before response. Qualify fuzzy numerical policy, approved retention/disposition, geocoder and key lifecycle separately. A declared contract is not runtime/provider qualification.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `location_safety` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`resolveLocationReveal / revokeLocationReveal`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.

## WA-R077 — Bilateral qualification sequence

Public/fuzzy/reveal projections are not checkout tax evidence; no universal tax-location authority is added. Follow the owner architecture and WA-R077 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.

## WA-R080 — Bilateral qualification sequence

Consume taxonomy.policy_changed.v1 only for registered purpose-specific requirement mappings; a term change is not disclosure permission. Follow the owner architecture and WA-R080 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.

## WA-R081–083 — Bridge qualification sequence

Implement only the owner architecture's reviewed bridge obligations (BF-010, BF-026, BF-027, BF-030, BF-033, BF-042, BF-043, BF-048, BF-063, BF-065, BF-066, BF-071, BF-093, BF-102, BF-120, BF-129, BF-131, BF-148, BF-160, BF-162, BF-163, BF-164, BF-171, BF-188, BF-203, BF-204, BF-205, BF-210, BF-211, BF-214, BF-218, BF-221, BF-222, BF-223, BF-225, BF-229, BF-230, BF-231, BF-232, BF-234, BF-235, BF-236, BF-237, BF-249, BF-256, BF-257, BF-266). Load `context/reconciliation/bridge-contract-bindings.md` and the final inventory for current versions and disabled facets. First bind closed schemas and current source/actor/purpose fixtures; then qualify shared persistence/outbox/idempotency/receipt mechanisms; then connect producer and consumer. Required denial, stale/replay/conflicting-key, late-result and sensitive-field negative fixtures precede interface freeze. Provider/legal/database evidence gates only the affected activation. No full-Cluster dependency or parallel lane is implied, and no optional path is enabled by a fake or a passing structural checker. Preserve historical snapshots and P01–P19; do not implement schema/provider/product slices during readiness.


## WA-R085–087 — Platform qualification dependencies

Follow this owner's platform-convergence architecture and the platform lifecycle/action matrix. Current lifecycle scope: Source-bound fuzzy projection; exact reveal/grant/revoke; separate Interview meeting-location purpose.

Qualify source-fact leaves and exact required owner ports against fixtures before composed decisions, then local persistence/receipts and actual adapters. A contract dependency is not a requirement that the whole upstream Module/Cluster be mature. Production activation still requires every actual port and action-specific external requirement. Do not wait for downstream Search/Notification/telemetry to commit source truth or to bootstrap shared primitives.

Negative qualification must cover the relevant cycles in platform-dependency-graph.json, stale/revoked source facts, changed fingerprints, unknown external outcomes, projection-as-authority, recursive fact/access calls and actual mandatory proof failures. No schema migration, provider activation, DTO freeze, root build plan or parallel lane approval follows from static review. Preserve Privacy per-owner field/action/serializer coverage as a separate gate.
