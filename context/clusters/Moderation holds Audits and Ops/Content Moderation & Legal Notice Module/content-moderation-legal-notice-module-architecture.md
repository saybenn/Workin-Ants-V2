# Content Moderation & Legal Notice Module Architecture

## 1. Module Header

| Item | Value |
| --- | --- |
| Module ID | `content_moderation_legal_notice` |
| Module name | Content Moderation & Legal Notice Module |
| Module type | `compliance_ops` |
| Build status | `mvp_active_legal_gated` |
| Primary Cluster | `CL-09` — Moderation, Holds, Audit & Ops |
| Document status | Implementation-grade Module architecture synthesized from current Workin Ants evidence |
| Intended audience | Coding agents, developers, reviewers, maintainers, compliance/legal-policy reviewers, and architecture owners |
| Relationship to root architecture | Subordinate to Workin Ants root architecture, project overview, code standards, and canonical source-of-truth rules. This document may narrow but must not contradict them. |
| Relationship to Cluster architecture | Subordinate to CL-09 architecture. The Cluster coordinates collaboration; this Module alone owns its moderation/legal-notice truth. |
| Update rule | Update when ownership, model meaning, lifecycle rules, public contracts, evidence/retention policy, shared-operation usage, or a previously unresolved/proposed ruling becomes binding. Build progress must not silently redefine this file. |

### Evidence basis and precedence

This document is grounded in the current supplied:

1. Deep Module Registry;
2. Prisma schema;
3. Ubiquitous Language / Compliance Inventory;
4. Canonical Shared Operations Architecture;
5. CL-09 `architecture.md`;
6. CL-09 `build-plan.md`;
7. Workin Ants project overview;
8. the standardized Module Architecture Extract already produced for this Module.

Where these conflict, concrete current Prisma evidence controls model/enum facts, Module/Glossary evidence controls domain meaning, the Canonical Shared Operations registry controls anti-duplication/shared-capability boundaries, and Cluster documents control sequencing/collaboration without taking Module ownership.

### Current evidence correction

The earlier CL-09 snapshot recorded `U-01` as an unresolved bad Prisma mapping for `ModerationTargetType`; CL-09-R017 corrects that Cluster snapshot. The **current supplied Prisma schema no longer contains that defect**: `ModerationTargetType` maps to `moderation_target_type`. The current enum also includes `media_access_grant`, which the earlier Cluster enum snapshot omitted.

**Binding for this document:** use the current supplied Prisma definition. Before any migration that touches this enum, verify migration/database history so an old deployed mapping is not mistaken for current architecture. `U-01` is therefore no longer a Module architecture design blocker, but database migration compatibility still must be checked.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the structured platform truth for:

- user/admin/rights-holder reports;
- formal legal or legal-adjacent notices;
- DMCA takedown and counter-notice records;
- DSA/illegal-content notice handling;
- moderation case review;
- moderation/legal decisions recorded as actions;
- content freeze/hide/restore decisions;
- requests for public URL removal and downstream access restriction;
- the moderation/legal workflow that coordinates those effects.

### Goal

Turn an allegation, formal notice, or administrative concern into a traceable, reviewable, evidence-preserving decision and coordinated enforcement/restoration request without absorbing the target object's lifecycle or the infrastructure that executes the effect.

### What enters

- authenticated or controlled-external actor context;
- `ReportSource`, `ReportReason`, or `LegalNoticeType`;
- typed target reference: `ModerationTargetType` + target UUID;
- safe report details, URL references, statements, and evidence references;
- target-owner facts required to validate and review the target;
- moderator/legal-reviewer decisions;
- downstream execution acknowledgments when orchestration is enabled;
- privacy instructions from Privacy / Data Erasure.

### What leaves

- `Report`;
- `LegalNotice`;
- `ModerationCase`;
- append-style `ModerationAction`;
- safe report/legal/case status results;
- active-moderation restriction decisions;
- domain events/outbox messages describing facts that occurred;
- requests to target owners for hide/freeze/restore/access effects;
- Search projection-refresh requests;
- ComplianceHold requests when a reusable stop sign is needed;
- Notification requests;
- Audit / sensitive-access evidence requests;
- privacy executor results;
- operational failure/queue telemetry requests when technical execution fails.

### Transformation

```text
Allegation / formal notice / admin concern
    -> validate actor or controlled intake
    -> validate target through owner contract
    -> create Report or LegalNotice truth
    -> triage / open ModerationCase
    -> obtain minimized target facts and protected evidence
    -> preserve evidence where policy requires
    -> record ModerationAction decision
    -> dispatch owner-local effects through public contracts
    -> reconcile acknowledgments if approved orchestration exists
    -> notify / audit / observe
    -> restore or close under approved policy
```

### Why this deserves its own Module boundary

A `Report`, `LegalNotice`, `ModerationCase`, and `ModerationAction` have legal/compliance meaning that must not be spread across Media, Search, Marketplace, Messaging, Digital Goods, Video, Payment, or generic admin code. Centralizing moderation/legal decision truth here prevents downstream status fields or provider actions from becoming accidental legal truth while still preserving one-owner-per-lifecycle boundaries.

---

## 3. Owned Truth

### Owned Prisma models

| Record | Plain-English meaning | Source-of-truth rule |
| --- | --- | --- |
| `Report` | A user/admin/rights-holder/system/law-enforcement flag against a platform object. | `Report.status` is report-intake truth. It is not automatically a formal legal notice. |
| `LegalNotice` | A formal legal/legal-adjacent notice such as DMCA takedown, DMCA counter-notice, DSA notice, law-enforcement request, or copyright-owner notice. | `LegalNotice.status` is formal notice workflow truth. Email receipt or target disablement is not a substitute. |
| `ModerationCase` | The review container opened from a report, legal notice, or admin concern. | `ModerationCase.status` is moderation/legal review-container truth. It is not a `Dispute`, `ComplianceHold`, or generic support ticket. |
| `ModerationAction` | An immutable/append-style record of a specific moderation or legal decision/action. | `ModerationAction.type` records what was decided/requested. It does **not** prove downstream execution succeeded. |

### Owned enums/status vocabularies

- `ReportReason`
- `ReportStatus`
- `ReportSource`
- `LegalNoticeType`
- `LegalNoticeStatus`
- `ModerationCaseStatus`
- `ModerationActionType`
- `ModerationTargetType`

### Current executable enum values

**`ReportReason`**

`copyright`, `illegal_content`, `counterfeit`, `fraud`, `spam`, `harassment`, `health_safety`, `child_safety`, `terrorism`, `privacy_violation`, `other`

**`ReportSource`**

`user`, `rights_holder`, `trusted_flagger`, `admin`, `system`, `law_enforcement`

**`ReportStatus`**

`submitted`, `triaged`, `under_review`, `action_taken`, `dismissed`, `closed`

**`LegalNoticeType`**

`dmca_takedown`, `dmca_counter_notice`, `dsa_notice`, `law_enforcement`, `copyright_owner_notice`, `other`

**`LegalNoticeStatus`**

`received`, `validating`, `valid`, `invalid`, `action_taken`, `counter_notice_received`, `restored`, `rejected`, `closed`

**`ModerationCaseStatus`**

`opened`, `triaged`, `under_review`, `waiting_for_counter_notice`, `escalated`, `action_taken`, `dismissed`, `closed`

**`ModerationActionType`**

`hide`, `unhide`, `freeze_content`, `archive_content`, `remove_public_url`, `restore`, `suspend_profile`, `pause_payout`, `freeze_order`, `apply_takedown`, `reject_takedown`, `accept_counter_notice`, `escalate_to_legal`, `disable_digital_access`, `restore_digital_access`, `revoke_download_grants`, `disable_course_playback`

**`ModerationTargetType`**

`user`, `professional_profile`, `candidate_profile`, `organization`, `offering`, `course_details`, `product_details`, `media_asset`, `message`, `thread`, `gig`, `job`, `review`, `digital_download_asset`, `course_video_asset`, `course_accessibility_asset`, `media_upload_session`, `media_access_grant`

### Lifecycles owned

- Report lifecycle.
- LegalNotice lifecycle.
- ModerationCase lifecycle.
- ModerationAction creation/history semantics.

The Module owns transition policy for the first three. `ModerationAction` is creation-only in the current schema.

### Domain events/ledgers owned

There is no dedicated moderation event-ledger table in the current Prisma schema. `ModerationAction` is domain action truth, not a generic audit ledger.

The Module owns the meaning and emission conditions of event classes such as:

- report submitted;
- legal notice received;
- case opened/assigned/transitioned;
- moderation action recorded;
- restriction changed/restoration decided.

Exact serialized event names and versions are not yet binding and must be specified with the transactional outbox implementation.

### Projections owned

No durable search/public projection is owned here.

The Module may expose query projections:

- `listModerationQueue`;
- redacted `getModerationCase` view;
- `queryActiveModerationRestriction`.

Those projections are derived from this Module's source truth plus owner-supplied target summaries. They do not create a new lifecycle.

### Snapshots/proof owned

Current source truth contains report/legal details and JSON evidence fields, but **no immutable moderation evidence snapshot record exists**.

- `Report.evidenceJson` is intake metadata, not immutable evidence proof.
- `LegalNotice.statementJson` is notice statement data, not immutable captured-target proof.
- A Moderation-owned evidence snapshot/reference is a **Proposed Ruling** (`PR-CL09-02`), backed by Media bytes and shared hashing.
- Generic `AuditEvent` must not be used as a substitute for the missing snapshot.

