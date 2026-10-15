# Search / Public Visibility Implementation Plan

> **Module ID:** `search_public_visibility`  
> **Canonical module name:** Search / Public Visibility Module  
> **Primary Cluster:** `CL-02 — Discovery, Classification & Visibility`  
> **Plan status:** implementation-grade Module plan subordinate to root/Cluster sequencing  
> **Primary Cluster build-plan link:** CL-02 Features 02–03 — Search contract harness, provider, and taxonomy discovery\
> **Later linked Cluster features:** 09 public source integration; 10 protected Candidate Search; 11 enforcement prerequisites/reaction integration; 12–13 reconciliation and hardening

This plan implements the Module architecture without changing ownership or Cluster order. It does not authorize application code outside the numbered feature being executed.

The current CL-02 architecture and build plan are linked above; use their coordination and sequence under context-map.md.

Current coordination: [Cluster architecture](<../discovery-classification-architecture.md>) and [Cluster build plan](<../discovery-classification-build-plan.md>). Locate supporting artifacts through [context-map.md](<../../../context-map.md>); authority follows concern, not location or age. Root architecture/build-plan files are currently unavailable and do not supply enforceable phases.

---

## Core Principle

Implement Search / Public Visibility through narrow, verifiable slices:

```text
public/observable behavior
→ validated Search command/query
→ Search-owned projection policy
→ Search-owned work/read
→ owner public-interface calls
→ canonical shared-operation calls
→ Typesense adapter effect
→ audit/ops/privacy/moderation result where applicable
→ tests
→ exit gate
```

Search has very little user-owned business state. Its observable results are primarily:

- a durable projection work request;
- a provider document created/removed;
- a public/protected query result;
- a privacy/moderation enforcement acknowledgment;
- a reconciliation/backfill report;
- a Search-specific debug view.

Do not invent UI merely to satisfy a vertical-slice pattern. The only UI justified by current evidence is a narrow admin/debug viewer attached to the existing admin shell.

---

## Build Rules

1. Follow root Workin Ants architecture, code standards, shared-operation registry, Cluster sequencing, and this Module architecture.
2. Search owns only `SearchUpsertEvent`, `SearchEntityType`, provider projection/query behavior, Search work lifecycle, provider adapter, and Search-specific reconciliation/debug behavior.
3. Source business entities remain authoritative in their owning Modules.
4. Cross-Module reads use public interfaces/owner projection contracts; do not import neighboring repositories as an indexing shortcut.
5. Use **SH-091** as the only canonical source-facing refresh command.
6. Use **SH-092** as the only Typesense provider boundary.
7. Use **SH-094** for owner-produced, privacy-safe source projections and **SH-024** for owner-issued public/protected readiness.
8. Reuse SH-044/047/048/051/052 for idempotency, queueing, retry, and concurrency. Do not build local infrastructure equivalents.
9. Every mutation/query boundary uses runtime validation. TypeScript types alone do not validate caller input.
10. External/provider effects are idempotent and normalized behind the adapter.
11. A provider failure never changes source business lifecycle status.
12. Eligibility is decided before ranking. Boost/trust signals cannot make forbidden content searchable.
13. Exact private location and raw resumes/application documents are prohibited from Search documents.
14. Candidate search is a protected later feature and must not be pulled into the initial public-search slice.
15. Privacy orchestration remains Privacy-owned; Moderation decision lifecycle remains Moderation-owned.
16. `SearchUpsertEvent` work truth remains distinct from AuditEvent, IntegrationFailure, QueueJob, and provider documents.
17. Every numbered feature ends with exact tests and an exit gate; the next feature must not begin on a failed gate unless the plan is explicitly revised.
18. Unresolved architecture is surfaced and recorded; the coding agent must not silently choose a provider topology, ranking algorithm, retention rule, or protected-search entitlement model.

---

## Preconditions

### Hard platform dependencies

The following must exist before production activation of the initial Search slice:

- Prisma/Postgres foundation and migration discipline;
- shared request/correlation context;
- canonical idempotency infrastructure;
- reliable queue/worker mechanism with retry/dead-letter visibility;
- Observability/Ops logging, metrics, IntegrationFailure, queue telemetry, and health integration;
- Identity/Role operations for admin/protected endpoints;
- Typesense environment/credential management in the deployment platform;
- runtime-validation standard used by Workin Ants.

### Hard Search architecture dependency

Before Feature 04/05 production implementation, the separate PR-SPV-01 physical representation must be approved and implemented. CL02-R008 already requires durable Search-owned SH-091 identity/context, source version/currentness, idempotency, requester, action, claimability, completion, retry/operator failure, and stale/superseded outcomes; the current Boolean is insufficient. Generic queues own transport/retry mechanics only.

Feature 01 exists specifically to settle and implement that schema alignment.

### Source interfaces that may initially be faked

Search may build against contract fakes until source Modules expose the required public contracts. Fakes may stand in for:

- Marketplace Supply `buildSourceProjection` / public readiness;
- Gig / Demand projection/readiness;
- Organization Hiring Job/Organization projection/readiness;
- Professional Eligibility readiness;
- Trust display signal;
- Location Safety fuzzy location;
- Track entitlement;
- Candidate-owned `CandidateSearchProjection` interface;
- Privacy target executor request;
- Moderation enforcement request;
- ComplianceHold decision.

A fake does not make Search the temporary owner of the missing source truth.

### Phase sequencing constraints

- Basic Search work/provider/public query maps to CL-02 Features 02–03.
- Production integration with a source entity occurs only once that source Module exposes its approved public interface.
- Protected Candidate Search waits for Candidate/Organization interfaces and CL-02 Feature 10 prerequisites.
- Formal Privacy/Moderation reaction integration maps to CL-02 Feature 11; prerequisite enforcement contracts/tests precede protected Candidate Search.
- Full outage/reconciliation/performance/security verification maps to CL-02 Features 12–13.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Projection Work Contract and Schema Alignment

### Objective

Make `SearchUpsertEvent` capable of representing the confirmed canonical Search refresh contract without absorbing generic queue/retry infrastructure.

### Observable Result

A validated `requestSearchProjectionRefresh` contract can be represented durably and idempotently in the database, including the requested intent, source version, requester Module, and semantic command identity. The repository can distinguish pending/completed/terminally failed/superseded Search work without using provider state as truth.

### Cluster Build-Plan Link

CL-02 Feature 02 contract harness and production persistence prerequisite. CL02-R008 semantics are approved; physical representation requires a separate database decision.

### Dependencies

- current Prisma schema/migration foundation;
- Canonical Shared Operations Registry, especially SH-091 and SH-044;
- Module architecture PR-SPV-01;
- shared queue model boundaries so generic lease/retry fields are not copied into Search.

### In Scope

- inspect current `SearchUpsertEvent` migration history and usage;
- obtain separate approval for expanding SearchUpsertEvent or another Search-owned representation and its migration; no physical choice is approved by CL02-R008;
- implement only the separately approved representation of CL02-R008 durable Search-work requirements;
- add `SearchProjectionIntent` / work-status/outcome enums only if approved by the feature specification;
- add unique/idempotency indexes and worker-read indexes;
- preserve existing rows through a deterministic migration/backfill strategy;
- define public command/result TypeScript/Zod contracts;
- define `SearchEntityType` surface support registry, with `user` disabled by default;
- repository methods only for Search-owned work rows.

Illustrative field names from the Module proposal, not an approved schema:

```text
intent
sourceVersion
requesterModule
idempotencyKey
workStatus
projectionVersion?
outcome?
```

Generic `attemptCount`, lease, heartbeat, `nextAttemptAt`, dead-letter state, and generic failure payloads remain shared queue/Ops truth unless the canonical queue implementation explicitly requires a Search reference.

### Out of Scope

- Typesense SDK/client;
- source Module projections;
- public search query;
- candidate search;
- ranking weights;
- queue runner implementation;
- Privacy/Moderation workflow ownership;
- adding/removing `SearchEntityType.user` without explicit architecture ruling.

### Module-Owned Data

- `SearchUpsertEvent`;
- `SearchEntityType` support registry;
- approved Search work intent/status/outcome enum(s), if architecture accepts them.

### Public Interfaces

Define contract shape for:

- SH-091 `requestSearchProjectionRefresh` request/accepted/replayed/conflict result;
- internal `SearchProjectionWork` repository DTO.

Do not make the command callable from a browser in this feature.

### Shared Operations Used

#### SH-044 — `executeIdempotentCommand`

- **Owner:** platform application infrastructure.
- **Invocation:** wraps creation of a Search refresh request.
- **Local policy:** Search defines semantic fingerprint from entity type/ID, intent, source version, requester, and reason/reference.
- **Prohibited duplicate:** `searchIdempotencyService`, local idempotency table.

#### SH-032 — `createRequestContext`

- **Owner:** Observability/platform.
- **Invocation:** persisted correlation/request references where allowed.
- **Local policy:** Search stores only safe identifiers.
- **Prohibited duplicate:** Search-specific correlation middleware.

### Domain Logic

- `entityType` must be a supported `SearchEntityType` for the requested surface.
- `user` is rejected until explicitly enabled.
- a refresh request must include an owner-issued `sourceVersion` even if the worker later discovers a newer version;
- same idempotency key + same fingerprint replays the original accepted result;
- same key + different fingerprint returns conflict;
- Search work status describes Search projection work only;
- work lifecycle must not duplicate queue attempt mechanics.

### Authorization / Compliance

This feature defines an internal contract only. The public command later accepts trusted Module/system context or already-authorized admin workflow context. No end-user permission model is introduced here.

### Database / Transaction Behavior

- command claim/idempotency record and `SearchUpsertEvent` insertion must be atomic under the canonical SH-044 mechanism;
- add a unique constraint/index sufficient to enforce idempotency at the database level;
- add indexes for pending work ordered by creation time and for `entityType/entityId/sourceVersion` lookup;
- existing `processed` rows migrate only under the separately approved, evidence-backed mapping; neither Boolean value alone approves an exact target state, currentness, or outcome;
- do not fabricate historical intent/sourceVersion values without a documented sentinel/backfill strategy;
- validate migration from clean and realistic existing data.

### Events / Jobs

No worker runs yet. No new Search domain event is emitted. Queue payload schema may be defined but not dispatched until Feature 04.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- migration ambiguity → stop and record unresolved migration rule, do not guess;
- idempotency conflict → stable conflict result;
- unsupported `user` entity request → stable validation/surface error;
- database failure → no accepted Search work acknowledgment.

### Tests

- Prisma migration from clean database;
- migration fixture from current `processed=false/true` rows;
- unique idempotency constraint;
- supported/unsupported entity type validation;
- `user` fail-closed test;
- same-key/same-payload replay test;
- same-key/different-payload conflict test;
- work status transition unit tests;
- check that no retry/lease table was added locally.

### Documentation Updates

- record the separately approved physical design and reconcile the illustrative PR-SPV-01 fields/statuses; no implementation convenience approves a proposal;
- update shared-operation registry only if SH-091 itself changes, not for normal implementation detail;
- record migration/ruling in progress tracker/ADR if the repo uses ADRs.

### Acceptance Criteria

- current Search work rows can migrate safely;
- a canonical SH-091 request can be persisted without missing required semantic fields;
- Search work and generic QueueJob truth remain separate;
- database enforces semantic idempotency;
- `SearchEntityType.user` remains non-indexable;
- no Typesense or source-domain code exists yet.

### Exit Gate

Run the repository's canonical:

```text
prisma/schema validation
clean-database migration test
existing-data migration fixture test
typecheck
lint/format check
Search Feature 01 unit/integration tests
```

