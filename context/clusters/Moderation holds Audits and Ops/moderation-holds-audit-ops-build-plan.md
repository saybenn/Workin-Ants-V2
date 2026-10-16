# Moderation, Holds, Audit & Ops Build Plan

## Core Principle

Build CL-09 as a sequence of vertical, testable governance slices. Every numbered feature must produce a concrete behavior that a user, admin, worker, developer, or consuming Module can observe through a public contract, persisted source record, protected admin surface, operational signal, or automated test.

The preferred slice is:

```text
observable behavior
  -> owning application/domain service
  -> authoritative owner state
  -> stable public contract
  -> authorization/compliance gates
  -> audit/ops/notification effects
  -> async/provider integration when required
  -> tests
  -> exit gate
```

CL-09 must not become a large infrastructure-first project. Shared primitives are introduced only when a numbered feature needs them. However, unresolved schema/contract decisions that materially affect source truth must be settled **before** a coding agent implements the affected feature.

A capability feature does not need artificial UI. If a user-facing screen is not appropriate, the slice must still produce a testable command/query, worker, protected administrative view, health surface, or durable result.

---

## Build Rules

1. Follow the CL-09 `architecture.md`, root architecture, root code standards, target Module architecture, and target Module implementation plan.
2. Do not expand CL-09 scope merely because the Cluster sees cross-platform data.
3. Do not redesign Deep Module ownership in the build plan.
4. Canonical Shared Operations must be reused; do not create local substitutes.
5. Every mutation validates input, actor context, authorization, target references, owner invariants, and idempotency where retries are possible.
6. Every cross-Module write uses a public command, event handler, or approved protocol; no direct foreign Prisma mutation.
7. Provider operations remain behind the provider-owning Module's adapter.
8. Provider payloads never become CL-09 domain types.
9. Audit evidence, domain event truth, provider-event truth, and Observability truth remain separate.
10. `ComplianceHold` remains the reusable stop sign; no feature-local competing block fields.
11. Search remains projection; Moderation requests Search work instead of writing Search state.
12. File/storage mechanics remain Media-owned.
13. Privacy request orchestration remains Privacy-owned; CL-09 data owners only enumerate and execute their own targets.
14. Every asynchronous operation is idempotent, correlated, retry-bounded, and observable.
15. Every feature ends with tests and a concrete exit gate.
16. Do not silently implement an item listed as Unresolved or a Proposed Ruling that has not been accepted.
17. Schema corrections are documented as architecture alignment, not smuggled into unrelated features.
18. Legal timing, retention duration, repeat-infringer thresholds, and content-fingerprint thresholds require approved policy; general internet knowledge is not sufficient.
19. The implementation plan may stub an external provider or neighboring Module contract when that dependency should not block the first vertical slice, but the stub must conform to the published owner contract.
20. A feature completion report must record assumptions, risks, and any deferred unresolved item.

---

## Dependencies and Preconditions

### Root/platform prerequisites

- Next.js/TypeScript/Prisma/Supabase foundation is available according to root context.
- SH-001 `resolveAuthenticatedActor` is available from Identity & Access or is implemented before the first protected CL-09 mutation.
- SH-002 `authorizeResourceAction` is available from Role / Authority or a contract-compatible dependency stub exists for initial tests.
- Shared transaction/idempotency/outbox/queue/locking primitives are available as needed by each feature; do not create CL-09-only substitutes.
- Request/correlation context and safe structured logging are established no later than Feature 01/02.

### Shared-operation prerequisites

The following canonical operations are expected during the plan:

- SH-001 `resolveAuthenticatedActor`
- SH-002 `authorizeResourceAction`
- SH-014 `requireStepUpForSensitiveAction` where security policy requires it
- SH-044 `executeIdempotentCommand`
- SH-046 `publishDomainEvent`
- SH-045 `deduplicateDomainEvent`
- SH-047 `enqueueReliableJob`
- SH-048 `executeRetryWithBackoff`
- SH-051 `acquireAggregateLock`
- SH-052 `withOptimisticConcurrency`
- SH-053 `transitionLifecycleState`
- SH-032 `createRequestContext`
- SH-034 `sanitizeTelemetryMetadata`
- SH-041 `requestNotification`
- SH-091 `requestSearchProjectionRefresh`
- SH-123 `validateOwnedTargetReference`
- Privacy owner/executor contracts

The CL-09-owned canonical operations are implemented in the numbered features below rather than as a separate “shared utilities” phase.

### Upstream / neighboring Cluster prerequisites

The initial CL-09 source-record slices should not wait for every neighboring Cluster to be complete. Use typed contract fakes for tests where needed. Production integration requires the following owner contracts before the Cross-Cluster Integration Phase exits:

- Identity & Access actor/step-up interfaces;
- Role / Authority permission interface;
- Search projection-refresh interface;
- Media evidence/freeze/public-URL/signed-access interfaces;
- Notification request interface;
- Privacy enumeration/retention/execution protocol;
- target-owner resolver/execution handlers for supported moderation targets;
- source compliance fact/readiness interfaces for hold request/release integration.

### Existing migrations / source records

Current Prisma evidence already contains:

- `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction` and moderation enums;
- `ComplianceHold`, `ComplianceHoldReason`, `ComplianceHoldStatus`;
- `AuditEvent`, `AccessAuditLog`, `AccessAuditAction`.

Current Prisma does **not** contain the four Observability-owned records claimed by registry/glossary.

### Decisions that must be settled before affected features

| Decision | Required before |
| --- | --- |
| Verify `ModerationTargetType` migration compatibility (U-01 snapshot corrected by CL-09-R017) | Before any migration touching the current `moderation_target_type` enum; CL-09-R013 provenance remains investigation-only. |
| SH-029 `appendAuditEvent` request ID/outcome storage (`U-17`) | Feature 01 final command/schema contract. |
| Observability persistence/status ruling (`PR-CL09-05`, `U-19`, `U-20`) | Feature 02 persistence implementation. |
| ComplianceHold target/provenance/idempotency rules (`PR-CL09-04`, `U-10`, `U-12`, `U-14`) | Feature 04 general hold API. |
| Moderation evidence snapshot ruling (`PR-CL09-02`, `U-04`) | Feature 05 evidence-preserving decision path. |
| Enforcement correlation ruling (`PR-CL09-03`, `U-06`) | Feature 06 durable multi-owner enforcement. |
| Legal counter-notice/deadline policy (`U-25`) | Feature 07 automated deadlines; restoration can otherwise proceed using approved manual decision flow. |
| Privacy target vocabulary/retention rulings (`U-24`) | Feature 10 production retention/erasure behavior. |

### Provider prerequisites

- Sentry is the confirmed error-monitoring technology; it can be stubbed behind the Observability port in tests.
- Structured logging and metrics provider choices do not block contract/domain work.
- Queue runtime choice does not block defining queue payloads and worker contracts if the shared queue abstraction is already approved.
- R2/Typesense/payment/video/notification providers do not block CL-09 domain slices because their owner Modules can be represented with contract fakes until integration phases.

---

## Phase 1 — Evidence and Operational Spine

### 01 Audit Evidence and Request Correlation

Implement the generic audit and sensitive-access rail so later moderation, hold, privacy, and admin features can preserve proof without inventing local logging systems.

#### Objective

Make SH-029 `appendAuditEvent` and SH-030 `recordSensitiveAccess` usable as stable, protected Module interfaces with safe request correlation, insert-only storage, restricted queries, and payload minimization.

#### User-visible / Observable Result

- A consuming Module can append a generic audit event and receive its ID/timestamp.
- A sensitive data owner can record allowed, denied, blocked, redacted, viewed, downloaded, or credential-issued access evidence.
- An authorized admin/compliance caller can query audit/access history through protected interfaces.
- Tests prove normal app/admin code cannot update/delete sensitive access evidence.
- A correlation/request ID can connect a sensitive-access log to the request that caused it.

#### Owning Module(s)

- Primary truth: Audit / Event Ledger.
- Narrow shared dependency: Observability/platform request context.
- Identity and Role / Authority remain external owners.

#### Dependencies

- SH-001 `resolveAuthenticatedActor`.
- SH-002 `authorizeResourceAction` for restricted queries.
- SH-032 `createRequestContext` and SH-034 `sanitizeTelemetryMetadata`.
- SH-044 `executeIdempotentCommand` only if the chosen audit command contract requires caller idempotency; audit insert semantics must not accidentally suppress distinct legitimate events.
- Architecture decision `U-17` must be resolved: explicit `AuditEvent.requestId`/`outcome` fields versus an approved normalized metadata representation.

**CL-09-R010 — Confirmed Audit contract semantics.** SH-029 `appendAuditEvent` and SH-030 `recordSensitiveAccess` are the authoritative integration boundaries. Persistence must support actor attribution (including supported non-user/system actions), action, target, outcome/access outcome, request/correlation identity, and safe validated metadata. Generic access evidence must represent a normalized access outcome; Healthcare may supply its own decision as source evidence but its policy vocabulary is not universal Audit policy. `AuditEventType` and `AuditEventActor` are absent current-schema claims, not available structures. Exact fields/enums, non-user actor storage, migration design, and hash-chain architecture remain unresolved; SH-073 `hashChainRecords` remains Proposed ruling.

Feature 01 is gated on an approved representation satisfying those confirmed semantics, including normalized generic access outcomes. Existing schema fields alone do not satisfy that exit gate.

#### Shared Operations Used

| Operation | Owner | Use in this feature | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Identity & Access | Attach trusted actor/system context. | Which actor fields may be persisted. | Local current-user helper. |
| SH-002 `authorizeResourceAction` | Role / Authority | Gate audit viewer/export queries. | Audit evidence scopes and redaction. | Audit-specific authority engine. |
| SH-032 `createRequestContext` | Observability/platform | Create request/correlation IDs. | Safe propagation only. | Per-audit correlation helper. |
| SH-034 `sanitizeTelemetryMetadata` | Audit/Observability policy | Validate metadata before persistence. | Audit action-specific allowlists and size limits. | `redactAuditJson` clones. |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Core generic evidence command. | Action vocabulary/target validation. | Generic action log tables. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Core protected-access evidence command. | Sensitivity/action compatibility and safe metadata. | Finance/PHI/file generic audit tables. |
| SH-072 `hashCanonicalPayload` | Shared crypto | Optional support for later integrity work. | What payload is canonical. | Local SHA helper. |

#### Data / Schema

- Use existing `AuditEvent` and `AccessAuditLog` as source records.
- Use existing `AccessAuditAction` enum.
- Preserve `DataSensitivity` and `HealthcareAccessDecision` as consumed vocabularies, not Audit-owned policy.
- Resolve and migrate the canonical SH-029 `appendAuditEvent` request/outcome contract as required by `U-17`.
- Do **not** add `AuditEventType` or `AuditEventActor` merely because the Deep Module Registry claims them; their absence is `U-16` and requires an explicit ruling.
- Enforce insert-only DB permissions/policies for `AuditEvent` and `AccessAuditLog` for normal app/admin roles.
- Add/verify indexes required by public query filters and request correlation after schema decision.

#### Public Interfaces

- SH-029 `appendAuditEvent(command) -> AuditEventReceipt`
- SH-030 `recordSensitiveAccess(command) -> AccessAuditReceipt`
- `queryAuditEvents(filters, viewer) -> Page<AuditEventView>`
- `querySensitiveAccessHistory(filters, viewer) -> Page<AccessAuditView>`

The receipt must contain an evidence ID and creation timestamp. Query views must be redacted DTOs, not raw Prisma records.

#### Logic

- Validate actor/system source, target type/ID, action, sensitivity, request context, and safe metadata.
- For SH-030 `recordSensitiveAccess`, require caller-owned access outcome where action implies a decision.
- Reject prohibited keys/payload classes and over-sized metadata.
- Persist through insert-only repository methods; do not expose general update/delete methods.
- Keep generic audit action meaning separate from domain events.
- If hash fields are populated, label them as integrity metadata only; do not claim a complete hash chain until `PR-CL09-07` is accepted.

#### UI / Administrative Surface

No full admin UI is required yet. Provide protected query contracts and a minimal developer/admin proof route or test harness if root code standards permit. Full viewer arrives in Feature 08.

#### Authorization / Compliance

- Audit mutation callers require trusted internal application context; public clients do not write arbitrary audit events directly.
- Restricted queries require Role / Authority.
- Sensitive evidence queries use field-level redaction and may require step-up if security policy says so.
- App/admin roles cannot update/delete sensitive evidence.
- Metadata must not contain PHI, raw resume bodies, secrets, payment/card data, OTPs, raw biometrics, raw identity documents, or full contracts.

#### Events / Jobs / Integrations

- No domain event is required merely because an audit record was appended.
- Optional operational signal on audit write failure goes to Observability; failure must not be hidden by the logger itself.
- Integrity verification worker is deferred until hash-chain policy is approved.

#### Failure Behavior

- Invalid metadata/action/target: reject synchronously with typed validation error.
- Unauthorized query: deny without leaking whether a target exists where that would be sensitive.
- Audit persistence failure during a legally required workflow: fail closed or route to owner-defined recovery; do not claim success without proof.
- Duplicate caller retries: use an approved semantic identity only where duplication is harmful; distinct access attempts must remain distinct evidence.

#### Tests

- Unit: metadata sanitizer, action/sensitivity validation, safe DTO mapping.
- Integration: insert and query paths; DB update/delete denied for normal roles.
- Contract: command/query DTOs and redaction.
- Compliance: prohibited payload fixtures rejected.
- Concurrency/idempotency: retried command behavior documented and tested.
- Security: viewer permission and target-not-found/forbidden separation.

