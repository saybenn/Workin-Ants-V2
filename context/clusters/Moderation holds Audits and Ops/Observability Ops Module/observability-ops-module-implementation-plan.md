# Observability / Ops Module Implementation Plan

## Core Principle

Implement Observability / Ops through narrow, verifiable slices that make technical execution visible without moving business, provider-event, audit, privacy, or workflow truth into this Module.

Each slice follows:

```text
observable operational behavior
  -> validated command/query
  -> Observability-owned telemetry/failure/incident policy
  -> authoritative Observability write/read when approved
  -> canonical shared-operation calls
  -> audit/notification/privacy effects where required
  -> tests
  -> exit gate
```

This plan is subordinate to the CL-09 build plan. It subdivides only the Observability work needed by CL-09. It does not change Cluster feature order, accept unresolved architecture by implication, or authorize a schema that the Cluster architecture still marks Proposed/Unresolved.

The critical build constraint is the current persistence conflict:

- Registry/glossary claim `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` as Observability-owned truth.
- Current Prisma contains none of those models or Observability lifecycle enums.
- CL-09 tracks this under `PR-CL09-05`, `U-19`, and `U-20`.

Therefore contract/provider-neutral work can begin before persistence is settled, but no canonical migration or persistent lifecycle implementation may begin until the required architecture decisions are explicitly accepted.

---

## Build Rules

1. Follow root architecture, root code standards, CL-09 architecture/build plan, Canonical Shared Operations, and `module-architecture.md`.
2. Observability owns only operational visibility and its approved operational records/policies.
3. Source business Modules retain all business lifecycle truth.
4. Provider-owning Modules retain webhook verification, provider-event dedupe, provider status translation, reconciliation, and provider-driven domain transitions.
5. Audit / Event Ledger retains `AuditEvent` and `AccessAuditLog`; operational records never replace them.
6. Shared queue/platform infrastructure owns queue execution, leases, retry engine, dead-letter mechanics, idempotency, locking, and outbox primitives.
7. Reuse canonical shared operations. Do not create local substitutes.
8. All telemetry input is runtime-validated and sanitized before persistence/transmission.
9. No provider SDK type or raw provider payload may become a public Observability contract.
10. Detailed operational queries are server-authorized and redacted.
11. Public health responses are minimal; internal diagnostics are protected.
12. External effects such as Notification are idempotent and go through their owner interface.
13. Jobs are durable, retry-bounded, correlated, and observable through shared queue infrastructure.
14. Observability failures must not recursively crash or recursively log themselves.
15. Every numbered feature ends with tests and a concrete exit gate.
16. A Proposed Ruling or Unresolved item is never silently implemented.
17. Schema changes settle architecture only through an explicit architecture update/approval, not through implementation convenience.
18. Privacy / Data Erasure owns request/job/retention-exemption orchestration; Observability implements owner-local executors only.
19. Automatic incident grouping/alert thresholds remain disabled until `U-22` is approved.
20. Production retention behavior remains disabled until `U-24` is approved.

---

## Preconditions

### Hard platform dependencies

- Next.js / TypeScript / Prisma / Supabase foundation is available according to root context.
- Runtime validation follows root standards, expected to use Zod where current project context requires it.
- SH-001 `resolveAuthenticatedActor` exists before protected ops routes/actions are exposed.
- SH-002 `authorizeResourceAction` exists before protected operational detail or incident mutations are exposed.
- Shared request context, idempotency, queue, retry, locking, outbox/inbox, and concurrency primitives are available as each feature requires them. A contract-compatible stub is acceptable only where the CL-09 build plan explicitly allows one.

### Hard Cluster sequencing dependencies

- Module Feature 01 is a narrow dependency of CL-09 Feature 01 and primary dependency of CL-09 Feature 02.
- Module Features 02–06 implement the Observability portion of CL-09 Feature 02.
- Module Features 07–08 implement the Observability portion of CL-09 Feature 09 and may not jump ahead of Cluster prerequisites.
- Module Feature 09 implements the Observability portion of CL-09 Feature 10.
- Module Feature 10 implements the Observability portion of CL-09 Feature 11.
- Module Feature 11 implements the Observability portion of CL-09 Feature 12.

### Architecture decisions that are hard blockers

| Decision | Required before |
| --- | --- |
| `PR-CL09-05` / `U-19` — canonical persistence location | Module Feature 02 migration/repository work. |
| `U-20` — statuses/severities/lifecycle transitions | Any persisted failure/queue/incident lifecycle code; especially Features 02, 04, 05, 07. |
| `U-21` — queue runtime/provider | Production queue adapter only; contracts/telemetry instrumentation may use shared queue abstraction first. |
| `U-22` — automatic incident grouping / alert thresholds | Automatic incident creation, threshold worker, automatic severe alerts in Features 07–08. |
| `U-23` — logging/metrics backend selection | Production logging/metrics adapters; provider-neutral contracts can precede it. |
| `U-24` — Privacy target vocabulary / retention | Feature 09 production privacy execution. |

### Dependencies that may initially be stubbed behind published contracts

- Sentry adapter can use a fake provider in tests until deployment credentials exist.
- Search health/index-lag facts may be supplied by a typed fake until the Search owner interface exists.
- Payment, Calendar, Video, Media, Notification, Track Subscription, Verification, and other provider-owning Module failure signals may be contract fakes until cross-Cluster integration.
- Notification may be a contract fake until Feature 08/10 integration, but the fake must match Notification's public request contract.
- Privacy orchestration may use a contract harness until CL-09 Feature 10.

### Preconditions that must not be “solved” locally

Do not create a local queue provider, processed-webhook table, Sentry alternative, Role/Authority helper, Notification delivery client, cross-domain repository, or Privacy workflow merely because a dependency is not ready.

---

# Implementation Phases

## Phase 1 — Operational Foundation and Source-of-Truth Contract

### 01 Request Context and Telemetry Safety

#### Objective

Create the canonical request/correlation context and telemetry-safety boundary that CL-09 audit and all later Observability features depend on.

#### Observable Result

- Every test request/job can obtain a stable correlation/request context through the canonical interface.
- Telemetry metadata passes through one allowlist/redaction/truncation policy before logging or provider transmission.
- Prohibited sensitive fixtures are rejected or redacted deterministically.
- CL-09 Feature 01 can consume request context without creating its own correlation helper.

#### Cluster Build-Plan Link

Supports CL-09 Phase 1 Feature 01 **Audit Evidence and Request Correlation** and is foundational to Feature 02 **Operational Telemetry, Failure Visibility, and Health**.

#### Dependencies

- Root runtime/request middleware conventions.
- Canonical SH-032 `createRequestContext`.
- Canonical SH-034 `sanitizeTelemetryMetadata`.
- Identity & Access actor context if the current request is authenticated.
- No Observability Prisma model is required.

#### In Scope

- Typed request/correlation context contract.
- Async propagation across server request -> application service -> provider call -> queued job envelope.
- Correlation/causation propagation helpers consistent with canonical operation.
- Telemetry metadata allowlists, secret/sensitive-key detection, size/depth limits, safe serialization, truncation.
- Safe context extraction for logs, metrics, Sentry, audit requests, queue envelopes.
- Tests covering synchronous and asynchronous propagation.

#### Out of Scope

- `SystemEvent` persistence.
- integration-failure persistence.
- queue runtime implementation.
- Sentry/logging/metrics provider adapters beyond test seams.
- Role/Authority logic.
- audit record persistence.

#### Module-Owned Data

No Module-owned Prisma records affected.

Runtime contracts only:

- request/correlation context DTO;
- safe telemetry metadata DTO;
- telemetry rejection/result type.

#### Public Interfaces

- SH-032 `createRequestContext`
- context accessor/propagator consistent with root platform convention;
- SH-034 `sanitizeTelemetryMetadata`