Proceed only when the migration is reversible according to project migration policy, all tests pass, and PR-SPV-01 is recorded as settled.

---

## 02 Source Projection and Public-Readiness Contract Registry

### Objective

Define the one safe boundary through which Search obtains indexable source data and owner-issued discovery readiness without importing foreign repositories.

### Observable Result

Search can ask a fake source owner for a deterministic, versioned, allowlisted projection plus SH-024 readiness and can reject stale, malformed, or surface-incompatible responses.

### Cluster Build-Plan Link

CL-02 Features 02–03 — source-safe projection/readiness contracts; later owners integrate as their public contracts become available.

### Dependencies

- Feature 01 contracts/entity support registry;
- SH-094 `buildSourceProjection`;
- SH-024 `evaluatePublicReadiness`;
- SH-015 decision-result contract if/when approved;
- source Module Architecture/public-interface evidence.

### In Scope

- define `SourceProjectionPort` keyed by `SearchEntityType`;
- define a versioned envelope containing source entity ID, source version, projection schema version, surface, and allowlisted payload;
- define readiness dependency contract using SH-024;
- define source-owner adapter registry without making a universal DB repository;
- define separate candidate projection adapter that accepts Candidate-owned `CandidateSearchProjection` data only;
- define source-not-found/stale/denied results;
- add contract fakes for Offering, Gig, Job, Organization, Professional, Taxonomy, TrustBadge, Candidate;
- assert exact-location/raw-resume prohibited fields at the contract boundary.

### Out of Scope

- real source Module database access;
- provider documents;
- ranking;
- Typesense;
- public query;
- AI taxonomy suggestions;
- direct compliance joins.

### Module-Owned Data

No new durable Search model. Contracts/types only.

### Public Interfaces

Search **consumes**, not owns:

- SH-094 `buildSourceProjection`;
- SH-024 `evaluatePublicReadiness`;
- SH-003 `queryOwnerFacts` only for later protected authorization when needed.

Search introduces no competing `getOfferingForSearch`, `getJobForSearch`, or raw Prisma interface.

### Shared Operations Used

#### SH-094 — `buildSourceProjection`

- **Owner:** each source Module.
- **Invocation:** before Search document build/backfill/reconciliation.
- **Local policy:** Search validates envelope/version/surface; source owner chooses fields.
- **Prohibited duplicate:** Search-specific foreign repository/projection builder.

#### SH-024 — `evaluatePublicReadiness`

- **Owner:** source/compliance owner; Search composes.
- **Invocation:** before any provider upsert.
- **Local policy:** map owner allow/deny to Search projection action.
- **Prohibited duplicate:** `searchProfessionalReadiness`, `searchJobCompliance`, universal `isSearchable` business rule.

#### SH-015 — `returnDecisionResult` (Proposed Ruling)

- use only as the response envelope if root/shared architecture has approved it by implementation time;
- never centralize the owner's policy.

### Domain Logic

Every source projection must be:

- deterministic for a given source version;
- explicit about intended search surface;
- field-allowlisted;
- independent of provider syntax;
- able to rebuild without historical Search state;
- accompanied by owner readiness or a reference to it;
- safe against exact-location and sensitive-document leakage.

Candidate rules:

- only Candidate-owned projection DTOs are accepted;
- inactive/hidden/erased/disabled projection → deny provider projection;
- raw resume text is not part of the contract even if a source table physically contains it.

### Authorization / Compliance

No end-user query yet. Contract tests must demonstrate Search cannot bypass source owner privacy/readiness merely by choosing another adapter.

### Database / Transaction Behavior

No Search DB mutation. Source versions are treated as opaque owner values and compared using the approved currentness semantics.

### Events / Jobs

None.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- source not found → worker later maps to remove/no-op;
- owner readiness denied → remove/exclude;
- projection malformed or contains forbidden field → terminal mapping error, no provider write;
- dependency unavailable → retryable worker failure later;
- incompatible source/projection version → explicit stale/version error.

### Tests

- contract test for each fake entity adapter;
- forbidden exact-address/private-coordinate field fixture;
- forbidden raw-resume/application field fixture;
- owner-denied decision cannot be overridden by Search ranking input;
- source projection version stability test;
- candidate statuses map to protected eligibility correctly;
- Search codebase contains no import of fake source Prisma repositories.

### Documentation Updates

Record the exact source-projection envelope and version semantics. If any source owner lacks an interface, mark the dependency as a required stub rather than inventing ownership.

### Acceptance Criteria

- one adapter registry covers supported entity types without a cross-domain repository;
- source owner controls fields and readiness;
- Search can deterministically accept/reject the envelope;
- candidate/raw-resume and exact-location violations fail tests;
- no provider code exists yet.

### Exit Gate

Pass all source contract/unit tests, typecheck, lint, and architecture import-boundary checks. Proceed only when real source Modules could replace fakes without changing Search domain logic.

---

## 03 Typesense Provider Port and Collection Registry

### Objective

Establish one Search-owned, provider-neutral boundary for collection schemas, document writes/deletes, queries, and health without leaking Typesense details into application/source code.

### Observable Result

Application tests can swap a fake Search provider for a Typesense adapter. A development/provider test can ensure a collection schema, upsert a safe document, query it, delete it, and report health using normalized results.

### Cluster Build-Plan Link

CL-02 Feature 03 — SH-092 provider adapter. The Module provider gate precedes the production worker; CP Feature 02 uses a fake writer.

### Dependencies

- Features 01–02;
- Typesense environment credentials/configuration;
- SH-092;
- SH-034 telemetry sanitization;
- SH-037 operational failure contract;
- root secret/config standards.

### In Scope

- `SearchProvider` port;
- Typesense adapter/client construction;
- collection registry abstraction;
- provider document schema version metadata;
- normalized upsert/delete/batch/query/fetch-metadata/health operations;
- provider error translation;
- fake in-memory provider for application tests;
- initial public-surface collection descriptors sufficient for Feature 06;
- protected-candidate collection descriptor may be declared disabled/reserved, not activated;
- provider schema compatibility check.

### Out of Scope

- source projection worker;
- ranking weights beyond fields needed by the minimal schema;
- candidate search activation;
- public browser API keys unless separately ruled;
- provider webhooks;
- reconciliation worker implementation;
- source Module Typesense clients.

### Module-Owned Data

No new Prisma truth. Search owns code/config for:

- collection registry keys;
- document schema versions;
- provider document identity convention.

### Public Interfaces

Implements **SH-092 `writeSearchProjection`** internally. No source Module can access the raw provider port.

### Shared Operations Used

- **SH-061 `translateProviderStatus`** — existing Search adapter status/error mapping; provider-owning adapter retains mapping/version and normalized failure policy.

#### SH-092 — `writeSearchProjection`

- **Owner:** Search.
- **Invocation:** worker/query services only.
- **Local policy:** collection schema, version, ranking/facets/document identity.
- **Prohibited duplicate:** per-entity Typesense clients.

#### SH-034 / SH-037 / SH-039

- sanitize provider diagnostics;
- record integration failure;
- expose safe health check.

No SH-059/060 webhook operations are used because Search has no confirmed provider callback flow.

### Domain Logic

- provider collection names never appear in external Search contracts;
- document IDs are stable/deterministic from Search entity identity/surface;
- every document carries enough Search-owned schema/source-version metadata for stale/reconcile decisions without exposing internal sensitive facts;
- delete missing document is normalized as successful no-op;
- unsupported schema version is a manual/terminal configuration problem, not a source eligibility problem.

### Authorization / Compliance

- provider credentials server-side only;
- protected collection is inaccessible through public query mode;
- public collection schemas exclude exact location/raw private content by construction.

### Database / Transaction Behavior

None beyond existing Search work. Provider state is external and nontransactional.

### Events / Jobs

None yet.

### Provider Integration

Implement Typesense adapter behind the port. Provider-specific exceptions are translated into Search errors. Do not persist raw provider responses as source truth.

### UI / Admin Surface

None.

### Failure Behavior

- configuration/auth error → normalized terminal/manual intervention;
- timeout/network error → normalized retryable;
- invalid document schema → permanent until mapper/schema corrected;
- collection missing/version mismatch → explicit provider-schema error;
- delete not found → success/no-op.

### Tests

- fake provider contract suite;
- Typesense adapter contract suite where environment is available;
- credential-not-exposed test/build assertion;
- schema compatibility test;
- safe error translation/redaction test;
- public/protected registry isolation test;
- no raw Typesense type leaks in application/public contract compilation.

### Documentation Updates

Record the selected collection topology only if architecture settles it during this feature. If still unresolved, implement the registry abstraction with the minimal approved physical layout and record the decision before proceeding to production.

### Acceptance Criteria

- one provider port serves all Search entity types/surfaces;
- a fake and Typesense adapter pass the same core contract tests;
- application code has no direct Typesense SDK dependency;
- public/protected collection isolation is testable;
- health/error outputs are normalized and sanitized.

### Exit Gate

Pass provider contract tests, typecheck/lint/build, secret-scan/config validation, and a development Typesense smoke test if credentials are available. No projection worker begins until this gate passes.

---

# Phase 2 — Core Projection and Public Discovery

## 04 Canonical Refresh Command and Durable Dispatch

### Objective

Implement SH-091 end-to-end: a trusted source/enforcement caller can request projection work exactly once and Search durably dispatches that work to the shared queue.

### Observable Result

Calling `requestSearchProjectionRefresh` with a valid entity, intent, source version, requester, and idempotency key creates/replays one Search work record and one durable queued projection task.

### Cluster Build-Plan Link

CL-02 Feature 02 — SH-091 command/queue contract harness; production use also requires the approved persistence/provider gates.

### Dependencies

- Feature 01 schema/contract;
- Feature 02 entity/source registry;
- SH-044 idempotency;
- SH-047 queue;
- SH-032/038 request and queue telemetry;
- shared service/system caller context.

### In Scope

- SH-091 application service;
- runtime validation;
- requester Module allowlist/system context;
- transaction-safe Search work creation;
- reliable job dispatch through shared queue;
- replay/idempotency behavior;
- safe correlation IDs;
- thin internal/admin adapter if needed for tests.

### Out of Scope

- actual Typesense write;
- source projection loading;
- public search API;
- source Module event subscriptions;
- candidate search;
- independent queue runner.

### Module-Owned Data

`SearchUpsertEvent` work row/status.

### Public Interfaces

**Introduced/activated:** SH-091 `requestSearchProjectionRefresh`.

Request must not expose database model internals; response includes accepted/replayed work ID, normalized status, and safe correlation reference.

### Shared Operations Used

- **SH-044** idempotent command;
- **SH-047** reliable job;
- **SH-032** request context;
- **SH-038** queue telemetry;
- **SH-033** structured logging.

### Domain Logic

- source caller provides intent but the worker will still re-evaluate current readiness;
- a requested `restore` cannot force an upsert if owner readiness is now denied;
- `hide/remove` should result in a removal attempt even if source projection is unavailable, provided provider document identity is deterministic;
- `update/index` with missing source will eventually remove/no-op rather than preserve stale data indefinitely;
- `user` is rejected;
- one request path serves all supported source Modules—no entity-specific queues.

### Authorization / Compliance

This is an internal Module interface. Browser identity is not accepted as `requesterModule`. If an admin action triggers it, the admin command authenticates/authorizes first and calls SH-091 with an approved system/request context.

### Database / Transaction Behavior

- insert Search work under SH-044 semantic claim;
- durable job dispatch uses the shared queue's approved transactional/outbox behavior;
- no acknowledgment if work cannot be durably persisted/queued under the canonical mechanism;
- no source-domain write occurs.

