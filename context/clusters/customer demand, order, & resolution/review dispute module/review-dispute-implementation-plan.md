# Review / Dispute Implementation Plan

> **Module ID:** `review_dispute`  
> **Module name:** Review / Dispute  
> **Primary Cluster:** CL-04 — Customer Demand, Order & Resolution  
> **Module type:** `domain_compliance_support`  
> **Build status:** `mvp_active`  
> **Plan status:** Implementation-grade Module plan; subordinate to root architecture and CL-04 `build-plan.md`  
> **Source-of-truth scope:** `Review`, `ReviewStatus`, `Dispute`, `DisputeStatus`

**Shared Operation status (CL-04-R015/R016):** exact SH IDs/names resolve to the canonical registry. SH-046 publication/outbox is Confirmed. SH-003 `queryOwnerFacts` and SH-015 `returnDecisionResult` remain Proposed ruling: use owner-specific fact/decision DTOs, not binding APIs dependent on those proposals. SH-054, SH-073, and SH-111, wherever referenced, remain Proposed ruling and conditional on separate approval. All other referenced registered operations retain their registry status and owner.

---

## Core Principle

Implement Review / Dispute through narrow, verifiable slices:

```text
public/observable behavior
→ validated command/query
→ Review / Dispute-owned policy
→ authoritative Review / Dispute write/read
→ canonical shared-operation calls
→ event/audit/notification/workflow effects
→ tests
→ exit gate
```

This Module must never become the financial, hold, moderation, media, search, notification, privacy, or generic admin implementation for the workflows it coordinates.

At all times keep these truths distinguishable:

```text
Dispute adjudication truth               → Review / Dispute
Order refund/dispute attachment truth    → Transaction / Order
Provider refund/payout execution truth   → Payment / Payout / Tax
Reusable stop-sign truth                 → Admin Review / Compliance Hold
```

The plan is narrower than CL-04's Cluster plan. It implements the Review / Dispute portion of CL-04 Features **10–12**, then proves/hardens its boundaries as part of CL-04 Features **13–14**. It does not independently reorder the Cluster.

---

## Build Rules

1. Follow root architecture, root code standards, CL-04 architecture, and CL-04 build sequencing.
2. This Module owns only Review/Dispute truth declared in `module-architecture.md`.
3. Consume neighboring truth only through approved public contracts or normalized internal events.
4. Reuse canonical shared operations; never create local authentication, authority, hold, audit, queue, outbox, concurrency, search, media, notification, or privacy infrastructure.
5. Every mutation validates input, authenticated actor, authority, current owner state, and relevant contextual gates.
6. Buyer commercial identity resolves through `CustomerProfile`; User remains authentication/audit identity.
7. Review target Professional must be derived from or validated against authoritative Order seller facts.
8. Commercially consequential retryable commands use SH-044 `executeIdempotentCommand`.
9. Lifecycle changes use database-safe concurrency and owner-local transition policy.
10. Cross-Module effects use committed state + transactional outbox/durable workflow; do not depend on one best-effort network call.
11. Dispute opening/adjudication may commit before downstream hold/payment/search/notification work completes; pending coordination is explicit and retryable.
12. Provider-specific details never enter Review / Dispute domain APIs.
13. Review publication may affect reputation; Review never writes verification or TrustBadge truth.
14. Private evidence uses Media-owned access and generic sensitive-access audit.
15. Privacy / Data Erasure owns privacy workflow; Review / Dispute implements only its data-owner contracts.
16. Every feature ends with automated tests and a concrete exit gate.
17. If a feature reaches an unresolved architecture decision, stop at that boundary and document it. Do not infer a product/legal rule from enum names or current schema convenience.
18. No later hardening feature may be used to hide unfinished source-of-truth logic from an earlier feature.

---

## Preconditions

### Hard platform dependencies

The following must exist before the first production mutation that uses them:

- Prisma/Postgres migration workflow;
- TypeScript strict mode and project validation conventions;
- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- canonical command idempotency;
- canonical database concurrency primitive;
- transactional outbox/domain-event envelope;
- consumer inbox/deduplication;
- shared queue/worker shell with retry/dead-letter;
- structured request/correlation context;
- SH-029 `appendAuditEvent`;
- stable application error/decision result conventions.

If these are not implemented when Review / Dispute work begins, this Module may compile against approved interfaces/test doubles but must not create substitutes.

### Hard domain dependencies before Review production

- CL-04 Feature 09 Order fulfillment/completion truth;
- Transaction / Order public owner-fact query containing review-relevant Order status, CustomerProfile buyer, seller ProfessionalProfile, and version;
- Customer / Buyer Profile SH-004 `resolveCustomerActor`;
- explicit Review rating-scale ruling;
- explicit Review author schema/migration ruling;
- initial Review publication policy;
- approved Professional reputation projection storage/interface.

### Hard domain dependencies before Dispute production

- Transaction / Order owner facts and dispute-effect/refund contracts;
- explicit dispute opener actor model;
- explicit dispute multiplicity/reopen ruling;
- approved dispute eligibility/time-window policy;
- approved minimum evidence-reference policy for MVP;
- Admin Review / Compliance Hold public request/evaluate/release contracts;
- Transaction / Order SH-108 refund-coordination/settlement contract, with Payment-owned verified execution outcomes and approved release results;
- explicit `resolved_*` versus `closed` lifecycle semantics before automatic closure;
- approved structured adjudication/correlation proof shape.

### Interfaces that may initially be stubbed

With contract fixtures, earlier slices may proceed before full neighboring implementations exist:

- Professional reputation projection writer;
- Search projection refresh;
- Notification request;
- Media signed-access interface;
- Content Moderation intake/result;
- Payment refund/release execution;
- Compliance Hold;
- Privacy executor orchestration;
- Observability failure sink.

Stubs must match owner-owned public contracts. They must not become permanent local implementations.

### Cluster sequencing dependency

Review / Dispute Module production work starts only after CL-04 Feature 09 has passed its exit gate. Module Features 01–02 below may prepare contracts/schema decisions earlier, but must not ship behavior that bypasses the Cluster sequence.

---

# Phase 1 — Contracts and Source-of-Truth Foundation

## 01 Review Source-Truth and Public Contract Foundation

### Objective

Prepare Review for production implementation by settling the schema/public-contract prerequisites required by CL-04 Feature 10 without yet implementing Review submission behavior.

### Observable Result

The repository has an approved Review actor/target/rating/concurrency schema shape, Review-owned DTOs and public contract signatures, repository boundary, and migration tests sufficient for Feature 03 to implement behavior without inventing architecture.

### Cluster Build-Plan Link

Supports **CL-04 Feature 10 — Post-Order Review and Reputation Projection**. This Module feature may begin as design/schema preparation, but CL-04 Feature 10 remains the Cluster execution gate.

### Dependencies

- current Prisma `Review`/`ReviewStatus`;
- root schema/migration standards;
- CustomerProfile buyer ruling;
- Transaction / Order public owner-fact contract;
- explicit rating-scale ruling;
- Review author schema ruling;
- initial publication policy;
- canonical concurrency/idempotency contracts.

### In Scope

- finalize Review production schema changes explicitly approved by architecture;
- establish relational actor fields needed to represent CustomerProfile/User audit identity;
- enforce/prepare rating constraint;
- preserve `orderId @unique`;
- decide whether Professional target is stored and constrained or derived-only;
- add approved optimistic version/update fields if required;
- define Review repository interface inside this Module;
- define public DTOs/results for:
  - `evaluateReviewEligibility`;
  - `submitOrderReview`;
  - `getOrderReview`;
  - `listProfessionalReviews`;
  - `publishReview`;
  - `hideReview`;
  - `removeReview`;
  - `getProfessionalReputationFacts`;
- define Review event schemas/version 1 without yet wiring all consumers.

### Out of Scope

- Review form/UI behavior;
- actual Review submission;
- automatic publication;
- review editing/replies;
- Search implementation;
- ProfessionalProfile projection writes;
- moderation-case implementation;
- verification/trust logic.

**Actor prerequisite (CL-04-R007):** enforce CustomerProfile as semantic buyer identity for new records; Review authors resolve from the Order buyer and Dispute opener identity is typed. Historical backfill and final Prisma representation remain separate approval gates. No schema is changed in this reconciliation.

### Module-Owned Data

- `Review`;
- `ReviewStatus`;
- approved Review version/history fields only;
- Review public event schemas.

### Public Interfaces

Contracts only in this feature. No production command may be advertised as complete until its behavior feature passes its exit gate.

### Shared Operations Used

- SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) — source-owner contract pattern; define the minimal Order DTO Review needs; prohibit direct Order repository reads.
- SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) — define stable Review eligibility decision shape; local reason codes remain Review-owned.
- SH-052 `withOptimisticConcurrency` / SH-051 `acquireAggregateLock` — select approved concurrency integration if schema needs a version field; no local lock implementation.
- SH-046 `publishDomainEvent` — define event envelope/schema contract; no custom event bus.
- SH-044 `executeIdempotentCommand` — define submission semantic idempotency inputs; no local dedupe table.

### Domain Logic

Document, but do not yet execute, the binding Review rules:

1. Review references one authoritative Order.
2. One Review per Order under current architecture.
3. buyer actor is CustomerProfile under approved migration.
4. User may remain audit actor but not replace CustomerProfile commercial identity.
5. Professional target equals the Order seller.
6. rating uses the approved scale.
7. initial status follows explicit publication ruling.
8. public reputation inclusion is Review-owned policy.

### Authorization / Compliance

Define action vocabulary and relationship facts for Role / Authority. Do not create permission rows or local RBAC engine here.

### Database / Transaction Behavior

- migration must be backward-safe for greenfield/current fixtures;
- add database constraint for rating after scale approval;
- preserve one-Review-per-Order uniqueness;
- add indexes required by professional/status/pagination queries;
- if actor migration changes nullable legacy fields, provide explicit migration/backfill strategy;
- schema must not create CustomerProfile, ProfessionalProfile, Order, Search, or audit truth.

### Events / Jobs

Define Review event schemas and outbox integration point. No worker required yet.

### Provider Integration

None.

### UI / Admin Surface

None.

### Failure Behavior

- migration cannot proceed if actor/rating/publication ruling remains unresolved;
- incompatible legacy fixture rows are reported by migration verification rather than silently coerced;
- contract version mismatch is a compile/test failure.

### Tests

- Prisma migration/schema tests;
- unique Review per Order;
- rating constraint boundaries;
- actor relationship integrity;
- professional target integrity strategy;
- repository boundary tests;
- DTO serialization/version contract tests;
- architecture lint/check proving no direct Stripe/Typesense/Media implementation.

### Documentation Updates

If the schema ruling settles a Section 35 decision, update:

- `module-architecture.md`;
- CL-04 architecture if the Cluster contract changed;
- dependency public-interface docs if DTO requirements changed;
- progress tracker.

### Acceptance Criteria

- every field needed for production Review submission has approved meaning;
- database can reject invalid rating/duplicate Order Review;
- CustomerProfile/User actor semantics are explicit;
- public contracts do not leak Prisma model types across Module boundaries;
- no neighboring source truth moved into Review.

### Exit Gate

Before Feature 02/03 proceeds:

- schema migration applies/reverts according to project standard;
- schema/contract tests pass;
- all Review decisions blocking production submission are marked resolved in architecture;
- no direct cross-Module repository import is needed by the proposed command.

---

**Mandatory durable Dispute proof (CL-04-R010):** persist the authorized adjudicator, decision, basis/reason, decision timestamp, refund amount/basis where applicable, idempotency/correlation identity, hold request/release correlation, settlement/refund correlation, and whether required downstream steps are pending or completed. This domain proof must survive retries/outages. Generic AuditEvent, QueueJob, or mutable `adminNotes` cannot substitute for it. The final decision/event/workflow persistence design remains unresolved and must be approved before production adjudication.

## 02 Dispute Source-Truth and Workflow Contract Foundation

### Objective

Prepare Dispute for production intake/adjudication by resolving the minimum actor, multiplicity, history/evidence, decision, correlation, and concurrency shape required by CL-04 Features 11–12.

### Observable Result

The repository has an approved Dispute schema/public contract capable of expressing who opened the case, what was decided, how external workflow effects correlate, and how concurrent decisions are rejected—without absorbing Order, Payment, Hold, Media, or Moderation truth.

### Cluster Build-Plan Link

Supports **CL-04 Feature 11 — Dispute Intake and Payout Hold Coordination** and **Feature 12 — Dispute Adjudication, Refund/Release, and Closure**.

### Dependencies

- current `Dispute`/`DisputeStatus`;
- explicit opener actor ruling;
- explicit one-case/reopen/multiplicity ruling;
- approved dispute opening window/eligible Order states;
- approved evidence-reference minimum;
- structured adjudication/history proof ruling;
- `resolved_*` vs `closed` semantics;
- Hold, Payment, and Order public contract shapes;
- canonical workflow/idempotency/concurrency contracts.

### In Scope

- approved migration of `openedById` to explicit actor relations/context;
- preserve/change `orderId @unique` only under approved multiplicity ruling;
- introduce approved structured resolution/history fields or records;
- define stable workflow/correlation identifiers without storing provider-native IDs as business meaning;
- introduce approved version/update fields;
- define minimum evidence-reference schema if approved;
- constrain `adminNotes` role so it cannot be sole adjudication proof;
- define Dispute repository and public DTOs;
- define domain-event schemas for open/review/adjudication/close;
- define semantic workflow step contracts for hold/Order/Payment/closure coordination.