### Policies/invariants owned

This Module owns:

- report reason/source/target compatibility;
- which target types are reportable;
- legal-notice structural intake requirements;
- report/case/notice transition rules once explicitly approved;
- which moderation actions are valid for which target classes;
- which decisions require evidence preservation before dispatch;
- the distinction between decision truth and downstream execution truth;
- active moderation restriction composition;
- counter-notice/restoration decision policy once approved;
- repeat-infringer policy only after its currently missing truth/policy is explicitly designed.

---

## 4. Explicit Non-Ownership

| Adjacent owner | This Module must not own |
| --- | --- |
| Identity & Access | Authentication, session identity, MFA/passkeys, step-up challenge/session lifecycle. |
| Role / Authority | Generic permission interpretation, organization/thread/ownership access engine. |
| Admin Review / Compliance Hold | `ComplianceHold` lifecycle, hold reason/status truth, release truth, generic stop-sign policy. |
| Audit / Event Ledger | Generic `AuditEvent`, `AccessAuditLog`, append-only audit infrastructure, generic sensitive-access evidence. |
| Observability / Ops | Generic integration failures, queue telemetry, incident state, logging/metrics/error-provider integration. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense clients, index/de-index execution, search reconciliation. |
| Media / File Access | `MediaAsset`, R2/file storage, file freeze mechanics, public URL revocation mechanics, signed URLs, generic MediaAccessGrant lifecycle, file scan/processing. |
| Notification | Notification records, templates/channel rendering, SES/SMS/push/provider delivery, delivery attempts. |
| Messaging | `Thread`, `ThreadParticipant`, `Message`, message deletion/restriction execution. |
| Marketplace Supply | `Offering`, `CourseDetails`, `ProductDetails`, their statuses and publish/disable execution. |
| Gig / Demand | `Gig`, `GigResponse`, `GigAssignment` lifecycle. |
| Organization Hiring | `Organization`, `Job`, organization/job lifecycle. |
| Candidate Application & Resume Privacy | Candidate/resume application truth and resume-access proof. |
| Review / Dispute | `Review` lifecycle and Order `Dispute` lifecycle. A dispute is not a ModerationCase. |
| Transaction / Order | `Order`, `OrderEvent`, `RefundStatus`, agreement truth. |
| Payment / Payout / Tax | Payout readiness, `PayoutTransfer`, provider financial state. A moderation payout pause must use the Hold interface. |
| Digital Goods Access | `DigitalDownloadAsset`, `DigitalDownloadGrant`, download events, actual digital-access disable/revoke/restore execution. |
| Video Infrastructure | `CourseVideoAsset`, `CourseVideoPlaybackGrant`, provider playback disable/revoke/restore execution. |
| Privacy / Data Erasure | `PrivacyRequest`, `DataErasureJob`, `DataErasureTarget`, `DataRetentionExemption`, export orchestration. |
| Legal counsel/policy owner | Legal advice, invented statutory deadlines, jurisdiction-specific sufficiency rules, retention durations, repeat-infringer thresholds. |

### Concrete anti-leak rule

Referencing another Module's schema in a case, action, or query never authorizes direct Prisma access or mutation of that schema. Cross-Module reads and writes use the owner interface or an explicitly approved event/protocol.

---

## 5. Module Architecture Principles

1. Report truth, formal legal-notice truth, case truth, and action truth remain distinct.
2. LegalNotice is legal-workflow truth; downstream disable/hide states are execution/projection state.
3. Moderation decides; target owners execute their own state changes.
4. Preserve required evidence before destructive or public-removal effects.
5. Do not delete accused content merely because it was reported; deletion requires an explicit approved legal/admin decision.
6. `ModerationAction` is immutable decision history; reversal/restoration adds later truth rather than rewriting the original row.
7. `ComplianceHold` is the reusable stop sign; no moderation-local `isBlocked` or payout block field.
8. Search is projection; request Search work, never write Search state.
9. Media owns file mechanics; request Media work, never call R2 directly.
10. Notification owns delivery; request messages, never send email/SMS/push directly.
11. Audit records proof; it does not replace moderation truth.
12. Observability records technical failure; it does not change legal/moderation state.
13. Privacy orchestrates erasure/export; this Module only enumerates and executes its own data instructions.
14. External provider/webhook logic stays with the provider-owning Module.
15. Legal-gated policy is versioned/approved or remains disabled/unresolved; it is never guessed from enum order or internet knowledge.
16. Current schema is the executable record of current model/enum facts; stale Cluster snapshots do not override it.
17. Shared mechanism may be reused without merging domain truth.

---

## 6. Proposed Folder / Code Structure

The exact repository prefix follows root `code-standards.md`. Relative Module shape:

```text
<module-root>/content-moderation-legal-notice/
  domain/
    report/
      report-policy.ts
      report-transitions.ts
    legal-notice/
      legal-notice-policy.ts
      legal-notice-transitions.ts
    moderation-case/
      case-policy.ts
      case-transitions.ts
      restriction-policy.ts
    moderation-action/
      action-policy.ts
      enforcement-plan.ts
    evidence/
      evidence-policy.ts
    policies/
      target-action-policy.ts

  application/
    commands/
      submit-moderation-report.ts
      submit-legal-notice.ts
      triage-report.ts
      open-moderation-case.ts
      assign-moderation-case.ts
      record-moderation-action.ts
      process-counter-notice.ts
      restore-moderated-content.ts
    queries/
      get-report-status.ts
      get-legal-notice-status.ts
      get-moderation-case.ts
      list-moderation-queue.ts
      query-active-moderation-restriction.ts
    orchestration/
      moderation-enforcement.ts
      restoration-orchestration.ts

  public/
    commands.ts
    queries.ts
    contracts.ts
    events.ts
    privacy.ts

  infrastructure/
    repositories/
      report-repository.ts
      legal-notice-repository.ts
      moderation-case-repository.ts
      moderation-action-repository.ts

  workers/
    moderation-enforcement-worker.ts
    moderation-reconciliation-worker.ts
    legal-deadline-worker.ts

  ui/
    report-intake/
    legal-notice-intake/
    admin/

  tests/
    unit/
    integration/
    contract/
    e2e/
```

### Conditional folders

- `evidence/` exists for policy and Moderation-owned evidence-reference meaning; it does not store file bytes or implement R2.
- No `providers/` folder is required because this Module owns no direct provider integration.
- No local `shared/`, `utils/`, `auth/`, `search/`, `storage/`, `notifications/`, `queue/`, `audit/`, or `privacy-request/` infrastructure folders.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / UI | Report/legal intake forms, moderation case/reviewer surfaces, safe status views. | Business rules, direct Prisma, target-owner data access, provider clients. |
| Application commands | Command validation, orchestration order, owner-repository transaction boundaries, shared-operation calls. | Generic auth, generic queue, Search/R2/email execution. |
| Application queries | Safe DTO composition from Module truth and owner-supplied target summaries. | Universal cross-domain joins/repositories. |
| Domain policy | Report/legal/case/action compatibility, transition rules, evidence-required matrix, restriction decision. | Identity permission policy, hold policy, file mechanics, search ranking. |
| Repositories | Direct Prisma access only to `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction`. | Foreign Module table writes/joins as convenience. |
| Workers | Moderation-owned enforcement/reconciliation/deadline workflow meaning. | Generic queue runtime/retry framework; target-owner execution logic. |
| Adapters | None directly owned for R2, Typesense, SES/SMS/push, payment, video. | Provider credentials/SDKs for neighboring Modules. |
| Public contracts | Stable moderation commands, queries, execution protocol, event shapes, privacy executor. | Leaking Prisma records/provider payloads. |
| Evidence policy | What must be preserved and what legal meaning the snapshot/reference carries. | File bytes/storage/signing mechanics, generic AuditEvent. |

---

## 8. Data Model

### `Report`

**Purpose:** intake truth for a report against a typed platform target.

**Key fields**

- `reporterUserId?`
- `source`
- `targetType`
- `targetId`
- `reason`
- `details?`
- `reportedUrl?`
- `evidenceJson?`
- `status`
- timestamps

**Relationships**

- optional reporter `User`;
- zero-to-many `ModerationCase` relations through `ModerationCase.reportId`.

**Authoritative fields**

`source`, `targetType`, `targetId`, `reason`, `status`.

**Lifecycle field**

`status: ReportStatus`.

**Constraints/indexes**

- no semantic uniqueness constraint;
- indexes by reporter/time, target, reason/status, source/status.

**Concurrency-sensitive**

`updatedAt` may be used as the expected-version token through SH-052 `withOptimisticConcurrency`; no explicit version column exists.

**Retention/privacy**

Contains reporter linkage, free-text details, URL and JSON evidence metadata. Do not copy prohibited sensitive payloads. Retention/anonymization is unresolved until Privacy target vocabulary/policy is approved.

### `LegalNotice`

**Purpose:** formal legal/legal-adjacent notice truth.

**Key fields**

- `moderationCaseId?`
- `type`
- `status`
- `targetType`
- `targetId`
- submitter name/email
- rights-owner name
- claimed work
- infringing URL
- `statementJson?`
- details
- `receivedAt`
- `actionDueAt?`

**Relationships**

Optional relation to one `ModerationCase`.

**Authoritative fields**

`type`, `status`, `targetType`, `targetId`, notice/claim fields, `receivedAt`.

**Lifecycle field**

`status: LegalNoticeStatus`.