No public browser endpoint is introduced.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | Optional authenticated request entry. | Persist/propagate only safe actor identifiers. | local current-user helper. |
| SH-032 `createRequestContext` | Observability/platform | Every request/job/provider entry. | Allowed identifiers and propagation rules. | `request-id.ts`, per-module ALS context. |
| SH-034 `sanitizeTelemetryMetadata` | Observability + Audit payload policy | Before logging/provider/persistence boundary. | Observability allowlist, size, cardinality, truncation. | `redactError`, `scrubLog`, blacklist-only helper. |

#### Domain Logic

- Create a request ID if one is not supplied by an approved trusted upstream boundary.
- Preserve correlation ID across nested work.
- Create causation linkage when a new async job/event is derived from an existing request.
- Treat correlation IDs as opaque identifiers, never authentication credentials.
- Never serialize arbitrary exception/provider objects directly.
- Reject or strip prohibited fields before any sink sees the payload.
- Ensure sanitized metadata is serializable, bounded, and deterministic enough for tests.

#### Authorization / Compliance

- No user-facing mutation.
- Authenticated actor data is optional and minimized.
- Prohibited telemetry fixtures include secrets, OTPs, PHI, card/payment data, SSNs, raw resumes, raw identity documents, private messages, and complete contracts.

#### Database / Transaction Behavior

No database write required.

#### Events / Jobs

- Job envelope must carry request/correlation context through the shared queue contract.
- No queue provider implementation.

#### Provider Integration

None required.

#### UI / Admin Surface

None.

#### Failure Behavior

- Unsafe metadata -> typed rejection/redaction result.
- Missing current request context -> create a new bounded context at an approved entry point, not in random helper code.
- Malformed upstream correlation ID -> normalize/reject according to root security conventions.
- Sanitizer failure -> fail closed for telemetry transmission; do not emit raw input as fallback.

#### Tests

- Unit: context creation, nested propagation, metadata allowlist, secret detection, truncation, serialization.
- Contract: DTO stability.
- Security: prohibited payload fixtures.
- Async: request -> queued job context propagation fake.
- Regression: sanitizer never returns original unsafe object by reference.

#### Documentation Updates

- Update Canonical Shared Operations only if the accepted operation contract itself changes.
- Update Module architecture if request-context ownership or payload policy changes.
- Record progress/exit gate.

#### Acceptance Criteria

1. One canonical request context is available to CL-09 Feature 01 and future Observability code.
2. Sensitive fixtures do not reach the sink test double.
3. Correlation survives an async boundary in tests.
4. No feature-local correlation/sanitizer helper is introduced.

#### Exit Gate

- Typecheck/lint/unit/security/contract tests pass.
- A test demonstrates one request ID appearing in an audit request stub, log stub, and queued job envelope without copying sensitive payload content.
- No Observability persistence decision was invented.

---

### 02 Canonical Operational Persistence and Repository Contract

#### Objective

After the architecture owner accepts the persistence and lifecycle decisions, add the canonical Observability source records and repositories exactly as approved.

#### Observable Result

If the accepted ruling is PostgreSQL/Prisma persistence:

- Prisma contains approved `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` models and approved enums/constraints.
- Repositories can create/query only Observability-owned records.
- External telemetry references remain secondary.

If the accepted ruling is an alternate persistence strategy:

- the Module architecture is updated first;
- repository/query contracts reflect that approved authority model;
- the implementation does not pretend missing Workin Ants records exist.

#### Cluster Build-Plan Link

Primary implementation slice for CL-09 Phase 1 Feature 02 **Operational Telemetry, Failure Visibility, and Health**.

#### Dependencies

- Feature 01.
- Explicit acceptance/resolution of `PR-CL09-05`, `U-19`, and `U-20`.
- Approved schema specification including fields, statuses/severities where any, indexes, mutability, idempotency, and retention markers.
- Shared migration standards.

#### In Scope

Only after decision approval:

- Prisma models/enums exactly matching the accepted architecture.
- relations or polymorphic source references as approved.
- indexes for request/correlation, source reference, provider/integration, status/severity, queue lookup, incident lookup.
- unique constraints / concurrency fields required by approved semantics.
- repositories with narrow owner-specific methods.
- safe DTO mapping from persistence records.
- migration and migration tests.

#### Out of Scope

- inventing fields/statuses/severity values.
- queue execution payloads or lease logic.
- business statuses.
- provider-event dedupe.
- incident automation thresholds.
- admin dashboard.
- Privacy retention duration unless `U-24` is separately resolved.

#### Module-Owned Data

Conditional on approved schema:

- `SystemEvent`
- `IntegrationFailure`
- `QueueJob`
- `OpsIncident`
- any explicitly approved Observability-owned enums/association records

No other Module's records are touched.

#### Public Interfaces

Repository layer remains internal. Public command/query contracts are finalized enough for later features:

- `recordSystemEvent` if approved;
- SH-037 `recordIntegrationFailure`;
- SH-038 `recordQueueTelemetry`;
- query contracts for failures/queue/system events;
- incident command/query contracts if lifecycle approved.

#### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-044 `executeIdempotentCommand` | Platform app infrastructure | Writes that require replay safety. | semantic key per approved record. | local idempotency table. |
| SH-052 `withOptimisticConcurrency` | Shared persistence | Mutable incident/failure rows if approved. | conflict/retry policy. | custom stale-write code. |
| SH-051 `acquireAggregateLock` | Shared persistence | Only where approved constraints need serialization. | lock key. | in-memory mutex. |
| SH-053 `transitionLifecycleState` | Shared mechanism | Any approved lifecycle transition. | Observability transition graph. | generic global lifecycle policy. |
| SH-034 `sanitizeTelemetryMetadata` | Observability/Audit policy | Before persistence. | record-specific safe fields. | raw JSON passthrough. |

#### Domain Logic

- Repositories never infer source business state.
- `QueueJob` cannot contain authoritative job/business completion fields beyond approved operational observation.
- `OpsIncident` relation/association cannot own foreign business objects.
- External provider references are secondary correlation only.
- Every mutable lifecycle field follows the accepted transition owner and concurrency rules.

#### Authorization / Compliance

Repository methods are server-only. Authorization belongs at application/public interface layer. Sensitive metadata remains minimized.

#### Database / Transaction Behavior

- Use one transaction for each authoritative write and its approved outbox/idempotency row where applicable.
- Apply accepted uniqueness constraints in DB, not only application code.
- Use migration safety review and production-like validation.
- Do not introduce cascading deletes that silently remove retained operational evidence unless Privacy/retention architecture explicitly permits it.

#### Events / Jobs

No event required merely because a record exists. Outbox wiring is added only for approved consumers.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- Architecture approval absent -> **STOP; do not implement migration.**
- Migration mismatch -> fail deployment; do not normalize silently.
- Unique/concurrency conflict -> typed conflict.
- Persistence unavailable -> typed retryable/unavailable result at application boundary.

#### Tests

- Schema validation.
- Migration apply on clean DB and production-like snapshot.
- Repository integration tests.
- Constraint/unique/index tests.
- Mutation boundary tests proving foreign records are untouched.
- Concurrency tests required by approved model.

#### Documentation Updates

Mandatory:

- update `module-architecture.md` from Proposed/Unresolved to accepted model details;
- update CL-09 architecture decision register;
- update root schema ownership references if required;
- update progress tracker.

#### Acceptance Criteria

1. The implemented schema exactly matches an accepted decision.
2. Four claimed records are either correctly persisted as approved or the architecture explicitly documents the accepted alternative.
3. No provider/business lifecycle fields are smuggled into the models.
4. Repository APIs are owner-scoped and do not access foreign Prisma tables.

#### Exit Gate

- Architecture approval references are recorded.
- Prisma validation/migration/integration/concurrency tests pass.
- Module architecture reflects the settled source-of-truth design.
- No next persistence-backed feature begins until this gate is green.

---

## Phase 2 — Core Operational Behavior

### 03 Structured Logging, Error Capture, Metrics, and Health Registry

#### Objective

