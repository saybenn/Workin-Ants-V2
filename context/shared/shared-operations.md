# Workin Ants Shared Operations Registry

> **Repository location:** `context/shared/shared-operations.md`  
> **Registry status:** Canonical reference derived from the 34/34 Module Shared Operations synthesis  
> **Source architecture:** *Workin Ants — Canonical Shared Operations Architecture*  
> **Operation count:** 126 canonical operations and interfaces  
> **ID namespace:** `SH-001` through `SH-126`  
> **Controlling principle:** Shared mechanism does not transfer lifecycle ownership or source-of-truth authority.

## Purpose

This file is the authoritative lookup registry for reusable Workin Ants operations, Module public interfaces, shared contracts, provider-adapter contracts, and platform primitives.

Cluster and Module plans **reference this registry by permanent `SH-###` identifier**. They do not copy the entire registry into local context files.

Use this file to answer:

- What is the canonical name of this operation?
- What does it mean in plain English?
- Who owns it?
- What kind of shared operation is it?
- Is the ruling confirmed, proposed, or unresolved?
- What boundary must remain local?
- What implementation must be reused instead of rebuilt?

This registry does **not** replace Module architecture. The consuming Module still owns the business reason for invoking an operation, the action-specific policy it supplies, and its own source-of-truth lifecycle.

## Authority and Evidence

Authority order inherited from the canonical synthesis:

1. Deep Module Registry and approved source-of-truth ownership rules.
2. Cluster Registry for controlled context, support rails, and declared bridges.
3. Prisma schema for concrete records, enums, relationships, uniqueness, and lifecycle evidence.
4. Ubiquitous Language / Compliance Inventory for canonical meanings and legal constraints.
5. The 34 standardized Module Shared Operations extracts as candidate evidence and duplicate-risk observations.

## Permanent ID Governance

The identifiers in this file are stable architecture references.

- An existing `SH-###` ID must **never be renumbered or reused**.
- Renaming an operation does not change its ID; record the old name as an alias.
- If an operation is retired, keep its ID and mark it deprecated rather than deleting or reassigning it.
- If an operation is split into materially different contracts, keep the original ID as deprecated/superseded and append new IDs after the current highest ID.
- New canonical operations begin at `SH-127`; do not insert new IDs into the existing sequence.
- Candidate aliases do not receive independent IDs unless architecture later rules that they are genuinely separate operations.

The `SH-###` namespace is therefore suitable for Cluster architecture, Cluster build plans, Module architecture, Module implementation plans, feature specifications, tests, ADRs, and code comments where an architectural reference is useful.

## How Cluster and Module Plans Must Reference Shared Operations

A consuming plan should include **only the operations it actually uses**.

For each referenced operation, record:

1. **Why needed** — why this Cluster/Module needs the operation.
2. **Invocation point** — where it enters the workflow or implementation sequence.
3. **Local policy** — what decision, mapping, semantic key, lifecycle rule, or context remains owned by the consuming Module.
4. **Do not build** — the local helper/service/adapter/ledger that must not be independently created.
5. **Integration proof** — the test or acceptance criterion proving the Module uses the canonical operation correctly.

Use this format:

```markdown
## Shared Operations Used

### SH-XXX — canonicalOperationName
Owner: [canonical owner]
Why needed: [consumer-specific reason]
Invocation point: [workflow/feature step]
Local policy: [what remains owned here]
Do not build: [duplicate helper/service/adapter/ledger]
Integration proof: [contract/integration/E2E test]
```

Do **not** paste the global plain-English definition, build rule, alias catalog, or unrelated operations wholesale into every plan. The `SH-###` reference points back to this file.

## Status Semantics

- **Confirmed:** Directly supported by repeated Module extracts and foundational architecture boundaries.
- **Proposed ruling:** Strong cross-Module synthesis that requires explicit architecture approval before becoming authoritative.
- **Unresolved:** Evidence establishes the need but not a final owner, contract, schema, or provider decision.

Implementation rule:

- **Confirmed** entries may be used as implementation constraints.
- **Proposed ruling** entries may be referenced for planning, but architecture approval is required before schema/API commitment.
- **Unresolved** entries must not be silently implemented by the first feature that needs them.

## Classification Semantics

- **Platform primitive:** Low-level mechanism implemented once, such as idempotency, hashing, encryption, locking, queue execution, or request context.
- **Cross-cutting capability:** One owning Module exposes a reusable operation to many consumers.
- **Module public interface:** A source-of-truth Module exposes a query or command; it is reusable but not neutral infrastructure.
- **Shared contract; separate policy:** Only the request/result shape is shared. Each Module retains its own facts, rules, and evidence.
- **Shared mechanism; separate truth:** Implementation plumbing is shared while records, enums, lifecycles, and ownership remain separate.
- **Provider-adapter contract:** A common port with provider- and domain-specific implementations.
- **Cluster-local capability:** Reusable within a bounded workflow or cluster, not platform-wide.
- **Module-internal:** Retained by one owner because sharing would transfer policy or lifecycle truth.

## Canonical Registry

The registry remains in the canonical source order. Every entry contains the required plain-English field.

## A. Identity, Authority, Consent, Entitlements, and Holds

### SH-001 — `resolveAuthenticatedActor`

- **Plain English:** Turn a valid provider session or system credential into the trusted Workin Ants actor context used by server-side operations.
- **Owner:** Identity & Access
- **Classification:** Platform capability
- **Status:** Confirmed
- **Boundary:** Authentication ends at actor resolution. Feature Modules still decide what the actor is trying to do.
- **Build rule:** Implement once as request middleware plus a typed actor context. Prohibit feature-local current-user helpers.
- **Candidate aliases / narrower variants:** authenticateActor; requireAuthenticatedActor; getAuthenticatedActor; getAuthenticatedActorContext; Authentication/session resolution; Authenticated actor context

### SH-002 — `authorizeResourceAction`

- **Plain English:** Decide whether an authenticated actor may perform a named action on a protected resource in platform, organization, participant, or ownership scope.
- **Owner:** Role / Authority
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The resource-owning Module supplies relationship facts and action vocabulary; Role / Authority interprets permission.
- **Build rule:** Expose a typed decision API and matching route/RLS enforcement. Do not embed business readiness or entitlement policy.
- **Candidate aliases / narrower variants:** authorizeAction; authorizeDomainAction; authorizeScopedAction; authorizeBusinessAction; Authorization decision; contextual ownership check; organization-role authorization; thread-participant authorization

### SH-003 — `queryOwnerFacts`

- **Plain English:** Read the minimum relationship or ownership facts needed by another Module without transferring lifecycle ownership.
- **Owner:** Each source Module
- **Classification:** Shared contract; separate implementations
- **Status:** Proposed ruling
- **Boundary:** Organization membership, Thread participation, Order participants, Booking facts, and similar facts remain source-owned.
- **Build rule:** Define small owner-specific DTOs. Reject a universal polymorphic repository or cross-domain direct Prisma reads.

### SH-004 — `resolveCustomerActor`

- **Plain English:** Resolve an authenticated User into the CustomerProfile that acts as the commercial buyer.
- **Owner:** Customer / Buyer Profile
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** CustomerProfile identity is distinct from the base User and from CandidateProfile or ProfessionalProfile.
- **Build rule:** Provide an idempotent lookup/provisioning interface; consumers store customerProfileId where the schema requires it.

### SH-005 — `resolveEntitlement`

- **Plain English:** Return the effective feature, quota, waiver, boost, commission, priority, or perk for a specific actor track and entitlement key.
- **Owner:** Track Subscription & Entitlement
- **Classification:** Platform commercial-policy capability
- **Status:** Confirmed
- **Boundary:** Consuming Modules own how the result affects their action and historical snapshots. No local premium booleans.
- **Build rule:** Use typed keys and typed values, effective dates, grant precedence, reason codes, and evidence references.
- **Candidate aliases / narrower variants:** evaluateEntitlement; lookupEntitlement; getActiveEntitlement; getEffectiveEntitlements; resolveEffectiveEntitlement; Entitlement lookup

### SH-006 — `consumeMeteredEntitlement`

- **Plain English:** Atomically confirm that a limited entitlement can be used and record the permitted quantity as immutable usage proof.
- **Owner:** Track Subscription & Entitlement
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The source Module defines when the business event actually counts; Track owns usage periods, counters, and receipts.
- **Build rule:** Use one transaction, idempotency key, immutable TrackUsageEvent, and rebuildable counter projection.
- **Candidate aliases / narrower variants:** recordUsageEvent; Usage metering; consumeUsageAtomically; atomicCounterIncrement

### SH-007 — `recordConsentProof`

- **Plain English:** Persist version-specific evidence that a User accepted a particular consent, disclosure, authorization, or agreement.
- **Owner:** Consent & Disclosure
- **Classification:** Platform consent capability
- **Status:** Confirmed
- **Boundary:** ConsentLog proves acceptance; it does not grant the downstream permission or replace contextual consent records.
- **Build rule:** Expose one acceptance command with exact type, version, acceptedAt, and minimized request evidence.

### SH-008 — `queryConsentProof`

- **Plain English:** Return whether the required consent type and version was accepted, including the proof reference.
- **Owner:** Consent & Disclosure
- **Classification:** Platform consent capability
- **Status:** Confirmed
- **Boundary:** The consuming Module determines whether that proof is sufficient for its current action.
- **Build rule:** Return proof ID, type, version, acceptedAt, and validity status; never duplicate consent tables in consumers.
- **Candidate aliases / narrower variants:** lookupConsentProof; getConsentProof; resolveConsentProof; verifyConsentProof; Consent proof lookup

### SH-009 — `resolveActiveConsentVersion`

- **Plain English:** Select the currently applicable consent or disclosure version for type, locale, jurisdiction, and effective date.
- **Owner:** Consent & Disclosure
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Material-change and re-consent policy remain Consent-owned.
- **Build rule:** Use an immutable version catalog with effective dates, content hash, locale, and jurisdiction.

### SH-010 — `presentStandaloneConsent`

- **Plain English:** Render a high-risk disclosure separately and submit its acceptance through the canonical consent command.
- **Owner:** Consent & Disclosure
- **Classification:** Cross-cutting UI/application capability
- **Status:** Confirmed
- **Boundary:** The owning workflow supplies context; Consent owns version rendering and generic acceptance proof.
- **Build rule:** Build one reusable shell with version lookup, accessibility, evidence capture, and no provider-specific side effects.

### SH-011 — `evaluateComplianceHold`

- **Plain English:** Return active reusable stop signs that apply to a target and requested action.
- **Owner:** Admin Review / Compliance Hold
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The consumer maps applicable holds to its own lifecycle behavior; it must not create local blocked flags.
- **Build rule:** Query by target type/ID and action; return safe reason codes, hold IDs, scope, and expiration.
- **Candidate aliases / narrower variants:** checkComplianceHold; checkActiveComplianceHold; evaluateComplianceHolds; applyComplianceHoldGate

### SH-012 — `requestComplianceHold`

- **Plain English:** Ask the hold owner to create an authoritative platform stop sign for a target.
- **Owner:** Admin Review / Compliance Hold
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The requesting Module supplies domain evidence and justification; the hold Module validates and owns lifecycle truth.
- **Build rule:** Use a typed, idempotent command with target, reason, source, evidence references, requested scope, and actor.

### SH-013 — `releaseComplianceHold`

- **Plain English:** Ask the hold owner to release an existing hold after the source condition is resolved.
- **Owner:** Admin Review / Compliance Hold
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Only the hold owner changes hold status; the requesting Module decides whether its domain outcome permits requesting release.
- **Build rule:** Require hold ID, source decision reference, actor, reason, and idempotency key; append audit proof.

### SH-014 — `requireStepUpForSensitiveAction`

- **Plain English:** Require fresh MFA, passkey, or equivalent assurance before a high-risk action proceeds.
- **Owner:** Identity & Access
- **Classification:** Platform security capability
- **Status:** Confirmed
- **Boundary:** Feature Modules declare which actions require step-up; Identity owns challenge, expiry, attempt, and assurance-session lifecycles.
- **Build rule:** Bind SensitiveActionSession to actor, action, target, assurance level, and short expiry; enforce server-side.