#### Out of Scope

- Domain event ledgers.
- Provider-event dedupe.
- Observability incident state.
- Hash-chain compliance claim.
- Audit evidence export bundle.
- Ghost-account cleanup actions.

#### Exit Gate

Feature 01 passes only when:

1. SH-029 `appendAuditEvent` and SH-030 `recordSensitiveAccess` have stable typed contracts;
2. an approved storage representation implements the CL-09-R010 contract, including U-17 correlation/outcome and normalized generic access outcome support, without treating absent actor/type schemas as current structures;
3. insert-only DB enforcement is proven by automated tests;
4. payload redaction/prohibited-field fixtures pass;
5. restricted query contracts return safe DTOs;
6. no CL-09 or test code writes domain lifecycle truth into Audit records;
7. typecheck, lint, unit, integration, and relevant RLS/DB-policy tests pass.

---

### 02 Operational Telemetry, Failure Visibility, and Health

Establish the Observability interfaces that all later workers and cross-Module enforcement flows will use to surface technical failures.

#### Objective

Provide one request/logging/error/metrics/failure/queue/health rail and, if `PR-CL09-05` is accepted, create the canonical Workin Ants operational records required by the registry/glossary.

#### User-visible / Observable Result

- Requests/jobs have correlation IDs visible in structured logs and failures.
- A module can record a normalized integration failure without creating its own failure table.
- Shared queue work emits attempt/retry/dead-letter telemetry.
- A protected health query shows component status.
- A captured exception appears through the configured Sentry adapter with sensitive fields stripped.
- If persistence is approved, an operator can query persisted failures/queue visibility through protected APIs.

#### Owning Module(s)

- Observability / Ops owns operational visibility.
- Shared queue/platform infrastructure owns execution primitives.
- Source business Modules remain owners of business failures and provider-dedupe state.

#### Dependencies

- Feature 01 for audit of sensitive ops access where required.
- Acceptance of `PR-CL09-05` or an explicit alternate persistence ruling.
- Resolution of `U-20` for any statuses/severities being persisted.
- Sentry adapter credentials/config in deployment; can be stubbed in development/tests.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-032 `createRequestContext` | Observability/platform | Request/job correlation. | Safe dimensions. | Module correlation helpers. |
| SH-033 `writeStructuredLog` | Observability / Ops | One machine-readable logger. | Log level/fields. | Per-module logger instances. |
| SH-034 `sanitizeTelemetryMetadata` | Observability + Audit policy | Strip prohibited data. | Operational allowlists/cardinality. | Ad hoc redactors. |
| SH-035 `captureException` | Observability / Ops | One Sentry adapter. | Sampling/grouping. | Direct Sentry init in features. |
| SH-036 `emitMetric` | Observability / Ops | One metrics interface. | Metric names/dimensions/thresholds. | Per-module metrics clients. |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Persist/emit normalized technical failure. | Failure normalization and safe diagnostic fields. | Local generic failure tables. |
| SH-038 `recordQueueTelemetry` | Observability/queue infra | Operational job visibility. | Queue telemetry vocabulary. | Domain job replacement. |
| SH-039 `checkServiceHealth` | Observability coordinates | Standard health checks. | Owner-defined health criteria. | Multiple health frameworks. |
| SH-041 `requestNotification` | Notification | Later severe alert delivery. | Alert trigger meaning. | Direct email/SMS/push. |

#### Data / Schema

If `PR-CL09-05` is accepted:

- add Prisma models for `SystemEvent`, `IntegrationFailure`, `QueueJob`, and `OpsIncident` according to an explicitly approved schema specification;
- add explicit status/severity/source-reference/request-correlation indexes;
- mark `QueueJob` as operational visibility rather than authoritative work payload/business completion truth;
- keep Sentry/logging/metrics provider references secondary.

If the ruling is rejected in favor of external-only telemetry, the feature must document exactly which Workin Ants operational truth is queryable when providers expire or are unavailable and revise the Module architecture before implementation proceeds.

#### Public Interfaces

Minimum interfaces:

- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`
- SH-039 `checkServiceHealth`
- SH-035 `captureException` through infrastructure adapter
- SH-036 `emitMetric`
- protected `queryIntegrationFailures` and `queryQueueJobs` if persisted

SH-040 `correlateOpsIncident` persistence can be introduced here only if incident schema/status is approved; otherwise incident grouping is deferred to Feature 09.

#### Logic

- Normalize technical failure details from owner-provided result; never parse arbitrary domain/provider payloads generically.
- Preserve source Module, operation, source record ref, request ID, retryability, safe code/classification, attempt info.
- Queue telemetry records claim/start/attempt/heartbeat/retry/completion/dead-letter visibility without deciding business completion.
- Health checks use bounded timeouts and distinguish readiness from informational degradation.
- Structured logger and error adapter sanitize before serialization/transmission.

#### UI / Administrative Surface

A minimal protected health/failure proof surface is acceptable. The complete operations dashboard is deferred to Feature 09.

#### Authorization / Compliance

- Public health endpoint exposes minimal non-sensitive information only.
- Detailed health/failure/queue queries require Role / Authority.
- Sensitive diagnostics may require SH-030 `recordSensitiveAccess`.
- No secrets, provider credentials, PHI, card data, SSNs, raw resume content, or message bodies in telemetry.

#### Events / Jobs / Integrations

- Sentry adapter for exceptions.
- Logging and metrics adapters behind provider-neutral ports.
- Shared queue runner instruments SH-038 `recordQueueTelemetry` automatically.
- No provider webhook dedupe is introduced here.

#### Failure Behavior

- Observability failure must not recursively crash the business request; use bounded fallback logging where safe.
- If persistence is unavailable, return a typed telemetry failure to callers whose policy requires proof; otherwise degrade according to owner policy.
- Sentry/logging provider outages are reported through local fallback/health without creating recursive provider-failure loops.

#### Tests

- Unit: redaction, failure normalization, health mapping, metric dimensions.
- Integration: persistence/query if approved.
- Provider: Sentry adapter with sanitized payload.
- Queue: telemetry for retry/dead-letter.
- Contract: source Modules cannot write provider-specific payloads as domain types.
- Security: health detail authorization and redaction.

#### Out of Scope

- Business retry policy.
- Provider-event dedupe or reconciliation ownership.
- Full incident dashboard/automation.
- Automatic production alert thresholds.

#### Exit Gate

1. `PR-CL09-05` and status/lifecycle decisions are documented before any canonical operational migration.
2. One logger, Sentry adapter, metrics interface, request context, and health registry are used by CL-09 code.
3. SH-037 `recordIntegrationFailure` and queue telemetry preserve source references without replacing business state.
4. Detailed operational queries are protected and redacted.
5. Provider/queue failure tests prove no direct mutation of source business records.
6. typecheck/lint/tests/build pass.

---

## Phase 2 — Intake and Stop Signs

### 03 Moderation Report, Legal Notice, and Case Intake

Build the first end-to-end moderation/legal vertical slice: intake -> authoritative records -> triage/case -> protected review query.

#### Objective

Allow users/controlled external submitters/admins to create reports or formal notices and allow authorized reviewers to triage them and open/query moderation cases without yet executing destructive downstream enforcement.

#### User-visible / Observable Result

- A user/source Module can submit a report and receive a report ID/status.
- A controlled legal-intake flow can create a formal `LegalNotice` distinct from a casual report.
- An authorized reviewer can triage a report, open/assign a moderation case, and list a moderation queue.
- A case view shows owner-composed safe target summaries without unrestricted cross-domain DB reads.

#### Owning Module(s)

Content Moderation & Legal Notice.

#### Dependencies

- Features 01 and 02.
- Identity/Role contracts.
- SH-123 `validateOwnedTargetReference` owner stubs for initial supported targets.
- Verify migration compatibility with current `@@map("moderation_target_type")`, including `media_access_grant`; CL-09-R017 corrects the snapshot, not migration provenance.
- `U-03` multi-report aggregation does not block a single-trigger-report MVP; the implementation must explicitly support only the current one-report relation until ruled otherwise.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-101 `submitModerationReport` | Moderation | Canonical report intake. | Report reasons/source/evidence requirements. | Local report tables. |
| SH-123 `validateOwnedTargetReference` | Target owner | Verify typed target exists/eligible. | Supported target/action combinations. | Cross-domain Prisma repository. |
| SH-001 `resolveAuthenticatedActor` | Identity | Reporter/reviewer identity. | Controlled external notice identity policy. | Local auth. |
| SH-002 `authorizeResourceAction` | Role | Reviewer/admin actions. | Moderation actions/target facts. | `isModerator` logic. |
| SH-044 `executeIdempotentCommand` | Platform | Report/notice/case creation. | Semantic duplicate rules. | Local dedupe table. |
| SH-053 `transitionLifecycleState` | Shared mechanism | Report/case/notice transition plumbing. | Owner transition graph. | Generic global moderation policy. |
| SH-029 `appendAuditEvent` | Audit | Important review/admin actions. | Safe audit metadata. | Moderation audit table. |
| SH-033 `writeStructuredLog` | Ops | Diagnostic execution. | Safe dimensions. | Local logger. |

#### Data / Schema

- `Report`, `ReportReason`, `ReportSource`, `ReportStatus`.
- `LegalNotice`, `LegalNoticeType`, `LegalNoticeStatus`.
- `ModerationCase`, `ModerationCaseStatus`.
- Existing `assignedAdminUserId` can support direct assignment to an authorized reviewer.
- Do not add a multi-report join until `U-03` is ruled.
- Do not add repeat-infringer/fingerprint schemas.
- Verify current `ModerationTargetType` mapping `@@map("moderation_target_type")` and values including `media_access_grant` against migration/database evidence; no mapping change is authorized by CL-09-R017.

#### Public Interfaces

- SH-101 `submitModerationReport`
- `getReportStatus`
- `submitLegalNotice`
- `getLegalNoticeStatus`
- `triageReport`
- `openModerationCase`
- `assignModerationCase`
- `getModerationCase`
- `listModerationQueue`

#### Logic

- Report intake distinguishes source/reason/target/evidence refs.
- Legal notice intake validates structural fields but does not claim legal sufficiency until `validateLegalNotice` policy is approved.
- Report and legal-notice flows remain separate even if both lead to a case.
- Target resolver returns minimized safe summary; sensitive evidence stays behind owner access policy.
- Triage/case transitions use explicit state-machine rules. Where transition graph is not confirmed, implement only transitions approved in the feature spec.
- Case assignment requires authorized reviewer identity.

#### UI / Administrative Surface

- Basic report intake UI/API where applicable.
- Controlled legal notice intake surface.
- Admin moderation queue and case detail shell with safe target summary.
- UI must label report versus legal notice distinctly.

#### Authorization / Compliance

- Public/controlled intake rate limits and abuse controls.
- External legal submitter identity/contact handling follows approved policy; do not force a Workin Ants `User` if legal intake policy permits external submitters.
- Admin case views use Role / Authority.
- Sensitive target/evidence access calls Audit when required.
- No legal advice or fully automated legal disposition.

#### Events / Jobs / Integrations

- Source writes may publish report/case/notice event classes through outbox for downstream notification/admin projections.
- Notification may acknowledge receipt using SH-041 `requestNotification` once template/policy is available.
- No Search/Media enforcement yet.

#### Failure Behavior

- Invalid/unsupported target -> typed validation error; do not create orphan report unless policy explicitly allows unresolved external target evidence.
- Duplicate idempotency key -> replay original result if fingerprint matches; conflict otherwise.
- Target owner unavailable -> retry or accept intake with clearly modeled unresolved-target policy only if approved; do not silently guess.
- Unauthorized reviewer -> deny without leaking case evidence.

#### Tests

- Unit: report/legal structural validation, target type mapping, transition guards.
- Integration: create/triage/open/assign/list case.
- Contract: target owner resolver/fake.
- Security: rate limits, authority, redacted case DTO.
- Idempotency/concurrency: duplicate intake and case-opening races.
- E2E: report -> triage -> case visible to reviewer.

#### Out of Scope

- Final legal validation rules/timing.
- Evidence snapshot proof.
- Moderation actions/enforcement.
- Counter-notice restoration.
- Repeat-infringer and duplicate detection.

#### Exit Gate

1. Report and LegalNotice are demonstrably separate flows.
2. Supported moderation targets validate through owner contracts, not direct foreign Prisma reads.
3. Case queue/detail is protected and redacted.
4. Current one-report-per-case limitation is documented and not hidden.
5. Current `ModerationTargetType` snapshot matches Prisma, including `media_access_grant`; migration provenance/compatibility is verified separately before migration.
6. All mutation/query/authorization/idempotency tests pass.

---

### 04 Reusable Compliance Hold Gate

Implement the canonical platform stop sign and prove at least one consumer can request, evaluate, and release it without local block state.

#### Objective

Make SH-012 `requestComplianceHold`, SH-011 `evaluateComplianceHold`, and SH-013 `releaseComplianceHold` the only authoritative CL-09 hold lifecycle path.

#### User-visible / Observable Result

- A source Module requests a hold with source/evidence context.
- A consuming workflow asks whether a named action is blocked and receives a safe decision.
- An authorized source/admin releases a hold and receives release proof.
- A demo consumer is blocked while the hold is active and allowed after release without reading a local boolean.

#### Owning Module(s)

Admin Review / Compliance Hold.

#### Dependencies

- Features 01 and 02.
- Identity/Role.
- CL-09-R006 confirms exactly one typed target per hold, explicit scope/applicability, controlled reason, source/requester provenance, source evidence, actor/system context, and semantic idempotency. Feature 04 still requires approval of the physical representation under PR-CL09-04/U-10.
- Resolve the U-12 storage representation and U-14 equivalence key/constraint strategy implementing the confirmed provenance and duplicate-prevention semantics.
- SH-054 `claimWorkItem` is **not** required for the base hold API; claim/escalation can remain deferred.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-012 `requestComplianceHold` | Hold | Create stop sign. | Reason/target/source validation. | Feature-local holds. |
| SH-011 `evaluateComplianceHold` | Hold | Action gate decision. | Reason/scope-to-action applicability. | Local `isBlocked`. |
| SH-013 `releaseComplianceHold` | Hold | Transition out of active. | Release authority/evidence. | Consumer status writes. |
| SH-123 `validateOwnedTargetReference` | Target owner | Validate hold target. | Supported target classes. | Generic cross-domain DB lookup. |
| SH-044 `executeIdempotentCommand` | Platform | Create/release replay safety. | Semantic hold key. | Hold-specific idempotency infrastructure. |
| SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency` | Shared DB | Duplicate/release race control. | Lock/equivalence key. | In-memory mutex. |
| SH-053 `transitionLifecycleState` | Shared | Hold transitions. | `active -> released/expired` rules. | Global lifecycle policy. |
| SH-029 `appendAuditEvent` | Audit | Hold creation/release proof. | Safe reason/source refs. | Hold audit table. |
| SH-041 `requestNotification` | Notification | Optional reviewer/affected-party alerts. | Who/when/what template. | Direct delivery. |