Provide one provider-neutral operational telemetry rail for logs, exceptions, metrics, and component health.

#### Observable Result

- CL-09 code emits structured logs through one logger.
- A sanitized exception reaches a Sentry test adapter and, in configured environments, Sentry itself.
- Metrics are emitted through one client with controlled dimensions.
- Registered components return standardized health results with bounded timeouts.
- Public/minimal health and protected/detailed health are distinguishable.

#### Cluster Build-Plan Link

CL-09 Phase 1 Feature 02 **Operational Telemetry, Failure Visibility, and Health**.

#### Dependencies

- Feature 01.
- Feature 02 only if health/failure persistence is required by the accepted design; provider-neutral log/metric/Sentry contracts do not otherwise require DB.
- Sentry deployment configuration for production adapter; fake permitted in tests.
- Logging/metrics backend provider choice may remain unresolved through provider-neutral ports.

#### In Scope

- SH-033 `writeStructuredLog` implementation.
- logging port + current provider adapter if selected; safe console/server fallback only as root standards permit.
- error-monitoring port + Sentry adapter.
- SH-035 `captureException` implementation.
- metrics port + provider-neutral client; adapter if provider selected.
- metric naming/dimension registry.
- health registry and SH-039 `checkServiceHealth` implementation.
- minimal public health response and protected detail query plumbing.

#### Out of Scope

- integration failure persistence behavior beyond calls delegated to Feature 04.
- queue telemetry.
- incident grouping.
- automatic alerts.
- source business health definitions; owners register those.

#### Module-Owned Data

No new source records beyond any approved SystemEvent/health persistence explicitly accepted in Feature 02. Health registry may be runtime configuration.

#### Public Interfaces

- SH-033 `writeStructuredLog`
- SH-035 `captureException`
- SH-036 `emitMetric`
- `registerHealthCheck`
- SH-039 `checkServiceHealth`
- `getOperationalHealth`

#### Shared Operations Used

- SH-032 `createRequestContext`
- SH-034 `sanitizeTelemetryMetadata`
- SH-002 `authorizeResourceAction` for detailed health
- SH-030 `recordSensitiveAccess` when a detailed view exposes protected diagnostics
- SH-037 `recordIntegrationFailure` only for safe non-recursive sink degradation where policy says it is appropriate

Prohibited duplicates: direct Sentry client, feature logger, per-module metric client, independent health framework.

#### Domain Logic

- Logger enforces controlled fields and level vocabulary from configuration.
- Exception adapter removes unsafe fields before Sentry serialization.
- Metrics reject uncontrolled/high-cardinality dimensions.
- Health checks use bounded timeout; timeout -> unavailable/degraded result, never implicit healthy.
- Component owner defines check semantics; Observability aggregates them.
- Public health omits stack traces, provider account refs, internal URLs, queue payloads, record IDs, and secret/config detail.

#### Authorization / Compliance

- Public minimal endpoint requires no privileged detail.
- Internal/detail query requires Role / Authority.
- Sensitive diagnostic fields are hidden by default and access-audited when revealed.

#### Database / Transaction Behavior

None unless accepted persistence stores a health/system-event record. If so, follow Feature 02 repository contracts only.

#### Events / Jobs

No scheduled worker required.

#### Provider Integration

- Sentry adapter: unit/provider contract tests; no direct Sentry use elsewhere.
- Logging/metrics adapters behind ports; unresolved provider choice does not alter public contract.

#### UI / Admin Surface

Minimal developer/admin proof surface may show current component health. Full dashboard is Feature 08.

#### Failure Behavior

- Sentry unavailable -> bounded fallback; do not call Sentry recursively.
- logging sink unavailable -> bounded fallback and health degradation; do not crash unrelated business request unless caller policy requires telemetry proof.
- metric sink unavailable -> record health degradation/fallback without recursive metric emission.
- health check timeout -> explicit unavailable/delayed result.

#### Tests

- Unit: logger formatting, sanitizer integration, metric dimension validation, health aggregation/timeouts.
- Provider: Sentry adapter receives sanitized payload and correlation ID.
- Security: public vs protected health response.
- Fault injection: telemetry sink outage without recursion.
- Contract: provider-neutral result types.

#### Documentation Updates

Document selected logging/metrics providers if `U-23` is resolved during this feature. Otherwise record adapters still pending.

#### Acceptance Criteria

1. CL-09 uses one logger and one Sentry adapter.
2. Sensitive exception fixture never reaches provider stub in raw form.
3. Metrics reject user/source IDs as uncontrolled dimensions.
4. Health distinguishes healthy/degraded/unavailable/delayed semantics.
5. Public health is minimal.

#### Exit Gate

- Unit/provider/security/fault-injection tests pass.
- No direct Sentry/logging/metrics client exists outside canonical adapter in CL-09 code.
- Health proof route/query returns expected redaction.

---

### 04 Integration Failure Visibility

#### Objective

Implement the canonical SH-037 `recordIntegrationFailure` command and protected failure query so provider-owning Modules can surface technical degradation without creating local generic failure tables.

#### Observable Result

- A source Module/provider adapter can submit a normalized failure and receive an operational receipt.
- The same idempotent command retry replays the original result.
- A distinct provider attempt remains a distinct occurrence according to the accepted schema.
- Authorized operators can query failures by owner/provider/operation/request/source/time.
- Source business state is untouched.

#### Cluster Build-Plan Link

CL-09 Phase 1 Feature 02; later exercised by Features 06, 07, 11, and Cluster Feature 11/12.

#### Dependencies

- Features 01–03.
- Feature 02 approved persistence/repository if DB-backed.
- Provider-owning Module supplies normalized failure facts and retryability.
- `U-20` resolved if failure status/recovery lifecycle is persisted.
- `OBS-U-03` semantic failure identity resolved enough for idempotency.

#### In Scope

- public command DTO and validation.
- `normalizeOperationalFailure`.
- idempotency behavior.
- persistence through approved repository.
- metric/log side effects.
- protected `queryIntegrationFailures`.
- safe failure view DTO.
- optional source/incident linkage allowed by approved schema.

#### Out of Scope

- parsing raw Stripe/Cronofy/Mux/R2/etc. payloads.
- provider webhook verification/dedupe.
- source business transition.
- provider reconciliation.
- automatic incident opening.

#### Module-Owned Data

- `IntegrationFailure` if approved.
- optional approved `SystemEvent` supporting record if policy requires it.

#### Public Interfaces

- SH-037 `recordIntegrationFailure(command) -> IntegrationFailureReceipt`
- `queryIntegrationFailures(filters, viewer) -> Page<IntegrationFailureView>`

#### Shared Operations Used

| Operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| SH-044 `executeIdempotentCommand` | Platform | Failure command. | semantic failure command identity. | local dedupe table. |
| SH-034 `sanitizeTelemetryMetadata` | Observability/Audit | Before persistence. | failure safe fields. | raw error JSON. |
| SH-033 `writeStructuredLog` | Observability | command outcome. | safe failure summary. | failure-specific logger. |
| SH-036 `emitMetric` | Observability | failure counts/latency. | allowed dimensions. | local metrics. |
| SH-002 `authorizeResourceAction` | Role | detailed query. | view failure action facts. | local admin guard. |
| SH-030 `recordSensitiveAccess` | Audit | if detailed query exposes protected source refs. | sensitivity classification. | ops access table. |

#### Domain Logic

- Require source Module + operation + integration/provider key + safe normalized class/code + retryability + request/source correlation where available.
- Reject raw exception/provider objects.
- Retryability is supplied by source/provider owner; Observability does not reinterpret provider business semantics.
- If recovery is represented, follow the exact accepted `U-20` model; otherwise record a new operational observation rather than inventing a status update.
- Query DTO explicitly states it is operational evidence only.

#### Authorization / Compliance

- Ingestion is trusted-server only.
- Detailed query requires Role / Authority.
- Source references may be redacted according to viewer scope.
- No user-facing raw provider details.