### SH-015 — `returnDecisionResult`

- **Plain English:** Return a stable allow, deny, warning, review, or remediation response without centralizing the participating Module’s policy.
- **Owner:** Shared contract; policy owner varies
- **Classification:** Shared contract; separate policy
- **Status:** Proposed ruling
- **Boundary:** Professional, healthcare, verification, financial, job, authority, and hold decisions remain separate truths.
- **Build rule:** Standardize decision, reason codes, evidence references, warnings, evaluatedAt, policy version, expiry, and next action.
- **Candidate aliases / narrower variants:** buildReadinessDecision; composeReadinessDecision; returnReadinessDecision; evaluateReadinessResult; evaluateReadiness response shape; Access-denial translation

## B. Domain and Compliance Public Interfaces

### SH-016 — `evaluateProfessionalReadiness`

- **Plain English:** Determine whether a ProfessionalProfile may perform a named selling action.
- **Owner:** Professional Eligibility
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** The action-to-gate composition remains Professional Eligibility policy; underlying verification, healthcare, financial, entitlement, and hold truth stays external.
- **Build rule:** Expose action-specific decisions such as publish_offering, respond_to_gig, and participate_in_order.

### SH-017 — `resolveVerificationRequirements`

- **Plain English:** Return the verification checks required by accepted taxonomy and target context.
- **Owner:** Trust Verification / Screening
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Requirement resolution does not assert that the checks are satisfied.
- **Build rule:** Return requirement IDs, check types, severity, applicability, expiry expectations, and owning evidence.

### SH-018 — `evaluateVerificationReadiness`

- **Plain English:** Determine whether the required verification checks and credentials are currently satisfied.
- **Owner:** Trust Verification / Screening
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Consumers must not reconstruct readiness from badges or raw provider statuses.
- **Build rule:** Evaluate VerificationRequirement and VerificationCheck truth; return a DecisionResult with safe evidence references.

### SH-019 — `evaluateFinancialReadiness`

- **Plain English:** Determine KYC, tax-profile, payout-account, available-balance, and financial-restriction readiness.
- **Owner:** Payment / Payout / Tax
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Consumers decide when financial readiness is required; they do not interpret Stripe state directly.
- **Build rule:** Return separate readiness dimensions and reasons rather than one opaque boolean.

### SH-020 — `evaluateHealthcareReadiness`

- **Plain English:** Determine whether healthcare-lane, provider, BAA, and data-boundary requirements are satisfied.
- **Owner:** Healthcare / Regulated Services
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Healthcare is a sensitivity lane, not a User type; consumers enforce the returned result.
- **Build rule:** Return provider/BAA/data-boundary decision with permitted, blocked, or redacted outcome and policy version.

### SH-021 — `evaluateJobCompliance`

- **Plain English:** Evaluate a versioned Job snapshot against jurisdiction-aware employment-posting rules.
- **Owner:** Job Compliance
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Organization Hiring owns Job lifecycle; Job Compliance owns findings, decision, and proof.
- **Build rule:** Accept canonical Job input and rule-set version; return pass, warning, block, or review with findings and snapshot hash.

### SH-022 — `resolveTaxonomyRequirements`

- **Plain English:** Translate accepted Domain, Category, and Tag combinations into verification, healthcare, location, license, or sensitivity requirements.
- **Owner:** Taxonomy & Classification
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Taxonomy triggers requirements but does not determine whether another Module’s requirement is completed.
- **Build rule:** Return requirement identifiers, owner Module, trigger source, severity, and applicability.

### SH-023 — `validateTaxonomyAssignment`

- **Plain English:** Validate canonical Domain, Category, Tag, hierarchy, active status, and entity-assignment compatibility.
- **Owner:** Taxonomy & Classification
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** The target Module owns whether classification is mandatory for its lifecycle transition.
- **Build rule:** Expose normalized validation errors and canonical IDs; prevent local tag cleaners and taxonomy copies.

### SH-024 — `evaluatePublicReadiness`

- **Plain English:** Return whether source truth may appear in a specified public or protected discovery surface.
- **Owner:** Source/compliance owner; Search composes
- **Classification:** Shared contract; separate policy
- **Status:** Confirmed
- **Boundary:** Search must not rebuild professional, Offering, Job, candidate privacy, healthcare, verification, moderation, or hold policy.
- **Build rule:** Require owner-issued decisions and source version; Search only composes them into index, update, or removal.

### SH-025 — `authorizeOrderEntitlement`

- **Plain English:** Confirm that an authoritative Order currently permits a requested booking, file, download, playback, or delivery action.
- **Owner:** Transaction / Order
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Order remains transaction truth; delivery Modules retain their own grant and usage policy.
- **Build rule:** Return Order state, participant relationship, qualifying line/item, refund/dispute effects, and decision evidence.

### SH-026 — `authorizeContextualResourceAccess`

- **Plain English:** Return the business-context decision required before Media, video, location, resume, agreement, or digital access is granted.
- **Owner:** Relevant context owner
- **Classification:** Shared contract; separate implementations
- **Status:** Confirmed
- **Boundary:** Role authority, contextual entitlement, healthcare policy, and resource mechanics remain separate gates.
- **Build rule:** Use owner-specific implementations with one response shape; prohibit a generic service that infers all domains.

### SH-027 — `resolveLocationReveal`

- **Plain English:** Decide whether an exact private location may be decrypted and shown to a particular viewer in an Order or Booking context.
- **Owner:** Location Safety
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** General authorization and paid status are inputs, not location-reveal truth.
- **Build rule:** Return reveal eligibility, permitted precision, expiry/revocation context, and create LocationReveal proof.

### SH-028 — `applyFuzzyPublicLocation`

- **Plain English:** Return an approved approximate public location instead of exact coordinates.
- **Owner:** Location Safety
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Search and business Modules decide display/filter use but may not perform their own coordinate fuzzing.
- **Build rule:** Expose stable fuzzy coordinates/area, radius, expiry, and source version without exact-location leakage.

## C. Audit, Observability, and Notification

### SH-029 — `appendAuditEvent`

- **Plain English:** Append generic proof that an important actor or system action occurred.
- **Owner:** Audit / Event Ledger
- **Classification:** Platform audit capability
- **Status:** Confirmed
- **Boundary:** AuditEvent does not replace domain lifecycle records, provider dedupe records, or operational failures.
- **Build rule:** Expose an insert-only command with actor, action, target, outcome, request ID, and schema-validated safe metadata.
- **Candidate aliases / narrower variants:** recordAuditEvent; writeAuditEvent; Generic audit event append

### SH-030 — `recordSensitiveAccess`

- **Plain English:** Append proof that protected data or access credentials were viewed, issued, downloaded, denied, blocked, or redacted.
- **Owner:** Audit / Event Ledger
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The data-owning Module determines sensitivity, authorization, and safe context.
- **Build rule:** Use AccessAuditLog with normalized actions, sensitivity, decision, target references, request context, and payload minimization.
- **Candidate aliases / narrower variants:** appendSensitiveAccessLog; appendSensitiveAccessAudit; writeSensitiveAccessLog; Sensitive-access logging

### SH-031 — `appendDomainLifecycleEvent`

- **Plain English:** Append an immutable domain-owned transition record transactionally with the owning aggregate change.
- **Owner:** Shared persistence mechanism; each domain owns truth
- **Classification:** Shared mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** OrderEvent, BookingEvent, JobInterviewEvent, UserSecurityEvent, PointLedgerEntry, and similar records must not be merged.
- **Build rule:** Provide insert-only repository conventions, actor/time capture, optional hash support, and transaction hooks.
- **Candidate aliases / narrower variants:** appendDomainEvent; Domain event ledger append; appendDomainLedgerEntry (mechanism only); recordDomainAccessEvent (domain-specific variant)

### SH-032 — `createRequestContext`

- **Plain English:** Create and propagate request, correlation, trace, environment, and actor identifiers across synchronous and asynchronous work.
- **Owner:** Observability / platform infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Only safe identifiers may enter telemetry; domain payloads remain source-owned.
- **Build rule:** Use async context propagation and include correlation IDs in provider calls, jobs, audit requests, and logs.

### SH-033 — `writeStructuredLog`

- **Plain English:** Emit consistent machine-readable operational logs.
- **Owner:** Observability / Ops
- **Classification:** Platform capability
- **Status:** Confirmed
- **Boundary:** Logs diagnose execution and must not become business or compliance truth.
- **Build rule:** Implement one logger with controlled fields, levels, environments, redaction, and request context.

### SH-034 — `sanitizeTelemetryMetadata`

- **Plain English:** Remove secrets, PHI, payment data, credentials, raw documents, and unnecessary personal data from telemetry and audit metadata.
- **Owner:** Observability / Ops and Audit payload policy
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Domain owners supply sensitivity labels; telemetry owners enforce accepted shapes and size limits.
- **Build rule:** Use allowlists, sensitive-key detection, truncation, safe serialization, and test fixtures for prohibited fields.

### SH-035 — `captureException`

- **Plain English:** Send an exception to the monitoring provider with safe grouping and request context.
- **Owner:** Observability / Ops
- **Classification:** Provider adapter
- **Status:** Confirmed
- **Boundary:** Feature Modules provide operation context but must not instantiate separate Sentry clients.
- **Build rule:** Wrap the provider once; apply sampling, release/environment tags, redaction, and correlation IDs.

### SH-036 — `emitMetric`

- **Plain English:** Publish counters, gauges, timings, queue depth, retries, and failure rates through one metrics client.
- **Owner:** Observability / Ops
- **Classification:** Platform capability
- **Status:** Confirmed
- **Boundary:** Metric semantics remain operational; avoid user-level high-cardinality dimensions.
- **Build rule:** Define a naming registry, allowed dimensions, cardinality limits, and alert ownership.

### SH-037 — `recordIntegrationFailure`

- **Plain English:** Persist normalized operational evidence that a provider, worker, or integration failed or degraded.
- **Owner:** Observability / Ops
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** The owning Module still writes any business-relevant failure status. IntegrationFailure does not replace domain truth.
- **Build rule:** Accept provider, operation, source reference, safe diagnostics, retryability, request ID, and incident linkage.
- **Candidate aliases / narrower variants:** appendOperationalFailure; recordOperationalFailure; reportIntegrationFailure; Operational failure recording

### SH-038 — `recordQueueTelemetry`

- **Plain English:** Record queue claim, attempt, heartbeat, duration, retry, completion, and dead-letter state.
- **Owner:** Observability / Ops / queue infrastructure
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Queue telemetry does not replace the owning Module’s workflow or target status.
- **Build rule:** Instrument the shared worker runner and expose QueueJob/metrics without custom per-Module queue ledgers.

### SH-039 — `checkServiceHealth`

- **Plain English:** Return standardized healthy, degraded, unavailable, or delayed status for an application component or dependency.
- **Owner:** Observability / Ops coordinates; owner supplies check
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Each owner defines what health means for its source truth and provider.
- **Build rule:** Register typed health checks with bounded timeouts, no sensitive payloads, and readiness/liveness separation.

### SH-040 — `correlateOpsIncident`

- **Plain English:** Group related failures, system events, queue signals, and alerts into one operational incident.
- **Owner:** Observability / Ops
- **Classification:** Module-internal public ops interface
- **Status:** Confirmed
- **Boundary:** Business Modules must not create competing generic incident systems.
- **Build rule:** Use correlation IDs, grouping rules, severity, assignment, mitigation, and resolution transitions.

### SH-041 — `requestNotification`

- **Plain English:** Submit a business, security, compliance, or operational alert through one canonical delivery interface.
- **Owner:** Notification
- **Classification:** Platform notification capability
- **Status:** Confirmed
- **Boundary:** The source Module owns the triggering event and message meaning; Notification owns routing, persistence, and delivery.
- **Build rule:** Use a typed command with recipients, template key, sensitivity, priority, variables, idempotency key, and action route.
- **Candidate aliases / narrower variants:** sendNotification; enqueueNotification; dispatchNotification; dispatchWorkflowNotification; requestNotificationDelivery; Notification request

