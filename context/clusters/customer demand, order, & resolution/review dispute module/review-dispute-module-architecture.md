# Review / Dispute Module Architecture

> **Module ID:** `review_dispute`  
> **Module name:** Review / Dispute Module  
> **Primary Cluster:** CL-04 — Customer Demand, Order & Resolution  
> **Document role:** Binding Module-local architecture where evidence is confirmed; proposed rulings and unresolved decisions are explicitly non-binding until approved.

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

---

## 1. Module Header

| Field | Value |
| --- | --- |
| Module ID | `review_dispute` |
| Module name | Review / Dispute Module |
| Module type | `domain_compliance_support` |
| Build status | `mvp_active` |
| Primary Cluster | CL-04 — Customer Demand, Order & Resolution |
| Document status | Implementation-grade Module architecture. Confirmed rulings are binding; **Proposed Rulings** require explicit approval; unresolved decisions must block affected production implementation. |
| Intended audience | Coding agents, application/domain developers, reviewers, migration authors, test authors, maintainers, and operators implementing or reviewing Review / Dispute behavior. |
| Relationship to root architecture | Root Workin Ants rules govern platform-wide identity, authorization, shared primitives, provider boundaries, privacy, observability, and source-of-truth conventions. This file narrows those rules to `review_dispute`; it must not override stronger root rulings. |
| Relationship to Cluster architecture | CL-04 defines integration boundaries and sequencing across `gig_demand`, `transaction_order`, and `review_dispute`. This file is authoritative only for Review / Dispute-owned truth and local policy. |
| Relationship to Cluster build plan | This Module implements the Review / Dispute portion of CL-04 Feature 10 (Review), Feature 11 (Dispute intake/hold), Feature 12 (adjudication/settlement), and participates in Features 13–14 (cross-cluster proof and hardening). |
| Update rule | Update only when a binding Module decision changes: ownership, lifecycle semantics, public contract, schema meaning, cross-Module boundary, compliance behavior, or shared-operation use. Build progress alone must not redefine architecture. |

### Authority by concern

Follow [context/context-map.md](<../../../context-map.md>) authority by concern: Ubiquitous Language owns terminology; approved compliance material owns obligations; Prisma/migrations own persisted structure; the owning Module architecture owns lifecycle/API/invariants; Cluster architecture owns collaboration; Shared Operations owns SH identity/owner/status/boundaries; Cluster and Module plans own their respective sequence. No document class, timestamp, or file depth supplies a global precedence ladder.

---

## 2. Purpose, Goal, and Transformation

### Purpose

Own post-Order reputation feedback and commercial conflict adjudication while coordinating—without absorbing—the transaction, refund, payout, hold, moderation, communication, search, media, privacy, and audit capabilities that those outcomes affect.

### Goal

Produce a durable, explainable answer to two post-transaction questions:

1. **Review:** What eligible buyer feedback is authoritative for this completed Order, and may it currently contribute to Professional reputation?
2. **Dispute:** What commercial conflict was opened against this Order, what adjudication decision was made, and what downstream settlement effects are still pending or complete?

### What enters

- authenticated User/system actor context;
- resolved `CustomerProfile` buyer context for buyer-side Review actions;
- Order-owned participant, seller, completion, refund, and transaction facts;
- Review rating/comment input;
- dispute reason and approved evidence references;
- admin/support reviewer context and authority decisions;
- `ComplianceHold` decisions and hold references;
- normalized refund/release/settlement outcomes from the appropriate financial and Order owners;
- moderation outcomes affecting Review visibility;
- Media access decisions for dispute evidence;
- privacy instructions and retention decisions;
- correlation/idempotency context from shared platform primitives.

### What leaves

- authoritative `Review` state;
- authoritative `Dispute` state;
- Review publication/visibility decisions;
- dispute adjudication decisions;
- owner-defined Review/Dispute domain events through the shared outbox mechanism;
- requests to create/release `ComplianceHold` through the hold owner;
- refund requests through Transaction / Order's SH-108 `requestOrderRefund`; release/transaction effects through their approved owner interfaces;
- reputation recalculation inputs and Search projection refresh requests;
- notification intent;
- generic AuditEvent requests and sensitive-access audit requests;
- privacy executor results for Review/Dispute-owned data;
- operational failure/telemetry signals when coordination fails.

### Business transformation

```text
Completed/eligible Order + authorized buyer
→ Review eligibility decision
→ one authoritative Review
→ publication/visibility lifecycle
→ reputation effect
→ Search/notification/reward consumers react through contracts

Order + authorized participant/admin
→ dispute eligibility decision
→ one authoritative dispute case under approved multiplicity policy
→ review/adjudication
→ refund OR release decision
→ external Order/payment/hold effects through owner interfaces
→ settlement confirmation
→ case closure under approved lifecycle semantics
```

### Why this deserves its own Module boundary

Review and Dispute share post-Order context but own domain truth that is neither transaction truth nor moderation truth. The Module must preserve the distinction between:

- reputation feedback and verification;
- commercial adjudication and financial execution;
- commercial dispute and legal/moderation case;
- dispute-triggered hold request and `ComplianceHold` lifecycle;
- Review/Dispute state and generic audit/operational records.

Without this boundary, Order, Payment, Moderation, or ProfessionalProfile would be pressured to absorb unrelated post-transaction policy and lifecycle truth.

---

## 3. Owned Truth

### 3.1 Schemas / models owned

| Record | Plain-English meaning | Ownership status |
| --- | --- | --- |
| `Review` | Post-Order buyer feedback that may contribute to Professional reputation when the Review is in a reputation-eligible state. | Confirmed |
| `Dispute` | The commercial conflict case attached to an Order and the current adjudication lifecycle state. | Confirmed |

### 3.2 Enums/statuses owned

- `ReviewStatus`: `pending`, `published`, `hidden`, `removed`
- `DisputeStatus`: `open`, `under_review`, `resolved_refund`, `resolved_release`, `dismissed`, `closed`

### 3.3 Lifecycles owned

- Review lifecycle and visibility/reputation eligibility.
- Dispute case lifecycle and commercial adjudication outcome.

The Module alone may mutate `Review.status` and `Dispute.status`. External Modules may supply facts, gates, or formal moderation/settlement outcomes, but they must invoke this Module’s public commands rather than write these fields directly.

### 3.4 Source-of-truth records

- `Review` is Review source truth. Professional rating caches/projections are derived; Search documents are derived.
- `Dispute` is commercial dispute source truth. `ComplianceHold`, `RefundStatus`, `PayoutTransfer`, provider refund objects, `ModerationCase`, and operational records are separate truth owned elsewhere.

### 3.5 Domain events / ledgers owned

The Module owns the **meaning and emission policy** of Review/Dispute domain events. Shared outbox infrastructure owns transport mechanics.

Minimum event vocabulary to design around committed facts:

- `ReviewSubmitted`
- `ReviewPublished`
- `ReviewHidden`
- `ReviewRemoved`
- `DisputeOpened`
- `DisputeReviewStarted`
- `DisputeRefundResolved`
- `DisputeReleaseResolved`
- `DisputeDismissed`
- `DisputeClosed`

No `ReviewEvent` or `DisputeEvent` Prisma ledger is confirmed in the current schema. **The absence of a Module-owned lifecycle ledger is a known evidence/history gap, not permission to misuse `AuditEvent` as the domain ledger.**

### 3.6 Projections owned

The Module owns the policy that determines which Review records count toward Professional reputation and may compute a deterministic reputation aggregate. Current persistence fields `ProfessionalProfile.ratingAverage` and `ProfessionalProfile.ratingCount` are not Module-owned fields.

**Boundary:** until the owner/public contract for storing those derived fields is explicitly settled, `review_dispute` must not directly write `ProfessionalProfile` through a foreign repository.

### 3.7 Snapshots / proof owned

Current schema confirms no dedicated Review revision snapshot, Dispute evidence record, Dispute resolution record, or Dispute lifecycle ledger.

The Module does own:

- current Review state as evidence of publication/visibility;
- current Dispute state and `resolvedAt` where populated;
- the domain meaning of adjudication decision inputs and outputs.

**Proposed Ruling — not binding:** production dispute adjudication may require dedicated structured proof such as a `DisputeResolution` and/or `DisputeEvent`, and richer evidence references may require a `DisputeEvidence` contextual record. These must not be created until the corresponding schema rulings are approved.

### 3.8 Policies / invariants owned

- Review eligibility policy.
- Review target consistency with the Order seller.
- Review reputation-inclusion policy by Review status.
- Dispute eligibility policy.
- Dispute transition/adjudication policy.
- Rules mapping external settlement confirmation back into Dispute state.
- Rules deciding when a dispute requests a hold or hold release.
- Rules deciding when an Order conflict must be routed to Moderation/Legal rather than treated only as a commercial Dispute.
- Rules deciding what Review/Dispute information is safe to emit in events, notifications, logs, and projections.

---

## 4. Explicit Non-Ownership

| Adjacent owner | Responsibility that remains external | What `review_dispute` may do |
| --- | --- | --- |
| Identity & Access | Authentication, session truth, MFA/passkey challenges, step-up lifecycle. | Consume resolved actor and conditional step-up result. |
| Role / Authority | Generic permission interpretation. | Supply Review/Dispute relationship facts and named actions. |
| Customer / Buyer Profile | `CustomerProfile` lifecycle and buyer actor truth. | Resolve CustomerProfile for Review/dispute actions where buyer context is needed. |
| Transaction / Order | `Order`, `OrderStatus`, `OrderEvent`, Order participant/source truth, Order-attached `RefundStatus`. | Query minimum Order facts; request disputed/refund effects through public contracts. |
| Professional Eligibility | `ProfessionalProfile` lifecycle/readiness. | Consume seller facts if needed; supply reputation outcome/projection input without owning profile lifecycle. |
| Payment / Payout / Tax | Payment/refund provider rail, Stripe webhook verification/dedupe, provider status mapping, payout ledger, payout execution, KYC/tax. | Route refund decisions through Transaction / Order SH-108; consume settlement results and use approved payout/release reevaluation interfaces without calling Payment's refund executor. |
| Admin Review / Compliance Hold | `ComplianceHold` record and create/release/expire lifecycle. | Request/evaluate/release holds using canonical operations. |
| Content Moderation & Legal Notice | `Report`, `LegalNotice`, `ModerationCase`, `ModerationAction`, legal/content adjudication. | Route applicable Review/dispute issues and consume formal moderation outcome. |
| Media / File Access | `MediaAsset`, upload validation, malware scanning, object storage, signed URL mechanics, `MediaAccessGrant`. | Own contextual dispute-evidence meaning only if/when an evidence schema is approved; consume signed access. |
| Messaging | `Thread`, `ThreadParticipant`, `Message`, `MessageMedia`. | Use Order/support thread context through Messaging interface; never create a shadow dispute chat system. |
| Notification | Notification records, templates, channel routing, delivery attempts, provider callbacks. | Request notifications with safe intent/variables. |
| Search / Public Visibility | `SearchUpsertEvent`, Typesense adapter, indexing, reconciliation, search query surface. | For Professional reputation, hand the Review aggregate to Professional Eligibility; Search receives its resulting Professional projection. |
| Audit / Event Ledger | Generic `AuditEvent`, `AccessAuditLog`. | Request generic audit/access evidence while retaining separate domain truth. |
| Privacy / Data Erasure | `PrivacyRequest`, erasure/export orchestration, `DataRetentionExemption`. | Enumerate/execute instructions against owned Review/Dispute data. |
| Observability / Ops | `IntegrationFailure`, `SystemEvent`, `QueueJob`, `OpsIncident`, logger/metrics/incident stack. | Emit safe operational telemetry and failure reports. |
| Gamification / Rewards | Points, reward rules, `PointLedgerEntry`. | Emit eligible Review facts; never award points directly. |

