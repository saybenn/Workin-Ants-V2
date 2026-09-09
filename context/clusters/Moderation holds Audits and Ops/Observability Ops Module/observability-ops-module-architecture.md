# Observability / Ops Module Architecture

## 1. Module Header

| Item | Value |
| --- | --- |
| Module ID | `observability_ops` |
| Module name | Observability / Ops Module |
| Module type | `ops_capability` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-09` — Moderation, Holds, Audit & Ops |
| Document status | Implementation-grade Module architecture with explicit blocking Proposed Rulings / Unresolved decisions |
| Intended audience | Coding agents, developers, reviewers, maintainers, operators, security reviewers, privacy reviewers, and architecture owners |
| Relationship to root architecture | Subordinate to the root Workin Ants architecture, project overview, code standards, and canonical source-of-truth rules. This file may narrow Observability behavior but may not redefine platform ownership. |
| Relationship to Cluster architecture | Subordinate to the CL-09 `architecture.md`; this file defines only the Observability / Ops Module boundary and the exact contracts it owns or consumes. |
| Relationship to Cluster build plan | The Module implementation plan subdivides the Observability work required by CL-09 Features 01/02, 09, 10, 11, and 12 without changing Cluster sequencing. |
| Update rule | Update this file only when a binding decision changes Module ownership, persistence, lifecycle meaning, public contracts, shared-operation ownership, provider boundaries, privacy/retention behavior, or another architecture invariant. Build progress must not silently redefine this file. |

### Evidence status used here

- **Confirmed** — directly supported by the current Deep Module Registry, Cluster Registry, Prisma schema, Ubiquitous Language / Compliance Inventory, Canonical Shared Operations Architecture, or CL-09 architecture/build plan.
- **Proposed Ruling** — a concrete decision needed for coherent implementation but not yet accepted as authoritative.
- **Unresolved** — the evidence establishes a need or conflict but does not permit a safe implementation choice.

### Current architecture conflict

The registry and Ubiquitous Language assign `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` to this Module. The current Prisma schema contains none of those four models and contains no Observability-specific lifecycle/status/severity enums. CL-09 records this as `PR-CL09-05`, `U-19`, and `U-20`.

**Binding consequence:** conceptual ownership is confirmed, but coding agents do not have permission to invent or migrate the four persistence models, their fields, statuses, severity vocabularies, or transition graphs until the persistence and lifecycle decisions are explicitly accepted.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Observability / Ops makes technical execution visible across Workin Ants. It gives requests, workers, provider adapters, queues, indexing flows, uploads, calendar/payment integrations, notifications, and other runtime paths a consistent way to expose safe diagnostic context, normalized integration failures, queue execution visibility, health, metrics, exceptions, and operational incidents.

### Goal

Make failures diagnosable, correlatable, and actionable before launch and in production without allowing operational records or external monitoring tools to become business, compliance, audit, provider-event, or workflow source truth.

### What enters

The Module may accept or observe:

- request / trace / correlation context;
- safe actor or system identifiers already resolved by Identity & Access;
- source Module name and source-record references;
- operation names and bounded execution metadata;
- normalized provider or integration failure results supplied by the provider-owning Module;
- queue claim, attempt, heartbeat, duration, retry, completion, and dead-letter telemetry from the shared queue runner;
- owner-supplied component health checks;
- safe exception context;
- low-cardinality metric values and dimensions;
- operational signals used to correlate an incident;
- Privacy-owned instructions affecting Observability-held personal data, once the Privacy target vocabulary and retention policy are approved.

It must not accept arbitrary provider payloads, complete business objects, private message bodies, raw resumes, PHI payloads, payment/card data, secrets, OTPs, raw identity documents, raw biometrics, complete contract documents, or other unnecessary sensitive content merely because it would be useful for debugging.

### What leaves

The Module exposes or produces:

- trusted request/correlation context;
- safe structured logs;
- Sentry/error-monitoring submissions through one provider adapter;
- operational metrics;
- standardized component health results;
- normalized integration-failure evidence;
- queue execution visibility;
- operational query results and request/source correlation views;
- grouped operational incidents if/when `OpsIncident` persistence/lifecycle is approved;
- operational notification requests sent through Notification;
- owner-local privacy enumeration, retention facts, and execution results when Privacy invokes its canonical protocol.

### Capability transformation

```text
request / job / provider operation / owner health fact
        |
        v
create request context
        |
        +--> sanitize safe dimensions
        +--> structured log / metric / exception capture
        +--> normalize technical failure
        +--> record queue execution visibility
        +--> aggregate health
        +--> correlate operational signals
        |
        v
operator-safe diagnostics and operational evidence

Business source record remains with its owner throughout.
```

### Why this is a separate Deep Module

The platform needs one canonical operational rail. Without it, every Module is likely to create its own logger, failure table, queue dashboard, Sentry initialization, health route, correlation helper, incident system, retry diagnostics, or provider-error storage. Centralizing the operational mechanism prevents duplication while preserving domain truth with each source owner. This boundary is therefore a cross-cutting capability boundary, not a new business domain.

---

## 3. Owned Truth

### 3.1 Confirmed conceptual ownership

| Record / concept | Meaning | Ownership status | Current Prisma status |
| --- | --- | --- | --- |
| `SystemEvent` | An operational event that helps diagnose system behavior without becoming business truth. | Confirmed conceptual ownership from registry/glossary. | Missing. |
| `IntegrationFailure` | A normalized record that an external integration, worker, or provider operation failed or degraded. | Confirmed conceptual ownership; provider-failure tracking is explicitly assigned here. | Missing. |
| `QueueJob` | A visible operational record/projection of background job claim, attempts, retries, heartbeat, duration, completion, and dead-letter state. | Confirmed conceptual ownership of visibility only. | Missing. |
| `OpsIncident` | A grouped operational incident used for launch/support diagnosis and operational response. | Confirmed conceptual ownership. | Missing. |

### 3.2 Source-of-truth meaning

If canonical persistence is accepted:

- `SystemEvent` is source truth only for the fact that an **operational observation** was recorded.
- `IntegrationFailure` is source truth only for the normalized **technical integration failure / degradation evidence** recorded by Observability.
- `QueueJob` is source truth only for **operational queue execution visibility**; it is not the authoritative job payload, business completion status, or workflow lifecycle.
- `OpsIncident` is source truth only for **operational incident grouping, assignment, mitigation, and resolution**; it does not block or resolve business objects.

### 3.3 Enums and statuses owned

**None are currently confirmed in Prisma.**

No coding agent may create `SystemEventStatus`, `IntegrationFailureStatus`, `QueueJobStatus`, `OpsIncidentStatus`, `OpsSeverity`, or equivalent vocabulary without an accepted resolution of `U-20`.

The concepts “healthy / degraded / unavailable / delayed” are confirmed for the `checkServiceHealth` result contract, but they are not permission to create persistent Prisma enums until a schema ruling explicitly says so.

### 3.4 Lifecycles owned

The Module owns these lifecycle meanings only after persistence/status designs are accepted:

- integration failure occurrence / recovery visibility;
- queue telemetry visibility for claim, attempt, retry, terminal result, and dead-letter;
- operational incident lifecycle and grouping;
- any persisted operational system-event append behavior.

The Module does **not** own the lifecycle of the source business object, source job, provider event, webhook dedupe record, payment, calendar connection, search projection request, notification delivery, media processing record, privacy job, or any other observed workflow.

### 3.5 Domain events / ledgers owned

No business-domain event ledger is owned here. `SystemEvent` is operational evidence, not a replacement for domain event ledgers. The Module may publish carefully minimized operational facts when a consumer requires durable asynchronous reaction, but no canonical Observability event names are currently confirmed.

### 3.6 Projections owned

- `QueueJob`, if implemented, is explicitly an operational projection/visibility record.
- The health view is a runtime aggregation/projection of registered owner health checks.
- The ops dashboard is an admin projection over Observability-owned records and safe provider references.

### 3.7 Snapshots / proof owned

- Normalized integration-failure evidence is operational proof, not legal/compliance audit proof.
- External Sentry event IDs, logging-provider references, and metric-provider references may be stored only as secondary correlation references if approved; provider telemetry is not Workin Ants business truth.

### 3.8 Policies and invariants owned

Observability owns:

- safe telemetry acceptance and redaction policy, jointly constrained by Audit payload policy and domain sensitivity supplied by data owners;
- normalized operational failure shape and safe diagnostic fields;
- request/correlation propagation rules;
- structured logging field, level, environment, and cardinality policy;
- metrics naming and low-cardinality dimension policy;
- health registry aggregation and public-versus-internal disclosure policy;
- operational query filter, pagination, and redaction policy;
- incident grouping and operator workflow policy once `U-20`/`U-22` are resolved;
- telemetry-provider fallback behavior that avoids recursive observability failures.

---

## 4. Explicit Non-Ownership

This Module must not own or implement convenient substitutes for the following adjacent truths.

| Adjacent owner | Responsibility that stays outside Observability / Ops | Forbidden local substitute |
| --- | --- | --- |
| Identity & Access | Authentication, sessions, actor resolution, step-up assurance. | `currentUser`, `opsSession`, MFA/passkey/OTP logic. |
| Role / Authority | Permission interpretation for ops/admin actions. | `isOpsAdmin`, `canViewLogs`, local admin role tables/guards. |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog`, append-only audit proof, sensitive access proof. | `opsAuditLog`, generic access audit table, using SystemEvent as compliance proof. |
| Admin Review / Compliance Hold | Platform stop-sign truth and hold lifecycle. | `incidentBlock`, `outageHold`, operational blocked flags. |
| Content Moderation & Legal Notice | Reports, legal notices, cases, moderation decisions. | Treating incidents/provider failures as moderation cases. |
| Payment / Payout / Tax | Stripe/payment execution, KYC/tax/payout truth, `ProcessedStripeEvent`, reconciliation policy. | Global webhook log, payment status inference, marking payment event processed. |
| Booking & Calendar | Calendar provider integration, `ProcessedCalendarEvent`, booking/calendar state. | Calendar webhook dedupe or status translation. |
| Video Infrastructure | Video provider records, processed provider events, tokens/playback state. | Video webhook/dedupe truth. |
| Media / File Access | Upload validation, scanning, storage, object lifecycle, signed URLs, media processing truth. | R2 client, media failure state as operational truth only. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense projection execution, search reconciliation. | Typesense client, local index queue, search state mutation. |
| Notification | Notification persistence, channel routing, templates, email/SMS/push delivery, provider delivery status. | SES/SMS/push client or local notification queue. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, target orchestration, `DataRetentionExemption`. | Local privacy-request or retention-exemption tables. |
| Track Subscription & Entitlement | Subscription/entitlement truth, usage metering, provider events. | Plan/premium/entitlement flags in telemetry records. |
| Source business Modules generally | Order, Booking, Job, Offering, Gig, Message, Dispute, Verification, Healthcare, Reward, Prize, etc. | Cross-domain repository or operational fields used as source state. |
| Provider-owning Modules | Provider webhook verification, provider event dedupe, provider status translation, provider reconciliation. | One global webhook processor / processed-event table. |
| Shared queue infrastructure | Job payload persistence, lease execution primitive, retry scheduler, dead-letter mechanics. | Observability-owned queue execution framework. |

