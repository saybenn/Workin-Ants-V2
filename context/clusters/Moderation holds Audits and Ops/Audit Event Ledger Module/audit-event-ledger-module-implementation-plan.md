# Audit / Event Ledger Module Implementation Plan

## Document Header

| Item | Value |
| --- | --- |
| Module ID | `audit_event_ledger` |
| Module name | Audit / Event Ledger Module |
| Primary Cluster | `CL-09 Moderation, Holds, Audit & Ops` |
| Plan status | Implementation-grade Module plan |
| Parent architecture | `audit_event_ledger/module-architecture.md` |
| Cluster sequencing authority | CL-09 `build-plan.md` |
| Build posture | Narrow, evidence-first implementation; no neighboring lifecycle ownership |
| Current build status | `mvp_active` |

This plan is subordinate to the root Workin Ants architecture, code standards, Canonical Shared Operations Architecture, CL-09 architecture, and CL-09 build plan. It does not independently change Cluster sequencing, source-of-truth ownership, legal policy, or shared-operation ownership.

---

## Core Principle

Implement Audit / Event Ledger through narrow, verifiable slices:

```text
public / observable behavior
  -> validated command or query
  -> Audit-owned evidence policy
  -> authoritative Audit write/read
  -> canonical shared-operation calls
  -> bounded downstream effect, if any
  -> tests
  -> exit gate
```

The Module has no general end-user workflow. Its observable outputs are:

- stable internal/public Module commands;
- append-only `AuditEvent` evidence;
- append-only `AccessAuditLog` evidence;
- protected redacted query interfaces;
- the Audit-owned portion of the CL-09 admin review surface;
- Privacy-owned workflow executor results;
- cross-Module contract proof;
- optional integrity verification only after explicit architecture approval.

No feature in this plan may use Audit evidence to replace the business or compliance truth that caused the evidence.

---

## Build Rules

1. Follow root and CL-09 architecture before this plan.
2. This Module owns only `AuditEvent`, `AccessAuditLog`, `AccessAuditAction`, and Audit-specific evidence/query/privacy policy.
3. Do not create `AuditEventType` or `AuditEventActor` until `U-16` is explicitly resolved.
4. Do not finalize the canonical `appendAuditEvent` storage contract until `U-17` is explicitly resolved.
5. Do not implement or claim hash-chain integrity until `PR-CL09-07` / `U-18` are explicitly resolved.
6. Do not implement production Privacy retention/anonymization behavior until `U-24` is explicitly resolved.
7. Consume authenticated actor context through Identity & Access.
8. Consume permission decisions through Role / Authority.
9. Consume request/correlation context, structured logging, exception capture, and generic operational failure visibility through Observability/platform capabilities.
10. Consume shared metadata-sanitization mechanics; keep Audit action-specific allowlists and limits local.
11. Consume target facts through target-owner interfaces when validation is required. Never build a universal foreign Prisma repository.
12. Do not add generic domain-event, provider-event, operational-failure, privacy-request, search, media, or notification tables to this Module.
13. Mutations are schema validated, internal/trusted, and transaction-safe.
14. Normal application and admin roles must be unable to update or delete Audit evidence at both repository and database-policy boundaries.
15. Distinct legitimate sensitive accesses remain distinct records. Idempotency is used only when a source-defined semantic identity proves a retry is the same fact.
16. External effects use canonical shared operations. Audit owns no provider adapter.
17. Any background work uses the shared queue/retry/telemetry infrastructure.
18. Every feature ends with automated tests and an explicit exit gate.
19. Unresolved architecture is surfaced rather than filled in by coding convention.
20. A failed cross-Module contract is corrected at the owner/interface boundary; it is never patched with a direct foreign database write.
21. Raw Prisma records do not cross the Module's public boundary.
22. Audit payloads are minimized; JSON fields are not an escape hatch for protected source payloads.
23. Build progress may record implementation state but must not silently redefine architecture.

---

## Preconditions

### Hard platform prerequisites

These must exist, or be implemented as accepted platform foundations before the corresponding Module feature can exit:

- PostgreSQL/Prisma foundation and migration workflow;
- server-only application execution boundary;
- authenticated actor interface: `resolveAuthenticatedActor`;
- Role / Authority interface: `authorizeResourceAction`;
- request/correlation interface: `createRequestContext`;
- metadata sanitization mechanism: `sanitizeTelemetryMetadata`;
- canonical structured logging/error boundary;
- testable database permission/RLS/grant mechanism appropriate to root standards;
- canonical idempotency primitive for any source command that requires replay protection.

### Hard architecture decisions by feature

| Decision | Required before |
| --- | --- |
| `U-16` — `AuditEventType` / `AuditEventActor` conflict | Feature 01 exit if the implementation changes current free-form type/actor representation. At minimum, the conflict must be formally resolved as "keep current representation for MVP" or an approved migration. |
| `U-17` — `AuditEvent` request ID/outcome storage | Feature 01 exit and therefore all `appendAuditEvent` implementation. |
| `U-24` — Audit Privacy target vocabulary and retention policy | Feature 07 production exit. Contract scaffolding may precede it; destructive/anonymizing behavior may not. |
| `PR-CL09-07` / `U-18` — Audit hash chaining | Only the optional integrity branch in Feature 09. Baseline production hardening does not require hash chaining if it remains unaccepted and no launch claim depends on it. |

### Direct Module interfaces that may initially be stubbed

Contract fakes are acceptable before the Module Integration Phase for:

- source-owner target validation;
- Healthcare access-result provider;
- Payment/financial access-result provider;
- Candidate/Resume access-result provider;
- Media access-result provider;
- Transaction/Agreement access-result provider;
- Booking/Calendar access-result provider;
- Messaging access-result provider;
- Location Safety access-result provider;
- Privacy orchestration.

The fakes must match the approved public interface shape. They must not become permanent shadow implementations.

### Cluster prerequisites

Audit's source-record foundation is the first CL-09 evidence spine and should not wait for Moderation, Hold, or Observability admin screens.

However:

- Feature 06 must align with CL-09 Feature 08;
- Feature 07 must align with CL-09 Feature 10;
- Feature 08 must align with CL-09 Feature 11;
- Feature 09 must align with CL-09 Feature 12.

The Module plan cannot pull those Cluster milestones earlier.

---

## Architecture Decision Gates

Before beginning a feature, check the following table. A blocked decision is not resolved by choosing the easiest implementation.

| Gate | Status at plan creation | Required behavior |
| --- | --- | --- |
| `U-16` Audit event type/actor representation | Unresolved | Do not create absent enums/schema without explicit ruling. |
| `U-17` Audit request ID/outcome storage | Unresolved | Feature 01 must obtain/record the decision before final command/schema implementation. |
| `U-18` / `PR-CL09-07` hash chaining | Proposed/unresolved | Keep integrity branch disabled unless explicitly accepted. |
| `U-24` privacy target/retention rules | Unresolved | Feature 07 may build contracts/tests with non-destructive fixtures, but production disposition must remain blocked until policy is approved. |
| Audit-specific step-up matrix | Unresolved | Use step-up only for actions explicitly designated by Identity/Security policy. |
| Audit evidence export manifest | Unresolved | Do not add a new export source record merely for convenience. |
| Generic non-healthcare access-decision persistence | Unresolved | Do not widen `HealthcareAccessDecision?` into a generic decision enum without architecture review. |
| Ghost-account cleanup policy | Unresolved | No account deletion/suspension workflow in this Module. |

---

# IMPLEMENTATION PHASES

## Phase 1 — Contracts and Source-of-Truth Foundation

This phase implements the exact Audit storage and safety boundary needed by CL-09 Feature 01 before application commands depend on it.

---

### 01 Audit Contract and Schema Alignment

#### Objective

Resolve the current Audit schema/contract conflicts and establish stable typed contracts for generic audit evidence and sensitive-access evidence without inventing new ownership.

#### Observable Result

- The repository has explicit typed request/receipt/view contracts for `appendAuditEvent`, `recordSensitiveAccess`, `queryAuditEvents`, and `querySensitiveAccessHistory`.
- The `U-16` conflict is explicitly resolved or intentionally preserved with a documented MVP representation.
- The `U-17` request-ID/outcome storage decision is explicitly resolved and represented in Prisma or an approved normalized representation.
- Schema validation/migration checks pass.
- No unapproved `AuditEventType` or `AuditEventActor` schema appears.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 1, Feature 01 — Audit Evidence and Request Correlation**.