### Events / Jobs

Enqueue `search.projection.process` (or repository-approved queue name) carrying only Search work ID and correlation context. Payload must not include full source records.

### Provider Integration

None in command path.

### UI / Admin Surface

Optional internal test harness only; no product UI.

### Failure Behavior

- invalid input → validation error, no work;
- untrusted requester → forbidden/internal-auth failure;
- idempotency conflict → conflict;
- queue unavailable → follow shared reliable-dispatch semantics; do not leave falsely accepted unqueued work;
- DB unavailable → no work acknowledgment.

### Tests

- SH-091 contract tests;
- trusted/untrusted requester tests;
- idempotent replay/conflict tests;
- queue dispatch exactly-once semantic test;
- no source data in queue payload test;
- `user` rejected;
- multiple entity types share same command path;
- transaction failure leaves no inconsistent accepted state.

### Documentation Updates

Update the public-interface reference and progress tracker. No architecture change unless dispatch semantics require a binding revision.

### Acceptance Criteria

- source Modules have exactly one canonical refresh command;
- one call yields one semantic Search work item despite retries;
- Search work can be found by entity/source version/idempotency;
- shared queue is used;
- no Typesense call occurs synchronously.

### Exit Gate

Pass SH-091 contract/integration tests, queue fake/integration tests, typecheck/lint/build, and manual inspection proving no parallel `enqueueSearch*` service was created.

---

## 05 Projection Worker and Visibility Composition

### Objective

Turn one Search work item into the correct provider effect by loading owner-approved projection/readiness, composing Search-surface policy, and idempotently upserting/removing through SH-092.

### Observable Result

For a fake source owner and fake/real Search provider:

- eligible public source → document exists;
- source denied/nonpublic/missing → document absent;
- hide/privacy-style removal intent → document absent;
- stale work → no overwrite;
- transient provider failure → retried through shared infrastructure;
- terminal provider/mapping failure → visible Search work failure + IntegrationFailure.

### Cluster Build-Plan Link

CL-02 Feature 03 — production projection worker after this Module provider gate. The earlier CP Feature 02 fake-writer harness is not this milestone.

### Dependencies

- Features 01–04;
- SH-024, SH-094;
- SH-092 provider port;
- SH-047/048/051/052 reliability;
- SH-037 failure telemetry;
- source contract fakes.

### In Scope

- worker handler;
- atomic Search work claim/transition using shared mechanisms;
- source projection/readiness loading;
- `composeSearchVisibilityDecision`;
- safe document mapper;
- provider upsert/delete;
- projection/source version checks;
- ranking-signal hook with no complex weighting yet;
- work outcome recording;
- retry/permanent error classification;
- provider-success/crash replay safety.

### Out of Scope

- real cross-Module event subscriptions;
- public query endpoint;
- complex ranking algorithm;
- protected candidate query;
- scheduled reconciliation;
- direct Notification.

### Module-Owned Data

`SearchUpsertEvent` work status/outcome/projection-version fields as settled in Feature 01; external provider projection.

### Public Interfaces

No new public interface. Implements the execution behind SH-091.

### Shared Operations Used

- **SH-024 `evaluatePublicReadiness`** — owner decision;
- **SH-094 `buildSourceProjection`** — owner data;
- **SH-092 `writeSearchProjection`** — provider effect;
- **SH-047/048** — durable job and retry;
- **SH-051/052** — same-entity concurrency/source-version protection;
- **SH-037/038** — failure/queue telemetry;
- **SH-034** — telemetry redaction.

### Domain Logic

Processing algorithm:

```text
load Search work
→ reject completed/superseded replay safely
→ acquire same-entity concurrency guard / verify source version currentness
→ load owner source projection
→ load owner readiness for requested surface
→ if missing/denied/restricted: determine stable provider identity and delete/no-op
→ otherwise validate safe source projection
→ apply Search surface field minimization
→ obtain/validate fuzzy public location when required
→ attach basic approved ranking metadata only after eligibility
→ build provider document + projection version
→ SH-092 upsert/delete
→ persist Search outcome
```

Rules:

- source owner denial always wins over requested restore/update;
- missing source defaults to removal/no-op, not preservation of stale index;
- exact private location causes a mapping failure/removal, never fallback exposure;
- raw resume content causes hard mapping rejection;
- no paid/trust ranking signal overrides a denied decision;
- stale source version cannot overwrite newer doc.

### Authorization / Compliance

Worker runs under trusted system context. It does not bypass owner readiness just because no human actor is involved.

### Database / Transaction Behavior

- claim/Search-state transition is database/queue safe;
- provider write is external and cannot share DB transaction;
- completion recording happens after confirmed normalized provider effect;
- crash after provider success is recovered by idempotent replay;
- terminal failure records Search work failure and SH-037 operational evidence separately.

### Events / Jobs

Consumes the job queued in Feature 04. No outbound domain event required. Shared queue manages retry/dead-letter.

### Provider Integration

Uses SH-092 only. Never instantiate Typesense client in worker service directly.

### UI / Admin Surface

None.

### Failure Behavior

- dependency unavailable/provider timeout → retryable;
- invalid source projection → terminal until source/mapper corrected;
- schema mismatch/credential failure → terminal/manual intervention after classification;
- stale work → superseded/no-op;
- provider delete missing → completed no-op;
- worker retry exhaustion → Search work terminal failure + Ops visibility; source remains unchanged.

### Tests

- eligible → upsert;
- denied → remove;
- missing → remove/no-op;
- stale update after newer hide → cannot restore;
- update after hide with newer valid source → can restore;
- raw resume field rejection;
- exact location rejection;
- boost/trust signal cannot overcome denial;
- provider timeout retries;
- permanent mapping error dead-letters/records failure;
- crash after provider success replay;
- concurrent same-entity work;
- no foreign Prisma repository import.

### Documentation Updates

Record finalized Search-level exclusion/outcome reason codes and source-version comparison semantics if they were deferred.

### Acceptance Criteria

- worker can produce correct upsert/remove/no-op using only Search work + public source contracts;
- stale/out-of-order work is safe;
- provider failure cannot mutate source truth;
- shared reliability infrastructure is used;
- privacy/location/resume safety invariants are enforced in document mapping.

### Exit Gate

Pass domain, concurrency, provider-fake, queue-retry, and integration tests plus typecheck/lint/build. Manually verify a test document can be added/removed against development Typesense when available.

---

## 06 Public Discovery Query Surface

### Objective

Expose a normalized public Search query that can discover only approved public projections without leaking provider topology or protected data.

### Observable Result

A public caller can search supported public entity types with bounded query/filter/facet/pagination inputs and receive normalized public-safe results. Candidate and `user` results cannot be requested through this surface.

### Cluster Build-Plan Link

CL-02 Feature 03 — initial public taxonomy query, extended by Feature 09 source integrations.

### Dependencies

- Feature 03 provider query port;
- Feature 05 public projections;
- runtime validation;
- platform rate-limit/abuse-control mechanism when available;
- taxonomy/fuzzy-location fields exposed by approved projection schemas.

### In Scope

- `searchPublicDiscovery` contract/service;
- public entity-type allowlist;
- query text normalization only to the extent Search owns provider query behavior—not taxonomy normalization truth;
- allowlisted filters/facets/sorts;
- bounded pagination;
- normalized heterogeneous result envelope;
- provider highlights/snippets only from allowlisted public fields;
- safe empty/degraded/error states;
- public search metrics without raw sensitive query logging.

### Out of Scope

- protected candidates;
- exact location radius over private coordinates;
- complex recommendation/personalization;
- AI query interpretation;
- complex ranking algorithm;
- user account search;
- exposing raw Typesense collection/filter syntax.

### Module-Owned Data

None. Reads provider projections only.

### Public Interfaces

Introduces `searchPublicDiscovery`.

Expected request semantics:

```text
query
entityTypes?         # approved public types only
filters?             # typed/allowlisted
facets?              # typed/allowlisted
sort?                # approved values
page/cursor
pageSize             # bounded by config
public location filter using approved fuzzy fields only
```

### Shared Operations Used

- **SH-092** provider query path;
- **SH-032/033/034/036** request context, safe logs, redaction, metrics;
- platform rate limiting if/when its canonical operation is defined in root context.

No SH-001 is required for genuinely anonymous public search unless root product policy requires a session.

### Domain Logic

- permitted public types: `professional_profile`, `organization`, `offering`, `gig`, `job`, `taxonomy`, approved `trust_badge` surface as architecture defines;
- `candidate_profile` and `user` are forbidden;
- provider document hits are returned as projections, not re-labeled “verified/current source truth”;
- queries can filter only over fields present in the Search collection registry;
- safe location fields are fuzzy/public only;
- ranking remains basic MVP and cannot include unapproved entitlement signals for public surfaces.

### Authorization / Compliance

Anonymous public access is allowed only to public collection descriptors. Protected collection keys/queries are unreachable from the public contract. Rate/abuse policy applies through shared platform controls.

### Database / Transaction Behavior

None.

### Events / Jobs

None. Search-query analytics, if later needed, must be explicitly architecture-reviewed before storing user search history.

### Provider Integration

SH-092 maps normalized query DTO to Typesense. Raw Typesense response is transformed to Search result DTO.

### UI / Admin Surface

No UI is required by the Module plan. Public product pages consume the query.

### Failure Behavior

- invalid/unsupported filter/entity type → validation error;
- protected entity request → surface not supported/forbidden;
- provider unavailable → safe dependency/provider unavailable result; do not fall back to unfiltered database search without architecture approval;
- empty result → successful empty page.

### Tests

- every supported public entity type query;
- candidate/user type denial;
- arbitrary filter/sort/collection injection denial;
- exact-location field absent from response;
- raw source/provider fields absent;
- pagination bounds;
- provider unavailable normalized response;
- public/protected collection isolation;
- query log redaction/telemetry cardinality tests.

### Documentation Updates

Document the approved public entity types, filters/facets, and result envelope. Do not document provider collection names as public API.

### Acceptance Criteria

- public query returns only provider-projected public fields;
- candidate/user are inaccessible;
- filters are allowlisted and runtime validated;
- provider topology is hidden;
- no direct database fallback bypasses Search readiness/privacy.

### Exit Gate

Pass public Search contract/security/provider tests, typecheck/lint/build, and an E2E test proving an eligible fake/test source becomes searchable and disappears after de-index.

---

## 07 Backfill and Search Debug Foundation

### Objective

Make the projection rebuildable and diagnosable before broad source integrations are connected.

### Observable Result

An authorized operator can dry-run or execute a bounded backfill for a supported source adapter and inspect why a specific entity is present, absent, stale, superseded, or failing.

### Cluster Build-Plan Link

CL-02 Feature 03 — taxonomy-slice repair/debug proof; Feature 12 and SP Feature 11 retain generalized production reconciliation.

### Dependencies

- Features 01–06;
- SH-001/002 for admin;
- SH-029 audit;
- SH-047 queue;
- source contract fakes/first real source adapter;
- existing authorized Admin shell, if available.

### In Scope

- `runSearchBackfill` command;
- cursor/checkpoint/batch job payload;
- dry-run mode;
- one or more adapter-driven enumeration contracts without direct foreign Prisma access;
- `inspectSearchProjection` query;
- minimal Search-specific admin/debug UI if the admin shell exists;
- manual reindex/deindex action through SH-091;
- safe audit of privileged manual actions;
- repair summary counts.

### Out of Scope

- scheduled recurring reconciliation;
- generic queue/Ops dashboard;
- raw source record viewer;
- raw resume/candidate private content;
- arbitrary Typesense console;
- collection topology editor.