#### Data / Schema

- Preserve `ComplianceHold` ownership and reason/status enums.
- Implement a separately approved physical target representation under PR-CL09-04/U-10; the current three-nullable-FK shape is not final and CL-09-R006 does not choose its replacement.
- Add approved creation actor/requesting source/evidence/idempotency fields or relations required by `U-12`/canonical request contract.
- Encode semantic duplicate prevention/unique strategy from `U-14`.
- Do not add local hold fields to consumer schemas for convenience.
- Do not implement `expiresAt` or automatic expiry until `U-13` is ruled.

#### Public Interfaces

- SH-012 `requestComplianceHold`
- SH-011 `evaluateComplianceHold`
- SH-013 `releaseComplianceHold`
- `getComplianceHold`
- `listActiveComplianceHolds`

#### Logic

- Validate exactly one approved primary target representation.
- Confirm requested reason is valid and source/evidence references are structurally credible; the Hold Module does not re-adjudicate source compliance truth.
- Semantic duplicate requests return the existing equivalent hold or a deterministic conflict according to approved policy.
- SH-011 `evaluateComplianceHold` applies Hold-owned reason/scope/action mapping and returns safe reason codes/hold IDs.
- SH-013 `releaseComplianceHold` requires authorized actor/source decision reference and is idempotent.
- A released hold stays historical proof; no silent deletion/reopen.

#### UI / Administrative Surface

- Minimal hold detail/list view for admin proof.
- Consumer integration can use a test fixture or one real neighboring Module if available.
- Full review claim/escalation queue is Feature 08 or deferred until SH-054 `claimWorkItem` ruling.

#### Authorization / Compliance

- Source system/admin permissions validated server-side.
- Hold release may require step-up only if security policy designates it.
- Hold note/source metadata must not copy sensitive source payloads.
- Hold reason is not exposed to unauthorized users if it could reveal sensitive compliance information.

#### Events / Jobs / Integrations

- Publish hold created/released event classes through outbox if consumers need asynchronous reaction.
- Notification request is optional/policy driven.
- No expiration worker until expiry semantics exist.

#### Failure Behavior

- Unsupported target/reason -> reject.
- Duplicate equivalent hold -> replay existing result or deterministic conflict.
- Release of already released hold -> idempotent success if same semantic command; conflicting release reason/source -> typed conflict.
- Source owner unavailable during release validation -> retain active hold and return retryable failure; do not “fail open.”

#### Tests

- Unit: reason/action applicability, transition rules, duplicate semantics.
- Integration: request/evaluate/release persistence.
- Contract: at least one source owner/consumer.
- Concurrency: simultaneous equivalent creates, release races.
- Security: authority and safe reason exposure.
- E2E: active hold blocks action, release allows action.

#### Out of Scope

- Underlying KYC/tax/moderation/dispute decisioning.
- Automatic expiry.
- Generic manual review claim infrastructure.
- Candidate/resume hold integration until `U-15` resolved.

#### Exit Gate

1. A consumer can only obtain authoritative block state through SH-011 `evaluateComplianceHold`.
2. The CL-09-R006 semantic contract is implemented against a separately approved and documented target/provenance/equivalence storage design; schema approval is still a prerequisite.
3. Concurrent equivalent hold creation does not create uncontrolled duplicates.
4. Hold release records actor/reason/time/source decision reference as approved.
5. No new feature-local hold truth exists.
6. All lifecycle/contract/concurrency tests pass.

---

## Phase 3 — Adjudication and Enforcement

### 05 Evidence-Preserving Moderation Decisions

Add legal/moderation decision recording with immutable evidence preservation before destructive or public-visibility effects.

#### Objective

Allow an authorized reviewer to evaluate a case, preserve required evidence, record a `ModerationAction`, and generate an enforcement plan without yet assuming every downstream owner has completed its effect.

#### User-visible / Observable Result

- Reviewer sees case + minimized target context + protected evidence.
- Required evidence is captured in immutable/retention-protected form before enforcement.
- Reviewer records a moderation action and rationale.
- Case/action history is queryable and original evidence remains available to authorized reviewers after a target is hidden/frozen in test fixtures.

#### Owning Module(s)

Content Moderation & Legal Notice owns decision/evidence meaning. Media owns file bytes/storage mechanics. Audit owns generic access proof.

#### Dependencies

- Features 01–04.
- Acceptance of `PR-CL09-02` or another explicit immutable evidence design.
- Media evidence-storage/signed-access contract (real or stub).
- Hash primitive SH-072 `hashCanonicalPayload`.
- Legal validation policy/version may remain manual/approved-fixture based; do not invent law-specific rules.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-102 `resolveModerationTarget` | Proposed target-registry contract | Reviewer-safe target context. | Allowed targets/fields/actions. | Universal Prisma target repo. |
| SH-104 `preserveEvidenceSnapshot` | Proposed shared evidence mechanism | Freeze canonical evidence before enforcement. | Which evidence is required and legal meaning. | Audit-owned generic evidence blob. |
| SH-072 `hashCanonicalPayload` | Shared crypto | Hash canonical snapshot metadata/bytes. | Canonical fields and proof meaning. | Local hash helper. |
| SH-030 `recordSensitiveAccess` | Audit | Evidence-view proof. | Sensitivity/access outcome. | Local evidence access log. |
| SH-002 `authorizeResourceAction` | Role | Reviewer/action authority. | Moderation action permission. | Ad hoc admin checks. |
| SH-053 `transitionLifecycleState` | Shared | Case/report/notice transitions. | Moderation transition graph. | Global lifecycle policy. |
| SH-029 `appendAuditEvent` | Audit | Decision/admin action proof. | Safe case/action refs. | Local audit. |

#### Data / Schema

- `ModerationAction` remains decision/action truth.
- Implement approved evidence snapshot/reference schema if `PR-CL09-02` accepted; include target/source version, capturedAt, canonical hash, Media reference, policy/version, retention classification, and chain-of-custody fields required by approved design.
- Do not store full binary evidence in generic JSON fields.
- Do not use `AuditEvent` as the evidence snapshot.
- Do not add repeat-infringer/fingerprint records.

#### Public Interfaces

- `evaluateModerationCase` (internal domain service)
- `recordModerationAction`
- protected `getModerationCase`
- evidence snapshot creation/read contract
- `queryActiveModerationRestriction` for consumers

#### Logic

- Evaluate case using owner policy and owner-provided target facts.
- Require evidence snapshot before actions marked evidence-destructive/public-removal sensitive.
- Record decision before dispatching downstream effects.
- Preserve action immutability; reversal/restoration creates later action/evidence rather than rewriting history.
- Case/notice/report transitions occur according to explicitly approved rules only.

#### UI / Administrative Surface

- Reviewer case detail with evidence references, target summary, decision controls, rationale, and confirmation of preservation.
- Explicit warning when an action requires evidence preservation and preservation is incomplete.
- Sensitive evidence rendered only through protected Media access.

#### Authorization / Compliance

- Reviewer authority server-side.
- Sensitive evidence access audited.
- High-risk action step-up only per approved Identity/Security policy.
- No automatic legal advice or final legal decision from AI.
- Evidence retention classification recorded, but retention duration may remain pending legal policy.

#### Events / Jobs / Integrations

- After transaction commits, publish moderation action event or enqueue enforcement workflow for Feature 06.
- Evidence Media operations use Media provider adapter indirectly.
- Technical preservation failures go to Observability and block destructive enforcement where policy requires preservation.

#### Failure Behavior

- Evidence preservation failure -> do not execute destructive action; keep case reviewable and surface operational failure.
- Target changed between review and action -> optimistic conflict; refresh target/evidence and re-evaluate.
- Unauthorized evidence access -> deny and record appropriate sensitive access outcome where policy requires.

#### Tests

- Unit: evidence-required action matrix, decision validation, transition guards.
- Integration: snapshot/reference + action transaction.
- Contract: Media evidence storage/access.
- Security/compliance: protected evidence audit; prohibited metadata.
- Concurrency: stale target/case version rejects action.
- E2E: preserve evidence -> record action -> hidden-target fixture still has reviewer-safe evidence.

#### Out of Scope

- Downstream enforcement success tracking.
- Repeat-infringer automation.
- Content fingerprinting.
- Automated legal deadlines.

#### Exit Gate

1. Evidence-sensitive actions cannot proceed without approved preservation proof.
2. `ModerationAction` is created only after target/case validation and evidence requirements pass.
3. Evidence bytes remain Media-owned and privately accessible through owner contracts.
4. Sensitive evidence reads produce AccessAuditLog proof.
5. Decision/action history is not rewritten on reversal.
6. Tests prove destructive dispatch is blocked on evidence failure.

---

### 06 Cross-Module Moderation Enforcement and Reconciliation

Dispatch an approved `ModerationAction` to the correct target owners and track acknowledgments/retries without stealing execution truth.

#### Objective

Make one moderation decision reliably cause the required Search, Media, Messaging, Marketplace, Digital Goods, Video, Hold, or other owner-local effects through stable contracts and idempotent orchestration.

#### User-visible / Observable Result

A reviewer can see whether each required effect for an action is pending, acknowledged, completed, failed, or restored **as orchestration correlation**, while the actual target state is still owned and queryable from the target Module.

#### Owning Module(s)

- Moderation owns the decision and orchestration correlation.
- Each target Module owns execution truth.
- Observability owns technical failure visibility.

#### Dependencies

- Feature 05.
- Acceptance of `PR-CL09-03` / SH-105 `correlateEnforcementResult` design.
- Shared SH-049 `orchestrateWorkflowSteps`, queue, retry, outbox, idempotency.
- Target-owner execution handler contracts; fakes allowed initially.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-103 `executeModerationDecision` | Moderation + target owner protocol | Owner-local effect dispatch. | Action -> required owner/effect mapping. | Direct cross-module DB writes. |
| SH-105 `correlateEnforcementResult` | Proposed Moderation capability | Track ack/retry/restoration. | Required step/partial completion meaning. | Target state copied into Moderation. |
| SH-049 `orchestrateWorkflowSteps` | Shared runner | Multi-step execution. | Ordering/required/compensation semantics. | Global saga policy. |
| SH-046 `publishDomainEvent` | Outbox infra | Reliable post-transaction dispatch. | Event meaning. | Fire-and-forget. |
| SH-047 `enqueueReliableJob` | Shared queue | Async dispatch/reconciliation. | Payload and completion. | Local queue framework. |
| SH-048 `executeRetryWithBackoff` | Shared queue | Technical retry. | Retryability/legal side effects. | Custom loops. |
| SH-045 `deduplicateDomainEvent` / SH-044 `executeIdempotentCommand` | Shared infra | Replay safety. | Handler semantic identity. | Ad hoc processed tables. |
| SH-091 `requestSearchProjectionRefresh` | Search | De-index/re-index request. | Moderation decision reason. | Typesense write. |
| SH-012 `requestComplianceHold` | Hold | Stop sign where required. | Whether moderation action requires hold. | Payout/profile local blocks. |
| SH-037 `recordIntegrationFailure` | Ops | Technical failure evidence. | Safe source refs. | Moderation failure table. |
| SH-029 `appendAuditEvent` | Audit | Administrative action/workflow proof. | Safe IDs/outcomes. | Local audit. |
| SH-041 `requestNotification` | Notification | Affected-party/admin notifications. | Message meaning/template. | Direct delivery. |

#### Data / Schema

- Preserve `ModerationAction` as immutable decision.
- Implement approved enforcement run/step correlation schema or equivalent durable workflow record from `PR-CL09-03`.
- Required fields should identify case/action, target/effect, target-owner Module, idempotency key, attempt state, acknowledgment/result reference, correlation, timestamps, and restoration linkage without copying target source fields.
- Do not put target-owner lifecycle statuses into Moderation as canonical state.