This feature must not advance CL-09 Feature 01 beyond the Cluster's architecture-decision gates.

#### Dependencies

- current Prisma schema and migration history;
- Canonical Shared Operations Architecture;
- `createRequestContext` contract;
- root naming/error/validation conventions;
- explicit architecture resolution for `U-17`;
- explicit ruling for `U-16` if schema/type changes are proposed.

#### In Scope

- inspect current `AuditEvent`, `AccessAuditLog`, `AccessAuditAction`, `DataSensitivity`, and `HealthcareAccessDecision`;
- define stable command DTOs and receipts;
- define redacted query-view DTOs at the contract layer;
- resolve/document how `appendAuditEvent` stores request ID and outcome;
- add only the approved schema/migration changes required by that decision;
- verify/adjust indexes required by the approved correlation/filter contract;
- document actor representation under current nullable `actorUserId`;
- add schema-level tests/fixtures for current enum values.

#### Out of Scope

- repository append implementation;
- DB insert-only policy;
- admin UI;
- Privacy disposition;
- hash chaining;
- provider clients;
- domain-event ledgers;
- generic operational records;
- ghost-account logic.

#### Module-Owned Data

Potentially affected:

- `AuditEvent`;
- `AccessAuditLog`;
- `AccessAuditAction`.

Consumed only:

- `DataSensitivity`;
- `HealthcareAccessDecision`.

`AuditEventType` and `AuditEventActor` are not added unless the explicit `U-16` ruling says to do so.

#### Public Interfaces

Define, but do not yet fully wire, the stable contracts:

```text
appendAuditEvent(command) -> AuditEventReceipt
recordSensitiveAccess(command) -> AccessAuditReceipt
queryAuditEvents(filters, viewer) -> Page<AuditEventView>
querySensitiveAccessHistory(filters, viewer) -> Page<AccessAuditView>
```

At minimum, receipts contain:

- evidence ID;
- created-at timestamp;
- correlation/request reference when part of the approved contract.

No public type exports a raw Prisma row.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `createRequestContext` | Observability/platform | Contract alignment for request/correlation field semantics. | Whether/how Audit persists safe correlation reference. | `auditRequestId` helper or alternate correlation vocabulary. |
| `sanitizeTelemetryMetadata` | Observability / Ops + Audit payload policy | Define accepted metadata input/result type. | Audit action-specific allowlists/size limits are defined in later implementation. | Custom generic sanitizer contract. |
| `resolveAuthenticatedActor` | Identity & Access | Align actor DTO/reference semantics. | Which actor fields may be persisted. | `AuditActor` identity subsystem. |

#### Domain Logic

- `AuditEvent` represents generic action proof only.
- `AccessAuditLog` represents generic protected-access proof only.
- `AccessAuditAction` is Audit-owned vocabulary.
- `DataSensitivity` and `HealthcareAccessDecision` are consumed vocabulary, not Audit policy.
- Actor, action, target, request, and outcome fields must be explicit enough that callers do not hide canonical data in opaque metadata unless that is the approved `U-17` decision.
- Public command types must separate required fields from optional metadata.
- Contract naming uses canonical operation names, not aliases.

#### Authorization / Compliance

No public endpoint is introduced here.

Contracts must make room for:

- trusted internal caller context;
- source-owner access outcome;
- Role / Authority viewer context;
- step-up result where later required.

Contract types must not imply that Audit itself grants sensitive access.

#### Database / Transaction Behavior

- inspect existing constraints and indexes;
- create only approved migration(s) needed for `U-17`/`U-16`;
- no destructive migration without explicit review;
- no backfill guesses for existing metadata;
- if request ID/outcome become first-class fields, define nullability/backfill/compatibility explicitly;
- use schema validation and migration dry-run against a representative database.

#### Events / Jobs

None.

Do not publish a domain event merely because a contract was defined.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- unresolved `U-17` -> feature cannot pass;
- proposed schema change without explicit ruling -> stop and record architecture blocker;
- migration conflict -> fail feature; do not silently rename/map current fields;
- DTO incompatible with canonical shared operation -> correct contract before proceeding.

#### Tests

- Prisma/schema validation;
- type-level contract compilation;
- request/receipt serialization fixtures;
- enum snapshot test for `AccessAuditAction`;
- migration forward test;
- rollback or forward-fix plan review for any migration;
- test proving raw Prisma row types are not the public contract.

#### Documentation Updates

Update:

- this Module architecture if `U-16` or `U-17` becomes binding;
- Cluster architecture unresolved-decision register if applicable;
- canonical interface documentation only if the approved shared-operation contract itself changes;
- progress tracker.

#### Acceptance Criteria

1. `U-17` is explicitly decided and reflected in the contract/storage design.
2. `U-16` is explicitly resolved or preserved as a documented no-schema-change ruling.
3. Public DTO names use canonical operation names.
4. No unapproved Audit-owned enum/model has been invented.
5. The current owned/consumed enum boundary is explicit in code types.
6. Schema and migration checks pass.
7. No neighboring truth is added to Audit tables.

#### Exit Gate

Feature 01 passes only when:

- the architecture decisions required for the chosen schema are recorded;
- Prisma validates;
- migrations are reviewed and tested if present;
- typed public contracts compile;
- the `AuditEvent` request/correlation/outcome representation is unambiguous;
- `AuditEventType` / `AuditEventActor` are not silently invented;
- typecheck, lint, contract tests, and schema checks pass.

---

### 02 Insert-Only Storage and Audit Payload Policy

#### Objective

Create the protected Audit-owned persistence boundary so `AuditEvent` and `AccessAuditLog` can be inserted and queried without exposing normal update/delete paths or accepting unsafe metadata.

#### Observable Result

- Trusted server code can append each Audit-owned record through an internal repository.
- Normal app/admin roles cannot update or delete either evidence model.
- Unsafe, oversized, or prohibited metadata is rejected before persistence.
- Repository APIs expose insert and bounded reads only.
- Database tests prove insert-only enforcement rather than relying on TypeScript convention.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 1, Feature 01 — Audit Evidence and Request Correlation**.

#### Dependencies

- Module Feature 01;
- approved root database/RLS/grant pattern;
- `sanitizeTelemetryMetadata`;
- structured logger/test environment;
- current migrations.

#### In Scope

- `AuditEvent` insert repository;
- `AccessAuditLog` insert repository;
- bounded owner-table read methods needed by later queries;
- no ordinary update/delete repository methods;
- database role/RLS/grant/trigger enforcement according to root standards;
- Audit-specific metadata allowlists;
- prohibited-key/classes rules;
- safe JSON serialization;
- size limits;
- action/sensitivity compatibility validation primitives;
- test-only privileged setup that does not leak into normal app API.

#### Out of Scope

- public command orchestration;
- source-owner authorization;
- admin UI;
- Privacy mutation path;
- hash chain;
- operational failure tables;
- provider integrations.

#### Module-Owned Data

- `AuditEvent`;
- `AccessAuditLog`;
- `AccessAuditAction`.

#### Public Interfaces

No new public Module interface beyond the contracts from Feature 01.

Internal repository interfaces must be narrower than Prisma:

```text
insertAuditEvent(validatedRecord)
insertAccessAuditLog(validatedRecord)
findAuditEvents(boundedFilters)
findAccessAuditLogs(boundedFilters)
```

No generic `save`, `update`, `delete`, `upsert`, or arbitrary raw-query public repository method.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `sanitizeTelemetryMetadata` | Observability / Ops + Audit payload policy | Before any JSON evidence is accepted. | Allowed keys, maximum depth/size, action-specific fields. | `redactAuditJson`, `safeAuditJson`, duplicate global serializer. |
| `writeStructuredLog` | Observability / Ops | Repository/validation failures with safe dimensions. | No raw evidence metadata in logs. | Audit-specific logger. |
| `captureException` | Observability / Ops | Unexpected persistence failure boundary. | Safe operation/evidence type only. | Direct Sentry setup. |

#### Domain Logic

Prohibited payload classes include:

- PHI payloads;
- raw resumes;
- private message bodies;
- card/payment credentials;
- OTPs;
- passwords/secrets;
- raw biometrics;
- raw identity documents;
- full agreements/contracts/PDF content.

Permitted data is reference-oriented and minimized.

`AccessAuditAction` validation must:

- accept only canonical enum values;
- ensure action-specific required fields are present;
- avoid claiming owner policy not supplied by the caller.

