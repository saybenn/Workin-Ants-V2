# Audit / Event Ledger Module Architecture

## 1. Module Header

| Item | Value |
| --- | --- |
| Module ID | `audit_event_ledger` |
| Module name | Audit / Event Ledger Module |
| Module type | `capability_ops_compliance_support` |
| Build status | `mvp_active` |
| Primary Cluster | `CL-09 Moderation, Holds, Audit & Ops` |
| Document status | Implementation-grade Module architecture. Binding for confirmed rulings; Proposed Rulings and Unresolved Decisions are not implementation authority until explicitly accepted. |
| Intended audience | Coding agents, developers, reviewers, maintainers, security/compliance reviewers, and architecture owners |
| Relationship to root architecture | Subordinate to the root Workin Ants architecture, project overview, code standards, and source-of-truth rules. Root decisions take precedence when they are more specific and do not transfer this Module's confirmed ownership. |
| Relationship to Cluster architecture | Implements only the Audit / Event Ledger responsibility inside CL-09. The Cluster coordinates Moderation, Holds, Audit, and Observability but owns no source records itself. |
| Update rule | Update this file when a binding decision changes Audit-owned schema meaning, public contracts, append-only enforcement, action vocabulary, privacy/retention behavior, integrity design, or a confirmed cross-Module boundary. Build progress must not silently redefine architecture. |

### Evidence basis

This architecture is synthesized from the current Workin Ants Module Architecture Extract and the supplied current evidence set:

- Deep Module Registry;
- current Prisma schema;
- Ubiquitous Language / Compliance Inventory;
- Canonical Shared Operations Architecture;
- CL-09 `architecture.md`;
- CL-09 `build-plan.md`;
- current project overview.

Where those sources conflict, this document preserves the confirmed source-of-truth boundary and marks the conflict explicitly.

### Evidence conflicts carried into this document

1. The Deep Module Registry claims `AuditEventType` and `AuditEventActor` as Audit-owned schemas, but neither exists in the current Prisma schema.
2. Canonical `appendAuditEvent` requires request ID and outcome in its contract, but current `AuditEvent` has neither as a first-class field.
3. `AccessAuditLog` has optional `previousHash` and `entryHash`, but no approved hash-chain partition, sequence, algorithm/version, anchoring, verification, or privacy strategy exists.
4. CL-09 privacy target vocabulary and Audit retention durations are not yet approved.
5. `AccessAuditLog.accessDecision` currently consumes the Healthcare-owned `HealthcareAccessDecision` enum; Audit records that result but does not own healthcare access policy.

---

## 2. Purpose, Goal, and Transformation

### Purpose

The Audit / Event Ledger Module preserves two kinds of cross-platform proof:

1. generic proof that an important actor or system action occurred; and
2. generic proof that protected data or access credentials were viewed, issued, downloaded, denied, blocked, or redacted.

It centralizes these proof rails so every compliance-sensitive Module does not invent its own generic audit table, logger, or sensitive-access ledger.

### Goal

Make important action and sensitive-access evidence trustworthy, queryable, minimized, correlated, and protected while preserving the rule that the business or compliance Module that made the underlying decision remains the source of truth.

### What enters

Typical inputs are:

- trusted authenticated or system actor context;
- a source Module and operation context;
- target type and target ID;
- generic action or `AccessAuditAction`;
- source-owner access outcome when the operation concerns protected data;
- `DataSensitivity`;
- healthcare-owned access decision when applicable;
- request/correlation ID;
- hashed IP and user-agent evidence where permitted;
- schema-validated, minimized metadata;
- optional integrity metadata only after an approved integrity design.

### What leaves

The Module may produce:

- an `AuditEvent` receipt;
- an `AccessAuditLog` receipt;
- restricted, redacted audit-history query results;
- restricted, redacted sensitive-access-history query results;
- privacy-owner enumeration, retention-fact, export, or disposition results for Audit-owned records;
- an integrity finding only if the proposed hash-chain architecture is later accepted.

### Capability transformation

```text
Important action / protected-access outcome
        |
        v
Trusted actor + request context
        |
        v
Audit-owned validation and payload minimization
        |
        +--> AuditEvent
        |
        +--> AccessAuditLog
        |
        v
Insert-only evidence storage
        |
        +--> protected evidence queries / admin viewer
        |
        +--> Privacy-owned workflow participation
        |
        +--> conditional integrity verification if approved
```

The Module transforms an already-decided action or access result into durable evidence. It does **not** transform that evidence into authorization, compliance approval, business state, provider state, or workflow completion.

### Why this deserves its own Module boundary

Audit proof is cross-cutting, security-sensitive, and subject to anti-duplication, append-only, minimization, retention, and restricted-query requirements that should be implemented once. At the same time, generic audit cannot safely own the meaning of every Order, Booking, Agreement, Resume, Security, Media, Healthcare, Payment, or provider lifecycle. A dedicated Module gives the platform one proof rail without creating a universal event store or universal policy engine.

---

## 3. Owned Truth

### 3.1 Confirmed owned models

| Record | Plain-English meaning | Source-of-truth role |
| --- | --- | --- |
| `AuditEvent` | Generic proof that an important actor or system action occurred against a named target. | Generic platform action evidence. It is not the target's lifecycle truth. |
| `AccessAuditLog` | Generic proof of a protected data/access event such as a read, download, token issuance, denial, block, redaction, sensitive financial read, contract access, privacy action, or similar event. | Generic sensitive-access evidence. It is not the data owner's access policy or domain-specific access ledger. |

### 3.2 Confirmed owned enum

`AccessAuditAction` is the controlled action vocabulary used by `AccessAuditLog`.

Current executable values are:

**General protected access**
- `file_read`
- `file_download`
- `message_read`
- `thread_opened`
- `video_joined`
- `location_revealed`

**Privacy**
- `privacy_export_generated`
- `privacy_erasure_started`
- `privacy_erasure_completed`

**Healthcare/admin redaction**
- `healthcare_policy_checked`
- `healthcare_payload_redacted`
- `healthcare_payload_blocked`
- `admin_redacted_view`
- `admin_blocked_view`

**Financial/security**
- `processor_balance_read`
- `payout_account_read`
- `tax_profile_read`
- `tax_dashboard_opened`
- `payout_request_started`
- `sensitive_financial_step_up_verified`
- `phone_number_changed`
- `account_recovery_completed`

**Video and digital delivery**
- `course_video_started`
- `course_video_completed`
- `live_video_token_issued`
- `digital_download_url_issued`
- `digital_download_denied`
- `digital_download_started`
- `digital_download_completed`
- `course_video_playback_granted`
- `course_video_playback_denied`

**Agreement/contract**
- `agreement_viewed`
- `agreement_downloaded`
- `agreement_signed`
- `agreement_hash_verified`
- `agreement_tamper_detected`
- `agreement_manual_opt_out`

**Media**
- `media_signed_url_issued`
- `media_signed_url_denied`
- `media_upload_rejected`
- `media_malware_detected`
- `media_metadata_scrubbed`
- `media_quarantined`
- `media_promoted_to_ready`

**Calendar/booking**
- `calendar_connection_started`
- `calendar_connection_authorized`
- `calendar_connection_revoked`
- `calendar_free_busy_synced`
- `booking_hold_created`
- `booking_confirmed`
- `booking_slot_lock_failed`
- `booking_orchestration_started`
- `booking_orchestration_failed`

Adding, renaming, or merging an `AccessAuditAction` is an Audit contract/schema change. A coding agent must not create a local string alias to avoid updating the canonical vocabulary.

### 3.3 Claimed but not currently implemented schemas

The registry claims ownership of:

- `AuditEventType`;
- `AuditEventActor`.

They are absent from the current Prisma schema. Current `AuditEvent.action` and `AuditEvent.entityType` are `String`, while actor identity is represented only by nullable `actorUserId`.

**Binding implementation rule:** do not create `AuditEventType` or `AuditEventActor` merely because the registry lists them. Resolve Unresolved Decision `U-16` first.

### 3.4 Lifecycles owned

`AuditEvent` and `AccessAuditLog` are creation-only evidence records.

They have no status lifecycle. Their lifecycle is:

```text
validated request
  -> insert
  -> retained/queryable evidence
```

There is no normal update, reopen, release, completion, or delete transition.

### 3.5 Domain events / ledgers owned

The Module owns the generic `AuditEvent` evidence ledger and generic `AccessAuditLog` access-evidence ledger.

It does **not** own domain lifecycle ledgers such as:

- `OrderEvent`;
- `BookingEvent`;
- `JobInterviewEvent`;
- `AgreementEvent`;
- `UserSecurityEvent`;
- `ResumeAccessLog`;
- `MediaAccessEvent`;
- `DigitalDownloadEvent`;
- `PointLedgerEntry`;
- provider processed-event ledgers.

### 3.6 Projections owned

No durable Audit projection is currently confirmed.

The admin audit viewer may use redacted DTO/read-model composition, but that read model is rebuildable and must not become a third Audit source-of-truth table without an explicit architecture decision.

