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
- SH-087 `issueSignedMediaUrl`;
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
- SH-087 `issueSignedMediaUrl`;
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