**Constraints/indexes**

No uniqueness or explicit parent/counter-notice relation. Indexed by type/received time, status, target, case.

**Concurrency-sensitive**

`updatedAt` is the available optimistic token.

**Retention/privacy**

Contains personal contact information and potentially sensitive legal statements. Legal retention duration and counter-notice correspondence policy are unresolved.

### `ModerationCase`

**Purpose:** review container for a report, notice, or admin concern.

**Key fields**

- `reportId?`
- `targetType`
- `targetId`
- `status`
- `openedByUserId?`
- `assignedAdminUserId?`
- `summary?`
- `resolutionNote?`
- `openedAt`
- `closedAt?`

**Relationships**

- optional triggering `Report`;
- zero-to-many `LegalNotice`;
- zero-to-many `ModerationAction`;
- optional opener and assignee Users.

**Authoritative fields**

Target, status, opener/assignment, summary/resolution, timestamps.

**Lifecycle field**

`status: ModerationCaseStatus`.

**Cardinality concern**

Current schema supports one optional `reportId` per case. Whether a case may aggregate multiple reports is unresolved (`U-03`). Do not add a join model without a ruling.

**Concurrency-sensitive**

Reviewer assignment and lifecycle transitions. Use optimistic concurrency/aggregate lock as needed; do not use in-memory locks.

**Retention/privacy**

Case summaries may contain legal/sensitive facts. Query views must minimize and redact.

### `ModerationAction`

**Purpose:** append-style record of an approved moderation/legal decision/action.

**Key fields**

- `moderationCaseId`
- `actorUserId?`
- `type`
- `targetType`
- `targetId`
- `note?`
- `createdAt`

**Relationships**

Belongs to `ModerationCase` and optional actor User.

**Authoritative fields**

Case, actor, type, target, note, creation time.

**Lifecycle/status**

None. It is creation-only evidence/truth.

**Important constraint**

The relation currently uses `onDelete: Cascade` from `ModerationCase`. **CL-09-R009 — Retained decision proof.** A retained `ModerationAction` must not be destroyed merely because its parent `ModerationCase` is hard-deleted. Current cascade behavior is architecturally invalid for retained actions. A later schema correction must preserve required decision proof; the replacement FK/deletion strategy remains unresolved. Privacy erasure uses approved owner-local anonymization/retention disposition, never accidental cascade. Normal application code must not expose a case deletion path that removes retained actions. No replacement FK strategy is selected in this pass.

**Execution boundary**

No field records pending/acknowledged/completed/failed/restored downstream effects. That is why `PR-CL09-03` exists.

### Target representation

All owned records use `ModerationTargetType + targetId(UUID)`. This provides typing but not foreign-key validation. Every cross-Module target must be validated through the target owner before a protected mutation or effect.

### Current no-schema facts

No current model exists for:

- immutable moderation evidence snapshot;
- moderation enforcement run/step correlation;
- repeat-infringer decision/signal;
- content fingerprint/similarity signal;
- legal correspondence timeline;
- legal notice validation result/policy version;
- multi-report case join.

These remain proposed/unresolved, not implied implementation permission.

---

## 9. Enums, Statuses, and Lifecycles

### Report lifecycle

**Statuses:** `submitted`, `triaged`, `under_review`, `action_taken`, `dismissed`, `closed`

**Transition owner:** Content Moderation & Legal Notice.

**Triggers:** report intake, reviewer triage, case review, recorded action, dismissal/closure.

**Terminal states:** not fully specified by authoritative evidence.

**Reopen/reversal:** unresolved.

**Concurrency:** all updates require expected current state and preferably `updatedAt` optimistic concurrency; conflicting reviewer changes return a typed conflict.

**History proof:** generic audit may record reviewer actions, but `Report.status` remains truth.

**Valid transitions:** **unresolved beyond the existence of the vocabulary.** Do not infer enum order. A binding transition matrix must be approved before implementation of each mutation.

### LegalNotice lifecycle

**Statuses:** `received`, `validating`, `valid`, `invalid`, `action_taken`, `counter_notice_received`, `restored`, `rejected`, `closed`

**Transition owner:** Content Moderation & Legal Notice under approved legal-policy rules.

**Triggers:** intake, structural/legal validation, action decision, counter-notice, restoration/rejection, closure.

**Terminal/reopen rules:** unresolved.

**Deadlines:** `actionDueAt` exists, but calculation/expiry behavior is unresolved (`U-25`).

**History proof:** actions and audit evidence; exact legal-policy version storage is unresolved (`U-05`).

**Valid transitions:** not fully defined. No worker or command may infer a legal transition from enum order.

### ModerationCase lifecycle

**Statuses:** `opened`, `triaged`, `under_review`, `waiting_for_counter_notice`, `escalated`, `action_taken`, `dismissed`, `closed`

**Transition owner:** Content Moderation & Legal Notice.

**Triggers:** case opening, assignment/triage, review, counter-notice waiting state, legal escalation, action, dismissal/close.

**Reopen/reversal:** unresolved.

**Concurrency:** stale transition must fail; assignment/action races require DB-backed coordination.

**History proof:** `ModerationAction` and generic AuditEvent; case state remains source truth.

**Valid transitions:** incomplete in current evidence and must be approved before coding.

### ModerationAction history

```text
decision recorded
    -> immutable historical row
    -> downstream effect dispatched separately
    -> reversal/restoration = later ModerationAction
```

Never update an earlier action to pretend it did not occur.

### Prohibited lifecycle shortcuts

- `isModerated` boolean as source truth.
- `isDmca` boolean as legal truth.
- Search removal as proof that a notice is valid.
- Media freeze as proof that a case is `action_taken`.
- Notification delivery as proof of legal receipt or workflow completion.
- `ComplianceHold` status as proof of moderation case status.
- Observability job status as moderation workflow truth.

---

## 10. Commands

### SH-101 `submitModerationReport`

**Purpose:** create `Report` truth.

**Actor/context:** authenticated actor when source requires it; controlled system/external path only under approved intake policy.

**Inputs:** source, typed target, reason, safe details/URL/evidence refs, idempotency key.

**Preconditions**

- supported source/reason;
- target validated through owner contract;
- input size/rate limits;
- actor/source compatibility.

**Writes:** `Report`.

**Shared operations:** SH-001 `resolveAuthenticatedActor`, SH-002 `authorizeResourceAction` where required, SH-123 `validateOwnedTargetReference`, SH-044 `executeIdempotentCommand`, optional SH-046 `publishDomainEvent`, SH-029 `appendAuditEvent`, SH-032 `createRequestContext`.

**Effects:** optional receipt notification and report-submitted event.

**Idempotency:** same key + same fingerprint replays original result; same key + different fingerprint conflicts.

**Failure modes:** validation denial, unsupported target, authorization denial, owner unavailable, idempotency conflict.

### `submitLegalNotice`

**Purpose:** create formal `LegalNotice` truth.

**Actor/context:** controlled legal intake/admin. The schema supports external submitter fields and does not require a submitter User.

**Inputs:** notice type, target, submitter/rights-owner fields, claimed work, infringing URL, statement/evidence refs.

**Preconditions:** structural validation, target validation, anti-abuse controls; legal sufficiency is not assumed unless approved policy exists.

**Writes:** `LegalNotice(received)`.

**Shared operations:** target validation, idempotency, request context, optional audit/notification/event.

**Failure modes:** malformed notice, unsupported target, ambiguous/replayed intake, dependency unavailable.

### `triageReport`

**Purpose:** move report through approved triage policy.

**Actor:** authorized reviewer/admin.

**Inputs:** report ID, triage decision/note, expected version.

**Writes:** `Report.status` and safe triage fields only if schema/approved command supports them.

**Shared operations:** actor, authority, lifecycle transition, optimistic concurrency, audit.

**Failure modes:** stale state, unauthorized reviewer, invalid transition.

### `openModerationCase`

**Purpose:** create review container.

**Inputs:** trigger report/notice/admin concern, typed target, opener, summary, idempotency key.

**Writes:** `ModerationCase`.

**Preconditions:** target agreement with trigger, no disallowed duplicate under approved policy.

**Shared operations:** target validation, idempotency, lifecycle helper, audit/event.

### `assignModerationCase`

**Purpose:** assign the existing `assignedAdminUserId`.

**Inputs:** case ID, assignee, assigning actor, expected version.

**Writes:** `ModerationCase.assignedAdminUserId`.

**Preconditions:** reviewer eligibility/authority. Do not imply lease/claim semantics beyond the existing field unless SH-054 `claimWorkItem` is approved.

### `recordModerationAction`

**Purpose:** persist approved decision/action after required evidence and policy gates.

**Inputs:** case, actor, action type, target, rationale/reference, expected case/target version, evidence proof reference if required.

**Writes:** append `ModerationAction`; allowed case/report/notice transitions in same owner transaction where defined.

**Shared operations:** authority, step-up if designated, evidence snapshot mechanism if approved, hash primitive, lifecycle transition, optimistic concurrency/lock, audit, event/outbox.

**Invariant:** downstream owner state is not written in this transaction.

### `processCounterNotice`

**Purpose:** process a counter-notice under approved relationship and legal policy.

**Status:** internal command; production behavior partially blocked by unresolved linkage/legal policy.

**Writes:** legal notice/case states and later action decisions only under approved transition rules.

**Failure modes:** ambiguous original notice, unapproved legal rule, stale case.

### `restoreModeratedContent`

**Purpose:** record restoration decision and dispatch restoration effects.