### 3.7 Snapshots / proof owned

Confirmed proof:

- generic actor/action/target/time proof in `AuditEvent`;
- sensitive access/action/sensitivity/request-context proof in `AccessAuditLog`.

Conditional integrity metadata:

- `AccessAuditLog.previousHash`;
- `AccessAuditLog.entryHash`.

These fields do not establish a complete tamper-evident chain until `PR-CL09-07` and `U-18` are resolved.

### 3.8 Policies and invariants owned

The Module owns:

- which input shapes are valid for `appendAuditEvent`;
- which input shapes are valid for `recordSensitiveAccess`;
- Audit metadata allowlists and size limits;
- prohibited-data filtering for generic evidence payloads;
- mapping from canonical Audit public contracts to Audit-owned records;
- redaction of Audit query DTOs;
- append-only repository behavior;
- Audit-specific retention facts once approved;
- Audit-specific integrity partition/canonical fields/anomaly policy only if hash chaining is later approved.

---

## 4. Explicit Non-Ownership

Coding agents must preserve the following boundaries.

| Adjacent owner | Responsibility that stays outside Audit | Audit's permitted role |
| --- | --- | --- |
| Identity & Access | Authentication, sessions, actor assurance, passkeys/MFA, recovery lifecycle, `UserSecurityEvent` truth. | Record safe generic proof or sensitive access/security actions after Identity has made the decision. |
| Role / Authority | Permission interpretation for platform, organization, participant, and ownership scope. | Use authority decisions to protect Audit queries/admin surfaces; never become a permission engine. |
| Healthcare / Regulated Services | Healthcare data-boundary and allow/redact/block/deny policy. | Record the healthcare-owned decision and access action. |
| Payment / Payout / Tax | KYC, tax, payout-account, balance, payout lifecycle, Stripe/provider state, `ProcessedStripeEvent`. | Record sensitive financial reads/actions and important generic admin actions. |
| Transaction / Order | `Order`, `OrderEvent`, Agreement lifecycle, `AgreementEvent`, signature/hash/document truth. | Record generic important actions and sensitive contract access/tamper-detection evidence. |
| Booking & Calendar | Booking lifecycle, calendar provider connection/sync state, `ProcessedCalendarEvent`, booking event truth. | Record sensitive booking/calendar actions when policy requires. |
| Job Interview | Interview lifecycle and `JobInterviewEvent`. | Record generic/sensitive interview or video access evidence. |
| Candidate Application & Resume Privacy | Resume authorization, `ResumeAccessLog`, application/resume context. | Record broader sensitive-access proof in addition to the resume-specific record. |
| Media / File Access | `MediaAsset`, scanning, processing, storage, signed URLs, `MediaAccessGrant`, file access mechanics. | Record generic sensitive access or security proof after Media makes the access/processing decision. |
| Video Infrastructure | Video rooms/assets/grants, provider mechanics, provider-event dedupe, playback/join policy. | Record video access/token evidence. |
| Digital Goods Access | Digital download asset/grant/event truth and entitlement policy. | Record download URL issuance/denial/start/completion evidence as appropriate. |
| Messaging | Thread/message truth and participant context. | Record protected reads after Messaging/Role/Healthcare access decisions. |
| Location Safety | Exact-location reveal policy and `LocationReveal`. | Record `location_revealed` evidence; never decide reveal eligibility. |
| Content Moderation & Legal Notice | Reports, notices, cases, moderation decisions/actions, enforcement orchestration. | Record reviewer/admin actions and protected evidence reads. |
| Admin Review / Compliance Hold | `ComplianceHold` creation/evaluation/release lifecycle. | Record important hold actions. |
| Observability / Ops | Request context, structured logs, metrics, exceptions, integration failures, queue telemetry, health, incidents. | Consume request context and operational diagnostics; never create competing generic operational records. |
| Notification | Notification persistence, routing, templates, channel/provider delivery. | Request an alert only for an Audit-owned trigger such as an approved integrity anomaly. |
| Privacy / Data Erasure | `PrivacyRequest`, erasure jobs/targets, retention exemptions, export orchestration. | Enumerate Audit-owned subject data and execute owner-local instructions under Privacy orchestration. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense projection, search queries/reconciliation. | None. Audit records are not public-search source records. |
| Track Subscription & Entitlement | Plan, entitlement, usage, quota, waiver, boost, commission policy. | None except optional generic audit proof of admin entitlement actions. |

### Prohibited ownership shortcuts

Audit must not become:

- a universal domain event store;
- a generic cross-domain repository;
- a generic authorization service;
- a generic compliance engine;
- a generic provider webhook ledger;
- a generic operational failure table;
- a privacy workflow owner;
- a search index;
- a file evidence store;
- a notification delivery service;
- a ghost-account deletion workflow.

The registry desire to identify "ghost accounts" may support a future Audit-derived inactivity report, but account suspension/deletion/erasure remains Identity/Admin/Privacy-owned.

---

## 5. Module Architecture Principles

1. **Evidence records describe facts; they do not create business truth.**
2. **Generic audit and sensitive-access proof are separate commands.** `appendAuditEvent` and `recordSensitiveAccess` must not collapse into one ambiguous logging API.
3. **Sensitive access is decided before it is recorded.** The data/context owner supplies the access result.
4. **Normal app/admin roles cannot update or delete Audit evidence.**
5. **Audit metadata is minimized and schema-validated.** Generic JSON is not permission to dump domain payloads.
6. **Domain access proof can coexist with `AccessAuditLog`.** `ResumeAccessLog`, `MediaAccessEvent`, `DigitalDownloadEvent`, Agreement access events, and similar records remain separate truth.
7. **Request correlation is shared infrastructure.** Audit consumes `createRequestContext`; it does not invent a correlation-ID subsystem.
8. **Operational logging is not Audit truth.** Structured logs/Sentry are diagnostics and cannot substitute for `AuditEvent`/`AccessAuditLog`.
9. **Audit should not re-read provider state.** Provider-specific status and dedupe remain with provider owners.
10. **No direct cross-Module Prisma access for business meaning.** If existence or safe target context must be validated, use owner interfaces.
11. **Legitimate repeated accesses are legitimate repeated evidence.** Idempotency must not accidentally suppress separate reads/downloads/attempts.
12. **Integrity claims require a complete design.** Optional hash fields are not sufficient proof of hash-chain integrity.
13. **Privacy orchestration stays external.** Audit owns its data disposition execution, not the request/job lifecycle.
14. **Admin audit access is itself subject to authority and, where appropriate, sensitive-access logging.**
15. **No false compliance claims.** The Module may claim only the audit properties actually enforced and tested.

---

## 6. Proposed Folder / Code Structure

The exact repository prefix must follow root `code-standards.md`. The relative ownership shape is:

```text
<module-root>/audit-event-ledger/
  domain/
    payload-policy/
    action-policy/
  application/
    commands/
      append-audit-event.*
      record-sensitive-access.*
    queries/
      query-audit-events.*
      query-sensitive-access-history.*
  public/
    commands.*
    queries.*
    contracts.*
    privacy.*
  infrastructure/
    repositories/
      audit-event-repository.*
      access-audit-repository.*
    append-only-storage/
  privacy/
    enumerate-subject-data.*
    evaluate-retention-requirement.*
    execute-privacy-instruction.*
    export-audit-subject-data.*
  ui/
    admin/
      audit-viewer/
  tests/
    unit/
    integration/
    contract/
    authorization/
    privacy/
    e2e/
```

Conditional only after `PR-CL09-07` is explicitly accepted:

```text
<module-root>/audit-event-ledger/
  domain/
    integrity-policy/
  workers/
    verify-audit-integrity.*
```

### Folder constraints

- Do not create a `providers/` folder; this Module owns no external provider.
- Do not create `utils/`, `helpers/`, or generic `services/` buckets.
- Shared crypto, idempotency, locking, queue, request-context, logging, and retry primitives remain in the canonical shared/platform locations.
- Caller-specific finance/healthcare/resume/media helpers must not become new Audit services. They may construct the canonical command DTO at the source Module boundary.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / admin UI | Audit viewer/filter UX, safe rendering, bounded pagination, explicit sensitive-data reveal controls. | Role engine, source-domain detail screens, universal admin review lifecycle. |
| Public contracts | Stable command/query DTOs, receipts, redacted views, privacy executor contract. | Provider payload types, foreign Prisma models as DTOs. |
| Application commands | Orchestrate validation, sanitization, request context, repository append, safe result. | Source business/compliance decisioning. |
| Application queries | Protected filters, paging, DTO redaction, actor/target references. | Generic cross-domain joins or hidden authorization reconstruction. |
| Domain payload policy | Allowed metadata fields, forbidden classes, size/truncation rules, action/sensitivity compatibility. | Healthcare/financial/resume authorization policy. |
| Domain action policy | `AccessAuditAction` ownership and compatibility rules. | Domain lifecycle transition vocabularies. |
| Repositories | Insert `AuditEvent` / `AccessAuditLog`; bounded reads of Audit-owned tables. | Update/delete APIs for normal operation; repositories for other Modules. |
| Append-only storage | Database-enforced mutation restrictions and privileged maintenance boundary. | Privacy orchestration or domain repair policy. |
| Privacy executor | Enumerate Audit-owned subject data, return retention facts, execute approved owner-local dispositions. | `PrivacyRequest`, `DataRetentionExemption`, or cross-platform erasure orchestration. |
| Workers | Conditional integrity verification only after accepted architecture. | Generic queue framework or provider reconciliation. |
| Adapters | None owned. Audit consumes platform/Module public ports. | Sentry, Stripe, Typesense, R2, calendar, video, notification, or webhook clients. |

