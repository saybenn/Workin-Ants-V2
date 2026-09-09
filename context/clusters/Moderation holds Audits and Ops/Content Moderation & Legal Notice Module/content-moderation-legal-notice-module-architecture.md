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

The CL-09 architecture records `U-01` as an unresolved bad Prisma mapping for `ModerationTargetType`. The **current supplied Prisma schema no longer contains that defect**: `ModerationTargetType` maps to `moderation_target_type`. The current enum also includes `media_access_grant`, which the earlier Cluster enum snapshot omitted.

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

`updatedAt` may be used as the expected-version token through `withOptimisticConcurrency`; no explicit version column exists.

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

The relation currently uses `onDelete: Cascade` from `ModerationCase`. This is potentially in tension with evidence-retention goals. Normal application code must not expose case deletion. Whether the FK should be changed to `Restrict`/equivalent is an unresolved schema-retention decision and must not be changed incidentally.

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

### `submitModerationReport`

**Purpose:** create `Report` truth.

**Actor/context:** authenticated actor when source requires it; controlled system/external path only under approved intake policy.

**Inputs:** source, typed target, reason, safe details/URL/evidence refs, idempotency key.

**Preconditions**

- supported source/reason;
- target validated through owner contract;
- input size/rate limits;
- actor/source compatibility.

**Writes:** `Report`.

**Shared operations:** `resolveAuthenticatedActor`, `authorizeResourceAction` where required, `validateOwnedTargetReference`, `executeIdempotentCommand`, optional `publishDomainEvent`, `appendAuditEvent`, `createRequestContext`.

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

**Preconditions:** reviewer eligibility/authority. Do not imply lease/claim semantics beyond the existing field unless `claimWorkItem` is approved.

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

Where practical, use the proposed shared `returnDecisionResult` shape without creating a global policy engine:

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

- `submitModerationReport`
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

`executeModerationDecision` is a confirmed cross-cutting protocol:

- Moderation supplies authorized case/action/effect context.
- Each target owner implements its own handler.
- Handler returns normalized acknowledgment/completion/failure/restoration evidence.
- Target owner writes its own truth.
- Moderation never writes target tables.

### Emitted domain event classes

The Module owns event meaning for report, notice, case, action, restriction/restoration facts. Exact event names/versioned envelopes are finalized with `publishDomainEvent`.

### Privacy executor

This Module must implement Privacy-defined contracts:

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- export serializer where required

Production mapping is blocked until CL-09 privacy target vocabulary/retention rules are approved.

### Provider-facing interfaces

None directly owned.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why required | Minimum information | Can block? | Must not copy locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | `resolveAuthenticatedActor` | Trusted reviewer/reporter/system context. | user/system ID, assurance/session facts needed by action. | Yes for protected actions. | `currentUser` auth helper/MFA logic. |
| Role / Authority | `authorizeResourceAction` | Permission to review, assign, decide, access evidence. | actor, action, target relationship facts. | Yes. | Moderator/admin permission engine. |
| Identity & Access | `requireStepUpForSensitiveAction` | High-assurance action where policy designates it. | actor/action/target/assurance requirement. | Yes when configured. | OTP/passkey implementation. |
| Target owner | `validateOwnedTargetReference` / owner facts query | Prevent orphan/IDOR polymorphic targets and obtain safe context. | type, ID, requested action, safe owner version. | Yes. | universal Prisma target repository. |
| Media / File Access | evidence/private-access/freeze/public-URL commands | Preserve evidence and execute file effects. | Media refs, action/case source refs. | Yes for evidence-required destructive actions. | R2, signed URL, freeze logic. |
| Search / Public Visibility | `requestSearchProjectionRefresh` | Hide/remove/restore public projection. | entity type/ID, action, reason, source version, idempotency. | Async effect may remain pending. | Typesense/SearchUpsertEvent writes. |
| Admin Review / Compliance Hold | `requestComplianceHold` | Reusable stop sign for payout/profile/order/etc. | target, reason, source evidence, scope. | Yes when hold required. | local block state. |
| Audit / Event Ledger | `appendAuditEvent`, `recordSensitiveAccess` | Generic action/access proof. | safe IDs/outcome/metadata. | Required proof failure may fail closed per workflow. | audit tables/loggers. |
| Notification | `requestNotification` | Acknowledgments, takedown/counter/restoration/admin notices. | recipient facts, template intent, safe source refs. | Usually no for source write; legal policy may require delivery workflow. | SES/SMS/push clients. |
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

The current Canonical Shared Operations Architecture provides canonical **names**, not permanent `SH-###` IDs. Do not invent numeric IDs.