### Module-Owned Data

Existing Search work. Optional backfill checkpoint is Search-owned only if the shared queue payload/checkpoint cannot safely carry it; prefer shared job checkpoint mechanism when available.

### Public Interfaces

- `runSearchBackfill` restricted command;
- `inspectSearchProjection` restricted query;
- SH-091 used for manual individual repair.

### Shared Operations Used

- SH-001/002 actor/authority;
- SH-029 audit for manual/bulk actions;
- SH-032–038 telemetry;
- SH-047/048 reliable job/retry;
- SH-094/024 source projection/readiness.

### Domain Logic

Backfill:

```text
enumerate owner projection identities by cursor
→ request/currently load owner projection + readiness
→ invoke same Feature 05 mapper/provider path
→ checkpoint
→ summarize upsert/remove/skip/failure
```

It may not copy rows directly into Typesense with a special “fast” path that bypasses visibility composition.

Debug query exposes:

- Search work IDs/status/outcome;
- owner source/projection version reference;
- provider document presence/version;
- Search-level reason codes;
- safe dependency references;
- failure correlation ID.

It does not expose protected source payloads.

### Authorization / Compliance

Admin/debug requires SH-001 + SH-002. Manual bulk/deindex actions append SH-029 audit evidence. Use SH-030 only if the debug result is classified sensitive under policy.

### Database / Transaction Behavior

Batch checkpoints must allow restart without duplicating harmful effects. No global transaction across a backfill batch. Each entity uses normal idempotent projection semantics.

### Events / Jobs

Backfill is a durable job. No independent backfill queue implementation.

### Provider Integration

Uses the normal SH-092 adapter path.

### UI / Admin Surface

If root admin shell is ready, add only Search-specific screens/components:

```text
/admin/search
  - entity/event lookup
  - provider presence/version
  - recent Search work/failures by reference
  - backfill dry-run/execute controls according to permission
```

Otherwise expose the command/query to internal tests/CLI and defer UI without inventing a shell.

### Failure Behavior

- one bad entity records failure and continues according to approved batch policy;
- provider outage causes durable retry/checkpoint, not loss of cursor;
- unauthorized admin → no debug data/action;
- missing source during backfill → remove/no-op according to normal worker policy.

### Tests

- dry-run has no provider mutation;
- backfill uses same mapper/readiness path as normal worker;
- resume after failure/checkpoint;
- no duplicate effects on replay;
- admin authorization;
- audit event for manual bulk action;
- debug view redacts raw source/private fields;
- public user cannot access admin query.

### Documentation Updates

Document operator runbook inputs/exit criteria and the difference between Search debug evidence and source truth.

### Acceptance Criteria

- Search can be rebuilt without direct source-table SQL copying;
- operator can explain projection state using safe evidence;
- backfill is resumable/idempotent;
- admin tooling does not become a generic Ops console.

### Exit Gate

Pass backfill/debug/auth/audit tests, typecheck/lint/build, plus a dry-run and real small-batch development verification.

---

# Phase 3 — Module Integration

This phase proves Search works with real neighboring Modules through public contracts. It must be executed incrementally as those Modules expose their required public contracts. A source integration cannot be “completed” by importing that source's Prisma repository if its public interface is not ready.

## 08 Public Source and Signal Integrations

### Objective

Connect the public Search projection pipeline to the first real source owners and to CL-02/guardrail signals without transferring lifecycle policy into Search.

### Observable Result

At least the source types currently available in the repository can change their authoritative public state and reliably cause Search to create/remove/update the correct projection through SH-091. Contract tests prove every integration uses owner projections/readiness.

### Cluster Build-Plan Link

CL-02 Feature 09 — real public-source integrations as Professional/Offering, Gig, and Organization/Job owner contracts become available.

### Dependencies

- Features 01–07;
- source Module public interfaces/events;
- SH-046/045 outbox/inbox where event-driven;
- SH-091 Search command;
- SH-094/024 source contracts;
- SH-131 Location Safety;
- SH-005 Track candidate boost signal when relevant;
- Trust/Professional/Job/Healthcare readiness interfaces as source owners require.

### In Scope

For each ready source type:

1. define/consume its SH-094 adapter;
2. define/consume its SH-024 readiness contract;
3. register source-change events or explicit post-commit command path;
4. consume change idempotently;
5. call SH-091;
6. add end-to-end contract tests.

Target public types:

- taxonomy;
- professional_profile;
- offering;
- gig;
- organization;
- job;
- trust_badge as an approved display/ranking projection.

Also integrate:

- SH-131 fuzzy location through source projection/document mapper;
- Track entitlement change → candidate reindex signal only when the candidate source integration exists;
- accepted taxonomy changes → affected projection refresh; AI suggestions alone must not trigger public indexing.

### Out of Scope

- raw foreign Prisma reads;
- candidate protected query (Feature 10);
- organization ATS commercial entitlement decision;
- complex ranking;
- raw VerificationCheck/JobComplianceFinding reads;
- AI provider output directly into Search.

### Module-Owned Data

Only Search work/provider projections. No source model writes.

### Public Interfaces

Consumes source events/interfaces; exposes SH-091. No source-specific parallel Search command.

### Shared Operations Used

- SH-091 Search refresh;
- SH-094 source projection;
- SH-024 public readiness;
- SH-046 `publishDomainEvent` + SH-045 `deduplicateDomainEvent` when source change is event-driven;
- SH-131 fuzzy location;
- SH-016/018/020/021 only through the approved owner composition path when a source interface requires them;
- SH-005 for candidate boost signal when later connected.

### Domain Logic

Integration principles:

- source lifecycle event describes source fact, not “write Typesense document”;
- Search reacts by loading current owner projection/readiness;
- accepted Taxonomy owns facet/classification values; AI suggestion changes are irrelevant until accepted;
- Job cannot be indexed because `Job.status` “looks publishable” if Job Compliance/owner public readiness denies it;
- Professional/Offering cannot be indexed because a TrustBadge exists if readiness denies it;
- trust/boost changes refresh ranking metadata only for already-eligible sources;
- source event ordering is neutralized by current source version.

### Authorization / Compliance

System event consumers still enforce public-readiness/privacy policies. No user actor is required for passive source sync, but event authenticity/dedupe comes from shared platform event infrastructure.

### Database / Transaction Behavior

Source Modules own their authoritative transaction and outbox. Search consumer inbox/dedupe then invokes SH-091. Do not write Search work from source repository code directly.

### Events / Jobs

- consume versioned source domain events;
- use SH-045 dedupe;
- call SH-091;
- ordinary Search projection job executes afterward.

### Provider Integration

Always uses existing SH-092 adapter/mapper. No source-specific provider path.

### UI / Admin Surface

No new UI beyond debug view showing source integration references.

### Failure Behavior

- event consumer fails before SH-091 → inbox/event retry;
- Search request fails → consumer retries idempotently;
- source interface unavailable → Search worker retries;
- source owner denies → projection removed;
- unknown source event/version → explicit integration error, not guessed mapping.

### Tests

For each activated source:

- source publishes/updates → Search projection appears/changes;
- source hides/unpublishes → Search projection disappears;
- duplicate domain event → one semantic Search refresh;
- out-of-order source event → newest source version wins;
- owner readiness denial wins over raw status field;
- taxonomy accepted change triggers refresh; AI suggestion alone does not;
- fuzzy location only;
- trust/boost signal cannot create an otherwise absent projection;
- no direct source repository import.

### Documentation Updates

Maintain an integration matrix recording which entity types have real source adapters/events versus test fakes. Update source Module public-interface docs if their contract is settled there.

### Acceptance Criteria

- every active source type has one owner and one projection/readiness boundary;
- source lifecycle changes reach SH-091 durably;
- no source Module calls Typesense or writes SearchUpsertEvent directly;
- public projections reflect owner policy and safe location;
- Search remains replaceable/rebuildable.

### Exit Gate

Each source integration has its own contract/E2E proof. The feature is considered fully complete only when all public entity types planned for MVP have real owner interfaces; partial source completion must be explicitly recorded rather than marked complete globally.

---

## 09 Privacy, Moderation, and Hold Enforcement Integration

### Objective

Prove that legal/privacy/moderation/hold changes remove or restore Search projections through their owning workflows and that rebuild/reconciliation cannot resurrect forbidden data.

### Observable Result

A Privacy target instruction can idempotently remove Search provider documents and return a typed result; a Moderation action can hide/remove/restore through SH-103/SH-091; an applicable ComplianceHold causes owner/Search readiness to exclude the projection. Backfill respects all three.

### Cluster Build-Plan Link

CL-02 Feature 11 prerequisite-contract slice precedes Feature 10; later asynchronous reaction/owner-orchestrator integration remains in Feature 11. Preserve all Module enforcement/anti-resurrection tests.

### Dependencies

- Features 01–08;
- SH-095/096 Privacy protocols;
- SH-097 `evaluateRetentionRequirement` where Search-owned work/provider data requires retention evaluation; no exemption ownership transfer;
- SH-103 Moderation executor protocol;
- SH-011 ComplianceHold;
- SH-029 audit for manual enforcement if required;
- Privacy/Moderation/Hold owner interfaces or contract fakes.

### In Scope

- Search-owned retention facts through SH-097, with approved basis/minimum-fields/retain-until/anonymization-permission result; no retention policy or field-level anonymization mapping is approved here;

- `executeSearchPrivacyInstruction`;
- `enumerateSearchSubjectData`;
- moderation target executor mapping hide/remove/restore to Search work;
- Search enforcement result DTOs;
- idempotent provider delete;
- anti-resurrection checks in backfill/reconcile;
- hold-aware readiness composition where the source owner contract says Search must evaluate the hold directly;
- operational failure reporting.

### Out of Scope

- PrivacyRequest/DataErasureJob lifecycle;
- legal retention exemption decision;
- ModerationCase/LegalNotice resolution;
- generic ComplianceHold lifecycle;
- file/media public URL removal;
- notification delivery.

### Module-Owned Data

- Search work references/outcomes;
- provider projection presence/absence;
- Search-owned subject-data enumeration metadata.

### Public Interfaces

- Search implementation of **SH-095**;
- Search implementation of **SH-096**;
- Search target implementation under **SH-103**;
- SH-091 remains internal enforcement funnel.

### Shared Operations Used

- SH-095 `executePrivacyInstruction`;
- SH-096 `enumerateSubjectData`;
- SH-103 `executeModerationDecision`;
- SH-011 `evaluateComplianceHold`;
- SH-091 Search refresh;
- SH-029 audit when actor-driven/manual;
- SH-037 integration failure;
- SH-044 idempotency.

### Domain Logic

Privacy:

```text
Privacy instruction
→ resolve Search provider identities for target
→ delete/restrict idempotently
→ create/complete Search work as appropriate
→ return typed result
→ future backfill still asks owner readiness/privacy state before restore
```

Moderation:

```text
Moderation action hide/remove
→ SH-103 Search executor
→ SH-091 remove/hide intent
→ delete provider doc

Moderation restore
→ SH-091 restore intent
→ worker re-loads current source readiness
→ upsert only if all current gates allow
```

Hold:

- active applicable hold may produce exclusion/removal;
- hold release triggers refresh but does not force restore if another gate denies.

### Authorization / Compliance

Authority to erase/moderate/hold comes from the owning Module's verified instruction. Search validates target/scope but does not re-authorize the legal decision itself.

### Database / Transaction Behavior

Privacy/Moderation owner records remain in their owner transactions. Search target execution is separately idempotent and returns evidence. Do not directly mark Privacy/Moderation rows completed from Search.