---

## 8. Data Model

### 8.1 `AuditEvent`

**Purpose:** generic proof that an important platform actor or system action occurred.

Current authoritative fields:

| Field | Meaning / rule |
| --- | --- |
| `id` | UUID evidence identifier. |
| `actorUserId` | Optional UUID of the acting User when a user actor exists. It is currently a scalar, not a Prisma relation. |
| `entityType` | Free-form target/entity namespace string. It identifies a target class but does not confer ownership or validate the foreign record by itself. |
| `entityId` | Optional UUID of the referenced target. |
| `action` | Free-form action string in current Prisma. Canonical action naming must be controlled by public contracts/payload validation until `U-16` is resolved. |
| `metadata` | Optional JSON. Must be schema-validated, minimized, size-bounded, and free of prohibited sensitive payloads. |
| `createdAt` | Server-created evidence timestamp. |

Current indexes:

- `actorUserId`;
- `(entityType, entityId)`;
- `(action, createdAt)`.

Current missing fields relative to canonical `appendAuditEvent`:

- first-class request/correlation ID;
- first-class outcome.

That mismatch is `U-17`.

**Lifecycle/status:** none; creation-only.

**Uniqueness:** only primary key. There is no semantic event uniqueness constraint.

**Concurrency:** append-only; no normal write-write transition race. Caller idempotency must be handled intentionally where a retried command should not create duplicate proof.

**Retention/privacy:** may contain actor ID and metadata containing personal references. Retention and anonymization require approved Privacy/Audit policy. Do not hard-delete evidence solely because it contains a user reference.

### 8.2 `AccessAuditLog`

**Purpose:** sensitive-data/access proof for protected reads, downloads, token/grant issuance, denies, blocks, redactions, privacy actions, sensitive financial actions, contract access, and similar actions.

Current authoritative fields:

| Field | Meaning / rule |
| --- | --- |
| `id` | UUID evidence identifier. |
| `actorUserId` | Optional UUID of the user actor. Current Prisma relation points to `User`. |
| `targetType` | Target namespace string. This is not a universal cross-domain repository key. |
| `targetId` | Required UUID target identifier. |
| `action` | Canonical `AccessAuditAction`. |
| `sensitivity` | `DataSensitivity`, default `normal`; the underlying sensitivity meaning is supplied by the data/context owner. |
| `accessDecision` | Optional `HealthcareAccessDecision`. When present, it records Healthcare-owned outcome; Audit does not decide it. |
| `requestId` | Optional request/correlation identifier. |
| `ipHash` | Optional hashed IP evidence. Raw IP should not be persisted here by convenience. |
| `userAgent` | Optional user-agent evidence; treat as personal/telemetry data for retention purposes. |
| `previousHash` | Optional prior-entry integrity metadata. Not proof of a complete chain by itself. |
| `entryHash` | Optional current-entry integrity metadata. Not proof of a complete chain by itself. |
| `createdAt` | Server-created evidence timestamp. |

Current indexes:

- `(actorUserId, createdAt)`;
- `(targetType, targetId)`;
- `(sensitivity, createdAt)`;
- `(action, createdAt)`;
- `requestId`.

**Lifecycle/status:** none; creation-only.

**Uniqueness:** only primary key. Legitimate repeated accesses are expected.

**Concurrency-sensitive fields:** `previousHash` and `entryHash` become concurrency-sensitive only if hash chaining is approved. Any chain design then requires an approved partition, atomic order/sequence, and locking strategy.

**Retention/privacy:** this model may contain actor ID, target reference, sensitivity, user-agent, hashed IP, and request context. Security/legal retention may apply, but exact duration and anonymization are unresolved. Hash chaining, if enabled, must explicitly support privacy disposition without falsifying integrity.

### 8.3 Consumed enums

Audit consumes but does not own:

- `DataSensitivity`;
- `HealthcareAccessDecision`.

Current `DataSensitivity` values include:

- `normal`;
- `sensitive`;
- `healthcare`;
- `financial`;
- `identity_document`;
- `resume`;
- `legal_contract`;
- `private_message`.

Current `HealthcareAccessDecision` values:

- `allowed`;
- `redacted`;
- `blocked`;
- `denied`.

Audit records these facts; it does not define the healthcare decision policy.

### 8.4 Relationship rules

- A reference to `entityType/entityId` or `targetType/targetId` does not grant direct database access to the target owner.
- Audit query DTOs should expose stable references and safe labels only when those labels can be obtained through an approved owner interface.
- `AuditEvent` and `AccessAuditLog` must not gain foreign keys to every possible target merely to make joins convenient.
- Any future actor representation for system/webhook/service actors requires an explicit ruling; do not overload `actorUserId`.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `AuditEvent`

```text
validated
  -> appended
  -> retained/queryable
```

There is no mutable status.

- **Transition owner:** Audit / Event Ledger.
- **Trigger:** approved `appendAuditEvent`.
- **Terminal state:** appended evidence.
- **Reversal/reopen:** none. A later correction is a new evidence event if architecture permits; it does not rewrite prior evidence.
- **Concurrency expectation:** concurrent valid events may append independently.
- **History proof:** the row itself is the generic evidence.
- **Prohibited shortcut:** updating metadata or action after insert to "fix" a prior event.

### 9.2 `AccessAuditLog`

```text
owner access decision / protected action outcome
  -> recordSensitiveAccess
  -> appended
  -> retained/queryable
```

There is no mutable status.

- **Transition owner:** Audit / Event Ledger for the evidence append only.
- **Trigger:** data/context owner has enough facts to state the access action/outcome.
- **Terminal state:** appended evidence.
- **Reversal/reopen:** none. A later action is another row.
- **Concurrency expectation:** legitimate simultaneous accesses produce separate rows.
- **Event/history proof:** the row itself is generic access proof; domain access records remain separate.
- **Prohibited shortcut:** using an `AccessAuditLog` row to infer that an access is currently authorized.

### 9.3 `AccessAuditAction`

This enum is not a lifecycle. It is an Audit-owned vocabulary.

Rules:

- callers use canonical values;
- source Modules retain the business meaning of the action;
- an action value does not replace a domain status;
- adding an action requires contract/schema tests and consumer review;
- do not introduce caller-local string actions that duplicate this enum.

### 9.4 Integrity lifecycle

No hash-chain lifecycle is currently binding.

If `PR-CL09-07` is accepted, a separate approved design must define:

- chain partition;
- atomic sequence/order;
- canonical field set;
- algorithm and version;
- anchor/head;
- verification frequency;
- integrity finding semantics;
- privacy/anonymization behavior;
- anomaly escalation.

Until then, `previousHash` and `entryHash` are optional integrity metadata only.

---

## 10. Commands

### 10.1 `appendAuditEvent`

**Purpose:** append generic proof that an important actor or system action occurred.

**Actor/context required:**
- trusted internal application call;
- authenticated User actor when one exists, or approved system context;
- request/correlation context.

**Authoritative inputs:**
- actor context;
- action;
- target/entity type;
- optional target/entity ID;
- outcome once `U-17` is resolved;
- request ID once `U-17` is resolved;
- minimized metadata.

**Preconditions:**
- caller is an approved internal caller;
- action and target shape are valid;
- metadata passes Audit payload policy;
- source Module has already made the business/compliance decision being recorded;
- if foreign target existence must be checked, use the target owner's public interface rather than direct Prisma.

**State written:** one `AuditEvent`.

**Shared operations consumed:**
- `resolveAuthenticatedActor` where a user actor is involved;
- `createRequestContext`;
- `sanitizeTelemetryMetadata`;
- `executeIdempotentCommand` only where the source command has a semantic retry identity that should not duplicate the audit record;
- `validateOwnedTargetReference` only where target existence/eligibility validation is required.

**Events/audit/notifications produced:** no automatic domain event merely because an AuditEvent was appended. Audit-write technical failure may be reported to Observability. Do not recursively append an AuditEvent about every AuditEvent.

**Idempotency expectations:**
- default behavior is append-per-fact;
- repeated legitimate facts must remain separate;
- when a source command retry would otherwise duplicate one evidence fact, use the canonical platform idempotency mechanism with source-defined semantic identity;
- do not create an Audit-local generic dedupe table.

**Failure modes:**
- invalid input;
- rejected metadata;
- unsupported/unapproved target namespace;
- unauthorized direct caller;
- persistence failure;
- unresolved schema contract (`U-17`) blocks final implementation.