### Explicit provider prohibition

The historical Module registry lists “Stripe refund APIs” as technology, but stronger boundary evidence states Payment / Payout / Tax owns processor rail and refund execution. Therefore:

> **No Stripe client, webhook endpoint, signature verification, `ProcessedStripeEvent`, provider refund mapper, or direct refund call may be implemented inside `review_dispute`.**

---

## 5. Module Architecture Principles

1. `Review` and `Dispute` are the only confirmed Module-owned source records.
2. `Order` remains transaction truth; this Module consumes Order facts through public contracts.
3. CustomerProfile is buyer actor truth for new buyer-domain writes; User is authentication/audit identity.
4. Review is reputation feedback, never verification, licensing, KYC, or TrustBadge truth.
5. A dispute adjudication is not the same thing as refund execution, Order refund attachment, payout release, or hold release.
6. `ComplianceHold` is the only reusable platform stop sign; no local blocked/payout-hold boolean may be created.
7. Commercial disputes and moderation/legal cases remain separate lifecycles even when one triggers the other.
8. Shared mechanisms may be reused without merging Review/Dispute lifecycle truth into generic infrastructure.
9. Cross-Module facts are consumed through owner contracts by default, not unrestricted Prisma repositories.
10. Every retryable commercial mutation is idempotent.
11. Every competing lifecycle mutation uses database/platform concurrency primitives.
12. Events describe committed facts; they are not cross-Module commands in disguise.
13. External effects that can fail independently must not be the only copy of Review/Dispute truth.
14. Search, notification, audit, and observability failures must not roll back already committed source truth when asynchronous retry is architecturally appropriate.
15. Unresolved product/legal/schema decisions are implementation gates, not blanks coding agents may fill.

---

## 6. Proposed Folder / Code Structure

```text
src/modules/review-dispute/
  application/
    reviews/
      commands/
      queries/
      services/
    disputes/
      commands/
      queries/
      services/
    resolution/
      services/
      workflows/
    privacy/
      executor.ts
      inventory.ts
    contracts/

  domain/
    review/
      review-policy.ts
      review-transitions.ts
      review-events.ts
    dispute/
      dispute-policy.ts
      dispute-transitions.ts
      dispute-events.ts
    reputation/
      reputation-policy.ts
    decisions/
      reason-codes.ts

  infrastructure/
    repositories/
      review-repository.ts
      dispute-repository.ts
    workers/
      dispute-settlement-worker.ts
      reputation-rebuild-worker.ts

  public/
    contracts.ts
    index.ts

  ui/
    reviews/
    disputes/
    admin/

  tests/
    unit/
    contract/
    integration/
    authorization/
    concurrency/
    privacy/
    e2e/
```

### Structure rules

- `infrastructure/providers/` is intentionally absent because the Module owns no external provider integration.
- Do not create a Module-local `auth/`, `authorization/`, `idempotency/`, `queue/`, `outbox/`, `search/`, `media/`, or `notifications/` infrastructure package.
- `workers/` contains only Module-owned asynchronous workflow handlers using the shared queue runner.
- `ui/admin/` may contain dispute-specific queue/detail/adjudication views, but not a platform-wide admin shell.
- A `DisputeEvidence` repository/folder must not be created until an evidence schema is approved.
- Domain transition files contain Review/Dispute-specific graphs/reason rules only; generic state-machine plumbing remains shared.

---

## 7. Internal Boundaries

| Layer / Area | Owns | Must not own |
| --- | --- | --- |
| Delivery / UI | Review submission/status views; participant dispute intake/status; dispute-specific admin queue/detail/adjudication controls. | Authentication implementation, platform admin shell, Stripe UI/provider logic, Notification delivery, Media signed URL generation. |
| Application services | Command/query orchestration; dependency calls; transaction boundaries; idempotency invocation; workflow coordination. | Generic shared primitives or direct mutation of another Module’s records. |
| Domain policy | Review eligibility; Review status/reputation inclusion; dispute eligibility; dispute transition/adjudication policy; hold-request criteria. | Permission interpretation, payment provider status mapping, ComplianceHold lifecycle, moderation/legal policy. |
| Repositories / data access | Reads/writes for `Review` and `Dispute` only, plus transactionally coupled owner-local state if later approved. | Cross-domain repositories for Order, ProfessionalProfile, ComplianceHold, Payment, Media, Notification, Search, Audit. |
| Workers | Reputation rebuild coordination and dispute settlement/reconciliation steps owned by this Module. | Generic scheduler/queue mechanics, provider webhook workers, Search workers, Notification workers. |
| Adapters | Owner-specific public contract clients/ports to other Modules where repository architecture requires them. | External provider adapters such as Stripe or Typesense. |
| Public contracts | Stable Review/Dispute commands, queries, events, privacy executor. | Internal repository models, provider-native DTOs, neighboring lifecycle details. |

---

## 8. Data Model

### 8.1 `Review`

**Purpose:** one post-Order feedback record used as Review source truth and as input to Professional reputation.

**Current authoritative fields:** `id`, `orderId`, `reviewerUserId?`, `professionalProfileId?`, `rating`, `comment?`, `status` default `pending`, `createdAt`.

**Relationships and constraints:**

- required relation to `Order` with `onDelete: Cascade`;
- optional relation to `ProfessionalProfile`;
- `orderId` is unique, so current schema permits at most one Review per Order;
- indexes on `(professionalProfileId, rating)`, `reviewerUserId`, and `status`.

**Current integrity gaps / architecture gates:**

- `reviewerUserId` is optional and lacks a Prisma relation;
- CustomerProfile is buyer actor truth but Review has no CustomerProfile relation;
- `professionalProfileId` is optional even though reputation feedback targets the Order seller;
- no DB-level rating-range constraint is evidenced;
- no `updatedAt` or version field exists;
- no revision/edit history exists;
- cascade deletion may conflict with later retention/privacy policy.

**Confirmed CL-04-R007:** a new Review author resolves to the Order's buyer CustomerProfile; User remains account/audit identity. Exact migration/backfill shape remains unresolved.

### 8.2 `Dispute`

**Purpose:** one current commercial conflict case attached to an Order under the current schema.

**Current authoritative fields:** `id`, `orderId`, `openedById?`, `reason`, `status` default `open`, `adminNotes?`, `createdAt`, `resolvedAt?`.

**Relationships and constraints:**

- required relation to `Order` with `onDelete: Cascade`;
- `orderId` is unique, so current schema allows only one Dispute row per Order;
- indexes on `status` and `openedById`.

**Current integrity/proof gaps:**

- `openedById` is optional and not relationally typed as User, CustomerProfile, ProfessionalProfile, or admin actor;
- one-Dispute-per-Order intent is unresolved;
- `adminNotes` is a mutable free-text blob and must not become the only case timeline/evidence/decision record;
- no dedicated evidence relation, structured resolution record, domain event ledger, or workflow correlation field is confirmed;
- no `updatedAt` or version field exists;
- cascade deletion may conflict with dispute/financial/legal retention requirements.

**Proposed Ruling:** production dispute adjudication should preserve structured decision/evidence/correlation proof rather than relying solely on `adminNotes`; exact schema remains unresolved.

### 8.3 External data referenced, not owned

- `Order` and `RefundStatus`
- `CustomerProfile`
- `ProfessionalProfile`
- `ComplianceHold`
- `PayoutTransfer` and normalized refund/payment results
- `AuditEvent`, `AccessAuditLog`
- `Notification`
- `Thread`
- `MediaAsset`/OrderFile/MessageMedia as evidence sources

A foreign key or Prisma relation does not grant write ownership.

## 9. Enums, Statuses, and Lifecycles

### 9.1 `ReviewStatus`

Known values:

```text
pending
→ published
→ hidden
→ removed
```

The enum vocabulary is confirmed; the complete transition graph is not.

| Status | Confirmed meaning | Allowed transition guidance |
| --- | --- | --- |
| `pending` | Review exists but is not yet confirmed as public reputation. | May transition only according to an approved publication/moderation policy. |
| `published` | Review is eligible for normal public/reputation consumption. | May be hidden or removed by an authorized Review / Dispute command. |
| `hidden` | Review is not presently public/reputation-bearing. | Re-publication is unresolved; do not invent it. |
| `removed` | Review is removed from ordinary product/public use. | Treat as product-state removal, not legal erasure. Reversal is unresolved. |

**Transition owner:** Review / Dispute only.

**Known triggers:**

- buyer submission creates the Review in the approved initial state; current schema default is `pending`;
- authorized publication/moderation action may change visibility;
- a formal moderation outcome may be an input, but Content Moderation does not write Review state directly.

**Terminal state:** not fully settled. `removed` appears terminal in current evidence, but this is not explicitly confirmed.

**Concurrency expectation:** publication/hide/remove commands must reject stale conflicting transitions through the canonical lifecycle/concurrency mechanism.

**History proof:** no Review-specific event table is confirmed. If Review history becomes necessary, use the shared SH-031 `appendDomainLifecycleEvent` persistence pattern with Review-owned event meaning or a transactional outbox; do not use generic `AuditEvent` as a substitute for lifecycle truth.

**Prohibited shortcuts:**

- no direct `status` update from Search, Professional Eligibility, Moderation, or an admin UI;
- no `isPublished`/`isHidden` shadow booleans;
- no treating `removed` as privacy erasure;
- no treating rating/publication state as verification truth.

### 9.2 `DisputeStatus`

Known values:

```text
open
→ under_review
→ resolved_refund | resolved_release | dismissed
→ closed
```

This is an architectural visualization, not a finalized transition matrix. In particular, the meaning of `resolved_*` versus `closed` remains unresolved.

| Status | Confirmed meaning | Boundary |
| --- | --- | --- |
| `open` | Commercial conflict case has been opened against an Order. | Does not itself prove a ComplianceHold exists or an Order refund was requested. |
| `under_review` | Review / Dispute is actively adjudicating the case. | Does not transfer ownership to a generic admin queue. |
| `resolved_refund` | Adjudication favors a refund outcome. | Must not be interpreted as provider refund completion. |
| `resolved_release` | Adjudication favors release/no-refund outcome. | Must not be interpreted as payout transfer completion or hold release. |
| `dismissed` | Case ended without refund/release adjudication under an approved dismissal reason. | Exact dismissal reasons are unresolved. |
| `closed` | Case has reached the Module-defined final closed condition. | Exact prerequisites for closure are unresolved. |

**Transition owner:** Review / Dispute only.

**Triggers:**

- authorized participant opens;
- authorized reviewer begins review;
- authorized adjudicator records refund/release/dismissal decision;
- normalized settlement/hold completion facts may permit later closure.

**Terminal states:** unresolved. `closed` appears intended as final, while `dismissed` may be terminal or may be followed by `closed`.

