# Admin Review / Compliance Hold Module Architecture

## 1. Module Header

| Item | Value |
| --- | --- |
| Module ID | `admin_review_compliance_hold` |
| Module name | Admin Review / Compliance Hold Module |
| Module type | `ops_compliance` |
| Build status | `mvp_active` |
| Primary Cluster | CL-09 - Moderation, Holds, Audit & Ops |
| Document status | Implementation-grade Module architecture synthesized from current Workin Ants evidence |
| Intended audience | Coding agents, developers, reviewers, maintainers, compliance reviewers, and architecture owners |
| Relationship to root architecture | Subordinate to the root Workin Ants project overview, architecture, code standards, and source-of-truth rules. This file narrows those rules to this Module. |
| Relationship to Cluster architecture | Subordinate to CL-09 `architecture.md`; it defines the Module-local boundary and must not change Cluster ownership or sequencing. |
| Update rule | Update when a binding decision changes hold ownership, lifecycle, target/provenance representation, public contracts, reason/action applicability, review persistence, retention, or a shared-operation boundary. Build progress must not silently redefine architecture. |

### Evidence labels

- **Confirmed** means directly supported by the current Prisma schema, registries, glossary/compliance inventory, Canonical Shared Operations Architecture, or CL-09 architecture/build plan.
- **Proposed Ruling** means a concrete decision required for coherent implementation but not yet accepted as source authority.
- **Unresolved** means the evidence does not safely determine an implementation choice. A coding agent must stop or explicitly defer the affected scope.

The Canonical Shared Operations Architecture currently supplies canonical names, not permanent `SH-###` identifiers. This document does not invent numeric IDs.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own the reusable Workin Ants compliance stop sign: a durable record that a specified action against a specified target must not proceed while a source-domain condition remains unresolved.

### Goal

Provide one authoritative, validated, idempotent path to request, evaluate, review, release, and, only after policy approval, expire compliance holds. Feature Modules must be able to block their own actions without creating incompatible `isBlocked`, `canPayout`, `jobHold`, or equivalent truth.

### Inputs

- trusted actor or system context;
- one validated primary target;
- controlled `ComplianceHoldReason`;
- requested action scope;
- requesting Module and source decision/reference;
- minimized evidence references, not raw sensitive evidence;
- idempotency and request/correlation context;
- for release, an authorized source decision reference and release reason;
- for review reads, viewer authority and owner-supplied minimized context.

### Outputs

- an authoritative `ComplianceHold` in `active`, `released`, or, after an approved expiry rule, `expired` state;
- a safe allow/block decision for a named action;
- authorized hold detail and review-queue projections;
- release proof containing actor, reason, time, and source decision reference once the approved schema supports it;
- minimized domain events/outbox records when downstream reaction is required;
- audit, sensitive-access, notification, privacy, and operational requests through their owners.

### Capability transformation

```text
source-owned compliance decision + typed target + requested scope
  -> validate actor, target, provenance, reason, and semantic identity
  -> create or replay one authoritative active ComplianceHold
  -> evaluate target + action against active hold applicability policy
  -> allow or block consumer action
  -> source owner later supplies release-ready decision
  -> authorized, idempotent Hold-owned transition
  -> retained released/expired proof + audit/event/notification effects
```

### Why this is a separate Module

The hold lifecycle is cross-cutting, while the facts that justify a hold are distributed across Payment, Verification, Healthcare, Job Compliance, Moderation, Dispute, Prize, Rewards, Identity/Security, and other owners. Keeping the stop sign separate prevents a universal compliance engine from absorbing those facts and prevents each consumer from inventing its own blocking truth.

---

## 3. Owned Truth

### Confirmed ownership

| Owned item | Meaning |
| --- | --- |
| `ComplianceHold` | The authoritative statement that one approved target/action scope is stopped for a controlled reason, together with current lifecycle state and available creation/release proof. |
| `ComplianceHoldReason` | The controlled vocabulary describing why the stop sign exists. A reason references a source condition; it is not proof that the source condition itself is true. |
| `ComplianceHoldStatus` | The lifecycle vocabulary `active`, `released`, `expired`. |
| Hold lifecycle policy | The only policy permitted to create or change `ComplianceHold.status`. |
| Reason/scope/action applicability policy | Determines which active holds apply to a requested action. Consumers must not reconstruct this mapping. |
| Semantic duplicate policy | Defines when retried/concurrent hold requests are equivalent, once U-14 is approved. |
| Hold release policy | Determines whether a release command has acceptable authority, source decision proof, state, and idempotency. It does not decide the underlying source-domain outcome. |
| Hold-specific review presentation policy | Defines which hold facts are shown, redacted, or unavailable in this Module's list/detail surfaces. Source owners still authorize and redact their own context. |

### Proof and history ownership

- The persisted `ComplianceHold` row is the source of truth for current hold state and remains historical after release or expiry.
- The Module owns the business meaning of creation and release provenance that must eventually be stored with or referenced by the hold.
- No separate Hold-owned immutable history/decision ledger is confirmed in the current schema.
- Generic `AuditEvent` and `AccessAuditLog` are owned by Audit / Event Ledger. This Module requests them; it does not own or duplicate them.
- Module domain-event classes for hold creation, release, and approved expiry are Module-owned facts, but exact permanent event names are **Unresolved**. They require the platform event registry/contract decision.

### Projections and snapshots

- `listComplianceReviewQueue` is a Hold-owned read projection over hold truth plus bounded owner summaries. It is not a separate universal review lifecycle.
- No search projection is owned here.
- No immutable evidence snapshot schema is currently confirmed for this Module. `preserveEvidenceSnapshot` is a **Proposed Ruling** shared mechanism; if adopted, this Module owns the decision meaning and reference, while Media owns bytes and shared cryptography owns hashing mechanics.

### Supported compliance role

The Module is a supporting proof/control for processor-held payout flows, prize-tax fulfillment locks, and verified-only/high-risk service gates. Payment, Sweepstakes/Prize, Verification, and Professional Eligibility remain the primary policy owners.

---

## 4. Explicit Non-Ownership

| Adjacent owner | Truth that remains outside this Module | What must not be created here |
| --- | --- | --- |
| Identity & Access | User authentication, sessions, system credential validation, MFA/passkeys, step-up challenges, recovery, security events | Session resolver, MFA verifier, `security_lockout` lifecycle, account recovery workflow |
| Role / Authority | Permission interpretation and route/RLS authorization semantics | `isAdmin`, local role matrix, generic admin guard |
| Consent & Disclosure | `ConsentLog`, active consent versions, acceptance proof | FCRA/healthcare/other consent tables or consent sufficiency policy |
| Payment / Payout / Tax | KYC, tax, payout account/request/transfer, processor state, financial readiness, provider reconciliation | Stripe client, KYC/tax decisioning, payout execution, local `canPayout` truth |
| Trust Verification / Screening | Verification requirements/checks, licenses, background/DMV checks, provider results, adverse-action workflow | Provider status mapper, background decision, adverse-action state |
| Professional Eligibility | Action-specific professional readiness composition | Universal eligibility engine or professional status mutation |
| Job Compliance | Job text snapshot, scanner findings, rule evaluation, job compliance decision proof | Job scanner, job publication decision, job lifecycle mutation |
| Content Moderation & Legal Notice | `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction`, legal/moderation adjudication and enforcement orchestration | Moderation case, takedown decision, legal notice workflow, content restriction truth |
| Review / Dispute | Dispute lifecycle, evidence, resolution | Dispute state, resolution, refund/order decision |
| Healthcare / Regulated Services | Healthcare readiness, PHI access/redaction decision, BAA/data-boundary policy | Healthcare compliance or PHI decisioning |
| Sweepstakes / Prize | Prize drawing/entry/winning and fulfillment policy | Prize status or tax-policy truth |
| Gamification / Rewards | Points, rewards, redemption, fraud/tax coordination facts | Reward/redemption lifecycle or point-abuse adjudication |
| Candidate Application & Resume Privacy | Candidate/application/resume records, access authorization, `ResumeAccessLog` | Resume access policy or candidate lifecycle; applicable hold target/action is unresolved |
| Transaction / Order | `Order` lifecycle and `OrderEvent` | Order status changes, transaction truth |
| Notification | Notification, delivery, templates, routing, channel/provider state | Email/SMS/push sender or delivery table |
| Audit / Event Ledger | `AuditEvent`, `AccessAuditLog`, append-only storage, audit query/redaction policy | Hold audit table, local access log, generic event log |
| Observability / Ops | Request context, structured logs, metrics, exceptions, `IntegrationFailure`, queue telemetry, incidents | Local logger/Sentry client, generic failure/queue/incident store |
| Privacy / Data Erasure | Privacy requests/jobs/targets, retention exemptions, export bundle, orchestration | Local privacy workflow or retention-exemption table |
| Media / File Access | `MediaAsset`, file validation/scanning, storage, access grants, signed URLs | Evidence file store, upload pipeline, signed URL logic |
| Search / Public Visibility | Search queue/projection, Typesense adapter, indexing/de-indexing/reconciliation | Typesense client, `SearchUpsertEvent`, public search document |