| Canonical operation | Status/classification | Owner | Why this Module uses it | Invocation point | Local policy retained here | Expected result | Prohibited duplicate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Confirmed platform capability | Identity & Access | Trusted actor context. | Protected entry point. | Which action/source is being attempted. | typed actor context | `moderationAuth.ts`, `currentModerator.ts` |
| `authorizeResourceAction` | Confirmed cross-cutting capability | Role / Authority | Permission decision. | Before protected query/mutation. | moderation action/resource facts | allow/deny + reasons | `isModerator.ts`, admin role engine |
| `requireStepUpForSensitiveAction` | Confirmed security capability | Identity & Access | Optional fresh assurance. | Before designated high-risk action. | which actions require it | valid SensitiveActionSession/decision | local MFA checks |
| `validateOwnedTargetReference` | Confirmed shared contract/separate implementation | Target owner | Safe polymorphic target validation. | Before persisting/actioning target. | allowed target/action compatibility | valid target ref + source version/safe facts | universal target Prisma repo |
| `executeIdempotentCommand` | Confirmed platform primitive | Platform application infra | Replay-safe mutation. | Intake/action/orchestration command. | semantic identity/conflict behavior | original result or conflict | local dedupe framework |
| `publishDomainEvent` | Confirmed platform primitive | Event/outbox infra | Reliable fact publication. | Same transaction/outbox as source write. | event meaning/payload/privacy | versioned event envelope | fire-and-forget emitter |
| `deduplicateDomainEvent` | Confirmed platform primitive | Consumer inbox infra | Replay-safe event handling. | Target-owner/worker handlers. | handler semantic identity | one completed effect | ad hoc processed-event table |
| `enqueueReliableJob` | Confirmed platform primitive | Shared queue | Durable enforcement/deadline/reconciliation work. | After source transaction. | job payload/business completion | durable job reference | `moderationQueue.ts` framework |
| `executeRetryWithBackoff` | Confirmed platform primitive | Shared queue | Retry transient technical failures. | Worker handler. | retryability/legal side-effect policy | retry/dead-letter result | custom retry loops |
| `orchestrateWorkflowSteps` | Confirmed shared mechanism/separate truth | Workflow owner using shared runner | Multi-owner enforcement sequence. | Enforcement/restoration. | required steps/order/compensation | run/step execution | generic saga policy |
| `reconcileWorkflowStatus` | Confirmed shared mechanism/separate policy | Workflow owner | Aggregate enforcement step outcomes. | Reconciliation. | partial/completed/failed meaning | parent workflow evaluation | target state copy |
| `acquireAggregateLock` | Confirmed platform primitive | Shared persistence | Serialize conflicting case/action commands. | Critical transition/action. | lock key/conflict rules | lock/transaction control | in-memory mutex |
| `withOptimisticConcurrency` | Confirmed platform primitive | Shared persistence | Reject stale case/report/notice updates. | lifecycle mutation. | retry/conflict policy | success/conflict + current version | custom stale check |
| `transitionLifecycleState` | Confirmed shared mechanism/separate policy | Shared state-machine plumbing | Apply owner transition graph. | Every status mutation. | full moderation transition matrix | new state or invalid-transition error | generic global moderation policy |
| `runDeadlineExpiration` | Confirmed shared scheduler capability | Shared scheduler/queue | Execute approved legal deadline work. | Scheduled scan. | legal deadline calculation/outcome | owner command dispatch | local cron engine |
| `hashCanonicalPayload` | Confirmed shared crypto | Shared crypto | Evidence integrity digest. | Evidence snapshot creation. | canonical fields/proof meaning | digest + version | local SHA helper |
| `requestSearchProjectionRefresh` | Confirmed Module public interface | Search / Public Visibility | De-index/re-index/hide/restore. | After moderation action. | reason/source version | Search request receipt | Typesense/SearchUpsertEvent write |
| `requestComplianceHold` | Confirmed cross-cutting capability | Admin Review / Compliance Hold | Reusable stop sign. | After moderation decision requiring hold. | whether/why/scope | hold ID/status | payout/profile block fields |
| `appendAuditEvent` | Confirmed platform audit capability | Audit / Event Ledger | Important action proof. | Intake/admin/decision transition. | safe action metadata | audit ID/time | `moderationAudit.ts` |
| `recordSensitiveAccess` | Confirmed cross-cutting capability | Audit / Event Ledger | Evidence-view proof. | Protected evidence read/credential issuance. | sensitivity/access outcome | access log receipt | local evidence-view log |
| `requestNotification` | Confirmed Notification interface | Notification | Deliver safe workflow communications. | After source fact committed. | recipient/event meaning/template intent | notification receipt | direct SES/SMS/push |
| `createRequestContext` | Confirmed platform capability | Observability/platform | Correlation. | Request/job entry. | safe dimensions | correlation IDs | local request ID helper |
| `writeStructuredLog` | Confirmed ops capability | Observability / Ops | Safe diagnostics. | Throughout execution. | operation-specific fields | log side effect | local logger |
| `sanitizeTelemetryMetadata` | Confirmed shared payload policy | Observability + Audit policy | Prevent sensitive leakage. | Before audit/log/provider transmission. | allowed metadata fields | sanitized/rejected payload | `redactModerationJson.ts` |
| `recordIntegrationFailure` | Confirmed ops interface | Observability / Ops | Technical failure visibility. | Failed owner dispatch/provider-mediated effect. | retryability/source refs | failure reference | moderation failure table |
| `recordQueueTelemetry` | Confirmed ops/queue interface | Observability / queue infra | Worker attempt/retry/dead-letter visibility. | Worker lifecycle. | business completion meaning stays local | telemetry record/metric | local QueueJob truth |
| `enumerateSubjectData` | Confirmed privacy contract | This owner via Privacy protocol | Discover moderation subject data. | Privacy workflow. | local relationships/export meaning | subject-data descriptors | global DB crawler |
| `evaluateRetentionRequirement` | Confirmed shared contract | Data owner + Privacy | Return retention facts. | Before erase/anonymize. | moderation legal/security facts | retain/no-retain facts | local exemption table |
| `executePrivacyInstruction` | Confirmed privacy protocol | Privacy orchestrates; this owner executes | Perform approved local disposition. | Privacy target execution. | field-level behavior | erased/anonymized/retained/exported result | local PrivacyRequest |
| `anonymizePersonalFields` | Confirmed shared primitive | Shared primitive + owner mapping | Safe field pseudonymization. | Privacy executor. | which fields may change | transformed owner record | ad hoc scrub helper |
| `submitModerationReport` | Confirmed Module public interface | This Module | Canonical report intake. | External/internal report path. | report policy | report receipt | local report models elsewhere |
| `executeModerationDecision` | Confirmed cross-cutting protocol | Moderation decision + target owner execution | Owner-local enforcement. | After `ModerationAction`. | action/effect mapping | ack/completed/failed/restored result | direct foreign writes |
| `resolveModerationTarget` | **Proposed Ruling** | typed registry + owner resolvers | Reviewer-safe target composition. | Case review. | fields/actions allowed | minimized target summary | universal repository |
| `preserveEvidenceSnapshot` | **Proposed Ruling** | decision/evidence owner using Media/hash | Immutable legal evidence proof. | Before destructive effect. | evidence-required matrix/legal meaning | snapshot/reference | Audit generic blob |
| `correlateEnforcementResult` | **Proposed Ruling** | This Module | Durable acknowledgment/retry/restoration correlation. | Enforcement/reconciliation. | required-step/partial meaning | orchestration state | copying target lifecycle state |
| `computeContentFingerprint` | **Unresolved** | Media/specialized adapter unresolved | Future duplicate/piracy signal. | Not implemented until ruled. | match meaning/infringement decision | signal only | local piracy detector |

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
| Lifecycle state machine | `transitionLifecycleState` plumbing | Report, LegalNotice, ModerationCase each retain their own statuses/transition policy. |
| Idempotency | `executeIdempotentCommand` | Duplicate semantics remain command-specific. |
| Events | transactional outbox/inbox | Moderation event meaning remains here; target handlers own their effects. |
| Workflow runner | `orchestrateWorkflowSteps` | Moderation enforcement run meaning stays here; target state stays with target owner. |
| Hashing | `hashCanonicalPayload` | Moderation evidence meaning stays with moderation; Agreement/audit hashes remain separate truth. |
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