The registry phrase “all integration and workflow tables” must not be interpreted as unrestricted direct Prisma access. Cross-Module reads require owner queries, owner-emitted events, or explicitly approved projections.

---

## 5. Module Architecture Principles

1. Operational visibility must never replace business source truth.
2. Every request, job, and provider operation that participates in diagnostics should carry a correlation/request context.
3. Observability receives normalized operational facts; it does not ingest arbitrary provider payloads as domain types.
4. Provider-owning Modules decide provider status meaning, retryability, reconciliation, and business effects.
5. `QueueJob` visibility does not own the underlying workflow/job lifecycle.
6. `OpsIncident` does not block a user, payout, content item, order, job, or other resource; `ComplianceHold` is the reusable stop sign.
7. `SystemEvent` is not `AuditEvent`; operational evidence is not generic compliance proof.
8. Detailed ops reads are protected, minimized, redacted, and access-audited when sensitive.
9. Public health surfaces expose only minimal, non-sensitive status.
10. Telemetry payloads are allowlisted. Blacklist-only redaction is insufficient for sensitive contexts.
11. Metrics must avoid user-level or source-record high-cardinality dimensions unless explicitly approved.
12. Sentry, logging, and metrics providers are adapters/telemetry sources, not Workin Ants business truth.
13. Observability failures must not create recursive logging/failure loops.
14. A telemetry write failure must not automatically crash unrelated business work unless the source owner explicitly requires durable operational proof as a precondition.
15. Shared queue, retry, idempotency, locking, and outbox primitives are consumed, not rebuilt.
16. Incident automation and alert thresholds remain disabled until `U-22` is approved.
17. Persistent Observability models/statuses must not be invented before `PR-CL09-05`, `U-19`, and `U-20` are settled.
18. Privacy / Data Erasure orchestrates subject-data handling; Observability only enumerates and executes against its own data/provider resources.

---

## 6. Proposed Folder / Code Structure

Exact repository prefixes follow root `code-standards.md`. The structure below is the required relative ownership shape.

```text
<module-root>/observability-ops/
  domain/
    failure/
      failure-normalization.ts
      failure-policy.ts
    incident/
      incident-policy.ts              # only after U-20/U-22 are accepted
    telemetry-policy/
      metadata-policy.ts
      metric-policy.ts
      health-policy.ts

  application/
    ingestion/
      record-integration-failure.ts
      record-queue-telemetry.ts
      record-system-event.ts          # only if canonical persistence is approved
    queries/
      query-integration-failures.ts
      query-queue-jobs.ts
      get-operational-health.ts
      correlate-operational-trace.ts
      query-ops-incidents.ts           # only if approved
    incidents/
      open-ops-incident.ts             # only if approved
      update-ops-incident.ts           # only if approved

  public/
    commands.ts
    queries.ts
    contracts.ts
    health.ts
    privacy.ts

  infrastructure/
    repositories/                     # only for approved Prisma-backed Observability records
    logging/
      structured-logger.ts
    metrics/
      metrics-port.ts
      <provider-adapter>.ts            # provider choice unresolved
    sentry/
      error-monitoring-port.ts
      sentry-adapter.ts
    health/
      health-registry.ts
    queue-telemetry/
      queue-instrumentation-adapter.ts

  workers/
    stalled-queue-monitor.ts           # only after thresholds are approved
    indexing-lag-monitor.ts            # consumes Search health/public facts
    provider-health-monitor.ts         # consumes owner health contracts
    incident-correlation-worker.ts     # only after U-22 is approved

  privacy/
    enumerate-subject-data.ts
    evaluate-retention-requirement.ts
    execute-privacy-instruction.ts

  ui/admin/
    ops-dashboard/
    failure-detail/
    queue-detail/
    incident-detail/                   # only if incident persistence is approved

  tests/
    unit/
    contract/
    integration/
    authorization/
    privacy/
    providers/
    queue/
    e2e/

<shared-platform-root>/
  request-context/                    # canonical createRequestContext primitive
  queue-runner/                       # canonical enqueue/retry/lease/dead-letter execution
  idempotency/
  locking/
  outbox/
```

### Folder rules

- Do not create `utils/`, `helpers/`, `common/`, or generic `services/` dumping grounds.
- `request-context` belongs in shared platform infrastructure if root code standards use that location; Observability remains its canonical owner/co-owner.
- Shared queue execution stays outside `observability-ops`; only queue instrumentation/visibility belongs here.
- Provider adapters for Stripe, Cronofy, video, media, notification, search, verification, subscription, etc. stay with their owning Modules.
- `infrastructure/repositories/` must not exist until canonical persistence is accepted.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / admin UI | Protected operational views, bounded filters, safe status summaries, request/source links. | Business remediation workflows, foreign domain dashboards, unrestricted raw payload viewers. |
| Public contracts | Stable ingestion/query/health/privacy DTOs and error categories. | Prisma types, provider SDK types, foreign domain entities. |
| Application ingestion | Validate/sanitize operational input, invoke repositories/adapters, correlate request context. | Provider-specific status translation or business transitions. |
| Application queries | Authorized/redacted reads of Observability truth and health aggregation. | Direct foreign Prisma reads. |
| Domain failure policy | Normalized technical failure categories, safe diagnostic fields, incident eligibility input. | Payment/calendar/search/video business failure meaning. |
| Domain incident policy | Grouping, operator assignment/mitigation/resolution after approved lifecycle exists. | Compliance holds, moderation cases, business remediation. |
| Telemetry policy | Allowlist/redaction, log levels, metric dimensions, health disclosure. | Healthcare/financial/resume access decisions; those facts come from owners. |
| Repositories | Persist/query only approved Observability models. | Generic repository over other Modules. |
| Workers | Operational monitors, correlation, bounded aggregation. | Source business repair or provider reconciliation owned elsewhere. |
| Adapters | Sentry, logging, metrics adapters owned here; queue instrumentation adapter. | Stripe/Cronofy/Typesense/R2/video/notification provider adapters. |
| Privacy executor | Enumerate/retain/anonymize/erase Observability-held subject data under Privacy command. | `PrivacyRequest` orchestration or exemption truth. |

---

## 8. Data Model

### 8.1 Current executable state

The current Prisma schema has no `SystemEvent`, `IntegrationFailure`, `QueueJob`, or `OpsIncident` model. There is therefore no current Observability-owned Prisma repository that a coding agent may implement against.

`DataErasureTargetType` also has no explicit Observability-specific target values; `other` is not an approved substitute for production privacy behavior. This is part of `U-24`.

### 8.2 Proposed Ruling OBS-PR-01 — canonical persistence

This Module inherits `PR-CL09-05`:

> Persist the four registry/glossary-owned operational records in Workin Ants PostgreSQL/Prisma while treating Sentry/logging/metrics as secondary provider telemetry.

This is still a **Proposed Ruling**. Acceptance of the persistence direction does not by itself approve field names/statuses. A separate schema specification resolving `U-20` is required before migration.