Consumer-owned `blockedByHoldId` fields on `PayoutRequest`, `PayoutTransfer`, `PrizeWinning`, and `RewardRedemption` are associations/projections in those Modules. They do not transfer the `ComplianceHold` lifecycle to those consumers and must not become competing block truth.

---

## 5. Module Architecture Principles

1. A hold is a stop sign, never the source compliance fact.
2. Only this Module creates or changes `ComplianceHold.status`.
3. Hold release is not KYC, tax, verification, dispute, moderation, healthcare, security, prize, reward, or job-compliance approval.
4. Consumers ask `evaluateComplianceHold`; they do not infer applicability from raw rows, reason enum values, or local links.
5. Requesters supply domain justification and source references; this Module validates structure and authority but does not re-adjudicate foreign domain truth.
6. One hold has exactly one primary typed target if PR-CL09-04 is accepted; derived consumer associations do not create additional primary targets.
7. Reason and requested action scope are separate. A reason alone cannot define every blocked action.
8. Retried commands produce effectively-once business effects through canonical idempotency and database concurrency primitives.
9. Released/expired holds remain historical proof; no reopen or silent deletion is allowed under current confirmed policy.
10. Sensitive source payloads stay with source owners. Holds store minimized references and safe structured detail only.
11. Admin/service authority never bypasses target validation, source-decision requirements, lifecycle guards, privacy, or audit.
12. Review UI composes owner-safe summaries through public contracts, never a universal cross-domain Prisma repository.
13. Queue, locking, lifecycle, outbox, audit, notification, privacy, and telemetry mechanics are reused, not rebuilt.
14. Expiry, durable review claims/escalation, immutable evidence snapshots, and candidate/resume applicability remain disabled until their rulings are accepted.

---

## 6. Proposed Folder / Code Structure

The exact repository prefix must follow root `code-standards.md`. The relative ownership shape is:

```text
<module-root>/admin-review-compliance-hold/
  domain/
    compliance-hold/
      hold-policy.ts
      hold-transition.ts
      hold-applicability.ts
      hold-semantic-key.ts
    review-policy/
      review-visibility.ts
      review-queue-policy.ts
  application/
    commands/
      request-compliance-hold.ts
      release-compliance-hold.ts
      expire-compliance-hold.ts        # only after U-13 approval
    queries/
      get-compliance-hold.ts
      list-active-compliance-holds.ts
      evaluate-compliance-hold.ts
      list-compliance-review-queue.ts
      assemble-compliance-review-context.ts
    services/
      hold-target-validation.ts
      hold-review-context.ts
  public/
    commands.ts
    queries.ts
    contracts.ts
    events.ts
    privacy.ts
  infrastructure/
    repositories/
      compliance-hold-repository.ts
  workers/
    expire-due-compliance-holds.ts     # absent until U-13 approval
  privacy/
    enumerate-hold-subject-data.ts
    evaluate-hold-retention.ts
    execute-hold-privacy-instruction.ts
    serialize-hold-export.ts
  ui/admin/
    components/
    actions/
    queries/
  tests/
    unit/
    contract/
    integration/
    authorization/
    concurrency/
    privacy/
    e2e/
```

Do not create `providers/`: this Module owns no external provider. Do not create a Module-local `shared/`, `utils/`, `auth/`, `audit/`, `notification/`, `queue/`, `outbox/`, `logger/`, `search/`, or `storage/` package.

Conditional files shown above are architecture placeholders only; their existence is not authorized until the named unresolved decision is accepted.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / admin UI | Hold list/detail presentation, safe filters, authorized request/release actions, conflict/error states | Authority engine, foreign evidence rendering bypass, provider clients, universal review dashboard truth |
| Application commands | Command validation/orchestration, idempotency invocation, target-owner validation, Hold transaction, outbox/audit/notification requests | Source-domain adjudication or direct foreign writes |
| Application queries | Hold truth reads, action gate decision, queue projection, owner-safe review-context composition | Cross-domain repositories or permission inference from raw roles |
| Domain policy | Hold transitions, semantic equivalence, reason/scope/action applicability, release rules, safe reason exposure, review visibility | Generic state-machine engine, foreign readiness policies |
| Repository / data access | `ComplianceHold` persistence, constraints, indexes, transactional compare-and-set/locking | Foreign table repositories, audit/notification/outbox/queue persistence implementations |
| Workers | Owner-defined expiry scan/transition only after U-13; optional review escalation work only after U-11 | Generic queue runtime, unapproved cron policy, foreign reconciliation |
| Adapters | Thin adapters to approved Module public ports, owned outside this Module | Stripe, Checkr, R2, Typesense, email/SMS, logging-provider adapters |
| Public contracts | Hold commands, truth queries, gate decision, safe DTOs, event classes, Privacy executor | Provider-native types, raw Prisma models as public DTOs, source-owner private schemas |
| Privacy executor | Hold record enumeration, retention facts, local anonymize/erase/export/retain execution | Privacy request orchestration or exemption truth |

---

## 8. Data Model

### 8.1 Current Prisma model: `ComplianceHold`

**Purpose:** persist the current and historical state of the reusable stop sign.

**Current authoritative fields:**

- `id` - stable UUID for the hold;
- `reason` - controlled hold reason;
- `status` - authoritative lifecycle state, default `active`;
- `note` - optional current safe note; it is not an immutable evidence snapshot;
- `createdAt` - creation time;
- `releasedByUserId`, `releasedAt`, `releaseNote` - partial release proof.

**Current direct target relationships:** nullable `userId`, `professionalProfileId`, and `orderId` relations.

**Current consumer associations:** reverse relations from `PayoutRequest`, `PayoutTransfer`, `PrizeWinning`, and `RewardRedemption` through their `blockedByHoldId` fields.

**Current indexes:** `(userId, status)`, `(professionalProfileId, status)`, `(orderId, status)`, and `releasedByUserId`.

**Current deficiencies:**

- no database constraint requires exactly one target;
- a row can currently target zero records or multiple unrelated records;
- direct target coverage does not include claimed payout, content, prize, reward, verification, job, moderation, healthcare, or candidate targets;
- no requesting actor/system, requesting Module, source record/event, source decision version, requested action scope, evidence-reference structure, or idempotency key;
- no semantic active-hold uniqueness constraint;
- no aggregate `version`/approved compare-and-set field;
- no expiry time/condition or expiry actor/proof;
- no persistent assignment, priority, lease, review status, escalation, or due date;
- release proof lacks a structured release reason/source decision reference;
- mutable `note`/`releaseNote` is not immutable decision evidence.

### 8.2 Required schema-alignment gate

CL-09 Feature 04 cannot implement the general hold API until the following are explicitly approved:

- **PR-CL09-04 / U-10:** typed target representation and cardinality;
- **U-12:** creation/source provenance storage;
- **U-14:** semantic equivalence, idempotency, and duplicate prevention;
- reason/scope/action applicability contract needed by `evaluateComplianceHold`.

The accepted design must provide, logically, even if physical names differ:

1. exactly one primary target type and ID per hold;
2. target-owner validation and source version where required;
3. requested scope/action applicability input;
4. requesting Module and actor/system provenance;
5. source decision/record/event references and minimized evidence references;
6. semantic request identity/idempotency;
7. complete release actor/time/reason/source decision proof;
8. concurrency support appropriate to the accepted uniqueness strategy;
9. query indexes for target + status and queue filters.

**Proposed Ruling inherited from CL-09:** replace or augment the narrow nullable FKs with one validated typed target representation and exactly one primary target unless an explicit multi-target rule is later approved. This proposal is not migration authority until accepted.

### 8.3 Relationship meaning

- Direct target references identify what the hold is about; they do not make this Module owner of the target.
- `blockedByHoldId` on consumer records indicates which hold affected a consumer-owned lifecycle decision. It is not the canonical way to evaluate current blocking and must not compete with target/action evaluation.
- `releasedByUserId` identifies a human releaser when applicable. System release requires an approved typed system-actor representation; a nullable user ID alone is insufficient provenance.
- Foreign source/evidence references must be opaque typed identifiers resolved through owner interfaces, not Prisma relations added merely to simplify joins.