**Reopen rule:** unresolved. Current `orderId @unique` prevents multiple case rows but does not define reopening semantics.

**Concurrency expectation:** only one competing adjudication may win. Use aggregate locking or optimistic concurrency; never process refund-vs-release decisions concurrently without conflict protection.

**History proof:** current `Dispute` is insufficient to reconstruct adjudication sequence. Structured lifecycle proof is a required architecture decision before production-grade adjudication.

**Prohibited shortcuts:**

- no direct write of `RefundStatus`;
- no local payout-block flag;
- no `resolved_refund` merely because a provider request was submitted;
- no `resolved_release` merely because a hold-release command was sent;
- no automatic close until the closure semantics are approved.

---

## 10. Commands

The commands below are Module-owned mutations. Exact API transport is repository-specific; the names represent stable application/domain contracts.

| Command | Purpose | Required actor/context | Authoritative inputs | Preconditions | State written | Shared operations/effects | Idempotency / failure expectations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `submitOrderReview` | Create the one Review associated with an eligible Order. | authenticated actor + resolved CustomerProfile | `orderId`, rating, optional comment, idempotency key | Order facts say reviewable; buyer controls Order; no existing Review; approved rating scale | `Review` | SH-001 `resolveAuthenticatedActor`, SH-004 `resolveCustomerActor`, SH-002 `authorizeResourceAction`, SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite), SH-044 `executeIdempotentCommand`, SH-046 `publishDomainEvent`, SH-029 `appendAuditEvent`, optional SH-041 `requestNotification` | retry must replay same semantic result; duplicate non-matching attempt returns conflict |
| `publishReview` | Move an eligible Review into reputation-bearing public state. | authorized admin/system actor under approved publication policy | review ID, expected version/state, reason/context | transition permitted; no moderation/hold policy blocks it if such gate is approved | `Review.status` | SH-002 `authorizeResourceAction`, SH-053 `transitionLifecycleState`, SH-046 `publishDomainEvent`, SH-029 `appendAuditEvent` | stale state conflicts; projection failure does not roll back Review truth |
| `hideReview` | Remove Review from public/reputation contribution without erasing it. | authorized admin/system actor | review ID, reason, expected state | legal transition | `Review.status` | lifecycle transition, audit, domain event, downstream projection refresh | repeat same intent is replay-safe |
| `removeReview` | Mark Review removed from ordinary product/public use. | authorized admin/system/privacy-integrated path as applicable | review ID, reason, expected state | legal transition and retention/privacy rule | `Review.status` and any approved removal metadata | lifecycle transition, audit, domain event | removal is not legal erasure; stale transition conflicts |
| `applyReviewModerationDecision` | Translate an authoritative moderation outcome into Review-owned visibility state. | verified internal event/system actor | review ID, moderation decision reference, desired approved Review action, event ID | decision references this Review; handler not already applied | `Review.status` only | SH-045 `deduplicateDomainEvent`, lifecycle transition, audit, publish event | must not create/alter ModerationCase truth |
| `openOrderDispute` | Create an Order-bound commercial conflict and start coordination. | authenticated authorized Order participant | Order ID, opener context, reason, approved evidence references, idempotency key | Order may be disputed; opener authorized; multiplicity rule permits case | `Dispute` | auth/authority, idempotency, domain event, audit, durable workflow, SH-012 `requestComplianceHold`, Order dispute-effect handoff, notification | Dispute truth may commit before an external hold succeeds; failed coordination is retried, not faked |
| `beginDisputeReview` | Move an open case into active review. | authorized admin/reviewer | dispute ID, expected state, optional assignment/context | legal transition and reviewer authority | `Dispute.status` plus approved reviewer/history proof | authority, SH-053 `transitionLifecycleState`, audit, event | competing claim/review action conflicts or uses shared work-item claim |
| `recordDisputeEvidenceReference` | Attach stable references to evidence owned elsewhere. | authorized participant/reviewer | dispute ID, evidence target type/ID, submitter context, description if allowed | evidence accessible and contextually relevant; schema approved | approved dispute-context evidence record/reference | authority, Media/context access, sensitive-access audit when read | unavailable until evidence-reference schema is approved; must never copy raw storage mechanics |
| `addDisputeAdminNote` | Add internal case commentary without pretending the note is lifecycle truth. | authorized admin/reviewer | dispute ID, note, actor | case exists; authority passes | current `adminNotes` only if retained, preferably approved append-only note record | audit, telemetry sanitization | mutable blob must not be used as sole adjudication proof |
| `resolveDisputeWithRefund` | Record adjudication favoring refund and start owner-separated settlement workflow. | authorized adjudicator; SH-014 required for financial movement | dispute ID, resolution basis, approved amount if applicable, expected state, idempotency key | dispute reviewable; no competing final decision; resolution schema/rules approved | Review / Dispute-owned adjudication state/proof | idempotency, lock/concurrency, lifecycle event, audit, workflow enqueue, notification | does not write Order RefundStatus or call Stripe |
| `resolveDisputeWithRelease` | Record adjudication favoring release/no refund and start owner-separated release workflow. | authorized adjudicator; SH-014 required for financial movement | dispute ID, resolution basis, expected state, idempotency key | same as above | Module-owned adjudication state/proof | same shared mechanisms; hold-release/payout reevaluation through owners | does not assert payout was released |
| `dismissDispute` | End a case under an approved dismissal rule. | authorized adjudicator/reviewer | dispute ID, reason, expected state | dismissal transition allowed | `Dispute.status` and approved decision proof | lifecycle transition, audit, event, notification; hold reevaluation if policy says | exact dismissal policy unresolved |
| `applyOrderSettlementResultToDispute` | Apply normalized external-owner settlement facts back to the dispute workflow. | trusted internal event/system actor | dispute ID/correlation, normalized Order/Payment result, event ID | result matches active workflow/correlation; not already applied | approved settlement progress and potentially Dispute transition/close | SH-045 `deduplicateDomainEvent`, lifecycle transition, audit, workflow reconciliation | raw provider payload/status is prohibited |
| `closeDispute` | Make the dispute final only after approved closure conditions are met. | authorized system/reviewer | dispute ID, expected state, required downstream completion evidence | closure semantics approved and all required prerequisites met | `Dispute.status=closed`, `resolvedAt` as defined | transition, audit, event, notification | must fail closed if settlement/hold state is ambiguous |
| `executeReviewDisputePrivacyInstruction` | Apply a Privacy-owned instruction to Review / Dispute data. | trusted Privacy workflow | instruction ID, target record, operation, retention decision/reference | validated Privacy instruction; retention decision satisfied | owner records only | privacy protocol, audit/observability as required | must not create a local PrivacyRequest workflow |

### Command result requirements

Every public mutation should use stable application-level result categories rather than leak Prisma/provider exceptions. Where a decision precedes mutation, return safe reason codes and evidence references without exposing private provider/compliance details.

---

## 11. Queries / Decisions

| Query / decision | Consumers | Input | Result kind | Stable meaning | Consumer must not infer |
| --- | --- | --- | --- | --- | --- |
| `evaluateReviewEligibility` | buyer UI, Order workflow, tests | actor/CustomerProfile + Order ID | decision | whether this buyer may submit a Review now, with safe reason codes | Order state by reading Review tables; verification status |
| `getOrderReview` | Order UI, buyer/seller views, support | Order ID + requester context | source truth view | authoritative Review for one Order if caller may see it | public visibility from existence alone |
| `listProfessionalReviews` | Professional profile/reputation surfaces | ProfessionalProfile ID, visibility filter, pagination | source-truth-backed read | Review rows eligible for caller/surface | verification/readiness or Search ranking |
| `getProfessionalReputationFacts` | Professional Eligibility/presentation/reputation projection | ProfessionalProfile ID | contextual facts/projection input | counts/ratings derived strictly from Review-owned inclusion policy | TrustBadge or compliance readiness |
| `evaluateDisputeEligibility` | participant UI, Order UI | actor context + Order ID + proposed reason/category if applicable | decision | whether an Order-bound commercial dispute may be opened | that refund will be granted or hold will exist |
| `getOrderDispute` | Order UI, participants, admins, Payment/Hold context | Order ID + requester | source truth view | current Dispute attached to Order | provider settlement state beyond owner-provided facts |
| `listDisputesForActor` | participant account surfaces | actor/profile + filters + pagination | source truth list | disputes caller is allowed to know about | unrestricted evidence access |
| `listDisputeReviewQueue` | admin/reviewer surface | reviewer context, status filters, pagination | review work view | cases eligible for review; may include safe owner-fact summaries | blanket access to Media/messages/contracts |
| `getDisputeResolutionStatus` | participants, Order/Payment support | dispute ID | source truth + normalized workflow facts | adjudication state and separately labelled settlement/hold progress | that `resolved_*` equals provider settlement |
| `enumerateReviewDisputeSubjectData` | Privacy / Data Erasure | data subject + request context | privacy inventory | Review/Dispute records and owner-local data eligible for privacy processing | automatic deletion or retention decision |

### Decision reason-code guidance

Reason codes should be stable and domain-oriented, for example:

- `order_not_reviewable`
- `actor_not_order_buyer`
- `review_already_exists`
- `rating_invalid`
- `order_not_disputable`
- `actor_not_order_participant`
- `dispute_already_exists`
- `dispute_transition_not_allowed`
- `resolution_already_decided`
- `settlement_pending`
- `hold_state_pending`
- `architecture_ruling_required`

Do not encode provider names or internal SQL errors into public reason codes.

---

## 12. Public Module Interface

Other Modules should consume this surface rather than read/write Review / Dispute repositories directly.

### Public commands

- `submitOrderReview`
- `publishReview`
- `hideReview`
- `removeReview`
- `applyReviewModerationDecision`
- `openOrderDispute`
- `beginDisputeReview`
- `recordDisputeEvidenceReference` — only after schema ruling
- `addDisputeAdminNote` — only if current note model remains approved
- `resolveDisputeWithRefund`
- `resolveDisputeWithRelease`
- `dismissDispute`
- `applyOrderSettlementResultToDispute`
- `closeDispute`

### Public queries / decisions

- `evaluateReviewEligibility`
- `getOrderReview`
- `listProfessionalReviews`
- `getProfessionalReputationFacts`
- `evaluateDisputeEligibility`
- `getOrderDispute`
- `listDisputesForActor`
- `listDisputeReviewQueue`
- `getDisputeResolutionStatus`

### Emitted domain events

At minimum, design versioned facts for:

- `ReviewSubmitted`
- `ReviewPublished`
- `ReviewHidden`
- `ReviewRemoved`
- `DisputeOpened`
- `DisputeReviewStarted`
- `DisputeRefundResolved`
- `DisputeReleaseResolved`
- `DisputeDismissed`
- `DisputeClosed`

Exact event schemas, names, and versions remain Module-owned.

### Privacy executor

- `enumerateReviewDisputeSubjectData`
- `executeReviewDisputePrivacyInstruction`

The Privacy / Data Erasure Module owns the request/job/target lifecycle; these are data-owner participation contracts.

### Provider-facing interfaces

None are owned by this Module. Review / Dispute consumes normalized owner contracts only.

---

## 13. Inbound Dependencies