### Events / Jobs

Use SH-091/shared queue for asynchronous projection effect unless the privacy protocol requires a synchronous deletion acknowledgment; if synchronous provider deletion is required, it still uses SH-092 and idempotency and must be documented in the feature specification.

### Provider Integration

Delete-by-stable-ID through SH-092. Provider absence is success/no-op.

### UI / Admin Surface

Debug viewer may display enforcement reference IDs/status safely; it must not expose legal notice content or privacy request details beyond references.

### Failure Behavior

- provider unavailable → retryable privacy/moderation target failure according to shared protocol;
- invalid target → terminal invalid target result;
- already absent → success/skipped/no-op;
- retention question about SearchUpsertEvent → return/search-specific retained status only if Privacy protocol/ruling has established it; do not invent exemption.

### Tests

- privacy removal deletes public/protected docs;
- repeated privacy target is idempotent;
- backfill after erasure does not resurrect;
- moderation hide removes;
- moderation restore rechecks readiness;
- hold activation removes/blocks as configured;
- hold release does not bypass privacy/moderation/source denial;
- Search cannot mutate PrivacyRequest/ModerationCase/ComplianceHold tables;
- subject-data enumeration returns only Search-owned references;
- provider failure returns typed retryable result and records Ops failure.

### Documentation Updates

Resolve or explicitly retain the SearchUpsertEvent privacy-retention question. Update privacy target registry documentation with Search executor target types.

### Acceptance Criteria

- Search executes, but never owns, privacy/moderation/hold decisions;
- enforcement is idempotent and observable;
- provider doc removal is independent from source deletion;
- rebuild paths honor current restrictions;
- legal/privacy records remain in owner Modules.

### Exit Gate

Pass privacy/moderation/hold contract and anti-resurrection tests. Production wiring to actual owner workflows waits until the actual Privacy/Moderation/Hold owner interfaces pass their own exit gates.

---

## 10 Protected Candidate Search Integration

### Objective

Enable organization-authorized, privacy-safe candidate discovery without exposing candidates publicly, indexing raw resumes, or turning Search into an ATS.

### Observable Result

An authorized organization actor with any required commercial entitlement can query a protected candidate collection built only from active Candidate-owned `CandidateSearchProjection` data. Unauthorized, privacy-disabled, hidden, erased, or ineligible candidates never appear.

### Cluster Build-Plan Link

CL-02 Feature 10 — protected Candidate Search, after Candidate/Organization owner interfaces and enforcement prerequisites; exact composition remains U-CL02-10.

### Dependencies

- Features 01–09;
- Candidate Application & Resume Privacy public interface and `CandidateSearchProjection` lifecycle;
- Organization Hiring owner facts/authorization context;
- SH-001/002;
- SH-005 Track entitlement where feature is gated;
- unresolved organization commercial-entitlement ruling if applicable;
- protected collection isolation from Feature 03;
- Candidate privacy/readiness contract;
- SH-030 policy decision if protected candidate search is classified sensitive.

### In Scope

- candidate source adapter consuming Candidate-owned projection only;
- protected collection document schema;
- protected projection refresh/reindex on candidate projection/privacy changes;
- `searchCandidatesForOrganization` query;
- organization authority context;
- entitlement lookup if the approved product model gates candidate search/boost;
- approved boost metadata on eligible candidates;
- protected query filter allowlist;
- sensitive-access audit only if architecture requires it;
- E2E integration with Candidate/Organization contracts.

### Out of Scope

- raw resume text/documents;
- resume viewer or signed file access;
- JobApplication/Interview lifecycle;
- hiring recommendations or automated suitability scores;
- background-check provider truth;
- public candidate search;
- organization plan model invention;
- Track usage metering unless exact business event/entitlement key is approved.

### Module-Owned Data

Protected Typesense candidate document; Search work rows only. Candidate projection remains external source truth.

### Public Interfaces

Introduces/activates `searchCandidatesForOrganization`.

Consumes:

- Candidate SH-094/SH-024 equivalent;
- SH-001/002 actor/authority;
- SH-005 entitlement;
- SH-006 only if a metered event is explicitly approved.

### Shared Operations Used

#### SH-001 / SH-002

Resolve actor and authorize the organization-scoped `search_candidates` action. Search supplies the action/resource context; Organization Hiring supplies membership facts.

#### SH-005 `resolveEntitlement`

Return effective candidate-search or boost policy. Search uses the result only for protected access/ranking as approved; it stores no premium truth.

#### SH-006 `consumeMeteredEntitlement` — conditional

Do **not** call this merely because a search occurred. The feature specification must identify the exact Track entitlement and business event that counts. If unresolved, leave metering out and record the decision blocker.

#### SH-030 `recordSensitiveAccess` — conditional

Use only if the privacy/security architecture classifies protected candidate search/result exposure as sensitive access.

### Domain Logic

Eligibility:

```text
CandidateSearchProjection is owner-approved active
+ not erased/hidden/disabled
+ candidate privacy allows protected discovery
+ organization actor is authorized
+ feature entitlement allows query, if applicable
→ candidate result may be returned
```

Ranking:

- active Track boost may affect order among eligible candidates;
- boost cannot include a private/hidden/erased candidate;
- boost truth is resolved from Track and refreshed when grant changes;
- no local `isBoosted` source-of-truth boolean.

Projection payload may contain only approved fields such as normalized titles/skills, experience band, safe location state, remote preference, and other Candidate-owned privacy-safe fields. It must not contain `ResumeParseResult.extractedText`, original resume file URLs, application answers, cover letters, or hidden source metadata.

### Authorization / Compliance

Fail closed if any organization membership, Candidate privacy, or required entitlement decision is unavailable. Admin role is not a bypass to candidate privacy unless a separate approved policy says so.

### Database / Transaction Behavior

No Candidate/Organization/Track mutation. Candidate projection change emits/request Search refresh. Protected query reads provider only after authorization.

### Events / Jobs

Candidate projection/privacy/boost changes funnel through SH-091 to ordinary Search worker. No candidate-specific queue.

### Provider Integration

Protected collection/query path through SH-092. Public search credentials/contract must be unable to access it.

### UI / Admin Surface

Search does not own the ATS UI. Organization Hiring UI calls this query and uses returned safe projections.

### Failure Behavior

- unauthenticated → unauthenticated;
- unauthorized organization actor → forbidden;
- entitlement denied → stable feature-denied result if applicable;
- candidate privacy/source dependency unavailable → fail closed/no result or dependency error according to query contract;
- provider unavailable → provider unavailable; no direct Candidate DB fallback;
- attempted raw-resume filter/field → validation error.

### Tests

- public surface cannot query candidate collection;
- organization member authority allow/deny matrix;
- Candidate projection statuses;
- erased/hidden candidate cannot appear even with boost;
- raw resume/app fields absent from provider document and response;
- Track boost changes ordering only among eligible candidates;
- missing entitlement denies only if entitlement is configured as required;
- no local usage event/counter write;
- no direct Candidate/Organization repository import;
- sensitive-access logging behavior if approved;
- provider outage does not fall back to raw DB candidate search.

### Documentation Updates

Before implementation settles:

- organization candidate-search entitlement owner/model;
- exact protected collection isolation;
- whether Search access is sensitive-audited;
- Track boost/metering semantics.

Update the architecture if any of those become binding decisions.

### Acceptance Criteria

- candidate search is protected, never anonymous;
- only Candidate-owned privacy-safe projection fields are searchable;
- raw resume/application content is impossible to retrieve through Search;
- authority/privacy/entitlement are all external owner decisions;
- boost cannot create eligibility;
- Search remains not an ATS.

### Exit Gate

Pass Candidate/Organization/Track contract tests, protected-collection security tests, privacy tests, typecheck/lint/build, and a real E2E organization candidate search. Do not mark complete if any required owner interface is still a fake in production configuration.

---

# Phase 4 — Reconciliation and Operational Maturity

## 11 Reconciliation, Drift Repair, and Provider Schema Migration

### Objective

Implement SH-093 so Search can prove and repair external-provider consistency over time without unsafe bulk scripts or source-policy bypasses.

### Observable Result

An authorized dry-run reconciliation reports missing, stale, extra/orphaned, version-mismatched, and forbidden documents. Execute mode repairs them through the normal mapper/provider path and records a bounded repair report.

### Cluster Build-Plan Link

CL-02 Feature 12 — generalized production reconciliation, distinct from early taxonomy-only repair proof; scheduling remains an Ops decision.

### Dependencies

- Features 01–10 as applicable;
- SH-093;
- SH-047/048;
- owner enumeration/projection/readiness interfaces;
- provider metadata/fetch APIs;
- Privacy/Moderation anti-resurrection integration;
- admin authorization/audit.

### In Scope

- `reconcileSearchProjection` implementation;
- cursor/checkpoint/dry-run;
- expected-vs-provider comparison;
- missing doc repair;
- stale version refresh;
- orphan/forbidden doc deletion;
- projection schema-version migration support;
- bounded repair report;
- resumable failure behavior;
- manual trigger; recurring schedule hook but no invented cadence.

### Out of Scope

- new generic scheduler/queue system;
- source lifecycle mutation;
- unbounded full-table memory scan;
- provider collection topology redesign during reconciliation;
- automatic legal/moderation decisions.

### Module-Owned Data

Search work/projection metadata; optional Search-specific reconciliation report/checkpoint only if the shared job system cannot represent required durable progress. Prefer shared job/checkpoint mechanisms and safe report output over a new truth table.

### Public Interfaces

- SH-093 internal worker;
- `runSearchReconciliation` admin/system command;
- `inspectSearchProjection` can surface drift references.

### Shared Operations Used

- **SH-115 `buildAggregateProjection`** — existing Search-owned versioned projection/rebuild behavior with checkpoint, idempotent write, lag, and source reconciliation; inclusion/ranking remains Search policy.

- SH-093 reconcile;
- SH-094/024 source expectation;
- SH-047/048 queue/retry;
- SH-001/002 admin authority;
- SH-029 audit manual repair;
- SH-036 metrics;
- SH-037 failures;
- SH-039 health.

### Domain Logic

For each expected entity:

```text
owner projection/readiness
→ expected provider identity + sourceVersion + projectionVersion OR expected absent
→ compare provider metadata
→ classify: healthy | missing | stale | forbidden | orphan | incompatible
→ dry-run report OR normal projection/delete path
```

Orphan deletion must verify the source/public-readiness/privacy/moderation state before destructive repair. A provider document not found in the current enumeration is not automatically safe to delete if enumeration is partial or a dependency is unavailable.

### Authorization / Compliance

Manual reconciliation requires admin authority. Privacy/moderation deny state must take precedence over stale provider documents. Repair reports are sanitized.

### Database / Transaction Behavior

Each entity repair is independently idempotent. Cursor/checkpoint is persisted through the shared job runner or Search-specific checkpoint only if necessary. No single transaction spans the full reconcile run.

### Events / Jobs

Durable reconciliation worker with shared retry/dead-letter. Schedule is **unresolved**; expose a hook/config for later Ops scheduling.

### Provider Integration

Uses SH-092 metadata/write/delete and schema-version operations.

### UI / Admin Surface

Add dry-run/execute controls and report summary to Search debug surface only if admin shell exists.

### Failure Behavior

- source enumeration incomplete/dependency outage → pause/retry, do not delete presumed orphans;
- provider unavailable → retry;
- schema incompatibility → stop affected collection migration and record manual intervention;
- single document mapping failure → record item failure and continue according to batch policy;
- stale privacy/moderation data → fail closed against restore.

### Tests