### 10.2 `recordSensitiveAccess`

**Purpose:** append generic protected-access evidence.

**Actor/context required:**
- trusted internal caller;
- actor/system context;
- request/correlation context;
- data/context owner result.

**Authoritative inputs:**
- actor;
- `targetType`;
- `targetId`;
- `AccessAuditAction`;
- `DataSensitivity`;
- owner-provided access outcome/context;
- optional `HealthcareAccessDecision` when applicable;
- `requestId`;
- optional `ipHash`;
- optional `userAgent`;
- minimized metadata if the approved contract includes it.

**Preconditions:**
- source owner has already decided authorization/contextual access;
- action/sensitivity combination is valid;
- access-decision field is used only according to its owner semantics;
- payload contains no prohibited raw sensitive content.

**State written:** one `AccessAuditLog`.

**Shared operations consumed:**
- `createRequestContext`;
- `sanitizeTelemetryMetadata`;
- `resolveAuthenticatedActor` when appropriate;
- source Module's own authorization/context decision;
- conditional platform idempotency only for technical replay of the same evidence append.

**Events/audit/notifications produced:** none by default.

**Idempotency expectations:**
- separate access attempts remain separate rows;
- retries of the same access-recording command may replay only if the caller supplies an approved semantic idempotency identity;
- request ID alone must not be assumed to mean "duplicate" because one request can contain multiple protected access actions.

**Failure modes:**
- invalid action;
- invalid sensitivity/action combination;
- missing owner outcome where required;
- prohibited payload;
- persistence failure.

### 10.3 Privacy instruction execution

`executePrivacyInstruction` is not a general Audit mutation. It is a Privacy-owned protocol implemented by Audit for Audit-owned records.

It may:

- retain;
- anonymize;
- erase only where explicitly permitted;
- export;
- return manual-review/blocked result when retention or integrity policy is unresolved.

It must never create or transition `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, or `DataRetentionExemption`.

---

## 11. Queries / Decisions

### 11.1 `queryAuditEvents`

**Consumers:** authorized admin/compliance tooling and approved internal review services.

**Input:**
- bounded actor filter;
- action filter;
- entity type/ID;
- date range;
- request ID if `U-17` produces a first-class field;
- cursor/page size;
- viewer context.

**Result:** page of redacted `AuditEventView` DTOs.

**Type:** source evidence view.

**Consumer must not infer:**
- current target status;
- current authorization;
- current compliance readiness;
- provider processing state;
- that absence of an event proves an action did not occur unless the audited workflow contract explicitly guarantees completeness.

### 11.2 `querySensitiveAccessHistory`

**Consumers:** authorized admin/security/compliance tooling and approved source Modules.

**Input:**
- actor;
- target type/ID;
- `AccessAuditAction`;
- `DataSensitivity`;
- request ID;
- date range;
- bounded pagination;
- viewer context.

**Result:** page of redacted `AccessAuditView` DTOs.

**Type:** source evidence view.

**Consumer must not infer:**
- that a prior `allowed`/read event means access is currently allowed;
- that an access log replaces a resume/media/agreement/video domain access record;
- that a healthcare decision applies to non-healthcare policy.

### 11.3 `evaluateRetentionRequirement`

**Consumer:** Privacy / Data Erasure.

**Input:** subject/target reference, privacy instruction context, approved retention-policy version.

**Result:** owner fact describing whether the Audit record can be erased/anonymized/exported or requires retention/manual review.

**Type:** Module-owned retention fact consumed by Privacy.

**Boundary:** Privacy owns the resulting `DataRetentionExemption`. Audit does not create a local exemption record.

**Current status:** production behavior is blocked by `U-24` until retention target vocabulary and approved policy are supplied.

### 11.4 `enumerateSubjectData`

**Consumer:** Privacy / Data Erasure.

**Input:** privacy subject and approved target vocabulary/context.

**Result:** Audit-owned records linked to that subject through approved relationships.

**Type:** source-record inventory.

**Boundary:** do not build a universal polymorphic cross-domain crawler. Actor-linked records can be enumerated directly; target-linked subject meaning must use approved target vocabulary/mapping.

### 11.5 Integrity verification

A public or internal integrity query is **not** currently binding.

If `PR-CL09-07` is accepted, the Module may own a query such as `queryAuditIntegrityStatus` over an approved integrity model/result. Exact name, schema, and result are deferred until that ruling is accepted.

---

## 12. Public Module Interface

### Public commands

```text
appendAuditEvent(command) -> AuditEventReceipt
recordSensitiveAccess(command) -> AccessAuditReceipt
```

These are the canonical operations. Caller-specific aliases such as `recordFinancialSensitiveAccess`, `recordHealthcareAccess`, `writeAuditEvent`, or `appendSensitiveAccessLog` must not become independent public services.

### Public queries

```text
queryAuditEvents(filters, viewer) -> Page<AuditEventView>
querySensitiveAccessHistory(filters, viewer) -> Page<AccessAuditView>
```

Queries return redacted DTOs, never raw Prisma records.

### Emitted domain events

None are required in the baseline architecture merely because an audit row was appended.

If a later feature introduces an Audit-owned event, it must describe an Audit-owned fact and use the canonical outbox. It must not become a disguised command to another Module.

### Privacy executor

Audit implements Privacy-defined contracts:

```text
enumerateSubjectData(...)
evaluateRetentionRequirement(...)
executePrivacyInstruction(...)
exportSubjectData(...)   // only where Privacy's contract requires owner serialization
```

The exact privacy target vocabulary and retention policy remain subject to `U-24`.

### Provider-facing interfaces

None. Audit owns no provider adapter, webhook, provider credentials, or provider-event dedupe record.

---

## 13. Inbound Dependencies

| Owning Module / capability | Public operation / interface consumed | Why required | Minimum information needed | Can it block? | Must not be copied locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | `resolveAuthenticatedActor` | Trusted actor context for user-driven evidence and admin surfaces. | User ID/system context, assurance context where needed. | Yes for protected direct entry points. | Session parsing, current-user helper, MFA/passkey logic. |
| Role / Authority | `authorizeResourceAction` | Protect audit queries, admin viewer, and sensitive evidence access. | Actor, action, Audit resource/scope facts. | Yes. | Audit-local admin/role engine. |
| Identity & Access | `requireStepUpForSensitiveAction` | Fresh assurance for designated high-risk audit evidence review/export if policy requires it. | Actor, action, target, current assurance. | Yes. | Local OTP/MFA/passkey implementation. |
| Observability / platform | `createRequestContext` | Correlation across source action, Audit record, logs, and async work. | Request/correlation/trace IDs and safe actor/environment IDs. | Normally no; required correlation may be policy-dependent. | Audit-specific request-ID generator. |
| Observability + Audit payload policy | `sanitizeTelemetryMetadata` | Remove secrets and prohibited data before persistence. | Proposed metadata and sensitivity labels. | Yes when payload is unsafe. | Ad hoc redaction utilities. |
| Target owner | `validateOwnedTargetReference` or owner-specific fact query | Validate cross-Module target where the command contract requires it. | Target ID/type, safe status/version/relationship facts. | Yes if target is required. | Universal `findByTypeAndId` Prisma repository. |
| Privacy / Data Erasure | Privacy executor protocol | Execute Privacy-owned workflow instructions. | Request/job/target IDs, disposition, idempotency key, retention context. | Yes; only trusted Privacy orchestration may call it. | Local privacy request/job/exemption workflow. |
| Observability / Ops | `writeStructuredLog`, `captureException`, `recordIntegrationFailure` as appropriate | Diagnose technical Audit failures without converting them into audit truth. | Safe operation/error/request references. | Must not recursively fail the core path. | Audit-local logger, Sentry client, generic failure table. |
| Shared crypto | `hashCanonicalPayload` | Only if an approved Audit integrity or export-proof design needs canonical hashing. | Purpose/version + canonical bytes. | Only for integrity-enabled path. | Local SHA/HMAC implementation. |
| Shared queue | `enqueueReliableJob`, `executeRetryWithBackoff` | Only for approved Audit workers such as integrity verification. | Audit-owned job payload, correlation, retryability. | Worker-specific. | Audit-only queue runtime/retry loop. |

### Dependency rule

Audit may store a target reference, but it must not use that reference as permission to query or mutate the target owner's tables directly.

---

## 14. Outbound Consumers and Effects

### Major consumers

- Content Moderation & Legal Notice;
- Admin Review / Compliance Hold;
- Payment / Payout / Tax;
- Transaction / Order;
- Booking & Calendar;
- Job Interview;
- Candidate Application & Resume Privacy;
- Media / File Access;
- Video Infrastructure;
- Digital Goods Access;
- Messaging;
- Healthcare / Regulated Services;
- Identity & Access;
- Location Safety;
- Privacy / Data Erasure;
- other compliance-sensitive Modules.

### What consumers receive

Consumers receive:

- append receipts;
- redacted evidence query results;
- request-correlation references;
- privacy executor results.

They do not receive authority to mutate Audit tables directly.

### Downstream effects

Baseline Audit appends have no mandatory downstream side effect.

Possible effects:

- Observability receives technical Audit-write failures;
- Notification may receive an Audit-owned integrity alert only after integrity policy is approved;
- Privacy receives owner-local disposition results.

Audit never directly:

- changes Search;
- revokes Media;
- releases a Hold;
- changes Order/Booking/Agreement/Resume status;
- marks provider events processed;
- sends email/SMS/push.

---

## 15. Canonical Shared Operations Used

The current Canonical Shared Operations Architecture supplies canonical names rather than permanent numeric IDs. Do not invent `SH-###` identifiers in this document or code.