#### Public Interfaces

Target-owner handler contract must return a normalized result such as:

- acknowledged;
- completed with owner state/evidence reference;
- retryable failure;
- terminal/manual-review failure;
- already applied/idempotent replay;
- restored/already restored.

Exact enum names belong in the approved protocol specification.

For supported Job/Organization effects, the Organization Hiring provider contract and retry-safe handler must be available before Feature 06 enables them. Feature 11 must prove that bilateral SH-103 `executeModerationDecision` contract with real launch-critical owners; this does not resequence either Cluster or authorize a CL-09 fallback writer.

#### Logic

**CL-09-R007 — Primary target versus downstream effect.** The primary moderation target identifies the subject of the moderation/legal decision. A downstream affected record is not automatically a primary target. Order/payout blocking uses `ComplianceHold` where a reusable stop sign is required. Digital Goods Access executes DigitalDownloadGrant revocation; Video Infrastructure executes CourseVideoPlaybackGrant revocation. These owner-local effect references may travel through SH-103 `executeModerationDecision` requests/results without extending `ModerationTargetType`. Existing `media_access_grant` remains valid. Any new first-class decision target requires a separate explicit vocabulary ruling; no enum extension is authorized here.

**CL-09-R003 — Organization Hiring executor.** Moderation issues the decision; Organization Hiring executes supported effects against `Job` and `Organization` through SH-103 `executeModerationDecision` and returns execution evidence. Hiring validates owner-local transitions and retains every mutation to those records. Its retry-safe result must distinguish accepted, rejected, idempotently already applied, retryable failure, and terminal failure as supported by the eventual contract, within the canonical acknowledged/completed/failed/restored evidence boundary. Exact effect/result encoding remains for the owner contract; this does not create a competing operation or permit CL-09 database writes to Hiring.

- Map each `ModerationActionType` to required owner steps.
- Validate the primary decision target separately from each owner-local execution effect under CL-09-R007. Enabled effects require approved owner mappings; absence of a child record from `ModerationTargetType` does not require an enum extension.
- Dispatch owner commands only after action transaction commits.
- Each owner independently validates the request and writes its own state.
- Track acknowledgments and retry only technical failures judged retryable by the owner.
- Case closure requires owner-defined required-step completion policy; do not close merely because jobs were enqueued.
- Restoration creates new authorized restoration work, not deletion of prior history.

#### UI / Administrative Surface

- Case action detail displays each required enforcement effect and current orchestration result.
- Failures expose safe retry/manual-review controls for authorized staff.
- Target owner current state may be linked/read through its public query, not copied into Moderation as truth.

#### Authorization / Compliance

- Only authorized moderation decisions can produce signed/typed enforcement envelopes.
- Target owner re-validates command source/shape and cannot accept arbitrary client-generated enforcement.
- Notifications use safe template variables.
- Sensitive effect details remain minimized.

#### Events / Jobs / Integrations

- Async workers for dispatch/retry/reconciliation.
- Search via Search owner.
- Media via Media owner.
- Messaging via Messaging owner.
- Digital Goods/Video via their owners.
- Hold via canonical hold command.
- Technical failures to Observability.

#### Failure Behavior

- One step fails after others succeed -> retain partial orchestration state; retry only failed retryable step; do not roll back successful owner state unless moderation policy defines restoration/compensation.
- Target owner reports terminal conflict -> route case to manual review; do not fake success.
- Duplicate dispatch -> owner idempotency returns existing effect.
- Queue dead-letter -> visible operational failure and moderation action remains unresolved for required steps.

#### Tests

- Contract tests for every supported target-owner handler.
- Integration: multi-step action with partial success/failure.
- Idempotency: repeated dispatch cannot duplicate destructive effects.
- Concurrency: restoration vs late original retry.
- Observability: failed step visible with correlation.
- E2E: moderation action -> Search de-index + Media freeze + hold request in a supported fixture.

#### Out of Scope

- New target lifecycle ownership.
- Provider-specific implementation inside Moderation.
- Repeat-infringer/fingerprint policy.
- Legal deadline automation.

#### Exit Gate

1. No target owner is mutated directly from Moderation repositories.
2. Every supported action has an explicit allowed target/effect mapping.
3. Required steps have durable idempotent correlation if `PR-CL09-03` accepted.
4. Partial failure is visible and does not silently close the case.
5. Search/Media/Hold/Notification interactions use canonical owner contracts.
6. Contract, retry, idempotency, partial-failure, and E2E tests pass.

---

### 07 Counter-Notice, Restoration, and Approved Deadlines

Complete the reversible legal/moderation workflow without inventing legal timing.

#### Objective

Support counter-notice intake, waiting/review states, explicit restoration decisions, and deadline work only when approved legal policy supplies the timing and transition rules.

#### User-visible / Observable Result

- A controlled submitter can provide a counter-notice linked to the original legal workflow.
- Reviewer can see counter-notice state and decide restoration/rejection/escalation according to approved policy.
- Restoration reactivates owner-local access/visibility through the same execution protocol and preserves historical action records.
- If legal deadline policy is approved, overdue/approaching work is surfaced by a worker and admin queue.

#### Owning Module(s)

Content Moderation & Legal Notice.

#### Dependencies

- Feature 06.
- Approved counter-notice linkage/cardinality rule.
- `U-25` only for automated deadlines; manual policy-driven transitions can proceed without scheduling automation.
- Notification templates/recipient resolver for legal communications.

#### Shared Operations Used

| Canonical operation | Owner | How this feature uses it | Local policy supplied here | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-053 `transitionLifecycleState` | Shared mechanism; Moderation owns policy | Apply notice/case transitions. | Counter-notice/restoration transition graph. | A generic legal state machine. |
| SH-055 `runDeadlineExpiration` | Shared scheduler/queue | Dispatch approved deadline work. | Legal deadline calculation and resulting owner command. | Module-specific cron engine. |
| SH-047 `enqueueReliableJob` | Shared queue infrastructure | Run restoration/deadline work asynchronously. | Payload and completion meaning. | Local queue framework. |
| SH-048 `executeRetryWithBackoff` | Shared queue/platform | Retry transient restoration/deadline failures. | Which legal/provider effects are safe to retry. | Hand-written retry loops. |
| SH-103 `executeModerationDecision` | Moderation + target owner protocol | Apply restoration to target owners. | Restoration decision/effect mapping. | Direct foreign writes. |
| SH-105 `correlateEnforcementResult` | Proposed Moderation capability | Track restoration acknowledgments/failures. | Required steps and completion meaning. | Copying target lifecycle state. |
| SH-041 `requestNotification` | Notification | Deliver counter-notice/restoration communications. | Recipient/message meaning and approved template. | Direct email/SMS/push. |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Record important reviewer/legal actions. | Safe notice/case/action metadata. | Local legal audit table. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Record protected evidence access. | Sensitivity and owner access decision. | Local evidence access log. |
| SH-033 `writeStructuredLog` | Observability / Ops | Diagnose execution. | Safe operational fields. | Local logger. |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Surface technical delivery/restoration/deadline failure. | Retryability/source reference. | Local failure table. |

#### Data / Schema

- Continue using `LegalNotice.status` and `ModerationCase.status` under explicit transition policy.
- Do not invent a dedicated correspondence timeline until `U-09` is ruled.
- If additional counter-notice linkage is required beyond current `LegalNotice`/case relation, add it only under an approved schema specification.
- `actionDueAt` is used only when an approved legal policy defines how it is calculated and what happens at expiry.

#### Public Interfaces

- counter-notice submission/status query;
- `processCounterNotice` internal application command;
- restoration/rejection/escalation commands;
- legal deadline worker entry point if enabled.

#### Logic

- Validate counter-notice structural requirements and relationship to original notice/case.
- Move case/notice into waiting/review state only through owner transition policy.
- Restoration creates a new `ModerationAction` or equivalent approved restoration decision and dispatches owner restoration commands.
- Historical takedown/action evidence stays immutable.
- Deadline worker dispatches owner commands; it does not hardcode legal outcomes in scheduler code.

#### UI / Administrative Surface

- Counter-notice intake/status surface.
- Admin case timeline showing notice/action/counter-notice/restoration records.
- Deadline indicators only from approved `actionDueAt` policy.

#### Authorization / Compliance

- Controlled submitter access does not expose restricted case evidence.
- Legal reviewer authority server-side.
- No statement that Notification delivery proves legal receipt unless policy explicitly says so.
- Legal policy version/reference included in decisions where the approved design supports it.

#### Events / Jobs / Integrations

- Restoration uses the same target-owner protocol and idempotency as enforcement.
- Deadline worker uses shared scheduler/queue; dead-letter visible in Observability.
- Notification sends counter-notice/takedown/restoration communications.

#### Failure Behavior

- Missing/ambiguous original notice linkage -> reject or manual review; do not attach by fuzzy guess.
- Restoration partial failure -> remain unresolved; reconcile owner steps.
- Deadline policy absent -> worker disabled; admin may still act manually under approved legal instruction.

#### Tests

- Unit: counter-notice transition guards and restoration decision rules.
- Integration: linked counter-notice and restoration action.
- Idempotency: repeated counter-notice/restoration submission.
- Worker: clock-controlled deadline tests only with policy fixture.
- E2E: takedown -> counter-notice -> restoration across at least one Search/Media target.

#### Out of Scope

- General legal correspondence system.
- Repeat-infringer status.
- Legal advice generation.
- Unapproved statutory timing.

#### Exit Gate

1. Counter-notice is linked deterministically to legal/case truth.
2. Restoration never deletes/relabels original action history.
3. Owner-local restoration effects are idempotent and reconciled.
4. Automated deadlines run only from approved policy fixtures.
5. Notification and evidence access boundaries pass security/compliance tests.

---

## Phase 4 — Admin Review and Operational Surfaces

### 08 Moderation, Hold, and Audit Administrative Review Surfaces

Turn the underlying source records into protected operator workflows without creating a generic Cluster-owned review lifecycle.

#### Objective

Provide secure admin surfaces for moderation cases, active holds, audit evidence, and sensitive-access history, with safe cross-Module context and auditable reviewer actions.

#### User-visible / Observable Result

Authorized admins/support/legal reviewers can:

- list/filter assigned/unassigned moderation cases;
- inspect a moderation case and its enforcement results;
- list/view active/released holds;
- request/release holds if authorized;
- search generic audit/access evidence;
- view protected evidence only through redacted/owner-authorized surfaces;
- see every sensitive admin read reflected in audit evidence where required.

#### Owning Module(s)

Each Module owns its own admin surface data and actions:

- Moderation for case queues/details;
- Hold for hold queue/details;
- Audit for audit viewer;
- no Cluster-level generic record owner.

#### Dependencies

- Features 01, 03–07.
- Role / Authority policies.
- Optional SH-054 `claimWorkItem` acceptance for durable claim/lease behavior beyond existing `ModerationCase.assignedAdminUserId`.
- Sensitive target owner redaction/read contracts.

#### Shared Operations Used

| Canonical operation | Owner | How this feature uses it | Local policy supplied here | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-002 `authorizeResourceAction` | Role / Authority | Gate every admin query/action. | Moderation/hold/audit action vocabulary and owner facts. | Local admin permission engine. |
| SH-014 `requireStepUpForSensitiveAction` | Identity & Access | Add fresh assurance where approved. | Which admin actions require step-up. | Local MFA checks. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Record protected evidence/diagnostic reads. | Sensitivity and contextual outcome. | Per-screen access log. |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Record reviewer/admin mutations. | Safe action/target metadata. | Admin audit helper/table. |
| SH-054 `claimWorkItem` | Proposed shared review claim capability | Claim/lease review work if accepted. | Reviewer eligibility, assignment, escalation. | Universal or per-screen claim primitive. |
| SH-123 `validateOwnedTargetReference` | Target owner | Resolve safe owner summaries. | Which target context is needed. | Cross-domain Prisma lookup. |
| SH-041 `requestNotification` | Notification | Reviewer assignment/escalation alerts. | Trigger/recipient/message meaning. | Direct delivery. |
| SH-033 `writeStructuredLog` | Observability / Ops | Diagnose admin workflow failures. | Safe operation fields. | Local logger. |

#### Data / Schema

- Do not create a universal `AdminReviewCase` table that merges `ModerationCase`, `ComplianceHold`, `JobComplianceCheck`, etc.
- Moderation uses existing assignment fields unless shared claim mechanics are accepted.
- Hold review assignment/priority/escalation remains limited by `U-11`; if no persistent review schema is approved, the hold UI may provide a read-only/filterable active review queue plus authorized hold transitions, but must not claim lease/assignment semantics it cannot persist.
- Audit viewer uses redacted DTO projections, not a new source-of-truth table.

#### Public Interfaces

- Moderation queue/detail/action queries/commands.
- Hold list/detail/evaluate/release queries/commands.
- Audit/access evidence queries.
- Optional review-claim interface if accepted.

#### Logic

- Compose safe summaries by calling owner public queries.
- Separate not-found from forbidden where information leakage matters.
- Reviewer actions go through owner commands and append audit proof.
- Sensitive evidence reads call SH-030 `recordSensitiveAccess`.
- Pagination/filtering uses owner indexes and bounded queries.

#### UI / Administrative Surface

This is primarily a UI/admin feature:

- Moderation queue with status/assignee/deadline/action state.
- Case detail with evidence, action history, enforcement results, safe target context.
- Hold queue/detail with target/reason/status/source refs and release controls.
- Audit viewer with actor/action/target/date/request/sensitivity filters.
- Clear visual separation between moderation decision, hold state, audit proof, and operational failures.