### 8.4 Retention and privacy

Holds may contain user/profile/order identifiers, actor references, compliance reason, notes, and foreign evidence references. Financial, fraud, security, legal, or dispute proof may require retention, but exact bases and durations are **Unresolved**. The Module must minimize free text, support Privacy-owned enumeration/execution, and preserve required proof only through an approved owner retention fact plus Privacy-owned exemption.

---

## 9. Enums, Statuses, and Lifecycles

### 9.1 `ComplianceHoldStatus`

```text
active ── authorized release ──> released
   │
   └── approved expiry rule ───> expired

released / expired ──X──> active
```

| State | Meaning | Terminal under current policy |
| --- | --- | --- |
| `active` | The hold may block applicable actions. | No |
| `released` | The Hold owner ended the stop sign after authorized source/admin release proof. | Yes |
| `expired` | The Hold owner ended a time/event-bound stop sign under an approved expiry rule. Current expiry semantics are unresolved. | Yes |

**Valid transitions:** `active -> released`; `active -> expired` only after U-13 approval. No other transition is confirmed.

**Transition owner:** Admin Review / Compliance Hold Module only.

**Triggers:** validated `releaseComplianceHold`; a future `expireComplianceHold` invoked manually or by approved deadline processing.

**Reopen/reversal:** prohibited under current confirmed rules. A newly justified stop requires a new hold with new provenance. Historical rows are not rewritten to `active`.

**Concurrency:** release and expiry compete on the same hold aggregate. Use database locking or compare-and-set/optimistic concurrency; only one terminal transition may win. Equivalent retries replay the committed result; conflicting retries return a typed conflict.

**Proof:** current row plus required generic audit and outbox event. No separate immutable Hold history table is confirmed.

**Prohibited shortcuts:** direct status update, enum-order inference, delete/recreate to simulate reopen, consumer-owned release, or fail-open release when source validation is unavailable.

### 9.2 `ComplianceHoldReason`

Current executable values:

```text
kyc_required
tax_required
payout_account_required
background_check_required
background_check_failed
license_verification_required
license_expired
dmv_check_required
adverse_action_pending
verification_fraud_review
prize_tax_required
reward_tax_required
sweepstakes_rules_review
gamification_fraud_review
points_abuse_review
fraud_review
dispute_open
moderation_review
copyright_dispute
legal_notice_review
chargeback_risk
admin_hold
provider_restricted
tax_reporting_required
mfa_required
phone_verification_required
account_recovery_review
security_lockout
other
```

These are reason references, not imported lifecycle statuses. `mfa_required`, `account_recovery_review`, `security_lockout`, `provider_restricted`, and `adverse_action_pending` may remain reasons only if they do not replace Identity, provider-owner, or Trust source state. `admin_hold` and `other` require structured source/provenance; free text alone is insufficient.

The exact reason-to-action-scope matrix is **Unresolved** and must be approved before production gate evaluation. Consumers must never infer it from enum names.

---

## 10. Commands

| Command | Purpose | Actor/context and authoritative inputs | Preconditions | State written | Shared operations/effects | Idempotency and failures |
| --- | --- | --- | --- | --- | --- | --- |
| `requestComplianceHold` | Create or replay one authoritative active stop sign. | Authenticated/system actor; requesting Module; typed target; reason; requested scope; source decision and evidence refs; idempotency key; request/correlation IDs. | Approved target/provenance/semantic-key design; authority; target-owner validation; structurally credible source ref; valid reason/scope combination. | New `ComplianceHold(active)` and required provenance fields; transactional outbox if needed. | `resolveAuthenticatedActor`, `authorizeResourceAction`, `validateOwnedTargetReference`, `executeIdempotentCommand`, lock/concurrency primitive, `appendAuditEvent`, `publishDomainEvent`, optional `requestNotification`. | Equivalent retry returns original/existing result; non-equivalent key reuse conflicts; unsupported target/reason, forbidden actor, target unavailable, or source invalid rejects without a hold. |
| `releaseComplianceHold` | End an active hold without changing the source-domain decision. | Hold ID; actor/system; structured release reason; source decision ref/version; idempotency key; expected version if adopted. | Hold exists and active; requester authorized; source owner supplied release-ready decision or is itself the authorized source; no conflicting terminal transition. | `status=released`, release actor/time/reason/source proof; outbox. | actor/authority/step-up where approved; idempotency; lock/CAS; lifecycle transition; audit; event; optional notification. | Same semantic retry returns committed release; already terminal with different basis conflicts; dependency unavailable retains active state and returns retryable failure. |
| `expireComplianceHold` | End an active hold under an approved expiry rule. | Hold ID; expiry basis; system/actor; idempotency; expected version. | **Disabled until U-13 is approved**; due condition verified; hold active. | `status=expired` plus approved expiry proof. | deadline scheduler/queue, idempotency, lock/CAS, lifecycle transition, audit/event/notification. | Same expiry replays; release/expiry race yields one winner; unknown due basis is manual review/permanent failure. |
| `escalateComplianceReview` | Persist or request escalation for unresolved/high-risk hold review. | Hold ID; reviewer; escalation reason/destination/priority; expected version. | **Disabled until U-11 and review ownership/schema are approved.** | Approved Hold-owned review/escalation truth only; never foreign compliance truth. | authority, optional step-up, `claimWorkItem` if accepted, audit, notification. | Stale claim/conflict rejected; no generic review record may be improvised. |

Commands are server-side application services, not direct database utilities. Input DTO validation, authorization, idempotency, transaction, audit/event, and safe response behavior are mandatory parts of the command contract.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result kind and content | Consumer must not infer |
| --- | --- | --- | --- | --- |
| `getComplianceHold` | Authorized source owners, admins/support, internal workflows | Hold ID + viewer context | Source-truth view with safe target, reason/status, provenance/release proof allowed to viewer | Underlying source condition is currently true; viewer may access source evidence; action is blocked without evaluating action scope |
| `listActiveComplianceHolds` | Authorized Modules/admin UI | Typed target and optional safe filters/cursor | Paginated active hold truth | Reason alone defines blocked actions; direct results may replace `evaluateComplianceHold` |
| `evaluateComplianceHold` | Any gated workflow | Typed target, named action/scope, actor/context, optional source version | Decision: allowed/denied/unavailable; applicable hold IDs, safe reason codes, scope, evaluation time, policy/source version, expiry/recheck only if approved | Underlying KYC/tax/etc. status; consumer may release hold; raw reason may be publicly exposed; a dependency failure means allowed |
| `listComplianceReviewQueue` | Authorized hold reviewers/admin UI | Status/reason/age/target/source filters, cursor, viewer authority | Bounded queue projection over holds; assignment/lease only if approved and persisted | A derived list is a durable claim/assignment lifecycle |
| `assembleComplianceReviewContext` | Authorized reviewer | Hold ID, viewer context, requested context sections | Hold truth plus owner-issued minimized/redacted source summaries and unavailable markers | This Module owns foreign facts or may bypass owner access rules |
| `getHoldReleaseReadiness` | Release command/admin UI when an owner supplies a readiness query | Hold/source reference | Contextual fact: source owner says release-ready/not-ready/unavailable with evidence/version | This Module independently approved the source condition |

Stable gate reason families should distinguish at least active hold, dependency unavailable, unsupported target/action, and redacted detail. Exact externally visible reason-code strings must be frozen with the public contract and must not leak sensitive source reasons.

---

## 12. Public Module Interface

### Public commands

- `requestComplianceHold`
- `releaseComplianceHold`
- `expireComplianceHold` only after U-13 approval
- `escalateComplianceReview` only after U-11/PR-CL09-06 approval

### Public queries

- `getComplianceHold`
- `listActiveComplianceHolds`
- `evaluateComplianceHold`
- protected `listComplianceReviewQueue`
- protected `assembleComplianceReviewContext`

### Emitted domain-event classes

- hold created;
- hold released;
- hold expired, only if expiry is approved;
- review escalated, only if review escalation truth is approved.

Permanent event identifiers are unresolved. Every event uses the canonical event envelope: event ID/type/schema version, source Module, hold aggregate ID/version, occurred time, correlation/causation, actor/system context, privacy classification, and minimized payload. Events report facts; they do not command consumers to approve a source condition.

### Privacy executor

- `enumerateSubjectData`
- `evaluateRetentionRequirement`
- `executePrivacyInstruction`
- Hold export serializer

### Provider-facing interfaces

None. This Module must not expose or accept raw provider types.

Public DTOs must be schema-validated and versioned. Raw Prisma records, unrestricted notes, provider payloads, and foreign private data are not public contracts.