#### Database / Transaction Behavior

- Idempotency claim + IntegrationFailure write in one safe transaction if using platform idempotency primitive.
- Unique constraints from Feature 02 enforced in DB.
- Bounded indexed queries only.

#### Events / Jobs

No event required by default. Failure may later be consumed by manual/approved incident correlation.

#### Provider Integration

None directly. Source provider adapter owns normalization before calling this command.

#### UI / Admin Surface

No full UI; a protected proof query/harness is sufficient. Feature 08 renders it.

#### Failure Behavior

- unsafe metadata -> invalid_input.
- provider-specific unmapped raw input -> invalid_input at this boundary; source adapter must translate.
- idempotency fingerprint mismatch -> conflict.
- persistence unavailable -> retryable_failure/unavailable.
- authorization denied -> forbidden without leaking hidden failure details.

#### Tests

- Unit: normalization, unsafe input rejection, safe DTO mapping.
- Integration: create/query/index filters.
- Idempotency: same command replay vs distinct occurrence.
- Security: redacted query.
- Ownership: test confirms no foreign business record is written.

#### Documentation Updates

If failure lifecycle/recovery semantics are settled here, update Module architecture and CL-09 `U-20` resolution.

#### Acceptance Criteria

1. At least two provider-owner fakes can call the same canonical failure command.
2. Failure records never contain raw provider payload fixtures.
3. Duplicate command retry does not duplicate one occurrence.
4. Source business table state is unchanged in integration test.

#### Exit Gate

- Unit/integration/idempotency/security tests pass.
- Query returns bounded redacted DTOs.
- No provider-specific mapping code exists in Observability.

---

### 05 Shared Queue Telemetry Visibility

#### Objective

Instrument the canonical shared queue runner so all async work can expose claim/attempt/heartbeat/retry/completion/dead-letter visibility without Observability taking ownership of job execution or business completion.

#### Observable Result

- A queued test job produces visible queue telemetry for claim, attempt, heartbeat, retry, and terminal result.
- Dead-lettered work is discoverable through the protected queue query.
- The source workflow remains authoritative for business completion.

#### Cluster Build-Plan Link

CL-09 Phase 1 Feature 02; foundational to Cluster Features 06/07/10/11/12 and Observability dashboard Feature 09.

#### Dependencies

- Features 01–04.
- Shared queue runner contract.
- Feature 02 QueueJob persistence if approved.
- `U-20` queue telemetry lifecycle/status semantics resolved for persistence.
- `U-21` is required only for final production provider adapter, not runner contract tests.

#### In Scope

- queue instrumentation adapter/hooks.
- SH-038 `recordQueueTelemetry` command.
- queue telemetry normalization/safety.
- `queryQueueJobs` protected query.
- dead-letter and retry visibility.
- stale/duplicate instrumentation protection.
- queue metrics.

#### Out of Scope

- queue client implementation.
- lease acquisition algorithm.
- retry scheduler/backoff engine.
- job payload persistence.
- source Module job state.
- source Module completion policy.

#### Module-Owned Data

- `QueueJob` operational visibility if approved.

#### Public Interfaces

- SH-038 `recordQueueTelemetry`
- `queryQueueJobs`

The shared runner calls the command; feature Modules normally do not hand-roll telemetry calls.

#### Shared Operations Used

- SH-047 `enqueueReliableJob` — shared queue owner; exercised by test job.
- SH-048 `executeRetryWithBackoff` — shared queue/platform.
- SH-038 `recordQueueTelemetry` — Observability/queue instrumentation.
- SH-036 `emitMetric` — queue depth/retry/duration/dead-letter.
- SH-033 `writeStructuredLog`.
- SH-034 `sanitizeTelemetryMetadata`.
- SH-002 `authorizeResourceAction` for queue detail query.

Prohibited duplicate: per-Module queue telemetry table, manual retry loop, in-module dead-letter engine.

#### Domain Logic

- Store/reference job type and source workflow reference, not full payload.
- Queue completion means runner completion, not business workflow success.
- Retryability and permanent/manual-review classification come from job owner/adapter.
- Stale heartbeat cannot overwrite a terminal operational state if approved model is mutable.
- Duplicate runner callback for the same telemetry observation is idempotent.

#### Authorization / Compliance

- Queue ingestion accepts only trusted runner context.
- Detailed queue view protected by Role / Authority.
- Payload/arguments not exposed to ops view unless separately safe and approved.

#### Database / Transaction Behavior

Follow approved QueueJob schema constraints. Use atomic compare/update or event append design as accepted. Do not solve races in memory.

#### Events / Jobs

A test/dummy shared queue job is permitted solely to prove instrumentation. No new business worker.

#### Provider Integration

Production queue adapter is shared platform responsibility. Observability receives instrumentation independent of provider.

#### UI / Admin Surface

No full dashboard; protected query proof only.

#### Failure Behavior

- telemetry persistence failure -> runner follows approved non-recursive fallback policy; it must not incorrectly fail the business job unless telemetry durability is a stated job-owner requirement.
- invalid transition observation -> typed telemetry rejection + safe diagnostic.
- queue provider unavailable -> shared queue health degrades; Observability does not invent job success.

#### Tests

- Runner contract: claim/attempt/heartbeat/retry/terminal/dead-letter instrumentation.
- Duplicate event tests.
- Stale heartbeat / terminal ordering tests.
- Security/redaction tests.
- Ownership test using a domain job fake with independent authoritative status.

#### Documentation Updates

Record queue runtime adapter when `U-21` is selected; no Module architecture change needed if only adapter selection changes within approved port.

#### Acceptance Criteria

1. One queue runner instrumentation path works for multiple job owners.
2. No job payload is persisted in operational visibility tests.
3. Dead-lettered test job is queryable.
4. Source workflow status remains owner-controlled.

#### Exit Gate

- Queue contract/idempotency/concurrency tests pass.
- No feature-local queue telemetry implementation exists.
- `queryQueueJobs` returns safe bounded DTOs.

---

### 06 Operational Query and Trace Correlation Surface

#### Objective

Provide the stable protected query boundary that operators and later UI use to correlate failures, queue work, system events, health, and source references without direct foreign database access.

#### Observable Result

- Authorized operator can search bounded failure and queue views.
- Given a request/correlation ID, the system returns a safe operational trace with linked operational records and safe source links/references.
- Missing source owner data is represented as unavailable rather than bypassed via Prisma.

#### Cluster Build-Plan Link

Completes query/correlation aspects of CL-09 Phase 1 Feature 02 and prepares CL-09 Phase 4 Feature 09.

#### Dependencies

- Features 01–05.
- approved persistence for any DB-backed source queried.
- Role / Authority.
- Audit sensitive-access contract.
- owner-specific link/query contracts where source detail is needed.

#### In Scope

- `correlateOperationalTrace`.
- bounded query filter objects.
- pagination/time-window enforcement.
- safe source reference resolver/link contract — link/reference only, not universal cross-domain data loader.
- operational view mappers.
- detailed versus summary DTOs.
- authorization/redaction integration.

#### Out of Scope

- admin dashboard layout.
- direct source business record hydration.
- incident grouping.
- provider reconciliation.
- search across raw logs from arbitrary provider unless provider port explicitly supports it.

#### Module-Owned Data

Read-only over approved Observability records and runtime health/provider references.

#### Public Interfaces

- `queryIntegrationFailures`
- `queryQueueJobs`
- `querySystemEvents` if approved
- `getOperationalHealth`
- `correlateOperationalTrace`

#### Shared Operations Used

- SH-002 `authorizeResourceAction`
- SH-030 `recordSensitiveAccess`
- SH-003 `queryOwnerFacts` only where an approved owner-specific DTO is needed; because canonical status is Proposed Ruling, use concrete owner public interface where available.
- SH-033 `writeStructuredLog`
- SH-036 `emitMetric`

Prohibited duplicate: universal polymorphic repository, raw Prisma exposure, unrestricted provider-log browser.