#### Authorization / Compliance

- Route protection plus server-side action checks.
- Sensitive fields hidden by default and revealed only through owner policy.
- No admin role implies unrestricted PHI, financial, resume, contract, private message, or security data access.
- Step-up applied only per approved security policy.
- Export/download actions are separately authorized and audited.

#### Events / Jobs / Integrations

- Assignment/escalation notifications use Notification.
- No direct provider calls.
- Admin actions emit owner events/audit as required.

#### Failure Behavior

- Target summary owner unavailable -> show safe unavailable state; do not bypass via direct DB query.
- Stale case/hold -> optimistic conflict and refresh.
- Audit query too broad -> require narrower bounded filters/pagination.

#### Tests

- UI/component tests for redaction and action-state rendering.
- Integration tests for route/action authorization.
- Sensitive-access audit completeness.
- Contract tests for owner-composed target summaries.
- E2E reviewer journey: case decision; hold release; audit search.

#### Out of Scope

- Generic admin dashboard shell outside CL-09 scope.
- Universal review queue across all platform Modules.
- Legal correspondence center.

#### Exit Gate

1. Each screen writes only through the owning Module's commands.
2. Sensitive views are owner-authorized and access-audited.
3. No universal admin repository or review truth is introduced.
4. Hold UI does not claim assignment/lease semantics absent from schema.
5. Critical reviewer E2E journeys pass.

---

### 09 Ops Incident, Failure, Queue, and Health Dashboard

Complete the operational control surface after the underlying Observability contracts have proven themselves in earlier workers.

#### Objective

Give operators a protected view of integration failures, queue problems, health degradation, request traces, and incidents without converting operational state into business state.

#### User-visible / Observable Result

Operators can:

- search unresolved/recent integration failures;
- inspect queue attempts/retries/dead-letter state;
- view component health;
- correlate request/source references;
- open/update/resolve an `OpsIncident` if its schema/lifecycle is approved;
- receive an alert for approved severe conditions.

#### Owning Module(s)

Observability / Ops.

#### Dependencies

- Feature 02.
- `OpsIncident` persistence/status decision from `PR-CL09-05`/`U-20`.
- Notification alert contract.
- Owner health checks for Search, Media, Payment, Calendar, Notification, queue, etc. can be registered incrementally.

#### Shared Operations Used

| Canonical operation / interface | Owner | How this feature uses it | Local policy supplied here | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| `queryIntegrationFailures` | Observability / Ops | Populate failure views. | Filter/redaction rules. | Direct table/UI repository bypass. |
| `queryQueueJobs` | Observability / Ops | Populate queue views. | Operational filter semantics. | Domain job dashboard copies. |
| SH-039 `checkServiceHealth` | Observability coordinates; component owner supplies check | Build health view. | Dashboard aggregation/visibility. | Per-dashboard health calls. |
| SH-040 `correlateOpsIncident` | Observability / Ops | Group related operational signals. | Incident grouping/severity/transition policy. | Local incident system. |
| SH-036 `emitMetric` | Observability / Ops | Publish dashboard/alert metrics. | Approved names/dimensions. | Local metrics client. |
| SH-035 `captureException` | Observability / Ops | Capture dashboard/worker exceptions. | Safe grouping/context. | Direct Sentry client. |
| SH-041 `requestNotification` | Notification | Send approved operational alerts. | Alert trigger/recipients/priority. | Direct notification provider calls. |
| SH-002 `authorizeResourceAction` | Role / Authority | Protect detailed operations tooling. | Ops action vocabulary. | Local ops admin guard. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Audit protected diagnostic access. | Sensitivity/access outcome. | Ops-sensitive audit table. |
| SH-033 `writeStructuredLog` | Observability / Ops | Log dashboard/incident operations. | Safe structured fields. | Local logger. |

#### Data / Schema

- Use approved `SystemEvent`, `IntegrationFailure`, `QueueJob`, `OpsIncident` models if persisted.
- Do not add domain business state columns to these records.
- Incident associations point to operational/source references; they do not own foreign records.
- If an external provider/dashboard remains the only store for a signal, store only the approved provider reference/context needed for correlation.

#### Public Interfaces

- `queryIntegrationFailures`
- `queryQueueJobs`
- `getOperationalHealth`
- `correlateOperationalTrace`
- `openOpsIncident`, `updateOpsIncident`, `queryOpsIncidents` if approved

#### Logic

- Build bounded filters by Module/provider/operation/status/request/source/time.
- Correlate using request/correlation IDs and source references.
- Incident grouping must be deterministic and explainable; automatic thresholds remain disabled until approved.
- Resolution of an OpsIncident does not mutate or “resolve” provider/business source records.
- Health status is a projection of registered checks.

#### UI / Administrative Surface

- Ops dashboard cards/list for health, failures, queues, incidents.
- Failure detail with request trace and source link.
- Queue detail with attempts/retry/dead-letter.
- Incident detail with linked operational signals.
- No sensitive domain payload dump.

#### Authorization / Compliance

- Detailed ops surface restricted by Role / Authority.
- Sensitive diagnostics redacted and access-audited.
- Low-cardinality safe dimensions only.

#### Events / Jobs / Integrations

- Optional stalled-job detector/index-lag/provider-health monitors use shared queue/scheduler.
- Severe approved incident conditions request Notification alerts.
- Sentry/logging/metrics remain provider adapters/telemetry sources.

#### Failure Behavior

- Telemetry provider unavailable -> dashboard shows degraded/unavailable check; do not fabricate “healthy.”
- Missing source owner -> show source unavailable and retain operational record.
- Incident update race -> optimistic conflict.

#### Tests

- Unit: incident grouping/health aggregation.
- Integration: failure/queue/incident queries.
- UI: safe rendering and filters.
- Security: protected diagnostics.
- E2E: worker failure -> visible failure -> incident -> notification request.

#### Out of Scope

- Business workflow remediation that belongs to source Module.
- Provider reconciliation implementation outside owner Modules.
- Automated alert thresholds not approved.

#### Exit Gate

1. Operators can trace at least one real/test provider or worker failure from request/source to queue/failure view.
2. Incident state, if implemented, never changes business source state.
3. Sensitive diagnostics are redacted and protected.
4. Health endpoint/dashboard distinguishes degraded/unavailable from healthy.
5. Ops alert delivery goes through Notification only.

---

## Phase 5 — Privacy and Cross-Cluster Contract Proof

### 10 CL-09 Privacy, Retention, and Export Executors

Make all four CL-09 data owners participate correctly in Privacy-owned workflows without creating local privacy orchestration.

#### Objective

Allow Privacy / Data Erasure to discover CL-09 subject data, ask each owner whether retention is required, and execute approved erase/anonymize/export/retain actions with proof.

#### User-visible / Observable Result

A Privacy workflow test can:

- enumerate a subject's moderation/hold/audit/ops records;
- receive explicit owner retention facts;
- anonymize/erase permitted fields;
- retain protected legal/security records only through Privacy-owned exemption truth;
- export approved CL-09 data without exposing prohibited operational/audit payloads.

#### Owning Module(s)

- Privacy / Data Erasure owns request/job/exemption orchestration.
- Each of the four CL-09 Modules owns its local executor behavior.

#### Dependencies

- Features 01–09 as applicable.
- Resolve `U-24` privacy target vocabulary and approved retention policy for production.
- Media deletion/export contract where evidence assets are involved.
- External Observability provider deletion capability where applicable.

#### Shared Operations Used

| Operation | Owner | Use | Local policy | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-096 `enumerateSubjectData` | Each owner through Privacy contract | Discover CL-09 data. | Owner schema relationships/export meaning. | Global DB crawler. |
| SH-097 `evaluateRetentionRequirement` | Owner + Privacy | Return legal/security/fraud retention facts. | CL-09 record-specific fact. | Local exemption table. |
| SH-095 `executePrivacyInstruction` | Privacy orchestrates; owner executes | Erase/anonymize/export/retain. | Field-level behavior. | Local PrivacyRequest workflow. |
| SH-098 `anonymizePersonalFields` | Shared primitive | Safe pseudonymization. | Owner mapping/invariants. | Ad hoc scrubbing. |
| SH-029 `appendAuditEvent` / SH-030 `recordSensitiveAccess` | Audit | Privacy fulfillment/access proof. | Safe metadata. | Privacy audit duplicates. |
| SH-070 `deleteProviderResource` | Provider owner | External telemetry/evidence deletion where authorized. | Provider capability/retention. | Privacy direct provider credentials. |

#### Data / Schema

- Extend or formally define Privacy target types for CL-09 per `U-24`; do not use inconsistent arbitrary `other` strings.
- No local privacy job/exemption table.
- Evidence snapshots/Media references respect Privacy-owned retention result.
- Audit chain policy, if later enabled, must account for anonymization without falsifying integrity.

#### Public Interfaces

Each CL-09 Module implements Privacy-defined:

- subject-data enumerator;
- retention-fact evaluator;
- privacy instruction executor;
- export serializer where applicable.

#### Logic

**Moderation:** enumerate reporter/submitter/actor/target-linked data; retain legal evidence only with approved basis; anonymize allowed personal fields.

**Hold:** enumerate target/requester/releaser-linked data; retain fraud/security/financial proof only with approved basis.

**Audit:** retain minimum security/legal proof where required; anonymize personal identifiers if allowed; preserve proof of privacy fulfillment.

**Observability:** minimize or erase personal identifiers and external telemetry references according to approved retention/provider capability.

#### UI / Administrative Surface

No CL-09-specific privacy UI required. Observable result is Privacy job execution/reporting. Admin diagnostic view may show owner target status through Privacy's existing surface.

#### Authorization / Compliance

- Privacy verifies requester; CL-09 executors trust only authenticated/authorized Privacy commands.
- Retention decisions must cite owner fact and Privacy-owned exemption.
- No soft-delete substitution for legal erasure.
- No hard-delete of retention-locked evidence.

#### Events / Jobs / Integrations

- Execute via Privacy-owned job/orchestration and shared queue.
- Media/provider deletion through owner adapters.
- Search removal remains Search-owned if public projections exist.

#### Failure Behavior

- Unknown/unapproved retention basis -> do not invent exemption; return blocked/manual-review result.
- Provider deletion unavailable -> return provider result to Privacy for partial completion handling.
- Anonymization would break required evidence integrity -> return retention/manual-review fact until approved strategy exists.

#### Tests

- Contract tests for all four enumerators/executors.
- Integration: Privacy request target -> CL-09 executor result.
- Retention: retained vs anonymized vs erased fixtures.
- Security: executor cannot be called by ordinary clients.
- E2E: user erasure with moderation legal evidence retained and nonessential personal fields anonymized under an approved test policy.

#### Out of Scope

- Defining legal retention duration without counsel/policy.
- Privacy request UI/orchestration.
- Provider deletion outside CL-09-owned providers.

#### Exit Gate

1. All four CL-09 Modules are registered as Privacy data owners/executors.
2. No local PrivacyRequest/DataErasureJob/DataRetentionExemption truth exists in CL-09.
3. Production retention behavior is backed by approved policy/target vocabulary.
4. Export/anonymization tests prove prohibited data is not leaked.
5. Partial provider deletion failures return explicit outcomes to Privacy.

---

### 11 Cross-Cluster Integration Verification

Prove CL-09's most important inbound/outbound contracts against neighboring Clusters without importing their source truth.

#### Objective

Run contract and E2E verification across the control-tower bridges required for launch.

#### User-visible / Observable Result

The platform demonstrates the following integrated journeys with real Module contracts or production-equivalent adapters:

1. Report -> moderation case -> evidence -> action -> Search de-index.
2. Moderation action -> Media freeze/public URL removal -> authorized evidence access.
3. Moderation action -> ComplianceHold -> target action blocked.
4. Source compliance resolution -> hold release -> consumer action proceeds.
5. Sensitive finance/healthcare/resume/media/contract access -> `AccessAuditLog` proof.
6. Provider/worker failure -> Observability failure/queue view -> operator alert.
7. Privacy request -> CL-09 executors -> retention/anonymization outcome.

#### Owning Module(s)

All four CL-09 Modules for their own truth; neighboring owners for their side of each contract.

#### Dependencies

Features 01–10 and relevant neighboring Module implementations.

#### Shared Operations Used