- missing provider doc repaired;
- stale version repaired;
- forbidden provider doc removed;
- true orphan removed only after safe verification;
- incomplete source enumeration does not mass-delete;
- dry run no mutations;
- replay/checkpoint resume;
- provider schema version migration fixture;
- privacy erased entity never restored;
- admin auth/audit;
- large dataset cursor/pagination test.

### Documentation Updates

Create/maintain operator reconciliation runbook and projection-schema migration runbook. Record recurring cadence only when root Ops decides it.

### Acceptance Criteria

- Search drift can be detected without direct cross-domain SQL;
- dry-run accurately classifies known fixtures;
- repairs use the same normal projection path;
- no unsafe orphan deletion on partial dependency failure;
- schema-version migration is observable/recoverable.

### Exit Gate

Pass reconciliation/provider/schema-migration tests, typecheck/lint/build, and a development dry-run/repair exercise against deliberately drifted data.

---

# Phase 5 — Module Hardening and Production Verification

## 12 Security, Idempotency, Outage, Privacy, and Performance Hardening

### Objective

Close the Module against the races, outage modes, privacy leaks, authorization bypasses, provider drift, migration hazards, and performance failures expected in production.

### Observable Result

The complete Search Module passes production-grade concurrency, replay, provider outage, privacy, protected/public isolation, telemetry-redaction, reconciliation, migration, and load/performance verification with no source-of-truth leakage.

### Cluster Build-Plan Link

CL-02 Feature 13 — production hardening and launch-readiness evidence.

### Dependencies

- all prior Search features required for the launched MVP surface;
- root production observability/security/rate-limit infrastructure;
- real Typesense staging environment;
- real source Module contract environments;
- Privacy/Moderation/Hold integration for launched entities;
- production migration/backfill tooling.

### In Scope

- concurrency/race test matrix;
- duplicate/replayed source events;
- worker crash/restart;
- provider outage/degradation;
- schema migration rollback/forward strategy;
- privacy/moderation race with backfill/reconcile;
- public/protected collection/key isolation;
- authorization abuse tests;
- query/filter injection/fuzz testing;
- telemetry payload audit;
- rate/load/performance testing;
- projection lag SLO/alert thresholds if root Ops has defined them;
- backfill/reconcile production runbook;
- disaster rebuild from authoritative source projections;
- data-retention/subject-enumeration verification;
- no sensitive source fields in provider schema.

### Out of Scope

- new product search/recommendation features;
- complex ranking experimentation;
- personalization history;
- new source entity types without architecture review;
- changing Privacy/Moderation/Track ownership.

### Module-Owned Data

No new business truth should be introduced merely for hardening. Add indexes/constraints/checkpoints only when justified by measured correctness/performance needs.

### Public Interfaces

Freeze/contract-test all launched interfaces:

- SH-091;
- `searchPublicDiscovery`;
- SH-095/096 executor/inventory;
- SH-103 Search executor;
- `inspectSearchProjection`;
- protected candidate query if launched;
- provider adapter contract.

### Shared Operations Used

Re-verify integration with:

- SH-001/002;
- SH-005/006 where active;
- SH-011/024/028;
- SH-029/030;
- SH-032–039;
- SH-044–048;
- SH-051/052;
- SH-091–096;
- SH-103.

Hardening must not replace any of them with Search-specific infrastructure.

### Domain Logic

Race scenarios that must pass:

```text
newer update vs older update
newer hide vs older restore
privacy erase vs backfill
moderation hide vs entitlement boost refresh
hold activation vs reconciliation
source delete vs worker retry
provider success vs worker crash before completion
schema vN→vN+1 migration vs ordinary update
candidate privacy disable vs protected query
```

Correctness rule: the current authoritative owner decision/source version wins; provider state never wins over source truth.

### Authorization / Compliance

- public contract cannot access protected candidate/admin collections even with crafted provider parameters;
- admin support cannot view raw candidate/private source data through debug;
- every launched protected action has server-side authorization tests;
- exact private location/raw resume/credentials are absent from provider/logs/queue/audit fixtures;
- Privacy target replay is idempotent and non-resurrecting.

### Database / Transaction Behavior

- verify idempotency and Search work indexes under contention;
- test realistic queue backlog and work-claim pattern;
- verify migration on realistic row counts;
- confirm no in-memory concurrency assumptions;
- confirm cleanup/retention behavior once Privacy ruling is settled.

### Events / Jobs

- duplicate event/inbox tests;
- retry exhaustion/dead-letter visible in Ops;
- worker restart/resume;
- reconciliation/backfill checkpoint recovery;
- schedule hook smoke test if cadence has been configured.

### Provider Integration

- simulated timeouts/429/5xx/config error/schema error;
- staging failover/restart behavior according to Typesense deployment;
- batch size/load tuning;
- query latency under realistic index size;
- safe collection schema update and rollback/alias strategy.

### UI / Admin Surface

- admin debug permission tests;
- dangerous bulk actions require explicit confirmation according to root UI/security standards;
- debug surface clearly labels projection/provider status as derived, not source truth.

### Failure Behavior

- provider outage → degraded Search result/error, no raw DB fallback unless separately architected;
- retry exhaustion → visible terminal Search work + IntegrationFailure;
- source dependency outage → no unsafe orphan deletion/rebuild;
- collection schema migration failure → halt affected writes/queries safely and surface operator action;
- privacy/moderation instruction failure → retryable/terminal executor result to owner; never falsely acknowledge success.

### Tests

Exact categories:

- unit policy suite;
- state-transition suite;
- SH contract suite;
- database migration/concurrency suite;
- provider adapter chaos/failure suite;
- authorization/public-protected isolation suite;
- privacy/moderation/hold anti-resurrection suite;
- sensitive telemetry/static provider-schema audit;
- E2E publish→search→hide/remove→restore journeys;
- candidate protected E2E if launched;
- load/performance tests for public query and projection throughput;
- reconciliation/backfill scale tests;
- clean rebuild from source contracts.

### Documentation Updates

- production Search runbook;
- Typesense collection/schema migration runbook;
- backfill/reconciliation runbook;
- incident/degraded-mode notes;
- resolved privacy retention and candidate entitlement/sensitive-access decisions;
- progress tracker and launch checklist.

### Acceptance Criteria

- no invariant in Module architecture is violated under the hardening scenarios;
- all launched Search surfaces can be rebuilt from owner interfaces;
- Search has no direct foreign repositories or provider client duplicates;
- provider outage does not corrupt business truth;
- privacy/moderation/hold races fail safely;
- public/protected isolation is penetration-tested at the application contract level;
- queue/retry/dead-letter and failure visibility use canonical infrastructure;
- measured query/projection performance meets root launch targets or explicit blockers are recorded.

### Exit Gate

The Module is production-ready only when the repository's canonical full quality suite passes, including:

```text
schema/migration validation
typecheck
lint/format
unit tests
contract tests
integration tests
authorization/security tests
privacy/moderation tests
provider adapter tests
queue/idempotency/concurrency tests
E2E tests
build
staging Typesense smoke/rebuild/reconciliation
performance/load checks required by launch plan
```

Any known failure or unresolved launch-critical decision blocks the Module launch and must be recorded as such.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01–03 |
| 2 | Core Projection and Public Discovery | 04–07 |
| 3 | Module Integration | 08–10 |
| 4 | Reconciliation and Operational Maturity | 11 |
| 5 | Module Hardening and Production Verification | 12 |

**Total features: 12**

### Sequence notes

- Features 01–07 map to the basic CL-02 Features 02–03 Search slices; generalized reconciliation is not implied.
- Feature 08 is incremental and closes source integrations only as their owning Modules become available.
- Feature 09 provides enforcement contracts before protected Candidate Search; production Privacy/Moderation reaction wiring follows the CP Feature 11 split.
- Feature 10 waits for CL-06 owner contracts and maps to CP Feature 10; protected candidate truth/authority remains external.
- Feature 11 can begin manually once enough source adapters exist; recurring scheduling is not decided here.
- Feature 12 maps to CP Feature 13 hardening.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview and root architecture.
2. Read repository instructions; referenced root code standards are unavailable.
3. Read the Canonical Shared Operations Registry.
4. Read current CL-02 architecture and build plan if they exist.
5. Read the current linked CL-02 build plan and verify actual external prerequisites.
6. Read this Module architecture and implementation plan.
7. Read public-interface sections for every direct dependency used by the feature.
8. Inspect current Prisma schema/migrations and existing Search implementation before creating files.
9. Confirm the prior feature exit gate.
10. Write the required feature implementation specification below.
11. Implement only the numbered feature.
12. Run all required quality checks for that feature.
13. Verify contracts/workflow against fakes or real dependencies as specified.
14. Update progress.
15. Update architecture only when a binding decision legitimately changed.
16. Record unresolved risks, missing owner interfaces, and any use of contract fakes.

A later feature may not “helpfully” finish deferred work from an earlier/later mapped Cluster feature unless the plan is explicitly updated.

---

# Required Feature Implementation Specification

Immediately before coding one numbered feature, the coding agent must produce a concise specification containing:

- **Feature:** exact number/name.
- **Objective:** one result.
- **Observable result:** what a reviewer can prove.
- **Dependencies:** prior Search features, root/Cluster milestones, source public interfaces, shared operations, provider prerequisites.
- **In scope:** exact files/services/migrations/tests.
- **Out of scope:** neighboring truths and later features.
- **Owned data affected:** Search-owned models/enums/provider projection only.
- **Public contracts:** commands/queries/executors/events changed.
- **Shared operations consumed:** IDs, owners, invocation, local policy, prohibited duplicate.
- **Permissions/compliance:** actor, authority, readiness, privacy, moderation, hold, entitlement, location gates as relevant.
- **Primary workflow:** ordered happy path.
- **Provider integration:** port/adapter operations, or `none`.
- **Jobs/events:** queue/outbox/inbox behavior, or `none`.
- **Idempotency/concurrency:** semantic key, version/lock/race behavior.
- **Error behavior:** stable failures and retryability.
- **Tests:** exact unit/contract/integration/provider/security/privacy cases.
- **Acceptance criteria:** observable requirements.
- **Documentation updates:** progress/architecture/interface/ADR changes.

Do **not** generate implementation specifications for all future features in advance. The agent writes the specification immediately before the feature so it reflects the repository state and settled prior decisions.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- **Feature completed** — number/name and result.
- **Files added** — exact paths.
- **Files changed** — exact paths.
- **Database changes** — models/enums/indexes/constraints/backfills.
- **Migrations** — migration names and validation status.
- **Dependencies added** — package/provider dependencies; explain why.
- **Module public interfaces added/changed** — contract names and compatibility notes.
- **Shared operations reused** — SH IDs; confirm no duplicate implementation.
- **Events/jobs added** — names, payload minimization, idempotency/retry semantics.
- **Provider adapter changes** — port/Typesense collection/schema/query/write changes.
- **Tests added/changed** — exact files/categories.
- **Commands run** — typecheck/lint/tests/build/migration/provider smoke checks.
- **Manual/contract verification** — what was actually exercised.
- **Documentation updated** — progress, architecture, interface, ADR/runbook.
- **Assumptions** — only those still valid and documented.
- **Known failures** — exact failing checks; never hide them.
- **Remaining risks** — concurrency/privacy/provider/coupling risks.
- **Deferred work** — Module/Cluster feature number that owns it.
- **Exit-gate result** — PASS or BLOCKED with evidence.

A feature with a blocked exit gate is not complete.

---

# Final Quality Check

Before considering this Module plan executed, verify all of the following:

1. `SearchUpsertEvent` and `SearchEntityType` have exactly one owner: Search / Public Visibility.
2. No Offering/Gig/Job/Organization/Professional/Candidate/Taxonomy/Trust/Privacy/Moderation/Location/Track truth has been absorbed.
3. SH-091 is the only source-facing refresh command.
4. SH-092 is the only Search provider boundary.
5. Source projections/readiness use SH-094/SH-024 rather than cross-domain repositories.
6. Queue/idempotency/retry/locking/audit/ops infrastructure is reused rather than duplicated.
7. Search provider state remains derived and rebuildable.
8. Privacy orchestration remains Privacy-owned and Search implements only its target effect.
9. Moderation decision lifecycle remains Moderation-owned.
10. Public Search never exposes protected candidate or `user` account projections.
11. Candidate Search uses Candidate-owned `CandidateSearchProjection` only.
12. Raw resumes/application documents/raw resume text are absent from provider documents, queues, logs, and Search results.
13. Exact private location is absent from public Search.
14. Eligibility always precedes ranking/boosting.
15. Track boost truth is external and no local premium/boost boolean exists.
16. Search work outcome, AuditEvent, IntegrationFailure, QueueJob, and source domain truth remain distinct.
17. Backfill/reconciliation cannot resurrect Privacy/Moderation/Hold-denied data.
18. Source-version/idempotency rules prevent stale out-of-order writes.
19. Every numbered feature has tests and a passed exit gate or is explicitly blocked/deferred.
20. Root/Cluster sequencing has not been silently reordered.
21. A coding agent can implement the next feature without inventing ownership, provider topology, privacy authority, or duplicate shared infrastructure.

## WA-R006 — Public-location read boundary

Search consumes SH-131 `getPublicLocationProjection`, the Location-owned side-effect-free read of current safe public fields. SH-028 remains Location's generation/update/invalidation command and is not called by Search projection reads. Never fall back to exact coordinates, local fuzzing or a read-triggered refresh loop. An unavailable/stale public projection must be withheld; where location is required for the document's eligibility, withhold that document until current safe data is available. This correction normalizes identity/use only: SH-131 retains Proposed ruling status until its owner-specific freshness/result contract is bound before production integration.


## WA-R013 — Explicit work arrangements (P03)

Product-owner ruling approved 2026-09-29: distinguish **fixed-term employment** and **independent-contractor work** as separate canonical concepts. A generic CONTRACT/contract value must not hide the distinction. This closes the product-meaning portion of U-CL06-07 / CL-06-U007. WA-R010 already assigns CompensationPeriod stewardship to Organization Hiring.

Hiring owns the work-arrangement vocabulary and source selection. The canonical concepts are FIXED_TERM_EMPLOYMENT and INDEPENDENT_CONTRACTOR; exact persisted enum spelling follows schema conventions in the coordinated database pass. Job Compliance consumes the explicit arrangement, preserves it in evaluated input/rule evidence and applies the relevant approved rule set. A selected label is not a legal determination of worker classification. Applicable jurisdictional legal rules remain an external gate.

Search projects the explicit owner-provided concepts and presents distinct filters/labels; it cannot derive them from job title, compensation period, or old contract text. Legacy EmploymentType.contract is ambiguous: preserve historical value, require authorized source clarification before affected republication/re-evaluation, and do not silently map every old row to either new concept. Reindex only after owner correction. Existing unambiguous employment types remain unchanged. Organization contractor Jobs remain Hiring work, not automatically Gigs or Offerings.

Implementation acceptance: distinct create/edit/publication and query/filter paths; exact compliance input and evidence for each concept; ambiguous historical rows blocked from new publication until clarified; no mass inferred backfill; no legal conclusion based only on employer-selected label. Prisma's present enum is implementation reality, not evidence that this ruling has been migrated.


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


## WA-R025 — Location consumer alignment and reveal evidence

Class: **AI_RESOLVED** from the binding location product ruling and canonical SH-027/028/131. U-08-13/14's product predicate/directionality is settled: exact service location is disclosed only to the authenticated Professional/provider legitimately performing the active in-person service, within its service-performance window. No buyer, Organization, Search or public-map entitlement to another party's exact location is implied. Completion ends that justification; cancellation, refund or dispute masks/revokes it. Rescheduling requires a fresh current decision. Payment, Booking confirmation or a cached flag alone is insufficient authorization.

Source Modules own their protected location facts/references. Booking's exact/fuzzy/precision/reveal fields are non-authoritative scheduling snapshots or compatibility fields; neither Booking nor Order operates a second reveal lifecycle. Location queries current typed participant, service-state, time-window and source-location facts through owners. Missing/stale/inconsistent facts deny disclosure. Each supported service context has a typed identity; an attached Booking and Order must be consistent, not arbitrarily XOR when both legitimately describe the service. A nullable context pair never permits context-free disclosure. Non-Booking source contexts require an explicitly supported service-performance contract; Job/Organization address fields do not automatically qualify.

Location stores current per-viewer/service/source decision plus immutable decision/revocation history using its owned lifecycle and SH-031 mechanism. The semantic current key includes viewer, typed service context and source reference; an owner source/policy token binds the decision. Atomically reject stale Location writes; revoke/expiry wins over a replayed old allow. Replays may reproduce proof identity but must never re-disclose exact data without a current authorization evaluation. Rescheduling updates evidence in the same owner lifecycle rather than creating a parallel reveal flag. WA-R023 requires durable sensitive-access proof before returning exact data. This resolves U-08-11/12/15/16/19 architecture; exact fields/constraints and coordinated migration remain implementation prerequisites.

Fuzzy generation uses a versioned Location policy per supported typed source, stable for the same source/policy generation. Radius/precision and refresh/expiry settings must be explicitly configured and validated before public use. Source/policy changes, privacy removal and expiry invalidate old results. SH-131 returns only current approved projection fields with source/policy version and validity; absent/stale data is unavailable, never exact fallback or read-triggered generation. Consumers use SH-028 only for generation/invalidation commands. The target-kind registry names actual source owners and validators; free-form target strings cannot broaden support. U-08-17/18 policy structure is AI_RESOLVED; numerical deployment settings are deferred configuration, and geocoder/KMS/vendor evidence is externally gated.

Acceptance: wrong viewer or source relation, absent context, Booking/Order mismatch, completed/cancelled/refunded/disputed service, reschedule, stale source/policy and delayed events, duplicate reveal after revocation, audit failure and expired public projection. Exact location remains absent from Search, notification payloads and telemetry. Legal retention/Privacy dispositions are not selected by this ruling.


## WA-R026 — Approved Review and multi-episode Dispute policy (P06–P08)

**Binding product-owner ruling, 2026-10-01.** Review input is a whole-number 1–5 star rating. Zero and half-star input are invalid; aggregate/reputation values may be fractional. Review owns the rating calculation; Professional and Search consume its versioned result, not separate scales or calculators.

Automatically publish an otherwise eligible Review after completed-Order, buyer-author and applicable safety/moderation checks pass. An author may revise rating or comment. Every proposed revision is immutable history and passes the same applicable checks before becoming the public/reputation-bearing revision. Promotion is atomic against the expected Review version; a delayed check for an older revision cannot supersede a newer one. A rejected/unavailable revision does not overwrite the previously accepted public revision; an active restriction independently controls whether any revision is public. Author editing never restores hidden/removed state or bypasses a restriction. Restoration is an explicitly authorized Review owner/Moderation action. Revisions update the contribution of the same Review; they never add another rating count. Hiding/removal withdraws its contribution; restoration uses the current eligible accepted revision.

The Order's buyer Customer or seller Professional may open a commercial dispute. Authorized support may record one on behalf of an identified participant where policy allows; preserve both actual support actor and represented participant. There is **one durable Dispute case container per Order at launch**, not one dispute episode for the Order's lifetime. Authorized reviewers may reopen that case for new evidence, a correction, or a later episode associated with the same Order, including another session of a multi-session package.

Persist a distinct immutable cycle/episode identity for each review/adjudication/settlement cycle, with opening/reopening reason, initiating/represented actor, relevant Order version, session references where applicable, evidence, decisions and outcomes. The case's current state is a projection of its current cycle; reopening never overwrites prior closed decisions or settlement proof. Serialize cycle creation and adjudication per case. A current pending cycle can receive new evidence; it does not require competing active refund/release decisions. Any concurrency policy must preserve one authoritative current case decision path.

Every financial effect requires valid current owner authorization and an idempotent identity bound to the specific cycle/decision/effect, with prior effects retained for reconciliation. Never key a new valid effect only by case ID, and never mint a fresh identity merely to retry an old effect. Reopening itself cannot replay a previous refund, charge, payout adjustment, settlement or hold-release effect. Order/Payment validate cumulative amounts and remaining authorized source value across all cycles; a new cycle is not permission to exceed the purchased/refundable amount. Dispute decides, Order coordinates transaction effects, Payment executes its rail, and Holds retains its own action-scoped lifecycle.

Opening/appeal windows remain separately versioned product policy; no numerical deadline is introduced. Bind the applicable policy version to each cycle. Product case windows do not redefine statutory/provider rights. Current Prisma's one-case relation is compatible with the container rule but does not supply cycle/revision proof; the coordinated database pass must add that representation before activation.

Acceptance: ratings 0/6/fractions rejected, fractional aggregate allowed; two revisions race without double counting; failed safety check leaves the accepted revision unchanged; hidden/removed edit cannot restore; buyer/seller/support attribution; unrelated actor denied; later-session episode reuses the case with a new cycle; old cycle remains reconstructible; replay of old financial result cannot affect the new cycle; valid new effect has its own authorization and respects cumulative Order limits. These are required implementation checks, not claims of executed feature tests.

Duplicate collapse: CL04-U034/035/036/038/040 and owner §9/§35 product questions; CL04-U039 retains its versioned configuration gate. WA-R022/023 technical proof, financial finality and assurance rules remain binding. Classification: PRODUCT_OWNER_CHOICE — RESOLVED by explicit approval; enforcement/revision/cycle identity details AI_RESOLVED.

## WA-R030 — Track catalog, enrollment, immutable grants and usage protocol

Classification: AI_RESOLVED_WITH_TRADEOFF. Track remains the commercial-policy owner; Candidate owns applications, Search owns ranking projections, Order owns transaction snapshots and Payment owns financial effects. This resolves technical representation/protocol alternatives; paid cancellation/grace and application quota product policies are explicitly separated below.

Represent free participation as an explicit Track-owned enrollment in a versioned free plan for each activated actor track, not absence of a subscription, a Stripe-created $0 subscription or a consumer-local free flag. Introduce a provider-neutral free enrollment representation; current provider default `stripe` must not label free records. Provision idempotently by User/track/profile identity. At most one current base enrollment selection exists per User/track; pending paid attempts may coexist without becoming current. Exactly one Customer/Candidate/Professional profile binding must match the selected track and User. Enforce typed FK/check constraints, user/profile consistency and current-selection uniqueness in the coordinated migration. Separate Organization ATS subject scope remains WA-R005, never a fourth AccountTrack. Historical enrollment rows remain reconstructible.

TrackPlanPrice is canonical for immutable amount/currency/billing cadence and provider-price correlation. TrackPlan.monthlyPriceCents is a compatibility/display projection and never a second price editor. A paid enrollment binds an immutable plan revision, price revision and applicable Consent proof/presentation; old enrollments and Order quotes never silently read today's edited price. Separate BillingCadence from TrackUsagePeriod. Existing monthly prices remain product truth; no new cadence, trial or price is invented. Activate a new revision only after catalog validation, retain effective intervals and prevent conflicting active revisions for the same selection key. Retiring a plan stops new enrollment, not evidence or previously authorized benefit periods. Accept conservative plan graph draft→active→retired→archived and draft→archived; archived is terminal, later publication is a new revision.