### 8.3 Required semantic shape if persistence is approved

The following describes required meaning, not approved Prisma field names.

#### `SystemEvent`

**Purpose:** record a safe operational observation useful for diagnosis.

Required semantic categories:

- unique record identity;
- event/operation classification;
- source Module;
- optional source target type/ID reference;
- request/correlation/trace context;
- safe structured metadata;
- occurrence/creation timestamp;
- optional relation/reference to integration failure, queue job, or incident only if approved by schema design.

**Authoritative fields:** the operational fact, source reference, safe metadata, and correlation context.

**Lifecycle/status:** none confirmed. The natural meaning is append-style, but mutability/append-only enforcement is not yet ruled.

**Retention/privacy:** may contain personal identifiers indirectly through actor/source references; must participate in Privacy and telemetry minimization.

#### `IntegrationFailure`

**Purpose:** normalized technical failure/degradation evidence for a provider, integration, worker, or external dependency.

Required semantic categories:

- unique record identity;
- source Module and operation;
- provider/integration class;
- optional source record reference;
- request/correlation context;
- safe error classification/code, never raw secret-bearing payload;
- retryability classification supplied by the owner/provider adapter;
- attempt/timing information where relevant;
- failure occurrence time;
- recovery/resolution linkage only if the approved lifecycle requires it;
- optional incident linkage.

**Uniqueness/idempotency:** must distinguish a genuine repeated failure occurrence from caller retry of the same failure-record command. Exact semantic key is unresolved.

**Lifecycle/status:** unresolved under `U-20`.

**Retention/privacy:** avoid user data; source references may still be personal. Retention duration unresolved under `U-24`.

#### `QueueJob`

**Purpose:** operational visibility of work executed by shared queue infrastructure.

Required semantic categories:

- queue/runtime job identity;
- owner Module / job type;
- source workflow/job reference;
- request/correlation context;
- claim / attempt / heartbeat / duration / retry / terminal visibility;
- safe failure classification;
- dead-letter visibility;
- timestamps needed for stall/latency diagnosis.

**Authoritative boundary:** this record never stores or owns the source business completion meaning. Examples: `DataErasureJob`, `SearchUpsertEvent`, moderation enforcement runs, booking orchestration, media processing, or provider-reconciliation jobs remain their owners' truth.

**Lifecycle/status:** unresolved under `U-20`. Queue runtime semantics cannot be guessed from a provider choice.

**Concurrency-sensitive fields:** attempt/heartbeat/terminal telemetry must tolerate repeated instrumentation and runner retries without inventing business state.

**Retention/privacy:** job payloads must not be copied here; store references and safe metadata only.

#### `OpsIncident`

**Purpose:** group related operational signals for operator/support response.

Required semantic categories:

- incident identity;
- title/summary safe for ops use;
- severity only after approved vocabulary exists;
- assignment/ownership if approved;
- lifecycle state only after `U-20` approval;
- opened/updated/mitigated/resolved timestamps as required by the lifecycle;
- deterministic linkage to relevant `SystemEvent`, `IntegrationFailure`, `QueueJob`, health signal, Sentry reference, or source reference;
- correlation/causation context.

**Authoritative boundary:** resolving an incident never mutates or resolves source business/provider records.

**Concurrency-sensitive fields:** incident updates require optimistic concurrency or aggregate locking.

**Retention/privacy:** incident summaries must remain sanitized; sensitive source details are accessed through source owner interfaces and recorded through Audit where required.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 Binding current state

No Module-owned lifecycle enum is currently approved.

### 9.2 SystemEvent

```text
operational observation occurs
  -> validate / sanitize
  -> append or emit operational event
```

No status transition graph is approved. Do not add update/delete semantics merely for convenience.

### 9.3 IntegrationFailure

The architecture requires a way to distinguish failure visibility from recovery, but the exact persistence model is unresolved.

Prohibited shortcut:

```text
IntegrationFailure.status = success
  -> therefore Order / Booking / provider event is fixed
```

Recovery visibility, if represented, means only that the technical integration condition changed. Source owners remain responsible for reconciliation and business state.

### 9.4 QueueJob

Confirmed semantic progression for telemetry observation includes claim, attempt, heartbeat, retry, completion, and dead-letter signals. These are **operational concepts**, not approved persisted enum values.

The shared queue runner owns execution primitives. The source Module owns completion meaning. Observability may only report what the runner observed.

### 9.5 OpsIncident

The Canonical Shared Operations Architecture confirms `correlateOpsIncident` and mentions grouping, severity, assignment, mitigation, and resolution transitions. Exact statuses, reopen rules, automatic thresholds, and terminal semantics remain unresolved under `U-20` and `U-22`.

Until resolved:

- do not create an incident state machine;
- do not auto-open incidents;
- do not auto-send severe incident alerts based on invented thresholds;
- do not treat an incident as a `ComplianceHold`.

### 9.6 Transition owner and concurrency

If/when mutable incident/failure records exist, only Observability application commands may transition them. Use `withOptimisticConcurrency` and/or `acquireAggregateLock` according to the approved schema. No client or admin UI may write lifecycle columns directly.

---

## 10. Commands

The names below are the preferred stable Module boundary. A command marked **conditional** must not be implemented until its blocking architecture decision is accepted.

### 10.1 `recordSystemEvent` — conditional

**Purpose:** persist a safe operational observation when `SystemEvent` persistence is approved.

**Actor/context required:** trusted internal system/module caller; request context when available.

**Authoritative inputs:** event/operation classification, source Module, optional source reference, safe metadata, request/correlation context.

**Preconditions:** canonical persistence accepted; metadata sanitized; caller is trusted internal code; no prohibited payload classes.

**State written:** `SystemEvent` only.

**Shared operations consumed:** `createRequestContext`, `sanitizeTelemetryMetadata`; `executeIdempotentCommand` only if the accepted append semantics require it.

**Events/audit/notifications:** none automatically. A system event is already operational evidence; do not append Audit merely because telemetry was written.

**Idempotency:** distinct genuine observations must not be collapsed. If caller supplies a semantic idempotency key, replay rules must be explicit.

**Failure modes:** invalid metadata, unavailable persistence, payload rejected, idempotency conflict.

### 10.2 `recordIntegrationFailure`

**Purpose:** record normalized operational evidence that a provider, worker, integration, or dependency failed or degraded.

**Actor/context required:** trusted internal source Module/provider adapter/worker; request context where available.

**Authoritative inputs:** provider/integration identifier, operation, source Module, optional source reference, normalized safe diagnostics, retryability, attempt context, request ID/correlation ID, optional incident linkage.

**Preconditions:** provider/domain owner has already interpreted provider-specific failure enough to provide a normalized safe result; telemetry sanitization passes.

**State written:** `IntegrationFailure` if persistence is approved; otherwise the approved external-only operational mechanism defined by the architecture decision.

**Shared operations consumed:** `sanitizeTelemetryMetadata`, `createRequestContext`, `executeIdempotentCommand` where caller retry can duplicate the same record, `writeStructuredLog`, `emitMetric` as policy requires.

**Events/audit/notifications:** severe/incident linkage may eventually request Notification; no direct notification delivery. No provider dedupe writes.

**Idempotency:** caller retries of the same failure-record operation must replay the original receipt; separate provider attempts remain separate occurrences.

**Failure modes:** invalid source ref shape, unsafe metadata, persistence unavailable, idempotency conflict.

### 10.3 `recordQueueTelemetry`

**Purpose:** record or project shared queue execution visibility.

**Actor/context required:** shared queue runner/worker instrumentation, not public clients.

**Authoritative inputs:** queue job identity, owner Module, job type, source workflow reference, request/correlation context, attempt, claim/heartbeat/timing/retry/terminal observation, safe error classification.

**Preconditions:** telemetry originates from approved queue runtime instrumentation; no business payload copied.

**State written:** `QueueJob` operational visibility if approved; metrics/logs as configured.

**Shared operations consumed:** shared queue runner, `sanitizeTelemetryMetadata`, `emitMetric`; no local retry engine.

**Events/audit/notifications:** dead-letter or approved severe conditions may feed incident correlation/Notification through separate policy.

**Idempotency:** repeated instrumentation for the same runner event must not create contradictory operational state; exact uniqueness follows approved queue telemetry schema.

**Failure modes:** unsupported transition observation, stale heartbeat, telemetry persistence unavailable, unsafe metadata.

### 10.4 `registerHealthCheck`

**Purpose:** register an owner-supplied typed health check with the Observability health registry.

**Actor/context required:** application composition/bootstrap code.

**Authoritative inputs:** component key, owner Module, timeout, visibility classification, callback/port returning standardized health result.

**Preconditions:** owner defines what health means; check must not expose secrets or business payloads.

**State written:** runtime registry/configuration, not business state.

**Shared operations consumed:** `checkServiceHealth`, `sanitizeTelemetryMetadata`, `emitMetric`.

**Idempotency:** duplicate component keys are deterministic configuration conflicts.

**Failure modes:** duplicate key, invalid timeout, unsafe detail fields, check timeout.

### 10.5 `openOpsIncident` — conditional