#### Authorization / Compliance

- repository is server-only;
- application/admin database roles cannot update/delete evidence;
- direct client writes are prohibited;
- test fixtures prove prohibited mutation failure.

#### Database / Transaction Behavior

- evidence insert occurs in a single database transaction;
- server-generated `createdAt` is authoritative;
- no update/delete method is exposed;
- indexes from Prisma are verified;
- any database policy migration is reversible or has a forward-fix plan;
- privileged maintenance/privacy paths, if required later, are separate from the normal repository role.

#### Events / Jobs

None.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- unsafe metadata -> deterministic `metadata_rejected`;
- invalid enum/action/sensitivity shape -> validation error;
- DB permission misconfiguration -> integration test fails feature;
- persistence unavailable -> return typed technical failure to caller; do not pretend evidence exists.

#### Tests

- unit: prohibited keys and payload fixtures;
- unit: size/depth limits;
- unit: action/sensitivity compatibility;
- integration: successful inserts;
- integration: update denied for app role;
- integration: delete denied for app role;
- integration: update/delete denied for admin role;
- integration: repository exposes no ordinary mutation API;
- security: raw metadata does not appear in logs;
- migration/policy test.

#### Documentation Updates

- document exact DB insert-only enforcement mechanism in Module architecture if it becomes binding;
- update progress tracker;
- document any approved payload limits/allowlists that become stable policy.

#### Acceptance Criteria

1. Normal app/admin roles cannot update/delete Audit evidence.
2. Trusted server insert succeeds.
3. Unsafe metadata fixtures are rejected before persistence.
4. No raw foreign payload is required to create valid evidence.
5. Repositories cannot mutate neighboring Module truth.
6. Operational logs are sanitized.
7. All DB and security tests pass.

#### Exit Gate

Feature 02 passes only when insert-only enforcement is proven at the database and application boundaries, payload-policy tests pass, and no normal update/delete path exists.

---

## Phase 2 — Core Public Audit Capabilities

This phase exposes the stable Module operations that other Workin Ants Modules use instead of creating their own generic audit systems.

---

### 03 Generic Audit Append Command

#### Objective

Implement `appendAuditEvent` as the canonical trusted server command for generic important-action proof.

#### Observable Result

A consuming Module can submit a valid generic action fact and receive an `AuditEventReceipt` containing durable evidence identity and timestamp/correlation information according to Feature 01's approved contract.

#### Cluster Build-Plan Link

Completes a major portion of **CL-09 Phase 1, Feature 01**.

#### Dependencies

- Module Features 01–02;
- `resolveAuthenticatedActor` for user-driven contexts;
- `createRequestContext`;
- `sanitizeTelemetryMetadata`;
- optional `validateOwnedTargetReference` where the target contract requires existence;
- optional `executeIdempotentCommand` for source-defined replay identity.

#### In Scope

- application command handler;
- schema validation;
- actor/system context mapping;
- target/entity reference validation;
- outcome/request context mapping per approved `U-17`;
- metadata policy application;
- insert through Audit repository;
- typed receipt;
- safe operational telemetry;
- caller-controlled criticality/recovery contract only if root/Cluster standards define it.

#### Out of Scope

- protected data-access evidence;
- domain lifecycle updates;
- direct target-owner mutations;
- provider webhook processing;
- notification delivery;
- auto-publishing an event for every Audit append;
- generic audit deduplication.

#### Module-Owned Data

Writes:

- `AuditEvent`.

No neighboring record is written.

#### Public Interfaces

```text
appendAuditEvent(command) -> AuditEventReceipt
```

The command must expose canonical fields rather than require callers to place actor/action/target/outcome/request ID inside metadata.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity & Access | At user-originated command context before append. | Which resolved actor attributes are persisted. | Audit current-user helper. |
| `createRequestContext` | Observability/platform | At source request/job boundary; Audit consumes propagated context. | Safe correlation persistence. | Per-Audit request ID generator. |
| `sanitizeTelemetryMetadata` | Observability / Ops + Audit policy | Before persistence. | AuditEvent action-specific metadata allowlist. | Local generic redactor. |
| `validateOwnedTargetReference` | Target owner | Only when command semantics require target existence/eligibility proof. | Which Audit actions require validation. | Cross-domain target repository. |
| `executeIdempotentCommand` | Platform application infra | Only when source supplies semantic retry identity. | Retry equivalence and conflict behavior. | Audit processed-command table. |
| `writeStructuredLog` / `captureException` | Observability / Ops | Safe execution diagnostics. | No raw metadata. | Audit logger/Sentry. |

#### Domain Logic

1. Verify trusted internal caller context.
2. Validate action and entity/target namespace.
3. Resolve/attach user actor or approved system context.
4. Consume request context.
5. Validate target through owner interface if required by the action.
6. Sanitize/minimize metadata.
7. Apply source-defined idempotency only when explicitly supplied.
8. Insert one `AuditEvent`.
9. Return receipt.
10. Do not change source state.

#### Authorization / Compliance

- public browser clients cannot submit arbitrary audit actions;
- the source Module has already authorized the underlying business action;
- Audit does not re-authorize that business action;
- Audit may validate that the internal caller is permitted to invoke the capability under root service boundaries.

#### Database / Transaction Behavior

- one insert transaction;
- server timestamp;
- source-defined idempotency claim and append must be transactionally coordinated when used;
- no `upsert` that can mutate an existing evidence row;
- no merge-on-duplicate behavior.

#### Events / Jobs

No domain event required.

If Audit persistence fails during a source workflow that requires proof, the source owner decides whether to fail closed or route recovery under its approved policy.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- invalid action/target -> validation error;
- unsafe metadata -> `metadata_rejected`;
- target required but unavailable -> `target_unavailable`;
- idempotency conflict -> `conflict`;
- DB unavailable -> `persistence_unavailable`;
- source criticality requires fail closed -> caller must not report success without evidence receipt.

#### Tests

- unit command validation;
- unit metadata policy;
- contract receipt;
- integration insert;
- integration system actor / user actor cases;
- idempotency replay fixture;
- test proving two distinct facts can coexist;
- target-owner contract fake;
- technical failure propagation;
- no domain table mutation assertion.

#### Documentation Updates

- public interface section if command DTO/result changes;
- progress tracker;
- integration guide/examples for calling Modules.

#### Acceptance Criteria

1. Valid command creates one durable `AuditEvent`.
2. Receipt contains approved evidence/correlation fields.
3. Invalid/unsafe payloads are rejected.
4. The command does not update target/source truth.
5. Canonical idempotency is optional and semantic, not blanket dedupe.
6. No Audit event is recursively produced about the append itself.
7. All contract/integration/security tests pass.

#### Exit Gate

Feature 03 passes when at least two representative consumer contract tests can append generic evidence through the public command without direct Prisma access or duplicate helper services.

---

### 04 Sensitive Access Evidence Command

#### Objective

Implement `recordSensitiveAccess` as the canonical cross-platform command for protected-access proof while preserving source-owner authorization and domain-specific access records.

#### Observable Result

A source Module can record an allowed, denied, blocked, redacted, viewed, downloaded, credential-issued, financial, contract, digital, media, calendar, or other canonical sensitive-access action and receive an `AccessAuditReceipt`.

#### Cluster Build-Plan Link

Completes the core mutation portion of **CL-09 Phase 1, Feature 01** and establishes the rail required by later CL-09/admin/cross-cluster features.

#### Dependencies

- Module Features 01–03;
- current `AccessAuditAction`;
- current `DataSensitivity`;
- current `HealthcareAccessDecision`;
- `createRequestContext`;
- `sanitizeTelemetryMetadata`;
- source-owner access decision contract/fake.

#### In Scope

- application command;
- target/action/sensitivity validation;
- source-owner outcome requirement;
- request/correlation capture;
- IP hash/user-agent handling according to approved request-context policy;
- append repository;
- receipt;
- safe operational failure handling;
- explicit coexistence with domain-specific access proof.

#### Out of Scope

- deciding authorization;
- healthcare access policy;
- financial readiness;
- resume authorization;
- Media grant generation;
- contract access grant;
- video token creation;
- location reveal decision;
- provider status;
- new generic access-decision enum;
- hash chaining.

#### Module-Owned Data

Writes:

- `AccessAuditLog`.

Uses canonical Audit enum:

- `AccessAuditAction`.

Consumes:

- `DataSensitivity`;
- `HealthcareAccessDecision`.