### SH-042 — `renderNotificationTemplate`

- **Plain English:** Render validated, localized, channel-specific content from a named/versioned template.
- **Owner:** Notification
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Legal or business owners approve meaning and versions; Notification enforces safe variables and channel limits.
- **Build rule:** Centralize template rendering and variable schemas; prohibit per-Module provider dispatch and ad hoc HTML builders.

### SH-043 — `resolveNotificationRecipients`

- **Plain English:** Resolve domain-owned recipient groups into concrete User IDs while retaining delivery routing in Notification.
- **Owner:** Source context owner plus Notification
- **Classification:** Shared contract; separate policy
- **Status:** Confirmed
- **Boundary:** Organization roles, Thread participants, Order parties, and other recipient facts remain with their owners.
- **Build rule:** Expose owner-specific recipient queries and let Notification handle dedupe, channel preference, and fan-out.

## D. Reliability, Concurrency, Events, and Workflow

### SH-044 — `executeIdempotentCommand`

- **Plain English:** Ensure a retried command produces one business effect and can replay the original result.
- **Owner:** Platform application infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Each Module defines semantic command identity, conflict rules, and valid replay behavior.
- **Build rule:** Use request fingerprint, idempotency key, atomic claim/result persistence, transaction boundary, and expiry policy.
- **Candidate aliases / narrower variants:** withIdempotency; applyIdempotencyKey; enforceIdempotentCommand; idempotentCommandExecution; runIdempotentCommand

### SH-045 — `deduplicateDomainEvent`

- **Plain English:** Prevent one published domain event from causing the same consumer-side effect more than once.
- **Owner:** Platform event infrastructure; consumer owns inbox
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** A consumer’s processed-event identity and side effect remain domain-specific.
- **Build rule:** Use transactional inbox claims keyed by event ID plus handler/version, with idempotent completion.

### SH-046 — `publishDomainEvent`

- **Plain English:** Reliably publish a versioned domain event after the source-of-truth transaction commits.
- **Owner:** Platform event/outbox infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** The source Module owns event names, payload meaning, privacy filtering, and emission conditions.
- **Build rule:** Use a transactional outbox, stable envelope, aggregate version, correlation/causation IDs, retries, and schema versioning.
- **Candidate aliases / narrower variants:** publishOutboxEvent; publishTransactionalDomainEvent; transactional outbox; publishDomainEvent

### SH-047 — `enqueueReliableJob`

- **Plain English:** Persist asynchronous work with correlation, retries, leases, and visible terminal failure.
- **Owner:** Shared queue infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** The owning Module defines payload, completion meaning, and business state; QueueJob is operational only.
- **Build rule:** Provide one queue client/worker shell with idempotency, lease, heartbeat, dead-letter, and telemetry.
- **Candidate aliases / narrower variants:** enqueueRetryableJob; enqueueBackgroundJob; enqueueIdempotentJob; enqueueDomainJob; enqueueReliableWork

### SH-048 — `executeRetryWithBackoff`

- **Plain English:** Retry transient technical failures while stopping on permanent, unsafe, or manual-review failures.
- **Owner:** Shared queue/platform infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** The domain/provider owner classifies retryability and legal side effects.
- **Build rule:** Use bounded exponential backoff, jitter, max attempts, timeout, circuit breaking, and dead-letter routing.
- **Candidate aliases / narrower variants:** retryQueuedWork; executeWithRetry; runQueuedJobWithRetry; runRetryableProviderOperation; processQueueRetryAndDeadLetter

### SH-049 — `orchestrateWorkflowSteps`

- **Plain English:** Persist and execute a multi-step cross-Module sequence without taking ownership of participant truth.
- **Owner:** Workflow-owning Module using shared runner
- **Classification:** Shared mechanism; separate workflow truth
- **Status:** Confirmed
- **Boundary:** Booking, Order, Privacy, Moderation, and Dispute sequences retain separate run/step semantics.
- **Build rule:** Provide reusable run/step, dependency, retry, compensation, correlation, and acknowledgment primitives.

### SH-050 — `reconcileWorkflowStatus`

- **Plain English:** Aggregate child-step outcomes into the owning workflow’s parent status.
- **Owner:** Workflow owner using shared helper
- **Classification:** Shared mechanism; separate policy
- **Status:** Confirmed
- **Boundary:** Completed, partial, failed, retained, skipped, or compensated meanings remain workflow-specific.
- **Build rule:** Provide deterministic aggregation hooks; never encode all domain statuses in one generic table.

### SH-051 — `acquireAggregateLock`

- **Plain English:** Serialize conflicting commands against the same aggregate or constrained resource.
- **Owner:** Shared persistence infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** The Module defines lock key, conflicting actions, and safe retry behavior.
- **Build rule:** Prefer Postgres row/advisory locks or serializable transactions; prohibit in-memory mutexes for distributed work.
- **Candidate aliases / narrower variants:** acquireDomainLock; acquireContextLock; lockMutableAggregate; lockAggregateForTransition; concurrencyGuard; acquireResourceLock

### SH-052 — `withOptimisticConcurrency`

- **Plain English:** Reject stale writes when the expected aggregate version or updatedAt value no longer matches.
- **Owner:** Shared persistence infrastructure
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Each lifecycle owner defines whether to retry, merge, or return conflict.
- **Build rule:** Use version columns or compare-and-set updates and include current version in conflict results.

### SH-053 — `transitionLifecycleState`

- **Plain English:** Apply reusable state-machine plumbing while preserving each Module’s transition graph and invariants.
- **Owner:** Shared mechanism; lifecycle owner supplies policy
- **Classification:** Shared mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** No generic policy table may own Order, Booking, Job, Review, Hold, or other lifecycle semantics.
- **Build rule:** Provide transition validation, transactional update, event hook, and explicit reason/actor metadata.

### SH-054 — `claimWorkItem`

- **Plain English:** Prevent multiple reviewers or workers from simultaneously owning the same manual-review item.
- **Owner:** Shared work-queue/locking capability
- **Classification:** Cross-cutting capability
- **Status:** Proposed ruling
- **Boundary:** Reviewer eligibility, assignment, lease duration, escalation, and decision remain with the review owner.
- **Build rule:** Use transactional claim/lease, optimistic versioning, reassignment, expiry, and audit hooks.

### SH-055 — `runDeadlineExpiration`

- **Plain English:** Find time-bound records whose deadline passed and invoke their owner-defined expiration transition.
- **Owner:** Shared scheduler/queue infrastructure
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Gig, grant, subscription, hold, booking, and session expiration rules remain local.
- **Build rule:** Use cursor batching, owner command dispatch, idempotency, retries, and clock-controlled tests.

### SH-056 — `executeAtomicReservation`

- **Plain English:** Atomically reserve scarce value or inventory so concurrent commands cannot overspend or over-allocate it.
- **Owner:** Shared database primitive
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Points, reward inventory, funds, slots, and other reserves retain domain-specific sufficiency and release rules.
- **Build rule:** Use a transaction plus row/range lock, reservation proof where needed, and idempotent release/commit.

### SH-057 — `consumeCounterAtomically`

- **Plain English:** Increment a bounded counter and enforce its maximum without concurrency races.
- **Owner:** Shared database primitive
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Usage period, maximum, quantity, reversal, and denial semantics remain with the owning Module.
- **Build rule:** Use atomic upsert/compare-and-update or row lock and return a receipt containing before/after/remaining.

### SH-058 — `acquireIntervalLock`

- **Plain English:** Reserve a time interval and reject prohibited overlap.
- **Owner:** Booking & Calendar policy over shared Postgres mechanism
- **Classification:** Cluster-local capability
- **Status:** Confirmed
- **Boundary:** Booking owns active interval and conflict policy; Job Interview may consume a distinct scheduling interface but not BookingSlotLock truth.
- **Build rule:** Use range types/exclusion constraints and transactionally create the booking hold or lock.

## E. Provider and External-System Adapters

### SH-059 — `verifyProviderWebhookSignature`

- **Plain English:** Verify raw webhook bytes, timestamp, and provider signature before accepting an external event.
- **Owner:** Shared integration-security shell; provider adapter supplies algorithm
- **Classification:** Provider-adapter contract
- **Status:** Confirmed
- **Boundary:** Provider secrets, accepted endpoints, algorithms, tolerance, and event types remain adapter-local.
- **Build rule:** Build one raw-body verifier contract and provider implementations; reject before parsing or side effects.
- **Candidate aliases / narrower variants:** verifyWebhookSignature; verifyProviderWebhook; verifyWebhookSignature; Webhook signature verification

### SH-060 — `deduplicateProviderEvent`

- **Plain English:** Atomically claim a provider event so the same callback cannot repeat side effects.
- **Owner:** Provider-owning Module using shared primitive
- **Classification:** Shared mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** ProcessedStripeEvent, ProcessedCalendarEvent, ProcessedVideoProviderEvent, verification, subscription, and notification event records stay separate.
- **Build rule:** Use provider + event ID uniqueness, payload hash, processing result, and one transaction around claim and domain command.
- **Candidate aliases / narrower variants:** Provider-event deduplication; verifyAndDeduplicateProviderWebhook (dedupe portion)

### SH-061 — `translateProviderStatus`

- **Plain English:** Convert provider-native statuses and errors into the owning Module’s canonical result and transition vocabulary.
- **Owner:** Provider-owning adapter
- **Classification:** Provider-adapter contract
- **Status:** Confirmed
- **Boundary:** Payment, calendar, video, verification, subscription, notification, storage, and fulfillment mappings must not be centralized.
- **Build rule:** Require explicit mapping tables, unknown-status handling, mapping version, and normalized result envelope.
- **Candidate aliases / narrower variants:** Provider-status translation; translateProviderResult; translateProviderFailure (operational mapping variant)

### SH-062 — `reconcileProviderState`

- **Plain English:** Compare Workin Ants source truth with provider state and safely repair missed or inconsistent effects.
- **Owner:** Each provider-owning Module using shared worker framework
- **Classification:** Shared mechanism; separate policy
- **Status:** Confirmed
- **Boundary:** Only the owner decides which discrepancies can be repaired automatically.
- **Build rule:** Use pagination/cursors, time windows, dry run, discrepancy report, idempotent repair commands, and incident creation.

### SH-063 — `captureProviderSnapshot`

- **Plain English:** Preserve a timestamped, immutable representation of provider state needed for explanation, support, or audit.
- **Owner:** Provider-owning Module
- **Classification:** Shared snapshot mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** The fields and domain meaning remain adapter- and Module-specific.
- **Build rule:** Store normalized fields, provider/account reference, source event, schema version, and payload hash; avoid secrets/raw sensitive payloads.

### SH-064 — `authorizeExternalProviderConnection`

- **Plain English:** Initiate an OAuth, hosted authorization, checkout, or linked-account flow owned by an integration Module.
- **Owner:** Provider-owning Module
- **Classification:** Provider-adapter capability
- **Status:** Confirmed
- **Boundary:** Consent proof may be a precondition, but Consent & Disclosure does not own the external connection.
- **Build rule:** Use state/nonce, redirect allowlist, scoped permissions, callback validation, encryption, and provider-reference lifecycle.

### SH-065 — `invokeFoundationModel`

- **Plain English:** Invoke a configured foundation model with request correlation, timeout, retry classification, and safe telemetry.
- **Owner:** AI Taxonomy initially; broader AI infrastructure ownership unresolved
- **Classification:** Provider-adapter capability
- **Status:** Proposed ruling
- **Boundary:** Prompts, taxonomy semantics, policy, confidence, and output meaning remain with the consuming AI Module.
- **Build rule:** Expose a provider-neutral port with Bedrock implementation, model/version capture, token limits, and no unnecessary sensitive input.