| Canonical operation | Classification | Owner | Why Audit uses it | Invocation point | Audit-local policy | Expected contract/result | Prohibited duplicate names |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Canonical shared capability | Identity & Access | Trusted actor context. | Protected command/query entry. | Which actor fields may be persisted. | Typed actor/system context. | `currentUser`, `auditActor`, `requireAuditUser`. |
| `authorizeResourceAction` | Canonical shared capability | Role / Authority | Gate audit evidence queries/admin actions. | Before protected read/admin action. | Audit action vocabulary and evidence scopes. | Allowed/denied decision with safe reasons. | `auditPermissions`, `isAuditAdmin`, `canViewLogs`. |
| `requireStepUpForSensitiveAction` | Canonical shared capability | Identity & Access | Fresh assurance for designated high-risk evidence access/export. | After authority, before high-risk action. | Which Audit actions require step-up. | Assurance satisfied or challenge required. | `auditMfa`, `verifyAdminOtp`. |
| `createRequestContext` | Platform primitive | Observability/platform | Request/correlation IDs. | Request/job entry; passed into append commands. | Safe propagation only. | Typed correlation context. | `auditRequestId`, `correlationHelper`. |
| `sanitizeTelemetryMetadata` | Canonical shared capability | Observability / Ops + Audit payload policy | Prevent sensitive payload leakage. | Before Audit persistence and operational telemetry. | Audit-specific allowlists and size limits. | Sanitized metadata or typed rejection. | `redactAuditJson`, `safeAuditMetadata`. |
| `writeStructuredLog` | Canonical shared capability | Observability / Ops | Diagnose execution. | Command/query/worker boundaries. | Safe dimensions only. | Operational log emission. | Audit-local logger. |
| `captureException` | Provider adapter | Observability / Ops | Send unexpected exceptions through one monitoring adapter. | Unexpected exception boundary. | Safe Audit operation context. | Monitoring reference/fallback behavior. | Direct Sentry client/init. |
| `executeIdempotentCommand` | Platform primitive | Platform application infrastructure | Replay a source command safely when duplicate Audit evidence would be a retry artifact. | Only where source-defined semantic identity exists. | Which repeats are retries versus separate facts. | Original result replay or conflict. | Audit idempotency table/helper. |
| `validateOwnedTargetReference` | Shared contract / separate implementations | Target owner | Validate a target without foreign Prisma access when required. | Before append only when contract requires target existence/eligibility. | Audit target namespace allowed for that command. | Safe target reference/version or not-found/forbidden. | Universal target repository. |
| `hashCanonicalPayload` | Platform primitive | Shared security/crypto | Canonical digest where an accepted integrity/export design requires it. | Conditional integrity/export path. | What the hash proves and canonical Audit fields. | Versioned digest. | `sha256Audit`, local crypto helper. |
| `hashChainRecords` | Proposed shared capability | Shared cryptographic capability; ownership unresolved | Potential tamper-evident AccessAuditLog chain. | **Do not invoke until `PR-CL09-07` is accepted.** | Chain partition, sequence, canonical fields, anomaly policy. | Approved chain append/verify result. | Local chain algorithm. |
| `enumerateSubjectData` | Another Module's public protocol | Audit as data owner under Privacy orchestration | Discover Audit-owned subject data. | Privacy job dispatch. | Audit relationship mapping. | Bounded target inventory. | Global DB crawler. |
| `evaluateRetentionRequirement` | Shared contract / separate policy | Audit + Privacy | Return Audit-specific retention fact. | Before Privacy disposition. | Security/legal proof rules. | Retain/anonymize/erase/export/manual-review fact. | Local exemption table. |
| `executePrivacyInstruction` | Another Module's public protocol | Privacy orchestrates; Audit executes | Apply approved disposition to Audit-owned data. | Privacy job target execution. | Field-level Audit behavior. | Typed privacy target result. | Local `PrivacyRequest` workflow. |
| `anonymizePersonalFields` | Platform/shared primitive | Shared mechanism; record owner supplies mapping | Approved pseudonymization. | Privacy executor only. | Which Audit fields may change without invalidating required proof. | Versioned anonymization result. | Ad hoc scrubber. |
| `enqueueReliableJob` | Platform primitive | Shared queue infrastructure | Run conditional integrity verification. | Only after approved worker exists. | Payload/completion meaning. | Durable job receipt. | Audit queue framework. |
| `executeRetryWithBackoff` | Platform primitive | Shared queue/platform | Retry transient worker failures. | Conditional Audit worker. | Retryability/anomaly handling. | Bounded retry/dead-letter result. | Local retry loop. |
| `recordIntegrationFailure` | Canonical shared capability | Observability / Ops | Surface technical Audit dependency/worker failure. | After normalized technical failure. | Source refs/retryability. | Operational failure receipt. | Audit generic failure table. |
| `requestNotification` | Canonical shared capability | Notification | Alert authorized recipients only for a confirmed Audit-owned trigger. | Conditional integrity/security alert. | Trigger severity and safe variables. | Notification request receipt. | Direct SES/SMS/push. |

---

## 16. Module-Internal Operations

### `validateAuditEventInput`

**Purpose:** validate the canonical generic-audit command against Audit-owned shape rules.

**Input:** actor/system context, action, target reference, request context, outcome, metadata.

**Output:** validated normalized append input or typed validation error.

**Source truth affected:** none directly.

**Why local:** the meaning of a valid `AuditEvent` payload belongs to Audit.

### `validateSensitiveAccessInput`

**Purpose:** verify action/sensitivity/decision/target/request shape for `AccessAuditLog`.

**Input:** canonical sensitive-access command.

**Output:** validated append input or typed error.

**Source truth affected:** none directly.

**Why local:** `AccessAuditAction` and generic sensitive-access evidence shape are Audit-owned.

### `applyAuditPayloadPolicy`

**Purpose:** enforce action-specific allowlists, prohibited keys, maximum sizes, and safe serialization.

**Input:** metadata + action/sensitivity/context.

**Output:** safe metadata or rejection.

**Source truth affected:** none until append.

**Why local:** shared sanitizer mechanics are reused, but Audit owns what is permitted in Audit evidence.

### `mapAuditEventView`

**Purpose:** convert owned rows into redacted public/admin DTOs.

**Input:** `AuditEvent` + viewer context/safe optional owner labels.

**Output:** `AuditEventView`.

**Why local:** Audit owns its evidence projection and disclosure shape.

### `mapAccessAuditView`

**Purpose:** convert `AccessAuditLog` into redacted evidence DTO.

**Input:** row + viewer context.

**Output:** `AccessAuditView`.

**Why local:** Audit owns the evidence disclosure shape.

### Conditional `verifyAuditIntegrity`

Exists only after `PR-CL09-07` is accepted.

It must use the shared crypto primitive rather than implement hashing locally.

---

## 17. Shared Mechanism / Separate Truth Rules