**Purpose:** create an operator incident grouping after `OpsIncident` persistence/status/severity is approved.

**Actor/context required:** authorized operator or approved system automation; automation thresholds are separately blocked by `U-22`.

**Authoritative inputs:** safe summary, approved severity, initiating signals/references, request/correlation context, actor/system source.

**Preconditions:** `U-20` resolved; actor authorized; referenced signals exist or are valid external references; automatic creation only if `U-22` is approved.

**State written:** `OpsIncident` and approved association records/fields.

**Shared operations consumed:** `executeIdempotentCommand`, `withOptimisticConcurrency` / `acquireAggregateLock`, `appendAuditEvent` for important operator action where policy requires, `requestNotification` only under approved alert policy.

**Idempotency:** deterministic incident creation key when created from the same approved trigger; manual incidents use request idempotency.

**Failure modes:** duplicate/open incident conflict, stale signal references, authorization denial, unresolved severity policy.

### 10.6 `updateOpsIncident` — conditional

**Purpose:** assign, mitigate, annotate, transition, or resolve an approved incident lifecycle.

**Actor/context required:** authorized operator/system according to incident policy.

**Preconditions:** incident exists; expected version matches; transition is allowed by owner state machine.

**State written:** `OpsIncident` only plus audit/notification effects when required.

**Shared operations consumed:** `authorizeResourceAction`, `withOptimisticConcurrency`, `transitionLifecycleState`, `appendAuditEvent`, `requestNotification` where approved.

**Idempotency/concurrency:** optimistic version required; conflicting stale updates return typed conflict.

**Failure modes:** unauthorized, invalid transition, stale version, missing incident, persistence unavailable.

---

## 11. Queries / Decisions

### 11.1 `queryIntegrationFailures`

**Consumers:** admin ops dashboard, support tooling, integration owners.

**Input:** bounded filters such as source Module, provider/integration, operation, approved status if one exists, request/correlation ID, source reference, time window, pagination.

**Result:** redacted operational evidence/projection.

**Meaning:** returns Observability truth only. Consumers must not infer that the source business operation succeeded, failed permanently, reconciled, or is safe to retry solely from this result.

### 11.2 `queryQueueJobs`

**Consumers:** admin ops dashboard, async Module owners, support tooling.

**Input:** queue, job type, owner Module, source reference, operational state if approved, request ID, time window, pagination.

**Result:** operational queue visibility.

**Consumer must not infer:** that the source business workflow completed merely because queue execution completed.

### 11.3 `getOperationalHealth`

**Consumers:** deployment/readiness checks, admin ops dashboard, support tooling; optionally minimal public infrastructure endpoint.

**Input:** requested component scope and caller visibility level.

**Result:** standardized aggregated health facts from registered owner checks.

**Meaning:** health projection, not business readiness. `healthy` cannot be inferred as “all orders/payments/search are correct.”

### 11.4 `correlateOperationalTrace`

**Consumers:** authorized operators/support.

**Input:** request/correlation/trace ID, optional source reference and bounded time range.

**Result:** redacted correlation view over Observability-owned signals plus safe owner-provided links/references.

**Meaning:** diagnostic context; it must not directly fetch complete foreign business records through a universal repository.

### 11.5 `querySystemEvents` — conditional

Available only if `SystemEvent` persistence is approved. Returns redacted operational event truth. It does not return Audit evidence or domain event ledgers.

### 11.6 `queryOpsIncidents` / `getOpsIncident` — conditional

Available only after incident persistence/lifecycle is approved. Returns incident source truth and linked operational references. The consumer must not infer that linked source issues have been fixed because the incident is resolved.

### Decision reason patterns

Where a query or command returns a denied/unavailable result, use stable Module result categories rather than provider strings. Provider-native errors terminate at adapters.

---

## 12. Public Module Interface

### Confirmed canonical shared capabilities owned/co-owned here

- `createRequestContext`
- `writeStructuredLog`
- `sanitizeTelemetryMetadata`
- `captureException`
- `emitMetric`
- `recordIntegrationFailure`
- `recordQueueTelemetry`
- `checkServiceHealth`
- `correlateOpsIncident` — confirmed canonical operation, but persistent incident behavior remains blocked by `U-20`/`U-22`.

### Public commands

- `recordIntegrationFailure`
- `recordQueueTelemetry`
- `registerHealthCheck`
- `recordSystemEvent` — conditional on approved `SystemEvent` persistence
- `openOpsIncident` — conditional
- `updateOpsIncident` — conditional

### Public queries

- `queryIntegrationFailures` — requires approved persistence if the query is DB-backed
- `queryQueueJobs` — requires approved persistence if the query is DB-backed
- `getOperationalHealth`
- `correlateOperationalTrace`
- `querySystemEvents` — conditional
- `queryOpsIncidents` / `getOpsIncident` — conditional

### Emitted events

No canonical Observability domain event names are currently confirmed. Do not invent a public event namespace merely to mirror every log/failure write. Use the transactional outbox only when a durable consumer requirement is established and the event meaning is approved.

### Privacy executor

Implements the Privacy-owned protocol:

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- export serializer where applicable

Production implementation is blocked until `U-24` resolves target vocabulary and retention policy.

### Provider-facing interfaces owned here

- error monitoring port -> Sentry adapter;
- structured logging port -> provider choice unresolved;
- metrics port -> provider choice unresolved.

Shared queue runtime is not an Observability-owned provider interface; Observability instruments it.

---

## 13. Inbound Dependencies

| Owning Module / capability | Public operation/interface consumed | Why required | Minimum information needed | May block action? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | `resolveAuthenticatedActor` | Trust actor/system context for protected ops actions. | actor ID, platform context, assurance facts only as needed. | Yes for protected admin commands/queries. | Session/auth helpers. |
| Identity & Access | `requireStepUpForSensitiveAction` when approved policy requires | Additional assurance for high-risk diagnostic/export/admin action. | assurance result/session ref. | Yes. | MFA/passkey/OTP logic. |
| Role / Authority | `authorizeResourceAction` | Protect detailed failures, incidents, diagnostics, privacy executors. | actor, action, resource/scope facts. | Yes. | Local admin permission engine. |
| Audit / Event Ledger | `recordSensitiveAccess` | Record access to protected diagnostic data when required. | actor, target, action, sensitivity, access outcome, request ID. | Audit persistence may be required for sensitive access policy. | Access audit table. |
| Audit / Event Ledger | `appendAuditEvent` | Record important operator incident/admin actions when required. | actor/system, action, target, outcome, request ID, safe metadata. | Depends on owner workflow policy. | Generic audit logger. |
| Notification | `requestNotification` | Deliver approved severe operational alerts. | recipients/recipient strategy, template key, priority, safe variables, idempotency key. | Notification delivery itself does not change incident/source truth. | SES/SMS/push. |
| Privacy / Data Erasure | Privacy orchestration command/protocol | Execute approved subject-data disposition. | target, disposition, retention/exemption context, request/job ID. | Yes for privacy executor behavior. | Privacy lifecycle. |
| Source Modules | owner-emitted operational signal / owner facts / health check | Receive normalized failure/health/source reference without direct DB coupling. | source Module, operation, source ref, safe status/failure facts. | No to unrelated operations; a source owner may choose to require durable telemetry. | Foreign repositories. |
| Provider-owning Modules | normalized provider failure result; `translateProviderStatus` stays owner-side | Observability needs safe technical failure evidence. | normalized code/class, retryability, provider/integration key, source ref. | No domain decision here. | Provider status mappings. |
| Shared queue infrastructure | `enqueueReliableJob`, `executeRetryWithBackoff`, runner instrumentation | Execute Observability-owned monitor workers and produce queue telemetry. | job identity, payload refs, retry classification, correlation. | Yes for async monitor execution. | Queue engine/leases/dead-letter. |
| Shared persistence infrastructure | `executeIdempotentCommand`, `acquireAggregateLock`, `withOptimisticConcurrency`, `transitionLifecycleState` | Safe mutable operational commands when applicable. | semantic key/version/lock key. | Yes for conflicting mutations. | Local idempotency/locks. |
| Search / Public Visibility | owner health/projection-lag facts or approved query | Measure indexing lag without owning search execution. | backlog age/count, worker health, source version as needed. | No search mutation. | SearchUpsertEvent reads/writes unless owner API explicitly returns facts. |

---

## 14. Outbound Consumers and Effects

### Consumers

- all Modules and shared runtime consume request context, structured logging, metrics, exception capture, failure recording, queue telemetry, and health contracts;
- Payment, Calendar, Video, Search, Notification, Media, Subscription/Entitlement, Verification, and other provider-owning Modules use `recordIntegrationFailure` for generic operational visibility;
- all asynchronous Modules benefit from `recordQueueTelemetry` through shared queue instrumentation;
- admin/support/incident responders consume protected operational queries and the ops dashboard;
- Privacy consumes Observability subject-data enumeration/execution results;
- Audit consumes request context and may correlate operator actions, while preserving separate audit truth;
- Notification consumes safe alert requests, not raw telemetry payloads.

### Downstream effects

Observability may:

- request Notification delivery;
- append Audit evidence for operator actions or sensitive diagnostic access;
- publish approved operational facts through outbox if a durable consumer is established;
- enqueue Observability-owned monitors through shared queue infrastructure.

Observability must not directly mutate another Module's source state in response to a failure or incident.

---

## 15. Canonical Shared Operations Used

The current Canonical Shared Operations Architecture supplies canonical operation **names**, not permanent `SH-###` identifiers. Do not invent numeric IDs.

| Canonical operation | Meaning | Canonical owner | Classification | Why Observability uses it | Invocation point | Local policy retained here | Expected contract/result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Resolve provider session/system credential to trusted actor context. | Identity & Access | Platform capability | Protect ops/admin interfaces. | Protected entry points. | Which ops action/resource is being attempted. | trusted actor context. | `getCurrentUser`, `opsCurrentUser`, `requireOpsUser`. |
| `authorizeResourceAction` | Decide permission for named resource action. | Role / Authority | Cross-cutting capability | Protect diagnostics/incidents/privacy operations. | Before protected query/mutation. | Ops action vocabulary and resource facts. | allow/deny decision with reason/evidence. | `isOpsAdmin`, `opsGuard`, `canViewLogs`. |
| `requireStepUpForSensitiveAction` | Require fresh assurance for high-risk action. | Identity & Access | Platform security capability | Optional gate for sensitive exports or high-risk incident actions. | Only where approved security policy says so. | Which ops actions require step-up. | active assurance/session or denial. | local OTP/MFA. |
| `createRequestContext` | Propagate request/correlation/trace/environment/actor identifiers. | Observability / platform infrastructure | Platform primitive | Core correlation rail. | Request/job/provider entry. | Safe dimensions only. | typed immutable context. | `request-id.ts`, `correlation.ts`, per-module ALS stores. |
| `writeStructuredLog` | Emit safe machine-readable logs. | Observability / Ops | Platform capability | One logging rail. | Throughout requests/workers/adapters. | level/field naming and safe fields. | log receipt/no-throw operational result. | module loggers, ad hoc JSON console wrappers. |
| `sanitizeTelemetryMetadata` | Remove/reject sensitive content from telemetry/audit metadata. | Observability / Ops + Audit payload policy | Cross-cutting capability | Mandatory before persistence/transmission. | Every telemetry boundary. | allowlists, size/cardinality, safe serialization. | safe metadata or typed rejection. | `redactError`, `scrubLog`, one-off secret blacklist. |
| `captureException` | Send exception through monitoring provider. | Observability / Ops | Provider adapter | One Sentry adapter. | Unexpected exception boundary. | sampling/grouping/release/environment/safe tags. | safe provider reference/result. | direct `Sentry.init`, local Sentry clients. |
| `emitMetric` | Publish operational metrics through one client. | Observability / Ops | Platform capability | Metrics/health/queue/failure visibility. | Request/job/provider lifecycle points. | naming/cardinality/threshold ownership. | metric emission result. | `stats.ts`, module metrics clients. |
| `recordIntegrationFailure` | Persist normalized failure/degradation evidence. | Observability / Ops | Cross-cutting capability | Canonical provider/worker failure visibility. | After owner-normalized technical failure. | failure grouping, safe fields, retention. | operational failure receipt. | `integration_failures` tables elsewhere, `failureLogger`. |
| `recordQueueTelemetry` | Record queue claim/attempt/heartbeat/retry/terminal visibility. | Observability / Ops / queue infrastructure | Cross-cutting capability | One queue visibility rail. | Shared runner lifecycle hooks. | telemetry vocabulary and dashboard semantics. | queue telemetry receipt/projection. | local queue job ledgers/dashboards. |
| `checkServiceHealth` | Return standardized component health. | Observability coordinates; component owner supplies check | Cross-cutting capability | Aggregate deployment/ops health. | Health routes/dashboard. | timeouts, disclosure, aggregation. | healthy/degraded/unavailable/delayed result. | multiple health frameworks. |
| `correlateOpsIncident` | Group operational signals into incident. | Observability / Ops | Module-internal public ops interface | Incident grouping. | After manual/approved signal selection; automation only after U-22. | grouping/severity/operator workflow. | incident/correlation result. | local incident systems. |
| `executeIdempotentCommand` | Ensure retried command causes one effect and replays result. | Platform application infrastructure | Platform primitive | Failure record and incident command replay safety where needed. | Mutating commands. | semantic identity/conflict/replay policy. | original receipt or conflict. | local idempotency stores. |
| `publishDomainEvent` | Publish versioned event after source transaction. | Platform event/outbox infrastructure | Platform primitive | Only for approved durable Observability facts with real consumers. | After source write. | event meaning/payload minimization. | outbox receipt/event envelope. | fire-and-forget emitters. |
| `deduplicateDomainEvent` | Prevent repeat consumer effect. | Platform event infrastructure + consumer inbox | Platform primitive | For Observability consumers of source Module events. | Event consumption. | handler identity/effect. | inbox claim/result. | ad hoc generic processed-event table. |
| `enqueueReliableJob` | Persist async work with retries/leases/dead-letter visibility. | Shared queue infrastructure | Platform primitive | Run monitors/correlation workers. | Async boundary. | job payload refs/completion meaning. | job receipt. | module queue frameworks. |
| `executeRetryWithBackoff` | Retry transient work safely. | Shared queue/platform | Platform primitive | Monitor/provider-telemetry retries. | Worker/provider transient failure. | retryability classification and max policy. | retry/dead-letter outcome. | hand-written retry loops. |
| `acquireAggregateLock` | Serialize conflicting commands. | Shared persistence infrastructure | Platform primitive | Incident concurrency if needed. | Before conflicting mutable transition. | lock key/conflict policy. | lock/transaction result. | in-memory mutex. |
| `withOptimisticConcurrency` | Reject stale writes. | Shared persistence infrastructure | Platform primitive | Incident updates and other mutable lifecycle rows. | Mutable command. | merge/retry/conflict behavior. | current version/conflict. | custom compare-and-set helpers. |
| `transitionLifecycleState` | Reusable transition plumbing. | Shared mechanism | Shared mechanism / separate policy | Apply approved incident/failure transition graph. | Status mutation only after U-20. | actual graph remains Observability-owned. | transition result. | one generic global state machine. |
| `requestNotification` | Request alert delivery. | Notification | Platform notification capability | Operational alerts. | After approved severe event/incident. | trigger/recipient/priority meaning. | notification request receipt. | SES/SMS/push code. |
| `appendAuditEvent` | Append generic important-action proof. | Audit / Event Ledger | Platform audit capability | Audit important operator/admin actions. | Incident/admin mutation where policy requires. | safe operational context only. | Audit receipt. | ops audit table/logger. |
| `recordSensitiveAccess` | Append protected-access proof. | Audit / Event Ledger | Cross-cutting capability | Audit detailed diagnostic access. | After/with authorized sensitive view. | ops sensitivity classification and target ref. | AccessAudit receipt. | ops access log table. |
| `enumerateSubjectData` | Enumerate owner-held subject data. | Each data owner through Privacy contract | Shared contract | Privacy participation. | Privacy discovery. | Observability relationships/export meaning. | targets + supported dispositions. | global DB crawler. |
| `evaluateRetentionRequirement` | Return owner facts requiring retention. | Data owner + Privacy | Shared contract | Privacy retention analysis. | Before erasure. | operational/security retention fact. | retention fact/evidence. | local exemption table. |
| `executePrivacyInstruction` | Execute Privacy-owned disposition against owner data. | Privacy orchestrates; each owner executes | Shared contract | Erase/anonymize/retain/export Observability data. | Privacy job execution. | field/provider-specific behavior. | typed disposition result. | local privacy workflow. |
| `anonymizePersonalFields` | Apply approved field-level anonymization. | Shared primitive; owner maps fields | Shared mechanism | Minimize identifiers without breaking retained proof. | Privacy executor. | field mapping/version. | anonymization result. | ad hoc erasure helper. |

### Provider-adapter shared patterns that Observability must respect, not own globally

- `verifyProviderWebhookSignature`
- `deduplicateProviderEvent`
- `translateProviderStatus`
- `reconcileProviderState`
- `captureProviderSnapshot`