#### Domain Logic

- Require bounded time ranges and pagination.
- Correlation starts from operational IDs/request/source refs, not from arbitrary data warehouse search.
- If source owner cannot supply a safe summary/link, show “source unavailable/not authorized”; do not direct-query its table.
- Query result includes evidence/reference that it is operational, not business truth.

#### Authorization / Compliance

- All detailed queries protected.
- Field-level redaction according to action/sensitivity.
- Protected reveal triggers SH-030 `recordSensitiveAccess`.
- Existence of sensitive source record must not be leaked to unauthorized caller.

#### Database / Transaction Behavior

Read-only bounded indexed queries. No cross-Module joins that create runtime ownership coupling.

#### Events / Jobs

None.

#### Provider Integration

Optional read-only provider references through Observability-owned ports only; no raw unbounded provider query in MVP.

#### UI / Admin Surface

Optional minimal admin proof page is allowed if needed to prove query authorization; full UX remains Feature 08.

#### Failure Behavior

- query too broad -> validation denial requiring narrower filters.
- unauthorized -> forbidden/redacted result.
- source owner unavailable -> partial trace with explicit unavailable link.
- provider/log backend unavailable -> explicit unavailable/degraded section, not false empty result.

#### Tests

- Unit: filter bounds, DTO redaction, trace correlation.
- Integration: query indexes/pagination.
- Contract: owner-link fake unavailable/authorized behavior.
- Security: target existence leakage tests.
- Audit: sensitive reveal writes access proof.

#### Documentation Updates

Document stable query contracts for dashboard consumers.

#### Acceptance Criteria

1. Trace correlation works from one request across at least failure + queue + health/test operational signals.
2. No foreign Prisma query is used.
3. Sensitive detail requires authorization and is audit-recorded.
4. Query bounds prevent unbounded scans.

#### Exit Gate

- Contract/security/integration tests pass.
- Public query DTOs are stable and provider/Prisma neutral.
- Dashboard feature can be built without direct repository access.

---

## Phase 3 — Incident and Operator Surface

### 07 Ops Incident Lifecycle and Correlation

#### Objective

Implement the approved `OpsIncident` lifecycle and SH-040 `correlateOpsIncident` behavior without turning incidents into business remediation or compliance holds.

#### Observable Result

- Authorized operator can open an incident from selected operational signals.
- Incident updates obey the approved lifecycle and optimistic concurrency.
- Operator can link failures/queue/system/health references and explain grouping.
- Resolving an incident leaves source business/provider state unchanged.

#### Cluster Build-Plan Link

CL-09 Phase 4 Feature 09 **Ops Incident, Failure, Queue, and Health Dashboard**.

#### Dependencies

- Features 01–06.
- Explicit resolution of `U-20` for incident status/severity/transitions.
- `U-22` must be resolved only for automated grouping/alerts; manual incident flow may proceed if the approved lifecycle permits it.
- Role / Authority.
- shared concurrency/idempotency primitives.
- Feature 02 OpsIncident repository.

#### In Scope

- incident domain policy/state machine exactly as approved.
- `openOpsIncident`.
- `updateOpsIncident`.
- `queryOpsIncidents` / `getOpsIncident`.
- signal association/correlation.
- explainable grouping rationale.
- assignment/mitigation/resolution only if included in approved model.
- audit of important operator transitions where policy requires.

#### Out of Scope

- automatic incident thresholds if `U-22` unresolved.
- source business repair.
- provider reconciliation.
- ComplianceHold creation as an automatic side effect unless a separate owning workflow explicitly requests it.
- moderation case creation.

#### Module-Owned Data

- `OpsIncident` and approved associations only.

#### Public Interfaces

- SH-040 `correlateOpsIncident`
- `openOpsIncident`
- `updateOpsIncident`
- `getOpsIncident`
- `queryOpsIncidents`

#### Shared Operations Used

- SH-002 `authorizeResourceAction`
- SH-044 `executeIdempotentCommand`
- SH-052 `withOptimisticConcurrency`
- SH-051 `acquireAggregateLock` if approved conflict scenarios require it
- SH-053 `transitionLifecycleState`
- SH-029 `appendAuditEvent`
- SH-033 `writeStructuredLog`
- SH-036 `emitMetric`
- SH-041 `requestNotification` only if alert policy is approved

Prohibited duplicate: local incident systems in provider/business Modules.

#### Domain Logic

- Incident grouping uses operational signal IDs/references and deterministic rationale.
- Incident state is operational response state only.
- Resolution cannot call source Module mutation directly as a hidden side effect.
- Any remediation link is an operator handoff to the source owner.
- Reopen/terminal behavior follows accepted state graph exactly.

#### Authorization / Compliance

- Operators need explicit ops action permission.
- Sensitive signal details remain redacted or owner-gated.
- Admin role alone does not imply unrestricted PHI/finance/resume/message access.

#### Database / Transaction Behavior

- command idempotency + incident create in one transaction.
- optimistic version/CAS for updates.
- associations written transactionally with incident command where required.
- indexes support status/severity/updated time if those fields are approved.

#### Events / Jobs

- No automatic correlation worker unless `U-22` is accepted.
- Domain events only if an actual consumer requires incident-open/resolved facts; event names defined in the feature spec and architecture updated if introduced.

#### Provider Integration

None directly.

#### UI / Admin Surface

No complete dashboard yet; minimal incident command/query proof surface acceptable.

#### Failure Behavior

- architecture status/severity unresolved -> STOP.
- stale incident version -> conflict + current version.
- invalid transition -> typed invalid_state.
- missing linked signal -> reject or allow external reference only per approved contract.
- source owner unavailable -> incident remains valid; source link shows unavailable.

#### Tests

- State-transition unit tests for every approved transition.
- Concurrency: simultaneous update/resolve/reopen races as applicable.
- Idempotent incident create/update replay.
- Security/redaction.
- Ownership: incident resolve does not mutate source fixtures.

#### Documentation Updates

Mandatory when `U-20` is resolved: update Module architecture lifecycle section and CL-09 decision register.

#### Acceptance Criteria

1. Every allowed/denied transition is explicitly tested.
2. Stale writes cannot silently win.
3. Incident resolution does not change source business state.
4. Grouped signals remain operational references.

#### Exit Gate

- Lifecycle/concurrency/security tests pass.
- `U-20` resolution is documented.
- Automatic thresholds remain disabled unless `U-22` is separately approved.

---

### 08 Ops Incident, Failure, Queue, and Health Dashboard

#### Objective

Deliver the protected operator surface required by CL-09 Feature 09 using only Observability public queries/commands and owner-safe links.

#### Observable Result

Operators can:

- view component health;
- search recent/unresolved integration failures;
- inspect queue attempts/retries/dead-letter state;
- correlate request/source references;
- view/manage approved incident state;
- request an approved operational alert through Notification.

#### Cluster Build-Plan Link

Directly implements the Observability portion of CL-09 Phase 4 Feature 09.

#### Dependencies

- Features 03–07.
- Notification public request contract.
- Role / Authority.
- Audit sensitive-access contract.
- `U-22` only if automatic alerts are desired; manual policy-approved alerts can proceed if recipients/trigger are approved.

#### In Scope

- ops dashboard route/screen.
- health summary cards/list.
- failure list/detail.
- queue list/detail.
- incident list/detail if approved.
- request trace view.
- safe source links.
- manual operator actions through Module commands.
- notification intent handoff.

#### Out of Scope

- generic platform admin dashboard shell beyond this Module.
- source business remediation UI.
- raw logs/stack traces exposed without redaction.
- neighboring Module dashboards.
- provider control consoles.

#### Module-Owned Data

Read/write only through public Observability interfaces. UI must not import repositories or Prisma clients.

#### Public Interfaces

Consumes:

- `queryIntegrationFailures`
- `queryQueueJobs`
- `getOperationalHealth`
- `correlateOperationalTrace`
- incident queries/commands if approved