### SH-066 — `validateStructuredProviderOutput`

- **Plain English:** Parse and validate structured provider output before any domain workflow uses it.
- **Owner:** Shared validation primitive; consuming Module owns schema
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Exact AI/provider schema, referenced IDs, confidence rules, and semantic validation remain local.
- **Build rule:** Use Zod/JSON Schema, reject unknown fields, produce typed failures, and never trust provider JSON directly.

### SH-067 — `invokeCalendarProvider`

- **Plain English:** Create, update, cancel, and synchronize external calendar resources through a provider-neutral adapter.
- **Owner:** Booking & Calendar
- **Classification:** Module provider interface
- **Status:** Confirmed
- **Boundary:** Job Interview supplies interview policy; Booking owns calendar connection, busy-window, sync, and provider mechanics.
- **Build rule:** Provide Cronofy adapter methods, idempotent request keys, normalized results, webhook/reconciliation support, and safe event descriptions.

### SH-068 — `invokeVideoProvider`

- **Plain English:** Provision rooms/assets and issue provider-bound playback or join credentials through a provider-neutral video adapter.
- **Owner:** Video Infrastructure
- **Classification:** Module provider interface
- **Status:** Confirmed
- **Boundary:** Booking and Job Interview own parent lifecycle and participant context; Video owns provider resources and canonical video state.
- **Build rule:** Separate live-room and on-demand asset ports; enforce time windows, participant claims, deletion, callbacks, and status mapping.

### SH-069 — `geocodeAddress`

- **Plain English:** Convert a protected normalized address into provider coordinates without making the provider response platform truth.
- **Owner:** Location Safety adapter ownership proposed
- **Classification:** Provider-adapter capability
- **Status:** Proposed ruling
- **Boundary:** Location Safety owns storage, fuzzing, precision, retention, and reveal policy.
- **Build rule:** Use input normalization, purpose restriction, rate limiting, timeout/retry, normalized response, and no public exact-coordinate leakage.

### SH-070 — `deleteProviderResource`

- **Plain English:** Delete or revoke an external provider resource after an authorized privacy, moderation, security, or lifecycle command.
- **Owner:** Provider-owning Module
- **Classification:** Provider-adapter contract
- **Status:** Confirmed
- **Boundary:** Privacy or Moderation owns the instruction; the provider Module owns deletion mechanics and resulting local state.
- **Build rule:** Return typed deleted, absent, retained, retryable-failure, or terminal-failure result with provider evidence.

### SH-071 — `publishRealtimeChange`

- **Plain English:** Publish committed changes to authorized connected clients through one realtime adapter.
- **Owner:** Platform realtime adapter; Messaging is primary consumer
- **Classification:** Infrastructure adapter
- **Status:** Proposed ruling
- **Boundary:** The source Module defines safe payload and audience; realtime delivery is not source truth.
- **Build rule:** Use authorized channel names, participant filtering, event version, health/fallback behavior, and no sensitive overbroadcast.

## F. Security, Cryptography, Data Normalization, and Media

### SH-072 — `hashCanonicalPayload`

- **Plain English:** Create a stable cryptographic digest over canonical bytes or fields for integrity, idempotency, provenance, or comparison.
- **Owner:** Shared security/cryptography capability
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Each owner defines canonical input and what the hash proves. Media checksum, agreement hash, consent text hash, and AI input hash remain distinct meanings.
- **Build rule:** Use SHA-256 or versioned HMAC as appropriate, canonical serialization, purpose/version metadata, and test vectors.

### SH-073 — `hashChainRecords`

- **Plain English:** Cryptographically link ordered evidence records so alteration, deletion, or reordering can be detected.
- **Owner:** Shared cryptographic capability; ownership unresolved
- **Classification:** Cross-cutting primitive
- **Status:** Proposed ruling
- **Boundary:** Audit and Agreement owners retain separate chain partitions, canonical fields, and integrity-failure policy.
- **Build rule:** Use previous hash, entry hash, canonical serialization, chain head, atomic sequence allocation, and verification worker.

### SH-074 — `generateSecureToken`

- **Plain English:** Generate an unguessable secret while storing only a hash or protected representation.
- **Owner:** Shared security capability
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Grant TTL, binding, usage, and revocation remain domain-specific.
- **Build rule:** Use cryptographically secure randomness, purpose-bound hash, constant-time verification, rotation/version metadata, and one-time display.

### SH-075 — `encryptSensitiveValue`

- **Plain English:** Encrypt data that must later be recovered using managed keys and versioned envelope encryption.
- **Owner:** Shared security/cryptography capability
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Identity, location, notification, healthcare, payment, and agreement owners decide necessity, access, rotation effects, and retention.
- **Build rule:** Centralize KMS/envelope encryption, authenticated encryption, key version, access audit, and rotation tooling.

### SH-076 — `normalizeAndHashIdentifier`

- **Plain English:** Normalize a sensitive identifier or request attribute and create a stable non-plaintext comparison value.
- **Owner:** Shared security/cryptography capability
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** Jurisdiction-specific license normalization, IP evidence needs, phone lookup rules, and retention remain local.
- **Build rule:** Use purpose-specific keyed HMAC, normalization version, key rotation, collision-safe storage, and no raw value in logs.

### SH-077 — `buildCanonicalTextSnapshot`

- **Plain English:** Build deterministic normalized text/field input for scanning, hashing, comparison, or decision provenance.
- **Owner:** Shared text canonicalization mechanism
- **Classification:** Cross-cutting primitive
- **Status:** Confirmed
- **Boundary:** Each Module defines included fields, interpretation, and canonicalization version.
- **Build rule:** Use stable ordering, Unicode normalization, newline/whitespace policy, explicit version, and snapshot hash.

### SH-078 — `minimizeAndRedactProviderInput`

- **Plain English:** Construct the minimum purpose-bound payload allowed to leave Workin Ants for a provider.
- **Owner:** Source-data owner supplies policy; shared serializer enforces
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Candidate privacy, healthcare, payment, identity, and other sensitivity policies cannot be recreated by the provider consumer.
- **Build rule:** Use field allowlists, sensitivity labels, redaction/tokenization, purpose code, schema validation, and telemetry-safe copy.

### SH-079 — `normalizeControlledTerm`

- **Plain English:** Normalize case, whitespace, punctuation, Unicode, and slug form before matching controlled vocabulary.
- **Owner:** Taxonomy & Classification policy over shared text primitive
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Canonical matching, alias, collisions, hierarchy, and acceptance into taxonomy remain Taxonomy-owned.
- **Build rule:** Provide deterministic normalized key and slug helper; consumers never create taxonomy terms directly.

### SH-080 — `manageVersionedRules`

- **Plain English:** Activate, retire, and resolve effective-dated, jurisdiction- or context-scoped rule/configuration versions.
- **Owner:** Each policy Module using shared versioning mechanism
- **Classification:** Shared mechanism; separate policy
- **Status:** Confirmed
- **Boundary:** Employment, healthcare, tax, moderation, consent, and other rule meanings remain separate.
- **Build rule:** Use immutable versions, effective intervals, status, jurisdiction/context, validation, provenance, and no in-place mutation.

### SH-081 — `runPatternScanner`

- **Plain English:** Run configured text patterns and return raw structured matches with offsets and scanner version.
- **Owner:** Shared scanner mechanism; policy owner unresolved
- **Classification:** Cross-cutting capability
- **Status:** Proposed ruling
- **Boundary:** Job Compliance or Moderation interprets matches, severity, legal meaning, and final decision.
- **Build rule:** Separate tokenizer/pattern execution from policy; return deterministic offsets, rule IDs, and scanner version.

### SH-082 — `validateUploadedFile`

- **Plain English:** Validate file size, extension, claimed MIME, binary signature, encryption/archive restrictions, and upload context.
- **Owner:** Media / File Access
- **Classification:** Cross-cutting media capability
- **Status:** Confirmed
- **Boundary:** Context owners decide whether a clean ready MediaAsset is suitable for their business attachment.
- **Build rule:** Use MediaUploadPolicy, server-side byte inspection, quarantine-first flow, standardized rejection reasons, and fail closed.

### SH-083 — `scanFileForMalware`

- **Plain English:** Scan untrusted bytes and prevent infected or unscanned required files from becoming ready.
- **Owner:** Media / File Access
- **Classification:** Cross-cutting media capability
- **Status:** Confirmed
- **Boundary:** MediaUploadPolicy controls whether scanning is required; context Modules do not own scanner proof.
- **Build rule:** Use one scanner adapter, retry classification, quarantine, immutable scan result, signatures/version, and fail-closed status.

### SH-084 — `scrubFileMetadata`

- **Plain English:** Remove EXIF, GPS, PDF metadata, and other unnecessary identifying information before publication or access.
- **Owner:** Media / File Access
- **Classification:** Cross-cutting media capability
- **Status:** Confirmed
- **Boundary:** Required processing varies by MediaUploadContext and policy.
- **Build rule:** Implement deterministic processing actions, original/derivative linkage, checksums, and processing-result proof.

### SH-085 — `generatePrivateObjectKey`

- **Plain English:** Generate an opaque provider object key that does not expose or execute the user-supplied filename.
- **Owner:** Media / File Access / storage primitive
- **Classification:** Platform storage primitive
- **Status:** Confirmed
- **Boundary:** Media chooses bucket class, quarantine/promoted path, visibility, and derivative context.
- **Build rule:** Use UUID/random identifiers, controlled path segments, reserved-character avoidance, and retain original name only as protected metadata if needed.

### SH-086 — `calculateChecksum`

- **Plain English:** Hash stored bytes to prove binary integrity and transformation relationships.
- **Owner:** Shared hash primitive consumed by Media
- **Classification:** Platform primitive
- **Status:** Confirmed
- **Boundary:** A file checksum is not legal agreement proof unless the Agreement owner binds it to its snapshot.
- **Build rule:** Calculate SHA-256 on upload and derivatives; store algorithm/version and compare using exact bytes.

### SH-087 — `issueSignedMediaUrl`

- **Plain English:** Issue a short-lived provider URL for a private MediaAsset after authority and contextual entitlement gates pass.
- **Owner:** Media / File Access
- **Classification:** Cross-cutting media capability
- **Status:** Confirmed
- **Boundary:** A signed URL is a delivery mechanism, not entitlement. Domain grant records remain separate.
- **Build rule:** Validate MediaAsset readiness/freeze/erasure, grant, action, TTL, response headers, and record issuance/access evidence.
- **Candidate aliases / narrower variants:** issueSignedObjectUrl; issueTemporaryMediaAccess; issueTemporaryFileAccess; Signed media URL issuance

### SH-088 — `manageTemporaryAccessGrant`

- **Plain English:** Apply common issue, validate, expire, deny, use, and revoke mechanics to a domain-owned temporary grant.
- **Owner:** Shared grant mechanism; each domain owns its record
- **Classification:** Shared mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** SensitiveActionSession, MediaAccessGrant, AgreementAccessGrant, DigitalDownloadGrant, CourseVideoPlaybackGrant, and LocationReveal must not merge.
- **Build rule:** Provide common status/expiry/token/actor/target helpers while retaining separate schemas, enums, repositories, and policy.
- **Candidate aliases / narrower variants:** temporaryAccessGrantPrimitive; temporaryAccessGrantMechanism; manageTemporaryAccessState; Temporary access grants

### SH-089 — `revokeTemporaryAccessGrant`

- **Plain English:** Revoke applicable domain-owned grants after moderation, privacy, refund, security, or lifecycle changes.
- **Owner:** Each grant owner using shared primitive
- **Classification:** Cross-cutting command pattern
- **Status:** Confirmed
- **Boundary:** The instructing Module supplies authority; each grant owner performs its own transition and evidence.
- **Build rule:** Use typed revocation request, reason/source reference, idempotency, cascade registry, and domain event/access log.

### SH-090 — `attachValidatedMedia`