| Mechanism | Shared mechanism | Separate truth that remains outside Audit |
| --- | --- | --- |
| Append-only persistence | Shared insert-only repository conventions/DB enforcement. | `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `AgreementEvent`, `UserSecurityEvent`, `PointLedgerEntry`, `ResumeAccessLog`, `MediaAccessEvent`, etc. |
| Sensitive access evidence | `recordSensitiveAccess` is the generic cross-cutting proof rail. | Resume, Media, Agreement, Digital Download, Video, Location, and Security domain-specific proof records remain local where they exist. |
| Hashing | `hashCanonicalPayload` is shared crypto. | Agreement document hash meaning remains Transaction / Order; Audit integrity meaning remains Audit. |
| Hash chaining | Proposed `hashChainRecords` shared algorithm/plumbing. | Audit and Agreement chains, partitions, fields, retention, anomaly policy remain separate. |
| Idempotency | `executeIdempotentCommand`. | Each caller defines whether repeated action is the same fact or a new legitimate access. |
| Request correlation | `createRequestContext`. | Source business action and Audit evidence remain separate records. |
| Privacy executor | Privacy dispatch/result protocol. | Audit owns disposition of Audit fields; Privacy owns request/job/exemption lifecycle. |
| Target validation | `validateOwnedTargetReference` contract. | Target owner retains target lifecycle and access policy. |
| Operational failure | Observability failure rail. | Audit append failure does not become `AuditEvent` truth automatically, and Observability does not replace the failed Audit requirement. |

---

## 18. Authentication and Authorization

### Authenticated actor requirement

- Public clients do not receive a generic endpoint that can write arbitrary `AuditEvent` or `AccessAuditLog`.
- User-driven app operations resolve trusted actor context through `resolveAuthenticatedActor`.
- System/background actions require an approved trusted system context; nullable `actorUserId` does not mean anonymous public callers are allowed.

### Authorization

- The source Module authorizes the business action being audited.
- Audit does not re-decide the source business authorization.
- Audit-owned query/admin actions use `authorizeResourceAction`.
- Viewer authorization is server-side and must align with database/RLS policy where applicable.

### Contextual facts supplied by Audit

Audit may supply:

- evidence owner = Audit;
- target/entity reference;
- sensitivity;
- action;
- actor reference;
- date/request context.

It must not fabricate organization/participant/business ownership facts for Role / Authority.

### Admin/support actions

Admin/support ability does not imply unrestricted access to:

- PHI;
- financial details;
- resume contents;
- contracts;
- private messages;
- security/recovery data.

Audit viewer routes must return minimized/redacted DTOs. Sensitive source data remains behind the source owner's access interface.

### Step-up

`requireStepUpForSensitiveAction` may be required for high-risk audit export or evidence review when Identity/Security policy explicitly designates that action.

The exact step-up matrix is not currently supplied. Do not add Module-local MFA logic or assume every audit query requires step-up.

---

## 19. Compliance / Readiness / Entitlement Gates

Audit is an evidence Module, not a readiness composer.

### Relevant gates

| Audit action | Underlying truth owner | Query/gate consumed | Local Audit role | Result |
| --- | --- | --- | --- | --- |
| Protected audit viewer/query | Role / Authority | `authorizeResourceAction` | Define Audit resource/action facts and redaction. | Allow/deny query. |
| High-risk evidence review/export | Identity & Access | `requireStepUpForSensitiveAction` when policy says so | Identify the Audit action/target. | Proceed or step-up required. |
| Recording protected source access | Source data/context owner | Owner-specific authorization/context decision | Preserve the outcome; do not reinterpret it. | Append `AccessAuditLog`. |
| Privacy disposition | Privacy / Data Erasure + Audit retention fact | Privacy executor protocol | Execute only approved Audit-local disposition. | Privacy target result. |

### Not applicable as a generic Audit gate

- `resolveEntitlement`: no subscription entitlement is required to create compliance audit proof.
- `evaluateComplianceHold`: a hold does not normally prevent mandatory evidence from being written.
- financial/healthcare/professional readiness: Audit records their outcomes only where required.

If a future product requirement proposes hiding audit proof behind a commercial entitlement, it requires explicit architecture review.

---

## 20. Provider Integrations

Audit / Event Ledger owns no direct provider integration.

### Explicit prohibitions

Do not place these inside this Module:

- Sentry initialization/client;
- Stripe/webhook code;
- Cronofy/calendar webhook code;
- Mux/Daily/video provider code;
- Typesense client;
- Cloudflare R2 client;
- SES/SMS/push provider;
- background-check provider;
- generic webhook signature verification;
- provider event dedupe ledgers.

### Observability boundary

Audit uses Observability-owned:

- structured logging;
- exception capture;
- technical failure visibility.

Those providers are diagnostics and never replace Audit source records.

---

## 21. Events and Outbox

### Baseline event rule

An `AuditEvent` row is not automatically a domain event.

The baseline Module does not need to publish a new event every time evidence is appended. Doing so would create audit-of-audit loops and unnecessary event traffic.

### When an Audit-owned event could be justified

Only a new Audit-owned fact that other Modules must react to may justify a domain event, such as an accepted future integrity anomaly.

If introduced, it must use:

- `publishDomainEvent`;
- versioned envelope;
- source Module = Audit / Event Ledger;
- Audit aggregate/reference;
- correlation/causation IDs;
- minimized payload;
- consumer inbox/idempotency.

### Prohibited event uses

- events must not tell another Module to mutate its truth under the guise of an "audit event";
- provider callbacks are not Audit events;
- Audit must not republish every foreign domain lifecycle event.

---

## 22. Background Jobs / Scheduled Work

### Baseline

No Audit-owned recurring worker is required for the core append/query capability.

### Conditional integrity worker

Only if `PR-CL09-07` is accepted:

**Purpose:** verify an approved hash chain and identify altered/missing/reordered evidence.

**Input:** approved chain partition/range and integrity-policy version.

**Owner:** Audit / Event Ledger.

**Idempotency key:** approved partition + verification window/version.

**Retryable failures:** transient database/queue/telemetry failures.

**Permanent failures:** malformed historical record, unsupported chain version, cryptographic mismatch after deterministic recheck.

**Dead-letter/manual review:** permanent integrity anomaly or exhausted technical retry routes to approved security/compliance review.

**Business truth updated:** no foreign business truth. The worker may create an approved Audit integrity finding or operational signal only if that record/contract is explicitly approved.

**Operational telemetry:** Observability-owned logs/metrics/failure records.

### Generic queue rule

Use `enqueueReliableJob` and `executeRetryWithBackoff`. Do not create an Audit-specific queue runtime.

---

## 23. Concurrency and Idempotency

### Append races

Normal concurrent `AuditEvent` and `AccessAuditLog` inserts are allowed.

### Idempotency semantics

Do not globally deduplicate by:

- actor + action + target;
- request ID;
- timestamp bucket;
- metadata hash.

Those strategies could erase legitimate repeated access proof.

Use `executeIdempotentCommand` only when a source command supplies a semantic identity proving two attempts are retries of the same fact.

### Transaction boundary

At minimum:

1. validate/sanitize;
2. claim source-defined idempotency if applicable;
3. insert Audit evidence;
4. commit receipt.

The source Module determines whether Audit append must occur inside the same database transaction, through an outbox/after-commit path, or as a mandatory follow-up based on that workflow's legal/security criticality. Audit does not invent a universal cross-Module distributed transaction.

### Fail-closed semantics

For workflows where evidence is legally/security mandatory, the owner may require the protected action to fail closed when Audit persistence fails.

For lower-risk generic action proof, the owner may permit bounded recovery.

The action-by-action failure matrix is not globally defined and must be explicit in each owner integration.

### Hash-chain concurrency

If hash chaining is accepted:

- define a chain partition;
- define one atomic order/sequence;
- use database row/advisory lock or serializable transaction through `acquireAggregateLock`;
- do not use an in-memory mutex;
- allocate previous hash and new entry hash in the same protected transaction;
- define deterministic replay behavior.

Until then, no code may infer chain semantics from nullable hash fields.

---

## 24. Media / Storage

Audit owns no `MediaAsset`, upload context, file validation, malware scanning, object storage, or signed URL.

If an audit/admin workflow needs a protected file:

1. source/context owner decides business access;
2. Media / File Access validates the asset/grant;
3. Media issues short-lived access;
4. Audit records `recordSensitiveAccess` if required.

Audit metadata must contain references and minimized facts, not full file contents, full contracts, full resumes, images, or raw documents.

---

## 25. Search / Projection

- Audit records are not public Search source records.
- Audit owns no Typesense collection.
- Audit does not write `SearchUpsertEvent`.
- The admin audit viewer is an internal protected read surface, not Search / Public Visibility.
- Do not index sensitive audit metadata into a generic search engine for convenience.
- If internal query scale later requires a projection/search technology, that is a separate architecture decision with retention/security review.

---

## 26. Notification

Audit normally records evidence silently.

A Notification request is justified only for an Audit-owned trigger that requires human attention, such as an accepted future integrity anomaly.

Audit supplies:

- trigger meaning;
- safe recipient/context facts;
- priority/sensitivity;
- action route.

Notification owns:

- templates;
- recipient/channel routing;
- persistence;
- email/SMS/push provider;
- delivery attempts.

Audit must not instantiate notification providers.

---

## 27. Audit and Sensitive Access

This Module **is** the owner of generic Audit and sensitive-access proof, but must still preserve separation among four evidence classes:

| Evidence class | Owner | Example |
| --- | --- | --- |
| Generic important-action proof | Audit / Event Ledger | Admin released a hold; moderation reviewer made an action. |
| Generic sensitive-access proof | Audit / Event Ledger | Resume file was downloaded; PHI view was blocked; contract was viewed. |
| Domain lifecycle/history proof | Domain owner | `OrderEvent`, `AgreementEvent`, `UserSecurityEvent`, `JobInterviewEvent`. |
| Domain-specific access proof | Domain owner | `ResumeAccessLog`, `MediaAccessEvent`, `DigitalDownloadEvent`, video/access-grant history. |

One real-world operation may require both a domain-specific record and `AccessAuditLog`. That is shared mechanism / separate truth, not duplication.

---

## 28. Privacy and Retention

### Subject-data inventory

Audit-owned personal/sensitive references can include:

- `actorUserId`;
- `entityId` / `targetId` when they refer to a personal subject;
- `requestId`;
- `ipHash`;
- `userAgent`;
- metadata;
- sensitivity/action information that may reveal protected context.

### Privacy target executor

Audit must implement the Privacy owner protocol:

- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
- export serialization where Privacy requires it.

### Erase/anonymize/revoke/retain behavior

Current binding rules:

- do not erase the only proof that a privacy erasure occurred;
- do not hard-delete legal/security proof merely because a request exists;
- return retention facts to Privacy; Privacy owns `DataRetentionExemption`;
- do not create a local `retentionLocked` boolean as a substitute;
- do not use soft delete as legal erasure;
- normal app/admin roles remain unable to update/delete evidence.

### Current unresolved production policy

`U-24` must define:

- privacy target vocabulary for Audit records;
- which Audit records are subject data;
- retention durations/bases;
- which fields may be anonymized;
- when full erasure is permitted;
- export fields;
- how actor linkage is treated;
- how integrity metadata is handled if chaining is enabled.

### Append-only versus privacy mutation

Append-only means normal product/admin code cannot rewrite evidence.

A privileged Privacy executor is a different, explicitly controlled data-disposition path. It may mutate/anonymize only if approved retention/privacy policy says that doing so preserves required proof. If policy is unresolved, return retained/manual-review rather than silently editing evidence.

### Hash-chain privacy

If a hash chain is later enabled, privacy design must be approved before anonymizing any chained field. A chain cannot be declared valid after changing canonical fields unless the chain design explicitly supports that disposition.

---

## 29. Observability

Audit consumes Observability; it does not replace it.

### Structured logs

Use the canonical structured logger with:

- operation name;
- request/correlation ID;
- Audit evidence ID after commit;
- safe action/target namespace;
- success/failure category;
- duration.

Do not log Audit metadata payloads by default.

### Safe dimensions

Allowed operational dimensions should be low-cardinality and non-sensitive, such as:

- operation;
- evidence type;
- action category;
- success/failure class;
- environment;
- retry count.

Avoid target IDs, user IDs, full action metadata, private content, and raw user agents in metrics.

### IntegrationFailure/SystemEvent usage

Technical failures may be sent to Observability through its canonical interface. Audit must not create local `IntegrationFailure`, `SystemEvent`, `QueueJob`, or `OpsIncident` records.

### Correlation

`requestId`/correlation context should connect Audit to source execution and Observability without copying domain payloads.

### Recursion guard

Observability failures while recording an Audit failure must not recursively attempt infinite Audit/Observability writes. Bounded fallback behavior belongs to the Observability/platform design.

---

## 30. Security Boundaries

1. All command/query DTOs are schema validated.
2. Generic Audit writes are internal server capabilities, not arbitrary client-write endpoints.
3. Audit query/admin surfaces require server-side Role / Authority checks.
4. Step-up is used only where Identity policy explicitly requires it.
5. Metadata uses allowlists, prohibited-key detection, truncation/size limits, and safe serialization.
6. Never store:
   - plaintext OTPs;
   - passwords;
   - raw biometric images/templates;
   - raw identity documents;
   - card/payment credentials;
   - SSNs;
   - full background reports;
   - PHI payloads;
   - full resumes;
   - private message bodies;
   - complete contract/PDF content.
7. `ipHash` is a hash; raw IP should not be added by local convenience.
8. Hashing is integrity/provenance support, not encryption.
9. Audit owns no external-provider credentials.
10. Insert-only storage must be enforced at the database/application boundary, not by repository convention alone.
11. Admin viewer filters and pagination are bounded to prevent data scraping/DoS.
12. Not-found/forbidden behavior must avoid sensitive target enumeration.
13. Raw Prisma records must not cross the public Module interface.
14. Generic JSON metadata must never become an unbounded storage escape hatch.

---

## 31. Error / Decision Result Pattern

Audit public interfaces should return typed application results and stable error categories without leaking provider/database internals.

Recommended stable categories:

- `validation_error` — malformed/unsupported command or filter;
- `metadata_rejected` — prohibited or over-sized evidence payload;
- `unauthenticated` — protected entry point lacks trusted actor/system context;
- `forbidden` — viewer/caller lacks authority;
- `target_unavailable` — required owner target validation could not be safely completed;
- `conflict` — idempotency fingerprint or stale contract conflict;
- `persistence_unavailable` — evidence could not be committed;
- `retention_policy_unresolved` — Privacy disposition cannot proceed safely;
- `integrity_policy_unavailable` — caller requested chain semantics that are not approved;
- `internal_error` — sanitized unexpected failure.

### Receipt pattern

Successful append receipts contain:

- evidence ID;
- created timestamp;
- request/correlation reference when contract supports it.

They do not return raw database rows.

### Query pattern

Query results include:

- bounded page/cursor;
- redacted evidence DTOs;
- safe source references;
- no raw metadata unless explicitly authorized and DTO-approved.

---

## 32. Testing Architecture

### Domain/unit tests

- Audit payload allowlists and prohibited fields;
- size/truncation policy;
- `AccessAuditAction` compatibility;
- sensitivity/decision validation;
- DTO redaction;
- privacy field mapping once approved.

### Public contract tests

- `appendAuditEvent`;
- `recordSensitiveAccess`;
- `queryAuditEvents`;
- `querySensitiveAccessHistory`;
- Privacy executor contracts.

### Database/integration tests

- successful insert;
- query/index filters;
- normal app/admin update denied;
- normal app/admin delete denied;
- privileged repository exposes no normal update/delete method;
- migration safety for any `U-17` alignment change.

### Authorization tests

- protected query denied without permission;
- sensitive evidence not leaked through not-found/forbidden distinctions;
- step-up path tested where policy requires it.

### Compliance tests

Fixtures prove rejection of:

- PHI payload;
- raw resume text;
- full contract text;
- card data;
- OTP;
- biometric/raw ID document fields;
- secrets/credentials.

### Idempotency/concurrency tests

- legitimate repeated accesses produce separate evidence;
- source-command technical replay behaves according to explicit semantic identity;
- concurrent append does not corrupt records;
- conditional chain tests only after `PR-CL09-07`.

### Privacy tests

- subject enumeration;
- retention/manual-review result;
- approved anonymization/erase behavior;
- export minimization;
- no destruction of required erasure proof.

### E2E participation tests

At minimum:

- moderation admin action -> `AuditEvent`;
- ComplianceHold release -> `AuditEvent`;
- healthcare/financial/resume/media/contract protected access -> `AccessAuditLog`;
- protected admin viewer -> authority + access-audit behavior where required;
- privacy request -> Audit executor result.

### Provider adapter tests

Not applicable. Audit owns no provider adapter.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `AuditEvent` is generic action proof, not business lifecycle truth.
2. `AccessAuditLog` is generic sensitive-access proof, not authorization policy.
3. The source Module decides whether the business/compliance action is allowed.
4. Role / Authority owns permission interpretation.
5. Identity & Access owns authentication and step-up assurance.
6. Normal app/admin roles cannot update `AuditEvent` or `AccessAuditLog`.
7. Normal app/admin roles cannot delete `AuditEvent` or `AccessAuditLog`.
8. No generic update/delete repository method is exposed for Audit evidence.
9. Distinct legitimate accesses must not be deduplicated.
10. Source-command replay must use canonical idempotency rather than an Audit-local dedupe table.
11. `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `AgreementEvent`, and `UserSecurityEvent` remain domain-owned.
12. `ResumeAccessLog`, `MediaAccessEvent`, `DigitalDownloadEvent`, video access events, and similar domain access proof remain separate truth.
13. `ProcessedStripeEvent`, `ProcessedCalendarEvent`, video/subscription processed events remain provider-owner truth.
14. `SearchUpsertEvent` remains Search truth.
15. Operational failures remain Observability truth.
16. Audit metadata never contains secrets, PHI payloads, card data, OTPs, raw biometrics, raw identity documents, full resumes, private message bodies, or complete contract/PDF contents.
17. A target reference never grants direct foreign Prisma access.
18. Public Audit interfaces return DTOs, not Prisma models.
19. Request correlation uses the canonical request-context mechanism.
20. `AuditEventType` and `AuditEventActor` are not created until `U-16` is explicitly resolved.
21. The final `appendAuditEvent` contract is not implemented until `U-17` is resolved.
22. Optional `previousHash` / `entryHash` do not justify a tamper-evident-chain claim.
23. `hashChainRecords` is not used until `PR-CL09-07` is accepted.
24. Crypto algorithms are never implemented locally in Audit domain code.
25. Audit owns no Sentry, Stripe, Typesense, R2, notification, calendar, video, or webhook provider client.
26. Audit owns no `PrivacyRequest`, `DataErasureJob`, `DataRetentionExemption`, or Privacy orchestration.
27. Retention durations are not invented.
28. Anonymization/erasure does not proceed when required evidence integrity would be broken and policy is unresolved.
29. Admin/support role does not imply unrestricted sensitive evidence access.
30. Absence of an Audit record must not be interpreted as proof of absence unless the source workflow explicitly guarantees audit completeness.
31. Audit append failure is never silently converted to success.
32. Observability failure must not trigger recursive audit-failure loops.
33. Audit records are not public Search projections.
34. Audit does not send email/SMS/push directly.
35. Ghost-account analysis, if later approved, cannot delete/suspend/erase accounts directly.