| Owning Module / capability | Public operation/interface consumed | Why required | Minimum information | May block action? | Must not be copied locally |
| --- | --- | --- | --- | --- | --- |
| Identity & Access | SH-001 `resolveAuthenticatedActor` | establish trusted User/system actor | actor ID, actor kind, assurance context | yes | session parsing/current-user helper |
| Customer / Buyer Profile | SH-004 `resolveCustomerActor` | identify buyer commercial actor for Review and buyer-side dispute | customerProfileId linked to authenticated User | yes | buyer identity on User or local customer mapping |
| Role / Authority | SH-002 `authorizeResourceAction` | interpret participant/admin permission | action + Review/Dispute relationship facts | yes | feature-local RBAC/role engine |
| Transaction / Order | owner-fact query (SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) pattern) | Review/dispute requires Order status, participants, seller, refund/dispute effects | Order ID/version, customerProfileId, sellerProfessionalProfileId, relevant status/refund facts | yes | Order repository or status reconstruction |
| Transaction / Order | dispute/refund public commands and normalized outcome events | attach transaction effect to Order | Order/dispute correlation + normalized decision/outcome | yes/downstream | direct Order writes |
| Professional Eligibility / Profile owner | minimum ProfessionalProfile/reputation projection contract | validate target and surface rating projection | ProfessionalProfile ID; projection update/accepted facts | no for existing Review truth; may block invalid target at submit | Profile repository writes |
| Admin Review / Compliance Hold | SH-011 `evaluateComplianceHold`, SH-012 `requestComplianceHold`, SH-013 `releaseComplianceHold` | reusable payout/action stop sign | target, reason, source/evidence refs, hold ID/status | yes | local hold table/boolean |
| Payment / Payout / Tax | refund execution behind Transaction / Order SH-108; approved release/settlement interfaces | execute provider financial effect; Order returns refund settlement | Order/dispute correlation, approved amount/basis; normalized result | downstream through Order for refunds | direct refund-executor call, Stripe client, webhook verification/dedupe, payout ledger |
| Media / File Access | contextual Media access + SH-087 `issueSignedMediaUrl` | safe dispute evidence retrieval | media ID/context, authorized actor, purpose | yes for evidence read | R2/S3 client, signed URL helper, scan/validation |
| Messaging | context-thread facts/interfaces | case communication when approved | Order/support context and participant facts | possibly | Thread/Message lifecycle or participant ACL |
| Content Moderation & Legal Notice | report/moderation public interface; moderation result events | route abuse/legal/content issues and apply resulting Review visibility action | target Review/related evidence, moderation action reference | yes for visibility action | Report/ModerationCase/LegalNotice tables |
| Notification | SH-041 `requestNotification` | participant/admin alerts | recipients/context or owner recipient facts, template intent, safe variables | no to committed domain truth | email/SMS/push provider |
| Audit / Event Ledger | SH-029 `appendAuditEvent`, SH-030 `recordSensitiveAccess` | generic proof and protected evidence-access proof | safe actor/action/target/outcome/request context | normally no to domain commit unless required control fails closed by policy | audit/access tables |
| Search / Public Visibility | SH-091 `requestSearchProjectionRefresh` through Professional Eligibility after its Profile update | refresh professional public reputation projection | target profile/entity ID, source version/reason | no to Review truth | Typesense/SearchUpsertEvent writes |
| Privacy / Data Erasure | privacy executor protocol + retention decision | legal data-rights orchestration | instruction, target, exemption decision/ref | yes for destructive action | PrivacyRequest/erasure orchestrator |
| Observability / Ops | request context/log/failure primitives | operational visibility | safe correlation, operation, failure class | no | local Sentry/logger/incident system |

---

## 14. Outbound Consumers and Effects

| Consumer | Source fact/event | Permitted effect | Boundary |
| --- | --- | --- | --- |
| Transaction / Order | `DisputeOpened`, adjudication, settlement status | apply Order dispute/refund attachment through owner command | Review / Dispute never writes Order directly |
| Payment / Payout / Tax | refund decision coordinated by Transaction / Order SH-108; approved release reevaluation | execute provider-neutral financial effect / reevaluate payout | no direct Review / Dispute call to Payment refund executor; no direct Dispute mutation |
| Admin Review / Compliance Hold | dispute open/resolution evidence | create/evaluate/release hold | hold lifecycle stays external |
| Professional reputation/Profile presentation | Review publication changes | rebuild/update rating projection through approved contract | Review determines inclusion policy; Profile does not reinterpret raw statuses |
| Search / Public Visibility | resulting Professional projection after the Review aggregate handoff | refresh public projection | Search owns SearchUpsertEvent/Typesense; disputes are not public search docs |
| Notification | Review/Dispute lifecycle event | route/deliver alert | delivery truth stays Notification-owned |
| Audit / Event Ledger | significant action/access intent | append AuditEvent/AccessAuditLog | generic audit does not replace Review/Dispute lifecycle |
| Content Moderation | Review/dispute content concern | open Report/ModerationCase and issue moderation outcome | moderation case remains separate from Dispute |
| Messaging | approved case/order communication trigger | create/use context-bound thread/message | Review / Dispute does not own thread lifecycle |
| Privacy / Data Erasure | subject-data inventory/executor | orchestrate erasure/export/retention | Privacy does not mutate through raw Review/Dispute repository |
| Gamification / Rewards | `ReviewPublished` or other explicitly approved source event | evaluate reward rule | Review / Dispute never writes point/reward truth |
| Observability / Ops | operational failure/metrics | diagnostics, incident visibility | SystemEvent/IntegrationFailure never become domain status |

Cross-Module effects must be commands/events against owner interfaces. A convenient foreign key is not permission to mutate another Module’s table.

---

## 15. Canonical Shared Operations Used

Use the permanent IDs, canonical owners, and statuses in [Shared Operations](<../../../shared/shared-operations.md>). Confirmed references retain their registered boundaries; proposed references are conditional only.

| Canonical operation | Classification / owner | Why used here | Invocation point | Module-specific policy retained here | Expected result | Prohibited local duplicates |
| --- | --- | --- | --- | --- | --- | --- |
| SH-001 `resolveAuthenticatedActor` | canonical shared capability — Identity & Access | establish trusted actor | every protected command/query | what Review/Dispute action is attempted | typed actor context | `reviewAuth.ts`, `disputeAuth.ts`, `getCurrentUser.ts` |
| SH-004 `resolveCustomerActor` | another Module public interface — Customer / Buyer Profile | resolve buyer identity | Review submission and buyer dispute actions | whether CustomerProfile is eligible participant | customer actor facts | `buyerResolver.ts`, User-only buyer helper |
| SH-002 `authorizeResourceAction` | canonical shared capability — Role / Authority | permission interpretation | before protected Review/Dispute action | relationship facts and action vocabulary | allow/deny with safe reason | `reviewPermissions.ts`, `disputeRbac.ts` |
| SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) | shared contract / separate implementations — source owner | get minimum Order/participant facts | eligibility and workflows | which Order facts are required | versioned owner DTO | cross-domain `orderRepository` in this Module |
| SH-011 `evaluateComplianceHold` | canonical shared capability — Hold owner | check applicable stop signs | selected actions/settlement | which actions a hold blocks | active hold decision | `isPayoutBlocked`, `disputeBlocked` |
| SH-012 `requestComplianceHold` | canonical shared capability — Hold owner | request authoritative stop sign | after Dispute opens | when dispute justifies hold and evidence supplied | hold ID/result | local hold model/service |
| SH-013 `releaseComplianceHold` | canonical shared capability — Hold owner | request hold release | approved resolution/settlement | whether source condition is resolved | release result | `unblockPayout.ts` writing hold table |
| SH-014 `requireStepUpForSensitiveAction` | canonical shared capability — Identity & Access | refund/release adjudication causing or authorizing financial movement | refund/release admin action | financial refund/release movement requires SH-014; other action rules remain unresolved | assurance decision/session | local OTP/MFA |
| SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) | shared contract / separate policy | consistent eligibility decisions | review/dispute policy queries | reason namespace and evidence meaning | allow/deny/warn/review structure | universal compliance policy engine |
| SH-044 `executeIdempotentCommand` | platform primitive | retry-safe commercial mutations | submit/open/resolve/settlement commands | semantic command identity/replay | original or new result | `reviewDedupe.ts`, `disputeIdempotency.ts` |
| SH-051 `acquireAggregateLock` | platform primitive | serialize conflicting adjudication/state changes | dispute resolution, critical review transitions if needed | lock key/conflict policy | exclusive transaction scope | in-memory mutex, custom lock table |
| SH-052 `withOptimisticConcurrency` | platform primitive | reject stale transitions | update transitions | retry/merge/conflict semantics | compare-and-set result | hand-rolled `updatedAt` checks |
| SH-053 `transitionLifecycleState` | shared mechanism / separate truth | reusable state-machine plumbing | every status mutation | ReviewStatus/DisputeStatus graph | valid transition result | global lifecycle policy table |
| SH-031 `appendDomainLifecycleEvent` | shared mechanism / separate truth | immutable transition/history mechanics if approved | same transaction as owner state | event names/meaning/retention | append-only domain record | universal Event replacing domain truth |
| SH-046 `publishDomainEvent` | platform primitive — outbox | reliable downstream facts | after committed state | event schema/privacy/emission rule | durable outbox event | fire-and-forget event bus calls |
| SH-045 `deduplicateDomainEvent` | platform primitive — consumer inbox | prevent repeated settlement/moderation side effects | inbound event handlers | handler identity/side effect | one applied consumer effect | ordinary-event bespoke processed table |
| SH-047 `enqueueReliableJob` | platform primitive — queue | durable reputation/settlement work | after source transaction | job payload and success meaning | persisted job | `disputeQueue.ts` custom queue |
| SH-048 `executeRetryWithBackoff` | platform primitive — queue | retry transient dependencies | workers/workflow steps | retryability classification | bounded retry/dead-letter | custom retry loops |
| SH-049 `orchestrateWorkflowSteps` | shared mechanism / separate workflow truth | coordinate dispute settlement owners | after adjudication/open | exact step sequence and completion policy | durable workflow progress | one global saga owning Dispute status |
| SH-050 `reconcileWorkflowStatus` | shared mechanism / separate policy | combine child step outcomes | settlement workflow | what partial/complete means | deterministic workflow status | generic status owning business semantics |
| SH-054 `claimWorkItem` | cross-cutting capability, proposed | prevent simultaneous admin review | review-queue claim if adopted | reviewer eligibility/lease/escalation | claim/lease | local mutable `assignedTo` without locking |
| SH-029 `appendAuditEvent` | canonical shared capability — Audit / Event Ledger | generic action proof | significant mutations/admin actions | safe metadata and which actions audit | AuditEvent ID/result | `reviewAuditLog`, `disputeAuditTable` |
| SH-030 `recordSensitiveAccess` | canonical shared capability — Audit / Event Ledger | evidence access proof | private evidence issue/view/download | sensitivity/context authorization | access audit result | `disputeFileViewLog` substitute |
| SH-041 `requestNotification` | canonical shared capability — Notification | lifecycle alerts | post-commit events/workflow | intent/recipient meaning and safe variables | notification request | direct SES/SMS/push code |
| SH-043 `resolveNotificationRecipients` | shared contract / separate policy — context owner + Notification | derive participant recipients | notification request composition | Order/dispute recipient group semantics | User IDs/recipient facts | delivery/channel logic |
| SH-087 `issueSignedMediaUrl` | another Module public interface — Media / File Access | private evidence retrieval | authorized evidence access | contextual entitlement/purpose | short-lived access result | R2/S3 presigner |
| SH-091 `requestSearchProjectionRefresh` | another Module public interface — Search | reputation refresh through Professional Eligibility's resulting projection | after the Review result is consumed and Profile projection updated | source version and public-safe facts | queued refresh | Typesense client / SearchUpsertEvent insert |
| SH-115 `buildAggregateProjection` | shared mechanism / separate policy — projection owner | rebuild rating/count projection | Review state changes/backfill | which Review statuses count and exact math | projection snapshot | duplicate rating calculator in Search/Profile |
| SH-096 `enumerateSubjectData` | privacy protocol — each data owner | identify subject Review/Dispute data | privacy job inventory | Module-owned data inventory | target descriptors | local privacy-request system |
| SH-095 `executePrivacyInstruction` | privacy protocol — data owner executes | apply erase/anonymize/retain/export instruction | Privacy-owned job | field-specific behavior | execution receipt | local DataErasureJob |
| SH-097 `evaluateRetentionRequirement` | owner facts + Privacy exemption | prevent unlawful/unsafe destructive erase | before destructive privacy action | dispute/review retention facts | retain/erase decision + proof | hardcoded retention guess |
| SH-032 `createRequestContext` | platform primitive — Observability | correlation across sync/async work | request/worker entry | safe domain correlation only | request/correlation IDs | local request-ID helper |
| SH-033 `writeStructuredLog` | canonical shared capability — Observability/Ops | operational diagnostics | command/query/worker boundaries | safe dimensions | structured log | separate module logger |
| SH-034 `sanitizeTelemetryMetadata` | canonical shared capability — Observability/Audit policy | redact sensitive evidence/comments | before audit/log/exception | sensitivity tags/context | sanitized metadata | ad hoc redaction |
| SH-037 `recordIntegrationFailure` | canonical shared capability — Observability/Ops | persist dependency/worker failure | failed hold/payment/search/media/notification coordination | retryability and domain correlation | IntegrationFailure | local provider-failure table |