### Out of Scope

- dispute UI;
- opening a real Dispute;
- calling Hold/Payment/Order;
- Stripe/webhooks;
- Media upload mechanics;
- generic admin review platform;
- ModerationCase/LegalNotice;
- automatic closure.

### Module-Owned Data

- `Dispute`;
- `DisputeStatus`;
- approved `DisputeEvent`, resolution, evidence-reference, or workflow records if architecture authorizes them;
- Dispute event schemas.

### Public Interfaces

Contract shapes for:

- `evaluateDisputeEligibility`;
- `openOrderDispute`;
- `getOrderDispute`;
- `listDisputesForActor`;
- `listDisputeReviewQueue`;
- `beginDisputeReview`;
- `recordDisputeEvidenceReference` if approved;
- `resolveDisputeWithRefund`;
- `resolveDisputeWithRelease`;
- `dismissDispute`;
- `applyOrderSettlementResultToDispute`;
- `closeDispute`;
- `getDisputeResolutionStatus`.

### Shared Operations Used

- SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite);
- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency`;
- SH-053 `transitionLifecycleState`;
- SH-031 `appendDomainLifecycleEvent` if a domain ledger is approved;
- SH-046 `publishDomainEvent`;
- SH-049 `orchestrateWorkflowSteps`;
- SH-050 `reconcileWorkflowStatus`.

Local rules define statuses, case identity, decision meaning, workflow steps, and closure.

### Domain Logic

Document the approved distinction:

```text
open/review/adjudication        = Dispute truth
Order disputed/refund state     = Transaction / Order truth
refund/release provider effect  = Payment / Payout / Tax truth
payout stop sign                = ComplianceHold truth
```

The Dispute schema may hold opaque owner references/correlation evidence, but not duplicate their statuses as source truth.

### Authorization / Compliance

Define participant/reviewer/adjudicator action facts. SH-014 is required for refund/release adjudication causing or authorizing financial movement; Identity owns the assurance/session mechanics.

### Database / Transaction Behavior

- enforce approved dispute cardinality;
- enforce one adjudication decision where applicable;
- add concurrency/version constraints if approved;
- structured history/event writes must be append-only where designed;
- keep owner state + local lifecycle event + outbox transactionally consistent;
- no cross-domain foreign records are mutated.

### Events / Jobs

Define workflow/event schemas only. No financial workflow executes yet.

### Provider Integration

None. Payment owner contract uses normalized domain results.

### UI / Admin Surface

None.

### Failure Behavior

- any unresolved actor/multiplicity/finality decision blocks schema commitment;
- existing ambiguous rows must be migrated only by explicit safe rule;
- no fallback to `adminNotes` as universal serialized state.

### Tests

- schema cardinality;
- actor integrity;
- resolution uniqueness;
- lifecycle/history immutability if introduced;
- correlation uniqueness/indexing;
- DTO contract tests;
- transition table tests for approved graph;
- no Payment/Hold/Order ownership migration.

### Documentation Updates

Update Module/Cluster architecture whenever an approved decision changes schema meaning or public workflow.

### Acceptance Criteria

- a coding agent can distinguish adjudication, settlement, and hold state from schema/contracts alone;
- opener and reviewer/adjudicator evidence are unambiguous;
- durable workflow correlation does not depend on raw provider objects;
- current one-Dispute uniqueness is either explicitly ratified or explicitly replaced.

### Exit Gate

- all decisions required for CL-04 Feature 11 production intake are resolved;
- all decisions required for Feature 12 adjudication are either resolved or explicitly defer only later settlement/closure behavior;
- migration/contract/state-transition tests pass;
- no shadow hold/payment/provider schema exists.

---

# Phase 2 — Review Lifecycle and Reputation

## 03 Review Eligibility and Submission

### Objective

Implement the first complete Review behavior: an eligible buyer can submit exactly one valid Review for a reviewable Order.

### Observable Result

The buyer receives a deterministic eligibility decision and can submit one Review. Wrong buyers, non-reviewable Orders, invalid ratings, duplicates, stale facts, and unauthorized callers fail with stable results.

### Cluster Build-Plan Link

Implements the submission half of **CL-04 Feature 10**.

### Dependencies

- Features 01–02 only insofar as shared foundations are complete;
- CL-04 Feature 09 exit gate;
- Transaction / Order owner-fact query;
- SH-004 `resolveCustomerActor`;
- Role / Authority;
- canonical idempotency;
- approved Review schema/rating/publication policy.

### In Scope

- `evaluateReviewEligibility`;
- `submitOrderReview`;
- `getOrderReview`;
- buyer-facing source-truth read DTO;
- Review submission event/outbox;
- audit/notification request where approved.

### Out of Scope

- publish/hide/remove admin behavior beyond the approved initial status;
- reputation aggregate update;
- Search refresh;
- Review edit/reply;
- moderation case;
- dispute behavior.

### Module-Owned Data

- `Review`;
- initial `ReviewStatus`;
- `ReviewSubmitted` event.

### Public Interfaces

- `evaluateReviewEligibility`;
- `submitOrderReview`;
- `getOrderReview`.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor` — resolve User/system actor; prohibit local auth helper.
- SH-004 `resolveCustomerActor` — establish commercial buyer; prohibit User-only buyer inference.
- SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) — fetch minimum Order facts; prohibit direct Order repository.
- SH-002 `authorizeResourceAction` — authorize `review.submit`/read.
- SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite) — eligibility response.
- SH-044 `executeIdempotentCommand` — one semantic Review create.
- SH-046 `publishDomainEvent` — `ReviewSubmitted`.
- SH-029 `appendAuditEvent` — only if audit policy requires submission proof.
- SH-041 `requestNotification` — only approved post-submit intent.

### Domain Logic

Primary workflow:

1. validate request;
2. resolve authenticated actor;
3. resolve CustomerProfile;
4. obtain versioned Order review facts;
5. verify buyer relationship;
6. authorize action;
7. apply Review eligibility policy;
8. validate rating;
9. derive/validate Professional target from Order seller;
10. execute idempotent create transaction;
11. persist Review in approved initial status;
12. write outbox event in same transaction;
13. return Review DTO;
14. downstream notification is post-commit.

A Review is not created merely because an Order ID exists.

### Authorization / Compliance

- only the Order buyer CustomerProfile may submit under current proposed/approved model;
- admin cannot forge a buyer Review through this command;
- Review comments are untrusted user content and validated/sanitized according to project input/display rules;
- no entitlement gate is introduced.

### Database / Transaction Behavior

- `orderId @unique` guarantees one row;
- create and outbox are atomic;
- unique conflict is translated into existing/replay/conflict result;
- no cross-Module write occurs in transaction;
- Order facts include a version/status sufficient to reject stale invalid eligibility if needed.

### Events / Jobs

Emit `ReviewSubmitted` only after source commit via outbox. No worker required.

### Provider Integration

None.

### UI / Admin Surface

Minimal Review submission/read surface only if CL-04 owns such UI in repository. If UI is being built at Cluster slice, bind it to these public contracts; do not invent a parallel client policy.

### Failure Behavior

- unauthenticated → `unauthenticated`;
- wrong buyer → `forbidden`/stable policy denial;
- Order not reviewable → `precondition_failed` + `order_not_reviewable`;
- invalid rating → `validation_error`;
- existing Review → idempotent replay or `conflict`;
- Order contract unavailable → no write, dependency unavailable;
- notification unavailable → Review remains committed; notification retries externally.

### Tests

- domain eligibility unit tests;
- correct/wrong CustomerProfile;
- non-completed/non-reviewable Order;
- rating boundaries;
- one Review per Order;
- duplicate identical retry;
- duplicate conflicting retry;
- Professional target cannot be spoofed;
- source write + outbox atomicity;
- no verification mutation;
- authorization negative tests.

### Documentation Updates

Update public interface docs and progress. Architecture changes only if behavior settles a previously unresolved rule.

### Acceptance Criteria

- Review submission can be explained entirely by Order facts + CustomerProfile + Review policy;
- no client-provided seller identity is trusted;
- duplicate requests cannot create duplicate Review or events;
- Review status equals the approved initial publication policy.

### Exit Gate

- all Review submission tests pass;
- migration/constraint tests pass;
- public contract has stable error/reason codes;
- no direct Order/Profile/Search/provider writes exist.

---

**Approved reputation handoff (CL-04-R005):** Review / Dispute owns Review inclusion and aggregate calculation. It supplies its owner-issued reputation result/facts for a ProfessionalProfile through the explicit Module contract: target ProfessionalProfile ID, derived ratingAverage/ratingCount, and source/projection version evidence. Professional Eligibility consumes that result, owns writes to its `ProfessionalProfile.ratingAverage`/`ratingCount`, and supplies the resulting Professional projection to Search. Review / Dispute must not mutate the ProfessionalProfile repository. SH-115 supplies shared projection/version/replay mechanics, not Review policy or Profile ownership. Dependency failure leaves Review truth committed and projection work retryable; exact transport/API naming is not newly selected here.

## 04 Review Publication, Reputation Projection, and Search Effect

### Objective

Complete Review visibility lifecycle and make public reputation reproducibly follow Review-owned publication state.

### Observable Result

Authorized publication/hide/remove actions change Review truth; rating/count projection is rebuilt deterministically; Search receives refresh requests; projection/search failures do not alter Review source truth.

### Cluster Build-Plan Link

Completes **CL-04 Feature 10 — Post-Order Review and Reputation Projection**.

### Dependencies

- Feature 03;
- approved publication/restore transition policy;
- CL-04-R005 Review-result → Professional Eligibility consumer contract, with the Profile writer available before the reputation integration exit gate;
- Search SH-091 `requestSearchProjectionRefresh`;
- Notification;
- moderation result interface if Review moderation is active.

### In Scope

- `publishReview`;
- `hideReview`;
- `removeReview`;
- `applyReviewModerationDecision`;
- `listProfessionalReviews`;
- `getProfessionalReputationFacts`;
- Review inclusion/calculation policy;
- reputation projection worker;
- Search refresh request;
- Review publication lifecycle events.

### Out of Scope

- Review editing/replies unless separately approved;
- Search index implementation;
- Professional verification/readiness mutation;
- ModerationCase lifecycle;
- privacy erasure beyond keeping `removed` distinct.

### Module-Owned Data

- Review status transitions;
- Review lifecycle proof if approved;
- Review publication events;
- Review-owned reputation calculation policy.

### Public Interfaces

- `publishReview`;
- `hideReview`;
- `removeReview`;
- `applyReviewModerationDecision`;
- `listProfessionalReviews`;
- `getProfessionalReputationFacts`.

### Shared Operations Used

- SH-002 `authorizeResourceAction`;
- SH-053 `transitionLifecycleState`;
- SH-044 `executeIdempotentCommand` for retryable administrative commands;
- SH-052 `withOptimisticConcurrency`/lock as selected;
- SH-046 `publishDomainEvent`;
- SH-029 `appendAuditEvent`;
- SH-115 `buildAggregateProjection`;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-091 `requestSearchProjectionRefresh`;
- SH-041 `requestNotification`;
- SH-045 `deduplicateDomainEvent` for moderation input.

Local policy: which Review statuses count, allowed transition graph, aggregation math.

### Domain Logic

For each committed visibility change:

1. authorize action;
2. validate expected Review state;
3. apply Review-owned transition;
4. append lifecycle proof/outbox;
5. enqueue reputation rebuild for ProfessionalProfile;
6. recompute aggregate only from inclusion-eligible Review source truth;
7. hand the owner-issued aggregate to Professional Eligibility, which writes its own ProfessionalProfile rating fields; then Search consumes the resulting Professional projection;
8. Professional Eligibility supplies its updated Professional projection to Search through the Search-owned refresh contract;
9. request safe notifications if product policy requires.

Search failure must never revert `Review.status`.

### Authorization / Compliance

- publication/hide/remove require approved admin/system/moderation authority;
- moderation outcome is an input reference; ModerationCase remains external;
- Review public text must follow project moderation/display safety rules without moving moderation lifecycle into this Module;
- Review cannot issue TrustBadge or change VerificationCheck.

### Database / Transaction Behavior

- Review transition + local history/outbox atomic;
- reputation aggregate rebuild is separate, idempotent work;
- projection update must reject stale source generations if interface supports it;
- query indexes support published Professional reviews/pagination.

### Events / Jobs

- `ReviewPublished`;
- `ReviewHidden`;
- `ReviewRemoved`;
- reputation rebuild job;
- Search refresh after successful source/projection change;
- consumer dedupe for moderation events.

### Provider Integration

None.

### UI / Admin Surface

- participant/public Review list/view as appropriate;
- admin/moderation visibility controls only if Module/Cluster owns the surface;
- never expose private moderation reason or internal audit metadata publicly.

### Failure Behavior

- stale transition → conflict;
- invalid reverse transition → precondition failure;
- projection service unavailable → retry job; Review remains truth;
- Search unavailable → refresh retries; source/projection remains truth;
- moderation duplicate → inbox replay/no duplicate transition;
- projection mismatch/rebuild failure → operational incident/manual repair path, no source rewrite.