---

## 34. Prohibited Duplicate Implementations

Do not create inside this Module:

- `current-user.ts`;
- `audit-actor.ts`;
- `require-audit-admin.ts`;
- `audit-permissions.ts`;
- `admin-auth.ts`;
- `audit-mfa.ts`;
- `audit-request-id.ts`;
- `correlation.ts`;
- local `structured-logger.ts`;
- local Sentry initialization/client;
- `redact-audit-json.ts` that duplicates canonical sanitization mechanics;
- `safe-json.ts` as a second generic sanitizer;
- local `idempotency.ts` / `processed-audit-event` table;
- `webhook-dedupe.ts`;
- `processed-webhook-event` generic ledger;
- `queue.service.ts`;
- local retry/backoff framework;
- `audit-lock.ts` or in-memory mutex;
- local SHA/HMAC implementation;
- local generic hash-chain algorithm;
- `audit-notification-service.ts`;
- direct SES/SMS/push code;
- `audit-search-indexer.ts`;
- Typesense client;
- R2/file storage client;
- local PrivacyRequest/retention-exemption tables;
- generic `event_log` table;
- copies of `OrderEvent`, `BookingEvent`, `JobInterviewEvent`, `AgreementEvent`, or `UserSecurityEvent`;
- PHI-specific, financial-specific, resume-specific, media-specific generic audit tables that duplicate `AccessAuditLog`;
- universal `findTargetByTypeAndId` cross-domain Prisma repository;
- Audit-owned operational incident/failure/queue tables.