| Canonical operation | Owner | How this feature uses it | Local policy supplied here | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-002 `authorizeResourceAction` | Role / Authority | Verify end-to-end actor permission across CL-09 entry points. | CL-09 action/relationship facts. | Local integration auth bypass. |
| SH-091 `requestSearchProjectionRefresh` | Search / Public Visibility | Prove moderation-driven de-index/re-index. | Moderation decision/source version. | Search writes in CL-09. |
| SH-103 `executeModerationDecision` | Moderation + target owners | Prove target-owner enforcement protocol. | Supported action/effect mapping. | Direct foreign mutation. |
| SH-012 `requestComplianceHold` | Admin Review / Compliance Hold | Prove source-owned hold request. | Source justification/evidence. | Local block models. |
| SH-011 `evaluateComplianceHold` | Admin Review / Compliance Hold | Prove consumer gate behavior. | Hold applicability. | Consumer interpretation from raw rows. |
| SH-013 `releaseComplianceHold` | Admin Review / Compliance Hold | Prove source-resolution release. | Release evidence/authority. | Foreign hold status write. |
| SH-029 `appendAuditEvent` | Audit / Event Ledger | Prove important integrated actions. | Safe metadata. | Domain audit copies. |
| SH-030 `recordSensitiveAccess` | Audit / Event Ledger | Prove sensitive integrated access. | Context owner access outcome. | Feature access log copies. |
| SH-041 `requestNotification` | Notification | Prove communication handoff. | Message meaning/recipient facts. | Direct delivery. |
| SH-037 `recordIntegrationFailure` | Observability / Ops | Prove provider/handler failure visibility. | Source refs/retryability. | Local generic failure tables. |
| SH-038 `recordQueueTelemetry` | Observability / queue infra | Prove async attempt/retry/dead-letter visibility. | Domain completion meaning. | Queue truth copies. |
| SH-096 `enumerateSubjectData` / SH-095 `executePrivacyInstruction` / SH-097 `evaluateRetentionRequirement` | Privacy protocol + CL-09 owners | Prove Privacy orchestration with owner-local execution. | Record-specific privacy behavior. | Local PrivacyRequest workflow. |
| SH-044 `executeIdempotentCommand` | Platform app infrastructure | Prove replay-safe mutations. | Semantic identities. | Per-bridge idempotency store. |
| SH-046 `publishDomainEvent` / SH-045 `deduplicateDomainEvent` | Platform event infrastructure | Prove outbox/inbox delivery. | Event names/handler effects. | Fire-and-forget or ad hoc dedupe. |
| SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` | Shared queue/platform | Prove async reliability. | Payload, retryability, completion. | Per-module queue framework. |

#### Data / Schema

No new cross-Cluster source table is created. Any integration-specific foreign reference is added only to the owning Module under its approved schema.

#### Public Interfaces

Verify production contracts for:

- Search;
- Media;
- Messaging;
- Digital Goods;
- Video;
- Payment/Payout/Tax;
- Verification/Healthcare/Job Compliance/Dispute sources;
- Notification;
- Privacy;
- Identity/Role.

#### Logic

- Replace contract fakes with real owner calls one bridge at a time.
- Confirm owner result semantics match CL-09 expectations.
- Verify errors remain typed and ownership-safe.
- Confirm eventual async effects are reconciled and observable.

#### UI / Administrative Surface

Use existing CL-09 admin surfaces to verify integrated state; do not build neighboring Cluster dashboards here.

#### Authorization / Compliance

- End-to-end actor and authority checks.
- Sensitive access logging completeness.
- No privilege widening at integration boundary.
- Public Search/Media surfaces reflect moderation/privacy decisions only after owner execution.

#### Events / Jobs / Integrations

- Outbox/inbox/retry path is exercised across process boundaries where applicable.
- Provider-owning Modules retain webhook/dedupe/reconciliation.
- Observability receives technical failures from integrated handlers.

#### Failure Behavior

- Neighbor owner unavailable -> queue/retry where safe; required moderation step remains unresolved.
- Contract version mismatch -> fail fast and block deployment rather than fallback to direct DB access.
- Search/Media/Notification provider failure -> visible operational failure; source decision remains preserved.

#### Tests

- Cross-Module contract suites.
- Playwright/admin E2E for moderation/hold/audit workflows.
- Async idempotency/retry/dead-letter integration tests.
- Privacy/compliance integration tests.
- Provider failure simulation through owner Modules.

#### Out of Scope

- Rebuilding neighboring source logic in CL-09.
- New product features unrelated to launch governance flows.

#### Exit Gate

1. Every launch-critical bridge uses a published owner contract/event.
2. No integration test relies on direct foreign Prisma writes.
3. The seven listed journeys pass with production-equivalent boundaries.
4. Provider failure simulation shows business truth + operational evidence remain separate.
5. Contract versions and dependency requirements are documented.

---

## Phase 6 — Production Hardening

### 12 CL-09 Security, Concurrency, Reconciliation, and Launch Hardening

Harden the complete Cluster for destructive actions, sensitive evidence, async retries, schema safety, privacy, and production operations.

#### Objective

Close launch-critical risk gaps without adding new domain scope.

#### User-visible / Observable Result

- Destructive/legal/admin workflows remain correct under retries, concurrency, provider degradation, partial failures, and unauthorized access.
- Operators can diagnose failures without exposing sensitive data.
- Backfills/reconciliation can run safely in dry-run mode.
- Privacy/audit controls are verified.
- Production readiness checks and rollback plans exist for CL-09 migrations/workers.

#### Owning Module(s)

All four CL-09 Modules plus shared platform infrastructure for the primitives they consume.

#### Dependencies

Features 01–11.

#### Shared Operations Used

| Canonical operation | Owner | How this feature uses it | Local policy supplied here | Must not be rebuilt |
| --- | --- | --- | --- | --- |
| SH-062 `reconcileProviderState` | Each provider-owning Module | Fault-injection and reconciliation verification for indirect provider effects. | Owner-specific repair policy. | CL-09 provider reconciliation. |
| SH-055 `runDeadlineExpiration` | Shared scheduler/queue | Harden approved legal/hold deadline work. | Owner deadline semantics. | Ad hoc cron loops. |
| SH-073 `hashChainRecords` | Proposed shared crypto capability | Verify audit chain only if accepted. | Audit chain partition/canonical fields/response to anomaly. | Local chain algorithm. |
| SH-054 `claimWorkItem` | Proposed shared review claim capability | Harden review claims if accepted. | Reviewer eligibility/lease/escalation. | Competing claim mechanisms. |
| SH-051 `acquireAggregateLock` | Shared persistence infrastructure | Serialize conflicting moderation/hold/incident commands. | Lock keys and conflict policy. | In-memory locks. |
| SH-052 `withOptimisticConcurrency` | Shared persistence infrastructure | Reject stale lifecycle mutations. | Retry/merge/conflict policy. | Custom stale-write checks. |
| SH-044 `executeIdempotentCommand` | Platform app infrastructure | Verify replay safety under faults. | Semantic command identity. | Local idempotency framework. |
| SH-047 `enqueueReliableJob` / SH-048 `executeRetryWithBackoff` | Shared queue/platform | Harden leases/retries/dead-letter. | Payload, attempts, retryability. | Per-module queue/retry framework. |
| SH-034 `sanitizeTelemetryMetadata` | Audit/Observability policy | Final prohibited-data controls. | CL-09 safe field allowlists. | Local redaction helpers. |
| SH-002 `authorizeResourceAction` / SH-014 `requireStepUpForSensitiveAction` | Role / Authority; Identity & Access | Final permission/assurance matrix. | CL-09 action facts and selected high-risk actions. | Local role/MFA systems. |

#### Data / Schema

Perform final schema review for:

- foreign-key/index correctness;
- polymorphic target constraints/registry validation;
- semantic uniqueness/idempotency keys;
- optimistic version fields where needed;
- append-only DB grants/policies;
- migration ordering and rollback/forward-fix plan;
- retention/index performance;
- Observability model retention/partitioning if implemented;
- destructive migration safety.

No unresolved schema is introduced merely to “finish” the phase.

#### Public Interfaces

- Freeze and version stable CL-09 contracts.
- Add compatibility tests and deprecation rules for any changed DTO/event version.
- Verify admin queries are bounded/paginated.

#### Logic

#### Security review

- IDOR/polymorphic target attacks.
- role escalation/admin service actions.
- sensitive evidence leakage.
- injection/oversized JSON/file abuse.
- telemetry redaction.
- signed access expiry.
- audit immutability.
- secret/provider credential boundaries.

#### Concurrency review

- duplicate reports/legal notices where idempotency applies;
- competing moderation decisions;
- action/restoration replay;
- duplicate holds;
- hold release/expiry race;
- incident updates;
- queue lease/duplicate execution.

#### Reconciliation/backfill

- moderation enforcement reconciliation for incomplete owner steps;
- Search/Media owner reconciliation remains in those Modules but CL-09 verifies moderation request state;
- failure/queue backfill only if operational records are rebuildable from existing telemetry/source events;
- dry-run before mutation;
- bounded cursor batches and checkpoints.

#### Performance

- indexes for moderation queues, legal notice deadlines, holds, audit queries, failures, queues, incidents;
- request payload/metadata size limits;
- pagination and retention strategy;
- no unbounded cross-domain joins.

#### UI / Administrative Surface

- Empty/loading/error/stale/conflict states.
- explicit partial enforcement and retry visibility.
- safe redaction and copy/download controls.
- accessibility and operator confirmation for destructive actions.

#### Authorization / Compliance

- Complete permission matrix reviewed with Role / Authority.
- Step-up matrix reviewed with Identity/Security.
- Sensitive-access audit completeness sampled/tested.
- Legal/privacy unresolved items either approved or explicitly disabled/deferred.
- No launch path depends on an unapproved legal timing/retention/fingerprint policy.

#### Events / Jobs / Integrations

- Retry/backoff/dead-letter thresholds configured.
- Worker concurrency/lease timeouts load-tested.
- Provider degradation simulated.
- Outbox/inbox cleanup/retention strategy documented.
- Operational alerts route through Notification and avoid recursive storms.

#### Failure Behavior

- Fail closed for legally required evidence preservation, hold checks designated mandatory, and sensitive authorization.
- Fail safe/degraded for optional telemetry surfaces where source workflow can proceed under owner policy.
- Never convert missing telemetry into “success.”
- Never bypass owner interfaces because a dependency is degraded.

#### Tests

- Full unit/integration/contract suite.
- Concurrency/load tests for holds/audit/admin queues.
- Security/authorization/RLS tests.
- Provider degradation/fault injection.
- Queue retry/dead-letter/replay tests.
- Privacy retention/erasure tests.
- Critical Playwright E2E journeys.
- Migration dry-run and rollback/forward-fix verification.

#### Out of Scope

- Repeat-infringer automation unless separately approved.
- Duplicate-content fingerprinting unless separately approved.
- Generic platform legal correspondence unless separately approved.
- New provider selections unrelated to launch.

#### Exit Gate

CL-09 is production-ready only when:

1. all previous feature gates are green;
2. no launch path depends on an unresolved architecture/legal decision;
3. all migrations are reviewed with destructive-change safety and tested on a production-like database; CL-09-R009 tests prove case hard deletion cannot cascade-delete retained `ModerationAction` proof. The retention-safe FK/deletion strategy requires separate schema approval;
4. audit insert-only enforcement is verified at database and application boundaries;
5. moderation enforcement and hold commands pass concurrency/idempotency/fault-injection tests;
6. provider/queue failures are observable and dead-lettered work is actionable;
7. privacy executors and retention behavior are approved and tested;
8. admin/sensitive evidence access passes permission, redaction, and access-audit tests;
9. critical E2E journeys pass;
10. typecheck, lint, unit, integration, Playwright, schema validation, and production build commands all pass;
11. progress tracker, architecture, Module plans, and completion report are updated.

---

## Cross-Cluster Integration Phase

Phase 5 Feature 11 is the dedicated Cross-Cluster Integration Phase for CL-09. It exists to prove the contracts that make CL-09 a control tower without making it a source-of-truth owner for neighboring domains.

The phase must specifically prove:

- Search is changed only through Search-owned projection commands;
- Media/file access is changed only through Media-owned commands;
- Notification delivery stays Notification-owned;
- provider/webhook truth stays with provider-owning Modules;
- Holds gate workflows without copying underlying compliance facts;
- sensitive access is decided by context owners and recorded by Audit;
- Privacy orchestrates and CL-09 Modules execute only their own data dispositions;
- target-owner execution acknowledgments never become foreign lifecycle ownership.

A failed Cross-Cluster contract is fixed at the contract/owner boundary. It is never “temporarily solved” with a direct foreign database write.

---

## Hardening Phase

Phase 6 Feature 12 is the dedicated hardening phase. It covers only CL-09-relevant production readiness:

- server-side security and authorization review;
- append-only audit enforcement;
- sensitive telemetry/evidence redaction;
- provider degradation and retry behavior;
- idempotency and concurrency;
- queue leases, retries, dead-letter handling, and operational visibility;
- moderation enforcement reconciliation;
- hold duplicate/release/expiry safety where expiry is approved;
- privacy/retention execution;
- audit completeness;
- health/incident/operational visibility;
- query/index performance;
- migration/backfill/destructive-change safety;
- critical workflow E2E verification.

It does not authorize unresolved product/legal features.

---

## Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Evidence and Operational Spine | 01 Audit Evidence and Request Correlation; 02 Operational Telemetry, Failure Visibility, and Health |
| 2 | Intake and Stop Signs | 03 Moderation Report, Legal Notice, and Case Intake; 04 Reusable Compliance Hold Gate |
| 3 | Adjudication and Enforcement | 05 Evidence-Preserving Moderation Decisions; 06 Cross-Module Moderation Enforcement and Reconciliation; 07 Counter-Notice, Restoration, and Approved Deadlines |
| 4 | Admin Review and Operational Surfaces | 08 Moderation, Hold, and Audit Administrative Review Surfaces; 09 Ops Incident, Failure, Queue, and Health Dashboard |
| 5 | Privacy and Cross-Cluster Contract Proof | 10 CL-09 Privacy, Retention, and Export Executors; 11 Cross-Cluster Integration Verification |
| 6 | Production Hardening | 12 CL-09 Security, Concurrency, Reconciliation, and Launch Hardening |

**Total numbered features: 12.**

---

## Phase Execution Pattern

Before each numbered feature:

1. Read required context.
2. Confirm the previous feature exit gate is green.
3. Check this build plan for Proposed Rulings/Unresolved Decisions that block the feature.
4. Write the concise feature implementation specification.
5. Confirm schemas, migration impact, public contracts, permissions, shared operations, events/jobs, and tests.
6. Implement only that feature.
7. Run typecheck, lint, unit tests, integration tests, schema validation, and build as applicable.
8. Perform the feature's workflow/E2E verification.
9. Update progress.
10. Update architecture only if a binding architecture decision legitimately changed.
11. Record assumptions, known failures, remaining risks, and deferred work.
12. Do not begin the next feature unless the current exit gate passes or the architecture owner explicitly records an accepted exception.

---

## Required Feature Specification

Immediately before implementation, each numbered feature receives a concise specification containing:

- **Objective**
- **Observable result**
- **Dependencies**
- **In scope**
- **Out of scope**
- **Owning Module**
- **Data records affected**
- **Schema/migration changes**
- **Public interfaces**
- **Shared operations consumed**
- **Permissions / Role / Authority actions**
- **Primary workflow**
- **UI/admin states if applicable**
- **Provider integrations**
- **Jobs/events/outbox/inbox behavior**
- **Idempotency/concurrency behavior**
- **Error/failure/partial-completion behavior**
- **Privacy/retention behavior where applicable**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**

Do not pre-write giant implementation specifications for all remaining features. The implementation specification is written for the **next** feature only, using current accepted architecture and the previous feature completion report.

---

## Required Completion Report

After every numbered feature, the coding agent must report:

- Feature completed
- Files added
- Files changed
- Database changes
- Migrations
- Dependencies added
- Shared operations reused
- Public interfaces added/changed
- Events/jobs added
- Provider adapters touched
- Tests added/changed
- Commands run
- Manual/workflow verification
- Authorization/RLS verification
- Privacy/compliance verification where applicable
- Documentation updated
- Architecture decisions accepted or changed
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Exit-gate result: **PASS / FAIL**

If the exit gate fails, the report must identify the exact failing condition and must not mark the next feature ready.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.


## WA-R018 — Durable execution, receipts and operational evidence

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R018 contract](../../reconciliation/platform-architecture-rulings.md#wa-r018--durable-execution-receipts-and-operational-evidence) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one platform-owned persistent command-idempotency/inbox/outbox/job mechanism with Postgres transactional persistence in the coordinated database pass. Module application/domain boundaries own effect semantics. A successful owner mutation atomically stores its domain change and outbox record; no transaction is held across provider/network calls. Consumers atomically claim a stable source event plus effect identity and commit their owner effect. Unknown outcomes reconcile before a new business attempt. Same scoped command key plus same canonical fingerprint replays the original result; different fingerprint conflicts. Owner/operation/subject scope is part of the key. At-least-once delivery is assumed; never promise global exactly-once execution.

Provider callbacks use verified provider/account/event identity, payload fingerprint, receipt state and separate effect/attempt state under the provider-owning Module (SH-059/060). A received/claimed record is not proof of completed effect. Duplicates preserve original proof; telemetry records observations. A retry of one semantic effect reuses its downstream idempotency identity. A genuinely new business attempt has a new identity linked to the prior result and cannot silently overwrite history. Booking workflow steps likewise carry a stable run/step/effect key. Exact tables/index names and runner library are implementation details; production runtime evaluation remains a scoped provider/operational gate, not a reason to build Module-local queues.

Adopt Ops-owned Postgres persistence for operational SystemEvent, IntegrationFailure and OpsIncident; QueueJob remains an operational projection of the platform runner, not a second executable queue. SystemEvent is append-only; correction references the original. IntegrationFailure separates occurrence identity from recovery observations; recording the same occurrence replays, another actual attempt creates another occurrence. Incident operator state is open/triaged/mitigated/resolved, with explicit authorized reopening recorded as a new transition; automatic grouping/alerts require versioned configured rules. Ops success/recovery cannot finish a business workflow. Tradeoff: durable local diagnostic queries require migrations/storage; provider dashboards remain secondary. Accept PR-CL09-05 persistence direction without claiming schema deployment or selecting retention periods.

Acceptance: concurrent identical/conflicting keys, crash after receipt and before effect, crash after domain commit and before dispatch, duplicate/out-of-order callback, lease recovery, retry exhaustion and reconciliation. Do not activate a consumer merely because a queue accepted its job.


## WA-R021 — Notification recipient and attempt model

**Applied architecture ruling (AI_RESOLVED_WITH_TRADEOFF), 2026-09-30.** The [WA-R021 contract](../../reconciliation/platform-architecture-rulings.md#wa-r021--notification-recipient-and-attempt-model) amends this document for the scoped concerns below. Earlier unresolved/proposed labels on those concerns are superseded; adjacent legal/product gates remain.

Use one logical Notification per resolved User recipient and semantic source intent; channels are deliveries of that notification. Organization is source/context, not an inbox principal. Hiring supplies the authorized recipient set and source-policy version; Notification expands/deduplicates User recipients and snapshots the resolved routing context. Revalidate current sensitive access before including protected payload or dereferencing context; a historical fan-out snapshot grants no future access. Source Modules own recipient eligibility and message meaning; Notification owns safe rendering, channel routing and provider mechanics.

Each delivery attempt has its own immutable attempt identity and correlation to logical notification, recipient, channel, destination generation and semantic send key. Retrying unknown provider outcomes reconciles before resending. Provider acceptance is not confirmed delivery or user interaction. Notification summary separately tracks pending/in-progress, partial success, all required routable deliveries successful, or exhausted failure; dismiss/read state remains independent and never alters source workflow status. The database pass must provide a representation for partial delivery rather than mapping it to total success. Policy may mark a channel optional; that requirement is snapshotted before dispatch, not rewritten to hide failure.

Persist dismissedAt/expiresAt when these actions/policies apply. User interaction is Notification-owned append-only evidence separate from Delivery receipts. Template versions are immutable and schema-validated; source supplies a registered semantic template intent plus allowlisted variables. Generic external channels carry minimal safe summaries/deep links, never raw message bodies, financial/tax documents, exact addresses or regulated data by default. Identity challenge-provider transport stays Identity-owned. Concrete provider selection/configuration and legally sufficient notice delivery remain external prerequisites.

Tradeoff: explicit parent/attempt representation needs schema alignment but avoids multiple inbox items per channel and false completion. Acceptance: organization fan-out dedupe, removed member sensitive access, duplicate send, partial channel failure, expiry/dismissal independence, callback before/after retry, unsupported channel and secret redaction.


## WA-R023 — Sensitive disclosure and audit failure boundaries

Class: **AI_RESOLVED_WITH_TRADEOFF**.

Require a durable sensitive-access audit acceptance before returning exact private location, protected file/playback/join credentials, resumes, healthcare-sensitive fields, tax/identity/Agreement evidence, or sensitive admin exports. If required proof cannot be durably recorded, withhold the protected response and return a retriable unavailable result; never return the secret and log later. Record safe allowed/denied/redacted/blocked/unavailable outcomes under Audit-owned vocabulary without importing Healthcare enums as generic authorization. Include service/system/provider actor attribution and request correlation, not nullable User alone. A denied request must still disclose no target-existence details; audit trouble never changes denial into access.

Privileged irreversible mutations require durable owner decision/history plus atomic audit-outbox intent before committing owner state. If that local durable write fails, roll back the mutation. Later Audit transport failure retries/reconciles; it does not roll back an already executed external financial/legal effect or erase domain evidence. Where a legal action specifically requires pre-action Audit acceptance, its owner contract adds that stricter gate; legal deadlines/recovery remain scoped requirements. Low-risk diagnostics are best effort and never recursively produce infinite failures.

Identity owns fresh action-bound assurance; Role still authorizes the action. Require step-up for security-factor/recovery changes, financial adjudication/movement, privileged permission changes, bulk sensitive evidence export and administrative override/release of protective controls. Existing sessions or admin roles do not substitute. Exact assurance methods/lifetimes and action registration are security implementation policy, with provider capability checked before activation. Ordinary read access is not automatically all step-up; owner-specific policy may require it. Privacy identity verification is a separate statutory proof requirement.

Tradeoff: protected access becomes dependent on durable audit availability; this is preferable to an unprovable sensitive disclosure. Acceptance: audit unavailable before response, durable intent failure before mutation, outbox delivery outage after commit, privileged service actor, retry without duplicate effect, denied-target anti-enumeration and redaction-safe evidence. These rules amend failure/assurance portions only; per-owner legal retention and complete target/action matrices remain separate work.

Duplicate-collapse scope: CL01-HU-006/007/008/012 security portions; CL02-D025/044/056; CL04-U032; CL-05-U007/062; CL-06-U048/055; CL-08-U16 and HU-09/19; CL-09-D016/030/031/032/035/043/046; CL-10-HU031/PR-CL10-09. Unnamed adjacent questions are not closed.

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

## WA-R037 — Payment effects, payout reservation and tax evidence

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

Payment owns immutable financial operation and attempt history, not just outbox delivery. Every effect has unique owner/sourceType/sourceId/sourceRevision/effectKind/effectOrdinal plus currency, semantic payload hash and original-effect reference for compensation. Reuse with different amount/subject/currency conflicts. Verified provider ingress receipt is separate from Payment and Track effect receipts; route by approved provider object/metadata ownership, never both owners applying the same business effect. Unknown routing is quarantined. Payment receipt fields: provider/account/eventId, eventType, fingerprint, handlerVersion, target operation, receivedAt, processing/attempt/recovery state and committed effect references. No raw secret payload by default; legal retention remains externally supplied.

Balance accounting uses immutable signed minor-unit effects with explicit bucket vectors and per-currency conservation. Earnings credit available (or pending until the approved availability rule); payout reservation moves available -A/reserved +A atomically with request acceptance; reservation release moves reserved -A/available +A only once after known cancellation/failure with no possible pending provider movement; successful payout moves reserved -A/paid +A. Transport retries have zero ledger effect. Provider return/reversal records its actual returned amount as a new linked effect, paid -R/available +R only after verified return and applicable financial restrictions; it never mutates the original payout. Fees/refunds/chargebacks are separate authorized signed effects, never hidden in payout status. Unknown money movement retains reservation and reconciles. Existing one-amount enum records are insufficient to infer these vectors: use an explicit owner allocation/bucket effect structure and forward constraints. This is accounting of processor-held value, not permission to introduce a wallet or new financial product.

At launch each PayoutTransfer belongs to one PayoutRequest; Order references are optional immutable allocation provenance, not a second transfer source. A request supplies an explicit validated active payoutAccountId; no guessed default among multiple accounts. Capture all blocking Hold IDs and decision versions in a separate immutable evaluation snapshot; blockedByHoldId is explanatory only. Reevaluate current holds/account/financial readiness immediately before dispatch. Keep one semantic transfer identity and stable provider idempotency key through network retries. Record each transport attempt separately. A terminal failed transfer never reopens; a new request/transfer after confirmed nonmovement and reservation release requires fresh authorization. Unknown is nonterminal even if transport timed out. No automatic retry of a terminal financially reversed/paid transfer.

Ratify the minimum Payment §9 graphs with these restrictions: KYC rejected/expired/disabled attempts are terminal; new attempt linked to previous evidence. TaxProfile rejected/expired creates a new collection revision, never overwrites submitted documents. One current applicable selector per subject+purpose+jurisdiction/provider scope points explicitly to the accepted evidence; pending new evidence does not silently replace valid current proof, while revocation immediately invalidates it. PayoutAccount disabled is terminal for that account; restriction recovery uses verified current provider evidence. PayoutRequest failed/cancelled/reversed terminal; processing cannot cancel without proven no movement. PayoutTransfer failed/cancelled/reversed terminal. SalesTaxCalculation changed quote requires a new calculation; finalized is immutable, voiding is a separately evidenced provider operation. Tax submission rejected/failed uses a new linked submission revision; transport retries of an unacknowledged submission retain semantic identity. Filed recipient correction creates replacement evidence and a link, preserving prior filing. No enum setter or provider callback bypasses these rules.

Tax subject is a Payment-owned stable subject reference mapped to an identified legal recipient, with explicit User and optional ProfessionalProfile provenance; profile identity is not automatically a separate legal taxpayer. Effective mappings/versioned evidence prevent accidental subject merge. Aggregate key is taxSubjectId + jurisdiction + taxYear + currency + reportingRegime; retain source owner/id/revision/recognition type and unique reversal identity. Prize-owned summaries use the same dimensions and preserve their own source valuation truth. SH-019 supports an explicit tax_fulfillment purpose and tax dimension; no second generic tax-readiness service is needed. Payment owns TaxReportingSubmissionStatus and TaxReportingRecipientStatus. Reporting bundle uniqueness includes regime/jurisdiction/year/currency/submission series/revision; recipients unique within submission by tax subject and applicable form/category. Rule versions, form requirements, recognition dates, thresholds and correction legality remain approved external configuration, never invented constants.

Order binds final calculation ID to exact immutable quote/order revision, currency, line IDs and buyer-tax-location evidence revision. Payment preserves line-level taxable basis, tax, jurisdiction, provider tax code and liability role even for mixed-liability lines. Tax-location provenance includes approved source owner, source/evidence revision, validation method/result and captured/effective time, minimum required location fields; it is not public-location consent. Each authorized refund has immutable line allocations against the original captured quantities/basis/tax and links its own provider refund and tax reversal attempts. Cumulative refunds cannot exceed captured refundable allocation; lock the operation allocation counters and reject mismatched currency. Use deterministic minor-unit residual allocation only within an approved tax/provider allocation policy; do not guess rates or liability. Partial/multiple refund representation requires separate child records, not one overwritten reversalId. Provider unsupported/ambiguous results stay pending/manual review, never fabricated successful tax reversal. Full provider/rule qualification remains external before affected execution.

Required verification: concurrent reservation conservation, duplicate callback/compensation, timeout followed by paid result, multiple holds, account changes before dispatch, line-level cumulative refund cap, subject/jurisdiction separation, replacement filing traceability. No live financial test or migration is claimed by this architecture decision.


## WA-R058 — Moderation execution receipts and review cycles

**Applied architecture ruling — 2026-10-08.** This scoped amendment supersedes earlier proposed/unresolved labels only for the concerns below. It records architecture, not implemented schema, successful tests, deployment or legal approval.

Moderation owns intake, case decisions, legal correspondence and immutable action history. A case aggregates reports through retained explicit links; report identity/history survives consolidation. Each action carries case/cycle, target owner/type/ID and version, authorized actor, policy version, requested effect, reason, evidence references and correlation/idempotency identity. SH-102 resolves only registered typed owner targets/actions. Missing, unavailable or unsupported targets remain unresolved intake; no actionable target or authorization is fabricated.

Before a destructive effect, preserve the authorized evidence snapshot or retained immutable content/reference/hash through Media under its access contract. A URL alone is not evidence. Preservation is purpose/retention constrained and must not copy restricted adjudication material into participant conversations (WA-R042/P19). Moderation records its action before dispatch; each owner executor returns acknowledged, completed, failed or restored evidence with effect identity, source version, retryability and receipt. Acknowledgment is not completion. Persist the run and steps; reconcile unknown outcomes before retry. Restoration is a new authorized owner effect linked to the original, never an edited historical action. Restrict cascades over decisions/actions/receipts; Privacy governs lawful retained-field disposition.

Report graph: submitted→triaged; triaged→under_review or dismissed; under_review→action_taken only after required owner receipts, or dismissed; action_taken/dismissed→closed. Duplicates retain their own triage evidence and link to the original report/case before dismissal. Ordinary closed reports are terminal; later evidence creates a linked review cycle without rewriting the original outcome. Case graph: opened→triaged→under_review; under_review→escalated or waiting_for_counter_notice only when applicable approved policy requires it; those waiting states return to under_review upon authorized new evidence. under_review→action_taken requires all required successful effects; under_review→dismissed records the no-action decision; action_taken/dismissed→closed. Authorized reopening of a closed case creates a new immutable cycle and resumes under_review, preserving earlier disposition. A reopened case never repeats prior enforcement automatically.

LegalNotice validation, counter-notice eligibility, deadline, restoration entitlement and mandatory correspondence remain externally approved legal policy. Store policy version and evidence with each allowed transition; unavailable policy prevents that legal mutation. This ruling supplies the execution protocol and ordinary Report/Case graphs, not numerical legal deadlines or permission to infer legal validity from notification, Search or Hold outcomes. Each target/action mapping must identify its actual owner executor and denial/unavailable behavior before activation; unsupported mappings fail closed.

Implementation sequence: specify owner storage/typed contract and forward migration; implement concurrency-safe owner commands; then wire consumers. Before activation verify replay, stale version, concurrent decisions, denied/unavailable dependencies, evidence retention, and failure/recovery fixtures. Exact physical names and executable tests remain implementation work. No cross-owner direct writes.


## WA-R059 — Hold provenance and safe release

**Applied architecture ruling — 2026-10-08.** This scoped amendment supersedes earlier proposed/unresolved labels only for the concerns below. It records architecture, not implemented schema, successful tests, deployment or legal approval.

Hold owns one validated typed primary target, immutable creation/review/release evidence, and the active→released lifecycle. A new justified stop after release/expiry is a new linked generation, never a historical status rewrite. Multiple sources may independently justify Holds: dedupe only equivalent source-owner + source-cause + typed target + action scope + reason-policy identity. Exact retry returns the same Hold; distinct causes remain separately evaluated. Retain durable reviewer claim/lease and expected revision so concurrent reviewers cannot silently overwrite decisions.

Register explicit action scopes and safe reason exposure with each target owner. A Hold decision returns applicability, opaque Hold/evidence identity and safe denial classification; it does not copy sensitive reasons to arbitrary consumers. Existing supported targets keep their established typed mapping; Candidate/Application/Resume or other absent targets require coordinated typed schema registration before activation. Their scope is only the registered action, never all activity or statutory rights. Foreign reason/status is source provenance, not an imported lifecycle.

Release requires fresh source-owner readiness evidence, current Hold policy/authority and expected active revision. Missing/unavailable source facts cannot release. Administrative authority alone never overrides legal/provider constraints. Expiry requires explicit approved policy, effective evidence and auditable owner transition; no generic timer default is introduced. Competing release/expiry attempts serialize and return the committed result or conflict. blockedByHoldId is a rebuildable association; every protected action evaluates all currently applicable Holds. Release emits a fact for owner reevaluation, never automatically fulfills a reward, releases money, completes service, restores content or grants review eligibility (WA-R042).

Implementation sequence: specify owner storage/typed contract and forward migration; implement concurrency-safe owner commands; then wire consumers. Before activation verify replay, stale version, concurrent decisions, denied/unavailable dependencies, evidence retention, and failure/recovery fixtures. Exact physical names and executable tests remain implementation work. No cross-owner direct writes.


## WA-R060 — Audit vocabulary and bounded operator evidence

**Applied architecture ruling — 2026-10-08.** This scoped amendment supersedes earlier proposed/unresolved labels only for the concerns below. It records architecture, not implemented schema, successful tests, deployment or legal approval.

Audit persists request/correlation identity, normalized outcome, typed actor kind (user/service/system/provider), owner-namespaced versioned action and typed target references, occurrence/recording time and minimal evidence references. Owners declare their vocabulary and classification; Audit validates declared namespace/shape and stores proof without querying another owner's repository or deciding its lifecycle. DataSensitivity meaning follows platform vocabulary; each owner supplies classification and Healthcare supplies its regulated interpretation. Exact enum/column names and forward backfill are implementation decisions.

Accept PR-AUD-02: unused hash/chain fields remain unpopulated; an append-only application contract is not a tamper-proof cryptographic chain. Any later chain requires a separately reviewed partition/sequence/canonicalization/algorithm/version/anchor/privacy contract. Do not manufacture hashes merely to satisfy nullable fields.

Ops and Admin viewers use bounded paginated Audit-owner queries before introducing a durable projection. Owner queries enforce current scope, redaction and mandatory access proof; unavailable mandatory proof fails closed under WA-R023. Register stable action IDs with Role; apply the established sensitive-action step-up rules to bulk sensitive exports, financial effects, drawing/reversal and protective-control release. No dashboard or diagnostic signal grants mutation authority. Ghost-account/inactivity signals are diagnostic; Identity alone owns account action, and there is no automatic deletion policy. Versioned grouping/alert/action registries and fixtures precede enablement. Preserve WA-R018 operational persistence/lifecycles; Ops recovery state cannot finish another owner's workflow.

Implementation sequence: specify owner storage/typed contract and forward migration; implement concurrency-safe owner commands; then wire consumers. Before activation verify replay, stale version, concurrent decisions, denied/unavailable dependencies, evidence retention, and failure/recovery fixtures. Exact physical names and executable tests remain implementation work. No cross-owner direct writes.


## WA-R067 — Typed moderation execution and normalized receipts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-103 remains the existing cross-cutting execution protocol; no new Shared Operation ID or schema change is authorized. Each instruction carries authorized decision/action ID, case/cycle, typed owner target ID and expected owner revision, approved effect, actor/service authority, purpose/policy/evidence references, semantic effect key and correlation. Owners validate target/action compatibility and current authority before mutation. The following versioned ports name existing owner handlers, not new lifecycle ownership or permission.

| Existing primary target / typed downstream effect | Owner port v1 | Allowed effect and guard |
| --- | --- | --- |
| job, organization | Hiring applyHiringModerationDecision.v1 | Publication suppression/eligible restoration under R047; compliance, lifecycle and all restrictions still apply |
| candidate_profile, with owned current search projection reference | Candidate applyCandidateModerationDecision.v1 | Search-projection suppression/eligible restoration only; current explicit opt-in/readiness required. No application mutation or new Candidate Hold target |
| thread, message | Messaging applyMessagingModerationDecision.v1 | Persistent content restriction/authorized restoration under R054; current membership, sensitivity and all restriction sources still apply |
| media_asset, media_access_grant | Media executeMediaModerationInstruction.v1 | Existing asset freeze, public exposure/grant revocation, evidence preservation and eligible file exposure restoration; source context and safety remain required |
| digital_download_asset, affected owned grant references | Digital Goods applyDigitalModerationDecision.v1 | Disable/restore asset and revoke affected grants; current Order entitlement/Media safety/purchased policy required, no revival of terminal grant |
| course_video_asset, affected owned playback grant references | Video applyVideoModerationDecision.v1 | Disable/restore asset and revoke affected playback grants; current entitlement/safety/provider evidence required |
| review | Review applyReviewModerationDecision.v1 | Existing hide/remove/authorized restoration under R026; restore current eligible accepted revision and adjust original reputation contribution exactly once |
| offering | Marketplace applyOfferingModerationDecision.v1 | Valid moderation restriction/clearance under R035; clearance returns to draft, fresh publish remains separate |

Existing unversioned Media/Digital/Video handler names become aliases of their listed v1 contract and must not create duplicate effects. CandidateSearchProjection, DigitalDownloadGrant and playback-grant references are owner-local downstream effects under existing primary targets, not new ModerationTargetType values. The owner validates their parent/target relationship. Each port returns semantic effect key, source decision/action, target/revision, effect state, safe outcome/retry classification and durable receipt identity. No secret/provider payload or private evidence is returned.

| Local result | Canonical effect state | Required semantics |
| --- | --- | --- |
| accepted/queued | acknowledged | Durable acceptance only; mutation/provider effect not yet proved |
| applied | completed | Exact requested effect durable, resulting owner revision and proof retained |
| restoration applied | restored | New authorized linked restoration completed; original restriction/history untouched |
| already-applied | Original receipt state | Replay exact stored receipt, including pending state; dedupe alone is not completion |
| unsupported/denied/stale conflict | failed with terminal or reevaluate classification | No mutation; conflict requires fresh facts and applicable authorized decision, never silent overwrite |
| known retryable failure | failed with retryable classification | Retry the same semantic effect identity |
| uncertain owner/provider outcome | acknowledged with reconcile_required outcome | Durable unknown-state evidence; reconcile original effect before redispatch, never claim completed/restored |

Multi-owner work retains per-step receipts; Report/Case action_taken requires every required successful effect under R058. Search refresh and provider request acknowledgments do not prove de-indexing or revocation. Restoration is a new effect linked to the original, not an edit of the original receipt. Partial bulk revocation remains incomplete until its target inventory is accounted.

Order/payout reusable stops use Hold's registered typed action/command boundary per CL-09-R007/R059, not direct Moderation writes to Order/Payment. Release triggers current owner reevaluation, never financial execution, content restoration, service completion or review eligibility. Candidate Hold types absent from the typed Hold schema remain disabled. CL-01 has no generic moderation executor under R063: only separately named authorized security/entitlement/Hold/lifecycle commands may act. Enumeration of user or profile targets is not permission. Other target/effect families not listed here must have an existing explicit owner registration before activation; this scoped matrix does not invent their semantics or silently delete their historical proposals. Unsupported combinations return unsupported, with no fallback mutation.

R026 already settles explicitly authorized Review restoration; old unresolved base text is superseded. R042 settles Booking Professional reports, authorized support adjudication and Customer contest, with no automatic consequence; R052 completed/no_show aliases are performance-report facts, not final financial/review truth. These are existing rulings, not new product decisions. Contract adapters/fixtures, typed receipt persistence and coordinated migrations remain implementation qualification.

## WA-R081–083 — Integrated bridge sequence

Follow Module owner contracts and the complete bridge inventory before cross-Cluster integration. CONTRACT_ONLY work may establish schemas/fakes; FOUNDATION_CAPABILITY is required before actual effects; executable bilateral and external evidence precede freeze/activation. R081 named queries/receipts, R082 Media invalidation, and R083 disabled optional paths supersede only the corresponding historical open labels. Keep current source checks at action/disclosure boundaries. Do not begin whole-Cluster parallel work, root synthesis or runtime implementation from source-coverage counts alone.


## WA-R085–087 — Platform convergence

Current platform reconciliation covers `admin_review_compliance_hold`, `audit_event_ledger`, `content_moderation_legal_notice`, `observability_ops`. Module owners retain all lifecycles and source facts. R085 separates terminating fact inputs from composed permissions, readiness, credential issuance and Hold release; R086 locates one shared execution capability and bootstrap dependencies; R087 routes Organization commercial schema responsibility to Track without enabling monetized ATS.

Coordinate required ports and semantic fixtures before actual adapters; do not require complete upstream Clusters from a contract edge. Source commits precede outbox delivery and downstream projection/Notification/provider setup. Recovery reuses stable effect identity and cannot infer completion from acknowledgment, telemetry or a read model. The platform dependency graph records typed edges and critical cycle dispositions; action-specific external gates remain scoped.

Root architecture synthesis is conditional on the recorded Gate 5 exit and Gate 6 posture confirmation. A root build plan, runtime choice, database migration, interface freeze and parallel implementation lanes remain later prerequisites. No such implementation approval is made by this coordination appendix.