---

## 13. Inbound Dependencies

| Owning Module / capability | Interface consumed | Why/minimum information | Can block? | Must not be copied locally |
| --- | --- | --- | --- | --- |
| Identity & Access | `resolveAuthenticatedActor`; optionally `requireStepUpForSensitiveAction` | Trusted actor/system ID, assurance, request actor context | Yes for protected commands/reads | Session/MFA/security workflow |
| Role / Authority | `authorizeResourceAction` | Decision for logical hold request/view/evaluate/release/review/escalate/export action plus resource facts | Yes | Role lookup/permission engine |
| Each target owner | `validateOwnedTargetReference`; owner-specific `queryOwnerFacts` | Existence, source version, minimum relationship/sensitivity facts, supported target/action | Yes for create/review | Universal target repository or foreign Prisma read |
| Source compliance owner | Owner readiness/decision query or signed source decision reference | Source record ID/version, decision outcome, evidence refs, release-ready fact | Yes; fail closed for required creation/release validation | KYC/tax/verification/moderation/dispute/etc. policy |
| Audit / Event Ledger | `appendAuditEvent`, `recordSensitiveAccess` | Safe action/access proof and receipt | A required audit failure blocks/rolls back where policy requires atomic proof | Audit/access tables and append-only mechanism |
| Notification | `requestNotification` | Recipient facts/template key/safe variables/priority/sensitivity/idempotency | Normally no for hold truth; failure becomes observable/retryable delivery work | Channel/provider delivery |
| Observability / Ops | request context, logging, metrics, exception/failure/queue telemetry | Correlation and safe operational diagnostics | Optional telemetry may degrade; required operational job persistence may block async scheduling | Logger, Sentry, failure/queue/incident schemas |
| Shared application infrastructure | idempotency, outbox/inbox, locks/CAS, lifecycle plumbing, queues/retries | Effectively-once command/event/job execution | Yes where required | Local idempotency/queue/outbox/lock packages |
| Privacy / Data Erasure | Privacy instruction protocol and exemption reference | Authorized request/job/target, desired disposition, exemption ID if retained | Yes for privacy execution | Privacy orchestration/exemption truth |
| Media / File Access | owner-authorized evidence access, if review evidence uses Media | Safe asset summary/signed short-lived access after owner policy | Yes for evidence access, not ordinary hold truth | File/storage/grant mechanics |

Direct dependency examples include Payment/Payout/Tax, Trust Verification, Professional Eligibility, Job Compliance, Content Moderation, Review/Dispute, Healthcare, Sweepstakes/Prize, Rewards, Candidate Privacy, Transaction/Order, and Identity/Security. Each supplies only its own public facts; none grants permission for a consolidated cross-domain repository.

---

## 14. Outbound Consumers and Effects

| Consumer | What it consumes | Permitted reaction | Prohibited coupling |
| --- | --- | --- | --- |
| Payment / Payout / Tax | request/evaluate/release; hold events | Stop or resume its own payout workflow; maintain an association to hold | Direct hold status writes; infer KYC/tax truth from reason |
| Professional Eligibility | `evaluateComplianceHold` decision | Compose Hold decision into its own readiness | Duplicate hold/eligibility truth |
| Job Compliance / Hiring | request/evaluate/release where approved | Stop owner action; route review | Candidate/job target use before U-10/U-15; foreign hold row writes |
| Content Moderation & Legal Notice | request/evaluate/release and events | Request stop sign after moderation decision | Replace `ModerationCase`/`ModerationAction` with hold |
| Review / Dispute | request/evaluate/release | Stop Order/payout action while dispute truth remains open | Treat hold as dispute lifecycle |
| Healthcare | evaluate/request through safe interfaces | Compose hold into owner decision | Reveal PHI or outsource healthcare policy |
| Sweepstakes / Prize | evaluate and association/event | Stop/resume prize fulfillment | Make `blockedByHoldId` competing truth |
| Gamification / Rewards | evaluate and association/event | Stop/resume redemption | Treat reason as reward fraud adjudication |
| Candidate / Resume Privacy | gate decision after U-15 | Stop an approved sensitive action | Bypass resume authorization/access logging |
| Search / source public-readiness owners | source-owner decision derived from hold | Rebuild/hide public projection through Search owner | Search scanning raw hold rows/reasons |
| Notification | safe request/event context | Deliver affected-party/reviewer alerts | Own hold meaning |
| Audit | action/access requests | Store generic proof | Own hold lifecycle |
| Privacy | enumerator/retention/executor/export results | Orchestrate subject rights and record exemptions | Direct hold mutations outside executor |

No outbound consumer may be mutated directly. Downstream projection, notification, audit, and workflow work uses the owning Module's command/protocol or a minimized domain event.

---

## 15. Canonical Shared Operations Used

No numeric shared-operation IDs are supplied. Names below are canonical.

| Canonical operation | Meaning / owner / classification | Use and invocation point | Hold-local policy / expected result | Prohibited duplicates |
| --- | --- | --- | --- | --- |
| `resolveAuthenticatedActor` | Resolve trusted Workin Ants actor; Identity & Access; platform capability | Every protected command/query entry | Hold supplies attempted logical action; returns actor/system context | `currentUser`, `holdSession`, local auth middleware |
| `authorizeResourceAction` | Permission decision; Role / Authority; canonical shared capability | After actor resolution, before protected hold read/mutation | Hold supplies resource/target/source relationship facts; returns allow/deny with reason | `isAdmin`, `requireAdmin`, `holdAdminAuth` |
| `requireStepUpForSensitiveAction` | Fresh assurance; Identity & Access; platform security capability | Only for actions designated by approved security policy | Hold identifies high-risk action/target; returns valid assurance or challenge requirement | Local MFA/OTP/passkey checks |
| `validateOwnedTargetReference` | Owner validates cross-Module target; target owner; shared contract/separate implementation | Before hold create and sensitive review composition | Hold defines supported target/action combinations; returns existence/version/safe facts | `findTargetByTypeAndId`, cross-domain Prisma repository |
| `queryOwnerFacts` | Minimum source facts; each source Module; proposed shared contract | Review context and source-decision validation | Hold requests only needed fields; owner returns redacted/unavailable outcome | Foreign-model imports/joins |
| `returnDecisionResult` | Stable decision envelope; shared contract/policy owner varies; Proposed Ruling | `evaluateComplianceHold` response | Hold owns active-hold applicability and reason namespace | Universal readiness/compliance engine |
| `executeIdempotentCommand` | One business effect/replay original result; platform primitive | Every mutating public command | Hold defines request fingerprint, semantic identity, conflicts, replay result | `holdIdempotency`, `dedupeHold`, processed-event-as-command table |
| `acquireAggregateLock` / `withOptimisticConcurrency` | Serialize or reject stale writes; shared persistence primitives | Equivalent create races and release/expiry/claim races | Hold defines semantic lock key and conflict behavior | In-memory mutex, ad hoc stale checks |
| `transitionLifecycleState` | State-machine plumbing; shared mechanism/separate truth | Every Hold status transition | Hold owns allowed graph, actor/reason requirements, terminal behavior | Generic global lifecycle policy or direct status setter |
| `publishDomainEvent` | Transactional outbox publication; platform primitive | Same transaction as authoritative hold change when consumers react | Hold owns event class, payload, privacy, emission condition | Fire-and-forget emitter |
| `deduplicateDomainEvent` | Consumer inbox dedupe; platform primitive | Hold event handlers/reconciliation if added | Handler/version/effect remain local | Ad hoc event-dedupe map |
| `appendAuditEvent` | Generic action proof; Audit / Event Ledger; platform audit capability | Hold create/release/expiry/escalation and material denial where policy requires | Hold supplies safe action/target/outcome/source refs; receives audit ID/time | `holdAudit`, `adminAuditLogger`, local audit table |
| `recordSensitiveAccess` | Protected-access proof; Audit / Event Ledger; canonical shared capability | After owner decision for sensitive review/evidence reads, including deny/redact/block | Hold identifies safe context; source owner retains sensitivity/access decision | `reviewAccessLog`, `financialReviewLog`, `phiAdminLog` |
| `requestNotification` | Submit safe alert; Notification; platform notification capability | After committed hold fact or review escalation | Hold owns trigger/recipient intent and safe variables; returns request ID | `sendHoldEmail`, `notifyReviewer`, SMS/push client |
| `createRequestContext` | Correlation/trace/request propagation; Observability/platform primitive | Request/job/event entry | Safe identifiers only | Local correlation helper |
| `writeStructuredLog` / `emitMetric` / `captureException` | Operational telemetry; Observability / Ops | Around commands, queries, jobs, unexpected failure | Hold owns safe operation outcome and low-cardinality dimensions | Logger/metrics/Sentry clients |
| `sanitizeTelemetryMetadata` | Remove prohibited data; Observability + Audit policy | Before audit/telemetry transmission | Hold supplies sensitivity labels and allowlisted fields | Ad hoc redactor |
| `recordIntegrationFailure` | Normalized dependency/worker failure; Observability / Ops | Owner-interface or async technical failure | Hold classifies retryability without changing business truth | `hold_failures` table |
| `enqueueReliableJob` / `executeRetryWithBackoff` | Durable job and bounded retry; shared queue/platform | Approved expiry, privacy execution, notifications/event consumers if async | Hold owns payload, semantic key, retryability, completion meaning | `holdQueue`, handwritten retry loop |
| `recordQueueTelemetry` | Queue execution visibility; Observability/queue infra | Worker claim/attempt/retry/dead-letter | Hold truth remains in `ComplianceHold` | Module queue ledger/dashboard backend |
| `runDeadlineExpiration` | Scan due records and invoke owner transition; shared scheduler/queue | Only after U-13 establishes expiry | Hold owns due semantics and `expireComplianceHold`; returns batch result | Cron loop interpreting `createdAt` |
| `claimWorkItem` | Transactional manual-review claim; proposed shared capability | Only after PR-CL09-06/U-11 | Hold owns reviewer eligibility, lease/escalation; returns claim/conflict | `claimReview`, `lockHold`, universal review case |
| `enumerateSubjectData` | Discover owner-held subject data; each owner through Privacy contract | Privacy discovery | Hold returns its record refs/dispositions | Global DB crawler |
| `evaluateRetentionRequirement` | Owner retention fact; Privacy records exemption | Before privacy erasure/anonymization | Hold owns fact/basis/minimum fields; returns required/allowed detail | Local retention table/`retainForever` |
| `executePrivacyInstruction` | Owner-local privacy action; Privacy orchestrates | Privacy job target execution | Hold mutates only owned records and returns canonical outcome | Local privacy request/job |
| `anonymizePersonalFields` | Versioned field-level anonymization; shared primitive/owner mapping | Approved hold anonymization | Hold defines field map/invariants/result proof | `scrubHold`, ad hoc SQL cleanup |
| `preserveEvidenceSnapshot` | Immutable/retention-protected evidence; proposed shared mechanism | Only if approved for high-impact hold decision | Hold owns proof meaning; Media owns bytes; crypto owns hash | Generic Audit evidence blob, `holdEvidenceHash` helper |