#### Public Interfaces

```text
recordSensitiveAccess(command) -> AccessAuditReceipt
```

The command must require the source owner to supply enough information to state what happened. It must not query raw provider or neighboring-domain state to reconstruct the outcome.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Identity & Access | Where a user actor is involved. | Persist only approved actor reference. | Caller-specific audit actor helpers. |
| `createRequestContext` | Observability/platform | Correlate access to request/job. | Request ID is evidence, not dedupe key. | Local correlation generator. |
| `sanitizeTelemetryMetadata` | Observability / Ops + Audit policy | Before append. | Action/sensitivity-specific safe fields. | Finance/PHI/resume-specific generic redactors. |
| `executeIdempotentCommand` | Platform app infra | Only for a technical retry of the same evidence append. | Preserve distinct real accesses. | Global access-dedupe table. |
| `writeStructuredLog` / `captureException` | Observability / Ops | Diagnostics. | No protected payload in logs. | Audit-local logger/Sentry. |

#### Domain Logic

1. Source owner decides whether requested access/action is allowed, denied, redacted, blocked, or otherwise completed.
2. Source owner creates its domain-specific access record where that domain requires one.
3. Source owner calls `recordSensitiveAccess`.
4. Audit validates:
   - actor/system context;
   - target type/ID;
   - canonical `AccessAuditAction`;
   - sensitivity;
   - access decision where applicable;
   - request context;
   - safe metadata.
5. Audit appends one `AccessAuditLog`.
6. Audit returns receipt.

Examples of separate truth:

```text
ResumeAccessLog        + AccessAuditLog
MediaAccessEvent       + AccessAuditLog
DigitalDownloadEvent   + AccessAuditLog
AgreementEvent/access  + AccessAuditLog
LocationReveal         + AccessAuditLog
UserSecurityEvent      + AccessAuditLog
```

The plus sign means “both may be required,” not “duplicate ownership.”

#### Authorization / Compliance

- caller must be trusted internal code;
- data/context owner authorizes the protected access;
- `recordSensitiveAccess` never grants access;
- healthcare `accessDecision` is recorded only when Healthcare supplies it;
- financial reads use `DataSensitivity.financial`;
- resume reads use `DataSensitivity.resume`;
- contract reads use `DataSensitivity.legal_contract`;
- private-message access uses `DataSensitivity.private_message` as applicable;
- no raw protected payload is accepted.

#### Database / Transaction Behavior

- each real access attempt is append-only;
- `requestId` does not impose uniqueness;
- no update/delete;
- idempotency is source-defined for retry only;
- hashes remain null/uninterpreted unless the integrity architecture is later approved.

#### Events / Jobs

None.

#### Provider Integration

None. Token/grant/provider actions are performed by the provider-owning Module before/around this proof append.

#### UI / Admin Surface

None.

#### Failure Behavior

- unsupported action -> validation error;
- missing required source-owner outcome -> validation error;
- protected payload present -> `metadata_rejected`;
- persistence failure in legally/security-required path -> caller must follow its approved fail-closed/recovery policy;
- legitimate repeat action must not be treated as duplicate.

#### Tests

- unit for every action category at least once;
- enum snapshot/contract;
- sensitivity mapping fixtures;
- Healthcare allowed/redacted/blocked/denied fixtures without PHI;
- financial fixture without financial payload;
- resume fixture without raw resume text;
- agreement fixture without contract body;
- repeated-access test proving two rows;
- retry test proving only explicit semantic replay is suppressed;
- DB insert/query test;
- no foreign mutations.

#### Documentation Updates

- action usage guidance;
- Module public interface docs;
- progress tracker;
- architecture only if enum/decision semantics become binding changes.

#### Acceptance Criteria

1. Source-owner outcome is required where action semantics imply a decision.
2. A valid access creates one `AccessAuditLog`.
3. Distinct repeated access creates distinct evidence.
4. No source access policy is implemented inside Audit.
5. No prohibited content is persisted.
6. Domain-specific access records remain separate.
7. Tests cover healthcare, financial, resume, media/digital, and agreement categories.

#### Exit Gate

Feature 04 passes when representative source owners can call the canonical command and tests prove Audit is recording—not deciding—the protected access.

---

### 05 Protected Evidence Queries and Request Correlation

#### Objective

Expose bounded, authorized, redacted Audit evidence queries so admin/compliance tooling and approved internal consumers can inspect proof without direct Prisma access.

#### Observable Result

Authorized callers can filter and page generic Audit and sensitive-access evidence by supported fields, including request/correlation references where available, while unauthorized callers receive safe denials and raw protected metadata remains hidden.

#### Cluster Build-Plan Link

Completes the query portion of **CL-09 Phase 1, Feature 01** and creates the API used later by **CL-09 Feature 08**.

#### Dependencies

- Module Features 01–04;
- `authorizeResourceAction`;
- `requireStepUpForSensitiveAction` only if an Audit-specific security policy designates a query;
- `createRequestContext`;
- current indexes;
- redacted DTO mapping.

#### In Scope

- `queryAuditEvents`;
- `querySensitiveAccessHistory`;
- bounded cursor pagination;
- actor/action/target/date/sensitivity/request filters supported by schema;
- DTO redaction;
- optional safe target labels only through target-owner interface;
- query-level authority;
- query performance tests.

#### Out of Scope

- full UI;
- unbounded export;
- generic full-text search engine;
- direct target-table joins;
- cross-domain analytics;
- retention mutation;
- new evidence table.

#### Module-Owned Data

Reads:

- `AuditEvent`;
- `AccessAuditLog`.

No writes are required merely to list evidence unless an explicitly protected viewer action itself requires separate Audit proof under existing vocabulary/policy.

#### Public Interfaces

```text
queryAuditEvents(filters, viewer) -> Page<AuditEventView>
querySensitiveAccessHistory(filters, viewer) -> Page<AccessAuditView>
```

Filters must be validated and bounded.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `authorizeResourceAction` | Role / Authority | Before every protected evidence query. | Audit query action names and resource facts. | `canViewAudit`, local admin role checks. |
| `requireStepUpForSensitiveAction` | Identity & Access | Only for specifically approved high-risk query/export action. | Which Audit query requires fresh assurance. | Local MFA flow. |
| `createRequestContext` | Observability/platform | Correlate query and diagnostics. | Safe request metadata. | Query-specific correlation helper. |
| `validateOwnedTargetReference` | Target owner | Optional safe target label/context lookup. | Only minimized view context. | Cross-domain join/repository. |
| `writeStructuredLog` / `captureException` | Observability / Ops | Query diagnostics. | No returned evidence body in logs. | Audit query logger. |

#### Domain Logic

- query only Audit-owned tables;
- authorize before returning evidence;
- redact fields by viewer/action policy;
- do not return arbitrary `metadata` JSON by default;
- enforce maximum page size and date windows;
- preserve not-found/forbidden non-enumeration behavior for sensitive target filters;
- request ID is a correlation aid, not source truth.

#### Authorization / Compliance

- no unauthenticated evidence query;
- admin/support role alone is not sufficient without Role / Authority decision;
- field-level redaction applies to sensitive evidence;
- step-up is conditional on approved Identity/Security policy;
- viewing a target's protected source payload remains a source-owner operation, not an Audit query.

#### Database / Transaction Behavior

Read-only queries:

- use indexes;
- have deterministic order, normally `(createdAt, id)`;
- are cursor/page bounded;
- avoid N+1 foreign-domain joins;
- do not perform locks/mutations.

#### Events / Jobs

None.

#### Provider Integration

None.

#### UI / Admin Surface

No full UI. A minimal protected proof route or test harness is allowed only if root code standards permit it.

#### Failure Behavior

- unauthorized -> safe forbidden result;
- malformed/unbounded filter -> validation error;
- target-context lookup forbidden/not-found -> do not leak target existence;
- database failure -> `persistence_unavailable`/sanitized internal error;
- step-up required -> stable step-up result from Identity capability.

#### Tests

- query filters;
- cursor pagination;
- sort stability;
- max page/window enforcement;
- authorization matrix;
- redaction snapshots;
- not-found versus forbidden leakage test;
- request correlation query;
- index/query-plan smoke test if root DB test tooling supports it;
- test raw Prisma/metadata is not returned.

#### Documentation Updates

- public query contract docs;
- filter/limit rules;
- progress tracker.

#### Acceptance Criteria