**Writes:** a new `ModerationAction` plus allowed case/notice transitions.

**Invariant:** never mutate/delete prior takedown action history.

### `dispatchModerationEnforcement`

**Purpose:** orchestrate owner-local effects after a recorded action.

**Status:** application/orchestration command, not direct target mutation.

**Dependency:** requires accepted enforcement-correlation design for durable multi-step production execution.

**CL-09-R007 — Primary target versus downstream effect.** The primary moderation target identifies the subject of the moderation/legal decision. A downstream affected record is not automatically a primary target. Order/payout blocking uses `ComplianceHold` where a reusable stop sign is required. Digital Goods Access executes DigitalDownloadGrant revocation; Video Infrastructure executes CourseVideoPlaybackGrant revocation. These owner-local effect references may travel through SH-103 `executeModerationDecision` requests/results without extending `ModerationTargetType`. Existing `media_access_grant` remains valid. Any new first-class decision target requires a separate explicit vocabulary ruling; no enum extension is authorized here.

**CL-09-R003 — Organization Hiring executor.** Moderation issues the decision; Organization Hiring executes supported effects against `Job` and `Organization` through SH-103 `executeModerationDecision` and returns execution evidence. Hiring validates owner-local transitions and retains every mutation to those records. Its retry-safe result must distinguish accepted, rejected, idempotently already applied, retryable failure, and terminal failure as supported by the eventual contract, within the canonical acknowledged/completed/failed/restored evidence boundary. Exact effect/result encoding remains for the owner contract; this does not create a competing operation or permit CL-09 database writes to Hiring.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result kind | Result | Consumer must not infer |
| --- | --- | --- | --- | --- | --- |
| `getReportStatus` | Reporter/authorized support | report ID + viewer context | Source truth view | safe status, timestamps, permitted summary | LegalNotice/case current state unless explicitly returned. |
| `getLegalNoticeStatus` | Submitter/authorized review | notice ID + viewer context | Source truth view | safe notice status and permitted timestamps | That notification delivery or target disablement equals legal completion. |
| `getModerationCase` | Authorized reviewer/support | case ID + viewer | Truth + contextual projection | case, related report/notices/actions, minimized target/evidence summaries | Direct target source state beyond owner-supplied summary. |
| `listModerationQueue` | Admin moderation UI | filters/cursor/viewer | Query projection | actionable cases, assignment/deadline summary | A separate queue lifecycle. |
| `queryActiveModerationRestriction` | Search, Media, delivery, target owners | typed target + requested action/surface | Decision | active restriction, safe reason codes, source case/action refs, evaluatedAt | Raw case/status interpretation or target lifecycle state. |
| `evaluateModerationCase` | Internal application service | case aggregate + owner facts + approved policy | Decision | proposed allowed action set, evidence requirements, warnings/manual-review need | Legal advice or statutory correctness outside approved policy. |
| `validateLegalNotice` | Internal legal-policy service | notice + policy version + structural/approved rule facts | Decision | valid/invalid/review/deficiency outcome when policy exists | Provider/email state or unversioned legal assumptions. |

### Decision result shape

Where practical, use the proposed shared SH-015 `returnDecisionResult` shape without creating a global policy engine:

- decision: `allow | deny | warning | review | remediation`;
- stable reason code(s);
- evidence/source references;
- evaluatedAt;
- policy version where applicable;
- expiry/recheck timestamp if applicable;
- safe next action.

---

## 12. Public Module Interface

### Public commands

- SH-101 `submitModerationReport`
- `submitLegalNotice`
- `triageReport`
- `openModerationCase`
- `assignModerationCase`
- `recordModerationAction`
- restoration/counter-notice commands only after their contract/policy is approved

### Public queries

- `getReportStatus`
- `getLegalNoticeStatus`
- `getModerationCase`
- `listModerationQueue`
- `queryActiveModerationRestriction`

### Cross-Module execution protocol

SH-103 `executeModerationDecision` is a confirmed cross-cutting protocol:

- Moderation supplies authorized case/action/effect context.
- Each target owner implements its own handler.
- Handler returns normalized acknowledgment/completion/failure/restoration evidence.
- Target owner writes its own truth.
- Moderation never writes target tables.

### Emitted domain event classes

The Module owns event meaning for report, notice, case, action, restriction/restoration facts. Exact event names/versioned envelopes are finalized with SH-046 `publishDomainEvent`.

### Privacy executor

This Module must implement Privacy-defined contracts:

- SH-096 `enumerateSubjectData`
- SH-097 `evaluateRetentionRequirement`
- SH-095 `executePrivacyInstruction`
- export serializer where required

Production mapping is blocked until CL-09 privacy target vocabulary/retention rules are approved.

### Provider-facing interfaces