- **Plain English:** Attach a ready MediaAsset to a business object using a contextual join owned by that business Module.
- **Owner:** Contextual domain Module; Media owns asset truth
- **Classification:** Shared contract; separate contextual truth
- **Status:** Confirmed
- **Boundary:** OfferingMedia, GigMedia, MessageMedia, OrderFile, resume links, and similar joins retain distinct roles and lifecycles.
- **Build rule:** Require ready asset, valid upload context, actor authorization, role/sort metadata, and transactional join creation.

## G. Search, Privacy, Moderation, and Evidence

### SH-091 — `requestSearchProjectionRefresh`

- **Plain English:** Provide one controlled command for source Modules to request index, update, hide, remove, or restore work.
- **Owner:** Search / Public Visibility
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** Source Modules do not write SearchUpsertEvent or call Typesense directly.
- **Build rule:** Validate SearchEntityType, entity ID, action, reason, source version, requester Module, and idempotency key.
- **Candidate aliases / narrower variants:** enqueueSearchProjection; enqueueProjectionUpdate; enqueueProjectionWork; requestSearchProjectionUpdate; enqueueSearchProjectionChange; deindexEntity

### SH-092 — `writeSearchProjection`

- **Plain English:** Create, replace, batch, or delete a provider search document through one adapter and collection registry.
- **Owner:** Search / Public Visibility
- **Classification:** Provider adapter
- **Status:** Confirmed
- **Boundary:** Each collection retains distinct schema, visibility, ranking, and document identity policy.
- **Build rule:** Centralize Typesense client, health, schema/version management, error translation, batch operations, and protected/public collection boundaries.

### SH-093 — `reconcileSearchProjection`

- **Plain English:** Compare authoritative searchable entities with provider documents and repair missing, stale, or orphaned projections.
- **Owner:** Search / Public Visibility
- **Classification:** Module-internal worker using shared queue
- **Status:** Confirmed
- **Boundary:** Source Modules expose approved projection inputs but never run their own Typesense reconciliation.
- **Build rule:** Use cursor/checkpoint, dry run, projection version, orphan deletion, privacy/moderation verification, and repair report.

### SH-094 — `buildSourceProjection`

- **Plain English:** Produce the privacy-safe source projection that Search is allowed to index.
- **Owner:** Each source Module
- **Classification:** Shared pattern; separate source projection
- **Status:** Confirmed
- **Boundary:** CandidateSearchProjection remains Candidate-owned; other entities supply their own approved document source. Search does not reconstruct raw private truth.
- **Build rule:** Use deterministic versioned builders, allowlisted fields, public-readiness decision, safe location/trust signals, and rebuild support.

### SH-095 — `executePrivacyInstruction`

- **Plain English:** Execute erase, anonymize, export, restrict, detach, revoke, delete-provider, or retain action against one Module’s owned records.
- **Owner:** Privacy orchestrates; each data owner executes
- **Classification:** Cross-cutting protocol
- **Status:** Confirmed
- **Boundary:** Feature Modules must not create separate PrivacyRequest/DataErasureJob workflows; Privacy must not directly rewrite every owner’s tables.
- **Build rule:** Define target request/result types, idempotency, retries, evidence, provider result, and retained/skipped/failure outcomes.
- **Candidate aliases / narrower variants:** executePrivacyTarget; executeErasureTarget; processPrivacyErasureTarget; executePrivacyErasureTarget; applyPrivacyDisposition; executePrivacyTargetAction

### SH-096 — `enumerateSubjectData`

- **Plain English:** Return the records and provider references a Module holds about a data subject and the supported privacy dispositions.
- **Owner:** Each data-owning Module through Privacy-defined interface
- **Classification:** Cross-cutting protocol
- **Status:** Confirmed
- **Boundary:** Privacy coordinates inventory; owners know their schema, relationships, and export meaning.
- **Build rule:** Require stable target types, identifiers, sensitivity, retention candidates, export serializer, and cursoring.

### SH-097 — `evaluateRetentionRequirement`

- **Plain English:** Return whether owner-held data must be retained and what anonymization remains permitted.
- **Owner:** Data owner supplies facts; Privacy records exemption
- **Classification:** Cross-cutting protocol
- **Status:** Confirmed
- **Boundary:** Privacy does not independently decide tax, contract, fraud, dispute, security, or legal retention facts. Owners do not create parallel exemption systems.
- **Build rule:** Return required, reason code, legal/policy basis, retainUntil, minimum fields, permitted anonymization, and source reference.
- **Candidate aliases / narrower variants:** applyRetentionDecision; applyRetentionExemption; retainLegallyRequiredRecord; resolveRetentionDecision; handleRetentionDecision

### SH-098 — `anonymizePersonalFields`

- **Plain English:** Apply approved field-level pseudonymization or scrubbing while preserving required relational and compliance truth.
- **Owner:** Shared primitive; record owner supplies mapping
- **Classification:** Cross-cutting capability
- **Status:** Confirmed
- **Boundary:** Each owner decides exact fields and invariants; no global crawler bypasses Module policy.
- **Build rule:** Use versioned field maps, deterministic pseudonyms where needed, referential strategy, dry run, and result proof.

### SH-099 — `orchestratePrivacyFulfillment`

- **Plain English:** Own verification, target discovery, ordering, retention exemptions, execution, aggregation, export, and completion of a privacy request.
- **Owner:** Privacy / Data Erasure
- **Classification:** Module-internal orchestration with public interfaces
- **Status:** Confirmed
- **Boundary:** PrivacyRequest, DataErasureJob, DataErasureTarget, DataRetentionExemption, and DataExportBundle remain Privacy truth.
- **Build rule:** Use shared queues/audit/authorization, owner executors, deadlines, retries, partial completion, and final evidence.

### SH-100 — `createPrivacyExportArtifact`

- **Plain English:** Assemble, encrypt, store privately, and temporarily deliver a user privacy export.
- **Owner:** Privacy owns bundle; Media/storage owns object mechanics
- **Classification:** Cluster-local capability
- **Status:** Confirmed
- **Boundary:** Export contents and eligibility remain Privacy policy; signed URL/storage mechanics remain Media.
- **Build rule:** Create manifest, per-owner sections, archive hash/encryption, expiry/cleanup, MediaAccessGrant, and sensitive-access audit.

### SH-101 — `submitModerationReport`

- **Plain English:** Submit an abuse, safety, copyright, privacy, spam, harassment, or legal allegation against a typed target.
- **Owner:** Content Moderation & Legal Notice
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** The content-bearing Module supplies target/evidence context but does not create competing Report or ModerationCase truth.
- **Build rule:** Use typed target, reason/source, reporter context, evidence references, idempotency, rate limits, and intake status.

### SH-102 — `resolveModerationTarget`

- **Plain English:** Resolve a typed moderation target into a validated, minimized reviewer summary through the owning Module.
- **Owner:** Target registry contract; each owner supplies resolver
- **Classification:** Cross-cutting capability
- **Status:** Proposed ruling
- **Boundary:** No generic cross-domain repository may directly inspect every table. Moderation controls allowable target/action combinations.
- **Build rule:** Use typed target adapters, authorization, sensitivity/redaction, source version, and unavailable/erased outcomes.

### SH-103 — `executeModerationDecision`

- **Plain English:** Apply an authoritative moderation/legal action inside each affected source or delivery Module.
- **Owner:** Moderation owns decision; each target owner executes
- **Classification:** Cross-cutting protocol
- **Status:** Confirmed
- **Boundary:** Moderation does not directly mutate Media, Search, Messaging, Digital Goods, Video, or Marketplace tables.
- **Build rule:** Dispatch signed/authorized action envelope with case/action IDs; handlers return acknowledged, completed, failed, or restored evidence.

### SH-104 — `preserveEvidenceSnapshot`

- **Plain English:** Capture immutable or retention-protected content and metadata before enforcement can change it.
- **Owner:** Decision/evidence owner using Media and hash primitives
- **Classification:** Shared evidence mechanism; ownership case-specific
- **Status:** Proposed ruling
- **Boundary:** The proof record’s legal meaning remains with Moderation, Hold, Verification, or another decision owner; Audit does not absorb it.
- **Build rule:** Use canonical snapshot, private storage, hash, policy/source versions, chain of custody, retention lock, and controlled access.

### SH-105 — `correlateEnforcementResult`

- **Plain English:** Track acknowledgment, success, failure, retry, and reversal of each downstream step authorized by one moderation action.
- **Owner:** Content Moderation & Legal Notice
- **Classification:** Cluster-local orchestration
- **Status:** Proposed ruling
- **Boundary:** Downstream Modules retain execution truth; they do not create competing ModerationAction state.
- **Build rule:** Use action/step IDs, required-step policy, idempotent dispatch, acknowledgments, retries, reconciliation, and restoration logic.

### SH-106 — `computeContentFingerprint`

- **Plain English:** Generate exact or perceptual fingerprints used as duplicate or similarity signals for content review.
- **Owner:** Media / File Access or specialized adapter; ownership unresolved
- **Classification:** Provider/cross-cutting capability
- **Status:** Unresolved
- **Boundary:** A match is a signal, not proof of infringement or automatic enforcement.
- **Build rule:** Support checksum, perceptual image hash, audio/video fingerprint, provider version, threshold, and explainable result.

## H. Cluster-Local and Module-Owned Reusable Operations

### SH-107 — `createChargeableOrder`

- **Plain English:** Create an authoritative Order for a paid platform workflow and initiate the approved payment path.
- **Owner:** Transaction / Order
- **Classification:** Cluster-local public interface
- **Status:** Confirmed
- **Boundary:** The calling Module owns what is being bought; Order owns transaction snapshot and lifecycle; Payment owns provider rail.
- **Build rule:** Require buyer/customer actor, seller/platform context, item snapshot, price/tax inputs, consent, idempotency, and returned Order reference.

### SH-108 — `requestOrderRefund`

- **Plain English:** Submit an authorized refund decision to Order and Payment for execution and transaction recording.
- **Owner:** Transaction / Order coordinates; Payment executes provider rail
- **Classification:** Cluster-local public interface
- **Status:** Confirmed
- **Boundary:** Dispute/support owns adjudication reason; Order owns RefundStatus; Payment owns provider result.
- **Build rule:** Use amount, currency, reason, source decision, actor authority, idempotency, correlation, and asynchronous result events.

### SH-109 — `snapshotExternalDecision`

- **Plain English:** Freeze a policy, entitlement, pricing, commission, fee, tax, or priority decision at the moment a historical domain record is created.
- **Owner:** Consuming domain owner
- **Classification:** Shared snapshot pattern; separate truth
- **Status:** Confirmed
- **Boundary:** The policy owner supplies current decision; Order, Booking, or other consumer owns historical snapshot.
- **Build rule:** Store value, source plan/grant/record IDs, policy/version, evaluatedAt, relevant inputs, and hash where material.
- **Candidate aliases / narrower variants:** snapshotCommercialDecision; snapshotExternalPolicyDecision; snapshotDecisionInputs; recordPolicySnapshot

### SH-110 — `createDomainSnapshot`

- **Plain English:** Freeze source values when a downstream lifecycle requires immutable historical truth.
- **Owner:** Downstream lifecycle owner
- **Classification:** Shared snapshot pattern; separate truth
- **Status:** Confirmed
- **Boundary:** Marketplace supplies current Offering/PricingTier facts; Order owns transaction snapshot. Similar consumers own their own snapshots.
- **Build rule:** Use versioned immutable schema, source IDs/versions, copied values, provenance, and no later recalculation.

### SH-111 — `renderDocument`

- **Plain English:** Generate a document from a versioned template and frozen data through a provider-neutral renderer.
- **Owner:** Document-owning Module; Transaction / Order initially
- **Classification:** Cross-cutting document mechanism
- **Status:** Proposed ruling
- **Boundary:** Agreement template, signer, finalization, supersession, and legal meaning remain Transaction / Order policy.
- **Build rule:** Provide renderer port, deterministic template/version, asset embedding, hash, private storage handoff, retry/idempotency, and render metadata.

### SH-112 — `verifyAgreementDocumentHash`