---

## 35. Unresolved Decisions

| ID | Question | Why unresolved | What it blocks |
| --- | --- | --- | --- |
| `U-16` | Should `AuditEventType` and `AuditEventActor` exist? | Registry claims them; Prisma does not. Current canonical public operation does not require those exact schemas. | Any enum/schema migration claiming canonical audit type/actor vocabulary. |
| `U-17` | How should `appendAuditEvent` persist request ID and outcome? | Canonical Shared Operations require both; current `AuditEvent` lacks them. | Final command DTO/schema contract and request-correlation query behavior. |
| `U-18` / `PR-CL09-07` | What is the AccessAuditLog hash-chain partition, sequence, algorithm/version, anchor, verifier, and privacy policy? | Optional hash fields exist but no complete chain architecture exists. | Hash-chain implementation and tamper-evident-chain compliance claim. |
| `U-24` | Which Audit records are Privacy target types and what retention/anonymization durations apply? | Privacy target vocabulary and legal/security retention policy are incomplete. | Production privacy executor. |
| `AUD-U-01` | What is the approved action namespace governance for free-form `AuditEvent.action`? | Current schema is a string; registry claims absent controlled schemas. | Long-term prevention of action-name drift. |
| `AUD-U-02` | How are non-user actors represented in `AuditEvent` and `AccessAuditLog` beyond nullable `actorUserId`? | System/webhook/service actors are conceptually supported but no typed actor field is current. | Rich actor attribution without metadata conventions. |
| `AUD-U-03` | Which audit/admin actions require fresh step-up? | Identity capability exists, but Audit-specific matrix is not supplied. | High-risk export/evidence-view enforcement. |
| `AUD-U-04` | What is the exact fail-closed matrix when Audit persistence is unavailable? | Different source workflows have different legal/security criticality. | Per-consumer recovery policy. |
| `AUD-U-05` | What actor deletion/pseudonymization behavior is valid for `actorUserId` and its relation? | Privacy/retention requirements are unresolved; `AccessAuditLog` has a User relation while `AuditEvent` has only a scalar. | Account-erasure behavior and FK migration policy. |
| `AUD-U-06` | Should a durable audit evidence export manifest exist? | Admin viewer support is confirmed, but no Audit export source record is supplied. | Reproducible legal/security evidence bundles beyond query results. |
| `AUD-U-07` | How should generic `AccessAuditLog.accessDecision` evolve if non-healthcare decision outcomes need first-class representation? | Current field is specifically `HealthcareAccessDecision?`. | Any generalized decision-result persistence change. |
| `AUD-U-08` | What internal target namespace registry, if any, is needed for `entityType` / `targetType` strings? | Current schema is polymorphic strings; universal cross-domain repository is prohibited. | Stronger target validation without ownership leakage. |
| `AUD-U-09` | Is a durable Audit viewer projection necessary at scale? | Current requirement can be met through bounded owned queries; no projection schema is approved. | Future performance architecture only. |
| `AUD-U-10` | What exactly constitutes an actionable "ghost account" signal? | Registry contains a desire, but account lifecycle/removal ownership is external and no policy is supplied. | Any inactivity report beyond exploratory analytics. |

### Proposed Ruling: first-class correlation alignment

**PR-AUD-01 — Prefer first-class `AuditEvent` correlation/outcome fields over hiding canonical contract data in free-form metadata.**

Rationale: Canonical `appendAuditEvent` explicitly requires request ID and outcome, and request correlation is a cross-platform architectural primitive. If accepted, the exact field types, nullability, outcome vocabulary, indexes, migration/backfill, and compatibility behavior must be specified before schema change.

Status: **Proposed Ruling, not yet accepted.**

### Proposed Ruling: baseline integrity behavior

**PR-AUD-02 — Until `PR-CL09-07` is accepted, baseline code must not populate or interpret `previousHash`/`entryHash` as a complete chain and must not market/test the Module as hash-chain tamper-evident.**

This is a conservative implementation ruling derived from the current CL-09 architecture. Acceptance would make the baseline behavior explicit without deciding the eventual chain design.

Status: **Proposed Ruling, not yet accepted.**

---

## 36. Architecture Decision Summary

### Binding confirmed rulings

1. Audit / Event Ledger owns `AuditEvent`, `AccessAuditLog`, and `AccessAuditAction`.
2. `AuditEvent` is generic important-action proof.
3. `AccessAuditLog` is generic sensitive-access proof.
4. Both records are creation-only evidence with insert-only normal application/admin behavior.
5. `appendAuditEvent` and `recordSensitiveAccess` are the canonical public mutation contracts.
6. Domain lifecycle event ledgers remain with their parent Modules.
7. Domain-specific access records remain with their parent Modules even when generic `AccessAuditLog` is also required.
8. The source data/context owner makes authorization, sensitivity, healthcare, financial, entitlement, and business decisions.
9. Audit consumes Identity, Role / Authority, request context, Privacy, and other owner interfaces rather than duplicating them.
10. Metadata must be minimized and free of prohibited sensitive payloads.
11. Observability is separate from Audit truth.
12. Provider dedupe is separate from Audit truth.
13. Search is separate from Audit truth.
14. Privacy owns request/job/exemption orchestration; Audit implements only owner-local executor behavior.
15. No provider integration belongs inside this Module.
16. Normal app/admin roles must not update/delete Audit evidence.

### Binding conflict handling

17. Do not implement `AuditEventType` or `AuditEventActor` until `U-16` is resolved.
18. Do not finalize the canonical `appendAuditEvent` storage contract until `U-17` is resolved.
19. Do not implement hash chaining until `PR-CL09-07` and `U-18` are resolved.
20. Do not implement production Audit retention/anonymization durations until `U-24` is resolved.

### Implementation posture

The Module should be built as a narrow proof capability:

```text
trusted source fact
  -> canonical append command
  -> Audit-owned validation/minimization
  -> insert-only Audit source record
  -> protected evidence query
```

Anything that changes the source business object belongs outside this Module.

---

## 37. Coding-Agent Usage

Before implementing any Audit / Event Ledger feature, the coding agent must read, in order:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry / Architecture;
5. CL-09 `architecture.md`;
6. CL-09 `build-plan.md`;
7. this `module-architecture.md`;
8. this Module's `implementation-plan.md`;
9. public-interface sections for direct dependencies, especially:
   - Identity & Access;
   - Role / Authority;
   - Privacy / Data Erasure;
   - Observability / Ops;
   - Healthcare / Regulated Services;
   - Payment / Payout / Tax;
   - Transaction / Order;
   - Candidate Application & Resume Privacy;
   - Media / File Access;
   - Messaging;
   - Booking & Calendar;
   - Video Infrastructure;
   - Digital Goods Access;
10. the current Prisma schema and migration history;
11. the progress tracker and previous feature completion report.

Before coding, the agent must also:

- verify the prior Module feature exit gate;
- verify the corresponding CL-09 feature is ready under Cluster sequencing;
- check whether `U-16`, `U-17`, `U-18`, `U-24`, or any Module-local unresolved item blocks the work;
- refuse to implement an unaccepted Proposed Ruling;
- confirm all shared operations are imported from their canonical owner;
- confirm the feature writes only Audit-owned truth;
- record any new architecture conflict instead of resolving it by convenience.