### Tests

- transition matrix;
- authorization for publication/hide/remove;
- included/excluded Review statuses;
- aggregate average/count correctness and empty case;
- projection idempotency/out-of-order source version;
- Search refresh after relevant change only;
- Search failure isolation;
- moderation dedupe;
- hidden/removed cease contribution;
- never mutates TrustBadge/VerificationCheck.

### Documentation Updates

Storage ownership is binding under CL-04-R005: Professional Eligibility writes its rating fields from Review-owned results. Preserve unresolved restore/republication policy.

### Acceptance Criteria

- public rating/count can be rebuilt from Review truth;
- every visibility change has owner event/audit behavior;
- Search receives only public-safe refresh intent;
- no consumer needs to independently decide which Review statuses count.

### Exit Gate

CL-04 Feature 10 is complete for this Module when:

- eligible Review submission and visibility transitions pass;
- rating/count projection is deterministic and rebuildable;
- hidden/removed Reviews no longer contribute;
- projection/Search outage is retry-safe;
- review score never becomes verification truth.

# Phase 3 — Dispute Intake and Review

## 05 Dispute Eligibility, Intake, and Hold Coordination

### Objective

Implement authoritative dispute intake and reliable payout-hold/Order coordination without creating local financial or hold truth.

### Observable Result

An authorized Order participant can receive a dispute-eligibility decision and open the permitted dispute case exactly once. The Dispute becomes visible to participants/admin review, while Hold and Order effects are requested durably through their owners.

### Cluster Build-Plan Link

Implements the intake/coordination core of **CL-04 Feature 11 — Dispute Intake and Payout Hold Coordination**.

### Dependencies

- Feature 02;
- CL-04 Feature 09;
- approved opener actor and dispute eligibility/window rules;
- approved multiplicity;
- Transaction / Order owner facts + dispute-effect command;
- Admin Review / Compliance Hold SH-012 `requestComplianceHold`;
- Notification;
- canonical workflow/outbox/queue.

### In Scope

- `evaluateDisputeEligibility`;
- `openOrderDispute`;
- `getOrderDispute`;
- `listDisputesForActor`;
- durable post-open workflow for:
  - Hold request;
  - Transaction / Order disputed-effect request;
  - Notification;
- participant status DTO separating Dispute state from hold/settlement state.

### Out of Scope

- adjudication;
- refund execution;
- hold lifecycle implementation;
- provider calls;
- evidence upload;
- moderation/legal case;
- dedicated case messaging unless separately approved.

### Module-Owned Data

- `Dispute`;
- initial `DisputeStatus=open`;
- approved opener/history/workflow references;
- `DisputeOpened` event;
- owner-local workflow state if approved.

### Public Interfaces

- `evaluateDisputeEligibility`;
- `openOrderDispute`;
- `getOrderDispute`;
- `listDisputesForActor`.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`;
- SH-004 `resolveCustomerActor` for buyer-side opener where applicable;
- SH-003 `queryOwnerFacts` (Proposed future normalization only; not a prerequisite) for Order participant/transaction state;
- SH-002 `authorizeResourceAction`;
- SH-015 `returnDecisionResult` (Proposed future normalization only; not a prerequisite);
- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock`/approved concurrency;
- SH-046 `publishDomainEvent`;
- SH-029 `appendAuditEvent`;
- SH-049 `orchestrateWorkflowSteps`;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-012 `requestComplianceHold`;
- SH-041 `requestNotification`;
- SH-037 `recordIntegrationFailure`.

Local policy defines dispute eligibility, opener validity, multiplicity, and which hold scope/reason is requested.

### Domain Logic

Primary open flow:

1. validate request;
2. resolve actor/profile context;
3. obtain versioned Order dispute facts;
4. authorize participant action;
5. evaluate local dispute policy;
6. acquire/claim semantic idempotency + concurrency scope;
7. create Dispute in one transaction;
8. write local lifecycle proof/outbox;
9. commit;
10. start durable coordination:
    - request ComplianceHold;
    - request Transaction / Order disputed effect;
    - request Notification;
11. preserve owner results/correlations in approved workflow proof;
12. surface “coordination pending” through workflow/result data, never by inventing hold/refund status on Dispute.

### Authorization / Compliance

- opener must be an approved Order participant/admin/system actor under the finalized policy;
- opening a dispute cannot depend on subscription premium status;
- any financial stop sign is created through Hold owner;
- dispute reason/evidence metadata is minimized in audit/events/telemetry.

### Database / Transaction Behavior

- enforce approved one-case/multiplicity constraint;
- create + outbox/lifecycle proof atomic;
- network calls happen after commit;
- unique conflicts become idempotent replay/domain conflict;
- if a workflow record exists, its semantic owner is Review / Dispute but it may not mirror external truth as authoritative state.

### Events / Jobs

- emit `DisputeOpened`;
- enqueue durable hold/Order coordination;
- each workflow step has semantic idempotency key;
- transient dependency failure retries with bounded backoff;
- dead-letter creates visible ops/manual-review need.

### Provider Integration

None. Payment provider is not called in dispute intake.

### UI / Admin Surface

- participant dispute intake/status;
- initial admin queue visibility may consume `listDisputeReviewQueue` in Feature 06;
- status presentation must distinguish “Dispute open” from “hold coordination pending/confirmed” when such external facts are shown.

### Failure Behavior

- invalid/wrong participant → deny, no row;
- duplicate open → replay/existing or conflict according to approved multiplicity;
- Hold unavailable after Dispute commit → retry workflow; Dispute remains open;
- Order effect unavailable → retry; never write Order directly;
- Notification unavailable → retry independently;
- permanent Hold denial contradictory to domain expectation → manual review/ops, no fake hold.

### Tests

- eligibility by approved participant types;
- invalid Order state/window;
- duplicate/concurrent open;
- create + outbox atomicity;
- hold requested exactly once semantically;
- Order dispute effect contract;
- Hold/Order outage and retry;
- dead-letter/manual-review path;
- no local hold/payment/Order mutation;
- payload minimization.

### Documentation Updates

Update architecture if multiplicity/opener/window rules were resolved. Update dependency contract docs if Hold/Order request shapes change.

### Acceptance Criteria

- Dispute opening is an authoritative local effect independent of downstream transport availability;
- Hold and Order coordination are durable and traceable;
- no field in Dispute pretends to be ComplianceHold, RefundStatus, or provider status;
- duplicate retries cannot create repeated cases/hold requests.

### Exit Gate

Before Feature 06/07:

- intake/eligibility tests pass;
- Hold and Order contract tests pass;
- outage/retry/dead-letter behavior is demonstrated;
- participant can retrieve authoritative Dispute status without direct access to neighboring repositories.

---

## 06 Dispute Review Queue, Evidence Access, and Moderation Routing

### Objective

Provide the administrative review and evidence-reading capabilities needed to adjudicate a Dispute while preserving Media, Messaging, Moderation, authority, and sensitive-access boundaries.

### Observable Result

Authorized reviewers can list/claim/open dispute cases, begin review, inspect approved evidence references through short-lived owner-controlled access, and route non-commercial moderation/legal issues to the correct Module.

### Cluster Build-Plan Link

Completes the review/evidence portion of **CL-04 Feature 11**.

### Dependencies

- Feature 05;
- approved evidence-reference model or explicitly approved MVP reference types;
- Media signed-access interface;
- SH-030 `recordSensitiveAccess`;
- Content Moderation intake interface;
- Role / Authority admin/reviewer actions;
- SH-054 `claimWorkItem` only if canonical proposed operation is accepted/available.

### In Scope

- `listDisputeReviewQueue`;
- `beginDisputeReview`;
- approved reviewer claim/lease integration;
- `recordDisputeEvidenceReference` if schema approved;
- dispute evidence metadata query;
- contextual evidence authorization;
- Media signed access;
- sensitive-access audit;
- moderation/legal routing;
- `addDisputeAdminNote` only within the approved note/history design.

### Out of Scope

- Media upload/scanning/storage;
- raw signed URL generation;
- Thread/Message lifecycle;
- generic admin dashboard shell;
- ModerationCase/LegalNotice decisions;
- adjudication/refund/release;
- unrestricted admin access.

### Module-Owned Data

- Dispute status to `under_review`;
- approved evidence-reference/context records;
- approved case note/history;
- `DisputeReviewStarted` event.

### Public Interfaces

- `listDisputeReviewQueue`;
- `beginDisputeReview`;
- `recordDisputeEvidenceReference` if approved;
- `getOrderDispute`/reviewer detail projection;
- moderation routing command wrapper only as a client of owner interface.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-054 `claimWorkItem` if approved;
- SH-053 `transitionLifecycleState`;
- SH-044 `executeIdempotentCommand`;
- SH-127 `requestMediaAccess`;
- SH-030 `recordSensitiveAccess`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
- SH-034 `sanitizeTelemetryMetadata`;
- Content Moderation public intake;
- SH-041 `requestNotification` where review-start notification is approved.

Local policy: reviewer eligibility, which evidence refs are relevant, and when a commercial case must be routed to moderation/legal handling.

### Domain Logic

Review queue flow:

1. authenticate/authorize reviewer;
2. list cases through Review / Dispute repository/query only;
3. claim case transactionally if claim semantics are approved;
4. transition `open → under_review` through local state policy;
5. append event/audit;
6. for each evidence read:
   - resolve evidence reference;
   - authorize contextual access;
   - call Media access;
   - record sensitive access as required;
7. if evidence reveals content/legal issue, submit Report/Moderation request and retain only safe reference to resulting owner record;
8. do not convert the Dispute into a ModerationCase.

### Authorization / Compliance

- admin/support role alone is insufficient for private evidence;
- evidence access purpose/reason must be explicit where Audit policy requires;
- signed access must be short-lived and target-specific;
- case notes/evidence are not public participant fields unless approved;
- legal/moderation routing does not grant adjudicator permission automatically.

### Database / Transaction Behavior

- begin-review transition is transaction-safe;
- reviewer claim uses shared lease/CAS if implemented;
- evidence relation uniqueness/order/version follows approved schema;
- evidence access itself does not mutate Media object;
- audit/network calls outside source transaction unless an approved control requires fail-closed semantics.

### Events / Jobs

- `DisputeReviewStarted`;
- no Module-owned scheduled job;
- moderation request may be event/command to owner;
- duplicate moderation result handled with consumer dedupe if it later affects local state.

### Provider Integration

None.

### UI / Admin Surface

A Module-owned dispute review surface may include:

- queue;
- case detail;
- participant-safe Order summary;
- evidence references/access action;
- internal notes/history;
- begin-review/claim action;
- moderation/legal routing action.

It must not become a platform-wide admin shell.

### Failure Behavior

- unauthorized reviewer → forbidden without evidence existence leakage;
- claim conflict → stable conflict/reload result;
- evidence missing/private → access denied/not found with minimized detail;
- Media unavailable → case remains reviewable; evidence action fails/retries independently;
- sensitive audit failure follows central control policy; do not silently bypass if policy requires audit-before-access;
- Moderation unavailable → routing request retried/visible; Dispute remains commercial truth.

### Tests

- queue authorization;
- claim/review transition concurrency;
- evidence contextual authorization;
- signed-access TTL/contract;
- sensitive-access audit success/denial metadata;
- no raw storage key/URL persistence;
- moderation routing contract;
- wrong admin/private access;
- no Thread/Moderation/Media lifecycle writes.

### Documentation Updates

Update evidence/claim/note architecture decisions if finalized. Update Media/Moderation contract references if changed.

### Acceptance Criteria

- reviewers can obtain only evidence they are authorized to access;
- every sensitive evidence grant/view is auditable as policy requires;
- commercial case review remains distinct from moderation/legal processing;
- the admin surface depends on public owner interfaces rather than raw provider/storage state.

### Exit Gate

CL-04 Feature 11 is complete for this Module when:

- dispute intake, queue, review transition, hold coordination, and approved evidence access pass;
- no local ComplianceHold or file pipeline exists;
- moderator/legal routing is owner-separated;
- failed external coordination is observable/retryable.

---

# Phase 4 — Dispute Adjudication and Settlement

## 07 Dispute Adjudication: Refund or Release Decision

### Objective

Implement the authoritative adjudication command that chooses refund, release/no-refund, or approved dismissal without claiming that any external financial/hold effect has completed.

### Observable Result

An authorized adjudicator can make exactly one valid case decision. Participants can see the decision separately from settlement progress. A durable settlement workflow is started after commit.

### Cluster Build-Plan Link

Implements the adjudication half of **CL-04 Feature 12 — Dispute Adjudication, Refund/Release, and Closure**.

### Dependencies

- Features 05–06;
- explicit adjudicator authority;
- approved structured decision proof;
- approved `resolved_refund`, `resolved_release`, `dismissed` semantics;
- SH-014 assurance for refund/release actions causing or authorizing financial movement;
- Payment, Order, Hold contract definitions;
- canonical workflow runner.

### In Scope

- `resolveDisputeWithRefund`;
- `resolveDisputeWithRelease`;
- `dismissDispute`;
- adjudication policy;
- structured decision record/history;
- conflict protection;
- `DisputeRefundResolved`, `DisputeReleaseResolved`, `DisputeDismissed`;
- settlement workflow creation/enqueue;
- participant decision-status query.