- **Plain English:** Verify that a finalized Agreement document matches its retained bytes, version, and legal snapshot hash.
- **Owner:** Transaction / Order
- **Classification:** Module public/internal interface
- **Status:** Confirmed
- **Boundary:** Media verifies storage integrity only; it does not own Agreement finalization or supersession.
- **Build rule:** Read exact bytes, recompute hash, compare algorithm/version, record sensitive access/integrity result, and block on mismatch.

### SH-113 — `ensureContextThread`

- **Plain English:** Idempotently create or retrieve the one Messaging Thread permitted for a canonical business context.
- **Owner:** Messaging
- **Classification:** Module public interface
- **Status:** Confirmed
- **Boundary:** The source workflow decides context and participants; Messaging owns Thread, ThreadParticipant, uniqueness, and messaging lifecycle.
- **Build rule:** Require ThreadContextType, context ID, initial participants/roles, idempotency; enforce unique context and authorization.

### SH-114 — `provisionOneToOneProfile`

- **Plain English:** Idempotently create the actor-branch profile associated one-to-one with a User.
- **Owner:** Each profile Module using shared provisioning mechanism
- **Classification:** Shared mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** CustomerProfile may be automatic; CandidateProfile and ProfessionalProfile have different opt-in and readiness lifecycles.
- **Build rule:** Use unique userId, transactional upsert, owner defaults, idempotency, reconciliation, and owner-specific events.

### SH-115 — `buildAggregateProjection`

- **Plain English:** Build or rebuild a derived balance, leaderboard, rating, usage, or dashboard read model from authoritative records.
- **Owner:** Projection owner
- **Classification:** Shared projection mechanism; separate policy
- **Status:** Confirmed
- **Boundary:** Point balance, review rating, leaderboard, TrackUsageCounter, search, and customer dashboard projections retain distinct inclusion and ranking rules.
- **Build rule:** Use projection version, event/cursor checkpoint, idempotent writes, full rebuild, lag metrics, and source reconciliation.
- **Candidate aliases / narrower variants:** buildProjection; recomputeAggregateProjection; rebuildProjection; Candidate projection generation (specific implementation)

### SH-116 — `secureRandomSelection`

- **Plain English:** Select one or more entries using an unbiased cryptographically secure random source.
- **Owner:** Sweepstakes / Prize
- **Classification:** Module-internal capability over shared CSPRNG
- **Status:** Confirmed
- **Boundary:** Eligible population, weighting, winner count, replacement, redraw, repeat-winner, and proof remain Sweepstakes policy.
- **Build rule:** Use CSPRNG/unbiased sampling, frozen eligible population, seed/randomness evidence where appropriate, immutable run proof, and audit.

### SH-117 — `aggregateYearlyReportableValue`

- **Plain English:** Maintain a year-level total of reportable value with reconciliation and rebuild support.
- **Owner:** Each value-owning Module; tax consumes
- **Classification:** Shared aggregation mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** PrizeTaxYearSummary, TaxYearEarningsSummary, and reward value records remain separate.
- **Build rule:** Use source-event uniqueness, transactional increment, currency/jurisdiction/year key, reversal handling, and full reconciliation worker.

### SH-118 — `reportTaxableValue`

- **Plain English:** Send a recognized prize, reward, earning, or other reportable value to the tax-owning Module.
- **Owner:** Payment / Payout / Tax
- **Classification:** Cross-cutting public interface
- **Status:** Confirmed
- **Boundary:** The source Module owns fair-market-value snapshot and recognition event; Tax owns profile, threshold, summary, and filing truth.
- **Build rule:** Require subject, value/currency, jurisdiction, source type/ID, recognition date, valuation evidence, and idempotency.

### SH-119 — `applyTemporaryFeatureGrant`

- **Plain English:** Apply a deterministic time-bound platform benefit earned outside subscription billing.
- **Owner:** Track Subscription & Entitlement or affected feature owner
- **Classification:** Cross-cutting public interface; ownership partly unresolved
- **Status:** Proposed ruling
- **Boundary:** Gamification owns why the benefit was earned; Search or another feature owns effect; no reward may increase sweepstakes odds.
- **Build rule:** Represent source, entitlement/benefit key, effective interval, value, revocation, and consumption; avoid local feature flags.

### SH-120 — `normalizeJurisdictionContext`

- **Plain English:** Normalize country, region/state, city, postal, remote-role, and evidence source for a jurisdiction-dependent decision.
- **Owner:** Shared commerce/location capability ownership unresolved
- **Classification:** Cross-cutting capability
- **Status:** Unresolved
- **Boundary:** Tax, Job Compliance, and Location Safety retain separate authority rules and evidence requirements.
- **Build rule:** Return normalized jurisdiction DTO, confidence/evidence source, validation errors, and no public exact-location leakage.

### SH-121 — `applyAiSuggestion`

- **Plain English:** Convert an administrator-approved AI classification proposal into accepted taxonomy truth.
- **Owner:** Workflow between AI Taxonomy and Taxonomy & Classification
- **Classification:** Cluster-local public interface
- **Status:** Confirmed
- **Boundary:** AI Taxonomy owns suggestion/model provenance; Taxonomy owns normalization, hierarchy, duplicate prevention, and final mutation.
- **Build rule:** Require suggestion ID/version, target, selected canonical term, reviewer, reason, idempotency, and audit event.

### SH-122 — `mergeCanonicalRecord`

- **Plain English:** Move references from a duplicate/retired controlled term to one canonical replacement transactionally.
- **Owner:** Taxonomy & Classification for taxonomy terms
- **Classification:** Module-internal reusable operation
- **Status:** Proposed ruling
- **Boundary:** The merge policy is taxonomy-specific and must not become a generic cross-domain merge service.
- **Build rule:** Use lock, compatibility validation, reference migration, affected counts, provenance/alias preservation, rollback plan, and idempotency.

### SH-123 — `validateOwnedTargetReference`

- **Plain English:** Validate that a cross-Module target exists and is eligible for the requested relationship through its owner’s interface.
- **Owner:** Target owner
- **Classification:** Shared contract; separate implementations
- **Status:** Confirmed
- **Boundary:** Referencing another Module’s schema does not grant direct lifecycle or repository access.
- **Build rule:** Use typed owner query, target version/status, allowed relationship context, and not-found/forbidden separation.

### SH-124 — `generateUniqueSlug`

- **Plain English:** Generate a canonical, reserved-word-safe, collision-resistant public slug.
- **Owner:** Public entity owner using shared text primitive
- **Classification:** Cross-cutting primitive; policy local
- **Status:** Proposed ruling
- **Boundary:** Organization, Offering, and other public entities retain rename, redirect, reservation, and URL rules.
- **Build rule:** Normalize, validate reserved words, transactionally claim uniqueness, retry suffix strategy, and preserve redirect/history where required.

### SH-125 — `recordDomainAccessEvent`

- **Plain English:** Persist domain-specific access or delivery proof in addition to any generic AccessAuditLog.
- **Owner:** Domain owner
- **Classification:** Shared append-only mechanism; separate truth
- **Status:** Confirmed
- **Boundary:** ResumeAccessLog, MediaAccessEvent, DigitalDownloadEvent, video access, and Agreement access remain distinct.
- **Build rule:** Define domain action/reason, context relationships, expiry/usage/provider details, immutable append, and optional generic audit request.

### SH-126 — `getCustomerAggregateView`

- **Plain English:** Assemble a customer-facing commerce/history dashboard without copying source lifecycles into CustomerProfile.
- **Owner:** Application read-model layer; owner unresolved
- **Classification:** Read-model composition
- **Status:** Unresolved
- **Boundary:** Gig, Order, Booking, Review, Dispute, download, and video truth stays with source Modules.
- **Build rule:** Use federated queries or derived projection with source links, authorization, freshness indicators, and rebuild strategy.

## Alias and Naming Rules

Canonical APIs use the `SH-###` ID and canonical operation name above. Historical candidate names, shorthand, and narrower variants should resolve back to the canonical entry rather than becoming independent services.

Naming rules inherited from the synthesis:

- Use lowerCamelCase, verb-first names that describe the result rather than implementation technology.
- Use `resolve` for authoritative lookups.
- Use `evaluate` for policy decisions.
- Use `request` for commands sent to another owner.
- Use `append` / `record` for evidence.
- Use `execute` for owner-local effects.
- Provider/framework names belong in adapters, not generic business APIs.

## Shared Mechanism / Separate Truth Matrix

| Mechanism family | Shared owner / mechanism | Separate truths that must remain | Mandatory rule |
|---|---|---|---|
| Append-only records | AuditEvent / AccessAuditLog | OrderEvent, AgreementEvent, BookingEvent, JobInterviewEvent, UserSecurityEvent, PointLedgerEntry, ProfessionalBalanceLedgerEntry, TrackUsageEvent, ResumeAccessLog, MediaAccessEvent, DigitalDownloadEvent | Share insert-only, hashing, timestamps, and repository mechanics; never merge the records or status vocabularies. |
| Provider-event deduplication | Shared atomic claim pattern | ProcessedStripeEvent, ProcessedCalendarEvent, ProcessedVideoProviderEvent, subscription, verification, notification, and other adapter ledgers | Share the helper and envelope. Keep one provider/domain-specific record owner per integration boundary. |
| Temporary access | Shared issue/validate/expire/revoke mechanics | SensitiveActionSession, MediaAccessGrant, AgreementAccessGrant, DigitalDownloadGrant, CourseVideoPlaybackGrant, LocationReveal | Do not create a universal grant table. Each record proves a different business entitlement. |
| Readiness and gate decisions | DecisionResult response contract | Professional, verification, financial, healthcare, job-compliance, taxonomy, authority, hold, and public-readiness policy | Reuse response shape only. Every policy owner retains facts, rules, evidence, and reason codes. |
| Snapshots | Versioned immutable snapshot mechanism | Order pricing, agreement document, provider requirements, Job compliance input, AI run configuration, moderation evidence, consent reference | The consuming/decision Module owns historical meaning and retention. |
| Projections | Shared replay/checkpoint/rebuild mechanics | Typesense documents, CandidateSearchProjection, leaderboards, rating aggregates, point balances, TrackUsageCounter, customer dashboard | Each projection owner defines source records, inclusion, visibility, ranking, and staleness. |
| Privacy execution | Privacy-defined request/result protocol | Every Module’s local erase/anonymize/export/retain executor | Privacy owns orchestration; source owners alone mutate their records and provider resources. |
| Moderation enforcement | Typed dispatch/acknowledgment protocol | Media freeze, Search de-index, download revoke, video delete, Message restriction, hold creation | Moderation owns the decision; target owners own execution state and source truth. |
| Hashing | Shared cryptographic primitive | Media checksum, Agreement hash, consent text hash, audit chain, AI input hash, identifier HMAC | Never infer legal or domain meaning from the shared algorithm alone. |
| Authorization and entitlement | Shared invocation patterns | Role/Authority decision, Track entitlement, context owner access, healthcare sensitivity, Media readiness | Passing one gate never substitutes for the others. |

## Common Contract Requirements

### Command envelope

- `operationId` or `idempotencyKey`.
- `requestId`, `correlationId`, and `causationId` where event-derived.
- Actor context or explicit system actor.
- Requesting Module.
- Typed target and target ID.
- Expected source/aggregate version for concurrency-sensitive commands.
- Purpose/action key and privacy classification.
- Minimized typed payload.
- `issuedAt` and optional deadline/expiry/effective time.

### Decision envelope

- Decision such as `allowed`, `denied`, `warning`, `review_required`, `step_up_required`, or `unavailable`.
- Stable owner-specific reason codes.
- Human-safe explanation.
- Evidence references.
- `evaluatedAt`, policy/rule version, and source version.
- Blocking versus warning distinction.
- Expiry/recheck time where applicable.
- Retryability and remediation/next action.
- No raw provider payloads, secrets, private documents, PHI, or unnecessary personal data.

### Provider result envelope