#### Shared Operations Used

- SH-002 `authorizeResourceAction`
- SH-030 `recordSensitiveAccess`
- SH-041 `requestNotification`
- SH-033 `writeStructuredLog`
- SH-036 `emitMetric`

Prohibited duplicate: direct table query from UI/server component, direct SES/SMS/push, UI-level authorization booleans.

#### Domain Logic

- Health state must distinguish degraded/unavailable from healthy.
- Filters are bounded and server-validated.
- Failure detail emphasizes operational evidence, retryability supplied by owner, and source links.
- Queue detail explicitly labels runner completion versus source workflow truth.
- Incident detail explicitly labels incident resolution as operational only.
- Automatic incident creation/alerting remains off unless approved.

#### Authorization / Compliance

- Route protection + server action/query authorization.
- Sensitive detail hidden by default.
- Reveal/export action separately authorized and access-audited.
- Public user cannot infer internal incident/provider details.

#### Database / Transaction Behavior

UI never accesses DB directly. All mutations through application/public command transaction behavior already defined.

#### Events / Jobs

- Optional manual/approved alert -> SH-041 `requestNotification` with idempotency key.
- No direct provider dispatch.

#### Provider Integration

None from UI. Sentry/logging/metrics remain behind Module adapters.

#### UI / Admin Surface

This feature owns the actual protected ops UI. Use root UI standards. Required states:

- loading;
- empty/no recent failures;
- degraded/unavailable component;
- unauthorized/forbidden;
- stale incident conflict;
- provider/reference unavailable;
- retry/dead-letter detail;
- redacted sensitive field state.

#### Failure Behavior

- backend detail unavailable -> show explicit unavailable state.
- source owner unavailable -> preserve operational record and mark source link unavailable.
- stale incident update -> show conflict/refresh.
- notification request fails -> incident/source state remains unchanged; show retryable delivery failure.

#### Tests

- Component/UI tests for health/failure/queue/incident states.
- Route/action authorization.
- Redaction and sensitive-access audit completeness.
- Integration: dashboard uses public query interfaces only.
- E2E: worker/provider failure -> failure view -> incident -> manual notification request.

#### Documentation Updates

Record UI routes/components in UI registry if the project maintains one. Update progress tracker.

#### Acceptance Criteria

1. Operators can trace at least one test provider/worker failure end-to-end.
2. UI contains no Prisma/provider client imports.
3. Sensitive detail is protected and access-audited.
4. Notification delivery uses Notification only.
5. Incident state never changes source business state.

#### Exit Gate

- UI/integration/security/E2E tests pass.
- The CL-09 Feature 09 Observability requirements are demonstrably satisfied.
- No unresolved auto-threshold behavior is enabled.

---

## Phase 4 — Privacy and Cross-Module Contract Proof

### 09 Observability Privacy, Retention, and Export Executor

#### Objective

Make Observability participate correctly in Privacy-owned subject-data workflows without creating local privacy orchestration or inventing retention policy.

#### Observable Result

A Privacy test workflow can:

- discover Observability-held subject-linked data;
- request owner retention facts;
- execute approved erase/anonymize/retain/export dispositions;
- receive explicit provider partial-failure results;
- preserve approved retained operational/security evidence without unnecessary personal fields.

#### Cluster Build-Plan Link

Implements the Observability portion of CL-09 Phase 5 Feature 10 **CL-09 Privacy, Retention, and Export Executors**.

#### Dependencies

- Features 02–08 as applicable.
- Privacy public protocol.
- Explicit resolution of `U-24` for target vocabulary and production retention behavior.
- provider deletion/retention capability for Sentry/logging/metrics if the approved design requires provider-side deletion.
- Shared queue for Privacy-executed async work.

#### In Scope

- SH-096 `enumerateSubjectData` implementation for Observability-owned records/references.
- SH-097 `evaluateRetentionRequirement` implementation returning owner facts.
- SH-095 `executePrivacyInstruction` implementation.
- export serializer if Privacy requires one.
- field-level anonymization mapping.
- provider deletion/revocation through Observability-owned adapter only when instructed/approved.
- explicit partial completion results.

#### Out of Scope

- `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption` ownership.
- legal retention duration invention.
- direct Privacy mutation of Observability tables.
- deleting another Module's provider resources.

#### Module-Owned Data

Approved Observability records and approved provider references only.

#### Public Interfaces

Implements Privacy-defined:

- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement`
- SH-095 `executePrivacyInstruction`
- export serializer

#### Shared Operations Used

- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement`
- SH-095 `executePrivacyInstruction`
- SH-098 `anonymizePersonalFields`
- SH-047 `enqueueReliableJob`
- SH-048 `executeRetryWithBackoff`
- SH-029 `appendAuditEvent` if Privacy/audit policy requires execution proof
- SH-037 `recordIntegrationFailure` for provider deletion failure without replacing Privacy job truth

Prohibited duplicate: local PrivacyRequest flow, local exemption table, ad hoc delete cron.

#### Domain Logic

- Enumerate only data actually owned/controlled by Observability.
- Return supported disposition per record/provider reference.
- Retention fact must cite approved security/operational basis; Privacy decides/records exemption.
- Anonymize nonessential personal identifiers when allowed.
- Provider deletion failure is returned as retryable/terminal/retained result; Privacy determines partial job outcome.
- Do not use `DataErasureTargetType.other` as a hidden production mapping if canonical target vocabulary is still missing.

#### Authorization / Compliance

- Executor callable only by authenticated/authorized Privacy orchestration, not ordinary users.
- No hard delete of approved retention-locked evidence.
- No claim of legal erasure if external provider resource remains where deletion was required.

#### Database / Transaction Behavior

- Owner-local data mutations in transaction per target/disposition.
- Idempotent replay for repeated Privacy instruction.
- Provider side effect uses idempotent/retryable adapter pattern.

#### Events / Jobs

- Privacy orchestration owns job sequencing.
- Long-running provider deletion may be enqueued via shared queue with Privacy job/target correlation.

#### Provider Integration

Only Observability-owned telemetry providers. Deletion/retention capability must be documented per provider adapter.

#### UI / Admin Surface

None required.

#### Failure Behavior

- `U-24` unresolved -> STOP production behavior; contract tests may use approved test vocabulary only.
- unknown retention basis -> return manual-review/blocked result; do not invent exemption.
- provider unavailable -> retryable partial result.
- provider cannot delete due to approved retention/technical limitation -> explicit retained/terminal result with safe evidence.

#### Tests

- Privacy contract tests.
- Enumeration completeness.
- erase/anonymize/retain/export fixtures.
- idempotent replay.
- provider deletion partial failure.
- security: ordinary client cannot invoke executor.

#### Documentation Updates

Mandatory when `U-24` resolved: Module architecture privacy section, CL-09 decision register, Privacy target vocabulary references.

#### Acceptance Criteria

1. No local Privacy lifecycle truth exists.
2. Privacy can discover and execute against every approved Observability target type.
3. Retention is evidence-based and Privacy-owned.
4. Provider partial failure is explicit.
5. Tests prove unnecessary identifiers are removed/anonymized when instructed.

#### Exit Gate

- `U-24` resolution is documented for production.
- Privacy contract/integration/security tests pass.
- No silent `other` target mapping remains.

---

### 10 Cross-Module Operational Signal Integration

#### Objective

Replace contract fakes with real launch-critical owner integrations and prove that provider/worker failures flow into Observability without transferring source truth.

#### Observable Result

Production-equivalent tests prove normalized operational signals from launch-critical Modules reach Observability and remain separable from source status/provider-event truth.

At minimum, integrations should cover representative paths from:

- Payment / Payout / Tax;
- Booking & Calendar;
- Search / Public Visibility;
- Media / File Access;
- Notification;
- at least one video/digital/provider-backed Module if launch-critical;
- Track Subscription & Entitlement if subscription provider failure is launch-critical;
- CL-09 moderation/hold workers themselves.