`requestComplianceHold`, `evaluateComplianceHold`, and `releaseComplianceHold` are themselves canonical cross-cutting capabilities owned by this Module, not external operations it consumes.

---

## 16. Module-Internal Operations

| Operation | Purpose | Input -> output | Truth affected | Why local |
| --- | --- | --- | --- | --- |
| `validateHoldRequestPolicy` | Check reason, target class, scope, source shape, and safe detail | Command DTO + actor + owner validation -> accepted/typed denial | None | Hold owns admissibility, not generic validation infrastructure |
| `deriveHoldSemanticKey` | Determine equivalence for dedupe/locking | Normalized target/reason/scope/source identity -> semantic key | Supports hold uniqueness/idempotency | Equivalence is Hold domain policy; hashing/storage mechanics are shared |
| `imposeComplianceHold` | Apply creation invariant and construct active aggregate | Validated request -> active hold | `ComplianceHold` | Core Hold transformation |
| `resolveApplicableActiveHolds` | Select active holds applicable to target/action | Target/action/context -> applicable hold set | Read only | Reason/scope/action mapping is Hold-owned |
| `buildHoldGateDecision` | Produce safe allow/deny/unavailable result | Applicable holds + viewer/consumer policy -> decision DTO | Read only | Hold owns decision meaning and safe reason exposure |
| `assertHoldReleasePolicy` | Verify authority, source decision, state, semantic retry, and step-up when approved | Release request + hold + source facts -> allowed/conflict/denial | None | Release is Hold lifecycle policy |
| `transitionComplianceHold` | Apply valid terminal transition | Hold + transition context -> updated hold | `ComplianceHold` | Lifecycle graph belongs here |
| `composeSafeHoldView` | Redact/projection logic for public/admin read | Hold + viewer decision -> safe DTO | Read only | Hold knows which of its own fields may be exposed |
| `deriveComplianceReviewQueue` | Build bounded review list from hold truth | Filters/cursor/viewer -> page of review summaries | Read projection | Queue view is Hold-specific; not generic queue truth |
| `assembleHoldReviewContext` | Combine safe hold view with owner-provided summaries | Hold + requested sections + owner results -> composite view | Read only | Orchestration is Hold-review specific; source data remains external |
| `mapHoldPrivacyDisposition` | Apply approved field/record privacy behavior | Privacy instruction + retention fact -> result | `ComplianceHold` only | Owner alone understands hold invariants/export meaning |

---

## 17. Shared Mechanism / Separate Truth Rules

| Mechanism | Reused capability | Separate truth that remains |
| --- | --- | --- |
| Lifecycle plumbing | `transitionLifecycleState` | Hold transition graph, release/expiry proof, terminal semantics |
| Idempotency/locks | command idempotency, Postgres locks/CAS | Hold semantic equivalence and conflict policy |
| Outbox/inbox | event publication/deduplication | Hold event classes and consumer effects |
| Append-only evidence | `appendAuditEvent`, `recordSensitiveAccess` | `ComplianceHold` lifecycle truth; source-domain histories |
| Readiness response | `returnDecisionResult` shape if accepted | Hold applicability policy and reason codes; foreign readiness decisions |
| Manual work claims | `claimWorkItem` if accepted | Hold review eligibility, assignment, escalation; moderation/job/health review truth remains separate |
| Snapshots/hashing | `preserveEvidenceSnapshot`, canonical hashing if accepted | Hold decision evidence meaning and retention; Media bytes; Audit generic proof |
| Privacy execution | Privacy protocol and anonymization primitive | Hold field map/retention facts; Privacy request/exemption truth |
| Queue/worker runner | durable jobs, retry, telemetry | Hold expiry rule and terminal transition; `QueueJob` is operational only |
| Provider-event dedupe | Provider owners' shared pattern | No provider-event record exists here; source owners translate provider state before hold use |
| Projections | bounded queue/read DTO mechanisms | Hold source row remains authoritative; Search projection remains Search-owned |

Passing an authority, entitlement, consent, readiness, or hold gate never substitutes for the others. The action-owning consumer composes the relevant decisions.

---

## 18. Authentication and Authorization

- Every protected entry resolves a trusted actor/system context through `resolveAuthenticatedActor`.
- Anonymous hold creation, release, review, evidence access, and administrative list/detail access are prohibited. A narrowly public legal/report intake belongs to Moderation, not here.
- Role / Authority evaluates permission through `authorizeResourceAction`; this Module supplies the logical action, hold ID, target, requesting/source Module, and safe relationship facts.
- Logical actions include request, evaluate, view, review, release, expire, escalate, and export. Exact permission-key strings are owned by the Role / Authority registry and are **Unresolved** here; do not hardcode a second vocabulary.
- `evaluateComplianceHold` may be callable by trusted internal Modules/system actors. User-facing callers receive only the minimum result needed for their own action.
- Admin/support status does not grant unrestricted access to financial, healthcare, resume, identity, security, legal, message, or private evidence. The source owner separately authorizes/redacts its review summary; sensitive access is audited.
- A service role uses the same application command and invariants. It is not permission to write hold rows directly.
- Step-up is available for high-impact release, evidence export, or sensitive review only if Identity/Security policy explicitly designates the action. No exact step-up matrix is confirmed.
- RLS and server decisions must be semantically aligned. Direct client writes to `ComplianceHold` are prohibited.

---

## 19. Compliance / Readiness / Entitlement Gates