---

## 16. Module-Internal Operations

These operations contain Review / Dispute domain meaning and should remain local even when they reuse shared plumbing.

| Local operation | Purpose | Input | Output | Source truth affected | Why local |
| --- | --- | --- | --- | --- | --- |
| `evaluateReviewEligibilityPolicy` | compose Order and actor facts into Review permission | Order owner facts, CustomerProfile, existing Review, rating-policy context | decision + reason | none | Review defines when feedback is valid |
| `validateReviewRating` | enforce approved rating scale | rating | normalized/validated rating or denial | none | rating semantics belong to Review |
| `deriveReviewedProfessional` | bind Review target to Order seller | Order facts | ProfessionalProfile ID | none | prevents arbitrary reputation target |
| `evaluateReviewReputationInclusion` | decide if Review contributes to rating/count | Review status + approved policy | include/exclude | projection input | Review owns meaning of its visibility statuses |
| `computeProfessionalReputationFacts` | derive average/count from included Reviews | Review rows/source IDs | deterministic aggregate | no source mutation; projection output | Review semantics must not be reinterpreted elsewhere |
| `evaluateDisputeEligibilityPolicy` | decide if participant may open conflict case | Order facts, actor, existing dispute, timing/reason policy | decision + reason | none | dispute eligibility is domain policy |
| `evaluateDisputeTransition` | validate Dispute lifecycle change | current state, action, actor, workflow facts | allowed/denied | none | lifecycle semantics belong here |
| `recordDisputeAdjudication` | persist refund/release/dismissal decision | dispute, adjudicator, basis, approved structured proof | adjudication record/state | Dispute-owned truth | financial owners execute but do not decide the case |
| `buildDisputeSettlementWorkflow` | define owner-separated settlement steps | adjudication + correlation | workflow step plan | workflow truth only | Review / Dispute owns semantic sequence |
| `reconcileDisputeClosurePolicy` | determine if closure prerequisites are met | adjudication + normalized Order/Payment/Hold facts | close/not-ready decision | potentially Dispute state | only this Module defines “case closed” once approved |
| `mapModerationOutcomeToReviewAction` | translate moderation result into Review action | moderation reference/outcome | publish/hide/remove/no-op intent | Review status through command | moderation owns its case; Review owns its state |
| `buildReviewDisputePrivacyInventory` | enumerate owner data and retention-sensitive fields | subject | target list | none | only owner knows Review/Dispute field meaning |

---

## 17. Shared Mechanism / Separate Truth Rules

1. **State-machine plumbing may be shared; transition policy cannot.** SH-053 `transitionLifecycleState` can validate mechanics, but only Review / Dispute defines legal ReviewStatus and DisputeStatus transitions.
2. **Idempotency is shared; command identity is local.** `submitOrderReview`, `openOrderDispute`, and adjudication commands define their own semantic keys.
3. **Locks are shared; conflict scope is local.** The platform supplies DB locking/CAS. Review / Dispute defines which commands conflict on an Order, Review, or Dispute.
4. **Outbox/inbox is shared; events remain Module facts.** `ReviewPublished` is not a generic “status changed” truth and cannot be renamed by infrastructure.
5. **Workflow runner is shared; dispute settlement truth is local.** A runner may persist technical steps, but it cannot own adjudication, Order refund state, provider execution, or hold state.
6. **Audit is shared; lifecycle proof remains separate.** `AuditEvent` records significant action evidence; it is not a Dispute history model.
7. **Sensitive-access logging is shared; evidence entitlement remains contextual.** Media/Audit manage mechanics; Review / Dispute supplies case context.
8. **Projection infrastructure is shared; reputation inclusion is local.** Search/Profile consumers must not independently decide which Review statuses count.
9. **Privacy protocol is shared; record meaning is local.** Privacy orchestrates; this Module applies instructions to its own records.
10. **Provider adapter patterns are shared, but this Module owns no provider adapter.** Refund provider verification/dedupe/status translation stays Payment-owned.
11. **Snapshot mechanisms do not justify a generic dispute snapshot.** Add a structured resolution/evidence snapshot only if approved domain proof requires it.

---

## 18. Authentication and Authorization

Every protected operation begins with SH-001 `resolveAuthenticatedActor`. Buyer-side operations then resolve the `CustomerProfile` commercial actor where relevant.

### Relationship facts supplied by this Module or source owners

- Review candidate Order ID;
- whether a Review already exists;
- Review author/customer relationship as confirmed by Transaction / Order + Customer Profile;
- ProfessionalProfile target derived from Order seller;
- Dispute Order ID and current status;
- opener/participant relationship from Order facts;
- whether caller is acting as admin/support/reviewer under an approved action;
- evidence target context when private evidence is requested.

### Authority interpretation

SH-002 `authorizeResourceAction` owns permission interpretation. Review / Dispute supplies the action vocabulary and facts. Example actions may include:

- `review.submit`
- `review.read_private`
- `review.publish`
- `review.hide`
- `review.remove`
- `dispute.open`
- `dispute.read`
- `dispute.begin_review`
- `dispute.view_evidence`
- `dispute.adjudicate`
- `dispute.close`

These names are proposed interface vocabulary, not permission rows that may be invented without Role / Authority alignment.

### Resource ownership

- A buyer Review is anchored to the Order’s authoritative CustomerProfile.
- The reviewed Professional is anchored to the Order seller.
- A dispute participant is derived from Order participant facts, not an arbitrary submitted User ID.
- Admin/support role is not blanket entitlement to private evidence. Evidence access still requires contextual authorization and SH-030 `recordSensitiveAccess`.

### Step-up

SH-014 `requireStepUpForSensitiveAction` is required for refund/release adjudication causing or authorizing financial movement. Other evidence/action-specific assurance rules remain unresolved and must not be guessed.

No Module-local auth middleware, MFA flow, role engine, or RLS bypass helper may be created.

---

## 19. Compliance / Readiness / Entitlement Gates

### 19.1 Review submission

- **Underlying truth owner:** Transaction / Order for Order state/participants; Customer / Buyer Profile for buyer actor.
- **Queries consumed:** Order owner facts + SH-004 `resolveCustomerActor`; authority decision.
- **Gated action:** `submitOrderReview`.
- **Local policy:** Order must satisfy approved review eligibility, normally completed; only buyer may submit; one Review per Order; rating valid; target Professional equals Order seller.
- **Result:** allow/deny with stable reasons.

No subscription entitlement is currently evidenced as a prerequisite to legitimate Review submission.

### 19.2 Review publication

- **Underlying truth owners:** Review / Dispute for Review state; Content Moderation for formal moderation outcomes where invoked.
- **Gated action:** publish/hide/remove.
- **Local policy:** publication/inclusion rules remain Review-owned.
- **Result:** ReviewStatus transition and reputation projection effect.

### 19.3 Dispute opening

- **Underlying truth owners:** Order for participant/transaction facts; Hold owner for existing stop signs if relevant.
- **Gated action:** `openOrderDispute`.
- **Local policy:** commercial conflict eligibility, actor, timing, multiplicity, reason/evidence sufficiency.
- **Result:** Dispute created or denied.

No paid Track entitlement may gate a legitimate dispute unless a future explicit product/legal ruling establishes it.

### 19.4 Payout hold

- **Underlying truth owner:** Admin Review / Compliance Hold.
- **Operation consumed:** SH-012 `requestComplianceHold`.
- **Local trigger policy:** an open qualifying Dispute requests a hold with source evidence.
- **Result:** external hold record/result. Review / Dispute does not store a competing blocked boolean.

### 19.5 Refund/release adjudication

- **Underlying truth owners:** Review / Dispute for adjudication; Order for refund attachment; Payment/Payout/Tax for financial execution; Hold for stop-sign lifecycle.
- **Gated action:** `resolveDisputeWithRefund` / `resolveDisputeWithRelease`.
- **Local policy:** authorized adjudicator, valid case state, one non-conflicting decision, approved basis/evidence.
- **Result:** Module-owned decision followed by owner-separated workflow.

---

## 20. Provider Integrations

This Module owns **no external provider integration**.

The registry historically lists “Stripe refund APIs” as a technology near Review / Dispute. Stronger current Cluster architecture resolves that ambiguity:

```text
Review / Dispute adjudication
→ Transaction / Order receives the refund decision and coordinates SH-108 requestOrderRefund
→ Payment / Payout / Tax provider-neutral refund executor
→ Payment-owned Stripe adapter
→ webhook signature verification
→ Payment-owned provider-event dedupe
→ normalized provider result
→ Transaction / Order refund effect
→ normalized settlement result back to Review / Dispute
```

### Explicit prohibitions

Do not create inside `review-dispute/`:

- Stripe SDK client;
- Stripe refund API wrapper;
- Stripe webhook endpoint;
- webhook signature verifier;
- `ProcessedStripeEvent` equivalent;
- provider status mapper;
- payout ledger/service;
- provider reconciliation worker;
- provider credentials/configuration.

Provider outages are surfaced through owner-neutral results plus Observability / Ops. Provider details must not leak into ReviewStatus/DisputeStatus or public error codes.

## 21. Events and Outbox

Events are facts that occurred in Review / Dispute. They are not disguised commands to another Module.

### 21.1 Event envelope