#### Cluster Build-Plan Link

Implements the Observability portion of CL-09 Phase 5 Feature 11 **Cross-Cluster Integration Verification**.

#### Dependencies

- Features 01–09 as relevant.
- Published owner provider/failure/health contracts.
- Shared event/queue/outbox/inbox infrastructure.
- Identity/Role/Audit/Notification/Privacy production-equivalent contracts.

#### In Scope

- replace failure/health contract fakes one boundary at a time.
- instrument owner adapters/workers to call canonical SH-037 `recordIntegrationFailure`.
- register owner health checks.
- ensure shared queue runner telemetry works for real Module workers.
- exercise correlation IDs across process/provider boundaries.
- exercise provider failure simulations through owner adapters.
- verify provider-event dedupe remains owner-local.

#### Out of Scope

- modifying source business status logic.
- provider reconciliation implementation in Observability.
- direct foreign Prisma read/write fallback.
- new product features.

#### Module-Owned Data

Only Observability operational records from real integrated signals.

#### Public Interfaces

Verify real integration for:

- SH-032 `createRequestContext`
- SH-033 `writeStructuredLog`
- SH-035 `captureException`
- SH-036 `emitMetric`
- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`
- SH-039 `checkServiceHealth`
- operational queries
- SH-041 `requestNotification` for ops alert handoff
- Privacy executor contract

#### Shared Operations Used

- SH-059 `verifyProviderWebhookSignature` — source owner, not Observability.
- SH-060 `deduplicateProviderEvent` — source owner.
- SH-061 `translateProviderStatus` — source owner.
- SH-062 `reconcileProviderState` — source owner.
- SH-037 `recordIntegrationFailure` — Observability.
- SH-038 `recordQueueTelemetry` — Observability/shared runner.
- SH-046 `publishDomainEvent` / SH-045 `deduplicateDomainEvent` — where source owners emit operational facts through events.
- SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` — shared queue.
- SH-041 `requestNotification` — Notification.

Prohibited duplicate: any Observability implementation of provider signature/dedupe/reconciliation.

#### Domain Logic

- Owner adapter verifies/translates first, then submits normalized failure.
- Observability stores source Module + source ref + correlation, never source status replacement.
- Search indexing lag comes from Search-owned health/facts.
- Notification delivery failure remains NotificationDelivery truth plus Observability failure visibility.
- Calendar/payment processed-event status remains in provider-owner table.
- Queue runner terminal state remains distinct from workflow completion.

#### Authorization / Compliance

- Production actor/authority checks exercised for detailed ops views.
- Sensitive operational data redaction verified end-to-end.
- No privilege widening at cross-Module boundary.

#### Database / Transaction Behavior

No direct foreign writes. Owner command transaction and Observability operational write are separate truths; use outbox/queue where durable cross-process delivery is required.

#### Events / Jobs

- Exercise at least one outbox/inbox path if failure signal is event-delivered.
- Exercise retry/dead-letter for one integrated async signal.
- Confirm duplicate domain event does not duplicate consumer side effect.

#### Provider Integration

Provider failures are simulated through their owner Module adapter. Observability never directly calls that provider for the purpose of deciding source state.

#### UI / Admin Surface

Use Feature 08 dashboard to verify integrated data. Do not build source dashboards here.

#### Failure Behavior

- owner contract unavailable -> queue/retry or source-defined degraded behavior; never direct DB fallback.
- contract version mismatch -> fail fast/deployment block.
- provider failure signal cannot be persisted -> typed Observability failure plus source owner policy; never mutate source state to “failed because logging failed.”
- duplicate source event -> consumer inbox idempotency.

#### Tests

- Cross-Module contract suites.
- Provider failure simulation through owner adapters.
- Async outbox/inbox/idempotency tests.
- Queue telemetry integration.
- Security/redaction.
- E2E: source provider failure -> owner source state + Observability evidence stay distinct.

#### Documentation Updates

- dependency interface versions;
- progress tracker;
- Module architecture only if contract meaning changes.

#### Acceptance Criteria

1. Every launch-critical operational bridge uses a published owner contract/event.
2. No integration test uses direct foreign Prisma mutation.
3. At least one Payment/Calendar/Search/Media/Notification-style provider failure is visible in Observability while source truth remains owner-controlled.
4. Queue and correlation context survive the integrated path.
5. Provider dedupe rows remain with source owner.

#### Exit Gate

- Cross-Module contract and E2E tests pass.
- No temporary direct DB coupling exists.
- Cluster Feature 11 Observability proof is complete.

---

## Phase 5 — Production Hardening

### 11 Observability Security, Fault Injection, Concurrency, and Launch Hardening

#### Objective

Close launch-critical operational risk under concurrency, provider outages, queue failures, sensitive-data pressure, migration/backfill, privacy, and partial telemetry failure without adding new domain scope.

#### Observable Result

- Operators can diagnose representative production failures safely.
- Observability sinks can fail without recursive failure storms.
- Queue retry/dead-letter visibility is actionable.
- Incident transitions remain concurrency-safe.
- Privacy execution works under partial provider deletion.
- migrations/backfills are safe and reversible/forward-fixable.
- critical E2E journeys pass in production-equivalent conditions.

#### Cluster Build-Plan Link

Implements the Observability portion of CL-09 Phase 6 Feature 12 **CL-09 Security, Concurrency, Reconciliation, and Launch Hardening**.

#### Dependencies

Features 01–10 and all accepted architecture decisions needed by launched behaviors.

#### In Scope

- server-side security/authorization review.
- telemetry redaction regression suite.
- Sentry/logging/metrics outage fault injection.
- shared queue lease/retry/dead-letter/replay verification from Observability perspective.
- failure-record idempotency and query performance.
- incident concurrency/replay if incident lifecycle launched.
- health timeout/circuit/degraded behavior.
- operational query/index load tests.
- migration/backfill dry run.
- Privacy executor/retention verification.
- ops dashboard E2E.
- launch runbook inputs such as health checks, dead-letter visibility, failure query usage, without inventing operational policy not in architecture.

#### Out of Scope

- new provider selections unrelated to launch.
- new automatic incident thresholds if `U-22` unresolved.
- new retention periods if `U-24` unresolved.
- provider reconciliation implementation belonging to source owners.
- repeat-infringer/moderation/legal features outside Observability.

#### Module-Owned Data

All approved Observability records and operational adapters.

#### Public Interfaces

All Module public interfaces are contract-regression tested.

#### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`
- SH-002 `authorizeResourceAction`
- SH-014 `requireStepUpForSensitiveAction` where approved
- SH-032 `createRequestContext`
- SH-034 `sanitizeTelemetryMetadata`
- SH-035 `captureException`
- SH-036 `emitMetric`
- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`
- SH-039 `checkServiceHealth`
- SH-044 `executeIdempotentCommand`
- SH-046 `publishDomainEvent` / SH-045 `deduplicateDomainEvent` where used
- SH-047 `enqueueReliableJob`
- SH-048 `executeRetryWithBackoff`
- SH-051 `acquireAggregateLock`
- SH-052 `withOptimisticConcurrency`
- SH-053 `transitionLifecycleState`
- SH-029 `appendAuditEvent`
- SH-030 `recordSensitiveAccess`
- SH-041 `requestNotification`
- Privacy owner/executor operations

No local substitute is permitted for any of these.

#### Domain Logic

- Confirm no operational record can be interpreted as source business status.
- Confirm failure/recovery behavior cannot write provider dedupe truth.
- Confirm incident close does not repair/close source records.
- Confirm queue completion and source completion remain distinct in UI/API.
- Confirm public health never leaks internals.
- Confirm high-cardinality metric protections under real/test load.

#### Authorization / Compliance

- Full route/action permission matrix.
- Sensitive diagnostic access audited.
- Step-up only where approved.
- Privacy/retention rules tested.
- no admin/support blanket access to PHI/finance/resume/private messages via ops tooling.

#### Database / Transaction Behavior

- concurrency/load tests for failure/queue/incident records.
- index/query plan review for common filters.
- migration dry run against production-like DB.
- destructive-change safety and rollback/forward-fix plan.
- backfill jobs use shared queue, idempotency, checkpoints, and telemetry.

#### Events / Jobs

- queue retry/dead-letter/replay fault injection.
- outbox/inbox duplicate delivery where used.
- monitor workers tested under owner dependency outage.
- no automatic incident worker unless policy approved.

#### Provider Integration

- Sentry outage.
- logging sink outage.
- metrics sink outage.
- source provider outages simulated through source owners, not Observability direct clients.
- provider reconciliation tested only as source-owner responsibility with resulting failure visibility.

#### UI / Admin Surface

- dashboard performance and security.
- safe empty/degraded/unavailable states.
- stale incident conflict handling.
- dead-letter actionable view.

#### Failure Behavior

- telemetry provider outage -> degraded state + bounded fallback.
- DB unavailable -> typed unavailable/retryable result; no fabricated persistence.
- queue dead-letter -> visible/actionable, source truth unchanged.
- sensitive redaction failure -> fail closed for emission.
- contract mismatch -> deployment/test failure, no fallback to direct DB.
- privacy provider deletion partial -> explicit partial result.

#### Tests

- full unit/integration/contract suite.
- authorization/security suite.
- sensitive telemetry fixtures.
- idempotency/concurrency/load.
- provider sink fault injection.
- source provider fault injection through owner Modules.
- queue retry/dead-letter/replay.
- Privacy retention/erasure.
- Playwright ops E2E.
- schema/migration dry run and rollback/forward-fix verification.

#### Documentation Updates

- progress tracker.
- completion report.
- runbook/operational docs if project context includes them.
- architecture only when a binding decision changed.
- library/provider docs if final adapters/config were selected.

#### Acceptance Criteria

1. No launch path relies on unresolved persistence/status/privacy/alert architecture.
2. Operational providers can fail without recursive crash loops.
3. All detailed diagnostics are authorized/redacted.
4. Queue failures/dead letters are visible and source status remains separate.
5. Incident concurrency is safe if incidents are launched.
6. Privacy behavior is approved and tested.
7. Production queries perform within project-defined thresholds on representative data.
8. Critical E2E journeys pass.

#### Exit Gate

The Observability / Ops Module is launch-ready only when:

1. all previous Module feature gates are green;
2. CL-09 Feature 12 prerequisites are satisfied;
3. no launched behavior depends on `U-19`/`U-20`/`U-22`/`U-24` without explicit accepted resolution;
4. migrations are reviewed and tested on production-like data;
5. telemetry-safety regression fixtures pass;
6. failure/queue/incident idempotency/concurrency tests pass;
7. provider sink outages and source-provider outages are diagnosable without ownership violations;
8. Privacy executor/retention behavior is approved and verified;
9. ops dashboard authorization/redaction/access-audit tests pass;
10. typecheck, lint, unit, integration, Playwright, schema validation, and production build commands pass;
11. progress tracker and completion report are updated.

---

# Module Integration Phase

Module Feature 10 is the dedicated integration phase. It proves that Observability works with its most important neighbors through contracts rather than database reach-through.

Required contract proofs:

1. **Identity / Role** — protected ops views/actions resolve authenticated actor and use SH-002 `authorizeResourceAction`.
2. **Audit** — sensitive diagnostic access uses SH-030 `recordSensitiveAccess`; important operator actions use SH-029 `appendAuditEvent` where policy requires it.
3. **Notification** — operational alerts use SH-041 `requestNotification`; no channel/provider code appears here.
4. **Payment / Calendar / Video / Media / Search / Notification / Subscription provider owners** — normalized failure signal enters Observability only after provider-owner verification/translation/dedupe boundaries.
5. **Shared queue** — queue telemetry comes from canonical runner instrumentation; job completion remains source-owned.
6. **Privacy** — Privacy orchestrates; Observability enumerates/executes only its own targets.
7. **Search** — indexing-lag/health is owner-provided; Observability never writes `SearchUpsertEvent`/Typesense.

A failed integration contract is fixed at the owner/public-interface boundary. It is never temporarily solved with direct foreign Prisma access.

---

# Module Hardening Phase

Module Feature 11 is the hardening phase. It focuses only on launch-relevant Observability risks:

- telemetry safety;
- authentication/authorization;
- sensitive diagnostic access;
- request/correlation integrity;
- provider sink outages;
- idempotent failure recording;
- queue duplicate/stale/dead-letter behavior;
- incident concurrency if launched;
- health timeouts and degraded states;
- privacy/retention execution;
- query/index performance;
- migration/backfill safety;
- cross-Module provider failure simulation;
- operational UI E2E.

It does not authorize any unresolved product/legal/operational policy.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Operational Foundation and Source-of-Truth Contract | 01 Request Context and Telemetry Safety; 02 Canonical Operational Persistence and Repository Contract |
| 2 | Core Operational Behavior | 03 Structured Logging, Error Capture, Metrics, and Health Registry; 04 Integration Failure Visibility; 05 Shared Queue Telemetry Visibility; 06 Operational Query and Trace Correlation Surface |
| 3 | Incident and Operator Surface | 07 Ops Incident Lifecycle and Correlation; 08 Ops Incident, Failure, Queue, and Health Dashboard |
| 4 | Privacy and Cross-Module Contract Proof | 09 Observability Privacy, Retention, and Export Executor; 10 Cross-Module Operational Signal Integration |
| 5 | Production Hardening | 11 Observability Security, Fault Injection, Concurrency, and Launch Hardening |

**Total numbered Module features: 11.**

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root project overview.
2. Read root architecture and code standards.
3. Read Canonical Shared Operations.
4. Read CL-09 architecture and build plan.
5. Read this Module architecture and plan.
6. Read public-interface sections for direct dependencies.
7. Confirm the previous Module feature exit gate and the governing Cluster feature gate/sequence.
8. Check whether a Proposed Ruling / Unresolved decision blocks the feature.
9. Write a concise implementation specification for **this feature only**.
10. Implement only this feature.
11. Run required quality checks.
12. Verify public contracts and ownership boundaries.
13. Update progress.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks and deferred work.
16. Do not begin the next feature unless the current exit gate passes or an explicit architecture exception is recorded.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent should produce a concise, current specification containing:

- Objective
- Observable result
- Cluster build-plan link
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

Do **not** pre-generate implementation specifications for all future features. The plan above defines scope; the coding specification is written immediately before the next feature using the latest accepted architecture and completion report.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Cluster build-plan feature supported
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
- Authorization/security verification
- Privacy/compliance verification where applicable
- Documentation updated
- Architecture decisions accepted/changed
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: **PASS / FAIL**

If the exit gate fails, identify the exact failing condition and do not mark the next feature ready.

---

# Final Quality Check

Before treating this Module as complete, verify:

1. Observability source truth has exactly one owner.
2. `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` persistence/status design is explicitly accepted rather than invented.
3. No neighboring Module truth was absorbed.
4. Canonical request context, logger, sanitizer, Sentry adapter, metrics client, queue telemetry, health, reliability primitives, Audit, Notification, and Privacy contracts are reused rather than duplicated.
5. `QueueJob` remains operational visibility only.
6. Provider verification/dedupe/status translation/reconciliation remain with provider owners.
7. Detailed operational queries use public/owner interfaces where foreign facts are needed, not cross-domain Prisma repositories.
8. Audit evidence, domain event truth, provider-event truth, and Observability truth remain distinct.
9. Privacy orchestration remains Privacy-owned.
10. Search remains a projection and is not written by Observability.
11. Incident state never becomes a ComplianceHold or business status.
12. Provider adapters remain secondary telemetry, not Workin Ants business truth.
13. Every numbered feature has tests and a passing exit gate.
14. Cluster sequence is preserved.
15. A coding agent can execute the next feature without inventing architecture.