Catalog definitions are immutable typed keys with actor scope, value schema/unit, combination rule, period applicability and consuming capability. At most the designated value field may be populated and its type must equal the definition. Validate integer/money bounds, basis points and versioned JSON schemas; raw JSON is not executable policy. The initial product-backed key meanings are Candidate application allowance (15/month free, unlimited paid), Candidate employer-search boost (0 or 1500 basis points), verified-applicant plan badge and application-view insights; Customer qualifying buyer-fee waiver and early-availability eligibility; Professional commission (1000 or 300 basis points). Exact persisted key spelling is a coordinated contract constant, not a consumer-created alias. Additional unspecified premium features/ATS prices/limits are inactive catalog entries until explicitly defined; enum presence grants no benefit.

Resolve one current base plan revision, then only applicable active grant revisions. Equivalent benefits do not stack automatically. Each grant must declare an approved composition mode: extend duration, add a bounded quota, provide separately scoped value, or no additional effect for an equivalent benefit. Reject ambiguous overlap/configuration before grant activation; do not choose a winner by insertion order or a universal max/sum rule. An explicit replacement identifies the superseded grant with history. A grant never bypasses Role, readiness, Hold or source-owner eligibility. Accept grant graph active→expired/revoked/suspended/consumed; suspended→active only with authorized restoration and current validity, or →expired/revoked. Consumed is one-shot only; expired/revoked/consumed records are terminal. Append Track-owned immutable grant transitions, separate from audit and provider receipts; use a dedicated grant-history record or typed owner event table with equivalent append-only guarantees, not only mutable grant columns.

Track's Billing adapter owns subscription normalization and owner-specific provider receipts. A shared verified Stripe ingress routes by registered integration/account/resource/event purpose to Track or Payment; each owner has an independent effect receipt keyed by owner+provider-account+event ID, so one owner's receipt never suppresses the other's legitimate effect. Neither owner mutates the other's subscription/payment truth. New paid checkout starts incomplete, never default active. Provider confirmation is authenticated evidence bound to the exact attempt/price/subject. Out-of-order callbacks trigger owner reconciliation/version checks, not timestamp-only last-write-wins. Transition, immutable history and outbox commit together. Unknown financial/provider state cannot create paid access. Exact trial/grace/cancellation/downgrade benefits remain product policy, not imported from a provider enum; this ruling does not enable them.

Usage is an owner protocol: versioned period policy supplies a durable period identity/start/end/timezone; subject+track+entitlement+period policy/version identifies the counter across free/paid plan switches. Switching plans or provisioning another record never resets same-period consumption. Keep the counter rebuildable from immutable accepted consumption and compensating events. No destructive monthly reset or consumer-local quota. Semantic key binds source owner, source command/logical action, subject and entitlement; same key/fingerprint returns the same receipt, different payload conflicts. Quantity and policy revision persist with the receipt. A correction references the original event, is authorized by the source/Track policy and can compensate once; withdrawal or a monetary refund is not automatically a usage reversal. The actual monthly boundaries and withdrawal policy still require the product ruling identified in the decision packet.

For Candidate application submission use durable reservation/commit/reconcile, not foreign repositories or a distributed database transaction. Candidate first validates subject/Job eligibility and creates a stable submission intent. Track atomically reserves allowance and returns reservation/period/policy proof. Candidate commits the application once with that reservation, then emits a durable confirmation; Track converts the reservation to consumption idempotently. A duplicate source submission returns the original application/receipt. In-flight reservations reduce remaining capacity. On timeout query the Candidate submission outcome; release only on proven non-commit or owner-confirmed cancellation that prevents later commit. Unknown remains reconcilable, never silently free capacity. Withdrawal after successful commit follows the separately approved quota policy. Background cleanup cannot free a reservation while an application can still commit against it. This protocol is FOUNDATION_CAPABILITY, not full CL-01 maturity.

The approved Candidate subscription boost is non-metered effective ranking metadata, not a billable impression/application event. Search applies a 1.15 multiplier to its nonnegative base relevance/quality score only after all audience/eligibility/privacy filters; zero remains zero and deterministic ties use the normal stable tie-breaker. It is not a guarantee of 15% more views or permission to enter a protected result set. No `candidate_search_boost_applied` usage debit is enabled merely because the enum exists. Bound the projection to Track evidence/version and refresh on effective benefit change; stale or unavailable paid-boost evidence cannot silently confer a bonus. Earned separate boosts require their explicitly approved combination rule.

Fee/commission quotes carry integer basis points, currency, applicable basis identifier/amount, policy/plan/grant revisions and evaluation time. Order freezes the quote at its approved pricing/acceptance boundary. Use checked integer minor-unit arithmetic with deterministic round-half-up for nonnegative fee/commission calculation; sum the persisted rounded line allocations to the total and distribute any explicitly required remainder deterministically by stable line identity. Never use binary floating point or recompute old orders from current rates. Tax's jurisdiction-specific rounding remains Tax policy. A missing approved fee basis/eligibility policy is unavailable, not an invented charge. Payment consumes the Order-authorized monetary result, not a second Track fee calculator.

Required validation before activation: free/paid concurrent selection, wrong profile/actor binding, price revision change, typed value mismatch, ambiguous grants, grant restoration after expiry, duplicate/provider cross-owner event, quota contention/plan switch, crash before/after Candidate commit, unknown reservation outcome, duplicate compensation, stale boost and exact price rounding vectors. Schema/runtime proof remains unperformed at this architecture checkpoint.

## WA-R032 — Approved subscription benefit periods and Candidate quota (P12/P13)

Binding product-owner ruling, 2026-10-01 America/New_York. Supersedes P12/P13 open alternatives; WA-R030's owner boundaries and durable reservation/history design remain binding.

Cancellation or voluntary downgrade takes effect at the end of the already-paid subscription period. Premium benefits remain active through that paid-through time. Failed renewal creates no unpaid premium grace at launch. Provider retry/recovery may continue, but premium benefits end at the previously paid boundary unless payment is successfully recovered. Later recovery may resume benefits within the valid renewed entitlement period; never fabricate retroactive usage rights. Return to the applicable free-track policy when premium entitlement ends.

Existing purchase, Order, Booking, digital-access and other rights validly acquired while premium are not revoked merely because the subscription ends. Their owning Module/policy determines continuing rights. Subscription change cannot reprice an accepted Order, cancel an accepted Booking or revoke a purchased download by itself. End only the current subscription-derived benefit. No automatic free trials, subscription pauses or automatic prorated cancellation refunds at launch. Refunds follow approved refund policy rather than cancellation implying a refund. Core account/security access is never paid-only.

Track separates provider billing/recovery state from effective benefit intervals. A cancel request records scheduled end plus immutable intent/history; it does not set present benefits to false. Verified payment evidence binds a specific enrollment/price revision and paid interval. Query-time evaluation enforces interval boundaries even if the expiry worker is late. Past-due/retry state alone cannot extend the paid-through interval. A late recovered payment records the valid new interval and observation/activation time; effective resumption starts no earlier than verified recovery and never reauthorizes denied historical actions. Duplicate receipts cannot extend a period twice. Terminal or expired enrollment history is preserved; renewed access is an explicit versioned entitlement selection, not history overwrite. Paused/trial enum values remain unsupported launch transitions. Payment truth, retries and Track entitlement evaluation remain separate owners.

Free Candidate users receive 15 successful application submissions per UTC calendar month. Consume one quota unit only when one logical submission succeeds and is durably accepted into Candidate's application workflow. Failed attempts, retries, duplicate transport and rejected technical writes consume zero. Later Candidate withdrawal, employer rejection or any downstream application outcome does not restore a consumed unit. A proven technical duplicate/error is corrected by an authorized append-only adjustment referencing the original, not by deleting usage history.

Persist successful monthly usage for every Candidate submission, including while Premium is unlimited. The effective unlimited plan bypasses the numeric cap, not usage recording. On return to Free within that UTC month, available allowance is max(0, 15 minus already-recorded successful monthly usage), including Premium-period successes. Plan changes cannot reset counters, duplicate usage or create another 15. Calendar boundaries are half-open [first day 00:00:00 UTC, next first day 00:00:00 UTC); the owning Candidate durable acceptance timestamp selects the month, not the client clock or delayed outbox delivery time. Preserve policy revision, source intent/application, accepted timestamp and consumption identity.

For a submission spanning a month boundary, Track's capacity reservation must cover the month in which Candidate commits acceptance. Candidate must not commit against an expired prior-month authorization: renew/rebind the reservation under the new period, check the current plan/remaining capacity, then durably accept once. Store the resulting period proof with acceptance. At the period boundary, use a server-authoritative time/transaction guard and reconciliation so cleanup cannot release a reservation still eligible to commit. Unknown outcomes remain reserved until reconciled; failed/noncommitted work consumes zero. Successful unlimited submissions still produce idempotent consumption evidence without denying submission for exceeding 15. A late confirmation applies to its proven acceptance month, never the arrival month.

Required implementation checks: cancellation before paid end; failed renewal at boundary; recovery before/after boundary; duplicate recovery; preserved purchased rights; no retroactive authorization; 15/16 simultaneous Free submissions; failed technical writes; duplicate receipt; withdrawal/rejection without credit; Premium submits above 15 with recorded usage; downgrade with zero remaining allowance; period-boundary submission and delayed confirmation. These are acceptance requirements, not claims of runtime execution.

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

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P17

Candidate discovery/search participation is explicit opt-in and off by default. Persist the Candidate-owned participation choice with version, actor and time; no default database visibility boolean or JobApplication submission implies opt-in. Application workflow can expose the Candidate/application to that specific authorized hiring Organization independently of general discovery.

Disabling discovery invalidates future candidate-search exposure immediately at the authoritative query boundary and requests removal through Search/privacy contracts with durable completion evidence. Delayed provider deletion cannot authorize stale result disclosure. Opt-out preserves valid JobApplications and authorized hiring history under their owners. It grants no raw-resume access and does not enable anonymous Candidate indexing.

## WA-R070 — Source descriptors, assignment receipts and affected-target enumeration — implementation obligations

Qualify stable page retry, stale/scope-mismatched cursors and concurrent source changes before rebuild/merge integration. Require explicit comparable snapshot completion for orphan detection; verify Candidate opt-out wins over old enumeration and stale upsert.

## WA-R071 — Purpose-specific Location facts and disclosure — implementation obligations

Qualify the owner/Location WA-R071 bridge with denied/unavailable/mismatched facts, policy/source change, concurrent revocation versus old allow and bounded response validity. Assert exact fields never enter Search, generic events, Notification or telemetry. Activate only after relevant field serializer, numerical policy and legal/provider evidence qualify.


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `search_public_visibility` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`requestSearchProjectionRefresh / executePrivacyInstruction`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Qualify Track entitlement invalidation against current source/entitlement facts, including expiry, out-of-order revisions and acquired-right preservation. Search does not subscribe to track.usage_changed.v1 or treat eventual entitlement events as authorization.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.

## WA-R080 — Bilateral qualification sequence

Use scoped enumerateTaxonomyAffectedTargets.v1 and current owner projections; enumeration does not publish private targets. Follow the owner architecture and WA-R080 in `context/reconciliation/platform-architecture-rulings.md`. Qualify its named stale-source, wrong-scope, retry/conflict, unavailable and privacy cases on both sides before activation. External policy/provider and database prerequisites remain separate; no interface is frozen by this appendix.
