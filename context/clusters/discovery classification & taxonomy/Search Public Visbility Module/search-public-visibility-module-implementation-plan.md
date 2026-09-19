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
- SH-028 Location Safety;
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

- SH-028 fuzzy location through source projection/document mapper;
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
- SH-028 fuzzy location;
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