- Protected reviewer/admin commands and queries require `resolveAuthenticatedActor`.
- Report intake uses authenticated actor context when the source is a Workin Ants User/admin/system action.
- Formal legal notice intake may be a controlled external flow because current schema stores submitter name/email without requiring a User relation. Do not force a User account unless legal-intake policy requires it.
- External/anonymous intake must not be able to spoof `ReportSource.admin`, `system`, `law_enforcement`, or another privileged source.

### Role / Authority

Use `authorizeResourceAction` for:

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

`requireStepUpForSensitiveAction` is used only for actions explicitly designated by security policy, such as sensitive evidence export or high-impact decisions if approved. This Module does not choose an MFA provider or build local step-up logic.

---

## 19. Compliance / Readiness / Entitlement Gates

| Gate | Truth owner | Interface/fact | Gated Module action | Local composition |
| --- | --- | --- | --- | --- |
| Actor authority | Role / Authority | `authorizeResourceAction` | review/assign/decide/read evidence | map moderation action/resource facts. |
| Target validity | target owner | `validateOwnedTargetReference` | create report/case/action | validate target exists and requested action is compatible. |
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

Target owner normalizes provider failure and returns a typed handler result. Moderation records orchestration correlation if approved and sends technical failure context to `recordIntegrationFailure`; provider error payloads do not become moderation domain types.