- Provider and adapter version.
- Provider request/event reference.
- Normalized operation and result.
- Canonical status/result and retryability.
- Safe error category.
- Mapping version.
- Timestamp/correlation reference.
- Raw-payload hash only where justified.
- Unknown provider values must become explicit unsupported/review states rather than silent mappings.

### Privacy target result

- Privacy request/job/target references.
- Owner Module.
- Requested disposition.
- Idempotency key.
- Result such as erased, anonymized, retained, restricted, exported, detached, revoked, skipped, retryable failure, or terminal failure.
- Evidence and retention-exemption references.
- Provider deletion result where applicable.
- Safe counts and completion metadata.

### Event envelope

- `eventId`, event type, schema version.
- Source Module.
- Aggregate type, ID, and version.
- `occurredAt`.
- Correlation and causation IDs.
- Actor/system context.
- Privacy classification.
- Minimized payload.
- Source owners publish through a transactional outbox; consumers protect side effects through an inbox/idempotency mechanism.

## Cross-Cutting Build Rules

- **Authentication and authority:** resolve identity once and pass typed actor/resource/fact DTOs. Keep RLS semantics aligned with server authorization.
- **Entitlements and usage:** Track owns entitlement lookup and metered usage truth. Historical business records snapshot decisions rather than rereading current plan state.
- **Consent:** one version catalog, acceptance command, and proof query; contextual workflows may reference ConsentLog but do not replace it.
- **Compliance holds/readiness:** use one ComplianceHold API and shared decision shape; every readiness owner keeps its own reason codes and policy.
- **Audit/access proof:** keep generic audit and sensitive-access proof separate from domain lifecycle ledgers.
- **Observability:** use one request-context/logger/metrics/exception/queue/failure/health stack; operational evidence never becomes business truth.
- **Notification:** source Modules provide event intent and safe variables; Notification owns templates, routing, persistence, provider delivery, callbacks, and outward redaction.
- **Idempotency/events:** use shared command idempotency plus transactional outbox/inbox patterns; target effectively-once domain effects rather than assuming exactly-once transport.
- **Queues/workflows:** use one durable worker framework; workflow owners may keep Module-specific run/step records and compensation policy.
- **Concurrency:** prefer database-enforced constraints, compare-and-set, row/advisory locks, exclusion constraints, or serializable transactions; conflict semantics remain owner-defined.
- **Provider adapters:** share adapter/result/webhook/reconciliation patterns while keeping credentials, accepted events, status mappings, processed-event records, and lifecycle effects with the provider-owning Module.
- **Cryptography:** domain Modules use approved hashing/HMAC/token/encryption primitives and supply purpose/canonical bytes; they do not implement cryptographic algorithms.
- **Media/storage:** Media owns file validation, scanning, processing, object storage, MediaAccessGrant, and signed URLs; context Modules own attachment meaning and business access.
- **Search:** Search owns refresh commands, SearchUpsertEvent, provider adapter, workers, reconciliation, query APIs, and debug tooling; source Modules expose safe source projections and readiness facts.
- **Privacy:** Privacy owns request orchestration; every data owner registers enumeration/execution/export behavior and mutates only its own records/provider resources.
- **Moderation:** Moderation owns intake/decision/orchestration; target Modules resolve and execute enforcement against their own truth.
- **Snapshots/projections:** reuse mechanics, never meaning. Historical snapshot meaning and projection inclusion/ranking remain owner-specific.

## Prohibited Duplicate Implementations

- Feature-local authentication or current-user helpers that bypass `resolveAuthenticatedActor`.
- Feature-local RBAC, `isAdmin`, recruiter, participant, owner, or permission middleware outside Role / Authority.
- Local premium, plan, boost, fee-waiver, commission, priority, or quota booleans outside Track Subscription & Entitlement.
- Local `ConsentLog` substitutes or feature-specific generic consent repositories.
- Local blocked/suspended flags used as substitutes for `ComplianceHold`.
- One universal readiness engine that owns professional, healthcare, verification, financial, job, or hold policy.
- Generic cross-domain repositories that directly query arbitrary Module tables by target type and ID.
- Feature-specific generic `AuditEvent` or `AccessAuditLog` tables and writers.
- Using `AuditEvent` as `OrderEvent`, `BookingEvent`, security history, point ledger, or provider-event truth.
- Using `IntegrationFailure` or `QueueJob` as business workflow state.
- Separate queue, retry, dead-letter, correlation, or worker frameworks per Module.
- In-memory locks for distributed financial, booking, grant, application, drawing, or lifecycle invariants.
- Separate Typesense clients, queues, indexers, or de-index logic inside source Modules.
- Indexing raw resumes, private application documents, PHI, exact locations, or unapproved source fields.
- Separate upload validation, MIME sniffing, malware scanning, EXIF/PDF scrubbing, object-key generation, or signed-URL services.
- Original filenames used as storage keys or permanent public URLs for private media.
- A universal temporary-access-grant table replacing domain grant records.
- Reusing `ProcessedStripeEvent`, `ProcessedCalendarEvent`, or `ProcessedVideoProviderEvent` outside its owner.
- One global provider-status mapper containing payment, calendar, video, verification, notification, and subscription semantics.
- Privacy workflows implemented independently in feature Modules or a Privacy service directly mutating all feature tables.
- Local retention flags without `DataRetentionExemption` and owner-supplied retention facts.
- Moderation directly mutating Search, Media, Messaging, Digital Goods, Video, or marketplace source records.
- Notification producers calling email, SMS, push, FCM, OneSignal, SES, or Twilio providers directly.
- Custom cryptographic code in domain Modules instead of approved hashing, HMAC, token, and encryption primitives.
- Raw provider payloads, secrets, PHI, tax data, identity documents, resumes, contract text, or private Message bodies in audit/telemetry/notification payloads.
- Order, Payment, Booking, Media, Search, Audit, or provider records used as substitutes for another Module’s source truth.

## Conflict and Unresolved-Decision Register

These findings remain open in the source architecture. A consuming plan may cite the relevant `SH-###` entry, but must not settle the issue silently.

| Decision | Current finding |
|---|---|
| Shared AI provider infrastructure owner | AI Taxonomy can initially own the Bedrock adapter, but a broader AI capability owner should be ruled only when another production AI Module requires the same runtime. |
| Jurisdiction normalization owner | Job Compliance, Payment/Tax, and Location Safety need normalized jurisdiction context, but none is confirmed as the neutral owner. |
| Hash-chain platform owner | Audit and Agreement workflows need similar cryptographic machinery; ownership and anchoring strategy are not yet assigned. |
| Generic manual-review infrastructure | Admin Review, Moderation, Job Compliance, Healthcare, and Verification need claim/assignment mechanics, but shared review-queue schemas are not confirmed. |
| Evidence snapshot ownership | Moderation and high-impact review workflows need immutable decision evidence, but a generic evidence record is not established. |
| Content fingerprinting and piracy provider | Exact checksum exists in Media; perceptual fingerprint provider, thresholds, and ownership remain unselected. |
| Shared fraud-risk capability | Sweepstakes and Gamification identify fraud needs, but no canonical risk Module or schema is assigned. |
| Organization commercial entitlement model | Track Subscription covers User actor tracks; an Organization ATS plan/entitlement owner is not confirmed. |
| Customer aggregate read-model owner | A customer dashboard needs cross-Module composition, but no canonical read-model owner is established. |
| Document rendering capability owner | Transaction / Order needs agreement PDFs; whether rendering becomes a lower platform capability remains a proposed ruling. |
| Temporary feature-grant owner | Profile boosts and similar deterministic rewards should not become local flags, but final ownership between Track Entitlement and affected feature owners needs ruling. |
| Moderation enforcement execution record | ModerationAction lacks explicit downstream step/acknowledgment schema; correlateEnforcementResult is a proposed addition. |
| Provider notification callback ledger | Notification likely needs a processed-provider-event record, but no authoritative schema is supplied. |
| Tax-location evidence authority | Address normalization can be shared, but authoritative evidence selection and conflict rules must remain tax-owned and are not fully specified. |

## Compact ID Index