| Underlying truth owner | Query/fact consumed | Hold action gated | Local composition | Result |
| --- | --- | --- | --- | --- |
| Payment / Payout / Tax | KYC/tax/payout readiness or source decision ref | Request/release hold; review context | Validate reference and source release readiness; do not interpret provider state | Hold created/released/retained/unavailable |
| Trust Verification / Screening | Verification/license/background/adverse-action decision | Request/release; review | Treat result as owner fact; reason only references it | Hold decision only |
| Professional Eligibility | Professional/target facts | Target validation/review; consumer later evaluates hold | This Module does not compute overall readiness | Valid target or dependency unavailable |
| Job Compliance | Job compliance result/source ref | Request/release after target support approved | No scanner re-evaluation | Hold only |
| Moderation | Case/action/source decision | Request/release moderation/legal hold | No case adjudication | Hold only |
| Review / Dispute | Dispute open/resolved fact | Request/release dispute hold | No dispute resolution | Hold only |
| Healthcare | Owner-safe readiness/access result | Request/release/review | Apply owner redaction and fail closed when required | Hold/review decision without PHI |
| Sweepstakes / Prize, Rewards | Prize/reward/tax/fraud source fact | Request/release and target validation | No fulfillment/redemption decision | Hold only |
| Identity/Security | MFA/recovery/security source fact | Request/release for related reasons | No challenge/recovery/security lifecycle | Hold only |

No Track entitlement is confirmed as a precondition for operating this Module. A consumer may combine entitlement and hold decisions in its own action. This Module must not create plan/premium booleans. Consent proof is queried only when an approved hold-review workflow requires it; this Module does not decide consent sufficiency for foreign workflows.

---

## 20. Provider Integrations

This Module owns **no direct provider integration**.

- No Stripe, payment, KYC, tax, Checkr/background, identity, healthcare, email/SMS/push, R2, Typesense, queue-provider, Sentry, or other provider client belongs here.
- Provider owners verify webhooks, deduplicate provider events, translate provider state, reconcile, retry, and retain credentials.
- Hold commands consume only translated Workin Ants domain decisions or source references.
- Provider-native statuses/errors must not appear in Hold public DTOs, reason mapping, or database enums.
- A provider/source dependency failure becomes a normalized unavailable/retryable result and may be reported through `recordIntegrationFailure`; it never causes a silent release or fail-open gate.

---

## 21. Events and Outbox

### Event classes

| Fact class | Emit when | Minimum safe payload |
| --- | --- | --- |
| Hold created | Active hold commits | Hold ID/version, typed target reference, safe scope/reason code, requesting Module/source ref, occurredAt |
| Hold released | Authorized release commits | Hold ID/version, target reference, safe release reason/source decision ref, actor/system ref, releasedAt |
| Hold expired | Approved expiry commits | Hold ID/version, target, expiry basis/ref, expiredAt |
| Review escalated | Approved escalation truth commits | Hold/review ref, safe escalation reason/destination, occurredAt |

Exact permanent event names are unresolved. Use `publishDomainEvent` and the common event envelope after names/contracts are accepted.

### Rules

- Hold state and required outbox row commit atomically.
- Payloads omit raw source evidence, PHI, resumes, tax/KYC detail, identity documents, message bodies, credentials, or provider payloads.
- `aggregateType=ComplianceHold`; aggregate version or accepted source-version equivalent is required for ordering/conflict reasoning.
- Correlation and causation link the source decision, command, audit request, notification, and downstream consumer work.
- Consumers use `deduplicateDomainEvent`/transactional inbox and own their side effects.
- An event states that a hold changed. It must not instruct a consumer to mark KYC approved, close a dispute, release a payout, or restore content.

---

## 22. Background Jobs / Scheduled Work

No Module-owned scheduled worker is currently authorized for the base hold API.

### Conditional: `expireDueComplianceHolds`

| Item | Rule |
| --- | --- |
| Purpose | Find holds due under an approved expiry policy and call `expireComplianceHold`. |
| Activation | Only after U-13 defines time/event/manual expiry, proof fields, and due semantics. |
| Input | Cursor/batch size/clock/correlation plus approved due-hold selector. |
| Owner | Admin Review / Compliance Hold for due/transition meaning; shared scheduler/queue for execution. |
| Idempotency key | Stable hold ID + expiry basis/version. |
| Retryable failures | Database/transient dependency/queue failures. |
| Permanent/manual-review failures | Missing/invalid expiry basis, policy version unknown, target/source contradiction, competing release already won. |
| Dead letter | Visible through Observability with hold/source refs; hold remains active unless transition committed. |
| Business truth updated | `ComplianceHold` only. |
| Telemetry | Request/correlation ID, batch/attempt/outcome/duration; no sensitive payload. |

Review queue display is a query, not a background job. Durable claim expiry/escalation work is not authorized until U-11 and `claimWorkItem` are accepted.

---

## 23. Concurrency and Idempotency

### Races to prevent

- simultaneous equivalent hold requests;
- same idempotency key with different request fingerprint;
- active hold request racing with release of an equivalent existing hold;
- two releases with different source decisions/reasons;
- release racing with approved expiry;
- reviewer claim/reassignment/escalation races if review persistence is adopted;
- event/job replay repeating audit, notification, or consumer effects.

### Required strategy

| Concern | Rule |
| --- | --- |
| Semantic create key | Must be approved under U-14; logically includes normalized primary target, reason, scope, and authoritative source identity/version as required. |
| Aggregate lock key | Hold ID for transitions; accepted semantic hold key for equivalent creation. |
| Database constraint | Encode accepted request-idempotency uniqueness and active semantic uniqueness where PostgreSQL can enforce it. Application-only duplicate checks are insufficient. |
| Transaction boundary | Idempotency claim/result, authoritative hold mutation, and required outbox record commit atomically; required audit coupling follows the approved audit/outbox pattern. |
| Concurrency mechanism | PostgreSQL row/advisory lock, serializable transaction, or compare-and-set/versioning through shared primitives. No in-memory locks. |
| Create replay | Same key/fingerprint returns original hold/result. Same key/different fingerprint returns conflict. Semantically equivalent concurrent request returns existing hold or the deterministic policy result. |
| Release replay | Same semantic command returns committed release. Different basis against terminal hold returns conflict; it does not rewrite proof. |
| Evaluation consistency | Reads authoritative active state within a transaction/isolation level appropriate to the consumer action. The action-owning consumer is responsible for composing the gate with its own write atomically enough to prevent time-of-check/time-of-use bypass. |

The exact physical uniqueness/index/version design remains blocked by U-10/U-12/U-14. Coding agents must not substitute a process-local cache or mutex.

---

## 24. Media / Storage

- A hold may own the business meaning of an evidence reference, but not the file.
- Raw documents, screenshots, identity documents, resumes, PHI, message bodies, or provider payloads must not be copied into `note`, `releaseNote`, event payloads, audit metadata, or telemetry.
- If evidence files are needed, the source/decision owner references a ready private `MediaAsset`; Media validates upload context, size/type/signature, malware state, processing readiness, and private/public status.
- Reviewer access requires general authority, source-owner contextual authorization/redaction, Media-issued short-lived access, and `recordSensitiveAccess` where required.
- This Module does not issue signed URLs, manage access grants, scan files, delete provider objects, or make a file public.
- Immutable hold evidence snapshots are not authorized until `preserveEvidenceSnapshot` ownership, schema, retention, and hash meaning are approved.

---

## 25. Search / Projection

- `ComplianceHold` is source truth in PostgreSQL/Prisma, not a search document.
- This Module owns no Typesense collection, `SearchUpsertEvent`, public search projection, or de-index worker.
- A source Module may incorporate `evaluateComplianceHold` into its own public-readiness/source projection policy and then call Search's `requestSearchProjectionRefresh`.
- Search must not scan Hold tables or interpret raw reason values to decide public visibility.
- Hold created/released events may prompt a source owner to recompute its projection; that reaction remains consumer-owned and idempotent.
- The Hold admin review queue is a bounded protected database projection, not public Search truth.

---

## 26. Notification

### Business triggers

- hold created: reviewer and/or affected-party alert where policy requires;
- hold released: safe status-change alert;
- hold expired: only after expiry policy approval;
- review assigned/escalated: only after review persistence approval;
- dead-letter/manual intervention: operational alert through Observability/Notification.

### Safe payload intent

Include notification type/template key, recipient facts, hold ID, safe target label/reference, safe status, action route, sensitivity, priority, and idempotency key. Omit raw reason/source detail when it could reveal financial, identity, health, security, resume, dispute, or legal information. Notification owns recipient fan-out, preferences, templates, channel rendering, provider calls, retries, and delivery truth.

Notification failure does not roll back a committed hold unless an approved legal/business policy explicitly requires atomic notice. It becomes retryable work and operational visibility.

---

## 27. Audit and Sensitive Access

| Evidence surface | Owner | Hold use | Separation rule |
| --- | --- | --- | --- |
| `ComplianceHold` | This Module | Current/historical stop-sign and release truth | Not generic audit or source compliance truth |
| Hold domain event/outbox | This Module + platform outbox mechanism | Reliable fact publication | Not an `AuditEvent` and not cross-Module command |
| `AuditEvent` | Audit / Event Ledger | Creation, release, approved expiry/escalation, material admin mutation/denial proof | Does not replace Hold status/provenance |
| `AccessAuditLog` | Audit / Event Ledger | Sensitive review/evidence view/download/deny/redact/block proof | Source owner still decides access; not a Hold review ledger |
| Source-domain history | Payment, Trust, Moderation, Dispute, etc. | Supplies decision/evidence reference | Never copied or absorbed |