1. Authorized query returns only redacted DTOs.
2. Unauthorized caller learns no protected target details.
3. Query pagination is bounded.
4. Correlation filters work according to approved schema.
5. No direct foreign Prisma reads are used.
6. No raw metadata escapes by default.
7. Tests pass at unit, integration, contract, and authorization levels.

#### Exit Gate

Feature 05 passes when CL-09 Feature 01's Module-level requirements are fully green: stable append/query contracts, insert-only evidence, payload minimization, request correlation, and restricted reads.

---

## Phase 3 — Audit Administrative Review Surface

This phase is intentionally sequenced to CL-09's admin-surface milestone. The underlying evidence capability must already be complete.

---

### 06 Audit Administrative Viewer

#### Objective

Provide the Audit-owned portion of the protected CL-09 administrative review surface using public Audit queries rather than repository/Prisma shortcuts.

#### Observable Result

Authorized admin/support/compliance users can:

- list and filter generic audit evidence;
- list and filter sensitive-access evidence;
- inspect a safe evidence detail view;
- correlate records by request/target/actor/action/time as permitted;
- see redacted fields instead of protected source payloads;
- be denied safely when permission/step-up policy is not satisfied.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 4, Feature 08 — Moderation, Hold, and Audit Administrative Review Surfaces**.

This Module feature must not start before the Cluster says Feature 08 is ready.

#### Dependencies

- Module Features 01–05;
- CL-09 Features required by Cluster Feature 08;
- Role / Authority admin permissions;
- root UI/accessibility/routing standards;
- optional Identity step-up policy;
- source-owner protected data views for links to external context, where available.

#### In Scope

- Audit evidence list;
- sensitive-access evidence list;
- filter controls;
- pagination;
- safe evidence detail panel/page;
- explicit redaction states;
- request/correlation navigation;
- source target references that link to owner-approved admin surfaces;
- loading/empty/error/forbidden states;
- accessible table/list behavior.

#### Out of Scope

- generic CL-09 review queue;
- moderation case workflow;
- hold workflow;
- Ops dashboard;
- cross-domain editing;
- raw source payload viewer;
- arbitrary export bundle;
- direct database access from UI;
- custom role engine.

#### Module-Owned Data

Reads only:

- `AuditEvent`;
- `AccessAuditLog`.

Any Audit proof generated by a reviewer action uses existing canonical commands; do not invent a new `AccessAuditAction` solely for UI telemetry.

#### Public Interfaces

The UI consumes:

- `queryAuditEvents`;
- `querySensitiveAccessHistory`.

If a detail endpoint is needed, it must be a narrow protected Audit query returning the same redacted DTO family rather than exposing repository access.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `authorizeResourceAction` | Role / Authority | Route/query/detail guard. | Audit viewer actions and evidence scopes. | `requireAdmin`, `isAuditAdmin`. |
| `requireStepUpForSensitiveAction` | Identity & Access | Only for explicitly designated high-risk view/export action. | Which viewer action requires step-up. | UI-local MFA. |
| `recordSensitiveAccess` | Audit / Event Ledger | Only when the act of accessing protected evidence itself fits an approved canonical action and policy. | Do not invent enum values to log the viewer. | `adminViewAuditLog` local table/action string. |
| `appendAuditEvent` | Audit / Event Ledger | Record important admin mutations only; baseline viewer is read-only. | Do not recursively log every list fetch. | Ad hoc admin logger. |
| `validateOwnedTargetReference` | Target owner | Resolve safe link/summary when needed. | Safe fields only. | Universal target lookup. |

#### Domain Logic

- UI is a view over Audit public queries;
- filter state does not become a source record;
- detail view shows references and safe evidence, not target payload;
- evidence links route to source owner surfaces;
- Audit viewer cannot change underlying Audit rows;
- sensitive viewer access is logged only under an approved existing action/vocabulary; if no current action semantically applies, raise an architecture/action-vocabulary decision rather than invent a string.

#### Authorization / Compliance

- every server query/action checks Role / Authority;
- browser rendering never receives fields the viewer is not allowed to see;
- step-up is server-enforced where approved;
- no assumption that `admin` means unrestricted healthcare/finance/resume/contract access;
- source-domain protected data is viewed through source-domain access controls.

#### Database / Transaction Behavior

Read-only.

No direct Prisma access from route/components.

#### Events / Jobs

None.

#### Provider Integration

None.

#### UI / Admin Surface

Required UI states:

- loading;
- empty;
- results;
- invalid filter;
- forbidden;
- step-up required if applicable;
- transient server error.

Filters should include only fields backed by approved query contracts/indexes.

#### Failure Behavior

- forbidden -> no evidence detail leak;
- target source unavailable -> Audit reference remains visible if authorized, with safe unavailable state;
- missing source record -> do not rewrite Audit history;
- query timeout -> safe retry, no hidden unbounded query fallback.

#### Tests

- component tests for loading/empty/error/redacted states;
- route authorization tests;
- E2E authorized list/detail journey;
- E2E unauthorized denial;
- filter/pagination E2E;
- accessibility checks;
- test that UI cannot invoke update/delete;
- test source links use owner contracts/routes.

#### Documentation Updates

- UI registry if root architecture requires it;
- Module architecture only if a new stable admin query contract is introduced;
- progress tracker;
- Cluster Feature 08 completion evidence.

#### Acceptance Criteria

1. Viewer uses public Audit interfaces only.
2. Unauthorized users cannot query or infer sensitive evidence.
3. No editing/deleting exists.
4. Redaction is visible and enforced server-side.
5. Filters are bounded and index-supported.
6. Source target payloads remain outside Audit.
7. E2E viewer journey passes.

#### Exit Gate

Feature 06 passes only when Audit's portion of CL-09 Feature 08 is contract-safe, redacted, authorized, read-only, and covered by E2E tests.

---

## Phase 4 — Privacy and Cross-Module Integration

This is the Module Integration Phase. It proves Audit behaves as a platform rail without absorbing neighboring truth.

---

### 07 Audit Privacy, Retention, and Export Executor

#### Objective

Implement Audit's owner-local side of the Privacy protocol so Privacy / Data Erasure can discover and safely disposition Audit-owned subject data while preserving required security/legal proof.

#### Observable Result

Privacy orchestration can:

- enumerate Audit-owned subject-linked evidence;
- ask Audit for retention facts;
- request an approved erase/anonymize/retain/export action;
- receive a typed owner result;
- preserve proof that the Privacy workflow occurred without creating an Audit-local Privacy lifecycle.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 5, Feature 10 — CL-09 Privacy, Retention, and Export Executors**.

Production completion is blocked until `U-24` is resolved.

#### Dependencies

- Module Features 01–06;
- Privacy / Data Erasure public protocol;
- explicit `U-24` target vocabulary and retention policy for production disposition;
- canonical `anonymizePersonalFields` if anonymization is approved;
- approved privileged data-disposition boundary.

#### In Scope

- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- owner-specific export serialization if required by Privacy protocol;
- actor-linked record enumeration;
- approved target-linked relationship mapping;
- retention/manual-review outcomes;
- approved anonymization/erasure only after policy exists;
- proof-preserving behavior;
- idempotent Privacy execution.

#### Out of Scope

- `PrivacyRequest`;
- `DataErasureJob`;
- `DataErasureTarget`;
- `DataRetentionExemption`;
- privacy deadline orchestration;
- export bundle storage/delivery;
- deleting foreign records;
- guessing retention periods;
- changing hash-chain fields without approved integrity/privacy design.

#### Module-Owned Data

Potentially reads/mutates under privileged Privacy instruction:

- `AuditEvent`;
- `AccessAuditLog`.

Normal app/admin insert-only rules remain unchanged.

#### Public Interfaces

Implements Privacy-defined owner contracts:

```text
enumerateSubjectData(...)
evaluateRetentionRequirement(...)
executePrivacyInstruction(...)
exportSubjectData(...)   // only if required by Privacy's approved owner contract
```

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `enumerateSubjectData` | Privacy protocol + Audit implementation | Privacy target discovery. | Audit actor/target relationship mapping. | Global DB crawler. |
| `evaluateRetentionRequirement` | Data owner + Privacy | Before disposition. | Audit security/legal retention facts. | Local retention-exemption table. |
| `executePrivacyInstruction` | Privacy orchestrates; Audit executes | Apply approved owner-local result. | Field-level disposition rules. | Audit-local Privacy workflow. |
| `anonymizePersonalFields` | Shared primitive; Audit maps fields | Approved anonymization. | Which fields can change without invalidating proof. | Ad hoc scrubber. |
| `executeIdempotentCommand` | Platform app infra | Privacy target replay. | Privacy target/idempotency identity. | Audit privacy dedupe table. |
| `writeStructuredLog` / `recordIntegrationFailure` | Observability / Ops | Privacy executor diagnostics. | No subject data in telemetry. | Local privacy failure table. |