Use canonical SH-046 `publishDomainEvent` with the platform event envelope:

- event ID;
- event type;
- schema version;
- source Module;
- aggregate type/ID/version where available;
- occurredAt;
- correlation ID;
- causation ID;
- minimized actor/system context;
- privacy classification;
- minimized payload.

Consumers deduplicate with the canonical inbox mechanism.

### 21.2 Review events

| Event | Emission condition | Minimum safe meaning | Likely consumers |
| --- | --- | --- | --- |
| `ReviewSubmitted` | Review create commits | review ID, Order ID, professional target, status, source version; omit comment unless a consumer explicitly requires and is permitted | Notification, Audit/analytics adapters |
| `ReviewPublished` | status becomes published | review ID, ProfessionalProfile ID, rating, source version | reputation projection, Search refresh, Notification, potentially Gamification |
| `ReviewHidden` | published/eligible Review becomes hidden | review ID, ProfessionalProfile ID, source version, safe reason code | reputation projection, Search refresh |
| `ReviewRemoved` | Review becomes removed | review ID, ProfessionalProfile ID, source version, safe reason code | reputation projection, Search refresh, Privacy/Audit where relevant |

Review comments should not be copied into general events unless a narrowly scoped consumer contract explicitly requires them.

### 21.3 Dispute events

| Event | Emission condition | Minimum safe meaning | Likely consumers |
| --- | --- | --- | --- |
| `DisputeOpened` | Dispute create commits | dispute ID, Order ID, source actor reference, status, correlation | Hold/Order workflow, Notification, Audit |
| `DisputeReviewStarted` | case enters active review | dispute ID, Order ID, status, safe reviewer reference if allowed | Notification, Audit |
| `DisputeRefundResolved` | adjudication decision favoring refund commits | dispute ID, Order ID, decision reference/correlation, approved amount if contract permits | settlement workflow, Notification |
| `DisputeReleaseResolved` | adjudication decision favoring release/no refund commits | dispute ID, Order ID, decision reference/correlation | settlement workflow, Notification |
| `DisputeDismissed` | dismissal commits | dispute ID, Order ID, safe reason code | Hold/Order coordination, Notification |
| `DisputeClosed` | approved closure transition commits | dispute ID, Order ID, final adjudication category and correlation | Order/Payment support, Notification, Audit |

### 21.4 Transactional outbox rule

If an external effect must reliably follow a committed Review/Dispute mutation, the owner transaction should persist the source change and outbox record together. Network delivery must not be the only evidence that the effect was requested.

Examples:

- Review publish commits even if Search is temporarily unavailable; outbox/worker retries refresh.
- Dispute open commits even if Compliance Hold is temporarily unavailable; durable workflow retries the request.
- Adjudication commits before provider execution; workflow state records pending downstream coordination without pretending financial success.

---

## 22. Background Jobs / Scheduled Work

This Module has no confirmed cron-style business lifecycle that should be invented. It does have likely asynchronous work owned semantically by Review / Dispute.

### 22.1 Reputation projection rebuild worker

- **Purpose:** rebuild Professional rating/count from authoritative Review inclusion policy.
- **Input:** ProfessionalProfile ID, triggering Review/event/source version.
- **Owner:** Review / Dispute owns inclusion/calculation; Professional Eligibility consumes the result and writes its own derived ProfessionalProfile rating/count fields.
- **Idempotency key:** projection target + source version/rebuild generation.
- **Retryable failures:** target projection service unavailable, Search refresh unavailable, queue/transient DB failure.
- **Permanent failures:** malformed source identity, deleted/invalid target requiring manual architecture/data repair.
- **Dead-letter behavior:** visible operational failure; source Review remains authoritative.
- **Business truth updated:** no Review truth changes; only approved projection state.
- **Telemetry:** aggregate IDs, source version, counts/timing; never review comments.

### 22.2 Dispute settlement coordination worker/workflow

- **Purpose:** execute owner-separated steps after dispute open/adjudication: hold, Order dispute/refund effect, Payment refund/release, hold release, closure reevaluation.
- **Input:** dispute ID, adjudication/workflow reference, correlation ID.
- **Owner:** Review / Dispute owns semantic workflow; shared workflow runner owns mechanics.
- **Idempotency key:** dispute + workflow/decision version + step.
- **Retryable failures:** dependency timeout, provider-owner temporary error, hold service unavailable, notification failure.
- **Permanent failures:** owner returns permanent policy denial, contradictory normalized settlement result, missing required correlation/evidence.
- **Dead-letter/manual review:** mark technical workflow failed/stuck in workflow/ops truth and surface to operator; do not fabricate Dispute, RefundStatus, payment, or hold success.
- **Business truth updated:** Review / Dispute-owned workflow/adjudication/closure state only; participant owners update their own records.
- **Telemetry:** request/correlation IDs, step name, retry count, safe owner result code.

### 22.3 No invented schedulers

Do not add automatic dispute deadlines, review publication timers, reopen windows, or purge schedules until those domain policies are approved.

All jobs use canonical SH-047 `enqueueReliableJob`, SH-048 `executeRetryWithBackoff`, request context, queue telemetry, and dead-letter handling.

---

## 23. Concurrency and Idempotency

### 23.1 Critical races

1. two Review submission requests for one Order;
2. Review publish/hide/remove racing;
3. two dispute-open requests for one Order;
4. two admins beginning/adjudicating the same Dispute;
5. refund and release decisions racing;
6. repeated settlement events;
7. hold/release workflow retries;
8. reputation projection events arriving out of order.

### 23.2 Database-enforced constraints

Current schema already provides:

- `Review.orderId @unique`;
- `Dispute.orderId @unique`.

These constraints are authoritative concurrency backstops under the current one-row-per-Order design. Application commands must translate unique violations into stable replay/conflict results rather than expose Prisma errors.

### 23.3 Semantic lock keys

Where a shared aggregate lock is required, preferred semantic keys are:

```text
review:order:{orderId}
review:{reviewId}
dispute:order:{orderId}
dispute:{disputeId}
```

The shared persistence layer decides how those keys map to Postgres row/advisory/serializable locking.

### 23.4 Optimistic concurrency

Current Review/Dispute models lack a version field and Dispute lacks `updatedAt`. If production transitions require optimistic concurrency, add an approved version/CAS field through architecture/schema ruling. Do not simulate distributed correctness with process memory.

### 23.5 Idempotency semantics

- `submitOrderReview`: same idempotency key/fingerprint replays the original Review; a different request after Review exists conflicts.
- `openOrderDispute`: same semantic request replays existing Dispute/workflow; a conflicting second case follows the approved multiplicity rule.
- `resolveDisputeWithRefund` / `resolveDisputeWithRelease`: same decision command replays; opposite decision after one is committed conflicts.
- external result handlers: deduplicate by canonical domain-event/inbox ID plus handler/version.
- hold/payment steps: owner command idempotency keys derive from dispute/workflow/step, not random retry UUIDs.

### 23.6 Transaction boundaries

Within a Module-owned transaction, persist together when applicable:

```text
validate current owner state
→ claim idempotency / concurrency
→ mutate Review or Dispute
→ append Module lifecycle proof if approved
→ write transactional outbox
→ commit
```

External Module/provider network calls should not be required to hold the database transaction open.

---

## 24. Media / Storage

Review / Dispute owns **business evidence context**, not file mechanics.

### Current evidence

- Order files and Message/Media records may be relevant to disputes.
- No dedicated `DisputeEvidence` schema is confirmed.
- Media / File Access owns `MediaAsset`, upload policies, validation, scanning, processing, object keys, storage, `MediaAccessGrant`, and signed URLs.
- Current Messaging `ThreadContextType` has no dedicated `dispute` context; using an Order/support thread versus introducing a dispute context remains unresolved.

### Rules

1. A dispute may reference only owner-approved stable evidence targets.
2. Do not copy file bytes or storage keys into Dispute.
3. Do not build a `dispute-uploads` pipeline.
4. All newly uploaded evidence, if later approved, must use Media upload policy/context.
5. Private evidence access requires:
   - actor/context authorization;
   - Media access operation;
   - short-lived signed access;
   - SH-030 `recordSensitiveAccess` when sensitivity/policy requires.
6. Media failure does not change Dispute truth.
7. Deleting a dispute evidence association does not automatically delete the underlying MediaAsset.
8. Retention/exemption policy controls destructive deletion.

---

**Approved reputation handoff (CL-04-R005):** Review / Dispute owns Review inclusion and aggregate calculation. It supplies its owner-issued reputation result/facts for a ProfessionalProfile through the explicit Module contract: target ProfessionalProfile ID, derived ratingAverage/ratingCount, and source/projection version evidence. Professional Eligibility consumes that result, owns writes to its `ProfessionalProfile.ratingAverage`/`ratingCount`, and supplies the resulting Professional projection to Search. Review / Dispute must not mutate the ProfessionalProfile repository. SH-115 supplies shared projection/version/replay mechanics, not Review policy or Profile ownership. Dependency failure leaves Review truth committed and projection work retryable; exact transport/API naming is not newly selected here.

**Shared access mapping (CL-04-R017):** SH-026 `authorizeContextualResourceAccess` (Confirmed) supplies the context-owner boundary for private dispute evidence; Media owns signed transport. Where domain-specific access proof is applicable, SH-125 `recordDomainAccessEvent` (Confirmed) supplements rather than replaces generic AccessAuditLog.

## 25. Search / Projection

Review / Dispute owns no Typesense/search record.

### Review reputation

Source chain:

```text
Review source truth
→ Review-owned inclusion policy
→ deterministic rating/count projection
→ Professional Eligibility consumes the result and persists its derived ProfessionalProfile rating fields
→ Search / Public Visibility refresh
→ public search projection
```

Only `published` Reviews should contribute under the current inferred policy; the final publication/inclusion policy must be approved before production. Hidden/removed Reviews must not continue contributing once the projection is rebuilt.

### Disputes

Disputes, reasons, admin notes, evidence, financial settlement details, and private case data are not public search documents.

### Search rules

- use SH-091 `requestSearchProjectionRefresh`;
- never insert `SearchUpsertEvent` directly from this Module unless Search’s public implementation contract explicitly encapsulates it;
- never instantiate a Typesense client here;
- Search must consume source-safe reputation facts and cannot reconstruct review visibility, verification, or dispute policy from raw tables;
- review rating may affect public presentation/ranking but cannot create verification/trust truth.

---

## 26. Notification

Review / Dispute owns notification **triggers and business meaning**. Notification owns persistence, template rendering, channel routing, provider delivery, retries, callbacks, token cleanup, and delivery truth.

### Likely triggers

- Review submitted, published, hidden, removed where product policy requires;
- Dispute opened;
- Dispute entered review;
- additional evidence requested if such workflow is later approved;
- refund/release decision recorded;
- settlement completed or failed requiring participant action;
- dispute closed.

### Payload rules

- use IDs, safe status labels, safe reason codes, action routes;
- do not place review/dispute evidence, private messages, payment details, raw admin notes, or sensitive attachment names in push/SMS/email variables unless an explicitly approved template and sensitivity policy permits them;
- provider delivery failure never rolls back Review/Dispute truth;
- use SH-041 `requestNotification` after authoritative state commit/outbox event.

---

## 27. Audit and Sensitive Access

Three different records must remain distinct:

### 27.1 Module domain truth/history