Audit metadata is schema-validated, bounded, sanitized, and correlated. A required audit append must use the approved transaction/outbox coupling so partial success is explicit. Normal app/admin roles cannot update/delete audit evidence.

---

## 28. Privacy and Retention

### Subject-data inventory

Enumerate holds where the subject is, as the approved schema permits:

- primary target;
- requester/creating actor;
- releasing actor;
- source/evidence subject referenced by typed identifier;
- subject named in permitted notes, which should be minimized.

### Privacy executor behavior

- `enumerateSubjectData` returns stable Hold target references, sensitivity, supported dispositions, retention candidates, and export capability.
- `evaluateRetentionRequirement` returns owner facts such as required/not required, reason code, policy/legal basis, `retainUntil` if known, minimum retained fields, permitted anonymization, and source reference. Privacy owns the exemption record.
- `executePrivacyInstruction` supports approved erase, anonymize, restrict, export, retain, detach, skip, retryable failure, or terminal failure outcomes against Hold-owned data only.
- Export serializer emits safe subject-relevant hold state/proof and omits other subjects' data, private source evidence, internal risk signals, secrets, and unrestricted notes.

### Retention rules

- Financial/fraud/security/legal/dispute proof may require retention, but exact bases/durations are unresolved.
- Unknown or unapproved retention basis returns blocked/manual-review; do not create `retainForever` or invent a legal period.
- Released hold history must not be silently destroyed when needed to explain a historic block.
- If anonymization would invalidate approved evidence/hash integrity, return a retention/manual-review fact until an approved strategy exists.
- No provider resources are directly owned here. Media/source-owner resources are handled through their executors.

Production behavior is blocked until U-24 establishes Privacy target vocabulary and approved retention policy.

---

## 29. Observability

### Structured signals

- command/query name and version;
- success/denial/conflict/unavailable/retry outcome;
- hold status transition class;
- target type and reason/scope category only where approved and non-sensitive;
- dependency owner and normalized failure category;
- duration, retry count, queue attempt, and dead-letter state;
- request, correlation, causation, and event/job IDs.

Never log note/release-note text, raw source evidence, tax/KYC/provider details, PHI, resumes, identity documents, message bodies, credentials, or full personal identifiers. User/target IDs should be omitted, protected, or purpose-limited according to telemetry policy; avoid high-cardinality metric dimensions.

Use canonical request context, logger, metric client, exception capture, integration-failure recording, and queue telemetry. Operational records do not change or replace `ComplianceHold`. A missing telemetry provider must not be represented as a successful hold operation or healthy dependency.

Relevant metrics include request/evaluation/release counts, conflict/duplicate rate, dependency-unavailable rate, active-hold age distribution, release latency, admin queue latency, worker retry/dead-letter counts if workers exist, and authorization denials. Thresholds are operational policy, not invented here.

---

## 30. Security Boundaries

1. Validate all public DTOs at runtime; TypeScript types alone are insufficient.
2. Validate target type/ID through its owner and allow only approved target/action combinations.
3. Protect against IDOR by authorizing the logical hold resource and source/target context on every read and mutation.
4. Do not accept arbitrary Module names, table names, URLs, JSON paths, or Prisma model names as target/source references.
5. Bound, schema-validate, and sanitize notes, reason detail, evidence references, pagination, filters, and metadata.
6. Treat reason/source details as potentially sensitive. Return safe reason codes and redacted views.
7. Server/service roles use typed system identity and the same owner command path.
8. No external credentials, webhook endpoints, temporary secrets, signed URL generation, or provider payload storage belongs here.
9. Use canonical hashing/encryption only if approved; do not claim a mutable note hash proves evidence integrity.
10. Apply rate limits to exposed hold-request/evaluation/admin query entry points according to platform policy, especially where target probing is possible.
11. Separate not-found/forbidden presentation where revealing target/hold existence would leak sensitive facts.
12. Fail closed for mandatory hold evaluation, release-source validation, authorization, and evidence-preservation requirements.

---

## 31. Error / Decision Result Pattern

### Command result categories

- success;
- idempotent replay;
- validation failure;
- unauthenticated;
- forbidden or step-up required;
- target not found/unsupported/unavailable;
- source decision required/not release-ready;
- semantic duplicate conflict;
- stale version/transition conflict;
- dependency unavailable/retryable failure;
- manual review required;
- terminal internal failure.

Errors expose a stable Module code, safe message, retryability, request/correlation ID, and current aggregate version/status where safe. They never expose provider-native errors or foreign sensitive payloads.

### Gate decision

Align with the common decision envelope:

```text
decision: allowed | denied | unavailable
blocking: true | false
reasonCodes: Hold-owned, safe, stable codes
holdIds: authorized/minimized references
evaluatedAt
policyVersion
sourceVersion or aggregateVersion
retryable
recheckAt/expiry only when approved
remediation/nextAction when safe
```

`unavailable` is never silently converted to `allowed` for an action whose policy requires the hold gate.

---

## 32. Testing Architecture

### Domain unit tests

- reason/scope/action applicability;
- request admissibility and safe reason exposure;
- semantic equivalence once approved;
- release policy and release-is-not-approval invariant;
- review visibility/redaction;
- privacy field/disposition mappings.

### Lifecycle tests

- `active -> released` succeeds with complete proof;
- all unspecified transitions reject;
- released cannot reopen or be silently rewritten;
- `active -> expired` is unavailable until U-13, then tested under approved rules;
- duplicate release and release/expiry race behavior.

### Public contract tests

- request/evaluate/release/get/list DTO schemas and safe errors;
- gate decision reason/version fields;
- owner target validation and source-decision contracts;
- event envelope/payload minimization;
- Privacy executor protocol.

### Database/integration tests

- migrations, FK/target constraints, indexes, uniqueness, transaction rollback;
- idempotency claim/result + hold + outbox atomicity;
- concurrent equivalent creates;
- read filters/pagination and no unbounded joins;
- released history remains queryable.

### Authorization/security tests

- unauthenticated/unauthorized/step-up outcomes;
- internal system actor validation;
- IDOR and target enumeration attempts;
- owner-specific sensitive context redaction;
- direct client/foreign Module writes denied;
- oversized/malicious metadata rejected.

### Compliance tests

- hold does not mutate source-domain truth;
- release does not mark source approved;
- consumer uses `evaluateComplianceHold`, not raw rows/local booleans;
- `admin_hold`/`other` require structured provenance;
- fail-closed dependency behavior.

### Idempotency/concurrency tests

- same key/same payload replay;
- same key/different payload conflict;
- simultaneous semantic duplicates;
- concurrent releases and release/expiry race;
- duplicate event/job handling and notification/audit side effects.

### Provider adapter tests

None inside this Module. Contract fakes verify that provider-owning Modules deliver translated decisions; raw provider payloads are rejected.

### Privacy tests

- enumerate target/requester/releaser links;
- retained versus anonymized/erased fixtures under approved policy;
- ordinary clients cannot invoke executor;
- export minimization/cross-subject isolation;
- no local exemption truth.

### E2E participation