These stay with each provider-owning Module. Observability may receive a normalized failure from them.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `normalizeOperationalFailure` | Convert already owner-normalized technical failure facts into the Observability failure envelope. | source Module, provider/integration key, operation, safe code/class, retryability, source ref, correlation. | validated failure command payload. | none until command persists failure. | Failure evidence semantics belong here, while provider status translation stays with owner. |
| `classifyTelemetrySensitivity` | Decide whether a proposed operational field is allowed, redacted, truncated, or rejected. | field/value labels plus owner-provided sensitivity. | safe/rejected field set. | none. | Telemetry acceptance is Observability policy. |
| `aggregateHealthResults` | Compose registered check results into an operator-safe health response. | typed health results. | aggregate health projection. | none. | Aggregation/disclosure belongs to Observability; owner check meaning remains external. |
| `buildOperationalTrace` | Correlate Observability signals by request/source/time. | request/correlation ID, source ref, time range. | redacted trace view. | none. | Diagnostic view semantics belong here. |
| `mapOpsQueryView` | Convert internal operational records/provider refs to redacted public/admin DTOs. | repository results + viewer authority facts. | safe DTO. | none. | Prevents Prisma/provider leakage. |
| `evaluateIncidentGrouping` | Determine whether selected signals belong to one incident. | operational signal refs + approved grouping policy. | grouping explanation/result. | `OpsIncident` only after approval. | Incident meaning belongs here; automation thresholds separately unresolved. |
| `evaluateOpsAlertIntent` | Decide whether an approved incident/health condition warrants requesting Notification. | incident/health result + approved alert policy. | safe notification intent or no-op. | none. | Trigger meaning belongs to Observability; delivery stays Notification-owned. |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **Provider webhook dedupe:** shared dedupe infrastructure may be reused, but `ProcessedStripeEvent`, `ProcessedCalendarEvent`, video/subscription/notification processed-event records remain separate owner truth. `IntegrationFailure` is not a dedupe record.
2. **Queue execution:** shared queue runner owns lease/retry/dead-letter mechanics; `QueueJob` is visibility only; domain job/workflow records remain with owners.
3. **Domain lifecycle events:** shared append/outbox mechanisms may be reused; `SystemEvent` does not absorb `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `AgreementEvent`, `UserSecurityEvent`, etc.
4. **Incidents versus holds:** incident grouping may share lifecycle/concurrency plumbing, but `OpsIncident` is operational; `ComplianceHold` is the reusable stop sign.
5. **Health contracts:** a standard result shape is shared; each component owner defines what healthy/degraded means for its source truth.
6. **Provider status translation:** provider adapters may share a result envelope; mappings remain provider-owner specific.
7. **Reconciliation:** shared worker framework may be reused; only provider/source owners decide repairs.
8. **Privacy:** enumeration/execution protocol is shared; Observability decides how its own records can be erased/anonymized while Privacy owns orchestration/exemption truth.
9. **Locks/concurrency/state machines:** infrastructure is shared; incident/failure transition graphs remain Observability policy once approved.
10. **Audit:** operational correlation may point to Audit records, but `AuditEvent`/`AccessAuditLog` remain separate evidence truth.

---

## 18. Authentication and Authorization

### Authenticated actor requirement

- ingestion from trusted server modules/workers may use system actor context rather than end-user auth;
- all detailed admin/support query surfaces require `resolveAuthenticatedActor`;
- all protected ops actions require `authorizeResourceAction`;
- public health endpoints, if exposed, are intentionally minimal and do not return internal failure details.

### Resource/context facts supplied by Observability

Observability supplies:

- operational resource type and ID;
- owner/source Module;
- requested ops action such as view detailed failure, view queue detail, manage incident, export diagnostics;
- sensitivity classification and whether the view exposes protected references.

Role / Authority interprets permissions.

### Admin/support actions

Potential action vocabulary includes viewing detailed operational diagnostics, managing incidents, and exporting operational evidence. Exact action identifiers must follow Role / Authority conventions and are not invented here if that registry has not yet defined them.

### Step-up

`requireStepUpForSensitiveAction` is used only if an approved security policy designates a particular ops action as high risk. Observability must not decide MFA satisfaction itself.

---

## 19. Compliance / Readiness / Entitlement Gates

Observability is not a commercial or compliance gate composer.

Relevant gates are limited to:

| Gate | Underlying owner | Target action | Local composition | Result |
| --- | --- | --- | --- | --- |
| Authentication | Identity & Access | protected ops query/mutation | require trusted actor/system context | proceed/deny |
| Authorization | Role / Authority | view/manage operational resource | supply ops action/resource facts | proceed/deny |
| Step-up where approved | Identity & Access | sensitive ops action | declare required action/target | proceed/challenge/deny |
| Sensitive access proof | Audit / Event Ledger | protected diagnostic read/export | data owner/Observability supplies sensitivity + outcome | access evidence receipt |
| Privacy retention instruction | Privacy / Data Erasure + Observability facts | erase/anonymize/retain/export operational data | Observability returns owner fact; Privacy records exemption | typed disposition |

Track entitlement, professional readiness, healthcare readiness, financial readiness, verification readiness, moderation, and ComplianceHold do not generally gate ordinary operational telemetry. If a future ops product feature is entitlement-gated, that is a separate product decision and must consume `resolveEntitlement`; do not add local premium flags.

---

## 20. Provider Integrations

### 20.1 Direct providers owned by Observability

#### Error monitoring port

- **Confirmed adapter:** Sentry.
- Provider-neutral inputs: exception, operation, request/correlation context, safe tags, environment/release.
- Credentials: server/environment configuration; never persisted in operational records or returned to clients.
- Status/error translation: adapter returns a safe provider result/reference; raw Sentry errors do not leak into Module contracts.
- Retry: bounded according to provider adapter policy; error reporting must not create recursive failure storms.
- Privacy: provider references and personal data must be minimized; deletion/retention follows Privacy instruction and provider capability when approved.

### 20.2 Direct providers with unresolved choice

- structured logging backend;
- metrics backend.

Interfaces and policy can be built before provider selection. Provider selection affects only adapters, not Module contracts.

### 20.3 Shared queue runtime

Queue runtime/provider is unresolved (`U-21`). It is shared platform infrastructure, not a direct Observability-owned provider. Observability instruments the runner through `recordQueueTelemetry`.

### 20.4 Providers not owned here

Do not instantiate Stripe, Cronofy, Typesense, Cloudflare R2, Daily/Mux/Agora, notification delivery providers, verification providers, AI providers, or subscription billing providers in this Module merely to observe them.

### 20.5 Webhook verification / dedupe / reconciliation

Observability does not own provider webhook endpoints for other Modules. The provider owner:

1. verifies signature;
2. deduplicates provider event;
3. translates provider status;
4. executes its source command;
5. reconciles missed state when required;
6. calls `recordIntegrationFailure` if a technical failure/degradation must be surfaced.

Observability never marks another Module's processed-provider-event record as processed, ignored, failed, or recovered.

---

## 21. Events and Outbox

### Module-owned event policy

Events describe facts that occurred; they are not cross-Module commands. Operational logs and metrics are not automatically domain events.

No canonical Observability event names are currently confirmed. Therefore:

- do not emit an event for every log line or metric;
- do not create a generic `system.event` bus that becomes a second business event system;
- only introduce an outbox event when a concrete consumer requires durable reaction to an approved Observability fact;
- event payloads must contain stable IDs, source references, schema version, correlation/causation IDs, timestamps, and minimized safe context;
- consumers use `deduplicateDomainEvent` and remain idempotent.

### Incident events

If incident persistence/lifecycle is approved, opened/updated/resolved event classes may be proposed in the feature specification, but they are not approved by this architecture today.

---

## 22. Background Jobs / Scheduled Work

### 22.1 Stalled queue monitor

**Purpose:** find queue execution records that exceed an approved heartbeat/lease/runtime threshold and surface operational degradation.

**Input:** QueueJob/queue-runner operational facts, approved thresholds.

**Owner:** Observability for monitoring policy; shared queue infrastructure for execution facts.

**Idempotency key:** monitor window + queue/job identity + rule version.

**Retryable failures:** repository/provider temporary unavailability.

**Permanent failures:** invalid configuration or unsupported queue source.

**Dead-letter/manual review:** dead-letter through shared queue; operator investigates configuration/adapter failure.

**Business truth updated:** none.

**Operational telemetry:** metric + IntegrationFailure/SystemEvent as approved.

**Blocked by:** threshold policy if not already part of queue runtime contract.

### 22.2 Indexing lag monitor

**Purpose:** surface Search indexing backlog age/size without owning Search execution.

**Input:** Search-owned health/backlog facts through public interface.

**Owner:** Observability monitor; Search owns backlog/projection truth.

**Idempotency:** schedule window + Search component key.

**Business truth updated:** none.

**Failure:** Search owner unavailable -> degraded health/failure visibility, never direct `SearchUpsertEvent` query fallback unless Search explicitly exposes that repository through its contract.

### 22.3 Provider health monitor

**Purpose:** aggregate owner-supplied health checks for external integrations.

**Input:** registered owner check results.

**Business truth updated:** none.

### 22.4 Incident-correlation worker — conditional

Only after `U-22` approves automatic grouping/thresholds. Until then, incident correlation may be operator-invoked only.

### Queue rule

All jobs use `enqueueReliableJob` and `executeRetryWithBackoff`. No Observability-specific queue/cron engine is permitted.

---

## 23. Concurrency and Idempotency

### Failure recording

- A technical failure occurrence and a retry of the **record command** are different concepts.
- `executeIdempotentCommand` may collapse command retries only when the caller provides the same semantic failure identity/fingerprint.
- New provider attempts or new worker attempts must remain observable as distinct occurrences where the approved data model requires it.

### Queue telemetry

- Queue runner identity + attempt + instrumentation event must be safe under duplicate delivery.
- Heartbeat/terminal observations must not regress a terminal view due to stale instrumentation.
- Exact constraint strategy depends on the approved QueueJob schema.

### Incident transitions

- Use optimistic versioning or compare-and-set for incident updates.
- Use aggregate locking when two commands cannot safely race.
- Stale updates return conflict and current version; do not last-write-wins silently.

### Health registry

- component keys must be unique at application composition time;
- health checks are bounded by timeouts;
- one failing health check cannot block all other checks indefinitely.

### No in-memory distributed locks

Database/shared infrastructure locking is required for persisted concurrency. In-memory mutexes are prohibited for multi-instance correctness.

---

## 24. Media / Storage

Observability owns no user/business media attachment meaning and no `MediaAsset` lifecycle.

- Do not upload logs, traces, incident evidence, exports, or provider payload dumps to R2 directly from this Module unless a future approved owner contract explicitly requires a Media-managed object.
- If an ops export eventually needs a file, Media / File Access owns object storage mechanics and signed access; Observability owns only the export meaning if such a feature is approved.
- Sensitive diagnostics must not be made available through permanent public URLs.

---

## 25. Search / Projection

Observability records are not public discovery source records.

Observability may measure Search health/indexing lag only through Search-owned facts/interfaces. It must not:

- write `SearchUpsertEvent`;
- instantiate Typesense clients;
- derive or repair search documents;
- mark search work complete;
- use search state as business source truth.

The ops dashboard may provide links/references to Search-owned diagnostic pages if authorized.

---

## 26. Notification

Observability owns the **trigger meaning** for an operational alert; Notification owns delivery.

Safe alert intent should contain only:

- incident/failure ID or safe reference;
- component/provider key;
- approved severity/priority;
- concise safe summary;
- operator action route;
- correlation ID where useful;
- no raw error payload, secret, PHI, payment data, resume text, private message, or provider credential.

Use `requestNotification`. Do not call SES, SMS, push, Web Push, FCM, OneSignal, or other channel providers here.

Automatic alert thresholds are blocked by `U-22` until approved.

---

## 27. Audit and Sensitive Access

### Distinction

- `SystemEvent` / `IntegrationFailure` / `QueueJob` / `OpsIncident` = operational truth.
- `AuditEvent` = generic important-action proof owned by Audit / Event Ledger.
- `AccessAuditLog` = sensitive-data access proof owned by Audit / Event Ledger.
- provider processed-event records = provider-dedupe truth owned by provider Modules.
- domain event ledgers = source-domain transition truth.

### When Observability invokes Audit

- protected diagnostic view exposing sensitive source references;
- diagnostic export if later approved;
- incident admin actions that policy classifies as auditable;
- privacy execution actions when Audit/Privacy requires proof.

Observability never writes Audit tables directly. Use `appendAuditEvent` and `recordSensitiveAccess`.

---

## 28. Privacy and Retention

### Subject-data inventory

Potential subject-linked data includes:

- actor/user IDs included in request context if approved;
- source record references tied to a user/profile;
- IP hashes/user-agent data only if explicitly approved for operational records;
- safe diagnostic metadata that may still indirectly identify a user;
- Sentry/logging provider references that may contain personal context;
- incident assignment/operator IDs;
- request/correlation IDs linked to subject activity.

### Privacy executor contract

Observability implements:

1. `enumerateSubjectData` — enumerate Observability-owned records/provider references linked to the subject and supported dispositions;
2. `evaluateRetentionRequirement` — return security/operational retention facts without creating `DataRetentionExemption` itself;
3. `executePrivacyInstruction` — erase/anonymize/retain/export under Privacy-owned instruction;
4. export serializer if Privacy requires an export contribution.

### Current blockers

`U-24` remains unresolved:

- current `DataErasureTargetType` has no specific Observability targets;
- retention durations for operational/security evidence are not approved;
- provider deletion capability/retention for logging/metrics/Sentry is not fully specified.

Production privacy execution must not use arbitrary `other` strings as a hidden substitute for a canonical target vocabulary.

### Rules

- soft delete is not legal erasure;
- do not invent a retention exemption;
- minimize personal fields before collection to reduce erasure burden;
- retained records may require anonymization of nonessential identifiers where allowed;
- provider deletion failures must return explicit partial/retryable/retained results to Privacy;
- privacy cannot silently destroy evidence that an approved security/legal retention rule requires.

---

## 29. Observability

This section defines the Module's own operational self-observability.

### Structured logs

Required safe dimensions:

- environment;
- application/service component;
- Module ID;
- operation name;
- request/correlation ID;
- queue job ID/attempt where relevant;
- provider/integration key where relevant;
- normalized error class/code;
- duration bucket/timing;
- safe source type/ID only where approved.

Never log secrets, access tokens, session tokens, OTPs, card data, raw bank/tax data, PHI, resume bodies, message bodies, raw identity documents, raw provider payloads, or complete agreements.

### Metrics

Prefer low-cardinality dimensions such as Module, provider key, operation, result class, queue name, environment. User IDs and arbitrary source IDs are not metric dimensions by default.

### Health

Separate:

- **liveness** — process can respond;
- **readiness** — component can serve its intended operational function;
- **informational degradation** — dependency/provider problem visible to operators but not necessarily a deployment-blocking readiness failure.

### Self-failure loop prevention

- logging provider failure uses bounded fallback, not recursive `recordIntegrationFailure` loops;
- Sentry failure does not cause a new Sentry call about the Sentry failure;
- metrics failure does not recursively emit metric failure metrics;
- persistence failure may use a minimal local fallback channel, but must not fabricate durable proof.

---

## 30. Security Boundaries

1. Validate every public command/query DTO with root-standard runtime validation.
2. Only trusted server code may invoke telemetry ingestion commands; browser clients cannot write arbitrary failure/system-event records.
3. Detailed ops routes/actions use server-side authorization.
4. Public health responses are minimal and do not expose provider account IDs, secret names, internal URLs, stack traces, queue payloads, or source record details.
5. Provider credentials remain environment/secret-manager configuration and never become Prisma/telemetry fields.
6. Sentry/logging/metrics adapters sanitize before serialization/transmission.
7. No arbitrary `Json` passthrough from a provider or exception object into persisted metadata.
8. Metadata size and nesting depth are bounded.
9. Rate-limit public health or external telemetry endpoints if such endpoints exist; prefer internal server invocation for ingestion.
10. Correlation IDs are identifiers, not authentication credentials.
11. Provider event IDs are not authorization tokens.
12. Incident notes/summaries are operational metadata and remain subject to telemetry safety policy.

---

## 31. Error / Decision Result Pattern

Public Module interfaces return a provider-neutral typed result. Exact TypeScript names follow code standards, but the semantic categories are:

| Category | Meaning |
| --- | --- |
| `ok` | Operation/query completed successfully. |
| `invalid_input` | Contract validation or telemetry-safety validation failed. |
| `unauthorized` | No trusted actor/system context for a protected operation. |
| `forbidden` | Actor exists but Role / Authority denied the action. |
| `not_found` | Requested Observability resource does not exist or is not visible to caller. |
| `conflict` | Idempotency fingerprint mismatch, stale incident version, duplicate registry key, or conflicting transition. |
| `retryable_failure` | Temporary persistence/provider/dependency failure; retry may be safe under owner policy. |
| `terminal_failure` | Operation cannot proceed without code/configuration/policy change or manual action. |
| `unavailable` | Health/query dependency unavailable; no false success is returned. |

Provider-native error strings/codes may be stored only in a sanitized internal diagnostic field when approved and must not become the consumer-facing contract.

---

## 32. Testing Architecture

### Domain unit tests

- telemetry allowlist/redaction/truncation;
- failure normalization;
- metric dimension/cardinality policy;
- health aggregation;
- incident grouping/transition policy after approval;
- operational result mapping.

### Public contract tests

- command/query DTO validation;
- provider-neutral result shape;
- no Prisma/provider SDK type leakage;
- stable reason/error categories;
- owner signal contracts.

### Database / integration tests

If persistence is approved:

- create/query each approved operational record;
- indexes support bounded filters;
- idempotent failure recording;
- queue telemetry stale/duplicate behavior;
- incident optimistic concurrency;
- migration/backfill safety.

### Authorization tests

- public minimal health versus protected detailed health;
- detailed failure/queue/incident queries require Role / Authority;
- sensitive diagnostic access invokes Audit where required;
- ordinary users cannot write operational source records.

### Compliance / telemetry-safety tests

Fixtures containing:

- PHI;
- card numbers/payment details;
- SSNs;
- OTPs/secrets/tokens;
- raw resume text;
- private message bodies;
- raw identity documents;
- full contracts;

must be rejected or safely redacted according to policy.

### Idempotency / concurrency tests

- duplicate `recordIntegrationFailure` command replay;
- separate failure occurrences not collapsed;
- duplicate queue instrumentation;
- stale heartbeat/terminal update ordering;
- simultaneous incident updates/resolve races.

### Provider adapter tests

- Sentry adapter receives only sanitized context;
- provider failure returns typed result;
- Sentry outage does not recurse;
- logging/metrics adapter contract tests independent of chosen provider.

### Privacy tests

After `U-24` approval:

- subject enumeration completeness;
- erase/anonymize/retain/export behavior;
- provider deletion partial failure;
- approved retention fact without local exemption truth.

### E2E participation tests

- worker/provider failure -> normalized failure visible -> protected query/dashboard;
- queue retry/dead-letter -> queue visibility;
- health degradation -> dashboard state;
- approved incident -> notification request;
- Privacy job -> Observability executor result.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. Observability truth is operational truth only.
2. `SystemEvent` is not `AuditEvent`.
3. `IntegrationFailure` is not a provider processed-event/dedupe record.
4. `QueueJob` is not the authoritative domain job/workflow lifecycle.
5. `OpsIncident` is not `ComplianceHold`, `ModerationCase`, or `Dispute`.
6. Closing an incident never resolves a source business record automatically.
7. A successful retry does not permit Observability to mark another Module's provider event processed.
8. Provider status translation stays with the provider-owning adapter.
9. Provider reconciliation stays with the provider/source owner.
10. Observability may not write `ProcessedStripeEvent`, `ProcessedCalendarEvent`, `SearchUpsertEvent`, Notification delivery state, Media state, or other foreign tables.
11. Cross-Module diagnostic reads use owner interfaces/events, not a universal Prisma repository.
12. One structured logger is used platform-wide.
13. Feature Modules do not instantiate independent Sentry clients.
14. Metrics use controlled low-cardinality dimensions.
15. Telemetry metadata is sanitized before persistence or transmission.
16. Secrets, OTPs, raw biometrics, raw identity documents, card data, PHI payloads, full resumes, private messages, and full contracts are prohibited in generic telemetry.
17. Public health endpoints do not expose internal diagnostic detail.
18. Detailed ops views are authorized server-side.
19. Sensitive diagnostic reads are access-audited when policy requires it.
20. Notification delivery is requested through Notification only.
21. Shared queue execution, retries, idempotency, locks, and outbox are reused; no local equivalents.
22. Queue instrumentation never copies full job payloads into operational records.
23. Sentry/logging/metrics providers remain secondary telemetry, not business truth.
24. Observability provider failures do not recursively create infinite telemetry failure loops.
25. `PR-CL09-05` must be accepted before adding canonical Observability Prisma models.
26. `U-20` must be resolved before adding persistent statuses/severities or lifecycle code.
27. `U-22` must be resolved before automatic incident grouping/alerts are enabled.
28. `U-24` must be resolved before production privacy retention/erasure behavior is enabled.
29. `DataErasureTargetType.other` is not a silent substitute for missing canonical Observability privacy target types.
30. Build progress never silently converts a Proposed Ruling into a binding decision.

---

## 34. Prohibited Duplicate Implementations

Do not generate inside this Module or its consumers:

- `currentUser.ts`, `getOpsUser.ts`, `requireOpsAdmin.ts`, `ops-auth.ts` as an alternate auth/authority engine;
- `request-id.ts`, `correlation-id.ts`, `trace-context.ts` outside the canonical request-context primitive;
- per-Module `logger.ts`, `structured-logger.ts`, `server-logger.ts` clients that bypass the canonical logger;
- direct `Sentry.init` / feature-local Sentry clients;
- per-Module `metrics.ts`, `stats.ts`, `telemetry.ts` clients;
- ad hoc `redact-error.ts`, `scrub-log.ts`, blacklist-only metadata sanitizers;
- generic `integration_failures` tables in Payment, Calendar, Media, Search, Notification, Video, Subscription, Moderation, or other Modules;
- feature-local `queue_job`, `job_attempt`, or queue dashboard tables that replace `recordQueueTelemetry`;
- an Observability-owned queue runtime, retry loop, lease table, or dead-letter engine when shared queue infrastructure exists;
- local generic incident systems in business Modules;
- a global processed-webhook table;
- provider-specific webhook verification/dedupe/status translation/reconciliation in Observability;
- direct Typesense, R2, Stripe, Cronofy, video, notification, verification, or subscription provider clients for observed Modules;
- local `AuditEvent`/`AccessAuditLog` substitutes;
- local `PrivacyRequest`, `DataErasureJob`, or `DataRetentionExemption` tables;
- in-memory distributed locks;
- a universal `findAnyRecordByTypeAndId` repository;
- a generic global state machine that owns all lifecycle policy.

---

## 35. Unresolved Decisions

| ID | Question | Current evidence | What it blocks |
| --- | --- | --- | --- |
| `PR-CL09-05` / `U-19` | Where do `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` persist? | Registry/glossary claim the records; Prisma omits all. Cluster proposes Postgres/Prisma canonical persistence with external telemetry secondary. | Repositories, migrations, durable admin queries. |
| `U-20` | What are Observability statuses, severities, and lifecycle transitions? | No enums/models supplied. | Incident/failure/queue lifecycle implementation. |
| `U-21` | Which shared queue runtime/provider executes jobs? | Shared queue infrastructure is canonical; provider/runtime unspecified. | Production adapter only, not contracts/domain meaning. |
| `U-22` | Which incident grouping and alert thresholds are automatic versus manual? | Incident grouping capability confirmed; thresholds absent. | Automatic incident creation and alerting. |
| `U-23` | Which logging and metrics backends are authoritative for diagnostics? | Sentry confirmed for errors; logging/metrics provider unspecified. | Production adapters only. |
| `U-24` | Which Observability records are Privacy targets and how long are they retained? | Current Privacy target enum lacks CL-09-specific values; retention periods absent. | Production privacy executor/retention behavior. |
| `OBS-U-01` | Is `SystemEvent` strictly append-only, or can operational records be corrected/superseded? | Glossary calls it event truth but no persistence/lifecycle policy exists. | Repository mutation rules. |
| `OBS-U-02` | How is `IntegrationFailure` recovery represented: mutable record, linked occurrence, or separate recovery observation? | Need is clear, model absent. | Failure lifecycle/query semantics. |
| `OBS-U-03` | What semantic key distinguishes duplicate failure-record commands from separate real failure attempts? | Idempotency is canonical; exact failure identity is not. | Unique constraints/idempotency policy. |
| `OBS-U-04` | What is the stable Ops action vocabulary in Role / Authority? | Authorization owner is confirmed; exact action IDs not supplied here. | Final authorization contract names. |
| `OBS-U-05` | Which detailed ops views require step-up? | Step-up capability exists; policy not specified. | High-risk admin security gating. |

Coding agents must stop and surface these decisions rather than resolving them through arbitrary schema/code choices.

---

## 36. Architecture Decision Summary

### Binding rulings

1. `observability_ops` is the canonical owner of generic operational diagnostics and integration-failure visibility.
2. Conceptual ownership of `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` is confirmed, but current Prisma persistence is absent.
3. No canonical Observability migration or lifecycle enum may be created until `PR-CL09-05`/`U-19` and `U-20` are accepted/resolved.
4. `QueueJob` is operational visibility only; shared queue infrastructure owns execution mechanics and source Modules own business completion meaning.
5. Provider-owning Modules retain webhook verification, dedupe, status translation, reconciliation, and business transitions.
6. Sentry is the confirmed error-monitoring adapter; structured logging and metrics backends remain provider-neutral/unresolved.
7. `createRequestContext`, `writeStructuredLog`, `sanitizeTelemetryMetadata`, `captureException`, `emitMetric`, `recordIntegrationFailure`, `recordQueueTelemetry`, and `checkServiceHealth` are canonical shared capabilities associated with this Module/platform and must not be duplicated.
8. `correlateOpsIncident` is the canonical incident capability, but durable incident lifecycle/automation remains blocked by unresolved status/threshold decisions.
9. Authentication, authorization, Audit, Notification, Privacy, Search, Media, Payment, Booking/Calendar, Video, Track Entitlement, and all source business lifecycles remain external owners.
10. Detailed diagnostics are protected and redacted; sensitive access is recorded through Audit where required.
11. Privacy / Data Erasure owns orchestration and retention-exemption truth; Observability is only an owner-local executor.
12. Operational records never become public search truth and never directly mutate business source state.

### Proposed ruling inherited

`PR-CL09-05` proposes canonical PostgreSQL/Prisma persistence for the four Observability records with Sentry/logging/metrics as secondary telemetry. This document does not silently accept it; implementation remains gated on explicit approval plus a concrete schema/status design.

---

## 37. Coding-Agent Usage

Before implementing any Observability / Ops feature, the coding agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md` if present;
3. root `code-standards.md` if present;
4. Canonical Shared Operations Architecture / Registry;
5. CL-09 `architecture.md`;
6. CL-09 `build-plan.md`;
7. this `observability_ops/module-architecture.md`;
8. this `observability_ops/implementation-plan.md`;
9. public-interface sections for direct dependencies: Identity & Access, Role / Authority, Audit / Event Ledger, Notification, Privacy / Data Erasure, Search / Public Visibility, shared queue/platform infrastructure, and each provider-owning Module integrated by the current feature;
10. `progress-tracker.md`.

Before coding, confirm that the feature's blocking Proposed Rulings / Unresolved decisions have been accepted or intentionally deferred in a way the Cluster build plan permits. If a required root file is not available in the working context, do not invent its rules; obtain/read it before implementation.