None directly owned.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | Trusted reviewer/reporter/system context. | user/system ID, assurance/session facts needed by action. | Yes for protected actions. | `currentUser` auth helper/MFA logic. |
| Role / Authority | SH-002 `authorizeResourceAction` | Permission to review, assign, decide, access evidence. | actor, action, target relationship facts. | Yes. | Moderator/admin permission engine. |
| Identity & Access | SH-014 `requireStepUpForSensitiveAction` | High-assurance action where policy designates it. | actor/action/target/assurance requirement. | Yes when configured. | OTP/passkey implementation. |
| Target owner | SH-123 `validateOwnedTargetReference` / owner facts query | Prevent orphan/IDOR polymorphic targets and obtain safe context. | type, ID, requested action, safe owner version. | Yes. | universal Prisma target repository. |
| Context owner / Media / File Access | SH-026 `authorizeContextualResourceAccess` then Media-owned SH-127 `requestMediaAccess` for protected evidence; Media freeze/public-URL commands for effects | Context owner authorizes; Media supplies delivery and file effects; SH-030 `recordSensitiveAccess` where required. | Media refs, action/case source refs, contextual access decision. | Yes for evidence access and evidence-required destructive actions. | R2, CL-09 signer, authorization bypass, freeze logic. |
| Search / Public Visibility | SH-091 `requestSearchProjectionRefresh` | Hide/remove/restore public projection. | entity type/ID, action, reason, source version, idempotency. | Async effect may remain pending. | Typesense/SearchUpsertEvent writes. |
| Admin Review / Compliance Hold | SH-012 `requestComplianceHold` | Reusable stop sign for payout/profile/order/etc. | target, reason, source evidence, scope. | Yes when hold required. | local block state. |
| Audit / Event Ledger | SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess` | Generic action/access proof. | safe IDs/outcome/metadata. | Required proof failure may fail closed per workflow. | audit tables/loggers. |
| Notification | SH-041 `requestNotification` | Acknowledgments, takedown/counter/restoration/admin notices. | recipient facts, template intent, safe source refs. | Usually no for source write; legal policy may require delivery workflow. | SES/SMS/push clients. |
| Observability / Ops | request context/log/failure/queue operations | Correlation and technical failure visibility. | safe operation/source refs. | Telemetry often degrades; evidence-required ops do not silently succeed. | local integration-failure/queue tables. |
| Privacy / Data Erasure | privacy instruction protocol | Execute Privacy-owned request against moderation data. | subject, target instruction, retention decision context. | Yes for privacy completion. | PrivacyRequest/jobs/exemptions. |
| Digital Goods Access | owner execution handler | Disable/restore assets/revoke grants. | action/effect + asset target. | Yes for effect completion. | DigitalDownloadAsset/Grant writes. |
| Video Infrastructure | owner execution handler | Disable/restore playback/revoke grants. | action/effect + video asset target. | Yes for effect completion. | CourseVideoAsset/Grant writes. |
| Messaging | owner execution handler | Restrict/restore message/thread content. | action/effect + target. | Yes for effect completion. | Message/Thread writes. |
| Marketplace/Gig/Hiring/Profile owners | owner execution handlers | Apply hide/suspend/freeze effects to owned business objects. | action/effect + target + source refs. | Yes for effect completion. | business lifecycle mutations. |

---

## 14. Outbound Consumers and Effects

### Consumers of source truth

- Search / Public Visibility
- Media / File Access
- Messaging
- Marketplace Supply
- Gig / Demand
- Organization Hiring
- Professional Eligibility/Profile owner
- Admin Review / Compliance Hold
- Digital Goods Access
- Video Infrastructure
- Notification/admin support surfaces

### Effects

- Search refresh/remove/restore request.
- Media freeze/public URL removal/restore request.
- Messaging restriction/restore request.
- Offering/Gig/Job/Profile owner-local moderation effect request.
- Digital download asset/grant disable/revoke/restore request.
- Course playback disable/revoke/restore request.
- ComplianceHold creation when a reusable stop sign is needed.
- Notification request.
- Audit/sensitive-access request.
- Operational failure/queue telemetry.
- Privacy owner executor response.

### Boundary rule

A moderation action can be the **authority/source decision** for another owner to change state. It is never permission for this Module to mutate that owner's Prisma rows.

---

## 15. Canonical Shared Operations Used

**CL-09-R016 — Protected evidence access.** The relevant context owner supplies SH-026 `authorizeContextualResourceAccess`; only after the required contextual authorization succeeds may Media / File Access provide SH-087 `issueSignedMediaUrl` for protected short-lived delivery. Where sensitivity/action policy requires proof, use SH-030 `recordSensitiveAccess`. Signing is not permission logic. CL-09 must not implement a signer, object-storage access service, or generic evidence-access bypass.

The canonical `context/shared/shared-operations.md` registry supplies permanent SH IDs and names. References below use those existing identities; canonical ownership, boundaries, and Confirmed / Proposed ruling / Unresolved status remain unchanged. An ID reference does not approve a proposed operation or an unresolved implementation design.

| Canonical operation | Status/classification | Owner | Why this Module uses it | Invocation point | Local policy retained here | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | Confirmed platform capability | Identity & Access | Trusted actor context. | Protected entry point. | Which action/source is being attempted. | typed actor context | `moderationAuth.ts`, `currentModerator.ts` |
| SH-002 `authorizeResourceAction` | Confirmed cross-cutting capability | Role / Authority | Permission decision. | Before protected query/mutation. | moderation action/resource facts | allow/deny + reasons | `isModerator.ts`, admin role engine |
| SH-014 `requireStepUpForSensitiveAction` | Confirmed security capability | Identity & Access | Optional fresh assurance. | Before designated high-risk action. | which actions require it | valid SensitiveActionSession/decision | local MFA checks |
| SH-123 `validateOwnedTargetReference` | Confirmed shared contract/separate implementation | Target owner | Safe polymorphic target validation. | Before persisting/actioning target. | allowed target/action compatibility | valid target ref + source version/safe facts | universal target Prisma repo |
| SH-044 `executeIdempotentCommand` | Confirmed platform primitive | Platform application infra | Replay-safe mutation. | Intake/action/orchestration command. | semantic identity/conflict behavior | original result or conflict | local dedupe framework |
| SH-046 `publishDomainEvent` | Confirmed platform primitive | Event/outbox infra | Reliable fact publication. | Same transaction/outbox as source write. | event meaning/payload/privacy | versioned event envelope | fire-and-forget emitter |
| SH-045 `deduplicateDomainEvent` | Confirmed platform primitive | Consumer inbox infra | Replay-safe event handling. | Target-owner/worker handlers. | handler semantic identity | one completed effect | ad hoc processed-event table |
| SH-047 `enqueueReliableJob` | Confirmed platform primitive | Shared queue | Durable enforcement/deadline/reconciliation work. | After source transaction. | job payload/business completion | durable job reference | `moderationQueue.ts` framework |
| SH-048 `executeRetryWithBackoff` | Confirmed platform primitive | Shared queue | Retry transient technical failures. | Worker handler. | retryability/legal side-effect policy | retry/dead-letter result | custom retry loops |
| SH-049 `orchestrateWorkflowSteps` | Confirmed shared mechanism/separate truth | Workflow owner using shared runner | Multi-owner enforcement sequence. | Enforcement/restoration. | required steps/order/compensation | run/step execution | generic saga policy |
| SH-050 `reconcileWorkflowStatus` | Confirmed shared mechanism/separate policy | Workflow owner | Aggregate enforcement step outcomes. | Reconciliation. | partial/completed/failed meaning | parent workflow evaluation | target state copy |
| SH-051 `acquireAggregateLock` | Confirmed platform primitive | Shared persistence | Serialize conflicting case/action commands. | Critical transition/action. | lock key/conflict rules | lock/transaction control | in-memory mutex |
| SH-052 `withOptimisticConcurrency` | Confirmed platform primitive | Shared persistence | Reject stale case/report/notice updates. | lifecycle mutation. | retry/conflict policy | success/conflict + current version | custom stale check |
| SH-053 `transitionLifecycleState` | Confirmed shared mechanism/separate policy | Shared state-machine plumbing | Apply owner transition graph. | Every status mutation. | full moderation transition matrix | new state or invalid-transition error | generic global moderation policy |
| SH-055 `runDeadlineExpiration` | Confirmed shared scheduler capability | Shared scheduler/queue | Execute approved legal deadline work. | Scheduled scan. | legal deadline calculation/outcome | owner command dispatch | local cron engine |
| SH-072 `hashCanonicalPayload` | Confirmed shared crypto | Shared crypto | Evidence integrity digest. | Evidence snapshot creation. | canonical fields/proof meaning | digest + version | local SHA helper |
| SH-091 `requestSearchProjectionRefresh` | Confirmed Module public interface | Search / Public Visibility | De-index/re-index/hide/restore. | After moderation action. | reason/source version | Search request receipt | Typesense/SearchUpsertEvent write |
| SH-012 `requestComplianceHold` | Confirmed cross-cutting capability | Admin Review / Compliance Hold | Reusable stop sign. | After moderation decision requiring hold. | whether/why/scope | hold ID/status | payout/profile block fields |
| SH-029 `appendAuditEvent` | Confirmed platform audit capability | Audit / Event Ledger | Important action proof. | Intake/admin/decision transition. | safe action metadata | audit ID/time | `moderationAudit.ts` |
| SH-030 `recordSensitiveAccess` | Confirmed cross-cutting capability | Audit / Event Ledger | Evidence-view proof. | Protected evidence read/credential issuance. | sensitivity/access outcome | access log receipt | local evidence-view log |
| SH-041 `requestNotification` | Confirmed Notification interface | Notification | Deliver safe workflow communications. | After source fact committed. | recipient/event meaning/template intent | notification receipt | direct SES/SMS/push |
| SH-032 `createRequestContext` | Confirmed platform capability | Observability/platform | Correlation. | Request/job entry. | safe dimensions | correlation IDs | local request ID helper |
| SH-033 `writeStructuredLog` | Confirmed ops capability | Observability / Ops | Safe diagnostics. | Throughout execution. | operation-specific fields | log side effect | local logger |
| SH-034 `sanitizeTelemetryMetadata` | Confirmed shared payload policy | Observability + Audit policy | Prevent sensitive leakage. | Before audit/log/provider transmission. | allowed metadata fields | sanitized/rejected payload | `redactModerationJson.ts` |
| SH-037 `recordIntegrationFailure` | Confirmed ops interface | Observability / Ops | Technical failure visibility. | Failed owner dispatch/provider-mediated effect. | retryability/source refs | failure reference | moderation failure table |
| SH-038 `recordQueueTelemetry` | Confirmed ops/queue interface | Observability / queue infra | Worker attempt/retry/dead-letter visibility. | Worker lifecycle. | business completion meaning stays local | telemetry record/metric | local QueueJob truth |
| SH-096 `enumerateSubjectData` | Confirmed privacy contract | This owner via Privacy protocol | Discover moderation subject data. | Privacy workflow. | local relationships/export meaning | subject-data descriptors | global DB crawler |
| SH-097 `evaluateRetentionRequirement` | Confirmed shared contract | Data owner + Privacy | Return retention facts. | Before erase/anonymize. | moderation legal/security facts | retain/no-retain facts | local exemption table |
| SH-095 `executePrivacyInstruction` | Confirmed privacy protocol | Privacy orchestrates; this owner executes | Perform approved local disposition. | Privacy target execution. | field-level behavior | erased/anonymized/retained/exported result | local PrivacyRequest |
| SH-098 `anonymizePersonalFields` | Confirmed shared primitive | Shared primitive + owner mapping | Safe field pseudonymization. | Privacy executor. | which fields may change | transformed owner record | ad hoc scrub helper |
| SH-101 `submitModerationReport` | Confirmed Module public interface | This Module | Canonical report intake. | External/internal report path. | report policy | report receipt | local report models elsewhere |
| SH-103 `executeModerationDecision` | Confirmed cross-cutting protocol | Moderation decision + target owner execution | Owner-local enforcement. | After `ModerationAction`. | action/effect mapping | ack/completed/failed/restored result | direct foreign writes |
| SH-102 `resolveModerationTarget` | **Proposed Ruling** | typed registry + owner resolvers | Reviewer-safe target composition. | Case review. | fields/actions allowed | minimized target summary | universal repository |
| SH-104 `preserveEvidenceSnapshot` | **Proposed Ruling** | decision/evidence owner using Media/hash | Immutable legal evidence proof. | Before destructive effect. | evidence-required matrix/legal meaning | snapshot/reference | Audit generic blob |
| SH-105 `correlateEnforcementResult` | **Proposed Ruling** | This Module | Durable acknowledgment/retry/restoration correlation. | Enforcement/reconciliation. | required-step/partial meaning | orchestration state | copying target lifecycle state |
| SH-106 `computeContentFingerprint` | **Proposed ruling; optional after launch (WA-R004)** | Media / File Access adapter owner (WA-R016); technical/provider contract remains gated | Future duplicate/piracy signal; report-driven moderation ships without it. | Technical/provider gates before later activation. | match meaning/infringement decision | signal only | local piracy detector |

---

## 16. Module-Internal Operations

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `validateReportIntake` | Enforce report reason/source/target input rules. | report command | normalized/denied input | none | report semantics belong here. |
| `validateLegalNoticeStructure` | Enforce current structural fields without pretending legal sufficiency. | legal notice command | structural validation result | none | notice semantics belong here. |
| `triageReportPolicy` | Decide permitted report triage outcome. | Report + reviewer context | next state/next action | Report | lifecycle policy is local. |
| `evaluateModerationCase` | Produce allowed decision candidates from case + owner facts. | case aggregate/evidence/policy | decision result | none until command | core moderation policy. |
| `evaluateEvidencePreservationRequirement` | Determine whether action must have preservation proof before dispatch. | action/target/policy | required/not required + reasons | none | legal/moderation meaning is local. |
| `deriveEnforcementPlan` | Map approved action to required owner effects. | ModerationAction + target | ordered/required effects | no foreign state | workflow sequence belongs to moderation. |
| `buildActiveRestrictionDecision` | Translate current moderation truth into a stable consumer decision. | target/action/surface | restriction decision | none | consumers must not reconstruct policy. |
| `processCounterNotice` | Apply approved counter-notice workflow. | notice/case/policy | transitions/action proposal | LegalNotice/Case | legal workflow truth is local. |
| `deriveRestorationPlan` | Map restoration decision to owner effects. | restoration action | restoration steps | no foreign state | compensation semantics are moderation-specific. |
| `evaluateRepeatInfringerSignal` | Future repeat-infringer policy. | history/policy | signal/decision | **no current schema** | claimed responsibility but unresolved; do not implement yet. |

---

## 17. Shared Mechanism / Separate Truth Rules

| Mechanism | Reused mechanism | Truth that stays separate |
| --- | --- | --- |
| Lifecycle state machine | SH-053 `transitionLifecycleState` plumbing | Report, LegalNotice, ModerationCase each retain their own statuses/transition policy. |
| Idempotency | SH-044 `executeIdempotentCommand` | Duplicate semantics remain command-specific. |
| Events | transactional outbox/inbox | Moderation event meaning remains here; target handlers own their effects. |
| Workflow runner | SH-049 `orchestrateWorkflowSteps` | Moderation enforcement run meaning stays here; target state stays with target owner. |
| Hashing | SH-072 `hashCanonicalPayload` | Moderation evidence meaning stays with moderation; Agreement/audit hashes remain separate truth. |
| Evidence bytes | Media private storage/access | Legal meaning/reference stays with moderation if evidence snapshot ruling accepted. |
| Temporary grant revocation | shared grant mechanics / target owner | MediaAccessGrant, DigitalDownloadGrant, CourseVideoPlaybackGrant remain separate domain truth. |
| Audit append | Audit shared capability | ModerationAction remains decision truth. |
| Search projection | Search refresh command | SearchUpsertEvent/Typesense remain Search truth; moderation restriction remains here. |
| Queue/retry | shared queue platform | Moderation case/action status is not QueueJob status. |
| Target resolution | owner-specific contract/optional registry | Each target owner keeps source data and visibility policy. |
| Content fingerprint | exact/perceptual mechanism if approved | A match is only a signal; infringement decision remains moderation/legal truth. |

---

## 18. Authentication and Authorization

### Authenticated actor requirement

- Protected reviewer/admin commands and queries require SH-001 `resolveAuthenticatedActor`.
- Report intake uses authenticated actor context when the source is a Workin Ants User/admin/system action.
- Formal legal notice intake may be a controlled external flow because current schema stores submitter name/email without requiring a User relation. Do not force a User account unless legal-intake policy requires it.
- External/anonymous intake must not be able to spoof `ReportSource.admin`, `system`, `law_enforcement`, or another privileged source.

### Role / Authority

Use SH-002 `authorizeResourceAction` for:

- report triage;
- case open/assignment;
- case/evidence view;
- action decision;
- escalation;
- restoration;
- protected queue/status views.

This Module supplies moderation action vocabulary, target facts, assignment facts, and relationship context. Role / Authority interprets permission.

### Resource ownership/context

- Target ownership/participation facts come from the target owner.
- Messaging participant, organization membership, order participant, profile owner, etc. must not be reconstructed here.
- `assignedAdminUserId` is workflow assignment, not a general authorization grant.

### Step-up

SH-014 `requireStepUpForSensitiveAction` is used only for actions explicitly designated by security policy, such as sensitive evidence export or high-impact decisions if approved. This Module does not choose an MFA provider or build local step-up logic.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Interface/fact | Gated Module action | Local composition |
| --- | --- | --- | --- | --- |
| Actor authority | Role / Authority | SH-002 `authorizeResourceAction` | review/assign/decide/read evidence | map moderation action/resource facts. |
| Target validity | target owner | SH-123 `validateOwnedTargetReference` | create report/case/action | validate target exists and requested action is compatible. |
| Evidence preservation | Moderation policy + proposed evidence mechanism | preservation proof | destructive/public-removal action dispatch | action/target evidence-required matrix. |
| Compliance hold | Admin Review / Compliance Hold | request/evaluate hold | payout/profile/order stop-sign effects | decide when moderation outcome justifies requesting a hold. |
| Legal policy/version | approved legal-policy source | versioned rule set | `valid`/`invalid`, deadlines, counter-notice transitions | execute only approved rules. |
| Privacy retention | Privacy / Data Erasure + owner facts | retention instruction/exemption | erase/anonymize/export | return record-specific facts; Privacy owns exemption. |

### Entitlements

No current evidence establishes a Track Subscription entitlement gate for report submission, legal notice intake, or moderation review. Do not create one.

---

## 20. Provider Integrations

### Provider ownership ruling

This Module owns **no direct external-provider integration**.

Although historical registry technology lists include Cloudflare R2, Typesense, notification systems, and file access controls, stronger Cluster/shared-operation boundaries place those adapters with their owner Modules.

### Prohibited direct clients

Do not place in this Module:

- Cloudflare R2 SDK/client/credentials;
- Typesense client/index worker;
- SES/SMS/push provider clients;
- payment/Stripe client;
- Mux/video provider client;
- generic malware/file scanner;
- provider webhook endpoints/dedupe ledgers for those providers.

### Provider failures

Target owner normalizes provider failure and returns a typed handler result. Moderation records orchestration correlation if approved and sends technical failure context to SH-037 `recordIntegrationFailure`; provider error payloads do not become moderation domain types.

---

## 21. Events and Outbox

### Event rules

1. Events describe facts that occurred; they are not disguised commands.
2. Cross-Module effects use explicit owner commands/protocols such as SH-103 `executeModerationDecision` or SH-091 `requestSearchProjectionRefresh`.
3. Source write + outbox publication must be transactional where a consumer depends on the event.
4. Events carry minimized IDs/reason codes, not report bodies, legal statements, message bodies, full evidence, or private files.
5. Include event ID, schema version, aggregate ID/version or expected state token, correlation/causation IDs, occurredAt, source Module.
6. Consumers use SH-045 `deduplicateDomainEvent`.

### Candidate event classes

Exact wire names are deferred, but the Module needs versioned event classes for:

- report created;
- legal notice created;
- case opened/assigned/status changed;
- moderation action recorded;
- restriction/restoration decision changed.

### No event-table ownership transfer

The transactional outbox is platform infrastructure. It does not become a moderation event source-of-truth table.

---

## 22. Background Jobs / Scheduled Work

### Moderation enforcement worker

- **Purpose:** dispatch recorded action effects to target owners.
- **Input:** action ID + correlation/idempotency context.
- **Owner:** this Module for workflow sequence; target owners for execution.
- **Idempotency key:** action ID + effect/target + handler version.
- **Retryable:** transient owner/provider unavailability.
- **Permanent/manual-review:** invalid target/action, policy conflict, repeated terminal failure.
- **Dead-letter:** visible through shared queue/Observability; case/action truth remains intact.
- **Business truth updated:** only approved moderation orchestration correlation if `PR-CL09-03` accepted.
- **Telemetry:** queue attempts and integration failures.

### Reconciliation worker

- **Purpose:** find missing/failed acknowledgments and re-query/re-dispatch safely.
- **Dependency:** accepted enforcement-correlation record.
- **Business rule:** never infer target completion from queue telemetry alone.

### Legal deadline worker

- **Purpose:** find approved `actionDueAt` deadlines and dispatch owner commands.
- **Dependency:** `U-25` legal timing policy must be approved.
- **Scheduler:** SH-055 `runDeadlineExpiration`.
- **Rule:** scheduler code contains no legal outcome logic; Module policy does.

If legal deadline policy is absent, the worker is disabled.

---

## 23. Concurrency and Idempotency

### Races to prevent

- repeated report/legal notice submission with same semantic command;
- two reviewers transitioning the same report/case;
- duplicate case opening for the same explicit trigger when policy says one case;
- two actions issued from stale case/target context;
- enforcement worker duplicate delivery;
- takedown/restoration crossing in flight;
- case close while enforcement remains unresolved;
- repeated counter-notice/restoration submission.

### Lock/version strategy

- Prefer `updatedAt` compare-and-set or a future explicit version field for Report/LegalNotice/ModerationCase.
- Use SH-052 `withOptimisticConcurrency` for normal lifecycle updates.
- Use SH-051 `acquireAggregateLock` or transaction-level lock when two conflicting actions must be serialized.
- No in-memory mutex for distributed correctness.

### Transaction boundaries

- source record/status mutation + ModerationAction + outbox event should be one transaction when they represent one decision;
- no foreign Module table participates in that transaction;
- downstream owner effects are separate idempotent commands.

### Idempotency semantics

- caller provides idempotency key for external/retryable commands;
- platform persists key + fingerprint + result;
- same key/same fingerprint => replay original result;
- same key/different fingerprint => typed conflict;
- target owner handlers must also be idempotent.

---

## 24. Media / Storage

### Business meaning owned here

- whether evidence must be preserved;
- which case/action the evidence proves;
- which target/source version was captured;
- legal/moderation retention classification;
- chain-of-custody meaning if approved.

### Mechanics owned by Media / File Access

- `MediaAsset`;
- upload policy/session;
- validation/scanning/processing;
- private object storage;
- freeze/public URL revoke;
- signed access/MediaAccessGrant;
- object deletion/erasure mechanics.

### Evidence access

- evidence is private by default;
- reviewer accesses through Media contract;
- sensitive access invokes SH-030 `recordSensitiveAccess`;
- no permanent public evidence URL;
- do not store binary evidence in `evidenceJson`/`statementJson`.

---

## 25. Search / Projection

### Source truth

This Module's restriction/decision state.

### Search-owned projection

`SearchUpsertEvent` and Typesense state belong to Search / Public Visibility.

### Trigger

Actions/restriction changes that affect public discovery call SH-091 `requestSearchProjectionRefresh` with:

- typed searchable entity;
- entity ID;
- hide/remove/restore/update action;
- moderation source case/action;
- source version;
- idempotency key.

### Search must not reconstruct

Search must not infer moderation status from raw case rows or duplicate moderation policy. It consumes `queryActiveModerationRestriction` / owner-issued decision and source version.

---

## 26. Notification

### Business triggers defined here

Potential trigger intents include:

- report/notice receipt;
- reviewer/admin escalation;
- takedown/action decision;
- counter-notice receipt/status;
- restoration/rejection;
- manual-review required;
- terminal enforcement failure requiring operator attention.

### Delivery boundary

Call SH-041 `requestNotification`. Notification owns:

- channel selection;
- template rendering implementation;
- provider routing;
- delivery attempts/status;
- token/subscription state;
- retries.

### Safe payload rule

Use source IDs, safe status/reason codes, and authenticated deep links. Do not place legal statement bodies, private evidence, message bodies, PHI, full resume text, or full agreement content in outward notification payloads.

---

## 27. Audit and Sensitive Access

### Domain truth

- `ModerationAction` is moderation action/decision truth.
- Report/Notice/Case status fields are lifecycle truth.

### Generic audit

Use SH-029 `appendAuditEvent` for significant reviewer/admin actions. AuditEvent does not replace source records.

### Sensitive access

Use SH-030 `recordSensitiveAccess` when protected evidence or sensitive target data is read, downloaded, redacted, denied, or a signed credential is issued.

### Module-specific access proof

No additional generic access-log table belongs here. If an immutable moderation evidence snapshot is approved, it is decision proof, not an access log.

---

## 28. Privacy and Retention

### Subject-data inventory

Potential personal data includes:

- reporter User link;
- legal submitter name/email;
- rights-owner name;
- free-text details;
- reported/infringing URLs;
- `evidenceJson`/`statementJson`;
- opener/assignee/action actor User IDs;
- notes/summaries/resolution notes;
- evidence references;
- target references that may indirectly identify a person.

### Privacy executor

This Module participates through:

- SH-096 `enumerateSubjectData`;
- SH-097 `evaluateRetentionRequirement`;
- SH-095 `executePrivacyInstruction`;
- export serializer.

### Behavior categories

- erase fields where approved and nonessential;
- anonymize personal identifiers while preserving required legal proof where approved;
- retain only when owner facts justify it and Privacy creates `DataRetentionExemption`;
- revoke/delete Media evidence only through Media after Privacy instruction;
- contribute safe export data when required.

### Current blocker

`DataErasureTargetType` still has no explicit Report/LegalNotice/ModerationCase/ModerationAction target values. Production mapping/retention rules remain `U-24`. Do not silently use arbitrary `other` strings as a final architecture.

### Retention

No legal retention duration is supplied. Do not invent one.

---

## 29. Observability

### Required operations

- SH-032 `createRequestContext`
- SH-033 `writeStructuredLog`
- SH-034 `sanitizeTelemetryMetadata`
- SH-035 `captureException`
- SH-036 `emitMetric` where relevant
- SH-037 `recordIntegrationFailure`
- SH-038 `recordQueueTelemetry`

### Safe dimensions

Examples:

- operation name;
- Module;
- target type (not sensitive payload);
- case/report/notice/action ID where protected diagnostics permit;
- request/correlation ID;
- handler owner;
- attempt;
- normalized error code/class;
- retryability;
- elapsed time.

### Redaction

Never place secrets, OTPs, raw identity documents, PHI, private messages, full resumes, payment/card data, full legal statements, full evidence, or provider credentials in telemetry.

### Separation

Operational failure never changes `LegalNotice.status`, `ModerationCase.status`, or `ModerationAction` meaning by itself.

---

## 30. Security Boundaries

1. Validate all inputs with strict schemas and size limits.
2. Treat polymorphic `targetType + targetId` as an IDOR boundary; owner validation is mandatory.
3. Privileged source values cannot come from untrusted clients.
4. Rate-limit report/legal intake and protect against spam/abuse.
5. Reviewer/admin actions are server-authorized.
6. Sensitive evidence is fetched through owner-controlled, short-lived access.
7. Evidence/action confirmation must protect against stale target/case state.
8. JSON metadata must be schema-validated and size-bounded.
9. Shared hashing is used; no local cryptographic implementation.
10. Provider credentials never enter this Module.
11. Service-role execution cannot bypass Module lifecycle/target validation.
12. Direct database deletion of moderation/legal truth is not a normal application operation.
13. Admin exports are bounded, private, authorized, and access-audited.
14. Webhook verification/dedupe remains outside this Module unless a future provider is explicitly owned here.

---

## 31. Error / Decision Result Pattern

Public interfaces return stable Module/platform errors rather than Prisma/provider exceptions.

### Command/result categories

- `ok`
- `validation_denied`
- `authorization_denied`
- `not_found`
- `unsupported_target`
- `invalid_transition`
- `conflict`
- `stale_state`
- `idempotency_conflict`
- `policy_not_configured`
- `manual_review_required`
- `dependency_unavailable`
- `retryable_failure`
- `terminal_failure`
- `partial_execution` — orchestration only, not source decision failure

### Decision categories

Use `allow`, `deny`, `warning`, `review`, `remediation` where a decision API fits.

### Rules

- Do not expose raw provider error strings as stable reason codes.
- Do not reveal target existence to unauthorized viewers.
- A technical failure is not converted to a business/legal denial unless owner policy explicitly says so.
- A legal policy gap returns `policy_not_configured`/manual review rather than guessed behavior.

---

## 32. Testing Architecture

### Domain unit tests

- report source/reason/target policy;
- legal notice structural validation;
- action/target compatibility;
- evidence-required action matrix;
- restriction decision;
- lifecycle transition matrices once approved;
- restoration/counter-notice rules once approved.

### Public contract tests

- every command/query uses versioned DTOs;
- target-owner validation contracts;
- SH-103 `executeModerationDecision` handler protocol;
- Search/Media/Notification/Hold/Audit/Ops contracts;
- privacy executor contract.

### Database/integration tests

- create/read/transition Report/LegalNotice/Case;
- append ModerationAction;
- indexes/query paths;
- optimistic concurrency;
- no foreign Prisma mutation;
- evidence/reference transaction if approved.

### Authorization/security tests

- actor/source spoof prevention;
- reviewer role/action matrix;
- IDOR target validation;
- redacted case/status views;
- sensitive evidence access logging;
- intake rate limit/abuse controls.

### Compliance tests

- Report != LegalNotice;
- evidence preservation before destructive dispatch when required;
- LegalNotice remains truth after downstream disable/hide;
- no automated legal deadline without approved policy;
- no repeat-infringer/fingerprint automation without ruling.

### Idempotency/concurrency tests

- repeated intake;
- stale triage;
- double case open;
- concurrent action decisions;
- duplicate enforcement dispatch;
- takedown/restoration replay;
- counter-notice replay.

### Privacy tests

- enumeration;
- approved anonymize/erase/retain;
- retained legal evidence only through Privacy-owned exemption;
- export redaction;
- Media deletion delegated.

### E2E participation

- report -> case -> action -> Search removal;
- legal notice -> evidence -> takedown -> counter-notice -> restoration using approved fixtures;
- action -> Media freeze/public URL removal -> protected evidence view;
- action -> ComplianceHold -> blocked owner action;
- privacy request -> Module executor outcome.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. Only this Module owns `Report`, `LegalNotice`, `ModerationCase`, and `ModerationAction`.
2. A casual `Report` is not automatically a `LegalNotice`.
3. `LegalNotice` remains formal legal-workflow truth even after another object is hidden or disabled.
4. `ModerationCase` is not `Dispute`, `ComplianceHold`, `OpsIncident`, or support-ticket truth.
5. `ModerationAction` is not `AuditEvent`.
6. `ModerationAction` does not prove downstream execution succeeded.
7. A reversal/restoration creates new action/history; it does not rewrite prior action truth.
8. Target owners execute their own state changes.
9. No direct foreign Prisma writes from this Module.
10. Search changes only through Search public interface.
11. No direct Typesense client or `SearchUpsertEvent` write here.
12. File/public-URL changes only through Media public interface.
13. No direct R2/file provider client here.
14. Payout/profile/order stop signs use `ComplianceHold`; no local block flags.
15. Notification delivery remains Notification-owned.
16. Generic audit/access proof remains Audit-owned.
17. Observability failure records do not replace moderation/legal state.
18. Privacy request/job/exemption truth remains Privacy-owned.
19. Evidence required by policy is preserved before destructive/public-removal dispatch.
20. `Report.evidenceJson` and `LegalNotice.statementJson` are not immutable evidence snapshots.
21. Do not claim a legal deadline, retention duration, notice sufficiency rule, or repeat-infringer threshold without approved policy.
22. Do not implement repeat-infringer automation until its truth/policy is designed.
23. Do not implement duplicate/piracy fingerprint enforcement until ownership/provider/threshold/persistence are ruled.
24. A fingerprint match, if later added, is a signal, not infringement proof.
25. Do not build a universal cross-domain target repository.
26. Do not infer lifecycle transitions from enum order.
27. Reviewer actions must be concurrency-safe.
28. Async enforcement must be idempotent, retry-bounded, correlated, and observable.
29. Sensitive evidence access must be protected and auditable.
30. Provider payloads/errors/credentials do not become moderation domain types.
31. Current Prisma `ModerationTargetType` mapping is `moderation_target_type`; verify deployed migration history before changing it.
32. The current `media_access_grant` target value is valid current schema evidence; earlier Cluster snapshots omitting it are stale.
33. Current action/target mismatch for order/payout/grant effects must not be solved by inventing IDs/types locally.
34. Normal application code must not hard-delete moderation/legal evidence merely to satisfy product deletion.
35. Cluster sequencing remains authoritative; this Module plan must not reorder CL-09.

---

## 34. Prohibited Duplicate Implementations

Do not create:

- `moderationAuth.ts`, `legalAuth.ts`, `currentModerator.ts`;
- `moderationPermissions.ts`, `isModerator.ts`, local admin role engine;
- `targetResolverRepository.ts` that queries arbitrary domain tables;
- direct Typesense client, de-index worker, or `moderationSearch.ts`;
- direct R2 client, `r2Takedown.ts`, `removePublicUrl.ts`, `mediaFreezeService.ts`;
- `sendDmcaEmail.ts`, `moderationMailer.ts`, direct SES/SMS/push adapter;
- `moderationAudit.ts`, `legalAuditService.ts`, generic admin-action log table;
- `evidenceAccessLog.ts` duplicating `AccessAuditLog`;
- `moderationHold.ts`, `payoutPauseService.ts`, `isBlocked`, `contentHold`;
- local `integration_failures`, `queue_jobs`, incident tables;
- local idempotency table/framework when platform operation exists;
- local retry/backoff loop/framework;
- local outbox/event bus;
- local queue runner;
- local request/correlation ID framework;
- local lifecycle-state-machine framework;
- local hashing/canonicalization helper;
- local MFA/OTP/step-up logic;
- local PrivacyRequest/DataErasureJob/DataRetentionExemption;
- local signed URL/access-grant implementation;
- global processed-webhook table;
- generic review queue merging moderation, holds, job compliance, healthcare, and verification;
- repeat-infringer or content-fingerprint schema before ruling;
- legal correspondence system before ownership ruling.

---

## 35. Unresolved Decisions

| ID | Decision | Current state | Blocks |
| --- | --- | --- | --- |
| `M-01` | Exact Report transition matrix, terminal/reopen rules. | Status vocabulary confirmed; graph not. | Full lifecycle mutation implementation. |
| `M-02` | Exact ModerationCase transition matrix, close/reopen/reversal rules. | Vocabulary confirmed; graph not. | Full case lifecycle. |
| `M-03` | Exact LegalNotice transition matrix and legal-policy version storage. | `U-05`; legal-gated. | Auditable `valid/invalid` decision beyond structural intake. |
| `U-02` / CL-09-R007 | Primary target versus owner-local effect distinction is confirmed. | Order/payout blocking uses Holds; Digital Goods/Video execute grant effects through SH-103 `executeModerationDecision`; no new primary target is implied. | Exact enabled effect mappings still require target-owner contracts; new primary targets require separate approval. |
| `U-03` | Multi-report case aggregation/cardinality. | One optional `reportId`. | Consolidated multi-report case model. |
| `PR-CL09-02 / U-04` | Immutable evidence snapshot/reference. | Proposed, not accepted. | Strong evidence-preserving destructive decision path. |
| `PR-CL09-03 / U-06` | Durable enforcement run/step correlation. | Proposed, not accepted. | Reliable multi-owner reconciliation UI/worker. |
| `U-07` | Repeat-infringer source truth/policy. | Claimed responsibility, no schema/policy. | Repeat-infringer automation. |
| `U-08` | Duplicate/piracy fingerprinting owner/provider/threshold/persistence. | Unresolved. | Proactive duplicate detection. |
| `U-09` | Legal correspondence ownership/timeline. | Unresolved. | Complete legal correspondence history. |
| `U-24` | Privacy target vocabulary and retention rules for moderation/legal records. | Unresolved. | Production privacy executor. |
| `U-25` | Legal deadlines for `actionDueAt`/counter-notice restoration. | Unresolved legal policy. | Automated legal deadline worker. |
| `M-04` / CL-09-R009 | Retention-safe physical deletion/FK strategy. | Cascade deletion of retained action proof is prohibited; current FK needs later schema correction. | Unsafe case hard-delete remains prohibited; replacement strategy and retention disposition remain separately gated. |
| `M-05` | Controlled external legal-intake identity/verification/anti-abuse policy. | Schema supports external submitter; policy details not supplied. | Production external legal intake. |

### Resolved conflict

Earlier CL-09 `U-01` mapping concern is superseded by the current supplied Prisma mapping `@@map("moderation_target_type")`. Migration compatibility remains a deployment check, not a domain-ownership question.

---

## 36. Architecture Decision Summary

### Binding rulings

1. This Module exclusively owns Report, LegalNotice, ModerationCase, ModerationAction and their owned vocabularies.
2. The Module owns legal/moderation decision meaning; target owners execute effects.
3. Report and LegalNotice are separate source records and workflows.
4. ModerationAction is append-style decision truth and is not downstream completion truth.
5. ComplianceHold is the only reusable platform stop sign.
6. Search, Media, Notification, Audit, Observability, Privacy, Identity, Role/Authority, Digital Goods, Video, Payment, and business target lifecycles remain outside this Module.
7. Cross-Module reads/writes require published owner interfaces or approved protocols.
8. Evidence must be preserved before destructive/public-removal effects where owner policy requires it.
9. No direct R2, Typesense, notification, payment, or video provider integration belongs here.
10. Shared idempotency, outbox, queue, retry, locking, state-machine, hashing, request-context, audit, search, notification, and privacy mechanisms are consumed rather than duplicated.
11. Current Prisma `ModerationTargetType` mapping is accepted as current executable evidence; earlier stale mapping concern is not repeated as a new design problem.

### Proposed rulings not yet binding

- `PR-CL09-01` typed SH-102 `resolveModerationTarget` registry.
- `PR-CL09-02` Moderation-owned immutable evidence snapshot/reference using Media + shared hash.
- `PR-CL09-03` Moderation-owned enforcement run/step correlation.
- SH-015 `returnDecisionResult` shared response shape as a contract pattern, not a policy engine.

### Deferred/unresolved

- lifecycle transition matrices;
- action/target mapping gaps;
- case/report cardinality;
- legal validation provenance/version;
- repeat-infringer truth;
- duplicate-content fingerprinting;
- legal correspondence;
- privacy target/retention policy;
- legal deadlines;
- evidence deletion/FK behavior;
- external legal-intake verification policy.

No coding agent may silently settle these by creating a schema/helper while implementing another feature.

---

## 37. Coding-Agent Usage

Before implementing this Module, read in order:

1. root project overview;
2. root architecture, if present;
3. root code standards, if present;
4. Canonical Shared Operations Architecture;
5. CL-09 architecture;
6. CL-09 build plan;
7. this `module-architecture.md`;
8. this Module `implementation-plan.md`;
9. public-interface sections for direct dependencies used by the numbered feature;
10. progress tracker/current implementation state.

For each numbered feature:

- confirm its Cluster milestone is ready;
- confirm blocking Proposed Rulings/Unresolved Decisions are settled or explicitly deferred;
- implement only declared Module truth;
- use canonical operations and owner contracts;
- record any architecture change explicitly rather than embedding it in code.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R016 — Remaining shared adapter ownership

Class: **AI_RESOLVED_WITH_TRADEOFF**. Adopt Location Safety as the SH-069 geocoder adapter owner. It owns location normalization/protected-coordinate handling and already declares that boundary. Job Compliance and Payment independently select/interpret jurisdiction evidence; geocoding is not universal legal truth. Provider choice, permitted processing and purpose-specific evidence remain external/contract gates. Duplicate collapse: CL-08-HU-16 and SH-069 owner proposal, not the provider-policy question U-08-20.

Adopt Media / File Access as SH-106's optional content-fingerprint adapter owner, with a specialized implementation behind that owner. Media handles authorized file bytes/mechanics; Moderation determines investigative use/threshold policy and owns case/enforcement meaning. This avoids a new platform business Module and a competing detector in Moderation. The tradeoff is Media coordinating another optional processor; it gains no infringement authority. Scope remains optional after launch. No new provider or sensitive-input permission is implied. Duplicate collapse: CL-09-D007 / Moderation U-08 owner portion; WA-R004 already settles launch scope. Algorithm/provider/version, permitted input and explainable result contract remain later gates.

SH-065 stays inside AI Taxonomy for the current taxonomy use case; speculative future cross-domain AI use does not require creating another owner now. Consumers cannot import its provider SDK. Broader reuse requires an explicit future purpose/owner contract. SH-073 is shared cryptographic mechanism with separate owner chains; SH-081 is shared scanner mechanism with independent Job Compliance/Moderation policy and evidence. Neither creates a new business owner. SH-132 is platform security rate limiting and never Track metering.

All affected SH statuses remain Proposed ruling because contract/provider completion remains scoped. This ruling settles owner placement only; it does not mark provider readiness or approve a universal owner-facts/decision DTO. Shared normalization/mechanisms never acquire foreign lifecycle truth.

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