- source owner requests hold -> consumer action denied -> source owner supplies resolution -> hold released -> consumer action allowed;
- moderation action requests hold -> downstream action blocked;
- prize/payout association does not replace central gate;
- authorized reviewer views redacted context -> required `AccessAuditLog` exists;
- Privacy job invokes Hold executor and receives explicit result.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `ComplianceHold` is the sole reusable platform stop-sign truth.
2. Only this Module creates or changes `ComplianceHold.status`.
3. A hold never replaces the compliance/business record that justified it.
4. Release never updates or implies approval of KYC, tax, payout, verification, adverse action, healthcare, job compliance, moderation, dispute, prize, reward, identity/security, Order, or other foreign truth.
5. Consumers use `evaluateComplianceHold` for action applicability; raw hold rows and `blockedByHoldId` are insufficient.
6. A hold reason is not proof that the named condition currently exists.
7. Reason and blocked action scope are distinct and must be evaluated by Hold-owned policy.
8. Exactly one approved primary target is required once PR-CL09-04 is accepted; zero-target and ambiguous multi-target holds are invalid.
9. No general hold API is implemented before target, provenance, and semantic uniqueness decisions are accepted.
10. Retried/concurrent equivalent requests cannot create uncontrolled duplicate active holds.
11. Hold transitions are transaction-safe and database-concurrency-safe; in-memory locks are prohibited.
12. Released/expired holds are terminal under current policy and remain historical proof.
13. Automatic expiry is prohibited until U-13 defines due semantics and proof.
14. Durable assignment/claim/escalation is prohibited until U-11/PR-CL09-06 defines the record and shared mechanism.
15. Admin/service authority never bypasses source-owner release readiness, target validation, lifecycle rules, privacy, or audit.
16. Cross-Module reads/writes use public interfaces/events; no foreign Prisma repository or direct status write.
17. Raw sensitive source evidence and provider payloads are not stored in Hold notes/events/audit/telemetry.
18. Notification delivery, audit storage, operational telemetry, privacy orchestration, Search, and Media remain externally owned.
19. Required events use a transactional outbox; consumer effects use inbox/idempotency.
20. Audit events, domain events, source-domain histories, and Observability records remain distinct.
21. Privacy retention is based on approved owner facts and Privacy-owned exemptions, never an invented local flag.
22. Search never reconstructs public visibility from raw Hold reasons.
23. No provider client, credential, webhook, or provider-event dedupe table exists in this Module.
24. `admin_hold` and `other` cannot be used without structured provenance.
25. Dependency unavailability never becomes an implicit allow or release where the gate is mandatory.

---

## 34. Prohibited Duplicate Implementations

Do not generate:

- `isBlocked.ts`, `checkHold.ts`, `payoutHoldCheck.ts`, `jobBlockCheck.ts`, `contentHold.ts`, `canPayout.ts`, or consumer-local hold truth;
- `createPayoutHold.ts`, `createPrizeHold.ts`, `createModerationBlock.ts`, feature-local hold tables/enums/status setters;
- `holdAdminAuth.ts`, `adminGuard.ts`, `requireAdmin.ts`, `isAdmin.ts`, local role/MFA/session helpers;
- `findTargetByTypeAndId.ts` or a universal cross-domain Prisma repository;
- `holdIdempotency.ts`, `dedupeHold.ts`, local command-result store, in-memory mutex/lock;
- `holdOutbox.ts`, fire-and-forget event emitter, local queue runner, `holdQueue.ts`, retry/backoff loop, queue telemetry table;
- `holdAudit.ts`, `adminAuditLogger.ts`, `logComplianceAction.ts`, `reviewAccessLog.ts`, `financialReviewLog.ts`, local audit/access tables;
- `sendHoldEmail.ts`, `notifyReviewer.ts`, direct SES/SMS/push clients or notification delivery records;
- `stripeHoldMapper.ts`, `checkrHoldMapper.ts`, `providerRestrictionMapper.ts`, provider webhook/dedupe/reconciliation code;
- Typesense/SearchUpsertEvent/de-index code or R2/file/signed-URL code;
- local `PrivacyRequest`, `DataErasureJob`, `DataRetentionExemption`, generic data crawler, `retainForever`, or ad hoc scrubbing;
- universal `AdminReviewCase`, generic review queue merging Hold, Moderation, Job Compliance, Healthcare, and Verification;
- `holdEvidenceHash.ts` or generic evidence blob presented as immutable proof without the approved snapshot/hash design;
- a global compliance/readiness engine that owns foreign reason/status policy.

---

## 35. Unresolved Decisions

| ID | Decision | Why it matters / blocked scope |
| --- | --- | --- |
| U-10 / PR-CL09-04 | Exact typed target representation, target vocabulary, migration strategy, and cardinality | Blocks general `request/evaluateComplianceHold`; proposal is exactly one primary target |
| U-12 | Physical creation/source provenance fields and whether system actors need a dedicated representation | Blocks complete creation/release proof and schema contract |
| U-14 | Semantic equivalence key, active uniqueness constraint, idempotency retention, and create-race result | Blocks safe concurrent creation |
| Hold action scope | Stable action/scope vocabulary and reason/scope/action applicability matrix | Blocks production gate evaluation |
| U-11 / PR-CL09-06 | Whether review queue state is derived or a Hold-owned work-item/claim/escalation record exists; claim lease semantics | Blocks durable assignment/claim/escalation; base read-only queue may proceed |
| U-13 | Whether expiry is time-, event-, or manually based; expiry proof fields and reopen/replacement behavior | Blocks `expireComplianceHold` and expiry worker |
| U-15 | Which candidate/application/resume actions may be blocked and how target is represented | Blocks Candidate/Resume integration |
| Release authority | Exact source-owner release-readiness contract and circumstances, if any, for admin override | Blocks final authorization matrix; release must not become approval |
| Step-up matrix | Which hold review/release/export actions require fresh assurance | Blocks final high-risk action policy, not base contract stubs |
| Event registry | Permanent event names, versions, aggregate version field, and consumer list | Blocks freezing public event identifiers |
| Release/history proof | Whether enriched mutable hold fields + `AuditEvent` suffice or a Hold-owned immutable decision/history record is required | Blocks claims of full immutable lifecycle evidence |
| Evidence snapshot | Whether Hold uses `preserveEvidenceSnapshot`, its schema, Media relation, hash meaning, and retention | Blocks immutable high-impact review evidence |
| U-24 | Privacy target vocabulary and legal/financial/fraud/security retention bases/durations | Blocks production erasure/retention behavior |
| Reason vocabulary review | Whether MFA/recovery/security/provider/adverse-action reasons duplicate foreign lifecycle state | Blocks casual expansion/use of these reasons, not current schema recognition |
| Consumer association standard | Whether `blockedByHoldId` is merely local association/projection and how it is synchronized without becoming gate truth | Blocks standardization/backfill of consumer links |

Unresolved decisions must be accepted in root/Cluster/Module architecture before dependent code is implemented. A completion report may record a deliberate deferral; it may not hide an invented answer.

---

## 36. Architecture Decision Summary

### Binding confirmed rulings

1. The Module owns `ComplianceHold`, `ComplianceHoldReason`, `ComplianceHoldStatus`, hold lifecycle policy, action applicability, and release proof meaning.
2. `requestComplianceHold`, `evaluateComplianceHold`, and `releaseComplianceHold` are the canonical platform hold interfaces.
3. Source Modules own the conditions that justify creation or release; consumers own their reactions to a block decision.
4. Hold release is not source approval; terminal hold history is retained.
5. Cross-Module target/source context is consumed through owner interfaces with least privilege and redaction.
6. Audit, sensitive-access logging, Notification, Observability, Privacy orchestration, Search, Media, provider adapters, queues, locks, idempotency, and outbox mechanisms remain with their canonical owners.
7. The base admin queue may be a bounded projection over holds. It must not claim assignment/lease/escalation truth absent an approved schema.
8. No automatic expiration is implemented under current evidence.

### Proposed rulings inherited or required

- Adopt PR-CL09-04: one validated typed primary target per hold, replacing/augmenting the narrow nullable-FK design.
- Accept a concrete provenance/idempotency/semantic uniqueness design under U-12/U-14 before CL-09 Feature 04.
- Use `claimWorkItem` only after PR-CL09-06/U-11; Hold retains review policy.
- Use `preserveEvidenceSnapshot` only after proof ownership/schema/retention is approved.

### Explicitly deferred

Expiry, durable review assignment/escalation, candidate/resume applicability, permanent event names, exact retention periods, admin override conditions, and immutable decision-history design remain unresolved.

---

## 37. Coding-Agent Usage

Before implementing this Module, read in order:

1. root `context/project-overview.md`;
2. root `context/architecture.md`;
3. root `context/code-standards.md`;
4. Canonical Shared Operations Registry / Architecture;
5. CL-09 `architecture.md`;
6. CL-09 `build-plan.md`;
7. this `module-architecture.md`;
8. this `implementation-plan.md`;
9. relevant dependency public-interface sections, especially Identity & Access, Role / Authority, Audit, Notification, Privacy, Payment/Payout/Tax, Verification, Professional Eligibility, Job Compliance, Moderation, Dispute, Healthcare, Prize, Rewards, Candidate Privacy, Media, Search, and Observability as applicable;
10. the progress tracker and prior feature completion report.

Then:

- confirm every required Proposed Ruling has been explicitly accepted;
- inspect current Prisma and migrations before schema work;
- verify the previous numbered Module/Cluster exit gate;
- implement only the feature slice and Module-owned truth;
- use public owner contracts, not direct foreign tables;
- reuse canonical operations and platform primitives;
- run the feature's tests and contract/E2E verification;
- update progress and any legitimately changed binding architecture;
- record assumptions, known failures, remaining risks, and deferred decisions.