Review and Dispute state—and any approved ReviewEvent/DisputeEvent or structured adjudication/evidence record—answer what happened in the domain.

### 27.2 Generic `AuditEvent`

Use SH-029 `appendAuditEvent` for significant actions such as:

- admin publishes/hides/removes Review;
- dispute opened where audit policy requires;
- admin begins/assigns case;
- adjudication recorded;
- dispute dismissed/closed;
- manual retry/reconciliation action.

AuditEvent is supplemental proof. It cannot be the only source of a Dispute decision.

### 27.3 `AccessAuditLog`

Use SH-030 `recordSensitiveAccess` for protected evidence issue/view/download/denial and other sensitive access required by policy.

### Payload minimization

Do not place raw Review comments, full dispute reasons, admin notes, file URLs, signed tokens, payment provider payloads, or private message bodies into generic audit metadata. Store references and safe codes.

---

## 28. Privacy and Retention

Privacy / Data Erasure owns PrivacyRequest/DataErasureJob/targets/exemptions. Review / Dispute participates as a data owner.

### 28.1 Subject data inventory

Potential personal data includes:

- Review author identifiers;
- Review professional target;
- Review rating/comment;
- Dispute opener identifier;
- Dispute reason/narrative;
- admin notes;
- evidence references and access history;
- actor/reviewer/adjudicator references in any approved event/resolution history;
- timestamps/correlation data.

### 28.2 Required owner contracts

`enumerateReviewDisputeSubjectData` should identify records by data subject and context.

`executeReviewDisputePrivacyInstruction` should support only approved instructions such as:

- anonymize actor metadata;
- erase removable comment/narrative;
- retain record with exemption;
- remove public Review visibility;
- contribute export data;
- detach/delete evidence association where permitted.

### 28.3 Retention concerns

Supplied architecture explicitly recognizes that financial/dispute/fraud/legal records may require retention. Exact durations and fields are not supplied.

Current `Review` and `Dispute` relations cascade when Order is deleted. This may conflict with retention requirements and must be reviewed before destructive production migrations/erasure.

### 28.4 Rules

- product `removed` status is not privacy erasure;
- Privacy orchestration may anonymize rather than hard delete when retention applies;
- do not erase audit proof required to prove an action occurred;
- do not destroy underlying Media objects unless Privacy/Media ownership rules authorize it;
- do not invent retention durations.

---

## 29. Observability

Operational visibility supplements but never replaces Review/Dispute truth.

### Structured logging

Log:

- operation name;
- Review/Dispute/Order IDs as allowed;
- request/correlation/causation IDs;
- result category/reason code;
- transition from/to values;
- dependency name/operation;
- retry/attempt count for workers;
- latency.

Do not log:

- raw dispute reason/admin notes by default;
- Review comment;
- signed URLs/tokens;
- provider payloads;
- private message bodies;
- sensitive file names/paths;
- payment details beyond safe correlation references.

### Integration failures

Use SH-037 `recordIntegrationFailure` for failures coordinating with:

- Compliance Hold;
- Payment/Payout/Tax;
- Transaction / Order;
- Media;
- Search;
- Notification;
- Moderation.

The relevant Review/Dispute workflow must also remain truthful about its own pending/stuck state where business semantics require it.

### Metrics

Useful low-cardinality metrics may include:

- review submission allowed/denied counts by safe reason;
- review projection lag/failures;
- dispute open count;
- dispute queue age;
- adjudication-to-settlement duration;
- workflow retry/dead-letter count;
- hold/refund/release coordination failures.

Do not emit User IDs or free text as metric dimensions.

---

## 30. Security Boundaries

1. Validate all command DTOs with project-standard schema validation before domain logic.
2. Treat User ID, CustomerProfile ID, ProfessionalProfile ID, Order ID, Review ID, Dispute ID, Media ID, and correlation IDs as untrusted input until resolved.
3. Derive buyer/seller relationship from authoritative owner facts; do not accept it from client payload.
4. Enforce authorization server-side.
5. Apply rate limiting through shared platform mechanisms where abuse risk warrants it; do not create a Module-specific rate limiter.
6. Minimize Review/dispute free text in logs/events/analytics.
7. Private evidence uses Media-owned signed access; never expose permanent object URLs.
8. No payment-provider credentials, webhook secrets, or SDK clients belong here.
9. No custom crypto is required. If hashing/token work is later approved, consume the canonical security package.
10. Admin/support access is contextual, not blanket.
11. Refund/release adjudication causing or authorizing financial movement requires SH-014 step-up.
12. Public reputation output must never include private dispute facts.

---

## 31. Error / Decision Result Pattern

Public interfaces should return stable application-level categories.

### Error categories

```text
validation_error
unauthenticated
forbidden
not_found
conflict
stale_state
precondition_failed
dependency_denied
dependency_unavailable
retryable_failure
manual_review_required
retention_blocked
feature_unavailable_pending_ruling
internal_error
```

### Decision shape

Use owner-specific decision results; SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) is proposed future normalization only:

```text
decision: allow | deny | warning | review
reasonCodes: stable Module-owned codes
evidenceRefs: safe opaque references
warnings: safe user/operator guidance
evaluatedAt
policyVersion
expiresAt? when the decision can become stale
nextAction? safe remediation/action hint
```

### Rules

- provider errors are translated by provider-owning Modules before reaching this Module;
- Prisma constraint errors become domain conflict/replay categories;
- authorization denials do not reveal whether private evidence exists;
- unresolved architecture produces an explicit `feature_unavailable_pending_ruling` or implementation blocker, not invented policy;
- dependency failure after local commit must be represented as durable workflow/operational failure, not rollback by fabrication.

---

## 32. Testing Architecture

### Domain unit tests

- Review eligibility policy;
- rating validation after scale ruling;
- reviewed Professional derivation;
- reputation inclusion/calculation;
- Dispute eligibility;
- Review transition rules;
- Dispute transition/adjudication/closure rules;
- moderation-to-Review action mapping.

### State-transition tests

Every approved ReviewStatus and DisputeStatus transition must have:

- allowed path test;
- denied path test;
- stale expected-state test;
- terminal/reopen behavior test;
- event/history proof test where applicable.

### Public contract tests

- owner-fact DTO version handling;
- CustomerProfile resolution;
- Order participant/status contract;
- Hold request/release;
- Payment normalized result;
- Order refund/dispute effect;
- Media signed access;
- Search refresh;
- Notification request;
- Privacy executor.

### Database/integration tests

- unique one-Review-per-Order;
- unique one-Dispute-per-Order under current rule;
- relationship/foreign-key behavior;
- rating DB constraint once approved;
- transaction + outbox atomicity;
- migration/backfill behavior for actor/version/evidence changes.

### Authorization tests

- correct buyer Review submission;
- wrong buyer denied;
- Professional cannot submit buyer Review unless explicitly acting as same buyer CustomerProfile under approved multi-profile rules;
- participant/nonparticipant dispute access;
- admin/support permitted/denied actions;
- sensitive evidence access separate from general admin role.

### Compliance tests

- dispute creates/requests Hold through owner, not local flag;
- Review never creates TrustBadge/VerificationCheck;
- resolved refund does not equal provider refund execution;
- moderation/legal route does not turn Dispute into ModerationCase;
- removed Review is not automatically legal erasure.

### Idempotency/concurrency tests

- duplicate Review submission;
- concurrent Review submission;
- publish/hide/remove race;
- duplicate Dispute open;
- concurrent Dispute open;
- competing refund/release resolution;
- duplicate settlement event;
- retry after partial hold/payment failure;
- out-of-order projection/event handling.

### Provider adapter tests

No provider adapter is owned here. Review / Dispute contract tests must use normalized Payment fixtures and prove raw Stripe statuses/payloads are rejected at this boundary.

### Privacy tests

- subject-data enumeration;
- anonymization/retention instruction;
- exemption blocks destructive action;
- removed/public state changes do not equal erasure;
- evidence deletion delegation;
- retained Dispute remains minimally identifiable where allowed.

### E2E participation tests

At Cluster level:

- completed Order → Review → published reputation update;
- Order → Dispute → hold request → admin review;
- Dispute → refund adjudication → Order SH-108 coordination → Payment execution → Order settlement → Dispute settlement → hold release/closure under approved policy;
- Dispute → release adjudication → owner-separated completion;
- dependency outage/retry path;
- privacy request affecting Review/Dispute.

---

## 33. Module Invariants

**Rules coding agents must never violate**

1. `Review` and `Dispute` are mutated only through Review / Dispute-owned application/domain operations.
2. `ReviewStatus` and `DisputeStatus` transition authority belongs only to this Module.
3. A Review is post-order reputation feedback, not verification, KYC, licensing, readiness, or TrustBadge truth.
4. A Review must be tied to an authoritative Order.
5. New Review authors resolve to the Order's buyer CustomerProfile under CL-04-R007; physical migration/backfill remains gated.
6. The reviewed Professional must be derived from or validated against the Order seller.
7. At most one Review per Order exists under the current schema.
8. Rating must satisfy an explicitly approved scale; coding agents may not invent the scale.
9. Review publication/inclusion policy must be centralized in this Module.
10. Hidden/removed Reviews must not continue contributing to public reputation once projection catches up.
11. `removed` is product state, not legal erasure.
12. A Dispute is an Order-bound commercial conflict, not a Report, ModerationCase, LegalNotice, or support ticket.
13. At most one Dispute row per Order exists under the current schema until multiplicity/reopen policy changes.
14. Coding agents may not infer that one-row uniqueness means “one lifetime dispute” without an approved ruling.
15. An open Dispute may request a ComplianceHold but does not own hold truth.
16. No `isPayoutBlocked`, `holdStatus`, or equivalent local competing stop-sign truth may be added.
17. Dispute adjudication is separate from Order refund attachment.
18. Dispute adjudication is separate from Payment/Payout/Tax provider execution.
19. `resolved_refund` must never be treated as raw Stripe refund success.
20. `resolved_release` must never be treated as payout transfer success or hold release.
21. Review / Dispute never writes `RefundStatus` directly.
22. Review / Dispute never creates/updates `PayoutTransfer` or financial ledger records.
23. Review / Dispute never verifies/deduplicates Stripe webhooks.
24. Provider-native statuses/payloads never become Review/Dispute domain DTOs.
25. Content/legal concerns route to Content Moderation & Legal Notice; Dispute does not absorb that lifecycle.
26. Formal moderation actions may cause a Review-owned visibility transition but do not write Review tables directly.
27. Media / File Access owns upload, scan, storage, signed URLs, and MediaAccessGrant.
28. No dispute-specific shadow file pipeline may be built.
29. Private evidence access is separately authorized and audited when required.
30. Notification owns delivery mechanics; this Module owns only trigger/meaning.
31. Search owns public projection mechanics; this Module never writes Typesense directly.
32. Search/reputation consumers must not independently reinterpret Review inclusion rules.
33. AuditEvent/AccessAuditLog never replace Review/Dispute lifecycle proof.
34. Privacy / Data Erasure owns privacy-request orchestration; this Module only enumerates/executes owner instructions.
35. Retention durations may not be invented.
36. Commercially consequential retryable commands use canonical idempotency.
37. Distributed concurrency uses database/platform primitives, never an in-memory mutex.
38. Cross-Module facts are obtained through approved public contracts by default, not unrestricted foreign repositories.
39. Domain events publish only after authoritative writes commit through the approved outbox path.
40. Review/dispute free text and evidence are minimized in events, logs, metrics, analytics, audit metadata, and notifications.
41. Operational failure does not become business success or business status.
42. An unresolved architecture decision is a blocker, not permission to invent a local rule.