| ID | Canonical operation | Owner | Classification | Status |
|---|---|---|---|---|
| SH-001 | `resolveAuthenticatedActor` | Identity & Access | Platform capability | Confirmed |
| SH-002 | `authorizeResourceAction` | Role / Authority | Cross-cutting capability | Confirmed |
| SH-003 | `queryOwnerFacts` | Each source Module | Shared contract; separate implementations | Proposed ruling |
| SH-004 | `resolveCustomerActor` | Customer / Buyer Profile | Module public interface | Confirmed |
| SH-005 | `resolveEntitlement` | Track Subscription & Entitlement | Platform commercial-policy capability | Confirmed |
| SH-006 | `consumeMeteredEntitlement` | Track Subscription & Entitlement | Cross-cutting capability | Confirmed |
| SH-007 | `recordConsentProof` | Consent & Disclosure | Platform consent capability | Confirmed |
| SH-008 | `queryConsentProof` | Consent & Disclosure | Platform consent capability | Confirmed |
| SH-009 | `resolveActiveConsentVersion` | Consent & Disclosure | Cross-cutting capability | Confirmed |
| SH-010 | `presentStandaloneConsent` | Consent & Disclosure | Cross-cutting UI/application capability | Confirmed |
| SH-011 | `evaluateComplianceHold` | Admin Review / Compliance Hold | Cross-cutting capability | Confirmed |
| SH-012 | `requestComplianceHold` | Admin Review / Compliance Hold | Cross-cutting capability | Confirmed |
| SH-013 | `releaseComplianceHold` | Admin Review / Compliance Hold | Cross-cutting capability | Confirmed |
| SH-014 | `requireStepUpForSensitiveAction` | Identity & Access | Platform security capability | Confirmed |
| SH-015 | `returnDecisionResult` | Shared contract; policy owner varies | Shared contract; separate policy | Proposed ruling |
| SH-016 | `evaluateProfessionalReadiness` | Professional Eligibility | Module public interface | Confirmed |
| SH-017 | `resolveVerificationRequirements` | Trust Verification / Screening | Module public interface | Confirmed |
| SH-018 | `evaluateVerificationReadiness` | Trust Verification / Screening | Module public interface | Confirmed |
| SH-019 | `evaluateFinancialReadiness` | Payment / Payout / Tax | Module public interface | Confirmed |
| SH-020 | `evaluateHealthcareReadiness` | Healthcare / Regulated Services | Module public interface | Confirmed |
| SH-021 | `evaluateJobCompliance` | Job Compliance | Module public interface | Confirmed |
| SH-022 | `resolveTaxonomyRequirements` | Taxonomy & Classification | Module public interface | Confirmed |
| SH-023 | `validateTaxonomyAssignment` | Taxonomy & Classification | Module public interface | Confirmed |
| SH-024 | `evaluatePublicReadiness` | Source/compliance owner; Search composes | Shared contract; separate policy | Confirmed |
| SH-025 | `authorizeOrderEntitlement` | Transaction / Order | Module public interface | Confirmed |
| SH-026 | `authorizeContextualResourceAccess` | Relevant context owner | Shared contract; separate implementations | Confirmed |
| SH-027 | `resolveLocationReveal` | Location Safety | Module public interface | Confirmed |
| SH-028 | `applyFuzzyPublicLocation` | Location Safety | Module public interface | Confirmed |
| SH-029 | `appendAuditEvent` | Audit / Event Ledger | Platform audit capability | Confirmed |
| SH-030 | `recordSensitiveAccess` | Audit / Event Ledger | Cross-cutting capability | Confirmed |
| SH-031 | `appendDomainLifecycleEvent` | Shared persistence mechanism; each domain owns truth | Shared mechanism; separate truth | Confirmed |
| SH-032 | `createRequestContext` | Observability / platform infrastructure | Platform primitive | Confirmed |
| SH-033 | `writeStructuredLog` | Observability / Ops | Platform capability | Confirmed |
| SH-034 | `sanitizeTelemetryMetadata` | Observability / Ops and Audit payload policy | Cross-cutting capability | Confirmed |
| SH-035 | `captureException` | Observability / Ops | Provider adapter | Confirmed |
| SH-036 | `emitMetric` | Observability / Ops | Platform capability | Confirmed |
| SH-037 | `recordIntegrationFailure` | Observability / Ops | Cross-cutting capability | Confirmed |
| SH-038 | `recordQueueTelemetry` | Observability / Ops / queue infrastructure | Cross-cutting capability | Confirmed |
| SH-039 | `checkServiceHealth` | Observability / Ops coordinates; owner supplies check | Cross-cutting capability | Confirmed |
| SH-040 | `correlateOpsIncident` | Observability / Ops | Module-internal public ops interface | Confirmed |
| SH-041 | `requestNotification` | Notification | Platform notification capability | Confirmed |
| SH-042 | `renderNotificationTemplate` | Notification | Cross-cutting capability | Confirmed |
| SH-043 | `resolveNotificationRecipients` | Source context owner plus Notification | Shared contract; separate policy | Confirmed |
| SH-044 | `executeIdempotentCommand` | Platform application infrastructure | Platform primitive | Confirmed |
| SH-045 | `deduplicateDomainEvent` | Platform event infrastructure; consumer owns inbox | Platform primitive | Confirmed |
| SH-046 | `publishDomainEvent` | Platform event/outbox infrastructure | Platform primitive | Confirmed |
| SH-047 | `enqueueReliableJob` | Shared queue infrastructure | Platform primitive | Confirmed |
| SH-048 | `executeRetryWithBackoff` | Shared queue/platform infrastructure | Platform primitive | Confirmed |
| SH-049 | `orchestrateWorkflowSteps` | Workflow-owning Module using shared runner | Shared mechanism; separate workflow truth | Confirmed |
| SH-050 | `reconcileWorkflowStatus` | Workflow owner using shared helper | Shared mechanism; separate policy | Confirmed |
| SH-051 | `acquireAggregateLock` | Shared persistence infrastructure | Platform primitive | Confirmed |
| SH-052 | `withOptimisticConcurrency` | Shared persistence infrastructure | Platform primitive | Confirmed |
| SH-053 | `transitionLifecycleState` | Shared mechanism; lifecycle owner supplies policy | Shared mechanism; separate truth | Confirmed |
| SH-054 | `claimWorkItem` | Shared work-queue/locking capability | Cross-cutting capability | Proposed ruling |
| SH-055 | `runDeadlineExpiration` | Shared scheduler/queue infrastructure | Cross-cutting capability | Confirmed |
| SH-056 | `executeAtomicReservation` | Shared database primitive | Cross-cutting capability | Confirmed |
| SH-057 | `consumeCounterAtomically` | Shared database primitive | Platform primitive | Confirmed |
| SH-058 | `acquireIntervalLock` | Booking & Calendar policy over shared Postgres mechanism | Cluster-local capability | Confirmed |
| SH-059 | `verifyProviderWebhookSignature` | Shared integration-security shell; provider adapter supplies algorithm | Provider-adapter contract | Confirmed |
| SH-060 | `deduplicateProviderEvent` | Provider-owning Module using shared primitive | Shared mechanism; separate truth | Confirmed |
| SH-061 | `translateProviderStatus` | Provider-owning adapter | Provider-adapter contract | Confirmed |
| SH-062 | `reconcileProviderState` | Each provider-owning Module using shared worker framework | Shared mechanism; separate policy | Confirmed |
| SH-063 | `captureProviderSnapshot` | Provider-owning Module | Shared snapshot mechanism; separate truth | Confirmed |
| SH-064 | `authorizeExternalProviderConnection` | Provider-owning Module | Provider-adapter capability | Confirmed |
| SH-065 | `invokeFoundationModel` | AI Taxonomy initially; broader AI infrastructure ownership unresolved | Provider-adapter capability | Proposed ruling |
| SH-066 | `validateStructuredProviderOutput` | Shared validation primitive; consuming Module owns schema | Cross-cutting capability | Confirmed |
| SH-067 | `invokeCalendarProvider` | Booking & Calendar | Module provider interface | Confirmed |
| SH-068 | `invokeVideoProvider` | Video Infrastructure | Module provider interface | Confirmed |
| SH-069 | `geocodeAddress` | Location Safety adapter ownership proposed | Provider-adapter capability | Proposed ruling |
| SH-070 | `deleteProviderResource` | Provider-owning Module | Provider-adapter contract | Confirmed |
| SH-071 | `publishRealtimeChange` | Platform realtime adapter; Messaging is primary consumer | Infrastructure adapter | Proposed ruling |
| SH-072 | `hashCanonicalPayload` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-073 | `hashChainRecords` | Shared cryptographic capability; ownership unresolved | Cross-cutting primitive | Proposed ruling |
| SH-074 | `generateSecureToken` | Shared security capability | Platform primitive | Confirmed |
| SH-075 | `encryptSensitiveValue` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-076 | `normalizeAndHashIdentifier` | Shared security/cryptography capability | Platform primitive | Confirmed |
| SH-077 | `buildCanonicalTextSnapshot` | Shared text canonicalization mechanism | Cross-cutting primitive | Confirmed |
| SH-078 | `minimizeAndRedactProviderInput` | Source-data owner supplies policy; shared serializer enforces | Cross-cutting capability | Confirmed |
| SH-079 | `normalizeControlledTerm` | Taxonomy & Classification policy over shared text primitive | Cross-cutting capability | Confirmed |
| SH-080 | `manageVersionedRules` | Each policy Module using shared versioning mechanism | Shared mechanism; separate policy | Confirmed |
| SH-081 | `runPatternScanner` | Shared scanner mechanism; policy owner unresolved | Cross-cutting capability | Proposed ruling |
| SH-082 | `validateUploadedFile` | Media / File Access | Cross-cutting media capability | Confirmed |
| SH-083 | `scanFileForMalware` | Media / File Access | Cross-cutting media capability | Confirmed |
| SH-084 | `scrubFileMetadata` | Media / File Access | Cross-cutting media capability | Confirmed |
| SH-085 | `generatePrivateObjectKey` | Media / File Access / storage primitive | Platform storage primitive | Confirmed |
| SH-086 | `calculateChecksum` | Shared hash primitive consumed by Media | Platform primitive | Confirmed |
| SH-087 | `issueSignedMediaUrl` | Media / File Access | Cross-cutting media capability | Confirmed |
| SH-088 | `manageTemporaryAccessGrant` | Shared grant mechanism; each domain owns its record | Shared mechanism; separate truth | Confirmed |
| SH-089 | `revokeTemporaryAccessGrant` | Each grant owner using shared primitive | Cross-cutting command pattern | Confirmed |
| SH-090 | `attachValidatedMedia` | Contextual domain Module; Media owns asset truth | Shared contract; separate contextual truth | Confirmed |
| SH-091 | `requestSearchProjectionRefresh` | Search / Public Visibility | Module public interface | Confirmed |
| SH-092 | `writeSearchProjection` | Search / Public Visibility | Provider adapter | Confirmed |
| SH-093 | `reconcileSearchProjection` | Search / Public Visibility | Module-internal worker using shared queue | Confirmed |
| SH-094 | `buildSourceProjection` | Each source Module | Shared pattern; separate source projection | Confirmed |
| SH-095 | `executePrivacyInstruction` | Privacy orchestrates; each data owner executes | Cross-cutting protocol | Confirmed |
| SH-096 | `enumerateSubjectData` | Each data-owning Module through Privacy-defined interface | Cross-cutting protocol | Confirmed |
| SH-097 | `evaluateRetentionRequirement` | Data owner supplies facts; Privacy records exemption | Cross-cutting protocol | Confirmed |
| SH-098 | `anonymizePersonalFields` | Shared primitive; record owner supplies mapping | Cross-cutting capability | Confirmed |
| SH-099 | `orchestratePrivacyFulfillment` | Privacy / Data Erasure | Module-internal orchestration with public interfaces | Confirmed |
| SH-100 | `createPrivacyExportArtifact` | Privacy owns bundle; Media/storage owns object mechanics | Cluster-local capability | Confirmed |
| SH-101 | `submitModerationReport` | Content Moderation & Legal Notice | Module public interface | Confirmed |
| SH-102 | `resolveModerationTarget` | Target registry contract; each owner supplies resolver | Cross-cutting capability | Proposed ruling |
| SH-103 | `executeModerationDecision` | Moderation owns decision; each target owner executes | Cross-cutting protocol | Confirmed |
| SH-104 | `preserveEvidenceSnapshot` | Decision/evidence owner using Media and hash primitives | Shared evidence mechanism; ownership case-specific | Proposed ruling |
| SH-105 | `correlateEnforcementResult` | Content Moderation & Legal Notice | Cluster-local orchestration | Proposed ruling |
| SH-106 | `computeContentFingerprint` | Media / File Access or specialized adapter; ownership unresolved | Provider/cross-cutting capability | Unresolved |
| SH-107 | `createChargeableOrder` | Transaction / Order | Cluster-local public interface | Confirmed |
| SH-108 | `requestOrderRefund` | Transaction / Order coordinates; Payment executes provider rail | Cluster-local public interface | Confirmed |
| SH-109 | `snapshotExternalDecision` | Consuming domain owner | Shared snapshot pattern; separate truth | Confirmed |
| SH-110 | `createDomainSnapshot` | Downstream lifecycle owner | Shared snapshot pattern; separate truth | Confirmed |
| SH-111 | `renderDocument` | Document-owning Module; Transaction / Order initially | Cross-cutting document mechanism | Proposed ruling |
| SH-112 | `verifyAgreementDocumentHash` | Transaction / Order | Module public/internal interface | Confirmed |
| SH-113 | `ensureContextThread` | Messaging | Module public interface | Confirmed |
| SH-114 | `provisionOneToOneProfile` | Each profile Module using shared provisioning mechanism | Shared mechanism; separate truth | Confirmed |
| SH-115 | `buildAggregateProjection` | Projection owner | Shared projection mechanism; separate policy | Confirmed |
| SH-116 | `secureRandomSelection` | Sweepstakes / Prize | Module-internal capability over shared CSPRNG | Confirmed |
| SH-117 | `aggregateYearlyReportableValue` | Each value-owning Module; tax consumes | Shared aggregation mechanism; separate truth | Confirmed |
| SH-118 | `reportTaxableValue` | Payment / Payout / Tax | Cross-cutting public interface | Confirmed |
| SH-119 | `applyTemporaryFeatureGrant` | Track Subscription & Entitlement or affected feature owner | Cross-cutting public interface; ownership partly unresolved | Proposed ruling |
| SH-120 | `normalizeJurisdictionContext` | Shared commerce/location capability ownership unresolved | Cross-cutting capability | Unresolved |
| SH-121 | `applyAiSuggestion` | Workflow between AI Taxonomy and Taxonomy & Classification | Cluster-local public interface | Confirmed |
| SH-122 | `mergeCanonicalRecord` | Taxonomy & Classification for taxonomy terms | Module-internal reusable operation | Proposed ruling |
| SH-123 | `validateOwnedTargetReference` | Target owner | Shared contract; separate implementations | Confirmed |
| SH-124 | `generateUniqueSlug` | Public entity owner using shared text primitive | Cross-cutting primitive; policy local | Proposed ruling |
| SH-125 | `recordDomainAccessEvent` | Domain owner | Shared append-only mechanism; separate truth | Confirmed |
| SH-126 | `getCustomerAggregateView` | Application read-model layer; owner unresolved | Read-model composition | Unresolved |

## Registry Maintenance Rule

When architecture work changes a shared operation:

1. Update this registry first or in the same architecture change.
2. Preserve the existing permanent ID.
3. Record renamed terms as aliases.
4. Update affected Cluster and Module plans by ID rather than copying the revised definition.
5. If a new operation is approved, append the next unused ID beginning with `SH-127`.
6. If an operation is deprecated or superseded, retain its row and mark the status instead of deleting/reusing the ID.

This file is the canonical reference target for `Shared Operations Used` sections throughout Workin Ants context.