### Out of Scope

- Stripe/provider call;
- writing Order `RefundStatus`;
- payout transfer/release;
- ComplianceHold status change;
- final `closed` transition;
- chargeback/provider dispute lifecycle.

### Module-Owned Data

- Dispute adjudication/status;
- approved decision proof fields/record;
- lifecycle event/history;
- settlement workflow correlation;
- domain events.

### Public Interfaces

- `resolveDisputeWithRefund`;
- `resolveDisputeWithRelease`;
- `dismissDispute`;
- `getDisputeResolutionStatus`.

### Shared Operations Used

- SH-001 `resolveAuthenticatedActor`;
- SH-002 `authorizeResourceAction`;
- SH-014 `requireStepUpForSensitiveAction` if root policy applies;
- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock` / SH-052 `withOptimisticConcurrency`;
- SH-053 `transitionLifecycleState`;
- SH-031 `appendDomainLifecycleEvent`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
- SH-049 `orchestrateWorkflowSteps`;
- SH-047 `enqueueReliableJob`;
- SH-041 `requestNotification`.

Local policy: which outcomes are valid from current state, required evidence/basis, refund amount bounds, decision finality, and dismissal reasons.

### Domain Logic

Refund decision transaction:

1. authenticate/authorize/step-up as required;
2. lock/compare expected Dispute state;
3. verify no competing adjudication exists;
4. validate refund decision basis and approved amount against Order facts;
5. record structured adjudication;
6. transition to `resolved_refund` under approved semantics;
7. append lifecycle/audit/outbox proof;
8. create durable settlement workflow reference;
9. commit;
10. enqueue financial/Order/Hold coordination.

Release path is equivalent but records `resolved_release`.

Dismissal records the approved dismissal reason and initiates only the downstream cleanup/hold reevaluation required by policy.

### Authorization / Compliance

- adjudication is an explicit high-authority action;
- SH-014 step-up is mandatory for refund/release actions causing or authorizing financial movement;
- refund amount/basis must come from authorized decision and Order facts, not client/provider guess;
- decision notes/evidence are minimized in generic audit/events.

### Database / Transaction Behavior

- serialize competing decisions on one Dispute;
- enforce one adjudication record/current final decision as approved;
- adjudication state + local history + outbox + workflow creation atomic;
- external owner commands happen after commit;
- opposite resolution after commit returns conflict unless an explicit appeal/reopen model exists.

### Events / Jobs

- emit adjudication event;
- enqueue settlement workflow with correlation;
- notification request after decision;
- each downstream step uses semantic idempotency.

### Provider Integration

None. Provider work begins only inside Payment-owned adapter after this Module sends a provider-neutral command through the Payment interface.

### UI / Admin Surface

Admin adjudication controls should visibly distinguish:

- case facts/evidence;
- decision being made;
- “decision recorded”;
- “settlement pending”;
- “settled/closed” only after later workflow.

Do not show provider success merely because the adjudication command returned.

### Failure Behavior

- stale/competing admin decision → conflict;
- missing required evidence/policy basis → precondition denial;
- step-up missing → step-up required result;
- workflow enqueue transient failure after commit → outbox/worker recovery; adjudication remains true;
- Payment/Hold unavailable after commit → Feature 08 workflow retries;
- no fallback direct Stripe call.

### Tests

- authorized/unauthorized adjudicator;
- SH-014 allow/deny and missing-assurance tests for financial refund/release adjudication;
- refund amount/basis validation;
- refund vs release race;
- duplicate same decision replay;
- opposite decision conflict;
- structured proof completeness;
- source transaction + outbox/workflow atomicity;
- no external status mutated in this feature.

### Documentation Updates

Update lifecycle architecture when decision/finality semantics become binding. The financial refund/release SH-014 gate is approved by CL-04-R021; do not invent other action-specific policy.

### Acceptance Criteria

- one Dispute can have one authoritative adjudication under approved rules;
- decision is independently queryable before settlement completes;
- financial/hold owner state is not represented as locally completed;
- workflow correlation is durable and provider-neutral.

### Exit Gate

Before Feature 08:

- concurrency/idempotency tests pass;
- refund and release decisions are distinct and auditable;
- settlement workflow can resume from persisted correlation;
- direct Stripe/Order/Hold writes are absent.

---

## 08 Settlement Reconciliation, Hold Release, and Dispute Closure

### Objective

Coordinate and reconcile downstream Order, Payment, and Hold effects after adjudication, then close the Dispute only when the approved finality conditions are satisfied.

### Observable Result

A refund/release decision progresses through external-owner settlement. Partial failures retry safely. Participants can distinguish decision, pending settlement, settled outcome, and closed case. Duplicate callbacks cannot double financial effects.

### Cluster Build-Plan Link

Completes **CL-04 Feature 12**.

### Dependencies

- Feature 07;
- Transaction / Order SH-108 refund-coordination contract and Payment-owned verified outcomes; approved release reevaluation interface;
- Transaction / Order `applyRefundOutcomeToOrder`/dispute-effect interfaces;
- Hold evaluate/release interface;
- explicit closure semantics;
- consumer event dedupe;
- workflow reconciliation.

### In Scope

- settlement workflow step handlers;
- Payment request/normalized result consumption;
- Order effect request/acknowledgment;
- Hold release/reevaluation request;
- `applyOrderSettlementResultToDispute`;
- `closeDispute`;
- workflow status query;
- retry/dead-letter/manual review;
- reconciliation of stuck workflows using owner APIs;
- `DisputeClosed`.

### Out of Scope

- Payment provider adapter/webhook;
- Order state machine implementation;
- Hold state machine;
- payout ledger;
- chargebacks;
- legal appeals unless separately approved.

### Module-Owned Data

- dispute settlement workflow progress/correlation;
- Dispute closure transition/resolvedAt according to approved semantics;
- local lifecycle/history;
- final domain event.

### Public Interfaces

- `applyOrderSettlementResultToDispute`;
- `closeDispute`;
- `getDisputeResolutionStatus`;
- internal workflow handler contracts.

### Shared Operations Used

- SH-049 `orchestrateWorkflowSteps`;
- SH-050 `reconcileWorkflowStatus`;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-044 `executeIdempotentCommand`;
- SH-045 `deduplicateDomainEvent`;
- SH-051 `acquireAggregateLock`/optimistic concurrency;
- SH-053 `transitionLifecycleState`;
- SH-013 `releaseComplianceHold`;
- SH-011 `evaluateComplianceHold`;
- SH-029 `appendAuditEvent`;
- SH-046 `publishDomainEvent`;
- SH-041 `requestNotification`;
- SH-037 `recordIntegrationFailure`;
- request/telemetry primitives.

Local policy: step order/dependency, accepted owner result codes, when settlement is complete, when close is permitted.

### Domain Logic

Refund path, conceptually:

```text
adjudication already committed
→ send authorized refund decision to Transaction / Order SH-108 requestOrderRefund with semantic idempotency
→ Transaction / Order coordinates Payment refund execution
→ Payment returns/ultimately emits normalized verified result
→ Transaction / Order applies the verified refund outcome
→ consume Order acknowledgment/facts
→ apply settlement result to Dispute workflow
→ request/evaluate ComplianceHold release as policy permits
→ verify all required owner steps complete
→ close Dispute under approved close rule
→ emit DisputeClosed
```

Release path:

```text
adjudication already committed
→ request Payment payout/release reevaluation as appropriate
→ request Order dispute-effect normalization as appropriate
→ request/evaluate Hold release
→ wait for required owner acknowledgments
→ close only after approved completion facts
```

The exact order can be adapted to approved owner interfaces, but ownership cannot change.

### Authorization / Compliance

Workflow/system actions use trusted internal identity. Manual retry/override requires explicit admin authority and audit. Manual refund/release retry or override capable of causing or authorizing financial movement requires SH-014.

### Database / Transaction Behavior

- each workflow step is separately idempotent;
- inbound result events use consumer inbox dedupe;
- workflow state update and local outbox/history are transactional;
- a stale late result cannot overwrite newer adjudication/workflow generation;
- closure is guarded by approved prerequisites and concurrency;
- no transaction spans a network call.

### Events / Jobs

- durable settlement workflow;
- bounded retries;
- dead-letter/manual-review status;
- periodic/manual reconciliation may use a shared worker but only if required by production operation;
- emit `DisputeClosed` after local close commit;
- notifications can report decision/settlement/closure separately.

### Provider Integration

No provider adapter. Payment contract fixtures must be normalized, e.g. success/partial/denied/retryable/manual-review categories. Raw Stripe event names are invalid at this boundary.

### UI / Admin Surface

Participant/admin status must not flatten:

- adjudication outcome;
- Payment execution state;
- Order refund state;
- Hold state;
- Dispute closed state.

Operator view should show stuck workflow step/correlation and safe retry/manual-review action.

### Failure Behavior

- Payment provider-owner failure → retry/dead-letter, decision remains committed;
- Order update unavailable → retry, no local RefundStatus;
- Hold release unavailable → retry, no local release flag;
- duplicate normalized result → inbox replay/no-op;
- conflicting result → manual review/incident, never overwrite blindly;
- closure attempted while required external state pending → `precondition_failed`;
- retry exhaustion → visible manual review, not automatic fabricated close.

### Tests

- refund success end-to-end with owner fixtures;
- partial/denied refund outcomes;
- release path;
- Payment timeout/retry;
- Order timeout/retry;
- Hold release timeout/retry;
- duplicate/out-of-order owner events;
- stale workflow generation;
- concurrent close/late result;
- manual retry audit;
- no double financial command;
- no direct provider call;
- final status truth separation assertions.

### Documentation Updates

Update owner-contract docs if result categories/correlation change. Update architecture only if closure semantics or workflow ownership changes by approved ruling.

### Acceptance Criteria

For any completed test case, architecture and persisted data can answer independently:

1. What did the dispute adjudicator decide?
2. What does Order say about refund/dispute attachment?
3. What did Payment/Payout/Tax execute?
4. What does ComplianceHold say?
5. Is the Dispute closed?

No one field substitutes for the others.

### Exit Gate

CL-04 Feature 12 is complete for this Module when:

- refund/release settlement succeeds under normal path;
- partial failures recover without duplicate financial effects;
- duplicate/out-of-order results are safe;
- closure is impossible before approved prerequisites;
- no direct Stripe, Order-table, Hold-table, or payout-ledger write exists.

# Phase 5 — Compliance and Cross-Cutting Boundary Completion

**Binding retention boundary (CL-04-R011):** hard deletion of an Order must not cascade-delete retained transaction, Agreement, Review, Dispute, or domain-history evidence without owner-specific Privacy/retention evaluation. Privacy issues the instruction; each owner enumerates its targets, evaluates retention/exemption facts, erases/anonymizes eligible data, preserves/minimizes retained evidence, and returns proof to Privacy. Database cascades must not provide an alternate destructive path. Existing cascade behavior requires a later approved database correction; legal retention durations remain unresolved.

## 09 Privacy, Audit, Notification, Moderation, and Media Boundary Completion

### Objective

Complete the Module’s data-owner participation in privacy, audit, notification, moderation, Media access, and observability so no cross-cutting responsibility is left as an ad hoc local implementation.

### Observable Result

Review / Dispute can enumerate and execute privacy instructions, produce required generic audit/access proof, request safe notifications, route moderation/legal concerns, and access approved evidence through Media—all through canonical owner contracts.

### Cluster Build-Plan Link

Completes Module-specific cross-cutting work needed before **CL-04 Feature 13 — Cross-Cluster Contract Proof** and contributes to **Feature 14 — Security, Privacy, Reconciliation, and Production Readiness**.

### Dependencies

- Features 03–08;
- Privacy data-owner executor protocol;
- approved retention decisions sufficient for non-destructive and tested destructive behavior;
- Audit/Event Ledger;
- Media/File Access;
- Notification;
- Content Moderation;
- Observability/Ops;
- Search/reputation interfaces from Feature 04.

### In Scope

- `enumerateReviewDisputeSubjectData`;
- `executeReviewDisputePrivacyInstruction`;
- approved anonymization/erase/retain/export behavior;
- retention-exemption enforcement;
- Review public removal versus privacy erasure behavior;
- generic SH-029 `appendAuditEvent` coverage map;
- SH-030 `recordSensitiveAccess` coverage for evidence;
- notification trigger/template-intent map;
- moderation routing and Review moderation-result handler;
- evidence access telemetry/redaction;
- operational failure recording;
- safe analytics/product event payload definitions if root analytics uses them.

### Out of Scope

- PrivacyRequest/DataErasureJob orchestration;
- legal determination of retention duration;
- Media object deletion mechanics;
- Notification provider delivery;
- ModerationCase/LegalNotice workflow;
- Search indexing implementation;
- generic audit/observability infrastructure.

### Module-Owned Data

- Review/Dispute records affected by privacy instruction;
- Module-owned event/history fields;
- approved evidence associations;
- no cross-cutting owner records.

### Public Interfaces

- `enumerateReviewDisputeSubjectData`;
- `executeReviewDisputePrivacyInstruction`;
- `applyReviewModerationDecision`;
- existing Review/Dispute commands now fully wired to audit/notification/media/moderation intents.

### Shared Operations Used

- SH-096 `enumerateSubjectData`;
- SH-095 `executePrivacyInstruction`;
- SH-097 `evaluateRetentionRequirement`;
- SH-029 `appendAuditEvent`;
- SH-030 `recordSensitiveAccess`;
- SH-041 `requestNotification`;
- SH-043 `resolveNotificationRecipients`;
- SH-127 `requestMediaAccess`;
- SH-045 `deduplicateDomainEvent`;
- SH-034 `sanitizeTelemetryMetadata`;
- SH-033 `writeStructuredLog`;
- SH-037 `recordIntegrationFailure`;
- SH-091 `requestSearchProjectionRefresh` where privacy/moderation changes Review public state.

Local policy: what Review/Dispute data is subject data; what can be anonymized/removed; what is retained; which actions trigger audit/notification; how moderation outcome maps to local Review state.

### Domain Logic

Privacy executor flow:

1. receive trusted Privacy-owned instruction;
2. locate target only within Review / Dispute;
3. evaluate supplied/owner retention facts;
4. apply approved owner-local action;
5. preserve required domain/audit proof;
6. return execution receipt;
7. trigger projection refresh if public Review visibility/content changed;
8. never mutate Privacy workflow status directly.

Evidence access flow:

1. authorize case/evidence context;
2. request Media signed access;
3. record sensitive access;
4. return short-lived access result only;
5. never persist signed URL.

Moderation result flow:

1. dedupe result event;
2. confirm it targets Review;
3. map owner outcome to an approved Review action;
4. execute Review transition;
5. refresh reputation/Search as needed;
6. preserve moderation reference but not copy moderation lifecycle.

### Authorization / Compliance

- Privacy executor accepts only trusted Privacy workflow context;
- retained dispute/financial/legal proof cannot be erased merely because normal product deletion is requested;
- admin evidence access remains contextual;
- notification/audit payloads are sanitized;
- Review removal from public surface does not imply hard delete;
- no retention period is invented.

### Database / Transaction Behavior

- privacy record mutation uses owner transaction and outbox where downstream projection must update;
- retained/exempt records remain queryable only through appropriate protected paths;
- evidence associations and Media objects have separate deletion semantics;
- moderation-result transition uses event dedupe and concurrency;
- no cross-Module record is changed in the same Prisma repository transaction.

### Events / Jobs

- privacy-driven Review visibility/source events as appropriate;
- no separate privacy queue;
- evidence access uses Audit/Media owner operations;
- moderation result uses inbox dedupe;
- notification failures retry in Notification;
- integration failures recorded through Ops.

### Provider Integration

None.

### UI / Admin Surface

- privacy effects may be visible as removed/anonymized Review or retained dispute-safe status;
- admin evidence surfaces use Media access;
- no Privacy admin shell, Notification console, or Moderation dashboard is built here.

### Failure Behavior

- retention exemption → `retention_blocked`/retain receipt, not forced deletion;
- Media access denied → safe denial and access audit according to policy;
- Audit/Notification/Moderation dependency unavailable → follow owner-specific fail/retry policy; do not fabricate domain changes;
- duplicate moderation event → no duplicate transition;
- destructive instruction not supported because retention ruling missing → explicit architecture/policy blocker.

### Tests

- privacy inventory completeness for current fields;
- anonymization/remove/retain cases;
- retention exemption;
- cascade-delete safety/migration behavior;
- Review projection refresh after privacy/moderation visibility change;
- evidence access + sensitive audit;
- notification payload contains no prohibited free text;
- audit metadata redaction;
- moderation result dedupe/transition;
- no local privacy/media/notification/moderation implementation.

### Documentation Updates

Update privacy/retention section when approved legal/business policy arrives. Record all current data fields and executor behavior in Module architecture. Update progress tracker.

### Acceptance Criteria

- Privacy orchestration can operate on Review/Dispute without raw repository access from Privacy;
- required retention can block destructive action;
- private evidence is never returned through permanent URLs;
- generic audit/notification/observability records contain safe references rather than raw case content;
- moderation remains separate truth.

### Exit Gate

- privacy, access-audit, moderation, notification, and observability contract tests pass;
- no destructive privacy test bypasses retention;
- no signed URL/provider payload/private case text is persisted in generic telemetry;
- Module is ready for full cross-cluster contract proof.

---

# Phase 6 — Module Integration Proof

## 10 Review / Dispute Cross-Module Contract Proof

### Objective

Prove the Module works with its major neighboring owners through public contracts/events rather than direct database assumptions.

### Observable Result

Complete Review and Dispute journeys pass against real or contract-faithful owner implementations/fixtures. Negative dependency decisions and transient failures are safe. Tests demonstrate that no neighboring truth has been absorbed.

### Cluster Build-Plan Link

This is the Review / Dispute contribution to **CL-04 Feature 13 — Cross-Cluster Contract Proof**.

### Dependencies

- Features 01–09;
- CL-04 Features 10–12 complete for this Module;
- contract fixtures or implementations for:
  - Customer / Buyer Profile;
  - Transaction / Order;
  - Role / Authority;
  - Professional reputation/Profile;
  - Payment / Payout / Tax;
  - Admin Review / Compliance Hold;
  - Media / File Access;
  - Search / Public Visibility;
  - Notification;
  - Audit / Event Ledger;
  - Privacy / Data Erasure;
  - Content Moderation;
  - Observability/Ops.

### In Scope

Contract/integration proof for:

```text
CustomerProfile → Review submission
Order → Review eligibility
Review aggregate → Professional Eligibility rating-field update → Professional projection → Search refresh
Order participant → Dispute open
Dispute → ComplianceHold request
Dispute adjudication → Payment command
Payment normalized result → Order refund effect
Order result → Dispute settlement/closure
Dispute evidence → Media access + sensitive audit
Review moderation → local visibility transition
Privacy → Review/Dispute executor
Review/Dispute events → Notification
```

### Out of Scope

Implementing missing neighboring Module business logic; changing CL-04 sequence; new product features; direct integration shortcuts added just for tests.

### Module-Owned Data

No new ownership. Test fixtures may expose a needed migration, but any ownership/schema change returns to architecture governance.

### Public Interfaces

All Module public commands/queries/events/privacy executor are exercised. Consumers/producers use versioned contract DTOs.

### Shared Operations Used

All canonical operations actually exercised by the journeys. No new shared operation should be invented in this feature merely to make integration easier.

### Domain Logic

Integration tests must prove both positive and negative owner facts:

- Order completed versus not reviewable;
- correct versus wrong CustomerProfile;
- correct seller target;
- participant versus nonparticipant dispute;
- Hold accepted versus denied/unavailable;
- Payment success/partial/denied/retry;
- Order refund outcome accepted/rejected/stale;
- Media evidence permitted/denied;
- moderation action valid/duplicate;
- privacy erase versus retention;
- Search/Notification unavailable after source commit.

### Authorization / Compliance

Cross-module negative-path tests are mandatory:

- wrong buyer;
- wrong seller/participant;
- unauthorized admin;
- missing step-up where applicable;
- evidence private/blocked;
- retained privacy data;
- moderation route;
- stale/duplicate external result.

### Database / Transaction Behavior

- tests must not directly mutate neighboring repositories just to create workflow success, except isolated fixtures owned by those test harnesses;
- real outbox/inbox/queue runner should be used in integration environment where available;
- assert authoritative owner rows separately;
- verify no distributed transaction across Module databases/repositories is assumed.

### Events / Jobs

- verify event schema/version/correlation;
- verify consumer dedupe;
- verify queue retry/dead-letter;
- verify outbox delivery after source commit;
- verify out-of-order event behavior.

### Provider Integration

Use Payment-owner normalized fixtures or real adapter test harness. Raw Stripe payload/status types must be rejected/unrepresentable in Review / Dispute public contracts.

### UI / Admin Surface

Where UI exists, Playwright or equivalent journeys:

1. completed Order → buyer Review → publication/reputation;
2. Order → participant Dispute → admin queue;
3. refund adjudication → pending settlement → settled/closed;
4. release adjudication → owner-separated completion;
5. protected evidence access denial/allow;
6. dependency failure/recovery where practical.

### Failure Behavior

Simulate:

- dependency timeout;
- duplicate event;
- stale owner-fact version;
- dead-letter workflow;
- Search/Notification outage;
- Hold/Payment outage;
- conflicting settlement result;
- privacy retention block.

Source truth must remain correct in every case.

### Tests

- public contract tests;
- integration tests;
- E2E;
- RLS/authority tests if project uses RLS at this boundary;
- idempotency/replay;
- event ordering/dedupe;
- queue retry/dead-letter;
- privacy/retention;
- audit completeness.

### Documentation Updates

Any discovered contract mismatch is resolved in the owner’s public-interface docs and, if architectural, root/Cluster/Module architecture. Do not patch around it privately.

### Acceptance Criteria

- no integration test requires Review / Dispute to write another Module’s source table;
- no neighboring Module needs direct Review/Dispute repository access;
- all major owner contracts have positive and negative tests;
- partial failures preserve one-owner-per-truth.

### Exit Gate

This Module’s CL-04 Feature 13 participation passes when:

- critical cross-module journeys pass;
- contract versions/reason codes are stable;
- event/queue replay is safe;
- no direct cross-owner/provider implementation is required to make tests green.

---

# Phase 7 — Module Hardening and Production Verification

## 11 Security, Concurrency, Privacy, Reconciliation, and Production Hardening

### Objective

Prove Review / Dispute is production-safe under races, replays, dependency degradation, privacy/retention constraints, data migration/backfill, and operational recovery.

### Observable Result

The Module survives concurrent Review/Dispute actions, duplicate/out-of-order events, owner/provider outages, privacy instructions, and stuck workflows without corrupting source truth or duplicating financial effects. Operators can identify and safely remediate failures.

### Cluster Build-Plan Link

This is the Review / Dispute contribution to **CL-04 Feature 14 — Security, Privacy, Reconciliation, and Production Readiness**.

### Dependencies

- Features 01–10;
- production-like queue/outbox/inbox;
- approved retention rules sufficient for destructive paths;
- owner reconciliation endpoints where applicable;
- migration/backfill tools;
- performance/load-test fixtures;
- observability dashboards/alerts or testable telemetry sinks.

### In Scope

Hardening for:

- Review submission race;
- Review publication transition race;
- reputation projection replay/backfill;
- duplicate/out-of-order moderation events;
- duplicate/concurrent Dispute open;
- competing adjudications;
- duplicate Payment/Order/Hold result events;
- workflow retry exhaustion;
- settlement reconciliation;
- stale workflow generations;
- privacy erase/anonymize/retain;
- cascade-delete/retention safety;
- evidence access security;
- telemetry redaction;
- query/index performance;
- backfill/migration safety;
- operator/manual retry;
- deploy rollback/data compatibility.

### Out of Scope

New rating scale, new dispute policy, new appeal model, new provider, new moderation feature, new Track entitlement, or any feature deferred by architecture.

### Module-Owned Data

No new ownership. Schema changes are permitted only to harden approved Review/Dispute truth—indexes, version fields, migration-safe proof fields—after architecture review when they change meaning.

### Public Interfaces

No gratuitous new public APIs. Hardening may add operator-safe internal commands for reconciliation/retry only if their authority, idempotency, audit, and source semantics are explicit.

### Shared Operations Used

- SH-044 `executeIdempotentCommand`;
- SH-051 `acquireAggregateLock`;
- SH-052 `withOptimisticConcurrency`;
- SH-045 `deduplicateDomainEvent`;
- SH-047 `enqueueReliableJob`;
- SH-048 `executeRetryWithBackoff`;
- SH-049 `orchestrateWorkflowSteps`;
- SH-050 `reconcileWorkflowStatus`;
- SH-115 `buildAggregateProjection`;
- SH-097 `evaluateRetentionRequirement`;
- SH-030 `recordSensitiveAccess`;
- SH-029 `appendAuditEvent`;
- SH-032 `createRequestContext`;
- SH-033 `writeStructuredLog`;
- SH-034 `sanitizeTelemetryMetadata`;
- SH-037 `recordIntegrationFailure`;
- SH-036 `emitMetric`/health primitives if available.

No new local infrastructure.

### Domain Logic

Hardening must validate these non-negotiable outcomes:

1. one valid Review effect per Order under concurrent submission;
2. one valid active/current Dispute case according to approved multiplicity;
3. only one competing adjudication wins;
4. same adjudication never triggers duplicate financial command;
5. a late result cannot overwrite a newer workflow generation;
6. reputation can be rebuilt from Review truth;
7. dead-letter does not imply domain success;
8. retention can stop destructive erase;
9. operator retry uses the same idempotent owner contracts;
10. recovery never edits another Module’s database directly.

### Authorization / Compliance

- review all public/admin actions against Role / Authority;
- verify step-up policy on high-risk adjudication/manual retry;
- verify private evidence access and access-audit;
- verify no private case payload enters analytics/logs;
- verify privacy/export interfaces expose only authorized subject data;
- verify public Review surfaces do not expose removed/private dispute data.

### Database / Transaction Behavior

- stress unique constraints;
- test locks/CAS under parallel execution;
- verify indexes/query plans for:
  - Review by Professional/status/pagination;
  - Review by Order;
  - Dispute by Order/status/opener/queue fields;
- migration tests with representative legacy nullable actor data;
- resumable, idempotent backfills;
- reconciliation/backfill never overwrites newer owner state;
- destructive migrations require rollback/backup strategy according to root standards.

### Events / Jobs

- production-like event replay;
- duplicate and out-of-order delivery;
- queue lease expiry/worker crash;
- retry exhaustion/dead-letter;
- resumable projection rebuild;
- settlement reconciliation against Order/Payment/Hold public facts;
- health/lag metrics.

### Provider Integration

Still none. Simulate provider degradation only through Payment-owner normalized contract behavior.

### UI / Admin Surface

- operator view can identify stuck dispute workflow safely;
- manual retry/reconcile actions require authority/audit;
- no raw provider payload or sensitive evidence appears in ops UI/logs;
- participant UI never reports “refund complete” based solely on Dispute decision.

### Failure Behavior

- poison job is isolated, not infinite retry;
- conflicting normalized owner state produces manual review, not automatic overwrite;
- unavailable dependency yields degraded operational state while domain state remains accurate;
- privacy destructive action blocked by retention returns explicit retained result;
- backfill resumes after interruption;
- migration failure stops deployment rather than partially reinterpreting actor identity.

### Tests

- parallel Review submit stress;
- parallel publication transition;
- parallel Dispute open;
- refund-vs-release race;
- duplicate workflow command/result;
- late/out-of-order event;
- queue lease loss/retry;
- dead-letter/manual retry;
- projection rebuild/backfill;
- Payment/Hold/Order reconciliation;
- privacy retention;
- evidence access authorization/audit;
- telemetry redaction fixtures;
- query plan/performance;
- migration/backfill resume/rollback;
- full critical E2E journeys.

### Documentation Updates

- progress tracker;
- runbook/operator recovery notes;
- architecture only if hardening discovers and approves a binding ownership/lifecycle change;
- migration/backfill documentation;
- known residual risk register.

### Acceptance Criteria

- no high-severity ownership, authorization, privacy, retention, or concurrency issue remains;
- duplicate/replay behavior is deterministic;
- external degradation cannot fabricate Review/Dispute/financial success;
- operator can recover stuck workflows through supported public/owner paths;
- Review/Dispute source truth is rebuildable/auditable from approved records;
- migrations/backfills are reversible/resumable according to root standards.

### Exit Gate

Module production verification passes when:

- all feature/unit/contract/integration/E2E/hardening tests pass;
- typecheck/lint/format/build/migration checks pass according to repository standards;
- concurrency/replay tests demonstrate one semantic effect;
- privacy/retention tests pass;
- telemetry safety checks pass;
- no prohibited duplicate implementation exists;
- no unresolved architecture question is silently encoded in production behavior.

---

# Module Integration Phase

Feature 10 is the explicit Module integration proof. It validates Review / Dispute across owner APIs/events while leaving neighboring truth where it belongs.

Minimum boundary proof:

```text
CL-01
  Identity & Access        → actor
  Role / Authority         → permission
  Customer / Buyer Profile→ buyer actor