#### Domain Logic

- Privacy is caller/orchestrator;
- Audit returns owner facts rather than creating exemptions;
- required security/legal evidence is retained when approved policy says so;
- nonessential personal fields are anonymized only through approved mapping;
- erasure proof itself is not silently destroyed;
- if integrity chaining is later enabled, any canonical field mutation follows the approved integrity/privacy design;
- unresolved retention -> `retained` or `manual_review`/policy-unresolved result according to the Privacy result contract, never silent deletion.

#### Authorization / Compliance

- only trusted Privacy orchestration can invoke privileged disposition;
- normal app/admin callers remain insert-only/read-only as authorized;
- export output is minimized to the Privacy request purpose;
- no PHI/resume/contract bodies can appear merely because a target reference exists.

#### Database / Transaction Behavior

- enumerate is bounded/read-only;
- each target instruction is transactionally idempotent;
- privileged anonymization/erase path is explicitly separated from normal application role;
- retained records remain unchanged;
- partial target completion returns typed result to Privacy;
- no broad "delete user from audit tables" query.

#### Events / Jobs

Audit owns no privacy orchestration job.

If Privacy invokes asynchronously, shared queue mechanics belong to Privacy/platform. Audit returns deterministic target results.

#### Provider Integration

None.

#### UI / Admin Surface

None.

#### Failure Behavior

- `U-24` unresolved for a destructive disposition -> feature remains non-production / returns policy-unresolved/manual-review;
- record retention required -> retain and return owner evidence;
- target already anonymized/absent under approved policy -> idempotent result;
- DB failure -> retryable/terminal result per Privacy contract;
- unsupported target mapping -> explicit failure, not fuzzy matching.

#### Tests

- subject enumeration;
- actor-linked records;
- approved target-linked mapping;
- retention path;
- anonymization path with fixture policy;
- erasure path only if approved;
- idempotent replay;
- export minimization;
- normal app/admin still unable to mutate;
- no erasure of required fulfillment proof;
- integration contract with Privacy fake/real implementation.

#### Documentation Updates

When `U-24` is resolved:

- update Module architecture Privacy section;
- update Cluster architecture unresolved register;
- document retention-policy version and target mapping;
- update progress tracker.

#### Acceptance Criteria

1. Privacy orchestrates; Audit does not create a local Privacy lifecycle.
2. Every Audit disposition is based on an approved policy.
3. Required proof is retained where required.
4. Normal roles remain unable to mutate/delete evidence.
5. Executor is idempotent.
6. Export is minimized.
7. Production disposition has no dependency on unresolved `U-24`.

#### Exit Gate

Feature 07 production exit requires `U-24` to be explicitly approved and all retention/anonymization/erasure tests to pass. If `U-24` remains unresolved, only non-destructive contract scaffolding may be marked complete; the feature exit is **FAIL/BLOCKED**, not conditionally green.

---

### 08 Cross-Module Audit Contract Verification

#### Objective

Prove that the most important Workin Ants Modules consume Audit through `appendAuditEvent` and `recordSensitiveAccess` while preserving their own domain/event/access truth.

#### Observable Result

End-to-end contract tests demonstrate that representative workflows create the correct Audit evidence without direct Audit table writes and without Audit changing neighboring source records.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 5, Feature 11 — Cross-Cluster Integration Verification**.

This is the Module's dedicated Integration Phase.

#### Dependencies

- Module Features 01–07;
- corresponding Cluster Features 01–10 as required;
- real public interfaces from representative neighboring Modules;
- contract fakes may be replaced with real integrations here.

#### In Scope

Required representative journeys:

1. **Moderation / Hold**
   - moderation/admin action -> `appendAuditEvent`;
   - hold creation/release -> `appendAuditEvent`;
   - original `ModerationAction` / `ComplianceHold` remains source truth.

2. **Healthcare**
   - source owner decides allowed/redacted/blocked/denied;
   - `recordSensitiveAccess` records result without PHI;
   - Healthcare policy remains truth.

3. **Financial**
   - sensitive processor balance/payout/tax read -> `recordSensitiveAccess` with financial sensitivity;
   - Payment/Payout/Tax remains truth.

4. **Resume**
   - authorized/denied resume access follows Candidate/Role policy;
   - `ResumeAccessLog` remains domain access truth;
   - generic `AccessAuditLog` is also recorded when required.

5. **Media / Digital / Video**
   - Media/Digital/Video owner issues or denies grant/token/URL;
   - domain access event/grant remains source truth;
   - Audit records generic access proof.

6. **Agreement / Contract**
   - Transaction/Order Agreement access/hash action remains domain truth;
   - Audit records view/download/sign/hash verification/tamper detection as required;
   - no full contract content in Audit.

7. **Booking / Calendar**
   - booking/calendar owner changes source state;
   - Audit records selected canonical actions;
   - `ProcessedCalendarEvent` remains Booking-owned.

8. **Location / Messaging / Security**
   - at least one additional protected-context integration proves owner decision + generic Audit evidence.

#### Out of Scope

- replacing every consumer's full E2E suite;
- universal event-store integration;
- direct provider calls;
- direct foreign database writes;
- new local audit tables in consumers;
- Search indexing from Audit;
- Notification provider delivery from Audit.

#### Module-Owned Data

Writes only:

- `AuditEvent`;
- `AccessAuditLog`.

No neighboring source record is written by Audit.

#### Public Interfaces

Production verification for:

```text
appendAuditEvent
recordSensitiveAccess
queryAuditEvents
querySensitiveAccessHistory
```

Privacy executor contract is verified through Feature 07/Cluster Feature 10.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `appendAuditEvent` | Audit / Event Ledger | Generic important actions from source Modules. | Safe action/metadata policy. | Source-local generic audit tables. |
| `recordSensitiveAccess` | Audit / Event Ledger | Protected access outcomes from source owners. | Action/sensitivity compatibility. | Finance/PHI/resume/media generic audit tables. |
| `authorizeResourceAction` | Role / Authority | Source-owner and Audit admin query authority. | Audit does not reinterpret source decision. | Integration auth bypass. |
| `createRequestContext` | Observability/platform | Correlate source action and evidence. | Safe identifiers. | Per-bridge correlation helpers. |
| `recordIntegrationFailure` | Observability / Ops | Surface technical audit handoff failure. | Source operation/retryability. | Consumer-local generic failure tables. |
| `executeIdempotentCommand` | Platform app infra | Replay-safe source commands where needed. | Semantic identity remains source-owned. | Per-consumer audit dedupe table. |
| `publishDomainEvent` / `deduplicateDomainEvent` | Platform event infra | Only where a source owner reaches Audit through an approved event-driven integration. | Source event meaning and Audit consumer effect. | Fire-and-forget/ad hoc inbox. |

#### Domain Logic

The integration contract must preserve this invariant:

```text
source decision / source domain record
  -> optional source domain event/access record
  -> canonical Audit command
  -> Audit evidence
```

Never:

```text
Audit evidence
  -> infer source decision
  -> mutate source domain record
```

Audit completeness expectations must be explicit per integration. A source workflow may require an Audit receipt before it can report success, but that requirement belongs to the source workflow's policy.

#### Authorization / Compliance

Every integration proves:

- source authorization occurs in source owner;
- Audit command is internal/trusted;
- protected payload is minimized;
- sensitive/admin Audit queries are independently authorized;
- no entitlement/hold/readiness logic is copied into Audit.

#### Database / Transaction Behavior

- no cross-module direct Prisma writes;
- Audit insert transaction is separate unless an approved same-database owner transaction hook is explicitly designed;
- event-driven integrations use outbox/inbox when that pattern is selected;
- retries preserve effective-once business effect while distinct accesses remain distinct evidence.

#### Events / Jobs

Only source-owner events/jobs are used where their architecture requires them.

Audit does not publish a mirror of every source event.

#### Provider Integration

None inside Audit.

Provider-facing effects remain with provider owners.

#### UI / Admin Surface

Use the Feature 06 viewer to verify selected evidence appears safely after the workflows run.