---

## 34. Prohibited Duplicate Implementations

Coding agents must not create these responsibilities inside `review-dispute/`, regardless of convenient filenames.

| Prohibited implementation | Why | Use instead |
| --- | --- | --- |
| `review-auth.ts`, `dispute-auth.ts`, `getCurrentUser.ts` | duplicates authentication | SH-001 `resolveAuthenticatedActor` |
| `review-permissions.ts`, `dispute-rbac.ts`, generic `canAdmin*` | duplicates authority | SH-002 `authorizeResourceAction` |
| `customerResolver.ts`, User-only buyer helper | duplicates buyer actor truth | SH-004 `resolveCustomerActor` |
| `orderRepository.ts` reading/writing Transaction / Order internals | crosses owner boundary | Order public fact/command interfaces |
| `isPayoutBlocked`, `disputeHoldService` owning hold rows | duplicates ComplianceHold | Hold owner operations |
| `stripeRefundService.ts`, `stripeClient.ts`, `disputeWebhook.ts` | duplicates Payment provider adapter | Transaction / Order SH-108 coordinates Payment refund execution |
| `ProcessedDisputeStripeEvent` | duplicates provider-event dedupe | Payment-owned provider dedupe |
| `refundStatusMapper.ts` for Stripe | provider mapping not owned here | Payment adapter translation |
| `payoutService.ts`, `wallet.ts`, `escrow.ts` | wrong financial ownership | Payment/Payout/Tax |
| `disputeUploader.ts`, `evidenceSignedUrl.ts`, direct R2/S3 client | duplicates Media mechanics | Media / File Access |
| `reviewIndexer.ts`, `typesenseRatingService.ts` | duplicates Search | Search refresh interface |
| `reviewEmailService.ts`, `disputeSms.ts`, provider push client | duplicates Notification delivery | SH-041 `requestNotification` |
| `reviewAuditTable`, `disputeAuditLogger` as generic ledger | duplicates Audit/Event Ledger | SH-029 `appendAuditEvent` |
| `disputeFileViewLog` replacing AccessAuditLog | duplicate sensitive access proof | SH-030 `recordSensitiveAccess` |
| `reviewPrivacyJob.ts`, `disputeErasureOrchestrator.ts` | duplicates Privacy workflow | privacy executor protocol |
| `reviewEventBus.ts`, `disputeQueue.ts`, custom retry loop | duplicates event/queue primitives | outbox, queue, retry primitives |
| `reviewMutex.ts`, `disputeLockTable` | unsafe/duplicate concurrency | shared Postgres lock/CAS primitive |
| universal `stateMachine.ts` encoding Review/Dispute semantics globally | transfers lifecycle policy | shared transition plumbing + local policy |
| `reviewVerificationService.ts` | corrupts reputation/verification boundary | Trust Verification + Review facts separately |
| `disputeModerationCase.ts` as shadow moderation system | duplicates moderation/legal truth | Content Moderation public interface |
| `disputeThread` lifecycle copy | duplicates Messaging | Messaging context contract once approved |
| hardcoded dispute/review retention duration | unsupported legal policy | Privacy retention decision/exemption |

---

**Confirmed actor semantics (CL-04-R007):** CustomerProfile is required semantic buyer identity for new CL-04 buyer-domain records; User remains authenticated account/audit identity. After CustomerProfile migration, Gig/GigAssignment/Order buyer ownership must not be authorized from User ID alone. A Review author resolves to the Order's buyer CustomerProfile. Dispute opener proof must distinguish customer, professional, and privileged/admin initiation with an unambiguous typed domain actor; this representation requirement does not approve which actors may open a Dispute. Historical backfill, permanent legacy-User reference semantics, and the physical typed-opener schema remain unresolved.

**Mandatory durable Dispute proof (CL-04-R010):** persist the authorized adjudicator, decision, basis/reason, decision timestamp, refund amount/basis where applicable, idempotency/correlation identity, hold request/release correlation, settlement/refund correlation, and whether required downstream steps are pending or completed. This domain proof must survive retries/outages. Generic AuditEvent, QueueJob, or mutable `adminNotes` cannot substitute for it. The final decision/event/workflow persistence design remains unresolved and must be approved before production adjudication.

**Binding retention boundary (CL-04-R011):** hard deletion of an Order must not cascade-delete retained transaction, Agreement, Review, Dispute, or domain-history evidence without owner-specific Privacy/retention evaluation. Privacy issues the instruction; each owner enumerates its targets, evaluates retention/exemption facts, erases/anonymizes eligible data, preserves/minimizes retained evidence, and returns proof to Privacy. Database cascades must not provide an alternate destructive path. Existing cascade behavior requires a later approved database correction; legal retention durations remain unresolved.

**Confirmed sensitive-action gate (CL-04-R021):** refund/release adjudication or actions that cause or authorize financial movement require SH-014 `requireStepUpForSensitiveAction`, owned by Identity & Access. This gate does not approve finality, grant TTL/reuse/renewal, manual-signature procedure, non-payout hold effects, signer anonymization, or retention periods. Optional external e-sign adoption must not block the provider-neutral Agreement domain.

## 35. Unresolved Decisions

These questions are intentionally non-authoritative. Implementation must stop at the affected boundary until an approved ruling exists.

| Decision | Evidence today | Blocks |
| --- | --- | --- |
| What rating scale is valid? | `rating Int`; no canonical range | production Review write/DB constraint |
| What exact actor schema identifies Review author? | CustomerProfile is buyer truth; current `reviewerUserId?` is optional/non-relational | production Review migration/write |
| Is Review auto-published or moderated from `pending`? | schema default `pending`; no policy | publication automation/default |
| Can a Review be edited/revised? | no revision/history policy | edit feature |
| Can hidden/removed Reviews be republished/restored? | no transition rule | reverse transitions |
| Reputation result handoff | CL-04-R005 confirms Review calculation and Professional Eligibility persistence. | consumer contract/implementation readiness; ownership is settled |
| Who may open a Dispute: buyer, seller, both, admin/system? | `openedById?` ambiguous; Order participant concept | production dispute authorization/schema |
| What is the dispute opening time/window and eligible Order status set? | not supplied | eligibility policy |
| Is there one lifetime Dispute, one active Dispute, or reopenable case? | `orderId @unique`; semantics absent | reopen/multiplicity |
| What structured evidence-reference schema exists? | no dedicated DisputeEvidence confirmed | rich evidence intake |
| Does `adminNotes` remain, or is an append-only note/history model required? | mutable blob only | admin case history |
| What physical persistence implements the approved durable adjudication proof? | CL-04-R010 fixes the minimum decision/correlation/recovery facts; status + resolvedAt is insufficient. | production persistence design/migration |
| What exactly distinguishes `resolved_refund`/`resolved_release`/`dismissed` from `closed`? | enum exists; finality semantics absent | close automation |
| How is a requested ComplianceHold correlated back to a Dispute? | no explicit dispute source relation confirmed | robust hold reconciliation |
| How is refund/release execution correlated to adjudication? | no Review/Dispute correlation field confirmed | robust settlement workflow |
| Other sensitive-action rules | Financial refund/release movement requires SH-014 under CL-04-R021. | remaining action-specific policy only |
| What Messaging context is used for dispute communication? | ThreadContextType lacks dispute; Order/support possible | dedicated case messaging |
| What records/fields require retention exemptions and for how long? | retention risk confirmed; duration absent | destructive erasure/purge |
| What optimistic concurrency/version field should Review/Dispute use? | current models lack version; Dispute lacks updatedAt | CAS implementation |
| Should a Review/Dispute-specific event ledger schema be introduced? | domain history need evidenced; no schema confirmed | durable fine-grained history |
| Does a dedicated dispute workflow run/step record exist? | shared workflow runner approved; local persistence shape unresolved | durable multi-step orchestration implementation |

---

## 36. Architecture Decision Summary

### Binding confirmed rulings

1. `review_dispute` is the source owner for `Review`, `ReviewStatus`, `Dispute`, and `DisputeStatus`.
2. The Module belongs primarily to CL-04 and is subordinate to root and CL-04 architecture.
3. Review is post-order reputation feedback.
4. Dispute is Order-bound commercial conflict/adjudication truth.
5. Order and RefundStatus remain Transaction / Order truth.
6. Payment / Payout / Tax owns provider refund/payout execution and Stripe webhook/dedupe truth.
7. Admin Review / Compliance Hold owns reusable stop-sign truth.
8. CustomerProfile is buyer actor truth; User remains authentication/audit identity.
9. Content Moderation & Legal Notice owns moderation/legal case truth.
10. Media / File Access owns file safety/storage/signed access.
11. Search / Public Visibility owns SearchUpsertEvent, Typesense, and public projection execution.
12. Notification owns channel delivery.
13. Audit / Event Ledger owns generic audit and sensitive-access records.
14. Privacy / Data Erasure owns privacy-rights orchestration.
15. Canonical idempotency, concurrency, outbox/inbox, queue, workflow, observability, and shared-operation mechanisms must be reused.
16. Review publication status may influence reputation; it must never become verification truth.
17. Dispute adjudication must remain distinguishable from refund attachment, provider financial execution, and hold lifecycle.

### Confirmed reconciliation rulings

- **Confirmed CL-04-R007:** new Review authors resolve to the Order buyer CustomerProfile and the Professional target is derived/validated from Order.

**Confirmed SH-046:** cross-Module facts use canonical transactional publication. **Confirmed CL-04-R005:** Review / Dispute calculates reputation; Professional Eligibility persists its derived Profile fields and supplies the Professional projection to Search.

### Proposed rulings carried forward

1. Production Review/Dispute schemas should be strengthened for actor integrity, concurrency, and structured proof before their affected features ship.
2. Dispute settlement should be a Review / Dispute-owned semantic workflow over shared runner mechanics.

### Non-rulings

All questions in Section 35 remain unresolved until explicitly accepted through architecture governance.

---

## 37. Coding-Agent Usage

Before implementing or changing this Module, an agent must read:

1. root `project-overview.md`;
2. root `architecture.md`;
3. root `code-standards.md`;
4. Canonical Shared Operations Registry;
5. CL-04 `architecture.md`;
6. CL-04 `build-plan.md`;
7. this `review_dispute/module-architecture.md`;
8. this `review_dispute/implementation-plan.md`;
9. public-interface sections for Transaction / Order, Customer / Buyer Profile, Role / Authority, Payment / Payout / Tax, Admin Review / Compliance Hold, Media / File Access, Search / Public Visibility, Notification, Audit / Event Ledger, Privacy / Data Erasure, Content Moderation & Legal Notice, and Observability / Ops as touched;
10. `progress-tracker.md`;
11. relevant provider/library documentation only for owner contracts the feature interacts with.

Before coding a feature, confirm that every Section 35 decision it depends on is resolved. If not, report the architecture blocker and implement only unaffected work.

The implementation agent must not use repository convenience, a direct Prisma relation, or a provider SDK as justification to bypass the ownership and public-interface boundaries defined here.