CL-03 / CL-04 neighbors
  Professional/Profile     ← reputation projection
  Transaction / Order     ↔ SH-108 refund coordination and settlement
  Payment/Payout/Tax       ↔ provider execution behind Order for refunds; approved release effects
  Transaction / Order      ↔ Order facts, dispute/refund attachment

CL-07
  Notification             ← lifecycle alert intent
  Messaging                ↔ approved case/order communication context

CL-08
  Privacy / Data Erasure   → privacy instruction / retention
  Review / Dispute         → owner execution receipt

CL-09
  Compliance Hold          ↔ hold request/release
  Audit / Event Ledger     ← audit/access proof
  Content Moderation       ↔ report/moderation outcome
  Observability / Ops      ← technical failure/telemetry

CL-02
  Professional Eligibility ← Review-owned reputation aggregate
  Search                   ← resulting Professional projection

CL-05
  Media / File Access      ↔ approved dispute evidence access

CL-10
  Gamification / Rewards   ← approved ReviewPublished fact, if configured
```

The integration phase must test contracts rather than reach through neighboring repositories.

---

# Module Hardening Phase

Feature 11 is the hardening phase. It is intentionally limited to Review / Dispute production risks:

- state transition races;
- command idempotency;
- domain-event replay/dedupe;
- settlement workflow replay/reconciliation;
- dependency/provider-owner outage;
- access security;
- private evidence handling;
- privacy/retention;
- audit/access-audit completeness;
- telemetry safety;
- projection rebuild/backfill;
- migration safety;
- query performance;
- operator recovery.

It must not become a catch-all for postponed lifecycle rules, actor identity decisions, rating scale, dispute multiplicity, or closure semantics. Those are architecture preconditions for their earlier features.

---

# Phase Summary

| **Phase** | **Name** | **Features** |
| --------- | -------- | ------------ |
| 1 | Contracts and Source-of-Truth Foundation | 01–02 |
| 2 | Review Lifecycle and Reputation | 03–04 |
| 3 | Dispute Intake and Review | 05–06 |
| 4 | Dispute Adjudication and Settlement | 07–08 |
| 5 | Compliance and Cross-Cutting Boundary Completion | 09 |
| 6 | Module Integration Proof | 10 |
| 7 | Module Hardening and Production Verification | 11 |

**Total numbered Module features: 11**

### Cluster alignment

| Module feature | Primary CL-04 feature supported |
| --- | --- |
| 01, 03, 04 | CL-04 Feature 10 — Post-Order Review and Reputation Projection |
| 02, 05, 06 | CL-04 Feature 11 — Dispute Intake and Payout Hold Coordination |
| 02, 07, 08 | CL-04 Feature 12 — Dispute Adjudication, Refund/Release, and Closure |
| 09, 10 | CL-04 Feature 13 — Cross-Cluster Contract Proof |
| 09, 11 | CL-04 Feature 14 — Security, Privacy, Reconciliation, and Production Readiness |

This alignment does not authorize Review / Dispute to start before its Cluster prerequisites have passed.

---

# Module Execution Pattern

Before implementing each numbered feature:

1. Read root architecture and standards.
2. Read the Canonical Shared Operations Registry.
3. Read CL-04 architecture and build plan.
4. Read this Module architecture and implementation plan.
5. Read public-interface sections for direct dependencies touched by the feature.
6. Confirm the previous Module feature exit gate and the corresponding Cluster prerequisite.
7. Confirm every unresolved architecture decision that blocks the feature has been explicitly resolved.
8. Write the required feature implementation specification.
9. Implement only this feature.
10. Run required quality checks.
11. Verify public workflows/contracts, including negative paths.
12. Update progress.
13. Update architecture only when a binding decision legitimately changed and was approved.
14. Record unresolved risks, dead-letter/manual-recovery behavior, and deferred work.

---

# Required Feature Implementation Specification

Immediately before coding a numbered feature, the coding agent must produce a concise specification containing:

- **Objective**
- **Observable result**
- **Cluster build-plan link**
- **Dependencies**
- **In scope**
- **Out of scope**
- **Owned data affected**
- **Public contracts**
- **Shared operations consumed**
- **Permissions/compliance**
- **Primary workflow**
- **Provider integration**
- **Jobs/events**
- **Idempotency/concurrency**
- **Database/transaction behavior**
- **Error behavior**
- **Tests**
- **Acceptance criteria**
- **Documentation updates**

Do not pre-generate implementation specifications for all remaining features. The specification is written immediately before its feature so it can reflect current repository state and prior exit-gate results.

---

# Required Completion Report

After implementing each numbered feature, the coding agent must report:

- Feature completed
- Cluster feature/milestone supported
- Files added
- Files changed
- Database changes
- Migrations
- Backfills
- Dependencies added
- Module public interfaces added/changed
- Dependency contracts consumed/changed
- Shared operations reused
- Events/jobs added
- Workflow steps added/changed
- Provider adapter changes — expected to be **none** in Review / Dispute unless architecture changes
- Tests added/changed
- Commands run
- Typecheck/lint/format/build results
- Migration verification
- Manual/contract/E2E verification
- Authorization/compliance verification
- Documentation updated
- Assumptions
- Known failures
- Remaining risks
- Deferred work
- Unresolved architecture items encountered
- Exit-gate result

A completion report must explicitly state if any prohibited duplicate implementation was introduced. The expected result is “none.”

---

# Final Quality Check

Before declaring the Module plan complete or the implementation production-ready, verify:

1. Review and Dispute source truth each have exactly one owner.
2. No Order, RefundStatus, Payment, PayoutTransfer, ComplianceHold, ModerationCase, MediaAsset, Search, Notification, PrivacyRequest, or audit lifecycle was absorbed.
3. Every shared operation is consumed rather than duplicated.
4. Shared mechanism / separate truth boundaries are explicit in code and tests.
5. Review/Dispute commands and queries have clear ownership and stable contracts.
6. Cross-Module reads use public owner facts/contracts where appropriate.
7. Raw provider adapters/statuses do not enter this Module.
8. Dispute adjudication, Order refund state, financial execution, and hold state remain independently answerable.
9. Audit, domain history, workflow state, and observability are distinct.
10. Privacy orchestration remains Privacy-owned.
11. Search remains a rebuildable projection.
12. Review rating/reputation never becomes verification truth.
13. Media mechanics remain Media-owned.
14. Notification delivery remains Notification-owned.
15. Idempotency and concurrency are database/platform-backed.
16. Domain events publish only after source commits and are consumer-deduplicated.
17. Every numbered feature has tests and a passed exit gate.
18. Features align with CL-04 Features 10–14 and do not independently reorder the Cluster.
19. Unresolved decisions remain documented rather than encoded by guess.
20. A coding agent can execute each feature without inventing architecture.

## WA-R008 — Public Media boundary alignment

External file-access calls above use SH-127 `requestMediaAccess`; Media alone performs SH-087 signing internally after contextual authorization and Media safety/grant checks. SH-127 retains Proposed ruling status for owner-specific integration completion. Required caller bindings, expiry, revocation and access-proof contracts must pass before production use. Existing supported public-processed media rules are unchanged.


## WA-R022 — Review and Dispute durable adjudication

Class: **AI_RESOLVED**.

New buyer Reviews bind the Order's authoritative CustomerProfile author and ProfessionalProfile target; User is authentication/audit identity. Review owns append-only revision/lifecycle evidence using SH-031, while the current Review record is its present state. This does not authorize user editing or a publication policy: those product choices remain explicit. Professional reputation consumes Review's versioned aggregate (ProfessionalProfile ID, rating sum/count or derived average/count, projection/source version); use an idempotent owner command/public contract, not direct profile writes. Exact transport name is implementation detail; older aggregate versions cannot overwrite newer ones.

Dispute owns immutable case events, adjudication decisions and workflow-step evidence: actor/authority proof, decision/reason/basis/time, amount/currency/basis where applicable, source Order version, semantic command identity and required Hold/Order settlement correlations. Mutable adminNotes is not adjudication or history. Keep authorized notes as append-only records with controlled reason codes and minimized text; corrections reference previous entries. Use an owner version token checked atomically on competing adjudications. Shared execution handles retries; Dispute records whether each required effect is pending, completed or failed.

`resolved_refund`/`resolved_release` represent the committed adjudication outcome, not completed financial movement. `closed` requires all required downstream outcomes confirmed/reconciled, or a durable authorized determination that none apply. Dismissal must state a controlled basis and require no outstanding effects before closure. A failed/refused/timed-out refund does not become closed success; retry/reconciliation stays visible. Financial effects go through Order/Payment and Hold owners with idempotent correlations. This resolves the proof/finality distinction without selecting eligible openers, case multiplicity, deadlines or appeal/reopen product policy.

Database migration must supply owner history and workflow evidence rather than extending generic Audit into a dispute ledger. Review/Event and Dispute/Event names are conceptual owner records, with exact models/FKs/indexes deferred until the coordinated database pass. Acceptance: mutually exclusive adjudications, audit versus domain-proof distinction, downstream timeout, duplicate refund result, stale reputation aggregate and reconstruction after restart.

Duplicate-collapse scope: CL04-U037/041/042/043/045; CL03-HD082; CL-04-R010 persistence strategy; review-author portion of CL-04-R007. Unnamed adjacent questions are not closed.


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

## WA-R028 — Digital delivery evidence and policy separation

Classification: AI_RESOLVED_WITH_TRADEOFF. Resolves the technical evidence/text-storage boundary while preserving PRODUCT_OWNER_CHOICE P09/P10 for refund finality and allowance consumption. It does not activate either policy.

Digital Goods owns an immutable contextual policy-content revision with Offering/policy identity, locale/jurisdiction applicability, terms/refund/license versions, exact retained content or immutable Media document/version reference, checksum and effective interval. Acceptance binds the precise revision/rendered presentation and contextual Order/User evidence. Do not overwrite accepted content on policy edit or use an unresolvable hash/version as historical proof. Consent owns generic disclosure content/proof separately; neither owner's proof implies the other's requirements passed. Actual legal text, applicable rights and retention remain external activation requirements. This supplies the persistence direction missing from Digital Goods §35.9; exact relational names follow coordinated schema conventions.

Separate grant issuance, download intent, transfer attempt, observed delivery outcome and policy evaluation. Digital Goods owns each immutable logical delivery identity bound to actor, asset version, Order entitlement reference, grant and policy revision. Media owns storage/transport evidence and returns a normalized authenticated receipt correlated to that identity; a browser assertion is untrusted. Video playback progress and byte serving are different observations and cannot silently stand in for Digital Goods delivery. Preserve observed byte/range/completion evidence with adapter capability and timestamps; an adapter that cannot establish completion returns unknown rather than manufactures success. Completion of server delivery never claims the person read or understood the content.

A signed URL or accepted terms is not proof of download completion. Record it as the distinct event it is. Retries/resumptions for the same logical intent retain identity and attempt history; conflicting asset/actor bindings reject. Finite-allowance implementations must account for in-flight reservations under the grant lock so concurrent requests cannot bypass the approved cap; do not release an unknown outcome merely on client timeout. Reconcile durable owner/Media evidence before deciding release/consumption. The exact consumption event is P10, not chosen by this technical protocol. Unknown evidence cannot automatically make a purchase non-refundable. No `used`, URL or playback projection grants Order refund authority.

Expose delivery evidence to Order/Review as a versioned owner query containing logical identity, asset version, accepted policy/proof reference, grant state, observations and their reliability, with minimal actor/context references. Order/Review apply their approved refund/dispute policy and current authorization; Media and Digital Goods do not execute financial refunds or declare legal finality. P08 case reopening may add a new interpretation/decision cycle while retaining the original observations. Corrections append evidence and reevaluate projections; they never rewrite the old observation or repeat an old financial effect.

Acceptance before activation: URL issued without bytes, aborted transfer, range resume, duplicate receipt, unknown completion, concurrent last-allowance requests, changed policy after purchase, stale/revoked Order entitlement and later dispute cycle. These tests establish technical truthfulness; approved P09/P10 behavior and actual provider capabilities remain separate prerequisites.

## WA-R029 — Approved digital refund, download and seller-acceptance policies (P09–P11)

Binding product-owner ruling: 2026-10-01 America/New_York (2026-10-02 UTC). Supersedes the open P09–P11 alternatives and contrary conceptual payment/acceptance sequences. WA-R028 continues to govern truthful delivery evidence.

P09: At launch, digital access, grant issuance, streaming and download completion never automatically make a purchase non-refundable. Delivery/access evidence may inform authorized refund/dispute review but never determines the result alone. Apply the applicable product/refund policy, dispute facts and required external/legal rules. An approved refund or revocation triggers only the downstream access consequences specified by the owning Order/Digital Goods policy. Download history alone neither revokes access nor preserves it against an authorized revocation. No automatic `final_after_access` denial is enabled by a stored enum value.

P10: Consume one allowance only when one user-initiated logical download successfully completes with verified delivery. Retries, resumes, range requests, duplicate transport attempts and recovery of the same logical download consume no additional allowance. Failed or unverified delivery consumes zero. A genuinely new user-initiated download after a completed one may consume another allowance only when the applicable product policy actually limits download count. Finite `used` means allowance exhausted; unlimited grants are not exhausted by first use. Completion observation proves delivery, not human reading or legal acceptance.

Digital Goods mints and persists the logical-download identity at explicit user initiation, with actor/asset-version/grant/Order/policy binding. Transport retries cannot mint a new identity. Atomically convert that intent's reservation to one consumption on its first verified completion; a unique consumption reference prevents duplicates. Resumes retain the same identity. A new explicit post-completion initiation is a new logical identity, subject to policy and current authorization. Unverified attempts remain zero-consumption even while their in-flight reservation is reconciled. Bound reservation lifetime through server-side access expiry/revocation and reconcile before releasing capacity; never strand allowance indefinitely or release while an old transfer remains capable of independently completing. Late receipts reconcile to the original identity and cannot charge another allowance. Provider evidence incapable of proving the approved completion event cannot support finite-count consumption; do not substitute URL issuance, elapsed time or client claims. This capability requirement gates that delivery adapter, not P10's product meaning.

P11: For live or seller-performed services, final capture requires seller acceptance. Acceptance is either explicit approval of the specific Order/Gig/service request or valid precommitted acceptance: the seller intentionally configured an approved instant-book/availability/product policy and the frozen requested transaction satisfies all its constraints. A matching accepted Gig award satisfies acceptance; merely publishing a service does not. Published standalone downloads and self-paced digital courses/products may auto-accept because fulfillment requires no later seller performance decision. Payment authorization/holds may precede acceptance where Payment architecture permits; authorization is not final capture. Platform screening has its separate approved source, with no fabricated seller.

Order records immutable acceptance evidence: seller/context, explicit decision or intentional precommit policy identity/version, frozen scope/price/package version, applicability result and timestamp. A precommit must be active and applicable when accepted, scoped to the actual seller/product, and cannot be inferred from a premium flag or open calendar alone. Policy changes do not rewrite already recorded acceptance; material requested scope/price changes require fresh acceptance of the changed terms. Recheck current financial capability, cancellation/hold and payment authorization validity immediately before capture. Payment accepts a uniquely identified Order-authorized capture intent with acceptance proof; retries preserve that effect identity and uncertain outcomes reconcile before any new capture. No capture from stale acceptance for different terms or from mere Booking existence.

Order remains transaction truth and Booking owns individual scheduled sessions. Acceptance is evidence within Order, not a second Order/Booking lifecycle or a separate booking authority. A multi-session package acceptance binds purchased scope; each Booking still uses current eligibility/conflict checks and bounded Order session authorization. Instant booking does not bypass locks, consume nonexistent availability or displace customers. Decline/expiry releases only valid owner reservations/authorizations; any already captured amount follows an independently authorized refund. Numerical response windows remain versioned policy, not invented here.

Implementation acceptance requirements: access/completion cannot auto-deny refund; authorized revocation follows current owner policy; aborted/unverified delivery zero consumption; range/resume/replay one consumption; new post-completion initiation counts only under bounded policy; concurrent last allowance; late receipt reconciliation; explicit versus valid precommitted acceptance; absent/revoked/inapplicable precommit denied; changed terms need new acceptance; Gig acceptance matching; authorization-before-acceptance permitted but capture-before-acceptance denied; capture retries idempotent; Booking conflict rules unchanged. These are required tests, not executed runtime claims.

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

## WA-R035 — Supply lifecycle, history and source projections

Classification: AI_RESOLVED_WITH_TRADEOFF except explicitly deferred or external activation requirements.

This ruling supersedes the proposed/unresolved lifecycle and projection alternatives named below; implementation still requires forward schema coverage and contract fixtures. Professional graph: create→draft; draft→active after current activation readiness; active→paused; paused→active after current readiness; draft/active/paused→suspended only by an authorized source restriction; draft/active/paused→archived by owner-authorized retirement. Archiving a suspended record may record retirement intent but cannot remove the restriction. Archived→draft is an explicit owner restore command, never implicit activation. Suspended→draft requires authorized release of all applicable restriction sources; subsequent activation rechecks readiness. Preserve previously acquired transactions and obligations. Ordinary dependency loss invalidates the affected action/public decision and requests reevaluation, not an automatic Profile status change. Only an explicit source policy may instruct suspension.

Offering graph: draft→active by publish; active→paused; paused→active by resume, each activation requiring current composed gates. Draft/active/paused may enter under_moderation/disabled_by_moderation/disabled_by_dmca only from a valid Moderation decision. Those restriction states may change to another restriction state only with a superseding valid decision. Restriction clearance restores to draft, preserving all other restriction sources; publication is a separate fresh command. Rejected→draft is an explicit correction/resubmission command after the rejecting owner permits it. Draft/active/paused/rejected→archived; archived→draft by explicit restore. Retirement never clears restrictions, destroys Order snapshots or grants a refund. An Offering kind can change in draft only before any Order, delivery or durable external reference; otherwise create a new Offering. isPublic is seller publication intent; effective visibility additionally requires active lifecycle, current SH-024 decision and no applicable restriction. Moderation timestamps are evidence, not independent allow flags.

Adopt immutable owner lifecycle histories for ProfessionalProfile and Offering, with aggregate version, prior/next state, command/source decision identity, actor, timestamp and policy/decision references. Mutations commit history and outbox atomically using expected opaque version plus row serialization for competing transitions; updatedAt alone is not the concurrency token. Publication/activation and seller Order acceptance retain immutable minimized gate decisions/source versions; current actions still reevaluate. Legacy financial/Trust columns remain non-authoritative compatibility projections until a measured reader inventory and forward migration remove them; never backfill authoritative readiness from a legacy boolean.

onboardingCompleteAt is the first successful owner activation after required onboarding facts pass, immutable except an audited data correction. It is not current readiness. ProfileCompleted.v1 may qualify one Gamification rule per profile and rule revision, containing profileId, subject User reference, firstCompletionAt, aggregateVersion, eventId; no raw onboarding facts. Gamification decides awards and source-event dedupe. Reinstatement does not emit another first completion. Dependency changes are owner outbox facts carrying target, changed dimension and source version; Professional/Supply consume idempotently and reevaluate current truth. Do not propagate a copied allow decision indefinitely. Booking availability is not an eligibility prerequisite; a public availability presentation uses Booking's separately authorized query and never changes Professional status.

Public Professional projection allowlist: professionalProfileId, slug, display name, approved biography, accepted active taxonomy IDs/labels/revisions, owner-supplied public avatar rendition reference, Review-owned ratingAverage/ratingCount with reputation version, and SH-131 fuzzy public location when allowed. Public Offering projection: offeringId, professionalProfileId, slug, title, approved summary, kind, accepted taxonomy IDs/labels/revisions, current public pricing summary/currency, approved public rendition references and public delivery/location mode. Each includes sourceVersion and current public-readiness evidence. Exclude User IDs, contact details, exact location, credential documents, provider refs, financial/Healthcare/hold reasons. Search must obtain URLs through approved Media/public rendition rules; no private original URL. Review→Professional transport is an outbox-triggered owner query getProfessionalReputation.v1 returning profileId, ratingAverage, ratingCount, projectionVersion, then a version-checked Professional projection command; stale events trigger current query rather than regress values.

priceFromCents is a rebuildable minimum of currently eligible active pricing options in one currency, not purchase truth. Missing or mixed-currency options produce no priceFrom value, never zero/implicit conversion. Orders bind the selected immutable price/package. isFeatured has no ranking or commercial effect at launch; promotion is deferred pending a separately approved owner policy. Heterogeneous bundle Offering creation remains disabled; this does not disable P02 multi-session packages within supported kinds. No new seller entitlement gates: supported effects remain approved Professional commission terms; unknown keys cannot gate drafting or fabricate quota. SH-016 action keys are activate_profile, public_visibility, publish_offering, respond_to_gig, participate_in_order; payout stays Payment-owned.

Owner status/remediation notifications use committed source-event identity, generic status/remediation template and safe authenticated destination; no sensitive provider/Healthcare/hold details. Notifications do not prove readiness. No generic admin force-ready override: each source owner must authorize and record its own correction, followed by reevaluation. Required verification includes stale-resume versus restriction, archive/restore preserving obligations, projection field exclusion, duplicate first-completion award, and reputation version replay. These are implementation acceptance criteria, not tests already executed.


## WA-R039 — Gig award and Order outcome boundary

Apply the scoped WA-R039 contract in `context/reconciliation/platform-architecture-rulings.md`: Gig serializes one current winning assignment and retains immutable accepted proposal/terms and lifecycle history; Order binds its source revision and remains purchase/completion truth. Booking/delivery facts cannot independently finish a multi-session purchase. Review case cycles preserve completed work history and cannot replay financial effects. Gig consumes only the authorized current owner outcome; a closed dispute is not an automatic restoration instruction. P14/P15 response revision and loser-disposition choices remain open, so the full Gig acceptance contract is not frozen. No schema/runtime completion is claimed.

Sequence owner history and coordinated winner constraint/source DTO before acceptance integration. Verify competing awards, revise/withdraw races, altered-payload replay, partial-session completion, stale outcomes and repeated dispute cycles. Do not activate loser disposition or response-edit eligibility until P14/P15 is approved and applied. Database provenance and forward migration/replay remain separate gates.


## WA-R042 — Approved service reports, discovery choice, invitation validity and conversations

Binding P16–P19 owner rulings, received 2026-10-07 America/New_York. Supersede open recommendations; no implementation completion implied.

### P16

A Professional may report completion or no-show for an authorized service session. Authorized support may confirm, correct or adjudicate the service-performance state where policy permits; the Customer can contest the report. Preserve immutable report/correction history, reporting actor and authority, occurrence/recorded time, evidence references, affected session and which participant allegedly failed to attend. A correction references the original; it does not erase it. Reported outcome and contested/adjudicated status are distinguishable, so a Professional assertion is never represented as independent support verification.

Completion/no-show status alone must not automatically trigger refund, charge, payout release, forfeiture, review eligibility or any other financial consequence. Order, Payment/Payout, Review/Dispute, Booking and the applicable policy owner each evaluate their owned consequences from current authorized evidence. A single session report never proves full multi-session Order completion. Clock passage does not fabricate a performance report.


### P19

Booking and participant-facing Dispute discussion associated with the same Order reuse that Order's conversation. Context labels/session/case references aid navigation, but do not create duplicate buyer/seller threads. Messaging resolves the canonical Order thread and current membership through its public interface; source owners supply authoritative context and participant facts. Reuse does not automatically enroll a reviewer/support actor or expose unrelated history.

Private adjudication notes, reviewer deliberation, restricted evidence, internal support/moderation material and decision-making records remain separate from the participant conversation under their owning access/audit boundaries. No generic attachment forwarding or notification may leak those records into the thread. Sharing a conversation transfers none of Booking, Dispute, Messaging, Moderation or Order lifecycle ownership.


## WA-R052 — Commerce source events and projection contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. This scoped ruling supersedes earlier proposed/unresolved alternatives for the concerns explicitly specified here; other policy/provider gates remain.

Implement the architecture contract below only after the coordinated forward schema and concrete owner/consumer contract tests exist. This is sequencing and acceptance criteria, not implementation-completion evidence.

Owner events carry immutable eventId, event name/schemaVersion, aggregate ID/revision, occurredAt, causationId/correlationId, safe typed actor reference and minimum immutable outcome evidence. Write owner history and outbox atomically. Consumers retain durable semantic effect identity and last applied source version beyond transport inbox expiry; duplicate aliases cannot repeat effects. Public commands and queries remain distinct from facts.

| Producer contract | Minimum scoped payload | Consumer effect |
| --- | --- | --- |
| order.outcome_changed.v1 | Order ID/revision, source kind/id, frozen purchase revision, operational outcome, dispute cycle reference if relevant, authorized disposition reference | Gig records matching assignment projection; Digital Goods/Booking reevaluate their own current rights; no automatic financial or review action |
| booking.performance_reported.v1 | Booking ID/revision, Order/session authorization ref, completed/no_show allegation, reporting actor, alleged absentee for no-show, evidence ref, contest state | Order records evidence and evaluates policy; never treats allegation as automatic package completion |
| booking.performance_adjudicated.v1 | same identity plus support authority, prior report ref, correction/adjudication outcome and evidence | Order reevaluates; preserve original report and prior decisions |
| booking.confirmed.v1 / rescheduled.v1 / cancelled.v1 | Booking ID/revision, Order/session ref, schedule revision, authorized participant refs, safe reason | Video/calendar/Messaging setup or invalidation through their owners; Notification receives source-directed safe recipient references |
| review.reputation_changed.v1 | Professional ID, source/projection version and changed Review ID/revision; no private comment/evidence | Professional/Search refresh via getProfessionalReputation.v1, apply only current version |

Booking owns BookingEventActor and BookingLocationType vocabularies. Domain actor values distinguish customer/professional/support/system and retain authenticated User attribution where lawful; no free-text role can authorize a transition. Its existing completed/no_show event aliases normalize to performance-report facts, not adjudicated or commercial-completion facts. Existing proposed booking.* / calendar.* names in §12 become the owner event namespace; only the specific registered semantics qualify integration. Existing OrderCreated/OrderCompleted-style aliases normalize at ingress to their owner versioned equivalent with original event identity, never publish duplicate semantic facts. This table is architecture, not evidence of implemented producer/consumer compatibility.

Review owns `getProfessionalReputation.v1`: request Professional ID with caller context and optional known projection version; response ratingAverage (nullable when count=0), ratingCount, source revision, projection revision, asOf and readiness/staleness result. Fractional aggregate is valid under P06. A refresh event invalidates/reloads this query; consumers cannot recompute from private Review rows or mistake missing/unready result for a zero rating. Hidden/removed Reviews withdraw exactly their existing contribution; revision updates do not add a rating count. Bilateral race, tombstone and replay fixtures are required before freeze.

Notification routing remains source-selected and asynchronous: material accepted-term/proposal changes and appointment/case participant-visible changes carry an authorized destination and affected participant references; failure to deliver cannot roll back owner truth. Private adjudication/evidence never enters participant notifications. P19 uses the Order conversation with Booking/case links; those links do not expand access. Optional viewed/shortlisted alerts stay inactive absent an approved trigger/template policy. This identifies source facts; final template/recipient fan-out matrix remains with Notification convergence.

Gamification may qualify Order completion or eligible reputation changes only through its versioned rule catalog and original source event identity; propagated Gig completion is not a second earning fact. Hold consumers evaluate scoped action decisions and preserve restriction provenance; release only triggers reevaluation, never automatic restoration. Moderation commands use authorized target/action/revision plus durable receipt and local owner execution. Exact shared action, assurance, reward rule and Notification contracts still require canonical cross-rail convergence; this owner event contract does not promote adjacent proposed SH operations.


## WA-R066 — Finite Notification source and recipient contracts

Classification: AI_RESOLVED_WITH_TRADEOFF. Architecture contract; implementation and external qualification remain explicit gates.

SH-041 uses the following finite versioned semantic-intent/template registrations. These are architecture contracts, not implemented renderers, selected delivery vendors or proof of delivery. Sources emit an intent only after the corresponding durable owner transition. Every intent binds source owner, typed aggregate ID/revision, immutable semantic intent ID, template key/version, owner-resolved local User recipients, safe authenticated route, sensitivity and event kind. Notification owns channel consent, current endpoint generation, eligible delivery, attempts and receipts. Sources never ask Notification to scan foreign memberships or reconstruct business state.

| Intent/template | Committed source and recipients | Safe additional content |
| --- | --- | --- |
| message.new.v1 | Messaging messaging.message_created.v1; other currently eligible Thread participants selected by Messaging, excluding sender | Thread/Message references only; no message body or attachment URL |
| order.outcome.v1 | Order order.outcome_changed.v1; currently authorized Order participants selected by Order for its source kind | Safe operational outcome code and Order link; no financial consequence implied |
| booking.schedule.v1 | Booking confirmed/rescheduled/cancelled facts; currently authorized affected Booking participants | Safe change kind and authenticated schedule link; no exact address or meeting credential |
| interview.invitation.v1 | Interview invitation/current schedule revision; invited eligible Candidate and authorized Organization participants selected by Interview | Interview reference and safe proposed/scheduled kind |
| interview.schedule.v1 | Interview cancellation/reschedule/replacement; currently authorized affected participants selected by Interview | Safe change kind and authorized predecessor/successor references; no new removed-user notice |
| application.status.v1 | Candidate accepted_offer or withdrawn: current authorized hiring Organization recipients selected by Candidate through Hiring facts; Candidate rejected or hired: the application Candidate User | Application reference and exactly accepted_offer/withdrawn/rejected/hired change code; no view/stage alert or general Candidate exposure |
| privacy.verification_needed.v1 | Privacy durable request transition requiring verification; request subject through Privacy/Identity-authorized route | Request reference and safe action-needed code; no verification secret |
| privacy.outcome.v1 | Privacy accounted terminal outcome; currently authorized request subject/representative | Safe terminal category and link; no restricted exemption evidence or other parties' data |
| privacy.export_ready.v1 | Privacy complete manifest and ready exact Media version/current generation; currently authorized export requester | Request/bundle reference; no signed credential or stored public URL |
| security.notice.v1 | Identity committed security intent; affected local User only | Generic change and authenticated-context link; no OTP, recovery token, precise IP or factor details |
| supply.status.v1 | Professional/Marketplace committed status/remediation intent under R035; owner-resolved Professional User | Generic status/remediation code; no Healthcare/provider/Hold detail |

Candidate registers `candidate.application_status_changed.v1` with eventId, application ID/revision, committed time, semantic command identity, old/new status, authorized actor reference and safe typed Candidate/Organization subject references. This event contains no resume, message, employer notes or protected evidence. The source owner derives notification recipients from current Hiring authority. Only the four listed successful status transitions may create application.status.v1 at launch; application views, recruiter stages and retry transport do not. Candidate acceptance must already satisfy R045 current-offer proof, and withdrawal does not restore quota. Sending a notification never makes an application or Candidate publicly discoverable.

Deduplicate one semantic intent × resolved User; channel attempts are children of that intent. Changed payload under the same fingerprint conflicts. Retries preserve identity. Current protected-context access is rechecked before rendering/dereference; loss of membership suppresses the protected notice. Do not create a removed-user notice without its own approved source policy. Delayed invitation links must recheck P18/current schedule. Notification failure never rolls back source truth. No message bodies, resumes, exact locations, raw provider failures, adjudication evidence or credentials may enter generic variables.

Material proposal changes remain visibly surfaced by Gig's current-revision presentation under P14; a delivered notice is not evidence the latest terms were presented for acceptance. Participant-facing Dispute updates reuse Order conversation under P19, but a Review fact cannot be relabeled as an Order event; any separate Review alert remains disabled until registered. Optional viewed/shortlisted, Location, Interview completion/no-show and other undeclared alerts remain disabled. This finite registration does not provide legally sufficient notice policy. Exact copy, renderer/schema fixtures, provider/account/channel qualification and delivery recovery proof remain activation prerequisites. Existing broad notification suggestions are narrowed by this explicit source/recipient matrix for these intents.


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


## WA-R068 / WA-R069 — Authority/event qualification sequence

Implement the `review_dispute` obligations in this Module's architecture and `context/reconciliation/authority-event-contracts.md` before dependent event consumers activate. First register concrete action ports (`submitOrderReview / recordDisputeEvidenceReference / resolveDisputeWithRefund / resolveDisputeWithRelease`), source fact fields/revisions and required B/S/A assurance; then qualify producer outbox/history and the specifically named subscriber effects. Do not implement the entire cross-platform matrix inside this Module.

Acceptance evidence must show wrong relationship/target and stale source facts deny; action-bound assurance cannot replay cross-target; source outage cannot become allowed; duplicate event replay has one effect; same ID/different fingerprint quarantines; late revisions/tombstones cannot resurrect access; correction preserves history and reevaluates the original logical effect. Verify registered payload field minimization and subscriber audience independently of transport delivery. Existing explicit commands and notification intents retain their separate receipts/qualification.

Individual eligible published Review ID/revision, rating/scale and preserved Professional-to-User recipient mapping qualify rating triggers; aggregate reputation cannot substitute. Removal/correction reevaluates the original source/rule effect. Review continues to decide eligibility separately from Booking reports.

DTO/server-RLS parity, executable fixtures, outbox/inbox recovery and provider/security configuration are implementation qualification, not unresolved ownership. Legal/program/provider values remain scoped activation gates; unsupported paths stay disabled. Architecture integration does not claim frozen interfaces, successful runtime tests or permission to change schemas.


## WA-R075 — Typed Hold action applicability and source readiness

This owner adopts its source/consumer obligations in `context/reconciliation/hold-action-contracts.md`. The appendix defines the versioned query/action fields, current-source checks, denial/unavailable behavior and privacy limits; it does not transfer lifecycle ownership or freeze an implementation interface. Implement the named owner port or consumer call with typed fixtures for stale authority, unsupported scope, duplicate effects and minimized fields before activation. Existing product rights and all other applicable gates remain.

## WA-R081–083 — Bridge qualification sequence

Implement only the owner architecture's reviewed bridge obligations (BF-008, BF-017, BF-025, BF-026, BF-027, BF-031, BF-033, BF-048, BF-063, BF-065, BF-066, BF-079, BF-080, BF-082, BF-094, BF-102, BF-108, BF-111, BF-115, BF-116, BF-117, BF-121, BF-123, BF-129, BF-131, BF-133, BF-134, BF-135, BF-143, BF-144, BF-152, BF-153, BF-154, BF-155, BF-156, BF-157, BF-158, BF-160, BF-162, BF-163, BF-164, BF-165, BF-171, BF-175, BF-176, BF-177, BF-188, BF-203, BF-204, BF-205, BF-210, BF-211, BF-230, BF-231, BF-232, BF-242, BF-246, BF-248, BF-249, BF-256, BF-257, BF-260, BF-266, BF-267). Load `context/reconciliation/bridge-contract-bindings.md` and the final inventory for current versions and disabled facets. First bind closed schemas and current source/actor/purpose fixtures; then qualify shared persistence/outbox/idempotency/receipt mechanisms; then connect producer and consumer. Required denial, stale/replay/conflicting-key, late-result and sensitive-field negative fixtures precede interface freeze. Provider/legal/database evidence gates only the affected activation. No full-Cluster dependency or parallel lane is implied, and no optional path is enabled by a fake or a passing structural checker. Preserve historical snapshots and P01–P19; do not implement schema/provider/product slices during readiness.


## WA-R085–087 — Platform qualification dependencies

Follow this owner's platform-convergence architecture and the platform lifecycle/action matrix. Current lifecycle scope: Review eligibility/publication/correction; Dispute case/cycle adjudication and settlement tracking.

Qualify source-fact leaves and exact required owner ports against fixtures before composed decisions, then local persistence/receipts and actual adapters. A contract dependency is not a requirement that the whole upstream Module/Cluster be mature. Production activation still requires every actual port and action-specific external requirement. Do not wait for downstream Search/Notification/telemetry to commit source truth or to bootstrap shared primitives.

Bilateral R085 ports for this owner: `getHoldSourceCauseFacts.v1`. Implement the source/consumer role documented in architecture, including fenced noncommit, complete inventory and cause-only readiness where applicable.

Negative qualification must cover the relevant cycles in platform-dependency-graph.json, stale/revoked source facts, changed fingerprints, unknown external outcomes, projection-as-authority, recursive fact/access calls and actual mandatory proof failures. No schema migration, provider activation, DTO freeze, root build plan or parallel lane approval follows from static review. Preserve Privacy per-owner field/action/serializer coverage as a separate gate.