#### Failure Behavior

- Audit handoff fails in mandatory-proof workflow -> source follows its approved fail-closed/recovery policy;
- source owner unavailable -> Audit does not reconstruct decision from raw tables;
- event replay -> consumer inbox/idempotency prevents duplicate side effect only where the same evidence fact is being retried;
- technical integration failure -> Observability records it; no fake Audit evidence is created.

#### Tests

- contract test per representative owner;
- integration tests for source truth + Audit evidence;
- assertion that no consumer writes Audit Prisma tables directly;
- assertion that Audit does not write consumer tables;
- no-prohibited-payload fixtures;
- request-correlation propagation;
- event replay where used;
- authorization path;
- E2E admin viewer verification of at least one generic action and one sensitive access.

#### Documentation Updates

- dependency public-interface references;
- integration matrix in Module architecture if a stable new boundary emerges;
- progress tracker;
- Cluster Feature 11 completion report.

#### Acceptance Criteria

1. Representative source Modules use canonical Audit interfaces.
2. No consumer-local generic audit system exists.
3. Domain-specific ledgers remain separate.
4. Audit never decides source authorization/readiness.
5. Correlation survives across source and Audit evidence.
6. Technical failures are observable.
7. No direct foreign Prisma write exists.
8. Integration tests cover generic and sensitive evidence families.

#### Exit Gate

Feature 08 passes when all required representative contracts are proven against real owner interfaces (or explicitly accepted launch fakes for not-yet-built noncritical modules), and no cross-Module ownership violation is present.

---

## Phase 5 — Production Hardening

This phase aligns to CL-09's final hardening milestone and closes Audit-specific launch risks without expanding scope.

---

### 09 Audit Production Hardening and Integrity Readiness

#### Objective

Harden Audit for production under concurrency, retries, unauthorized access, migration/backfill pressure, privacy constraints, high query volume, and optional approved integrity verification.

#### Observable Result

- Insert-only controls survive adversarial mutation attempts.
- Evidence append/query paths remain correct under concurrent load and retries.
- Sensitive payload leakage tests remain green.
- Admin evidence queries remain bounded and performant.
- Privacy behavior is production-approved.
- Audit failure behavior is observable.
- Integrity behavior is explicit: either an approved hash-chain implementation is verified, or the system clearly does not populate/claim a chain.

#### Cluster Build-Plan Link

Supports **CL-09 Phase 6, Feature 12 — CL-09 Security, Concurrency, Reconciliation, and Launch Hardening**.

#### Dependencies

- Module Features 01–08;
- CL-09 Features 01–11;
- all launch-critical architecture decisions resolved;
- production-like database;
- Observability stack;
- Privacy policy;
- optional accepted `PR-CL09-07` / `U-18` for integrity branch.

#### In Scope

Baseline hardening:

- security review;
- authorization review;
- DB policy/grant review;
- evidence immutability tests;
- concurrency/load tests;
- idempotency/replay tests;
- metadata fuzzing/prohibited-field tests;
- query/index performance;
- pagination/DoS bounds;
- Privacy/retention verification;
- migration/backfill review;
- request-correlation completeness;
- failure injection;
- recovery/runbook evidence;
- public contract compatibility/version tests.

Conditional integrity branch only if approved:

- integrate `hashChainRecords`;
- define and implement Audit-owned partition/sequence/canonical field set;
- use canonical crypto;
- use database lock/serializable strategy;
- create verification worker;
- add anomaly handling;
- add safe Notification/Observability handoff if approved;
- add privacy-aware integrity tests.

#### Out of Scope

- introducing hash-chain requirements without approval;
- repeat-infringer/fingerprint logic;
- ghost-account cleanup;
- new providers;
- general analytics warehouse;
- changing source-domain lifecycles;
- new legal retention periods.

#### Module-Owned Data

Baseline:

- `AuditEvent`;
- `AccessAuditLog`;
- `AccessAuditAction`.

Conditional integrity data only if architecture explicitly approves additional fields/records. Do not invent an integrity finding table merely to complete this phase.

#### Public Interfaces

Freeze/version:

- `appendAuditEvent`;
- `recordSensitiveAccess`;
- `queryAuditEvents`;
- `querySensitiveAccessHistory`;
- Privacy executor contracts.

Any breaking DTO change requires explicit migration/deprecation plan.

#### Shared Operations Used

| Canonical operation | Owner | Invocation | Local policy | Prohibited duplicate |
| --- | --- | --- | --- | --- |
| `authorizeResourceAction` | Role / Authority | Final permission matrix tests. | Audit resource/action facts. | Local admin permission code. |
| `requireStepUpForSensitiveAction` | Identity & Access | Final approved high-risk actions. | Audit-specific action selection. | Local MFA. |
| `executeIdempotentCommand` | Platform app infra | Fault/replay testing. | Same-fact versus new-fact semantics. | Audit idempotency subsystem. |
| `acquireAggregateLock` | Shared persistence infra | Conditional hash-chain append/verification coordination only if approved. | Chain partition lock key. | In-memory mutex / local lock helper. |
| `hashCanonicalPayload` | Shared crypto | Approved integrity/export proof only. | Audit canonical bytes/purpose/version. | Local SHA/HMAC. |
| `hashChainRecords` | Proposed shared crypto | **Conditional: use only after explicit acceptance.** | Audit chain partition/sequence/anomaly policy. | Local chain implementation. |
| `enqueueReliableJob` / `executeRetryWithBackoff` | Shared queue/platform | Conditional integrity verification worker. | Payload/retry/dead-letter meaning. | Audit queue/retry framework. |
| `sanitizeTelemetryMetadata` | Observability / Ops + Audit policy | Final fuzzing/redaction. | Audit allowlists/limits. | Local redaction stack. |
| `recordIntegrationFailure` / `writeStructuredLog` / `captureException` | Observability / Ops | Fault-injection visibility. | Safe Audit diagnostics. | Generic Audit failure table or direct Sentry. |
| `requestNotification` | Notification | Conditional integrity alert after approved anomaly. | Severity, recipients, safe variables. | Direct email/SMS/push. |

#### Domain Logic

### Baseline path when hash chaining is not approved

- leave `previousHash` / `entryHash` unused or only in their explicitly approved non-chain role;
- do not populate them in a way that implies a chain;
- do not expose "tamper-evident chain verified" UI/copy;
- pass launch hardening based on insert-only DB enforcement, access controls, payload minimization, and tested evidence integrity within that scope.

### Conditional path when hash chaining is approved

The accepted architecture must specify before coding:

- partition key;
- ordered sequence;
- canonical field set;
- canonical serialization version;
- digest/HMAC algorithm/version;
- head/anchor storage;
- atomic append strategy;
- verification cadence;
- anomaly result;
- privacy/anonymization effect;
- backfill/migration behavior;
- alert/escalation behavior.

Implementation then uses shared crypto and shared DB-lock/queue mechanisms only.

#### Authorization / Compliance

Security review must cover:

- unauthorized direct write;
- update/delete attempts;
- evidence scraping;
- actor spoofing;
- target-ID enumeration;
- role escalation;
- step-up bypass;
- metadata injection;
- oversized JSON;
- secret/PHI/resume/contract leakage;
- privacy privileged-path isolation.

#### Database / Transaction Behavior

Review:

- indexes;
- query plans;
- role/grant/RLS behavior;
- insert throughput;
- lock behavior if integrity branch exists;
- idempotency transaction boundaries;
- migration ordering;
- backfill dry-run;
- rollback/forward-fix plan;
- retention/index growth strategy;
- production-like concurrency.

No unresolved destructive migration is allowed.

#### Events / Jobs

Baseline: no Audit-owned recurring job required.

Conditional integrity:

- durable shared queue;
- retry classification;
- dead-letter/manual review;
- correlation;
- operational telemetry;
- no source business mutation.

#### Provider Integration

None.

Audit may use Observability/Notification public ports; provider clients remain external.

#### UI / Admin Surface

- final viewer security/performance pass;
- no new screens required;
- optional integrity status display only if architecture/record/query contract is approved.

#### Failure Behavior

- Audit persistence failure is surfaced and never silently ignored;
- permission failure returns safe denial;
- queue/integrity technical failure is retryable/dead-lettered if that branch exists;
- deterministic integrity mismatch is not retried forever;
- privacy policy mismatch blocks disposition;
- migration/backfill anomaly blocks deployment.

#### Tests

Baseline:

- full unit suite;
- full contract suite;
- full DB integration suite;
- RLS/grant/update/delete attack tests;
- load/concurrency append test;
- query performance test;
- idempotency replay/fault test;
- metadata fuzz/property tests;
- authorization/step-up tests;
- Privacy retention/anonymization/erase tests;
- admin E2E;
- cross-Module E2E;
- migration dry-run;
- production build/typecheck/lint.

Conditional integrity:

- canonical serialization test vectors;
- chain append concurrency;
- missing/reordered/modified record detection;
- version migration;
- worker retry/dead-letter;
- privacy mutation interaction;
- anomaly notification/observability.

#### Documentation Updates

- freeze Module public contracts;
- update Module architecture with all accepted decisions;
- update Cluster architecture if a binding cross-cutting decision changed;
- update runbook/progress tracker;
- include final completion report and unresolved non-launch risks.

#### Acceptance Criteria

1. Normal app/admin update/delete attempts fail at DB and application boundaries.
2. Authorized append/query succeeds under production-like load.
3. Distinct repeated access is never lost through over-aggressive dedupe.
4. All prohibited-data tests pass.
5. Audit query surfaces are bounded and performant.
6. Privacy behavior has approved policy and passing tests.
7. No launch-critical Audit path depends on unresolved architecture.
8. Provider/operational failures remain outside Audit truth.
9. If hash chaining is not approved, no code/copy/test claims it exists.
10. If hash chaining is approved, full chain design and verification tests pass.
11. Cross-Module integration tests remain green.
12. Typecheck, lint, unit, integration, E2E, schema validation, and production build all pass.

#### Exit Gate

The Audit / Event Ledger Module is production-ready only when:

1. Features 01–08 are green;
2. `U-17` is resolved and implemented;
3. `U-24` is resolved for production Privacy behavior;
4. normal-role insert-only enforcement is verified;
5. admin/sensitive evidence access passes authority/redaction tests;
6. evidence append/query paths pass concurrency/load/fault tests;
7. no prohibited sensitive payload enters Audit or telemetry fixtures;
8. cross-Module contracts prove source-owner truth separation;
9. migrations/backfills are safe on a production-like database;
10. the integrity branch is either fully approved/tested or explicitly absent with no compliance claim depending on it;
11. all required quality commands pass;
12. architecture, plan, progress tracker, and completion report reflect the final state.

---

# MODULE INTEGRATION PHASE

**Phase 4, Feature 08** is the dedicated Module Integration Phase.

Its purpose is not merely to prove that Audit can insert rows. It proves the architectural boundary:

```text
source owner decides / mutates source truth
        |
        +--> domain event/access proof, if owned there
        |
        +--> appendAuditEvent or recordSensitiveAccess
        |
        v
Audit preserves generic evidence only
```

Required boundary proofs include:

- Moderation/Hold -> generic Audit;
- Healthcare -> source decision + AccessAuditLog;
- Payment/financial -> source decision + AccessAuditLog;
- Resume -> ResumeAccessLog + AccessAuditLog;
- Media/Digital/Video -> owner grant/event + AccessAuditLog;
- Agreement -> Agreement lifecycle/access proof + AccessAuditLog;
- Booking/Calendar -> Booking/processed-event truth + Audit evidence;
- Privacy -> Privacy orchestration + Audit owner-local executor.

Every integration test must use public contracts. A failing public contract is corrected at that boundary rather than replaced with a direct Prisma query/write.

---

# MODULE HARDENING PHASE

**Phase 5, Feature 09** is the dedicated Module Hardening Phase.

It covers only Audit-specific production risk:

- insert-only enforcement;
- query authorization;
- step-up where approved;
- payload minimization/redaction;
- concurrency;
- idempotency/replay;
- request correlation;
- audit completeness;
- failure visibility;
- Privacy/retention;
- query/index performance;
- migration/backfill safety;
- optional hash-chain implementation only after explicit acceptance.

It does not authorize:

- new provider integrations;
- new domain ledgers;
- new legal retention periods;
- ghost-account deletion;
- unapproved hash-chain claims.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --- | --- | --- |
| 1 | Contracts and Source-of-Truth Foundation | 01 Audit Contract and Schema Alignment; 02 Insert-Only Storage and Audit Payload Policy |
| 2 | Core Public Audit Capabilities | 03 Generic Audit Append Command; 04 Sensitive Access Evidence Command; 05 Protected Evidence Queries and Request Correlation |
| 3 | Audit Administrative Review Surface | 06 Audit Administrative Viewer |
| 4 | Privacy and Cross-Module Integration | 07 Audit Privacy, Retention, and Export Executor; 08 Cross-Module Audit Contract Verification |
| 5 | Production Hardening | 09 Audit Production Hardening and Integrity Readiness |

**Total numbered features: 9.**

---

# MODULE EXECUTION PATTERN

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read Canonical Shared Operations.
3. Read CL-09 architecture and build plan.
4. Read `audit_event_ledger/module-architecture.md` and this plan.
5. Read public-interface sections for direct dependencies.
6. Confirm the prior Module feature exit gate.
7. Confirm the corresponding CL-09 milestone is ready.
8. Check every Proposed Ruling / Unresolved Decision that can block this feature.
9. Write a concise implementation specification for this feature only.
10. Implement only this feature.
11. Run required quality checks.
12. Verify public contracts/workflow boundaries.
13. Update progress and completion report.
14. Update architecture only when a binding decision legitimately changed.
15. Record unresolved risks.
16. Do not begin the next feature if the exit gate is failed or blocked.

---

# REQUIRED FEATURE IMPLEMENTATION SPECIFICATION

Immediately before coding a numbered feature, the coding agent must produce a concise implementation specification for **that feature only** containing:

- Objective
- Observable result
- Cluster build-plan link
- Dependencies
- In scope
- Out of scope
- Owned data affected
- Schema/migration impact
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
- Blocking Proposed Rulings / Unresolved Decisions

Do not pre-write implementation specifications for all remaining features. The specification must use the current accepted architecture and the previous feature's completion report.

---

# REQUIRED COMPLETION REPORT

After implementing each numbered feature, the coding agent must report:

- **Feature completed**
- **Cluster build-plan feature supported**
- **Files added**
- **Files changed**
- **Database changes**
- **Migrations**
- **Dependencies added**
- **Module public interfaces added/changed**
- **Shared operations reused**
- **Shared duplicate implementations removed/avoided**
- **Events/jobs added**
- **Provider adapters changed** — normally `None` for this Module
- **Tests added/changed**
- **Commands run**
- **Manual/contract verification**
- **Authorization/RLS/database-policy verification**
- **Privacy/compliance verification**
- **Architecture decisions accepted/changed**
- **Documentation updated**
- **Assumptions**
- **Known failures**
- **Remaining risks**
- **Deferred work**
- **Exit-gate result: PASS / FAIL / BLOCKED**

If the exit gate is not `PASS`, the report must name the exact failing or blocking condition and the next numbered feature must not be marked ready.

---

# FINAL MODULE QUALITY GATE

Before declaring the Module complete, verify all of the following:

1. `AuditEvent`, `AccessAuditLog`, and `AccessAuditAction` have exactly one owner.
2. `AuditEventType` / `AuditEventActor` were not invented from registry claims without explicit ruling.
3. `appendAuditEvent` has one canonical storage contract including the approved request/outcome behavior.
4. `recordSensitiveAccess` records owner decisions without becoming the decision maker.
5. Domain lifecycle event ledgers remain domain-owned.
6. Domain-specific access proof remains domain-owned.
7. Provider processed-event ledgers remain provider-owner truth.
8. Observability remains separate from Audit evidence.
9. Privacy orchestration remains Privacy-owned.
10. Search and Media/Notification/provider integrations remain external.
11. Normal application/admin roles cannot update/delete Audit evidence.
12. Public interfaces return DTOs, not Prisma models.
13. Generic metadata cannot carry prohibited payload classes.
14. Request correlation uses the shared context mechanism.
15. Idempotency does not suppress distinct legitimate access attempts.
16. Cross-Module reads use owner public interfaces where needed.
17. Admin viewer is authorized, redacted, bounded, and read-only.
18. Privacy behavior is approved and testable.
19. Hash chaining is either fully approved and implemented through shared crypto or explicitly absent.
20. Every numbered feature has a completion report and passing exit gate.
21. The final Module implementation remains aligned with CL-09 sequencing and does not silently redefine Cluster architecture.