---

## 21. Events and Outbox

### Event rules

1. Events describe facts that occurred; they are not disguised commands.
2. Cross-Module effects use explicit owner commands/protocols such as `executeModerationDecision` or `requestSearchProjectionRefresh`.
3. Source write + outbox publication must be transactional where a consumer depends on the event.
4. Events carry minimized IDs/reason codes, not report bodies, legal statements, message bodies, full evidence, or private files.
5. Include event ID, schema version, aggregate ID/version or expected state token, correlation/causation IDs, occurredAt, source Module.
6. Consumers use `deduplicateDomainEvent`.

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
- **Scheduler:** `runDeadlineExpiration`.
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
- Use `withOptimisticConcurrency` for normal lifecycle updates.
- Use `acquireAggregateLock` or transaction-level lock when two conflicting actions must be serialized.
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
- sensitive access invokes `recordSensitiveAccess`;
- no permanent public evidence URL;
- do not store binary evidence in `evidenceJson`/`statementJson`.

---

## 25. Search / Projection

### Source truth

This Module's restriction/decision state.

### Search-owned projection

`SearchUpsertEvent` and Typesense state belong to Search / Public Visibility.

### Trigger

Actions/restriction changes that affect public discovery call `requestSearchProjectionRefresh` with:

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

Call `requestNotification`. Notification owns:

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

Use `appendAuditEvent` for significant reviewer/admin actions. AuditEvent does not replace source records.

### Sensitive access

Use `recordSensitiveAccess` when protected evidence or sensitive target data is read, downloaded, redacted, denied, or a signed credential is issued.

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

- `enumerateSubjectData`;
- `evaluateRetentionRequirement`;
- `executePrivacyInstruction`;
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

- `createRequestContext`
- `writeStructuredLog`
- `sanitizeTelemetryMetadata`
- `captureException`
- `emitMetric` where relevant
- `recordIntegrationFailure`
- `recordQueueTelemetry`

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
- `executeModerationDecision` handler protocol;
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
| `U-02` | How action effects target Order, payout, download grants, playback grants. | Action vocabulary exceeds target vocabulary; current schema adds `media_access_grant` but still lacks these. | Production cross-owner enforcement for affected actions. |
| `U-03` | Multi-report case aggregation/cardinality. | One optional `reportId`. | Consolidated multi-report case model. |
| `PR-CL09-02 / U-04` | Immutable evidence snapshot/reference. | Proposed, not accepted. | Strong evidence-preserving destructive decision path. |
| `PR-CL09-03 / U-06` | Durable enforcement run/step correlation. | Proposed, not accepted. | Reliable multi-owner reconciliation UI/worker. |
| `U-07` | Repeat-infringer source truth/policy. | Claimed responsibility, no schema/policy. | Repeat-infringer automation. |
| `U-08` | Duplicate/piracy fingerprinting owner/provider/threshold/persistence. | Unresolved. | Proactive duplicate detection. |
| `U-09` | Legal correspondence ownership/timeline. | Unresolved. | Complete legal correspondence history. |
| `U-24` | Privacy target vocabulary and retention rules for moderation/legal records. | Unresolved. | Production privacy executor. |
| `U-25` | Legal deadlines for `actionDueAt`/counter-notice restoration. | Unresolved legal policy. | Automated legal deadline worker. |
| `M-04` | `ModerationAction` cascade deletion retention safety. | Current FK cascades on case delete; retention policy not ruled. | Any case hard-delete path / possible FK migration. |
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

- `PR-CL09-01` typed `resolveModerationTarget` registry.
- `PR-CL09-02` Moderation-owned immutable evidence snapshot/reference using Media + shared hash.
- `PR-CL09-03` Moderation-owned enforcement run/step correlation.
- `returnDecisionResult` shared response shape as a contract pattern, not a policy engine.

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
